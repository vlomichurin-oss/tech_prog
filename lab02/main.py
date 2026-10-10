from parrot import Parrot
from person import Person
from turtle_pet import Turtle


def main() -> None:
    kesha = Parrot("Kesha", 2)
    zavala = Turtle("Zavala", 4)
    kesha.happy_birthday()

    jack = Person("Jack", kesha)
    john = Person("John")

    jack.get_pet_info()
    john.get_pet_info()

    john.set_pet(zavala)
    john.get_pet_info()


if __name__ == "__main__":
    main()
