"""A run is one measurement, in order. Anything else is refused.

This is the V-1 family. The defect it closes: run the chain, dislike the number,
lower the pre-registered threshold, re-run everything into the same workspace --
and `verify` certified the second attempt as the original, printing the second
plan's hash under the word "genesis".

Three layers, and each is tested separately because each covers a case the
others do not:

* Layer 1, `do_plan` refuses a second plan -- prevention.
* Layer 2, `verify` refuses a non-linear ledger -- detection, and it holds for a
  record this code never wrote. An auditor may be handed anything.
* Layer 3, the plan is ledger entry 0 and the word "genesis" means that.

Layer 4 (`plan.sealed` is write-once) is a prerequisite for Layer 3 rather than
a fourth extra: bind entry 0 while `do_plan` can still overwrite the sealed plan
and the sealed-copy check fails first, so the working-file check never runs.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
import yaml

from prevalence_kit.canonical import GENESIS_LINK, digest
from prevalence_kit.errors import Reason, Refusal
from prevalence_kit.ledger import Ledger
from prevalence_kit.plan import Plan
from prevalence_kit.run import Workspace, do_estimate, do_ingest, do_plan, do_sample
from prevalence_kit.verify import EVIDENCE_STEPS, REPEATABLE_STEPS, verify_run
from tests.conftest import PLAN_YAML, POSITIVES, write_labels


def rechain(ws: Workspace, records: list[dict[str, Any]]) -> None:
    """Rewrite a ledger with every link honestly recomputed.

    The point of these tests is a record that is internally perfect and still
    wrong. If the chain were merely broken, `LEDGER_BROKEN` would catch it and
    nothing would be learned.
    """
    prev = GENESIS_LINK
    for seq, record in enumerate(records):
        record.pop("entry_digest", None)
        record["seq"] = seq
        record["prev"] = prev
        record["entry_digest"] = digest({k: v for k, v in record.items() if k != "entry_digest"})
        prev = str(record["entry_digest"])
    (ws.root / "ledger.jsonl").write_text(
        "\n".join(
            json.dumps(r, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
            for r in records
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def ledger_records(ws: Workspace) -> list[dict[str, Any]]:
    text = (ws.root / "ledger.jsonl").read_text(encoding="utf-8")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


# --------------------------------------------------------- positive controls


def test_an_honest_run_still_passes(run: Workspace, plan_path: Path) -> None:
    """Without this, every refusal below proves only that the gate refuses."""
    checks = verify_run(run, plan_path)
    assert all(c.ok for c in checks)
    shape = next(c for c in checks if c.name == "run shape")
    assert "plan -> sample -> ingest-labels -> estimate" in shape.note


def test_genesis_names_entry_zero(run: Workspace, plan_path: Path) -> None:
    """Layer 3. The word must describe the record, not the latest thing found."""
    entry_zero_hash = str(run.ledger.verify()[0].body["plan_hash"])
    note = next(c for c in verify_run(run, plan_path) if c.name == "plan (sealed copy)").note
    assert entry_zero_hash[:16] in note
    assert "ledger entry 0" in note


def test_a_partial_run_verifies(
    tmp_path: Path, plan: Plan, plan_path: Path, frame_path: Path
) -> None:
    """plan + sample and nothing else is a lawful prefix, not a broken run."""
    ws = Workspace(tmp_path / "run")
    do_plan(ws, plan)
    do_sample(ws, plan, frame_path)
    assert all(c.ok for c in verify_run(ws, plan_path))


def test_a_failed_step_writes_no_entry(
    tmp_path: Path, plan: Plan, plan_path: Path, frame_path: Path
) -> None:
    """Load-bearing for the strict-linearity ruling, so it is asserted, not assumed.

    Because a refusal happens before `ledger.append`, retrying after a mistake
    leaves no trace -- so the ordinary retry workflow passes strict linearity
    untouched. Which means a repeated step in a ledger is always a repeated
    *success*, and that is not a usability case.
    """
    ws = Workspace(tmp_path / "run")
    do_plan(ws, plan)
    drawn = do_sample(ws, plan, frame_path)
    before = [e.step for e in ws.ledger.verify()]

    incomplete = write_labels(tmp_path, list(drawn)[:10], positives=POSITIVES)
    with pytest.raises(Refusal) as exc:
        do_ingest(ws, plan, incomplete)
    assert exc.value.reason is Reason.LABELS_UNMATCHED
    assert [e.step for e in ws.ledger.verify()] == before

    do_ingest(ws, plan, write_labels(tmp_path, list(drawn), positives=POSITIVES))
    do_estimate(ws, plan)
    steps = [e.step for e in ws.ledger.verify()]
    assert steps == list(EVIDENCE_STEPS)
    assert len(steps) == len(set(steps))


def test_report_may_repeat(run: Workspace, plan_path: Path) -> None:
    """The exemption, stated as a rule rather than left to be inferred.

    Re-emitting cannot change the number -- the estimate is already sealed and
    chained -- and a record of every emission is something an auditor wants.
    """
    assert "report" in REPEATABLE_STEPS
    run.ledger.append("report", {"emitted": 1})
    run.ledger.append("report", {"emitted": 2})
    assert all(c.ok for c in verify_run(run, plan_path))


# --------------------------------------------------------- negative controls


def test_replanning_into_an_open_workspace_is_refused(
    tmp_path: Path, plan: Plan, plan_path: Path, frame_path: Path
) -> None:
    """Layer 1, at write time. The V-1 scenario, end to end."""
    ws = Workspace(tmp_path / "run")
    do_plan(ws, plan)
    drawn = do_sample(ws, plan, frame_path)
    do_ingest(ws, plan, write_labels(tmp_path, list(drawn), positives=POSITIVES))
    first = do_estimate(ws, plan).point

    lowered = PLAN_YAML | {"estimand": PLAN_YAML["estimand"] | {"threshold": "0.05"}}
    plan_path.write_text(yaml.safe_dump(lowered, sort_keys=True), encoding="utf-8")

    with pytest.raises(Refusal) as exc:
        do_plan(ws, Plan.load(plan_path))
    assert exc.value.reason is Reason.RUN_ALREADY_OPEN
    assert first == "0.225000000000"


def test_a_second_attempt_in_one_ledger_is_refused(run: Workspace, plan_path: Path) -> None:
    """Layer 2, repeat half.

    Built by hand, with every link honestly recomputed, because `verify` must
    hold against a record this code never wrote.
    """
    records = ledger_records(run)
    rechain(run, records + [dict(r) for r in records])

    with pytest.raises(Refusal) as exc:
        verify_run(run, plan_path)
    assert exc.value.reason is Reason.RUN_NOT_LINEAR
    assert "more than once" in exc.value.detail


def test_steps_out_of_order_are_refused(run: Workspace, plan_path: Path) -> None:
    """Layer 2, order half.

    A record claiming the estimate was computed before the sample was drawn used
    to verify clean, because `by_step` was a dict and dicts do not care about
    order. Same root cause as V-1: trusting the shape of a record instead of
    re-deriving it.
    """
    records = ledger_records(run)
    rechain(run, [records[0], records[3], records[1], records[2]])

    with pytest.raises(Refusal) as exc:
        verify_run(run, plan_path)
    assert exc.value.reason is Reason.RUN_NOT_LINEAR
    assert "must go" in exc.value.detail


def test_an_unknown_step_is_refused(run: Workspace, plan_path: Path) -> None:
    """Nothing gets smuggled into a run by inventing a step name."""
    run.ledger.append("adjust", {"nudge": True})

    with pytest.raises(Refusal) as exc:
        verify_run(run, plan_path)
    assert exc.value.reason is Reason.RUN_NOT_LINEAR
    assert "unknown step" in exc.value.detail


def test_a_ledger_not_opening_with_plan_is_refused(tmp_path: Path, plan_path: Path) -> None:
    ws = Workspace(tmp_path / "run")
    ws.root.mkdir(parents=True)
    Ledger(ws.root / "ledger.jsonl").append("sample", {"n": 1})

    with pytest.raises(Refusal) as exc:
        verify_run(ws, plan_path)
    assert exc.value.reason in {Reason.RUN_NOT_LINEAR, Reason.LEDGER_BROKEN}


def test_replan_without_rerunning_names_the_plan_not_the_estimate(
    run: Workspace, plan_path: Path
) -> None:
    """V-2. The right code for the flagship failure mode.

    This used to refuse `ESTIMATE_MISMATCH`, sending an operator to inspect
    frame.json when what actually happened was a plan re-registered after the
    results were seen.
    """
    plan_path.write_text(yaml.safe_dump(PLAN_YAML | {"seed": "changed"}), encoding="utf-8")

    with pytest.raises(Refusal) as exc:
        verify_run(run, plan_path)
    assert exc.value.reason is Reason.PLAN_HASH_MISMATCH


def test_verify_without_the_key_refuses_by_name(run: Workspace, plan_path: Path) -> None:
    """V-6. This path read the key file directly and died with FileNotFoundError."""
    run.key_path.unlink()

    with pytest.raises(Refusal) as exc:
        verify_run(run, plan_path)
    assert exc.value.reason is Reason.KEY_MISSING


def test_labels_for_a_different_sample_are_refused(run: Workspace, plan_path: Path) -> None:
    """F-6. `verify` used to trust that ingest had checked this.

    `do_ingest` enforces a one-to-one match at write time. `verify` checked
    labels.json against its ledger digest and stopped there -- so a run whose
    ledger is internally consistent but whose labels belong to a different
    sample passed. G4 claims verify re-derives rather than trusts; here it
    trusted.

    Both files are digest-protected, so this is built by hand with every link
    honestly recomputed.
    """
    labels = json.loads((run.root / "labels.json").read_text(encoding="utf-8"))
    swapped = {f"not-the-sample-{i}": v for i, v in enumerate(labels.values())}
    (run.root / "labels.json").write_text(
        json.dumps(swapped, sort_keys=True, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
        newline="\n",
    )
    records = ledger_records(run)
    records[2]["body"]["labels_digest"] = digest(swapped)
    rechain(run, records)

    with pytest.raises(Refusal) as exc:
        verify_run(run, plan_path)
    assert exc.value.reason is Reason.LABELS_UNMATCHED
