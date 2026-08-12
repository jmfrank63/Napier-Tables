import tomllib
from pathlib import Path


def test_package_imports_and_python_requirement_metadata():
    import napier_tables

    assert napier_tables is not None
    metadata = tomllib.loads(
        (Path(__file__).parents[1] / "pyproject.toml").read_text()
    )["project"]
    assert metadata["requires-python"] == ">=3.14"
