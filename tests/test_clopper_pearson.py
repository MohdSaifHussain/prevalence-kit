"""D2.4 -- the Clopper-Pearson interval, checked two independent ways.

The contract's section 2.3 said Clopper-Pearson has "no published table" and
would be checked against an independent implementation we wrote ourselves. That
was pessimistic: `stats::binom.test` ships with base R, returns the
Clopper-Pearson interval, and is a different implementation lineage from
`survey`. So this has a genuinely EXTERNAL witness after all.

The independence is the point, and it is structural rather than promised:

    R              inverts an incomplete beta, via `qbeta`
    prevalence-kit root-finds on the binomial tail, in log space via `lgamma`

`lgamma` is the log of the COMPLETE gamma -- a log factorial. **There is no
incomplete beta function anywhere in this package**, so "checking betainc
against betainc" cannot happen here by construction. Two arithmetic paths, one
definition.

`r/fixtures/clopper_pearson.json` was generated and committed in `9c652fc`,
before any of this code existed. R2.2.
"""

from __future__ import annotations

import json
from functools import partial
from pathlib import Path
from typing import Any

import pytest

from prevalence_kit.errors import Reason, Refusal
from prevalence_kit.estimators import (
    _binomial_tail_at_least,
    _binomial_tail_at_most,
    _solve,
    clopper_pearson,
    wilson,
)

FIXTURE = Path(__file__).resolve().parents[1] / "r" / "fixtures" / "clopper_pearson.json"


def fixture() -> dict[str, Any]:
    parsed: dict[str, Any] = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return parsed


CASES: list[dict[str, Any]] = list(fixture()["cases"])
ALPHA_HALF = (1 - fixture()["confidence"]) / 2


def ident(case: dict[str, Any]) -> str:
    return f"k{case['k']}_n{case['n']}"


def relative(got: float, want: float) -> float:
    return abs(got - want) / abs(want) if want else abs(got)


# --------------------------------------------------- witness 1: base R, external


@pytest.mark.parametrize("case", CASES, ids=[ident(c) for c in CASES])
def test_clopper_pearson_matches_base_r(case: dict[str, Any]) -> None:
    """R2.3, against numbers base R produced before this code existed."""
    interval = clopper_pearson(case["k"], case["n"])

    assert relative(float(interval.low), case["lower"]) < 1e-4, case["note"]
    assert relative(float(interval.high), case["upper"]) < 1e-4, case["note"]
    assert interval.method == "clopper-pearson"
    assert interval.n == case["n"]
    assert interval.positives == case["k"]


def test_the_agreement_with_r_is_limited_by_our_record_not_our_method() -> None:
    """Two figures, because they measure different things and only one is ours.

    Measured 2026-08-29 across all 23 fixture cases:

        full double precision      7.1e-11   <- the method
        after DIGITS = 12 rounding 6.9e-09   <- our own record format

    The rounding is the larger of the two. That is a deliberate choice made in
    Phase 1 -- twelve decimal places is enough to reproduce and few enough that
    float noise in the last bits cannot change a digest -- and at rare-event
    rates around 1e-5 it leaves about eight significant digits.

    Recorded so nobody reads 6.9e-09 as the accuracy of the estimator. R2.3 asks
    for four significant digits and both figures clear it by orders of
    magnitude.
    """
    worst_raw = 0.0
    worst_rounded = 0.0
    for case in CASES:
        k, n = case["k"], case["n"]
        # `partial` rather than a lambda closing over the loop variables. ruff
        # flagged the late binding as fragile (B023) and mypy could not infer
        # the type of the default-argument workaround, so this satisfies both
        # and reads better than either.
        low = (
            0.0
            if k == 0
            else _solve(ALPHA_HALF, partial(_binomial_tail_at_least, k, n), rising=True)
        )
        high = (
            1.0
            if k == n
            else _solve(ALPHA_HALF, partial(_binomial_tail_at_most, k, n), rising=False)
        )
        for raw, want in ((low, case["lower"]), (high, case["upper"])):
            if want:
                worst_raw = max(worst_raw, relative(raw, want))
                worst_rounded = max(worst_rounded, relative(float(f"{raw:.12f}"), want))

    assert worst_raw < 1e-9, f"method drifted from base R: {worst_raw:.3e}"
    assert worst_rounded < 1e-7, f"record precision drifted: {worst_rounded:.3e}"
    assert worst_rounded > worst_raw, (
        "The rounded figure is no longer the larger one. If the method got worse "
        "rather than the record getting better, this test is hiding it."
    )


# ------------------------------------- witness 2: the defining property itself


@pytest.mark.parametrize("case", CASES, ids=[ident(c) for c in CASES])
def test_each_endpoint_satisfies_the_definition(case: dict[str, Any]) -> None:
    """The interval is defined by its coverage. This asserts the definition.

        P(X >= k | n, lower) = alpha/2
        P(X <= k | n, upper) = alpha/2

    Not a second way of computing the same thing -- the property the interval is
    *for*. Worst observed across all cases: 3.9e-13 relative.
    """
    k, n = case["k"], case["n"]
    interval = clopper_pearson(k, n)

    if k > 0:
        tail = _binomial_tail_at_least(k, n, float(interval.low))
        assert relative(tail, ALPHA_HALF) < 1e-6, f"lower endpoint carries {tail}, not {ALPHA_HALF}"
    if k < n:
        tail = _binomial_tail_at_most(k, n, float(interval.high))
        assert relative(tail, ALPHA_HALF) < 1e-6, f"upper endpoint carries {tail}, not {ALPHA_HALF}"


def test_the_tails_are_monotone_in_p() -> None:
    """The property bisection depends on. If it fails, `_solve` is meaningless."""
    rising = [_binomial_tail_at_least(3, 10, p / 100) for p in range(1, 100)]
    falling = [_binomial_tail_at_most(3, 10, p / 100) for p in range(1, 100)]
    assert rising == sorted(rising)
    assert falling == sorted(falling, reverse=True)


# ------------------------------------------------------------ shape and edges


@pytest.mark.parametrize(("k", "n"), [(0, 1), (0, 2), (0, 10), (0, 4000)])
def test_zero_positives_gives_a_lower_bound_of_exactly_zero(k: int, n: int) -> None:
    """Not special-cased into existence -- P(X >= 0) = 1 for every p, so the
    equation has no solution below 1 and the bound is 0 by definition."""
    interval = clopper_pearson(k, n)
    assert float(interval.low) == 0.0
    assert 0.0 < float(interval.high) < 1.0


@pytest.mark.parametrize(("k", "n"), [(1, 1), (2, 2), (10, 10)])
def test_all_positives_gives_an_upper_bound_of_exactly_one(k: int, n: int) -> None:
    interval = clopper_pearson(k, n)
    assert float(interval.high) == 1.0
    assert 0.0 < float(interval.low) < 1.0


@pytest.mark.parametrize("case", CASES, ids=[ident(c) for c in CASES])
def test_clopper_pearson_is_wider_than_wilson_except_at_zero(case: dict[str, Any]) -> None:
    """Measured, because the obvious version of this property is false.

    The first draft asserted "Clopper-Pearson is never narrower than Wilson",
    on the reasoning that it is the conservative interval. **That is wrong**, and
    this test caught it before it was committed.

    **Conservative means coverage at least 1 - alpha. It does not mean wider
    everywhere.** At k = 0 and large n, Clopper-Pearson is about 4% NARROWER.
    Both endpoints have closed forms there, so this is arithmetic, not opinion:

        Clopper-Pearson upper = 1 - (alpha/2)^(1/n)  ->  -ln(0.025)/n = 3.6889/n
        Wilson upper          = z^2 / (n + z^2)      ->        z^2/n  = 3.8415/n

    TWO RATIOS, and they are not the same number. Confusing them is C-24.

        at n = 4000, the actual widths     0.960760   <- the case here
        as n grows, the approximations     0.960281   <- the limit

    Re-derived: n = 4,000 -> 0.960760; 40,000 -> 0.960329; 4,000,000 -> 0.960281.
    Quote the first when talking about n = 4000. The second is where it is going.
    Measured across the 23 fixture cases: wider in 22, narrower in exactly one,
    which is k = 0 at n = 4000.

    So the test asserts what is true rather than what sounded right, and it
    still fails if the relationship changes anywhere else.
    """
    k, n = case["k"], case["n"]
    exact = clopper_pearson(k, n)
    score = wilson(k, n)

    width_exact = float(exact.high) - float(exact.low)
    width_score = float(score.high) - float(score.low)

    if k == 0 and n >= 4000:
        assert width_exact < width_score, (
            f"{ident(case)}: expected Clopper-Pearson to be narrower here. "
            "If that stopped being true, the docstring above needs rewriting."
        )
        # And it is narrow by the amount the closed forms predict.
        assert width_exact == pytest.approx(1 - ALPHA_HALF ** (1 / n), rel=1e-9)
    else:
        assert width_exact >= width_score - 1e-12, (
            f"{ident(case)}: Clopper-Pearson {width_exact} is narrower than Wilson {width_score}"
        )


def test_it_works_at_the_scale_that_broke_the_first_version() -> None:
    """The naive sum raised OverflowError at n = 4000.

    `comb(4000, 2000)` is an integer far too large to become a float, and
    multiplying it by `p**2000` raises rather than returning a small number. The
    log-space version has no such ceiling. This is the regression test for a
    defect that never shipped, kept because the next person writing a tail sum
    will reach for the same naive form.
    """
    for n, k in ((4000, 8), (1_999_514, 137)):
        interval = clopper_pearson(k, n)
        assert 0.0 < float(interval.low) < float(interval.high) < 1.0


# -------------------------------------------------------------------- refusals


def test_an_empty_sample_is_refused_by_name() -> None:
    with pytest.raises(Refusal) as caught:
        clopper_pearson(0, 0)
    assert caught.value.reason is Reason.EMPTY_SAMPLE


def test_more_positives_than_items_is_refused_by_name() -> None:
    with pytest.raises(Refusal) as caught:
        clopper_pearson(11, 10)
    assert caught.value.reason is Reason.LABELS_UNMATCHED


def test_a_well_formed_count_is_accepted() -> None:
    """The positive control. A gate that refuses everything proves nothing."""
    interval = clopper_pearson(5, 100)
    assert float(interval.low) < 0.05 < float(interval.high)
