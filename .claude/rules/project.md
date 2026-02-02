<extremely-important>

## Project Scripts
**NON-NEGOTIABLE**: You **MUST ALWAYS** use the project scripts for the tasks which they cover. **NON-COMPLIANCE** with this directive is **UNACCEPTABLE**.
- All Scripts live under `scripts/`.
- All scripts are executable, run them using `./scripts/<script-name>`.
- `setup`: Installs all project deps required for local development (bash script).
- `install.py`: Installs dependencies and creates a virtual environment (called by `setup` internally).
- `lint.py`: identify and fix some of the linting errors. support running on specific files when possible.
- `test.py`: Run tests.  never run tests using any other method. **NON-COMPLIANCE** with this directive is **UNACCEPTABLE**.
- `build.py`: builds a docker image of the solution
- The same scripts are used in CI/CD pipelines to ensure consistency between local and remote runs.

## Source Code
files that qualify as source code match the following patterns:
- `src/` source code lives here
- `test/` tests live here. tests are also source code
- `scripts/` project specific script live here
- `.claude/**/*.py` claude code specific scripts live here

## Source Code to Test Mapping
a source code file `src/<path>/<file>.py`  maps to `test/<type>/<path>/<file>.py` or `test/<type>/<path>/<file>`, where
- `<type>` is the test type / kind.
- <path> is the same relative path under `src/` and `test/<type>/`
- <file> is the same file name without any suffixes
- if a file contains code that is complex enough, tests may be split into multiple test suites under a `test/<type>/<path>/<file>` folder

## Tech Stack

- FastAPI for REST backend
- asyncpg for Postgres access
- pydantic v2 for data modeling & validation
- alembic for database migrations

### Testing
- use `pytest` as the testing framework.
- use `unittest` MagicMock for mocking.
- testcontainers for infra dependencies / e2e tests.

</extremely-important>
