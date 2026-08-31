# Changelog

All notable changes to this project are recorded here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and
this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**This file is a summary for people who will not read the record.** The record is
the authority and it is far more detailed: `docs/DECISIONS.md` says why each
choice was made and what was rejected, `docs/CORRECTIONS.md` lists every claim
this project got wrong and who got it wrong, and the phase contracts under
`docs/contracts/` define what "done" meant at each stage. Nothing here replaces
them.

## [Unreleased]

Nothing yet.

## [1.0.0] — 2026-09-01

The first release. Everything below was built across Phases 0 to 3, under a
governed process in which the director wrote none of the code and all of the
decisions.

**Rehearsed before it was released.** Three release candidates were cut against
TestPyPI and a separate container registry path before anything reached PyPI or
the real image name. Two failed and are kept in the record —
`docs/contracts/PHASE-3-REHEARSAL.md` says what broke and why. The release
artifacts carry SLSA provenance attestations, verified as an outsider would
verify them, with negative controls that had to fail: a wrong repository and a
tampered artifact both refuse.

### Added

- **Six verbs**: `plan`, `sample`, `ingest-labels`, `estimate`, `verify`,
  `emit-report`. A plan is hashed before any data is touched; content is sealed
  on ingest; every step is written to a hash-chained ledger; `verify` re-checks
  the whole chain from the sealed record.
- **Simple random and stratified sampling**, deterministic under a recorded seed
  by keyed hash rather than a pseudo-random generator, so an outsider can redraw
  the same sample in any language.
- **Neyman allocation** with declared largest-remainder rounding, validated
  against R `survey` 4.5 and Python `svy` 0.25.0.
- **Wilson and Clopper-Pearson intervals** under a simple random design;
  **design-based Wilson and Korn-Graubard** under a stratified design. The plan
  names the method and there is no default.
- **Rogan-Gladen misclassification correction** from pre-registered sensitivity
  and specificity, with named refusals where the correction is undefined or
  leaves [0, 1].
- **38 named refusal reasons**, each with a negative and a positive control, and
  a distinct code so an operator knows which artifact to open.
- **Coverage demonstration** on Civil Comments (1,999,514 rows), pre-registered
  and hashed before the corpus was fetched: `demo/`.
- **A containerised runtime** and a step-by-step SOP, so the tool can be run
  without a Python installation.

### Known limits

Carried unchanged from `PROJECT_CHARTER.md` §8 and stated in the README and in
every report the tool emits. The two that most often surprise people:

- At rare-event prevalence an ordinary-sounding specificity makes the
  Rogan-Gladen correction **undefined, not merely imprecise** — 0.2% apparent
  prevalence needs specificity above 99.8%.
- **The stratified intervals do not hold their nominal level at rare rates**, and
  the interval frequently does not exist at all. The measured figures are in the
  charter, and `sample` states the odds before the label budget is spent.

[Unreleased]: https://github.com/MohdSaifHussain/prevalence-kit/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/MohdSaifHussain/prevalence-kit/releases/tag/v1.0.0
