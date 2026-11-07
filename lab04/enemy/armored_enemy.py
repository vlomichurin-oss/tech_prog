from ..defense.damage import Damage
from .enemy_decorator import EnemyDecorator


# бронированный враг: уменьшает входящий урон вдвое и передает остаток дальше по цепочке декораторов
class ArmoredEnemy(EnemyDecorator):

    @property
    def name(self) -> str:
        return "Бронированный " + super().name

    def receive_hit(self, amount: int) -> Damage:
        if amount < 0:
            raise ValueError("Урон не может быть отрицательным")
        if amount == 0:
            return Damage(0)

        return super().receive_hit(amount - amount // 2)
