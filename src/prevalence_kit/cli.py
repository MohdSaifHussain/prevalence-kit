"""The six verbs.

    plan -> sample -> ingest-labels -> estimate -> verify -> emit-report

Exit codes are the contract, because that is what the director's exit checklist
reads and what a shell script downstream will branch on:

    0   the step succeeded, or `verify` found nothing wrong
    2   a Refusal -- the evidence failed a check. The reason code is printed
        first, on its own line, so `prevalence-kit verify | head -1` is useful.
    1   anything else, which is a bug in this tool rather than a problem with
        the evidence, and is reported as such.

Two exit codes for two different situations, deliberately. A tool that returns
the same non-zero for "your ledger was edited" and "I crashed" makes the
operator debug the wrong thing.
"""

from __future__ import annotations

import functools
import sys
from collections.abc import Callable
from pathlib import Path
from typing import NoReturn

import click

from . import __version__
from . import report as report_mod
from .coverage import NOTICE_THRESHOLD
from .errors import Refusal
from .plan import Plan
from .run import Workspace, do_estimate, do_ingest, do_plan, do_sample
from .verify import summarise, verify_run

EXIT_OK = 0
EXIT_BUG = 1
EXIT_REFUSED = 2

run_option = click.option(
    "--run",
    "run_dir",
    type=click.Path(path_type=Path),
    default=Path("run"),
    show_default=True,
    help="The run directory. One measurement per directory.",
)
plan_argument = click.argument("plan_path", type=click.Path(exists=True, path_type=Path))


_ENVIRONMENT_CAUSE: dict[type[OSError], str] = {
    PermissionError: "This user cannot read or write that path.",
    IsADirectoryError: "That path is a directory and a file was expected.",
    NotADirectoryError: "Part of that path is a file, so it cannot contain anything.",
    FileNotFoundError: "That path is not there, or a directory above it is not.",
    FileExistsError: "That path already exists and is not what was expected there.",
}
"""Named causes, in the operator's terms rather than the exception's.

**The classification is by `OSError` with a filename, not by this table.** The
table only supplies a better sentence where one is known; anything else gets a
generic line and is still classified. Keying the *classification* off this dict
would make it a list to remember to extend, which is the shape V-15 and D-23
are both about -- and the platforms disagree about which subclass they raise
for the same condition, so a list would be wrong somewhere by construction.
Asking for a directory under a regular file raises `NotADirectoryError` on
Linux and `FileExistsError` on Windows; both are the same operator mistake.
"""

_UNKNOWN_CAUSE = "The filesystem refused that path."


def _environment_cause(exc: OSError) -> str:
    for kind, line in _ENVIRONMENT_CAUSE.items():
        if isinstance(exc, kind):
            return line
    return _UNKNOWN_CAUSE


def guard[**P](fn: Callable[P, None]) -> Callable[P, None]:
    """Turn a Refusal into a named exit, and anything else into an honest one.

    Three outcomes, not two:

    * a **Refusal** -- the evidence failed a check and the operator must act;
    * an **environment error** -- the filesystem said no about a path the
      operator supplied. Neither a defect here nor a problem with their data;
    * anything else -- a defect in this tool, and saying so is more useful than
      a traceback that looks like the data's fault.

    **The middle case was missing, and C-52 is what that cost.** A bind mount
    the container user could not write printed *"This is a defect in
    prevalence-kit, not a problem with your data"*, and **both halves of that
    were false**: it was the environment. The operator is then sent hunting a
    bug that does not exist -- the exact harm `docs/TRIPWIRES.md` warns about in
    TW-4's own text.

    **The internal-defect message is unchanged** for the case it was written
    for. This adds a branch in front of it; it does not soften it.
    """

    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
        try:
            fn(*args, **kwargs)
        except Refusal as refusal:
            click.echo(refusal.report(), err=True)
            sys.exit(EXIT_REFUSED)
        except OSError as exc:
            if exc.filename is None:
                # Nothing to name, so nothing an operator can act on. Falls
                # through to the internal-defect path deliberately.
                _internal_error(exc)
            click.echo(f"CANNOT USE [{type(exc).__name__}] {exc.filename}", err=True)
            click.echo(f"  {_environment_cause(exc)}", err=True)
            click.echo(
                "  What to do: check that the path exists, that it is the right "
                "kind of thing, and that this user can write to it. Running in a "
                "container? A mounted directory keeps its owner on the host -- "
                'pass --user "$(id -u):$(id -g)". See docs/SOP.md section 2.',
                err=True,
            )
            click.echo(
                "  This is your environment, not a defect in prevalence-kit and "
                "not a problem with your data.",
                err=True,
            )
            sys.exit(EXIT_BUG)
        except Exception as exc:
            _internal_error(exc)

    return wrapper


def _internal_error(exc: BaseException) -> NoReturn:
    """The message this tool has always given for a real defect, unchanged."""
    click.echo(f"INTERNAL ERROR [{type(exc).__name__}] {exc}", err=True)
    click.echo("This is a defect in prevalence-kit, not a problem with your data.", err=True)
    sys.exit(EXIT_BUG)


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, prog_name="prevalence-kit")
def main() -> None:
    """Audit-grade prevalence measurement for Trust and Safety.

    A run directory holds exactly one measurement. A new measurement is a new
    directory: that is what stops a number being chosen after the results are
    seen.
    """


@main.command()
@plan_argument
@run_option
@guard
def plan(plan_path: Path, run_dir: Path) -> None:
    """Hash the plan and open the run. No data file is touched."""
    measurement = Plan.load(plan_path)
    workspace = Workspace(run_dir)
    plan_hash = do_plan(workspace, measurement)
    click.echo(f"plan hash  {plan_hash}")
    click.echo(f"run        {run_dir}")
    click.echo("The plan is now pre-registered. Editing it will make `verify` refuse.")


@main.command()
@plan_argument
@click.argument("frame_path", type=click.Path(exists=True, path_type=Path))
@run_option
@guard
def sample(plan_path: Path, frame_path: Path, run_dir: Path) -> None:
    """Draw the sample. Deterministic under the plan's seed."""
    measurement = Plan.load(plan_path)
    drawn = do_sample(Workspace(run_dir), measurement, frame_path)
    click.echo(f"drew {len(drawn)} items from {frame_path}")

    # The design's odds of producing NO interval, said out loud before the label
    # budget is spent. Q2's reason, and the same shape as
    # CORRECTION_OUT_OF_RANGE: name the number that has to change, not just the
    # fact that something is wrong.
    #
    # STATED, not refused. RULED 2026-08-30, D-41. `expected_rate` is documented
    # as a prior that costs efficiency and never validity, and that guarantee is
    # what made it safe to require -- so a refusal driven by it would be a
    # refusal on a guess, and a pessimistic prior would block a measurement that
    # would have worked. Recording the number in the ledger as well as printing
    # it is what makes stating sufficient.
    body = Workspace(run_dir).ledger.verify()[-1].body
    odds = body.get("probability_no_interval")
    if odds is not None and float(str(odds)) >= NOTICE_THRESHOLD:
        percent = float(str(odds)) * 100.0
        click.echo("")
        click.echo(
            f"  NOTE: this design has AT LEAST a {percent:.1f}% chance of producing "
            "NO INTERVAL at all."
        )
        click.echo("  At the rates your plan declares, that share of samples this size come back")
        click.echo("  entirely negative. The design standard error is then zero and there is no")
        click.echo("  spread to build an interval from -- you would get a point estimate and a")
        click.echo("  refusal, after paying for the labels.")
        click.echo("  To lower it: raise sample_size, or raise the expected_rate of the stratum")
        click.echo("  carrying most of the sample, if the plan's rates are pessimistic.")
    click.echo(f"first three: {', '.join(drawn[:3])}")


@main.command("ingest-labels")
@plan_argument
@click.argument("labels_path", type=click.Path(exists=True, path_type=Path))
@run_option
@guard
def ingest_labels(plan_path: Path, labels_path: Path, run_dir: Path) -> None:
    """Read human labels and seal the content."""
    measurement = Plan.load(plan_path)
    labels = do_ingest(Workspace(run_dir), measurement, labels_path)
    click.echo(f"sealed {len(labels)} items and recorded their labels")
    click.echo("Content is encrypted at rest. Nothing prints it.")


@main.command()
@plan_argument
@run_option
@guard
def estimate(plan_path: Path, run_dir: Path) -> None:
    """Compute the prevalence estimate and its interval."""
    measurement = Plan.load(plan_path)
    interval = do_estimate(Workspace(run_dir), measurement)
    click.echo(f"method     {interval.method}")
    click.echo(f"estimate   {interval.point}")
    click.echo(f"95% CI     [{interval.low}, {interval.high}]")
    click.echo(f"n          {interval.n}  ({interval.positives} positive)")


@main.command()
@run_option
@click.option(
    "--plan",
    "plan_path",
    type=click.Path(path_type=Path),
    default=None,
    help="The working plan file, if it still exists. Checked as well as the sealed copy.",
)
@guard
def verify(run_dir: Path, plan_path: Path | None) -> None:
    """Re-check the whole chain. Redraws and recomputes; does not re-read."""
    checks = verify_run(Workspace(run_dir), plan_path)
    for check in checks:
        click.echo(check.line())
    click.echo("")
    click.echo(summarise(checks))


@main.command("emit-report")
@plan_argument
@run_option
@click.option("--stem", default="report", show_default=True, help="Output filename stem.")
@guard
def emit_report(plan_path: Path, run_dir: Path, stem: str) -> None:
    """Write the stamped report, in Markdown and JSON."""
    measurement = Plan.load(plan_path)
    markdown, as_json = report_mod.emit(Workspace(run_dir), measurement, stem=stem)
    click.echo(f"wrote {markdown}")
    click.echo(f"wrote {as_json}")
    click.echo("Read the Honest Limits block before quoting the number.")


if __name__ == "__main__":
    main()
