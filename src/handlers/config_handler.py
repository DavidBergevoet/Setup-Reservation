import json
from flask import jsonify


class ConfigurationHandler:
    _required_keys = ["title", "maximum_minutes", "secret_key", "setups"]
    _required_setup_keys = ["name", "queue_file_path", "title_image"]

    def load(self, config_file_path):
        file = open(config_file_path)
        data = json.load(file)

        all_keys_exist = all(key in data for key in self._required_keys)
        if not all_keys_exist:
            raise Exception("Config file does not contain all neccessary keys")

        if not all(key in data["setups"][0] for key in self._required_setup_keys):
            raise Exception(
                "Setup in config file does not contain all neccessary keys")

        # Multiple setups is handled in another issue
        self._setup = data["setups"][0]
        self._root = data

    def name(self):
        return self._setup["name"]

    def maximum_minutes(self):
        return self._root["maximum_minutes"]

    def queue_file_path(self):
        return self._setup["queue_file_path"]

    def title_image(self):
        return self._setup["title_image"]

    def title(self):
        return self._root["title"]

    def secret_key(self):
        return self._root["secret_key"]

    def setup(self):
        return jsonify(self._setup)


configuration_handler = ConfigurationHandler()
