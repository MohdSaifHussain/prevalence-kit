"""The measurement run: the six steps, and the workspace they write into.

Layout of a run directory::

    ledger.jsonl      the chain -- the record everything else is checked against
    seal.key          the sealing key (never committed; see SECURITY.md 3.1)
    plan.sealed/      a sealed copy of the plan, so verify works without the file
    frame.json        the sampling frame ids, so a draw can be re-derived
    sample.json       the drawn ids
    labels.json       item id -> raw label value. No content.
    estimate.json     the number and its interval
    sealed/           the content, chunked and encrypted

Content lives only under `sealed/`. `labels.json` holds label values and never
text, which is what lets `verify` and `emit-report` run without unsealing
anything.
"""

from __future__ import annotations

import csv
import json
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from .canonical import JSONValue, canonical, digest, digest_bytes
from .errors import Reason, Refusal
from .estimators import Interval, clopper_pearson, wilson
from .ledger import Ledger
from .plan import SUPPORTED_INTERVALS, Plan
from .sampling import (
    draw_srs,
    draw_stratified,
    sample_record,
    stratified_sample_record,
)
from .seal import Manifest, SealedStore
from .stratified import Rounding, Stratum, allocate

PLAN_ITEM = "__plan__"

_CSV_FIELD_LIMIT = 64 * 1024 * 1024
"""Largest single CSV field accepted: exactly 67,108,864 bytes (64 MiB).

Not unbounded -- a runaway file should refuse rather than exhaust memory. The
figure is restated here in bytes so `tools/check_claims.py` can compare the prose
against the constant; rule 8 wants a checkable limit defended by machinery rather
than by a decision record."""


@dataclass(frozen=True, slots=True)
class Workspace:
    root: Path

    @property
    def ledger(self) -> Ledger:
        return Ledger(self.root / "ledger.jsonl")

    @property
    def key_path(self) -> Path:
        return self.root / "seal.key"

    def key(self) -> bytes:
        """The one place the sealing key is read.

        Every path goes through here. `verify` used to read the key file directly
        and died with a raw FileNotFoundError, which is why F-5's fix to
        `store()` did not reach it. One reader, one refusal. V-6.
        """
        if not self.key_path.exists():
            raise Refusal(
                Reason.KEY_MISSING,
                f"No sealing key at {self.key_path}.",
                "Without the key nothing can be unsealed. Restore it from wherever you kept it.",
            )
        return self.key_path.read_bytes()

    def store(self) -> SealedStore:
        return SealedStore(self.root / "sealed", self.key())

    def plan_store(self) -> SealedStore:
        """The plan's sealed copy. Write-once: a re-plan must never destroy the
        copy of the plan that was originally committed to. Layer 4 of V-1."""
        return SealedStore(self.root / "plan.sealed", self.key(), write_once=True)

    def read_json(self, name: str) -> Any:
        path = self.root / name
        if not path.exists():
            raise Refusal(
                Reason.LEDGER_BROKEN,
                f"The run is missing {name}.",
                "A step has not been run yet, or the run directory was edited.",
            )
        return json.loads(path.read_text(encoding="utf-8"))

    def write_json(self, name: str, value: JSONValue) -> str:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
            newline="\n",
        )
        return digest(value)


# --------------------------------------------------------------------- steps


def do_plan(ws: Workspace, plan: Plan) -> str:
    """Hash the plan and open the chain. No data file is touched here.

    The hash is computed from the plan alone (R1). We also seal a copy of the
    plan, so `verify` still has something to check against after the working file
    is moved or deleted (D-15).
    """
    ws.root.mkdir(parents=True, exist_ok=True)

    # Layer 1: a workspace holds exactly one measurement. Refusing here is
    # prevention; `verify` refuses independently (Layer 2), because an auditor
    # may be handed a record this code never wrote.
    if ws.ledger.read_raw():
        raise Refusal(
            Reason.RUN_ALREADY_OPEN,
            f"{ws.root} already holds a measurement.",
            "A new measurement is a new workspace. Re-registering a plan over an "
            "existing run is how a number gets chosen after the results are seen.",
        )

    if not ws.key_path.exists():
        ws.key_path.write_bytes(SealedStore.new_key())

    plan_hash = plan.plan_hash
    manifest = ws.plan_store().seal(PLAN_ITEM, canonical(plan.as_record()))

    ws.ledger.append(
        "plan",
        {
            "plan_hash": plan_hash,
            "plan_seal": manifest.as_record(),
            "estimand": plan.estimand.description,
            # Where the working plan file was when the run opened. In the entry
            # BODY, deliberately not in `Plan.as_record()`, so the plan hash is
            # untouched and D-15's principle survives: where a file sits on
            # someone's disk is not part of the commitment, and moving a plan
            # still does not change its identity. The body is digest-protected by
            # the chain like everything else.
            #
            # `verify` defaults to this path, so forgetting `--plan` is no longer
            # a case where the tool knows where the plan was and declines to look.
            # V-12, D-24. Disclosure consequence: SECURITY.md section 3.11.
            "plan_source_path": str(plan.source_path) if plan.source_path else None,
        },
    )
    return plan_hash


def _declared_path(plan: Plan, declared: str) -> Path:
    """Where the plan's `population` / `labels` value points, resolved.

    **The convention, stated because an unstated resolution rule is its own
    defect:** a relative path in the plan is resolved **against the directory
    holding the plan file**, not against the current working directory. That is
    how configuration files conventionally work, and it is the only rule that
    survives running the tool from somewhere else -- a plan that names
    `frame.txt` beside itself keeps meaning that file wherever you invoke from.

    A plan built through the Python API has no `source_path` (D-25 records that
    as a supported case), so there is no plan directory to resolve against and
    the working directory is used instead. That difference is visible rather than
    silent: the ledger records the path actually used.
    """
    base = plan.source_path.parent if plan.source_path is not None else Path.cwd()
    return (base / declared).resolve()


def _require_preregistered(plan: Plan, field: str, declared: str, supplied: Path) -> None:
    """F-11. Refuse when the file supplied is not the file the plan committed to.

    **Resolved paths, never strings.** `frame.txt` and `./frame.txt` are the same
    file and different strings, and a string comparison would refuse correct runs
    -- a control that fires for the wrong reason, which is rule 21.

    Raised at `sample` and at `ingest-labels`, which is **before the label budget
    is spent** -- Q2's reason, and the same reason Q7 refuses at plan load.
    """
    wanted = _declared_path(plan, declared)
    got = supplied.resolve()
    if wanted != got:
        raise Refusal(
            Reason.EVIDENCE_NOT_PREREGISTERED,
            f"The plan pre-registers `{field}: {declared}`, which resolves to "
            f"{wanted}. You supplied {got}. A pre-registered measurement is a "
            f"commitment about which evidence produces the number, so this run "
            f"would not be the measurement the plan describes.",
            f"Run it against {wanted}, or change `{field}` in the plan and re-run "
            f"`plan` into a fresh run directory. Changing the plan changes its "
            f"hash, which is what makes the swap visible instead of silent.",
        )


def do_sample(ws: Workspace, plan: Plan, frame_path: Path) -> tuple[str, ...]:
    """Draw the sample. Records the frame too, so the draw stays re-derivable.

    **Dispatches on the design.** It used to call `draw_srs` unconditionally,
    which was correct while `srs` was the only design and became a hazard the
    moment `stratified` was loadable: a stratified plan answered with a simple
    random draw is a number the plan does not describe. F-10's family.
    """
    _require_preregistered(plan, "population", plan.population, frame_path)

    if plan.design == "stratified":
        return _sample_stratified(ws, plan, frame_path)

    ids = _read_frame(frame_path)
    drawn = draw_srs(ids, seed=plan.seed, n=plan.sample_size)

    # V-7: a frame is a set of units, so de-duplicating is correct -- but doing it
    # silently is not. For a prevalence tool this is the denominator. Both counts
    # go in the record, so a reader can see the input differed from what was used.
    unique = sorted(set(ids))
    frame_digest = ws.write_json("frame.json", unique)
    record = sample_record(plan.plan_hash, plan.seed, len(unique), drawn)
    sample_digest = ws.write_json("sample.json", record)

    ws.ledger.append(
        "sample",
        {
            "frame_digest": frame_digest,
            "sample_digest": sample_digest,
            "frame_rows_read": len(ids),
            "frame_unique_ids": len(unique),
            "n": len(drawn),
            # D-24's shape, applied to the frame. After F-11's check these
            # cannot differ -- and recording both is what makes that checkable
            # rather than assumed. Stored AS INVOKED, not resolved: SECURITY
            # section 3.8 gives the operator a control by letting a bare
            # filename stay a bare filename, and an absolute path here would
            # take it away.
            "population_declared": plan.population,
            "population_used": str(frame_path),
        },
    )
    return drawn


def do_ingest(ws: Workspace, plan: Plan, labels_path: Path) -> dict[str, str]:
    """Seal the content, record the labels.

    Refuses unless the labels line up one-to-one with the drawn sample. A label
    set that is merely *mostly* right is how a measurement quietly becomes a
    different measurement.
    """
    _require_preregistered(plan, "labels", plan.labels, labels_path)

    drawn: list[str] = list(ws.read_json("sample.json")["item_ids"])
    rows = _read_labels(labels_path, plan.estimand.label_field)

    missing = sorted(set(drawn) - rows.keys())
    extra = sorted(rows.keys() - set(drawn))
    if missing or extra:
        raise Refusal(
            Reason.LABELS_UNMATCHED,
            f"{len(missing)} sampled items have no label; "
            f"{len(extra)} labels are for items not sampled.",
            "Label exactly the drawn sample -- no more, no less.",
        )

    store = ws.store()
    manifests = [store.seal(item_id, rows[item_id][1].encode("utf-8")) for item_id in drawn]
    labels = {item_id: rows[item_id][0] for item_id in drawn}

    labels_digest = ws.write_json("labels.json", labels)
    ws.ledger.append(
        "ingest-labels",
        {
            "labels_digest": labels_digest,
            "seals": [m.as_record() for m in manifests],
            "sealed_items": len(manifests),
            "labels_declared": plan.labels,
            "labels_used": str(labels_path),
        },
    )
    return labels


def do_estimate(ws: Workspace, plan: Plan) -> Interval:
    labels: dict[str, str] = ws.read_json("labels.json")
    interval = _estimate_from(plan, labels)
    estimate_digest = ws.write_json("estimate.json", interval.as_record())
    ws.ledger.append("estimate", {"estimate_digest": estimate_digest, "method": interval.method})
    return interval


def _estimate_from(plan: Plan, labels: dict[str, str]) -> Interval:
    _refuse_unestimable_design(plan)
    positives = 0
    for item_id, raw in labels.items():
        try:
            positives += 1 if plan.estimand.is_positive(raw) else 0
        except Refusal as exc:
            # Re-raised with the item id so the operator can find the row. The
            # label value is a label, not content, so naming it leaks nothing.
            raise Refusal(exc.reason, f"Item {item_id}: {exc.detail}", exc.fix) from exc
    return _interval_for(plan, positives, len(labels))


def _refuse_unestimable_design(plan: Plan) -> None:
    """A design that draws but cannot yet be estimated refuses BY NAME.

    `stratified_estimate` returns a standard error and no interval, and building
    the interval is **O-26** under **Q7** -- the plan names the method. Until it
    exists, the alternative to this refusal is `_estimate_from` answering a
    stratified draw with SRS Wilson: a number that looks fine, ignores the
    strata, and contradicts the design its own plan pre-registered.

    **A half-wired path that produces a number is worse than a refusal.** This is
    the same hazard as adding `stratified` to `SUPPORTED_DESIGNS` while
    `do_sample` still called `draw_srs`, and it is closed the same way -- named,
    not defaulted.

    Placed in `_estimate_from` rather than in `do_estimate` on purpose: `verify`
    recomputes through this function, so the refusal covers the auditor's path
    too and cannot be bypassed by re-verifying a run created by an older build.
    """
    if plan.design == "stratified":
        raise Refusal(
            Reason.DESIGN_NOT_ESTIMABLE,
            "This plan uses design: stratified. The sample is drawn correctly, "
            "per stratum, but this version has no stratified interval yet -- the "
            "stratified estimator returns a standard error and nothing turns it "
            "into a bound.",
            "Use `design: srs` to get a number now. The stratified interval is "
            "obligation O-26 and is governed by Q7: the plan will name the "
            "method, with no default. Refusing is deliberate -- estimating a "
            "stratified draw as a simple random sample would print a number your "
            "plan does not describe.",
        )


INTERVAL_METHOD = {
    "wilson": "wilson",
    "clopper_pearson": "clopper-pearson",
}
"""Plan vocabulary -> the `method` string the estimator stamps on its result.

**Two vocabularies that must agree, so something makes them agree** -- D-28.
The plan says `clopper_pearson` and the estimator stamps `clopper-pearson`, and
`verify`'s cross-check compares those two strings. Comparing them directly would
have fired `ESTIMATE_METHOD_MISMATCH` on every correct Clopper-Pearson run.

Found by running the dispatch rather than reading it, which is the only way this
class is ever found. `test_every_supported_interval_stamps_the_method_the_map_claims`
walks `SUPPORTED_INTERVALS` and checks each value against what the estimator
actually returns, so the map cannot drift from the behaviour it describes.
"""


def _interval_for(plan: Plan, positives: int, n: int) -> Interval:
    """The interval the plan pre-registered. Q11 / D-37, wired.

    **This dispatch is F-10's fix.** `plan.interval` was validated at load,
    hashed into the pre-registration record, and then read by nothing: a plan
    naming `clopper_pearson` was answered with Wilson, and `verify` agreed
    because it recomputes through this same function. The field reached the hash
    and changed no number.

    There is no default here and no fallback branch. `SUPPORTED_INTERVALS`
    already refused anything else at load, so an unknown method at this point
    means the two vocabularies have drifted, and that is worth a refusal rather
    than a quiet choice.
    """
    if plan.interval == "wilson":
        return wilson(positives, n)
    if plan.interval == "clopper_pearson":
        return clopper_pearson(positives, n)
    raise Refusal(
        Reason.PLAN_INVALID,
        f"The plan names interval {plan.interval!r}, which this version cannot compute.",
        f"Use one of: {', '.join(sorted(SUPPORTED_INTERVALS))}.",
    )


# ----------------------------------------------------------------- input I/O


def _sample_stratified(ws: Workspace, plan: Plan, frame_path: Path) -> tuple[str, ...]:
    """Allocate by Neyman, round by the plan's rule, then draw within each stratum.

    Order of operations is **D-30 condition 4**: allocate, round, *then* apply
    Q2's floor. `ALLOCATION_TOO_THIN` fires on the rounded number, because
    largest remainder can still leave a stratum at 0 or 1.

    `M_h` is the count of **unique** ids in the stratum. D-21 de-duplicates the
    frame and records both counts; stratum sizes inherit that rather than
    restating it, and both totals still reach the ledger.
    """
    rows = _read_stratified_frame(frame_path)
    assert plan.strata is not None  # guaranteed by Plan.from_mapping

    declared = {s.name: s for s in plan.strata}
    members: dict[str, list[str]] = {name: [] for name in declared}
    seen_rows = 0
    for item_id, stratum in rows:
        seen_rows += 1
        if stratum not in declared:
            # Q14 / D-40. S-1.13 makes strata mutually exclusive and covering, so
            # a unit outside every declared stratum cannot be silently dropped:
            # the frame is the denominator, and dropping is V-7's class.
            raise Refusal(
                Reason.STRATUM_UNDECLARED,
                f"Frame unit {item_id!r} is in stratum {stratum!r}, which the plan "
                f"does not declare. The plan declares: "
                f"{', '.join(sorted(declared))}.",
                "Add that stratum to the plan, or correct the frame's `stratum` "
                "column. Every frame unit must fall in exactly one declared "
                "stratum -- dropping the rest would change the denominator.",
            )
        members[stratum].append(item_id)

    unique = {name: sorted(set(ids)) for name, ids in members.items()}
    for name in sorted(unique):
        if not unique[name]:
            raise Refusal(
                Reason.STRATUM_EMPTY,
                f"Stratum {name!r} is declared in the plan but no frame unit is in it.",
                "Remove the stratum from the plan, or supply a frame that has "
                "units in it. This sends you to the frame; STRATUM_UNSAMPLED "
                "would send you to the sample.",
            )

    strata = tuple(
        Stratum(name=name, size=len(unique[name]), variance_proxy=declared[name].rate)
        for name in sorted(unique)
    )
    assert plan.allocation_rounding is not None  # required under stratified
    allocation = allocate(strata, plan.sample_size, Rounding(plan.allocation_rounding))
    per_stratum = dict(zip(allocation.strata, allocation.units, strict=True))

    drawn = draw_stratified(unique, seed=plan.seed, allocation=per_stratum)
    for name in sorted(drawn):
        if not drawn[name]:
            # Unreachable while ALLOCATION_TOO_THIN holds the floor at 2, and
            # kept because that floor is Q2's ruling rather than an invariant of
            # this function. If the floor is ever relaxed, this is the honest
            # code: it sends the operator to the sample, not the frame.
            raise Refusal(
                Reason.STRATUM_UNSAMPLED,
                f"Stratum {name!r} received no sampled units.",
                "Raise sample_size, or merge this stratum into a neighbour.",
            )

    total_rows = seen_rows
    total_unique = sum(len(ids) for ids in unique.values())
    frame_digest = ws.write_json("frame.json", {name: unique[name] for name in sorted(unique)})
    record = stratified_sample_record(
        plan.plan_hash, plan.seed, total_unique, drawn, allocation.as_record()
    )
    drawn_ids = tuple(str(i) for i in cast("list[str]", record["item_ids"]))
    sample_digest = ws.write_json("sample.json", record)

    ws.ledger.append(
        "sample",
        {
            "frame_digest": frame_digest,
            "sample_digest": sample_digest,
            "frame_rows_read": total_rows,
            "frame_unique_ids": total_unique,
            "n": len(drawn_ids),
            "design": "stratified",
            "strata": len(strata),
            "population_declared": plan.population,
            "population_used": str(frame_path),
        },
    )
    return drawn_ids


def _read_stratified_frame(path: Path) -> list[tuple[str, str]]:
    """(item_id, stratum) per row. Q13 / D-39: the frame says which unit is where.

    A `.txt` frame carries no stratum column, so **every** unit in it is
    undeclared. That lands on `STRATUM_UNDECLARED` rather than a code of its own:
    same artifact to open, same remedial act, and the direction travels in the
    detail text. D-22, and PLAN_THRESHOLD_INVALID's precedent.
    """
    if not path.exists():
        raise Refusal(
            Reason.EMPTY_SAMPLE,
            f"No population frame at {path}.",
            "Point the plan's `population` at a CSV with `item_id` and `stratum` columns.",
        )
    if path.suffix.lower() != ".csv":
        raise Refusal(
            Reason.STRATUM_UNDECLARED,
            f"{path.name} is not a CSV, so it carries no `stratum` column and no "
            "frame unit is in a declared stratum.",
            "A stratified design needs a CSV frame with `item_id` and `stratum` "
            "columns. A plain id list cannot say which unit is in which stratum.",
        )
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        columns = reader.fieldnames or []
        if "stratum" not in columns:
            raise Refusal(
                Reason.STRATUM_UNDECLARED,
                f"{path.name} has no `stratum` column, so no frame unit is in a "
                f"declared stratum. Columns found: {', '.join(columns) or 'none'}.",
                "Add a `stratum` column naming, for each unit, which stratum it "
                "belongs to. The names must match the plan's `strata` block.",
            )
        # Both readers strip, for V-7's reason: " item-1" and "item-1" are one
        # unit, and two readers disagreeing about that is the same defect as
        # silence about de-duplication.
        rows = [(str(r["item_id"]).strip(), str(r["stratum"]).strip()) for r in reader]
    return [(i, s) for i, s in rows if i]


def _read_frame(path: Path) -> list[str]:
    if not path.exists():
        raise Refusal(
            Reason.EMPTY_SAMPLE,
            f"No population frame at {path}.",
            "Point the plan's `population` at a file with one item id per line, "
            "or a CSV with item_id.",
        )
    # Both readers strip. They used to disagree, so " item-1" was two distinct
    # population members from a CSV and one from a text file. V-7.
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8") as fh:
            rows = [str(r["item_id"]).strip() for r in csv.DictReader(fh)]
    else:
        rows = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    return [r for r in rows if r]


def _read_labels(path: Path, label_field: str) -> dict[str, tuple[str, str]]:
    """item_id -> (label value, content). Content is sealed immediately after."""
    if not path.exists():
        raise Refusal(
            Reason.LABELS_UNMATCHED,
            f"No labels file at {path}.",
            "Point the plan's `labels` at a CSV or JSONL with item_id and your label column.",
        )
    rows: dict[str, tuple[str, str]] = {}
    if path.suffix.lower() == ".jsonl":
        records = [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    else:
        try:
            with path.open(newline="", encoding="utf-8") as fh, _wide_csv_fields():
                records = list(csv.DictReader(fh))
        except csv.Error as exc:
            # V-11. D-19 moved this cliff from 128 KiB to 64 MiB; it did not remove
            # it. A field past the ceiling raised the identical bare `_csv.Error`
            # that D-19 was opened to get rid of, 512x further out. Same class as
            # F-1: a real input producing a library traceback instead of a refusal.
            raise Refusal(
                Reason.CONTENT_TOO_LARGE,
                f"A field in {path.name} is larger than this tool will read "
                f"({_CSV_FIELD_LIMIT:,} bytes).",
                "Split the oversized row, or store that item's content in a separate "
                "file and reference it. The limit is deliberate: it stops a runaway "
                "file exhausting memory.",
            ) from exc

    for r in records:
        if "item_id" not in r or label_field not in r:
            raise Refusal(
                Reason.LABELS_UNMATCHED,
                f"A label row is missing 'item_id' or '{label_field}'.",
                f"Every row needs an item_id and a {label_field} column.",
            )
        rows[str(r["item_id"])] = (str(r[label_field]), str(r.get("content", "")))
    return rows


@contextmanager
def _wide_csv_fields() -> Iterator[None]:
    """Let a CSV field hold a whole piece of content.

    `csv` caps a single field at 128 KiB and raises a bare `_csv.Error` past it.
    Trust & Safety content routinely exceeds that -- a long post, a transcript, a
    thread -- and this tool chunks content precisely so size is not a limit. A
    library default is not a reason to refuse an operator's data, and a raw
    `_csv.Error` is not a refusal.

    Restored afterwards: this is process-global state and this tool does not get
    to leave it changed for whatever else is running.
    """
    previous = csv.field_size_limit()
    csv.field_size_limit(_CSV_FIELD_LIMIT)
    try:
        yield
    finally:
        csv.field_size_limit(previous)


def content_digest_of(text: str) -> str:
    return digest_bytes(text.encode("utf-8"))


def manifests_from(entry_body: dict[str, JSONValue]) -> list[Manifest]:
    seals = entry_body["seals"]
    assert isinstance(seals, list)
    return [Manifest.from_record(s) for s in seals]
