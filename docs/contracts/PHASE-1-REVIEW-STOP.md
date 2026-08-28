# Phase 1 — review stop

**Date:** 28 August 2026 · **Commit:** `f95304b` · **Status: OPEN. Awaiting the director's rulings.**

The core is built. The surface is not. Contract §6 places the stop exactly here, before the CLI, the
report emitter and the three checker tools, so that a pretty surface is not hiding the thing the
guarantees rest on.

**Gate at this commit:** `ruff check` clean · `ruff format --check` clean (29 files) ·
`mypy --strict` clean (16 files) · **88 tests pass** · 2,291 lines across `src/` and `tests/`.

**Seven defects found. All seven were found by the builder, and all seven were confirmed by
running something, not by reading.** Each has a proposed disposition. **The builder does not close
its own findings.**

---

## Part 1 — The guarantees, proved by quoting lines

Summaries hide defects. These are the exact lines.

### G1 — The plan is hashed before any data file is opened (R1)

`src/prevalence_kit/run.py:95-97`:

```python
    plan_hash = plan.plan_hash
    sealed = SealedStore(ws.root / "plan.sealed", ws.key_path.read_bytes())
    manifest = sealed.seal(PLAN_ITEM, json.dumps(plan.as_record(), sort_keys=True).encode("utf-8"))
```

`do_plan` takes a `Plan` and a `Workspace`. It receives no path to the population or the labels, and
`Plan.load` opens only the plan file. There is no code path by which data can reach the hash.

Proved by execution, not by inspection: `test_hash_does_not_need_the_data` points the plan at
`no-such-frame.txt` and `no-such-labels.csv` and asserts a 64-character hash still comes out.

### G2 — Every ledger entry commits to the one before it

`src/prevalence_kit/ledger.py:114, 129, 135`:

```python
        expected_prev = GENESIS_LINK
            ...
            if entry.prev != expected_prev:
            ...
            expected_prev = entry.entry_digest
```

Three negative controls: an edited entry, a removed entry, and a truncated JSON line. All three
raise `LEDGER_BROKEN` rather than a traceback.

### G3 — Chunk authentication runs before sequence checking, and the order is why the codes differ

`src/prevalence_kit/seal.py:153, 159, 188`:

```python
            except InvalidToken as exc:      # -> SEAL_TAMPERED
        ...
        self.verify_structure(manifest)      # only reached by chunks that authenticate
        ...
        if Counter(observed) == Counter(expected):   # -> SEAL_REORDERED, not MISMATCH
```

This ordering is what makes D-14's four codes distinct. Edited bytes fail authentication first, so
they report `SEAL_TAMPERED` rather than surfacing as a generic digest mismatch. Only chunks that
genuinely authenticate are then judged truncated, reordered, or substituted — and the multiset
comparison is what separates the last two.

`test_the_four_reason_codes_are_distinct` asserts the distinctness directly rather than leaving it
to be inferred from four separate tests passing.

### G4 — `verify` re-derives; it does not re-read

`src/prevalence_kit/verify.py:130, 178`:

```python
    redrawn = draw_srs(frame, seed=plan.seed, n=plan.sample_size)
    ...
    recomputed = _estimate_from(plan, ws.read_json("labels.json")).as_record()
```

The sample is redrawn from the recorded frame and the estimate is recomputed from the recorded
labels. Nothing already written down is trusted.

`test_estimate_that_does_not_follow_from_the_labels` rewrites `estimate.json` **and** its ledger
digest **and** the entry digest, so the chain is internally consistent and only recomputation
catches it. That is the test that separates a record from a story.

### G5 — The plan is checked twice, and a skipped check is stated out loud (D-15)

`src/prevalence_kit/verify.py:65, 87, 95`:

```python
    # (a) The sealed copy. Always available, so R5 holds after the file is gone.
    ...
    # (b) The working file, when it is still there. Catches edits made at any
                "SKIPPED -- no plan file on disk to compare. Only the sealed copy was checked.",
```

### G6 — Zero network, proved through the same code path the real check uses

`offline_violations` is called by the real test with the declared dependencies, and by the negative
control with the declared dependencies **plus `httpx`**. The control asserts `httpx` is reported.
A third test proves the walk is recursive by requiring `{cryptography, cffi, pycparser}`, so a
broken recursion cannot leave everything else passing while checking nothing.

---

## Part 2 — Defects found

### F-1 — A non-numeric label crashes instead of refusing · **severity: high**

`Estimand.is_positive` calls `float(raw)`. A label value of `"unclear"` — entirely plausible in real
Trust & Safety data — produces:

```
ValueError: could not convert string to float: 'not-a-number'
```

A raw traceback, not a named refusal. This breaks R8 (every refusal says what went wrong and what to
do) and it breaks the tool's central promise on the most likely real-world input error.

**Proposed disposition: FIX NOW, before the surface.** Add reason code `LABEL_NOT_NUMERIC`, refusing
with the item id and the offending value — and *not* the content. Both controls.

### F-2 — Chunk filenames misorder above 9,999 chunks · **severity: medium**

Chunk files are `f"{i:04d}.bin"` and read back with `sorted(glob("*.bin"))`. Past four digits the
zero-padding stops working:

```
sorted(...)  -> ['0998.bin', '0999.bin', '1000.bin', '10000.bin', '10001.bin', '9999.bin']
correct      -> ['0998.bin', '0999.bin', '1000.bin', '9999.bin',  '10000.bin', '10001.bin']
```

At `CHUNK_BYTES = 64 KiB` that is any single item over **640 MB**.

**It fails safe** — `verify` reports `SEAL_REORDERED` rather than returning wrong bytes — but a
lawful large item cannot be sealed and read back, and the operator gets a tamper alarm for a bug.

**Proposed disposition: FIX NOW.** Sort numerically on the stem rather than lexicographically, and
add a test that seals a synthetic item with more than 10,000 chunks using a small `CHUNK_BYTES`
override. Cheap now; a silent trap later.

### F-3 — `EMPTY_SAMPLE` covers three different situations · **severity: medium**

| Situation | Code today |
|---|---|
| `sample_size <= 0` in the plan | `EMPTY_SAMPLE` |
| Frame holds fewer items than the plan asks for | `EMPTY_SAMPLE` |
| Frame is empty | `EMPTY_SAMPLE` |

Doctrine rule 5 and contract R3 require a **distinct reason code per failure mode**. These are three
different operator problems with three different fixes, and one code for all three tells the
operator nothing. The contract itself defines `EMPTY_SAMPLE` narrowly as "n = 0 — no interval is
defined".

**Proposed disposition: FIX NOW.** Split into `EMPTY_SAMPLE` (n = 0), `FRAME_EMPTY`, and
`FRAME_TOO_SMALL`. Each with both controls. This is the contract's own rule, failing on the
contract's own list.

### F-4 — Run-level E9c does not actually exercise `SEAL_REORDERED` · **severity: medium**

The fixture's content is ~45 bytes per item and `CHUNK_BYTES` is 64 KiB, so **every ingested item is
exactly one chunk**. An intra-item reorder is not expressible, and `test_swapped_chunks_between_items`
honestly asserts `SEAL_MANIFEST_MISMATCH` instead.

The unit test in `test_seal.py` does prove `SEAL_REORDERED` on a 4-chunk item. But **the contract's
exit check E9c says "swap two chunks → `SEAL_REORDERED`"**, and when the director performs E9c by
hand on a realistic run he will get `SEAL_MANIFEST_MISMATCH` and the contract will look wrong.

**This is the finding I would most expect to escape.** It is a gap between a passing test and the
document the director will read, and every individual piece is green.

**Proposed disposition: FIX NOW, and it is a fixture change, not a code change.** Make the synthetic
generator emit one deliberately large item so the run-level reorder is real, then restate E9c in the
contract to name which item to damage. Alternatively the director may rule that E9c is a unit-level
check and amend the contract to say so — that is a legitimate call, and it is his.

### F-5 — Missing sealing key reports `SEAL_TAMPERED` · **severity: low**

`Workspace.store()` raises `SEAL_TAMPERED` when `seal.key` is absent. Nothing has been tampered
with; the operator has simply lost or not supplied a key, which is a completely different problem
with a completely different remedy.

**Proposed disposition: FIX NOW.** Add `KEY_MISSING`. Same class of defect as F-3.

### F-6 — `verify` never re-derives the labels-to-sample correspondence · **severity: low**

`do_ingest` refuses unless labels match the drawn sample one-to-one. `verify` checks `labels.json`
against its ledger digest, but **never re-asserts that its keys equal `sample.json`'s `item_ids`**.

Both files are digest-protected, so this is not reachable by editing one file. It is reachable by
assembling a run whose ledger is internally consistent but whose labels belong to a different
sample. Narrow — but G4 claims `verify` re-derives rather than trusts, and here it trusts.

**Proposed disposition: FIX NOW.** Two lines and a test. Cheaper than the paragraph explaining why
it is safe.

### F-7 — `_safe_id` truncates SHA-256 to 128 bits · **severity: low, disclosure**

Sealed items live in directories named by the first 32 hex characters of the item id's digest.
128 bits gives a birthday bound around 2⁶⁴ items, so collision is not a practical risk. But a
collision would mean one item silently overwriting another's directory, and nothing detects it.

**Proposed disposition: DEFER to Phase 2, with a cheap guard now.** Refuse if a seal would write into
a directory that already exists for a different item id. That converts an undetectable silent
overwrite into a named refusal, which is the property that matters.

---

## Part 3 — Two things I want ruled, not assumed

### Q1 — `svy`'s Wilson is not the textbook Wilson. O-4 needs narrowing.

While cross-checking, I read `svy` 0.25.0's source. Its `wilson` is the **design-based** variant: it
replaces *n* with an effective sample size `n_eff = p(1-p)/se²` and uses a **t-quantile with df**,
not *z*. Its own comment cites Wilson (1927) and Franco et al. (2019, JSSAM).

For a simple random sample our textbook interval uses *z*; svy would use *t* with df = n−1. **The two
will not agree to 4 significant digits at small n**, and D-3 assumed they would.

Our implementation is independently confirmed correct: `test_wilson_endpoints_satisfy_the_score_equation`
checks the *defining* property — that the score statistic equals *z* at each endpoint — rather than
checking my algebra against itself. Residual ≤ 3×10⁻⁸, which is the 12-decimal string rounding.

**I recommend narrowing obligation O-4:** cross-check against **R `survey`** as the primary witness,
and against `svy` only where its estimator is the same estimator. Recording this now rather than
discovering it mid-Phase-2.

### Q2 — The 88 tests are mine, and that is a limit on what they prove

I wrote the code and the tests from one understanding. Where that understanding is wrong, it is
wrong in both, and the suite agrees with itself. The measured escape rate on the prior governed
build was roughly a quarter to a third of defects reaching the director undetected.

The score-equation test (Q1) is the one place I deliberately built a check that *cannot* agree with
my implementation for the same wrong reason. **Everything else in the suite can.**

Concretely, what I would look at first if I were you: **F-4**, because every piece of it is green
and the gap is only visible by reading the contract next to the fixture.

---

## Proposed dispositions, in one table

| # | Finding | Severity | Proposed |
|---|---|---|---|
| F-1 | Non-numeric label crashes | **high** | Fix now — `LABEL_NOT_NUMERIC` |
| F-2 | Chunk misorder above 9,999 | medium | Fix now — numeric sort + test |
| F-3 | One reason code for three situations | medium | Fix now — split into three |
| F-4 | Run-level E9c does not test reorder | medium | Fix now — fixture, **or** amend E9c |
| F-5 | Missing key reports tampering | low | Fix now — `KEY_MISSING` |
| F-6 | `verify` trusts labels↔sample | low | Fix now — two lines |
| F-7 | 128-bit item-id truncation | low | Guard now, resolve Phase 2 |
| Q1 | `svy` Wilson ≠ textbook Wilson | — | Narrow O-4 |
| Q2 | Suite is builder-written | — | Noted, not fixable by me |

**Nothing proceeds to the CLI, the report emitter, or the checker tools until these are closed.**
