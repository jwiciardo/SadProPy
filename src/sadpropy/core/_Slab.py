import numpy as np
from collections import defaultdict

class Slabs:
    def __init__(self, workspace):
        self.ws = workspace
    
    def create(self, Node_dict, Nodes_to_Element_dict):
        StoreyHeight = self.ws.storeyheight # Recalling dictionary for Storey height
        SlabSection_dict = self.ws.slabsections # Recalling dictionary for each slab section name

        Slab_dict = self.ws.slabs # Recalling dictionary for each slab tag
        Nodes_to_Slab_dict = {} # Predefined Nodes to slab dictionary
        for SlabTag, (inode, jnode, knode, lnode, SlabSection) in Slab_dict.items():
            Nodes = tuple((inode, jnode, knode, lnode))
            Nodes_to_Slab_dict[Nodes] = SlabTag # Storing slab tag for each nodes

        SlabNodes_list = [[inode, jnode, knode, lnode] for SlabTag, (inode, jnode, knode, lnode, SlabSection) in Slab_dict.items()] # Defining nodes list for each slab
        for SlabNodes in SlabNodes_list:
            SlabNodes[:] = [node for node in SlabNodes if not np.isnan(node)] # Removing empty values from Slab list
        
        SlabNodes_Storey_dict = {} # Predefined Slab nodes for each Storey height dictionary
        for height in StoreyHeight:
            SlabNodes_oneStorey = [] # Predefined Slab nodes for a Storey list
            for SlabNodes in SlabNodes_list:
                zCoord = [Node_dict[node]['Z'] for node in SlabNodes] # Recalling Z Coordinate of each slab node from node dictionary
                if np.all(zCoord == height):
                    SlabNodes_oneStorey.append(SlabNodes) # Appending Slab nodes to Slab nodes for a Storey list if Z Coordinate of slab nodes is same as Storey height
            SlabNodes_Storey_dict[height] = SlabNodes_oneStorey # Storing Slab nodes for each Storey height

        SlabElements_Storey_dict = {} # Predefined Slab elements for each Storey height dictionary
        SlabLoad_to_Element_Tributary_dict = [] # Predefined Slab load to element tributary length list
        for height, SlabNodes_oneStorey in SlabNodes_Storey_dict.items():
            SlabElements_oneStorey = set() # Predefined Slab elements for a Storey set
            for SlabNodes in SlabNodes_oneStorey:
                SlabTag = Nodes_to_Slab_dict[tuple(SlabNodes)] # Recalling slab tag for each nodes
                t_slab = SlabSection_dict[Slab_dict[SlabTag]['Slab Section']]['t'] # Recalling slab thickness for each slab
                unitweight_slab = self.ws.materials[SlabSection_dict[Slab_dict[SlabTag]['Slab Section']]['Base Material']]['Unitweight'] # Recalling unitweight of slab
                nNodes = len(SlabNodes) # Number of nodes in each slab
                SlabElementsLength_dict = {} # Predefined Slab elements length dictionary
                for i in range(nNodes):
                    inode = SlabNodes[i] # Selecting node at i-end
                    jnode = SlabNodes[(i + 1) % nNodes] # Selecting node at j-end
                    ElementNodes = tuple(sorted((inode, jnode))) # Selecting i-end and j-end nodes of an element
                    ElementTag = Nodes_to_Element_dict[ElementNodes] # Recalling element from dictionary
                    i_xCoord, i_yCoord = Node_dict[inode]['X'], Node_dict[inode]['Y'] # Recalling X and Y Coordinates of each element i-end node from node dictionary
                    j_xCoord, j_yCoord = Node_dict[jnode]['X'], Node_dict[jnode]['Y'] # Recalling X and Y Coordinates of each element j-end node from node dictionary
                    ElementLength = np.sqrt((i_xCoord - j_xCoord)**2 + (i_yCoord - j_yCoord)**2) # Calculating element length
                    SlabElementsLength_dict[ElementTag] = ElementLength # Storing element length for each element
                    SlabElements_oneStorey.add(ElementTag) # Adding Slab element to Slab elements set

                shortest_ElementLength = min(SlabElementsLength_dict.values()) # Finding the shortest element length in each slab
                for ElementTag, ElementLength in SlabElementsLength_dict.items():
                    if ElementLength == shortest_ElementLength:
                        eq_uniform_TributaryLength = shortest_ElementLength / 4
                    elif ElementLength > shortest_ElementLength:
                        eq_uniform_TributaryLength = ((2 * shortest_ElementLength * ElementLength) - shortest_ElementLength**2) / (4 * ElementLength)
                    SlabLoad_to_Element_Tributary_dict.append({
                        'Element': ElementTag,
                        'Slab': SlabTag,
                        'Thickness': float(t_slab),
                        'Unitweight': float(unitweight_slab),
                        'Tributary Length': eq_uniform_TributaryLength
                    }) # Appending Slab elements data to Slab load to element tributary length list
            SlabElements_Storey_dict[height] = list(SlabElements_oneStorey) # Storing Slab elements for each Storey height

        SlabLoad_to_Element_TributaryLength = defaultdict(float)
        for SlabData in SlabLoad_to_Element_Tributary_dict:
            Elements = SlabData['Element']
            SlabLoad_to_Element_TributaryLength[Elements] += SlabData['Tributary Length']

        # DEFINE GROUP OF EDGE ELEMENTS
        EdgeNodes_Storey_dict = {} # Predefined edge element nodes dictionary
        EdgeElements_Storey_dict = {} # Predefined edge elements dictionary
        for height, SlabNodes_oneStorey in SlabNodes_Storey_dict.items():
            EdgeNodes_count = defaultdict(int)
            for SlabNodes in SlabNodes_oneStorey:
                nNodes = len(SlabNodes) # Number of nodes in each slab
                for i in range(nNodes):
                    inode = SlabNodes[i] # Selecting node at i-end
                    jnode = SlabNodes[(i + 1) % nNodes] # Selecting node at j-end
                    ElementNodes = tuple(sorted((inode, jnode))) # Selecting i-end and j-end nodes of an element
                    EdgeNodes_count[ElementNodes] += 1 # Counting and identifying each element nodes (1: edge element nodes, >1: inner element nodes)
            EdgeNodes_oneStorey = [ElementNodes for ElementNodes, count in EdgeNodes_count.items() if count == 1] # Storing edge element nodes for a Storey
            EdgeNodes_Storey_dict[height] = EdgeNodes_oneStorey # Storing edge element nodes for each Storey height
            
            EdgeElements_oneStorey = [] # Predefined edge elements for a Storey list
            for EdgeNodes in EdgeNodes_oneStorey:
                ElementTag = Nodes_to_Element_dict[EdgeNodes] # Recalling element tag from dictionary
                EdgeElements_oneStorey.append(ElementTag) # Appending element tag to edge elements for a Storey list
            EdgeElements_Storey_dict[height] = EdgeElements_oneStorey # Storing edge elements for each Storey height
        return SlabNodes_Storey_dict, Nodes_to_Slab_dict, EdgeNodes_Storey_dict, SlabLoad_to_Element_Tributary_dict, SlabElements_Storey_dict, SlabLoad_to_Element_TributaryLength, EdgeElements_Storey_dict