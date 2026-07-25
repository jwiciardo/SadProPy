import numpy as np
from ._preproc_dataclass import (
    ModelDataclass,
    Nodes,
    BeamColumnElements,
    Restraints,
)
from ._exceltranslator import ExcelTranslator
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
        point_objects = self._translator_result["Point Objects"],
        line_objects = self._translator_result["Line Objects"],
        surface_objects = self._translator_result["Surface Objects"],
        nodes = self._generate_nodes(point_objects=point_objects),
        restraints = self._translator_result["Restraints"],
        return ModelDataclass(
            filepath_information=filepath_information,
            project_information=project_information,
            userdefined_units=userdefined_units,
            analysis_preferences=analysis_preferences,
            materials=materials,
            mat_concrete04=mat_concrete04,
            mat_steel02=mat_steel02,
            mat_minmax=mat_minmax,
            mat_imk=mat_imk,
            materials_list=materials_list,
            frame_sections=frame_sections,
            sec_fiber=sec_fiber,
            sec_aggregator=sec_aggregator,
            sections_list=sections_list,
            slab_sections=slab_sections,
            storeys=storeys,
            nodes=nodes,
            restraints=restraints,
        )
    
    # SUPPORTING METHODS
    def _generate_nodes(self, point_objects):
        data = point_objects # Recall point_objects data
        point_idx = data["Index"]
        n = len(point_idx)
        index = np.arange(n, dtype=np.int32)
        nodes = Nodes(
            index = index,
            label = data["Unique Name"],
            coords = data["Coordinates"],
        )
        return nodes
        
    def _generate_beamcolumn_elements(self, nodes):
        data = self._modeldata.line_objects # Recall line_objects data
        data_pointobj = self._modeldata.point_objects # Recall point_objects data
        secs_list = self._modeldata.sections_list # Recall sections_list data
        element_type = np.fromiter((secs_list[sc].element_type[idx]
            for sc, idx in zip(data.sec_class, data.sec_idx)), dtype="U15")
        mask = (element_type == "Beam")
        #mask = (element_type == "Column") | (element_type == "Beam")
        n = len(data.index[mask])
        index = np.arange(n, dtype=np.int32)
        label = data.unique_name[mask]
        point_name = data_pointobj.unique_name
        end_points_idx = data.end_points_idx[mask]
        end_nodes_idx = retrieve_output_from_input(
            inputdata=end_points_idx,
            shared_data_in=point_name,
            outputdata=nodes.index, 
            shared_data_out=nodes.label,
        )
        return element_type
    
    def _translate_point_objects(self, project_information):
        sheet_name = "Point Objects"
        data = self._reader.read(sheet_name=sheet_name, start_row=7) # Reading Sheet "Point Objects" in the Input file
        self._validate_data(data=data, sheet_name=sheet_name, mandatory=True)
        n = len(data)
        index = np.arange(n, dtype=np.int32)
        unique_name = np.empty(n, dtype="U15")
        coords = np.empty((n, 3), dtype=np.float64)
        name_to_idx = {}
        for i, row in enumerate(data):
            name = str(row["Unique Name"])
            if name in name_to_idx:
                raise ValidationError(f"Duplicate Point object name '{name}'")
            name_to_idx[name] = index[i]
            unique_name[i] = name
            coords[i] = (
                self._to_internalunits.length(value=row["X"]),
                self._to_internalunits.length(value=row["Y"]),
                self._to_internalunits.length(value=row["Z"]),
            )
        point_objects = PointObjects(
            index = index,
            unique_name = unique_name,
            coords = coords,
            name_to_idx = name_to_idx,
        ) # Defining dataclass for each point object
        ndim = project_information.ndim # Retrieve number of dimensional space
        storey_elevations = np.unique(coords[:, 2]) if ndim == 3 else np.unique(coords[:, 1]) # Determine storey elevations
        storeys = self._generate_storeys(storey_elevations=storey_elevations) # Generating Storey data from storey elevations
        return point_objects, storeys

    def _translate_line_objects(self, point_objects, project_information):
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

    def _translate_surface_objects(self, line_objects, slab_sections):
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