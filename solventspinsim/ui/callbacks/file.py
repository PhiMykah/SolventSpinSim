from sys import stderr

from spin.spin import Spin, loadSpinFromFile
from .plot import add_subplots, update_plot_callback, set_nmr_plot_values, zoom_subplots_to_peaks
from .nmr import load_nmr_array

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ui.ui import UI

def set_spin_file(sender, app_data : dict, user_data : "UI") -> None:
    """
    Sets the spin file of a UI object to the selected file path.
    Additionally trigger plot update and set spin value.
    Optionally triggers a plot update.
    """
    file : str = app_data['file_path_name']
    ui : "UI" = user_data

    if not file:
        print("No file found, skipping update...", file=stderr)
        return 

    ui.spin_file = file
    
    spin_names, nuclei_frequencies, couplings = loadSpinFromFile(ui.spin_file)
    spin = Spin(spin_names, nuclei_frequencies, couplings)
    ui.spin = spin

    add_subplots(ui)
    zoom_subplots_to_peaks(ui)
    update_plot_callback(sender, app_data, ui)

def set_nmr_file_callback(sender, app_data, user_data : "tuple[UI, str, bool]") -> None:
    """
    Sets the NMR file attribute and optionally updates the NMR plot.
    """
    file = app_data['file_path_name']
    ui = user_data[0]
    attr = user_data[1]

    setattr(ui, attr, file)


    field_strength : float = getattr(user_data[0], 'field_strength', 500.0)
    nmr_array = load_nmr_array(file, field_strength)
    ui.points = len(nmr_array[0])
    if user_data[2]:
        set_nmr_plot_values(nmr_array)