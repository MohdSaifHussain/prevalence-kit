# V-1 — proposed mechanism

**Status: PROPOSAL. Nothing implemented. Awaiting the director's ruling.**
**Date:** 28 August 2026 · **Against commit:** `eb4c2cc`

Part F item 1 says propose and stop, because this changes ledger and `verify` semantics. That is
why the stop sits before the surface.

---

## 1. Reproduced independently, before the probes arrived

Reproduced from the written description alone, not from `probe3.py`. The probe scripts arrived
afterwards and were not used to establish this.

```
attempt 1: threshold 0.5  -> point estimate 0.225000000000
attempt 2: threshold 0.05 -> point estimate 1.000000000000

ledger steps: ['plan','sample','ingest-labels','estimate','plan','sample','ingest-labels','estimate']
verify: PASSED, exit 0. 6 checks
  [ok] plan (sealed copy): matches genesis hash 733a98556db85922
```

`733a9855…` is **ledger entry 4**. Entry 0 holds `f5e37e4b…`. The word "genesis" is attached to a
hash that is not the genesis hash.

**One thing I found that was not in the report, and it matters for the fix.** The first plan's
sealed copy is destroyed by the re-plan, and *the destruction is already detectable*:

```
plan.sealed chunk files: ['0000.bin']
first plan NOT recoverable: Refusal SEAL_MANIFEST_MISMATCH:
    Item __plan__ contains a chunk the record does not list.
```

Entry 0's manifest no longer matches what is on disk. **D-14's manifest already catches this.**
`verify` never asks, because it only unseals the manifest from the *latest* plan entry. The evidence
of the tampering is sitting in the record and `verify` walks past it. That is the shape of the fix.

## 2. Your load-bearing judgment holds. I am not pushing back.

You invited pushback on whether V-1 is a defect against a stated protection or a case of a stated
limit. I checked §1.3, §2.2 and §3.5 myself. **It is a defect, and §2.2's own words make the case
stronger than you put it.**

- **§1.3 names this exact attack** in its opening paragraph — *"Redefine the estimand"* — and then
  promises protection against it. Its closing line is *"the analyst who wants to be able to prove,
  later, that they did not move the goalposts."* V-1 is moving the goalposts and `verify` certifying
  it.
- **§2.2's mitigation is falsified literally:** *"A plan changed after results are seen produces a
  hash mismatch, and `verify` refuses with a named reason."* The plan was changed after results were
  seen. `verify` did not refuse.
- **§2.2 and §3.5's honest limit does not reach this.** Both are about *separate runs* —
  "running the tool many times and publishing only the run you liked". V-1 is one workspace, one
  ledger, one `verify` call.
- **And §2.2's fallback reasoning also fails.** It says the discarded runs are *"conspicuous by
  absence if anyone asks."* Here the discarded attempt is **not absent** — it is in the ledger at
  entries 0–3 — and `verify` passes anyway. The sentence assumes a reader would notice; nothing
  makes them.

A protection that is named, then falsified by a five-line script, is a defect.

## 3. Exact width of what is caught today

Re-derived here rather than restated. Three cases, same fixture, current code:

| Case | Today |
|---|---|
| Re-plan (description changed), chain **not** re-run | REFUSED `ESTIMATE_MISMATCH` |
| Re-plan (threshold moved), chain **not** re-run | REFUSED `ESTIMATE_MISMATCH` |
| **Re-plan (threshold moved) + full chain re-run** | **PASSED, exit 0** |

So: caught when the re-plan leaves the downstream record inconsistent — because `sample_record`
embeds `plan_hash`, which is real protection and worth keeping. **Not caught when the operator
re-runs everything**, which is the case that requires no skill and produces a clean-looking record.
And in the two caught cases the code is wrong (V-2).

## 4. Proposed mechanism — three layers, not three alternatives

You listed three options. **I recommend all three, because each covers a case the others do not**,
plus a fourth item that falls out of your F-7 ruling.

### Layer 1 — writer side: a workspace is one run

`do_plan` refuses if the ledger already has **any** entry.

- New code: **`RUN_ALREADY_OPEN`**
- Message: this workspace already holds a measurement; start a new one.

*Why not enough alone:* prevention does not help an auditor handed an already-corrupted record, and
`verify` must never assume the writer behaved. `verify` is the auditor's tool.

### Layer 2 — reader side: a run is a linear sequence of steps

`verify` refuses if **any step name appears more than once** in the ledger.

- New code: **`RUN_NOT_LINEAR`**
- Message: names the repeated step and the entry numbers.

*Why this is the load-bearing layer:* it holds regardless of what produced the record — this
version, an older one, or a hand-assembled directory. It is also the cheapest thing for an outside
auditor to re-implement.

### Layer 3 — correctness: "genesis" may only ever mean entry 0

`_verify_plan` binds `entries[0]`, never `by_step["plan"]`. The string "genesis hash" is only ever
printed for the hash in ledger entry 0.

*Required independently of Layers 1 and 2.* The false statement is its own defect and would survive
both other fixes. This is also what fixes **V-2**: with the plan bound to entry 0, a re-plan with no
re-run compares the working file against entry 0's hash and refuses `PLAN_HASH_MISMATCH` — the code
already in the contract's §4 for exactly this event.

### Layer 4 — `do_plan` must not overwrite `plan.sealed/`

This is your F-7 ruling doing its second job: *"write the guard so it covers the reachable case, not
only the astronomical one."* Re-sealing the same item id into the same directory is the reachable
case, and §1 above shows it silently destroying the original commitment. The guard refuses rather
than overwriting.

### What this does and does not buy

**Caught after the fix:** any re-plan in a workspace, with or without a re-run, at write time and
again at verify time; and the destruction of a prior sealed plan.

**Still not caught, and these remain honest limits under §3.5:** deleting the workspace and starting
over; running two workspaces and publishing one. No local tool can prevent either, and the charter
already says so. **I do not propose to claim otherwise.**

## 5. The one thing I will not decide alone

**Layer 2 forbids re-running any step, not just `plan`.** That means this is refused:

> ingest labels → estimate → *more labels arrive* → re-ingest → re-estimate

Under strict linearity that operator must open a new workspace. I think that is right — it is the
p-hacking path in miniature, and "a new measurement is a new workspace" is a clean rule an auditor
can hold in their head. But it is a real usability cost on a legitimate workflow, and it is a
judgment about how the tool is used, not about whether it is correct.

**Options:** (a) strict linearity, every step at most once — my recommendation; (b) only `plan` is
once-only, other steps may repeat and `verify` binds the last; (c) strict linearity plus an explicit
`--amend` that appends a visible `amendment` entry the report must print.

(b) reopens the hole one layer down. (c) is honest but is new surface, and §4 of the charter caps
v1.0 at six verbs.

## 6. Sequencing note

Layers 2 and 3 change `verify`'s semantics, so **every exit check from E5 onward must be re-run
after this lands** — not the ones that look affected. The current suite's `run` fixture builds one
linear chain and will be unaffected, which is precisely why it did not catch this.

New tests, each with both controls: the full V-1 scenario asserting a refusal; a single honest run
still passing; entry-0 binding asserted by hash, not by string; and E8d.

---

## Appendix — Q1 evidence, as required before you rule on O-4

You declined to rule on narrowing O-4 without quoted, version-locked source. Here it is.

**Provenance.** `svy` 0.25.0 sdist, `svy-0.25.0.tar.gz`, uploaded **2026-08-26T13:54:41Z**,
PyPI-published sha256 `870ef8104e10c6f7e8bfd3cf1c71ccad2e07d41bb79fc8163a4b9c7f7900a93c`. The local
copy's sha256 matches that value exactly.

**File:** `src/svy/estimation/base.py`, **lines 713–746**, verbatim:

```python
713|        elif method == "wilson":
714|            # ── Wilson score interval ──
715|            # Uses the score-test inversion with effective sample size.
716|            # Replaces n with n_eff = p(1-p)/se² and uses t-quantile for df.
717|            # Reference: Wilson (1927); Franco et al. (2019, JSSAM).
...
729|            # Effective sample size
730|            n_eff = (p * (1 - p)) / (se**2)
731|
732|            # df-adjustment (same as beta method)
733|            if df > 0 and n > 1:
734|                t_n = stats.t.ppf(1 - alpha / 2, n - 1)
735|                t_df = stats.t.ppf(1 - alpha / 2, df)
736|                n_eff = n_eff * (t_n / t_df) ** 2
737|
738|            # Wilson score interval: roots of the score-test quadratic
739|            z = self._t_crit(alpha, df)
```

Two differences from the textbook binomial interval, both from the library's own source rather than
from my reading of it: `n` is replaced by `n_eff = p(1-p)/se²` (line 730), and the critical value
comes from `self._t_crit(alpha, df)` (line 739), a **t**-quantile, not `z`. Line 716 states both in
the library's own words.

**What this does not establish.** I have not run svy's estimator against ours to measure the
disagreement at a given n. The quoted source shows the estimators differ in construction; it does
not quantify by how much. That measurement belongs in Phase 2 and I am not asserting it now.

**Recommendation unchanged, now with evidence:** narrow O-4 so R `survey` is the primary witness and
`svy` is used only where its estimator is the same estimator. To be recorded in `docs/STANDARDS.md`
S-2.2 with this provenance if you rule for it.
