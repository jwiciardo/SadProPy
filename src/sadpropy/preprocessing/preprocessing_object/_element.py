import numpy as np
from collections import defaultdict
from ..preprocessing_class_index import ElementType, ConnectionEnd
from ._section import _get_section_dimensions
from ...utility.helper import transform_to_global_axes, transform_to_local_axes, get_parent_node
from ...utility.tolerance import Tolerance

# GENERATE LOCAL AXES
def _compute_element_centroids(inode_coords, jnode_coords):
    return (inode_coords + jnode_coords) / 2.0

def _generate_element_local_axes(nodes, end_nodes_index, ndim):
    coords = nodes.coords # Retrieve nodes coordinates
    inode_coords = coords[end_nodes_index[:, ConnectionEnd.I_End]] # Retrieve I-end node coordinates from node coordinates
    jnode_coords = coords[end_nodes_index[:, ConnectionEnd.J_End]] # Retrieve J-end node coordinates from node coordinates
    centroids = _compute_element_centroids(inode_coords=inode_coords, jnode_coords=jnode_coords) # Compute centroids of elements
    if ndim == 3: # 3D Structure
        d_vectors = jnode_coords - inode_coords # Determine direction vectors
        length = np.linalg.norm(d_vectors, axis=1) # Compute length of elements
        vector_x = d_vectors / length[:, None] # Determine vector x-axis
        reference = np.tile(np.array([0.0, 0.0, 1.0]), (len(vector_x), 1)) # Define reference direction, default is toward global Z-axis
        vertical = np.abs(vector_x[:, 2]) > 0.99 # Build masking for vertical elements
        reference[vertical] = np.array([1.0, 0.0, 0.0]) # Change reference direction for vertical elements which is toward global X-axis
        vector_z = np.cross(vector_x, reference) # Determine vector z-axis using cross product of vector x-axis and reference direction
        vector_z /= np.linalg.norm(vector_z, axis=1)[:, None] # Normalise vector z-axis
        vector_y = np.cross(vector_z, vector_x) # Determine vector y-axis using cross product of vector z-axis and vector x-axis
        vector_y /= np.linalg.norm(vector_y, axis=1)[:, None] # Normalise vector y-axis
        rotation_matrices = np.stack((vector_x, vector_y, vector_z), axis=2) # Build rotation matrices 3x3 for transforming global to local axes and local to global axes
        return (centroids, vector_x, vector_y, vector_z, rotation_matrices)
    else: # 2D Structure
        inode_coords = inode_coords[:2] # Retrieve I-end node coordinates (X, Y)
        jnode_coords = jnode_coords[:2] # Retrieve J-end node coordinates (X, Y)
        d_vectors = jnode_coords - inode_coords # Determine direction vectors
        length = np.linalg.norm(d_vectors, axis=1) # Compute length of elements
        cx = d_vectors[:, 0] / length # Compute the x-component of the direction cosine of elements
        cy = d_vectors[:, 1] / length # Compute the y-component of the direction cosine of elements
        vector_x = np.column_stack((cx, cy)) # Determine vector x-axis
        vector_y = np.column_stack((-cy, cx)) # Determine vector y-axis
        rotation_matrices = np.stack((vector_x, vector_y), axis=2) # Build rotation matrices 2x2 for transforming global to local axes and local to global axes
        return (centroids, vector_x, vector_y, None, rotation_matrices)

# GENERATE ELEMENT CONNECTIVITY
def _map_node_to_element(iend_nodes_idx, jend_nodes_idx):
    node_to_beamcolumn_element = defaultdict(list) # Predefined node to element dictionary
    for ele_idx, (iend_node_idx, jend_node_idx) in enumerate(zip(iend_nodes_idx, jend_nodes_idx)): # Loop over end nodes index
        node_to_beamcolumn_element[int(iend_node_idx)].append(ele_idx) # Append element index into key: I-end node index
        node_to_beamcolumn_element[int(jend_node_idx)].append(ele_idx) # Append element index into key: J-end node index
    return node_to_beamcolumn_element

def _generate_element_connectivity(nodes, end_nodes_index):
    n = len(end_nodes_index) # Determine number of rows in end nodes index
    iend_nodes_idx = get_parent_node(nodes=nodes, child_node=end_nodes_index[:,0]) # Get parent node of I-end node
    jend_nodes_idx = get_parent_node(nodes=nodes, child_node=end_nodes_index[:,1]) # Get parent node of J-end node
    node_to_beamcolumn_element_map = _map_node_to_element(
        iend_nodes_idx=iend_nodes_idx,
        jend_nodes_idx=jend_nodes_idx,
    ) # Build node to beam-column element map
    connected_elements = [] # Predefined connected elements list
    shared_nodes = []  # Predefined shared nodes list
    elements_end = [] # Predefined current elements end list
    connected_elements_end = [] # Predefined connected elements end list
    max_connections = 0 # Predefined maximum number of connections
    for ele_idx in range(n): # Loop over end nodes index
        conn_element = [] # Predefined connected element list
        shared_node = [] # Predefined share node list
        element_end = [] # Predefined current element end list
        conn_element_end = [] # Predefined connected element end list
        iend_node_idx = iend_nodes_idx[ele_idx] # Retrieve I-end node index
        for conn_ele_idx_iend in node_to_beamcolumn_element_map[iend_node_idx]: # Loop over connected element indices on I-end node
            if conn_ele_idx_iend == ele_idx: # Set condition if connected element index on I-end node is same as current element index then skip the remaining code
                continue
            conn_element.append(conn_ele_idx_iend) # Append connected element index on I-end node into connected element list
            shared_node.append(iend_node_idx) # Append I-end node index into shared node list
            element_end.append(ConnectionEnd.I_End) # Append I-end node class into current element end list
            if iend_nodes_idx[conn_ele_idx_iend] == iend_node_idx: # Set condition if end node of connected element index is on I-end node
                conn_element_end.append(ConnectionEnd.I_End) # If True, append I-end node class into connected element end list
            else:
                conn_element_end.append(ConnectionEnd.J_End) # Otherwise, append J-end node class into connected element end list

        jend_node_idx = jend_nodes_idx[ele_idx] # Retrieve J-end node index
        for conn_ele_idx_jend in node_to_beamcolumn_element_map[jend_node_idx]: # Loop over connected element indices on J-end node
            if conn_ele_idx_jend == ele_idx: # Set condition if connected element index on J-end node is same as current element index then skip the remaining code
                continue
            conn_element.append(conn_ele_idx_jend) # Append connected element index on J-end node into connected element list
            shared_node.append(jend_node_idx) # Append J-end node index into shared node list
            element_end.append(ConnectionEnd.J_End) # Append J-end node class into current element end list
            if jend_nodes_idx[conn_ele_idx_jend] == jend_node_idx: # Set condition if end node of connected element index is on J-end node
                conn_element_end.append(ConnectionEnd.J_End) # If True, append J-end node class into connected element end list
            else:
                conn_element_end.append(ConnectionEnd.I_End) # Otherwise, append I-end node class into connected element end list

        connected_elements.append(np.asarray(conn_element, dtype=np.int32)) # Append connected element list into connected elements list
        shared_nodes.append(np.asarray(shared_node, dtype=np.int32)) # Append shared node list into shared nodes list
        elements_end.append(np.asarray(element_end, dtype=np.int32)) # Append current element end list into current elements end list
        connected_elements_end.append(np.asarray(conn_element_end, dtype=np.int32)) # Append connected element end list into connected elements end list
        max_connections = max(max_connections, len(conn_element)) # Determine maximum number of connections
    elements_connectivity = np.full((n, max_connections), -1, dtype=np.int32) # Predefined elements connectivity array (N, Max. Conn)
    shared_connected_nodes = np.full((n, max_connections), -1, dtype=np.int32) # Predefined shared connected nodes array (N, Max. Conn)
    current_elements_end = np.full((n, max_connections), -1, dtype=np.int32) # Predefined current elements end array (N, Max. Conn)
    neighbour_elements_end = np.full((n, max_connections), -1, dtype=np.int32) # Predefined neighbour elements end array (N, Max. Conn)
    for ele_idx in range(n): # Loop over end nodes index
        m = len(connected_elements[ele_idx]) # Determine number of connected elements
        if m == 0: # Set condition if there is no connected element then skip the remaining code
            continue
        elements_connectivity[ele_idx, :m] = connected_elements[ele_idx] # Store connected elements into elements connectivity array
        shared_connected_nodes[ele_idx, :m] = shared_nodes[ele_idx] # Store shared nodes into shared connected nodes array
        current_elements_end[ele_idx, :m] = elements_end[ele_idx] # Store elements end class into current elements end class array
        neighbour_elements_end[ele_idx, :m] = connected_elements_end[ele_idx] # Store connected elements end class into neighbour elements end class array
    return elements_connectivity, shared_connected_nodes, current_elements_end, neighbour_elements_end

# AUTOGENERATE END OFFSETS
def _compute_offsets_length(
        element_type,
        centroids,
        rotation_matrices,
        filtered_elements_connectivity,
        filtered_current_elements_end,
        sec_dim,
        tol=Tolerance.LENGTH,
    ):
    n = len(filtered_elements_connectivity) # Determine number of rows in filtered elements connectivity
    offsets_length = np.zeros((n, 2), dtype=np.float64) # Predefined offsets length array
    for ele_idx, connected_elements in enumerate(filtered_elements_connectivity): # Loop over filtered elements connectivity
        elements_end = filtered_current_elements_end[ele_idx] # Retrieve current elements end 
        current_ele_centroids = centroids[ele_idx] # Retrieve centroids for current element
        connected_ele_centroids = centroids[connected_elements] # Retrieve centroids for connected elements
        delta = connected_ele_centroids - current_ele_centroids # Compute delta, difference between connected elements centroids and current element centroids
        delta_local = transform_to_local_axes(
            values=delta,
            rotation_matrices=rotation_matrices[ele_idx],
        ) # Transform delta to local axes
        dx = delta_local[:, 0] # Unpack dx from delta local
        dy = delta_local[:, 1] # Unpack dy from delta local
        dz = delta_local[:, 2] # Unpack dz from delta local

        iend_offset_length = 0.0 # Predefined I-end offset length
        jend_offset_length = 0.0 # Predefined J-end offset length
        for conn_element, element_end, dy_i, dz_i in zip(connected_elements, elements_end, dy, dz): # Loop over elements connectivity
            h_conn, b_conn = sec_dim[conn_element] # Retrieve section dimension
            offset_length = 0.0 # Predefined offset length
            if element_type[ele_idx] == ElementType.Column: # Set condition if element type is "Column"
                offset_length = h_conn # If True, compute offset length
            else: # Otherwise, if element type is "Beam"
                if np.abs(dz_i) < tol: # Set condition if beam lies on xy plane
                    offset_length = h_conn / 2.0 # Compute offset length  
                elif np.abs(dy_i) < tol: # Set condition if beam lies on xz plane
                    offset_length = b_conn / 2.0 # Compute offset length 
            if element_end == ConnectionEnd.I_End: # Set condition if current element end is on I-end
                iend_offset_length = max(iend_offset_length, offset_length) if element_type[ele_idx] != ElementType.Column else 0.0 # If True, compute I-end offset length
            else:
                jend_offset_length = max(jend_offset_length, offset_length) # Otherwise, compute J-end offset length
        offsets_length[ele_idx] = (iend_offset_length, jend_offset_length) # Store I-end and J-end offsets length into offsets length array
    return offsets_length

def _autogenerate_offsets_length(sections, sec_idx, element_type, elements_connectivity, current_elements_end, centroids, rotation_matrices, tol=Tolerance.LENGTH):
    filtered_elements_connectivity = [] # Predefined filtered elements connectivity list
    filtered_current_elements_end = [] # Predefined filtered current elements end list
    for ele_idx, connected_elements in enumerate(elements_connectivity): # Loop over elements connectivity
        connected_elements = connected_elements[connected_elements != -1] # Filter none (-1) values in connected elements
        element_end = current_elements_end[ele_idx] # Retrieve current element end data
        element_end = element_end[element_end != -1] # Filter none (-1) values in element end
        current_ele_centroids = centroids[ele_idx] # Retrieve centroids for current element
        connected_ele_centroids = centroids[connected_elements] # Retrieve centroids for connected elements
        delta = connected_ele_centroids - current_ele_centroids # Compute delta, difference between connected elements centroids and current element centroids 
        delta_local = transform_to_local_axes(
            values=delta,
            rotation_matrices=rotation_matrices[ele_idx],
        ) # Transform delta to local axes
        dx = delta_local[:, 0] # Unpack dx from delta local
        dy = delta_local[:, 1] # Unpack dy from delta local
        dz = delta_local[:, 2] # Unpack dz from delta local

        if element_type[ele_idx] == ElementType.Beam: # Set condition if element type is "Beam"
            xy_plane = np.abs(dz) < tol # Define filter for local xy plane
            not_collinear = np.abs(dy) >= tol # Define filter for non collinear element
            mask = xy_plane & not_collinear # Define filter for beam elements
            filtered_elements_connectivity.append(connected_elements[mask]) # Append filtered result to filtered elements connectivity
            filtered_current_elements_end.append(element_end[mask]) # Append filtered result to filtered current element end
        elif element_type[ele_idx] == ElementType.Column: # Set condition if element type is "Column"
            # Local xy plane
            xy_plane = np.abs(dz) < tol # Define filter for local xy plane
            not_collinear_xy = np.abs(dy) >= tol # Define filter for non collinear element in local xy plane
            xy_mask = xy_plane & not_collinear_xy # Define filter for column elements in local xy plane
            filtered_elements_xy = connected_elements[xy_mask] # Retreive filtered result of connected elements in local xy plane
            filtered_end_xy = element_end[xy_mask] # Retrieve filtered result of current element end in local xy plane
            # Local xz plane
            xz_plane = np.abs(dy) < tol # Define filter for local xz plane
            not_collinear_xz = np.abs(dz) >= tol # Define filter for non collinear element in local xz plane
            xz_mask = xz_plane & not_collinear_xz # Define filter for column elements in local xz plane
            filtered_elements_xz = connected_elements[xz_mask] # Retreive filtered result of connected elements in local xz plane
            filtered_ends_xz = element_end[xz_mask] # Retrieve filtered result of current element end in local xz plane
            filtered_elements_connectivity.append(np.concatenate((filtered_elements_xy, filtered_elements_xz))) # Append filtered result to filtered elements connectivity
            filtered_current_elements_end.append(np.concatenate((filtered_end_xy, filtered_ends_xz))) # Append filtered result to filtered current elements end
    sec_dim = _get_section_dimensions(
        sections=sections,
        sec_idx=sec_idx,
        dims_name=["h", "b"],
    ) # Get section dimensions of all beamcolumn elements
    offsets_length = _compute_offsets_length(
        element_type=element_type,
        centroids=centroids,
        rotation_matrices=rotation_matrices,
        filtered_elements_connectivity=filtered_elements_connectivity,
        filtered_current_elements_end=filtered_current_elements_end,
        sec_dim=sec_dim,
    ) # Retrieve offsets length
    return offsets_length

def _generate_end_offsets(offsets_length, rotation_matrices):
    n = len(offsets_length)
    end_offsets = np.zeros((n, 6), dtype=np.float64) # Predefined end offsets array
    for ele_idx in range(n):
        iend_offset_length, jend_offset_length = offsets_length[ele_idx] # Unpack offsets length
        iend_offset_local_vector = np.array((iend_offset_length, 0.0, 0.0), dtype=np.float64) # Define I-end offset local vector
        iend_offset_global_vector = transform_to_global_axes(
            values=iend_offset_local_vector,
            rotation_matrices=rotation_matrices[ele_idx],
        ) # Transform I-End offset local vector to global axes
        jend_offset_local_vector = np.array((-jend_offset_length, 0.0, 0.0), dtype=np.float64) # Define J-end offset local vector
        jend_offset_global_vector = transform_to_global_axes(
            values=jend_offset_local_vector,
            rotation_matrices=rotation_matrices[ele_idx],
        ) # Transform J-End offset local vector to global axes
        offsets_vector = np.concatenate((iend_offset_global_vector, jend_offset_global_vector)) # Concatenate I-end and J-end offsets vector
        end_offsets[ele_idx] = offsets_vector # Store offsets vector into end offsets array
    return end_offsets

# GENERATE GEOMETRIC TRANSFORMATION
def _map_vectorz_to_name(element_type, vec_z):
    vectorz_to_name = {}
    for ele_type, vec in zip(element_type, vec_z):
        axis = np.argmax(np.abs(vec))
        sign = np.sign(vec[axis])
        if axis == 0:
            z_dir = "z_in_X"
        elif axis == 1:
            z_dir = "z_in_Y"
        elif axis == 2:
            z_dir = "z_in_Z"
        if ele_type == ElementType.Beam:
            prefix = "Beam"
        elif ele_type == ElementType.Column:
            prefix = "Column"
    vectorz_to_name[(ele_type, tuple(vec))] = (f"{prefix}-{z_dir}")
    return vectorz_to_name

def _generate_geometric_transformation(element_type, vec_z, end_offsets):
    beam_column_mask = np.isin(element_type, [ElementType.Beam, ElementType.Column])
    bc_element_type = element_type[beam_column_mask]
    bc_vec_z = vec_z[beam_column_mask]
    bc_end_offsets = end_offsets[beam_column_mask]
    bc_transf_data = np.column_stack([bc_vec_z, bc_end_offsets])
    bc_transf_unique, bc_geom_transf_idx = np.unique(bc_transf_data, axis=0, return_inverse=True)
    bc_transf_vec = bc_transf_unique[:, 0:3]
    bc_transf_offsets = bc_transf_unique[:, 3:9]
    print(bc_transf_vec)
    print(bc_transf_offsets)
    bc_transf_name = _map_vectorz_to_name(element_type=bc_element_type, vec_z=bc_vec_z)
    
    geom_transf_idx = np.full(len(element_type), -1, dtype=np.int32)
    geom_transf_idx[beam_column_mask] = bc_geom_transf_idx
    print(geom_transf_idx)
    print(bc_transf_name)
    return geom_transf_idx, bc_transf_vec, bc_transf_offsets, bc_transf_name