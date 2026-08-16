import numpy as np

def _plot_nodes(ax, nodes, coords, show_labels, marker="o", markersize=10, colour="black"):
    ax.scatter(
        coords[:, 0],
        coords[:, 1],
        coords[:, 2],
        s=markersize,
        c=colour,
        marker=marker,
        depthshade=True,
        zorder=1,
    ) # Plot nodes

    if show_labels: # Set condition if show_labels is True or False
        model_size = np.max(coords.max(axis=0) - coords.min(axis=0))
        offset = 0.005 * model_size # Set label offset
        for i in nodes.index: # Loop over nodes index
            p = coords[i]
            ax.text(
                p[0] + offset,
                p[1] + offset,
                p[2] + offset,
                nodes.unique_name[i],
                fontsize=8,
                color="black",
                ha="left",
                va="bottom",
                zorder=1,
            ) # Plot nodes labels
