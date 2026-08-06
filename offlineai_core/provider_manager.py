from __future__ import annotations

from offlineai_core.provider import ProviderBase


class ProviderManager:

    def __init__(self) -> None:
        self._providers: dict[str, ProviderBase] = {}

    def register(self, provider: ProviderBase) -> None:

        self._providers[provider.id] = provider

    def unregister(self, provider_id: str) -> None:

        self._providers.pop(provider_id, None)

    def get(self, provider_id: str) -> ProviderBase | None:

        return self._providers.get(provider_id)

    def all(self) -> list[ProviderBase]:

        return list(self._providers.values())

    def startup(self) -> None:

        for provider in self._providers.values():
            provider.startup()

    def shutdown(self) -> None:

        for provider in self._providers.values():
            provider.shutdown()
