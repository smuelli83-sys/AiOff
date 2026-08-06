from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(slots=True)
class Provider:

    id: str

    name: str

    version: str

    capabilities: List[str] = field(default_factory=list)

    dependencies: List[str] = field(default_factory=list)

    healthy: bool = False

    enabled: bool = True


class Registry:

    def __init__(self):

        self.providers: Dict[str, Provider] = {}

    def register(self, provider: Provider):

        self.providers[provider.id] = provider

    def unregister(self, provider_id: str):

        self.providers.pop(provider_id, None)

    def exists(self, provider_id: str) -> bool:

        return provider_id in self.providers

    def get(self, provider_id: str):

        return self.providers.get(provider_id)

    def list(self):

        return list(self.providers.values())

    def health(self):

        return all(p.healthy for p in self.providers.values())
