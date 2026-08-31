# prevalence-kit 1.0.0

**Released 1 September 2026.** The first release.

Audit-grade prevalence measurement for Trust & Safety. You give it a sampling
plan and human labels; it returns an estimate, an honest interval, sealed
content, a tamper-evident record, and a stamped report. **No AI touches the
evidence or the estimate.**

## Install

```
pip install prevalence-kit
```

```
docker pull ghcr.io/mohdsaifhussain/prevalence-kit:1.0.0
```

On Linux and macOS, mount a working directory and pass your own uid, because the
image runs unprivileged:

```
docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/work" \
  ghcr.io/mohdsaifhussain/prevalence-kit:1.0.0 --version
```

`docs/SOP.md` is the full procedure, end to end, including what every refusal
means and what to do about it.

## What it does

Six verbs — `plan`, `sample`, `ingest-labels`, `estimate`, `verify`,
`emit-report`. The plan is hashed before any data is touched, so the question is
fixed before the answer is known. Content is sealed on ingest. Every step is
written to a hash-chained ledger. `verify` re-draws the sample and recomputes the
estimate from the sealed record, and it can say no — which is what makes its yes
worth anything.

- Simple random and stratified sampling with Neyman allocation, deterministic
  under a recorded seed by keyed hash, so anyone can redraw the same sample in
  any language.
- Wilson and Clopper-Pearson under a simple random design; design-based Wilson
  and Korn-Graubard under a stratified one. **The plan names the method and
  there is no default.**
- The Rogan-Gladen misclassification correction from pre-registered sensitivity
  and specificity, with named refusals where the correction is undefined.
- **38 named refusal reasons**, each with a negative and a positive control, and
  a distinct code so an operator knows which artifact to open.

## Verifying this release

Every artifact carries a SLSA provenance attestation. Check one:

```
gh attestation verify prevalence_kit-1.0.0-py3-none-any.whl \
  --repo MohdSaifHussain/prevalence-kit
```

And the image:

```
gh attestation verify oci://ghcr.io/mohdsaifhussain/prevalence-kit:1.0.0 \
  --repo MohdSaifHussain/prevalence-kit
```

**A verification that cannot fail proves nothing**, so try one that must: pass
`--repo` for a repository the artifact did not come from, or append a byte to the
file. Both refuse. That check was run against these artifacts before they were
published and again afterwards.

A CycloneDX SBOM over the locked runtime dependencies is attached to this
release.

## Does the method hold?

Yes, and you can recompute it. The coverage demonstration draws 10,000 samples
per threshold from Civil Comments (CC0, 1,999,514 rows), where the true
prevalence is knowable **by census**, and compares each interval against that
truth. The thresholds were pre-registered and hashed **before the corpus was
fetched**.

Clopper-Pearson covered at or above its nominal 95% at all four points, paying in
width as the rate rarefies. Wilson sat below nominal at the two commoner rates
and above it at the two rarer — nowhere below by more than the demonstration's
own Monte Carlo error. `demo/READING.md` carries the counts, the tallies, the
digests, and what four points do *not* establish.

## Read the limits before quoting a number

They are in the tool's own output, not only here.

- **At rare rates an ordinary-sounding specificity makes the Rogan-Gladen
  correction undefined, not imprecise.** 0.2% apparent prevalence needs
  specificity above **99.8%**.
- **The stratified intervals do not hold their nominal level at rare rates**, and
  often no interval exists at all. `sample` tells you those odds in closed form
  before the label budget is spent.
- **A 95% Wilson interval can cover as little as 90.98%** at the rates this tool
  is built for. Clopper-Pearson holds its level and is wider for it.
- **Interval guarantees are sampling-only.** They do not account for rater
  quality — the same caveat YouTube publishes for its Violative View Rate.
- **`verify` recomputes through the same estimator that produced the number.** It
  proves the record is intact; it does not independently confirm the estimator.
- **No external security audit. No production deployment claim.** Validation is
  synthetic data and one public dataset.

`PROJECT_CHARTER.md` §8 carries every measured figure with the conditions it was
measured under.

## How this was built

By directing an AI under a governed process. **The director wrote none of the
code and all of the decisions**, and the record of that is part of what ships:
`docs/DECISIONS.md` says why each choice was made and what was rejected;
`docs/CORRECTIONS.md` lists every claim this project got wrong, who got it wrong,
and in which direction.

**This release was rehearsed before it was made.** Three candidates were cut
against TestPyPI and a separate container registry path; two failed.
`docs/contracts/PHASE-3-REHEARSAL.md` says what broke and why, because a
rehearsal whose failures are deleted is not evidence of anything.

## Not in 1.0

Not a classifier, detector, or moderation system — it measures and never judges
content. Not a survey-statistics library:
[`svy`](https://github.com/samplics-org/svy) is the estimator layer and this
project says so. No dashboards, no daemon, no cloud. No importance sampling or
ML-assisted weights. No DSA-shaped report emitter.

## Licence

MIT. `NOTICE` records the third-party material this repository redistributes and
the conditions attached to it.
