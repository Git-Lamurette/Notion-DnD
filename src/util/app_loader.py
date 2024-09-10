# utils/app_loader.py
import os
import json
from py_dm_tk.utilities.json_parser import parsing_monster_data
from py_dm_tk.models.creature_table_model import (
    CreatureTableModel,
    creatureTableProxyModel,
)

from PySide6.QtCore import Qt


class AppLoader:
    def __init__(self, json_directory, splash_screen):
        self.json_directory = json_directory
        self.splash_screen = splash_screen
        self.models = {}
        self.proxy_models = {}
        self.parsed_data = {}

        self.parser_mapping = {"5e-SRD-Monsters.json": parsing_monster_data}

        self.model_mapping = {
            "5e-SRD-Monsters.json": (CreatureTableModel, creatureTableProxyModel)
        }

    def load_and_parse_data(self):
        self.splash_screen.update_message("Loading data files...")
        self.raw_data = {}

        for file_name in self.parser_mapping.keys():
            file_path = os.path.join(self.json_directory, file_name)
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    data = json.load(f)
                self.raw_data[file_name] = data

        for file_name, data in self.raw_data.items():
            parsing_func = self.parser_mapping[file_name]
            self.parsed_data[file_name] = parsing_func(data)

    def create_models_and_proxies(self):
        self.splash_screen.update_message("Creating models and proxies...")

        for file_name, data in self.parsed_data.items():

            model_class, proxy_class = self.model_mapping[file_name]

            if file_name == "5e-SRD-Monsters.json":

                headers = data["header"]
                table = data["creature_data"]

                model = model_class(table, headers)

                self.models[file_name] = model

                proxy_model = proxy_class()
                proxy_model.setSourceModel(model)
                self.proxy_models[file_name] = proxy_model
