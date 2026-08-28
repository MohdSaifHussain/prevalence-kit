"""The measurement run: the six steps, and the workspace they write into.

Layout of a run directory::

    ledger.jsonl      the chain -- the record everything else is checked against
    seal.key          the sealing key (never committed; see SECURITY.md 3.1)
    plan.sealed/      a sealed copy of the plan, so verify works without the file
    frame.json        the sampling frame ids, so a draw can be re-derived
    sample.json       the drawn ids
    labels.json       item id -> raw label value. No content.
    estimate.json     the number and its interval
    sealed/           the content, chunked and encrypted

Content lives only under `sealed/`. `labels.json` holds label values and never
text, which is what lets `verify` and `emit-report` run without unsealing
anything.
"""

from __future__ import annotations

import csv
import json
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .canonical import JSONValue, canonical, digest, digest_bytes
from .errors import Reason, Refusal
from .estimators import Interval, wilson
from .ledger import Ledger
from .plan import Plan
from .sampling import draw_srs, sample_record
from .seal import Manifest, SealedStore

PLAN_ITEM = "__plan__"

_CSV_FIELD_LIMIT = 64 * 1024 * 1024
"""Largest single CSV field accepted: exactly 67,108,864 bytes (64 MiB).

Not unbounded -- a runaway file should refuse rather than exhaust memory. The
figure is restated here in bytes so `tools/check_claims.py` can compare the prose
against the constant; rule 8 wants a checkable limit defended by machinery rather
than by a decision record."""


@dataclass(frozen=True, slots=True)
class Workspace:
    root: Path

    @property
    def ledger(self) -> Ledger:
        return Ledger(self.root / "ledger.jsonl")

    @property
    def key_path(self) -> Path:
        return self.root / "seal.key"

    def key(self) -> bytes:
        """The one place the sealing key is read.

        Every path goes through here. `verify` used to read the key file directly
        and died with a raw FileNotFoundError, which is why F-5's fix to
        `store()` did not reach it. One reader, one refusal. V-6.
        """
        if not self.key_path.exists():
            raise Refusal(
                Reason.KEY_MISSING,
                f"No sealing key at {self.key_path}.",
                "Without the key nothing can be unsealed. Restore it from wherever you kept it.",
            )
        return self.key_path.read_bytes()

    def store(self) -> SealedStore:
        return SealedStore(self.root / "sealed", self.key())

    def plan_store(self) -> SealedStore:
        """The plan's sealed copy. Write-once: a re-plan must never destroy the
        copy of the plan that was originally committed to. Layer 4 of V-1."""
        return SealedStore(self.root / "plan.sealed", self.key(), write_once=True)

    def read_json(self, name: str) -> Any:
        path = self.root / name
        if not path.exists():
            raise Refusal(
                Reason.LEDGER_BROKEN,
                f"The run is missing {name}.",
                "A step has not been run yet, or the run directory was edited.",
            )
        return json.loads(path.read_text(encoding="utf-8"))

    def write_json(self, name: str, value: JSONValue) -> str:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
            newline="\n",
        )
        return digest(value)


# --------------------------------------------------------------------- steps


def do_plan(ws: Workspace, plan: Plan) -> str:
    """Hash the plan and open the chain. No data file is touched here.

    The hash is computed from the plan alone (R1). We also seal a copy of the
    plan, so `verify` still has something to check against after the working file
    is moved or deleted (D-15).
    """
    ws.root.mkdir(parents=True, exist_ok=True)

    # Layer 1: a workspace holds exactly one measurement. Refusing here is
    # prevention; `verify` refuses independently (Layer 2), because an auditor
    # may be handed a record this code never wrote.
    if ws.ledger.read_raw():
        raise Refusal(
            Reason.RUN_ALREADY_OPEN,
            f"{ws.root} already holds a measurement.",
            "A new measurement is a new workspace. Re-registering a plan over an "
            "existing run is how a number gets chosen after the results are seen.",
        )

    if not ws.key_path.exists():
        ws.key_path.write_bytes(SealedStore.new_key())

    plan_hash = plan.plan_hash
    manifest = ws.plan_store().seal(PLAN_ITEM, canonical(plan.as_record()))

    ws.ledger.append(
        "plan",
        {
            "plan_hash": plan_hash,
            "plan_seal": manifest.as_record(),
            "estimand": plan.estimand.description,
        },
    )
    return plan_hash


def do_sample(ws: Workspace, plan: Plan, frame_path: Path) -> tuple[str, ...]:
    """Draw the sample. Records the frame too, so the draw stays re-derivable."""
    ids = _read_frame(frame_path)
    drawn = draw_srs(ids, seed=plan.seed, n=plan.sample_size)

    # V-7: a frame is a set of units, so de-duplicating is correct -- but doing it
    # silently is not. For a prevalence tool this is the denominator. Both counts
    # go in the record, so a reader can see the input differed from what was used.
    unique = sorted(set(ids))
    frame_digest = ws.write_json("frame.json", unique)
    record = sample_record(plan.plan_hash, plan.seed, len(unique), drawn)
    sample_digest = ws.write_json("sample.json", record)

    ws.ledger.append(
        "sample",
        {
            "frame_digest": frame_digest,
            "sample_digest": sample_digest,
            "frame_rows_read": len(ids),
            "frame_unique_ids": len(unique),
            "n": len(drawn),
        },
    )
    return drawn


def do_ingest(ws: Workspace, plan: Plan, labels_path: Path) -> dict[str, str]:
    """Seal the content, record the labels.

    Refuses unless the labels line up one-to-one with the drawn sample. A label
    set that is merely *mostly* right is how a measurement quietly becomes a
    different measurement.
    """
    drawn: list[str] = list(ws.read_json("sample.json")["item_ids"])
    rows = _read_labels(labels_path, plan.estimand.label_field)

    missing = sorted(set(drawn) - rows.keys())
    extra = sorted(rows.keys() - set(drawn))
    if missing or extra:
        raise Refusal(
            Reason.LABELS_UNMATCHED,
            f"{len(missing)} sampled items have no label; "
            f"{len(extra)} labels are for items not sampled.",
            "Label exactly the drawn sample -- no more, no less.",
        )

    store = ws.store()
    manifests = [store.seal(item_id, rows[item_id][1].encode("utf-8")) for item_id in drawn]
    labels = {item_id: rows[item_id][0] for item_id in drawn}

    labels_digest = ws.write_json("labels.json", labels)
    ws.ledger.append(
        "ingest-labels",
        {
            "labels_digest": labels_digest,
            "seals": [m.as_record() for m in manifests],
            "sealed_items": len(manifests),
        },
    )
    return labels


def do_estimate(ws: Workspace, plan: Plan) -> Interval:
    labels: dict[str, str] = ws.read_json("labels.json")
    interval = _estimate_from(plan, labels)
    estimate_digest = ws.write_json("estimate.json", interval.as_record())
    ws.ledger.append("estimate", {"estimate_digest": estimate_digest, "method": interval.method})
    return interval


def _estimate_from(plan: Plan, labels: dict[str, str]) -> Interval:
    positives = 0
    for item_id, raw in labels.items():
        try:
            positives += 1 if plan.estimand.is_positive(raw) else 0
        except Refusal as exc:
            # Re-raised with the item id so the operator can find the row. The
            # label value is a label, not content, so naming it leaks nothing.
            raise Refusal(exc.reason, f"Item {item_id}: {exc.detail}", exc.fix) from exc
    return wilson(positives, len(labels))


# ----------------------------------------------------------------- input I/O


def _read_frame(path: Path) -> list[str]:
    if not path.exists():
        raise Refusal(
            Reason.EMPTY_SAMPLE,
            f"No population frame at {path}.",
            "Point the plan's `population` at a file with one item id per line, "
            "or a CSV with item_id.",
        )
    # Both readers strip. They used to disagree, so " item-1" was two distinct
    # population members from a CSV and one from a text file. V-7.
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8") as fh:
            rows = [str(r["item_id"]).strip() for r in csv.DictReader(fh)]
    else:
        rows = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    return [r for r in rows if r]


def _read_labels(path: Path, label_field: str) -> dict[str, tuple[str, str]]:
    """item_id -> (label value, content). Content is sealed immediately after."""
    if not path.exists():
        raise Refusal(
            Reason.LABELS_UNMATCHED,
            f"No labels file at {path}.",
            "Point the plan's `labels` at a CSV or JSONL with item_id and your label column.",
        )
    rows: dict[str, tuple[str, str]] = {}
    if path.suffix.lower() == ".jsonl":
        records = [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    else:
        try:
            with path.open(newline="", encoding="utf-8") as fh, _wide_csv_fields():
                records = list(csv.DictReader(fh))
        except csv.Error as exc:
            # V-11. D-19 moved this cliff from 128 KiB to 64 MiB; it did not remove
            # it. A field past the ceiling raised the identical bare `_csv.Error`
            # that D-19 was opened to get rid of, 512x further out. Same class as
            # F-1: a real input producing a library traceback instead of a refusal.
            raise Refusal(
                Reason.CONTENT_TOO_LARGE,
                f"A field in {path.name} is larger than this tool will read "
                f"({_CSV_FIELD_LIMIT:,} bytes).",
                "Split the oversized row, or store that item's content in a separate "
                "file and reference it. The limit is deliberate: it stops a runaway "
                "file exhausting memory.",
            ) from exc

    for r in records:
        if "item_id" not in r or label_field not in r:
            raise Refusal(
                Reason.LABELS_UNMATCHED,
                f"A label row is missing 'item_id' or '{label_field}'.",
                f"Every row needs an item_id and a {label_field} column.",
            )
        rows[str(r["item_id"])] = (str(r[label_field]), str(r.get("content", "")))
    return rows


@contextmanager
def _wide_csv_fields() -> Iterator[None]:
    """Let a CSV field hold a whole piece of content.

    `csv` caps a single field at 128 KiB and raises a bare `_csv.Error` past it.
    Trust & Safety content routinely exceeds that -- a long post, a transcript, a
    thread -- and this tool chunks content precisely so size is not a limit. A
    library default is not a reason to refuse an operator's data, and a raw
    `_csv.Error` is not a refusal.

    Restored afterwards: this is process-global state and this tool does not get
    to leave it changed for whatever else is running.
    """
    previous = csv.field_size_limit()
    csv.field_size_limit(_CSV_FIELD_LIMIT)
    try:
        yield
    finally:
        csv.field_size_limit(previous)


def content_digest_of(text: str) -> str:
    return digest_bytes(text.encode("utf-8"))


def manifests_from(entry_body: dict[str, JSONValue]) -> list[Manifest]:
    seals = entry_body["seals"]
    assert isinstance(seals, list)
    return [Manifest.from_record(s) for s in seals]
