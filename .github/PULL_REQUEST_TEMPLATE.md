<!--
Thank you for the contribution. CONTRIBUTING.md explains why this repository
asks for the record as well as the change; the short version is that a claim
here is expected to be exactly as wide as its evidence.
-->

## What this changes

<!-- One or two sentences. What is different after this lands? -->

## Why

<!--
If this fixes something that was wrong, say what was wrong and what proved it.
"Found by reading the report by eye" is a perfectly good answer and has been
the origin of several of this project's most useful fixes.
-->

## Evidence

<!--
How do you know it works? Prefer something someone else can re-run over a
description. If a number moved, say what it was and what it is now, and which
direction that is.
-->

## The gate

All seven, on the tree as submitted:

- [ ] `ruff check .`
- [ ] `ruff format --check .`
- [ ] `mypy --strict src`
- [ ] `mypy`
- [ ] `tools/check_claims.py --selftest`
- [ ] `tools/check_claims.py`
- [ ] `pytest` — count printed: <!-- N passed -->

## Checks that apply to this change

- [ ] If it adds or changes a **refusal**, it has a negative control that
      reproduces the state the real defect produces, and a positive control.
- [ ] If it changes a **claim** — in the README, a docstring, an operator
      message, or the record — the claim is no wider than the evidence.
- [ ] If it moves a **number** that is stated anywhere in prose, every place
      that states it has been found by searching, not by memory.
- [ ] If it touches a **dated reading** (`docs/contracts/PHASE-*-HAND-RUN.md`,
      `PHASE-*-REVIEW-STOP.md`, `PHASE-3-HISTORY-REVIEW.md`,
      `docs/RULINGS-QUEUE.md`) — it should not. Those are never edited;
      corrections go in `docs/CORRECTIONS.md`.
- [ ] If it adds a **material decision**, `docs/DECISIONS.md` has an entry with
      the alternatives not taken.

## Anything you are unsure about

<!--
Say so here rather than leaving it out. An uncertainty stated is a review
finding; an uncertainty omitted is a defect waiting for someone else.
-->
