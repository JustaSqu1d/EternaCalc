import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pokemon import Type


class Move:
    """
    Representing a move.

    Attributes
    ----------
    name: str
        The name of the move.
    unique_id: str
        The unique ID of the move.
    type: Type
        The type of the move.
    power: int
        The power of the move.
    energy: int
        The energy cost of the move.
    turns: int
        The number of turns the move takes.
    usage_type: Literal["fast", "charge"]
        The type of move.
    """
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

    @staticmethod
    def parse_move_string(raw_move_string: str) -> str:
        """
        Parses a move string and returns the formatted name.

        Parameters
        ----------
        raw_move_string : str
            The raw move string.

        Returns
        -------
        str
            The formatted move name.
        """
        raw_move_string = raw_move_string.replace("FAST", "")
        return " ".join(word.capitalize() for word in raw_move_string.split("_"))


    @classmethod
    def get_move_by_name(cls, name: str) -> 'Move':
        """
        Returns a move object by name.

        Parameters
        ----------
        name : str
            The name of the move.

        Returns
        -------
        Move
            The move object. If the move is not found, it will return the STRUGGLE move, instead.
        """
        from .pokemon import parse_type_string  # fix circular import

        with open("pokemon/game_data/moves.json", "r") as f:
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

        return cls.get_move_by_name("STRUGGLE")
