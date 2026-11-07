from __future__ import annotations

from enum import Enum

from ..core.unknown_code_error import UnknownCodeError
from ..defense.armor_handler import ArmorHandler
from ..defense.barrier_handler import BarrierHandler
from ..defense.damage_handler import DamageHandler
from ..defense.evasion_handler import EvasionHandler
from ..item.armor import Armor
from ..item.item_catalog import ItemCatalog
from ..kit.mage_kit_factory import MageKitFactory
from ..kit.ranger_kit_factory import RangerKitFactory
from ..kit.starter_kit_factory import StarterKitFactory
from ..kit.warrior_kit_factory import WarriorKitFactory


class HeroClass(Enum):

    # код, название, стартовое здоровье, фабрика стартового набора, шанс уклонения, прочность барьера
    WARRIOR = ("warrior", "Воин", 120, WarriorKitFactory, 0, 0)
    RANGER = ("ranger", "Следопыт", 100, RangerKitFactory, 0.15, 0)
    MAGE = ("mage", "Маг", 85, MageKitFactory, 0, 30)

    def __init__(
        self, code: str, display_name: str, base_health: int,
        kit_factory: type[StarterKitFactory], evasion: float, barrier: int,
    ) -> None:
        self.code = code
        self.display_name = display_name
        self.base_health = base_health
        self._kit_factory = kit_factory
        self.evasion = evasion
        self.barrier = barrier

    # каждый класс сам знает свою фабрику стартового снаряжения
    def starter_kit(self, catalog: ItemCatalog) -> StarterKitFactory:
        return self._kit_factory(catalog)

    # каждый класс сам собирает свою цепочку защиты: уклонение -> броня -> барьер;
    # звенья, которых у класса нет, в цепочку просто не попадают
    def create_defense(self, armor: Armor, level: int) -> DamageHandler:
        evasion = self.evasion
        barrier = self.barrier
        # с ростом уровня защита дополняется
        if self is HeroClass.WARRIOR and level >= 3:
            barrier = 20
        elif self is HeroClass.RANGER and level >= 5:
            barrier = 15
        elif self is HeroClass.MAGE and level >= 3:
            evasion = 0.10

        armor_handler = ArmorHandler(armor.defense)
        first: DamageHandler = armor_handler

        if evasion > 0:
            first = EvasionHandler(evasion)
            first.set_next(armor_handler)
        if barrier > 0:
            armor_handler.set_next(BarrierHandler(barrier))

        return first

    @classmethod
    def by_code(cls, code: str) -> HeroClass:
        for hero_class in cls:
            if hero_class.code == code:
                return hero_class

        raise UnknownCodeError("Класс героя", code)
