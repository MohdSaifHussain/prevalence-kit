# Rulings queue — Phase 0

**CLOSED — 28 August 2026. All seven ruled by the director.**

This file is kept as the historical record of what was asked and what was recommended. The
director's answers are recorded **verbatim** in `docs/RATIFICATION.md`, and their consequences in
`docs/DECISIONS.md` (D-1 … D-13).

| Ruling | Outcome |
|---|---|
| R-1 svy | **ACCEPTED as recommended** — keep `lean`, httpx rationale, dual cross-check, credit svy → D-2, D-3, D-4 |
| R-2 regulatory positioning | **ACCEPTED** — inverted → D-5 |
| R-3 citations | **ACCEPTED, all three** — plus: record the ROOST source conflict, do not resolve it → D-6, D-7 |
| R-4 interval anchor | **ACCEPTED** — Brown/Cai/DasGupta; Wilson + Clopper-Pearson; Jeffreys dropped → D-8 |
| R-5 cipher | **RULED: Fernet** (builder recommended Cobblestone-128; overruled on soak time) → D-9 |
| R-6 Python | **ACCEPTED as recommended** → D-10 |
| R-7 coverage demo | **ACCEPTED** — plus: extend to multiple thresholds, sensitivity curve → D-11 |

**One recommendation was overruled: R-5.** The builder recommended Cobblestone-128; the director
ruled Fernet. The director's precondition — verify Cobblestone exists or report its absence as a
defect — was discharged: it exists, confirmed in the official changelog at two URLs. No defect.

---

*The original queue, as presented, follows unchanged.*

---

## Reported findings — no ruling needed, acknowledgement requested

### F-1 — Name-collision check: **CLEAR**. Checked, not assumed.

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

PEP 503 normalises `-`, `_` and `.` to a single name, so the three PyPI spellings are one namespace
and it is free. **The name is available on every registry checked.**

### F-2 — Validation dataset licence: **CC0 1.0**. Best possible outcome.

`google/civil_comments`, verbatim from the dataset card: *"This dataset is released under CC0, as is
the underlying comment text."* No attribution obligation, no share-alike, no redistribution
restriction. 1,999,514 rows. Siblings `google/jigsaw_unintended_bias` and
`google/jigsaw_toxicity_pred` are also CC0 1.0.

**Nothing blocks the flagship demo.** But see **R-7** — the labels are not what the vision assumed.

---

## R-1 — svy is installable. The TW-2 premise was false. *(Changes the project)*

**The defect.** The vision says svy's installable code "was not yet publicly downloadable", and
makes that the reason v1.0 writes its own `lean` estimators. **This is false.**

Verified by execution on 2026-08-28, in a clean virtual environment on this machine:
`pip install svy==0.25.0` succeeded. Wheel and sdist both published. It imports and runs.

**And the overlap is bigger than assumed.** svy 0.25.0 already has: SRS selection, proportional
allocation, **Neyman allocation** (with named refusals), **Wilson intervals**, Clopper-Pearson,
Korn-Graubard, logit intervals, Taylor-linearization variance, post-stratification, raking,
calibration, replicate weights, sample size and power.

That is most of Phase 2's estimator work, already written, MIT-licensed, released two days before
this check.

**What svy does not have** — and this is the whole product: Jeffreys (0 occurrences),
Rogan–Gladen (0 occurrences), sealing, encryption, hash-chained ledger, audit trail (0 occurrences
of `ledger`, `fernet`, `encrypt`, `tamper`).

**A better reason for `lean` exists, and it is checkable.** `svy` declares a hard runtime dependency
on **`httpx`** (`Requires: httpx, msgspec, numpy, polars, scipy, svy-io, svy-rs`). Hard Rule 1 is
zero network calls at runtime, *proven by a test that fails if any network capability appears*. We
cannot ship an HTTP client and make that claim.

**Options.**

| | Option | Consequence |
|---|---|---|
| **A** | **Keep `lean` estimators. Replace the reason with the `httpx` argument. Cross-check against svy as well as R `survey`.** | Hard Rule 1 survives intact. Phase 2 keeps its work but gains a second independent validator. Positioning shifts from "we fill an estimator gap" to "we are the governance layer." |
| B | Depend on svy; drop the zero-network guarantee to "no network calls made by us" | Cheaper build. **Weakens the headline security claim to something unprovable by the existing test.** |
| C | Depend on svy as an optional extra; `lean` remains the default | Most flexible, most surface area, most to test. Breaches the scope cap. |

**Recommendation: A.** It is the only option that keeps Hard Rule 1 provable, and cross-checking
against two independent implementations is stronger validation than the vision planned. Cost: the
README must stop implying we fill an estimator gap. We do not. svy fills it well.

**Ruling: ______________________**

---

## R-2 — No regulation requires prevalence. The positioning must change. *(Changes the project)*

**The defect.** The vision's §2 says *"The timing is regulatory, and it is now."*

**The word "prevalence" appears zero times in Regulation (EU) 2022/2065 (the DSA) and zero times in
Implementing Regulation (EU) 2024/2835.** Counted mechanically over the full official texts, both
retrieved from the EU Publications Office, and 2024/2835 independently corroborated against the PDF
you downloaded yourself.

No EU regulation requires a platform to report prevalence. A regulator or a reviewer would find this
in one search, and the credibility of a tool whose entire pitch is verifiability would not survive
it.

**What the regulation actually requires** (Annex I §1.6): accuracy, precision and recall of automated
moderation, with qualitative guidance explicitly naming *"sensitivity ... specificity ... precision
or positive predictive value ..."*

**Those are the Rogan–Gladen inputs.** So there is a real seam and it runs the other way:

> Regulation obliges platforms to publish label-quality figures. prevalence-kit shows what those
> figures do to a prevalence estimate — and refuses when they make it undefined.

**Options.**

| | Option | Consequence |
|---|---|---|
| **A** | **Replace the regulatory claim with the inverted framing above. State in Honest Limits that no regulation requires this number.** | Honest, checkable, and more interesting than the claim it replaces. Loses the "it's urgent" energy. |
| B | Drop regulatory framing entirely; position purely on platform practice (Meta, YouTube, Pinterest all do this) | Safest. Also true and well-sourced. Loses a genuine connection. |
| C | Keep the vision's framing | **Not recommended. It is not supportable and it is trivially falsifiable.** |

**Recommendation: A.** It is drafted that way in `PROJECT_CHARTER.md` §3 and `docs/PRIOR-ART.md` §5.

Secondary point, same ruling: "first harmonized reports due in early 2026" is **verified** — the
Commission's own announcement says so verbatim. But today is 28 August 2026, so it is in the past.
Do not write it as forthcoming.

**Ruling: ______________________**

---

## R-3 — Three citation defects. *(Changes wording)*

Bundled because they are the same class: a claim stated wider than its source.

**(a) "KDD '26" is wrong.** The Pinterest paper's own header targets *"The 33rd ACM SIGKDD
Conference ... August 2027, San Jose"*, its DOI field is the unfilled ACM placeholder
`XXXXXXX.XXXXXXX`, and arXiv carries no `journal_ref`. It is a preprint formatted for **KDD 2027**,
not a KDD 2026 paper. Also: cite **v2 (2026-08-17)**, not the February v1.

**(b) ROOST funding is $27M, not $28M.** The official launch release of 10 February 2025 says
verbatim: *"more than **$27 million** for its first four years of operations."* No source was found
for $28M.

**(c) `ml_sampler` lives at `facebookarchive/ml_sampler`.** `facebook/ml_sampler` returns 404. The
commit range 2017–2020 is exactly right (first 2017-01-25, last 2020-08-06). **"Archived 2021" could
not be verified** — GitHub exposes no archive date.

**Recommendation:** accept all three corrections as drafted in `docs/PRIOR-ART.md`, and for (c) write
*"archived (date not publicly recorded); last commit 2020-08-06"*, which is provable.

The $1M rounding is small. The principle is not: this is precisely the failure the tool exists to
prevent, appearing in the tool's own charter.

**Ruling: ______________________**

---

## R-4 — The Google blog cannot be a method source, and it does not say what the vision claims.

**Two defects in one line.**

**(a) It does not endorse Jeffreys — it criticises it.** The post is *"Estimating the prevalence of
rare events — theory and practice"*, Yi Liu, 27 August 2019. It concludes *"the stratified Wilson
interval works well for our video sampling problem"* and reports that **Jeffreys over-covers for
rare events** by shrinking toward 0.5. Presenting "Wilson / Jeffreys" as jointly matching "Google's
published practice" misrepresents it.

**(b) It is not an official source, and Hard Rule 3 forbids it.** The blog is self-declared
unofficial. Rule 3: *"no method enters the code from memory or from a tutorial."* A blog is a
tutorial. Anchoring an estimator there breaks the project's spine on its first technical page.

*You raised this in session. For completeness the domain was checked and is genuine Google
infrastructure — NS `ns-cloud-d1.googledomains.com`, Blogger IP block, `www` CNAME `ghs.google.com`,
TLS from Google Trust Services. Not a lookalike. Still unofficial.*

**Recommendation.** Anchor the intervals on the peer-reviewed canonical source:

> Brown, L.D., Cai, T.T., DasGupta, A. (2001). *Interval Estimation for a Binomial Proportion.*
> **Statistical Science** 16(2). DOI `10.1214/ss/1009213286` — verified in the Crossref registry.

Demote the blog to context in `docs/PRIOR-ART.md`, cited only as evidence of what a Google author
reports YouTube does.

**Consequential sub-ruling — which second interval ships in Phase 2?** The vision says Jeffreys.
Given that the only source cited for it criticises it for this exact use case:

| | Option |
|---|---|
| **A** | **Wilson (primary) + Clopper–Pearson (conservative second).** Clopper–Pearson is exact, never under-covers, and svy and R `survey` both implement it — so both cross-checks work. |
| B | Wilson + Jeffreys as drafted. Defensible on Brown/Cai/DasGupta, but svy has no Jeffreys, so only R `survey` can cross-check it. |
| C | Wilson only in v1.0; second interval to NEXT. Smallest scope. |

**Recommendation: A.**

**Ruling: ______________________**

---

## R-5 — Cipher for sealing content. *(Security decision)*

The vision says *"Fernet or better — Phase 0 ruling against current official cryptography
guidance."* Here is that guidance, read from the official documentation at the **version-pinned**
URL `https://cryptography.io/en/50.0.1/`, current release **50.0.1 (2026-08-25)**.

| | Option | What the official docs say | Layer |
|---|---|---|---|
| A | **Fernet** | *"AES in CBC mode with a 128-bit key ... PKCS7 padding. HMAC using SHA256 for authentication."* Stated limitation: *"Fernet is ideal for encrypting data that easily fits in memory."* | recipes (safe) |
| **B** | **Cobblestone-128** | *"authenticated symmetric encryption of large messages — up to 4 PiB — as a stream, without ever holding the whole message in memory."* Implements the C2SP chunked-encryption specification. *"Cobblestone-128 (SHA-512 and AES-128-GCM, **the recommended choice**)"* | recipes (safe) |
| C | `AESGCM` via `hazmat` | *"**Danger.** This is a 'Hazardous Materials' module. You should ONLY use it if you're 100% absolutely sure that you know what you're doing because this module is full of land mines, dragons, and dinosaurs with laser [beams]."* Plus: *"NEVER REUSE A NONCE with a key."* | hazmat |

**Recommendation: B, Cobblestone-128.** Four reasons:

1. It is in the **recipes layer**. Option C is explicitly warned against by the library's own
   documentation, and nonce management is a footgun we would own forever.
2. It removes Fernet's size cliff. We seal content sets, and "must fit in memory" is a limit we
   would eventually hit and have to migrate off.
3. **It has a `context` parameter for domain separation.** We can bind every seal to the plan hash —
   `context=b"prevalence-kit seal v1 <plan-hash>"` — so a ciphertext from one measurement cannot be
   silently decrypted as part of another. That is a real integrity win specific to this tool, and it
   is free.
4. AES-128-GCM is AEAD, and it is what the library itself calls "the recommended choice".

**The honest counter-argument, stated because you should have it.** Cobblestone was **added in
`cryptography` 50.0.0, released 2026-07-31** — four weeks ago. New is a real risk factor for a
security primitive, even one implementing a public specification from a reputable maintainer. If
maturity outweighs the size limit for you, **Fernet (A) is a perfectly defensible ruling** and it
has years of use behind it.

This is a genuine judgment call between a better fit and a longer track record. It is yours.

**Ruling: ______________________**

---

## R-6 — Python floor and development line.

Your standing direction: everything aligned to the latest. Current facts, 2026-08-28:

- Python **3.14.7** is current; this machine runs **3.14.0**
- Python **3.12** is the hard floor regardless of preference — `numpy` 2.5.2 and `scipy` 1.18.1 both
  require ≥ 3.12
- Python **3.10 reaches end of life on 2026-10-31**, inside this project's lifetime

| | Option |
|---|---|
| **A** | **Develop on 3.14. Declare floor `>=3.12`. CI runs 3.12, 3.13 and 3.14.** |
| B | Floor `>=3.14`. Simplest, newest, smallest CI matrix. Excludes users on 3.12/3.13 for no gain. |
| C | Floor `>=3.12`, CI on 3.12 only. Cheapest CI; does not prove the tool works on the line you develop on. |

**Recommendation: A.** It is the normal and stronger arrangement — CI proves the floor, development
uses the current line, and both are latest-aligned in the sense you meant.

**Ruling: ______________________**

---

## R-7 — "The TRUE prevalence is known" is not accurate. *(Changes the flagship demo's wording)*

**The defect.** The vision's §7.3 says *"Because every item is labeled, the TRUE prevalence is
known."*

Civil Comments labels are **`float32`**, not booleans. Every field — `toxicity`, `severe_toxicity`,
`obscene`, `threat`, `insult`, `identity_attack`, `sexual_explicit` — is the **fraction of human
annotators** who applied that label. **There is no binary ground truth in the dataset.**

"True prevalence" exists only once a **threshold** is fixed. That threshold is our definitional
choice, not a fact recovered from the data.

**This is fixable, and the fix makes the demo better.** State the estimand explicitly and the true
value becomes exactly knowable by census over all 1,999,514 rows — which is all the coverage
demonstration needs.

**Recommended wording:**

> Every item carries a continuous human-annotation score. Once the estimand fixes a threshold, the
> true value for this corpus is knowable by census — so we can check whether our 95% intervals
> really cover it.

**Why this matters more than a sentence.** It would sit on the README front page of a tool whose
entire claim is that its numbers are checkable. Claiming access to a ground truth that does not
exist, in the flagship demo, is the single most damaging small error available in this project.

**Ruling: ______________________**

---

## What happens after you rule

1. Your rulings are recorded **verbatim** in the charter's amendment log.
2. The charter, TRIPWIRES, PRIOR-ART, STANDARDS and SECURITY are updated to match.
3. You ratify the charter in writing.
4. **Only then:** `git init`, package scaffolding, Phase 1 contract.

Nothing is scaffolded, initialised, or written as code before step 4.
