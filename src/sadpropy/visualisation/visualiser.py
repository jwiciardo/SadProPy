import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
from sadpropy.utility._exceptions import ValidationError

__all__ = ["Visualisation"]

class Visualisation:
    def __init__(self, modeldata):
        self._modeldata = modeldata

        # Colour List
        self._colour_cycle = [
            "blue",
            "green",
            "red",
            "cyan",
            "yellow",
            "magenta",
            "tab:blue",
            "tab:green",
            "tab:red",
            "tab:orange",
            "tab:purple",
            "tab:brown",
            "tab:pink",
            "tab:gray",
            "tab:olive",
            "tab:cyan",
        ]

        # View Dictionary
        self._views = {
            "Isometric": (35, -120),
            "Front": (0, -90),
            "Back": (0, 90),
            "Left": (0, 180),
            "Right": (0, 0),
            "Top": (90, -90),
            "Bottom": (-90, -90),
        }

        # DOFs Symbol Dictionary
        self._dof_style = {
            "UX": {"offset": (-1, 0, 0), "marker": ">"},
            "UY": {"offset": (0, 1, 0), "marker": ">"},
            "UZ": {"offset": (0, 0, 1), "marker": "^"},
            "RX": {"offset": (1, 0, 0), "marker": "_"},
            "RY": {"offset": (0, -1, 0), "marker": "_"},
            "RZ": {"offset": (0, 0, -1), "marker": "|"},
        }

    # HELPER METHOD
    def _set_axes(self, ax, title, view, coords):
        ax.set_title(title, fontsize=15, pad=0) # Set title for a plot
        elev, azim = self._views[view] # Retrieve elevation and azimuth for views
        ax.view_init(elev=elev, azim=azim) # Set viewing angle
        ax.axis('off')

        mins = coords.min(axis=0) # Determine minimum limit of the model
        maxs = coords.max(axis=0) # Determine maximum limit of the model
        ax.set_box_aspect((
            maxs[0] - mins[0],
            maxs[1] - mins[1],
            maxs[2] - mins[2],
        )) # Set box aspect ratio

    def _draw_global_axes(self, ax, ndim, coords, show_axes, linewidth=3):
        if show_axes: # Set condition if show_axes is True or False
            model_size = np.max(coords.max(axis=0) - coords.min(axis=0)) # Determine model size
            arrow_length = model_size * 0.05 # Set arrow length 
            ox, oy, oz = (0.0, 0.0, 0.0) # Set original point
            ax.quiver(
                ox, oy, oz,
                arrow_length, 0, 0,
                color="red",
                linewidth=linewidth,
            ) # Plot X-axis arrow
            ax.text(
                ox + arrow_length,
                oy,
                oz,
                "X",
                color="red",
                fontsize=10,
                weight="bold",
            ) # Plot X-axis label

            if ndim == 3:
                ax.quiver(
                    ox, oy, oz,
                    0, arrow_length, 0,
                    color="green",
                    linewidth=linewidth,
                ) # Plot Y-axis arrow
                ax.text(
                    ox,
                    oy + arrow_length,
                    oz,
                    "Y",
                    color="green",
                    fontsize=10,
                    weight="bold",
                ) # Plot Y-axis label

                ax.quiver(
                    ox, oy, oz,
                    0, 0, arrow_length,
                    color="blue",
                    linewidth=linewidth,
                ) # Plot Z-axis arrow
                ax.text(
                    ox,
                    oy,
                    oz + arrow_length,
                    "Z",
                    color="blue",
                    fontsize=10,
                    weight="bold",
                ) # Plot Z-axis label
            else:
                ax.quiver(
                    ox, oy,
                    arrow_length, 0,
                    color="red",
                    linewidth=linewidth,
                ) # Plot X-axis arrow
                ax.quiver(
                    ox, oy,
                    0, arrow_length,
                    color="green",
                    linewidth=linewidth,
                ) # Plot Y-axis arrow
                ax.text(
                    ox + arrow_length,
                    oy,
                    "X",
                    color="red",
                    fontsize=10,
                    weight="bold",
                ) # Plot X-axis label
                ax.text(
                    ox,
                    oy + arrow_length,
                    "Y",
                    color="green",
                    fontsize=10,
                    weight="bold",
                ) # Plot Y-axis label

    def _draw_local_axes(self, ax, elements_list, show_axes, linewidth=1.2):
        if show_axes:
            for element in elements_list:
                arrow_length = 0.2 * np.min(element.length)
                for ele_idx in element.index:
                    c = element.centroids[ele_idx]
                    lx = element.local_x[ele_idx]
                    ly = element.local_y[ele_idx]
                    lz = element.local_z[ele_idx]
                    ax.quiver(
                        c[0], c[1], c[2],
                        *(arrow_length * lx),
                        color="red",
                        linewidth=linewidth,
                    )
                    ax.quiver(
                        c[0], c[1], c[2],
                        *(arrow_length * ly),
                        color="green",
                        linewidth=linewidth,
                    )
                    ax.quiver(
                        c[0], c[1], c[2],
                        *(arrow_length * lz),
                        color="blue",
                        linewidth=linewidth,
                    )
                    tip_x = c + arrow_length * lx
                    ax.text(
                        tip_x[0],
                        tip_x[1],
                        tip_x[2],
                        "x",
                        color="red",
                        fontsize=8,
                    )
                    tip_y = c + arrow_length * ly
                    ax.text(
                        tip_y[0],
                        tip_y[1],
                        tip_y[2],
                        "y",
                        color="green",
                        fontsize=8,
                    )
                    tip_z = c + arrow_length * lz
                    ax.text(
                        tip_z[0],
                        tip_z[1],
                        tip_z[2],
                        "z",
                        color="blue",
                        fontsize=8,
                    )

    def _draw_grid(self, ax, ndim, storeys, coords, show_grids, colour="lightgray", linewidth=1.2, linestyle="--"):
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
                zlabels = sorted([storeys[storey].name for storey in storeys]) # Set Z-axis coordinate label
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
                zticks = np.sort(np.array([storeys[storey].elevation for storey in storeys], dtype=float))
                ymin = coords[:, 1].min()
                ymax = coords[:, 1].max()
                zmin = coords[:, 2].min()
                zmax = coords[:, 2].max()
            else:
                yticks = np.sort(np.array([storeys[storey].elevation for storey in storeys], dtype=float))
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
                            zorder=0,
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
                    )
                else:
                    ax.plot(
                        [x, x],
                        [ymin, ymax],
                        color=colour,
                        linestyle=linestyle,
                        linewidth=linewidth,
                        zorder=0,
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
                            zorder=0,
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
                    )

                    for x in xticks: # Loop over xticks
                        ax.plot(
                            [x, x],
                            [y, y],
                            [zmin, zmax],
                            color=colour,
                            linestyle=linestyle,
                            linewidth=linewidth,
                            zorder=0,
                        ) # Plot grid for Z-axis
                else:
                    ax.plot(
                        [xmin, xmax],
                        [y, y],
                        color=colour,
                        linestyle=linestyle,
                        linewidth=linewidth,
                        zorder=0,
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
                    )
    
    def _plot_nodes(self, ax, nodes, coords, show_labels, marker="o", markersize=10, colour="black"):
        ax.scatter(
            coords[:, 0],
            coords[:, 1],
            coords[:, 2],
            s=markersize,
            c=colour,
            marker=marker,
            depthshade=True,
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
                ) # Plot nodes labels
    
    def _plot_elements(self, ax, coords, elements_list, colour_by, show_labels, linewidth=1.2):
        def get_element_colour(elements):
            if elements is None: # Return nothing if there are no elements
                return
            
            if len(elements.index) == 0: # Return nothing if there are no elements
                return
            
            # Get element categories
            sections_list = self._modeldata.sections_list # Retrieve sections list
            materials_list = self._modeldata.materials_list # Retrieve materials list
            if colour_by is None: # Return default if colour_by is None
                categories = np.full(len(elements.index), "Default", dtype="U15")
            else:
                categories = np.empty(len(elements.index), dtype="U15") # Preallocated empty categories array
                for i in elements.index: # Loop over element index
                    section = sections_list[elements.sec_class[i]] # Get section data
                    material = materials_list[section.mats_class[elements.sec_idx[i]][0]] # Get material data
                    if colour_by == "Section": # Get section name if colour_by is "Section"
                        categories[i] = section.sec_name[elements.sec_idx[i]]
                    elif colour_by == "Element Type": # Get element type if colour_by is "Element Type"
                        categories[i] = section.element_type[elements.sec_idx[i]]
                    elif colour_by == "Material": # Get material name if colour_by is "Material"
                        categories[i] = material.mat_name[section.mats_idx[elements.sec_idx[i]][0]]
                    else:
                        raise ValidationError(f"Unknown colour_by='{colour_by}'"
                            "Choose None or between 'Section', 'Material', or 'Element Type'")
                    
            # Generate colour map
            unique_categories = np.unique(categories) # Get unique categories
            category_colours = {
                category: self._colour_cycle[i % len(self._colour_cycle)]
                for i, category in enumerate(unique_categories)
            } # Define dictionary fo colour for each category
            colours = np.empty(len(elements.index), dtype=object) # Preallocated empty colours array
            for i in elements.index: # Loop over element index
                colours[i] = category_colours[categories[i]]
            return colours, categories, category_colours
        
        for elements in elements_list: # Loop over elements_list
            colours, _, category_colours = get_element_colour(elements=elements) # Get element colour
            model_size = np.max(coords.max(axis=0) - coords.min(axis=0))
            offset = 0.005 * model_size # Set label offset
            for i in elements.index: # Loop for each element index
                inode, jnode = elements.end_nodes_idx[i] # Retrieve element end nodes index
                p1 = coords[inode] # Retreive I-node coordinates
                p2 = coords[jnode] # Retreive J-node coordinates
                ax.plot(
                    [p1[0], p2[0]],
                    [p1[1], p2[1]],
                    [p1[2], p2[2]],
                    color=colours[i],
                    linewidth=linewidth,
                ) # Plot elements

                if show_labels: # Set condition if show_labels is True or False
                    c = elements.centroids[i] # Retrieve centroid of the elements
                    ax.text(
                        c[0] + offset,
                        c[1] + offset,
                        c[2] + offset,
                        elements.unique_name[i],
                        fontsize=8,
                        color="black",
                    ) # Plot nodes labels
            
            # Generate legends
            if not category_colours: # Set condition if category_colours is "Default" return nothing
                return
            handles = [Line2D([0], [0], color=colour, lw=2.5, label=label)
                for label, colour in sorted(category_colours.items())
            ] # Set handles for legends
            ax.legend(
                handles=handles,
                title=f"Colour by: {colour_by}",
                loc="upper left",
                bbox_to_anchor=(1.02, 1.0),
                borderaxespad=0,
            ) # Plot legends

    def _plot_restraints(self, ax, coords, restraints, marker_size=80, colour="black"):
        def draw_restraint_symbol(coords, dof):
            if np.all(dof):
                ax.scatter(
                    *coords,
                    marker="s",
                    s=marker_size,
                    c=colour,
                    edgecolors=colour,
                    zorder=11,
                ) # Plot marker for fixed restraints
            elif np.array_equal(dof, [1,1,1,0,0,0]):
                ax.scatter(
                    *coords,
                    marker="^",
                    s=marker_size,
                    c=colour,
                    edgecolors=colour,
                    zorder=11,
                ) # Plot marker for pinned restraints

        for node, dof in zip(restraints.node_idx, restraints.dofs): # Loop over each node
            draw_restraint_symbol(coords=coords[node], dof=dof) # Plot marker for restraints

    # MAIN METHOD
    def plot_undeformed_model(
            self,
            view="Isometric",
            colour_by=None,
            show_grids=True,
            show_nodes=True,
            show_elements=True,
            show_restraints=True,
            show_node_labels=True,
            show_element_labels=True,
            show_spring_hinges=False,
            show_end_releases=False,
            show_end_length_offsets=False,
            show_global_axes=True,
            show_local_axes=False,
            show_finite_length_hinges=False,
            show_fiber_section=False,
        ):
        fig = plt.figure(figsize=(12, 10)) # Start plotting figure
        ax = fig.add_subplot(111, projection="3d") # Add axis in 3D
        
        title = "Undeformed Model"
        ndim = self._modeldata.project_information.ndim # Retrieve number of dimensional space
        storeys = self._modeldata.storeys # Retrieve storeys data
        nodes = self._modeldata.nodes # Retrieve nodes data
        coords = self._modeldata.nodes.coords # Retrieve nodes coordinates
        beamcolumn_elements = self._modeldata.beamcolumn_elements # Retrieve beam column elements data
        elements_list = [beamcolumn_elements]
        restraints = self._modeldata.restraints # Retrieve restraints data
        
        self._set_axes(ax=ax, title=title, view=view, coords=coords) # Set axes
        self._draw_global_axes(ax=ax, ndim=ndim, coords=coords, show_axes=show_global_axes) # Set global axes arrows
        self._draw_local_axes(ax=ax, elements_list=elements_list, show_axes=show_local_axes) # Set local axes arrows
        self._draw_grid(ax=ax, ndim=ndim, storeys=storeys, coords=coords, show_grids=show_grids) # Set gridlines
        if show_nodes: # Set condition if show_nodes is True or False
            self._plot_nodes(
                ax=ax,
                nodes=nodes,
                coords=coords,
                show_labels=show_node_labels,
            ) # Plot nodes if show_nodes is True
        if show_elements: # Set condition if show_elements is True or False
            self._plot_elements(
                ax=ax,
                coords=coords,
                elements_list=elements_list,
                colour_by=colour_by,
                show_labels=show_element_labels,
            ) # Plot nodes if show_elements is True
        if show_restraints: # Set condition if show_restraints is True or False
            self._plot_restraints(
                ax=ax,
                coords=coords,
                restraints=restraints,
            ) # Plot nodes if show_restraints is True
        
        plt.tight_layout()
        plt.show()