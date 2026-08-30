"""D2.16 -- `stratallo` fixtures. **Fixture only. No estimator is built from this.**

S-1.12. `stratallo` 3.0.1 is inside the pinned CRAN snapshot already, so it costs
no new pin and no network call the witness image does not already make. It is the
third *no witness exists* claim this project made and got wrong.

**It witnesses one of the two things it was expected to, and the one it witnesses
is the one that had nothing.**

`round_oric` is the **first witness from R** that D-30's largest-remainder
rounding has ever had. `survey` has **no allocator at all** -- that is F-9, the
sixth instrument-limit kind, a fixture that looks external and is not. `svy` gave
the rounding its first witness of any kind at D2.9; this is the second, in a
different language by different authors.

`var_stsi` **does not** witness our stratified variance, and that is recorded as a
boundary rather than chased as a gap. See the test.

**The narrowing travels with it, in `epiR`'s words.** `stratallo` is the algorithm
authors' own implementation of their own papers: it confirms we compute what they
compute, and it does **not** independently confirm the method. Barnett Table 2B is
a different kind of evidence and this is not that.
"""

from __future__ import annotations

import json
from math import sqrt
from pathlib import Path
from typing import Any

import pytest

from prevalence_kit.stratified import largest_remainder

FIXTURE = Path(__file__).resolve().parents[1] / "r" / "fixtures" / "stratallo.json"


def fixture() -> dict[str, Any]:
    parsed: dict[str, Any] = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return parsed


def as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, list) else [value]


def test_the_fixture_records_its_environment_and_its_narrowing() -> None:
    """O-3's rule, and the narrowing kept in the artifact rather than only in prose."""
    data = fixture()
    assert data["deliverable"] == "D2.16"
    assert data["fixture_only"] is True
    assert data["environment"]["stratallo_version"] == "3.0.1"
    assert "2026-04-23" in data["environment"]["cran_snapshot"]
    assert "does NOT" in data["narrowing"]
    assert "round_oric" in data["exact_call"]
    # The digest is the pin that makes this reproducible by a stranger.
    # tests/test_fixtures.py asserts it against the register; this asserts the
    # fixture carries it at all, which it did not on the first attempt.
    assert data["environment"]["image_digest"].startswith("sha256:")


@pytest.mark.parametrize(
    "label", ["barnett_neyman_4000", "two_stratum_neyman_1000", "rare_event_neyman_5000"]
)
def test_stratallo_reproduces_our_rounding_on_every_shipped_fixture(label: str) -> None:
    """The half that had no witness, on the three allocations this project ships.

    `rare_event_neyman_5000` is the one that matters: its floors sum to 4999, which
    is what forced **Q4 / D-30**. `stratallo` hands the remainder to the same
    stratum, and `barnett_neyman_4000` reproduces the **published** figures
    `2098 / 828 / 584 / 256 / 234`.
    """
    case = next(f for f in fixture()["fixtures"] if f["label"] == label)
    ours = list(largest_remainder(tuple(as_list(case["raw"])), case["n_total"]))

    assert ours == as_list(case["round_oric"])
    assert sum(ours) == case["n_total"]


def test_the_rounding_sweep_agrees_across_its_whole_stated_space() -> None:
    """Agreement as a measurement with its space stated, not as three cases."""
    data = fixture()
    sweep = data["sweep"]
    assert len(sweep) == 2000

    disagreements = [
        case
        for case in sweep
        if list(largest_remainder(tuple(as_list(case["raw"])), case["n_total"]))
        != as_list(case["round_oric"])
    ]
    assert not disagreements, (
        f"{len(disagreements)} of {len(sweep)} disagree over {data['sweep_space']}"
    )


def test_stratallo_variance_is_a_different_estimator_from_ours() -> None:
    """**The boundary, asserted rather than described** -- and it is the fourth
    time a same-named function turned out to be a different estimator.

    `var_stsi` computes the **without-replacement** variance of the **total**.
    Ours is the **with-replacement** variance of the **mean**, with no
    finite-population correction, which is **S-2.3**'s specification and what
    reproduces Barnett Table 2B.

    After dividing out the `N^2` scaling the two are still different: `stratallo`
    matches the fpc form exactly and ours does not, by construction. So **this
    fixture witnesses the rounding and not the variance**, and the difference is
    about the design each assumes rather than about the arithmetic.

    Not a gap to close. Adopting the fpc form would move every interval this tool
    prints and would break the anchor that validates it. Recorded so nobody later
    reads `var_stsi` as a second opinion on `stratified_estimate`.
    """
    for case in fixture()["fixtures"]:
        sizes = as_list(case["N_h"])
        units = as_list(case["round_oric"])
        spreads = [sqrt(p * (1 - p)) for p in as_list(case["p_h"])]
        total = sum(sizes)

        with_replacement = sum(
            (n / total) ** 2 * s * s / u for n, s, u in zip(sizes, spreads, units, strict=True)
        )
        with_fpc = sum(
            (n / total) ** 2 * s * s / u * (1 - u / n)
            for n, s, u in zip(sizes, spreads, units, strict=True)
        )
        theirs = case["var_stsi"] / total**2

        assert theirs == pytest.approx(with_fpc, rel=1e-12), (
            "stratallo no longer matches the without-replacement form"
        )
        assert theirs != pytest.approx(with_replacement, rel=1e-12), (
            "the two forms have converged, so this test no longer distinguishes them"
        )


def test_the_size_of_that_difference_is_recorded_not_waved_away() -> None:
    """A limit stated as a sentence is a shrug; stated as a number it is weighable.

    Our standard error is larger than `stratallo`'s by **0.18% to 0.43%** on the
    three shipped fixtures -- the price of the with-replacement assumption, which
    is conservative in the direction this project already chose.
    """
    gaps = []
    for case in fixture()["fixtures"]:
        sizes = as_list(case["N_h"])
        units = as_list(case["round_oric"])
        spreads = [sqrt(p * (1 - p)) for p in as_list(case["p_h"])]
        total = sum(sizes)
        wr = sum(
            (n / total) ** 2 * s * s / u for n, s, u in zip(sizes, spreads, units, strict=True)
        )
        wor = sum(
            (n / total) ** 2 * s * s / u * (1 - u / n)
            for n, s, u in zip(sizes, spreads, units, strict=True)
        )
        gaps.append((wr / wor) ** 0.5 - 1)

    assert max(gaps) < 0.005, "the with-replacement premium grew past half a percent"
    assert min(gaps) > 0.0, "our SE should be the larger one -- we take no fpc credit"
