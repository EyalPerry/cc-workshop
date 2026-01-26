#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["GitPython>=3.1,<4", "typer>=0.15,<1"]
# ///
# pyright: reportMissingImports=false
# pyright: reportMissingModuleSource=false
"""Squash all branch commits into one using a provided commit message."""

import typing as t

import git
import typer


def _get_default_branch(repo: git.Repo) -> str:
    """Detect the default branch (main or master)."""
    for branch_name in ["main", "master"]:
        if branch_name in [ref.name for ref in repo.refs]:
            return branch_name

    typer.echo("ERROR: Could not find main or master branch.", err=True)
    raise typer.Exit(1)


def main(
    message: t.Annotated[
        str, typer.Argument(help="Commit message for compacted commit", min=1)
    ],
) -> None:
    """Squash all branch commits into one by resetting to default branch."""
    repo = git.Repo(".")

    if repo.head.is_detached:
        typer.echo("ERROR: HEAD is detached. Cannot compact.", err=True)
        raise typer.Exit(1)

    default_branch = _get_default_branch(repo)
    current_branch = repo.active_branch.name

    if current_branch == default_branch:
        typer.echo("ERROR: Cannot compact the default branch.", err=True)
        raise typer.Exit(1)

    typer.echo(f"Compacting commits from {current_branch} onto {default_branch}...")

    # Soft reset to default branch and create single commit
    repo.git.reset("--soft", default_branch)
    repo.git.commit("-m", message)

    # Check if origin remote exists
    if "origin" not in [r.name for r in repo.remotes]:
        typer.echo("No 'origin' remote configured. Skipping push.")
        typer.echo(f"Compacted commit created:\n{message}")
        raise typer.Exit(0)

    # Check if branch has upstream tracking
    tracking_branch = repo.active_branch.tracking_branch()

    try:
        if tracking_branch is None:
            typer.echo(f"Publishing {current_branch} to origin (force)...")
            repo.git.push("--force", "-u", "origin", current_branch)
        else:
            typer.echo(f"Force pushing to {tracking_branch}...")
            repo.git.push("--force")
    except git.GitCommandError as e:
        typer.echo(f"Push failed: {e}", err=True)
        raise typer.Exit(1) from None

    typer.echo(f"Compacted commit created and pushed:\n{message}")


if __name__ == "__main__":
    typer.run(main)
