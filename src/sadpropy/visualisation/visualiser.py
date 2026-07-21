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
            "Isometric": (35, -60),
            "Front": (0, -90),
            "Back": (0, 90),
            "Left": (0, 180),
            "Right": (0, 0),
            "Top": (90, -90),
            "Bottom": (-90, -90),
        }

    # HELPER METHOD
    def _setup_axes(self, ax, title, view, coords):
        ax.set_title(title, fontsize=15, pad=0) # Set title for a plot
        ax.set_xlabel("X", labelpad=1) # Set label for X axis
        ax.set_ylabel("Y", labelpad=1) # Set label for Y axis
        ax.set_zlabel("Z", labelpad=1) # Set label for Z axis
        ax.grid(True) # Set invisibility of grid
        ax.xaxis.pane.set_facecolor((1, 1, 1, 1)) # Set X axis pane background colour
        ax.yaxis.pane.set_facecolor((1, 1, 1, 1)) # Set Y axis pane background colour
        ax.zaxis.pane.set_facecolor((1, 1, 1, 1)) # Set Z axis pane background colour
        ax.xaxis.pane.set_edgecolor("lightgray") # Set X axis pane edge colour
        ax.yaxis.pane.set_edgecolor("lightgray") # Set Y axis pane edge colour
        ax.zaxis.pane.set_edgecolor("lightgray") # Set Z axis pane edge colour
        ax.tick_params(labelsize=10) # Set tick size
        elev, azim = self._views[view] # Retrieve elevation and azimuth for views
        ax.view_init(elev=elev, azim=azim) # Set viewing angle

        # Axes Limit
        mins = coords.min(axis=0) # Determine minimum limit of the model
        maxs = coords.max(axis=0) # Determine maximum limit of the model
        model_size = np.max(maxs - mins) # Determine model size
        padding = model_size * 0.05 # Set padding for the model
        ax.set_xlim(mins[0] - padding, maxs[0] + padding) # Set X axis limit
        ax.set_ylim(mins[1] - padding, maxs[1] + padding) # Set Y axis limit
        ax.set_zlim(mins[2], maxs[2] + padding) # Set Z axis limit
        ax.set_box_aspect((
            maxs[0] - mins[0],
            maxs[1] - mins[1],
            maxs[2] - mins[2],
        )) # Set box limit

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

        if show_labels: # Set condition if show_labels True or False
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
    
    def _get_element_colour(self, elements, colour_by):
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
            categories = np.empty(len(elements.index), dtype="U15") # Preallocated empty array for categories
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
        colours = np.empty(len(elements.index), dtype=object) # Preallocated empty array for colours
        for i in elements.index: # Loop over element index
            colours[i] = category_colours[categories[i]]
        return colours
    
    def _plot_elements(self, ax, coords, elements_list, colour_by, show_labels, linewidth=1.2):
        for elements in elements_list: # Loop over elements_list
            colours = self._get_element_colour(elements=elements, colour_by=colour_by) # Get element colour
            model_size = np.max(coords.max(axis=0) - coords.min(axis=0))
            offset = 0.005 * model_size # Set label offset
            for i in elements.index: # Loop for each element index
                inode, jnode = elements.end_points_idx[i] # Retrieve element end nodes index (need to change end_points_idx into end_nodes_idx)
                p1 = coords[inode] # Retreive I-node coordinates
                p2 = coords[jnode] # Retreive J-node coordinates
                ax.plot(
                    [p1[0], p2[0]],
                    [p1[1], p2[1]],
                    [p1[2], p2[2]],
                    color=colours[i],
                    linewidth=linewidth,
                ) # Plot elements

                if show_labels: # Set condition if show_labels True or False
                    c = elements.centroids[i] # Retrieve centroid of the elements
                    ax.text(
                        c[0] + offset,
                        c[1] + offset,
                        c[2] + offset,
                        elements.unique_name[i],
                        fontsize=8,
                        color="black",
                    ) # Plot nodes labels

    def _build_legend(self, ax, colour_map, title):
        handles = []
        for category, colour in colour_map.items():
            handles.append(Line2D([0], [0], color=colour, lw=3, label=category))
        ax.legend(handles=handles, title=title, loc="upper left", bbox_to_anchor=(1.02, 1.0))

    # MAIN METHOD
    def plot_undeformed_model(
            self,
            view="Isometric",
            colour_by=None,
            show_nodes=True,
            show_elements=True,
            show_restraints=True,
            show_node_labels=False,
            show_element_labels=False,
            show_spring_hinges=False,
            show_end_releases=False,
            show_end_length_offsets=False,
            show_local_axes=False,
            show_finite_length_hinges=False,
            show_fiber_section=False,
        ):
        fig = plt.figure(figsize=(12, 10)) # Start plotting figure
        ax = fig.add_subplot(111, projection="3d") # Add axis in 3D
        title = "Undeformed Model"
        nodes = self._modeldata.point_objects # Retrieve nodes data (need to change point_objects into nodes)
        coords = self._modeldata.point_objects.coords # Retrieve nodes coordinates (need to change point_objects into nodes)
        beamcolumn_elements = self._modeldata.line_objects # Retrieve beam column elements data (need to change line_objects into beamcolumn_elements)
        elements_list = [beamcolumn_elements]
        
        self._setup_axes(ax=ax, title=title, view=view, coords=coords)

        if show_nodes:
            self._plot_nodes(
                ax=ax,
                nodes=nodes,
                coords=coords,
                show_labels=show_node_labels,
            )

        if show_elements:
            self._plot_elements(
                ax=ax,
                coords=coords,
                elements_list=elements_list,
                colour_by=colour_by,
                show_labels=show_element_labels,
            )
        
        plt.tight_layout()
        plt.show()

        


        point_objects = self._modeldata.point_objects
        line_objects = self._modeldata.line_objects
        restraints = self._modeldata.restraints

        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection="3d")
        ax.set_title("Line Connectivity")
        ax.set_xlabel("X", labelpad=5)
        ax.set_ylabel("Y", labelpad=5)
        ax.set_zlabel("Z", labelpad=5)

        ax.tick_params(axis="x", pad=5)
        ax.tick_params(axis="y", pad=5)
        ax.tick_params(axis="z", pad=5)
        coords = point_objects.coords
        mins = coords.min(axis=0)
        maxs = coords.max(axis=0)
        model_size = np.max(maxs - mins)

        # --------------------------------------------------------
        # Draw Restraint objects
        # --------------------------------------------------------
        for point_idx in restraints.point_idx:
            p = point_objects.coords[point_idx]
            ax.scatter(
                p[0],
                p[1],
                p[2],
                color="red",
                marker="^",
                s=80,
                zorder=10,
            )

        # --------------------------------------------------------
        # Draw local axes
        # --------------------------------------------------------
        arrow_length = 0.2 * np.min(line_objects.length)
        for line_idx in line_objects.index:
            c = line_objects.centroids[line_idx]
            lx = line_objects.local_x[line_idx]
            ly = line_objects.local_y[line_idx]
            lz = line_objects.local_z[line_idx]
            ax.quiver(
                c[0], c[1], c[2],
                *(arrow_length * lx),
                color="red",
                arrow_length_ratio=0.2,
            )
            ax.quiver(
                c[0], c[1], c[2],
                *(arrow_length * ly),
                color="green",
                arrow_length_ratio=0.2,
            )
            ax.quiver(
                c[0], c[1], c[2],
                *(arrow_length * lz),
                color="blue",
                arrow_length_ratio=0.2,
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