# Phase 3 contract — flagship demo and launch

**Status: APPROVED — 31 August 2026. Q16–Q25 all ruled by the director the same day; the
rulings are written into each question below, marked RULED.** Drafting this contract was the
first build act of the phase, per the Phase 2 close. The commit that lands it also updates the
phase sentence in `README.md` and `CLAUDE.md`, because creating this file moves the phase the
sentence must state, and the gate reads both.

**The boundary commit was red until Q24 and Q25 were ruled, and the redness was evidence.**
Creating this file made Phase 3 the live phase, and two instruments did not survive the event
they exist to track: `check_open_items` lost sight of every discharge recorded in the Phase 2
contract — its own selftest caught it, **Q24** — and four of the C-47 tests anchored on the
live tree's phase state, so two asserted stale constants and two planted their violation
against a sentence that no longer existed, silently planting nothing (**Q25**, corrections
**C-48** and **C-49**). The tree was held uncommitted and red on exactly these until the
rulings; the fixes land in the same commit as this contract, so the boundary commit is green
and atomic. The reviewer reproduced all three findings against the tree before the rulings.

| | |
|---|---|
| **Phase** | 3 of 4 — the last |
| **Name** | Flagship demo and launch |
| **Tier** | **STANDARD carried in**, per the ruling of 2026-08-30. **The re-ask is D3.2 and is genuinely open** — see §9 |
| **Proposed** | 31 August 2026 |
| **Governing charter** | `PROJECT_CHARTER.md`, ratified 2026-08-28 |
| **Predecessor** | Phase 2 — closed 31 August 2026, exit evidence `docs/contracts/PHASE-2-HAND-RUN.md`, tree at close `cad419c` |

---

## 1. Objective

**Show the method holds, then let strangers check everything — and rehearse every act that
cannot be taken back before taking it.**

Phases 0–2 built a tool that refuses well and proved its arithmetic against witnesses. Nothing
in them was irreversible. Phase 3 is different in kind, and the contract says so up front:

> **Phase 3 performs this project's first irreversible acts** — a tag, a publish, a repository
> going public, and a pull request to someone else's repository. The record itself becomes a
> published artifact, read by people it was not written for.

Exit criterion, in one line: **the published artifacts verified by the director's own hand as an
outsider would verify them, including a negative control that failed — after a rehearsal that
did the same.**

## 2. What makes this phase different, named before the deliverables

1. **The first irreversible acts.** Everything before could be re-cut. A tag can be moved but
   its move is visible; a publish cannot be unpublished; a PR to ROOST is a message sent.
   Doctrine rule 6 — rehearse the irreversible — has had nothing to bite on until now.
2. **The record goes public, backwards.** The git history publishes with the tree, and this
   history is not rewritten — the record cites commit hashes as evidence throughout. **O-28**
   is the one-time review of that history before it is shown, and it is a deliverable of this
   contract, before any release. One thing it will find is already recorded: committed local
   Windows paths in five documents, two of them dated readings that are never edited. That is
   a disclosure question, not a find-and-replace — **Q19**.
3. **The tier re-ask finally has something to decide.** Discharged twice by naming an absence;
   both times honest because those phases shipped nothing to rehearse. **No forecast is
   recorded, by the ruling of 2026-08-30**, and this contract offers no recommendation on it
   for the same reason — a builder recommendation would be the forecast that ruling declined
   to record. **Q16.**

## 3. Deliverables

Each names the top standard it must follow. Order is deliberate: O-19 first, the demo and its
README before the stop, everything public after it.

| # | Deliverable | Governing standard |
|---|---|---|
| **D3.1** ▸ **DONE 2026-08-31 — and the re-read came first, as ruled.** The premise was half false when written (**C-50**): checkout v5.0.0 declared node24 at its own SHA. Re-pinned to checkout v7.0.1 (`3d3c42e...`) and setup-python v7.0.0 (`5fda3b9...`), both declaring node24 at the pinned SHA, both workflows, TW-4 clear | **O-19 — re-pin the CI actions, after re-reading the premise.** TW-4 watches for GitHub *dropping* Node 20; the last run's log already reports `setup-python` being *forced onto Node 24*, so the tripwire's premise has **partly happened** rather than merely approached. First: re-derive the current state from a live run log and the actions' release pages, not from the tripwire's text. Then re-pin `actions/checkout` and `actions/setup-python` **by SHA** to current majors in both workflows, verify the SHAs against the tags on GitHub, and re-run both workflows green — `witness.yml` must still regenerate every fixture byte-identically. TW-4 then clears or restates itself from the workflow file it reads | Charter §5.1 · TW-4 · **O-19** |
| **D3.2** ▸ **DONE 2026-08-31 — STANDARD, D-42** | **The tier re-ask — a ruling, not a paragraph.** Ruled at **Q16** with the forward-looking question answered too: *the practice matters and the label does not*, and the practices FULL would buy are bound by D3.7/D3.8/R3.1/R3.2 at either tier. The first re-ask with something irreversible to decide, and it was decided rather than defaulted | D-1 · charter §7 · **D-42** |
| **D3.3** | **The coverage demonstration — the flagship.** Civil Comments (CC0 1.0, 1,999,514 rows), truth knowable by census at each **pre-registered threshold, hashed before any data is touched**. Many samples, an interval each time, coverage against the census truth, at multiple thresholds across the prevalence range including the rare end — **the sensitivity curve, plotted**. Design details at **Q18**. The generating script, environment and exact calls recorded to S-8's bar; the artifact committed, like every fixture | Charter §6.3 · R-7 / D-11 · S-1.1 |
| **D3.4** | **The README, finished, and the docs with it.** The coverage plot on the front page. `svy` credited as the estimator layer — **closes C-1** under T-1 at the phase close. **O-21**: the rare-event facts grouped and introduced as **one thing** — *at the prevalence rates this tool is for, several ordinary intuitions fail, and here they are* — per the Q6 cluster note, not three scattered caveats. Charter §8's limits carried unchanged; the not-in-v1.0 list from charter §4; the provenance sentence — the director wrote none of the code and all of the decisions | **O-21** · C-1 · charter §8 · R2.7's rule carried as R3.4 |
| **D3.5** | **O-28 — the git-history review.** A one-time look backwards over the full history as a stranger would read it, before anything is public. Findings reported to the director with proposed dispositions; **the director rules each**, including the recorded local-paths finding (**Q19**). The review's reading is written down and dated. **Nothing goes public before the director closes this review** | **O-28** · CLAUDE.md rule 20 · SECURITY.md §3.8 |
| **D3.6** | **Instrument work, both halves proved to fail.** (a) **Restore `check_figures`' phase claim**: C-47's rebuild added the canonical two-file sentence check and left the superseded `readme phase` entry beside it — number-only, vacuous since the close, the exact semantics C-47 condemned. Resolve at **Q21**, selftest proving the survivor fails in both directions. (b) The CLAUDE.md open-corrections row: stale at this drafting (says 49 entries, 6 open; the register holds 50, 7 open) while crediting a checker that does not read it — **Q22** rules the correction entry and the machinery | Rule 14 · rule 7 · C-47 · C-34's class |
| **D3.7** | **The release rehearsal.** A release candidate that executes the **full** publish path — build, SBOM, attestation, signing, upload to the rehearsal target — not a subset. The director hand-verifies its artifacts as an outsider: fresh download, run the published instructions exactly as written. **A negative control that must fail**, built to rule 21's bar: it reproduces the state a real compromise or mix-up would produce, and if the check it exercises were deleted, nothing else would catch it. Run at the final candidate **and again after the real act**. Every failed candidate stays in the record | Doctrine rule 6 · rule 21 · Template 6 |
| **D3.8** | **The release.** Tag and publish to the ts-sentry supply-chain bar: hash-locked dependencies, SHA-pinned actions, SBOM, signed artifacts with provenance attestation. Channels ruled at **Q17**; ordering of repo-public against the tag at **Q20**. Performed only after a fully clean rehearsal **and** the director's explicit word, and re-verified the same way afterwards. Anything the constraints make unachievable is stated plainly, never implied done | Charter §5.1 · ts-sentry precedent |
| **D3.9** | **The ROOST pull request.** One PR to `awesome-safety-tools`, adding prevalence-kit to the directory that has fourteen categories and no measurement. **The PR text is approved by the director verbatim before submission** — it is a message sent under his name to someone else's project. Submitted last, after the release it points at exists (Q20) | Charter §3 · doctrine: outward acts gated |
| **D3.10** | **Post-release closure.** T-1 closes C-1 and C-42–C-47 (and anything newer), each naming its discharging commit. O-14 / O-15 get their final disposition (**Q23**). The outcome section written **at** the close, evidence per checklist row; the phase sentence flips to `Phase 3 of 4 complete` in both public files, which the gate enforces in both directions | Rule 11 · T-1 (D2.12) · C-47's check |

**Not a deliverable, deliberately:** any change to the estimators, the refusal codes, the plan
schema, or `verify`. Phase 2 closed in both directions. A defect found in them during this phase
is a finding for the director, not a reopening.

## 4. Requirements

**R3.1 — No irreversible act without a clean rehearsal first.** The rehearsal executes the full
path, the director verifies its artifacts by hand, and its negative control **fails for the
right reason** — rule 21: the control reproduces the state the real failure would produce, not
merely a state that turns something red. The real act follows only on the director's explicit
word, and is re-verified the same way.

**R3.2 — Nothing goes public before O-28 is closed by the director.** Repo visibility, tag,
publish, PR — all of it waits.

**R3.3 — Every number in a public artifact is re-derived from its generating artifact before it
is written, and cites it.** The README's figures name their fixture, measurement or run. Rule 4
has bitten this project ten times; the README is where it would bite a stranger.

**R3.4 — Limits carry forward unchanged.** Charter §8 and SECURITY.md §3 reach the README
whole. A limit is narrowed only when it genuinely narrowed, and the change is stated.

**R3.5 — The coverage demonstration is pre-registered like any measurement this tool takes.**
Thresholds, sample sizes, replication counts and seeds fixed and hashed before the corpus is
touched. The corpus itself is fetched by a recorded procedure and pinned by digest — it is not
committed. Retrieval to S-8's bar.

**R3.6 — The whole gate, after anything that writes to the tree, and that run is what is
reported.** All seven commands, `.venv` Python, never `pytest -q`. C-29's rule, unchanged.

**R3.7 — Instrument changes prove both directions.** Anything touching `tools/` gains selftest
coverage showing the check fires on the defect it exists for and passes on the healthy state.

**R3.8 — Sources are cited, never committed.** Rule 18 and rule 20 hold through the phase where
the repository is finally read by strangers: no paper text, no acquisition routes, bibliographic
metadata only.

**R3.9 — Claims at the width of the evidence, in the artifacts strangers read first.** The
README claims the governance layer and never the statistics (D-4, C-1's lesson); the release
notes state what was verified and by whom; anything unachievable is named as such.

## 5. Out of scope

Named, so scope creep is visible rather than absorbed.

- Everything in the charter's NEXT queue, by name: importance sampling and ML-assisted weights,
  `emit-dsa`, Beta-Binomial upper bounds, label-quality estimation, Wright's exact optimal
  allocation, per-stratum Se/Sp, eval-bridge (still gated on its own prior-art sweep).
- Any estimator, refusal, plan-schema or `verify` change — §3's closing note.
- Rewriting git history, for any finding O-28 produces. The answer is disclosure or a
  forward-looking fix, ruled by the director.
- A Phase 4. The charter caps the build at four phases numbered 0–3; a feature that wants one
  goes to NEXT.

**One boundary act inside this commit, stated rather than absorbed:** creating this file makes
Phase 3 the live phase in the machinery (`current_phase` reads the highest-numbered contract),
so the canonical phase sentence in `README.md` and `CLAUDE.md` moves to `Phase 3 of 4 in
progress` in the same commit. That is the C-47 check working as built, not a deviation.

## 6. Review stop

**Placement: after D3.3 and D3.4 — the demonstration and the README draft — and before D3.5
through D3.9, which is everything public or irreversible.**

The split falls there because the demonstration's numbers and the README's sentences are the
load-bearing core of this phase: every public act afterwards distributes them. Reviewed after
the release, they would be reviewed too late to change.

At the stop the builder will quote exact lines proving: the thresholds were hashed before the
corpus was touched; the coverage figures in the plot are the figures in the committed artifact;
every README claim names its source. Then hunt its own defects against the charter, the
decisions log and the corrections register — wrong statement, wrong reporting, and D-23's class:
a property proved in one artifact and assumed in another. Report ends with what remains open,
by name and severity. **The director closes each finding; the builder closes none.**

The tier re-ask (Q16) is ruled **before** the phase's post-stop half regardless of when the
stop is reached — if FULL is the ruling, the back half runs under it from the start.

## 7. Exit checklist

Expected results stated in advance. **Every "Expected" below is a prediction at drafting time —
none of these commands has been run for this phase** — which Template 5 says must be stated so
that "observed matches expected" is never read as two measurements agreeing. The director runs
every row by hand at the close.

| # | Command / act | Expected |
|---|---|---|
| G1 | `tools/check_tripwires.py --check` after D3.1 | Five tripwires reported. TW-4 no longer fired — or restated against the new pins, and the ruling that restated it named. Exit 0 if nothing is fired, exit 1 with the fired tripwire named otherwise |
| G2 | Re-run `witness.yml` after the re-pin | Every fixture regenerates byte-identically. The re-pin touched the runner, not the witness |
| G3 | Reproduce the coverage artifact from its recorded procedure | Figures identical to the committed artifact. The plot's curve is the artifact's numbers |
| G4 | Read the coverage plot by eye | Coverage near nominal at the pre-registered thresholds; the rare end behaving as charter §8's measured figures predict — Wilson dipping where the table says it dips. **A curve that looks better than §8's table is a finding, not a success** |
| G5 | Read the README by eye | The O-21 block present and grouped as one thing; `svy` credited as the estimator layer; the honest limits whole; the provenance sentence; no claim wider than its cited artifact |
| G6 | **README status row** — read the first status sentence at the release commit | It states the true phase and release state at that commit, exactly. C-47 is why this row exists: the most public sentence in the repository, read by a person at every close from now on, machine-checked in between |
| G7 | Negative control on the phase-sentence check | Perturb the phase sentence in either public file: gate red, naming the file. Delete it: gate red — absence is a failure. Restore: green |
| G8 | O-28 review reading exists, dated, with every finding ruled | The director's rulings recorded per finding, including the local-paths disclosure per Q19 |
| G9 | Rehearsal candidate verified by hand | Fresh download, published instructions followed exactly, checks pass with official tooling |
| G10 | **Rehearsal negative control** | **Must fail**, with the failure naming what it caught. If it passes, G9 proved nothing and the release is blocked |
| G11 | The real release, verified the same way as G9 and G10 | Same results, on the real artifacts, from outside the repository — fresh clone or fresh install, not the working tree |
| G12 | SBOM and provenance attestation verified with official tooling | Verification succeeds against the published artifacts; the negative control (wrong artifact or wrong repository) refuses |
| G13 | The ROOST PR | Submitted with the director-approved text, verbatim; the link recorded in the outcome |
| G14 | The full local gate, all seven commands | All green, counts printed, matching CI's run on the same head — stated apart, as two measurements |
| G15 | `tools/check_claims.py --selftest` then without | Both exit 0; the selftest covers D3.6's changes in both directions |
| G16 | T-1 sweep at close | C-1 and C-42–C-47 closed, each naming its discharging commit; open corrections at close are named in the outcome with their conditions |
| G17 | The phase sentence at close | `Phase 3 of 4 complete` in both public files, and the gate green on it |

## 8. Carried into Phase 3, by name

Every row is open at this drafting; each is reported at close as discharged, or unmet with a
named blocker. Owning records: the Phase 2 contract §10 and `docs/CORRECTIONS.md`.

| # | What | Owner here |
|---|---|---|
| O-19 ▸ **DISCHARGED 2026-08-31 by D3.1** | Re-pin the CI actions, premise re-read first. The re-read found the premise half false — **C-50** | **D3.1** |
| O-21 | The rare-event specificity fact reaches the README, grouped | **D3.4** |
| O-28 | Git-history review before publication | **D3.5** |
| O-14 | Keyless structural audit mode — carried, low | **Q23** rules its endgame |
| O-15 | Ledger schema version — unmet **by design** (D-25), added only if ever needed | **Q23** confirms the recording |
| C-1 | Closes when the README credits `svy` — the condition D3.4 meets | **D3.10**, under T-1 |
| C-42 … C-47 | Open corrections; close under T-1 naming their discharging commits | **D3.10** |
| Q-2 | Permanently `noted` — the suite is the builder's. Phase 3 adds the one instrument that is not: the director's outsider verification of published artifacts | — |

## 9. Tier — the re-ask, put to the director

**This section asks; it does not answer.** The standing discharge standard (D-1) says moving to
FULL requires naming a concrete finding attributable to a FULL-only practice. That standard was
written for phases with nothing to rehearse, and it is **backward-looking** — Phase 3's live
question is **forward-looking**: whether the first irreversible acts of this project's life
should run under the tier whose distinguishing practice is rehearsal of the irreversible.

What is true at either tier, because this contract binds it: the rehearsal, the negative
control, the hand-verification, the gated go (D3.7, D3.8, R3.1, R3.2). What FULL would add:
the method's whole lifecycle weight on the record itself — which Phase 3 makes public
regardless. **Q16 is the ruling. No recommendation is offered, per the ruling of 2026-08-30.**

**RULED 2026-08-31: STANDARD — D-42.** The director ruled the forward-looking question as well
as the backward-looking one: the rehearsal, the negative control, the hand-verification and the
gated go are what FULL would have been bought for, and this contract already binds them at
either tier. *The practice matters and the label does not.* Recorded as a numbered decision so
a later reader sees it was decided rather than defaulted.

---

## Numbered questions

Numbering continues from Phase 2's Q15 — question numbers are allocated across the project, and
`CLAUDE.md`'s ruled-questions figure is derived from the highest ruled number in any contract.
C-41 is why each question below has its own section. None is ruled yet.

### Q16 — The tier for Phase 3: FULL or STANDARD?

The first re-ask with something to decide. §9 states what is bound either way and what FULL
would add.

| | Option | Consequence |
|---|---|---|
| A | **Remain at STANDARD**, with D3.7/D3.8/R3.1/R3.2 binding rehearsal and gates contractually | The discipline of FULL's release practice without re-tiering; the discharge standard as written is honoured (no FULL-only finding exists to name — nothing irreversible has happened yet) |
| B | **Move to FULL for this phase** | The method's own release tier for the project's only release. Names the truth that this phase is what FULL exists for; costs the heavier record — in the one phase where the record is itself published |
| C | STANDARD to the review stop, FULL for the post-stop half | Matches where the irreversibility actually lives; a mid-phase tier boundary is a novelty this method has run once, in the other direction |

Awaiting the director's ruling. **No recommendation, and the reason is recorded in §2.3.**
One note the ruling may want: the backward-looking discharge standard cannot be met before the
first irreversible act by construction, so if it is applied literally, A follows automatically —
ruling on whether that standard even governs this boundary is part of the question.

**RULED: A — STANDARD. D-42.** And the framing was ruled on, not just the option: the
backward-looking discharge standard does not govern this boundary alone; on the forward-looking
question, *the practice matters and the label does not* — the rehearsal, the negative control,
the hand-verification and the gated go are what FULL would be bought for, and this contract
binds them at either tier.

### Q17 — What does "publish" mean: GitHub release alone, or PyPI as well?

Phase 0 ran the name-collision check and found `prevalence-kit` clear on PyPI, GitHub and npm —
insurance, or intent. A PyPI publish is the most irreversible act available to this project:
filenames are burned permanently, and yanking is visible forever.

| | Option | Consequence |
|---|---|---|
| A | **GitHub release only** — tag, signed artifacts, SBOM, attestation. PyPI to NEXT | Smaller surface; the release bar met in full; adoption requires a clone. The name stays unclaimed by us |
| **B** | **GitHub release + PyPI**, rehearsed on TestPyPI first | `pip install prevalence-kit` is how the audience §2 names would actually adopt it; TestPyPI gives D3.7 a real rehearsal target for the full path. Costs trusted-publisher setup and one more irreversible act |
| C | GitHub release now, PyPI as a fast follow inside this phase | Two release ceremonies for one version; the second performed when attention has moved on |

**Recommendation: B.** The charter's audience is an analyst or a small platform, and their route
is pip. TestPyPI makes the rehearsal genuinely execute the full publish path, which is what
Template 6 demands and a GitHub-only rehearsal cannot fully give. If the ts-sentry bar did not
include PyPI, A matches precedent and the collision check was insurance — the director knows
which it was.

**RULED: B.** GitHub + PyPI, TestPyPI rehearsed first. **D-43.**

### Q18 — The coverage demonstration's design

Charter §6.3 fixes the shape: pre-registered thresholds, hashed, truth by census, many samples,
the sensitivity curve. Open: which designs, how many thresholds, how many replications, and how
much of it runs through the sealed full chain.

| | Option | Consequence |
|---|---|---|
| **A** | **SRS, both binomial intervals** (`wilson`, `clopper_pearson`), roughly four pre-registered thresholds spanning the prevalence range including the rare end, order of 10,000 replications per point through the estimators directly — **plus one pre-registered full-chain run** (plan → sample → ingest → estimate → verify → report) as the governance demonstration | The flagship as ruled in R-7/D-11. Replication at the estimator level is what makes 10,000 draws feasible — the full chain pays Fernet sealing and real filesystem writes on every run, the profiled cost that dominates the local suite (2026-08-29), so mass replication through it would cost orders of magnitude more than the estimator-level loop for no additional statistical claim |
| B | A: plus stratified designs at the same scale | Demonstrates the design intervals under sampling — but their coverage is already measured **exhaustively** by enumeration (charter §8's 96-point table, re-derived in the suite). A sampled estimate of a quantity we hold exactly is weaker evidence than what ships |
| C | Fewer replications, more thresholds | A denser curve with wider error on every point of it |

**Recommendation: A**, with the §8 enumeration figures cross-referenced on the plot so the
stratified story is told by the stronger instrument. Conditions I would attach for the ruling:
seeds and thresholds in a hashed pre-registration file committed before the corpus is fetched;
the corpus pinned by digest and never committed; the demonstration artifact committed with its
generating procedure recorded to S-8's bar; and the plot stating the replication count and that
the curve's error bars come from it.

**RULED: A, with the four conditions above binding — and one more, the reviewer's, made
binding with them: the demonstration's reading must state that this corpus was already
characterised in this record (the charter carries its row count) before pre-registration, and
say why that does not weaken the pre-registration of thresholds and seeds.** **D-44.**

### Q19 — The committed local paths: disclose, or edit what can be edited?

O-28's recorded finding: local Windows paths with the director's username in five committed
documents; two are dated readings that are never edited; the username is already public via the
repository owner. SECURITY.md §3.8 warns operators against exactly this leak in run
directories.

| | Option | Consequence |
|---|---|---|
| **A** | **Disclose, edit nothing**: one note in the O-28 review reading — the paths are directory structure, not identity; the documents that carry them are dated evidence; §3.8's advice is about run artifacts operators publish, and the tension is named rather than hidden | Honest and cheap; a stranger who notices finds the project noticed first. The paths remain |
| B | Edit the three editable documents forward, disclose for the two dated readings | Working tree stops carrying the paths; history still does, so the leak is not closed — only made inconsistent between tree and history |
| C | Rewrite history | Ruled out by this contract's §5 and by the record's own structure — every citation of a commit hash breaks |

**Recommendation: A.** The half-measure of B buys nothing a historian cannot undo and costs the
consistency of the record. The disclosure note is the same move §8a's preamble narrowing made:
name the gap where a reader will meet it.

**RULED: A.** Disclose, edit nothing. **D-45.**

### Q20 — Ordering: when does the repository go public, relative to the tag?

| | Option | Consequence |
|---|---|---|
| **A** | O-28 closed → **repo public** → rehearsal candidate → tag + publish → ROOST PR | The release happens in public, so its run links and artifacts resolve for an outsider from the first moment; the rehearsal is visible, which is the honest history Template 6 wants kept |
| B | Everything rehearsed and tagged private, then public, then the PR | The public repo appears fully formed; every CI link in the release notes was run private; the rehearsal's honesty is retroactive |

**Recommendation: A.** The record's value is that it was not cleaned for company. Going public
before the release also gives G11's outsider verification a real outside.

**RULED: A.** O-28 closed, then public, then rehearse, then tag and publish, then the ROOST PR
last. **D-46.**

### Q21 — Restoring `check_figures`' phase claim: delete the superseded entry, or keep both?

C-47's rebuild added the canonical sentence check — both files, word and number, derived from
the contract's own close line, absence a failure. The old `readme phase` entry survives beside
it in the claims table: it compares the number to `current_phase` and reads only `in progress`,
the exact semantics C-47 condemned, and it has been vacuous since the README's sentence moved
to `complete`.

| | Option | Consequence |
|---|---|---|
| **A** | **Delete the superseded entry.** The canonical check is the one phase claim; the selftest proves it red on a wrong sentence and red on a deleted one | One claim, one scope, no vestige with condemned semantics waiting to match again the day the sentence next says `in progress` — at which point two checks would assert subtly different things about one sentence |
| B | Keep both | The legacy entry re-arms this commit (the sentence returns to `in progress`) and goes on comparing the number under semantics the correction it sits beside says are wrong |

**Recommendation: A.** Note the timing: option B is not hypothetical — the sentence flips back
to `in progress` with this very commit, re-arming the legacy pattern immediately. Two checks on
one sentence with different semantics is D-28's two-lists defect inside a single function.

**RULED: A.** The superseded entry is deleted; the canonical check is the one phase claim.
**D-47.**

### Q22 — The stale open-corrections row in `CLAUDE.md`, and its false attribution

Found while drafting this contract, reported rather than fixed. The row reads *"6 corrections
open — C-42 … C-46. 49 entries, 41 closed, 2 noted. Derived and machine-checked by
`check_counts`"*. The register holds **50** entries and **7** open — C-47 is open and absent
from the row. And `check_counts` reads only the counts table inside `docs/CORRECTIONS.md`; it
has never read this row. The count is stale **and** the attribution was never true: C-34's
class — the stated scope makes the reader stop looking, and here the false scope claim sat
beside the very correction (C-47) it failed to count.

| | Option | Consequence |
|---|---|---|
| **A** | **Correction entry + fix the row + extend the machinery**: a new C-number for the false row; the row corrected; `check_counts` (or a sibling) taught to read `CLAUDE.md`'s open-corrections row against the register, both directions, selftest proving it | The row's claim becomes true by machinery — the scope becomes the object the code walks. Rule 14's full move |
| B | Correction entry + fix the row + strike the attribution sentence | Honest and cheap; the row returns to being a live figure in prose with nothing watching it, which is C-9's mechanism and the reason the attribution was written |
| C | Fix silently | Ruled out by the register's own admission rule — the false row reached commits |

**Recommendation: A.** The row exists because hand-maintained figures in this file drifted
within hours, twice. Watching it is the point; B rebuilds the trap that produced this finding.

**RULED: A.** Correction entry — **C-48** — the row fixed, and `check_counts` taught to read it
against the register in both directions. **D-48.**

### Q23 — O-14 and O-15 at the end of the last phase

Rule 11 says every obligation is discharged or reported unmet with a blocker — and this is the
last phase, so "carried" stops being available.

| | Option | Consequence |
|---|---|---|
| **A** | **O-14 to the NEXT queue by name** (charter §4's list); **O-15 recorded in the outcome as unmet by design**, with D-25's condition restated as the trigger that would create it | Both stay visible: one as deferred work with a name, one as a decision not to build speculatively. Nothing silently expires |
| B | Build O-14 in Phase 3 | A keyless audit mode is real scope in the phase already carrying the release; charter §4 sends exactly this growth to NEXT |
| C | Close both as won't-do | O-15's condition is real (D-25) and O-14 was wanted (V-10); won't-do erases the reasons |

**Recommendation: A.**

**RULED: A.** **D-49.**

### Q24 — `check_open_items` can no longer see the discharges the closed phase recorded

Found by the selftest, on this contract's first gate run. The check reads obligation states
from the decisions log, the standards register and the contracts, **minus the contract of every
closed phase** — an exclusion ruled so that Phase 1 §10's dated open-at-the-time rows cannot
false-positive. But the Phase 2 contract §10 is also where O-4, O-8, O-13, O-20, O-22, O-23,
O-25, O-26, O-27 and O-29 are marked **discharged**, and the moment this file existed, all of
that left the walked set. The selftest's planted violation — O-4 listed as open in `CLAUDE.md`
— went undetected because nothing in scope still says O-4 is discharged. The drift this check
was built for (a hand-maintained row going stale against the record) is exactly what it can no
longer catch for any Phase-2-discharged obligation.

| | Option | Consequence |
|---|---|---|
| **A** | **Read closed contracts one-directionally**: their `discharged` rows stay in scope, their open-state rows stay excluded | A discharge is permanent, so a dated document's discharge rows never go stale — the original exclusion's reason (dated open-rows false-positiving) is preserved, and the coverage returns. The selftest passes again for the reason it should |
| B | Restate every discharge in a live file the check reads | A second copy of the record, maintained by hand — the count treadmill, made of obligations |
| C | Narrow the selftest to plant an obligation whose discharge is recorded in a live file | The selftest goes green by testing less; the coverage loss stands |

**Recommendation: A.** The asymmetry is the fact being modelled: open-ness expires, discharge
does not.

**RULED: A.** One-directional reading of closed contracts — discharge is permanent, open-ness
expires. **D-50.**

### Q25 — Four C-47 tests anchored on the live phase, and two of their plants went vacuous

Found by running the gate on this tree. `test_the_phase_state_is_read_from_the_contract`
asserts `(2, "complete")` against the live tree — a live figure hard-coded in a test, the class
this register keeps correcting — and its negative-control sibling assumes the newest contract
is Phase 2's. Worse in kind: the two sentence tests plant their violation by replacing the
literal string `Phase 2 of 4 complete`, and neither asserts the anchor matched — so on this
tree they replace nothing, plant nothing, and fail on an empty problem list. Had their
assertions been written the other way round, they would have gone **green while proving
nothing**, which is C-27's control shape inside the fix C-47 shipped. The heredoc lesson
already says it: assert the anchor before writing through it.

| | Option | Consequence |
|---|---|---|
| **A** | **Rewrite the four to derive their anchor from the artifact**: read the current sentence via the check's own `phase_state`, perturb *that*, and assert the plant took before asserting the checker fired; the state test asserts the property (close line present → `complete`, removed → `in progress`) on the newest contract, whichever it is | Phase-agnostic: survives every future boundary, including this phase's own close at G17 |
| B | Update the constants to Phase 3's state | Green until the next boundary event, then this same failure again — the treadmill, in the suite |

**Recommendation: A.** Also for the director's judgment: whether the vacuous-anchor pair and
the hard-coded live figure warrant correction entries under the register's rule — both reached
commits; both were true or green at their commit and could not survive the next boundary. The
builder proposes entries and does not close its own findings.

**RULED: A.** Artifact-derived anchors, plants asserted before the checker is consulted, the
state test a property. **One correction entry for the pair — C-49 — because they have one
cause**: tests anchored on the state of the moment rather than on the artifact, and it notes
that this happened inside the fix for C-47, which is the part worth remembering. **D-51.**

---

## 10. Deviations and outcome

Written at the close, not before. Phase 2's §11 opens with the reason.
