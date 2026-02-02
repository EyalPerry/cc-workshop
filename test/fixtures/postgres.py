"""Shared PostgreSQL testcontainer fixtures for integration tests."""

import typing as t
from collections.abc import AsyncGenerator, Generator

import asyncpg
import pytest
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, t.Any]:
    """Start a PostgreSQL container for the test session.

    Yields:
        A running PostgreSQL container.
    """
    with PostgresContainer("postgres:16-alpine") as container:
        yield container


@pytest.fixture(scope="session")
def postgres_dsn(postgres_container: PostgresContainer) -> str:
    """Get the DSN for the running PostgreSQL container.

    Args:
        postgres_container: The running PostgreSQL container.

    Returns:
        A PostgreSQL connection string.
    """
    return postgres_container.get_connection_url().replace(
        "postgresql+psycopg2://", "postgresql://"
    )


@pytest.fixture()
async def db_pool(postgres_dsn: str) -> AsyncGenerator[asyncpg.Pool]:
    """Create a function-scoped asyncpg pool connected to the test container.

    Args:
        postgres_dsn: The PostgreSQL DSN.

    Yields:
        An asyncpg connection pool.
    """
    pool: asyncpg.Pool = await asyncpg.create_pool(
        dsn=postgres_dsn,
        min_size=2,
        max_size=5,
    )
    yield pool
    await pool.close()
