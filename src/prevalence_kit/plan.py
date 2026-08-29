"""The measurement plan, and its pre-registration hash.

The plan says what is being measured, over what population, by what design, from
what labels, under what seed. It is hashed *before any data file is opened*, and
that hash is the first link in the ledger chain.

That ordering is the whole point. A plan hashed after the data is seen is a
description; a plan hashed before is a commitment. Requirement R1, proven by
tests/test_core.py::test_hash_does_not_need_the_data.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Self

import yaml

from .canonical import JSONObject, digest
from .errors import Reason, Refusal

REQUIRED = (
    "estimand",
    "population",
    "design",
    "sample_size",
    "labels",
    "seed",
    "interval",
)
"""Every key a plan must carry.

`interval` joined this list under **Q11 / D-37**. It is required, with no
default, because the two intervals differ in what they guarantee and the
difference is large in the regime this tool is for. A default would be this
project choosing for an operator who did not know there was a choice.
"""

SUPPORTED_DESIGNS = frozenset({"srs", "stratified"})
SUPPORTED_COMPARISONS = frozenset({"equals", "at_least"})
SUPPORTED_INTERVALS = frozenset({"wilson", "clopper_pearson"})
SUPPORTED_ROUNDING = frozenset({"largest_remainder"})
"""Mirrors `stratified.Rounding`, asserted equal by
`test_the_plan_vocabulary_matches_the_rounding_enum`. Two lists that must
agree get something making them agree -- D-28.
"""


def _as_number(text: str) -> float | None:
    """The number this text denotes, or None if it does not denote one."""
    try:
        return float(text)
    except ValueError:
        return None


@dataclass(frozen=True, slots=True)
class Estimand:
    """What exactly is being measured.

    `threshold` exists because real label sets are often continuous -- a fraction
    of annotators, not a verdict. Fixing it here, before the data, is what makes a
    "true value" well defined at all. docs/DECISIONS.md D-11.
    """

    description: str
    label_field: str
    positive_when: str  # "equals" | "at_least"; validated at load
    threshold: str  # decimal string; see canonical.py on why not a float

    def is_positive(self, raw: str) -> bool:
        """Is this label value positive under the pre-registered estimand?

        `equals` is **exact string identity** after stripping surrounding
        whitespace, and it exists for categorical labels ("violating",
        "not_violating"). A numeric threshold under `equals` is refused at load,
        because it is a trap: threshold `1` against a label of `1.0` would count
        as negative and the tool would print a wrong number with no refusal. V-8.

        `at_least` is numeric, and a label that is not a number is a refusal, not
        a traceback. Real label columns contain "unclear", "n/a" and blanks. F-1.
        """
        if self.positive_when == "equals":
            return raw.strip() == self.threshold
        try:
            return float(raw) >= float(self.threshold)
        except ValueError as exc:
            raise Refusal(
                Reason.LABEL_NOT_NUMERIC,
                f"Label value {raw.strip()!r} is not a number, and the estimand compares "
                f"numerically (`positive_when: at_least`).",
                "Either clean the label column, or use `positive_when: equals` with a "
                "categorical threshold.",
            ) from exc


@dataclass(frozen=True, slots=True)
class Plan:
    """A pre-registered measurement plan. Immutable by construction."""

    estimand: Estimand
    population: str
    design: str
    sample_size: int
    labels: str
    seed: str
    interval: str
    """`wilson` or `clopper_pearson`. Required, no default. Q11 / D-37."""
    allocation_rounding: str | None = None
    """Required under `design: stratified`, absent otherwise. Q4 / D-30
    condition 1: the rounding rule is a commitment the operator makes, so it
    cannot be defaulted or live as a constant in the source."""
    source_path: Path | None = None

    @classmethod
    def load(cls, path: Path) -> Self:
        """Read and validate a plan. Opens the plan only -- never the data."""
        if not path.exists():
            raise Refusal(
                Reason.PLAN_FILE_MISSING,
                f"No plan file at {path}.",
                "This is a Python API guard. Every CLI verb declares its plan "
                "argument as click.Path(exists=True), so Click refuses a missing "
                "path before this runs. Check the path passed to Plan.load().",
            )
        try:
            raw: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise Refusal(
                Reason.PLAN_INVALID, f"{path} is not valid YAML: {exc}", "Fix the YAML."
            ) from exc
        return cls.from_mapping(raw, source_path=path)

    @classmethod
    def from_mapping(cls, raw: Any, *, source_path: Path | None = None) -> Self:
        if not isinstance(raw, dict):
            raise Refusal(Reason.PLAN_INVALID, "A plan must be a YAML mapping.", "See examples/.")

        if missing := [k for k in REQUIRED if k not in raw]:
            raise Refusal(
                Reason.PLAN_INVALID,
                f"Plan is missing: {', '.join(missing)}.",
                "Add the missing keys. Every plan needs all five.",
            )

        # Seed is checked by its own code so a missing seed never hides inside a
        # generic schema error -- an unseeded sample cannot be redrawn by anyone.
        seed = raw["seed"]
        if seed is None or str(seed).strip() == "":
            raise Refusal(
                Reason.SEED_MISSING,
                "The plan has no seed, so nobody could redraw this sample.",
                "Set `seed:` to any fixed string. Record it and never change it.",
            )

        interval = str(raw["interval"]).strip().lower()
        if interval not in SUPPORTED_INTERVALS:
            raise Refusal(
                Reason.PLAN_INVALID,
                f"Interval {interval!r} is not one this tool computes.",
                f"Use one of: {', '.join(sorted(SUPPORTED_INTERVALS))}.",
            )

        design = str(raw["design"]).strip().lower()
        if design not in SUPPORTED_DESIGNS:
            raise Refusal(
                Reason.PLAN_INVALID,
                f"Design {design!r} is not supported in this version.",
                f"Use one of: {', '.join(sorted(SUPPORTED_DESIGNS))}.",
            )

        # Q4 / D-30 condition 1. Only stratified plans allocate, so only they
        # commit to a rounding rule -- requiring it of an SRS plan would be
        # asking the operator to pre-register a decision the run never makes.
        rounding = raw.get("allocation_rounding")
        if design == "stratified":
            if rounding is None or str(rounding).strip() == "":
                raise Refusal(
                    Reason.ALLOCATION_ROUNDING_UNDECLARED,
                    "This plan uses design: stratified but does not say how a "
                    "fractional allocation becomes whole units. Neyman allocation "
                    "rarely lands on integers, and the rule that rounds it changes "
                    "which units get sampled.",
                    "Add `allocation_rounding: largest_remainder`. That is the only "
                    "rule this version implements, and naming it in the plan is what "
                    "keeps the allocation derived rather than chosen after the fact.",
                )
            rounding = str(rounding).strip().lower()
            if rounding not in SUPPORTED_ROUNDING:
                raise Refusal(
                    Reason.PLAN_INVALID,
                    f"Rounding rule {rounding!r} is not one this tool implements.",
                    f"Use one of: {', '.join(sorted(SUPPORTED_ROUNDING))}.",
                )
            # A stratified plan is loadable and its allocation commitment is
            # checked above -- but `do_sample` still calls `draw_srs`. Letting it
            # through would draw a SIMPLE RANDOM SAMPLE from a plan that says
            # stratified, which is a silently wrong number: the exact thing this
            # tool exists to refuse.
            #
            # `STRATA_UNDEFINED` is the honest code and the contract already
            # documents it as "design: stratified with no strata definition".
            # That is literally true today -- the schema has no strata field yet,
            # because it is the rest of D2.8.
            if "strata" not in raw:
                raise Refusal(
                    Reason.STRATA_UNDEFINED,
                    "This plan uses design: stratified but defines no strata, and "
                    "this version has no field for them yet. Sampling would fall "
                    "back to a simple random draw, which is not the design you "
                    "pre-registered and would give you a number your plan does "
                    "not describe.",
                    "Use `design: srs` for now. Stratified sampling is built and "
                    "checked against R `survey` (D2.3) but is not yet wired to "
                    "the plan; until it is, the tool refuses rather than draw the "
                    "wrong design.",
                )
        elif rounding is not None:
            raise Refusal(
                Reason.PLAN_INVALID,
                f"This plan sets allocation_rounding but its design is {design!r}, "
                "which never allocates across strata, so the rule would have "
                "nothing to round.",
                "Remove allocation_rounding, or set design: stratified.",
            )

        # F-3: sample_size is in REQUIRED, so its absence is a missing field rather
        # than an empty sample wearing the wrong code. And a fractional size is
        # refused rather than silently truncated -- 40.7 used to become 40.
        size = raw["sample_size"]
        if isinstance(size, bool) or not isinstance(size, int):
            raise Refusal(
                Reason.PLAN_INVALID,
                f"sample_size is {size!r}. It must be a whole number.",
                "Write it as an integer. A fraction of an item cannot be sampled.",
            )
        n = size
        if n <= 0:
            raise Refusal(
                Reason.EMPTY_SAMPLE,
                f"sample_size is {n}. There is no interval for a sample of nothing.",
                "Set sample_size to a positive whole number.",
            )

        est = raw["estimand"]
        if (
            not isinstance(est, dict)
            or not {"description", "label_field", "threshold"} <= est.keys()
        ):
            raise Refusal(
                Reason.PLAN_INVALID,
                "estimand needs description, label_field and threshold.",
                "A threshold is required even for binary labels; say `positive_when: equals`.",
            )

        # V-3: an unrecognised comparison used to fall through to `at_least`, so a
        # typo silently changed what was being measured -- and the wrong meaning is
        # what got hashed and sealed as the commitment.
        comparison = str(est.get("positive_when", "at_least")).strip().lower()
        if comparison not in SUPPORTED_COMPARISONS:
            raise Refusal(
                Reason.PLAN_INVALID,
                f"positive_when is {comparison!r}, which this tool does not understand.",
                f"Use one of: {', '.join(sorted(SUPPORTED_COMPARISONS))}.",
            )

        # V-4 and V-8: the threshold is validated here, not at estimate time. A
        # pre-registration that accepts a meaningless estimand is not a
        # pre-registration -- the operator would get a hash, believe they had
        # committed, and find out at the end that the commitment meant nothing.
        threshold = str(est["threshold"]).strip()
        numeric = _as_number(threshold)
        if comparison == "at_least" and numeric is None:
            raise Refusal(
                Reason.PLAN_THRESHOLD_INVALID,
                f"threshold {threshold!r} is not a number, but positive_when is `at_least`.",
                "Give a numeric threshold, or use `positive_when: equals` for categorical labels.",
            )
        if comparison == "equals" and numeric is not None:
            raise Refusal(
                Reason.PLAN_THRESHOLD_INVALID,
                f"threshold {threshold!r} is a number, but positive_when is `equals`, "
                f"which compares text exactly.",
                "Use `positive_when: at_least` for numeric labels. Under `equals` a label "
                "of '1.0' would not match a threshold of '1', and the number would be "
                "quietly wrong.",
            )

        return cls(
            estimand=Estimand(
                description=str(est["description"]),
                label_field=str(est["label_field"]),
                positive_when=comparison,
                threshold=threshold,
            ),
            population=str(raw["population"]),
            design=design,
            sample_size=n,
            labels=str(raw["labels"]),
            seed=str(seed),
            interval=interval,
            allocation_rounding=rounding,
            source_path=source_path,
        )

    def as_record(self) -> JSONObject:
        """The hashable form. `source_path` is excluded on purpose.

        Where the file happens to sit on someone's disk is not part of the
        commitment; moving a plan must not change its identity.
        """
        return {
            "estimand": {
                "description": self.estimand.description,
                "label_field": self.estimand.label_field,
                "positive_when": self.estimand.positive_when,
                "threshold": self.estimand.threshold,
            },
            "population": self.population,
            "design": self.design,
            "sample_size": self.sample_size,
            "labels": self.labels,
            "seed": self.seed,
            "interval": self.interval,
            "allocation_rounding": self.allocation_rounding,
        }

    @property
    def plan_hash(self) -> str:
        """The pre-registration hash. Genesis of the chain."""
        return digest(self.as_record())
