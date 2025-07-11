import dearpygui.dearpygui as dpg
from simulate.simulate import simulate_peaklist
from spin.spin import Spin, loadSpinFromFile
from sys import stderr

# ---------------------------------------------------------------------------- #
#                              Callback Functions                              #
# ---------------------------------------------------------------------------- #

def test_callback(sender, app_data, user_data) -> None:
    print(f"sender is: {sender}")
    print(f"app_data is: {app_data}")
    print(f"user_data is: {user_data}")

# Callback to close all windows and the viewport
def close_application(sender, app_data, user_data) -> None:
    dpg.stop_dearpygui()

# Callback to resize viewport and perform other
def viewport_resize_callback(sender, app_data, user_data) -> None:
    current_width = dpg.get_viewport_width()
    current_height = dpg.get_viewport_height()
    print(f"Viewport resized to: Width={current_width}, Height={current_height}")

def set_file_callback(sender, app_data, user_data) -> None:
    """
    Sets the user_data[1] attribute of user_data[0] to the file from app_data,
    Assumes that the function parent has a file_path_name attribute and
    that user_data[0] has attribute user_data[1]
    """
    file = app_data['file_path_name']
    obj = user_data[0]
    attr = user_data[1]

    setattr(obj, attr, file)

def update_plot(sender, app_data, user_data) -> None:
    if not user_data.spin_file:
        print("No file found, skipping update...", file=stderr)
        return 
    nuclei_frequencies, couplings = loadSpinFromFile(user_data.spin_file)
    spin = Spin(nuclei_frequencies, couplings)
    simulation = simulate_peaklist(spin.peaklist(), 1000, spin.half_height_width)
    dpg.set_value('main_plot', [simulation[0], simulation[1]])
    dpg.set_item_label('main_plot', "Updated Plot")
