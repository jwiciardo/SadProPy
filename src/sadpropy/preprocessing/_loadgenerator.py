import numpy as np

def get_concentrated_line_loads(line_name, loadcase_type, load_direction, locations, loads):
    new_line_name = []
    new_loadcase_type = []
    new_load_direction = []
    new_location = []
    new_load = []

    for i in range(len(line_name)):
        for j in range(loads.shape[1]):
            if loads[i, j] == 0: # Skip empty loads
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

def generate_unique_nodal_loads(node_tag, loadcase_type, loads):
    grouping_keys = np.column_stack((node_tag, loadcase_type))
    unique_grouping_keys, indices = np.unique(
        grouping_keys,
        axis=0,
        return_inverse=True,
    )
    summed_loads = np.zeros((len(unique_grouping_keys), loads.shape[1]), dtype=loads.dtype)
    np.add.at(summed_loads, indices, loads)
    unique_node_tag = unique_grouping_keys[:, 0]
    unique_loadcase_type = unique_grouping_keys[:, 1]
    unique_loads = summed_loads
    return unique_node_tag, unique_loadcase_type, unique_loads

def generate_unique_concentrated_element_loads(element_tag, loadcase_type, direction, locations, loads):
    grouping_keys = np.column_stack((element_tag, loadcase_type, direction, locations))
    unique_grouping_keys, indices = np.unique(
        grouping_keys,
        axis=0,
        return_inverse=True,
    )
    summed_load = np.zeros(len(unique_grouping_keys), dtype=loads.dtype)
    np.add.at(summed_load, indices, loads)
    unique_element_tag = unique_grouping_keys[:, 0]
    unique_loadcase_type = unique_grouping_keys[:, 1]
    unique_direction = unique_grouping_keys[:, 2]
    unique_locations = unique_grouping_keys[:, 3]
    unique_loads = summed_load
    return unique_element_tag, unique_loadcase_type, unique_direction, unique_locations, unique_loads