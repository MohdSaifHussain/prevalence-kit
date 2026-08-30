"""D2.9 -- the `svy` cross-check, and the narrowing that decides its scope.

**O-4 as narrowed by D-18**: `svy` is a witness *only where its estimator is the
same estimator*. This file is the measurement of where that is true, and the
record of where it is not.

**The fixture is committed; `svy` is never installed here.** It declares a hard
dependency on `httpx`, and Hard Rule 1 is zero network calls at runtime, proven
by a test that fails if any network capability appears in the dependency tree --
D-2. So `svy/generate_allocation_fixtures.py` runs in a throwaway environment and
only its output is committed. These tests read JSON.

**Why allocation is the whole of it.** Every interval `svy` 0.25.0 offers is
design-based: `logit` is Wald on the logit scale, `beta` and `korn-graubard` use a
df-adjusted effective sample size, and its `wilson` is the one D-18 recorded.
**It maps the alias `"clopper-pearson"` to `"korn-graubard"`**, so asking it for
Clopper-Pearson does not return the textbook interval we ship. None of them
witnesses ours.

**Why this one matters more than a second opinion.** **F-9** established that the
allocation half of D2.3 had no external witness at all -- R `survey` has no
allocator, so the R fixture's `neyman()` is our own formula re-implemented by its
own author. **This is the first genuine outside check on allocation this project
has had**, and it independently reproduces **D-30**'s largest-remainder rounding
including the case that forced the ruling.
"""

from __future__ import annotations

import json
from itertools import pairwise
from pathlib import Path
from typing import Any

import pytest

from prevalence_kit.stratified import Stratum, largest_remainder, neyman_raw

FIXTURE = Path(__file__).resolve().parents[1] / "svy" / "fixtures" / "allocation.json"


def fixture() -> dict[str, Any]:
    parsed: dict[str, Any] = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return parsed


def ours_from_weights(weights: list[float], rates: list[float], n: int, frame: int) -> list[int]:
    strata = tuple(
        Stratum(name=f"s{i}", size=round(w * frame), variance_proxy=p)
        for i, (w, p) in enumerate(zip(weights, rates, strict=True))
    )
    return list(largest_remainder(neyman_raw(strata, n), n))


def test_the_fixture_records_the_version_and_the_exact_call() -> None:
    """O-3's rule, applied to `svy` rather than to R.

    A fixture whose provenance is not recorded is a number with no witness
    attached to it.
    """
    data = fixture()
    assert data["svy_version"] == "0.25.0", (
        "S-2.2 pins 0.25.0. If this moved, the register and TW-2 move with it -- "
        "the witness is the pinned build, not whatever is current (C-25)."
    )
    assert "_neyman_allocation" in data["exact_call"]
    assert data["deliverable"] == "D2.9"
    # numpy decides the tie ordering, so it is part of this fixture's provenance
    # exactly as svy's own version is.
    assert data["numpy_version"]


@pytest.mark.parametrize(
    "label", ["barnett_neyman_4000", "two_stratum_neyman_1000", "rare_event_neyman_5000"]
)
def test_svy_reproduces_our_allocation_on_every_shipped_fixture(label: str) -> None:
    """The three Neyman allocations this project ships, checked against svy.

    `rare_event_neyman_5000` is the one that matters most: it is the case whose
    floors summed to 4999 and forced **Q4 / D-30**. `svy` independently rounds it
    to the same `3846/884/270`, giving the same stratum the remainder.
    """
    data = fixture()
    case = next(f for f in data["shipped_fixtures"] if f["label"] == label)
    ours = ours_from_weights(case["W_h"], case["p_h"], case["n_total"], data["frame_total"])

    assert ours == case["allocation"], f"{label}: ours {ours} vs svy {case['allocation']}"


def test_svy_breaks_an_exact_tie_the_way_d30_condition_2_pins_it() -> None:
    """D-30 condition 2 said OUR tie-break must be deterministic and stated.

    It did not say another implementation would agree, and nothing required that.

    **This is a measurement on a numpy build, not a property of `svy`.** `svy`
    orders tied fractional parts with `numpy.argsort`, whose **default sort is not
    stable**, so a different numpy could order equal keys differently and this
    agreement would evaporate with nothing being wrong. The fixture records the
    numpy version for that reason -- it is the axes rule applied to a dependency
    rather than to a parameter, and without the version the claim is not
    checkable later.
    """
    data = fixture()
    assert data["numpy_version"] == "2.5.2", (
        "The tie agreement below was measured on numpy 2.5.2. numpy's default "
        "sort is not stable, so on a different build this is an open question "
        "again, not a regression. Re-measure and restate rather than assuming."
    )
    for case in data["edge_cases"]:
        weights = [case["sizes"][k] for k in sorted(case["sizes"])]
        total = sum(weights)
        sds = [case["sds"][k] for k in sorted(case["sds"])]
        denominator = sum((w / total) * s for w, s in zip(weights, sds, strict=True))
        raw = tuple(
            case["n_total"] * ((w / total) * s) / denominator
            for w, s in zip(weights, sds, strict=True)
        )
        ours = list(largest_remainder(raw, case["n_total"]))
        assert ours == case["allocation"], f"{case['label']}: {ours} vs {case['allocation']}"


def test_the_sweep_agrees_across_its_whole_stated_space() -> None:
    """Agreement as a measurement with its space stated, not as three cases.

    The space is in the fixture's `sweep_space` and is repeated in the failure
    message, because an agreement figure that does not say what varied is the
    class C-30 records.
    """
    data = fixture()
    sweep = data["sweep"]
    assert len(sweep) == 2000

    disagreements = []
    for case in sweep:
        ours = ours_from_weights(case["W_h"], case["p_h"], case["n_total"], data["frame_total"])
        if ours != case["allocation"]:
            disagreements.append((case, ours))

    assert not disagreements, (
        f"{len(disagreements)} of {len(sweep)} designs disagree over "
        f"{data['sweep_space']} -- first: {disagreements[0]}"
    )


def test_where_the_two_implementations_diverge_we_refuse_rather_than_adjust() -> None:
    """The honest boundary, asserted rather than described.

    `svy` has two policies we do not: `min_n` floors a stratum up from a raw
    allocation below 1, and `cap_at_population` caps and redistributes when Neyman
    asks for more units than a stratum holds. **We refuse in both places** --
    `ALLOCATION_TOO_THIN` (Q2) and `ALLOCATION_IMPOSSIBLE`.

    So the two agree wherever both produce an *unconstrained* allocation, and part
    only where each applies its own constraint policy. That is a difference in
    what the tools do about a problem, not a difference in the estimator, and this
    test pins it so nobody later reads the 2000-case agreement as wider than it is.
    """
    from prevalence_kit.errors import Reason, Refusal
    from prevalence_kit.stratified import Rounding, allocate

    # svy floors this to [49, 1]; Neyman's raw for s1 is 0.001.
    with pytest.raises(Refusal) as thin:
        allocate(
            (Stratum("s0", 100_000, 0.25), Stratum("s1", 100, 1e-8)),
            50,
            Rounding.LARGEST_REMAINDER,
        )
    assert thin.value.reason is Reason.ALLOCATION_TOO_THIN

    # svy caps this to [10, 490]; Neyman wants more of s0 than s0 holds.
    with pytest.raises(Refusal) as impossible:
        allocate(
            (Stratum("s0", 10, 0.4899), Stratum("s1", 100_000, 1e-6)),
            500,
            Rounding.LARGEST_REMAINDER,
        )
    assert impossible.value.reason is Reason.ALLOCATION_IMPOSSIBLE


def test_the_narrowing_travels_with_the_fixture() -> None:
    """D-18's scope, kept in the artifact rather than only in prose.

    If someone later generates interval fixtures from `svy` and drops them beside
    this one, this fails and they have to read why first.
    """
    data = fixture()
    assert "same estimator" in data["narrowing"]
    assert "clopper-pearson" in data["narrowing"]
    assert set(data) >= {"shipped_fixtures", "edge_cases", "sweep"}
    assert "interval_fixtures" not in data, (
        "svy's intervals are all design-based -- it maps 'clopper-pearson' to "
        "'korn-graubard'. None of them witnesses ours, and a fixture claiming "
        "otherwise would need D-18 reopened first."
    )


# ------------------------------------------------- D2.10 / O-13: the divergence

WILSON_FIXTURE = Path(__file__).resolve().parents[1] / "svy" / "fixtures" / "wilson_divergence.json"


def wilson_fixture() -> dict[str, Any]:
    parsed: dict[str, Any] = json.loads(WILSON_FIXTURE.read_text(encoding="utf-8"))
    return parsed


def test_the_wilson_fixture_states_its_axes_and_its_versions() -> None:
    """O-13's figure is a measurement, so it carries what it was measured over.

    D-18 recorded that the builder's claim -- that the two "will not agree to 4
    significant digits at small n" -- was **a claim about magnitude the evidence
    did not carry**. This fixture is that evidence, and a divergence figure
    without its axes would repeat the error it exists to close.
    """
    data = wilson_fixture()
    assert data["obligation"] == "O-13"
    assert data["svy_version"] == "0.25.0"
    assert data["numpy_version"] and data["polars_version"]
    assert data["axes"]["n"] == [10, 20, 40, 80, 160, 500, 1000]
    assert data["axes"]["confidence"] == [0.90, 0.95, 0.99]
    assert "not a general property" in data["narrowing"]


def test_the_divergence_shrinks_with_n_and_is_largest_at_small_n() -> None:
    """O-13, measured. **123 interior cases, 0 < k < n**, three confidence levels.

    The worst endpoint difference is **0.117330** at `n = 10, k = 9, conf 0.99`,
    and it falls away fast: 0.0479 at n = 20, 0.0155 at n = 40, 9.7e-05 at
    n = 1000.

    **This is a measurement at these points, not a property of the two methods.**
    Quoting it as "svy's Wilson differs by about a tenth" would be the mistake the
    intervals half of D2.9 just spent itself proving.

    Boundary cases are excluded here and asserted separately below, because a
    worst case dominated by a degenerate interval describes the boundary rather
    than the method.
    """
    from prevalence_kit.estimators import wilson as ours

    data = wilson_fixture()
    worst_by_n: dict[int, float] = {}
    interior = 0
    for row in data["rows"]:
        if row["k"] in (0, row["n"]):
            continue
        interior += 1
        mine = ours(row["k"], row["n"], confidence=row["confidence"])
        gap = max(abs(float(mine.low) - row["low"]), abs(float(mine.high) - row["high"]))
        worst_by_n[row["n"]] = max(worst_by_n.get(row["n"], 0.0), gap)

    assert interior == 123
    assert worst_by_n[10] == pytest.approx(0.117330, abs=1e-6)
    assert worst_by_n[1000] == pytest.approx(0.000097, abs=1e-6)
    # Monotone decay in n, which is the shape of the claim rather than a point.
    sizes = sorted(worst_by_n)
    for smaller, larger in pairwise(sizes):
        assert worst_by_n[larger] < worst_by_n[smaller], (
            f"divergence grew from n={smaller} to n={larger}"
        )


def test_svy_returns_a_zero_width_interval_where_every_unit_is_positive() -> None:
    """The boundary, and it is a difference in kind rather than in magnitude.

    At `k == n` `svy`'s standard error is 0, so its effective sample size gives a
    **zero-width** interval: `[1.0, 1.0]`, claiming certainty from ten
    observations. Ours returns `[0.601146, 1.0]` at n = 10, conf 0.99.

    Recorded because this is the regime a rare-event tool meets from the other
    side, and because it explains the raw worst-case figure -- 0.398854 across all
    cases -- which is about this boundary and not about the method in general.
    """
    from prevalence_kit.estimators import wilson as ours

    data = wilson_fixture()
    boundary = [r for r in data["rows"] if r["k"] == r["n"]]
    assert boundary, "the fixture no longer covers k == n"
    assert all(r["high"] - r["low"] == 0.0 for r in boundary), (
        "svy no longer degenerates at k == n; re-measure before restating"
    )

    at_ten = next(r for r in boundary if r["n"] == 10 and r["confidence"] == pytest.approx(0.99))
    mine = ours(at_ten["k"], at_ten["n"], confidence=at_ten["confidence"])
    assert float(mine.high) - float(mine.low) > 0.39, "ours should still have width"


def test_svy_produces_no_interval_at_all_when_there_are_no_positives() -> None:
    """The other boundary, and the search behind the claim is recorded.

    `svy`'s `prop` returns one row per level **present in the data**, so at
    `k = 0` there is no `y_level == 1` row and no interval. **Two invocations were
    tried** -- a plain integer column, and a polars `Enum` declaring both levels --
    and neither produces one.

    Stated at the width of that search, per rule 9: this is what two routes did,
    not a claim that `svy` cannot do it at all.

    **It matters because `k = 0` is the most common honest result in rare-event
    Trust & Safety work** -- the same fact that struck `CORRECTION_DEGENERATE`.
    Our Wilson returns `[0, upper]` there.
    """
    from prevalence_kit.estimators import wilson as ours

    data = wilson_fixture()
    zero_rows = [r for r in data["rows"] if r["k"] == 0]
    assert not zero_rows, "svy now returns a k = 0 row; the fixture should carry it"

    failures = [f for f in data["failures"] if f["k"] == 0]
    assert len(failures) == 21
    assert all("y_level == 1" in f["error"] for f in failures)

    # Ours has an answer there, and it is the answer the tool exists to give.
    mine = ours(0, 4000, confidence=0.95)
    assert float(mine.low) == 0.0
    assert 0.0 < float(mine.high) < 0.01
