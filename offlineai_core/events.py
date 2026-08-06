from collections import defaultdict
from collections.abc import Callable


class EventBus:

    def __init__(self) -> None:
        self._events: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, event: str, callback: Callable) -> None:
        self._events[event].append(callback)

    def unsubscribe(self, event: str, callback: Callable) -> None:
        if callback in self._events[event]:
            self._events[event].remove(callback)

    def publish(self, event: str, *args, **kwargs) -> None:
        for callback in self._events[event]:
            callback(*args, **kwargs)
