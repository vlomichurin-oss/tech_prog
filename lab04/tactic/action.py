from enum import Enum


# что герой может сделать в раунде: множитель исходящего и множитель входящего урона
class Action(Enum):

    ATTACK = (1.0, 1.0)
    POWER_STRIKE = (1.5, 1.5)
    DEFEND = (0.5, 0.3)

    def __init__(self, attack_multiplier: float, incoming_multiplier: float) -> None:
        self.attack_multiplier = attack_multiplier
        self.incoming_multiplier = incoming_multiplier
