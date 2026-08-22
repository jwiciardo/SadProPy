import numpy as np
from ..preprocessing_class_index import SlabSectionDimensions
from ...utility.exception import ValidationError

# GENERATE SHELL SELFWEIGHT
def _generate_shell_selfweight(materials, slab_sections, shell_sec_idx):
    # Shell section dimensions
    shell_sec_dims = slab_sections.dimensions[shell_sec_idx]
    shell_thickness = shell_sec_dims[:, SlabSectionDimensions.t]

    # Shell material properties
    shell_mats_idx = slab_sections.mats_idx[shell_sec_idx]
    shell_mat_idx = shell_mats_idx[:, np.argmax(shell_mats_idx != -1)]
    shell_mat_def = materials.mat_def[shell_mat_idx]
    shell_mat_props = materials.properties[shell_mat_idx]
    row_idx = np.arange(len(shell_mat_props))
    unitweight_idx = np.array([matdef.properties.Unitweight for matdef in shell_mat_def])
    shell_unitweight = shell_mat_props[row_idx, unitweight_idx]
    shell_selfweight = shell_unitweight * shell_thickness
    return shell_selfweight

# GENERATE SHELL CONNECTIVITY
# Need to be vectorised for faster performance
def _generate_shell_connectivity(edges_name, element_objects, shell_name):
    # Get edge indices
    edges_idx = np.full(4, -1, dtype=np.int32)
    for i, edge_name in enumerate(edges_name):
        try:
            edges_idx[i] = element_objects["Name to Index"][str(edge_name)]
        except KeyError:
            raise ValidationError(f"Shell '{shell_name}' references undefined element '{edge_name}'.")
    current_edges = edges_idx[:len(edges_name)]

    # Determine ordered vertices
    if len(edges_name) < 3:
        raise ValidationError(f"Shell '{shell_name}' must contain at least three edges.")
    edge1 = element_objects["End Nodes Index"][current_edges[0]]
    edge2 = element_objects["End Nodes Index"][current_edges[1]]

    if edge1[1] in edge2:
        vertices = [edge1[0], edge1[1]]
    elif edge1[0] in edge2:
        vertices = [edge1[1], edge1[0]]
    else:
        raise ValidationError(f"Shell '{shell_name}' has connection edges that are not closed.")

    for edge_idx in current_edges[1:]:
        edge = element_objects["End Nodes Index"][edge_idx]
        current_vertex = vertices[-1]
        if edge[0] == current_vertex:
            vertices.append(edge[1])
        elif edge[1] == current_vertex:
            vertices.append(edge[0])
        else:
            raise ValidationError(f"Shell '{shell_name}' has connection edges that are not closed.")

    if vertices[0] != vertices[-1]:
        raise ValidationError(f"Shell '{shell_name}' has connection edges that are not closed.")

    vertices.pop()
    vertices_idx = np.full(4, -1, dtype=np.int32)
    vertices_idx[:len(vertices)] = vertices
    return edges_idx, vertices_idx