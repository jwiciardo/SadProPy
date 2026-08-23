import numpy as np

def _get_storey_nodes(nodes, elevation):
    storey_nodes_idx = []
    for i, elev in enumerate(elevation):
        mask = np.isclose(nodes.coords[:, 2], elev)
        nodes_idx = nodes.index[mask]
        storey_nodes_idx.append(nodes_idx)
    constrained_node_idx = np.array(storey_nodes_idx, dtype=np.int32)
    return constrained_node_idx
