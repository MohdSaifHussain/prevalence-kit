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
from collections.abc import Callable
from functools import partial
from pathlib import Path
from typing import Any

import pytest

from prevalence_kit.errors import Reason, Refusal
from prevalence_kit.estimators import (
    Interval,
    _binomial_tail_at_least,
    _binomial_tail_at_most,
    _solve,
    clopper_pearson,
    rogan_gladen_interval,
    wilson,
)

FIXTURE = Path(__file__).resolve().parents[1] / "r" / "fixtures" / "clopper_pearson.json"


def fixture() -> dict[str, Any]:
    parsed: dict[str, Any] = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return parsed


CASES: list[dict[str, Any]] = list(fixture()["cases"])
CONF_LEVELS: list[float] = list(fixture()["confidence_levels"])
"""The fixture varies confidence now, so nothing here may assume 0.95.

Before 2026-08-29 every case was at 0.95 and the agreement figures did not
say so. `alpha/2` was a module constant, which is what made the assumption
invisible: it read as a property of the method rather than of one column.
"""


def alpha_half(case: dict[str, Any]) -> float:
    """Half the tail mass for THIS case, not for the fixture."""
    return float(1 - case["conf"]) / 2


def ident(case: dict[str, Any]) -> str:
    return f"k{case['k']}_n{case['n']}_c{case['conf']}"


def relative(got: float, want: float) -> float:
    return abs(got - want) / abs(want) if want else abs(got)


# --------------------------------------------------- witness 1: base R, external


@pytest.mark.parametrize("case", CASES, ids=[ident(c) for c in CASES])
def test_clopper_pearson_matches_base_r(case: dict[str, Any]) -> None:
    """R2.3, against numbers base R produced before this code existed.

    Now across three confidence levels as well as eight orders of magnitude in
    n. The confidence comes from the case, so a fixture row at 0.90 is checked
    at 0.90 -- previously every row was compared against a 0.95 computation
    because there were no other rows to get wrong.
    """
    interval = clopper_pearson(case["k"], case["n"], confidence=case["conf"])

    assert relative(float(interval.low), case["lower"]) < 1e-4, case["note"]
    assert relative(float(interval.high), case["upper"]) < 1e-4, case["note"]
    assert interval.method == "clopper-pearson"
    assert interval.n == case["n"]
    assert interval.positives == case["k"]


def test_the_agreement_with_r_is_limited_by_our_record_not_our_method() -> None:
    """Two figures, because they measure different things and only one is ours.

    **Stated with their axes, which the earlier version of this docstring did
    not do.** Measured across all 69 fixture cases: n from 1 to 1,999,514, k
    across each, confidence in {0.90, 0.95, 0.99}.

        full double precision      8.4e-11   <- the method
        after DIGITS = 12 rounding 2.6e-07   <- our own record format

    **What the second axis changed, and it is the point of adding it.** The
    figures used to read 7.1e-11 and 6.9e-09. Both were correct and both were
    measurements at confidence 0.95, which the sentence quoting them did not say.

        conf 0.90   method 8.4e-11   record 3.0e-08
        conf 0.95   method 7.1e-11   record 6.9e-09
        conf 0.99   method 5.3e-11   record 2.6e-07

    **The method figure barely moved. The record figure moved by a factor of 38.**
    That is not noise, and it is worth understanding rather than absorbing:
    `DIGITS = 12` is a fixed number of decimal places, so it costs a fixed
    absolute precision. At higher confidence the rare-event lower bounds get
    smaller -- k=1, n=4000 at 0.99 has a lower bound of 1.25e-06 -- and a fixed
    absolute error is a larger relative one against a smaller number.

    So the honest sentence is: **the estimator is accurate across the range, and
    our record format is the binding constraint, more so the smaller the number.**

    R2.3 asks for four significant digits. Both figures clear it by at least
    three orders of magnitude, at every level measured.
    """
    worst_raw = 0.0
    worst_rounded = 0.0
    for case in CASES:
        k, n = case["k"], case["n"]
        half = alpha_half(case)
        # `partial` rather than a lambda closing over the loop variables. ruff
        # flagged the late binding as fragile (B023) and mypy could not infer
        # the type of the default-argument workaround, so this satisfies both
        # and reads better than either.
        low = 0.0 if k == 0 else _solve(half, partial(_binomial_tail_at_least, k, n), rising=True)
        high = 1.0 if k == n else _solve(half, partial(_binomial_tail_at_most, k, n), rising=False)
        for raw, want in ((low, case["lower"]), (high, case["upper"])):
            if want:
                worst_raw = max(worst_raw, relative(raw, want))
                worst_rounded = max(worst_rounded, relative(float(f"{raw:.12f}"), want))

    assert worst_raw < 1e-9, f"method drifted from base R: {worst_raw:.3e}"
    assert worst_rounded < 1e-6, f"record precision drifted: {worst_rounded:.3e}"
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
    *for*. Worst observed: 3.9e-13 relative, across 69 cases spanning n = 1 to
    1,999,514 and confidence in {0.90, 0.95, 0.99}.
    """
    k, n, conf = case["k"], case["n"], case["conf"]
    half = alpha_half(case)
    interval = clopper_pearson(k, n, confidence=conf)

    if k > 0:
        tail = _binomial_tail_at_least(k, n, float(interval.low))
        assert relative(tail, half) < 1e-6, f"lower endpoint carries {tail}, not {half}"
    if k < n:
        tail = _binomial_tail_at_most(k, n, float(interval.high))
        assert relative(tail, half) < 1e-6, f"upper endpoint carries {tail}, not {half}"


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
def test_clopper_pearson_is_narrower_than_wilson_only_near_the_boundary(
    case: dict[str, Any],
) -> None:
    """Measured, because the obvious version of this property is false -- twice.

    **First draft:** "Clopper-Pearson is never narrower than Wilson", reasoning
    that it is the conservative interval. Wrong. Conservative means coverage at
    least 1 - alpha; it does not mean wider everywhere.

    **Second draft, and this is the one the confidence axis caught.** The test
    was renamed `..._except_at_zero` and its docstring said *"narrower in exactly
    one, which is k = 0 at n = 4000"*. That was true of the 23 cases it had --
    and all 23 were at confidence 0.95. The exception set is not k = 0. C-30.

    Re-measured across all 69 cases, three confidence levels:

        conf 0.90    0 narrower
        conf 0.95    1 narrower   k=0 n=4000
        conf 0.99    6 narrower   k=0,1 n=4000; k=1,39 n=40; k=1,99 n=100

    **The real property is about the boundary, not about zero**, and the region
    grows as confidence rises: Clopper-Pearson is narrower only when k is within
    one of an endpoint. So that is what this asserts.

    The closed forms at k = 0 still say why:

        Clopper-Pearson upper = 1 - (alpha/2)^(1/n)
        Wilson upper          = z^2 / (n + z^2)

    At 0.95 those give 3.6889/n against 3.8415/n, ratio 0.960760 at n = 4000.
    That ratio is a 0.95 statement and always was -- at 0.99 the same case is
    0.799348. C-24 was about confusing two ratios; this is about quoting one
    without its confidence level.
    """
    k, n, conf = case["k"], case["n"], case["conf"]
    exact = clopper_pearson(k, n, confidence=conf)
    score = wilson(k, n, confidence=conf)

    width_exact = float(exact.high) - float(exact.low)
    width_score = float(score.high) - float(score.low)
    near_boundary = k <= 1 or k >= n - 1

    if width_exact < width_score:
        assert near_boundary, (
            f"Clopper-Pearson is narrower than Wilson at k={k}, n={n}, conf={conf}, "
            "which is not near a boundary. The characterisation in this docstring "
            "is wrong again -- re-measure before changing the assertion."
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


# ------------------------------------------------------------------- F-8
#
# `confidence` was unvalidated in every interval estimator. Found by D2.7's
# boundary hunt, not at a review stop.


@pytest.mark.parametrize("bad", [-0.5, 0.0, 1.0, 1.5, 2.0])
@pytest.mark.parametrize("estimator", [wilson, clopper_pearson])
def test_a_confidence_outside_zero_to_one_is_refused_by_name(
    estimator: Callable[..., Interval], bad: float
) -> None:
    """The negative control, on both estimators and both kinds of bad input.

    Before this guard, the two failed differently and both failures were wrong:

        wilson(5, 100, confidence=1.0)    StatisticsError traceback
        wilson(5, 100, confidence=-0.5)   [0.066846, 0.037230] -- inverted
        clopper_pearson(5, 100, -0.5)     [0.062031, 0.042361] -- inverted

    The traceback breaks rule 5, which wants refusals named. The inverted
    interval is worse: no error at all, a lower bound above its upper bound, and
    the point estimate outside both. A silently wrong number is the one thing
    the charter says this tool must never produce.

    The endpoints are refused too, not only values outside. At 1.0 the normal
    quantile is undefined; at 0.0 the interval collapses and claims nothing.
    """
    with pytest.raises(Refusal) as caught:
        estimator(5, 100, confidence=bad)

    assert caught.value.reason is Reason.PLAN_INVALID
    assert str(bad) in caught.value.detail, "the operator must see the value they gave"
    assert "0.95" in caught.value.fix, "R8: say what to set it to"


@pytest.mark.parametrize("good", [0.5, 0.9, 0.95, 0.99, 0.999])
@pytest.mark.parametrize("estimator", [wilson, clopper_pearson])
def test_ordinary_confidence_levels_are_accepted(
    estimator: Callable[..., Interval], good: float
) -> None:
    """The positive control. A gate that refuses everything proves nothing.

    Also checks the interval stays sane across the range, since the defect being
    closed was an interval that came back inverted rather than an exception.
    """
    got = estimator(5, 100, confidence=good)

    assert float(got.low) <= float(got.point) <= float(got.high)
    assert 0.0 <= float(got.low) <= float(got.high) <= 1.0


def test_a_wider_confidence_gives_a_wider_interval() -> None:
    """The property the guard exists to protect, asserted rather than assumed.

    If confidence and width ever stop moving together, something is wrong with
    the arithmetic and not just with the input checking.
    """
    for estimator in (wilson, clopper_pearson):
        widths = [
            float(estimator(5, 100, confidence=c).high) - float(estimator(5, 100, confidence=c).low)
            for c in (0.80, 0.90, 0.95, 0.99)
        ]
        assert widths == sorted(widths), f"{estimator.__name__} widths not monotone: {widths}"


def test_the_corrected_interval_inherits_the_confidence_guard() -> None:
    """`rogan_gladen_interval` builds on `clopper_pearson`, so it is covered too.

    Asserted rather than assumed, because "it calls the guarded function" is the
    kind of reasoning that stops being true after a refactor.
    """
    with pytest.raises(Refusal) as caught:
        rogan_gladen_interval(
            45, 150, 0.96, 0.89, interval_method="clopper_pearson", confidence=1.5
        )

    assert caught.value.reason is Reason.PLAN_INVALID
