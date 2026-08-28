# Standards register

**Status: RATIFIED — 28 August 2026.** Skeleton; entries are added as phases pin new sources.
**All entries verified 28 August 2026.** Evidence: `docs/PHASE-0-VERIFICATION.md`.

Every method, control and format used by prevalence-kit is anchored here to a named primary source,
pinned by version, date or commit. Nothing enters the code from memory or from a tutorial.

---

## The three rules of this register

**1. Pin the version. Never `/latest/`, and never `/stable/` either.**
Measured on 2026-08-28 (decision D-13):

| URL | Version served |
|---|---|
| `cryptography.io/en/latest/` | **51.0.0-dev1** — an unreleased dev build |
| `cryptography.io/en/stable/changelog/` | 50.0.1 |
| `cryptography.io/en/50.0.1/changelog/` | 50.0.1 |

`/latest/` was already wrong. `/stable/` happened to be right *that day*, and will silently become
51.0.0 when it ships — which is exactly how a moving alias lulls a reader. Only the explicit
version pin holds. Every documentation URL below is version-locked.

**2. Official sources only. A blog is a tutorial.**
Peer-reviewed papers, standards bodies, official documentation, statutory texts, and package
registries. Nothing else can be a *method source*. Non-official material may appear as **context**,
clearly marked, and may never be cited as the reason a method was chosen.

**3. Flip-day re-check.**
Every source has a **re-check date**. On that date, the pin is re-fetched and either confirmed or
updated with a dated note. A pin nobody re-checks is a pin that quietly expires.

**Retrieval note -- corrected 2026-08-29. The earlier version of this note no longer works.**

`eur-lex.europa.eu` blocks scripts. It answers **HTTP 202 with an empty body**. Measured again on
2026-08-29, on the legal notice and on the CELEX record for `32011D0833`: both 202, both 0 bytes.
That has not changed.

The workaround changed. The Publications Office endpoint needs **two** headers. The version of this
note written on 2026-08-28 gave only one:

    curl -H "Accept: application/xhtml+xml" -H "Accept-Language: eng" \
         http://publications.europa.eu/resource/celex/<CELEX>

**Measured 2026-08-29 against `32011D0833`:**

| Request | Result |
|---|---|
| `Accept: application/xhtml+xml` alone | **HTTP 400**, 205 bytes: *"Invalid content type CONTENT_STREAM for WORK ... without language"* |
| `Accept: text/html` alone | HTTP 400, 205 bytes |
| no `Accept` header | HTTP 200, but `application/rdf+xml` -- metadata, not the act |
| **both headers** | **HTTP 200**, 48,730 bytes, `application/xhtml+xml` |

The one-header call also fails on `32024R2835` -- the CELEX this note was written for.

**So the recorded procedure had stopped working on the document it was written for, and nothing said
so.** `docs/CORRECTIONS.md` C-22.

---

## S-1 — Statistical method

| ID | Method | Source | Pin | Re-check |
|---|---|---|---|---|
| S-1.1 | Binomial interval estimation — **ships Wilson (primary) + Clopper-Pearson (conservative). Jeffreys dropped, ruling R-4.** | Brown, L.D., Cai, T.T., DasGupta, A., *Interval Estimation for a Binomial Proportion*, **Statistical Science** 16(2) | **2001**, DOI `10.1214/ss/1009213286` | never — fixed publication |
| S-1.2 | Stratified sampling, Neyman (optimal) allocation | Neyman, J., *On the Two Different Aspects of the Representative Method* | **1934**, reprint DOI `10.1007/978-1-4612-4380-9_12` | never |
| S-1.3 | Sampling design reference | Cochran, W.G., *Sampling Techniques*, Wiley | **3rd edition, 1977**, ISBN `0-471-16240-X` | never |
| S-1.4 | Misclassification correction | Rogan, W.J. & Gladen, B., *Estimating Prevalence from the Results of a Screening Test*, **Am. J. Epidemiol.** | **1978**, DOI `10.1093/oxfordjournals.aje.a112510` | never |
| S-1.5 | Confidence limits for corrected prevalence | Lang, Z. & Reiczigel, J., *Confidence limits for prevalence of disease adjusted for estimated sensitivity and specificity*, **Prev. Vet. Med.** | **2014**, DOI `10.1016/j.prevetmed.2013.09.015` | never |
| S-1.6 | Exact limits with an imperfect test (Phase 2 cross-check) | Reiczigel, J., Földi, J., Ózsvári, L., **Epidemiol. Infect.** | **2010**, DOI `10.1017/s0950268810000385` | never |

**Refusal conditions are mathematical consequences, not citations.** The Rogan–Gladen estimator is
`π̂ = (p̂ + Sp − 1)/(Se + Sp − 1)`. The denominator vanishes at `Se + Sp = 1` and the estimator
inverts sign below it. Refusing there is arithmetic, and it is marked as such so no reader mistakes
it for a claim about a source.

## S-2 — Validation targets

| ID | Target | Source | Pin | Re-check |
|---|---|---|---|---|
| S-2.1 | Numerical cross-check for every estimator | R **`survey`** (Lumley) | **4.5**, published **2026-02-24**; re-verified live **2026-08-29**; source `https://cran.r-project.org/src/contrib/survey_4.5.tar.gz` (HTTP 200); GPL-2 \| GPL-3 | **2026-11-28** |
| S-2.1a | The R environment the witness runs in | `rocker/r-ver`, **pinned by digest, not by tag** | **`rocker/r-ver@sha256:c3f39b365d1077fe24f8e9ab2742e352b6d3950897f51af1624a5bb5550c21c0`** (tag `4.5.3`, pushed 2026-06-24). Docker 29.7.2 on this machine. | **2026-11-29** |
| S-2.1b | The witness **as actually executed**, 2026-08-29 (O-3) | `r/Dockerfile` builds on S-2.1a | **R 4.5.3 (2026-03-11)**, **`survey` 4.5**, `jsonlite` 2.0.0. CRAN frozen at the base image's snapshot `https://p3m.dev/cran/__linux__/noble/2026-04-23`, so the install is deterministic and serves the version S-2.1 pins. **The exact call:** `svydesign(ids = ~1, strata = ~stratum, weights = ~w, data = sample_rows)` — no `fpc`, which is what makes it the with-replacement form S-2.3 specifies | **2026-11-29** |
| S-2.2 | Second independent cross-check where coverage overlaps | Python **`svy`** (Samplics LLC) | **0.25.0**, uploaded **2026-08-26**; MIT | **2026-09-28** — fast-moving, 48 releases |
| S-2.3 | Stratified/Neyman allocation reproduction | Barnett, A., *YouTube's Violative View Rate Methodology: A Statistical Assessment*, MIT | **September 2021**, Tables 2A / 2B | never — fixed publication |

**Why by digest and not by tag.** `rocker/r-ver:4.5` and `:4.5.3` resolve to the same image today.
`4.5` is a moving pointer and will not. A witness that is meant to be reproducible by a stranger
cannot be pinned to something that moves. Phase 2 contract R2.6.

**S-2.3 specification, pinned by reproduction not by intention.** Independently recomputed on
2026-08-28 (`docs/PHASE-0-VERIFICATION.md` §C6). The estimator that reproduces Barnett's Table 2B is:

- allocation `n_h ∝ W_h · √(p_h(1−p_h))` (Neyman, with the proportion standard deviation)
- variance `Var = Σ W_h² · p_h(1−p_h)/n_h` — **with replacement, no finite-population correction**

Reproduced values: allocations `2098 / 828 / 584 / 256 / 234` against published
`2098 / 828 / 584 / 256 / 234`; population VVR `0.2000%` against published `0.20%`; expected standard
deviation `0.0539 pp` against published `0.054 pp`.

**Provenance caveat carried forward:** Barnett's assessment was *"commissioned and funded by
Google."* Expert review, not independent peer review. State this wherever it is cited.

## S-3 — Platform methodology (context; sets the honest limits)

| ID | Subject | Source | Pin | Re-check |
|---|---|---|---|---|
| S-3.1 | YouTube VVR method + interval caveat | Google Transparency Report Help Centre, *YouTube Community Guidelines enforcement FAQs* | fetched **2026-08-28** | **2026-11-28** |
| S-3.2 | Meta prevalence method | Meta Transparency Center, *Prevalence*, `transparency.meta.com/policies/improving/prevalence-metric/` | fetched **2026-08-28** | **2026-11-28** |
| S-3.3 | Nearest full system | Dobi et al., arXiv **2602.18518v2** | v1 **2026-02-19**, **v2 2026-08-17** | **every phase close** (TW-1) |
| S-3.4 | Only open ancestor | `facebookarchive/ml_sampler` | last commit **2020-08-06**, archived, licence `NOASSERTION` | **2027-08-28** |

**S-3.1 verbatim caveat, adopted as our own honest limit:**
> *"The confidence intervals do not take into account rater quality, which may impact our
> measurements."*

## S-4 — Regulation (context only — no regulation requires prevalence)

| ID | Instrument | Pin | Re-check |
|---|---|---|---|
| S-4.1 | Regulation (EU) 2022/2065 (Digital Services Act) | **19 October 2022**; OJ L 277, 27.10.2022, p. 1; ELI `http://data.europa.eu/eli/reg/2022/2065/oj`; CELEX `32022R2065` | **2027-02-28** |
| S-4.2 | Commission Implementing Regulation (EU) 2024/2835 | **4 November 2024**; OJ L series 2024/2835, **5.11.2024**; CELEX `32024R2835`; in force, **unamended**, `END-OF-VALIDITY 9999-12-31`, no consolidated version | **every phase close** (TW-3) |
| S-4.3 | **Commission Decision 2011/833/EU** on the reuse of Commission documents -- the reuse anchor, not a prevalence source | **12 December 2011**; OJ L 330, **14.12.2011**, p. 39; CELEX `32011D0833`; ELI `http://data.europa.eu/eli/dec/2011/833/oj`; repeals 2006/291/EC, Euratom | **2027-02-28** |

**Recorded finding, and it governs how the README may be written:** the word "prevalence" appears
**zero times** in S-4.1 and **zero times** in S-4.2, counted mechanically over the full official
texts. What 2024/2835 requires under Annex I §1.6 is accuracy, precision and recall of automated
moderation, with qualitative guidance naming sensitivity and specificity.

**Local copies held.** `OJ_L_202402835_EN_TXT.pdf` (48 pages, sha256
`daff77f027fde1e0f92f89d70114327255456a3a4fa420fb6478da204a31337b`), downloaded independently by the
director from EUR-Lex on 2026-08-28. It agrees verbatim with the Publications Office XHTML on every
sentence quoted in this project.

Dates, for the record: templates apply from **1 July 2025**; the Commission's announcement of
4 November 2024 says *"the first harmonised reports due in the beginning of 2026"*; recital (9) says
*"The first full harmonised reporting cycle covers 1 January 2026 until 31 December 2026"*; reports
are due within two months of each period's end.

### The reuse question -- O-18's evidence, gathered 2026-08-29

**What O-18 asks.** Can `OJ_L_202402835_EN_TXT.pdf` go in a public repository? The EUR-Lex reuse
terms had to be **checked, not assumed**. Phase 2 contract, section 10.

**We anchor to the law, not to the website's summary of it.** The EUR-Lex legal notice says the
reuse policy "is based on Decision 2011/833/EU". That is the Publications Office describing a law in
its own words. Hard Rule 3 says go to the law itself. So the articles below are quoted from the
Decision. The notice is recorded as **backup evidence**, not as the anchor.

**Quoted verbatim from Decision 2011/833/EU** (S-4.3):

> **Article 2, Scope.** *"1. This Decision applies to public documents produced by the Commission or
> by public and private entities on its behalf: (a) which have been published by the Commission or
> by the Publications Office on its behalf through publications, websites or dissemination tools;
> or (b) which have not been published for economic or other practical reasons, such as studies,
> reports and other data."*
>
> *"2. This Decision shall not apply: (a) to software or to documents covered by industrial property
> rights such as patents, trademarks, registered designs, logos and names; (b) to documents for
> which the Commission is not in a position to allow their reuse in view of intellectual property
> rights of third parties; (c) to documents which pursuant to the rules established in Regulation
> (EC) No 1049/2001 are excluded from access or only made accessible to a party under specific rules
> governing privileged access; (d) to confidential data ...; (e) to documents resulting from ongoing
> research projects ..."*
>
> *"4. Nothing in this Decision authorises reuse of documents in a manner calculated to deceive or
> to defraud."*
>
> **Article 4, General principle.** *"All documents shall be available for reuse: (a) for commercial
> or non-commercial purposes under the conditions laid down in Article 6; (b) without charge,
> subject to the provisions laid down in Article 9; and (c) without the need to make an individual
> application, unless otherwise provided in Article 7."*
>
> **Article 6, Conditions for reuse of documents.** *"1. Documents shall be made available for reuse
> without application unless otherwise specified and without restrictions or, where appropriate, an
> open licence or disclaimer setting out conditions explaining the rights of reusers."*
>
> *"2. Those conditions, which shall not unnecessarily restrict possibilities for reuse, may include
> the following: (a) the obligation for the reuser to acknowledge the source of the documents;
> (b) the obligation not to distort the original meaning or message of the documents; (c) the
> non-liability of the Commission for any consequence stemming from the reuse."*

**The backup evidence.** This is the EUR-Lex legal notice, copyright section. The director read it
in a browser on 2026-08-29 and typed it out, because no fetcher here can reach the page:

> *"(c) European Union, 1998-2026 ... The Commission's document reuse policy is based on Decision
> 2011/833/EU. Unless otherwise specified, you can re-use the legal documents published in EUR-Lex
> for commercial or non-commercial purposes."*

**We fetched the Decision twice, two different ways, and the two agree.** One is the director's PDF
of OJ L 330. The other is the Publications Office XHTML for CELEX `32011D0833`. Both were extracted
and compared on Articles 2, 4 and 6. They match word for word.

The second copy exists only because we ran the recorded procedure instead of trusting it. See the
retrieval note above, and C-22.

**"Unless otherwise specified" -- checked against the act itself, not assumed.**

"Unless otherwise specified" comes from Article 6(1). The notice gives International Accounting
Standards as an example of a document with special conditions, and says those conditions appear in
the Official Journal itself. So the place to look is the act.

**What we searched.** The whole of `OJ_L_202402835_EN_TXT.pdf` -- 48 pages, 4,595 lines of extracted
text. Terms: `reproduc`, `copyright`, `(c) European Union`, the copyright symbol, `all rights
reserved`, `reuse`, `re-use`, `licence`, `license`, `2011/833`, `permission`, `otherwise specified`,
`otherwise stated`, `special condition`. We also read the first page, the last page, and the PDF's
own metadata.

**What we found: nothing.** There are four hits on `copyright`. All four are ordinary content -- the
`KEYWORD_COPYRIGHT_INFRINGEMENT` category in the reporting template, and a note about counting
copyright complaints. The copyright symbol does not appear at all. The metadata holds no `dc:rights`,
`xmpRights`, `WebStatement` or `Marked` tag. The only thing on every page is the ELI footer,
`http://data.europa.eu/eli/reg_impl/2024/2835/oj`.

**So nothing is otherwise specified in this act.** We ran that check. The search terms are listed
above so anyone can run it again.

**Where this stops.** Decision 2011/833/EU covers documents **made by the Commission**.
Implementing Regulation (EU) 2024/2835 is a Commission act, so Article 2(1)(a) covers it.

**Regulation (EU) 2022/2065 -- the DSA, S-4.1 -- is a Parliament and Council act.** This evidence
says nothing about it. If a later phase wants to ship the DSA text, that needs its own answer.

**O-18 CLOSED -- ruled by the director, 2026-08-29.** Decision 2011/833/EU permits reuse.
Article 6(2)(a)'s source acknowledgement is the binding condition, and this register already
satisfies it for both documents by CELEX, ELI, OJ reference, date and sha256. The director's
grounds, recorded as given: two independent retrievals agreeing word for word on all three articles
is stronger evidence than the charter asks for.

> **The boundary travels with the clearance, and it is not decoration.** This closure covers
> **Commission documents**. Implementing Regulation (EU) 2024/2835 is a Commission act and
> Article 2(1)(a) fits it. **Regulation (EU) 2022/2065 -- the DSA, S-4.1 -- is a Parliament and
> Council act, and O-18's closure says nothing about it.** The charter cites the DSA repeatedly.
> The day someone adds its Official Journal text to this repository, they must not read this
> clearance as covering it. That is a separate question needing its own answer, and this sentence
> exists so nobody has to reconstruct that later.

**Local copies, and only one of them is tracked.**

| File | sha256, re-derived 2026-08-29 | Bytes | Pages | In git? |
|---|---|---|---|---|
| `OJ_L_202402835_EN_TXT.pdf` | `daff77f027fde1e0f92f89d70114327255456a3a4fa420fb6478da204a31337b` | 1,387,069 | 48 | **yes, since `5b4f97f`** |
| `OJ_L_2011_330_FULL_EN_TXT.pdf` | `5ac1d20087e45d96a821af65748a77b20be8f794210ad7a324b0a37404e34886` | 2,084,648 | 52 | **no, deliberately** |

**Why one is tracked and the other is not.** The first PDF cannot be kept out now. It has been in
git history since `5b4f97f`, and a private repository's history is what a public one would inherit.

The second has never been committed, so keeping it out still works, and it costs nothing.
`.gitignore` names it so it cannot be added by accident. Anyone can fetch it from the CELEX URL in
S-4.3 and check it against the digest above.

**This is what O-18 would have asked for on the first file, if the question had come up before
`5b4f97f`. We applied it to the one file where it still works.**

**What the checker does not cover here.** `check_paths` in `tools/check_claims.py` only looks at
paths under `src/`, `tests/`, `docs/` or `tools/` that end in `.py`, `.md`, `.toml` or `.txt`.
Neither PDF matches -- wrong folder, wrong extension.

So **no check confirms these two filenames exist**, and the second one is meant to be missing from a
fresh clone. Ruled into **D2.14**.

## S-5 — Security engineering

| ID | Control | Source | Pin | Re-check |
|---|---|---|---|---|
| S-5.1 | Symmetric encryption at rest — **Fernet, chunked. Ruled R-5 / D-9.** | `cryptography` (PyCA), `Fernet` recipe | **50.0.1**, released **2026-08-25**; `Apache-2.0 OR BSD-3-Clause`; docs pinned at `https://cryptography.io/en/50.0.1/fernet/` | **2026-11-28** |
| S-5.2 | Build provenance attestation | **SLSA v1.1** specification, `https://slsa.dev/spec/v1.1/levels` | fetched **2026-08-28**, HTTP 200 | **2027-02-28** |
| S-5.2a | Provenance in CI | `actions/attest-build-provenance` | **v4.2.2**, released **2026-08-06** | **2026-11-28** |
| S-5.2b | Supply-chain posture | OpenSSF `ossf/scorecard` | **v5.5.0**, released **2026-04-23** | **2026-11-28** |
| S-5.3 | Hash chain and all digests | **SHA-256**, NIST **FIPS 180-4** (Secure Hash Standard) | `https://csrc.nist.gov/pubs/fips/180-4/upd1/final`, fetched **2026-08-28**, HTTP 200 | never — fixed publication |

| S-5.4 | CI actions, SHA-pinned per charter 5.1 | `actions/checkout` **v5.0.0** (`08c6903cd8c0fde910a37f88322edcfb5dd907a8`); `actions/setup-python` **v5.6.0** (`a26af69be951a213d495a4c3e4e4022e16d87065`) | Both **target Node 20**, which GitHub is deprecating and currently force-runs on Node 24. 28 warnings in run `33204075014`. **TW-4 / O-19.** | **every phase close** (TW-4) |

*(S-5.4 sits in this table because a pinned action is a supply-chain control. The pins are read out
of `.github/workflows/gate.yml` by `tools/check_tripwires.py` rather than copied into it, so the
tripwire and the artifact cannot drift apart.)*

**S-5.1 ruled: Fernet**, on soak time, cross-project consistency with finding-bridge, and the
availability of AES-GCM AAD binding if ever needed. **Cobblestone-128 considered and rejected** — it
exists (official changelog, `50.0.0 - 2026-07-31`) but is four weeks old, and a tool about
auditability anchors on reviewed, aged primitives. Full reasoning in `docs/DECISIONS.md` D-9.

**S-5.1 recorded facts from the official documentation:** Fernet uses
*"AES in CBC mode with a 128-bit key for encryption, using PKCS7 padding"*, *"HMAC using SHA256 for
authentication"*, and IVs from `os.urandom()`. Stated limitation: *"Fernet is ideal for encrypting
data that easily fits in memory."*

## S-6 — Toolchain (all current as of 2026-08-28)

Per the director's standing direction: everything aligned to the latest.

| Component | Pinned version | Released | Note |
|---|---|---|---|
| Python (development line) | **3.14.7** | 3.14 line from 2025-10-07 | EOL 2030-10-31; this machine runs 3.14.0 |
| Python (floor) | **3.12** | 2023-10-02 | EOL 2028-10-31. Also the hard floor: `numpy` and `scipy` both require ≥ 3.12. Ruling **R-6**. |
| `cryptography` | **50.0.1** | 2026-08-25 | |
| `ruff` | **0.16.5** | 2026-08-27 | run **both** `ruff check` and `ruff format --check` — one green says nothing about the other |
| `mypy` | **2.3.1** | 2026-08-15 | strict mode |
| `pytest` | **9.1.1** | 2026-06-19 | |
| `hypothesis` | **6.165.10** | 2026-08-16 | |
| `numpy` | **2.5.2** | 2026-08-09 | requires Python ≥ 3.12 |
| `scipy` | **1.18.1** | 2026-08-21 | requires Python ≥ 3.12 |
| `click` | **8.5.0** | 2026-08-26 | CLI candidate |
| `typer` | **0.27.2** | 2026-08-28 | CLI candidate — released the day of this check |
| `pyyaml` | **6.0.3** | 2025-09-25 | plan file parsing |

**Re-check: 2026-09-28**, and again at every phase close. Versions move weekly; four of the twelve
above were released in the seven days before this check.

**Python 3.10 reaches end of life on 2026-10-31** — inside this project's expected lifetime. Do not
support it.

## S-7 — Datasets

| ID | Dataset | Licence | Pin | Re-check |
|---|---|---|---|---|
| S-7.1 | `google/civil_comments` | **CC0 1.0** | 1,804,874 / 97,320 / 97,320 = **1,999,514 rows**; card last modified 2024-01-25 | **2027-08-28** |
| S-7.2 | `google/jigsaw_unintended_bias` (alternative) | CC0 1.0 | card last modified 2024-01-18 | — |
| S-7.3 | `google/jigsaw_toxicity_pred` (alternative) | CC0 1.0 | card last modified 2024-01-18 | — |

**Licence text, verbatim:** *"This dataset is released under CC0, as is the underlying comment
text."*

**Label structure, and it constrains the flagship demo.** All seven label fields — `toxicity`,
`severe_toxicity`, `obscene`, `threat`, `insult`, `identity_attack`, `sexual_explicit` — are
**`float32`**: the fraction of human annotators who applied that label. **There is no binary ground
truth.**

Per ruling **R-7 / D-11**: the threshold is **pre-registered in the plan and hashed before any data
is touched**; the truth is then knowable **by census** at that threshold; and the coverage demo runs
at **multiple pre-registered thresholds as a sensitivity curve**. The float labels are an asset, not
a caveat.

Citation: Borkan, Dixon, Sorensen, Thain, Vasserman (2019), arXiv 1903.04561.

---

## S-8 — Retrieval procedures

**Why this section exists.** C-22. The register pinned *what* to fetch -- a URL, a version, a
digest. It never pinned *how* to fetch it. The how broke.

A pinned URL is worth nothing if the call that fetches it returns 400. Rule 3 says a pin nobody
re-checks quietly expires, but rule 3 had only ever been applied to sources. So the one entry every
other entry depends on was the one with no re-check date.

**Ruled by the director, 2026-08-29: a procedure is a pinned thing too, and it gets its own
re-check date.** D-27.

| ID | Procedure | Exact call | Last measured | Re-check |
|---|---|---|---|---|
| S-8.1 | Fetch an EU legal act as readable text | `curl -H "Accept: application/xhtml+xml" -H "Accept-Language: eng" http://publications.europa.eu/resource/celex/<CELEX>` | **2026-08-29**: HTTP 200, 48,730 bytes on `32011D0833`; HTTP 200, 721,977 bytes on `32024R2835` | **2026-09-29** |
| S-8.2 | Probe whether a CELEX work exists at all | the same URL, **no** `Accept` header | **2026-08-29**: HTTP 200, `application/rdf+xml`, 339,544 bytes. This is the form `tools/check_tripwires.py` TW-3 uses, **deliberately**: it needs existence, not content | **2026-09-29** |
| S-8.3 | `eur-lex.europa.eu` directly | any scripted fetch | **2026-08-29**: **HTTP 202, 0 bytes**, on the legal notice and on the CELEX record for `32011D0833`. Unusable. Measured twice, by two instruments | **2026-11-29** |

**The standing rule.** It has two incidents behind it now, not one: the reviewer's three empty
EUR-Lex fetches, and the expired header in C-22.

> **"I could not read it" is a result to report, not a reason to work from memory.**

If a source cannot be fetched, say so. Say what was tried and what came back. The director decides
what happens next. Never fill it in from memory, and never quietly drop it.

**What this section cannot do.** It records that a call worked on one date. It cannot tell you the
day it stops working. Only running it can do that. The re-check date is the instruction to run it.
C-22 is what happens when nobody does.

---

## S-X — Context sources (never a method source)

| ID | Source | Why it is here | Why it cannot be a method source |
|---|---|---|---|
| S-X.1 | Liu, Y., *Estimating the prevalence of rare events — theory and practice*, The Unofficial Google Data Science Blog, **2019-08-27** | Evidence of what a Google author reports YouTube does. Recommends the **stratified Wilson** interval; reports that **Jeffreys over-covers** for rare events. | Self-declared unofficial. Hard Rule 3 forbids sourcing a method from a tutorial. The method anchor is **S-1.1**. |

*Domain checked 2026-08-28 after the director raised it: authoritative NS `ns-cloud-d1.googledomains.com`,
A records in Google's Blogger block, `www` CNAME `ghs.google.com`, TLS from Google Trust Services.
Genuine Google-hosted blog, not a lookalike. Still unofficial.*

---

## Carried obligations from Phase 0

Tracked by name until discharged. Each is owned by a named phase.

| # | Obligation | Owner | Status |
|---|---|---|---|
| O-1 | Pin S-5.2 (OpenSSF/SLSA) and S-5.3 (SHA-256 / FIPS 180-4) to exact documents | Phase 1 | **discharged 2026-08-28** — S-5.2, S-5.2a, S-5.2b, S-5.3 above, each fetched live |
| O-2 | Build the tripwire check script (TW-1, TW-2, TW-3 are all scriptable) | Phase 1 | **discharged 2026-08-28** — `tools/check_tripwires.py`, run live, all three not fired |
| O-3 | Record R version, `survey` version and exact call alongside every fixture | Phase 2 | open |
| O-4 | Cross-check `lean` estimators against `svy` **as well as** R `survey`, in a separate optional environment so the runtime tree stays network-free | Phase 2 | open |
| O-5 | Re-derive the ts-sentry "1,230 tests" and finding-bridge "739 prompts" figures from those repositories before they appear in any README | Phase 3 | open |
| O-6 | Confirm whether a ROOST `awesome-safety-tools` PR needs a new Measurement category | Phase 3 | open |
| O-7 | Build a checker that searches for restated claims across files, per rule 14 | Phase 1 | **discharged 2026-08-28** — `tools/check_claims.py`, five checks, selftest proves each can fail |
| O-8 | Rogan–Gladen has no library witness — validate against the worked results in Lang & Reiczigel (2014) | Phase 2 | open |
| O-9 | Implement and test Fernet chunking above the in-memory limit; assert chunk-boundary behaviour | Phase 1 | **discharged 2026-08-28** — `test_chunking_is_exact_at_the_boundary` and the F-2 pair |
| O-10 | README credits `svy` as the estimator layer; assert by overclaim scanner | Phase 3 | open |
| O-19 | **Re-pin the CI actions before GitHub drops Node 20.** Both are SHA-pinned two major versions back (S-5.4) and both target Node 20. When it is dropped, the failure is a **red X on every job with nothing wrong in this repository**. Watched by **TW-4**, which **FIRED on its first run**, 2026-08-29 | Phase 3 | open |

## Re-check log

| Date | Who | What was re-checked | Result |
|---|---|---|---|
| 2026-08-28 | Claude (builder), Phase 0 | All of S-1 to S-7 established from primary sources | Baseline set |
| 2026-08-29 | Claude (builder), Phase 1 to 2 boundary | **The retrieval procedure itself**, by execution | **Stale.** The one-header call returns HTTP 400 on `32011D0833` and on `32024R2835`. `Accept-Language: eng` added. C-22 |
| 2026-08-29 | Claude (builder), Phase 1 to 2 boundary | EUR-Lex reachability: legal notice, and CELEX `32011D0833` | Unchanged. HTTP 202, 0 bytes, both |
| 2026-08-29 | Claude (builder), Phase 1 to 2 boundary | **S-4.3 added.** Decision 2011/833/EU, quoted from the OJ PDF and from the Publications Office XHTML | The two agree word for word on Articles 2, 4 and 6 |
| 2026-08-29 | Claude (builder), Phase 1 to 2 boundary | S-4.2's digest and page count, re-derived from the file | `daff77f0...31337b`, 48 pages. Both match what was recorded |
| 2026-08-29 | **Director's ruling** | **O-18 closed**, with the Parliament-and-Council boundary written into S-4.3 | Closed on the evidence above |
| 2026-08-29 | Claude (builder), first `--check` of TW-4 | **S-5.4's actions against their latest releases** | **TW-4 FIRED.** `checkout` v5.0.0 vs latest **v7.0.1**; `setup-python` v5.6.0 vs latest **v7.0.0**. Both two majors back. O-19 |
