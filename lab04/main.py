from __future__ import annotations

# позволяет запускать файл напрямую (python3 main.py / кнопка Run в VS Code):
# добавляем родительскую папку в sys.path и говорим Python, что файл - часть пакета
if __name__ == "__main__" and not __package__:
    import sys
    from pathlib import Path

    _package_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(_package_dir.parent))
    __package__ = _package_dir.name

from pathlib import Path
from typing import Sequence

from .combat.outcome import Outcome
from .console_view import ConsoleView
from .game.game_facade import GameFacade
from .item.item import Item

# файл сохранения лежит рядом с кодом игры, откуда бы ее ни запустили
SAVE_FILE = Path(__file__).resolve().parent / "saves" / "heroes.json"
VIEW = ConsoleView()


# игровой цикл работает только с фасадом и помнит лишь имя текущего героя
def main() -> None:
    print(f"Файл сохранения: {SAVE_FILE}")
    game = GameFacade(SAVE_FILE)
    hero_name = choose_hero(game)

    while True:
        print()
        VIEW.print_hero(game.hero(hero_name))
        print("1 - отправиться в экспедицию, 2 - снаряжение, 3 - торговец, 4 - журнал экспедиций, 0 - выйти из игры")
        choice = input().strip()
        if choice == "1":
            go_on_expedition(game, hero_name)
        elif choice == "2":
            manage_equipment(game, hero_name)
        elif choice == "3":
            visit_merchant(game, hero_name)
        elif choice == "4":
            print_journal(game, hero_name)
        elif choice == "0":
            return
        else:
            print("Такого варианта нет")


# выбор сохраненного героя или создание нового
def choose_hero(game: GameFacade) -> str:
    saved = game.heroes
    if saved:
        print("Выберите героя (0 - создать нового):")
        for i, hero in enumerate(saved):
            print(f"{i + 1} - {hero.name}, {hero.hero_class.display_name} {hero.level} ур.")
        index = read_choice(len(saved))
        if index >= 0:
            name = saved[index].name
            print(f"{name} возвращается в лагерь на опушке мистического леса.")
            return name

    name = create_hero(game)
    print(f"{name} разбивает лагерь на опушке мистического леса.")
    return name


def create_hero(game: GameFacade) -> str:
    print("Создайте своего героя!")
    while True:
        print("Выберите класс:")
        hero_classes = game.hero_classes
        for i, hero_class in enumerate(hero_classes):
            weapon, armor = game.starter_kit(hero_class.code)
            print(
                f"{i + 1} - {hero_class.display_name} (здоровье {hero_class.base_health}, "
                f"{VIEW.describe_hero_class(hero_class)}): {VIEW.describe(weapon)}, {VIEW.describe(armor)}"
            )
        class_index = read_choice(len(hero_classes))
        if class_index < 0:
            continue

        print("Введите имя:")
        name = input().strip()

        try:
            return game.create_hero(name, hero_classes[class_index].code).name
        except ValueError as error:
            print(f"Не получилось создать героя: {error}")


def go_on_expedition(game: GameFacade, hero_name: str) -> None:
    locations = game.locations
    print("Куда отправимся?")
    for i, location in enumerate(locations):
        print(f"{i + 1} - {location.display_name} (рекомендуемый уровень {location.recommended_level})")
    location_index = read_choice(len(locations))
    if location_index < 0:
        return

    tactics = game.tactics
    print("Какой тактики держаться в бою?")
    for i, tactic in enumerate(tactics):
        print(f"{i + 1} - {tactic.display_name}: {tactic.description}")
    tactic_index = read_choice(len(tactics))
    if tactic_index < 0:
        return

    location = locations[location_index]
    report = game.explore(hero_name, location.code, tactics[tactic_index].code)
    print()
    VIEW.print_report(report, location.display_name)

    if report.battle.outcome == Outcome.VICTORY and report.battle.enemy.code == "dragon":
        print(f"\nДракон повержен! Барды еще долго будут петь о подвиге героя по имени {hero_name}.")


def manage_equipment(game: GameFacade, hero_name: str) -> None:
    inventory = game.hero(hero_name).inventory
    if not inventory:
        print("Инвентарь пуст")
        return

    print("Что экипировать? (0 - назад)")
    print_items(inventory)
    index = read_choice(len(inventory))
    if index < 0:
        return

    item = game.equip(hero_name, index)
    print("Экипировано: " + VIEW.describe(item))


def visit_merchant(game: GameFacade, hero_name: str) -> None:
    print(f'Торговец: "Чего желаешь?" (золото: {game.hero(hero_name).gold})')
    print("1 - купить, 2 - продать, 0 - назад")
    choice = input().strip()
    if choice == "1":
        buy(game, hero_name)
    elif choice == "2":
        sell(game, hero_name)


def buy(game: GameFacade, hero_name: str) -> None:
    showcase = game.showcase
    for i, item in enumerate(showcase):
        print(f"{i + 1} - {VIEW.describe(item)}: {item.price} золота")
    index = read_choice(len(showcase))
    if index < 0:
        return

    try:
        item = game.buy(hero_name, showcase[index].code)
        print("Куплено: " + VIEW.describe(item))
    except ValueError as error:
        print(error)


def sell(game: GameFacade, hero_name: str) -> None:
    inventory = game.hero(hero_name).inventory
    if not inventory:
        print("Продавать нечего (экипированные предметы продать нельзя)")
        return

    for i, item in enumerate(inventory):
        print(f"{i + 1} - {VIEW.describe(item)}: {game.sell_price(item)} золота")
    index = read_choice(len(inventory))
    if index < 0:
        return

    item_name = inventory[index].name
    price = game.sell(hero_name, index)
    print(f"Продано: {item_name} за {price} золота")


def print_journal(game: GameFacade, hero_name: str) -> None:
    journal = game.journal(hero_name)
    if not journal:
        print("В этот раз экспедиций еще не было")
        return

    for i, report in enumerate(journal):
        summary = VIEW.summarize(
            report,
            game.location(report.location_code).display_name,
            game.tactic(report.tactic_code).display_name,
        )
        print(f"{i + 1}. {summary}")


def print_items(items: Sequence[Item]) -> None:
    for i, item in enumerate(items):
        print(f"{i + 1} - {VIEW.describe(item)}")


# читает номер варианта от 1 до count, возвращает индекс или -1, если ввели что-то другое
def read_choice(count: int) -> int:
    try:
        choice = int(input().strip())
        if 1 <= choice <= count:
            return choice - 1
    except ValueError:
        # некорректный ввод обрабатываем так же, как отказ от выбора
        pass

    return -1


if __name__ == "__main__":
    main()
