from __future__ import annotations
import json

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pokemon import Species, Type


class PokemonWeight:
    """
    A class representing a Pokémon and its weight.

    Used for calculating the best Mega Evolution/Primal Reversion against a list of target Pokémon.

    Attributes
    ----------
    pokemon: Union[:class:`.Species`, :class:`str`]
        The Pokémon. If a string is provided, it will be converted to a :class:`.Species` object.
    weight: Union[:class:`int`, :class:`float`]
        The weight of the Pokémon.

    Raises
    ------
    ValueError
        The Pokémon name is invalid.
    """
    def __init__(self, pokemon: Species | str, weight: int | float):
        from pokemon import Species  # resolve circular import
        if isinstance(pokemon, str):
            pokemon = Species.get_pokemon_species_by_name(name=pokemon)
            if not pokemon:
                raise ValueError(f"Invalid Pokémon name: {str}")

        self.pokemon = pokemon
        self.weight = weight


def is_boosted(mega: Species, target: Species) -> bool:
    """
    Determines if a Mega Evolution/Primal Reversion is boosted against a target.

    Parameters
    ----------
    mega: :class:`.Species`
        The Mega Evolution/Primal Reversion.
    target: :class:`.Species`
        The target Pokémon.

    Returns
    -------
    :class:`bool`
        Whether the Mega Evolution/Primal Reversion is boosted against the target.
    """

    boosted_types = mega.types

    if mega.species.lower() == "rayquaza":
        boosted_types.append(Type.PSYCHIC)
    elif mega.species.lower() == "groudon":
        boosted_types.append(Type.GRASS)
    elif mega.species.lower() == "kyogre":
        boosted_types.append(Type.ELECTRIC)
        boosted_types.append(Type.ICE)

    return any(_ in boosted_types for _ in target.types)


def find_best_mega(targets: list[Species] | list[PokemonWeight], megas: list[Species] | None = None) -> list[dict]:
    """
    Finds the best Mega Evolution/Primal Reversion against a list of target Pokémon.

    :param targets: The list of target Pokémon.
    :param megas: The list of Mega Evolutions/Primal Reversions.

    :return: A list of dictionaries containing the Mega Evolution/Primal Reversion, its weight, and the raw count of targets it is boosted against.
        Example:
            [
                {
                    "mega": "Mega Charizard X",
                    "weight": 15
                    "raw_count": 3
                },
                {
                    "mega": "Mega Charizard Y",
                    "weight": 10
                    "raw_count": 2
                }
            ]
    """
    from pokemon import Species  # resolve circular import

    targets_final = []

    for target in targets:
        if isinstance(target, Species):
            targets_final.append(PokemonWeight(target, 1))
        elif isinstance(target, str):
            targets_final.append(PokemonWeight(Species.get_pokemon_species_by_name(name=target), 1))
        else:
            targets_final.append(target)

    megas = megas or fetch_all_megas()

    mega_data: list[dict] = []

    for mega in megas:
        mega_weight: int = 0
        mega_raw_count: int = 0
        for target in targets_final:
            if is_boosted(mega, target.pokemon):
                mega_weight += target.weight
                mega_raw_count += 1
        mega_data.append(
            {
                "mega": mega,
                "weight": mega_weight,
                "raw_count": mega_raw_count
            }
        )

    # sort the mega_data by weight
    mega_data.sort(key=lambda x: x["weight"], reverse=True)

    return mega_data


def fetch_all_megas() -> list[Species]:
    """
    Fetches all Mega Evolutions/Primal Reversions.

    Returns
    -------
    list[:class:`.Species`]
        A list of all Mega Evolutions/Primal Reversions.
    """
    from pokemon import Species, parse_type_string  # resolve circular import

    with open("pokemon/game_data/pokemon.json", "r") as f:
        pokemon_json = json.load(f)

    megas = []

    for pokemon_json_key in pokemon_json:

        name = Species.parse_pokemon_string(pokemon_json[pokemon_json_key]["name"])
        species_name = pokemon_json[pokemon_json_key]["species"]

        if (not name.startswith("Mega ")) and (not name.startswith("Primal ")):
            continue

        types = []
        for raw_type_string in pokemon_json[pokemon_json_key]["types"]:
            if raw_type_string:
                types.append(parse_type_string(raw_type_string))

        species = Species(
            name=name,
            species=species_name,
            types=types
        )

        megas.append(species)

    return megas
