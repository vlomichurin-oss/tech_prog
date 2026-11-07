from ..combat.hit import Hit
from ..core.dice import Dice
from ..defense.armor_handler import ArmorHandler
from .abstract_enemy import AbstractEnemy

RESISTANCE = 0.25
FIRE_BREATH_CHANCE = 0.25
FIRE_BREATH_MULTIPLIER = 2


# дракон защищен чешуей (броня в цепочке защиты) и время от времени дышит огнем
class Dragon(AbstractEnemy):

    def __init__(self) -> None:
        super().__init__("dragon", "Дракон", 260, 16, 22, 500, 400, ArmorHandler(RESISTANCE))

    def roll_damage(self) -> Hit:
        bite = super().roll_damage()
        if Dice().chance(FIRE_BREATH_CHANCE):
            return Hit(bite.damage * FIRE_BREATH_MULTIPLIER, True)

        return bite
