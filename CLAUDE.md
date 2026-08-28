# prevalence-kit — orientation for the next session

Audit-grade prevalence measurement for Trust & Safety. You give it a sampling plan and human labels;
it returns an estimate, an honest interval, sealed content, a tamper-evident record, and a stamped
report. **No AI ever touches the evidence or the estimate.**

This project runs the **governed-orchestration** skill at **STANDARD** tier, manual-approve.

## The three roles

- **Director** — Mohd Saif Hussain. Rules on every judgment call, runs the phase-close ritual by
  hand, gates every push. The tiebreaker.
- **Builder** — you. Read the record, plan, ask, build, self-review adversarially, stop at gates.
  **You never close your own findings.**
- **Reviewer** — a separate session with its own probes and harness. It has been wrong five times,
  always about *what the contract's action is*, never about what the code does.

## Read these, in this order

| File | What it is |
|---|---|
| `PROJECT_CHARTER.md` | **Binding.** Scope, six verbs, hard rules, honest limits |
| `docs/contracts/PHASE-2-CONTRACT.md` | **Binding, current.** Proposed; 3 numbered questions ruled |
| `docs/DECISIONS.md` | D-1 … D-25. Why each choice, and what was rejected |
| `docs/CORRECTIONS.md` | Every claim that was wrong, counted **by source separately** |
| `docs/FINDINGS.md` | Findings register. `check_claims` reconciles it against the code |
| `docs/STANDARDS.md` | Every source pinned by version, date, digest or DOI |
| `docs/contracts/PHASE-1-CONTRACT.md` | Closed. §10 is the outcome |
| `SECURITY.md` | Threat model. §3 is the limits, carried forward unchanged |
| `TIME-LOG.txt` | Append-only wall clock. Stamp on request |

`docs/PHASE-1-REVIEW-STOP.md` and `docs/RULINGS-QUEUE.md` are **dated readings — never edited.**
Corrections to them go in `docs/CORRECTIONS.md` with the date and the direction the number moved.

## The gate is seven checks, not four

```
ruff check .                       ruff format --check .
mypy --strict src                  mypy            (config: src + tests)
tools/check_claims.py --selftest   tools/check_claims.py
pytest                             (NOT pytest -q -- addopts already sets -q, so -q is -qq
                                    and suppresses the count. E11 exists for that count.)
```

Run **all of them** after any scripted edit, not the half that looks affected. Use
`.venv\Scripts\python.exe`.

`tools/check_tripwires.py` is offline by default; `--check` reaches the network. It is a phase-close
ritual, not a CI job — a tripwire firing is a decision for the director, not a red X.

## Rules that have actually bitten here

1. **No code without a ruling.** Contract before build; numbered questions with options and a
   recommendation; the director rules.
2. **Green tests prove self-consistency, not meaning.** C-16 was found by a person reading the
   report, with every test passing and the checker reconciling.
3. **Every gate gets both controls and a distinct reason code.** How many codes? **D-22**: count the
   artifacts an operator must open, not the situations.
4. **Re-derive numbers from the artifact.** Three corrections are figures nobody re-derived.
5. **End every report with what remains open, by name and severity.** C-12 is what happens otherwise.
6. **A finding closed in one artifact can be open in another** — D-23. `check_claims`'s `fixtures`
   check covers the shipped example; the general class is still open.
7. **Never delete or overwrite the director's working directories.** `C:\Users\mohds\ts-sentry` is
   read-only.

## Where things stand

**Phase 0** ratified. **Phase 1** closed at `d66d225` — 222 tests, 20 findings closed, 23 corrections
open. **Phase 2** contract proposed and its questions ruled; no Phase 2 code exists.

**Two blockers owed before Phase 2 code, both needing a remote:**

- **O-17** — CI has never executed. `.github/workflows/gate.yml` was verified by reading.
- **O-16** — all 222 tests have only run on Python 3.14.0. R2 requires byte-identical sampling across
  3.12/3.13/3.14 "asserted, not assumed". It is currently **assumed**. CI is the only instrument that
  asserts it.

**Next session:** create the private repository, push, read the CI result — especially a red 3.12
job, which would mean the sample is not byte-identical across versions. Then Phase 2 code, starting
with **D2.1: reproduce Barnett Table 2B in R before any estimator is written.**
