#!/usr/bin/env python
"""Regenerate the shipped example under examples/synthetic/.

The example is a fixture the director runs the exit checklist against, so it has
to be able to *perform* every exit check that names it. It is generated rather
than hand-made, so the properties the checklist depends on are visible here in
code instead of implied by a 200 KB CSV nobody reads.

Two properties the checklist depends on:

  * **One deliberately multi-chunk item.** Exit check E9c swaps two chunks
    *within one item* and expects `SEAL_REORDERED`. With every item under
    `CHUNK_BYTES` that is not expressible, the nearest possible action is a
    cross-item swap, and that reports `SEAL_MANIFEST_MISMATCH` -- the contract
    would say one thing and the tool another.

    This is finding F-4 exactly, which was fixed in `tests/conftest.py` and then
    regressed into this directory when it was created afterwards. See
    docs/CORRECTIONS.md C-15.

  * **A known true prevalence.** 9 of 40, so E4 -- reading the report by eye --
    has something to judge the interval against.

`tools/check_claims.py` asserts the first property, so the regression cannot
happen a second time silently.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "synthetic"

FRAME_SIZE = 200
SAMPLE_SIZE = 40
POSITIVES = 9

BIG_ITEM_INDEX = 0
BIG_ITEM_CHUNKS = 4
"""The first sampled item gets content spanning this many chunks, so E9c has an
item whose chunks can be reordered relative to each other."""


def main() -> int:
    sys.path.insert(0, str(ROOT / "src"))
    from prevalence_kit.plan import Plan
    from prevalence_kit.sampling import draw_srs
    from prevalence_kit.seal import CHUNK_BYTES

    EXAMPLE.mkdir(parents=True, exist_ok=True)

    frame_path = EXAMPLE / "frame.txt"
    frame = [f"item-{i:04d}" for i in range(FRAME_SIZE)]
    frame_path.write_text("\n".join(frame) + "\n", encoding="utf-8", newline="\n")

    plan = Plan.load(EXAMPLE / "plan.yaml")
    drawn = draw_srs(frame, seed=plan.seed, n=plan.sample_size)

    big = "X" * (CHUNK_BYTES * (BIG_ITEM_CHUNKS - 1) + 17)
    labels_path = EXAMPLE / "labels.csv"
    with labels_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["item_id", "toxicity", "content"])
        writer.writeheader()
        for i, item_id in enumerate(drawn):
            content = f"synthetic content for {item_id}"
            if i == BIG_ITEM_INDEX:
                content += big
            writer.writerow(
                {
                    "item_id": item_id,
                    "toxicity": "0.90" if i < POSITIVES else "0.10",
                    "content": content,
                }
            )

    chunks = -(-len(big.encode()) // CHUNK_BYTES)
    print(f"wrote {frame_path}  ({FRAME_SIZE} items)")
    print(f"wrote {labels_path} ({len(drawn)} rows, {POSITIVES} positive)")
    print(f"  multi-chunk item: {drawn[BIG_ITEM_INDEX]}, about {chunks} chunks -- E9c needs this")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
