from ..defense.armor_handler import ArmorHandler
from .abstract_enemy import AbstractEnemy

RESISTANCE = 0.3


# скелет: кости работают как броня, поэтому защита - звено ArmorHandler
class Skeleton(AbstractEnemy):

    def __init__(self) -> None:
        super().__init__("skeleton", "Скелет", 110, 10, 24, 90, 70, ArmorHandler(RESISTANCE))
