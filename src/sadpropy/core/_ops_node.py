import openseespy.opensees as ops

def _define_node(modeldata):
    nodes = modeldata.nodes # Retrieve nodes data
    node_tag = nodes.node_tag
    node_coords = nodes.coords
    for i in nodes.index:
        tag = int(node_tag[i])
        coords = list(map(float, node_coords[i]))
        ops.node(
            tag, # nodeTag
            *coords, # *crds = [X, Y, Z]
        )