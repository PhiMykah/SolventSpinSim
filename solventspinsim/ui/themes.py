import dearpygui.dearpygui as dpg

class Theme:
    _disabled_theme = None

    @classmethod
    def disabled_theme(cls):
        """
        Loads the disable theme or accesses the disabled theme

        Assumes that the dpg context has been created.
        """
        if cls._disabled_theme is None:
            with dpg.theme() as disabled_theme:
                with dpg.theme_component(dpg.mvButton, enabled_state=False):
                    dpg.add_theme_color(dpg.mvThemeCol_Text, [128, 128, 128])
                    dpg.add_theme_color(dpg.mvThemeCol_Button, [165, 178, 194])
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [165, 178, 194])
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [165, 178, 194])
            cls._disabled_theme = disabled_theme
        return cls._disabled_theme