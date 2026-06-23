import openseespy.opensees as ops
import pandas as pd
from utility.Operator import SignificantNumber

class Diaphragm:
    def __init__(self, workspace):
        self.ws = workspace
        self.tag = self.ws.tag_manager

    def determine_center_of_mass(self, SlabNodes_Storey_dict, Node_dict, Mass):
        # DETERMINE CENTER OF MASS
        StoreyHeight = self.ws.storeyheight # Recalling dictionary for Storey height
        ElementColNodesMass = Mass['Element Col Nodes Mass']
        ElementBeamXNodesMass = Mass['Element Beam X Nodes Mass']
        ElementBeamYNodesMass = Mass['Element Beam Y Nodes Mass']
        FloorNodesMass = Mass['Floor Nodes Mass']
        FloorNodesDLMass = Mass['Floor Nodes DL Mass']
        FloorNodesLLMass = Mass['Floor Nodes LL Mass']
        RoofNodesDLMass = Mass['Roof Nodes DL Mass']
        RoofNodesLrMass = Mass['Roof Nodes Lr Mass']
        FloorNodesCladdingMass = Mass['Floor Nodes Cladding Mass']
        RoofNodesParapetMass = Mass['Roof Nodes Parapet Mass']

        StructureMass = {} # Predefined total Mass of structure dictionary
        StructureNodesMass = {} # Predefined nodes Mass of structure dictionary
        DiaphCMX = {} # Predefined X coordinate of Diaphragm dictionary
        DiaphCMY= {} # Predefined Y coordinate of Diaphragm dictionary
        DiaphCMZ = {} # Predefined Z coordinate of Diaphragm dictionary
        DiaphCMNodes = {} # Predefined node tag for Diaphragm dictionary
        Nodes_Storey_dict = {} # Predefined node tag for each Storey dictionary
        for i, height in enumerate(StoreyHeight):
            if height != 0.0:
                SlabNodes_oneStorey = SlabNodes_Storey_dict[height] # Recalling Slab nodes from Slab nodes dictionary 
                Nodes = set(node for SlabNodes in SlabNodes_oneStorey for node in SlabNodes) # Selecting node tags for each Storey height
                DiaphNodeTag = int(i * 1000 + 999) # Creating node tag for diaphragm node

                if len(SlabNodes_oneStorey) == 0: # Checking if there is no slab at each Storey height, then return 0 value
                    StructureMass[height] = 0.0
                    DiaphCMX[height] = 0.0
                    DiaphCMY[height] = 0.0
                    DiaphCMZ[height] = 0.0
                    DiaphCMNodes[height] = int(0)
                    Nodes_Storey_dict[height] = int(0)
                    continue
                
                TotalMass = 0.0
                WeightedMass_X = 0.0
                WeightedMass_Y = 0.0
                WeightedMass_Z = 0.0
                for node in Nodes:
                    xCoord, yCoord, zCoord = Node_dict[node] # Recalling coordinates from node from dictionary
                    Mass = (
                        ElementColNodesMass.get(node, 0) + ElementBeamXNodesMass.get(node, 0) + ElementBeamYNodesMass.get(node, 0) +
                        FloorNodesMass.get(node, 0) + FloorNodesDLMass.get(node, 0) + FloorNodesLLMass.get(node, 0) +
                        RoofNodesDLMass.get(node, 0) + RoofNodesLrMass.get(node, 0) + FloorNodesCladdingMass.get(node, 0) + RoofNodesParapetMass.get(node, 0)
                    ) # Calculating node mass from considered mass
                    StructureNodesMass[node] = Mass # Storing nodes mass for each node
                    TotalMass += Mass # Calculating total mass of structure for each Storey height

                    WeightedMass_X += xCoord * Mass # Calculating weighted mass of X direction
                    WeightedMass_Y += yCoord * Mass # Calculating weighted mass of Y direction
                    WeightedMass_Z += zCoord * Mass # Calculating weighted mass of Z direction
                StructureMass[height] = TotalMass # Storing total mass of structure for each Storey height
                DiaphCMX[height] = round(WeightedMass_X / TotalMass, 1) # Determining and Storing X coordinate of diaphragm for each Storey height
                DiaphCMY[height] = round(WeightedMass_Y / TotalMass, 1) # Determining and Storing Y coordinate of diaphragm for each Storey height
                DiaphCMZ[height] = round(WeightedMass_Z / TotalMass, 1) # Determining and Storing Z coordinate of diaphragm for each Storey height
                DiaphCMNodes[height] = DiaphNodeTag # Storing diaphragm's node tags for each Storey height
                Nodes_Storey_dict[height] = Nodes # Storing Storey's node tags for each Storey height
        DiaphCMNode_dict = {int(DiaphCMNodes[height]): [float(DiaphCMX.get(height, 0)), float(DiaphCMY.get(height, 0)), float(DiaphCMZ.get(height, 0))] for height in DiaphCMNodes} # Defining dictionary for each diaphragm node tag

        StructureMass_df = pd.DataFrame([{'Height (m)': key, 'Storey Mass': SignificantNumber(value)} for key, value in StructureMass.items()]) # Creating Dataframe for Structure Mass data
        DiaphCM_df = pd.DataFrame([{'Diaphragm Node': key, 'X (m)': SignificantNumber(xCoord), 'Y (m)': SignificantNumber(yCoord), 'Z (m)': SignificantNumber(zCoord)} for key, (xCoord, yCoord, zCoord) in DiaphCMNode_dict.items()]) # Creating Dataframe for diaphragm data

        # ASSIGN RIGID DIAPHRAGM CONSTRAINT
        Zdirection = 3 # Defining direction perpendicular to the rigid plane which is at Global Z axis

        for DiaphNodeTag, (Diaph_xCoord, Diaph_yCoord, Diaph_zCoord) in DiaphCMNode_dict.items():
                        # nodeTag, *crds (X, Y, Z)
            ops.node(DiaphNodeTag, *(Diaph_xCoord, Diaph_yCoord, Diaph_zCoord)) # Creating Diaphragm Node objects
                    # nodeTag, *constrValues (UX, UY, UZ, RX, RY, RZ)
            ops.fix(DiaphNodeTag, *(0, 0, 1, 1, 1, 0)) # Defining constraints at Diaphragm Node objects
            self.tag.store('Node', DiaphNodeTag, f"{DiaphNodeTag}")

        for height in StoreyHeight[1:]:
            retainedNode = DiaphCMNodes[height]
            constrainedNode = Nodes_Storey_dict[height]
                            # perpDirn, rNodeTag,     *cNodeTags 
            ops.rigidDiaphragm(Zdirection, retainedNode, *constrainedNode) # Creating Constraint of Rigid diaphragm for each Storey
        
        return DiaphCMNode_dict, StructureMass, StructureNodesMass, StructureMass_df, DiaphCM_df
