from __future__ import annotations

from typing import TYPE_CHECKING

from .pokemon import get_type_multiplier, get_type_circle

if TYPE_CHECKING:
    from pokemon import Pokemon
    from moves import Move


def calculate_damage_ranges(attacker: Pokemon, defender: Pokemon, move: Move) -> list[int]:
    """
    Calculates the damage dealt by an attacker to a defender using a specific move.

    Parameters
    ----------
    attacker : Pokemon
        The Pokémon that is attacking.
    defender : Pokemon
        The Pokémon that is defending.
    move : Move
        The move that the attacker is using.

    Returns
    -------
    list[int]
        A list of damage ranges.
        If the move is a charge move, it will return a list of possible damage rolls.
    """

    half_circle_rule = 0.5  # I made the name up

    attack = attacker.get_true_attack(include_shadow=True)

    defense = defender.get_true_defense(include_shadow=True)

    trainer_constant = 1.3

    stab_multiplier = 1.2 if move.type in attacker.species.types else 1.0

    type_multiplier = get_type_multiplier(move.type, defender.species.types)

    modifiers = trainer_constant * stab_multiplier * type_multiplier

    if move.usage_type == "charge":

        damage_rolls = list()

        damage_rolls.append(1)  # damage if the move is shielded

        circles = get_type_circle(move.type)

        base_percentage = 0.25

        for _ in range(circles + 1):
            damage = int(
                half_circle_rule * move.power * attack / defense * base_percentage * modifiers
            ) + 1
            damage_rolls.append(damage)
            base_percentage += 0.75 / circles
            base_percentage = min(base_percentage, 1.0)

        return sorted(list(damage_rolls))  # cast set to list

    else:
        return [int(half_circle_rule * move.power * attack / defense * modifiers) + 1]
