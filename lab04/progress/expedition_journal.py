from __future__ import annotations

from ..event.game_event import GameEvent
from ..event.game_event_listener import GameEventListener
from ..world.expedition_report import ExpeditionReport


# подписчик, который записывает экспедиции в журнал (журнал живет, пока запущена игра)
class ExpeditionJournal(GameEventListener):

    def __init__(self) -> None:
        self._entries: dict[str, list[ExpeditionReport]] = {}

    def on_event(self, event: GameEvent) -> None:
        self._entries.setdefault(event.hero.name, []).append(event.expedition)

    def entries(self, hero_name: str) -> list[ExpeditionReport]:
        return list(self._entries.get(hero_name, []))
