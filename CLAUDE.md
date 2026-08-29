# prevalence-kit — orientation for the next session

Audit-grade prevalence measurement for Trust & Safety. You give it a sampling plan and human labels;
it returns an estimate, an honest interval, sealed content, a tamper-evident record, and a stamped
report. **No AI ever touches the evidence or the estimate.**

This project runs the **governed-orchestration** skill at **STANDARD** tier, manual-approve.

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
| `PROJECT_CHARTER.md` | **Binding.** Scope, six verbs, hard rules, honest limits. Amendments A-1, A-2 |
| `docs/contracts/PHASE-2-CONTRACT.md` | **Binding, current.** Q1-Q5 ruled. D2.1-D2.5 done |
| `docs/DECISIONS.md` | D-1 … D-31. Why each choice, and what was rejected |
| `docs/CORRECTIONS.md` | Every claim that was wrong. **Counts claims that reached a commit *or changed a ruling*** |
| `docs/FINDINGS.md` | Findings register. `check_claims` reconciles it against the code |
| `docs/STANDARDS.md` | Every source pinned by version, date, digest or DOI. **S-8 pins the retrieval *procedures* too** |
| `docs/contracts/PHASE-1-CONTRACT.md` | Closed. §10 is the outcome |
| `SECURITY.md` | Threat model. §3 is the limits, carried forward unchanged |
| `TIME-LOG.txt` | Append-only wall clock. Stamp on request |

`docs/contracts/PHASE-1-REVIEW-STOP.md` and `docs/RULINGS-QUEUE.md` are **dated readings — never edited.**
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
checkpoint:** `--strict src` reads **13** files, plain `mypy` reads **28**. Both numbers move as the
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

**The suite takes ~55s locally and ~10s in CI. That is not a defect** — profiled 2026-08-29: the time
is Fernet sealing plus real filesystem writes in the Phase 1 tests, and Windows pays for both. The
Phase 2 arithmetic tests are nearly free.

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
7. **A check covers less than it looks like it covers.** Nine times now: C-15, C-19, V-15, V-16,
   C-23, `check_codes` reading one contract when there were three, D-34, C-27, and **C-34**. Ask
   what it does **not** read, in both directions. **C-34 is the worst kind: a checker that
   *stated* a scope it did not have.** No stated scope invites the question; a wrong one answers
   it falsely, and the reader comes away more confident and less correct. **Make the scope the
   object the code walks, never a sentence beside it.**
8. **A worst case measured over a grid is an *upper bound* on the worst case, and a bound is
   rounded in the direction that keeps it true.** A finer grid can only find a more extreme
   value, so state the grid step like any other axis — 0.9540 at step 0.25, 0.9537 at 0.05, and
   **keep both**, because two grids disagreeing is evidence about the measurement.
   **Rounding to nearest is right for a measurement and wrong for a bound**: it rounds toward
   the middle and silently weakens a claim about everything outside your sample. *"As little as
   91%"* is false when the measurement is 0.9098 — **C-32**, the director's, in the charter.
   The sweep it prompted found two more, both ours and both flattering: **C-33**.
9. **A checked number can carry an unchecked claim.** *"23 reason codes, each with both controls"*
   looks like one verified sentence. A machine counted the 23. Nothing checked "each with both
   controls", and it was false — C-27. Same shape in C-28. This is worse than a plain unchecked
   claim, because the half you can verify makes you stop looking. **Check the property, or split
   the sentence.**
10. **A test asserts a defining property, or a measurement with stated scope. Never a region.**
   A defining property is true by construction — *Clopper-Pearson covers at least 1 − α*, and
   S-1.1 §4.2.1 says so. A region description — *narrower where k ≤ 1* — is a summary of the
   grid you happened to sample, and it will be wrong at the corner you did not. **C-30(c) was
   wrong three times** before the width test was deleted and replaced by a coverage test.
11. **Check an artifact the way its real consumer reads it.** Structured files — YAML, JSON, TOML,
   CSV, XML — get the **consumer's parser**, never a regex. That is how an unparseable `gate.yml`
   passed a green checker (**C-23**). **Markdown is the exception**, and the reason is the rule: its
   consumer is a human, who reads it loosely too.
12. **"The guard did not object" is not "the guard looked."** Know what each check does *not* read,
    and assert that scope rather than describe it.
13. **A check with no artifact is a memory with a result attached.** The fixture verdict check ran
    once as a `python -c`, was reported as "machine-checked", and left no trace. **The suite count
    not moving is what exposed it** — which is why the gate prints its own count.
14. **The witness's documentation is not the witness. Only the pinned build is.** C-25: the manual
    on CRAN described a version we do not run.
15. **Re-run the whole gate after anything that writes to the working tree, and report *that*
    run.** C-29: a mutation loop ended with `git checkout --` on a file whose real edit was
    still unstaged, so it reverted the edit. The gate had been green before the loop. I
    reported those numbers after it, and committed a tree that failed 3 tests.
16. **A source that anchors an *arithmetic* can be validated by reproduction. A source that
    anchors a *decision* has to be read.** S-1.4 and S-1.6 are unread and that is fine — the
    Rogan-Gladen formula either reproduces against `epiR` or it does not. **S-1.1 anchors a
    choice**, and no reproduction checks a choice. It went unread for two phases. O-24.
17. **Never delete or overwrite the director's working directories.** `C:\Users\mohds\ts-sentry` is
    read-only. **Never remove a Docker image** — they belong to the director's other projects.

## Where things stand

**Phase 0** ratified. **Phase 1** closed at `d66d225`. **Phase 2 is in build**, **Q1–Q11 ruled**,
**A-1 … A-4** applied to the charter.

**Repository:** `github.com/MohdSaifHussain/prevalence-kit`, private. **607 tests**, seven gate
checks green. **CI last ran green at 602** on CPython 3.12.14 / 3.13.15 / 3.14.7, run
`33241090771`, head `8565ddc`. Local and CI figures are stated apart on purpose.

**Three of these figures are now machine-checked** — the test count, the highest ruled question,
and the phase — because this file went stale within hours of being written and nothing noticed.
A stale README misleads a reader; **a stale CLAUDE.md misleads the next session before it has
read anything else.** `check_figures` derives all three.

### Done

| | |
|---|---|
| **D2.1** | R witness reproduces **Barnett Table 2B** — `2098/828/584/256/234`, VVR 0.2000%, SD 0.0539 pp. `svydesign` SE against the closed form: 4e-16 |
| **D2.2** | 4 allocation + 5 estimation fixtures from `survey` 4.5, through the one validated call |
| **D2.3** | `stratified.py` — Neyman, largest-remainder rounding, stratified estimator. Worst disagreement with `survey`: **9.5e-15** |
| **D2.4** | Clopper-Pearson **from its definition** — binomial tail in log space, no incomplete beta anywhere. Witness: base R `binom.test`. **8.4e-11**, across n = 1…1,999,514 **and** confidence {0.90, 0.95, 0.99} |
| **D2.5** | Rogan-Gladen point estimate, 11 cases from `epiR`. Two refusals, both controls |
| **D2.6** | Rogan-Gladen **interval** — the corrected bounds are the apparent Clopper-Pearson bounds transformed endpoint by endpoint. Against `epiR`: **7.3e-13**. **O-8 discharged.** Clamped both ends (Q6/D-32), Clopper-Pearson only (Q7/D-33) |
| **D2.7** | Refusals proved to fire. **Mutation sweep** over all 31 codes found two nothing could distinguish (**C-27**); a **boundary probe** found **F-8**, `confidence` unvalidated everywhere. Ninth checker check, `controls` |
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

### Open, by name

| # | What | Owner |
|---|---|---|
| **O-19** | Re-pin `checkout` and `setup-python` before GitHub drops Node 20. **TW-4 fired** | Phase 3 |
| **O-20** | `allocation_rounding` in the *hashed plan file*. Today it is a required API argument only | D2.8 |
| **O-21** | The rare-event specificity fact must reach the README | Phase 3 |
| **D2.11** | The witness image is rebuilt by hand; CI never runs it. Static half closed | Phase 2 |
| **O-22, O-23** | Q7's plan-load refusal and Q6's ledger + report disclosure. **D2.6 built the estimator half only** | D2.8, post-stop |
| **D2.14** | `check_claims` gaps: PDF paths, the CORRECTIONS counts table (**document its semantics, do not guess them**), the R artifacts. **The register gap is closed — D-34, `check_register`** | Phase 2 |
| **Charter §6.1** | Still says Rogan-Gladen *"has no witness … validated against Lang & Reiczigel (2014)"*. **D-31 says both halves are wrong.** The charter is ratified, so it needs an **amendment-log ruling (A-3)**, not a builder edit | **Director** |
| **O-3, O-4, O-13, O-14, O-15** | Carried, untouched | Phase 2 |
| **28 corrections open** | C-1 … C-26. Close under **T-1 (D2.12)**, each naming its commit | D2.12 |
