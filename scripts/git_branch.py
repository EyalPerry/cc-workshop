#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["GitPython>=3.1,<4", "typer>=0.15,<1"]
# ///
# pyright: reportMissingImports=false
# pyright: reportMissingModuleSource=false
"""Create an up to date branch with project ticket naming convention."""

import re
import typing as t

import git
import typer

MAX_DESC_LENGTH = 25


def _normalize_name(value: str) -> str:
    """Normalize and validate name."""
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    if len(normalized) > MAX_DESC_LENGTH:
        raise typer.BadParameter(
            f"Description exceeds {MAX_DESC_LENGTH} characters: "
            f"'{normalized}' ({len(normalized)} chars)"
        )
    return normalized


def _get_default_branch(repo: git.Repo) -> str:
    """Detect the default branch (main or master)."""
    for branch_name in ["main", "master"]:
        if branch_name in [ref.name for ref in repo.refs]:
            return branch_name

    typer.echo("ERROR: Could not find main or master branch.", err=True)
    raise typer.Exit(1)


def _get_stash_count(repo: git.Repo) -> int:
    """Return the current number of stash entries."""
    stash_list = repo.git.stash("list")
    return len(stash_list.splitlines()) if stash_list else 0


def _stash_changes(repo: git.Repo) -> bool:
    """Stash uncommitted changes if present. Return True if stash was created."""
    if not repo.is_dirty(untracked_files=True):
        return False

    count_before = _get_stash_count(repo)
    typer.echo("Stashing uncommitted changes...")
    repo.git.stash("-u")
    count_after = _get_stash_count(repo)

    return count_after > count_before


def _restore_stash(repo: git.Repo) -> None:
    """Pop the most recent stash entry."""
    typer.echo("Restoring stashed changes...")
    repo.git.stash("pop")


def _has_remote(repo: git.Repo) -> bool:
    """Check if any remote is configured."""
    return len(repo.remotes) > 0


def _create_branch_from_default(repo: git.Repo, branch_name: str) -> None:
    """Checkout default branch, pull latest if remote exists, create new branch."""
    default_branch = _get_default_branch(repo)

    typer.echo(f"Checking out {default_branch}...")
    repo.git.checkout(default_branch)

    if _has_remote(repo):
        typer.echo(f"Pulling latest from {default_branch}...")
        repo.git.pull()

    typer.echo(f"Creating branch: {branch_name}")
    repo.git.checkout("-b", branch_name)

    for remote in repo.remotes:
        remote_branch = f"{remote.name}/{branch_name}"
        if remote_branch in [ref.name for ref in repo.refs]:
            typer.echo(f"Branch already exists on {remote.name}, skipping publish.")
            continue
        typer.echo(f"Publishing {branch_name} to {remote.name}...")
        repo.git.push("-u", remote.name, branch_name)

    typer.echo(f"Successfully created and checked out: {branch_name}")


def _build_branch_name(
    prefix: str | None, project: str, issue_id: int, name: str
) -> str:
    """Construct the full branch name."""
    base_name = f"{project}-{issue_id}-{name}"
    return f"{prefix}/{base_name}" if prefix else base_name


def main(
    project: t.Annotated[
        str,
        typer.Option(
            "--project",
            "-P",
            help="Project key (will be uppercased)",
            callback=lambda v: v.upper(),
        ),
    ],
    issue_id: t.Annotated[
        int,
        typer.Option("--issue-id", "-i", help="Ticket ID (must be > 0)", min=1),
    ],
    name: t.Annotated[
        str,
        typer.Option(
            "--name", "-n", help="Branch name (max 25 chars)", callback=_normalize_name
        ),
    ],
    prefix: t.Annotated[
        str | None,
        typer.Option("--prefix", "-p", help="Branch prefix (e.g., feature, bugfix)"),
    ] = None,
) -> None:
    """Create a branch: [prefix/]<PROJECT>-<id>-<name>."""
    repo = git.Repo(".")
    original_branch = repo.active_branch.name
    stashed = _stash_changes(repo)
    success = False

    try:
        branch_name = _build_branch_name(prefix, project, issue_id, name)
        _create_branch_from_default(repo, branch_name)
        success = True

    finally:
        if stashed:
            if not success:
                typer.echo(f"Returning to {original_branch}...")
                repo.git.checkout(original_branch)
            _restore_stash(repo)


if __name__ == "__main__":
    typer.run(main)
