from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .game_event_type import GameEventType

if TYPE_CHECKING:
    from ..hero.hero import Hero
    from ..world.expedition_report import ExpeditionReport


# событие - это просто данные: что произошло, с каким героем и в какой экспедиции
@dataclass(frozen=True)
class GameEvent:
    type: GameEventType
    hero: Hero
    expedition: ExpeditionReport
