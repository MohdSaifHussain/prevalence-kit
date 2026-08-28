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

import json
import math
from pathlib import Path
from typing import Any

import pytest

from prevalence_kit.errors import Reason, Refusal
from prevalence_kit.estimators import rogan_gladen

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
