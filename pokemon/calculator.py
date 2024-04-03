from __future__ import annotations

from math import ceil
from typing import TYPE_CHECKING

from .type import get_type_multiplier

if TYPE_CHECKING:
    from pokemon import Pokemon
    from moves import Move


def calculate_damage_ranges(attacker: Pokemon, defender: Pokemon, move: Move) -> list[int]:
    """
    Calculates the damage dealt by an attacker to a defender using a specific move.

    Args:
        attacker: The attacking Pokémon.
        defender: The defending Pokémon.
        move: The move used by the attacker.

    Returns:
        The list of damage rolls at no charge, min. nice charge, min. great charge, and max excellent charge.
    """
    charge_multipliers = [0.25, 0.5, 0.75, 1.0]

    half_circle_rule = 0.5  # I made the name up

    attack = attacker.get_true_attack(include_shadow=True)

    defense = defender.get_true_defense(include_shadow=True)

    trainer_constant = 1.3

    stab_multiplier = 1.2 if move.type in attacker.species.types else 1.0

    type_multiplier = get_type_multiplier(move.type, defender.species.types)

    modifiers = trainer_constant * stab_multiplier * type_multiplier

    if move.usage_type == "charge":

        damage_rolls = []

        for charge_multiplier in charge_multipliers:
            damage = int(
                half_circle_rule * move.power * attack / defense * charge_multiplier * modifiers
            ) + 1
            damage_rolls.append(damage)

        return damage_rolls

    else:
        return [int(half_circle_rule * move.power * attack / defense * modifiers) + 1]


def display_calculated_damage(st, move, attacker, target):
    damage = calculate_damage_ranges(attacker, target, move)

    low_percentage = round(100 * damage[0] / target.get_true_hp(), 1)
    high_percentage = round(100 * damage[-1] / target.get_true_hp(), 1)

    low_damage = damage[0]
    high_damage = damage[-1]

    times = ceil(target.get_true_hp() / high_damage)
    if times == 1:
        times = "O"

    attacker_string = f"**{attacker.attack_iv} Atk IV Level {attacker.level} {attacker}**"
    if attacker.shadow:
        attacker_string += " :violet[(Shadow)]"
    if attacker.attack_stages > 0:
        attacker_string = f"+{attacker.attack_stages} {attacker_string}"
    elif attacker.attack_stages < 0:
        attacker_string = f"{attacker.attack_stages} {attacker_string}"

    target_string = f"**{target.hp_iv} HP / {target.defense_iv} Def IVs Level {target.level} {target}**"
    if target.shadow:
        target_string += " :violet[(Shadow)]"
    if target.defense_stages > 0:
        target_string = f"+{target.defense_stages} {target_string}"
    elif target.defense_stages < 0:
        target_string = f"{target.defense_stages} {target_string}"

    damage_per_energy = round(high_damage / move.energy, 1)

    effectiveness_text = ""
    if get_type_multiplier(move.type, target.species.types) > 1:
        effectiveness_text = ":green[It's super effective!]"
    elif get_type_multiplier(move.type, target.species.types) < 1:
        effectiveness_text = ":red[It's not very effective...]"
    damage_rolls_string = "Possible damage amounts: (" + ", ".join(
        [str(damage_roll) for damage_roll in damage]) + ")"
    st.write(
        f"**{attacker_string} {move.name} vs. {target_string}**"
    )
    st.write(f"""{effectiveness_text}  
            **{low_damage} - {high_damage} ({low_percentage}% - {high_percentage}%) -- {times}HKO**
            """)
    if move.usage_type == "charge":
        st.write(damage_rolls_string)
    st.write(f"""**{damage_per_energy} dpe**  
            {move.energy} energy""")
