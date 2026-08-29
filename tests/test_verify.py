"""End-to-end: the chain holds, and every way of breaking it is named.

These mirror the exit checks in docs/contracts/PHASE-1-CONTRACT.md section 7, so
the director's manual run and CI are checking the same properties. Where a test
corresponds to an exit check, the check id is in the docstring.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from prevalence_kit.errors import Reason, Refusal
from prevalence_kit.plan import Plan
from prevalence_kit.run import Workspace
from prevalence_kit.seal import _safe_id
from prevalence_kit.verify import verify_run
from tests.conftest import PLAN_YAML, POSITIVES, big_item_chunks, rewrite_ledger_line

# ------------------------------------------------------------ positive control


def test_honest_run_verifies(run: Workspace, plan_path: Path) -> None:
    """E3 and E5. The accept case, without which every refusal below proves nothing."""
    checks = verify_run(run, plan_path)
    assert all(c.ok for c in checks)
    assert {c.name for c in checks} >= {
        "ledger chain",
        "plan (sealed copy)",
        "plan (working file)",
        "sample",
        "sealed content",
        "estimate",
    }


def test_estimate_matches_the_labels(run: Workspace) -> None:
    estimate = json.loads((run.root / "estimate.json").read_text(encoding="utf-8"))
    assert estimate["positives"] == POSITIVES
    assert estimate["n"] == PLAN_YAML["sample_size"]
    assert float(estimate["low"]) <= float(estimate["point"]) <= float(estimate["high"])


def test_verify_without_the_original_inputs(
    run: Workspace, tmp_path: Path, plan_path: Path
) -> None:
    """E6, and requirement R5 -- the claim the whole tool rests on.

    Delete the population file and the labels file. `verify` must still reproduce
    the number from the sealed record alone.
    """
    (tmp_path / "frame.txt").unlink()
    (tmp_path / "labels.csv").unlink()
    assert all(c.ok for c in verify_run(run, plan_path))


def test_verify_says_out_loud_when_it_skipped_the_plan_file(
    run: Workspace, plan_path: Path
) -> None:
    """E8c, and requirement R10 (D-15).

    With the working plan gone, only the sealed copy can be checked. Verify must
    still pass -- and must say which check it did not run. Silence here would let
    an operator believe both ran.
    """
    plan_path.unlink()
    checks = verify_run(run, plan_path)
    working = next(c for c in checks if c.name == "plan (working file)")
    assert working.ok
    assert not working.performed, "a check that did not run must not report as performed"
    assert "NOT CHECKED" in working.note
    assert str(plan_path) in working.note, "the message must name the path it looked for"


# ------------------------------------------------------------ negative controls


def test_edited_ledger(run: Workspace, plan_path: Path) -> None:
    """E7."""
    rewrite_ledger_line(run, 1, lambda r: r["body"].__setitem__("n", 999))

    with pytest.raises(Refusal) as exc:
        verify_run(run, plan_path)
    assert exc.value.reason is Reason.LEDGER_BROKEN


def test_edited_plan_file(run: Workspace, plan_path: Path) -> None:
    """E8. Any field, not only the estimand."""
    plan_path.write_text(yaml.safe_dump(PLAN_YAML | {"seed": "tampered"}), encoding="utf-8")

    with pytest.raises(Refusal) as exc:
        verify_run(run, plan_path)
    assert exc.value.reason is Reason.PLAN_HASH_MISMATCH


def test_plan_edited_after_ingest_and_estimate(
    tmp_path: Path, plan: Plan, plan_path: Path, frame_path: Path
) -> None:
    """E8b, and the answer to the director's E2-complement question.

    The genesis hash is fixed when `plan` runs, so the *timing* of an edit cannot
    matter. This runs the entire chain through estimate first, and only then edits
    the plan -- and asserts the same reason code as E8. Prose saying "timing does
    not matter" would not hold; this does.
    """
    from prevalence_kit.run import do_estimate, do_ingest, do_plan, do_sample
    from tests.conftest import write_labels

    ws = Workspace(tmp_path / "run")
    do_plan(ws, plan)
    drawn = do_sample(ws, plan, frame_path)
    do_ingest(ws, plan, write_labels(tmp_path, list(drawn), positives=POSITIVES))
    do_estimate(ws, plan)
    assert all(c.ok for c in verify_run(ws, plan_path))  # honest before the edit

    plan_path.write_text(yaml.safe_dump(PLAN_YAML | {"sample_size": 41}), encoding="utf-8")

    with pytest.raises(Refusal) as exc:
        verify_run(ws, plan_path)
    assert exc.value.reason is Reason.PLAN_HASH_MISMATCH


def test_tampered_sealed_chunk(run: Workspace, plan_path: Path) -> None:
    """E9."""
    chunk = next((run.root / "sealed").rglob("*.bin"))
    raw = bytearray(chunk.read_bytes())
    raw[-1] ^= 0xFF
    chunk.write_bytes(bytes(raw))

    with pytest.raises(Refusal) as exc:
        verify_run(run, plan_path)
    assert exc.value.reason is Reason.SEAL_TAMPERED


def test_dropped_chunk(run: Workspace, plan_path: Path) -> None:
    """E9b. Drops the final chunk of the multi-chunk item."""
    big_item_chunks(run)[-1].unlink()

    with pytest.raises(Refusal) as exc:
        verify_run(run, plan_path)
    assert exc.value.reason is Reason.SEAL_TRUNCATED


def test_swapped_chunks_within_one_item(run: Workspace, plan_path: Path) -> None:
    """E9c at run level.

    This is what F-4 was about. Every fixture item used to be a single chunk, so
    an intra-item reorder was not expressible and this test asserted
    MANIFEST_MISMATCH while the contract said REORDERED -- green test, wrong
    document. The fixture now seals one deliberately multi-chunk item, so the
    check tests what the contract says it tests.

    Every chunk still authenticates. Only the order is wrong.
    """
    chunks = big_item_chunks(run)
    assert len(chunks) >= 2, "the fixture must contain a multi-chunk item"
    first, second = chunks[0], chunks[1]
    first_bytes, second_bytes = first.read_bytes(), second.read_bytes()
    first.write_bytes(second_bytes)
    second.write_bytes(first_bytes)

    with pytest.raises(Refusal) as exc:
        verify_run(run, plan_path)
    assert exc.value.reason is Reason.SEAL_REORDERED


def test_swapped_chunks_between_items(run: Workspace, plan_path: Path) -> None:
    """A chunk from another item authenticates but does not belong here.

    Distinct from the reorder above, and it must stay distinct -- one code for
    both would tell an operator nothing about what happened.
    """
    a, b = (
        big_item_chunks(run)[0],
        next(
            p
            for p in (run.root / "sealed").rglob("*.bin")
            if p.parent != big_item_chunks(run)[0].parent
        ),
    )
    a.write_bytes(b.read_bytes())

    with pytest.raises(Refusal) as exc:
        verify_run(run, plan_path)
    assert exc.value.reason is Reason.SEAL_MANIFEST_MISMATCH


def test_edited_labels(run: Workspace, plan_path: Path) -> None:
    labels = json.loads((run.root / "labels.json").read_text(encoding="utf-8"))
    labels[next(iter(labels))] = "0.99"
    (run.root / "labels.json").write_text(json.dumps(labels, sort_keys=True), encoding="utf-8")

    with pytest.raises(Refusal) as exc:
        verify_run(run, plan_path)
    assert exc.value.reason is Reason.LEDGER_BROKEN


def test_edited_estimate(run: Workspace, plan_path: Path) -> None:
    path = run.root / "estimate.json"
    estimate = json.loads(path.read_text(encoding="utf-8"))
    estimate["point"] = "0.000000000000"
    path.write_text(json.dumps(estimate, sort_keys=True), encoding="utf-8")

    with pytest.raises(Refusal) as exc:
        verify_run(run, plan_path)
    assert exc.value.reason is Reason.LEDGER_BROKEN


def test_estimate_that_does_not_follow_from_the_labels(run: Workspace, plan_path: Path) -> None:
    """The one that matters: a number inconsistent with its own evidence.

    Rewrite the estimate AND its ledger digest, so the chain is internally clean
    and only recomputation catches it. This is the check that separates a record
    from a story.
    """
    from prevalence_kit.canonical import digest

    path = run.root / "estimate.json"
    estimate = json.loads(path.read_text(encoding="utf-8"))
    estimate["positives"] = 0
    estimate["point"] = "0.000000000000"
    path.write_text(
        json.dumps(estimate, sort_keys=True, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
        newline="\n",
    )
    rewrite_ledger_line(
        run, 3, lambda r: r["body"].__setitem__("estimate_digest", digest(estimate))
    )
    rewrite_ledger_line(run, 3, lambda r: r.__setitem__("entry_digest", _redigest(r)))

    with pytest.raises(Refusal) as exc:
        verify_run(run, plan_path)
    assert exc.value.reason is Reason.ESTIMATE_MISMATCH


def _redigest(record: dict) -> str:  # type: ignore[type-arg]
    from prevalence_kit.canonical import digest

    body = {k: v for k, v in record.items() if k != "entry_digest"}
    return digest(body)


# --------------------------------------------------------------- content leak


def test_no_content_anywhere_outside_the_sealed_store(run: Workspace) -> None:
    """E10, and requirement R4.

    The fixture plants SENTINEL-CONTENT- in every item. It must appear nowhere in
    the ledger, the labels record, the estimate, or any filename.
    """
    for path in run.root.rglob("*"):
        if not path.is_file() or _safe_id("") == path.parent.name:
            continue
        if "sealed" in path.parts:
            continue
        assert b"SENTINEL-CONTENT-" not in path.read_bytes(), path


def test_sealed_store_does_not_hold_plaintext(run: Workspace) -> None:
    for path in (run.root / "sealed").rglob("*.bin"):
        assert b"SENTINEL-CONTENT-" not in path.read_bytes(), path


def test_refusal_messages_carry_no_content(run: Workspace, plan_path: Path) -> None:
    chunk = next((run.root / "sealed").rglob("*.bin"))
    chunk.write_bytes(b"garbage")
    with pytest.raises(Refusal) as exc:
        verify_run(run, plan_path)
    assert "SENTINEL" not in exc.value.report()


# ------------------------------ PLAN_FILE_MISSING / PLAN_SEAL_MISSING, D2.7
#
# Two raise sites, two artifacts. Until 2026-08-29 they shared one code,
# `PLAN_MISSING`, and neither had a control. Found by D2.7's opening inventory
# and confirmed by mutation: swapping the code at either site left all 418 tests
# passing. Phase 1's outcome recorded "23 reason codes, each with both controls"
# and R3 as met. That was false for this code. C-27.
#
# Q8 / D-35 then split it, because D-22 counts artifacts and these are two: the
# plan file the operator named, and the sealed copy inside the run.


def test_a_missing_plan_file_is_refused_by_name(tmp_path: Path) -> None:
    """`PLAN_FILE_MISSING` -- the operator names a plan that is not there.

    The artifact is the path they typed on the command line, and the remedy is to
    fix the path or write a plan. **Nothing about the run directory is wrong**,
    which is the whole reason this is not the same code as the one below.
    """
    with pytest.raises(Refusal) as caught:
        Plan.load(tmp_path / "no-such-plan.yaml")

    assert caught.value.reason is Reason.PLAN_FILE_MISSING
    assert "no-such-plan.yaml" in caught.value.detail, "the operator must see which path failed"


def test_a_plan_that_is_there_loads(plan_path: Path) -> None:
    """The positive control for the pair above.

    A gate that refuses everything proves nothing, and `Plan.load` is the gate
    every CLI verb goes through.
    """
    assert Plan.load(plan_path).plan_hash


def test_a_missing_sealed_plan_copy_is_refused_by_name(run: Workspace, plan_path: Path) -> None:
    """`PLAN_SEAL_MISSING` -- the sealed copy is gone from the run directory.

    A different artifact from the test above and a different remedy -- restore the
    run, not the path. `verify` translates the seal store's `SEAL_TRUNCATED` here
    because at this point the missing thing is not a chunk, it is the plan.

    **D-15 check (a) is what this protects.** Without the sealed copy the plan
    cannot be checked at all, so `verify` must say that rather than skip quietly
    and still exit 0 -- which is V-12's shape.
    """
    sealed = run.root / "plan.sealed"
    assert sealed.is_dir(), "this test expects the sealed plan store where do_plan puts it"
    removed = 0
    for chunk in sorted(sealed.rglob("*")):
        if chunk.is_file():
            chunk.unlink()
            removed += 1
    assert removed, "nothing was removed, so the test would pass without testing anything"

    with pytest.raises(Refusal) as caught:
        list(verify_run(run, plan_path))

    assert caught.value.reason is Reason.PLAN_SEAL_MISSING
    assert "Restore the run" in caught.value.fix


def test_the_two_missing_plan_codes_send_the_operator_to_different_places() -> None:
    """Q8 / D-35, pinned so the split cannot quietly collapse back into one code.

    D-22's rule is to count the artifacts an operator must open, not the
    situations. These are two: the plan file the operator named, and the sealed
    copy inside the run. Two remedies too -- fix the path, or restore the run.

    **The operator-facing defect this closed was concrete.** Under the single
    `PLAN_MISSING`, someone who mistyped a path got a code whose contract
    description told them to restore their run directory. That is worse than an
    undifferentiated refusal: it sends them to the wrong artifact with
    confidence.
    """
    root = Path(__file__).resolve().parents[1] / "src" / "prevalence_kit"
    plan_src = (root / "plan.py").read_text(encoding="utf-8")
    verify_src = (root / "verify.py").read_text(encoding="utf-8")

    assert "Reason.PLAN_FILE_MISSING" in plan_src
    assert "Plan.load()" in plan_src, (
        "the file code is defensive and its fix text must address a caller, not an operator -- "
        "the CLI refuses a missing path before this runs"
    )

    assert "Reason.PLAN_SEAL_MISSING" in verify_src
    assert "Restore the run directory" in verify_src, "the seal code must send them to the run"

    assert "Reason.PLAN_SEAL_MISSING" not in plan_src
    assert "Reason.PLAN_FILE_MISSING" not in verify_src
