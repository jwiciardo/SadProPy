import numpy as np
from ._node import autogenerate_nodes
from ._element import (
    generate_element_local_axes,
    generate_element_connectivity,
    autogenerate_offsets_length,
    generate_end_offsets,
    generate_geometric_transformation,
)
from ._load import (
    generate_group_nodal_loads,
    generate_group_concentrated_element_loads,
    generate_group_distributed_element_loads,
)
from ._zerolengthelements import generate_zerolength_element_local_axes
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
from sadpropy.utility.helperfunc import get_parent_node

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
        point_objects = self._translator_data["Point Objects"] # Retrieve point objects data
        line_objects = self._translator_data["Line Objects"] # Retrieve line objects data

        # Userdefined generated nodes
        n = len(point_objects["Index"])
        usr_unique_name = point_objects["Unique Name"]
        usr_coords = point_objects["Coordinates"]
        usr_generated_source = np.full(n, NodeSource.User, dtype=np.int32)
        usr_generated_from = np.empty(n, dtype="U15")
        usr_line_to_end_nodes = {
            line_idx: [iend_node, jend_node]
            for line_idx, (iend_node, jend_node) in zip(line_objects["Index"], line_objects["End Points Index"])
        }
        usr_nodes = {
            "Unique Name": usr_unique_name,
            "Coordinates": usr_coords,
            "Generated Source": usr_generated_source,
            "Generated From": usr_generated_from,
            "Line to End Nodes": usr_line_to_end_nodes,
        }
        # Generated nodes
        gen_unique_name, gen_coords, gen_generated_source, gen_generated_from, gen_line_to_end_nodes = autogenerate_nodes(
            usr_nodes=usr_nodes,
            line_objects=line_objects
        )
        unique_name = np.concatenate((usr_unique_name, np.asarray(gen_unique_name, dtype="U20")))
        if len(gen_coords) > 0:
            coords = np.vstack((usr_coords, np.asarray(gen_coords, dtype=np.float64)))
        else:
            coords = usr_coords
        generated_source = np.concatenate((usr_generated_source, np.asarray(gen_generated_source, dtype=np.int32)))
        generated_from = np.concatenate((usr_generated_from, np.asarray(gen_generated_from, dtype="U15")))
        self._line_to_end_nodes_map = usr_line_to_end_nodes | gen_line_to_end_nodes
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
        line_objects = self._translator_data["Line Objects"] # Retrieve line objects data
        element_type = line_objects["Element Type"]
        mask = (element_type == ElementType.Column) | (element_type == ElementType.Beam) | (element_type == ElementType.Brace)
        n = len(line_objects["Index"][mask])
        index = np.arange(n, dtype=np.int32)
        unique_name = line_objects["Unique Name"][mask]
        element_tag = np.asarray(self._tagmanager.add(category="Element", n=n, names=unique_name), dtype=np.int32)
        end_nodes_idx = np.asarray([self._line_to_end_nodes_map[line_idx] for line_idx in line_objects["Index"][mask]], dtype=np.int32)
        element_type = line_objects["Element Type"][mask]
        sec_idx = line_objects["Section Index"][mask]
        length = line_objects["Length"][mask]
        centroids, vec_x, vec_y, vec_z, rotation_matrices = generate_element_local_axes(nodes=nodes, end_nodes_index=end_nodes_idx, ndim=ndim)
        geometric_transf, geometric_transf_name = generate_geometric_transformation(element_type=element_type, vec_z=vec_z)
        transformation_tag = np.asarray(self._tagmanager.add(category="Geometric Transformation", n=len(geometric_transf), names=geometric_transf_name), dtype=np.int32)
        elements_connectivity, shared_connected_nodes, current_elements_end, neighbour_elements_end = generate_element_connectivity(nodes=nodes, end_nodes_index=end_nodes_idx)
        is_auto_end_offsets = line_objects["Is Auto End Offsets"]
        rigid_zone_factor = line_objects["Rigid Zone Factor"]
        # Userdefined end offsets
        usr_offsets_length = line_objects["Offsets Length"]
        
        # Autogenerated end offsets
        autogen_offsets_length = autogenerate_offsets_length(
            sections=self._translator_data["Frame Sections"],
            sec_idx=sec_idx,
            element_type=element_type,
            elements_connectivity=elements_connectivity,
            current_elements_end=current_elements_end,
            centroids=centroids,
            rotation_matrices=rotation_matrices,
        )
        offsets_length = np.where(is_auto_end_offsets[:, None], autogen_offsets_length, usr_offsets_length) # Set condition where auto end offsets return is True return autogen offsets length, otherwise usr offsets length
        end_offsets = generate_end_offsets(
            offsets_length=offsets_length,
            rotation_matrices=rotation_matrices,
        )
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
            transformation_tag = transformation_tag,
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
        rotation_matrices = generate_zerolength_element_local_axes(ndim=ndim, elements=elements, child_nodes=child_nodes)
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
        surface_objects = self._translator_data["Surface Objects"] # Retrieve surface objects data
        sec_idx = surface_objects["Section Index"]
        element_type = surface_objects["Element Type"]
        mask = element_type == ElementType.Slab
        n = len(surface_objects["Index"][mask])
        index = np.arange(n, dtype=np.int32)
        unique_name = surface_objects["Unique Name"][mask]
        elements_idx = np.asarray([element for element in surface_objects["Edges Index"][mask]], dtype=np.int32)
        vertices = get_parent_node(nodes=nodes, child_node=surface_objects["Vertices Index"][mask])
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
        point_idx = restraints["Point Index"] # Retrieve point index
        node_idx = get_parent_node(nodes, point_idx) # Get node index
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
        point_loads = self._translator_data["Point Loads"] # Retrieve point loads data
        if len(point_loads) == 0:
            nodal_loads = NodalLoads.empty()
            return nodal_loads
        point_name = point_loads["Point Name"]
        node_tag = self._tagmanager.get_tag(category="Node", names=point_name) # Retrieve node tag
        loadcase_type = point_loads["Load Case"] # Retrieve load case
        loads = point_loads["Loads"] # Retrieve point loads
        result_node_tag, result_loadcase_type, result_loads = generate_group_nodal_loads(
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
        concentrated_line_loads = self._translator_data["Concentrated Line Loads"] # Retrieve concentrated line loads data
        if len(concentrated_line_loads) == 0:
            concentrated_elemental_loads = ConcentratedElementalLoads.empty()
            return concentrated_elemental_loads
        line_name = concentrated_line_loads["Line Name"]
        element_tag = self._tagmanager.get_tag(category="Element", names=line_name) # Retrieve element tag
        loadcase_type = concentrated_line_loads["Load Case"] # Retrieve load case
        direction = concentrated_line_loads["Direction"] # Retrieve load direction
        load = concentrated_line_loads["Load"] # Retrieve concentrated line loads
        location = concentrated_line_loads["Location"] # Retrieve concentrated line loads location
        result_element_tag, result_loadcase_type, result_location, transformed_loads = generate_group_concentrated_element_loads(
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
        distributed_line_loads = self._translator_data["Distributed Line Loads"] # Retrieve distributed line loads data
        if len(distributed_line_loads) == 0:
            distributed_elemental_loads = DistributedElementalLoads.empty()
            return distributed_elemental_loads
        line_name = distributed_line_loads["Line Name"]
        element_tag = self._tagmanager.get_tag(category="Element", names=line_name) # Retrieve element tag
        loadcase_type = distributed_line_loads["Load Case"] # Retrieve load case
        direction = distributed_line_loads["Direction"] # Retrieve load direction
        load = distributed_line_loads["Load"] # Retrieve distributed line loads
        location = distributed_line_loads["Location"] # Retrieve distributed line loads location
        result_element_tag, result_loadcase_type, result_location, transformed_loads = generate_group_distributed_element_loads(
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
        surface_to_edge_loads = self._translator_data["Surface to Edge Loads"] # Retrieve surface to edge loads data
        if len(surface_to_edge_loads) == 0:
            shell_to_elemental_loads = ShellToElementalLoads.empty()
            return shell_to_elemental_loads
        surface_name = surface_to_edge_loads["Surface Name"]
        edge_name = surface_to_edge_loads["Edge Name"]
        element_tag = self._tagmanager.get_tag(category="Element", names=edge_name) # Retrieve element tag
        loadcase_type = surface_to_edge_loads["Load Case"] # Retrieve load case
        direction = surface_to_edge_loads["Direction"] # Retrieve load direction
        load = surface_to_edge_loads["Load"] # Retrieve shell to element loads
        location = surface_to_edge_loads["Location"] # Retrieve shell to element loads location
        result_element_tag, result_loadcase_type, result_location, transformed_loads = generate_group_distributed_element_loads(
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

