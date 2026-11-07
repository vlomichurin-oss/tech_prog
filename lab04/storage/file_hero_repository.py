from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..hero.hero import Hero
from ..hero.hero_class import HeroClass
from ..item.armor import Armor
from ..item.enchantment import Enchantment
from ..item.item import Item
from ..item.item_catalog import ItemCatalog
from ..item.weapon import Weapon
from ..progress.achievement import Achievement
from .hero_repository import HeroRepository


# сохранения в обычном файле в формате JSON: в файле лежит массив героев.
# минус этой реализации: на каждый запрос файл читается целиком, а герои собираются заново
class FileHeroRepository(HeroRepository):

    def __init__(self, file: Path, catalog: ItemCatalog) -> None:
        self._file = file
        self._catalog = catalog

    def find_by_name(self, name: str) -> Hero | None:
        for hero in self.find_all():
            if hero.name == name:
                return hero

        return None

    def find_all(self) -> list[Hero]:
        if not self._file.exists():
            return []
        text = self._read()
        if not text.strip():
            return []

        saves = json.loads(text)
        if not isinstance(saves, list):
            raise ValueError(f"Ожидался массив героев: {self._file.resolve()}")

        return [self._restore(save) for save in saves]

    def save(self, hero: Hero) -> None:
        saves = [self._snapshot(saved) for saved in self.find_all() if saved.name != hero.name]
        saves.append(self._snapshot(hero))
        # ensure_ascii=False - чтобы русские буквы в файле были буквами, а не А...
        self._write(json.dumps(saves, ensure_ascii=False, indent=2) + "\n")

    # герой -> словарь, который json умеет записать (снимок состояния)
    def _snapshot(self, hero: Hero) -> dict[str, Any]:
        return {
            "name": hero.name,
            "heroClass": hero.hero_class.code,
            "level": hero.level,
            "experience": hero.experience,
            "gold": hero.gold,
            "weapon": self._snapshot_item(hero.weapon),
            "armor": self._snapshot_item(hero.armor),
            "inventory": [self._snapshot_item(item) for item in hero.inventory],
            "achievements": [achievement.code for achievement in hero.achievements],
        }

    # предмет храним по коду шаблона и кодам зачарований - этого хватает, чтобы собрать его заново
    @staticmethod
    def _snapshot_item(item: Item) -> dict[str, Any]:
        return {"code": item.code, "enchantments": [enchantment.code for enchantment in item.enchantments]}

    # словарь из файла -> герой, собранный строителем
    def _restore(self, save: dict[str, Any]) -> Hero:
        weapon = self._restore_item(save["weapon"])
        armor = self._restore_item(save["armor"])
        if not isinstance(weapon, Weapon) or not isinstance(armor, Armor):
            raise ValueError(f"Повреждено снаряжение героя {save['name']}")

        return (
            Hero.Builder()
            .set_name(save["name"])
            .set_hero_class(HeroClass.by_code(save["heroClass"]))
            .set_level(save["level"])
            .set_experience(save["experience"])
            .set_gold(save["gold"])
            .set_weapon(weapon)
            .set_armor(armor)
            .set_inventory(self._restore_item(item) for item in save["inventory"])
            .set_achievements(Achievement.by_code(code) for code in save["achievements"])
            .build()
        )

    # предмет снова получаем копией шаблона из каталога (прототип) и накладываем зачарования
    def _restore_item(self, save: dict[str, Any]) -> Item:
        item = self._catalog.create(save["code"])
        for code in save["enchantments"]:
            item.enchant(Enchantment.by_code(code))
        return item

    def _read(self) -> str:
        try:
            return self._file.read_text(encoding="utf-8")
        except OSError as error:
            raise OSError(f"Не удалось прочитать сохранение: {self._file.resolve()}") from error

    def _write(self, text: str) -> None:
        try:
            self._file.parent.mkdir(parents=True, exist_ok=True)
            self._file.write_text(text, encoding="utf-8")
        except OSError as error:
            raise OSError(f"Не удалось записать сохранение: {self._file.resolve()}") from error
