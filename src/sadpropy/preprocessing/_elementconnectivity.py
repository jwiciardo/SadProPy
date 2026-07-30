import numpy as np
from collections import defaultdict
from ._preproc_class import ConnectionEnd
from ._sectiondata import get_section_properties
from sadpropy.utility.helperfunc import transform_to_global_axes, transform_to_local_axes
from sadpropy.utility.tolerance import Tolerance

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
    n = len(end_nodes_index) # Determine number of rows in end nodes index
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
    for idx in range(n): # Loop over index of end nodes data
        m = len(connected_elements[idx]) # Determine number of connected elements
        if m == 0: # Set condition if there is no connected element then skip the remaining code
            continue
        element_connectivity[idx, :m] = connected_elements[idx] # Store connected elements in element connectivity array
        connections_end[idx, :m] = connection_end[idx] # Store connection end class into connection end array
    return element_connectivity, connections_end

# AUTOGENERATE END OFFSETS
def _compute_offsets_length(
        element_type,
        centroids,
        rotation_matrix,
        filtered_element_connectivity,
        filtered_connections_end,
        sec_dim,
        tol=Tolerance.LENGTH,
    ):
    n = len(filtered_element_connectivity) # Determine number of rows in filtered elements connectivity
    offsets_length = np.zeros((n, 2), dtype=np.float64) # Predefined offsets length array
    for ele_idx, connected_elements in enumerate(filtered_element_connectivity): # Loop over filtered elements connectivity
        connection_end = filtered_connections_end[ele_idx] # Retrieve connection end 
        current_ele_centroids = centroids[ele_idx] # Retrieve centroids for current element index
        connected_ele_centroids = centroids[connected_elements] # Retrieve centroids for connected elements
        delta = connected_ele_centroids - current_ele_centroids # Compute delta, difference between connected elements centroid and current element centroids
        delta_local = transform_to_local_axes(
            values=delta,
            rotation_matrix=rotation_matrix[ele_idx],
        ) # Transform delta to local axes
        dx = delta_local[:, 0] # Unpack dx from delta local
        dy = delta_local[:, 1] # Unpack dy from delta local
        dz = delta_local[:, 2] # Unpack dz from delta local
        iend_offset_length = 0.0 # Predefined I-end offset length
        jend_offset_length = 0.0 # Predefined J-end offset length
        for conn_element, conn_end, dy_i, dz_i in zip(connected_elements, connection_end, dy, dz):
            h_conn, b_conn = sec_dim[conn_element] # Retrieve section dimension
            offset_length = 0.0 # Predefined offset length
            if element_type[ele_idx] == "Column": # Set condition if element type is "Column"
                offset_length = h_conn # If True, compute offset length
            else: # Otherwise, if element type is "Beam"
                if np.abs(dz_i) < tol: # Set condition if beam lies on xy plane
                    offset_length = h_conn / 2.0 # Compute offset length  
                elif np.abs(dy_i) < tol: # Set condition if beam lies on xz plane
                    offset_length = b_conn / 2.0 # Compute offset length 
            if conn_end == ConnectionEnd.I_End: # Set condition if connected end is on I-End
                iend_offset_length = max(iend_offset_length, offset_length) if element_type[ele_idx] != "Column" else 0.0 # If True, compute I-end offset length
            else:
                jend_offset_length = max(jend_offset_length, offset_length) # Otherwise, compute J-end offset length
        offsets_length[ele_idx] = (iend_offset_length, jend_offset_length) # Store I-End and J-End offsets length into offsets length array
    return offsets_length

def autogenerate_offsets_length(secs_list, sec_class, sec_idx, element_type, element_connectivity, connections_end, centroids, rotation_matrix, tol=Tolerance.LENGTH):
    n = len(element_connectivity) # Determine number of rows in element connectivity
    filtered_element_connectivity = [] # Predefined filtered element connectivity list
    filtered_connections_end = [] # Predefined filtered connections end list
    for ele_idx, connected_elements in enumerate(element_connectivity): # Loop over element connectivity
        connected_elements = connected_elements[connected_elements != -1] # Filter none (-1) values in connected elements
        connection_end = connections_end[ele_idx] # Retrieve connections end data
        connection_end = connection_end[connection_end != -1] # Filter none (-1) values in connection end
        current_ele_centroids = centroids[ele_idx] # Retrieve centroids for current element index
        connected_ele_centroids = centroids[connected_elements] # Retrieve centroids for connected elements
        delta = connected_ele_centroids - current_ele_centroids # Compute delta, difference between connected elements centroid and current element centroids 
        delta_local = transform_to_local_axes(
            values=delta,
            rotation_matrix=rotation_matrix[ele_idx],
        ) # Transform delta to local axes
        dx = delta_local[:, 0] # Unpack dx from delta local
        dy = delta_local[:, 1] # Unpack dy from delta local
        dz = delta_local[:, 2] # Unpack dz from delta local

        if element_type[ele_idx] == "Beam": # Set condition if element type is "Beam"
            xy_plane = np.abs(dz) < tol # Define mask for local xy plane
            not_collinear = np.abs(dy) >= tol # Define mask for non collinear element
            mask = xy_plane & not_collinear # Define mask to filter beam elements
            filtered_element_connectivity.append(connected_elements[mask]) # Append filtered result to filtered element connectivity
            filtered_connections_end.append(connection_end[mask]) # Append filtered result to filtered connection end
        elif element_type[ele_idx] == "Column": # Set condition if element type is "Column"
            # Local xy plane
            xy_plane = np.abs(dz) < tol # Define mask for local xy plane
            not_collinear_xy = np.abs(dy) >= tol # Define mask for non collinear element in local xy plane
            xy_mask = xy_plane & not_collinear_xy # Define mask to filter column elements in local xy plane
            filtered_elements_xy = connected_elements[xy_mask] # Retreive filtered result of connected elements in local xy plane
            filtered_end_xy = connection_end[xy_mask] # Retrieve filtered result of connection end in local xy plane
            # Local xz plane
            xz_plane = np.abs(dy) < tol # Define mask for local xz plane
            not_collinear_xz = np.abs(dz) >= tol # Define mask for non collinear element in local xz plane
            xz_mask = xz_plane & not_collinear_xz # Define mask to filter column elements in local xz plane
            filtered_elements_xz = connected_elements[xz_mask] # Retreive filtered result of connected elements in local xz plane
            filtered_ends_xz = connection_end[xz_mask] # Retrieve filtered result of connection end in local xz plane
            filtered_element_connectivity.append(np.concatenate((filtered_elements_xy, filtered_elements_xz))) # Append filtered result to filtered element connectivity
            filtered_connections_end.append(np.concatenate((filtered_end_xy, filtered_ends_xz))) # Append filtered result to filtered connection end
    sec_props = get_section_properties(
        secs_list=secs_list,
        sec_class=sec_class,
        sec_idx=sec_idx,
        props_name=["h", "b"],
    ) # Get section properties of all beamcolumn elements
    sec_dim = np.asarray(sec_props) # Define section dimensions
    offsets_length = _compute_offsets_length(
        element_type=element_type,
        centroids=centroids,
        rotation_matrix=rotation_matrix,
        filtered_element_connectivity=filtered_element_connectivity,
        filtered_connections_end=filtered_connections_end,
        sec_dim=sec_dim,
    ) # Retrieve offsets length
    return offsets_length

def generate_end_offsets(offsets_length, rotation_matrix):
    n = len(offsets_length)
    end_offsets = np.zeros((n, 6), dtype=np.float64) # Predefined end offsets array
    for ele_idx in range(n):
        iend_offset_length, jend_offset_length = offsets_length[ele_idx] # Unpack offsets length
        iend_offset_local_vector = np.array((iend_offset_length, 0.0, 0.0), dtype=np.float64) # Define I-End offset local vector
        iend_offset_global_vector = transform_to_global_axes(
            values=iend_offset_local_vector,
            rotation_matrix=rotation_matrix[ele_idx],
        ) # Transform I-End offset local vector to global axes
        jend_offset_local_vector = np.array((-jend_offset_length, 0.0, 0.0), dtype=np.float64) # Define J-End offset local vector
        jend_offset_global_vector = transform_to_global_axes(
            values=jend_offset_local_vector,
            rotation_matrix=rotation_matrix[ele_idx],
        ) # Transform J-End offset local vector to global axes
        offsets_vector = np.concatenate((iend_offset_global_vector, jend_offset_global_vector)) # Concatenate I-End and J-End offsets vector
        end_offsets[ele_idx] = offsets_vector # Store offsets vector into end offsets array
    return end_offsets