#Importing Libraries
import re
from dataclasses import dataclass
from typing import Optional, Union
from uuid import uuid4
from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QLabel, QFrame

@dataclass(kw_only=True)
class _Creature():
    index: str
    uid: str = uuid4().hex
    type: str
    subtype: Optional[str] = None
    desc: Optional[str] = None
    image: Optional[str] = None
    images: Optional[str] = None
    url: str
    name: str
    size: str
    alignment: str
    armor_class: list[dict[str, Union[str, int]]]
    hit_points: int
    hit_dice: str
    hit_points_roll: str
    speed: dict[str, str]
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int
    proficiency_bonus: int
    proficiencies: list[dict[str, Union[str, dict[str, str]]]]
    damage_vulnerabilities: list[str]
    damage_resistances: list[str]
    damage_immunities: list[str]
    condition_immunities: list[dict[str, str]]
    senses: dict[str, Union[str, int]]
    languages: str
    challenge_rating: float
    xp: int
    special_abilities: Optional[list[dict[str, str]]] = None
    legendary_actions: Optional[list[dict[str, str]]] = None
    actions: Optional[list[dict]] = None
    reactions: Optional[list[dict]] = None
    forms: Optional[list[dict[str, str]]] = None
            
            
#Makes a list of monster names        
def creaturename(creatures):
    return [m["name"] for m in creatures]

def build_labels(name, content, layout):
    #This dynamically generates the labels in a two row form layout
    label = QLabel(f'{content}')
    label.setWordWrap(True)
    layout.addRow(f'{name}', label)

def build_single_labels(content, layout):
    #This dynamically generates the labels in a single row layout
    label = QLabel(f'{content}')
    label.setWordWrap(True)
    layout.addRow(label)
        
def build_title(content, layout):
    #This takes the fed through label values and generates a formatted title
    #This then generated the underscore for the said title
    label = QLabel(f'{content}')
    label.setWordWrap(True)
    label.setStyleSheet("color: rgb(170, 170, 0);"
                        "font: 14pt Segoe UI;")
    layout.addRow(label)
    build_line(layout)

        
def build_line(layout):
    #This dynamically generates the separator lines in a single row layout
    h_line = QFrame()
    h_line.setFrameShape(QFrame.HLine)
    h_line.setFrameShadow(QFrame.Sunken)
    h_line.setStyleSheet("background-color: rgb(5, 128, 3);")
    layout.addRow(h_line)
 
def ability_modifier(number):
    #Calculating abilit score modifiers
    ability_table = [
        ("1", "-5"), 
        ("2-3", "-4"), 
        ("4-5", "-3"), 
        ("6-7", "-2"), 
        ("8-9", "-1"), 
        ("10-11", "0"), 
        ("12-13", "+1"), 
        ("14-15", "+2"), 
        ("16-17", "+3"), 
        ("18-19", "+4"), 
        ("20-21", "+5"), 
        ("22-23", "+6"), 
        ("24-25", "+7"), 
        ("26-27", "+8"), 
        ("28-29", "+9"), 
        ("30", "+10")
    ]

    for range, value in ability_table:
        if '-' in range:
            start, end = map(int, range.split('-'))
            if start <= number <= end:
                return value
        elif int(range) == number:
            return value   
                    
def parse_creature(userin, creatures, main_win_ui):

    for creature in creatures:
        
        #If the monster matches our filter we display to user
        creaturelow = creature["name"]
        if userin.lower() == creaturelow.lower():
            
            #Turns the creature into a dataclass
            creature_obj = _Creature(**creature)

            #== Removes previously generated labels
            #===========================
            formLayoutList = [main_win_ui.formLayout_3, 
                              main_win_ui.formLayout_5,
                              main_win_ui.formLayout_9,
                              main_win_ui.formLayout_7,
                              main_win_ui.formLayout_8,
                              main_win_ui.formLayout_11,
                              main_win_ui.formLayout,
                              main_win_ui.formLayout_12,
                              main_win_ui.formLayout_4,
                              main_win_ui.formLayout_2]

            for x in formLayoutList:
                while x.rowCount() > 0:
                    x.removeRow(0)

            #== form Layout 12
            #===========================
            build_single_labels((f"{creature_obj.size} {creature_obj.type.capitalize()} , {creature_obj.alignment.capitalize()}"), main_win_ui.formLayout_12)

            #== form Layout
            #===========================
            build_line(main_win_ui.formLayout)
            build_labels(
                "Hit Points :",
                f"{creature_obj.hit_points} ({creature_obj.hit_points_roll})",
                main_win_ui.formLayout,
            )

            #== Armor Class
            #===============
            parsed_armor = []
            for armor in creature_obj.armor_class:
                if 'spell' in armor:
                    parsed_armor.append(f"{armor['type'].capitalize()} {armor['value']} : {armor['spell']['name']}")
                elif 'condition' in armor:
                    parsed_armor.append(f"{armor['type'].capitalize()} {armor['value']} : {armor['condition']['name']}")
                elif 'armor' in armor:
                    for x in armor['armor']:
                        parsed_armor.append(f"{armor['type'].capitalize()} {armor['value']} : {x['name']}")
                else:
                    parsed_armor.append(f"{armor['type'].capitalize()} {armor['value']}")

            parsed_armor = " - ".join(parsed_armor)
            build_labels("Armor Class :", parsed_armor, main_win_ui.formLayout)

            #== Movement and Distance
            #===============  
            parsed_speed = [f"{Movement}: {Distance}" for Movement, Distance in creature_obj.speed.items()]
            parsed_speed = ' - '.join([x.capitalize() for x in parsed_speed])
            build_labels("Speed :", parsed_speed, main_win_ui.formLayout)

            #== form Layout 4
            #===========================      
            build_line(main_win_ui.formLayout_4)
            build_labels(
                "Challenge Rating :",
                f"{creature_obj.challenge_rating} ({creature_obj.xp})",
                main_win_ui.formLayout_4,
            )
            build_labels(f"Proficiency Bonus :", (f"{creature_obj.proficiency_bonus}"), main_win_ui.formLayout_4)

            #== form Layout 5
            #=========================== 
            #== Proficiencies
            #===============
            saving_line = []
            skill_line = []
            for x in creature_obj.proficiencies:
                name = x['proficiency']['name']
                if name.startswith("Skill"):
                    name = name.removeprefix("Skill: ")
                    skill_line.append(f"{name} {x["value"]}")
                if name.startswith("Saving Throw"):
                    name = name.removeprefix("Saving Throw: ")
                    saving_line.append(f"{name} {x["value"]}")
            if saving_line:
                saving_line = (' - '.join(saving_line))
                build_labels('Prof Saving Throw :', saving_line, main_win_ui.formLayout_5)
            if skill_line:    
                skill_line = (' - '.join(skill_line))
                build_labels('Prof Skill :', skill_line, main_win_ui.formLayout_5)

            if parsed_dam_res := creature_obj.damage_resistances:
                parsed_dam_res = (' - '.join([x.capitalize() for x in parsed_dam_res]))
                build_labels(f"Resistances :", parsed_dam_res, main_win_ui.formLayout_5)

            if parsed_dam_vul := list(creature_obj.damage_vulnerabilities):
                parsed_dam_vul = (' - '.join([x.capitalize() for x in parsed_dam_vul]))
                build_labels(f"Vulnerabilities :", parsed_dam_vul, main_win_ui.formLayout_5)


            #== Damage Immunities
            #===============  
            parsed_dam_imun = []
            if parsed_dam_imun := list(creature_obj.damage_immunities):
                parsed_dam_imun = (' - '.join([x.capitalize() for x in parsed_dam_imun]))
                build_labels(f"Damage Immunities :", parsed_dam_imun, main_win_ui.formLayout_5)

            #== Condition Immunities
            #===============  
            parsed_con_imun = []
            if parsed_con_imun := [
                x['name'] for x in creature_obj.condition_immunities
            ]:
                parsed_con_imun = (' - '.join(parsed_con_imun))
                build_labels(f"Condition Immunities :", parsed_con_imun, main_win_ui.formLayout_5)

            #== form Layout 2
            #=========================== 
            build_line(main_win_ui.formLayout_2)
            build_labels(f"STR :", (f"{creature_obj.strength} ({ability_modifier(creature_obj.strength)})"), main_win_ui.formLayout_2)
            build_labels(f"DEX :", (f"{creature_obj.dexterity} ({ability_modifier(creature_obj.dexterity)})"), main_win_ui.formLayout_2)
            build_labels(f"CON :", (f"{creature_obj.constitution} ({ability_modifier(creature_obj.constitution)})"), main_win_ui.formLayout_2)
            build_labels(f"INT :", (f"{creature_obj.intelligence} ({ability_modifier(creature_obj.intelligence)})"), main_win_ui.formLayout_2)
            build_labels(f"WIS :", (f"{creature_obj.wisdom} ({ability_modifier(creature_obj.wisdom)})"), main_win_ui.formLayout_2)
            build_labels(f"CHA :", (f"{creature_obj.charisma} ({ability_modifier(creature_obj.charisma)})"), main_win_ui.formLayout_2)

            #== form Layout 3
            #=========================== 
            build_line(main_win_ui.formLayout_3)

            #== Senses
            #===============
            parsed_senses = [f"{key.replace("_", " ")}: {value}" for key, value in creature_obj.senses.items()]
            parsed_senses = (' - '.join([x.capitalize() for x in parsed_senses]))
            build_labels('Senses(s) :', parsed_senses, main_win_ui.formLayout_3)

            #== Languages
            #===============
            build_labels('Language(s) :', creature_obj.languages, main_win_ui.formLayout_3)

            #== form Layout 9
            #===========================
            #== Spell slots
            #===============
            for x in creature_obj.special_abilities or []:
                if x['name'].startswith("Spellcasting"):
                    build_line(main_win_ui.formLayout_9) 
                    parsed_slots = [f"Level {level} - {slots}" for level, slots in x["spellcasting"]["slots"].items()]
                    parsed_slots = ('\n'.join(parsed_slots))
                    spell_slots = parsed_slots
                    build_labels('Spell Slot(s) :', spell_slots, main_win_ui.formLayout_9)

            #== form Layout 7
            #===========================           
            #Actions
            #===============
            if creature_obj.actions:
                build_title('Actions', main_win_ui.formLayout_7)
                for x in creature_obj.actions:
                    build_labels(f"{x['name']} :", x['desc'], main_win_ui.formLayout_7)

            #== form Layout 8
            #===========================
            #== Special Abilities - Spells Only
            #===============

            for x in creature_obj.special_abilities or []:
                if x['name'].startswith("Spellcasting"):
                    build_title('Spells', main_win_ui.formLayout_8)
                    spells_by_level = {}
                    for x in x["spellcasting"]["spells"]:
                        level = x["level"]
                        name = x["name"]
                        if level in spells_by_level:
                            spells_by_level[level].append(name)
                        else:
                            spells_by_level[level] = [name]

                    spells_by_level = dict(sorted(spells_by_level.items()))
                    for level, spells in spells_by_level.items():
                        spells = (' - '.join(spells))
                        build_labels((f'Level : {level}'), spells, main_win_ui.formLayout_8)

            #== form Layout 11
            #===========================
            #== Special Abilities - Excludes Spells
            #===============
            if creature_obj.special_abilities:
                first_check = False         
                for x in creature_obj.special_abilities:
                    if x['name'].startswith("Spellcasting"):
                        continue
                    if x['name'] != ("Spellcasting"):
                        if first_check == False:
                            build_title('Special Abilities', main_win_ui.formLayout_11)
                            first_check = True
                        build_labels(f'{x['name']} :', x['desc'], main_win_ui.formLayout_11)
