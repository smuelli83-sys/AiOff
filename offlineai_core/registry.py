from dataclasses import dataclass, field

from offlineai_core.types import ProviderType


@dataclass(slots=True)
class Provider:

    id: str
    name: str
    version: str

    type: ProviderType = ProviderType.CORE

    capabilities: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)

    healthy: bool = False
    enabled: bool = True


class Registry:

    def __init__(self) -> None:
        self._providers: dict[str, Provider] = {}

    def register(self, provider: Provider) -> None:
        self._providers[provider.id] = provider

    def unregister(self, provider_id: str) -> None:
        self._providers.pop(provider_id, None)

    def exists(self, provider_id: str) -> bool:
        return provider_id in self._providers

    def get(self, provider_id: str) -> Provider | None:
        return self._providers.get(provider_id)

    def list(self) -> list[Provider]:
        return sorted(
            self._providers.values(),
            key=lambda provider: provider.name,
        )

    def healthy(self) -> bool:
        return all(provider.healthy for provider in self._providers.values())
