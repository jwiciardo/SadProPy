import numpy as np

def _draw_grid(ax, ndim, storeys, coords, show_grids, colour="lightgray", linewidth=1.2, linestyle="--"):
    def convert_number_to_letters(num):
        letters = ""
        while True:
            num, rem = divmod(num, 26)
            letters = chr(ord("A") + rem) + letters
            if num == 0:
                break
            num -= 1
        return letters # return converted letters from numbers
    
    def set_grid_labels(xticks, yticks):
        xlabels = [convert_number_to_letters(num=i) for i in range(len(xticks))] # Set X-axis coordinate label
        if ndim == 3:
            ylabels = [str(i + 1) for i in range(len(yticks))] # Set Y-axis coordinate label
            zlabels = sorted(storeys.name) # Set Z-axis coordinate label
        else:
            ylabels = sorted(storeys.name) # Set Y-axis coordinate label
            zlabels = None # Set Z-axis coordinate label as None
        return xlabels, ylabels, zlabels

    def get_ticks(values):
        values = np.asarray(values)
        return np.sort(np.unique(values)) # Return sorted array of unique values

    if show_grids:
        model_size = np.max(coords.max(axis=0) - coords.min(axis=0)) # Determine model size
        padding = model_size * 0.05 # Set padding for the model
        xticks = get_ticks(coords[:, 0])
        xmin = coords[:, 0].min()
        xmax = coords[:, 0].max()
        if ndim == 3:
            yticks = get_ticks(coords[:, 1])
            zticks = np.sort(storeys.elevation)
            ymin = coords[:, 1].min()
            ymax = coords[:, 1].max()
            zmin = coords[:, 2].min()
            zmax = coords[:, 2].max()
        else:
            yticks = np.sort(storeys.elevation)
            ymin = coords[:, 1].min()
            ymax = coords[:, 1].max()
        xlabels, ylabels, zlabels = set_grid_labels(xticks=xticks, yticks=yticks)
        for x, label in zip(xticks, xlabels):
            if ndim == 3:
                for z in zticks:
                    ax.plot(
                        [x, x],
                        [ymin, ymax],
                        [z, z],
                        color=colour,
                        linestyle=linestyle,
                        linewidth=linewidth,
                        zorder=1,
                    )
                ax.text(
                    x,
                    ymin - padding,
                    zmin,
                    label,
                    color=colour,
                    ha="center",
                    va="center",
                    fontsize=10,
                    weight="bold",
                    bbox=dict(
                        boxstyle="circle, pad=0.35",
                        facecolor="white",
                        edgecolor=colour,
                        linewidth=linewidth,
                    ),
                    zorder=1,
                )
            else:
                ax.plot(
                    [x, x],
                    [ymin, ymax],
                    color=colour,
                    linestyle=linestyle,
                    linewidth=linewidth,
                    zorder=1,
                )
                ax.text(
                    x,
                    ymin - padding,
                    label,
                    color=colour,
                    ha="center",
                    va="center",
                    fontsize=10,
                    weight="bold",
                    bbox=dict(
                        boxstyle="circle, pad=0.35",
                        facecolor="white",
                        edgecolor=colour,
                        linewidth=linewidth,
                    ),
                    zorder=1,
                )
        
        for y, label in zip(yticks, ylabels):
            if ndim == 3:
                for z in zticks:
                    ax.plot(
                        [xmin, xmax],
                        [y, y],
                        [z, z],
                        color=colour,
                        linestyle=linestyle,
                        linewidth=linewidth,
                        zorder=1,
                    )
                ax.text(
                    xmin - padding,
                    y,
                    zmin,
                    label,
                    color=colour,
                    ha="center",
                    va="center",
                    fontsize=10,
                    weight="bold",
                    bbox=dict(
                        boxstyle="circle, pad=0.35",
                        facecolor="white",
                        edgecolor=colour,
                        linewidth=linewidth,
                    ),
                    zorder=1,
                )

                for x in xticks: # Loop over xticks
                    ax.plot(
                        [x, x],
                        [y, y],
                        [zmin, zmax],
                        color=colour,
                        linestyle=linestyle,
                        linewidth=linewidth,
                        zorder=1,
                    ) # Plot grid for Z-axis
            else:
                ax.plot(
                    [xmin, xmax],
                    [y, y],
                    color=colour,
                    linestyle=linestyle,
                    linewidth=linewidth,
                    zorder=1,
                )
                ax.text(
                    xmin - padding,
                    y,
                    label,
                    color=colour,
                    ha="center",
                    va="center",
                    fontsize=10,
                    weight="bold",
                    bbox=dict(
                        boxstyle="circle, pad=0.35",
                        facecolor="white",
                        edgecolor=colour,
                        linewidth=linewidth,
                    ),
                    zorder=1,
                )