import dearpygui.dearpygui as dpg

DARK: dict[str, tuple[int, int, int]] = {
    "BASE100": (29, 35, 42),  # 1d232a
    "BASE200": (25, 30, 36),  # 191e24
    "BASE300": (21, 25, 30),  # 15191e
    "BASE75": (36, 42, 49),  # 242a31
    "BASE50": (44, 50, 65),  # 2c3241
    "BASE_DISABLED": (122, 139, 160),  # 7a8ba0
    "BASE_CONTENT": (236, 249, 255),  # ecf9ff
    "PRIMARY": (96, 93, 255),  # 605dff
    "PRIMARY_CONTENT": (237, 241, 254),  # edf1fe
    "SECONDARY": (244, 48, 152),  # f43098
    "SECONDARY_CONTENT": (249, 228, 240),  # f9e4f0
    "ACCENT": (0, 211, 187),  # 00d3bb
    "ACCENT_CONTENT": (8, 77, 73),  # 084d49
    "NEUTRAL": (9, 9, 11),  # 09090b
    "NEUTRAL_CONTENT": (228, 228, 231),  # e4e4e7
    "INFO": (0, 186, 254),  # 00bafe
    "INFO_CONTENT": (4, 46, 73),  # 042e49
    "SUCCESS": (0, 211, 144),  # 00d390
    "SUCCESS_CONTENT": (0, 76, 57),  # 004c39
    "WARNING": (252, 183, 0),  # fcb700
    "WARNING_CONTENT": (121, 50, 5),  # 793205
    "ERROR": (255, 98, 125),  # ff627d
    "ERROR_CONTENT": (77, 2, 24),  # 4d0218
}

LIGHT: dict[str, tuple[int, int, int]] = {
    "BASE100": (255, 255, 255),  # ffffff
    "BASE200": (248, 248, 248),  # f8f8f8
    "BASE300": (238, 238, 238),  # eeeeee
    "BASE75": (242, 242, 242),  # f2f2f2
    "BASE50": (245, 245, 244),  # f5f5f4
    "BASE_DISABLED": (158, 158, 158),  # 9e9e9e
    "BASE_CONTENT": (24, 24, 27),  # 18181b
    "PRIMARY": (66, 42, 213),  # 422ad5
    "PRIMARY_CONTENT": (224, 231, 255),  # e0e7ff
    "SECONDARY": (244, 48, 152),  # f43098
    "SECONDARY_CONTENT": (249, 228, 240),  # f9e4f0
    "ACCENT": (0, 211, 187),  # 00d3bb
    "ACCENT_CONTENT": (8, 77, 73),  # 084d49
    "NEUTRAL": (9, 9, 11),  # 09090b
    "NEUTRAL_CONTENT": (228, 228, 231),  # e4e4e7
    "INFO": (0, 186, 254),  # 00bafe
    "INFO_CONTENT": (4, 46, 73),  # 042e49
    "SUCCESS": (0, 211, 144),  # 00d390
    "SUCCESS_CONTENT": (0, 76, 57),  # 004c39
    "WARNING": (252, 183, 0),  # fcb700
    "WARNING_CONTENT": (121, 50, 5),  # 793205
    "ERROR": (255, 98, 125),  # ff627d
    "ERROR_CONTENT": (77, 2, 24),  # 4d0218
}

MAIN_THEME_TYPES = {"dark": DARK, "light": LIGHT}


class Theme:
    _main_themes = {}
    _disabled_theme = None
    _sim_plot_theme = None
    _nmr_plot_theme = None
    _region_theme = None
    _current_main_theme = "dark"

    @classmethod
    def main_themes(cls, theme_type: "str" = "dark"):
        """
        Loads the main theme or accesses the main theme

        Assumes that the dpg context has been created.
        """
        if not cls._main_themes:
            for theme_name, thm in MAIN_THEME_TYPES.items():
                with dpg.theme() as main_theme:
                    # ----------------------------------- Text ----------------------------------- #
                    """
                    Modify the appearance of standard text
                    """

                    with dpg.theme_component(dpg.mvAll):
                        dpg.add_theme_color(  # Text Color
                            dpg.mvThemeCol_Text,
                            thm["BASE_CONTENT"],
                            category=dpg.mvThemeCat_Core,
                        )

                        dpg.add_theme_color(  # Disabled Text Color
                            dpg.mvThemeCol_TextDisabled,
                            thm["NEUTRAL"],
                            category=dpg.mvThemeCat_Core,
                        )

                        # dpg.add_theme_color(  # Selected Text Background Color
                        #     dpg.mvThemeCol_TextSelectedBg,
                        #     thm["ACCENT"],
                        #     category=dpg.mvThemeCat_Core,
                        # )

                    # ---------------------------------- Window ---------------------------------- #
                    """
                    Modify the window background and surrounding elements
                    """

                    with dpg.theme_component(dpg.mvAll):
                        dpg.add_theme_color(  # Window Background Color
                            dpg.mvThemeCol_WindowBg,
                            thm["BASE200"],
                            category=dpg.mvThemeCat_Core,
                        )

                        dpg.add_theme_color(  # Child Window Background Color
                            dpg.mvThemeCol_ChildBg,
                            thm["BASE200"],
                            category=dpg.mvThemeCat_Core,
                        )

                        dpg.add_theme_color(  # Window Border Color
                            dpg.mvThemeCol_Border,
                            thm["BASE50"],
                            category=dpg.mvThemeCat_Core,
                        )

                        dpg.add_theme_color(  # Window Border Shadow Color
                            dpg.mvThemeCol_BorderShadow,
                            thm["NEUTRAL"] + (100,),
                            category=dpg.mvThemeCat_Core,
                        )

                    # ----------------------------------- Frame ---------------------------------- #
                    """
                    Modify the Frame encapulating interactable content
                    """
                    with dpg.theme_component(dpg.mvAll):
                        dpg.add_theme_color(  # Frame Background Color
                            dpg.mvThemeCol_FrameBg,
                            thm["BASE100"],
                            category=dpg.mvThemeCat_Core,
                        )

                        dpg.add_theme_color(  # Frame Background Hovered Color
                            dpg.mvThemeCol_FrameBgHovered,
                            thm["BASE50"],
                            category=dpg.mvThemeCat_Core,
                        )

                        dpg.add_theme_color(  # Active Frame Background Color
                            dpg.mvThemeCol_FrameBgActive,
                            thm["BASE50"],
                            category=dpg.mvThemeCat_Core,
                        )

                    # ----------------------------------- Title ---------------------------------- #
                    """
                    Modify the title bar region of floating windows
                    """
                    with dpg.theme_component(dpg.mvAll):
                        dpg.add_theme_color(  # Title Background Color
                            dpg.mvThemeCol_TitleBg,
                            thm["BASE100"],
                            category=dpg.mvThemeCat_Core,
                        )

                        dpg.add_theme_color(  # Active Title Background Color
                            dpg.mvThemeCol_TitleBgActive,
                            thm["PRIMARY"],
                            category=dpg.mvThemeCat_Core,
                        )

                        dpg.add_theme_color(  # Collapsed Title Background Color
                            dpg.mvThemeCol_TitleBgCollapsed,
                            thm["PRIMARY"],
                            category=dpg.mvThemeCat_Core,
                        )

                    # ----------------------------------- Menu ----------------------------------- #
                    """
                    Modify menu bar and menu elements
                    """
                    with dpg.theme_component(dpg.mvAll):
                        dpg.add_theme_color(  # Menu Bar Background Color
                            dpg.mvThemeCol_MenuBarBg,
                            thm["BASE100"],
                            category=dpg.mvThemeCat_Core,
                        )

                        # Menu Elements

                        dpg.add_theme_color(  # Selected Header Color
                            dpg.mvThemeCol_Header,
                            thm["PRIMARY"],
                            category=dpg.mvThemeCat_Core,
                        )

                        dpg.add_theme_color(  # Header Hovered Color
                            dpg.mvThemeCol_HeaderHovered,
                            thm["BASE50"],
                            category=dpg.mvThemeCat_Core,
                        )

                        dpg.add_theme_color(  # Active Header Color
                            dpg.mvThemeCol_HeaderActive,
                            thm["ACCENT"],
                            category=dpg.mvThemeCat_Core,
                        )

                    # ----------------------------------- Table ---------------------------------- #
                    """
                    Modify table UI and elements
                    """
                    with dpg.theme_component(dpg.mvAll):
                        dpg.add_theme_color(  # Table Header Background Color
                            dpg.mvThemeCol_TableHeaderBg,
                            thm["PRIMARY"],
                            category=dpg.mvThemeCat_Core,
                        )

                        dpg.add_theme_color(  # Light Table Border Color
                            dpg.mvThemeCol_TableBorderLight,
                            thm["BASE100"],
                            category=dpg.mvThemeCat_Core,
                        )

                        dpg.add_theme_color(  # Strong Table Border Color
                            dpg.mvThemeCol_TableBorderStrong,
                            thm["BASE50"],
                            category=dpg.mvThemeCat_Core,
                        )

                        dpg.add_theme_color(  # Table Row Background Color
                            dpg.mvThemeCol_TableRowBg,
                            thm["BASE100"],
                            category=dpg.mvThemeCat_Core,
                        )

                        dpg.add_theme_color(  # Table Row Alternate Color
                            dpg.mvThemeCol_TableRowBgAlt,
                            thm["BASE75"],
                            category=dpg.mvThemeCat_Core,
                        )

                    # --------------------------------- Separator -------------------------------- #
                    """
                    Modify section separator object
                    """
                    with dpg.theme_component(dpg.mvAll):
                        dpg.add_theme_color(  # Separator Color
                            dpg.mvThemeCol_Separator,
                            thm["BASE_CONTENT"],
                            category=dpg.mvThemeCat_Core,
                        )

                        dpg.add_theme_color(  # Separator Hovered Color
                            dpg.mvThemeCol_SeparatorHovered,
                            thm["ACCENT"],
                            category=dpg.mvThemeCat_Core,
                        )

                        dpg.add_theme_color(  # Active Separator Color
                            dpg.mvThemeCol_SeparatorActive,
                            thm["SECONDARY"],
                            category=dpg.mvThemeCat_Core,
                        )

                    # ---------------------------------- Button ---------------------------------- #
                    """
                    Modify the button objects in windows
                    """
                    with dpg.theme_component(dpg.mvAll):
                        dpg.add_theme_color(  # Default Button Color
                            dpg.mvThemeCol_Button,
                            thm["PRIMARY"],
                            category=dpg.mvThemeCat_Core,
                        )

                        dpg.add_theme_color(  # Hovered Button Color
                            dpg.mvThemeCol_ButtonHovered,
                            thm["ACCENT"],
                            category=dpg.mvThemeCat_Core,
                        )

                        dpg.add_theme_color(  # Active Button Color
                            dpg.mvThemeCol_ButtonActive,
                            thm["SUCCESS"],
                            category=dpg.mvThemeCat_Core,
                        )
                        # Checkmark

                        dpg.add_theme_color(  # Checkmark Color
                            dpg.mvThemeCol_CheckMark,
                            thm["BASE_CONTENT"],
                            category=dpg.mvThemeCat_Core,
                        )

                    with dpg.theme_component(dpg.mvButton):
                        dpg.add_theme_color(
                            dpg.mvThemeCol_Text,
                            thm["PRIMARY_CONTENT"],
                        )

                    # ------------------------------------ Tab ----------------------------------- #
                    """
                    Modify the tab container components
                    """
                    with dpg.theme_component(dpg.mvAll):
                        dpg.add_theme_color(  # Active Tab Color
                            dpg.mvThemeCol_TabActive,
                            thm["PRIMARY"],
                            category=dpg.mvThemeCat_Core,
                        )

                        dpg.add_theme_color(  # Unfocused Tab Color
                            dpg.mvThemeCol_TabUnfocused,
                            thm["BASE200"],
                            category=dpg.mvThemeCat_Core,
                        )

                        dpg.add_theme_color(  # Active Unfocused Tab Color
                            dpg.mvThemeCol_TabUnfocusedActive,
                            thm["BASE50"],
                            category=dpg.mvThemeCat_Core,
                        )

                        dpg.add_theme_color(  # Tab Color
                            dpg.mvThemeCol_Tab,
                            thm["BASE100"],
                            category=dpg.mvThemeCat_Core,
                        )

                        dpg.add_theme_color(  # Hovered Tab Color
                            dpg.mvThemeCol_TabHovered,
                            thm["ACCENT"],
                            category=dpg.mvThemeCat_Core,
                        )

                    # ---------------------------------- Slider ---------------------------------- #
                    """
                    Modify the 2D/3D Slider objects
                    """
                    with dpg.theme_component(dpg.mvAll):
                        dpg.add_theme_color(  # Active Slider Grab Color
                            dpg.mvThemeCol_SliderGrabActive,
                            thm["ACCENT"],
                            category=dpg.mvThemeCat_Core,
                        )

                        dpg.add_theme_color(  # Slider Grab Color
                            dpg.mvThemeCol_SliderGrab,
                            thm["PRIMARY"],
                            category=dpg.mvThemeCat_Core,
                        )

                    # ---------------------------------- Resize ---------------------------------- #
                    """
                    Modify the Resize grip object at the corner of moveable windows
                    """
                    with dpg.theme_component(dpg.mvAll):
                        dpg.add_theme_color(  # Resize Grip Color
                            dpg.mvThemeCol_ResizeGrip,
                            thm["PRIMARY"],
                            category=dpg.mvThemeCat_Core,
                        )

                        dpg.add_theme_color(  # Resize Grip Hovered Color
                            dpg.mvThemeCol_ResizeGripHovered,
                            thm["ACCENT"],
                            category=dpg.mvThemeCat_Core,
                        )

                        dpg.add_theme_color(  # Active Resize Grip Color
                            dpg.mvThemeCol_ResizeGripActive,
                            thm["ACCENT"],
                            category=dpg.mvThemeCat_Core,
                        )

                    # --------------------------------- Scrollbar -------------------------------- #
                    """
                    Modify the scrollbar object for scrolling on large windows
                    """
                    with dpg.theme_component(dpg.mvAll):
                        dpg.add_theme_color(  # Scrollbar Background Color
                            dpg.mvThemeCol_ScrollbarBg,
                            thm["BASE300"],
                            category=dpg.mvThemeCat_Core,
                        )

                        dpg.add_theme_color(  # Scrollbar Grab Color
                            dpg.mvThemeCol_ScrollbarGrab,
                            thm["BASE200"],
                            category=dpg.mvThemeCat_Core,
                        )

                        dpg.add_theme_color(  # Hovered Scrollbar Grab Color
                            dpg.mvThemeCol_ScrollbarGrabHovered,
                            thm["BASE100"],
                            category=dpg.mvThemeCat_Core,
                        )

                        dpg.add_theme_color(  # Active Scrollbar Grab Color
                            dpg.mvThemeCol_ScrollbarGrabActive,
                            thm["BASE100"],
                            category=dpg.mvThemeCat_Core,
                        )

                    # ------------------------------- Drag 'n' Drop ------------------------------ #
                    with dpg.theme_component(dpg.mvAll):
                        dpg.add_theme_color(  # Drag and Drop Target/Receipient Color
                            dpg.mvThemeCol_DragDropTarget,
                            thm["ACCENT"],
                            category=dpg.mvThemeCat_Core,
                        )

                    # ---------------------------------- Docking --------------------------------- #
                    with dpg.theme_component(dpg.mvAll):
                        dpg.add_theme_color(  # Docking Preview Color
                            dpg.mvThemeCol_DockingPreview,
                            thm["ACCENT"],
                            category=dpg.mvThemeCat_Core,
                        )

                        dpg.add_theme_color(  # Docking Empty Background Color
                            dpg.mvThemeCol_DockingEmptyBg,
                            thm["BASE200"],
                            category=dpg.mvThemeCat_Core,
                        )

                    # -------------------------------- Popup/Modal ------------------------------- #
                    with dpg.theme_component(dpg.mvAll):
                        dpg.add_theme_color(  # Pop-up Background Color
                            dpg.mvThemeCol_PopupBg,
                            thm["BASE200"],
                            category=dpg.mvThemeCat_Core,
                        )

                        dpg.add_theme_color(  # Modal Window Background Dim Color
                            dpg.mvThemeCol_ModalWindowDimBg,
                            thm["NEUTRAL"] + (125,),
                            category=dpg.mvThemeCat_Core,
                        )

                    # -------------------------------- Navigation -------------------------------- #
                    with dpg.theme_component(dpg.mvAll):
                        dpg.add_theme_color(  # Navigation Highlight Color
                            dpg.mvThemeCol_NavHighlight,
                            thm["PRIMARY"],
                            category=dpg.mvThemeCat_Core,
                        )

                        dpg.add_theme_color(  # Navigation Window Highlight Color
                            dpg.mvThemeCol_NavWindowingHighlight,
                            thm["ACCENT"],
                            category=dpg.mvThemeCat_Core,
                        )

                        dpg.add_theme_color(  # Navigation Window Dimming Color
                            dpg.mvThemeCol_NavWindowingDimBg,
                            thm["BASE300"],
                            category=dpg.mvThemeCat_Core,
                        )

                    # ----------------------------------- Plot ----------------------------------- #
                    with dpg.theme_component(dpg.mvAll):
                        dpg.add_theme_color(  # Plot Lines Color
                            dpg.mvThemeCol_PlotLines,
                            thm["PRIMARY"],
                            category=dpg.mvThemeCat_Core,
                        )

                        dpg.add_theme_color(  # Plot Lines Hovered Color
                            dpg.mvThemeCol_PlotLinesHovered,
                            thm["ACCENT"],
                            category=dpg.mvThemeCat_Core,
                        )

                        dpg.add_theme_color(  # Histogram Plot Color
                            dpg.mvThemeCol_PlotHistogram,
                            thm["PRIMARY"],
                            category=dpg.mvThemeCat_Core,
                        )

                        dpg.add_theme_color(  # Histogram Plot Hovered Color
                            dpg.mvThemeCol_PlotHistogramHovered,
                            thm["ACCENT"],
                            category=dpg.mvThemeCat_Core,
                        )

                cls._main_themes[theme_name] = main_theme
        cls._current_main_theme = theme_type.lower()
        return cls._main_themes[theme_type.lower()]

    @classmethod
    def disabled_theme(cls):
        """
        Loads the disable theme or accesses the disabled theme

        Assumes that the dpg context has been created.
        """
        if cls._disabled_theme is None:
            with dpg.theme() as disabled_theme:
                with dpg.theme_component(dpg.mvButton, enabled_state=False):
                    dpg.add_theme_color(
                        dpg.mvThemeCol_Text,
                        MAIN_THEME_TYPES[cls._current_main_theme]["BASE50"],
                    )
                    dpg.add_theme_color(
                        dpg.mvThemeCol_Button,
                        MAIN_THEME_TYPES[cls._current_main_theme]["BASE_DISABLED"],
                    )
                    dpg.add_theme_color(
                        dpg.mvThemeCol_ButtonHovered,
                        MAIN_THEME_TYPES[cls._current_main_theme]["BASE_DISABLED"],
                    )
                    dpg.add_theme_color(
                        dpg.mvThemeCol_ButtonActive,
                        MAIN_THEME_TYPES[cls._current_main_theme]["BASE_DISABLED"],
                    )
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


def change_theme_callback(sender, app_data: str, user_data) -> None:
    dpg.bind_theme(Theme.main_themes(app_data.lower()))
