dependencies = [
    "pydantic>=2.11",
    "pyyaml>=6.0",
    "rich>=14.0",
    "typer>=0.16",
]

[project.optional-dependencies]
dev = [
    "pytest",
    "ruff",
    "black",
    "mypy",
]
