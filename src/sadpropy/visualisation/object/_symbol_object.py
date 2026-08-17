from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from ...utility.helperfunc import transform_to_global_axes

def _draw_symbol(ax, symbol, node_coords, rotation_matrix, size, colour, linewidth, alpha):
    vertices = symbol.vertices.copy()
    vertices *= size
    vertices = transform_to_global_axes(
        values=vertices,
        rotation_matrices=rotation_matrix,
    )
    vertices += node_coords
    for i, j in symbol.segments:
        ax.plot(
            [vertices[i,0], vertices[j,0]],
            [vertices[i,1], vertices[j,1]],
            [vertices[i,2], vertices[j,2]],
            color=colour,
            linewidth=linewidth,
            zorder=10,
        )
    ax.add_collection3d(Poly3DCollection(
        [vertices],
        facecolor=colour,
        edgecolor="none",
        alpha=alpha,
        zorder=10,
    ))