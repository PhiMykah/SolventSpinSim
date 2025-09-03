from sys import argv

from dearpygui.dearpygui import destroy_context
from parse import parse_args
from settings import Settings
from commandline import CommandLine
from ui import UI


class DPGStatus:
    _context_enabled: bool = False
    _viewport_enabled: bool = False

    @staticmethod
    def set_context_status(status: bool) -> None:
        DPGStatus._context_enabled = status

    @staticmethod
    def is_context_enabled() -> bool:
        return DPGStatus._context_enabled

    @staticmethod
    def set_viewport_status(status: bool) -> None:
        DPGStatus._viewport_enabled = status

    @staticmethod
    def is_viewport_enabled() -> bool:
        return DPGStatus._viewport_enabled


def main(argv: list[str]) -> None:
    """
    Main entry point of SolventSpinSim (3S) function

    Parameters
    ----------
    argv : list[str]
        command-line arguments from system (exclude file_name as parameter)
    """
    settings = Settings(parse_args(argv))
    if settings["ui_disabled"]:
        cl = CommandLine(settings)
        cl.run()
    else:
        ui = UI("SolventSpinSim", settings)
        ui.run(clear_color=(0, 0, 0, 0))
        destroy_context()
        DPGStatus.set_context_status(False)
        DPGStatus.set_viewport_status(False)


if __name__ == "__main__":
    main(argv[1:])
