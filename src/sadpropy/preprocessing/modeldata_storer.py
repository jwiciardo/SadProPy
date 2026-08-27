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
from .preprocessing_object._mass import (
    _generate_concentrated_element_to_nodal_gravity_loads,
    _generate_distributed_element_to_nodal_gravity_loads,
    _generate_summed_grouping_nodal_loads,
    _generate_summed_grouping_storey_masses,
)
from .preprocessing_object._diaphragm import _get_storey_nodes
from .preprocessing_object._zero_length_element import _generate_zerolength_element_local_axes
from .preprocessing_class_index import ElementType, NodeSource, LoadType
from .preprocessing_class import MassSource
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
    SelfweightToElementalLoads,
    NodalMasses,
    Diaphragms,
)
from ..utility import TagManager
from ..utility.helper import get_parent_node
from ..utility.constant import GRAVITATIONAL_ACCELERATION


__all__ = ["ModelDataStorer"]

g = GRAVITATIONAL_ACCELERATION

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
        selfweight_to_elemental_loads = self._generate_selfweight_to_elemental_loads(elements=elements)
        nodal_masses = self._generate_masses(
            nodes=nodes,
            elements=elements,
            nodal_loads=nodal_loads,
            concentrated_elemental_loads=concentrated_elemental_loads,
            distributed_elemental_loads=distributed_elemental_loads,
            shell_to_elemental_loads=shell_to_elemental_loads,
            selfweight_to_elemental_loads=selfweight_to_elemental_loads,
        )
        diaphragms = self._generate_diaphragms(nodes=nodes, masses=nodal_masses)
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
            load_cases = self._translator_data["Load Cases"],
            nodal_loads = nodal_loads,
            concentrated_elemental_loads = concentrated_elemental_loads,
            distributed_elemental_loads = distributed_elemental_loads,
            shell_to_elemental_loads = shell_to_elemental_loads,
            selfweight_to_elemental_loads = selfweight_to_elemental_loads,
            nodal_masses = nodal_masses,
            diaphragms = diaphragms,
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
            coords = np.round(np.vstack((usr_coords, np.asarray(gen_coords, dtype=np.float64))), decimals=6)
        else:
            coords = np.round(usr_coords, decimals=6)
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
        is_auto_end_offsets = element_objects["Is Auto End Offsets"][mask]
        rigid_zone_factor = element_objects["Rigid Zone Factor"][mask]
        # Userdefined end offsets
        usr_offsets_length = element_objects["Offsets Length"][mask]
        
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
        geom_transf_idx, transf_vec, transf_offsets, transf_name = _generate_geometric_transformation(
            element_type=element_type,
            vec_z=vec_z, 
            end_offsets=end_offsets,
            rigid_zone_factor=rigid_zone_factor
        )
        transf_tag = np.asarray(self._tagmanager.add(category="Geometric Transformation", n=len(transf_vec), names=transf_name), dtype=np.int32)
        geom_transf_tag = np.full_like(geom_transf_idx, -1)
        geom_transf_tag[geom_transf_idx >= 0] = transf_tag[geom_transf_idx[geom_transf_idx >= 0]]
        selfweight = element_objects["Selfweight"][mask]
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
            elements_connectivity = elements_connectivity,
            shared_connected_nodes = shared_connected_nodes,
            current_elements_end = current_elements_end,
            neighbour_elements_end = neighbour_elements_end,
            rigid_zone_factor = rigid_zone_factor,
            offsets_length = offsets_length,
            end_offsets = end_offsets,
            transf_tag = transf_tag,
            transf_vec = transf_vec,
            transf_offsets = transf_offsets,
            transformation_tag = geom_transf_tag,
            selfweight = selfweight,
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
        element_type = shell_objects["Element Type"]
        mask = element_type == ElementType.Slab
        n = len(shell_objects["Index"][mask])
        index = np.arange(n, dtype=np.int32)
        unique_name = shell_objects["Unique Name"][mask]
        elements_idx = np.asarray([element for element in shell_objects["Edges Index"][mask]], dtype=np.int32)
        vertices = get_parent_node(nodes=nodes, child_node=shell_objects["Vertices Index"][mask])
        nodes_idx = np.asarray([node for node in vertices], dtype=np.int32)
        sec_idx = shell_objects["Section Index"][mask]
        area = shell_objects["Area"][mask]
        selfweight = shell_objects["Selfweight"][mask]
        shells = Shells(
            index = index,
            unique_name = unique_name,
            elements_idx = elements_idx,
            nodes_idx = nodes_idx,
            element_type = element_type,
            sec_idx = sec_idx,
            area = area,
            selfweight = selfweight,
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

    def _generate_selfweight_to_elemental_loads(self, elements):
        ndim = self._translator_data["Project Information"].ndim # Retrieve number of dimensional space
        selfweight_loads = self._translator_data["Selfweight to Elemental Loads"] # Retrieve selfweight to elemental loads data
        if len(selfweight_loads) == 0:
            selfweight_to_elemental_loads = SelfweightToElementalLoads.empty()
            return selfweight_to_elemental_loads
        element_name = selfweight_loads["Element Name"]
        element_tag = self._tagmanager.get_tag(category="Element", names=element_name) # Retrieve element tag
        loadcase_type = selfweight_loads["Load Case"] # Retrieve load case
        direction = selfweight_loads["Direction"] # Retrieve load direction
        load = selfweight_loads["Load"] # Retrieve shell to element loads
        location = selfweight_loads["Location"] # Retrieve shell to element loads location
        result_element_tag, result_loadcase_type, result_location, transformed_loads = _generate_group_distributed_element_loads(
            ndim=ndim,
            elements=elements,
            element_tag=element_tag,
            loadcase_type=loadcase_type,
            direction=direction,
            location=location,
            load=load,
        )
        selfweight_to_elemental_loads = SelfweightToElementalLoads(
            element_tag = result_element_tag,
            loadcase = result_loadcase_type,
            location = result_location,
            loads = transformed_loads,
        ) # Store shell to elemental loads data to dataclass
        return selfweight_to_elemental_loads

    def _generate_masses(self, nodes, elements, nodal_loads, concentrated_elemental_loads, distributed_elemental_loads, shell_to_elemental_loads, selfweight_to_elemental_loads):
        mass_source_ref = self._translator_data["Analysis Preferences"].mass_source_ref
        factor = MassSource.get(mass_source_ref)
        
        # Nodal loads
        nod_loadcase_mask = (nodal_loads.loadcase == LoadType.Dead) | (nodal_loads.loadcase == LoadType.Dead) | (nodal_loads.loadcase == LoadType.Live) | (nodal_loads.loadcase == LoadType.LiveRoof)
        nod_node_tag = nodal_loads.node_tag[nod_loadcase_mask]
        nod_loadcase = np.empty(0, dtype=np.int8)
        nod_load = np.empty(0, dtype=np.float64)
        if len(nod_node_tag) != 0:
            nod_loadcase = nodal_loads.loadcase[nod_loadcase_mask]
            nod_load = nodal_loads.loads[nod_loadcase_mask, 2]

        # Concentrated elemental loads
        conc_loadcase_mask = (concentrated_elemental_loads.loadcase == LoadType.Dead) | (concentrated_elemental_loads.loadcase == LoadType.Dead) | (concentrated_elemental_loads.loadcase == LoadType.Live) | (concentrated_elemental_loads.loadcase == LoadType.LiveRoof)
        conc_element_tag = concentrated_elemental_loads.element_tag[conc_loadcase_mask]
        conc_node_tag = np.empty(0, dtype=np.int32)
        conc_loadcase = np.empty(0, dtype=np.int8)
        conc_load = np.empty(0, dtype=np.float64)
        if len(conc_element_tag) != 0:
            conc_loadcase = concentrated_elemental_loads.loadcase[conc_loadcase_mask]
            conc_location = concentrated_elemental_loads.location[conc_loadcase_mask]
            conc_loads = concentrated_elemental_loads.loads[conc_loadcase_mask]
            conc_inode_tag, conc_jnode_tag, conc_loadcase, conc_nodal_i_load, conc_nodal_j_load = _generate_concentrated_element_to_nodal_gravity_loads(
                nodes=nodes,
                elements=elements, 
                element_tag=conc_element_tag, 
                loadcase=conc_loadcase, 
                location=conc_location, 
                loads=conc_loads,
            )
            conc_node_tag = np.concatenate([conc_inode_tag, conc_jnode_tag])
            conc_loadcase = np.concatenate([conc_loadcase, conc_loadcase])
            conc_load = np.concatenate([conc_nodal_i_load, conc_nodal_j_load])

        # Distributed elemental loads
        dist_loadcase_mask = (distributed_elemental_loads.loadcase == LoadType.Dead) | (distributed_elemental_loads.loadcase == LoadType.Dead) | (distributed_elemental_loads.loadcase == LoadType.Live) | (distributed_elemental_loads.loadcase == LoadType.LiveRoof)
        dist_element_tag = distributed_elemental_loads.element_tag[dist_loadcase_mask]
        dist_node_tag = np.empty(0, dtype=np.int32)
        dist_loadcase = np.empty(0, dtype=np.int8)
        dist_load = np.empty(0, dtype=np.float64)
        if len(dist_element_tag) != 0:
            dist_loadcase = distributed_elemental_loads.loadcase[dist_loadcase_mask]
            dist_location = distributed_elemental_loads.location[dist_loadcase_mask]
            dist_loads = distributed_elemental_loads.loads[dist_loadcase_mask]
            dist_inode_tag, dist_jnode_tag, dist_loadcase, dist_nodal_i_load, dist_nodal_j_load = _generate_distributed_element_to_nodal_gravity_loads(
                nodes=nodes,
                elements=elements, 
                element_tag=dist_element_tag, 
                loadcase=dist_loadcase, 
                location=dist_location, 
                loads=dist_loads,
            )
            dist_node_tag = np.concatenate([dist_inode_tag, dist_jnode_tag])
            dist_loadcase = np.concatenate([dist_loadcase, dist_loadcase])
            dist_load = np.concatenate([dist_nodal_i_load, dist_nodal_j_load])

        # Shell to elemental loads
        shell_loadcase_mask = (shell_to_elemental_loads.loadcase == LoadType.Dead) | (shell_to_elemental_loads.loadcase == LoadType.Dead) | (shell_to_elemental_loads.loadcase == LoadType.Live) | (shell_to_elemental_loads.loadcase == LoadType.LiveRoof)
        shell_element_tag = shell_to_elemental_loads.element_tag[shell_loadcase_mask]
        shell_node_tag = np.empty(0, dtype=np.int32)
        shell_loadcase = np.empty(0, dtype=np.int8)
        shell_load = np.empty(0, dtype=np.float64)
        if len(shell_element_tag) != 0:
            shell_loadcase = shell_to_elemental_loads.loadcase[shell_loadcase_mask]
            shell_location = shell_to_elemental_loads.location[shell_loadcase_mask]
            shell_loads = shell_to_elemental_loads.loads[shell_loadcase_mask]
            shell_inode_tag, shell_jnode_tag, shell_loadcase, shell_nodal_i_load, shell_nodal_j_load = _generate_distributed_element_to_nodal_gravity_loads(
                nodes=nodes,
                elements=elements, 
                element_tag=shell_element_tag, 
                loadcase=shell_loadcase, 
                location=shell_location, 
                loads=shell_loads,
            )
            shell_node_tag = np.concatenate([shell_inode_tag, shell_jnode_tag])
            shell_loadcase = np.concatenate([shell_loadcase, shell_loadcase])
            shell_load = np.concatenate([shell_nodal_i_load, shell_nodal_j_load])

        # Selfweight to elemental loads
        selfweight_loadcase_mask = (selfweight_to_elemental_loads.loadcase == LoadType.Dead) | (selfweight_to_elemental_loads.loadcase == LoadType.Dead) | (selfweight_to_elemental_loads.loadcase == LoadType.Live) | (selfweight_to_elemental_loads.loadcase == LoadType.LiveRoof)
        selfweight_element_tag = selfweight_to_elemental_loads.element_tag[selfweight_loadcase_mask]
        selfweight_node_tag = np.empty(0, dtype=np.int32)
        selfweight_loadcase = np.empty(0, dtype=np.int8)
        selfweight_load = np.empty(0, dtype=np.float64)
        if len(selfweight_element_tag) != 0:
            selfweight_loadcase = selfweight_to_elemental_loads.loadcase[selfweight_loadcase_mask]
            selfweight_location = selfweight_to_elemental_loads.location[selfweight_loadcase_mask]
            selfweight_loads = selfweight_to_elemental_loads.loads[selfweight_loadcase_mask]
            selfweight_inode_tag, selfweight_jnode_tag, selfweight_loadcase, selfweight_nodal_i_load, selfweight_nodal_j_load = _generate_distributed_element_to_nodal_gravity_loads(
                nodes=nodes,
                elements=elements, 
                element_tag=selfweight_element_tag, 
                loadcase=selfweight_loadcase, 
                location=selfweight_location, 
                loads=selfweight_loads,
            )
            selfweight_node_tag = np.concatenate([selfweight_inode_tag, selfweight_jnode_tag])
            selfweight_loadcase = np.concatenate([selfweight_loadcase, selfweight_loadcase])
            selfweight_load = np.concatenate([selfweight_nodal_i_load, selfweight_nodal_j_load])

        # Concatenate all loads
        node_tag = np.concatenate([nod_node_tag, conc_node_tag, dist_node_tag, shell_node_tag, selfweight_node_tag])
        loadcase = np.concatenate([nod_loadcase, conc_loadcase, dist_loadcase, shell_loadcase, selfweight_loadcase])
        mass_factor = np.array([factor[lc] for lc in loadcase])
        load = np.concatenate([nod_load, conc_load, dist_load, shell_load, selfweight_load])
        load = np.abs(load) * mass_factor
        result_node_tag, result_load = _generate_summed_grouping_nodal_loads(node_tag=node_tag, load=load)

        # Compute nodal mass
        result_mass = result_load / g
        nodal_masses = NodalMasses(
            node_tag = result_node_tag,
            weight = result_load,
            mass = result_mass,
        ) # Store nodal masses data to dataclass
        return nodal_masses

    def _generate_diaphragms(self, nodes, masses):
        # Total storey mass
        masses_node_idx = nodes.tag_to_idx(tags=masses.node_tag)
        masses_node_coords = nodes.coords[masses_node_idx]
        masses_nodal_mass = masses.mass
        total_storey_mass, elevation = _generate_summed_grouping_storey_masses(node_coords=masses_node_coords, masses=masses_nodal_mass)

        # Total weighted storey mass
        weighted_nodal_mass = masses_node_coords * masses_nodal_mass[:, None]
        total_weighted_storey_mass, _ =_generate_summed_grouping_storey_masses(node_coords=masses_node_coords, masses=weighted_nodal_mass)
        diaph_coords = np.round(total_weighted_storey_mass / total_storey_mass[:, None], decimals=6)

        # Diaphragms properties
        n = len(diaph_coords)
        index = np.arange(n, dtype=np.int32)
        diaph_name = np.array([f"Diaph-{z:.1f}" for z in diaph_coords[:, 2]], dtype="U32")
        diaph_tag = np.asarray(self._tagmanager.add(category="Node", n=n, names=diaph_name), dtype=np.int32)
        dofs = np.tile((0, 0, 1, 1, 1, 0), (n, 1)).astype(np.int8)
        constrained_node_idx = _get_storey_nodes(nodes=nodes, elevation=elevation)
        constrained_node_tag = self._tagmanager.get_tag(category="Node", names=nodes.unique_name[constrained_node_idx]) # Retrieve constrained node tag
        diaphragms = Diaphragms(
            index = index,
            unique_name = diaph_name,
            diaph_tag = diaph_tag,
            coords = diaph_coords,
            dofs = dofs,
            constrained_nodes_idx = constrained_node_idx,
            constrained_nodes_tag = constrained_node_tag,
            storey_mass = total_storey_mass,
        ) # Store diaphragms data to dataclass
        return diaphragms


