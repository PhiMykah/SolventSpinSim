import json
from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING

from parse import SettingsArguments

if TYPE_CHECKING:
    from ui import UI

DEFAULT_JSON_PATH = Path(__file__).parent / "default.json"
SCHEMA_PATH = Path(__file__).parent / "schema.json"


class Settings:
    def __init__(
        self, args: SettingsArguments | None = None, json_path: Path = DEFAULT_JSON_PATH
    ):
        """
        Loads settings from a JSON file and applies them to the value registry.
        """
        self.json_path = json_path
        self.values = {}
        if args is not None:
            if args.settings is not None:
                self.json_path = Path(args.settings)
                self.load_from_json(args.settings)
                self.load_from_args(args)
            else:
                self.load_from_json(DEFAULT_JSON_PATH)
                self.load_from_args(args)
        else:
            self.load_from_json(self.json_path)

    def load_from_args(self, args: SettingsArguments) -> None:
        # Main settings arguments
        self._set_attribute("ui_disabled", value=args.ui_disabled)
        self._set_attribute("spin_file", value=args.spin_file)
        self._set_attribute("nmr_file", value=args.nmr_file)

        # Water range Settings
        self._set_attribute("water_range", args.water_range)

        # Simulation Settings
        if not self.values["sim_settings"]:
            self.values["sim_settings"] = {}
        self._set_attribute("sim_settings", "is_enabled", value=args.sim_enabled)
        self._set_attribute("sim_settings", "field_strength", value=args.field_strength)
        self._set_attribute("sim_settings", "points", value=args.sim_points)
        self._set_attribute("sim_settings", "intensity", value=args.sim_intensity)
        self._set_attribute("sim_settings", "half_height_width", value=args.sim_hhw)
        self._set_attribute("sim_settings", "use_settings", value=args.sim_use_settings)

        # Optimization settings
        if not self.values["opt_settings"]:
            self.values["opt_settings"] = {}
        self._set_attribute("opt_settings", "is_enabled", value=args.opt_enabled)
        if args.water_bounds is not None:
            self._set_attribute(
                "opt_settings", "water_left", value=args.water_bounds[0]
            )
            self._set_attribute(
                "opt_settings", "water_right", value=args.water_bounds[1]
            )

        # Plot window settings
        if not self.values["plot_window"]:
            self.values["plot_window"] = {}
        self._set_attribute("plot_window", "is_enabled", value=args.plot_enabled)
        self._set_attribute("plot_window", "height", value=args.plot_height)
        self._set_attribute("plot_window", "x_axis_label", value=args.plot_x_label)
        self._set_attribute("plot_window", "y_axis_label", value=args.plot_y_label)

        # Water simulation settings
        if not self.values["water_sim"]:
            self.values["water_sim"] = {}
        self._set_attribute("water_sim", "water_enable", value=args.water_enable)
        self._set_attribute("water_sim", "frequency", value=args.water_frequency)
        self._set_attribute("water_sim", "intensity", value=args.water_intensity)
        self._set_attribute("water_sim", "hhw", value=args.water_hhw)

        # UI arguments
        self._set_attribute("title", value=args.ui_title)

    def load_from_json(self, filepath: Path | str):
        """Load values from a JSON file"""
        with open(filepath, "r") as f:
            self.values = json.load(f)

    def save_to_json(self, filepath: str):
        """Save current registry values to a JSON file."""
        with open(filepath, "w") as f:
            json.dump(self.values, f, indent=2, separators=(",", ": "))

    def update_settings(self, ui: "UI") -> None:
        from graphics import OptimizationSettings, PlotWindow, SimulationSettings

        self.values["$schema"] = f"file:///{str(SCHEMA_PATH).replace('\\', '/')}"
        # Files
        self.values["title"] = ui.title
        self.values["ui_disabled"] = False
        self.values["spin_file"] = ui.spin_file
        self.values["nmr_file"] = ui.nmr_file
        self.values["output_file"] = ui.output_file

        # Spin Object
        spin: dict = {
            "spin_names": ui.spin.spin_names,
            "nuclei_frequencies": ui.spin._ppm_nuclei_frequencies,
            "half_height_width": ui.spin.half_height_width,
            "field_strength": ui.spin.field_strength,
            "intensities": ui.spin.intensities,
            "coupling_strength": "weak"
            if ui.spin.coupling_strength.value == 0
            else "strong",
        }
        spin["couplings"] = [list(c) for c in ui.spin._couplings]

        self.values["spin"] = spin
        # Water range
        self.values["water_range"] = [ui.water_range[0], ui.water_range[1]]
        # Sim Settings Object
        sim_settings: dict = {
            "is_enabled": ui.sim_settings.is_enabled,
            "field_strength": ui.sim_settings[SimulationSettings.field_strength_tag],
            "points": ui.sim_settings[SimulationSettings.points_tag],
            "intensity": ui.sim_settings[SimulationSettings.intensity_tag],
            "half_height_width": ui.sim_settings[SimulationSettings.hhw_tag],
            "use_settings": ui.sim_settings[SimulationSettings.use_settings_tag],
        }
        self.values["sim_settings"] = sim_settings
        # Optimization Settings Object
        opt_settings: dict = {
            "is_enabled": ui.opt_settings.is_enabled,
            "water_left": ui.opt_settings[OptimizationSettings.water_left_tag],
            "water_right": ui.opt_settings[OptimizationSettings.water_right_tag],
        }
        self.values["opt_settings"] = opt_settings
        # Plot Window Object
        plot_window: dict = {
            "is_enabled": ui.plot_window.is_enabled,
            "height": ui.plot_window[PlotWindow.main_plot_tag],
            "x_axis_label": ui.plot_window[PlotWindow.main_x_axis_tag],
            "y_axis_label": ui.plot_window[PlotWindow.main_y_axis_tag],
        }
        self.values["plot_window"] = plot_window
        # Water Sim
        water_sim: dict = {
            "water_enable": ui.water_sim.water_enable,
            "frequency": ui.water_sim.frequency,
            "intensity": ui.water_sim.intensity,
            "hhw": ui.water_sim.hhw,
        }
        self.values["water_sim"] = water_sim

    def update_ui(self, ui: "UI") -> None:
        from graphics import OptimizationSettings, PlotWindow, SimulationSettings
        from simulate import Water
        from spin import Spin

        # Files
        ui.title = self.values.get("title", "SolventSpinSim")
        ui.spin_file = self.values.get("spin_file", "")
        ui.nmr_file = self.values.get("nmr_file", "")
        ui.mat_table = self.values.get("matrix_table", "")
        ui.output_file = self.values.get("output_file", "output.ft1")

        # Spin Object
        spin: dict = self.values.get("spin", {})
        spin_names = spin.get("spin_names", [])
        ppm_nuclei_frequencies = spin.get("nuclei_frequencies", [])
        couplings = [c for c in spin.get("couplings", [])]
        half_height_width = spin.get("half_height_width", 1.0)
        field_strength = spin.get("field_strength", 500.0)
        intensities = spin.get("intensities", [])
        coupling_strength = spin.get("coupling_strength", "weak")
        loaded_spin = Spin(
            spin_names,
            ppm_nuclei_frequencies,
            couplings,
            half_height_width,
            field_strength,
            intensities,
            coupling_strength,
        )
        ui.spin = loaded_spin

        # Water range
        water_range = self.values.get("water_range", [0.0, 1000.0])
        ui.water_range = (water_range[0], water_range[1])

        # Sim Settings Object
        sim_settings: dict = self.values.get("sim_settings", {})
        ui.sim_settings.is_enabled = sim_settings.get("is_enabled", False)
        ui.sim_settings[SimulationSettings.field_strength_tag] = sim_settings.get(
            "field_strength", 500.0
        )
        ui.sim_settings[SimulationSettings.points_tag] = sim_settings.get(
            "points", 1000
        )
        ui.sim_settings[SimulationSettings.intensity_tag] = sim_settings.get(
            "intensity", 1.0
        )
        ui.sim_settings[SimulationSettings.hhw_tag] = sim_settings.get(
            "half_height_width", 1.0
        )
        ui.sim_settings[SimulationSettings.use_settings_tag] = sim_settings.get(
            "use_settings", False
        )
        ui.sim_settings.update_ui_values()

        # Optimization Settings Object
        opt_settings: dict = self.values.get("opt_settings", {})
        ui.opt_settings.is_enabled = opt_settings.get("is_enabled", False)
        ui.opt_settings[OptimizationSettings.water_left_tag] = opt_settings.get(
            "water_left", 0.0
        )
        ui.opt_settings[OptimizationSettings.water_right_tag] = opt_settings.get(
            "water_right", 10.0
        )
        ui.opt_settings.update_ui_values()

        # Plot Window Object
        plot_window: dict = self.values.get("plot_window", {})
        ui.plot_window.is_enabled = plot_window.get("is_enabled", False)
        ui.plot_window[PlotWindow.main_plot_tag] = plot_window.get("height", 400)
        ui.plot_window[PlotWindow.main_x_axis_tag] = plot_window.get(
            "x_axis_label", "x"
        )
        ui.plot_window[PlotWindow.main_y_axis_tag] = plot_window.get(
            "y_axis_label", "y"
        )
        ui.plot_window.update_ui_values()

        # Water Sim
        water_sim: dict = self.values.get("water_sim", {})
        water_enable = water_sim.get("water_enable", False)
        water_frequency = water_sim.get("frequency", 0.0)
        water_intensity = water_sim.get("intensity", 1.0)
        water_hhw = water_sim.get("hhw", 0.0)
        loaded_water = Water(water_frequency, water_intensity, water_hhw, water_enable)
        ui.water_sim = loaded_water

    # ---------------------------------------------------------------------------- #
    #                                 Magic Methods                                #
    # ---------------------------------------------------------------------------- #

    def __getitem__(self, key):
        return self.values[key]

    def __setitem__(self, key, value):
        self.values[key] = value

    # ---------------------------------------------------------------------------- #
    #                               Helper Functions                               #
    # ---------------------------------------------------------------------------- #

    def _set_attribute(self, *keys, value=None, default=None) -> None:
        if value is not None:
            if isinstance(value, Iterable) and not isinstance(value, str):
                if all(value):
                    return_value = value
                else:
                    return_value = default
            else:
                return_value = value
        else:
            return_value = default

        if return_value is None:
            return

        if len(keys) == 1:
            self.values[keys[0]] = return_value
        else:
            _set_nested(self.values, return_value, *keys)


def save_settings_callback(sender, app_data, user_data: "tuple[Settings, UI]") -> None:
    """Update all settings then save json file"""
    settings = user_data[0]
    ui = user_data[1]
    filepath: str = app_data["file_path_name"]

    settings.update_settings(ui)
    settings.save_to_json(filepath)


def load_settings_callback(sender, app_data, user_data: "tuple[Settings, UI]") -> None:
    settings = user_data[0]
    ui = user_data[1]
    filepath: str = app_data["file_path_name"]

    settings.load_from_json(filepath)
    settings.update_ui(ui)


def _set_nested(dict_, set_value, *keys, default=None):
    target_dict = _get_nested_dict(dict_, *keys, default=default)
    target_dict[keys[-1]] = set_value
    return target_dict


def _get_nested_dict(dict_, *keys, default=None):
    if not isinstance(dict_, dict):
        raise TypeError("Object must be dictionary to obtain nested dictionary!")
    if not dict_:
        return dict_
    elem = dict_.get(keys[0], default)
    if len(keys) == 1:
        return dict_
    return _get_nested_dict(elem, *keys[1:], default=default)


def _get_nested(dict_, *keys, default=None):
    if not isinstance(dict_, dict):
        return default
    if not dict_:
        return dict_
    elem = dict_.get(keys[0], default)
    if len(keys) == 1:
        return elem
    return _get_nested_dict(elem, *keys[1:], default=default)
