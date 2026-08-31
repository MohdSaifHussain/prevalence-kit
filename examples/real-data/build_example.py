#!/usr/bin/env python
"""Rebuild the real-data worked example from the pinned corpus.

**D3.14, ruled at Q28 / D-54 and Q29 / D-55.** The example measures a real
population with real human labels, and **commits no comment text** -- item
identifiers and label values only. That is a choice, not a limitation:
`content` is optional in a labels file, so the whole chain runs without it, and
publishing the text this tool exists to keep sealed would contradict the
product. `examples/real-data/README.md` says so where a reader meets it.

What this script does, in the order a real measurement happens:

  1. writes the frame -- every unit of the population, identified, no content;
  2. runs `plan`, which hashes the plan before any data is touched;
  3. runs `sample`, which draws the units to be labelled;
  4. **then** builds the labels file for exactly those units, which is where a
     real workflow sends the sample to human raters and gets labels back;
  5. runs `ingest-labels`, `estimate`, `verify` and `emit-report`.

The corpus is not committed and is not fetched by this script. Get it first --
`docs/STANDARDS.md` S-8.5 records the procedure and S-7.1 the licence -- and
pass the directory holding the four parquet files.

    python examples/real-data/build_example.py --corpus <dir>

Requires `pyarrow`, which is NOT a dependency of this project and never enters
its tree: run this in a throwaway environment, as `demo/run_coverage.py` does.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

SPLIT_FILE = "validation-00000-of-00001.parquet"
"""The population is the Civil Comments **validation split**, on its own.

A population has to be stated exactly, and "the validation split" is a named,
checkable subset of a corpus whose licence and digests are already in the
register. The whole corpus would make a 26 MB frame file; a slice chosen by us
would be a population nobody else could reconstruct. This one is neither.
"""

EXPECTED_ROWS = 97_320
LABEL_FIELD = "toxicity"
ID_PREFIX = "cc-val-"


def item_id(index: int) -> str:
    """Row index within the split, zero-padded. Reconstructible by anyone."""
    return f"{ID_PREFIX}{index:06d}"


def read_split(corpus: Path) -> list[float]:
    """The toxicity column of the validation split, in file order.

    Rounded to 6 decimal places on the way in, the same decode rule the
    coverage demonstration pre-registered: the corpus stores annotator
    fractions as 32-bit floats, so 7/10 arrives as 0.699999988 and rounding
    restores the intended fraction deterministically.
    """
    import pyarrow.parquet as pq

    path = corpus / SPLIT_FILE
    if not path.exists():
        raise SystemExit(f"corpus file not found: {path}\nS-8.5 records how to fetch it.")
    column = pq.read_table(path, columns=[LABEL_FIELD]).column(LABEL_FIELD).to_pylist()
    if len(column) != EXPECTED_ROWS:
        raise SystemExit(f"REFUSED: split holds {len(column)} rows, expected {EXPECTED_ROWS}")
    return [round(float(v), 6) for v in column]


def run(step: list[str]) -> None:
    print("$ prevalence-kit " + " ".join(step))
    proc = subprocess.run(  # noqa: S603 -- this project's own CLI, arguments from this file
        [sys.executable, "-m", "prevalence_kit.cli", *step],
        capture_output=True,
        text=True,
        cwd=HERE,
    )
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, required=True, help="directory of parquet files")
    args = parser.parse_args()

    values = read_split(args.corpus)
    digest = hashlib.sha256((args.corpus / SPLIT_FILE).read_bytes()).hexdigest()

    # 1. The frame: the whole population, identified. No content, no labels.
    frame = HERE / "frame.txt"
    frame.write_text(
        "\n".join(item_id(i) for i in range(len(values))) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"wrote {frame.name}: {len(values)} units")

    # 2 and 3. Pre-register, then draw. The plan is hashed before the draw.
    run(["plan", "plan.yaml", "--run", "run"])
    run(["sample", "plan.yaml", "frame.txt", "--run", "run"])

    # 4. The labels come back for exactly the drawn units -- the point in a real
    #    measurement where humans have done the work. Here the corpus's own
    #    annotator fractions stand in for them, and no comment text is written.
    drawn = json.loads((HERE / "run" / "sample.json").read_text(encoding="utf-8"))["item_ids"]
    labels = HERE / "labels.csv"
    with labels.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["item_id", LABEL_FIELD], lineterminator="\n")
        writer.writeheader()
        for ident in drawn:
            value = values[int(ident.removeprefix(ID_PREFIX))]
            writer.writerow({"item_id": ident, LABEL_FIELD: f"{value:.6f}"})
    print(f"wrote {labels.name}: {len(drawn)} labels, no content")

    # 5. The rest of the chain.
    run(["ingest-labels", "plan.yaml", "labels.csv", "--run", "run"])
    run(["estimate", "plan.yaml", "--run", "run"])
    run(["verify", "--run", "run", "--plan", "plan.yaml"])
    run(["emit-report", "plan.yaml", "--run", "run"])

    # The census truth, for the README to compare the interval against. This is
    # not part of the measurement -- it is the thing a measurement usually
    # cannot have, and the only reason it exists here is that the population is
    # fully labelled.
    plan = (HERE / "plan.yaml").read_text(encoding="utf-8")
    threshold = float(plan.split("threshold:")[1].split("\n")[0].strip().strip('"'))
    positives = sum(1 for v in values if v >= threshold)
    truth = {
        "population": SPLIT_FILE,
        "sha256": digest,
        "units": len(values),
        "threshold": threshold,
        "census_positives": positives,
        "census_prevalence": positives / len(values),
    }
    (HERE / "census_truth.json").write_text(
        json.dumps(truth, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"census truth: {positives} of {len(values)} = {positives / len(values):.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
