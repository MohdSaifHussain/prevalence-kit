"""Canonicalisation, the plan's pre-registration property, the ledger chain,
deterministic sampling, and the Wilson interval.

Each gate gets both controls: a case it must accept, and a case it must refuse.
"""

from __future__ import annotations

from math import sqrt
from pathlib import Path
from statistics import NormalDist
from types import SimpleNamespace

import pytest
import yaml

from prevalence_kit.canonical import canonical, digest
from prevalence_kit.errors import Reason, Refusal
from prevalence_kit.estimators import wilson
from prevalence_kit.ledger import Ledger
from prevalence_kit.plan import Plan
from prevalence_kit.sampling import draw_srs
from tests.conftest import PLAN_YAML, rewrite_ledger_line

# ------------------------------------------------------------------ canonical


def test_key_order_does_not_change_the_digest() -> None:
    assert digest({"a": 1, "b": 2}) == digest({"b": 2, "a": 1})


def test_canonical_is_compact_utf8() -> None:
    assert canonical({"k": "é"}) == b'{"k":"\xc3\xa9"}'


def test_floats_are_refused() -> None:
    """A digest that depends on platform float formatting is not a digest."""
    with pytest.raises(TypeError, match="round-trip"):
        digest({"p": 0.1})


def test_nested_floats_are_refused() -> None:
    with pytest.raises(TypeError):
        digest({"outer": [{"inner": 1.5}]})


# ----------------------------------------------------------------------- plan


def test_hash_does_not_need_the_data(tmp_path: Path) -> None:
    """R1, and the whole basis of pre-registration.

    The plan points at files that do not exist. If the hash still comes out, the
    hash cannot depend on the data -- which is what makes it a commitment rather
    than a description. Exit check E2.
    """
    spec = dict(PLAN_YAML) | {"population": "no-such-frame.txt", "labels": "no-such-labels.csv"}
    path = tmp_path / "plan.yaml"
    path.write_text(yaml.safe_dump(spec, sort_keys=True), encoding="utf-8")

    assert len(Plan.load(path).plan_hash) == 64


def test_plan_identity_survives_being_moved(tmp_path: Path, plan_path: Path) -> None:
    """Where the file sits is not part of the commitment."""
    moved = tmp_path / "elsewhere" / "plan.yaml"
    moved.parent.mkdir()
    moved.write_text(plan_path.read_text(encoding="utf-8"), encoding="utf-8")
    assert Plan.load(moved).plan_hash == Plan.load(plan_path).plan_hash


def test_any_field_change_changes_the_hash(plan: Plan) -> None:
    for field, value in [("population", "other.txt"), ("seed", "different"), ("sample_size", 41)]:
        altered = Plan.from_mapping(PLAN_YAML | {field: value})
        assert altered.plan_hash != plan.plan_hash, field


def test_missing_seed_has_its_own_reason_code() -> None:
    """Not folded into a generic schema error: an unseeded sample cannot be redrawn."""
    with pytest.raises(Refusal) as exc:
        Plan.from_mapping(PLAN_YAML | {"seed": ""})
    assert exc.value.reason is Reason.SEED_MISSING


def test_unsupported_design_refused() -> None:
    with pytest.raises(Refusal) as exc:
        Plan.from_mapping(PLAN_YAML | {"design": "stratified"})
    assert exc.value.reason is Reason.PLAN_INVALID


def test_zero_sample_size_refused() -> None:
    with pytest.raises(Refusal) as exc:
        Plan.from_mapping(PLAN_YAML | {"sample_size": 0})
    assert exc.value.reason is Reason.EMPTY_SAMPLE


def test_threshold_semantics(plan: Plan) -> None:
    assert plan.estimand.is_positive("0.5")
    assert plan.estimand.is_positive("0.51")
    assert not plan.estimand.is_positive("0.49")


# --------------------------------------------------------------------- ledger


def test_intact_chain_verifies(tmp_path: Path) -> None:
    led = Ledger(tmp_path / "l.jsonl")
    for step in ("plan", "sample", "estimate"):
        led.append(step, {"x": step})
    assert [e.step for e in led.verify()] == ["plan", "sample", "estimate"]


def test_edited_entry_breaks_the_chain(tmp_path: Path) -> None:
    path = tmp_path / "ledger.jsonl"
    led = Ledger(path)
    led.append("plan", {"plan_hash": "aaa"})
    led.append("sample", {"n": 40})
    rewrite_ledger_line(
        SimpleNamespace(root=tmp_path), 0, lambda r: r["body"].__setitem__("plan_hash", "bbb")
    )

    with pytest.raises(Refusal) as exc:
        led.verify()
    assert exc.value.reason is Reason.LEDGER_BROKEN


def test_removed_entry_breaks_the_chain(tmp_path: Path) -> None:
    path = tmp_path / "l.jsonl"
    led = Ledger(path)
    for step in ("plan", "sample", "estimate"):
        led.append(step, {"x": step})
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join([lines[0], lines[2]]) + "\n", encoding="utf-8", newline="\n")

    with pytest.raises(Refusal) as exc:
        led.verify()
    assert exc.value.reason is Reason.LEDGER_BROKEN


def test_truncated_json_line_is_a_refusal_not_a_traceback(tmp_path: Path) -> None:
    path = tmp_path / "l.jsonl"
    Ledger(path).append("plan", {"a": 1})
    path.write_text(path.read_text(encoding="utf-8")[:-20], encoding="utf-8")

    with pytest.raises(Refusal) as exc:
        Ledger(path).verify()
    assert exc.value.reason is Reason.LEDGER_BROKEN


# ------------------------------------------------------------------- sampling


def test_draw_is_deterministic() -> None:
    frame = [f"item-{i:04d}" for i in range(200)]
    assert draw_srs(frame, seed="s", n=40) == draw_srs(frame, seed="s", n=40)


def test_draw_does_not_depend_on_frame_order() -> None:
    frame = [f"item-{i:04d}" for i in range(200)]
    assert draw_srs(frame, seed="s", n=40) == draw_srs(list(reversed(frame)), seed="s", n=40)


def test_different_seeds_give_different_samples() -> None:
    frame = [f"item-{i:04d}" for i in range(200)]
    assert draw_srs(frame, seed="a", n=40) != draw_srs(frame, seed="b", n=40)


def test_draw_is_a_subset_without_duplicates() -> None:
    frame = [f"item-{i:04d}" for i in range(200)]
    drawn = draw_srs(frame, seed="s", n=40)
    assert len(set(drawn)) == 40
    assert set(drawn) <= set(frame)


def test_draw_pinned_against_a_recorded_value() -> None:
    """Locks the selection rule itself.

    If someone later swaps the keyed-hash scheme for anything else, this fails --
    which is the point. Determinism that only holds within one release is not the
    property R2 asks for.
    """
    frame = [f"item-{i:04d}" for i in range(200)]
    assert draw_srs(frame, seed="phase-1-fixture-seed", n=5) == (
        "item-0129",
        "item-0089",
        "item-0169",
        "item-0027",
        "item-0008",
    )


def test_empty_frame_refused() -> None:
    with pytest.raises(Refusal) as exc:
        draw_srs([], seed="s", n=1)
    assert exc.value.reason is Reason.EMPTY_SAMPLE


def test_sample_larger_than_frame_refused() -> None:
    with pytest.raises(Refusal) as exc:
        draw_srs(["a", "b"], seed="s", n=5)
    assert exc.value.reason is Reason.EMPTY_SAMPLE


# ----------------------------------------------------------------- estimators


@pytest.mark.parametrize(
    ("positives", "n"),
    [(5, 100), (1, 10000), (37, 250), (3, 40), (500, 1000)],
)
def test_wilson_endpoints_satisfy_the_score_equation(positives: int, n: int) -> None:
    """Tests the definition, not the algebra.

    The Wilson interval IS the set of p for which the score statistic
    |p_hat - p| / sqrt(p(1-p)/n) does not exceed z. So at each endpoint that
    statistic must equal z. Checking this rather than hard-coded numbers means the
    test cannot agree with the implementation for the same wrong reason -- which is
    the failure mode a builder writing both is most prone to.

    Tolerance is 1e-6: the endpoints are stored to 12 decimal places, so the
    residual here is string rounding, not arithmetic.
    """
    z = NormalDist().inv_cdf(0.975)
    r = wilson(positives, n)
    p_hat = positives / n
    for endpoint in (float(r.low), float(r.high)):
        score = abs(p_hat - endpoint) / sqrt(endpoint * (1 - endpoint) / n)
        assert score == pytest.approx(z, abs=1e-6)


@pytest.mark.parametrize(
    ("positives", "n", "low", "high"),
    [
        # Recorded from a run on 2026-08-28, after the score-equation property
        # above confirmed the implementation. These pin the values so a later
        # refactor that changes them has to say why.
        # Phase 2 cross-checks against R survey 4.5 (obligation O-4).
        (5, 100, "0.021543679154", "0.111750469232"),
        (0, 100, "0.000000000000", "0.036993498207"),
        (100, 100, "0.963006501793", "1.000000000000"),
        (1, 10000, "0.000017652674", "0.000566268897"),
    ],
)
def test_wilson_pinned_values(positives: int, n: int, low: str, high: str) -> None:
    result = wilson(positives, n)
    assert (result.low, result.high) == (low, high)


def test_wilson_is_defined_at_zero_positives() -> None:
    """The case that matters most: no violations found still needs an upper bound."""
    result = wilson(0, 500)
    assert float(result.point) == 0.0
    assert float(result.high) > 0.0


def test_wilson_interval_contains_the_point() -> None:
    for positives in (0, 1, 7, 50, 100):
        r = wilson(positives, 100)
        assert float(r.low) <= float(r.point) <= float(r.high)


def test_wilson_stays_inside_zero_one() -> None:
    for positives in (0, 1, 99, 100):
        r = wilson(positives, 100)
        assert float(r.low) >= 0.0 and float(r.high) <= 1.0


def test_wilson_narrows_as_n_grows() -> None:
    widths = [
        float(wilson(n // 20, n).high) - float(wilson(n // 20, n).low) for n in (100, 1000, 10000)
    ]
    assert widths[0] > widths[1] > widths[2]


def test_empty_sample_refused() -> None:
    with pytest.raises(Refusal) as exc:
        wilson(0, 0)
    assert exc.value.reason is Reason.EMPTY_SAMPLE


def test_impossible_positive_count_refused() -> None:
    with pytest.raises(Refusal) as exc:
        wilson(11, 10)
    assert exc.value.reason is Reason.LABELS_UNMATCHED
