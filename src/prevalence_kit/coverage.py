"""What a confidence level actually delivers -- **O-25 / D-37 condition 3**.

A report that prints *95% interval* and stops has told the reader the label on
the box. **This module carries what the box contains**: the measured coverage of
each interval this tool ships, at each nominal level, in the rare-event regime it
is built for.

**Why the figures live here as data rather than being computed at emission.**
Coverage at one true rate costs one interval per possible outcome. Measured on
this machine: Wilson at n = 500 is 0.002s, and **Clopper-Pearson at n = 500 is
3.3s**, growing with n -- the root-find is per outcome. A report that took
minutes at n = 2000, or that computed coverage through a second, faster
construction than the one it shipped, would be worse than one that quotes a
measurement and says what the measurement covers. **So the report quotes, and
every figure it quotes is checked against the artifact that produced it.**

**Every number below is a worst value over a grid**, so the true worst is **at
most** this and may be lower, and each is rounded **DOWN** rather than to
nearest. Rounding to nearest would round toward the middle and claim coverage
never falls below a level the measurement already shows it falls below --
**C-32**, the director's, in the charter.

**Where each figure comes from, and the two are not the same kind of evidence.**

- The binomial rows are read from `r/fixtures/coverage.json`, produced in the
  digest-pinned R image by `r/coverage_fixtures.R`, which validates itself
  against three of **S-1.1**'s published limits before reporting anything.
- The design rows are **our own arithmetic on our own estimators**. There is no
  published table for them and no library computes them; what makes them
  checkable is that the enumeration is exact and reproducible, not that anyone
  else has done it. `tests/test_coverage_disclosure.py` recomputes each one from
  the shipped estimators.
"""

from __future__ import annotations

from dataclasses import dataclass

DISCLOSURE_DIGITS = 4
"""Four places. A coverage figure is a probability and the fifth place is noise."""

RARE_EVENT_GAMMA = (0.5, 15.0)
"""The regime the binomial measurement covers: true rate `p = gamma / n`.

**S-1.1 section 4.1.1's regime**, and the one `r/coverage_fixtures.R` sweeps.
A run whose `gamma = p * n` falls outside it is outside the measurement, and the
report says so rather than quoting a figure at it.
"""

MEASURED_N = (100, 500, 1000)
"""The sample sizes `r/fixtures/coverage.json` was measured at.

**It is a second axis and it needed saying separately.** The first draft of the
report told a run at `n = 40` that it sat *inside the measured regime*, because
its `gamma` was inside the swept range -- and its sample size was not one of the
three ever measured. Binomial coverage oscillates with `n`, so a worst case at
`n = 1000` does not bound `n = 40`. **Two axes, two statements**: the same defect
C-30 recorded, caught here by reading the rendered report rather than the code.
"""


@dataclass(frozen=True, slots=True)
class Measured:
    """One measured worst-case coverage, with the conditions that produced it.

    `where` is not decoration. A coverage figure without its axes is the defect
    C-30 recorded three times, and a **worst**-over-a-grid figure without its
    grid is the defect C-32 and C-33 recorded three more.
    """

    method: str
    confidence: float
    coverage: float
    where: str


BINOMIAL: tuple[Measured, ...] = (
    Measured("wilson", 0.90, 0.8531, "n = 1000, p = gamma/n, gamma in [0.5, 15] step 0.25"),
    Measured("wilson", 0.95, 0.9098, "n = 1000, p = gamma/n, gamma in [0.5, 15] step 0.25"),
    Measured("wilson", 0.99, 0.9595, "n = 1000, p = gamma/n, gamma in [0.5, 15] step 0.25"),
    Measured("clopper_pearson", 0.90, 0.9021, "n = 100, p = gamma/n, gamma in [0.5, 15] step 0.25"),
    Measured("clopper_pearson", 0.95, 0.9520, "n = 500, p = gamma/n, gamma in [0.5, 15] step 0.25"),
    Measured("clopper_pearson", 0.99, 0.9906, "n = 500, p = gamma/n, gamma in [0.5, 15] step 0.25"),
)
"""Worst measured coverage across n in {100, 500, 1000}, from `r/fixtures/coverage.json`.

**Clopper-Pearson holds its nominal level at every one of these points and Wilson
does not.** That is the trade D-37 refused to make for the operator, stated as
the numbers rather than as an adjective.
"""

DESIGN: tuple[Measured, ...] = (
    Measured("design_wilson", 0.90, 0.0000, "design `wide`, true rate 0.001"),
    Measured("design_wilson", 0.95, 0.0000, "design `wide`, true rate 0.001"),
    Measured("design_wilson", 0.99, 0.2938, "design `two_stratum`, true rate 0.001"),
    Measured("design_korn_graubard", 0.90, 0.7472, "design `rare`, true rate 0.01"),
    Measured("design_korn_graubard", 0.95, 0.7937, "design `rare`, true rate 0.01"),
    Measured("design_korn_graubard", 0.99, 0.8549, "design `rare`, true rate 0.01"),
)
"""Worst measured **conditional** coverage -- charter section 8, amendment A-6.

**Conditional on the interval existing.** At rare rates the design standard error
is frequently zero and there is no interval to cover anything; that is a
different failure and it is disclosed separately, by `sample`, before the label
budget is spent.

**Neither design interval holds its nominal level**, and the name
`design_korn_graubard` exists because the draft name `design_clopper_pearson`
would have promised that it did.
"""

DESIGN_GRID = "four stratified design structures at eight true rates"
"""What the design sweep covered, as data rather than as a sentence in the report.

**A grid described in prose beside a number is how a figure and its axes come
apart** -- C-30, three times. The renderer quotes this; it does not compose its
own description of a measurement it did not make.
"""

NOTICE_THRESHOLD = 0.05
"""Below this, the odds of no interval are recorded but not announced.

**The threshold is the builder's and is stated as such.** D-41 ruled that the
odds are stated rather than refused on; it did not rule a number for when a
notice is worth an operator's attention. `sample` and the report use this one
value so the two artifacts cannot disagree about what was worth saying.
"""

_ALL = BINOMIAL + DESIGN


def measured_for(method: str, confidence: float) -> Measured | None:
    """The measured figure for a method at a nominal level, or `None`.

    **`None` is a real answer and the caller must render it as one.** A
    confidence level this project has never measured at gets a report that says
    so, not a report that quotes the nearest level it has.
    """
    for row in _ALL:
        if row.method == method and abs(row.confidence - confidence) < 1e-12:
            return row
    return None


def gamma_for(point: float, n: int) -> float:
    """`gamma = p * n`, the axis the binomial measurement is swept along."""
    return point * n


def in_rare_event_regime(point: float, n: int) -> bool:
    """Is this run's operating point inside the regime that was measured?

    **This is the sentence that keeps the figure honest.** The measurement is a
    worst case over a stated grid; a run sitting outside that grid is not
    described by it, and saying so costs one line and prevents a reader taking a
    bound for a measurement of their own run.
    """
    low, high = RARE_EVENT_GAMMA
    return low <= gamma_for(point, n) <= high


def disclosure(method: str, confidence: str, point: str, n: int) -> dict[str, object]:
    """The coverage block the report renders and the JSON report carries.

    Returns the measured figure, its conditions, and **where this run sits
    relative to the measurement** -- never a coverage computed for this run,
    because none was computed. D-37 condition 3 asks what the choice cost on this
    data; the honest answer names the measurement and its distance from here.

    **Every number out of here is a decimal string, and that is not a style
    choice.** This block goes into `report.json`, which is canonicalised and
    digested, and `canonical()` refuses floats outright because they do not
    round-trip identically across platforms. `expected_rate` learned the same
    thing at D-39, by the same route: the record refused to hash.
    """
    row = measured_for(method, float(confidence))
    block: dict[str, object] = {
        "method": method,
        "confidence": confidence,
        "point": point,
        "n": n,
    }
    if row is None:
        block["measured"] = None
        return block
    block["measured"] = f"{row.coverage:.{DISCLOSURE_DIGITS}f}"
    block["measured_where"] = row.where
    block["is_design_based"] = method.startswith("design_")
    if not block["is_design_based"]:
        block["gamma"] = f"{gamma_for(float(point), n):.3f}"
        block["gamma_in_swept_range"] = in_rare_event_regime(float(point), n)
        block["n_was_measured"] = n in MEASURED_N
    return block
