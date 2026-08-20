import numpy as np
from ...utility.tolerance import Tolerance

def _plot_nodes(ax, view_info, nodes, coords, projection_coords, plane, show_labels, marker="o", markersize=10, colour="black"):
    if view_info["projection"] == "3d":
        ax.scatter(
            coords[:, 0],
            coords[:, 1],
            coords[:, 2],
            s=markersize,
            c=colour,
            marker=marker,
            depthshade=True,
            zorder=2,
        ) # Plot nodes

        if show_labels: # Set condition if show_labels is True or False
            model_size = np.max(np.max(coords, axis=0) - np.min(coords, axis=0))
            offset = 0.005 * model_size # Set label offset
            for i in nodes.index: # Loop over nodes index
                n = coords[i]
                ax.text(
                    n[0] + offset,
                    n[1] + offset,
                    n[2] + offset,
                    nodes.unique_name[i],
                    fontsize=8,
                    color="black",
                    ha="left",
                    va="bottom",
                    zorder=2,
                ) # Plot nodes labels
    else:
        if plane is None:
            plane = 1 # Define default plane for plotting
        perpendicular_idx = view_info["perpendicular"]
        planes_coord = np.unique(coords[:, perpendicular_idx]) # Determine planes coordinate
        plane_coord = planes_coord[plane - 1] # Determine plane coordinate
        plane_mask = np.isclose(
            coords[:, perpendicular_idx],
            plane_coord,
            atol=Tolerance.LENGTH,
            rtol=0.0,
        )
        coords = projection_coords[plane_mask]
        nodes_idx = nodes.index
        nodes_idx = nodes_idx[plane_mask]
        ax.scatter(
            coords[:, 0],
            coords[:, 1],
            s=markersize,
            c=colour,
            marker=marker,
            zorder=2,
        ) # Plot nodes

        if show_labels: # Set condition if show_labels is True or False
            model_size = np.max(np.max(coords, axis=0) - np.min(coords, axis=0))
            offset = 0.005 * model_size # Set label offset
            for i, node_idx in enumerate(nodes_idx): # Loop over nodes index
                n = coords[i]
                ax.text(
                    n[0] + offset,
                    n[1] + offset,
                    nodes.unique_name[node_idx],
                    fontsize=8,
                    color="black",
                    ha="left",
                    va="bottom",
                    zorder=2,
                ) # Plot nodes labels
