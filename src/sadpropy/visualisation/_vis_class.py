import numpy as np
from ._vis_dataclass import Symbol3D

class StructuralSymbols:

    @staticmethod
    def fixed():
        vertices = np.array([
            [-0.5, 0.0, -0.7],
            [0.5, 0.0, -0.7],
            [0.5, 0.0, 0.0],
            [-0.5, 0.0, 0.0],
            [0.0, -0.5, -0.7],
            [0.0, 0.5, -0.7],
            [0.0, 0.5, 0.0],
            [0.0, -0.5, 0.0],
        ], dtype=np.float64)
        segments = np.array([
            [0, 1],
            [1, 2],
            [2, 3],
            [3, 0],
            [4, 5],
            [5, 6],
            [6, 7],
            [7, 4],
        ], dtype=np.int32)
        return Symbol3D(vertices, segments)

#    @staticmethod
#    def pinned():
        vertices = np.array([
            [0.0, 0.0, 0.6],
            [0.0, -0.6, -0.6],
            [0.0, 0.6, -0.6],
            [0.0, 0.0, 0.6],
        ], dtype=np.float64)
        segments = np.array([
            [0, 1],
            [1, 2],
            [2, 3],
        ], dtype=np.int32)
        return Symbol3D(vertices, segments)

#    @staticmethod
#    def roller():
        vertices = np.array([
            [0.0, 0.0, 0.6],
            [0.0, -0.6, -0.4],
            [0.0, 0.6, -0.4],
            [0.0, 0.0, 0.6],
            [0.0, -0.3, -0.8],
            [0.0, 0.3, -0.8],
        ], dtype=np.float64)
        segments = np.array([
            [0, 1],
            [1, 2],
            [2, 3],
            [4, 5],
        ], dtype=np.int32)
        return Symbol3D(vertices, segments)