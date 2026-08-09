import numpy as np
from ._preproc_class import LoadDirection
from sadpropy.utility.helperfunc import transform_to_local_axes

def get_concentrated_line_loads(line_name, loadcase_type, load_direction, locations, loads):
    new_line_name = []
    new_loadcase_type = []
    new_load_direction = []
    new_location = []
    new_load = []

    for i in range(len(line_name)):
        for j in range(loads.shape[1]):
            if np.isnan(loads[i, j]): # Skip empty loads
                continue
            new_line_name.append(line_name[i])
            new_loadcase_type.append(loadcase_type[i])
            new_load_direction.append(load_direction[i])
            new_location.append(locations[i, j])
            new_load.append(loads[i, j])
    new_line_name = np.asarray(new_line_name, dtype="U15")
    new_loadcase_type = np.asarray(new_loadcase_type, dtype="U15")
    new_load_direction = np.asarray(new_load_direction, dtype="U15")
    new_location = np.asarray(new_location, dtype=np.float64)
    new_load = np.asarray(new_load, dtype=np.float64)
    return new_line_name, new_loadcase_type, new_load_direction, new_location, new_load

def get_distributed_line_loads(line_name, loadcase_type, load_direction, locations, uniform_load, loads):
    new_line_name = []
    new_loadcase_type = []
    new_load_direction = []
    new_location = []
    new_load = []
    for i in range(len(line_name)):
        if not np.isnan(uniform_load[i]):
            new_line_name.append(line_name[i])
            new_loadcase_type.append(loadcase_type[i])
            new_load_direction.append(load_direction[i])
            new_location.append([np.nan, np.nan])
            new_load.append([uniform_load[i], uniform_load[i]])
        for j in range(loads.shape[1] - 1):
            k = j + 1
            if np.isnan(loads[i, j]): # Skip empty load: first point
                continue
            if np.isnan(loads[i, j + 1]): # Skip empty load: second point
                continue
            if np.isnan(locations[i, j]): # Skip empty location: first point
                continue
            if np.isnan(locations[i, j + 1]): # Skip empty location: second point
                continue
            new_line_name.append(line_name[i])
            new_loadcase_type.append(loadcase_type[i])
            new_load_direction.append(load_direction[i])
            new_location.append(locations[i, j:k+1])
            new_load.append(loads[i, j:k+1])
    new_line_name = np.asarray(new_line_name, dtype="U15")
    new_loadcase_type = np.asarray(new_loadcase_type, dtype="U15")
    new_load_direction = np.asarray(new_load_direction, dtype="U15")
    new_location = np.asarray(new_location, dtype=np.float64)
    new_load = np.asarray(new_load, dtype=np.float64)
    return new_line_name, new_loadcase_type, new_load_direction, new_location, new_load

def generate_group_nodal_loads(node_tag, loadcase_type, loads):
    grouping_keys = np.empty(
        len(node_tag),
        dtype=[
            ("tag", np.int32),
            ("loadcase", np.int32),
        ])
    grouping_keys["tag"] = node_tag
    grouping_keys["loadcase"] = loadcase_type
    unique_grouping_keys, indices = np.unique(
        grouping_keys,
        return_inverse=True,
    )
    summed_loads = np.zeros((len(unique_grouping_keys), loads.shape[1]), dtype=loads.dtype)
    np.add.at(summed_loads, indices, loads)
    result_node_tag = unique_grouping_keys["tag"]
    result_loadcase_type = unique_grouping_keys["loadcase"]
    result_loads = summed_loads
    return result_node_tag, result_loadcase_type, result_loads

def generate_group_concentrated_element_loads(ndim, elements, element_tag, loadcase_type, direction, location, load):
    n = len(element_tag)
    element_idx = np.fromiter((elements.tag_to_idx[tag]
        for tag in element_tag), dtype=np.int32, count=n)
    element_length = elements.length[element_idx]
    fraction_location = location / element_length
    grouping_keys = np.empty(
        n,
        dtype=[
            ("tag", np.int32),
            ("loadcase", np.int32),
            ("direction", "U15"),
            ("location", np.float64),
        ])
    grouping_keys["tag"] = element_tag
    grouping_keys["loadcase"] = loadcase_type
    grouping_keys["direction"] = direction
    grouping_keys["location"] = fraction_location
    unique_grouping_keys, indices = np.unique(
        grouping_keys,
        return_inverse=True,
    )
    summed_load = np.zeros(len(unique_grouping_keys), dtype=load.dtype)
    np.add.at(summed_load, indices, load)
    result_element_tag = unique_grouping_keys["tag"]
    result_loadcase_type = unique_grouping_keys["loadcase"]
    result_direction = unique_grouping_keys["direction"]
    result_location = unique_grouping_keys["location"]
    result_load = summed_load

    # Transform Load to Local axes
    m = len(result_element_tag)
    unique_element_idx = np.fromiter((elements.tag_to_idx[tag]
        for tag in result_element_tag), dtype=np.int32, count=m)
    rotation_matrices = elements.rotation_matrices[unique_element_idx]
    direction_map = LoadDirection.get_direction(ndim)
    direction_vectors = np.stack([direction_map[dir] for dir in result_direction])
    global_map = LoadDirection.global_direction[ndim]
    local_map = LoadDirection.local_direction[ndim]
    global_mask = np.isin(result_direction, list(global_map))
    local_mask = np.isin(result_direction, list(local_map))
    transformed_loads = np.empty((m, ndim), dtype=np.float64)
    if np.any(global_mask):
        load_vectors = (direction_vectors[global_mask] * result_load[global_mask, None])
        transformed_loads[global_mask] = transform_to_local_axes(values=load_vectors, rotation_matrices=rotation_matrices[global_mask])
    if np.any(local_mask):
        transformed_loads[local_mask] = (direction_vectors[local_mask] * result_load[local_mask, None])
    return result_element_tag, result_loadcase_type, result_location, transformed_loads

def generate_group_distributed_element_loads(ndim, elements, element_tag, loadcase_type, direction, location, load):
    n = len(element_tag)
    element_idx = np.fromiter((elements.tag_to_idx[tag]
        for tag in element_tag), dtype=np.int32, count=n)
    element_length = elements.length[element_idx]
    uniform_mask = np.all(np.isnan(location), axis=1)
    location = location.copy()
    location[uniform_mask, 0] = 0.0
    location[uniform_mask, 1] = element_length[uniform_mask]
    fraction_location = location / element_length[:, None]
    grouping_keys = np.empty(
        n,
        dtype=[
            ("tag", np.int32),
            ("loadcase", np.int32),
            ("direction", "U15"),
        ])
    grouping_keys["tag"] = element_tag
    grouping_keys["loadcase"] = loadcase_type
    grouping_keys["direction"] = direction
    unique_groups, group_indices = np.unique(
        grouping_keys,
        return_inverse=True,
    )

    result_element_tag = []
    result_loadcase_type = []
    result_direction = []
    result_location = []
    result_load = []
    for group_idx in range(len(unique_groups)):
        mask = group_indices == group_idx
        group_locations = fraction_location[mask]
        group_loads = load[mask]

        # --------------------------------------------------------------
        # Find all location boundaries
        # --------------------------------------------------------------

        breakpoints = np.unique(group_locations.ravel())

        # Need at least two points to create a segment
        if len(breakpoints) < 2:
            continue

        # --------------------------------------------------------------
        # Process every interval between consecutive breakpoints
        # --------------------------------------------------------------
        for j in range(len(breakpoints) - 1):
            x1 = breakpoints[j]
            x2 = breakpoints[j + 1]
            if np.isclose(x1, x2):
                continue

            # ----------------------------------------------------------
            # Find loads that cover this entire interval
            # ----------------------------------------------------------
            active = ((group_locations[:, 0] <= x1) & (group_locations[:, 1] >= x2))
            if not np.any(active):
                continue

            active_locations = group_locations[active]
            active_loads = group_loads[active]
            
            # ----------------------------------------------------------
            # Interpolate each active load at x1 and x2
            # ----------------------------------------------------------
            start_load = np.zeros(len(active_loads), dtype=np.float64)
            end_load = np.zeros( len(active_loads), dtype=np.float64,)
            for k in range(len(active_loads)):
                lx1, lx2 = active_locations[k]
                lw1, lw2 = active_loads[k]

                # Linear interpolation
                if np.isclose(lx1, lx2):
                    # Degenerate interval; shouldn't normally occur
                    continue

                slope = (lw2 - lw1) / (lx2 - lx1)
                start_load[k] = lw1 + slope * (x1 - lx1)
                end_load[k] = lw1 + slope * (x2 - lx1)

            # ----------------------------------------------------------
            # Superimpose active loads
            # ----------------------------------------------------------
            total_start_load = np.sum(start_load)
            total_end_load = np.sum(end_load)
            result_element_tag.append(unique_groups[group_idx]["tag"])
            result_loadcase_type.append(unique_groups[group_idx]["loadcase"])
            result_direction.append(unique_groups[group_idx]["direction"])
            result_location.append([x1, x2])
            result_load.append([total_start_load, total_end_load])
    result_element_tag = np.asarray(result_element_tag, dtype=np.int32)
    result_loadcase_type = np.asarray(result_loadcase_type, dtype=np.int32)
    result_direction = np.asarray(result_direction, dtype="U15")
    result_location = np.asarray(result_location, dtype=np.float64)
    result_load = np.asarray(result_load, dtype=np.float64)

    # Transform Load to Local axes
    m = len(result_element_tag)
    unique_element_idx = np.fromiter((elements.tag_to_idx[tag]
        for tag in result_element_tag), dtype=np.int32, count=m)
    rotation_matrices = elements.rotation_matrices[unique_element_idx]
    direction_map = LoadDirection.get_direction(ndim)
    direction_vectors = np.stack([direction_map[dir] for dir in result_direction])
    global_map = LoadDirection.global_direction[ndim]
    local_map = LoadDirection.local_direction[ndim]
    global_mask = np.isin(result_direction, list(global_map))
    local_mask = np.isin(result_direction, list(local_map))
    transformed_loads = np.empty((m, 2, ndim), dtype=np.float64)
    if np.any(global_mask):
        load_vectors = (result_load[global_mask, :, None] * direction_vectors[global_mask, None, :])
        transformed_loads[global_mask] = transform_to_local_axes(values=load_vectors, rotation_matrices=rotation_matrices[global_mask])
    if np.any(local_mask):
        transformed_loads[local_mask] = (result_load[local_mask, :, None] * direction_vectors[local_mask, None, :])
    return result_element_tag, result_loadcase_type, result_location, transformed_loads

def _tributary_width(x, edge_length, perpendicular_length):
    return min(x, perpendicular_length / 2.0, edge_length - x)

def generate_edge_load_segments(edge_length, perpendicular_length, surface_load):
    # --------------------------------------------------------------
    # Important locations along the edge
    # --------------------------------------------------------------
    breakpoints = np.array([0.0, perpendicular_length / 2.0, edge_length - perpendicular_length / 2.0, edge_length])

    # Keep only locations that are actually inside the edge
    breakpoints = breakpoints[(breakpoints >= 0.0) & (breakpoints <= edge_length)]

    # Remove duplicate points
    breakpoints = np.unique(breakpoints)

    result_location = []
    result_load = []
    # --------------------------------------------------------------
    # Generate piecewise-linear segments
    # --------------------------------------------------------------
    for x1, x2 in zip(breakpoints[:-1], breakpoints[1:]):
        if np.isclose(x1, x2):
            continue
        b1 = _tributary_width(x=x1, edge_length=edge_length, perpendicular_length=perpendicular_length)
        b2 = _tributary_width(x=x2, edge_length=edge_length, perpendicular_length=perpendicular_length)
        w1 = surface_load * b1
        w2 = surface_load * b2

        # Ignore a completely zero segment
        if np.isclose(w1, 0.0) and np.isclose(w2, 0.0):
            continue
        result_location.append([x1, x2])
        result_load.append([w1, w2])
    return (np.asarray(result_location, dtype=np.float64), np.asarray(result_load, dtype=np.float64))