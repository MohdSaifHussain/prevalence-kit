# The release rehearsal — a dated reading

**Date: 31 August 2026** · **Deliverable: D3.7** · **Tree: `b501abe`** ·
**Candidate version: `1.0.0rc1`** · **Status: the reading. Not clean. Two
candidates cut, both failed, and the second failed on a blocker only the
director can clear.**

**This file is a dated reading and is never edited.** Corrections go in
`docs/CORRECTIONS.md` with the date and the direction the number moved.

**Nothing irreversible happened.** No tag exists, nothing reached PyPI or
TestPyPI, no image was pushed to any registry. The repository went public
earlier the same day on the director's word — D-46's first step — and that is
the only step of the release order that has been taken.

## What a rehearsal is for, and what this one found

R3.1: no irreversible act without a clean rehearsal, and *a rehearsal that skips
the risky steps proves only the safe ones*. So `release.yml` runs the **full**
path on a manual dispatch — build, SBOM, provenance attestation, upload — and
only a tag reaches PyPI proper.

**It found two defects and one blocker in two runs.** That is the process
working: every one of them would otherwise have been met for the first time
during the irreversible act.

## Candidate 1 — run `33424417661`, head `354f128`. FAILED.

| Step | Result |
|---|---|
| Build sdist and wheel | success |
| **Software bill of materials** | **failure** |
| Attest build provenance | skipped |
| Publish | skipped |

```
cyclonedx-py: error: unrecognized arguments: --outfile dist/prevalence-kit.cdx.json
```

**`--outfile` is not an argument that tool has.** The flag is `-o` /
`--output-file`. It was written from memory rather than from the tool's own
help — the same class as the `docker run --entrypoint id -u` argument-order
defect two commits earlier, and the second time in one session that a command
line was composed rather than checked.

**Fixed, and the fix was run locally before it was pushed**: CycloneDX
specVersion 1.6, five components — `cffi`, `click`, `cryptography`, `pycparser`,
`pyyaml` — which is the locked runtime set exactly and nothing else.

## Candidate 2 — run `33424603765`, head `b501abe`. FAILED, at the last step.

| Step | Result |
|---|---|
| Build sdist and wheel | success |
| Software bill of materials | success |
| Attest build provenance | **success** |
| Keep the artifacts | success |
| **Publish to TestPyPI** | **failure** |

```
Trusted publishing exchange failure:
* `invalid-publisher`: valid token, but no corresponding publisher
```

**This is a configuration action on TestPyPI, not a defect in this repository.**
Trusted publishing means no API token exists to leak; the price is that the
publisher must be registered on TestPyPI before the first upload. It has not
been. **Only the account holder can do it**, so the rehearsal stops here.

**The exact claims TestPyPI needs**, taken from the failing run rather than
from documentation:

| Field | Value |
|---|---|
| PyPI Project Name | `prevalence-kit` |
| Owner | `MohdSaifHussain` |
| Repository name | `prevalence-kit` |
| Workflow name | `release.yml` |
| Environment name | `testpypi` |

The same registration is needed on PyPI proper, with environment `pypi`, before
the real publish.

**Both were completed by the director on 1 September 2026** and verified against
`release.yml`. **And a pending publisher does not reserve the name.** PyPI's own
documentation is explicit that a pending publisher creates the project only when
it is first used to publish — so registering it holds nothing. Phase 0's
name-collision check was never a reservation either; it was a check that the
name was free on the day it was run. **`prevalence-kit` is unheld on PyPI until
v1.0 actually ships**, and anyone could take it before then. Recorded because
this project has been wrong before about what a check establishes, and "we
checked the name" is exactly the kind of sentence that quietly becomes "we have
the name".

**A second environment gap, found before it could burn a candidate.**
`release.yml` declares `environment: pypi` on a tag push and `testpypi`
otherwise, and **a job naming an environment that does not exist fails before it
reaches the index** — which would have looked like a publish failure and been
neither. Checked in repository settings on 1 September: **`testpypi` existed,
`pypi` did not.** `pypi` was created. Neither carries a protection rule, so
neither gates the run; they exist so the OIDC subject claim matches what the
publishers were registered against.

## The controls — and the first attempt at them proved nothing

Everything up to the upload succeeded on candidate 2, so the artifacts and their
provenance attestation exist and could be verified as an outsider would.

**The first run of these controls reported exit 0 for controls that were meant
to fail.** The commands were piped into `tail`, so `$?` reported *tail's* status
rather than `gh`'s. Both negatives printed the right error and claimed success —
**a control that cannot fail, which is exactly C-27's and C-49's shape**, found
here in the rehearsal's own instrument. Re-run capturing each exit code directly:

| Control | Command | Expected | Exit |
|---|---|---|---|
| **Positive** | `gh attestation verify <wheel> --repo MohdSaifHussain/prevalence-kit` | pass | **0** |
| **Negative 1 — a provenance mix-up** | the same wheel, `--repo MohdSaifHussain/finding-bridge` | fail | **1** |
| **Negative 2 — a substituted release** | one byte appended to the wheel, real repo | fail | **1** |

**Both negatives reproduce a state a real failure would produce**, which is
rule 21's bar rather than merely turning something red. Negative 1 is an
artifact presented as coming from a repository it did not come from. Negative 2
is the artifact altered after signing: its digest changes, so no attestation
matches it, and the verification fails for that reason and not another. **C-52
is the same principle already paying**: the container workflow runs the tool
rather than merely building it, and that is what caught a documented command
that fails on Linux.

## What is rehearsed, and what is not

**Rehearsed and working:** the build, the SBOM over the locked dependencies, the
provenance attestation, the artifact retention, and verification of that
attestation as an outsider would perform it — including two negative controls
that fail for the right reason.

**Not rehearsed, and named rather than implied:**

- **The TestPyPI upload itself.** Blocked on the trusted-publisher registration
  above. Until it runs, *nothing about the upload path is proven* — not the
  metadata, not the filename acceptance, not the response.
- **The container push to a registry.** `container.yml`'s publish job is
  tag-triggered, and **no tag will exist until Q34 is ruled** — GHCR is a third
  publish channel that D-43 never authorised. The image itself is built and
  exercised on every push, including the negative control, but **it has never
  been pushed anywhere.**
- **The PyPI publish**, which by D-43 follows a clean TestPyPI rehearsal.
- **The GitHub release object**, which the tag creates.

## What has to happen before a third candidate

1. The director registers the pending publisher on TestPyPI with the claims
   above.
2. **Q34 is ruled**, so the registry channel is authorised and its rehearsal
   target is named.
3. **Q33 is ruled** — not a release blocker, but it is an operator-facing
   message that is wrong, and it ships with v1.0 if it is not settled.

Then candidate 3 runs the full path, and the same three controls run against
what it produces.
