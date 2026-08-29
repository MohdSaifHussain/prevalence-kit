# Phase 2 contract — the honest-statistics layer

**Status: APPROVED and UNBLOCKED — 29 August 2026. Q1-Q7 ruled.**
O-16, O-17 and O-18 discharged; the push and CI have happened. **D2.1 through D2.5 are done.**
**Q4 was found by D2.2 and ruled the same day — D-30.** See §10.

**Amended 2026-08-29, before D2.6, and the reason is the amendment's whole point.** A fresh session
read this contract against the rulings it is supposed to encode and found it disagreeing with them in
three places: the D2.6 row named **S-1.5** as its governing standard when **D-31** had ruled **S-1.6**;
§2.3 carried the same stale citation; and exit check **F8** still expected `CORRECTION_DEGENERATE`,
struck the same day, so as written it could not pass. **Building against a contract row that cites the
wrong paper is building against a wrong spec, and this contract is binding.** Q6 and Q7 are written in
at the same time, for the same reason — *a ruling that does not reach the binding document is not
binding.* Every change is marked ▸ **AMENDED** in place.

| | |
|---|---|
| **Phase** | 2 of 4 |
| **Name** | The honest-statistics layer |
| **Tier** | **STANDARD** — re-asked and discharged below, §9 |
| **Proposed** | 29 August 2026 |
| **Governing charter** | `PROJECT_CHARTER.md`, ratified 2026-08-28 |
| **Predecessor** | Phase 1 — closed 2026-08-29, commit `d66d225` |

---

## 1. Objective

**Make the statistics honest, and make an outside witness say so before we write them.**

Phase 1 proved the governance: pre-registration, sealing, a chain that refuses, a report an auditor
can check. It shipped exactly one estimator because the point was the spine, not the mathematics.

Phase 2 adds stratified sampling with Neyman allocation, the Clopper-Pearson interval, and the
Rogan–Gladen misclassification correction with its refusals. It also does something no earlier phase
could:

> **It brings in the first instrument in this project that neither the director nor the builder
> wrote.**

That sentence is the reason the phase is shaped the way it is, and §2 is about nothing else.

## 2. The witness comes first, and the witness is itself checked first

### 2.1 Why the usual order is wrong here

Twenty-three corrections have been recorded. **Not one came from an instrument with no author in
this room.** The builder's suite shares an author with the builder's code. The reviewer's harness
and probes read a contract the builder wrote — which is how C-21 and V-12's escape happened, and
why the director's hand-run, the closest thing to independent, still ran commands the reviewer
wrote.

R `survey` 4.5 is the first thing here with no author in this room.

So the fixtures are **not** a validation step at the end. **Each estimator is written against an
expected value that already existed before the estimator did.** A test cannot agree with an
implementation for the same wrong reason when the expected number predates the implementation.

### 2.2 The residual, and how it is closed

Inverting the order removes the shared author at one level and **not at the level above it.** The
builder writes the `svydesign(...)` call. A wrong call — wrong weights, wrong finite-population
correction, wrong strata argument — produces a wrong fixture that a correct estimator faithfully
reproduces, and the whole suite is green. The witness is external; **the invocation of the witness
is still the builder's.** That is every escape recorded so far, moved one layer out.

**It is closed with a published anchor, and the anchor comes before anything else.**

> **D2.1 is the first deliverable of this phase and it produces no estimator.** The first R fixture
> generated must reproduce **Barnett Table 2B** — allocations `2098 / 828 / 584 / 256 / 234`,
> population VVR `0.20%`, expected standard deviation `0.054 pp` — from Barnett Table 2A.
>
> If the R call reproduces a published number nobody in this project produced, the call is
> trustworthy. Only then does it become the witness for anything else.

Without that step the fixtures are the builder's reading of `survey`'s API dressed as an external
witness.

### 2.3 What the anchor does not cover — stated so nobody reads more into it

**Barnett validates the R invocation for the stratified / Neyman design only.** It says nothing
about the other two calls, which have no published anchor of their own in this project.

| Estimator | How its witness is itself validated |
|---|---|
| Stratified + Neyman | **Barnett Table 2B**, published, re-derived in Phase 0 §C6 |
| Clopper-Pearson | ~~**No published table.** Checked against an independent implementation we write.~~ **Corrected 2026-08-29, in our favour: there is an external witness.** `stats::binom.test` ships with base R and is a different lineage from `survey`. It inverts an incomplete beta; we root-find on the binomial tail. **S-2.4.** Worst disagreement 7.1 × 10⁻¹¹ across 23 cases |
| Rogan–Gladen ▸ **AMENDED** | ~~**Lang & Reiczigel (2014) worked results**, treated as the same kind of anchor and generated the same way.~~ **Restated 2026-08-29 under D-31, and both halves of the old row were wrong in our favour.** There *is* a library witness — `epiR::epi.prev()`, **S-1.10** — and the interval that matches our assumption is **S-1.6** Reiczigel et al. (2010), Se/Sp *known*, not S-1.5. **The narrowing is the point and it must not be lost:** Jenő Reiczigel is a listed contributor to `epiR`, so this is the method author's own implementation of the method author's own paper. **It confirms we implement the method as its author does. It does not independently confirm the method** — which is weaker than Barnett in a specific, named way. Obligation **O-8** |

## 3. Deliverables

Each names the top standard it must follow.

| # | Deliverable | Governing standard |
|---|---|---|
| **D2.1** | **The R witness, validated against Barnett before it witnesses anything.** A pinned R image, a script, and a committed fixture reproducing Table 2B. **No estimator code in this deliverable.** | **S-2.3** Barnett (2021) · `docs/PHASE-0-VERIFICATION.md` §C6 |
| D2.2 | R `survey` fixtures for stratified/Neyman, generated by the now-trusted call | S-2.1 `survey` 4.5 |
| D2.3 ▸ **AMENDED** | **Stratified sampling + Neyman allocation**, written against D2.2 | **Charter §6.2** · **S-2.3** Barnett, which pins the specification by reproduction · S-1.2 Neyman (1934) and S-1.3 Cochran 3rd ed. **as origin of the method, not as the source of our formula** — both write the optimum with the finite-population-corrected `S_h`, and ours is their large-stratum limit. **F-9**, ruled 2026-08-29 |
| D2.4 | Clopper-Pearson interval + its independent-implementation check | **S-1.1** Brown, Cai & DasGupta (2001) |
| D2.5 | Rogan–Gladen correction | **S-1.4** Rogan & Gladen (1978) |
| D2.6 ▸ **AMENDED** | Rogan–Gladen CI propagation, written against the **`epiR` fixture already committed under D2.5** — there are no "Lang & Reiczigel fixtures" and there never were. Clamped to [0, 1] under **Q6**, Clopper-Pearson only under **Q7** | **S-1.6** Reiczigel et al. (2010) · S-1.10 · O-8 · **D-31** · **Q6** · **Q7** |
| D2.7 ▸ **AMENDED** | **Refusals**: `Se + Sp <= 1`, ~~degenerate zero apparent prevalence~~ **(struck — see §6)**, an interval method the correction cannot honour (**Q7**), unsampled stratum, and any further undefined case found. **Two hunts ran, and both found something.** A **mutation sweep** over all 31 codes (swap each at every raise site, run the suite) found two nothing could distinguish — C-27, and the Q8 split came out of fixing it. A **boundary probe** across every estimator found **F-8**: `confidence` was unvalidated everywhere, so `wilson(5, 100, confidence=-0.5)` returned the inverted interval `[0.066846, 0.037230]` with its point estimate outside it, silently | Charter §6.4 · doctrine rule 5 |
| D2.8 ▸ **AMENDED** | Plan schema extension: `design: stratified`, strata definition, allocation method, **`allocation_rounding` (required under `stratified`, Q4 / D-30)**, optional `sensitivity`/`specificity`, and **`interval` (Q7 / D-33)**. **It discharges three related things at once and none of them counts without the others: O-20, O-22, and exit check F8d.** Both O-20 and O-22 are the same shape — a commitment honoured today by a required argument with no default, still owed as a field in the hashed plan. **Building one and calling D2.8 done would leave the other holding the line alone in the source**, which is the arrangement both obligations exist to end | Charter §4 `plan` · D-22 · **D-30** · **D-33** |
| D2.9 ▸ **DONE 2026-08-30** | `svy` cross-check **where its estimator is the same estimator** — which turned out to be **allocation only**. Every interval `svy` 0.25.0 offers is design-based, and **it maps the alias `clopper-pearson` to `korn-graubard`**, so D-18's finding about Wilson holds for all of them. Its `_neyman_allocation` **is** ours, largest-remainder rounding included: **2000/2000 designs identical**, all three shipped fixtures identical, exact ties identical. **The first genuine external witness the allocation has ever had** — F-9 established R `survey` has no allocator. Fixture committed, `svy` never installed here | **O-4 as narrowed by D-18** · **S-2.2** |
| D2.10 | Measure how far `svy`'s design-based Wilson diverges from the textbook interval at small *n* | **O-13** |
| D2.11 | CI wiring: fixtures in the gate, R image pinned by digest | S-6 toolchain |
| **D2.12** | **T-1.** Close every discharged correction, each naming the commit that discharged it | Tier trim, ruled 2026-08-29 |
| **D2.13** | **T-2.** Apply the decision-entry rule to the log, and state it in `docs/DECISIONS.md`. **The rule governs choices the builder makes alone. A question put to the director and ruled is recorded because it was ruled, whatever its operator visibility.** Without that line, Q3 — same CLI, same codes, invisible to an operator — would be suppressed by the first rule written to shrink the log, which is the one thing it must never do. | Tier trim, ruled 2026-08-29 |
| D2.14 | Extend `check_claims` to the new artifacts (fixtures directory, R script). **Two more gaps found 2026-08-29, ruled into this deliverable:** (a) `check_paths` does not cover either PDF — wrong directory prefix *and* wrong extension; (b) **the counts table in `docs/CORRECTIONS.md` is not covered by `check_figures`, and was updated by hand.** That is the count treadmill, in the table that counts our own counting errors. ▸ **The semantics are now written down — `docs/CORRECTIONS.md`, "What these columns mean" — so the check has a specification rather than a number to copy, ruled 2026-08-30. The table was derived and found over by one: C-36. What remains owed is the machine check.** The definition it must encode: an **entry** is a `## C-n` or `## V-n` heading, `Open` counts `Status: OPEN`, `noted` is excluded from Open and included in Total, and **a class tally is a different population from this table** — which is how the reviewer-instrument row reached 3. **(c) Ruled in 2026-08-29, by the director, from four stale rows found by reading: an open-items row naming an item the record says is discharged must fail the gate.** `CLAUDE.md`'s "Open, by name" table is a **live figure written in prose**, and nothing checks it. Its three machine-checked figures were current while four hand-maintained rows in the same file had drifted, **inside about six hours** — §6.1 (discharged by A-3), O-20 and O-22 (both moved at `d25e6fe`), and the corrections range. **The minimum condition: an obligation or correction identifier in an open-items row, whose owning record marks it discharged, is a failure.** The three figures are checked because they went stale once and nobody noticed; this table went stale the same way and was caught only by a session that read carefully. **That assumption is the one `check_figures` exists to remove** | D-23's stated limit |
| **D2.16** *(new, 2026-08-29)* | **`stratallo` fixtures. FIXTURE-ONLY — no new estimator.** A second independent witness for D2.3's stratified variance (`var_st` / `var_stsi`) and the **first** for D-30's rounding (`round_oric` / `round_ran`). Strengthens work already built at the cost of a fixture. **The `epiR` narrowing travels with it**: these are the algorithm authors' own implementation, so it confirms we compute what they compute and does **not** independently confirm the method | **S-1.12** |
| D2.15 | Discharge or restate O-3, O-14, O-15 | rule 11 |

**Not a deliverable, deliberately:** any change to how the report or CLI *renders* the new
estimators. That is the surface, and it comes after the review stop.

## 4. Requirements

**R2.1 — The witness is validated before it is used.** D2.1 completes and is approved before D2.2
begins. A fixture generated by an unvalidated call is not evidence.

**R2.2 — Every estimator is written against a pre-existing expected value.** The fixture is committed
first, in a separate commit, with the generating call recorded. If an estimator's fixture postdates
its implementation, the ordering that makes the witness independent has been lost and the deliverable
is not done.

**R2.3 — Agreement to ≥ 4 significant digits**, or the build is red. Where a method has no external
witness (D2.4), agreement is against an independent implementation, and the docstring says which.

**R2.4 — Every refusal gets a distinct reason code, a negative control and a positive control**, and
the number of codes follows **D-22**: count the artifacts an operator must open, not the situations.

**R2.5 — Rogan–Gladen refuses rather than printing a number it cannot defend.** `Se + Sp <= 1` makes
the estimator undefined; a degenerate apparent prevalence makes it meaningless. Both refuse by name.
**The refusal is the feature.**

**R2.6 — The R environment is reproducible by a stranger.** Image pinned **by digest**, not by tag;
R version, `survey` version and the exact call recorded in `docs/STANDARDS.md`. A local R install
would mean "it worked on my machine", which is the claim this project exists to stop making.

**R2.7 — Limits carry forward unchanged.** Charter §8 and `SECURITY.md` §3 are not narrowed by this
phase unless something genuinely narrowed, and then the change is stated.

**R2.8 — Plain ASCII, both ruff halves, mypy strict, and `check_claims` green** — the Phase 1 gate,
unchanged, plus the new fixture checks.

## 5. Out of scope

Named, so scope creep is visible rather than absorbed.

- **Anything that renders the new estimators** — report layout, CLI flags for stratified output. That
  is the surface and it follows the stop.
- The Civil Comments coverage demonstration — **Phase 3**
- Importance sampling, ML-assisted weights, Hansen–Hurwitz — **NEXT**
- `emit-dsa` — **NEXT**
- Beta-Binomial upper bounds — **NEXT**
- Label-quality estimation (kappa, alpha) — **NEXT**; this phase *consumes* Se/Sp, it does not
  estimate them
- Any release, tag, publish, or push to a remote

**If a feature wants a fifth phase, it goes to NEXT.** Charter §4.

## 6. Named refusals for Phase 2

Each gets a distinct code, both controls, and a message that says what to do.

| Code | Fires when |
|---|---|
| `CORRECTION_UNDEFINED` | `Se + Sp <= 1` — the Rogan–Gladen denominator vanishes or inverts. **Built in D2.5.** The witness itself shows why this cannot be printed rather than merely should not be: at Se 0.60, Sp 0.30 `epi.prev` returns a lower bound of 6.712724 above an upper bound of 6.459273 |
| `CORRECTION_OUT_OF_RANGE` *(added 2026-08-29)* | The corrected estimate falls outside [0, 1]. The Se/Sp pair and the sample are each fine alone and jointly impossible — **D-22's fourth case**, which is why it is separate from the row above: that one sends the operator to two numbers in the plan, this one to the relationship between the plan and the data. **Built in D2.5** |
| ~~`CORRECTION_DEGENERATE`~~ | **STRUCK 2026-08-29. The row was not merely redundant; it was wrong.** See the deviation note below |
| `STRATUM_UNSAMPLED` | A stratum in the plan received no sampled units |
| `STRATUM_EMPTY` | A stratum is defined but contains no frame units |
| `ALLOCATION_IMPOSSIBLE` | Neyman allocation cannot be satisfied — e.g. a stratum's allocation exceeds its size |
| `STRATA_UNDEFINED` | `design: stratified` with no strata definition |
| `ALLOCATION_TOO_THIN` | Neyman allocated fewer than 2 units to a stratum — zero within-stratum degrees of freedom, so its variance contribution is undefined. Q2. **Checked after rounding, not before** — D-30 condition 4 |
| `ALLOCATION_ROUNDING_UNDECLARED` ▸ **AMENDED** — **PENDING-CONTROL** until **D2.8** | `design: stratified` with no `allocation_rounding` field. The rounding rule is a commitment the operator makes, so it cannot be defaulted. **Q4 / D-30 condition 1.** **The specification is right and not yet built** (**Q9** / D-36): the plan schema cannot express the condition until D2.8, so today's raise site is a defensive branch that no valid `Rounding` reaches. Marked PENDING rather than struck — striking would lose the contract's promise in between, and `check_codes` expires the marker by machinery when D2.8 lands |
| `PLAN_FILE_MISSING` ▸ **AMENDED** *(**Q8** / D-35, 2026-08-29)* — **defensive, not operator-facing** | The plan file passed to `Plan.load()` is not there. **The CLI cannot produce this.** Every verb declares its plan argument as `click.Path(exists=True)`, so Click refuses first with a usage error and exit 2. This guards the **Python API**, which D-25 records as a real surface. Its fix text addresses a caller, not an operator. Classification pinned by `test_the_cli_refuses_a_missing_plan_before_our_code_runs` — relax the Click guard and that test fails, forcing this row to be re-read |
| `PLAN_SEAL_MISSING` ▸ **AMENDED** *(**Q8** / D-35, 2026-08-29)* | The **sealed copy** of the plan is absent from the run. **Artifact: the run directory.** Remedy: restore the run. This is what protects **D-15 check (a)**, the check that makes R5 provable rather than aspirational |
| ~~`PLAN_MISSING`~~ **SUPERSEDED** *(2026-08-29, **Q8** / D-35)* | Phase 1's single code for both situations above. **It had no control at either raise site** — C-27 — and D-22 says two artifacts means two codes. An operator who mistyped a path got a message telling them to restore their run directory: **worse than an undifferentiated refusal, because it sends them to the wrong artifact with confidence.** `docs/contracts/PHASE-1-CONTRACT.md` §4 still names it and **is not edited** — a contract is a dated document. `check_codes` reads the supersession from this row |
| `STRATUM_UNDECLARED` *(new, 2026-08-30, **Q14 / D-40**)* | A frame unit is in a stratum the plan does not declare. **S-1.13** makes strata *mutually exclusive* and covering, so these units cannot be dropped: the frame is the denominator, and dropping them changes it silently -- **V-7's class**. **A `.txt` frame under `design: stratified` lands here too**: it carries no `stratum` column, so every unit is undeclared. Same artifact to open, same remedial act, direction carried in the detail text -- **D-22**, on `PLAN_THRESHOLD_INVALID`'s precedent. Its converse is `STRATUM_EMPTY`, and the pair is complete: a declared stratum with no units, and a unit in an undeclared stratum |
| `ESTIMATE_METHOD_MISMATCH` *(new, 2026-08-30, **F-10**)* | `estimate.json` records a method that is not the one the hashed plan pre-registered. **Two artifacts in one run directory contradicting each other, with nothing comparing them.** This is F-10's **durable** half: dispatching `_estimate_from` on `plan.interval` makes them agree today, and **this comparison does not depend on the dispatch being right** -- it catches the next plan field that goes inert the same way. Raised in `verify`, before the recomputation, because recomputing runs through the same function and therefore reproduces the same wrong method |
| `DESIGN_NOT_ESTIMABLE` *(new, 2026-08-30)* | The plan's design draws correctly but cannot yet be estimated. Today that is `stratified`: `stratified_estimate` returns a standard error and no interval, and building one is **O-26** under **Q7**. **Refusing is the point.** The alternative is `_estimate_from` answering a stratified draw with SRS Wilson -- a number that looks fine, ignores the strata, and contradicts the design its own plan pre-registered. **A half-wired path that produces a number is worse than a refusal** |
| `CORRECTION_INTERVAL_UNSUPPORTED` ▸ **AMENDED** *(added 2026-08-29, **Q7**)* | The plan pre-registers `interval: wilson` **and** supplies `sensitivity`/`specificity`. A Wilson-transformed corrected interval has no pre-existing expected value, so R2.2 forbids shipping one — and silently handing back a Clopper-Pearson-based interval instead would substitute a method inside a pre-registered measurement, which is V-1's and V-7's class. **Refused at plan load, before any data is touched.** Built in **D2.6** |

*Under D-22, `STRATUM_UNSAMPLED` and `STRATUM_EMPTY` are separate because they send the operator to
different artifacts: the sample, versus the frame.*

**Q6, ruled 2026-08-29 — a clamped bound is disclosed, never silent.** The corrected interval is
clamped to [0, 1] at **both** ends. This is not a refusal and it gets no code, because the estimate
is defined and the interval is real; it is a construction the operator must be able to see. Three
binding conditions, in **D-32**: clamp both ends, **record in the output that a bound was clamped**,
and **record the raw bound in the ledger beside the clamped one** so `verify` re-derives both and an
auditor sees what the arithmetic produced before policy touched it. *A silently clamped bound is a
small lie in the artifact an outsider reads.*

**Deviation, 2026-08-29: `CORRECTION_DEGENERATE` struck.** This row said *"apparent prevalence is
zero or one, so the corrected estimate carries no information."*

**That is false in the one case this tool exists for.** Run against the witness at
`AP = 0, n = 4000, Se = 0.90, Sp = 1.00`, `epi.prev` returns a point estimate of **0** and an upper
bound of **0.001024**, with no warning. A rare-event measurement that finds no violations and reports
a defensible upper bound is not an absence of information -- **it is the product.**

Implementing the row as written would have refused the most common honest result in Trust & Safety
prevalence work.

Where AP = 0 or 1 *is* a problem -- an imperfect test, so `AP < (1 - Sp)` or `AP > Se` -- it is
already `CORRECTION_OUT_OF_RANGE`. So the row pointed at no artifact of its own in one direction and
was wrong in the other.

**Caught by running the witness, not by reading the contract.** Two codes remain:
`CORRECTION_UNDEFINED` and `CORRECTION_OUT_OF_RANGE`, and D-22's test decides them -- the first sends
the operator to the Se/Sp pair, the second to the relationship between the plan and the sample.

**36 reason codes in total**, across Phase 1's 23 and this phase's 13. Counted from `Reason` by
`tools/check_claims.py`, not maintained by hand -- the figure moved from the Phase 1 contract to here
when Phase 2 added codes and the checker went on reading the closed phase's number.

## 7. Review stop

**Placement: after D2.1 through D2.9 — the estimators and their refusals — and before anything
renders them.**

At the stop the builder will:

1. **Quote exact lines** proving the Barnett reproduction, the fixture-before-implementation
   ordering, and each refusal's condition. Not summaries.
2. **Hunt its own defects** against the charter, `docs/DECISIONS.md`, `docs/STANDARDS.md` and the
   Phase 1 corrections — specifically for the three named classes: wrong statement, wrong reporting,
   and a property proved in one artifact and assumed in another (**D-23**).
3. Report every finding with a proposed disposition and its evidence.
4. **End the report with what remains open, by name and severity** — C-12's standing rule.

**The director closes each finding. The builder never closes its own.**

## 8. Exit checklist

Expected results stated in advance. Commands are CLI invocations; the director runs them.

| # | Command | Expected |
|---|---|---|
| F1 | Run the R witness script | Reproduces Barnett Table 2B: `2098 / 828 / 584 / 256 / 234`, VVR `0.20%`, SD `0.054 pp`. **Exit 0.** |
| F2 | `git log` the fixture and its estimator | **The fixture commit precedes the estimator commit.** Proves R2.2. |
| F3 | `prevalence-kit plan` a stratified plan | Prints the hash. Exit 0. |
| F4 | Full chain on a stratified plan | Exit 0. **Read the report by eye:** do the per-stratum figures look sane? |
| F5 | Compare estimate against the R fixture | Agreement to ≥ 4 significant digits, printed. |
| F6 | Clopper-Pearson vs the independent implementation | Agreement printed; docstring names it as an implementation check, not a published anchor. |
| F7 | Rogan–Gladen with Se = 0.6, Sp = 0.3 (`Se + Sp <= 1`) | **Exit 2, `CORRECTION_UNDEFINED`.** |
| F8 ▸ **AMENDED** | Rogan–Gladen at zero apparent prevalence with an **imperfect** specificity — `pos = 0, n = 4000, Se = 0.90, Sp = 0.99` | **Exit 2, `CORRECTION_OUT_OF_RANGE`.** The corrected estimate is `-0.011236`, outside [0, 1] |
| F8b ▸ **AMENDED** | Rogan–Gladen at zero apparent prevalence with **perfect** specificity — `pos = 0, n = 4000, Se = 0.90, Sp = 1.00` | **Exit 0.** Point estimate `0`, upper bound `0.001024`. **This is the case `CORRECTION_DEGENERATE` would have refused, and it is the most common honest result in T&S work.** The struck code's whole defect, made runnable |
| F8c ▸ **AMENDED** | Rogan–Gladen where the corrected lower bound goes negative but the point estimate is defined — `pos = 8, n = 4000, Se = 0.90, Sp = 0.999` | **Exit 0.** Interval printed as `[0, 0.003267]`, **with the output saying the lower bound was clamped** and the ledger carrying the raw `-0.000151` beside it. **Q6 / D-32.** |
| F8d ▸ **AMENDED** | A plan with `interval: wilson` that also supplies `sensitivity` and `specificity` | **Exit 2, `CORRECTION_INTERVAL_UNSUPPORTED`**. **Q7 / D-33.** The refusal also carries the coverage trade-off in the operator's terms — **D-37 condition 1** — naming 90.98% and 85.32% as what Wilson actually delivers at rare-event rates |
| F8e *(new)* | A stratified plan with no `allocation_rounding` | **Exit 2, `ALLOCATION_ROUNDING_UNDECLARED`**, at `plan`. **O-20 at the plan file**, which is what D-30 condition 1 asked for |
| F8f *(new)* | A plan with no `interval` at all | **Exit 2, `PLAN_INVALID`** naming the missing key. **O-22 at the plan file.** Changing the interval **changes the plan hash**, so a published number carries its own evidence of which method produced it |
| F8g *(new)* | A stratified plan with `allocation_rounding` but no strata | **Exit 2, `STRATA_UNDEFINED`.** The design is loadable and the draw is not wired, so it **refuses rather than silently drawing SRS** |
| F9 | A stratified plan with an unsampled stratum | **Exit 2, `STRATUM_UNSAMPLED`.** |
| F10 | An empty stratum | **Exit 2, `STRATUM_EMPTY`.** Distinct from F9. |
| F11 | Rogan–Gladen with valid Se/Sp | **Exit 0** — the positive control. A gate that refuses everything proves nothing. |
| F12 | `pytest` | All pass; the count printed. |
| F13 | `ruff check` · `ruff format --check` · `mypy --strict src` | All exit 0. |
| F14 | `tools/check_claims.py --selftest` then without | Both exit 0; the selftest covers the new fixture checks. |
| F15 | `tools/check_tripwires.py --check` | TW-1/2/3 reported. **TW-2 is the live one** — `svy` was releasing weekly. |
| F16 | Verify the R image digest matches `docs/STANDARDS.md` | Identical. Proves R2.6. |

**F1, F2 and F7 are the phase's real product.** F1 is the witness proving itself; F2 is the ordering
that makes it independent; F7 is the refusal the charter calls a feature.

## 9. Tier — re-asked and discharged

**Ruling: remain at STANDARD.** Discharged 2026-08-29 by the director.

The standard was fixed before any evidence existed: FULL requires naming a concrete finding
attributable to a **FULL-only** practice. **Neither director nor builder can name one.** The verdict
rests on an absence, which needs no counterfactual, and **the gloss that FULL "would have found more"
is a claim about a run nobody performed** and is rejected here rather than left to be implied.

Where Phase 1's findings actually came from — **attribution corrected**, because a tier discharge
rests on which practice found what:

| Finding | Found by | Practice |
|---|---|---|
| V-1 (critical) | Reviewer role, adversarial execution at the stop | STANDARD |
| F-1 … F-7 | Builder self-review at the stop | STANDARD |
| V-2 … V-11 | Reviewer probes | STANDARD |
| **C-15** | **Reviewer, reading `examples/`** | STANDARD |
| **V-12** | **Builder**, after the director's transcript exposed that the reviewer's E8c and the contract's E8c were different actions | STANDARD |
| **V-13, V-14** | **Reviewer, verifying the builder's close report** | STANDARD |
| C-12, C-14, C-21 | Director | STANDARD |

*The builder's first draft of this table attributed V-13, V-14 and C-15 to the director's hand-run.
Corrected on the director's instruction. The conclusion is unaffected — all are STANDARD — but a row
nobody re-derived is a row that drifts, which is what twenty-three corrections have been about.*

### Phase 3's re-ask, written in now rather than remembered

**Phase 3 releases: a tag, a publish, and a pull request to someone else's repository.** It is the
first phase where FULL's distinguishing practice — **rehearsal of the irreversible** — has anything
to bite on.

**Forecast recorded in advance, before Phase 2's evidence exists:** the re-ask at the Phase 2 → 3
boundary **will not fire either**, for the same structural reason — Phase 2 ships nothing
irreversible. **The re-ask at the Phase 3 boundary must be taken seriously**, and this paragraph
exists so that is a scheduled decision rather than a remembered intention.

## 10. Carried obligations owned by Phase 2

| # | Obligation | From |
|---|---|---|
| O-3 | Record R version, `survey` version and the exact call beside every fixture | Phase 0 |
| O-4 ▸ **DISCHARGED 2026-08-30 by D2.9** | Cross-check against R `survey` (primary) and `svy` where the estimator is the same. **The narrowing did most of the work**: `svy`'s intervals are all design-based, so the overlap is **allocation alone** — and that is exactly where F-9 said we had no external witness at all. 2000/2000 agreement over a stated space, plus the three shipped fixtures and exact ties. **O-13 is separate and still open** — the magnitude of `svy`'s Wilson divergence is D2.10 | D-18 |
| O-8 ▸ **DISCHARGED 2026-08-29 by D2.6** | The point estimate was checked against all eleven `epiR` 2.0.92 cases (D2.5); the **interval** now reproduces all five accepted cases to **7.3e-13**, against R2.3's four significant digits. **The narrowing travels with the discharge and is not dropped by it:** `epiR` is the method author's own implementation of the method author's own paper, so this confirms we implement the method as its author does and **does not independently confirm the method**. Restated below as it stood before discharge. ~~Rogan-Gladen has no library witness; validate against Lang & Reiczigel (2014).~~ **Both halves were wrong in our favour.** There is a witness -- `epiR::epi.prev()`, **S-1.10** -- and the interval matching our assumption that Se/Sp are supplied and exact is **S-1.6** Reiczigel et al. (2010), not S-1.5. S-1.5 is the wider method we do not implement; adopting it would be a plan-schema change | D-3, restated by **D-31** |
| O-13 | Measure the `svy` Wilson divergence at small *n* | D-18 |
| O-14 | Keyless structural audit mode | V-10 |
| O-15 | Ledger schema version, **only if** an old run and an API-created run need different advice | D-25 |
| **O-16** | **DISCHARGED 2026-08-29.** R2's cross-version determinism is now *asserted*. Run `33204075014` printed an identical draw on **CPython 3.12.14 / 3.13.15 / 3.14.7**: `('item-0129', 'item-0089', 'item-0169', 'item-0027', 'item-0008')`. Verified by the director from the run log, not from the builder's table. **The first externally-produced evidence in this project's life.** | Phase 1 close |
| **O-17** | **DISCHARGED 2026-08-29.** The workflow has executed: `https://github.com/MohdSaifHussain/prevalence-kit/actions/runs/33204075014`, head `7f19bd9`, four jobs, all success. It is no longer a gate verified by reading. **Its first run produced V-16 and the `pytest -q` defect** — which is what a first execution is for. | Phase 1 close |
| **O-18** | **CLOSED 2026-08-29.** Decision 2011/833/EU permits reuse; Article 6(2)(a)'s source acknowledgement is the binding condition and the register satisfies it. **The closure covers Commission documents only** — Regulation (EU) 2022/2065 is a Parliament and Council act and is **not** covered. Boundary written into `docs/STANDARDS.md` S-4.3 so it travels with the clearance. | Phase 3 |
| **O-21** *(new)* | **The README must carry the rare-event specificity fact.** Charter section 8 now states it and `CORRECTION_OUT_OF_RANGE` says it to an operator who hits it. The README is where someone decides whether to adopt the tool at all, and this is the fact that makes its refusals read as judgement rather than fragility: 99% specificity sounds excellent and makes the correction undefined at 0.2% prevalence. | **Phase 3** |
| **O-20** *(new)* | **D-30 condition 1 is honoured at the API and not yet at the plan file.** `allocate()` takes `rounding` as a **required argument with no default**, which is what holds the line today: the rule cannot be a constant in the source. Still owed: `allocation_rounding` as a field in the hashed plan record, and `ALLOCATION_ROUNDING_UNDECLARED` refusing at load when a stratified plan omits it. Opened as a numbered obligation rather than a bullet in a report, because everything said in that report was true and the omission is what would have misled -- C-12's shape. | **D2.8** |
| **O-25** *(new, 2026-08-29)* | **D-37 condition 3: the report states the coverage of the interval actually used, at the operating point actually observed.** Not O-23's disclosure and not O-22's plan field — **a third thing, opened separately because two obligations living in the same post-stop surface is how one of them quietly does not happen.** If a run measures 0.2% with Wilson, the report says what Wilson's coverage is there. The plan records the choice; this records what the choice cost on this data | **Post-stop surface** |
| **O-24** *(new, 2026-08-29)* | **Every S-entry must carry a read state, checked by machine.** The sweep is done and recorded in `docs/STANDARDS.md`, but nothing stops a new entry being added without one -- which is exactly how S-1.1 stayed silent for two phases. `check_claims` should require one of `full` / `partial` / `not read` / `not recorded` per entry. **And it carries a distinction, not just a mechanism:** *a source that anchors an arithmetic can be validated by reproduction; a source that anchors a decision has to be read.* S-1.4 and S-1.6 are `not recorded` and that is defensible -- the Rogan-Gladen formula either reproduces against `epiR` or it does not. S-1.1 was dangerous precisely because it anchors a **choice**, and no amount of reproduction can check a choice | **D2.14** |
| **O-22** *(new, 2026-08-29)* | **Q7 / D-33 is honoured at the API and not yet at the plan file.** `rogan_gladen_interval()` takes `interval_method` as a **keyword-only argument with no default**, and `test_the_interval_method_cannot_be_defaulted` pins that, so the choice cannot become a constant in the source. Still owed: an `interval` field in the hashed plan record, and `CORRECTION_INTERVAL_UNSUPPORTED` firing **at `plan`** as exit check **F8d** specifies. **Exactly O-20's shape**, opened the same way and for the same reason -- everything built is real, and the omission is what would mislead if it went unnamed. C-12's class | **D2.8** |
| **O-23** *(new, 2026-08-29)* | **Q6 / D-32's conditions 2 and 3 are carried by the estimate and not yet by an artifact.** `CorrectedInterval.note` produces the disclosure and `as_record()` carries `low_raw`, `high_raw` and `clamped`. But **no Phase 2 estimator is wired into `run.py` yet** — it still calls `wilson()` alone — so nothing writes the raw bound to a ledger and nothing renders the note to a report. That is the surface, deliberately after the review stop (§5). **Named here so "the output discloses it" is not read as already true.** | **Post-stop surface work** |
| **O-28** *(new, 2026-08-30)* | **Before publication, the git history is reviewed, not only the working tree.** A repository's history goes public with it, and this one is **not rewritten** — the record cites commit hashes as evidence throughout, so the answer is a review **before** release rather than a repair after it. **This record was written for an audience of three**; Phase 3 is the first time it is read **as a stranger would** read it. The register's fourth rule and `CLAUDE.md` rule 20 govern what goes in from here; this is the one-time look backwards. **Must be written into the Phase 3 contract before the release** | **Phase 3** |
| **O-26** *(new, 2026-08-30)* | **The stratified interval builder, governed by Q7 / D-33 — the plan names the method, no default.** `stratified_estimate` returns a `standard_error` and **no interval**. Until it exists, the stratified path computes a quantity nothing turns into a printed bound, and how far a stratified interval diverges from the binomial inversion is **unmeasured**. Named because Q12 exposed it as a hole with no name | **Post-stop surface** |
| **O-27** *(new, 2026-08-30)* | **D-38's one-stratum disclosure.** The run records and the report states: one stratum, therefore **no precision gain** from stratification, and an interval resting on a **stratified variance basis** rather than a binomial inversion. **Separate from O-26 on purpose** — O-25's reasoning | **Post-stop surface** |
| **O-19** *(new)* | **Re-pin the CI actions before GitHub drops Node 20.** `checkout` v5.0.0 and `setup-python` v5.6.0, both two majors behind, both targeting Node 20. Watched by **TW-4**, which **fired on its first check**. | Phase 3 |

Each reported at close as **discharged**, or **unmet with a named blocker**.

## 11. Deviations and outcome

*Completed at phase close. Empty until then.*

---

## Numbered questions

The R route is settled and is not among these.

### Q1 — Does the stratified plan schema allow per-stratum Se/Sp, or one pair for the whole measurement?

Rogan–Gladen consumes sensitivity and specificity. Under stratification, label quality plausibly
differs by stratum — a high-risk stratum may be reviewed more carefully than a low-risk one.

| | Option | Consequence |
|---|---|---|
| **A** | **One Se/Sp pair for the measurement.** Per-stratum goes to NEXT. | Simplest. Matches what a small platform can actually estimate. Under-describes reality where review effort differs by stratum. |
| B | Optional per-stratum, falling back to the global pair | More faithful; more surface, more refusals, more to validate — and **no published anchor** for the stratified-corrected variance. |
| C | Per-stratum required when stratified | Most faithful, least usable: an operator who cannot produce five Se/Sp pairs cannot use the correction at all. |

**RULED: A.** The director's grounds are the charter's own §5.4 -- a method that cannot be
validated against an authoritative reference does not ship. Per-stratum corrected variance has no
anchor in the register, so R2.3 would have nothing to check it against. Adding an estimator we
cannot witness would undo §2's argument in the same phase that makes it.

**B goes into the NEXT queue by name**, so it is visible as deferred rather than absent. *An option
nobody wrote down is not deferred; it is forgotten.* It needs its own published anchor first.

### Q2 — Does `sample` refuse or warn when Neyman allocation gives a stratum fewer than 2 units?

Neyman can allocate 0 or 1 units to a small or low-variance stratum. With fewer than 2 units a
stratum has no within-stratum variance estimate, so the overall variance is undefined or
understated.

| | Option |
|---|---|
| **A** | **Refuse at `sample` time** with a new code, naming the stratum and the allocation, so the operator fixes the plan before spending label budget. |
| B | Allocate a floor of 2 per stratum automatically and record the adjustment | Silently changes the design the operator pre-registered. |
| C | Allow it, and refuse at `estimate` time | The operator has already paid for the labels. |

**RULED: A**, with the statistical reason **in the operator message, not only in the code.**

> A stratum allocated one unit has **zero degrees of freedom within that stratum**, so its variance
> contribution is undefined. That is why two is the floor.

An operator told *"stratum 3 was allocated 1 unit; a stratum needs at least 2 for its variance to be
defined"* can fix the plan. One told only that it was refused will guess. New code
`ALLOCATION_TOO_THIN`, both controls, naming the stratum and its allocation.

It fails before the label budget is spent, and labels are the expensive resource in this whole tool.
Auto-flooring silently rewrites a pre-registered design, which is V-1's class exactly.

### Q3 — Does Phase 2 keep SRS working unchanged, or fold it into the stratified path as a one-stratum case?

| | Option |
|---|---|
| **A** | **Keep SRS as its own path.** Stratified is separate code. | Phase 1's 222 tests keep testing what they tested. Some duplication between the two estimators. |
| B | SRS becomes "stratified with one stratum" | Less code, one path to validate. **Every Phase 1 SRS test now exercises a rewritten path**, so a Phase 1 guarantee could regress without any test changing — the C-15 class, at the scale of the whole estimator. |

**RULED: A.** The director looked for a third option before agreeing, and found one worth
recording.

**Alternative not taken:** fold, *but pin the current path's byte output as recorded values first*,
so a fixture proves equivalence rather than the tests assuming it. The codebase already has that
pattern in `test_draw_pinned_against_a_recorded_value`. It turns a risk judgment into a checkable
condition, which is rule 14.

Still ruled separate: the elegance is worth less than the phase boundary, and Phase 2 is already the
largest phase in this build.

**The condition under which this answer changes, stated now rather than reconstructed later: if a
bug is ever fixed in one path and not the other, that is the day to revisit.**

---

### Q4 — Rounded Neyman allocation does not always sum to n

Found by **D2.2**, not by reasoning: `rare_event_neyman_5000` asks for 5000, and raw
`3845.4104 / 884.2526 / 270.3371` floors to `3845 / 884 / 270` = **4999**. Barnett's case sums
exactly, so D2.1's anchor never met this.

| | Option | Consequence |
|---|---|---|
| A | Hand the remainder to a stratum, ad hoc | Rewrites a pre-registered design after the operator wrote it. V-1's class |
| B | Refuse | Fails **R8** — the tool cannot say what to do, since the only lever is `sample_size` and n+1 may not sum either |
| C | Deliver the real size | Plan says 5000, record says 4999, nothing reconciles them |
| **D** | **Largest remainder, named in the plan and hashed** | The allocation is *derived*, not rewritten. Nobody chooses anything after seeing data |

**RULED: D.** The director's grounds: option A's objection *"only holds if the choice is made ad
hoc. If the rounding rule is named in the plan, hashed before any data is touched, and fully
determined by the frame, then the allocation is not being rewritten — it is being derived, exactly
as the Neyman allocation itself already is."*

Six binding conditions in **D-30**. Sources pinned live before any code: **S-1.7** (U.S. Census
Bureau, which calls it *controlled rounding*), **S-1.8**, **S-1.9**.

**Two limits disclosed, and the second was found by obeying condition 5** — pin the source rather
than cite it from memory. Controlled rounding of Neyman is **not always the variance-minimal integer
allocation** (Wright's own counterexample), and largest remainder is **not monotone in n**. Both in
`docs/STANDARDS.md` under S-1.7. Neither is a reason to reject the ruling; both would have been
found later by someone else.

---

### Q6 — The corrected interval's lower bound goes negative while the point estimate is fine

Found by reading the D2.5 fixture before writing any interval code, not by reasoning. The
`rare_event` case — `pos = 8, n = 4000, Se = 0.90, Sp = 0.999` — has a corrected point estimate of
`0.001112`, comfortably inside [0, 1], so `rogan_gladen()` **accepts** it today. Its interval, from
the witness, is `[-0.0001514559, 0.0032669342]`. `epi.prev` prints the negative bound with no
warning.

This is a **third** rare-event surprise in this phase, after `fpr_exceeds_prevalence` and the
inverted interval, and the record anticipated neither this one nor the cluster.

| | Option | Consequence |
|---|---|---|
| A | **Refuse** | Wrong. The point estimate is defined, the upper bound is meaningful, and this is precisely the rare-event measurement the tool exists to produce. **A tool that refuses `pos = 8, n = 4000` at 0.11% prevalence has refused its own use case** |
| B | **Print the negative bound**, as the witness does | Nonsense on its face. An auditor who sees a negative prevalence stops trusting the surrounding numbers — **correctly** |
| **C** | **Clamp to [0, 1], and say so in the output** | Ruled |

**RULED: C.** The director's grounds, recorded as given.

**It is what this codebase already does.** `wilson()` computes `low=_fixed(max(0.0, centre - half))`
and has since Phase 1. Printing a negative lower bound for the corrected interval would make the tool
inconsistent with itself **in the one place a reader compares two of its intervals side by side.**

**It is safe in the way that matters.** The true prevalence cannot be below zero, so `[0, U]` covers
everything `[-ε, U]` covered. **Clamping cannot reduce coverage.** It makes the interval very
slightly conservative, which is the direction this project already chose when it picked
Clopper-Pearson as the conservative option.

**Three binding conditions, as ruled — see D-32.**

1. **Clamp both ends.** An upper bound above 1 gets the same treatment for the same reason, and the
   symmetric case will arrive.
2. **Record in the output that a bound was clamped**, so a reader knows `[0, U]` is a *construction*
   and not a *measurement*. **A silently clamped bound is a small lie in the artifact an outsider
   reads.**
3. **Record the raw bound in the ledger beside the clamped one**, so `verify` re-derives both and an
   auditor can see what the arithmetic produced before policy touched it.

**This is visible to an operator, so T-2 gives it a decision entry** with both alternatives and why
each loses. **D-32.**

**The cluster, recorded now so Phase 3 does not rediscover it.** Three rare-event surprises have now
landed in one phase: an ordinary-sounding specificity making the correction *undefined* rather than
imprecise; a witness returning an inverted interval; and a negative lower bound in the accept region.
When **O-21** reaches the README these are **grouped and introduced as one thing** — *at the
prevalence rates this tool is for, several ordinary intuitions fail, and here they are* — rather than
as three scattered caveats. That framing is worth more than the three separate sentences.

---

### Q7 — Wilson is the charter's primary interval, and the corrected interval has no Wilson witness

The fixture witnesses `epi.prev(..., method = "c-p")` only. Verified across all nine
positive-denominator cases: `RG(ap_lower) == tp_lower` and `RG(ap_upper) == tp_upper` to every printed
digit, so the witness builds the corrected interval by transforming a **Clopper-Pearson** interval on
the apparent prevalence, endpoint by endpoint. A **Wilson**-transformed corrected interval would have
no pre-existing expected value — an **R2.2** breach inside the phase built on R2.2.

| | Option | Consequence |
|---|---|---|
| A | Ship a Wilson-transformed corrected interval too | Breaches R2.2 in the phase whose whole shape is R2.2. Q1's argument exactly |
| B | Clopper-Pearson only, **noted in the docstring** | The builder's recommendation, and **not enough** — see below |
| **C** | **Clopper-Pearson only, and refuse rather than switch silently** | Ruled |

**RULED: C.** The recommendation was right and B was too weak.

**The director's grounds.** Charter §4 makes **Wilson primary**. If an operator pre-registers Wilson
and supplies Se/Sp, and the tool quietly produces a Clopper-Pearson-based corrected interval instead,
**the number they get is not the one their plan committed to.** Silently substituting a method inside
a pre-registered measurement is the class **V-1** and **V-7** were both about. A docstring does not
protect an operator who never reads it at the moment they need it — **D-20's reasoning, applied to an
interval instead of a threshold.**

**So: refuse at plan load.** New code `CORRECTION_INTERVAL_UNSUPPORTED`, both controls, and **R8 at
full strength in the fix text** — pre-register Clopper-Pearson if you want the correction, or drop the
Se/Sp and report uncorrected. **That converts a silent substitution into a decision the operator makes
before any data is touched, which is what pre-registration is for.**

**Alternative not taken: allow it with a loud note.** Rejected. A note is read once, at a moment the
operator has already decided; the plan hash is the commitment, and a commitment the tool routinely
substitutes a different method into is not one. The refusal is at `plan`, not at `estimate`, for Q2's
reason — **it fails before the label budget is spent.**

---

---

### Q10 - Should this tool own its missing-input refusals, or is Click's message the right one?

Raised by the director from the `PLAN_FILE_MISSING` finding, and it is wider than that one code.

Three arguments take an input file that must already exist: the plan, the frame, and the labels. All
three are declared `click.Path(exists=True)`, so **Click refuses first** and our own refusal never
runs. Measured 2026-08-29:

| Command | Who refuses | Exit |
|---|---|---|
| `plan <missing>` | Click | 2 |
| `sample ... <missing frame>` | Click | 2 |
| `ingest-labels ... <missing labels>` | Click | 2 |
| `verify --run <missing>` | **ours**, `RUN_NOT_FOUND` | 2 |
| `verify --plan <missing>` | ours, and a **deliberate skip** with exit 0 | 0 (D-24) |

So the tool has two refusal vocabularies and nobody chose that. The exit code is the same either
way, and Click's message is clear, so **nothing is broken today**.

| | Option | Consequence |
|---|---|---|
| A | Leave it. Click owns missing-input errors; our codes cover everything after the file is open | Simplest. Two vocabularies, but the seam is at a clean line: *does the file exist* versus *is its content usable* |
| B | Relax `exists=True` on all three, let our refusals speak | One vocabulary, every refusal has a reason code. Costs a clear standard message and touches three arguments |
| C | Relax it only for the plan | Worst of both -- the inconsistency becomes deliberate and unexplained |

**Not ruled. Owned by the post-stop surface work**, because it changes the CLI, which section 5 puts
after the review stop. Recorded now so it is a decision rather than an accident.

**`PLAN_FILE_MISSING` is classified defensive in the meantime**, which is true under option A and
would change under B.

---

### Q11 - Should Wilson stay the primary interval, given what its coverage does at rare-event prevalence?

**RULED: C. The plan names the method and there is no default. D-37.** Three conditions attached, and
charter section 4 needs amending -- drafted below as **A-4**, unapplied, for the director's ruling on
the text.

**Not a defect, and the director did not reopen the choice on a hunch.** It became answerable with
evidence rather than intuition, and the evidence was uncomfortable enough to be worth a ruling.

Charter §4 makes **Wilson** primary. This tool measures **rare events**. S-1.1 §4.1.1's published
analytic result puts Wilson's coverage at **0.838** against a nominal 0.95 at `p = 0.1765/n`, and
§3.2 gives `lim inf = 0.92` across the whole `gamma/n` regime. Clopper-Pearson guarantees at or above
nominal (§4.2.1).

**Measured by `r/coverage_fixtures.R`**, which validates itself against three of S-1.1's published
limits first. Worst coverage over `p = gamma/n`, **gamma in [0.5, 15] at step 0.25**:

*A worst-over-a-grid figure is a property of the grid, and states it like any other axis. A finer
grid can only find a lower minimum, so **every number below is an upper bound on the worst case**,
not the worst case. At step 0.05 the director measured **0.9537** for Clopper-Pearson at n = 1000,
conf 0.95, where step 0.25 reports 0.9540. Both are correct for their grid.*

| n | nominal | Wilson | Clopper-Pearson | Jeffreys |
|---|---|---|---|---|
| 100 | 0.90 | 0.8610 | **0.9022** | 0.8165 |
| 100 | 0.95 | 0.9102 | **0.9544** | 0.8806 |
| 100 | 0.99 | 0.9601 | **0.9912** | 0.9763 |
| 500 | 0.90 | 0.8540 | **0.9058** | 0.8129 |
| 500 | 0.95 | 0.9099 | **0.9521** | 0.9145 |
| 500 | 0.99 | 0.9596 | **0.9907** | 0.9741 |
| 1000 | 0.90 | 0.8532 | **0.9043** | 0.8125 |
| 1000 | 0.95 | 0.9098 | **0.9540** | 0.9141 |
| 1000 | 0.99 | 0.9596 | **0.9908** | 0.9738 |

**An operator asking for a 95% interval on rare-event data currently gets one that covers about 91%
of the time.** That is not wrong -- Wilson is a good interval and this is its documented behaviour --
but it is not what the number on the report says, and this tool exists so that the number on the
report means what it says.

| | Option | Consequence |
|---|---|---|
| A | **Wilson stays primary.** Record the coverage table in the honest limits and the README | No code change. The tool's headline number keeps a known gap between nominal and actual in its own target regime |
| B | **Clopper-Pearson becomes primary**, Wilson the second | The headline interval then honours its nominal level by construction. Wider intervals, and S-1.1 calls Clopper-Pearson *"wastefully conservative"* for general use -- though it adds *"unless strict adherence ... is demanded"*, which is this tool's whole posture |
| C | **The plan chooses**, with no default | Consistent with D-30 and D-33, where a commitment the operator makes is never defaulted. Costs an operator a decision they may not be equipped to make |

**Recommendation: B or C, and the director should rule.** The argument for B is that §4.2.1's
guarantee is the only one of the three that survives the regime this tool is built for. The argument
for C is that this project has twice ruled that a commitment belongs in the plan rather than in a
default.

**Whatever is ruled, the table goes in the honest limits and the README.** It is the most
decision-relevant fact this project has produced about its own output, and no reader would derive it
unaided.

---

## A-4 — DRAFT for the director's ruling. Not applied.

**What it changes.** Charter §4's `estimate` verb row, which currently reads:

> `estimate` | Compute prevalence with a correct interval — **Wilson** (primary) or
> **Clopper-Pearson** (conservative). Optional Rogan–Gladen correction when sensitivity and
> specificity are supplied. **Refuse with a named reason** rather than print a silently wrong number.

**Why it must change under Q11 / D-37.** The ruling is that the plan chooses the interval method with
no default. Under that ruling **neither interval is primary**, so the row describes a tool this is no
longer going to be.

### Draft replacement text

> `estimate` | Compute prevalence with a correct interval. **The plan names the method and there is no
> default** — `interval: wilson` or `interval: clopper_pearson`. Neither is primary, because the
> right one depends on what you are measuring and only you know that. Optional Rogan–Gladen
> correction when sensitivity and specificity are supplied. **Refuse with a named reason** rather
> than print a silently wrong number.

### And a new bullet under §8, honest limits

> **The interval you choose has a coverage cost, and at rare-event rates it is large.** A 95% Wilson
> interval covers about **91%** of the time when the true rate is a few times 1/n — the regime this
> tool is built for. Clopper-Pearson holds at or above its nominal level there, and is wider for it.
> Measured, not asserted: `r/fixtures/coverage.json`, against the published limits in S-1.1
> (Brown, Cai & DasGupta 2001) which the same instrument reproduces before reporting anything.
> **This is why the plan must name the method.** A default would be this project choosing, for an
> operator who did not know there was a choice.

### What the director should weigh before ruling

**The wording says "neither is primary" rather than silently dropping the word.** Charter §4 has said
"Wilson (primary)" since ratification, and a reader of the old text who returns should find out that
it changed and why, not just find the word gone.

**It does not name a recommended method, deliberately.** Naming one would recreate the default in
prose, which is what C removes. The honest-limits bullet gives the operator the number instead.

**S-1.1's own recommendation is not adopted, and that is worth the director's eye.** The paper
recommends Wilson or Jeffreys for n ≤ 40 and Agresti-Coull above. This project ships neither
Agresti-Coull nor Jeffreys, because R2.3 requires a witness and neither is in `survey` or `svy`. So
the charter would differ from its own anchor's advice, for a reason the anchor does not discuss:
**we validate against libraries, and the libraries constrain what we can ship.** If the director
would rather the charter say that out loud, it belongs here rather than buried in D-8.

---

---

### Q12 - Is a one-stratum plan a design error, or merely redundant?

**Raised 2026-08-29, unruled.** Recorded because it existed only in a chat window, and Phase 1 §10 is
what happens to things that live there.

**How it came up.** While designing the strata layer the builder wrote a refusal for a plan defining
fewer than two strata, on the reasoning that *"stratified sampling with one stratum is simple random
sampling with extra bookkeeping, and the record would claim a design the run did not use."* That
reasoning is the builder's. **It is the one strata decision that no source anchors.**

**The other two are anchored.** **S-1.13** (Statistics Canada, official methodology, read) gives:

> *"the population is divided into homogeneous, **mutually exclusive** groups called strata"*
> *"**independent samples are selected from each stratum**"*

Mutual exclusivity anchors refusing frame units in strata the plan does not define. Independence
anchors drawing each stratum separately. **Neither says anything about how few strata is too few**,
and the draft that refused at one was written before S-1.2 and S-1.3 were obtainable.

| | Option | Consequence |
|---|---|---|
| **A** | **Refuse a plan with fewer than two strata**, at `plan` | The record never claims a design the run did not use. Costs an operator who genuinely wants one stratum a rewrite to `design: srs`, which is the same measurement |
| B | Accept it, and record in the ledger that the design degenerated to SRS | Nothing is refused that is arithmetically fine — a one-stratum stratified estimate *is* the SRS estimate, with weight 1. But the plan then says `stratified` while the run did SRS, and reconciling those is the reader's problem |
| C | Accept silently | Rejected without argument. It is the silent-substitution class this project has refused three times — V-1, V-7, Q7 |

**RULED: B — 30 August 2026. Accept the one-stratum plan and disclose it. D-38.**

**S-1.3 was read before this was ruled, and it does not answer it.** §5A.7 poses three questions —
best stratifying characteristic, boundary placement, and *how many strata should there be* — and
hands the third to **§5A.8 *Number of Strata***, which was read in full. **Cochran states no
minimum.** His two questions are the rate at which variance falls as `L` grows and what a larger
`L` costs; his conclusion is an **upper** bound (little gain beyond `L = 6` unless the correlation
exceeds 0.95). **Table 5A.12 runs `L` = 2 to 6 and ∞ because `L = 1` is its denominator** — every
figure is `V(y_st)/V(y)`, normalised against the unstratified variance, ratio 1 by construction.
§5.1 defines stratification over `L` nonoverlapping exhaustive subpopulations with no constraint on
`L`. **S-1.2 goes further and includes `L = 1` explicitly** as the special case where stratified
sampling becomes unrestricted sampling.

So the question was a judgment call, **and it is recorded as ours rather than as a reading.**

**The builder recommended A and its load-bearing claim was false.** It argued that accepting is
*"V-1, V-7 and Q7's class exactly."* It is not: in all three of those **the tool did something the
plan did not say**, and here the plan says stratified and the tool runs stratified. Without that
parallel, argument 1 reduces to *an operator might be surprised* — **an argument for telling them,
not for refusing.**

**The precedent that applies is D-21**: de-duplicating the frame was correct, and doing it silently
was the defect. **Accepting is correct; accepting silently would be the defect.**

**Three reasons A lost.** Both anchors treat `L = 1` as admissible, so refusing asserts a rule
neither source supports — **rule 9's shape in a design decision**. The precedents do not reach:
`ALLOCATION_TOO_THIN` refuses **undefined arithmetic**, while a one-stratum design is fully defined
with 39 degrees of freedom at `n = 40`, and nothing here refuses the merely **pointless**. And it
would rule a permanent question on a **temporary state** — the builder's strongest fact was that
the stratified path returns no interval today, which is a gap in the interval builder, not a
property of `L = 1`. **Do not build a permanent refusal on scaffolding scheduled to come down.**

**What the evidence did establish**, and why disclosure is mandatory: option B's premise — *a
one-stratum stratified estimate **is** the SRS estimate* — is **true of the point estimate and false
of the variance**. At `n = 40`, 9 positives: both give `0.225`, but the stratified path returns
`s^2 = 0.178846`, **SE `0.066867`**, df 39, while SRS inverts a binomial to Wilson
`[0.123161, 0.375031]`. **The 2.92 pp gap quoted in the ruling is a constructed comparison** — a
normal approximation the builder put on that SE to show the bases differ — and **no such interval
is shipped**. What is proven is that the two paths compute different quantities. **O-26** and
**O-27** carry the builder and the disclosure.

## Approval

- [x] Director approves this contract — **29 August 2026**
- [x] Q1, Q2 and Q3 ruled
- [x] **Unblocked 2026-08-29.** O-16 and O-17 discharged. R2's cross-version determinism is
      *asserted*: run `33206373461` drew an identical sample on CPython 3.12.14, 3.13.15 and 3.14.7.
- [x] **Q4 ruled — 29 August 2026.** Largest-remainder rounding, named in the plan. **D-30**, six
      binding conditions. Found by D2.2, which is what generating fixtures before estimators is for.

**Approved and unblocked. D2.1 and D2.2 are done; D2.3 begins.**
