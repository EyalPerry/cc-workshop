"""Configure Docker socket path and credentials for testcontainers."""

import os
from pathlib import Path


def pytest_configure(config: object) -> None:
    """Configure Docker socket path for testcontainers."""
    if "DOCKER_HOST" not in os.environ:
        docker_sock_paths = [
            "/var/run/docker.sock",
            str(Path.home() / ".docker" / "run" / "docker.sock"),
        ]

        for sock_path in docker_sock_paths:
            if Path(sock_path).exists():
                os.environ["DOCKER_HOST"] = f"unix://{sock_path}"
                break

    # Add Docker Desktop credential helper to PATH if it exists
    docker_desktop_bin = Path("/Applications/Docker.app/Contents/Resources/bin")
    if docker_desktop_bin.exists() and str(docker_desktop_bin) not in os.environ.get(
        "PATH", ""
    ):
        os.environ["PATH"] = f"{docker_desktop_bin}:{os.environ.get('PATH', '')}"
