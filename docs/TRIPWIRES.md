# Tripwires

**Status: RATIFIED — 28 August 2026.**

A tripwire is a thing that, if it happened, would change what this project should be. We write them
down now, while we are honest, rather than later, when we are invested.

Each tripwire says four things: how we watch for it, how often, what we do if it fires, and what
survives the pivot.

**The architecture makes each pivot an adapter swap, never a rewrite.** The estimator sits behind an
`EstimatorBackend` interface. Reports go out through emitter adapters. That is a design commitment
of this charter, and it is what makes the "preserved" column below true rather than hopeful.

## The ritual

- Every tripwire is checked at **every phase close** and again at **release**.
- The result is recorded in the phase outcome as `checked <date>, not fired` or
  `checked <date>, FIRED`.
- A tripwire that is never checked is a decoration. If a phase closes without the check, that is a
  deviation and it is recorded as one.
- **Rule 14 applies.** Where a check can be a script, it becomes one. Where it cannot, it is a named
  manual step with a URL, not a memory.

---

## TW-1 — Pinterest open-sources the 2602.18518 system

**Why it matters.** Pinterest has the nearest thing to a full production prevalence system, and it
is closed. If they release it, the estimator half of this project stops being the contribution.

**What fires it.** Any public release of runnable code implementing the system in arXiv 2602.18518.
A repository under `pinterest`, a paper revision adding a code-availability statement, or a
third-party release blessed by the authors.

**Monitor.**

| What | Where |
|---|---|
| Paper revisions | `http://export.arxiv.org/api/query?id_list=2602.18518` — check for a version later than **v2 (2026-08-17)**, and for a `journal_ref` or DOI appearing |
| Pinterest's repos | `https://api.github.com/orgs/pinterest/repos?per_page=100` — 99 repos at the 2026-08-28 baseline, none relevant |
| The open web | GitHub repository search for `prevalence policy violating content` — **0 results** at baseline |

All three are scriptable. Build the script in Phase 1.

**Cadence.** Every phase close. Every release.

**Pivot if it fires.**
1. Freeze the `lean` estimator backend where it stands. Do not race them.
2. Write a `pinterest` backend adapter behind the existing `EstimatorBackend` interface.
3. Reposition: prevalence-kit becomes the governance, sealing and audit wrapper their release does
   not have. Their design puts an LLM in the evidence path. Our spine is exactly the thing they did
   not ship.

**Preserved.** Plan format. Pre-registration hash. Sealing. Ledger. Refusal gates. Report emitters.
Everything except estimator internals.

**Honest note.** This tripwire would be *good news*. A released Pinterest system makes the
governance layer more valuable, not less, because there would then be something real to govern.

---

## TW-2 — `svy` ships Trust & Safety prevalence and transparency output

**This tripwire was rewritten in Phase 0. The vision's version rested on a false premise.**

The vision said svy's installable code "was not yet publicly downloadable." That is false.
`pip install svy==0.25.0` was run in a clean virtual environment on 2026-08-28 and succeeded.
See `docs/PHASE-0-VERIFICATION.md` §A8.

**The real baseline, read from the 0.25.0 source on 2026-08-28.**

| Capability | svy 0.25.0 |
|---|---|
| SRS selection | present |
| Stratified + proportional allocation | present |
| **Neyman (optimal) allocation** | **present**, with named refusals |
| **Wilson interval** | **present** |
| Clopper-Pearson / Korn-Graubard / logit intervals | present |
| Taylor-linearization variance, replicate weights, post-stratification, raking, calibration | present |
| Sample size and power | present |
| Jeffreys interval | absent |
| Rogan–Gladen correction | absent |
| Sealing, hash-chained ledger, encryption, audit trail | absent |

**So the overlap on estimators is already large, and this is not a future risk — it is today's
position.** What svy does not have is the entire governance half: pre-registration, sealing, the
ledger, the refusals, the report, the audit trail.

**What fires this tripwire now.** svy adding any of: a prevalence-framed API, a transparency-report
emitter, content sealing, or an audit ledger.

**Monitor.**

| What | Where |
|---|---|
| Releases | `https://pypi.org/pypi/svy/json` — baseline **0.25.0, uploaded 2026-08-26** |
| Changelog | `https://github.com/samplics-org/svy/blob/main/packages/svy/CHANGELOG.md` |
| Source shape | grep the sdist for `prevalence`, `ledger`, `seal`, `encrypt`, `transparency`, `rogan` — **all zero at baseline except `prevalence` in unrelated docstrings** |

**Cadence.** Every phase close. Every release. svy is releasing fast — 48 releases, the latest two
days before baseline — so this is the tripwire most likely to move.

**Pivot if it fires.** Retire the overlapping `lean` estimators through the backend swap. Offer the
governance layer as an svy-ecosystem plugin rather than a competing tool.

**Preserved.** Plan format, sealing, ledger, gates, emitters, the CLI.

**Why we still write `lean` estimators — the corrected reason, ruled R-1 / D-2.** Not because svy is
unavailable. It is available and it is good, and the README credits it as the estimator layer.
Because **svy declares a hard runtime dependency on `httpx`**
(`Requires: httpx, msgspec, numpy, polars, scipy, svy-io, svy-rs`), which pulls in `httpcore`,
`anyio` and `certifi`. Hard Rule 1 of this project is zero network calls at runtime, proven by a
test that fails if any network capability appears in the dependency tree. We cannot make that
guarantee and ship an HTTP client. That is an architectural reason, and it is checkable.

**Standing obligation.** `lean` estimators are validated against R `survey` 4.5 fixtures, and where
svy covers the same estimator, **against svy too** — in a separate optional test environment, so the
runtime tree stays clean. Agreeing with two independent implementations is stronger than agreeing
with one. Owned by Phase 2.

---

## TW-3 — Official DSA accuracy-indicator tooling appears

**Why it matters.** If the Commission or a DSA-adjacent body ships a schema or a tool for the
Article 15(1)(e) accuracy indicators, any format we invent is instantly legacy.

**Baseline, verified 2026-08-28.** Implementing Regulation (EU) 2024/2835 of 4 November 2024 is in
force, unamended, with no consolidated version and no repeal date (`END-OF-VALIDITY 9999-12-31`).
No official computation tooling was found. The templates are documents, not software.

**Note what this tripwire is and is not about.** It is about the **accuracy indicators** — accuracy,
precision, recall, and the sensitivity/specificity guidance — not about prevalence. **No EU
regulation requires prevalence.** The word appears zero times in 2024/2835 and zero times in the DSA
itself. See `docs/PHASE-0-VERIFICATION.md` §B5.

**What fires it.** Official tooling, an official machine-readable schema, or a Commission-published
calculation methodology for the Annex I indicators.

**Monitor.**

| What | Where |
|---|---|
| Amendments to 2024/2835 | `http://publications.europa.eu/resource/celex/32024R2835` with `Accept: application/xml;notice=branch` — watch for amendment relations, and probe `02024R2835-*` for a consolidated version appearing |
| New implementing acts | EUR-Lex search for implementing acts citing Regulation 2022/2065 |
| Commission announcements | `https://digital-strategy.ec.europa.eu/` DSA section |
| DSA Transparency Database | `https://transparency.dsa.ec.europa.eu/` |

**Retrieval note for whoever runs this check.** `eur-lex.europa.eu` sits behind an AWS WAF bot
challenge and returns HTTP 202 with an empty body to scripted fetches. Use the EU Publications
Office endpoint above instead — same authority, machine-readable, no challenge.

**Cadence.** Every phase close. Every release. Low expected rate of change.

**Pivot if it fires.** The NEXT-queue `emit-dsa` emitter targets the official schema instead of one
of ours. Any own schema is deprecated with a migration note. Since `emit-dsa` is not in v1.0, this
pivot is cheap by design — that is why it is not in v1.0.

**Preserved.** Everything upstream of the emitter: plan, sample, seal, estimate, verify.

---

## Baseline record

Every tripwire above was checked on **28 August 2026** as part of Phase 0. Result:

| Tripwire | Status |
|---|---|
| TW-1 Pinterest open-sources | checked 2026-08-28, **not fired** |
| TW-2 svy ships T&S prevalence / transparency | checked 2026-08-28, **not fired** — but the baseline was corrected; svy is installable and overlaps more than the vision assumed |
| TW-3 Official DSA tooling | checked 2026-08-28, **not fired** |

## Check log

| Date | Phase | TW-1 | TW-2 | TW-3 | Notes |
|---|---|---|---|---|---|
| 2026-08-28 | Phase 0 | not fired | not fired | not fired | Baseline established. TW-2 rewritten after its premise was found false. |
