# Standard operating procedure

How to measure prevalence with this tool, from nothing to a report someone else
can check. Written for a person who has not seen it before.

**Every command in this document was executed before it was written**, on
2026-08-31, and the outputs shown are the real ones. That sentence is a rule in
this project rather than a courtesy: the last time a checklist here was written
from expectation rather than execution, two of its rows described a tool that
did not exist.

---

## 1. What this tool is for, and when to stop reading

You want to say **"X% of the content on our platform violates policy Y,"** and
you want someone who does not trust you to be able to check it.

You have, or can get: a list of the units in the population, and humans who will
label a sample of them.

If you want a classifier, a detector, or something that decides what is
violating — this is not that tool and never will be. It measures. It never
judges content.

## 2. Install

**Read this first: v1.0 is not released yet.** The published-package and
published-image routes below are what the release will provide, and they are
marked because **they have not been executed** — nothing is on PyPI or in a
registry at the time of writing, and this document does not pretend otherwise.
The from-source and local-container routes are the ones that were run to produce
every output in this file.

**From source — executed:**

```
git clone https://github.com/MohdSaifHussain/prevalence-kit
cd prevalence-kit
pip install -e .
```

```
$ prevalence-kit --version
prevalence-kit, version 0.1.0.dev0
```

**Container, built locally — executed:**

```
docker build -t prevalence-kit .
docker run --rm -v "$PWD:/work" prevalence-kit --version
```

**After the release — not yet executed, and stated as future:**

```
pip install prevalence-kit
docker pull ghcr.io/mohdsaifhussain/prevalence-kit:latest
```

Everything below is written as `prevalence-kit …`. To use the container, put
`docker run --rm -v "$PWD:/work" prevalence-kit` in front of the same arguments.
It runs as a non-root user and writes only inside `/work`.

## 3. The shape of a measurement

Six commands, in this order. Each writes to a **run directory** — one
measurement per directory, which is what stops a number being chosen after the
results are seen.

| | Command | What it does |
|---|---|---|
| 1 | `plan` | Hashes your plan **before any data is touched**. This is the pre-registration |
| 2 | `sample` | Draws the units to be labelled, deterministically |
| 3 | `ingest-labels` | Reads the labels back and **seals the content** |
| 4 | `estimate` | Computes the prevalence and its interval |
| 5 | `verify` | Re-checks the whole chain from the sealed record |
| 6 | `emit-report` | Writes the stamped report |

Steps 1 and 2 happen before anyone labels anything. Step 3 happens after the
humans have done their work. That gap is the point: the commitment is made
first.

## 4. Walk through it now, on real data

The repository ships a worked example on 97,320 real comments. From
`examples/real-data/`:

### Step 1 — pre-register the plan

```
$ prevalence-kit plan plan.yaml --run run
plan hash  1e3202a0b63093716993068cf1bb244b3249dd96a28cdba473bcfc81471fce9c
run        run
The plan is now pre-registered. Editing it will make `verify` refuse.
```

**Write that hash down, or publish it.** It is what proves later that the
question was fixed before the answer was known.

A plan is a small YAML file:

```yaml
estimand:
  description: Comments at least half of annotators called toxic
  label_field: toxicity
  positive_when: at_least
  threshold: "0.5"
population: frame.txt
design: srs
sample_size: 1000
labels: labels.csv
interval: clopper_pearson
seed: real-data-example-2026-08-31
```

Every field is part of the commitment. Change any of them and the hash changes,
which is the point — it makes a change visible instead of silent.

**`interval` has no default and the tool will not choose for you.** Under `srs`
the choice is `wilson` or `clopper_pearson`: Clopper-Pearson holds its stated
confidence level and is wider; Wilson is narrower and can fall below it. At
rare-event rates that trade is the whole decision, and §7 has the numbers.

### Step 2 — draw the sample

```
$ prevalence-kit sample plan.yaml frame.txt --run run
drew 1000 items from frame.txt
first three: cc-val-003997, cc-val-045312, cc-val-076939
```

The frame is one identifier per line — the whole population, no labels, no
content. The draw is a keyed hash of the seed and each identifier, not a random
number generator, so anyone can redraw exactly this sample in any language.

**Send those 1,000 identifiers to your labellers.** This is where the money and
the time go, which is why the tool refuses as early as it can.

### Step 3 — bring the labels back and seal the content

```
$ prevalence-kit ingest-labels plan.yaml labels.csv --run run
sealed 1000 items and recorded their labels
Content is encrypted at rest. Nothing prints it.
```

`labels.csv` needs `item_id` and your label column. A `content` column is
**optional**: include it and the text is encrypted at rest and never printed;
leave it out and the chain runs exactly the same. The shipped example leaves it
out deliberately.

### Step 4 — estimate

```
$ prevalence-kit estimate plan.yaml --run run
method     clopper-pearson
estimate   0.068000000000
95% CI     [0.053188099760, 0.085413050191]
n          1000  (68 positive)
```

### Step 5 — verify

This is the one to run before you quote the number anywhere.

```
$ prevalence-kit verify --run run --plan plan.yaml
  [ok] ledger chain: 4 entries, each linked to the one before
  [ok] run shape: each evidence step recorded once, in order: plan -> sample -> ingest-labels -> estimate
  [ok] plan (sealed copy): matches genesis hash 1e3202a0b6309371 (ledger entry 0)
  [ok] plan (working file): plan.yaml unchanged since the run opened
  [ok] sample: 1000 ids redrawn from the frame as a simple random sample, identical
  [ok] labels: 1000 labels, matching the drawn sample one-to-one
  [ok] sealed content: 1000 items: every chunk authentic, in order, none missing
  [ok] estimate method: estimate.json records clopper-pearson, matching the plan
  [ok] estimate: recomputed 0.068000000000 from the record, identical

verified: 9 checks, nothing out of place.
```

It **re-draws** the sample and **recomputes** the estimate from the sealed
record rather than re-reading the numbers. Exit 0 means all nine passed.

### Step 6 — emit the report

```
$ prevalence-kit emit-report plan.yaml --run run
wrote run/report.md
wrote run/report.json
Read the Honest Limits block before quoting the number.
```

Markdown for people, JSON for machines. Both carry every hash, the method, the
interval, and a mandatory honest-limits block.

## 5. Reading the report

Four things to look at, in this order.

1. **The interval, not the point estimate.** `6.800% (95% interval 5.319% to
   8.541%)`. The interval is the answer; the point estimate is its midpoint.
2. **The count.** `68 of 1000 sampled items were positive` — a real count of
   real labels. If that number looks impossible, stop and investigate; a
   discrepancy there once revealed a genuine defect in this tool.
3. **The *What that 95% actually delivers* block.** It names the measured worst
   coverage of the method you chose, the grid it was measured on, and where your
   run sits relative to that grid. It also says plainly that this is **not a
   coverage computed for your run**.
4. **The honest limits.** They are in the artifact, not in a footnote somewhere
   else, and they include the ones that hurt.

## 6. Verifying a number somebody else published

This is what the tool is for. Given their run directory and their plan:

```
prevalence-kit verify --run <their-run> --plan <their-plan.yaml>
```

You do not have to trust their report. `verify` redraws and recomputes from the
sealed record. If they published the plan hash before the results, and `verify`
says yes, the number is what their pre-registered plan produced.

**One limit, stated plainly:** `verify` recomputes through the same estimator
that produced the number, so it proves the record is intact and self-consistent.
It does not independently confirm that the estimator is right — that is what the
external witnesses and the coverage demonstration are for.

## 7. Choosing the interval, when the rate is low

At the rates this tool is built for, several ordinary intuitions fail. All of
these are measured, not asserted:

- Ask for a **95% Wilson** interval at a few times `1/n` and you can get one
  that covers **as little as 90.98%** of the time. Clopper-Pearson holds at or
  above its level and is wider for it.
- Under a **stratified** design **neither** interval holds its nominal level at
  rare rates, and often **no interval exists at all** — when every sampled unit
  comes back negative there is no spread to invert. `sample` tells you those
  odds in closed form **before** you pay for labels.
- If you supply sensitivity and specificity, an ordinary-sounding specificity
  makes the correction **undefined, not imprecise**: at 0.2% apparent
  prevalence you need specificity above **99.8%**.

`PROJECT_CHARTER.md` §8 carries all the figures with the conditions they were
measured under.

## 8. When it refuses

**A refusal is the tool working.** It exits 2, names a reason code, says what
happened and what to do. There are 38 codes, each pointing at one artifact.

Find your code's group here, then read the message — it names the file to open.

| If the code starts with | The problem is in | Typical fix |
|---|---|---|
| `PLAN_` | Your plan file, or its sealed copy | Fix the YAML; or restore the run directory |
| `FRAME_`, `LABEL_`, `LABELS_` | The data files you supplied | Check the frame is non-empty and the labels are numeric and match the draw |
| `SEAL_`, `LEDGER_`, `KEY_` | The run directory's integrity | Something changed after the fact, or the key is gone. This is the alarm working |
| `RUN_` | Which run directory you pointed at | One measurement per directory; use a fresh one |
| `STRATA_`, `STRATUM_`, `ALLOCATION_` | The stratified design or the frame's strata | Declare the strata, or change the allocation |
| `CORRECTION_` | The sensitivity/specificity pair, or its relationship to the sample | §7's third bullet is usually why |
| `EVIDENCE_NOT_PREREGISTERED` | The file you passed is not the file the plan names | Use the registered file, or write a new plan — which changes the hash, visibly |
| `ESTIMATE_METHOD_MISMATCH`, `INTERVAL_UNDEFINED`, `DESIGN_NOT_ESTIMABLE` | The estimate step | Read the message; each names its own cause |

Four worth knowing before you meet them:

- **`EVIDENCE_NOT_PREREGISTERED`** — you drew from, or labelled from, a file the
  plan does not name. It fires at `sample` and at `ingest-labels`, before the
  label budget is spent.
- **`ALLOCATION_TOO_THIN`** — a stratum got fewer than 2 units, so its variance
  is undefined. Two is the floor and the message says which stratum.
- **`CORRECTION_UNDEFINED`** — sensitivity + specificity ≤ 1. There is no
  corrected estimate that exists, not one being withheld.
- **`INTERVAL_UNDEFINED`** — every sampled unit had the same label under a
  stratified design. The point estimate stands; there is nothing to invert.

## 9. Things that will bite you

- **One run directory per measurement.** Re-running `plan` into a used
  directory refuses.
- **The sealing key lives in the run directory** and is not backed up anywhere.
  Lose it and the sealed content is gone — the digests still verify, the text
  does not come back. `SECURITY.md` §3.1 is the full story.
- **Do not edit the plan mid-run.** `verify` will notice, which is the feature.
- **Paths are recorded as you type them.** Run with relative paths from the
  run's own directory, or your directory structure ends up in a report you
  publish. `SECURITY.md` §3.8.
- **The estimand is a definition, not a discovery.** `toxicity >= 0.5` and
  `toxicity >= 0.9` measure different things. Whoever reads your number needs
  the threshold, and it is in the hash.

## 10. What this procedure does not cover

Building the sampling frame; recruiting or calibrating labellers; deciding the
policy the labels encode; and estimating sensitivity and specificity — this tool
consumes those two figures, it does not estimate them. Each is real work and
none of it is here.
