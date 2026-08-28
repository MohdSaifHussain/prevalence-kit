# Ratification record — Phase 0

**Date:** 28 August 2026
**Ratified by:** Mohd Saif Hussain (director)
**Effect:** `PROJECT_CHARTER.md` is binding from this date.

The director's rulings are reproduced **verbatim**, exactly as given. Nothing is paraphrased,
summarised, or tidied. Where a ruling contains a precondition or an instruction, that text appears
here unchanged and is tracked in the disposition column.

---

## The rulings, as given

> **R-1 ACCEPTED as recommended.** Keep lean; httpx/zero-network is the recorded rationale
> (availability argument retired). Cross-check fixtures against BOTH R survey and svy as independent
> witnesses. README repositioning accepted: credit svy as the estimator layer; prevalence-kit claims
> the governance, label-quality, and audit layer only.

> **R-2 ACCEPTED.** Invert the regulatory positioning exactly as drafted: 2024/2835 mandates accuracy
> (sensitivity/specificity); prevalence-kit shows what those mandated quantities do to the estimate
> (Rogan-Gladen). No claim anywhere that any regulation requires prevalence.

> **R-3 ACCEPTED, all three fixes.** Funding figure: cite the launch release ("more than $27
> million", with date); footnote that ROOST's First 100 Days post states $28.5M - record the source
> conflict, don't resolve it.

> **R-4 ACCEPTED.** Anchor: Brown, Cai & DasGupta 2001 (Statistical Science). Intervals: Wilson +
> Clopper-Pearson. Jeffreys dropped. Blog demoted to context citation only.

> **R-5 RULED: Fernet.** Grounds: soak time (Cobblestone-128 is 4 weeks old; a tool about
> auditability anchors on reviewed, aged primitives), cross-project consistency with
> finding-bridge's sealed store, and the binding property is achievable via AES-GCM AAD if ever
> needed. Chunking answers the size limit; document it as a stated v1.0 limit in SECURITY.md. Record
> Cobblestone as considered-and-rejected in DECISIONS.md with this reasoning. Precondition: I will
> verify Cobblestone-128's existence in the official cryptography changelog myself; if it does not
> exist as described, that is a separate defect - report it as one.

> **R-6 ACCEPTED as recommended** (develop 3.14, floor >=3.12, CI 3.12/3.13/3.14).

> **R-7 ACCEPTED.** Wording: pre-registered threshold estimand; truth knowable by census at each
> threshold. Extend the coverage demo to multiple pre-registered thresholds (sensitivity curve) -
> the float labels are an asset, use them.

> **Corrections table:** open entries for the six draft defects. Source attribution: DSA-prevalence
> claim, Jeffreys-Google claim, and "TRUE prevalence is known" originate from the chat reviewer's
> draft; KDD '26 and the funding figure passed through from the research report unverified; svy
> availability was stale at draft time and TW-2 was built on it despite installability being queued
> as a ruling.

> **Proceed to charter ratification with these rulings applied, then present the Phase 1 (proof
> slice) contract.**

---

## Disposition

| Ruling | Recorded as | Applied in | Status |
|---|---|---|---|
| R-1 | D-2, D-3, D-4 | Charter §3, §6.1, §7 · TRIPWIRES TW-2 · PRIOR-ART §1 | applied |
| R-2 | D-5 | Charter §3 "What we do NOT claim" · PRIOR-ART §5 · STANDARDS S-4 | applied |
| R-3 | D-6, D-7 | PRIOR-ART §2, §3 · STANDARDS S-3.3 | applied |
| R-4 | D-8 | Charter §4 `estimate`, §5.3, §7 · STANDARDS S-1.1 · PRIOR-ART §4 | applied |
| R-5 | D-9 | Charter §5.1 · SECURITY §3.10, §6 · STANDARDS S-5.1 | applied |
| R-6 | D-10 | STANDARDS S-6 | applied |
| R-7 | D-11 | Charter §6.3 · STANDARDS S-7.1 | applied |
| Corrections instruction | `docs/CORRECTIONS.md` C-1 … C-6 with the director's source attribution | new file | applied |

## The R-5 precondition, discharged

The director required independent verification that Cobblestone-128 exists as described, and
directed that its absence be reported as a separate defect.

**It exists. No defect.**

The official `cryptography` changelog, under the heading `50.0.0 - 2026-07-31`, states verbatim:

> *"Added the Cobblestone (streaming symmetric encryption) recipe, an implementation of the
> Cobblestone-128 and Cobblestone-256 instantiations of the C2SP chunked-encryption specification
> for streaming authenticated encryption of large messages."*

Confirmed at two independent official URLs on 2026-08-28: `cryptography.io/en/50.0.1/changelog/`
and `cryptography.io/en/stable/changelog/`. Both serve documentation labelled **50.0.1**. The
`50.0.0` release date of **2026-07-31** is confirmed in the changelog index and matches the PyPI
upload date, making the "four weeks old" ground for the ruling factually correct.

**A pinning finding came out of the same check, and it is recorded as D-13.** Measured the same day:

| URL | Version served |
|---|---|
| `cryptography.io/en/latest/` | **51.0.0-dev1** — unreleased |
| `cryptography.io/en/stable/changelog/` | 50.0.1 |
| `cryptography.io/en/50.0.1/changelog/` | 50.0.1 |

`/stable/` agrees today and will silently become 51.0.0 when that ships. Only the explicit version
pin holds. `docs/STANDARDS.md` cites explicit pins throughout.

## The ROOST source conflict, recorded and not resolved

Per R-3. Both official ROOST sources, verbatim, neither preferred:

| Source | Date | Verbatim |
|---|---|---|
| Launch press release *(primary citation)* | **10 February 2025** | *"To date, ROOST has raised more than **$27 million** for its first four years of operations from a range of leading philanthropies and top technology companies."* |
| ROOST blog, *First 100 Days: Building & Planning* *(footnote)* | **4 June 2025** | *"Thanks to an initial **$28.5 million** in funding **and in-kind contributions** from founding partners"* |

The two differ in figure, in wording, and in date. Any reconciliation would be our inference rather
than either source's statement. Recorded as D-7 and left unresolved, as ruled.

## Standing directions in force

Given by the director during Phase 0. Binding on all later phases.

| Date | Direction, as given |
|---|---|
| 2026-08-28 | "EVERYTHING should be 2026 updated aligned to the latest. be it coding, be it any framework bieng applied or applicable" |
| 2026-08-28 | "make sure you have a document where time/date is being recorded for this whole project ... please track it in a .txt" — implemented as `TIME-LOG.txt` |
| 2026-08-28 | "please be careful while dwnloading from unbofficial sources" |
| 2026-08-28 | `C:\Users\mohds\ts-sentry` is **read-only**. Reference only. No write actions. |

## What Phase 0 produced

| Artifact | Lines | What it is |
|---|---|---|
| `PROJECT_CHARTER.md` | ~290 | The binding contract |
| `docs/PHASE-0-VERIFICATION.md` | 639 | 24 claims checked against primary sources |
| `docs/PRIOR-ART.md` | 339 | The register, with the gap stated at the width of the evidence |
| `docs/STANDARDS.md` | ~200 | Every source pinned by version, date or DOI |
| `docs/TRIPWIRES.md` | 177 | Three pivot seams, with baselines |
| `docs/DECISIONS.md` | — | D-1 … D-13 |
| `docs/CORRECTIONS.md` | — | C-1 … C-6, six draft defects |
| `SECURITY.md` | ~230 | Threat model, written before any code |
| `docs/RULINGS-QUEUE.md` | 286 | Closed |
| `TIME-LOG.txt` | — | Append-only wall-clock record |

**Phase 0 closed. No code was written. No package was scaffolded. `git init` had not been run.**
