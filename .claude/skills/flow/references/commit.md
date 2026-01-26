# Commit

**NON-NEGOTIABLE:** You **MUST ALWAYS** follow these steps:
- determine target files using `git diff HEAD`
- create a commit message based on target files using `./references/changes.md`.
- use the `scripts/git_commit.py "<commit_message>"` script.

## Success Criteria
- align skill processed only the source code files (if any).
- git_commit runs and terminates without error.
- Commit message accurately reflects changes according to `./changes.md` standards and the files under review.
- **NON-NEGOTIABLE:** do not use git commands directly. always use the provided script. **NON-COMPLIANCE** with this directive is **UNACCEPTABLE**.
