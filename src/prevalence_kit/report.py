"""The stamped report: Markdown for a person, JSON for a machine.

A report carries the number, the interval, the design, n, every hash in the
chain, and an Honest Limits block. The limits are not a footer -- they are a
deliverable, asserted present by test, and they carry the charter's section 8
wording so a reader of the report gets the same caveats as a reader of the
repository.

`report` is the one repeatable step (D-17). Re-emitting cannot change the number
-- the estimate is already sealed and chained -- and each emission appends its
own ledger entry, because a record of every emission is something an auditor
wants rather than something to forbid.

Plain ASCII throughout. Reports are where em-dashes and smart quotes get typed,
and an operator's console is not guaranteed to be UTF-8.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from .canonical import JSONObject, digest
from .coverage import DESIGN_GRID, MEASURED_N, NOTICE_THRESHOLD, disclosure
from .errors import Reason, Refusal
from .ledger import Entry
from .plan import Plan
from .run import Workspace

HONEST_LIMITS = (
    "It measures prevalence of labeled samples from a defined population. It cannot fix a "
    "bad sampling frame, biased labels, or a dishonest plan. It can only make them visible "
    "and permanent in the record.",
    "The interval is a SAMPLING interval. It does not account for rater quality. This is the "
    'same caveat YouTube publishes for its Violative View Rate: "The confidence intervals do '
    'not take into account rater quality, which may impact our measurements."',
    "This version relies on the sensitivity and specificity you provide, if you provide them. "
    "It does not estimate rater quality itself.",
    'No EU regulation requires this number. The word "prevalence" appears zero times in '
    "Regulation (EU) 2022/2065 and zero times in Implementing Regulation (EU) 2024/2835.",
    "Validation is on synthetic data and one public dataset. No claim of production deployment.",
    "Built by directing an AI under a governed process. The director wrote none of the code "
    "and all of the decisions.",
)
"""Carried forward unchanged from PROJECT_CHARTER.md section 8.

Narrowed only when a limit genuinely narrows, and never deleted for being
inconvenient. `tests/test_report_and_cli.py` asserts every one of these reaches
the rendered report.
"""


def build(ws: Workspace, plan: Plan) -> JSONObject:
    """Assemble the report from the record. Refuses if the chain is incomplete."""
    entries = ws.ledger.verify()
    by_step = {e.step: e for e in entries}
    if "estimate" not in by_step:
        raise Refusal(
            Reason.LEDGER_BROKEN,
            "This run has no estimate yet, so there is nothing to report.",
            "Run `estimate` first.",
        )

    estimate = ws.read_json("estimate.json")
    sample = by_step["sample"].body
    return {
        "tool": "prevalence-kit",
        "emitted_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "estimand": {
            "description": plan.estimand.description,
            "label_field": plan.estimand.label_field,
            "positive_when": plan.estimand.positive_when,
            "threshold": plan.estimand.threshold,
        },
        # F-11: the population the run ACTUALLY sampled, taken from the ledger.
        # This used to read `plan.population` -- the commitment -- so a run drawn
        # from another file printed the pre-registered filename beside a number
        # computed from a different one, in the artifact an outsider reads.
        # The check in `do_sample` means they cannot differ now; the report takes
        # the value from the record anyway, because the record is what happened.
        # Older runs have no such field and fall back to the plan, labelled.
        "population": sample.get("population_used", plan.population),
        "population_declared": plan.population,
        "design": plan.design,
        "seed": plan.seed,
        "frame_rows_read": sample.get("frame_rows_read"),
        "frame_unique_ids": sample.get("frame_unique_ids"),
        # O-27 / D-38. How many strata the design actually had, read from the
        # record rather than from the plan, for F-11's reason: the report states
        # what happened. `None` for an SRS run and for runs made before the
        # field existed.
        "strata": sample.get("strata"),
        # D-41. The odds this design produced no interval at all, as computed and
        # recorded at `sample`, before the labels were paid for.
        "probability_no_interval": sample.get("probability_no_interval"),
        # O-25 / D-37 condition 3. What the chosen interval's confidence level
        # actually delivers, at the nominal level this run used.
        "coverage": disclosure(
            str(plan.interval),
            str(estimate["confidence"]),
            str(estimate["point"]),
            int(str(estimate["n"])),
        ),
        "estimate": estimate,
        "chain": [
            {"seq": e.seq, "step": e.step, "at": e.at, "entry_digest": e.entry_digest}
            for e in entries
        ],
        "plan_hash": str(by_step["plan"].body["plan_hash"]),
        # The count a reader will get from `verify` after this report is emitted.
        # Without it the report lists N entries, `verify` reports N+1, and the
        # report itself tells the reader to go and run `verify`. The flagship
        # output would be sending an auditor to a command that contradicts it.
        # C-16.
        "entries_verify_will_report": len(entries) + 1,
        "honest_limits": list(HONEST_LIMITS),
    }


def render_markdown(report: JSONObject) -> str:
    """The version a person reads. Plain English, per the charter's writing rule."""
    est = report["estimate"]
    assert isinstance(est, dict)
    estimand = report["estimand"]
    assert isinstance(estimand, dict)
    chain = report["chain"]
    assert isinstance(chain, list)

    point = _percent(str(est["point"]))
    low, high = _percent(str(est["low"])), _percent(str(est["high"]))

    # The level the estimator actually used, read from the record. This line
    # said "95%" as a constant until O-25. Nothing reached it, because the CLI
    # takes the default and the default is 0.95 -- which is exactly what made it
    # worth fixing: a recorded field the artifact does not read is F-10's shape,
    # and the day a plan carries `confidence` the report would have printed the
    # wrong level beside the right bounds.
    level = _confidence_label(str(est["confidence"]))

    lines = [
        "# Prevalence report",
        "",
        f"**{point}**  ({level} interval {low} to {high})",
        "",
        f"{est['positives']} of {est['n']} sampled items were positive.",
        "",
    ]

    # O-23 / D-32 condition 2. A clamped bound is a CONSTRUCTION, not a
    # measurement, and a reader comparing two of this tool's intervals has no
    # way to tell unless it says so. The director's words: a silently clamped
    # bound is a small lie in the artifact an outsider reads.
    #
    # Placed immediately under the interval rather than in a footnote, because
    # the sentence is about the number directly above it. The raw bound is
    # quoted so the reader can see what the arithmetic produced before policy
    # touched it -- condition 3, which the ledger already carries.
    if est.get("clamped"):
        clamped = est["clamped"]
        assert isinstance(clamped, list)
        for end in clamped:
            raw = est["low_raw"] if end == "low" else est["high_raw"]
            limit = "0" if end == "low" else "1"
            lines += [
                f"> **The {end} bound is a construction, not a measurement.** The "
                f"arithmetic produced {raw}, which is outside [0, 1], and a "
                f"prevalence cannot be. It is shown as {limit}. The raw value is "
                f"in the record, and `verify` re-derives both.",
                "",
            ]

    lines += [
        "## What was measured",
        "",
        f"- **Estimand:** {estimand['description']}",
        f"- **Positive when:** `{estimand['label_field']}` "
        f"{estimand['positive_when']} `{estimand['threshold']}`",
        f"- **Population:** {report['population']}",
        f"- **Design:** {report['design']}, seed `{report['seed']}`",
    ]
    if report.get("frame_rows_read") is not None:
        lines.append(
            f"- **Frame:** {report['frame_rows_read']} rows read, "
            f"{report['frame_unique_ids']} unique items sampled from"
        )
    lines += [
        f"- **Interval method:** {est['method']}",
    ]
    if est.get("sensitivity") is not None:
        lines.append(
            f"- **Corrected for label quality:** sensitivity {est['sensitivity']}, "
            f"specificity {est['specificity']} (Rogan-Gladen). The uncorrected "
            f"apparent prevalence was {_percent(str(est['apparent']['point']))}."
        )
    lines += _one_stratum_disclosure(report)
    lines += _coverage_block(report, level)
    lines += [
        "## The record",
        "",
        f"Pre-registration hash: `{report['plan_hash']}`",
        "",
        "| # | Step | Recorded at | Entry digest |",
        "|---|---|---|---|",
    ]
    for link in chain:
        assert isinstance(link, dict)
        lines.append(
            f"| {link['seq']} | {link['step']} | {link['at']} | "
            f"`{str(link['entry_digest'])[:16]}` |"
        )
    lines += [
        "",
        f"**This is the chain as at emission: {len(chain)} entries.** Emitting this report "
        f"appends one further entry, so `prevalence-kit verify` on this run will report "
        f"**{report['entries_verify_will_report']} entries**. A report cannot list its own "
        "emission; the difference is that entry, not a discrepancy.",
        "",
        "Anyone can re-check this with `prevalence-kit verify`. It redraws the sample and "
        "recomputes the estimate from the sealed record, rather than re-reading the numbers "
        "above.",
        "",
        "## Honest limits",
        "",
        "Read these before quoting the number.",
        "",
    ]
    limits = report["honest_limits"]
    assert isinstance(limits, list)
    lines += [f"- {limit}" for limit in limits]
    lines += ["", f"_Emitted {report['emitted_at']} by {report['tool']}._", ""]
    return "\n".join(lines)


def _one_stratum_disclosure(report: JSONObject) -> list[str]:
    """**O-27 / D-38.** A one-stratum stratified design says so, in the report.

    The ruling was *accept and disclose*, and the precedent it rests on is
    **D-21**: de-duplicating the frame was correct, and doing it silently was the
    defect. Accepting a one-stratum plan is correct -- both anchors admit
    `L = 1` -- so the silence is the only thing left that could be wrong.

    **Three statements, because the ruling names three** and the third is the one
    a reader would never derive: the point estimate of a one-stratum stratified
    design equals the SRS estimate, and **its variance does not**. At the shipped
    example's numbers the two paths give the same `0.225` and different bases.
    """
    if report.get("design") != "stratified" or report.get("strata") != 1:
        return []
    return [
        "",
        "> **This design has one stratum, so stratification gained you nothing.** "
        "Splitting a population into one group is the unstratified design with "
        "extra bookkeeping, and the record says so rather than leaving you to "
        "notice. The number is not wrong and the plan was followed exactly.",
        "",
        "> **The interval still rests on a stratified variance, not on a binomial "
        "inversion.** A one-stratum stratified estimate equals the simple random "
        "sample estimate at the point and **not** at the interval: the two paths "
        "compute different quantities from the same data. Do not compare this "
        "bound with a `wilson` or `clopper_pearson` bound as though they were the "
        "same construction.",
    ]


def _coverage_block(report: JSONObject, level: str) -> list[str]:
    """**O-25 / D-37 condition 3.** What the level on the box actually delivers.

    The plan records which interval the operator chose. **This records what that
    choice cost**, at the nominal level the run actually used.

    **It quotes a measurement and says what the measurement covers.** It does not
    compute coverage at this run's operating point, and the difference is stated
    in the report rather than left for a reader to assume -- Clopper-Pearson
    coverage at one true rate costs one root-find per possible outcome, 3.3
    seconds at n = 500 on this machine and growing, so a report that computed it
    would either be slow or would use a second construction that is not the one
    it shipped. **The bound is real and it is a bound**, which is the honest
    thing to hand someone.
    """
    block = report.get("coverage")
    if not isinstance(block, dict) or block.get("measured") is None:
        return []
    measured = float(str(block["measured"]))
    lines = [
        "",
        f"## What that {level} actually delivers",
        "",
        f"Measured, not asserted. Worst coverage for `{block['method']}` at a "
        f"nominal {level}: **{measured * 100:.2f}%**, at {block['measured_where']}.",
        "",
        "That is the worst value found on a *grid* of true rates, so the real "
        "worst is **at most** this and may be lower. It is rounded down rather "
        "than to nearest, because rounding a bound toward the middle claims a "
        "floor the measurement already breaks.",
        "",
    ]
    if block.get("is_design_based"):
        lines += [
            "**Neither stratified interval holds its nominal level at rare "
            f"rates.** The figure comes from {DESIGN_GRID}. **It is not a "
            "measurement of your design**, which was not measured. Read it as "
            "what the method does in this regime.",
            "",
        ]
        odds = report.get("probability_no_interval")
        if odds is not None and float(str(odds)) >= NOTICE_THRESHOLD:
            lines += [
                f"**And this design had at least a {float(str(odds)) * 100:.1f}% chance "
                "of producing no interval at all**, computed from the plan before any "
                "labelling was paid for. It produced one. At rare rates that is the "
                "single most likely outcome rather than an edge case.",
                "",
            ]
    else:
        gamma = float(str(block["gamma"]))
        rate = "inside" if block.get("gamma_in_swept_range") else "outside"
        sizes = ", ".join(str(n) for n in MEASURED_N)
        size = (
            f"n = {block['n']}, one of the sizes measured"
            if block.get("n_was_measured")
            else f"n = {block['n']}, which is not one of the sizes measured ({sizes})"
        )
        lines += [
            f"**Where this run sits, on both axes.** True rate: gamma = p x n = "
            f"{gamma:.3f}, {rate} the swept range 0.5 to 15. Sample size: {size}.",
            "",
            "The figure above is what the method does at the sizes and rates that "
            "were measured. **It is not a coverage computed for this run, and none "
            "was computed.** Coverage oscillates with sample size, so a worst case "
            "at one n does not bound another.",
            "",
        ]
    return lines


def emit(ws: Workspace, plan: Plan, *, stem: str = "report") -> tuple[Path, Path]:
    """Write both forms and append a ledger entry. Returns (markdown, json)."""
    report = build(ws, plan)
    json_digest = ws.write_json(f"{stem}.json", report)

    markdown = ws.root / f"{stem}.md"
    text = render_markdown(report)
    _refuse_non_ascii(text)
    markdown.write_text(text, encoding="utf-8", newline="\n")

    ws.ledger.append(
        "report",
        {"report_digest": json_digest, "markdown_digest": digest(text), "stem": stem},
    )
    return markdown, ws.root / f"{stem}.json"


def _refuse_non_ascii(text: str) -> None:
    bad = [(i, c) for i, c in enumerate(text) if ord(c) > 127]
    if bad:
        raise Refusal(
            Reason.PLAN_INVALID,
            f"The report contains {len(bad)} non-ASCII character(s), first {bad[0][1]!r}.",
            'Reports must render on a default console. Use -- for a dash and " for quotes.',
        )


def _percent(decimal_string: str) -> str:
    """0.225000000000 -> 22.500%. Three decimal places holds rare-event rates."""
    return f"{float(decimal_string) * 100:.3f}%"


def _confidence_label(decimal_string: str) -> str:
    """0.950000000000 -> 95%. A header wants the level, not twelve places of it.

    Trailing zeros are stripped rather than a fixed width chosen, so 0.995 reads
    as 99.5% instead of being rounded into a level nobody asked for.
    """
    text = f"{float(decimal_string) * 100:.6f}".rstrip("0").rstrip(".")
    return f"{text}%"


def last_report(ws: Workspace) -> Entry | None:
    return next((e for e in reversed(ws.ledger.verify()) if e.step == "report"), None)
