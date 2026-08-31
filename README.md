# prevalence-kit

[![gate](https://github.com/MohdSaifHussain/prevalence-kit/actions/workflows/gate.yml/badge.svg?branch=main)](https://github.com/MohdSaifHussain/prevalence-kit/actions/workflows/gate.yml)
[![witness](https://github.com/MohdSaifHussain/prevalence-kit/actions/workflows/witness.yml/badge.svg?branch=main)](https://github.com/MohdSaifHussain/prevalence-kit/actions/workflows/witness.yml)
[![tests: 745 collected](https://img.shields.io/badge/tests-745%20collected-informational)](tests/)
[![gate checks: 7](https://img.shields.io/badge/gate%20checks-7-informational)](.github/workflows/gate.yml)
[![reason codes: 38](https://img.shields.io/badge/reason%20codes-38-informational)](src/prevalence_kit/errors.py)
[![AI in the evidence path: none](https://img.shields.io/badge/AI%20in%20the%20evidence%20path-none-success)](tests/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)](pyproject.toml)

**Every number in those badges is asserted by a test.** Change the test count,
the gate, or the reason codes without changing the badge and the build fails —
`tests/test_record.py`. A badge nobody checks is a decoration.

**Pre-release. Phase 3 of 4 in progress. Nothing here is ready to rely on yet.**

Audit-grade prevalence measurement for Trust & Safety.

You give it a sampling plan and human labels. It gives back a prevalence estimate, an honest
confidence interval, a sealed copy of the content, a tamper-evident record of every step, and a
stamped report.

**No AI ever touches the evidence or the estimate.**

## Does the method hold? Checked against a truth anyone can recompute

![Interval coverage on Civil Comments, by census prevalence](demo/coverage_curve.svg)

Civil Comments (CC0, 1,999,514 rows) carries continuous human annotation scores, so once a
threshold is fixed the true prevalence is knowable **by census**. Four thresholds were
pre-registered and hashed **before the corpus was fetched** — the commitment is
[`demo/preregistration.json`](demo/preregistration.json), and the commit that carries it predates
the download. Then 10,000 simple random samples of n = 1000 per threshold, each judged by both
shipped intervals against the census truth.

Clopper-Pearson covered at or above its nominal 95% at all four points, paying in width as the
rate rarefies. Wilson sat below nominal at the two commoner rates and above it at the two rarer
— nowhere below by more than the demonstration's own Monte Carlo error. The worst cases live in
the swept grid, not in four blind points. The full account — census counts, coverage tallies,
digests, and what these four points do *not* establish — is
[`demo/READING.md`](demo/READING.md). One run also went through the full sealed chain,
pre-registration to stamped report, on real comment text:
[`demo/full_chain/report.md`](demo/full_chain/report.md), with `verify` returning nine checks
and exit 0.

Platforms that publish prevalence this way cannot publish this demonstration, because their
truths are confidential. This one is reproducible by anyone.

## What this is, and what it is not

**It is the governance, label-quality and audit layer.** Pre-registration, sealed content, a
chain that can say no, and a report an auditor can check.

**It is not a survey-statistics library, and [`svy`](https://github.com/samplics-org/svy) is
the estimator layer.** `svy` covers stratified sampling, Neyman allocation, Wilson and
Clopper-Pearson intervals, Taylor linearization, post-stratification, and it is good.
R [`survey`](https://cran.r-project.org/package=survey) has covered this ground since 2003.
**Every estimator here is validated against the external witness that genuinely implements the
same quantity** — R `survey` for the stratified estimator, base R for Clopper-Pearson, `epiR`
for the misclassification correction, `svy` for the allocation and the design intervals — and
the record says which witnesses what, because a witness that implements a different quantity
witnesses nothing. We do not claim to fill an estimator gap, because there isn't one. We ship our own lean implementations for one recorded reason: `svy`
depends on an HTTP client, and this tool proves *zero network capability at runtime* with a
test that would fail the moment one entered the dependency tree.

What neither library does is seal content, keep a tamper-evident record, or refuse to print a
number it cannot defend. That is the gap.

## Six verbs

| Verb | What it does |
|---|---|
| `plan` | Hash the measurement plan before any data is touched. Pre-registration: the plan cannot quietly change after results are seen |
| `sample` | Draw the sample the plan describes — simple random, or stratified with Neyman allocation — deterministically under the recorded seed |
| `ingest-labels` | Read human labels; **seal the content on ingest**. Encrypted at rest, safe preview only, every unseal logged |
| `estimate` | Compute prevalence with the interval **the plan names — there is no default**, and an optional Rogan–Gladen correction from pre-registered sensitivity and specificity. Refuses, by name, rather than print a number it cannot defend |
| `verify` | Re-check the whole chain: plan hash, sample redraw, ledger integrity, estimate recomputation. It can say no, so its yes means something |
| `emit-report` | Stamped Markdown and JSON with every hash and a mandatory Honest Limits block |

The shipped example under [`examples/synthetic/`](examples/synthetic) runs the whole chain in
seconds.

## Getting started

```
git clone https://github.com/MohdSaifHussain/prevalence-kit
cd prevalence-kit
pip install -e .
prevalence-kit --version
```

Or run it with no Python installation at all:

```
docker build -t prevalence-kit .
docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/work" prevalence-kit --version
```

On Linux and macOS the `--user` flag is required when you mount a directory —
the image runs unprivileged and a bind mount keeps the host's ownership.
[`docs/SOP.md`](docs/SOP.md) §2 explains it.

Then measure something real. A complete run on 97,320 real comments, offline, in
about a second:

```
cd examples/real-data
prevalence-kit plan          plan.yaml            --run run
prevalence-kit sample        plan.yaml frame.txt  --run run
prevalence-kit ingest-labels plan.yaml labels.csv --run run
prevalence-kit estimate      plan.yaml            --run run
prevalence-kit verify        --run run --plan plan.yaml
prevalence-kit emit-report   plan.yaml            --run run
```

That answers **6.800%, 95% interval 5.319% to 8.541%** — and because that
population is fully labelled, the census truth is knowable: **7.8822%**, inside
the interval. [`examples/real-data/`](examples/real-data) has the whole account,
and [`examples/`](examples) explains why there are two examples and what each is
for.

**[`docs/SOP.md`](docs/SOP.md) is the full procedure**: every step, how to read
the report, how to verify someone else's number, and what each refusal means.

## At the rates this tool is for, several ordinary intuitions fail

These are one fact family, not scattered caveats, and every one was met in the artifacts rather
than reasoned into being.

- **An ordinary-sounding specificity makes the correction undefined, not imprecise.** At an
  apparent prevalence of 0.2%, the Rogan–Gladen correction needs specificity above **99.8%**.
  "99%" sounds excellent — and at that rate produces five times more apparent positives from
  clean content than the whole sample held, driving the corrected estimate negative. The tool
  refuses and names the figure you need. Below Se + Sp = 1 the arithmetic inverts outright:
  the method's own reference implementation prints a lower bound **above** its upper bound,
  with no warning. Ours refuses there too, by name.
- **A rare-event measurement that finds nothing is the product, not a failure.** Zero positives
  with a good test yields a point estimate of 0 and a real, defensible upper bound. The tool
  prints it. (An early design would have refused this as "no information"; it was struck.)
- **Under a stratified design at rare rates, the interval frequently does not exist at all** —
  every unit comes back negative, the design standard error is zero, and there is nothing to
  invert. `sample` computes those odds in closed form from the plan's own expectations and says
  them **before the label budget is spent**.
- **A corrected interval's lower bound can go negative while the estimate is fine.** The tool
  clamps to [0, 1], **says so in the output**, and keeps the raw bound in the ledger so an
  auditor sees what the arithmetic produced before policy touched it.
- **The interval you choose has a coverage cost, and at rare rates it is large.** Ask for a 95%
  Wilson interval and you can get one that covers **as little as 90.98%** of the time at the
  rates this tool is built for — measured, not asserted, and rounded *down* because a bound is
  rounded in the direction that keeps it true. Clopper-Pearson holds its level and is wider for
  it. **That is why the plan must name the method: a default would be this project choosing,
  for an operator who did not know there was a choice.**

## Honest limits

- It measures prevalence of labeled samples from a defined population. It **cannot fix a bad
  sampling frame, biased labels, or a dishonest plan.** It can only make them visible and
  permanent in the record.
- **Interval guarantees are sampling-only.** They do not account for rater quality — the same
  caveat YouTube publishes for its Violative View Rate.
- **The corrected interval treats the sensitivity and specificity you supply as exact.** The
  method that propagates their uncertainty (Lang & Reiczigel 2014) is a plan-schema change,
  deliberately not in v1.0.
- **The stratified intervals do not hold their nominal level, and at rare rates the gap is
  large** — measured by exhaustive enumeration, with the 96-point table in the
  [charter §8](PROJECT_CHARTER.md). Korn–Graubard is the better of the two and still does not
  hold. Neither is Clopper-Pearson, whose guarantee does not survive the approximation.
- **What we ship is limited by what we can witness.** Our own anchor recommends Jeffreys and
  Agresti–Coull; neither has a witness in the libraries we validate against, so we ship
  neither. The methods here are the ones we can prove, not the ones the anchor prefers.
- **No EU regulation requires the number this tool produces.** The word "prevalence" appears
  zero times in the Digital Services Act and zero times in Implementing Regulation (EU)
  2024/2835. What those do mandate is classifier accuracy, precision and recall — and, in the
  guidance, sensitivity and specificity. This tool shows what those mandated quantities do to a
  prevalence estimate.
- Validation is on synthetic data and one public dataset. **No claim of production deployment.**
- Built by directing an AI under a governed process. The director wrote none of the code and
  all of the decisions, and the record below — including a corrections register that counts the
  errors by who made them — is part of the deliverable.

## Not in v1.0

Not a classifier, detector, or moderation system — it measures and never judges content. Not a
survey-statistics library. No dashboards, no daemon, no cloud: a CLI that reads files and
writes files. No importance sampling or ML-assisted weights. No DSA-shaped report emitter.

## Where to get help

- **[`docs/SOP.md`](docs/SOP.md)** — the full procedure. §8 lists what every
  refusal means and what to do about it.
- **[Issues](https://github.com/MohdSaifHussain/prevalence-kit/issues)** — there
  is a template for reporting that **a claim here is wrong**, which is the most
  useful issue this project can receive.
- **[`SECURITY.md`](SECURITY.md)** — how to report a vulnerability privately, and
  §3 states what this tool deliberately does **not** protect against. Some of
  what looks like a vulnerability is a documented limit.
- **[`PROJECT_CHARTER.md`](PROJECT_CHARTER.md)** — what is in scope, what is not,
  and every measured figure with the conditions it was measured under.

## Who maintains it

Built and maintained by [Mohd Saif Hussain](https://github.com/MohdSaifHussain).

[`CONTRIBUTING.md`](CONTRIBUTING.md) explains what is most useful to contribute
and the rules that shaped this codebase, and
[`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) applies to everyone taking part.

## The record

Every claim above is checked against a primary source and pinned by version, date or DOI.

| | |
|---|---|
| [`PROJECT_CHARTER.md`](PROJECT_CHARTER.md) | What is being built, and the cap on it |
| [`docs/PHASE-0-VERIFICATION.md`](docs/PHASE-0-VERIFICATION.md) | 24 claims checked; 6 defects found and recorded |
| [`docs/STANDARDS.md`](docs/STANDARDS.md) | Every source, pinned |
| [`docs/DECISIONS.md`](docs/DECISIONS.md) | Why each choice was made, and what was rejected |
| [`docs/CORRECTIONS.md`](docs/CORRECTIONS.md) | What we got wrong, and where it came from |
| [`docs/FINDINGS.md`](docs/FINDINGS.md) | Every accepted finding and the test that closes it |
| [`docs/SOP.md`](docs/SOP.md) | How to run a measurement, end to end |
| [`SECURITY.md`](SECURITY.md) | What it protects, from whom, and what it does not |
| [`CHANGELOG.md`](CHANGELOG.md) | What changed, release by release |

## Licence

MIT. See [`LICENSE`](LICENSE), and [`NOTICE`](NOTICE) for the third-party
material this repository redistributes and the conditions attached to it.
