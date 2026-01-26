# Checkpoint

You **MUST ALWAYS** follow these steps:
1. Get files changed relative to default branch: `git diff --name-only <default-branch>...HEAD`
2. **NON-NEGOTIABLE:** Compile a changelog entry based ONLY on the actual diff. reating the changelog entry based on any commit messages is **UNACCEPTABLE**.
3. create the changelog entry according to guidelines in `./references/changes.md`.
4. Persist the changelog entry in CHANGELOG.md, Prepending the entry to the top of the file and specifying the branch name.
   - If the first changelog entry in the file already refers to the current branch, override it instead of adding another.
5. Run the `scripts/git_checkpoint.py "<changelog>"` script.
 
## Success Criteria
- The changelog entry is based on the actual diff against the default branch.
- The changelog entry is prepended to CHANGELOG.md, or overrides it if one exists for the current branch
- The format specified in `./references/changes.md` is respected.
- **NON-NEGOTIABLE:** do not use git commands directly. always use the provided script. **NON-COMPLIANCE** with this directive is **UNACCEPTABLE**.
