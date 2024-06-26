import json

from pokemon import Species, parse_pokemon_string, get_pokemon_species_by_name
from type import Type, parse_type_string


def is_boosted(mega: Species, target: Species) -> bool:
    """
    Determines if a Mega Evolution/Primal Reversion is boosted against a target.

    Args:
        mega: The Mega Evolution/Primal Reversion.
        target: The target Pokémon.

    Returns:
        True if the Mega Evolution boosts the target Pokemon, False otherwise.
    """

    boosted_types = mega.types

    if mega.species.lower() == "rayquaza":
        boosted_types.append(Type.PSYCHIC)
    elif mega.species.lower() == "Groudon":
        boosted_types.append(Type.GRASS)
    elif mega.species.lower() == "Kyogre":
        boosted_types.append(Type.ELECTRIC)
        boosted_types.append(Type.ICE)

    return any(_ in boosted_types for _ in target.types)


def find_best_mega(targets: list[Species] | list[PokemonWeight], megas: list[Species] | None = None) -> list[dict]:
    """
    Finds the best Mega Evolution/Primal Reversion against a list of target Pokémon.

    Args:
        targets: The list of target Pokémon.
        megas: The list of Mega Evolutions/Primal Reversions.
                Defaults to None, in which case all Mega Evolutions/Primal Reversions are considered.

    Returns:
        A list of Mega Evolutions/Primal Reversions sorted by their weight against the target Pokémon.

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

    targets_final = []

    for target in targets:
        if isinstance(target, Species):
            targets_final.append(PokemonWeight(target, 1))
        elif isinstance(target, str):
            targets_final.append(PokemonWeight(get_pokemon_species_by_name(name=target), 1))
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

    Returns:
        A list of all Mega Evolutions/Primal Reversions.
    """

    with open("game_data/pokemon.json", "r") as f:
        pokemon_json = json.load(f)

    megas = []

    for pokemon_json_key in pokemon_json:

        name = parse_pokemon_string(pokemon_json[pokemon_json_key]["name"])
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


class PokemonWeight:
    def __init__(self, pokemon: Species | str, weight: int):
        self.pokemon = pokemon if isinstance(pokemon, Species) else get_pokemon_species_by_name(name=pokemon)
        self.weight = weight
