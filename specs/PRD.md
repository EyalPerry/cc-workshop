# Product Requirements Document: TaskFlow Scheduler

## Overview

TaskFlow is a task scheduling system that manages jobs with dependencies, retry policies, and priority-based execution. Users submit jobs via a simple API, and the system handles scheduling, retries, and state management.

## Problem Statement

Applications need reliable background job processing with:
- **Dependency ordering**: Jobs execute only after their dependencies complete
- **Automatic retries**: Failed jobs retry with configurable backoff
- **Priority scheduling**: Important jobs execute first

## Target Users

- **Developers**: Submit and monitor jobs via REST API

## Core Features

### F1: Job Management (CRUD)

Create, read, update, and delete jobs with:
- Unique identifier and name
- Payload (JSON data up to 64KB)
- Priority level (1-10, higher = more urgent)
- Dependencies on other jobs
- Retry policy (attempts, backoff strategy, delays)

### F2: Job Search

Query jobs by:
- Queue name
- Status
- Priority range
- Created date range
- Pagination (limit/offset)

### F3: Dependency Management

- Jobs wait for all dependencies to complete before becoming ready
- Circular dependencies are rejected at submission
- When a dependency fails, downstream jobs are marked blocked

### F4: Priority Scheduling

Ready jobs are ordered by:
1. Priority (highest first)
2. Submission time (oldest first)

### F5: Retry Policies

When jobs fail, retry with configurable:
- **Max attempts**: 1-10 tries
- **Backoff strategy**: Fixed, linear, or exponential delays
- **Base delay**: Initial wait time (seconds)
- **Max delay**: Cap on delay growth

### F6: Job States

```
PENDING → READY → RUNNING → COMPLETED
                        ↘→ FAILED
PENDING → BLOCKED
```

- **PENDING**: Waiting for dependencies
- **READY**: Dependencies satisfied, awaiting execution
- **RUNNING**: Currently executing
- **COMPLETED**: Finished successfully
- **FAILED**: Exhausted all retry attempts
- **BLOCKED**: A dependency failed

## Out of Scope

- Multi-node coordination
- Scheduled/cron triggers
- Web UI
- Webhooks
