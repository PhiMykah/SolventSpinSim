from nmrPype import DataFrame, write_to_file
from numpy import array as nparray

from solventspinsim.settings import Settings
from solventspinsim.simulate.water import Water
from solventspinsim.spin import Spin, loadSpinFromFile


class CommandLine:
    def __init__(self, settings: Settings):
        self.settings: Settings = settings
        self.spin = Spin()
        self.water = Water()

    def run(self) -> None:
        from solventspinsim.simulate import simulate_peaklist

        optimizations: Spin | tuple[Spin, Water] = self._optimize()

        if isinstance(optimizations, Spin):
            optimized_spin: Spin = optimizations
            optimized_water: Water = self.water
        else:
            optimized_spin = optimizations[0]
            optimized_water = optimizations[1]

        points: int = self.settings["sim_settings"]["points"]

        simulation = simulate_peaklist(
            optimized_spin.peaklist(), points, optimized_spin.half_height_width
        )

        if self.water.water_enable:
            l_limit: float = simulation[0][0]
            r_limit: float = simulation[0][-1]

            water_simulation = simulate_peaklist(
                optimized_water.peaklist,
                points,
                optimized_water.hhw,
                (l_limit, r_limit),
            )

            output_result = [simulation[0], simulation[1] + water_simulation[1]]
        else:
            output_result = [simulation[0], simulation[1]]

        self._save_to_nmr(output_result)

    def _set_spin(self) -> None:
        loaded_spin_names, loaded_nuclei_frequencies, loaded_couplings = (
            loadSpinFromFile(self.settings["spin_file"])
        )
        spin_dict: dict = self.settings["spin"]
        sim_settings_dict: dict = self.settings["sim_settings"]

        spin_names: list[str] = (
            spin_dict["spin_names"] if spin_dict["spin_names"] else loaded_spin_names
        )

        nuclei_frequencies: list[float] | list[int] = (
            spin_dict["nuclei_frequencies"]
            if spin_dict["nuclei_frequencies"]
            else loaded_nuclei_frequencies
        )

        nuclei_count: int = len(nuclei_frequencies)

        couplings = (
            spin_dict["couplings"] if spin_dict["couplings"] else loaded_couplings
        )

        field_strength: float = sim_settings_dict["field_strength"]

        intensities: list[float] = (
            spin_dict["intensities"]
            if spin_dict["intensities"]
            else [sim_settings_dict["intensity"]] * nuclei_count
        )

        hhw = (
            spin_dict["half_height_width"]
            if spin_dict["half_height_width"]
            else [sim_settings_dict["half_height_width"]] * nuclei_count
        )

        coupling_strength = spin_dict["coupling_strength"]

        self.spin = Spin(
            spin_names,
            nuclei_frequencies,
            couplings,
            hhw,
            field_strength,
            intensities,
            coupling_strength,
        )

    def _set_water(self) -> None:
        water_sim: dict = self.settings["water_sim"]
        self.water = Water(
            water_sim["frequency"],
            water_sim["intensity"],
            water_sim["hhw"],
            water_sim["water_enable"],
        )

    def _optimize(self) -> Spin | tuple[Spin, Water]:
        from solventspinsim.optimize import optimize_simulation

        nmr_file: str = self.settings["nmr_file"]
        opt_settings: dict = self.settings["opt_settings"]

        self._set_spin()
        self._set_water()

        water_range: tuple[float, float] = (
            opt_settings["water_left"],
            opt_settings["water_right"],
        )

        if self.water.water_enable:
            optimizations: Spin | tuple[Spin, Water] = optimize_simulation(
                nmr_file, self.spin, water_range, self.water
            )
        else:
            optimizations = optimize_simulation(nmr_file, self.spin, water_range, None)

        return optimizations

    def _save_to_nmr(self, simulation) -> None:
        df = DataFrame(self.settings["nmr_file"])

        result_array = nparray(simulation[1][::-1], dtype="float32")
        df.setArray(result_array)

        output_file: str = (
            self.settings["output_file"]
            if self.settings["output_file"]
            else "output.ft1"
        )

        write_to_file(df, output_file, True)
