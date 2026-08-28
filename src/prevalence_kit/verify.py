"""verify -- re-check the whole chain, and say no when it does not hold.

`verify` is the only reason to trust anything else this tool prints. So it
re-derives rather than re-reads: it redraws the sample from the recorded frame
and recomputes the estimate from the recorded labels, instead of trusting the
numbers already written down.

It must work from the sealed record alone (R5). The original population file,
labels file, and even the plan file may all be gone.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .canonical import digest
from .errors import Reason, Refusal
from .plan import Plan
from .run import Workspace, _estimate_from
from .sampling import draw_srs, sample_record
from .seal import Manifest, SealedStore


@dataclass(frozen=True, slots=True)
class Check:
    name: str
    ok: bool
    note: str

    def line(self) -> str:
        return f"  [{'ok' if self.ok else '--'}] {self.name}: {self.note}"


def verify_run(ws: Workspace, plan_path: Path | None = None) -> list[Check]:
    """Walk every link. Raises Refusal at the first thing that does not hold."""
    checks: list[Check] = []

    entries = ws.ledger.verify()
    if not entries:
        raise Refusal(
            Reason.LEDGER_BROKEN,
            "The ledger is empty; there is nothing to verify.",
            "Run `plan` first.",
        )
    checks.append(
        Check("ledger chain", True, f"{len(entries)} entries, each linked to the one before")
    )

    by_step = {e.step: e for e in entries}
    plan = _verify_plan(ws, by_step, plan_path, checks)
    _verify_sample(ws, by_step, plan, checks)
    _verify_seals(ws, by_step, checks)
    _verify_estimate(ws, by_step, plan, checks)
    return checks


def _verify_plan(ws, by_step, plan_path, checks) -> Plan:  # type: ignore[no-untyped-def]
    entry = by_step.get("plan")
    if entry is None:
        raise Refusal(Reason.LEDGER_BROKEN, "The ledger has no plan step.", "Run `plan` first.")
    recorded_hash = str(entry.body["plan_hash"])

    # (a) The sealed copy. Always available, so R5 holds after the file is gone.
    sealed = SealedStore(ws.root / "plan.sealed", ws.key_path.read_bytes())
    manifest = Manifest.from_record(entry.body["plan_seal"])
    try:
        plan_bytes = sealed.unseal(manifest)
    except Refusal as exc:
        if exc.reason is Reason.SEAL_TRUNCATED:
            raise Refusal(
                Reason.PLAN_MISSING,
                "The sealed copy of the plan is not in the run.",
                "Without it the plan cannot be checked at all. Restore the run directory.",
            ) from exc
        raise
    plan = Plan.from_mapping(json.loads(plan_bytes))
    if digest(plan.as_record()) != recorded_hash:
        raise Refusal(
            Reason.PLAN_HASH_MISMATCH,
            "The sealed plan does not match the hash recorded when the run opened.",
            "The record is inconsistent with itself. Do not publish this number.",
        )
    checks.append(Check("plan (sealed copy)", True, f"matches genesis hash {recorded_hash[:16]}"))

    # (b) The working file, when it is still there. Catches edits made at any
    #     point after the run opened -- before ingest or long after it.
    candidate = plan_path or plan.source_path
    if candidate is None or not Path(candidate).exists():
        checks.append(
            Check(
                "plan (working file)",
                True,
                "SKIPPED -- no plan file on disk to compare. Only the sealed copy was checked.",
            )
        )
    elif Plan.load(Path(candidate)).plan_hash != recorded_hash:
        raise Refusal(
            Reason.PLAN_HASH_MISMATCH,
            f"{candidate} no longer matches the plan this run was opened with.",
            "The plan was edited after the run started. "
            "A plan changed after the fact is not a plan.",
        )
    else:
        checks.append(
            Check("plan (working file)", True, f"{candidate} unchanged since the run opened")
        )
    return plan


def _verify_sample(ws, by_step, plan, checks) -> None:  # type: ignore[no-untyped-def]
    entry = by_step.get("sample")
    if entry is None:
        return
    frame = ws.read_json("frame.json")
    if digest(frame) != str(entry.body["frame_digest"]):
        raise Refusal(
            Reason.LEDGER_BROKEN,
            "frame.json does not match the digest in the ledger.",
            "The recorded population was edited after the sample was drawn.",
        )
    recorded = ws.read_json("sample.json")
    if digest(recorded) != str(entry.body["sample_digest"]):
        raise Refusal(
            Reason.LEDGER_BROKEN,
            "sample.json does not match the digest in the ledger.",
            "The recorded sample was edited after it was drawn.",
        )
    redrawn = draw_srs(frame, seed=plan.seed, n=plan.sample_size)
    if digest(sample_record(plan.plan_hash, plan.seed, len(set(frame)), redrawn)) != digest(
        recorded
    ):
        raise Refusal(
            Reason.ESTIMATE_MISMATCH,
            "Redrawing the sample from the recorded plan and frame gives a different sample.",
            "The sample was not drawn by the plan it claims. Do not publish this number.",
        )
    checks.append(Check("sample", True, f"{len(redrawn)} ids redrawn from the frame, identical"))


def _verify_seals(ws, by_step, checks) -> None:  # type: ignore[no-untyped-def]
    entry = by_step.get("ingest-labels")
    if entry is None:
        return
    labels = ws.read_json("labels.json")
    if digest(labels) != str(entry.body["labels_digest"]):
        raise Refusal(
            Reason.LEDGER_BROKEN,
            "labels.json does not match the digest in the ledger.",
            "Labels were changed after they were ingested.",
        )
    store = ws.store()
    seals = entry.body["seals"]
    assert isinstance(seals, list)
    for record in seals:
        store.verify_item(Manifest.from_record(record))
    checks.append(
        Check(
            "sealed content",
            True,
            f"{len(seals)} items: every chunk authentic, in order, none missing",
        )
    )


def _verify_estimate(ws, by_step, plan, checks) -> None:  # type: ignore[no-untyped-def]
    entry = by_step.get("estimate")
    if entry is None:
        return
    recorded = ws.read_json("estimate.json")
    if digest(recorded) != str(entry.body["estimate_digest"]):
        raise Refusal(
            Reason.LEDGER_BROKEN,
            "estimate.json does not match the digest in the ledger.",
            "The estimate was edited after it was computed.",
        )
    recomputed = _estimate_from(plan, ws.read_json("labels.json")).as_record()
    if recomputed != recorded:
        raise Refusal(
            Reason.ESTIMATE_MISMATCH,
            f"Recomputing from the sealed labels gives {recomputed['point']}, "
            f"but the record says {recorded['point']}.",
            "The published number does not follow from the evidence. Do not publish it.",
        )
    checks.append(
        Check("estimate", True, f"recomputed {recorded['point']} from the record, identical")
    )
