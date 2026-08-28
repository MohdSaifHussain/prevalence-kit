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
| **Builder (Claude Code)** | **15** | **0** | **15** |
| Reviewer instrument | **1** | 0 | **2** (1 noted) |
| Director | 0 | 0 | 0 |
| Tool artifact (noted, not a defect) | - | - | **1** |
| **Total** | **22** | **0** | **23** |

C-1 … C-6 are Phase 0: defects in the chat-drafted vision, all caught before any code, none reaching
an artifact. **C-7 … C-13 are Phase 1, and all seven are mine.** Five were caught by the director's
reviewer and two by the director; **none was caught by my own review stop**, which is the measurement
of the limit I raised as Q2 rather than a separate finding.

**C-12 and C-13 are a different kind from the rest.** C-7 to C-11 are wrong statements. C-12 and
C-13 are wrong *reporting* — the statements were accurate and the omissions made them mislead. That
class does not show up by re-deriving a number, only by reconciling a report against the artifact.

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

**Note on the dated document.** `docs/PHASE-1-REVIEW-STOP.md` is **not** edited. It is a dated
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

**The class is now a property, not a run of luck.** Five occasions: the harness's clean frame that
never exercised V-7; the harness encoding the wrong reading of E2; the E8c command that omitted
`--plan` instead of deleting the file; and now a re-run directed into a dirty directory. The
director's characterisation, recorded verbatim at C-19, holds on all five:

> *My instruments have been wrong about what the contract's action is, never about what the code
> does.*

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
