from collections import defaultdict
from sadpropy.model.dataclasses import StoreyData
from .exceptions import ValidationError

__all__ = ["create_storeys", "get_vertices_from_surface"]

# CREATE STOREY DATA
def create_storeys(storey_elevations):
    storey_data = {}
    for i, elev in enumerate(storey_elevations):
        if i == 0:
            storey_name = "Base"
            height = 0.0
        else:
            storey_name = f"Storey{i}"
            height = elev - storey_elevations[i - 1]
        storey_data[storey_name] = StoreyData(
            name = storey_name,
            height = height,
            elevation = elev,
        )
    return dict(reversed(storey_data.items()))

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