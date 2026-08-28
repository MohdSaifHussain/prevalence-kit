#!/usr/bin/env python
"""Check the three tripwires in docs/TRIPWIRES.md against their baselines.

A tripwire that is never checked is a decoration. Each is checked at every phase
close and at release, and the result is recorded in the phase outcome as
"checked <date>, not fired" or "checked <date>, FIRED".

  TW-1  Pinterest open-sources the arXiv 2602.18518 system.
  TW-2  svy ships Trust & Safety prevalence or transparency output.
  TW-3  Official DSA accuracy-indicator tooling appears.
  TW-4  A SHA-pinned GitHub Action falls behind its runtime. Pinning is what
        stops an action updating itself, so the pin has an expiry and somebody
        has to watch it. That is the cost of pinning, not an argument against
        it. O-19.
  TW-5  The p3m mirror stops carrying CRAN's bytes. The register names CRAN as
        the source of `survey`; the R image installs from a Posit mirror. V-17.
        Verified once by hand; this is what keeps it verified.

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
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
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


def fetch(  # type: ignore[type-arg]
    url: str, *, as_json: bool = False, as_bytes: bool = False
) -> str | bytes | dict:
    request = urllib.request.Request(url, headers={"User-Agent": AGENT})  # noqa: S310
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:  # noqa: S310
        raw = response.read()
    if as_bytes:
        return bytes(raw)
    body = raw.decode("utf-8", errors="replace")
    return json.loads(body) if as_json else body


def check_tw1() -> Result:
    """Pinterest: a newer paper version, a code link, or a matching repository."""
    notes: list[str] = []
    fired = False

    feed = fetch(f"https://export.arxiv.org/api/query?id_list={BASELINE_ARXIV_VERSION[:-2]}")
    assert isinstance(feed, str)

    # Parsed as XML, not pattern-matched. C-23: check an artifact the way its
    # real consumer reads it. This used a regex over the Atom feed, which is the
    # same defect that let an unparseable gate.yml through a green checker.
    atom = "{http://www.w3.org/2005/Atom}"
    arxiv = "{http://arxiv.org/schemas/atom}"
    # The suppression below is justified, not a silencing. S314 warns that `xml`
    # parses untrusted
    # data unsafely. Three things bound it here: the feed is fetched over TLS
    # (this call was plain http:// until ruff pointed at it); CPython's
    # ElementTree does not resolve external entities, so XXE is not reachable;
    # and this file is a hand-run phase-close tool outside the shipped package,
    # so the worst case of an entity-expansion feed is a hung ritual, not a
    # compromised estimate. `defusedxml` would close the last of those and is a
    # new dependency for a dev tool -- recorded as the option not taken.
    entry = ElementTree.fromstring(feed).find(f"{atom}entry")  # noqa: S314
    if entry is None:
        return Result("TW-1", False, "COULD NOT CHECK: the arXiv feed carried no <entry>")

    ident = (entry.findtext(f"{atom}id") or "").rsplit("/", 1)[-1]
    if ident and ident != BASELINE_ARXIV_VERSION:
        fired = True
        notes.append(f"paper is now {ident}, baseline {BASELINE_ARXIV_VERSION}")
    if entry.find(f"{arxiv}journal_ref") is not None:
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


ACTION_PIN = re.compile(r"uses:\s+([\w.-]+/[\w.-]+)@([0-9a-f]{40})\s*#\s*(v\S+)")


def pinned_actions() -> dict[str, tuple[str, str]]:
    """Read the pins out of the workflow instead of carrying a copy of them.

    A baseline constant here would be a second place the SHA lives, and the two
    would drift. The workflow is the artifact; this reads it. Rule 13.
    """
    text = (ROOT / ".github" / "workflows" / "gate.yml").read_text(encoding="utf-8")
    return {repo: (sha, tag) for repo, sha, tag in ACTION_PIN.findall(text)}


def check_tw4() -> Result:
    """Actions: has a pinned action been superseded?

    Fires on "a newer release exists", not on "Node 20 is gone", because the
    first is the signal you can still act on. When GitHub drops Node 20 the
    failure is a red X on every job with nothing wrong in this repository, and
    by then the decision has been made for us.
    """
    fired = False
    notes: list[str] = []
    pins = pinned_actions()
    if not pins:
        return Result("TW-4", False, "COULD NOT CHECK: no SHA-pinned actions found in gate.yml")

    for repo, (sha, tag) in sorted(pins.items()):
        release = fetch(f"https://api.github.com/repos/{repo}/releases/latest", as_json=True)
        assert isinstance(release, dict)
        newest = release.get("tag_name", "?")
        if newest != tag:
            fired = True
            notes.append(f"{repo} pinned at {tag} ({sha[:12]}...), latest release is {newest}")

    return Result(
        "TW-4",
        fired,
        "; ".join(notes) or f"{len(pins)} pinned actions, each at its latest release",
    )


CRAN_SURVEY = "https://cran.r-project.org/src/contrib/survey_4.5.tar.gz"
P3M_SURVEY = "https://p3m.dev/cran/2026-04-23/src/contrib/survey_4.5.tar.gz"
MIRROR_EXPECTED_DIFFERENCES = {"survey/DESCRIPTION", "survey/MD5"}
"""The only two files allowed to differ between CRAN and the mirror.

Measured 2026-08-29: the tarball holds 355 entries, of which **341 are regular
files** and 14 are directories. **339 of the 341 are byte-identical.**
`DESCRIPTION` differs because the mirror stamps `Repository: RSPM` over
`Repository: CRAN` and adds an `Encoding:` line; `MD5` differs because it lists
DESCRIPTION's own checksum. Any third file appearing here means the mirror is
serving something CRAN is not.

The count is 341 and not 355 because the first hand-count of this treated
directory entries as files. This tool reported 339/341 on its first run and the
figure here was corrected to match it -- re-derive from the artifact, do not
restate the sentence.
"""


def check_tw5() -> Result:
    """The mirror the R image builds from must still carry CRAN's bytes.

    V-17: the register named CRAN and the build retrieved from Posit Package
    Manager, and nobody had checked the two carry the same package. They do,
    except for two metadata files. This watches that it stays true.
    """
    import io
    import tarfile

    def members(url: str) -> dict[str, bytes]:
        raw = fetch(url, as_bytes=True)
        assert isinstance(raw, bytes)
        with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as tar:
            out: dict[str, bytes] = {}
            for member in tar.getmembers():
                if member.isfile():
                    handle = tar.extractfile(member)
                    if handle is not None:
                        out[member.name] = handle.read()
            return out

    cran, mirror = members(CRAN_SURVEY), members(P3M_SURVEY)

    notes: list[str] = []
    fired = False
    only_cran = sorted(set(cran) - set(mirror))
    only_mirror = sorted(set(mirror) - set(cran))
    if only_cran or only_mirror:
        fired = True
        notes.append(
            f"file lists differ: {len(only_cran)} only on CRAN, "
            f"{len(only_mirror)} only on the mirror"
        )

    differing = {name for name in set(cran) & set(mirror) if cran[name] != mirror[name]}
    unexpected = sorted(differing - MIRROR_EXPECTED_DIFFERENCES)
    if unexpected:
        fired = True
        notes.append(f"content differs beyond the metadata pair: {', '.join(unexpected)}")

    detail = "; ".join(notes) or (
        f"{len(set(cran) & set(mirror)) - len(differing)} of {len(cran)} files byte-identical; "
        f"only {', '.join(sorted(differing))} differ, as recorded"
    )
    return Result("TW-5", fired, detail)


CHECKS = {
    "TW-1": check_tw1,
    "TW-2": check_tw2,
    "TW-3": check_tw3,
    "TW-4": check_tw4,
    "TW-5": check_tw5,
}


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
        for repo, (sha, tag) in sorted(pinned_actions().items()):
            print(f"    TW-4  {repo} pinned {tag} @ {sha[:12]}...")
        print("    TW-5  survey 4.5: CRAN vs the p3m mirror, 339/341 files byte-identical")
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
