#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["docker>=7.0.0,<8", "typer>=0.9.0,<1"]
# ///
# pyright: reportMissingImports=false
# pyright: reportMissingModuleSource=false
"""Build Docker image for the application."""

from pathlib import Path

import docker
import typer


def main(
    image_name: str = typer.Option(
        "app:latest",
        "--image-name",
        "-i",
        envvar="IMAGE_NAME",
        help="Docker image name and tag",
    ),
) -> None:
    """Build Docker image with Python version from .python-version file."""
    dockerfile = "Dockerfile"
    context = "."

    # Normalize image name to lowercase
    image_name = image_name.lower()

    # Read Python version from .python-version file
    python_version_file = Path(".python-version")
    if not python_version_file.exists():
        typer.echo("Error: .python-version file not found", err=True)
        raise typer.Exit(1)

    python_version = python_version_file.read_text().strip()

    typer.echo(f"🐳 Building Docker Image: {image_name}")
    typer.echo(f"   Python version: {python_version}")

    client = docker.from_env()

    try:
        image, build_logs = client.images.build(
            path=context,
            dockerfile=dockerfile,
            tag=image_name,
            buildargs={"PYTHON_VERSION": python_version},
            rm=True,
        )

        for log in build_logs:
            if isinstance(log, dict) and "stream" in log:
                stream = str(log["stream"]).strip()
                if stream:
                    typer.echo(stream)
            elif isinstance(log, dict) and "error" in log:
                typer.echo(f"ERROR: {log['error']}", err=True)
                raise typer.Exit(1) from None

        typer.echo(f"\n✅ Successfully built image: {image_name}")
        typer.echo(f"   Image ID: {image.id}")

    except docker.errors.BuildError as e:  # pyright: ignore[reportAttributeAccessIssue]
        typer.echo(f"Build failed: {e}", err=True)
        raise typer.Exit(1) from None
    except docker.errors.APIError as e:  # pyright: ignore[reportAttributeAccessIssue]
        typer.echo(f"Docker API error: {e}", err=True)
        raise typer.Exit(1) from None


if __name__ == "__main__":
    typer.run(main)
