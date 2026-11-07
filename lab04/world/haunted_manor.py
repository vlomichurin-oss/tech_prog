from ..core.dice import Dice
from ..enemy.enemy import Enemy
from ..enemy.haunted_weapon import HauntedWeapon
from ..item.default_catalog import ELVEN_BOW, EMBER_STAFF, IRON_SWORD, PLATE_ARMOR
from ..item.item_catalog import ItemCatalog
from .location import Location

# оружие, которое может стать одержимым
HAUNTED_WEAPONS = (IRON_SWORD, ELVEN_BOW, EMBER_STAFF)


class HauntedManor(Location):

    CODE = "haunted-manor"

    def __init__(self, catalog: ItemCatalog) -> None:
        super().__init__(HauntedManor.CODE, "Проклятый особняк", 2, catalog)

    # в фабричном методе берем одно из оружий и оборачиваем его в адаптер - оно становится одержимым
    def _create_enemy(self) -> Enemy:
        weapon = self._item_catalog.create_weapon(Dice().pick(HAUNTED_WEAPONS))
        return HauntedWeapon(weapon)

    @property
    def _loot_table(self) -> tuple[str, ...]:
        return (IRON_SWORD, ELVEN_BOW, EMBER_STAFF, PLATE_ARMOR)
