from typing import Optional

from pet import Pet  


class Person:

    def __init__(self, name: str, pet: Optional[Pet] = None) -> None:
        self.__name = name
        self.__pet = pet

    def set_pet(self, pet: Pet) -> None:
        self.__pet = pet

    def get_pet_info(self) -> None:
        print("--------------------")
        if self.__pet is None:
            print(f"{self.__name} has no pet yet")
            print("--------------------")
            return

        pet = self.__pet
        print(f"Pet for {self.__name} is named {pet.get_name()}")
        print(f"Age: {pet.get_age()} year(s), about {pet.get_age_in_human_years()} human years")
        print("And it expresses itself like this:")
        pet.express()
        print("--------------------")
