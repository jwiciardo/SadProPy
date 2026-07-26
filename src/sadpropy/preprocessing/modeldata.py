import numpy as np
from ._preproc_class import (
    NodeSource,
    ConnectionEnd,
)
from ._preproc_dataclass import (
    ModelDataclass,
    Nodes,
    BeamColumnElements,
    Restraints,
)
from ._exceltranslator import ExcelTranslator
from ._nodegenerator import NodeBuilder
from sadpropy.utility import (
    UserDefinedUnits,
    section_properties,
    fibersection_properties,
    TagManager,
)
from sadpropy.utility._exceptions import ValidationError
from sadpropy.utility.helperfunc import retrieve_output_from_input


__all__ = ["ModelData"]

class ModelData:
    def __init__(self):
        # TAG MANAGER
        self._tagmanager = TagManager()

        # TRANSLATE INPUTFILE AND STORE TO MODEL DATA
        self._translator_result = ExcelTranslator().translate()
    
    def retrieve(self):
        nodes = self._generate_nodes()
        self.node_builder = NodeBuilder(nodes)
        beamcolumn_elements = self._generate_beamcolumn_elements()
        restraints = self._translator_result["Restraints"]
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
            restraints = restraints,
        )
    
    # SUPPORTING METHODS
    def _generate_nodes(self):
        point_objects = self._translator_result["Point Objects"] # Recalling point objects data
        # Original nodes
        n = len(point_objects["Index"])
        unique_name = point_objects["Unique Name"]
        tag = np.asarray(self._tagmanager.add(category="Node", n=n, names=unique_name), dtype=np.int32)
        coords = point_objects["Coordinates"]
        source = np.full(n, NodeSource.Original, dtype=np.int32)
        original_nodes = {
            "Unique Name": unique_name,
            "Coordinates": coords,
            "Source": source,
        }

        # Generated nodes

        nodes = Nodes(
            index = np.arange(n, dtype=np.int32),
            unique_name = unique_name,
            tag = tag,
            coords = coords,
            source = source,
        ) # Storing nodes data to dataclass
        return nodes

    def _generate_beamcolumn_elements(self):
        line_objects = self._translator_result["Line Objects"] # Recall line objects data
        analysis_end_points_idx = line_objects["End Points Index"].copy()
        for line_idx in line_objects["Index"]:
            if not line_objects["Is Zero Length Element"][line_idx]:
                continue
            i_node_original = line_objects["End Points Index"][line_idx][ConnectionEnd.I_End]
            j_node_original = line_objects["End Points Index"][line_idx][ConnectionEnd.J_End]
            analysis_end_points_idx[line_idx][ConnectionEnd.I_End] = (self.node_builder.duplicate_node(
                line_idx=line_idx,
                end=ConnectionEnd.I_End,
                original_node=i_node_original,
                source=NodeSource.Zero_Length_Element,
            ))
            analysis_end_points_idx[line_idx][ConnectionEnd.J_End] = (self.node_builder.duplicate_node(
                line_idx=line_idx,
                end=ConnectionEnd.J_End,
                original_node=j_node_original,
                source=NodeSource.Zero_Length_Element,
            ))
            
        return analysis_end_points_idx

        
    #def _generate_beamcolumn_elements(self, nodes):
        data_lineobj = self._translator_result["Line Objects"] # Recall line objects data
        data_pointobj = self._translator_result["Point Objects"] # Recall point objects data
        secs_list = self._translator_result["Sections List"] # Recall sections list data
        element_type = np.fromiter((secs_list[sc].element_type[idx]
            for sc, idx in zip(data_lineobj["Section Class"], data_lineobj["Section Index"])), dtype="U15")
        mask = (element_type == "Beam")
        #mask = (element_type == "Column") | (element_type == "Beam")
        n = len(data_lineobj["Index"][mask])
        index = np.arange(n, dtype=np.int32)
        unique_name = data_lineobj["Unique Name"][mask]
        point_name = data_pointobj.unique_name
        end_points_idx = data_lineobj.end_points_idx[mask]
        end_nodes_idx = retrieve_output_from_input(
            inputdata=end_points_idx,
            shared_data_in=point_name,
            outputdata=nodes.index, 
            shared_data_out=nodes.label,
        )
        return element_type
    
    #def _translate_line_objects(self, point_objects, project_information):
        sheet_name = "Line Objects"
        data = self._reader.read(sheet_name=sheet_name, start_row=13) # Reading Sheet "Line Objects" in the Input file
        self._validate_data(data=data, sheet_name=sheet_name, mandatory=True)
        n = len(data)
        index = np.arange(n, dtype=np.int32)
        unique_name = np.empty(n, dtype="U15")
        end_points_idx = np.empty((n, 2), dtype=np.int32)
        sec_class = np.empty(n, dtype=np.int32)
        sec_idx = np.empty(n, dtype=np.int32)
        is_zero_length_element = np.empty(n, dtype=bool)
        end_offset_option = np.empty(n, dtype="U22")
        end_offsets = np.empty((n, 2), dtype=np.float64)
        name_to_idx = {}
        for i, row in enumerate(data):
            name = str(row["Unique Name"])
            if name in name_to_idx:
                raise ValidationError(f"Duplicate Line object name '{name}'")
            name_to_idx[name] = index[i]
            unique_name[i] = name
            end_points_idx[i] = (point_objects.name_to_idx[str(row["I-End"])], point_objects.name_to_idx[str(row["J-End"])],)
            end_offset_option[i] = str(row["End Offset"])
            end_offsets[i] = (
                self._to_internalunits.length(value=row["I-End Offset Length"] if row["I-End Offset Length"] is not None else 0.0),
                self._to_internalunits.length(value=row["J-End Offset Length"] if row["J-End Offset Length"] is not None else 0.0),
            )
            sec_class[i], _, sec_idx[i] = self._retrieve_section_index(sec_name=str(row["Section"]))
            is_zero_length_element[i] = (str(row["Zero Length Element"]).strip().lower() == "yes")
        line_objects = LineObjects(
            index = index,
            unique_name = unique_name,
            end_points_idx = end_points_idx,
            end_offset_option = end_offset_option,
            end_offsets = end_offsets,
            sec_class = sec_class,
            sec_idx = sec_idx,
            is_zero_length_element = is_zero_length_element,
            name_to_idx = name_to_idx,
        ) # Defining dataclass for each line object
        return line_objects

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
    
    def _translate_restraints(self, point_objects):
        sheet_name="Restraints"
        data = self._reader.read(sheet_name=sheet_name, start_row=10) # Reading Sheet "Restraints" in the Input file
        self._validate_data(data=data, sheet_name=sheet_name, mandatory=True)
        n = len(data)
        point_idx = np.empty(n, dtype=np.int32)
        dofs = np.empty((n, 6), dtype=np.int32)
        idx_set = set()
        for i, row in enumerate(data):
            point_name = str(row["Point"])
            idx = point_objects.name_to_idx[point_name]
            if idx in idx_set:
                raise ValidationError(f"Duplicate Restraints at Point '{point_name}'")
            idx_set.add(idx)
            point_idx[i] = idx
            dofs[i] = (
                int(row["UX"]),
                int(row["UY"]),
                int(row["UZ"]),
                int(row["RX"]),
                int(row["RY"]),
                int(row["RZ"]),
            )
        restraints = Restraints(
            point_idx = point_idx,
            dofs = dofs,
        ) # Defining dataclass for each restraint
        return restraints



    