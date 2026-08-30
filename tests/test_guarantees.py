"""The two structural guarantees, proven rather than asserted in prose.

Hard Rule 1: zero network calls at runtime.
Hard Rule 2: no AI in the evidence path.

Both are claims about what the code *cannot* do, so both are checked against the
code and the dependency tree, not against behaviour at runtime. A test that only
watches a happy path go by would pass on the day someone adds an HTTP client.

Exit check E13 exercises the first one's ability to fail: add `httpx` to the
declared dependencies and `test_declared_dependencies_are_offline` must go red.
"""

from __future__ import annotations

import ast
import tomllib
from importlib.metadata import PackageNotFoundError, distribution
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "prevalence_kit"

NETWORK_MODULES = frozenset(
    {
        # stdlib
        "socket",
        "socketserver",
        "ssl",
        "http",
        "urllib",
        "ftplib",
        "smtplib",
        "imaplib",
        "poplib",
        "telnetlib",
        "nntplib",
        "xmlrpc",
        "webbrowser",
        "wsgiref",
        "ipaddress",
        # common clients
        "requests",
        "httpx",
        "httpcore",
        "urllib3",
        "aiohttp",
        "websockets",
        "grpc",
        "boto3",
        "botocore",
        "paramiko",
        "pycurl",
    }
)

AI_MODULES = frozenset(
    {
        "anthropic",
        "openai",
        "cohere",
        "mistralai",
        "google",
        "vertexai",
        "transformers",
        "torch",
        "tensorflow",
        "sentence_transformers",
        "langchain",
        "llama_index",
        "litellm",
        "ollama",
        "replicate",
    }
)

EVIDENCE_PATH = (
    "plan.py",
    "sampling.py",
    "seal.py",
    "ledger.py",
    "estimators.py",
    "run.py",
    "verify.py",
    # Phase 2. It decides how many units each stratum gets and computes the
    # stratified estimate, so it is as much evidence path as estimators.py.
    # This line exists because the guard refused to let the module through
    # unclassified, which is the guard doing its job rather than a formality.
    "stratified.py",
)


def imports_of(path: Path) -> set[str]:
    """Top-level module names imported by one file."""
    found: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"), filename=str(path))):
        if isinstance(node, ast.Import):
            found |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            found.add(node.module.split(".")[0])
    return found


def declared_dependencies() -> list[str]:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return list(data["project"]["dependencies"])


def transitive_requirements(
    name: str, seen: set[str] | None = None, unresolved: set[str] | None = None
) -> tuple[set[str], set[str]]:
    """Every distribution `name` drags in, as installed, plus what could not be resolved.

    The second return value matters as much as the first. A package that is not
    installed cannot be walked, so its own dependencies are invisible here -- and
    an invisible dependency must read as "not checked", never as "clean". The
    caller decides what to do about that; this function refuses to hide it.
    """
    seen = seen if seen is not None else set()
    unresolved = unresolved if unresolved is not None else set()
    key = name.lower().replace("_", "-")
    if key in seen:
        return seen, unresolved
    seen.add(key)
    try:
        requires = distribution(key).requires or []
    except PackageNotFoundError:
        unresolved.add(key)
        return seen, unresolved
    for spec in requires:
        if "extra ==" in spec:  # optional; not part of the runtime tree
            continue
        dep = spec.split(";")[0].split("[")[0].strip()
        for stop in ("==", ">=", "<=", "~=", "!=", ">", "<", " ", "("):
            dep = dep.split(stop)[0]
        if dep:
            transitive_requirements(dep, seen, unresolved)
    return seen, unresolved


def offline_violations(specs: list[str]) -> tuple[list[str], list[str]]:
    """(network-capable packages found, declared packages that could not be walked).

    One code path, used by both the real check and its negative control, so the
    control proves the thing the real check actually runs.
    """
    tree: set[str] = set()
    unresolved: set[str] = set()
    for spec in specs:
        name = spec.split("==")[0].split(">=")[0].split("[")[0].strip()
        found, missing = transitive_requirements(name)
        tree |= found
        unresolved |= missing
    network_names = {m.replace("_", "-") for m in NETWORK_MODULES}
    return sorted(tree & network_names), sorted(unresolved)


# ------------------------------------------------------------- zero network


@pytest.mark.parametrize("path", sorted(SRC.rglob("*.py")), ids=lambda p: p.name)
def test_no_runtime_module_imports_a_network_module(path: Path) -> None:
    offenders = imports_of(path) & NETWORK_MODULES
    assert not offenders, f"{path.name} imports {sorted(offenders)}"


def test_declared_dependencies_are_offline() -> None:
    """Exit check E13.

    To prove this guard can fail: add `httpx` to [project].dependencies and run
    this test. It must go red. A guard that has only ever passed is a decoration.

    This is why `svy` is not a dependency -- it requires httpx. docs/DECISIONS.md D-2.
    """
    offenders, unresolved = offline_violations(declared_dependencies())
    assert not offenders, (
        f"Network-capable packages reached the runtime dependency tree: {offenders}. "
        "Hard Rule 1 says zero network calls at runtime, and this is how that is proven."
    )
    assert not unresolved, (
        f"These declared dependencies are not installed, so their own dependencies "
        f"could not be inspected: {unresolved}. An unchecked subtree is not a clean "
        "subtree. Install the runtime dependencies before trusting this test."
    )


def test_the_network_guard_can_fail() -> None:
    """The guard's own negative control, through the real code path.

    E13 asks the director to add httpx to pyproject.toml by hand. This proves the
    same property in CI without editing the file: feed `offline_violations` the
    real dependency list plus httpx, and confirm it objects. A guard that has only
    ever passed is a decoration.
    """
    offenders, _ = offline_violations([*declared_dependencies(), "httpx"])
    assert "httpx" in offenders


def test_the_network_guard_reports_what_it_could_not_check() -> None:
    """The second half of the guard, which is easy to forget it has.

    A package that is not installed hides its own dependencies. The checker must
    say so rather than return a short list that looks clean.
    """
    _, unresolved = offline_violations(["definitely-not-a-real-package-9f3a"])
    assert unresolved == ["definitely-not-a-real-package-9f3a"]


def test_transitive_resolution_actually_walks() -> None:
    """Proves the walk is real, not a one-level lookup.

    cryptography requires cffi, which requires pycparser. If the recursion broke,
    every other assertion in this file would still pass while checking nothing.
    """
    tree, _ = transitive_requirements("cryptography")
    assert {"cryptography", "cffi", "pycparser"} <= tree


# ------------------------------------------------------------- no AI in path


@pytest.mark.parametrize("name", EVIDENCE_PATH)
def test_no_ai_module_reaches_the_evidence_path(name: str) -> None:
    """Labels come from humans. Estimates come from deterministic math."""
    offenders = imports_of(SRC / name) & AI_MODULES
    assert not offenders, f"{name} imports {sorted(offenders)}"


def test_evidence_path_files_all_exist() -> None:
    """Guards the guard: a renamed module must not silently drop out of the check."""
    missing = [n for n in EVIDENCE_PATH if not (SRC / n).exists()]
    assert not missing, f"EVIDENCE_PATH names files that no longer exist: {missing}"


def test_evidence_path_covers_every_runtime_module() -> None:
    """And the other direction: a new module must be classified, not ignored."""
    surface = {
        "__init__.py",
        "errors.py",
        "canonical.py",
        "cli.py",
        "report.py",
        # O-25. Measured coverage figures and the block the report renders from
        # them. **Surface, and the classification is the honest one rather than
        # the cautious one**: it touches no label and computes no estimate, so
        # putting it in the evidence path would widen what "evidence path" means
        # in order to look careful. The AI guard therefore does not cover it,
        # which is said here rather than left for someone to discover.
        "coverage.py",
    }
    unclassified = {p.name for p in SRC.glob("*.py")} - set(EVIDENCE_PATH) - surface
    assert not unclassified, (
        f"New runtime modules are in neither the evidence path nor the surface list: "
        f"{sorted(unclassified)}. Classify them so the AI guard keeps covering everything."
    )


def test_the_network_guard_stops_at_runtime_dependencies() -> None:
    """What the guard does NOT look at, asserted so its silence cannot mislead.

    Ruled 2026-08-29, when `defusedxml` went into dev extras. The guard walks
    `[project.dependencies]` and skips any requirement marked `extra == ...`. So
    it reads the shipped package's tree and nothing else.

    That is correct -- Hard Rule 1 is about what an operator installs, and dev
    tools that reach the network are the whole point of `tools/`. But it means
    adding a dev dependency draws no objection from this guard, and **"the guard
    did not object" must never be read as "the guard looked."**

    The scope is asserted rather than described, because a description drifts.
    """
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    # The guard's own input is the runtime list, not the extras.
    assert declared_dependencies() == data["project"]["dependencies"]
    dev = data["project"]["optional-dependencies"]["dev"]
    assert any(spec.startswith("defusedxml") for spec in dev), (
        "defusedxml belongs in dev extras. If it moved to runtime dependencies, "
        "this test is the wrong place to find that out -- but find it out here."
    )
    assert not any(spec.startswith("defusedxml") for spec in declared_dependencies())

    # And nothing in dev extras is walked, so none of it can be vouched for here.
    walked, _ = transitive_requirements("defusedxml")
    assert "defusedxml" in walked, "sanity: the walker can see it when asked directly"
    runtime_walk: set[str] = set()
    for spec in declared_dependencies():
        seen, _ = transitive_requirements(spec.split(";")[0].split("[")[0].strip())
        runtime_walk |= seen
    assert "defusedxml" not in runtime_walk, (
        "defusedxml appeared in the runtime tree. It is a dev tool and must not ship."
    )
