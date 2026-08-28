# prevalence-kit — What I Want to Build

**Status:** Vision draft. Not ratified. This document goes into Phase 0, where every claim
in it gets checked against primary sources before any code is written.
**Author:** Mohd Saif Hussain (director). Drafted with Claude (chat), 28 Aug 2026.
**Writing rule for this project:** plain English. Short sentences. Common words. If a
sentence needs reading twice, rewrite it.

---

## 1. The one-paragraph pitch

Trust & Safety teams must answer one hard question in public: *"How much violating
content is on our platform?"* The big platforms (Meta, YouTube, Pinterest) each built
private systems to answer it. The math is published in papers and blog posts. The tools
are not. The one open-source tool that existed (Meta's ml_sampler) was archived in 2021.
prevalence-kit is the missing open tool: give it a sampling plan and human labels, and it
gives back a defensible prevalence estimate with an honest confidence interval, a sealed
record of the harmful content, a tamper-evident audit trail, and a stamped report.
**No AI ever touches the evidence or the estimate.**

Think of it as the measurement sibling of finding-bridge: finding-bridge turns attack
output into sealed findings; prevalence-kit turns labeled samples into sealed numbers.

## 2. Why this is worth building (verified, not assumed)

An exhaustive prior-art review was completed on 28 Aug 2026 before this document was
written. Full register: `docs/PRIOR-ART.md` (to be committed in Phase 0 from the review).
The short version:

- **The statistics are solved. The tool is not.** R `survey` (maintained since 2003) and
  `svy` (MIT, active) cover survey estimation in general. Neither knows anything about
  T&S: no content handling, no label-quality gates, no audit trail, no report output.
- **The closest system is closed.** Pinterest published its full production prevalence
  pipeline in Feb 2026 (arXiv 2602.18518, KDD '26) — and released **no code**. It also
  puts an LLM inside the labeling path. The open, human-label-first, auditable version
  does not exist.
- **The only open ancestor is dead.** Meta's ml_sampler: commit history 2017–2020,
  archived 2021.
- **The timing is regulatory, and it is now.** EU DSA Implementing Regulation 2024/2835
  requires harmonized transparency reports with accuracy indicators; the first
  harmonized reports are due in early 2026. There is **no official tooling** to compute
  those numbers.
- **ROOST** (the major open-source T&S initiative, $28M+ funding) ships detection and
  enforcement tools. It has **nothing in measurement**. That is a contribution seam.

## 3. Who it is for

A T&S analyst, researcher, auditor, or small platform that needs to produce a
prevalence number they can defend — to leadership, to a regulator, or in public —
without building a Meta-sized internal system, and without sending sensitive content
to any cloud service.

## 4. What it does (v1.0 scope — CAPPED)

Six verbs. Nothing more in v1.0.

1. **`plan`** — Read a measurement plan (YAML). The plan states the estimand (what
   exactly is being measured), the population, the sampling design, and the label
   source. The plan file is hashed **before any data is touched**. This is
   pre-registration: the plan cannot quietly change after results are seen.
2. **`sample`** — Draw the sample per the plan. v1.0 designs: simple random sampling
   (SRS) and stratified sampling with proportional or Neyman (optimal) allocation.
   Deterministic under a recorded seed.
3. **`ingest-labels`** — Read human labels (CSV/JSONL). Content items are **sealed on
   ingest**: encrypted at rest, shown only as a safe metadata preview (length, digest,
   harm flags). Reused pattern from finding-bridge. Every unseal is explicit and logged.
4. **`estimate`** — Compute prevalence with a correct confidence interval.
   Rare-event-safe intervals only (Wilson / Jeffreys — never plain Wald for rare
   events; this matches Google's published practice). Optional Rogan–Gladen correction
   when label sensitivity/specificity are provided, with CI propagation per
   Lang & Reiczigel (2014). When the correction is mathematically undefined
   (Se + Sp ≤ 1) or degenerate (zero apparent prevalence), the tool **refuses with a
   named reason instead of printing a silently wrong number**. The refusal is a feature.
5. **`verify`** — Re-check the whole chain: plan hash, sample determinism, ledger
   integrity, estimate reproduction. An outside person must be able to verify a
   published number from the sealed record alone.
6. **`emit-report`** — Stamped Markdown (and JSON) report: estimate, interval, design,
   n, all hashes, and a mandatory **Honest Limits** block (asserted present by test).
   A DSA-shaped emitter is a NEXT-queue item, not v1.0.

### Explicit non-goals (write these in the README)
- Not a classifier, detector, or moderation system. It measures; it never judges content.
- Not a survey-statistics library. Where mature math exists, validate against it,
  don't compete with it.
- No dashboards, no daemon, no cloud. A CLI that reads files and writes files.
- No importance sampling / ML-assisted sampling in v1.0 (NEXT queue, behind the
  estimator interface).

## 5. Hard rules (the spine — these are what make it mine)

1. **Security first.**
   - Local-first. Zero network calls at runtime. Zero telemetry. Proven by a test that
     fails if any network capability appears (same class as finding-bridge's
     environment scrub).
   - Harmful content sealed by default: encrypted at rest (Fernet or better — Phase 0
     ruling against current official cryptography guidance), safe preview only,
     explicit logged unseal.
   - Supply chain to the ts-sentry bar: hash-locked dependencies, SHA-pinned actions,
     SBOM, signed release artifacts with provenance attestation.
   - Threat model written down in `SECURITY.md` before Phase 1 code: what the tool
     protects (content, labels, the integrity of the number), from whom, and what it
     does not protect against (stated honestly).
2. **No AI in the evidence path.** Labels come from humans. Estimates come from
   deterministic math. If AI is ever allowed to *propose* anything (e.g., sampling
   weights, later), it enters as a plain input file, and a structural test proves AI
   output can never reach labels or estimates. Same cage as finding-bridge.
3. **Official sources only.** Every statistical method, security control, and format
   is anchored to a named primary source, pinned by version/date/commit in
   `docs/STANDARDS.md` (the finding-bridge pattern, including flip-day re-checks).
   No method enters the code from memory or from a tutorial.
4. **Proven, researched approach only.** Every estimator must pass validation before
   it ships (Section 7). A method that cannot be validated against an authoritative
   reference does not go in.
5. **Tamper-evident record.** Hash-chained ledger over every step: plan, sample,
   ingest, estimate, report. `verify` can say no — so its yes means something.
6. **Honesty is enforced by machinery, not intention.** Overclaim scanner, badge-truth
   tests, corrections table counting the director's errors and the AI's separately,
   and rule 14 from the governed-orchestration skill: a lesson that lives only in
   prose will not hold — build the check.

## 6. Standards and sources register (starting set — Phase 0 verifies and pins each)

| Area | Anchor |
|---|---|
| Survey estimation reference | R `survey` (Lumley) — numerical cross-check target |
| Stratified design & Neyman allocation | Cochran, *Sampling Techniques*; ts-sentry STEP-07 record (validated against Barnett's published VVR Table 2B to the digit) |
| Rare-event intervals | Wilson / Jeffreys per the published Google rare-events methodology (Unofficial Google Data Science, 2019) |
| Misclassification correction | Rogan & Gladen (1978); CI propagation per Lang & Reiczigel (2014) |
| Nearest full-system prior art | Pinterest, arXiv 2602.18518 (cited and positioned against — no code exists) |
| Platform methodology context | Meta CSER methodology posts; YouTube VVR methodology + Barnett assessment |
| DSA context (NEXT-queue emitter) | Regulation (EU) 2022/2065 Arts. 15/24/42; Implementing Regulation (EU) 2024/2835 |
| Security engineering | Official `cryptography` library docs; OpenSSF/SLSA guidance as used in ts-sentry STEP-08 |
| Code quality | Python 3.12+, ruff, mypy strict, frozen dataclasses, pyproject — the house stack |

## 7. Validation plan (how we prove the numbers are right)

1. **Cross-check fixtures.** Every estimator's output is compared against R `survey`
   results committed as fixtures. Agreement to ≥4 significant digits or the build is red.
2. **Reuse the strongest existing proof.** Port the ts-sentry stratified/Neyman code
   that already reproduced YouTube's published VVR assessment figures to the digit.
3. **The coverage demonstration (the flagship demo).** Use a fully labeled public
   dataset (candidate: Jigsaw Civil Comments family — license verified in Phase 0).
   Because every item is labeled, the TRUE prevalence is known. Draw many samples,
   estimate each time, and show the 95% intervals cover the truth ~95% of the time.
   Meta, Google, and Pinterest cannot publish this demo — their truths are
   confidential. This one is reproducible by anyone. It goes on the README front page.
4. **Refusal tests.** Every named refusal (undefined correction, unsampled stratum,
   broken chain, plan-hash mismatch) has a red test proving it fires.

## 8. Tripwires — pivot seams built into the architecture

`docs/TRIPWIRES.md` is a governed artifact. Each tripwire is checked at every phase
close and at release; the release checklist records "checked on <date>, not fired."
The architecture makes each pivot an adapter swap, never a rewrite: the estimator sits
behind an `EstimatorBackend` interface, and reports go through emitter adapters.

- **TW-1 — Pinterest open-sources the 2602.18518 system.**
  *Monitor:* arXiv page + Pinterest engineering GitHub, each phase close.
  *Pivot:* freeze the `lean` backend; write a `pinterest` backend adapter;
  reposition prevalence-kit as the governance/sealing/audit wrapper their release
  lacks (their design has an LLM in the evidence path — the spine is exactly what
  they did not ship). *Preserved:* plan format, sealing, ledger, gates, emitters —
  everything except estimator internals.
- **TW-2 — `svy` ships T&S prevalence + transparency output.**
  *Monitor:* svy releases/changelog. *Pivot:* retire overlapping `lean` estimators via
  the backend swap; offer the governance layer as an svy-ecosystem plugin.
  *Note:* the review found svy's installable code was not yet publicly downloadable —
  so v1.0 defaults to `lean` estimators + R-survey fixtures, and svy adoption is
  tracked as the reverse of this tripwire.
- **TW-3 — EU Commission or a DSA-adjacent body ships official accuracy-indicator
  tooling.** *Monitor:* DSA Transparency Database announcements + EUR-Lex, phase
  closes. *Pivot:* the (NEXT-queue) DSA emitter targets the official schema; any own
  schema is deprecated with a migration note. *Preserved:* everything upstream.

## 9. Build plan and scope cap

**Scope cap (charter constraint, named):** finding-bridge-sized. Target 1–2 weeks at
demonstrated velocity; 4 phases; if the phase count wants to grow, the feature moves
to NEXT instead. This is a portfolio tool, not a platform.

- **Phase 0 — ratification, no code.** Charter, this vision (corrected), TRIPWIRES.md,
  PRIOR-ART.md from the research register, STANDARDS.md skeleton, SECURITY.md threat
  model, dataset license ruling, crypto ruling, name-collision check for
  "prevalence-kit". Source-verify every claim in this document (the finding-bridge
  Phase 0 caught two real draft defects that way — assume this draft has some too).
- **Phase 1 — proof slice.** `plan` → `sample` (SRS) → `ingest-labels` (sealed) →
  `estimate` (Wilson) → `verify` → `emit-report`, end to end on synthetic data.
  The whole spine working on the simplest estimator.
- **Phase 2 — the honest-statistics layer.** Stratified + Neyman (ported, validated),
  Jeffreys, Rogan–Gladen with refusals, R-survey fixtures wired into CI.
- **Phase 3 — the flagship demo + launch.** Coverage demonstration on the public
  dataset; README with the demo front and center; docs; release to the ts-sentry
  supply-chain bar; PR to ROOST's awesome-safety-tools; post-release closure
  (LESSONS, corrections, rule census — the finding-bridge ritual).

**NEXT queue (recorded now, none started before its own prior-art review):**
importance sampling / ML-assisted weights (Hansen–Hurwitz + ESS diagnostics);
`emit-dsa` (2024/2835-shaped); Beta-Binomial upper bounds for very low prevalence;
label-quality gates as a fuller module (kappa/alpha); **eval-bridge** — explicitly
gated: no code before a dedicated prior-art sweep (Inspect AI, promptfoo, LangSmith,
Braintrust, W&B Weave, Arize Phoenix, OpenAI evals), because that seam is crowded and
the gap is unverified.

## 10. Honest limits (v1.0, stated up front)

- Measures prevalence of labeled samples from a defined population. It cannot fix a
  bad sampling frame, biased labels, or a dishonest plan — it can only make them
  visible and permanent in the record.
- v1.0 label quality relies on provided Se/Sp when correction is used; it does not
  estimate rater quality itself (NEXT).
- Interval guarantees are sampling-only, matching the caveat YouTube publishes for VVR.
- Synthetic and public-dataset validation only; no claim of production deployment.
- Built by directing an AI (Claude Code) under the governed process; the director
  wrote none of the code and all of the decisions. Stated in the README, measured in
  the provenance section — the finding-bridge standard.

## 11. Why me (one paragraph, for the README later)

I spent a decade doing the labeling and review work these numbers are built from, and
this year I shipped two governed, audited tools for the analysts who come after the
labels: a Trust & Safety workbench (ts-sentry, 1,230 tests) and a red-team findings
pipeline (finding-bridge, sealed-by-default, validated on 739 real attack prompts).
prevalence-kit completes the arc: label → finding → number. Every claim in it is
verifiable in the public record, which is the whole point of the tool.
