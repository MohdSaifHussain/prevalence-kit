"""D2.8 -- the strata field in the hashed plan, the stratified draw, and F-10.

Three things land together here, and the reason they are one deliverable is the
hazard rather than tidiness: a stratified plan that loads and draws while
`_estimate_from` still answers with SRS Wilson would print a number that looks
fine, ignores the strata, and contradicts the design its own plan pre-registered.
So the draw and the refusal are built in one commit -- **a half-wired path that
produces a number is worse than a refusal.**

**F-10** is the defect that made this urgent. `plan.interval` was validated at
load, hashed into the pre-registration record, and read by nothing: a plan naming
`clopper_pearson` was answered with Wilson, and `verify` agreed because it
recomputes through the same function. Two fixes, and the second is the durable
one -- dispatch makes the artifacts agree today, the cross-check catches the next
field that goes inert the same way.

Every refusal here has both controls. A gate that refuses everything proves
nothing.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from prevalence_kit.errors import Reason, Refusal
from prevalence_kit.estimators import wilson
from prevalence_kit.plan import SUPPORTED_INTERVALS, Plan
from prevalence_kit.run import (
    INTERVAL_METHOD,
    Workspace,
    _estimate_from,
    _interval_for,
    do_estimate,
    do_ingest,
    do_plan,
    do_sample,
)
from prevalence_kit.verify import verify_run

from .conftest import PLAN_YAML, write_labels

STRATA: list[dict[str, Any]] = [
    {"name": "high", "expected_rate": "0.30"},
    {"name": "mid", "expected_rate": "0.05"},
    {"name": "low", "expected_rate": "0.002"},
]
SIZES = {"high": 200, "mid": 800, "low": 4000}


def stratified_plan(**over: Any) -> dict[str, Any]:
    base: dict[str, Any] = dict(PLAN_YAML) | {
        "population": "frame.csv",
        "design": "stratified",
        "sample_size": 300,
        "interval": "clopper_pearson",
        "allocation_rounding": "largest_remainder",
        "strata": [dict(s) for s in STRATA],
    }
    base.update(over)
    return base


def write_frame(path: Path, sizes: dict[str, int], *, rogue: str | None = None) -> Path:
    lines = ["item_id,stratum"]
    for name, count in sizes.items():
        lines.extend(f"{name}-{k:05d},{name}" for k in range(count))
    if rogue is not None:
        lines.append(f"rogue-1,{rogue}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


@pytest.fixture
def frame_csv(tmp_path: Path) -> Path:
    return write_frame(tmp_path / "frame.csv", SIZES)


# ------------------------------------------------------- F-10: the plan's method


@pytest.mark.parametrize("method", sorted(SUPPORTED_INTERVALS))
def test_the_estimator_uses_the_interval_the_plan_names(method: str) -> None:
    """F-10, the positive control, once per supported method.

    The bug this closes: `plan.interval` reached the hash and nothing read it.
    """
    plan = Plan.from_mapping(PLAN_YAML | {"interval": method})
    labels = {f"i{k}": ("1.0" if k < 9 else "0.0") for k in range(40)}

    assert _estimate_from(plan, labels).method == INTERVAL_METHOD[method]


def test_a_clopper_pearson_plan_does_not_return_wilson() -> None:
    """F-10's negative control, written as the defect rather than a stand-in.

    This is the exact state the tool shipped in for one commit: the plan says
    clopper_pearson and the number that comes back is Wilson's. The two intervals
    genuinely differ at this n, so the assertion cannot pass by coincidence.
    """
    labels = {f"i{k}": ("1.0" if k < 9 else "0.0") for k in range(40)}
    cp = _estimate_from(Plan.from_mapping(PLAN_YAML | {"interval": "clopper_pearson"}), labels)
    wilson = _estimate_from(Plan.from_mapping(PLAN_YAML | {"interval": "wilson"}), labels)

    assert cp.method != wilson.method
    assert (cp.low, cp.high) != (wilson.low, wilson.high), (
        "the two intervals are identical here, so this test could not tell them apart"
    )
    # The specific numbers, so a silent swap of one for the other is caught.
    assert (wilson.low, wilson.high) == ("0.123160913235", "0.375030967423")
    assert (cp.low, cp.high) == ("0.108396638984", "0.384511677303")


def test_every_supported_interval_stamps_the_method_the_map_claims() -> None:
    """`INTERVAL_METHOD` is checked against behaviour, not against a second copy.

    The plan says `clopper_pearson`; the estimator stamps `clopper-pearson`. Two
    vocabularies that must agree, so something makes them agree -- D-28. Comparing
    them directly fired a false `ESTIMATE_METHOD_MISMATCH` on every correct
    Clopper-Pearson run, and it was found by running the dispatch rather than by
    reading it.
    """
    assert set(INTERVAL_METHOD) == set(SUPPORTED_INTERVALS), (
        "a supported interval has no entry in INTERVAL_METHOD, so verify's "
        "cross-check would skip it silently"
    )
    for name in sorted(SUPPORTED_INTERVALS):
        plan = Plan.from_mapping(PLAN_YAML | {"interval": name})
        assert _interval_for(plan, 9, 40).method == INTERVAL_METHOD[name]


def test_verify_refuses_when_the_estimate_method_contradicts_the_plan(
    tmp_path: Path,
    plan_path: Path,
    frame_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """F-10's durable half, and the negative control is the defect itself.

    The scenario is **a broken writer, not a tamperer**: a build whose dispatch
    is wrong writes an estimate by one method while the plan pre-registers
    another, and every digest in the run is honest. That is precisely the state
    this tool shipped in for one commit -- so the control is reproduced by
    breaking the dispatch, not by editing a file.

    Editing `estimate.json` would trip `LEDGER_BROKEN` first, which is a
    different defect and would prove nothing about this one.

    **This check does not depend on the dispatch being right.** That is the whole
    point of it: dispatch makes the two artifacts agree today, and this catches
    the next plan field that goes inert the same way.
    """
    from prevalence_kit import run as run_module

    body = dict(PLAN_YAML) | {"interval": "clopper_pearson"}
    path = tmp_path / "cp-plan.yaml"
    path.write_text(yaml.safe_dump(body, sort_keys=True), encoding="utf-8")
    plan = Plan.load(path)

    # The broken build: whatever the plan says, Wilson comes back.
    monkeypatch.setattr(
        run_module,
        "_interval_for",
        lambda plan, positives, n: wilson(positives, n),
    )

    ws = Workspace(tmp_path / "run")
    do_plan(ws, plan)
    drawn = do_sample(ws, plan, frame_path)
    labels_path = write_labels(tmp_path, list(drawn), positives=9)
    do_ingest(ws, plan, labels_path)
    do_estimate(ws, plan)

    assert ws.read_json("estimate.json")["method"] == "wilson"

    # Now verify with the dispatch restored, as a later build would.
    monkeypatch.undo()
    with pytest.raises(Refusal) as caught:
        verify_run(ws)
    assert caught.value.reason is Reason.ESTIMATE_METHOD_MISMATCH
    assert "clopper_pearson" in caught.value.detail
    assert "wilson" in caught.value.detail


def test_verify_accepts_a_run_whose_method_matches_the_plan(run: Workspace) -> None:
    """The positive control for the cross-check above."""
    checks = verify_run(run)
    assert all(c.ok for c in checks)
    assert any(c.name == "estimate method" for c in checks), (
        "the cross-check did not run, so its green means nothing"
    )


# ------------------------------------------------------------ the plan's strata


def test_a_stratified_plan_carries_its_strata_into_the_hash(tmp_path: Path) -> None:
    """Q13 / D-39. Changing a stratum changes the plan hash, like every commitment."""
    plan = Plan.from_mapping(stratified_plan())
    record = plan.as_record()
    assert record["strata"] == [
        {"name": "high", "expected_rate": "0.30"},
        {"name": "mid", "expected_rate": "0.05"},
        {"name": "low", "expected_rate": "0.002"},
    ]

    moved = stratified_plan()
    moved["strata"][0]["expected_rate"] = "0.31"
    assert Plan.from_mapping(moved).plan_hash != plan.plan_hash


def test_expected_rate_is_a_decimal_string_not_a_float() -> None:
    """Estimand.threshold's precedent, and canonical() enforces it.

    Floats do not round-trip identically across platforms, and this value is in
    the pre-registration hash. Found by running the draw: `canonical()` refused
    the record outright.
    """
    plan = Plan.from_mapping(stratified_plan())
    assert plan.strata is not None
    assert all(isinstance(s.expected_rate, str) for s in plan.strata)
    assert plan.strata[0].rate == pytest.approx(0.30)
    assert plan.plan_hash  # canonical() would refuse a float here


def test_a_stratified_plan_with_no_strata_is_refused() -> None:
    """STRATA_UNDEFINED. The negative control."""
    body = stratified_plan()
    del body["strata"]
    with pytest.raises(Refusal) as caught:
        Plan.from_mapping(body)
    assert caught.value.reason is Reason.STRATA_UNDEFINED


def test_an_empty_strata_list_is_refused_the_same_way() -> None:
    with pytest.raises(Refusal) as caught:
        Plan.from_mapping(stratified_plan(strata=[]))
    assert caught.value.reason is Reason.STRATA_UNDEFINED


def test_a_valid_stratified_plan_is_accepted() -> None:
    """The positive control. A gate that refuses everything proves nothing."""
    plan = Plan.from_mapping(stratified_plan())
    assert plan.design == "stratified"
    assert plan.strata is not None
    assert [s.name for s in plan.strata] == ["high", "mid", "low"]


@pytest.mark.parametrize(
    ("strata", "fragment"),
    [
        ([{"name": "a"}], "expected_rate"),
        ([{"expected_rate": "0.1"}], "name"),
        ([{"name": "", "expected_rate": "0.1"}], "empty name"),
        ([{"name": "a", "expected_rate": "0.1"}, {"name": "a", "expected_rate": "0.2"}], "once"),
        ([{"name": "a", "expected_rate": "nope"}], "not a number"),
        ([{"name": "a", "expected_rate": "1.5"}], "outside"),
        ([{"name": "a", "expected_rate": "-0.1"}], "outside"),
        ("not-a-list", "not a list"),
    ],
)
def test_a_malformed_strata_block_is_refused_by_name(strata: Any, fragment: str) -> None:
    """PLAN_INVALID, not STRATA_UNDEFINED -- D-22, different acts.

    "Write a strata block" and "fix the one you wrote" send the operator to
    different places, so they are different codes.
    """
    with pytest.raises(Refusal) as caught:
        Plan.from_mapping(stratified_plan(strata=strata))
    assert caught.value.reason is Reason.PLAN_INVALID
    assert fragment in caught.value.detail


def test_strata_on_a_design_that_never_stratifies_is_refused() -> None:
    """Symmetric to allocation_rounding, and for F-10's reason.

    Accepting the block would hash a commitment into the plan that no step
    honours, which is exactly how `interval` went inert.
    """
    with pytest.raises(Refusal) as caught:
        Plan.from_mapping(PLAN_YAML | {"design": "srs", "strata": [dict(STRATA[0])]})
    assert caught.value.reason is Reason.PLAN_INVALID
    assert "never used" in caught.value.fix or "Remove the strata" in caught.value.fix


def test_one_stratum_is_accepted(tmp_path: Path) -> None:
    """D-38, ruled 2026-08-30. Both anchors admit L = 1.

    S-1.2 includes it explicitly as the case where stratified sampling becomes
    unrestricted sampling; S-1.3 sets no lower bound and its Table 5A.12 measures
    *from* it. Refusing would assert a rule neither source supports.

    What it must not be is silent, and that is O-27's disclosure, post-stop.
    """
    plan = Plan.from_mapping(
        stratified_plan(sample_size=50, strata=[{"name": "only", "expected_rate": "0.2"}])
    )
    assert plan.strata is not None
    assert len(plan.strata) == 1

    frame = write_frame(tmp_path / "solo.csv", {"only": 500})
    ws = Workspace(tmp_path / "run")
    do_plan(ws, plan)
    assert len(do_sample(ws, plan, frame)) == 50


# ---------------------------------------------------------- the stratified draw


def test_the_stratified_draw_allocates_and_sums_to_n(tmp_path: Path, frame_csv: Path) -> None:
    plan = Plan.from_mapping(stratified_plan())
    ws = Workspace(tmp_path / "run")
    do_plan(ws, plan)
    drawn = do_sample(ws, plan, frame_csv)

    record = ws.read_json("sample.json")
    allocation = record["allocation"]
    assert len(drawn) == plan.sample_size
    assert sum(allocation["units"]) == plan.sample_size
    assert record["method"] == "sha256-keyed-sort-per-stratum"
    # Every drawn id came from the stratum it was allocated to. S-1.13's
    # independence rule: the draws are per stratum, not one draw partitioned.
    for name, ids in record["by_stratum"].items():
        assert all(i.startswith(f"{name}-") for i in ids)
    per = {name: len(ids) for name, ids in record["by_stratum"].items()}
    assert per == dict(zip(allocation["strata"], allocation["units"], strict=True))


def test_the_ledger_carries_both_allocations(tmp_path: Path, frame_csv: Path) -> None:
    """D-30 condition 3: raw and rounded both reach the record.

    An outsider re-derives the rounding without running this code, and `verify`
    re-derives it so a changed rule breaks the chain.
    """
    plan = Plan.from_mapping(stratified_plan())
    ws = Workspace(tmp_path / "run")
    do_plan(ws, plan)
    do_sample(ws, plan, frame_csv)

    allocation = ws.read_json("sample.json")["allocation"]
    assert allocation["rule"] == "largest_remainder"
    assert len(allocation["raw"]) == len(allocation["units"]) == 3
    # Raw values are strings for canonical()'s reason, and they are not integers.
    assert any("." in str(r) for r in allocation["raw"])


def test_the_stratified_draw_is_deterministic(tmp_path: Path, frame_csv: Path) -> None:
    """R2, per stratum. The stratum never enters the key -- D-16 unchanged."""
    plan = Plan.from_mapping(stratified_plan())
    first = Workspace(tmp_path / "a")
    do_plan(first, plan)
    second = Workspace(tmp_path / "b")
    do_plan(second, plan)

    assert do_sample(first, plan, frame_csv) == do_sample(second, plan, frame_csv)


def test_verify_redraws_the_stratified_sample(tmp_path: Path, frame_csv: Path) -> None:
    """verify.py called draw_srs unconditionally -- F-10's family, third site.

    A stratified run checked against a simple random redraw is the auditor's tool
    making the same substitution the estimator was making.
    """
    plan = Plan.from_mapping(stratified_plan())
    ws = Workspace(tmp_path / "run")
    do_plan(ws, plan)
    do_sample(ws, plan, frame_csv)

    checks = verify_run(ws)
    assert all(c.ok for c in checks)
    assert any("redrawn" in c.note for c in checks)


# -------------------------------------------------------------------- refusals


def test_a_frame_unit_in_an_undeclared_stratum_is_refused(tmp_path: Path) -> None:
    """Q14 / D-40. Dropping it would change the denominator -- V-7's class."""
    frame = write_frame(tmp_path / "bad.csv", SIZES, rogue="unexpected")
    plan = Plan.from_mapping(stratified_plan())
    ws = Workspace(tmp_path / "run")
    do_plan(ws, plan)

    with pytest.raises(Refusal) as caught:
        do_sample(ws, plan, frame)
    assert caught.value.reason is Reason.STRATUM_UNDECLARED
    assert "rogue-1" in caught.value.detail
    assert "unexpected" in caught.value.detail


def test_a_text_frame_under_a_stratified_design_is_refused(tmp_path: Path) -> None:
    """Same code, and that is D-22 rather than a shortcut.

    A .txt frame has no stratum column, so every unit is undeclared: same
    artifact to open, same remedial act, direction carried in the detail text.
    PLAN_THRESHOLD_INVALID's precedent on its second outing.
    """
    frame = tmp_path / "frame.txt"
    frame.write_text("a\nb\nc\n", encoding="utf-8")
    plan = Plan.from_mapping(stratified_plan(population="frame.txt"))
    ws = Workspace(tmp_path / "run")
    do_plan(ws, plan)

    with pytest.raises(Refusal) as caught:
        do_sample(ws, plan, frame)
    assert caught.value.reason is Reason.STRATUM_UNDECLARED
    assert "stratum" in caught.value.fix


def test_a_csv_frame_without_a_stratum_column_is_refused(tmp_path: Path) -> None:
    frame = tmp_path / "plain.csv"
    frame.write_text("item_id\na\nb\n", encoding="utf-8")
    plan = Plan.from_mapping(stratified_plan(population="plain.csv"))
    ws = Workspace(tmp_path / "run")
    do_plan(ws, plan)

    with pytest.raises(Refusal) as caught:
        do_sample(ws, plan, frame)
    assert caught.value.reason is Reason.STRATUM_UNDECLARED


def test_a_declared_stratum_with_no_frame_units_is_refused(tmp_path: Path, frame_csv: Path) -> None:
    """STRATUM_EMPTY sends the operator to the frame; STRATUM_UNSAMPLED to the
    sample. D-22 keeps them apart."""
    plan = Plan.from_mapping(
        stratified_plan(strata=[*STRATA, {"name": "ghost", "expected_rate": "0.1"}])
    )
    ws = Workspace(tmp_path / "run")
    do_plan(ws, plan)

    with pytest.raises(Refusal) as caught:
        do_sample(ws, plan, frame_csv)
    assert caught.value.reason is Reason.STRATUM_EMPTY
    assert "ghost" in caught.value.detail


def test_a_stratified_run_refuses_to_estimate_by_name(tmp_path: Path, frame_csv: Path) -> None:
    """The hazard this deliverable exists to close.

    Without this, `_estimate_from` answers a stratified draw with SRS Wilson: a
    number that looks fine and is not the design. O-26 builds the interval, under
    Q7 -- the plan names the method.
    """
    plan = Plan.from_mapping(stratified_plan())
    ws = Workspace(tmp_path / "run")
    do_plan(ws, plan)
    drawn = do_sample(ws, plan, frame_csv)

    with pytest.raises(Refusal) as caught:
        _estimate_from(plan, dict.fromkeys(drawn, "0.0"))
    assert caught.value.reason is Reason.DESIGN_NOT_ESTIMABLE
    assert "O-26" in caught.value.fix


def test_an_srs_run_still_estimates(plan: Plan) -> None:
    """The positive control for the refusal above.

    The refusal must be about the design, not about estimating at all.
    """
    labels = {f"i{k}": ("1.0" if k < 9 else "0.0") for k in range(40)}
    assert _estimate_from(plan, labels).point == "0.225000000000"


def test_the_plan_yaml_round_trips_through_disk(tmp_path: Path) -> None:
    """The schema has to survive YAML, not just a dict literal.

    `expected_rate` is a decimal string; YAML would happily turn an unquoted 0.30
    into a float, so this pins that a written plan loads back the same way.
    """
    path = tmp_path / "plan.yaml"
    path.write_text(yaml.safe_dump(stratified_plan(), sort_keys=True), encoding="utf-8")
    loaded = Plan.load(path)
    assert loaded.strata is not None
    assert [s.expected_rate for s in loaded.strata] == ["0.30", "0.05", "0.002"]
