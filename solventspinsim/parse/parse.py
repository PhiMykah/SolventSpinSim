import argparse
import json
from pathlib import Path


def get_settings_schema(schema_path: Path | None = None):
    """Load settings schema for argument help and types."""
    if schema_path is None:
        schema_path = Path(__file__).parent.parent / "settings" / "schema.json"
    with open(schema_path, "r") as f:
        return json.load(f)


def build_parser() -> argparse.ArgumentParser:
    """
    Empty Parser:
    Namespace(settings=None, spin_file=None, nmr_file=None,
                field_strength=None, water_range=None,
                sim_enabled=False, points=None, intensity=None,
                hhw=None, sim_use_settings=False, opt_enabled=False,
                water_bounds=None, plot_enabled=False, plot_height=None,
                x=None, y=None, water_enable=False, water_frequency=None,
                water_intensity=None, water_hhw=None, title=None)
    """
    parser = argparse.ArgumentParser(
        description="SolventSpinSim Command Line Arguments"
    )

    parser.add_argument(
        "-help",
        action="help",
        default=argparse.SUPPRESS,
        help="Show this help message and exit",
    )

    # Main settings arguments
    parser.add_argument(
        "--settings",
        type=str,
        metavar="'Settings Path'",
        default=None,
        dest="settings",
        help="Path to settings JSON file",
    )
    parser.add_argument(
        "--spin-file",
        type=str,
        metavar="'Spin File Path'",
        dest="spin_file",
        help="Path to spin matrix file",
    )
    parser.add_argument(
        "--nmr-file",
        type=str,
        metavar="'NMR File Path'",
        dest="nmr_file",
        help="Path to NMR data file",
    )

    # Water range Settings
    parser.add_argument(
        "--water-range",
        type=float,
        nargs=2,
        metavar=("LEFT", "RIGHT"),
        dest="water_range",
        help="Water range as two floats",
    )

    # Simulation settings
    parser.add_argument(
        "--sim-enabled",
        action="store_true",
        dest="sim_enabled",
        help="Enable simulation",
    )
    parser.add_argument(
        "--field-strength",
        type=float,
        metavar="FIELD_STRENGTH",
        dest="field_strength",
        help="Magnetic field strength (in Hz)",
    )
    parser.add_argument(
        "--points",
        type=int,
        metavar="POINTS",
        dest="sim_points",
        help="Number of simulation points",
    )
    parser.add_argument(
        "--intensity",
        type=float,
        metavar="INTENSITY",
        dest="sim_intensity",
        help="Simulation intensity",
    )
    parser.add_argument(
        "--hhw",
        type=float,
        metavar="HHW",
        dest="sim_hhw",
        help="Simulation half-height width",
    )
    parser.add_argument(
        "--sim-use-settings",
        action="store_true",
        dest="sim_use_settings",
        help="Use simulation settings",
    )

    # Optimization settings
    parser.add_argument(
        "--opt-enabled",
        action="store_true",
        dest="opt_enabled",
        help="Enable optimization settings",
    )
    parser.add_argument(
        "--water-bounds",
        type=float,
        nargs=2,
        metavar=("LEFT", "RIGHT"),
        dest="water_bounds",
        help="Water signal left and right bounds (in Hz)",
    )

    # Plot window settings
    parser.add_argument(
        "--plot-enabled",
        action="store_true",
        dest="plot_enabled",
        help="Enable interaction with the plot window",
    )
    parser.add_argument(
        "--plot-height",
        type=int,
        metavar="HEIGHT",
        dest="plot_height",
        help="Plot window height",
    )
    parser.add_argument(
        "--x",
        type=str,
        metavar="X_LABEL",
        dest="plot_x_label",
        help="Main plot window x-axis label",
    )
    parser.add_argument(
        "--y",
        type=str,
        metavar="Y_LABEL",
        dest="plot_y_label",
        help="Main plot window y-axis label",
    )

    # Water simulation settings
    parser.add_argument(
        "--water-enable",
        action="store_true",
        dest="water_enable",
        help="Enable water simulation",
    )
    parser.add_argument(
        "--water-frequency",
        type=float,
        metavar="FREQUENCY",
        dest="water_frequency",
        help="Water frequency",
    )
    parser.add_argument(
        "--water-intensity",
        type=float,
        metavar="INTENSITY",
        dest="water_intensity",
        help="Water intensity",
    )
    parser.add_argument(
        "--water-hhw",
        type=float,
        metavar="HHW",
        dest="water_hhw",
        help="Water half-height width",
    )

    # UI arguments
    parser.add_argument(
        "--title", type=str, metavar="MY_TITLE", dest="ui_title", help="UI window title"
    )

    return parser


class SettingsArguments(argparse.Namespace):
    def __init__(
        self,
        settings: str | None,
        spin_file: str | None,
        nmr_file: str | None,
        field_strength: float | None,
        water_range: list[float],
        sim_enabled: bool | None,
        sim_points: int | None,
        sim_intensity: float | None,
        sim_hhw: float | None,
        sim_use_settings: bool | None,
        opt_enabled: bool | None,
        water_bounds: list[float],
        plot_enabled: bool | None,
        plot_height: int | None,
        plot_x_label: str | None,
        plot_y_label: str | None,
        water_enable: bool | None,
        water_frequency: float | None,
        water_intensity: float | None,
        water_hhw: float | None,
        ui_title: str,
    ) -> None:
        # Main settings arguments
        self.settings: str | None = settings
        self.spin_file: str | None = spin_file
        self.nmr_file: str | None = nmr_file

        # Water range Settings
        self.water_range: list[float] = water_range

        # Simulation Settings
        self.sim_enabled: bool | None = sim_enabled
        self.field_strength: float | None = field_strength
        self.sim_points: int | None = sim_points
        self.sim_intensity: float | None = sim_intensity
        self.sim_hhw: float | None = sim_hhw
        self.sim_use_settings: bool | None = sim_use_settings

        # Optimization settings
        self.opt_enabled: bool | None = opt_enabled
        self.water_bounds: list[float] = water_bounds

        # Plot window settings
        self.plot_enabled: bool | None = plot_enabled
        self.plot_height: int | None = plot_height
        self.plot_x_label: str | None = plot_x_label
        self.plot_y_label: str | None = plot_y_label

        # Water simulation settings
        self.water_enable: bool | None = water_enable
        self.water_frequency: float | None = water_frequency
        self.water_intensity: float | None = water_intensity
        self.water_hhw: float | None = water_hhw

        # UI arguments
        self.ui_title: str | None = ui_title


def parse_args(argv: list[str] | None = None) -> SettingsArguments:
    parser: argparse.ArgumentParser = build_parser()
    args: argparse.Namespace = parser.parse_args(argv)
    return SettingsArguments(
        args.settings,
        args.spin_file,
        args.nmr_file,
        args.field_strength,
        args.water_range,
        args.sim_enabled,
        args.sim_points,
        args.sim_intensity,
        args.sim_hhw,
        args.sim_use_settings,
        args.opt_enabled,
        args.water_bounds,
        args.plot_enabled,
        args.plot_height,
        args.plot_x_label,
        args.plot_y_label,
        args.water_enable,
        args.water_frequency,
        args.water_intensity,
        args.water_hhw,
        args.ui_title,
    )


if __name__ == "__main__":
    args: SettingsArguments | None = parse_args()
    print(args)
