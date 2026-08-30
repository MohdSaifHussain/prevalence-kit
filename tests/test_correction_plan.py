"""O-29 -- sensitivity and specificity reach the plan, so the correction is reachable.

**Rogan-Gladen was built, validated to 7.3e-13 against `epiR` 2.0.92, and
unreachable.** There was no `sensitivity` or `specificity` field in the schema and
`rogan_gladen` was referenced only in `estimators.py`, so the correction charter
section 4 promises -- *Optional Rogan-Gladen correction when sensitivity and
specificity are supplied* -- could not be invoked by any plan.

**Found by the director checking the open table at the review stop**, and it is
the same class as F-10 and F-11: O-20 covered `allocation_rounding`, O-22 covered
`interval`, and no obligation named these two.

Every test here asks the standing question of the new fields: **what reads this,
and what happens if it changes?**
"""

from __future__ import annotations

from typing import Any

import pytest

from prevalence_kit.errors import Reason, Refusal
from prevalence_kit.plan import FIELD_KIND, Plan
from prevalence_kit.run import _estimate_from

BASE: dict[str, Any] = {
    "estimand": {
        "description": "Comments scored toxic by at least half of annotators",
        "label_field": "toxicity",
        "positive_when": "at_least",
        "threshold": "0.5",
    },
    "population": "frame.txt",
    "design": "srs",
    "sample_size": 4000,
    "labels": "labels.csv",
    "seed": "fixture-seed",
    "interval": "clopper_pearson",
}

# The `rare_event` case from `r/fixtures/rogan_gladen.json`: 8 positives in 4000
# at Se 0.90, Sp 0.999. Its raw lower bound is negative, which is Q6's whole
# subject, so this exercises the clamp as well as the correction.
LABELS = {f"item-{k:04d}": ("0.9" if k < 8 else "0.1") for k in range(4000)}


def corrected(**over: Any) -> Any:
    body = dict(BASE) | {"sensitivity": "0.90", "specificity": "0.999"} | over
    return _estimate_from(Plan.from_mapping(body), LABELS)


# ------------------------------------------------------- the fields are read


def test_supplying_se_and_sp_changes_the_number() -> None:
    """The behavioural assertion, and F-10's lesson is why it comes first.

    A field that reaches the hash and changes no number is inert. `interval` was
    exactly that for four commits, and the only test checked the half that worked.
    """
    uncorrected = _estimate_from(Plan.from_mapping(BASE), LABELS)
    with_correction = corrected()

    assert uncorrected.point == "0.002000000000"
    assert with_correction.point == "0.001112347052"
    assert uncorrected.point != with_correction.point
    assert with_correction.method == "rogan-gladen/clopper-pearson"


def test_changing_specificity_changes_the_number() -> None:
    """Not merely present-versus-absent: the VALUE has to matter too.

    A dispatch that switched on presence and ignored the numbers would pass the
    test above and still be wrong.
    """
    assert corrected(specificity="0.999").point != corrected(specificity="0.9995").point


def test_the_wired_path_reproduces_the_epir_witness() -> None:
    """The correction reaching a plan must be the correction D2.6 validated.

    `epiR` 2.0.92 gives this case `[-0.0001514559, 0.0032669342]`. Wiring it to the
    plan introduced no third thing: the raw bounds still match the witness to every
    printed digit, and Q6's clamp is applied on top rather than instead.
    """
    got = corrected()
    assert got.low_raw == "-0.000151455949"
    assert got.high_raw == "0.003266934245"
    assert got.low == "0.000000000000"
    assert got.clamped == ("low",)


def test_the_raw_bounds_reach_the_record() -> None:
    """D-32 condition 3, which until now had nothing to write to.

    O-23 named this: `note` and the raw bounds existed on the estimate, but no
    Phase 2 estimator was wired into `run.py`, so nothing wrote them anywhere.
    They reach `estimate.json` now because the correction is reachable.
    """
    record = corrected().as_record()
    assert record["low_raw"] == "-0.000151455949"
    assert record["high_raw"] == "0.003266934245"
    assert record["clamped"] == ["low"]
    # The disclosure is derived from those fields rather than stored beside them,
    # so it cannot drift from the arithmetic it describes.
    assert "clamped to 0 from -0.000151455949" in corrected().note


def test_se_and_sp_reach_the_hashed_plan() -> None:
    """Changing a commitment changes the plan's identity. That is what it is for."""
    plain = Plan.from_mapping(BASE)
    with_pair = Plan.from_mapping(BASE | {"sensitivity": "0.90", "specificity": "0.999"})
    moved = Plan.from_mapping(BASE | {"sensitivity": "0.91", "specificity": "0.999"})

    assert plain.as_record()["sensitivity"] is None
    assert with_pair.as_record()["sensitivity"] == "0.90"
    assert plain.plan_hash != with_pair.plan_hash
    assert with_pair.plan_hash != moved.plan_hash


def test_they_are_decimal_strings_not_floats() -> None:
    """`Estimand.threshold`'s precedent, enforced by `canonical()`.

    Floats do not round-trip identically across platforms and these are in the
    pre-registration hash. Correcting for a different Se than the one registered
    would be a different measurement.
    """
    plan = Plan.from_mapping(BASE | {"sensitivity": "0.90", "specificity": "0.999"})
    assert isinstance(plan.sensitivity, str)
    assert plan.plan_hash  # canonical() would refuse a float here


# ------------------------------------------------------------------ refusals


@pytest.mark.parametrize("supplied", ["sensitivity", "specificity"])
def test_one_without_the_other_is_refused_at_load(supplied: str) -> None:
    """A plan asking for a correction it cannot have is refused before the label
    budget is spent -- Q2's reason."""
    with pytest.raises(Refusal) as caught:
        Plan.from_mapping(BASE | {supplied: "0.90"})
    assert caught.value.reason is Reason.PLAN_INVALID
    assert "needs both" in caught.value.detail


@pytest.mark.parametrize("bad", ["1.5", "-0.1", "high", "", "none"])
def test_a_rate_outside_zero_to_one_is_refused(bad: str) -> None:
    with pytest.raises(Refusal) as caught:
        Plan.from_mapping(BASE | {"sensitivity": bad, "specificity": "0.99"})
    assert caught.value.reason is Reason.PLAN_INVALID


def test_a_valid_pair_is_accepted() -> None:
    """The positive control. A gate that refuses everything proves nothing."""
    plan = Plan.from_mapping(BASE | {"sensitivity": "0.90", "specificity": "0.999"})
    assert (plan.sensitivity, plan.specificity) == ("0.90", "0.999")


def test_wilson_with_se_and_sp_is_refused_at_plan_load() -> None:
    """**Q7 / D-33, and this is exit check F8d -- performable for the first time.**

    F8d could not be run before: the plan it describes, `interval: wilson` that
    also supplies Se/Sp, could not be written, because the schema had no fields for
    them. That was O-22's last unbuilt half.

    The refusal is at **plan load**, not at `estimate`: after `plan` the hash has
    already recorded a commitment the tool cannot honour.
    """
    with pytest.raises(Refusal) as caught:
        Plan.from_mapping(
            BASE | {"interval": "wilson", "sensitivity": "0.90", "specificity": "0.999"}
        )
    assert caught.value.reason is Reason.CORRECTION_INTERVAL_UNSUPPORTED
    # D-37 condition 1: the trade-off in the operator's terms, with the numbers.
    assert "90.98" in caught.value.fix
    assert "85.32" in caught.value.fix
    assert "clopper_pearson" in caught.value.fix


def test_wilson_without_se_and_sp_is_accepted() -> None:
    """The positive control for the refusal above. Wilson is not being banned."""
    assert Plan.from_mapping(BASE | {"interval": "wilson"}).interval == "wilson"


# ------------------------------------------------- the schema declares itself


def test_every_hashed_field_declares_what_it_is_for() -> None:
    """The declaration half of **D2.14(d)**. The checker is that deliverable.

    Stated as a limit rather than implied: this asserts every hashed field has a
    kind, and **not** that the kind is true. Asserting the kinds is D2.14(d), and
    claiming more here would be **C-34** -- a scope stated wider than it is.
    """
    record = Plan.from_mapping(BASE).as_record()
    estimand = record["estimand"]
    assert isinstance(estimand, dict)
    fields = {k for k in record if k != "estimand"}
    fields |= {f"estimand.{k}" for k in estimand}

    assert fields == set(FIELD_KIND), (
        "a hashed plan field has no declared kind, or a kind names a field that is not hashed"
    )
    assert set(FIELD_KIND.values()) == {"behavioural", "declarative"}
    assert FIELD_KIND["sensitivity"] == "behavioural"
    assert FIELD_KIND["estimand.description"] == "declarative"


def test_the_expected_method_matches_what_the_estimator_stamps() -> None:
    """`expected_method` is checked against behaviour, not against a second copy.

    **This test exists because the first version was wrong.** The cross-check
    compared `INTERVAL_METHOD[plan.interval]` alone, which held while the
    correction was unreachable and became false the moment O-29 wired it: `verify`
    refused a correct corrected run, because `estimate.json` said
    `rogan-gladen/clopper-pearson` and the check expected `clopper-pearson`.

    **The cross-check was right and its input was wrong** -- two artifacts really
    did disagree. So the fix is not a wider comparison, it is deriving the
    expected string from the plan the same way the estimator derives it, in one
    place, and walking every constructible plan shape here to prove they agree.

    `wilson` + Se/Sp is not in the list because it cannot be constructed: Q7 /
    D-33 refuses it at plan load.
    """
    from prevalence_kit.run import expected_method

    shapes: list[dict[str, Any]] = [
        {"interval": "wilson"},
        {"interval": "clopper_pearson"},
        {"interval": "clopper_pearson", "sensitivity": "0.90", "specificity": "0.999"},
    ]
    for over in shapes:
        plan = Plan.from_mapping(BASE | over)
        stamped = _estimate_from(plan, LABELS).method
        assert expected_method(plan) == stamped, (
            f"expected_method predicts {expected_method(plan)!r} but the estimator "
            f"stamps {stamped!r} for {over}"
        )
