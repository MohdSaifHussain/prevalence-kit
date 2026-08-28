# Security

**Status: RATIFIED — 28 August 2026.**
**Written before any Phase 1 code**, as Hard Rule 5.1 requires. Cipher ruled R-5 / D-9.

Plain English, on purpose. A threat model nobody reads protects nobody.

---

## What prevalence-kit is, in security terms

A local command-line tool. It reads files. It writes files. **It makes no network calls at
runtime.** It handles two things worth protecting: content that is often harmful, and a number that
people may act on.

Those are two different security problems and this document keeps them separate.

---

## 1. What it protects

### 1.1 The content

Prevalence measurement means putting harmful material — abuse, threats, sexual content, graphic
violence — into a working set on someone's machine, and then labeling it. That material is the
input. It cannot be avoided. It can be contained.

**Protection:** content is **sealed on ingest**. Encrypted at rest. What you see by default is a
safe preview — length, digest, harm flags — not the content. Unsealing is explicit, deliberate, and
logged in the record. Nothing unseals as a side effect of an ordinary command.

**Who this protects.** The analyst who does not want abuse material rendered in their terminal by
accident. The reviewer who opens a file six months later. The colleague who runs `verify` on a
shared record and should see hashes, not harm.

### 1.2 The labels

Human labels are the evidence. Change them and the number changes, with no other trace.

**Protection:** labels enter the hash chain at ingest. A changed label breaks the chain, and
`verify` fails with a named reason.

### 1.3 The integrity of the number

This is the one that matters most, and it is the least obvious.

A prevalence number can be made to say almost anything by choosing the plan after seeing the
results. Sample until it looks good. Redefine the estimand. Drop the stratum that came out badly.
None of that requires touching a file — it only requires reordering the work and telling the story
in the right order afterwards.

**Protection, and it is the core of the design:**

- **The plan is hashed before any data is touched.** This is pre-registration. The estimand, the
  population, the design and the label source are fixed and stamped before the first row is read.
- **Every step joins a hash chain:** plan → sample → ingest → estimate → report.
- **The sample is deterministic under a recorded seed.** Anyone can redraw it.
- **`verify` re-runs the whole chain** and reproduces the estimate from the sealed record alone.
- **`verify` can say no.** That is what makes its yes worth anything.

**Who this protects.** The auditor. The regulator. The reader of a public transparency report. And
the analyst who wants to be able to prove, later, that they did not move the goalposts.

---

## 2. Who it protects against

We name the adversary, because a threat model without one is a wish list.

### 2.1 Accidental exposure — the most likely threat by far

A person, usually the operator, seeing harmful content they did not ask to see. A terminal
scrollback. A screen share. A log file. A crash dump.

**Mitigation:** sealed by default; preview-only rendering; explicit logged unseal; no content in
logs, errors, or report output — asserted by test.

**This is the threat most likely to actually happen.** It is ranked first deliberately.

### 2.2 The dishonest reporter

Someone — possibly the tool's own operator, possibly their employer — who wants a favourable number
and will adjust the method until they get one.

**Mitigation:** pre-registration hash. The plan is stamped before the data is touched. A plan
changed after results are seen produces a hash mismatch, and `verify` refuses with a named reason.

**Honest limit, stated plainly:** this does not stop anyone from running the tool many times and
publishing only the run they liked. Nothing in a local tool can stop that. What it does is make each
published run *internally* honest and independently checkable, and make the discarded runs
conspicuous by absence if anyone asks.

### 2.3 The tamperer

Someone who edits a record after the fact — changing a label, a sample, a stored estimate — to make
a published number match a story.

**Mitigation:** hash-chained ledger over every step. Any edit breaks the chain. `verify` fails with
a distinct reason code identifying which link broke.

### 2.4 The casual snoop

Someone with read access to the working directory — a backup service, a synced folder, a colleague
on a shared machine — who would otherwise read harmful content straight off disk.

**Mitigation:** encryption at rest. They get ciphertext.

### 2.5 The exfiltrator

Anything that would send content, labels, or estimates off the machine.

**Mitigation:** zero network calls at runtime, zero telemetry, **proven by a test that fails if any
network capability appears in the dependency tree**. This is why `svy` — an otherwise excellent
library — is not a runtime dependency: it requires `httpx`.

### 2.6 The supply chain

A compromised dependency or a compromised release artifact.

**Mitigation:** hash-locked dependencies, SHA-pinned GitHub Actions, SBOM, signed release artifacts
with provenance attestation. The ts-sentry bar.

---

## 3. What it does NOT protect against

Stated honestly. This section is a deliverable, not a disclaimer, and it is carried forward
unchanged into every later phase.

### 3.1 It does not protect the key

Encryption at rest is only as good as the key handling. **prevalence-kit does not solve key
management.** Here is exactly what it does, so you can decide whether that is good enough for your
situation. It is your call, not the tool's.

**Where the key lives.** `plan` generates a Fernet key on the first step of a run and writes it to
`<run>/seal.key`, in the same directory as the sealed content it protects. Nothing else creates,
moves, rotates or deletes it. Every read goes through one function, `Workspace.key`, which refuses
`KEY_MISSING` when the file is absent rather than raising a traceback.

**What that means, plainly:**

- **An attacker with read access to the run directory has both the ciphertext and the key.** Sealing
  protects against a backup service, a synced folder, a colleague browsing a share, or content
  rendering by accident. It does **not** protect against someone who can read the whole directory.
- **`seal.key` must never be committed.** `.gitignore` excludes `*.key`. If you move a run
  directory into version control, check that first.
- **Lose the key and the content is gone.** The ledger, the labels, the estimate and `verify` all
  still work -- they never need the plaintext -- but nothing can unseal the content again. That is
  the design, not a bug: `verify` reproduces the number without ever decrypting content.
- **There is no rotation.** `MultiFernet` supports it and this version does not use it. A run is a
  single measurement with a single key.

**If that is not good enough for you,** keep the run directory on an encrypted volume, or move
`seal.key` to a separate location after the run and restore it only when you need to unseal. The
tool will refuse by name when the key is absent, which makes that workflow safe to operate.

### 3.2 It does not protect against a compromised machine

Root access, a keylogger, a malicious process reading memory. Content is plaintext in memory while
being processed. There is no defence here and we will not pretend otherwise.

### 3.3 It does not protect against a bad sampling frame

If the population you sampled from is not the population you claim, the number is wrong and every
hash in the chain will verify perfectly. **The chain proves the process was followed. It cannot
prove the process was right.**

### 3.4 It does not protect against biased or wrong labels

Garbage in, sealed and hash-chained garbage out. Rogan–Gladen can correct for *known* sensitivity
and specificity, if you supply them. It cannot tell you whether your raters were biased, tired,
under-trained, or wrong in a way that correlates with the thing you are measuring.

**v1.0 does not estimate rater quality at all.** It uses the numbers you give it.

### 3.5 It does not protect against selective publication

See §2.2. Run it a hundred times, publish once. No local tool can prevent this.

### 3.6 The intervals do not cover rater error

The confidence interval is a **sampling** interval. It describes uncertainty from having sampled
rather than counted. It says nothing about label error.

This is not a shortcut. It is the same limit YouTube publishes for VVR:

> *"The confidence intervals do not take into account rater quality, which may impact our
> measurements."*

And the same limit Meta publishes: *"the people who apply labels to our samples sometimes make
mistakes."*

We adopt their caveat because it is honest and because it is true of us too.

### 3.7 Sealing is chunked, and chunk boundaries are visible to an attacker

The sealing cipher is **Fernet** (`cryptography` 50.0.1): AES-128-CBC with PKCS7 padding,
HMAC-SHA256 authentication, IVs from `os.urandom()`. The official documentation states its
limitation plainly: *"Fernet is ideal for encrypting data that easily fits in memory."*

**We answer that by chunking, plus an ordered chunk-digest manifest bound into the ledger**
(decision D-14). The honest position, narrowed to what is actually true:

**Detected:**

- Tampering with any chunk — Fernet authentication fails → `SEAL_TAMPERED`
- **Truncation** — chunks dropped from the end → `SEAL_TRUNCATED`
- **Reordering** — chunks swapped → `SEAL_REORDERED`
- **Substitution** — a chunk replaced with a validly-sealed chunk from elsewhere →
  `SEAL_MANIFEST_MISMATCH`

Fernet authenticates each chunk individually; the **manifest and count**, bound into the ledger
entry, authenticate the sequence. Order and completeness tampering is **detected at `verify`**,
with a distinct reason code per failure mode.

**Still not protected:**

- **Chunk count and chunk sizes leak an approximate plaintext length.** Sealing hides content,
  not size. An observer with the sealed store can tell a long item from a short one. This is a
  real limit and it is not fixable by the manifest.

**Why Fernet and not a streaming AEAD.** `cryptography` 50.0.0 (2026-07-31) added Cobblestone-128,
a streaming authenticated cipher that would remove the size limit natively and bind ciphertext to
a context string. It was **considered and rejected on soak time**: four weeks old at the decision
date, and a tool about auditability anchors on reviewed, aged primitives. If context binding is
later needed, it is achievable via AES-GCM AAD. Full reasoning: `docs/DECISIONS.md` D-9.

**Having declined the specification that solves whole-message integrity, we carry that obligation
ourselves.** The manifest above is the cost of that choice, paid rather than deferred. D-14.

### 3.8 The ledger records where the plan file was, and that travels

`plan` writes the working plan file's path into the plan ledger entry, so `verify` can check the
working file without being told where it is. That closes a real hole: forgetting `--plan` used to
give a clean `verify` on a tampered plan (V-12).

**The consequence, stated rather than absorbed.** A run directory that is shared, published, or
attached to an audit carries that path with it. On this platform it is absolute, so it can disclose
a username and directory structure. Paths already appear in refusal messages; this is the first time
one is written into the ledger, which is the artifact most likely to be handed to someone else.

It is a small disclosure and it is not nothing. If a run will leave your machine, look at
`ledger.jsonl` entry 0 before it does. The plan **hash** is unaffected -- the path is in the entry
body, not in the hashed plan record -- so removing or rewriting the field would break the chain, not
the plan's identity. There is no supported way to redact it in this version.

**A moved run reports honestly rather than silently.** Copy a run to another machine and the
recorded path will not exist there; `verify` says `NOT CHECKED`, names the path, and says it may
belong to another machine. That is the honest outcome, not a failure.

### 3.9 It is not a moderation or enforcement system

It measures. It never judges content, never actions an account, never removes anything. If you need
a detector, ROOST ships several. This is not one.

### 3.10 It has not been through an external security audit

Built by directing an AI under a governed process, with the gates and tests described here. That is
not the same as a penetration test or a professional code audit, and it is not claimed to be.

### 3.11 It is not validated in production

Validation is on synthetic data and one public dataset. **No claim of production deployment.**

---

## 4. The no-AI cage

A security property, not a preference.

**Labels come from humans. Estimates come from deterministic math.**

If AI is ever permitted to *propose* anything — sampling weights, say — it enters as a plain input
file, and **a structural test proves AI output can never reach labels or estimates.** Same cage as
finding-bridge.

Why this is in the threat model: an LLM in the evidence path is an unauditable, non-reproducible,
silently-drifting component sitting between the content and the number. Pinterest's published system
puts one there. That is the specific thing this tool refuses to do.

---

## 5. Reporting a vulnerability

*To be completed at Phase 3, before release. Placeholder — do not publish this file with this
section unfinished.*

Until then, this is a pre-release draft in a repository with no published artifacts.

---

## 6. Open security decisions

| # | Question | Status |
|---|---|---|
| R-5 | Cipher for sealing | **RULED 2026-08-28: Fernet, chunked.** Cobblestone-128 considered and rejected on soak time. See `docs/DECISIONS.md` D-9. |
| O-1 | Pin the exact OpenSSF/SLSA documents and the SHA-256 standard | Phase 1 |
| — | Key management: where the key lives, and what §3.1 will say concretely | Phase 1 |
