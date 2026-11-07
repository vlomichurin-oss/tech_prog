from ..combat.combatant import Combatant
from .action import Action
from .tactic import Tactic

LOW_HEALTH = 0.4


class CautiousTactic(Tactic):

    @property
    def code(self) -> str:
        return "cautious"

    @property
    def display_name(self) -> str:
        return "Осторожность"

    @property
    def description(self) -> str:
        return "при здоровье ниже 40% через раунд уходить в оборону"

    def choose_action(self, round_number: int, hero: Combatant, enemy: Combatant) -> Action:
        wounded = hero.health < hero.max_health * LOW_HEALTH
        return Action.DEFEND if wounded and round_number % 2 == 0 else Action.ATTACK
