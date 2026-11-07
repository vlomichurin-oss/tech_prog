from .damage import Damage
from .damage_handler import DamageHandler


# магический барьер поглощает урон, пока у него есть запас прочности
class BarrierHandler(DamageHandler):

    def __init__(self, strength: int) -> None:
        super().__init__()
        self._strength = strength

    def handle(self, damage: Damage) -> None:
        absorbed = min(self._strength, damage.amount)
        if absorbed > 0:
            self._strength -= absorbed
            damage.absorb(absorbed)

        self._pass_to_next(damage)
