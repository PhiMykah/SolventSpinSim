import dearpygui.dearpygui as dpg


class Theme:
    _disabled_theme = None
    _sim_plot_theme = None
    _nmr_plot_theme = None
    _region_theme = None

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

    @classmethod
    def sim_plot_theme(cls):
        """
        Load or access the main simulation plot theme

        Assumes that the dpg context has been created.
        """
        if cls._sim_plot_theme is None:
            with dpg.theme() as sim_plot_theme:
                with dpg.theme_component(dpg.mvLineSeries):
                    dpg.add_theme_color(
                        dpg.mvPlotCol_Line,
                        (76, 114, 176),
                        category=dpg.mvThemeCat_Plots,
                    )

            cls._sim_plot_theme = sim_plot_theme
        return cls._sim_plot_theme

    @classmethod
    def nmr_plot_theme(cls):
        """
        Load or access the nmr plot theme

        Assumes that the dpg context has been created.
        """
        if cls._nmr_plot_theme is None:
            with dpg.theme() as nmr_plot_theme:
                with dpg.theme_component(dpg.mvLineSeries):
                    dpg.add_theme_color(
                        dpg.mvPlotCol_Line,
                        (221, 132, 82),
                        category=dpg.mvThemeCat_Plots,
                    )

            cls._nmr_plot_theme = nmr_plot_theme
        return cls._nmr_plot_theme

    @classmethod
    def region_theme(cls):
        """
        Load or access the nmr plot theme

        Assumes that the dpg context has been created.
        """
        if cls._region_theme is None:
            with dpg.theme() as region_theme:
                with dpg.theme_component(dpg.mvLineSeries):
                    dpg.add_theme_color(
                        dpg.mvPlotCol_Line, (255, 0, 0), category=dpg.mvThemeCat_Plots
                    )
                with dpg.theme_component(dpg.mvInfLineSeries):
                    dpg.add_theme_color(
                        dpg.mvPlotCol_Line, (255, 0, 0), category=dpg.mvThemeCat_Plots
                    )

            cls._region_theme = region_theme
        return cls._region_theme
