# Software Requirements Specification: TaskFlow Scheduler

## 1. Data Models

### 1.1 Job

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | Primary key | Unique job identifier |
| name | string | 1-255 chars | Human-readable name |
| queue | string | 1-64 chars, `^[a-zA-Z0-9_]+$` | Logical queue grouping |
| payload | JSON | Max 64KB | Arbitrary job data |
| priority | integer | 1-10 inclusive | Execution priority (10 = highest) |
| status | JobStatus | Required | Current job state |
| dependencies | UUID[] | Max 50 items | Jobs that must complete first |
| retry_policy | RetryPolicy | Required | Retry configuration |
| created_at | datetime | Auto-generated | Submission time (UTC) |
| updated_at | datetime | Auto-updated | Last modification time (UTC) |
| attempt_count | integer | >= 0, default 0 | Current attempt number |

### 1.2 RetryPolicy

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| max_attempts | integer | 1-10 | 3 | Maximum execution attempts |
| backoff_strategy | BackoffStrategy | Required | EXPONENTIAL | Delay growth pattern |
| base_delay_seconds | integer | 1-300 | 10 | Initial retry delay |
| max_delay_seconds | integer | 1-3600 | 300 | Maximum delay cap |

### 1.3 BackoffStrategy Enum

| Value | Description |
|-------|-------------|
| FIXED | Same delay every retry |
| LINEAR | Delay grows by base_delay each attempt |
| EXPONENTIAL | Delay doubles each attempt |

### 1.4 JobStatus Enum

| Value | Description |
|-------|-------------|
| PENDING | Waiting for dependencies to complete |
| READY | Dependencies satisfied, eligible for execution |
| RUNNING | Currently executing |
| COMPLETED | Finished successfully |
| FAILED | Exhausted all retry attempts |
| BLOCKED | A dependency failed, cannot proceed |

---

## 2. Business Logic

### 2.1 Dependency Resolution

#### 2.1.1 Cycle Detection

Detect circular dependencies when submitting a new job.

**Input**:
- `new_job_id`: UUID of job being created
- `new_job_dependencies`: List of dependency UUIDs
- `existing_jobs`: Map of job_id → list of dependency UUIDs

**Output**: `CycleDetectionResult`
- `has_cycle`: boolean
- `cycle_path`: List of UUIDs forming the cycle (empty if no cycle)

**Algorithm** (DFS-based):
1. Build directed graph: job → dependencies
2. Add new job's edges to graph
3. Run DFS from new job, tracking visited and recursion stack
4. If we revisit a node in current recursion stack, cycle exists
5. Return cycle path by backtracking from repeated node

**Edge Cases**:
- Self-dependency (job depends on itself): cycle of length 1
- Empty dependencies: no cycle possible
- Dependency not in existing_jobs: valid (may be external reference)

#### 2.1.2 Dependency Satisfaction Check

Determine a job's readiness based on dependency states.

**Input**:
- `job`: Job with dependencies list
- `dependency_statuses`: Map of dependency_id → JobStatus

**Output**: `DependencyStatus`
- `SATISFIED`: All dependencies COMPLETED
- `WAITING`: At least one dependency is PENDING, READY, or RUNNING
- `BLOCKED`: At least one dependency is FAILED or BLOCKED

**Rules** (evaluated in order):
1. If dependencies list is empty → SATISFIED
2. If any dependency status is FAILED or BLOCKED → BLOCKED
3. If any dependency status is PENDING, READY, or RUNNING → WAITING
4. If all dependency statuses are COMPLETED → SATISFIED

### 2.2 Priority Scheduling

#### 2.2.1 Job Ordering

Sort jobs for execution scheduling.

**Input**: List of jobs (all in READY status)

**Output**: Sorted list of jobs

**Comparison Rules** (applied in order, first difference wins):
1. Higher priority first: `b.priority - a.priority`
2. Earlier created first: `a.created_at - b.created_at`
3. Lexicographic UUID for determinism: `a.id.compareTo(b.id)`

#### 2.2.2 Select Next Jobs

Select jobs eligible for execution.

**Input**:
- `ready_jobs`: List of READY jobs
- `running_count`: Current number of RUNNING jobs
- `max_concurrent`: Maximum allowed concurrent jobs

**Output**: List of jobs to start (may be empty)

**Algorithm**:
1. Calculate available slots: `max_concurrent - running_count`
2. If available_slots <= 0, return empty list
3. Sort ready_jobs using Job Ordering (2.2.1)
4. Return first `available_slots` jobs

### 2.3 Retry Logic

#### 2.3.1 Calculate Retry Delay

Compute delay before next retry attempt.

**Input**:
- `retry_policy`: RetryPolicy
- `attempt_number`: Current attempt (1-indexed, represents the attempt that just failed)

**Output**: Delay in seconds (integer)

**Formulas**:

| Strategy | Formula |
|----------|---------|
| FIXED | `base_delay_seconds` |
| LINEAR | `min(base_delay_seconds * attempt_number, max_delay_seconds)` |
| EXPONENTIAL | `min(base_delay_seconds * (2 ^ (attempt_number - 1)), max_delay_seconds)` |

**Examples** (base=10, max=300):

| Strategy | Attempt 1 | Attempt 2 | Attempt 3 | Attempt 4 |
|----------|-----------|-----------|-----------|-----------|
| FIXED | 10 | 10 | 10 | 10 |
| LINEAR | 10 | 20 | 30 | 40 |
| EXPONENTIAL | 10 | 20 | 40 | 80 |

#### 2.3.2 Should Retry

Determine if a failed job should retry.

**Input**:
- `job`: Job with attempt_count and retry_policy

**Output**: boolean

**Rule**: `job.attempt_count < job.retry_policy.max_attempts`

### 2.4 State Machine

#### 2.4.1 Valid Transitions

| From | To | Trigger |
|------|----|---------|
| PENDING | READY | All dependencies completed |
| PENDING | BLOCKED | Any dependency failed/blocked |
| READY | RUNNING | Scheduler picks job |
| RUNNING | COMPLETED | Execution succeeds |
| RUNNING | READY | Execution fails, retry allowed (increment attempt_count) |
| RUNNING | FAILED | Execution fails, no retries left |

#### 2.4.2 Terminal States

Jobs in these states cannot transition: `COMPLETED`, `FAILED`, `BLOCKED`

#### 2.4.3 Validate Transition

Check if a state transition is allowed.

**Input**: `current_status`, `target_status`

**Output**: boolean

**Implementation**: Return true if (current_status, target_status) pair exists in Valid Transitions table.

### 2.5 Cascading Updates

#### 2.5.1 Propagate Failure

When a job fails, block all downstream jobs.

**Input**:
- `failed_job_id`: UUID of failed job
- `all_jobs`: List of all jobs

**Output**: Set of job IDs to mark as BLOCKED

**Algorithm**:
1. Initialize result set
2. Find jobs that have failed_job_id in their dependencies
3. For each found job in PENDING status:
   - Add to result set
   - Recursively find its dependents
4. Return result set

#### 2.5.2 Propagate Completion

When a job completes, check if dependents can become ready.

**Input**:
- `completed_job_id`: UUID of completed job
- `all_jobs`: List of all jobs with their statuses

**Output**: Set of job IDs to transition from PENDING to READY

**Algorithm**:
1. Find PENDING jobs that have completed_job_id in dependencies
2. For each, check if ALL dependencies are now COMPLETED
3. Return set of jobs where all dependencies satisfied

---

## 3. Validation Rules

### 3.1 Job Creation

| Field | Validation |
|-------|------------|
| name | 1-255 characters |
| queue | Matches `^[a-zA-Z0-9_]{1,64}$` |
| priority | 1 ≤ value ≤ 10 |
| payload | Size ≤ 65536 bytes |
| dependencies | Length ≤ 50, all UUIDs exist, no cycles |
| retry_policy.max_attempts | 1 ≤ value ≤ 10 |
| retry_policy.base_delay_seconds | 1 ≤ value ≤ 300 |
| retry_policy.max_delay_seconds | base_delay ≤ value ≤ 3600 |

### 3.2 Job Update

- Job must exist and not be in terminal state
- Cannot change: id, created_at, status, attempt_count
- All creation validations apply to updated fields

### 3.3 Job Deletion

- Job must exist
- No other jobs can depend on this job

---

## 4. Search Specification

### 4.1 Search Filters

| Filter | Type | Description |
|--------|------|-------------|
| queue | string | Exact match on queue name |
| status | JobStatus | Exact match on status |
| priority_min | integer | Priority >= value |
| priority_max | integer | Priority <= value |
| created_after | datetime | created_at >= value |
| created_before | datetime | created_at < value |

All filters are optional. Multiple filters combine with AND logic.

### 4.2 Cursor-Based Pagination

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| cursor | string | null | Opaque cursor from previous response |
| limit | integer | 20 | Results per page (1-100) |

**Cursor Encoding**: Base64-encoded `{created_at_iso}|{id}`

**Response**:
```
{
  "items": Job[],
  "next_cursor": string | null,
  "has_more": boolean
}
```

**Behavior**:
- First request: omit cursor, returns first page
- Next page: pass `next_cursor` from previous response
- `has_more=false` indicates final page
- `next_cursor` is null on final page

### 4.3 Sort Order

Results sorted by: `created_at DESC, id ASC` (consistent with cursor)

---

## 5. API Endpoints

### 5.1 Create Job
```
POST /api/v1/jobs
Request: JobCreateRequest
Response: 201 Created → Job
```

### 5.2 Get Job
```
GET /api/v1/jobs/{job_id}
Response: 200 OK → Job
```

### 5.3 Update Job
```
PUT /api/v1/jobs/{job_id}
Request: JobUpdateRequest
Response: 200 OK → Job
```

### 5.4 Delete Job
```
DELETE /api/v1/jobs/{job_id}
Response: 204 No Content
```

### 5.5 Search Jobs
```
GET /api/v1/jobs
Query: queue, status, priority_min, priority_max, created_after, created_before, cursor, limit
Response: 200 OK → { items: Job[], next_cursor: string?, has_more: boolean }
```

---

## 6. Error Codes

| Code | HTTP | Description |
|------|------|-------------|
| VALIDATION_ERROR | 400 | Request failed validation (details in message) |
| NOT_FOUND | 404 | Job does not exist |
| CONFLICT | 409 | Operation not allowed (circular dependency, has dependents, terminal state) |
