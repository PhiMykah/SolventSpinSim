import json
import dearpygui.dearpygui as dpg
from pathlib import Path

DEFAULT_JSON_PATH = Path(__file__).parent / "default.json"
SCHEMA_PATH = Path(__file__).parent / "schema.json"

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ui.ui import UI

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

	def save_to_json(self, filepath : str):
		"""Save current registry values to a JSON file."""
		with open(filepath, 'w') as f:
			json.dump(self.values, f, indent=2, separators=(',', ': '))

	def update_settings(self, ui : "UI") -> None:
		from ui.graphics import SimulationSettings, OptimizationSettings, PlotWindow

		self.values["$schema"] = f"file:///{str(SCHEMA_PATH).replace("\\","/")}"
		# Files
		self.values["spin_file"] = ui.spin_file
		self.values["nmr_file"] = ui.nmr_file
		self.values["matrix_table"] = ui.mat_table
		# Spin Object
		spin : dict = {
			"spin_names" : ui.spin.spin_names,
			"nuclei_frequencies" : ui.spin.nuclei_frequencies,
			"half_height_width" : ui.spin.half_height_width,
			"field_strength" : ui.spin.field_strength,
			"intensities" : ui.spin.intensities,
			"coupling_strength" : "weak" if ui.spin.coupling_strength.value == 0 else "strong"
		}
		spin["couplings"] = [list(c) for c in ui.spin._couplings]

		self.values["spin"] = spin
		# Water range
		self.values["water_range"] = [ui.water_range[0], ui.water_range[1]]
		# Sim Settings Object
		sim_settings : dict = {
			"is_enabled" : ui.sim_settings.is_enabled,
			"field_strength" : ui.sim_settings[SimulationSettings.field_strength_tag],
			"points" : ui.sim_settings[SimulationSettings.points_tag],
			"intensity" : ui.sim_settings[SimulationSettings.intensity_tag],
			"half_height_width" : ui.sim_settings[SimulationSettings.hhw_tag],
			"use_settings" : ui.sim_settings[SimulationSettings.use_settings_tag],
		}
		self.values["sim_settings"] = sim_settings
		# Optimization Settings Object
		opt_settings : dict = {
			"is_enabled" : ui.opt_settings.is_enabled,
			"water_left" : ui.opt_settings[OptimizationSettings.water_left_tag],
			"water_right" : ui.opt_settings[OptimizationSettings.water_right_tag],
		}						
		self.values["opt_settings"] = opt_settings
		# Plot Window Object
		plot_window : dict = {
			"is_enabled" : ui.plot_window.is_enabled,
			"height" : ui.plot_window[PlotWindow.main_plot_tag],
			"x_axis_label" : ui.plot_window[PlotWindow.main_x_axis_tag],
			"y_axis_label" : ui.plot_window[PlotWindow.main_y_axis_tag],
		}
		self.values["plot_window"] = plot_window
		# Water Sim
		water_sim : dict = {
			"water_enable" : ui.water_sim.water_enable,
			"frequency" : ui.water_sim.frequency,
			"intensity" : ui.water_sim.intensity,
			"hhw" : ui.water_sim.hhw,
		}
		self.values["water_sim"] = water_sim

	# ---------------------------------------------------------------------------- #
	#                                 Magic Methods                                #
	# ---------------------------------------------------------------------------- #

	def __getitem__(self, key):
		return self.values[key]

	def __setitem__(self, key, value):
		self.values[key] = value

def save_settings_callback(sender, app_data, user_data : "tuple[Settings, UI]") -> None:
	"""Update all settings then save json file"""
	settings = user_data[0]
	ui = user_data[1]
	filepath : str = app_data['file_path_name']

	settings.update_settings(ui)
	settings.save_to_json(filepath)
