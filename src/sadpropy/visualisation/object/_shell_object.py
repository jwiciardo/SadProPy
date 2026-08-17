import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def _plot_shells(ax, coords, shells, show_labels, colour="gray", alpha=0.3):
    model_size = np.max(coords.max(axis=0) - coords.min(axis=0))
    offset = 0.02 * model_size # Set label offset
    for i, node_idx in enumerate(shells.nodes_idx):
        vertices = coords[node_idx]
        ax.add_collection3d(Poly3DCollection(
            [vertices],
            facecolor=colour,
            edgecolor=colour,
            linewidth=1.0,
            alpha=alpha,
            zorder=2,
        ))
        if show_labels:
            c = vertices.mean(axis=0)
            ax.text(
                c[0],
                c[1],
                c[2] + offset,
                shells.unique_name[i],
                fontsize=8,
                color="black",
                zorder=2,
            ) # Plot shells labels