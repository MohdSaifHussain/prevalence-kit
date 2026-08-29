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
    """D-30 condition 2 said the tie-break must be deterministic and stated.

    It did not say another implementation would agree, and nothing required that.
    `svy` sorts fractional parts with numpy, whose default sort is not stable, so
    this could have gone either way. It agrees, and that is a measurement rather
    than a property -- stated at the width of the two cases in the fixture.
    """
    data = fixture()
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
