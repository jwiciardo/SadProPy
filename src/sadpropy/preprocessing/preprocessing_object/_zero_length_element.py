import numpy as np
from ..preprocessing_class_index import ConnectionEnd

def _generate_zerolength_element_local_axes(ndim, elements, child_nodes):
    n = len(child_nodes)
    rotation_matrices = np.zeros((n, ndim, ndim), dtype=np.float64)
    for node_idx, child_node in enumerate(child_nodes):
        mask = np.any(elements.end_nodes_idx == child_node, axis=1)
        if not np.any(mask):
            continue
        ele_idx = np.flatnonzero(mask)[0]
        rotation = elements.rotation_matrices[ele_idx].copy()
        iend_node_idx = elements.end_nodes_idx[ele_idx][ConnectionEnd.I_End]
        if child_node != iend_node_idx:
            rotation[:, 0] *= -1
        rotation_matrices[node_idx] = rotation
    return rotation_matrices