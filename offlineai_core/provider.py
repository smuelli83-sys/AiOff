from typing import Protocol


class ProviderProtocol(Protocol):

    id: str
    version: str

    def install(self) -> None:
        ...

    def uninstall(self) -> None:
        ...

    def verify(self) -> bool:
        ...

    def health(self) -> bool:
        ...

    def configure(self) -> None:
        ...
