"""D2.5 -- the Rogan-Gladen correction, against epiR 2.0.92.

Eleven cases, generated and committed in `ad73030` before this code existed.
R2.2.

**What the witness establishes, and what it does not.** `epiR` implements
Rogan-Gladen and its intervals follow Reiczigel et al. (2010) -- S-1.6, the paper
matching our assumption that Se and Sp are supplied and exact (D-31). But Jeno
Reiczigel is a listed contributor to `epiR`, so this is the method author's own
implementation of the method author's own paper. It confirms we implement the
method as its author does. **It does not independently confirm the method.**
Barnett Table 2B is a published table computed without reference to any
implementation; this is not that.
"""

from __future__ import annotations

import inspect
import json
import math
from pathlib import Path
from typing import Any

import pytest

from prevalence_kit.errors import Reason, Refusal
from prevalence_kit.estimators import rogan_gladen, rogan_gladen_interval

FIXTURE = Path(__file__).resolve().parents[1] / "r" / "fixtures" / "rogan_gladen.json"
CASES: list[dict[str, Any]] = list(json.loads(FIXTURE.read_text(encoding="utf-8"))["cases"])

ACCEPTED = [c for c in CASES if c["prevalence_kit"] == "accept"]
REFUSED = [c for c in CASES if c["prevalence_kit"] != "accept"]


def label(case: dict[str, Any]) -> str:
    return str(case["label"])


# ------------------------------------------------------------- the accept side


@pytest.mark.parametrize("case", ACCEPTED, ids=[label(c) for c in ACCEPTED])
def test_the_corrected_estimate_matches_epir(case: dict[str, Any]) -> None:
    """R2.3. Against a number the witness produced first."""
    got = rogan_gladen(case["apparent"], case["se"], case["sp"])
    assert float(got.corrected) == pytest.approx(case["tp_est"], rel=1e-9), case["note"]
    assert float(got.apparent) == pytest.approx(case["apparent"], rel=1e-12)


def test_a_perfect_test_leaves_the_estimate_alone() -> None:
    """Se = Sp = 1 makes the correction the identity. If it does not, the
    formula is wrong in a way no fixture comparison would necessarily show."""
    got = rogan_gladen(0.002, 1.0, 1.0)
    assert float(got.corrected) == pytest.approx(0.002, rel=1e-12)


def test_zero_positives_with_perfect_specificity_is_accepted() -> None:
    """The case the struck CORRECTION_DEGENERATE row would have refused.

    A rare-event measurement that finds no violations and can still report a
    bound is this tool's product, not an absence of information. The contract
    said otherwise and the contract was wrong.
    """
    got = rogan_gladen(0.0, 0.90, 1.0)
    assert float(got.corrected) == 0.0


# ------------------------------------------------------------ the refuse side


@pytest.mark.parametrize("case", REFUSED, ids=[label(c) for c in REFUSED])
def test_every_refusing_case_refuses_with_the_declared_code(case: dict[str, Any]) -> None:
    """The fixture declares which code each case must raise. This is that check.

    The fixture records what `epiR` did as well: it warns and returns the
    invalid number. We refuse. Both are deliberate and the difference is the
    point -- `epiR` is a research tool, and this one refuses to print a number it
    cannot defend.
    """
    expected = Reason[case["prevalence_kit"].removeprefix("refuse ")]

    with pytest.raises(Refusal) as caught:
        rogan_gladen(case["apparent"], case["se"], case["sp"])

    assert caught.value.reason is expected, case["note"]


def test_the_undefined_refusal_says_there_is_nothing_to_print() -> None:
    """Not "we chose not to print it". The witness proves the stronger claim.

    At Se = 0.60, Sp = 0.30 `epi.prev` returns a point estimate with a lower
    bound of 6.712724 ABOVE an upper bound of 6.459273. An interval whose lower
    bound exceeds its upper bound is not an interval, so refusing is arithmetic
    rather than policy, and an auditor reading the message should find that.
    """
    inverted = next(c for c in CASES if c.get("tp_interval_inverted"))
    assert inverted["tp_lower"] > inverted["tp_upper"]

    with pytest.raises(Refusal) as caught:
        rogan_gladen(inverted["apparent"], inverted["se"], inverted["sp"])

    assert caught.value.reason is Reason.CORRECTION_UNDEFINED
    assert "none that exists" in caught.value.detail
    # And the fix names the most likely real cause rather than restating the rule.
    assert "the other way" in caught.value.fix


def test_the_out_of_range_fix_names_the_number_that_has_to_change() -> None:
    """R8 at full strength, and the reason `fpr_exceeds_prevalence` has a name.

    The correction is defined only when `Sp >= 1 - AP`. At an apparent
    prevalence of 0.2% that means a specificity above 99.8%. A team reading
    "99% specificity" hears excellent; at rare-event rates it makes the
    correction undefined, not merely imprecise, and nobody who has not done this
    arithmetic expects it.

    So the message gives the threshold and the shortfall, not just the failure.
    """
    with pytest.raises(Refusal) as caught:
        rogan_gladen(0.002, 0.90, 0.99)

    fix = caught.value.fix
    assert "99.8000%" in fix, fix  # the specificity actually required
    assert "99.0000%" in fix, fix  # the one supplied
    assert "0.2000%" in fix, fix  # the apparent prevalence it follows from
    assert "uncorrected" in fix  # and the honest fallback

    detail = caught.value.detail
    assert "below zero" in detail
    assert "cannot both be right" in detail


def test_the_upper_refusal_names_sensitivity_rather_than_specificity() -> None:
    """The mirror case sends the operator to the other number. Without this, one
    message could serve both and neither would say which figure to look at."""
    with pytest.raises(Refusal) as caught:
        rogan_gladen(1.0, 0.90, 0.99)

    assert caught.value.reason is Reason.CORRECTION_OUT_OF_RANGE
    assert "above one" in caught.value.detail
    assert "sensitivity" in caught.value.fix
    assert "specificity" not in caught.value.fix


# ------------------------------------------------------- inputs, and the record


@pytest.mark.parametrize(
    ("apparent", "se", "sp"),
    [(-0.1, 0.9, 0.9), (1.1, 0.9, 0.9)],
)
def test_an_impossible_apparent_prevalence_is_refused(
    apparent: float, se: float, sp: float
) -> None:
    with pytest.raises(Refusal) as caught:
        rogan_gladen(apparent, se, sp)
    assert caught.value.reason is Reason.LABELS_UNMATCHED


@pytest.mark.parametrize(("se", "sp"), [(1.5, 0.9), (0.9, -0.2)])
def test_a_non_proportion_se_or_sp_is_refused_at_the_plan(se: float, sp: float) -> None:
    with pytest.raises(Refusal) as caught:
        rogan_gladen(0.1, se, sp)
    assert caught.value.reason is Reason.PLAN_INVALID


def test_the_record_carries_the_inputs_the_correction_used() -> None:
    """An outsider must be able to redo the arithmetic from the record alone.

    Se and Sp are what turn an apparent prevalence into a corrected one, so a
    record holding only the answer would not be reproducible.
    """
    record = rogan_gladen(0.30, 0.96, 0.89).as_record()
    assert record["method"] == "rogan-gladen"

    apparent = float(str(record["apparent"]))
    corrected = float(str(record["corrected"]))
    se = float(str(record["sensitivity"]))
    sp = float(str(record["specificity"]))
    assert corrected == pytest.approx((apparent + sp - 1) / (se + sp - 1), rel=1e-9)


def test_the_fixture_still_covers_both_refusals_and_the_accepting_case() -> None:
    """Both controls. A suite of refusals alone would pass an estimator that
    refuses everything, which is what doctrine rule 5 exists to stop."""
    assert len(ACCEPTED) >= 3
    assert {c["prevalence_kit"] for c in REFUSED} == {
        "refuse CORRECTION_UNDEFINED",
        "refuse CORRECTION_OUT_OF_RANGE",
    }
    assert not math.isnan(float(rogan_gladen(0.30, 0.96, 0.89).corrected))


# ===================================================================== D2.6
#
# The Rogan-Gladen interval. Every expected value below that describes the
# ESTIMATOR comes from `r/fixtures/rogan_gladen.json`, generated by epiR 2.0.92
# on 2026-08-29, committed before this code existed. R2.2.
#
# The expected values that describe the CLAMP do not, and the difference is
# stated rather than blurred: the witness does not clamp. Clamping is our ruled
# policy (Q6 / D-32), so its tests assert the ruling, and its arithmetic is our
# own. Saying otherwise would dress a policy up as a witnessed fact.


CONFIDENCE: float = float(json.loads(FIXTURE.read_text(encoding="utf-8"))["confidence"])


def _accept_cases() -> list[dict[str, Any]]:
    return [c for c in CASES if c["prevalence_kit"].startswith("accept")]


def test_the_corrected_interval_reproduces_every_accepted_epir_case() -> None:
    """D2.6 against its witness, on the five cases epiR and we both accept.

    Worst disagreement: **7.3e-13** on either end, across 15 accepted cases --
    pos, tested, se and sp varied, AND confidence in {0.90, 0.95, 0.99}. Stated
    with its axes, because the figure used to be measured at 0.95 only and the
    sentence quoting it did not say so.

    The bounds compared are `low_raw` / `high_raw`, deliberately. Those are what
    the arithmetic produced, and they are what epiR reports; `low` / `high` carry
    our clamp, which epiR does not apply. Comparing the clamped bound against the
    witness would silently pass on `rare_event` for the wrong reason -- the two
    would differ and the test would be measuring the policy, not the estimator.
    """
    worst = 0.0
    for case in _accept_cases():
        got = rogan_gladen_interval(
            case["pos"],
            case["tested"],
            case["se"],
            case["sp"],
            interval_method="clopper_pearson",
            confidence=case["conf"],
        )
        for ours, theirs in (
            (got.low_raw, case["tp_lower"]),
            (got.high_raw, case["tp_upper"]),
        ):
            worst = max(worst, abs(float(ours) - theirs))

    assert worst < 1e-9, f"worst disagreement with epiR is {worst:.3e}"


def test_the_corrected_interval_is_the_transformed_apparent_interval() -> None:
    """The witness's construction, asserted on the witness's own numbers.

    `RG(ap_lower) == tp_lower` and `RG(ap_upper) == tp_upper` on every fixture row
    with a positive denominator -- including the six we refuse, because the
    fixture records what epiR did there too and the relationship holds regardless
    of what we do with it.

    This is what makes D2.6 a composition of two already-witnessed pieces rather
    than a third unwitnessed one. It is an observation about `epi.prev`, not a
    theorem about corrected intervals.
    """
    for case in CASES:
        denominator = case["se"] + case["sp"] - 1
        if denominator <= 0:
            continue
        for apparent, corrected in (
            (case["ap_lower"], case["tp_lower"]),
            (case["ap_upper"], case["tp_upper"]),
        ):
            transformed = (apparent + case["sp"] - 1) / denominator
            assert abs(transformed - corrected) < 1e-9, case["label"]


def test_every_refused_case_refuses_with_the_interval_too() -> None:
    """The six refusals survive asking for an interval, with the same code.

    The point estimate owns both correction refusals. If the interval path had
    its own copy of the conditions, the two could disagree and an operator could
    get an interval around a number the tool refuses to print.
    """
    for case in CASES:
        if case["prevalence_kit"].startswith("accept"):
            continue
        expected = case["prevalence_kit"].split()[-1]
        with pytest.raises(Refusal) as caught:
            rogan_gladen_interval(
                case["pos"],
                case["tested"],
                case["se"],
                case["sp"],
                interval_method="clopper_pearson",
            )
        assert caught.value.reason.name == expected, case["label"]


def test_the_transform_is_monotone_so_the_ends_keep_their_order() -> None:
    """Why the endpoints may simply be transformed, asserted rather than assumed.

    With `Se + Sp > 1` the denominator is positive, so the correction is strictly
    increasing and carries an interval to an interval with its ends in order. The
    case where that fails -- `Se + Sp <= 1`, where the witness itself returns a
    lower bound of 6.712724 ABOVE an upper bound of 6.459273 -- never reaches this
    function, because the point estimate refuses first.

    Checked across the fixture and a grid, because "the denominator is positive"
    is the kind of claim that is true right up until a boundary case.
    """
    for case in _accept_cases():
        got = rogan_gladen_interval(
            case["pos"],
            case["tested"],
            case["se"],
            case["sp"],
            interval_method="clopper_pearson",
        )
        assert float(got.low_raw) <= float(got.high_raw), case["label"]
        assert float(got.low) <= float(got.high), case["label"]

    for se in (0.60, 0.75, 0.90, 1.00):
        for sp in (0.55, 0.80, 0.99, 1.00):
            if se + sp <= 1:
                continue
            for positives in (0, 1, 25, 99, 100):
                try:
                    got = rogan_gladen_interval(
                        positives, 100, se, sp, interval_method="clopper_pearson"
                    )
                except Refusal:
                    continue
                assert float(got.low_raw) <= float(got.high_raw), (se, sp, positives)


# ------------------------------------------------------------- Q6 / D-32


def test_a_negative_lower_bound_is_clamped_and_said_out_loud() -> None:
    """Q6 / D-32, on the case that raised the question.

    `rare_event` -- pos 8, n 4000, Se 0.90, Sp 0.999 -- has a point estimate of
    0.001112, comfortably inside [0, 1], so the estimator ACCEPTS it. The witness
    returns a lower bound of -0.000151 and prints it with no warning.

    Refusing would refuse the tool's own use case. Printing a negative prevalence
    would cost an auditor's trust in every number beside it. So: clamp, disclose,
    and keep the raw bound.

    **The disclosure is the half that makes clamping honest**, and it is asserted
    here rather than left to the renderer. A silently clamped bound is a small lie
    in the artifact an outsider reads.
    """
    got = rogan_gladen_interval(8, 4000, 0.90, 0.999, interval_method="clopper_pearson")

    assert got.clamped == ("low",)
    assert got.low == "0.000000000000"
    assert float(got.low_raw) < 0
    assert got.high == got.high_raw, "the upper end was fine and must not be touched"

    assert "clamped to 0" in got.note
    assert got.low_raw in got.note, "the note must carry the raw number, not just the fact"
    assert "construction, not a measurement" in got.note

    record = got.as_record()
    assert record["low"] == got.low and record["low_raw"] == got.low_raw
    assert record["clamped"] == ["low"]


def test_an_upper_bound_above_one_is_clamped_the_same_way() -> None:
    """The symmetric case. D-32 condition 1: both ends, or the pair drifts apart.

    No fixture case reaches it -- every epiR row whose upper bound exceeds 1 also
    has a point estimate outside [0, 1], so it refuses first. This one is
    constructed: pos 95, n 100, Se 0.96, Sp 0.99 puts the point estimate at
    0.9895 and the raw upper bound at 1.0248.

    **Its expected values are our arithmetic, not the witness's**, and that is
    stated because the witness does not clamp at all. What is being asserted here
    is the RULING, which is ours to make; the estimator underneath it is the one
    checked against epiR above.
    """
    got = rogan_gladen_interval(95, 100, 0.96, 0.99, interval_method="clopper_pearson")

    assert got.clamped == ("high",)
    assert got.high == "1.000000000000"
    assert float(got.high_raw) > 1
    assert got.low == got.low_raw
    assert "clamped to 1" in got.note


def test_an_interval_needing_no_clamp_says_nothing() -> None:
    """The positive control. A disclosure that appears on every estimate is noise.

    If `note` were non-empty here, an operator would learn to skip it, and the one
    case that matters would be skipped with the rest.
    """
    got = rogan_gladen_interval(45, 150, 0.96, 0.89, interval_method="clopper_pearson")

    assert got.clamped == ()
    assert got.note == ""
    assert got.low == got.low_raw and got.high == got.high_raw
    assert got.as_record()["clamped"] == []


def test_the_clamp_only_ever_narrows_the_interval() -> None:
    """The property that makes clamping safe, rather than merely tidy.

    A true prevalence cannot lie outside [0, 1], so replacing a bound that does
    with the edge cannot remove any admissible value. Coverage is preserved and
    the interval becomes very slightly conservative -- the same direction this
    project chose when it picked Clopper-Pearson as the conservative option.
    """
    for se, sp, positives, n in ((0.90, 0.999, 8, 4000), (0.96, 0.99, 95, 100)):
        got = rogan_gladen_interval(positives, n, se, sp, interval_method="clopper_pearson")
        assert float(got.low) >= float(got.low_raw)
        assert float(got.high) <= float(got.high_raw)
        assert 0.0 <= float(got.low) <= float(got.high) <= 1.0


# ------------------------------------------------------------- Q7 / D-33


def test_wilson_with_a_correction_is_refused_by_name() -> None:
    """Q7 / D-33. The negative control.

    A Wilson-transformed corrected interval has no pre-existing expected value,
    so R2.2 forbids shipping one. The refusal exists because the alternative --
    quietly returning a Clopper-Pearson-based interval -- would substitute a
    method inside a pre-registered measurement, which is V-1's and V-7's class.

    R8: the fix text names both remedies, and both are edits to the plan.
    """
    with pytest.raises(Refusal) as caught:
        rogan_gladen_interval(45, 150, 0.96, 0.89, interval_method="wilson")

    assert caught.value.reason is Reason.CORRECTION_INTERVAL_UNSUPPORTED
    assert "clopper_pearson" in caught.value.fix
    assert "remove sensitivity and specificity" in caught.value.fix
    assert "did not commit to" in caught.value.detail


def test_clopper_pearson_with_a_correction_is_accepted() -> None:
    """The positive control. A gate that refuses everything proves nothing."""
    got = rogan_gladen_interval(45, 150, 0.96, 0.89, interval_method="clopper_pearson")
    assert got.method == "rogan-gladen/clopper-pearson"
    assert float(got.low) < float(got.point) < float(got.high)


def test_an_unknown_interval_is_a_different_refusal_from_an_unsupported_one() -> None:
    """D-22: count the artifacts the operator opens.

    A typo and a real-but-uncorrectable method send the operator to different
    places -- one to fix a misspelling, one to make a decision about their
    measurement. An operator who asked for Wilson has not made a typo, and a
    refusal telling them they have would be worse than useless.
    """
    with pytest.raises(Refusal) as caught:
        rogan_gladen_interval(45, 150, 0.96, 0.89, interval_method="wilsonn")
    assert caught.value.reason is Reason.PLAN_INVALID


def test_the_interval_method_cannot_be_defaulted() -> None:
    """D-30 condition 1's shape, applied to a second commitment.

    `interval_method` is keyword-only with no default, so the choice cannot become
    a constant in the source. If a default is ever added, the silent substitution
    Q7 exists to prevent is back, and this test is what says so.
    """
    signature = inspect.signature(rogan_gladen_interval)
    parameter = signature.parameters["interval_method"]

    assert parameter.default is inspect.Parameter.empty
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
