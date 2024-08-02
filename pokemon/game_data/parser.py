import json

import requests

moves_json = {}
pokemon_json = {}

BLACKLISTED_POKEMON_FORMS = ["UNOWN", "SPINDA", "CASTFORM", "BURMY", "WORMADAM", "CHERRIM", "SHELLOS", "GASTRODON",
                             "BASCULIN", "DEERLING", "SAWSBUCK", "FURFROU", "PUMPKABOO", "GOURGEIST"]

BLACKLISTED_WORDS = ["FAMILY", "MOVE", "HOME_FORM_REVERSION", "HOME_REVERSION", "FALL_2019", "COPY_2019",
                     "_NORMAL", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "COSTUME"]

WHITELISTED_POKEMON = ["KYUREM", "KYUREM_WHITE", "KYUREM_BLACK"]

MANUAL_NAME_CHANGES = {
    "MEWOSTIC": "MEOWSTIC_MALE",
    "JANGMO_O": "JANGMO-O",
    "HAKAMO_O": "HAKAMO-O",
    "KOMMO_O": "KOMMO-O",
    "MINIOR_BLUE": "MINIOR",
    "INDEEDEE": "INDEEDEE_MALE",
    "URSHIFU": "URSHIFU_SINGLE_STRIKE",
    "OINKOLOGNE": "OINKOLOGNE_MALE",
    "GREATTUSK": "GREAT_TUSK",
    "SCREAMTAIL": "SCREAM_TAIL",
    "BRUTEBONNET": "BRUTE_BONNET",
    "FLUTTERMANE": "FLUTTER_MANE",
    "SLITHERWING": "SLITHER_WING",
    "SANDYSHOCKS": "SANDY_SHOCKS",
    "IRONTREADS": "IRON_TREADS",
    "IRONBUNDLE": "IRON_BUNDLE",
    "IRONHANDS": "IRON_HANDS",
    "IRONJUGULIS": "IRON_JUGULIS",
    "IRONMOTH": "IRON_MOTH",
    "IRONTHORNS": "IRON_THORNS",
    "WOCHIEN": "WO-CHIEN",
    "CHIENPAO": "CHIEN-PAO",
    "TINGLU": "TING-LU",
    "CHIYU": "CHI-YU",
    "ROARINGMOON": "ROARING_MOON",
    "IRONVALIANT": "IRON_VALIANT"
}

MANUAL_MOVE_CHANGES = {
    404: "SUNSTEEL_STRIKE",
    405: "MOONGEIST_BEAM",
    462: "FORCE_PALM_FAST",
}

MANUAL_MOVE_ADDITIONS = {
    "TOXICROAK": {"name": "ICY_WIND", "type": "charged"},
    "DIALGA_ORIGIN": {"name": "ROAR_OF_TIME", "type": "charged"},
    "PALKIA_ORIGIN": {"name": "SPACIAL_REND", "type": "charged"},
    "NECROZMA_DUSK_MANE": {"name": "SUNSTEEL_STRIKE", "type": "charged"},
    "NECROZMA_DAWN_WINGS": {"name": "MOONGEIST_BEAM", "type": "charged"},
}

MANUAL_CATEGORY_CHANGES = {
    "COSMOG": "POKEMON_CLASS_ULTRA_BEAST",
    "COSMOEM": "POKEMON_CLASS_ULTRA_BEAST",
    "SOLGALEO": "POKEMON_CLASS_ULTRA_BEAST",
    "LUNALA": "POKEMON_CLASS_ULTRA_BEAST",
    "NECROZMA": "POKEMON_CLASS_ULTRA_BEAST",
    "NECROZMA_DUSK_MANE": "POKEMON_CLASS_ULTRA_BEAST",
    "NECROZMA_DAWN_WINGS": "POKEMON_CLASS_ULTRA_BEAST",
    "NECROZMA_ULTRA": "POKEMON_CLASS_ULTRA_BEAST",
}


def is_same(pokemon1, pokemon2):
    return (pokemon1["species"] == pokemon2["species"] and
            pokemon1["types"] == pokemon2["types"] and
            pokemon1["base_attack"] == pokemon2["base_attack"] and
            pokemon1["base_defense"] == pokemon2["base_defense"] and
            pokemon1["base_hp"] == pokemon2["base_hp"] and
            pokemon1["fast_move_pool"] == pokemon2["fast_move_pool"] and
            pokemon1["charged_move_pool"] == pokemon2["charged_move_pool"]
            )

def fetch_game_data():
    raw_data = requests.get(
        "https://raw.githubusercontent.com/PokeMiners/game_masters/master/latest/latest.json").json()

    data_dict = {"main": raw_data}

    with open("raw_game_data.json", "w") as f:
        json.dump(data_dict, f, indent=4)

    with open("raw_game_data.json", "r") as f:
        data = json.load(f)

    return data


def parse_pokemon_data(template_id, data):
    pokemon_data: dict = data.get("pokemonSettings", {})

    name = template_id.split("POKEMON_")[1]
    species = pokemon_data.get("pokemonId")
    types = [pokemon_data.get("type"), pokemon_data.get("type2")]
    base_attack = pokemon_data.get("stats", {}).get("baseAttack")
    base_defense = pokemon_data.get("stats", {}).get("baseDefense")
    base_hp = pokemon_data.get("stats", {}).get("baseStamina")
    pokedex_number = int(template_id.split("V")[1].split("_POKEMON")[0])

    fast_move_pool = []

    for move in pokemon_data.get("quickMoves", {}):
        fast_move_pool.append(move)
    for move in pokemon_data.get("eliteQuickMove", {}):
        fast_move_pool.append(move)

    charged_move_pool = []

    for move in pokemon_data.get("cinematicMoves", {}):
        charged_move_pool.append(move)
    for move in pokemon_data.get("eliteCinematicMove", {}):
        charged_move_pool.append(move)
    for move in pokemon_data.get("nonTmCinematicMoves", {}):
        charged_move_pool.append(move)

    return {
        "name": name,
        "species": species,
        "types": types,
        "base_attack": base_attack,
        "base_defense": base_defense,
        "base_hp": base_hp,
        "fast_move_pool": fast_move_pool,
        "charged_move_pool": charged_move_pool,
        "pokedex_number": pokedex_number,
        "pokemon_category": [pokemon_data.get("pokemonClass", "POKEMON_CLASS_REGULAR")]
    }

def check_for_existing_pokemon(pokemon_data):
    for pokemon in pokemon_json:

        if pokemon_data.get("name") in WHITELISTED_POKEMON:
            break

        pokemon_compared = pokemon_json[pokemon]

        if is_same(pokemon_compared, {
            "name": pokemon_data.get("name"),
            "species": pokemon_data.get("species"),
            "types": pokemon_data.get("types"),
            "base_attack": pokemon_data.get("base_attack"),
            "base_defense": pokemon_data.get("base_defense"),
            "base_hp": pokemon_data.get("base_hp"),
            "fast_move_pool": pokemon_data.get("fast_move_pool"),
            "charged_move_pool": pokemon_data.get("charged_move_pool"),
            "pokedex_number": pokemon_data.get("pokedex_number")
        }):
            return True
    else:
        return False

def apply_manual_changes(pokemon_data):
    name = pokemon_data["name"]
    fast_move_pool = pokemon_data["fast_move_pool"]
    charged_move_pool = pokemon_data["charged_move_pool"]

    if name in MANUAL_NAME_CHANGES:
        pokemon_data["name"] = MANUAL_NAME_CHANGES[name]

    if name in MANUAL_MOVE_ADDITIONS:
        move_data = MANUAL_MOVE_ADDITIONS[name]

        if move_data.get("type") == "fast":
            fast_move_pool.append(move_data.get("name"))
        elif move_data.get("type") == "charged":
            charged_move_pool.append(move_data.get("name"))

        pokemon_data["fast_move_pool"] = fast_move_pool
        pokemon_data["charged_move_pool"] = charged_move_pool

    if name in MANUAL_CATEGORY_CHANGES:
        pokemon_data["pokemon_category"].append(MANUAL_CATEGORY_CHANGES[name])

    return pokemon_data


def has_temp_evo_overrides(raw_data):
    return raw_data.get("pokemonSettings", {}).get("tempEvoOverrides") is not None

def process_temp_evo_overrides(pokemon_data, raw_data):

    for evolution in raw_data.get("pokemonSettings", {}).get("tempEvoOverrides"):

        name = pokemon_data.get("name")

        if evolution.get("tempEvoId") == "TEMP_EVOLUTION_MEGA":
            new_name = "MEGA_" + name
        elif evolution.get("tempEvoId") == "TEMP_EVOLUTION_MEGA_X":
            new_name = "MEGA_" + name + "_X"
        elif evolution.get("tempEvoId") == "TEMP_EVOLUTION_MEGA_Y":
            new_name = "MEGA_" + name + "_Y"
        elif evolution.get("tempEvoId") == "TEMP_EVOLUTION_PRIMAL":
            new_name = "PRIMAL_" + name
        else:
            new_name = name

        new_types = [
            evolution.get("typeOverride1", None),
            evolution.get("typeOverride2", None)
        ]

        if not evolution.get("stats"):
            continue

        new_base_attack, new_base_defense, new_base_hp = evolution.get("stats").get(
            "baseAttack"), evolution.get("stats").get("baseDefense"), evolution.get("stats").get(
            "baseStamina")

        new_category = "POKEMON_CLASS_MEGA" if "MEGA" in new_name else "POKEMON_CLASS_PRIMAL"

        yield {
            "name": new_name,
            "species": pokemon_data.get("species"),
            "types": new_types,
            "base_attack": new_base_attack,
            "base_defense": new_base_defense,
            "base_hp": new_base_hp,
            "fast_move_pool": pokemon_data.get("fast_move_pool"),
            "charged_move_pool": pokemon_data.get("charged_move_pool"),
            "pokedex_number": pokemon_data.get("pokedex_number"),
            "pokemon_category": [new_category],
        }

def process_pokemon_data(data):
    template_id = data.get("templateId")

    if any(word in template_id for word in BLACKLISTED_WORDS):
        return []

    pokemon_data = parse_pokemon_data(template_id, data)
    if not pokemon_data:
        return []

    if check_for_existing_pokemon(pokemon_data):
        return []

    pokemon_data = apply_manual_changes(pokemon_data)

    final_pokemon_data = [{
        "name": pokemon_data.get("name"),
        "species": pokemon_data.get("species"),
        "types": pokemon_data.get("types"),
        "base_attack": pokemon_data.get("base_attack"),
        "base_defense": pokemon_data.get("base_defense"),
        "base_hp": pokemon_data.get("base_hp"),
        "fast_move_pool": pokemon_data.get("fast_move_pool"),
        "charged_move_pool": pokemon_data.get("charged_move_pool"),
        "pokedex_number": pokemon_data.get("pokedex_number"),
        "pokemon_category": pokemon_data.get("pokemon_category"),
    }]

    if has_temp_evo_overrides(data):
        temp_evo_override_data = process_temp_evo_overrides(pokemon_data, data)

        for data in temp_evo_override_data:
            final_pokemon_data.append(data)

    return final_pokemon_data


def process_pokemon_move(entry):
    move_data: dict = entry["combatMove"]

    move_data.pop("vfxName", None)

    move_name = move_data["uniqueId"]

    if move_name in MANUAL_MOVE_CHANGES:
        move_name = move_data["uniqueId"] = MANUAL_MOVE_CHANGES[move_name]

    move_data["energyDelta"] = abs(move_data.get("energyDelta", 0))
    move_data["power"] = move_data.get("power", 0)

    move_data["turns"] = move_data.get("durationTurns", 0)
    move_data.pop("durationTurns", None)

    if move_name.endswith("_FAST"):
        move_data["usageType"] = "fast"
        move_data["turns"] += 1
    else:
        move_data["usageType"] = "charge"

    return move_data


def update():
    data = fetch_game_data()

    for entry in data["main"]:

        template_id = entry["templateId"]
        data = entry["data"]

        if (template_id.startswith("V0") or template_id.startswith(
                "V1")) and "POKEMON" in template_id:

            pokemon_data = process_pokemon_data(data)

            if not pokemon_data:
                continue

            for pokemon in pokemon_data:
                pokemon_json[pokemon["name"]] = pokemon

        elif template_id.startswith("COMBAT_V"):
            move_data = process_pokemon_move(data)
            moves_json[move_data["uniqueId"]] = move_data

    with open("moves.json", "w") as f:
        json.dump(moves_json, f, indent=4)

    with open("pokemon.json", "w") as f:
        json.dump(pokemon_json, f, indent=4)


if __name__ == "__main__":
    update()