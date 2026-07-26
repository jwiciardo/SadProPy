import numpy as np
from collections import defaultdict
from sadpropy.preprocessing._preproc_class import PropertiesClassRegistry, SectionShape, ConnectionEnd
from ..utility._exceptions import ValidationError

# GENERATE LOCAL AXES OF LINE OBJECTS
def generate_local_axes(end_points_index, point_objects, ndim):
    coords = point_objects.coords # Retrieve array of point coordinates
    if ndim == 3: # 3D Structure
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
    else: # 2D Structure
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

def _build_point_to_line_map(end_points_index):
    point_map = defaultdict(list) # Predefined dictionary of point map list
    for line_idx, (iend_point_idx, jend_point_idx) in enumerate(end_points_index): # Loop over end points index
        point_map[int(iend_point_idx)].append(line_idx) # Append line index into key: I-end point index
        point_map[int(jend_point_idx)].append(line_idx) # Append line index into key: J-end point index
    return point_map

def generate_line_connectivity(end_points_index):
    point_map = _build_point_to_line_map(end_points_index) # Build point to line map
    n = len(end_points_index) # Compute number of end points data
    connected_lines_list = [] # Predefined connected lines list of arrays
    end_points_list = [] # Predefined end points list of arrays
    max_connections = 0 # Predefined maximum number of connections
    for line_idx, (iend_point_idx, jend_point_idx) in enumerate(end_points_index): # Loop over end points index
        connected_lines = [] # Predefined connected lines list
        end_points = [] # Predefined end points list
        for line_idx_i in point_map[int(iend_point_idx)]: # Loop over line index list of I-end point map
            if line_idx_i == line_idx: # Set condition if line index I-end is same as current line index then skip the remaining code
                continue
            connected_lines.append(line_idx_i) # Append line index I-end into connected line
            end_points.append(ConnectionEnd.I_End) # Append I-end class into end points
        for line_idx_j in point_map[int(jend_point_idx)]: # Loop over line index list of J-end point map
            if line_idx_j == line_idx: # Set condition if line index J-end is same as current line index then skip the remaining code
                continue
            connected_lines.append(line_idx_j) # Append line index J-end into connected line
            end_points.append(ConnectionEnd.J_End) # Append J-end class into end points
        connected_lines_list.append(np.asarray(connected_lines, dtype=np.int32)) # Append connected lines as array into line connectiivty list
        end_points_list.append(np.asarray(end_points, dtype=np.int32)) # Append end points as array into end list
        max_connections = max(max_connections, len(connected_lines)) # Determine maximum number of connections
    line_connectivity = np.full((n, max_connections), -1, dtype=np.int32) # Preallocated line connectivity array
    connection_end = np.full((n, max_connections), -1, dtype=np.int32) # Preallocated connection end array
    for i in range(n): # Loop over end points index
        m = len(connected_lines_list[i]) # Compute number of connected lines
        if m == 0: # Set condition if there is no connection then skip the remaining code
            continue
        line_connectivity[i, :m] = connected_lines_list[i] # Store connected lines into line connectivity array
        connection_end[i, :m] = end_points_list[i] # Store end points into connection end array
    return line_connectivity, connection_end

def generate_auto_end_offsets(line_connectivity, connection_end, sec_class, sec_idx, secs_list, sec_data):
    n = len(line_connectivity)
    props_class = PropertiesClassRegistry()._get_sec_props_class(sec_class=sec_class)
    end_offsets = np.zeros((n, 2), dtype=np.float64)
    for i in range(n):
        for j in range(line_connectivity.shape[1]):
            connected_line = line_connectivity[i, j]
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