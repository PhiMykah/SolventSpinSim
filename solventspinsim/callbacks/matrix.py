import dearpygui.dearpygui as dpg
import numpy as np

from .plot import update_simulation_plot, update_plotting_ui, zoom_subplots_to_peaks, fit_axes, COUPLING_DRAG_HEIGHT
from .callbacks import help_msg

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ui import UI
    from spin import Spin

def matrix_table(ui : "UI") -> None:
    with dpg.window(label='Spin Matrix', show=False, tag='matrix_window'):
        
        with dpg.table(header_row=False):
            dpg.add_table_column(width=100)
            dpg.add_table_column(width=100)
            dpg.add_table_column(width=100)

            with dpg.table_row():
                dpg.add_text('Minimum Frequency')
                help_msg("Minimum frequency for the coupling matrix and chemical shift sliders.")

                dpg.add_text('Maximum Frequency')
                help_msg("Maximum frequency for the coupling matrix and chemical shift sliders.")

            with dpg.table_row():
                dpg.add_drag_float(label='##Minimum Frequency', tag='table_min_freq', default_value=-100.0, width=-1)
                dpg.add_drag_float(label='##Maximum Frequency', tag='table_max_freq', default_value=100.0, width=-1)
                dpg.add_button(label='Update Matrix', callback=load_table, user_data=ui)

def load_table(sender, app_data, user_data : "UI") -> None:
    """
    Loads the spin coupling matrix into a DearPyGui table for editing.
    """
    ui : "UI" = user_data

    min_value : float = dpg.get_value('table_min_freq')
    max_value : float = dpg.get_value('table_max_freq')

    if not hasattr(ui, 'spin') or not ui.spin:
        return
    spin : "Spin" = ui.spin

    if hasattr(ui, 'mat_table') and ui.mat_table != "":
        for i,row in enumerate(np.array(spin.couplings)):
            for j, col in enumerate(row):
                if dpg.does_item_exist(f'coupling_{i}_{j}'):
                    dpg.configure_item(f'coupling_{i}_{j}', min_value=min_value, max_value=max_value)
        return

    table_tag = 'matrix_table'

    if not spin.spin_names or not spin.nuclei_frequencies:
        return
    
    if ui.window is None:
        return
    
    with dpg.table(tag=table_tag, header_row=True, row_background=False,
              borders_innerH=True, borders_outerH=True, borders_innerV=True,
              borders_outerV=True, delay_search=True, parent='matrix_window'):
        dpg.add_table_column(label="##Top Left Corner")
        for atom in spin.spin_names:
            dpg.add_table_column(label=str(atom))

        for i, row in enumerate(np.array(spin.couplings)):
            with dpg.table_row():
                dpg.add_text(spin.spin_names[i], tag=f'row_{i}_header')
                for j, col in enumerate(row):
                    default_val = col
                    if i != j:
                        dpg.add_drag_float(label=f'##coupling_{i}_{j}', tag=f'coupling_{i}_{j}', width=-1, 
                                        min_value=min_value, max_value=max_value, default_value=default_val,
                                        user_data=(ui, j, i, ui.spin._nuclei_frequencies[i]), callback=modify_matrix)
                    else:
                        dpg.add_text(f"", label=f'##coupling_{i}_{j}', tag=f'coupling_{i}_{j}')

    ui.mat_table = table_tag

def modify_matrix(sender, app_data, user_data : "tuple[UI, int, int, float]") -> None:
    """
    Modifies the spin coupling matrix value at (j, i) with the new value.
    """
    spin : Spin = user_data[0].spin
    j : int = user_data[1]
    i : int = user_data[2]
    nuclei = user_data[3]
    value = app_data

    spin._couplings[j][i] = value
    dpg.set_value(f'coupling_{j}_{i}', value)

    for tag_type, sign in (('r', 1), ('l', -1)):
        for a, b in ((i, j), (j, i)):
            tag = f'coupling_drag_{tag_type}_{a}_{b}'
            if dpg.does_item_exist(tag):
                dpg.set_value(tag, (nuclei + sign * value, COUPLING_DRAG_HEIGHT))
                break

    f'coupling_drag_l_{i}_{j}'
    spin._couplings[i][j] = value
    update_simulation_plot(spin, user_data[0].points, user_data[0].water_sim, spin.half_height_width,
                           spin._nuclei_number)
    update_plotting_ui(user_data[0])
    zoom_subplots_to_peaks(user_data[0])