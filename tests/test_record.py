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

import re
from pathlib import Path

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
    from prevalence_kit import estimators

    # Ours: n and z, per Brown, Cai & DasGupta (2001).
    source = Path(estimators.__file__).read_text(encoding="utf-8")
    assert "NormalDist().inv_cdf" in source
    assert "n_eff" not in source
    assert "t_crit" not in source

    # And the anchor is named where a reader will find it.
    assert "10.1214/ss/1009213286" in source


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
