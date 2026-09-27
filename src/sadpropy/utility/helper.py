import numpy as np
from .exception import ValidationError

__all__ = ["retrieve_output_from_input", "transform_to_global_axes", "transform_to_local_axes", "get_parent_node"]

# RETRIEVE OUTPUT DATA FROM INPUT DATA WHICH SHARED COMMON TABLE
def retrieve_output_from_input(inputdata, shared_data_in, outputdata, shared_data_out):
    shared = shared_data_in[inputdata]
    lookup = dict(zip(shared_data_out, outputdata))
    try:
        outputdata_converted = np.vectorize(lookup.__getitem__)(shared)
    except KeyError as e:
        raise ValidationError(f"Shared value {e.args[0]!r} not found in output shared data")
    return outputdata_converted.astype(np.int32)

# TRASNFORM TO GLOBAL AXES
def transform_to_global_axes(values, rotation_matrices):
    values = np.asarray(values) # Make values into an array
    if values.ndim == 1: # Set condition if values is 1D-array return projection to local axes
        if rotation_matrices.ndim != 2: # Set condition if rotation matrices is not 2D-array raise ValidationError
            raise ValidationError("Single vector requires a single rotation matrix")
        return values @ rotation_matrices.T
    elif values.ndim == 2: # Set condition if values is 2D-array
        if rotation_matrices.ndim == 2: # Set condition if rotation matrices is 2D-array (Same rotation matrix for every value) return projection to local axes
            return values @ rotation_matrices.T
        elif rotation_matrices.ndim == 3: # Set condition if rotation matrices is 3D-array (Different rotation matrix per every value) return projection to local axes
            return np.einsum("ni,nji->nj", values, rotation_matrices)
    elif values.ndim == 3: # Set condition if values is 3D-array return projection to local axes
        if rotation_matrices.ndim != 3: # Set condition if rotation matrices is not 3D-array raise ValidationError
            raise ValidationError("Batched vectors require batched rotation matrices")
        return np.einsum("nki,nji->nkj", values, rotation_matrices)
    raise ValidationError("Values must have shape 1D, 2D or 3D array")

# TRANSFORM TO LOCAL AXES
def transform_to_local_axes(values, rotation_matrices):
    values = np.asarray(values) # Make values into an array
    if values.ndim == 1: # Set condition if values is 1D-array return projection to local axes
        if rotation_matrices.ndim != 2: # Set condition if rotation matrices is not 2D-array raise ValidationError
            raise ValidationError("Single vector requires a single rotation matrix")
        return values @ rotation_matrices
    elif values.ndim == 2: # Set condition if values is 2D-array
        if rotation_matrices.ndim == 2: # Set condition if rotation matrices is 2D-array (Same rotation matrix for every value) return projection to local axes
            return values @ rotation_matrices
        elif rotation_matrices.ndim == 3: # Set condition if rotation matrices is 3D-array (Different rotation matrix per every value) return projection to local axes
            return np.einsum("ni,nij->nj", values, rotation_matrices)
    elif values.ndim == 3: # Set condition if values is 3D-array return projection to local axes
        if rotation_matrices.ndim != 3: # Set condition if rotation matrices is not 3D-array raise ValidationError
            raise ValidationError("Batched vectors require batched rotation matrices")
        return np.einsum("nki,nij->nkj", values, rotation_matrices)
    raise ValidationError("Values must have shape 1D, 2D or 3D array")

# GET PARENT NODE
def get_parent_node(nodes, child_node):
    nodes_generated_from = nodes.generated_from # Retrieve parent name of generated node
    # Scalar case
    if np.isscalar(child_node): # Set condition if child node is scalar
        if nodes_generated_from[child_node] != "": # Set condition if parent name of generated node is not empty string
            return nodes.name_to_idx(names=nodes_generated_from[child_node]) # If True, return parent node index
        parent_node = child_node # Otherwise, generated node is parent node then return generated node index
        return parent_node

    # Array case
    child_node = np.asarray(child_node, dtype=np.int32) # Make child node as an array
    parent_node = child_node.copy() # Set default value of parent node that is same as child node
    mask = nodes_generated_from[child_node] != "" # Filter parent name of generated node is not empty string
    if np.any(mask): # Set condition if any parent name of generated node is not empty string
        parent_node[mask] = [
            nodes.name_to_idx(names=name)
            for name in nodes_generated_from[child_node][mask]
        ] # If True, get parent node index from name to index dictionary
    return parent_node