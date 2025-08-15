# Typing #
from typing import Literal, Any, Generator
from numpy.typing import ArrayLike
import numpy as np

Peak = tuple[float,float,int]
PeakList = list[Peak]
PeakArray = np.ndarray[tuple[Any, ...], np.dtype[np.float64]]