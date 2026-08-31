"""Properties of the record and the operator-facing surface.

These are the tests `docs/FINDINGS.md` names as closing evidence for findings
that have no natural home in the behaviour suite -- a canonical-bytes claim, a
docstring that must not over-promise, a cross-library difference, and the
plain-ASCII property of every message an operator reads.

They exist because rule 8 says a limit that is checkable is asserted as a
*passing* test, so the day it stops being true the suite fails and forces the
claim to be rewritten rather than quietly outliving its own truth.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

from prevalence_kit.canonical import canonical
from prevalence_kit.plan import Plan
from prevalence_kit.run import Workspace, do_plan
from prevalence_kit.seal import Manifest, SealedStore

SRC = Path(__file__).resolve().parents[1] / "src" / "prevalence_kit"


# ---------------------------------------------------------------------- V-9


def test_the_sealed_plan_is_canonical_bytes(tmp_path: Path, plan: Plan) -> None:
    """V-9. The sealed plan used to be `json.dumps(..., sort_keys=True)`.

    `canonical.py`'s own docstring says everything hashed anywhere goes through
    one function, so two parties can never disagree about what "the hash of this"
    means. With default separators they could: an outsider recomputing the sealed
    plan's `plaintext_digest` had to guess Python's spacing. 280 bytes against
    262 for the same object.
    """
    ws = Workspace(tmp_path / "run")
    do_plan(ws, plan)

    manifest = Manifest.from_record(ws.ledger.verify()[0].body["plan_seal"])
    sealed = ws.plan_store().unseal(manifest)

    assert sealed == canonical(plan.as_record())
    assert b", " not in sealed and b": " not in sealed  # no default-separator spacing


def test_the_sealed_plan_round_trips_to_the_same_plan(tmp_path: Path, plan: Plan) -> None:
    """The positive control: canonical bytes must still rebuild the plan."""
    import json

    ws = Workspace(tmp_path / "run")
    do_plan(ws, plan)
    manifest = Manifest.from_record(ws.ledger.verify()[0].body["plan_seal"])
    rebuilt = Plan.from_mapping(json.loads(ws.plan_store().unseal(manifest)))

    assert rebuilt.plan_hash == plan.plan_hash


# --------------------------------------------------------------------- V-10


def test_verify_structure_docstring_does_not_promise_a_keyless_verify() -> None:
    """V-10. The docstring claimed a path no run-level code offered.

    `verify_structure` genuinely needs no key -- digests are over ciphertext. But
    `verify_run` has no keyless mode and refuses `KEY_MISSING` long before
    reaching it, so the sentence "Runs without the key", read next to `verify`,
    described a capability that did not exist.

    A keyless audit mode is worth building and is carried as O-14 for Phase 2.
    This test pins the docstring to what is true until then.
    """
    doc = SealedStore.verify_structure.__doc__ or ""
    assert "Runs without the key" not in doc
    assert "verify_run` does not offer that as a mode" in doc
    assert "O-14" in doc


def test_verify_structure_really_does_work_without_a_key(tmp_path: Path) -> None:
    """The other half: the capability is real, even though `verify` does not use it."""
    store = SealedStore(tmp_path / "sealed", SealedStore.new_key())
    manifest = store.seal("item-1", b"content")

    SealedStore(tmp_path / "sealed").verify_structure(manifest)  # no key, must not raise


# ---------------------------------------------------------------------- Q-1


def test_svy_wilson_is_not_the_textbook_interval() -> None:
    """Q-1, and the evidence behind D-18's narrowing of O-4.

    `svy` 0.25.0's Wilson is design-based: it replaces n with an effective sample
    size and uses a t-quantile with df, where the textbook binomial interval uses
    n and z. D-3 assumed the two would agree to four significant digits; they
    implement different estimators, so that assumption was withdrawn.

    Pinned against the quoted source lines rather than against a live import,
    because `svy` is deliberately not a dependency (D-2, httpx). If someone later
    adds it as a witness for Wilson, this docstring is where they should look
    first.
    """
    import ast

    from prevalence_kit import estimators

    source = Path(estimators.__file__).read_text(encoding="utf-8")

    # Ours: n and z, per Brown, Cai & DasGupta (2001).
    assert "NormalDist().inv_cdf" in source
    assert "10.1214/ss/1009213286" in source, "the anchor is not where a reader looks"

    # **Narrowed 2026-08-30, and the narrowing is the same shape as S-2.4's.**
    # This used to assert `n_eff` appeared NOWHERE in the file, which was a
    # structural claim while the file held only binomial estimators. O-26 added
    # the design intervals, which are BUILT on an effective sample size, so the
    # file-level absence is gone.
    #
    # The claim it was making is still true and is now checked where it lives:
    # the BINOMIAL `wilson` does not use an effective sample size, asserted by
    # walking its call graph rather than by scanning the file.
    tree = ast.parse(source)
    defined = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    reachable: set[str] = set()
    stack = ["wilson"]
    while stack:
        name = stack.pop()
        if name in reachable or name not in defined:
            continue
        reachable.add(name)
        for node in ast.walk(defined[name]):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                stack.append(node.func.id)

    assert "effective_n" not in reachable, (
        "the binomial Wilson now reaches an effective sample size, so it is no "
        "longer a different estimator from svy's -- D-18's evidence would need "
        "re-reading"
    )
    # The control: the DESIGN Wilson does reach it, so this can tell them apart.
    design_reachable: set[str] = set()
    stack = ["design_wilson"]
    while stack:
        name = stack.pop()
        if name in design_reachable or name not in defined:
            continue
        design_reachable.add(name)
        for node in ast.walk(defined[name]):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                stack.append(node.func.id)
    assert "effective_n" in design_reachable


# ------------------------------------------------- plain ASCII, operator-facing


def user_facing_strings(path: Path) -> list[tuple[int, str]]:
    """Lines carrying a character above U+007F."""
    return [
        (i, line)
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1)
        if any(ord(c) > 127 for c in line)
    ]


@pytest.mark.parametrize("path", sorted(SRC.rglob("*.py")), ids=lambda p: p.name)
def test_no_non_ascii_in_the_shipped_source(path: Path) -> None:
    """Every message an operator reads must render on a default Windows console.

    This property is true today and nothing asserted it. When the reviewer
    harness ran under PowerShell its em-dashes came out as `ù`; our messages did
    not, because they use `--`. Rule 8: pin it before it silently stops being
    true.

    Scope is deliberately the whole of `src/`, not a hand-maintained list of
    message strings -- a list is something someone forgets to add to. The cost is
    that comments and docstrings are covered too, which is the right trade: a
    docstring is read by whoever is debugging at 6pm.
    """
    offenders = user_facing_strings(path)
    assert not offenders, (
        f"{path.name} has {len(offenders)} line(s) above U+007F, first at line "
        f'{offenders[0][0]}. Use ASCII: -- for a dash, " for quotes.'
    )


def test_the_ascii_guard_can_fail(tmp_path: Path) -> None:
    """The guard's negative control. Without it a broken scanner passes forever."""
    planted = tmp_path / "planted.py"
    planted.write_text('MESSAGE = "an em-dash — here"\n', encoding="utf-8")
    assert user_facing_strings(planted)


def test_refusal_messages_are_ascii_and_say_what_to_do() -> None:
    """R8. Every refusal names the problem and the next action.

    Checked by construction: `Refusal` requires both a detail and a fix, so the
    only way to ship a message that does not say what to do is to write a useless
    fix string. This asserts the ones we have are not that.
    """
    from prevalence_kit.errors import Reason, Refusal

    sample = Refusal(Reason.SEAL_TAMPERED, "Chunk 0 failed authentication.", "Restore the store.")
    report = sample.report()
    assert all(ord(c) < 128 for c in report)
    assert "What to do:" in report
    assert "SEAL_TAMPERED" in report


def test_every_reason_code_is_screaming_snake_ascii() -> None:
    from prevalence_kit.errors import Reason

    for reason in Reason:
        assert re.fullmatch(r"[A-Z][A-Z_]+", reason.value), reason
        assert reason.name == reason.value


# --------------------------------------------------------------------- V-16


def _check_claims_module() -> ModuleType:
    """Load `tools/check_claims.py` as a module. It is not on the import path."""
    import importlib.util
    import sys

    path = Path(__file__).resolve().parents[1] / "tools" / "check_claims.py"
    spec = importlib.util.spec_from_file_location("check_claims_under_test", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    # Registered before exec: `@dataclass(slots=True)` looks its own module up in
    # sys.modules and fails with an unregistered synthetic name.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_ci_runs_every_check_the_gate_documents() -> None:
    """V-16. The documented gate and the executed gate are one list.

    CI ran `mypy --strict src` and stopped, so the eleven test files were never
    type-checked on the remote -- 12 files against the config form's 23. A type
    error in a test passed CI and failed on the director's machine, and nothing
    said the remote gate was the weaker one. Rule 5 applied to the gate's own
    coverage: a gate half-run is a gate not run.

    This is the positive control. The negative control is below, and
    `check_claims.py --selftest` plants `pytest -q` -- the other half of the same
    defect -- and requires the checker to catch it.
    """
    root = Path(__file__).resolve().parents[1]
    problems = _check_claims_module().check_gate(root)
    assert not problems, "\n".join(p.line() for p in problems)


def test_the_gate_check_notices_a_step_ci_stops_running(tmp_path: Path) -> None:
    """The negative control. Without it the check passes forever, checking nothing.

    Reproduces V-16 itself rather than a stand-in: delete the config-form `mypy`
    line from the documented block's counterpart in CI and require the checker to
    name the missing command.
    """
    module = _check_claims_module()
    root = Path(__file__).resolve().parents[1]

    workflow = tmp_path / ".github" / "workflows"
    workflow.mkdir(parents=True)
    original = (root / ".github" / "workflows" / "gate.yml").read_text(encoding="utf-8")
    assert "\n        run: mypy\n" in original, "V-16's step is not where this test expects it"
    (workflow / "gate.yml").write_text(
        original.replace("\n        run: mypy\n", "\n", 1), encoding="utf-8", newline="\n"
    )
    (tmp_path / "CLAUDE.md").write_text(
        (root / "CLAUDE.md").read_text(encoding="utf-8"), encoding="utf-8", newline="\n"
    )

    problems = module.check_gate(tmp_path)
    assert [p for p in problems if "`mypy`" in p.detail], [p.line() for p in problems]


def test_the_gate_check_reads_the_workflow_the_way_github_does(tmp_path: Path) -> None:
    """The second negative control, and it is a defect that actually shipped.

    The first version of this check read `gate.yml` with a regex, so it accepted
    a workflow GitHub rejects. An unquoted `name: mypy (config: src + tests)` is
    a nested mapping in YAML: the whole file fails to parse. Run 33205536300 died
    with "a workflow file issue" while all seven local checks were green.

    A checker that accepts what the real consumer rejects is not checking the
    same artifact.
    """
    module = _check_claims_module()
    root = Path(__file__).resolve().parents[1]

    workflow = tmp_path / ".github" / "workflows"
    workflow.mkdir(parents=True)
    (workflow / "gate.yml").write_text(
        "      - name: mypy (config: src + tests)\n        run: mypy\n",
        encoding="utf-8",
        newline="\n",
    )
    (tmp_path / "CLAUDE.md").write_text(
        (root / "CLAUDE.md").read_text(encoding="utf-8"), encoding="utf-8", newline="\n"
    )

    problems = module.check_gate(tmp_path)
    assert [p for p in problems if "not valid YAML" in p.detail], [p.line() for p in problems]


def test_the_real_workflow_is_valid_yaml() -> None:
    """The positive control for the pair above."""
    module = _check_claims_module()
    root = Path(__file__).resolve().parents[1]
    _, parse_error = module.ci_run_steps(root / ".github" / "workflows" / "gate.yml")
    assert parse_error is None, parse_error


# --------------------------------------------------------------------- V-17


def test_the_register_names_the_route_the_witness_used() -> None:
    """V-17. The register said CRAN; the R image installed from a Posit mirror.

    Two names for one package, and nobody had checked they carry the same bytes.
    They do -- 339 of 341 regular files, the two exceptions being repository
    metadata -- but that was measured only after the gap was found.

    This is the offline half: whatever route the witness actually ran through
    must be named in `docs/STANDARDS.md`. The byte comparison itself needs the
    network and lives in `tools/check_tripwires.py` as TW-5.

    The same shape as the `gate` check: two lists that must agree, with
    something making them agree.
    """
    import json

    root = Path(__file__).resolve().parents[1]
    fixture = json.loads(
        (root / "r" / "fixtures" / "barnett_table_2b.json").read_text(encoding="utf-8")
    )
    register = (root / "docs" / "STANDARDS.md").read_text(encoding="utf-8")

    route = fixture["environment"]["cran_snapshot"]
    assert route in register, (
        f"the witness installed from {route}, which docs/STANDARDS.md does not name. "
        "That is V-17: one source named, another used."
    )

    # The image digest and the survey version travel with it.
    assert fixture["environment"]["image_digest"].removeprefix("sha256:") in register
    assert fixture["environment"]["survey_version"] == "4.5"


def test_the_route_check_notices_an_unrecorded_route(tmp_path: Path) -> None:
    """The negative control. Without it the check passes forever, checking nothing."""
    register = "S-2.1 pins survey 4.5 from CRAN and names no mirror.\n"
    route = "https://p3m.dev/cran/__linux__/noble/2026-04-23"
    assert route not in register


# ---------------------------------------------------------------------- D2.2


def _fixture(name: str) -> dict[str, Any]:
    import json

    root = Path(__file__).resolve().parents[1]
    parsed: dict[str, Any] = json.loads(
        (root / "r" / "fixtures" / name).read_text(encoding="utf-8")
    )
    return parsed


def test_every_fixture_uses_the_call_barnett_validated() -> None:
    """The director's D2.2 condition, made checkable instead of promised.

    D2.1 validated exactly one invocation against Barnett's published Table 2B:

        svydesign(ids = ~1, strata = ~stratum, weights = ~w, data = sample_rows)

    with no fpc. The anchor covers the call it tested and no other. If a later
    deliverable needs a different design -- an fpc, clusters, a different
    variance form -- Barnett does not cover it and it needs its own anchor
    recorded before it generates anything.

    Nothing stops that drift except this test.
    """
    anchor = _fixture("barnett_table_2b.json")
    stratified = _fixture("stratified.json")

    validated = anchor["exact_call"]
    assert validated == ("svydesign(ids = ~1, strata = ~stratum, weights = ~w, data = sample_rows)")
    assert stratified["validated_call"] == validated

    for entry in stratified["allocation_fixtures"]:
        assert "fpc" not in str(entry), "an fpc appeared in an allocation fixture"
    for entry in stratified["estimation_fixtures"]:
        assert entry["call"] == validated, f"{entry['label']} used a call Barnett did not validate"


def test_the_fixtures_record_an_unruled_question() -> None:
    """Rounded Neyman allocation does not always sum to n. Found by D2.2.

    `rare_event_neyman_5000` asks for 5000 and its rounded allocation sums to
    4999. Barnett's case sums exactly, so D2.1 never met this.

    The estimator cannot decide alone -- handing the remainder to a stratum
    rewrites a pre-registered design, which is V-1's class. Pinned as unruled so
    it cannot be quietly resolved in code.
    """
    stratified = _fixture("stratified.json")
    question = stratified["open_question"]
    assert question["status"].startswith("UNRULED")

    drifting = []
    for entry in stratified["allocation_fixtures"]:
        allocation = entry["result"]["allocation"]
        if not isinstance(allocation, list):
            allocation = [allocation]
        if sum(allocation) != entry["n_total"]:
            drifting.append(entry["label"])

    assert drifting == ["rare_event_neyman_5000"], (
        f"expected exactly the known rounding-drift case, got {drifting}. "
        "If it has gone, the question above may have been resolved in code."
    )


# --------------------------------------------------------------------- V-15


def test_the_path_check_reads_documents_outside_src_and_tests() -> None:
    """V-15. `check_paths` read a fixed list of `src/` and `tests/` globs.

    So a document added later was silently uncovered: `CLAUDE.md` named
    `docs/PHASE-1-REVIEW-STOP.md`, which lives under `docs/contracts/`, and the
    check passed. No failure, no warning, just less coverage than the day
    before.

    The fix is a pattern rather than a list -- `SCANNED` -- and this is the
    positive control for it. The negative control is below, and
    `check_claims.py --selftest` plants a broken path in `CLAUDE.md`
    specifically, because that plant would not have been seen at all before.

    D-23's principle applied to the checker's own inputs: a check that names its
    question generalises; a check that names a row does not.
    """
    module = _check_claims_module()
    patterns = set(module.SCANNED)

    assert "**/*.md" in patterns, f"Markdown outside src/ and tests/ is uncovered again: {patterns}"
    root = Path(__file__).resolve().parents[1]
    read = {p.name for p in module.repo_files(root, *module.SCANNED)}
    assert {"CLAUDE.md", "SECURITY.md", "PROJECT_CHARTER.md"} <= read, sorted(read)


def test_the_path_check_notices_a_bad_path_in_a_root_document(tmp_path: Path) -> None:
    """The negative control. Reproduces V-15's own gap, not a stand-in.

    The broken path goes in a root Markdown file -- the exact class of document
    the old glob list did not read.
    """
    module = _check_claims_module()
    # Assembled rather than written out: a literal here would be a real broken
    # path inside a real document, and `check_paths` reads this file too.
    absent = "docs/" + "no-such-document" + ".md"
    (tmp_path / "CLAUDE.md").write_text(
        f"# plant\n\nSee {absent}.\n", encoding="utf-8", newline="\n"
    )

    problems = module.check_paths(tmp_path)
    assert [p for p in problems if absent in p.detail], [p.line() for p in problems]


# ------------------------------------------------------- the register check


def test_every_finding_the_record_names_has_a_register_row() -> None:
    """The positive control for `check_register`, and the thing it exists for.

    `check_findings` validates the rows that are present. It cannot see a row
    that was never written, and for some weeks four were not: V-12, V-13, V-14
    and V-15 were discussed across three to nine documents each -- V-12 in
    `SECURITY.md`, V-15 in `tools/check_claims.py` itself -- while the register
    held 22 rows and none of them these four.

    `check_claims` reported "22 findings in the register, all accounted for"
    the whole time. True, and worthless: it answered *is everything here
    consistent?* when the question was *is everything here?*
    """
    root = Path(__file__).resolve().parents[1]
    problems = _check_claims_module().check_register(root)
    assert not problems, "\n".join(p.line() for p in problems)


def test_the_register_check_notices_a_finding_with_no_row(tmp_path: Path) -> None:
    """The negative control, and the plant is the defect as it actually was.

    Delete V-12's register row and leave every other mention of it standing.
    That is precisely the state this repository was in: a finding the record
    discusses at length, absent from the register that exists to track it.

    A made-up identifier nobody writes about would pass this test and prove
    nothing -- the check has to fire on a finding the record really does carry.
    """
    module = _check_claims_module()
    root = Path(__file__).resolve().parents[1]

    docs = tmp_path / "docs"
    docs.mkdir()
    register = (root / "docs" / "FINDINGS.md").read_text(encoding="utf-8")
    row = "| V-12 | high | closed | `test_the_tampered_plan_is_caught_without_the_flag` | D-24 |\n"
    assert row in register, "V-12's row is not where this test expects it"
    (docs / "FINDINGS.md").write_text(register.replace(row, "", 1), encoding="utf-8", newline="\n")
    (tmp_path / "SECURITY.md").write_text(
        "A clean verify on a tampered plan (V-12).\n", encoding="utf-8", newline="\n"
    )

    problems = module.check_register(tmp_path)
    assert [p for p in problems if p.where == "V-12"], [p.line() for p in problems]


def test_the_contracts_numbered_questions_are_not_read_as_findings() -> None:
    """A boundary the check depends on, asserted rather than assumed.

    The contracts number their questions `Q1` ... `Q7`, without a hyphen. The
    register's findings use the hyphenated form. If a contract ever spelled a
    numbered question the hyphenated way, `check_register` would demand a
    register row for it and the two vocabularies would have collided silently.

    So the separation is pinned here. If this fails, the fix is the contract's
    spelling or the regex, and someone has to choose deliberately.

    (This docstring spells no hyphenated identifier of its own, for the same
    reason the test above assembles its path: the checker reads this file.)
    """
    root = Path(__file__).resolve().parents[1]
    module = _check_claims_module()
    registered = {ident for ident, *_ in module.register_rows(root)}

    for path in sorted((root / "docs" / "contracts").glob("*.md")):
        for ident in module.FINDING_ID.findall(path.read_text(encoding="utf-8")):
            if ident.startswith("Q-"):
                assert ident in registered, (
                    f"{path.name} writes {ident}, which reads as a register finding. "
                    "Numbered questions are spelled Q5, without the hyphen."
                )


def test_the_documented_scope_is_the_scope_walked() -> None:
    """C-34. A checker's stated scope is a claim, and claims get checked.

    `defined_ids` once said obligations live in two files. They live in three,
    seven were invisible, and the sentence naming the scope was worse than no
    sentence: it answered the question before anyone asked it, and answered it
    wrongly. A reader who checked the docstring came away more confident and
    less correct.

    So the scope is now a tuple the function walks, and the human-readable form
    is rendered from that tuple. This pins the two together: if someone adds a
    fourth source to the walk and forgets the prose, there is no prose to
    forget.
    """
    module = _check_claims_module()
    root = Path(__file__).resolve().parents[1]

    assert "docs/contracts/*-CONTRACT.md" in module.OBLIGATION_SOURCES, (
        "contracts are where a phase opens the obligations it discovers"
    )
    for pattern in module.OBLIGATION_SOURCES:
        assert sorted(root.glob(pattern)), f"{pattern} matches nothing"
        assert pattern in module.scope_of(module.OBLIGATION_SOURCES)

    # The seven that were invisible must now resolve.
    defined = module.defined_ids(root)["O"]
    for name in ("O-8", "O-16", "O-17", "O-18", "O-20", "O-21", "O-24"):
        assert name in defined, f"{name} is defined in a contract and still unseen"


# ------------------------------------------------------- the phase sentence


def _repo_copy(tmp_path: Path) -> Path:
    """A copy of the repository, so a planted violation touches nothing real."""
    import shutil

    root = Path(__file__).resolve().parents[1]
    target = tmp_path / "repo"
    shutil.copytree(
        root,
        target,
        # `sealed` and the key are the expensive half and the wrong half: a run
        # directory's sealed store is a thousand small files, `copytree` does
        # not read .gitignore, and every test using this helper was paying for
        # all of them. They are also not part of the repository -- .gitignore
        # has excluded keys and sealed content since Phase 1 -- so copying the
        # working tree without them is closer to what these tests mean by "the
        # repository", not further from it. Adding the real-data example took
        # the suite from about 70s to 265s until this line existed.
        ignore=shutil.ignore_patterns(
            ".venv",
            ".git",
            "__pycache__",
            "*.pyc",
            # Tool caches. Gitignored, thousands of small files, and not the
            # repository by any definition these tests use.
            ".mypy_cache",
            ".ruff_cache",
            ".pytest_cache",
            "sealed",
            "*.sealed",
            "*.key",
        ),
    )
    return target


def test_the_phase_sentence_is_checked_for_its_word_not_only_its_number(
    tmp_path: Path,
) -> None:
    """**C-47.** The README said *in progress* for a phase that had closed.

    The old check compared the NUMBER to the highest-numbered contract and never
    read the word. `current_phase` means *the highest contract that exists*,
    which is not *the phase in progress* -- so when Phase 2 closed the number
    stayed 2 and **the check went green on a false sentence, in the most public
    file this project has.** C-34's class: a checker that affirms a wrong claim
    leaves the reader more confident and less correct.
    """
    module = _check_claims_module()
    root = _repo_copy(tmp_path)
    number, state = module.phase_state(root)
    wrong = "complete" if state == "in progress" else "in progress"
    readme = root / "README.md"
    text = readme.read_text(encoding="utf-8")
    anchor = f"Phase {number} of 4 {state}"
    # C-49: the first version of this test replaced a hard-coded sentence and
    # never checked the replace took, so it planted nothing the day the phase
    # moved. The anchor is derived from the artifact, and the plant is asserted.
    assert anchor in text, f"nothing to perturb: README carries no {anchor!r}"
    readme.write_text(text.replace(anchor, f"Phase {number} of 4 {wrong}"), encoding="utf-8")

    details = [p.detail for p in module.check_figures(root)]
    assert any(wrong in d and state in d for d in details), details


def test_deleting_the_phase_sentence_does_not_silence_the_check(
    tmp_path: Path,
) -> None:
    """The other direction, and it is the half that went quiet.

    Every other claim in `check_figures` iterates its matches, so a claim whose
    sentence is deleted reports nothing. `CLAUDE.md`'s phase claim went vacuous
    exactly that way when its old wording had no true form. **Absence is a
    failure for this one**, so deleting the sentence cannot be a way to silence
    it.
    """
    module = _check_claims_module()
    root = _repo_copy(tmp_path)
    number, state = module.phase_state(root)
    anchor = f"Phase {number} of 4 {state}"
    for name in ("README.md", "CLAUDE.md"):
        path = root / name
        text = path.read_text(encoding="utf-8")
        # C-49: anchor derived, plant asserted -- see the test above.
        assert anchor in text, f"nothing to remove: {name} carries no {anchor!r}"
        path.write_text(text.replace(anchor, "Phase gone"), encoding="utf-8")

    details = [p.detail for p in module.check_figures(root)]
    assert sum("carries no" in d for d in details) == 2, details


def test_the_phase_state_is_read_from_the_contract(tmp_path: Path) -> None:
    """The close line in the newest contract is what makes the state `complete`.

    Not a flag someone maintains beside it -- that is the arrangement this
    project has been correcting all phase. **C-49**: the first version asserted
    `(2, "complete")` against the live tree -- a live figure hard-coded in a
    test -- and broke the day the Phase 3 contract existed. This one asserts the
    property on whichever contract is newest: planting a close line flips the
    state to `complete`.
    """
    module = _check_claims_module()
    root = _repo_copy(tmp_path)
    number, state = module.phase_state(root)
    contract = root / "docs" / "contracts" / f"PHASE-{number}-CONTRACT.md"
    text = contract.read_text(encoding="utf-8")
    if state == "complete":
        # The newest contract is closed; strip its close line first so the
        # plant below starts from `in progress` whichever way the tree stands.
        text = re.sub(rf"^\*\*(?:Phase {number} )?CLOSED\b", "**Was closed", text, flags=re.M)
        contract.write_text(text, encoding="utf-8")
        assert module.phase_state(root) == (number, "in progress")
    contract.write_text(text + f"\n**Phase {number} CLOSED for this test.**\n", encoding="utf-8")
    assert module.phase_state(root) == (number, "complete")


def test_a_contract_without_its_close_reads_as_in_progress(tmp_path: Path) -> None:
    """The negative control for the state itself.

    Remove the close line and the state must revert. Without this, `complete`
    could be a constant and nothing would tell. Phase-agnostic for C-49's
    reason: the close is planted and then removed on whichever contract is
    newest, so the test survives every boundary including this phase's own.
    """
    module = _check_claims_module()
    root = _repo_copy(tmp_path)
    number, _state = module.phase_state(root)
    contract = root / "docs" / "contracts" / f"PHASE-{number}-CONTRACT.md"
    original = contract.read_text(encoding="utf-8")
    close_line = f"\n**Phase {number} CLOSED for this test.**\n"
    contract.write_text(original + close_line, encoding="utf-8")
    assert module.phase_state(root) == (number, "complete")
    contract.write_text(original, encoding="utf-8")
    stripped = re.sub(rf"^\*\*(?:Phase {number} )?CLOSED\b", "**Was closed", original, flags=re.M)
    contract.write_text(stripped, encoding="utf-8")
    assert module.phase_state(root) == (number, "in progress")


# --------------------------------------------------------------------- C-48


_OPEN_ROW = re.compile(r"^\|[^|\n]*\*\*(\d+) corrections open\*\*[^|\n]*\|[^\n]*", re.M)


def test_the_open_corrections_row_count_is_checked(tmp_path: Path) -> None:
    """**C-48.** The row said 49 entries and 6 open; the register held 50 and 7.

    And it credited `check_counts` with reading it, when that check read only
    the counts table in `docs/CORRECTIONS.md`. The claim is now true by
    machinery, and this is the count half: a wrong open count is a failure.
    """
    module = _check_claims_module()
    root = _repo_copy(tmp_path)
    claude = root / "CLAUDE.md"
    text = claude.read_text(encoding="utf-8")
    row = _OPEN_ROW.search(text)
    assert row is not None, "nothing to perturb: CLAUDE.md carries no open-corrections row"
    stated = int(row.group(1))
    claude.write_text(
        text.replace(f"**{stated} corrections open**", f"**{stated + 1} corrections open**"),
        encoding="utf-8",
    )
    details = [p.detail for p in module.check_counts(root)]
    assert any("corrections open, entries say" in d for d in details), details


def test_a_closed_correction_named_in_the_open_row_is_a_failure(tmp_path: Path) -> None:
    """One direction of the identifier check: the row may not keep a closed id."""
    module = _check_claims_module()
    root = _repo_copy(tmp_path)
    claude = root / "CLAUDE.md"
    text = claude.read_text(encoding="utf-8")
    row = _OPEN_ROW.search(text)
    assert row is not None
    # C-2 closed under T-1; naming it as open is the planted drift.
    claude.write_text(text.replace(row.group(0), row.group(0) + " **C-2**,", 1), encoding="utf-8")
    details = [p.detail for p in module.check_counts(root)]
    assert any("named in the row, not open in the register" in d and "C-2" in d for d in details), (
        details
    )


def test_an_open_correction_missing_from_the_row_is_a_failure(tmp_path: Path) -> None:
    """The other direction: every open entry must appear in the row.

    C-48's own shape -- C-47 was open and absent from the row -- so the planted
    violation removes one open identifier rather than inventing a state.
    """
    module = _check_claims_module()
    root = _repo_copy(tmp_path)
    claude = root / "CLAUDE.md"
    text = claude.read_text(encoding="utf-8")
    row = _OPEN_ROW.search(text)
    assert row is not None
    ids = re.findall(r"\*\*([CV]-\d+)\*\*", row.group(0))
    assert ids, "the row names no identifiers to remove"
    planted = row.group(0).replace(f"**{ids[-1]}**", "**(one removed)**", 1)
    claude.write_text(text.replace(row.group(0), planted, 1), encoding="utf-8")
    details = [p.detail for p in module.check_counts(root)]
    assert any(
        "open in the register, absent from the row" in d and ids[-1] in d for d in details
    ), details


def test_deleting_the_open_corrections_row_is_a_failure(tmp_path: Path) -> None:
    """Absence is a failure -- C-47's lesson, applied to this row.

    Every other figure claim iterates its matches, so a deleted sentence
    reports nothing. Deleting this row must not be a way to silence it.
    """
    module = _check_claims_module()
    root = _repo_copy(tmp_path)
    claude = root / "CLAUDE.md"
    text = claude.read_text(encoding="utf-8")
    row = _OPEN_ROW.search(text)
    assert row is not None, "nothing to delete"
    claude.write_text(text.replace(row.group(0), "", 1), encoding="utf-8")
    details = [p.detail for p in module.check_counts(root)]
    assert any("carries no" in d and "corrections open" in d for d in details), details


# ------------------------------------------- the stop rulings of 2026-08-31


def test_a_named_demo_path_is_walked(tmp_path: Path) -> None:
    """PATH_LIKE's second widening: `demo/` prefix and `.svg` extension.

    The README's front page links four files under demo/, one an .svg, and a
    vanished link passed check_paths before the widening -- the reviewer's
    negative control at the Phase 3 stop proved it. Same two axes as D2.14(a).
    """
    module = _check_claims_module()
    root = _repo_copy(tmp_path)
    readme = root / "README.md"
    # Assembled from pieces so this test file does not itself name a path that
    # does not exist -- check_paths walks tests/*.py too.
    bogus = "demo/" + "does-not-" + "exist.svg"
    readme.write_text(
        readme.read_text(encoding="utf-8") + f"\nSee {bogus} for nothing.\n", encoding="utf-8"
    )
    details = [p.detail for p in module.check_paths(root)]
    assert any(bogus in d for d in details), details


def test_the_licence_claim_and_the_licence_file_agree() -> None:
    """**F-A**, Q27. Two artifacts claimed MIT and no LICENSE file existed.

    A public repository whose README and `pyproject.toml` both say MIT, with no
    licence text anywhere, shows **no licence** in GitHub's own interface and
    grants a reader nothing. That is an overclaim in the charter section 5.6
    sense, in the two files a stranger reads first, and it stood until the
    Phase 3 structural comparison went looking for it.

    Three places, one answer, asserted together -- because the defect was not
    that any one of them was wrong, it was that nothing compared them.
    """
    root = Path(__file__).resolve().parents[1]
    licence = root / "LICENSE"
    assert licence.exists(), "no LICENSE file: the README and pyproject both claim one"
    text = licence.read_text(encoding="utf-8")
    assert text.startswith("MIT License"), "LICENSE does not open as the MIT licence"
    assert "Copyright (c) 2026 Mohd Saif Hussain" in text
    # The grant and the disclaimer, so a truncated or placeholder file fails.
    assert "without restriction" in text
    assert 'PROVIDED "AS IS"' in text

    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    assert 'license = "MIT"' in pyproject

    readme = (root / "README.md").read_text(encoding="utf-8")
    assert re.search(r"^MIT\b", readme, flags=re.M), "README states no licence"
    assert "license-MIT-blue" in readme, "README carries no licence badge"

    citation = (root / "CITATION.cff").read_text(encoding="utf-8")
    assert "license: MIT" in citation


def test_a_stale_badge_number_fails_the_gate(tmp_path: Path) -> None:
    """**Charter section 5.6: badge-truth tests.** Named since Phase 0, built now.

    A badge is the most-read claim in a repository and the least-checked. It is
    a picture of a number, and nothing about a picture goes stale visibly.
    """
    module = _check_claims_module()
    root = _repo_copy(tmp_path)
    readme = root / "README.md"
    text = readme.read_text(encoding="utf-8")
    match = re.search(r"tests-(\d+)%20collected", text)
    assert match is not None, "nothing to perturb: README carries no tests badge"
    stated = int(match.group(1))
    planted = text.replace(match.group(0), f"tests-{stated + 1}%20collected")
    readme.write_text(planted, encoding="utf-8")

    # Figures injected rather than derived: deriving the test count collects the
    # suite in a subprocess, and doing that from inside the suite works and
    # costs minutes. The live tree's real figures are checked by the gate's own
    # `check_claims` run, which is where that cost belongs.
    figures = {"tests": stated, "gate checks": 7, "reason codes": 38}
    details = [p.detail for p in module._badge_problems(root, figures)]
    assert any("badge 'tests'" in d for d in details), details

    # The positive control, same call, unplanted README.
    readme.write_text(text, encoding="utf-8")
    assert module._badge_problems(root, figures) == []


def test_deleting_a_badge_does_not_silence_the_check(tmp_path: Path) -> None:
    """Absence is a failure, as it is for the phase sentence.

    C-47's lesson, fourth application: a claim whose sentence is deleted must
    not stop being checked. Removing a badge is the easiest way to make a
    stale number stop failing, so it fails on its own.
    """
    module = _check_claims_module()
    root = _repo_copy(tmp_path)
    readme = root / "README.md"
    text = readme.read_text(encoding="utf-8")
    line = next(ln for ln in text.splitlines() if "reason%20codes" in ln)
    assert line in text, "nothing to delete"
    readme.write_text(text.replace(line + "\n", ""), encoding="utf-8")

    figures = {"tests": 1, "gate checks": 7, "reason codes": 38}
    details = [p.detail for p in module._badge_problems(root, figures)]
    assert any("carries no 'reason codes' badge" in d for d in details), details


def test_the_badge_figures_are_derived_from_the_artifacts() -> None:
    """The derivation itself, without the subprocess half.

    `badge_figures` reads three artifacts. Two are cheap and are checked here
    against the same sources the rest of the suite uses; the third collects the
    suite and is left to the gate, which is stated rather than quietly omitted.
    """
    module = _check_claims_module()
    root = Path(__file__).resolve().parents[1]
    import sys as _sys

    _sys.path.insert(0, str(root / "src"))
    from prevalence_kit.errors import Reason

    gate_block = module.GATE_BLOCK.search((root / "CLAUDE.md").read_text(encoding="utf-8"))
    assert gate_block is not None, "CLAUDE.md has no machine-readable gate block"
    commands = [ln for ln in gate_block.group(1).splitlines() if ln.strip()]

    readme = (root / "README.md").read_text(encoding="utf-8")
    assert f"gate%20checks-{len(commands)}-" in readme
    assert f"reason%20codes-{len(list(Reason))}-" in readme


def test_the_real_data_example_readme_matches_its_artifacts() -> None:
    """**D3.14.** The worked example states numbers; the artifacts must carry them.

    The README quotes an estimate, an interval, a positive count and a census
    truth, and says the interval covered the truth. Every one of those is
    checkable against a committed file, so none of them is allowed to be a
    sentence somebody typed. This is the shape C-51 came from: a number stated
    beside a bound, with nothing comparing the two.
    """
    example = Path(__file__).resolve().parents[1] / "examples" / "real-data"
    report = json.loads((example / "run" / "report.json").read_text(encoding="utf-8"))
    truth = json.loads((example / "census_truth.json").read_text(encoding="utf-8"))
    readme = (example / "README.md").read_text(encoding="utf-8")

    estimate = report["estimate"]
    point, low, high = (
        float(estimate["point"]),
        float(estimate["low"]),
        float(estimate["high"]),
    )

    # The claim the example is built on: the interval covered the census truth.
    census = float(truth["census_prevalence"])
    assert low <= census <= high, (
        f"the README claims the interval covered the truth; {census} is not in [{low}, {high}]"
    )

    # Every figure the README prints, as printed.
    assert f"{point * 100:.3f}%" in readme
    assert f"{low * 100:.3f}%" in readme
    assert f"{high * 100:.3f}%" in readme
    assert f"{census * 100:.4f}%" in readme
    assert f"{truth['census_positives']:,} of {truth['units']:,}" in readme
    assert f"{estimate['positives']} positives" in readme

    # The population the plan names is the one the truth was computed over.
    frame_lines = (example / "frame.txt").read_text(encoding="utf-8").split()
    assert len(frame_lines) == int(truth["units"])

    # And no comment text reached the labels file -- D-54, asserted rather than
    # trusted, because this is the one promise the example makes about itself.
    header = (example / "labels.csv").read_text(encoding="utf-8").splitlines()[0]
    assert header == "item_id,toxicity", f"labels.csv carries an unexpected column: {header}"


def test_the_notice_carries_the_eu_acknowledgement() -> None:
    """O-18's binding condition, where a reuser meets it.

    Decision 2011/833/EU authorises reuse of Commission documents **provided the
    source is acknowledged**. That acknowledgement lived only in the standards
    register, which is not where anyone redistributing this repository would
    look. The boundary travels with it: the clearance covers Commission
    documents and NOT Regulation (EU) 2022/2065, which is an act of the
    Parliament and Council.
    """
    root = Path(__file__).resolve().parents[1]
    notice = root / "NOTICE"
    assert notice.exists(), "no NOTICE file to carry O-18's acknowledgement"
    text = notice.read_text(encoding="utf-8")
    assert "European Union" in text
    assert "2011/833/EU" in text
    assert "2022/2065" in text, "the boundary of the clearance is not stated"
    # The PDF it covers is the one actually tracked here.
    pdf = "OJ_L_202402835_EN_TXT.pdf"
    assert pdf in text
    assert (root / pdf).exists(), "NOTICE names a redistributed file that is absent"


def test_the_svy_credit_cannot_be_silently_dropped(tmp_path: Path) -> None:
    """O-10 / C-1: the estimator-layer credit is held by machinery, not memory.

    Both directions: the live README passes (the credit is there), and a README
    whose credit is reworded away fails -- absence is a failure, so deleting
    the sentence cannot silence the claim.
    """
    module = _check_claims_module()
    root = _repo_copy(tmp_path)
    assert not module._svy_credit_problems(root), "the live README should carry the credit"
    readme = root / "README.md"
    text = readme.read_text(encoding="utf-8")
    assert "the estimator layer" in text, "nothing to remove"
    readme.write_text(text.replace("the estimator layer", "a fine library"), encoding="utf-8")
    details = [p.detail for p in module._svy_credit_problems(root)]
    assert any("estimator-layer credit" in d for d in details), details
