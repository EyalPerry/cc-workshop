---
name: align
description: Use this skill proactively whenever source code files change.
---

Whenever you are done with your turn and you have changed source code files, ask the user if he wants to cleanup.
If they don't, terminate and perform no further action.
if they do, perform the following actions:
  - Run the lint script on all changed source code files.
  - Align all source code changes according to rules in `.claude/rules/**/*.*`.
  - Run all tests related to changed files. DO NOT FIX ANY ISSUES WITHOUT USER CONFIRMATION.

<extremely-important>

## Success Criteria

- It is **UNACCEPTABLE** to perform any action stated above without explicit user confirmation to cleanup.
- You **MUST ALWAYS** terminate and perform no further action if the user does not explicitly ask for cleanup.
- If tests fail, do not fix any issues without explicit user confirmation that this is something they'd like to tackle right now.
- Present a report detailing the actions taken, issues found, and any user decisions required.

</extremely-important>
