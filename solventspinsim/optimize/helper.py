import numpy as np


def unpack_params(params: np.ndarray | list, matrix_size: int, matrix_shape: tuple):
    cMatrix_flat = np.array(params[:matrix_size])
    intensities = np.array(params[matrix_size : matrix_size + matrix_shape[0]])

    sw, obs = params[matrix_size + matrix_shape[0] : matrix_size + matrix_shape[0] + 2]
    w = params[matrix_size + matrix_shape[0] + 2 :]

    return cMatrix_flat.reshape(matrix_shape), intensities, sw, obs, w


def unpack_params_water(
    params: np.ndarray | list, matrix_size: int, matrix_shape: tuple
):
    cMatrix_flat = np.array(params[:matrix_size])
    intensities = np.array(params[matrix_size : matrix_size + matrix_shape[0]])

    water_freq, water_intensity, water_hhw = params[
        matrix_size + matrix_shape[0] : matrix_size + matrix_shape[0] + 3
    ]
    sw, obs = params[
        matrix_size + matrix_shape[0] + 3 : matrix_size + matrix_shape[0] + 5
    ]
    w = params[matrix_size + matrix_shape[0] + 5 :]

    return (
        cMatrix_flat.reshape(matrix_shape),
        intensities,
        water_freq,
        water_intensity,
        water_hhw,
        sw,
        obs,
        w,
    )
