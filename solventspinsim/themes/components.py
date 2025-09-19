import dearpygui.dearpygui as dpg

from .types import ThemeDict
from .styles import button_style


def main_theme_components(theme: ThemeDict) -> None:
    # ----------------------------------- Text ----------------------------------- #
    """
    Modify the appearance of standard text
    """

    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(  # Text Color
            dpg.mvThemeCol_Text,
            theme["BASE_CONTENT"],
            category=dpg.mvThemeCat_Core,
        )

        dpg.add_theme_color(  # Disabled Text Color
            dpg.mvThemeCol_TextDisabled,
            theme["NEUTRAL"],
            category=dpg.mvThemeCat_Core,
        )

        # dpg.add_theme_color(  # Selected Text Background Color
        #     dpg.mvThemeCol_TextSelectedBg,
        #     theme["ACCENT"],
        #     category=dpg.mvThemeCat_Core,
        # )

    # ---------------------------------- Window ---------------------------------- #
    """
    Modify the window background and surrounding elements
    """

    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(  # Window Background Color
            dpg.mvThemeCol_WindowBg,
            theme["BASE200"],
            category=dpg.mvThemeCat_Core,
        )

        dpg.add_theme_color(  # Child Window Background Color
            dpg.mvThemeCol_ChildBg,
            theme["BASE200"],
            category=dpg.mvThemeCat_Core,
        )

        dpg.add_theme_color(  # Window Border Color
            dpg.mvThemeCol_Border,
            theme["BASE50"],
            category=dpg.mvThemeCat_Core,
        )

        dpg.add_theme_color(  # Window Border Shadow Color
            dpg.mvThemeCol_BorderShadow,
            theme["NEUTRAL"] + (100,),
            category=dpg.mvThemeCat_Core,
        )

    # ----------------------------------- Frame ---------------------------------- #
    """
    Modify the Frame encapulating interactable content
    """
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(  # Frame Background Color
            dpg.mvThemeCol_FrameBg,
            theme["BASE100"],
            category=dpg.mvThemeCat_Core,
        )

        dpg.add_theme_color(  # Frame Background Hovered Color
            dpg.mvThemeCol_FrameBgHovered,
            theme["BASE50"],
            category=dpg.mvThemeCat_Core,
        )

        dpg.add_theme_color(  # Active Frame Background Color
            dpg.mvThemeCol_FrameBgActive,
            theme["BASE50"],
            category=dpg.mvThemeCat_Core,
        )

    # ----------------------------------- Title ---------------------------------- #
    """
    Modify the title bar region of floating windows
    """
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(  # Title Background Color
            dpg.mvThemeCol_TitleBg,
            theme["BASE100"],
            category=dpg.mvThemeCat_Core,
        )

        dpg.add_theme_color(  # Active Title Background Color
            dpg.mvThemeCol_TitleBgActive,
            theme["PRIMARY"],
            category=dpg.mvThemeCat_Core,
        )

        dpg.add_theme_color(  # Collapsed Title Background Color
            dpg.mvThemeCol_TitleBgCollapsed,
            theme["PRIMARY"],
            category=dpg.mvThemeCat_Core,
        )

    # ----------------------------------- Menu ----------------------------------- #
    """
    Modify menu bar and menu elements
    """
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(  # Menu Bar Background Color
            dpg.mvThemeCol_MenuBarBg,
            theme["BASE100"],
            category=dpg.mvThemeCat_Core,
        )

        # Menu Elements

        dpg.add_theme_color(  # Selected Header Color
            dpg.mvThemeCol_Header,
            theme["PRIMARY"],
            category=dpg.mvThemeCat_Core,
        )

        dpg.add_theme_color(  # Header Hovered Color
            dpg.mvThemeCol_HeaderHovered,
            theme["BASE50"],
            category=dpg.mvThemeCat_Core,
        )

        dpg.add_theme_color(  # Active Header Color
            dpg.mvThemeCol_HeaderActive,
            theme["ACCENT"],
            category=dpg.mvThemeCat_Core,
        )

    # ----------------------------------- Table ---------------------------------- #
    """
    Modify table UI and elements
    """
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(  # Table Header Background Color
            dpg.mvThemeCol_TableHeaderBg,
            theme["PRIMARY"],
            category=dpg.mvThemeCat_Core,
        )

        dpg.add_theme_color(  # Light Table Border Color
            dpg.mvThemeCol_TableBorderLight,
            theme["BASE100"],
            category=dpg.mvThemeCat_Core,
        )

        dpg.add_theme_color(  # Strong Table Border Color
            dpg.mvThemeCol_TableBorderStrong,
            theme["BASE50"],
            category=dpg.mvThemeCat_Core,
        )

        dpg.add_theme_color(  # Table Row Background Color
            dpg.mvThemeCol_TableRowBg,
            theme["BASE100"],
            category=dpg.mvThemeCat_Core,
        )

        dpg.add_theme_color(  # Table Row Alternate Color
            dpg.mvThemeCol_TableRowBgAlt,
            theme["BASE75"],
            category=dpg.mvThemeCat_Core,
        )

    # --------------------------------- Separator -------------------------------- #
    """
    Modify section separator object
    """
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(  # Separator Color
            dpg.mvThemeCol_Separator,
            theme["BASE_CONTENT"],
            category=dpg.mvThemeCat_Core,
        )

        dpg.add_theme_color(  # Separator Hovered Color
            dpg.mvThemeCol_SeparatorHovered,
            theme["ACCENT"],
            category=dpg.mvThemeCat_Core,
        )

        dpg.add_theme_color(  # Active Separator Color
            dpg.mvThemeCol_SeparatorActive,
            theme["SECONDARY"],
            category=dpg.mvThemeCat_Core,
        )

    # ---------------------------------- Button ---------------------------------- #
    """
    Modify the button objects in windows
    """
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(  # Default Button Color
            dpg.mvThemeCol_Button,
            theme["PRIMARY"],
            category=dpg.mvThemeCat_Core,
        )

        dpg.add_theme_color(  # Hovered Button Color
            dpg.mvThemeCol_ButtonHovered,
            theme["ACCENT"],
            category=dpg.mvThemeCat_Core,
        )

        dpg.add_theme_color(  # Active Button Color
            dpg.mvThemeCol_ButtonActive,
            theme["SUCCESS"],
            category=dpg.mvThemeCat_Core,
        )
        # Checkmark

        dpg.add_theme_color(  # Checkmark Color
            dpg.mvThemeCol_CheckMark,
            theme["BASE_CONTENT"],
            category=dpg.mvThemeCat_Core,
        )

    with dpg.theme_component(dpg.mvButton):
        dpg.add_theme_color(
            dpg.mvThemeCol_Text,
            theme["PRIMARY_CONTENT"],
        )

    with dpg.theme_component(dpg.mvButton):
        button_style()

    # ------------------------------------ Tab ----------------------------------- #
    """
    Modify the tab container components
    """
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(  # Active Tab Color
            dpg.mvThemeCol_TabActive,
            theme["PRIMARY"],
            category=dpg.mvThemeCat_Core,
        )

        dpg.add_theme_color(  # Unfocused Tab Color
            dpg.mvThemeCol_TabUnfocused,
            theme["BASE200"],
            category=dpg.mvThemeCat_Core,
        )

        dpg.add_theme_color(  # Active Unfocused Tab Color
            dpg.mvThemeCol_TabUnfocusedActive,
            theme["BASE50"],
            category=dpg.mvThemeCat_Core,
        )

        dpg.add_theme_color(  # Tab Color
            dpg.mvThemeCol_Tab,
            theme["BASE100"],
            category=dpg.mvThemeCat_Core,
        )

        dpg.add_theme_color(  # Hovered Tab Color
            dpg.mvThemeCol_TabHovered,
            theme["ACCENT"],
            category=dpg.mvThemeCat_Core,
        )

    # ---------------------------------- Slider ---------------------------------- #
    """
    Modify the 2D/3D Slider objects
    """
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(  # Active Slider Grab Color
            dpg.mvThemeCol_SliderGrabActive,
            theme["ACCENT"],
            category=dpg.mvThemeCat_Core,
        )

        dpg.add_theme_color(  # Slider Grab Color
            dpg.mvThemeCol_SliderGrab,
            theme["PRIMARY"],
            category=dpg.mvThemeCat_Core,
        )

    # ---------------------------------- Resize ---------------------------------- #
    """
    Modify the Resize grip object at the corner of moveable windows
    """
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(  # Resize Grip Color
            dpg.mvThemeCol_ResizeGrip,
            theme["PRIMARY"],
            category=dpg.mvThemeCat_Core,
        )

        dpg.add_theme_color(  # Resize Grip Hovered Color
            dpg.mvThemeCol_ResizeGripHovered,
            theme["ACCENT"],
            category=dpg.mvThemeCat_Core,
        )

        dpg.add_theme_color(  # Active Resize Grip Color
            dpg.mvThemeCol_ResizeGripActive,
            theme["ACCENT"],
            category=dpg.mvThemeCat_Core,
        )

    # --------------------------------- Scrollbar -------------------------------- #
    """
    Modify the scrollbar object for scrolling on large windows
    """
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(  # Scrollbar Background Color
            dpg.mvThemeCol_ScrollbarBg,
            theme["BASE300"],
            category=dpg.mvThemeCat_Core,
        )

        dpg.add_theme_color(  # Scrollbar Grab Color
            dpg.mvThemeCol_ScrollbarGrab,
            theme["BASE200"],
            category=dpg.mvThemeCat_Core,
        )

        dpg.add_theme_color(  # Hovered Scrollbar Grab Color
            dpg.mvThemeCol_ScrollbarGrabHovered,
            theme["BASE100"],
            category=dpg.mvThemeCat_Core,
        )

        dpg.add_theme_color(  # Active Scrollbar Grab Color
            dpg.mvThemeCol_ScrollbarGrabActive,
            theme["BASE100"],
            category=dpg.mvThemeCat_Core,
        )

    # ------------------------------- Drag 'n' Drop ------------------------------ #
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(  # Drag and Drop Target/Receipient Color
            dpg.mvThemeCol_DragDropTarget,
            theme["ACCENT"],
            category=dpg.mvThemeCat_Core,
        )

    # ---------------------------------- Docking --------------------------------- #
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(  # Docking Preview Color
            dpg.mvThemeCol_DockingPreview,
            theme["ACCENT"],
            category=dpg.mvThemeCat_Core,
        )

        dpg.add_theme_color(  # Docking Empty Background Color
            dpg.mvThemeCol_DockingEmptyBg,
            theme["BASE200"],
            category=dpg.mvThemeCat_Core,
        )

    # -------------------------------- Popup/Modal ------------------------------- #
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(  # Pop-up Background Color
            dpg.mvThemeCol_PopupBg,
            theme["BASE200"],
            category=dpg.mvThemeCat_Core,
        )

        dpg.add_theme_color(  # Modal Window Background Dim Color
            dpg.mvThemeCol_ModalWindowDimBg,
            theme["NEUTRAL"] + (125,),
            category=dpg.mvThemeCat_Core,
        )

    # -------------------------------- Navigation -------------------------------- #
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(  # Navigation Highlight Color
            dpg.mvThemeCol_NavHighlight,
            theme["PRIMARY"],
            category=dpg.mvThemeCat_Core,
        )

        dpg.add_theme_color(  # Navigation Window Highlight Color
            dpg.mvThemeCol_NavWindowingHighlight,
            theme["ACCENT"],
            category=dpg.mvThemeCat_Core,
        )

        dpg.add_theme_color(  # Navigation Window Dimming Color
            dpg.mvThemeCol_NavWindowingDimBg,
            theme["BASE300"],
            category=dpg.mvThemeCat_Core,
        )

    # ----------------------------------- Plot ----------------------------------- #
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(  # Plot Lines Color
            dpg.mvThemeCol_PlotLines,
            theme["PRIMARY"],
            category=dpg.mvThemeCat_Core,
        )

        dpg.add_theme_color(  # Plot Lines Hovered Color
            dpg.mvThemeCol_PlotLinesHovered,
            theme["ACCENT"],
            category=dpg.mvThemeCat_Core,
        )

        dpg.add_theme_color(  # Histogram Plot Color
            dpg.mvThemeCol_PlotHistogram,
            theme["PRIMARY"],
            category=dpg.mvThemeCat_Core,
        )

        dpg.add_theme_color(  # Histogram Plot Hovered Color
            dpg.mvThemeCol_PlotHistogramHovered,
            theme["ACCENT"],
            category=dpg.mvThemeCat_Core,
        )

    with dpg.theme_component(dpg.mvPlot):
        dpg.add_theme_color(  # Plot's Background Color
            dpg.mvThemeCol_WindowBg,
            theme["BASE100"],
            category=dpg.mvThemeCat_Core,
        )
