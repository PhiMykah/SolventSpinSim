from sys import argv
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
    ui = UI('SolventSpinSim')
    ui.run(clear_color=(0,0,0,0))
    destroy_context()

if __name__ == "__main__":
    main(argv[1:])