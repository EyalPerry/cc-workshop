<extremely-important>

# Understand the Requirements
**NON-NEGOTIABLE**: You **MUST ALWAYS** read every file in the `specs` folder before starting any task. **NON-COMPLIANCE** with this directive is **UNACCEPTABLE**.

# Git
**NON-NEGOTIABLE**: You **MUST ALWAYS** use the flow skill for all git related operations supported by this skill. using git commands directly for operations supported by this skill is **UNACCEPTABLE**.

# Running Scripts

**NON-NEGOTIABLE**: You **MUST ALWAYS** Always run scripts relative to the project root AS WELL AS their path inside the project root.
Running scripts by specifying the absolute path**UNACCEPTABLE**.

# Evolution of Code
**NON-NEGOTIABLE**: You **MUST ALWAYS** Always use the align skill after making changes to source code (creating new files, removing them, or modifying existing ones). following that, invoke the doc agent. **NON-COMPLIANCE** with this directive is **UNACCEPTABLE**.

# Extended Planning
You **MUST ALWAYS** produce a detailed implementation roadmap as part of any plan you make such that each step in the roadmap is:
- **NON-NEGOTIABLE**: self contained (no partial implementation of a class or function)
- **NON-NEGOTIABLE**: testable (able to be verified as correct or incorrect)
- **NON-NEGOTIABLE**: builds on prior steps in order to achieve the final goal.
- **NON-NEGOTIABLE**: contains the names and responsibilities of classes / standalone functions to be implemented / modified in that step. no code is to be written in the plan.
- **NON-NEGOTIABLE**: contains no more than 100 lines of code (altered / replaced lines count as well, deleted lines don't)
- **NON-NEGOTIABLE**: contains a detailed test plan, including all test kinds which can be implemented at that step. each test plan must contain all of the tests you are going to implement for that step, detailing all tests for each applicable kind.
- **NON-NEGOTIABLE**: a file system path for each class / function to be implemented / modified in that step.
- **NON-NEGOTIABLE**: explain the reasoning behind each change, deletion and addition.
**NON-COMPLIANCE** with this directive is **UNACCEPTABLE**.

- **NON-NEGOTIABLE**: include a file system layout of the final solution, showing all files to be created / modified / deleted.

**NON-NEGOTIABLE**: You **MUST ALWAYS** create / overwrite PLAN.md in the project root with this plan, and update it as you iterate on it with the user. PLAN.md must always contain the FULL plan with all above details. **NON-COMPLIANCE** with this directive is **UNACCEPTABLE**.

# Paced Implementation
Whenever you work on such a plan, you **MUST ALWAYS** follow the roadmap step by step, and **MUST NOT** deviate from it under any circumstance.

On each turn, you **MUST ALWAYS** create three kinds of tasks:
1) implement phase and iterate with user until they are satisfied. **IMPORTANT**: do not move on to the next task until the user explicitly confirms they are satisfied.
2) run align skill after each iteration with the user where code changes were made. do this only once the user is satisfied with the implementation of the current phase.
3) test phase: run the tests for the entire solution. do this once just before moving to the next phase. if any test fails, you **MUST ALWAYS** present a plan to the user which explains in detail how to fix the issues and iterate with the user until they are satisfied, the fix is applied and all tests pass. It is **UNACCEPTABLE** to move on to the next phase if any test is failing.
3) use the doc subagent: do this once just before moving to the next phase.
At each phase's implementation, you **MUST ALWAYS** create the above three tasks and only mark them as completed at the appropriate time. always display these three tasks to the user. all of these steps must not be paralellized. when running one, do not run the other in parallel. **NON-COMPLIANCE** with this directive is **UNACCEPTABLE**.

You must not proceed to the next step / phase until the current one is fully completed, and you have verified and the user has acknowledged the completion of the current step to their satisfaction. You MUST ALWAYS ask for the user's explicit permission before moving on to the next phase. consent given for one stage does not carry over into the next one.**NON-COMPLIANCE** with this directive is **UNACCEPTABLE**.

**NON-NEGOTIABLE**At each turn, before you write a single line of coding using any library, you **MUST ALWAYS** use context7. **NON-COMPLIANCE** with this directive is **UNACCEPTABLE**.

Once the user has acknowledged the completion of the current step to their satisfaction, you **MUST ALWAYS** commit the changes before moving on to the next step / phase - but only after the doc agent has finished running. consent given for one stage does not carry over into the next one- so you must ask the user if they are ready to proceed to the next phase after performing the commit. **NON-COMPLIANCE** with this directive is **UNACCEPTABLE**.



</extremely-important>
