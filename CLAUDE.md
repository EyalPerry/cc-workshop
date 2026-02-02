# TaskFlow Scheduler

## Overview
A task/job scheduling application built with FastAPI, asyncpg, and Pydantic v2. Manages job lifecycle including creation, scheduling, dependency resolution, retry logic, and state transitions.

## Key Components
- `src/taskflow/` -- Main application package. Sub-packages:
  - `models/` -- Pydantic domain models, API schemas, and internal types.
  - `logic/` -- Pure business logic (cycle detection, dependency satisfaction, scheduling, retry, state machine, cascading updates).
  - `db/` -- Database connection pool management (asyncpg).
  - `validation/` -- Input validation logic.
- `test/` -- Test suite:
  - `unit/` -- Unit tests for isolated logic.
  - `it/` -- Integration tests using testcontainers (e.g., PostgreSQL pool lifecycle tests).
  - `fixtures/` -- Shared pytest fixtures.
  - `utils/` -- Shared test utilities.
- `scripts/` -- Project scripts for setup, linting, testing, and building.

## Usage Instructions
- Run `./scripts/setup.sh` to install dependencies.
- Run `./scripts/test.py` to execute the test suite.
- Run `./scripts/lint.py` to lint source code.
- Run `./scripts/build.py` to build a Docker image.

## Dependencies
- FastAPI -- REST backend.
- asyncpg -- Async PostgreSQL driver and connection pooling.
- pydantic v2 -- Data modeling and validation.
- alembic -- Database migrations.
- pytest / testcontainers -- Testing infrastructure.
