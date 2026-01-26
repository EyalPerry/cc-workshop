#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["GitPython>=3.1,<4", "typer>=0.15,<1"]
# ///
# pyright: reportMissingImports=false
# pyright: reportMissingModuleSource=false
"""Squash N commits before the latest into a single commit with the latest."""

import typing as t

import git
import typer


def main(
    message: t.Annotated[
        str, typer.Argument(help="Commit message for squashed commit", min=1)
    ],
    count: t.Annotated[
        int,
        typer.Argument(help="Number of commits before HEAD to squash into HEAD", min=1),
    ] = 1,
) -> None:
    """Squash N commits before HEAD into HEAD, resulting in one combined commit."""
    repo = git.Repo(".")

    if repo.head.is_detached:
        typer.echo("ERROR: HEAD is detached. Cannot squash.", err=True)
        raise typer.Exit(1)

    # squash N means combine HEAD with N commits before it = N+1 total commits
    total_commits = count + 1
    commits = list(repo.iter_commits(max_count=total_commits + 1))
    if len(commits) < total_commits:
        msg = f"ERROR: Need at least {total_commits} commits to squash {count}."
        typer.echo(msg, err=True)
        raise typer.Exit(1)

    # Print messages of commits being squashed
    typer.echo(f"Squashing {total_commits} commit(s) into one:")
    for i, commit in enumerate(commits[:total_commits]):
        typer.echo(f"\n--- Commit {i + 1} ---")
        typer.echo(commit.message.strip())

    typer.echo("\n" + "=" * 40 + "\n")

    repo.git.reset("--soft", f"HEAD~{total_commits}")
    repo.git.commit("-m", message)

    typer.echo(f"Squashed commit created with message:\n{message}")

    current_branch = repo.active_branch.name

    # Check if origin remote exists
    if "origin" not in [r.name for r in repo.remotes]:
        typer.echo("No 'origin' remote configured. Skipping push.")
        typer.echo(f"Successfully squashed to {current_branch}")
        raise typer.Exit(0)

    # Check if branch has upstream tracking
    tracking_branch = repo.active_branch.tracking_branch()

    try:
        if tracking_branch is None:
            typer.echo(f"\nPublishing {current_branch} to origin (force)...")
            repo.git.push("--force", "-u", "origin", current_branch)
        else:
            typer.echo(f"\nForce pushing to {tracking_branch}...")
            repo.git.push("--force")
        typer.echo(f"Successfully force pushed to origin/{current_branch}")
    except git.GitCommandError as e:
        typer.echo(f"Push failed: {e}", err=True)
        raise typer.Exit(1) from None


if __name__ == "__main__":
    typer.run(main)
