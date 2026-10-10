from abc import abstractmethod

from pet import Pet


class Animal(Pet):

    def __init__(self, name: str, age: int) -> None:
        self.__name = name
        self.__age = age

    def happy_birthday(self) -> None:
        self.__age += 1

    def get_name(self) -> str:
        return self.__name

    def get_age(self) -> int:
        return self.__age

    @abstractmethod
    def express(self) -> None:
        ...

    @abstractmethod
    def get_age_in_human_years(self) -> int:
        ...
