---
path: {src,test,tests}/**/*.*
---
# Clean Code

## General
- dont write one line wrappers functions that simply invoke another function without adding any value. inline such calls instead.
- prefer composition over inheritance.
- prefer delegation over inheritance.

## Functions
- A Function must not exceed 50 lines of code. If it does, refactor it into smaller functions.
- When a function exceeds 10 lines of code, break it into logical sections separated by a blank line and a descriptive comment.
- A function must have at most 4 parameters. If more are needed, group them into an object or data structure.
- A Function must do one thing only. If it does more than one thing, refactor it into smaller functions.
- Prefer pure functions. push side effects to the edges (first and last lines of code)- even if implicit.
- The Function name must clearly describe what the function does.
- Private functions must be prefixed with an underscore (_). If the language supports it, use visibility modifiers (e.g., private, protected) accordingly.
- Private Functions MUST NOT have a docstring. Instead, use clear and descriptive names.
- Public functions must have docstrings which describe
  - The function's purpose, parameters, return values, raised errors and side effects.
  - The business functionality the function implements.

## Keyword Arguments
**NON-NEGOTIABLE**: You **MUST ALWAYS** use keyword arguments when calling functions (except for javascript). Positional arguments are **UNACCEPTABLE**. **NON-COMPLIANCE** with this directive is **UNACCEPTABLE**.

## Type Safety
- **NON-NEGOTIABLE:** - always use type hints / type annotations in dynamic languages which support it. **NON-COMPLIANCE** with this directive is **UNACCEPTABLE**.
- Use typescript- never javascript. zealously use type hints in python **NON-COMPLIANCE** with this directive is **UNACCEPTABLE**.
- whenever using generic types, always specify ALL generic type arguments. (e.g. `dict[str, float]` instead of just `dict`).
- always specify a return type from functions: None / Void if does not return anything.

# Dependency Management
- You must use dependencies which are
- You must only choose dependencies that meet the following criteria
  - Actively developed / maintained (at most 6 months since last release)
  - Are not deprecated or marked for end-of-life / maintenance mode.
  - Maintained by well known organizations (for or non profit, e.g. Apache, Linux Foundation, CNCF, etc or alternatively Akamai, Meta, Google, Microsoft etc)
  - Well established and mature.
  - Have an active community and user base according to public metrics (e.g. GitHub stars, forks, issues, StackOverflow questions, etc)
