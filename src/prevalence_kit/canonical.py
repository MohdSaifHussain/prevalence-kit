"""Canonical bytes and digests.

Everything hashed anywhere in this tool goes through `canonical()` first. One
function, so two parties can never disagree about what "the hash of this" means
-- which is the whole basis on which `verify` can say no.

Canonical form: JSON, keys sorted, no insignificant whitespace, UTF-8, no ASCII
escaping. Chosen because it is reimplementable in any language in ten lines; an
outside auditor must be able to recompute our digests without our code.

Digest: SHA-256, hex, lowercase. docs/STANDARDS.md S-5.3.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path

type JSONValue = bool | int | float | str | Sequence[JSONValue] | Mapping[str, JSONValue] | None
type JSONObject = dict[str, JSONValue]
"""`JSONObject` exists so functions that always return a mapping can say so.
`JSONValue` alone forces every caller to re-prove that fact before indexing."""

GENESIS_LINK = "0" * 64
"""What the first ledger entry links to. There is nothing before it."""


def canonical(value: JSONValue) -> bytes:
    """Serialise to the one byte-form this project hashes.

    Floats are rejected: they do not round-trip identically across platforms, and
    a digest that depends on the platform is not a digest. Encode any real number
    as a string at the point it is recorded.
    """
    _reject_floats(value)
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def digest(value: JSONValue) -> str:
    """SHA-256 of the canonical bytes, hex."""
    return hashlib.sha256(canonical(value)).hexdigest()


def digest_bytes(raw: bytes) -> str:
    """SHA-256 of raw bytes, hex. For ciphertext and file contents."""
    return hashlib.sha256(raw).hexdigest()


def digest_file(path: Path, *, chunk: int = 1 << 20) -> str:
    """SHA-256 of a file's bytes, hex. Streamed, so file size is not a limit."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while block := fh.read(chunk):
            h.update(block)
    return h.hexdigest()


def _reject_floats(value: JSONValue) -> None:
    if isinstance(value, float):
        raise TypeError(
            "canonical(): floats are not hashable here because they do not "
            "round-trip identically across platforms. Record the number as a string."
        )
    if isinstance(value, Mapping):
        for k, v in value.items():
            if not isinstance(k, str):
                raise TypeError(f"canonical(): object keys must be strings, got {type(k).__name__}")
            _reject_floats(v)
    elif isinstance(value, Sequence) and not isinstance(value, str | bytes):
        for v in value:
            _reject_floats(v)
