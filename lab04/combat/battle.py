from __future__ import annotations

from ..tactic.action import Action
from ..tactic.tactic import Tactic
from .battle_event import BattleEvent
from .battle_report import BattleReport
from .combatant import Combatant
from .event_type import EventType
from .outcome import Outcome
from .participant import Participant
from .side import Side


# бой идет по раундам: сначала бьет герой, потом враг, пока кто-то не погибнет
class Battle:

    # стратегия прокидывается в конструктор и сохраняется в поле, потому что применяется на весь бой
    def __init__(self, hero: Combatant, enemy: Combatant, tactic: Tactic) -> None:
        self._hero = hero
        self._enemy = enemy
        self._tactic = tactic
        self._events: list[BattleEvent] = []
        self._round = 0

    def run(self) -> BattleReport:
        while self._hero.is_alive() and self._enemy.is_alive():
            self._round += 1
            # использование стратегии: действие зависит от того, какой алгоритм выбрал игрок
            action = self._tactic.choose_action(self._round, self._hero, self._enemy)
            self._announce(action)

            self._strike(self._hero, Side.HERO, self._enemy, Side.ENEMY, action.attack_multiplier)
            if self._enemy.is_alive():
                self._strike(self._enemy, Side.ENEMY, self._hero, Side.HERO, action.incoming_multiplier)

        outcome = Outcome.VICTORY if self._hero.is_alive() else Outcome.DEFEAT
        return BattleReport(
            Participant.of(self._hero), Participant.of(self._enemy), outcome, tuple(self._events)
        )

    def _announce(self, action: Action) -> None:
        if action is Action.POWER_STRIKE:
            self._emit(BattleEvent(self._round, EventType.POWER_STRIKE, Side.HERO, Side.ENEMY, 0, 0))
        elif action is Action.DEFEND:
            self._emit(BattleEvent(self._round, EventType.DEFEND, Side.HERO, Side.HERO, 0, 0))

    def _strike(
        self, attacker: Combatant, source: Side, defender: Combatant, target: Side, multiplier: float
    ) -> None:
        hit = attacker.roll_damage()
        amount = max(1, round(hit.damage * multiplier))
        # полученный урон теперь хранится в Damage: видно, было ли уклонение и сколько поглотил барьер
        damage = defender.receive_hit(amount)

        if damage.evaded:
            self._emit(BattleEvent(self._round, EventType.EVADE, source, target, 0, defender.health))
            return
        if damage.absorbed > 0:
            self._emit(BattleEvent(self._round, EventType.ABSORB, source, target, damage.absorbed, defender.health))
        if damage.amount > 0:
            event_type = EventType.CRITICAL_HIT if hit.critical else EventType.HIT
            self._emit(BattleEvent(self._round, event_type, source, target, damage.amount, defender.health))

        if not defender.is_alive():
            self._emit(BattleEvent(self._round, EventType.DEATH, source, target, 0, 0))

    def _emit(self, event: BattleEvent) -> None:
        self._events.append(event)
