"""Интеграционные тесты сохранения в настоящий временный файл."""

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from lab04.hero.hero import Hero
from lab04.hero.hero_class import HeroClass
from lab04.item.default_catalog import create_default_catalog
from lab04.progress.achievement import Achievement
from lab04.storage.file_hero_repository import FileHeroRepository


class FileRepositoryTests(TestCase):
    def setUp(self):
        directory = self.enterContext(TemporaryDirectory())
        self.path = Path(directory) / "heroes.json"
        self.catalog = create_default_catalog()
        self.writer = FileHeroRepository(self.path, self.catalog)

    def test_missing_file_is_empty(self):
        self.assertEqual(self.writer.find_all(), [])
        self.assertIsNone(self.writer.find_by_name("Артур"))

    def test_new_repository_restores_hero(self):
        original = (
            Hero.Builder()
            .set_name("Артур")
            .set_hero_class(HeroClass.WARRIOR)
            .set_starter_kit(HeroClass.WARRIOR.starter_kit(self.catalog))
            .set_level(2)
            .set_experience(35)
            .set_gold(175)
            .set_achievements([Achievement.FIRST_BLOOD])
            .build()
        )
        self.writer.save(original)

        reader = FileHeroRepository(self.path, create_default_catalog())
        restored = reader.find_by_name("Артур")

        self.assertIsNotNone(restored)
        self.assertIsNot(restored, original)
        self.assertEqual(restored.name, "Артур")
        self.assertEqual(restored.hero_class, HeroClass.WARRIOR)
        self.assertEqual((restored.level, restored.experience, restored.gold), (2, 35, 175))
        self.assertEqual(restored.weapon.code, original.weapon.code)
        self.assertEqual(restored.armor.code, original.armor.code)
        self.assertEqual(restored.achievements, (Achievement.FIRST_BLOOD,))
