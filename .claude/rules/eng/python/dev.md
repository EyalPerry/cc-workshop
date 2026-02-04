---
path: *.py
---
# Python Development Guidelines

## Dependency Management
- **NON-NEGOTIABLE:** Add dependencies only using `uv add <dep>`. for dev dependencies use `uv add --group=dev <dep>`. this ensures `uv.lock` and `pyproject.toml` stay aligned. editing these files directly or using pip is **UNACCEPTABLE**.
- Always specify exclusive upper boundary major version, e.g. `library-name>=z.x.y,<z+1` (z is major version, z+1 is next version which is excluded)

## Type Safety
- Use dataclasses or pydantic BaseModel: never define constructors manually.

## Modules / Packages
1. **`src/` is NOT a module** - Never create `src/__init__.py`; `src/` is just a source directory.
2. **Create `__init__.py` files that export all symbols** - Each package under `src/` must have an `__init__.py` that exports its public API
3. **When adding a file, export it from all ancestor `__init__.py` files** - Export from the immediate parent's `__init__.py` and propagate up through all ancestor `__init__.py` files (stopping before `src/`)
4. **Never import from files directly** - Always import from folder modules (packages), not individual files
5. **Never access nested modules directly** - The containing folder will re-export nested modules; import from the parent package instead (e.g., `from models import nom` not `from models.nom import engine`)
6. **Don't import from `src`** - Modules inside `src/` are directly importable; use `from models import X` not `from src.models import X`
7. **Import sibling modules using relative imports** - Use `.` for same-level imports (e.g., `from .sibling_module import foo`)
8. **Never use `..` for parent imports** - Instead, use absolute imports with the full module path
9. **Use explicit full module paths for global imports** - Use the full module path like `from models import X` or `from functions import Y`, not just the immediate parent
10. **Avoid circular imports** - Structure code to prevent circular dependencies between modules; refactor into separate modules if needed.
11. **Keep imports organized** - Group imports into standard library, third-party, and local modules, with a blank line between each group.
12. **Sort imports alphabetically within groups** - This improves readability and maintainability.
13. **Import Second Level Local Modules** - `from <first-level>.<second-level> import <symbol>` is acceptable for local modules. Importing deeper than second level is **UNACCEPTABLE**.
14. **Do not rely on test modules in src modules** - Importing from test modules into src modules is **UNACCEPTABLE**.
16. **Keep imports short** - if importing > 3 symbols from a module, import the module instead (e.g. `import pyspark.sql.functions as f`, not `from pyspark.sql.functions import col, lit, when, array`).
17. **Import typing module as t** - Always import typing module as t, and use it. never import symbols from that module.
