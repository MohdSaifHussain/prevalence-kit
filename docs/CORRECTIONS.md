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
| **Builder (Claude Code)** | **7** | **0** | **7** |
| Director | 0 | 0 | 0 |
| **Total** | **13** | **0** | **13** |

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
