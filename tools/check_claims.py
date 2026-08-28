#!/usr/bin/env python
"""Reconcile what the record claims against what the repository contains.

Doctrine rule 14: a lesson that lives only in prose will not hold, so build the
check. Rule 11: an obligation is tracked by name until discharged, and reported
against the artifact rather than against the last report.

Seven checks, each answering a question that has actually gone wrong here.
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

ROOT = Path(__file__).resolve().parents[1]

CITATION = re.compile(r"\b([DCO])-(\d{1,3})\b")
FINDING_REF = re.compile(r"\b([FV])-(\d{1,2})\b")
PATH_LIKE = re.compile(r"(?<![\w./-])((?:src|tests|docs|tools)/[\w./-]+\.(?:py|md|toml|txt))")
"""A repository path. The lookbehind matters: without it `awesome-safety-tools/README.md`
matched on its `tools/README.md` suffix and was reported as a missing file."""


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


def defined_ids(root: Path) -> dict[str, set[str]]:
    """What the record actually defines, read from the record.

    Obligations are spread across two files -- O-1..O-6 in STANDARDS.md, the rest
    in DECISIONS.md -- so both are read. The first run of this checker flagged
    O-4 as undefined for exactly that reason, which is the checker finding a real
    thing about its own inputs.
    """
    decisions = (root / "docs" / "DECISIONS.md").read_text(encoding="utf-8")
    corrections = (root / "docs" / "CORRECTIONS.md").read_text(encoding="utf-8")
    standards = (root / "docs" / "STANDARDS.md").read_text(encoding="utf-8")
    return {
        "D": set(re.findall(r"^## (D-\d+)", decisions, re.M)),
        "C": set(re.findall(r"^## (C-\d+)", corrections, re.M)),
        # Obligations live in tables, not headings, and in two documents.
        "O": set(re.findall(r"^\| (O-\d+) \|", decisions + standards, re.M)),
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


def check_codes(root: Path) -> list[Problem]:
    """The contract and `Reason` must describe the same tool."""
    sys.path.insert(0, str(root / "src"))
    from prevalence_kit.errors import Reason

    in_code = {r.name for r in Reason}
    contract = (root / "docs" / "contracts" / "PHASE-1-CONTRACT.md").read_text(encoding="utf-8")
    in_contract = set(re.findall(r"`([A-Z][A-Z_]{4,})`", contract)) & (
        in_code | set(re.findall(r"\| `([A-Z_]+)`", contract))
    )
    problems = [
        Problem("codes", "contract §4", f"{name} is in the contract but not in Reason")
        for name in sorted(in_contract - in_code)
    ]
    problems += [
        Problem("codes", "errors.py", f"{name} exists but the contract never names it")
        for name in sorted(in_code - in_contract)
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

CI_RUN = re.compile(r"^\s+run:[ \t]+(?!\|)(.+?)\s*$", re.MULTILINE)
"""A single-line `run:` step. The `|` block form is a script, not a gate check."""

GATE_TOOLS = ("ruff ", "mypy", "pytest", "tools/check_claims.py")
"""Prefixes that mark a CI step as one of the gate's checks rather than setup."""


def _normalise_command(cmd: str) -> str:
    """`python -m ruff check .` and `ruff check .` are the same check."""
    cmd = re.sub(r"^python\s+-m\s+", "", cmd.strip())
    cmd = re.sub(r"^python\s+", "", cmd)
    cmd = re.sub(r"^\./", "", cmd)
    return " ".join(cmd.split())


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
    executed = {_normalise_command(c) for c in CI_RUN.findall(workflow.read_text(encoding="utf-8"))}

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

    claims = {
        "reason codes": (
            len(list(Reason)),
            re.compile(r"\*\*(\d+) reason codes"),
            root / "docs" / "contracts" / "PHASE-1-CONTRACT.md",
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
    return problems


CHECKS = {
    "citations": check_citations,
    "paths": check_paths,
    "codes": check_codes,
    "findings": check_findings,
    "fixtures": check_fixtures,
    "figures": check_figures,
    "gate": check_gate,
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
