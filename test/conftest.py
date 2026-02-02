"""Root test configuration with plugin discovery."""

from pathlib import Path

_test_root = Path("test")
_fixtures_dir = _test_root / "fixtures"


def _to_module_path(file_path: Path) -> str:
    """Convert file path to Python module path relative to test root."""
    relative = file_path.relative_to(_test_root)
    return ".".join(["test", *relative.parts[:-1], relative.stem])


pytest_plugins = [
    _to_module_path(f)
    for f in _fixtures_dir.rglob("*.py")
    if f.stem not in ("__init__", "conftest")
]
