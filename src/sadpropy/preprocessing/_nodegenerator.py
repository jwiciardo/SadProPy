import numpy as np
from dataclasses import dataclass
from ._preproc_class import (
    NodeSource,
    ConnectionEnd,
)
from ._preproc_dataclass import Nodes

class NodeBuilder:
    def __init__(self, nodes: Nodes):
        self._original_nodes = nodes

        # GENERATED NODES
        self._generated_unique_name = []
        self._generated_coords = []
        self._generated_source = []
        self._generated_node_map = {}

    @property
    def n_original_nodes(self):
        return len(self._original_nodes.index)

    @property
    def n_generated_nodes(self):
        return len(self._generated_unique_name)

    @property
    def n_total_nodes(self):
        return (self.n_original_nodes + self.n_generated_nodes)

    def get_coord(self, node_idx,):
        if node_idx < self.n_original_nodes:
            return self._original_nodes.coords[node_idx]
        return self._generated_coords[
            node_idx - self.n_original_nodes
        ]

    def duplicate_node(self, line_idx, end, original_node, source,):
        key = (
            int(line_idx),
            int(end),
            int(source),
        )

        #
        # Already created
        #
        if key in self._generated_node_map:
            return self._generated_node_map[key]

        #
        # New index
        #
        new_node = self.n_total_nodes

        #
        # Name
        #
        suffix = "I" if end == 0 else "J"

        name = (
            f"{self._original_nodes.unique_name[original_node]}"
            f"_{source.name}_{suffix}"
        )

        self._generated_unique_name.append(name)
        self._generated_coords.append(
            self._original_nodes.coords[
                original_node
            ].copy()
        )
        self._generated_source.append(source)
        self._generated_node_map[key] = new_node
        return new_node

    def build(self):
        unique_name = np.concatenate(
            (
                self._original_nodes.unique_name,
                np.asarray(
                    self._generated_unique_name,
                    dtype="U64",
                ),
            )
        )

        coords = np.vstack(
            (
                self._original_nodes.coords,
                np.asarray(
                    self._generated_coords,
                    dtype=np.float64,
                ),
            )
        )

        generated_source = np.concatenate(
            (
                self._original_nodes.generated_source,
                np.asarray(
                    self._generated_source,
                    dtype=np.int32,
                ),
            )
        )

        return Nodes(
            index=np.arange(
                len(unique_name),
                dtype=np.int32,
            ),
            unique_name=unique_name,
            coords=coords,
            generated_source=generated_source,
        )

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















    def _autogenerate_nodes(original_nodes, line_objects):
        lines_index = line_objects["Index"]
        end_points_idx = line_objects["End Points Index"]

        new_node_idx = len(original_nodes["Unique Name"])
        line_to_node = {}
        for line_idx in lines_index:
            if not line_objects["Is Zero Length Element"][line_idx]: # Set condition if "Is Zero Length Element" is True then autogenerate new node
                continue

        


        point_objects = self._translator_result["Point Objects"] # Recalling point objects data
        line_objects = self._translator_result["Line Objects"] # Recalling line objects data
        unique_name = point_objects["Unique Name"].tolist() # Converting unique name data into list
        coords = [c.copy() for c in point_objects["Coordinates"]].tolist() # Converting coordinates data into list
        line_to_nodes = {} # Predefined line to nodes dictionary
        next_index = len(unique_name) # Determining current index
        sub_index = 1 # Defining suffix name for new generated node
        for line_idx in line_objects["Index"]: # Loop over line objects index
            if not line_objects["Is Zero Length Element"][line_idx]: # Set condition if "Is Zero Length Element" is True then autogenerate new node
                continue
            line_to_nodes[line_idx] = [0, 0] # Predefined shape of values in line to nodes dictionary
            i_node = line_objects["End Points Index"][line_idx][ConnectionEnd.I_End] # Recalling I-end node index
            unique_name.append(f"{unique_name[i_node]}-{sub_index}") # Appending unique name of new generated I-end node
            coords.append(point_objects["Coordinates"][i_node].copy()) # Appending coordinates of new generated I-end node
            line_to_nodes[line_idx][ConnectionEnd.I_End] = next_index # Storing new generated I-end node index into line to nodes dictionary
            next_index += 1 # Redefining next index
            sub_index += 1 # Redefining next suffix name for new generated node
            j_node = line_objects["End Points Index"][line_idx][ConnectionEnd.J_End] # Recalling J-end node index
            unique_name.append(f"{unique_name[j_node]}-{sub_index}") # Appending unique name of new generated J-end node
            coords.append(point_objects["Coordinates"][j_node].copy()) # Appending coordinates of new generated J-end node
            line_to_nodes[line_idx][ConnectionEnd.J_End] = next_index # Storing new generated J-end node index into line to nodes dictionary
            next_index += 1 # Redefining next index
            sub_index += 1 # Redefining next suffix name for new generated node