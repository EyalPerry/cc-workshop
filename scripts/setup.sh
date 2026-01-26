#!/usr/bin/env bash

set -euxo pipefail

# Install uv if not already installed
if ! command -v uv &> /dev/null; then
    echo "🐍 Installing uv"
    curl -LsSf https://astral.sh/uv/install.sh | sh
else
    echo "🐍 uv is already available"
fi

# Read Python version from .python-version file
PYTHON_VERSION=$(cat .python-version | tr -d '\n')

# Install Python if not already available
if ! command -v python"$PYTHON_VERSION" &> /dev/null; then
    echo "🐍 Installing Python $PYTHON_VERSION"
    uv python install "$PYTHON_VERSION"
else
    echo "🐍 Python $PYTHON_VERSION is already available"
fi

uv run --script scripts/install.py
