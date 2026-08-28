"""Refusals.

Every refusal carries a distinct reason code. A gate that refuses everything for
one undifferentiated reason proves nothing, so the code -- not the message -- is
the contract, and the tests assert on it.

Contract: docs/contracts/PHASE-1-CONTRACT.md section 4.
"""

from __future__ import annotations

from enum import StrEnum


class Reason(StrEnum):
    """Why the tool refused. Stable identifiers; message text may be reworded."""

    PLAN_HASH_MISMATCH = "PLAN_HASH_MISMATCH"
    PLAN_MISSING = "PLAN_MISSING"
    PLAN_INVALID = "PLAN_INVALID"
    LEDGER_BROKEN = "LEDGER_BROKEN"
    SEAL_TAMPERED = "SEAL_TAMPERED"
    SEAL_TRUNCATED = "SEAL_TRUNCATED"
    SEAL_REORDERED = "SEAL_REORDERED"
    SEAL_MANIFEST_MISMATCH = "SEAL_MANIFEST_MISMATCH"
    SEED_MISSING = "SEED_MISSING"
    ESTIMATE_MISMATCH = "ESTIMATE_MISMATCH"
    LABELS_UNMATCHED = "LABELS_UNMATCHED"
    EMPTY_SAMPLE = "EMPTY_SAMPLE"


class Refusal(Exception):
    """The tool declined to produce a number it could not defend.

    Never raised for programmer error -- that is what the ordinary exceptions are
    for. A Refusal means the *evidence* failed a check, and the operator needs to
    know which one.
    """

    def __init__(self, reason: Reason, detail: str, fix: str) -> None:
        self.reason = reason
        self.detail = detail
        self.fix = fix
        super().__init__(f"{reason}: {detail}")

    def report(self) -> str:
        """Operator-facing text. Plain English, and it says what to do next."""
        return f"REFUSED [{self.reason}]\n  {self.detail}\n  What to do: {self.fix}"
