import dearpygui.dearpygui as dpg

from .components import main_theme_components
from .dark import DARK
from .disabled import disabled_theme_components
from .hover import hover_theme_components
from .light import LIGHT
from .plot import nmr_theme_components, region_theme_components, sim_theme_components
from .types import ThemeDict


class Theme:
    _theme_collection: dict[str, ThemeDict] = {"dark": DARK, "light": LIGHT}
    _main_themes: dict[str, str | int] = {}
    _hover_theme: dict[str, str | int] = {}
    _disabled_theme: dict[str, str | int] = {}
    _sim_plot_theme = None
    _nmr_plot_theme = None
    _region_plot_theme = None
    _current_theme: str = "dark"
    _handlers: dict[str, str] = {}
    _info_tags: dict[str, str] = {}

    # ---------------------------------------------------------------------------- #
    #                                    Themes                                    #
    # ---------------------------------------------------------------------------- #

    @classmethod
    def global_theme(cls, chosen_theme: "str" = "dark"):
        """
        Accesses the global theme, loads theme upon first call

        Assumes the dpg context has been created

        Parameters
        ----------
        chosen_theme : str, optional
            Selected Global Theme, by default "dark"
        """
        cls._set_current_theme(chosen_theme)
        return Theme._access_theme_dynamic(
            "_main_themes", main_theme_components, theme_choice=chosen_theme
        )

    @classmethod
    def disabled_theme(cls, chosen_theme: str | None = None):
        """
        Accesses the disabled theme, loads theme upon first call

        Assumes that the dpg context has been created.

        Parameters
        ----------
        chosen_theme : str, optional
            Selected Global Theme, by default "dark"
        """
        return Theme._access_theme_dynamic(
            "_disabled_theme", disabled_theme_components, theme_choice=chosen_theme
        )

    @classmethod
    def hover_theme(cls, chosen_theme: str | None = None):
        """
        Accesses the hover theme, loads theme upon first call

        Assumes that the dpg context has been created

        Parameters
        ----------
        chosen_theme : str, optional
            Selected Global Theme, by default "dark"
        """
        return Theme._access_theme_dynamic(
            "_hover_theme", hover_theme_components, theme_choice=chosen_theme
        )

    @classmethod
    def sim_plot_theme(cls):
        """
        Accesses the main simulation plot theme, loads theme upon first call

        Assumes that the dpg context has been created.
        """
        return Theme._access_theme("_sim_plot_theme", sim_theme_components)

    @classmethod
    def nmr_plot_theme(cls):
        """
        Accesses the nmr plot theme, loads theme upon first call

        Assumes that the dpg context has been created.
        """
        return Theme._access_theme("_nmr_plot_theme", nmr_theme_components)

    @classmethod
    def region_plot_theme(cls):
        """
        Accesses the region plot theme, loads theme upon first call

        Assumes that the dpg context has been created.
        """
        return Theme._access_theme("_region_plot_theme", region_theme_components)

    # ---------------------------------------------------------------------------- #
    #                                   Handlers                                   #
    # ---------------------------------------------------------------------------- #

    @classmethod
    def handlers(cls, key: str | None = None) -> str:
        if not cls._handlers:
            hover_tag = "hover_handler"
            with dpg.item_handler_registry(tag=hover_tag):
                dpg.add_item_hover_handler(callback=hover_callback)
            cls._handlers["hover"] = hover_tag
        if key is not None:
            return cls._handlers[key]
        else:
            return cls._handlers["hover"]

    # ---------------------------------------------------------------------------- #
    #                               Helper Functions                               #
    # ---------------------------------------------------------------------------- #

    @classmethod
    def add_info_tag(cls, key, value):
        cls._info_tags[key] = value

    @classmethod
    def _set_current_theme(cls, chosen_theme: "str" = "dark"):
        cls._current_theme = chosen_theme.lower()

    @classmethod
    def _access_theme(cls, theme: str, theme_components, *args):
        if getattr(cls, theme) is None:
            with dpg.theme() as output_theme:
                theme_components(*args)
            setattr(cls, theme, output_theme)
        return getattr(cls, theme)

    @classmethod
    def _access_theme_dynamic(
        cls, theme_type: str, theme_components, theme_choice: str | None = None, *args
    ):
        if not getattr(cls, theme_type):
            for theme_name, theme in cls._theme_collection.items():
                theme_tag = dpg.generate_uuid()
                with dpg.theme(tag=theme_tag):
                    theme_components(theme)
                getattr(cls, theme_type)[theme_name] = theme_tag
        if theme_choice is None:
            theme_choice = cls._current_theme
        return getattr(cls, theme_type)[theme_choice.lower()]


def change_theme_callback(sender, app_data: str, user_data) -> None:
    dpg.bind_theme(Theme.global_theme(app_data.lower()))
    Theme._set_current_theme(app_data.lower())
    for info_tag in Theme._info_tags.values():
        dpg.configure_item(
            info_tag, color=Theme._theme_collection[Theme._current_theme]["INFO"]
        )


def hover_callback(sender, app_data, user_data):
    if dpg.is_item_enabled(user_data):
        if dpg.is_item_hovered(user_data):
            dpg.bind_item_theme(user_data, Theme.hover_theme())
        else:
            dpg.bind_item_theme(user_data, Theme.global_theme())
