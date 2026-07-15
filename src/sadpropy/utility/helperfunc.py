import numpy as np
from collections import defaultdict
from sadpropy.preprocessing._propertiesclass import PropertiesClassRegistry
from ._exceptions import ValidationError

__all__ = ["get_material_properties", "get_section_properties", "get_vertices_from_surface"]

# GET MATERIAL PROPERTIES
def get_material_properties(mats_list, mat_class=np.ndarray, mat_idx=np.ndarray, props_name=list[str]):
    n = len(mat_class)
    props_class = PropertiesClassRegistry()._get_mat_props_class(mat_class)
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
    props_class = PropertiesClassRegistry()._get_sec_props_class(sec_class)
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

# GET VERTICES FROM SURFACE
def get_vertices_from_surface(edges, line_connectivity):
    first_edge = line_connectivity[edges[0]]
    vertices = [first_edge.i_end, first_edge.j_end]
    remaining_edges = edges[1:]
    while remaining_edges:
        current_edge = vertices[-1]
        found = False
        for edge_id in remaining_edges:
            edge = line_connectivity[edge_id]
            if edge.i_end == current_edge:
                vertices.append(edge.j_end)
                remaining_edges.remove(edge_id)
                found = True
                break
            elif edge.j_end == current_edge:
                vertices.append(edge.i_end)
                remaining_edges.remove(edge_id)
                found = True
                break
        if not found:
            raise ValidationError("Edges do not form a closed polygon")
    return vertices

# DETERMINE POINT CONNECTIVITY FOR AREA OBJECTS
def determine_pointconnectivity_for_areaobj(area_object, line_objects, point_objects):
    edgesdata_for_areaobj = [line_objects[eid] for eid in area_object.edges] # Recall edges data for area object's edges
    adj = defaultdict(list) # Build adjacency map for each node in edges data
    for edge in edgesdata_for_areaobj:
        adj[edge.iend_point].append(edge.jend_point)
        adj[edge.jend_point].append(edge.iend_point)
    
    # Recover ordered nodes loop
    start_node = min(adj)
    nodes_loop = [start_node]
    prev_node = None
    current_node = start_node
    while True:
        neighbour_nodes = adj[current_node]
        if len(neighbour_nodes) != 2:
            raise ValueError(
                f"Node {current_node} has {len(neighbour_nodes)} neighbours. "
                "Boundary is not a simple closed polygon."
            )
        next_node = neighbour_nodes[0] if neighbour_nodes[0] != prev_node else neighbour_nodes[1]
        if next_node == start_node:
            break
        nodes_loop.append(next_node)
        prev_node, current_node = current_node, next_node
        if len(nodes_loop) > len(adj):
            raise ValueError("Failed to reconstruct polygon.")
    
    # Determine area of polygon
    area = 0.0
    n = len(nodes_loop)
    for i in range(n):
        n1 = point_objects[nodes_loop[i]]
        n2 = point_objects[nodes_loop[(i + 1) % n]]
        area += n1.x * n2.y
        area -= n2.x * n1.y
    signed_area = area / 2.0

    if signed_area > 0:  # Enforce clockwise ordering of nodes
        return list(reversed(nodes_loop))
    return nodes_loop