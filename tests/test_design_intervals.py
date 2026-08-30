"""O-26 / D2.17 -- the design-based intervals, and the cage S-2.4's narrowing needs.

**Q15 gave these their own names because they are intervals for different
quantities.** A binomial interval inverts a distribution over the sampled
`(k, n)`; a design-based one replaces `n` with `n_eff`. Under stratification the
pooled `k/n` is not even the design estimate -- `0.020000` against `0.011333` on
the `rare` fixture.

**And the second name is Korn-Graubard, not `design_clopper_pearson`.** The A-5
draft used that name. Measuring its coverage before shipping it -- the director's
condition -- showed it does **not** hold nominal, so the name would have promised
the one property Clopper-Pearson is chosen for. **A-6** renamed it.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

import pytest

from prevalence_kit.errors import Reason, Refusal
from prevalence_kit.estimators import (
    design_korn_graubard,
    design_wilson,
    probability_no_interval,
)

FIXTURE = Path(__file__).resolve().parents[1] / "svy" / "fixtures" / "design_intervals.json"
ESTIMATORS = Path(__file__).resolve().parents[1] / "src" / "prevalence_kit" / "estimators.py"

BUILDERS = {"design_wilson": design_wilson, "design_korn_graubard": design_korn_graubard}


def fixture() -> dict[str, Any]:
    parsed: dict[str, Any] = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return parsed


# ------------------------------------------------- witnessed, and fixture first


def test_the_fixture_predates_the_estimator() -> None:
    """R2.2, recorded in the artifact rather than only in a commit message."""
    data = fixture()
    assert data["obligation"] == "O-26"
    assert data["svy_version"] == "0.25.0"
    assert data["method_map"] == {
        "design_wilson": "wilson",
        "design_korn_graubard": "beta",
    }
    assert "korn-graubard" in data["not_offered"]


@pytest.mark.parametrize("method", sorted(BUILDERS))
def test_the_design_intervals_reproduce_svy(method: str) -> None:
    """Every fixture row, both endpoints. R2.3 asks four significant digits.

    The first implementation missed Korn-Graubard's degrees-of-freedom
    adjustment -- `n_eff` scaled by `(t_{n-1} / t_df)^2` -- and agreed to
    5e-04, which is inside "looks right" and outside R2.3. **The fixture is what
    caught it**, which is the ordering's whole purpose.
    """
    data = fixture()
    worst = 0.0
    rows = 0
    for case in data["cases"]:
        for entry in case["intervals"][method]:
            got = BUILDERS[method](
                entry["point"],
                entry["se"],
                entry["df"],
                entry["n"],
                confidence=entry["confidence"],
            )
            worst = max(
                worst,
                abs(float(got.low) - entry["low"]),
                abs(float(got.high) - entry["high"]),
            )
            rows += 1
    assert rows == 15
    assert worst < 1e-9, f"{method}: worst endpoint disagreement {worst:.3e}"


def test_the_two_intervals_are_not_the_same_interval() -> None:
    """A control on the pair. If they agreed everywhere, one name would do."""
    data = fixture()
    case = next(c for c in data["cases"] if c["label"] == "rare")
    entry = next(e for e in case["intervals"]["design_wilson"] if e["confidence"] == 0.95)
    wilson = design_wilson(entry["point"], entry["se"], entry["df"], entry["n"])
    kg = design_korn_graubard(entry["point"], entry["se"], entry["df"], entry["n"])
    assert (wilson.low, wilson.high) != (kg.low, kg.high)


# ------------------------------------------------------ the undefined interval


def test_a_zero_standard_error_refuses_by_name() -> None:
    """`INTERVAL_UNDEFINED`. There is no spread, so there is nothing to invert.

    Refusing rather than inventing an interval is the point: at rare rates this
    is the most likely single outcome, not an edge case.
    """
    for builder in BUILDERS.values():
        with pytest.raises(Refusal) as caught:
            builder(0.0, 0.0, 100, 150)
        assert caught.value.reason is Reason.INTERVAL_UNDEFINED
        # **The verb has to be the one that actually reports the odds.** This
        # line asserted `plan` and passed, because the fix text said `plan` --
        # and the odds are computed at `sample`, where the allocation and the
        # frame sizes exist. The test agreed with the message rather than with
        # the tool, so an operator sent to `plan` would have found nothing.
        assert "`sample` reports" in caught.value.fix
        assert "`plan` reports" not in caught.value.fix


def test_a_real_standard_error_is_accepted() -> None:
    """The positive control for the refusal above."""
    for builder in BUILDERS.values():
        assert builder(0.1, 0.02, 100, 150).point == "0.100000000000"


def test_the_odds_of_no_interval_match_the_exhaustive_measurement() -> None:
    """The closed form against the enumeration that produced the coverage table.

    `P = product over strata of (1 - p_h) ** n_h`. The coverage run computed the
    same quantity by summing the full product space of outcomes, and the two
    agree to four decimal places -- which is what makes it safe to tell an
    operator this number at `sample` instead of simulating it.
    """
    assert probability_no_interval([0.001, 0.001], [90, 40]) == pytest.approx(0.8780, abs=5e-5)
    assert probability_no_interval([0.001] * 3, [60, 120, 120]) == pytest.approx(0.7407, abs=5e-5)
    # A design that will almost certainly produce one.
    assert probability_no_interval([0.20, 0.01], [102, 48]) < 1e-9


def test_the_odds_are_recorded_and_not_only_printed(tmp_path: Path) -> None:
    """An auditor reading the run later sees what the design's odds were.

    Printed-only would make it a courtesy to whoever ran the command. In the
    ledger it is part of the record the run is judged on.
    """
    import yaml

    from prevalence_kit.plan import Plan
    from prevalence_kit.run import Workspace, do_plan, do_sample

    rows = ["item_id,stratum"]
    rows += [f"a-{i:04d},a" for i in range(400)]
    rows += [f"b-{i:04d},b" for i in range(600)]
    (tmp_path / "frame.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    body = {
        "estimand": {
            "description": "t",
            "label_field": "toxicity",
            "positive_when": "at_least",
            "threshold": "0.5",
        },
        "population": "frame.csv",
        "design": "stratified",
        "sample_size": 60,
        "labels": "labels.csv",
        "seed": "odds",
        "interval": "design_korn_graubard",
        "allocation_rounding": "largest_remainder",
        "strata": [
            {"name": "a", "expected_rate": "0.001"},
            {"name": "b", "expected_rate": "0.001"},
        ],
    }
    (tmp_path / "plan.yaml").write_text(yaml.safe_dump(body, sort_keys=True), encoding="utf-8")
    plan = Plan.load(tmp_path / "plan.yaml")
    ws = Workspace(tmp_path / "run")
    do_plan(ws, plan)
    do_sample(ws, plan, tmp_path / "frame.csv")

    body_out = ws.ledger.verify()[-1].body
    assert "probability_no_interval" in body_out
    assert float(str(body_out["probability_no_interval"])) > 0.9


# ------------------------- condition 1: the cage that replaces S-2.4's sentence


def _reachable_from(function: str, tree: ast.Module) -> set[str]:
    """Every module-level function reachable from `function`, transitively."""
    defined = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    seen: set[str] = set()
    stack = [function]
    while stack:
        name = stack.pop()
        if name in seen or name not in defined:
            continue
        seen.add(name)
        for node in ast.walk(defined[name]):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                stack.append(node.func.id)
    return seen


def test_the_binomial_path_cannot_reach_the_incomplete_beta() -> None:
    """**Condition 1 on A's narrowing: the structure is replaced, not removed.**

    `docs/STANDARDS.md` S-2.4 used to say there was **no incomplete beta anywhere
    in this package**, which made D2.4's independence from base R's `qbeta`
    structural rather than careful -- the failure of checking `betainc` against
    `betainc` could not occur, by construction.

    The design intervals need one, so the beta now exists. **That is a downgrade
    from impossible to disciplined unless something asserts it**, and this
    project's doctrine is that discipline does not hold and structure does.

    So: the binomial `clopper_pearson` still root-finds on the tail, and this
    walks its call graph to prove it **cannot reach** `regularised_beta`. Same
    shape as `test_no_ai_module_reaches_the_evidence_path` -- a cage checked
    statically rather than a promise in a docstring.
    """
    tree = ast.parse(ESTIMATORS.read_text(encoding="utf-8"))
    reachable = _reachable_from("clopper_pearson", tree)

    assert "regularised_beta" not in reachable, (
        "the binomial Clopper-Pearson can now reach the incomplete beta, so its "
        "independence from base R's qbeta is no longer structural -- S-2.4's "
        "narrowed claim would be false"
    )
    assert "_beta_quantile" not in reachable
    # And the control: the design path DOES reach it, so this test is capable of
    # telling the two apart rather than passing because nothing reaches anything.
    assert "regularised_beta" in _reachable_from("design_korn_graubard", tree)


def test_the_incomplete_beta_exists_exactly_once() -> None:
    """One implementation, so there is one thing to check and one to reason about."""
    source = ESTIMATORS.read_text(encoding="utf-8")
    tree = ast.parse(source)
    names = [n.name for n in tree.body if isinstance(n, ast.FunctionDef)]
    assert names.count("regularised_beta") == 1
    assert "scipy" not in source, "the beta is written here, not imported"


def test_a_stratified_estimate_without_its_recorded_draw_refuses_by_name() -> None:
    """`DESIGN_NOT_ESTIMABLE`, and it now guards a different thing than it did.

    It used to mean *this version cannot estimate a stratified design at all* --
    the honest placeholder while the path drew but had no interval. **O-26 built
    the interval**, so what remains is the API surface D-25 records as real: a
    caller who has a plan and labels but does not pass the recorded per-stratum
    draw. The design estimate is a weighted mean of per-stratum rates, and a flat
    label dict cannot say which unit sat where.

    Unreachable through the CLI, which always reads the draw from the run
    directory -- so this is a guard on the Python API, classified the way
    `PLAN_FILE_MISSING` is under Q8 / D-35.
    """
    from prevalence_kit.plan import Plan
    from prevalence_kit.run import _estimate_from

    plan = Plan.from_mapping(
        {
            "estimand": {
                "description": "t",
                "label_field": "toxicity",
                "positive_when": "at_least",
                "threshold": "0.5",
            },
            "population": "frame.csv",
            "design": "stratified",
            "sample_size": 60,
            "labels": "labels.csv",
            "seed": "s",
            "interval": "design_wilson",
            "allocation_rounding": "largest_remainder",
            "strata": [{"name": "a", "expected_rate": "0.10"}],
        }
    )
    with pytest.raises(Refusal) as caught:
        _estimate_from(plan, {"a-0001": "0.9"}, None)

    assert caught.value.reason is Reason.DESIGN_NOT_ESTIMABLE
    assert "StratifiedDraw" in caught.value.fix
