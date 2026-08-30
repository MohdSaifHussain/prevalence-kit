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
from typing import cast

from .canonical import digest
from .errors import Reason, Refusal
from .ledger import Entry
from .plan import Plan
from .run import StratifiedDraw, Workspace, _estimate_from, expected_method
from .sampling import (
    draw_srs,
    draw_stratified,
    sample_record,
    stratified_sample_record,
)
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
    """One thing `verify` looked at.

    `performed` is separate from `ok` on purpose. A check that did not run is not
    a check that passed, and printing `[ok]` for one is how a green line comes to
    mean nothing. V-12: `verify` used to print

        [ok] plan (working file): SKIPPED -- no plan file on disk to compare

    and count it toward "8 checks, nothing out of place" -- while a tampered plan
    sat on disk unread.
    """

    name: str
    ok: bool
    note: str
    performed: bool = True

    def line(self) -> str:
        if not self.performed:
            return f"  [--] {self.name}: {self.note}"
        return f"  [{'ok' if self.ok else '!!'}] {self.name}: {self.note}"


def summarise(checks: list[Check]) -> str:
    """The last line. A script scraping only this must still see a shortfall.

    Never says "nothing out of place" when something was not performed: the count
    and the shortfall go in the same sentence.
    """
    not_performed = [c for c in checks if not c.performed]
    if not_performed:
        return (
            f"verified: {len(checks)} checks, {len(not_performed)} not performed "
            f"({', '.join(c.name for c in not_performed)})."
        )
    return f"verified: {len(checks)} checks, nothing out of place."


def verify_run(ws: Workspace, plan_path: Path | None = None) -> list[Check]:
    """Walk every link. Raises Refusal at the first thing that does not hold."""
    checks: list[Check] = []

    # A missing run directory and an empty ledger are different problems with
    # different artifacts to open -- the path you typed, versus the ledger file.
    # D-22's rule counts artifacts, and these are two. Reporting LEDGER_BROKEN for
    # a mistyped path sends the operator to inspect a file that is not there.
    if not ws.root.is_dir():
        raise Refusal(
            Reason.RUN_NOT_FOUND,
            f"There is no run directory at {ws.root}.",
            "Check the path you passed to --run. If this is a new measurement, run `plan` first.",
        )

    entries = ws.ledger.verify()
    if not entries:
        raise Refusal(
            Reason.LEDGER_BROKEN,
            f"The run at {ws.root} has no ledger entries yet.",
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
                Reason.PLAN_SEAL_MISSING,
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

    # (b) The working file. `--plan` is an explicit override; otherwise fall back
    #     to the path recorded when the run opened, so forgetting the flag is not
    #     a case where the tool knows where the plan was and declines to look.
    #     The only remaining not-performed case is a file that is genuinely gone.
    recorded_path = entry.body.get("plan_source_path")
    candidate = plan_path or (Path(str(recorded_path)) if recorded_path else None)

    if candidate is None:
        checks.append(
            Check(
                "plan (working file)",
                True,
                "NOT CHECKED -- this run recorded no plan path. Pass --plan <path> to "
                "compare the working file against the sealed copy.",
                performed=False,
            )
        )
    elif not Path(candidate).exists():
        checks.append(
            Check(
                "plan (working file)",
                True,
                f"NOT CHECKED -- no file at {candidate}. That path was recorded when this run "
                "was created, so it may belong to another machine. Only the sealed copy was "
                "checked; pass --plan <path> if the file is elsewhere.",
                performed=False,
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
    # Redraw the design the plan pre-registered, not the one this function used
    # to assume. `draw_srs` was called unconditionally here, so a stratified run
    # would have been checked against a simple random redraw -- the auditor's
    # tool making the same substitution the estimator was making. F-10's family,
    # third site.
    if plan.design == "stratified":
        assert plan.strata is not None  # guaranteed by Plan.from_mapping
        per_stratum = {
            str(name): int(count)
            for name, count in zip(
                recorded["allocation"]["strata"],
                recorded["allocation"]["units"],
                strict=True,
            )
        }
        redrawn_by_stratum = draw_stratified(
            {str(k): list(v) for k, v in frame.items()},
            seed=plan.seed,
            allocation=per_stratum,
        )
        total_unique = sum(len(set(v)) for v in frame.values())
        rebuilt = stratified_sample_record(
            plan.plan_hash,
            plan.seed,
            total_unique,
            redrawn_by_stratum,
            recorded["allocation"],
        )
        n_redrawn = len(cast("list[str]", rebuilt["item_ids"]))
    else:
        redrawn = draw_srs(frame, seed=plan.seed, n=plan.sample_size)
        rebuilt = sample_record(plan.plan_hash, plan.seed, len(set(frame)), redrawn)
        n_redrawn = len(redrawn)

    if digest(rebuilt) != digest(recorded):
        raise Refusal(
            Reason.ESTIMATE_MISMATCH,
            "Redrawing the sample from the recorded plan and frame gives a different sample.",
            "The sample was not drawn by the plan it claims. Do not publish this number.",
        )
    # **The note names the design it redrew, and that is the point of the line.**
    # It read `N ids redrawn from the frame, identical` for both designs, so the
    # director's hand-run could not tell a stratified redraw from a simple random
    # one -- which is exactly the substitution this branch exists to prevent.
    # A control nobody can read is a control on paper: the check was real, its
    # output was silent about what it had checked.
    how = "per stratum" if plan.design == "stratified" else "as a simple random sample"
    checks.append(Check("sample", True, f"{n_redrawn} ids redrawn from the frame {how}, identical"))


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
    # F-6: `do_ingest` enforces a one-to-one match at write time, but `verify`
    # trusted that it had. G4 claims verify re-derives rather than trusts, and
    # here it trusted. A run whose ledger is internally consistent but whose
    # labels belong to a different sample used to pass.
    sample = ws.read_json("sample.json")
    drawn = {str(i) for i in sample["item_ids"]}
    if set(labels) != drawn:
        raise Refusal(
            Reason.LABELS_UNMATCHED,
            f"The record holds {len(labels)} labels for a sample of {len(drawn)} items, "
            f"and they are not the same items.",
            "These labels are not for this sample. Do not publish this number.",
        )

    store = ws.store()
    seals = entry.body["seals"]
    assert isinstance(seals, list)
    for record in seals:
        store.verify_item(Manifest.from_record(record))
    checks.append(
        Check(
            "labels",
            True,
            f"{len(labels)} labels, matching the drawn sample one-to-one",
        )
    )
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
    # F-10's durable half, and it runs BEFORE the recomputation on purpose.
    #
    # Recomputing proves the number follows from the labels. It cannot prove the
    # number was produced by the method the operator pre-registered, because it
    # recomputes through the same function -- so when `plan.interval` sat inert,
    # `verify` reproduced the same Wilson interval and reported the estimate
    # reproduced. The instrument agreed with the defect because it shared the
    # defect. Q-2, arriving as a live failure rather than a caveat.
    #
    # This comparison does not depend on the dispatch being right. That is the
    # whole point: dispatch makes the two artifacts agree today, and this catches
    # the next plan field that goes inert the same way.
    wanted = expected_method(plan)
    if str(recorded["method"]) != wanted:
        raise Refusal(
            Reason.ESTIMATE_METHOD_MISMATCH,
            f"The plan pre-registers interval {plan.interval!r}, which this tool "
            f"records as {wanted!r} -- but estimate.json records method "
            f"{str(recorded['method'])!r}. Two artifacts in this run "
            "disagree about how the number was produced.",
            "Do not publish this number. The plan is the commitment, so either the "
            "estimate was produced by a different method than the one registered, "
            "or one of the two files has been edited. Re-run the chain from `plan`.",
        )
    checks.append(
        Check(
            "estimate method",
            True,
            f"estimate.json records {recorded['method']}, matching the plan",
        )
    )

    draw = StratifiedDraw.from_workspace(ws) if plan.design == "stratified" else None
    recomputed = _estimate_from(plan, ws.read_json("labels.json"), draw).as_record()
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
