from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from type import Type


class Move:
    def __init__(self, **kwargs):
        self.name: str = kwargs.get("name")
        self.unique_id: str = kwargs.get("unique_id")
        self.type: Type = kwargs.get("type")
        self.power: int = int(kwargs.get("power"))
        self.energy: int = int(kwargs.get("energy"))
        self.turns: int = int(kwargs.get("turns"))
        self.usage_type: str = kwargs.get("usage_type")

    def __str__(self):
        return f"({self.type}) {self.name} - {self.power}"


def parse_move_string(raw_move_string: str) -> str:
    raw_move_string = raw_move_string.replace("FAST", "")
    return " ".join(word.capitalize() for word in raw_move_string.split("_"))


def add_commas_to_number(num):
    return "{:,}".format(num)
