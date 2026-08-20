import numpy as np
from ..preprocessing_class import LoadDirection
from ...utility.helper import transform_to_local_axes

def _get_concentrated_elemental_loads(element_name, loadcase_type, load_direction, locations, loads):
    # Determine element name, loadcase type, load direction, location, and load for each segment
    segment_loads_mask = ~np.isnan(loads) # Loads for each segment masking
    element_idx, load_idx = np.nonzero(segment_loads_mask) # Determine element index and load index of valid loads for each segment
    segment_element_name = element_name[element_idx] # Element name for each segment
    segment_loadcase_type = loadcase_type[element_idx] # Loadcase type for each segment
    segment_load_direction = load_direction[element_idx] # Load direction for each segment
    segment_location = locations[element_idx, load_idx] # Location for each segment
    segment_load = loads[element_idx, load_idx] # Load for each segment

    # Modified concentrated element loads
    modified_element_name = np.asarray(segment_element_name, dtype="U15")
    modified_loadcase_type = np.asarray(segment_loadcase_type, dtype=np.int8)
    modified_load_direction = np.asarray(segment_load_direction, dtype="U15")
    modified_location = np.asarray(segment_location, dtype=np.float64)
    modified_load = np.asarray(segment_load, dtype=np.float64)
    return modified_element_name, modified_loadcase_type, modified_load_direction, modified_location, modified_load

def _get_distributed_elemental_loads(element_name, element_objects, loadcase_type, load_direction, locations, uniform_load, loads):
    element_idx = np.asarray([element_objects["Name to Index"][name] for name in element_name], dtype=np.int32)
    element_length = element_objects["Length"][element_idx]

    # Determine element name, loadcase type, load direction, location, and load for each segment of uniform load
    uniform_load_mask = ~np.isnan(uniform_load) # Uniform load masking
    segment_uniform_element_name = element_name[uniform_load_mask] # Element name for each segment of uniform load
    segment_uniform_loadcase_type = loadcase_type[uniform_load_mask] # Loadcase type for each segment of uniform load
    segment_uniform_load_direction = load_direction[uniform_load_mask] # Load direction for each segment of uniform load
    segment_uniform_location = np.column_stack((
        np.zeros(uniform_load_mask.sum(), dtype=np.float64),
        element_length[uniform_load_mask],
    )) # Location for each segment of uniform load
    segment_uniform_load = np.column_stack((
        uniform_load[uniform_load_mask],
        uniform_load[uniform_load_mask],
    )) # Uniform load for each segment

    # Determine element name, loadcase type, load direction, location, and load for each segment of nonuniform load
    segment_nonuniform_loads_mask = (
        ~np.isnan(loads[:, :-1])
        & ~np.isnan(loads[:, 1:])
        & ~np.isnan(loads[:, :-1])
        & ~np.isnan(loads[:, 1:])
    ) # Nonuniform loads for each segment masking
    element_idx, load_idx = np.nonzero(segment_nonuniform_loads_mask) # Determine element index and load index of valid nonuniform loads for each segment
    segment_nonuniform_element_name = element_name[element_idx] # Element name for each segment of nonuniform load
    segment_nonuniform_loadcase_type = loadcase_type[element_idx] # Loadcase type for each segment of nonuniform load
    segment_nonuniform_load_direction = load_direction[element_idx] # Load direction for each segment of nonuniform load
    segment_nonuniform_location = np.column_stack((
        locations[element_idx, load_idx],
        locations[element_idx, load_idx + 1],
    )) # Location for each segment of nonuniform load
    segment_nonuniform_load = np.column_stack((
        loads[element_idx, load_idx],
        loads[element_idx, load_idx + 1],
    )) # Nonuniform load for each segment

    # Modified distributed elemental loads
    modified_element_name = np.concatenate((segment_uniform_element_name, segment_nonuniform_element_name)).astype(dtype="U15")
    modified_loadcase_type = np.concatenate((segment_uniform_loadcase_type, segment_nonuniform_loadcase_type)).astype(dtype=np.int8)
    modified_load_direction = np.concatenate((segment_uniform_load_direction, segment_nonuniform_load_direction)).astype(dtype="U15")
    modified_location = np.vstack((segment_uniform_location, segment_nonuniform_location)).astype(dtype=np.float64)
    modified_load = np.vstack((segment_uniform_load, segment_nonuniform_load)).astype(dtype=np.float64)
    return modified_element_name, modified_loadcase_type, modified_load_direction, modified_location, modified_load

def _get_shell_to_elemental_loads(shell_name, element_objects, shell_objects, loadcase_type, load_direction, load):
    shell_idx = np.asarray([shell_objects["Name to Index"][name] for name in shell_name], dtype=np.int32)
    edges_idx = shell_objects["Edges Index"][shell_idx]
    edges_name = element_objects["Unique Name"][edges_idx]
    edges_length = element_objects["Length"][edges_idx]
    shell_width = np.min(edges_length, axis=1)
    edge_load_magnitude = load * shell_width / 2.0 # Load magnitude for each edge
    shortest_length_mask = np.isclose(edges_length, shell_width[:, np.newaxis]) # Shortest length masking

    # Determine shell name, edge name, loadcase type, and load direction for each segment
    n_edge_segments = np.where(shortest_length_mask, 2, 3) # Number of edge segments of shell to edge load distribution
    segment_shell_name = np.repeat(np.broadcast_to(shell_name[:, None], edges_name.shape).ravel(), n_edge_segments.ravel()) # Shell name for each segment
    segment_edge_name = np.repeat(edges_name.ravel(), n_edge_segments.ravel()) # Edge name for each segment
    segment_loadcase_type = np.repeat(np.broadcast_to(loadcase_type[:, None], edges_name.shape).ravel(), n_edge_segments.ravel()) # Loadcase type for each segment
    segment_load_direction = np.repeat(np.broadcast_to(load_direction[:, None], edges_name.shape).ravel(), n_edge_segments.ravel()) # Load direction for each segment
    edge_length_per_segment = np.repeat(edges_length.ravel(), n_edge_segments.ravel()) # Edge length for each segment
    edge_load_magnitude_per_segment = np.repeat(np.broadcast_to(edge_load_magnitude[:, None], edges_name.shape).ravel(), n_edge_segments.ravel()) # Load magnitude for each segment
    shortest_length_mask_per_segment = np.repeat(shortest_length_mask.ravel(), n_edge_segments.ravel()) # Shortest length masking for each segment

    # Determine location, and load for each segment
    segment_idx = np.concatenate([np.arange(n) for n in n_edge_segments.ravel()]) # Flattened segment index
    divisor = np.where(shortest_length_mask_per_segment, 2.0, 3.0)
    loc_start = (segment_idx * edge_length_per_segment / divisor)
    loc_end = ((segment_idx + 1) * edge_length_per_segment / divisor)
    segment_location = np.column_stack((loc_start, loc_end)) # Location for each segment
    load_start = np.where(segment_idx == 0, 0.0, edge_load_magnitude_per_segment)
    load_end = np.where(segment_idx == divisor - 1, 0.0, edge_load_magnitude_per_segment)
    segment_load = np.column_stack((load_start, load_end)) # Load for each segment

    # Modified shell to elemental loads
    modified_shell_name = np.asarray(segment_shell_name, dtype="U15")
    modified_edge_name = np.asarray(segment_edge_name, dtype="U15")
    modified_loadcase_type = np.asarray(segment_loadcase_type, dtype=np.int8)
    modified_load_direction = np.asarray(segment_load_direction, dtype="U15")
    modified_location = np.asarray(segment_location, dtype=np.float64)
    modified_load = np.asarray(segment_load, dtype=np.float64)
    return modified_shell_name, modified_edge_name, modified_loadcase_type, modified_load_direction, modified_location, modified_load

# Need to be vectorised for faster performance
def _generate_group_nodal_loads(node_tag, loadcase_type, loads):
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

# Need to be vectorised for faster performance
def _generate_group_concentrated_element_loads(ndim, elements, element_tag, loadcase_type, direction, location, load):
    n = len(element_tag)
    element_idx = np.fromiter((elements.tag_to_idx(tags=tag)
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
    unique_element_idx = np.fromiter((elements.tag_to_idx(tags=tag)
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

# Need to be vectorised for faster performance
def _generate_group_distributed_element_loads(ndim, elements, element_tag, loadcase_type, direction, location, load):
    n = len(element_tag)
    element_idx = np.fromiter((elements.tag_to_idx(tags=tag)
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
    unique_element_idx = np.fromiter((elements.tag_to_idx(tags=tag)
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