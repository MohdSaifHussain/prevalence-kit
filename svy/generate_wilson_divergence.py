"""D2.10 / O-13 -- how far `svy`'s design-based Wilson is from the textbook one.

**Runs in a throwaway environment only.** Same reasoning as the allocation
generator: `svy` needs `httpx`, Hard Rule 1 forbids that in the runtime tree, so
only the output is committed.

    /tmp/svyvenv/bin/python svy/generate_wilson_divergence.py svy/fixtures/wilson_divergence.json

**What O-13 asks and why it exists.** **D-18** read `svy`'s source and found its
Wilson is a *different estimator* -- it replaces `n` with an effective sample size
`n_eff = p(1-p)/se^2` and uses a t-quantile rather than a normal one. D-18 then
said, in its own words, that the builder's claim the two "will not agree to 4
significant digits at small n" was **a claim about magnitude that the evidence did
not carry**, and carried the measurement forward as **O-13**. This is that
measurement.

**The invocation is `svy`'s, not ours.** The interval is taken from a real
`Estimation.prop(..., ci_method="wilson")` call on a design `svy` builds, so the
standard error and degrees of freedom come from `svy` rather than from values we
choose. Handing an internal helper our own `se` and `df` would make the comparison
a function of our inputs -- §2.2's residual, where the witness is external and the
invocation is still the builder's.

**Every figure states its axes.** `n`, `k` and the confidence level all vary and
all are recorded per row, because a divergence figure without them is exactly the
class C-30 records -- and the intervals half of D2.9 has just finished proving
what a same-name-different-thing assumption costs.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy
import polars as pl
import svy

# Small n is the whole point of O-13: that is where a design-based interval and a
# textbook one have the most room to disagree.
SAMPLE_SIZES = [10, 20, 40, 80, 160, 500, 1000]
CONFIDENCES = [0.90, 0.95, 0.99]


def svy_wilson(k: int, n: int, alpha: float) -> dict[str, float]:
    """svy's Wilson interval for k positives out of n, from svy's own design.

    A simple random sample of `n` units with `k` ones: equal weights, no strata,
    each unit its own PSU -- the design our SRS path actually draws. `prop`
    returns one row per level of `y`; we take `y_level == 1`.

    `se` and `df` are recorded because they are what makes this a *different*
    estimator: `svy` derives `n_eff` from its own `se` and uses a t-quantile on
    its own `df`. Keeping them in the fixture means a later reader can see where
    the divergence comes from rather than only how big it is.
    """
    frame = pl.DataFrame(
        {
            "unit": list(range(n)),
            "y": [1] * k + [0] * (n - k),
            "wgt": [1.0] * n,
        }
    )
    design = svy.Design(row_index="unit", wgt="wgt", psu="unit")
    est = svy.Estimation(svy.Sample(frame, design)).prop("y", ci_method="wilson", alpha=alpha)
    for row in est.to_dicts():
        if int(row["y_level"]) == 1:
            return {
                "point": float(row["est"]),
                "low": float(row["lci"]),
                "high": float(row["uci"]),
                "se": float(row["se"]),
                "df": int(row["df"]),
            }
    raise RuntimeError(f"no y_level == 1 row for k={k}, n={n}")


def main(out_path: str) -> None:
    rows = []
    failures = []
    for n in SAMPLE_SIZES:
        # k across the whole range, densely at the rare-event end where this
        # tool operates and where the two constructions differ most.
        ks = sorted({0, 1, 2, 3, n // 4, n // 2, n - 1, n})
        for k in ks:
            if not 0 <= k <= n:
                continue
            for conf in CONFIDENCES:
                try:
                    got = svy_wilson(k, n, 1 - conf)
                except Exception as exc:
                    failures.append(
                        {
                            "n": n,
                            "k": k,
                            "confidence": conf,
                            "error": f"{type(exc).__name__}: {exc}",
                        }
                    )
                    continue
                rows.append({"n": n, "k": k, "confidence": conf, **got})

    payload = {
        "what": "svy's design-based Wilson interval, for O-13's magnitude measurement",
        "deliverable": "D2.10",
        "register": "S-2.2",
        "obligation": "O-13",
        "svy_version": getattr(svy, "__version__", "unknown"),
        "numpy_version": numpy.__version__,
        "polars_version": pl.__version__,
        "python": sys.version.split()[0],
        "exact_call": (
            "svy.Estimation(svy.Sample(frame, svy.Design(row_index='unit', "
            "wgt='wgt', psu='unit'))).prop('y', ci_method='wilson', "
            "alpha=1-confidence), taking the y_level == 1 row"
        ),
        "axes": {
            "n": SAMPLE_SIZES,
            "k": "0, 1, 2, 3, n//4, n//2, n-1, n (deduplicated)",
            "confidence": CONFIDENCES,
        },
        "narrowing": (
            "svy's Wilson replaces n with an effective sample size and uses a "
            "t-quantile (D-18). This measures HOW FAR that puts it from the "
            "textbook interval at these points. It is not a general property of "
            "the two methods and must not be quoted as one."
        ),
        "rows": rows,
        "failures": failures,
    }
    Path(out_path).write_text(json.dumps(payload, indent=1), encoding="utf-8")
    print(f"wrote {out_path}: {len(rows)} rows, {len(failures)} failures")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "svy/fixtures/wilson_divergence.json")
