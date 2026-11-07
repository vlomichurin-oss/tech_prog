from __future__ import annotations

# позволяет запускать файл напрямую (python3 demo.py / кнопка Run в VS Code):
# добавляем родительскую папку в sys.path и говорим Python, что файл - часть пакета
if __name__ == "__main__" and not __package__:
    import sys
    from pathlib import Path

    _package_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(_package_dir.parent))
    __package__ = _package_dir.name

import os
import tempfile
from pathlib import Path

from .console_view import ConsoleView
from .core.dice import Dice
from .defense.armor_handler import ArmorHandler
from .defense.barrier_handler import BarrierHandler
from .defense.damage import Damage
from .defense.damage_handler import DamageHandler
from .defense.evasion_handler import EvasionHandler
from .enemy.armored_enemy import ArmoredEnemy
from .enemy.dragon import Dragon
from .enemy.enemy import Enemy
from .enemy.goblin import Goblin
from .enemy.haunted_weapon import HauntedWeapon
from .enemy.legendary_enemy import LegendaryEnemy
from .enemy.windfury_enemy import WindfuryEnemy
from .event.game_event import GameEvent
from .event.game_event_listener import GameEventListener
from .event.game_event_publisher import GameEventPublisher
from .event.game_event_type import GameEventType
from .game.game_facade import GameFacade
from .hero.hero import Hero
from .hero.hero_class import HeroClass
from .item.default_catalog import ELVEN_BOW, create_default_catalog
from .item.item_catalog import ItemCatalog
from .progress.achievement_tracker import AchievementTracker
from .progress.expedition_journal import ExpeditionJournal
from .storage.caching_hero_repository import CachingHeroRepository
from .storage.file_hero_repository import FileHeroRepository
from .tactic.aggressive_tactic import AggressiveTactic
from .tactic.balanced_tactic import BalancedTactic
from .tactic.cautious_tactic import CautiousTactic
from .world.crypt import Crypt
from .world.expedition_report import ExpeditionReport
from .world.forest import Forest
from .world.haunted_manor import HauntedManor

VIEW = ConsoleView()


# третий подписчик, чтобы было видно: издателю все равно, кто и сколько на него подписано
class PrintListener(GameEventListener):

    def on_event(self, event: GameEvent) -> None:
        print(f"Событие {event.type.name}: герой {event.hero.name}")


def main() -> None:
    catalog = create_default_catalog()
    dice = Dice()

    print("===== Цепочка обязанностей =====")
    armor_only = ArmorHandler(0.3)
    print_hits("Броня 30%", armor_only, 2)

    armor_and_barrier = ArmorHandler(0.3)
    armor_and_barrier.set_next(BarrierHandler(30))
    print_hits("Броня 30% -> барьер 30", armor_and_barrier, 3)

    dice.reseed(3)
    full_chain = EvasionHandler(0.5)
    full_chain.set_next(ArmorHandler(0.3)).set_next(BarrierHandler(30))
    print_hits("Уклонение 50% -> броня 30% -> барьер 30", full_chain, 3)

    print()
    print("===== Стратегия =====")
    crypt = Crypt(catalog)
    for tactic in (BalancedTactic(), AggressiveTactic(), CautiousTactic()):
        mage = new_hero("Мерлин", HeroClass.MAGE, 2, catalog)
        report = crypt.explore(mage, tactic, seed=3)
        print(
            f"{tactic.display_name}: {describe_outcome(report)}, раундов {count_rounds(report)}, "
            f"у героя осталось {mage.health}/{mage.max_health} здоровья"
        )

    print()
    print("===== Декоратор =====")
    enemies: list[Enemy] = [
        Goblin(),
        LegendaryEnemy(Goblin()),
        WindfuryEnemy(Goblin()),
        LegendaryEnemy(WindfuryEnemy(Goblin())),
        ArmoredEnemy(Goblin()),
        ArmoredEnemy(LegendaryEnemy(WindfuryEnemy(Dragon()))),
    ]
    for enemy in enemies:
        dice.reseed(5)
        hits = [str(enemy.roll_damage().damage) for _ in range(3)]
        received = enemy.receive_hit(20)
        print(
            f"{enemy.name}: удары {', '.join(hits)}, награда {enemy.experience_reward} опыта; "
            f"входящий урон 20 -> {received.amount}, здоровье {enemy.health}/{enemy.max_health}"
        )

    print()
    print("===== Адаптер =====")
    bow = catalog.create_weapon(ELVEN_BOW)
    haunted_bow = HauntedWeapon(bow)
    print("Предмет: " + VIEW.describe(bow))
    print(
        f"Враг:    {haunted_bow.name} ({haunted_bow.max_health} здоровья, "
        f"награда {haunted_bow.experience_reward} опыта)"
    )
    manor = HauntedManor(catalog)
    ranger = new_hero("Леголас", HeroClass.RANGER, 2, catalog)
    VIEW.print_report(manor.explore(ranger, CautiousTactic(), seed=55), manor.display_name)

    print()
    print("===== Наблюдатель =====")
    events = GameEventPublisher()
    journal = ExpeditionJournal()
    achievements = AchievementTracker()
    events.subscribe(GameEventType.VICTORY, achievements)
    events.subscribe(GameEventType.VICTORY, journal)
    events.subscribe(GameEventType.DEFEAT, journal)
    events.subscribe(GameEventType.VICTORY, PrintListener())

    warrior = new_hero("Артур", HeroClass.WARRIOR, 1, catalog)
    forest = Forest(catalog)
    victory = forest.explore(warrior, BalancedTactic(), seed=7)
    events.publish(GameEvent(GameEventType.VICTORY, warrior, victory))
    print("Достижения героя: " + describe_achievements(warrior))
    print(f"Записей в журнале: {len(journal.entries(warrior.name))}")

    print()
    print("===== Заместитель =====")
    save_file = temp_file("heroes")
    file = FileHeroRepository(save_file, catalog)
    file.save(warrior)
    print("Содержимое файла:")
    print(save_file.read_text(encoding="utf-8"), end="")
    print(
        "Без заместителя два поиска дают один и тот же объект: "
        f"{file.find_by_name('Артур') is file.find_by_name('Артур')}"
    )
    cached = CachingHeroRepository(file)
    from_cache = cached.find_by_name("Артур")
    print(f"С заместителем два поиска дают один и тот же объект: {from_cache is cached.find_by_name('Артур')}")
    from_cache.add_gold(100)
    cached.save(from_cache)
    print(f"После сохранения через заместитель золото героя в файле: {file.find_by_name('Артур').gold}")
    save_file.unlink()

    print()
    print("===== Фасад =====")
    game_file = temp_file("game")
    game = GameFacade(game_file)
    game.create_hero("Гэндальф", HeroClass.MAGE.code)
    dice.reseed(2)
    expedition = game.explore("Гэндальф", Forest.CODE, "cautious")
    summary = VIEW.summarize(
        expedition,
        game.location(expedition.location_code).display_name,
        game.tactic(expedition.tactic_code).display_name,
    )
    print("Экспедиция через фасад: " + summary)
    VIEW.print_hero(game.hero("Гэндальф"))
    game_file.unlink()


def new_hero(name: str, hero_class: HeroClass, level: int, catalog: ItemCatalog) -> Hero:
    return (
        Hero.Builder()
        .set_name(name)
        .set_hero_class(hero_class)
        .set_starter_kit(hero_class.starter_kit(catalog))
        .set_level(level)
        .build()
    )


# прогоняет через цепочку несколько ударов по 30 урона и печатает, что с каждым стало
def print_hits(title: str, chain: DamageHandler, count: int) -> None:
    results = []
    for _ in range(count):
        damage = Damage(30)
        chain.handle(damage)
        if damage.evaded:
            results.append("уклонение")
        elif damage.absorbed > 0:
            results.append(f"поглощено {damage.absorbed}, прошло {damage.amount}")
        else:
            results.append(f"прошло {damage.amount}")
    print(f"{title}: {'; '.join(results)}")


def describe_outcome(report: ExpeditionReport) -> str:
    return "победа" if report.battle.outcome.name == "VICTORY" else "поражение"


def count_rounds(report: ExpeditionReport) -> int:
    return report.battle.events[-1].round


def describe_achievements(hero: Hero) -> str:
    return ", ".join(achievement.display_name for achievement in hero.achievements)


# пустой временный файл - чтобы демонстрация не трогала настоящие сохранения
def temp_file(prefix: str) -> Path:
    descriptor, path = tempfile.mkstemp(prefix=prefix, suffix=".json")
    os.close(descriptor)
    return Path(path)


if __name__ == "__main__":
    main()
