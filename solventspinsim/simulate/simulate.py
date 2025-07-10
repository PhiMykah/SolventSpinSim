from matplotlib.pylab import half
import numpy as np
from numpy._typing._array_like import NDArray
from simulate.types import *

def simulate_peaklist(peaklist : PeakList, points : int = 800, half_height_width : float | int = 1,
                      freq_limits : tuple[float,float] | None = None):
    """
    Simulate the NMR spectrum represented by the peaklist

    Parameters
    ----------
    peaklist : PeakList
        A list of peaks representing the simulated NMR spectrum for the given spin system
    points : int, optional
        Number of points in the entire spectrum, by default 800
    half_height_width : float | int, optional
        Linewidth at half height (in Hz) for each lorentzian
    freq_limits : tuple[float,float] | None, optional
        Frequency bounds for the simulation, by default None

    Returns
    -------
    # TODO

    Notes
    -----
        Adapted from nmrsim's mplplot fucntion in plt.py
    """
    peaklist.sort()
    if freq_limits:
        if isinstance(freq_limits, tuple) and len(freq_limits) == 2 and all(isinstance(x, (int, float)) for x in freq_limits):
            l_limit, r_limit = min(freq_limits), max(freq_limits)
        else:
            raise ValueError("freq_limits must be a tuple of two numbers (int or float)")
    else:
        l_limit = peaklist[0][0] - 50
        r_limit = peaklist[-1][0] + 50

    # Define x axis
    x : np.ndarray[tuple[Any, ...], np.dtype[np.float64]] = np.linspace(l_limit, r_limit, points)

    y = simulate_lorentzians(x, peaklist, half_height_width)

def simulate_lorentzians(x, peaklist, w) -> np.ndarray:
    return np.zeros(1)