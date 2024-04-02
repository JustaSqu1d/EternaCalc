import json
import os
from enum import Enum

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

    def __str__(self):
        return self.value


def list_types():
    return [_.value for _ in Type]


def get_type_multiplier(attacker_type: Type, defender_types: list[Type]):
    """
    Calculates the type effectiveness multiplier for an attack based on the attacker's type and the defender's types.

    Args:
        attacker_type: The type of the attacking move.
        defender_types: A list of the defender's types (single or dual type).

    Returns:
        The type effectiveness multiplier as a float.
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
    return Type(raw_type_string.split("_")[-1].capitalize())


def get_path_to_file(type: Type):
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
