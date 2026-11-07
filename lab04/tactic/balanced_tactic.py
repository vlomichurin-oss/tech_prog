from ..combat.combatant import Combatant
from .action import Action
from .tactic import Tactic


class BalancedTactic(Tactic):

    @property
    def code(self) -> str:
        return "balanced"

    @property
    def display_name(self) -> str:
        return "Баланс"

    @property
    def description(self) -> str:
        return "обычный удар каждый раунд"

    def choose_action(self, round_number: int, hero: Combatant, enemy: Combatant) -> Action:
        return Action.ATTACK
