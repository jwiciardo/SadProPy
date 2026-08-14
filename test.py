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
print()

def _generate_shell_element_load(length, half_width, line_load, is_shortest):
    if is_shortest:
        locations = np.array([[0.0, half_width], [half_width, length]], dtype=np.float64)
        loads = np.array([[0.0, line_load], [line_load, 0.0]], dtype=np.float64)
    else:
        middle = length - half_width
        locations = np.array([[0.0, half_width], [half_width, middle], [middle, length]], dtype=np.float64)
        loads = np.array([[0.0, line_load], [line_load, line_load], [line_load, 0.0]], dtype=np.float64)
    return locations, loads

elements_length = elements.length[shells.elements_idx]
shell_width = np.min(elements_length, axis=1)
half_width = shell_width * 0.5
line_load = shells.loads * half_width
is_shortest = np.isclose(elements_length, shell_width[:, np.newaxis])
shell_loc = []
shell_load = []
for i in range(len(shells.elements_idx)):
    shell_loc_i = []
    shell_load_i = []
    for j, length in enumerate(elements_length[i]):
        loc_ij, load_ij = _generate_shell_element_load(
            length=length,
            half_width=half_width[i],
            line_load=line_load[i],
            is_shortest=is_shortest[i, j],
        )
        shell_loc_i.append(loc_ij)
        shell_load_i.append(load_ij)
    shell_loc.append(shell_loc_i)
    shell_load.append(shell_load_i)
print(shell_loc)
print(shell_load)



from sadpropy.preprocessing.excel_translator import ExcelReader

ExcelReader()