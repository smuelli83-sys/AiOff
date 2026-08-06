from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class Paths(BaseModel):
    workspace: Path = Path("./workspace")
    releases: Path = Path("./releases")
    packages: Path = Path("./packages")
    models: Path = Path("./models")
    logs: Path = Path("./logs")


class Security(BaseModel):
    airgap: bool = True
    verify_checksums: bool = True
    telemetry: bool = False


class Build(BaseModel):
    create_iso: bool = False
    create_usb: bool = True
    verify_after_build: bool = True


class Configuration(BaseModel):
    project_name: str = "OfflineAI Enterprise"
    version: str = "0.1.0-alpha"

    paths: Paths = Field(default_factory=Paths)
    security: Security = Field(default_factory=Security)
    build: Build = Field(default_factory=Build)

    @classmethod
    def load(cls, file: Path) -> "Configuration":
        if not file.exists():
            return cls()

        with file.open("r", encoding="utf-8") as f:
            data: dict[str, Any] = yaml.safe_load(f) or {}

        return cls.model_validate(data)

    def save(self, file: Path) -> None:
        file.parent.mkdir(parents=True, exist_ok=True)

        with file.open("w", encoding="utf-8") as f:
            yaml.safe_dump(
                self.model_dump(mode="python"),
                f,
                sort_keys=False,
                allow_unicode=True,
            )
