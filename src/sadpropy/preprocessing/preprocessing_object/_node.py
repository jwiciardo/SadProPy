import numpy as np
from ..preprocessing_class_index import NodeSource, ConnectionEnd
from ...utility._exception import ValidationError

# AUTOGENERATE NODES
def autogenerate_nodes(usr_nodes, element_objects):
    usr_unique_name = usr_nodes["Unique Name"] # Recall node unique name
    usr_coords = usr_nodes["Coordinates"] # Recall node coordinates
    elements_index = element_objects["Index"] # Recall element objects index
    end_nodes_idx = element_objects["End Nodes Index"] # Recall end nodes index

    new_node_idx = len(usr_unique_name) # Determine new node index
    suffix_idx = 1 # Define suffix index for new node name
    gen_unique_name = [] # Predefined generated unique name list
    gen_coords = [] # Predefined generated coordinates list
    gen_generated_source = [] # Predefined generated generated source list
    gen_generated_from = [] # Predefined generated generated from list
    gen_element_to_end_nodes = {} # Predefined generated element to end nodes dictionary
    for element_idx in elements_index:
        if element_objects["Is Zero Length Element"][element_idx]: # Set condition if "Is Zero Length Element" is True then autogenerate new node
            if element_idx in gen_element_to_end_nodes:
                raise ValidationError(f"Duplicate generated nodes '{gen_element_to_end_nodes[element_idx]}'")
            gen_element_to_end_nodes[element_idx] = [0, 0]
            for end in (ConnectionEnd.I_End, ConnectionEnd.J_End):
                end_node = end_nodes_idx[element_idx][end]
                name = (f"N{usr_unique_name[end_node]}_{suffix_idx}")
                gen_unique_name.append(name)
                gen_coords.append(usr_coords[end_node].copy())
                gen_generated_source.append(NodeSource.ZeroLength)
                gen_generated_from.append(usr_unique_name[end_node])
                gen_element_to_end_nodes[element_idx][end] = np.int32(new_node_idx)
                new_node_idx += 1
                suffix_idx += 1
    return gen_unique_name, gen_coords, gen_generated_source, gen_generated_from, gen_element_to_end_nodes