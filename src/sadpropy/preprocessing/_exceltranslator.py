import warnings
import numpy as np
from openpyxl import load_workbook
from ._preproc_dataclass import (
    ProjectInformation,
    AnalysisPreferences,
    Materials,
    FrameSections,
    SlabSections,
    PointObjects,
    LineObjects,
    SurfaceObjects,
    Storeys,
    Mat_Concrete04,
    Mat_Steel02,
    Mat_MinMax,
    Mat_IMK,
    Sec_Fiber,
    Sec_Aggregator,
    Nodes,
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
        user_unitsystem = self._translate_user_unitsystem()
        self._units = user_unitsystem
        analysis_preferences = self._translate_analysis_preferences()
        materials = self._translate_materials()
        frame_sections = self._translate_frame_sections()
        slab_sections = self._translate_slab_sections()
        point_objects, storeys = self._translate_point_objects()
        line_objects = self._translate_line_objects(point_objects)
        surface_objects = self._translate_surface_objects(line_objects)
        mat_concrete04 = self._translate_mat_concrete04(materials)
        mat_steel02 = self._translate_mat_steel02(materials)
        materials_list = (materials, mat_concrete04, mat_steel02)
        mat_minmax = self._translate_mat_minmax(materials_list)
        mat_imk = self._translate_mat_imk()
        sec_fiber = self._translate_sec_fiber(frame_sections, materials)
        sections_list = (frame_sections, sec_fiber)
        sec_aggregator = self._translate_sec_aggregator(sections_list)
        return {
            "project_information": project_information,
            "user_unitsystem": user_unitsystem,
            "analysis_preferences": analysis_preferences,
            "materials": materials,
            "frame_sections": frame_sections,
            "slab_sections": slab_sections,
            "storeys": storeys,
            "point_objects": point_objects,
            "line_objects": line_objects,
            "surface_objects": surface_objects,
            "mat_concrete04": mat_concrete04,
            "mat_steel02": mat_steel02,
            "mat_minmax": mat_minmax,
            "mat_imk": mat_imk,
            "sec_fiber": sec_fiber,
            "sec_aggregator": sec_aggregator,
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
    
    def _retrieve_unique_name(self, ids, objects): # Retrieve Unique name of the objects
        return objects.unique_names[ids - 1]
    
    # SUPPORTING METHODS
    def _translate_project_information(self):
        data = self._reader.read(sheet_name="Project Information", start_row=6) # Reading Sheet "Project Information" in the Input file
        values = {row["Item"]: row["Value"] for row in data}
        project_information = ProjectInformation(
                name = str(values["Project Name"]),
                desc = str(values["Project Description"]),
                ndim = int(3 if values["Model Dimensional Space"] == "3-Dimensional" else 2),
        ) # Defining dictionary for project information
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
        ) # Defining dictionary for units
        return user_unitsystem

    def _translate_analysis_preferences(self):
        data = self._reader.read(sheet_name="Analysis Preferences", start_row=6) # Reading Sheet "Analysis Preferences" in the Input file
        values = {row["Item"]: row["Value"] for row in data}
        analysis_preferences = AnalysisPreferences(
                nonlinear_analysis = str(values["Nonlinear Analysis"]),
                pdelta = str(values["P-Delta"]),
                liveload_mass_factor = float(values["LL Mass Factor"]),
        ) # Defining dictionary for analysis preferences
        return analysis_preferences

    def _translate_materials(self):
        data = self._reader.read(sheet_name="Materials", start_row=13) # Reading Sheet "Materials" in the Input file
        materials = {}
        for row in data: # Defining dictionary for each material
            mat_name, mat_type = row["Material Name"], row["Material Type"]
            E, nu, Unitweight, fc, fy, fu = row["E"], row["nu"], row["Unitweight"], row["fc"], row["fy"], row["fu"]
            G = E / (2 * (1 + nu))
            if mat_type == "Concrete":
                materials[str(mat_name)] = Materials(
                    mat_name = str(mat_name),
                    mat_type = str(mat_type),
                    E = float(self._to_internalunit_stress(E)),
                    nu = float(nu),
                    G = float(self._to_internalunit_stress(G)),
                    unitweight = float(self._to_internalunit_unitweight(Unitweight)),
                    fc = float(self._to_internalunit_stress(fc)),
                    fy = 0.0,
                    fu = 0.0,
                )
            elif mat_type == "Rebar" or mat_type == "Steel":
                materials[str(mat_name)] = Materials(
                    mat_name = str(mat_name),
                    mat_type = str(mat_type),
                    E = float(self._to_internalunit_stress(E)),
                    nu = float(nu),
                    G = float(self._to_internalunit_stress(G)),
                    unitweight = float(self._to_internalunit_unitweight(Unitweight)),
                    fc = 0.0,
                    fy = float(self._to_internalunit_stress(fy)),
                    fu = float(self._to_internalunit_stress(fu)),
                )
        return materials
    
    def _translate_frame_sections(self):
        data = self._reader.read(sheet_name="Frame Sections", start_row=16) # Reading Sheet "Frame Sections" in the Input file
        frame_sections = {}
        for row in data:
            sec_name, sec_shape, base_mat, sec_model, element_type = row["Section Name"], row["Section Shape"], row["Base Material"], row["Section Model"], row["Element Type"]
            h, b = row["h"], row["b"]
            A, Avy, Avz, Iz, Iy, Jxx, alphaY, alphaZ = section_properties(row)
            k_A, k_Avy, k_Avz, k_Iz, k_Iy, k_Jxx = row["k_A"], row["k_Avy"], row["k_Avz"], row["k_Iz"], row["k_Iy"], row["k_Jxx"]
            frame_sections[str(sec_name)] = FrameSections(
                sec_name = str(sec_name),
                sec_shape = str (sec_shape),
                base_mat = str(base_mat),
                sec_model = str(sec_model),
                element_type = str(element_type),
                h = float(self._to_internalunit_length(h)),
                b = float(self._to_internalunit_length(b)),
                A = float(k_A * A),
                Avy = float(k_Avy * Avy),
                Avz = float(k_Avz * Avz),
                Iz = float(k_Iz * Iz),
                Iy = float(k_Iy * Iy),
                Jxx = float(k_Jxx * Jxx),
                alphaY = float(alphaY),
                alphaZ = float(alphaZ),
            ) # Defining dictionary for each frame section
        return frame_sections
    
    def _translate_slab_sections(self):
        data = self._reader.read(sheet_name="Slab Sections", start_row=6) # Reading Sheet "Slab Sections" in the Input file
        slab_sections = {}
        for row in data:
            sec_name, base_mat, t = row["Section Name"], row["Base Material"], row["t"]
            slab_sections[str(sec_name)] = SlabSections(
                sec_name = str(sec_name),
                base_mat = str(base_mat),
                t = float(self._to_internalunit_length(t)),
            ) # Defining dictionary for each slab section
        return slab_sections
    
    def _translate_point_objects(self):
        data = self._reader.read(sheet_name="Point Objects", start_row=7) # Reading Sheet "Point Objects" in the Input file
        n = len(data)
        ids = np.arange(1, n + 1, dtype=np.int32)
        unique_names = np.empty(n, dtype="U15")
        coords = np.empty((n, 3), dtype=np.float64)
        uname_to_id = {}
        point_objects = {}
        for i, row in enumerate(data):
            uname = str(row["Unique Name"])
            if uname in uname_to_id:
                raise ValidationError(f"Duplicate Point object's name: {uname}")
            uname_to_id[uname] = ids[i]
            unique_names[i] = uname
            coords[i] = (
                self._to_internalunit_length(row["X"]),
                self._to_internalunit_length(row["Y"]),
                self._to_internalunit_length(row["Z"]),
            )
        point_objects = PointObjects(
            ids = ids,
            unique_names = unique_names,
            coords = coords,
            uname_to_id = uname_to_id,
        ) # Defining dictionary for each point object
        storeys = self._generate_storeys(np.unique(coords[:, 2])) # Generating Storey data from Z-coordinate of nodes
        return point_objects, storeys

    def _translate_line_objects(self, point_objects):
        data = self._reader.read(sheet_name="Line Objects", start_row=11) # Reading Sheet "Line Objects" in the Input file
        n = len(data)
        ids = np.arange(1, n + 1, dtype=np.int32)
        unique_names = np.empty(n, dtype="U15")
        end_point_ids = np.empty((n, 2), dtype=np.int32)
        end_offset_option = np.empty(n, dtype="U22")
        end_offsets = np.empty((n, 2), dtype=np.float64)
        length = np.empty(n, dtype=np.float64)
        centroids = np.empty((n, 3), dtype=np.float64)
        uname_to_id = {}
        line_objects = {}
        for i, row in enumerate(data):
            uname = str(row["Unique Name"])
            if uname in uname_to_id:
                raise ValidationError(f"Duplicate Line object's name: {uname}")
            uname_to_id[uname] = ids[i]
            unique_names[i] = uname
            end_point_ids[i] = (point_objects.uname_to_id[str(row["I-End"])], point_objects.uname_to_id[str(row["J-End"])],)
            end_offset_option[i] = str(row["End Offset"])
            end_offsets[i] = (
                self._to_internalunit_length(0.0 if row["I-End Offset Length"] is None else row["I-End Offset Length"]),
                self._to_internalunit_length(0.0 if row["J-End Offset Length"] is None else row["J-End Offset Length"]),
            )
        i_coords = point_objects.coords[end_point_ids[:, 0] - 1]
        j_coords = point_objects.coords[end_point_ids[:, 1] - 1]
        d_vectors = j_coords - i_coords # Calculate direction vectors of the elements
        length = np.linalg.norm(d_vectors, axis=1) # Calculate full length of the elements
        centroids = (i_coords + j_coords) / 2.0 # Calculate centroid of the elements
        line_objects = LineObjects(
            ids = ids,
            unique_names = unique_names,
            end_point_ids = end_point_ids,
            end_offset_option = end_offset_option,
            end_offsets = end_offsets,
            length = length,
            centroids = centroids,
            uname_to_id = uname_to_id,
        ) # Defining dictionary for each line object
        return line_objects

    def _translate_surface_objects(self, line_objects):
        data = self._reader.read(sheet_name="Surface Objects", start_row=8) # Reading Sheet "Surface Objects" in the Input file
        n = len(data)
        ids = np.arange(1, n + 1, dtype=np.int32)
        unique_names = np.empty(n, dtype="U15")
        edge_ids = np.zeros((n, 4), dtype=np.int32)
        vertex_ids = np.zeros((n, 4), dtype=np.int32)
        uname_to_id = {}
        surface_objects = {}
        for i, row in enumerate(data):
            uname = str(row["Unique Name"])
            if uname in uname_to_id:
                raise ValidationError(f"Duplicate Surface object's name: {uname}")
            uname_to_id[uname] = ids[i]
            unique_names[i] = uname
            edge_names = [
                edge
                for edge in (
                    row["Edge 1"],
                    row["Edge 2"],
                    row["Edge 3"],
                    row["Edge 4"],
                )
                if edge is not None
            ]

            for j, edge_name in enumerate(edge_names):
                try:
                    edge_ids[i, j] = line_objects.uname_to_id[str(edge_name)]
                except KeyError:
                    raise ValidationError(
                        f"Surface '{uname}' references undefined line '{edge_name}'."
                    )
            current_edges = edge_ids[i, :len(edge_names)]

            e1 = line_objects.end_point_ids[current_edges[0] - 1]
            e2 = line_objects.end_point_ids[current_edges[1] - 1]

            if e1[1] in e2:
                vertices = [e1[0], e1[1]]
            elif e1[0] in e2:
                vertices = [e1[1], e1[0]]
            else:
                raise ValidationError(
                    f"Surface '{uname}' has connection edges that are not closed."
                )

            for edge_id in current_edges[1:]:
                edge = line_objects.end_point_ids[edge_id - 1]
                current_vertex = vertices[-1]
                if edge[0] == current_vertex:
                    vertices.append(edge[1])
                elif edge[1] == current_vertex:
                    vertices.append(edge[0])
                else:
                    raise ValidationError(
                        f"Surface '{uname}' has connection edges that are not closed."
                    )

            if vertices[0] != vertices[-1]:
                raise ValidationError(
                    f"Surface '{uname}' has connection edges that are not closed."
                )
            vertices.pop()
            vertex_ids[i, :len(vertices)] = vertices

            surface_objects = SurfaceObjects(
                ids = ids,
                unique_names = unique_names,
                edge_ids = edge_ids,
                vertex_ids = vertex_ids,
                uname_to_id = uname_to_id,
            ) # Defining dictionary for each surface object
        return surface_objects

    def _translate_mat_concrete04(self, materials):
        data = self._reader.read(sheet_name="Mat_Concrete04", start_row=13) # Reading Sheet "Mat_Concrete04" in the Input file
        mat_concrete04 = {}
        for row in data:
            mat_name, base_mat, mat_type, mat_model = row["Material Name"], row["Base Material"], row["Material Type"], row["Material Model"]
            fc, epsc, epscu, fct, et, beta = row["fc"], row["epsc"], row["epscu"], row["fct"], row["et"], row["beta"]
            base_mat_data = materials[base_mat]
            E, nu, G, Unitweight = base_mat_data.E, base_mat_data.nu, base_mat_data.G, base_mat_data.unitweight
            Esec = fc / epsc
            et_default = fct / Esec
            mat_concrete04[str(mat_name)] = Mat_Concrete04(
                mat_name = str(mat_name),
                base_mat = str(base_mat),
                mat_type = str(mat_type),
                mat_model = str(mat_model),
                E = float(E),
                nu = float(nu),
                G = float(G),
                unitweight = float(Unitweight),
                fc = float(self._to_internalunit_stress(-fc)),
                epsc = float(-epsc),
                epscu = float(-epscu),
                fct = float(self._to_internalunit_stress(fct)),
                et = float(et if et != 0.0 else et_default),
                beta = float(beta),
            ) # Defining dictionary for each material
        return mat_concrete04

    def _translate_mat_steel02(self, materials):
        data = self._reader.read(sheet_name="Mat_Steel02", start_row=19) # Reading Sheet "Mat_Steel02" in the Input file
        mat_steel02 = {}
        for row in data:
            mat_name, base_mat, mat_type, mat_model = row["Material Name"], row["Base Material"], row["Material Type"], row["Material Model"]
            fy, fu, eu, b, R0, cR1, cR2 = row["fy"], row["fu"], row["eu"], row["b"], row["R0"], row["cR1"], row["cR2"]
            a1, a2, a3, a4, f_init = row["a1"], row["a2"], row["a3"], row["a4"], row['f_init']
            base_mat_data = materials[base_mat]
            E, nu, G, Unitweight = base_mat_data.E, base_mat_data.nu, base_mat_data.G, base_mat_data.unitweight
            ey = fy / E
            eoffset = ey + 0.002
            Epy = (fu - fy) / (eu - eoffset)
            b_default = Epy / E
            mat_steel02[str(mat_name)] = Mat_Steel02(
                mat_name = str(mat_name),
                base_mat = str(base_mat),
                mat_type = str(mat_type),
                mat_model = str(mat_model),
                E = float(E),
                nu = float(nu),
                G = float(G),
                unitweight = float(Unitweight),
                fy = float(self._to_internalunit_stress(fy)),
                fu = float(self._to_internalunit_stress(fu)),
                ey = float(ey),
                eu = float(eu),
                b = float(b if b != 0.0 else b_default),
                R0 = int(R0),
                cR1 = float(cR1),
                cR2 = float(cR2),
                a1 = float(a1),
                a2 = float(a2),
                a3 = float(a3),
                a4 = float(a4),
                f_init = float(self._to_internalunit_stress(f_init)),
            ) # Defining dictionary for each material
        return mat_steel02

    def _translate_mat_minmax(self, materials_list):
        data = self._reader.read(sheet_name="Mat_MinMax", start_row=9) # Reading Sheet "Mat_MinMax" in the Input file
        mat_minmax = {}
        for row in data:
            mat_name, base_nl_mat, mat_type, mat_model = row["Material Name"], row["Base NL Material"], row["Material Type"], row["Material Model"]
            ec_max, et_max = row["ecmax"], row["etmax"]
            for mats in materials_list:
                if base_nl_mat in mats:
                    base_nl_mat_data = mats[base_nl_mat]
                    E, nu, G, Unitweight = base_nl_mat_data.E, base_nl_mat_data.nu, base_nl_mat_data.G, base_nl_mat_data.unitweight
                else:
                    continue
            mat_minmax[str(mat_name)] = Mat_MinMax(
                mat_name = str(mat_name),
                base_nonlinear_mat = str(base_nl_mat),
                mat_type = str(mat_type),
                mat_model = str(mat_model),
                E = float(E),
                nu = float(nu),
                G = float(G),
                unitweight = float(Unitweight),
                ec_max = float(-ec_max),
                et_max = float(et_max),
            ) # Defining dictionary for each material
        return mat_minmax
    
    def _translate_mat_imk(self):
        data = self._reader.read(sheet_name="Mat_IMK", start_row=19) # Reading Sheet "Mat_IMK" in the Input file
        mat_imk = {}
        for row in data:
            mat_name, mat_type, mat_model = row["Material Name"], row["Material Type"], row["Material Model"]
            K0, as_pos, as_neg = row["K0"], row["as_Pos"], row["as_Neg"]
            my_pos, my_neg, mu_pos, mu_neg = row["My_Pos"], row["My_Neg"], row["Mu_Pos"], row["Mu_Neg"]
            fpr_pos, fpr_neg, a_pinch, nfactor = row["Fpr_Pos"], row["Fpr_Neg"], row["A_pinch"], row["nFactor"]
            lamda_s, lamda_c, lamda_a, lamda_k, c_s, c_c, c_a, c_k = row["Lamda_S"], row["Lamda_C"], row["Lamda_A"], row["Lamda_K"], row["c_S"], row["c_C"], row["c_A"], row["c_K"]
            theta_p_pos, theta_p_neg, theta_pc_pos, theta_pc_neg, res_pos, res_neg = row["theta_p_Pos"], row["theta_p_Neg"], row["theta_pc_Pos"], row["theta_pc_Neg"], row["Res_Pos"], row["Res_Neg"]
            theta_u_pos, theta_u_neg, d_pos, d_neg = row["theta_u_Pos"], row["theta_u_Neg"], row["D_Pos"], row["D_Neg"]
            mat_imk[str(mat_name)] = Mat_IMK(
                mat_name = str(mat_name),
                mat_type = str(mat_type),
                mat_model = str(mat_model),
                K0 = float(self._to_internalunit_rotational_stiffness(K0)),
                as_pos = float(as_pos),
                as_neg = float(as_neg),
                my_pos = float(self._to_internalunit_moment(my_pos)),
                my_neg = float(self._to_internalunit_moment(my_neg)),
                mu_pos = float(self._to_internalunit_moment(mu_pos)),
                mu_neg = float(self._to_internalunit_moment(mu_neg)),
                fpr_pos = float(fpr_pos),
                fpr_neg = float(fpr_neg),
                a_pinch = float(a_pinch),
                nfactor = float(nfactor),
                lamda_s = float(lamda_s),
                lamda_c = float(lamda_c),
                lamda_a = float(lamda_a),
                lamda_k = float(lamda_k),
                c_s = float (c_s),
                c_c = float(c_c),
                c_a = float(c_a),
                c_k = float(c_k),
                theta_p_pos = float(theta_p_pos),
                theta_p_neg = float(theta_p_neg),
                theta_pc_pos = float(theta_pc_pos),
                theta_pc_neg = float(theta_pc_neg),
                res_pos = float(res_pos),
                res_neg = float(res_neg),
                theta_u_pos = float(theta_u_pos),
                theta_u_neg = float(theta_u_neg),
                d_pos = float(d_pos),
                d_neg = float(d_neg),
            ) # Defining dictionary for each material
        return mat_imk
    
    def _translate_sec_fiber(self, frame_sections, materials):
        data = self._reader.read(sheet_name="Sec_Fiber", start_row=18) # Reading Sheet "Sec_Fiber" in the Input file
        sec_fiber = {}
        for row in data:
            sec_name, base_sec, integration_type = row["Section Name"], row["Base Section"], row["Integration Type"]
            mat_1, mat_2, mat_3, sec_model = row["Material 1"], row["Material 2"], row["Material 3"], row["Section Model"]
            cover, nbars_top, nbars_bot, nbars_int = row["cover"], row["nBarsTop"], row["nBarsBot"], row["nBarsInt"]
            bar_dia_hoop, bar_dia_top, bar_dia_bot, bar_dia_int = row["barDiaHoop"], row["barDiaTop"], row["barDiaBot"], row["barDiaInt"]
            base_sec_data = frame_sections[base_sec]
            h, b, sec_shape, base_mat = base_sec_data.h, base_sec_data.b, base_sec_data.sec_shape, base_sec_data.base_mat
            base_mat_data = materials[base_mat]
            mat_type = base_mat_data.mat_type
            row["h"], row["b"], row["Section Shape"], row["Material Type"] = h, b, sec_shape, mat_type
            A, Avy, Avz, Iz, Iy, Jxx, Abar_top, Abar_bot, Abar_int = fibersection_properties(row)
            sec_fiber[str(sec_name)] = Sec_Fiber(
                sec_name = str(sec_name),
                base_sec = str(base_sec),
                integration_type = str(integration_type),
                mat_type = str(mat_type),
                mat_1 = str(mat_1),
                mat_2 = str(mat_2),
                mat_3 = str(mat_3),
                sec_model = str(sec_model),
                h = float(h),
                b = float(b),
                cover = float(self._to_internalunit_length(cover)),
                nbars_top = int(nbars_top),
                nbars_bot = int(nbars_bot),
                nbars_int = int(nbars_int),
                bar_dia_hoop = float(self._to_internalunit_length(bar_dia_hoop)),
                bar_dia_top = float(self._to_internalunit_length(bar_dia_top)),
                bar_dia_bot = float(self._to_internalunit_length(bar_dia_bot)),
                bar_dia_int = float(self._to_internalunit_length(bar_dia_int)),
                A = float(A),
                Avy = float(Avy),
                Avz = float(Avz),
                Iz = float(Iz),
                Iy = float(Iy),
                Jxx = float(Jxx),
                Abar_top = float(Abar_top),
                Abar_bot = float(Abar_bot),
                Abar_int = float(Abar_int),
            ) # Defining dictionary for each frame section
        return sec_fiber
    
    def _translate_sec_aggregator(self, sections_list):
        data = self._reader.read(sheet_name="Sec_Aggregator", start_row=8) # Reading Sheet "Sec_Aggregator" in the Input file
        sec_aggregator = {}
        for row in data:
            sec_name, aggregated_sec, base_mat, sec_model, aggregator_type = row["Section Name"], row["Aggregated Section"], row["Base Material"], row["Section Model"], row["Aggregator Type"]
            for sections in sections_list:
                if aggregated_sec in sections:
                    aggregated_sec_data = sections[aggregated_sec]
                    h, b, A, Avy, Avz, Iz, Iy, Jxx = aggregated_sec_data.h, aggregated_sec_data.b, aggregated_sec_data.A, aggregated_sec_data.Avy, aggregated_sec_data.Avz, aggregated_sec_data.Iz, aggregated_sec_data.Iy, aggregated_sec_data.Jxx
                else:
                    continue
            sec_aggregator[str(sec_name)] = Sec_Aggregator(
                sec_name = str(sec_name),
                aggregated_sec = str(aggregated_sec),
                base_mat = str(base_mat),
                sec_model = str(sec_model),
                aggregator_type = str(aggregator_type),
                h = float(h),
                b = float(b),
                A = float(A),
                Avy = float(Avy),
                Avz = float(Avz),
                Iz = float(Iz),
                Iy = float(Iy),
                Jxx = float(Jxx),
            ) # Defining dictionary for each frame section
        return sec_aggregator
