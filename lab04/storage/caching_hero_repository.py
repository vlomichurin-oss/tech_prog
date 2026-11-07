from __future__ import annotations

from ..hero.hero import Hero
from .hero_repository import HeroRepository


# Заместитель: тот же интерфейс HeroRepository, но перед обращением к настоящему хранилищу проверяет кэш.
# кэш заполняется лениво: пока героев никто не попросил, файл даже не читается
class CachingHeroRepository(HeroRepository):

    def __init__(self, target: HeroRepository) -> None:
        self._target = target
        self._cache: dict[str, Hero] | None = None

    def find_by_name(self, name: str) -> Hero | None:
        return self._cached().get(name)

    def find_all(self) -> list[Hero]:
        return list(self._cached().values())

    # запись идет в оба места, иначе кэш разойдется с файлом
    def save(self, hero: Hero) -> None:
        self._target.save(hero)
        self._cached()[hero.name] = hero

    def _cached(self) -> dict[str, Hero]:
        if self._cache is None:
            self._cache = {hero.name: hero for hero in self._target.find_all()}

        return self._cache
