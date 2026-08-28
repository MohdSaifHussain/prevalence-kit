# Phase 0 — Source Verification Report

**Subject:** every factual claim in `prevalence-kit-VISION.md` (14,490 bytes, 225 lines, drafted 28 Aug 2026)
**Verification performed:** 28 August 2026, by Claude (builder), on the director's instruction
**Rule applied:** primary/official sources only. Nothing entered from memory or from tutorials.
**Status:** complete. Not ratified. The director rules on every DEFECT.

---

## How to read this

Each claim is quoted from the vision by line number, then marked:

- **VERIFIED** — a primary source says this, and the source is named with its date/version.
- **DEFECT** — the primary source says something different. What it actually says is quoted.
- **UNVERIFIED** — no primary source could be reached. Not the same as false.

Where a check was performed by running something, the command class and the output are stated,
because a claim confirmed by execution is worth more than one confirmed by reading.

**Retrieval note:** `eur-lex.europa.eu` is behind an AWS WAF bot challenge and returns HTTP 202
with an empty body to a scripted fetch. The regulation texts below were obtained instead from the
**EU Publications Office** content-negotiation endpoint
(`http://publications.europa.eu/resource/celex/<CELEX>`, `Accept: application/xhtml+xml`), which is
the same authority serving the Official Journal. The director independently downloaded the PDF of
2024/2835 from EUR-Lex during this session; **both copies agree verbatim on every sentence quoted
here**, which is the strongest form this record could take.

---

## A. Prior art and positioning

### A1 — Pinterest paper exists, Feb 2026, arXiv 2602.18518
> *Line 34–35:* "Pinterest published its full production prevalence pipeline in Feb 2026 (arXiv 2602.18518, KDD '26)"

**VERIFIED (identity, date, affiliation).** arXiv API, 28 Aug 2026:

| Field | Value |
|---|---|
| Title | *Measuring the Prevalence of Policy-Violating Content with ML-Assisted Sampling and LLM Labeling* |
| arXiv ID | 2602.18518 — **v1 published 2026-02-19**, **v2 updated 2026-08-17** |
| Authors | Attila Dobi, Aravindh Manickavasagam, Benjamin Thompson, Xiaohan Yang, Faisal Farooq |
| Affiliation | **Pinterest** (all five authors, `@pinterest.com`, per the paper's HTML render) |
| Categories | cs.LG (primary), stat.ME, stat.ML |
| Comment field | "8 pages" |

### A2 — "KDD '26"
> *Line 35:* "(arXiv 2602.18518, **KDD '26**)"

**DEFECT — wrong venue year, and acceptance is unproven.**

The paper's own header block reads: *"Conference: The 33rd ACM SIGKDD Conference on Knowledge
Discovery and Data Mining; **August 2027**; San Jose, CA, USA"* — and its DOI field is the unfilled
ACM template placeholder **`XXXXXXX.XXXXXXX`**. The arXiv record carries **no `journal_ref`** and
no DOI.

So two things are wrong. The target venue is KDD **2027** (the 33rd SIGKDD), not KDD 2026. And a
placeholder DOI with no journal reference is a paper formatted for a venue, not a paper accepted at
one. Citing it as "KDD '26" asserts a peer-review status that no source supports.

**Correct citation:** arXiv preprint 2602.18518v2 (2026-08-17), formatted for submission to KDD 2027.

### A3 — Pinterest released no code
> *Line 35–36:* "and released **no code**"

**VERIFIED, with the limit of a negative result stated.** Three checks:

1. The paper's full HTML render contains **zero** GitHub URLs and zero code-availability statement.
2. The `pinterest` GitHub organisation's complete public repo list (99 repos, fetched 28 Aug 2026)
   contains no prevalence, sampling, or measurement repository.
3. GitHub global repository search for `prevalence policy violating content` and for
   `ML-assisted sampling LLM labeling prevalence` returned **0 results** each.

A negative result cannot prove code exists nowhere. It can prove it is not where a reader would
look. That is the width of this claim, and the charter should state it that way.

### A4 — An LLM sits in Pinterest's labeling path
> *Line 36:* "It also puts an LLM inside the labeling path."

**VERIFIED.** The title says so, and the abstract says the system *"labels sampled items with a
multimodal LLM governed by policy prompts and gold-set validation."*

### A5 — Meta's ml_sampler: commit history 2017–2020, archived
> *Line 38–39:* "Meta's ml_sampler: commit history 2017–2020, archived 2021."

**VERIFIED on the commit range. DEFECT on the repository path. UNVERIFIED on the archive year.**

GitHub API, 28 Aug 2026. The repository is **`facebookarchive/ml_sampler`** — *not*
`facebook/ml_sampler`, which returns 404. Any citation must use the real path.

| Field | Value |
|---|---|
| Created | 2016-12-27 |
| Commits | 20 total; **first 2017-01-25 ("Initial commit"), last 2020-08-06** |
| Commits by year | 2017: 12, 2018: 2, 2019: 1, 2020: 5 |
| `archived` | `true` |
| License | `NOASSERTION` (GitHub could not detect a standard license) |
| Stars / forks | 119 / 22 |

"Commit history 2017–2020" is exactly right. **"Archived 2021" could not be verified** — the GitHub
API exposes no archive date, and a Wayback CDX query for the old `facebook/` path returned nothing
parseable. Recommend the charter say "archived (date not publicly recorded); last commit
2020-08-06", which is provable.

Corroboration from an unrelated primary source: the Pinterest paper's own Related Work cites
*"Meta (Facebook) released an open-source implementation (ml_sampler) ... (Beecher et al., 2017)."*

### A6 — R `survey` maintained since 2003
> *Line 31:* "R `survey` (maintained since 2003)"

**VERIFIED.** CRAN database, 28 Aug 2026:

| Field | Value |
|---|---|
| Earliest release | **0.9-1, 2003-01-23** |
| Current release | **4.5, published 2026-02-24** |
| Releases | 112 |
| Maintainer | Thomas Lumley `<t.lumley@auckland.ac.nz>` |
| Authors | Lumley [cre]; Peter Gao, Ben Schneider, Stas Kolenikov [aut] |
| License | GPL-2 \| GPL-3 |

### A7 — svy is MIT and active
> *Line 31–32:* "`svy` (MIT, active)"

**VERIFIED.** PyPI + GitHub, 28 Aug 2026. `svy` **0.25.0**, uploaded **2026-08-26** (two days before
this check). License MIT, © 2026 Samplics LLC. 48 releases. Source `samplics-org/svy`, MIT, last
push 2026-08-26. Requires Python ≥ 3.11.

### A8 — svy's installable code was not publicly downloadable
> *Line 168–169:* "the review found svy's installable code was not yet publicly downloadable — so v1.0 defaults to `lean` estimators"

**DEFECT — this is false as of 28 Aug 2026, and it is the load-bearing premise under TW-2.**

Verified by execution, not by reading. In a clean virtual environment on this machine:

```
python -m venv <scratch>/venv_svy
<scratch>/venv_svy/Scripts/python.exe -m pip install "svy==0.25.0"
  → Successfully installed ... svy-0.25.0 svy-io-0.3.0 svy-rs-0.15.0
<scratch>/venv_svy/Scripts/python.exe -c "import svy; print(svy.__version__)"
  → 0.25.0
```

PyPI serves both a wheel (`svy-0.25.0-py3-none-any.whl`, 1,513,972 bytes) and an sdist
(`svy-0.25.0.tar.gz`, 1,447,216 bytes). It installs and imports.

**And the overlap is larger than the vision assumes.** Reading the 0.25.0 source directly:

| prevalence-kit plan | svy 0.25.0 status |
|---|---|
| SRS sampling | **present** — `selection/srs.py` |
| Stratified + proportional allocation | **present** — `selection/allocation.py`, `_proportional_allocation` |
| **Neyman (optimal) allocation** | **present** — `_neyman_allocation`, documented as "n_h proportional to N_h * SD_h", with named refusals |
| Wilson interval for a proportion | **present** — `estimation/base.py`, canonical method `"wilson"` |
| Clopper-Pearson / Korn-Graubard / logit intervals | **present** |
| Design-based variance | **present** — Taylor linearization, replicate weights, post-stratification, calibration, raking |
| Sample size / power | **present** — `engine/size_and_power/` |
| **Jeffreys interval** | **absent** — 0 occurrences in the source |
| **Rogan–Gladen correction** | **absent** — 0 occurrences of `rogan`, `gladen`, `misclassification` |
| **Sealing / hash-chained ledger / encryption / audit trail** | **absent** — 0 occurrences of `ledger`, `fernet`, `encrypt`, `tamper`, `hash-chain` |

**The far better argument for `lean` estimators, and it is verifiable:** `svy` declares a hard
runtime dependency on **`httpx`** (`Requires: httpx, msgspec, numpy, polars, scipy, svy-io,
svy-rs`), which pulls in `httpcore`, `anyio` and `certifi`. A tool whose Hard Rule 1 is *"zero
network calls at runtime, proven by a test that fails if any network capability appears"* cannot
put a full HTTP client in its dependency tree without weakening its own headline guarantee. That is
a real architectural reason. "Not downloadable" was not.

**This forces a ruling (R-1).** See the rulings queue.

### A9 — ROOST ships detection and enforcement, nothing in measurement
> *Line 44–45:* "**ROOST** ... ships detection and enforcement tools. It has **nothing in measurement**."

**VERIFIED.** GitHub org `roostorg` ("Robust Open Online Safety Tools"), 10 public repos,
28 Aug 2026: `osprey` (rules engine, 475★), `coop` (moderation dashboard, 89★),
`awesome-safety-tools` (263★), `model-community` (132★), `community`, `stats`, `mirror`,
`playground`, `coop-integration-example`, `.github`.

`awesome-safety-tools/README.md` has 14 categories — Hash Matching, Classification, AI for Safety,
Privacy Protection, Core Infrastructure, Redteaming Tools, Clustering, Rules Engines, Review,
Investigation, Datasets, Red Teaming Datasets, Decentralized Platforms, User Safety Tools.
**No measurement, statistics, or prevalence category. Zero occurrences of "prevalence".**

The official launch release states ROOST's scope as *"tools to detect, review, and report child
sexual abuse material (CSAM); leverage large language models (LLMs) to power safety
infrastructure; and make core safety technologies more accessible."* Measurement is absent from the
stated mission, not merely absent from the repo list.

*Consequence for Phase 3:* a PR to `awesome-safety-tools` would have to propose a **new category**
or accept a poor fit under an existing one. Plan for that.

### A10 — ROOST funding "$28M+"
> *Line 44:* "ROOST (the major open-source T&S initiative, **$28M+ funding**)"

**DEFECT — the figure is not supported; the primary source says $27M.**

The official launch announcement (10 February 2025) states verbatim:

> *"To date, ROOST has raised more than **$27 million** for its first four years of operations from
> a range of leading philanthropies and top technology companies."*

Named backers: Eric Schmidt, Discord, OpenAI, Google, Roblox, John S. and James L. Knight
Foundation, AI Collaborative, Patrick J. McGovern Foundation, Project Liberty Institute.

No source was found for $28M. The gap is small; the principle is not. Under the project's own rule
7 — *claims at the exact width of the evidence* — the charter must say **"more than $27 million,
raised February 2025, for its first four years"** and cite the release. Rounding a funding figure
upward in a document whose whole selling point is verifiability is the exact failure the tool
exists to prevent.

---

## B. The regulatory claim

### B1 — Implementing Regulation (EU) 2024/2835 exists and is current
> *Line 40–41:* "EU DSA Implementing Regulation 2024/2835"

**VERIFIED.** EU Publications Office, CELEX `32024R2835`, and independently the director's own
EUR-Lex PDF (`OJ_L_202402835_EN_TXT.pdf`, 48 pages, sha256
`daff77f027fde1e0f92f89d70114327255456a3a4fa420fb6478da204a31337b`).

> COMMISSION IMPLEMENTING REGULATION (EU) 2024/2835 **of 4 November 2024** laying down templates
> concerning the transparency reporting obligations of providers of intermediary services and of
> providers of online platforms under Regulation (EU) 2022/2065

Published OJ L series, **5.11.2024**. Entry into force: twentieth day after publication
(= 25 November 2024). Adopted under Articles **15(3)** and **24(6)** of Regulation (EU) 2022/2065.

**Still current, no 2026 version.** The EUR-Lex metadata notice records
`RESOURCE_LEGAL_IN-FORCE = true` and `END-OF-VALIDITY = 9999-12-31`, carries no amendment,
corrigendum or repeal relationship, and **no consolidated version exists** — every probe for
`02024R2835-*` returns 404, and EUR-Lex only mints consolidated versions after an amendment.

### B2 — Articles 15 / 24 / 42
> *Line 132:* "Regulation (EU) 2022/2065 Arts. 15/24/42"

**VERIFIED.** Recital (1) of 2024/2835: *"reports that providers of intermediary services must
publish pursuant to Articles **15(1), 24(1) and 42(2)** of Regulation (EU) 2022/2065."*

### B3 — "First harmonized reports are due in early 2026"
> *Line 42:* "the first harmonized reports are due in early 2026"

**VERIFIED, and it needs one sentence of precision.**

The Commission's own announcement of 4 November 2024 states verbatim: *"Providers will have to
start collecting data according to the Implementing Regulation as of **1 July 2025**"* and *"with
the **first harmonised reports due in the beginning of 2026**."*

The regulation itself adds the detail that changes what a reader should conclude — recital (9):

> *"...shall follow the templates set out in Annex I to this Regulation as of 1 July 2025. **The
> first full harmonised reporting cycle covers 1 January 2026 until 31 December 2026.**"*

Reports are published *"at the latest by two months from the date of the conclusion of each
reporting period."* So the reports due in early 2026 cover the transitional period; the first
**full** harmonised cycle is calendar 2026 and lands in early **2027**.

**Both facts are true and they are not the same fact.** As of today (28 Aug 2026) the early-2026
milestone is in the past. The charter must not present it as forthcoming.

### B4 — "Requires harmonized transparency reports with accuracy indicators"
> *Line 41–42:* "requires harmonized transparency reports with accuracy indicators"

**VERIFIED as to the words. DEFECT as to what the reader will conclude.**

2024/2835 does require accuracy indicators — but they are indicators of **classifier** accuracy,
not of prevalence. Annex I §1.6 (*"Article 15(1)(b)(c)(e) and Article 42(2)(c). Use of automated
means for content moderation and indicators of accuracy"*) requires three numeric fields:

> *"Accuracy of the automated means – **Accuracy** ... – **Precision** ... – **Recall**"*, with
> *"Separate rows ... to report on the accuracy, precision and recall for automatically removed
> content per type of content moderation system."*

The qualitative field asks for *"sensitivity, recall, hit rate, or true positive rate; specificity,
selectivity, or true negative rate; precision or positive predictive value; negative predictive
value; miss rate or false negative rate; fall-out or false [positive rate]."*

### B5 — "The timing is regulatory, and it is now"
> *Line 40:* section heading claim

**DEFECT — the strongest overclaim in the vision, and the one most likely to be challenged in
public.**

**The word "prevalence" appears zero times in Implementing Regulation (EU) 2024/2835 (48 pages),
and zero times in Regulation (EU) 2022/2065, the DSA itself (415,117 characters of official text).**
Both counted mechanically over the full official texts.

The DSA does not require any platform to report prevalence. prevalence-kit computes a number no EU
regulation asks for. Positioning the tool as answering a regulatory mandate is not supportable, and
a regulator or a reviewer would find this in one search.

**There is a real seam, and it runs the other way.** What 2024/2835 *does* mandate — accuracy,
precision, recall, and in the qualitative field explicitly **sensitivity and specificity** — are
precisely the Se/Sp inputs the Rogan–Gladen correction consumes (§C3 below). So the honest framing
is: *the regulation obliges platforms to publish label-quality figures; prevalence-kit is the tool
that shows what those figures do to a prevalence estimate, and refuses when they make it
undefined.* That is a true, defensible, and more interesting claim than the one drafted.

**This forces a ruling (R-2).**

---

## C. Statistical methods

### C1 — Rare-event intervals: "Wilson / Jeffreys ... this matches Google's published practice"
> *Line 69–71:* "Rare-event-safe intervals only (Wilson / Jeffreys — never plain Wald for rare events; this matches Google's published practice)"
> *Line 128:* "per the published Google rare-events methodology (Unofficial Google Data Science, 2019)"

**DEFECT on two counts.**

**(a) The named source does not endorse Jeffreys for rare events — it criticises it.** The post is
*"Estimating the prevalence of rare events — theory and practice"*, by **Yi Liu**, **27 August
2019**, on the Unofficial Google Data Science Blog, and it is explicitly about YouTube's
violative-content sampling. It evaluates Wald, Jeffreys, Agresti–Coull and Wilson, and concludes:

> *"In our problem, the stratified Wilson interval works well for our video sampling problem."*

On Jeffreys it reports the opposite of an endorsement: Jeffreys **over-covers** for rare events by
shrinking toward 0.5, inflating the interval. Presenting "Wilson / Jeffreys" as a matched pair that
"matches Google's published practice" misrepresents the cited source.

**(b) The source is not an official source, and this project's own Hard Rule 3 forbids it.** The
blog is self-declared unofficial. Rule 3 says *"no method enters the code from memory or from a
tutorial."* A blog is a tutorial. Anchoring an estimator on it violates the project's spine on the
project's first technical page.

*The director raised this independently during the session and was right to.* For completeness, the
domain was checked and is **not** a phishing lookalike: authoritative NS `ns-cloud-d1.googledomains.com`
(SOA `dns-admin.google.com`), A records in Google's Blogger block `216.239.32.21/.34/.36/.38`,
`www` CNAME → `ghs.google.com`, TLS issued by Google Trust Services (CN=WR3). It is a genuine
Google-hosted blog written by Google data scientists. It is still unofficial.

**Correct anchor** — peer-reviewed, DOI-registered, and the canonical reference for exactly this
comparison, verified in the Crossref registry:

> Brown, L.D., Cai, T.T., DasGupta, A. (2001). *Interval Estimation for a Binomial Proportion.*
> **Statistical Science** 16(2). DOI `10.1214/ss/1009213286`

The blog is retained in PRIOR-ART.md as *context* — evidence of what a Google author reports
YouTube does — and never as a method source. **Ruling R-4.**

### C2 — Rogan–Gladen (1978)
> *Line 71–72:* "Optional Rogan–Gladen correction"

**VERIFIED.** Crossref, 28 Aug 2026:

> Rogan, W.J. & Gladen, B. (1978). *Estimating Prevalence from the Results of a Screening Test.*
> **American Journal of Epidemiology.** DOI `10.1093/oxfordjournals.aje.a112510`

### C3 — Lang & Reiczigel (2014) for CI propagation
> *Line 72–73:* "with CI propagation per Lang & Reiczigel (2014)"

**VERIFIED, title matches exactly.**

> Lang, Z. & Reiczigel, J. (2014). *Confidence limits for prevalence of disease adjusted for
> estimated sensitivity and specificity.* **Preventive Veterinary Medicine.**
> DOI `10.1016/j.prevetmed.2013.09.015`

Related, surfaced in the same search and worth carrying into Phase 2 as a cross-check:
Reiczigel, Földi & Ózsvári (2010), *Exact confidence limits for prevalence of a disease with an
imperfect diagnostic test*, **Epidemiology and Infection**, DOI `10.1017/s0950268810000385`.

### C4 — Refusal when Se + Sp ≤ 1 or apparent prevalence is zero
> *Line 73–75:* "When the correction is mathematically undefined (Se + Sp ≤ 1) or degenerate ... the tool refuses"

**VERIFIED as mathematics, from the Rogan–Gladen estimator itself.** The estimator is
`π̂ = (p̂ + Sp − 1) / (Se + Sp − 1)`. The denominator is zero at `Se + Sp = 1` and the estimator
inverts sign below it. Refusing is correct. This is a definitional consequence, not a citation —
marked as such so no reviewer mistakes it for a claim about a source.

### C5 — Cochran, *Sampling Techniques*
> *Line 127:* "Cochran, *Sampling Techniques*"

**VERIFIED as a real work; edition must be pinned.** William G. Cochran, *Sampling Techniques*,
Wiley; first published 1953; the standard citation is the **3rd edition, 1977, ISBN 0-471-16240-X**
(Open Library records `047116240X` under Wiley). The Neyman-allocation result predates it:
Neyman, J. (1934), *On the Two Different Aspects of the Representative Method*, reprinted in
Springer Series in Statistics, DOI `10.1007/978-1-4612-4380-9_12`.

### C6 — ts-sentry reproduced Barnett's VVR Table 2B "to the digit"
> *Line 127:* "ts-sentry STEP-07 record (validated against Barnett's published VVR Table 2B to the digit)"
> *Line 140–141:* "Port the ts-sentry stratified/Neyman code that already reproduced YouTube's published VVR assessment figures to the digit."

**VERIFIED — and independently re-derived here, not taken on trust.**

Source located in the director's own read-only tree at
`C:\Users\mohds\ts-sentry\docs\barnett-vvr-assessment.txt` (30,285 bytes):

> *YouTube's Violative View Rate Methodology: A Statistical Assessment.* **Arnold Barnett**,
> Massachusetts Institute of Technology, **September 2021**.
> *"This evaluation was commissioned and funded by Google. The conclusions and opinions expressed
> are exclusively those of the author."*

Barnett's Table 2A (a hypothetical population) and Table 2B (YouTube's allocation of n = 4,000)
were transcribed, and Table 2B was recomputed from Table 2A using Neyman allocation
`n_h ∝ W_h · √(p_h(1−p_h))`:

| Stratum | W_h | p_h | Recomputed n_h | Barnett Table 2B | Match |
|---|---|---|---|---|---|
| Lowest Risk | 80% | 0.05% | 2098.50 → **2098** | 2,098 | OK |
| Low Risk | 10% | 0.50% | 827.63 → **828** | 828 | OK |
| Middle Risk | 5% | 1.00% | 583.75 → **584** | 584 | OK |
| High Risk | 1% | 5.00% | 255.73 → **256** | 256 | OK |
| No score available | 4% | 0.25% | 234.38 → **234** | 234 | OK |
| **Total** | 100% | | **4,000** | 4,000 | OK |

Population VVR: computed **0.2000%**, published 0.20%.
Expected SD of the estimate: computed **0.0539 pp**, published **0.054 pp**.

All five allocations reproduce exactly. One cosmetic difference: 234/4000 = 5.85%, which Barnett
prints as 5.9% (half-up) and the check printed as 5.8% (half-even). The counts are identical; only
the displayed rounding differs. Noted so nobody later mistakes it for a discrepancy.

**What this pins down for Phase 2:** the estimator to port is Neyman allocation with
`S_h = √(p_h(1−p_h))`, and the variance is the with-replacement stratified form
`Var = Σ W_h² p_h(1−p_h)/n_h` **with no finite-population correction** — that is what reproduces
0.054 pp. This is now a specification, not an intention.

**Provenance caveat that must be carried:** Barnett's assessment was *commissioned and funded by
Google*. It is an expert review, not independent peer review. PRIOR-ART.md says so.

### C7 — YouTube's published interval caveat
> *Line 212:* "Interval guarantees are sampling-only, matching the caveat YouTube publishes for VVR."

**VERIFIED, verbatim.** Google Transparency Report Help Centre, YouTube Community Guidelines
enforcement FAQs:

> *"The VVR metric is reported with a 95% confidence interval. This means that if we performed the
> measurement many times for the same time period, we would expect the true metric to lie within
> the interval 95% of the time."*
> *"**The confidence intervals do not take into account rater quality, which may impact our
> measurements.**"*

The vision's honest limit is an exact match to a published platform caveat. Keep it, and cite it.

### C8 — Meta CSER methodology
> *Line 131:* "Meta CSER methodology posts"

**VERIFIED, and it strengthens the design.** Meta Transparency Center, *Prevalence*: prevalence is
*"the estimated percentage of those views that were of violating content"*, measured by reviewing
*"samples of views ... then we label the samples as violating or not violating"*; for some violation
types *"we use **stratified sampling**, which increases the sample rate if the context indicates the
content view is more likely to contain a violation"*; reported as a range reflecting *"a 95%
confidence window"*; with the stated limitation that *"the people who apply labels to our samples
sometimes make mistakes."*

Meta and YouTube independently use the same design family — stratified, risk-weighted, human-labeled,
95% CI, with a published rater-quality caveat. The vision's core design matches published industry
practice at two platforms. That is a stronger claim than the one the vision makes, and it is
sourced.

---

## D. Validation plan

### D1 — Jigsaw / Civil Comments licence
> *Line 143:* "candidate: Jigsaw Civil Comments family — license verified in Phase 0"

**VERIFIED — CC0 1.0.** Dataset card for `google/civil_comments`:

> *"This data set is an exact replica of the data released for the Jigsaw Unintended Bias in
> Toxicity Classification Kaggle challenge. **This dataset is released under CC0, as is the
> underlying comment text.**"*
> *"### Licensing Information — This dataset is released under [CC0 1.0]."*

Sibling datasets `google/jigsaw_toxicity_pred` and `google/jigsaw_unintended_bias` also carry
`cc0-1.0`. Size: **1,804,874 train / 97,320 validation / 97,320 test = 1,999,514 rows**.
Origin: Civil Comments shut down in 2017 and released its public archive on figshare; Jigsaw added
toxicity and identity labels. Citation: Borkan, Dixon, Sorensen, Thain, Vasserman (2019),
arXiv 1903.04561.

**CC0 is the most permissive outcome available.** No attribution obligation, no share-alike, no
redistribution restriction. Nothing blocks the flagship demo.

### D2 — "Because every item is labeled, the TRUE prevalence is known"
> *Line 144:* "Because every item is labeled, the TRUE prevalence is known."

**DEFECT — imprecise in a way that would become a README overclaim.**

Civil Comments labels are **`float32`**, not booleans. The schema is `toxicity`, `severe_toxicity`,
`obscene`, `threat`, `insult`, `identity_attack`, `sexual_explicit`, each a continuous value — the
**fraction of human annotators** who applied that label. There is no binary ground truth in the
dataset.

"True prevalence" only exists once a **threshold** is fixed (conventionally `toxicity ≥ 0.5`). That
threshold is a definitional choice made by the analyst, not a fact recovered from the data.

This is fixable and the fix makes the demo *better*, not worse. State the estimand explicitly —
*"the proportion of items in this corpus with `toxicity ≥ 0.5`"* — and it becomes exactly knowable
by census over all 1,999,514 rows, and the coverage demonstration is fully valid. But the sentence
as drafted claims access to a ground truth that does not exist, in the one document the whole
project is meant to make trustworthy.

Recommended wording: *"Every item carries a continuous human-annotation score. Once the estimand
fixes a threshold, the true value for this corpus is knowable by census — so we can check whether
our 95% intervals really cover it."*

### D3 — Cross-check against R `survey` fixtures
> *Line 138–139:* "compared against R `survey` results committed as fixtures. Agreement to ≥4 significant digits"

**VERIFIED as feasible; two conditions the charter must record.**

1. `survey` **4.5** (2026-02-24) is the version to pin. Fixtures must record the R version, the
   `survey` version, and the exact call.
2. `survey` is **GPL-2 | GPL-3**. Committing *numeric output* produced by running it is not
   distributing the package and does not make this project a derivative work — but the charter
   should state that reasoning explicitly rather than leave it unaddressed, and no `survey` source
   may be copied into this repository. *(Marked inference, not legal advice.)*
3. Generating fixtures requires an R installation. Docker (the director has Docker Desktop running)
   is the clean way to pin a reproducible R + `survey` 4.5 image in Phase 2. Recorded as a Phase 2
   note, not a Phase 0 action.

---

## E. Security, toolchain, and naming

### E1 — Fernet
> *Line 96–97:* "encrypted at rest (Fernet or better — Phase 0 ruling against current official cryptography guidance)"

**VERIFIED as to what Fernet is; the ruling is open (R-5).** Official `cryptography` documentation:

> *"Fernet is built on top of a number of standard cryptographic primitives. Specifically it uses:
> **AES in CBC mode with a 128-bit key** for encryption, using PKCS7 padding. **HMAC using SHA256**
> for authentication. Initialization vectors are generated using `os.urandom()`."*
> *"**Limitations** — Fernet is ideal for encrypting data that easily fits in memory."*

Current release: **`cryptography` 50.0.1**, uploaded **2026-08-25**, licence
`Apache-2.0 OR BSD-3-Clause`.

**Pinning defect found while checking this.** `https://cryptography.io/en/latest/fernet/` currently
serves documentation labelled **"Cryptography 51.0.0-dev1"** — an unreleased dev build — while the
released version is 50.0.1. STANDARDS.md must pin **version-locked** documentation URLs
(`/en/50.0.1/fernet/`), never `/latest/`. A standards register that cites a moving URL is not
pinned at all.

### E2 — Toolchain "Python 3.12+, ruff, mypy strict"
> *Line 134:* "Python 3.12+, ruff, mypy strict, frozen dataclasses, pyproject — the house stack"

**VERIFIED as available; the floor should move.** All figures from PyPI and endoflife.date,
28 Aug 2026:

| Component | Current | Released | Note |
|---|---|---|---|
| Python | **3.14.7** | 3.14 line since 2025-10-07 | 3.14 EOL 2030-10-31 |
| Python 3.12 | 3.12.14 | 2023-10-02 | EOL 2028-10-31 — supported, but two lines behind |
| Python 3.10 | 3.10.21 | | **EOL 2026-10-31 — under two months away** |
| `cryptography` | **50.0.1** | 2026-08-25 | |
| `ruff` | **0.16.5** | 2026-08-27 | |
| `mypy` | **2.3.1** | 2026-08-15 | requires ≥ 3.10 |
| `pytest` | **9.1.1** | 2026-06-19 | |
| `hypothesis` | **6.165.10** | 2026-08-16 | |
| `numpy` | **2.5.2** | 2026-08-09 | **requires Python ≥ 3.12** |
| `scipy` | **1.18.1** | 2026-08-21 | **requires Python ≥ 3.12** |
| `click` | **8.5.0** | 2026-08-26 | |
| `typer` | **0.27.2** | 2026-08-28 | released today |
| `pyyaml` | **6.0.3** | 2025-09-25 | |

Python 3.12+ is a valid floor — `numpy` and `scipy` both require ≥ 3.12, so it is also the minimum
that works. But the director's standing instruction is that everything be aligned to the latest, and
this build starts today on a machine already running **3.14.0**. Developing on 3.14 with a 3.12
floor is the normal, and stronger, arrangement: CI proves the floor, development uses the current
line. **Ruling R-6.**

### E3 — Name collision for "prevalence-kit"
> *Line 185:* "name-collision check for 'prevalence-kit'"

**VERIFIED CLEAR on every registry checked, 28 Aug 2026.**

| Registry | Name | Result |
|---|---|---|
| PyPI JSON API | `prevalence-kit` | **404 — unclaimed** |
| PyPI JSON API | `prevalence_kit` | 404 |
| PyPI JSON API | `prevalencekit` | 404 |
| PyPI simple index | `prevalence-kit`, `prevalencekit` | 404 |
| GitHub repo | `MohdSaifHussain/prevalence-kit` | 404 |
| GitHub repo | `prevalence-kit/prevalence-kit` | 404 |
| GitHub search | `prevalence-kit in:name` | **total_count 0** |
| npm registry | `prevalence-kit`, `prevalencekit` | 404 |

PEP 503 normalises `-`, `_` and `.` to one name, so the three PyPI spellings are a single namespace
and it is free. **No collision. The name is available.**

### E4 — Prior repositories exist and are public
> *Lines 221–223:* ts-sentry, finding-bridge

**VERIFIED as existing and public** (GitHub API, 28 Aug 2026): `MohdSaifHussain/ts-sentry`
(created 2026-07-31, MIT), `MohdSaifHussain/finding-bridge` (created 2026-08-24, Apache-2.0),
`MohdSaifHussain/switchyard` (created 2026-08-14, MIT), `MohdSaifHussain/ts-sentry-case-study`
(created 2026-08-02, MIT).

**The counts in the vision were not audited.** "1,230 tests" and "739 real attack prompts"
(lines 222–223) are the director's own figures about the director's own repositories. Under rule 13
— *re-derive a number from the artifact it describes* — these must be re-derived from those
repositories before they appear in any README, not carried across from this document. Recorded as a
**carried obligation for Phase 3**, not a Phase 0 defect.

---

## Summary

**24 claims checked. 18 VERIFIED, 6 DEFECT, 2 UNVERIFIED** (one claim carries both a verified and a
defective component; counted under its defect).

| ID | Claim | Verdict | Needs a ruling |
|---|---|---|---|
| A1 | Pinterest paper, Feb 2026 | VERIFIED (v2 exists, 2026-08-17) | — |
| A2 | "KDD '26" | **DEFECT** — targets KDD **2027**, placeholder DOI | R-3 |
| A3 | No code released | VERIFIED (negative result, width stated) | — |
| A4 | LLM in labeling path | VERIFIED | — |
| A5 | ml_sampler 2017–2020, archived 2021 | VERIFIED range / **path wrong** / archive year UNVERIFIED | R-3 |
| A6 | R survey since 2003 | VERIFIED (0.9-1, 2003-01-23; now 4.5) | — |
| A7 | svy MIT, active | VERIFIED (0.25.0, 2026-08-26) | — |
| A8 | svy not downloadable | **DEFECT — false; installs; overlaps more than assumed** | **R-1** |
| A9 | ROOST has nothing in measurement | VERIFIED | — |
| A10 | ROOST "$28M+" | **DEFECT** — source says **more than $27M** | R-3 |
| B1 | 2024/2835 exists, in force | VERIFIED, no 2026 version | — |
| B2 | DSA Arts 15/24/42 | VERIFIED | — |
| B3 | First reports early 2026 | VERIFIED, needs precision, now past | R-2 |
| B4 | "Accuracy indicators" | VERIFIED as words, misleading as framing | **R-2** |
| B5 | "Timing is regulatory" | **DEFECT — "prevalence" appears 0 times in both texts** | **R-2** |
| C1 | Wilson/Jeffreys per Google | **DEFECT** — source rejects Jeffreys; source is unofficial | **R-4** |
| C2 | Rogan–Gladen 1978 | VERIFIED (DOI) | — |
| C3 | Lang & Reiczigel 2014 | VERIFIED (DOI) | — |
| C4 | Refusal conditions | VERIFIED (mathematical, marked as such) | — |
| C5 | Cochran | VERIFIED; pin 3rd ed. 1977 | — |
| C6 | Barnett Table 2B to the digit | **VERIFIED by independent recomputation** | — |
| C7 | YouTube rater-quality caveat | VERIFIED verbatim | — |
| C8 | Meta CSER stratified + 95% CI | VERIFIED; strengthens the design | — |
| D1 | Civil Comments licence | VERIFIED — **CC0 1.0** | — |
| D2 | "TRUE prevalence is known" | **DEFECT** — labels are continuous, not binary | **R-7** |
| D3 | R survey fixtures | VERIFIED feasible; pin 4.5; GPL reasoning to record | — |
| E1 | Fernet | VERIFIED; `/latest/` doc URL is a pinning defect | **R-5** |
| E2 | Python 3.12+ toolchain | VERIFIED available; floor vs dev line open | **R-6** |
| E3 | Name "prevalence-kit" | **VERIFIED CLEAR** on PyPI, GitHub, npm | — |
| E4 | Prior repos | VERIFIED public; **counts not re-derived** | obligation |

**The two prior chat-drafted charters each contained real defects. So does this one — six.** The
two that change the project rather than a sentence are **A8** (svy is installable and overlaps the
Phase 2 plan) and **B5** (no regulation asks for prevalence).
