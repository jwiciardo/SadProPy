import numpy as np
from ._preproc_class import (
    NodeSource,
    ConnectionEnd,
)
from sadpropy.utility._exceptions import ValidationError

def has_duplicate(self, line_idx, end, source,):
    key = (
        int(line_idx),
        int(end),
        int(source),
    )
    return key in self._generated_node_map

def get_duplicate(self, line_idx, end, source,):
    key = (
        int(line_idx),
        int(end),
            int(source),
    )
    return self._generated_node_map[key]

def autogenerate_nodes(usr_nodes, line_objects):
    usr_unique_name = usr_nodes["Unique Name"] # Recalling node unique name
    usr_coords = usr_nodes["Coordinates"] # Recalling node coordinates
    lines_index = line_objects["Index"] # Recalling line objects index
    end_points_idx = line_objects["End Points Index"] # Recalling end points index

    new_node_idx = len(usr_unique_name) # Determining new node index
    suffix_idx = 1 # Defining suffix index for new node name
    gen_unique_name = [] # Predefined generated unique name list
    gen_coords = [] # PRedefined generated coordinates list
    gen_generated_source = []
    gen_generated_from = []
    gen_line_to_nodes = {}
    for line_idx in lines_index:
        if line_objects["Is Zero Length Element"][line_idx]: # Set condition if "Is Zero Length Element" is True then autogenerate new node
            if line_idx in gen_line_to_nodes:
                raise ValidationError(f"Duplicate generated nodes '{gen_line_to_nodes[line_idx]}'")
            gen_line_to_nodes[line_idx] = [0, 0]
            for end in (ConnectionEnd.I_End, ConnectionEnd.J_End):
                end_node = end_points_idx[line_idx][end]
                name = (f"N{usr_unique_name[end_node]}_{suffix_idx}")
                gen_unique_name.append(name)
                gen_coords.append(usr_coords[end_node].copy())
                gen_generated_source.append(NodeSource.ZLE)
                gen_generated_from.append(usr_unique_name[end_node])
                gen_line_to_nodes[line_idx][end] = np.int32(new_node_idx)
                new_node_idx += 1
                suffix_idx += 1
    return gen_unique_name, gen_coords, gen_generated_source, gen_generated_from, gen_line_to_nodes