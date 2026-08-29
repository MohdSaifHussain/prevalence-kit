"""D2.9 -- the `svy` cross-check, where its estimator is the same estimator.

**This script never runs in the project environment, and must not.** `svy`
declares a hard dependency on `httpx`, and Hard Rule 1 is zero network calls at
runtime, *proven by a test that fails if any network capability appears in the
dependency tree*. That is D-2's whole reasoning. So `svy` is installed in a
**separate throwaway environment**, this script is run there, and only its
**output** is committed. The project's virtualenv and `pyproject.toml` never see
it.

    python -m venv /tmp/svyvenv
    /tmp/svyvenv/bin/python -m pip install svy==0.25.0
    /tmp/svyvenv/bin/python svy/generate_allocation_fixtures.py svy/fixtures/allocation.json

**Why allocation and not the intervals.** **D-18** narrowed O-4: `svy` is a
witness *only where its estimator is the same estimator*, and for Wilson it is
not -- `svy` substitutes an effective sample size and uses a t-quantile. Reading
`svy/estimation/base.py` at 0.25.0 shows that holds for **every** interval it
offers: `logit` is a Wald interval on the logit scale, `beta` and
`korn-graubard` are Korn-Graubard with a df-adjusted effective sample size, and
its `wilson` is the design-based one D-18 already recorded. **`svy` maps the
alias `"clopper-pearson"` to `"korn-graubard"`** -- so asking it for
Clopper-Pearson does not give the textbook interval we ship.

**Allocation is different, and it is the one place the estimators coincide.**
`_neyman_allocation` computes `measure = N * S`, `raw = measure / total * n`,
then floors and hands the shortfall to the largest fractional parts. That is
Neyman allocation with **largest-remainder rounding** -- our formula and
**D-30**'s rule.

**Why this matters more than a second opinion.** **F-9** established that the
allocation half of D2.3 has never had an external witness at all: R `survey` has
no allocator, so `r/stratified_fixtures.R`'s `neyman()` is our own formula
re-implemented in R by its own author. That is the sixth instrument-limit kind --
a fixture that looks external and is not. **This is the first genuine outside
check on allocation this project has had.**
"""

from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

import svy
from svy.selection.allocation import _neyman_allocation

FRAME_TOTAL = 1_000_000
"""Weights are turned into sizes against this frame. Neyman is scale-free in the
weights, so the total only has to be large enough that rounding W_h * FRAME does
not move the ratios."""

SHIPPED = [
    (
        "barnett_neyman_4000",
        [0.8, 0.1, 0.05, 0.01, 0.04],
        [0.0005, 0.005, 0.01, 0.05, 0.0025],
        4000,
    ),
    ("two_stratum_neyman_1000", [0.9, 0.1], [0.001, 0.20], 1000),
    ("rare_event_neyman_5000", [0.95, 0.04, 0.01], [0.0002, 0.0060, 0.0090], 5000),
]

EDGES = {
    "exact_tie_two_equal": ({"s0": 1000, "s1": 1000}, {"s0": 1.0, "s1": 1.0}, 5),
    "exact_tie_three_equal": (
        {"s0": 1000, "s1": 1000, "s2": 1000},
        {"s0": 1.0, "s1": 1.0, "s2": 1.0},
        7,
    ),
}
"""Only the edges where both implementations produce an *unconstrained*
allocation. `min_n` and `cap_at_population` are `svy` policy, and where they bite
we refuse instead -- those cases belong in the divergence note, not in a fixture
that asserts agreement."""


def allocate_via_svy(weights: list[float], rates: list[float], n: int) -> list[int]:
    sizes = {f"s{i}": round(w * FRAME_TOTAL) for i, w in enumerate(weights)}
    sds = {f"s{i}": math.sqrt(p * (1 - p)) for i, p in enumerate(rates)}
    got = _neyman_allocation(sizes, sds, n, min_n=1, cap_at_population=True)
    return [got[f"s{i}"] for i in range(len(weights))]


def main(out_path: str) -> None:
    version = getattr(svy, "__version__", "unknown")
    payload: dict[str, object] = {
        "what": "svy Neyman allocation, for D2.9's same-estimator cross-check",
        "deliverable": "D2.9",
        "register": "S-2.2",
        "svy_version": version,
        "python": sys.version.split()[0],
        "exact_call": (
            "svy.selection.allocation._neyman_allocation("
            "group_sizes, group_sds, n_total, min_n=1, cap_at_population=True)"
        ),
        "frame_total": FRAME_TOTAL,
        "narrowing": (
            "svy is a witness ONLY where its estimator is the same estimator "
            "(D-18). Its interval methods are all design-based -- it maps the "
            "alias 'clopper-pearson' to 'korn-graubard' -- so none of them "
            "witnesses ours. Allocation is the one place they coincide."
        ),
    }

    fixtures = []
    for label, weights, rates, n in SHIPPED:
        fixtures.append(
            {
                "label": label,
                "W_h": weights,
                "p_h": rates,
                "n_total": n,
                "allocation": allocate_via_svy(weights, rates, n),
            }
        )
    payload["shipped_fixtures"] = fixtures

    edges = []
    for label, (sizes, sds, n) in EDGES.items():
        got = _neyman_allocation(sizes, sds, n, min_n=1, cap_at_population=True)
        edges.append(
            {
                "label": label,
                "sizes": sizes,
                "sds": sds,
                "n_total": n,
                "allocation": [got[k] for k in sorted(got)],
            }
        )
    payload["edge_cases"] = edges

    # A randomised sweep, so agreement is a measurement with a stated space
    # rather than three cases that happen to line up.
    random.seed(20260830)
    sweep = []
    for _ in range(2000):
        k = random.randint(2, 6)
        raw_weights = [random.uniform(0.01, 1.0) for _ in range(k)]
        total = sum(raw_weights)
        weights = [w / total for w in raw_weights]
        rates = [random.uniform(0.0005, 0.5) for _ in range(k)]
        n = random.randint(2 * k, 20000)
        sweep.append(
            {
                "W_h": weights,
                "p_h": rates,
                "n_total": n,
                "allocation": allocate_via_svy(weights, rates, n),
            }
        )
    payload["sweep"] = sweep
    payload["sweep_space"] = (
        "2000 designs, seed 20260830: 2-6 strata, weights ~ U(0.01, 1) normalised, "
        "p ~ U(0.0005, 0.5), n ~ U(2k, 20000)."
    )

    Path(out_path).write_text(json.dumps(payload, indent=1), encoding="utf-8")
    print(
        f"wrote {out_path}: svy {version}, {len(fixtures)} shipped, "
        f"{len(edges)} edges, {len(sweep)} sweep"
    )


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "svy/fixtures/allocation.json")
