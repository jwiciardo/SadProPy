import numpy as np

def _set_axes(ax, title, view, coords):
    views = {
        "Isometric": (35, -120),
        "Front": (0, -90),
        "Back": (0, 90),
        "Left": (0, 180),
        "Right": (0, 0),
        "Top": (90, -90),
        "Bottom": (-90, -90),
    } # View dictionary
    ax.set_title(title, fontsize=15, pad=0) # Set title for a plot
    elev, azim = views[view] # Retrieve elevation and azimuth for views
    ax.view_init(elev=elev, azim=azim) # Set viewing angle
    ax.axis('off')

    mins = coords.min(axis=0) # Determine minimum limit of the model
    maxs = coords.max(axis=0) # Determine maximum limit of the model
    ax.set_box_aspect((
        maxs[0] - mins[0],
        maxs[1] - mins[1],
        maxs[2] - mins[2],
    )) # Set box aspect ratio

def _draw_global_axes(ax, ndim, coords, show_axes, linewidth=3):
    if show_axes: # Set condition if show_axes is True or False
        model_size = np.max(coords.max(axis=0) - coords.min(axis=0)) # Determine model size
        arrow_length = model_size * 0.05 # Set arrow length 
        ox, oy, oz = (0.0, 0.0, 0.0) # Set original point
        ax.quiver(
            ox, oy, oz,
            arrow_length, 0, 0,
            color="red",
            linewidth=linewidth,
            zorder=10,
        ) # Plot X-axis arrow
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

        if ndim == 3:
            ax.quiver(
                ox, oy, oz,
                0, arrow_length, 0,
                color="green",
                linewidth=linewidth,
                zorder=10,
            ) # Plot Y-axis arrow
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

            ax.quiver(
                ox, oy, oz,
                0, 0, arrow_length,
                color="blue",
                linewidth=linewidth,
                zorder=10,
            ) # Plot Z-axis arrow
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
            ax.quiver(
                ox, oy,
                arrow_length, 0,
                color="red",
                linewidth=linewidth,
                zorder=10,
            ) # Plot X-axis arrow
            ax.quiver(
                ox, oy,
                0, arrow_length,
                color="green",
                linewidth=linewidth,
                zorder=10,
            ) # Plot Y-axis arrow
            ax.text(
                ox + arrow_length,
                oy,
                "X",
                color="red",
                fontsize=10,
                weight="bold",
                zorder=10,
            ) # Plot X-axis label
            ax.text(
                ox,
                oy + arrow_length,
                "Y",
                color="green",
                fontsize=10,
                weight="bold",
                zorder=10,
            ) # Plot Y-axis label

def _draw_local_axes(ax, elements, show_axes, linewidth=1.2):
    if show_axes:
        arrow_length = 0.2 * np.min(elements.length)
        for ele_idx in elements.index:
            c = elements.centroids[ele_idx]
            lx = elements.local_x[ele_idx]
            ly = elements.local_y[ele_idx]
            lz = elements.local_z[ele_idx]
            ax.quiver(
                c[0], c[1], c[2],
                *(arrow_length * lx),
                color="red",
                linewidth=linewidth,
                zorder=10,
            )
            ax.quiver(
                c[0], c[1], c[2],
                *(arrow_length * ly),
                color="green",
                linewidth=linewidth,
                zorder=10,
            )
            ax.quiver(
                c[0], c[1], c[2],
                *(arrow_length * lz),
                color="blue",
                linewidth=linewidth,
                zorder=10,
            )
            tip_x = c + arrow_length * lx
            ax.text(
                tip_x[0],
                tip_x[1],
                tip_x[2],
                "x",
                color="red",
                fontsize=8,
                zorder=10,
            )
            tip_y = c + arrow_length * ly
            ax.text(
                tip_y[0],
                tip_y[1],
                tip_y[2],
                "y",
                color="green",
                fontsize=8,
                zorder=10,
            )
            tip_z = c + arrow_length * lz
            ax.text(
                tip_z[0],
                tip_z[1],
                tip_z[2],
                "z",
                color="blue",
                fontsize=8,
                zorder=10,
            )
