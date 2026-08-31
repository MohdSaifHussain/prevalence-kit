# O-28 — the git-history review, a dated reading

**Date: 31 August 2026** · **Deliverable: D3.5** · **Tree: `4be95c4`, 82 commits, all refs** ·
**Status: the reading. Every finding ruled by the director, 2026-08-31; rulings recorded in
place. The close is the director's read of this document.**

**This file is a dated reading and is never edited.** Corrections to it go in
`docs/CORRECTIONS.md` with the date and the direction the number moved.

**What this is.** The one-time look backwards O-28 required before anything goes public: the
full git history read as a stranger's tools would read it — every commit message and tree,
every ref, by census and by pattern. This record cites commit hashes as evidence throughout,
so the history is not rewritten; this review is what stands in place of a repair. Every finding
below was verified independently by the reviewer, including four sweeps the builder had not
run, and every negative claim names the search that produced it — a "none found" with no named
search is a claim about the world, and this project has been wrong three times that way.

## Findings, with the director's rulings

**1. Local Windows paths, in exactly the five documents the record pre-named.** A fixed-string
sweep for the director's directory prefix over **every revision** returns `PROJECT_CHARTER.md`,
`CLAUDE.md`, `docs/RATIFICATION.md`, `docs/PHASE-0-VERIFICATION.md` and
`docs/contracts/PHASE-2-HAND-RUN.md` — one occurrence each at HEAD, no other file in any
revision. Two are dated readings that are never edited. **RULED: Q19 / D-45 stands — disclose,
edit nothing.** The paths are directory structure, not identity; the username is already public
via the repository owner; the documents carrying them are dated evidence. The tension with
`SECURITY.md` §3.8 — which tells operators to avoid exactly this in artifacts they publish —
is named here rather than hidden: §3.8's advice is about run artifacts, these are the record's
own working papers, and the one time the leak nearly reached a *run* artifact it was caught
before commit (finding 8).

**A stranger running a broader pattern gets seven files, not five, and should know the project
read all seven.** The reviewer's wider sweep — any `C:\` path form — adds `SECURITY.md`,
matching on the **invented example** `C:\work\jan\plan.yaml` inside the §3.8 warning itself,
and `docs/CORRECTIONS.md`, matching on an **elided** `C:\...\plan.yaml` in a verification
quote. Both are illustrative; neither is the director's directory. Reproduced by the builder
with `git grep -l -F 'C:\' HEAD`. That is the difference between a review and a claim about a
review: the seven-hit sweep is recorded so nobody has to wonder whether the extra two were
seen.

**2. Identity.** All 82 commits, author and committer, across every ref: the single GitHub
noreply address. A personal-email sweep (`gmail`, the address's local part) over every
revision's trees **and every commit message body** returns nothing. **RULED: no action.**

**3. Secrets.** Pattern sweep over every revision — GitHub token, AWS key id, private-key
block headers, Slack tokens, bearer tokens, `api_key=` — zero matches; the reviewer's
independent pattern list also returned zero; no `*.key` file was ever tracked. The sealing key
has never left a run directory. **RULED: no action.** The pattern lists are in the command
appendix so a stranger can extend them.

**4. Rule 18, backwards.** One PDF in all of history: `OJ_L_202402835_EN_TXT.pdf`, the EU
official text cleared for reuse under Decision 2011/833/EU (O-18). The second PDF **on disk**
is that clearance decision's own text, `OJ_L_2011_330_FULL_EN_TXT.pdf` — never tracked and
gitignored, so it cannot be committed by accident. No paper text, no acquisition routes.
**RULED: no action.**

**5. Nothing was ever deleted.** `git log --diff-filter=D` over all history is empty: there is
no removed file to excavate, no cleanup that reads as concealment. The largest objects ever
committed are the EU PDF, the `svy` and `stratallo` fixtures, and this project's own
corrections register; the demonstration corpus never entered the repository. **RULED: no
action.**

**6. The commit-trailer seam.** Commits from `03a0c7b` onward carry `Co-Authored-By` and
`Claude-Session` trailers; Phases 0–2 carry neither. **RULED: the trailers continue, and the
seam is disclosed here as form, not substance** — the record's central claim is that an AI
wrote the code under direction, so tooling metadata is consistent with it rather than
embarrassing to it. A stranger who notices learns nothing the README does not already say. The
session links resolve only for the account owner.

**7. `TIME-LOG.txt` carries IST wall-clock times** — a weak locale signal, noted. **RULED: no
action.**

**8. The near-miss that never reached history.** The first full-chain report of D3.3 carried an
absolute local path and was discarded before commit; `git log -p` over `demo/full_chain/`
shows no committed version ever carried one, and `demo/READING.md` discloses the discard. In
the record already; recorded here because a stranger auditing paths should find it where the
path audit is.

**9. All refs.** `main` and its remote-tracking mirror only. No tags — the first tag this
repository ever gets will be the release, after rehearsal. No abandoned branches. **RULED
(with 2): no action.**

## Scope — what this review did and did not do

It swept every revision **by pattern and by census** — identities, deletions, object sizes,
path forms, secret shapes, file types, refs, and every commit message — and read every commit
subject; it did not re-read every file's every revision line by line. The working tree at HEAD
has been under continuous review by the project's other instruments; this was the look
backwards at what only history holds. **The reviewer's independent sweeps are part of this
reading's evidence**: commit message bodies (a surface `git grep` cannot see, since it searches
trees, and this project writes long bodies), all refs, an independent secret-pattern list, and
the deletion census — each also run by the builder before being recorded here, because a
carried claim is how C-45 and C-50 happened.

## The commands, verbatim, so this review is re-runnable

```
git rev-list --count HEAD
git log --format="%an <%ae> | %cn <%ce>" | sort -u
git log --diff-filter=D --name-only --format=""
git rev-list --objects --all | git cat-file --batch-check="%(objecttype) %(objectsize) %(rest)"
git grep -I -E "ghp_[A-Za-z0-9]{20}|AKIA[0-9A-Z]{16}|BEGIN [A-Z ]*PRIVATE KEY|xox[bp]-|api_key\s*=|Bearer [A-Za-z0-9_\-\.]{20}" $(git rev-list --all)
git log --diff-filter=A --name-only --format="" -- "*.pdf"
git grep -l "C:\Users\mohds" $(git rev-list --all)
git grep -l -F 'C:\' HEAD
git grep -i "gmail\|saifhussain@" $(git rev-list --all)
git log --all --format="%H %B"   (swept with the same patterns)
git log -p --all -- demo/full_chain/
git log --all --name-only --format="" -- "*.key"
git for-each-ref --format="%(refname)"
git log --reverse --format="%h %s"   (all 82 subjects, read)
```

## Close

Every finding above was ruled by the director before this reading was written; the reading
records those rulings, and nothing in it blocks publication. **O-28's close is the director's
read of this document** — R3.2 gates everything public on that close, and the repository going
public is a separate explicit word after it. D-46's ruled order then governs: public →
rehearsal candidate → tag and publish → ROOST pull request.
