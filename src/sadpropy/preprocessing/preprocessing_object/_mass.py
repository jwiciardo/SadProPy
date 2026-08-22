import numpy as np
from ...utility.helper import transform_to_global_axes

def _generate_concentrated_element_to_nodal_gravity_loads(nodes, elements, element_tag, loadcase, location, loads):
    n = len(element_tag)
    element_idx = np.fromiter((elements.tag_to_idx(tags=tag)
        for tag in element_tag), dtype=np.int32, count=n)
    
    # Transform Load to Global axes
    rotation_matrices = elements.rotation_matrices[element_idx]
    transformed_loads = transform_to_global_axes(values=loads, rotation_matrices=rotation_matrices)
    transformed_load = transformed_loads[:, 2]

    # Distribute to end nodes
    end_nodes_idx = elements.end_nodes_idx[element_idx]
    inode_tag = nodes.node_tag[end_nodes_idx[:, 0]]
    jnode_tag = nodes.node_tag[end_nodes_idx[:, 1]]
    nodal_i_load = transformed_load * (1.0 - location)
    nodal_j_load = transformed_load * location

    grouping_keys = np.empty(
        n,
        dtype=[
            ("inode_tag", np.int32),
            ("jnode_tag", np.int32),
            ("loadcase", np.int8),
        ])
    grouping_keys["inode_tag"] = inode_tag
    grouping_keys["jnode_tag"] = jnode_tag
    grouping_keys["loadcase"] = loadcase
    unique_grouping_keys, indices = np.unique(
        grouping_keys,
        return_inverse=True,
    )
    total_nodal_i_load = np.zeros(len(unique_grouping_keys), dtype=nodal_i_load.dtype)
    np.add.at(total_nodal_i_load, indices, nodal_i_load)
    total_nodal_j_load = np.zeros(len(unique_grouping_keys), dtype=nodal_j_load.dtype)
    np.add.at(total_nodal_j_load, indices, nodal_j_load)
    result_inode_tag = unique_grouping_keys["inode_tag"]
    result_jnode_tag = unique_grouping_keys["jnode_tag"]
    result_loadcase = unique_grouping_keys["loadcase"]
    result_nodal_i_load = total_nodal_i_load
    result_nodal_j_load = total_nodal_j_load
    return result_inode_tag, result_jnode_tag, result_loadcase, result_nodal_i_load, result_nodal_j_load

def _generate_distributed_element_to_nodal_gravity_loads(nodes, elements, element_tag, loadcase, location, loads):
    n = len(element_tag)
    element_idx = np.fromiter((elements.tag_to_idx(tags=tag)
        for tag in element_tag), dtype=np.int32, count=n)
    element_length = elements.length[element_idx]
    
    # Transform Load to Global axes
    rotation_matrices = elements.rotation_matrices[element_idx]
    transformed_loads = transform_to_global_axes(values=loads, rotation_matrices=rotation_matrices)
    transformed_load = transformed_loads[:, :, 2]

    # Distribute to end nodes
    end_nodes_idx = elements.end_nodes_idx[element_idx]
    inode_tag = nodes.node_tag[end_nodes_idx[:, 0]]
    jnode_tag = nodes.node_tag[end_nodes_idx[:, 1]]
    fraction_length = location[:, 1] - location[:, 0]
    load1 = transformed_load[:, 0]
    load2 = transformed_load[:, 1]
    concentrated_load = (load1 + load2) / 2.0 * fraction_length * element_length
    concentrated_load_location = ((load1 / 2.0) + ((load2 - load1) / 3.0)) / ((load1 + load2) / 2.0) * fraction_length
    nodal_i_load = concentrated_load * (1.0 - concentrated_load_location)
    nodal_j_load = concentrated_load * concentrated_load_location

    grouping_keys = np.empty(
        n,
        dtype=[
            ("inode_tag", np.int32),
            ("jnode_tag", np.int32),
            ("loadcase", np.int8),
        ])
    grouping_keys["inode_tag"] = inode_tag
    grouping_keys["jnode_tag"] = jnode_tag
    grouping_keys["loadcase"] = loadcase
    unique_grouping_keys, indices = np.unique(
        grouping_keys,
        return_inverse=True,
    )
    total_nodal_i_load = np.zeros(len(unique_grouping_keys), dtype=nodal_i_load.dtype)
    np.add.at(total_nodal_i_load, indices, nodal_i_load)
    total_nodal_j_load = np.zeros(len(unique_grouping_keys), dtype=nodal_j_load.dtype)
    np.add.at(total_nodal_j_load, indices, nodal_j_load)
    result_inode_tag = unique_grouping_keys["inode_tag"]
    result_jnode_tag = unique_grouping_keys["jnode_tag"]
    result_loadcase = unique_grouping_keys["loadcase"]
    result_nodal_i_load = total_nodal_i_load
    result_nodal_j_load = total_nodal_j_load
    return result_inode_tag, result_jnode_tag, result_loadcase, result_nodal_i_load, result_nodal_j_load

def _generate_summed_grouping_nodal_loads(node_tag, loadcase, load):
    n = len(node_tag)
    grouping_keys = np.empty(
        n,
        dtype=[
            ("node_tag", np.int32),
            ("loadcase", np.int8),
        ])
    grouping_keys["node_tag"] = node_tag
    grouping_keys["loadcase"] = loadcase
    unique_grouping_keys, indices = np.unique(
        grouping_keys,
        return_inverse=True,
    )
    total_load = np.zeros(len(unique_grouping_keys), dtype=load.dtype)
    np.add.at(total_load, indices, load)
    result_node_tag = unique_grouping_keys["node_tag"]
    result_loadcase = unique_grouping_keys["loadcase"]
    result_load = total_load
    return result_node_tag, result_loadcase, result_load