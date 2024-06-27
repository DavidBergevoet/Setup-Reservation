import json
from flask import jsonify

class ConfigurationHandler:
	_required_keys = ["name", "maximum_minutes", "queue_file_path", "title_image"]
	
	def load(self, config_file_path):
		file = open(config_file_path)
		data = json.load(file)

		all_keys_exist = all(key in data for key in self._required_keys)
		if not all_keys_exist:
			raise Exception("Config file does not contain all neccessary keys")
		self.data = data

	def name(self):
		return self.data["name"]

	def maximum_minutes(self):
		return self.data["maximum_minutes"]

	def queue_file_path(self):
		return self.data["queue_file_path"]

	def title_image(self):
		return self.data["title_image"]

	def to_json(self):
		return jsonify(self.data)

configuration_handler = ConfigurationHandler()