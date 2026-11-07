from __future__ import annotations

from abc import ABC, abstractmethod

from ..hero.hero import Hero


# контракт хранилища сохранений: найти героя по имени, получить всех, сохранить
class HeroRepository(ABC):

    @abstractmethod
    def find_by_name(self, name: str) -> Hero | None: ...

    @abstractmethod
    def find_all(self) -> list[Hero]: ...

    @abstractmethod
    def save(self, hero: Hero) -> None: ...
