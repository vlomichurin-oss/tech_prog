# результат получения урона: сколько прошло, было ли уклонение и сколько поглотил барьер.
# объект изменяемый - его по очереди меняют звенья цепочки защиты
class Damage:

    def __init__(self, amount: int) -> None:
        self._amount = amount
        self._evaded = False
        self._absorbed = 0

    def reduce_to(self, amount: int) -> None:
        self._amount = amount

    def evade(self) -> None:
        self._amount = 0
        self._evaded = True

    def absorb(self, value: int) -> None:
        self._amount -= value
        self._absorbed += value

    @property
    def amount(self) -> int:
        return self._amount

    @property
    def evaded(self) -> bool:
        return self._evaded

    @property
    def absorbed(self) -> int:
        return self._absorbed
