"""Enumerations for the TaskFlow scheduler domain."""

from enum import Enum


class JobStatus(str, Enum):
    """Represents the current state of a job in the scheduling lifecycle.

    Values:
        PENDING: Waiting for dependencies to complete.
        READY: Dependencies satisfied, eligible for execution.
        RUNNING: Currently executing.
        COMPLETED: Finished successfully.
        FAILED: Exhausted all retry attempts.
        BLOCKED: A dependency failed, cannot proceed.
    """

    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class BackoffStrategy(str, Enum):
    """Backoff strategy for retry delay calculation.

    Values:
        FIXED: Same delay every retry.
        LINEAR: Delay grows by base_delay each attempt.
        EXPONENTIAL: Delay doubles each attempt.
    """

    FIXED = "fixed"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
