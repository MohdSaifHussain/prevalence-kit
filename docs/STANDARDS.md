# Standards register

**Status: RATIFIED — 28 August 2026.** Skeleton; entries are added as phases pin new sources.
**All entries verified 28 August 2026.** Evidence: `docs/PHASE-0-VERIFICATION.md`.

Every method, control and format used by prevalence-kit is anchored here to a named primary source,
pinned by version, date or commit. Nothing enters the code from memory or from a tutorial.

---

## The four rules of this register

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

**3. How a source was obtained is not recorded.**
Ruled by the director, 2026-08-30. This register carries the **citation**; whether the artifact is
the **publisher's copy**, where that was in question; the **read state with its scope**; and any
**route that changes what was read** -- a rendered scan is not a text layer, and that difference
belongs here. It **never** carries who supplied a source or how it arrived.

*Why it is a rule and not a preference.* An acquisition detail is about a **person**, not about the
work, and it has no bearing on whether the pin is sound. It also cannot be un-published: this
register is written to be read by a stranger, and Phase 3 is when that happens. **C-37.**

**4. Flip-day re-check.**
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
| S-1.1 | Binomial interval estimation — **ships Wilson (primary) + Clopper-Pearson (conservative). Jeffreys dropped, ruling R-4.** | Brown, L.D., Cai, T.T., DasGupta, A., *Interval Estimation for a Binomial Proportion*, **Statistical Science** 16(2) | **2001**, DOI `10.1214/ss/1009213286`. **Full text read 2026-08-29** — see below. Cited unread through Phases 0-2 | never — fixed publication |
| S-1.2 ▸ **ROLE NARROWED 2026-08-29** | **Origin of the method, not the source of our formula.** Stratified sampling, Neyman (optimal) allocation | Neyman, J., *On the Two Different Aspects of the Representative Method: The Method of Stratified Sampling and the Method of Purposive Selection* | **Primary publication: J. R. Statist. Soc. 97(4), 1934, pp. 558-625, DOI `10.2307/2342192`** — verified against Crossref by the director 2026-08-29. Reprint DOI `10.1007/978-1-4612-4380-9_12`. *The reprint was pinned alone until 2026-08-29, so a reader was sent to a republication rather than the primary.* **Our allocation is not the formula this paper writes — see below** | never |
| S-1.3 ▸ **READ 2026-08-29** | Sampling design reference | Cochran, W.G., *Sampling Techniques*, Wiley | **3rd edition, 1977**, ISBN `0-471-16240-X`. Sections read and the rendering route recorded below | never |
| S-1.4 | Misclassification correction | Rogan, W.J. & Gladen, B., *Estimating Prevalence from the Results of a Screening Test*, **Am. J. Epidemiol.** | **1978**, DOI `10.1093/oxfordjournals.aje.a112510` | never |
| S-1.5 | Confidence limits for corrected prevalence | Lang, Z. & Reiczigel, J., *Confidence limits for prevalence of disease adjusted for estimated sensitivity and specificity*, **Prev. Vet. Med.** | **2014**, DOI `10.1016/j.prevetmed.2013.09.015` | never |
| S-1.6 | Exact limits with an imperfect test (Phase 2 cross-check) | Reiczigel, J., Földi, J., Ózsvári, L., **Epidemiol. Infect.** | **2010**, DOI `10.1017/s0950268810000385` | never |
| **S-1.7** | **Rounding a Neyman allocation to whole units** -- the method Q4 ruled | Wright, T., *A Simple Method of Exact Optimal Sample Allocation under Stratification with Any Mixed Constraint Patterns*, **U.S. Census Bureau**, Research Report Series (Statistics) **#2014-07** | Issued **21 August 2014**; fetched **2026-08-29** from `https://www.census.gov/content/dam/Census/library/working-papers/2014/adrm/rrs2014-07.pdf` (HTTP 200, 154,969 bytes, sha256 `0fdd5e7ce795552843678d0871cfeacdb46c470c9fc0aa2eb182b352c0b0f196`) | never -- fixed publication |
| **S-1.8** | Why apportionment sources apply to survey allocation at all | Wright, T., *The Equivalence of Neyman Optimum Allocation for Sampling and Equal Proportions for Apportioning the U.S. House of Representatives*, **The American Statistician** | **2012**, 66(4), 217-224, DOI `10.1080/00031305.2012.733679` | never |
| **S-1.10** | **The Rogan-Gladen witness.** O-8 said there was none; that was true of `survey` and `svy`, not of the world | R **`epiR`** (Stevenson et al.), `epi.prev()`. Intervals *"based on code provided by Reiczigel et al. (2010)"* -- S-1.6 | **2.0.92 in our image**, because the base image's CRAN snapshot is frozen at 2026-04-23. **2.0.96 is current on CRAN** (published 2026-08-03), outside the snapshot. `GPL (>= 2)`, which CRAN expands to `GPL-2 \| GPL-3` | **2026-11-29** |
| S-1.11 *(context, never a method source for v1.0)* | A published alternative that answers where we refuse | Kopacka, I. & Fuchs, K., *Overcoming limitations of the Rogan-Gladen correction: a closed-form solution to a simplified Bayesian method for true prevalence estimation*, **Prev. Vet. Med.** | **2026**, vol 253, DOI `10.1016/j.prevetmed.2026.106891`. Verified live via Crossref 2026-08-29; full text not read. **NEXT queue, not v1.0.** Cited as *published work*, never as a package feature -- our pinned `epiR` 2.0.92 does not implement it, and the disclosure must hold regardless of what any version ships. C-25 | **every phase close** |
| **S-1.12** | **Witness for the stratified variance and for D-30's rounding.** Not a method source: nothing new is built from it | R **`stratallo`** (Wojciak, Wesolowski, Wieczorkowski). `var_st` / `var_stsi` for the stratified variance; `round_oric` / `round_ran` for integer rounding; `rna` / `rnabox` for allocation | **3.0.1**, published **2026-03-12**, GPL-2. **Inside our pinned snapshot** (2026-04-23) — confirmed by running the image, not by reading CRAN (C-25). `rnabox` implements Wojciak et al., *Survey Methodology* **2024**, box-constrained optimum allocation | **2026-11-29** |
| **S-1.9** | The formal treatment of largest remainder and its paradoxes | Balinski, M.L. & Young, H.P., *The Quota Method of Apportionment*, **American Mathematical Monthly** | **1975**, 82(7), 701-730, DOI `10.1080/00029890.1975.11993911`. **Metadata verified live via Crossref 2026-08-29; the full text was not read.** See the note below | never |

**Refusal conditions are mathematical consequences, not citations.** The Rogan–Gladen estimator is
`π̂ = (p̂ + Sp − 1)/(Se + Sp − 1)`. The denominator vanishes at `Se + Sp = 1` and the estimator
inverts sign below it. Refusing there is arithmetic, and it is marked as such so no reader mistakes
it for a claim about a source.


### S-1.1 -- read in full 2026-08-29, and it was cited unread for two phases

**The register was silent about this, and the silence was the defect.** S-1.9 and S-1.11 both say
plainly that their full text was not read. S-1.1 said nothing either way. It is the anchor for the
whole interval choice -- D-8, the charter, both contracts -- and nobody had read it.

Found when a ruling had to be checked against it and the text was not to hand. **Read 2026-08-29**,
in full. Statistical Science 2001, Vol. 16, No. 2, 101-133.

**Three published figures, now reproduced by our code.** This is the project's only external anchor
for the interval *choice*, as opposed to its arithmetic, and it is the same kind of evidence as
Barnett Table 2B: numbers computed by the method's own authors with nobody in this project involved.

| S-1.1 says | Section | We compute |
|---|---|---|
| Wilson at `p = 0.1765/n`, 95%, limit **0.838** | 4.1.1 | **0.8382** |
| Wilson at `p = 0.1174/n`, 99%, limit **0.889** | 4.1.1 | **0.8892** |
| Wilson `lim inf C(gamma/n, n)`, gamma >= 1, 95% = **0.92** | 3.2 | **0.9197** |

**What this establishes, and it is the contrast this project had never written down.** Wilson is the
charter's **primary** interval. At rare-event prevalence -- the regime this tool exists for -- its
coverage falls to **0.838 against a nominal 0.95**. Clopper-Pearson does not: section 4.2.1 says it
*"guarantees that the actual coverage probability is always equal to or above the nominal confidence
level."*

**The paper's own view of Clopper-Pearson, quoted rather than paraphrased**, because it does not
flatter our choice:

> *"The Clopper-Pearson interval is wastefully conservative and is not a good choice for practical
> use, unless strict adherence to the prescription C(p, n) >= 1 - alpha is demanded."*

For this tool, strict adherence **is** demanded -- it exists to refuse rather than to mislead -- so
shipping it as the conservative option is defensible. But the anchor's words are recorded here rather
than left out, because a register that only quotes the sentences supporting its choices is not a
register.

### Jeffreys: two sources that were never in conflict -- measured, not reconciled

**The first version of this section claimed S-1.1 said "close to the opposite" of the blog on
Jeffreys. That was wrong, and C-31 records it.** The two sources measure different quantities, and
S-1.1 says both things itself.

| Source | Quantity | Verdict |
|---|---|---|
| S-1.1 §3.2 | **average** coverage across p | *"excellent ... if anything, slightly superior"* to Wilson |
| S-1.1 §3.2 | coverage **near p = 0** | *"an unfortunate fairly deep spike"* |
| S-1.1 §4.1.2 | -- | supplies a **modified** Jeffreys whose whole purpose is removing that spike |
| S-X.1 (blog) | rare-event behaviour | reports Jeffreys is unsuitable there |

**So the anchor documents a rare-event problem with unmodified Jeffreys, independently of the blog.**
Averaging well across p and covering badly at small p are not contradictory; an average hides its
worst point, which is the whole reason this project measures at operating points rather than on
average.

**Measured rather than argued.** `r/coverage_fixtures.R` computes exact coverage for all three
candidates at the rare-event operating points. It validates itself against three of S-1.1's published
limits before reporting anything else -- D2.1's rule, applied to a second instrument. Worst coverage
over `p = gamma/n`, gamma in [0.5, 15]:

| n | nominal | Wilson | Clopper-Pearson | Jeffreys |
|---|---|---|---|---|
| 1000 | 0.90 | 0.8532 | **0.9043** | 0.8125 |
| 1000 | 0.95 | 0.9098 | **0.9540** | 0.9141 |
| 1000 | 0.99 | 0.9596 | **0.9908** | 0.9738 |

Our own numbers confirm the anchor's spike: **Jeffreys is the worst of the three at 0.90 and 0.95**,
which is the opposite of what "close to the opposite" implied.

**D-8's decision stands, and no charter amendment is needed.** The decisive reason was always that
Jeffreys is in neither witness library, so R2.3 has nothing to check it against -- Q1's reasoning,
applied before Q1 existed. And Jeffreys appears in `PROJECT_CHARTER.md` only inside the **A-0
amendment log**, a dated record of the director's ruling that is never edited. §6.1 does not mention
it; the builder's claim that it did was wrong.

### S-1.2 and S-1.3 -- read 2026-08-29, and our allocation is not the formula either one writes

**Ruled by the director, 2026-08-29: keep the formula, fix the citation.** S-1.2 was cited as
governing an allocation it states differently. The arithmetic is unchanged; the register role is
narrowed to **origin of the method**, and the divergence is recorded here with its measured size.

**What the paper says.** Neyman minimises the allocation-dependent term of his stratified variance,
and the minimum is at stratum sample sizes **proportional to `M_h · S_h`**, where he defines
**`S_h² = M_h σ_h² / (M_h − 1)`**. The variance he develops at his equation (37) is the
**without-replacement** form, carrying `(M_h − 1)`; the paper admits both regimes and works the
finite-population one.

**What we specify.** `n_h ∝ W_h · √(p_h(1 − p_h))`, i.e. `∝ M_h · σ_h`, with the
**with-replacement** stratified variance and **no finite-population correction**. That is
`PROJECT_CHARTER.md` §6.2 in its own ratified words, and S-2.3 below pins it by reproduction.
**The difference is a per-stratum factor of `√(M_h / (M_h − 1))`.**

**S-1.3 writes it the same way as S-1.2, and names the condition under which ours coincides.**
Cochran's §5.5 optimum is `n_h ∝ N_h S_h`; his (5.27) minimum variance carries a second term he
labels in the text as the fpc. His **Theorem 5.8** (`V_opt ≤ V_prop ≤ V_ran`) is stated to hold
*if terms in 1/N_h are ignored relative to unity* — **which is exactly the limit in which our
form and theirs agree.** So ours is a stated convention consistent with the with-replacement
variance this project uses throughout, not a misreading of either source.

*Cochran also records a priority note worth keeping, since this register names the method after
one man: he attributes the result to Neyman (1934) as the proof that gave it prominence, and
notes an earlier proof by **Tschuprow (1923)** was later discovered.*

**Why we did not adopt the paper's form**, as ruled. Barnett Table 2B — the only external anchor
this allocation has ever had — states its design in **weights `W_h`, not stratum sizes `M_h`**, so
it cannot express `√(M_h/(M_h − 1))` at all. Adopting Neyman's form would trade a formula
validated against a published table computed by nobody in this chain for one no instrument here
can check. That is Q1's argument pointing the other way.

**How large the divergence is. Two measurements, kept side by side, because they disagree by 7x.**
Neither figure means anything without the space it was measured over -- the axes rule, applied to
the newest number in the project.

| Measured by | Design space | Designs differing | Largest shift |
|---|---|---|---|
| Builder | 200,000 random designs; **2-6 strata**, sizes `U{2..4000}`, `p ~ U(0.001, 0.6)`, `n ~ U(2k, min(N, 5000))`, seed 20260829, largest-remainder rounding | **32,945 (16.47%)** | **3 units** (32,871 of them 1 unit) |
| Director | 199,994 designs; **2-5 strata**, `n = N/20`, `p ∈ [0.0005, 0.3]`, largest-remainder rounding | **2.30%** | **1 unit** |

**Both are kept and neither is reconciled into the other**, the same handling as the 0.9540 /
0.9537 coverage grids. Two measurements of one quantity differing by a factor of seven is evidence
about the measurement, and averaging it away would destroy that evidence. The director's search
also reports the divergence is nearly flat in stratum size -- 2.65% at sizes 8-40 against 2.17% at
1000-50000.

**A maximum found by search is a lower bound on the true maximum**, which is the opposite direction
from rule 8's usual case: a wider search can only find something larger. Neither "3 units" nor
"1 unit" is a ceiling.

**Nothing shipped is affected.** No stratified plan can be loaded today (`STRATA_UNDEFINED`), and
`run.py` calls `wilson()` alone. This was caught before the strata layer was built on it.

**The reading that produced this, and its route.**

| | S-1.2 Neyman (1934) | S-1.3 Cochran (1977) |
|---|---|---|
| **Artifact** | The **publisher's copy**: JSTOR stable `2342192`, matching the pinned DOI `10.2307/2342192`, with the Royal Statistical Society and Wiley named as collaborating on the digitisation. **Not a course-page scan**, which is why the earlier `not read` note existed | A **scanned book with no OCR layer** -- 442 pages, 442 image XObjects, **zero font objects**, producer `libtiff / tiff2pdf`. `pdftotext` returns 442 characters for the whole book |
| **What changed what was read** | -- | **Made readable locally** by rendering pages to images with `pypdfium2` **5.13.0** (2026-08-13, BSD-3-Clause / Apache-2.0) and `pillow` **12.3.0**, both version-verified live against PyPI and installed **into a scratchpad virtualenv outside the repository**. Recorded because it **changes the artifact that was read** -- rendered images, not a text layer |
| **Sections read** | Contents, §III.1, and the allocation derivation at (37)-(41) | §5.1 (definition), §5.5 end / §5.6 (Neyman allocation, relative precision), §5A.7 opening, and **§5A.8 *Number of Strata* in full** |
| **Read state** | **`partial`** | **`partial`** |

**A rendered scan is a different artifact from a publisher's text layer, and a reader should know
which they are trusting.** Cochran was read as images produced on this machine; every sentence
attributed to it above was read off a rendered page, not extracted as text.

**The zero-network guard is unaffected, and this is stated rather than left to be inferred.** The
guard walks `[project.dependencies]` in `pyproject.toml`. Neither `pypdfium2` nor `pillow` appears
there, in the dev extras, or in the project virtualenv -- they live only in a scratchpad
environment that no packaging metadata references. **"The guard did not object" is not "the guard
looked"**, so the evidence is this paragraph, not a green test.

**One caveat carried into the register rather than left in a chat message.** The Neyman reading
that bears on **Q12** -- that unrestricted sampling is the special case of stratified sampling
with a single stratum -- rests on **OCR of a 1934 scan**, where the glyph for "= 1" is mangled.
The sentence admits no other integer, so the meaning is robust, but a character-level claim taken
from OCR is **C-26's class** and is flagged as OCR-dependent here, not only where it was first
reported.

### S-1.7 -- largest-remainder rounding, quoted from the source

Q4 ruled that a rounded Neyman allocation uses **largest remainder**, named in the plan. Charter
section 5.4 says a method that cannot be validated against an authoritative reference does not ship,
so the method is quoted rather than described from memory.

The survey-sampling literature calls it **controlled rounding**. Wright (2014), S-1.7, section 1,
verbatim:

> *"In the allocation of the overall sample to the various strata, one may frequently need to round
> to integer values. The issue is often handled by controlled rounding. This is done by sorting
> fractional parts (non-integer remainders) from the largest to smallest and assigning the desired
> number of additional units to the strata with the largest fractional parts."*

That is exactly the rule Q4 ruled, from an official statistical agency, in the survey-allocation
context rather than the voting one.

**Why an apportionment method belongs in a sampling tool at all.** Wright (2012), S-1.8, proves
Neyman optimum allocation and the "equal proportions" method used to apportion the U.S. House of
Representatives are the same procedure. The two literatures are about one problem. Recorded because
citing voting theory in a prevalence tool otherwise looks like a reach.

### Two honest limits of the ruled method. Neither is a reason to reject it.

**Limit 1 -- controlled rounding is not always the best integer allocation.** From S-1.7's own
abstract, verbatim:

> *"The exact optimal allocation avoids the need to round to integer values, as is the case with
> Neyman allocation. Neyman allocation with rounded integers does not always lead to the optimal
> allocation."*

Wright gives a worked counterexample (section 2.3): Neyman yields `4.70 / 3.66 / 1.64` for n = 10;
controlled rounding gives `5 / 4 / 1` with variance 97,013, and an exact-optimal allocation does
better. **So our allocation is defensible and reproducible, and it is not variance-minimal.**

**How much is it costing us? Measured 2026-08-29, because a limit stated as a sentence is a shrug
and a limit stated as a number is something an auditor can weigh.** Rule 8.

For each allocation we enumerate every integer allocation within **two units per stratum** that sums
to n and keeps Q2's floor, compute the design variance of each, and compare.

| | Result |
|---|---|
| **On all three Neyman fixtures** | **gap exactly 0.** The ruled allocation *is* the best in the window. Widening to three and four units finds nothing better |
| Across 37,910 randomly generated admissible designs | the ruled rounding was not the in-window optimum in **1,976 of them, 5.21%** |
| **Worst gap found anywhere** | **0.7316% of variance**, which is **0.3651% of the standard error** an operator actually reads |

*Stated at the width of the search.* This is the best allocation found in a **bounded window**, not a
proof of global optimality. The zero on our fixtures means something only because the same search
finds real gaps elsewhere -- the negative control is pinned in
`test_the_optimality_search_can_find_a_gap`, and without it a search that reports zero everywhere
might simply be broken.

**Not grounds to revisit Q4.** Under 1% of variance at its worst, and zero on every fixture we
ship. **Wright's counterexample is not even admissible here** -- it puts a stratum at 1 unit, which
`ALLOCATION_TOO_THIN` refuses, so Q2's floor already excludes part of the region where rounding is
worst. Recorded because that was luck rather than design.

That is a real cost of the ruling, now with a size on it, stated here rather than discovered later.

**Limit 2 -- largest remainder is not monotone in n.** Raising the total sample size can *lower* a
stratum's allocation. Demonstrated on this project's own frames rather than cited, so it is
checkable:

| Frame | n where a stratum shrinks as n grows by 1 (searched n = 10..6000) |
|---|---|
| Barnett Table 2A | **303** values of n. Example: n = 60 gives `31/12/9/4/4`; n = 61 gives `32/13/9/4/3` -- stratum 5 loses a unit |
| `rare_event` | **173** values of n. Example: n = 48 gives `37/8/3`; n = 49 gives `38/9/2` |

This is the apportionment literature's **Alabama paradox** (S-1.9). **For a single pre-registered n
it never bites** -- the plan fixes n before any data is touched, so there is no second allocation to
be inconsistent with. It matters only to someone comparing two runs at different n, who could see it
and think the tool is broken. Stated so they find the explanation before they find the behaviour.

*Provenance note, per the standing rule.* S-1.9's metadata -- title, authors, journal, volume, issue,
pages, DOI -- was verified live against Crossref on 2026-08-29. **The full text was not read**, so no
sentence here is quoted from it, and the paradox above rests on our own computation instead. The DOI
first written from memory, `10.2307/2319793`, is a different paper entirely -- Bender and Goldman on
Mobius inversion. Caught by fetching. C-8's class, and the reason S-1.9 is cited by verified metadata
and nothing more.

### S-1.10 -- what the epiR witness establishes, and what it does not

**O-8's premise was wrong in our favour, and this is the second time this phase.** O-8 says
Rogan-Gladen has no library witness. D-3 was right that neither `survey` nor `svy` implements it. It
did not follow that nobody does. `epiR::epi.prev()` does, and it is on CRAN.

**The narrowing, and it is the part that must not be lost.** Jeno Reiczigel is a **listed contributor
to `epiR`**, and he is an author of both S-1.5 and S-1.6.

> **Barnett Table 2B is a published table produced without reference to any implementation.**
> Reproducing it tests our arithmetic against a number nobody in this chain computed.
>
> **`epiR` tests our arithmetic against the paper author's own code.** It confirms we implement the
> method as its author implements it. **It does not independently confirm the method.**

That is weaker than D2.1's anchor in a *specific* way, and naming the way is what stops the sentence
being read as modesty. For fidelity to the paper it is arguably the best witness available. For
independence it is not the same kind of evidence at all.

*(Ian Kopacka and Klemens Fuchs are also listed contributors, which is why S-1.11's method ships in
later `epiR` -- the authors' own package, not a third party adopting them.)*

**The version our witness actually runs is 2.0.92, not 2.0.96.** The base image pins CRAN to the
2026-04-23 snapshot, and 2.0.96 was published 2026-08-03 -- after it. Found by running the image
rather than by reading CRAN, which is V-17's shape exactly, caught this time before it reached the
register.

**One consequence, because it changes a disclosure.** `epi.prev()` in **2.0.92 has no `tp.method`
argument and no `simplified.bayes`** -- verified in the image. So S-1.11's method is in CRAN's current
`epiR` and **not in our pinned witness**. Anything read from the 2.0.96 manual about
`tp.method` describes a version we do not run.

**Behaviour verified in 2.0.92 directly, not read from the 2.0.96 manual:**

| Input | What `epi.prev` does |
|---|---|
| AP = 0, Sp = 0.99 | warns *"Apparent prevalence is less than (1 - Sp)"*, returns tp = **-0.011236** |
| **AP = 0, Sp = 1.00** | **no warning.** tp = 0, CI `[0, 0.001024]` -- a perfectly good rare-event answer |
| AP = 1, Se = 0.90 | warns *"Apparent prevalence greater than Se"*, returns tp = **1.112360** |
| **AP = 1, Se = 1.00** | **no warning.** tp = 1 |
| `pos=6, n=151, se=0.964, sp=0.927` | warns, returns tp = **-0.037334**, CI `[-0.065410, 0.012882]` |
| Se + Sp = 1 exactly | tp = **-Inf** |
| Se + Sp < 1 | tp = 6.6, and **the interval inverts**: lower 6.712724 above upper 6.459273 |

**That last row is the argument for refusing, and it belongs in the refusal itself.** Where
`Se + Sp < 1`, `epi.prev` returns **lower 6.712724 above upper 6.459273**. An inverted interval is
not an interval. So refusing is not a policy choice made in preference to a working alternative --
**there is nothing there to print.** An auditor reading our code should find that reason, not the
weaker one, and `CORRECTION_UNDEFINED`'s detail text carries it.

**Recorded as a property of the witness, not only of the region.** A witness that returns an inverted
interval inside the region we refuse is evidence *about* that region, and it sits here beside the
narrowing rather than in the estimator alone.

**PINNED AT 2.0.92, ruled 2026-08-29.** The same frozen snapshot that serves `survey` 4.5, so the
whole witness is reproducible from one pin. **2.0.96 is current on CRAN, outside the snapshot**, and
carries its own re-check date under **D-27** -- a version we could move to, not one we are running.

**The standing rule this produced, from C-25:**

> **The witness's documentation is not the witness. Only the pinned build is.**

Everything quoted from the 2.0.96 manual described a version we do not run. Every behaviour in the
table above was re-verified in 2.0.92 directly before it entered this register.

**System libraries, and which side of the line they fall on.** `epiR` pulls in `sf`, which links
against **proj, gdal, geos and udunits2**. Those are installed **in the witness image only**. They
are **not** in `[project.dependencies]`, not in the dev extras, and never reach anything an operator
installs.

**Hard Rule 1 is untouched, and this is stated rather than left to be inferred**, because the
zero-network guard's scope is now asserted: it walks `[project.dependencies]` and skips anything
marked `extra ==`. The witness image is on the far side of that line -- **the guard does not look at
it, and the guard not objecting to it is not evidence about it.** The evidence is this paragraph and
`r/Dockerfile`.


### S-1.12 -- what `stratallo` witnesses, and the narrowing that travels with it

**Found by going to official sources on stratified design, on the director's instruction**, rather
than by designing the strata layer from reasoning. The search turned up Statistics Canada's *Survey
Methodology* (2024) on box-constrained optimum allocation, and from there its CRAN implementation.

**It is in our pinned snapshot already.** Verified by running the image:

    snapshot: https://p3m.dev/cran/__linux__/noble/2026-04-23
    stratallo AVAILABLE, version 3.0.1
    EXPORTS: alloc_summary, coma, dca, dca_nmax, dca0, dopt, opt, optcost, rdca,
             rna, rnabox, round_oric, round_ran, sga, sgaplus, var_st, var_stsi

**What it strengthens, and it is all work already built:**

| Ours | Witness | Was checked against |
|---|---|---|
| `stratified_estimate` variance | `var_st` / `var_stsi` | R `survey` only |
| `largest_remainder` (D-30) | `round_oric` / `round_ran` | **nothing** — this is its first |

**The same narrowing as `epiR`, in the same words.** `stratallo` is the algorithm authors' own
implementation of their own papers. **It confirms we compute what they compute. It does not
independently confirm the method.** That is a different kind of evidence from Barnett Table 2B, which
is a published table produced without reference to any implementation.

**What it does NOT change.** `rnabox` is not adopted. Q2's `ALLOCATION_TOO_THIN` continues to refuse
under `allocation: neyman`, unchanged, and RNABOX is not a plan value in v1.0 — **deferred on scope,
not on witness.** See the charter's NEXT queue, whose reason was restated the same day because the
old one was false.

### Read state -- every entry, stated either way

**S-1.1 was cited unread through two phases and the register was silent about it.** S-1.9 and S-1.11
both said plainly that their full text was unread; S-1.1 said nothing, and **silence read as "read."**
That is a register-level defect, not a citation slip.

**So read state is now recorded for every entry, and absence of a note is no longer an answer.**
Four values, and `not recorded` is a real one -- filling it in by assumption would be the original
defect repeated.

| State | Means |
|---|---|
| `full` | The full text has been read by someone on this project |
| `partial` | Named sections read, quoted or re-derived. The scope is stated |
| `not read` | Deliberately cited on metadata alone, and the entry says so |
| `not recorded` | **Nobody wrote it down. Unknown, not assumed.** |

| Entry | Read state | Evidence |
|---|---|---|
| S-1.1 | **full** | Read in full 2026-08-29. Three published limits reproduced |
| S-1.2 Neyman 1934 | **`partial`** *(read 2026-08-29)* | **The publisher's copy** — JSTOR stable `2342192`, matching the pinned DOI, RSS and Wiley named. Contents, §III.1, and the derivation at (37)-(41). The earlier `not read` note was correct at the time: the only text then found was a university course-page scan, the paper's text but not the publisher's copy. **Confirmed by the reading: the allocation formula came from S-2.3's re-derivation and not from this text — the paper writes it differently.** See the S-1.2 / S-1.3 section |
| S-1.3 Cochran | **`partial`** *(read 2026-08-29)* | §5.1, §5.5 end / §5.6, §5A.7 opening, and **§5A.8 in full**. A 1977 book with no free official text and **no OCR layer**: read as pages rendered locally with pinned `pypdfium2` / `pillow` in a scratchpad virtualenv, never the project one. **A rendered scan is not a publisher's text layer**, and the entry says which was trusted |
| **S-1.13** *(new)* | **full** | **Statistics Canada**, official methodology, read 2026-08-29. Supplies the two design rules S-1.2 and S-1.3 were standing in for: strata are *"homogeneous, **mutually exclusive** groups"* and *"**independent samples are selected from each stratum**"* |
| S-1.4 Rogan-Gladen 1978 | `not recorded` | The estimator is one line of algebra and is checked against `epiR`, not against this text |
| S-1.5 Lang & Reiczigel 2014 | `not read` | Deliberately not implemented (D-31). Cited to say what we do **not** do |
| S-1.6 Reiczigel 2010 | `not recorded` | The interval is checked against `epiR`, which cites it. We have not read it |
| S-1.7 Wright 2014 | **partial** | §1 and §2.3 quoted verbatim; abstract quoted. Fetched, digest recorded |
| S-1.8 Wright 2012 | `not read` | Metadata verified via Crossref |
| S-1.9 Balinski-Young 1975 | `not read` | Stated in the entry. The paradox is demonstrated on our own frames instead |
| S-1.10 `epiR` | **partial** | Source behaviour verified by running 2.0.92 directly. Package docs not the witness (C-25) |
| S-1.11 Kopacka & Fuchs 2026 | `not read` | Stated in the entry. Crossref metadata only |
| S-1.12 `stratallo` | **partial** | Availability and exports verified by running the pinned image. Vignette and reference manual **not read** |
| S-2.1 `survey` 4.5 | **partial** | Tarball compared file by file against the p3m mirror (V-17). Source not read |
| S-2.1a / S-2.1b | **full** | An image digest and a call, not a document. Both executed |
| S-2.2 `svy` 0.25.0 | **partial** | `base.py` lines 713-746 read and quoted (D-18) |
| S-2.3 Barnett 2021 | **partial** | Tables 2A and 2B read and independently re-derived, Phase 0 §C6 |
| S-2.4 `binom.test` | **full** | Base R behaviour, executed across 69 cases |
| S-3.1 … S-3.4 | `not recorded` | Platform methodology pages, cited for published caveats |
| S-4.1 Reg. 2022/2065 | **partial** | Full text retrieved and mechanically counted for one word (D-5) |
| S-4.2 Reg. 2024/2835 | **partial** | Same. Digest and page count re-derived |
| S-4.3 Decision 2011/833/EU | **partial** | Articles 2, 4 and 6 read in two renderings and compared (O-18) |
| S-5.1 … S-5.4 | **partial** | Documentation and changelog sections read at pinned URLs |
| S-7.1 … S-7.3 | `not recorded` | Dataset and licence pages |
| S-8.1 … S-8.4 | **full** | Procedures, not documents. Each executed and its result recorded |
| S-X.1 (the blog) | **full** | Read end to end during Phase 0 verification, which is how C-3 was found |

**What this table is not.** It records whether a source was read, not whether reading it would change
anything. Several `not recorded` entries are almost certainly harmless -- Cochran is a textbook
reference, and the Rogan-Gladen formula is checked against a witness rather than against its paper.
**S-1.1 was the dangerous one precisely because it is the anchor for a choice rather than a formula**,
and choices cannot be checked against a witness.

**Owed:** a `check_claims` check that every S-entry carries one of the four states, so a new entry
cannot be added without one. Opened as **O-24**.

## S-2 — Validation targets

| ID | Target | Source | Pin | Re-check |
|---|---|---|---|---|
| S-2.1 | Numerical cross-check for every estimator | R **`survey`** (Lumley) | **4.5**, published **2026-02-24**; re-verified live **2026-08-29**. **Upstream:** `https://cran.r-project.org/src/contrib/survey_4.5.tar.gz` (HTTP 200). **Retrieved from:** the p3m mirror, S-8.4 -- the two were compared byte for byte, V-17. GPL-2 \| GPL-3 | **2026-11-28** |
| S-2.1a | The R environment the witness runs in | `rocker/r-ver`, **pinned by digest, not by tag** | **`rocker/r-ver@sha256:c3f39b365d1077fe24f8e9ab2742e352b6d3950897f51af1624a5bb5550c21c0`** (tag `4.5.3`, pushed 2026-06-24). Docker 29.7.2 on this machine. | **2026-11-29** |
| S-2.1b | The witness **as actually executed**, 2026-08-29 (O-3) | `r/Dockerfile` builds on S-2.1a | **R 4.5.3 (2026-03-11)**, **`survey` 4.5**, `jsonlite` 2.0.0. CRAN frozen at the base image's snapshot `https://p3m.dev/cran/__linux__/noble/2026-04-23`, so the install is deterministic and serves the version S-2.1 pins. **The exact call:** `svydesign(ids = ~1, strata = ~stratum, weights = ~w, data = sample_rows)` — no `fpc`, which is what makes it the with-replacement form S-2.3 specifies | **2026-11-29** |
| S-2.2 ▸ **USED 2026-08-30, D2.9** | Second independent cross-check **where its estimator is the same estimator** — which is **allocation only**, see below | Python **`svy`** (Samplics LLC) | **0.25.0**, uploaded **2026-08-26**; MIT. **`0.26.0` is current on PyPI as of 2026-08-30 and we do not run it** — the witness is the pinned build (C-25), and TW-2 watches the gap | **2026-09-28** — fast-moving, 48 releases |
| **S-2.4** | **The Clopper-Pearson witness** | R **`stats::binom.test`**, base R -- a different implementation lineage from `survey` | **R 4.5.3**, in the S-2.1a image. Call: `binom.test(k, n, conf.level = 0.95)$conf.int`. 23 cases in `r/fixtures/clopper_pearson.json` | **2026-11-29** |
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

### V-17 -- the register said CRAN, the build installed from a mirror

**The defect.** S-2.1 named CRAN. The R image installs from **Posit Package Manager**
(`p3m.dev`), because that is the mirror `rocker/r-ver` pins. Mirroring CRAN at a frozen date is a
good choice for reproducibility and is not the problem. The problem was that **the register named
one source, the build fetched from another, and nobody had checked the two carry the same package.**

That is the gap between *should be identical* and *verified identical*, which is the gap this whole
project exists to close.

**What we did.** Fetched both tarballs and compared them file by file.

| | |
|---|---|
| CRAN | `https://cran.r-project.org/src/contrib/survey_4.5.tar.gz`, 2,417,046 bytes, sha256 `8a2ab01759f9acf6000274255edf00e342dfbf320a39fb76d42594e4d262b519` |
| p3m | `https://p3m.dev/cran/2026-04-23/src/contrib/survey_4.5.tar.gz`, 2,416,230 bytes, sha256 `18b6b42755169daefe49525401857fa9817ea0b77ca551f87c94dda01a9f71ab` |

**The archives are not byte-identical. The package is.**

The tarball holds 355 entries: **341 regular files** and 14 directories. **339 of the 341 files are
byte-identical.** `R/`, `src/`, `man/`, `data/`, `inst/`, `tests/` and `NAMESPACE` all match exactly.

**Exactly two files differ, and both are repository metadata:**

- `DESCRIPTION` -- the mirror writes `Repository: RSPM` where CRAN writes `Repository: CRAN`, and
  adds an `Encoding: UTF-8` line.
- `MD5` -- follows from the line above, because it lists `DESCRIPTION`'s own checksum.

So the mirror serves CRAN's `survey` 4.5 with a mirror stamp on it. **That is now measured, not
assumed.**

**Stated at the width of the evidence, and no wider.** This compares the two **source** tarballs.
The image installs a **binary** build that p3m compiled from its copy of that source. We have not
rebuilt that binary ourselves, so what is proven is that the source p3m serves is CRAN's source, not
that the binary is a faithful build of it.

**Watched, not remembered.** **TW-5** re-runs this comparison. A third differing file means the
mirror is serving something CRAN is not.

### S-2.4 -- why base R is a real witness for Clopper-Pearson, and not a mirror

The Phase 2 contract's §2.3 assumed Clopper-Pearson had **no external witness**, because it has no
published table, and planned to check it against an implementation we wrote. That was pessimistic in
our favour: `stats::binom.test` ships with base R, returns the Clopper-Pearson interval, and is a
different lineage from `survey`.

**The independence is structural, not promised.** The two sides reach the interval by different
arithmetic:

| | Route |
|---|---|
| R | inverts an **incomplete beta**, via `qbeta` |
| prevalence-kit | root-finds on the **binomial tail**, in log space via `lgamma` |

`lgamma` is the log of the *complete* gamma -- a log factorial. **There is no incomplete beta
function anywhere in this package.** So the failure the director warned about -- checking `betainc`
against `betainc`, which would look like agreement and mean nothing -- cannot occur here by
construction rather than by care.

**Measured across all 69 cases: n = 1 to n = 1,999,514, k across each, and confidence in
{0.90, 0.95, 0.99}.** The figures below were first published as 7.1e-11 and 6.9e-09, which were
the same measurements at confidence 0.95 only -- **C-30**. An agreement figure states its axes.

| What | Worst disagreement |
|---|---|
| The method, in full double precision | **8.4e-11** |
| After our own `DIGITS = 12` record rounding | **2.7e-07** |
| The defining property at our endpoints -- `P(X >= k | lower)` against `alpha/2` | **3.9e-13** |

**The rounding is the larger of the two, and adding the confidence axis widened the gap from 100x
to 3000x.** `DIGITS = 12` costs a fixed *absolute* precision; higher confidence pushes rare-event
lower bounds smaller, so the same absolute error is a larger relative one. The 2.7e-07 is our
record format, not our estimator. R2.3 asks for four significant digits; both clear
it by orders of magnitude.

### S-2.2 -- what `svy` witnesses, and what it turns out not to

**D2.9, 2026-08-30.** **D-18** narrowed O-4 to *only where its estimator is the same
estimator*, and D2.9 is where that rule was applied by reading the source and running it
rather than by assuming an overlap.

**Every interval `svy` 0.25.0 offers is design-based, so none of them witnesses ours.**
Read from `svy/estimation/base.py` in the pinned build:

| `svy` method | What it computes |
|---|---|
| `logit` *(its default)* | Wald-type interval on the logit scale, back-transformed |
| `beta` | Korn-Graubard with a **df-adjusted effective sample size**, via the incomplete beta |
| `korn-graubard` | The same, plus truncation of the effective sample size at `n` (NCHS) |
| `wilson` | The design-based Wilson **D-18** already recorded -- `n_eff = p(1-p)/se^2`, t-quantile |

**And the alias is the tell.** `svy` maps **`"clopper-pearson"` to `"korn-graubard"`**.
Asking it for Clopper-Pearson does not return the textbook interval this project ships. So
D-18's finding about Wilson was not a quirk of one method: **it is true of every interval
`svy` has**, for the same structural reason -- each substitutes an effective sample size for
`n`, and ours do not.

**Allocation is the one place the two coincide, and it is the place we most needed one.**
`svy.selection.allocation._neyman_allocation` computes `measure = N * S`, then
`raw = measure / total * n`, then floors and hands the shortfall to the largest fractional
parts. **That is Neyman allocation with largest-remainder rounding** -- our formula and
**D-30**'s rule, arrived at independently.

**This is the first genuine external witness the allocation has ever had.** **F-9**
established that R `survey` has **no allocator**, so `r/stratified_fixtures.R`'s `neyman()`
is our own formula re-implemented in R by its own author -- the sixth instrument-limit kind,
a fixture that looks external and is not. `svy` is a different author, a different language
and a different lineage.

**Measured, with the space stated.**

| What | Result |
|---|---|
| The three shipped Neyman fixtures | **all three identical**, including `rare_event_neyman_5000` -- the case whose floors summed to 4999 and forced **Q4 / D-30**. `svy` gives the remainder to the same stratum |
| Randomised sweep: 2000 designs, seed 20260830, 2-6 strata, weights ~ U(0.01, 1) normalised, `p` ~ U(0.0005, 0.5), `n` ~ U(2k, 20000) | **2000 of 2000 identical** |
| Exact fractional ties, 2 and 3 equal strata | **Identical.** `svy` sorts with numpy, whose default sort is not stable, so this could have gone either way. D-30 condition 2 required our tie-break to be deterministic and stated; it did not require anyone else to agree |

**Where they part, and it is policy rather than estimator.** `svy` has two behaviours we do
not: `min_n` floors a stratum up from a raw allocation below 1, and `cap_at_population` caps
and redistributes when Neyman asks for more units than a stratum holds. **We refuse in both
places** -- `ALLOCATION_TOO_THIN` (Q2) and `ALLOCATION_IMPOSSIBLE`. So the agreement above is
over the region where both produce an *unconstrained* allocation, and outside it the two
tools do different things about the same problem. Asserted in
`test_where_the_two_implementations_diverge_we_refuse_rather_than_adjust`, so the 2000-case
figure cannot later be read wider than it is.

**Hard Rule 1 is untouched, and the mechanism is the same as the renderer's.** `svy` declares
a hard dependency on **`httpx`**, which is D-2's whole reasoning for not depending on it. So
it is installed in a **throwaway environment**, `svy/generate_allocation_fixtures.py` is run
there, and **only the output is committed**. `svy` is not in `[project.dependencies]`, not in
the dev extras, and not in the project virtualenv. The zero-network guard walks
`[project.dependencies]`; **it does not look at a throwaway environment, and its silence is
not evidence about one** -- this paragraph is the evidence.

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

**The backup evidence.** This is the EUR-Lex legal notice, copyright section. **Transcribed by hand
from a browser on 2026-08-29**, because no fetcher here can reach the page. *The transcription is
recorded because it changes what was read -- a hand copy, not a fetched document:*

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
| S-8.4 | Install `survey` into the R image | `install.packages("survey")` inside `rocker/r-ver` (S-2.1a), which pins its CRAN mirror to `https://p3m.dev/cran/__linux__/noble/2026-04-23` | **2026-08-29**: serves `survey` **4.5**, the version S-2.1 pins. Compared against CRAN's own tarball: **339 of 341 regular files byte-identical**. See V-17 for the two that differ and why | **2026-11-29** |
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
| O-8 **(restated 2026-08-29 by D-31)** | ~~Rogan–Gladen has no library witness — validate against the worked results in Lang & Reiczigel (2014)~~ **Both halves wrong in our favour.** Witness is `epiR::epi.prev()` 2.0.92, **S-1.10**; interval anchor is **S-1.6** Reiczigel et al. (2010), Se/Sp *known*, **not S-1.5** | Phase 2 | open — discharges at **D2.6** |
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
