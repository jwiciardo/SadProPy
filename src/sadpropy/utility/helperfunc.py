import numpy as np
from collections import defaultdict
from sadpropy.preprocessing._propertiesclass import PropertiesClassRegistry
from ._exceptions import ValidationError

__all__ = ["get_material_properties", "get_section_properties", "get_edges_and_vertices_from_surface", "retrieve_output_from_input"]

# GET MATERIAL PROPERTIES
def get_material_properties(mats_list, mat_class=np.ndarray, mat_idx=np.ndarray, props_name=list[str]):
    n = len(mat_class)
    props_class = PropertiesClassRegistry()._get_mat_props_class(mat_class=mat_class)
    max_ncol_props_class = np.max(np.array([len(propcls) for propcls in props_class])) # Maximum number of array columns in all material properties
    mat_props = np.zeros((n, max_ncol_props_class), dtype=np.float64)
    for cls in np.unique(mat_class):
            mask = mat_class == cls
            mat = mats_list[cls]
            props = mat.properties[mat_idx[mask]]
            mat_props[mask, :props.shape[1]] = props
    row_idx = np.arange(n)[:, None]
    col_idx = np.array(
        [[getattr(propcls, propname) for propname in props_name]
        for propcls in props_class
    ])
    return mat_props[row_idx, col_idx]

# GET SECTION PROPERTIES
def get_section_properties(secs_list, sec_class=np.ndarray, sec_idx=np.ndarray, props_name=list[str]):
    n = len(sec_class)
    props_class = PropertiesClassRegistry()._get_sec_props_class(sec_class=sec_class)
    max_ncol_props_class = np.max(np.array([len(propcls) for propcls in props_class])) # Maximum number of array columns in all section properties
    sec_props = np.zeros((n, max_ncol_props_class), dtype=np.float64)
    for cls in np.unique(sec_class):
            mask = sec_class == cls
            sec = secs_list[cls]
            props = sec.properties[sec_idx[mask]]
            sec_props[mask, :props.shape[1]] = props
    row_idx = np.arange(n)[:, None]
    col_idx = np.array(
        [[getattr(propcls, propname) for propname in props_name]
        for propcls in props_class
    ])
    return sec_props[row_idx, col_idx]

# RETRIEVE OUTPUT DATA FROM INPUT DATA WHICH SHARED COMMON TABLE
def retrieve_output_from_input(inputdata, shared_data_in, outputdata, shared_data_out):
    shared = shared_data_in[inputdata]
    lookup = dict(zip(shared_data_out, outputdata))
    try:
        outputdata_converted = np.vectorize(lookup.__getitem__)(shared)
    except KeyError as e:
        raise ValidationError(f"Shared value {e.args[0]!r} not found in output shared data.")
    return outputdata_converted.astype(np.int32)

# GET EDGES AND VERTICES FROM SURFACE
def get_edges_and_vertices_from_surface(edges_name, line_objects, surface_name):
    # Get edge indices
    edges_idx = np.full(4, -1, dtype=np.int32)
    for i, edge_name in enumerate(edges_name):
        try:
            edges_idx[i] = line_objects.name_to_idx[str(edge_name)]
        except KeyError:
            raise ValidationError(f"Surface '{surface_name}' references undefined line '{edge_name}'.")
    current_edges = edges_idx[:len(edges_name)]

    # Determine ordered vertices
    if len(edges_name) < 3:
        raise ValidationError(f"Surface '{surface_name}' must contain at least three edges.")
    edge1 = line_objects.end_points_idx[current_edges[0]]
    edge2 = line_objects.end_points_idx[current_edges[1]]

    if edge1[1] in edge2:
        vertices = [edge1[0], edge1[1]]
    elif edge1[0] in edge2:
        vertices = [edge1[1], edge1[0]]
    else:
        raise ValidationError(f"Surface '{surface_name}' has connection edges that are not closed.")

    for edge_idx in current_edges[1:]:
        edge = line_objects.end_points_idx[edge_idx]
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