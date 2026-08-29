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
from functools import cache, partial
from math import comb, fsum
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
        after DIGITS = 12 rounding 2.7e-07   <- our own record format

    **What the second axis changed, and it is the point of adding it.** The
    figures used to read 7.1e-11 and 6.9e-09. Both were correct and both were
    measurements at confidence 0.95, which the sentence quoting them did not say.

        conf 0.90   method 8.4e-11   record 3.0e-08
        conf 0.95   method 7.1e-11   record 6.9e-09
        conf 0.99   method 5.3e-11   record 2.7e-07

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


@cache
def _bounds(
    estimator: Callable[..., Interval], n: int, confidence: float
) -> tuple[tuple[float, float], ...]:
    """Every interval for this (n, confidence), computed once.

    Cached because coverage sweeps p across a grid while the intervals depend
    only on k. Without this the tests below recompute the same n+1 bisections
    for every p and the suite goes from seconds to minutes.
    """
    out = []
    for k in range(n + 1):
        interval = estimator(k, n, confidence=confidence)
        out.append((float(interval.low), float(interval.high)))
    return tuple(out)


def coverage(estimator: Callable[..., Interval], n: int, p: float, confidence: float) -> float:
    """P(the interval covers p), computed exactly. No simulation.

    Sum the binomial pmf over every k whose interval contains p. The binomial is
    a finite sum, so this is the coverage probability itself rather than an
    estimate of it.
    """
    bounds = _bounds(estimator, n, confidence)
    return fsum(
        comb(n, k) * p**k * (1 - p) ** (n - k)
        for k, (low, high) in enumerate(bounds)
        if low <= p <= high
    )


# --------------------------------------------------------- coverage, not width
#
# This section replaces a test that asserted WHERE Clopper-Pearson is narrower
# than Wilson. That test was wrong three times running -- C-30. The root cause
# was not any of the three regions. It was that a region was being asserted at
# all: where a derived property holds depends on n, k and confidence with no
# simple closed form, so every hand-written description is false at the next
# corner nobody sampled.
#
# Conservative has a definition. Coverage >= 1 - alpha for every true p.
# Clopper-Pearson guarantees it; Wilson does not. Width is a consequence, and
# consequences vary. So the tests below assert the definition.
#
# The expected values are S-1.1's own published figures -- Brown, Cai &
# DasGupta (2001), full text read 2026-08-29. Nobody in this project computed
# them. That makes them the same kind of evidence as Barnett Table 2B, and the
# only external anchor this project has for its INTERVAL CHOICE as opposed to
# its arithmetic.


@pytest.mark.parametrize("n", [10, 25, 50, 100])
@pytest.mark.parametrize("confidence", [0.90, 0.95, 0.99])
def test_clopper_pearson_never_covers_less_than_nominal(n: int, confidence: float) -> None:
    """The defining property, from S-1.1 section 4.2.1, verbatim:

        "The Clopper-Pearson interval guarantees that the actual coverage
         probability is always equal to or above the nominal confidence level."

    This is why the charter ships it as the conservative option. It is a
    guarantee, not a tendency, so it is asserted over a grid of p rather than
    described.
    """
    for i in range(1, 200):
        p = i / 200
        got = coverage(clopper_pearson, n, p, confidence)
        assert got >= confidence - 1e-12, (
            f"Clopper-Pearson covered {got:.4f} at n={n}, p={p}, nominal {confidence}. "
            "That contradicts S-1.1 section 4.2.1, which is a guarantee."
        )


def test_wilson_undercovers_in_the_rare_event_regime_as_the_anchor_says() -> None:
    """Wilson does NOT guarantee coverage, and S-1.1 says where it fails.

    Section 4.1.1, verbatim:

        "The coverage has downward spikes when p is very near 0 or 1. These
         spikes exist for all n and alpha. For example, it can be shown that,
         when 1 - alpha = 0.95 and p = 0.1765/n, lim P(p in CIW) = 0.838 and
         when 1 - alpha = 0.99 and p = 0.1174/n, lim = 0.889."

    **This is the contrast the project had never written down, and it matters
    more than the width question ever did.** Wilson is the charter's primary
    interval. At rare-event prevalence -- the regime this tool exists for -- its
    coverage drops to 0.838 against a nominal 0.95.

    Reproduced here, which also makes these published numbers a third external
    witness: computed by the method's own authors, with nobody in this project
    involved.
    """
    for n in (200, 500, 1000, 2000):
        assert coverage(wilson, n, 0.1765 / n, 0.95) == pytest.approx(0.838, abs=5e-4)
        assert coverage(wilson, n, 0.1174 / n, 0.99) == pytest.approx(0.889, abs=5e-4)


def test_wilsons_worst_rare_event_coverage_matches_the_published_limit() -> None:
    """S-1.1 section 3.2, verbatim, for the Wilson interval at 1 - alpha = 0.95:

        lim inf over gamma >= 1 of C(gamma/n, n) = 0.92

    So across the whole rare-event regime -- p a small multiple of 1/n -- Wilson
    bottoms out around 0.92 against a nominal 0.95. Clopper-Pearson does not,
    which is the whole reason both ship.
    """
    worst = 1.0
    for n in (500, 1000, 2000):
        for step in range(200):
            worst = min(worst, coverage(wilson, n, (1 + step * 0.05) / n, 0.95))

    assert worst == pytest.approx(0.920, abs=2e-3), f"observed {worst:.4f}, S-1.1 says 0.920"


def test_clopper_pearson_holds_where_wilson_does_not() -> None:
    """The pair, side by side, at the point S-1.1 names as Wilson's worst.

    The positive control for the negative result above: at exactly the p where
    Wilson falls to 0.838, Clopper-Pearson is still at or above nominal. Without
    this, the test above only shows that some interval undercovers somewhere.
    """
    n = 1000
    p = 0.1765 / n

    assert coverage(wilson, n, p, 0.95) < 0.95
    assert coverage(clopper_pearson, n, p, 0.95) >= 0.95


def test_the_width_comparison_is_a_measurement_with_stated_scope() -> None:
    """What is left of the width question, stated as a fact rather than a rule.

    C-30 records three attempts to say WHERE Clopper-Pearson is narrower than
    Wilson, each falsified by widening the grid. The lesson is that a region
    description is a summary of the grid you happened to sample.

    So this records a count with its scope and asserts nothing about inputs
    outside it. Over the fixture's 69 cases -- n in {1, 2, 10, 20, 40, 100, 4000,
    1999514}, k across each, confidence in {0.90, 0.95, 0.99} -- Clopper-Pearson
    was narrower than Wilson in 7. It says nothing about the 70th case, and it
    is not supposed to.
    """
    narrower = [
        case
        for case in CASES
        if (
            float(clopper_pearson(case["k"], case["n"], confidence=case["conf"]).high)
            - float(clopper_pearson(case["k"], case["n"], confidence=case["conf"]).low)
        )
        < (
            float(wilson(case["k"], case["n"], confidence=case["conf"]).high)
            - float(wilson(case["k"], case["n"], confidence=case["conf"]).low)
        )
    ]

    assert len(narrower) == 7, (
        f"{len(narrower)} of {len(CASES)} fixture cases have Clopper-Pearson narrower. "
        "This is a measurement over one grid, not a rule -- if the fixture changed, "
        "re-measure and update the number. Do not infer a region from it."
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
