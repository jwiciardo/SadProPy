import numpy as np
from ..visualisation_class import StructuralSymbols
from ._symbol_object import _draw_symbol

def _plot_restraints(ax, coords, rotation_matrix, restraints, colour="black", linewidth=1.2):
    model_size = np.max(coords.max(axis=0) - coords.min(axis=0))
    symbol_size = 0.02 * model_size # Set symbol size

    for node, dof in zip(restraints.node_idx, restraints.dofs): # Loop over each node
        if np.all(dof):
            _draw_symbol(
                ax=ax,
                symbol=StructuralSymbols.fixed(),
                node_coords=coords[node],
                rotation_matrix=rotation_matrix,
                size=symbol_size,
                colour=colour,
                linewidth=linewidth,
            ) # Plot marker for restraints