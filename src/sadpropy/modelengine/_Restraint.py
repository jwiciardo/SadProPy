import openseespy.opensees as ops

class Restraints:
    def __init__(self, workspace):
        self.ws = workspace
    
    def assign(self):
        ## Support at Base
        SupportNodes = []
        Restraints_dict = self.ws.restraints
        for NodeTag, (UX, UY, UZ, RX, RY, RZ) in Restraints_dict.items():
                  # nodeTag, *constrValues (UX, UY, UZ, RX, RY, RZ)
            ops.fix(NodeTag, *(UX, UY, UZ, RX, RY, RZ)) # Creating Constraint of fixed support for all nodes at Z=0
            SupportNodes.append(NodeTag)
        return SupportNodes