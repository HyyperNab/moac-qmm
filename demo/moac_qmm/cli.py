"""CLI interface for MOAC QMM.

Run simulations, homeostasis optimization and neural PK prediction from
JSON telemetry files. All stochastic components are seeded via
``--seed`` for reproducible runs.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.table import Table

from moac_qmm import QMMEngine, StableHomeostasisOptimizer, __version__

console = Console()


def _load_json(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _install_logging(quiet: bool) -> None:
    level = logging.WARNING if quiet else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True, show_path=False)],
    )


def _render_events(events: list[dict[str, Any]]) -> None:
    table = Table(title="Phase Trace", show_lines=False, expand=False)
    table.add_column("Phase", style="cyan", justify="right")
    table.add_column("Title", style="bold")
    table.add_column("Detail", overflow="fold")
    for event in events:
        table.add_row(
            str(event["phase"]),
            event["title"],
            "\n".join(event["lines"]) or "-",
        )
    console.print(table)


@click.group()
@click.version_option(version=__version__, prog_name="moac-qmm")
def main() -> None:
    """MOAC QMM — Strata-Oblivion Kernel. Medical decision engine."""


@main.command()
@click.option(
    "--telemetry",
    "-t",
    required=True,
    type=click.Path(exists=True),
    help="Path to JSON telemetry file",
)
@click.option("--output", "-o", type=click.Path(), default=None, help="Save results to JSON file")
@click.option(
    "--seed",
    "-s",
    type=int,
    default=42,
    show_default=True,
    help="RNG seed for deterministic Monte Carlo",
)
@click.option("--quiet", "-q", is_flag=True, help="Suppress phase trace output")
def run(telemetry: str, output: str | None, seed: int, quiet: bool) -> None:
    """Run the full 29-dimensional tensor collision."""
    _install_logging(quiet)
    data = _load_json(telemetry)

    console.print(
        Panel.fit(
            "[bold red]⚠️  NOT A MEDICAL DEVICE — Research/Educational only[/bold red]",
            border_style="red",
        )
    )

    engine = QMMEngine(data, seed=seed)
    result = engine.execute()

    if not quiet:
        _render_events(result.get("events", []))

    if "hash" in result:
        console.print(
            Panel.fit(
                f"[bold green]RAGNAR HASH: {result['hash']}[/bold green]",
                border_style="green",
            )
        )

    if output:
        Path(output).write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
        console.print(f"[green]Results saved to {output}[/green]")

    if "error" in result:
        console.print(f"[red]Engine aborted: {result['error']}[/red]")
        sys.exit(1)


@main.command()
@click.option(
    "--telemetry",
    "-t",
    required=True,
    type=click.Path(exists=True),
    help="Path to JSON telemetry file",
)
def optimize(telemetry: str) -> None:
    """Calculate the stable homeostasis vector (prescriptions)."""
    data = _load_json(telemetry)

    optimizer = StableHomeostasisOptimizer()
    prescriptions = optimizer.calculate_optimal_vector(data)

    console.print(
        Panel.fit(
            "[bold green]STABLE HOMEOSTASIS VECTOR[/bold green]",
            border_style="green",
        )
    )
    if not prescriptions:
        console.print("No prescriptions required — telemetry already stable.")
        return
    for category, details in prescriptions.items():
        console.print(f"\n[bold cyan]{category}[/bold cyan]")
        if isinstance(details, dict):
            for k, v in details.items():
                if isinstance(v, list):
                    for item in v:
                        console.print(f"  • {item}")
                else:
                    console.print(f"  {k}: {v}")


@main.command()
@click.option(
    "--features",
    "-f",
    required=True,
    type=click.Path(exists=True),
    help="Path to JSON features file",
)
@click.option(
    "--seed",
    "-s",
    type=int,
    default=42,
    show_default=True,
    help="RNG seed (affects trained-model MC dropout)",
)
def predict(features: str, seed: int) -> None:
    """Run neural PK prediction (heuristic fallback when untrained)."""
    from moac_qmm.deep_learning import NeuralPKPredictor

    data = _load_json(features)
    predictor = NeuralPKPredictor(seed=seed)
    result = predictor.predict(data)

    console.print(
        Panel.fit(
            "[bold magenta]NEURAL PK PREDICTION[/bold magenta]",
            border_style="magenta",
        )
    )
    for k, v in result.items():
        console.print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
