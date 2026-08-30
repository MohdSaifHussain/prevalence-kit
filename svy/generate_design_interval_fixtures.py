"""O-26 / D2.17 -- design-based interval fixtures from `svy`, BEFORE the estimator.

**R2.2, and it is the whole shape of this phase.** The expected values are
generated and committed first, so a test cannot agree with an implementation for
the same wrong reason. This script runs in the throwaway `svy` environment; only
its output is committed.

**Why `svy` witnesses these when it witnesses none of our binomial intervals.**
D2.9 measured that `svy` cannot witness Wilson or Clopper-Pearson on `(k, n)`: it
substitutes an effective sample size and we do not. **A stratified estimate is
itself design-based**, so that conclusion does not reach it, and re-measuring
rather than inheriting is what Q15 turned on. `svy` reproduces our stratified
point estimate, standard error and degrees of freedom **exactly** -- 2.9e-16
relative at worst -- so the interval built on top of them can be witnessed.

**The mapping, and the reason each name means what it does.**

    design_wilson           -> svy `wilson`
    design_clopper_pearson  -> svy `beta`

`svy`'s own documentation: `beta` is *"Korn-Graubard CI matching R's
`survey::svyciprop(method="beta")`. Uses df-adjusted effective sample size (no
truncation) and the incomplete Beta function (Clopper-Pearson formulation)."*
That is the Clopper-Pearson construction on a design-based effective `n`, which is
what `design_clopper_pearson` names.

**Not `korn-graubard`**, which adds NCHS truncation of the effective sample size.
It is a third construction and this version does not offer it -- deferred by name
rather than absent by accident.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy
import polars as pl
import svy

# Stratified designs: name -> {stratum: (N_h, n_h, k_h)}. Chosen to cover the
# rare-event end this tool exists for, a balanced case, and a two-stratum case
# with a small stratum, so the fixture is not three variations of one shape.
DESIGNS: dict[str, dict[str, tuple[int, int, int]]] = {
    "balanced": {"a": (2000, 100, 20), "b": (3000, 150, 15), "c": (5000, 250, 5)},
    "rare": {"a": (200, 60, 3), "b": (800, 120, 2), "c": (4000, 120, 1)},
    "two_stratum": {"a": (900, 90, 30), "b": (100, 40, 2)},
    "very_rare": {"a": (500, 100, 1), "b": (9500, 400, 0)},
    "wide": {"a": (1000, 50, 25), "b": (1000, 50, 10), "c": (1000, 50, 40)},
}

CONFIDENCES = [0.90, 0.95, 0.99]

METHODS = {"design_wilson": "wilson", "design_clopper_pearson": "beta"}


def build(spec: dict[str, tuple[int, int, int]]) -> pl.DataFrame:
    rows = []
    for name, (big_n, small_n, positives) in spec.items():
        weight = big_n / small_n
        for i in range(small_n):
            rows.append(
                {
                    "unit": f"{name}-{i:05d}",
                    "stratum": name,
                    "y": 1 if i < positives else 0,
                    "wgt": weight,
                }
            )
    return pl.DataFrame(rows)


def main(out_path: str) -> None:
    cases = []
    for label, spec in DESIGNS.items():
        frame = build(spec)
        design = svy.Design(row_index="unit", stratum="stratum", wgt="wgt", psu="unit")
        sample = svy.Sample(frame, design)
        entry: dict[str, object] = {
            "label": label,
            "strata": {k: list(v) for k, v in spec.items()},
            "intervals": {},
        }
        intervals: dict[str, list[dict[str, object]]] = {}
        for ours, theirs in METHODS.items():
            rows = []
            for confidence in CONFIDENCES:
                est = svy.Estimation(sample).prop(
                    "y", ci_method=theirs, alpha=1 - confidence
                )
                row = next(r for r in est.to_dicts() if int(r["y_level"]) == 1)
                rows.append(
                    {
                        "confidence": confidence,
                        "point": float(row["est"]),
                        "se": float(row["se"]),
                        "df": int(row["df"]),
                        "low": float(row["lci"]),
                        "high": float(row["uci"]),
                    }
                )
            intervals[ours] = rows
        entry["intervals"] = intervals
        cases.append(entry)

    payload = {
        "what": "svy design-based interval fixtures, generated BEFORE the estimator",
        "deliverable": "D2.17",
        "obligation": "O-26",
        "register": "S-2.2",
        "svy_version": getattr(svy, "__version__", "unknown"),
        "numpy_version": numpy.__version__,
        "polars_version": pl.__version__,
        "python": sys.version.split()[0],
        "exact_call": (
            "svy.Estimation(svy.Sample(frame, svy.Design(row_index='unit', "
            "stratum='stratum', wgt='wgt', psu='unit')))"
            ".prop('y', ci_method=M, alpha=1-confidence), y_level == 1 row"
        ),
        "method_map": METHODS,
        "narrowing": (
            "svy witnesses these because a stratified estimate is design-based, "
            "which is what D2.9's conclusion about the BINOMIAL intervals does not "
            "reach. It reproduces our point estimate, standard error and degrees "
            "of freedom exactly. It does not independently confirm the method: it "
            "is an implementation, not a published table like Barnett Table 2B."
        ),
        "not_offered": (
            "svy's 'korn-graubard' adds NCHS truncation of the effective sample "
            "size. It is a third construction and this version does not offer it "
            "-- deferred by name rather than absent by accident."
        ),
        "cases": cases,
    }
    Path(out_path).write_text(json.dumps(payload, indent=1), encoding="utf-8")
    print(f"wrote {out_path}: {len(cases)} designs x {len(METHODS)} methods x {len(CONFIDENCES)}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "svy/fixtures/design_intervals.json")
