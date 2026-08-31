# Contributing to prevalence-kit

Thank you for looking. Please read this before opening a pull request, because
this project is governed in a way that is unusual and the difference matters.

## The one thing to know first

**This repository is a record as well as a codebase.** Every material choice has
a numbered entry in `docs/DECISIONS.md` saying what was decided, what was
rejected, and why. Every claim that turned out to be wrong has an entry in
`docs/CORRECTIONS.md` naming who got it wrong. Several documents are **dated
readings** and are never edited — corrections to them go in the corrections
register instead, with the date and the direction the number moved.

That means a change here is usually two things: the change, and the record of
why. A pull request that improves the code and leaves the record behind will be
asked for the second half.

## What is most useful

**Finding a claim that is wrong.** This project publishes measured figures, and
several of the most valuable defects in its history were found by a person
reading an output file and checking the arithmetic — not by a failing test. If a
number here does not reproduce, that is the most welcome issue you can open, and
there is an issue template for it.

**Reproducing something.** The estimators are validated against R `survey`,
`epiR`, `stratallo`, base R and Python `svy`; the coverage demonstration runs on
a public corpus with a census truth. If you re-run any of it and get a different
answer, please say so.

**Using it and telling us what was confusing.** The tool is meant to be checkable
by an outsider. Where it is not, that is a defect in the tool.

## Before you open a pull request

Run the whole gate, not the part that looks affected:

```
ruff check .
ruff format --check .
mypy --strict src
mypy
tools/check_claims.py --selftest
tools/check_claims.py
pytest
```

All seven must pass. A few notes that will save you time:

- **Never `pytest -q`.** `pyproject.toml` already sets `-q`, so passing it again
  suppresses the count, and the count is evidence.
- **`mypy` on its own is not the same command as `mypy --strict src`.** The bare
  form reads the config and covers the tests too. Both are in the gate because
  each passes things the other catches.
- **`tools/check_claims.py` reconciles the record against the code.** It runs
  twelve checks — that every cited decision exists, that every named file
  exists, that every refusal code in a contract exists in the code and has a
  test proving it fires, that the counts in the documents match the entries, and
  more. `--selftest` plants a violation for each check and requires it to be
  caught; run it first.
- The suite takes about a minute locally. If it takes much longer, profile
  before assuming — the last time that happened the cause was a test fixture,
  not the code.

## The rules that shaped this codebase

You do not have to agree with these, but changes that contradict them will be
questioned:

1. **Every gate gets a negative control and a positive control**, and the
   negative control must reproduce the state the real defect produced — not
   merely a state that turns the check red. A check that has only ever passed is
   a decoration.
2. **A claim is made at exactly the width of its evidence.** "Validated against
   `survey`" means the specific quantity that library computes, not everything
   nearby. Where a witness implements a different quantity, it witnesses nothing.
3. **Numbers are re-derived from the artifact, never carried from a sentence.**
   Several corrections in the register are figures nobody re-derived.
4. **Honest limits are a deliverable.** They are written into the tool's own
   output, not buried in documentation, and they are carried forward unchanged.
   A limit is narrowed only when it genuinely narrowed, and never deleted for
   being inconvenient.
5. **No AI output may reach labels or estimates.** This is enforced by a
   structural test, and it is the project's central promise.

## Style

Plain English. Short sentences. Common words. If a sentence needs reading twice,
rewrite it. This applies to the README, the code comments, the error messages,
the report output and the documentation equally — a tool that exists to make a
number checkable by an outsider has failed if the outsider cannot read it.

Code is `ruff`-formatted at a 100-column line length and type-checked with
`mypy --strict`. Messages an operator sees are plain ASCII, asserted by a test,
because they have to render on a default Windows console.

## Reporting a security issue

Please do not open a public issue. `SECURITY.md` has the process, and it also
states plainly what this tool does **not** protect against — that section is
worth reading before you report, because some of what looks like a
vulnerability is a documented limit.

## Licence

By contributing you agree that your contribution is licensed under the MIT
Licence, the same terms as the project. See `LICENSE`.
