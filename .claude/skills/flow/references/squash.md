# Squash

You **MUST ALWAYS** follow these steps:

1. Determine the number of commits to squash (n):
   - Default: 2
   - If user specifies a number, use that value
2. Read the messages of the last n commits using `git log -<n> --format='%B'`
3. Generate a unified commit message that merges all messages from the squashed commits, consolidating duplicate categories using `./references/changes.md`.
4. Invoke the script: `scripts/git_squash.py "<message>" <n>`

## Success Criteria
- The git_squash script terminates without error.
- The unified message accurately reflects all changes from the squashed commits.
- **NON-NEGOTIABLE:** do not use git commands directly. always use the provided script. **NON-COMPLIANCE** with this directive is **UNACCEPTABLE**.
