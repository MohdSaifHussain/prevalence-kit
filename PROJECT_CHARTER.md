# prevalence-kit — Project Charter

**Status: RATIFIED — 28 August 2026.**
All seven Phase 0 rulings closed by the director. Recorded verbatim in the amendment log below.
This document is binding. Deviations are recorded, never silently absorbed.

| | |
|---|---|
| **Director** | Mohd Saif Hussain |
| **Builder** | Claude (Claude Code) |
| **Method** | governed-orchestration, **STANDARD** tier, manual-approve |
| **Drafted** | 28 August 2026 |
| **Ratified** | 28 August 2026 |
| **Source** | `prevalence-kit-VISION.md`, corrected by `docs/PHASE-0-VERIFICATION.md` |
| **Decisions** | `docs/DECISIONS.md` (D-1 … D-13) |
| **Corrections** | `docs/CORRECTIONS.md` (C-1 … C-6, six draft defects, all open) |
| **Predecessors** | ts-sentry, finding-bridge, switchyard |

---

## The writing rule

Plain English. Short sentences. Common words. If a sentence needs reading twice, rewrite it.

This applies to every file in this repository: the README, the code comments, the error messages,
the report output, and this charter. It is a rule, not a preference. A tool that exists to make a
number checkable by an outsider has failed if the outsider cannot read it.

---

## 1. What this is

prevalence-kit answers one question, and it shows its work.

*How much violating content is on this platform?*

You give it a sampling plan and human labels. It gives back a prevalence estimate, an honest
confidence interval, a sealed copy of the content, a tamper-evident record of every step, and a
stamped report.

**No AI ever touches the evidence or the estimate.**

It is the measurement sibling of finding-bridge. finding-bridge turns attack output into sealed
findings. prevalence-kit turns labeled samples into sealed numbers.

## 2. Who it is for

A Trust & Safety analyst, researcher, auditor, or small platform that needs a prevalence number
they can defend — to leadership, to a regulator, or in public. Without building a Meta-sized
internal system. Without sending sensitive content to any cloud service.

## 3. Why it should exist

Every claim here is checked in `docs/PHASE-0-VERIFICATION.md` and pinned in `docs/STANDARDS.md`.
Where the vision draft was wrong, this section states the corrected version.

**The statistics are solved. The governance is not.** R `survey` 4.5 has covered survey estimation
since 2003. Python **`svy` 0.25.0 covers it too, and it is good** — stratified sampling, Neyman
allocation, Wilson and Clopper-Pearson intervals, Taylor-linearization variance, post-stratification,
raking, calibration. **`svy` is the estimator layer, and this project says so in public.** What
neither library knows anything about is Trust & Safety. Neither seals content. Neither keeps a
tamper-evident record. Neither refuses to print a number it cannot defend.

**prevalence-kit claims one thing: the governance, label-quality and audit layer.** Not the
statistics. Anyone can check that in one `pip install`, so we do not claim it. *(Ruling R-1, D-4.)*

**The closest full system is closed.** Pinterest published its production prevalence pipeline as
arXiv preprint 2602.18518 (v1 February 2026, v2 August 2026), formatted for KDD 2027. No code was
released. Its design puts an LLM inside the labeling path. The open, human-label-first, auditable
version does not exist.

**The only open ancestor is dead.** `facebookarchive/ml_sampler`: 20 commits, January 2017 to
August 2020, now archived.

**Two big platforms already do it this way, and say so.** YouTube and Meta both publish prevalence
from stratified, risk-weighted, human-labeled samples with 95% confidence intervals, and both
publish the same caveat: the intervals do not account for rater quality. This design is not novel.
It is industry practice, and there is no open tool for it.

**ROOST has nothing in measurement.** ROOST raised more than $27 million in February 2025 for its
first four years. Its tools are detection, review, and enforcement. Its `awesome-safety-tools`
directory has fourteen categories and not one of them is measurement. That is a contribution seam.

### What we do NOT claim

The vision draft said the timing was regulatory. **It is not, and the charter says so plainly.**

The word "prevalence" appears **zero times** in the Digital Services Act (Regulation (EU) 2022/2065)
and **zero times** in Implementing Regulation (EU) 2024/2835. No EU law requires a platform to
report prevalence. Anyone can check this in one search, and if we claimed otherwise they would.

There is a real connection, and it runs the other way. 2024/2835 *does* require platforms to publish
the accuracy, precision and recall of their automated moderation, and its guidance names sensitivity
and specificity explicitly. Those are exactly the inputs the Rogan–Gladen correction consumes. So:

> **Regulation obliges platforms to publish label-quality figures. prevalence-kit is the tool that
> shows what those figures do to a prevalence estimate — and refuses when they make it undefined.**

That is true, it is checkable, and it is more interesting than the claim it replaces.

## 4. Scope — capped, and the cap is named

**The cap:** finding-bridge-sized. **Four phases. One to two weeks** at demonstrated velocity.

**The rule that enforces it:** if the phase count wants to grow, the feature goes to the NEXT queue
instead. Not "we'll see". The feature moves.

This is a portfolio tool, not a platform. The cap is a deliverable of this charter, and a phase that
breaches it is a deviation to be recorded, not absorbed.

### Six verbs. Nothing more in v1.0.

| Verb | What it does |
|---|---|
| `plan` | Read a measurement plan (YAML): the estimand, the population, the sampling design, the label source. **Hash the plan before any data is touched.** This is pre-registration. The plan cannot quietly change after results are seen. |
| `sample` | Draw the sample per the plan. v1.0: simple random sampling, and stratified with proportional or Neyman allocation. Deterministic under a recorded seed. |
| `ingest-labels` | Read human labels (CSV/JSONL). Content is **sealed on ingest**: encrypted at rest, shown only as a safe preview (length, digest, harm flags). Every unseal is explicit and logged. |
| `estimate` | Compute prevalence with a correct interval — **Wilson** (primary) or **Clopper-Pearson** (conservative). Optional Rogan–Gladen correction when sensitivity and specificity are supplied. **Refuse with a named reason** rather than print a silently wrong number. |
| `verify` | Re-check the whole chain: plan hash, sample determinism, ledger integrity, estimate reproduction. An outsider must be able to verify a published number from the sealed record alone. |
| `emit-report` | Stamped Markdown and JSON: estimate, interval, design, n, every hash, and a mandatory **Honest Limits** block, asserted present by a test. |

### Not in v1.0 (write these in the README)

- Not a classifier, detector, or moderation system. It measures. It never judges content.
- Not a survey-statistics library. Where mature math exists, validate against it. Do not compete
  with it.
- No dashboards. No daemon. No cloud. A CLI that reads files and writes files.
- No importance sampling or ML-assisted weights in v1.0.
- No DSA-shaped report emitter in v1.0.

### NEXT queue — recorded now, none started without its own prior-art review

- Importance sampling / ML-assisted weights (Hansen–Hurwitz + effective-sample-size diagnostics)
- `emit-dsa` — an emitter shaped to the 2024/2835 Annex I template
- Beta-Binomial upper bounds for very low prevalence
- Label-quality gates as a fuller module (kappa / alpha)
- **Wright's exact optimal sample allocation** — authorised for this queue by the director,
  2026-08-29. Solves the integer allocation directly instead of rounding a Neyman solution, and is
  variance-minimal where our ruled largest-remainder rounding is not (`docs/STANDARDS.md` S-1.7,
  measured: 0 on every shipped fixture, worst 0.73% of variance across 37,910 random designs).
  **Deferred for the same reason as Q1: neither R `survey` nor `svy` implements it, so R2.3 would
  have nothing to check it against.** It needs a witness before it can be built. Sources: Wright
  (2014) S-1.7, Wright (2012) S-1.8.
- **Per-stratum sensitivity/specificity for Rogan–Gladen** — deferred by name, Phase 2 Q1. The
  corrected variance under stratification has **no published anchor** in `docs/STANDARDS.md`, so
  nothing could witness it. It needs its own anchor before it can be built.
- **eval-bridge** — explicitly gated. No code before a dedicated prior-art sweep of Inspect AI,
  promptfoo, LangSmith, Braintrust, W&B Weave, Arize Phoenix and OpenAI evals. That seam is crowded
  and the gap is unverified.

## 5. Hard rules — the spine

These are what make the tool worth trusting. A phase that breaks one has failed, whatever else it
shipped.

### 5.1 Security first

- **Local-first.** Zero network calls at runtime. Zero telemetry. Proven by a test that fails if any
  network capability appears.
- **Sealed by default.** Harmful content encrypted at rest. Safe preview only. Every unseal explicit
  and logged. **Cipher: Fernet** (AES-128-CBC + HMAC-SHA256), `cryptography` 50.0.1. Chunked, so the
  size limit is answered rather than inherited. *(Ruling R-5, D-9.)*
- **Supply chain to the ts-sentry bar.** Hash-locked dependencies, SHA-pinned actions, SBOM, signed
  release artifacts with provenance attestation.
- **Threat model written before Phase 1 code.** `SECURITY.md` states what the tool protects, from
  whom, and what it does not protect against. Drafted in this phase.

### 5.2 No AI in the evidence path

Labels come from humans. Estimates come from deterministic math. If AI is ever allowed to *propose*
anything, it enters as a plain input file, and a structural test proves AI output can never reach
labels or estimates. Same cage as finding-bridge.

### 5.3 Official sources only

Every statistical method, security control and format is anchored to a named primary source, pinned
by version, date or commit in `docs/STANDARDS.md`. No method enters the code from memory or from a
tutorial.

**A blog is a tutorial.** This rule already caught one thing in the vision draft: the interval
choice was anchored on the Unofficial Google Data Science Blog. That anchor is removed. The method
now rests on Brown, Cai & DasGupta (2001), *Statistical Science*, DOI `10.1214/ss/1009213286`. The
blog stays in `docs/PRIOR-ART.md` as context and never as a method source.

**Pin versions, not `latest`.** Documentation URLs must be version-locked. `/en/latest/` moves under
you — while checking this, it was serving docs for an unreleased dev build.

### 5.4 Proven approach only

Every estimator passes validation before it ships. A method that cannot be validated against an
authoritative reference does not go in.

### 5.5 Tamper-evident record

A hash-chained ledger over every step: plan, sample, ingest, estimate, report. **`verify` can say
no — so its yes means something.**

### 5.6 Honesty is enforced by machinery, not intention

Overclaim scanner. Badge-truth tests. A corrections table counting the director's errors and the
AI's separately. And rule 14 from the governed-orchestration method:

> **A lesson that lives only in prose will not hold. Build the check.**

Every ruling in this charter that can become a failing test becomes one.

## 6. How we prove the numbers are right

1. **Cross-check fixtures against two independent witnesses.** Every estimator is compared against
   **R `survey` 4.5** *and* **Python `svy` 0.25.0**, committed as fixtures with each library's
   version and the exact call recorded. Agreement to ≥ 4 significant digits or the build is red.
   Agreeing with two independent implementations is stronger than agreeing with one. The `svy`
   comparison runs in a separate optional test environment so the runtime dependency tree stays
   network-free. *(Ruling R-1, D-3.)*

   **Rogan–Gladen has no witness** — neither library implements a misclassification correction. It is
   validated against the published worked results in Lang & Reiczigel (2014) instead. Obligation O-8.
2. **Reuse the strongest existing proof.** Port the ts-sentry stratified/Neyman code. Its validation
   target is Arnold Barnett's *YouTube's Violative View Rate Methodology: A Statistical Assessment*
   (MIT, September 2021), Table 2B. **This was re-derived independently during Phase 0 and matches
   on all five strata, the total, and the standard deviation** — see
   `docs/PHASE-0-VERIFICATION.md` §C6. The specification is Neyman allocation with
   `S_h = √(p_h(1−p_h))` and with-replacement stratified variance, no finite-population correction.
3. **The coverage demonstration — the flagship.** Use the Civil Comments corpus (CC0 1.0,
   1,999,514 rows). Its labels are continuous annotator fractions, not binary truth. So the estimand
   **fixes a threshold, pre-registered in the plan and hashed before any data is touched** — and the
   true value is then knowable **by census** at that threshold. Draw many samples. Estimate each
   time. Show the 95% intervals cover the truth about 95% of the time.

   **Run it at multiple pre-registered thresholds and plot the sensitivity curve.** The float labels
   are an asset, not a caveat: a single threshold shows coverage at one operating point, a curve
   shows the method holds across the prevalence range — including the rare-event end, which is the
   regime the intervals were chosen for.

   Meta, Google and Pinterest cannot publish this demonstration, because their truths are
   confidential. This one is reproducible by anyone. It goes on the README front page.
   *(Ruling R-7, D-11.)*
4. **Refusal tests.** Every named refusal — undefined correction, unsampled stratum, broken chain,
   plan-hash mismatch — has a test proving it fires, and a distinct reason code. Every gate also
   gets a positive control, because a gate that refuses everything proves nothing.

## 7. Phases

| Phase | Name | What it delivers | What the director reads at close |
|---|---|---|---|
| **0** | Ratification, no code | This charter, verification report, TRIPWIRES, PRIOR-ART, STANDARDS skeleton, SECURITY threat model, rulings queue | The rulings queue, and this charter |
| **1** | Proof slice | `plan` → `sample` (SRS) → `ingest-labels` (sealed) → `estimate` (Wilson) → `verify` → `emit-report`, end to end on synthetic data | A report he runs himself, and a `verify` that he breaks on purpose and watches fail |
| **2** | Honest statistics | Stratified + Neyman (ported, validated), **Clopper-Pearson**, Rogan–Gladen with refusals, **R `survey` and `svy` fixtures** in CI | The Barnett Table 2B reproduction, and every refusal firing |
| **3** | Flagship demo + launch | Coverage demonstration, README, docs, release to the ts-sentry supply-chain bar, PR to ROOST `awesome-safety-tools`, post-release closure | The coverage plot, and the published artifacts verified by hand |

**Tier re-ask is binding.** At every phase boundary the tier is re-asked as a named deliverable.
Default: stay at STANDARD. Moving up to FULL requires the director to name, in a numbered ruling, a
concrete finding that only FULL-tier ceremony would have produced.

## 8. Honest limits — stated up front, carried forward unchanged

- It measures prevalence of labeled samples from a defined population. It **cannot fix a bad
  sampling frame, biased labels, or a dishonest plan.** It can only make them visible and permanent
  in the record.
- v1.0 relies on sensitivity and specificity you provide. It does not estimate rater quality itself.
- **The corrected interval treats the Se and Sp you supply as exact.** It accounts for sampling
  uncertainty and for nothing else -- including any uncertainty in those two numbers. This is the
  specific version of the caveat above, added 2026-08-29 under ruling Q5 / D-31. The method that
  does propagate that uncertainty is Lang & Reiczigel (2014), S-1.5, and adopting it is a plan
  schema change rather than an estimator swap.
- **At rare-event prevalence, an ordinary-sounding specificity makes the correction undefined, not
  merely imprecise.** The correction is defined only when specificity is at least `1 - apparent
  prevalence`. At an apparent prevalence of 0.2% that means **above 99.8%**. A team reading "99%
  specificity" hears excellent; at that rate the test alone produces five times more apparent
  positives from clean content than the whole sample contained, and the corrected estimate goes
  negative. The tool refuses and names the figure you need. Added 2026-08-29, from the
  `fpr_exceeds_prevalence` case.
- **Interval guarantees are sampling-only.** They do not account for rater quality. This matches the
  caveat YouTube publishes for VVR: *"The confidence intervals do not take into account rater
  quality, which may impact our measurements."*
- Validation is on synthetic data and one public dataset. **No claim of production deployment.**
- No EU regulation requires the number this tool produces. See §3.
- Built by directing an AI under the governed process. The director wrote none of the code and all
  of the decisions. Stated in the README and measured in the provenance section.

Limits carry forward unchanged across phases. A limit is narrowed only when it genuinely narrowed,
and the change is stated. **A limit is never deleted for being inconvenient.**

## 9. Exit checklist for Phase 0

Phase 0 closes when all of these are true. Not before.

- [ ] Every factual claim in the vision is marked VERIFIED, DEFECT or UNVERIFIED with a named source
      — **done**, `docs/PHASE-0-VERIFICATION.md`, 24 claims
- [ ] This charter drafted from the corrected vision — **done**
- [ ] `docs/TRIPWIRES.md` drafted with monitoring, cadence, pivot and what is preserved — **done**
- [ ] `docs/PRIOR-ART.md` drafted — **done**
- [ ] `docs/STANDARDS.md` skeleton drafted with every source pinned — **done**
- [ ] `SECURITY.md` threat model drafted — **done**
- [ ] Name-collision check run, not assumed — **done**, clear on PyPI, GitHub, npm
- [x] All seven rulings closed by the director — **done**, 2026-08-28
- [x] Director ratifies this charter in writing — **done**, 2026-08-28
- [x] Amendment log below records every ruling verbatim — **done**
- [x] `docs/DECISIONS.md` opened (D-1 … D-13) — **done**
- [x] `docs/CORRECTIONS.md` opened with all six draft defects and their sources — **done**

**Phase 0 is closed.** Next: `git init`, then the Phase 1 contract.

---

## Amendment log

The director's rulings are recorded **verbatim** in `docs/RATIFICATION.md`, not paraphrased. That
file is the primary record. This table indexes it.

Every change to this charter after ratification gets a row here.

| # | Date | Change | Ruled by | Verbatim ruling |
|---|---|---|---|---|
| A-2 | 2026-08-29 | **Honest limits gain a second line**: at rare-event prevalence an ordinary-sounding specificity makes the Rogan-Gladen correction undefined rather than imprecise. From the `fpr_exceeds_prevalence` case, found by the D2.5 fixture contradicting its own author's note. | Director | D2.5 review, this session |
| A-1 | 2026-08-29 | **Honest limits gain one line** under ruling Q5 / D-31: the corrected interval treats supplied Se and Sp as exact. A limit added, never narrowed -- section 8's rule is intact. Wright's exact optimal allocation added to the NEXT queue the same day. | Director | Q5 ruling, this session |
| A-0 | 2026-08-28 | **Charter ratified.** Seven Phase 0 rulings applied: R-1 (lean estimators, httpx rationale, dual cross-check, svy credited), R-2 (regulatory positioning inverted), R-3 (three citation fixes, ROOST conflict recorded unresolved), R-4 (Brown/Cai/DasGupta anchor; Wilson + Clopper-Pearson; Jeffreys dropped), R-5 (Fernet; Cobblestone rejected on soak time), R-6 (dev 3.14, floor 3.12), R-7 (pre-registered threshold estimand, multi-threshold sensitivity curve) | Director | `docs/RATIFICATION.md` — full text of all seven |

### Standing directions in force

Given during Phase 0. Binding on all later phases. Full text in `docs/RATIFICATION.md`.

| Date | Direction (as given) |
|---|---|
| 2026-08-28 | "EVERYTHING should be 2026 updated aligned to the latest. be it coding, be it any framework bieng applied or applicable" |
| 2026-08-28 | "make sure you have a document where time/date is being recorded for this whole project ... please track it in a .txt" — implemented as `TIME-LOG.txt` |
| 2026-08-28 | "please be careful while dwnloading from unbofficial sources" |
| 2026-08-28 | `C:\Users\mohds\ts-sentry` is **read-only**. Reference only. No write actions. |
