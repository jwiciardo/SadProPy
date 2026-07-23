import numpy as np
from collections import defaultdict
from sadpropy.preprocessing._propertiesclass import PropertiesClassRegistry
from sadpropy.preprocessing._connectivityclass import ConnectionDirection
from ._exceptions import ValidationError

__all__ = ["get_material_properties", "get_section_properties", "retrieve_output_from_input", "generate_local_axes", "generate_line_connectivity", "get_edges_and_vertices_from_surface"]

# GET MATERIAL PROPERTIES
def get_material_properties(mats_list, mat_class=np.ndarray, mat_idx=np.ndarray, props_name=list[str]):
    n = len(mat_class) # Get length of array (rows)
    props_class = PropertiesClassRegistry()._get_mat_props_class(mat_class=mat_class) # Get Properties class index of material, look at _propertiesclass.py
    max_ncol_props_class = np.max(np.array([len(propcls) for propcls in props_class])) # Determine maximum number of columns among all material properties arrays
    mat_props = np.zeros((n, max_ncol_props_class), dtype=np.float64) # Allocate material properties array which has shape (n, max number of columns)
    for cls in np.unique(mat_class): # Filter material properties array using material class mask
            mask = mat_class == cls
            mat = mats_list[cls]
            props = mat.properties[mat_idx[mask]]
            mat_props[mask, :props.shape[1]] = props
    row_idx = np.arange(n)[:, None] # Build array of index
    col_idx = np.array(
        [[getattr(propcls, propname) for propname in props_name]
        for propcls in props_class
    ]) # Build array of properties class
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

# GENERATE LOCAL AXES OF LINE OBJECTS
def generate_local_axes(end_points_index, point_objects, ndim):
    coords = point_objects.coords # Retrieve array of point coordinates
    
    # 3-Dimensional Structure
    if ndim == 3:
        i_coords = coords[end_points_index[:, 0]] # Obtain I-end point coordinates from array of point coordinates
        j_coords = coords[end_points_index[:, 1]] # Obtain I-end point coordinates from array of point coordinates
        d_vectors = j_coords - i_coords # Determine direction vectors
        length = np.linalg.norm(d_vectors, axis=1) # Compute length of line objects
        local_x = d_vectors / length[:, None] # Determine local x-axis
        reference = np.tile(np.array([0.0, 0.0, 1.0]), (len(local_x), 1)) # Build reference direction array, default is toward global Z-axis
        vertical = np.abs(local_x[:, 2]) > 0.99 # Build masking for vertical line objects
        reference[vertical] = np.array([1.0, 0.0, 0.0]) # Change reference direction array for vertical line objects which is toward global X-axis
        local_z = np.cross(local_x, reference) # Cross product to determine local z-axis
        local_z /= np.linalg.norm(local_z, axis=1)[:, None] # Determine local z-axis
        local_y = np.cross(local_z, local_x) # Cross product to determine local y-axis
        local_y /= np.linalg.norm(local_y, axis=1)[:, None] # Determine local y-axis
        rotation_matrix = np.stack((local_x, local_y, local_z), axis=1) # Build rotation matrix 3x3 for transforming global to local axes and local to global axes
        return (length, local_x, local_y, local_z, rotation_matrix)

    # 2-Dimensional Structure
    else:
        i_coords = coords[end_points_index[:, 0], :2] # Obtain I-end point coordinates from array of point coordinates
        j_coords = coords[end_points_index[:, 1], :2] # Obtain I-end point coordinates from array of point coordinates
        d_vectors = j_coords - i_coords # Determine direction vectors
        length = np.linalg.norm(d_vectors, axis=1) # Compute length of line objects
        cx = d_vectors[:, 0] / length # Compute the x-component of the direction cosine of line objects
        cy = d_vectors[:, 1] / length # Compute the y-component of the direction cosine of line objects
        local_x = np.column_stack((cx, cy)) # Determine local x-axis
        local_y = np.column_stack((-cy, cx)) # Determine local y-axis
        rotation_matrix = np.empty((len(length), 2, 2)) # Allocate rotation matrix 2x2
        rotation_matrix[:, 0, 0] = cx # Input value in row 1, column 1 rotation matrix
        rotation_matrix[:, 0, 1] = cy # Input value in row 1, column 2 rotation matrix
        rotation_matrix[:, 1, 0] = -cy # Input value in row 2, column 1 rotation matrix
        rotation_matrix[:, 1, 1] = cx # Input value in row 2, column 2 rotation matrix
        return (length, local_x, local_y, None, rotation_matrix)

# GENERATE LINE CONNECTIVITY
def _classify_connectivity_direction(dx, dy, dz, tol=1.0e-9):
    # Horizontal direction
    if dx > tol:
        horizontal = ConnectionDirection.RIGHT
    elif dx < -tol:
        horizontal = ConnectionDirection.LEFT
    elif dy > tol:
        horizontal = ConnectionDirection.FRONT
    elif dy < -tol:
        horizontal = ConnectionDirection.BACK
    else:
        horizontal = None
    # Vertical direction
    if dz > tol:
        vertical = ConnectionDirection.TOP
    elif dz < -tol:
        vertical = ConnectionDirection.BOTTOM
    else:
        vertical = None
    # Pure horizontal
    if vertical is None:
        return horizontal
    # Pure vertical
    if horizontal is None:
        return vertical
    combined_connection = {
        (ConnectionDirection.TOP, ConnectionDirection.LEFT): ConnectionDirection.TOP_LEFT,
        (ConnectionDirection.TOP, ConnectionDirection.RIGHT): ConnectionDirection.TOP_RIGHT,
        (ConnectionDirection.TOP, ConnectionDirection.FRONT): ConnectionDirection.TOP_FRONT,
        (ConnectionDirection.TOP, ConnectionDirection.BACK): ConnectionDirection.TOP_BACK,
        (ConnectionDirection.BOTTOM, ConnectionDirection.LEFT): ConnectionDirection.BOTTOM_LEFT,
        (ConnectionDirection.BOTTOM, ConnectionDirection.RIGHT): ConnectionDirection.BOTTOM_RIGHT,
        (ConnectionDirection.BOTTOM, ConnectionDirection.FRONT): ConnectionDirection.BOTTOM_FRONT,
        (ConnectionDirection.BOTTOM, ConnectionDirection.BACK): ConnectionDirection.BOTTOM_BACK,
    }
    return combined_connection[(vertical, horizontal)]

def _build_node_to_line_map(end_points_idx):
    node_map = defaultdict(list)
    for line_idx, (i_node, j_node) in enumerate(end_points_idx):
        node_map[int(i_node)].append(line_idx)
        node_map[int(j_node)].append(line_idx)
    return node_map
    
def generate_line_connectivity(end_points_idx, centroids):
    node_map = _build_node_to_line_map(end_points_idx)
    n = len(end_points_idx)
    candidate_list = []
    max_connections = 0
    for line_idx, (i_node, j_node) in enumerate(end_points_idx):
        candidates = np.unique(np.concatenate((node_map[int(i_node)], node_map[int(j_node)])))
        candidates = candidates[candidates != line_idx]
        candidate_list.append(candidates)
        if len(candidates) > max_connections:
            max_connections = len(candidates)
    connected_lines = np.full((n, max_connections), -1, dtype=np.int32)
    connection_direction = np.full((n, max_connections), -1, dtype=np.int32)
    for line_idx, candidates in enumerate(candidate_list):
        if candidates.size == 0:
            continue
        delta = centroids[candidates] - centroids[line_idx]
        directions = np.empty(len(candidates), dtype=np.int32)
        for k, (dx, dy, dz) in enumerate(delta):
            directions[k] = _classify_connectivity_direction(dx, dy, dz)
        m = len(candidates)
        connected_lines[line_idx, :m] = candidates
        connection_direction[line_idx, :m] = directions
    return connected_lines, connection_direction

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