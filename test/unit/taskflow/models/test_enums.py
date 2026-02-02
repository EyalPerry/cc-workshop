from taskflow.models import BackoffStrategy, JobStatus


def test_should_have_all_job_status_values_when_enum_defined():
    expected = {
        JobStatus.PENDING,
        JobStatus.READY,
        JobStatus.RUNNING,
        JobStatus.COMPLETED,
        JobStatus.FAILED,
        JobStatus.BLOCKED,
    }

    actual = set(JobStatus)

    assert actual == expected, (
        "JobStatus enum must define exactly the six lifecycle states "
        "required by the scheduling state machine."
    )


def test_should_have_all_backoff_strategy_values_when_enum_defined():
    expected = {
        BackoffStrategy.FIXED,
        BackoffStrategy.LINEAR,
        BackoffStrategy.EXPONENTIAL,
    }

    actual = set(BackoffStrategy)

    assert actual == expected, (
        "BackoffStrategy enum must define exactly the three retry "
        "strategies supported by the scheduler."
    )


def test_should_serialize_to_string_when_value_accessed():
    expected_statuses = {
        JobStatus.PENDING: "pending",
        JobStatus.READY: "ready",
        JobStatus.RUNNING: "running",
        JobStatus.COMPLETED: "completed",
        JobStatus.FAILED: "failed",
        JobStatus.BLOCKED: "blocked",
    }
    expected_strategies = {
        BackoffStrategy.FIXED: "fixed",
        BackoffStrategy.LINEAR: "linear",
        BackoffStrategy.EXPONENTIAL: "exponential",
    }

    actual_statuses = {s: s.value for s in JobStatus}
    actual_strategies = {s: s.value for s in BackoffStrategy}

    assert actual_statuses == expected_statuses, (
        "JobStatus values must serialize to lowercase strings for "
        "database and API compatibility."
    )
    assert actual_strategies == expected_strategies, (
        "BackoffStrategy values must serialize to lowercase strings for "
        "database and API compatibility."
    )
