import json
from typing import TYPE_CHECKING

from type import parse_type_string

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

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "unique_id": self.unique_id,
            "type": self.type.name,
            "power": self.power,
            "energy": self.energy,
            "turns": self.turns,
            "usage_type": self.usage_type
        }


def parse_move_string(raw_move_string: str) -> str:
    raw_move_string = raw_move_string.replace("FAST", "")
    return " ".join(word.capitalize() for word in raw_move_string.split("_"))


def get_move_by_name(name: str) -> Move:
    with open("game_data/moves.json", "r") as f:
        moves_json = json.load(f)

    name = name.replace(" ", "_").upper()

    for move_json_key in moves_json:
        if move_json_key == name or move_json_key == name + "_FAST":
            return Move(
                unique_id=move_json_key,
                type=parse_type_string(moves_json[move_json_key]["type"]),
                power=moves_json[move_json_key]["power"],
                energy=moves_json[move_json_key]["energyDelta"],
                turns=moves_json[move_json_key]["turns"],
                usage_type=moves_json[move_json_key]["usageType"]
            )

    return get_move_by_name("STRUGGLE")


def add_commas_to_number(num):
    return "{:,}".format(num)
