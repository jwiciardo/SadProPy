import numpy as np
from ._exceptions import ValidationError

__all__ = ["transform_to_global_axes", "transform_to_local_axes", "retrieve_output_from_input", "get_edges_and_vertices_from_surface"]

# TRASNFORM TO GLOBAL AXES
def transform_to_global_axes(values, rotation_matrix):
    values = np.asarray(values) # Make values into an array
    if values.ndim == 1: # Set condition if dimension of array in values is 1 (3,) return projection to local axes
        return rotation_matrix @ values
    elif values.ndim == 2: # Set condition if dimension of array in values is 2 (N,3) return projection to local axes
        return values @ rotation_matrix.T
    raise ValidationError("Values must have shape (3,) or (N,3)")

# TRANSFORM TO LOCAL AXES
def transform_to_local_axes(values, rotation_matrix):
    values = np.asarray(values) # Make values into an array
    if values.ndim == 1: # Set condition if dimension of array in values is 1 (3,) return projection to local axes
        return rotation_matrix.T @ values
    elif values.ndim == 2: # Set condition if dimension of array in values is 2 (N,3) return projection to local axes
        return values @ rotation_matrix
    raise ValidationError("Values must have shape (3,) or (N,3)")

# RETRIEVE OUTPUT DATA FROM INPUT DATA WHICH SHARED COMMON TABLE
def retrieve_output_from_input(inputdata, shared_data_in, outputdata, shared_data_out):
    shared = shared_data_in[inputdata]
    lookup = dict(zip(shared_data_out, outputdata))
    try:
        outputdata_converted = np.vectorize(lookup.__getitem__)(shared)
    except KeyError as e:
        raise ValidationError(f"Shared value {e.args[0]!r} not found in output shared data")
    return outputdata_converted.astype(np.int32)

# GET EDGES AND VERTICES FROM SURFACE
def get_edges_and_vertices_from_surface(edges_name, line_objects, surface_name):
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