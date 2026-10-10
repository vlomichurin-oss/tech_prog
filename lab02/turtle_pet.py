from animal import Animal

TURTLE_ART = r"""  _____     ____
 /      \  |  o |
|        |/ ___\|
|_________/
|_|_| |_|_|
"""


class Turtle(Animal):

    def __init__(self, name: str, age: int) -> None:
        super().__init__(name, age)

    def get_age_in_human_years(self) -> int:
        if self.get_age() <= 0:
            return 0
        return 15 + (self.get_age() - 1) * 2

    def express(self) -> None:
        print(TURTLE_ART)
