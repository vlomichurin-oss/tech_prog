from ..combat.hit import Hit
from ..core.dice import Dice
from ..defense.damage import Damage
from ..item.weapon import Weapon
from .enemy import Enemy

# у оружия нет здоровья, поэтому адаптер придумывает его сам: 5 здоровья за каждую единицу урона
HEALTH_PER_DAMAGE = 5


# Адаптер: оборачивает Weapon и реализует интерфейс Enemy, не меняя ни Weapon, ни Enemy
class HauntedWeapon(Enemy):

    def __init__(self, weapon: Weapon) -> None:
        self._weapon = weapon
        self._max_health = weapon.damage * HEALTH_PER_DAMAGE
        self._health = self._max_health

    @property
    def code(self) -> str:
        return "haunted-weapon"

    # название врага берется из названия оружия
    @property
    def name(self) -> str:
        return "Одержимый " + self._weapon.name

    # нанесение урона полностью переиспользует логику оружия - тут основная ценность адаптера
    def roll_damage(self) -> Hit:
        return self._weapon.roll_damage()

    # а методы ниже адаптер реализует сам: у оружия такой логики нет
    def receive_hit(self, amount: int) -> Damage:
        damage = Damage(amount)
        self._health = max(0, self._health - damage.amount)
        return damage

    def is_alive(self) -> bool:
        return self._health > 0

    # награду за победу над одержимым оружием привязываем к его стоимости
    @property
    def experience_reward(self) -> int:
        return self._weapon.price // 2

    def roll_gold_reward(self) -> int:
        return Dice().roll(self._weapon.price // 4, self._weapon.price // 2)

    @property
    def health(self) -> int:
        return self._health

    @property
    def max_health(self) -> int:
        return self._max_health
