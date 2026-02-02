#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["typer>=0.9.0,<1"]
# ///
# pyright: reportMissingImports=false
# pyright: reportMissingModuleSource=false
"""Run pytest with various options."""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Annotated

import typer

SCRIPTS_DIR = Path("scripts")


def clean_pycache() -> None:
    """Remove all __pycache__ directories."""
    for pycache in Path().rglob("__pycache__"):
        shutil.rmtree(pycache, ignore_errors=True)


def needs_docker_build(targets: list[str]) -> bool:
    """Check if any target needs a Docker image build.

    Docker image build is required only for:
    - test/ (all tests, which includes e2e)
    - test/e2e (end-to-end tests)
    - test/fr (functional regression tests)
    """
    build_prefixes = ("test/e2e", "test/fr")
    return any(
        target == "test/" or target.startswith(build_prefixes) for target in targets
    )


def needs_docker_image_arg(targets: list[str]) -> bool:
    """Check if any target needs the --image_name pytest arg.

    Required for e2e and fr tests that reference the built image.
    """
    image_prefixes = ("test/e2e", "test/fr")
    return any(
        target == "test/" or target.startswith(image_prefixes) for target in targets
    )


def build_docker_image(image_name: str) -> None:
    """Build Docker image by invoking the build script."""
    build_script = SCRIPTS_DIR / "build.py"
    cmd = ["uv", "run", "--script", str(build_script), "--image-name", image_name]

    result = subprocess.run(cmd, check=False)  # noqa: S603
    if result.returncode != 0:
        typer.echo("Docker build failed", err=True)
        raise typer.Exit(1) from None


def normalize_target(arg: str) -> str:
    """Normalize test target path."""
    # Handle "test" as "run all tests"
    if arg == "test":
        return "test/"

    # Prepend test/ if needed
    if not arg.startswith("test/"):
        return f"test/{arg}"

    return arg


def main(
    targets: Annotated[
        list[str] | None,
        typer.Argument(help="Test targets (e.g., unit, it/test_foo.py::test_bar)"),
    ] = None,
    strict: bool = typer.Option(
        False,
        "--strict",
        help="Run with --runxfail to fail on expected failures",
    ),
    image_name: str = typer.Option(
        "example/app:latest",
        "--image-name",
        "-i",
        envvar="IMAGE_NAME",
        help="Docker image name for testing",
    ),
    parallel: int = typer.Option(
        4,
        "--parallel",
        "-n",
        help="Number of parallel workers (1 to disable)",
    ),
) -> None:
    """Run pytest with various options."""
    # Normalize targets
    normalized_targets: list[str] = (
        [normalize_target(arg) for arg in targets] if targets else ["test/"]
    )

    # Build Docker image if needed (skip in CI)
    is_ci = os.environ.get("CI", "").lower() == "true"
    if needs_docker_build(normalized_targets) and not is_ci:
        build_docker_image(image_name)

    # Build pytest args
    pytest_args: list[str] = ["-v", "--tb=long"]

    # Add image_name arg for e2e/fr tests
    if needs_docker_image_arg(normalized_targets):
        pytest_args.append(f"--image_name={image_name}")

    # Strict mode
    if strict:
        pytest_args.append("--runxfail")

    # Parallelism - disable in CI to avoid Spark gateway conflicts
    if not is_ci and parallel > 0:
        pytest_args.extend(["-n", str(parallel)])

    # Clean pycache
    clean_pycache()

    # Build command
    cmd = [
        "uv",
        "run",
        "--env-file",
        "test.env",
        "pytest",
        *pytest_args,
        *normalized_targets,
    ]

    typer.echo(f"🧪 Running Tests: {' '.join(normalized_targets)}")

    result = subprocess.run(cmd, check=False)  # noqa: S603
    raise typer.Exit(result.returncode)


if __name__ == "__main__":
    typer.run(main)
