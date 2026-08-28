# Prior art

**Status: RATIFIED — 28 August 2026.**
**Compiled:** 28 August 2026. Every entry checked against a primary source on that date.
**Evidence:** `docs/PHASE-0-VERIFICATION.md`. Pins: `docs/STANDARDS.md`.

This register exists to answer one question honestly: **has someone already built this?**

The answer is no, but the honest answer is more interesting than that. The statistics are solved,
twice over, in libraries better than anything we will write. The production systems exist at three
large platforms and are closed. What does not exist anywhere is the governance layer: sealing,
pre-registration, a tamper-evident record, and a tool that refuses to print a number it cannot
defend.

---

## 1. Survey statistics libraries — solved, and we should not compete

### R `survey`

| | |
|---|---|
| Author / maintainer | Thomas Lumley (`t.lumley@auckland.ac.nz`) |
| First CRAN release | **0.9-1, 23 January 2003** |
| Current | **4.5, published 24 February 2026** |
| Releases | 112 |
| Licence | GPL-2 \| GPL-3 |
| URL | `http://r-survey.r-forge.r-project.org/survey/` |

The reference implementation for design-based survey estimation, maintained continuously for
twenty-three years. **Our role: validate against it. Never compete with it.** Estimator outputs are
cross-checked to ≥ 4 significant digits against `survey` 4.5 fixtures.

*Licence note (inference, not legal advice):* committing numeric output produced by running
`survey` is not distributing `survey` and does not make this project a derivative work. No `survey`
source is copied into this repository. Recorded so the reasoning is visible rather than assumed.

### Python `svy`

| | |
|---|---|
| Publisher | Samplics LLC |
| Current | **0.25.0, uploaded 26 August 2026** |
| Releases | 48 |
| Licence | MIT |
| Source | `github.com/samplics-org/svy` (MIT, 20★, last push 2026-08-26) |
| Docs | `https://svylab.com/docs/svy` |
| Requires | Python ≥ 3.11; `httpx, msgspec, numpy, polars, scipy, svy-io, svy-rs` |

**This is the most important correction Phase 0 made.** The vision recorded that svy's installable
code "was not yet publicly downloadable." It is downloadable. It installs. It was verified by
running `pip install svy==0.25.0` in a clean virtual environment on 2026-08-28.

And it overlaps our Phase 2 plan substantially. Read from the 0.25.0 source:

**Present in svy:** SRS selection (`selection/srs.py`), PPS, multistage, proportional allocation,
**Neyman allocation** (`_neyman_allocation`, documented as `n_h proportional to N_h * SD_h`, with
named refusals), **Wilson intervals**, Clopper-Pearson, Korn-Graubard, logit intervals, Taylor
linearization, replicate weights, post-stratification, raking, calibration, trimming, sample size
and power.

**Absent from svy:** Jeffreys interval (0 occurrences). Rogan–Gladen / misclassification correction
(0 occurrences). Sealing, encryption, hash-chained ledger, tamper-evidence, audit trail
(0 occurrences of `ledger`, `fernet`, `encrypt`, `tamper`).

**What this means for positioning.** We are not the Python survey-statistics library. **svy is, and
the README credits it as the estimator layer.** prevalence-kit claims the Trust & Safety governance,
label-quality and audit layer only: pre-registration, sealed content, a chain that can say no, and a
report an auditor can check. *(Ruling R-1, D-4. Asserted by the overclaim scanner — obligation O-10.)*

**Why we still write `lean` estimators.** `svy` has a hard runtime dependency on `httpx`. Hard
Rule 1 of this project is zero network calls at runtime, proven by a test that fails if any network
capability appears. We cannot make that guarantee while shipping an HTTP client. That is the reason.
It is architectural and checkable. It is not "svy is unavailable."

### `samplics` (predecessor by the same organisation)

| | |
|---|---|
| Current | 0.6.0, 10 March 2026 |
| First release | 0.0.2, 19 January 2020 |
| Releases | 118 |
| Requires | Python ≥ 3.10, < 3.15 |

Predecessor to `svy`. Same problem space. Noted so the register is complete — the vision did not
mention it.

---

## 2. Platform production systems — all closed

### Pinterest — the nearest full system

> Dobi, A., Manickavasagam, A., Thompson, B., Yang, X., Farooq, F.
> *Measuring the Prevalence of Policy-Violating Content with ML-Assisted Sampling and LLM Labeling.*
> arXiv **2602.18518** — v1 **19 February 2026**, **v2 17 August 2026**. cs.LG, stat.ME, stat.ML.
> All authors affiliated with **Pinterest**.

**Cite it as a preprint.** Its header targets *"The 33rd ACM SIGKDD Conference ... August 2027, San
Jose"*, and its DOI field is the unfilled ACM placeholder `XXXXXXX.XXXXXXX`. arXiv carries no
`journal_ref`. It is **not** "KDD '26" — that was a defect in the vision draft.

**Their design:** daily probability samples from the impression stream, ML-assisted weights to
concentrate label budget on high-exposure and high-risk content while preserving unbiasedness,
Hansen–Hurwitz ratio estimation (PPS with replacement), post-stratified drill-downs from one global
sample, effective-sample-size diagnostics, and label-error bias correction. Labeling is done by a
**multimodal LLM** governed by policy prompts and gold-set validation.

**No code released.** Verified three ways: no GitHub URL anywhere in the paper; the `pinterest` org's
complete 99-repo public list has nothing relevant; global GitHub search for the system returns zero
results. A negative result proves it is not where a reader would look, not that it exists nowhere.

**How we differ, and it is the whole point:** their evidence path runs through an LLM. Ours is
forbidden to. Their system is closed; ours is the open, auditable, human-label-first version.

*Useful corroboration:* their Related Work cites *"Meta (Facebook) released an open-source
implementation (ml_sampler) ... (Beecher et al., 2017)"* — an independent primary confirmation of
the ancestor below.

### Meta — Community Standards Enforcement Report

Meta Transparency Center, *Prevalence*. Prevalence is *"the estimated percentage of those views that
were of violating content."* Method: review *"samples of views ... then we label the samples as
violating or not violating according to our policies."* For some violation types *"we use
**stratified sampling**, which increases the sample rate if the context indicates the content view is
more likely to contain a violation."* Reported as a range reflecting *"a 95% confidence window."*
Stated limitation: *"the people who apply labels to our samples sometimes make mistakes."*
Coverage gap stated: excludes private conversations on Messenger and Instagram Direct.

**No code released.**

### YouTube — Violative View Rate

Google Transparency Report, YouTube Community Guidelines enforcement. VVR is the percentage of views
of videos that violate Community Guidelines, estimated from a sample of viewed videos sent to human
reviewers, published quarterly with a 95% confidence interval.

Published caveat, verbatim, and we adopt it as our own honest limit:

> *"The confidence intervals do not take into account rater quality, which may impact our
> measurements."*

**No code released.**

### Barnett's assessment of VVR — our validation target

> Barnett, A. *YouTube's Violative View Rate Methodology: A Statistical Assessment.*
> Massachusetts Institute of Technology, **September 2021**. Published via Analysis Group.

**Provenance caveat, in the document's own words:** *"This evaluation was commissioned and funded by
Google. The conclusions and opinions expressed are exclusively those of the author."* It is an
expert review, not independent peer review. That must be stated wherever we cite it.

**Why it matters to us.** It is the only public document that gives real numbers for a real platform
prevalence design, in enough detail to reproduce. VVR uses **five strata** — four score-based plus
one for unscored views — with risk-weighted allocation. Table 2A gives a hypothetical population;
Table 2B gives the allocation of n = 4,000 across the strata.

**Reproduced independently during Phase 0** (`docs/PHASE-0-VERIFICATION.md` §C6): Neyman allocation
with `S_h = √(p_h(1−p_h))` recovers all five of Barnett's allocations exactly
(2098 / 828 / 584 / 256 / 234), the population VVR to 0.2000% against a published 0.20%, and the
expected standard deviation to 0.0539 pp against a published 0.054 pp.

Barnett's own conclusion on the design: five strata are sufficient — moving to eight strata reduced
the expected standard deviation by only 4%.

### Meta `ml_sampler` — the only open ancestor, dead

| | |
|---|---|
| Repository | **`facebookarchive/ml_sampler`** (note: `facebook/ml_sampler` is 404) |
| Description | "Model assisted random sampling." |
| Created | 2016-12-27 |
| Commits | 20 — first **2017-01-25**, last **2020-08-06** |
| By year | 2017: 12, 2018: 2, 2019: 1, 2020: 5 |
| Archived | yes (date not publicly recorded) |
| Licence | `NOASSERTION` — GitHub could not detect a standard licence |
| Stars / forks | 119 / 22 |

Model-assisted importance sampling for rare-event estimation. **Archived and unmaintained for six
years.** Relevant to the NEXT-queue importance-sampling item, not to v1.0.

The licence being undetectable is worth noting before anyone reuses code from it.

---

## 3. The open-source Trust & Safety ecosystem

### ROOST — Robust Open Online Safety Tools

| | |
|---|---|
| Launched | **10 February 2025**, at the AI Action Summit, Paris |
| Funding | **"more than $27 million ... for its first four years"** — official launch release, 10 Feb 2025. **A second official source conflicts — see below.** |
| Backers | Eric Schmidt, Discord, OpenAI, Google, Roblox, Knight Foundation, AI Collaborative, Patrick J. McGovern Foundation, Project Liberty Institute |
| GitHub | `roostorg`, 10 public repos |

**Funding: two official sources conflict. Both recorded. Neither preferred.** *(Ruling R-3, D-7.)*

| Source | Date | Verbatim |
|---|---|---|
| Launch press release *(primary citation)* | **10 February 2025** | *"To date, ROOST has raised more than **$27 million** for its first four years of operations from a range of leading philanthropies and top technology companies."* |
| ROOST blog, *First 100 Days: Building & Planning* *(footnote)* | **4 June 2025** | *"Thanks to an initial **$28.5 million** in funding **and in-kind contributions** from founding partners"* |

The two differ in figure, in wording (funding, versus funding and in-kind contributions), and in
date. **We record both and stop there.** Any reconciliation would be our inference, not either
source's statement. The vision's "$28M+" matches neither and is withdrawn.

Stated mission, verbatim: tools *"to detect, review, and report child sexual abuse material (CSAM);
leverage large language models (LLMs) to power safety infrastructure; and make core safety
technologies more accessible and more user friendly."*

Repositories at 2026-08-28: `osprey` (rules engine, 475★), `coop` (moderation dashboard, 89★),
`awesome-safety-tools` (263★), `model-community` (132★), plus `community`, `stats`, `mirror`,
`playground`, `coop-integration-example`, `.github`.

**Nothing in measurement.** `awesome-safety-tools` has fourteen categories — Hash Matching,
Classification, AI for Safety, Privacy Protection, Core Infrastructure, Redteaming Tools,
Clustering, Rules Engines, Review, Investigation, Datasets, Red Teaming Datasets, Decentralized
Platforms, User Safety Tools — and **zero occurrences of "prevalence"**.

**Consequence for Phase 3.** A pull request would need a **new category** (Measurement) or accept a
poor fit under an existing one. Plan for the new-category conversation; do not assume the PR lands
by simply appending a line.

---

## 4. Statistical methods

### Binomial interval estimation — the method anchor

> Brown, L.D., Cai, T.T., DasGupta, A. (2001). *Interval Estimation for a Binomial Proportion.*
> **Statistical Science** 16(2). DOI `10.1214/ss/1009213286`

Peer-reviewed, DOI-registered, and the canonical comparison of Wald, Wilson, Agresti–Coull and
Jeffreys. **This is the method source for our intervals.** It replaces the blog the vision draft
anchored on.

**Shipped: Wilson (primary) and Clopper-Pearson (conservative second). Jeffreys is dropped.**
*(Ruling R-4, D-8.)* Clopper-Pearson is exact, never under-covers, and — unlike Jeffreys — is
implemented in **both** R `survey` and `svy`, so the dual cross-check of D-3 applies to it.

### Stratified sampling and Neyman allocation

> Neyman, J. (1934). *On the Two Different Aspects of the Representative Method: the Method of
> Stratified Sampling and the Method of Purposive Selection.* Reprinted, Springer Series in
> Statistics, DOI `10.1007/978-1-4612-4380-9_12`

> Cochran, W.G. *Sampling Techniques.* Wiley. First published 1953; pin the **3rd edition, 1977**,
> ISBN `0-471-16240-X`.

### Misclassification correction

> Rogan, W.J. & Gladen, B. (1978). *Estimating Prevalence from the Results of a Screening Test.*
> **American Journal of Epidemiology.** DOI `10.1093/oxfordjournals.aje.a112510`

> Lang, Z. & Reiczigel, J. (2014). *Confidence limits for prevalence of disease adjusted for
> estimated sensitivity and specificity.* **Preventive Veterinary Medicine.**
> DOI `10.1016/j.prevetmed.2013.09.015`

Also worth carrying as a Phase 2 cross-check:

> Reiczigel, J., Földi, J., Ózsvári, L. (2010). *Exact confidence limits for prevalence of a disease
> with an imperfect diagnostic test.* **Epidemiology and Infection.** DOI `10.1017/s0950268810000385`

### Context, not a method source

> Liu, Y. *Estimating the prevalence of rare events — theory and practice.* The Unofficial Google
> Data Science Blog, **27 August 2019**.

**Demoted deliberately.** The vision anchored the interval choice here. It cannot: the blog is
self-declared unofficial, and Hard Rule 3 forbids sourcing a method from a tutorial.

It is also worth recording *what it actually says*, because the vision misread it. It evaluates
Wald, Jeffreys, Agresti–Coull and Wilson, concludes *"the stratified Wilson interval works well for
our video sampling problem"*, and reports that **Jeffreys over-covers for rare events** by shrinking
toward 0.5. It does not endorse Jeffreys.

Its value here is as evidence of what a Google author reports YouTube does. That is all it is cited
for.

*(For the record, since the question was raised: the domain was checked and is genuine Google
infrastructure — NS `ns-cloud-d1.googledomains.com`, A records in Google's Blogger block, `www`
CNAME `ghs.google.com`, TLS from Google Trust Services. It is a real blog, not a lookalike. It is
still unofficial.)*

---

## 5. Regulation — context, not a driver

> **Regulation (EU) 2022/2065** (Digital Services Act), 19 October 2022. OJ L 277, 27.10.2022, p. 1.
> ELI `http://data.europa.eu/eli/reg/2022/2065/oj`

> **Commission Implementing Regulation (EU) 2024/2835** of 4 November 2024, laying down templates
> concerning the transparency reporting obligations of providers of intermediary services and of
> providers of online platforms under Regulation (EU) 2022/2065. OJ L series 2024/2835, 5.11.2024.
> Adopted under Articles 15(3) and 24(6). In force, unamended as of 2026-08-28.

**The key fact, and it is the one the vision got wrong.** The word "prevalence" appears **zero
times** in either text. No EU regulation requires a platform to report prevalence.

What 2024/2835 requires under Annex I §1.6 is **accuracy, precision and recall of automated content
moderation**, with qualitative guidance naming *"sensitivity, recall, hit rate, or true positive
rate; specificity, selectivity, or true negative rate; precision or positive predictive value..."*

**Those are the Rogan–Gladen inputs.** So the honest connection is: regulation obliges platforms to
publish label-quality figures, and prevalence-kit shows what those figures do to a prevalence
estimate. Not: regulation requires this tool.

Timeline, for the record: templates apply from 1 July 2025; the Commission's announcement says
*"the first harmonised reports due in the beginning of 2026"*; recital (9) says *"The first full
harmonised reporting cycle covers 1 January 2026 until 31 December 2026"*, with reports due within
two months of the period's end.

---

## 6. Datasets for the coverage demonstration

### Civil Comments — selected

| | |
|---|---|
| Dataset | `google/civil_comments` |
| **Licence** | **CC0 1.0** — *"This dataset is released under CC0, as is the underlying comment text."* |
| Size | 1,804,874 train + 97,320 validation + 97,320 test = **1,999,514 rows** |
| Fields | `text`, plus `toxicity`, `severe_toxicity`, `obscene`, `threat`, `insult`, `identity_attack`, `sexual_explicit` — all **`float32`** |
| Origin | Civil Comments shut down in 2017 and released its public archive on figshare; Jigsaw added toxicity and identity labels |
| Citation | Borkan, Dixon, Sorensen, Thain, Vasserman (2019), *Nuanced Metrics for Measuring Unintended Bias with Real Data for Text Classification*, arXiv 1903.04561 |

**CC0 is the best available outcome.** No attribution obligation, no share-alike, no redistribution
restriction. Nothing blocks the demonstration.

**The critical detail the vision missed.** The labels are **continuous** — the fraction of human
annotators who applied each label — not booleans. There is no binary ground truth in the file. A
"true prevalence" exists only once a threshold is fixed. That threshold is our definitional choice,
and the demo must say so out loud. See ruling R-7.

Sibling datasets `google/jigsaw_toxicity_pred` and `google/jigsaw_unintended_bias` are also CC0 1.0
and are alternatives if needed.

---

## 7. The gap, stated at the width of the evidence

| Layer | Who has it | Open? |
|---|---|---|
| Survey estimation math | R `survey`, Python `svy` | **Yes, and better than ours will be** |
| Production prevalence system | Meta, YouTube, Pinterest | No — all three closed |
| Model-assisted rare-event sampling | `facebookarchive/ml_sampler` | Yes, but dead since 2020 |
| Open T&S tooling | ROOST | Yes — detection, review, enforcement only |
| **Pre-registered plan, sealed content, hash-chained record, refusal gates, auditable prevalence report** | **nobody** | **—** |

The contribution is the last row. Not the statistics.
