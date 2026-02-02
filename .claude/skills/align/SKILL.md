---
name: align
description: Use this skill proactively whenever source code files are changed or created.
---

<extremely-important>
- detect changed files: `git status --short`
- Run the lint script on all changed source code files (whether commite).
- You **MUST ALWAYS** Evaluate all changed source code files agains all applicable rules in `.claude/rules/` folder hierarchy. (if no frontmatter is present in a rule file, assume that it applies to all source code files). fix any violations found immediately.

## Success Criteria

- If tests fail, do not fix any issues without explicit user confirmation that this is something they'd like to tackle right now.
- Present a report detailing the actions taken, issues found, and any user decisions required.
- always evaluate against all rules in the `.claude/rules/` folder hierarchy, based on frontmatter metadata if present.

</extremely-important>
