import numpy as np

class LoadDirection:
    global_direction = {
        3 : {
            "Global-X": np.asarray([1, 0, 0], dtype=np.float64),
            "Global-Y": np.asarray([0, 1, 0], dtype=np.float64),
            "Gravity": np.asarray([0, 0, -1], dtype=np.float64),
        },
        2 : {
            "Global-X": np.asarray([1, 0], dtype=np.float64),
            "Global-Y": np.asarray([0, 1], dtype=np.float64),
            "Gravity": np.asarray([0, -1], dtype=np.float64),
        }
    }
    local_direction = {
        3: {
            "Local-x": np.asarray([1, 0, 0], dtype=np.float64),
            "Local-y": np.asarray([0, 1, 0], dtype=np.float64),
            "Local-z": np.asarray([0, 0, 1], dtype=np.float64),
        },
        2: {
            "Local-x": np.asarray([1, 0], dtype=np.float64),
            "Local-y": np.asarray([0, 1], dtype=np.float64),
        }
    }

    @classmethod
    def get_direction(cls, ndim):
        return {**cls.global_direction[ndim], **cls.local_direction[ndim]}