#!/usr/bin/env python
"""Reconcile what the record claims against what the repository contains.

Doctrine rule 14: a lesson that lives only in prose will not hold, so build the
check. Rule 11: an obligation is tracked by name until discharged, and reported
against the artifact rather than against the last report.

Nine checks, each answering a question that has actually gone wrong here.
(This sentence said "five" while six were listed, which is the count treadmill
rule 14 names. Re-derive it from `CHECKS` if you touch this file.)

  citations   Does every D-nn / C-nn / O-nn / F-n / V-n reference resolve?
              (C-8: the code cited a D-17 that did not exist, and a
              tests/test_plan.py that did not exist.)

  paths       Does every repository path named in the source exist?
              (Same defect, other half.)

  codes       Do the contract's reason codes and `Reason` agree, both ways?
              (A code in one and not the other means the contract is
              describing a tool that is not this one.)

  findings    Which accepted findings have no closing evidence?
              (C-12: a report accurate about what it covered and misleading
              about what it omitted. This is the half that needs a machine,
              because running the tool cannot detect it.)

  controls    Which refusals can nobody prove fire?
              (Rule 5 wants a distinct reason code per failure mode, because
              refusals that cannot be counted by cause are meaningless. Three
              raise sites across PLAN_MISSING and ALLOCATION_ROUNDING_UNDECLARED
              could have their code swapped for an unrelated one with all 418
              tests still passing. `codes` cannot see this: it checks that a
              code is documented, not that anything proves it fires.)

  register    Which findings does the record discuss but the register omit?
              (The other direction, and the one that was missing. V-12 through
              V-15 were each named across three to nine documents while the
              register held 22 rows and none of them these four -- and the
              checker said "all accounted for". A register checker that
              validates the rows present cannot detect the rows missing.)

  figures     Is any figure restated in prose without being derivable?
              (C-7: two gate numbers quoted that no command produces.)

  fixtures    Can the shipped example actually perform the exit checks that
              name it?
              (C-15: F-4 was closed in tests/conftest.py and regressed into
              examples/synthetic/, which was created afterwards. Every item
              was one chunk, so E9c -- swap two chunks WITHIN one item --
              could not be performed at all. A finding closed in one artifact
              and open in another. See D-23 for why the findings check cannot
              see this class on its own.)

  gate        Does CI run every check the gate documents, and only those?
              (V-16: CLAUDE.md documented seven and gate.yml ran six. The
              missing one was `mypy` in its config form, so the eleven test
              files were never type-checked on the remote. The gate on the
              remote was weaker than the gate on the desk and nothing said so.)

Exit 0 when everything reconciles, 1 otherwise. `--selftest` proves each check
can fail, because a check that has only ever passed is a decoration.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]

CITATION = re.compile(r"\b([DCO])-(\d{1,3})\b")
FINDING_REF = re.compile(r"\b([FV])-(\d{1,2})\b")
FINDING_ID = re.compile(r"\b([FVQ]-\d{1,2})\b")
"""A finding identifier as the record writes it, anywhere in any document.

Deliberately wider than `FINDING_REF`: it includes `Q-n`, and it captures the
whole id rather than its parts, because `check_register` asks a set question --
*is this one in the register?* -- not a parsing question. The contracts write
their numbered questions as `Q1`, without the hyphen, so they do not collide
with the register's `Q-1` and `Q-2`.
"""
PATH_LIKE = re.compile(
    r"(?<![\w./-])((?:src|tests|docs|tools|r|svy|examples|demo)/[\w./-]+"
    r"\.(?:py|md|toml|txt|pdf|json|R|sh|yml|svg))"
)
"""A repository path. The lookbehind matters: without it `awesome-safety-tools/README.md`
matched on its `tools/README.md` suffix and was reported as a missing file.

**Widened a second time at the Phase 3 review stop, ruled 2026-08-31** -- the same two axes as
D2.14(a), because the same two axes went narrow again: the README's front page links four files
under `demo/`, one of them an `.svg`, and a vanished link passed this check (the reviewer's
negative control proved it). A check that names its question generalises; this one's question is
"does every named repository file exist", and its scope is this pattern, not a sentence.

**D2.14(a), 2026-08-30.** Both directory prefixes and extensions were too narrow, and the
register said so about itself: *"`check_paths` only looks at paths under `src/`, `tests/`,
`docs/` or `tools/` that end in `.py`, `.md`, `.toml` or `.txt`. Neither PDF matches -- wrong
folder, wrong extension."* The R witness, the `svy` fixtures and the shipped example were
invisible for the same reason.

**Widened by the two axes that were wrong**, rather than by naming the files that were missed
-- a check that names its question generalises; one that names a row does not (D-23, V-15).
`.pdf` is here because the register cites two of them and neither was covered; one is tracked
and one is deliberately absent, which is what `KNOWN_ABSENT` is for."""


@dataclass(frozen=True, slots=True)
class Problem:
    check: str
    where: str
    detail: str

    def line(self) -> str:
        return f"  [{self.check}] {self.where}: {self.detail}"


# --------------------------------------------------------------------- inputs


def repo_files(root: Path, *globs: str) -> Iterator[Path]:
    for pattern in globs:
        for path in sorted(root.glob(pattern)):
            if ".venv" not in path.parts and "__pycache__" not in path.parts:
                yield path


OBLIGATION_SOURCES = ("docs/DECISIONS.md", "docs/STANDARDS.md", "docs/contracts/*-CONTRACT.md")
"""Where obligations are defined. **This tuple is the scope, not a sentence about it.**

`defined_ids` walks exactly these and `scope_of` renders them for humans, so the
documented scope is derived from the behaviour instead of written beside it.

That is C-34's fix. The old docstring said obligations live in two files. They
live in three, seven were invisible, and **the sentence naming the scope was
worse than no sentence** -- it answered the question before anyone asked it, and
answered it wrongly.
"""


def scope_of(paths: tuple[str, ...]) -> str:
    """The scope, rendered from the list actually walked. Never hand-written."""
    return ", ".join(paths)


def defined_ids(root: Path) -> dict[str, set[str]]:
    """What the record actually defines, read from the record.

    Obligations are read from `OBLIGATION_SOURCES`, which is the single place
    that list exists. **Do not restate it in prose here.** The previous version
    of this docstring named two files when there were three, and because it read
    as a considered statement nobody re-checked it: O-8, O-16, O-17, O-18, O-20,
    O-21 and O-24 were all invisible until a test happened to cite one.

    A checker with no stated scope invites the question. A checker with a wrong
    stated scope answers it falsely, and the reader comes away **more confident
    and less correct**. So the scope is derived -- `scope_of(OBLIGATION_SOURCES)`
    -- and `test_the_documented_scope_is_the_scope_walked` pins that it stays so.

    Contracts are matched by glob, not by name, so a Phase 3 contract is covered
    the day it is written. V-15.
    """
    decisions = (root / "docs" / "DECISIONS.md").read_text(encoding="utf-8")
    corrections = (root / "docs" / "CORRECTIONS.md").read_text(encoding="utf-8")

    obligations = ""
    for pattern in OBLIGATION_SOURCES:
        for path in sorted(root.glob(pattern)):
            obligations += path.read_text(encoding="utf-8") + "\n"

    return {
        "D": set(re.findall(r"^## (D-\d+)", decisions, re.M)),
        "C": set(re.findall(r"^## (C-\d+)", corrections, re.M)),
        # A contract row may be bolded: `| **O-20** *(new)* | ...`
        "O": set(re.findall(r"^\| \*{0,2}(O-\d+)\*{0,2}", obligations, re.M)),
    }


def register_rows(root: Path) -> list[tuple[str, str, str, str]]:
    """(id, severity, status, evidence) from docs/FINDINGS.md."""
    text = (root / "docs" / "FINDINGS.md").read_text(encoding="utf-8")
    rows: list[tuple[str, str, str, str]] = []
    for line in text.splitlines():
        m = re.match(r"^\| ([FVQ]-\d+) \| ([^|]+)\| ([^|]+)\| ([^|]+)\|", line)
        if m:
            rows.append(tuple(g.strip() for g in m.groups()))  # type: ignore[arg-type]
    return rows


def test_names(root: Path) -> set[str]:
    names: set[str] = set()
    for path in repo_files(root, "tests/*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        names |= {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    return names


# --------------------------------------------------------------------- checks


def check_citations(root: Path) -> list[Problem]:
    defined = defined_ids(root)
    problems: list[Problem] = []
    # `tools/` is excluded: this file contains deliberately broken citations as
    # selftest fixtures, and a checker that flags its own test data is a checker
    # someone switches off. Stated rather than left as a silent gap.
    for path in repo_files(root, "src/**/*.py", "tests/*.py"):
        text = path.read_text(encoding="utf-8")
        for kind, number in CITATION.findall(text):
            ident = f"{kind}-{int(number)}"
            if ident not in defined[kind]:
                problems.append(
                    Problem("citations", f"{path.relative_to(root)}", f"{ident} is not defined")
                )
    return problems


SCANNED = ("**/*.py", "**/*.md", "**/*.txt")
"""What the path check reads. Patterns, not a list of files.

A named list stops covering a document the day it is added -- no failure, no
warning, just less coverage than yesterday. CLAUDE.md was added, named a path
that did not exist, and this check passed. D-23's principle applied to the
checker's own inputs: a check that names its question generalises; a check that
names a row does not. V-15.
"""


KNOWN_ABSENT = {
    # Quoted from another package as D-18's evidence: svy's own source, read to
    # establish that its Wilson is a different estimator. Widening PATH_LIKE for
    # D2.14(a) made this spelling visible where `src/svy/...` already was.
    "svy/estimation/base.py",
    # Quoted as evidence from another package, not a path in this repository.
    # docs/DECISIONS.md D-18 quotes svy 0.25.0's source by file and line.
    "src/svy/estimation/base.py",
    # Quoted as the defect itself. docs/CORRECTIONS.md C-8 records that plan.py
    # once cited this file, which never existed. Naming it is the point.
    "tests/test_plan.py",
    # Also quoted as the defect. V-15 records that CLAUDE.md named this path
    # when the file is under docs/contracts/.
    "docs/PHASE-1-REVIEW-STOP.md",
    # Quoted as the regex bug. V-15 records that awesome-safety-tools/README.md
    # matched on this suffix before the lookbehind was added.
    "tools/README.md",
}
"""Paths deliberately named that do not exist here, each with a stated reason.

An explicit set beats widening the regex or skipping whole files: every
exemption is visible and has to be justified when it is added.
"""


def check_paths(root: Path) -> list[Problem]:
    problems: list[Problem] = []
    for path in repo_files(root, *SCANNED):
        # This file carries deliberately broken paths as selftest fixtures.
        if path.name == "check_claims.py":
            continue
        for named in PATH_LIKE.findall(path.read_text(encoding="utf-8")):
            if named in KNOWN_ABSENT or (root / named).exists():
                continue
            problems.append(
                Problem("paths", f"{path.relative_to(root)}", f"{named} does not exist")
            )
    return problems


def pending_codes(root: Path) -> set[str]:
    """Codes a contract promises before the deliverable that builds them lands.

    Those are obligations, not defects, and the difference has to be visible:
    a row marked PENDING is expected to be absent, and anything else is not.
    Rule 11 -- tracked by name until discharged, never quietly dropped.

    **Read by two checks, from one definition.** `check_codes` allows a PENDING
    code to be missing from `Reason`; `check_controls` allows a PENDING code to
    have no test. Two lists that must agree, with nothing making them agree, is
    D-28's defect -- so there is one list.

    **The exemption expires by machinery, not by memory.** `check_codes` fires on
    a code still marked PENDING after it exists, and has done so twice. So a
    deliverable that lands without the marker being removed fails the gate.
    """
    contract = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((root / "docs" / "contracts").glob("*-CONTRACT.md"))
    )
    return {
        name
        for line in contract.splitlines()
        if "PENDING" in line and "PENDING-CONTROL" not in line
        for name in re.findall(r"`([A-Z][A-Z_]{4,})`", line)
    }


def control_deferred_codes(root: Path) -> set[str]:
    """Codes that exist and whose specified trigger the schema cannot yet express.

    **A third state, and it needed its own name.** `PENDING` means *the
    contract promises a code that `Reason` does not yet have*, and `check_codes`
    fires when such a code turns up in `Reason` -- which is how the marker
    expires by machinery rather than by memory. It has caught that twice.

    `ALLOCATION_ROUNDING_UNDECLARED` is not that. **The code exists**, raised on
    a defensive branch no valid `Rounding` reaches, and its specification --
    *`design: stratified` with no `allocation_rounding` field* -- is right and
    not yet buildable, because the plan schema gains that field in D2.8 (O-20).
    Reusing `PENDING` for it would have required relaxing the rule that has
    fired twice, to accommodate one row. Q9 / D-36.

    **Its expiry is machinery, not a date.** The branch becomes reachable only
    when `Rounding` gains a second member, and
    `test_the_rounding_enum_still_has_exactly_one_member` fails the day it does.
    """
    contract = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((root / "docs" / "contracts").glob("*-CONTRACT.md"))
    )
    return {
        name
        for line in contract.splitlines()
        if "PENDING-CONTROL" in line
        for name in re.findall(r"`([A-Z][A-Z_]{4,})`", line)
    }


def superseded_codes(root: Path) -> set[str]:
    """Codes a closed phase's contract names that a later phase replaced.

    **A contract is a dated document and is not edited**, so the Phase 1 contract
    goes on naming `PLAN_MISSING` forever -- correctly, because that is what
    Phase 1 shipped. Q8 / D-35 split it into `PLAN_FILE_MISSING` and
    `PLAN_SEAL_MISSING`, and the supersession is recorded in the **Phase 2**
    contract, where the change was made.

    Without this, the choice would be between editing a dated reading and
    carrying a permanent gate failure. Neither is acceptable, and the mechanism
    that resolves it is the same shape as PENDING: **a marker in the live
    contract, read by the checker, so the exception is visible rather than
    hard-coded.**
    """
    contract = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((root / "docs" / "contracts").glob("*-CONTRACT.md"))
    )
    return {
        name
        for line in contract.splitlines()
        if "SUPERSEDED" in line
        for name in re.findall(r"`([A-Z][A-Z_]{4,})`", line)
    }


def check_codes(root: Path) -> list[Problem]:
    """The contract and `Reason` must describe the same tool."""
    sys.path.insert(0, str(root / "src"))
    from prevalence_kit.errors import Reason

    in_code = {r.name for r in Reason}
    # Every contract, discovered, not one named file. Phase 2 added six codes
    # and this check reported all six as undocumented because it only ever read
    # the Phase 1 contract. Same shape as V-15: a check that names a row stops
    # covering the thing the day a second row appears.
    contract = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((root / "docs" / "contracts").glob("*-CONTRACT.md"))
    )
    in_contract = set(re.findall(r"`([A-Z][A-Z_]{4,})`", contract)) & (
        in_code | set(re.findall(r"\| `([A-Z_]+)`", contract))
    )

    pending = pending_codes(root)

    problems = [
        Problem(
            "codes",
            "contracts",
            f"{name} is in a contract but not in Reason, and is not marked PENDING",
        )
        for name in sorted(in_contract - in_code - pending - superseded_codes(root))
    ]
    problems += [
        Problem("codes", "errors.py", f"{name} exists but no contract names it")
        for name in sorted(in_code - in_contract)
    ]
    problems += [
        Problem("codes", "errors.py", f"{name} is marked PENDING but already exists")
        for name in sorted(pending & in_code)
    ]
    return problems


def check_findings(root: Path) -> list[Problem]:
    """Which accepted findings have no closing evidence?

    Reconciled against the code, not against the last report. This is the check
    that gives C-12's class a machine.
    """
    known = test_names(root)
    problems: list[Problem] = []
    for ident, _sev, status, evidence in register_rows(root):
        clean = evidence.strip("`").strip()
        if status == "open":
            problems.append(Problem("findings", ident, "accepted and still open"))
        elif status in {"closed", "ruled"}:
            if not clean or clean in {"—", "-", "none"}:
                problems.append(Problem("findings", ident, f"{status} with no evidence named"))
            elif clean not in known:
                problems.append(
                    Problem("findings", ident, f"names test {clean!r}, which does not exist")
                )
        elif status != "noted":
            problems.append(Problem("findings", ident, f"unknown status {status!r}"))
    return problems


def asserted_codes(root: Path) -> set[str]:
    """Reason codes a test actually names, by AST rather than by text search.

    Three spellings count, because the suite legitimately uses all three:

      `Reason.SOME_CODE`            direct reference
      `"SOME_CODE"`                 fixture-driven, comparing `reason.name`
      `"REFUSED [SOME_CODE]"`       the CLI surface, asserting stderr

    **The third was missed by the first draft of this function and the check
    reported a false positive**, on `RUN_NOT_FOUND`. The mutation sweep
    contradicted it: swapping that code made a test fail, so the suite could tell
    and the checker could not. **The instrument was wrong, not the suite.** So a
    code now counts if it appears anywhere inside a string literal, not only as
    the whole of one.

    **Docstrings are excluded, and that is the point of reading the AST.** A code
    discussed in prose is not a code under test. Widening to any string without
    that exclusion would have made this check pass on documentation, which is the
    failure it exists to catch.
    """
    found: set[str] = set()
    codes: set[str] = set()
    sys.path.insert(0, str(root / "src"))
    from prevalence_kit.errors import Reason

    codes = {r.name for r in Reason}

    for path in repo_files(root, "tests/*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        prose = {
            id(ast.get_docstring(node, clean=False) and node.body[0].value)  # type: ignore[attr-defined]
            for node in ast.walk(tree)
            if isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef)
        }
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Attribute)
                and isinstance(node.value, ast.Name)
                and node.value.id == "Reason"
            ):
                found.add(node.attr)
            elif (
                isinstance(node, ast.Constant)
                and isinstance(node.value, str)
                and id(node) not in prose
            ):
                found |= {code for code in codes if code in node.value}
    return found


def check_controls(root: Path) -> list[Problem]:
    """Which refusals can nobody prove fire?

    Doctrine rule 5: every gate gets a negative control, a positive control, and
    a **distinct reason code**. The distinct code is not decoration -- refusals
    that cannot be counted by cause make the refusal metric meaningless. So a
    code no test names is a refusal nobody has ever shown firing **for that
    reason**, whatever else the suite exercises on the way past it.

    **Found by D2.7's opening inventory, and confirmed by mutation rather than by
    reading.** Swapping `Reason.PLAN_MISSING` for an unrelated code at either of
    its two raise sites left all 418 tests passing. Same for
    `ALLOCATION_ROUNDING_UNDECLARED`. Three raise sites, no test able to tell.

    **`check_codes` looks like it covers this and does not.** It reconciles the
    `Reason` enum against the contracts in both directions, so every code is
    documented and every documented code exists. It says nothing about whether a
    code can fire, or whether anything checks that it does. That is D-34's shape
    again, in the checker that most looks like it already asked: **an
    instrument's coverage is defined by what it looks at.**
    """
    sys.path.insert(0, str(root / "src"))
    from prevalence_kit.errors import Reason

    asserted = asserted_codes(root)
    # Q9 / D-36. A code whose deliverable has not landed cannot have an
    # operator-facing control yet, and striking it would lose the contract's
    # promise in between. PENDING keeps the promise visible and unbuilt, which is
    # the honest state -- and `check_codes` expires the marker by machinery.
    deferred = pending_codes(root) | control_deferred_codes(root)
    return [
        Problem("controls", name, "no test names this reason code, so nothing proves it fires")
        for name in sorted({r.name for r in Reason} - asserted - deferred)
    ]


def check_register(root: Path) -> list[Problem]:
    """Which findings does the record discuss that the register never admitted?

    The other direction, and it is the one that was missing. `check_findings`
    validates the rows that are *present*: is each closed, does its named test
    exist? Nothing in that question can reveal a row that was never written.

    **V-12, V-13, V-14 and V-15 were each discussed across three to nine
    documents** -- V-12 in `SECURITY.md`, `docs/CORRECTIONS.md`,
    `docs/DECISIONS.md` and both contracts; V-15 in `CLAUDE.md` and in this file,
    which is the checker naming a finding the checker could not see -- while
    `docs/FINDINGS.md` held 22 rows and none of them these four. `check_claims`
    reported *"22 findings in the register, all accounted for"* for some weeks.
    **That statement was true and worthless.** It answered *is everything here
    consistent?* when the question was *is everything here?*

    **Third instance of one shape**, and the shape is what earns this check:

      V-15   `check_paths` read a fixed list of `src/` and `tests/` globs, so a
             new document was silently uncovered.
      C-23   the gate check read `gate.yml` with a regex, so it accepted a file
             its real consumer cannot parse.
      here   the findings check reconciled in one direction only.

    **An instrument's coverage is defined by what it looks at, and what it looks
    at is a choice someone made once.** Rule 11 says an obligation is tracked by
    name until discharged; the register is that rule's instrument, and it had
    holes it could not see.

    Scanned by pattern, never by a named list -- V-15's own lesson, applied to
    the check written because of V-15.
    """
    registered = {ident for ident, *_ in register_rows(root)}
    named: dict[str, set[str]] = {}
    for path in repo_files(root, *SCANNED):
        for ident in FINDING_ID.findall(path.read_text(encoding="utf-8")):
            named.setdefault(ident, set()).add(str(path.relative_to(root)).replace("\\", "/"))

    return [
        Problem(
            "register",
            ident,
            f"named in {len(where)} file(s) but has no row in docs/FINDINGS.md "
            f"({', '.join(sorted(where)[:3])}{', ...' if len(where) > 3 else ''})",
        )
        for ident, where in sorted(
            named.items(), key=lambda kv: (kv[0][0], int(kv[0].split("-")[1]))
        )
        if ident not in registered
    ]


def check_fixtures(root: Path) -> list[Problem]:
    """Can the shipped example perform the exit checks that name it?

    An exit check the director cannot perform is not a check. The findings check
    cannot see this: F-4's closing test passes, so the register is correct that
    it is closed *in the suite*. It has no way to know a different artifact
    cannot reproduce the contract's own instruction. D-23.

    Each requirement names the exit check that needs it, so a failure says what
    the director will not be able to do rather than only what is missing.
    """
    import csv

    sys.path.insert(0, str(root / "src"))
    from prevalence_kit.run import _wide_csv_fields
    from prevalence_kit.seal import CHUNK_BYTES

    labels = root / "examples" / "synthetic" / "labels.csv"
    if not labels.exists():
        return [Problem("fixtures", "examples/synthetic", "labels.csv is missing")]

    # Read it the way the tool reads it. The first version of this check used a
    # bare DictReader and died on `_csv.Error: field larger than field limit` --
    # the exact defect V-11 named, in the checker written to prevent its class.
    with labels.open(newline="", encoding="utf-8") as fh, _wide_csv_fields():
        rows = list(csv.DictReader(fh))

    problems: list[Problem] = []

    multi = [r for r in rows if len(r.get("content", "").encode("utf-8")) > CHUNK_BYTES]
    if not multi:
        problems.append(
            Problem(
                "fixtures",
                "examples/synthetic/labels.csv",
                f"no item exceeds CHUNK_BYTES ({CHUNK_BYTES:,}), so E9c -- swap two chunks "
                "within one item, expect SEAL_REORDERED -- cannot be performed. "
                "Run tools/make_example.py.",
            )
        )

    if len(rows) < 2:
        problems.append(
            Problem(
                "fixtures",
                "examples/synthetic/labels.csv",
                "too few rows for E9's cross-item cases",
            )
        )

    return problems


GATE_BLOCK = re.compile(r"## The gate is \w+ checks.*?```\n(.*?)```", re.DOTALL)
"""The fenced block under CLAUDE.md's gate heading. One command per line."""

GATE_COUNT = re.compile(r"## The gate is (\w+) checks")
NUMBER_WORD = {
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}

GATE_TOOLS = ("ruff ", "mypy", "pytest", "tools/check_claims.py")
"""Prefixes that mark a CI step as one of the gate's checks rather than setup."""


def ci_run_steps(workflow: Path) -> tuple[set[str], str | None]:
    """Every single-line `run:` in the workflow, and a parse error if there is one.

    Parsed, not pattern-matched. The first version read the file with a regex,
    so it read a workflow GitHub could not: an unquoted `name: mypy (config: src
    + tests)` is a nested mapping in YAML, the whole file failed to parse, and
    run 33205536300 died with "a workflow file issue" while all seven local
    checks were green. A checker that accepts what the real consumer rejects is
    not checking the same artifact.

    Multi-line `run:` blocks are scripts, not gate checks, and are skipped.
    """
    import yaml

    try:
        parsed = yaml.safe_load(workflow.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return set(), str(exc).replace("\n", " ")
    if not isinstance(parsed, dict):
        return set(), "workflow does not parse to a mapping"

    steps: set[str] = set()
    for job in (parsed.get("jobs") or {}).values():
        for step in (job or {}).get("steps") or []:
            command = step.get("run") if isinstance(step, dict) else None
            if isinstance(command, str) and "\n" not in command.strip():
                steps.add(_normalise_command(command))
    return steps, None


def _normalise_command(cmd: str) -> str:
    """`python -m ruff check .` and `ruff check .` are the same check."""
    cmd = re.sub(r"^python\s+-m\s+", "", cmd.strip())
    cmd = re.sub(r"^python\s+", "", cmd)
    cmd = re.sub(r"^\./", "", cmd)
    return " ".join(cmd.split())


def check_counts(root: Path) -> list[Problem]:
    """**D2.14(b).** The counts table in `docs/CORRECTIONS.md`, derived rather than trusted.

    That table counts this project's own counting errors and was maintained by
    hand. It was **over by one** -- C-36 -- and its own Total column summed to 38
    against a stated 37, visible to anyone who added it up.

    The semantics are written down in the file itself and this encodes them:

      * an **entry** is one `## C-n` or `## V-n` heading. Three corrections carry
        `V-` numbers because they were found as review findings; the letter
        records where they were found, not what they are;
      * **Open** counts entries whose `Status` row says `OPEN`;
      * `noted` is excluded from Open and included in Total.

    **A class tally is a different population from this table**, and reading one
    into the other is how the reviewer-instrument row reached 3. That is why this
    reads the entries and never the classes.
    """
    path = root / "docs" / "CORRECTIONS.md"
    if not path.exists():
        return [Problem("counts", "docs/CORRECTIONS.md", "is missing")]
    text = path.read_text(encoding="utf-8")

    entries = re.split(r"^## ((?:C|V)-\d+)", text, flags=re.M)
    blocks = list(zip(entries[1::2], entries[2::2], strict=True))
    if not blocks:
        return [Problem("counts", "docs/CORRECTIONS.md", "no C-n or V-n entries found")]

    total = len(blocks)
    noted = sum(1 for _, body in blocks if _status(body) == "noted")
    still_open = sum(1 for _, body in blocks if _status(body) == "open")
    shut = sum(1 for _, body in blocks if _status(body) == "closed")

    problems: list[Problem] = []
    row = re.search(
        r"^\|\s*\*\*Total\*\*\s*\|\s*\*\*(\d+)\*\*\s*\|\s*\*\*(\d+)\*\*\s*\|"
        r"\s*\*\*(\d+)\*\*\s*\|",
        text,
        flags=re.M,
    )
    if row is None:
        return [Problem("counts", "docs/CORRECTIONS.md", "has no Total row to check")]
    stated_open, stated_closed, stated_total = (
        int(row.group(1)),
        int(row.group(2)),
        int(row.group(3)),
    )
    if stated_closed != shut:
        problems.append(
            Problem(
                "counts",
                "docs/CORRECTIONS.md",
                f"Total row says {stated_closed} closed, entries say {shut}",
            )
        )
    if stated_open != still_open:
        problems.append(
            Problem(
                "counts",
                "docs/CORRECTIONS.md",
                f"Total row says {stated_open} open, entries say {still_open}",
            )
        )
    if stated_total != total:
        problems.append(
            Problem(
                "counts",
                "docs/CORRECTIONS.md",
                f"Total row says {stated_total} entries, file has {total}",
            )
        )
    unclassified = [ident for ident, body in blocks if _status(body) == "?"]
    if unclassified:
        problems.append(
            Problem(
                "counts",
                "docs/CORRECTIONS.md",
                f"no readable Status row: {', '.join(unclassified)}",
            )
        )

    # **Q22, ruled 2026-08-31 -- C-48.** CLAUDE.md's open-corrections row said
    # "49 entries, 6 open" while this file held 50 and 7, and credited this
    # check with reading a row it had never read. The scope is now the object
    # the code walks: the row's open count, its identifier list (both
    # directions) and its three figures are compared against the entries, and
    # ABSENCE of the row is a failure, so deleting it cannot silence the claim
    # -- C-47's lesson, applied here.
    open_ids = {ident for ident, body in blocks if _status(body) == "open"}
    claude = root / "CLAUDE.md"
    if not claude.exists():
        problems.append(Problem("counts", "CLAUDE.md", "is missing"))
        return problems
    row = re.search(
        r"^\|[^|\n]*\*\*(\d+) corrections open\*\*[^|\n]*\|([^\n]*)",
        claude.read_text(encoding="utf-8"),
        flags=re.M,
    )
    if row is None:
        problems.append(Problem("counts", "CLAUDE.md", "carries no '<N> corrections open' row"))
        return problems
    by_number = _entry_order
    if int(row.group(1)) != still_open:
        problems.append(
            Problem(
                "counts",
                "CLAUDE.md",
                f"row says {row.group(1)} corrections open, entries say {still_open}",
            )
        )
    stated_ids = set(re.findall(r"\b([CV]-\d+)\b", row.group(2)))
    missing = sorted(open_ids - stated_ids, key=by_number)
    extra = sorted(stated_ids - open_ids, key=by_number)
    if missing:
        problems.append(
            Problem(
                "counts",
                "CLAUDE.md",
                f"open in the register, absent from the row: {', '.join(missing)}",
            )
        )
    if extra:
        problems.append(
            Problem(
                "counts",
                "CLAUDE.md",
                f"named in the row, not open in the register: {', '.join(extra)}",
            )
        )
    figures = re.search(r"(\d+) entries, (\d+) closed, (\d+) `?noted`?", row.group(2))
    if figures is None:
        problems.append(
            Problem(
                "counts",
                "CLAUDE.md",
                "row carries no 'N entries, N closed, N noted' figures",
            )
        )
    else:
        for stated_n, actual, what in (
            (int(figures.group(1)), total, "entries"),
            (int(figures.group(2)), shut, "closed"),
            (int(figures.group(3)), noted, "noted"),
        ):
            if stated_n != actual:
                problems.append(
                    Problem(
                        "counts",
                        "CLAUDE.md",
                        f"row says {stated_n} {what}, entries say {actual}",
                    )
                )
    return problems


def _entry_order(ident: str) -> tuple[str, int]:
    """Sort `C-10` after `C-9`, not after `C-1`."""
    kind, _, number = ident.partition("-")
    return kind, int(number)


def _status(body: str) -> str:
    """`open`, `closed`, `noted`, or `?` when the entry has no readable Status row.

    **Three states, not two.** The first version knew only `open` and `noted`,
    which was true of the file until T-1 closed forty-one entries at once and the
    check reported every one of them as unreadable. It was right that it could not
    read them; the vocabulary was short.
    """
    found = re.search(r"\*\*Status\*\*\s*\|\s*(?:\*\*)?([A-Za-z]+)", body)
    if found is None:
        return "?"
    word = found.group(1).lower()
    if word in {"open", "closed", "noted"}:
        return word
    return "?"


def _hashed_fields(source: str) -> set[str] | None:
    """The keys `Plan.as_record` puts in the hashed record, read structurally.

    **`ast`, not a regex.** The first version of this matched indentation and
    reported every field as undeclared, which is C-23's rule arriving on the
    checker written to enforce the other three: read an artifact the way its real
    consumer reads it. Python source has one correct parser and this is it.

    Nested one level, because `estimand` is a dict inside the record and its four
    fields are commitments in their own right.
    """
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not (isinstance(node, ast.ClassDef) and node.name == "Plan"):
            continue
        for item in node.body:
            if not (isinstance(item, ast.FunctionDef) and item.name == "as_record"):
                continue
            for statement in ast.walk(item):
                if not (
                    isinstance(statement, ast.Return) and isinstance(statement.value, ast.Dict)
                ):
                    continue
                fields: set[str] = set()
                for key, value in zip(statement.value.keys, statement.value.values, strict=True):
                    if not (isinstance(key, ast.Constant) and isinstance(key.value, str)):
                        continue
                    fields.add(key.value)
                    if isinstance(value, ast.Dict):
                        fields.discard(key.value)
                        for inner in value.keys:
                            if isinstance(inner, ast.Constant) and isinstance(inner.value, str):
                                fields.add(f"{key.value}.{inner.value}")
                return fields
    return None


def check_schema(root: Path) -> list[Problem]:
    """**D2.14(d).** Every hashed plan field declares what it is for, and the
    declaration is checked against the code rather than believed.

    **Two plan fields have been inert and neither was found by an instrument.**
    `interval` was validated, hashed and read by nothing (F-10); `population` was
    read only to be printed and `labels` by nothing at all (F-11). One was found
    by reading code and asking what reads a field, the other by a probe the
    director named at the review stop.

    So `plan.FIELD_KIND` declares each field **behavioural** or **declarative**,
    and this asserts both halves:

      * every hashed field has a declared kind, and every declared kind names a
        hashed field -- both directions, D-28's rule;
      * every **behavioural** field is **read somewhere in `src/`** outside the
        plan module itself. A field only `plan.py` touches is a field nothing
        acts on, which is exactly what `interval` was.

    **What it cannot do, said here rather than left to be assumed.** It cannot
    prove a `declarative` field selects no behaviour -- absence is not
    observable this way. It checks the direction that has actually failed twice.
    """
    plan_py = root / "src" / "prevalence_kit" / "plan.py"
    if not plan_py.exists():
        return [Problem("schema", "src/prevalence_kit/plan.py", "is missing")]

    source = plan_py.read_text(encoding="utf-8")
    block = re.search(r"^FIELD_KIND = \{(.*?)^\}", source, flags=re.M | re.S)
    if block is None:
        return [Problem("schema", "src/prevalence_kit/plan.py", "has no FIELD_KIND map")]
    declared = dict(re.findall(r'"([\w.]+)":\s*"(behavioural|declarative)"', block.group(1)))

    hashed = _hashed_fields(source)
    if hashed is None:
        return [Problem("schema", "src/prevalence_kit/plan.py", "has no Plan.as_record to read")]

    problems: list[Problem] = []
    for field in sorted(hashed - set(declared)):
        problems.append(
            Problem(
                "schema",
                "src/prevalence_kit/plan.py",
                f"{field} is hashed but FIELD_KIND does not declare it",
            )
        )
    for field in sorted(set(declared) - hashed):
        problems.append(
            Problem(
                "schema",
                "src/prevalence_kit/plan.py",
                f"FIELD_KIND declares {field} but as_record does not hash it",
            )
        )

    # The half that has actually failed: a behavioural field nothing reads.
    others = [p for p in (root / "src" / "prevalence_kit").glob("*.py") if p.name != "plan.py"]
    elsewhere = "\n".join(p.read_text(encoding="utf-8") for p in others)
    for field, kind in sorted(declared.items()):
        if kind != "behavioural":
            continue
        attribute = field.split(".")[-1]
        if not re.search(rf"\.{attribute}\b", elsewhere):
            problems.append(
                Problem(
                    "schema",
                    "src/prevalence_kit/plan.py",
                    f"{field} is declared behavioural but nothing outside plan.py "
                    f"reads it -- F-10's shape",
                )
            )
    return problems


def check_open_items(root: Path) -> list[Problem]:
    """**D2.14(c), widened 2026-08-30.** An obligation asserted in two states.

    `CLAUDE.md`'s *Open, by name* table is a **live figure written in prose**, and
    nothing checked it. Its three machine-checked figures were current while
    **four hand-maintained rows in the same file had drifted**, inside about six
    hours: charter section 6.1 (discharged by A-3), O-20 and O-22 (both moved at
    `d25e6fe`), and the corrections range.

    **The first version read one table in one direction, and section 11 of the
    Phase 2 contract proved that was too narrow.** That table still said
    *"O-26 | Unmet, named blocker: A-5 unruled"* after A-5 was applied and O-26
    was built. The row is the artifact the director rules on at phase close, and
    nothing compared it to the tree. It also missed **O-3**, discharged in the
    same section 11 and still listed as carried in `CLAUDE.md` -- because the
    discharge scan was case-sensitive and section 11 writes *Discharged*, not
    *DISCHARGED*.

    **The condition now:** an obligation whose identifier heads a table row in one
    live document, asserted **discharged** there and **unmet or open** somewhere
    else, is a failure. Both directions, every table, because *which* of the two
    rows is stale is not something a checker can know -- and does not need to.

    **Three scope decisions, stated because each one silences something.**

    1. **The identifier must be in the row's FIRST cell.** An `O-n` mentioned in
       passing inside a long prose cell is a citation, not a status claim.
       Scanning whole rows flagged D2.12's deliverable row, where *"O-4"* and
       *"unmet"* appear in unrelated sentences about C-9 and C-1.
    2. **Contracts for closed phases are read for their discharges only** --
       Q24, ruled 2026-08-31, replacing a full exclusion. A dated contract's
       open-state rows were true at its close and expire without the document
       changing: Phase 1's section 10 records O-16 and O-17 as *unmet, named
       blocker: no remote*, both discharged in Phase 2, and **a dated reading
       is never rewritten to satisfy a checker**. Its discharge rows never
       expire -- a discharge is permanent, open-ness is what ages. The full
       exclusion silently cost this check every discharge the Phase 2 outcome
       records the day the Phase 3 contract was created, and the selftest's
       planted O-4 row going undetected is what surfaced it.
    3. **It still cannot tell that a row's prose has gone stale while its
       identifier is genuinely open.** That is unchanged, and claiming otherwise
       would be C-34.
    """
    claude = root / "CLAUDE.md"
    if not claude.exists():
        return [Problem("open-items", "CLAUDE.md", "is missing")]
    if not re.search(r"^### Open, by name$", claude.read_text(encoding="utf-8"), flags=re.M):
        return [Problem("open-items", "CLAUDE.md", "has no 'Open, by name' table")]

    claims = _obligation_claims(root)
    problems: list[Problem] = []
    for ident in sorted(claims, key=lambda o: int(o[2:])):
        rows = claims[ident]
        states = {state for _, _, state in rows}
        if len(states) < 2:
            continue
        open_at = [f"{path}:{line}" for path, line, state in rows if state == "open"]
        done_at = [f"{path}:{line}" for path, line, state in rows if state == "discharged"]
        problems.append(
            Problem(
                "open-items",
                open_at[0].split(":")[0],
                f"{ident} is listed as open at {', '.join(open_at)} "
                f"but marked discharged at {', '.join(done_at)}",
            )
        )
    return problems


_OPEN_WORDS = re.compile(r"\b(UNMET|Unmet|unmet|OPEN|Open|Carried|CARRIED)\b")
_DONE_WORDS = re.compile(r"\b(DISCHARGED|Discharged|discharged|CLOSED|Closed|DONE|Done)\b")


def _live_documents(root: Path) -> list[Path]:
    """Where a status claim about an obligation is still a live claim.

    `OBLIGATION_SOURCES` plus `CLAUDE.md`, **minus the contract of every phase
    that has closed**. Derived from `current_phase` rather than naming a file, so
    it moves on its own when Phase 3 opens -- the alternative is a constant that
    is right today and wrong at the next boundary.
    """
    live = current_phase(root)
    paths = [root / "CLAUDE.md"]
    for pattern in OBLIGATION_SOURCES:
        for path in sorted(root.glob(pattern)):
            phase = re.search(r"PHASE-(\d+)-CONTRACT\.md$", path.name)
            if phase is not None and int(phase.group(1)) < live:
                continue
            paths.append(path)
    return [p for p in paths if p.exists()]


def _closed_contracts(root: Path) -> list[Path]:
    """The contracts `_live_documents` excludes -- read one-directionally.

    **Q24, ruled 2026-08-31.** A closed phase's contract is where its outcome
    records obligations as discharged, and a discharge is permanent: that row
    cannot go stale. Its open-state rows are the opposite -- true at the close,
    expiring without the document changing -- and flagging them would demand
    edits to a dated document. So these contribute their **discharge claims
    only**. Before this, the full exclusion meant every discharge in the Phase 2
    outcome left the walked set the moment the Phase 3 contract existed, and
    the selftest's planted violation went undetected -- the check's coverage
    shrank at exactly the boundary it exists to police.
    """
    live = current_phase(root)
    paths = []
    for path in sorted((root / "docs" / "contracts").glob("*-CONTRACT.md")):
        phase = re.search(r"PHASE-(\d+)-CONTRACT\.md$", path.name)
        if phase is not None and int(phase.group(1)) < live:
            paths.append(path)
    return paths


def _obligation_claims(root: Path) -> dict[str, list[tuple[str, int, str]]]:
    """`{O-n: [(file, line, "open" | "discharged"), ...]}` from every live table.

    A row counts when an obligation identifier appears in its **first cell**. The
    state is read from the whole row, which is safe because no row in the record
    asserts both -- checked before this rule was written, not assumed.

    **A row under a *Done* heading asserts discharge whether or not it says so**,
    and that is the clause that catches the case this widening was built for.
    Section 11 of the Phase 2 contract said *"O-26 | Unmet, named blocker: A-5
    unruled"* while `CLAUDE.md` listed D2.17 / O-26 in its **Done** table -- and
    the Done row carries no status word at all, so a word-matching rule saw one
    claim, found nothing to contradict, and passed. **The heading is the claim.**
    """
    claims: dict[str, list[tuple[str, int, str]]] = {}
    sources = [(path, False) for path in _live_documents(root)]
    # Closed contracts: discharge claims only. Q24 -- see _closed_contracts.
    sources += [(path, True) for path in _closed_contracts(root)]
    for path, discharge_only in sources:
        rel = path.relative_to(root).as_posix()
        section = ""
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if line.startswith("#"):
                section = "done" if line.strip().lower().endswith("done") else ""
            if not line.startswith("|"):
                continue
            cells = line.split("|")
            if len(cells) < 3:
                continue
            idents = set(re.findall(r"\b(O-\d+)\b", cells[1]))
            if not idents:
                continue
            # **Where the state is read from, and the order matters.**
            #
            # 1. The FIRST CELL wins when it carries a state word. Section 10
            #    writes `| O-4 > DISCHARGED by D2.9 | ... O-13 is separate and
            #    still open ... |` -- the status belongs to O-4 and the mention
            #    of O-13 is prose about a neighbour.
            # 2. Otherwise the rest of the row, but ONLY if it names no other
            #    obligation. Section 11 writes `| O-26 | **Unmet, named blocker
            #    ...** |`, where the status is genuinely in the second cell.
            # 3. A row under a *Done* heading is discharged either way.
            #
            # The first draft read the whole row and attributed the state to
            # whatever cell 1 named. It fired on a row listing O-14 and O-15 as
            # carried whose prose explained that O-3 had been discharged. The
            # second draft skipped any row naming another obligation -- and
            # silenced section 10's O-4 row, which is a real discharge claim.
            # **Both were found by running it, not by reading it.**
            others = set(re.findall(r"\b(O-\d+)\b", line)) - idents
            head = cells[1]
            if _DONE_WORDS.search(head) or _OPEN_WORDS.search(head):
                scope = head
            else:
                scope = "" if others else line
            if _DONE_WORDS.search(scope) or section == "done":
                state = "discharged"
            elif _OPEN_WORDS.search(scope):
                state = "open"
            else:
                continue
            if discharge_only and state != "discharged":
                continue
            for ident in idents:
                claims.setdefault(ident, []).append((rel, number, state))
    return claims


def check_gate(root: Path) -> list[Problem]:
    """The documented gate and the executed gate must be one list.

    V-16: `CLAUDE.md` documented seven checks and `gate.yml` ran six. The missing
    one was `mypy` in its config form, so the eleven test files were never
    type-checked on the remote -- 12 files against 23. A type error in a test
    passed CI and failed on the director's machine, and nothing said the remote
    gate was the weaker one.

    Same shape as V-15: an instrument whose inputs drifted from what it claims to
    cover, with no failure and no warning, just less checked than the day before.
    """
    problems: list[Problem] = []
    claude = root / "CLAUDE.md"
    workflow = root / ".github" / "workflows" / "gate.yml"
    if not claude.exists() or not workflow.exists():
        return problems

    claude_text = claude.read_text(encoding="utf-8")
    block = GATE_BLOCK.search(claude_text)
    if not block:
        return [Problem("gate", "CLAUDE.md", "no machine-readable gate block found")]

    documented = [_normalise_command(ln) for ln in block.group(1).splitlines() if ln.strip()]
    executed, parse_error = ci_run_steps(workflow)
    if parse_error:
        # No point comparing lists against a file GitHub will refuse to read.
        return [Problem("gate", ".github/workflows/gate.yml", f"is not valid YAML: {parse_error}")]

    # The heading's number word is itself a restated figure. C-7's class.
    stated = GATE_COUNT.search(claude_text)
    if stated and NUMBER_WORD.get(stated.group(1)) not in (None, len(documented)):
        problems.append(
            Problem(
                "gate",
                "CLAUDE.md",
                f"heading says {stated.group(1)} checks, the block lists {len(documented)}",
            )
        )

    for cmd in documented:
        if cmd not in executed:
            problems.append(Problem("gate", ".github/workflows/gate.yml", f"does not run `{cmd}`"))

    for cmd in sorted(executed):
        if cmd.startswith(GATE_TOOLS) and cmd not in documented:
            problems.append(
                Problem("gate", "CLAUDE.md", f"gate.yml runs `{cmd}`, which is not documented")
            )
    return problems


def current_phase(root: Path) -> int:
    """The phase in progress: the highest-numbered contract that exists.

    Deliberately this simple, and the reason is worth stating. The first version
    tried to read a CLOSED marker out of each contract's status line. Phase 1's
    closure is in its section 10, not its status line, so that version would have
    called Phase 1 live and still returned the right answer -- by taking a max
    over a test that never fired. **A check that gets the right answer for a
    reason that does not hold is the thing rule 8 is about**, so it was replaced
    rather than tuned.

    A contract for phase N+1 is written only when phase N is done, so the newest
    contract is the live phase. That is a real property of how this project
    works, and if it ever stops being true this returns a wrong number loudly
    instead of a right one by luck.
    """
    numbers = [
        int(m.group(1))
        for path in (root / "docs" / "contracts").glob("PHASE-*-CONTRACT.md")
        if (m := re.search(r"PHASE-(\d)-CONTRACT", path.name))
    ]
    return max(numbers) if numbers else 0


ANSI = re.compile(r"\x1b\[[0-9;]*m")
"""SGR colour escapes, so a coloured line can still be read as a number."""


def collected_tests(root: Path) -> int:
    """How many tests the suite actually has, by collecting them.

    Counted rather than remembered. `pytest --collect-only -q` is the consumer's
    own count, which is the point -- CLAUDE.md's figure is a claim about what
    `pytest` reports, so `pytest` is what should produce it.
    """
    import subprocess

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "--collect-only",
            # `-o addopts=` clears pyproject's own `-q`. Without it our `-q`
            # becomes `-qq`, which prints per-file counts and no total -- the
            # same doubling that suppressed the count in CI (V-16's sibling,
            # and the reason CLAUDE.md says never to pass `-q`). It bit here,
            # inside the checker written to catch stale counts.
            "-o",
            "addopts=",
            "-q",
            "--no-header",
            "-p",
            "no:cacheprovider",
        ],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    for line in reversed(result.stdout.splitlines()):
        # Strip ANSI colour before matching. pytest normally emits none when
        # its output is captured, but `FORCE_COLOR` in the environment makes it
        # colour anyway -- and then this returned **-1**, silently, which is the
        # worst possible answer: it is not a count, and every claim compared
        # against it fails for a reason that has nothing to do with the claim.
        # Found on a shell that sets FORCE_COLOR=3; CI and PowerShell do not.
        if m := re.match(r"^(\d+) tests? collected", ANSI.sub("", line).strip()):
            return int(m.group(1))
    return -1


def highest_ruled_question(root: Path) -> int:
    """The highest numbered question a contract records as RULED.

    CLAUDE.md says "Q1-Qn ruled" and that n went stale within hours of being
    written. It is derivable: the contracts mark a ruling with **RULED** or
    "RULED:", beside the question's own heading.
    """
    highest = 0
    for path in sorted((root / "docs" / "contracts").glob("*-CONTRACT.md")):
        text = path.read_text(encoding="utf-8")
        parts = re.split(r"^### Q(\d+)", text, flags=re.M)
        for number, body in zip(parts[1::2], parts[2::2], strict=True):
            if re.search(r"\*\*RULED", body) or "RULED:" in body:
                highest = max(highest, int(number))
    return highest


def check_figures(root: Path) -> list[Problem]:
    """Figures restated in prose must be derivable, not remembered.

    Narrow on purpose: it checks the figures this build has already got wrong
    rather than every number in every document. A checker that flags hundreds of
    false positives gets switched off, and a switched-off checker defends nothing.
    """
    problems: list[Problem] = []
    sys.path.insert(0, str(root / "src"))
    from prevalence_kit.errors import Reason
    from prevalence_kit.run import _CSV_FIELD_LIMIT

    # Collected once. It shells out to pytest, and it is wanted twice: by the
    # CLAUDE.md claim below and by the tests badge. Deriving it twice per call
    # tripled the suite the first time these were written independently.
    tests_collected = collected_tests(root)

    claims = {
        "reason codes": (
            len(list(Reason)),
            re.compile(r"\*\*(\d+) reason codes in total"),
            root / "docs" / "contracts" / "PHASE-2-CONTRACT.md",
        ),
        "csv ceiling": (
            _CSV_FIELD_LIMIT,
            re.compile(r"exactly (\d[\d,]*) bytes"),
            root / "src" / "prevalence_kit" / "run.py",
        ),
        "findings in register": (
            len(register_rows(root)),
            re.compile(r"(\d+) findings in the register"),
            root / "docs" / "FINDINGS.md",
        ),
        # The README's phase claim used to live here as a number-only pattern
        # compared against current_phase -- the semantics C-47 condemned, kept
        # vacuous beside their replacement until Q21 ruled the entry deleted.
        # The phase sentence is checked by _phase_problems alone: both files,
        # word and number, absence a failure.
        # CLAUDE.md went stale within hours of being written -- "Q1-Q7 ruled"
        # and "406 tests locally / CI green at 401" were both wrong by the same
        # afternoon. It is the more consequential file: a stale README misleads
        # a reader, a stale CLAUDE.md misleads the NEXT SESSION before it has
        # read anything else and while it is deciding what to trust.
        #
        # The test count is the figure that moves most and is easiest to derive.
        "claude.md tests": (
            tests_collected,
            re.compile(r"\*\*(\d[\d,]*) tests\*\*"),
            root / "CLAUDE.md",
        ),
        "claude.md rulings": (
            highest_ruled_question(root),
            re.compile(r"\*\*Q1.Q(\d+) ruled"),
            root / "CLAUDE.md",
        ),
    }
    for label, (actual, pattern, path) in claims.items():
        if not path.exists():
            continue
        for stated in pattern.findall(path.read_text(encoding="utf-8")):
            if int(stated.replace(",", "")) != actual:
                problems.append(
                    Problem(
                        "figures",
                        f"{path.relative_to(root)}",
                        f"{label}: states {stated}, artifact says {actual}",
                    )
                )
    problems.extend(_phase_problems(root))
    problems.extend(_svy_credit_problems(root))
    problems.extend(_badge_problems(root, badge_figures(root, tests_collected)))
    return problems


BADGE = re.compile(r"!\[[^\]]*\]\(https://img\.shields\.io/badge/([^)\s]+)\)")
"""A shields.io badge in the README. The label and value live in the URL path,
percent-encoded, as `label-value-colour`."""


def badge_figures(root: Path, tests_collected: int | None = None) -> dict[str, int]:
    """The badge numbers, derived from the artifacts that own them.

    Split out from the check so a test can inject cheap values. Deriving the
    test count means collecting the suite in a subprocess, and a test that
    calls it collects the suite from inside the suite -- which works and cost
    three minutes of wall clock the first time it was written this way.
    """
    sys.path.insert(0, str(root / "src"))
    from prevalence_kit.errors import Reason

    gate_block = GATE_BLOCK.search((root / "CLAUDE.md").read_text(encoding="utf-8"))
    return {
        "tests": collected_tests(root) if tests_collected is None else tests_collected,
        "gate checks": len([ln for ln in gate_block.group(1).splitlines() if ln.strip()])
        if gate_block
        else -1,
        "reason codes": len(list(Reason)),
    }


def _badge_problems(root: Path, derived: dict[str, int] | None = None) -> list[Problem]:
    """**Charter section 5.6: badge-truth.** A badge states a figure; derive it.

    The charter names "badge-truth tests" as one of the two things that make
    honesty *enforced by machinery, not intention*, and neither existed until
    the launch programme. A badge is the most-read claim in a repository and
    the least-checked: it is a picture of a number, and nothing about a picture
    goes stale visibly.

    **The scope is the badges this function can derive, and no others** --
    stated here because C-34 was a checker that claimed a scope it did not
    have. Licence and Python-version badges are not derived; they are asserted
    by `test_the_licence_claim_and_the_licence_file_agree` and by the
    `requires-python` pin respectively. An unknown badge label is IGNORED
    rather than failed, so adding a badge is never blocked by this check --
    which is itself a gap, and the honest name for it is: this catches a badge
    that has gone stale, not a badge that was never true.
    """
    readme = root / "README.md"
    if not readme.exists():
        return [Problem("figures", "README.md", "is missing")]

    if derived is None:
        derived = badge_figures(root)

    problems: list[Problem] = []
    seen: set[str] = set()
    for path in BADGE.findall(readme.read_text(encoding="utf-8")):
        # `label-value-colour`, percent-encoded. Hyphens inside a label are
        # doubled by the shields.io syntax, which is why this splits on the
        # encoded spaces rather than on hyphens.
        parts = unquote(path).split("-")
        if len(parts) < 3:
            continue
        label, value = parts[0].strip(), parts[1].strip()
        if label not in derived:
            continue
        seen.add(label)
        stated = re.search(r"\d[\d,]*", value)
        if stated is None:
            problems.append(Problem("figures", "README.md", f"badge {label!r} states no number"))
            continue
        if int(stated.group().replace(",", "")) != derived[label]:
            problems.append(
                Problem(
                    "figures",
                    "README.md",
                    f"badge {label!r}: states {stated.group()}, artifact says {derived[label]}",
                )
            )

    # Absence is a failure, as it is for the phase sentence: deleting a badge
    # must not be a way to stop it being checked.
    for label in derived:
        if label not in seen:
            problems.append(Problem("figures", "README.md", f"carries no {label!r} badge"))
    return problems


SVY_CREDIT = re.compile(r"`svy`.{0,200}?the estimator layer", re.S)
"""O-10 / C-1: the README credits `svy` as the estimator layer.

Ruled at the Phase 3 review stop, 2026-08-31: the credit is C-1's closing
condition, and nothing should hold it in place by memory. Absence is a failure
-- C-47's lesson, third application: a deleted sentence must not silence the
claim it carried."""


def _svy_credit_problems(root: Path) -> list[Problem]:
    readme = root / "README.md"
    if not readme.exists():
        return [Problem("figures", "README.md", "is missing")]
    if not SVY_CREDIT.search(readme.read_text(encoding="utf-8")):
        return [
            Problem(
                "figures",
                "README.md",
                "carries no `svy` estimator-layer credit -- O-10, and C-1's closing condition",
            )
        ]
    return []


PHASE_SENTENCE = re.compile(r"Phase (\d) of 4 (in progress|complete)")
r"""The one canonical phase sentence, in the same shape in both public files.

**It replaces two patterns that failed in opposite directions**, and the pair is
worth keeping in mind because they came from one root:

  README.md    `Phase (\d) of 4 in progress` compared the NUMBER to the highest
               contract and never read the word. Phase 2 closed, the number
               stayed 2, and the check **went green on a false sentence** --
               C-34's class, in the most public file this project has.
  CLAUDE.md    `\*\*Phase (\d) is in build\*\*` had no true form once the phase
               closed, so the sentence was removed and the claim **went
               vacuous**: `findall` over no matches reports nothing.

**A checker that affirms a wrong claim is worse than one that says nothing**, and
this project had one of each from a single cause: `current_phase` means *the
highest-numbered contract that exists*, which is not *the phase in progress*.
"""


def phase_state(root: Path) -> tuple[int, str]:
    """`(number, "in progress" | "complete")`, derived from the contract itself.

    A phase is complete when its own contract records the close in its outcome
    section. Both closures are written as a bold line at the start of it, which
    is the marker read here rather than a hand-maintained flag somewhere else.
    """
    number = current_phase(root)
    contract = root / "docs" / "contracts" / f"PHASE-{number}-CONTRACT.md"
    closed = False
    if contract.exists():
        closed = bool(
            re.search(
                rf"^\*\*(?:Phase {number} )?CLOSED\b",
                contract.read_text(encoding="utf-8"),
                flags=re.M,
            )
        )
    return number, "complete" if closed else "in progress"


def _phase_problems(root: Path) -> list[Problem]:
    """Both public files carry the phase sentence, and it must be true.

    **Absence is a failure here, unlike every other figure claim.** The rest of
    `check_figures` iterates its matches, so a claim whose sentence is deleted
    reports nothing -- which is how the CLAUDE.md half of this went quiet.
    Deleting the sentence must not be a way to silence the check.
    """
    number, state = phase_state(root)
    problems: list[Problem] = []
    for name in ("README.md", "CLAUDE.md"):
        path = root / name
        if not path.exists():
            continue
        found = PHASE_SENTENCE.findall(path.read_text(encoding="utf-8"))
        if not found:
            problems.append(Problem("figures", name, f"carries no `Phase N of 4 {state}` sentence"))
            continue
        for stated_number, stated_state in found:
            if (int(stated_number), stated_state) != (number, state):
                problems.append(
                    Problem(
                        "figures",
                        name,
                        f"phase: states 'Phase {stated_number} of 4 {stated_state}', "
                        f"artifact says 'Phase {number} of 4 {state}'",
                    )
                )
    return problems


CHECKS = {
    "citations": check_citations,
    "paths": check_paths,
    "codes": check_codes,
    "findings": check_findings,
    "register": check_register,
    "controls": check_controls,
    "fixtures": check_fixtures,
    "figures": check_figures,
    "gate": check_gate,
    "counts": check_counts,
    "schema": check_schema,
    "open-items": check_open_items,
}


def run(root: Path) -> list[Problem]:
    problems: list[Problem] = []
    for fn in CHECKS.values():
        problems.extend(fn(root))
    return problems


# ------------------------------------------------------------------ selftest


def selftest() -> int:
    """Prove each check can fail. Plants one violation at a time in a copy.

    Without this, a bug that made every check return an empty list would leave
    the tool passing forever while checking nothing.
    """
    import shutil
    import tempfile

    plants: dict[str, tuple[str, str, str]] = {
        "citations": ("src/prevalence_kit/errors.py", '"""Refusals.', '"""Refusals. See D-999.'),
        "paths": (
            # Deliberately CLAUDE.md, not a Python file: the old check read a
            # fixed list of src/ and tests/ globs, so this plant would not have
            # been seen at all. V-15 was exactly that gap.
            "CLAUDE.md",
            "# prevalence-kit",
            "# prevalence-kit\n\nSee docs/does-not-exist.md.",
        ),
        "codes": (
            "src/prevalence_kit/errors.py",
            '    SEED_MISSING = "SEED_MISSING"',
            '    SEED_MISSING = "SEED_MISSING"\n    UNDOCUMENTED_CODE = "UNDOCUMENTED_CODE"',
        ),
        "findings": (
            "docs/FINDINGS.md",
            "`test_a_non_numeric_label_is_refused_by_name`",
            "`test_that_was_never_written`",
        ),
        "controls": (
            # Plant: stop a test naming SEED_MISSING, which exactly one test
            # names. The code goes on being raised in plan.py and goes on being
            # documented in the contract, so `codes` stays green -- which is
            # precisely the blind spot this check was added to cover.
            "tests/test_core.py",
            "Reason.SEED_MISSING",
            "Reason.LEDGER_BROKEN",
        ),
        "register": (
            # The plant is the defect exactly as it was: delete V-12's row and
            # leave every other mention of it standing. V-12 is discussed in
            # SECURITY.md, both contracts, CORRECTIONS.md, DECISIONS.md and a
            # test docstring, and for some weeks the register did not hold it.
            # A stand-in id nobody writes about would not reproduce that -- the
            # point is a finding the record talks about at length.
            "docs/FINDINGS.md",
            "| V-12 | high | closed | "
            "`test_the_tampered_plan_is_caught_without_the_flag` | D-24 |\n",
            "",
        ),
        "counts": (
            # The defect exactly as it was: the Total row over by one. C-36 sat
            # in the file with its own columns summing to 38 against a stated 37.
            "docs/CORRECTIONS.md",
            "| **Total** | **11** | **41** | **54** |",
            "| **Total** | **11** | **40** | **54** |",
        ),
        "schema": (
            # F-10's shape, planted: declare a field behavioural that nothing
            # outside plan.py reads. `interval` was exactly this for four
            # commits -- validated, hashed, and read by nothing.
            "src/prevalence_kit/plan.py",
            '    "estimand.description": "declarative",',
            '    "estimand.description": "declarative",\n    "seed": "behavioural",\n'
            '    "nothing_reads_me": "behavioural",',
        ),
        "open-items": (
            # A row naming an obligation the record already marks discharged.
            # O-4 was discharged by D2.9; listing it as open is the drift this
            # check exists for.
            "CLAUDE.md",
            "| **O-21** | The rare-event specificity fact must reach the README | Phase 3 |",
            "| **O-4** | **Unmet, carried.** Still awaiting the cross-check | Phase 2 |",
        ),
        "figures": (
            "src/prevalence_kit/run.py",
            "bytes. Not unbounded",
            "bytes. Not unbounded",
        ),
        "fixtures": (
            "examples/synthetic/labels.csv",
            "",
            "",
        ),
        "gate": (
            # The plant is the defect itself: `pytest -q` on top of
            # addopts = "-q" is -qq, which suppresses the count. That shipped in
            # CI and only the first real run exposed it.
            ".github/workflows/gate.yml",
            "        run: pytest\n",
            "        run: pytest -q\n",
        ),
    }

    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        for name, (rel, old, new) in plants.items():
            copy = Path(tmp) / name
            shutil.copytree(
                ROOT,
                copy,
                ignore=shutil.ignore_patterns(".venv", "__pycache__", ".git", "*.pdf"),
            )
            target = copy / rel
            text = target.read_text(encoding="utf-8")
            if name == "figures":
                # Change the artifact, not the prose, so the two disagree.
                text = text.replace("_CSV_FIELD_LIMIT = 64 * 1024 * 1024", "_CSV_FIELD_LIMIT = 123")
            elif name == "fixtures":
                # Shrink every content field, recreating the C-15 regression.
                lines = text.splitlines()
                text = "\n".join([lines[0], *(ln[:60] for ln in lines[1:4])]) + "\n"
            else:
                assert old in text, f"selftest plant anchor missing for {name}"
                text = text.replace(old, new, 1)
            target.write_text(text, encoding="utf-8", newline="\n")

            for mod in [m for m in sys.modules if m.startswith("prevalence_kit")]:
                del sys.modules[mod]
            sys.path.insert(0, str(copy / "src"))
            caught = [p for p in CHECKS[name](copy) if p.check == name]
            sys.path.pop(0)

            status = "OK  " if caught else "FAIL"
            if not caught:
                failures += 1
            print(f"  [{status}] {name}: planted a violation, checker found {len(caught)}")
            if caught:
                print(f"         {caught[0].detail}")

    for mod in [m for m in sys.modules if m.startswith("prevalence_kit")]:
        del sys.modules[mod]
    print()
    if failures:
        print(f"SELFTEST FAILED: {failures} check(s) did not detect their planted violation.")
        return 1
    print(f"SELFTEST PASSED: all {len(plants)} checks detected their planted violation.")
    return 0


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest", action="store_true", help="prove each check can fail")
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.selftest:
        return selftest()

    problems = run(ROOT)
    if not problems:
        rows = register_rows(ROOT)
        print(f"check_claims: reconciled. {len(rows)} findings in the register, all accounted for.")
        return 0

    print(f"check_claims: {len(problems)} problem(s).\n")
    for problem in problems:
        print(problem.line())
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
