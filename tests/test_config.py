import tomllib
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from napier_tables import ConfigurationError, TableConfig


def test_package_imports_and_python_requirement_metadata():
    import napier_tables

    assert napier_tables is not None
    metadata = tomllib.loads(
        (Path(__file__).parents[1] / "pyproject.toml").read_text()
    )["project"]
    assert metadata["requires-python"] == ">=3.14"
    assert any(
        requirement.startswith("pytest")
        for requirement in metadata["optional-dependencies"]["test"]
    )


def test_table_config_constructs_with_defaults_and_validates():
    config = TableConfig()

    assert config == TableConfig(
        base=10, fractional_digits=4, start=1, end=1000, workers=None
    )
    assert config.validate() is None


def test_table_config_is_frozen():
    config = TableConfig()

    with pytest.raises(FrozenInstanceError):
        config.base = 2


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("base", 1, "base must be at least 2"),
        ("fractional_digits", -1, "fractional_digits must be non-negative"),
        ("start", 0, "start must be at least 1"),
        ("end", 0, "end must be greater than or equal to start"),
        ("workers", 0, "workers must be at least 1 or None"),
    ],
)
def test_table_config_rejects_invalid_field(field, value, message):
    config = TableConfig(**{field: value})

    with pytest.raises(ConfigurationError, match=f"^{message}$"):
        config.validate()


def test_table_config_rejects_end_before_start():
    config = TableConfig(start=10, end=9)

    with pytest.raises(
        ConfigurationError, match=r"^end must be greater than or equal to start$"
    ):
        config.validate()
