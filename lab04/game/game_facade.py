from __future__ import annotations

from pathlib import Path

from ..camp.merchant import Merchant
from ..combat.outcome import Outcome
from ..core.unknown_code_error import UnknownCodeError
from ..event.game_event import GameEvent
from ..event.game_event_publisher import GameEventPublisher
from ..event.game_event_type import GameEventType
from ..hero.hero import Hero
from ..hero.hero_class import HeroClass
from ..item.default_catalog import (
    CHAINMAIL, ELVEN_BOW, EMBER_STAFF, IRON_SWORD, PLATE_ARMOR, create_default_catalog,
)
from ..item.item import Item
from ..progress.achievement_tracker import AchievementTracker
from ..progress.expedition_journal import ExpeditionJournal
from ..storage.caching_hero_repository import CachingHeroRepository
from ..storage.file_hero_repository import FileHeroRepository
from ..storage.hero_repository import HeroRepository
from ..tactic.aggressive_tactic import AggressiveTactic
from ..tactic.balanced_tactic import BalancedTactic
from ..tactic.cautious_tactic import CautiousTactic
from ..tactic.tactic import Tactic
from ..world.crypt import Crypt
from ..world.dragon_lair import DragonLair
from ..world.expedition_report import ExpeditionReport
from ..world.forest import Forest
from ..world.haunted_manor import HauntedManor
from ..world.location import Location
from ..world.location_registry import LocationRegistry


# Фасад: простой интерфейс ко всей игре. Внутри он создает и связывает подсистемы
# (каталог, локации, тактики, торговца, хранилище с заместителем, издателя событий и подписчиков),
# а наружу отдает несколько понятных операций. Своей игровой логики у фасада нет - только связи
class GameFacade:

    def __init__(self, save_file: Path) -> None:
        self._catalog = create_default_catalog()
        self._locations = LocationRegistry([
            Forest(self._catalog),
            HauntedManor(self._catalog),
            Crypt(self._catalog),
            DragonLair(self._catalog),
        ])
        self._tactics: list[Tactic] = [BalancedTactic(), AggressiveTactic(), CautiousTactic()]
        self._merchant = Merchant(self._catalog, [
            IRON_SWORD, ELVEN_BOW, EMBER_STAFF, CHAINMAIL, PLATE_ARMOR,
        ])
        # заместитель с кэшем оборачивает файловое хранилище
        self._heroes: HeroRepository = CachingHeroRepository(FileHeroRepository(save_file, self._catalog))

        # здесь настраиваются связи издателя и подписчиков
        self._events = GameEventPublisher()
        self._journal = ExpeditionJournal()
        achievements = AchievementTracker()
        self._events.subscribe(GameEventType.VICTORY, achievements)
        self._events.subscribe(GameEventType.LEVEL_UP, achievements)
        self._events.subscribe(GameEventType.VICTORY, self._journal)
        self._events.subscribe(GameEventType.DEFEAT, self._journal)

    @property
    def hero_classes(self) -> list[HeroClass]:
        return list(HeroClass)

    def starter_kit(self, hero_class_code: str) -> list[Item]:
        kit = HeroClass.by_code(hero_class_code).starter_kit(self._catalog)
        return [kit.create_weapon(), kit.create_armor()]

    @property
    def locations(self) -> list[Location]:
        return self._locations.all

    def location(self, code: str) -> Location:
        return self._locations.get(code)

    @property
    def tactics(self) -> list[Tactic]:
        return list(self._tactics)

    def tactic(self, code: str) -> Tactic:
        for tactic in self._tactics:
            if tactic.code == code:
                return tactic

        raise UnknownCodeError("Тактика", code)

    @property
    def showcase(self) -> list[Item]:
        return self._merchant.showcase

    def sell_price(self, item: Item) -> int:
        return self._merchant.sell_price(item)

    @property
    def heroes(self) -> list[Hero]:
        return self._heroes.find_all()

    def hero(self, name: str) -> Hero:
        hero = self._heroes.find_by_name(name)
        if hero is None:
            raise ValueError(f"Героя с именем {name} нет")

        return hero

    def create_hero(self, name: str, hero_class_code: str) -> Hero:
        if self._heroes.find_by_name(name) is not None:
            raise ValueError(f"Герой с именем {name} уже есть")

        hero_class = HeroClass.by_code(hero_class_code)
        hero = (
            Hero.Builder()
            .set_name(name)
            .set_hero_class(hero_class)
            .set_starter_kit(hero_class.starter_kit(self._catalog))
            .build()
        )
        self._heroes.save(hero)
        return hero

    def explore(self, hero_name: str, location_code: str, tactic_code: str) -> ExpeditionReport:
        hero = self.hero(hero_name)
        report = self._locations.get(location_code).explore(hero, self.tactic(tactic_code))

        # отправка событий: о том, кто на них подписан, фасаду знать не нужно
        result = GameEventType.VICTORY if report.battle.outcome is Outcome.VICTORY else GameEventType.DEFEAT
        self._events.publish(GameEvent(result, hero, report))
        if report.rewards.levels_gained > 0:
            self._events.publish(GameEvent(GameEventType.LEVEL_UP, hero, report))

        self._heroes.save(hero)
        return report

    def equip(self, hero_name: str, inventory_index: int) -> Item:
        hero = self.hero(hero_name)
        item = hero.inventory[inventory_index]
        hero.equip(item)
        self._heroes.save(hero)
        return item

    def buy(self, hero_name: str, item_code: str) -> Item:
        hero = self.hero(hero_name)
        item = self._merchant.buy(hero, item_code)
        self._heroes.save(hero)
        return item

    def sell(self, hero_name: str, inventory_index: int) -> int:
        hero = self.hero(hero_name)
        price = self._merchant.sell(hero, hero.inventory[inventory_index])
        self._heroes.save(hero)
        return price

    def journal(self, hero_name: str) -> list[ExpeditionReport]:
        return self._journal.entries(hero_name)
