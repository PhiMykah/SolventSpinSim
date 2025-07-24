import numpy as np

from nmrPype import DataFrame

def load_nmr_array(nmr_file : str, field_strength : float) -> np.ndarray:
    """
    Loads NMR data from file and returns a 2D array of (Hz, intensity).
    """
    df = DataFrame(nmr_file)

    if df.array is None:
        raise ValueError("nmrPype array is empty!")
    if df.array.ndim != 1:
        raise ValueError("Unsupported NMRPipe file dimensionality!")
    
    x_vals = np.arange(1, len(df.array)+1)

    init_sw: float = df.getParam("NDSW") 
    init_obs: float = df.getParam("NDOBS")
    init_orig: float = df.getParam("NDORIG")
    init_size: float = df.getParam("NDSIZE")

    init_sw  = 1.0 if (init_sw == 0.0) else init_sw
    init_obs = 1.0 if (init_obs == 0.0) else init_obs

    delta: float = -init_sw/(init_size)
    first: float = init_orig - delta*(init_size - 1)

    specValPPM  = (first + (x_vals - 1.0)*delta)/init_obs

    specValHz : list[float] = [ppm * field_strength for ppm in specValPPM]
    return np.vstack((specValHz, df.array))