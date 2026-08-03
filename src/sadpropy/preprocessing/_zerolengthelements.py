import numpy as np
from ._preproc_class import ConnectionEnd

def generate_zerolength_element_local_axes(ndim, elements_list, child_nodes):
    n = len(child_nodes)
    rotation_matrix = np.empty((n, 3, 3), dtype=np.float64) if ndim == 3 else np.empty((n, 2, 2), dtype=np.float64)
    for node_idx, child_node in enumerate(child_nodes):
        for elements in elements_list:
            mask = np.any(elements.end_nodes_idx == child_node, axis=1)
            if not np.any(mask):
                continue
            ele_idx = np.flatnonzero(mask)[0]
            iend_node_idx = elements.end_nodes_idx[ele_idx][ConnectionEnd.I_End]
            rotation_matrix[node_idx] = elements.rotation_matrix[ele_idx]
            if child_node != iend_node_idx:
                rotation_matrix[node_idx][:, 0] *= -1
            break
    return rotation_matrix