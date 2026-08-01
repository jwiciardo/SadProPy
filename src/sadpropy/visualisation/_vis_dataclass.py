from dataclasses import dataclass
import numpy as np

@dataclass(slots=True, frozen=True)
class Symbol3D:
    vertices: np.ndarray                # float64, shape (N,3)
    segments: np.ndarray                # int32, shape (M,2)