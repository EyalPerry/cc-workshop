
FROM debian:bookworm-slim 

USER root

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

RUN apt-get update \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /root/.cache/* \
    && useradd --create-home --uid 1000 --shell /bin/bash app

ARG PYTHON_VERSION

ENV PYTHON_VERSION=${PYTHON_VERSION} \
    PATH="/home/app/.venv/bin:$PATH" \
    PYTHONPATH="/home/app" \
    CONFIG_ROOT=/etc/app/config \
    VARIABLES_ROOT=/etc/app/config \
    TZ=UTC

WORKDIR /home/app
COPY pyproject.toml uv.lock ./

RUN uv python install ${PYTHON_VERSION} && \
    uv sync --frozen --no-dev

COPY --chown=app:app src/ ./
COPY --chown=app:app assets/config/ /etc/app/config/

USER app

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
