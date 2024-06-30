import json
from flask import jsonify

class ConfigurationHandler:
	_required_keys = ["title", "maximum_minutes", "setups"]
	_required_setup_keys = ["name", "queue_file_path", "title_image"]
	
	def load(self, config_file_path):
		file = open(config_file_path)
		data = json.load(file)

		all_keys_exist = all(key in data for key in self._required_keys)
		if not all_keys_exist:
			raise Exception("Config file does not contain all neccessary keys")

		if not all(key in data["setups"][0] for key in self._required_setup_keys):
			raise Exception("Setup in config file does not contain all neccessary keys")

		# Multiple setups is handled in another issue
		self.setup = data["setups"][0]
		self.root = data

	def name(self):
		return self.setup["name"]

	def maximum_minutes(self):
		return self.root["maximum_minutes"]

	def queue_file_path(self):
		return self.setup["queue_file_path"]

	def title_image(self):
		return self.setup["title_image"]

	def title(self):
		return self.root["title"]

	def to_json(self):
		return jsonify(self.data)

configuration_handler = ConfigurationHandler()