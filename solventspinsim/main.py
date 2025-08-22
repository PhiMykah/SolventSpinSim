class ContextStatus:
    is_context_enabled = False

    @staticmethod
    def set_status(status: bool) -> None:
        ContextStatus.is_context_enabled = status

    @staticmethod
    def is_enabled() -> bool:
        return ContextStatus.is_context_enabled
    
from sys import argv
from settings import Settings
from ui import UI
from dearpygui.dearpygui import destroy_context

def main(argv : list[str]) -> None:
    """
    Main entry point of SolventSpinSim (3S) function

    Parameters
    ----------
    argv : list[str]
        command-line arguments from system (exclude file_name as parameter)
    """
    settings = Settings()
    ui = UI('SolventSpinSim', settings)
    ui.run(clear_color=(0,0,0,0))
    destroy_context()
    ContextStatus.set_status(False)
    
if __name__ == "__main__":
    main(argv[1:])