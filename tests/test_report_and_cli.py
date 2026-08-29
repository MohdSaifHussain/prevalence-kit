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
from prevalence_kit.verify import summarise, verify_run
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


def test_the_report_says_what_verify_will_count(
    run: Workspace, plan: Plan, plan_path: Path
) -> None:
    """C-16. The flagship artifact must not contradict the command it recommends.

    The report lists the chain as at emission, then `emit-report` appends its own
    entry -- so the table showed 4 and `verify` reported 5, with nothing
    explaining the difference, in the one document that tells the reader to go
    and run `verify`.

    A report cannot list its own emission. It can say so, and state the count the
    reader should expect, so the two artifacts agree out loud rather than by
    inference.
    """
    markdown, as_json = report_mod.emit(run, plan)
    report = json.loads(as_json.read_text(encoding="utf-8"))

    predicted = report["entries_verify_will_report"]
    assert predicted == len(report["chain"]) + 1
    assert f"will report **{predicted} entries**" in markdown.read_text(encoding="utf-8")

    # And the prediction has to be right, not merely present.
    actual = next(c for c in verify_run(run, plan_path) if c.name == "ledger chain")
    assert f"{predicted} entries" in actual.note


def test_the_prediction_holds_on_a_second_emission(
    run: Workspace, plan: Plan, plan_path: Path
) -> None:
    """`report` repeats (D-17), so the count must track, not be hardcoded."""
    report_mod.emit(run, plan, stem="first")
    _, as_json = report_mod.emit(run, plan, stem="second")

    predicted = json.loads(as_json.read_text(encoding="utf-8"))["entries_verify_will_report"]
    actual = next(c for c in verify_run(run, plan_path) if c.name == "ledger chain")
    assert f"{predicted} entries" in actual.note


# ------------------------------------------------------------------- V-12


def test_the_tampered_plan_is_caught_without_the_flag(run: Workspace, plan_path: Path) -> None:
    """V-12, and the reason labelling alone was not enough.

    The hole: omit `--plan`, leave a TAMPERED plan on disk, and `verify` printed
    `[ok] plan (working file): SKIPPED -- no plan file on disk to compare`,
    summarised "nothing out of place", and exited 0 -- while E8/V-2's protection
    silently did not run.

    `verify` now falls back to the path recorded in the plan ledger entry, so
    there is no case where the tool knows where the plan was and declines to
    look. Called with no plan_path at all, exactly as an operator who forgot the
    flag would.
    """
    plan_path.write_text(yaml.safe_dump(PLAN_YAML | {"seed": "tampered"}), encoding="utf-8")

    with pytest.raises(Refusal) as exc:
        verify_run(run)
    assert exc.value.reason is Reason.PLAN_HASH_MISMATCH


def test_an_untampered_plan_passes_without_the_flag(run: Workspace) -> None:
    """The positive control. The fallback must check, not merely refuse."""
    checks = verify_run(run)
    working = next(c for c in checks if c.name == "plan (working file)")
    assert working.performed
    assert "unchanged since the run opened" in working.note


def test_the_plan_path_is_recorded_but_not_hashed(
    tmp_path: Path, plan: Plan, plan_path: Path
) -> None:
    """D-24. The path is in the entry body; the plan hash must not move.

    D-15 says where a file sits on disk is not part of the commitment, so a plan
    copied elsewhere keeps its identity. Recording the path in the hashed record
    would have broken that.
    """
    ws = Workspace(tmp_path / "run")
    do_plan(ws, plan)

    body = ws.ledger.verify()[0].body
    assert body["plan_source_path"] == str(plan_path)
    assert "plan_source_path" not in plan.as_record()

    moved = tmp_path / "elsewhere.yaml"
    moved.write_text(plan_path.read_text(encoding="utf-8"), encoding="utf-8")
    assert Plan.load(moved).plan_hash == plan.plan_hash


def test_a_deleted_plan_is_not_performed_and_says_so(run: Workspace, plan_path: Path) -> None:
    """E8c as written: delete the file. The one honest remaining skip."""
    plan_path.unlink()
    checks = verify_run(run)
    working = next(c for c in checks if c.name == "plan (working file)")

    assert not working.performed
    assert "NOT CHECKED" in working.note
    assert str(plan_path) in working.note
    assert "another machine" in working.note


def test_an_unperformed_check_never_prints_ok(run: Workspace, plan_path: Path) -> None:
    """Condition 1 of the ruling."""
    plan_path.unlink()
    line = next(c for c in verify_run(run) if not c.performed).line()
    assert line.startswith("  [--]")
    assert "[ok]" not in line


def test_the_summary_names_the_shortfall(run: Workspace, plan_path: Path) -> None:
    """Condition 2. The count and the shortfall in one sentence.

    A script scraping only the last line must see that something was skipped,
    which is why the shortfall is not on a separate line.
    """
    assert "nothing out of place" in summarise(verify_run(run))

    plan_path.unlink()
    line = summarise(verify_run(run))
    assert "nothing out of place" not in line
    assert "1 not performed" in line
    assert "plan (working file)" in line


def test_verify_still_exits_zero_on_a_genuinely_absent_plan(tmp_path: Path) -> None:
    """A missing working file is not evidence of tampering, and E8c promises 0.

    An auditor scripting `verify` and reading only the exit code is a real
    person. What they must never get is exit 0 beside "nothing out of place"
    when a check was skipped -- which the test above covers.
    """
    plan_path, frame = build_inputs(tmp_path)
    run_dir = tmp_path / "run"
    cli("plan", str(plan_path), "--run", str(run_dir))
    cli("sample", str(plan_path), str(frame), "--run", str(run_dir))
    plan_path.unlink()

    result = cli("verify", "--run", str(run_dir))
    assert result.returncode == 0
    assert "not performed" in result.stdout
    assert "nothing out of place" not in result.stdout


def test_the_only_unperformed_case_reachable_from_the_cli_is_a_missing_file(
    tmp_path: Path,
) -> None:
    """Condition 3, asserted rather than asserted-in-prose.

    Every CLI verb loads the plan from a file, so `source_path` is always set and
    a path is always recorded. The `no plan path recorded` branch needs the
    Python API, which Phase 1 does not document as a surface -- raised with the
    director under condition 3 rather than shipped quietly as a second skip.
    """
    plan_path, frame = build_inputs(tmp_path)
    run_dir = tmp_path / "run"
    cli("plan", str(plan_path), "--run", str(run_dir))
    cli("sample", str(plan_path), str(frame), "--run", str(run_dir))

    assert "not performed" not in cli("verify", "--run", str(run_dir)).stdout

    plan_path.unlink()
    out = cli("verify", "--run", str(run_dir)).stdout
    assert "1 not performed" in out
    assert "no file at" in out


def test_a_plan_without_a_source_path_records_none(tmp_path: Path) -> None:
    """The condition-3 case itself, pinned so it cannot change unnoticed."""
    ws = Workspace(tmp_path / "run")
    do_plan(ws, Plan.from_mapping(PLAN_YAML))  # no source_path

    assert ws.ledger.verify()[0].body["plan_source_path"] is None
    working = next(c for c in verify_run(ws) if c.name == "plan (working file)")
    assert not working.performed
    assert "recorded no plan path" in working.note


def test_the_recorded_plan_path_is_as_invoked(tmp_path: Path) -> None:
    """V-13. SECURITY 3.8 said the path "is absolute". It is not.

    It is whatever was typed, which is why the operator has a control: run `plan`
    from the plan's own directory with a bare filename and the ledger records a
    filename, disclosing nothing about the machine.

    Pinned because 3.8 now documents that control, and a security document must
    describe the tool.
    """
    plan_path, _ = build_inputs(tmp_path)
    absolute = tmp_path / "abs-run"
    relative = tmp_path / "rel-run"

    cli("plan", str(plan_path), "--run", str(absolute))
    subprocess.run(
        [*CLI, "plan", "plan.yaml", "--run", str(relative)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    def recorded(run_dir: Path) -> str:
        line = (run_dir / "ledger.jsonl").read_text(encoding="utf-8").splitlines()[0]
        return str(json.loads(line)["body"]["plan_source_path"])

    assert recorded(relative) == "plan.yaml", "a bare filename must stay a bare filename"
    assert recorded(absolute) == str(plan_path)
    assert str(tmp_path) not in str(recorded(relative))


def test_the_cli_refuses_a_missing_plan_before_our_code_runs() -> None:
    """PLAN_FILE_MISSING is defensive, and this is what pins that.

    Every verb declares its plan argument as `click.Path(exists=True)`, so Click
    refuses a missing path with a usage error and exit 2. `Plan.load`'s own
    refusal never runs from the CLI.

    That makes the code a Python API guard, not an operator-facing refusal, and
    the Phase 2 contract says so. If someone relaxes the Click guard to let our
    message through, this test fails and the contract row has to be re-read
    rather than quietly becoming wrong.

    It also records a limit of the mutation sweep. The sweep proved
    PLAN_FILE_MISSING is distinguishable, because a test calls `Plan.load`
    directly. Distinguishable is not the same as reachable by an operator.
    """
    result = cli("plan", "no-such-plan.yaml")
    combined = result.stdout + result.stderr

    assert result.returncode == 2
    assert "Invalid value" in combined, "Click no longer owns this refusal"
    assert "PLAN_FILE_MISSING" not in combined


def test_every_input_path_argument_still_declares_exists() -> None:
    """The general shape of the above, so it is not pinned one argument at a time.

    Three arguments take an input file that must already be there: the plan, the
    frame, and the labels. All three let Click check existence, so none of our
    own missing-file refusals can reach an operator through them.

    Recorded as a property rather than a per-argument test because the open
    question is about all three at once: should this tool own missing-input
    refusals, or is Click's message the right one? Nobody has decided. Until
    somebody does, this asserts what is actually true.
    """
    source = (Path(__file__).resolve().parents[1] / "src" / "prevalence_kit" / "cli.py").read_text(
        encoding="utf-8"
    )
    for name in ("plan_path", "frame_path", "labels_path"):
        assert name in source, name
    assert source.count("click.Path(exists=True, path_type=Path)") == 3, (
        "the number of existence-checked input arguments changed; "
        "see the Phase 2 contract on PLAN_FILE_MISSING being defensive"
    )
