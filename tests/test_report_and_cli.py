"""The report emitter and the command line -- the surface E1-E15 runs against.

R7: the Honest Limits block is mandatory. `emit-report` cannot produce a report
without it, and the block carries the charter's section 8 wording rather than a
paraphrase, so a reader of the report gets the same caveats as a reader of the
repository.

Exit codes are the contract here, because that is what the director's checklist
reads: 0 success, 2 a Refusal with its reason code printed first, 1 a bug in
this tool. Two non-zero codes for two different situations, so an operator does
not debug the wrong thing.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from prevalence_kit import report as report_mod
from prevalence_kit.errors import Reason, Refusal
from prevalence_kit.plan import Plan
from prevalence_kit.run import Workspace, do_plan, do_sample
from prevalence_kit.verify import verify_run
from tests.conftest import PLAN_YAML, POSITIVES, write_labels

CLI = [sys.executable, "-m", "prevalence_kit.cli"]


# ------------------------------------------------------------------- report


def test_the_report_carries_every_honest_limit(run: Workspace, plan: Plan) -> None:
    """R7. Not a footer -- a deliverable, asserted verbatim.

    Paraphrasing would let the limits drift away from the charter one edit at a
    time, which is exactly how a caveat stops meaning what it meant.
    """
    markdown, _ = report_mod.emit(run, plan)
    text = markdown.read_text(encoding="utf-8")
    for limit in report_mod.HONEST_LIMITS:
        assert limit in text, limit[:60]


def test_the_report_carries_the_youtube_caveat_verbatim(run: Workspace, plan: Plan) -> None:
    """The one limit that is quoted from an outside source, so it must be exact."""
    markdown, _ = report_mod.emit(run, plan)
    assert (
        "The confidence intervals do not take into account rater quality, "
        "which may impact our measurements." in markdown.read_text(encoding="utf-8")
    )


def test_the_report_says_no_regulation_requires_the_number(run: Workspace, plan: Plan) -> None:
    """D-5. The claim the vision got wrong now travels with every report."""
    text = report_mod.emit(run, plan)[0].read_text(encoding="utf-8")
    assert "No EU regulation requires this number" in text


def test_the_report_carries_the_number_the_record_holds(run: Workspace, plan: Plan) -> None:
    _, as_json = report_mod.emit(run, plan)
    report = json.loads(as_json.read_text(encoding="utf-8"))
    recorded = json.loads((run.root / "estimate.json").read_text(encoding="utf-8"))
    assert report["estimate"] == recorded
    assert report["estimate"]["positives"] == POSITIVES


def test_the_report_shows_every_link_in_the_chain(run: Workspace, plan: Plan) -> None:
    _, as_json = report_mod.emit(run, plan)
    report = json.loads(as_json.read_text(encoding="utf-8"))
    assert [link["step"] for link in report["chain"]] == [
        "plan",
        "sample",
        "ingest-labels",
        "estimate",
    ]


def test_the_report_shows_both_frame_counts(run: Workspace, plan: Plan) -> None:
    """V-7 reaches the operator, not just the ledger."""
    _, as_json = report_mod.emit(run, plan)
    report = json.loads(as_json.read_text(encoding="utf-8"))
    assert report["frame_rows_read"] is not None
    assert report["frame_unique_ids"] is not None


def test_the_report_never_contains_content(run: Workspace, plan: Plan) -> None:
    """R4 again, at the surface. A report is the thing most likely to be shared."""
    markdown, as_json = report_mod.emit(run, plan)
    for path in (markdown, as_json):
        assert "SENTINEL-CONTENT-" not in path.read_text(encoding="utf-8")


def test_the_report_is_plain_ascii(run: Workspace, plan: Plan) -> None:
    markdown, _ = report_mod.emit(run, plan)
    text = markdown.read_text(encoding="utf-8")
    assert all(ord(c) < 128 for c in text)


def test_a_non_ascii_report_is_refused() -> None:
    """The guard's negative control. Reports are where em-dashes get typed."""
    with pytest.raises(Refusal) as exc:
        report_mod._refuse_non_ascii("a report with an em-dash — in it")
    assert exc.value.reason is Reason.PLAN_INVALID


def test_a_report_cannot_be_emitted_without_an_estimate(
    tmp_path: Path, plan: Plan, frame_path: Path
) -> None:
    ws = Workspace(tmp_path / "run")
    do_plan(ws, plan)
    do_sample(ws, plan, frame_path)

    with pytest.raises(Refusal) as exc:
        report_mod.emit(ws, plan)
    assert exc.value.reason is Reason.LEDGER_BROKEN


def test_emitting_twice_is_allowed_and_verify_still_passes(
    run: Workspace, plan: Plan, plan_path: Path
) -> None:
    """D-17's report exemption, end to end.

    Re-emitting cannot change the number, and each emission appends its own
    entry. If linearity were applied to `report` this would refuse.
    """
    report_mod.emit(run, plan, stem="first")
    report_mod.emit(run, plan, stem="second")

    steps = [e.step for e in run.ledger.verify()]
    assert steps.count("report") == 2
    assert all(c.ok for c in verify_run(run, plan_path))


def test_the_second_report_records_the_first(run: Workspace, plan: Plan) -> None:
    """An auditor wants the emission history, which is why repeats are allowed."""
    report_mod.emit(run, plan, stem="first")
    _, as_json = report_mod.emit(run, plan, stem="second")
    report = json.loads(as_json.read_text(encoding="utf-8"))
    assert [link["step"] for link in report["chain"]].count("report") == 1


# ---------------------------------------------------------------------- CLI


def build_inputs(tmp_path: Path) -> tuple[Path, Path]:
    plan_path = tmp_path / "plan.yaml"
    plan_path.write_text(yaml.safe_dump(PLAN_YAML, sort_keys=True), encoding="utf-8")
    frame = tmp_path / "frame.txt"
    frame.write_text("\n".join(f"item-{i:04d}" for i in range(200)), encoding="utf-8")
    return plan_path, frame


def cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([*CLI, *args], capture_output=True, text=True, check=False)


def test_the_whole_chain_exits_zero(tmp_path: Path) -> None:
    """E1 / E3 / E5, as the checklist runs them."""
    plan_path, frame = build_inputs(tmp_path)
    run_dir = tmp_path / "run"

    assert cli("plan", str(plan_path), "--run", str(run_dir)).returncode == 0
    assert cli("sample", str(plan_path), str(frame), "--run", str(run_dir)).returncode == 0

    drawn = json.loads((run_dir / "sample.json").read_text(encoding="utf-8"))["item_ids"]
    labels = write_labels(tmp_path, drawn, positives=POSITIVES)

    assert cli("ingest-labels", str(plan_path), str(labels), "--run", str(run_dir)).returncode == 0
    assert cli("estimate", str(plan_path), "--run", str(run_dir)).returncode == 0
    assert cli("emit-report", str(plan_path), "--run", str(run_dir)).returncode == 0

    done = cli("verify", "--run", str(run_dir), "--plan", str(plan_path))
    assert done.returncode == 0
    assert "nothing out of place" in done.stdout


def test_a_refusal_exits_two_and_names_the_code_first(tmp_path: Path) -> None:
    """E7. The reason code is the first line, so `| head -1` is useful."""
    plan_path, frame = build_inputs(tmp_path)
    run_dir = tmp_path / "run"
    cli("plan", str(plan_path), "--run", str(run_dir))
    cli("sample", str(plan_path), str(frame), "--run", str(run_dir))

    ledger = run_dir / "ledger.jsonl"
    ledger.write_text(
        ledger.read_text(encoding="utf-8").replace('"n":40', '"n":41', 1),
        encoding="utf-8",
        newline="\n",
    )

    result = cli("verify", "--run", str(run_dir), "--plan", str(plan_path))
    assert result.returncode == 2
    assert result.stderr.splitlines()[0] == "REFUSED [LEDGER_BROKEN]"


def test_replanning_through_the_cli_refuses(tmp_path: Path) -> None:
    """E8d at the surface."""
    plan_path, _ = build_inputs(tmp_path)
    run_dir = tmp_path / "run"
    assert cli("plan", str(plan_path), "--run", str(run_dir)).returncode == 0

    again = cli("plan", str(plan_path), "--run", str(run_dir))
    assert again.returncode == 2
    assert "RUN_ALREADY_OPEN" in again.stderr


def test_refusal_and_bug_have_different_exit_codes() -> None:
    """A tool returning one non-zero for both makes the operator debug the wrong thing."""
    from prevalence_kit.cli import EXIT_BUG, EXIT_OK, EXIT_REFUSED

    assert len({EXIT_OK, EXIT_BUG, EXIT_REFUSED}) == 3


def test_help_lists_exactly_the_six_verbs() -> None:
    """The charter caps v1.0 at six. This is the cap, asserted."""
    result = cli("--help")
    assert result.returncode == 0
    listed = {
        line.split()[0]
        for line in result.stdout.splitlines()
        if line.startswith("  ") and line.strip() and not line.startswith("   ")
    }
    assert {"plan", "sample", "ingest-labels", "estimate", "verify", "emit-report"} <= listed


def test_every_command_prints_ascii_only(tmp_path: Path) -> None:
    build_inputs(tmp_path)
    for args in (("--help",), ("plan", "--help"), ("verify", "--help")):
        result = cli(*args)
        assert all(ord(c) < 128 for c in result.stdout), args


# --------------------------------------------- the shipped example, C-15 / D-23


def test_the_shipped_example_has_a_multi_chunk_item() -> None:
    """C-15. E9c cannot be performed without one, and it regressed once already.

    F-4 was fixed in `tests/conftest.py`; `examples/synthetic/` was created
    afterwards from a demo run and had none. The defect came back in a new
    artifact while its closing test went on passing -- the class D-23 names.

    `tools/check_claims.py`'s `fixtures` check asserts the same property, so this
    is belt and braces on purpose: the checker guards the repository, this guards
    the suite that the checker's own findings row points at.
    """
    import csv

    from prevalence_kit.run import _wide_csv_fields
    from prevalence_kit.seal import CHUNK_BYTES

    labels = Path(__file__).resolve().parents[1] / "examples" / "synthetic" / "labels.csv"
    with labels.open(newline="", encoding="utf-8") as fh, _wide_csv_fields():
        rows = list(csv.DictReader(fh))

    multi = [r for r in rows if len(r["content"].encode("utf-8")) > CHUNK_BYTES]
    assert multi, "the shipped example needs one multi-chunk item or E9c cannot be run"
    assert len(rows) == 40


def test_a_missing_run_directory_is_not_a_broken_ledger(tmp_path: Path) -> None:
    """D-22's rule applied: the artifact to open is the path, not the ledger.

    `verify --run <nonexistent>` used to say "The ledger is empty; there is
    nothing to verify", sending the operator to inspect a file that is not there.
    """
    result = cli("verify", "--run", str(tmp_path / "no-such-run"))
    assert result.returncode == 2
    assert result.stderr.splitlines()[0] == "REFUSED [RUN_NOT_FOUND]"


def test_an_empty_run_directory_still_says_ledger(tmp_path: Path) -> None:
    """The other side of the split: the directory exists, the ledger does not."""
    empty = tmp_path / "empty-run"
    empty.mkdir()
    result = cli("verify", "--run", str(empty))
    assert result.returncode == 2
    assert result.stderr.splitlines()[0] == "REFUSED [LEDGER_BROKEN]"
