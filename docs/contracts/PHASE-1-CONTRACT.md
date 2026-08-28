# Phase 1 contract — the proof slice

**Status: APPROVED — 28 August 2026. Amended at the review-stop close (D-17, D-18).**
Building is authorised. The addition and the E2-complement answer are marked ▸ **AMENDED** below.

| | |
|---|---|
| **Phase** | 1 of 4 |
| **Name** | Proof slice |
| **Tier** | **STANDARD** — re-asked below, §8 |
| **Proposed** | 28 August 2026 |
| **Governing charter** | `PROJECT_CHARTER.md`, ratified 2026-08-28 |
| **Predecessor** | Phase 0 — closed, commit `5b4f97f` |

---

## 1. Objective

**Get the whole spine working end to end on the simplest possible estimator.**

One command chain — `plan` → `sample` → `ingest-labels` → `estimate` → `verify` → `emit-report` —
running on synthetic data, producing a stamped report, with a chain that `verify` can break.

Phase 1 is not about statistics. It ships exactly one estimator, Wilson on a simple random sample,
because the point is to prove the **governance** works: pre-registration, sealing, the ledger, the
refusals, and a report an outsider could check. Phase 2 makes the statistics honest. Phase 1 makes
them *governed*.

**The load-bearing core is built before any surface.** Plan hashing, sealing, and the ledger come
first. The CLI and the report come last. If the core is wrong, a pretty CLI hides it.

## 2. Deliverables

Each names the top standard it must follow, from `docs/STANDARDS.md`.

| # | Deliverable | Governing standard |
|---|---|---|
| D1.1 | **Plan schema and loader.** YAML. Fields: estimand (including any threshold), population, design, label source, seed. Frozen dataclasses. | Charter §4 `plan` · S-6 toolchain |
| D1.2 | **Pre-registration hash.** The plan is canonicalised and hashed **before any data file is opened**. The hash is the chain's genesis block. | S-5.3 (SHA-256, FIPS 180-4 — to be pinned, O-1) |
| D1.3 | **Hash-chained ledger.** Append-only. Every step links to the previous. Each entry records step, timestamp, inputs by digest, outputs by digest. | S-5.3 · Charter §5.5 |
| D1.4 | **Sealed store.** Fernet, chunked. Encrypt on ingest. Safe preview only — length, digest, harm flags. Explicit, logged unseal. | S-5.1 · D-9 · SECURITY §3.7 |
| D1.4b ▸ **AMENDED** | **Ordered chunk-digest manifest + total chunk count**, bound into the ledger entry for the ingest step. `verify` checks it. Truncation, reordering and substitution become detectable defects with distinct reason codes. | **D-14** · SECURITY §3.7 |
| D1.5 | **`sample` — simple random sampling.** Deterministic under a recorded seed. Same seed, same sample, byte-identical, asserted. | Charter §4 `sample` |
| D1.6 | **`estimate` — Wilson interval.** Point estimate and 95% interval for a proportion. | **S-1.1** Brown, Cai & DasGupta (2001), DOI `10.1214/ss/1009213286` |
| D1.7 | **`verify` — the whole chain.** Re-check plan hash, sample determinism, ledger integrity, and reproduce the estimate from the sealed record alone. | Charter §5.5 |
| D1.8 | **`emit-report`.** Markdown and JSON. Estimate, interval, design, n, every hash, and a mandatory **Honest Limits** block asserted present by test. | Charter §4 `emit-report` · §8 |
| D1.9 | **Zero-network proof.** A test that fails if any network-capable package appears in the runtime dependency tree, or if any runtime code imports a network module. | Charter §5.1 · D-2 |
| D1.10 | **No-AI-in-evidence-path proof.** A structural test proving no AI-produced value can reach labels or estimates. | Charter §5.2 |
| D1.11 | **Refusal gates**, each with a distinct reason code, a negative control, and a **positive control**. | Charter §6.4 · doctrine rule 5 |
| D1.12 | **Standards-register check.** Fails the build if any method cites a source not marked official in `docs/STANDARDS.md`. | Discharges C-3's rule-14 obligation |
| D1.13 | **Claim-search checker** with a selftest. Finds every restatement of a figure across files. | Discharges **O-7**, doctrine rule 14 |
| D1.14 | **Tripwire check script.** TW-1, TW-2, TW-3 — all three are scriptable. | Discharges **O-2** · `docs/TRIPWIRES.md` |
| D1.15 | **Package scaffolding.** `pyproject.toml`, hash-locked dependencies, ruff, mypy strict, pytest, CI on 3.12 / 3.13 / 3.14. | **S-6** · D-10 |
| D1.16 | **Synthetic fixture generator.** Reproducible, seeded, with a known true proportion. | — |
| D1.17 ▸ **AMENDED** | **Sealed copy of the plan**, so `verify` can check the plan without the working file, plus the on-disk re-hash when the file is present. | **D-15** |

## 3. Requirements

**R1 — Pre-registration is real, not decorative.** `plan` must hash before opening any data file.
The test proves it by pointing the plan at a data file that **does not exist** and asserting the plan
hash is still produced. If the hash needs the data, it is not pre-registration.

**R2 — Determinism is byte-identical.** Same plan, same seed, same input → the sample file is
byte-identical across runs and across the 3.12 / 3.13 / 3.14 CI matrix. Asserted, not assumed.

**R3 — Every gate proves it can fail *and* that it can pass.** For each refusal in D1.11: a negative
control demonstrating refusal, a positive control demonstrating acceptance, and a **distinct reason
code**. A suite asserting only "this was rejected" passes when the gate rejects everything for the
wrong reason.

**R4 — Content never leaks.** No content in logs, error messages, tracebacks, report output, or
ledger entries. Asserted by a test that seeds a known sentinel string into the content and greps
every output artifact for it.

**R5 — `verify` reproduces from the sealed record alone.** Given only the sealed store and the
ledger — no original input files — `verify` recomputes the estimate and matches. This is the claim
the whole tool rests on.

**R6 — Both linters, both halves.** CI runs `ruff check` **and** `ruff format --check`. One green
says nothing about the other. `mypy` in strict mode.

**R7 — Honest Limits block is mandatory.** `emit-report` cannot produce a report without it. A test
asserts its presence and that it carries the charter's §8 limits verbatim, including the
sampling-only interval caveat.

**R9 ▸ AMENDED — the chunk sequence is authenticated, not just each chunk.** Fernet authenticates
chunks individually. The **manifest and count**, bound into the ledger, authenticate the sequence.
`verify` must discriminate four distinct failure modes by reason code, not collapse them into one.
The discriminator is a **multiset** comparison: if the count matches, the order differs, and the
multiset of digests still matches the manifest, that is a reorder; if a digest is absent from the
multiset, that is a substitution. Without the multiset step both look like "digest at position *i*
is wrong", and one code covering both is exactly the undifferentiated refusal doctrine rule 5
forbids. *(D-14.)*

**R10 ▸ AMENDED — the plan is checked twice, and a skipped check is stated out loud.** `verify`
checks the sealed plan copy against the genesis hash **always**, and the working plan file on disk
**when it exists**. When the on-disk check is skipped because the file is absent, `verify` says so
in words in its output. Silence would let an operator believe both checks ran. *(D-15.)*

**R8 — Plain English.** Error messages and report text follow the charter's writing rule. Every
refusal message says what went wrong and what to do about it.

## 4. Named refusals for Phase 1

Each gets a distinct reason code, a negative control, and a positive control.

| Code | Fires when |
|---|---|
| `PLAN_HASH_MISMATCH` | The plan changed after the chain started |
| `PLAN_INVALID` ▸ **AMENDED** | The plan is missing a required key, or a value is the wrong shape |
| `PLAN_MISSING` ▸ **AMENDED** | The sealed copy of the plan is absent from the run |
| `LEDGER_BROKEN` | A ledger link does not match its predecessor's digest |
| `SEAL_TAMPERED` | A sealed chunk fails Fernet authentication |
| `SEAL_TRUNCATED` ▸ **AMENDED** | Fewer chunks present than the manifest count |
| `SEAL_REORDERED` ▸ **AMENDED** | Count matches, order differs, digest multiset still matches the manifest |
| `SEAL_MANIFEST_MISMATCH` ▸ **AMENDED** | A chunk digest is absent from the manifest multiset — substitution |
| `SEED_MISSING` | The plan has no recorded seed, so the sample could not be redrawn |
| `ESTIMATE_MISMATCH` | `verify` recomputes a different estimate than the one recorded |
| `LABELS_UNMATCHED` | Labels do not correspond one-to-one with the drawn sample |
| `EMPTY_SAMPLE` | n = 0 — no interval is defined |
| `RUN_ALREADY_OPEN` ▸ **AMENDED** | `plan` was run into a workspace that already holds a measurement |
| `RUN_NOT_FOUND` ▸ **AMENDED** | The run directory does not exist -- a mistyped path, not a broken ledger |
| `RUN_NOT_LINEAR` ▸ **AMENDED** | An evidence step repeats, or the steps are recorded out of order, or a step name is unknown |
| `SEAL_ALREADY_WRITTEN` ▸ **AMENDED** | A second seal into the write-once `plan.sealed` store |
| `SEAL_ID_COLLISION` ▸ **AMENDED** | A sealed directory already belongs to a different item id |
| `KEY_MISSING` ▸ **AMENDED** | The sealing key is absent (was reported as `SEAL_TAMPERED`, and on the `verify` path as a raw `FileNotFoundError`) |
| `PLAN_THRESHOLD_INVALID` ▸ **AMENDED** | The threshold does not fit the comparison: non-numeric under `at_least`, or numeric under `equals` |
| `LABEL_NOT_NUMERIC` ▸ **AMENDED** | A label value is not a number and the estimand compares numerically |
| `FRAME_EMPTY` ▸ **AMENDED** | The sampling frame has no rows |
| `FRAME_TOO_SMALL` ▸ **AMENDED** | The frame holds fewer items than the plan asks for |
| `CONTENT_TOO_LARGE` ▸ **AMENDED** | A CSV field exceeds the reader's ceiling |

**23 reason codes at Phase 1 close (`d66d225`).** A dated figure, not a live one -- Phase 2
adds more, and the live total is in the Phase 2 contract §6 where the checker reads it. `EMPTY_SAMPLE` used to carry four of these situations at once, which told an operator nothing about which of four different things to fix.
| `PLAN_MISSING` ▸ **AMENDED** | The sealed plan copy is absent, so check (a) of D-15 cannot run. *(A missing **working** plan file is not a failure — see R10.)* |

## 4b. The linearity rule ▸ **AMENDED**

Stated here in the words it was ruled, so nobody has to infer it:

> **Linearity binds the four evidence steps — `plan`, `sample`, `ingest-labels`, `estimate` — at
> most once each, in that order. `report` may repeat, and each emission appends its own entry.**

Enforced in two independent places. `do_plan` refuses a workspace that already holds a measurement;
`verify` refuses a non-linear ledger regardless of what wrote it, because an auditor may be handed a
record this code never produced.

**Why strict, and this fact is load-bearing.** Every step raises its `Refusal` *before*
`ledger.append`, so a failed step writes no entry. The ordinary retry-after-a-mistake workflow
therefore passes untouched, and a repeated step in a ledger is always a repeated *success* — a step
that completed, produced a result, and was then deliberately done again. That is not a usability
case. Asserted by `test_a_failed_step_writes_no_entry`, not assumed. *(D-17.)*

**Why `report` is exempt.** Re-emitting cannot change the number — the estimate is already sealed
and chained — and a record of every emission is something an auditor wants, not something to forbid.
Ruled before `emit-report` was built, deliberately.

## 5. Out of scope for Phase 1

Named, so scope creep is visible rather than absorbed.

- Stratified sampling, Neyman allocation, Clopper-Pearson, Rogan–Gladen — **all Phase 2**
- R `survey` and `svy` cross-check fixtures — **Phase 2**
- The Civil Comments coverage demonstration — **Phase 3**
- Any DSA-shaped emitter — **NEXT queue**
- Importance sampling, ML-assisted weights — **NEXT queue**
- Key management beyond documenting where the key lives — **SECURITY §3.1**
- Any release, tag, publish, or push to a remote

**If a feature wants a fifth phase, it goes to NEXT instead.** Charter §4.

## 6. Review stop

**Placement: after D1.1 through D1.7 and D1.9 through D1.11 — before the CLI surface, the report
emitter (D1.8), and the three checker tools (D1.12–D1.14).**

That is the point where the load-bearing core exists and nothing pretty is hiding it yet.

At the stop, the builder will:

1. **Quote exact lines** proving each core guarantee — where the plan hash is computed relative to
   the first file open; where the ledger link is verified; where the seal is authenticated. Not
   summaries. Summaries hide defects; quoted lines surface them.
2. **Hunt its own defects** against the charter, `docs/DECISIONS.md`, and `docs/STANDARDS.md`.
3. Report every finding with a proposed disposition and the evidence behind it.

**The director closes each finding. The builder never closes its own.**

Reminder from the method, and it is measured rather than assumed: across the third governed build,
roughly a quarter to a third of defects reached the director undetected by the builder. The builder
writes the code and the test from one understanding; when that understanding is wrong, it is wrong
in both. The stop exists to convert the director's independent position into caught defects.

## 7. Exit checklist — what the director runs and reads

Nothing is claimed done until the director has run these himself and reported what he saw.
Expected results are stated **in advance**, including exit codes.

| # | Command | Expected |
|---|---|---|
| E1 | `prevalence-kit plan examples/synthetic/plan.yaml` | Prints the plan hash. **Exit 0.** |
| E2 ▸ **RESTATED** | **Leave the plan file untouched. Rename or move the population file so it is absent from disk.** Rerun E1. | **Same plan hash as E1, byte for byte. Exit 0.** Proves R1. |
| E3 | `sample` → `ingest-labels` → `estimate` → `emit-report`, full chain | A report at a named path. **Exit 0.** |
| E4 | **Read `report.md` by eye** | Estimate, 95% interval, design, n, every hash, and an Honest Limits block. Does it read in plain English? Does the interval look sane against the synthetic truth? |
| E5 | `verify` | **Exit 0.** Prints each link checked. |
| E5b ▸ **AMENDED** | Scramble a ledger's step order — e.g. `plan, estimate, sample, ingest-labels` — **re-chaining every link honestly**, then rerun `verify` | **Non-zero exit. Reason code `RUN_NOT_LINEAR`.** |
| E6 | Delete the original input file, rerun `verify` | **Exit 0.** Proves R5 — it reproduces from the sealed record alone. |
| E7 | Edit one byte in the ledger, rerun `verify` | **Non-zero exit. Reason code `LEDGER_BROKEN`.** Not a stack trace. |
| E8 ▸ **CORRECTED** | Edit **any field in the plan file** — the estimand, the seed, the population — then rerun `verify` | **Non-zero exit. Reason code `PLAN_HASH_MISMATCH`.** *(The drafted wording said "edit one label in the plan". Plans contain no labels. Builder's drafting defect, corrected.)* |
| E8b ▸ **AMENDED** | Run the **full chain through ingest and estimate first**, and only **then** edit the plan file. Rerun `verify`. | **Non-zero exit. Reason code `PLAN_HASH_MISMATCH`.** Post-ingest edits are covered — see §7b. |
| E8c ▸ **RESTATED** | **Delete the working plan file** (do not merely omit `--plan` -- see below), then rerun `verify` | **Exit 0.** The plan line reads `[--] ... NOT CHECKED`, names the recorded path, and the summary reads **`N checks, 1 not performed`** -- never "nothing out of place". Proves R10. |
| E8d ▸ **AMENDED** | Run the full chain. Then edit the plan, **re-run `plan`**, and re-run the full chain into the same workspace. Rerun `verify`. | **Non-zero exit, named reason code, and the code must NOT be `ESTIMATE_MISMATCH`.** Expect `RUN_ALREADY_OPEN` at the re-plan. |
| E9 | Edit one byte in a sealed chunk, rerun `verify` | **Non-zero exit. Reason code `SEAL_TAMPERED`.** |
| E9b ▸ **AMENDED** | **Drop the final chunk** of a sealed item, rerun `verify` | **Non-zero exit. Reason code `SEAL_TRUNCATED`.** |
| E9c ▸ **RESTATED AGAIN** | **Swap `0000.bin` and `0001.bin` of item `item-0154`** in `<run>/sealed/` — the one deliberately multi-chunk item in the shipped example — then rerun `verify` | **Non-zero exit. Reason code `SEAL_REORDERED`.** Distinct from E9 and E9b, which use the same item. |
| E10 | `grep -ri "<sentinel string>"` across every output artifact | **No matches.** Proves R4. |
| E11 ▸ **RESTATED** | `pytest` (**not** `pytest -q`) | All pass, and **the count is printed**. `pyproject.toml` already sets `addopts = "-q"`, so `pytest -q` is `-qq`, which suppresses the summary line -- an exit check whose command cannot produce its own evidence. Expected at this commit: **see the count in the phase outcome**, compared against the number printed. |
| E12 | `ruff check . && ruff format --check . && mypy --strict src` | All clean. Both ruff halves. |
| E13 | Run the zero-network test | Passes. **Then add `httpx` to the dependencies and run it again — it must fail.** A guard that has only ever passed is a decoration. |
| E14 | Run `tools/check_claims.py --selftest` | Passes, and demonstrates it catches a planted mismatch. |
| E15 | Run the tripwire script | Reports TW-1/2/3 against the 2026-08-28 baselines. |

**E8c's action is deleting the file, not omitting the flag.** Omitting `--plan` no longer skips
anything: `verify` falls back to the path recorded in the plan ledger entry. The two actions
produced identical output under the old semantics, which is how V-12 survived a hand-run --
`docs/CORRECTIONS.md` C-19.

**E2's action is stated as an action on the *filesystem*, not on the plan.** The original wording -- *"point the plan's data path at a nonexistent file"* -- reads naturally as *edit the plan so it names a file that does not exist*. Under that reading the plan record changes, so the hash changes, and the stated expectation of "same plan hash" is **false**. The check is that the hash does not depend on the *data*; the path is part of the commitment and is supposed to affect it. The director performed the correct action and the hash was identical.

*The reviewer's harness had encoded the wrong reading:* it edited the plan and printed `same as the real plan? False` with a note explaining why that was acceptable. That is §7a's stated limit -- **a second instrument is not an independent truth** -- demonstrating itself on the first occasion it mattered. Recorded as evidence for that sentence rather than as an assertion of it. `docs/CORRECTIONS.md` C-17.

**E8d exists because E8 and E8b both passed while E8d failed.** Both of those edit the plan file; neither re-runs `plan`, which is the path that actually defeated pre-registration. A checklist that only tests the path the builder had in mind is a checklist testing the builder.

**E7, E8, E8d, E9, E9b, E9c and E13 are the ones that matter most.** They are the phase's real product:
gates that demonstrably refuse, for named and **distinct** reasons. E9, E9b and E9c must produce
**three different reason codes** — if any two collapse into one, the gate has not been built.

---

## 7a. The reviewer harness is not the exit checklist ▸ **AMENDED**

**E1–E15 stay as written, as CLI invocations, and the director runs them for real at phase close
when D1.8 exists.** The reviewer harness — a director-run script driving the core Python API and
printing reason codes for the director to read by eye — is an **additional instrument for the review
stop, not a replacement for the ritual, and it does not discharge any exit check.**

Why not `pytest` instead: doctrine rule 4 says green tests prove self-consistency, not meaning. The
suite is the builder's, written from one understanding and wrong in both places when that
understanding is wrong. The director running `pytest` is the director running the builder's
instrument and reading the builder's assertions — the exact substitution the stop exists to prevent.
The exit-check-to-test mapping is retained as **supporting evidence that each check has a test
behind it**, never as the check itself.

### What the harness does not reach ▸ **AMENDED**

Recorded before anyone later reads "the harness passed" as more than it was.

* **It observes reason codes, not exit codes.** It calls the Python API directly. Nothing about
  process exit status is exercised, and E1, E3, E5, E6, E8c and E11–E15 all state expected exit
  codes that remain untested.
* **No report exists, so E4 and R7 are untested.** The Honest Limits block, and reading a report by
  eye, are the parts of the exit checklist that most need a human, and neither has happened.
* **A second instrument is not an independent truth.** The harness was written by the reviewer, from
  the reviewer's reading of this contract, so it carries the reviewer's blind spots the way the
  builder's suite carries the builder's. What it removes is the *shared* blind spot between the code
  and the tests, which is the specific thing it was for — not blind spots in general.

**What it did establish, at that width:** 24 damage cases each produced the reason code this
contract names; E9, E9b and E9c produced three distinct codes on a real multi-chunk item; and R4 was
clean across 91 written files.

## 7b. E2 complement — are post-ingest plan edits covered by E8?

**Asked by the director at approval. Answer: yes, and here is why — plus one thing that was not
covered until D-15.**

The genesis hash is fixed when `plan` runs. `verify` recomputes the plan hash and compares. **The
timing of an edit does not change the mechanism** — an edit before ingest, after ingest, or after
the report is emitted all produce the same recomputed-hash mismatch and the same reason code. So
E8 covers post-ingest edits, and **E8b pins that with an actual check.**

*The director's instruction was "if yes, state it in the contract". E8b is added beyond that
instruction, and this note flags it as the builder's choice so it can be struck. The reason is
doctrine rule 14: a lesson that lives only in prose will not hold. "Timing does not matter" is a
claim about behaviour, and a claim about behaviour should be a test.*

**What answering this turned up, and it is a real finding.** Re-hashing only the on-disk plan — the
behaviour the drafted E8 implied — **cannot survive E6**, the check that deletes the original inputs
and requires `verify` to reproduce from the sealed record alone. If the plan exists only on disk,
the plan is not part of the sealed record and **R5 is false**. Conversely, checking only a sealed
copy would keep verifying while the file the operator actually reads has been edited.

Hence **D-15: check both.** The sealed copy always; the working file when it exists; and say so
when the second is skipped. This changed D1.2 and D1.7 before any code was written, which is what
the question was worth.

## 8. Tier re-ask — a named deliverable of this phase

Per the charter §7 and the method's binding re-ask.

**Current tier: STANDARD. Stated default: remain at STANDARD.**

**Discharge standard, fixed now before any evidence exists:** moving to FULL requires the director to
name, in a numbered ruling, a **concrete finding attributable to a FULL-only practice**. Not a
feeling that more ceremony would be safer.

**Forecast, recorded in advance:** the re-ask will probably not fire. Phase 1 ships no irreversible
act — no tag, no publish, no deploy, no remote push. FULL's distinguishing practices are rehearsal
of the irreversible and a heavier written record, and Phase 1 has nothing irreversible to rehearse.

Recording the forecast now means the re-ask can be *wrong*, which is the only way it is worth
running.

### Discharged — 28 August 2026 ▸ **AMENDED**

**Ruling: remain at STANDARD.**

The discharge standard, fixed before any evidence existed, was that moving to FULL requires naming a
concrete finding attributable to a FULL-only practice. **No such finding can be named.** V-1 — the
most serious defect in the phase — was found by the Reviewer role and by adversarial execution at
the review stop. Both are STANDARD practices.

**The forecast, recorded in advance, said the re-ask would probably not fire. It did not.** The
verdict rests on an absence, which needs no counterfactual; any gloss that "FULL would have found it
sooner" is a claim about a run that never happened.

## 9. Carried obligations owned by Phase 1

| # | Obligation | From |
|---|---|---|
| O-1 | Pin S-5.2 (OpenSSF/SLSA) and S-5.3 (SHA-256 / FIPS 180-4) to exact documents | Phase 0 |
| O-2 | Build the tripwire check script | Phase 0 |
| O-7 | Build the claim-search checker with a selftest | Phase 0 |
| O-9 | Implement and test Fernet chunking; assert chunk-boundary behaviour | D-9 |
| O-11 ▸ **AMENDED** | Chunk-digest manifest bound into the ledger; four distinct reason codes | **D-14** |
| O-12 ▸ **AMENDED** | `verify` states in words when the on-disk plan check was skipped | **D-15** |
| — | Document concretely where the sealing key lives, for SECURITY §3.1 | Phase 0 |

Each is reported at close as **discharged**, or as **unmet with a named blocker**. A partial counted
as a pass is how an obligation quietly stops constraining anything.

## 10. Deviations and outcome

**Phase 1 CLOSED — 29 August 2026, commit `d66d225`.** Closed on evidence the director produced
himself: E1-E15 run by hand in a clean workspace outside the repository, exit codes read from
`$LASTEXITCODE` at every step, then re-run after V-12.

### Evidence per deliverable

| # | Deliverable | Evidence |
|---|---|---|
| D1.1-D1.2 | Plan schema, pre-registration hash | **E2**: population file renamed away, plan untouched -> identical hash `6b1a20a6...`, exit 0 |
| D1.3 | Hash-chained ledger | **E7**: one byte edited -> `LEDGER_BROKEN`, exit 2 |
| D1.4 / D1.4b | Sealed store + ordered chunk manifest | **E9/E9b/E9c** on `item-0154`, 4 chunks: `SEAL_TAMPERED` / `SEAL_TRUNCATED` / `SEAL_REORDERED`, three distinct codes, all exit 2 |
| D1.5 | SRS, deterministic | **E5**: 40 ids redrawn from the frame, identical |
| D1.6 | Wilson | **E3**: `0.225000000000`, CI `[0.123160913235, 0.375030967423]`, n=40, 9 positive |
| D1.7 | `verify` | **E5** eight `[ok]` lines; **E6** exit 0 with `frame.txt` and `labels.csv` off disk -- R5 by hand, sample redrawn and estimate recomputed from the sealed record with the originals not on the machine |
| D1.8 | `emit-report` | **E4** read by eye. Produced C-16: the report listed 4 entries where `verify` reported 5. Fixed; the report now states the count `verify` will report, asserted correct by test |
| D1.9 | Zero-network proof | **E13**: guard went **red** on `['httpx']`, tree reverted clean. The failure is the pass |
| D1.10 | No-AI-in-evidence-path | `test_no_ai_module_reaches_the_evidence_path`, all seven evidence modules |
| D1.11 | Refusal gates | 23 reason codes, each with both controls |
| D1.12-D1.14 | Checkers | **E14**: six planted violations, all caught. **E15**: TW-1/2/3 against baselines |
| D1.15 | Package, CLI, CI | **E12** both ruff halves + `mypy --strict src` exit 0. **CI has never executed** -- see deviations |
| D1.16 | Synthetic fixture | Regenerated by `tools/make_example.py` after C-15 |
| D1.17 | Sealed plan copy | **E8c**: `[--] NOT CHECKED`, `8 checks, 1 not performed`, exit 0 |

**E11** at the hand-run: 221 passed. **222 at close** (`d66d225`) -- the difference is the V-13
as-invoked-path test. Re-derived, not carried.

### Requirements

R1, R2, R4, R5, R6, R7, R8, R9, R10 met. **R3 met** -- every gate has both controls.

**R2 is met in the suite and NOT asserted across the matrix.** All 222 tests have only ever run on
Python 3.14.0, the only interpreter on this machine. R2 requires the sample to be byte-identical
across 3.12 / 3.13 / 3.14, "asserted, not assumed." **It is currently assumed.** The CI matrix is the
only instrument that asserts it, and CI has never run. Carried as **O-16**.

### Deviations

1. **The review stop ran three times, not once.** Round one: 7 builder findings, 10 missed. Round
   two: the report omitted 8 open findings including the highest severity. Rounds two and three were
   caused by defects in the *reporting*, not by the method asking for them. Remedy shipped:
   `tools/check_claims.py`.
2. **CI was built and never executed.** No remote is configured. `.github/workflows/gate.yml` was
   verified by reading, in a project whose doctrine says a gate that has only ever passed is a
   decoration -- this one has not even passed. **O-17.**
3. **The exit checklist was amended five times mid-phase** (E5b, E8d added; E2, E8c, E9c, E11
   restated). Each amendment is recorded in the contract with its reason. Four of the five came from
   the check being wrong rather than the code.

### Obligations

| # | Status |
|---|---|
| O-1 | **Discharged** -- SLSA v1.1, FIPS 180-4, `attest-build-provenance` v4.2.2, `scorecard` v5.5.0, each fetched live |
| O-2 | **Discharged** -- `tools/check_tripwires.py`, run live, none fired |
| O-7 | **Discharged** -- `tools/check_claims.py`, six checks, selftest proves each can fail |
| O-9 | **Discharged** -- `test_chunking_is_exact_at_the_boundary` plus the F-2 pair |
| Key location for SECURITY 3.1 | **Discharged** -- and 3.8 added for the path disclosure (V-13) |
| O-16 *(new)* | **Unmet, named blocker: no remote.** R2's cross-version determinism is asserted only by CI, and CI has never run. Owned by the next session's push |
| O-17 *(new)* | **Unmet, named blocker: no remote.** The gate workflow has never executed |

### Findings

**20 accepted, 20 closed**, each with named closing evidence in `docs/FINDINGS.md`, reconciled
against the code by `tools/check_claims.py`. Q-2 stays permanently `noted`: no test the builder
writes can close "the suite is the builder's".

### Corrections

**23 open**, 15 builder, 2 reviewer-instrument, 0 director. They close at the Phase 1 to 2 boundary
under **T-1 (D2.12)**, each naming the commit that discharged it.

### Tripwires at close

**Checked 2026-08-29 by `tools/check_tripwires.py --check`: TW-1, TW-2, TW-3 -- none fired.**

### What Phase 1 proves, at the width of the evidence

The spine works: a plan hashed before data, a chain that refuses, content sealed, a number that
`verify` recomputes from the record alone, and refusals with distinct names. It was hardened by 20
findings, of which the builder self-found 7.

**What it does not prove.** No estimator has been checked against anything neither the director nor
the builder wrote. That is Phase 2's whole shape.
