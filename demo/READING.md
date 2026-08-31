# The coverage demonstration — a dated reading

**Date: 31 August 2026.** This file is a dated reading and is never edited. Corrections to it go
in `docs/CORRECTIONS.md` with the date and the direction the number moved. It records what
happened when D3.3 was run under `demo/preregistration.json`, ruled at Q18 / D-44.

## The commitment came first, and here is the ordering evidence

`demo/preregistration.json` — SHA-256
`42ed961480d49900924b4bbed596a3bff9f72cbfb6cba8885c4f58b5955e0302` — was committed at
`ce25ce1`, **before any byte of the corpus was fetched**. Thresholds, seeds, sample size,
replication count, both interval names, the sampler specification and the full-chain plan values
were all fixed in that commit. The corpus was downloaded after it, and the fetch is recorded
below rather than promised.

## What was fetched

`google/civil_comments` (register S-7.1, CC0 1.0), four parquet files from
`huggingface.co/datasets/google/civil_comments/resolve/main/data/`, fetched 2026-08-31:

| File | Bytes | Rows | SHA-256 |
|---|---|---|---|
| `train-00000-of-00002.parquet` | 193,527,147 | 902,437 | `c20f01c3aecbdd942886cacb0ee67e995df33bc712a622fde75927ed3d6ccefe` |
| `train-00001-of-00002.parquet` | 186,778,090 | 902,437 | `a76af69d7b24758bc38b196bc422d4767935c1dd7d3c1465554649c546d99ccb` |
| `validation-00000-of-00001.parquet` | 20,955,569 | 97,320 | `2e0eb65474e7e1290df8689fc93eea783160c898c09ae15382c0a9662367bd03` |
| `test-00000-of-00001.parquet` | 20,800,265 | 97,320 | `410f803ff161e7c4ba005db7de5b444cac413f4861bf056b0fd69d670d75aa08` |

**Total: 1,999,514 rows** — exactly the count S-7.1 recorded a phase before this demonstration
was designed, and the count the pre-registration refuses without. The corpus itself is never
committed; these digests are how a stranger knows they fetched what we fetched.

## What the census found, and what the intervals did

10,000 simple random draws of n = 1000 per threshold, each draw's positive count judged by both
shipped estimators at a nominal 0.95. The truth is the census over all 1,999,514 rows.

| Threshold | Census positives | Census prevalence | Wilson covered | Clopper-Pearson covered |
|---|---|---|---|---|
| 0.5 | 159,782 | 7.9910% | 9,460 / 10,000 (**0.9460**) | 9,517 / 10,000 (**0.9517**) |
| 0.7 | 65,021 | 3.2518% | 9,493 / 10,000 (**0.9493**) | 9,585 / 10,000 (**0.9585**) |
| 0.9 | 10,224 | 0.5113% | 9,564 / 10,000 (**0.9564**) | 9,762 / 10,000 (**0.9762**) |
| 0.98 | 5,037 | 0.2519% | 9,576 / 10,000 (**0.9576**) | 9,868 / 10,000 (**0.9868**) |

The Monte Carlo error on a coverage figure at 10,000 draws is about ±0.0043 (1.96·√(.95·.05/10⁴)).

**Read the two columns the way the record has already taught — and no further than the error
allows.** *(This paragraph was corrected at the review stop, before any push, on the director's
ruling — C-51; its first form claimed a comparison that had never been performed.)* Judged
against the ±0.0043 band around nominal, **neither interval falls below 0.95 by more than the
Monte Carlo error at any point**: Wilson's two below-nominal readings, 0.9460 and 0.9493, are
inside the band, and every other reading sits above nominal. What the demonstration *can*
resolve is conservatism at the rare end — Wilson at 0.9564 and 0.9576, Clopper-Pearson at
0.9585, 0.9762 and 0.9868, each above nominal by more than the error. For Clopper-Pearson that
is the direction S-1.1 §4.2.1's guarantee permits and its width pays for; for Wilson it is the
upper half of the oscillation its literature describes. Below at the two commoner rates, above
at the two rarer, is the oscillation's shape — **four points cannot establish it, only fail to
contradict it.**

**What these four points are not.** They are a demonstration at four pre-registered operating
points, **not a sweep, and not a worst case**. The worst case for Wilson at these sizes is the
swept figure the charter carries — coverage as low as **90.98%** at n = 1000 over the gamma grid
in `r/fixtures/coverage.json` — and a four-point demonstration landing near nominal does not
soften it: a finer grid can only find a more extreme value, and these four thresholds were
chosen blind, not to find one. Rule 8, applied to our own flattering-looking numbers.

## The full-chain run

One run of the sealed chain at the pre-registered plan — threshold 0.9, `interval: wilson`,
n = 1000, seed `coverage-demo-full-chain-2026-08-31` — with the corpus's own annotator
fractions as the labels and each sampled comment's text sealed on ingest.

- Plan hash `3f5db3b38def7700f0b7c23fe151969864a409566d1759ac4615f4917266e141` (this is the
  **plan's** hash, computed by `plan`; the pre-registration file's SHA-256 above is a different
  object and the two are deliberately both recorded).
- The draw found **8 positives in 1000** — the true count, counted from the labels.
- Estimate **0.008000**, 95% Wilson interval **[0.004059, 0.015706]**. The census truth at this
  threshold, **0.005113**, lies inside it.
- `verify`: **9 checks, exit 0**, and its `sample` line reads *redrawn from the frame as a
  simple random sample* — the line F25 forced the tool to say.
- The chain was run twice while preparing this reading and produced identical numbers; the
  second run exists because the first was discarded, and the reason is recorded below.
- `demo/full_chain/` carries the plan and both reports. The run directory itself — sealed
  comment texts, ledger, key — is not committed: it is reproducible from the corpus with
  `demo/run_coverage.py`, and the reports carry the hashes.

## A leak caught by reading the report, before it was committed

The first full-chain report's Population line carried an **absolute local path** — the exact
leak `SECURITY.md` §3.8 warns operators about, about to enter the repository in a new artifact
while O-28 discloses the same leak in old ones. The tool records paths **as invoked**, by
design; the fix was to invoke it as §3.8 advises — relative paths, from the run's own directory
— and re-run. The committed reports carry `frame.txt` and no absolute path. Caught by the
phase-close habit applied early: read the artifact by eye before it becomes evidence.

## Prior characterisation — D-44 condition 5, the reviewer's

This corpus was already characterised in this record before the pre-registration existed:
S-7.1 carries the row count and licence, and Phase 0's verification (claims D1 and D2)
established that the labels are continuous annotator fractions — the fact that forced the
thresholded estimand under R-7. **That does not weaken the pre-registration, and here is why:**
pre-registration protects the choice of thresholds, seeds and design from being made after
seeing results. Nothing in the record contained a label value, a census count, or a prevalence
at any threshold — the row count and the schema are facts about the frame, not outcomes. Every
choice in the commitment was blind to everything the commitment exists to be blind to. The
census prevalences in the table above were computed for the first time after `ce25ce1`.

## Approximations and scope, stated rather than implied

- **Draws are without replacement from a finite population**, so the positive count is
  hypergeometric while both intervals are binomial constructions. At n/N = 0.05% the difference
  is far below the Monte Carlo error; disclosed, not corrected for.
- **The replication sampler is the demonstration's, not the shipped one.** The shipped
  `draw_srs` keys every frame id and sorts — right for one auditable draw, infeasible for
  40,000. The demonstration's hash-counter sampler is specified in the pre-registration well
  enough to reimplement in any language; the full-chain run uses the shipped sampler.
- **The decode rule matters.** The corpus stores annotator fractions as 32-bit floats; values
  were decoded to 64-bit and rounded to 6 decimal places before comparison, as pre-registered,
  so 7/10 compares as 0.7 and not as 0.699999988.
- **Modulo bias** in the sampler is below 1e-70 per candidate.
- **Environment:** CPython 3.14.0, Windows 11, pyarrow 25.0.1 in a throwaway virtual
  environment. pyarrow is not a dependency of this project and never enters its tree — the
  `svy/` precedent: committed artifact, recorded environment, regenerable by a stranger.

## Open at this reading, by name

| # | What | Severity |
|---|---|---|
| README integration | The plot and these figures reach the README under D3.4, behind the review stop | — |
| O-10's assertion | The `svy` credit is owed an overclaim-scanner assertion, and no such scanner exists yet; the credit lands in D3.4, the assertion remains open | low |
| Corpus cache | The demonstration is regenerable only by re-fetching ~422 MB; the digests above are the bridge. Accepted: committing the corpus is neither licensed-required nor wanted | low |
