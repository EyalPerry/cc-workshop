import pytest
from pydantic import ValidationError

from taskflow.models import BackoffStrategy, RetryPolicy


def test_should_create_with_defaults_when_no_args():
    expected = RetryPolicy(
        max_attempts=3,
        backoff_strategy=BackoffStrategy.EXPONENTIAL,
        base_delay_seconds=10,
        max_delay_seconds=300,
    )

    actual = RetryPolicy()

    assert actual == expected, (
        "RetryPolicy defaults must match SRS specification: "
        "3 attempts, exponential backoff, 10s base, 300s max."
    )


def test_should_create_with_custom_values_when_valid():
    expected = RetryPolicy(
        max_attempts=5,
        backoff_strategy=BackoffStrategy.LINEAR,
        base_delay_seconds=20,
        max_delay_seconds=600,
    )

    actual = RetryPolicy(
        max_attempts=5,
        backoff_strategy=BackoffStrategy.LINEAR,
        base_delay_seconds=20,
        max_delay_seconds=600,
    )

    assert actual == expected, (
        "RetryPolicy must accept valid custom values within the allowed ranges."
    )


def test_should_reject_max_attempts_below_1_when_invalid():
    with pytest.raises(ValidationError) as exc_info:
        RetryPolicy(max_attempts=0)

    assert "max_attempts" in str(exc_info.value), (
        "At least 1 attempt is required; zero attempts would mean "
        "the job can never execute."
    )


def test_should_reject_max_attempts_above_10_when_invalid():
    with pytest.raises(ValidationError) as exc_info:
        RetryPolicy(max_attempts=11)

    assert "max_attempts" in str(exc_info.value), (
        "More than 10 retry attempts risks excessive resource "
        "consumption and should be rejected."
    )


def test_should_reject_base_delay_below_1_when_invalid():
    with pytest.raises(ValidationError) as exc_info:
        RetryPolicy(base_delay_seconds=0)

    assert "base_delay_seconds" in str(exc_info.value), (
        "A zero-second base delay would cause immediate retries without any backoff."
    )


def test_should_reject_base_delay_above_300_when_invalid():
    with pytest.raises(ValidationError) as exc_info:
        RetryPolicy(base_delay_seconds=301)

    assert "base_delay_seconds" in str(exc_info.value), (
        "Base delay above 300 seconds would cause excessively long initial wait times."
    )


def test_should_reject_max_delay_below_base_delay_when_invalid():
    with pytest.raises(ValidationError) as exc_info:
        RetryPolicy(base_delay_seconds=100, max_delay_seconds=50)

    assert "max_delay_seconds" in str(exc_info.value), (
        "max_delay_seconds below base_delay_seconds is contradictory; "
        "the cap cannot be lower than the starting delay."
    )


def test_should_reject_max_delay_above_3600_when_invalid():
    with pytest.raises(ValidationError) as exc_info:
        RetryPolicy(max_delay_seconds=3601)

    assert "max_delay_seconds" in str(exc_info.value), (
        "Max delay above 3600 seconds (1 hour) would cause "
        "unacceptably long retry waits."
    )
