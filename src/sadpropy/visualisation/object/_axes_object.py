import numpy as np

def _set_axes(ax, view_info, coords):
    ax.axis('off')
    mins = coords.min(axis=0) # Determine minimum limit of the model
    maxs = coords.max(axis=0) # Determine maximum limit of the model
    if view_info["projection"] == "3d":
        ax.set_box_aspect((
            maxs[0] - mins[0],
            maxs[1] - mins[1],
            maxs[2] - mins[2],
        )) # Set box aspect ratio
    else:
        ax.set_aspect("equal", adjustable="box")

def _draw_global_axes(ax, view_info, coords, linewidth=1.2):
    model_size = np.max(coords.max(axis=0) - coords.min(axis=0)) # Determine model size
    arrow_length = model_size * 0.05 # Set arrow length
    ox, oy, oz = (0.0, 0.0, 0.0) # Set original point
    if view_info["projection"] == "3d":
        # Plot arrow
        ax.quiver(
            ox, oy, oz,
            arrow_length, 0, 0,
            color="red",
            linewidth=linewidth,
            zorder=10,
        ) # Plot X-axis arrow
        ax.quiver(
            ox, oy, oz,
            0, arrow_length, 0,
            color="green",
            linewidth=linewidth,
            zorder=10,
        ) # Plot Y-axis arrow
        ax.quiver(
            ox, oy, oz,
            0, 0, arrow_length,
            color="blue",
            linewidth=linewidth,
            zorder=10,
        ) # Plot Z-axis arrow

        # Plot text
        ax.text(
            ox + arrow_length,
            oy,
            oz,
            "X",
            color="red",
            fontsize=10,
            weight="bold",
            zorder=10,
        ) # Plot X-axis label
        ax.text(
            ox,
            oy + arrow_length,
            oz,
            "Y",
            color="green",
            fontsize=10,
            weight="bold",
            zorder=10,
        ) # Plot Y-axis label
        ax.text(
            ox,
            oy,
            oz + arrow_length,
            "Z",
            color="blue",
            fontsize=10,
            weight="bold",
            zorder=10,
        ) # Plot Z-axis label
    else:
        # Plot arrow
        ax.quiver(
            ox, oy,
            arrow_length, 0,
            color="red",
            linewidth=linewidth,
            zorder=10,
        ) # Plot horizontal axis arrow
        ax.quiver(
            ox, oy,
            0, arrow_length,
            color="green",
            linewidth=linewidth,
            zorder=10,
        ) # Plot vertical axis arrow

        # Plot text
        ax.text(
            ox + arrow_length,
            oy,
            view_info["xlabel"],
            color="red",
            fontsize=10,
            weight="bold",
            zorder=10,
        ) # Plot horizontal axis label
        ax.text(
            ox,
            oy + arrow_length,
            view_info["ylabel"],
            color="green",
            fontsize=10,
            weight="bold",
            zorder=10,
        ) # Plot vertical axis label

def _draw_local_axes(ax, view_info, elements, linewidth=1.2):
    arrow_length = 0.2 * np.min(elements.length)
    for ele_idx in elements.index:
        c = elements.centroids[ele_idx]
        vecx = elements.rotation_matrices[:, :, 0][ele_idx]
        vecy = elements.rotation_matrices[:, :, 1][ele_idx]
        vecz = elements.rotation_matrices[:, :, 2][ele_idx]
        ax.quiver(
            c[0], c[1], c[2],
            *(arrow_length * vecx),
            color="red",
            linewidth=linewidth,
            zorder=10,
        )
        ax.quiver(
            c[0], c[1], c[2],
            *(arrow_length * vecy),
            color="green",
            linewidth=linewidth,
            zorder=10,
        )
        ax.quiver(
            c[0], c[1], c[2],
            *(arrow_length * vecz),
            color="blue",
            linewidth=linewidth,
            zorder=10,
        )
        tip_x = c + arrow_length * vecx
        ax.text(
            tip_x[0],
            tip_x[1],
            tip_x[2],
            "x",
            color="red",
            fontsize=8,
            zorder=10,
        )
        tip_y = c + arrow_length * vecy
        ax.text(
            tip_y[0],
            tip_y[1],
            tip_y[2],
            "y",
            color="green",
            fontsize=8,
            zorder=10,
        )
        tip_z = c + arrow_length * vecz
        ax.text(
            tip_z[0],
            tip_z[1],
            tip_z[2],
            "z",
            color="blue",
            fontsize=8,
            zorder=10,
        )
