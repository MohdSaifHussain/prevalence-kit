# Decisions

Numbered, dated, with the reason, the alternatives not taken, and where the decision was actually
made. Decisions taken by default with no reason are recorded too, and marked as such.

A log that manufactures rationale after the fact is worse than no log, because it reads as evidence.

---

## D-1 — Tier: STANDARD, manual-approve

**Date:** 2026-08-28 · **Made in:** director's kickoff instruction · **Ruled by:** director

The build runs at STANDARD tier of the governed-orchestration method, manual-approve mode.

**Alternatives not taken.** FULL — rejected by the director at kickoff. The record here serves the
build; it is not itself the deliverable that a stranger must read as evidence. LITE — insufficient
for a four-phase build.

**Re-ask is binding.** The tier is re-asked at every phase boundary as a named deliverable. Default
is to stay at STANDARD. Moving to FULL requires a numbered ruling naming a concrete finding that
only FULL-tier ceremony would have produced.

---

## D-2 — `lean` estimators, with zero-network as the recorded rationale

**Date:** 2026-08-28 · **Made in:** ruling R-1 · **Ruled by:** director

prevalence-kit ships its own `lean` estimators rather than depending on `svy`.

**Reason, as ruled.** `svy` 0.25.0 declares a hard runtime dependency on **`httpx`**
(`Requires: httpx, msgspec, numpy, polars, scipy, svy-io, svy-rs`), which pulls in `httpcore`,
`anyio` and `certifi`. Hard Rule 1 is zero network calls at runtime, *proven by a test that fails if
any network capability appears in the dependency tree*. We cannot ship an HTTP client and make that
claim.

**The availability argument is retired.** The vision's stated reason — that svy's installable code
"was not yet publicly downloadable" — was **false** and is withdrawn. `pip install svy==0.25.0`
succeeded in a clean virtual environment on 2026-08-28. See `docs/CORRECTIONS.md` C-1.

**Alternatives not taken.**
- Depend on svy and weaken Hard Rule 1 to "no network calls made by us" — rejected: the claim would
  no longer be provable by the existing test.
- Depend on svy as an optional extra with `lean` as default — rejected: breaches the scope cap for
  no gain in v1.0.

---

## D-3 — Cross-check against R `survey` **and** `svy`, as independent witnesses

**Date:** 2026-08-28 · **Made in:** ruling R-1 · **Ruled by:** director

Every estimator that both libraries implement is validated against both, in a separate optional test
environment so the runtime dependency tree stays network-free.

**Reason.** Agreement with two independent implementations is stronger evidence than agreement with
one. The vision planned only R `survey`.

**Consequence.** Wilson and Clopper-Pearson can be checked twice (both libraries have them).
Rogan–Gladen can be checked against neither — `svy` has no misclassification correction and
`survey` has no Rogan–Gladen — so it is validated against the published worked results in
Lang & Reiczigel (2014) instead. Recorded as obligation O-8.

---

## D-4 — Positioning: credit `svy` as the estimator layer; claim only governance

**Date:** 2026-08-28 · **Made in:** ruling R-1 · **Ruled by:** director

The README and all public material credit `svy` as the estimator layer. prevalence-kit claims the
**governance, label-quality and audit layer only**.

**Reason.** `svy` 0.25.0 already implements SRS, proportional and Neyman allocation, Wilson,
Clopper-Pearson, Korn-Graubard and logit intervals, Taylor variance, post-stratification, raking and
calibration. Claiming to fill an estimator gap would be false, and checkable in one `pip install`.

**Alternative not taken.** The vision's framing ("the statistics are solved, the tool is not")
implied an estimator gap. Withdrawn.

---

## D-5 — Regulatory positioning inverted

**Date:** 2026-08-28 · **Made in:** ruling R-2 · **Ruled by:** director

No claim anywhere that any regulation requires prevalence. The positioning is:

> Implementing Regulation (EU) 2024/2835 mandates accuracy indicators — accuracy, precision, recall,
> and in its qualitative guidance, sensitivity and specificity. prevalence-kit shows what those
> mandated quantities do to a prevalence estimate, via Rogan–Gladen, and refuses when they make it
> undefined.

**Reason.** The word "prevalence" appears **zero times** in Regulation (EU) 2022/2065 and **zero
times** in Implementing Regulation (EU) 2024/2835, counted mechanically over the full official
texts. The vision's claim that "the timing is regulatory" was not supportable.

**Alternative not taken.** Dropping regulatory framing entirely — rejected: the sensitivity/
specificity connection is real and worth stating.

---

## D-6 — Three citation corrections

**Date:** 2026-08-28 · **Made in:** ruling R-3 · **Ruled by:** director

1. The Pinterest paper is **arXiv 2602.18518v2 (2026-08-17)**, a preprint whose header targets **the
   33rd ACM SIGKDD, August 2027**, with an unfilled ACM DOI placeholder and no `journal_ref`. Not
   "KDD '26".
2. `ml_sampler` is at **`facebookarchive/ml_sampler`**. Commits 2017-01-25 to 2020-08-06. Archived,
   **date not publicly recorded**.
3. ROOST funding — see D-7.

---

## D-7 — ROOST funding: record the source conflict, do not resolve it

**Date:** 2026-08-28 · **Made in:** ruling R-3 · **Ruled by:** director

Two official ROOST sources give different figures. **Both are recorded. Neither is preferred.**

| Source | Date | Verbatim |
|---|---|---|
| Launch press release | **10 February 2025** | *"To date, ROOST has raised more than **$27 million** for its first four years of operations from a range of leading philanthropies and top technology companies."* |
| ROOST blog, *First 100 Days: Building & Planning* | **4 June 2025** | *"Thanks to an initial **$28.5 million** in funding **and in-kind contributions** from founding partners"* |

**Primary citation** is the launch release, with its date. The blog figure is footnoted.

**Explicitly not resolved.** The two quotes differ in wording as well as figure — one says funding,
the other says funding and in-kind contributions — and the dates differ by four months. Any
reconciliation would be our inference, not either source's statement. We record what each says and
stop there.

**The vision's "$28M+" matches neither source** and is withdrawn.

---

## D-8 — Interval anchor and interval set

**Date:** 2026-08-28 · **Made in:** ruling R-4 · **Ruled by:** director

**Method anchor:** Brown, L.D., Cai, T.T., DasGupta, A. (2001), *Interval Estimation for a Binomial
Proportion*, **Statistical Science** 16(2), DOI `10.1214/ss/1009213286`.

**Intervals shipped:** **Wilson** (primary) and **Clopper-Pearson** (conservative second).

**Jeffreys is dropped.**

**Reason.** The only source the vision cited for Jeffreys — the Unofficial Google Data Science Blog
— criticises it for this exact use case, reporting that it over-covers for rare events by shrinking
toward 0.5. And that source is self-declared unofficial, which Hard Rule 3 forbids as a method
source. Clopper-Pearson is exact, never under-covers, and is implemented in **both** R `survey` and
`svy`, so D-3's double cross-check applies to it. Jeffreys is in neither, so it could have been
checked against only one witness.

**The blog is demoted to a context citation** in `docs/PRIOR-ART.md` §4 — evidence of what a Google
author reports YouTube does, never a reason a method was chosen.

---

## D-9 — Sealing cipher: **Fernet**. Cobblestone-128 considered and rejected.

**Date:** 2026-08-28 · **Made in:** ruling R-5 · **Ruled by:** director

Content sealing uses **Fernet** from `cryptography` 50.0.1 — AES-128-CBC with PKCS7 padding, HMAC-SHA256
authentication, IVs from `os.urandom()`, per the official documentation at the version-pinned URL
`https://cryptography.io/en/50.0.1/fernet/`.

**Alternative considered and rejected: Cobblestone-128.** The builder recommended it. The director
ruled against it, on these grounds, recorded as given:

1. **Soak time.** Cobblestone was added in `cryptography` **50.0.0, released 2026-07-31** — four
   weeks before this decision. A tool about auditability anchors on reviewed, aged primitives.
2. **Cross-project consistency** with finding-bridge's sealed store.
3. **The binding property is achievable via AES-GCM AAD if ever needed**, so Cobblestone's `context`
   parameter is not a unique capability we would be giving up permanently.

**The size limitation is answered by chunking**, and documented as a stated v1.0 limit in
`SECURITY.md` §3.10 rather than left implicit. Fernet's official documentation states: *"Fernet is
ideal for encrypting data that easily fits in memory."*

**Precondition discharged.** The director required independent verification that Cobblestone-128
exists as described, and that its absence would be reported as a separate defect. It exists. The
official changelog at `https://cryptography.io/en/50.0.1/changelog/`, under `50.0.0 - 2026-07-31`,
states verbatim: *"Added the Cobblestone (streaming symmetric encryption) recipe, an implementation
of the Cobblestone-128 and Cobblestone-256 instantiations of the C2SP chunked-encryption
specification for streaming authenticated encryption of large messages."* Confirmed independently at
`/en/stable/changelog/`. **No defect.**

**Alternative not taken: `AESGCM` via `hazmat`.** The library's own documentation warns: *"This is a
'Hazardous Materials' module. You should ONLY use it if you're 100% absolutely sure that you know
what you're doing."* Nonce management would be a permanent footgun.

---

## D-10 — Python: develop on 3.14, floor `>=3.12`, CI on 3.12 / 3.13 / 3.14

**Date:** 2026-08-28 · **Made in:** ruling R-6 · **Ruled by:** director

**Reason.** 3.12 is the hard floor regardless of preference — `numpy` 2.5.2 and `scipy` 1.18.1 both
require it. 3.14.7 is the current line and this machine runs 3.14.0. CI proves the floor;
development uses the current line.

**Python 3.10 reaches end of life 2026-10-31**, inside this project's lifetime. Not supported.

---

## D-11 — Coverage demo: pre-registered threshold estimand, multiple thresholds

**Date:** 2026-08-28 · **Made in:** ruling R-7 · **Ruled by:** director

The estimand fixes a threshold, **pre-registered in the plan and hashed before any data is touched**.
The true value is then knowable **by census** at each threshold. The demo runs at **multiple
pre-registered thresholds and plots a sensitivity curve**.

**Reason, as ruled:** "the float labels are an asset, use them."

**What this replaces.** The vision said *"Because every item is labeled, the TRUE prevalence is
known."* Civil Comments labels are `float32` annotator fractions. There is no binary ground truth.
See `docs/CORRECTIONS.md` C-6.

**Why this is stronger than the original plan.** A single threshold shows coverage at one operating
point. A curve shows the method holds across the prevalence range — including the rare-event end,
which is the regime the intervals were chosen for. It turns a limitation of the dataset into the
demonstration's main axis.

---

## D-12 — Name: `prevalence-kit`

**Date:** 2026-08-28 · **Made in:** Phase 0 name-collision check · **Reason: default, none recorded**

Carried from the vision. Verified free on PyPI (all three PEP 503 spellings), GitHub (direct probe
and name search) and npm. **No reason was given for choosing this name over alternatives, and none
is manufactured here.** It was available and the director had already chosen it.

---

## D-13 — Documentation URLs are version-pinned, never `/latest/` or `/stable/`

**Date:** 2026-08-28 · **Made in:** Phase 0, from evidence · **Reason: recorded below**

`docs/STANDARDS.md` cites documentation only at explicit version URLs.

**Evidence, measured 2026-08-28:**

| URL | Version served |
|---|---|
| `cryptography.io/en/latest/` | **51.0.0-dev1** — an unreleased dev build |
| `cryptography.io/en/stable/changelog/` | 50.0.1 |
| `cryptography.io/en/50.0.1/changelog/` | 50.0.1 |

`/latest/` was already wrong. `/stable/` happened to be right *today*, and will silently become
51.0.0 the day it ships — which is exactly how a moving alias lulls a reader. Only the explicit pin
is stable in the literal sense.

---

---

## D-14 — Sealed chunks carry an ordered digest manifest, bound into the ledger

**Date:** 2026-08-28 · **Made in:** Phase 1 contract approval, director's binding addition ·
**Ruled by:** director

Every seal record carries an **ordered chunk-digest manifest** and a **total chunk count**. The
manifest is bound into the ledger entry for that ingest step. `verify` checks it.

**Reason, as ruled.** SECURITY §3.7 stated a limit — Fernet authenticates per chunk, not across the
whole item — and stating a limit is not answering it. Chunk **truncation** and chunk **reordering**
become detectable defects with named reason codes rather than acknowledged weaknesses.

**Cross-reference to D-9, and it is the point of this entry.** We declined Cobblestone-128, which
implements the C2SP chunked-encryption specification and solves whole-message integrity natively.
**Having declined the spec that solves this, we carry the obligation ourselves.** D-14 is the cost
of D-9, paid rather than deferred.

**How the three failure modes are told apart.** The manifest is an ordered list of chunk digests
plus a count. On `verify`:

| Observation | Reason code |
|---|---|
| A chunk fails Fernet authentication | `SEAL_TAMPERED` |
| Chunk count is less than the manifest count | `SEAL_TRUNCATED` |
| Count matches, order differs, but the **multiset** of digests still matches the manifest | `SEAL_REORDERED` |
| Count matches and a digest is absent from the manifest multiset | `SEAL_MANIFEST_MISMATCH` |

The multiset comparison is what discriminates a reorder from a substitution. Without it, both look
like "digest at position *i* is wrong", and a single reason code covering both would be exactly the
undifferentiated refusal doctrine rule 5 forbids.

**What this does not fix.** Chunk count and chunk sizes still leak approximate plaintext length.
Sealing hides content, not size. That limit stays in SECURITY §3.7, narrowed to what is actually
true.

---

## D-15 — The plan is checked twice: sealed copy, and the working file if it still exists

**Date:** 2026-08-28 · **Made in:** answering the director's E2-complement question ·
**Reason: builder's finding, surfaced pre-build**

At genesis, `plan` does two things: it hashes the canonicalised plan, and it **seals a copy of the
plan into the store**. `verify` then performs two independent checks:

| Check | Runs when | Fails with |
|---|---|---|
| (a) The sealed plan copy's digest matches the genesis hash in the ledger | **always** | `PLAN_HASH_MISMATCH` |
| (b) The working plan file on disk re-canonicalises to the genesis hash | only if the file still exists | `PLAN_HASH_MISMATCH` |

**Why both are needed, and this is the finding.** Check (b) alone cannot survive E6 — the exit check
that deletes the original inputs and requires `verify` to reproduce from the sealed record alone. If
the plan lives only on disk, then the plan is *not* reproducible from the sealed record, and R5 is
false. Check (a) alone cannot catch a post-ingest edit to the working file, because the sealed copy
is immutable and would keep verifying while the file the operator is actually reading has changed.

**A missing working plan file is not a failure.** Check (b) is skipped and `verify` reports it
skipped, in words, in its output. Silence there would let an operator believe both checks ran.

**Alternative not taken.** Re-hashing only the on-disk plan — simpler, and it was the drafted
behaviour implied by exit check E8. Rejected: it makes R5 unprovable.

---

---

## D-16 — Sampling by keyed hash, not by a pseudo-random generator

**Date:** 2026-08-28 · **Made in:** Phase 1 build; approved at the V-1 ruling · **Ruled by:** director

`draw_srs` selects by sorting the frame on `SHA-256(seed ‖ item_id)` and taking the first *n*.
Sorting a population by a keyed hash is a uniformly random permutation, so the first *n* are a
simple random sample without replacement.

**Reason.** Two requirements, not preferences.

1. **R2 wants byte-identical output** across 3.12 / 3.13 / 3.14 and across platforms.
   `random.sample`'s internal algorithm is an implementation detail with no stability promise.
   SHA-256 has one.
2. **R5 wants an outsider to be able to recompute the sample without running this code.**
   "SHA-256 the seed and the id, sort, take *n*" is a few lines in any language. A Mersenne Twister
   draw sequence is not.

The director's assessment at the V-1 ruling: *"The keyed sort is the stronger of the two decisions;
it is what makes R5's 'an outsider can recompute this' true rather than aspirational."*

**Alternative not taken.** `random.sample` with a seeded `random.Random` — rejected on both counts
above.

**Pinned.** `test_draw_pinned_against_a_recorded_value` locks the selection rule itself, so a later
refactor that changes which items are drawn has to say why.

**Record note.** `sampling.py` cited a "D-17" for this decision before any such entry existed. The
code comment pre-empted the log by two numbers. Corrected to D-16 before this entry was written; see
`docs/CORRECTIONS.md` C-8.

---

## D-17 — A run is linear: four evidence steps, once each, in order

**Date:** 2026-08-28 · **Made in:** V-1 mechanism ruling · **Ruled by:** director

**The rule, in the words it is written in the code and the contract:**

> Linearity binds the four evidence steps — `plan`, `sample`, `ingest-labels`, `estimate` — at most
> once each, in that order. `report` may repeat, and each emission appends its own entry.

Enforced in two independent places, because they cover different cases:

| Layer | Where | Code |
|---|---|---|
| 1 | `do_plan` refuses a non-empty ledger | `RUN_ALREADY_OPEN` |
| 2 | `verify` refuses repeats **and** out-of-order steps | `RUN_NOT_LINEAR` |
| 3 | the plan is ledger entry 0; "genesis" names entry 0 | — |
| 4 | `plan.sealed` is write-once | `SEAL_ALREADY_WRITTEN` |

**What this closes.** Running the chain, disliking the number, lowering the pre-registered
threshold, and re-running everything into the same workspace took the estimate from 0.225 to 1.000
while `verify` exited 0 — and printed the *second* plan's hash under the word "genesis". A stated
protection (`SECURITY.md` §1.3, §2.2) failing, not a stated limit.

**Why layers, not alternatives.** Layer 1 alone leaves an already-corrupted record certifiable, and
`verify` must never assume the writer behaved — it is the auditor's tool. Layer 2 alone lets the bad
record be created. Layer 3 is required regardless: the false "genesis" string is its own defect and
would survive both other fixes. **Layer 4 is a prerequisite for Layer 3, not a fourth extra** —
confirmed by execution: bind entry 0 while `do_plan` can still overwrite `plan.sealed` and the
sealed-copy check fails first with a seal code, so the working-file check never runs.

**Why strict, and this fact is load-bearing for the ruling.** Every step raises its `Refusal`
*before* `ledger.append`, so **a failed step writes no entry**. Verified, and asserted in
`test_a_failed_step_writes_no_entry`. Therefore the ordinary retry-after-a-mistake workflow passes
strict linearity untouched — and a repeated step in a ledger is always a repeated *success*: a step
that completed, produced a result, and was then deliberately done again. That is not a usability
case. It is the p-hacking path.

The builder estimated the usability cost as "real"; the director measured it and it is close to
nil. Recorded because the estimate was wrong and the correction is the reason the strict option was
takeable.

**Alternatives not taken.**

- *Only `plan` is once-only, later steps may repeat with `verify` binding the last.* Rejected: it
  reopens the same hole one layer down.
- *An explicit `--amend` verb.* Rejected, and not only on the six-verb cap. In the director's words:
  *"An amend flag is a p-hacking affordance with a polite name: it moves the auditor's question from
  'did the plan change?' — which the tool can answer — to 'was the amendment legitimate?', which it
  cannot."* "A new measurement is a new workspace" leaves both runs on disk as separate records,
  which is strictly more honest and costs the operator one directory. Recorded in NEXT if anyone
  asks for it; not built.

**The `report` exemption.** Re-emitting cannot change the number — the estimate is already sealed
and chained — and a record of every emission is something an auditor wants, not something to forbid.
Ruled before `emit-report` was built, deliberately, rather than letting the builder hit it and
quietly pick one.

**Ordering is checked, not only repetition.** A ledger scrambled to
`plan → estimate → sample → ingest-labels`, with every link honestly re-chained, used to verify
clean: `by_step` was a dict and dicts do not care about order. Same root cause as V-1 — `verify`
trusting the shape of a record it should be re-deriving.

---

## D-18 — O-4 narrowed: R `survey` is the primary witness

**Date:** 2026-08-28 · **Made in:** ruling Q1 · **Ruled by:** director

**D-3's original assumption is withdrawn on evidence.** D-3 said every estimator both libraries
implement would be validated against both, to ≥ 4 significant digits. That assumed the two implement
the same estimator. For Wilson they do not.

**O-4 as narrowed:** R `survey` 4.5 is the **primary witness**. `svy` is used as a witness **only
where its estimator is the same estimator**.

**Evidence, quoted rather than recalled.** `svy` 0.25.0 sdist, PyPI sha256
`870ef8104e10c6f7e8bfd3cf1c71ccad2e07d41bb79fc8163a4b9c7f7900a93c`, uploaded
`2026-08-26T13:54:41.421035Z`. Provenance independently re-checked by the director against the PyPI
JSON API. File `src/svy/estimation/base.py`, lines 713–746:

- line 716: *"Replaces n with n_eff = p(1-p)/se² and uses t-quantile for df."*
- line 730: `n_eff = (p * (1 - p)) / (se**2)`
- line 739: `z = self._t_crit(alpha, df)` — a **t**-quantile, not *z*

**Stated at the width of the evidence, and no wider.** The source shows the two estimators **differ
in construction**. It does **not** show by how much they disagree at any given *n*. The earlier
builder claim that "the two will not agree to 4 significant digits at small n" is a claim about
magnitude that this evidence does not carry. It is very likely true and it is unmeasured.
**Obligation O-13** carries the measurement to Phase 2, which will either confirm it or narrow the
sentence again.

**A second confirmation of D-2, recorded because it previously rested on one reading.** The PyPI
registry metadata for `svy` 0.25.0 lists `httpx>=0.28.1` in `requires_dist`. D-2's zero-network
rationale is now corroborated by the registry as well as by the installed distribution.

**Our own Wilson is confirmed by two independent witnesses, neither of which is its own algebra:**
the score-equation property test, and a quadratic root-finder using the numerically-stable form
(reviewer-supplied, now adopted into the suite). Maximum absolute disagreement 6.367 × 10⁻¹³ across
63 (k, n) pairs including n = 1, 2 and k = 0, k = n.

---

## D-19 — CSV fields may hold a whole piece of content

**Date:** 2026-08-28 · **Made in:** Phase 1 build · **Reason: builder's finding, recorded below**

`_read_labels` raises the `csv` module's field-size limit to **64 MiB** for the duration of the
read, and restores it afterwards.

**Reason.** `csv` caps a single field at 128 KiB and raises a bare `_csv.Error` past it. Trust &
Safety content routinely exceeds that — a long post, a transcript, a thread — and this tool chunks
content precisely so that size is not a limit. A library default is not a reason to refuse an
operator's data, and a raw `_csv.Error` is not a refusal.

**Not unbounded.** 64 MiB rather than `sys.maxsize`, so a runaway file refuses rather than
exhausting memory.

**Restored afterwards** because `csv.field_size_limit` is process-global and this tool does not get
to leave it changed for whatever else is running in the same interpreter.

**How it was found, which is the part worth keeping.** Not by review. By changing the test fixture
to contain one deliberately multi-chunk item — a change made for an unrelated reason (F-4) — which
immediately broke fourteen tests with `_csv.Error`. The defect was in production code and had been
invisible because every fixture item was small. The director's instruction at the V-1 ruling was
*"Build the record shapes that a dishonest or broken writer would produce, and make verify meet
them."* This is the same lesson pointing at input rather than at records.

---

---

## D-20 — `equals` is exact string identity, and a numeric threshold under it is refused

**Date:** 2026-08-28 · **Made in:** V-8, ruled open by the director · **Decided by:** builder,
recorded for the director's confirmation

`positive_when: equals` compares the label to the threshold as **text**, after stripping surrounding
whitespace. It exists for categorical labels — `violating` / `not_violating`. `positive_when:
at_least` compares numerically.

**A numeric threshold under `equals` is refused at plan load** with `PLAN_THRESHOLD_INVALID`, and
the operator is directed to `at_least`.

**Reason.** The director's instruction was to decide deliberately: document exact-string semantics,
or compare numerically. Documenting is not enough, because the trap survives the documentation. With
`threshold: 1` and a label of `1.0`, the item counts as **negative**, the tool prints a wrong number,
and nothing refuses. A caveat in a schema does not protect an operator who never reads it at the
moment they need it.

Refusing removes the trap instead of describing it. A genuinely categorical threshold is not a
number, so nothing legitimate is lost; and `at_least` with threshold `1` expresses the numeric
intent exactly.

**Alternative not taken.** Comparing numerically whenever both sides parse as numbers — rejected:
the behaviour would then depend on the *data*, so the same plan could mean different things against
different label files. An estimand that changes meaning with its input is not a commitment.

**Edge case accepted.** A categorical label whose text happens to be `"1"` cannot be expressed under
`equals`. Recorded rather than hidden. Use `at_least` with threshold `1`.

---

## D-21 — A frame is de-duplicated, and both counts are recorded

**Date:** 2026-08-28 · **Made in:** V-7, ruled open by the director · **Decided by:** builder,
recorded for the director's confirmation

`do_sample` records **`frame_rows_read`** and **`frame_unique_ids`** in the ledger entry. Both
readers strip surrounding whitespace.

**Reason.** The director offered two options: refuse duplicates, or record both counts explicitly.
Recording is the right one, because **de-duplicating is correct** — a sampling frame is a set of
units, and the same unit listed twice is one unit. Refusing would reject a legitimate frame produced
by any export that repeats a row.

**Silence was the defect, not the de-duplication.** For a prevalence tool the frame is the
denominator. Reading 300 rows, sampling from 200, and recording only "200" changed the denominator
with nothing in the record saying the input differed from what was used.

**The whitespace half.** The `.txt` reader stripped and the CSV reader did not, so `" item-1"` was
two distinct population members from a CSV and one from a text file. Both strip now. Two readers of
the same frame disagreeing about how many units exist is the same class of defect as the silence.

**This is the builder's proposal implemented, and it is the director's ruling.** Marked so it is not
mistaken for a closed decision.

**Limit unchanged.** `SECURITY.md` §3.3 still holds: the tool cannot tell whether the frame is the
right frame. It can now only promise that the frame it used is the frame it recorded, and that any
difference from the input is visible.

---

---

## D-22 — One code for the threshold, four for the empty sample. The rule that separates them.

**Date:** 2026-08-28 · **Made in:** the director's close of the review stop · **Ruled by:** director
(one code accepted; the reasoning required to be recorded)

`PLAN_THRESHOLD_INVALID` covers two situations — a non-numeric threshold under `at_least`, and a
numeric one under `equals`. `EMPTY_SAMPLE` was split into four. Both happened in the same commit and
the reason was not stated, which is the defect being corrected here.

**The rule, in one line: a reason code names the artifact the operator has to go and open. Count the
artifacts, not the situations.**

Applied to the split:

| Situation | Artifact to open | Remedy |
|---|---|---|
| `sample_size` key absent | the plan's **structure** | add a key |
| `sample_size: 0` | the plan's **value** | change a number |
| frame has no rows | the **population file** | supply a different file |
| frame smaller than `n` | the **relationship** between two good files | change either |

Four different places to look, four different fixes, so four codes. An operator told
`EMPTY_SAMPLE` learned nothing about which of those four to go and read.

Applied to the threshold:

| Situation | Artifact to open | Remedy |
|---|---|---|
| non-numeric threshold under `at_least` | the estimand's **two lines** | make them agree |
| numeric threshold under `equals` | the estimand's **two lines** | make them agree |

One place, one pair of fields, one invariant: **the threshold and the comparison must agree**. Both
remedies are the same act — edit `threshold` or edit `positive_when`, in the same block of the same
file. The direction (which way they disagree) and the specific remedy are carried in the detail and
fix text, which is what that text is for. A second code would route the operator to the same two
lines twice.

**Honestly recorded: this invariant is defensible and it was not articulated at the time.** The
codes were split one way and merged the other in a single commit with no stated reason, and the
director caught the inconsistency rather than the outcome. The rule above is written now, and it is
written as a rule for future splits rather than as a justification for this one — the test of it is
whether it decides the *next* case before the code is written.

**Consequence for later phases.** Phase 2 adds stratified designs, Rogan–Gladen, and their refusals.
Each new code answers: *how many artifacts must the operator open?* If the answer is one, it is one
code with directional detail text.

---

---

## D-23 - A finding can be closed in one artifact and open in another

**Date:** 2026-08-28 - **Made in:** the director's F-4 regression finding - **Reason: recorded as a
limit of the checker, not special-cased**

`tools/check_claims.py` reconciles the findings register against the code. It cannot see this class,
and that is a property of what it checks rather than a bug in how it checks:

> **The findings check asks whether a closing test exists and passes. F-4's test does exist and does
> pass. The register is correct that F-4 is closed *in the test suite*. Nothing in that question can
> reveal that a different artifact - the shipped example - cannot reproduce the contract's own exit
> check.**

**What happened.** F-4 was "run-level E9c cannot exercise `SEAL_REORDERED` because every fixture item
is one chunk". It was fixed in `tests/conftest.py`. `examples/synthetic/` was created afterwards,
from a demo run, with no large item - so the defect came back in a new place while its closing test
went on passing. Three instruments looked at this repository and none of them looked there: the test
suite has its own fixture, the reviewer harness synthesises its own, and the checker asks about
tests.

**The decision: record it as a limit, then narrow it with a sixth check rather than a special case.**
`check_fixtures` asks a different question - *can the shipped example perform the exit checks that
name it?* - and each requirement names the check that needs it, so a failure says what the director
will not be able to do. That does not close the general class. It closes the one instance and gives
the class a name.

**The general class stays open, and is stated here so nobody reads the checker as covering it:**
a property proved in one artifact and assumed in another. The checker now covers two artifacts (the
suite and the shipped example); it does not cover documentation examples, the README, or any future
fixture. Adding artifacts to `check_fixtures` is the way to extend it.

**Alternative not taken.** Special-casing F-4 in the findings check - asserting that this particular
finding has evidence in two places. Rejected: it would fix one row and teach nothing, and the next
regression would be in a finding nobody special-cased. A check that names its question generalises;
a check that names a row does not.

**Recorded for the tier re-ask.** The instance was caught by the director running the shipped
example by hand, which is a STANDARD practice. It is not evidence for FULL.

---

## Carried obligations opened by these decisions

| # | Obligation | Owner | Opened by |
|---|---|---|---|
| O-8 | Rogan–Gladen cannot be cross-checked against either library. Validate against the published worked results in Lang & Reiczigel (2014). | Phase 2 | D-3 |
| O-9 | Implement and test Fernet chunking for content larger than memory; assert the chunk boundary behaviour. | Phase 1 | D-9 |
| O-10 | README must credit `svy` explicitly as the estimator layer. Assert by overclaim scanner. | Phase 3 | D-4 |
| O-11 | Chunk-digest manifest bound into the ledger; `verify` discriminates tamper / truncate / reorder / substitute by distinct reason code. | Phase 1 | **D-14** |
| O-12 | `verify` states in words when the on-disk plan check was skipped because the file is absent. | Phase 1 | **D-15** |
| O-13 | Measure how far `svy`'s design-based Wilson diverges from the textbook binomial interval at small *n*. D-18 records that they differ in construction; the magnitude is unmeasured. | Phase 2 | **D-18** |
| O-14 | Build the keyless structural audit mode `verify_structure`'s docstring described but `verify_run` never offered. Genuinely valuable: an auditor without the key could still check sequence integrity. | Phase 2 | **V-10** |
