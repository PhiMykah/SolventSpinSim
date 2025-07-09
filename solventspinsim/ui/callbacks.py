import dearpygui.dearpygui as dpg

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
