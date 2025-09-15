from sys import stderr
from typing import TYPE_CHECKING

import dearpygui.dearpygui as dpg
import nmrPype
import numpy as np
from scipy.optimize import minimize

from solventspinsim.simulate import simulate_peaklist
from solventspinsim.spin import Spin
from solventspinsim.themes import Theme

from .display import _optimization_ui, _update_optimization_ui
from .helper import unpack_params, unpack_params_water

if TYPE_CHECKING:
    from solventspinsim.simulate import Water


def section_optimization(
    nmr_array: np.ndarray,
    spin: Spin,
    matrix_shape: tuple,
    matrix_size: int,
    init_params: np.ndarray,
    water_range: tuple[float, float],
    simulate_water: bool = False,
) -> np.ndarray:
    from solventspinsim.main import DPGStatus
    from solventspinsim.simulate import Water

    if DPGStatus.is_context_enabled():
        _optimization_ui(spin)

    optimized_params_list: list = []
    spin_names = spin.spin_names

    # Define water peak bounds
    water_left: float = min(water_range)
    water_center: float = sum(water_range) / 2
    water_right: float = max(water_range)

    bounds = [water_left, water_center, water_right]

    # Find indices of each water bound
    increasing_x = nmr_array[0][::-1]
    bound_indices = np.searchsorted(increasing_x, bounds)
    indices = [len(nmr_array[0]) - i for i in bound_indices]
    quadrants: tuple[tuple[float, float], ...] = (
        (0, indices[2]),
        (indices[2], indices[1]),
        (indices[1], indices[0]),
        (indices[0], len(nmr_array[0])),
    )

    if simulate_water:
        param_bounds: list[tuple[float, float]] = (
            [(-100, 100)] * len(spin._couplings.flatten())
            + [(-1000, 1000)] * spin._nuclei_number
            + [(water_left, water_right)]
            + [(-1000, 1000)]
            + [(0.5, 100)]
            + [(1e-6, 1e6)]
            + [(1e-6, 1e6)]
            + [(0.5, 100)] * spin._nuclei_number
        )
    else:
        param_bounds: list[tuple[float, float]] = (
            [(-100, 100)] * len(spin._couplings.flatten())
            + [(-1000, 1000)] * spin._nuclei_number
            + [(1e-6, 1e6)]
            + [(1e-6, 1e6)]
            + [(0.5, 100)] * spin._nuclei_number
        )

    for quadrant in quadrants:
        start: int = quadrant[0]
        end: int = quadrant[1]

        real_x = nmr_array[0][start:end]
        real_y = nmr_array[1][start:end]

        # print(f"({start}, {end}) -> ({real_x[0]}, {real_x[-1]})", file=stderr)

        if DPGStatus.is_context_enabled():
            if dpg.does_item_exist("main_x_axis"):
                if dpg.does_item_exist("region_line_left"):
                    dpg.delete_item("region_line_left")
                if dpg.does_item_exist("region_line_right"):
                    dpg.delete_item("region_line_right")
                # Draw new region lines
                dpg.add_inf_line_series(
                    real_x[0],
                    label="Region Start",
                    parent="main_x_axis",
                    tag="region_line_left",
                )
                dpg.add_inf_line_series(
                    real_x[-1],
                    label="Region End",
                    parent="main_x_axis",
                    tag="region_line_right",
                )
                dpg.bind_item_theme("region_line_left", Theme.region_plot_theme())
                dpg.bind_item_theme("region_line_right", Theme.region_plot_theme())

        full_x = nmr_array[0]

        def quadrant_objective(params):
            if simulate_water:
                (
                    couplings,
                    intensities,
                    water_freq,
                    water_intensity,
                    water_hhw,
                    spec_width,
                    obs,
                    hhw,
                ) = unpack_params_water(params, matrix_size, matrix_shape)
                new_spin = Spin(
                    spin_names,
                    list(spin._ppm_nuclei_frequencies),
                    couplings,
                    list(hhw),
                    spin.field_strength,
                )
                simulation = simulate_peaklist(
                    new_spin.peaklist(list(intensities)),
                    len(real_x),
                    list(hhw),
                    (real_x[0], real_x[-1]),
                )
                new_water = Water(
                    water_freq, water_intensity, water_hhw, water_enable=True
                )
                water_simulation_full = simulate_peaklist(
                    new_water.peaklist,
                    len(full_x),
                    new_water.hhw,
                    (full_x[0], full_x[-1]),
                )
                water_y_quadrant = np.interp(
                    real_x, full_x, water_simulation_full[1][::-1]
                )
                sim_y = list(
                    np.ascontiguousarray(simulation[1][::-1] + water_y_quadrant)
                )

                if DPGStatus.is_context_enabled():
                    dpg.set_value("opt_wf", f"Water Frequency {water_freq}")
                    dpg.set_value("opt_wi", f"Water Intensity: {water_intensity}")
                    dpg.set_value("opt_whhw", f"Water Half-Height Width: {water_hhw}")
            else:
                couplings, intensities, spec_width, obs, hhw = unpack_params(
                    params, matrix_size, matrix_shape
                )
                new_spin = Spin(
                    spin_names,
                    list(spin._ppm_nuclei_frequencies),
                    couplings,
                    list(hhw),
                    spin.field_strength,
                )
                simulation = simulate_peaklist(
                    new_spin.peaklist(list(intensities)),
                    len(real_x),
                    list(hhw),
                    (real_x[0], real_x[-1]),
                )
                sim_y = list(np.ascontiguousarray(simulation[1][::-1]))

            if DPGStatus.is_context_enabled():
                _update_optimization_ui(
                    matrix_shape,
                    couplings,
                    intensities,
                    spec_width,
                    hhw,
                    real_x,
                    real_y,
                    sim_y,
                )

            return np.sqrt(np.mean((sim_y - real_y) ** 2))

        result = minimize(
            quadrant_objective, init_params, method="L-BFGS-B", bounds=param_bounds
        )
        optimized_params_list.append(result.x)
        init_params = result.x

    nuclei_quadrant_indices = []
    for quadrant in quadrants:
        start, end = quadrant
        quadrant_range = (nmr_array[0][start], nmr_array[0][end - 1])
        indices_in_quadrant = [
            idx
            for idx, freq in enumerate(spin._nuclei_frequencies)
            if min(quadrant_range) <= freq <= max(quadrant_range)
        ]
        nuclei_quadrant_indices.append(indices_in_quadrant)

    # for idx, quadrant in enumerate(nuclei_quadrant_indices):
    #     print(f"Quadrant {idx + 1}:", file=stderr, end=' ')
    #     for j in range(len(quadrant)):
    #         print(f"{quadrant[j]}", file=stderr, end=" ")
    #     print("", file=stderr)

    if simulate_water:
        couplings_list = []
        intensities_list = []
        hhw_list = []

        for opt_param in optimized_params_list:
            c, i, _, _, _, _, _, hhw = unpack_params_water(
                opt_param, matrix_size, matrix_shape
            )
            couplings_list.append(c)
            intensities_list.append(i)
            hhw_list.append(hhw)

        # Combine couplings and intensities from each quadrant using nuclei_quadrant_indices
        new_couplings = np.zeros_like(spin._couplings)
        new_intensities = np.zeros(spin._nuclei_number)
        new_hhw = np.zeros(spin._nuclei_number)

        for q_idx, indices in enumerate(nuclei_quadrant_indices):
            for i in indices:
                # For couplings, copy the row and column for each nucleus in this quadrant
                new_couplings[i, :] = couplings_list[q_idx][i, :]
                # For intensities, copy the value for each nucleus in this quadrant
                new_intensities[i] = intensities_list[q_idx][i]
                # For half_height_widths, copy the value for each nucleus in this quadrant
                new_hhw[i] = hhw_list[q_idx][i]

        _, _, new_water_freq, new_water_intensity, new_water_hhw, new_sw, new_obs, _ = (
            unpack_params_water(optimized_params_list[0], matrix_size, matrix_shape)
        )

        optimized_params = np.concatenate(
            (
                new_couplings.flatten(),
                new_intensities,
                [new_water_freq, new_water_intensity, new_water_hhw, new_sw, new_obs],
                new_hhw,
            )
        )

    else:
        couplings_list = []
        intensities_list = []
        hhw_list = []

        for opt_param in optimized_params_list:
            c, i, _, _, hhw = unpack_params(opt_param, matrix_size, matrix_shape)
            couplings_list.append(c)
            intensities_list.append(i)
            hhw_list.append(hhw)

        # Combine couplings and intensities from each quadrant using nuclei_quadrant_indices
        new_couplings = np.zeros_like(spin._couplings)
        new_intensities = np.zeros(spin._nuclei_number)
        new_hhw = np.zeros(spin._nuclei_number)

        for q_idx, indices in enumerate(nuclei_quadrant_indices):
            for i in indices:
                # For couplings, copy the row and column for each nucleus in this quadrant
                new_couplings[i, :] = couplings_list[q_idx][i, :]
                # For intensities, copy the value for each nucleus in this quadrant
                new_intensities[i] = intensities_list[q_idx][i]
                # For half_height_widths, copy the value for each nucleus in this quadrant
                new_hhw[i] = hhw_list[q_idx][i]

        _, _, new_sw, new_obs, _ = unpack_params(
            optimized_params_list[0], matrix_size, matrix_shape
        )

        # Use the last optimized parameters for other values
        optimized_params = np.concatenate(
            (new_couplings.flatten(), new_intensities, [new_sw, new_obs], new_hhw)
        )

    if DPGStatus.is_context_enabled():
        if dpg.does_item_exist("region_line_left"):
            dpg.delete_item("region_line_left")
        if dpg.does_item_exist("region_line_right"):
            dpg.delete_item("region_line_right")

    return optimized_params


def optimize_simulation(
    nmr_file: str,
    spin: Spin,
    water_range: tuple[float, float],
    water: "Water | None" = None,
) -> "Spin | tuple[Spin, Water]":
    from solventspinsim.simulate import Water

    df = nmrPype.DataFrame(nmr_file)

    if df.array is None:
        raise ValueError("nmrPype array is empty!")
    if df.array.ndim != 1:
        raise ValueError("Unsupported NMRPipe file dimensionality!")

    x_vals: np.ndarray = np.arange(1, len(df.array) + 1)

    init_sw: float = df.getParam("NDSW")
    init_obs: float = df.getParam("NDOBS")
    init_orig: float = df.getParam("NDORIG")
    init_size: float = df.getParam("NDSIZE")

    init_sw = 1.0 if (init_sw == 0.0) else init_sw
    init_obs = 1.0 if (init_obs == 0.0) else init_obs

    delta: float = -init_sw / (init_size)
    first: float = init_orig - delta * (init_size - 1)

    specValPPM = (first + (x_vals - 1.0) * delta) / init_obs
    specValHz: list[float] = [ppm * spin._field_strength for ppm in specValPPM]

    freq_limits: list[float] = [specValHz[0], specValHz[-1]]
    freq_limits.sort()

    nmr_array = np.vstack((specValHz, df.array))

    if water is not None:
        simulate_water = True
        initial_values: list[float] = [
            water.frequency,
            water.intensity,
            water.hhw,
            init_sw,
            init_obs,
        ]
    else:
        initial_values: list[float] = [init_sw, init_obs]
        simulate_water = False

    initial_intensities = [1.0] * spin._nuclei_number
    matrix_shape = spin._couplings.shape
    matrix_size: int = spin._couplings.size

    init_params: np.ndarray = np.concatenate(
        (
            spin._couplings.flatten(),
            initial_intensities,
            initial_values,
            spin._half_height_width,
        )
    )

    optimized_params = section_optimization(
        nmr_array,
        spin,
        matrix_shape,
        matrix_size,
        init_params,
        water_range,
        simulate_water,
    )

    if simulate_water:
        (
            new_couplings,
            new_intensities,
            new_water_freq,
            new_water_intensity,
            new_water_hhw,
            new_spec_width,
            new_obs,
            new_hhw,
        ) = unpack_params_water(optimized_params, matrix_size, matrix_shape)

        optimized_spin = Spin(
            spin.spin_names,
            spin._ppm_nuclei_frequencies,
            new_couplings,
            list(new_hhw),
            spin._field_strength,
            list(new_intensities),
        )
        optimized_water = Water(
            new_water_freq, new_water_intensity, new_water_hhw, True
        )

        print("Optimization Complete!", file=stderr)
        return optimized_spin, optimized_water
    else:
        new_couplings, new_intensities, new_spec_width, new_obs, new_hhw = (
            unpack_params(optimized_params, matrix_size, matrix_shape)
        )

        optimized_spin = Spin(
            spin.spin_names,
            spin._ppm_nuclei_frequencies,
            new_couplings,
            list(new_hhw),
            spin._field_strength,
            list(new_intensities),
        )
        print("Optimization Complete!", file=stderr)
        return optimized_spin
