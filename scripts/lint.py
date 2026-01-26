#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["typer>=0.9.0,<1"]
# ///
# pyright: reportMissingImports=false
# pyright: reportMissingModuleSource=false
"""Lint script that runs ruff format, ruff check, and pyright on Python files.

Usage:
    ./lint.py [file1.py file2.py ...]

If no files are provided, defaults to linting src/.

Exit codes:
- 0: Success (all tools passed)
- 1: Lint errors found
"""

import subprocess
from pathlib import Path
from typing import Annotated

import typer

# Lint commands to run on each file
LINT_COMMANDS: list[tuple[str, list[str]]] = [
    ("format", ["uvx", "ruff", "format", "{file}"]),
    ("lint", ["uvx", "ruff", "check", "--fix", "{file}"]),
    ("type check", ["uvx", "pyright", "{file}"]),
]


def run_lint_on_file(path: Path) -> list[str]:
    """Run all lint commands on a single file.

    Args:
        path: Path to the Python file to lint.

    Returns:
        List of error messages (empty if all passed).
    """
    errors: list[str] = []

    for name, cmd_template in LINT_COMMANDS:
        cmd = [arg.replace("{file}", str(path)) for arg in cmd_template]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)  # noqa: S603

        if result.returncode != 0:
            output = (result.stdout + result.stderr).strip()
            if output:
                errors.append(f"{name} (exit {result.returncode}):\n{output}")

    return errors


def lint_paths(paths: list[Path]) -> list[str]:
    """Lint Python files or directories and return errors.

    Args:
        paths: List of file or directory paths to lint.

    Returns:
        List of error messages (empty if all passed).
    """
    all_errors: list[str] = []
    for path in paths:
        if not path.exists():
            continue
        if path.is_file() and path.suffix != ".py":
            continue
        all_errors.extend(run_lint_on_file(path))
    return all_errors


def main(
    file_paths: Annotated[
        list[Path] | None,
        typer.Argument(help="Files or directories to lint"),
    ] = None,
) -> None:
    """Run linters (ruff format, ruff check, pyright) on Python files."""
    if not file_paths:
        file_paths = [Path("src")]

    errors = lint_paths(file_paths)

    if errors:
        typer.echo("\n\n".join(errors), err=True)
        raise typer.Exit(1)

    raise typer.Exit(0)


if __name__ == "__main__":
    typer.run(main)
