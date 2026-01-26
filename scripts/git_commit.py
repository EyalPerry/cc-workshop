#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["GitPython>=3.1,<4", "typer>=0.15,<1"]
# ///
# pyright: reportMissingImports=false
# pyright: reportMissingModuleSource=false
"""Stage all changes, commit, and push to remote."""

import typing as t

import git
import typer


def main(
    message: t.Annotated[
        str,
        typer.Argument(help="Commit message"),
    ],
) -> None:
    """Stage all changes, commit, and push to remote."""
    repo = git.Repo(".")

    if repo.head.is_detached:
        typer.echo("ERROR: HEAD is detached. Cannot checkpoint.", err=True)
        raise typer.Exit(1)

    # Check for any changes (staged, unstaged, or untracked)
    if not repo.is_dirty(untracked_files=True):
        typer.echo("Nothing to commit.", err=True)
        raise typer.Exit(1)

    typer.echo("Staging all changes...")
    repo.git.add("-A")

    typer.echo("Committing...")
    repo.git.commit("-m", message)

    current_branch = repo.active_branch.name

    # Check if origin remote exists
    if "origin" not in [r.name for r in repo.remotes]:
        typer.echo("No 'origin' remote configured. Skipping push.")
        typer.echo(f"Successfully committed to {current_branch}")
        raise typer.Exit(0)

    # Check if branch has upstream tracking
    tracking_branch = repo.active_branch.tracking_branch()

    try:
        if tracking_branch is None:
            typer.echo(f"Publishing {current_branch} to origin...")
            repo.git.push("-u", "origin", current_branch)
        else:
            typer.echo(f"Pushing to {tracking_branch}...")
            repo.git.push()
    except git.GitCommandError as e:
        typer.echo(f"Push failed: {e}", err=True)
        raise typer.Exit(1) from None

    typer.echo(f"Successfully committed and pushed to origin/{current_branch}")


if __name__ == "__main__":
    typer.run(main)
