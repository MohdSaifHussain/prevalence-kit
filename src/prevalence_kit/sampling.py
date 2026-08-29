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

docs/DECISIONS.md D-16.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Mapping, Sequence

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
            Reason.FRAME_EMPTY,
            "The sampling frame is empty.",
            "Point the plan at a population file that has rows in it.",
        )
    if n > len(ids):
        raise Refusal(
            Reason.FRAME_TOO_SMALL,
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


def draw_stratified(
    members: Mapping[str, Sequence[str]],
    *,
    seed: str,
    allocation: Mapping[str, int],
) -> dict[str, tuple[str, ...]]:
    """Draw independently within each stratum, by the same keyed sort as SRS.

    **S-1.13 gives the two rules this obeys**: strata are mutually exclusive, and
    *independent samples are selected from each stratum*. So this is `draw_srs`
    applied per stratum rather than a single draw partitioned afterwards -- those
    are different designs and only one of them is what the plan pre-registered.

    Determinism is D-16's, unchanged: the key is `SHA-256(seed || id)`, so the
    stratum a unit belongs to never enters its key. An outsider can recompute any
    stratum's draw knowing only the seed, that stratum's ids, and its allocation.

    Returns a mapping so the caller can record per-stratum counts. Flattening
    here would discard the structure `verify` and the estimator both need.
    """
    drawn: dict[str, tuple[str, ...]] = {}
    for name in sorted(members):
        ids = sorted(set(members[name]))
        want = allocation[name]
        if want > len(ids):
            # Guarded in `allocate` as well; kept here because this function is
            # part of the API surface D-25 records as real, and a caller that
            # reaches it directly gets the named refusal rather than a short draw.
            raise Refusal(
                Reason.ALLOCATION_IMPOSSIBLE,
                f"Stratum {name!r} was allocated {want} units but holds {len(ids)}.",
                "Lower sample_size, or merge this stratum into a neighbour.",
            )
        drawn[name] = tuple(sorted(ids, key=lambda i: (selection_key(seed, i), i))[:want])
    return drawn


def stratified_sample_record(
    plan_hash: str,
    seed: str,
    frame_size: int,
    drawn: Mapping[str, Sequence[str]],
    allocation: JSONObject,
) -> JSONObject:
    """The hashable record of a stratified draw.

    Carries the **raw and rounded** allocation, which is **D-30 condition 3**:
    both reach the ledger so an outsider can re-derive the rounding without
    running this code, and `verify` re-derives it so a changed rule breaks the
    chain.

    `item_ids` is the flattened draw in stratum-name order, so the downstream
    label match is identical to the SRS path; `by_stratum` keeps the structure.
    """
    flat: list[str] = []
    for name in sorted(drawn):
        flat.extend(drawn[name])
    return {
        "plan_hash": plan_hash,
        "method": "sha256-keyed-sort-per-stratum",
        "seed": seed,
        "frame_size": frame_size,
        "n": len(flat),
        "item_ids": flat,
        "by_stratum": {name: list(drawn[name]) for name in sorted(drawn)},
        "allocation": allocation,
    }
