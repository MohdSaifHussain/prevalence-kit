# Corrections

Every claim that was wrong, who it came from, how it was caught, and what replaced it.

**The point of this table is that it is uncomfortable to write.** A project that claims its numbers
are checkable has to show the ones that were not. Errors are counted by source, separately, so
neither the director nor the AI can quietly absorb the other's.

**Source attribution is the director's, given at ratification**, and is recorded as given.

**The `Director` row read 0 through thirty-one entries and now reads 1 — C-32.** A table that
counts the builder's errors and never the director's is not measuring honesty; it is measuring
who writes the entries. The director raised that one himself and asked for it to be counted.

---

## Counts

| Source | Open | Closed | Total |
|---|---|---|---|
| Chat reviewer (draft author) | 0 | 3 | **3** |
| Research report (passed through unverified) | 0 | 2 | **2** |
| Stale-at-draft-time, queued but built on anyway | **1** | 0 | **1** |
| **Builder (Claude Code)** | **4** | **33** | **37** |
| Reviewer instrument | **1** | **2** | **4** (1 noted) |
| **Director** | 0 | **1** | **1** |
| Tool artifact (noted, not a defect) | - | - | **1** (noted) |
| **Total** | **6** | **41** | **49** |

**Derived, and now checked — 2026-08-30.** Every figure above is computed from the entry blocks in
this file rather than incremented as rows arrived. An earlier version said 36 open and 3
reviewer-instrument, and both were over by one: **C-36**.

**`check_claims`' `counts` check enforces it from D2.14(b).** The semantics below are its
specification, and the Total row failing against the entries is now a red gate rather than
something a reader has to add up. It fired on its first run, on the two rows C-40 and C-41 added.

### What these columns mean, written down so nobody has to re-derive them

**This is D2.14(b)'s specification.** The check is still owed; the definition is not, and the
ambiguity below is what produced C-36.

| Term | Definition |
|---|---|
| **An entry** | One `## C-n` or `## V-n` heading in this file. **Three corrections carry `V-` numbers** — V-13, V-14, V-15 — because they were found as review findings and recorded here as wrong claims. They count in this table exactly like a `C-`; the letter records where they were found, not what they are |
| **Total** | Entries with that source. **Not class instances** |
| **Open** | Entries whose `Status` row is `OPEN`. They close under **T-1 (D2.12)**, each naming its discharging commit |
| **Closed** | `Status` is neither `OPEN` nor `noted`. **Zero so far, and the zero is real** — nothing has been closed yet |
| **noted** | A permanent record that is not a defect to fix. Two: **C-18** (a ruff artifact, not this project's defect) and **C-21** (a reviewer-instrument accident that demonstrated a gate firing). Counted in Total, excluded from Open |
| **Source** | The `Source` row, bucketed. A source row naming the director as the person who *caught* something is **not** a director-sourced entry — C-18 says "the director's own hand-run" and belongs to *Tool artifact* |

**The distinction that C-36 turned on, and the one to hold on to:**

> **A class tally and this table count different things.** The *Classes* section below tracks every
> instance of a pattern **including ones that never got a C-number**, and says so per row. This
> table counts **entries**. C-21's own text reads *"Second recorded instance; fifth overall in the
> class"* — two numbers in one sentence, measuring two different populations. **Reading the class
> figure into the table is the most likely way the reviewer-instrument row reached 3.**

**And the scope, restated from the header because it is the question that keeps arising:** this
table counts claims that **reached a commit, or changed a ruling**. A finding in
`docs/FINDINGS.md` and a correction here are **not double-counting** — the finding is the defect,
the correction is the sentence that defect put into a commit. **F-9 and C-35 are one such pair**,
and the question of whether they were double-counted came up twice in two days, which is why the
definition is now written rather than ruled again.

C-1 … C-6 are Phase 0: defects in the chat-drafted vision, all caught before any code, none reaching
an artifact. **C-7 … C-13 are Phase 1, and all seven are mine.** Five were caught by the director's
reviewer and two by the director; **none was caught by my own review stop**, which is the measurement
of the limit I raised as Q2 rather than a separate finding.

**C-12 and C-13 are a different kind from the rest.** C-7 to C-11 are wrong statements. C-12 and
C-13 are wrong *reporting* — the statements were accurate and the omissions made them mislead. That
class does not show up by re-deriving a number, only by reconciling a report against the artifact.

**What this table counts, and it matters because the count gets quoted.** It counts claims that
**reached a commit, or changed a ruling**. It does not count errors caught while working -- a wrong
sentence noticed and rewritten before it was committed is ordinary work, not a correction.

**The second half was added 2026-08-29, and it widened the scope.** The builder judged that a
sentence which never reached a commit needed no entry. The director overruled it: *"A claim that
never reached a commit but did reach a director's ruling has done more damage than one sitting
unread in a file."* C-25 is the instance. Rulings are in the record too, so the widened scope is
still something the table can be checked against.

Without that line the number is ambiguous the first time someone else reads it, and nobody could say
which kind it is or compare it with its own history. Ruled 2026-08-29, when a wrong claim about
rounding was caught before commit and deliberately **not** given a C-number. The class it belongs to
is still tracked, below.

Entries stay **open** until the corrected text is committed and verified.

**T-1 (D2.12) ran 2026-08-30 and closed 41 of the 44.** Each closed entry names
**the commit that discharged it**, derived rather than guessed: the Phase 0 vision
defects were discharged by the charter's ratification `5b4f97f`; anything closing
*at phase close* or *at the Phase 1 to 2 boundary* by Phase 1's close `d66d225`;
and the rest by the commit that made the fix. Every hash was checked to exist
before it was written down.

**One stays open, and it is not an oversight.** **C-1** closes when the README
credits `svy` as the estimator layer, and there is no README yet -- that is Phase
3. **C-18 and C-21 stay `noted`**, which is a permanent state rather than an
unfinished one.

**C-9 was the one that could not simply be marked.** Its condition was *closes when
O-4 is discharged and the sentence can be rewritten as a fact*. O-4 discharged at
D2.9 -- and the shipped package docstring still read *"is not yet done"*, which had
become false in the other direction. T-1's bookkeeping is what surfaced it. The
sentence is now the fact, at the width of the evidence and no wider.

---

## C-1 — svy's installable code was "not yet publicly downloadable"

| | |
|---|---|
| **Claimed** | Vision §8 TW-2: *"the review found svy's installable code was not yet publicly downloadable — so v1.0 defaults to `lean` estimators"* |
| **Actually** | `pip install svy==0.25.0` succeeded in a clean venv on 2026-08-28. Wheel and sdist both on PyPI. Version 0.25.0 uploaded **2026-08-26**, two days before the check. 48 releases. |
| **Source** | **Stale at draft time.** Installability was queued as a ruling item, and TW-2 was built on the stale finding anyway rather than waiting for the ruling. |
| **Caught by** | Phase 0 verification, by execution — installing it, not reading about it |
| **Severity** | **High.** It was the load-bearing premise under a tripwire and under the whole `lean`-estimator plan. |
| **Replaced by** | D-2 — `lean` retained, with the `httpx` zero-network dependency as the recorded rationale. Availability argument retired. TW-2 rewritten with a corrected baseline. |
| **Second finding, same check** | svy already implements Neyman allocation, Wilson, Clopper-Pearson, Korn-Graubard, logit intervals, Taylor variance, post-stratification and raking — most of the planned Phase 2. Positioning corrected in D-4. |
| **Status** | **OPEN** -- closes when the README credits `svy` as the estimator layer -- **Phase 3**, and there is no README yet. Its condition is unmet rather than overlooked|

**The process lesson, and it is the one worth keeping.** A finding was queued for a ruling *and*
relied upon before the ruling came. That is the failure mode, not the stale fact. A claim awaiting a
ruling is not available for use as a premise.

---

## C-2 — "The timing is regulatory, and it is now"

| | |
|---|---|
| **Claimed** | Vision §2: *"EU DSA Implementing Regulation 2024/2835 requires harmonized transparency reports with accuracy indicators... There is no official tooling to compute those numbers."* Framed as regulatory demand for prevalence. |
| **Actually** | The word **"prevalence" appears zero times** in Regulation (EU) 2022/2065 and **zero times** in Implementing Regulation (EU) 2024/2835. No EU regulation requires a platform to report prevalence. What 2024/2835 mandates is accuracy, precision and recall of automated moderation. |
| **Source** | **Chat reviewer's draft** |
| **Caught by** | Phase 0 verification — mechanical count over both full official texts, retrieved from the EU Publications Office and corroborated against the director's own EUR-Lex PDF |
| **Severity** | **High.** Trivially falsifiable in one search, in a document whose whole premise is verifiability. |
| **Replaced by** | D-5 — inverted positioning: regulation mandates sensitivity/specificity; prevalence-kit shows what those do to the estimate |
| **Status** | **CLOSED** -- discharged by `5b4f97f`: the charter's inverted regulatory positioning, D-5|

---

## C-3 — "Wilson / Jeffreys ... matches Google's published practice"

| | |
|---|---|
| **Claimed** | Vision §4: *"Rare-event-safe intervals only (Wilson / Jeffreys ... this matches Google's published practice)"*, anchored on the Unofficial Google Data Science Blog, 2019 |
| **Actually** | Two errors. (a) The cited post **criticises** Jeffreys for this exact use case — it over-covers for rare events by shrinking toward 0.5 — and recommends the stratified Wilson interval. (b) The blog is **self-declared unofficial**, and the project's own Hard Rule 3 forbids sourcing a method from a tutorial. |
| **Source** | **Chat reviewer's draft** |
| **Caught by** | Phase 0 verification, reading the cited post. The **director independently flagged the source's provenance** in the same session, before seeing the finding. |
| **Severity** | Medium as statistics; **high as a rules breach** — the spine was broken on the first technical page. |
| **Replaced by** | D-8 — anchor Brown, Cai & DasGupta (2001), *Statistical Science*, DOI `10.1214/ss/1009213286`. Ship Wilson + Clopper-Pearson. Jeffreys dropped. Blog demoted to context. |
| **Status** | **CLOSED** -- discharged by `5b4f97f`: D-8's anchor: Brown, Cai & DasGupta, blog demoted to context|

*Provenance note for the record:* the domain was checked and is genuine Google infrastructure
(NS `ns-cloud-d1.googledomains.com`, Blogger IP block, `www` CNAME `ghs.google.com`, TLS from Google
Trust Services). Not a lookalike. Still unofficial. The rule bites on *official*, not on *real*.

---

## C-4 — "KDD '26"

| | |
|---|---|
| **Claimed** | Vision §2 and §6: the Pinterest paper is *"arXiv 2602.18518, KDD '26"* |
| **Actually** | The paper's own header targets *"The 33rd ACM SIGKDD Conference on Knowledge Discovery and Data Mining; **August 2027**; San Jose, CA, USA"*. Its DOI field is the unfilled ACM template placeholder `XXXXXXX.XXXXXXX`. arXiv carries no `journal_ref`. It is a preprint formatted for KDD **2027**, and acceptance is unproven. Also, **v2 (2026-08-17)** exists and the vision cites only the February v1. |
| **Source** | **Research report — passed through unverified** |
| **Caught by** | Phase 0 verification, arXiv API and the paper's HTML render |
| **Severity** | Medium. Asserts a peer-review status no source supports. |
| **Replaced by** | D-6 — cite as arXiv preprint 2602.18518v2 (2026-08-17), formatted for KDD 2027 |
| **Status** | **CLOSED** -- discharged by `5b4f97f`: D-6's corrected citation: arXiv 2602.18518v2, KDD 2027|

---

## C-5 — ROOST funding "$28M+"

| | |
|---|---|
| **Claimed** | Vision §2: *"ROOST (the major open-source T&S initiative, **$28M+** funding)"* |
| **Actually** | **The figure matches neither official ROOST source.** The launch press release (10 Feb 2025) says *"more than **$27 million** for its first four years of operations."* The ROOST blog post *First 100 Days* (4 June 2025) says *"an initial **$28.5 million** in funding **and in-kind contributions** from founding partners."* |
| **Source** | **Research report — passed through unverified** |
| **Caught by** | Phase 0 verification, launch release. The **second source, and therefore the conflict, was surfaced by the director** at ratification. |
| **Severity** | Low in magnitude; **the principle is the point.** Rounding a funding figure in a charter about verifiability is the exact failure the tool exists to prevent. |
| **Replaced by** | D-7 — cite the launch release with its date; footnote the blog figure; **record the conflict, do not resolve it** |
| **Status** | **CLOSED** -- discharged by `5b4f97f`: D-7: both ROOST figures recorded, conflict unresolved|

---

## C-6 — "Because every item is labeled, the TRUE prevalence is known"

| | |
|---|---|
| **Claimed** | Vision §7.3, describing the flagship coverage demonstration |
| **Actually** | Civil Comments labels are **`float32`** — `toxicity`, `severe_toxicity`, `obscene`, `threat`, `insult`, `identity_attack`, `sexual_explicit`, each the **fraction of human annotators** who applied it. **There is no binary ground truth in the dataset.** A "true prevalence" exists only relative to a threshold, and that threshold is our definitional choice. |
| **Source** | **Chat reviewer's draft** |
| **Caught by** | Phase 0 verification, reading the dataset schema rather than the dataset description |
| **Severity** | **High.** It would have sat on the README front page of a tool whose entire claim is that its numbers are checkable, asserting access to a ground truth that does not exist. |
| **Replaced by** | D-11 — pre-registered threshold estimand, hashed before data is touched; truth knowable **by census** at each threshold; demo extended to **multiple thresholds as a sensitivity curve** |
| **Status** | **CLOSED** -- discharged by `5b4f97f`: D-11's pre-registered threshold estimand|

**This correction improved the deliverable.** The float labels became the demonstration's main axis
rather than a caveat buried in it.

---

---

## C-7 — Two gate numbers I reported that do not reproduce

| | |
|---|---|
| **Claimed** | Phase 1 review stop, gate line: *"`mypy --strict` clean (16 files)"* and *"`ruff format --check` clean (29 files)"* |
| **Actually** | `mypy --strict src` — the command exit check **E12 actually specifies** — reports **10** source files, not 16. I had run `mypy` with the project config, which also checks `tests/`. And ruff's summary integer is not a file count at all: it reported 29, then 30 at the next commit whose only diff was a `.txt` and a `.md`, against **16** tracked `.py` files. |
| **Direction** | Both moved **against me**: I quoted a larger, more impressive number than the specified command produces, and quoted a second number that measures nothing. |
| **Source** | **Builder (Claude Code)** |
| **Caught by** | The director's reviewer, re-running the commands. Confirmed by me: `mypy --strict src` → 10; `ruff format --check .` → 30 against `git ls-files '*.py'` → 16. |
| **Severity** | Low in magnitude; the standing rule it breaks is not. *Numbers the director will repeat come from a run someone actually performed, stated with its conditions.* I had not performed the run I was quoting. |
| **Replaced by** | Gate evidence is now reported as **exit codes and the test count**, both re-derived per report. The file-count integers are not quoted at all. |
| **Status** | **CLOSED** -- discharged by `d66d225`: the Phase 1 close report ships exit codes and a re-derived count|

**Note on the dated document.** `docs/contracts/PHASE-1-REVIEW-STOP.md` is **not** edited. It is a dated
reading and stands as the honest record of what was believed on 28 August 2026. This entry is the
correction, per the standing rule.

---

## C-8 — A code comment cited a decision that did not exist

| | |
|---|---|
| **Claimed** | `sampling.py:18`: *"docs/DECISIONS.md D-17."* And `plan.py:9` cited `tests/test_plan.py::test_hash_does_not_need_the_data`. |
| **Actually** | `DECISIONS.md` held D-1 … D-15. There was no D-17 and no D-16 either — the code comment pre-empted the log by two numbers. `tests/test_plan.py` does not exist; the test is at `test_core.py:50`. |
| **Direction** | Both point at things that do not exist, so neither could mislead a reader into a wrong belief — they would simply fail to resolve. Still: a citation that cannot be followed is not a citation. |
| **Source** | **Builder (Claude Code)** |
| **Caught by** | The director's reviewer, by looking. Confirmed by me: `grep -cE '^## D-' docs/DECISIONS.md` → 15. |
| **Severity** | Low individually. As a class it is the standing rule *"verify a filename or entity exists before naming it"*, and three of the four record defects found were that rule. |
| **Replaced by** | The keyed-sort decision is now genuinely logged as **D-16**, and the comment points at it. `plan.py` points at `test_core.py`. |
| **Status** | **CLOSED** -- discharged by `d66d225`: `check_claims` citations and paths resolve every D-nn and path|

---

## C-9 — A present-tense validation claim in the shipped package docstring

| | |
|---|---|
| **Claimed** | `src/prevalence_kit/__init__.py`: *"The statistics **are validated** against R `survey` and Python `svy`."* |
| **Actually** | Neither cross-check exists. O-4 is open, the work is Phase 2, and D-18 has since narrowed it: `svy` is not a witness for Wilson at all, because its Wilson is a different estimator. |
| **Direction** | Against the evidence — the claim was wider than the artifact, in the one file that ships inside the package. |
| **Source** | **Builder (Claude Code)** |
| **Caught by** | The director's reviewer |
| **Severity** | Medium. Doctrine rule 7: claims at the exact width of the evidence. A package docstring is read by people who will never open the repository. |
| **Replaced by** | *"`svy` and R `survey` are the estimator layer; this package does not claim to replace them. Cross-validation against R `survey` is a Phase 2 obligation (O-4) and is not yet done."* |
| **Status** | **CLOSED** -- discharged by this commit: the package docstring rewritten as a fact, this commit|

---

## C-10 — My own claim that Layer 3 fixes V-2 on its own

| | |
|---|---|
| **Claimed** | `docs/contracts/PHASE-1-V1-PROPOSAL.md` §4: binding `entries[0]` *"also fixes V-2: … the working file compares against entry 0's hash and refuses `PLAN_HASH_MISMATCH`."* |
| **Actually** | It does not, on its own. `_verify_plan` unseals the sealed copy **before** it looks at the working file. With `do_plan` still free to overwrite `plan.sealed/`, entry 0's manifest no longer matches disk, so step (a) refuses `SEAL_MANIFEST_MISMATCH` and the working-file check at step (b) **is never reached**. Layer 4 is a **prerequisite** for the V-2 fix, not a fourth extra. |
| **Direction** | Against me: I claimed one layer did work that needs two. |
| **Source** | **Builder (Claude Code)** |
| **Caught by** | The director's reviewer, by simulating Layer 3 without Layer 4. Confirmed by me before building: step (a) refused `SEAL_MANIFEST_MISMATCH`, step (b) never ran. |
| **Severity** | Medium. It would have shipped as a wrong sentence in the record, and it would have reordered the work wrongly. |
| **Class** | **The same class as V-5**: a claim about a mechanism, believed because it sounds right, never run. That is now three entries of this shape (C-10, V-5, and C-7's ruff number). |
| **Replaced by** | Build order Layer 4 → 3 → 1 → 2, and refusals asserted by `Reason`, not by whether a refusal happened |
| **Status** | **CLOSED** -- discharged by `d66d225`: the V-1 mechanism signed off at Phase 1 close|

---

## C-11 — My estimate of strict linearity's usability cost was too high

| | |
|---|---|
| **Claimed** | `PHASE-1-V1-PROPOSAL.md` §5: strict linearity is *"a real usability cost on a legitimate workflow"* — specifically retrying after a mistake. |
| **Actually** | Close to nil. Every step raises its `Refusal` **before** `ledger.append`, so a failed step writes no entry, and the retry-after-a-mistake workflow passes strict linearity untouched. A repeated step in a ledger is therefore always a repeated *success*. |
| **Direction** | Against me, and in the direction that made me hedge a ruling I should have recommended cleanly. |
| **Source** | **Builder (Claude Code)** |
| **Caught by** | The director, by running it rather than reasoning about it |
| **Severity** | Low as a defect, notable as a pattern: I described a system property I had not measured, in a document asking for a ruling on it. |
| **Replaced by** | D-17 records the fact and its consequence, and `test_a_failed_step_writes_no_entry` asserts it so it cannot quietly stop being true |
| **Status** | **CLOSED** -- discharged by `d66d225`: `test_a_failed_step_writes_no_entry` pins the fact D-17 rests on|

---

---

## C-12 — I reported what I fixed and not what I did not

| | |
|---|---|
| **Claimed** | Report of 2026-08-28 against `82cf114`: *"V-1 mechanism landed. All four layers, plus nine other findings."* Followed immediately by a question about the CLI. |
| **Actually** | **Eight accepted findings were untouched**, including F-1, V-3 and V-4 — the three highest severities on the list, and F-1 was the one I had myself ranked first. Part F step 3, the plan-load family, was skipped entirely; steps 4-7 were done in part. `Reason` contained no `LABEL_NOT_NUMERIC`, no `FRAME_EMPTY`, no `FRAME_TOO_SMALL`, and `Estimand.is_positive` was byte-identical to `eb4c2cc`. |
| **Direction** | Against the reader. Everything I wrote was true of what it covered; the omission is what made the report misleading. A stop that is a third done reads as a stop nearly closed. |
| **Source** | **Builder (Claude Code)** |
| **Caught by** | The director, reconciling my report against `errors.py` |
| **Severity** | **High as a process defect.** An obligation reported by omission stops constraining anything just as surely as one reported wrongly. This is the standing rule to reconcile the deliverable list against what exists and raise the difference, attached to the artifact that exposed it — and the artifact was three missing enum members. |
| **Replaced by** | **Every report now ends with what remains open, by name and severity, or it is not a report on the stop.** |
| **Status** | **CLOSED** -- discharged by `d66d225`: every report since has ended with what remains open, by name|

**A second instance in the same message.** "Nine other findings" did not reconcile against my own
table, which listed seven rows beyond the four layers. That is the count treadmill rule 14 warns
about, in prose rather than a document. The fix is the same: state a figure once against the
artifact that produces it, not in passing.

---

## C-13 — F-1 deferred against my own severity ranking

| | |
|---|---|
| **Claimed** | Review stop: F-1 ranked **high**, on the grounds that real Trust & Safety label columns contain "unclear", "n/a" and blanks, and a raw traceback on the most likely real input breaks R8 and the tool's central promise. |
| **Actually** | I then built four layers of V-1 and left F-1 open, without saying so. The argument I made for its severity had not weakened between writing it and skipping it. |
| **Direction** | Against my own stated judgment, which is the part worth recording. |
| **Source** | **Builder (Claude Code)** |
| **Caught by** | The director |
| **Severity** | Medium. The same class as V-11 — a real, likely input producing a library traceback instead of a refusal — which the director named as a further reason F-1 should not have been deferred. |
| **Replaced by** | F-1 fixed and widened to the plan-load layer per the ruling, with `LABEL_NOT_NUMERIC` at estimate time as the second net and `PLAN_THRESHOLD_INVALID` at load as the first |
| **Status** | **CLOSED** -- discharged by `d66d225`: F-1 fixed and widened to the plan-load layer|

---

---

## C-14 - The docs/src ratio I used to answer "are we over-documenting?"

| | |
|---|---|
| **Claimed** | Drift answer of 2026-08-28: a table with rows `src/` 1,607, `tests/` 1,853, **`docs/` 4,375**, and the conclusion *"Docs are 2.7x the source."* |
| **Actually** | `docs/` is **3,531** lines. The 4,375 figure counted every markdown file in the repository - `docs/` plus the charter, README, SECURITY.md and `prevalence-kit-VISION.md`, which is the Phase 0 *input* the charter was drafted from, not record this build produced. The ratio is **2.20x** for `docs/` proper, 2.72x for all repo prose. |
| **Direction** | Against the argument I was making. The number overstated the thing I was being asked about, by counting a 225-line document that predates the build. |
| **Source** | **Builder (Claude Code)** |
| **Caught by** | The director, re-deriving all six figures in the table. Five matched; this one did not. |
| **Severity** | Medium. The label said `docs/` in a table whose other two rows were literal directories, so the label was wrong even if the intent was "all prose in the repo" - and it landed in the one answer where the number *was* the argument. |
| **Class** | Same as C-7: a number nobody re-derived. Third instance. |
| **Replaced by** | `docs/` 3,531 lines, ratio **2.20x**; all repo prose 4,375, ratio 2.72x. Both stated with what they count. |
| **Status** | **CLOSED** -- discharged by `d66d225`: both ratios stated with what they count|

**Note on the ceremony conclusion that rested on it.** The director rejected the "three review rounds
is inflation" reading, on evidence: round one found seven defects and missed ten; round two's report
omitted eight open findings. Rounds two and three were caused by defects in the *reporting*, not by
the method asking for them. Had the first report been complete there would have been one round. So
the remedy is not fewer rounds - it is `tools/check_claims.py`, which makes a report reconcilable
against the artifact. Recorded here because the correction and the conclusion travelled together.

---

---

## C-15 - F-4 regressed into the shipped example

| | |
|---|---|
| **Claimed** | Report of 2026-08-28 against `d5442d4`: F-4 closed, and "Phase 1: nothing" open. |
| **Actually** | `examples/synthetic/labels.csv` had 40 rows, every content field exactly 31 bytes, against `CHUNK_BYTES = 65,536`. Every item sealed to one chunk, so **exit check E9c - swap two chunks WITHIN one item, expect `SEAL_REORDERED` - could not be performed at all** on the fixture the director was about to run the checklist against. The nearest possible action, a cross-item swap, returns `SEAL_MANIFEST_MISMATCH`. |
| **Direction** | Against the contract. F-4's own sentence returning: green tests, wrong document. |
| **Source** | **Builder (Claude Code)** |
| **Caught by** | The director, running the shipped example end to end before the hand-run |
| **Severity** | **Medium, and blocking.** It did not make the tool wrong - E9, E9b and E9c still returned three distinct codes, but by luck, because dropping an item's only chunk reads as truncation. The reorder path was never exercised at the director's hand. |
| **How it happened** | I fixed F-4 in `tests/conftest.py`, then generated `examples/synthetic/labels.csv` from a demo run without carrying the same property across. The fixture requirement lived in one file's constants and in prose, and prose does not travel. |
| **Replaced by** | `tools/make_example.py` generates the example with one deliberately multi-chunk item, and states in code why. `check_claims`'s sixth check, `fixtures`, asserts the property. E9c restated to name `item-0154` and `0000.bin`/`0001.bin` specifically. **Verified: E9c on the shipped example now returns `SEAL_REORDERED`, with E9 and E9b returning `SEAL_TAMPERED` and `SEAL_TRUNCATED` on the same item.** |
| **Class** | New, and named in **D-23**: a finding closed in one artifact and open in another. Distinct from the wrong-statement class (C-7..C-11) and the wrong-reporting class (C-12..C-14). |
| **Status** | **CLOSED** -- discharged by `87b05f3`: `tools/make_example.py` and `check_fixtures`|

**Two smaller things the same fix surfaced, both mine.** `check_fixtures`'s first version read the
CSV with a bare `DictReader` and died on `_csv.Error: field larger than field limit` - the exact
defect V-11 named, inside the checker written to prevent that class of thing recurring. And adding
`RUN_NOT_FOUND` made the contract's "22 reason codes" stale, which the `figures` check caught on the
same run. Both are the checker working on its own author.

---

---

## C-16 - The report contradicted the command it tells the reader to run

| | |
|---|---|
| **Claimed** | `report.md` listed the chain as four ledger entries. |
| **Actually** | `verify` on the same run reports **five**. `emit-report` appends its own entry after the table is built, and nothing in the report explained the difference - in the one document that tells the reader *"Anyone can re-check this with `prevalence-kit verify`"*. |
| **Direction** | Against the reader, in the flagship artifact. An outsider reading the report and running the command it recommends gets two numbers that disagree, with no way to tell which is wrong. |
| **Source** | **Builder (Claude Code)** |
| **Caught by** | The director, at exit check **E4** - reading the report by eye. No instrument caught it: the tests assert the chain's *contents*, the checker asks about citations and fixtures, and the harness never emitted a report at all (contract 7a records that E4 and R7 were outside its reach). |
| **Severity** | Medium. Nothing computed is wrong. What was wrong is that the artifact an auditor actually reads undermined its own audit instruction. |
| **Replaced by** | The report now states the chain as at emission, that emitting appends one further entry, and **the exact count `verify` will report**. Asserted by `test_the_report_says_what_verify_will_count`, which checks the prediction is *correct* and not merely present, and by a second test that it tracks across repeat emissions. |
| **Status** | **CLOSED** -- discharged by `875a244`: the report states the count `verify` will report, asserted by test|

**Why this one is worth its entry.** It is the clearest instance in the phase of the thing rule 4
exists for: *green tests prove self-consistency, not meaning.* Every test passed, the checker
reconciled, the harness ran 24 damage cases - and the defect was visible in ten seconds to a person
reading the output.

---

## C-17 - E2's wording admitted a reading under which its own expectation was false

| | |
|---|---|
| **Claimed** | Exit check E2: *"Point the plan's data path at a nonexistent file, rerun E1. Expected: same plan hash."* |
| **Actually** | Ambiguous. Read as *edit the plan so it names a file that does not exist*, the plan record changes, so the hash changes, and the stated expectation is **wrong**. The path is part of the commitment and is *supposed* to affect the hash. The check is that the hash does not depend on the **data**, which requires leaving the plan alone and making the file absent. |
| **Direction** | Against the check. A checklist item whose expectation is false under a natural reading of its own action is not a check. |
| **Source** | **Builder (Claude Code)** - I wrote E2. |
| **Caught by** | The director, performing it, noticing both readings, and choosing the correct one |
| **Severity** | Low in effect, notable in kind. R1 is the property pre-registration rests on, and its exit check was the one written loosely. |
| **Replaced by** | E2 restated as an action on the filesystem: *leave the plan untouched, rename or move the population file*. |
| **Status** | **CLOSED** -- discharged by `875a244`: E2 restated as an action on the filesystem|

**The part worth keeping.** *The reviewer's harness had encoded the wrong reading.* It edited the
plan, printed `same as the real plan? False`, and added a note explaining why that was fine - so the
harness was internally coherent and testing the wrong thing. Contract 7a says **a second instrument
is not an independent truth** because it carries its author's blind spots. This is the evidence for
that sentence rather than an assertion of it, and it arrived on the first occasion it mattered.

Neither instrument was wrong about what it checked. Both read the same ambiguous sentence and
resolved it the same way. That is what a shared upstream defect looks like, and it is why the
*director* performing the checklist is not redundant with either.

---

## C-18 - The ruff file-count artifact, appearing where C-7 said it would

| | |
|---|---|
| **Claimed** | Nothing new. C-7 already records that ruff's summary integer is not a file count. |
| **Actually** | The director's hand-run of E12 printed *"42 files already formatted"* against a project with far fewer Python files. |
| **Direction** | - |
| **Source** | Not a defect in this project. Recorded because **C-7 predicted it would keep surfacing, and it has now surfaced in the director's own hand-run** rather than only in my reports. |
| **Severity** | None. Logged so that the next person who sees the number has somewhere to look instead of investigating it again. |
| **Replaced by** | Gate evidence is exit codes and the test count. Neither this project nor its record quotes the ruff integer. |
| **Status** | **noted** - carries forward as a known artifact of the tool, not an open item |

---

---

## C-19 - V-12: a check that did not run, reported as a check that passed

| | |
|---|---|
| **Claimed** | Phase 1 close: E8c performed, `verify` "exit 0 with the skip stated in words", 8 checks, nothing out of place. |
| **Actually** | With `--plan` omitted and a **tampered** `plan.yaml` sitting on disk, `verify` printed `[ok] plan (working file): SKIPPED -- no plan file on disk to compare`, summarised **"8 checks, nothing out of place"**, and exited **0**. Three faults in increasing order: the message was false (the file *was* on disk), the `[ok]` counted a check that never ran, and **E8/V-2's protection - the flagship one - silently did not run.** |
| **Direction** | Against the operator, in the command the report tells them to trust. |
| **Source** | **Builder (Claude Code)** for the code. **The reviewer** for the check that missed it: the E8c command handed to the director omitted `--plan` while `plan.yaml` sat in the working directory, instead of deleting the file as the contract says. The director performed it faithfully. |
| **Caught by** | The builder, reconciling the director's hand-run transcript against the contract's wording, after the director asked for exactly that reconciliation |
| **Severity** | **High.** A stated protection not running, reported as green. |
| **Replaced by** | D-24: the path is recorded in the plan entry body and `verify` defaults to it, so there is no longer a case where the tool knows where the plan was and declines to look. Plus the three conditions - no `[ok]` for an unperformed check, no "nothing out of place" when one was skipped, and any further skip brought back before shipping. |
| **Status** | **CLOSED** -- discharged by `25f9996`: D-24: the path recorded in the plan entry, `verify` defaults to it|

**The pattern, now specific enough to name.** This is the **third** instance of the
reviewer-instrument class, after the harness's clean frame that never exercised V-7 and the harness
encoding the wrong reading of E2. The director's own characterisation, recorded as given:

> *My instruments have been wrong about what the contract's action is, never about what the code
> does.*

That is a sharper statement than contract section 7a's, and it says where a second instrument helps
and where it cannot. It reads the same contract the builder wrote; where that contract is ambiguous
or wrong, both instruments inherit the defect. **Only executing the action as written catches it** -
which is what the director's hand-run is for, and why the transcript was worth reading line by line
against the wording.

---

## C-20 - I argued the exit-code question rested on two checks; it rests on one

| | |
|---|---|
| **Claimed** | V-12 proposal: *"E6 and E8c legitimately skip and are specified as exit 0, so this would change two passing exit checks."* |
| **Actually** | **E6 skips nothing.** Run with `frame.txt` and `labels.csv` moved off disk, it reports the full eight checks - because `verify` redraws from the recorded `frame.json`, not from the original input. That is R5 working exactly as designed. Only E8c skips. |
| **Direction** | Against the strength of my own argument. I presented a conclusion as resting on two supports when it rests on one. |
| **Source** | **Builder (Claude Code)** |
| **Caught by** | The director, running E6 rather than reasoning about it - and the evidence was already in the transcript he had sent me, which I had read and reconciled without noticing |
| **Severity** | Low in effect: the conclusion survives. Notable in kind - this is the believed-mechanism class again (C-10, V-5, C-7), and it appeared **in the same message where I corrected someone else's reading of a transcript.** |
| **Replaced by** | Recorded in D-24's "alternative not taken": the argument holds on one check, not two. |
| **Status** | **CLOSED** -- discharged by `25f9996`: D-24 records that the argument holds on one check, not two|

---

---

## V-13 - SECURITY 3.8 stated the disclosure wider than the behaviour

| | |
|---|---|
| **Claimed** | `SECURITY.md` 3.8: *"On this platform it is absolute, so it can disclose a username and directory structure."* |
| **Actually** | The recorded path is **as invoked**, not resolved. Verified both ways: `plan plan.yaml` records `"plan.yaml"`; `plan C:\...\plan.yaml` records the full path. The director's own Phase 1 hand-run recorded `plan.yaml` and disclosed nothing. |
| **Direction** | **Overstated a limit** - safe in effect, wrong in kind. Doctrine 7 is never more and never less, and a security document is exactly where a reader checks a claim against the artifact. An operator who reads 3.8, opens `ledger.jsonl` entry 0, and finds a bare filename learns the document does not describe the tool. |
| **Source** | **Builder (Claude Code)** |
| **Caught by** | The director, reading the section against the ledger |
| **Severity** | Low in exposure, medium in kind: it is a false statement in the one document read for accuracy. |
| **Replaced by** | 3.8 now states the as-invoked behaviour with both examples, **and gives the operator the control it was hiding**: run `plan` from the plan's own directory with a bare filename and nothing sensitive is recorded. The old text said only "there is no supported way to redact it", leaving the reader with no action. |
| **Status** | **CLOSED** -- discharged by `d66d225`: SECURITY 3.8 restated as-invoked, with the control it was hiding|

**The part worth keeping.** Overstating a limit felt like the safe direction and was not. It cost the
reader a control they actually had, and it put a checkable falsehood in the security document.

---

## V-14 - I called a branch unreachable that every existing user hits first

| | |
|---|---|
| **Claimed** | V-12 report and D-24: a run with no recorded plan path *"is unreachable through the CLI... it requires the Python API, which Phase 1 does not document as a supported surface."* |
| **Actually** | **Every run created before commit `25f9996` has no `plan_source_path`.** The director reached the branch through the CLI, against his own Phase 1 close run. Reproduced here by stripping the field and re-chaining honestly: `[--] NOT CHECKED -- this run recorded no plan path`, exit 0, no traceback. Anyone who used the tool before that commit has such a run on disk. |
| **Direction** | Against the case's importance. I described a branch as needing an undocumented surface when it is the first thing an existing user meets. |
| **Source** | **Builder (Claude Code)** |
| **Caught by** | The director, running the new `verify` against an old run rather than reasoning about which callers reach the branch |
| **Severity** | Low in effect - **no harm done**, the message is well worded and the behaviour is right. Medium in kind: **the reasoning decides the treatment.** A branch believed unreachable gets a pin and a shrug; a branch every user hits deserves a release note and a check that the message reads right to someone who never had the field. It does. That was luck. |
| **Replaced by** | **D-25** treats it as a supported case, records that the ledger cannot distinguish an old run from an API caller, and carries **O-15** for a schema version if the two ever need different advice. |
| **Class** | Believed-mechanism (C-10, V-5, C-7, C-20). Fourth instance in that family, and the second inside a sentence where I was careful enough to bring the case to the director rather than absorb it. **Bringing it was right; the characterisation attached to it was not.** |
| **Status** | **CLOSED** -- discharged by `d66d225`: D-25 treats it as a supported case; O-15 carries the schema version|

---

## C-21 - The fifth reviewer-instrument defect, and the first gate to fire on an accident

| | |
|---|---|
| **What happened** | The reviewer directed the V-12 re-run into a directory its own dry-run had already populated. `plan` refused `RUN_ALREADY_OPEN`; the later verbs appended a second attempt; `verify` refused `RUN_NOT_LINEAR: Step 'sample' was recorded more than once (again at entry 4)`. The re-run was redone in a fresh timestamped workspace and passed. |
| **Source** | **Reviewer instrument.** Second recorded instance; fifth overall in the class. |
| **Severity** | None to the tool. Recorded because of what it demonstrates. |
| **Status** | **noted** |

**Two things this is evidence for, and neither was constructed by us.**

**V-1's Layers 1 and 2 fired on a real accident.** Every previous exercise of them was a case one of
us built. This time a person made an ordinary mistake -- reusing a folder -- and both layers behaved
exactly as designed, including `verify` refusing to certify a workspace holding two attempts. The
mechanism has now been tested by the world rather than by its authors.

**Refusals go to stderr.** `| Out-Null` swallowed stdout and the refusal still printed. That is what
makes the CLI usable in a pipeline, and it was confirmed by accident rather than by a test.

**Narrowed 2026-08-29: the sentence below held for five instances and then broke.** C-26 is a
sixth, and it is wrong about a **fact in a source** rather than about a contract's action --
because a summarising fetch tool dropped a character. The characterisation is kept as what was
true when it was written, with its boundary now known.

**The class is now a property, not a run of luck.** Five occasions: the harness's clean frame that
never exercised V-7; the harness encoding the wrong reading of E2; the E8c command that omitted
`--plan` instead of deleting the file; and now a re-run directed into a dirty directory. The
director's characterisation, recorded verbatim at C-19, holds on all five:

> *My instruments have been wrong about what the contract's action is, never about what the code
> does.*

---

---

## V-15 - A wrong path in CLAUDE.md, and the reason the checker missed it

| | |
|---|---|
| **Claimed** | `CLAUDE.md` and `docs/CORRECTIONS.md` both named `docs/PHASE-1-REVIEW-STOP.md`. |
| **Actually** | The file is at `docs/contracts/PHASE-1-REVIEW-STOP.md`. The next session reads `CLAUDE.md` first and would have gone looking for a document that is not there. |
| **Direction** | Against the next session, in the file written to orient it. |
| **Source** | **Builder (Claude Code)** |
| **Caught by** | The director |
| **Severity** | Low as a typo. **The real finding is that `check_claims` passed.** |
| **Status** | **CLOSED** -- discharged by `d66d225`: `check_paths` discovers files instead of naming them|

**Why the checker missed it.** `check_paths` read a fixed list of globs -- `src/**/*.py` and
`tests/*.py`. `CLAUDE.md` was not in it, so adding a new document silently reduced coverage: no
failure, no warning, just less checked than the day before.

That is **D-23's principle turned on the checker's own inputs**. *A check that names its question
generalises; a check that names a row does not.* This check named its files.

**Fixed by discovery, not by adding a row.** `check_paths` now reads every `.py`, `.md` and `.txt`
in the repository, so the next document added is covered on the day it lands. Its selftest plants a
bad path in **`CLAUDE.md` specifically** - a file the old list would never have opened.

**Three things the widened scan found immediately**, which is the coverage that was missing:

1. This defect, in two files.
2. **A bug in the checker's own regex.** `awesome-safety-tools/README.md` matched on its
   `tools/README.md` suffix and was reported as a missing file. Fixed with a lookbehind.
3. Two paths that are deliberately absent and now say so in a `KNOWN_ABSENT` set with a reason each:
   `src/svy/estimation/base.py`, quoted from another package as D-18's evidence, and
   `tests/test_plan.py`, quoted in C-8 as the defect itself. **An explicit set beats widening the
   regex or skipping whole files: every exemption is visible and has to be justified when added.**

---

## C-22 - A recorded retrieval procedure that had quietly stopped working

| | |
|---|---|
| **Claimed** | `docs/STANDARDS.md`, retrieval note, written 2026-08-28: *"Use the EU Publications Office endpoint `http://publications.europa.eu/resource/celex/<CELEX>` with `Accept: application/xhtml+xml`. Same authority, machine-readable, no challenge."* |
| **Actually** | That call returns **HTTP 400**, 205 bytes: *"Invalid content type CONTENT_STREAM for WORK ... without language"*. Measured 2026-08-29 against `32011D0833` **and against `32024R2835`, the CELEX the note was originally written for.** It needs a second header. With `Accept: application/xhtml+xml` **and** `Accept-Language: eng`: HTTP 200, 48,730 bytes, `application/xhtml+xml`. |
| **Direction** | Against the next person who needs a primary source. A recorded procedure that does not work is worse than no procedure, because it reads as checked. |
| **Source** | **Builder (Claude Code)** - I wrote the note in Phase 0. |
| **Caught by** | The builder, by **executing** the recorded procedure instead of quoting it, while gathering the O-18 evidence the director asked for. It surfaced only because the director supplied the EUR-Lex text his browser could read and no fetcher here could. |
| **Severity** | Medium. Nothing shipped wrong. But every future pin in this register depends on being able to fetch a primary source, and the one instruction for doing that had expired with nothing saying so. |
| **Replaced by** | The corrected note, with both headers, the four measured request forms and their results, and the date. Plus four rows in the re-check log. |
| **Status** | **CLOSED** -- discharged by `7f19bd9`: the corrected retrieval note, and S-8 under D-27|

**This is not the believed-mechanism class.** The note was **true when written**. Phase 0 used that
endpoint on 2026-08-28 and it worked -- that is how the "prevalence appears zero times" count was
made over the full texts. It expired within about a day, and nothing here was watching.

**Rule 3 should have caught it and could not.** Rule 3 gives every *source* a re-check date, because
a pin nobody re-checks quietly expires. **The retrieval procedure had no re-check date.** Every pin
in the register sits on it, and it was the one entry with no expiry of its own. It has dated
measurements now.

**The tooling limit, recorded because it is wider than this one question.** The reviewer tried
three EUR-Lex pages -- the legal notice, the about page, and the CELEX record for `32011D0833`. All
three came back empty. I reproduced it here: the legal notice and the CELEX record both return
**HTTP 202 with 0 bytes**. The director read the site in a browser and typed out the text.

So: **a source this project depends on cannot be read by the tool this project uses to check
sources.** That matters now, because Phase 2 leans on more outside references than any phase so far
-- CRAN, a pinned Docker digest, and the Lang & Reiczigel worked results.

**RULED 2026-08-29: accepted, and taken further than this entry took it.** The director's ruling
adds one step: the procedure gets **its own register entry, with its own re-check date**. A pinned
URL, digest and version are worth nothing if the call that fetches them returns 400. The register
pinned *what* to fetch and never *how*, and the how is what broke. `docs/STANDARDS.md` **S-8**, and
**D-27**.

**The standing rule it produces:** *"I could not read it" is a result to report, not a reason to
work from memory.* If a source cannot be fetched, say so, say what was tried, and say what came
back. The director decides. Never fill it in from memory. Never quietly drop it. That is doctrine
rule 7 -- claims at the width of the evidence -- applied to fetching rather than to the claim.

---

## C-23 - The new gate check passed a workflow GitHub could not read

| | |
|---|---|
| **Claimed** | All seven gate checks green at `95b4a88`, including the new `gate` check that reconciles `CLAUDE.md` against `.github/workflows/gate.yml`. |
| **Actually** | The workflow was **not valid YAML**. I had written `- name: mypy (config: src + tests)` unquoted. The `: ` inside the brackets makes YAML read a nested mapping, so the whole file failed to parse. Run `33205536300` died with *"This run likely failed because of a workflow file issue"* -- no jobs ran at all. |
| **Direction** | Against the check I had just written to stop this class of thing. |
| **Source** | **Builder (Claude Code)** |
| **Caught by** | CI, one push later. Not by the local gate, which was green. |
| **Severity** | Low in effect -- one red run, fixed in minutes, nothing shipped. Medium in kind, and the kind is the point. |
| **Replaced by** | `check_gate` now parses the workflow with `yaml.safe_load` instead of a regex, and reports `is not valid YAML` when it cannot. Two controls: `test_the_gate_check_reads_the_workflow_the_way_github_does` and `test_the_real_workflow_is_valid_yaml`. |
| **Status** | **CLOSED** -- discharged by `b018d2a`: `check_gate` parses the workflow with `yaml.safe_load`|

**Why this is worth an entry.** My check read the workflow with a regular expression. A regular
expression will happily read a file that YAML rejects. So **the checker accepted an artifact the
real consumer refuses**, and reported green.

That is the same shape as V-16, which I had just fixed, and the same shape as C-19 before it: an
instrument that looks like it covers something and does not. Third instance in one session.

**RULED 2026-08-29: accepted, and the rule generalises past checkers.**

> **Check an artifact the way its real consumer reads it.**
>
> Anywhere this project reads a **structured** file -- YAML, JSON, TOML, CSV, XML -- the check uses
> the **same parser the consumer uses**. A regex reading YAML is a checker with a different parser
> from the thing it checks, so it can only ever agree by luck.
>
> **Markdown is the exception, and the reason is the rule.** Markdown's consumer is a human, and a
> human reads it loosely too. So `check_claims` scanning Markdown with regexes is sound for the same
> reason the YAML one was not: the checker and the consumer read it the same way.

**Applied on the day it was ruled**, not left as prose. An audit of every structured-file reader in
the tree found one more instance: `tools/check_tripwires.py` TW-1 read arXiv's **Atom XML** with a
regex. It now uses `xml.etree.ElementTree`. Everything else already used the right parser --
`json.loads`, `yaml.safe_load`, `csv.DictReader` in both `src/` and `tools/`.

---

## C-24 - A ratio taken from a working step instead of from the artifact

| | |
|---|---|
| **Claimed** | Report and commit message for `104abe3`, explaining why Clopper-Pearson is narrower than Wilson at k = 0, n = 4000: *"Ratio 0.9603."* |
| **Actually** | **0.9608.** The interval widths are `0.000921794749` and `0.000959443290`, and their ratio is **0.960760**. 0.960281 is a different quantity -- the ratio of the two *linear approximations*, `-ln(0.025) / z^2 = 3.6889 / 3.8415`, which is the limit the sequence reaches as n grows. Re-derived: n = 4,000 gives 0.960760; 40,000 gives 0.960329; 4,000,000 gives 0.960281. |
| **Direction** | Against the artifact. Both numbers are real; the wrong one was attached to the case being discussed. |
| **Source** | **Builder (Claude Code)** |
| **Caught by** | The director, re-deriving the ratio from the exact values rather than accepting the correction |
| **Severity** | Low in effect -- the finding it decorated is correct, and the shipped code returns the right numbers to twelve decimals. Notable in kind, and in where it happened. |
| **Replaced by** | The two figures stated as what they are: **0.9608 at n = 4000**, and **0.9603 as the asymptotic limit**, with the convergence shown. |
| **Status** | **CLOSED** -- discharged by `087f499`: both figures stated as what they are, with the convergence shown|

**This is C-7's family: a figure taken from a working step rather than re-derived from the artifact.**
The working step was the algebra that explains *why* the interval is narrower. That algebra is right,
and the ratio it produces is not the ratio of the two intervals.

**Where it happened is the uncomfortable part.** It landed in the paragraph where I was correcting
myself for asserting a believed mechanism. The correction was right; the number attached to it was
not re-derived.

**And the artifact had already printed the right answer.** The table I generated to check the
property has a `CP/Wilson` column, and it reads `0.960760`. I had it on screen and quoted the
algebra instead.

**The test docstring was already correct** -- it distinguishes "tends to 0.9603" from "at n = 4000
it is 0.96076". So the defect was in the prose I wrote *about* the code, not in the code or its
tests, which is its own small lesson about where to look.

---

## C-25 - A claim about CRAN's package read as a claim about our build

| | |
|---|---|
| **Claimed** | D2.5 anchoring plan, 2026-08-29: *"`epiR` already ships it as `tp.method = \"simplified.bayes\"` -- it is the authors' own package, not a third party adopting them."* |
| **Actually** | True of `epiR` **2.0.96** on CRAN. **False of the build we run.** The witness image pins CRAN to the 2026-04-23 snapshot, which serves **2.0.92**, and `epi.prev()` there has **no `tp.method` argument and no `simplified.bayes`** -- verified by inspecting `formals(epi.prev)` in the image. |
| **Direction** | Against a ruling. The sentence was accurate about CRAN and was read -- reasonably -- as being about our witness. |
| **Source** | **Builder (Claude Code)** |
| **Caught by** | The builder, by building the image and running it. Nothing about reading CRAN would have shown it. |
| **Severity** | **Medium, and higher than its wording suggests.** It did not reach a commit. It reached a **ruling**: the director changed a disclosure requirement on the premise that our witness returns an answer where we refuse. |
| **Replaced by** | The disclosure restated to cite **the paper, not the package** -- S-1.11, Kopacka & Fuchs (2026) -- so it holds whatever any package version ships. And S-1.10 records that our witness is 2.0.92, with what that version does and does not have. |
| **Status** | **CLOSED** -- discharged by `eec1084`: the disclosure cites the paper, S-1.11, not the package|

**The builder proposed no C-number and was overruled**, and the reasoning is what changed the
table's scope. The director's words: *"A claim that never reached a commit but did reach a
director's ruling has done more damage than one sitting unread in a file."* The header now says the
table counts claims that reached a commit **or changed a ruling**.

**The ruling it changed was right for a different reason, and that is recorded rather than quietly
kept.** A refusal that implies *no method can answer this* is an overclaim because Kopacka & Fuchs
(2026) exists as published work -- not because our pinned image ships it. The disclosure stands; its
premise is corrected.

**The standing rule it produces:**

> **The witness's documentation is not the witness. Only the pinned build is.**

Everything quoted from the 2.0.96 manual described a version we do not run. The failure behaviours
were re-verified directly in 2.0.92 before any of them entered the register.

---

## C-26 - A reviewer finding that was manufactured by a summarising fetch tool

| | |
|---|---|
| **Claimed** | Director's review, 2026-08-29: the register spells the third author of S-1.6 **Ozsvari** while Crossref returns **Ozvari**, so one of them has a typo and the disagreement should be recorded rather than reconciled. |
| **Actually** | **There is no disagreement.** Crossref returns codepoints `U+00D3 U+005A U+0053 U+0056 U+00C1 U+0052 U+0049` -- O-Z-S-V-A-R-I with acutes, the **S present**. The register matches it exactly. The apparent missing letter was mojibake in a terminal rendering: the accented characters were mangled, not the `S`. |
| **Direction** | Against the register, which was correct. A correction was proposed against a document that had nothing wrong with it. |
| **Source** | **Reviewer instrument.** |
| **Caught by** | The builder, by asking the Crossref API for the raw record and printing codepoints instead of glyphs. The director then re-checked the same way and withdrew the finding. |
| **Severity** | Low in effect -- nothing was changed on the strength of it. Notable in kind: it is the first instance of its class that is about a **fact in a source** rather than about a contract's action. |
| **Replaced by** | Nothing to replace. The register was right. Recorded because the *finding* was the defect. |
| **Status** | **CLOSED** -- discharged by `eec1084`: nothing to replace -- the register was right; the finding was the defect|

**This breaks C-19's characterisation, and the break is the point.**

C-19 records the director's own sentence, which had held for five instances:

> *"My instruments have been wrong about what the contract's action is, never about what the code
> does."*

**That sentence is now true of five instances and false of the sixth.** This one was wrong about a
character in a bibliographic record.

**The mechanism is new and worth naming.** The reviewer's fetch tool **summarises a page through a
model** rather than returning bytes. A summariser can drop or normalise a character without saying
so. **So any character-level claim made from a summarising fetch is unreliable** -- spellings,
diacritics, digests, exact quotations.

**The remedy, adopted by the director:** for anything where a character matters, go to the raw API
and read codepoints. That is what settled this, twice, independently.

---

## C-27 - "23 reason codes, each with both controls" was false for one of the 23

| | |
|---|---|
| **Claimed** | `docs/contracts/PHASE-1-CONTRACT.md` §10: *"D1.11 \| Refusal gates \| 23 reason codes, each with both controls"*, and in the same section *"R3 met -- every gate has both controls."* |
| **Actually** | **`PLAN_MISSING` had no control at either of its two raise sites.** Proved by mutation, not by reading: swapping `Reason.PLAN_MISSING` for an unrelated code in `plan.py`, and separately in `verify.py`, left **all 418 tests passing** both times. Nothing in the suite could tell the difference. |
| **Direction** | Against the artifact. The refusal itself works -- both sites were confirmed to fire by execution. What was false is the claim that something proved it. |
| **Source** | **Builder (Claude Code)** |
| **Caught by** | **D2.7's opening inventory**, then confirmed by a **31-code mutation sweep** -- every reason code swapped at every raise site, the suite run against each. Two codes survived. |
| **Severity** | **Medium.** Doctrine rule 5 exists because *refusals that cannot be counted by cause make the refusal metric meaningless*, and this is a count that included one nobody could count. It is worse than a missing test in one specific way: **`PLAN_MISSING` at the `verify` site is what protects D-15 check (a)**, the check that makes R5 -- an outsider can verify from the sealed record alone -- provable rather than aspirational. |
| **Replaced by** | Four tests in `tests/test_verify.py`: a negative control per site, a positive control, and one pinning that the two sites send the operator to different artifacts. Re-verified by mutation: both sites now fail the suite when their code is swapped. And **`check_controls`**, the ninth check, so the class cannot recur silently. |
| **Status** | **CLOSED** -- discharged by `09dfdce`: four tests in test_verify.py, and `check_controls`|

**This is a defect against Phase 1's own stated exit criterion, not a limit of Phase 1, and doctrine
rule 9 requires saying which.** Phase 1 did not promise "most codes have controls" and then get held
to a higher bar later. It promised **each**, in a numbered count, and closed on it. The claim was
wrong when it was written.

**Phase 1 is not reopened.** The record is corrected here, and the fix lands in Phase 2 under D2.7,
whose contract row already reads *"and any further undefined case found."* The closed phase's
outcome section keeps its original sentence with a pointer to this entry -- **a dated reading is
never rewritten**, and the outcome is the most dated reading in the repository.

**Why no instrument caught it for a phase and a half.** `check_codes` reconciles the `Reason` enum
against the contracts in both directions, so every code is documented and every documented code
exists. **It looks like the reason-code checker and it never asks whether a code fires.** That is
D-34's shape, one week later, in the checker that most looks like it already asked. The count "23
reason codes" was itself derived by that checker -- so the number was machine-checked and the
property it was quoted to support was not.

**The instrument that found this was itself wrong first, and that is worth keeping.** The first draft
of `check_controls` reported three codes, including `RUN_NOT_FOUND`. The mutation sweep contradicted
it: swapping `RUN_NOT_FOUND` **did** fail a test, which asserts the CLI's stderr string
`REFUSED [RUN_NOT_FOUND]` rather than the enum member. The checker was reading string literals only
when they were the whole code name. **Ground truth corrected the new instrument before the new
instrument entered the record** -- which is the only reason a false finding against `RUN_NOT_FOUND`
is not in this table.

---

## C-28 - "20 accepted, 20 closed" rode on a machine-checked reconciliation

| | |
|---|---|
| **Claimed** | `docs/contracts/PHASE-1-CONTRACT.md` §10: *"**20 accepted, 20 closed**, each with named closing evidence in `docs/FINDINGS.md`, reconciled against the code by `tools/check_claims.py`."* |
| **Actually** | Wrong in two ways. **The register held 20 rows, but only 18 were findings.** Q-1 was `ruled` and Q-2 is `noted` and permanently unclosable -- the same file says so in a section titled *"Q-2 is deliberately unclosable"*. So "20 closed" contradicts its own register. **And four accepted findings had no row at all**: V-12, V-13, V-14 and V-15. The register now holds 24 findings, not 20. |
| **Direction** | Against the artifact, twice. Both errors made the phase look tidier than it was. |
| **Source** | **Builder (Claude Code)** |
| **Caught by** | Searching for the class C-27 named, on the director's instruction to go looking. |
| **Severity** | **Medium.** The count was wrong, and the sentence made the wrongness hard to see. |
| **Replaced by** | The four missing rows, added under D-34. The register is now reconciled in both directions by `check_register`. |
| **Status** | **CLOSED** -- discharged by `b018d2a`: the four missing rows, added under D-34|

**This is the second instance of the class C-27 named, and it is why that class has its own rule.**
The sentence ends with *"reconciled against the code by `tools/check_claims.py`"*. That is true. The
checker did reconcile -- the 20 rows that were there. The numbers in front of it were written by
hand and neither was right.

A reader has no way to see where the checking stops.

**Phase 1 stays closed and its outcome keeps its sentence.** A dated reading is not rewritten. The
correction lives here.

---

## C-29 - I reported a green gate for a tree I had not run

| | |
|---|---|
| **Claimed** | Report and commit `09dfdce`: *"Gate: seven green. 423 tests, selftest 9/9."* |
| **Actually** | The committed tree failed **3 tests**. `plan.py:93` still raised `Reason.PLAN_MISSING`, which the Q8 split had removed from the enum. `AttributeError: type object 'Reason' has no attribute 'PLAN_MISSING'`. |
| **Direction** | Against the artifact. The gate was green on a tree that no longer existed when I committed. |
| **Source** | **Builder (Claude Code)** |
| **Caught by** | The director, running `pytest` on the committed state |
| **Severity** | **High.** Not for the breakage, which was one line, but for the claim. The gate is the one figure every other figure leans on. |
| **Replaced by** | The line fixed in `plan.py` and `verify.py`, and the whole gate re-run on the committed tree before reporting. |
| **Status** | **CLOSED** -- discharged by `a418473`: the tree fixed and the whole gate re-run on the committed state|

**The mechanism, because it is worse than carelessness.** My mutation re-verification loop ended each
pass with `git checkout -- src/prevalence_kit/plan.py`. The Q8 edit to that file was **unstaged** at
the time, so the checkout did not just undo the mutation -- it reverted my real change. The same
happened to `verify.py`. Then `git add -A` committed the reverted files beside an `errors.py` that
had the new names.

I ran the gate **before** that loop and reported its numbers **after** it.

**This is the skill's own warning, hit while using the tool it warns about:** commit the evidence
before running anything that touches the tree, because a tool that acts on the working tree can
destroy the record it exists to protect.

**And it is rule 8, one commit after I wrote rule 8.** "Seven green, 423 tests" is a property
restated without being re-derived from the artifact it describes.

**The standing rule this produces:**

> **Re-run the whole gate after anything that writes to the working tree, and report that run.**
> Not the run before it.

---

## C-30 - Three agreement figures that were measurements at one confidence level

> **See the re-recording at the end of this entry. Part (c) was corrected once and the
> correction was also wrong.**


| | |
|---|---|
| **Claimed** | Three separate claims, all from fixtures that varied `n` and held `conf.level` at 0.95. (a) *"7.1e-11 across 23 cases, n = 1 to n = 1,999,514"* -- `docs/STANDARDS.md` S-2.4, `CLAUDE.md`, `estimators.py`. (b) *"after DIGITS = 12 rounding, 6.9e-09"*. (c) The test `test_clopper_pearson_is_wider_than_wilson_except_at_zero`, whose docstring said *"narrower in exactly one, which is k = 0 at n = 4000"*. |
| **Actually** | Re-measured across 69 cases at confidence 0.90, 0.95 and 0.99. (a) the method is **8.4e-11**, barely moved. (b) the record format is **2.6e-07**, a factor of **38** worse. (c) **the exception set is not k = 0.** At 0.99 six cases are narrower, including `k=1, n=40` and `k=99, n=100`. The real property is `k <= 1 or k >= n - 1`, and the region grows with confidence. |
| **Direction** | Two against us, one neutral. (b) is the uncomfortable one: our record format is a bigger constraint than reported. (c) was a wrong characterisation stated as a measured fact. |
| **Source** | **Builder (Claude Code)** |
| **Caught by** | Adding a second axis to the fixtures, on the director's instruction. **Nothing else could have caught it** -- no witness comparison varies a parameter no fixture varies. |
| **Severity** | **Medium.** No shipped number is wrong. Three reported figures were narrower in scope than they read, and one characterisation was false outside its measured point. |
| **Replaced by** | All three restated with their axes. The test renamed `test_clopper_pearson_is_narrower_than_wilson_only_near_the_boundary` and asserting the boundary property instead of the k = 0 one. |
| **Status** | **CLOSED** -- discharged by `fca213b`: all three restated with their axes; the width test replaced by coverage|

**Why (b) moved so much, since a factor of 38 deserves an explanation rather than
a shrug.** `DIGITS = 12` is a fixed number of decimal places, so it costs a fixed
*absolute* precision. Raising confidence pushes rare-event lower bounds smaller --
`k=1, n=4000` at 0.99 has a lower bound of 1.25e-06 -- and a fixed absolute error
is a larger *relative* one against a smaller number.

**So the honest sentence is the one now in the test:** the estimator is accurate
across the range, and our record format is the binding constraint, more so the
smaller the number. Both still clear R2.3's four significant digits by at least
three orders of magnitude at every level.

**C-30(c) re-recorded 2026-08-29, and the first recording of it was itself wrong.**

This entry originally said the exception set was `k <= 1 or k >= n - 1`. **That is false at 0.99.**
Sweeping every k for n in {40, 100, 1000, 4000}: 0 narrower cases at 0.90, 6 at 0.95, and **44 at
0.99, of which 28 are not near a boundary** -- k = 2..7 at n = 4000, k = 97, 98 at n = 100.

So the property was stated wrong three times: never narrower, then narrower only at k = 0, then
narrower only near the boundary. **Widening the grid and re-describing would have produced a fourth.**

**The root cause is not any of the three regions. It is that a region was being asserted at all.**
Where a derived property holds depends on n, k and confidence with no simple closed form, so every
hand-written description is false at the next corner nobody sampled.

**And it broke the axes rule in the commit that introduced it.** The rule was applied to agreement
figures and not to property claims. *"Clopper-Pearson is narrower where k <= 1"* is exactly as
axis-dependent as *"8.4e-11 across 69 cases"*, and it shipped without its axes. That is the single
root cause under all three failures.

**The fix is to stop testing width and test coverage.** Conservative has a definition -- coverage at
least 1 - alpha for every true p -- and Clopper-Pearson guarantees it while Wilson does not. Width is
a consequence, and consequences vary. The width comparison survives only as a **measurement with a
stated scope**: 7 of the fixture's 69 cases, and nothing claimed about the 70th.

**What replaced it is anchored on S-1.1**, whose full text was read the same day after two phases of
being cited unread. Wilson's coverage falls to **0.838** at `p = 0.1765/n` against a nominal 0.95 --
the paper's published figure, which our code reproduces as 0.8382. **That belongs in the honest
limits and in whatever the README says about choosing an interval**, and it matters more than the
width question ever did.

---

## C-31 - I read a paper for the first time and immediately misread it

| | |
|---|---|
| **Claimed** | `docs/STANDARDS.md`, commit `e665344`, and the report and commit message with it: S-1.1's assessment of Jeffreys is *"close to the opposite"* of the blog's, and D-8 therefore rests on a characterisation the anchor contradicts. Also: *"the charter's §6.1 ... cite a blog's reading"*. |
| **Actually** | **Neither half holds.** (a) The two sources measure different quantities and do not conflict. S-1.1 §3.2 praises Jeffreys' **average** coverage across p and, in the same section, records *"an unfortunate fairly deep spike near p = 0"* -- then §4.1.2 supplies a modified Jeffreys whose purpose is removing that spike. The anchor documents a rare-event problem itself. (b) **Jeffreys does not appear in charter §6.1 at all.** Its only mention is line 340, inside the A-0 amendment log -- a dated record of the director's ruling, never edited. |
| **Direction** | Against two documents that were fine. A correction proposed against a non-defect, which is C-26's shape with the builder as the source rather than an instrument. |
| **Source** | **Builder (Claude Code)** |
| **Caught by** | The director, who declined to accept the reading and asked for it to be measured rather than reconciled in prose, and who checked every charter mention. |
| **Severity** | **Medium.** It reached a commit and a push. Nothing in the code depended on it, but it was on its way to becoming a correction entry asserting a conflict between two papers that agree. |
| **Replaced by** | `r/coverage_fixtures.R`, which measures all three intervals at the rare-event operating points, and a rewritten S-1.1 section stating what each source measured. |
| **Status** | **CLOSED** -- discharged by `95a521a`: `r/coverage_fixtures.R` measures it; S-1.1 rewritten|

**What the measurement found, and it is the reverse of what I implied.** Worst coverage over
`p = gamma/n`, gamma in [0.5, 15], at n = 1000:

| nominal | Wilson | Clopper-Pearson | Jeffreys |
|---|---|---|---|
| 0.90 | 0.8532 | **0.9043** | **0.8125** |
| 0.95 | 0.9098 | **0.9540** | 0.9141 |

**Jeffreys is the worst of the three at 0.90**, which is the opposite of "close to the opposite."
Our own instrument confirms the anchor's own caveat.

**The class this belongs to, and it is not a new one.** *A figure measured along one axis and stated
as though along all of them* -- C-30's class -- with "average coverage" as the axis and "coverage" as
the unqualified word. **The record conflated an average with its worst point.** An average hides its
worst point by construction, which is exactly why this project measures at operating points.

**Reading a source for the first time is not the same as understanding it**, and the gap between
those two is where this landed. The fix was not to read more carefully; it was to compute the
quantity both sources were talking about.

---

## C-32 - "As little as 91%" asserts a floor the measurement already breaks

| | |
|---|---|
| **Claimed** | `PROJECT_CHARTER.md` §8, amendment **A-4**: a 95% Wilson interval *"covers **as little as 91%** of the time"* at rare-event rates. Also in the `CORRECTION_INTERVAL_UNSUPPORTED` refusal text. |
| **Actually** | The measurement is **0.9098**, which is **below** 0.91. So the sentence asserts a floor the measurement has already gone under -- and since it is a worst-over-a-grid figure, a finer grid can only push it lower. |
| **Direction** | Toward the flattering answer. It makes the tool's primary interval look better than measured. |
| **Source** | **Director.** |
| **Caught by** | The builder, verifying the refusal text against the fixture before shipping it -- `int(0.9098 * 100)` returned 90, not 91. |
| **Severity** | **Medium.** It reached the **ratified charter**. Nothing computed from it, but it is the number an operator is meant to make a decision on. |
| **Replaced by** | **90.98%** in the charter and in the refusal, with the reason stated: round a bound in the direction that keeps it true. |
| **Status** | **CLOSED** -- discharged by `9d66392`: 90.98% in the charter and in the refusal|

**This is the first correction sourced to the director**, and the counts table has read `Director | 0`
through thirty-one entries. Recorded because a table that counts the builder's errors and never the
director's is not measuring honesty, it is measuring who writes the entries.

**How it happened is the useful part, and it is not carelessness.** The director changed *"about
91%"* to *"as little as 91%"* and **the framing got better while the number got worse.** "About" is a
loose claim that 0.9098 satisfies. "As little as" is a precise one that it does not. The edit
improved the sentence and broke it in the same stroke, and it read well enough to be ruled into a
ratified document.

**The director's own note on the shape**, recorded because it revises a characterisation in the
record: C-19 said *"my instruments have been wrong about what the contract's action is, never about
what the code does."* That held for five instances. **This is the second break, after C-26** -- and
both breaks came when the director was correcting someone else.

**The rule is worth more than the fix.**

> **Round a bound in the direction that preserves it.** Rounding to nearest is correct for a
> measurement and wrong for a bound, because a bound is a claim about everything *outside* your
> sample, and rounding toward the middle silently weakens it.

---

## C-33 - Two more bounds rounded toward the middle, both ours

| | |
|---|---|
| **Claimed** | (a) `docs/STANDARDS.md` S-2.4 and `tests/test_clopper_pearson.py`: the worst Clopper-Pearson agreement after `DIGITS = 12` record rounding is **2.6e-07**. (b) `PROJECT_CHARTER.md` NEXT queue: largest-remainder rounding costs at **worst 0.73%** of variance. |
| **Actually** | (a) **2.627713e-07**, so 2.6e-07 understates the worst by rounding down. (b) `docs/STANDARDS.md` S-1.7 records **0.7316%**; the charter's 0.73% rounds it down too. Both claim a tighter bound than was measured. |
| **Direction** | Both toward the flattering answer. (a) makes our record format look more precise than it is; (b) makes the ruled rounding method look cheaper than it is. |
| **Source** | **Builder (Claude Code)** |
| **Caught by** | The sweep the director ordered after **C-32** -- *"start with any figure in the record described as 'worst', 'at most' or 'no more than'."* Both were found in the first pass. |
| **Severity** | **Low each, notable together.** Neither changes a decision. What they show is that the class was already present twice before anyone named it. |
| **Replaced by** | **2.7e-07** and **0.74%**, rounded away from the middle. |
| **Status** | **CLOSED** -- discharged by `9d66392`: 2.7e-07 and 0.74%, rounded away from the middle|

**The sweep also confirmed three figures that were already right**, which is what makes it a
measurement rather than a hunt: `8.4e-11` from 8.383e-11, `7.3e-13` from 7.281e-13, and S-1.7's own
`0.7316%` in STANDARDS. Each rounds **up**, away from the middle, and each is a real bound. So the
error is not systematic -- it is what happens when a figure is copied into prose without asking which
direction is safe.

**Where to look next.** Any figure in this record described as *worst*, *at most*, *no more than*, or
*as little as*. The sweep covered those four words. It did not cover a bound stated without one of
them, and that is the harder case.

---

## C-34 - A checker that stated a scope it did not have

| | |
|---|---|
| **Claimed** | `tools/check_claims.py`, `defined_ids` docstring: *"Obligations are spread across two files -- O-1..O-6 in STANDARDS.md, the rest in DECISIONS.md -- so both are read."* |
| **Actually** | They are spread across **three**. The phase contracts are where a phase opens the obligations it discovers, and the function never read them. **Seven were invisible**: O-8, O-16, O-17, O-18, O-20, O-21, O-24. Any code or test citing one would have been told it was undefined. |
| **Direction** | Against the checker's own coverage, and it hid the gap rather than leaving it open. |
| **Source** | **Builder (Claude Code)** |
| **Caught by** | A D2.8 test citing **O-20** for the first time. The citations check called a real obligation undefined, which is the checker reporting a true fact about itself in the form of a false one about the record. |
| **Severity** | **Medium.** Nothing was wrong in the record; the instrument could not see a third of the obligations and said it could. |
| **Replaced by** | `OBLIGATION_SOURCES`, a tuple the function walks, with `scope_of()` rendering it for humans. **The documented scope is now derived from the behaviour**, pinned by `test_the_documented_scope_is_the_scope_walked`. Contracts matched by glob so a Phase 3 contract is covered the day it is written. |
| **Status** | **CLOSED** -- discharged by `9d66392`: `OBLIGATION_SOURCES` walked, `scope_of()` rendering it|

**This is a different kind from the seven instrument-coverage instances before it, and the director
named the difference:**

> A checker with **no** stated scope invites someone to ask. A checker with a **wrong** stated scope
> answers the question before it is asked, and answers it falsely. **A reader who checks the
> docstring comes away more confident and less correct.**

That is why the fix is not "correct the sentence." A sentence written beside the behaviour drifts
from it; the seven earlier instances are all that shape. **The scope has to be the same object the
code walks**, so there is no second copy to go stale.

**A documented scope is a claim, and claims get checked.** That is rule 9 -- a checked number can
carry an unchecked claim -- applied to the one place nobody thought to apply it: the checker's own
description of itself.

---

## C-35 - S-1.2 was cited as governing a formula it states differently

| | |
|---|---|
| **Claimed** | `src/prevalence_kit/stratified.py`, `neyman_raw` docstring: *"Neyman allocation, before rounding. **S-1.2**, specification pinned by S-2.3."* And `docs/contracts/PHASE-2-CONTRACT.md`'s D2.3 row, governing standard: *"**S-1.2** Neyman (1934) · S-1.3 Cochran 3rd ed."* |
| **Actually** | **Neither source writes our formula.** S-1.2 minimises at `n_h` proportional to `M_h * S_h` with `S_h^2 = M_h * sigma_h^2 / (M_h - 1)`, and develops the **without-replacement** variance at its (37). S-1.3 writes the optimum the same way and carries an explicit fpc term at (5.27). Ours is `M_h * sigma_h`, with-replacement, no fpc -- charter §6.2. The two differ by a per-stratum `sqrt(M_h / (M_h - 1))` |
| **Direction** | Against the citation, not the arithmetic. It named a primary source as the origin of a formula that source does not contain, in the deliverable whose whole shape is *the expected value predates the implementation* |
| **Source** | **Builder (Claude Code)** |
| **Caught by** | Reading S-1.2 and S-1.3, on the director's instruction, before building the strata layer. **Nothing else could have caught it**: Barnett Table 2B states its design in **weights, not stratum sizes**, so the only external anchor this allocation has cannot express the factor |
| **Severity** | **Medium.** No shipped number is wrong and none changes. What was wrong is a citation, in the register that exists so a reader can check a method against its source |
| **Replaced by** | S-1.2's register role narrowed to **origin of the method**; the divergence recorded with both measurements and their design spaces; D2.3's row and docstring reciting **charter §6.2 and S-2.3** as governing. Ruled 2026-08-29: **keep the formula, fix the citation** -- adopting the paper's form would trade a witnessed formula for one no instrument here can check |
| **Status** | **CLOSED** -- discharged by `8dbfcad`: S-1.2 narrowed to origin of the method; D2.3 recites charter 6.2|

**This is the wrong claim that F-9 exposed, and the two are not double-counting.** F-9 is the
finding -- the record cited a source it had not read against the code it governs. C-35 is the
**claim that reached a commit** because of it. The register holds the defect; this table holds the
sentence.

**The uncomfortable half is how long it was checkable and unchecked.** S-1.2 sat at `not read` for
two phases while being cited as a governing standard, which is exactly **O-24's distinction**: a
source that anchors an **arithmetic** can be validated by reproduction, and a source that anchors a
**formula's provenance** has to be read. The reproduction against Barnett was real and it was never
evidence about S-1.2's text.

---

## C-36 - The table that counts our counting errors was over by one

| | |
|---|---|
| **Claimed** | The counts table above, committed: **Reviewer instrument `2` open, `3` total**, and **Total `36` open, `37` total** |
| **Actually** | **Two** reviewer-instrument entries exist, not three: **C-21** (noted) and **C-26** (open). So that row is `1` open, `2` total. The open total is **35**, not 36. The `37` total was right, and the Total column's own figures summed to **38** rather than 37 -- the overstatement was visible on the face of the table to anyone who added it up |
| **Direction** | Against the artifact, and **toward the less flattering answer for once**: it counted one more reviewer-instrument error than the record contains. The open total moved down, not up |
| **Source** | **Builder (Claude Code)** |
| **Caught by** | **Deriving the table from the entries instead of guessing them**, on the director's instruction to prioritise D2.14(b). The derivation was written before the numbers were read |
| **Severity** | **Low in magnitude, and it is the location that earns the entry.** This is the count treadmill inside the table that records the count treadmill |
| **Replaced by** | The recomputed table, plus **the semantics written down** below it so the next reader does not have to re-derive them, and so D2.14(b) has a specification to check against rather than a number to copy |
| **Status** | **CLOSED** -- discharged by `d096da0`: the table derived; D2.14(b) now checks it by machine|

**Why the number was wrong is worth more than the number.** C-21's own text says *"Second recorded
instance; **fifth overall in the class**."* The **class** tracks instances that never got a
C-number; the **table** counts entries. Someone reading a class tally into a table of entries is the
most likely way this arose. **That ambiguity is the thing D2.14(b) has to remove**, and it is why
the fix is a written definition rather than a corrected integer.

**Second time in two days that the same scope question surfaced** -- the first was whether F-9
warranted a C-number at all. A question asked twice is a specification missing once.

---

## C-37 - A register field that should not exist

| | |
|---|---|
| **Claimed** | `docs/STANDARDS.md` gained a field recording **how a source reached this machine**, alongside the citation and the read state. It was filled in for S-1.2 and referred to in that entry's read-state row |
| **Actually** | **The register has no such field.** It carries what a source **is**, when it was checked, and what came back. Every other entry is already written that way -- S-5.2 is *fetched 2026-08-28, HTTP 200*; S-2.1 is *4.5, re-verified live 2026-08-29*. **Not one of them says where a copy came from**, and none is weaker for it |
| **Direction** | Toward recording something **about a person rather than about the work**. Nothing methodological was wrong, which is exactly what made it easy to write and easy to miss |
| **Source** | **Reviewer instrument.** The field was the reviewer's invention; **the builder correctly declined to fill it in** and left it open rather than assuming an answer |
| **Caught by** | The director, reading the register as a stranger would |
| **Severity** | **Medium**, and it is about **where it landed**, not what it said. No estimate, pin or read state depended on it |
| **Replaced by** | The register's **fourth rule** and `CLAUDE.md`'s **rule 20**, both stating the boundary so the field cannot be reinvented. The entry now carries only the citation, that the artifact is the publisher's copy, the read state with its sections, and the OCR caveat |
| **Status** | **CLOSED** -- discharged by `14305f1`: the register's fourth rule and CLAUDE.md rule 20|

**The line the rule draws, and it is not "no routes."** Cochran's rendering route **stays**, because
rendering a scan to images **changes what was read** -- a rendered page is not a text layer, and a
reader must know which they are trusting. The EU legal notice's hand transcription stays for the
same reason. **A route that changes what you read belongs in the register; a route that says where
a copy came from does not.**

**Why this is the reviewer's and not the builder's, recorded because the attribution is the
director's to give.** The builder wrote the row, and it was the reviewer that introduced the field
as something a register ought to have. Presented with it, the builder **refused to fill it in** and
said the answer was not its to supply -- which was right, and which is why the entry sat visibly
incomplete instead of quietly wrong. **An invented field with an honest blank is still an invented
field.**

**A coincidence worth flagging so nobody misreads it later.** This entry moves the
reviewer-instrument row to **2 open, 3 total** -- the same figures the counts table carried
*incorrectly* before **C-36** corrected them. **C-36 was still right**: at that time only two
entries existed. The row now reads 3 because a third was added, not because the old number is
vindicated.

---

## C-38 - "A published number carries its own evidence of which method produced it"

| | |
|---|---|
| **Claimed** | Commit `d25e6fe`, the D2.8 message: *"`interval` is a required key with no default, validated against wilson / clopper_pearson, and it reaches as_record() -- so changing the interval changes the plan hash and **a published number carries its own evidence of which method produced it**."* Recorded as discharging **O-22** at the plan file |
| **Actually** | **Both clauses are true and the conclusion does not follow.** `plan.interval` was read by **nothing**: it appeared once in `src/`, inside `as_record()`. `_estimate_from` ended in `return wilson(positives, len(labels))`, unconditionally. **A plan naming `clopper_pearson` was answered with a Wilson interval** -- `[0.123160913235, 0.375030967423]` where Clopper-Pearson gives `[0.108396638984, 0.384511677303]`. The published number carried evidence of a method it did not use |
| **Direction** | Against the operator, in the one field **D-37** exists to protect. Q7 refused a *silent substitution* of interval method as **V-1's and V-7's class**; this was the same substitution, shipped, in the ordinary path |
| **Source** | **Builder (Claude Code)** |
| **Caught by** | The builder, reading `_estimate_from` before wiring the stratified draw into it -- and **confirmed by the director independently**, who reproduced it end to end: CLI prints `method wilson`, `verify` reports the estimate reproduced |
| **Severity** | **High.** It reached a commit and a push, it was live on the only design that runs end to end, and **`verify` could not see it** |
| **Replaced by** | Two fixes. `_estimate_from` dispatches on `plan.interval` through `INTERVAL_METHOD`. And `verify` **cross-checks `estimate.json`'s method against the plan** -- `ESTIMATE_METHOD_MISMATCH`, both controls. **F-10** |
| **Status** | **CLOSED** -- discharged by `f67e5b4`: `_estimate_from` dispatches; `verify` cross-checks the method|

**Why `verify` agreed with the defect, which is the part that outlives the fix.** `verify` recomputes
the estimate by calling **the same `_estimate_from`**. So it reproduced the same Wilson interval,
compared it to the recorded Wilson interval, and reported the estimate reproduced. **The instrument
agreed with the defect because it shared the defect** -- and `estimate.json` recorded
`method: "wilson"` beside a plan saying `clopper_pearson`, two artifacts in one run directory
contradicting each other, with nothing comparing them.

**That is Q-2 arriving as a live failure rather than a caveat.** Q-2 is registered permanently
`noted`: the suite is the builder's, written from one understanding, wrong in both places when that
understanding is wrong. It has now produced a live defect twice.

**The durable fix is the cross-check, not the dispatch, and the director's reasoning is why.**
Dispatch makes the two artifacts agree **today**. It does nothing about the next field added to the
plan going inert the same way. The comparison is one line, has a distinct code and both controls,
and **does not depend on the dispatch being right**.

**This is O-20 and O-22's shape running backwards.** Those were *honoured at the API, still owed at
the plan file* -- and both were **written down as obligations**. This one was honoured at the plan
file, never wired to the estimator, and recorded as **discharged**. A half-built commitment that is
named stays visible; one that is announced complete does not.

**The class it belongs to is already in this file: a checked figure carrying an unchecked claim.**
`test_core.py:168` asserts `interval` reaches `as_record()`. That is the half that worked. Nothing
asserted the field was **used**, and the passing test is why nothing looked.

---

## C-39 - The plan pre-registered the evidence and nothing enforced it

| | |
|---|---|
| **Claimed** | `SECURITY.md` 1.3, ratified before Phase 1 code: *"The plan is hashed before any data is touched. This is pre-registration. The estimand, the **population**, the design and the **label source** are fixed and stamped before the first row is read."* Charter 5.5: *"`verify` can say no -- so its yes means something."* |
| **Actually** | **Stamped, and not enforced.** `plan.population` was read in exactly one place -- `report.py`, **to print it** -- and never opened or compared to the frame actually sampled. **`plan.labels` was read by nothing at all.** The CLI takes both paths as separate arguments. So a run could be drawn from a file the plan does not name: `verify` reported **nine checks and exit 0**, and the report printed `Population: frame_APPROVED.txt` beside a number every one of whose ids began `other-` |
| **Direction** | Against the operator, the auditor and the reader at once, in the property the whole tool exists to provide |
| **Source** | **Builder (Claude Code)** |
| **Caught by** | **The director's probe**, named at the review stop: *for every field in the hashed plan record, what reads it, and what happens if it changes?* Run by the builder, reproduced end to end by the director |
| **Severity** | **Critical.** **V-1 defeated pre-registration of the plan. This defeated pre-registration of the evidence, which is the thing the plan is about** |
| **Replaced by** | `EVIDENCE_NOT_PREREGISTERED`, refused at `sample` and `ingest-labels` -- before the label budget, Q2's reason. **Resolved paths, never strings**, with the plan's value resolved against the **plan file's directory**, stated in the schema docs. Both resolved paths in the message. The path used is recorded in the ledger beside the declared one, D-24's shape. **The report takes the population from the record, not from the commitment** |
| **Status** | **CLOSED** -- discharged by `c5f71c1`: `EVIDENCE_NOT_PREREGISTERED`, and the report reads the ledger|

**A defect against a stated protection, not a limit -- and doctrine rule 9 requires saying
which.** SECURITY 1.3 was written before Phase 1 code and claims the population and the label
source are fixed and stamped. Phase 1 did not meet that claim. **Phase 1 is not reopened**:
the record is corrected here and the fix lands in Phase 2, which is **C-27's precedent
exactly**. A dated document keeps its sentence; this entry is the correction.

**Why no instrument found it, and this is the part that generalises.** `grep -rn
"\.population\|plan\.labels" tests/` returned **nothing**. Not a weak test -- **no test at
all**. F-10 at least had a test checking the half that worked. Two plan fields have now been
inert, and **neither was found by an instrument**: one by reading code and asking what reads a
field, one by the director naming the probe.

**The third will be found the same way unless the schema declares its own intent.** That is
the fix that outlives this one: every field marked *behavioural* must be read somewhere, every
field marked *declarative* must not select behaviour, and a checker asserts both. Ruled into
**D2.14**. `estimand.description` is inert and **correct** -- it declares intent rather than
selecting behaviour -- and today nothing in the record distinguishes that from an accident.

**The report was the worst of it.** A number computed from one file, printed beside the
filename of another, in the artifact an outsider reads and the one the report itself tells
them to re-check. **C-16's class**, at a severity C-16 never had. The report now reads the
ledger, because **the record is what happened and the plan is only what was promised**.

---

## C-40 - A containment claim that my own table disproved

| | |
|---|---|
| **Claimed** | Review-stop report, O-26's witness question, 2026-08-30: *"In `two_stratum` the binomial interval **does not contain the design estimate at all**."* |
| **Actually** | It contains it. `0.180098 <= 0.305000 <= 0.326781`. So do the other two: `0.080000` in `[0.059298, 0.107106]`, and `0.011333` in `[0.009198, 0.042940]`. **All three are contained**, and all six numbers were printed in the table immediately above the sentence |
| **Direction** | Toward the conclusion I was arguing for. It made the case look stronger than the evidence, in the paragraph doing the persuading |
| **Source** | **Builder (Claude Code)** |
| **Caught by** | The director, checking the sentence against the table above it |
| **Severity** | **Medium.** Nothing was built on it and the ruling it supported was correct for a different reason. What is medium is where it sat: a false claim inside a request for a ruling, which is the one place a claim is doing work rather than describing it |
| **Replaced by** | The true argument, which does not depend on a coincidence of three designs: **containment is not validity.** The pooled `k/n` estimates a **different quantity** from the design-weighted estimate, so a binomial interval around it is not an interval for the design estimate whether or not the two happen to overlap. **Coverage is the test, not containment**, and coverage is precisely what an interval built on the wrong estimand cannot deliver |
| **Status** | **CLOSED** -- discharged by `feab599`: the true argument recorded: containment is not validity|

**The class, counted from the artifact rather than from memory: this is the fifth**, after
C-27, C-28, C-29 and C-31. A figure that is right, carrying a sentence about it that nobody
checked. **The numbers were not merely available -- they were in the table the sentence sat
under.**

**Why the argument survived it, which is the part worth keeping.** Two of the three designs
give a pooled `k/n` that is a **different number** from the design estimate -- `0.020000`
against `0.011333`, and `0.246154` against `0.305000`. That is the real defect and it is
enough on its own: an interval centred on the wrong quantity is not an interval for the right
one. **Overlap was never the question.** I reached for the more dramatic claim when the
duller one was true and sufficient.

---

## C-41 - A question number issued twice

| | |
|---|---|
| **Claimed** | The O-26 ruling request numbered its question **Q13** |
| **Actually** | **Q13 and Q14 were already taken** -- Q13 is strata membership (**D-39**) and Q14 is `STRATUM_UNDECLARED` (**D-40**), both ruled 2026-08-30. The question is **Q15** |
| **Direction** | Against the record's own citation scheme. This project cites questions by number across the contract, the decisions log and the code |
| **Source** | **Builder (Claude Code)** |
| **Caught by** | The director |
| **Severity** | **Low in effect, and it has a root cause worth more than the fix.** A duplicate number in a record whose questions are cited by number would send a later reader to the wrong ruling |
| **Replaced by** | Renumbered to **Q15**, and **Q13 and Q14 written into the contract**, which is where the collision came from |
| **Status** | **CLOSED** -- discharged by `feab599`: renumbered to Q15; Q13 and Q14 written into the contract|

**The root cause, and it is D-28's shape.** Question numbers are **allocated in
`docs/DECISIONS.md`** -- D-39 says *"the director's Q13 ruling"*, D-40 says *"Q14"* -- while
the visible list of questions is the `### Qn` sections in the **phase contract**. Q13 and Q14
were ruled and recorded as decisions and **never got contract sections**. So scanning the
contract for the next free number returned 13, correctly, against a list that was missing two.

**Two lists that must agree, with nothing making them agree.** That is the same defect as
V-16's documented-versus-executed gate and `SUPPORTED_ROUNDING` versus `Rounding`, and it has
the same answer: **something has to make them agree.** Both sections are written now, and the
reconciliation is folded into **D2.14** -- every `Q-n` a decision claims must have a section
in the contract that opened it.

---

## C-42 - A conclusion about a text from an incomplete reading of it

| | |
|---|---|
| **Claimed** | Director's review of the A-5 draft, 2026-08-30: the replacement *"silently drops two clauses from the ratified text"* -- A-4's Rogan-Gladen promise and its general refusal principle -- and *"one of them is the correction you just built"* |
| **Actually** | **Both were always there**, as the draft's last two sentences. A new sentence had been inserted **before** them, which is what makes the paragraph read as though it ends at the vocabulary. In the director's own words: *"I read 875,910p and concluded about text at 916"* |
| **Direction** | Against a draft that had nothing wrong with it, and toward more work rather than less -- the instruction was to restore what was already present |
| **Source** | **Reviewer instrument.** Attributed as the director gave it |
| **Caught by** | The builder, checking the artifact before acting on the finding. The director then re-read and withdrew it |
| **Severity** | **Low in effect** -- nothing was changed on the strength of it, because the check came first. Notable in kind |
| **Replaced by** | Nothing to replace in the draft. **The half of the instruction that was right was applied**: A-4 said *"when sensitivity and specificity are supplied"* and left the mechanism to inference, and the row now states the commitment -- hashed plan fields, both or neither, validated at load |
| **Status** | **OPEN** - closes with the rest under **T-1 (D2.12)** |

**Second instance of one shape, and the director named it as such: concluding about an artifact
from an incomplete reading of it.** The first was **C-26**, where a summarising fetch dropped a
character and produced a finding about a spelling that was correct. Both were about **what a
document says**, and in both the remedy was the same -- **go back to the artifact and read the
part the conclusion is about.**

**The rule this project already had is what caught it.** *When the director pushes back, treat
it as a review finding: check, do not defend.* The check was cheap -- two `grep`s -- and it ran
before anything was edited, which is the only reason this entry says "nothing was changed on
the strength of it".

**And the finding was still worth having.** The half that survived is the stronger half of the
row. A reviewer wrong about one clause and right about another is the ordinary case, and
treating the whole finding as void because part of it failed would be its own error.

---

## C-43 - A source described as a methodology manual when it is a teaching page

| | |
|---|---|
| **Claimed** | `docs/STANDARDS.md`, and after it the Phase 2 contract at Q12: **S-1.13** is *"Statistics Canada, official methodology, read"* |
| **Actually** | It is **Statistics Canada, *Power from Data!*, section 3.2.2** -- an official Statistics Canada publication and an **educational** one. Their methodology manual is *Survey Methods and Practices* (12-587-X) and **has not been read**. Verified by re-fetching the page 2026-08-30, HTTP 200, date modified 2021-09-02 |
| **Direction** | **In our favour**, and in the way this register keeps finding: the source is real, the sentence is real, and the description makes the support sound one rank stronger than it is |
| **Source** | **Builder (Claude Code)** |
| **Caught by** | The builder, adding the register row the entry never had. **The row is what forced it** -- rule 4 of the register asks for a pin, a URL and a re-check date, and none of the three can be written without going to the artifact |
| **Severity** | **Low in effect, and worth the entry anyway.** The sentence it supplies is correct and the two rulings that rest on it are unaffected: strata are mutually exclusive and covering, whichever Statistics Canada document says so |
| **Replaced by** | A full S-1.13 row naming the publication, the URL, the fetch, the date modified and the re-check date, and stating that the methodology manual is a different document that has not been read |
| **Status** | **OPEN** - closes with the rest under **T-1 (D2.12)** |

**A second, smaller thing came with it, and it is the same shape one level down.** The register
quoted the source as **two** fragments -- *"homogeneous, mutually exclusive groups"* and
*"independent samples are selected from each stratum"* -- which reads as two statements
supporting two rules. **It is one sentence.** One sentence quoted twice is one piece of
evidence, not two, and the corrected row says so.

**Why an entry rather than a quiet fix.** The description reached three committed documents and
**anchored two rulings** -- Q12, where it was the reason a one-stratum plan is not refused, and
Q14 / D-40, where it is the reason an undeclared unit cannot be dropped. That is the register's
own admission rule: it counts claims that reached a commit **or changed a ruling**, and this did
both.

**And it says something about where the gap was.** S-1.13 had a **read state** and no **register
row**, so `O-24`'s check -- every entry carries one of four read states -- passed it. A check
that walks the read-state table cannot see an entry missing from the table beside it. **D-34's
shape, in the standards register**: the reconciliation ran in one direction only.

---

## C-44 - A deliverable that two artifacts name and the contract does not

| | |
|---|---|
| **Claimed** | `CLAUDE.md`: *"D2.1-D2.16 done, **D2.17** built"*, and again in its Done table |
| **Actually** | **The Phase 2 contract had no D2.17.** Section 3's deliverable table ran D2.1 to D2.16, and section 11's evidence table stopped at D2.16. The name was also committed inside two artifacts -- `svy/fixtures/design_intervals.json` records `"deliverable": "D2.17"` and `tests/test_design_intervals.py` opens with it -- so **three places used a deliverable number the binding document did not define** |
| **Direction** | Against the contract, and in the direction that matters most: **the contract is what "done" means.** A deliverable absent from it cannot be reported at close, and its exit checks cannot be written |
| **Source** | **Builder (Claude Code)** |
| **Caught by** | The builder, reading the record on a fresh window before doing anything else. **Not by an instrument** -- `check_citations` resolves `D-nn` decisions and `O-nn` obligations, and deliverable numbers are a different vocabulary that nothing walks |
| **Severity** | **Low in effect and high in kind.** No number is wrong. But O-26's work was real, shipped, and had no row in the document that defines the phase, which is how a phase closes with a deliverable nobody signed off |
| **Replaced by** | A **D2.17 row in section 3** naming its governing standard and obligation, and an evidence row in section 11. The direction was chosen deliberately: two committed artifacts already carried the name, so adding the row keeps the record consistent, where renaming would have edited artifacts to match a document |
| **Status** | **OPEN** - closes with the rest under **T-1 (D2.12)** |

**Why the contract was corrected rather than `CLAUDE.md`.** The director's instruction was
*"one of the two is wrong; decide which and make them agree."* The tie-break is that the name
is already **inside committed evidence** -- a fixture and a test file -- and evidence is not
edited to match a document. **The document was the thing missing a row.**

**And it is the same shape as C-41 one deliverable later.** Question numbers were allocated in
`DECISIONS.md` and listed in the contract, with nothing making the two agree; deliverable
numbers are allocated in commit messages and listed in the contract, with nothing making
*those* agree. **Two lists that must agree and no third thing making them.** That class now has
three instances here -- V-16's gate, C-41's questions, and this one.

---

## C-45 - A row count nobody counted, and the overclaim beside it

| | |
|---|---|
| **Claimed** | `CLAUDE.md`, committed at `d95a014`: *"**§8a is approved and is what the director runs.** Twenty-six rows, every command executed before it was written."* Repeated in the builder's handoff message, carried by the reviewer into the director's briefing, and repeated by the director in his own report of the hand-run |
| **Actually** | **34 rows.** Counted from the file: F1-F8, F8b-F8h, F9, F10, F10b, F11, F17-F25b, F12-F16. **And the second half was false too**: the commands were run for the rows written new and **not** for the fifteen carried unchanged from section 8 |
| **Direction** | **Up, and understating the work** -- the unusual direction for this register, which is the point of recording it. The overclaim beside it runs the usual way |
| **Source** | **Builder (Claude Code)**, for both halves. **The reviewer owns carrying the figure without counting**, and says so; the director repeated it from the briefing |
| **Caught by** | **The reviewer, counting**, after the hand-run was complete. Not by any instrument: `check_figures` covers three numbers in this file and a deliberately narrow set elsewhere, and a row count in a contract is not among them |
| **Severity** | **Low in effect, high in kind.** No command was wrong and no result changed. But the figure sat in the file **the next session reads first**, beside a claim about verification coverage that was also untrue, and the director ran a 34-row checklist believing it had 26 |
| **Replaced by** | The corrected row in `CLAUDE.md` naming the hand-run's dated reading, and `docs/contracts/PHASE-2-HAND-RUN.md`, whose header says **34 because it was counted** |
| **Status** | **OPEN** - closes with the rest under **T-1 (D2.12)** |

**Two claims in one sentence, and only one of them was even checkable.** *"Twenty-six rows"* is a
number a reader could have verified in ten seconds and nobody did. *"Every command executed before
it was written"* is not checkable from the artifact at all -- it is a claim about the past, and the
only person who could falsify it was the one making it. **C-27's shape**, and this time the
uncheckable half was the one that mattered: it is what made the checklist look verified when
fifteen of its rows were inherited.

**The count travelled through three people and was checked by none of them.** The builder asserted
it, the reviewer carried it into a briefing, the director repeated it back. **Each stage looked
like corroboration and none of them was a measurement** -- the same structure as C-24's ratio and
C-7's file count, at the scale of a working relationship rather than a file.

**Why it is recorded even though nothing broke.** The admission rule counts claims that reached a
commit. This one reached `CLAUDE.md` at `d95a014`, and `CLAUDE.md` is the file that misleads the
next session **before it has read anything else**.

---

## C-46 - The report stated a count that was not a count

| | |
|---|---|
| **Claimed** | Every stratified report, console `estimate` line and `estimate.json` since `eb17c9a`: *"N of M sampled items were positive"* |
| **Actually** | For both design intervals `N` was **`round(point * n)`** -- the design-weighted estimate multiplied back out. **Not a count of anything.** The director's hand-run printed `5` beside a `labels.csv` holding **10**; the builder's reproduction printed `3` beside a file holding **5** |
| **Direction** | **Either way, and that is what makes it worse than an overstatement.** It tracks the estimate, so it understates when positives concentrate in a low-weight stratum and overstates when they concentrate in a high-weight one |
| **Source** | **Builder (Claude Code)** |
| **Caught by** | **The director, reading a report by hand at the phase-close ritual** -- and reached through **F4, a checklist row that was wrong about something else entirely**. The reviewer then found the second instance, on the console line, in the transcript |
| **Severity** | **High.** A false statement of fact in the artifact an outsider reads, with `verify` returning nine checks and exit 0 |
| **Replaced by** | The true count, supplied by the caller that counted the labels, plus a per-stratum table -- **F-12** |
| **Status** | **OPEN** - closes with the rest under **T-1 (D2.12)** |

**C-16's class, and the third live instance of the seventh instrument-limit kind.** `verify`
recomputes through `_estimate_from`, the same function that produced the number, so it reproduced
the same fabricated count and reported the estimate verified. **No instrument in this project
could have caught it**, and the record already said so: *"no test the builder writes can close
`the suite is the builder's`."*

**The one-stratum case would have hidden it, and nearly did.** At `L = 1` the design estimate
**is** the pooled proportion, so `round(point * n)` equals the true count by construction. The
project shipped a one-stratum disclosure and a one-stratum test the day before, both green. **A
test written on the obvious case would have passed for the whole life of the defect**, which is
why F-12's closing test asserts the two numbers *differ* before asserting which one is recorded.

**What made it reachable at all was a wrong row.** F4 expected per-stratum figures the report had
never carried -- the builder restated that phrase from the superseded section 8 without deriving it
from a rendered report. **The director ran the wrong expectation, looked at the artifact, and found
a defect underneath it.** An argument for hand-runs that no test can make, and it is recorded as
such rather than as luck.

---

## The direction of our errors, and the first counterexample

**Every correction before C-9's discharge overstated in our favour.** That is what the record
kept finding: a bound rounded toward the middle (C-32, C-33), an agreement figure without its
axes (C-30), a claim about the world drawn from two packages (the *no witness exists* class), a
containment claim its own table disproved (C-40). The pattern is real and it is why the sweeps
were ordered.

**C-9 went the other way, and it is the first one that did.** Its sentence said the
cross-validation against R `survey` *"is not yet done"* -- **when it was done**, to 9.5e-15,
and had been since D2.3. The shipped package docstring **understated our own work**, in the
file read by people who never open the repository.

**Worth recording as such**, because the record has been quietly building a claim about the
direction of our errors, and a claim with no counterexample is a claim nobody has tested.
**This is the counterexample.** It also says something about the mechanism: the sentence was
true when written and expired when O-4 discharged, so the error was not optimism -- it was a
**live figure in prose** with nothing watching it, which is the same root as the count
treadmill.

**And it was found by bookkeeping rather than by review.** T-1 required each closed correction
to name its discharging commit; C-9's condition made that impossible to fake, and the
impossibility is what surfaced it.

---

## Classes, tracked separately from the count

A correction gets a C-number when it reached a commit. A **class** keeps its own tally, because a
pattern that stops being counted stops being visible. These threads include instances the table
above does not, and say so.

### Believed mechanism -- a claim about how something works, believed because it sounds right, never run

| # | Where | Reached a commit? |
|---|---|---|
| 1 | C-7 -- the ruff integer, quoted as a file count | yes |
| 2 | V-5 -- a chunk-count claim that no run supported | yes |
| 3 | C-10 -- Layer 3 said to fix V-2 on its own | yes |
| 4 | C-20 -- the exit-code argument said to rest on two checks | yes |
| 5 | V-14 -- a branch called unreachable that every existing user hits | yes |
| 6 | Barnett rounding, 2026-08-29 -- stratum 1 said to land on exactly 2098.5, with R's half-to-even rule producing 2098. The raw value is **2098.4952**, below the midpoint, so no tie-break is involved. Read "2098.50" in a two-decimal table and invented a mechanism for it | **no -- caught before commit** |
| 7 | Clopper-Pearson width, 2026-08-29 -- asserted "Clopper-Pearson is never narrower than Wilson", reasoning that it is the conservative interval. **Conservative means coverage at least 1 - alpha; it does not mean wider everywhere.** At k = 0 and n = 4000 it is about 4% narrower, and both endpoints have closed forms that say so. Caught by the test written to assert it | **no -- caught before commit** |

**Instances 6 and 7 have no C-number on purpose.** Neither reached a commit, and the table above
counts what escaped. Recorded here so the class keeps its count.

**Both were caught by the artifact rather than by rereading.** Instance 6 by the fixture printing the
raw value; instance 7 by the test written to assert the false property. Neither would have been found
by thinking harder about it.

**The fix is the part worth keeping.** The raw allocation print went from two decimals to four, so
the display that caused the misreading no longer exists. That is rule 14: not a resolution to read
more carefully, but a changed artifact where the mistake is no longer available.

### A figure taken from a working step rather than re-derived from the artifact

| # | Where | Reached a commit? |
|---|---|---|
| 1 | C-7 -- ruff's summary integer quoted as a file count | yes |
| 2 | C-14 -- the docs/src ratio, counting files the label did not name | yes |
| 3 | The CRAN/p3m file count, 2026-08-29 -- "353 of 355" counted tar entries including 14 directories. **TW-5 reported 339 of 341 on its first run and was right** | **no -- the instrument corrected it first** |
| 4 | **C-24** -- the CP/Wilson ratio quoted from the linear approximations, not the widths | yes |

**Three of the four were caught by something mechanical**, not by rereading: ruff itself, the
director re-deriving all six rows of a table, and TW-5 contradicting its own author on its first
run.

### A checked figure carrying an unchecked claim

The number is machine-derived. The property beside it is not. The sentence reads as one verified
statement, and nothing in it says where the checking stops.

**This is worse than an unchecked claim on its own.** An unchecked claim invites scrutiny. A
half-checked one deflects it, because the part a reader can verify is right.

| # | Where | The checked half | The unchecked half |
|---|---|---|---|
| 1 | **C-27** | "23 reason codes" -- counted from `Reason` by `check_claims` | "each with both controls" -- false for `PLAN_MISSING`, at both its raise sites |
| 2 | **C-28** | "reconciled against the code by `tools/check_claims.py`" -- it did reconcile | "20 accepted, 20 closed" -- 18 were closed, and four accepted findings had no row |
| 3 | **C-29** | "423 tests, selftest 9/9" -- true of the tree I measured | "seven green" -- false of the tree I committed, which failed 3 tests |
| 4 | **C-31** | S-1.1 calls Jeffreys' **average** coverage excellent -- it does | read as "coverage", when the same section records a deep spike near p = 0 |
| 5 | **C-40** | six figures printed in a table, all correct | *"does not contain the design estimate at all"* -- written directly under the table that disproves it |

**The rule: when a checked figure sits in a sentence with an unchecked property, either check the
property or split the sentence.**

Both instances were in Phase 1's closed outcome, written in the same section, on the same day.

### "No witness exists" -- a claim about the world, made by looking at two packages

Three times this project concluded nothing implements a method. **Three times it was wrong, and
every time in our favour.** The search space was always **D-3's two-library shortlist**, never the
world.

| # | Concluded | Actually | Found |
|---|---|---|---|
| 1 | Rogan-Gladen has no library witness (**O-8**) | `epiR` implements it | D2.5 research, **D-31** |
| 2 | Clopper-Pearson has no published table, check against an implementation we write (**§2.3**) | base R `stats::binom.test` | D2.4, **S-2.4** |
| 3 | Neither `survey` nor `svy` implements exact optimal allocation, so it cannot be witnessed (**charter NEXT**) | `stratallo` 3.0.1, **already in our pinned snapshot** | 2026-08-29, **S-1.12** |

**None was found by looking.** Each turned up sideways -- while researching a deliverable, while
writing a test, while being told to consult official sources on something else.

**The shape.** *"Not in `survey` or `svy`"* is a finding: a search was run and its scope is known.
*"No witness exists"* is a claim about all of CRAN and PyPI. The first was true every time. The
second was inferred from it, and **nothing in this project has ever been entitled to make it.**

It is the same class as an agreement figure without its axes and a worst case without its grid: **a
claim whose scope is the sample you took, stated as though it were the population.** That is now
three of the record's classes with one root.

**The rule:**

> **A negative claim about the world records the search that produced it** -- what was searched, how,
> and when. Without that it is not a finding, it is an absence of evidence wearing a finding's
> clothes.

**Instance 3 is the worst of the three**, because the witness was not merely findable -- it was
*already inside the pinned image*, installable with no network call the project had not already made.
Nobody had asked.

**One live claim of this shape survived the sweep**, and it was narrowed rather than re-searched: the
charter's per-stratum Se/Sp deferral said the corrected variance has *"no published anchor in
`docs/STANDARDS.md`, so nothing could witness it."* The premise is correctly scoped to our own
register; the conclusion is not, and no search of CRAN or PyPI was ever made for it. Now stated at
the width of what was checked. **Two others -- §2.3 and eval-bridge -- were already honestly scoped.**

### One pyproject setting, two costs

`addopts = "-q"` is set once and has now cost something twice, both times by **doubling** into
`-qq`, which suppresses the total pytest prints.

| # | Where | What it cost |
|---|---|---|
| 1 | **E11**, Phase 1 | The exit check that exists to print the test count could not print it. CI ran `pytest -q` on top of the setting. Closed phase; recorded there |
| 2 | **2026-08-29** | `check_figures`' new collect call passed `-q` and got per-file counts with no total, returning `-1`. **Inside the checker written to catch stale counts.** Fixed with `-o addopts=` |

**Neither was a bug in the setting.** `-q` is a reasonable default. The cost is that it is
invisible at every call site, so anyone reaching for `-q` gets `-qq` and no error. CLAUDE.md has
said *"never `pytest -q`"* since Phase 1 and it happened anyway, which is the argument for the
flag being explicit at the call rather than remembered.

### A worst case measured over a grid is an upper bound on the worst case

**Not the axes rule restated.** The axes rule says a figure names what varied and what was pinned.
This is stronger and narrower: **for any minimum or maximum taken over a sampled space, a finer
sample can only find a more extreme value.** So the number is a bound, and the direction of the bound
is known.

It applies to every min or max this project reports over a grid, not only to coverage.

| # | Figure | The grid | Consequence |
|---|---|---|---|
| 1 | Worst coverage of Wilson / Clopper-Pearson / Jeffreys | `p = gamma/n`, gamma in [0.5, 15] **step 0.25** | The director re-measured at step **0.05** and found **0.9537** where step 0.25 reports **0.9540** |
| 2 | *"Worst gap found anywhere: 0.7316% of variance"* — S-1.7's optimality search | 37,910 random designs, window +/- 2 units | Already stated at the width of its search. It says *"stated at the width of the search"* and it was right to |

**Both grids are kept, not reconciled.** Two grids disagreeing in the fourth decimal is evidence about
the method of measurement, and averaging them away would destroy that evidence. The witness records
its step; the director's is recorded beside it.

**The wording that follows from it.** *"covers about 91%"* reads as a point fact about typical
behaviour. **"Covers as little as 91%"** is what an upper-bound-on-the-worst-case supports, and it is
the framing an operator needs. The charter says the second.

**Recorded because the builder had the insight and then wrote the prose the other way, minutes
apart.** The upper-bound property was established in one message and the honest-limits bullet was
drafted with "about" in the next. Knowing a thing and writing it are different acts, and the gap
between them is where this class lives.

### A figure measured along one axis and stated as though along all of them

The measurement is real. The sentence reporting it does not say which dimensions
were explored and which were pinned, so the natural reading is wider than the
evidence.

| # | Where | Varied | Held fixed, unstated |
|---|---|---|---|
| 1 | **C-30** (a) | `n`, 1 to 1,999,514, and `k` across each | `conf.level = 0.95` |
| 2 | **C-30** (b) | the same | the same -- and this figure moved 38x when the axis was added |
| 3 | **C-30** (c) | the same | the same -- and the *characterisation* was false outside 0.95 |

**The rule: an agreement figure states its axes -- what was varied, over what
range, and what was held fixed.** *"7.1e-11 across 23 cases, n = 1 to 1,999,514"*
becomes *"... all at confidence 0.95"*, which is the same measurement at its real
width.

**F-8 is the same gap seen from the other side.** `confidence` was unvalidated in
every interval estimator and no fixture could have found it, because no fixture
varied it. A parameter no instrument points at is a parameter nothing defends.

### An instrument that does not cover what it appears to

| # | Where | What was not covered |
|---|---|---|
| 1 | C-15 / D-23 | F-4 was closed in the test fixture and regressed into the shipped example. Three instruments looked at the repository and none looked there |
| 2 | C-19 / V-12 | `verify` printed `[ok]` for a check that never ran |
| 3 | V-15 | `check_paths` read a fixed list of globs, so a new document was silently uncovered |
| 4 | V-16 | CI ran six of the gate's seven checks. No test file was type-checked on the remote |
| 5 | C-23 | `check_gate` read `gate.yml` with a regex, so it passed a file GitHub cannot parse |
| 8 | **C-34** | **A fifth kind, and worse than the others.** `defined_ids` did not merely cover less than it appeared to — it **stated a scope it did not have**. The seven above leave a reader free to ask what is covered; this one answers first, and wrongly. **The fix is structural: the scope is the tuple the code walks, not a sentence beside it** |
| 6 | **D-34** | `check_findings` validated the rows present and could not see a row missing. V-12..V-15 were named across three to nine documents each with no register row, while the checker reported "22 findings, all accounted for" |
| 7 | **C-27** | `check_codes` reconciles `Reason` against the contracts both ways, so it looks like the reason-code checker. **It never asks whether a code fires.** `PLAN_MISSING` had no control at either raise site for a phase and a half, and the "23 reason codes" count was derived by that same checker |
| 9 | **F-9** *(2026-08-29)* | **A sixth kind: a fixture that looks external and is not.** `r/fixtures/stratified.json` carries four **allocation** fixtures produced inside the pinned R witness image, and every signal around them — an R script, a digest-pinned image, a `survey` version recorded beside them — reads as an outside check. **`survey` has no allocator.** `r/stratified_fixtures.R` says so itself at line 18, and its `neyman()` is **our own formula re-implemented in R by the same author**. So **the allocation half of D2.3 has never had an external witness**, while sitting in the file that holds the estimation fixtures that do |

**The rule this class produced** is in `CLAUDE.md` beside the others.

**Why the sixth kind is not the fifth.** C-34 stated a scope it did not have, in a sentence a reader
could go and check. This one states nothing false anywhere: the R script is **honest in its own
comment**, the register never claimed `survey` allocates, and no number is wrong. What misleads is
**the company the fixture keeps** — an external witness and an internal re-implementation in one
file, one format, one directory, generated by one script in one image. **A reader checks the
provenance of the file, not of the row.**

It is also the reason **D2.16 is worth more than it looked.** `stratallo`'s `round_oric` and
`rnabox` would be the **first genuine outside check on allocation this project has ever had** — not
a second opinion on work already witnessed, which is how D2.16 was justified when it was opened.

---

## What produced these six

Recorded so the pattern is visible, not to assign blame.

| Pattern | Entries | The shape |
|---|---|---|
| A chat-drafted claim never checked against the thing it describes | C-2, C-3, C-6 | Three of six. All three were *plausible* readings of a real source, and all three were wrong about what the source says. |
| A figure passed through from an upstream report unverified | C-4, C-5 | Both are citation-shaped: a venue and a number, both copied rather than fetched. |
| A queued finding used as a premise before its ruling | C-1 | The most serious, and the only *process* failure rather than a fact failure. |

**Three of six were caught only by reading the primary source end to end** rather than checking that
it existed. Existence checks would have passed all six.

## Rule-14 obligation

Each correction that can become a failing test becomes one, rather than living in this prose:

| Correction | Check to build | Owner |
|---|---|---|
| C-2 | Overclaim scanner: fail the build if any published text asserts a regulation requires prevalence | Phase 3 |
| C-3 | Standards-register check: fail if any method cites a source not marked official in `STANDARDS.md` | Phase 1 |
| C-5 | Claim-search checker: find every restatement of a figure across files, per rule 14 | Phase 1 (O-7) |
| C-6 | Assert the coverage demo's estimand names an explicit threshold, and that the plan hash covers it | Phase 3 |
