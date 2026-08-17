import numpy as np


def _get_load_direction_vector(load_direction, rotation_matrices):
    """
    Return load direction as a global vector.

    Supported directions:
        Global X / X
        Global Y / Y
        Global Z / Z
        Local X
        Local Y
        Local Z
    """

    direction = str(load_direction).strip().title()

    global_directions = {
        "X": np.array([1.0, 0.0, 0.0]),
        "Y": np.array([0.0, 1.0, 0.0]),
        "Z": np.array([0.0, 0.0, 1.0]),
        "Global X": np.array([1.0, 0.0, 0.0]),
        "Global Y": np.array([0.0, 1.0, 0.0]),
        "Global Z": np.array([0.0, 0.0, 1.0]),
    }

    local_directions = {
        "Local X": np.array([1.0, 0.0, 0.0]),
        "Local Y": np.array([0.0, 1.0, 0.0]),
        "Local Z": np.array([0.0, 0.0, 1.0]),
    }

    if direction in global_directions:
        return global_directions[direction]

    if direction in local_directions:
        return rotation_matrix @ local_directions[direction]

    raise ValueError(
        f"Unknown load direction '{load_direction}'."
    )


def _plot_load_arrow(ax, coords, elements, position, direction, magnitude, arrow_scale, colour="red", linewidth=1.2):
    direction = np.asarray(
        direction,
        dtype=np.float64,
    )

    magnitude = float(magnitude)

    norm = np.linalg.norm(direction)

    if norm == 0.0 or magnitude == 0.0:
        return

    direction = direction / norm

    vector = (
        direction
        * np.sign(magnitude)
        * arrow_scale
    )

    ax.quiver(
        position[0],
        position[1],
        position[2],
        vector[0],
        vector[1],
        vector[2],
        color=colour,
        linewidth=linewidth,
        arrow_length_ratio=0.25,
        normalize=False,
        zorder=20,
    )


def _plot_uniform_line_loads(
    ax,
    line_name,
    loadcase_type,
    load_direction,
    location,
    load,
    line_objects,
    coords,
    rotation_matrices,
    arrow_scale,
    colour="red",
    linewidth=1.2,
    n_arrows=5,
):
    """
    Plot uniform/distributed line loads.

    Parameters
    ----------
    location : (N, 2)
        Start and end location along element.
    load : (N, 2)
        Load at start and end location.
    """

    name_to_index = line_objects["Name to Index"]

    for i in range(len(line_name)):

        element_index = name_to_index[line_name[i]]

        element_nodes = line_objects["Nodes"][element_index]

        node_i = element_nodes[0]
        node_j = element_nodes[1]

        coord_i = coords[node_i]
        coord_j = coords[node_j]

        rotation_matrix = rotation_matrices[element_index]

        length = np.linalg.norm(
            coord_j - coord_i
        )

        if length == 0.0:
            continue

        start = location[i, 0]
        end = location[i, 1]

        # Uniform load locations can contain NaN.
        if np.isnan(start):
            start = 0.0

        if np.isnan(end):
            end = length

        # Generate arrow locations
        positions = np.linspace(
            start,
            end,
            n_arrows,
        )

        # Interpolate load values
        load_values = np.interp(
            positions,
            location[i],
            load[i],
        )

        # Handle NaN location/load safely
        if np.any(np.isnan(load_values)):
            load_values = np.full(
                n_arrows,
                np.nanmean(load[i]),
            )

        direction = _get_load_direction_vector(
            load_direction[i],
            rotation_matrix,
        )

        # Element local x direction
        element_axis = (
            coord_j - coord_i
        ) / length

        for position, load_value in zip(
            positions,
            load_values,
        ):
            point = (
                coord_i
                + element_axis * position
            )

            _plot_load_arrow(
                ax=ax,
                position=point,
                direction=direction,
                magnitude=load_value,
                arrow_scale=arrow_scale,
                colour=colour,
                linewidth=linewidth,
            )


def _plot_concentrated_line_loads(
    ax,
    line_name,
    loadcase_type,
    load_direction,
    location,
    load,
    line_objects,
    coords,
    rotation_matrices,
    arrow_scale,
    colour="red",
    linewidth=1.2,
):
    """
    Plot concentrated loads applied to line elements.
    """

    name_to_index = line_objects["Name to Index"]

    for i in range(len(line_name)):

        element_index = name_to_index[line_name[i]]

        element_nodes = line_objects["Nodes"][element_index]

        node_i = element_nodes[0]
        node_j = element_nodes[1]

        coord_i = coords[node_i]
        coord_j = coords[node_j]

        rotation_matrix = rotation_matrices[element_index]

        length = np.linalg.norm(
            coord_j - coord_i
        )

        if length == 0.0:
            continue

        element_axis = (
            coord_j - coord_i
        ) / length

        position = location[i]

        point = (
            coord_i
            + element_axis * position
        )

        direction = _get_load_direction_vector(
            load_direction[i],
            rotation_matrix,
        )

        _plot_load_arrow(
            ax=ax,
            position=point,
            direction=direction,
            magnitude=load[i],
            arrow_scale=arrow_scale,
            colour=colour,
            linewidth=linewidth,
        )


def _plot_elemental_loads(ax, coords, elements, distributed_loads, concentrated_loads, rotation_matrices, show_labels, scale=1.0, colour="red", linewidth=1.2):
    return 0