import json
import os
from math import sqrt
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

path = os.path.dirname(__file__)
cp_multipliers_file = path + '/game_data/cp_multipliers.json'

with open(cp_multipliers_file) as f:
    cpms: dict = json.load(f)

stat_stages = {
    -4: 0.50,
    -3: 0.57,
    -2: 0.67,
    -1: 0.8,
    0: 1.0,
    1: 1.25,
    2: 1.5,
    3: 1.75,
    4: 2.0
}


class Species:
    def __init__(self, **kwargs):
        """
        name: str
        species: str
        types: list[Type]
        base_attack: int
        base_defense: int
        base_hp: int
        fast_movee_pool: list[Move]
        charged_move_pool: list[Move]
        """
        self.name: str = kwargs.get("name")
        self.species: str = kwargs.get("species")
        self.types: list = kwargs.get("types")
        self.base_attack: int = kwargs.get("base_attack")
        self.base_defense: int = kwargs.get("base_defense")
        self.base_hp: int = kwargs.get("base_hp")
        self.fast_move_pool: list = kwargs.get("fast_move_pool")
        self.charged_move_pool: list = kwargs.get("charged_move_pool")

    def __str__(self):
        return self.name


class Pokemon:
    def __init__(self, **kwargs):
        """
        The physical representation of a Pokemon in the game.

        - species: Species
        - current_hp: int
        - hp_iv: int
        - attack_iv: int
        - defense_iv: int
        - level: float
        - fast_move: Move
        - charged_move_1: Move
        - charged_move_2: Optional[Move]
        - shadow: bool
        - attack_stages: int (range from -4 to +4)
        - defense_stages: int (range from -4 to +4)


        """

        # check if all the types are correct

        if not isinstance(kwargs.get("current_hp"), int):
            raise ValueError("current_hp must be of type int, not " + str(type(kwargs.get("current_hp"))))
        if not isinstance(kwargs.get("hp_iv"), int):
            raise ValueError("hp_iv must be of type int, not " + str(type(kwargs.get("hp_iv"))))
        if not isinstance(kwargs.get("attack_iv"), int):
            raise ValueError("attack_iv must be of type int, not " + str(type(kwargs.get("attack_iv"))))
        if not isinstance(kwargs.get("defense_iv"), int):
            raise ValueError("defense_iv must be of type int, not " + str(type(kwargs.get("defense_iv"))))
        if not isinstance(kwargs.get("level"), float):
            raise ValueError("level must be of type float, not " + str(type(kwargs.get("level"))))
        if not isinstance(kwargs.get("shadow"), bool):
            raise ValueError("shadow must be of type bool, not " + str(type(kwargs.get("shadow"))))
        if not isinstance(kwargs.get("attack_stages"), int):
            raise ValueError("attack_stages must be of type int, not " + str(type(kwargs.get("attack_stages"))))
        if not isinstance(kwargs.get("defense_stages"), int):
            raise ValueError("defense_stages must be of type int, not " + str(type(kwargs.get("defense_stages"))))

        self.species: Species = kwargs.get("species")
        self.current_hp: int = kwargs.get("current_hp")
        self.hp_iv: int = kwargs.get("hp_iv")
        self.attack_iv: int = kwargs.get("attack_iv")
        self.defense_iv: int = kwargs.get("defense_iv")
        self.level: float = kwargs.get("level")
        self.shadow: bool = kwargs.get("shadow", False)
        self.attack_stages: int = kwargs.get("attack_stages", 0)
        self.defense_stages: int = kwargs.get("defense_stages", 0)

    def get_true_attack(self, include_shadow: bool = False) -> float:
        shadow_multiplier = 6 / 5 if self.shadow and include_shadow else 1.0
        return (self.species.base_attack + self.attack_iv) * self.get_cp_multiplier() * self.get_stage_multiplier(
            self.attack_stages) * shadow_multiplier

    def get_current_attack(self) -> float:
        return (self.species.base_attack + self.attack_iv) * self.get_cp_multiplier()

    def get_true_defense(self, include_shadow: bool = False) -> float:
        shadow_multiplier = 5 / 6 if self.shadow and include_shadow else 1.0

        return (self.species.base_defense + self.defense_iv) * self.get_cp_multiplier() * self.get_stage_multiplier(
            self.defense_stages) * shadow_multiplier

    def get_current_defense(self) -> float:
        return (self.species.base_defense + self.defense_iv) * self.get_cp_multiplier()

    def get_true_hp(self) -> int:
        return int((self.species.base_hp + self.hp_iv) * self.get_cp_multiplier())

    def get_current_hp(self) -> int:
        return self.get_true_hp()

    def get_cp_multiplier(self) -> float:
        return float(cpms[str(self.level)])

    def get_cp(self):
        return int(
            (self.species.base_attack + self.attack_iv)
            * sqrt(self.species.base_defense + self.defense_iv)
            * sqrt(self.species.base_hp + self.hp_iv)
            * self.get_cp_multiplier() ** 2
            / 10
        )

    @staticmethod
    def get_stage_multiplier(stage: int) -> float:
        return stat_stages.get(stage, 1.0)

    def __str__(self):
        return self.species.name


def parse_pokemon_string(raw_pokemon_string: str) -> str:
    final_string = ""
    for phrase in raw_pokemon_string.replace("-", "-_").split("_"):
        final_string += phrase.capitalize() + " "
    return final_string.strip().replace("- ", "-")


def get_pokemon_species_by_name(pokemon_species_dict: dict, name: str) -> Species:
    return pokemon_species_dict.get(name)
