"""O-23 -- Q6's clamp disclosure reaches the artifact an outsider reads.

**D-32's three conditions.** Clamp both ends; **say so in the output**; keep the raw
bound in the ledger beside the clamped one. The estimator has carried all three
since D2.6 -- but nothing wrote them anywhere, because no Phase 2 estimator was
wired into `run.py`. O-29 wired the correction, so the ledger half started
happening; this file is the **report** half.

The director's words, recorded in D-32: *a silently clamped bound is a small lie in
the artifact an outsider reads.*
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from prevalence_kit import report as report_mod
from prevalence_kit.plan import Plan
from prevalence_kit.run import Workspace, do_estimate, do_ingest, do_plan, do_sample

FRAME_SIZE = 20_000

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
    "seed": "clamp-fixture",
    "interval": "clopper_pearson",
}


def run_chain(tmp_path: Path, positives: int, **over: Any) -> tuple[Workspace, Plan]:
    body = dict(BASE) | over
    (tmp_path / "frame.txt").write_text(
        "\n".join(f"item-{i:05d}" for i in range(FRAME_SIZE)), encoding="utf-8"
    )
    path = tmp_path / "plan.yaml"
    path.write_text(yaml.safe_dump(body, sort_keys=True), encoding="utf-8")
    plan = Plan.load(path)

    ws = Workspace(tmp_path / "run")
    do_plan(ws, plan)
    drawn = do_sample(ws, plan, tmp_path / "frame.txt")
    rows = ["item_id,toxicity,content"] + [
        f"{item},{'0.9' if i < positives else '0.1'},x" for i, item in enumerate(drawn)
    ]
    (tmp_path / "labels.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    do_ingest(ws, plan, tmp_path / "labels.csv")
    do_estimate(ws, plan)
    return ws, plan


def rendered(tmp_path: Path, positives: int, **over: Any) -> str:
    ws, plan = run_chain(tmp_path, positives, **over)
    md_path, _ = report_mod.emit(ws, plan)
    return md_path.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def clamped_run(tmp_path_factory: pytest.TempPathFactory) -> tuple[Workspace, str]:
    """The rare_event chain, built once: its workspace and its rendered report.

    The clamp needs `8 / 4000` at Se 0.90, Sp 0.999 -- that is the arithmetic
    which puts the raw lower bound below zero. Sealing 4000 items costs about
    3.6s, and it was being paid once per assertion.
    """
    path = tmp_path_factory.mktemp("clamped")
    ws, plan = run_chain(path, 8, sensitivity="0.90", specificity="0.999")
    md_path, _ = report_mod.emit(ws, plan)
    return ws, md_path.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def clamped_report(clamped_run: tuple[Workspace, str]) -> str:
    """The rare_event report, rendered once for every assertion about it.

    **Seven tests were each running the whole chain to read one string.** The
    clamp needs `8 / 4000` at Se 0.90, Sp 0.999 -- that is the arithmetic which
    puts the raw lower bound below zero -- but nothing about a rendered sentence
    needs the chain re-run to see it. Sealing 4000 items costs about 3.6s each
    time, and it was paid seven times for one report.
    """
    return clamped_run[1]


@pytest.fixture(scope="module")
def plain_report(tmp_path_factory: pytest.TempPathFactory) -> str:
    """The uncorrected control, rendered once and small.

    It asserts the ABSENCE of a correction line, which no amount of `n` makes
    truer. Sealing 4000 items for it cost 3.8s of setup and as much again in
    teardown -- Windows deleting 4000 sealed directories is not free.
    """
    return rendered(tmp_path_factory.mktemp("plain"), 4, sample_size=40)


def test_a_clamped_bound_is_disclosed_in_the_report(clamped_report: str) -> None:
    """D-32 condition 2, in the artifact rather than on the estimate.

    The `rare_event` case: 8 positives in 4000 at Se 0.90, Sp 0.999, whose raw
    lower bound is `-0.000151455949`. A reader seeing `[0, 0.327%]` has no way to
    know the zero is a **construction** unless the report says so.
    """
    text = clamped_report

    assert "construction, not a measurement" in text
    assert "-0.000151455949" in text, "the raw bound the arithmetic produced is not shown"
    assert "verify" in text, "the reader is not told the raw value is re-derivable"


def test_the_disclosure_sits_with_the_number_it_describes(clamped_report: str) -> None:
    """Placement is the point, not decoration.

    A footnote about a bound printed twenty lines earlier is a sentence the reader
    meets after they have already believed the interval.
    """
    lines = clamped_report.splitlines()
    interval_line = next(i for i, x in enumerate(lines) if "95% interval" in x)
    disclosure = next(i for i, x in enumerate(lines) if "construction" in x)

    assert disclosure - interval_line <= 5, "the disclosure drifted away from the interval"


def test_an_unclamped_interval_says_nothing(tmp_path: Path) -> None:
    """The positive control, and it matters more than it looks.

    A disclosure printed on every report is a disclosure nobody reads. This one
    appears only when a bound was actually changed.
    """
    # A small run on purpose: "nothing was clamped" is not a property of n, and
    # sealing 4000 items to assert the absence of a sentence is 3.6s for nothing.
    text = rendered(tmp_path, 10, sample_size=40, sensitivity="0.99", specificity="0.99")

    assert "construction, not a measurement" not in text


def test_the_report_names_the_correction_and_the_apparent_prevalence(
    clamped_report: str,
) -> None:
    """A corrected number is not comparable to an uncorrected one without saying so.

    An auditor reading 0.111% needs to know it is corrected, from which Se/Sp, and
    what the uncorrected figure was -- otherwise they cannot tell whether the
    correction or the sample moved it.
    """
    text = clamped_report

    assert "Corrected for label quality" in text
    assert "sensitivity 0.900000000000" in text
    assert "specificity 0.999000000000" in text
    assert "0.200%" in text, "the uncorrected apparent prevalence is not shown"


def test_an_uncorrected_report_does_not_claim_a_correction(plain_report: str) -> None:
    """The control for the line above."""
    assert "Corrected for label quality" not in plain_report


def test_the_raw_bound_is_in_the_ledger_as_well_as_the_report(
    clamped_run: tuple[Workspace, str],
) -> None:
    """D-32 condition 3. Two artifacts, and the report is not the record.

    `verify` re-derives from the ledger, so the raw bound has to be there
    independently of anything the renderer chooses to print.
    """
    estimate = clamped_run[0].read_json("estimate.json")

    assert estimate["low_raw"] == "-0.000151455949"
    assert estimate["clamped"] == ["low"]


def test_the_report_survives_verify(tmp_path: Path) -> None:
    """Emitting a report must not break the chain it describes.

    `report` may repeat and each emission appends its own entry -- D-17's
    exemption -- so this is the check that the disclosure work did not disturb
    that.

    **Deliberately a small run.** `verify` re-unseals every sealed item, which is
    linear in `n` at about 13.7 ms each: this test used the 4000-item clamp
    fixture and cost **55 seconds on its own**, a quarter of the suite, to prove
    a property that has nothing to do with `n`. The clamp arithmetic lives in the
    tests that need it; this one needs a chain, and any chain will do.
    """
    from prevalence_kit.verify import verify_run

    ws, plan = run_chain(tmp_path, 4, sample_size=40)
    report_mod.emit(ws, plan)

    checks = verify_run(ws)
    assert all(c.ok for c in checks)


@pytest.mark.parametrize("ascii_only", [True])
def test_the_disclosure_is_plain_ascii(clamped_report: str, ascii_only: bool) -> None:
    """R2.8 and the charter's writing rule. `emit` refuses non-ASCII, so this
    would already fail loudly -- it is here so the reason is named."""
    assert clamped_report.isascii()
