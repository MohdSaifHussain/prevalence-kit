"""Prevalence estimation.

Phase 1 ships one interval: Wilson. Phase 2 adds Clopper-Pearson.

Method anchor: Brown, L.D., Cai, T.T., DasGupta, A. (2001), "Interval Estimation
for a Binomial Proportion", Statistical Science 16(2), DOI 10.1214/ss/1009213286.
docs/STANDARDS.md S-1.1, docs/DECISIONS.md D-8.

Wald is not implemented, deliberately. At the prevalence rates this tool exists
to measure -- a fraction of a percent -- Wald's interval is wrong in the
direction that flatters the platform, and an estimator you must remember not to
use is a defect waiting for a deadline.

The normal quantile comes from `statistics.NormalDist.inv_cdf`, standard library
and documented since 3.8. That keeps SciPy out of the runtime dependency tree,
which Hard Rule 1 cares about.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from math import exp, fsum, lgamma, log, log1p, sqrt
from statistics import NormalDist

from .canonical import JSONObject
from .errors import Reason, Refusal

DIGITS = 12
"""Decimal places carried in the record. Enough to reproduce, few enough that
platform float noise in the last bits cannot change a digest."""


@dataclass(frozen=True, slots=True)
class Interval:
    """A point estimate and its interval. Stored as strings; see canonical.py."""

    method: str
    point: str
    low: str
    high: str
    confidence: str
    n: int
    positives: int

    def as_record(self) -> JSONObject:
        return {
            "method": self.method,
            "point": self.point,
            "low": self.low,
            "high": self.high,
            "confidence": self.confidence,
            "n": self.n,
            "positives": self.positives,
        }


def wilson(positives: int, n: int, *, confidence: float = 0.95) -> Interval:
    """Wilson score interval for a binomial proportion.

        centre = (p + z^2/2n) / (1 + z^2/n)
        half   = z/(1 + z^2/n) * sqrt( p(1-p)/n + z^2/(4n^2) )

    Correct at p = 0 and p = 1, which is why it is the default here: a
    measurement that finds no violations still has to report an upper bound.
    """
    if n <= 0:
        raise Refusal(
            Reason.EMPTY_SAMPLE,
            "No sampled items, so there is no interval to compute.",
            "Draw a sample before estimating.",
        )
    if not 0 <= positives <= n:
        raise Refusal(
            Reason.LABELS_UNMATCHED,
            f"{positives} positives out of {n} items is not possible.",
            "The labels do not line up with the sample. Re-run ingest-labels.",
        )

    z = NormalDist().inv_cdf(1 - (1 - confidence) / 2)
    p = positives / n
    zsq_n = z * z / n
    denom = 1 + zsq_n
    centre = (p + zsq_n / 2) / denom
    half = (z / denom) * sqrt(p * (1 - p) / n + zsq_n / (4 * n))

    return Interval(
        method="wilson",
        point=_fixed(p),
        low=_fixed(max(0.0, centre - half)),
        high=_fixed(min(1.0, centre + half)),
        confidence=_fixed(confidence),
        n=n,
        positives=positives,
    )


def _fixed(x: float) -> str:
    return f"{x:.{DIGITS}f}"


def _log_pmf(n: int, i: int, p: float) -> float:
    """log P(X = i) for X ~ Binomial(n, p), via log factorials.

    `lgamma` is the log of the COMPLETE gamma function -- a factorial. It is not
    an incomplete beta, and nothing here inverts one. That distinction is the
    whole point of this module's independence from the R witness.
    """
    return lgamma(n + 1) - lgamma(i + 1) - lgamma(n - i + 1) + i * log(p) + (n - i) * log1p(-p)


def _sum_from(k: int, n: int, p: float, *, upward: bool) -> float:
    """Sum binomial terms outward from k until they stop mattering.

    Only terms within a few standard deviations of the mode carry any weight, so
    this is O(sqrt(n)) work rather than O(n). At Civil Comments scale --
    n = 1,999,514 -- that is a few thousand terms against two million.

    And the naive sum does not merely run slowly. `comb(4000, 2000) * p**2000`
    raises OverflowError, because the integer cannot be converted to a float.
    Working in logs removes both problems, and this docstring records that the
    first version of this function hit exactly that at n = 4000.
    """
    terms: list[float] = []
    total = 0.0
    indices = range(k, n + 1) if upward else range(k, -1, -1)
    for i in indices:
        term = exp(_log_pmf(n, i, p))
        terms.append(term)
        total += term
        # Stop once the tail is spent: a term negligible against what we already
        # have. Never on the first step, or we would stop before starting.
        if i != k and (term == 0.0 or term < 1e-22 * total):
            break
    return fsum(terms)


def _binomial_tail_at_least(k: int, n: int, p: float) -> float:
    """P(X >= k) for X ~ Binomial(n, p). The definition, no special functions.

    Computed from whichever side is the SHORT tail, complemented when needed.
    Summing through the mode would cost O(n) terms and buy nothing.
    """
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    if p <= 0.0:
        return 0.0
    if p >= 1.0:
        return 1.0
    if k > (n + 1) * p:
        return _sum_from(k, n, p, upward=True)
    return 1.0 - _sum_from(k - 1, n, p, upward=False)


def _binomial_tail_at_most(k: int, n: int, p: float) -> float:
    """P(X <= k) for X ~ Binomial(n, p)."""
    if k >= n:
        return 1.0
    if k < 0:
        return 0.0
    if p <= 0.0:
        return 1.0
    if p >= 1.0:
        return 0.0
    if k < (n + 1) * p:
        return _sum_from(k, n, p, upward=False)
    return 1.0 - _sum_from(k + 1, n, p, upward=True)


def _solve(target: float, tail: Callable[[float], float], rising: bool) -> float:
    """Bisect for the p where `tail(p) == target`. Both tails are monotone in p.

    Bisection rather than Newton on purpose. It cannot diverge, it needs no
    derivative, and an outsider can reimplement it in five lines -- which is the
    bar D-16's keyed sort was chosen to meet, applied to an interval.

    100 halvings takes the bracket below 1e-30, far under double precision, so
    this converges to the representable limit rather than to a tolerance.
    """
    low, high = 0.0, 1.0
    for _ in range(100):
        mid = (low + high) / 2
        if (tail(mid) < target) == rising:
            low = mid
        else:
            high = mid
    return (low + high) / 2


def clopper_pearson(positives: int, n: int, *, confidence: float = 0.95) -> Interval:
    """The Clopper-Pearson exact interval, from its definition.

    The interval is DEFINED by its coverage, not by a formula:

        lower p_L solves   P(X >= k | n, p_L) = alpha/2
        upper p_U solves   P(X <= k | n, p_U) = alpha/2

    Most implementations reach the same numbers through beta quantiles, because
    the binomial tail and the incomplete beta are the same function. This one
    solves the definition directly: binomial terms in log space via `lgamma`,
    summed, and bisected. `lgamma` is the COMPLETE gamma -- a log factorial.
    There is no incomplete beta function anywhere in this package.

    That is deliberate, and it is what makes the check independent. R's
    `stats::binom.test` inverts an incomplete beta via `qbeta`; we root-find on
    the tail. Agreement between them is evidence, where two routes through the
    same beta function would only ever be evidence about the beta function.
    `r/fixtures/clopper_pearson.json`, generated before this code existed.

    Anchor: S-1.1 Brown, Cai & DasGupta (2001), DOI 10.1214/ss/1009213286, which
    is also why this ships beside Wilson rather than instead of it. Clopper-
    Pearson never under-covers and is usually wider than it needs to be; Wilson
    is the primary and this is the conservative second. D-8.

    Exact at the ends by definition rather than by special-casing: at k = 0 the
    lower bound is 0 because P(X >= 0) = 1 for every p, and at k = n the upper
    bound is 1 for the mirror reason.
    """
    if n <= 0:
        raise Refusal(
            Reason.EMPTY_SAMPLE,
            "No sampled items, so there is no interval to compute.",
            "Draw a sample before estimating.",
        )
    if not 0 <= positives <= n:
        raise Refusal(
            Reason.LABELS_UNMATCHED,
            f"{positives} positives out of {n} items is not possible.",
            "The labels do not line up with the sample. Re-run ingest-labels.",
        )

    alpha_half = (1 - confidence) / 2

    # P(X >= k | p) rises with p, so the lower bound is where it reaches alpha/2.
    low = (
        0.0
        if positives == 0
        else _solve(alpha_half, lambda p: _binomial_tail_at_least(positives, n, p), rising=True)
    )
    # P(X <= k | p) falls with p, so the upper bound is where it drops to alpha/2.
    high = (
        1.0
        if positives == n
        else _solve(alpha_half, lambda p: _binomial_tail_at_most(positives, n, p), rising=False)
    )

    return Interval(
        method="clopper-pearson",
        point=_fixed(positives / n),
        low=_fixed(low),
        high=_fixed(high),
        confidence=_fixed(confidence),
        n=n,
        positives=positives,
    )
