# TaskFlow Scheduler — Implementation Plan

## File System Layout (Final)

```
src/
└── taskflow/
    ├── __init__.py
    ├── config.py
    ├── models/
    │   ├── __init__.py
    │   ├── enums.py
    │   ├── retry_policy.py
    │   ├── job.py
    │   ├── requests.py
    │   ├── responses.py
    │   └── search.py
    ├── db/
    │   ├── __init__.py
    │   ├── connection.py
    │   ├── repository.py
    │   └── migrations/
    │       ├── env.py
    │       ├── script.py.mako
    │       └── versions/
    │           └── 001_initial_schema.py
    ├── services/
    │   ├── __init__.py
    │   ├── retry.py
    │   ├── dependency.py
    │   ├── scheduling.py
    │   ├── validation.py
    │   └── job_service.py
    └── api/
        ├── __init__.py
        ├── errors.py
        ├── jobs.py
        └── app.py

test/
├── unit/
│   └── taskflow/
│       ├── __init__.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── test_enums.py
│       │   ├── test_retry_policy.py
│       │   ├── test_job.py
│       │   ├── test_requests.py
│       │   └── test_search.py
│       └── services/
│           ├── __init__.py
│           ├── test_retry.py
│           ├── test_dependency_cycle.py
│           ├── test_dependency_satisfaction.py
│           ├── test_scheduling.py
│           ├── test_validation.py
│           └── test_job_service.py
├── integration/
│   └── taskflow/
│       ├── __init__.py
│       ├── db/
│       │   ├── __init__.py
│       │   ├── conftest.py
│       │   ├── test_connection.py
│       │   ├── test_repository_create_read.py
│       │   ├── test_repository_update_delete.py
│       │   └── test_repository_search.py
│       └── api/
│           ├── __init__.py
│           ├── conftest.py
│           ├── test_jobs_create_get.py
│           ├── test_jobs_update_delete.py
│           └── test_jobs_search.py
└── e2e/
    └── taskflow/
        ├── __init__.py
        └── test_job_lifecycle.py
```

---

## Phase 1: Enums and RetryPolicy Model

**Files**: `src/taskflow/__init__.py`, `src/taskflow/models/__init__.py`, `src/taskflow/models/enums.py`, `src/taskflow/models/retry_policy.py`

### `src/taskflow/models/enums.py` (~20 lines)
- `JobStatus(str, Enum)`: PENDING, READY, RUNNING, COMPLETED, FAILED, BLOCKED
- `BackoffStrategy(str, Enum)`: FIXED, LINEAR, EXPONENTIAL

### `src/taskflow/models/retry_policy.py` (~35 lines)
- `RetryPolicy(BaseModel)`: max_attempts (1-10, default 3), backoff_strategy (default EXPONENTIAL), base_delay_seconds (1-300, default 10), max_delay_seconds (1-3600, default 300)
- `@model_validator`: max_delay_seconds >= base_delay_seconds

### `src/taskflow/models/__init__.py` (~5 lines)
- Re-export all models from enums and retry_policy

### `src/taskflow/__init__.py` (empty)

### Reasoning
Foundation types used everywhere. Pydantic validators enforce SRS constraints at construction time.

### Test Plan

**Unit tests** (`test/unit/taskflow/models/test_enums.py`):
- `test_should_have_all_job_status_values_when_enum_defined`
- `test_should_have_all_backoff_strategy_values_when_enum_defined`
- `test_should_serialize_to_string_when_value_accessed`

**Unit tests** (`test/unit/taskflow/models/test_retry_policy.py`):
- `test_should_create_with_defaults_when_no_args`
- `test_should_create_with_custom_values_when_valid`
- `test_should_reject_max_attempts_below_1_when_invalid`
- `test_should_reject_max_attempts_above_10_when_invalid`
- `test_should_reject_base_delay_below_1_when_invalid`
- `test_should_reject_base_delay_above_300_when_invalid`
- `test_should_reject_max_delay_below_base_delay_when_invalid`
- `test_should_reject_max_delay_above_3600_when_invalid`

---

## Phase 2: Job Model

**Files**: `src/taskflow/models/job.py`, update `src/taskflow/models/__init__.py`

### `src/taskflow/models/job.py` (~55 lines)
- `Job(BaseModel)`: id (UUID, default_factory), name (1-255), queue (regex `^[a-zA-Z0-9_]{1,64}$`), payload (dict, ≤64KB), priority (1-10), status (default PENDING), dependencies (max 50 UUIDs, default []), retry_policy (default RetryPolicy()), created_at/updated_at (datetime UTC), attempt_count (default 0, ≥0)
- Payload validator: serialize to JSON, check `len(json_bytes) <= 65536`

### Reasoning
Central domain entity. All SRS field constraints encoded as Pydantic validators.

### Test Plan

**Unit tests** (`test/unit/taskflow/models/test_job.py`):
- `test_should_create_with_minimal_fields_when_name_and_queue_provided`
- `test_should_create_with_all_fields_when_fully_specified`
- `test_should_reject_empty_name_when_blank`
- `test_should_reject_name_over_255_chars_when_too_long`
- `test_should_reject_invalid_queue_when_special_chars`
- `test_should_reject_queue_over_64_chars_when_too_long`
- `test_should_reject_priority_below_1_when_invalid`
- `test_should_reject_priority_above_10_when_invalid`
- `test_should_reject_payload_over_64kb_when_too_large`
- `test_should_reject_dependencies_over_50_when_too_many`

---

## Phase 3: Request, Response, and Search Models

**Files**: `src/taskflow/models/requests.py`, `src/taskflow/models/responses.py`, `src/taskflow/models/search.py`, update `__init__.py`

### `src/taskflow/models/requests.py` (~25 lines)
- `JobCreateRequest(BaseModel)`: name, queue, payload (default {}), priority (default 5), dependencies (default []), retry_policy (default RetryPolicy())
- `JobUpdateRequest(BaseModel)`: all Optional — name, queue, payload, priority, dependencies, retry_policy

### `src/taskflow/models/responses.py` (~15 lines)
- `JobResponse(BaseModel)`: mirrors Job fields for API serialization
- `JobSearchResponse(BaseModel)`: items (list[JobResponse]), next_cursor (str | None), has_more (bool)

### `src/taskflow/models/search.py` (~40 lines)
- `SearchFilters(BaseModel)`: queue, status, priority_min, priority_max, created_after, created_before — all Optional
- `@model_validator`: priority_min ≤ priority_max if both set; created_after < created_before if both set
- `CursorInfo(BaseModel)`: created_at (datetime), job_id (UUID)
  - `@classmethod decode(cls, cursor: str) -> CursorInfo`: base64 decode `{iso}|{uuid}`
  - `encode(self) -> str`: base64 encode

### Reasoning
Separates API contract from domain model. Cursor encapsulates pagination logic.

### Test Plan

**Unit tests** (`test/unit/taskflow/models/test_requests.py`):
- `test_should_create_job_create_request_with_defaults_when_minimal`
- `test_should_create_job_update_request_with_partial_fields_when_some_omitted`

**Unit tests** (`test/unit/taskflow/models/test_search.py`):
- `test_should_reject_priority_range_when_min_exceeds_max`
- `test_should_reject_date_range_when_after_exceeds_before`
- `test_should_encode_and_decode_cursor_roundtrip`
- `test_should_reject_malformed_cursor_when_invalid_base64`

---

## Phase 4: Retry Calculation Service

**Files**: `src/taskflow/services/__init__.py`, `src/taskflow/services/retry.py`

### `src/taskflow/services/retry.py` (~35 lines)
- `calculate_retry_delay(*, retry_policy: RetryPolicy, attempt_number: int) -> int`: FIXED → base, LINEAR → min(base * attempt, max), EXPONENTIAL → min(base * 2^(attempt-1), max)
- `should_retry(*, job: Job) -> bool`: attempt_count < max_attempts

### Reasoning
Pure functions matching SRS formulas exactly. No side effects, trivially testable.

### Test Plan

**Unit tests** (`test/unit/taskflow/services/test_retry.py`):
- `test_should_return_base_delay_for_fixed_when_any_attempt`
- `test_should_return_linear_delay_when_multiple_attempts`
- `test_should_return_exponential_delay_when_multiple_attempts`
- `test_should_cap_at_max_for_linear_when_exceeds`
- `test_should_cap_at_max_for_exponential_when_exceeds`
- `test_should_allow_retry_when_attempts_below_max`
- `test_should_deny_retry_when_attempts_at_max`

---

## Phase 5: Dependency Service — Cycle Detection

**Files**: `src/taskflow/services/dependency.py`

### `src/taskflow/services/dependency.py` (~60 lines, this phase)
- `CycleDetectionResult(BaseModel)`: has_cycle (bool), cycle_path (list[UUID])
- `detect_cycle(*, new_job_id: UUID, new_job_dependencies: list[UUID], existing_jobs: dict[UUID, list[UUID]]) -> CycleDetectionResult`: DFS with recursion stack

### Reasoning
DFS is O(V+E). Returning cycle_path aids API error messages.

### Test Plan

**Unit tests** (`test/unit/taskflow/services/test_dependency_cycle.py`):
- `test_should_detect_self_dependency_when_job_depends_on_itself`
- `test_should_detect_two_node_cycle_when_mutual_dependency`
- `test_should_detect_three_node_cycle_when_circular_chain`
- `test_should_not_detect_cycle_when_linear_chain`
- `test_should_not_detect_cycle_when_diamond_dag`
- `test_should_not_detect_cycle_when_no_dependencies`

---

## Phase 6: Dependency Service — Satisfaction & Cascading

**Files**: Update `src/taskflow/services/dependency.py`

### Additions (~50 lines)
- `DependencyStatus(str, Enum)`: SATISFIED, WAITING, BLOCKED
- `check_dependency_satisfaction(*, dependencies: list[UUID], dependency_statuses: dict[UUID, JobStatus]) -> DependencyStatus`: empty→SATISFIED, any FAILED/BLOCKED→BLOCKED, any PENDING/READY/RUNNING→WAITING, else SATISFIED
- `find_blocked_dependents(*, failed_job_id: UUID, all_jobs: list[Job]) -> set[UUID]`: recursive DFS for PENDING dependents
- `find_ready_dependents(*, completed_job_id: UUID, all_jobs: list[Job], job_statuses: dict[UUID, JobStatus]) -> set[UUID]`: find PENDING jobs where all deps now COMPLETED

### Reasoning
Implements SRS §2.1.2, §2.5.1, §2.5.2. Pure functions.

### Test Plan

**Unit tests** (`test/unit/taskflow/services/test_dependency_satisfaction.py`):
- `test_should_return_satisfied_when_no_dependencies`
- `test_should_return_satisfied_when_all_completed`
- `test_should_return_waiting_when_any_pending`
- `test_should_return_blocked_when_any_failed`
- `test_should_find_direct_blocked_dependents_when_job_fails`
- `test_should_find_transitive_blocked_dependents_when_job_fails`
- `test_should_find_ready_dependents_when_last_dep_completes`
- `test_should_not_find_ready_when_other_deps_incomplete`

---

## Phase 7: Scheduling and Validation Services

**Files**: `src/taskflow/services/scheduling.py`, `src/taskflow/services/validation.py`

### `src/taskflow/services/scheduling.py` (~25 lines)
- `sort_jobs_by_priority(*, jobs: list[Job]) -> list[Job]`: priority DESC, created_at ASC, id ASC
- `select_next_jobs(*, ready_jobs: list[Job], running_count: int, max_concurrent: int) -> list[Job]`

### `src/taskflow/services/validation.py` (~50 lines)
- `VALID_TRANSITIONS: dict[JobStatus, set[JobStatus]]` — from SRS §2.4.1
- `validate_job_update(*, job: Job) -> None`: raise if terminal state (COMPLETED, FAILED, BLOCKED) or RUNNING
- `validate_job_deletion(*, job: Job, all_jobs: list[Job]) -> None`: raise if any job depends on it (SRS §3.3)
- `validate_state_transition(*, current: JobStatus, target: JobStatus) -> None`: check VALID_TRANSITIONS

### Reasoning
Scheduling is pure sorting. Validation centralizes business rules from SRS §3.2, §3.3, §2.4.

### Test Plan

**Unit tests** (`test/unit/taskflow/services/test_scheduling.py`):
- `test_should_sort_by_priority_desc_when_different_priorities`
- `test_should_sort_by_created_at_asc_when_same_priority`
- `test_should_sort_by_id_asc_when_same_priority_and_time`
- `test_should_select_available_slots_when_below_max`
- `test_should_select_none_when_at_max_concurrent`

**Unit tests** (`test/unit/taskflow/services/test_validation.py`):
- `test_should_allow_update_when_pending`
- `test_should_allow_update_when_ready`
- `test_should_reject_update_when_completed`
- `test_should_reject_update_when_failed`
- `test_should_reject_update_when_blocked`
- `test_should_allow_deletion_when_no_dependents`
- `test_should_reject_deletion_when_dependents_exist`
- `test_should_allow_valid_transition_pending_to_ready`
- `test_should_reject_invalid_transition_completed_to_pending`

---

## Phase 8: Config and Database Connection

**Files**: `src/taskflow/config.py`, `src/taskflow/db/__init__.py`, `src/taskflow/db/connection.py`

### `src/taskflow/config.py` (~20 lines)
- `Settings(BaseSettings)`: database_url (str), database_pool_min_size (int, default 2), database_pool_max_size (int, default 10)
- `model_config = SettingsConfigDict(env_prefix="TASKFLOW_")`

### `src/taskflow/db/connection.py` (~40 lines)
- `DatabasePool`: init with Settings, `connect()`, `disconnect()`, `get_pool() -> asyncpg.Pool`

### Reasoning
12-factor config via env vars. Pool lifecycle management prevents connection leaks.

### Test Plan

**Integration tests** (`test/integration/taskflow/db/test_connection.py`):
- `test_should_connect_when_valid_dsn`
- `test_should_execute_query_when_connected`
- `test_should_disconnect_cleanly_when_closed`
- `test_should_raise_when_pool_not_connected`

---

## Phase 9: Database Migration

**Files**: `src/taskflow/db/migrations/env.py`, `src/taskflow/db/migrations/script.py.mako`, `src/taskflow/db/migrations/versions/001_initial_schema.py`

### Migration 001 (~55 lines)
- CREATE TABLE jobs with all fields (id UUID PK, name VARCHAR(255), queue VARCHAR(64), payload JSONB, priority INT, status VARCHAR(20), dependencies UUID[], retry_policy JSONB, created_at TIMESTAMPTZ, updated_at TIMESTAMPTZ, attempt_count INT DEFAULT 0)
- Indexes: idx_jobs_status, idx_jobs_queue, idx_jobs_priority_created (priority DESC, created_at ASC), idx_jobs_created_id (created_at DESC, id ASC)

### Reasoning
Raw SQL migration gives full control. Indexes target query patterns: status filter, queue filter, priority scheduling, cursor pagination.

### Test Plan

Migration correctness verified implicitly when repository tests in Phase 10+ succeed against the schema.

---

## Phase 10: Job Repository — Create & Read

**Files**: `src/taskflow/db/repository.py`, `test/integration/taskflow/db/conftest.py`

### `src/taskflow/db/repository.py` (~80 lines this phase)
- `JobRepository.__init__(self, *, pool: asyncpg.Pool)`
- `async def create(self, *, job: Job) -> Job`: INSERT RETURNING *
- `async def get_by_id(self, *, job_id: UUID) -> Job | None`: SELECT by id
- `_row_to_job(self, *, row: asyncpg.Record) -> Job`: mapping helper

### `test/integration/taskflow/db/conftest.py`
- Fixture `db_with_schema`: runs migration on db_pool, yields pool
- Fixture `job_repository`: creates JobRepository with pool

### Reasoning
Repository encapsulates all SQL. Pydantic conversion at boundary ensures type safety.

### Test Plan

**Integration tests** (`test/integration/taskflow/db/test_repository_create_read.py`):
- `test_should_create_job_when_valid`
- `test_should_return_created_job_with_all_fields`
- `test_should_retrieve_by_id_when_exists`
- `test_should_return_none_when_id_not_found`
- `test_should_store_dependencies_array`
- `test_should_store_retry_policy_jsonb`

---

## Phase 11: Job Repository — Update & Delete

**Files**: Update `src/taskflow/db/repository.py`

### Additions (~60 lines)
- `async def update(self, *, job_id: UUID, updates: dict[str, t.Any]) -> Job`: dynamic UPDATE SET, updated_at = now()
- `async def delete(self, *, job_id: UUID) -> bool`: DELETE, return whether row existed
- `async def get_all(self) -> list[Job]`: SELECT *
- `async def get_dependency_statuses(self, *, job_ids: list[UUID]) -> dict[UUID, JobStatus]`: batch SELECT id, status WHERE id = ANY($1)
- `async def bulk_update_status(self, *, job_ids: list[UUID], status: JobStatus) -> None`: UPDATE ... WHERE id = ANY($1)

### Reasoning
Dynamic UPDATE enables partial updates. Batch queries optimize cascading operations.

### Test Plan

**Integration tests** (`test/integration/taskflow/db/test_repository_update_delete.py`):
- `test_should_update_name_when_partial`
- `test_should_update_multiple_fields`
- `test_should_update_timestamp_on_modification`
- `test_should_delete_when_exists`
- `test_should_return_false_when_deleting_nonexistent`
- `test_should_return_dependency_statuses`
- `test_should_bulk_update_status`

---

## Phase 12: Job Repository — Search & Pagination

**Files**: Update `src/taskflow/db/repository.py`

### Additions (~75 lines)
- `async def search(self, *, filters: SearchFilters, cursor: CursorInfo | None, limit: int) -> tuple[list[Job], bool]`: dynamic WHERE from filters, cursor condition `(created_at, id) < ($cursor_at, $cursor_id)`, ORDER BY created_at DESC, id ASC, LIMIT limit+1, return (jobs[:limit], len>limit)

### Reasoning
Cursor pagination avoids OFFSET performance issues. Limit+1 trick detects has_more without COUNT.

### Test Plan

**Integration tests** (`test/integration/taskflow/db/test_repository_search.py`):
- `test_should_return_all_when_no_filters`
- `test_should_filter_by_queue`
- `test_should_filter_by_status`
- `test_should_filter_by_priority_range`
- `test_should_filter_by_date_range`
- `test_should_paginate_with_limit`
- `test_should_return_next_page_with_cursor`
- `test_should_combine_multiple_filters`
- `test_should_indicate_no_more_on_last_page`

---

## Phase 13: API Error Handling

**Files**: `src/taskflow/api/__init__.py`, `src/taskflow/api/errors.py`

### `src/taskflow/api/errors.py` (~55 lines)
- `ErrorCode(str, Enum)`: VALIDATION_ERROR, NOT_FOUND, CONFLICT
- `ErrorResponse(BaseModel)`: code, message, details (dict | None)
- `TaskFlowError(Exception)`: base with code, message, details
- `NotFoundException(TaskFlowError)`, `ConflictError(TaskFlowError)`, `ValidationError(TaskFlowError)`
- `register_error_handlers(*, app: FastAPI) -> None`: exception handlers mapping to HTTP 400/404/409

### Reasoning
Structured errors match SRS §6. Exception hierarchy enables clean handler mapping.

### Test Plan

**Unit tests** (`test/unit/taskflow/api/test_errors.py`):
- `test_should_create_error_response_with_all_fields`
- `test_should_serialize_error_response_to_json`

---

## Phase 14: Job Service

**Files**: `src/taskflow/services/job_service.py`

### `src/taskflow/services/job_service.py` (~90 lines)
- `JobService.__init__(self, *, repository: JobRepository)`
- `async def create_job(self, *, request: JobCreateRequest) -> Job`: validate deps exist, detect cycles, check satisfaction → set initial status (READY if no deps or all COMPLETED, PENDING if waiting, BLOCKED if any failed), call repo.create
- `async def get_job(self, *, job_id: UUID) -> Job`: repo.get_by_id, raise NotFoundException if None
- `async def update_job(self, *, job_id: UUID, request: JobUpdateRequest) -> Job`: get, validate_job_update, if deps changed: cycle check + re-check satisfaction, repo.update
- `async def delete_job(self, *, job_id: UUID) -> None`: get, validate_job_deletion, repo.delete
- `async def search_jobs(self, *, filters: SearchFilters, cursor: CursorInfo | None, limit: int) -> tuple[list[Job], bool]`: delegate to repo

### Reasoning
Orchestration layer keeping repo and services focused. All business rules enforced before DB interaction.

### Test Plan

**Unit tests** (`test/unit/taskflow/services/test_job_service.py`) — mock repository:
- `test_should_create_with_ready_status_when_no_dependencies`
- `test_should_create_with_pending_status_when_deps_not_complete`
- `test_should_create_with_blocked_status_when_dep_failed`
- `test_should_reject_creation_when_cycle_detected`
- `test_should_get_job_when_exists`
- `test_should_raise_not_found_when_missing`
- `test_should_update_when_pending`
- `test_should_reject_update_when_terminal`
- `test_should_delete_when_valid`
- `test_should_reject_deletion_when_has_dependents`

---

## Phase 15: API Endpoints — Create & Get

**Files**: `src/taskflow/api/jobs.py`, `src/taskflow/api/app.py`

### `src/taskflow/api/jobs.py` (~40 lines this phase)
- `router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])`
- `POST ""` → 201, creates job via service
- `GET "/{job_id}"` → 200, gets job via service

### `src/taskflow/api/app.py` (~50 lines)
- `lifespan` async context manager: connect DB pool on startup, disconnect on shutdown
- `create_app(*, settings: Settings | None = None) -> FastAPI`: create app, register error handlers, include router
- `GET "/health"` → basic health check

### Reasoning
Lifespan ensures clean resource lifecycle. Factory pattern enables test configuration.

### Test Plan

**Integration tests** (`test/integration/taskflow/api/conftest.py` + `test_jobs_create_get.py`):
- Fixture: `app_client` using httpx.AsyncClient with testcontainer DB
- `test_should_create_job_when_valid_request`
- `test_should_return_400_when_invalid_name`
- `test_should_return_409_when_circular_dependency`
- `test_should_get_job_when_exists`
- `test_should_return_404_when_not_found`

---

## Phase 16: API Endpoints — Update, Delete & Search

**Files**: Update `src/taskflow/api/jobs.py`

### Additions (~55 lines)
- `PUT "/{job_id}"` → 200, update via service
- `DELETE "/{job_id}"` → 204, delete via service
- `GET ""` → 200, search with query params, cursor pagination

### Reasoning
Completes the CRUD + search API surface per SRS §5.

### Test Plan

**Integration tests** (`test/integration/taskflow/api/test_jobs_update_delete.py`):
- `test_should_update_job_when_pending`
- `test_should_return_409_when_updating_terminal_job`
- `test_should_delete_job_when_no_dependents`
- `test_should_return_409_when_job_has_dependents`

**Integration tests** (`test/integration/taskflow/api/test_jobs_search.py`):
- `test_should_search_all_when_no_filters`
- `test_should_filter_by_queue`
- `test_should_paginate_with_cursor`
- `test_should_return_empty_when_no_matches`

---

## Phase 17: E2E Tests

**Files**: `test/e2e/taskflow/test_job_lifecycle.py`

### Tests (~90 lines)
- `test_should_complete_full_lifecycle_when_dependencies_satisfied`: Create A (READY), create B→A (PENDING), complete A → B becomes READY, search for READY jobs, verify B found
- `test_should_block_dependents_when_dependency_fails`: Create chain A→B→C, fail A, verify B and C BLOCKED
- `test_should_enforce_deletion_constraints_when_dependents_exist`: Create A, B→A, try delete A → 409

### Reasoning
Validates full system integration with real DB container and HTTP transport.

---

## Verification

After all phases complete:
1. `./scripts/lint.py` — passes with no errors
2. `./scripts/test.py unit` — all unit tests pass
3. `./scripts/test.py integration` — all integration tests pass (requires Docker)
4. `./scripts/test.py e2e` — all E2E tests pass (requires Docker)
5. Manual: `uvicorn taskflow.api.app:create_app --factory` starts and serves `/docs`
