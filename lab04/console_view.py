from __future__ import annotations

from .combat.battle_event import BattleEvent
from .combat.battle_report import BattleReport
from .combat.event_type import EventType
from .combat.outcome import Outcome
from .combat.participant import Participant
from .combat.side import Side
from .hero.hero import Hero
from .hero.hero_class import HeroClass
from .item.item import Item
from .world.expedition_report import ExpeditionReport
from .world.rewards import Rewards


# весь вывод в консоль собран здесь
class ConsoleView:

    def describe(self, item: Item) -> str:
        description = item.name

        if item.enchantments:
            names = []
            for enchantment in item.enchantments:
                names.append(enchantment.name)
            description += " [" + ", ".join(names) + "]"

        return description + " (" + item.description + ")"

    # особенность класса героя: уклонение или магический барьер
    def describe_hero_class(self, hero_class: HeroClass) -> str:
        if hero_class.evasion > 0:
            return f"уклонение {round(hero_class.evasion * 100)}%"
        if hero_class.barrier > 0:
            return f"магический барьер {hero_class.barrier}"

        return "без особенностей"

    def print_hero(self, hero: Hero) -> None:
        print(
            f"{hero.name}, {hero.hero_class.display_name} {hero.level} ур. | здоровье {hero.max_health} | "
            f"опыт {hero.experience}/{hero.experience_to_next_level} | золото {hero.gold}"
        )
        print("  Оружие: " + self.describe(hero.weapon))
        print("  Броня:  " + self.describe(hero.armor))

        if hero.achievements:
            names = []
            for achievement in hero.achievements:
                names.append(achievement.display_name)
            print("  Достижения: " + ", ".join(names))

    def print_report(self, report: ExpeditionReport, location_name: str) -> None:
        battle = report.battle
        print(f"=== {location_name} (сид {report.seed}) ===")
        print(f"{battle.hero.name} встречает врага: {battle.enemy.name} ({battle.enemy.max_health} здоровья)")

        for event in battle.events:
            self._print_event(event, battle)

        self._print_rewards(battle, report.rewards)

    # одна строка об экспедиции - для журнала
    def summarize(self, report: ExpeditionReport, location_name: str, tactic_name: str) -> str:
        battle = report.battle
        result = "победа" if battle.outcome == Outcome.VICTORY else "поражение"
        return f'{location_name}, {battle.enemy.name}, тактика "{tactic_name}": {result}'

    def _print_event(self, event: BattleEvent, battle: BattleReport) -> None:
        source = self._participant(event.source, battle)
        target = self._participant(event.target, battle)
        prefix = f"[раунд {event.round}]"

        if event.type == EventType.HIT:
            print(
                f"{prefix} {source.name} -> {target.name}: {event.amount} урона, "
                f"осталось {event.target_health_after}/{target.max_health}"
            )
        elif event.type == EventType.CRITICAL_HIT:
            print(
                f"{prefix} {source.name} -> {target.name}: КРИТ! {event.amount} урона, "
                f"осталось {event.target_health_after}/{target.max_health}"
            )
        elif event.type == EventType.EVADE:
            print(f"{prefix} {source.name} -> {target.name}: промах, {target.name} уклоняется")
        elif event.type == EventType.ABSORB:
            print(f"{prefix} {source.name} -> {target.name}: барьер поглощает {event.amount} урона")
        elif event.type == EventType.POWER_STRIKE:
            print(f"{prefix} {source.name} бьет в полную силу")
        elif event.type == EventType.DEFEND:
            print(f"{prefix} {source.name} уходит в оборону")
        elif event.type == EventType.DEATH:
            print(f"{target.name} повержен!")

    def _print_rewards(self, battle: BattleReport, rewards: Rewards) -> None:
        if battle.outcome == Outcome.DEFEAT:
            print(f"Поражение... {battle.hero.name} едва уносит ноги и теряет {-rewards.gold} золота")
            return

        print(f"Победа! +{rewards.experience} опыта, +{rewards.gold} золота")
        if rewards.loot is not None:
            print("Добыча: " + self.describe(rewards.loot))
        if rewards.levels_gained > 0:
            print("Новый уровень!")

    def _participant(self, side: Side, battle: BattleReport) -> Participant:
        return battle.hero if side == Side.HERO else battle.enemy
