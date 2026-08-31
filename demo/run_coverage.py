#!/usr/bin/env python
"""The coverage demonstration, exactly as demo/preregistration.json commits to it.

Two phases, because they need different environments:

  --prepare   Reads the corpus (pyarrow required -- the throwaway-environment
              precedent from svy/: pyarrow never enters this project's
              dependency tree), computes the census at each pre-registered
              threshold, runs the replication study through the shipped
              estimators, writes demo/coverage_results.json and
              demo/coverage_curve.svg, and materialises the full-chain run's
              inputs (frame and labels) into the scratch directory.

  --chain     Runs the sealed chain once -- plan, sample, ingest-labels,
              estimate, verify, emit-report -- on the inputs --prepare wrote,
              using this project's own venv, and copies the plan and the two
              reports into demo/full_chain/.

Every number this script emits is pinned by the pre-registration committed
before any corpus byte was fetched. Where this file and that file disagree,
this file is wrong.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import subprocess
import sys
from array import array
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "demo"

PREREG = json.loads((DEMO / "preregistration.json").read_text(encoding="utf-8"))
THRESHOLDS: list[str] = PREREG["thresholds"]
N_SAMPLE: int = PREREG["design"]["sample_size"]
CONFIDENCE: float = PREREG["design"]["confidence"]
REPS: int = PREREG["design"]["replications_per_threshold"]
SEED_ROOT: str = PREREG["replication_sampler"]["seed_root"]
EXPECTED_ROWS: int = PREREG["corpus"]["expected_rows_total"]

CORPUS_FILES = [
    "train-00000-of-00002.parquet",
    "train-00001-of-00002.parquet",
    "validation-00000-of-00001.parquet",
    "test-00000-of-00001.parquet",
]
"""Canonical frame order per the pre-registration: train files in lexicographic
name order, then validation, then test. Recorded here as the executed form."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_toxicity(corpus_dir: Path) -> tuple[array, list[dict[str, object]]]:
    """The toxicity column over the whole corpus, in canonical frame order.

    Values are decoded to 64-bit floats and rounded to 6 decimal places, the
    pre-registered decode rule: the corpus stores annotator fractions as
    32-bit floats, so 7/10 arrives as 0.699999988... and the rounding restores
    the intended fraction deterministically.
    """
    import pyarrow.parquet as pq

    values = array("d")
    fetch: list[dict[str, object]] = []
    for name in CORPUS_FILES:
        path = corpus_dir / name
        table = pq.read_table(path, columns=["toxicity"])
        column = table.column("toxicity").to_pylist()
        values.extend(round(float(v), 6) for v in column)
        fetch.append(
            {
                "file": name,
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
                "rows": len(column),
            }
        )
    if len(values) != EXPECTED_ROWS:
        raise SystemExit(
            f"REFUSED: corpus holds {len(values)} rows, pre-registration commits to {EXPECTED_ROWS}"
        )
    return values, fetch


def sample_indices(threshold: str, rep: int) -> list[int]:
    """The pre-registered hash-counter sampler, verbatim from its spec."""
    chosen: set[int] = set()
    out: list[int] = []
    counter = 0
    while len(out) < N_SAMPLE:
        material = f"{SEED_ROOT}|t={threshold}|rep={rep}|c={counter}".encode()
        candidate = int.from_bytes(hashlib.sha256(material).digest(), "big") % EXPECTED_ROWS
        counter += 1
        if candidate in chosen:
            continue
        chosen.add(candidate)
        out.append(candidate)
    return out


def replicate(values: array) -> dict[str, dict[str, object]]:
    """10,000 draws per threshold, each positive count judged by both intervals.

    Intervals are computed once per distinct k and tallied over the k
    distribution -- the same arithmetic as interval-per-draw, without paying
    the exact-tail root-find 40,000 times.
    """
    sys.path.insert(0, str(ROOT / "src"))
    from prevalence_kit.estimators import clopper_pearson, wilson

    results: dict[str, dict[str, object]] = {}
    for threshold in THRESHOLDS:
        limit = float(threshold)
        flags = bytearray(1 if v >= limit else 0 for v in values)
        census = sum(flags)
        truth = census / EXPECTED_ROWS

        k_counts: dict[int, int] = {}
        for rep in range(REPS):
            k = sum(flags[i] for i in sample_indices(threshold, rep))
            k_counts[k] = k_counts.get(k, 0) + 1

        per_interval: dict[str, dict[str, object]] = {}
        for name, estimator in (("wilson", wilson), ("clopper_pearson", clopper_pearson)):
            covered = 0
            for k, count in k_counts.items():
                interval = estimator(k, N_SAMPLE, confidence=CONFIDENCE)
                if float(interval.low) <= truth <= float(interval.high):
                    covered += count
            per_interval[name] = {"covered": covered, "coverage": covered / REPS}

        results[threshold] = {
            "census_count": census,
            "census_proportion": truth,
            "draws": REPS,
            "distinct_k": len(k_counts),
            "intervals": per_interval,
        }
        print(
            f"threshold {threshold}: census {census} ({truth:.6f}), "
            + ", ".join(f"{name} {info['coverage']:.4f}" for name, info in per_interval.items())
        )
    return results


def write_svg(results: dict[str, dict[str, object]]) -> None:
    """The sensitivity curve, drawn directly -- no plotting dependency.

    Coverage against census prevalence on a log axis, one line per interval,
    the nominal level dashed, error bars from the replication count, and the
    charter section 8 stratified enumeration cross-referenced rather than
    re-measured (D-44).
    """
    import math

    width, height = 760, 470
    left, right, top, bottom = 80, 30, 56, 96
    plot_w, plot_h = width - left - right, height - top - bottom
    y_lo, y_hi = 0.80, 1.00

    points = []
    for threshold in THRESHOLDS:
        row = results[threshold]
        points.append((threshold, float(str(row["census_proportion"])), row["intervals"]))
    xs = [math.log10(p) for _, p, _ in points]
    x_lo, x_hi = min(xs) - 0.25, max(xs) + 0.25

    def x_at(p: float) -> float:
        return left + (math.log10(p) - x_lo) / (x_hi - x_lo) * plot_w

    def y_at(c: float) -> float:
        return top + (y_hi - c) / (y_hi - y_lo) * plot_h

    half = 1.96 * math.sqrt(CONFIDENCE * (1 - CONFIDENCE) / REPS)
    colors = {"wilson": "#b34700", "clopper_pearson": "#1a5fb4"}
    labels = {"wilson": "Wilson", "clopper_pearson": "Clopper-Pearson"}

    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'font-family="Georgia, serif" font-size="13">'
    )
    parts.append(f'<rect width="{width}" height="{height}" fill="#ffffff"/>')
    parts.append(
        f'<text x="{left}" y="24" font-size="16" fill="#1a1a1a">'
        f"Interval coverage on Civil Comments, by census prevalence</text>"
    )
    parts.append(
        f'<text x="{left}" y="42" fill="#555555">{REPS:,} SRS draws per point, n = {N_SAMPLE}, '
        f"nominal {CONFIDENCE:.2f}; truth known by census over {EXPECTED_ROWS:,} rows</text>"
    )

    for tick in (0.80, 0.85, 0.90, 0.95, 1.00):
        y = y_at(tick)
        parts.append(
            f'<line x1="{left}" y1="{y:.1f}" x2="{width - right}" y2="{y:.1f}" '
            f'stroke="#e0e0e0" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{left - 10}" y="{y + 4:.1f}" text-anchor="end" '
            f'fill="#555555">{tick:.2f}</text>'
        )
    nominal_y = y_at(CONFIDENCE)
    parts.append(
        f'<line x1="{left}" y1="{nominal_y:.1f}" x2="{width - right}" y2="{nominal_y:.1f}" '
        f'stroke="#1a1a1a" stroke-width="1.2" stroke-dasharray="6 4"/>'
    )

    for threshold, p, _ in points:
        x = x_at(p)
        parts.append(
            f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top + plot_h}" '
            f'stroke="#f0f0f0" stroke-width="1"/>'
        )
        pct = f"{p * 100:.3f}%" if p < 0.01 else f"{p * 100:.2f}%"
        parts.append(
            f'<text x="{x:.1f}" y="{top + plot_h + 20}" text-anchor="middle" '
            f'fill="#555555">{pct}</text>'
        )
        parts.append(
            f'<text x="{x:.1f}" y="{top + plot_h + 38}" text-anchor="middle" fill="#999999" '
            f'font-size="11">t = {threshold}</text>'
        )

    for name in ("wilson", "clopper_pearson"):
        color = colors[name]
        coords = []
        for _, p, intervals in points:
            c = float(str(intervals[name]["coverage"]))
            coords.append((x_at(p), y_at(c), c))
        path = " ".join(
            f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}" for i, (x, y, _) in enumerate(coords)
        )
        parts.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="2"/>')
        for x, y, c in coords:
            parts.append(
                f'<line x1="{x:.1f}" y1="{y_at(c - half):.1f}" '
                f'x2="{x:.1f}" y2="{y_at(c + half):.1f}" '
                f'stroke="{color}" stroke-width="1.4"/>'
            )
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.4" fill="{color}"/>')

    legend_y = top + 16
    for i, name in enumerate(("wilson", "clopper_pearson")):
        y = legend_y + i * 18
        parts.append(
            f'<line x1="{left + 12}" y1="{y}" x2="{left + 40}" y2="{y}" '
            f'stroke="{colors[name]}" stroke-width="2"/>'
        )
        parts.append(f'<text x="{left + 48}" y="{y + 4}" fill="#1a1a1a">{labels[name]}</text>')

    parts.append(
        f'<text x="{left}" y="{height - 34}" fill="#555555" font-size="12">Error bars: '
        f"±1.96·√(0.95·0.05/{REPS:,}) ≈ ±{half:.4f}. Sampling is without "
        f"replacement (n/N = 0.05%), judged by binomial intervals; "
        f"disclosed in demo/READING.md.</text>"
    )
    parts.append(
        f'<text x="{left}" y="{height - 16}" fill="#555555" font-size="12">'
        f"Stratified intervals are measured exhaustively, not sampled: "
        f"charter section 8 carries that 96-point table.</text>"
    )
    parts.append("</svg>")
    (DEMO / "coverage_curve.svg").write_text(
        "\n".join(parts) + "\n", encoding="utf-8", newline="\n"
    )


def prepare(corpus_dir: Path, scratch: Path) -> int:
    values, fetch = load_toxicity(corpus_dir)
    results = replicate(values)

    payload = {
        "preregistration_sha256": sha256_file(DEMO / "preregistration.json"),
        "generated": date.today().isoformat(),
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "pyarrow": __import__("pyarrow").__version__,
            "note": "Throwaway environment; pyarrow is not a dependency of this project.",
        },
        "fetch": fetch,
        "total_rows": EXPECTED_ROWS,
        "results": results,
    }
    (DEMO / "coverage_results.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    write_svg(results)

    chain = PREREG["full_chain_run"]
    sys.path.insert(0, str(ROOT / "src"))
    from prevalence_kit.sampling import draw_srs

    ids = [f"cc-{i:07d}" for i in range(EXPECTED_ROWS)]
    scratch.mkdir(parents=True, exist_ok=True)
    (scratch / "frame.txt").write_text("\n".join(ids) + "\n", encoding="utf-8", newline="\n")
    drawn = draw_srs(ids, seed=str(chain["seed"]), n=int(chain["sample_size"]))

    import pyarrow.parquet as pq

    wanted = {int(item[3:]) for item in drawn}
    texts: dict[int, str] = {}
    offset = 0
    for name in CORPUS_FILES:
        table = pq.read_table(corpus_dir / name, columns=["text"])
        column = table.column("text")
        for local in range(len(column)):
            if offset + local in wanted:
                texts[offset + local] = str(column[local].as_py())
        offset += len(column)

    with (scratch / "labels.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["item_id", "toxicity", "content"])
        writer.writeheader()
        for item in drawn:
            index = int(item[3:])
            writer.writerow(
                {
                    "item_id": item,
                    "toxicity": f"{values[index]:.6f}".rstrip("0").rstrip(".") or "0",
                    "content": texts[index],
                }
            )
    print(f"full-chain inputs written to {scratch}")
    return 0


def chain(scratch: Path) -> int:
    spec = PREREG["full_chain_run"]
    plan_text = (
        "estimand:\n"
        "  description: Comments scored toxic by at least ninety percent of annotators\n"
        "  label_field: toxicity\n"
        "  positive_when: at_least\n"
        f'  threshold: "{spec["threshold"]}"\n'
        "population: frame.txt\n"
        f"design: {spec['design']}\n"
        f"sample_size: {spec['sample_size']}\n"
        "labels: labels.csv\n"
        f"interval: {spec['interval']}\n"
        f"seed: {spec['seed']}\n"
    )
    (scratch / "plan.yaml").write_text(plan_text, encoding="utf-8", newline="\n")

    # Every path is passed RELATIVE and the commands run from the scratch
    # directory. The ledger records paths as invoked (SECURITY.md 3.8), and a
    # committed report carrying an absolute local path is exactly the leak
    # that section tells operators to avoid -- caught here by reading the
    # first report by eye before committing it.
    run_dir = scratch / "run"
    steps = [
        ["plan", "plan.yaml", "--run", "run"],
        ["sample", "plan.yaml", "frame.txt", "--run", "run"],
        ["ingest-labels", "plan.yaml", "labels.csv", "--run", "run"],
        ["estimate", "plan.yaml", "--run", "run"],
        ["verify", "--run", "run", "--plan", "plan.yaml"],
        ["emit-report", "plan.yaml", "--run", "run"],
    ]
    for step in steps:
        print("$ prevalence-kit " + " ".join(step))
        # Not untrusted input: this project's own CLI, with arguments that come
        # from the committed pre-registration. Same justification shape as the
        # S310 exemptions in tools/check_tripwires.py.
        proc = subprocess.run(  # noqa: S603
            [sys.executable, "-m", "prevalence_kit.cli", *step],
            capture_output=True,
            text=True,
            cwd=scratch,
        )
        sys.stdout.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        if proc.returncode != 0:
            return proc.returncode

    out = DEMO / "full_chain"
    out.mkdir(exist_ok=True)
    (out / "plan.yaml").write_text(plan_text, encoding="utf-8", newline="\n")
    for name in ("report.md", "report.json"):
        (out / name).write_bytes((run_dir / name).read_bytes())
    print(f"plan and reports copied to {out}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--chain", action="store_true")
    parser.add_argument("--corpus", type=Path, help="directory holding the four parquet files")
    parser.add_argument("--scratch", type=Path, help="working directory for full-chain inputs")
    args = parser.parse_args()
    if args.prepare:
        if args.corpus is None or args.scratch is None:
            parser.error("--prepare needs --corpus and --scratch")
        return prepare(args.corpus, args.scratch)
    if args.chain:
        if args.scratch is None:
            parser.error("--chain needs --scratch")
        return chain(args.scratch)
    parser.error("pass --prepare or --chain")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
