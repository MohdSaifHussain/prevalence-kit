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

## TW-5 — The mirror stops carrying CRAN's bytes

**Added 2026-08-29, from V-17. Not fired on its first check.**

**Why it matters.** S-2.1 names CRAN as the source of `survey`. The R image installs from
**Posit Package Manager**, because that is the mirror `rocker/r-ver` pins. Two names, one package,
and until V-17 nobody had checked they were the same package.

**What fires it.** Any file beyond the known metadata pair differing between CRAN's tarball and the
mirror's, or the file lists diverging at all.

**Baseline, measured 2026-08-29.** 355 entries: 341 regular files, 14 directories.
**339 of the 341 files are byte-identical.** Two differ, both repository metadata:

| File | Why it differs |
|---|---|
| `DESCRIPTION` | The mirror writes `Repository: RSPM` where CRAN writes `Repository: CRAN`, and adds `Encoding: UTF-8` |
| `MD5` | Follows from the line above — it lists `DESCRIPTION`'s own checksum |

`R/`, `src/`, `man/`, `data/`, `inst/`, `tests/` and `NAMESPACE` match exactly.

**Monitor.** `tools/check_tripwires.py` TW-5 fetches both tarballs and compares them member by
member. The two allowed differences are named in the code, so a third one fires.

**Cadence.** Every phase close. Every release.

**Pivot if it fires.** Read the differing file. If the mirror is serving something CRAN is not, build
the witness image against CRAN directly and record the change in S-2.1a and S-8.4.

**Preserved.** Everything. This watches a supply route, not a design choice.

**What it does not cover, stated so nobody reads it wider.** It compares **source** tarballs. The
image installs a **binary** p3m built from its own copy of that source. Rebuilding that binary and
comparing is a stronger check and is not done.

---

## TW-4 — A SHA-pinned GitHub Action falls behind its runtime

**Added 2026-08-29, after the first CI run. FIRED on its first check.**

**Why it matters.** Charter §5.1 requires SHA-pinned actions, because a tag can move.

But pinning is what stops an action updating itself. **So a pin has an expiry, and someone has to
watch it.** That is the price of pinning, not a reason against it. The alternative is an action that
changes under us without telling anyone.

**What fires it.** A pinned action superseded by a newer release, or the runtime it targets being
withdrawn.

**Recorded state, 2026-08-29** (`docs/STANDARDS.md` S-5.4):

| Action | Pinned | SHA | Runtime it targets | Latest release |
|---|---|---|---|---|
| `actions/checkout` | **v5.0.0** | `08c6903cd8c0fde910a37f88322edcfb5dd907a8` | Node 20 | **v7.0.1** |
| `actions/setup-python` | **v5.6.0** | `a26af69be951a213d495a4c3e4e4022e16d87065` | Node 20 | **v7.0.0** |

Both are **two major versions behind**. Run `33204075014` carried **28 deprecation warnings**:
*"Node.js 20 is deprecated. The following actions target Node.js 20 but are being forced to run on
Node.js 24."*

> **Correction, 2026-08-31 — C-50.** The checkout row above was false when it was written.
> `action.yml` at `08c6903` declares `using: node24` — immutable at that SHA — so checkout
> **v5.0.0 never targeted Node 20**, and every deprecation warning in that run and since names
> `setup-python` alone. The table is a dated recorded-state block and is kept as written; this
> note is the disclosure, and the 2026-08-31 baseline below is the corrected record. The
> runtime column there is **derived from each action's `action.yml` at the pinned SHA**, not
> written by hand — hand-writing it is what produced the false cell.

**Recorded state, 2026-08-31, after the O-19 re-pin at D3.1** (`docs/STANDARDS.md` S-5.4):

| Action | Pinned | SHA | Runtime it declares (`action.yml` at that SHA) | Latest release |
|---|---|---|---|---|
| `actions/checkout` | **v7.0.1** | `3d3c42e5aac5ba805825da76410c181273ba90b1` | `using: node24` | **v7.0.1** |
| `actions/setup-python` | **v7.0.0** | `5fda3b95a4ea91299a34e894583c3862153e4b97` | `using: node24` | **v7.0.0** |

Both at their latest release, both declaring the runtime GitHub's hosted runners now force. The
event this tripwire was written to beat — the Node 20 withdrawal — **partly happened before the
re-pin**: the changelog of 2025-09-19 began forcing node20 actions onto Node 24, so the
setup-python jobs were already running on a runtime the pinned action did not declare, passing
anyway. The re-pin ends that state rather than pre-empting it.

**What it will look like when GitHub drops Node 20.** Not a wrong answer. **A red X on every job,
with nothing wrong in this repository** — no code change, no failing test, no commit that caused it.

Whoever debugs it will start hunting a bug that is not there. This paragraph exists so they read it
first.

**Monitor.**

| What | Where |
|---|---|
| A newer release of a pinned action | `https://api.github.com/repos/<owner>/<repo>/releases/latest`, compared against the pin **read out of `.github/workflows/gate.yml`**, never a copy of it |
| The runtime deprecation itself | The warning text in any run's annotations |

Scripted: `tools/check_tripwires.py` TW-4. It reads the workflow rather than carrying its own copy of
the SHA, so the tripwire and the artifact cannot drift apart.

**It fires on "a newer release exists", not on "Node 20 is gone"** — the first is the signal that can
still be acted on. By the time the second is true, the decision has been made for us.

**Cadence.** Every phase close. Every release.

**Pivot if it fires.** It has fired. **That is a decision for the director, not a red X. The tool
exits 0.**

The decision: re-pin to the current release SHAs, re-verify, and record the new pins in S-5.4. Weigh
that against D-26 — redoing verified, committed work to reach an equally good result is churn. Owned
by **Phase 3**, where the supply chain gets its bar. **O-19.**

**Preserved.** Everything. This is a CI pin, not a design commitment.

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
