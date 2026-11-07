from ..combat.hit import Hit
from .enemy_decorator import EnemyDecorator

MULTIPLIER = 2


# легендарный враг: двойной урон и двойная награда.
# все методы берут за основу super() - то есть поведение обернутого объекта, - поэтому декораторы комбинируются
class LegendaryEnemy(EnemyDecorator):

    @property
    def name(self) -> str:
        return "Легендарный " + super().name

    def roll_damage(self) -> Hit:
        hit = super().roll_damage()
        return Hit(hit.damage * MULTIPLIER, hit.critical)

    @property
    def experience_reward(self) -> int:
        return super().experience_reward * MULTIPLIER

    def roll_gold_reward(self) -> int:
        return super().roll_gold_reward() * MULTIPLIER
