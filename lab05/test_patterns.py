"""Модульные тесты паттернов игры из lab04."""

import unittest
from unittest.mock import Mock, create_autospec, patch

from lab04.combat.hit import Hit
from lab04.core.dice import Dice
from lab04.defense.armor_handler import ArmorHandler
from lab04.defense.barrier_handler import BarrierHandler
from lab04.defense.damage import Damage
from lab04.defense.damage_handler import DamageHandler
from lab04.defense.evasion_handler import EvasionHandler
from lab04.enemy.armored_enemy import ArmoredEnemy
from lab04.enemy.enemy import Enemy
from lab04.enemy.haunted_weapon import HauntedWeapon
from lab04.enemy.legendary_enemy import LegendaryEnemy
from lab04.hero.hero import Hero
from lab04.item.weapon import Weapon
from lab04.storage.caching_hero_repository import CachingHeroRepository
from lab04.storage.hero_repository import HeroRepository


class DiceTests(unittest.TestCase):
    def setUp(self):
        # У каждого теста свой одиночка. После теста восстанавливается прежний.
        self.enterContext(patch.object(Dice, "_instance", None))
        self.dice = Dice()
        self.dice.reseed(42)

    def test_single_instance(self):
        self.assertIs(self.dice, Dice())

    def test_roll_bounds(self):
        self.assertEqual(self.dice.roll(7, 7), 7)
        for _ in range(50):
            self.assertIn(self.dice.roll(-2, 3), range(-2, 4))

    def test_chance_limits(self):
        self.assertFalse(self.dice.chance(0))
        self.assertTrue(self.dice.chance(1))

    def test_pick(self):
        item = object()
        self.assertIs(self.dice.pick([item]), item)
        self.assertIn(self.dice.pick(["щит", "меч"]), ["щит", "меч"])

    def test_reseed_repeats_sequence(self):
        first = [self.dice.next_seed() for _ in range(5)]
        self.dice.reseed(42)
        self.assertEqual([self.dice.next_seed() for _ in range(5)], first)


class DamageChainTests(unittest.TestCase):
    @patch("lab04.defense.evasion_handler.Dice", autospec=True)
    def test_hit_traverses_chain_in_order(self, dice):
        dice.return_value.chance.return_value = False
        first = EvasionHandler(0.3)
        first.set_next(ArmorHandler(0.25)).set_next(BarrierHandler(10))
        hit = Damage(40)

        first.handle(hit)

        dice.return_value.chance.assert_called_once_with(0.3)
        self.assertFalse(hit.evaded)
        self.assertEqual(hit.absorbed, 10)
        self.assertEqual(hit.amount, 20)

    @patch("lab04.defense.evasion_handler.Dice", autospec=True)
    def test_evasion_stops_chain(self, dice):
        dice.return_value.chance.return_value = True
        first = EvasionHandler(0.3)
        following = create_autospec(DamageHandler, instance=True)
        first.set_next(following)
        hit = Damage(40)

        first.handle(hit)

        self.assertTrue(hit.evaded)
        self.assertEqual(hit.amount, 0)
        following.handle.assert_not_called()

    def test_barrier_spends_strength_across_hits(self):
        barrier = BarrierHandler(30)
        for amount, absorbed, remaining in [(20, 20, 0), (40, 10, 30), (5, 0, 5)]:
            with self.subTest(amount=amount):
                hit = Damage(amount)
                barrier.handle(hit)
                self.assertEqual((hit.absorbed, hit.amount), (absorbed, remaining))

    def test_armor_leaves_one_point(self):
        hit = Damage(5)
        ArmorHandler(1.0).handle(hit)
        self.assertEqual(hit.amount, 1)


class CacheTests(unittest.TestCase):
    def setUp(self):
        self.storage = create_autospec(HeroRepository, instance=True)
        self.cache = CachingHeroRepository(self.storage)

    def test_loads_lazily_and_reads_once(self):
        hero = Mock(spec=Hero)
        hero.name = "Артур"
        self.storage.find_all.return_value = [hero]
        self.storage.find_all.assert_not_called()

        self.assertIs(self.cache.find_by_name("Артур"), hero)
        self.assertIs(self.cache.find_by_name("Артур"), hero)
        self.storage.find_all.assert_called_once_with()

    def test_empty_result_is_cached(self):
        self.storage.find_all.return_value = []
        self.assertIsNone(self.cache.find_by_name("Артур"))
        self.assertEqual(self.cache.find_all(), [])
        self.storage.find_all.assert_called_once_with()

    def test_save_updates_warm_cache(self):
        old = Mock(spec=Hero)
        old.name = "Артур"
        updated = Mock(spec=Hero)
        updated.name = "Артур"
        self.storage.find_all.return_value = [old]
        self.assertIs(self.cache.find_by_name("Артур"), old)

        self.cache.save(updated)

        self.storage.save.assert_called_once_with(updated)
        self.assertEqual(self.cache.find_all(), [updated])
        self.storage.find_all.assert_called_once_with()


class AdapterTests(unittest.TestCase):
    def test_weapon_supplies_attack_and_adapter_tracks_health(self):
        weapon = Mock(spec=Weapon)
        weapon.damage = 8
        hit = Hit(12, True)
        weapon.roll_damage.return_value = hit
        enemy = HauntedWeapon(weapon)

        self.assertIs(enemy.roll_damage(), hit)
        weapon.roll_damage.assert_called_once_with()
        self.assertEqual(enemy.health, 40)
        enemy.receive_hit(9)
        self.assertEqual(enemy.health, 31)
        enemy.receive_hit(50)
        self.assertFalse(enemy.is_alive())
        self.assertEqual(enemy.health, 0)


class DecoratorTests(unittest.TestCase):
    def test_stacked_modifiers_delegate_to_enemy(self):
        base = Mock(spec=Enemy)
        base.roll_damage.return_value = Hit(7, True)
        base.receive_hit.return_value = Damage(5)
        enemy = ArmoredEnemy(LegendaryEnemy(base))

        self.assertEqual(enemy.roll_damage(), Hit(14, True))
        base.roll_damage.assert_called_once_with()
        self.assertIs(enemy.receive_hit(9), base.receive_hit.return_value)
        base.receive_hit.assert_called_once_with(5)
