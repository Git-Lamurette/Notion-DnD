from py_dm_tk.utilities.creature_parser import _Creature


def parsing_monster_data(data):

    def table_data_name():
        creature_list.append(f"{x.name}")

    def table_data_challenge_rating():
        creature_list.append(x.challenge_rating)

    def table_data_creature_type():
        creature_list.append(f"{x.type.capitalize()}")

    def table_data_creature_hp():
        creature_list.append(x.hit_points)

    def table_data_languages():
        languages = x.languages
        lang = languages.split(", ")
        merg_lang = "\n".join(list(lang))
        creature_list.append(f"{merg_lang}")

    def table_data_movement():
        parsed_speed = [
            f"{Movement.capitalize()}: {Distance}"
            for Movement, Distance in x.speed.items()
        ]

        merged_speed = "\n".join(list(parsed_speed))
        creature_list.append(f"{merged_speed}")

    def table_data_resistances():
        parsed_dam_res = list(x.damage_resistances)
        if parsed_dam_res:
            parsed_dam_res = "\n".join([x.capitalize() for x in parsed_dam_res])
            creature_list.append(f"{parsed_dam_res}")
        else:
            parsed_dam_res = ""
            creature_list.append(f"{parsed_dam_res}")

    def table_data_immunities():
        parsed_dam_imun = list(x.damage_immunities)
        if parsed_dam_imun:
            parsed_dam_imun = "\n".join([x.capitalize() for x in parsed_dam_imun])
            creature_list.append(f"{parsed_dam_imun}")
        else:
            parsed_dam_imun = ""
            creature_list.append(f"{parsed_dam_imun}")

    def table_data_spells():
        parsed_spell = ""
        if x.special_abilities:
            for spell in x.special_abilities:
                if spell["name"].startswith("Spellcasting"):

                    parsed_spell = "\n".join(
                        [spell["name"] for spell in spell["spellcasting"]["spells"]]
                    )

        creature_list.append(f"{parsed_spell}")

    def table_data_saving_throws():
        saving_lines = []
        for val in x.proficiencies:
            name = val["proficiency"]["name"]
            if name.startswith("Saving Throw"):
                name = name.removeprefix("Saving Throw: ")
                saving_lines.append(f"{name}: {val['value']}")

        final_saving_line = "\n".join(saving_lines)
        creature_list.append(final_saving_line if saving_lines else "")

    def table_data_skills():
        skill_lines = []
        for val in x.proficiencies:
            name = val["proficiency"]["name"]
            if name.startswith("Skill"):
                skill_lines.append(f"{name[7:]}: {val['value']}")

        final_skill_line = "\n".join(skill_lines)
        creature_list.append(final_skill_line if skill_lines else "")

    table_data_dict_functions = {
        "Creature Name": {"column": "0", "function": table_data_name},
        "CR": {"column": "1", "function": table_data_challenge_rating},
        "Type": {"column": "2", "function": table_data_creature_type},
        "Hit Points": {"column": "3", "function": table_data_creature_hp},
        "Movement": {"column": "4", "function": table_data_movement},
        "Languages": {"column": "5", "function": table_data_languages},
        "Spells": {"column": "6", "function": table_data_spells},
        "Saving Throws": {"column": "7", "function": table_data_saving_throws},
        "Skills": {"column": "8", "function": table_data_skills},
        "Resistances": {"column": "9", "function": table_data_resistances},
        "Immunities": {"column": "10", "function": table_data_immunities},
    }

    header_data = list(table_data_dict_functions.keys())

    # Iterate over the creatures model and build the table data
    processed_data = []
    for x in data:
        x = _Creature(**x)
        creature_list = []
        # Iterate over the keys in the dictionary
        for key in table_data_dict_functions:
            # Get the dictionary associated with the key
            table_data_dict_functions[key]["function"]()

        processed_data.append(creature_list)

    packaged_data = {"header": header_data, "creature_data": processed_data}

    return packaged_data
