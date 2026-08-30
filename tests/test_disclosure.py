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


def test_a_clamped_bound_is_disclosed_in_the_report(tmp_path: Path) -> None:
    """D-32 condition 2, in the artifact rather than on the estimate.

    The `rare_event` case: 8 positives in 4000 at Se 0.90, Sp 0.999, whose raw
    lower bound is `-0.000151455949`. A reader seeing `[0, 0.327%]` has no way to
    know the zero is a **construction** unless the report says so.
    """
    text = rendered(tmp_path, 8, sensitivity="0.90", specificity="0.999")

    assert "construction, not a measurement" in text
    assert "-0.000151455949" in text, "the raw bound the arithmetic produced is not shown"
    assert "verify" in text, "the reader is not told the raw value is re-derivable"


def test_the_disclosure_sits_with_the_number_it_describes(tmp_path: Path) -> None:
    """Placement is the point, not decoration.

    A footnote about a bound printed twenty lines earlier is a sentence the reader
    meets after they have already believed the interval.
    """
    lines = rendered(tmp_path, 8, sensitivity="0.90", specificity="0.999").splitlines()
    interval_line = next(i for i, x in enumerate(lines) if "95% interval" in x)
    disclosure = next(i for i, x in enumerate(lines) if "construction" in x)

    assert disclosure - interval_line <= 5, "the disclosure drifted away from the interval"


def test_an_unclamped_interval_says_nothing(tmp_path: Path) -> None:
    """The positive control, and it matters more than it looks.

    A disclosure printed on every report is a disclosure nobody reads. This one
    appears only when a bound was actually changed.
    """
    text = rendered(tmp_path, 400, sensitivity="0.99", specificity="0.99")

    assert "construction, not a measurement" not in text


def test_the_report_names_the_correction_and_the_apparent_prevalence(
    tmp_path: Path,
) -> None:
    """A corrected number is not comparable to an uncorrected one without saying so.

    An auditor reading 0.111% needs to know it is corrected, from which Se/Sp, and
    what the uncorrected figure was -- otherwise they cannot tell whether the
    correction or the sample moved it.
    """
    text = rendered(tmp_path, 8, sensitivity="0.90", specificity="0.999")

    assert "Corrected for label quality" in text
    assert "sensitivity 0.900000000000" in text
    assert "specificity 0.999000000000" in text
    assert "0.200%" in text, "the uncorrected apparent prevalence is not shown"


def test_an_uncorrected_report_does_not_claim_a_correction(tmp_path: Path) -> None:
    """The control for the line above."""
    assert "Corrected for label quality" not in rendered(tmp_path, 8)


def test_the_raw_bound_is_in_the_ledger_as_well_as_the_report(tmp_path: Path) -> None:
    """D-32 condition 3. Two artifacts, and the report is not the record.

    `verify` re-derives from the ledger, so the raw bound has to be there
    independently of anything the renderer chooses to print.
    """
    ws, _plan = run_chain(tmp_path, 8, sensitivity="0.90", specificity="0.999")
    estimate = ws.read_json("estimate.json")

    assert estimate["low_raw"] == "-0.000151455949"
    assert estimate["clamped"] == ["low"]


def test_the_report_survives_verify(tmp_path: Path) -> None:
    """Emitting a report must not break the chain it describes.

    `report` may repeat and each emission appends its own entry -- D-17's
    exemption -- so this is the check that the disclosure work did not disturb
    that.
    """
    from prevalence_kit.verify import verify_run

    ws, plan = run_chain(tmp_path, 8, sensitivity="0.90", specificity="0.999")
    report_mod.emit(ws, plan)

    checks = verify_run(ws)
    assert all(c.ok for c in checks)


@pytest.mark.parametrize("ascii_only", [True])
def test_the_disclosure_is_plain_ascii(tmp_path: Path, ascii_only: bool) -> None:
    """R2.8 and the charter's writing rule. `emit` refuses non-ASCII, so this
    would already fail loudly -- it is here so the reason is named."""
    text = rendered(tmp_path, 8, sensitivity="0.90", specificity="0.999")
    assert text.isascii()
