from __future__ import annotations

from dataclasses import dataclass

from ..core.unknown_code_error import UnknownCodeError


# зачарование неизменяемо (frozen=True): его нельзя поменять после создания,
# поэтому одно и то же зачарование можно безопасно повесить на несколько предметов
@dataclass(frozen=True)
class Enchantment:
    code: str
    name: str
    bonus_damage: int
    bonus_defense: float
    bonus_price: int

    # восстановление зачарования по коду - понадобится при загрузке сохранений
    @staticmethod
    def by_code(code: str) -> Enchantment:
        for enchantment in ALL:
            if enchantment.code == code:
                return enchantment

        raise UnknownCodeError("Зачарование", code)


SHARP = Enchantment("sharp", "Острое", 3, 0, 20)
FIERY = Enchantment("fiery", "Огненное", 6, 0, 50)
STURDY = Enchantment("sturdy", "Прочное", 0, 0.05, 20)
WARDING = Enchantment("warding", "Охранное", 0, 0.10, 50)

FOR_WEAPONS = (SHARP, FIERY)
FOR_ARMOR = (STURDY, WARDING)
ALL = (SHARP, FIERY, STURDY, WARDING)
