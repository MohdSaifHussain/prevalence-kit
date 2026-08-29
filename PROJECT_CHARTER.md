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
| `estimate` ▸ **A-4** | Compute prevalence with a correct interval. **The plan names the method and there is no default** — `interval: wilson` or `interval: clopper_pearson`. **Neither is primary.** The choice is between coverage you can rely on and an interval that is narrower. Clopper-Pearson holds its nominal level; Wilson is tighter and can fall below it. You cannot have both, and the tool will not pick for you. Optional Rogan–Gladen correction when sensitivity and specificity are supplied. **Refuse with a named reason** rather than print a silently wrong number. |
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

   **Rogan–Gladen has a witness. It is a weaker kind than Barnett.** ▸ **AMENDED, A-3**

   Neither R `survey` nor Python `svy` implements a misclassification correction. That part was
   right, and it stays.

   It did not follow that nobody does. `epiR` implements it. We run **version 2.0.92**, inside the
   digest-pinned witness image. **S-1.10.**

   The interval anchor is **Reiczigel, Földi & Ózsvári (2010)**, **S-1.6**. That paper assumes
   sensitivity and specificity are known. That is what v1.0 does. The earlier text here named Lang &
   Reiczigel (2014), **S-1.5**. That paper assumes both are *estimated* and carry their own
   uncertainty. We do not model that. Adopting it later would change the plan schema, not just the
   estimator. *(D-31.)*

   **One narrowing, and it is not optional.** Jenő Reiczigel is a listed contributor to `epiR`. So
   this is the method author's own code for the method author's own paper. It shows we implement the
   method the way its author does. **It does not independently confirm the method.**

   That is weaker than Barnett Table 2B, and weaker in a specific way. Barnett is a published table.
   Nobody computed it from an implementation. Reproducing it tests our arithmetic against a number no
   one in this chain produced. **Read the two kinds of evidence differently.**

   Obligation O-8, **discharged 2026-08-29 by D2.6** — the interval reproduces every accepted `epiR`
   case to 7.3e-13.
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
- **The interval you choose has a coverage cost, and at rare-event rates it is large.** Ask for a
  95% Wilson interval and you can get one that covers **as little as 90.98%** of the time, when the
  true rate is a few times 1/n. That is the regime this tool is built for. Clopper-Pearson holds at or
  above its nominal level there, and is wider for it. Measured, not asserted:
  `r/fixtures/coverage.json`, checked against the published limits in S-1.1 — which the same
  instrument reproduces before it reports anything else. **Read the figure the safe way round.** Every number in that table is
  the worst found on a *grid* of points, so the real worst is **at most** that and may be lower.
  That is also why it says 90.98% and not 91%: rounding to nearest would have claimed coverage
  never drops below 91%, when the measurement already shows it does. **Round a bound in the
  direction that keeps it true.** **This is why the plan must name the method.** A default would be this
  project choosing, for an operator who did not know there was a choice. Added 2026-08-29, A-4.
- **What we ship is limited by what we can witness.** Section 6 says every estimator is validated
  against an authoritative reference before it ships. That rule has a price, and this is it. S-1.1 —
  our own anchor — recommends the Jeffreys interval for small samples and Agresti–Coull for larger
  ones. **We ship neither.** Neither is in R `survey` or Python `svy`, so R2.3 would have nothing to
  check them against. **The methods here are the ones we can prove, not the ones the anchor
  prefers.** That is a deliberate trade. It is written here so nobody reads Wilson and
  Clopper-Pearson as a claim about which intervals are best. Added 2026-08-29, A-4.
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
| A-4 | 2026-08-29 | **§4's `estimate` row and two honest limits.** Under **Q11 / D-37** the plan names the interval method and there is no default, so **neither interval is primary** and §4 said one was. Two limits added: what the choice costs in coverage at rare-event rates, and — the one that was invisible — **what we ship is limited by what we can witness**, since our own anchor recommends two intervals we cannot validate and therefore do not ship. Ruled after the builder raised it as a question about §6 reading as pure strength | Director | **Verbatim below** |
| A-3 | 2026-08-29 | **§6.1's Rogan–Gladen sentence amended.** Two claims in it were false and one was true. **True and kept:** neither `survey` nor `svy` implements a misclassification correction. **False:** that it followed there is no witness — `epiR` 2.0.92 implements it, S-1.10. **False:** that the anchor is Lang & Reiczigel (2014) — D-31 ruled S-1.6 Reiczigel et al. (2010). The narrowing travels with the amendment and is not optional. Found by a fresh session reading the record before building; the builder raised it and did **not** edit the ratified document. §6.1's numbered points are untouched | Director | **Verbatim below** |
| A-2 | 2026-08-29 | **Honest limits gain a second line**: at rare-event prevalence an ordinary-sounding specificity makes the Rogan-Gladen correction undefined rather than imprecise. From the `fpr_exceeds_prevalence` case, found by the D2.5 fixture contradicting its own author's note. | Director | D2.5 review, this session |
| A-1 | 2026-08-29 | **Honest limits gain one line** under ruling Q5 / D-31: the corrected interval treats supplied Se and Sp as exact. A limit added, never narrowed -- section 8's rule is intact. Wright's exact optimal allocation added to the NEXT queue the same day. | Director | Q5 ruling, this session |
| A-0 | 2026-08-28 | **Charter ratified.** Seven Phase 0 rulings applied: R-1 (lean estimators, httpx rationale, dual cross-check, svy credited), R-2 (regulatory positioning inverted), R-3 (three citation fixes, ROOST conflict recorded unresolved), R-4 (Brown/Cai/DasGupta anchor; Wilson + Clopper-Pearson; Jeffreys dropped), R-5 (Fernet; Cobblestone rejected on soak time), R-6 (dev 3.14, floor 3.12), R-7 (pre-registered threshold estimand, multi-threshold sensitivity curve) | Director | `docs/RATIFICATION.md` — full text of all seven |

### A-3, ruled 2026-08-29 — the director's words, verbatim

Recorded in full because §6.1 is where a reader decides how much the whole validation section is
worth, and a paraphrase of a ruling about evidence would be the wrong thing to keep.

> **A-3, ruled 2026-08-29.** Charter §6.1's Rogan–Gladen sentence is amended. Two of its claims are
> false and one is true and must survive the edit.
>
> **Still true:** neither R `survey` nor Python `svy` implements a misclassification correction. D-3
> was right about the two libraries it named.
>
> **False:** that it followed from this that Rogan–Gladen has no witness. `epiR` 2.0.92 implements
> it, and is pinned by digest as S-1.10. **The inference was wrong, not the observation.**
>
> **False:** that the anchor is Lang & Reiczigel (2014). D-31 ruled the anchor is Reiczigel, Földi &
> Ózsvári (2010) — the paper whose assumption, Se and Sp known, matches what v1.0 does. Lang &
> Reiczigel (2014) assumes Se and Sp are estimated with their own uncertainty, which this version
> does not model, and adopting it later is a plan-schema change rather than an estimator swap.
>
> The narrowing travels with the amendment and is not optional: `epiR` is the method author's own
> implementation — Reiczigel is a listed contributor. It confirms we implement the method as its
> author does. It does not independently confirm the method. That is a different kind of evidence
> from Barnett Table 2B, which is a published table computed without reference to any
> implementation, and §6.1 is where a reader decides how much the whole validation section is worth.

**Two instructions came with the ruling and are recorded because they shaped the edit.** Write it to
the charter's own writing rule — plain English, short sentences. And **do not edit the surrounding
numbered points**: §6.1 item 1's `survey` / `svy` cross-check language is unaffected, and reopening
it invites drift.

**How this reached a ruling at all.** A fresh session read the record against the rulings it encodes
before writing any code, and found seven places where O-8's restatement had not landed. Five were the
builder's to fix. **Two were in this ratified document, and the builder raised them rather than
editing them** — amendments are the director's. The builder's first report undercounted the drift as
"one place of four"; it was one place of seven, and the correction is what made this ruling cover the
charter at all.


### A-4, ruled 2026-08-29 — the director's words, verbatim

Recorded in full because the second limit was the director's ruling rather than the builder's draft,
and because it is the limit a reader is least likely to arrive at unaided.

> **Point 3 — yes. Say it out loud, and put it in §8.**
>
> This is the more important of the three, and it is currently invisible. §6 says every estimator is
> validated against an authoritative reference before it ships, and that reads as pure strength. The
> cost is not stated anywhere: the witness libraries constrain what we are able to ship, and that is
> not the same as choosing the best method.
>
> A reader today would reasonably conclude we ship Wilson and Clopper-Pearson because those are the
> best available. The truth is that we ship them because two libraries implement them. Our own anchor
> recommends Jeffreys for n ≤ 40 and Agresti-Coull above, and we ship neither.

**Two corrections to the builder's draft came with the ruling.**

*"the right one depends on what you are measuring and only you know that"* — struck. The director:
*"the second half overstates the operator's knowledge and understates what the tool can tell them.
They often do not know until they have measured."* The row now names the actual trade: coverage you
can rely on, or a narrower interval, and not both.

*"covers about 91% of the time"* — became **"as little as 91%."** The builder had established one
message earlier that a finer grid can only find a lower minimum, so every figure in that table is an
upper bound on the worst case, and then wrote the bullet as a point fact anyway. The director:
*"'about 91%' reads as a point fact about typical behaviour. 'As little as' is both what the
measurement supports and the framing an operator needs."*


### Standing directions in force

Given during Phase 0. Binding on all later phases. Full text in `docs/RATIFICATION.md`.

| Date | Direction (as given) |
|---|---|
| 2026-08-28 | "EVERYTHING should be 2026 updated aligned to the latest. be it coding, be it any framework bieng applied or applicable" |
| 2026-08-28 | "make sure you have a document where time/date is being recorded for this whole project ... please track it in a .txt" — implemented as `TIME-LOG.txt` |
| 2026-08-28 | "please be careful while dwnloading from unbofficial sources" |
| 2026-08-28 | `C:\Users\mohds\ts-sentry` is **read-only**. Reference only. No write actions. |
