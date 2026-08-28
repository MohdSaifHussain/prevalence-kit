"""The hash-chained ledger.

Append-only JSONL. Each entry commits to the one before it, so editing any entry
invalidates every entry after it. The chain is what lets `verify` say no.

Entry digest covers the entry's own fields *including* `prev`, which is what
links them. It does not cover `entry_digest` itself, for obvious reasons.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Self

from .canonical import GENESIS_LINK, JSONObject, JSONValue, digest
from .errors import Reason, Refusal


@dataclass(frozen=True, slots=True)
class Entry:
    seq: int
    step: str
    at: str  # RFC 3339, UTC, second precision
    prev: str
    body: dict[str, JSONValue]

    def payload(self) -> JSONObject:
        return {
            "seq": self.seq,
            "step": self.step,
            "at": self.at,
            "prev": self.prev,
            "body": self.body,
        }

    @property
    def entry_digest(self) -> str:
        return digest(self.payload())

    def to_json(self) -> str:
        record = dict(self.payload())
        record["entry_digest"] = self.entry_digest
        return json.dumps(record, sort_keys=True, ensure_ascii=False, separators=(",", ":"))

    @classmethod
    def from_json(cls, line: str, *, lineno: int) -> tuple[Self, str]:
        """Parse one line. Returns the entry and the digest the file claims for it."""
        try:
            raw: Any = json.loads(line)
        except json.JSONDecodeError as exc:
            raise Refusal(
                Reason.LEDGER_BROKEN,
                f"Ledger line {lineno} is not valid JSON.",
                "The ledger has been edited or truncated. Restore it from your record.",
            ) from exc
        try:
            claimed = str(raw.pop("entry_digest"))
            return cls(
                seq=int(raw["seq"]),
                step=str(raw["step"]),
                at=str(raw["at"]),
                prev=str(raw["prev"]),
                body=raw["body"],
            ), claimed
        except (KeyError, TypeError, ValueError) as exc:
            raise Refusal(
                Reason.LEDGER_BROKEN,
                f"Ledger line {lineno} is missing required fields.",
                "The ledger has been edited. Restore it from your record.",
            ) from exc


class Ledger:
    """Append-only chain over one measurement run."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def append(self, step: str, body: dict[str, JSONValue]) -> Entry:
        entries = self.read_raw()
        prev = entries[-1][0].entry_digest if entries else GENESIS_LINK
        entry = Entry(
            seq=len(entries),
            step=step,
            at=datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            prev=prev,
            body=body,
        )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write(entry.to_json() + "\n")
        return entry

    def read_raw(self) -> list[tuple[Entry, str]]:
        if not self.path.exists():
            return []
        return [
            Entry.from_json(line, lineno=i)
            for i, line in enumerate(self.path.read_text(encoding="utf-8").splitlines(), start=1)
            if line.strip()
        ]

    def verify(self) -> list[Entry]:
        """Walk the chain. Raises Refusal(LEDGER_BROKEN) at the first bad link.

        Reports the *first* break, not the last, because every entry after a break
        is untrustworthy and saying so twenty times helps nobody.
        """
        entries: list[Entry] = []
        expected_prev = GENESIS_LINK
        for i, (entry, claimed) in enumerate(self.read_raw()):
            where = f"entry {i} ({entry.step})"
            if entry.seq != i:
                raise Refusal(
                    Reason.LEDGER_BROKEN,
                    f"{where} is numbered {entry.seq}.",
                    "An entry was inserted or removed.",
                )
            if entry.entry_digest != claimed:
                raise Refusal(
                    Reason.LEDGER_BROKEN,
                    f"{where} does not match its own digest.",
                    "That entry's contents were edited after it was written.",
                )
            if entry.prev != expected_prev:
                raise Refusal(
                    Reason.LEDGER_BROKEN,
                    f"{where} does not link to the entry before it.",
                    "An earlier entry was edited, or an entry was removed.",
                )
            expected_prev = entry.entry_digest
            entries.append(entry)
        return entries

    def step(self, name: str) -> Entry | None:
        """Most recent entry for a step, or None."""
        return next((e for e in reversed(self.verify()) if e.step == name), None)

    def __iter__(self) -> Iterator[Entry]:
        return iter(self.verify())
