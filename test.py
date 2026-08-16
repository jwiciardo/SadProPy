import numpy as np
from dataclasses import dataclass

@dataclass(slots=True, frozen=True)
class Elements:
    index: np.ndarray                   # int32, shape (N,)
    length: np.ndarray                  # float64, shape (N,)

@dataclass(slots=True, frozen=True)
class Shells:
    index: np.ndarray                   # int32, shape (N,)
    elements_idx: np.ndarray            # int32, shape (N,4)
    loads: np.ndarray                   # float64, shape (N,)

elements = Elements(
    index = np.asarray([0, 1, 2, 3, 4, 5, 6], dtype=np.int32),
    length = np.asarray([12.0, 12.0, 12.0, 12.0, 8.0, 8.0, 8.0], dtype=np.float64),
)
shells = Shells(
    index = np.asarray([0, 1], dtype=np.int32),
    elements_idx =  np.asarray([[0, 5, 2, 4], [1, 6, 3, 5]], dtype=np.int32),
    loads = np.asarray([-12.0, -10.0], dtype=np.float64),
)


shells_idx = shells.index
elements_idx = shells.elements_idx
elements_length = elements.length[elements_idx]
shell_width = np.min(elements_length, axis=1)
line_load = shells.loads * shell_width / 2.0
is_shortest = np.isclose(elements_length, shell_width[:, np.newaxis])

shell_loc = []
shell_load = []
for i in range(len(shells_idx)):
    for j in range(len(elements_idx)):
        length = elements_length[i, j]
        load = line_load[i]
        n = len(elements_idx)
        if is_shortest[i, j]:
            n = 2
            for k in range(n):
                if (k + 1) == n:
                    loc_i = k * length / n
                    loc_j = (k + 1) * length / n
                    loc_ij = np.asarray([loc_i, loc_j], dtype=np.float64)
                    load_i = k * load
                    load_j = 0.0 * load
                    load_ij = np.asarray([load_i, load_j], dtype=np.float64)
                else:
                    loc_i = k * length / n
                    loc_j = (k + 1) * length / n
                    loc_ij = np.asarray([loc_i, loc_j], dtype=np.float64)
                    load_i = k * load
                    load_j = (k + 1) * load
                    load_ij = np.asarray([load_i, load_j], dtype=np.float64)
                shell_loc.append(loc_ij)
                shell_load.append(load_ij)
        else:
            n = 3
            for k in range(n):
                if (k + 1) == n:
                    loc_i = k * length / n
                    loc_j = (k + 1) * length / n
                    loc_ij = np.asarray([loc_i, loc_j], dtype=np.float64)
                    load_i = (k - 1) * load
                    load_j = 0.0 * load
                    load_ij = np.asarray([load_i, load_j], dtype=np.float64)
                elif (k + 1) == (n - 1):
                    loc_i = k * length / n
                    loc_j = (k + 1) * length / n
                    loc_ij = np.asarray([loc_i, loc_j], dtype=np.float64)
                    load_i = k * load
                    load_j = k * load
                    load_ij = np.asarray([load_i, load_j], dtype=np.float64)
                else:
                    loc_i = k * length / n
                    loc_j = (k + 1) * length / n
                    loc_ij = np.asarray([loc_i, loc_j], dtype=np.float64)
                    load_i = k * load
                    load_j = (k + 1) * load
                    load_ij = np.asarray([load_i, load_j], dtype=np.float64)
                shell_loc.append(loc_ij)
                shell_load.append(load_ij)
print(shell_loc)
print(shell_load)
print(elements_idx[0])
print(elements_length[0, 0])
print(shell_width[0])
print(line_load[0])
print(is_shortest[0, 0])