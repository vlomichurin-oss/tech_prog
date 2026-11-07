from __future__ import annotations

from typing import Iterable

from ..combat.combatant import Combatant
from ..combat.hit import Hit
from ..defense.damage import Damage
from ..defense.damage_handler import DamageHandler
from ..item.armor import Armor
from ..item.item import Item
from ..item.weapon import Weapon
from ..kit.starter_kit_factory import StarterKitFactory
from ..progress.achievement import Achievement
from .hero_class import HeroClass

MAX_NAME_LENGTH = 20
STARTING_GOLD = 50
HEALTH_PER_LEVEL = 15
DAMAGE_PER_LEVEL = 3
EXPERIENCE_PER_LEVEL = 100


class Hero(Combatant):

    # героя создают только через строителя: Hero.Builder()...build(),
    # поэтому конструктор принимает в себя билдера, из которого и берет значения полей
    def __init__(self, builder: Hero.Builder) -> None:
        self._name: str = builder.name
        self._hero_class: HeroClass = builder.hero_class
        self._level = builder.level
        # опыт, инвентарь и достижения теперь тоже приходят из строителя - так восстанавливаем героя из сохранения
        self._experience = builder.experience
        self._gold = builder.gold
        self._weapon: Weapon = builder.weapon
        self._armor: Armor = builder.armor
        self._inventory: list[Item] = list(builder.inventory)
        # достижения сохраняются вместе с героем
        self._achievements: list[Achievement] = list(builder.achievements)
        self._health = 0
        self._defense: DamageHandler | None = None
        self.rest()

    # внутренний класс билдер - чтобы удобно и безопасно создавать героев
    class Builder:

        def __init__(self) -> None:
            self.name: str | None = None
            self.hero_class: HeroClass | None = None
            self.weapon: Weapon | None = None
            self.armor: Armor | None = None
            # необязательные поля сразу получают значения по умолчанию
            self.level = 1
            self.experience = 0
            self.gold = STARTING_GOLD
            self.inventory: tuple[Item, ...] = ()
            self.achievements: tuple[Achievement, ...] = ()

        def set_name(self, name: str) -> Hero.Builder:
            self.name = name
            return self

        def set_hero_class(self, hero_class: HeroClass) -> Hero.Builder:
            self.hero_class = hero_class
            return self

        def set_weapon(self, weapon: Weapon) -> Hero.Builder:
            self.weapon = weapon
            return self

        def set_armor(self, armor: Armor) -> Hero.Builder:
            self.armor = armor
            return self

        # берет оружие и броню из стартового набора
        def set_starter_kit(self, starter_kit: StarterKitFactory) -> Hero.Builder:
            self.weapon = starter_kit.create_weapon()
            self.armor = starter_kit.create_armor()
            return self

        def set_level(self, level: int) -> Hero.Builder:
            self.level = level
            return self

        def set_experience(self, experience: int) -> Hero.Builder:
            self.experience = experience
            return self

        def set_gold(self, gold: int) -> Hero.Builder:
            self.gold = gold
            return self

        def set_inventory(self, inventory: Iterable[Item]) -> Hero.Builder:
            self.inventory = tuple(inventory)
            return self

        def set_achievements(self, achievements: Iterable[Achievement]) -> Hero.Builder:
            self.achievements = tuple(achievements)
            return self

        # перед созданием героя проверяем, что все обязательные поля заполнены корректно
        def build(self) -> Hero:
            if self.name is None or not self.name.strip():
                raise ValueError("У героя должно быть имя")
            if len(self.name) > MAX_NAME_LENGTH:
                raise ValueError(f"Имя героя не может быть длиннее {MAX_NAME_LENGTH} символов")
            if self.hero_class is None:
                raise ValueError("Не выбран класс героя")
            if self.weapon is None or self.armor is None:
                raise ValueError("Герою нужны оружие и броня")
            if self.level < 1:
                raise ValueError("Уровень героя не может быть меньше 1")
            if self.experience < 0:
                raise ValueError("Опыта не может быть меньше нуля")
            if self.gold < 0:
                raise ValueError("Золота не может быть меньше нуля")

            return Hero(self)

    def roll_damage(self) -> Hit:
        hit = self._weapon.roll_damage()
        return Hit(hit.damage + (self._level - 1) * DAMAGE_PER_LEVEL, hit.critical)

    # урон герой больше не считает сам, а передает в первое звено своей цепочки защиты
    def receive_hit(self, amount: int) -> Damage:
        damage = Damage(amount)
        self._defense.handle(damage)
        self._health = max(0, self._health - damage.amount)
        return damage

    def is_alive(self) -> bool:
        return self._health > 0

    # поведение героя между экспедициями

    # отдых перед экспедицией: здоровье восстанавливается, а цепочка защиты собирается заново,
    # поэтому барьер снова полный, а новые способности по уровню начинают действовать
    def rest(self) -> None:
        self._health = self.max_health
        self._defense = self._hero_class.create_defense(self._armor, self._level)

    # начисляет опыт, возвращает количество полученных уровней
    def gain_experience(self, amount: int) -> int:
        self._experience += amount
        levels_gained = 0
        while self._experience >= self.experience_to_next_level:
            self._experience -= self.experience_to_next_level
            self._level += 1
            levels_gained += 1

        return levels_gained

    def add_gold(self, amount: int) -> None:
        self._gold += amount

    def spend_gold(self, amount: int) -> None:
        if amount > self._gold:
            raise ValueError(f"Не хватает золота: нужно {amount}, есть {self._gold}")

        self._gold -= amount

    def add_item(self, item: Item) -> None:
        self._inventory.append(item)

    def remove_item(self, item: Item) -> None:
        if item not in self._inventory:
            raise ValueError(f"В инвентаре нет предмета {item.name}")

        self._inventory.remove(item)

    # экипирует предмет из инвентаря, снятый предмет возвращается в инвентарь
    def equip(self, item: Item) -> None:
        if isinstance(item, Weapon):
            self.remove_item(item)
            self._inventory.append(self._weapon)
            self._weapon = item
        elif isinstance(item, Armor):
            self.remove_item(item)
            self._inventory.append(self._armor)
            self._armor = item
            # после смены брони защита сразу учитывает новую броню
            self._defense = self._hero_class.create_defense(self._armor, self._level)
        else:
            raise ValueError(f"Предмет нельзя экипировать: {item.name}")

    # выдает достижение, возвращает False, если оно уже было
    def unlock(self, achievement: Achievement) -> bool:
        if achievement in self._achievements:
            return False

        self._achievements.append(achievement)
        return True

    # свойства только для чтения

    @property
    def code(self) -> str:
        return self._hero_class.code

    @property
    def name(self) -> str:
        return self._name

    @property
    def health(self) -> int:
        return self._health

    @property
    def max_health(self) -> int:
        return self._hero_class.base_health + (self._level - 1) * HEALTH_PER_LEVEL

    @property
    def hero_class(self) -> HeroClass:
        return self._hero_class

    @property
    def level(self) -> int:
        return self._level

    @property
    def experience(self) -> int:
        return self._experience

    @property
    def experience_to_next_level(self) -> int:
        return self._level * EXPERIENCE_PER_LEVEL

    @property
    def gold(self) -> int:
        return self._gold

    @property
    def weapon(self) -> Weapon:
        return self._weapon

    @property
    def armor(self) -> Armor:
        return self._armor

    @property
    def inventory(self) -> tuple[Item, ...]:
        return tuple(self._inventory)

    @property
    def achievements(self) -> tuple[Achievement, ...]:
        return tuple(self._achievements)
