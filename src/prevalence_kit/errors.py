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
    PLAN_FILE_MISSING = "PLAN_FILE_MISSING"
    PLAN_SEAL_MISSING = "PLAN_SEAL_MISSING"
    PLAN_INVALID = "PLAN_INVALID"
    LEDGER_BROKEN = "LEDGER_BROKEN"
    SEAL_TAMPERED = "SEAL_TAMPERED"
    SEAL_TRUNCATED = "SEAL_TRUNCATED"
    SEAL_REORDERED = "SEAL_REORDERED"
    SEAL_MANIFEST_MISMATCH = "SEAL_MANIFEST_MISMATCH"
    SEED_MISSING = "SEED_MISSING"
    PLAN_THRESHOLD_INVALID = "PLAN_THRESHOLD_INVALID"
    LABEL_NOT_NUMERIC = "LABEL_NOT_NUMERIC"
    FRAME_EMPTY = "FRAME_EMPTY"
    FRAME_TOO_SMALL = "FRAME_TOO_SMALL"
    CONTENT_TOO_LARGE = "CONTENT_TOO_LARGE"
    KEY_MISSING = "KEY_MISSING"
    RUN_ALREADY_OPEN = "RUN_ALREADY_OPEN"
    RUN_NOT_FOUND = "RUN_NOT_FOUND"
    RUN_NOT_LINEAR = "RUN_NOT_LINEAR"
    SEAL_ALREADY_WRITTEN = "SEAL_ALREADY_WRITTEN"
    SEAL_ID_COLLISION = "SEAL_ID_COLLISION"
    ESTIMATE_MISMATCH = "ESTIMATE_MISMATCH"
    LABELS_UNMATCHED = "LABELS_UNMATCHED"
    EMPTY_SAMPLE = "EMPTY_SAMPLE"

    # Phase 2, stratified designs. Contract section 6.
    # D-22 decides how many codes: count the artifacts an operator must open,
    # not the situations. STRATUM_UNSAMPLED and STRATUM_EMPTY are separate
    # because they send the operator to different files -- the sample, and the
    # frame.
    STRATA_UNDEFINED = "STRATA_UNDEFINED"
    STRATUM_EMPTY = "STRATUM_EMPTY"
    STRATUM_UNSAMPLED = "STRATUM_UNSAMPLED"
    ALLOCATION_IMPOSSIBLE = "ALLOCATION_IMPOSSIBLE"
    ALLOCATION_TOO_THIN = "ALLOCATION_TOO_THIN"
    ALLOCATION_ROUNDING_UNDECLARED = "ALLOCATION_ROUNDING_UNDECLARED"

    # Q14 / D-40. A frame unit whose stratum the plan does not declare. S-1.13
    # makes strata mutually exclusive and covering, so this cannot be ignored:
    # dropping those units would change the denominator silently, which is
    # V-7's class in the one number this tool exists to produce.
    #
    # A .txt frame under `design: stratified` lands here too. It carries no
    # stratum column, so every unit is undeclared -- same artifact to open, same
    # remedial act, and the direction travels in the detail text. That is
    # PLAN_THRESHOLD_INVALID's precedent under D-22, on its second outing.
    STRATUM_UNDECLARED = "STRATUM_UNDECLARED"

    # F-10's durable half. `estimate.json` records the method that produced the
    # number; the hashed plan records the method the operator pre-registered.
    # Nothing compared them, so `interval` sat inert for a commit while `verify`
    # reported the estimate reproduced -- because it recomputed through the same
    # function that ignored the field.
    #
    # This code does NOT depend on the dispatch being right. That is the point:
    # dispatch makes the two agree today, and this catches the next field that
    # goes inert the same way.
    ESTIMATE_METHOD_MISMATCH = "ESTIMATE_METHOD_MISMATCH"

    # The stratified path draws but does not yet estimate: `stratified_estimate`
    # returns a standard error and no interval, and building one is O-26 under
    # Q7 -- the plan names the method. Until it exists this refuses BY NAME
    # rather than letting `_estimate_from` answer a stratified draw with SRS
    # Wilson, which would be a number that looks fine and is not the design.
    DESIGN_NOT_ESTIMABLE = "DESIGN_NOT_ESTIMABLE"

    # Rogan-Gladen. Two codes, not three: CORRECTION_DEGENERATE was struck
    # 2026-08-29 because AP = 0 or 1 is either already out of range or perfectly
    # well defined, and the contract's description of it was wrong.
    #
    # D-22 separates these two by the artifact the operator must open.
    # UNDEFINED sends them to the Se/Sp pair -- two numbers that are internally
    # impossible. OUT_OF_RANGE sends them to the relationship between the plan
    # and the sample, each of which looks fine alone.
    CORRECTION_UNDEFINED = "CORRECTION_UNDEFINED"
    CORRECTION_OUT_OF_RANGE = "CORRECTION_OUT_OF_RANGE"
    CORRECTION_INTERVAL_UNSUPPORTED = "CORRECTION_INTERVAL_UNSUPPORTED"


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
