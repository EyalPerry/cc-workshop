#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["typer>=0.9.0,<1"]
# ///
# pyright: reportMissingImports=false
# pyright: reportMissingModuleSource=false
"""Install Python dependencies using uv."""

import subprocess

import typer


def main(
    dev: bool = typer.Option(
        True,
        "--dev/--no-dev",
        help="Include dev dependencies",
    ),
) -> None:
    """Install Python dependencies using uv sync."""
    typer.echo("🐍 Installing Python dependencies")

    cmd = ["uv", "sync"]
    if dev:
        cmd.append("--dev")

    result = subprocess.run(cmd, check=False)  # noqa: S603

    if result.returncode != 0:
        typer.echo("Failed to install dependencies", err=True)
        raise typer.Exit(result.returncode)


if __name__ == "__main__":
    typer.run(main)
