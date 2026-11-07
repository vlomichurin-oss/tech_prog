from __future__ import annotations

from abc import ABC, abstractmethod

from .damage import Damage


# Цепочка обязанностей: базовое звено цепочки защиты
class DamageHandler(ABC):

    def __init__(self) -> None:
        self._next: DamageHandler | None = None

    # подвешивает следующее звено и возвращает его, чтобы можно было строить цепочку подряд:
    # first.set_next(second).set_next(third)
    def set_next(self, next_handler: DamageHandler) -> DamageHandler:
        self._next = next_handler
        return next_handler

    # каждое звено само решает: обработать урон и передать дальше или остановить цепочку
    @abstractmethod
    def handle(self, damage: Damage) -> None: ...

    def _pass_to_next(self, damage: Damage) -> None:
        if self._next is not None:
            self._next.handle(damage)
