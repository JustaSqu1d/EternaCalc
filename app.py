import json

import streamlit as st

from pokemon import Species, parse_pokemon_string, Pokemon
from pokemon.calculator import display_calculated_damage
from pokemon.moves import Move, parse_move_string
from pokemon.type import parse_type_string, Type, get_path_to_file


def load_data():
    with open("pokemon/game_data/pokemon.json", "r") as f:
        pokemon_json = json.load(f)

    with open("pokemon/game_data/moves.json", "r") as f:
        moves_json = json.load(f)

    moves_dict = {}
    moves_list = []

    for move_json_key in moves_json:
        unique_id = moves_json[move_json_key]["uniqueId"]
        name = parse_move_string(unique_id)

        raw_type_string = moves_json[move_json_key]["type"]
        move_type = parse_type_string(raw_type_string)

        power = moves_json[move_json_key]["power"]
        energy = moves_json[move_json_key]["energyDelta"]
        turns = moves_json[move_json_key]["turns"]
        usage_type = moves_json[move_json_key]["usageType"]

        move = Move(
            name=name,
            unique_id=unique_id,
            type=move_type,
            power=power,
            energy=energy,
            turns=turns,
            usage_type=usage_type
        )

        moves_dict.update({unique_id: move})
        moves_list.append(move)

    species_dict = {}
    species_list = []
    forms_dict = {}

    for pokemon_json_key in pokemon_json:
        name = parse_pokemon_string(pokemon_json[pokemon_json_key]["name"])
        species_name = pokemon_json[pokemon_json_key]["species"]

        types = []
        for raw_type_string in pokemon_json[pokemon_json_key]["types"]:
            if raw_type_string:
                types.append(parse_type_string(raw_type_string))

        base_attack = pokemon_json[pokemon_json_key]["base_attack"]
        base_defense = pokemon_json[pokemon_json_key]["base_defense"]
        base_hp = pokemon_json[pokemon_json_key]["base_hp"]

        fast_move_pool = []
        for raw_move_string in pokemon_json[pokemon_json_key]["fast_move_pool"]:
            move = moves_dict[raw_move_string]
            fast_move_pool.append(move)

        charged_move_pool = []
        for raw_move_string in pokemon_json[pokemon_json_key]["charged_move_pool"]:
            move = moves_dict[raw_move_string]
            charged_move_pool.append(move)

        species = Species(
            name=name,
            species=species_name,
            types=types,
            base_attack=base_attack,
            base_defense=base_defense,
            base_hp=base_hp,
            fast_move_pool=fast_move_pool,
            charged_move_pool=charged_move_pool
        )

        species_dict.update({name: species})

        species_list.append(species)

        if species_name in forms_dict:
            forms_dict[species_name].append(name)
        else:
            forms_dict[species_name] = [name]

    return moves_dict, moves_list, species_dict, species_list, forms_dict


if __name__ == "__main__":

    pokemon_moves_dict, pokemon_moves_list, pokemon_species_dict, pokemon_species_list, pokemon_forms_dict = load_data()

    TITLE = "EternaCalc"
    DESCRIPTION = "A simple damage calculator for Pokémon GO PvP."

    st.set_page_config(page_title=TITLE, page_icon=":zap:", layout="wide")

    with st.container() as header:
        st.title(TITLE)
        st.write(DESCRIPTION)

    with (st.container() as body):
        if 'species' not in st.session_state:
            st.session_state.species = None

        left_column, right_column = st.columns(2)
        with left_column:
            st.write("#### Pokémon 1")

            input_column, spacing_column = st.columns([4, 1])
            with input_column:

                species1 = st.selectbox("Pokémon 1",
                                        pokemon_species_list,
                                        index=None,
                                        placeholder="Select a Pokémon...")

                if species1:
                    move1 = st.selectbox(
                        "Move",
                        list(species1.charged_move_pool + species1.fast_move_pool + ["Custom existing move...",
                                                                                     "Custom new move...!"]),
                        index=None,
                        placeholder="Select a move..."
                    )

                    if move1 == "Custom existing move...":
                        move1 = st.selectbox("Custom existing move",
                                             pokemon_moves_list,
                                             index=None,
                                             placeholder="Select a move...")

                    if move1 == "Custom new move...!":
                        move1_name = st.text_input("Move name")
                        move1_type = Type(st.selectbox("Type",
                                                       list(Type),
                                                       index=None,
                                                       placeholder="Select a type...")
                                          )
                        move1_power = st.number_input("Power", min_value=0, max_value=200, value=0)
                        move1_energy = st.number_input("Energy", min_value=0, max_value=100, value=0)
                        move1 = Move(
                            name=move1_name,
                            type=move1_type,
                            power=move1_power,
                            energy=move1_energy,
                            turns=1,
                            usage_type="CHARGE"
                        )

                    st.write("##### Configurations")
                    level1 = st.number_input("Level", min_value=1.0, max_value=51.0, value=40.0, step=0.5,
                                             format="%.1f")
                    level1 = int(level1 * 2) / 2  # Round to nearest 0.5
                else:
                    st.write("Select a Pokémon to show details.")

            if species1:
                label_column, base_stats_column, ivs_column, stages_column = st.columns([1.25, 0.9, 2, 2])
                with label_column:
                    st.write("Stats")
                    st.write("**Attack**")
                    st.write(" ")
                    st.write("**Defense**")
                    st.write(" ")
                    st.write("**HP**")
                with base_stats_column:
                    st.write("Base")
                    st.write(f"**{species1.base_attack}**")
                    st.write(" ")
                    st.write(f"**{species1.base_defense}**")
                    st.write(" ")
                    st.write(f"**{species1.base_hp}**")
                with ivs_column:
                    atk_iv1 = st.number_input("IVs", min_value=0, max_value=15, value=15)
                    def_iv1 = st.number_input("Defense IV", min_value=0, max_value=15, value=15,
                                              label_visibility="collapsed")
                    hp_iv1 = st.number_input("HP IV", min_value=0, max_value=15, value=15,
                                             label_visibility="collapsed")
                with stages_column:
                    atk_stages1 = st.number_input("Stages", min_value=-4, max_value=4, value=0)
                    def_stages1 = st.number_input("Defense stages", min_value=-4, max_value=4, value=0,
                                                  label_visibility="collapsed")
                is_shadow1 = st.checkbox("Is it a Shadow Pokémon?", value=False)

                pokemon1 = Pokemon(
                    species=species1,
                    current_hp=species1.base_hp,
                    hp_iv=hp_iv1,
                    attack_iv=atk_iv1,
                    defense_iv=def_iv1,
                    level=level1,
                    shadow=is_shadow1,
                    attack_stages=atk_stages1,
                    defense_stages=def_stages1
                )

        with right_column:
            st.write("#### Pokémon 2")

            input_column2, spacing_column2 = st.columns([4, 1])
            with input_column2:

                species2 = st.selectbox("Pokémon 2",
                                        pokemon_species_list,
                                        index=None,
                                        placeholder="Select a Pokémon...")

                if species2:
                    move2 = st.selectbox(
                        "Move ",
                        list(species2.charged_move_pool + species2.fast_move_pool + ["Custom existing move...",
                                                                                     "Custom new move...!"]),
                        index=None,
                        placeholder="Select a move..."
                    )

                    if move2 == "Custom existing move...":
                        move2 = st.selectbox("Custom existing move ",
                                             pokemon_moves_list,
                                             index=None,
                                             placeholder="Select a move...")

                    if move2 == "Custom new move...!":
                        move2_name = st.text_input("Move name ")
                        move2_type = Type(st.selectbox("Type ",
                                                       list(Type),
                                                       index=None,
                                                       placeholder="Select a type...")
                                          )
                        move2_power = st.number_input("Power ", min_value=0, max_value=200, value=0)
                        move2_energy = st.number_input("Energy ", min_value=0, max_value=100, value=0)
                        move2 = Move(
                            name=move2_name,
                            type=move2_type,
                            power=move2_power,
                            energy=move2_energy,
                            turns=1,
                            usage_type="CHARGE"
                        )

                    st.write("##### Configurations")
                    level2 = st.number_input("Level ", min_value=1.0, max_value=51.0, value=40.0, step=0.5,
                                             format="%.1f")
                    level2 = int(level2 * 2) / 2  # Round to nearest 0.5
                else:
                    st.write("Select a Pokémon to show details.")

            if species2:
                label_column2, base_stats_column2, ivs_column2, stages_column2 = st.columns([1.25, 0.9, 2, 2])
                with label_column2:
                    st.write("Stats")
                    st.write("**Attack**")
                    st.write(" ")
                    st.write("**Defense**")
                    st.write(" ")
                    st.write("**HP**")
                with base_stats_column2:
                    st.write("Base")
                    st.write(f"**{species2.base_attack}**")
                    st.write(" ")
                    st.write(f"**{species2.base_defense}**")
                    st.write(" ")
                    st.write(f"**{species2.base_hp}**")
                with ivs_column2:
                    atk_iv2 = st.number_input("IVs ", min_value=0, max_value=15, value=15)
                    def_iv2 = st.number_input("Defense IV ", min_value=0, max_value=15, value=15,
                                              label_visibility="collapsed")
                    hp_iv2 = st.number_input("HP IV ", min_value=0, max_value=15, value=15,
                                             label_visibility="collapsed")
                with stages_column2:
                    atk_stages2 = st.number_input("Stages ", min_value=-4, max_value=4, value=0)
                    def_stages2 = st.number_input("Defense stages ", min_value=-4, max_value=4, value=0,
                                                  label_visibility="collapsed")
                is_shadow2 = st.checkbox("Is it a Shadow Pokémon? ", value=False)

                pokemon2 = Pokemon(
                    species=species2,
                    current_hp=species2.base_hp,
                    hp_iv=hp_iv2,
                    attack_iv=atk_iv2,
                    defense_iv=def_iv2,
                    level=level2,
                    shadow=is_shadow2,
                    attack_stages=atk_stages2,
                    defense_stages=def_stages2
                )

        st.write("---")

        st.write("#### Pokémon Summary")

        if not species1 or not species2:
            st.write("Select 2 Pokémon to see Pokémon summary")

        else:

            left_column_2, right_column_2 = st.columns(2)

            with left_column_2:

                text_column3, image_column3, caption_column3 = st.columns([3.25, 0.75, 6])

                with text_column3:

                    st.write("##### Pokémon 1")

                    if pokemon1.shadow:
                        st.write(pokemon1.species.name + " :violet[(Shadow)]")
                    else:
                        st.write(pokemon1.species.name)
                    st.write(f"CP: {pokemon1.get_cp()}")
                    st.write(f"Level: {pokemon1.level}")

                    attack1 = round(pokemon1.get_true_attack(), 1)

                    if pokemon1.attack_stages > 0:
                        st.write(f"Attack: :green[{attack1}]")
                    elif pokemon1.attack_stages < 0:
                        st.write(f"Attack: :red[{attack1}]")
                    else:
                        st.write(f"Attack: {attack1}")

                    defense1 = round(pokemon1.get_true_defense(), 1)

                    if pokemon1.defense_stages > 0:
                        st.write(f"Defense: :green[{defense1}]")
                    elif pokemon1.defense_stages < 0:
                        st.write(f"Defense: :red[{defense1}]")
                    else:
                        st.write(f"Defense: {defense1}")

                    st.write(f"HP: {pokemon1.get_true_hp()}")

                with image_column3:
                    st.image(get_path_to_file(pokemon1.species.types[0]), width=24)
                    if len(pokemon1.species.types) > 1:
                        st.image(get_path_to_file(pokemon1.species.types[1]), width=24)

                with caption_column3:
                    st.write(f"{pokemon1.species.types[0]}")
                    if len(pokemon1.species.types) > 1:
                        st.write(f"{pokemon1.species.types[1]}")

            with right_column_2:

                text_column4, image_column4, caption_column4 = st.columns([3.25, 0.75, 6])

                with text_column4:

                    st.write("##### Pokémon 2")

                    if pokemon2.shadow:
                        st.write(pokemon2.species.name + " :violet[(Shadow)]")
                    else:
                        st.write(pokemon2.species.name)
                    st.write(f"CP: {pokemon2.get_cp()}")
                    st.write(f"Level: {pokemon2.level}")

                    attack2 = round(pokemon2.get_true_attack(), 1)

                    if pokemon2.attack_stages > 0:
                        st.write(f"Attack: :green[{attack2}]")
                    elif pokemon2.attack_stages < 0:
                        st.write(f"Attack: :red[{attack2}]")
                    else:
                        st.write(f"Attack: {attack2}")

                    defense2 = round(pokemon2.get_true_defense(), 1)

                    if pokemon2.defense_stages > 0:
                        st.write(f"Defense: :green[{defense2}]")
                    elif pokemon2.defense_stages < 0:
                        st.write(f"Defense: :red[{defense2}]")
                    else:
                        st.write(f"Defense: {defense2}")

                    st.write(f"HP: {pokemon2.get_true_hp()}")

                with image_column4:
                    st.image(get_path_to_file(pokemon2.species.types[0]), width=24)
                    if len(pokemon2.species.types) > 1:
                        st.image(get_path_to_file(pokemon2.species.types[1]), width=24)

                with caption_column4:
                    st.write(f"{pokemon2.species.types[0]}")
                    if len(pokemon2.species.types) > 1:
                        st.write(f"{pokemon2.species.types[1]}")

        st.write("---")

        st.write("#### Damage")

        if not species1 or not species2:
            st.write("Select 2 Pokémon to show damage details.")
        elif move1 is None and move2 is None:
            st.write("Select a move to calculate the damage.")
        elif species1 is None or species2 is None:
            st.write("Select 2 Pokémon to show damage details.")
        else:

            if move1 and move2:
                left_damage_results, right_damage_results = st.columns(2)
                with left_damage_results:
                    display_calculated_damage(st, move1, pokemon1, pokemon2)
                with right_damage_results:
                    display_calculated_damage(st, move2, pokemon2, pokemon1)
            elif move1:
                display_calculated_damage(st, move1, pokemon1, pokemon2)
            elif move2:
                display_calculated_damage(st, move2, pokemon2, pokemon1)
