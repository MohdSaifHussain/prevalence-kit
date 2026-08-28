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

## Carried obligations opened by these decisions

| # | Obligation | Owner | Opened by |
|---|---|---|---|
| O-8 | Rogan–Gladen cannot be cross-checked against either library. Validate against the published worked results in Lang & Reiczigel (2014). | Phase 2 | D-3 |
| O-9 | Implement and test Fernet chunking for content larger than memory; assert the chunk boundary behaviour. | Phase 1 | D-9 |
| O-10 | README must credit `svy` explicitly as the estimator layer. Assert by overclaim scanner. | Phase 3 | D-4 |
| O-11 | Chunk-digest manifest bound into the ledger; `verify` discriminates tamper / truncate / reorder / substitute by distinct reason code. | Phase 1 | **D-14** |
| O-12 | `verify` states in words when the on-disk plan check was skipped because the file is absent. | Phase 1 | **D-15** |
