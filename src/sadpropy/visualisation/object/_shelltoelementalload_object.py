import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from ...preprocessing.preprocessing_class_index import LoadCaseType
from ...utility._exception import ValidationError
from ...utility.helperfunc import transform_to_global_axes

loadcase_type = {
    "Selfweight": LoadCaseType.SW,
    "Dead": LoadCaseType.D,
    "Live": LoadCaseType.L,
    "Live Roof": LoadCaseType.Lr,
    "Earthquake-X": LoadCaseType.Ex,
    "Earthquake-Y": LoadCaseType.Ey,
    "Wind-X": LoadCaseType.Wx,
    "Wind-Y": LoadCaseType.Wy,
}

def _plot_shell_to_elemental_loads(ax, units, coords, elements, shell_to_elemental_loads, loadcase, show_labels, scale=1.0, is_arrow=True, linewidth=0.8):
    def compute_maximum_load():
        # Distributed loads
        dist_loadcase_mask = distributed_loads.loadcase == np.int8(loadcase_type[loadcase.strip().title()])
        dist_element_idx = elements.tag_to_idx(distributed_loads.element_tag[dist_loadcase_mask])
        dist_element_length = elements.length[dist_element_idx]
        dist_location = distributed_loads.location[dist_loadcase_mask] * dist_element_length[:, None]
        dist_location = dist_location[:, 1, None] - dist_location[:, 0, None]
        dist_loads = distributed_loads.loads[dist_loadcase_mask]
        dist_load = (dist_loads[:, 0, None, :] + dist_loads[:, 1, None, :]) / 2.0 * dist_location[:, None]
        dist_load_magnitude = np.linalg.norm(dist_load, axis=2)
        max_dist_load_magnitude = np.nanmax(dist_load_magnitude)

        # Maximum load
        max_load_magnitude = np.maximum(max_dist_load_magnitude, max_conc_load_magnitude)
        max_load_mask = dist_load_magnitude == max_load_magnitude
        max_dist_loads = dist_loads[max_load_mask[:, 0]]
        max_dist_load_magnitude = np.nanmax(np.linalg.norm(max_dist_loads, axis=2))
        return max_dist_load_magnitude

    if loadcase not in loadcase_type:
        raise ValidationError(f"Unknown loadcase: '{loadcase}'. "
            "Choose between 'Selfweight', 'Dead', 'Live', 'Live Roof',"
            "'Earthquake-X', 'Earthquake-Y', 'Wind-X', or 'Wind-Y'")

    if len(shell_to_elemental_loads.element_tag) != 0:
        loadcase_mask = shell_to_elemental_loads.loadcase == np.int8(loadcase_type[loadcase.strip().title()]) # Define loadcase masking
        element_idx = elements.tag_to_idx(shell_to_elemental_loads.element_tag[loadcase_mask]) # Retrieve element index
        end_nodes_idx = elements.end_nodes_idx[element_idx] # Retrieve element end nodes index
        element_length = elements.length[element_idx] # Retrieve element length
        inode = end_nodes_idx[:, 0] # Retrieve element I-end node index
        ni = coords[inode] # Retreive I-node coordinates
        rotation_matrices = elements.rotation_matrices[element_idx]
        loads = shell_to_elemental_loads.loads[loadcase_mask] # Retrieve loads
        n = len(loads) # Define number of loads
        location = shell_to_elemental_loads.location[loadcase_mask] * element_length[:, None] # Compute absolute load location

        # Determine interpolated loads and location
        n_arrows = 8 # Define number of load arrow segment
        arrow_spacing = (element_length / n_arrows).max() # Determine load arrow spacing
        arrow_location = (np.arange(0, n_arrows + 1)[None, :] * arrow_spacing) # Determine load arrow location within the longest element
        load_distance = np.diff(location, axis=1).ravel() # Compute load distance within the element
        valid_distance_mask = arrow_location <= load_distance[:, None] # Mask arrow location is within load distance
        normalised_arrow_location = np.where(valid_distance_mask, arrow_location / load_distance[:, None], 0.0) # Determine normalised arrow location
        interpolated_loads = (loads[:, 0, None, :] + normalised_arrow_location[:, :, None] * (loads[:, 1, None, :] - loads[:, 0, None, :]))
        interpolated_loads = np.where(valid_distance_mask[:, :, None], interpolated_loads, np.nan) # Determine distribution load arrow magnitude
        interpolated_location = (location[:, 0, None] + normalised_arrow_location * load_distance[:, None])
        interpolated_location = np.where(valid_distance_mask, interpolated_location, np.nan) # Determine distribution load arrow location

        # Determine load arrow coordinates
        vector_x = np.tile(np.array([1, 0, 0], dtype=np.int32), (n, 9, 1)) # Define unit vector x-axis in local axes (direction of load distribution)
        global_vector_x = transform_to_global_axes(values=vector_x, rotation_matrices=rotation_matrices) # Determine unit vector x-axis in global axes
        vec_location = global_vector_x * interpolated_location[:, :, None] # Determine vector of load location in global axes
        arrow_coords = ni[:, None, :] + vec_location # Determine start of arrow coordinates

        # Determine load arrow length and vector
        load_magnitude = np.linalg.norm(interpolated_loads, axis=2) # Determine load magnitude
        vector_loads = np.divide(interpolated_loads, load_magnitude[:, :, None], out=np.zeros_like(interpolated_loads), where=load_magnitude[:, :, None] > 0.0) # Determine unit vector of loads in local axes
        global_vector_loads = transform_to_global_axes(values=vector_loads, rotation_matrices=rotation_matrices) # Determine unit vector of loads in global axes
        _, max_load_magnitude = compute_maximum_load()
        normalised_load_magnitude = np.divide(load_magnitude, max_load_magnitude, out=np.zeros_like(load_magnitude), where=max_load_magnitude > 0.0) # Determine normalised load magnitude
        arrow_length = 0.15 * scale * element_length[:, None] * normalised_load_magnitude # Determine scalable arrow length
        global_vector_arrow = global_vector_loads * arrow_length[:, :, None] # Determine vector of arrow in global axes

        # Determine load arrow polygon
        arrow_tip_coords = arrow_coords + np.abs(global_vector_arrow)

        row_idx = np.arange(n)
        last_idx = valid_distance_mask.sum(axis=1) - 1
        polygon_base_start = arrow_coords[row_idx, 0, :]
        polygon_base_end = arrow_coords[row_idx, last_idx, :]
        polygon_tip_start = arrow_tip_coords[row_idx, 0, :]
        polygon_tip_end = arrow_tip_coords[row_idx, last_idx, :]
        polygon_vertices = np.stack((
            polygon_base_start,
            polygon_base_end,
            polygon_tip_end,
            polygon_tip_start,
        ), axis=1)
        ax.add_collection3d(Poly3DCollection(
            polygon_vertices,
            facecolor="None" if is_arrow else "tab:red",
            edgecolor="tab:red",
            alpha=0.20,
            linewidths=linewidth,
            zorder=3,
        ))

        # Plot load arrow
        negative = (np.any(global_vector_loads < 0.0, axis=2) & valid_distance_mask) # Determine negative load direction
        idx_neg, end_neg = np.where(negative) # Determine negative load direction index
        ax.quiver(
            arrow_coords[idx_neg, end_neg, 0], arrow_coords[idx_neg, end_neg, 1], arrow_coords[idx_neg, end_neg, 2],
            global_vector_arrow[idx_neg, end_neg, 0], global_vector_arrow[idx_neg, end_neg, 1], global_vector_arrow[idx_neg, end_neg, 2],
            color="tab:red",
            linewidth=linewidth,
            pivot="tip",
            zorder=3,
        ) # Plot arrow for negative load direction
        positive = (np.any(global_vector_loads > 0, axis=2) & valid_distance_mask) # Determine positive load direction
        idx_pos, end_pos = np.where(positive) # Determine positive load direction index
        ax.quiver(
            arrow_coords[idx_pos, end_pos, 0], arrow_coords[idx_pos, end_pos, 1], arrow_coords[idx_pos, end_pos, 2],
            global_vector_arrow[idx_pos, end_pos, 0], global_vector_arrow[idx_pos, end_pos, 1], global_vector_arrow[idx_pos, end_pos, 2],
            color="tab:red",
            linewidth=linewidth,
            pivot="tail",
            zorder=3,
        ) # Plot arrow for positive load direction

        # Plot load magnitude value
        visualised_load_magnitude_start = units.distributed_lineload(load_magnitude[row_idx, 0]) # Convert load units
        visualised_load_magnitude_end = units.distributed_lineload(load_magnitude[row_idx, last_idx]) # Convert load units
        model_size = np.max(coords.max(axis=0) - coords.min(axis=0))
        offset = 0.005 * model_size # Set label offset
        if show_labels: # Set condition if show_labels is True or False
            for i in range(n):
                ax.text(
                    arrow_tip_coords[i, 0, 0] + offset,
                    arrow_tip_coords[i, 0, 1] + offset,
                    arrow_tip_coords[i, 0, 2] + offset,
                    f"{visualised_load_magnitude_start[i]:.2f}",
                    fontsize=8,
                    color="black",
                    ha="center",
                    zorder=3,
                )
                ax.text(
                    arrow_tip_coords[i, last_idx[i], 0] + offset,
                    arrow_tip_coords[i, last_idx[i], 1] + offset,
                    arrow_tip_coords[i, last_idx[i], 2] + offset,
                    f"{visualised_load_magnitude_end[i]:.2f}",
                    fontsize=8,
                    color="black",
                    ha="center",
                    zorder=3,
                )