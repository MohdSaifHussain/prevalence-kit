"""Simple random sampling, deterministic by construction.

Selection is by keyed hash, not by a pseudo-random number generator: for each
frame id we compute SHA-256(seed || id) and take the n smallest. Sorting a
population by a keyed hash is a uniformly random permutation, so the first n are
a simple random sample without replacement.

We do it this way rather than with `random.sample` for two reasons, and both are
requirements rather than preferences:

  * R2 wants byte-identical output across 3.12/3.13/3.14 and across platforms.
    `random.sample`'s internal algorithm is an implementation detail and is not
    promised to be stable; SHA-256 is.
  * `verify` has to be reproducible by an outsider who is not running this code.
    "SHA-256 the seed and the id, sort, take n" is reimplementable in any
    language in a few lines. A Mersenne Twister draw sequence is not.

docs/DECISIONS.md D-17.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Sequence

from .canonical import JSONObject
from .errors import Reason, Refusal


def selection_key(seed: str, item_id: str) -> str:
    """The sort key for one item. Published, so anyone can recompute the sample."""
    return hashlib.sha256(f"{seed}\x00{item_id}".encode()).hexdigest()


def draw_srs(frame: Iterable[str], *, seed: str, n: int) -> tuple[str, ...]:
    """Draw n ids from the frame, without replacement, deterministically.

    Ties on the hash break on the id itself, so the result does not depend on the
    order the frame happened to arrive in.
    """
    ids = sorted(set(frame))
    if not ids:
        raise Refusal(
            Reason.EMPTY_SAMPLE,
            "The sampling frame is empty.",
            "Point the plan at a population file that has rows in it.",
        )
    if n > len(ids):
        raise Refusal(
            Reason.EMPTY_SAMPLE,
            f"The plan asks for {n} items but the frame holds {len(ids)}.",
            "Lower sample_size, or widen the population.",
        )
    return tuple(sorted(ids, key=lambda i: (selection_key(seed, i), i))[:n])


def sample_record(plan_hash: str, seed: str, frame_size: int, drawn: Sequence[str]) -> JSONObject:
    """The hashable record of a draw. Enough for anyone to redo it."""
    return {
        "plan_hash": plan_hash,
        "method": "sha256-keyed-sort",
        "seed": seed,
        "frame_size": frame_size,
        "n": len(drawn),
        "item_ids": list(drawn),
    }
