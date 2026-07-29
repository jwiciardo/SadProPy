import numpy as np
from collections import defaultdict
from ._preproc_class import (
    PropertiesClassRegistry,
    SectionShape,
    ConnectionEnd,
)
from sadpropy.utility._exceptions import ValidationError

# GENERATE LOCAL AXES
def _compute_beam_element_centroids(inode_coords, jnode_coords):
    return (inode_coords + jnode_coords) / 2.0

def generate_beam_element_local_axes(nodes, end_nodes_index, ndim):
    coords = nodes.coords # Retrieve nodes coordinates
    inode_coords = coords[end_nodes_index[:, ConnectionEnd.I_End]] # Retrieve I-end node coordinates from node coordinates
    jnode_coords = coords[end_nodes_index[:, ConnectionEnd.J_End]] # Retrieve J-end node coordinates from node coordinates
    centroids = _compute_beam_element_centroids(inode_coords=inode_coords, jnode_coords=jnode_coords) # Compute centroids of elements
    if ndim == 3: # 3D Structure
        d_vectors = jnode_coords - inode_coords # Determine direction vectors
        length = np.linalg.norm(d_vectors, axis=1) # Compute length of elements
        local_x = d_vectors / length[:, None] # Determine local x-axis
        reference = np.tile(np.array([0.0, 0.0, 1.0]), (len(local_x), 1)) # Define reference direction, default is toward global Z-axis
        vertical = np.abs(local_x[:, 2]) > 0.99 # Build masking for vertical elements
        reference[vertical] = np.array([1.0, 0.0, 0.0]) # Change reference direction for vertical elements which is toward global X-axis
        local_z = np.cross(local_x, reference) # Determine local z-axis using cross product of local x-axis and reference direction
        local_z /= np.linalg.norm(local_z, axis=1)[:, None] # Normalise local z-axis
        local_y = np.cross(local_z, local_x) # Determine local y-axis using cross product of local z-axis and local x-axis
        local_y /= np.linalg.norm(local_y, axis=1)[:, None] # Normalise local y-axis
        rotation_matrix = np.stack((local_x, local_y, local_z), axis=1) # Build rotation matrix 3x3 for transforming global to local axes and local to global axes
        return (centroids, length, local_x, local_y, local_z, rotation_matrix)
    else: # 2D Structure
        inode_coords = inode_coords[:2] # Retrieve I-end node coordinates (X, Y)
        jnode_coords = jnode_coords[:2] # Retrieve J-end node coordinates (X, Y)
        d_vectors = jnode_coords - inode_coords # Determine direction vectors
        length = np.linalg.norm(d_vectors, axis=1) # Compute length of elements
        cx = d_vectors[:, 0] / length # Compute the x-component of the direction cosine of elements
        cy = d_vectors[:, 1] / length # Compute the y-component of the direction cosine of elements
        local_x = np.column_stack((cx, cy)) # Determine local x-axis
        local_y = np.column_stack((-cy, cx)) # Determine local y-axis
        rotation_matrix = np.empty((len(length), 2, 2)) # Predefined rotation matrix 2x2
        rotation_matrix[:, 0, 0] = cx # Input value in row 1, column 1 rotation matrix
        rotation_matrix[:, 0, 1] = cy # Input value in row 1, column 2 rotation matrix
        rotation_matrix[:, 1, 0] = -cy # Input value in row 2, column 1 rotation matrix
        rotation_matrix[:, 1, 1] = cx # Input value in row 2, column 2 rotation matrix
        return (centroids, length, local_x, local_y, None, rotation_matrix)

# GENERATE ELEMENT CONNECTIVITY
def _get_parent_node(nodes, child_node):
    nodes_generated_from = nodes.generated_from
    node_name_to_idx = nodes.name_to_idx
    if nodes_generated_from[child_node] != "":
        parent_node = node_name_to_idx[nodes_generated_from[child_node]]
    else:
        parent_node = child_node
    return parent_node

def _map_node_to_beam_element(nodes, end_nodes_index):
    nodes_generated_from = nodes.generated_from
    node_name_to_idx = nodes.name_to_idx
    node_to_beam_element = defaultdict(list) # Predefined node to element dictionary
    for ele_idx, (iend_node_idx, jend_node_idx) in enumerate(end_nodes_index): # Loop over end nodes index
        iend_node_idx = _get_parent_node(nodes=nodes, child_node=iend_node_idx)
        jend_node_idx = _get_parent_node(nodes=nodes, child_node=jend_node_idx)
        node_to_beam_element[int(iend_node_idx)].append(ele_idx) # Append line index into key: I-end point index
        node_to_beam_element[int(jend_node_idx)].append(ele_idx) # Append line index into key: J-end point index
    return node_to_beam_element

def generate_beam_element_connectivity(nodes, end_nodes_index):
    node_to_beam_element_map = _map_node_to_beam_element(
        nodes=nodes,
        end_nodes_index=end_nodes_index
    ) # Build node to beam-column element map
    n = len(end_nodes_index) # Determine number of end nodes data
    connected_elements = [] # Predefined connected elements list
    end_nodes_connections = [] # Predefined end nodes connections list
    max_connections = 0 # Predefined maximum number of connections
    for ele_idx, (iend_node_idx, jend_node_idx) in enumerate(end_nodes_index): # Loop over end nodes 
        iend_node_idx = _get_parent_node(nodes=nodes, child_node=iend_node_idx)
        jend_node_idx = _get_parent_node(nodes=nodes, child_node=jend_node_idx)
        conn_ele = [] # Predefined connected element list
        end_node_conn = [] # Predefined end node connection list
        for ele_idx_i in node_to_beam_element_map[iend_node_idx]: # Loop over element index of I-end node
            if ele_idx_i == ele_idx: # Set condition if element index of I-end node is same as element index in current looping then skip the remaining code
                continue
            conn_ele.append(ele_idx_i) # Append element index of I-end node into connected element list
            end_node_conn.append(ConnectionEnd.I_End) # Append end node class into end node connection list
        for ele_idx_j in node_to_beam_element_map[jend_node_idx]: # Loop over element index of J-end node
            if ele_idx_j == ele_idx: # Set condition if element index of J-end node is same as element index in current looping then skip the remaining code
                continue
            conn_ele.append(ele_idx_j) # Append element index of J-end node into connected element list
            end_node_conn.append(ConnectionEnd.J_End) # Append end node class into end node connection list
        connected_elements.append(np.asarray(conn_ele, dtype=np.int32)) # Append connected element list into connected elements list
        end_nodes_connections.append(np.asarray(end_node_conn, dtype=np.int32)) # Append end node connection list into end nodes connections list
        max_connections = max(max_connections, len(connected_elements)) # Determine maximum number of connections
    element_connectivity = np.full((n, max_connections), -1, dtype=np.int32) # Predefined elements connectivity array (N, Max_con)
    connection_end = np.full((n, max_connections), -1, dtype=np.int32) # Predefined connection end array (N, Max_con)
    for i in range(n): # Loop over element index
        m = len(connected_elements[i]) # Determine number of connected elements
        if m == 0: # Set condition if there is no connection then skip the remaining code
            continue
        element_connectivity[i, :m] = connected_elements[i] # Store connected elements in element connectivity array
        connection_end[i, :m] = end_nodes_connections[i] # Store end node into connection end array
    return element_connectivity, connection_end

def autogenerate_end_offsets(element_connectivity, connection_end, sec_class, sec_idx, secs_list, sec_data):
    n = len(element_connectivity)
    props_class = PropertiesClassRegistry()._get_sec_props_class(sec_class=sec_class)
    end_offsets = np.zeros((n, 2), dtype=np.float64)
    for i in range(n):
        for j in range(element_connectivity.shape[1]):
            connected_line = element_connectivity[i, j]
            if connected_line < 0:
                continue
            if sec_data[i].sec_shape == SectionShape().shape["Rectangular"]:
                height, width = sec_data[i].properties[props_class[i].h, props_class[i]]
            offset = _calculate_offset_at_connection(
                connected_line=connected_line,
                sec_class=sec_class[i],
                sec_idx=sec_idx[i],
                secs_list=secs_list,
            )

            if connection_end[i, j] == ConnectionEnd.I_End:
                end_offsets[i, 0] = max(end_offsets[i, 0], offset)
            else:
                end_offsets[i, 1] = max(end_offsets[i, 1], offset)
    return end_offsets