import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from ...utility.units import ConverterFromInternalUnits, ConverterToInternalUnits
from ...utility.exception import warningtext

def _plot_nodal_loads(ax, units, nodes, coords, nodal_loads, loadcase, loadcase_type, scale, show_labels, linewidth=0.8):
    from_internalunits = ConverterFromInternalUnits(units=units)
    to_internalunits = ConverterToInternalUnits(units=units)

    loadcase_mask = nodal_loads.loadcase == np.int8(loadcase_type[loadcase.strip().title()]) # Define loadcase masking
    node_idx = nodes.tag_to_idx(nodal_loads.node_tag[loadcase_mask]) # Retrieve element index
    if len(node_idx) != 0:
        node_coords = coords[node_idx] # Retreive node coordinates
        loads = nodal_loads.loads[loadcase_mask] # Retrieve loads
        n = len(loads) # Define number of loads
        forces = loads[:, :3] # Get forces data
        moments = loads[:, 3:6] # Get moments data

        force_magnitude = np.absolute(forces)
        vector_forces = np.divide(forces, force_magnitude, out=np.zeros_like(forces), where=force_magnitude > 0.0) # Determine unit vector of forces
        default_force_magnitude = to_internalunits.force_pointload(values=75)
        normalised_force_magnitude = np.divide(force_magnitude, default_force_magnitude, out=np.zeros_like(force_magnitude), where=default_force_magnitude > 0.0) # Determine normalised force magnitude
        arrow_length = scale * normalised_force_magnitude # Determine scalable arrow length
        vector_arrow = vector_forces * arrow_length # Determine vector of arrow
        arrow_tip_coords = node_coords - vector_arrow

        # Plot load arrow
        X_mask = vector_forces[:, 0] != 0.0 # Mask X-axis force direction
        X_idx = np.where(X_mask)[0] # Determine X-axis force direction index
        ax.quiver(
            node_coords[X_idx, 0], node_coords[X_idx, 1], node_coords[X_idx, 2],
            vector_arrow[X_idx, 0], 0.0, 0.0,
            color="red",
            linewidth=linewidth,
            pivot="tip",
            zorder=5,
        ) # Plot arrow for X-axis load direction
        Y_mask = vector_forces[:, 1] != 0.0 # Mask Y-axis force direction
        Y_idx = np.where(Y_mask)[0] # Determine Y-axis force direction index
        ax.quiver(
            node_coords[Y_idx, 0], node_coords[Y_idx, 1], node_coords[Y_idx, 2],
            0.0, vector_arrow[Y_idx, 1], 0.0,
            color="red",
            linewidth=linewidth,
            pivot="tip",
            zorder=5,
        ) # Plot arrow for Y-axis load direction
        Z_mask = vector_forces[:, 2] != 0.0 # Mask Z-axis force direction
        Z_idx = np.where(Z_mask)[0] # Determine Z-axis force direction index
        ax.quiver(
            node_coords[Z_idx, 0], node_coords[Z_idx, 1], node_coords[Z_idx, 2],
            0.0, 0.0, vector_arrow[Z_idx, 2],
            color="red",
            linewidth=linewidth,
            pivot="tip",
            zorder=5,
        ) # Plot arrow for Z-axis load direction

        # Plot load magnitude value
        visualised_force_magnitude = from_internalunits.force_pointload(force_magnitude) # Convert force units
        model_size = np.max(coords.max(axis=0) - coords.min(axis=0))
        offset = 0.005 * model_size # Set label offset
        if show_labels: # Set condition if show_labels is True or False
            for i in X_idx:
                ax.text(
                    node_coords[i, 0] - vector_arrow[i, 0] - offset,
                    node_coords[i, 1],
                    node_coords[i, 2] + offset,
                    f"{visualised_force_magnitude[i, 0]:.2f}",
                    fontsize=8,
                    color="black",
                    ha="center",
                    zorder=5,
                )
            for i in Y_idx:
                ax.text(
                    node_coords[i, 0],
                    node_coords[i, 1] - vector_arrow[i, 1] - offset,
                    node_coords[i, 2] + offset,
                    f"{visualised_force_magnitude[i, 1]:.2f}",
                    fontsize=8,
                    color="black",
                    ha="center",
                    zorder=5,
                )
            for i in Z_idx:
                ax.text(
                    node_coords[i, 0],
                    node_coords[i, 1],
                    node_coords[i, 2] - vector_arrow[i, 2] - offset,
                    f"{visualised_force_magnitude[i, 2]:.2f}",
                    fontsize=8,
                    color="black",
                    ha="center",
                    zorder=5,
                )




        
            
    
        