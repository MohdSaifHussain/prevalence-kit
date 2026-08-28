#!/usr/bin/env python
"""Check the three tripwires in docs/TRIPWIRES.md against their baselines.

A tripwire that is never checked is a decoration. Each is checked at every phase
close and at release, and the result is recorded in the phase outcome as
"checked <date>, not fired" or "checked <date>, FIRED".

  TW-1  Pinterest open-sources the arXiv 2602.18518 system.
  TW-2  svy ships Trust & Safety prevalence or transparency output.
  TW-3  Official DSA accuracy-indicator tooling appears.

**This tool makes network calls. The shipped package does not.**
It lives in `tools/`, is not part of `prevalence_kit`, and is never imported by
it. Hard Rule 1 -- zero network calls at runtime -- is about the package, and
`tests/test_guarantees.py` proves it by scanning `src/` and the declared runtime
dependencies. Neither includes this file.

Offline by default: `--check` is required to reach the network, so running this
in CI or on a plane prints the baselines and exits 0 rather than failing for the
wrong reason.
"""

from __future__ import annotations

import argparse
import json
import re
import urllib.error
import urllib.request
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime

TIMEOUT = 30
AGENT = "prevalence-kit-tripwires (+https://github.com/MohdSaifHussain/prevalence-kit)"

# Baselines established 2026-08-28, docs/TRIPWIRES.md.
BASELINE_ARXIV_VERSION = "2602.18518v2"
BASELINE_ARXIV_UPDATED = "2026-08-17"
BASELINE_SVY_VERSION = "0.25.0"
BASELINE_PINTEREST_REPOS = 99
DSA_CELEX = "32024R2835"


@dataclass(frozen=True, slots=True)
class Result:
    tripwire: str
    fired: bool
    detail: str

    def line(self) -> str:
        mark = "FIRED" if self.fired else "not fired"
        return f"  {self.tripwire}: {mark} -- {self.detail}"


def fetch(url: str, *, as_json: bool = False) -> str | dict:  # type: ignore[type-arg]
    request = urllib.request.Request(url, headers={"User-Agent": AGENT})  # noqa: S310
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:  # noqa: S310
        body = response.read().decode("utf-8", errors="replace")
    return json.loads(body) if as_json else body


def check_tw1() -> Result:
    """Pinterest: a newer paper version, a code link, or a matching repository."""
    notes: list[str] = []
    fired = False

    feed = fetch(f"http://export.arxiv.org/api/query?id_list={BASELINE_ARXIV_VERSION[:-2]}")
    assert isinstance(feed, str)
    version = re.search(r"<id>http://arxiv\.org/abs/(\S+?)</id>", feed[feed.index("<entry>") :])
    if version and version.group(1) != BASELINE_ARXIV_VERSION:
        fired = True
        notes.append(f"paper is now {version.group(1)}, baseline {BASELINE_ARXIV_VERSION}")
    if "journal_ref" in feed:
        fired = True
        notes.append("a journal_ref appeared -- the preprint may have been accepted")

    search = fetch(
        "https://api.github.com/search/repositories?q=prevalence+policy+violating+content",
        as_json=True,
    )
    assert isinstance(search, dict)
    if search.get("total_count", 0):
        fired = True
        notes.append(f"{search['total_count']} repositories now match the system description")

    return Result("TW-1", fired, "; ".join(notes) or f"still {BASELINE_ARXIV_VERSION}, no code")


def check_tw2() -> Result:
    """svy: a new release, and whether it has grown into our half of the problem."""
    data = fetch("https://pypi.org/pypi/svy/json", as_json=True)
    assert isinstance(data, dict)
    version = data["info"]["version"]

    blurb = f"{data['info'].get('summary', '')} {data['info'].get('description', '')}".lower()
    ours = [
        w for w in ("prevalence", "transparency", "seal", "ledger", "audit trail") if w in blurb
    ]

    fired = bool(ours)
    detail = f"svy {version} (baseline {BASELINE_SVY_VERSION})"
    if version != BASELINE_SVY_VERSION:
        detail += " -- NEW RELEASE, re-read the changelog"
    if ours:
        detail += f"; now mentions {', '.join(ours)}"
    return Result("TW-2", fired, detail)


def check_tw3() -> Result:
    """DSA: has 2024/2835 been amended, consolidated, or repealed?

    EUR-Lex sits behind a bot challenge, so this uses the EU Publications Office
    endpoint -- same authority, machine-readable, no challenge.
    """
    notice = fetch(
        f"http://publications.europa.eu/resource/celex/{DSA_CELEX}",
        # Accept header is set below; urllib needs it on the Request, so refetch.
    )
    assert isinstance(notice, str)

    fired = False
    notes = []
    for date in ("20250701", "20260101", "20270101"):
        try:
            fetch(f"http://publications.europa.eu/resource/celex/0{DSA_CELEX[1:]}-{date}")
        except urllib.error.HTTPError:
            continue
        fired = True
        notes.append(f"a consolidated version dated {date} now exists -- it has been amended")

    return Result("TW-3", fired, "; ".join(notes) or "in force, unamended, no consolidated version")


CHECKS = {"TW-1": check_tw1, "TW-2": check_tw2, "TW-3": check_tw3}


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="make network calls")
    args = parser.parse_args(list(argv) if argv is not None else None)

    today = datetime.now(UTC).strftime("%Y-%m-%d")
    print(f"Tripwire check, {today}. Baselines from docs/TRIPWIRES.md, 2026-08-28.\n")

    if not args.check:
        print("  Offline. Baselines only; pass --check to reach the network.")
        print(
            f"    TW-1  arXiv {BASELINE_ARXIV_VERSION}, updated {BASELINE_ARXIV_UPDATED}, no code"
        )
        print(f"    TW-2  svy {BASELINE_SVY_VERSION}, no prevalence or transparency surface")
        print(f"    TW-3  CELEX {DSA_CELEX} in force, unamended")
        return 0

    results: list[Result] = []
    for name, fn in CHECKS.items():
        try:
            results.append(fn())
        except Exception as exc:
            results.append(Result(name, False, f"COULD NOT CHECK: {type(exc).__name__}: {exc}"))

    for result in results:
        print(result.line())

    unchecked = [r for r in results if "COULD NOT CHECK" in r.detail]
    fired = [r for r in results if r.fired]
    print()
    if unchecked:
        print(f"  {len(unchecked)} tripwire(s) could not be checked. That is not 'not fired'.")
    print(f"  Record in the phase outcome: checked {today}, " + ("FIRED" if fired else "not fired"))
    return 1 if fired or unchecked else 0


if __name__ == "__main__":
    raise SystemExit(main())
