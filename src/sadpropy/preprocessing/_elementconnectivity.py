import numpy as np
from collections import defaultdict
from ._preproc_class import (
    PropertiesClassRegistry,
    SectionShape,
    ConnectionEnd,
)
from ._sectiondata import get_section_properties
from sadpropy.utility._exceptions import ValidationError
from sadpropy.utility.helperfunc import project_to_local_axes

# GENERATE LOCAL AXES
def _compute_beamcolumn_element_centroids(inode_coords, jnode_coords):
    return (inode_coords + jnode_coords) / 2.0

def generate_beamcolumn_element_local_axes(nodes, end_nodes_index, ndim):
    coords = nodes.coords # Retrieve nodes coordinates
    inode_coords = coords[end_nodes_index[:, ConnectionEnd.I_End]] # Retrieve I-end node coordinates from node coordinates
    jnode_coords = coords[end_nodes_index[:, ConnectionEnd.J_End]] # Retrieve J-end node coordinates from node coordinates
    centroids = _compute_beamcolumn_element_centroids(inode_coords=inode_coords, jnode_coords=jnode_coords) # Compute centroids of elements
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
        rotation_matrix = np.stack((local_x, local_y, local_z), axis=2) # Build rotation matrix 3x3 for transforming global to local axes and local to global axes
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
        rotation_matrix = np.stack((local_x, local_y), axis=2) # Build rotation matrix 2x2 for transforming global to local axes and local to global axes
        return (centroids, length, local_x, local_y, None, rotation_matrix)

# GENERATE ELEMENT CONNECTIVITY
def _get_parent_node(nodes, child_node):
    nodes_generated_from = nodes.generated_from # Retrieve parent name of generated node
    node_name_to_idx = nodes.name_to_idx # Retrieve node index from node name
    if nodes_generated_from[child_node] != "": # Set condition if parent name of generated node is not empty
        parent_node = node_name_to_idx[nodes_generated_from[child_node]] # If True, return parent node index
    else:
        parent_node = child_node # If False, generated node is parent node then return generated node index
    return parent_node

def _map_node_to_beamcolumn_element(nodes, end_nodes_index):
    node_to_beamcolumn_element = defaultdict(list) # Predefined node to element dictionary
    for ele_idx, (iend_node_idx, jend_node_idx) in enumerate(end_nodes_index): # Loop over end nodes index
        iend_node_idx = _get_parent_node(nodes=nodes, child_node=iend_node_idx) # Get parrent node of I-end node
        jend_node_idx = _get_parent_node(nodes=nodes, child_node=jend_node_idx) # Get parrent node of J-end node
        node_to_beamcolumn_element[int(iend_node_idx)].append(ele_idx) # Append line index into key: I-end point index
        node_to_beamcolumn_element[int(jend_node_idx)].append(ele_idx) # Append line index into key: J-end point index
    return node_to_beamcolumn_element

def generate_beamcolumn_element_connectivity(nodes, end_nodes_index):
    node_to_beamcolumn_element_map = _map_node_to_beamcolumn_element(
        nodes=nodes,
        end_nodes_index=end_nodes_index
    ) # Build node to beam-column element map
    print(node_to_beamcolumn_element_map)
    n = len(end_nodes_index) # Determine number of end nodes data
    connected_elements = [] # Predefined connected elements list
    connection_end = [] # Predefined connection end list
    max_connections = 0 # Predefined maximum number of connections
    for ele_idx, (iend_node_idx, jend_node_idx) in enumerate(end_nodes_index): # Loop over end nodes index
        iend_node_idx = _get_parent_node(nodes=nodes, child_node=iend_node_idx) # Retrieve parent node of I-end node
        jend_node_idx = _get_parent_node(nodes=nodes, child_node=jend_node_idx) # Retrieve parent node of J-end node
        conn_element = [] # Predefined connected element list
        conn_end = [] # Predefined connection end list
        for i_ele_idx in node_to_beamcolumn_element_map[iend_node_idx]: # Loop over element index of I-end node
            if i_ele_idx == ele_idx: # Set condition if element index of I-end node is same as element index in current looping then skip the remaining code
                continue
            conn_element.append(i_ele_idx) # Append element index of I-end node into connected element list
            conn_end.append(ConnectionEnd.I_End) # Append end node class into end node connection list
        for j_ele_idx in node_to_beamcolumn_element_map[jend_node_idx]: # Loop over element index of J-end node
            if j_ele_idx == ele_idx: # Set condition if element index of J-end node is same as element index in current looping then skip the remaining code
                continue
            conn_element.append(j_ele_idx) # Append element index of J-end node into connected element list
            conn_end.append(ConnectionEnd.J_End) # Append end node class into end node connection list
        connected_elements.append(np.asarray(conn_element, dtype=np.int32)) # Append connected element list into connected elements list
        connection_end.append(np.asarray(conn_end, dtype=np.int32)) # Append connection end list into connections end list
        max_connections = max(max_connections, len(connected_elements)) # Determine maximum number of connections
    element_connectivity = np.full((n, max_connections), -1, dtype=np.int32) # Predefined element connectivity array (N, Max_Conn)
    connections_end = np.full((n, max_connections), -1, dtype=np.int32) # Predefined connections end array (N, Max_Conn)
    for i in range(n): # Loop over index of end nodes data
        m = len(connected_elements[i]) # Determine number of connected elements
        if m == 0: # Set condition if there is no connected element then skip the remaining code
            continue
        element_connectivity[i, :m] = connected_elements[i] # Store connected elements in element connectivity array
        connections_end[i, :m] = connection_end[i] # Store connection end class into connection end array
    return element_connectivity, connections_end

# AUTOGENERATE END OFFSETS
def _compute_end_offsets_values(
        element_type,
        centroids,
        local_x,
        rotation_matrix,
        connected_elements,
        connected_ends,
        sec_dim,
        tol=1e-9,
    ):
    n = len(connected_elements) # Determine number of connected elements
    offsets_length = np.zeros((n, 2), dtype=np.float64)
    for ele_idx, conn_elements in enumerate(connected_elements): # Loop over connected elements
        conn_ends = connected_ends[ele_idx]

        current_ele_centroids = centroids[ele_idx]
        connected_ele_centroids = centroids[conn_elements]
        delta = connected_ele_centroids - current_ele_centroids

        iend_offset_length = 0.0
        jend_offset_length = 0.0
        for conn_ele, conn_end, d in zip(conn_elements, conn_ends, delta):
            dx, dy, dz = project_to_local_axes(
                values=d,
                rotation_matrix=rotation_matrix[ele_idx],
            )
            conn_h, conn_b = sec_dim[conn_ele]
            if element_type[ele_idx] == "Column": # Set condition if element type is column
                offset_length = conn_h / 2.0 # If yes, compute offset length  
            else: # Otherwise, if element type is beam
                if np.abs(dz) < tol: # Set condition if beam lies on xy plane
                    offset_length = conn_h / 2.0 # Compute offset length  
                elif np.abs(dy) < tol: # Set condition if beam lies on xz plane
                    offset_length = conn_b / 2.0 # Compute offset length 
            if conn_end == ConnectionEnd.I_End: # Set condition if connected end == I-end class
                iend_offset_length = max(iend_offset_length, offset_length) # If yes, compute I-end offset length
            else:
                jend_offset_length = max(jend_offset_length, offset_length) # Otherwise, compute J-end offset length
        lx = local_x[ele_idx]
        i_offset_vector = -iend_offset_length * lx
        j_offset_vector =  jend_offset_length * lx


    return i_offset_vector, j_offset_vector


def autogenerate_end_offsets(secs_list, sec_class, sec_idx, element_type, element_connectivity, connections_end, centroids, local_x, rotation_matrix, tol=1e-9):
    n = len(element_connectivity) # Determine number of 
    connected_elements = []
    connected_ends = []
    for ele_idx, conn_elements in enumerate(element_connectivity):
        conn_elements = conn_elements[conn_elements != -1]
        conn_ends = connections_end[ele_idx]
        conn_ends = conn_ends[conn_ends != -1]
        current_ele_centroids = centroids[ele_idx]
        connected_ele_centroids = centroids[conn_elements]
        delta = connected_ele_centroids - current_ele_centroids
        delta_local = project_to_local_axes(
            values=delta,
            rotation_matrix=rotation_matrix[ele_idx],
        )
        dx = delta_local[:, 0]
        dy = delta_local[:, 1]
        dz = delta_local[:, 2]

        if element_type[ele_idx] == "Beam":
            xy_plane = np.abs(dz) < tol
            not_collinear = np.abs(dy) >= tol
            mask = xy_plane & not_collinear
            connected_elements.append(conn_elements[mask])
            connected_ends.append(conn_ends[mask])
        elif element_type[ele_idx] == "Column":
            # Local xy plane
            xy_plane = np.abs(dz) < tol
            not_collinear_xy = np.abs(dy) >= tol
            xy_mask = xy_plane & not_collinear_xy
            conn_elements_xy = conn_elements[xy_mask]
            conn_ends_xy = conn_ends[xy_mask]
            # Local xz plane
            xz_plane = np.abs(dy) < tol
            not_collinear_xz = np.abs(dz) >= tol
            xz_mask = xz_plane & not_collinear_xz
            conn_elements_xz = conn_elements[xz_mask]
            conn_ends_xz = conn_ends[xz_mask]
            connected_elements.append(np.concatenate((conn_elements_xy, conn_elements_xz)))
            connected_ends.append(np.concatenate((conn_ends_xy, conn_ends_xz)))
    sec_props = get_section_properties(
        secs_list=secs_list,
        sec_class=sec_class,
        sec_idx=sec_idx,
        props_name=["h", "b"],
    )
    sec_dim = np.asarray(sec_props)
    i_offset_vector, j_offset_vector = _compute_end_offsets_values(
        element_type=element_type,
        centroids=centroids,
        local_x=local_x,
        rotation_matrix=rotation_matrix,
        connected_elements=connected_elements,
        connected_ends=connected_ends,
        sec_dim=sec_dim,
    )

    print(connected_elements, len(connected_elements))

    return 0