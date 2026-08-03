import numpy as np
from ._exceltranslator import ExcelTranslator
from ._nodegenerator import autogenerate_nodes
from ._elementconnectivity import (
    generate_beamcolumn_element_local_axes,
    generate_beamcolumn_element_connectivity,
    autogenerate_offsets_length,
    generate_end_offsets,
    generate_geometric_transformation,
)
from ._zerolengthelements import generate_zerolength_element_local_axes
from ._preproc_dataclass import (
    ModelDataclass,
    Nodes,
    BeamColumnElements,
    ZeroLengthElements,
    Restraints,
)
from ._preproc_class import NodeSource
from sadpropy.utility import TagManager
from sadpropy.utility._exceptions import ValidationError
from sadpropy.utility.helperfunc import get_parent_node


__all__ = ["ModelData"]

class ModelData:
    def __init__(self):
        # TAG MANAGER
        self._tagmanager = TagManager()

        # TRANSLATE INPUTFILE AND STORE TO MODEL DATA
        self._translator_result = ExcelTranslator().translate()

        # DICTIONARY LIST
        self._elements_list = []
    
    def retrieve(self):
        nodes = self._generate_nodes()
        beamcolumn_elements = self._generate_beamcolumn_elements(nodes=nodes)
        zerolength_elements = self._generate_zero_length_elements(nodes=nodes)
        restraints = self._generate_restraints(nodes=nodes)
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
            beamcolumn_elements = beamcolumn_elements,
            zerolength_elements = zerolength_elements,
            elements_list = self._elements_list,
            restraints = restraints,
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

    def _generate_beamcolumn_elements(self, nodes):
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
        centroids, length, vec_x, vec_y, vec_z, rotation_matrix = generate_beamcolumn_element_local_axes(nodes=nodes, end_nodes_index=end_nodes_idx, ndim=ndim)
        geometric_transf, geometric_transf_name = generate_geometric_transformation(element_type=element_type, vec_z=vec_z)
        transformation_tag = np.asarray(self._tagmanager.add(category="Geometric Transformation", n=len(geometric_transf), names=geometric_transf_name), dtype=np.int32)
        elements_connectivity, shared_connected_nodes, current_elements_end, neighbour_elements_end = generate_beamcolumn_element_connectivity(nodes=nodes, end_nodes_index=end_nodes_idx)
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
        beamcolumn_elements = BeamColumnElements(
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
        self._elements_list.append(beamcolumn_elements) # Append BeamColumnElements into Elements List
        return beamcolumn_elements

    def _generate_zero_length_elements(self, nodes):
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
        rotation_matrix = generate_zerolength_element_local_axes(ndim=ndim, elements_list=self._elements_list, child_nodes=child_nodes)
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



    #def _translate_surface_objects(self, line_objects, slab_sections):
        sheet_name = "Surface Objects"
        data = self._reader.read(sheet_name=sheet_name, start_row=9) # Reading Sheet "Surface Objects" in the Input file
        self._validate_data(data=data, sheet_name=sheet_name, mandatory=True)
        n = len(data)
        index = np.arange(n, dtype=np.int32)
        unique_name = np.empty(n, dtype="U15")
        edges_idx = np.empty((n, 4), dtype=np.int32)
        vertices_idx = np.empty((n, 4), dtype=np.int32)
        sec_class = np.empty(n, dtype=np.int32)
        sec_idx = np.empty(n, dtype=np.int32)
        name_to_idx = {}
        for i, row in enumerate(data):
            name = str(row["Unique Name"])
            if name in name_to_idx:
                raise ValidationError(f"Duplicate Surface object name '{name}'")
            name_to_idx[name] = index[i]
            unique_name[i] = name
            edges_name = [edge for edge in (str(row["Edge 1"]), str(row["Edge 2"]), str(row["Edge 3"]), str(row["Edge 4"]),) if edge is not None]
            edges_idx[i], vertices_idx[i] = get_edges_and_vertices_from_surface(
                edges_name=edges_name,
                line_objects=line_objects,
                surface_name=name,
            )
            sec_class[i], _, sec_idx[i] = self._retrieve_slabsection_index(
                sec_name=str(row["Section"]),
                secs_list=slab_sections,
            )
        surface_objects = SurfaceObjects(
            index = index,
            unique_name = unique_name,
            edges_idx = edges_idx,
            vertices_idx = vertices_idx,
            sec_class = sec_class,
            sec_idx = sec_idx,
            name_to_idx = name_to_idx,
        ) # Defining dataclass for each surface object
        return surface_objects
    
    def _generate_restraints(self, nodes):
        elements = self._elements_list # Retrieve elements list
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



    