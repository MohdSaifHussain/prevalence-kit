# prevalence-kit — orientation for the next session

Audit-grade prevalence measurement for Trust & Safety. You give it a sampling plan and human labels;
it returns an estimate, an honest interval, sealed content, a tamper-evident record, and a stamped
report. **No AI ever touches the evidence or the estimate.**

This project runs the **governed-orchestration** skill at **STANDARD** tier, manual-approve.

**Phase 3 of 4 in progress.** The contract is APPROVED, **Q1–Q25 ruled** (Q16–Q25 on
2026-08-31). Tier: STANDARD by the re-ask's first live ruling, D-42. Next: D3.1 (O-19), then the
coverage demonstration; nothing public before O-28 closes.

> **First action of every session: invoke the `governed-orchestration` skill.** Do not wait to be
> asked. The director had to remember it last session, and a handoff that depends on him remembering
> is not a handoff.

## The three roles

- **Director** — Mohd Saif Hussain. Rules on every judgment call, runs the phase-close ritual by
  hand, gates every push. The tiebreaker.
- **Builder** — you. Read the record, plan, ask, build, self-review adversarially, stop at gates.
  **You never close your own findings.**
- **Reviewer** — a separate session with its own probes and harness. **Wrong six times.** For five of
  them the pattern was *what the contract's action is, never what the code does*. **C-26 broke that**:
  a finding manufactured by a summarising fetch tool that dropped a character. Any character-level
  claim from a summarising fetch is unreliable — go to the raw API and read codepoints.

## Read these, in this order

| File | What it is |
|---|---|
| `PROJECT_CHARTER.md` | **Binding.** Scope, six verbs, hard rules, honest limits. **A-0 … A-6 all applied.** §8's honest limits are a deliverable, not a footer |
| `docs/contracts/PHASE-2-CONTRACT.md` | **CLOSED 2026-08-31.** Q1–Q15 ruled, D2.1–D2.17 done. **§11 is the outcome; §8a is the checklist the director ran and §8b amends it.** Read §11's carried table before planning Phase 3 |
| `docs/contracts/PHASE-2-HAND-RUN.md` | **The exit evidence, and a dated reading — never edited.** 34 rows run by the director. Two were wrong and both were the builder's |
| `docs/DECISIONS.md` | **D-1 … D-51.** Why each choice, and what was rejected. **T-2's admission rule is at the head** |
| `docs/CORRECTIONS.md` | Every claim that was wrong. **Counts claims that reached a commit *or changed a ruling*** |
| `docs/FINDINGS.md` | Findings register. `check_claims` reconciles it against the code |
| `docs/STANDARDS.md` | Every source pinned by version, date, digest or DOI. **S-8 pins the retrieval *procedures* too** |
| `docs/contracts/PHASE-1-CONTRACT.md` | Closed. §10 is the outcome |
| `SECURITY.md` | Threat model. §3 is the limits, carried forward unchanged |
| `TIME-LOG.txt` | Append-only wall clock. Stamp on request |

`docs/contracts/PHASE-1-REVIEW-STOP.md`, `docs/contracts/PHASE-2-HAND-RUN.md` and `docs/RULINGS-QUEUE.md` are **dated readings — never edited.**
Corrections to them go in `docs/CORRECTIONS.md` with the date and the direction the number moved.

## The gate is seven checks, not four

**A machine reads this block.** The `gate` check in `tools/check_claims.py` reads it, then checks
that `.github/workflows/gate.yml` runs every line. One command per line. Nothing else in the block.

Before V-16 these were two lists that had to agree, with nothing making them agree.

```
ruff check .
ruff format --check .
mypy --strict src
mypy
tools/check_claims.py --selftest
tools/check_claims.py
pytest
```

`mypy` on its own is the **config form**. It covers `src` *and* `tests`. **Re-derived at this
checkpoint:** `--strict src` reads **14** files, plain `mypy` reads **36**. Both numbers move as the
phase adds modules — re-derive them, do not carry them. The 12 written here an hour earlier was
already stale.

Until V-16, CI ran only the first one. The test files were never type-checked on the remote.

**Never `pytest -q`.** `pyproject.toml` already sets `addopts = "-q"`, so `-q` is `-qq` and
suppresses the count. E11 exists for that count.

Run **all seven** after any scripted edit, not the half that looks affected. Use
`.venv\Scripts\python.exe`.

`tools/check_tripwires.py` is offline by default; `--check` reaches the network. It is a phase-close
ritual, not a CI job — a tripwire firing is a decision for the director, not a red X. **Five
tripwires now; TW-4 is FIRED and stays fired until O-19 is acted on.**

**The suite takes ~53s locally and ~10s in CI. That is not a defect** — profiled 2026-08-29: the time
is Fernet sealing plus real filesystem writes in the Phase 1 tests, and Windows pays for both. The
Phase 2 arithmetic tests are nearly free.

**Re-profiled 2026-08-30, because it had reached 150s and a number nobody has re-derived is a
number to distrust.** It was **not** quadratic: `verify` is **linear in n**, at about **13.7 ms
per sealed item** — 0.57s at n=40, 5.50s at 400, 54.94s at 4000, measured. One test I had
written verified a **4000-item** run to prove that emitting a report does not break the chain, a
property that has nothing to do with n, and cost **55s on its own** — a quarter of the suite.
Seven more rebuilt the same 4000-item chain to read one string each.

**Fixed at the cause rather than by marking anything slow.** The clamp arithmetic genuinely
needs `8 / 4000`, so that chain is built **once** in a module fixture and shared; every test
whose property is independent of n uses a small run. **150s to 53s**, no assertion weakened and
no coverage dropped. *If it climbs again, profile before assuming — last time the cause was a
fixture choice of mine, not the code.*

## The witness — read this before touching a fixture

Phase 2's whole shape rests on **numbers that existed before the code that reproduces them** (R2.2).

- **The image** is `rocker/r-ver@sha256:c3f39b36…c21c0`, pinned by **digest**, S-2.1a. A tag moves; a
  digest does not.
- Its CRAN mirror is frozen at **2026-04-23**, so `survey` 4.5, `epiR` 2.0.92 and `jsonlite` are
  deterministic. **`epiR` 2.0.92 is not a typo for the 2.0.96 on CRAN** — the snapshot predates it,
  and the Dockerfile asserts the version so a bump cannot pass silently.
- Run it with `bash r/run-witness.sh`. It refuses unless `r/Dockerfile` and S-2.1a carry the same
  digest.
- Fixtures live in `r/fixtures/`. **`tests/test_fixtures.py` checks them in the gate** — digest
  against the pin, every declared verdict against the arithmetic, and that epiR's estimate really is
  the Rogan-Gladen formula. It does **not** catch a fixture with a right digest and hand-edited
  contents. That is D2.11.

**What the witnesses establish, and what they do not.** Barnett Table 2B is a published table
computed without reference to any implementation, so reproducing it tests our arithmetic against a
number nobody in this chain computed. **`epiR` is different in kind**: Jenő Reiczigel is a listed
contributor, so it is the method author's own implementation of the method author's own paper. It
confirms we implement the method as its author does. It does not independently confirm the method.

## Rules that have actually bitten here

1. **No code without a ruling.** Contract before build; numbered questions with options and a
   recommendation; the director rules.
2. **Green tests prove self-consistency, not meaning.** C-16 was found by a person reading the
   report, with every test passing and the checker reconciling.
3. **Every gate gets both controls and a distinct reason code.** How many codes? **D-22**: count the
   artifacts an operator must open, not the situations.
4. **Re-derive numbers from the artifact.** Four corrections are figures nobody re-derived, and
   C-24's was printed on screen at the time.
5. **End every report with what remains open, by name and severity.** C-12 is what happens otherwise.
6. **A finding closed in one artifact can be open in another** — D-23.
7. **A check covers less than it looks like it covers.** Ten times now: C-15, C-19, V-15, V-16,
   C-23, `check_codes` reading one contract when there were three, D-34, C-27, **C-34**, and
   **F-9**. Ask what it does **not** read, in both directions. **C-34 is the worst kind: a checker
   that *stated* a scope it did not have.** No stated scope invites the question; a wrong one
   answers it falsely, and the reader comes away more confident and less correct. **Make the scope
   the object the code walks, never a sentence beside it.**
   **The SEVENTH kind leads the list, and it is the one to put in front of a reader before any
   passing number: `verify` recomputes through the function it is checking.** `verify.py` calls
   the same `_estimate_from` that produced the number, so when that function ignored
   `plan.interval` it reproduced the same wrong method and reported the estimate verified. **It
   has produced a live defect twice, and neither time was it caught by an instrument** — F-10 was
   found by reading the code and asking what reads a field. Q-2 named this unclosable at Phase 1
   and it still is: no test the builder writes can close *the suite is the builder's*.
   **F-9 is the sixth kind and it lies about nothing: a fixture that looks external and is not.**
   `r/fixtures/stratified.json` holds allocation fixtures made in the pinned R image — but
   **`survey` has no allocator**, so those rows are our own formula re-implemented in R by its own
   author, sitting beside estimation fixtures that really are external. Every document is honest;
   the R script says it in its own comment. **What misleads is the company the fixture keeps.**
   A reader checks the provenance of the file, not of the row. **Ask which rows in a witness file
   the witness actually produced.**
8. **A worst case measured over a grid is an *upper bound* on the worst case, and a bound is
   rounded in the direction that keeps it true.** A finer grid can only find a more extreme
   value, so state the grid step like any other axis — 0.9540 at step 0.25, 0.9537 at 0.05, and
   **keep both**, because two grids disagreeing is evidence about the measurement.
   **Rounding to nearest is right for a measurement and wrong for a bound**: it rounds toward
   the middle and silently weakens a claim about everything outside your sample. *"As little as
   91%"* is false when the measurement is 0.9098 — **C-32**, the director's, in the charter.
   The sweep it prompted found two more, both ours and both flattering: **C-33**.
9. **A negative claim about the world records the search that produced it.** *"Not in `survey` or
   `svy`"* is a finding. *"No witness exists"* is a claim about all of CRAN and PyPI, and this
   project has made it three times and been wrong three times, always in our favour — O-8 vs
   `epiR`, §2.3 vs base R `binom.test`, and the charter's NEXT queue vs **`stratallo`, which was
   already inside our pinned snapshot.** Same root as rules 8 and 10: **a claim whose scope is
   the sample you took, stated as though it were the population.**
10. **A checked number can carry an unchecked claim.** *"23 reason codes, each with both controls"*
   looks like one verified sentence. A machine counted the 23. Nothing checked "each with both
   controls", and it was false — C-27. Same shape in C-28. This is worse than a plain unchecked
   claim, because the half you can verify makes you stop looking. **Check the property, or split
   the sentence.**
11. **A test asserts a defining property, or a measurement with stated scope. Never a region.**
   A defining property is true by construction — *Clopper-Pearson covers at least 1 − α*, and
   S-1.1 §4.2.1 says so. A region description — *narrower where k ≤ 1* — is a summary of the
   grid you happened to sample, and it will be wrong at the corner you did not. **C-30(c) was
   wrong three times** before the width test was deleted and replaced by a coverage test.
12. **Check an artifact the way its real consumer reads it.** Structured files — YAML, JSON, TOML,
   CSV, XML — get the **consumer's parser**, never a regex. That is how an unparseable `gate.yml`
   passed a green checker (**C-23**). **Markdown is the exception**, and the reason is the rule: its
   consumer is a human, who reads it loosely too.
13. **"The guard did not object" is not "the guard looked."** Know what each check does *not* read,
    and assert that scope rather than describe it.
14. **A check with no artifact is a memory with a result attached.** The fixture verdict check ran
    once as a `python -c`, was reported as "machine-checked", and left no trace. **The suite count
    not moving is what exposed it** — which is why the gate prints its own count.
15. **The witness's documentation is not the witness. Only the pinned build is.** C-25: the manual
    on CRAN described a version we do not run.
16. **Re-run the whole gate after anything that writes to the working tree, and report *that*
    run.** C-29: a mutation loop ended with `git checkout --` on a file whose real edit was
    still unstaged, so it reverted the edit. The gate had been green before the loop. I
    reported those numbers after it, and committed a tree that failed 3 tests.
17. **A source that anchors an *arithmetic* can be validated by reproduction. A source that
    anchors a *decision* has to be read.** S-1.4 and S-1.6 are unread and that is fine — the
    Rogan-Gladen formula either reproduces against `epiR` or it does not. **S-1.1 anchors a
    choice**, and no reproduction checks a choice. It went unread for two phases. O-24.
18. **A source's text is for reading, never for committing.** The director supplies papers so
    the builder can learn from them. **They do not enter the repository** — not as a quote of
    any length, not as a PDF, not pasted into a doc. Cite them: title, authors, journal, DOI.
    Bibliographic metadata is not the work. **The one tracked PDF is an EU official text**,
    cleared for reuse under Decision 2011/833/EU with the acknowledgement O-18 requires — that
    is a licence, not a precedent for papers.
19. **Never delete or overwrite the director's working directories.** `C:\Users\mohds\ts-sentry` is
    read-only. **Never remove a Docker image** — they belong to the director's other projects.
20. **How a source was obtained is not recorded.** The register carries the **citation**; whether
    the artifact is the **publisher's copy**, where that was in question; the **read state with
    its scope**; and any **route that changes what was read** — a rendered scan is not a text
    layer, and that difference belongs in the register. **It never carries who supplied a source
    or how it arrived.** Rule 18's sibling: 18 keeps the *work* out of the repository, 20 keeps
    the *acquisition* out. Rule 17 asks you to read a source and this one bounds what reading it
    may put on the record. **The line is not "no routes":** Cochran is read as locally rendered
    images and the register says so, because that **changes what was read**. Where a copy came
    from does not. **Every other entry already works this way** -- S-5.2 is *fetched 2026-08-28,
    HTTP 200*, S-2.1 is *4.5, re-verified live 2026-08-29* -- and none is weaker for it. **C-37**:
    the field was invented, not merely mis-filled, so the fix is that it does not exist.

21. **A control that fires for the wrong reason is a control that has not been built.**
    Ruled 2026-08-30. Every gate needs a negative control, and the control has to reproduce **the
    state the defect actually produced** — not a state that merely makes the check go red.
    `ESTIMATE_METHOD_MISMATCH`'s first control edited `estimate.json`, which trips
    `LEDGER_BROKEN` **first**: green-to-red, proving nothing about the thing under test. The real
    defect was a **broken writer** — every digest honest, the dispatch wrong — so the control
    breaks the dispatch and writes an honest run. **Ask what the control would catch if the check
    it belongs to were deleted.** If the answer is "something else", it is testing a neighbour.
    The same reading of C-27's mutation sweep: a code nothing could distinguish still *fired*.


## Where things stand

**Phase 0** ratified. **Phase 1** closed at `d66d225`. **Phase 2 CLOSED 31 August 2026**,
ruled by the director. **Questions 1–15 ruled in that phase**, **A-0 … A-6 all applied to the
charter**, **D2.1 … D2.17 done.** Phase 3's Q16–Q25 were ruled 2026-08-31, at the boundary.

**The exit evidence is not the builder's.** It is `docs/contracts/PHASE-2-HAND-RUN.md` — the
director's own run of §8a's **34 rows**, every command by his hand — plus the reviewer's
independent verification of `d5741dd`. **32 rows behaved as stated. Two did not, and both were
the builder's**: F4 expected report output that had never existed, F9 named a refusal no command
can reach. **F4's wrong expectation is what surfaced F-12.**

**Phase 2's two worst defects were found by people, not instruments.** **F-11** at the review
stop, by a probe the director named; **F-12** at the phase close, by the director reading a
report by hand. In both, `verify` returned exit 0 — it recomputes through the estimator that
produced the number, which is Q-2 as a live failure rather than a caveat.

**The exit checklist was replaced before the hand-run, and that is the last thing that
happened.** Contract §8 covered the phase as it was, not as it is: it named nine reason codes
and omitted `EVIDENCE_NOT_PREREGISTERED`, `ESTIMATE_METHOD_MISMATCH`, `STRATUM_UNDECLARED` and
`INTERVAL_UNDEFINED`, so **the hand-run would have certified Phase 2 without ever exercising
F-11** — and the hand-run is the only instrument here that is not the builder's. **§8a
supersedes it**, approved 2026-08-30, every command run before it was written. §8 is left
unedited: it is a dated part of a binding document.

**The director's own addition to it found one more.** Nothing in the draft ran `verify` — the
verb whose `yes` is the entire product — so **F25** does. Writing that row exposed that
`verify`'s `sample` line read *"redrawn from the frame, identical"* for **both designs**, so a
reader could not tell a stratified redraw from a simple random one. `verify.py` redraws by
design (F-10's third site) and **its output was silent about what it had checked.** It now
names the draw.

**Repository:** `github.com/MohdSaifHussain/prevalence-kit`, private. **734 tests**, seven gate
checks green — **`check_claims` now runs twelve**, not seven; the gate block below is still
seven commands. **CI last ran green at 734** on the 3.12 / 3.13 / 3.14 matrix, run `33345614816`, head `03a0c7b` — the Phase 3 boundary commit, all three legs at 734, matching local. They are stated apart because they are two measurements, not one.
A second workflow, `witness.yml`, rebuilds the R image and requires every fixture to regenerate
**byte-identically** — it runs on `r/**` changes and on demand, not on every push.
Local and CI figures are stated apart on purpose.

*The exact patch versions are **not** carried here any more. The previous line said
`3.12.14 / 3.13.15 / 3.14.7`, and that run's log does not print a `Successfully set up CPython`
line, so re-deriving them from the artifact was not possible. **Quoting the old ones would have
been C-7's class** — a number carried rather than re-derived. The matrix keys are what the run
proves.*

**Three of these figures are machine-checked** — the test count, the highest ruled question,
and the phase — because this file went stale within hours of being written and nothing noticed.
A stale README misleads a reader; **a stale CLAUDE.md misleads the next session before it has
read anything else.** `check_figures` derives all three.

> **The phase figure was the weakest of the three and is now the strongest, because it broke
> in both directions at once.** `README.md` said *in progress* after Phase 2 closed and the
> check **passed** -- it compared the number to the highest contract and never read the word.
> `CLAUDE.md`'s version had no true form once the phase closed, so its sentence came out and the
> claim **went silent**. One canonical sentence now serves both files, `Phase N of 4 in progress`
> or `complete`; the state is derived from the contract's own close line; and **absence is a
> failure**, so deleting the sentence cannot silence it. **C-47.**

### Done in Phase 2 — kept as history, and the closed contract is the authority

**This table is not the record.** `docs/contracts/PHASE-2-CONTRACT.md` §11 is, and it is closed.
These rows are here so a reader knows what exists without opening it.


| | |
|---|---|
| **D2.17 / O-26** | **The stratified intervals.** `design_wilson` and `design_korn_graubard`, witnessed by `svy` to **4.9e-13**, fixtures committed first at `e04a7aa`. **Neither holds nominal coverage at rare rates** — worst conditional 0.7472 (KG) and 0.0000 (Wilson) against 0.90 — and A-6 carries the figures to §8 |
| **O-25 / O-27 / D-41** | **The three disclosures.** The report states what the chosen level actually delivers -- the measured coverage of the method used, the grid it came from, and **where this run sits on both axes**, because a worst case at n = 1000 does not bound n = 40. A one-stratum run says stratification gained it nothing. The no-interval odds are **stated, not refused** (D-41) |
| **A-6** | **APPLIED.** Three interval names, not four. `design_clopper_pearson` was renamed **before it shipped** because the name promised coverage at or above nominal and the measurement says 0.7472 against 0.90. Charter §8 carries the 96-point table, and `tests/test_coverage_disclosure.py` **re-derives every figure in it** from the shipped estimators -- the measurement had lived only in a commit message and three docstrings |
| **D2.16** | `stratallo` witnesses the **rounding** — 3/3 fixtures, 2000/2000 sweep — and **not** the variance, which is the without-replacement form. Fixture only |
| **D2.14** | All four conditions. `check_claims` runs **twelve** checks; `counts`, `schema`, `open-items` are new. **Two fired on their first run** |
| **D2.12 / D2.13** | T-1 and T-2. **41 of 44 corrections closed**, each naming its discharging commit |
| **D2.11** | `witness.yml` — the R image rebuilt by machine, fixtures regenerated byte-identically, both directions |
| **D2.10 / O-13** | `svy`'s Wilson divergence measured: interior worst **0.117330** at n=10, **9.7e-05** at n=1000. At `k = n` svy returns a **zero-width** interval; at `k = 0`, none at all |
| **D2.9 / O-4** | **`svy` witnesses the allocation and none of the intervals.** It maps `clopper-pearson` to `korn-graubard`. 2000/2000 designs identical |
| **D2.1** | R witness reproduces **Barnett Table 2B** — `2098/828/584/256/234`, VVR 0.2000%, SD 0.0539 pp. `svydesign` SE against the closed form: 4e-16 |
| **D2.2** | 4 allocation + 5 estimation fixtures from `survey` 4.5, through the one validated call |
| **D2.3** | `stratified.py` — Neyman, largest-remainder rounding, stratified estimator. Worst disagreement with `survey`: **9.5e-15** |
| **D2.4** | Clopper-Pearson **from its definition** — binomial tail in log space, no incomplete beta anywhere. Witness: base R `binom.test`. **8.4e-11**, across n = 1…1,999,514 **and** confidence {0.90, 0.95, 0.99} |
| **D2.5** | Rogan-Gladen point estimate, 11 cases from `epiR`. Two refusals, both controls |
| **D2.6** | Rogan-Gladen **interval** — the corrected bounds are the apparent Clopper-Pearson bounds transformed endpoint by endpoint. Against `epiR`: **7.3e-13**. **O-8 discharged.** Clamped both ends (Q6/D-32), Clopper-Pearson only (Q7/D-33) |
| **D2.7** | Refusals proved to fire. **Mutation sweep** over all 31 codes found two nothing could distinguish (**C-27**); a **boundary probe** found **F-8**, `confidence` unvalidated everywhere. Ninth checker check, `controls` |
| **D2.10** | **O-13 measured, and the boundaries mattered more than the magnitude.** Interior worst endpoint gap **0.117330** at n=10, **9.7e-05** at n=1000, over `n` {10…1000} x `k` x confidence {0.90, 0.95, 0.99}. At **`k = n` `svy` returns a zero-width interval**; at **`k = 0` it returns none at all** — the most common honest result in rare-event work |
| **D2.9** | **`svy` cross-check — and the narrowing decided the scope.** Every `svy` interval is design-based; it maps `clopper-pearson` to `korn-graubard`, so **none witnesses ours**. Its Neyman allocation **is** ours, rounding included: **2000/2000** identical over a stated space. **The first external witness the allocation has ever had** — R `survey` has no allocator (F-9). `svy` never enters this environment |
| **D2.8** *(part)* | **confidence is a fixture axis** — 69 CP cases, 33 RG, at 0.90/0.95/0.99. Found **C-30**. **Coverage** replaces the width test, anchored on S-1.1's published limits, which our code reproduces (0.8382 vs 0.838). **Q11/D-37**: the plan names the interval, no default |

### The Rogan-Gladen codes — two, not three

**`CORRECTION_UNDEFINED`** — `Se + Sp <= 1`. Sends the operator to **the two numbers in the plan**.
The message says *"not one we are declining to print, but none that exists"*, and it earns that: at
Se 0.60 / Sp 0.30 the witness returns a lower bound **above** its upper bound.

**`CORRECTION_OUT_OF_RANGE`** — the corrected estimate leaves [0, 1]. Sends them to **the
relationship between the plan and the sample**, each fine alone. D-22's fourth case.

**`CORRECTION_DEGENERATE` was struck.** It said AP = 0 or 1 "carries no information". False: AP = 0
with Sp = 1 gives a point estimate of 0 and a real upper bound. **It would have refused the most
common honest result in T&S work.**

**The fact that most needs to reach an operator** (charter §8, A-2; `CORRECTION_OUT_OF_RANGE`'s fix
text; O-21 for the README): at rare-event prevalence an ordinary-sounding specificity makes the
correction **undefined, not imprecise**. 0.2% apparent prevalence needs specificity above **99.8%**.
99% sounds excellent and produces five times more apparent positives from clean content than the
whole sample held.

### D2.6 — done. What it does and does not cover

**O-8 is discharged.** The estimator is built and checked. **Three halves of Q6 and Q7 are not**, and
they are named as **O-22** and **O-23** rather than left for the next session to discover:

- **Q7 refuses at the API, not at the plan.** `interval_method` is keyword-only with no default, so
  the substitution cannot become a constant in the source — but the plan has **no `interval` field
  yet**, so exit check **F8d** cannot be performed. **O-22**, owned by D2.8. O-20's shape exactly.
- **Q6's disclosure and raw bounds live on the estimate, not in an artifact.** `note` and
  `low_raw` / `high_raw` / `clamped` exist and are tested. But **`run.py` still calls `wilson()`
  alone** — no Phase 2 estimator is wired in — so nothing writes them to a ledger or renders them to
  a report. That is the surface, deliberately after the review stop. **O-23.**

Anchor is **S-1.6 Reiczigel et al. (2010)** — Se/Sp *known*, which is our assumption (D-31).
**Not S-1.5 Lang & Reiczigel (2014)**, which propagates uncertainty in *estimated* Se/Sp; adopting
it later is a **plan-schema change, not an estimator swap**. The contract's D2.6 row cited S-1.5
until 2026-08-29 and was amended before the build — **a ruling that has not reached the binding
document is not binding.**

**The expected values already exist.** `r/fixtures/rogan_gladen.json` carries `tp_lower` / `tp_upper`,
committed before any interval code. Measured across all nine positive-denominator cases:
`RG(ap_lower) == tp_lower` and `RG(ap_upper) == tp_upper` to every printed digit — so
`epi.prev(..., method = "c-p")` **transforms a Clopper-Pearson interval endpoint by endpoint.** D2.6
composes D2.4 (8.4e-11 against base R) and D2.5, and introduces no third unwitnessed thing. *That is
an observation about `epiR`, not a theorem about corrected intervals.*

**Two rulings bind it. `Q6 / D-32`:** clamp to [0, 1] at **both** ends, **say so in the output**, and
**keep the raw bound in the ledger** — a silently clamped bound is a small lie in the artifact an
outsider reads. **`Q7 / D-33`:** Clopper-Pearson only, and a plan naming `interval: wilson` while
supplying Se/Sp is **refused** with `CORRECTION_INTERVAL_UNSUPPORTED` — not silently switched, which
would substitute a method inside a pre-registered measurement.

**Next: D2.7 refusals, then D2.8–D2.9, then the review stop.** The stop falls after D2.9 and before
anything renders these estimators.

**Three rare-event surprises now cluster in this phase**, and none was anticipated by reasoning —
each came from the artifact. `fpr_exceeds_prevalence`; the inverted interval below `Se + Sp = 1`; and
a **negative lower bound in the accept region** (`rare_event`, lower `-0.000151`, point estimate
fine). **O-21 carries them to the README as one grouped fact**, not three scattered caveats: *at the
prevalence rates this tool is for, several ordinary intuitions fail, and here they are.*

### Phase 3 — what makes it different from every phase before it

**Phase 3 releases.** A tag, a publish, and a pull request to **someone else's repository**
(ROOST `awesome-safety-tools`). Nothing in Phases 0, 1 or 2 was irreversible, and that single
fact changes three things at once.

**1. The tier re-ask is a live decision for the first time.** It has been discharged twice by
naming an absence — *no finding attributable to a FULL-only practice* — and both times the
verdict was honest because the phases shipped nothing to rehearse. **FULL's distinguishing
practice is rehearsal of the irreversible, and Phase 3 finally has something for it to bite on.**
**No forecast is recorded, deliberately** (ruled 2026-08-30): forecasting that a re-ask will fail
is how a scheduled decision becomes a formality.

**2. Rehearsal comes before the act, not after.** A release candidate, verified by hand, with a
**negative control that must fail**, before any real tag. Failed candidates stay in the record.

**3. The record goes public.** It was written for an audience of three and Phase 3 is the first
time a stranger reads it — **that is O-28**, and it is a one-time look *backwards* over git
history, not only the working tree. The history is **not rewritten**: this record cites commit
hashes as evidence throughout, so the answer is a review before release rather than a repair
after it.

> **One thing O-28 will find, recorded now rather than discovered then.** The committed record
> contains local Windows paths including the director's username — `PROJECT_CHARTER.md`,
> `CLAUDE.md`, `docs/RATIFICATION.md`, `docs/PHASE-0-VERIFICATION.md` and
> `docs/contracts/PHASE-2-HAND-RUN.md`. The username is already public via the repository owner,
> so this is directory structure rather than identity. **`SECURITY.md` §3.8 tells operators to
> avoid exactly this leak in a run directory while our own documents do it**, which is the part
> a stranger will notice. Two of those files are **dated readings or ratified text and are not
> edited** — so this is a disclosure question, not a find-and-replace.

### Traps this file did not used to carry

Each of these cost time or produced a defect. None is obvious from the code.

- **`ruff format` reads Markdown; `ruff check` does not.** Confirmed on ruff 0.16.5 from its own
  resolver output: the format half formats Python fences inside `.md`, so it walks every document
  here, **including the dated readings that are never edited**. Nothing fails today. The day
  someone writes a mis-formatted Python fence into one, two rules collide.
- **The findings register cannot hold an accepted-but-unfixed finding.** `check_findings` fails
  the gate for any row whose status is `open`, while the register's own vocabulary defines `open`
  as *accepted, not yet fixed*. So an F-number attaches when its **fix** lands, not when the
  finding is accepted — which is why F-12's number is absent from the hand-run reading that found
  it. Do not add an `open` row and expect a green gate.
- **`check_open_items` reads every open-items table in both directions**, and it skips any row
  that names a *different* obligation in its prose — the state word cannot be attributed. It took
  three drafts and every defect in it was found by running it, not reading it.
- **`probability_no_interval` is a lower bound**, not the probability. It is the chance every
  sampled unit is negative; a design SE of zero also arises from uniformly-labelled strata. The
  operator notice and the report both say *at least*.
- **The coverage figures in `src/prevalence_kit/coverage.py` are data, and a test re-derives
  them** — the binomial rows against `r/fixtures/coverage.json`, the design rows by exhaustive
  enumeration through the shipped estimators. That enumeration is the slowest thing in the suite
  at about 10s. **It proves each figure at its stated conditions and does NOT prove the figure is
  the grid minimum**, which is stated in the test rather than implied.
- **`svy` is never installed in this environment.** Its fixtures were generated in a throwaway
  environment and committed; `svy/` holds the generators and the JSON, and that is all.
- **Windows PowerShell 5.1 splits a native command's argument at embedded double quotes.** A
  commit message passed as a single-quoted here-string to `git commit -m` broke apart at a
  quoted phrase inside it, and git read the fragments as pathspecs. The message goes through a
  file: `git commit -F <file>`. This is the heredoc lesson's class arriving through a different
  shell -- the shell's parse and the writer's mental model of the same bytes differ -- and the
  failure was clean only because git refused; a command that accepted the fragments would have
  acted on them. First hit 2026-08-31, on C-50's own commit message.

### Open, by name

**Phase 2 is closed and its table closed with it.** Everything below is the Phase 3 carry.
**Nothing here is optional and nothing here is done** — each row is either a numbered obligation
or a correction whose closing condition is written down.

| # | What | Owner |
|---|---|---|
| **The Phase 3 contract** | **Written and APPROVED 2026-08-31**, Q16–Q25 ruled. `docs/contracts/PHASE-3-CONTRACT.md` is binding; D3.1 (O-19) is the next build act, the review stop falls before anything public, and the boundary commit's own defects are C-48 and C-49 | **Done — the contract now owns the rows below** |
| **O-19** | **Discharged 2026-08-31 by D3.1.** The re-read came first and found the premise half false — **C-50**: checkout v5.0.0 declared node24 at its own SHA, so only `setup-python` ever targeted Node 20, and the "drop" had partly happened (force-run on Node 24 since 2025-09-19). Re-pinned to checkout **v7.0.1** and setup-python **v7.0.0** in both workflows, runtimes derived from `action.yml` at the pinned SHAs, TW-4 clear | **Done** |
| **O-21** | The rare-event specificity fact must reach the README | Phase 3 |
| **O-28** | Pre-publication review of **git history**, not only the working tree. **Must reach the Phase 3 contract before the release** | Phase 3 |
| **O-14, O-15** | Carried, low, no action. O-15 is deliberately unmet — a ledger schema version, added only if it is ever needed | Phase 3 |
| **10 corrections open** | **C-1**, **C-42**, **C-43**, **C-44**, **C-45**, **C-46**, **C-47**, **C-48**, **C-49**, **C-50**. 53 entries, 41 closed, 2 `noted`; every open entry closes under **T-1** at D3.10, naming its discharging commit. This row is read by `check_counts` against the register — count, identifier list in both directions, figures, and absence is a failure (C-48 is what happens otherwise) | — |
