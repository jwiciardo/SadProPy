import warnings
import numpy as np
from openpyxl import load_workbook
from .preprocessing_class_index import (
    MaterialType,
    MaterialModel,
    SectionShape,
    SectionModel,
    IntegrationType,
    ElementType,
    LoadCaseType,
)
from .material.concrete_class_index import ConcreteElastic, Concrete04, Concrete04MinMax
from .material.steel_class_index import SteelElastic, Steel02, Steel02MinMax
from .material.spring_class_index import SpringIMKBilinear, SpringIMKPeakOriented, SpringIMKPinching
from .section.rectangular_class_index import RectangularElastic, RectangularConcreteFiber
from .preprocessing_dataclass import (
    FilePathInformation,
    ProjectInformation,
    AnalysisPreferences,
    Materials,
    FrameSections,
    SlabSections,
    Storeys,
)
from ._surface import generate_surface_connectivity
from ._section import compute_section_properties
from ._load import (
    get_concentrated_line_loads,
    get_distributed_line_loads,
)
from ..utility import (
    ConverterToInternalUnits,
    UserDefinedUnits,
)
from ..utility import TagManager
from ..utility._exceptions import ValidationError
from ..utility._filepath import get_filepath

class ExcelReader:
    def __init__(self, inputfile_path):
        if not inputfile_path.exists():
            raise FileNotFoundError(f"File not found: {inputfile_path}")
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="Data Validation extension is not supported*")
            self._workbook = load_workbook(inputfile_path, data_only=True)
    
    # MAIN METHOD: EXCELREADER
    def read(self, sheet_name="", orientation="records", start_row=1):
        if sheet_name not in self._workbook.sheetnames:
            raise ValidationError(f"Sheet '{sheet_name}' not found in Excel file")
        worksheet = self._workbook[sheet_name]
        rows = list(worksheet.values)
        headers = list(rows[start_row - 1])
        while headers and headers[-1] is None:
            headers.pop()
        if orientation == "records":
            data = []
        elif orientation == "columns":
            data = {header: [] for header in headers}
        else:
            raise ValidationError("Orientation must be either 'records' or 'columns'")

        nrows = 0
        for row in rows[start_row:]:
            row = row[:len(headers)]
            if all(v is None for v in row): # Skip completely empty rows
                continue
            nrows += 1
            if orientation == "records":
                data.append(dict(zip(headers, row)))
            elif orientation == "columns":
                for header, value in zip(headers, row):
                    data[header].append(value)
        return data, nrows
    
    def read_preferences_sheet(self, sheet_name="", start_row=1, required_preferences=None):
        data, nrows = self.read(sheet_name=sheet_name, orientation="records", start_row=start_row)
        values = {row["Item"]: row["Value"] for row in data}

        if required_preferences is not None:
            for preference in required_preferences:
                value = values.get(preference)
                if value is None or str(value).strip() == "":
                    raise ValidationError(f"'{preference}' in sheet '{sheet_name}' cannot be empty")
        return values

class ExcelTranslator:
    def __init__(self, inputfile_path):
        # FILE PATH
        self._inputfile_path = inputfile_path
        self._parent_path, self._output_path, self._logfile_path = get_filepath(inputfile_path)

        # CORE
        self._reader = ExcelReader(inputfile_path=self._inputfile_path)
        self._units = self._translate_userdefined_units()
        self._to_internalunits = ConverterToInternalUnits(units=self._units)
        self._tagmanager = TagManager()
        
        # DICTIONARY
        self._material_type = {
            "Concrete": MaterialType.Concrete,
            "Rebar": MaterialType.Steel,
            "Steel": MaterialType.Steel,
            "Spring": MaterialType.Spring,
        }
        self._material_model = {
            "Elastic": MaterialModel.Elastic,
            "Concrete04": MaterialModel.Concrete04,
            "Concrete04+MinMax": MaterialModel.Concrete04MinMax,
            "Steel02": MaterialModel.Steel02,
            "Steel02+MinMax": MaterialModel.Steel02MinMax,
            "IMKBilinear": MaterialModel.IMKBilinear,
            "IMKPeakOriented": MaterialModel.IMKPeakOriented,
            "IMKPinching": MaterialModel.IMKPinching,
        }
        self._material_definition = {
            (MaterialType.Concrete, MaterialModel.Elastic): ConcreteElastic,
            (MaterialType.Concrete, MaterialModel.Concrete04): Concrete04,
            (MaterialType.Concrete, MaterialModel.Concrete04MinMax): Concrete04MinMax,
            (MaterialType.Steel, MaterialModel.Elastic): SteelElastic,
            (MaterialType.Steel, MaterialModel.Steel02): Steel02,
            (MaterialType.Steel, MaterialModel.Steel02MinMax): Steel02MinMax,
            (MaterialType.Spring, MaterialModel.IMKBilinear): SpringIMKBilinear,
            (MaterialType.Spring, MaterialModel.IMKPeakOriented): SpringIMKPeakOriented,
            (MaterialType.Spring, MaterialModel.IMKPinching): SpringIMKPinching,
        }
        self._section_shape = {
            "Rectangular": SectionShape.Rectangular,
            "Circular": SectionShape.Circular,
            "Wide Flange": SectionShape.WideFlange,
            "Channel": SectionShape.Channel,
            "Rectangular Hollow": SectionShape.RectangularHollow,
            "Circular Hollow": SectionShape.CircularHollow,
        }
        self._section_model = {
            "Elastic": SectionModel.Elastic,
            "Fiber": SectionModel.Fiber,
            "Aggregator": SectionModel.Aggregator,
        }
        self._section_definition = {
            (MaterialType.Concrete, SectionShape.Rectangular, SectionModel.Elastic): RectangularElastic,
            (MaterialType.Steel, SectionShape.Rectangular, SectionModel.Elastic): RectangularElastic,
            (MaterialType.Concrete, SectionShape.Rectangular, SectionModel.Fiber): RectangularConcreteFiber,
        }
        self._integration_type = {
            "Lobatto": IntegrationType.Lobatto,
            "Hinge Radau": IntegrationType.HingeRadau,
        }
        self._element_type = {
            "Column": ElementType.Column,
            "Beam": ElementType.Beam,
            "Slab": ElementType.Slab,
            "Brace": ElementType.Brace,
            "Zero Length": ElementType.ZeroLength,
        }
        self._loadcase_type = {
            "Selfweight": LoadCaseType.SW,
            "Dead": LoadCaseType.D,
            "Live": LoadCaseType.L,
            "Live Roof": LoadCaseType.Lr,
            "Earthquake-X": LoadCaseType.Ex,
            "Earthquake-Y": LoadCaseType.Ey,
            "Wind-X": LoadCaseType.Wx,
            "Wind-Y": LoadCaseType.Wy,
        }

    # MAIN METHOD: EXCEL TRANSLATOR
    def translate(self):
        filepath_information = self._translate_filepath_information()
        project_information = self._translate_project_information()
        analysis_preferences = self._translate_analysis_preferences()
        materials = self._translate_materials()
        frame_sections = self._translate_frame_sections(materials=materials)
        slab_sections = self._translate_slab_sections(materials=materials)
        point_objects, storeys = self._translate_point_objects(project_information=project_information)
        line_objects = self._translate_line_objects(point_objects=point_objects, sections=frame_sections)
        surface_objects = self._translate_surface_objects(
            line_objects=line_objects,
            slab_sections=slab_sections,
        )
        restraints = self._translate_restraints(point_objects=point_objects)
        point_loads = self._translate_point_loads()
        concentrated_line_loads = self._translate_concentrated_line_loads()
        distributed_line_loads = self._translate_distributed_line_loads()
        surface_loads = self._translate_surface_loads()
        return {
            "Filepath Information": filepath_information,
            "Project Information": project_information,
            "Userdefined Units": self._units,
            "Analysis Preferences": analysis_preferences,
            "Materials": materials,
            "Frame Sections": frame_sections,
            "Slab Sections": slab_sections,
            "Storeys": storeys,
            "Point Objects": point_objects,
            "Line Objects": line_objects,
            "Surface Objects": surface_objects,
            "Restraints": restraints,
            "Point Loads": point_loads,
            "Concentrated Line Loads": concentrated_line_loads,
            "Distributed Line Loads": distributed_line_loads,
            "Surface Loads": surface_loads,
        }

    # HELPER METHOD
    def _validate_data(self, nrows, sheet_name, mandatory=True):
        if nrows > 0: # Set condition if number of rows in data > 0 then return True
            return True
        if mandatory: # Set condition if mandatory is True then raise validation error (This condition will be run when number of rows in data = 0)
            raise ValidationError(f"Sheet '{sheet_name}' is mandatory but contains no data.")
        return False

    def _validate_duplicate_value(self, col_data, col_name=""):
        unique_names, counts = np.unique(col_data, return_counts=True)
        duplicates = unique_names[counts > 1]
        if duplicates.size > 0:
            raise ValidationError(f"Duplicate {col_name}(s): {', '.join(duplicates)}")
    
    def _generate_storeys(self, storey_elevations):
        storeys = {} # Predefined storeys dictionary
        for idx, elev in reversed(list(enumerate(storey_elevations))): # Loop over storey elevations
            if idx == 0: # Set condition if index == 0
                storey_name = "Base" # If True define storey name as "Base" and height = 0.0
                height = np.float64(0.0) 
            else:
                storey_name = f"Storey{idx}" # If False define storey name as "Storey{index}" and storey height
                height = elev - storey_elevations[idx - 1]
            storeys[storey_name] = Storeys(
                name=storey_name,
                height=height,
                elevation=elev,
            ) # Store storeys data as dataclass
        return storeys

    # SUPPORTING METHODS
    def _translate_filepath_information(self):
        filepath_information = FilePathInformation(
            parent_path = self._parent_path,
            output_path = self._output_path,
            inputfile_path = self._inputfile_path,
            logfile_path = self._logfile_path
        ) # Storing filepath information to dataclass
        return filepath_information

    def _translate_project_information(self):
        values = self._reader.read_preferences_sheet(
            sheet_name="Project Information",
            start_row=6,
            required_preferences=["Model Dimensional Space"],
        ) # Reading Sheet "Project Information" in the Input file
        project_information = ProjectInformation(
            name = str(values["Project Name"]),
            desc = str(values["Project Description"]),
            ndim = int(3 if str(values["Model Dimensional Space"]) == "3D-Space" else 2),
        ) # Storing project information to dataclass
        return project_information
    
    def _translate_userdefined_units(self):
        values = self._reader.read_preferences_sheet(
            sheet_name="User Defined Units",
            start_row=9,
            required_preferences=[
                "Force",
                "Length",
                "Mass",
                "Stress",
                "Time",
                "Angle",
            ],
        ) # Reading Sheet "User Defined Units" in the Input file
        userdefined_units = UserDefinedUnits(
            force = str(values["Force"]),
            length = str(values["Length"]),
            mass = str(values["Mass"]),
            stress = str(values["Stress"]),
            time = str(values["Time"]),
            angle = str(values["Angle"]),
        ) # Storing units to dataclass
        return userdefined_units

    def _translate_analysis_preferences(self):
        values = self._reader.read_preferences_sheet(
            sheet_name="Analysis Preferences",
            start_row=6,
            required_preferences=[
                "Nonlinear Analysis",
                "P-Delta",
                "LL Mass Factor",
            ],
        ) # Reading Sheet "Analysis Preferences" in the Input file
        analysis_preferences = AnalysisPreferences(
            is_nonlinear_analysis = str(values["Nonlinear Analysis"]).strip().lower() == "yes",
            is_pdelta = str(values["P-Delta"]).strip().lower() == "yes",
            liveload_mass_factor = float(values["LL Mass Factor"]),
        ) # Storing analysis preferences to dataclass
        return analysis_preferences

    def _translate_materials(self):
        sheet_name = "Materials"
        data, n = self._reader.read(
            sheet_name=sheet_name, 
            orientation="columns", 
            start_row=32,
        ) # Reading Sheet "Materials" in the Input file
        self._validate_data(nrows=n, sheet_name=sheet_name, mandatory=True)
        index = np.arange(n, dtype=np.int32)
        mat_name = np.asarray(data["Material Name"], dtype="U32")
        self._validate_duplicate_value(col_data=mat_name, col_name="Material Name")
        mat_tag = np.asarray(self._tagmanager.add(category="Material", n=n, names=mat_name), dtype=np.int32)
        mat_type = np.asarray([self._material_type[value.strip().title()] for value in data["Material Type"]], dtype=np.int8)
        mat_model = np.asarray([self._material_model[value.strip()] for value in data["Material Model"]], dtype=np.int8)

        # Translate material properties
        mat_def = [self._material_definition[(mtype, model)] for mtype, model in zip(mat_type, mat_model)]
        max_columns = max(definition.properties.Count for definition in mat_def)
        properties = np.full((n, max_columns), np.nan, dtype=np.float64)
        unique_definitions = list(dict.fromkeys(mat_def))
        for definition in unique_definitions:
            mask = np.asarray([d is definition for d in mat_def], dtype=bool)
            selected_data = {key: np.asarray(value)[mask] for key, value in data.items()}
            translated_props = definition.translate(selected_data, self._to_internalunits)
            properties[mask, :definition.properties.Count] = translated_props
        materials = Materials(
            index = index,
            mat_name = mat_name,
            mat_tag = mat_tag,
            mat_type = mat_type,
            mat_model = mat_model,
            mat_def = mat_def,
            properties = properties,
        ) # Storing materials data to dataclass
        return materials
    
    def _translate_frame_sections(self, materials):
        sheet_name = "Frame Sections"
        data, n = self._reader.read(
            sheet_name=sheet_name, 
            orientation="columns", 
            start_row=19,
        ) # Reading Sheet "Frame Sections" in the Input file
        self._validate_data(nrows=n, sheet_name=sheet_name, mandatory=True)
        index = np.arange(n, dtype=np.int32)
        sec_name = np.asarray(data["Section Name"], dtype="U32")
        self._validate_duplicate_value(col_data=sec_name, col_name="Section Name")
        sec_tag = np.asarray(self._tagmanager.add(category="Section", n=n, names=sec_name), dtype=np.int32)
        sec_shape = np.asarray([self._section_shape[value.strip().title()] for value in data["Section Shape"]], dtype=np.int8)
        sec_model = np.asarray([self._section_model[value.strip().title()] for value in data["Section Model"]], dtype=np.int8)
        mat_columns = ["Material", "Material2", "Material3", "Material4", "Material5", "Material6"]
        mats_idx = np.column_stack([
            materials.name_to_idx(data[column]) for column in mat_columns
        ])
        mat_type = np.empty(n, dtype=np.int8)
        for i in range(n):
            if mats_idx[i, 0] >= 0:
                j = 0
            elif mats_idx[i, 1] >= 0:
                j = 1
            elif mats_idx[i, 2] >= 0:
                j = 2
            elif mats_idx[i, 3] >= 0:
                j = 3
            elif mats_idx[i, 4] >= 0:
                j = 4
            elif mats_idx[i, 5] >= 0:
                j = 5
            else:
                continue
            mat_type[i] = materials.mat_type[mats_idx[i, j]]
        integration_type = np.asarray([
            self._integration_type[value.strip().title()]
            if value is not None and value.strip() else -1
            for value in data["Integration Type"]],
            dtype=np.int8
        )
        mask = integration_type != -1
        integration_tag = np.full(n, -1, dtype=np.int32)
        if np.any(mask):
            integration_tag[mask] = np.asarray(self._tagmanager.add(category="Beam Integration", n=np.count_nonzero(mask), names=sec_name[mask]), dtype=np.int32)  
        section_lookup = dict(zip(sec_name, index))
        aggregated_sec_idx = np.asarray([section_lookup[name]
            if name is not None and str(name).strip() else -1
            for name in data["Aggregated Section"]],
            dtype=np.int32
        )

        # Translate section dimensions
        aggregator_mask = sec_model == SectionModel.Aggregator
        normal_mask = ~aggregator_mask
        sec_def = np.empty(n, dtype=object)
        for i in np.flatnonzero(normal_mask):
            sec_def[i] = self._section_definition[
                (mat_type[i], sec_shape[i], sec_model[i])
            ]
        for i in np.flatnonzero(aggregator_mask):
            sec_def[i] = None
        max_columns = max(definition.dimensions.Count for definition in sec_def[normal_mask])
        dimensions = np.full((n, max_columns), np.nan, dtype=np.float64)
        unique_definitions = list(dict.fromkeys(sec_def[normal_mask]))
        for definition in unique_definitions:
            mask = np.asarray([normal_mask[i] and sec_def[i] is definition for i in range(n)], dtype=bool)
            selected_data = {key: np.asarray(value)[mask] for key, value in data.items()}
            translated_dims = definition.translate(selected_data, self._to_internalunits)
            dimensions[mask, :definition.dimensions.Count] = translated_dims

        # Compute section properties
        AMod = np.asarray(data["AMod"], dtype=np.float64)
        AvyMod = np.asarray(data["AvyMod"], dtype=np.float64)
        AvzMod = np.asarray(data["AvzMod"], dtype=np.float64)
        IzMod = np.asarray(data["IzMod"], dtype=np.float64)
        IyMod = np.asarray(data["IyMod"], dtype=np.float64)
        JxxMod = np.asarray(data["JxxMod"], dtype=np.float64)
        normal_sec_props = compute_section_properties(
            section_definitions=sec_def[normal_mask],
            dimensions=dimensions[normal_mask],
        )
        A = np.full(n, np.nan)
        Avy = np.full(n, np.nan)
        Avz = np.full(n, np.nan)
        Iz = np.full(n, np.nan)
        Iy = np.full(n, np.nan)
        Jxx = np.full(n, np.nan)
        alphaY = np.full(n, np.nan)
        alphaZ = np.full(n, np.nan)
        Abar_hoop = np.full(n, np.nan)
        Abar_top = np.full(n, np.nan)
        Abar_bot = np.full(n, np.nan)
        Abar_int = np.full(n, np.nan)
        (
            A[normal_mask],
            Avy[normal_mask],
            Avz[normal_mask],
            Iz[normal_mask],
            Iy[normal_mask],
            Jxx[normal_mask],
            alphaY[normal_mask],
            alphaZ[normal_mask],
            Abar_hoop[normal_mask],
            Abar_top[normal_mask],
            Abar_bot[normal_mask],
            Abar_int[normal_mask],
        ) = normal_sec_props
        properties = np.column_stack((
            AMod * A,
            AvyMod * Avy,
            AvzMod * Avz,
            IzMod * Iz,
            IyMod * Iy,
            JxxMod * Jxx,
            alphaY,
            alphaZ,
            Abar_hoop,
            Abar_top,
            Abar_bot,
            Abar_int,
        ))
        frame_sections = FrameSections(
            index = index,
            sec_name = sec_name,
            sec_tag = sec_tag,
            sec_shape = sec_shape,
            sec_model = sec_model,
            sec_def = sec_def,
            mats_idx = mats_idx,
            mat_type = mat_type,
            integration_type = integration_type,
            integration_tag = integration_tag,
            aggregated_sec_idx=aggregated_sec_idx,
            dimensions=dimensions,
            properties = properties,
        ) # Storing sections data to dataclass
        return frame_sections

    def _translate_slab_sections(self, materials):
        sheet_name = "Slab Sections"
        data, n = self._reader.read(
            sheet_name=sheet_name, 
            orientation="columns", 
            start_row=6,
        ) # Reading Sheet "Slab Sections" in the Input file
        if not self._validate_data(nrows=n, sheet_name=sheet_name, mandatory=False):
            slab_sections = SlabSections.empty()
            return slab_sections
        index = np.arange(n, dtype=np.int32)
        sec_name = np.asarray(data["Section Name"], dtype="U32")
        self._validate_duplicate_value(col_data=sec_name, col_name="Section Name")
        mat_columns = ["Material"]
        mats_idx = np.column_stack([
            materials.name_to_idx(data[column]) for column in mat_columns
        ])
        mat_type = np.empty(n, dtype=np.int8)
        for i in range(n):
            if mats_idx[i, 0] >= 0:
                j = 0
            else:
                continue
            mat_type[i] = materials.mat_type[mats_idx[i, j]]
        t = self._to_internalunits.length(values=data["t"])
        dimensions = np.column_stack((
            t,
        ))
        slab_sections = SlabSections(
            index = index,
            sec_name = sec_name,
            mats_idx = mats_idx,
            mat_type=mat_type,
            dimensions = dimensions,
        ) # Storing slab sections data to dataclass
        return slab_sections
    
    def _translate_point_objects(self, project_information):
        sheet_name = "Point Objects"
        data, n = self._reader.read(
            sheet_name=sheet_name, 
            orientation="columns", 
            start_row=7,
        ) # Reading Sheet "Point Objects" in the Input file
        self._validate_data(nrows=n, sheet_name=sheet_name, mandatory=True)
        index = np.arange(n, dtype=np.int32)
        unique_name = np.asarray(data["Unique Name"], dtype="U15")
        self._validate_duplicate_value(col_data=unique_name, col_name="Point object")
        coord_X = self._to_internalunits.length(values=data["X"])
        coord_Y = self._to_internalunits.length(values=data["Y"])
        coord_Z = self._to_internalunits.length(values=data["Z"])
        coords = np.column_stack((
            coord_X,
            coord_Y,
            coord_Z,
        ))
        name_to_idx = dict(zip(unique_name, index))
        point_objects = {
            "Index": index,
            "Unique Name": unique_name,
            "Coordinates": coords,
            "Name to Index": name_to_idx,
        } # Storing point object data to dictionary
        ndim = project_information.ndim # Retrieve number of dimensional space
        storey_elevations = np.unique(coords[:, 2]) if ndim == 3 else np.unique(coords[:, 1]) # Determine storey elevations
        storeys = self._generate_storeys(storey_elevations=storey_elevations) # Generating Storey data from storey elevations
        return point_objects, storeys

    def _translate_line_objects(self, point_objects, sections):
        sheet_name = "Line Objects"
        data, n = self._reader.read(
            sheet_name=sheet_name, 
            orientation="columns", 
            start_row=15,
        ) # Reading Sheet "Line Objects" in the Input file
        self._validate_data(nrows=n, sheet_name=sheet_name, mandatory=True)
        index = np.arange(n, dtype=np.int32)
        unique_name = np.asarray(data["Unique Name"], dtype="U15")
        self._validate_duplicate_value(col_data=unique_name, col_name="Line object")
        iend_point = np.asarray(data["I-End"], dtype="U15")
        jend_point = np.asarray(data["J-End"], dtype="U15")
        point_name_to_idx = point_objects["Name to Index"]
        end_points_idx = np.column_stack((
            np.fromiter((point_name_to_idx[name] for name in iend_point), dtype=np.int32, count=n),
            np.fromiter((point_name_to_idx[name] for name in jend_point), dtype=np.int32, count=n),
        ))
        element_type = np.asarray([self._element_type[value.strip().title()] for value in data["Element Type"]], dtype=np.int8)
        sec_idx = sections.name_to_idx(data["Section"])
        is_auto_end_offsets = np.fromiter((
            str(x).strip().lower() == "auto from connectivity"
            for x in data["End Offset"]),
            dtype=bool,
            count=n,
        )
        rigid_zone_factor = np.asarray(data["Rigid Zone Factor"], dtype=np.float64)
        iend_offset_length = np.where(
            [x is not None for x in data["I-End Offset Length"]],
            self._to_internalunits.length(values=data["I-End Offset Length"]), 
            0.0,
        )
        jend_offset_length = np.where(
            [x is not None for x in data["J-End Offset Length"]],
            self._to_internalunits.length(values=data["J-End Offset Length"]), 
            0.0,
        )
        offsets_length = np.column_stack((
            iend_offset_length,
            jend_offset_length,
        ))
        is_zero_length_element = np.fromiter((
            str(x).strip().lower() == "yes"
            for x in data["Zero Length Element"]),
            dtype=bool,
            count=n,
        )
        name_to_idx = dict(zip(unique_name, index))
        line_objects = {
            "Index": index,
            "Unique Name": unique_name,
            "End Points Index": end_points_idx,
            "Element Type": element_type,
            "Section Index": sec_idx,
            "Is Auto End Offsets": is_auto_end_offsets,
            "Rigid Zone Factor": rigid_zone_factor,
            "Offsets Length": offsets_length,
            "Is Zero Length Element": is_zero_length_element,
            "Name to Index": name_to_idx,
        } # Storing line objects data to dictionary
        return line_objects

    def _translate_surface_objects(self, line_objects, slab_sections):
        sheet_name = "Surface Objects"
        data, n = self._reader.read(
            sheet_name=sheet_name, 
            orientation="columns", 
            start_row=10,
        ) # Reading Sheet "Surface Objects" in the Input file
        self._validate_data(nrows=n, sheet_name=sheet_name, mandatory=True)
        index = np.arange(n, dtype=np.int32)
        unique_name = np.asarray(data["Unique Name"], dtype="U15")
        self._validate_duplicate_value(col_data=unique_name, col_name="Surface object")
        edge_1 = np.asarray(data["Edge 1"], dtype="U15")
        edge_2 = np.asarray(data["Edge 2"], dtype="U15")
        edge_3 = np.asarray(data["Edge 3"], dtype="U15")
        edge_4 = np.asarray(data["Edge 4"], dtype="U15")
        edges_name = np.column_stack((
            edge_1,
            edge_2,
            edge_3,
            edge_4,
        ))
        edges_idx = np.empty((n, 4), dtype=np.int32)
        vertices_idx = np.empty((n, 4), dtype=np.int32)
        for i in range(n):
            edges_idx[i], vertices_idx[i] = generate_surface_connectivity(
                edges_name=edges_name[i],
                line_objects=line_objects,
                surface_name=unique_name[i],
            )
        element_type = np.asarray([self._element_type[value.strip().title()] for value in data["Element Type"]], dtype=np.int8)
        sec_idx = slab_sections.name_to_idx(data["Section"])
        name_to_idx = dict(zip(unique_name, index))
        surface_objects = {
            "Index": index,
            "Unique Name": unique_name,
            "Edges Index": edges_idx,
            "Vertices Index": vertices_idx,
            "Element Type": element_type,
            "Section Index": sec_idx,
            "Name to Index": name_to_idx,
        } # Storing surface objects data to dictionary
        return surface_objects
    
    def _translate_restraints(self, point_objects):
        sheet_name="Restraints"
        data, n = self._reader.read(
            sheet_name=sheet_name, 
            orientation="columns", 
            start_row=10,
        ) # Reading Sheet "Restraints" in the Input file
        self._validate_data(nrows=n, sheet_name=sheet_name, mandatory=True)
        point_name_to_idx = point_objects["Name to Index"]
        point_name = np.asarray(data["Point"], dtype="U15")
        point_idx = np.fromiter((point_name_to_idx[name] for name in point_name), dtype=np.int32, count=n)
        ux = np.asarray(data["UX"], dtype=np.int32)
        uy = np.asarray(data["UY"], dtype=np.int32)
        uz = np.asarray(data["UZ"], dtype=np.int32)
        rx = np.asarray(data["RX"], dtype=np.int32)
        ry = np.asarray(data["RY"], dtype=np.int32)
        rz = np.asarray(data["RZ"], dtype=np.int32)
        dofs = np.column_stack((
            ux,
            uy,
            uz,
            rx,
            ry,
            rz,
        ))
        restraints = {
            "Point Index": point_idx,
            "DOFs": dofs,
        } # Storing restraints data to dictionary
        return restraints

    def _translate_point_loads(self):
        sheet_name="Point Loads"
        data, n = self._reader.read(
            sheet_name=sheet_name, 
            orientation="columns", 
            start_row=11,
        ) # Reading Sheet "Point Loads" in the Input file
        if not self._validate_data(nrows=n, sheet_name=sheet_name, mandatory=False):
            point_loads = []
            return point_loads
        point_name = np.asarray(data["Point"], dtype="U15")
        loadcase_type = np.asarray([self._loadcase_type[value.strip().title()] for value in data["Load Case"]], dtype=np.int8)
        fx = np.where(
            [x is not None for x in data["FX"]],
            self._to_internalunits.force_pointload(values=data["FX"]), 
            0.0,
        )
        fy = np.where(
            [x is not None for x in data["FY"]],
            self._to_internalunits.force_pointload(values=data["FY"]), 
            0.0,
        )
        fz = np.where(
            [x is not None for x in data["FZ"]],
            self._to_internalunits.force_pointload(values=data["FZ"]), 
            0.0,
        )
        mx = np.where(
            [x is not None for x in data["MX"]],
            self._to_internalunits.moment_pointload(values=data["MX"]), 
            0.0,
        )
        my = np.where(
            [x is not None for x in data["MY"]],
            self._to_internalunits.moment_pointload(values=data["MY"]), 
            0.0,
        )
        mz = np.where(
            [x is not None for x in data["MZ"]],
            self._to_internalunits.moment_pointload(values=data["MZ"]), 
            0.0,
        )
        loads = np.column_stack((
            fx,
            fy,
            fz,
            mx,
            my,
            mz,
        ))
        point_loads = {
            "Point Name": point_name,
            "Load Case": loadcase_type,
            "Loads": loads,
        } # Storing Point Loads data to dictionary
        return point_loads

    def _translate_concentrated_line_loads(self):
        sheet_name="Concentrated Line Loads"
        data, n = self._reader.read(
            sheet_name=sheet_name, 
            orientation="columns", 
            start_row=14,
        ) # Reading Sheet "Concentrated Line Loads" in the Input file
        if not self._validate_data(nrows=n, sheet_name=sheet_name, mandatory=False):
            concentrated_line_loads = []
            return concentrated_line_loads
        line_name = np.asarray(data["Line"], dtype="U15")
        loadcase_type = np.asarray([self._loadcase_type[value.strip().title()] for value in data["Load Case"]], dtype=np.int8)
        load_direction = np.asarray(data["Direction"], dtype="U15")
        load_1 = np.where(
            [x is not None for x in data["Load 1"]],
            self._to_internalunits.concentrated_lineload(values=data["Load 1"]), 
            np.nan,
        )
        load_2 = np.where(
            [x is not None for x in data["Load 2"]],
            self._to_internalunits.concentrated_lineload(values=data["Load 2"]), 
            np.nan,
        )
        load_3 = np.where(
            [x is not None for x in data["Load 3"]],
            self._to_internalunits.concentrated_lineload(values=data["Load 3"]), 
            np.nan,
        )
        load_4 = np.where(
            [x is not None for x in data["Load 4"]],
            self._to_internalunits.concentrated_lineload(values=data["Load 4"]), 
            np.nan,
        )
        loads = np.column_stack((
            load_1,
            load_2,
            load_3,
            load_4,
        ))
        loc_1 = np.where(
            [x is not None for x in data["Location 1"]],
            self._to_internalunits.length(values=data["Location 1"]), 
            np.nan,
        )
        loc_2 = np.where(
            [x is not None for x in data["Location 2"]],
            self._to_internalunits.length(values=data["Location 2"]), 
            np.nan,
        )
        loc_3 = np.where(
            [x is not None for x in data["Location 3"]],
            self._to_internalunits.length(values=data["Location 3"]), 
            np.nan,
        )
        loc_4 = np.where(
            [x is not None for x in data["Location 4"]],
            self._to_internalunits.length(values=data["Location 4"]), 
            np.nan,
        )
        locations = np.column_stack((
            loc_1,
            loc_2,
            loc_3,
            loc_4,
        ))
        new_line_name, new_loadcase_type, new_load_direction, new_location, new_load = get_concentrated_line_loads(
            line_name=line_name,
            loadcase_type=loadcase_type,
            load_direction=load_direction,
            locations=locations,
            loads=loads,
        )
        concentrated_line_loads = {
            "Line Name": new_line_name,
            "Load Case": new_loadcase_type,
            "Direction": new_load_direction,
            "Location": new_location,
            "Load": new_load,
        } # Storing Concentrated Line Loads data to dictionary
        return concentrated_line_loads

    def _translate_distributed_line_loads(self):
        sheet_name="Distributed Line Loads"
        data, n = self._reader.read(
            sheet_name=sheet_name, 
            orientation="columns", 
            start_row=15,
        ) # Reading Sheet "Distributed Line Loads" in the Input file
        if not self._validate_data(nrows=n, sheet_name=sheet_name, mandatory=False):
            distributed_line_loads = []
            return distributed_line_loads
        line_name = np.asarray(data["Line"], dtype="U15")
        loadcase_type = np.asarray([self._loadcase_type[value.strip().title()] for value in data["Load Case"]], dtype=np.int8)
        load_direction = np.asarray(data["Direction"], dtype="U15")
        uniform_load = np.where(
            [x is not None for x in data["Uniform Load"]],
            self._to_internalunits.distributed_lineload(values=data["Uniform Load"]), 
            np.nan,
        )
        load_1 = np.where(
            [x is not None for x in data["Load 1"]],
            self._to_internalunits.distributed_lineload(values=data["Load 1"]), 
            np.nan,
        )
        load_2 = np.where(
            [x is not None for x in data["Load 2"]],
            self._to_internalunits.distributed_lineload(values=data["Load 2"]), 
            np.nan,
        )
        load_3 = np.where(
            [x is not None for x in data["Load 3"]],
            self._to_internalunits.distributed_lineload(values=data["Load 3"]), 
            np.nan,
        )
        load_4 = np.where(
            [x is not None for x in data["Load 4"]],
            self._to_internalunits.distributed_lineload(values=data["Load 4"]), 
            np.nan,
        )
        loads = np.column_stack((
            load_1,
            load_2,
            load_3,
            load_4,
        ))
        loc_1 = np.where(
            [x is not None for x in data["Location 1"]],
            self._to_internalunits.length(values=data["Location 1"]), 
            np.nan,
        )
        loc_2 = np.where(
            [x is not None for x in data["Location 2"]],
            self._to_internalunits.length(values=data["Location 2"]), 
            np.nan,
        )
        loc_3 = np.where(
            [x is not None for x in data["Location 3"]],
            self._to_internalunits.length(values=data["Location 3"]), 
            np.nan,
        )
        loc_4 = np.where(
            [x is not None for x in data["Location 4"]],
            self._to_internalunits.length(values=data["Location 4"]), 
            np.nan,
        )
        locations = np.column_stack((
            loc_1,
            loc_2,
            loc_3,
            loc_4,
        ))
        new_line_name, new_loadcase_type, new_load_direction, new_location, new_load = get_distributed_line_loads(
            line_name=line_name,
            loadcase_type=loadcase_type,
            load_direction=load_direction,
            locations=locations,
            uniform_load=uniform_load,
            loads=loads,
        )
        distributed_line_loads = {
            "Line Name": new_line_name,
            "Load Case": new_loadcase_type,
            "Direction": new_load_direction,
            "Load": new_load,
            "Location": new_location,
        } # Storing Distributed Line Loads data to dictionary
        return distributed_line_loads

    def _translate_surface_loads(self):
        sheet_name="Surface Loads"
        data, n = self._reader.read(
            sheet_name=sheet_name, 
            orientation="columns", 
            start_row=7,
        ) # Reading Sheet "Surface Loads" in the Input file
        if not self._validate_data(nrows=n, sheet_name=sheet_name, mandatory=False):
            surface_loads = []
            return surface_loads
        surface_name = np.asarray(data["Surface"], dtype="U15")
        loadcase_type = np.asarray([self._loadcase_type[value.strip().title()] for value in data["Load Case"]], dtype=np.int8)
        load_direction = np.asarray(data["Direction"], dtype="U15")
        load = np.where(
            [x is not None for x in data["Load"]],
            self._to_internalunits.surfaceload(values=data["Load"]), 
            0.0,
        )
        surface_loads = {
            "Surface Name": surface_name,
            "Load Case": loadcase_type,
            "Direction": load_direction,
            "Load": load,
        } # Storing Surface Loads data to dictionary
        return surface_loads