from __future__ import annotations

from .game_event import GameEvent
from .game_event_listener import GameEventListener
from .game_event_type import GameEventType


# издатель: хранит подписчиков по типам событий и оповещает их, ничего не зная о том, что они делают
class GameEventPublisher:

    def __init__(self) -> None:
        self._listeners: dict[GameEventType, list[GameEventListener]] = {}

    def subscribe(self, event_type: GameEventType, listener: GameEventListener) -> None:
        self._listeners.setdefault(event_type, []).append(listener)

    def unsubscribe(self, event_type: GameEventType, listener: GameEventListener) -> None:
        subscribed = self._listeners.get(event_type)
        if subscribed is not None and listener in subscribed:
            subscribed.remove(listener)

    def publish(self, event: GameEvent) -> None:
        # обходим копию списка: подписчик может отписаться прямо во время оповещения
        for listener in list(self._listeners.get(event.type, [])):
            listener.on_event(event)
