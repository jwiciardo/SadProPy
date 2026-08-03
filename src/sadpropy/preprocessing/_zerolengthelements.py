import numpy as np
from ._preproc_class import ConnectionEnd

def zerolength_element_direction(nodes, elements_list, child_nodes):
    n = len(child_nodes)
    vec_dir = np.zeros((n, 3), dtype=np.float64)
    for node_idx, child_node in enumerate(child_nodes):
        for elements in elements_list:
            mask = np.any(elements.end_nodes_idx == child_node, axis=1)
            if not np.any(mask):
                continue
            ele_idx = np.flatnonzero(mask)[0]
            iend_node_idx = elements.end_nodes_idx[ele_idx][ConnectionEnd.I_End]
            jend_node_idx = elements.end_nodes_idx[ele_idx][ConnectionEnd.J_End]
            if child_node == iend_node_idx:
                vec = nodes.coords[jend_node_idx] - nodes.coords[iend_node_idx]
            else:
                vec = nodes.coords[iend_node_idx] - nodes.coords[jend_node_idx]
            vec /= np.linalg.norm(vec)
            vec_dir[node_idx] = vec
            break
    return vec_dir