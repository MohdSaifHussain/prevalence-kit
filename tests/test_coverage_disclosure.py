"""O-25 and O-27 -- the two disclosures, and the checks that keep them honest.

**O-25 / D-37 condition 3.** The report states the coverage of the interval
actually used, at the nominal level actually used. The plan records the choice;
this records what the choice cost.

**O-27 / D-38.** A one-stratum stratified run says that it had one stratum, that
stratification therefore gained nothing, and that its interval rests on a
stratified variance basis rather than a binomial inversion.

**Why the numbers are recomputed here rather than trusted.** `coverage.py` holds
measured figures as data, and data transcribed from a commit message is a
remembered number wearing a constant's clothes. The binomial rows are checked
against the R fixture that produced them; the design rows are checked against a
fresh enumeration through the **shipped estimators**. Before this file existed,
the 96-point design measurement lived only in prose -- three docstrings and a
commit message, no script and no artifact -- and it is now in the ratified
charter, which is the strongest reason to be able to re-derive it.
"""

from __future__ import annotations

import itertools
import json
import math
import re
from pathlib import Path

import pytest

from prevalence_kit import coverage as cov
from prevalence_kit.errors import Refusal
from prevalence_kit.estimators import design_korn_graubard, design_wilson
from prevalence_kit.report import render_markdown
from prevalence_kit.stratified import stratified_estimate

ROOT = Path(__file__).resolve().parents[1]
BUILDERS = {"design_wilson": design_wilson, "design_korn_graubard": design_korn_graubard}


# --------------------------------------------------------------------------
# The binomial rows, against the fixture that produced them
# --------------------------------------------------------------------------


def _fixture_worst() -> dict[tuple[str, float], tuple[float, int]]:
    """Worst coverage per (method, confidence) across the measured sample sizes.

    Returns the raw value and the `n` it occurred at, so the test can check the
    conditions string as well as the number. A figure whose stated conditions are
    wrong is C-30's defect with the number left correct.
    """
    payload = json.loads((ROOT / "r" / "fixtures" / "coverage.json").read_text(encoding="utf-8"))
    worst: dict[tuple[str, float], tuple[float, int]] = {}
    for row in payload["rare_event_worst_coverage"]:
        for method in ("wilson", "clopper_pearson"):
            key = (method, float(row["conf"]))
            value = float(row[method]["coverage"])
            if key not in worst or value < worst[key][0]:
                worst[key] = (value, int(row["n"]))
    return worst


def _floor(value: float) -> float:
    scale = 10**cov.DISCLOSURE_DIGITS
    return float(math.floor(value * scale) / scale)


def test_the_binomial_figures_are_the_fixture_rounded_down() -> None:
    """Every binomial row equals the R measurement, floored, at the stated `n`."""
    worst = _fixture_worst()
    for row in cov.BINOMIAL:
        raw, at_n = worst[(row.method, row.confidence)]
        assert row.coverage == _floor(raw), f"{row.method} at {row.confidence}"
        assert f"n = {at_n}" in row.where, f"{row.method} at {row.confidence} names the wrong n"


def test_rounding_to_nearest_would_change_a_published_figure() -> None:
    """The negative control for the sentence *rounded down, not to nearest*.

    **C-32 was exactly this**, in the charter, and it was the director's. A claim
    that figures are rounded down is worth nothing if rounding to nearest would
    have produced the same table -- the discipline would be untested. It would
    not: `clopper_pearson` at 0.95 measures 0.952073, which is 0.9520 floored and
    0.9521 to nearest, and 0.9521 asserts a floor the measurement breaks.
    """
    worst = _fixture_worst()
    differ = [
        row
        for row in cov.BINOMIAL
        if _floor(worst[(row.method, row.confidence)][0])
        != round(worst[(row.method, row.confidence)][0], cov.DISCLOSURE_DIGITS)
    ]
    assert differ, "no figure distinguishes flooring from rounding, so the claim is untested"


def test_clopper_pearson_holds_its_level_and_wilson_does_not() -> None:
    """The trade D-37 refused to make for the operator, as an assertion.

    S-1.1 section 4.2.1: Clopper-Pearson's coverage is at or above nominal by
    construction. This is the defining property, not a region description -- rule
    11 -- so it is a fair thing to assert.
    """
    for row in cov.BINOMIAL:
        if row.method == "clopper_pearson":
            assert row.coverage >= row.confidence, f"CP fell below nominal at {row.confidence}"
        else:
            assert row.coverage < row.confidence, f"Wilson held nominal at {row.confidence}"


# --------------------------------------------------------------------------
# The design rows, against a fresh enumeration through the shipped estimators
# --------------------------------------------------------------------------


def _designs() -> dict[str, dict[str, tuple[int, int]]]:
    """`{label: {stratum: (N_h, n_h)}}`, read from the committed `svy` fixture.

    **Read rather than restated**, so the coverage measurement and the interval
    fixtures cannot come to describe different designs. The fixture carries
    `[N_h, n_h, k_h]`; the observed count is a property of that fixture's case
    and has nothing to do with a coverage sweep, so it is dropped here.
    """
    payload = json.loads(
        (ROOT / "svy" / "fixtures" / "design_intervals.json").read_text(encoding="utf-8")
    )
    return {
        case["label"]: {name: (spec[0], spec[1]) for name, spec in case["strata"].items()}
        for case in payload["cases"]
    }


def _binomial_pmf(n: int, p: float) -> list[float]:
    return [math.comb(n, k) * p**k * (1.0 - p) ** (n - k) for k in range(n + 1)]


RETAINED_MASS = 1.0 - 1e-12
"""The charter's own criterion, applied where the charter states it: the product.

**Truncating per stratum instead was the first draft, and it was both slower and
looser about the claim.** A per-stratum budget has to be divided out of the
sentence to check it, and it keeps thousands of joint outcomes whose combined
mass is far below the threshold. Taking the product's outcomes in descending
mass order and stopping at 1 - 1e-12 keeps 1576 of 5415 outcomes on the `rare`
design at p = 0.01, retains 0.999999999999, reproduces the published figure to
eight decimal places, and runs in 40% of the time.
"""


def _enumerate(spec: dict[str, tuple[int, int]], rate: float) -> list[tuple[float, object]]:
    """The outcomes carrying the charter's retained mass, with their estimates.

    Built **once per (design, rate)** and shared across both methods and all
    three confidence levels. Rebuilding it per figure made this file the slowest
    thing in the suite for no extra assurance, which is the fixture mistake
    `CLAUDE.md` records at 150s-to-53s.
    """
    names = sorted(spec)
    total = sum(spec[name][0] for name in names)
    weights = tuple(spec[name][0] / total for name in names)
    sizes = tuple(spec[name][1] for name in names)
    pmfs = [_binomial_pmf(n, rate) for n in sizes]

    # A generous per-stratum window first, so the product contains everything the
    # mass ordering could want; the ordering below is what actually decides.
    ranges = []
    for pmf in pmfs:
        order = sorted(range(len(pmf)), key=lambda i: -pmf[i])
        kept, mass = [], 0.0
        for index in order:
            kept.append(index)
            mass += pmf[index]
            if mass >= 1.0 - 1e-15:
                break
        ranges.append(sorted(kept))

    joint = []
    for combo in itertools.product(*ranges):
        mass = 1.0
        for pmf, k in zip(pmfs, combo, strict=True):
            mass *= pmf[k]
        joint.append((mass, combo))
    joint.sort(key=lambda row: -row[0])

    outcomes: list[tuple[float, object]] = []
    retained = 0.0
    for mass, combo in joint:
        outcomes.append((mass, stratified_estimate(weights, tuple(combo), sizes)))
        retained += mass
        if retained >= RETAINED_MASS:
            break
    return outcomes


@pytest.fixture(scope="module")
def enumerations() -> dict[tuple[str, float], list[tuple[float, object]]]:
    """The outcome spaces the design figures are measured on, built once."""
    designs = _designs()
    needed = {(row.where.split("`")[1], float(row.where.rsplit(" ", 1)[1])) for row in cov.DESIGN}
    return {key: _enumerate(designs[key[0]], key[1]) for key in needed}


def _conditional_coverage(
    outcomes: list[tuple[float, object]], rate: float, method: str, confidence: float
) -> float:
    """Coverage **conditional on the interval existing**, as the charter states it.

    An outcome with no spread produces no interval; that is a different failure
    and is disclosed separately, by `sample`, before any labelling is paid for.
    Folding the two together would report one number for two things.
    """
    builder = BUILDERS[method]
    covered = exists = 0.0
    for mass, estimate in outcomes:
        try:
            interval = builder(
                estimate.point,  # type: ignore[attr-defined]
                estimate.standard_error,  # type: ignore[attr-defined]
                estimate.degrees_of_freedom,  # type: ignore[attr-defined]
                estimate.n,  # type: ignore[attr-defined]
                confidence=confidence,
            )
        except Refusal:
            continue
        exists += mass
        if float(interval.low) <= rate <= float(interval.high):
            covered += mass
    return covered / exists


def test_the_design_figures_are_reproduced_by_enumeration(
    enumerations: dict[tuple[str, float], list[tuple[float, object]]],
) -> None:
    """Every design row recomputed from the shipped estimators, floored.

    **This is what the 96-point measurement never had.** Its figures reached
    three docstrings, a commit message and the ratified charter, and no artifact
    or script could produce them again.

    **What it does not check, said rather than implied.** It reproduces each
    figure *at its stated conditions*. It does **not** prove that figure is the
    minimum over the whole grid -- that would need the grid, and the claim of
    minimality belongs to the sweep, not to this test. C-34's lesson: state the
    scope you have.
    """
    for row in cov.DESIGN:
        design = row.where.split("`")[1]
        rate = float(row.where.rsplit(" ", 1)[1])
        got = _conditional_coverage(enumerations[(design, rate)], rate, row.method, row.confidence)
        assert row.coverage == _floor(got), (
            f"{row.method} at {row.confidence} on {design} p={rate}: "
            f"module says {row.coverage}, enumeration says {got:.6f}"
        )


def test_neither_design_interval_holds_its_nominal_level() -> None:
    """The charter's claim, as an assertion rather than a sentence.

    **A-6 turns on this.** `design_clopper_pearson` was renamed because the name
    promised coverage at or above nominal and the measurement refused it. If a
    later change ever made either interval hold its level, this test fails and
    forces the charter to be rewritten rather than quietly outliving its truth --
    which is the charter's own rule for limits.
    """
    for row in cov.DESIGN:
        assert row.coverage < row.confidence, f"{row.method} now holds {row.confidence}"


def test_the_charter_carries_the_same_design_figures() -> None:
    """Charter section 8's table against the module. Rule 14, on A-6's numbers.

    Markdown gets read the way its consumer reads it -- rule 12's stated
    exception -- so this is a regex over the table rather than a parser.
    """
    text = (ROOT / "PROJECT_CHARTER.md").read_text(encoding="utf-8")
    for row in cov.DESIGN:
        column = 1 if row.method == "design_wilson" else 2
        pattern = re.compile(
            rf"^\s*\|\s*{row.confidence:.2f}\s*\|(.+?)\|(.+?)\|\s*$",
            re.M,
        )
        match = pattern.search(text)
        assert match is not None, f"charter section 8 has no row for nominal {row.confidence}"
        cell = match.group(column)
        assert f"{row.coverage:.4f}" in cell, (
            f"charter says {cell.strip()!r} for {row.method} at {row.confidence}, "
            f"module says {row.coverage:.4f}"
        )


# --------------------------------------------------------------------------
# What reaches the report
# --------------------------------------------------------------------------


def _report(**over: object) -> dict[str, object]:
    """A minimal report body. Only the fields the two disclosures read matter."""
    body: dict[str, object] = {
        "estimand": {
            "description": "d",
            "label_field": "toxicity",
            "positive_when": "at_least",
            "threshold": "0.5",
        },
        "population": "frame.txt",
        "population_declared": "frame.txt",
        "design": "srs",
        "seed": "s",
        "strata": None,
        "probability_no_interval": None,
        "estimate": {
            "method": "wilson",
            "point": "0.225000000000",
            "low": "0.123160913235",
            "high": "0.375030967423",
            "confidence": "0.950000000000",
            "n": 40,
            "positives": 9,
        },
        "coverage": cov.disclosure("wilson", "0.950000000000", "0.225000000000", 40),
        "chain": [{"seq": 0, "step": "plan", "at": "t", "entry_digest": "d" * 64}],
        "plan_hash": "h" * 64,
        "entries_verify_will_report": 2,
        "honest_limits": ["a limit"],
        "emitted_at": "2026-08-30T00:00:00Z",
        "tool": "prevalence-kit",
    }
    body.update(over)
    return body


def _estimate_of(body: dict[str, object]) -> dict[str, object]:
    """The estimate block, as a mutable copy. `_report`'s values are `object`."""
    estimate = body["estimate"]
    assert isinstance(estimate, dict)
    return dict(estimate)


def test_the_report_states_what_the_chosen_level_delivers() -> None:
    """O-25. The measured figure, its conditions, and the method it belongs to."""
    text = render_markdown(_report())  # type: ignore[arg-type]
    assert "## What that 95% actually delivers" in text
    assert "90.98%" in text
    assert "`wilson`" in text
    assert "gamma in [0.5, 15] step 0.25" in text


def test_the_report_says_no_coverage_was_computed_for_this_run() -> None:
    """The sentence that stops a bound being read as a measurement.

    The figure quoted is a worst case over a grid that this run is not on. Saying
    so is the difference between a disclosure and a number that flatters itself.
    """
    text = render_markdown(_report())  # type: ignore[arg-type]
    assert "not a coverage computed for this run, and none was computed" in text


def test_the_coverage_figure_follows_the_method_the_plan_named() -> None:
    """The control: change the method, and the quoted figure changes with it.

    Without this, the block could print one constant for every run and every
    assertion above would still pass -- **F-10's shape**, in a disclosure.
    """
    estimate = _estimate_of(_report())
    estimate["method"] = "clopper-pearson"
    text = render_markdown(
        _report(  # type: ignore[arg-type]
            estimate=estimate,
            coverage=cov.disclosure("clopper_pearson", "0.950000000000", "0.225000000000", 40),
        )
    )
    assert "95.20%" in text
    assert "90.98%" not in text


def test_the_report_names_the_level_the_estimator_recorded() -> None:
    """The header level is read from the record, not written as a constant.

    It said `95%` as a literal until O-25. Nothing reached it, because the CLI
    takes the estimator default -- which is what made it worth fixing rather than
    leaving: a recorded field the artifact does not read is F-10's shape, and the
    day a plan carries `confidence` this line would have printed the wrong level
    beside the right bounds.
    """
    estimate = _estimate_of(_report())
    estimate["confidence"] = "0.990000000000"
    text = render_markdown(
        _report(  # type: ignore[arg-type]
            estimate=estimate,
            coverage=cov.disclosure("wilson", "0.990000000000", "0.225000000000", 40),
        )
    )
    assert "(99% interval" in text
    assert "(95% interval" not in text


def test_a_one_stratum_run_discloses_that_it_gained_nothing() -> None:
    """O-27 / D-38, all three statements the ruling names."""
    text = render_markdown(_report(design="stratified", strata=1))  # type: ignore[arg-type]
    assert "one stratum" in text
    assert "gained you nothing" in text
    assert "not on a binomial inversion" in text


def test_a_multi_stratum_run_carries_no_such_disclosure() -> None:
    """The control. A disclosure that appears on every run discloses nothing."""
    text = render_markdown(_report(design="stratified", strata=3))  # type: ignore[arg-type]
    assert "gained you nothing" not in text


def test_an_srs_run_carries_no_stratum_disclosure() -> None:
    """The second control: `strata` is absent on an SRS run, not equal to one."""
    text = render_markdown(_report())  # type: ignore[arg-type]
    assert "gained you nothing" not in text
