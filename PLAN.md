# TaskFlow Scheduler - Implementation Plan

## Final File System Layout

```
src/
  taskflow/
    __init__.py
    models/
      __init__.py
      job.py              # Job, RetryPolicy, BackoffStrategy, JobStatus
      api.py              # JobCreateRequest, JobUpdateRequest, SearchResponse, ErrorResponse
      internal.py         # CycleDetectionResult, DependencyStatus
    logic/
      __init__.py
      dependencies.py     # detect_cycle, check_dependency_satisfaction
      scheduling.py       # order_jobs, select_next_jobs
      retry.py            # calculate_retry_delay, should_retry
      state_machine.py    # is_valid_transition, is_terminal_state
      cascading.py        # propagate_failure, propagate_completion
    validation/
      __init__.py
      job_validator.py    # validate_payload_size, validate_cursor
    db/
      __init__.py
      pool.py             # create_pool, close_pool
      repository.py       # JobRepository (CRUD + search)
      migrations/
        env.py
        script.py.mako
        versions/
          001_create_jobs_table.py
    api/
      __init__.py
      app.py              # create_app (FastAPI factory)
      dependencies.py     # get_pool, get_repository
      errors.py           # TaskFlowException, ValidationError, NotFoundError, ConflictError
      routes/
        __init__.py
        jobs.py           # POST/GET/PUT/DELETE /api/v1/jobs
test/
  conftest.py
  fixtures/
    __init__.py
    postgres.py           # postgres_container, db_pool
    sample_data.py        # sample factories
  utils/
    __init__.py
    factories.py          # JobFactory, RetryPolicyFactory
  unit/
    models/
      test_job.py
      test_api.py
    logic/
      test_dependencies.py
      test_scheduling.py
      test_retry.py
      test_state_machine.py
      test_cascading.py
    validation/
      test_job_validator.py
    api/
      test_errors.py
  it/
    db/
      test_pool.py
      test_migrations.py
      test_repository.py
  e2e/
    api/
      test_jobs_api.py
```

---

## Phase 1: Core Data Models

**Files**: `src/taskflow/models/job.py`, `api.py`, `internal.py`, `__init__.py`s

**Implement**:
- `BackoffStrategy(str, Enum)` - FIXED, LINEAR, EXPONENTIAL
- `JobStatus(str, Enum)` - 6 states
- `RetryPolicy(BaseModel)` - with defaults (max_attempts=3, backoff=EXPONENTIAL, base=10, max=300)
- `Job(BaseModel)` - all 10 fields with pydantic validators (name 1-255, queue regex, priority 1-10, deps max 50)
- `JobCreateRequest(BaseModel)` - name, queue, payload, priority, dependencies, retry_policy
- `JobUpdateRequest(BaseModel)` - optional name, queue, payload, priority, dependencies, retry_policy
- `SearchResponse(BaseModel, Generic[T])` - items, next_cursor, has_more
- `ErrorResponse(BaseModel)` - code, message, details
- `DependencyStatus(str, Enum)` - SATISFIED, WAITING, BLOCKED
- `CycleDetectionResult(BaseModel)` - has_cycle, cycle_path

**Reasoning**: Models are the foundation; everything else depends on them. Pydantic handles most field-level validation.

**Tests** (unit):
- `test/unit/models/test_job.py`: 10 tests - defaults, constraint violations, serialization
  - `test_should_create_retry_policy_with_defaults_when_no_values_provided`
  - `test_should_reject_retry_policy_when_max_attempts_exceeds_limit`
  - `test_should_reject_retry_policy_when_base_delay_exceeds_max_delay`
  - `test_should_create_job_with_valid_fields_when_all_constraints_met`
  - `test_should_reject_job_when_name_exceeds_255_characters`
  - `test_should_reject_job_when_queue_contains_invalid_characters`
  - `test_should_reject_job_when_priority_out_of_range`
  - `test_should_reject_job_when_dependencies_exceed_50_items`
  - `test_should_serialize_job_to_json_when_model_is_valid`
  - `test_should_deserialize_job_from_json_when_data_is_valid`
- `test/unit/models/test_api.py`: 3 tests - request/response model creation
  - `test_should_create_job_create_request_when_required_fields_provided`
  - `test_should_create_search_response_with_pagination_when_cursor_provided`
  - `test_should_serialize_error_response_when_validation_fails`

---

## Phase 2: Dependency Resolution Logic

**Files**: `src/taskflow/logic/dependencies.py`, `__init__.py`

**Implement**:
- `detect_cycle(new_job_id, new_job_dependencies, existing_jobs) -> CycleDetectionResult` - DFS cycle detection
- `check_dependency_satisfaction(dependencies, dependency_statuses) -> DependencyStatus` - rule-based status evaluation

**Reasoning**: Pure functions, no DB needed. Core correctness requirement.

**Tests** (unit):
- `test/unit/logic/test_dependencies.py`: 14 tests
  - `test_should_detect_no_cycle_when_dependencies_form_dag`
  - `test_should_detect_cycle_when_job_depends_on_itself`
  - `test_should_detect_cycle_when_two_jobs_depend_on_each_other`
  - `test_should_detect_cycle_when_three_jobs_form_cycle`
  - `test_should_return_cycle_path_when_cycle_exists`
  - `test_should_allow_job_when_dependency_not_in_existing_jobs`
  - `test_should_detect_no_cycle_when_dependencies_list_is_empty`
  - `test_should_return_satisfied_when_dependencies_list_is_empty`
  - `test_should_return_satisfied_when_all_dependencies_completed`
  - `test_should_return_blocked_when_any_dependency_failed`
  - `test_should_return_blocked_when_any_dependency_blocked`
  - `test_should_return_waiting_when_any_dependency_pending`
  - `test_should_return_waiting_when_any_dependency_running`
  - `test_should_prioritize_blocked_over_waiting_when_mixed_states`

---

## Phase 3: Scheduling Logic

**Files**: `src/taskflow/logic/scheduling.py`

**Implement**:
- `order_jobs(jobs) -> list[Job]` - sort by priority DESC, created_at ASC, id ASC
- `select_next_jobs(ready_jobs, running_count, max_concurrent) -> list[Job]` - slot calculation + ordering

**Reasoning**: Pure functions with deterministic sorting. Separation allows testing ordering independent of selection.

**Tests** (unit):
- `test/unit/logic/test_scheduling.py`: 9 tests
  - `test_should_sort_jobs_by_priority_when_priorities_differ`
  - `test_should_sort_by_created_at_when_priorities_equal`
  - `test_should_sort_by_id_when_priority_and_created_at_equal`
  - `test_should_handle_mixed_sorting_criteria_when_jobs_have_various_attributes`
  - `test_should_return_empty_list_when_no_slots_available`
  - `test_should_return_all_jobs_when_slots_exceed_job_count`
  - `test_should_return_exactly_available_slots_when_jobs_exceed_slots`
  - `test_should_select_highest_priority_jobs_when_limiting_selection`
  - `test_should_preserve_job_order_when_jobs_list_is_empty`

---

## Phase 4: Retry Logic

**Files**: `src/taskflow/logic/retry.py`

**Implement**:
- `calculate_retry_delay(retry_policy, attempt_number) -> int` - FIXED/LINEAR/EXPONENTIAL with max cap
- `should_retry(attempt_count, max_attempts) -> bool`

**Reasoning**: Pure mathematical functions, easy to verify against spec tables.

**Tests** (unit):
- `test/unit/logic/test_retry.py`: 10 tests
  - `test_should_return_base_delay_when_strategy_is_fixed`
  - `test_should_calculate_linear_delay_when_strategy_is_linear`
  - `test_should_cap_linear_delay_when_exceeds_max`
  - `test_should_calculate_exponential_delay_when_strategy_is_exponential`
  - `test_should_cap_exponential_delay_when_exceeds_max`
  - `test_should_handle_first_attempt_when_attempt_number_is_one`
  - `test_should_handle_high_attempt_numbers_when_exponential_strategy_used`
  - `test_should_allow_retry_when_attempts_below_max`
  - `test_should_deny_retry_when_attempts_equal_max`
  - `test_should_deny_retry_when_attempts_exceed_max`

---

## Phase 5: State Machine Logic

**Files**: `src/taskflow/logic/state_machine.py`

**Implement**:
- `_VALID_TRANSITIONS` constant dict
- `is_valid_transition(current, target) -> bool`
- `is_terminal_state(status) -> bool`

**Reasoning**: Centralized state machine rules prevent invalid state changes.

**Tests** (unit):
- `test/unit/logic/test_state_machine.py`: 12 tests
  - `test_should_allow_transition_from_pending_to_ready`
  - `test_should_allow_transition_from_pending_to_blocked`
  - `test_should_allow_transition_from_ready_to_running`
  - `test_should_allow_transition_from_running_to_completed`
  - `test_should_allow_transition_from_running_to_ready`
  - `test_should_allow_transition_from_running_to_failed`
  - `test_should_reject_transition_from_completed_to_any_state`
  - `test_should_reject_transition_from_failed_to_any_state`
  - `test_should_reject_transition_from_blocked_to_any_state`
  - `test_should_reject_invalid_transitions_when_not_in_spec`
  - `test_should_identify_terminal_states_when_status_is_completed_failed_or_blocked`
  - `test_should_identify_non_terminal_states_when_status_is_pending_ready_or_running`

---

## Phase 6: Cascading Updates Logic

**Files**: `src/taskflow/logic/cascading.py`

**Implement**:
- `propagate_failure(failed_job_id, all_jobs) -> set[UUID]` - recursive BFS for PENDING dependents
- `propagate_completion(completed_job_id, all_jobs) -> set[UUID]` - check all deps COMPLETED

**Reasoning**: Graph traversal algorithms critical for maintaining dependency integrity.

**Tests** (unit):
- `test/unit/logic/test_cascading.py`: 11 tests
  - `test_should_return_empty_set_when_no_jobs_depend_on_failed_job`
  - `test_should_block_direct_dependents_when_job_fails`
  - `test_should_block_transitive_dependents_when_job_fails`
  - `test_should_only_block_pending_jobs_when_job_fails`
  - `test_should_handle_multiple_dependency_paths_when_propagating_failure`
  - `test_should_return_empty_set_when_no_jobs_depend_on_completed_job`
  - `test_should_return_job_when_all_dependencies_completed`
  - `test_should_not_return_job_when_some_dependencies_still_pending`
  - `test_should_not_return_job_when_some_dependencies_running`
  - `test_should_handle_multiple_jobs_becoming_ready_when_dependency_completes`
  - `test_should_only_check_pending_jobs_when_propagating_completion`

---

## Phase 7: Validation Layer

**Files**: `src/taskflow/validation/job_validator.py`, `__init__.py`

**Implement**:
- `validate_payload_size(payload) -> None` - JSON serialize, check <= 65536 bytes
- `validate_cursor(cursor) -> tuple[datetime, UUID] | None` - base64 decode, parse format

**Reasoning**: Separates validation logic from API layer for testability.

**Tests** (unit):
- `test/unit/validation/test_job_validator.py`: 9 tests
  - `test_should_accept_payload_when_size_within_limit`
  - `test_should_reject_payload_when_size_exceeds_64kb`
  - `test_should_calculate_json_size_accurately_when_validating`
  - `test_should_return_none_when_cursor_is_none`
  - `test_should_parse_valid_cursor_when_format_is_correct`
  - `test_should_reject_cursor_when_not_base64_encoded`
  - `test_should_reject_cursor_when_missing_pipe_separator`
  - `test_should_reject_cursor_when_timestamp_is_invalid`
  - `test_should_reject_cursor_when_uuid_is_invalid`

---

## Phase 8: Database Pool

**Files**: `src/taskflow/db/pool.py`, `__init__.py`

**Implement**:
- `create_pool(dsn, min_size, max_size) -> asyncpg.Pool`
- `close_pool(pool) -> None`

**Tests** (integration):
- `test/it/db/test_pool.py`: 4 tests
  - `test_should_create_pool_when_postgres_is_available`
  - `test_should_execute_query_when_pool_is_connected`
  - `test_should_close_pool_gracefully_when_requested`
  - `test_should_reuse_connections_when_pool_is_active`

---

## Phase 9: Database Migration

**Files**: `src/taskflow/db/migrations/env.py`, `script.py.mako`, `versions/001_create_jobs_table.py`

**Implement**: `jobs` table - id UUID PK, name VARCHAR(255), queue VARCHAR(64), payload JSONB, priority INTEGER CHECK(1-10), status VARCHAR(20), dependencies UUID[], retry_policy JSONB, created_at/updated_at TIMESTAMPTZ, attempt_count INTEGER. Indexes: status, queue, created_at DESC, (priority DESC, created_at ASC).

**Reasoning**: Single table sufficient for MVP. JSONB for flexible nested data. UUID[] for native array support.

**Tests** (integration):
- `test/it/db/test_migrations.py`: 5 tests
  - `test_should_create_jobs_table_when_migration_runs`
  - `test_should_create_all_indexes_when_migration_runs`
  - `test_should_enforce_check_constraints_when_inserting_invalid_data`
  - `test_should_default_timestamps_when_not_provided`
  - `test_should_rollback_migration_when_downgrade_runs`

---

## Phase 10: Repository

**Files**: `src/taskflow/db/repository.py`

**Implement**: `JobRepository` - create, get_by_id, update, delete, get_by_ids, search (cursor pagination with base64 encoding), get_dependency_graph, get_jobs_depending_on

**Reasoning**: Raw SQL with asyncpg. Returns domain models. Search builds dynamic WHERE clauses.

**Tests** (integration):
- `test/it/db/test_repository.py`: 18 tests - CRUD, search filters (queue, status, priority range, date range), pagination, cursor encoding, sorting, dependency queries

**Shared test infrastructure**: `test/conftest.py`, `test/fixtures/postgres.py`, `test/utils/factories.py`

---

## Phase 11: API Error Handling

**Files**: `src/taskflow/api/errors.py`, `__init__.py`

**Implement**: `TaskFlowException`, `ValidationError(400)`, `NotFoundError(404)`, `ConflictError(409)`, `register_error_handlers(app)`

**Tests** (unit):
- `test/unit/api/test_errors.py`: 3 tests - exception construction

---

## Phase 12: API App Factory & Dependencies

**Files**: `src/taskflow/api/app.py`, `dependencies.py`

**Implement**: `create_app(database_url) -> FastAPI` with lifespan, error handlers, router. `get_pool()`, `get_repository()` for DI.

**Tests** (unit):
- `test/unit/api/test_app.py`: 2 tests - app config, router inclusion

---

## Phase 13: API Job Endpoints

**Files**: `src/taskflow/api/routes/jobs.py`, `__init__.py`

**Implement**: 5 endpoints (create, get, update, delete, search) delegating to logic + repository layers. Create validates payload size + cycles. Update checks non-terminal. Delete checks no dependents.

**Tests**: Covered by E2E in Phase 15.

---

## Phase 14: Integration Test Infrastructure

**Files**: `test/conftest.py`, `test/fixtures/`, `test/utils/`

**Implement**: Shared fixtures (postgres testcontainer session-scoped, pool function-scoped with migration), factories. Run all IT tests from phases 8-10.

---

## Phase 15: E2E Tests

**Files**: `test/e2e/api/test_jobs_api.py`

**Implement**: 16 tests - happy paths (CRUD, search, pagination), error cases (400/404/409), business logic (cascading, priority, retry). Uses httpx AsyncClient against full FastAPI app with real Postgres.

---

## Verification

1. `./scripts/test.py unit` - ~80 unit tests
2. `./scripts/test.py it` - ~27 integration tests (Docker required)
3. `./scripts/test.py e2e` - ~16 E2E tests (Docker required)
4. `./scripts/lint.py` - zero lint errors
