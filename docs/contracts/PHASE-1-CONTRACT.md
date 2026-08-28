# Phase 1 contract — the proof slice

**Status: APPROVED — 28 August 2026, with one binding addition (D-14) ruled in.**
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
| `LEDGER_BROKEN` | A ledger link does not match its predecessor's digest |
| `SEAL_TAMPERED` | A sealed chunk fails Fernet authentication |
| `SEAL_TRUNCATED` ▸ **AMENDED** | Fewer chunks present than the manifest count |
| `SEAL_REORDERED` ▸ **AMENDED** | Count matches, order differs, digest multiset still matches the manifest |
| `SEAL_MANIFEST_MISMATCH` ▸ **AMENDED** | A chunk digest is absent from the manifest multiset — substitution |
| `SEED_MISSING` | The plan has no recorded seed, so the sample could not be redrawn |
| `ESTIMATE_MISMATCH` | `verify` recomputes a different estimate than the one recorded |
| `LABELS_UNMATCHED` | Labels do not correspond one-to-one with the drawn sample |
| `EMPTY_SAMPLE` | n = 0 — no interval is defined |
| `PLAN_MISSING` ▸ **AMENDED** | The sealed plan copy is absent, so check (a) of D-15 cannot run. *(A missing **working** plan file is not a failure — see R10.)* |

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
| E2 | Point the plan's data path at a nonexistent file, rerun E1 | **Same plan hash. Exit 0.** Proves R1. |
| E3 | `sample` → `ingest-labels` → `estimate` → `emit-report`, full chain | A report at a named path. **Exit 0.** |
| E4 | **Read `report.md` by eye** | Estimate, 95% interval, design, n, every hash, and an Honest Limits block. Does it read in plain English? Does the interval look sane against the synthetic truth? |
| E5 | `verify` | **Exit 0.** Prints each link checked. |
| E6 | Delete the original input file, rerun `verify` | **Exit 0.** Proves R5 — it reproduces from the sealed record alone. |
| E7 | Edit one byte in the ledger, rerun `verify` | **Non-zero exit. Reason code `LEDGER_BROKEN`.** Not a stack trace. |
| E8 ▸ **CORRECTED** | Edit **any field in the plan file** — the estimand, the seed, the population — then rerun `verify` | **Non-zero exit. Reason code `PLAN_HASH_MISMATCH`.** *(The drafted wording said "edit one label in the plan". Plans contain no labels. Builder's drafting defect, corrected.)* |
| E8b ▸ **AMENDED** | Run the **full chain through ingest and estimate first**, and only **then** edit the plan file. Rerun `verify`. | **Non-zero exit. Reason code `PLAN_HASH_MISMATCH`.** Post-ingest edits are covered — see §7b. |
| E8c ▸ **AMENDED** | Delete the working plan file, rerun `verify` | **Exit 0**, and the output **says in words** that the on-disk plan check was skipped. Proves R10. |
| E9 | Edit one byte in a sealed chunk, rerun `verify` | **Non-zero exit. Reason code `SEAL_TAMPERED`.** |
| E9b ▸ **AMENDED** | **Drop the final chunk** of a sealed item, rerun `verify` | **Non-zero exit. Reason code `SEAL_TRUNCATED`.** |
| E9c ▸ **AMENDED** | **Swap two chunks** of a sealed item, rerun `verify` | **Non-zero exit. Reason code `SEAL_REORDERED`.** Distinct from E9 and E9b. |
| E10 | `grep -ri "<sentinel string>"` across every output artifact | **No matches.** Proves R4. |
| E11 | `pytest -q` | All pass. Every refusal has both controls. |
| E12 | `ruff check . && ruff format --check . && mypy --strict src` | All clean. Both ruff halves. |
| E13 | Run the zero-network test | Passes. **Then add `httpx` to the dependencies and run it again — it must fail.** A guard that has only ever passed is a decoration. |
| E14 | Run `tools/check_claims.py --selftest` | Passes, and demonstrates it catches a planted mismatch. |
| E15 | Run the tripwire script | Reports TW-1/2/3 against the 2026-08-28 baselines. |

**E7, E8, E9, E9b, E9c and E13 are the ones that matter most.** They are the phase's real product:
gates that demonstrably refuse, for named and **distinct** reasons. E9, E9b and E9c must produce
**three different reason codes** — if any two collapse into one, the gate has not been built.

---

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

*Completed at phase close. Empty until then.*

| Deliverable | Evidence | Status |
|---|---|---|
| — | — | — |

**Deviations from this contract:** *(none yet)*

**Tripwire check at close:** *(pending)*

---

## Approval

- [x] Director approves this contract — **28 August 2026**
- [x] Binding addition ruled in — chunk-digest manifest, E9b, E9c, SECURITY §3.7 narrowed → **D-14**
- [x] E2 complement answered — §7b, and it produced **D-15**
- [x] Review stop placement, E13 httpx guard-proof, tier re-ask — approved as drafted

**Director's addition, verbatim:**

> §3.7's per-chunk authentication limit must be answered structurally, not only stated.
> Requirement: each seal record carries an ordered chunk-digest manifest + total chunk count; the
> manifest is bound into the ledger entry; verify checks it. Chunk truncation and chunk reordering
> become detectable defects with named reason codes. Add exit checks: E9b (drop final chunk -> named
> reason, nonzero exit), E9c (swap two chunks -> named reason, nonzero exit). SECURITY.md §3.7
> narrows accordingly: size leaks (stated limit); order/count tampering is DETECTED at verify.
> Record as a decision with the Cobblestone rejection (D-9) cross-referenced: having declined the
> spec that solves this, we carry the obligation ourselves.

**Build authorised 2026-08-28.**
