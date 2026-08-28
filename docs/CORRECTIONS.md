# Corrections

Every claim that was wrong, who it came from, how it was caught, and what replaced it.

**The point of this table is that it is uncomfortable to write.** A project that claims its numbers
are checkable has to show the ones that were not. Errors are counted by source, separately, so
neither the director nor the AI can quietly absorb the other's.

**Source attribution is the director's, given at ratification**, and is recorded as given.

---

## Counts

| Source | Open | Closed | Total |
|---|---|---|---|
| Chat reviewer (draft author) | 3 | 0 | **3** |
| Research report (passed through unverified) | 2 | 0 | **2** |
| Stale-at-draft-time, queued but built on anyway | 1 | 0 | **1** |
| **Builder (Claude Code)** | **22** | **0** | **22** |
| Reviewer instrument | **2** | 0 | **3** (1 noted) |
| Director | 0 | 0 | 0 |
| Tool artifact (noted, not a defect) | - | - | **1** |
| **Total** | **30** | **0** | **31** |

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
| **Status** | **OPEN** — closes when README credits svy as the estimator layer |

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
| **Status** | **OPEN** |

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
| **Status** | **OPEN** |

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
| **Status** | **OPEN** |

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
| **Status** | **OPEN** |

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
| **Status** | **OPEN** |

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
| **Status** | **OPEN** — closes when a phase-close report ships using exit codes only |

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
| **Status** | **OPEN** — closes at Phase 1 close, when the claim-search checker (O-7, D1.13) can assert every `D-nn` and path citation in `src/` resolves |

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
| **Status** | **OPEN** — closes when O-4 is discharged and the sentence can be rewritten as a fact |

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
| **Status** | **OPEN** — closes when the V-1 mechanism is signed off at phase close |

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
| **Status** | **OPEN** — closes at phase close |

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
| **Status** | **OPEN** — closes at Phase 1 close, if every report between here and there carries the open list |

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
| **Status** | **OPEN** — closes at phase close |

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
| **Status** | **OPEN** - closes at phase close |

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
| **Status** | **OPEN** - closes at phase close |

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
| **Status** | **OPEN** - closes at phase close |

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
| **Status** | **OPEN** - closes at phase close |

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
| **Status** | **OPEN** - closes at the Phase 1 to 2 boundary |

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
| **Status** | **OPEN** - closes at the Phase 1 to 2 boundary |

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
| **Status** | **OPEN** - closes at the Phase 1 to 2 boundary |

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
| **Status** | **OPEN** - closes at the Phase 1 to 2 boundary |

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
| **Status** | **OPEN** - closes at the Phase 1 to 2 boundary |

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
| **Status** | **OPEN** - closes with the rest under **T-1 (D2.12)**, naming the commit that discharged it |

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
| **Status** | **OPEN** - closes with the rest under **T-1 (D2.12)** |

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
| **Status** | **OPEN** - closes with the rest under **T-1 (D2.12)** |

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
| **Status** | **OPEN** - closes with the rest under **T-1 (D2.12)** |

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
| **Status** | **OPEN** - closes with the rest under **T-1 (D2.12)** |

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
| **Status** | **OPEN** - closes with the rest under **T-1 (D2.12)** |

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
| **Status** | **OPEN** - closes with the rest under **T-1 (D2.12)** |

**This is the second instance of the class C-27 named, and it is why that class has its own rule.**
The sentence ends with *"reconciled against the code by `tools/check_claims.py`"*. That is true. The
checker did reconcile -- the 20 rows that were there. The numbers in front of it were written by
hand and neither was right.

A reader has no way to see where the checking stops.

**Phase 1 stays closed and its outcome keeps its sentence.** A dated reading is not rewritten. The
correction lives here.

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

**The rule: when a checked figure sits in a sentence with an unchecked property, either check the
property or split the sentence.**

Both instances were in Phase 1's closed outcome, written in the same section, on the same day.

### An instrument that does not cover what it appears to

| # | Where | What was not covered |
|---|---|---|
| 1 | C-15 / D-23 | F-4 was closed in the test fixture and regressed into the shipped example. Three instruments looked at the repository and none looked there |
| 2 | C-19 / V-12 | `verify` printed `[ok]` for a check that never ran |
| 3 | V-15 | `check_paths` read a fixed list of globs, so a new document was silently uncovered |
| 4 | V-16 | CI ran six of the gate's seven checks. No test file was type-checked on the remote |
| 5 | C-23 | `check_gate` read `gate.yml` with a regex, so it passed a file GitHub cannot parse |
| 6 | **D-34** | `check_findings` validated the rows present and could not see a row missing. V-12..V-15 were named across three to nine documents each with no register row, while the checker reported "22 findings, all accounted for" |
| 7 | **C-27** | `check_codes` reconciles `Reason` against the contracts both ways, so it looks like the reason-code checker. **It never asks whether a code fires.** `PLAN_MISSING` had no control at either raise site for a phase and a half, and the "23 reason codes" count was derived by that same checker |

**The rule this class produced** is in `CLAUDE.md` beside the others.

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
