from abc import ABC, abstractmethod

from .game_event import GameEvent


# Наблюдатель: интерфейс подписчика, единственный метод вызывается при наступлении события
class GameEventListener(ABC):

    @abstractmethod
    def on_event(self, event: GameEvent) -> None: ...
