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
    "ZYGARDE": "ZYGARDE_50",
    "ZYGARDE_COMPLETE": "ZYGARDE_100",
    "ZYGARDE_COMPLETE_TEN_PERCENT": "ZYGARDE_10",
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
    "V0462_MOVE_FORCE_PALM_FAST": "FORCE_PALM_FAST",
    406: "AURA_WHEEL_ELECTRIC",
    407: "AURA_WHEEL_DARK",
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

SKIPPED_POKEMON_IDS = [
    "WORMADAM",
    "ZACIAN",
    "ZAMAZENTA",
]


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
    form_number = 0

    for pokemon_key in pokemon_json:
        if pokemon_json.get(pokemon_key).get("pokedex_number") == pokedex_number:
            form_number += 1

    if name in SKIPPED_POKEMON_IDS:
        return None

    fast_move_pool = []

    for move in pokemon_data.get("quickMoves", {}):
        fast_move_pool.append(str(move))
    for move in pokemon_data.get("eliteQuickMove", {}):
        fast_move_pool.append(str(move))

    fast_move_pool = sorted(list(set(fast_move_pool)))

    string_manual_move_changes = {}
    for key in MANUAL_MOVE_CHANGES:
        string_manual_move_changes[str(key)] = MANUAL_MOVE_CHANGES[key]

    for index, move in enumerate(fast_move_pool):
        if move in string_manual_move_changes:
            fast_move_pool[index] = string_manual_move_changes[move]

    charged_move_pool = []

    for move in pokemon_data.get("cinematicMoves", {}):
        charged_move_pool.append(str(move))
    for move in pokemon_data.get("eliteCinematicMove", {}):
        charged_move_pool.append(str(move))
    for move in pokemon_data.get("nonTmCinematicMoves", {}):
        charged_move_pool.append(str(move))

    name = process_pokemon_name(name, species)

    charged_move_pool = sorted(list(set(charged_move_pool)))

    for index, move in enumerate(charged_move_pool):
        if move in string_manual_move_changes:
            charged_move_pool[index] = string_manual_move_changes[move]

    pokemon_category = get_pokemon_category(pokemon_data)

    display_name = get_pokemon_display_name(name)

    showdown_id = get_pokemon_showdown_id(name)

    return {
        "name": name,
        "species": species,
        "display_name": display_name,
        "showdown_id": showdown_id,
        "types": types,
        "base_attack": base_attack,
        "base_defense": base_defense,
        "base_hp": base_hp,
        "fast_move_pool": fast_move_pool,
        "charged_move_pool": charged_move_pool,
        "pokedex_number": pokedex_number,
        "form_number": form_number,
        "pokemon_category": pokemon_category
    }


def get_pokemon_display_name(name):
    final_string = ""
    for phrase in name.replace("-", "-_").split("_"):
        final_string += phrase.capitalize() + " "
    final_string = final_string.strip().replace("- ", "-")

    final_string = (final_string
        .replace(" Alola", " (Alolan)")
        .replace(" Galarian", " (Galarian)")
        .replace(" Hisuian", " (Hisuian)")
        .replace(" Paldea", " (Paldean)")
        .replace("Nidoran Female", "Nidoran♀")
        .replace("Nidoran Male", "Nidoran♂")
        .replace("Pikachu Doctor", "Pikachu (Doctor)")
        .replace("Pikachu Flying 01", "Pikachu (Flying)")
        .replace("Pikachu Flying Okinawa", "Pikachu (Flying Okinawa)")
        .replace("Pikachu Gofest 2024 Mtiara", "Pikachu (GOFest 2024)")
        .replace("Pikachu Horizons", "Pikachu (Horizons)")
        .replace("Pikachu Pop Star", "Pikachu (Pop Star)")
        .replace("Pikachu Rock Star", "Pikachu (Rock Star)")
        .replace("Mr Mime", "Mr. Mime")
        .replace("Mr. Mime Galarian", "Mr. Mime (Galarian)")
        .replace("Mewtwo A", "Mewtwo (Armored)")
        .replace("Ho Oh", "Ho-Oh")
        .replace("Castform Rainy", "Castform (Rainy)")
        .replace("Castform Snowy", "Castform (Snowy)")
        .replace("Castform Sunny", "Castform (Sunny)")
        .replace("Deoxys", "Deoxys (Normal)")
        .replace("Deoxys (Normal) Attack", "Deoxys (Attack)")
        .replace("Deoxys (Normal) Defense", "Deoxys (Defense)")
        .replace("Deoxys (Normal) Speed", "Deoxys (Speed)")
        .replace("Wormadam Plant", "Wormadam (Plant)")
        .replace("Wormadam Sandy", "Wormadam (Sandy)")
        .replace("Wormadam Trash", "Wormadam (Trash)")
        .replace("Cherrim Sunny", "Cherrim (Sunshine)")
        .replace("Mime Jr", "Mime Jr.")
        .replace("Porygon Z", "Porygon-Z")
        .replace("Rotom Fan", "Rotom (Fan)")
        .replace("Rotom Frost", "Rotom (Frost)")
        .replace("Rotom Heat", "Rotom (Heat)")
        .replace("Rotom Mow", "Rotom (Mow)")
        .replace("Rotom Wash", "Rotom (Wash)")
        .replace("Dialga", "Dialga (Altered)")
        .replace("Dialga (Altered) Origin", "Dialga (Origin)")
        .replace("Palkia", "Palkia (Altered)")
        .replace("Palkia (Altered) Origin", "Palkia (Origin)")
        .replace("Giratina", "Giratina (Altered)")
        .replace("Giratina (Altered) Origin", "Giratina (Origin)")
        .replace("Shaymin", "Shaymin (Land)")
        .replace("Shaymin (Land) Sky", "Shaymin (Sky)")
        .replace("Arceus Bug", "Arceus (Bug)")
        .replace("Arceus Dark", "Arceus (Dark)")
        .replace("Arceus Dragon", "Arceus (Dragon)")
        .replace("Arceus Electric", "Arceus (Electric)")
        .replace("Arceus Fairy", "Arceus (Fairy)")
        .replace("Arceus Fighting", "Arceus (Fighting)")
        .replace("Arceus Fire", "Arceus (Fire)")
        .replace("Arceus Flying", "Arceus (Flying)")
        .replace("Arceus Ghost", "Arceus (Ghost)")
        .replace("Arceus Grass", "Arceus (Grass)")
        .replace("Arceus Ground", "Arceus (Ground)")
        .replace("Arceus Ice", "Arceus (Ice)")
        .replace("Arceus Poison", "Arceus (Poison)")
        .replace("Arceus Psychic", "Arceus (Psychic)")
        .replace("Arceus Rock", "Arceus (Rock)")
        .replace("Arceus Steel", "Arceus (Steel)")
        .replace("Arceus Water", "Arceus (Water)")
        .replace("Darmanitan Zen", "Darmanitan (Zen)")
        .replace("Darmanitan (Galarian) Standard", "Darmanitan (Galarian)")
        .replace("Darmanitan (Galarian) Zen", "Darmanitan (Galarian) (Zen)")
        .replace("Tornadus", "Tornadus (Incarnate)")
        .replace("Tornadus (Incarnate) Therian", "Tornadus (Therian)")
        .replace("Thundurus", "Thundurus (Incarnate)")
        .replace("Thundurus (Incarnate) Therian", "Thundurus (Therian)")
        .replace("Landorus", "Landorus (Incarnate)")
        .replace("Landorus (Incarnate) Therian", "Landorus (Therian)")
        .replace("Keldeo", "Keldeo (Ordinary)")
        .replace("Keldeo Resolute", "Keldeo (Resolute)")
        .replace("Kyurem Black", "Kyurem (Black)")
        .replace("Kyurem White", "Kyurem (White)")
        .replace("Meloetta Aria", "Meloetta (Aria)")
        .replace("Meloetta Pirouette", "Meloetta (Pirouette)")
        .replace("Genesect Burn", "Genesect (Burn)")
        .replace("Genesect Chill", "Genesect (Chill)")
        .replace("Genesect Douse", "Genesect (Douse)")
        .replace("Genesect Shock", "Genesect (Shock)")
        .replace("Meowstic Female", "Meowstic (Female)")
        .replace("Pumpkaboo Average", "Pumpkaboo (Average)")
        .replace("Pumpkaboo Large", "Pumpkaboo (Large)")
        .replace("Pumpkaboo Super", "Pumpkaboo (Super)")
        .replace("Gourgeist Average", "Gourgeist (Average)")
        .replace("Gourgeist Large", "Gourgeist (Large)")
        .replace("Gourgeist Super", "Gourgeist (Super)")
        .replace("Zygarde", "Zygarde (50%)")
        .replace("Zygarde (50%) Complete", "Zygarde (Complete)")
        .replace("Zygarde (Complete) Ten Percent", "Zygarde (10%)")
        .replace("Hoopa Unbound", "Hoopa (Unbound)")
        .replace("Oricorio", "Oricorio (Baile)")
        .replace("Oricorio (Baile) Pompom", "Oricorio (Pom-Pom)")
        .replace("Oricorio (Baile) Pau", "Oricorio (Pa'u)")
        .replace("Oricorio (Baile) Sensu", "Oricorio (Sensu)")
        .replace("Lycanroc", "Lycanroc (Midday)")
        .replace("Lycanroc (Midday) Dusk", "Lycanroc (Dusk)")
        .replace("Lycanroc (Midday) Midnight", "Lycanroc (Midnight)")
        .replace("Wishiwashi", "Wishiwashi (Solo)")
        .replace("Wishiwashi (Solo) School", "Wishiwashi (School)")
        .replace("Type Null", "Type: Null")
        .replace("Silvally Bug", "Silvally (Bug)")
        .replace("Silvally Dark", "Silvally (Dark)")
        .replace("Silvally Dragon", "Silvally (Dragon)")
        .replace("Silvally Electric", "Silvally (Electric)")
        .replace("Silvally Fairy", "Silvally (Fairy)")
        .replace("Silvally Fighting", "Silvally (Fighting)")
        .replace("Silvally Fire", "Silvally (Fire)")
        .replace("Silvally Flying", "Silvally (Flying)")
        .replace("Silvally Ghost", "Silvally (Ghost)")
        .replace("Silvally Grass", "Silvally (Grass)")
        .replace("Silvally Ground", "Silvally (Ground)")
        .replace("Silvally Ice", "Silvally (Ice)")
        .replace("Silvally Poison", "Silvally (Poison)")
        .replace("Silvally Psychic", "Silvally (Psychic)")
        .replace("Silvally Rock", "Silvally (Rock)")
        .replace("Silvally Steel", "Silvally (Steel)")
        .replace("Silvally Water", "Silvally (Water)")
        .replace("Necrozma Dawn Wings", "Necrozma (Dawn Wings)")
        .replace("Necrozma Dusk Mane", "Necrozma (Dusk Mane)")
        .replace("Necrozma Ultra", "Necrozma (Ultra)")
        .replace("Mr Rime", "Mr. Rime")
        .replace("Eiscue", "Eiscue (Ice Face)")
        .replace("Eiscue (Ice Face) Noice", "Eiscue (No Ice Face)")
        .replace("Indeedee", "Indeedee (Male)")
        .replace("Indeedee (Male) Female", "Indeedee (Female)")
        .replace("Morpeko", "Morpeko (Full Belly)")
        .replace("Morpeko (Full Belly) Hangry", "Morpeko (Hangry)")
        .replace("Zacian Crowned Sword", "Zacian (Crowned Sword)")
        .replace("Zacian Hero", "Zacian (Hero of Many Battles)")
        .replace("Zamazenta Crowned Shield", "Zamazenta (Crowned Shield)")
        .replace("Zamazenta Hero", "Zamazenta (Hero of Many Battles)")
        .replace("Eternatus Eternamax", "Eternatus (Eternamax)")
        .replace("Urshifu Single Strike", "Urshifu (Single Strike)")
        .replace("Urshifu Rapid Strike", "Urshifu (Rapid Strike)")
        .replace("Calyrex Ice Rider", "Calyrex (Ice Rider)")
        .replace("Calyrex Shadow Rider", "Calyrex (Shadow Rider)")
        .replace("Enamorus", "Enamorus (Incarnate)")
        .replace("Enamorus Therian", "Enamorus (Therian)")
        .replace("Oinkologne", "Oinkologne (Male)")
        .replace("Oinkologne (Male) Female", "Oinkologne (Female)")
        .replace("Greattusk", "Great Tusk")
        .replace("Screamtail", "Scream Tail")
        .replace("Brutebonnet", "Brute Bonnet")
        .replace("Fluttermane", "Flutter Mane")
        .replace("Slitherwing", "Slither Wing")
        .replace("Sandyshocks", "Sandy Shocks")
        .replace("Irontreads", "Iron Treads")
        .replace("Ironbundle", "Iron Bundle")
        .replace("Ironhands", "Iron Hands")
        .replace("Ironjugulis", "Iron Jugulis")
        .replace("Ironmoth", "Iron Moth")
        .replace("Ironthorns", "Iron Thorns")
        .replace("Wochien", "Wo-Chein")
        .replace("Chienpao", "Chien-Pao")
        .replace("Tinglu", "Ting-Lu")
        .replace("Chiyu", "Chi-Yu")
        .replace("Roaringmoon", "Roaring Moon")
        .replace("Ironvaliant", "Iron Valiant")
    )

    return final_string


def get_pokemon_showdown_id(original_id):
    original_id = original_id.lower().replace("_", "-").replace("hisuian", "hisui").replace("galarian", "galar")

    switcher = {
        "mega-venusaur": "venusaur-mega",
        "mega-charizard-x": "charizard-mega-x",
        "mega-charizard-y": "charizard-mega-y",
        "mega-blastoise": "blastoise-mega",
        "mega-beedrill": "beedrill-mega",
        "mega-pidgeot": "pidgeot-mega",
        "pikachu-doctor": "pikachu",
        "pikachu-flying-01": "pikachu",
        "pikachu-flying-okinawa": "pikachu",
        "pikachu-gofest-2024-mtiara": "pikachu",
        "pikachu-horizons": "pikachu",
        "pikachu-pop-star": "pikachu",
        "pikachu-rock-star": "pikachu",
        "nidoran-female": "nidoranf",
        "nidoran-male": "nidoranm",
        "mega-alakazam": "alakazam-mega",
        "mega-slowbro": "slowbro-mega",
        "mega-gengar": "gengar-mega",
        "mega-kangaskhan": "kangaskhan-mega",
        "mr-mime": "mrmime",
        "mr-mime-galar": "mrmime-galar",
        "mega-pinsir": "pinsir-mega",
        "mega-gyarados": "gyarados-mega",
        "mega-aerodactyl": "aerodactyl-mega",
        "mewtwo-a": "mewtwo",
        "mega-ampharos": "ampharos-mega",
        "mega-steelix": "steelix-mega",
        "mega-scizor": "scizor-mega",
        "mega-heracross": "heracross-mega",
        "mega-houndoom": "houndoom-mega",
        "mega-tyranitar": "tyranitar-mega",
        "ho-oh": "hooh",
        "mega-sceptile": "sceptile-mega",
        "mega-blaziken": "blaziken-mega",
        "mega-swampert": "swampert-mega",
        "mega-gardevoir": "gardevoir-mega",
        "mega-sableye": "sableye-mega",
        "mega-aggron": "aggron-mega",
        "mega-medicham": "medicham-mega",
        "mega-manectric": "manectric-mega",
        "mega-altaria": "altaria-mega",
        "mega-banette": "banette-mega",
        "mega-absol": "absol-mega",
        "mega-glalie": "glalie-mega",
        "mega-salamence": "salamence-mega",
        "mega-latias": "latias-mega",
        "mega-latios": "latios-mega",
        "primal-kyogre": "kyogre-primal",
        "primal-groudon": "groudon-primal",
        "mega-rayquaza": "rayquaza-mega",
        "cherrim-sunny": "cherrim-sunshine",
        "mega-lopunny": "lopunny-mega",
        "mime-jr": "mimejr",
        "mega-garchomp": "garchomp-mega",
        "mega-lucario": "lucario-mega",
        "mega-abomasnow": "abomasnow-mega",
        "porygon-z": "porygonz",
        "darmanitan-galar-standard": "darmanitan-galar",
        "darmanitan-galar-zen": "darmanitan-galarzen",
        "meowstic-female": "meowstic-f",
        "pumpkaboo-average": "pumpkaboo",
        "gourgeist-average": "gourgeist",
        "zygarde-complete-ten-percent": "zygarde-10",
        "mega-diancie": "diancie-mega",
        "type-null": "typenull",
        "jangmo-o": "jangmoo",
        "hakamo-o": "hakamoo",
        "kommo-o": "kommoo",
        "tapu-koko": "tapukoko",
        "tapu-lele": "tapulele",
        "tapu-bulu": "tapubulu",
        "tapu-fini": "tapufini",
        "necrozma-dawn-wings": "necrozma-dawnwings",
        "necrozma-dusk-mane": "necrozma-duskmane",
        "mr-rime": "mrrime",
        "indeedee-male": "indeedee",
        "indeedee-female": "indeedee-f",
        "zacian-crowned-sword": "zacian-crowned",
        "zacian-hero": "zacian",
        "zamazenta-crowned-shield": "zamazenta-crowned",
        "zamazenta-hero": "zamazenta",
        "urshifu-single-strike": "urshifu",
        "urshifu-rapid-strike": "urshifu-rapidstrike",
        "calyrex-ice-rider": "calyrex-ice",
        "calyrex-shadow-rider": "calyrex-shadow",
        "oinkologne-male": "oinkologne",
        "oinkologne-female": "oinkologne-f",
        "great-tusk": "greattusk",
        "scream-tail": "screamtail",
        "brute-bonnet": "brutebonnet",
        "flutter-mane": "fluttermane",
        "slither-wing": "slitherwing",
        "sandy-shocks": "sandyshocks",
        "iron-treads": "irontreads",
        "iron-bundle": "ironbundle",
        "iron-hands": "ironhands",
        "iron-jugulis": "ironjugulis",
        "iron-moth": "ironmoth",
        "iron-thorns": "ironthorns",
        "wo-chein": "wochein",
        "chien-pao": "chienpao",
        "ting-lu": "tinglu",
        "chi-yu": "chiyu",
        "roaring-moon": "roaringmoon",
        "iron-valiant": "ironvaliant"
    }

    return switcher.get(original_id, original_id)


def get_pokemon_category(pokemon_data) -> list:
    if pokemon_data.get("tempEvoId"):
        if pokemon_data.get("tempEvoId") == "TEMP_EVOLUTION_MEGA" or pokemon_data.get(
                "tempEvoId") == "TEMP_EVOLUTION_MEGA_X" or pokemon_data.get("tempEvoId") == "TEMP_EVOLUTION_MEGA_Y":
            return ["POKEMON_CLASS_MEGA"]

        if pokemon_data.get("tempEvoId") == "TEMP_EVOLUTION_PRIMAL":
            return ["POKEMON_CLASS_PRIMAL"]

    categories = [pokemon_data.get("pokemonClass", "POKEMON_CLASS_REGULAR")]

    if pokemon_data.get("shadow"):
        categories.append("POKEMON_CLASS_SHADOW_ELIGIBLE")

    return sorted(list(set(categories)))


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

    for move in fast_move_pool + charged_move_pool:
        if move in MANUAL_MOVE_CHANGES:
            if move in fast_move_pool:
                fast_move_pool.remove(move)
                fast_move_pool.append(MANUAL_MOVE_CHANGES[move])
            elif move in charged_move_pool:
                charged_move_pool.remove(move)
                charged_move_pool.append(MANUAL_MOVE_CHANGES[move])

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

    for move in fast_move_pool + charged_move_pool:
        if move in MANUAL_MOVE_CHANGES:
            if move in fast_move_pool:
                fast_move_pool.remove(move)
                fast_move_pool.append(MANUAL_MOVE_CHANGES[move])
            elif move in charged_move_pool:
                charged_move_pool.remove(move)
                charged_move_pool.append(MANUAL_MOVE_CHANGES[move])

    if pokemon_data.get("name") in MANUAL_CATEGORY_CHANGES:
        pokemon_data["pokemon_category"].append(MANUAL_CATEGORY_CHANGES.get(pokemon_data.get("name")))

    return pokemon_data


def has_temp_evo_overrides(raw_data):
    return raw_data.get("pokemonSettings", {}).get("tempEvoOverrides") is not None


def process_temp_evo_overrides(pokemon_data, raw_data):
    for evolution in raw_data.get("pokemonSettings", {}).get("tempEvoOverrides"):
        name = pokemon_data.get("name")

        if evolution.get("tempEvoId") == "TEMP_EVOLUTION_MEGA":
            new_name = "MEGA_" + name
            form_number = 1
        elif evolution.get("tempEvoId") == "TEMP_EVOLUTION_MEGA_X":
            new_name = "MEGA_" + name + "_X"
            form_number = 1
        elif evolution.get("tempEvoId") == "TEMP_EVOLUTION_MEGA_Y":
            new_name = "MEGA_" + name + "_Y"
            form_number = 2
        elif evolution.get("tempEvoId") == "TEMP_EVOLUTION_PRIMAL":
            new_name = "PRIMAL_" + name
            form_number = 1
        else:
            new_name = name
            form_number = 1

        new_types = [
            evolution.get("typeOverride1", None),
            evolution.get("typeOverride2", None)
        ]

        if not evolution.get("stats"):
            continue

        new_base_attack, new_base_defense, new_base_hp = evolution.get("stats").get(
            "baseAttack"), evolution.get("stats").get("baseDefense"), evolution.get("stats").get(
            "baseStamina")

        display_name = get_pokemon_display_name(new_name)

        showdown_id = get_pokemon_showdown_id(new_name)

        yield {
            "name": new_name,
            "species": pokemon_data.get("species"),
            "display_name": display_name,
            "showdown_id": showdown_id,
            "types": new_types,
            "base_attack": new_base_attack,
            "base_defense": new_base_defense,
            "base_hp": new_base_hp,
            "fast_move_pool": pokemon_data.get("fast_move_pool"),
            "charged_move_pool": pokemon_data.get("charged_move_pool"),
            "pokedex_number": pokemon_data.get("pokedex_number"),
            "form_number": form_number,
            "pokemon_category": get_pokemon_category(evolution)
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
        "display_name": pokemon_data.get("display_name"),
        "showdown_id": pokemon_data.get("showdown_id"),
        "base_attack": pokemon_data.get("base_attack"),
        "base_defense": pokemon_data.get("base_defense"),
        "base_hp": pokemon_data.get("base_hp"),
        "fast_move_pool": pokemon_data.get("fast_move_pool"),
        "charged_move_pool": pokemon_data.get("charged_move_pool"),
        "pokedex_number": pokemon_data.get("pokedex_number"),
        "form_number": pokemon_data.get("form_number"),
        "pokemon_category": pokemon_data.get("pokemon_category"),
    }]

    if has_temp_evo_overrides(data):
        temp_evo_override_data = process_temp_evo_overrides(pokemon_data, data)

        for data in temp_evo_override_data:
            final_pokemon_data.append(data)

    return final_pokemon_data


def process_pokemon_name(name, species):
    if name == "NIDORAN":
        return species
    return name


def process_pokemon_move(entry):
    move_data: dict = entry["combatMove"]

    move_data.pop("vfxName", None)

    move_name = move_data["uniqueId"]

    if move_name in MANUAL_MOVE_CHANGES:
        move_name = move_data["uniqueId"] = MANUAL_MOVE_CHANGES[move_name]

    move_data["energyDelta"] = abs(move_data.get("energyDelta", 0))
    move_data["power"] = move_data.get("power", 0)

    move_data["turns"] = move_data.get("durationTurns", 0)

    move_uuid = int(entry["templateId"].split("_")[1][1:])
    move_data["uuid"] = move_uuid

    move_display_name = move_data.get("uniqueId").replace("_", " ").replace("FAST", "").title()
    move_display_name = (move_display_name
                         .replace(" Blastoise", "")
                         .replace("Wrap Green", "Wrap")
                         .replace("Wrap Pink", "Wrap")
                         .replace("X Scissor", "X-Scissor")
                         .replace("Super Power", "Superpower")
                         .replace("V Create", "V-create")
                         .replace("Lock On", "Lock-On")
                         .replace("Aeroblast Plus", "Aeroblast+")
                         .replace("Aeroblast Plus Plus", "Aeroblast++")
                         .replace("Scared Fire Plus", "Sacred Fire+")
                         .replace("Scared Fire Plus Plus", "Sacred Fire++")
                         .replace("Mud Slap", "Mud-Slap")
                         .replace("Futuresight", "Future Sight")
                         .replace("Natures Madness", "Nature's Madness")
                         .replace("Weather Ball Normal", "Weather Ball [Normal]")
                         .replace("Weather Ball Fire", "Weather Ball [Fire]")
                         .replace("Weather Ball Water", "Weather Ball [Water]")
                         .replace("Weather Ball Ice", "Weather Ball [Ice]")
                         .replace("Weather Ball Rock", "Weather Ball [Rock]")
                         .replace("Techno Blast Normal", "Techno Blast")
                         .replace("Techno Blast Burn", "Techno Blast")
                         .replace("Techno Blast Chill", "Techno Blast")
                         .replace("Techno Blast Douse", "Techno Blast")
                         .replace("Techno Blast Shock", "Techno Blast")
                         .replace("Roar Of Time", "Roar of Time")
                         ).strip()

    move_data["displayName"] = move_display_name

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
        query = entry["data"]

        if template_id.startswith("COMBAT_V"):
            move_data = process_pokemon_move(query)
            moves_json[move_data["uniqueId"]] = move_data

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

    # handle hidden power
    # remove "HIDDEN_POWER_FAST"
    hidden_power = moves_json.pop("HIDDEN_POWER_FAST")
    uuid = 600
    hidden_power_types = ["BUG", "DARK", "DRAGON", "ELECTRIC", "FIGHTING", "FIRE", "FLYING", "GHOST", "GRASS",
                          "GROUND", "ICE", "POISON", "PSYCHIC", "ROCK", "STEEL", "WATER"]
    for pokemon_type in hidden_power_types:
        new_move = hidden_power.copy()
        new_move["uniqueId"] = f"HIDDEN_POWER_{pokemon_type}"
        new_move["type"] = "POKEMON_TYPE_" + pokemon_type
        new_move["displayName"] = f"Hidden Power [{pokemon_type.title()}]"
        new_move["uuid"] = uuid
        uuid += 1
        moves_json[f"HIDDEN_POWER_{pokemon_type}"] = new_move

    # give all pokemon that have hidden power these moves
    for pokemon in pokemon_json:
        if "HIDDEN_POWER_FAST" in pokemon_json[pokemon]["fast_move_pool"]:
            pokemon_json[pokemon]["fast_move_pool"].remove("HIDDEN_POWER_FAST")
            for pokemon_type in hidden_power_types:
                pokemon_json[pokemon]["fast_move_pool"].append(f"HIDDEN_POWER_{pokemon_type}")

    with open("moves.json", "w") as f:
        json.dump(moves_json, f, indent=4)

    with open("pokemon.json", "w") as f:
        json.dump(pokemon_json, f, indent=4)


def print_pokemon():
    with open("pokemon.json", "r") as f:
        data = json.load(f)

    for pokemon in data:
        if "_" in pokemon and "MEGA" not in pokemon and "ALOLA" not in pokemon and "GALARIAN" not in pokemon:
            print(f"{pokemon} ({data[pokemon]['display_name']})")

if __name__ == "__main__":
    update()
    # print_pokemon()
