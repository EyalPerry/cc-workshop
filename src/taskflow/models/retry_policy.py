"""Retry policy model for configuring job retry behavior."""

import typing as t

from pydantic import BaseModel, Field, model_validator

from .enums import BackoffStrategy


class RetryPolicy(BaseModel):
    """Configuration for how a job should be retried on failure.

    Attributes:
        max_attempts: Maximum number of execution attempts (1-10).
        backoff_strategy: Delay growth pattern between retries.
        base_delay_seconds: Initial retry delay in seconds (1-300).
        max_delay_seconds: Maximum delay cap in seconds (1-3600).

    Raises:
        ValueError: If max_delay_seconds < base_delay_seconds.
    """

    max_attempts: int = Field(default=3, ge=1, le=10)
    backoff_strategy: BackoffStrategy = Field(
        default=BackoffStrategy.EXPONENTIAL,
    )
    base_delay_seconds: int = Field(default=10, ge=1, le=300)
    max_delay_seconds: int = Field(default=300, ge=1, le=3600)

    @model_validator(mode="after")
    def _validate_delay_range(self) -> t.Self:
        if self.max_delay_seconds < self.base_delay_seconds:
            msg = (
                f"max_delay_seconds ({self.max_delay_seconds}) must be "
                f">= base_delay_seconds ({self.base_delay_seconds})"
            )
            raise ValueError(msg)
        return self
