import numpy as np
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

def _plot_elemental_loads(ax, units, coords, elements, distributed_loads, concentrated_loads, loadcase, show_labels, scale=1.0, colour="red", linewidth=1.0):
    def plot_concentrated_loads():
        loadcase_mask = concentrated_loads.loadcase == np.int8(loadcase_type[loadcase.strip().title()]) # Define loadcase masking
        element_idx = elements.tag_to_idx(concentrated_loads.element_tag[loadcase_mask]) # Retrieve element index
        end_nodes_idx = elements.end_nodes_idx[element_idx] # Retrieve element end nodes index
        element_length = elements.length[element_idx] # Retrieve element length
        inode = end_nodes_idx[:, 0] # Retrieve element I-end node index
        ni = coords[inode] # Retreive I-node coordinates
        rotation_matrices = elements.rotation_matrices[element_idx]
        loads = concentrated_loads.loads[loadcase_mask] # Retrieve loads
        n = len(loads) # Define number of loads

        # Determine load arrow coordinates
        location = concentrated_loads.location[loadcase_mask] * element_length # Compute absolute load location
        vector_x = np.tile(np.array([1, 0, 0], dtype=np.int32), (n, 1)) # Define unit vector x-axis in local axes (direction of load distribution)
        global_vector_x = transform_to_global_axes(values=vector_x, rotation_matrices=rotation_matrices) # Determine unit vector x-axis in global axes
        vec_location = global_vector_x * location[:, None] # Determine vector of load location in global axes
        arrow_coords = ni + vec_location # Determine start of arrow coordinates

        # Determine load arrow length and vector
        vector_loads = np.divide(loads, np.linalg.norm(loads, axis=1, keepdims=True), out=np.zeros_like(loads), where=np.linalg.norm(loads, axis=1, keepdims=True) > 0.0) # Determine unit vector of loads in local axes
        global_vector_loads = transform_to_global_axes(values=vector_loads, rotation_matrices=rotation_matrices) # Determine unit vector of loads in global axes
        flatten_load_magnitude = np.linalg.norm(loads, axis=1) # Determine flatten load magnitude
        normalised_load_magnitude = flatten_load_magnitude / np.max(flatten_load_magnitude) # Determine normalised flatten load magnitude
        arrow_length = 0.2 * scale * element_length * normalised_load_magnitude # Determine scalable arrow length
        global_vector_arrow = global_vector_loads * arrow_length[:, None] # Determine vector of arrow in global axes

        # Plot load arrow
        negative = np.any(global_vector_loads < 0, axis=1) # Determine negative load direction
        idx_neg = np.where(negative)[0] # Determine negative load direction index
        ax.quiver(
            arrow_coords[idx_neg, 0], arrow_coords[idx_neg, 1], arrow_coords[idx_neg, 2],
            global_vector_arrow[idx_neg, 0], global_vector_arrow[idx_neg, 1], global_vector_arrow[idx_neg, 2],
            color=colour,
            linewidth=linewidth,
            pivot="tip",
            zorder=3,
        ) # Plot arrow for negative load direction
        positive = np.any(global_vector_loads > 0, axis=1) # Determine positive load direction
        idx_pos = np.where(positive)[0] # Determine positive load direction index
        ax.quiver(
            arrow_coords[idx_pos, 0], arrow_coords[idx_pos, 1], arrow_coords[idx_pos, 2],
            global_vector_arrow[idx_pos, 0], global_vector_arrow[idx_pos, 1], global_vector_arrow[idx_pos, 2],
            color=colour,
            linewidth=linewidth,
            pivot="tail",
            zorder=3,
        ) # Plot arrow for positive load direction

        # Plot load magnitude value
        visualised_load_magnitude = units.concentrated_lineload(flatten_load_magnitude) # Convert load units
        model_size = np.max(coords.max(axis=0) - coords.min(axis=0))
        offset = 0.005 * model_size # Set label offset
        coords_pos = arrow_coords + global_vector_arrow + offset
        coords_neg = arrow_coords - global_vector_arrow + offset
        if show_labels: # Set condition if show_labels is True or False
            for i in idx_neg:
                ax.text(
                    coords_neg[i, 0],
                    coords_neg[i, 1],
                    coords_neg[i, 2],
                    f"{visualised_load_magnitude[i]:.2f}",
                    fontsize=8,
                    color="black",
                    ha="center",
                    zorder=3,
                )
            for i in idx_pos:
                ax.text(
                    coords_pos[i, 0],
                    coords_pos[i, 1],
                    coords_pos[i, 2],
                    f"{visualised_load_magnitude[i]:.2f}",
                    fontsize=8,
                    color="black",
                    ha="center",
                    zorder=3,
                )

    def plot_distributed_loads():
        loadcase_mask = distributed_loads.loadcase == np.int8(loadcase_type[loadcase.strip().title()]) # Define loadcase masking
        element_idx = elements.tag_to_idx(distributed_loads.element_tag[loadcase_mask]) # Retrieve element index
        end_nodes_idx = elements.end_nodes_idx[element_idx] # Retrieve element end nodes index
        element_length = elements.length[element_idx] # Retrieve element length
        inode = end_nodes_idx[:, 0] # Retrieve element I-end node index
        jnode = end_nodes_idx[:, 1] # Retrieve element J-end node index
        ni = coords[inode] # Retreive I-node coordinates
        nj = coords[jnode] # Retreive J-node coordinates
        rotation_matrices = elements.rotation_matrices[element_idx]
        loads = distributed_loads.loads[loadcase_mask] # Retrieve loads
        n = len(loads) # Define number of loads

        n_arrows = 8 # Number of load arrow segment
        t = np.linspace(0.0, 1.0, n_arrows)

        arrow_spacing = (element_length / n_arrows).max()
        arrow_distance = (np.arange(0, n_arrows + 1)[None, :] * arrow_spacing)
        arrow_distance = np.broadcast_to(arrow_distance, (n, n_arrows))
        valid = arrow_distance <= element_length[:, None]
        t = np.where(
            valid,
            arrow_distance / element_length[:, None],
            0.0,
        )
        interpolated_loads = (
            loads[:, 0, None, :] * (1.0 - t[:, :, None])
            + loads[:, 1, None, :] * t[:, :, None]
        )

        print(t)
        print(interpolated_loads)



        # Determine load arrow coordinates
        location = distributed_loads.location[loadcase_mask] * element_length[:, None] # Compute absolute load location
        vector_x = np.tile(np.array([1, 0, 0], dtype=np.int32), (n, 2, 1)) # Define unit vector x-axis in local axes (direction of load distribution)
        global_vector_x = transform_to_global_axes(values=vector_x, rotation_matrices=rotation_matrices) # Determine unit vector x-axis in global axes
        vec_location = global_vector_x * location[:, :, None] # Determine vector of load location in global axes
        arrow_coords = ni[:, None, :] + vec_location # Determine start of arrow coordinates

        # Determine load arrow length and vector
        vector_loads = np.divide(loads, np.linalg.norm(loads, axis=2, keepdims=True), out=np.zeros_like(loads), where=np.linalg.norm(loads, axis=2, keepdims=True) > 0.0) # Determine unit vector of loads in local axes
        global_vector_loads = transform_to_global_axes(values=vector_loads, rotation_matrices=rotation_matrices) # Determine unit vector of loads in global axes
        flatten_load_magnitude = np.linalg.norm(loads, axis=2) # Determine flatten load magnitude
        normalised_load_magnitude = flatten_load_magnitude / np.max(flatten_load_magnitude) # Determine normalised flatten load magnitude
        arrow_length = 0.1 * scale * element_length[:, None] * normalised_load_magnitude # Determine scalable arrow length
        global_vector_arrow = global_vector_loads * arrow_length[:, :, None] # Determine vector of arrow in global axes

        # Plot load arrow
        negative = np.any(global_vector_loads < 0, axis=2) # Determine negative load direction
        idx_neg, end_neg = np.where(negative) # Determine negative load direction index
        ax.quiver(
            arrow_coords[idx_neg, end_neg, 0], arrow_coords[idx_neg, end_neg, 1], arrow_coords[idx_neg, end_neg, 2],
            global_vector_arrow[idx_neg, end_neg, 0], global_vector_arrow[idx_neg, end_neg, 1], global_vector_arrow[idx_neg, end_neg, 2],
            color=colour,
            linewidth=linewidth,
            pivot="tip",
            zorder=3,
        ) # Plot arrow for negative load direction
        # Plot load arrow
        positive = np.any(global_vector_loads > 0, axis=2) # Determine positive load direction
        idx_pos, end_pos = np.where(positive) # Determine positive load direction index
        ax.quiver(
            arrow_coords[idx_pos, end_pos, 0], arrow_coords[idx_pos, end_pos, 1], arrow_coords[idx_pos, end_pos, 2],
            global_vector_arrow[idx_pos, end_pos, 0], global_vector_arrow[idx_pos, end_pos, 1], global_vector_arrow[idx_pos, end_pos, 2],
            color=colour,
            linewidth=linewidth,
            pivot="tail",
            zorder=3,
        ) # Plot arrow for positive load direction




    if loadcase not in loadcase_type:
        raise ValidationError(f"Unknown loadcase: '{loadcase}'. "
            "Choose between 'Selfweight', 'Dead', 'Live', 'Live Roof',"
            "'Earthquake-X', 'Earthquake-Y', 'Wind-X', or 'Wind-Y'")
    if len(concentrated_loads.element_tag) != 0:
        plot_concentrated_loads()
    if len(distributed_loads.element_tag) != 0:
        plot_distributed_loads()
    

