from __future__ import annotations

from abc import ABC, abstractmethod

from ..combat.battle import Battle
from ..combat.outcome import Outcome
from ..core.dice import Dice
from ..enemy.armored_enemy import ArmoredEnemy
from ..enemy.enemy import Enemy
from ..enemy.legendary_enemy import LegendaryEnemy
from ..enemy.windfury_enemy import WindfuryEnemy
from ..hero.hero import Hero
from ..item.item import Item
from ..item.item_catalog import ItemCatalog
from ..tactic.balanced_tactic import BalancedTactic
from ..tactic.tactic import Tactic
from .expedition_report import ExpeditionReport
from .rewards import Rewards

LOOT_CHANCE = 0.6
ENCHANT_CHANCE = 0.3
ELITE_CHANCE = 0.2
DOUBLE_ELITE_CHANCE = 0.25
ARMORED_CHANCE = 0.3


class Location(ABC):

    def __init__(self, code: str, display_name: str, recommended_level: int, catalog: ItemCatalog) -> None:
        self._code = code
        self._display_name = display_name
        self._recommended_level = recommended_level
        self._catalog = catalog

    # фабричный метод: создание врага делегируется подклассам
    @abstractmethod
    def _create_enemy(self) -> Enemy: ...

    # коды предметов из каталога, которые можно найти в локации
    @property
    @abstractmethod
    def _loot_table(self) -> tuple[str, ...]: ...

    # бизнес-логика, общая для всех локаций:
    # герой встречает врага (возможно, элитного), сражается с ним по выбранной тактике и получает награду
    def explore(self, hero: Hero, tactic: Tactic | None = None, seed: int | None = None) -> ExpeditionReport:
        # без тактики герой бьется как раньше - сбалансированно
        if tactic is None:
            tactic = BalancedTactic()
        dice = Dice()
        if seed is None:
            seed = dice.next_seed()
        dice.reseed(seed)

        hero.rest()
        enemy = self._create_enemy()
        if dice.chance(ELITE_CHANCE):
            # усиления врага через декораторы
            enemy = self._make_elite(enemy, dice)
        battle = Battle(hero, enemy, tactic).run()

        if battle.outcome == Outcome.VICTORY:
            rewards = self._reward(hero, enemy, dice)
        else:
            rewards = self._punish(hero)

        return ExpeditionReport(seed, self._code, tactic.code, battle, rewards)

    # с помощью декораторов накладываем на врага модификаторы, причем они комбинируются
    @staticmethod
    def _make_elite(enemy: Enemy, dice: Dice) -> Enemy:
        both = dice.chance(DOUBLE_ELITE_CHANCE)
        if dice.chance(0.5):
            enemy = LegendaryEnemy(enemy)
            if both:
                enemy = WindfuryEnemy(enemy)
        else:
            enemy = WindfuryEnemy(enemy)
            if both:
                enemy = LegendaryEnemy(enemy)

        return ArmoredEnemy(enemy) if dice.chance(ARMORED_CHANCE) else enemy

    def _reward(self, hero: Hero, enemy: Enemy, dice: Dice) -> Rewards:
        experience = enemy.experience_reward
        gold = enemy.roll_gold_reward()
        loot = self._roll_loot(dice)

        levels_gained = hero.gain_experience(experience)
        hero.add_gold(gold)
        if loot is not None:
            hero.add_item(loot)

        return Rewards(experience, gold, loot, levels_gained)

    def _roll_loot(self, dice: Dice) -> Item | None:
        if not dice.chance(LOOT_CHANCE):
            return None

        # добыча - это копия шаблона из каталога, ее можно менять, не боясь испортить шаблон
        loot = self._catalog.create(dice.pick(self._loot_table))
        if dice.chance(ENCHANT_CHANCE):
            loot.enchant(dice.pick(loot.possible_enchantments))

        return loot

    # проигравший герой теряет половину золота
    @staticmethod
    def _punish(hero: Hero) -> Rewards:
        lost_gold = hero.gold // 2
        hero.spend_gold(lost_gold)
        return Rewards(0, -lost_gold, None, 0)

    # подклассам нужен доступ к каталогу (например, особняку - чтобы взять оружие)
    @property
    def _item_catalog(self) -> ItemCatalog:
        return self._catalog

    @property
    def code(self) -> str:
        return self._code

    @property
    def display_name(self) -> str:
        return self._display_name

    @property
    def recommended_level(self) -> int:
        return self._recommended_level
