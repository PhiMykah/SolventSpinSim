import json
import dearpygui.dearpygui as dpg
from pathlib import Path

DEFAULT_JSON_PATH = Path(__file__).parent / "default.json"

class Settings:
	def __init__(self, json_path: Path = DEFAULT_JSON_PATH):
		"""
		Loads settings from a JSON file and applies them to the value registry.
		"""
		self.json_path = json_path
		self.values = {}
		self.load_from_json(self.json_path)

	def load_from_json(self, filepath : Path):
		"""Load values from a JSON file"""
		with open(filepath, 'r') as f:
			self.values = json.load(f)

	# def apply_to_registry(self):
	# 	"""Apply loaded values to value registry, creating if missing."""
	# 	with dpg.value_registry():
	# 		for tag, value in self.values.items():
	# 			# Only create value if not exists
	# 			if dpg.does_item_exist(tag):
	# 				dpg.set_value(tag, value)
	# 			else:
	# 				if isinstance(value, int):
	# 					dpg.add_int_value(tag=tag, default_value=value)
	# 				elif isinstance(value, float):
	# 					dpg.add_float_value(tag=tag, default_value=value)
	# 				elif isinstance(value, bool):
	# 					dpg.add_bool_value(tag=tag, default_value=value)
	# 				elif isinstance(value, str):
	# 					dpg.add_string_value(tag=tag, default_value=value)
	# 				elif isinstance(value, list):
	# 					# Save lists as string for registry
	# 					dpg.add_string_value(tag=tag, default_value=json.dumps(value))
	# 				else:
	# 					dpg.add_string_value(tag=tag, default_value=str(value))

	def save_to_json(self, filepath : str):
		"""Save current registry values to a JSON file."""
		# Only save tags that exist in registry
		self.values = {tag: dpg.get_value(tag) for tag in self.values.keys() if dpg.does_item_exist(tag)}
		with open(filepath, 'w') as f:
			json.dump(self.values, f, indent=2)

	def __getitem__(self, key):
		return self.values[key]

	def __setitem__(self, key, value):
		self.values[key] = value
