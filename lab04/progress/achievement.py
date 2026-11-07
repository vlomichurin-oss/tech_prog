from __future__ import annotations

from enum import Enum

from ..core.unknown_code_error import UnknownCodeError


class Achievement(Enum):

    FIRST_BLOOD = ("first-blood", "Первая кровь", "одержать первую победу")
    LUCKY = ("lucky", "Счастливчик", "найти зачарованный лут")
    VETERAN = ("veteran", "Ветеран", "достичь 5 уровня")
    DRAGON_SLAYER = ("dragon-slayer", "Драконоборец", "победить дракона")

    def __init__(self, code: str, display_name: str, description: str) -> None:
        self.code = code
        self.display_name = display_name
        self.description = description

    @classmethod
    def by_code(cls, code: str) -> Achievement:
        for achievement in cls:
            if achievement.code == code:
                return achievement

        raise UnknownCodeError("Достижение", code)
