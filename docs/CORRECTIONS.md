# Corrections

Every claim that was wrong, who it came from, how it was caught, and what replaced it.

**The point of this table is that it is uncomfortable to write.** A project that claims its numbers
are checkable has to show the ones that were not. Errors are counted by source, separately, so
neither the director nor the AI can quietly absorb the other's.

**Source attribution is the director's, given at ratification**, and is recorded as given.

---

## Counts

| Source | Open | Closed | Total |
|---|---|---|---|
| Chat reviewer (draft author) | 3 | 0 | **3** |
| Research report (passed through unverified) | 2 | 0 | **2** |
| Stale-at-draft-time, queued but built on anyway | 1 | 0 | **1** |
| Director | 0 | 0 | 0 |
| Builder (Claude Code, this session) | 0 | 0 | 0 |
| **Total** | **6** | **0** | **6** |

All six were caught in Phase 0 source verification, before any code. None reached an artifact.
Entries stay **open** until the corrected text is committed in the ratified documents; they close
when the replacement is in place and verified.

---

## C-1 — svy's installable code was "not yet publicly downloadable"

| | |
|---|---|
| **Claimed** | Vision §8 TW-2: *"the review found svy's installable code was not yet publicly downloadable — so v1.0 defaults to `lean` estimators"* |
| **Actually** | `pip install svy==0.25.0` succeeded in a clean venv on 2026-08-28. Wheel and sdist both on PyPI. Version 0.25.0 uploaded **2026-08-26**, two days before the check. 48 releases. |
| **Source** | **Stale at draft time.** Installability was queued as a ruling item, and TW-2 was built on the stale finding anyway rather than waiting for the ruling. |
| **Caught by** | Phase 0 verification, by execution — installing it, not reading about it |
| **Severity** | **High.** It was the load-bearing premise under a tripwire and under the whole `lean`-estimator plan. |
| **Replaced by** | D-2 — `lean` retained, with the `httpx` zero-network dependency as the recorded rationale. Availability argument retired. TW-2 rewritten with a corrected baseline. |
| **Second finding, same check** | svy already implements Neyman allocation, Wilson, Clopper-Pearson, Korn-Graubard, logit intervals, Taylor variance, post-stratification and raking — most of the planned Phase 2. Positioning corrected in D-4. |
| **Status** | **OPEN** — closes when README credits svy as the estimator layer |

**The process lesson, and it is the one worth keeping.** A finding was queued for a ruling *and*
relied upon before the ruling came. That is the failure mode, not the stale fact. A claim awaiting a
ruling is not available for use as a premise.

---

## C-2 — "The timing is regulatory, and it is now"

| | |
|---|---|
| **Claimed** | Vision §2: *"EU DSA Implementing Regulation 2024/2835 requires harmonized transparency reports with accuracy indicators... There is no official tooling to compute those numbers."* Framed as regulatory demand for prevalence. |
| **Actually** | The word **"prevalence" appears zero times** in Regulation (EU) 2022/2065 and **zero times** in Implementing Regulation (EU) 2024/2835. No EU regulation requires a platform to report prevalence. What 2024/2835 mandates is accuracy, precision and recall of automated moderation. |
| **Source** | **Chat reviewer's draft** |
| **Caught by** | Phase 0 verification — mechanical count over both full official texts, retrieved from the EU Publications Office and corroborated against the director's own EUR-Lex PDF |
| **Severity** | **High.** Trivially falsifiable in one search, in a document whose whole premise is verifiability. |
| **Replaced by** | D-5 — inverted positioning: regulation mandates sensitivity/specificity; prevalence-kit shows what those do to the estimate |
| **Status** | **OPEN** |

---

## C-3 — "Wilson / Jeffreys ... matches Google's published practice"

| | |
|---|---|
| **Claimed** | Vision §4: *"Rare-event-safe intervals only (Wilson / Jeffreys ... this matches Google's published practice)"*, anchored on the Unofficial Google Data Science Blog, 2019 |
| **Actually** | Two errors. (a) The cited post **criticises** Jeffreys for this exact use case — it over-covers for rare events by shrinking toward 0.5 — and recommends the stratified Wilson interval. (b) The blog is **self-declared unofficial**, and the project's own Hard Rule 3 forbids sourcing a method from a tutorial. |
| **Source** | **Chat reviewer's draft** |
| **Caught by** | Phase 0 verification, reading the cited post. The **director independently flagged the source's provenance** in the same session, before seeing the finding. |
| **Severity** | Medium as statistics; **high as a rules breach** — the spine was broken on the first technical page. |
| **Replaced by** | D-8 — anchor Brown, Cai & DasGupta (2001), *Statistical Science*, DOI `10.1214/ss/1009213286`. Ship Wilson + Clopper-Pearson. Jeffreys dropped. Blog demoted to context. |
| **Status** | **OPEN** |

*Provenance note for the record:* the domain was checked and is genuine Google infrastructure
(NS `ns-cloud-d1.googledomains.com`, Blogger IP block, `www` CNAME `ghs.google.com`, TLS from Google
Trust Services). Not a lookalike. Still unofficial. The rule bites on *official*, not on *real*.

---

## C-4 — "KDD '26"

| | |
|---|---|
| **Claimed** | Vision §2 and §6: the Pinterest paper is *"arXiv 2602.18518, KDD '26"* |
| **Actually** | The paper's own header targets *"The 33rd ACM SIGKDD Conference on Knowledge Discovery and Data Mining; **August 2027**; San Jose, CA, USA"*. Its DOI field is the unfilled ACM template placeholder `XXXXXXX.XXXXXXX`. arXiv carries no `journal_ref`. It is a preprint formatted for KDD **2027**, and acceptance is unproven. Also, **v2 (2026-08-17)** exists and the vision cites only the February v1. |
| **Source** | **Research report — passed through unverified** |
| **Caught by** | Phase 0 verification, arXiv API and the paper's HTML render |
| **Severity** | Medium. Asserts a peer-review status no source supports. |
| **Replaced by** | D-6 — cite as arXiv preprint 2602.18518v2 (2026-08-17), formatted for KDD 2027 |
| **Status** | **OPEN** |

---

## C-5 — ROOST funding "$28M+"

| | |
|---|---|
| **Claimed** | Vision §2: *"ROOST (the major open-source T&S initiative, **$28M+** funding)"* |
| **Actually** | **The figure matches neither official ROOST source.** The launch press release (10 Feb 2025) says *"more than **$27 million** for its first four years of operations."* The ROOST blog post *First 100 Days* (4 June 2025) says *"an initial **$28.5 million** in funding **and in-kind contributions** from founding partners."* |
| **Source** | **Research report — passed through unverified** |
| **Caught by** | Phase 0 verification, launch release. The **second source, and therefore the conflict, was surfaced by the director** at ratification. |
| **Severity** | Low in magnitude; **the principle is the point.** Rounding a funding figure in a charter about verifiability is the exact failure the tool exists to prevent. |
| **Replaced by** | D-7 — cite the launch release with its date; footnote the blog figure; **record the conflict, do not resolve it** |
| **Status** | **OPEN** |

---

## C-6 — "Because every item is labeled, the TRUE prevalence is known"

| | |
|---|---|
| **Claimed** | Vision §7.3, describing the flagship coverage demonstration |
| **Actually** | Civil Comments labels are **`float32`** — `toxicity`, `severe_toxicity`, `obscene`, `threat`, `insult`, `identity_attack`, `sexual_explicit`, each the **fraction of human annotators** who applied it. **There is no binary ground truth in the dataset.** A "true prevalence" exists only relative to a threshold, and that threshold is our definitional choice. |
| **Source** | **Chat reviewer's draft** |
| **Caught by** | Phase 0 verification, reading the dataset schema rather than the dataset description |
| **Severity** | **High.** It would have sat on the README front page of a tool whose entire claim is that its numbers are checkable, asserting access to a ground truth that does not exist. |
| **Replaced by** | D-11 — pre-registered threshold estimand, hashed before data is touched; truth knowable **by census** at each threshold; demo extended to **multiple thresholds as a sensitivity curve** |
| **Status** | **OPEN** |

**This correction improved the deliverable.** The float labels became the demonstration's main axis
rather than a caveat buried in it.

---

## What produced these six

Recorded so the pattern is visible, not to assign blame.

| Pattern | Entries | The shape |
|---|---|---|
| A chat-drafted claim never checked against the thing it describes | C-2, C-3, C-6 | Three of six. All three were *plausible* readings of a real source, and all three were wrong about what the source says. |
| A figure passed through from an upstream report unverified | C-4, C-5 | Both are citation-shaped: a venue and a number, both copied rather than fetched. |
| A queued finding used as a premise before its ruling | C-1 | The most serious, and the only *process* failure rather than a fact failure. |

**Three of six were caught only by reading the primary source end to end** rather than checking that
it existed. Existence checks would have passed all six.

## Rule-14 obligation

Each correction that can become a failing test becomes one, rather than living in this prose:

| Correction | Check to build | Owner |
|---|---|---|
| C-2 | Overclaim scanner: fail the build if any published text asserts a regulation requires prevalence | Phase 3 |
| C-3 | Standards-register check: fail if any method cites a source not marked official in `STANDARDS.md` | Phase 1 |
| C-5 | Claim-search checker: find every restatement of a figure across files, per rule 14 | Phase 1 (O-7) |
| C-6 | Assert the coverage demo's estimand names an explicit threshold, and that the plan hash covers it | Phase 3 |
