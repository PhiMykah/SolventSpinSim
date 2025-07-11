# Typing #
from typing import Generator
from numpy.typing import ArrayLike
from typing import Literal
from typing import Any
import numpy as np

Peak = tuple[float,float]
PeakList = list[Peak]
PeakArray = np.ndarray[tuple[Any, ...], np.dtype[np.float64]]