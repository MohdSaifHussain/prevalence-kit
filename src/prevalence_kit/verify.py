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
from .ledger import Entry
from .plan import Plan
from .run import Workspace, _estimate_from
from .sampling import draw_srs, sample_record
from .seal import Manifest

EVIDENCE_STEPS = ("plan", "sample", "ingest-labels", "estimate")
"""The four steps that produce the number. Each may appear **at most once**, and
only in this order. A run is one measurement; a second measurement is a second
workspace."""

REPEATABLE_STEPS = ("report",)
"""`report` may repeat, and each emission appends its own entry. Re-emitting
cannot change the number -- the estimate is already sealed and chained -- and a
record of every emission is something an auditor wants, not something to forbid."""


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

    _verify_linear(entries)
    checks.append(
        Check(
            "run shape",
            True,
            "each evidence step recorded once, in order: " + " -> ".join(_evidence_of(entries)),
        )
    )

    by_step = {e.step: e for e in entries}
    plan = _verify_plan(ws, entries, plan_path, checks)
    _verify_sample(ws, by_step, plan, checks)
    _verify_seals(ws, by_step, checks)
    _verify_estimate(ws, by_step, plan, checks)
    return checks


def _evidence_of(entries: list[Entry]) -> list[str]:
    return [e.step for e in entries if e.step not in REPEATABLE_STEPS]


def _verify_linear(entries: list[Entry]) -> None:
    """A run is a linear sequence of evidence steps. Refuse anything else.

    Two distinct failures, one code, separate detail so an operator can tell them
    apart:

    * a repeated step -- and since every step raises its Refusal *before*
      appending, a failed step writes no entry. So a repeat in a ledger is always
      a repeated **success**: a step that completed, produced a result, and was
      then deliberately done again. That is not a retry, it is a second attempt
      at the same number.
    * steps out of order -- a record claiming the estimate was computed before
      the sample was drawn used to verify clean, because a dict does not care
      about order.
    """
    seen: list[str] = []
    for i, entry in enumerate(entries):
        if entry.step in REPEATABLE_STEPS:
            continue
        if entry.step not in EVIDENCE_STEPS:
            raise Refusal(
                Reason.RUN_NOT_LINEAR,
                f"Ledger entry {i} records an unknown step {entry.step!r}.",
                f"A run is made of {', '.join(EVIDENCE_STEPS)}. Restore the ledger.",
            )
        if entry.step in seen:
            raise Refusal(
                Reason.RUN_NOT_LINEAR,
                f"Step {entry.step!r} was recorded more than once (again at entry {i}).",
                "This workspace holds more than one attempt at the same measurement. "
                "A new measurement is a new workspace; do not publish this number.",
            )
        seen.append(entry.step)

    expected = [s for s in EVIDENCE_STEPS if s in seen]
    if seen != expected:
        raise Refusal(
            Reason.RUN_NOT_LINEAR,
            f"The steps are recorded as {' -> '.join(seen)}, "
            f"but a run must go {' -> '.join(expected)}.",
            "The record claims the work happened in an impossible order. "
            "Do not publish this number.",
        )


def _verify_plan(ws, entries, plan_path, checks) -> Plan:  # type: ignore[no-untyped-def]
    # Layer 3: the plan is ledger entry 0 and nothing else. Taking the *latest*
    # plan entry is what let a re-registered plan be certified as the original,
    # and printed under the word "genesis". The word now means what it says.
    entry = entries[0]
    if entry.step != "plan":
        raise Refusal(
            Reason.LEDGER_BROKEN,
            f"The first ledger entry is {entry.step!r}, not the plan.",
            "A run opens with `plan`. Restore the ledger from your record.",
        )
    recorded_hash = str(entry.body["plan_hash"])

    # (a) The sealed copy. Always available, so R5 holds after the file is gone.
    sealed = ws.plan_store()
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
    checks.append(
        Check(
            "plan (sealed copy)",
            True,
            f"matches genesis hash {recorded_hash[:16]} (ledger entry 0)",
        )
    )

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
