from ..core.dice import Dice
from .damage import Damage
from .damage_handler import DamageHandler


# уклонение: если сработало, удар не прошел и передавать урон дальше незачем
class EvasionHandler(DamageHandler):

    def __init__(self, chance: float) -> None:
        super().__init__()
        self._chance = chance

    def handle(self, damage: Damage) -> None:
        if Dice().chance(self._chance):
            damage.evade()
            return

        self._pass_to_next(damage)
