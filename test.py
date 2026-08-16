import numpy as np
from dataclasses import dataclass

@dataclass(slots=True, frozen=True)
class Elements:
    index: np.ndarray                   # int32, shape (N,)
    length: np.ndarray                  # float64, shape (N,)
    uniform_load: np.ndarray            # float64, shape (N,)
    nonuniform_load: np.ndarray         # float64, shape (N,4)
    location: np.ndarray               # float64, shape (N,4)

@dataclass(slots=True, frozen=True)
class Shells:
    index: np.ndarray                   # int32, shape (N,)
    elements_idx: np.ndarray            # int32, shape (N,4)
    loads: np.ndarray                   # float64, shape (N,)

elements = Elements(
    index = np.asarray([0, 1, 2, 3, 4, 5, 6], dtype=np.int32),
    length = np.asarray([12.0, 12.0, 12.0, 12.0, 8.0, 8.0, 8.0], dtype=np.float64),
    uniform_load = np.asarray([np.nan, np.nan, 10.0, np.nan, np.nan, 9.0, np.nan], dtype=np.float64),
    nonuniform_load = np.asarray([
        [np.nan, np.nan, np.nan, np.nan],
        [0.0, 13.0, 13.0, 0.0],
        [np.nan, np.nan, np.nan, np.nan],
        [np.nan, np.nan, np.nan, np.nan],
        [0.0, 15.0, 0.0, np.nan],
        [np.nan, np.nan, np.nan, np.nan],
        [np.nan, np.nan, np.nan, np.nan],
    ], dtype=np.float64),
    location = np.asarray([
        [np.nan, np.nan, np.nan, np.nan],
        [0.0, 4.0, 8.0, 12.0],
        [np.nan, np.nan, np.nan, np.nan],
        [np.nan, np.nan, np.nan, np.nan],
        [0.0, 4.0, 8.0, np.nan],
        [np.nan, np.nan, np.nan, np.nan],
        [np.nan, np.nan, np.nan, np.nan],
    ], dtype=np.float64),
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
is_shortest = np.isclose(elements_length, shell_width[:, None])

# Number of segments for each shell edge
n_segments = np.where(is_shortest, 2, 3)

# ------------------------------------------------------------------
# Segment index
# ------------------------------------------------------------------

# Repeat edge data according to number of segments
shell_index = np.repeat(np.broadcast_to(shells_idx[:, None], elements_idx.shape).ravel(), n_segments.ravel())
ele_index = np.repeat(elements_idx.ravel(), n_segments.ravel())
length = np.repeat(elements_length.ravel(), n_segments.ravel())
load = np.repeat(np.broadcast_to(line_load[:, None], elements_idx.shape).ravel(), n_segments.ravel())
short = np.repeat(is_shortest.ravel(), n_segments.ravel())

# ------------------------------------------------------------------
# Locations
# ------------------------------------------------------------------
segment_idx = np.concatenate([np.arange(n) for n in n_segments.ravel()])
divisor = np.where(short, 2.0, 3.0)
shell_loc_start = (segment_idx * length / divisor)
shell_loc_end = ((segment_idx + 1) * length / divisor)
shell_loc = np.column_stack((shell_loc_start, shell_loc_end))

# ------------------------------------------------------------------
# Loads
# ------------------------------------------------------------------
shell_load_start = np.where(segment_idx == 0, 0.0, load)
shell_load_end = np.where(segment_idx == divisor - 1, 0.0, load)
shell_load = np.column_stack((shell_load_start, shell_load_end))
print(shell_index)
print(ele_index)
print(shell_loc)
print(shell_load)

element_idx = elements.index
element_length = elements.length
element_uniform_load = elements.uniform_load
element_nonuniform_load = elements.nonuniform_load
element_location = elements.location

# Uniform distributed load
uniform_load_mask = ~np.isnan(element_uniform_load)
print(uniform_load_mask)

uniform_load_element_index = element_idx[uniform_load_mask]
uniform_load_location = np.full((uniform_load_mask.sum(), 2), np.nan, dtype=np.float64)
segment_uniform_load = np.column_stack((
    element_uniform_load[uniform_load_mask],
    element_uniform_load[uniform_load_mask],
))

# Nonuniform distributed load
valid_segment = (
    ~np.isnan(element_nonuniform_load[:, :-1])
    & ~np.isnan(element_nonuniform_load[:, 1:])
    & ~np.isnan(element_location[:, :-1])
    & ~np.isnan(element_location[:, 1:])
)

# Each True represents one valid load segment.
row_idx, col_idx = np.nonzero(valid_segment)


segment_element_index = element_idx[row_idx]
segment_location = np.column_stack((
    element_location[row_idx, col_idx],
    element_location[row_idx, col_idx + 1],
))
segment_load = np.column_stack((
    element_nonuniform_load[row_idx, col_idx],
    element_nonuniform_load[row_idx, col_idx + 1],
))


# ------------------------------------------------------------
# 3. Combine uniform + distributed loads
# ------------------------------------------------------------
modified_element_index = np.concatenate((
    uniform_load_element_index,
    segment_element_index,
)).astype("U15")
modified_location = np.vstack((
    uniform_load_location,
    segment_location,
)).astype(np.float64)
modified_load = np.vstack((
    segment_uniform_load,
    segment_load,
)).astype(np.float64)

print(modified_element_index)
print(modified_location)
print(modified_load)

