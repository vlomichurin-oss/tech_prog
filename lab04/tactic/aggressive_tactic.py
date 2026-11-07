from ..combat.combatant import Combatant
from .action import Action
from .tactic import Tactic


class AggressiveTactic(Tactic):

    @property
    def code(self) -> str:
        return "aggressive"

    @property
    def display_name(self) -> str:
        return "Натиск"

    @property
    def description(self) -> str:
        return "совершать безрассудные удары, пока у врага больше здоровья, чем у героя"

    def choose_action(self, round_number: int, hero: Combatant, enemy: Combatant) -> Action:
        return Action.POWER_STRIKE if enemy.health > hero.health else Action.ATTACK
