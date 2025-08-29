# ---------------------------------------------------------------------------- #
#                                    Configs                                   #
# ---------------------------------------------------------------------------- #
# Configurations for windows and components in the user interface

# ---------------------------------- Default --------------------------------- #
default: dict = {
    "width": 0,  # Width of the item.
    "height": 0,  # Height of the item.
    "indent": -1,  # Offsets the widget to the right the specified number multiplied by the indent style.
    "show": True,  #  Attempt to render widget.
    "pos": [],  # Places the item relative to window coordinates, [0,0] is top left.
    "delay_search": False,  # Delays searching container for specified items until the end of the app.
    "min_size": (100, 100),  # Minimum window size.
    "max_size": (30000, 30000),  # Maximum window size.
    "menubar": False,  # Shows or hides the menubar.
    "collapsed": False,  # Collapse the window.
    "autosize": False,  # Autosized the window to fit it’s items.
    "no_resize": False,  # Allows for the window size to be changed or fixed.
    "unsaved_document": False,  # Show a special marker if the document is not saved.
    "no_title_bar": False,  # Title name for the title bar of the window.
    "no_move": False,  # Allows for the window’s position to be changed or fixed.
    "no_scrollbar": False,  # Disable scrollbars
    "no_collapse": False,  # Disable user collapsing window by double-clicking on it.
    "horizontal_scrollbar": False,  # Allow horizontal scrollbar to appear.
    "no_focus_on_appearing": False,  # Disable taking focus when transitioning from hidden to visible state.
    "no_bring_to_front_on_focus": False,  # Disable bringing window to front when taking focus.
    "no_close": False,  # Disable user closing the window by removing the close button.
    "no_background": False,  # Sets Background and border alpha to transparent.
    "modal": False,  # Fills area behind window according to the theme and disables user ability to interact with anything except the window.
    "popup": False,  # Fills area behind window according to the theme, removes title bar, collapse and close. Window can be closed by selecting
    "no_saved_settings": False,  # Never load/save settings in .ini file.
    "no_open_over_existing_popup": True,  # Don’t open if there’s already a popup
    "no_scroll_with_mouse": False,  # Disable user vertically scrolling with mouse wheel.
    "on_close": None,  # Callback ran when window is closed.
}
