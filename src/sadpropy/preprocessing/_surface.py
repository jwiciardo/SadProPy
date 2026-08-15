import numpy as np
from ..utility._exceptions import ValidationError

# GENERATE SURFACE CONNECTIVITY
# Need to be vectorised for faster performance
def generate_surface_connectivity(edges_name, line_objects, surface_name):
    # Get edge indices
    edges_idx = np.full(4, -1, dtype=np.int32)
    for i, edge_name in enumerate(edges_name):
        try:
            edges_idx[i] = line_objects["Name to Index"][str(edge_name)]
        except KeyError:
            raise ValidationError(f"Surface '{surface_name}' references undefined line '{edge_name}'.")
    current_edges = edges_idx[:len(edges_name)]

    # Determine ordered vertices
    if len(edges_name) < 3:
        raise ValidationError(f"Surface '{surface_name}' must contain at least three edges.")
    edge1 = line_objects["End Points Index"][current_edges[0]]
    edge2 = line_objects["End Points Index"][current_edges[1]]

    if edge1[1] in edge2:
        vertices = [edge1[0], edge1[1]]
    elif edge1[0] in edge2:
        vertices = [edge1[1], edge1[0]]
    else:
        raise ValidationError(f"Surface '{surface_name}' has connection edges that are not closed.")

    for edge_idx in current_edges[1:]:
        edge = line_objects["End Points Index"][edge_idx]
        current_vertex = vertices[-1]
        if edge[0] == current_vertex:
            vertices.append(edge[1])
        elif edge[1] == current_vertex:
            vertices.append(edge[0])
        else:
            raise ValidationError(f"Surface '{surface_name}' has connection edges that are not closed.")

    if vertices[0] != vertices[-1]:
        raise ValidationError(f"Surface '{surface_name}' has connection edges that are not closed.")

    vertices.pop()
    vertices_idx = np.full(4, -1, dtype=np.int32)
    vertices_idx[:len(vertices)] = vertices
    return edges_idx, vertices_idx