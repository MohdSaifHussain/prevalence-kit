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

import click

from . import __version__
from . import report as report_mod
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


def guard[**P](fn: Callable[P, None]) -> Callable[P, None]:
    """Turn a Refusal into a named exit, and anything else into an honest one.

    A Refusal means the evidence failed a check and the operator needs to act.
    Anything else is a defect in this tool, and saying so is more useful than a
    traceback that looks like the data's fault.
    """

    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
        try:
            fn(*args, **kwargs)
        except Refusal as refusal:
            click.echo(refusal.report(), err=True)
            sys.exit(EXIT_REFUSED)
        except Exception as exc:
            click.echo(f"INTERNAL ERROR [{type(exc).__name__}] {exc}", err=True)
            click.echo(
                "This is a defect in prevalence-kit, not a problem with your data.", err=True
            )
            sys.exit(EXIT_BUG)

    return wrapper


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
