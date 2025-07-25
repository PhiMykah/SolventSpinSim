import dearpygui.dearpygui as dpg
import numpy as np

from .plot import update_simulation_plot, COUPLING_DRAG_HEIGHT

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ui.ui import UI
    from spin.spin import Spin

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

    if hasattr(ui, 'mat_table') and ui.mat_table is not None:
        for i,row in enumerate(np.array(spin.couplings)):
            for j, col in enumerate(row):
                dpg.configure_item(f'coupling_{i}_{j}', min_value=min_value, max_value=max_value)
        return

    table_tag = 'matrix_table'

    if not spin.spin_names or not spin.nuclei_frequencies:
        return
    
    if ui.window is None:
        return
    
    with dpg.table(tag=table_tag, header_row=True, row_background=False,
              borders_innerH=True, borders_outerH=True, borders_innerV=True,
              borders_outerV=True, delay_search=True, parent=ui.window):
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
    update_simulation_plot(spin, user_data[0].points, spin.half_height_width,
                           spin._nuclei_number)