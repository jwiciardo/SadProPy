import numpy as np
from .preprocessing_object._node import _autogenerate_nodes
from .preprocessing_object._element import (
    _generate_element_local_axes,
    _generate_element_connectivity,
    _autogenerate_offsets_length,
    _generate_end_offsets,
    _generate_geometric_transformation,
)
from .preprocessing_object._load import _generate_group_nodal_loads, _generate_group_concentrated_element_loads, _generate_group_distributed_element_loads
from .preprocessing_object._zero_length_element import _generate_zerolength_element_local_axes
from .preprocessing_class_index import ElementType, NodeSource
from .preprocessing_dataclass import (
    ModelData,
    Nodes,
    Elements,
    ZeroLengthElements,
    Shells,
    Restraints,
    NodalLoads,
    ConcentratedElementalLoads,
    DistributedElementalLoads,
    ShellToElementalLoads,
)
from sadpropy.utility import TagManager
from sadpropy.utility.helper import get_parent_node

__all__ = ["ModelDataStorer"]

class ModelDataStorer:
    def __init__(self, translator_data):
        # TAG MANAGER
        self._tagmanager = TagManager()

        # STORE INPUTFILE MODEL DATA
        self._translator_data = translator_data
    
    def retrieve(self):
        nodes = self._generate_nodes()
        elements = self._generate_elements(nodes=nodes)
        zerolength_elements = self._generate_zero_length_elements(nodes=nodes, elements=elements)
        shells = self._generate_shells(nodes=nodes)
        restraints = self._generate_restraints(nodes=nodes)
        nodal_loads = self._generate_nodal_loads()
        concentrated_elemental_loads = self._generate_concentrated_elemental_loads(elements=elements)
        distributed_elemental_loads = self._generate_distributed_elemental_loads(elements=elements)
        shell_to_elemental_loads = self._generate_shell_to_elemental_loads(elements=elements)
        print()
        return ModelData(
            filepath_information = self._translator_data["Filepath Information"],
            project_information = self._translator_data["Project Information"],
            userdefined_units = self._translator_data["Userdefined Units"],
            analysis_preferences = self._translator_data["Analysis Preferences"],
            materials = self._translator_data["Materials"],
            frame_sections = self._translator_data["Frame Sections"],
            slab_sections = self._translator_data["Slab Sections"],
            storeys = self._translator_data["Storeys"],
            nodes = nodes,
            elements = elements,
            zerolength_elements = zerolength_elements,
            shells = shells,
            restraints = restraints,
            nodal_loads = nodal_loads,
            concentrated_elemental_loads = concentrated_elemental_loads,
            distributed_elemental_loads = distributed_elemental_loads,
            shell_to_elemental_loads = shell_to_elemental_loads,
        )
    
    # SUPPORTING METHODS
    def _generate_nodes(self):
        node_objects = self._translator_data["Node Objects"] # Retrieve node objects data
        element_objects = self._translator_data["Element Objects"] # Retrieve element objects data

        # Userdefined generated nodes
        n = len(node_objects["Index"])
        usr_unique_name = node_objects["Unique Name"]
        usr_coords = node_objects["Coordinates"]
        usr_generated_source = np.full(n, NodeSource.User, dtype=np.int32)
        usr_generated_from = np.empty(n, dtype="U15")
        usr_element_to_end_nodes = {
            element_idx: [iend_node, jend_node]
            for element_idx, (iend_node, jend_node) in zip(element_objects["Index"], element_objects["End Nodes Index"])
        }
        usr_nodes = {
            "Unique Name": usr_unique_name,
            "Coordinates": usr_coords,
            "Generated Source": usr_generated_source,
            "Generated From": usr_generated_from,
            "Element to End Nodes": usr_element_to_end_nodes,
        }
        # Generated nodes
        gen_unique_name, gen_coords, gen_generated_source, gen_generated_from, gen_element_to_end_nodes = _autogenerate_nodes(
            usr_nodes=usr_nodes,
            element_objects=element_objects
        )
        unique_name = np.concatenate((usr_unique_name, np.asarray(gen_unique_name, dtype="U20")))
        if len(gen_coords) > 0:
            coords = np.vstack((usr_coords, np.asarray(gen_coords, dtype=np.float64)))
        else:
            coords = usr_coords
        generated_source = np.concatenate((usr_generated_source, np.asarray(gen_generated_source, dtype=np.int32)))
        generated_from = np.concatenate((usr_generated_from, np.asarray(gen_generated_from, dtype="U15")))
        self._element_to_end_nodes_map = usr_element_to_end_nodes | gen_element_to_end_nodes
        m = len(unique_name)
        index = np.arange(m, dtype=np.int32)
        node_tag = np.asarray(self._tagmanager.add(category="Node", n=m, names=unique_name), dtype=np.int32)
        nodes = Nodes(
            index = index,
            unique_name = unique_name,
            node_tag = node_tag,
            coords = coords,
            generated_source = generated_source,
            generated_from = generated_from,
        ) # Store nodes data to dataclass
        return nodes

    def _generate_elements(self, nodes):
        ndim = self._translator_data["Project Information"].ndim # Retrieve number of dimensional space
        element_objects = self._translator_data["Element Objects"] # Retrieve element objects data
        element_type = element_objects["Element Type"]
        mask = (element_type == ElementType.Column) | (element_type == ElementType.Beam) | (element_type == ElementType.Brace)
        n = len(element_objects["Index"][mask])
        index = np.arange(n, dtype=np.int32)
        unique_name = element_objects["Unique Name"][mask]
        element_tag = np.asarray(self._tagmanager.add(category="Element", n=n, names=unique_name), dtype=np.int32)
        end_nodes_idx = np.asarray([self._element_to_end_nodes_map[element_idx] for element_idx in element_objects["Index"][mask]], dtype=np.int32)
        element_type = element_objects["Element Type"][mask]
        sec_idx = element_objects["Section Index"][mask]
        length = element_objects["Length"][mask]
        centroids, vec_x, vec_y, vec_z, rotation_matrices = _generate_element_local_axes(nodes=nodes, end_nodes_index=end_nodes_idx, ndim=ndim)
        elements_connectivity, shared_connected_nodes, current_elements_end, neighbour_elements_end = _generate_element_connectivity(nodes=nodes, end_nodes_index=end_nodes_idx)
        is_auto_end_offsets = element_objects["Is Auto End Offsets"]
        rigid_zone_factor = element_objects["Rigid Zone Factor"]
        # Userdefined end offsets
        usr_offsets_length = element_objects["Offsets Length"]
        
        # Autogenerated end offsets
        autogen_offsets_length = _autogenerate_offsets_length(
            sections=self._translator_data["Frame Sections"],
            sec_idx=sec_idx,
            element_type=element_type,
            elements_connectivity=elements_connectivity,
            current_elements_end=current_elements_end,
            centroids=centroids,
            rotation_matrices=rotation_matrices,
        )
        offsets_length = np.where(is_auto_end_offsets[:, None], autogen_offsets_length, usr_offsets_length) # Set condition where auto end offsets return is True return autogen offsets length, otherwise usr offsets length
        end_offsets = _generate_end_offsets(
            offsets_length=offsets_length,
            rotation_matrices=rotation_matrices,
        )
        geom_transf_idx, transf_vec, transf_name = _generate_geometric_transformation(element_type=element_type, vec_z=vec_z, end_offsets=end_offsets)
        transf_tag = np.asarray(self._tagmanager.add(category="Geometric Transformation", n=len(transf_vec), names=transf_name), dtype=np.int32)
        elements = Elements(
            index = index,
            unique_name = unique_name,
            element_tag = element_tag,
            end_nodes_idx = end_nodes_idx,
            element_type = element_type,
            sec_idx = sec_idx,
            centroids = centroids,
            length = length,
            rotation_matrices = rotation_matrices,
            transf_tag = transf_tag,
            transf_vec = transf_vec,
            elements_connectivity = elements_connectivity,
            shared_connected_nodes = shared_connected_nodes,
            current_elements_end = current_elements_end,
            neighbour_elements_end = neighbour_elements_end,
            rigid_zone_factor = rigid_zone_factor,
            offsets_length = offsets_length,
            end_offsets = end_offsets,
        ) # Store beamcolumn elements data to dataclass
        return elements

    def _generate_zero_length_elements(self, nodes, elements):
        ndim = self._translator_data["Project Information"].ndim # Retrieve number of dimensional space
        nodes_generated_from = nodes.generated_from # Retrieve parent name of generated node
        if len(nodes.index[nodes_generated_from != ""]) == 0:
            zerolength_elements = ZeroLengthElements.empty()
            return zerolength_elements
        child_nodes = np.asarray([node_idx for node_idx in nodes.index[nodes_generated_from != ""]], dtype=np.int32) # Filter empty string values in nodes index
        parent_nodes = get_parent_node(nodes=nodes, child_node=child_nodes) # Get parent node
        n = len(child_nodes)
        index = np.arange(n, dtype=np.int32)
        unique_name = np.empty(n, dtype="U15")
        end_nodes_idx = np.empty((n, 2), dtype=np.int32)
        for i in range(n):
            name = f"ZL{i}"
            unique_name[i] = name
            end_nodes_idx[i] = [parent_nodes[i], child_nodes[i]]
        element_tag = np.asarray(self._tagmanager.add(category="Element", n=n, names=unique_name), dtype=np.int32)
        element_type = np.full(n, ElementType.ZeroLength, dtype=np.int8)
        rotation_matrices = _generate_zerolength_element_local_axes(ndim=ndim, elements=elements, child_nodes=child_nodes)
        zerolength_elements = ZeroLengthElements(
            index = index,
            unique_name = unique_name,
            element_tag = element_tag,
            end_nodes_idx = end_nodes_idx,
            element_type = element_type,
            rotation_matrices = rotation_matrices,
        ) # Store zerolength elements data to dataclass
        return zerolength_elements

    def _generate_shells(self, nodes):
        shell_objects = self._translator_data["Shell Objects"] # Retrieve shell objects data
        if len(shell_objects) == 0:
            shells = Shells.empty()
            return shells
        sec_idx = shell_objects["Section Index"]
        element_type = shell_objects["Element Type"]
        mask = element_type == ElementType.Slab
        n = len(shell_objects["Index"][mask])
        index = np.arange(n, dtype=np.int32)
        unique_name = shell_objects["Unique Name"][mask]
        elements_idx = np.asarray([element for element in shell_objects["Edges Index"][mask]], dtype=np.int32)
        vertices = get_parent_node(nodes=nodes, child_node=shell_objects["Vertices Index"][mask])
        nodes_idx = np.asarray([node for node in vertices], dtype=np.int32)
        shells = Shells(
            index = index,
            unique_name = unique_name,
            elements_idx = elements_idx,
            nodes_idx = nodes_idx,
            element_type = element_type,
            sec_idx = sec_idx,
        ) # Store shells data to dataclass
        return shells

    def _generate_restraints(self, nodes):
        restraints = self._translator_data["Restraints"] # Retrieve restraints data
        node_idx = restraints["Node Index"] # Retrieve node index
        node_idx = get_parent_node(nodes, node_idx) # Get node index
        node_name = nodes.unique_name[node_idx] # Retrieve node name
        node_tag = nodes.node_tag[node_idx] # Retrieve node tag
        dofs = restraints["DOFs"] # Retrieve dofs
        restraints = Restraints(
            node_idx = node_idx,
            node_name = node_name,
            node_tag = node_tag,
            dofs = dofs,
        ) # Store restraints data to dataclass
        return restraints

    def _generate_nodal_loads(self):
        nodalloads = self._translator_data["Nodal Loads"] # Retrieve nodal loads data
        if len(nodalloads) == 0:
            nodal_loads = NodalLoads.empty()
            return nodal_loads
        node_name = nodalloads["Node Name"]
        node_tag = self._tagmanager.get_tag(category="Node", names=node_name) # Retrieve node tag
        loadcase_type = nodalloads["Load Case"] # Retrieve load case
        loads = nodalloads["Loads"] # Retrieve nodal loads
        result_node_tag, result_loadcase_type, result_loads = _generate_group_nodal_loads(
            node_tag=node_tag,
            loadcase_type=loadcase_type,
            loads=loads,
        )
        nodal_loads = NodalLoads(
            node_tag = result_node_tag,
            loadcase = result_loadcase_type,
            loads = result_loads,
        ) # Store nodal loads data to dataclass
        return nodal_loads

    def _generate_concentrated_elemental_loads(self, elements):
        ndim = self._translator_data["Project Information"].ndim # Retrieve number of dimensional space
        elemental_loads = self._translator_data["Concentrated Elemental Loads"] # Retrieve concentrated elemental loads data
        if len(elemental_loads) == 0:
            concentrated_elemental_loads = ConcentratedElementalLoads.empty()
            return concentrated_elemental_loads
        element_name = elemental_loads["Element Name"]
        element_tag = self._tagmanager.get_tag(category="Element", names=element_name) # Retrieve element tag
        loadcase_type = elemental_loads["Load Case"] # Retrieve load case
        direction = elemental_loads["Direction"] # Retrieve load direction
        load = elemental_loads["Load"] # Retrieve concentrated element loads
        location = elemental_loads["Location"] # Retrieve concentrated element loads location
        result_element_tag, result_loadcase_type, result_location, transformed_loads = _generate_group_concentrated_element_loads(
            ndim=ndim,
            elements=elements,
            element_tag=element_tag,
            loadcase_type=loadcase_type,
            direction=direction,
            location=location,
            load=load,
        )
        concentrated_elemental_loads = ConcentratedElementalLoads(
            element_tag = result_element_tag,
            loadcase = result_loadcase_type,
            location = result_location,
            loads = transformed_loads,
        ) # Store concentrated elemental loads data to dataclass
        return concentrated_elemental_loads

    def _generate_distributed_elemental_loads(self, elements):
        ndim = self._translator_data["Project Information"].ndim # Retrieve number of dimensional space
        elemental_loads = self._translator_data["Distributed Elemental Loads"] # Retrieve distributed elemental loads data
        if len(elemental_loads) == 0:
            distributed_elemental_loads = DistributedElementalLoads.empty()
            return distributed_elemental_loads
        element_name = elemental_loads["Element Name"]
        element_tag = self._tagmanager.get_tag(category="Element", names=element_name) # Retrieve element tag
        loadcase_type = elemental_loads["Load Case"] # Retrieve load case
        direction = elemental_loads["Direction"] # Retrieve load direction
        load = elemental_loads["Load"] # Retrieve distributed element loads
        location = elemental_loads["Location"] # Retrieve distributed element loads location
        result_element_tag, result_loadcase_type, result_location, transformed_loads = _generate_group_distributed_element_loads(
            ndim=ndim,
            elements=elements,
            element_tag=element_tag,
            loadcase_type=loadcase_type,
            direction=direction,
            location=location,
            load=load,
        )
        distributed_elemental_loads = DistributedElementalLoads(
            element_tag = result_element_tag,
            loadcase = result_loadcase_type,
            location = result_location,
            loads = transformed_loads,
        ) # Store distributed elemental loads data to dataclass
        return distributed_elemental_loads

    def _generate_shell_to_elemental_loads(self, elements):
        ndim = self._translator_data["Project Information"].ndim # Retrieve number of dimensional space
        shell_loads = self._translator_data["Shell to Elemental Loads"] # Retrieve shell to elemental loads data
        if len(shell_loads) == 0:
            shell_to_elemental_loads = ShellToElementalLoads.empty()
            return shell_to_elemental_loads
        shell_name = shell_loads["Shell Name"]
        edge_name = shell_loads["Edge Name"]
        element_tag = self._tagmanager.get_tag(category="Element", names=edge_name) # Retrieve element tag
        loadcase_type = shell_loads["Load Case"] # Retrieve load case
        direction = shell_loads["Direction"] # Retrieve load direction
        load = shell_loads["Load"] # Retrieve shell to element loads
        location = shell_loads["Location"] # Retrieve shell to element loads location
        result_element_tag, result_loadcase_type, result_location, transformed_loads = _generate_group_distributed_element_loads(
            ndim=ndim,
            elements=elements,
            element_tag=element_tag,
            loadcase_type=loadcase_type,
            direction=direction,
            location=location,
            load=load,
        )
        shell_to_elemental_loads = ShellToElementalLoads(
            element_tag = result_element_tag,
            loadcase = result_loadcase_type,
            location = result_location,
            loads = transformed_loads,
        ) # Store shell to elemental loads data to dataclass
        return shell_to_elemental_loads

