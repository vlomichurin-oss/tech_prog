from abc import ABC, abstractmethod

from ..combat.combatant import Combatant
from .action import Action


# Стратегия: общий интерфейс для всех тактик боя
class Tactic(ABC):

    @property
    @abstractmethod
    def code(self) -> str: ...

    @property
    @abstractmethod
    def display_name(self) -> str: ...

    @property
    @abstractmethod
    def description(self) -> str: ...

    # алгоритм, которым тактики отличаются друг от друга: что делать герою в этом раунде
    @abstractmethod
    def choose_action(self, round_number: int, hero: Combatant, enemy: Combatant) -> Action: ...
