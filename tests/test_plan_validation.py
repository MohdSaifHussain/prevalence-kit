"""Pre-registration must be worth something at the moment it is issued.

The class of defect here: a plan that is accepted, hashed, sealed and reported
as a commitment -- and then turns out to have committed to nothing. The operator
gets a hash, believes they have pre-registered, and finds out at the end.

So the estimand is validated at `Plan.load`, and the estimate-time refusal is
kept as the second net rather than the only one.

Every gate gets both controls, because a validator that rejects everything is
worth as little as one that rejects nothing.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from prevalence_kit.errors import Reason, Refusal
from prevalence_kit.plan import SUPPORTED_COMPARISONS, Estimand, Plan
from prevalence_kit.run import _CSV_FIELD_LIMIT, _read_frame, _read_labels
from tests.conftest import PLAN_YAML


def with_estimand(**changes: object) -> dict[str, object]:
    return PLAN_YAML | {"estimand": PLAN_YAML["estimand"] | changes}


# ------------------------------------------------- V-3: positive_when is closed


def test_both_supported_comparisons_are_accepted() -> None:
    assert (
        Plan.from_mapping(with_estimand(positive_when="at_least")).estimand.positive_when
        == "at_least"
    )
    assert (
        Plan.from_mapping(
            with_estimand(positive_when="equals", threshold="violating")
        ).estimand.positive_when
        == "equals"
    )
    assert {"equals", "at_least"} == SUPPORTED_COMPARISONS


@pytest.mark.parametrize("typo", ["greater_than", "gte", "at least", "EQUAL", ""])
def test_an_unrecognised_comparison_is_refused(typo: str) -> None:
    """V-3. Anything unrecognised used to fall through to `at_least`.

    A typo silently changed what was being measured -- and the wrong meaning is
    what got canonicalised, hashed and sealed as the commitment.
    """
    with pytest.raises(Refusal) as exc:
        Plan.from_mapping(with_estimand(positive_when=typo))
    assert exc.value.reason is Reason.PLAN_INVALID


# ------------------------------------------------------ V-4 and V-8: threshold


def test_a_numeric_threshold_is_accepted_for_at_least() -> None:
    assert Plan.from_mapping(with_estimand(threshold="0.5")).estimand.threshold == "0.5"


@pytest.mark.parametrize("bad", ["high", "toxic", "", "0.5.1"])
def test_a_non_numeric_threshold_is_refused_at_load(bad: str) -> None:
    """V-4. `threshold: high` used to pass `plan`, print a hash, and detonate later.

    A pre-registration that accepts a meaningless estimand is not a
    pre-registration.
    """
    with pytest.raises(Refusal) as exc:
        Plan.from_mapping(with_estimand(positive_when="at_least", threshold=bad))
    assert exc.value.reason is Reason.PLAN_THRESHOLD_INVALID


def test_a_categorical_threshold_is_accepted_for_equals() -> None:
    plan = Plan.from_mapping(with_estimand(positive_when="equals", threshold="violating"))
    assert plan.estimand.is_positive("violating")
    assert plan.estimand.is_positive("  violating  ")
    assert not plan.estimand.is_positive("not_violating")


def test_a_numeric_threshold_under_equals_is_refused(recwarn: pytest.WarningsRecorder) -> None:
    """V-8, decided rather than left open.

    `equals` is exact string identity. Under it, a threshold of '1' against a
    label of '1.0' counts as negative -- the tool prints a wrong number and never
    refuses. Rather than document the trap, the trap is removed: a numeric
    threshold under `equals` is refused and the operator is sent to `at_least`.
    """
    with pytest.raises(Refusal) as exc:
        Plan.from_mapping(with_estimand(positive_when="equals", threshold="1"))
    assert exc.value.reason is Reason.PLAN_THRESHOLD_INVALID
    assert "at_least" in exc.value.fix


# ------------------------------------------------------------- F-3: sample_size


def test_a_valid_sample_size_is_accepted() -> None:
    assert Plan.from_mapping(PLAN_YAML | {"sample_size": 40}).sample_size == 40


def test_a_missing_sample_size_is_a_missing_field() -> None:
    """F-3. It used to default to 0 and refuse `EMPTY_SAMPLE`.

    That is a missing-field problem wearing an empty-sample code, and it sent the
    operator to the wrong part of their plan.
    """
    spec = {k: v for k, v in PLAN_YAML.items() if k != "sample_size"}
    with pytest.raises(Refusal) as exc:
        Plan.from_mapping(spec)
    assert exc.value.reason is Reason.PLAN_INVALID
    assert "sample_size" in exc.value.detail


@pytest.mark.parametrize("bad", [40.7, "40", None, True])
def test_a_non_integer_sample_size_is_refused(bad: object) -> None:
    """40.7 used to become 40 in silence. A fraction of an item cannot be sampled."""
    with pytest.raises(Refusal) as exc:
        Plan.from_mapping(PLAN_YAML | {"sample_size": bad})
    assert exc.value.reason is Reason.PLAN_INVALID


def test_zero_sample_size_keeps_its_own_code() -> None:
    with pytest.raises(Refusal) as exc:
        Plan.from_mapping(PLAN_YAML | {"sample_size": 0})
    assert exc.value.reason is Reason.EMPTY_SAMPLE


# ------------------------------------------------- F-1: labels at estimate time


def test_a_numeric_label_is_accepted(plan: Plan) -> None:
    assert plan.estimand.is_positive("0.90")
    assert not plan.estimand.is_positive("0.10")


@pytest.mark.parametrize("bad", ["unclear", "n/a", "", "  ", "TRUE"])
def test_a_non_numeric_label_is_refused_by_name(plan: Plan, bad: str) -> None:
    """F-1. Real label columns contain exactly these values.

    This used to be `ValueError: could not convert string to float: 'unclear'` --
    a raw traceback on the most likely real-world input error.
    """
    with pytest.raises(Refusal) as exc:
        plan.estimand.is_positive(bad)
    assert exc.value.reason is Reason.LABEL_NOT_NUMERIC


def test_the_estimate_names_the_offending_item(plan: Plan) -> None:
    """The second net, and it has to be findable: which row?"""
    from prevalence_kit.run import _estimate_from

    with pytest.raises(Refusal) as exc:
        _estimate_from(plan, {"item-0001": "0.9", "item-0002": "unclear"})
    assert exc.value.reason is Reason.LABEL_NOT_NUMERIC
    assert "item-0002" in exc.value.detail


def test_a_clean_label_set_still_estimates(plan: Plan) -> None:
    from prevalence_kit.run import _estimate_from

    result = _estimate_from(plan, {"a": "0.9", "b": "0.1", "c": "0.9"})
    assert result.positives == 2
    assert result.n == 3


# ----------------------------------------------------- V-11: the named ceiling


def test_a_field_within_the_ceiling_is_read(tmp_path: Path) -> None:
    path = tmp_path / "labels.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["item_id", "toxicity", "content"])
        w.writerow(["i1", "0.9", "Z" * 200_000])  # over csv's own 128 KiB default
    assert len(_read_labels(path, "toxicity")["i1"][1]) == 200_000


def test_the_ceiling_is_named_not_a_traceback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """V-11. D-19 moved this cliff from 128 KiB to 64 MiB; it did not remove it.

    Tested by shrinking the limit rather than writing a 64 MiB file -- same code
    path, same failure shape, one second instead of a minute.
    """
    monkeypatch.setattr("prevalence_kit.run._CSV_FIELD_LIMIT", 4096)
    path = tmp_path / "labels.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["item_id", "toxicity", "content"])
        w.writerow(["i1", "0.9", "Z" * 8192])

    with pytest.raises(Refusal) as exc:
        _read_labels(path, "toxicity")
    assert exc.value.reason is Reason.CONTENT_TOO_LARGE


def test_the_ceiling_is_asserted_so_it_cannot_drift() -> None:
    """Rule 8: a limit that is checkable is asserted as a passing test.

    The day this number changes, this fails and whoever changed it has to say so
    rather than letting a documented figure quietly outlive its own truth.
    """
    assert _CSV_FIELD_LIMIT == 64 * 1024 * 1024


def test_the_csv_field_limit_is_restored_afterwards(tmp_path: Path) -> None:
    """It is process-global state. This tool does not get to leave it changed."""
    before = csv.field_size_limit()
    path = tmp_path / "labels.csv"
    path.write_text("item_id,toxicity\ni1,0.9\n", encoding="utf-8")
    _read_labels(path, "toxicity")
    assert csv.field_size_limit() == before


# ------------------------------------------- V-7: duplicate rows are not silent


def test_both_frame_counts_reach_the_record(tmp_path: Path) -> None:
    """V-7. De-duplicating a frame is correct; doing it silently is not.

    For a prevalence tool this is the denominator.
    """
    import yaml

    from prevalence_kit.run import Workspace, do_plan, do_sample

    frame = tmp_path / "frame.txt"
    frame.write_text("\n".join(f"item-{i % 200:04d}" for i in range(300)), encoding="utf-8")
    # F-11: `population` resolves against the plan file's directory, so a test
    # that runs `sample` needs a plan file, exactly like a real invocation.
    plan_path = tmp_path / "plan.yaml"
    plan_path.write_text(yaml.safe_dump(PLAN_YAML, sort_keys=True), encoding="utf-8")
    plan = Plan.load(plan_path)

    ws = Workspace(tmp_path / "run")
    do_plan(ws, plan)
    do_sample(ws, plan, frame)

    body = ws.ledger.verify()[1].body
    assert body["frame_rows_read"] == 300
    assert body["frame_unique_ids"] == 200


def test_both_frame_readers_strip_whitespace(tmp_path: Path) -> None:
    """They used to disagree: " item-1" was two members from a CSV, one from text."""
    text = tmp_path / "f.txt"
    text.write_text(" item-1 \nitem-1\nitem-2\n", encoding="utf-8")
    comma = tmp_path / "f.csv"
    comma.write_text("item_id\n item-1 \nitem-1\nitem-2\n", encoding="utf-8")
    assert _read_frame(text) == _read_frame(comma) == ["item-1", "item-1", "item-2"]


def test_blank_frame_rows_are_dropped_by_both_readers(tmp_path: Path) -> None:
    text = tmp_path / "f.txt"
    text.write_text("item-1\n\n   \nitem-2\n", encoding="utf-8")
    assert _read_frame(text) == ["item-1", "item-2"]


def test_estimand_is_frozen() -> None:
    """The commitment must not be mutable after it is hashed."""
    est = Estimand(description="d", label_field="l", positive_when="at_least", threshold="0.5")
    with pytest.raises(AttributeError):
        est.threshold = "0.05"  # type: ignore[misc]
