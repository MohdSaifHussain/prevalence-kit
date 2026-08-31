# Decisions

Numbered, dated, with the reason, the alternatives not taken, and where the decision was actually
made. Decisions taken by default with no reason are recorded too, and marked as such.

A log that manufactures rationale after the fact is worse than no log, because it reads as evidence.

## What gets an entry — T-2, ruled 2026-08-29, applied 2026-08-30

This log had no stated admission rule, so it grew by habit. The rule is written here rather
than remembered, and it has two halves that must both survive.

**A choice the builder makes alone gets an entry when an operator could see its
consequence.** Not every implementation detail: the test is whether someone running the tool,
reading its output, or auditing its record could tell the difference. `csv.field_size_limit`
at 64 MiB (D-19) is here because an operator meets it as a refusal. The order two private
helpers are defined in is not.

**A question put to the director and ruled gets an entry because it was ruled — whatever its
operator visibility.** This half is the one that matters, and it is stated second because it
overrides the first.

> **Without that sentence, the first rule would delete Q3.**
>
> Q3 asked whether SRS should be folded into the stratified path as a one-stratum case. Same
> CLI, same reason codes, same numbers: **invisible to an operator by construction.** The
> first rule alone would suppress it — and Q3 is where the director found a third option
> nobody had proposed, and where the condition that would reverse the ruling was written
> down. *A rule written to shrink a log that deletes the log's best entry is the one thing it
> must never do.*

**Decisions taken by default, with no reason, are recorded and marked as such.** D-12 is the
example: the name was carried from the vision because it was available, and no rationale is
manufactured for it.

**Amendments to a ratified document are the director's**, never the builder's. The builder
drafts and raises; A-3, A-4 and A-5 are the record of that working.

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

**Superseded in part by D-31, 2026-08-29. The paragraph above is left exactly as it was decided** —
a dated decision is not rewritten to match what was learned later, or the log stops being evidence of
what was known when. What changed: the premise *"Rogan–Gladen can be checked against neither"* was
true of `survey` and `svy` and did not follow for the world. `epiR::epi.prev()` implements it
(**S-1.10**), and the interval anchor is **S-1.6** Reiczigel et al. (2010), not S-1.5. Read D-3's
consequence sentence as history and **D-31** as the standing rule.

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

---

## D-24 - The ledger records where the plan file was; the plan hash does not

**Date:** 2026-08-28 - **Made in:** the director's V-12 ruling - **Ruled by:** director

`plan` writes `plan_source_path` into the **plan ledger entry body**, and `verify` falls back to it
when `--plan` is not given.

**Why the body and not `Plan.as_record()`.** D-15 says where a file sits on someone's disk is not
part of the commitment, so moving a plan must not change its identity. Putting the path in the
hashed record would break that. Putting it in the entry body leaves the plan hash untouched while
still protecting the path under the chain like every other field.

**What it closes.** Labelling alone was not enough. Parts 1-3 of the builder's proposal turned a
false `[ok]` into an honest `[--]`, but an operator who forgot `--plan` still got a **green exit on
a tampered plan**, now with a better sentence explaining why nobody looked. In the director's words:
*better labelling of a hole is not a closed hole.* With the path recorded there is no longer a case
where the tool knows where the plan was and declines to look.

**The three conditions, ruled rather than preferred:**

1. A check that did not run never prints `[ok]`.
2. The summary never says "nothing out of place" when something was not performed. The count and the
   shortfall go in one sentence, so a script reading only the last line sees it.
3. The only remaining not-performed case is a file that is genuinely gone. **Any other must be
   brought back before shipping as a skip.**

**Exit code stays 0** on a genuinely absent file. That is not evidence of tampering and E8c promises
it. An auditor scripting `verify` and reading only the exit code is a real person.

**Alternative not taken.** Exit non-zero when any check is not performed - rejected: it would change
E8c's specified outcome, and absence of a working file is not a defect. *(The builder argued this
rested on E6 as well as E8c. That was wrong: E6 skips nothing, because `verify` redraws from the
recorded `frame.json` rather than the original input. The argument holds on one check, not two.
`docs/CORRECTIONS.md` C-20.)*

**Two consequences recorded rather than absorbed**, per the ruling: an absolute path now travels in
a shared run directory (`SECURITY.md` section 3.8), and a run moved to another machine reports
`NOT CHECKED` naming a path that means nothing there - which the message now says out loud.

**One condition-3 case found, and reported rather than shipped quietly.** A `Plan` built by
`Plan.from_mapping` has no `source_path`, so nothing is recorded and `verify` reports
`NOT CHECKED -- this run recorded no plan path`. **It is unreachable through the CLI**: all five
verbs call `Plan.load`, which always sets it. It requires the Python API, which Phase 1 does not
document as a supported surface. Raised for the director under condition 3 rather than absorbed as a
second skip.

---

---

## D-25 - A run with no recorded plan path is a supported case, not an edge

**Date:** 2026-08-29 - **Made in:** the director's V-14 finding - **Reason: recorded because the
reasoning decided the treatment**

`verify` reports `NOT CHECKED -- this run recorded no plan path` when the plan ledger entry has no
`plan_source_path`. Two different runs produce that, and **the ledger has no version marker, so
`verify` cannot tell them apart**:

1. **A run created before commit `25f9996`**, when the field did not exist. Every user of the tool
   before that commit has one.
2. **A run created through the Python API** by a caller who built a `Plan` with `from_mapping`
   rather than `Plan.load`.

**The message is honest for both**, which is why nothing needs to change today. It says what was not
checked and what to pass to check it, and neither reader is misled.

**Stated as a property rather than left as an accident**, per the director: the day those two cases
need different advice, nothing in the record distinguishes them. Adding a schema version to the
ledger is the fix if that day comes; it is not needed now and is not being added speculatively.
**Obligation O-15** carries it.

**Why this is a decision and not a note.** The builder called case 2 "unreachable through the CLI"
and treated case 1 as not existing. Case 1 is what every existing user meets on their next `verify`.
A branch believed unreachable gets a pin and a shrug; a branch every user hits deserves a release
note and a check that the message reads right to someone who never had the field. It does read
right -- and that was luck, not design. `docs/CORRECTIONS.md` V-14.

---

---

## D-26 - The Docker pin stands; a reversal was issued and withdrawn

**Date:** 2026-08-29 - **Made in:** the director's Phase 2 approval - **Ruled by:** director

The R witness runs in a **digest-pinned image**:
`rocker/r-ver@sha256:c3f39b365d1077fe24f8e9ab2742e352b6d3950897f51af1624a5bb5550c21c0`
(tag `4.5.3`, pushed 2026-06-24). `docs/STANDARDS.md` S-2.1a.

**Recorded because a reader of the register should not later find a ruling that contradicts it with
no trace of how it resolved.** After the pin was committed, the director was asked why not install R
locally. With the choice still open the reviewer said local was fine and simpler, and it does clear
the same bar: recorded versions, committed script, committed fixture, regenerable by a stranger.
That reversal reached the builder after the work was done, and **the director withdrew it.**

**Two reasons, in the director's order.** Reversing verified, committed work to reach an equally good
outcome is churn. And the digest pin is the more reproducible of the two: a local install means *it
worked on my machine*, which is the claim this project exists to stop making.

**Why a digest and not a tag.** `rocker/r-ver:4.5` and `:4.5.3` resolve to the same image today.
`4.5` is a moving pointer and will not tomorrow. **A truncated digest is not a pin either - it is a
prefix**, the same class as `_safe_id` in F-7, so the full 64 hex characters are in the register.

---

## D-27 - A retrieval procedure is a pinned thing, with its own re-check date

**Date:** 2026-08-29 - **Made in:** the director's C-22 ruling - **Ruled by:** director

`docs/STANDARDS.md` gains **S-8**, a section for the *calls* that fetch sources, each with its own
re-check date, alongside the sections for the sources themselves.

**Reason, as ruled:** *"A pinned URL, a digest and a version are all worthless if the call that
fetches them 400s. The register currently pins what to fetch and not how, and the how is the part
that just broke."*

**What broke.** The retrieval note written 2026-08-28 prescribed one header. It worked that day -- it
is how the "prevalence appears zero times" count was made over the full official texts. By 2026-08-29
the same call returned **HTTP 400** on `32011D0833` and on `32024R2835`, the CELEX it was written
for. It needs `Accept-Language: eng` as well. `docs/CORRECTIONS.md` C-22.

**Why this is a decision and not just a fix.** Fixing the header is one line. The decision is that
**rule 3 now covers procedures too**.

Rule 3 says a pin nobody re-checks quietly expires. We had only ever applied it to sources. So the
one entry that every other entry depends on was the one with no re-check date. The general form:
*anything the register depends on that can change under us gets a re-check date, whether or not it
looks like a source.*

**Reading did not find this. Running it did.** The note read just as correctly on 2026-08-29 as on
2026-08-28. Only the call returned 400.

**Alternative not taken.** Fix the header and move on. Rejected: that fixes one case and leaves the
class. The next expired procedure would be found the same way -- by accident, mid-task, by whoever
happened to run it instead of quoting it. D-23 again: a check that names its question generalises; a
check that names a row does not.

**Second-order consequence, recorded rather than absorbed.** `tools/check_tripwires.py` TW-3 fetches
the same endpoint **without** an `Accept` header, gets RDF, and works -- it needs existence, not
content. Stated in S-8.2 as deliberate, so a later reader does not "fix" it into the S-8.1 form and
silently change what TW-3 measures.

---

## D-28 - The documented gate and the executed gate are one list, reconciled by a check

**Date:** 2026-08-29 - **Made in:** the director's V-16 ruling - **Ruled by:** director

`CLAUDE.md`'s gate block is **machine-read**. `tools/check_claims.py`'s seventh check, `gate`, parses
it and requires `.github/workflows/gate.yml` to run every line, in both directions.

**What it closes.** `CLAUDE.md` documented seven checks. `gate.yml` ran six. The missing one was
`mypy` in its **config form**, which covers `src` *and* `tests` -- **23 files against
`--strict src`'s 12**, re-derived 2026-08-29. The eleven test files were never type-checked on the
remote, so **a type error in a test would pass CI and fail on the director's machine, and nothing
said the remote gate was the weaker one.**

**The director's framing, recorded as given:** doctrine rule 5's *a gate half-run is a gate not run*,
applied to the gate's own coverage. And the same shape as V-15 -- an instrument whose inputs quietly
drifted from what it claims to cover, with no failure and no warning, just less checked than the day
before.

**Why a check and not a habit.** Rule 14. Two lists that must agree, with nothing making them
agree, will drift apart. The only question is when. So the block in `CLAUDE.md` is now one command
per line, and the prose that used to sit inside it moved out.

**It checks both directions, on purpose.** A documented check missing from CI is the defect we hit.
A CI step running a gate tool nobody documented is the same defect from the other side -- and that
one looks like extra rigour rather than drift.

**The selftest plant is the defect itself**, not a stand-in: it rewrites `run: pytest` to
`run: pytest -q`, which is the other half of what the first CI run exposed -- `addopts` already sets
`-q`, so `-q` is `-qq` and the count is suppressed. The gate that asserts R2 could not say how many
tests it ran.

**Alternative not taken.** Have CI run a single `make gate` target so there is only one list.
Genuinely simpler, and rejected for this phase: it would rewrite the working gate at the Phase 1 to 2
boundary to remove a defect a check already catches, which is D-26's churn argument. **Recorded as
the better answer if a third list ever appears.**

---

## D-29 - The register names the route the bytes actually came from

**Date:** 2026-08-29 - **Made in:** the director's V-17 ruling - **Ruled by:** director

S-2.1 keeps **CRAN** as `survey`'s upstream and method source. **S-8.4** records the **p3m mirror**
as the route the R image installs from. Both are named, and the difference between them is measured
rather than assumed.

**The defect.** The register said CRAN. The build fetched from Posit Package Manager, because that
is the mirror `rocker/r-ver` pins. The mirror is a good choice and that was never the issue. The
issue is that **one source was named and another was used, and nobody had checked they carry the
same package.**

**Both halves were needed, and the director offered them as alternatives.** They are not
alternatives:

- **Verifying the bytes** closes the defect. It turns *should be identical* into *verified
  identical*, which is the distinction this project exists for.
- **Recording the route** stops it recurring. **D-27**, ruled the same day, says a retrieval
  procedure is a pinned thing with its own re-check date -- and this route had no entry at all.

Verifying without recording leaves the register still saying CRAN, so the next reader meets the same
confusion. Recording without verifying documents the gap honestly and never closes it.

**What the measurement found.** 339 of 341 regular files byte-identical. The two that differ are
`DESCRIPTION`, where the mirror stamps `Repository: RSPM`, and `MD5`, which follows from it. Full
evidence in `docs/STANDARDS.md` under S-2.

**Stated no wider than the evidence.** The comparison is of the two **source** tarballs. The image
installs a **binary** p3m built from its copy. We did not rebuild that binary, so what is proven is
that p3m's source is CRAN's source.

**And it is watched.** **TW-5** re-runs the comparison. A re-check date with no instrument is a
memory, which is what V-17 was.

**Recorded because it tested D-27 on the day D-27 was written.** D-27 generalised C-22 into
"retrieval procedures get their own re-check dates." V-17 was a retrieval route with no entry at
all, found within the hour. The rule earned its keep immediately.

---

## D-30 - Rounded Neyman allocation uses largest remainder, named in the plan

**Date:** 2026-08-29 - **Made in:** the director's Q4 ruling - **Ruled by:** director

A Neyman allocation rounded to whole units does not always sum to n. When it does not, the shortfall
goes to the strata with the **largest fractional parts**, and the rule is **named in the plan and
hashed before any data is touched**.

**The problem, found by D2.2 rather than reasoned about.** `rare_event_neyman_5000` asks for 5000.
Raw `3845.4104 / 884.2526 / 270.3371` floors to `3845 / 884 / 270`, which sums to **4999**. Barnett's
case happens to sum exactly, so D2.1's anchor never met it.

**The builder offered three options and all three were worse than a fourth.** The builder rejected
"hand the remainder to a stratum" on the grounds that it rewrites a pre-registered design after the
operator wrote it -- V-1's class.

**The director's answer, and it dissolves that objection:** *the objection only holds if the choice
is made ad hoc.* If the rounding rule is named in the plan, hashed before any data is touched, and
fully determined by the frame, then the allocation is **derived, not rewritten** -- exactly as the
Neyman allocation itself already is. Nobody chooses anything after seeing results.

On the failing case:

    raw        3845.4104   884.2526   270.3371
    floor      3845        884        270        = 4999, short by 1
    fraction   0.4104      0.2526     0.3371
    result     3846        884        270        = 5000

Stratum 1 takes the unit because its fractional part is largest. No judgement, no data seen, and
reimplementable by an outsider in a few lines -- the same bar D-16's keyed sort was chosen to meet.

**Why the other three lose, as ruled.**

- **Refuse** fails **R8**, and that is decisive. R8 requires every refusal to say what to do about
  it, and here the tool cannot: the operator's only lever is `sample_size`, and 5001 might not sum
  either. A refusal that hands the operator an arbitrary puzzle is worse than no refusal. *The
  director's words: this is the one place the builder's instinct for refusing should not carry.*
- **Deliver the real size** leaves the plan saying 5000 and the record saying 4999 with nothing
  reconciling them. Pre-registration means the plan is a commitment, and a commitment the tool
  routinely misses by one is not one.
- **Ad hoc assignment** is the option the builder was right to reject, and naming the rule in the
  plan is what removes it.

**Six binding conditions, as ruled.**

1. **The plan names the rule.** `allocation_rounding: largest_remainder`, an explicit field in the
   hashed plan record -- not a default and not a constant in the source. A plan that omits it is
   refused at load, in the F-1 / V-3 family.
2. **The tie-break is stated and deterministic.** Equal fractional parts resolve the same way on
   every machine and in every language, and it is pinned with a recorded-value test the way
   `draw_srs` is.
3. **Both allocations reach the ledger** -- raw and final -- so an outsider can re-derive the
   rounding without running our code. `verify` re-derives it, so a changed rule breaks the chain.
4. **Order of operations: allocate, round, then apply Q2's floor.** Largest remainder can still
   leave a stratum at 0 or 1, and `ALLOCATION_TOO_THIN` must fire after rounding, not before.
5. **The source is pinned live**, not cited from memory. S-1.7, S-1.8, S-1.9.
6. **The known property is disclosed** before anyone finds it.

**Alternative not taken, and it is a better method on the thing it optimises.** **Wright's exact
optimal allocation** (S-1.7) solves the integer allocation directly and is not merely a rounding of
Neyman. Its own abstract says *"Neyman allocation with rounded integers does not always lead to the
optimal allocation"*, with a worked counterexample. So the ruled method is **defensible and
reproducible, and it is not variance-minimal.**

Rejected for v1.0 on three grounds, recorded rather than implied: it is a different estimator
needing its own validation; **neither R `survey` nor `svy` implements it**, so R2.3 would have
nothing to check it against, which is Q1's argument exactly; and the charter's scope cap sends a
feature that wants more phases to NEXT. **Proposed for the NEXT queue by name**, so it is deferred
rather than forgotten.

**What condition 5 turned up that the ruling did not mention.** Following the pin-the-source rule
produced a second limit -- Wright's, above -- that neither director nor builder had in hand when the
ruling was written. The rule earned its keep on the first use. It also caught a DOI written from
memory that pointed at an unrelated paper on Mobius inversion.

---

## D-31 - The corrected interval is anchored on Reiczigel et al. (2010), not Lang & Reiczigel (2014)

**Date:** 2026-08-29 - **Made in:** the director's Q5 ruling - **Ruled by:** director

The Rogan-Gladen confidence interval is anchored on **S-1.6**, Reiczigel, Foldi & Ozsvari (2010).
**S-1.5**, Lang & Reiczigel (2014), is recorded as the wider method we do **not** implement.

**The charter settles it.** Section 8: *"v1.0 relies on sensitivity and specificity you provide. It
does not estimate rater quality itself."*

- **S-1.6 (2010)** assumes Se and Sp are **known**. That is our assumption.
- **S-1.5 (2014)** propagates uncertainty in **estimated** Se and Sp.

**Using the 2014 interval would model uncertainty this tool does not have** -- producing intervals
wider than our own assumptions justify, and describing a method we do not implement. The director's
words: *an overclaim wearing the costume of caution.*

**Adopting S-1.5 later is a plan-schema change, not an estimator swap.** This is the part the
builder's framing missed, and it is why the sentence is here. The operator would have to supply Se
and Sp **with their own uncertainty** -- new plan fields, new validation, and a new pre-registration
commitment, because the plan is hashed and its shape is the commitment. Nobody should later read
S-1.5 as a drop-in upgrade.

**It earns a line in the honest limits**, sharper than the one already there. The existing caveat
says intervals do not account for rater quality. The specific version: **the corrected interval
accounts for sampling uncertainty and for nothing else, including any uncertainty in the Se and Sp
you supplied.**

**O-8 restated** to name S-1.6. Its original wording -- that Rogan-Gladen has no library witness --
was also wrong in our favour: `epiR` implements it. S-1.10, with what that witness does and does not
establish.

---

## D-32 - A corrected bound outside [0, 1] is clamped, disclosed in the output, and kept raw in the ledger

**Date:** 2026-08-29 · **Made in:** the director's Q6 ruling · **Ruled by:** director

The Rogan-Gladen corrected interval is clamped to **[0, 1] at both ends**. The output **says** a bound
was clamped. The **raw** bound is recorded in the ledger beside the clamped one.

**How it was found.** Not by reasoning. By reading the D2.5 fixture before writing any interval code:
`rare_event` -- `pos = 8, n = 4000, Se = 0.90, Sp = 0.999` -- has a corrected point estimate of
`0.001112`, well inside [0, 1], so the estimator **accepts** it. Its witness interval is
`[-0.0001514559, 0.0032669342]`. `epi.prev` prints the negative bound with no warning. The refusals
built in D2.5 all key off the *point estimate*, so none of them fires here.

**Alternatives not taken, and why each loses.**

- **Refuse.** Rejected, and the reason is the tool's purpose rather than a preference. The point
  estimate is defined, the upper bound is meaningful, and this is precisely the rare-event
  measurement the tool exists to produce. In the director's words: **a tool that refuses
  `pos = 8, n = 4000` at 0.11% prevalence has refused its own use case.**
- **Print the negative bound**, as the witness does. Rejected: it is nonsense on its face, and **an
  auditor who sees a negative prevalence will stop trusting the surrounding numbers -- correctly.**
  Faithfulness to the witness is not a virtue when the witness is printing something no reader can
  use.

**Why clamping, in the two reasons that decided it.**

1. **It is what this codebase already does.** `wilson()` has computed
   `low = _fixed(max(0.0, centre - half))` since Phase 1. A negative lower bound on the *corrected*
   interval would make the tool inconsistent with itself **in the one place a reader compares two of
   its intervals side by side.**
2. **It cannot reduce coverage.** True prevalence cannot be below zero, so `[0, U]` covers everything
   `[-e, U]` covered. Clamping makes the interval very slightly **conservative**, which is the
   direction this project already chose when it picked Clopper-Pearson over Wilson as the
   conservative option.

**Three binding conditions, as ruled.**

1. **Both ends.** An upper bound above 1 is clamped for the same reason. The symmetric case will
   arrive, and building one end now and the other later is how a pair drifts apart.
2. **The output discloses it**, so a reader knows `[0, U]` is a **construction** and not a
   **measurement**. The director's words: *a silently clamped bound is a small lie in the artifact an
   outsider reads.*
3. **The ledger carries the raw bound beside the clamped one**, so `verify` re-derives both and an
   auditor can see what the arithmetic produced **before policy touched it**. Clamping is the only
   place in this tool where a printed number is not the number the estimator computed; that fact is
   therefore recorded rather than trusted to a docstring.

**Recorded under T-2 because it is operator-visible.** An operator reading `[0, 0.003267]` sees a
different artifact from one reading `[-0.000151, 0.003267]`, and the difference is a choice we made.

**The cluster this belongs to, recorded now rather than rediscovered in Phase 3.** This is the
**third** rare-event surprise of the phase: `fpr_exceeds_prevalence` (an ordinary-sounding specificity
makes the correction *undefined*, not imprecise), the inverted interval below `Se + Sp = 1`, and now a
negative lower bound in the *accept* region. **O-21 carries them to the README as one grouped fact** --
*at the prevalence rates this tool is for, several ordinary intuitions fail, and here they are* --
rather than as three scattered caveats. Ruled by the director: that framing is worth more than the
three separate sentences.

---

## D-33 - A plan that pre-registers Wilson and supplies Se/Sp is refused, not quietly switched

**Date:** 2026-08-29 · **Made in:** the director's Q7 ruling · **Ruled by:** director

`CORRECTION_INTERVAL_UNSUPPORTED`, refused **at plan load**, before any data is touched.

**The evidence that forced the question.** Across all nine positive-denominator fixture cases,
`RG(ap_lower) == tp_lower` and `RG(ap_upper) == tp_upper` to every printed digit. So
`epi.prev(..., method = "c-p")` builds the corrected interval by transforming a **Clopper-Pearson**
interval on the apparent prevalence, endpoint by endpoint. **There is no Wilson-transformed corrected
interval in the fixture, and therefore no pre-existing expected value for one** -- which R2.2 forbids
us from shipping, inside the phase whose entire shape is R2.2.

**Alternatives not taken.**

- **Ship a Wilson-transformed corrected interval too.** Rejected: it would be the one estimator in
  this phase with no witness, which is **Q1's argument exactly** and undoes section 2 in the same
  phase that makes it.
- **Clopper-Pearson only, noted in the docstring.** This was the builder's recommendation. **The
  director ruled it right in its conclusion and too weak in its remedy.** Charter section 4 makes
  Wilson **primary**. If an operator pre-registers Wilson, supplies Se/Sp, and receives a
  Clopper-Pearson-based corrected interval, **the number they get is not the one their plan committed
  to.** Silently substituting a method inside a pre-registered measurement is the class **V-1** and
  **V-7** were both about. This is **D-20's reasoning applied to an interval instead of a threshold**:
  a caveat in a docstring does not protect an operator who never reads it at the moment they need it.
  Refusing removes the trap instead of describing it.
- **Allow it with a loud note.** Rejected. A note is read once, at a moment the operator has already
  decided. The plan hash **is** the commitment, and a commitment the tool routinely substitutes a
  different method into is not a commitment.

**Why at `plan` and not at `estimate`.** **Q2's reason:** it fails before the label budget is spent,
and labels are the expensive resource in this whole tool. It is also the only place the refusal can be
honest -- after `plan`, the hash has already recorded a commitment the tool cannot honour.

**R8 at full strength in the fix text.** Not *what broke* but *which number has to change, and to
what*: pre-register `interval: clopper_pearson` if you want the correction, or remove `sensitivity`
and `specificity` and report an uncorrected prevalence. Two named remedies, both in the plan, which is
the single artifact the operator opens -- **one artifact, so one code, under D-22.**

**What this does not do.** It does not say a Wilson-based corrected interval is wrong or impossible.
It says **we have no witness for one**, and D-31's boundary applies here too: adopting one later needs
its own anchor first, not a flag.

**A region the witness cannot reach, recorded because it changes what the tests are.** Q6's clamp
applies at both ends, but **no `epiR` row exercises the upper one**: every fixture case whose upper
bound exceeds 1 also has a point estimate outside [0, 1], so it refuses before any interval is built.
The upper-clamp case is therefore constructed by us — `pos = 95, n = 100, Se = 0.96, Sp = 0.99` — and
its expected values are our arithmetic. **The witness does not clamp at all**, so every clamp test
encodes a ruling rather than a witnessed fact, and the test file says so in its header. Dressing a
policy as a witnessed fact is the exact overclaim §2 of the contract was built to prevent. **A
witness that cannot reach a region is a different kind of gap from having no witness**, and this
phase now has one of each.

---

## D-34 - The findings register is reconciled in both directions

**Date:** 2026-08-29 · **Made in:** the director's item-4 ruling at the D2.6 handoff · **Ruled by:**
director

`tools/check_claims.py` gains an eighth check, **`register`**. It scans every document for `F-n`,
`V-n` and `Q-n` and requires each identifier the record names to have a row in `docs/FINDINGS.md`.

**What was wrong.** `check_findings` validates the rows that are **present**: is each closed, does
its named test exist? **Nothing in that question can reveal a row that was never written.**

**V-12, V-13, V-14 and V-15 had no rows.** Each is discussed across three to nine documents --
V-12 in `SECURITY.md`, `docs/CORRECTIONS.md`, `docs/DECISIONS.md` and both contracts; **V-15 in
`tools/check_claims.py` itself**, which is the checker citing a finding the checker could not see.
The Phase 2 contract section 9 names V-12, V-13 and V-14 in its tier-attribution table. The register
held 22 rows and none of them these four.

And throughout, the checker printed:

> `check_claims: reconciled. 22 findings in the register, all accounted for.`

**The director's verdict, recorded as given: that statement is true and worthless.** A register
checker that validates the rows present cannot detect the rows missing. **It answers "is everything
here consistent?" when the question is "is everything here?"**

**Third instance of one shape**, and naming the shape is why this is a decision rather than a patch:

| | Instrument | What it did not look at |
|---|---|---|
| V-15 | `check_paths` | named its files, so a new document was silently uncovered |
| C-23 | `check_gate` | read YAML with a regex, so it accepted a file its real consumer rejects |
| **here** | `check_findings` | reconciled in one direction only |

> **An instrument's coverage is defined by what it looks at, and what it looks at is a choice
> someone made once.**

**Why this outranked D2.14's other gaps**, as ruled. **Rule 11** says obligations are tracked by
name until discharged, and **the register is that rule's instrument.** It had holes it could not see
for some weeks. Everything recorded into it during that time was recorded into a register with known
gaps -- so the fix comes **before** D2.6, not after, because otherwise D2.6's own findings land in
the same place.

**Both controls, and the negative one is the defect itself rather than a stand-in.** The selftest
deletes **V-12's** row and leaves all ten of its other mentions standing, which is exactly the state
this repository was in. `test_the_register_check_notices_a_finding_with_no_row` does the same in
pytest; `test_every_finding_the_record_names_has_a_register_row` is the positive control. **The
check was written before the four rows were added and fired on all four**, so it is known to catch
the real thing and not only the plant.

**One boundary, asserted rather than assumed.** The contracts number their questions `Q1` ... `Q7`,
with no hyphen; the register's findings are hyphenated. If a contract ever spelled a numbered
question the hyphenated way the two vocabularies would collide silently, so
`test_the_contracts_numbered_questions_are_not_read_as_findings` pins the separation.

**Alternative not taken: widen `check_findings` instead of adding a check.** Rejected. The two ask
different questions -- *are these rows sound?* and *are these all the rows?* -- and a single check
that answered both would report one failure for two unrelated causes, which is doctrine rule 5's
undifferentiated refusal in a checker instead of a gate.

**Alternative not taken: exempt the new tests' own fixtures.** The tests needed a broken path and a
hyphenated question identifier as fixtures, and both were caught by the existing checks reading the
test file. Adding them to `KNOWN_ABSENT` would have worked and would have **widened the exempted
surface for everyone** to accommodate one file. The fixtures are assembled from parts instead, and
each says why in a comment.

**V-15's closing test was written here, not before.** It had none: the fix was the `SCANNED` pattern
and the selftest plant. Registering it as `closed` required naming a test that fails without the fix,
so `test_the_path_check_reads_documents_outside_src_and_tests` and its negative control now exist.
**The register's own standard forced a missing test into existence**, which is the check earning its
keep on the first use.

**That is the finding inside the finding, and it is why the standard is worded the way it is.**
`docs/FINDINGS.md` does not say a closed row needs *evidence*. It says a closed row names **a test
that fails without the fix**. A looser word — "evidence", "a reference", "where it was fixed" — would
have accepted V-15's selftest plant and the row would have looked complete. The strict wording is
what turned a bookkeeping exercise into a missing test. **A checker that improves the thing it checks
rather than only reporting on it is rare**, and it happened here because the standard was written to
demand an artifact rather than a citation. Recorded so nobody relaxes that wording later to make a
row easier to add.

---

## D-35 - PLAN_MISSING splits into two codes

**Date:** 2026-08-29 · **Made in:** the director's Q8 ruling · **Ruled by:** director

`PLAN_MISSING` becomes `PLAN_FILE_MISSING` and `PLAN_SEAL_MISSING`.

**Why.** D-22 says count the artifacts an operator must open. There are two here:

| Code | Artifact | Fix |
|---|---|---|
| `PLAN_FILE_MISSING` | the plan file the operator named | correct the path, or write a plan |
| `PLAN_SEAL_MISSING` | the sealed copy inside the run | restore the run directory |

The two fix texts already differed. That was the sign the code should have split earlier.

**The operator-facing harm was real.** Under one code, someone who mistyped a path got a message
telling them to restore their run directory. That is worse than a vague refusal. It sends them to
the wrong file, confidently.

**How it was found.** D2.7 began by asking which refusals actually fire. A mutation sweep swapped
each of 31 codes at every raise site and ran the suite each time. `PLAN_MISSING` survived at both
sites: nothing could tell. Fixing the missing control meant writing a test per site, and writing
them showed the two sites were not the same thing.

**Alternative not taken: leave it as one code.** The argument was that it changes a Phase 1 code and
moves a count. The director rejected both halves. Phase 1 did not meet its criterion here, which is
what C-27 records, and finishing an unmet criterion forward is not reopening a satisfied phase.
Counts are machine-derived; C-7's lesson is not to quote a stale count, not to keep counts still.

**Phase 1's contract is not edited.** It is a dated document and still names `PLAN_MISSING`, which
is what Phase 1 shipped. The Phase 2 contract records the supersession, and `check_codes` reads it
from there. Same handling as F8.

---

## D-36 - ALLOCATION_ROUNDING_UNDECLARED is deferred, not struck

**Date:** 2026-08-29 · **Made in:** the director's Q9 ruling · **Ruled by:** director

The code stays. It is marked `PENDING-CONTROL` against D2.8 and exempt from the controls check
until then.

**The builder proposed striking it and was wrong about the precedent.**

`CORRECTION_DEGENERATE` was struck because its spec was wrong. Building it as written would have
refused the most common honest result in rare-event work. The row described behaviour we must never
have.

`ALLOCATION_ROUNDING_UNDECLARED` is the opposite case. Its spec is right. Section 6 describes what
D2.8 will build: a stratified plan with no `allocation_rounding` field is refused at load. The plan
schema cannot express that yet, so the code exists today only on a defensive branch that no valid
`Rounding` value reaches.

A wrong row and an unbuilt row are not the same thing, and only one of them should be deleted.

**Striking and re-adding it next deliverable is churn**, and it loses the contract's promise in
between. Deferring keeps the promise visible and marked unbuilt, which is the true state.

**Why a new marker rather than PENDING.** `PENDING` means the contract promises a code that
`Reason` does not have. `check_codes` fires when such a code appears, which is how that marker
expires without anyone remembering to remove it. It has fired that way twice.

This code already exists. Reusing `PENDING` would have meant relaxing a rule that has caught real
drift, to fit one row. So `PENDING-CONTROL` is a separate marker, read only by the controls check.
Raised with the director as a one-line deviation from condition 2 of the ruling, whose wording
assumed the code was absent.

**The exemption expires by machinery, not by a date.** The defensive branch becomes reachable only
if `Rounding` gains a second member. `test_the_rounding_enum_still_has_exactly_one_member` fails the
day it does, and the deferral has to be looked at again.

**The branch stays**, with a comment saying when it becomes live.

---

## D-37 - The plan names the interval method, and there is no default

**Date:** 2026-08-29 · **Made in:** the director's Q11 ruling · **Ruled by:** director

`interval: wilson` or `interval: clopper_pearson`, in the hashed plan. **No default.** Neither is
primary any more.

**What raised it.** S-1.1 was read for the first time and its published figures say Wilson's coverage
falls to 0.838 against a nominal 0.95 at rare-event rates. Our own witness measured all three
candidates and agreed. **An operator asking for a 95% interval on rare-event data was getting one
that covers about 91% of the time**, and Wilson was the default because charter section 4 made it
primary.

**Three reasons, in the director's order of weight.**

1. **Defaults are decisions made for people who do not decide.** Most operators take the default, and
   this one under-covers in the exact regime the tool exists for.
2. **It matches a pattern set twice already.** D-30 made `allocation_rounding` a required field with
   no default; D-33 made `interval_method` keyword-only with no default. **C is the consistent
   answer, not a new one.**
3. **It is the most auditable.** An outsider reading a published number sees the method in the hashed
   plan, rather than having to know what this version defaulted to.

**Three conditions, as ruled.**

1. **The refusal carries the trade-off in the operator's terms, with the coverage numbers in it** --
   the way `CORRECTION_OUT_OF_RANGE` carries the specificity inequality. Not *"choose a method"*, but
   what each one costs at rare-event rates.
2. **Charter section 4 is amended.** It says Wilson primary, and under this ruling neither is. Drafted
   as **A-4** for the director's ruling on the text; the builder does not apply it.
3. **The report states the coverage property of the interval actually used, at the operating point
   actually observed.** If a run measures 0.2% with Wilson, the report says what Wilson's coverage is
   there. **No plan field substitutes for this** -- the plan records the choice, the report records
   what the choice cost on this data.

**Alternatives not taken.**

- **Wilson stays primary**, with the table in the honest limits. Rejected: it leaves the headline
  number with a known gap between nominal and actual, disclosed in a document the operator may not
  read at the moment they need it. **D-20's reasoning** -- a caveat does not protect someone who never
  reads it.
- **Clopper-Pearson becomes primary.** Tempting, because section 4.2.1's guarantee is the only one of
  the three that survives this regime. Rejected because it is still a default, and S-1.1 itself calls
  Clopper-Pearson *"wastefully conservative"* for general use. Making it the default would trade one
  unexamined choice for another.

**Condition 3 is the part that outlives the ruling.** Whichever method an operator picks, the number
that matters is what that method's coverage is **at the prevalence this run actually found**, not in
general. That sentence is the most decision-relevant thing the report can carry, and it is owed
whatever else changes.

---

## D-38 - A one-stratum plan is accepted and disclosed, not refused

**Date:** 2026-08-30 · **Made in:** the director's Q12 ruling · **Ruled by:** director

`design: stratified` with a single stratum **loads, runs, and is recorded as what it is.** The run
records, and the report states, three things: that the design has one stratum, that stratification
therefore delivered **no precision gain**, and that the interval rests on a **stratified variance
basis** rather than a binomial inversion.

**The builder recommended refusing and the recommendation was wrong.** Its load-bearing claim was
that accepting is *"V-1, V-7 and Q7's class exactly -- the plan says one thing and the run does
another."* **It is not that class**, and the director's distinction is the reason this entry
exists:

> In **V-1** the tool re-registered a plan silently. In **V-7** it changed the denominator
> silently. In **Q7** it would have substituted an interval method silently. In all three, **the
> tool did something the plan did not say.** Here the plan says stratified and the tool runs
> stratified. **It does exactly what it was told.**

The surprise belongs to an operator who believed a one-stratum stratified design equals SRS. That
belief is wrong, and nothing in the tool encourages it. Remove the false parallel and argument 1
reduces to *an operator might be surprised* -- **which is an argument for telling them, not for
refusing.**

**The precedent that does apply is D-21**, the frame de-duplication. That ruling was: de-duplicating
is **correct**; doing it **silently** was the defect. Identical shape. Accepting a one-stratum plan
is correct -- both anchors say so -- and accepting it silently would be the defect.

**Three reasons refusal loses, in the director's order of weight.**

1. **Both anchors treat `L = 1` as admissible.** S-1.2 includes it explicitly as the special case
   where stratified sampling becomes unrestricted sampling. S-1.3 sets no lower bound, and its
   whole §5A.8 *measures from* `L = 1`: every figure in Table 5A.12 is `V(y_st)/V(y)`, normalised
   against the unstratified variance, and the table starts at `L = 2` because `L = 1` is the
   baseline with ratio 1 by construction. **Refusing would be this tool asserting a rule neither
   source supports** -- rule 9's shape, in a design decision rather than a witness claim. *The
   builder named this cost itself, and it is the decisive one.*
2. **The precedents do not reach.** `ALLOCATION_TOO_THIN` refuses a stratum with zero degrees of
   freedom -- **genuinely undefined arithmetic**. A one-stratum design is fully defined: at
   `n = 40` it has **39 degrees of freedom**. There is no refusal anywhere in this tool for
   something merely **pointless**.
3. **It would rule a permanent question on a temporary state.** The builder's strongest fact was
   that the stratified path returns no interval today. **That is a gap in the interval builder, not
   a property of `L = 1`.** Once the builder exists the question collapses to *which interval*,
   which **Q7 already answered**: the plan names it. **Do not build a permanent refusal on
   scaffolding that is scheduled to come down.**

**What the evidence did establish, and it is why disclosure is required rather than optional.** Q12
option B rested on *"a one-stratum stratified estimate **is** the SRS estimate, with weight 1."*
That is **true of the point estimate and false of the variance**. At the shipped example's own
numbers -- `n = 40`, 9 positives -- both paths give exactly `0.225`, but `stratified_estimate`
returns `s^2 = 0.178846` and **SE `0.066867` with 39 degrees of freedom**, while the SRS path
inverts a binomial to Wilson `[0.123161, 0.375031]`. Verified independently by the director.

**The 2.92 pp figure is a constructed comparison and is recorded as one.** Putting a normal
approximation on that SE gives `[0.093944, 0.356056]`, whose lower bound sits **2.92 percentage
points** below Wilson's. **No such interval is shipped**: the stratified path builds no interval at
all today, and the normal approximation was the builder's, chosen to show the bases differ. **What
is proven is that the two paths compute different quantities.** How far the *shipped* intervals
diverge is **unknown until the builder exists** -- **O-26**.

**Alternatives not taken.**

- **Refuse at `plan` (option A).** Rejected on the three grounds above. Its one real merit --
  an operator who did it by mistake is stopped before spending label budget -- is answered by
  disclosure at the moment they read the number, at no cost to an operator who meant it.
- **Accept silently (option C).** Rejected without argument in the contract and here: it is the
  silent-substitution class, and D-21 says the silence is the defect even when the act is right.

**Two obligations follow, opened separately on purpose** -- O-25's reasoning, that two obligations
living in one post-stop surface is how one of them quietly does not happen. **O-26** builds the
stratified interval, governed by Q7. **O-27** carries this disclosure.

---

## D-39 - The plan declares strata by name and rate; the frame says which unit is where

**Date:** 2026-08-30 · **Made in:** the director's Q13 ruling · **Ruled by:** director

`strata:` is a list of `{name, expected_rate}` in the hashed plan. **Membership comes from the
frame**, via a `stratum` column in a CSV. `M_h` is counted from the frame, not declared.

**Why not put the ids in the plan.** The plan is hashed **before any data file is opened** -- that
ordering is R1, and it is the property pre-registration rests on. A plan that enumerated its
population would **carry the frame**, which is a category error against R1 itself, and would make
plans the size of the data. *The director: "B is not close and your reason is the right one."*

**Why not a predicate language.** Expressions over frame columns would put a small interpreter in
the evidence path and grow the phase. **NEXT queue by name if anyone asks for it**, not v1.0.

**Two things the ruling attached, and both are about what an operator will believe.**

1. **`expected_rate` is a prior, and a wrong one costs efficiency, not validity.** It enters Neyman
   allocation and nothing else. A badly chosen rate gives a suboptimal allocation and a **perfectly
   valid number**, slightly wider than it could have been. **The opposite belief is the natural
   reading**, and it would make an operator afraid of a field that cannot hurt them. Stated in the
   schema documentation, in `PlanStratum`'s docstring, and in the limits.
2. **`M_h` is the count of *unique* ids in the stratum.** **D-21** already de-duplicates the frame
   and records both counts; stratum sizes **inherit** that rather than restating it. Said out loud
   rather than left for someone to derive.

**One thing the build found that no reading would have.** `expected_rate` is stored as a **decimal
string**, not a float -- `Estimand.threshold`'s precedent. `canonical()` refuses floats outright,
because they do not round-trip identically across platforms and this value is in the
pre-registration hash. **Found by running the draw, which refused to hash the record.**

---

## D-40 - A frame unit in an undeclared stratum is refused, not dropped

**Date:** 2026-08-30 · **Made in:** the director's Q14 ruling · **Ruled by:** director

New code **`STRATUM_UNDECLARED`**, raised at `sample`.

**S-1.13** makes strata *mutually exclusive* and covering the population, so a unit outside every
declared stratum is not a case to absorb.

**Alternatives not taken.**

- **Drop those units.** Rejected outright: it changes the **denominator** of a prevalence estimate
  with nothing in the record saying so. **V-7's class**, in the one number this tool exists to
  produce.
- **Reuse `STRATA_UNDEFINED`.** Rejected: *the plan declares none* and *the frame names one the plan
  does not* send the operator to **different artifacts**, and **D-22** says that means two codes.

**A `.txt` frame under `design: stratified` lands on the same code, and that is the ruling rather
than a shortcut.** It carries no `stratum` column, so **every** unit in it is undeclared -- the same
artifact to open, the same remedial act, with the direction carried in the detail text. *The
director: that is `PLAN_THRESHOLD_INVALID`'s precedent applied correctly on its second outing.*

**The pair is now complete.** `STRATUM_EMPTY` is a stratum the plan declares with no units in the
frame; `STRATUM_UNDECLARED` is a unit in the frame with no stratum in the plan. Between them, the
plan and the frame must describe the same population.

---

## D-41 - The odds of no interval are stated, not refused

**Date:** 2026-08-30 · **Made in:** the director's ruling on the no-interval notice · **Ruled by:** director

`sample` computes the chance that the design produces **no interval at all** -- the product over
strata of `(1 - p_h)` to the `n_h` -- prints it, and records it in the ledger. **It does not
refuse, however bad the odds are.**

**The director's grounds, and they turn on a property this project already promised.**

> `expected_rate` is documented as a prior that costs efficiency and never validity. **That
> guarantee is what made it safe to require.** If a wrong prior can block a run, the field stops
> being cost-free -- a pessimistic guess would refuse a measurement that would have worked.
> **Refusing on a prior means refusing on a guess.**

**D-39 is the entry that makes this one binding.** It attached the statement that `expected_rate`
is a prior whose only cost is efficiency, and said the opposite belief *"would make an operator
afraid of a field that cannot hurt them."* A refusal driven by that field would make the opposite
belief **true**, and would do it to an operator who had been told otherwise in the schema
documentation, the `PlanStratum` docstring and the limits.

**Why stating is sufficient rather than merely cheaper.** The number reaches the **ledger** as well
as the console, so an auditor reading the run later sees what the design's odds were rather than
taking the operator's word that they were told. Printed-only would have made it a courtesy to
whoever happened to run the command.

**Alternatives not taken.**

- **Refuse above a threshold.** Rejected on the grounds above, and on a second: any threshold would
  be this project choosing for an operator, which is what **D-37** removed from the interval
  method one ruling earlier. An operator may legitimately want the point estimate knowing the
  interval is unlikely -- at rare rates a run that finds nothing and reports a defensible upper
  bound is **the product**, which is exactly what striking `CORRECTION_DEGENERATE` established.
- **Warn only on the console.** Rejected: it leaves no artifact, and a warning nobody can audit is
  the shape `CLAUDE.md` rule 14 names -- a result with no record attached.

**The limit that travels with it.** The closed form is the probability that **every sampled unit is
negative**. A design standard error of zero also arises when every stratum is *uniformly* labelled,
including all-positive strata, so the true probability of no interval is very slightly higher than
the number printed. At the rates this tool is for the difference is far below the four decimal
places the closed form was checked to. **Stated because the printed number is a lower bound on the
risk, and a bound is read in the direction that keeps it true.**

---

## D-42 - Phase 3 tier: STANDARD, and the forward-looking question ruled with it

**Date:** 2026-08-31 · **Made in:** Phase 3 contract Q16 · **Ruled by:** director

The first tier re-ask with something irreversible to decide, and it was decided rather than
defaulted. **STANDARD**, on two grounds the ruling states explicitly.

**The backward-looking discharge standard does not govern this boundary alone.** D-1's standard
-- name a concrete finding attributable to a FULL-only practice -- cannot be met before a first
irreversible act by construction, so the director ruled the forward-looking question too rather
than letting the old standard decide by default.

**The practice matters and the label does not.** What FULL would be bought for -- rehearsal of
the irreversible, the mandatory negative control, the director's hand-verification of published
artifacts, the gated go -- is bound by the Phase 3 contract at either tier (D3.7, D3.8, R3.1,
R3.2). Moving the label would have changed the record's weight in the one phase where the
record is published regardless.

**Alternatives not taken.** FULL for the phase -- the practices it distinguishes are already
contractual. STANDARD-to-the-stop-then-FULL -- a mid-phase tier boundary bought nothing the
contract had not already bound.

---

## D-43 - Publish means GitHub release and PyPI, rehearsed on TestPyPI

**Date:** 2026-08-31 · **Made in:** Phase 3 contract Q17 · **Ruled by:** director

The release is a GitHub release **and** a PyPI publish, with the full publish path rehearsed on
TestPyPI first. The charter's audience -- an analyst, a researcher, a small platform -- adopts
by `pip install`, and TestPyPI gives the rehearsal a real target for the whole path rather than
a subset, which is what Template 6 demands. The Phase 0 name-collision check found the name
clear on PyPI; this ruling is what that insurance was for.

**Alternatives not taken.** GitHub-only with PyPI to NEXT -- leaves the audience's actual route
unserved and the rehearsal without a full-path target. PyPI as a fast follow -- two release
ceremonies for one version.

---

## D-44 - The coverage demonstration: SRS, both binomial intervals, pre-registered and bounded

**Date:** 2026-08-31 · **Made in:** Phase 3 contract Q18 · **Ruled by:** director

SRS with `wilson` and `clopper_pearson`, about four pre-registered thresholds spanning the
prevalence range including the rare end, on the order of 10,000 replications per point at the
estimator level, plus **one** pre-registered full-chain run as the governance demonstration --
the sealed chain pays Fernet sealing and real filesystem writes on every run -- the profiled
cost that dominates the local suite (2026-08-29) -- so mass replication through it would cost
orders of magnitude more than the estimator-level loop, for no additional statistical claim.

**Five binding conditions.** (1) Seeds and thresholds in a hashed pre-registration file
committed before the corpus is fetched. (2) The corpus pinned by digest and never committed.
(3) The artifact committed with its generating procedure recorded to S-8's bar. (4) The plot
states the replication count and that its error bars come from it. (5) **The reviewer's, made
binding at the ruling:** the demonstration's reading states that the corpus was already
characterised in this record -- the charter carries its row count -- before pre-registration,
and says why that does not weaken the pre-registration of thresholds and seeds.

**Alternatives not taken.** Adding stratified designs at the same scale -- their coverage is
already measured exhaustively by enumeration (charter section 8's 96-point table), and a
sampled estimate of a quantity held exactly is weaker evidence than what ships; the enumeration
figures are cross-referenced on the plot instead. Fewer replications with more thresholds -- a
denser curve with wider error on every point.

---

## D-45 - The committed local paths are disclosed, and nothing is edited

**Date:** 2026-08-31 · **Made in:** Phase 3 contract Q19 · **Ruled by:** director

O-28's recorded finding -- local Windows paths in five committed documents, two of them dated
readings -- is answered by **one disclosure note in the O-28 review reading**: the paths are
directory structure rather than identity, the documents carrying them are dated evidence, and
the tension with `SECURITY.md` section 3.8 is named rather than hidden.

**Alternatives not taken.** Editing the three editable documents forward -- history still
carries the paths, so the leak is not closed, only made inconsistent between tree and history.
Rewriting history -- ruled out structurally: the record cites commit hashes as evidence
throughout.

---

## D-46 - Release ordering: public before the tag, the ROOST PR last

**Date:** 2026-08-31 · **Made in:** Phase 3 contract Q20 · **Ruled by:** director

O-28 closes, then the repository goes public, then the rehearsal candidate, then tag and
publish, then the ROOST pull request. The release happens in public so its run links and
artifacts resolve for an outsider from the first moment; the rehearsal stays visible, which is
the honest history the method wants kept; and the PR -- the act that points strangers at the
repository -- comes only after the release it points at exists.

**Alternative not taken.** Rehearse and tag private, then go public -- the repository appears
fully formed, every CI link in the release notes was run private, and the rehearsal's honesty
becomes retroactive.

---

## D-47 - The superseded phase claim in check_figures is deleted

**Date:** 2026-08-31 · **Made in:** Phase 3 contract Q21 · **Ruled by:** director

C-47's rebuild left the old `readme phase` entry -- number-only, compared against
`current_phase`, vacuous since the close -- beside its replacement. Deleted. The canonical
two-file sentence check is the one phase claim, and its selftest proves both directions.

**Alternative not taken.** Keeping both -- the legacy pattern re-armed on the very commit that
opened Phase 3 (the sentence returned to *in progress*), leaving two checks asserting subtly
different things about one sentence: D-28's two-lists defect inside a single function.

---

## D-48 - The open-corrections row is read by machine, in both directions

**Date:** 2026-08-31 · **Made in:** Phase 3 contract Q22 · **Ruled by:** director

`CLAUDE.md`'s open-corrections row said *49 entries, 6 open* while the register held 50 and 7,
and credited `check_counts` with reading a row it had never read -- **C-48**. Ruled: a
correction entry, the row fixed, and the claim made true by machinery. `check_counts` now
compares the row's open count, its identifier list -- both directions -- and its three figures
against the register's entries, and the row's **absence is a failure**, C-47's lesson.

**Alternative not taken.** Fixing the row and striking the attribution sentence -- honest and
cheap, and it rebuilds the trap: a live figure in prose with nothing watching it is C-9's
mechanism, which is what produced the stale row in the first place.

---

## D-49 - O-14 goes to the NEXT queue; O-15 closes as unmet by design

**Date:** 2026-08-31 · **Made in:** Phase 3 contract Q23 · **Ruled by:** director

The last phase ends "carried" as an available state. **O-14** (keyless structural audit mode)
moves to the charter's NEXT queue by name at the close. **O-15** (a ledger schema version) is
recorded in the Phase 3 outcome as unmet **by design**, with D-25's condition restated as the
trigger that would create it.

**Alternatives not taken.** Building O-14 in Phase 3 -- real scope in the phase already
carrying the release, and charter section 4 sends exactly this growth to NEXT. Closing both as
won't-do -- erases reasons that are still true.

---

## D-50 - Closed contracts are read one-directionally: discharges only

**Date:** 2026-08-31 · **Made in:** Phase 3 contract Q24 · **Ruled by:** director

`check_open_items` excluded closed phases' contracts entirely, and the Phase 2 contract's
section 10 is where ten obligations are marked discharged -- so the moment the Phase 3 contract
existed, every one of those discharges left the walked set, and the selftest's planted
violation went undetected. Ruled: closed contracts contribute their **discharge claims only**.
A discharge is permanent and cannot go stale; an open-state row in a dated document was true at
the close and expires without the document changing, and flagging it would demand edits to a
dated reading.

**Caught by the selftest on the boundary commit** -- the check's coverage shrank at exactly the
boundary it exists to police, and the instrument that has only ever passed would never have
said so.

**Alternatives not taken.** Restating every discharge in a live file -- a second copy of the
record, maintained by hand. Narrowing the selftest -- green by testing less.

---

## D-51 - Test anchors are derived from the artifact, and a plant is asserted

**Date:** 2026-08-31 · **Made in:** Phase 3 contract Q25 · **Ruled by:** director

Four tests shipped inside C-47's fix anchored on the state of the moment: two asserted the live
tree's phase state as constants, two planted violations by replacing a literal sentence with
nothing asserting the replacement took -- so the boundary commit made the constants stale and
the plants **vacuous**. Ruled: all four rewritten phase-agnostic -- anchors derived from
`phase_state`, every plant asserted before the checker is consulted, the state test asserting
the close-line property on whichever contract is newest -- and **one** correction entry for the
pair, **C-49**, because the four failures have one cause. The entry notes that this happened
inside the fix for C-47, which is the part worth remembering.

**Alternative not taken.** Updating the constants to Phase 3's state -- green until the next
boundary event, then the same failure again: the count treadmill, in the suite.

---

## D-52 — The launch structure is additive; nothing in the record moves

**Date:** 2026-08-31 · **Made in:** Phase 3 contract Q26 · **Ruled by:** director

New files fill the structural gaps. **No existing tracked file is moved, renamed, or has its
prose rewritten.** The sibling project puts its charter under `docs/`; this one keeps
`PROJECT_CHARTER.md` at the root, and the difference stays.

**Reason, as ruled.** The director's instruction was *no paraphrasing, no rephrasing, no content
changes*, and the record independently forbids the move: dozens of documents cite
`PROJECT_CHARTER.md` and the record's files by path, `check_paths` validates every one of them,
and **three dated readings cite paths and can never be edited**. The cost of matching the sibling
layout is not the moves — it is that the only way to complete them is to rewrite evidence.

**Alternative not taken.** Restructure to match `finding-bridge`. Rejected on the above; the gain
is cosmetic and the loss is the citation graph.

---

## D-53 — MIT as already claimed, plus a NOTICE

**Date:** 2026-08-31 · **Made in:** Phase 3 contract Q27 · **Ruled by:** director

A `LICENSE` file carrying the MIT licence, copyright 2026 Mohd Saif Hussain — matching what
`README.md` and `pyproject.toml` have claimed all along — and a `NOTICE` carrying the EU
acknowledgement Decision 2011/833/EU requires, plus the provenance of the fixtures and the
corpus. A test pins the README, `pyproject.toml`, `CITATION.cff` and `LICENSE` to one answer.

**Reason, as ruled.** The claim already existed in two committed artifacts and nothing backed it
— **F-A**, and an overclaim in the charter's own section 5.6 sense. Choosing any other licence
would have meant changing two standing claims; choosing MIT means the file catches up with them.
`NOTICE` is the sibling project's pattern and puts O-18's binding condition where someone
redistributing this repository meets it, rather than only in the standards register.

**Alternatives not taken.** A `LICENSE` alone — leaves the EU acknowledgement discoverable only
through S-4.3. A different licence — would require rewriting claims that were never wrong about
the intent, only unsupported.

---

## D-54 — The worked example commits no content, and says so

**Date:** 2026-08-31 · **Made in:** Phase 3 contract Q28 · **Ruled by:** director

The real-data example commits the plan, the frame, the labels, the report and the `verify`
output. **The labels carry item identifiers and label values and no comment text.**

**Reason, as ruled, and it is the tool's own argument applied to itself.** This tool exists to
keep harmful content sealed; publishing the text it seals, in a repository a Trust & Safety
audience reads, would contradict the product. **Measured before it was ruled:** `content` is
optional in a labels file — `run.py` reads `r.get("content", "")` — so the whole chain runs
without it, and this is a choice rather than a limitation.

**The disclosure travels with it.** The example's reading states that content is absent by
choice and why, so a reader does not conclude the tool cannot handle it. Sealing is still
exercised: the chain seals whatever content is present, and the synthetic example carries the
deliberately multi-chunk item that the sealing checks depend on.

**Alternatives not taken.** Committing the content — exercises sealing on real text at the cost
of publishing what the tool exists to protect. Content for a handful of *benign* rows — half a
demonstration, and *benign* is a judgment nobody asked this project to make.

---

## D-55 — The worked example reuses the pinned corpus

**Date:** 2026-08-31 · **Made in:** Phase 3 contract Q29 · **Ruled by:** director

Civil Comments again — S-7.1, CC0, already fetched, digests recorded, row count verified at
1,999,514. The example is a **different run** on the same corpus: a plain measurement rather than
a coverage study.

**Reason, as ruled.** Rule 3 and S-8's retrieval bar make a second corpus real work — a fresh
licence review, a fresh register entry, a fresh recorded procedure — and the gain is variety,
which is not what a worked example is for. Reusing the pinned corpus also means a reader checks
its provenance once and it serves both artifacts.

**Alternative not taken.** A second dataset from Hugging Face or Kaggle. If breadth is wanted it
belongs in the NEXT queue, where it can carry its own prior-art and licence review; Kaggle's
terms in particular are per-dataset and frequently not open.

---

## D-56 — The container ships the tool alone

**Date:** 2026-08-31 · **Made in:** Phase 3 contract Q30 · **Ruled by:** director

One image: the CLI, its three runtime dependencies, and the shipped examples, on a
**digest-pinned** base, running as a non-root user. The R witness stays outside it.

**Reason, as ruled.** What an operator wants is to run the tool without installing Python. The
witness is a different job with a different audience — `witness.yml` already rebuilds it on
demand, and coupling a large R image to every operator who wants to measure something would make
the common case pay for the rare one. **Pinned by digest for S-2.1a's stated reason: a tag moves,
a digest does not** — the same rule the witness image already follows.

**Alternatives not taken.** One image containing both — couples the two audiences. Two images —
complete, and doubles the release surface in the phase already carrying the release.

---

## D-57 — Dependencies are hash-locked in a constraints file

**Date:** 2026-08-31 · **Made in:** Phase 3 contract Q31 · **Ruled by:** director

`constraints.txt` with `--hash` pins, installed with `--require-hashes` in CI and in the
container. This discharges the first clause of charter section 5.1, which has been unmet since
Phase 0 — **F-B**.

**Reason, as ruled.** It matches the sibling project, works with the existing pip-based CI
unchanged, and puts the hashes in a reviewable text file. The deciding factor was timing: the
supply chain has to **exist and be exercised before the rehearsal rehearses it**, and R3.1
forbids building it for the first time during the irreversible act.

**Alternative not taken, and named rather than dismissed.** A `uv` lock file is what
`sigstore-python` and `ruff` use and is probably where this ecosystem is going. It would rewrite
how every CI job installs, in the phase carrying the release. **The reason is scheduling, not
merit**, and that is worth recording so a later reader does not mistake this for a judgment about
the tool.

---

## D-58 — The version becomes 1.0.0 in the release commit

**Date:** 2026-08-31 · **Made in:** Phase 3 contract Q32 · **Ruled by:** director

`pyproject.toml` stays at `0.1.0.dev0` until the release commit, which sets `1.0.0` in the same
change that tags it. The rehearsal runs against an explicit release-candidate version. The
changelog's `Unreleased` section becomes the `1.0.0` entry at the tag, and `CITATION.cff`'s
version moves with them.

**Reason, as ruled.** The version in the tree is then true at every commit: a development version
while it is a development tree, `1.0.0` when it is released. Bumping early would make every
commit between now and the tag claim to be the released version — a live figure in prose, which
is the mechanism behind C-9 and half this register.

---

## D-59 — An environment error is not a defect in this tool

**Date:** 2026-09-01 · **Made in:** Phase 3 contract Q33 · **Ruled by:** director

`cli.py`'s guard had two outcomes: a `Refusal`, or a defect in this tool. It now has three.
An `OSError` carrying a filename — a path the operator supplied that the filesystem refused —
is reported as **`CANNOT USE`**, naming the path, the likely cause and the fix, and saying
plainly that it is the environment rather than a defect or a data problem. **The
internal-defect message is unchanged for the case it was written for.**

**Reason, as ruled.** C-52: a bind mount the container user could not write printed *"This is
a defect in prevalence-kit, not a problem with your data"*, and both halves were false. The
operator is then sent hunting a bug that does not exist — the harm TW-4's own text names.

**One widening at implementation, following the ruling over the recommendation.** The draft
listed four exception subclasses; the ruling said *OSError on an operator-named path*. The list
was wrong by construction: a directory requested under a regular file raises
`NotADirectoryError` on Linux and `FileExistsError` on Windows for the same operator mistake,
so any list is wrong on some platform. Classification is **any `OSError` with a filename**; a
table supplies a better sentence where one is known; an `OSError` with no filename falls
through to the internal-defect path, because there is nothing an operator could act on.

**Both controls, and the negative reproduces the state the incident produced** — a run
directory that cannot be created — rather than any exception that turns the check red. It skips
where the filesystem ignores the mode bits, and **a second control that fires on every
platform** was added for exactly that reason: a control that only runs elsewhere is not a
control here.

**Alternatives not taken.** A reason code and a refusal — a refusal is a pre-registered, named
condition about *evidence*, and a disk permission is not one; minting a code would blur what a
reason code means (D-22). Documentation only — an operator who hits this is reading a message,
not the SOP, and the message told them to file a bug.

---

## D-60 — Three publish channels, each with its own rehearsal target

**Date:** 2026-09-01 · **Made in:** Phase 3 contract Q34 · **Ruled by:** director

**D-43 is amended.** The channels are **a GitHub release, PyPI, and the GHCR container
registry** — three, not two. Each has a rehearsal target: **TestPyPI** for PyPI, and a
**separate registry repository** (`…/prevalence-kit-rc`) for GHCR. A manual dispatch of
`container.yml` publishes to the rehearsal path; only a tag reaches the real one.

**Reason, as ruled.** The registry entered the repository as a consequence of building the
container at D3.12, and `docs/SOP.md` already told operators to pull from it — a third
irreversible publish that no ruling named, which is the shape D-43 exists to prevent arriving
one level down. Found by the reviewer, and wired to fire on the first tag.

**Why option B and not A**, since the two differ in exactly the property the ruling's phrase is
about. The director ruled *"each with its own rehearsal target the way TestPyPI serves PyPI"*.
**TestPyPI is a separate index**, not the real index carrying a candidate label — so its
analogue is a separate registry repository, not the real repository carrying an `-rc` tag.
Mapped explicitly rather than assumed.

**The cost, stated rather than glossed.** A rehearsal on a separate path exercises the
credentials, the build, the push and the attestation, and **does not exercise the real name**.
That is the one thing it cannot prove, and it is the same thing TestPyPI cannot prove about
PyPI. Accepted on the same grounds: it is the only way to rehearse without spending the name.

**Alternatives not taken.** A candidate tag on the real path (option A) — higher fidelity, and
it publishes a permanent artifact to the name the release needs. Dropping GHCR — against the
director's stated intent, and it would make the container build-it-yourself.

---

## Carried obligations opened by these decisions

| # | Obligation | Owner | Opened by |
|---|---|---|---|
| O-8 **(restated 2026-08-29 by D-31)** | ~~Rogan–Gladen cannot be cross-checked against either library. Validate against the published worked results in Lang & Reiczigel (2014).~~ **Both halves were wrong in our favour.** The witness is `epiR::epi.prev()` (**S-1.10**); the interval anchor is **S-1.6** Reiczigel et al. (2010) — Se/Sp *known*, our assumption — **not S-1.5**, which propagates uncertainty in *estimated* Se/Sp and is the wider method we deliberately do not implement. | Phase 2 | D-3, restated by **D-31** |
| O-9 | Implement and test Fernet chunking for content larger than memory; assert the chunk boundary behaviour. | Phase 1 | D-9 |
| O-10 | README must credit `svy` explicitly as the estimator layer. Assert by overclaim scanner. | Phase 3 | D-4 |
| O-11 | Chunk-digest manifest bound into the ledger; `verify` discriminates tamper / truncate / reorder / substitute by distinct reason code. | Phase 1 | **D-14** |
| O-12 | `verify` states in words when the on-disk plan check was skipped because the file is absent. | Phase 1 | **D-15** |
| O-13 | Measure how far `svy`'s design-based Wilson diverges from the textbook binomial interval at small *n*. D-18 records that they differ in construction; the magnitude is unmeasured. | Phase 2 | **D-18** |
| O-15 | Add a schema version to the ledger, if a run made before `plan_source_path` existed ever needs different advice from an API-created run. Not added speculatively. | Phase 2+ | **D-25** |
| O-19 ▸ **discharged 2026-08-31 by D3.1** | Re-pin `actions/checkout` and `actions/setup-python`. ~~Both are two majors behind and both target Node 20.~~ **Half false when written — C-50**: checkout v5.0.0 declared node24 at its own SHA; only setup-python targeted Node 20, and GitHub had been force-running it on Node 24 since the 2025-09-19 changelog. Re-pinned to v7.0.1 / v7.0.0, both declaring node24 at the pinned SHA, runtime column derived from `action.yml` rather than written by hand | Phase 3 | **TW-4** |
| O-22 | **Q7 / D-33 at the plan file.** `interval_method` is a required keyword argument with no default today; still owed is an `interval` field in the hashed plan and `CORRECTION_INTERVAL_UNSUPPORTED` refusing at load. O-20's shape exactly. | D2.8 | **D-33** |
| O-23 | **Q6 / D-32 conditions 2 and 3 in an artifact.** `note` and the raw bounds exist on the estimate; no Phase 2 estimator is wired into `run.py`, so nothing writes them to a ledger or a report yet. | Post-stop surface | **D-32** |
| O-14 | Build the keyless structural audit mode `verify_structure`'s docstring described but `verify_run` never offered. Genuinely valuable: an auditor without the key could still check sequence integrity. | Phase 2 | **V-10** |
| **O-26** | **The stratified interval builder, and `Q7 / D-33` governs it: the plan names the method and there is no default.** `stratified_estimate` returns a `standard_error` and **no interval**, so the stratified path today produces a quantity nothing turns into a printed bound. **A hole with no name until now.** Until it exists, how far a one-stratum stratified interval diverges from Wilson is **unmeasured, not merely unmeasured-here** | Post-stop surface | **D-38** |
| **O-29** | **Rogan-Gladen is built, validated to 7.3e-13 against `epiR`, and unreachable.** There is no `sensitivity` or `specificity` field in the plan schema, and `rogan_gladen` is referenced only in `estimators.py` -- not in `run.py`, `cli.py` or `report.py`. **So a correction the charter section 4 promises** -- *"Optional Rogan-Gladen correction when sensitivity and specificity are supplied"* -- **cannot be invoked by any plan.** Not F-11's severity: nothing produces a wrong number. But **no obligation named the plan fields**: O-20 covered `allocation_rounding`, O-22 covered `interval`, and nothing covered these. Found by the director checking the open table at the review stop. **O-23's clamp disclosure is blocked behind this** -- a disclosure about a correction nobody can invoke has nothing to disclose | Whichever deliverable wires the correction | Review stop, 2026-08-30 |
| **O-28** ▸ **DISCHARGED 2026-08-31 by D3.5 — every finding ruled, closed by the director's read of `docs/contracts/PHASE-3-HISTORY-REVIEW.md`; repo-public remains a separate word, not yet given** | **Before publication, the git history is reviewed, not only the working tree.** A repository's history is what goes public with it, and this one is **not rewritten** — the record cites commit hashes as evidence throughout, so the answer is a review **before** release rather than a repair after it. **This record was written for an audience of three**, and Phase 3 is the first time anyone reads it **as a stranger would**: the register's fourth rule and `CLAUDE.md` rule 20 govern what belongs in it going forward, and this obligation is the one-time look backwards. **Must be written into the Phase 3 contract before the release, not discovered during it** | Phase 3 | **C-37** |
| **O-27** | **D-38's disclosure.** A run whose design has one stratum records, and its report states: that the design has one stratum, that stratification therefore delivered **no precision gain** (S-1.3's ratio-1 baseline is exactly this), and that the interval rests on a **stratified variance basis** rather than a binomial inversion. **Opened separately from O-26 deliberately** -- O-25's reasoning about two obligations sharing one surface | Post-stop surface | **D-38** |
