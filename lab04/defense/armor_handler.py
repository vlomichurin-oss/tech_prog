from .damage import Damage
from .damage_handler import DamageHandler


# броня гасит долю урона и передает остаток следующему звену;
# то же правило раньше было зашито в герое, скелете и драконе, теперь оно в одном месте
class ArmorHandler(DamageHandler):

    def __init__(self, defense: float) -> None:
        super().__init__()
        self._defense = defense

    def handle(self, damage: Damage) -> None:
        reduced = round(damage.amount * (1 - self._defense))
        # хотя бы единицу урона броня пропускает всегда
        damage.reduce_to(max(1, reduced))
        self._pass_to_next(damage)
