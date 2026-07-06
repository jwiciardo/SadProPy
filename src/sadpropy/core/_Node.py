import openseespy.opensees as ops

class Nodes:
    def __init__(self, workspace):
        self.ws = workspace
        self.tag = self.ws.tag_manager
    
    def create(self):
        Node_dict = self.ws.nodes
        for NodeTag, data in Node_dict.items():
            X, Y, Z = data['X'], data['Y'], data['Z']
                   # nodeTag, *crds (X, Y, Z)
            ops.node(NodeTag, *(X, Y, Z)) # Creating Node objects
            self.tag.store('Node', NodeTag, f"{NodeTag}")
        return Node_dict