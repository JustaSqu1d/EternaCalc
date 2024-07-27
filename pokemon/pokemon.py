from math import sqrt
import json
import os
from enum import Enum

path = os.path.dirname(__file__)
cp_multipliers_file = path + '/game_data/cp_multipliers.json'

with open(cp_multipliers_file) as f:
    cpms: dict = json.load(f)

stat_stages = {
    -4: 4/8,
    -3: 4/7,
    -2: 4/6,
    -1: 4/5,
    0: 4/4,
    1: 5/4,
    2: 6/4,
    3: 7/4,
    4: 8/4
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

    def to_dict(self) -> dict:

        string_types = []
        for type in self.types:
            string_types.append(type.name)

        fast_move_pool_dict = []
        for move in self.fast_move_pool:
            fast_move_pool_dict.append(move.to_dict())

        charged_move_pool_dict = []
        for move in self.charged_move_pool:
            charged_move_pool_dict.append(move.to_dict())

        return {
            "name": self.name,
            "species": self.species,
            "types": string_types,
            "base_attack": self.base_attack,
            "base_defense": self.base_defense,
            "base_hp": self.base_hp,
            "fast_move_pool": fast_move_pool_dict,
            "charged_move_pool": charged_move_pool_dict
        }

    @classmethod
    def get_pokemon_species_by_name(cls, name: str, pokemon_species_dict: dict | None = None) -> 'Species':
        """
        Returns the Pokémon species object by name.

        :param pokemon_species_dict: List of Pokémon species dictionary
                                     If None, it will load the default list from the game_data folder.
        :param name: The name of the Pokémon species to retrieve.
        :return: The Pokémon species object.
        """
        from .moves import Move  # resolve circular import

        if pokemon_species_dict is None:
            with open("pokemon/game_data/pokemon.json", "r") as f:
                pokemon_species_dict = json.load(f)

        name = cls.re_parse_pokemon_string(name)

        pokemon_dict = pokemon_species_dict.get(name, pokemon_species_dict.get("UNOWN"))

        pokemon_name = cls.parse_pokemon_string(pokemon_dict["name"])
        species_name = pokemon_dict["species"]

        types = []
        for raw_type_string in pokemon_dict["types"]:
            if raw_type_string:

                types.append(parse_type_string(raw_type_string))

        base_attack = pokemon_dict["base_attack"]
        base_defense = pokemon_dict["base_defense"]
        base_hp = pokemon_dict["base_hp"]

        fast_move_pool = []
        for raw_move_string in pokemon_dict["fast_move_pool"]:
            fast_move_pool.append(Move.get_move_by_name(raw_move_string))

        charged_move_pool = []
        for raw_move_string in pokemon_dict["charged_move_pool"]:
            charged_move_pool.append(Move.get_move_by_name(raw_move_string))

        species = cls(
            name=pokemon_name,
            species=species_name,
            types=types,
            base_attack=base_attack,
            base_defense=base_defense,
            base_hp=base_hp,
            fast_move_pool=fast_move_pool,
            charged_move_pool=charged_move_pool
        )

        return species

    @staticmethod
    def parse_pokemon_string(raw_pokemon_string: str) -> str:
        final_string = ""
        for phrase in raw_pokemon_string.replace("-", "-_").split("_"):
            final_string += phrase.capitalize() + " "
        return final_string.strip().replace("- ", "-")

    @staticmethod
    def re_parse_pokemon_string(raw_pokemon_string: str) -> str:
        final_string = ""
        for phrase in raw_pokemon_string.split():
            final_string += phrase + "_"
        return final_string[:-1].replace(" ", "-").upper()


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
        return max(
            int((self.species.base_hp + self.hp_iv) * self.get_cp_multiplier()),
            10
        )

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

multiplier_dict = {
    "SUPER_EFFECTIVE": 1.6,
    "NEUTRAL": 1.0,
    "NOT_VERY_EFFECTIVE": 0.625,
    "IMMUNE": 0.390625,
}


class Type(Enum):
    NORMAL = "Normal"
    FIRE = "Fire"
    WATER = "Water"
    ELECTRIC = "Electric"
    GRASS = "Grass"
    ICE = "Ice"
    FIGHTING = "Fighting"
    POISON = "Poison"
    GROUND = "Ground"
    FLYING = "Flying"
    PSYCHIC = "Psychic"
    BUG = "Bug"
    ROCK = "Rock"
    GHOST = "Ghost"
    DRAGON = "Dragon"
    DARK = "Dark"
    STEEL = "Steel"
    FAIRY = "Fairy"

    @classmethod
    def _missing_(cls, value):
        return cls.NORMAL

    def __str__(self):
        return self.value


TYPE_CIRCLES = {
    Type.FLYING: 23,
    Type.FIGHTING: 23,
    Type.GRASS: 23,
    Type.STEEL: 24,
    Type.GHOST: 25,
    Type.BUG: 27,
    Type.POISON: 28,
    Type.FIRE: 28,
    Type.WATER: 28,
    Type.ELECTRIC: 28,
    Type.GROUND: 29,
    Type.ROCK: 32,
    Type.ICE: 32,
    Type.DARK: 32,
    Type.DRAGON: 35,
    Type.PSYCHIC: 37,
    Type.FAIRY: 37,
    Type.NORMAL: 45
}

TYPE_EXCELLENT_THRESHOLDS = {
    Type.FLYING: 23,
    Type.FIGHTING: 23,
    Type.GRASS: 23,
    Type.STEEL: 23,
    Type.GHOST: 24,
    Type.BUG: 26,
    Type.POISON: 27,
    Type.FIRE: 27,
    Type.WATER: 27,
    Type.ELECTRIC: 27,
    Type.GROUND: 28,
    Type.ROCK: 31,
    Type.ICE: 31,
    Type.DARK: 31,
    Type.DRAGON: 34,
    Type.PSYCHIC: 36,
    Type.FAIRY: 36,
    Type.NORMAL: 43
}


def get_type_circle(type: Type) -> int:
    """
    Returns the number of circles to reach "excellent" for a given type.

    Parameters
    ----------
    type : Type
        The type of the move.

    Returns
    -------
    int
        The number of circles to reach "excellent". If the type is not found, it will return -1.

    """
    return TYPE_EXCELLENT_THRESHOLDS.get(type, -1)


def list_types():
    return [_.value for _ in Type]


def get_type_multiplier(attacker_type: Type, defender_types: list[Type]) -> float:
    """
    Calculates the type effectiveness multiplier for an attack based on the attacker's type and the defender's types.

    Parameters
    ----------
    attacker_type : Type
        The type of the move.
    defender_types : list[Type]
        The types of the defending Pokémon.

    Returns
    -------
    float
        The type effectiveness multiplier.
    """

    path = os.path.dirname(__file__)
    type_chart_file = path + '/game_data/type_chart.json'

    with open(type_chart_file, "r") as f:
        type_chart = json.load(f)

    multiplier = 1.0

    for defender_type in defender_types:
        effectiveness_string = type_chart.get(attacker_type.value).get(defender_type.value, "NEUTRAL")
        multiplier *= multiplier_dict.get(effectiveness_string, 1.0)

    return multiplier


def parse_type_string(raw_type_string: str) -> Type:
    """
    Parses a type string and returns the Type object.

    This is useful for converting the raw string from the game data.

    Parameters
    ----------
    raw_type_string : str
        The raw type string.

    Returns
    -------
    Type
        The Type object.
    """
    return Type(raw_type_string.split("_")[-1].capitalize())


def get_path_to_file(type: Type) -> str:
    file_name = ""
    match type:
        case Type.NORMAL:
            file_name = "ico_0_normal.png"
        case Type.FIGHTING:
            file_name = "ico_1_fighting.png"
        case Type.FLYING:
            file_name = "ico_2_flying.png"
        case Type.POISON:
            file_name = "ico_3_poison.png"
        case Type.GROUND:
            file_name = "ico_4_ground.png"
        case Type.ROCK:
            file_name = "ico_5_rock.png"
        case Type.BUG:
            file_name = "ico_6_bug.png"
        case Type.GHOST:
            file_name = "ico_7_ghost.png"
        case Type.STEEL:
            file_name = "ico_8_steel.png"
        case Type.FIRE:
            file_name = "ico_9_fire.png"
        case Type.WATER:
            file_name = "ico_10_water.png"
        case Type.GRASS:
            file_name = "ico_11_grass.png"
        case Type.ELECTRIC:
            file_name = "ico_12_electric.png"
        case Type.PSYCHIC:
            file_name = "ico_13_psychic.png"
        case Type.ICE:
            file_name = "ico_14_ice.png"
        case Type.DRAGON:
            file_name = "ico_15_dragon.png"
        case Type.DARK:
            file_name = "ico_16_dark.png"
        case Type.FAIRY:
            file_name = "ico_17_fairy.png"

    return f"assets/{file_name}"
