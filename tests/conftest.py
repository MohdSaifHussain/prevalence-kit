"""Fixtures. One helper builds a complete, honest run; the tests then damage it.

Every damage helper returns the path it broke, so a test reads as
"break this one thing, then assert exactly which refusal fires".
"""

from __future__ import annotations

import csv
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any, Protocol

import pytest
import yaml

from prevalence_kit.plan import Plan
from prevalence_kit.run import Workspace, do_estimate, do_ingest, do_plan, do_sample

FRAME_SIZE = 200
POSITIVES = 9

BIG_ITEM_INDEX = 0
"""One sampled item gets deliberately large content, so it seals into several
chunks. Without it every item is one chunk, an intra-item reorder is not
expressible, and exit check E9c cannot test what the contract says it tests --
which is exactly how F-4 stayed green while being wrong."""

BIG_ITEM_CHUNKS = 4

PLAN_YAML: dict[str, Any] = {
    "estimand": {
        "description": "Comments scored toxic by at least half of annotators",
        "label_field": "toxicity",
        "positive_when": "at_least",
        "threshold": "0.5",
    },
    "population": "frame.txt",
    "design": "srs",
    "sample_size": 40,
    "labels": "labels.csv",
    "seed": "phase-1-fixture-seed",
}


class HasRoot(Protocol):
    """Anything with a run directory. Lets the damage helpers work on a bare
    directory in unit tests as well as on a real Workspace."""

    @property
    def root(self) -> Path: ...


@pytest.fixture
def plan_path(tmp_path: Path) -> Path:
    path = tmp_path / "plan.yaml"
    path.write_text(yaml.safe_dump(PLAN_YAML, sort_keys=True), encoding="utf-8")
    return path


@pytest.fixture
def plan(plan_path: Path) -> Plan:
    return Plan.load(plan_path)


@pytest.fixture
def frame_path(tmp_path: Path) -> Path:
    path = tmp_path / "frame.txt"
    path.write_text("\n".join(f"item-{i:04d}" for i in range(FRAME_SIZE)), encoding="utf-8")
    return path


def write_labels(tmp_path: Path, drawn: list[str], *, positives: int) -> Path:
    """Label the drawn sample. The first `positives` items are over threshold.

    One item carries content large enough to span several chunks. See
    BIG_ITEM_INDEX.
    """
    from prevalence_kit.seal import CHUNK_BYTES

    path = tmp_path / "labels.csv"
    big = "X" * (CHUNK_BYTES * (BIG_ITEM_CHUNKS - 1) + 17)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["item_id", "toxicity", "content"])
        w.writeheader()
        for i, item_id in enumerate(drawn):
            # A sentinel, so a leak test has something unmistakable to grep for.
            content = f"SENTINEL-CONTENT-{item_id}-do-not-print"
            if i == BIG_ITEM_INDEX:
                content += big
            w.writerow(
                {
                    "item_id": item_id,
                    "toxicity": "0.90" if i < positives else "0.10",
                    "content": content,
                }
            )
    return path


def big_item_chunks(ws: Workspace) -> list[Path]:
    """The chunk files of the deliberately multi-chunk item, in index order."""
    from prevalence_kit.seal import _chunk_index

    drawn: list[str] = list(ws.read_json("sample.json")["item_ids"])
    from prevalence_kit.seal import _safe_id

    item_dir = ws.root / "sealed" / _safe_id(drawn[BIG_ITEM_INDEX])
    return sorted(item_dir.glob("*.bin"), key=_chunk_index)


@pytest.fixture
def run(tmp_path: Path, plan: Plan, plan_path: Path, frame_path: Path) -> Workspace:
    """A complete, honest run: plan -> sample -> ingest -> estimate."""
    ws = Workspace(tmp_path / "run")
    do_plan(ws, plan)
    drawn = do_sample(ws, plan, frame_path)
    labels_path = write_labels(tmp_path, list(drawn), positives=POSITIVES)
    do_ingest(ws, plan, labels_path)
    do_estimate(ws, plan)
    return ws


# ----------------------------------------------------------------- damage


def sealed_item_dir(ws: Workspace) -> Path:
    """The first sealed item that has more than one chunk-sized neighbour."""
    return sorted((ws.root / "sealed").iterdir())[0]


def multi_chunk_item(ws: Workspace, plan: Plan) -> Path:
    """Seal one deliberately large item so truncation and reorder have something to bite."""
    from prevalence_kit.seal import CHUNK_BYTES

    store = ws.store()
    manifest = store.seal("big-item", b"x" * (CHUNK_BYTES * 3 + 17))
    ws.ledger.append(
        "ingest-labels", {"labels_digest": "-", "seals": [manifest.as_record()], "sealed_items": 1}
    )
    return ws.root / "sealed" / sorted(p.name for p in (ws.root / "sealed").iterdir())[0]


def last_ledger_body(ws: Workspace) -> dict[str, Any]:
    lines = (ws.root / "ledger.jsonl").read_text(encoding="utf-8").splitlines()
    record: dict[str, Any] = json.loads(lines[-1])
    return record


def rewrite_ledger_line(ws: HasRoot, index: int, mutate: Callable[[dict[str, Any]], None]) -> None:
    path = ws.root / "ledger.jsonl"
    lines = path.read_text(encoding="utf-8").splitlines()
    record = json.loads(lines[index])
    mutate(record)
    lines[index] = json.dumps(record, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
