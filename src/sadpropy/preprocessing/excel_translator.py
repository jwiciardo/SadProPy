import warnings
import numpy as np
from openpyxl import load_workbook
from .preprocessing_dataclass import (
    FilePathInformation,
    ProjectInformation,
    AnalysisPreferences,
    Materials,
    Mat_Concrete04,
    Mat_Steel02,
    Mat_MinMax,
    Mat_IMK,
    FrameSections,
    Sec_Fiber,
    Sec_Aggregator,
    SlabSections,
    Storeys,
)
from ._surface import generate_surface_connectivity
from ._material import get_material_properties
from ._section import (
    compute_section_properties,
    compute_fibersection_properties,
    get_section_properties,
)
from ._load import (
    get_concentrated_line_loads,
    get_distributed_line_loads,
)
from sadpropy.utility import (
    ConverterToInternalUnits,
    UserDefinedUnits,
)
from sadpropy.utility import TagManager
from sadpropy.utility._exceptions import ValidationError
from sadpropy.utility._filepath import get_filepath

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
        
        # DICTIONARY LIST
        self._mats_list = []
        self._hinge_mats_list = []
        self._secs_list = []

    # MAIN METHOD: EXCEL TRANSLATOR
    def translate(self):
        filepath_information = self._translate_filepath_information()
        project_information = self._translate_project_information()
        analysis_preferences = self._translate_analysis_preferences()
        materials = self._translate_materials()
        mat_concrete04 = self._translate_mat_concrete04()
        mat_steel02 = self._translate_mat_steel02()
        mat_minmax = self._translate_mat_minmax()
        mat_imk = self._translate_mat_imk()
        frame_sections = self._translate_frame_sections()
        sec_fiber = self._translate_sec_fiber()
        sec_aggregator = self._translate_sec_aggregator()
        slab_sections = self._translate_slab_sections()
        point_objects, storeys = self._translate_point_objects(project_information=project_information)
        line_objects = self._translate_line_objects(point_objects=point_objects)
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
            "Mat: Concrete04": mat_concrete04,
            "Mat: Steel02": mat_steel02,
            "Mat: Minmax": mat_minmax,
            "Mat: IMK": mat_imk,
            "Materials List": self._mats_list,
            "Frame Sections": frame_sections,
            "Sec: Fiber": sec_fiber,
            "Sec: Aggregator": sec_aggregator,
            "Sections List": self._secs_list,
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

    def _retrieve_material_index(self, mats_name):
        if isinstance(mats_name, str): # Set condition if materials name is a string return list of materials name
            mats_name = [mats_name]
        mat_class = np.empty(len(mats_name), dtype=np.int32) # Predefined material class array
        mat_idx = np.empty(len(mats_name), dtype=np.int32) # Predefined material index array 
        mat = [] # Predefined materials dataclass list
        for i, mat_name in enumerate(mats_name): # Loop over materials name
            found = False # Predefined found material in materials list
            for cls, material in enumerate(self._mats_list): # Loop over materials list
                idx = material.name_to_idx.get(mat_name) # Retrieve material index
                if idx is not None: # Set condition if material index is not None
                    mat_class[i] = cls # Return material class, material index, and materials dataclass for index i
                    mat_idx[i] = idx
                    mat.append(material)
                    found = True # Set found to be True
                    break
            if not found: # Set condition if found is False return validation error
                raise ValidationError(f"Material '{mat_name}' not found")
        return mat_class, mat, mat_idx

    def _retrieve_section_index(self, secs_name):
        if isinstance(secs_name, str): # Set condition if sections name is a string return list of sections name
            secs_name = [secs_name]
        sec_class = np.empty(len(secs_name), dtype=np.int32) # Predefined section class array
        sec_idx = np.empty(len(secs_name), dtype=np.int32) # Predefined section index array 
        sec = [] # Predefined sections dataclass list
        for i, sec_name in enumerate(secs_name): # Loop over sections name
            found = False # Predefined found section in sections list
            for cls, section in enumerate(self._secs_list): # Loop over sections list
                idx = section.name_to_idx.get(sec_name) # Retrieve section index
                if idx is not None: # Set condition if section index is not None
                    sec_class[i] = cls # Return section class, section index, and sections dataclass for index i
                    sec_idx[i] = idx
                    sec.append(section)
                    found = True # Set found to be True
                    break
            if not found: # Set condition if found is False return validation error
                raise ValidationError(f"Section '{sec_name}' not found")
        return sec_class, sec, sec_idx
    
    def _retrieve_slabsection_index(self, secs_name, secs_list): # Retrieve slab section 
        if isinstance(secs_name, str): # Set condition if sections name is a string return list of sections name
            secs_name = [secs_name]
        sec_class = np.empty(len(secs_name), dtype=np.int32) # Predefined section class array
        sec_idx = np.empty(len(secs_name), dtype=np.int32) # Predefined section index array 
        sec = [] # Predefined sections dataclass list
        for i, sec_name in enumerate(secs_name): # Loop over sections name
            found = False # Predefined found section in sections list
            for cls, section in enumerate(secs_list): # Loop over sections list
                idx = section.name_to_idx.get(sec_name) # Retrieve section index
                if idx is not None: # Set condition if section index is not None
                    sec_class[i] = cls # Return section class, section index, and sections dataclass for index i
                    sec_idx[i] = idx
                    sec.append(section)
                    found = True # Set found to be True
                    break
            if not found: # Set condition if found is False return validation error
                raise ValidationError(f"Section '{sec_name}' not found")
        return sec_class, sec, sec_idx
        
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
            is_nonlinear_analysis = str(values["Nonlinear Analysis"]),
            is_pdelta = str(values["P-Delta"]),
            liveload_mass_factor = float(values["LL Mass Factor"]),
        ) # Storing analysis preferences to dataclass
        return analysis_preferences

    def _translate_materials(self):
        sheet_name = "Materials"
        data, n = self._reader.read(
            sheet_name=sheet_name, 
            orientation="columns", 
            start_row=13,
        ) # Reading Sheet "Materials" in the Input file
        self._validate_data(nrows=n, sheet_name=sheet_name, mandatory=True)
        index = np.arange(n, dtype=np.int32)
        mat_name = np.asarray(data["Material Name"], dtype="U32")
        self._validate_duplicate_value(col_data=mat_name, col_name="Material Name")
        mat_tag = np.asarray(self._tagmanager.add(category="Material", n=n, names=mat_name), dtype=np.int32)
        mat_type = np.asarray(data["Material Type"], dtype="U15")
        E = self._to_internalunits.stress(values=data["E"])
        nu = np.asarray(data["nu"], dtype=np.float64)
        G = E / (2.0 * (1.0 + nu))
        Unitweight = self._to_internalunits.unitweight(values=data["Unitweight"])
        fc = np.where(
            mat_type == "Concrete", 
            self._to_internalunits.stress(values=data["fc"]), 
            0.0,
        )
        fyfu_mask = np.isin(mat_type, ["Rebar", "Steel"])
        fy = np.where(
            fyfu_mask,
            self._to_internalunits.stress(values=data["fy"]), 
            0.0,
        )
        fu = np.where(
            fyfu_mask,
            self._to_internalunits.stress(values=data["fu"]), 
            0.0,
        )
        properties = np.column_stack((
            Unitweight,
            E,
            nu,
            G,
            fc,
            fy,
            fu,
        ))
        name_to_idx = dict(zip(mat_name, index))
        materials = Materials(
            index = index,
            mat_name = mat_name,
            mat_tag = mat_tag,
            mat_type = mat_type,
            properties = properties,
            name_to_idx = name_to_idx,
        ) # Storing materials data to dataclass
        self._mats_list.append(materials) # Append Materials Properties into material list
        return materials
    
    def _translate_mat_concrete04(self):
        sheet_name = "Mat_Concrete04"
        data, n = self._reader.read(
            sheet_name=sheet_name, 
            orientation="columns", 
            start_row=12,
        ) # Reading Sheet "Mat_Concrete04" in the Input file
        if not self._validate_data(nrows=n, sheet_name=sheet_name, mandatory=False):
            mat_concrete04 = Mat_Concrete04.empty()
            self._mats_list.append(mat_concrete04)
            return mat_concrete04
        index = np.arange(n, dtype=np.int32)
        mat_name = np.asarray(data["Material Name"], dtype="U32")
        self._validate_duplicate_value(col_data=mat_name, col_name="Material Name")
        mat_tag = np.asarray(self._tagmanager.add(category="Material", n=n, names=mat_name), dtype=np.int32)
        basemat_class, _, basemat_idx = self._retrieve_material_index(mats_name=data["Base Material"])
        mat_type = np.asarray([
            self._mats_list[cls].mat_type[idx]
            for cls, idx in zip(basemat_class, basemat_idx)],
            dtype="U15",
        )
        mat_model = np.asarray(data["Material Model"], dtype="U15")
        basemat_props = get_material_properties(
            mats_list=self._mats_list,
            mat_class=basemat_class,
            mat_idx=basemat_idx,
            props_name=["Unitweight", "E", "nu", "G"],
        )
        fc = self._to_internalunits.stress(values=data["fc"])
        epsc = np.asarray(data["epsc"], dtype=np.float64)
        epscu = np.asarray(data["epscu"], dtype=np.float64)
        fct = self._to_internalunits.stress(values=data["fct"])
        et = np.where(
            np.asarray(data["et"], dtype=np.float64) != 0.0,
            np.asarray(data["et"], dtype=np.float64), 
            fct * epsc / fc,
        )
        beta = np.asarray(data["beta"], dtype=np.float64)
        properties = np.column_stack((
            basemat_props,
            fc,
            epsc,
            epscu,
            fct,
            et,
            beta,
        ))
        name_to_idx = dict(zip(mat_name, index))
        mat_concrete04 = Mat_Concrete04(
            index = index,
            mat_name = mat_name,
            mat_tag=mat_tag,
            basemat_class = basemat_class,
            basemat_idx = basemat_idx,
            mat_type = mat_type,
            mat_model = mat_model,
            properties = properties,
            name_to_idx = name_to_idx,
        ) # Storing materials data to dataclass
        self._mats_list.append(mat_concrete04) # Append Mat_Concrete04 Properties into material list
        return mat_concrete04

    def _translate_mat_steel02(self):
        sheet_name = "Mat_Steel02"
        data, n = self._reader.read(
            sheet_name=sheet_name, 
            orientation="columns", 
            start_row=18,
        ) # Reading Sheet "Mat_Steel02" in the Input file
        if not self._validate_data(nrows=n, sheet_name=sheet_name, mandatory=False):
            mat_steel02 = Mat_Steel02.empty()
            self._mats_list.append(mat_steel02)
            return mat_steel02
        index = np.arange(n, dtype=np.int32)
        mat_name = np.asarray(data["Material Name"], dtype="U32")
        self._validate_duplicate_value(col_data=mat_name, col_name="Material Name")
        mat_tag = np.asarray(self._tagmanager.add(category="Material", n=n, names=mat_name), dtype=np.int32)
        basemat_class, _, basemat_idx = self._retrieve_material_index(mats_name=data["Base Material"])
        mat_type = np.asarray([
            self._mats_list[cls].mat_type[idx]
            for cls, idx in zip(basemat_class, basemat_idx)],
            dtype="U15",
        )
        mat_model = np.asarray(data["Material Model"], dtype="U15")
        basemat_props = get_material_properties(
            mats_list=self._mats_list,
            mat_class=basemat_class,
            mat_idx=basemat_idx,
            props_name=["Unitweight", "E", "nu", "G"],
        )
        E = basemat_props[:, 1]
        fy = self._to_internalunits.stress(values=data["fy"])
        fu = self._to_internalunits.stress(values=data["fu"])
        eu = np.asarray(data["eu"], dtype=np.float64)
        ey = fy / E
        eoffset = ey + 0.002
        Epy = (fu - fy) / (eu - eoffset)    
        b = np.where(
            np.asarray(data["b"], dtype=np.float64) != 0.0,
            np.asarray(data["b"], dtype=np.float64), 
            Epy / E,
        )
        R0 = np.asarray(data["R0"], dtype=np.float64)
        cR1 = np.asarray(data["cR1"], dtype=np.float64)
        cR2 = np.asarray(data["cR2"], dtype=np.float64)
        a1 = np.asarray(data["a1"], dtype=np.float64)
        a2 = np.asarray(data["a2"], dtype=np.float64)
        a3 = np.asarray(data["a3"], dtype=np.float64)
        a4 = np.asarray(data["a4"], dtype=np.float64)
        f_init = self._to_internalunits.stress(values=data["f_init"])
        properties = np.column_stack((
            basemat_props,
            fy,
            b,
            R0,
            cR1,
            cR2,
            a1,
            a2,
            a3,
            a4,
            f_init,
        ))
        name_to_idx = dict(zip(mat_name, index))
        mat_steel02 = Mat_Steel02(
            index = index,
            mat_name = mat_name,
            mat_tag=mat_tag,
            basemat_class = basemat_class,
            basemat_idx = basemat_idx,
            mat_type = mat_type,
            mat_model = mat_model,
            properties = properties,
            name_to_idx = name_to_idx,
        ) # Storing materials data to dataclass
        self._mats_list.append(mat_steel02) # Append Mat_Steel02 Properties into material list
        return mat_steel02

    def _translate_mat_minmax(self):
        sheet_name = "Mat_MinMax"
        data, n = self._reader.read(
            sheet_name=sheet_name, 
            orientation="columns", 
            start_row=8,
        ) # Reading Sheet "Mat_MinMax" in the Input file
        if not self._validate_data(nrows=n, sheet_name=sheet_name, mandatory=False):
            mat_minmax = Mat_MinMax.empty()
            self._mats_list.append(mat_minmax)
            return mat_minmax
        index = np.arange(n, dtype=np.int32)
        mat_name = np.asarray(data["Material Name"], dtype="U32")
        self._validate_duplicate_value(col_data=mat_name, col_name="Material Name")
        mat_tag = np.asarray(self._tagmanager.add(category="Material", n=n, names=mat_name), dtype=np.int32)
        basemat_class, _, basemat_idx = self._retrieve_material_index(mats_name=data["Base NL Material"])
        mat_type = np.asarray([
            self._mats_list[cls].mat_type[idx]
            for cls, idx in zip(basemat_class, basemat_idx)],
            dtype="U15",
        )
        mat_model = np.asarray(data["Material Model"], dtype="U15")
        basemat_props = get_material_properties(
            mats_list=self._mats_list,
            mat_class=basemat_class,
            mat_idx=basemat_idx,
            props_name=["Unitweight", "E", "nu", "G"],
        )
        ecmax = np.asarray(data["ecmax"], dtype=np.float64)
        etmax = np.asarray(data["etmax"], dtype=np.float64)
        properties = np.column_stack((
            basemat_props,
            ecmax,
            etmax,
        ))
        name_to_idx = dict(zip(mat_name, index))
        mat_minmax = Mat_MinMax(
            index = index,
            mat_name = mat_name,
            mat_tag=mat_tag,
            basemat_class = basemat_class,
            basemat_idx = basemat_idx,
            mat_type = mat_type,
            mat_model = mat_model,
            properties = properties,
            name_to_idx = name_to_idx
        ) # Storing materials data to dataclass
        self._mats_list.append(mat_minmax) # Append Mat_MinMax Properties into material list
        return mat_minmax
    
    def _translate_mat_imk(self):
        sheet_name = "Mat_IMK"
        data, n = self._reader.read(
            sheet_name=sheet_name, 
            orientation="columns", 
            start_row=19,
        ) # Reading Sheet "Mat_IMK" in the Input file
        if not self._validate_data(nrows=n, sheet_name=sheet_name, mandatory=False):
            mat_imk = Mat_IMK.empty()
            return mat_imk
        index = np.arange(n, dtype=np.int32)
        mat_name = np.asarray(data["Material Name"], dtype="U32")
        self._validate_duplicate_value(col_data=mat_name, col_name="Material Name")
        mat_tag = np.asarray(self._tagmanager.add(category="Material", n=n, names=mat_name), dtype=np.int32)
        mat_model = np.asarray(data["Material Model"], dtype="U15")
        K0 = self._to_internalunits.rotational_stiffness(values=data["K0"])
        my_pos = self._to_internalunits.moment(values=data["My_Pos"])
        my_neg = self._to_internalunits.moment(values=data["My_Neg"])
        theta_e_pos = my_pos / K0
        theta_e_neg = my_neg / K0
        mu_pos = self._to_internalunits.moment(values=data["Mu_Pos"])
        mu_neg = self._to_internalunits.moment(values=data["Mu_Neg"])
        fpr_pos = np.asarray(data["Fpr_Pos"], dtype=np.float64)
        fpr_neg = np.asarray(data["Fpr_Neg"], dtype=np.float64)
        a_pinch = np.asarray(data["A_pinch"], dtype=np.float64)
        nfactor = np.asarray(data["nFactor"], dtype=np.float64)
        lamda_s = np.asarray(data["Lamda_S"], dtype=np.float64)
        lamda_c = np.asarray(data["Lamda_C"], dtype=np.float64)
        lamda_a = np.asarray(data["Lamda_A"], dtype=np.float64)
        lamda_k = np.asarray(data["Lamda_K"], dtype=np.float64)
        c_s = np.asarray(data["c_S"], dtype=np.float64)
        c_c = np.asarray(data["c_C"], dtype=np.float64)
        c_a = np.asarray(data["c_A"], dtype=np.float64)
        c_k = np.asarray(data["c_K"], dtype=np.float64)
        theta_p_pos = self._to_internalunits.angle(values=data["theta_p_Pos"])
        theta_p_neg = self._to_internalunits.angle(values=data["theta_p_Neg"])
        Kpy_pos = (mu_pos - my_pos) / (theta_p_pos - theta_e_pos)
        Kpy_neg = (mu_neg - my_neg) / (theta_p_neg - theta_e_neg)
        as_pos = K0 / Kpy_pos
        as_neg = K0 / Kpy_neg
        theta_pc_pos = self._to_internalunits.angle(values=data["theta_pc_Pos"])
        theta_pc_neg = self._to_internalunits.angle(values=data["theta_pc_Neg"])
        res_pos = np.asarray(data["Res_Pos"], dtype=np.float64)
        res_neg = np.asarray(data["Res_Neg"], dtype=np.float64)
        theta_u_pos = self._to_internalunits.angle(values=data["theta_u_Pos"])
        theta_u_neg = self._to_internalunits.angle(values=data["theta_u_Neg"])
        d_pos = np.asarray(data["D_Pos"], dtype=np.float64)
        d_neg = np.asarray(data["D_Neg"], dtype=np.float64)
        properties = np.column_stack((
            K0,
            as_pos,
            as_neg,
            my_pos,
            my_neg,
            fpr_pos,
            fpr_neg,
            a_pinch,
            nfactor,
            lamda_s,
            lamda_c,
            lamda_a,
            lamda_k,
            c_s,
            c_c,
            c_a,
            c_k,
            theta_p_pos,
            theta_p_neg,
            theta_pc_pos,
            theta_pc_neg,
            res_pos,
            res_neg,
            theta_u_pos,
            theta_u_neg,
            d_pos,
            d_neg,
        ))
        name_to_idx = dict(zip(mat_name, index))
        mat_imk = Mat_IMK(
            index = index,
            mat_name = mat_name,
            mat_tag=mat_tag,
            mat_model = mat_model,
            properties = properties,
            name_to_idx = name_to_idx,
        ) # Storing materials data to dataclass
        self._hinge_mats_list.append(mat_imk) # Append Materials Properties into hinge material list
        return mat_imk
    
    def _translate_frame_sections(self):
        sheet_name = "Frame Sections"
        data, n = self._reader.read(
            sheet_name=sheet_name, 
            orientation="columns", 
            start_row=15,
        ) # Reading Sheet "Frame Sections" in the Input file
        self._validate_data(nrows=n, sheet_name=sheet_name, mandatory=True)
        index = np.arange(n, dtype=np.int32)
        sec_name = np.asarray(data["Section Name"], dtype="U32")
        self._validate_duplicate_value(col_data=sec_name, col_name="Section Name")
        sec_tag = np.asarray(self._tagmanager.add(category="Section", n=n, names=sec_name), dtype=np.int32)
        sec_shape = np.asarray(data["Section Shape"], dtype="U32")
        mat_class, _, mat_idx = self._retrieve_material_index(mats_name=data["Material"])
        mats_class = np.column_stack((
            mat_class,
        ))
        mats_idx = np.column_stack((
            mat_idx,
        ))
        mat_type = np.asarray([
            self._mats_list[cls].mat_type[idx]
            for cls, idx in zip(mat_class, mat_idx)],
            dtype="U15",
        )
        sec_model = np.asarray(data["Section Model"], dtype="U15")
        h = self._to_internalunits.length(values=data["h"])
        b = self._to_internalunits.length(values=data["b"])
        AMod = np.asarray(data["AMod"], dtype=np.float64)
        AvyMod = np.asarray(data["AvyMod"], dtype=np.float64)
        AvzMod = np.asarray(data["AvzMod"], dtype=np.float64)
        IzMod = np.asarray(data["IzMod"], dtype=np.float64)
        IyMod = np.asarray(data["IyMod"], dtype=np.float64)
        JxxMod = np.asarray(data["JxxMod"], dtype=np.float64)
        dimensions = np.column_stack((
            h,
            b,
        ))
        (A, Avy, Avz, Iz, Iy, Jxx, alphaY, alphaZ,) = compute_section_properties(
            sec_shape=sec_shape,
            mat_type=mat_type, 
            dimensions=dimensions,
        )
        properties = np.column_stack((
            dimensions,
            AMod * A,
            AvyMod * Avy,
            AvzMod * Avz,
            IzMod * Iz,
            IyMod * Iy,
            JxxMod * Jxx,
            alphaY,
            alphaZ,
        ))
        name_to_idx = dict(zip(sec_name, index))
        frame_sections = FrameSections(
            index = index,
            sec_name = sec_name,
            sec_tag=sec_tag,
            sec_shape = sec_shape,
            mats_class = mats_class,
            mats_idx = mats_idx,
            mat_type = mat_type,
            sec_model = sec_model,
            properties = properties,
            name_to_idx = name_to_idx
        ) # Storing sections data to dataclass
        self._secs_list.append(frame_sections) # Append FrameSections Properties into section list
        return frame_sections
    
    def _translate_sec_fiber(self):
        sheet_name = "Sec_Fiber"
        data, n = self._reader.read(
            sheet_name=sheet_name, 
            orientation="columns", 
            start_row=20,
        ) # Reading Sheet "Sec_Fiber" in the Input file
        if not self._validate_data(nrows=n, sheet_name=sheet_name, mandatory=False):
            sec_fiber = Sec_Fiber.empty()
            self._secs_list.append(sec_fiber)
            return sec_fiber
        index = np.arange(n, dtype=np.int32)
        sec_name = np.asarray(data["Section Name"], dtype="U32")
        self._validate_duplicate_value(col_data=sec_name, col_name="Section Name")
        sec_tag = np.asarray(self._tagmanager.add(category="Section", n=n, names=sec_name), dtype=np.int32)
        basesec_class, _, basesec_idx = self._retrieve_section_index(secs_name=data["Base Section"])
        sec_shape = np.asarray([
            self._secs_list[cls].sec_shape[idx]
            for cls, idx in zip(basesec_class, basesec_idx)],
            dtype="U32",
        )
        integration_type = np.asarray(data["Integration Type"], dtype="U15")
        integration_tag = np.asarray(self._tagmanager.add(category="Beam Integration", n=n, names=sec_name), dtype=np.int32)
        mats_class = np.full((n, 3), -1, dtype=np.int32)
        mats_idx = np.full((n, 3), -1, dtype=np.int32)
        material_columns = ["Material", "Material 2", "Material 3"]
        for j, column in enumerate(material_columns):
            materials = data[column]
            mask = np.array([m is not None for m in materials])
            if not np.any(mask):
                continue
            mat_class, _, mat_idx = self._retrieve_material_index(mats_name=[m for m in materials if m is not None])
            mats_class[mask, j] = mat_class
            mats_idx[mask, j] = mat_idx
        mat_type = np.empty(n, dtype="U15")
        for i in range(n):
            if mats_class[i, 0] >= 0:
                j = 0
            elif mats_class[i, 1] >= 0:
                j = 1
            elif mats_class[i, 2] >= 0:
                j = 2
            else:
                continue
            mat_type[i] = self._mats_list[mats_class[i, j]].mat_type[mats_idx[i, j]]
        sec_model = np.asarray(data["Section Model"], dtype="U15")
        basesec_props = get_section_properties(
            secs_list=self._secs_list,
            sec_class=basesec_class,
            sec_idx=basesec_idx,
            props_name=["h", "b"],
        )
        cover = self._to_internalunits.length(values=data["cover"])
        nbars_top = np.asarray(data["nBarsTop"], dtype=np.int32)
        nbars_bot = np.asarray(data["nBarsBot"], dtype=np.int32)
        nbars_int = np.asarray(data["nBarsInt"], dtype=np.int32)
        bar_dia_hoop = self._to_internalunits.length(values=data["barDiaHoop"])
        bar_dia_top = self._to_internalunits.length(values=data["barDiaTop"])
        bar_dia_bot = self._to_internalunits.length(values=data["barDiaBot"])
        bar_dia_int = self._to_internalunits.length(values=data["barDiaInt"])
        dimensions = np.column_stack((
            basesec_props,
            cover,
            nbars_top,
            nbars_bot,
            nbars_int,
            bar_dia_hoop,
            bar_dia_top,
            bar_dia_bot,
            bar_dia_int,
        ))
        (A, Avy, Avz, Iz, Iy, Jxx, Abar_top, Abar_bot, Abar_int,) = compute_fibersection_properties(
            sec_shape=sec_shape,
            mat_type=mat_type,
            dimensions=dimensions,
        )
        properties = np.column_stack((
            dimensions,
            A,
            Avy,
            Avz,
            Iz,
            Iy,
            Jxx,
            Abar_top,
            Abar_bot,
            Abar_int,
        ))
        name_to_idx = dict(zip(sec_name, index))
        sec_fiber = Sec_Fiber(
            index = index,
            sec_name = sec_name,
            sec_tag=sec_tag,
            sec_shape = sec_shape,
            basesec_class = basesec_class,
            basesec_idx = basesec_idx,
            integration_type = integration_type,
            integration_tag = integration_tag,
            mats_class = mats_class,
            mats_idx = mats_idx,
            mat_type = mat_type,
            sec_model = sec_model,
            properties = properties,
            name_to_idx = name_to_idx,
        ) # Storing sections data to dataclass
        self._secs_list.append(sec_fiber) # Append Sec_Fiber Properties into section list
        return sec_fiber
    
    def _translate_sec_aggregator(self):
        sheet_name = "Sec_Aggregator"
        data, n = self._reader.read(
            sheet_name=sheet_name, 
            orientation="columns", 
            start_row=15,
        ) # Reading Sheet "Sec_Aggregator" in the Input file
        if not self._validate_data(nrows=n, sheet_name=sheet_name, mandatory=False):
            sec_aggregator = Sec_Aggregator.empty()
            self._secs_list.append(sec_aggregator)
            return sec_aggregator
        index = np.arange(n, dtype=np.int32)
        sec_name = np.asarray(data["Section Name"], dtype="U32")
        self._validate_duplicate_value(col_data=sec_name, col_name="Section Name")
        sec_tag = np.asarray(self._tagmanager.add(category="Section", n=n, names=sec_name), dtype=np.int32)
        basesec_class, _, basesec_idx = self._retrieve_section_index(secs_name=data["Base Section"])
        sec_shape = np.asarray([
            self._secs_list[cls].sec_shape[idx]
            for cls, idx in zip(basesec_class, basesec_idx)],
            dtype="U32",
        )
        mats_class = np.full((n, 6), -1, dtype=np.int32)
        mats_idx = np.full((n, 6), -1, dtype=np.int32)
        material_columns = ["Material", "Material 2", "Material 3", "Material 4", "Material 5", "Material 6"]
        for j, column in enumerate(material_columns):
            materials = data[column]
            material_mask = np.array([m is not None for m in materials])
            if not np.any(material_mask):
                continue
            mat_class, _, mat_idx = self._retrieve_material_index(mats_name=[m for m in materials if m is not None])
            mats_class[material_mask, j] = mat_class
            mats_idx[material_mask, j] = mat_idx
        mat_type = np.empty(n, dtype="U15")
        for i in range(n):
            if mats_class[i, 0] >= 0:
                j = 0
            elif mats_class[i, 1] >= 0:
                j = 1
            elif mats_class[i, 2] >= 0:
                j = 2
            elif mats_class[i, 3] >= 0:
                j = 3
            elif mats_class[i, 4] >= 0:
                j = 4
            elif mats_class[i, 5] >= 0:
                j = 5
            else:
                continue
            mat_type[i] = self._mats_list[mats_class[i, j]].mat_type[mats_idx[i, j]]
        sec_model = np.asarray(data["Section Model"], dtype="U15")
        aggregated_sec_class = np.full(n, -1, dtype=np.int32)
        aggregated_sec_idx = np.full(n, -1, dtype=np.int32)
        sections = data["Aggregated Section"]
        section_mask = np.array([s is not None for s in sections])
        if np.any(section_mask):
            sec_class, _, sec_idx = self._retrieve_section_index(sec_name=[s for s in sections if s is not None])
            aggregated_sec_class[section_mask] = sec_class
            aggregated_sec_idx[section_mask] = sec_idx
        sec_props = get_section_properties(
            secs_list=self._secs_list,
            sec_class=np.where(aggregated_sec_class >= 0, aggregated_sec_class, basesec_class),
            sec_idx=np.where(aggregated_sec_idx >= 0, aggregated_sec_idx, basesec_idx),
            props_name=["h", "b", "A", "Avy", "Avz", "Iz", "Iy", "Jxx"],
        )
        properties = sec_props
        name_to_idx = dict(zip(sec_name, index))
        sec_aggregator = Sec_Aggregator(
            index = index,
            sec_name = sec_name,
            sec_tag=sec_tag,
            sec_shape = sec_shape,
            basesec_class = basesec_class,
            basesec_idx = basesec_idx,
            mats_class = mats_class,
            mats_idx = mats_idx,
            mat_type = mat_type,
            sec_model = sec_model,
            aggregated_sec_class = aggregated_sec_class,
            aggregated_sec_idx = aggregated_sec_idx,
            properties = properties,
            name_to_idx = name_to_idx,
        ) # Storing sections data to dataclass
        self._secs_list.append(sec_aggregator) # Append Sec_Aggregator Properties into section list
        return sec_aggregator

    def _translate_slab_sections(self):
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
        mat_class, _, mat_idx = self._retrieve_material_index(mats_name=data["Material"])
        mats_class = np.column_stack((
            mat_class,
        ))
        mats_idx = np.column_stack((
            mat_idx,
        ))
        t = self._to_internalunits.length(values=data["t"])
        properties = np.column_stack((
            t,
        ))
        name_to_idx = dict(zip(sec_name, index))
        slab_sections = SlabSections(
            index = index,
            sec_name = sec_name,
            mats_class = mats_class,
            mats_idx = mats_idx,
            properties = properties,
            name_to_idx = name_to_idx,
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

    def _translate_line_objects(self, point_objects):
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
        iend_node = np.asarray(data["I-End"], dtype="U15")
        jend_node = np.asarray(data["J-End"], dtype="U15")
        point_name_to_idx = point_objects["Name to Index"]
        end_points_idx = np.column_stack((
            np.fromiter((point_name_to_idx[name] for name in iend_node), dtype=np.int32, count=n),
            np.fromiter((point_name_to_idx[name] for name in jend_node), dtype=np.int32, count=n),
        ))
        element_type = np.asarray(data["Element Type"], dtype="U15")
        sec_class, _, sec_idx = self._retrieve_section_index(secs_name=data["Section"])
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
            "Section Class": sec_class,
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
        element_type = np.asarray(data["Element Type"], dtype="U15")
        sec_class, _, sec_idx = self._retrieve_slabsection_index(
            secs_name=data["Section"],
            secs_list=[slab_sections],
        )
        name_to_idx = dict(zip(unique_name, index))
        surface_objects = {
            "Index": index,
            "Unique Name": unique_name,
            "Edges Index": edges_idx,
            "Vertices Index": vertices_idx,
            "Element Type": element_type,
            "Section Class": sec_class,
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
        loadcase_type = np.asarray(data["Load Case"], dtype="U15")
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
        loadcase_type = np.asarray(data["Load Case"], dtype="U15")
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
        loadcase_type = np.asarray(data["Load Case"], dtype="U15")
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
        loadcase_type = np.asarray(data["Load Case"], dtype="U15")
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