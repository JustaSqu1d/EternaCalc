import json

import requests

raw_data = requests.get(
    "https://raw.githubusercontent.com/PokeMiners/game_masters/master/latest/latest.json").json()

data_dict = {"main": raw_data}

with open("raw_game_data.json", "w") as f:
    json.dump(data_dict, f, indent=4)

with open("raw_game_data.json", "r") as f:
    data = json.load(f)

moves_json = {}
pokemon_json = {}

BLACKLISTED_POKEMON_FORMS = ["UNOWN", "SPINDA", "CASTFORM", "BURMY", "WORMADAM", "CHERRIM", "SHELLOS", "GASTRODON",
                             "BASCULIN", "DEERLING", "SAWSBUCK", "FURFROU", "PUMPKABOO", "GOURGEIST"]

BLACKLISTED_WORDS = ["FAMILY", "MOVE", "SMEARGLE", "HOME_FORM_REVERSION", "HOME_REVERSION", "FALL_2019", "COPY_2019",
                     "_NORMAL", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "COSTUME"]

WHITELISTED_POKEMON = ["KYUREM", "KYUREM_WHITE", "KYUREM_BLACK"]

MANUAL_NAME_CHANGES = {
    "MINIOR_BLUE": "MINIOR",
    "URSHIFU": "URSHIFU_SINGLE_STRIKE",
    "GREATTUSK": "GREAT_TUSK",
    "SCREAMTAIL": "SCREAM_TAIL",
    "BRUTEBONNET": "BRUTE_BONNET",
    "FLUTTERMANE": "FLUTTER_MANE",
    "SLITHERWING": "SLITHER_WING",
    "SANDYSHOCKS": "SANDY_SHOCKS",
    "IRONTREADS": "IRON_TREADS",
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


def is_same(pokemon1, pokemon2):
    return (pokemon1["species"] == pokemon2["species"] and
            pokemon1["types"] == pokemon2["types"] and
            pokemon1["base_attack"] == pokemon2["base_attack"] and
            pokemon1["base_defense"] == pokemon2["base_defense"] and
            pokemon1["base_hp"] == pokemon2["base_hp"] and
            pokemon1["fast_move_pool"] == pokemon2["fast_move_pool"] and
            pokemon1["charged_move_pool"] == pokemon2["charged_move_pool"]
            )


if __name__ == "__main__":
    for entry in data["main"]:

        template_id = entry["templateId"]
        data = entry["data"]

        if (template_id.startswith("V0") or template_id.startswith(
                "V1")) and "POKEMON" in template_id:

            if any(word in template_id for word in BLACKLISTED_WORDS):
                continue

            pokemon_data: dict = data["pokemonSettings"]

            name = template_id.split("POKEMON_")[1]
            species = data.get("pokemonSettings", {}).get("pokemonId")
            types = [data.get("pokemonSettings", {}).get("type"), data.get("pokemonSettings", {}).get("type2")]
            base_attack = data.get("pokemonSettings", {}).get("stats", {}).get("baseAttack")
            base_defense = data.get("pokemonSettings", {}).get("stats", {}).get("baseDefense")
            base_hp = data.get("pokemonSettings", {}).get("stats", {}).get("baseStamina")
            fast_move_pool = data.get("pokemonSettings", {}).get("quickMoves")
            charged_move_pool = data.get("pokemonSettings", {}).get("cinematicMoves")

            skip = False
            # check if a similar pokemon already exists
            for pokemon in pokemon_json:

                if name in WHITELISTED_POKEMON:
                    break

                pokemon_compared = pokemon_json[pokemon]

                if is_same(pokemon_compared, {
                    "name": name,
                    "species": species,
                    "types": types,
                    "base_attack": base_attack,
                    "base_defense": base_defense,
                    "base_hp": base_hp,
                    "fast_move_pool": fast_move_pool,
                    "charged_move_pool": charged_move_pool
                }):
                    skip = True
                    break

            if skip:
                continue

            if name in MANUAL_NAME_CHANGES:
                name = MANUAL_NAME_CHANGES[name]

            pokemon_json[name] = {
                "name": name,
                "species": species,
                "types": types,
                "base_attack": base_attack,
                "base_defense": base_defense,
                "base_hp": base_hp,
                "fast_move_pool": fast_move_pool,
                "charged_move_pool": charged_move_pool
            }

        elif template_id.startswith("COMBAT_V"):

            move_data: dict = data["combatMove"]

            move_data.pop("vfxName", None)
            move_data.pop("durationTurns", None)

            move_name = move_data["uniqueId"]

            move_data["energyDelta"] = abs(move_data.get("energyDelta", 0))
            move_data["power"] = move_data.get("power", 0)

            turns = move_data.get("durationTurns", 0)
            move_data["turns"] = turns
            if move_name.endswith("_FAST"):
                move_data["usageType"] = "fast"
                move_data["turns"] += 1
            else:
                move_data["usageType"] = "charge"

            moves_json[move_data["uniqueId"]] = move_data

        elif template_id.startswith("FORMS_V"):
            form_setting = data["formSettings"]
            if len(form_setting) <= 1:
                continue

            form_counter = 1

            name = data["formSettings"]["pokemon"]

            if name in BLACKLISTED_POKEMON_FORMS:
                continue

    with open("moves.json", "w") as f:
        json.dump(moves_json, f, indent=4)

    with open("pokemon.json", "w") as f:
        json.dump(pokemon_json, f, indent=4)
