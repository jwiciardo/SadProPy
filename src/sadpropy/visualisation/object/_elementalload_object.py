import numpy as np
from ...utility.helperfunc import transform_to_global_axes

def _plot_distributed_elemental_loads(ax, loads, elements, nodes, arrow_scale=0.5, n_arrows=5, colour="red", linewidth=1.0):
    # ============================================================
    # Load data
    # ============================================================

    element_tags = loads.element_tag
    locations = loads.location
    local_loads = loads.loads

    n_loads = len(element_tags)
    if n_loads == 0:
        return

    # ============================================================
    # Find element indices
    # ============================================================
    element_indices = np.asarray([
        np.flatnonzero(elements.element_tag == tag)[0]
        for tag in element_tags],
        dtype=np.int32,
    )

    # ============================================================
    # Element node indices
    # ============================================================

    element_nodes = elements.end_nodes_idx[element_indices]
    node_i = element_nodes[:, 0]
    node_j = element_nodes[:, 1]

    # ============================================================
    # Node coordinates
    # ============================================================

    coord_i = nodes.coords[node_i]
    coord_j = nodes.coords[node_j]

    # ============================================================
    # Element geometry
    # ============================================================

    element_vector = coord_j - coord_i
    element_length = np.linalg.norm(element_vector, axis=1)

    # Avoid division by zero
    valid = element_length > 0.0

    if not np.all(valid):
        element_indices = element_indices[valid]
        coord_i = coord_i[valid]
        coord_j = coord_j[valid]
        element_vector = element_vector[valid]
        element_length = element_length[valid]
        locations = locations[valid]
        local_loads = local_loads[valid]

    element_axis = (element_vector / element_length[:, np.newaxis])

    # ============================================================
    # Element rotation matrices
    # ============================================================

    rotation_matrices = (elements.rotation_matrices[element_indices])

    # ============================================================
    # Generate normalized positions along loaded length
    # ============================================================

    xi = np.linspace(0.0, 1.0, n_arrows, dtype=np.float64)

    # ============================================================
    # Determine actual positions along each element
    # ============================================================

    # locations is assumed to contain normalized positions:
    #
    #     [0.0, 1.0] -> entire element
    #
    # Therefore convert normalized position to actual distance.

    start_location = locations[:, 0]
    end_location = locations[:, 1]

    positions = (start_location[:, np.newaxis] + (end_location - start_location)[:, np.newaxis] * xi[np.newaxis, :])
    positions *= element_length[:, np.newaxis]

    # ============================================================
    # Global coordinates of load arrows
    # ============================================================

    points = (coord_i[:, np.newaxis, :] + element_axis[:, np.newaxis, :] * positions[:, :, np.newaxis])

    # ============================================================
    # Interpolate local load along element
    # ============================================================

    local_load_start = local_loads[:, 0, :]
    local_load_end = local_loads[:, 1, :]

    interpolation = xi[np.newaxis, :, np.newaxis]

    local_load_vectors = (local_load_start[:, np.newaxis, :] + (local_load_end - local_load_start)[:, np.newaxis, :] * interpolation)

    # ============================================================
    # Transform local load -> global load
    # ============================================================

    #
    # rotation_matrices:
    #
    #     (N, 3, 3)
    #
    # local_load_vectors:
    #
    #     (N, n_arrows, 3)
    #
    # Result:
    #
    #     (N, n_arrows, 3)
    #

    global_load_vectors = np.einsum(
        "nij,nkj->nki",
        rotation_matrices,
        local_load_vectors,
    )

    # ============================================================
    # Plot load arrows
    # ============================================================

    for i in range(len(points)):

        for j in range(n_arrows):

            point = points[i, j]

            load_vector = global_load_vectors[i, j]

            magnitude = np.linalg.norm(
                load_vector
            )

            # Skip zero load
            if magnitude == 0.0:
                continue

            direction = (
                load_vector
                / magnitude
            )

            arrow_vector = (
                direction
                * arrow_scale
            )

            ax.quiver(
                point[0],
                point[1],
                point[2],
                arrow_vector[0],
                arrow_vector[1],
                arrow_vector[2],
                color=colour,
                linewidth=linewidth,
                arrow_length_ratio=0.25,
                normalize=False,
                zorder=20,
            )

def _plot_elemental_loads(ax, units, coords, elements, distributed_loads, concentrated_loads, rotation_matrices, show_labels, scale=1.0, colour="red", linewidth=1.2):
    # Concentrated loads
    element_idx = elements.tag_to_idx(concentrated_loads.element_tag) # Retrieve element index
    end_nodes_idx = elements.end_nodes_idx[element_idx] # Retrieve element end nodes index
    element_length = elements.length[element_idx] # Retrieve element length
    inode = end_nodes_idx[:, 0] # Retrieve element I-end node index
    ni = coords[inode] # Retreive I-node coordinates
    rotation_matrices = elements.rotation_matrices[element_idx]
    loads = concentrated_loads.loads # Retrieve loads
    n = len(loads) # Define number of loads
    vector_loads = np.divide(loads, np.linalg.norm(loads, axis=1, keepdims=True), out=np.zeros_like(loads), where=np.linalg.norm(loads, axis=1, keepdims=True) > 0.0) # Determine unit vector of loads in local axes
    global_vector_loads = transform_to_global_axes(values=vector_loads, rotation_matrices=rotation_matrices) # Determine unit vector of loads in global axes
    flatten_load_magnitude = np.linalg.norm(loads, axis=1) # Determine flatten load magnitude
    normalised_load_magnitude = flatten_load_magnitude / np.max(flatten_load_magnitude) # Determine normalised flatten load magnitude
    location = concentrated_loads.location * element_length # Compute absolute load location
    vector_x = np.tile(np.array([1, 0, 0], dtype=np.int32), (n, 1)) # Define unit vector x-axis in local axes (direction of load distribution)
    global_vector_x = transform_to_global_axes(values=vector_x, rotation_matrices=rotation_matrices) # Determine unit vector x-axis in global axes
    vec_location = global_vector_x * location[:, None] # Determine vector of load location in global axes
    arrow_coords = ni + vec_location # Determine start of arrow coordinates
    arrow_length = 0.2 * scale * element_length * normalised_load_magnitude # Determine scalable arrow length
    global_vector_arrow = global_vector_loads * arrow_length[:, None] # Determine vector of arrow in global axes

    negative = np.any(global_vector_loads < 0, axis=1) # Determine negative load direction
    idx_negative = np.where(negative)[0] # Determine negative load direction index
    ax.quiver(
        arrow_coords[idx_negative, 0], arrow_coords[idx_negative, 1], arrow_coords[idx_negative, 2],
        global_vector_arrow[idx_negative, 0], global_vector_arrow[idx_negative, 1], global_vector_arrow[idx_negative, 2],
        color=colour,
        linewidth=linewidth,
        pivot="tip",
        zorder=10,
    ) # Plot arrow for negative load direction
    positive = np.any(global_vector_loads > 0, axis=1) # Determine positive load direction
    idx_positive = np.where(positive)[0] # Determine positive load direction index
    ax.quiver(
        arrow_coords[idx_positive, 0], arrow_coords[idx_positive, 1], arrow_coords[idx_positive, 2],
        global_vector_arrow[idx_positive, 0], global_vector_arrow[idx_positive, 1], global_vector_arrow[idx_positive, 2],
        color=colour,
        linewidth=linewidth,
        pivot="tail",
        zorder=10,
    ) # Plot arrow for positive load direction
    visualised_load_magnitude = units.concentrated_lineload(flatten_load_magnitude) # Convert load units
    model_size = np.max(coords.max(axis=0) - coords.min(axis=0))
    offset = 0.005 * model_size # Set label offset
    coords_pos = arrow_coords + global_vector_arrow + offset
    coords_neg = arrow_coords - global_vector_arrow + offset
    if show_labels: # Set condition if show_labels is True or False
        for i in idx_negative:
            ax.text(
                coords_neg[i, 0],
                coords_neg[i, 1],
                coords_neg[i, 2],
                f"{visualised_load_magnitude[i]:.2f}",
                fontsize=8,
                color="black",
                zorder=10,
            )
        for i in idx_positive:
            ax.text(
                coords_pos[i, 0],
                coords_pos[i, 1],
                coords_pos[i, 2],
                f"{visualised_load_magnitude[i]:.2f}",
                fontsize=8,
                color="black",
                zorder=10,
            )
    print()
    print()