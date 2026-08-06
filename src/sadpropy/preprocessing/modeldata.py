import numpy as np
from ._exceltranslator import ExcelTranslator
from ._nodegenerator import autogenerate_nodes
from ._elementconnectivity import (
    generate_element_local_axes,
    generate_element_connectivity,
    autogenerate_offsets_length,
    generate_end_offsets,
    generate_geometric_transformation,
)
from ._loadgenerator import (
    generate_unique_nodal_loads,
    generate_unique_concentrated_element_loads,
)
from ._zerolengthelements import generate_zerolength_element_local_axes
from ._preproc_dataclass import (
    ModelDataclass,
    Nodes,
    Elements,
    ZeroLengthElements,
    Restraints,
    NodalLoads,
    ConcentratedElementLoads,
)
from ._preproc_class import (
    NodeSource,
    LoadCaseType,
    LoadDirection,
)
from sadpropy.utility import TagManager
from sadpropy.utility._exceptions import ValidationError
from sadpropy.utility.helperfunc import transform_to_local_axes, get_parent_node


__all__ = ["ModelData"]

class ModelData:
    def __init__(self):
        # TAG MANAGER
        self._tagmanager = TagManager()

        # TRANSLATE INPUTFILE AND STORE TO MODEL DATA
        self._translator_result = ExcelTranslator().translate()
    
    def retrieve(self):
        nodes = self._generate_nodes()
        elements = self._generate_elements(nodes=nodes)
        zerolength_elements = self._generate_zero_length_elements(nodes=nodes, elements=elements)
        restraints = self._generate_restraints(nodes=nodes)
        nodal_loads = self._generate_nodal_loads()
        concentrated_element_loads = self._generate_concentrated_element_loads()
        print()
        return ModelDataclass(
            filepath_information = self._translator_result["Filepath Information"],
            project_information = self._translator_result["Project Information"],
            userdefined_units = self._translator_result["Userdefined Units"],
            analysis_preferences = self._translator_result["Analysis Preferences"],
            materials = self._translator_result["Materials"],
            mat_concrete04 = self._translator_result["Mat: Concrete04"],
            mat_steel02 = self._translator_result["Mat: Steel02"],
            mat_minmax = self._translator_result["Mat: Minmax"],
            mat_imk = self._translator_result["Mat: IMK"],
            materials_list = self._translator_result["Materials List"],
            frame_sections = self._translator_result["Frame Sections"],
            sec_fiber = self._translator_result["Sec: Fiber"],
            sec_aggregator = self._translator_result["Sec: Aggregator"],
            sections_list = self._translator_result["Sections List"],
            slab_sections = self._translator_result["Slab Sections"],
            storeys = self._translator_result["Storeys"],
            nodes = nodes,
            elements = elements,
            zerolength_elements = zerolength_elements,
            restraints = restraints,
            nodal_loads = nodal_loads,
            concentrated_element_loads = concentrated_element_loads,
        )
    
    # SUPPORTING METHODS
    def _generate_nodes(self):
        point_objects = self._translator_result["Point Objects"] # Retrieve point objects data
        line_objects = self._translator_result["Line Objects"] # Retrieve line objects data

        # Userdefined generated nodes
        n = len(point_objects["Index"])
        usr_unique_name = point_objects["Unique Name"]
        usr_coords = point_objects["Coordinates"]
        usr_generated_source = np.full(n, NodeSource.USR, dtype=np.int32)
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
        coords = np.vstack((usr_coords, np.asarray(gen_coords, dtype=np.float64)))
        generated_source = np.concatenate((usr_generated_source, np.asarray(gen_generated_source, dtype=np.int32)))
        generated_from = np.concatenate((usr_generated_from, np.asarray(gen_generated_from, dtype="U15")))
        self._line_to_end_nodes_map = usr_line_to_end_nodes | gen_line_to_end_nodes
        m = len(unique_name)
        tag = np.asarray(self._tagmanager.add(category="Node", n=m, names=unique_name), dtype=np.int32)
        name_to_idx = {str(name): np.int32(i) for i, name in enumerate(unique_name)}
        nodes = Nodes(
            index = np.arange(m, dtype=np.int32),
            unique_name = unique_name,
            tag = tag,
            coords = coords,
            generated_source = generated_source,
            generated_from = generated_from,
            name_to_idx=name_to_idx,
        ) # Store nodes data to dataclass
        return nodes

    def _generate_elements(self, nodes):
        ndim = self._translator_result["Project Information"].ndim # Retrieve number of dimensional space
        line_objects = self._translator_result["Line Objects"] # Retrieve line objects data
        sec_class = line_objects["Section Class"]
        sec_idx = line_objects["Section Index"]
        element_type = line_objects["Element Type"]
        mask = (element_type == "Column") | (element_type == "Beam")
        n = len(line_objects["Index"][mask])
        unique_name = line_objects["Unique Name"][mask]
        tag = np.asarray(self._tagmanager.add(category="Element", n=n, names=unique_name), dtype=np.int32)
        end_nodes_idx = np.asarray([self._line_to_end_nodes_map[line_idx] for line_idx in line_objects["Index"][mask]], dtype=np.int32)
        centroids, length, vec_x, vec_y, vec_z, rotation_matrix = generate_element_local_axes(nodes=nodes, end_nodes_index=end_nodes_idx, ndim=ndim)
        geometric_transf, geometric_transf_name = generate_geometric_transformation(element_type=element_type, vec_z=vec_z)
        transformation_tag = np.asarray(self._tagmanager.add(category="Geometric Transformation", n=len(geometric_transf), names=geometric_transf_name), dtype=np.int32)
        elements_connectivity, shared_connected_nodes, current_elements_end, neighbour_elements_end = generate_element_connectivity(nodes=nodes, end_nodes_index=end_nodes_idx)
        is_auto_end_offsets = line_objects["Is Auto End Offsets"]
        rigid_zone_factor = line_objects["Rigid Zone Factor"]
        # Userdefined end offsets
        usr_offsets_length = line_objects["Offsets Length"]
        
        # Autogenerated end offsets
        autogen_offsets_length = autogenerate_offsets_length(
            secs_list=self._translator_result["Sections List"],
            sec_class=sec_class,
            sec_idx=sec_idx,
            element_type=element_type,
            elements_connectivity=elements_connectivity,
            current_elements_end=current_elements_end,
            centroids=centroids,
            rotation_matrix=rotation_matrix,
        )
        offsets_length = np.where(is_auto_end_offsets[:, None], autogen_offsets_length, usr_offsets_length) # Set condition where auto end offsets return is True return autogen offsets length, otherwise usr offsets length
        end_offsets = generate_end_offsets(
            offsets_length=offsets_length,
            rotation_matrix=rotation_matrix,
        )
        name_to_idx = {str(name): np.int32(i) for i, name in enumerate(unique_name)}
        elements = Elements(
            index = np.arange(n, dtype=np.int32),
            unique_name = unique_name,
            tag = tag,
            end_nodes_idx = end_nodes_idx,
            element_type = element_type,
            sec_class = sec_class,
            sec_idx = sec_idx,
            centroids = centroids,
            length = length,
            rotation_matrix = rotation_matrix,
            transformation_tag = transformation_tag,
            elements_connectivity = elements_connectivity,
            shared_connected_nodes = shared_connected_nodes,
            current_elements_end = current_elements_end,
            neighbour_elements_end = neighbour_elements_end,
            rigid_zone_factor = rigid_zone_factor,
            offsets_length = offsets_length,
            end_offsets = end_offsets,
            name_to_idx = name_to_idx,
        ) # Store beamcolumn elements data to dataclass
        return elements

    def _generate_zero_length_elements(self, nodes, elements):
        ndim = self._translator_result["Project Information"].ndim # Retrieve number of dimensional space
        nodes_generated_from = nodes.generated_from # Retrieve parent name of generated node
        child_nodes = np.asarray([node_idx for node_idx in nodes.index[nodes_generated_from != ""]], dtype=np.int32) # Filter empty string values in nodes index
        parent_nodes = get_parent_node(nodes=nodes, child_node=child_nodes) # Get parent node
        n = len(child_nodes)
        unique_name = np.empty(n, dtype="U15")
        end_nodes_idx = np.empty((n, 2), dtype=np.int32)
        for i in range(n):
            name = f"ZL{i}"
            unique_name[i] = name
            end_nodes_idx[i] = [parent_nodes[i], child_nodes[i]]
        tag = np.asarray(self._tagmanager.add(category="Element", n=n, names=unique_name), dtype=np.int32)
        element_type = np.full(n, f"Zero Length", dtype="U15")
        rotation_matrix = generate_zerolength_element_local_axes(ndim=ndim, elements=elements, child_nodes=child_nodes)
        name_to_idx = {str(name): np.int32(i) for i, name in enumerate(unique_name)}
        zerolength_elements = ZeroLengthElements(
            index = np.arange(n, dtype=np.int32),
            unique_name = unique_name,
            tag = tag,
            end_nodes_idx = end_nodes_idx,
            element_type = element_type,
            rotation_matrix = rotation_matrix,
            name_to_idx = name_to_idx,
        ) # Store zerolength elements data to dataclass
        return zerolength_elements
    
    def _generate_restraints(self, nodes):
        restraints = self._translator_result["Restraints"] # Retrieve restraints data
        point_idx = restraints["Point Index"] # Retrieve point index
        node_idx = get_parent_node(nodes, point_idx) # Get node index
        node_name = nodes.unique_name[node_idx] # Retrieve node name
        node_tag = nodes.tag[node_idx] # Retrieve node tag
        dofs = restraints["DOFs"] # Retrieve dofs
        restraints = Restraints(
            node_idx = node_idx,
            node_name = node_name,
            node_tag = node_tag,
            dofs = dofs,
        ) # Store restraints data to dataclass
        return restraints

    def _generate_nodal_loads(self):
        point_loads = self._translator_result["Point Loads"] # Retrieve point loads data
        if len(point_loads) == 0:
            nodal_loads = NodalLoads.empty()
            return nodal_loads
        point_name = point_loads["Point Name"]
        n = len(point_name)
        node_tag = self._tagmanager.get_tag(category="Node", names=point_name) # Retrieve node tag)
        loadcase_type = np.fromiter((LoadCaseType()._get_loadcase_class(lc)
            for lc in point_loads["Load Case"]), dtype=np.int32, count=n)
        loads = point_loads["Loads"] # Retrieve point loads
        unique_node_tag, unique_loadcase_type, unique_loads = generate_unique_nodal_loads(
            node_tag,
            loadcase_type,
            loads,
        )
        nodal_loads = NodalLoads(
            node_tag = unique_node_tag,
            loadcase_type = unique_loadcase_type,
            loads = unique_loads,
        ) # Store point loads data to dataclass
        return nodal_loads

    def _generate_concentrated_element_loads(self):
        ndim = self._translator_result["Project Information"].ndim # Retrieve number of dimensional space
        concentrated_line_loads = self._translator_result["Concentrated Line Loads"] # Retrieve concentrated line loads data
        if len(concentrated_line_loads) == 0:
            concentrated_element_loads = ConcentratedElementLoads.empty()
            return concentrated_element_loads
        line_name = concentrated_line_loads["Line Name"]
        n = len(line_name)
        element_tag = self._tagmanager.get_tag(category="Element", names=line_name) # Retrieve element tag
        loadcase_type = np.fromiter((LoadCaseType()._get_loadcase_class(lc)
            for lc in concentrated_line_loads["Load Case"]), dtype=np.int32, count=n)
        direction = concentrated_line_loads["Direction"] # Retrieve load direction
        load = concentrated_line_loads["Load"] # Retrieve concentrated line loads
        location = concentrated_line_loads["Location"] # Retrieve concentrated line loads location
        unique_element_tag, unique_loadcase_type, unique_direction, unique_location, unique_load = generate_unique_concentrated_element_loads(
            element_tag,
            loadcase_type,
            direction,
            location,
            load,
        )
        transformed_load = np.zeros(len(unique_load), dtype=unique_load.dtype)
        for i, dir in enumerate(unique_direction):
            load = unique_load[i]
            if ndim == 3:
                load_vec = LoadDirection()._get_load_direction3D_class(dir) * load
            else:
                load_vec = LoadDirection()._get_load_direction2D_class(dir) * load

            print(dir, load_vec)
        return 0

