import openseespy.opensees as ops
import numpy as np
import pandas as pd
import math
from utility.Operator import SignificantNumber, PolygonArea
from DISSERTATION.sarpy.utility.constants import g

class Masses:
    def __init__(self, workspace):
        self.ws = workspace
    
    def compute(self, SlabNodes_Storey_dict, Node_dict, Nodes_to_Slab_dict, EdgeNodes_Storey_dict):
        # COMPUTE MASS
        ## SLAB MASS
        SlabSection_dict = self.ws.slabsections # Recalling dictionary for each slab section name
        Slab_dict = self.ws.slabs # Recalling dictionary for each slab tag
        StoreyHeight = self.ws.storeyheight # Recalling dictionary for Storey height
        FloorArea = {} # Predefined Floor area dictionary
        FloorPerimeter = {} # Predefined Floor perimeter dictionary
        Floor_to_Node_TributaryArea = {} # Predefined Tributary area of floor to each node dictionary
        EdgeElement_to_Node_TributaryLength = {} # Predefined Tributary length of edge element to each node dictionary
        FloorNodesMass = {} # Predefined Floor nodes mass dictionary
        for height, SlabNodes_oneStorey in SlabNodes_Storey_dict.items():
            if len(SlabNodes_oneStorey) == 0: # Checking if there is no slab at each Storey height, then return 0 value
                FloorArea[height] = 0.0
                FloorPerimeter[height] = 0.0
                continue

            TotalArea = 0.0
            for SlabNodes in SlabNodes_oneStorey:
                XYcoords = np.array([[Node_dict[node]['X'], Node_dict[node]['Y']] for node in SlabNodes]) # Recalling X and Y Coordinates of each slab node from nodes dictionary
                SlabArea = PolygonArea(XYcoords) # Calculating each slab area
                TotalArea += SlabArea # Calculating total slab area
                nNodes = len(SlabNodes) # Number of nodes in each slab
                Node_TributaryArea = SlabArea / nNodes # Tributary area of floor to each node
                SlabTag = Nodes_to_Slab_dict[tuple(SlabNodes)] # Recalling slab tag for each nodes
                t_slab = SlabSection_dict[Slab_dict[SlabTag]['Slab Section']]['t'] # Recalling slab thickness for each slab
                unitweight_slab = self.ws.materials[SlabSection_dict[Slab_dict[SlabTag]['Slab Section']]['Base Material']]['Unitweight'] # Recalling unitweight of slab
                for node in SlabNodes:
                    Floor_to_Node_TributaryArea[node] = Node_TributaryArea # Storing Tributary area for each node
                    NodeMass = Floor_to_Node_TributaryArea[node] * t_slab * unitweight_slab/g # Calculating a node tributary mass
                    FloorNodesMass[node] = FloorNodesMass.get(node, 0) + NodeMass # Storing nodes mass for each node
            FloorArea[height] = TotalArea # Storing Floor area for each Storey height

            TotalPerimeter = 0.0
            EdgeNodes_oneStorey = EdgeNodes_Storey_dict[height]
            for EdgeNodes in EdgeNodes_oneStorey:
                inode, jnode = EdgeNodes # Defining i-end and j-end nodes from each edge element nodes
                i_xCoord, i_yCoord = Node_dict[inode]['X'], Node_dict[inode]['Y'] # Recalling X and Y Coordinates of each edge element i-end node from nodes dictionary
                j_xCoord, j_yCoord = Node_dict[jnode]['X'], Node_dict[jnode]['Y'] # Recalling X and Y Coordinates of each edge element j-end node from nodes dictionary
                ElementLength = np.sqrt((i_xCoord - j_xCoord)**2 + (i_yCoord - j_yCoord)**2) # Calculating element length
                TotalPerimeter += ElementLength # Calculating total floor perimeter
                nNodes = len(EdgeNodes) # Number of nodes in each edge element
                Node_TributaryLength = ElementLength / nNodes # Tributary length of edge element to each node
                for node in EdgeNodes:
                    EdgeElement_to_Node_TributaryLength[node] = Node_TributaryLength # Storing Tributary length for each node
            FloorPerimeter[height] = TotalPerimeter # Storing Floor perimeter for each Storey height

        ## BEAM AND COLUMN MASS
        ElementCol_dict = self.ws.elementscol # Defining dictionary for each slab tag
        ElementColNodesMass = {} # Predefined Element - Column nodes mass dictionary
        for height in StoreyHeight:
            for ElementTag, (inode, jnode, ElementType, SectionName, SectionNameNL) in ElementCol_dict.items():
                A = self.ws.framesections[f"{SectionName}"]['A'] # Recalling Section area from dictionary
                unitweight = self.ws.materials[self.ws.framesections[f"{SectionName}"]['Material 1']]['Unitweight'] # Recalling unitweight of section
                i_xCoord, i_yCoord, i_zCoord = Node_dict[inode]['X'], Node_dict[inode]['Y'], Node_dict[inode]['Z'] # Recalling Node data from dictionary
                j_xCoord, j_yCoord, j_zCoord = Node_dict[jnode]['X'], Node_dict[jnode]['Y'], Node_dict[jnode]['Z'] # Recalling Node data from dictionary
                ElementLength = np.sqrt((i_xCoord - j_xCoord)**2 + (i_yCoord - j_yCoord)**2 + (i_zCoord - j_zCoord)**2) # Calculating element length
                if math.isclose(i_zCoord, height):
                    NodeMass = unitweight/g * A * ElementLength / 2 # Calculating i-end node mass
                    ElementColNodesMass[inode] = ElementColNodesMass.get(inode, 0) + NodeMass # Storing nodes mass for each node
                if math.isclose(j_zCoord, height):
                    NodeMass = unitweight/g * A * ElementLength / 2 # Calculating j-end node mass
                    ElementColNodesMass[jnode] = ElementColNodesMass.get(jnode, 0) + NodeMass # Storing nodes mass for each node

        ElementBeamX_dict = self.ws.elementsbeamx # Defining dictionary for each slab tag
        ElementBeamXNodesMass = {} # Predefined Element - BeamX nodes mass dictionary
        for height in StoreyHeight:
            for ElementTag, (inode, jnode, ElementType, SectionName, SectionNameNL) in ElementBeamX_dict.items():
                A = self.ws.framesections[f"{SectionName}"]['A'] # Recalling Section area from dictionary
                unitweight = self.ws.materials[self.ws.framesections[f"{SectionName}"]['Material 1']]['Unitweight'] # Recalling unitweight of section
                i_xCoord, i_yCoord, i_zCoord = Node_dict[inode]['X'], Node_dict[inode]['Y'], Node_dict[inode]['Z'] # Recalling Node data from dictionary
                j_xCoord, j_yCoord, j_zCoord = Node_dict[jnode]['X'], Node_dict[jnode]['Y'], Node_dict[jnode]['Z'] # Recalling Node data from dictionary
                ElementLength = np.sqrt((i_xCoord - j_xCoord)**2 + (i_yCoord - j_yCoord)**2 + (i_zCoord - j_zCoord)**2) # Calculating element length
                if math.isclose(i_zCoord, height):
                    NodeMass = unitweight/g * A * ElementLength / 2 # Calculating i-end node mass
                    ElementBeamXNodesMass[inode] = ElementBeamXNodesMass.get(inode, 0) + NodeMass # Storing nodes mass for each node
                if math.isclose(j_zCoord, height):
                    NodeMass = unitweight/g * A * ElementLength / 2 # Calculating j-end node mass
                    ElementBeamXNodesMass[jnode] = ElementBeamXNodesMass.get(jnode, 0) + NodeMass # Storing nodes mass for each node

        ElementBeamY_dict = self.ws.elementsbeamy # Defining dictionary for each slab tag
        ElementBeamYNodesMass = {} # Predefined Element - BeamY nodes mass dictionary
        for height in StoreyHeight:
            for ElementTag, (inode, jnode, ElementType, SectionName, SectionNameNL) in ElementBeamY_dict.items():
                A = self.ws.framesections[f"{SectionName}"]['A'] # Recalling Section area from dictionary
                unitweight = self.ws.materials[self.ws.framesections[f"{SectionName}"]['Material 1']]['Unitweight'] # Recalling unitweight of section
                i_xCoord, i_yCoord, i_zCoord = Node_dict[inode]['X'], Node_dict[inode]['Y'], Node_dict[inode]['Z'] # Recalling Node data from dictionary
                j_xCoord, j_yCoord, j_zCoord = Node_dict[jnode]['X'], Node_dict[jnode]['Y'], Node_dict[jnode]['Z'] # Recalling Node data from dictionary
                ElementLength = np.sqrt((i_xCoord - j_xCoord)**2 + (i_yCoord - j_yCoord)**2 + (i_zCoord - j_zCoord)**2) # Calculating Element's length
                if math.isclose(i_zCoord, height):
                    NodeMass = unitweight/g * A * ElementLength / 2 # Calculating i-end node mass
                    ElementBeamYNodesMass[inode] = ElementBeamYNodesMass.get(inode, 0) + NodeMass # Storing nodes mass for each node
                if math.isclose(j_zCoord, height):
                    NodeMass = unitweight/g * A * ElementLength / 2 # Calculating j-end node mass
                    ElementBeamYNodesMass[jnode] = ElementBeamYNodesMass.get(jnode, 0) + NodeMass # Storing nodes mass for each node

        ## MASS DUE TO LOADING
        Load_dict = self.ws.loads
        wDead_roof = Load_dict['Dead Roof']['Value']
        wLive_roof = Load_dict['Live Roof']['Value']
        wDead_floor = Load_dict['Dead Floor']['Value']
        wLive_floor = Load_dict['Live Floor']['Value']
        wParapet = Load_dict['Parapet']['Value']
        wCladding = Load_dict['Cladding']['Value']

        ### Roof and Typical Floor
        LL_mass_factor = self.ws.options['LL Mass factor']
        FloorNodesDLMass = {} # Predefined nodes Dead Load mass on Typical Floor dictionary
        FloorNodesLLMass = {} # Predefined nodes Live Load mass on Typical Floor dictionary
        RoofNodesDLMass = {} # Predefined nodes Dead Load mass on Roof floor dictionary
        RoofNodesLrMass = {} # Predefined nodes Live Load mass on Roof floor dictionary
        FloorNodesCladdingMass = {} # Predefined nodes Cladding mass dictionary
        RoofNodesParapetMass = {} # Predefined nodes Parapet mass dictionary
        RoofHeight = max(StoreyHeight) # Defining roof height
        for height in StoreyHeight:
            SlabNodes_oneStorey = SlabNodes_Storey_dict[height]
            for SlabNodes in SlabNodes_oneStorey:
                for node in SlabNodes:
                    if height == RoofHeight:
                        # Dead Load
                        NodeDLMass = Floor_to_Node_TributaryArea[node] * wDead_roof/g # Calculating a node tributary dead load mass
                        RoofNodesDLMass[node] = RoofNodesDLMass.get(node, 0) + NodeDLMass # Storing nodes dead load mass for each node

                        # Roof Live Load
                        NodeLrMass = LL_mass_factor * Floor_to_Node_TributaryArea[node] * wLive_roof/g # Calculating a node tributary live load mass
                        RoofNodesLrMass[node] = RoofNodesLrMass.get(node, 0) + NodeLrMass # Storing nodes live load mass for each node
                    else:
                        # Dead Load
                        NodeDLMass = Floor_to_Node_TributaryArea[node] * wDead_floor/g # Calculating a node tributary dead load mass
                        FloorNodesDLMass[node] = FloorNodesDLMass.get(node, 0) + NodeDLMass # Storing nodes dead load mass for each node

                        # Live Load
                        NodeLLMass = LL_mass_factor * Floor_to_Node_TributaryArea[node] * wLive_floor/g # Calculating a node tributary live load mass
                        FloorNodesLLMass[node] = FloorNodesLLMass.get(node, 0) + NodeLLMass # Storing nodes live load mass for each node

            EdgeNodes_oneStorey = EdgeNodes_Storey_dict[height] # Recalling edge element nodes for each Storey height
            for EdgeNodes in EdgeNodes_oneStorey:
                for node in EdgeNodes:
                    if height == RoofHeight:
                        # Parapet Mass
                        NodeParapetMass = EdgeElement_to_Node_TributaryLength[node] * wParapet/g # Calculating a node tributary parapet mass
                        RoofNodesParapetMass[node] = RoofNodesParapetMass.get(node, 0) + NodeParapetMass # Storing nodes parapet mass for each node
                    else:
                        # Cladding Mass
                        NodeCladdingMass = EdgeElement_to_Node_TributaryLength[node] * wCladding/g # Calculating a node tributary cladding mass
                        FloorNodesCladdingMass[node] = FloorNodesCladdingMass.get(node, 0) + NodeCladdingMass # Storing nodes cladding mass for each node
        Mass = {
            'Element Col Nodes Mass': ElementColNodesMass,
            'Element Beam X Nodes Mass': ElementBeamXNodesMass,
            'Element Beam Y Nodes Mass': ElementBeamYNodesMass,
            'Floor Nodes Mass': FloorNodesMass,
            'Floor Nodes DL Mass': FloorNodesDLMass,
            'Floor Nodes LL Mass': FloorNodesLLMass,
            'Roof Nodes DL Mass': RoofNodesDLMass,
            'Roof Nodes Lr Mass': RoofNodesLrMass,
            'Floor Nodes Cladding Mass': FloorNodesCladdingMass,
            'Roof Nodes Parapet Mass': RoofNodesParapetMass
        }
        return Mass
    
    def assign(self, StructureNodesMass, Node_dict, DiaphCMNode_dict):
        # ASSIGN MASS
        NodalMass = [] # Predefined nodal mass list
        for NodeTag, Mass in StructureNodesMass.items():
            xCoord, yCoord, zCoord = Node_dict[NodeTag] # Recalling Node data from dictionary
            for DiaphNodeTag, (Diaph_xCoord, Diaph_yCoord, Diaph_zCoord) in DiaphCMNode_dict.items():
                if Diaph_zCoord == zCoord:
                    Diaph_xCoord = Diaph_xCoord
                    Diaph_yCoord = Diaph_yCoord
                # nodeTag, *massValues (massX, massY, massZ, massRX, massRY, massRZ)
            ops.mass(NodeTag, *(Mass, Mass, 1e-13, 1e-13, 1e-13, 1e-13)) # Assigning mass to each node
            ret = ops.nodeMass(NodeTag) # Returning value of each node's mass
            NodalMass.append({
                'Node': NodeTag,
                'Height (m)': zCoord,
                'MassX (kg)': SignificantNumber(ret[0]),
                'MassY (kg)': SignificantNumber(ret[1]),
                'MassZ (kg)': SignificantNumber(ret[2]),
                'MassRX (kg-m2)': SignificantNumber(ret[3]),
                'MassRY (kg-m2)': SignificantNumber(ret[4]),
                'MassRZ (kg-m2)': SignificantNumber(Mass * ((xCoord - Diaph_xCoord)**2 + (yCoord - Diaph_yCoord)**2))
            }) # Appending masses data to nodal mass list
        NodalMass_df = pd.DataFrame(NodalMass) # Creating Dataframe for nodal mass data
        return NodalMass_df