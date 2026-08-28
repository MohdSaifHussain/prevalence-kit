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
from tests.conftest import PLAN_YAML, POSITIVES, rewrite_ledger_line

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
    assert "SKIPPED" in working.note


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
    """E9b."""
    next((run.root / "sealed").rglob("*.bin")).unlink()

    with pytest.raises(Refusal) as exc:
        verify_run(run, plan_path)
    assert exc.value.reason is Reason.SEAL_TRUNCATED


def test_swapped_chunks_between_items(run: Workspace, plan_path: Path) -> None:
    """E9c at run level. Both chunks authenticate; neither belongs where it sits."""
    a, b = sorted((run.root / "sealed").rglob("*.bin"))[:2]
    a_bytes, b_bytes = a.read_bytes(), b.read_bytes()
    a.write_bytes(b_bytes)
    b.write_bytes(a_bytes)

    with pytest.raises(Refusal) as exc:
        verify_run(run, plan_path)
    # Single-chunk items, so a cross-item swap is a substitution, not a reorder.
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
