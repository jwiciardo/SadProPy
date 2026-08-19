import numpy as np
from matplotlib.lines import Line2D
from ...utility._exception import ValidationError

# Colour List
colour_cycle = [
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

def _plot_elements(ax, materials, sections, coords, elements, colour_by, show_labels, show_rigid_end_offsets, linewidth=1.2):
    def get_element_colour():
        if elements is None: # Return nothing if there are no elements
            return
        
        if len(elements.index) == 0: # Return nothing if there are no elements
            return
        
        # Get element categories
        if colour_by is None: # Return default if colour_by is None
            categories = np.full(len(elements.index), "Default", dtype="U15")
        else:
            categories = np.empty(len(elements.index), dtype="U15") # Preallocated empty categories array
            for i in elements.index: # Loop over element index
                if colour_by == "Section": # Get section name if colour_by is "Section"
                    categories[i] = sections.sec_name[elements.sec_idx[i]]
                elif colour_by == "Element Type": # Get element type if colour_by is "Element Type"
                    categories[i] = elements.element_type[i]
                elif colour_by == "Material": # Get material name if colour_by is "Material"
                    mats_idx = sections.mats_idx[elements.sec_idx[i]]
                    categories[i] = materials.mat_name[mats_idx[np.argmax(mats_idx != -1)]]
                else:
                    raise ValidationError(f"Unknown colour_by: '{colour_by}'. "
                        "Choose None or between 'Section', 'Material', or 'Element Type'")
                
        # Generate colour map
        unique_categories = np.unique(categories) # Get unique categories
        category_colours = {
            category: colour_cycle[i % len(colour_cycle)]
            for i, category in enumerate(unique_categories)
        } # Define dictionary fo colour for each category
        colours = np.empty(len(elements.index), dtype=object) # Preallocated empty colours array
        for i in elements.index: # Loop over element index
            colours[i] = category_colours[categories[i]]
        return colours, categories, category_colours
    
    end_offsets = elements.end_offsets # Retrieve elements end offsets
    rigid_zone_factor = elements.rigid_zone_factor # Retrieve elements rigid zone factor
    colours, _, category_colours = get_element_colour() # Get element colour
    model_size = np.max(coords.max(axis=0) - coords.min(axis=0))
    offset = 0.005 * model_size # Set label offset
    for i in elements.index: # Loop for each element index
        inode, jnode = elements.end_nodes_idx[i] # Retrieve element end nodes index
        ni = coords[inode] # Retreive I-node coordinates
        nj = coords[jnode] # Retreive J-node coordinates
        eoi = end_offsets[i][:3] * rigid_zone_factor[i] # Retrieve I-end offset vector
        eoj = end_offsets[i][3:] * rigid_zone_factor[i] # Retrieve J-end offset vector
        noi = ni + eoi # Determine I-node offset coordinate
        noj = nj + eoj # Determine J-node offset coordinate
        if show_rigid_end_offsets:
            ax.plot(
                [ni[0], noi[0]],
                [ni[1], noi[1]],
                [ni[2], noi[2]],
                color=colours[i],
                linewidth=3.0,
                zorder=3,
            ) # Plot I-end offset
            ax.plot(
                [noi[0], noj[0]],
                [noi[1], noj[1]],
                [noi[2], noj[2]],
                color=colours[i],
                linewidth=linewidth,
                zorder=3,
            ) # Plot elements
            ax.plot(
                [noj[0], nj[0]],
                [noj[1], nj[1]],
                [noj[2], nj[2]],
                color=colours[i],
                linewidth=3.0,
                zorder=3,
            ) # Plot J-end offset
        else:
            ax.plot(
                [ni[0], nj[0]],
                [ni[1], nj[1]],
                [ni[2], nj[2]],
                color=colours[i],
                linewidth=linewidth,
                zorder=3,
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
                zorder=3,
            ) # Plot elements labels
        
        # Generate legends
        if not category_colours: # Set condition if category_colours is "Default" return nothing
            return
        handles = [Line2D([0], [0], color=colour, lw=2.5, label=label)
            for label, colour in sorted(category_colours.items())
        ] # Set handles for legends
        ax.legend(
            handles=handles,
            title=f"View by Colours of: {colour_by}",
            alignment="left",
            loc="upper left",
            bbox_to_anchor=(1.02, 0.90),
            borderaxespad=0,
        ) # Plot legends
