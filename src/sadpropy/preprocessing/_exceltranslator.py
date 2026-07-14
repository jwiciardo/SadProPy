import warnings
import numpy as np
from openpyxl import load_workbook
from ._preproc_dataclass import (
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
    PointObjects,
    LineObjects,
    SurfaceObjects,
    Storeys,
    Nodes,
    )
from ._propertiesclass import (
    MaterialProperties,
    Concrete04Properties,
    Steel02Properties,
    MinMaxProperties,
    IMKProperties,
    FrameSectionProperties,
    FiberSectionProperties,
    SectionAggregatorProperties,
    SlabSectionProperties,
)
from sadpropy.utility import (
    UnitConverter,
    UnitRegistry,
    UnitSystem,
    section_properties,
    fibersection_properties,
    TagManager,
)
from sadpropy.utility._exceptions import ValidationError
from sadpropy.utility.helper import get_material_properties, get_section_properties

class ExcelReader:
    def __init__(self, inputfile_path):
        if not inputfile_path.exists():
            raise FileNotFoundError(f"File not found: {inputfile_path}")
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="Data Validation extension is not supported*")
            self._workbook = load_workbook(inputfile_path, data_only=True)
    
    # MAIN METHOD: EXCELREADER
    def read(self, sheet_name="", start_row=1):
        if sheet_name not in self._workbook.sheetnames:
            raise ValidationError(f"Sheet '{sheet_name}' not found in Excel file")
        worksheet = self._workbook[sheet_name]
        rows = list(worksheet.values)
        headers = list(rows[start_row - 1])
        while headers and headers[-1] is None:
            headers.pop()
        data = []
        for row in rows[start_row:]:
            row = row[:len(headers)]
            record = dict(zip(headers, row))
            if all(v is None for v in record.values()): # Skip completely empty rows
                continue
            data.append(record)
        return data

class ExcelTranslator:
    def __init__(self, inputfile_path):
        self._reader = ExcelReader(inputfile_path)
        self._units = None
        self._unitregistry = UnitRegistry()
        self._unitconverter = UnitConverter(self._unitregistry)
        self._mats_list = []
        self._secs_list = []

    # UNIT CONVERTER METHODS TO INTERNAL UNITS
    def _to_internalunit_length(self, value):
        return self._unitconverter.to_internal_units(value, self._units.length)

    def _to_internalunit_force(self, value):
        return self._unitconverter.to_internal_units(value, self._units.force)
        
    def _to_internalunit_mass(self, value):
        return self._unitconverter.to_internal_units(value, self._units.mass)
        
    def _to_internalunit_velocity(self, value):
        return self._unitconverter.to_internal_units(value, self._units.velocity())
        
    def _to_internalunit_acceleration(self, value):
        return self._unitconverter.to_internal_units(value, self.units._acceleration())
        
    def _to_internalunit_stress(self, value):
        return self._unitconverter.to_internal_units(value, self._units.stress)
        
    def _to_internalunit_time(self, value):
        return self._unitconverter.to_internal_units(value, self._units.time)
        
    def _to_internalunit_angle(self, value):
        return self._unitconverter.to_internal_units(value, self._units.angle)
        
    def _to_internalunit_area(self, value):
        return self._unitconverter.to_internal_units(value, self._units.area())
        
    def _to_internalunit_volume(self, value):
        return self._unitconverter.to_internal_units(value, self._units.volume())
        
    def _to_internalunit_second_moment_of_area(self, value):
        return self._unitconverter.to_internal_units(value, self._units.second_moment_of_area())
        
    def _to_internalunit_moment(self, value):
        return self._unitconverter.to_internal_units(value, self._units.moment())
        
    def _to_internalunit_unitweight(self, value):
        return self._unitconverter.to_internal_units(value, self._units.unitweight())
        
    def _to_internalunit_surfaceload(self, value):
        return self._unitconverter.to_internal_units(value, self._units.surface_load())
        
    def _to_internalunit_distributed_lineload(self, value):
        return self._unitconverter.to_internal_units(value, self._units.distributed_line_load())
        
    def _to_internalunit_concentrated_lineload(self, value):
        return self._unitconverter.to_internal_units(value, self._units.concentrated_line_load())
        
    def _to_internalunit_force_pointload(self, value):
        return self._unitconverter.to_internal_units(value, self._units.force_point_load())

    def _to_internalunit_moment_pointload(self, value):
        return self._unitconverter.to_internal_units(value, self._units.moment_point_load())
    
    def _to_internalunit_translational_stiffness(self, value):
        return self._unitconverter.to_internal_units(value, self._units.translational_stiffness())
    
    def _to_internalunit_rotational_stiffness(self, value):
        return self._unitconverter.to_internal_units(value, self._units.rotational_stiffness())
    
    # MAIN METHOD: EXCEL TRANSLATOR
    def translate(self):
        project_information = self._translate_project_information()
        self._units = self._translate_user_unitsystem()
        analysis_preferences = self._translate_analysis_preferences()
        materials = self._translate_materials()
        mat_concrete04 = self._translate_mat_concrete04()
        mat_steel02 = self._translate_mat_steel02()
        mat_minmax = self._translate_mat_minmax()
        mat_imk = self._translate_mat_imk()
        materials_list = self._mats_list
        frame_sections = self._translate_frame_sections()
        sec_fiber = self._translate_sec_fiber()
        sec_aggregator = self._translate_sec_aggregator()
        sections_list = self._secs_list
        slab_sections = self._translate_slab_sections()
        point_objects, storeys = self._translate_point_objects()
        line_objects = self._translate_line_objects(point_objects)
        surface_objects = self._translate_surface_objects(line_objects, slab_sections)
        return {
            "project_information": project_information,
            "user_unitsystem": self._units,
            "analysis_preferences": analysis_preferences,
            "materials": materials,
            "mat_concrete04": mat_concrete04,
            "mat_steel02": mat_steel02,
            "mat_minmax": mat_minmax,
            "mat_imk": mat_imk,
            "materials_list": materials_list,
            "frame_sections": frame_sections,
            "sec_fiber": sec_fiber,
            "sec_aggregator": sec_aggregator,
            "sections_list": sections_list,
            "slab_sections": slab_sections,
            "storeys": storeys,
            "point_objects": point_objects,
            "line_objects": line_objects,
            "surface_objects": surface_objects,
        }

    # HELPER METHOD
    def _generate_storeys(self, storey_elevations): # Create Storey data
        storeys = {}
        for i, elev in reversed(list(enumerate(storey_elevations))):
            if i == 0:
                storey_name = "Base"
                height = 0.0
            else:
                storey_name = f"Storey{i}"
                height = elev - storey_elevations[i - 1]
            storeys[storey_name] = Storeys(
                name = storey_name,
                height = height,
                elevation = elev,
            )
        return storeys

    def _retrieve_material_index(self, mat_name):
        for mat_class, mat in enumerate(self._mats_list):
            mat_idx = mat.name_to_idx.get(mat_name)
            if mat_idx is not None:
                return mat_class, mat, mat_idx
        raise ValidationError(f"Material '{mat_name}' not found.")
    
    def _retrieve_section_index(self, sec_name):
        for sec_class, sec in enumerate(self._secs_list):
            sec_idx = sec.name_to_idx.get(sec_name)
            if sec_idx is not None:
                return sec_class, sec, sec_idx
        raise ValidationError(f"Section '{sec_name}' not found.")
    
    def _retrieve_slabsection_index(self, sec_name, secs_list):
        for sec_class, sec in enumerate([secs_list]):
            sec_idx = sec.name_to_idx.get(sec_name)
            if sec_idx is not None:
                return sec_class, sec, sec_idx
        raise ValidationError(f"Section '{sec_name}' not found.")
    
    # SUPPORTING METHODS
    def _translate_project_information(self):
        data = self._reader.read(sheet_name="Project Information", start_row=6) # Reading Sheet "Project Information" in the Input file
        values = {row["Item"]: row["Value"] for row in data}
        project_information = ProjectInformation(
                name = str(values["Project Name"]),
                desc = str(values["Project Description"]),
                ndim = int(3 if values["Model Dimensional Space"] == "3-Dimensional" else 2),
        ) # Defining dataclass for project information
        return project_information
    
    def _translate_user_unitsystem(self):
        data = self._reader.read(sheet_name="User Specified Unitsystem", start_row=9) # Reading Sheet "User Specified Unitsystem" in the Input file
        values = {row["Item"]: row["Value"] for row in data}
        user_unitsystem = UnitSystem(
                force = str(values["Force"]),
                length = str(values["Length"]),
                mass = str(values["Mass"]),
                stress = str(values["Stress"]),
                time = str(values["Time"]),
                angle = str(values["Angle"]),
        ) # Defining dataclass for units
        return user_unitsystem

    def _translate_analysis_preferences(self):
        data = self._reader.read(sheet_name="Analysis Preferences", start_row=6) # Reading Sheet "Analysis Preferences" in the Input file
        values = {row["Item"]: row["Value"] for row in data}
        analysis_preferences = AnalysisPreferences(
                nonlinear_analysis = str(values["Nonlinear Analysis"]),
                pdelta = str(values["P-Delta"]),
                liveload_mass_factor = float(values["LL Mass Factor"]),
        ) # Defining dataclass for analysis preferences
        return analysis_preferences

    def _translate_materials(self):
        data = self._reader.read(sheet_name="Materials", start_row=13) # Reading Sheet "Materials" in the Input file
        n = len(data)
        index = np.arange(n, dtype=np.int32)
        mat_name = np.empty(n, dtype="U32")
        mat_type = np.empty(n, dtype="U15")
        properties = np.zeros((n, len(MaterialProperties)), dtype=np.float64)
        name_to_idx = {}
        for i, row in enumerate(data):
            name = str(row["Material Name"])
            if name in name_to_idx:
                raise ValidationError(f"Duplicate Material name '{name}'")
            name_to_idx[name] = index[i]
            mat_name[i] = name
            mattype = str(row["Material Type"])
            mat_type[i] = mattype
            Unitweight = self._to_internalunit_unitweight(row["Unitweight"])
            E = self._to_internalunit_stress(row["E"])
            nu = row["nu"]
            fc = self._to_internalunit_stress(row["fc"]) if mattype == "Concrete" else 0.0
            fy = self._to_internalunit_stress(row["fy"]) if mattype in ("Rebar", "Steel") else 0.0
            fu = self._to_internalunit_stress(row["fu"]) if mattype in ("Rebar", "Steel") else 0.0
            properties[i] = (Unitweight, E, nu, 0.0, fc, fy, fu,) # Look at MaterialProperties class in _propertiesclass.py to find definition of variables
        E, nu = properties[:, MaterialProperties.E], properties[:, MaterialProperties.nu]
        properties[:, MaterialProperties.G] = E / (2 * (1 + nu))
        materials = Materials(
            index = index,
            mat_name = mat_name,
            mat_type = mat_type,
            properties = properties,
            name_to_idx = name_to_idx,
        ) # Storing material data to dataclass
        self._mats_list.append(materials) # Append Materials Properties into Material Lists
        return materials
    
    def _translate_mat_concrete04(self):
        data = self._reader.read(sheet_name="Mat_Concrete04", start_row=12) # Reading Sheet "Mat_Concrete04" in the Input file
        n = len(data)
        index = np.arange(n, dtype=np.int32)
        mat_name = np.empty(n, dtype="U32")
        mat_type = np.empty(n, dtype="U15")
        base_mat_class = np.empty(n, dtype=np.int32)
        base_mat_idx = np.empty(n, dtype=np.int32)
        mat_model = np.empty(n, dtype="U15")
        properties = np.zeros((n, len(Concrete04Properties)), dtype=np.float64)
        name_to_idx = {}
        for i, row in enumerate(data):
            name = str(row["Material Name"])
            if name in name_to_idx:
                raise ValidationError(f"Duplicate Material name '{name}'")
            name_to_idx[name] = index[i]
            mat_name[i] = name
            mat_class, _, mat_idx = self._retrieve_material_index(str(row["Base Material"]))
            base_mat_class[i] = mat_class
            base_mat_idx[i] = mat_idx
            mat_type[i] = self._mats_list[mat_class].mat_type[mat_idx]
            mat_model[i] = str(row["Material Model"])
            fc = self._to_internalunit_stress(row["fc"])
            epsc, epscu = row["epsc"], row["epscu"]
            fct = self._to_internalunit_stress(row["fct"])
            et = row["et"] if row["et"] != 0.0 else fct * epsc / fc
            beta = row["beta"]
            properties[i] = (0.0, 0.0, 0.0, 0.0, -fc, -epsc, -epscu, fct, et, beta,) # Look at Concrete04Properties class in _propertiesclass.py to find definition of variables
        base_mat_props = get_material_properties(
            self._mats_list,
            base_mat_class,
            base_mat_idx,
            ["Unitweight", "E", "nu", "G"]
        )
        properties[:, Concrete04Properties.Unitweight:Concrete04Properties.G+1] = base_mat_props
        mat_concrete04 = Mat_Concrete04(
            index = index,
            mat_name = mat_name,
            mat_type = mat_type,
            base_mat_class = base_mat_class,
            base_mat_idx = base_mat_idx,
            mat_model = mat_model,
            properties = properties,
            name_to_idx = name_to_idx,
        ) # Storing material data to dataclass
        self._mats_list.append(mat_concrete04) # Append Mat_Concrete04 Properties into Material Lists
        return mat_concrete04

    def _translate_mat_steel02(self):
        data = self._reader.read(sheet_name="Mat_Steel02", start_row=18) # Reading Sheet "Mat_Steel02" in the Input file
        n = len(data)
        index = np.arange(n, dtype=np.int32)
        mat_name = np.empty(n, dtype="U32")
        mat_type = np.empty(n, dtype="U15")
        base_mat_class = np.empty(n, dtype=np.int32)
        base_mat_idx = np.empty(n, dtype=np.int32)
        mat_model = np.empty(n, dtype="U15")
        properties = np.zeros((n, len(Steel02Properties)), dtype=np.float64)
        name_to_idx = {}
        fy = np.zeros(n, dtype=np.float64)
        b = np.zeros(n, dtype=np.float64)
        fu = np.zeros(n, dtype=np.float64)
        eu= np.zeros(n, dtype=np.float64)
        for i, row in enumerate(data):
            name = str(row["Material Name"])
            if name in name_to_idx:
                raise ValidationError(f"Duplicate Material name '{name}'")
            name_to_idx[name] = index[i]
            mat_name[i] = name
            mat_class, _, mat_idx = self._retrieve_material_index(str(row["Base Material"]))
            base_mat_class[i] = mat_class
            base_mat_idx[i] = mat_idx
            mat_type[i] = self._mats_list[mat_class].mat_type[mat_idx]
            mat_model[i] = str(row["Material Model"])
            fy[i] = self._to_internalunit_stress(row["fy"])
            b[i] = row["b"]
            fu[i] = self._to_internalunit_stress(row["fu"])
            eu[i] = row["eu"]
            R0 = row["R0"]
            cR1 = row["cR1"]
            cR2 = row["cR2"]
            a1 = row["a1"]
            a2 = row["a2"]
            a3 = row["a3"]
            a4 = row["a4"]
            f_init = self._to_internalunit_stress(row["f_init"])
            properties[i] = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, R0, cR1, cR2, a1, a2, a3, a4, f_init,) # Look at Steel02Properties class in _propertiesclass.py to find definition of variables
        base_mat_props = get_material_properties(
            self._mats_list,
            base_mat_class,
            base_mat_idx,
            ["Unitweight", "E", "nu", "G"]
        )
        properties[:, Steel02Properties.Unitweight:Steel02Properties.G+1] = base_mat_props
        E = properties[:, Steel02Properties.E]
        if b == 0.0:
            ey = fy / E
            eoffset = ey + 0.002
            Epy = (fu - fy)/(eu - eoffset)
            b = Epy / E
        else:
            return b
        properties[:, Steel02Properties.fy] = fy
        properties[:, Steel02Properties.b] = b
        mat_steel02 = Mat_Steel02(
            index = index,
            mat_name = mat_name,
            mat_type = mat_type,
            base_mat_class = base_mat_class,
            base_mat_idx = base_mat_idx,
            mat_model = mat_model,
            properties = properties,
            name_to_idx = name_to_idx,
        ) # Storing material data to dataclass
        self._mats_list.append(mat_steel02) # Append Mat_Steel02 Properties into Material Lists
        return mat_steel02

    def _translate_mat_minmax(self):
        data = self._reader.read(sheet_name="Mat_MinMax", start_row=8) # Reading Sheet "Mat_MinMax" in the Input file
        n = len(data)
        index = np.arange(n, dtype=np.int32)
        mat_name = np.empty(n, dtype="U32")
        mat_type = np.empty(n, dtype="U15")
        base_nl_mat_class = np.empty(n, dtype=np.int32)
        base_nl_mat_idx = np.empty(n, dtype=np.int32)
        mat_model = np.empty(n, dtype="U15")
        properties = np.zeros((n, len(MinMaxProperties)), dtype=np.float64)
        name_to_idx = {}
        for i, row in enumerate(data):
            name = str(row["Material Name"])
            if name in name_to_idx:
                raise ValidationError(f"Duplicate Material name '{name}'")
            name_to_idx[name] = index[i]
            mat_name[i] = name
            mat_class, _, mat_idx = self._retrieve_material_index(str(row["Base NL Material"]))
            base_nl_mat_class[i] = mat_class
            base_nl_mat_idx[i] = mat_idx
            mat_type[i] = self._mats_list[mat_class].mat_type[mat_idx]
            mat_model[i] = str(row["Material Model"])
            ec_max = row["ecmax"]
            et_max = row["etmax"]
            properties[i] = (0.0, 0.0, 0.0, 0.0, ec_max, et_max,) # Look at MinMaxProperties class in _propertiesclass.py to find definition of variables
        base_nl_mat_props = get_material_properties(
            self._mats_list,
            base_nl_mat_class,
            base_nl_mat_idx,
            ["Unitweight", "E", "nu", "G"]
        )
        properties[:, MinMaxProperties.Unitweight:MinMaxProperties.G+1] = base_nl_mat_props
        mat_minmax = Mat_MinMax(
            index = index,
            mat_name = mat_name,
            mat_type = mat_type,
            base_nl_mat_class = base_nl_mat_class,
            base_nl_mat_idx = base_nl_mat_idx,
            mat_model = mat_model,
            properties = properties,
            name_to_idx = name_to_idx
        ) # Storing material data to dataclass
        self._mats_list.append(mat_minmax) # Append Mat_MinMax Properties into Material Lists
        return mat_minmax
    
    def _translate_mat_imk(self):
        data = self._reader.read(sheet_name="Mat_IMK", start_row=19) # Reading Sheet "Mat_IMK" in the Input file
        n = len(data)
        index = np.arange(n, dtype=np.int32)
        mat_name = np.empty(n, dtype="U32")
        mat_model = np.empty(n, dtype="U15")
        properties = np.zeros((n, len(IMKProperties)), dtype=np.float64)
        name_to_idx = {}
        mu_pos = np.zeros(n, dtype=np.float64)
        mu_neg = np.zeros(n, dtype=np.float64)
        for i, row in enumerate(data):
            name = str(row["Material Name"])
            if name in name_to_idx:
                raise ValidationError(f"Duplicate Material name '{name}'")
            name_to_idx[name] = index[i]
            mat_name[i] = name
            mat_model[i] = str(row["Material Model"])
            K0 = self._to_internalunit_rotational_stiffness(row["K0"])
            my_pos = self._to_internalunit_moment(row["My_Pos"])
            my_neg = self._to_internalunit_moment(row["My_Neg"])
            mu_pos[i] = self._to_internalunit_moment(row["Mu_Pos"])
            mu_neg[i] = self._to_internalunit_moment(row["Mu_Neg"])
            fpr_pos, fpr_neg, a_pinch, nfactor = row["Fpr_Pos"], row["Fpr_Neg"], row["A_pinch"], row["nFactor"]
            lamda_s, lamda_c, lamda_a, lamda_k, c_s, c_c, c_a, c_k = row["Lamda_S"], row["Lamda_C"], row["Lamda_A"], row["Lamda_K"], row["c_S"], row["c_C"], row["c_A"], row["c_K"]
            theta_p_pos, theta_p_neg, theta_pc_pos, theta_pc_neg, res_pos, res_neg = row["theta_p_Pos"], row["theta_p_Neg"], row["theta_pc_Pos"], row["theta_pc_Neg"], row["Res_Pos"], row["Res_Neg"]
            theta_u_pos, theta_u_neg, d_pos, d_neg = row["theta_u_Pos"], row["theta_u_Neg"], row["D_Pos"], row["D_Neg"]
            properties[i] = (
                K0, 0.0, 0.0, my_pos, my_neg, fpr_pos, fpr_neg, a_pinch, nfactor, lamda_s, lamda_c, lamda_a, lamda_k, c_s, c_c, c_a, c_k,
                theta_p_pos, theta_p_neg, theta_pc_pos, theta_pc_neg, res_pos, res_neg, theta_u_pos, theta_u_neg, d_pos, d_neg,
            ) # Look at IMKProperties class in _propertiesclass.py to find definition of variables
        K0, my_pos, my_neg, theta_p_pos, theta_p_neg = properties[:, IMKProperties.K0], properties[:, IMKProperties.My_pos], properties[:, IMKProperties.My_neg], properties[:, IMKProperties.theta_p_pos], properties[:, IMKProperties.theta_p_neg] # Recal K0, my_pos, my_neg, theta_p_pos and theta_p_neg arrays
        theta_e_pos = my_pos / K0
        theta_e_neg = my_neg / K0
        Kpy_pos = (mu_pos - my_pos) / (theta_p_pos - theta_e_pos)
        Kpy_neg = (mu_neg - my_neg) / (theta_p_neg - theta_e_neg)
        properties[:, IMKProperties.as_pos] = K0 / Kpy_pos
        properties[:, IMKProperties.as_neg] = K0 / Kpy_neg
        mat_imk = Mat_IMK(
            index = index,
            mat_name = mat_name,
            mat_model = mat_model,
            properties = properties,
            name_to_idx = name_to_idx,
        ) # Storing material data to dataclass
        self._mats_list.append(mat_imk) # Append Mat_IMK Properties into Material Lists
        return mat_imk
    
    def _translate_frame_sections(self):
        data = self._reader.read(sheet_name="Frame Sections", start_row=16) # Reading Sheet "Frame Sections" in the Input file
        n = len(data)
        index = np.arange(n, dtype=np.int32)
        sec_name = np.empty(n, dtype="U32")
        sec_shape = np.empty(n, dtype="U15")
        element_type = np.empty(n, dtype="U15")
        base_mat_class = np.empty(n, dtype=np.int32)
        base_mat_idx = np.empty(n, dtype=np.int32)
        mat_type = np.empty(n, dtype="U15")
        sec_model = np.empty(n, dtype="U15")
        properties = np.zeros((n, len(FrameSectionProperties)), dtype=np.float64)
        name_to_idx = {}
        kA = np.zeros(n, dtype=np.float64)
        kAvy = np.zeros(n, dtype=np.float64)
        kAvz = np.zeros(n, dtype=np.float64)
        kIz = np.zeros(n, dtype=np.float64)
        kIy = np.zeros(n, dtype=np.float64)
        kJxx = np.zeros(n, dtype=np.float64)
        for i, row in enumerate(data):
            name = str(row["Section Name"])
            if name in name_to_idx:
                raise ValidationError(f"Duplicate Section name '{name}'")
            name_to_idx[name] = index[i]
            sec_name[i] = name
            sec_shape[i] = str(row["Section Shape"])
            element_type[i] = (str(row["Element Type"]))
            mat_class, _, mat_idx = self._retrieve_material_index(str(row["Base Material"]))
            base_mat_class[i] = mat_class
            base_mat_idx[i] = mat_idx
            mat_type[i] = self._mats_list[mat_class].mat_type[mat_idx]
            sec_model[i] = str(row["Section Model"])
            h = self._to_internalunit_length(row["h"])
            b = self._to_internalunit_length(row["b"])
            kA[i] = row["k_A"]
            kAvy[i] = row["k_Avy"]
            kAvz[i] = row["k_Avz"]
            kIz[i] = row["k_Iz"]
            kIy[i] = row["k_Iy"]
            kJxx[i] = row["k_Jxx"]
            properties[i] = (h, b, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        (A, Avy, Avz, Iz, Iy, Jxx, alphaY, alphaZ,) = section_properties(sec_shape, mat_type, properties)
        properties[:, FrameSectionProperties.A] = kA * A
        properties[:, FrameSectionProperties.Avy] = kAvy * Avy
        properties[:, FrameSectionProperties.Avz] = kAvz * Avz
        properties[:, FrameSectionProperties.Iz] = kIz * Iz
        properties[:, FrameSectionProperties.Iy] = kIy * Iy
        properties[:, FrameSectionProperties.Jxx] = kJxx * Jxx
        properties[:, FrameSectionProperties.AlphaY] = alphaY
        properties[:, FrameSectionProperties.AlphaZ] = alphaZ
        frame_sections = FrameSections(
            index = index,
            sec_name = sec_name,
            sec_shape = sec_shape,
            element_type = element_type,
            base_mat_class = base_mat_class,
            base_mat_idx = base_mat_idx,
            mat_type = mat_type,
            sec_model = sec_model,
            properties = properties,
            name_to_idx = name_to_idx
        ) # Defining dataclass for each frame section
        self._secs_list.append(frame_sections) # Append FrameSections Properties into Section Lists
        return frame_sections
    
    def _translate_sec_fiber(self):
        data = self._reader.read(sheet_name="Sec_Fiber", start_row=18) # Reading Sheet "Sec_Fiber" in the Input file
        n = len(data)
        index = np.arange(n, dtype=np.int32)
        sec_name = np.empty(n, dtype="U32")
        sec_shape = np.empty(n, dtype="U15")
        element_type = np.empty(n, dtype="U15")
        base_sec_class = np.empty(n, dtype=np.int32)
        base_sec_idx = np.empty(n, dtype=np.int32)
        integration_type = np.empty(n, dtype="U15")
        mats_class = np.empty((n, 3), dtype=np.int32)
        mats_idx = np.empty((n, 3), dtype=np.int32)
        mat_type = np.empty(n, dtype="U15")
        sec_model = np.empty(n, dtype="U15")
        properties = np.zeros((n, len(FiberSectionProperties)), dtype=np.float64)
        name_to_idx = {}
        for i, row in enumerate(data):
            name = str(row["Section Name"])
            if name in name_to_idx:
                raise ValidationError(f"Duplicate Section name '{name}'")
            name_to_idx[name] = index[i]
            sec_name[i] = name
            sec_class, _, sec_idx = self._retrieve_section_index(str(row["Base Section"]))
            base_sec_class[i] = sec_class
            base_sec_idx[i] = sec_idx
            sec_shape[i] = self._secs_list[sec_class].sec_shape[sec_idx]
            element_type[i] = self._secs_list[sec_class].element_type[sec_idx]
            integration_type[i] = str(row["Integration Type"])
            mat_1_class, _, mat_1_idx = self._retrieve_material_index(str(row["Material 1"]))
            mat_2_class, _, mat_2_idx = self._retrieve_material_index(str(row["Material 2"]))
            mat_3_class, _, mat_3_idx = self._retrieve_material_index(str(row["Material 3"]))
            mats_class[i, :3] = (mat_1_class, mat_2_class, mat_3_class)
            mats_idx[i, :3] = (mat_1_idx, mat_2_idx, mat_3_idx)
            mat_type[i] = self._mats_list[mat_1_class].mat_type[mat_1_idx]
            sec_model[i] = str(row["Section Model"])
            cover, nbars_top, nbars_bot, nbars_int = self._to_internalunit_length(row["cover"]), row["nBarsTop"], row["nBarsBot"], row["nBarsInt"]
            bar_dia_hoop, bar_dia_top = self._to_internalunit_length(row["barDiaHoop"]), self._to_internalunit_length(row["barDiaTop"])
            bar_dia_bot, bar_dia_int = self._to_internalunit_length(row["barDiaBot"]), self._to_internalunit_length(row["barDiaInt"])
            properties[i] = (0.0, 0.0, cover, nbars_top, nbars_bot, nbars_int, bar_dia_hoop, bar_dia_top, bar_dia_bot, bar_dia_int,
                             0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        base_sec_props = get_section_properties(
            self._secs_list,
            base_sec_class,
            base_sec_idx,
            ["h", "b"]
        )
        properties[:, FiberSectionProperties.h:FiberSectionProperties.b+1] = base_sec_props
        (A, Avy, Avz, Iz, Iy, Jxx, Abar_top, Abar_bot, Abar_int,) = fibersection_properties(sec_shape, mat_type, properties)
        properties[:, FiberSectionProperties.A] = A
        properties[:, FiberSectionProperties.Avy] = Avy
        properties[:, FiberSectionProperties.Avz] = Avz
        properties[:, FiberSectionProperties.Iz] = Iz
        properties[:, FiberSectionProperties.Iy] = Iy
        properties[:, FiberSectionProperties.Jxx] = Jxx
        properties[:, FiberSectionProperties.Abar_top] = Abar_top
        properties[:, FiberSectionProperties.Abar_bot] = Abar_bot
        properties[:, FiberSectionProperties.Abar_int] = Abar_int
        sec_fiber = Sec_Fiber(
            index = index,
            sec_name = sec_name,
            sec_shape = sec_shape,
            element_type = element_type,
            base_sec_class = base_sec_class,
            base_sec_idx = base_sec_idx,
            integration_type = integration_type,
            mats_class = mats_class,
            mats_idx = mats_idx,
            mat_type = mat_type,
            sec_model = sec_model,
            properties = properties,
            name_to_idx = name_to_idx,
        ) # Defining dataclass for each frame section
        self._secs_list.append(sec_fiber) # Append Sec_Fiber Properties into Section Lists
        return sec_fiber
    
    def _translate_sec_aggregator(self):
        data = self._reader.read(sheet_name="Sec_Aggregator", start_row=8) # Reading Sheet "Sec_Aggregator" in the Input file
        n = len(data)
        index = np.arange(n, dtype=np.int32)
        sec_name = np.empty(n, dtype="U32")
        aggregator_type = np.empty(n, dtype="U32")
        aggregated_sec_class = np.empty(n, dtype=np.int32)
        aggregated_sec_idx = np.empty(n, dtype=np.int32)
        base_mat_class = np.empty(n, dtype=np.int32)
        base_mat_idx = np.empty(n, dtype=np.int32)
        sec_model = np.empty(n, dtype="U15")
        properties = np.zeros((n, len(SectionAggregatorProperties)), dtype=np.float64)
        name_to_idx = {}
        for i, row in enumerate(data):
            name = str(row["Section Name"])
            if name in name_to_idx:
                raise ValidationError(f"Duplicate Section name '{name}'")
            name_to_idx[name] = index[i]
            sec_name[i] = name
            aggregator_type[i] = str(row["Aggregator Type"])
            sec_class, _, sec_idx = self._retrieve_section_index(str(row["Aggregated Section"]))
            aggregated_sec_class[i] = sec_class
            aggregated_sec_idx[i] = sec_idx
            mat_class, _, mat_idx = self._retrieve_material_index(str(row["Base Material"]))
            base_mat_class[i] = mat_class
            base_mat_idx[i] = mat_idx
            sec_model[i] = str(row["Section Model"])
        base_sec_props = get_section_properties(
            self._secs_list,
            aggregated_sec_class,
            aggregated_sec_idx,
            ["h", "b", "A", "Avy", "Avz", "Iz", "Iy", "Jxx"]
        )
        properties[:, SectionAggregatorProperties.h:SectionAggregatorProperties.Jxx+1] = base_sec_props
        sec_aggregator = Sec_Aggregator(
            index = index,
            sec_name = sec_name,
            aggregator_type = aggregator_type,
            aggregated_sec_class = aggregated_sec_class,
            aggregated_sec_idx = aggregated_sec_idx,
            base_mat_class = base_mat_class,
            base_mat_idx = base_mat_idx,
            sec_model = sec_model,
            properties = properties,
            name_to_idx = name_to_idx,
        ) # Defining dataclass for each frame section
        self._secs_list.append(sec_aggregator) # Append Sec_Aggregator Properties into Section Lists
        return sec_aggregator

    def _translate_slab_sections(self):
        data = self._reader.read(sheet_name="Slab Sections", start_row=6) # Reading Sheet "Slab Sections" in the Input file
        n = len(data)
        index = np.arange(n, dtype=np.int32)
        sec_name = np.empty(n, dtype="U32")
        base_mat_class = np.empty(n, dtype=np.int32)
        base_mat_idx = np.empty(n, dtype=np.int32)
        properties = np.zeros((n, len(SlabSectionProperties)), dtype=np.float64)
        name_to_idx = {}
        for i, row in enumerate(data):
            name = str(row["Section Name"])
            if name in name_to_idx:
                raise ValidationError(f"Duplicate Section name '{name}'")
            name_to_idx[name] = index[i]
            sec_name[i] = name
            mat_class, _, mat_idx = self._retrieve_material_index(str(row["Base Material"]))
            base_mat_class[i] = mat_class
            base_mat_idx[i] = mat_idx
            t = self._to_internalunit_length(row["t"])
            properties[i] = (t)
        slab_sections = SlabSections(
            index = index,
            sec_name = sec_name,
            base_mat_class = base_mat_class,
            base_mat_idx = base_mat_idx,
            properties = properties,
            name_to_idx = name_to_idx,
        ) # Defining dataclass for each slab section
        return slab_sections
    
    def _translate_point_objects(self):
        data = self._reader.read(sheet_name="Point Objects", start_row=8) # Reading Sheet "Point Objects" in the Input file
        n = len(data)
        index = np.arange(n, dtype=np.int32)
        unique_name = np.empty(n, dtype="U15")
        coords = np.empty((n, 3), dtype=np.float64)
        is_zero_length = np.empty(n, dtype=bool)
        name_to_idx = {}
        for i, row in enumerate(data):
            name = str(row["Unique Name"])
            if name in name_to_idx:
                raise ValidationError(f"Duplicate Point object name '{name}'")
            name_to_idx[name] = index[i]
            unique_name[i] = name
            coords[i] = (
                self._to_internalunit_length(row["X"]),
                self._to_internalunit_length(row["Y"]),
                self._to_internalunit_length(row["Z"]),
            )
            is_zero_length[i] = (str(row["Zero Length Element"]).strip().lower() == "yes")
        point_objects = PointObjects(
            index = index,
            unique_name = unique_name,
            coords = coords,
            is_zero_length = is_zero_length,
            name_to_idx = name_to_idx,
        ) # Defining dataclass for each point object
        storeys = self._generate_storeys(np.unique(coords[:, 2])) # Generating Storey data from Z-coordinate of nodes
        return point_objects, storeys

    def _translate_line_objects(self, point_objects):
        data = self._reader.read(sheet_name="Line Objects", start_row=12) # Reading Sheet "Line Objects" in the Input file
        n = len(data)
        index = np.arange(n, dtype=np.int32)
        unique_name = np.empty(n, dtype="U15")
        end_points_idx = np.empty((n, 2), dtype=np.int32)
        end_offset_option = np.empty(n, dtype="U22")
        end_offsets = np.empty((n, 2), dtype=np.float64)
        sec_class = np.empty(n, dtype=np.int32)
        sec_idx = np.empty(n, dtype=np.int32)
        length = np.empty(n, dtype=np.float64)
        centroids = np.empty((n, 3), dtype=np.float64)
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
                self._to_internalunit_length(0.0 if row["I-End Offset Length"] is None else row["I-End Offset Length"]),
                self._to_internalunit_length(0.0 if row["J-End Offset Length"] is None else row["J-End Offset Length"]),
            )
            sec_class[i], _, sec_idx[i] = self._retrieve_section_index(str(row["Section"]))
        i_coords = point_objects.coords[end_points_idx[:, 0]]
        j_coords = point_objects.coords[end_points_idx[:, 1]]
        d_vectors = j_coords - i_coords # Calculate direction vectors of the elements
        length = np.linalg.norm(d_vectors, axis=1) # Calculate full length of the elements
        centroids = (i_coords + j_coords) / 2.0 # Calculate centroid of the elements
        line_objects = LineObjects(
            index = index,
            unique_name = unique_name,
            end_points_idx = end_points_idx,
            end_offset_option = end_offset_option,
            end_offsets = end_offsets,
            sec_class = sec_class,
            sec_idx = sec_idx,
            length = length,
            centroids = centroids,
            name_to_idx = name_to_idx,
        ) # Defining dataclass for each line object
        return line_objects

    def _translate_surface_objects(self, line_objects, slab_sections):
        data = self._reader.read(sheet_name="Surface Objects", start_row=9) # Reading Sheet "Surface Objects" in the Input file
        n = len(data)
        index = np.arange(n, dtype=np.int32)
        unique_name = np.empty(n, dtype="U15")
        edges_idx = np.zeros((n, 4), dtype=np.int32)
        vertices_idx = np.zeros((n, 4), dtype=np.int32)
        sec_class = np.empty(n, dtype=np.int32)
        sec_idx = np.empty(n, dtype=np.int32)
        name_to_idx = {}
        for i, row in enumerate(data):
            name = str(row["Unique Name"])
            if name in name_to_idx:
                raise ValidationError(f"Duplicate Surface object name '{name}'")
            name_to_idx[name] = index[i]
            unique_name[i] = name
            edges_name = [edge for edge in (row["Edge 1"], row["Edge 2"], row["Edge 3"], row["Edge 4"],) if edge is not None]
            for j, edge_name in enumerate(edges_name):
                try:
                    edges_idx[i, j] = line_objects.name_to_idx[str(edge_name)]
                except KeyError:
                    raise ValidationError(
                        f"Surface '{name}' references undefined line '{edge_name}'."
                    )
            current_edges = edges_idx[i, :len(edges_name)]
            e1 = line_objects.end_points_idx[current_edges[0]]
            e2 = line_objects.end_points_idx[current_edges[1]]
            if e1[1] in e2:
                vertices = [e1[0], e1[1]]
            elif e1[0] in e2:
                vertices = [e1[1], e1[0]]
            else:
                raise ValidationError(
                    f"Surface '{name}' has connection edges that are not closed."
                )

            for edge_idx in current_edges[1:]:
                edge = line_objects.end_points_idx[edge_idx]
                current_vertex = vertices[-1]
                if edge[0] == current_vertex:
                    vertices.append(edge[1])
                elif edge[1] == current_vertex:
                    vertices.append(edge[0])
                else:
                    raise ValidationError(
                        f"Surface '{name}' has connection edges that are not closed."
                    )
            if vertices[0] != vertices[-1]:
                raise ValidationError(
                    f"Surface '{name}' has connection edges that are not closed."
                )
            vertices.pop()
            vertices_idx[i, :len(vertices)] = vertices
            sec_class[i], _, sec_idx[i] = self._retrieve_slabsection_index(str(row["Section"]), slab_sections)
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
    