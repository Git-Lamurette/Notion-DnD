
def load_data():
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