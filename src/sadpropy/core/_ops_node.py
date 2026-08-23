import openseespy.opensees as ops

def _define_nodes(modeldata):
    nodes = modeldata.nodes # Retrieve nodes data
    node_tag = nodes.node_tag
    node_coords = nodes.coords
    for tag, coords in zip(node_tag, node_coords):
        coords = list(map(float, coords))
        ops.node(
            int(tag), # nodeTag
            *coords, # *crds = [X, Y, Z]
        )