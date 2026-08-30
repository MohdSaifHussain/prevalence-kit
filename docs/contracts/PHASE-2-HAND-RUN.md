# Phase 2 — the director's hand-run

**Date:** 31 August 2026 (IST) · **Checklist:** `docs/contracts/PHASE-2-CONTRACT.md` §8a,
**34 rows** · **Tree:** `bfe0edd` · **Status: the reading. The phase outcome is a separate ruling.**

**This file is a dated reading and is never edited.** Corrections to it go in
`docs/CORRECTIONS.md` with the date and the direction the number moved. It records what happened
when the director ran the checklist, not what the checklist should have said.

**Run by the director, every command by his own hand**, exit codes read from `$LASTEXITCODE`.
The reviewer prepared the inputs in a fresh folder outside the repository and tested every command
before it was typed. Evidence: `C:\Users\mohds\pk-handrun-20260830\TRANSCRIPT.txt`, whose ledger
stamps sit inside `bfe0edd`.

**Result: 32 of the 34 rows behaved as §8a states. Two did not, and both are defects in the
checklist rather than in the tool** — though one of them led to a defect in the tool that nothing
else had found.

**The row count in this header is 34 because it was counted.** An earlier figure of 26 was carried
into `CLAUDE.md`, into the reviewer's handoff and into the director's report of this run, and
**nobody counted until the reviewer did**. `docs/CORRECTIONS.md` **C-45** carries it, direction up.

---

## What the 32 confirmed

Named rather than summarised, because *"32 of 34 passed"* is the kind of sentence this project has
spent forty-seven corrections learning not to write.

| Row | What the director saw |
|---|---|
| **F1** | The R witness reproduces **Barnett Table 2B** — `2098 / 828 / 584 / 256 / 234`, VVR `0.20%`, SD `0.054 pp`, exit 0 — and **the tree was unchanged afterwards**, which he checked separately |
| **F2** | Four fixture commits precede their estimator commits, including `e04a7aa` before `eb17c9a` |
| **F3** | A stratified plan hashes, exit 0 |
| **F5, F6, F8h** | Agreement against the R fixtures, base R `binom.test`, and the `svy` design fixtures |
| **F7, F8, F8b, F8c, F8d** | The Rogan-Gladen refusals and the two accepts, including the clamp disclosure and the raw bound in the ledger |
| **F8e, F8f, F8g** | The plan-level refusals for undeclared rounding, a missing `interval`, and strata-less stratified |
| **F10, F10b** | `STRATUM_EMPTY` and `STRATUM_UNDECLARED`, the complete pair |
| **F11** | The Rogan-Gladen positive control |
| **F17, F18** | **`EVIDENCE_NOT_PREREGISTERED` at both `sample` and `ingest-labels`**, both naming the resolved paths. *One guard is not two*, and both are guards |
| **F19** | The `ESTIMATE_METHOD_MISMATCH` pair, all selected tests passing |
| **F20, F21** | `INTERVAL_UNDEFINED`, and the no-interval notice **stated rather than refused** (D-41) |
| **F22, F23** | The coverage block on an SRS run; the one-stratum disclosure |
| **F24** | Both vocabulary refusals, each teaching why |
| **F25** | **`verify` says `per stratum` on the stratified run and `as a simple random sample` on the SRS run.** The row the checklist did not have until the director added it |
| **F25b** | The redraw's negative control |
| **F12** | **721 passed** |
| **F13** | `ruff check`, `ruff format --check`, `mypy --strict src` (**14 files**), `mypy` (**36 files**) |
| **F14** | Selftest **12/12**; `check_claims` reconciled, **30 findings** |
| **F16** | The R image digest identical to `docs/STANDARDS.md` |
| **F15** | Five tripwires reported, TW-4 fired. **The results matched and the row is incomplete**: it states no exit code, and `--check` exits **1** while a tripwire is fired. Counted here as behaving as stated, with the gap recorded below |

**That is 31 rows named in this table plus F15, which is 32.** F4 and F9 are the two below.

**F17 and F25 are the two rows that did not exist a day earlier**, and both came from someone
reading the checklist against what the tool actually does — the builder for F17, the director for
F25.

---

## The two rows that did not behave as stated

### H-1 — F4 expects per-stratum figures the report has never carried

**Severity: the row is wrong. What it led to is high, and it is now an accepted register finding.**

**What the director found.** His two-stratum run rendered `5 of 100 sampled items were positive`
and **nothing by stratum**. `report.json` carries only `"strata": 2`; the allocation `[27, 73]`
exists only in `sample.json`. Three of F4's four required items were present; the fourth was not.

**The answer: §8a's row is wrong.** The phrase came from §8's original F4 — *"do the per-stratum
figures look sane?"* — written while the stratified path still refused and no such report could
exist. The builder restated it in the new row **without deriving it from a rendered report**. A
carried expectation, which is the carried-number defect applied to an expected result.

**And investigating it found a defect in the tool that nothing else had.** For both design
interval builders, `positives` is `round(point * n)` — a back-computation from the design-weighted
estimate, **not a count of anything**. Reproduced by the builder on a two-stratum run at `bfe0edd`:

| | |
|---|---|
| Positive labels actually in `labels.csv` | **5 of 100** |
| `report.md` | `3 of 100 sampled items were positive` |
| `report.json` → `estimate.positives` | `3` |
| `round(0.025554 x 100)` | `3` |
| `verify` | **nine checks, exit 0** |

**It reaches two artifacts, not one.** The reviewer found a second instance in this run's own
evidence file: the director's console printed `n 100  (5 positive)` from `estimate` while his
`labels.csv` holds **10** positives. So the false count is in the **estimate output** and
`estimate.json` as well as in the report, and any fix must cover all three.

**The one-stratum run's agreement is structural, not evidence.** At `L = 1` the design estimate is
the pooled proportion, so `round(point * n)` equals the true count by construction. A test built on
a one-stratum case would have passed while the defect stood.

`verify` agrees because it recomputes through the same estimator that produced the number — the
**seventh instrument-limit kind, third live occurrence**. The SRS path is unaffected: `wilson` and
`clopper_pearson` carry the real count.

**This is C-16's class.** A false line in the artifact an outsider reads, every check green, found
by a person reading the output. **The director found it by running a row that was wrong about
something else**, which is an argument for hand-runs that no test can make.

**Ruled 31 August 2026: accepted as a register finding, severity high.** The disposition, as
ruled: the report carries the **true positive count** and a **per-stratum block** — n, positives
and weight per stratum — which makes F4's expectation right rather than making the row wrong; the
console estimate line and `estimate.json` carry the true count too; and **the closing test anchors
on labels the estimator cannot back-compute**, a case where the true count and `round(point * n)`
differ, like the director's 10 against 5. A corrections entry follows for the shipped false count.
**The fix is a separate commit and nothing was changed for this reading.**

*The register number is deliberately not written here. `check_register` requires a row for any
finding id named in any document, and `check_findings` fails the gate for a row whose status is
`open` — so the id attaches when the fix commit closes it. That the register cannot hold an
accepted-but-unfixed finding, while its own status vocabulary defines `open` as exactly that, is
recorded as an observation about the instrument rather than smuggled into this reading.*

### H-2 — F9 names a refusal no command can produce

**Severity: the row is wrong. The preamble that vouched for it was an overclaim.**

**What the director found.** A plan allocating a stratum zero units refuses
**`ALLOCATION_TOO_THIN`** at `sample` — Q2's floor — not `STRATUM_UNSAMPLED`. The only route to
that code is `stratified_estimate` called directly, through
`test_an_unsampled_stratum_is_refused_by_name`, which he ran: 1 passed. **The reviewer reached the
same conclusion independently, by probing, before the builder answered.**

**The answer: no command produced it, and none can.** `src/prevalence_kit/run.py:559-562` says so
in its own comment — the branch is unreachable while `ALLOCATION_TOO_THIN` holds the floor at 2,
and is kept because that floor is **Q2's ruling rather than an invariant of the function**. The row
should be restated as a test-only row like F19, naming the test and the reason the CLI path does
not exist.

**The larger finding is the preamble.** §8a says *"Every command below was run before it was
written here."* That is **true of the rows written new** — F17, F18, F10b, F20, F21, F22, F23, F24,
F25, F25b, F2, F4's chain, F12 to F14 — and **false of every row carried unchanged from §8**: F1,
F5, F6, F7, F8, F8b to F8g, F9, F10, F11, F15, F16, F8h. Those were not re-run.

**C-27's shape, in the preamble of the document the director then ran against.** A sentence whose
verifiable half made the unverifiable half ride along, and *"every command"* is exactly the
construction that stops a reader asking which ones.

**Both accuracy notes below fall inside that carried set**, which is what the shape predicts.

---

## Two accuracy notes — for the record, not for action

Raised by the director as accuracy rather than as defects. Both confirmed by the builder.

1. **F19's selector picks three tests, not two.** `-k "method_contradicts or method_matches"` also
   matches `test_the_expected_method_matches_what_the_estimator_stamps` in
   `tests/test_correction_plan.py`. All three pass. The row says *"Both pass."*
2. **`tools/check_tripwires.py --check` exits 1 while TW-4 is fired.** F15 states no exit code.
   Offline it exits 0. **The exit 1 is the tripwire working, not a failure** — it is a phase-close
   ritual and a decision for the director, never a CI job, which is why it is not in the gate.

---

## What this reading establishes, at the width of the evidence

**The tool did what the contract says it does, on evidence the director produced himself.** Every
refusal that has a command fired with its own code and exit 2. Every positive control passed. The
gate is green on his machine at the same numbers CI reports.

**What it does not establish.** Two of the thirty-four rows described a tool that does not exist —
one expecting output the report has never had, one naming a refusal no command can reach. **Neither
was caught by any instrument in this project**, and both were caught within an hour by people
running the list. The checklist was the builder's, and this is the **third time in this phase** that
the thing needing an outside reader was **the builder's description of its own work** rather than
the work: **C-38** (the claim in a commit message), **C-34** (a checker stating a scope it did not
have), and **§8a's preamble**.

**And one defect in the tool came out of it** — a false count in the flagship artifact and in two
other places, reached through a row that was wrong about something else entirely.

---

## Open at this reading

| # | What | Owner |
|---|---|---|
| **H-1** | Accepted as a register finding, **high**, with its disposition ruled. The design-interval `positives` is back-computed and stated as a count in the report, the console and `estimate.json`. F4's row also needs restating | **Fix is a separate commit** |
| **H-2** | F9 restated as a test-only row, and §8a's preamble narrowed to what was actually re-run | **Builder, on the director's ruling** |
| **The register's `open` state** | `check_findings` fails the gate for any `open` row, so an accepted-but-unfixed finding cannot be recorded. Observation, not a proposal | **Director** |
| **Phase 2 outcome** | Not closed. §11 is written and the director's ruling on it is separate from this reading | **Director** |
