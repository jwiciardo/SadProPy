import numpy as np
from ..visualisation_class import StructuralSymbols
from ._symbol_object import _draw_symbol

def _plot_zerolength_elements(ax, coords, zerolength_elements, show_labels, show_hinges, colour="red", linewidth=1.2, alpha=1.0):
    rotation_matrices = zerolength_elements.rotation_matrices
    model_size = np.max(coords.max(axis=0) - coords.min(axis=0))
    offset = 0.005 * model_size  # Set label offset
    symbol_size = 0.02 * model_size # Set symbol size
    for i in zerolength_elements.index: # Loop for each element index
        child_node = zerolength_elements.end_nodes_idx[i][1] # Retrieve element child nodes index
        n_child = coords[child_node] # Retreive child node coordinates
        if show_hinges:
            _draw_symbol(
                ax=ax,
                symbol=StructuralSymbols.spring(),
                node_coords=n_child,
                rotation_matrix=rotation_matrices[i],
                size=symbol_size,
                colour=colour,
                linewidth=linewidth,
                alpha=alpha,
            ) # Plot marker for restraints
        
        if show_labels: # Set condition if show_labels is True or False
            ax.text(
                n_child[0] - offset,
                n_child[1] - offset,
                n_child[2] - offset,
                zerolength_elements.unique_name[i],
                fontsize=8,
                color="black",
                zorder=3,
            ) # Plot nodes labels        
