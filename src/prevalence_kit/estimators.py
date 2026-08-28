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

from dataclasses import dataclass
from math import sqrt
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
