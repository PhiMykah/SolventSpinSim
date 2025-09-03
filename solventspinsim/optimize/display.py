import dearpygui.dearpygui as dpg
from callbacks import show_item_callback
from spin import Spin
from ui.themes import Theme


def _optimization_ui(spin: Spin):
    if not dpg.does_item_exist("opt_window"):
        with dpg.window(
            label="Optimization in Progress", tag="opt_window", width=600, height=500
        ) as opt_window:
            with dpg.plot(
                label="Optimization Snippet", tag="opt_plot", width=-1, height=400
            ):
                dpg.add_plot_legend()
                dpg.add_plot_axis(dpg.mvXAxis, label="x", tag="opt_x_axis")
                dpg.add_plot_axis(dpg.mvYAxis, label="y", tag="opt_y_axis")
        with dpg.window(
            label="Optimization Parameters",
            tag="opt_params_window",
            width=400,
            height=600,
        ) as opt_window:
            dpg.add_text("Couplings:", tag="opt_coupling_title")
            with dpg.table(
                tag="opt_coupling_table",
                header_row=True,
                row_background=False,
                borders_innerH=True,
                borders_outerH=True,
                borders_innerV=True,
                borders_outerV=True,
                delay_search=True,
                parent=opt_window,
            ):
                dpg.add_table_column(label="##Top Left Corner")
                for atom in spin.spin_names:
                    dpg.add_table_column(label=str(atom))
                for i in range(spin._couplings.shape[0]):
                    with dpg.table_row():
                        dpg.add_text(spin.spin_names[i], tag=f"coupling_row_{i}_header")
                        for j in range(spin._couplings.shape[-1]):
                            dpg.add_text("", tag=f"opt_coupling_{i}_{j}")

            dpg.add_text("Intensities:", tag="opt_intensity_title")
            with dpg.table(
                tag="opt_intensity_table",
                header_row=False,
                row_background=False,
                borders_innerH=True,
                borders_outerH=True,
                borders_innerV=True,
                borders_outerV=True,
                delay_search=True,
                parent=opt_window,
            ):
                for i in range(spin._couplings.shape[0]):
                    dpg.add_table_column()

                with dpg.table_row():
                    for i in range(spin._couplings.shape[1]):
                        dpg.add_text("", tag=f"opt_intensities_{i}")

            dpg.add_text(default_value="Water Frequency", tag="opt_wf")

            dpg.add_text(default_value="Water Intensity", tag="opt_wi")

            dpg.add_text(default_value="Water Half-Height Width", tag="opt_whhw")

            dpg.add_text(default_value="Spectral Width", tag="opt_sw")

            dpg.add_text(default_value="Observation Frequency", tag="opt_obs")

            dpg.add_text("Half-Height Width:", tag="opt_hhw_title")
            with dpg.table(
                tag="opt_hhw_table",
                row_background=False,
                header_row=False,
                borders_innerH=True,
                borders_outerH=True,
                borders_innerV=True,
                borders_outerV=True,
                delay_search=True,
                parent=opt_window,
            ):
                for i in range(spin._couplings.shape[0]):
                    dpg.add_table_column()

                with dpg.table_row():
                    for i in range(spin._couplings.shape[1]):
                        dpg.add_text("", tag=f"opt_hhw_{i}")
        with dpg.value_registry():
            dpg.add_bool_value(default_value=False, tag="opt_series_added")
    else:
        dpg.show_item("opt_window")

    dpg.fit_axis_data("opt_x_axis")

    dpg.add_menu_item(
        label="Show Optimization Graph",
        callback=show_item_callback,
        user_data="opt_window",
        parent="view_menu",
    )
    dpg.add_menu_item(
        label="Show Optimization Parameters",
        callback=show_item_callback,
        user_data="opt_params_window",
        parent="view_menu",
    )


def _update_optimization_ui(
    matrix_shape, couplings, intensities, spec_width, hhw, real_x, real_y, sim_y
):
    for i in range(matrix_shape[0]):
        for j in range(matrix_shape[1]):
            dpg.set_value(f"opt_coupling_{i}_{j}", f"{couplings[i][j]}")
    for i in range(matrix_shape[0]):
        dpg.set_value(f"opt_intensities_{i}", f"{intensities[i]}")
    dpg.set_value("opt_sw", f"Spectral Width: {spec_width:.03f}")
    dpg.set_value("opt_obs", f"Observation Frequency: {spec_width:.03f}")
    for i in range(matrix_shape[0]):
        dpg.set_value(f"opt_hhw_{i}", f"{hhw[i]}")

    if not dpg.does_item_exist("sim_opt_series"):
        dpg.add_line_series(
            real_x,
            sim_y,
            label="Simulation Slice",
            parent="opt_y_axis",
            tag="sim_opt_series",
        )
        dpg.bind_item_theme("sim_opt_series", Theme.sim_plot_theme())
    else:
        dpg.set_value("sim_opt_series", [real_x, sim_y])

    if not dpg.does_item_exist("real_opt_series"):
        dpg.add_line_series(
            real_x,
            real_y,
            label="Real Slice",
            parent="opt_y_axis",
            tag="real_opt_series",
        )
        dpg.bind_item_theme("real_opt_series", Theme.nmr_plot_theme())
    else:
        dpg.set_value("real_opt_series", [real_x, real_y])
