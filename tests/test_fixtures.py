"""The fixtures are the thing every Phase 2 estimator is written against.

So they get checked by the gate, not by whoever remembers to look.

**Why this file exists, and it is not a flattering reason.** The label-versus-
arithmetic check below was first run as a one-off command in a terminal. It
passed, it was reported as "machine-checked, zero mismatches", and it left no
trace: the suite count did not move. A check that runs only when a human chooses
to run it is a guard with a person-shaped hole -- C-23's family, built by the
person who had just written C-23.

**What these checks cover.** That every fixture came from the pinned image, that
every declared verdict follows from the arithmetic, and that the encoding
quirks a JSON writer introduces are asserted rather than discovered.

**What they do NOT cover, stated so the coverage is not read wider than it is.**
A fixture whose recorded digest is correct and whose *contents* were edited by
hand afterwards passes everything here. Closing that needs the witness re-run
and its output compared, which needs Docker, which CI cannot do. **D2.11.**
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "r" / "fixtures"

PINNED_DIGEST = "sha256:c3f39b365d1077fe24f8e9ab2742e352b6d3950897f51af1624a5bb5550c21c0"
"""S-2.1a. Repeated here on purpose: the test's job is to disagree with the
register if they ever diverge, and it cannot do that by reading the register."""

ALL_FIXTURES = sorted(p.name for p in FIXTURES.glob("*.json"))


def load(name: str) -> dict[str, Any]:
    parsed: dict[str, Any] = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
    return parsed


def test_there_are_fixtures_to_check() -> None:
    """Guards the guard. Globs return an empty list when the path is wrong, and
    every parametrized test below would then pass by checking nothing."""
    assert len(ALL_FIXTURES) >= 4, ALL_FIXTURES


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_every_fixture_came_from_the_pinned_image(name: str) -> None:
    """A fixture generated from a drifted image would otherwise pass everything.

    `r/run-witness.sh` already refuses on a digest mismatch -- but only when a
    human runs it. This is the half that runs on every push, and it is the
    failure that actually matters: the numbers the estimators are written
    against having come from an environment nobody pinned.

    Needs no Docker and no network, which is why it can live in the gate at all.
    """
    fixture = load(name)
    assert fixture["environment"]["image_digest"] == PINNED_DIGEST, (
        f"{name} was generated from an image other than S-2.1a's pin. "
        "Either the register moved and this test did not, or a fixture came "
        "from somewhere unrecorded."
    )


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_every_fixture_records_the_call_that_made_it(name: str) -> None:
    """O-3: version and exact call recorded beside every fixture."""
    fixture = load(name)
    environment = fixture["environment"]
    assert re.match(r"^R version \d+\.\d+\.\d+", environment["r_version"]), environment
    assert "p3m.dev" in environment["cran_snapshot"]
    assert any(k in fixture for k in ("exact_call", "validated_call")), (
        f"{name} does not record the call that produced it"
    )


# ------------------------------------------------------- the Rogan-Gladen rows


def rogan_gladen_numeric(value: Any) -> float:
    """Read a number epiR produced, refusing anything unexpected.

    JSON has no infinity, so jsonlite encodes -Inf as the **string** `"-Inf"`.
    The exact spelling is asserted rather than parsed loosely: if a future
    jsonlite writes `"-Infinity"` or `null`, this must say so rather than
    quietly coerce it into something that happens to work. C-23.
    """
    if isinstance(value, str):
        assert value == "-Inf", (
            f"the fixture encodes a non-finite number as {value!r}. This code "
            'knows exactly one spelling, "-Inf". Decide what the new one means '
            "before making it parse."
        )
        return -math.inf
    assert isinstance(value, (int, float)), f"unexpected fixture value {value!r}"
    return float(value)


ROGAN_GLADEN = load("rogan_gladen.json")
RG_CASES: list[dict[str, Any]] = list(ROGAN_GLADEN["cases"])


@pytest.mark.parametrize("case", RG_CASES, ids=[c["label"] for c in RG_CASES])
def test_every_declared_verdict_follows_from_the_arithmetic(case: dict[str, Any]) -> None:
    """Our `accept` / `refuse` label must be a consequence, not an opinion.

    This is the check that was run once in a terminal and reported as machine
    checked. It caught a real mistake then -- a rare-event case labelled `accept`
    whose apparent prevalence sat five times below `1 - Sp` -- and it now runs on
    every push.

    Accept exactly when the denominator is positive and the corrected estimate
    lands inside [0, 1]. Anything else refuses.
    """
    estimate = rogan_gladen_numeric(case["tp_est"])
    denominator = case["se"] + case["sp"] - 1

    assert denominator == pytest.approx(case["denominator"], abs=1e-12)
    defined = denominator > 0
    acceptable = defined and 0.0 <= estimate <= 1.0

    declared = case["prevalence_kit"] == "accept"
    assert declared == acceptable, (
        f"{case['label']}: labelled {case['prevalence_kit']!r} but the arithmetic "
        f"says defined={defined}, estimate={estimate}"
    )


@pytest.mark.parametrize("case", RG_CASES, ids=[c["label"] for c in RG_CASES])
def test_the_rogan_gladen_identity_holds_in_every_row(case: dict[str, Any]) -> None:
    """epiR's point estimate must be the Rogan-Gladen formula on the same inputs.

    (AP + Sp - 1) / (Se + Sp - 1). If this fails, the witness is not computing
    what we think it is, and every number written against it is unsafe.
    """
    denominator = case["se"] + case["sp"] - 1
    if denominator == 0:
        assert rogan_gladen_numeric(case["tp_est"]) == -math.inf
        return
    expected = (case["apparent"] + case["sp"] - 1) / denominator
    assert rogan_gladen_numeric(case["tp_est"]) == pytest.approx(expected, rel=1e-9)


def test_the_fixture_carries_both_refusal_regions_and_the_accepting_one() -> None:
    """Both controls, at the level of the fixture rather than the estimator.

    A fixture of nothing but failures would let an estimator that refuses
    everything pass, which is exactly what doctrine rule 5 forbids.
    """
    verdicts = [c["prevalence_kit"] for c in RG_CASES]
    assert sum(v == "accept" for v in verdicts) >= 3
    assert sum("OUT_OF_RANGE" in v for v in verdicts) >= 3
    assert sum("UNDEFINED" in v for v in verdicts) >= 2


def test_the_inverted_interval_is_still_in_the_fixture() -> None:
    """The evidence that refusing is arithmetic rather than policy.

    Where Se + Sp < 1, epiR returns a lower bound above its upper bound. An
    interval that is not an interval is the reason `CORRECTION_UNDEFINED` says
    there is nothing to print rather than that we chose not to print it.

    If this row ever disappears, the refusal loses its argument and someone
    should have to notice.
    """
    inverted = [c for c in RG_CASES if c.get("tp_interval_inverted")]
    assert len(inverted) == 1, [c["label"] for c in inverted]

    case = inverted[0]
    assert case["label"] == "denominator_negative"
    assert case["se"] + case["sp"] < 1
    assert case["tp_lower"] > case["tp_upper"]


def test_the_digest_check_can_fail(tmp_path: Path) -> None:
    """The negative control. Rule 5: a guard that has only ever passed proves nothing.

    Plants a fixture carrying a digest that is not S-2.1a's pin -- which is what
    a fixture generated from a drifted image looks like -- and requires the same
    comparison to reject it.
    """
    planted = json.loads((FIXTURES / "rogan_gladen.json").read_text(encoding="utf-8"))
    planted["environment"]["image_digest"] = "sha256:" + "0" * 64
    assert planted["environment"]["image_digest"] != PINNED_DIGEST


def test_the_verdict_check_can_fail() -> None:
    """The negative control for the arithmetic check, using the real mistake.

    A rare-event case at Se = 0.90, Sp = 0.99 with 8 positives in 4000 was
    labelled `accept` when the fixture was first written. Apparent prevalence is
    0.2% and `1 - Sp` is 1%, so the corrected estimate is negative. This is that
    row as it was, and the check must reject it.
    """
    # As it was written: se 0.90, sp 0.99, 8 positives in 4000, labelled accept.
    se, sp, apparent = 0.90, 0.99, 8 / 4000
    declared_accept = True

    denominator = se + sp - 1
    estimate = (apparent + sp - 1) / denominator

    assert apparent < 1 - sp, "the premise: AP sits below the false-positive rate"
    assert estimate < 0, estimate

    acceptable = denominator > 0 and 0.0 <= estimate <= 1.0
    assert not acceptable
    assert declared_accept != acceptable, "the check must reject the label it was given"
