from math import sqrt
from sadpropy.model.dataclasses import (
    ProjectInformation,
    AnalysisPreferences,
    PointCoordinates,
    LineConnectivity,
    SurfaceConnectivity,
    Materials,
    Mat_Concrete04,
    Mat_Steel02,
    Mat_MinMax,
    Mat_IMK,
    FrameSections,
    )
from .units import UnitConverter, UnitRegistry, UnitSystem
from .exceptions import ValidationError
from .input_reader import InputReader
from .helper import create_storeys
from .operator import CoordinateToLength, SectionProperties

__all__ = ["InputTranslator"]

class InputTranslator:
    def __init__(self, inputfile_path):
        self.reader = InputReader(inputfile_path)
        self.units = None
        self.unitregistry = UnitRegistry()
        self.unitconverter = UnitConverter(self.unitregistry)

    # UNIT CONVERTER METHODS
    def length(self, value):
        return self.unitconverter.to_internal_units(value, self.units.length)

    def force(self, value):
        return self.unitconverter.to_internal_units(value, self.units.force)
        
    def mass(self, value):
        return self.unitconverter.to_internal_units(value, self.units.mass)
        
    def stress(self, value):
        return self.unitconverter.to_internal_units(value, self.units.stress)
        
    def time(self, value):
        return self.unitconverter.to_internal_units(value, self.units.time)
        
    def angle(self, value):
        return self.unitconverter.to_internal_units(value, self.units.angle)
        
    def area(self, value):
        return self.unitconverter.to_internal_units(value, self.units.area())
        
    def volume(self, value):
        return self.unitconverter.to_internal_units(value, self.units.volume())
        
    def inertia(self, value):
        return self.unitconverter.to_internal_units(value, self.units.length4())
        
    def moment(self, value):
        return self.unitconverter.to_internal_units(value, self.units.moment())
        
    def unitweight(self, value):
        return self.unitconverter.to_internal_units(value, self.units.unitweight())
        
    def surface_load(self, value):
        return self.unitconverter.to_internal_units(value, self.units.surface_load())
        
    def distributed_line_load(self, value):
        return self.unitconverter.to_internal_units(value, self.units.distributed_line_load())
        
    def concentrated_line_load(self, value):
        return self.unitconverter.to_internal_units(value, self.units.concentrated_line_load())
        
    def point_load(self, value):
        return self.unitconverter.to_internal_units(value, self.units.point_load())
    
    # CENTRAL FUNCTION: TRANSLATOR
    def translate_inputfile(self):
        project_information = self.translate_project_information()
        user_unitsystem = self.translate_user_unitsystem()
        self.units = user_unitsystem
        analysis_preferences = self.translate_analysis_preferences()
        point_coordinates, storey_elevations = self.translate_point_objects()
        storey_data = create_storeys(storey_elevations)
        line_connectivity = self.translate_line_objects(point_coordinates)
        surface_connectivity = self.translate_surface_objects(line_connectivity)
        materials = self.translate_materials()
        mat_concrete04 = self.translate_mat_concrete04(materials)
        mat_steel02 = self.translate_mat_steel02(materials)
        materials_nl = (mat_concrete04, mat_steel02)
        mat_minmax = self.translate_mat_minmax(materials_nl)
        mat_imk = self.translate_mat_imk()
        frame_sections = self.translate_frame_sections()
        return {
            "Project Information": project_information,
            "User Specified Unitsystem": user_unitsystem,
            "Analysis Preferences": analysis_preferences,
            "Storey Data": storey_data,
            "Point Coordinates": point_coordinates,
            "Line Connectivity": line_connectivity,
            "Surface Connectivity": surface_connectivity,
            "Materials": materials,
            "Mat: Concrete04": mat_concrete04,
            "Mat: Steel02": mat_steel02,
            "Mat: MinMax": mat_minmax,
            "Mat: IMK Hinge": mat_imk,
            "Frame Sections": frame_sections,
        }

    # TRANSLATE FUNCTION
    def translate_project_information(self):
        data = self.reader.read_inputfile(sheet_name="Project Information", start_row=5) # Reading Sheet "Project Information" in the Input file
        row = {r["Item"]: r["Value"] for r in data}
        project_information = ProjectInformation(
                project_name = str(row["Project Name"]),
                project_desc = str(row["Project Description"]),
        ) # Defining dictionary for project information
        return project_information
    
    def translate_user_unitsystem(self):
        data = self.reader.read_inputfile(sheet_name="User Specified Unitsystem", start_row=9) # Reading Sheet "User Specified Unitsystem" in the Input file
        row = {r["Item"]: r["Value"] for r in data}
        user_unitsystem = UnitSystem(
                force = str(row["Force"]),
                length = str(row["Length"]),
                mass = str(row["Mass"]),
                stress = str(row["Stress"]),
                time = str(row["Time"]),
                angle = str(row["Angle"]),
        ) # Defining dictionary for units
        return user_unitsystem

    def translate_analysis_preferences(self):
        data = self.reader.read_inputfile(sheet_name="Analysis Preferences", start_row=7) # Reading Sheet "Analysis Preferences" in the Input file
        row = {r["Item"]: r["Value"] for r in data}
        analysis_preferences = AnalysisPreferences(
                nonlinear_analysis = str(row["Nonlinear Analysis"]),
                auto_zero_length = str(row["Zero Length Element (Auto)"]),
                pdelta = str(row["P-Delta"]),
                liveload_mass_factor = float(row["LL Mass Factor"]),
        ) # Defining dictionary for analysis preferences
        return analysis_preferences
    
    def translate_point_objects(self):
        data = self.reader.read_inputfile(sheet_name="Point Objects", start_row=7) # Reading Sheet "Point Objects" in the Input file
        ids = [int(row["Point ID"]) for row in data]
        duplicates = {id for id in ids if ids.count(id) > 1}
        if duplicates:
            raise ValidationError(f"Duplicate Point IDs found: {sorted(duplicates)}")
        point_coordinates = {}
        for row in data:
            point_id, x_coord, y_coord, z_coord = row["Point ID"], self.length(row["X"]), self.length(row["Y"]), self.length(row["Z"])
            point_coordinates[int(point_id)] = PointCoordinates(
                point_id = int(point_id),
                x_coord = float(x_coord),
                y_coord = float(y_coord),
                z_coord = float(z_coord),
            ) # Defining dictionary for each point object
        storey_elevations = sorted({self.length(row["Z"]) for row in data}) # Retrieving Storey elevation from point coordinates data
        return point_coordinates, storey_elevations
    
    def translate_line_objects(self, point_coordinates):
        data = self.reader.read_inputfile(sheet_name="Line Objects", start_row=11) # Reading Sheet "Line Objects" in the Input file
        ids = [int(row["Line ID"]) for row in data]
        duplicates = {id for id in ids if ids.count(id) > 1}
        if duplicates:
            raise ValidationError(f"Duplicate Line IDs found: {sorted(duplicates)}")
        line_connectivity = {}
        for row in data:
            line_id, i_end, j_end = row["Line ID"], row["I-End"], row["J-End"]
            end_offset, i_end_offset, j_end_offset = row["End Offset"], self.length(row["I-End Offset Length"]), self.length(row["J-End Offset Length"])
            vertex_i, vertex_j = point_coordinates[i_end], point_coordinates[j_end]
            i_coord = (vertex_i.x_coord, vertex_i.y_coord, vertex_i.z_coord)
            j_coord = (vertex_j.x_coord, vertex_j.y_coord, vertex_j.z_coord)
            length = CoordinateToLength(i_coord, j_coord)
            centroid_x = (vertex_i.x_coord + vertex_j.x_coord) / 2.0
            centroid_y = (vertex_i.y_coord + vertex_j.y_coord) / 2.0
            centroid_z = (vertex_i.z_coord + vertex_j.z_coord) / 2.0
            line_connectivity[int(line_id)] = LineConnectivity(
                line_id = int(line_id),
                i_end = int(i_end),
                j_end = int(j_end),
                end_offset = str(end_offset),
                i_end_offset = float(i_end_offset),
                j_end_offset = float(j_end_offset),
                length = float(length),
                centroid_x = float(centroid_x),
                centroid_y = float(centroid_y),
                centroid_z = float(centroid_z),
            ) # Defining dictionary for each line object
        return line_connectivity
    
    def translate_surface_objects(self, line_connectivity):
        data = self.reader.read_inputfile(sheet_name="Surface Objects", start_row=8) # Reading Sheet "Surface Objects" in the Input file
        ids = [int(row["Surface ID"]) for row in data]
        duplicates = {id for id in ids if ids.count(id) > 1}
        if duplicates:
            raise ValidationError(f"Duplicate Surface IDs found: {sorted(duplicates)}")
        surface_connectivity = {}
        for row in data:
            surface_id = row["Surface ID"]
            edges = [edge for edge in (row["Edge 1"], row["Edge 2"], row["Edge 3"], row["Edge 4"]) if edge is not None]
            n_edges = len(edges)
            edge_1, edge_2 = line_connectivity[edges[0]], line_connectivity[edges[1]]
            if edge_1.j_end in (edge_2.i_end, edge_2.j_end):
                vertices = [edge_1.i_end, edge_1.j_end]
            elif edge_1.i_end in (edge_2.i_end, edge_2.j_end):
                vertices = [edge_1.j_end, edge_1.i_end]
            else:
                raise ValidationError(f"Surface {surface_id} has connection edges that are not closed")
            for edge_id in edges[1:]:
                edge = line_connectivity[edge_id]
                current_vertex = vertices[-1]
                if edge.i_end == current_vertex:
                    vertices.append(edge.j_end)
                elif edge.j_end == current_vertex:
                    vertices.append(edge.i_end)
                else:
                    raise ValidationError(f"Surface {surface_id} has connection edges that are not closed")
            if vertices[0] != vertices[-1]:
                    raise ValidationError(f"Surface {surface_id} has connection edges that are not closed")
            vertices.pop()
            surface_connectivity[int(surface_id)] = SurfaceConnectivity(
                surface_id = int(surface_id),
                edges = tuple(edges),
                n_edges = int(n_edges),
                vertices = tuple(vertices),
            ) # Defining dictionary for each surface object
        return surface_connectivity

    def translate_materials(self):
        data = self.reader.read_inputfile(sheet_name="Materials", start_row=13) # Reading Sheet "Materials" in the Input file
        materials = {}
        for row in data: # Defining dictionary for each material
            mat_name, mat_type = row["Material Name"], row["Material Type"]
            E, nu, Unitweight, fc, fy, fu = self.stress(row["E"]), row["nu"], self.unitweight(row["Unitweight"]), self.stress(row["fc"]), self.stress(row["fy"]), self.stress(row["fu"]), 
            G = E / (2 * (1 + nu))
            if mat_type == "Concrete":
                materials[str(mat_name)] = Materials(
                    mat_name = str(mat_name),
                    mat_type = str(mat_type),
                    E = float(E),
                    nu = float(nu),
                    G = float(G),
                    unitweight = float(Unitweight),
                    fc = float(fc),
                    fy = 0.0,
                    fu = 0.0,
                )
            elif mat_type == "Rebar" or mat_type == "Steel":
                materials[str(mat_name)] = Materials(
                    mat_name = str(mat_name),
                    mat_type = str(mat_type),
                    E = float(E),
                    nu = float(nu),
                    G = float(G),
                    unitweight = float(Unitweight),
                    fc = 0.0,
                    fy = float(fy),
                    fu = float(fu),
                )
        return materials
    
    def translate_mat_concrete04(self, materials):
        data = self.reader.read_inputfile(sheet_name="Mat_Concrete04", start_row=13) # Reading Sheet "Mat_Concrete04" in the Input file
        mat_concrete04 = {}
        for row in data:
            mat_name, base_mat, mat_type, mat_model = row["Material Name"], row["Base Material"], row["Material Type"], row["Material Model"]
            fc, epsc, epscu, fct, et, beta = self.stress(row["fc"]), row["epsc"], row["epscu"], self.stress(row["fct"]), row["et"], row["beta"]
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
                fc = float(-fc),
                epsc = float(-epsc),
                epscu = float(-epscu),
                fct = float(fct),
                et = float(et if et != 0.0 else et_default),
                beta = float(beta),
            ) # Defining dictionary for each material
        return mat_concrete04
    
    def translate_mat_steel02(self, materials):
        data = self.reader.read_inputfile(sheet_name="Mat_Steel02", start_row=19) # Reading Sheet "Mat_Steel02" in the Input file
        mat_steel02 = {}
        for row in data:
            mat_name, base_mat, mat_type, mat_model = row["Material Name"], row["Base Material"], row["Material Type"], row["Material Model"]
            fy, fu, eu, b, R0, cR1, cR2= self.stress(row["fy"]), self.stress(row["fu"]), row["eu"], row["b"], row["R0"], row["cR1"], row["cR2"]
            a1, a2, a3, a4, f_init = row["a1"], row["a2"], row["a3"], row["a4"], self.stress(row['f_init'])
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
                fy = float(fy),
                fu = float(fu),
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
                f_init = float(f_init),
            ) # Defining dictionary for each material
        return mat_steel02
    
    def translate_mat_minmax(self, materials_nl):
        data = self.reader.read_inputfile(sheet_name="Mat_MinMax", start_row=9) # Reading Sheet "Mat_MinMax" in the Input file
        mat_minmax = {}
        for row in data:
            mat_name, base_nl_mat, mat_type, mat_model = row["Material Name"], row["Base NL Material"], row["Material Type"], row["Material Model"]
            ec_max, et_max = row["ecmax"], row["etmax"]
            for mats in materials_nl:
                if base_nl_mat in mats:
                    base_nl_mat_data = mats[base_nl_mat]
                    E, nu, G, Unitweight = base_nl_mat_data.E, base_nl_mat_data.nu, base_nl_mat_data.G, base_nl_mat_data.unitweight
                else:
                    continue
            mat_minmax[str(mat_name)] = Mat_MinMax(
                mat_name = str(mat_name),
                base_nl_mat = str(base_nl_mat),
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
    
    def translate_mat_imk(self):
        data = self.reader.read_inputfile(sheet_name="Mat_IMK", start_row=19) # Reading Sheet "Mat_IMK" in the Input file
        mat_imk = {}
        for row in data:
            mat_name, mat_type, mat_model = row["Material Name"], row["Material Type"], row["Material Model"]
            K0, as_pos, as_neg = self.moment(row["K0"]), row["as_Pos"], row["as_Neg"]
            my_pos, my_neg, mu_pos, mu_neg = self.moment(row["My_Pos"]), self.moment(row["My_Neg"]), self.moment(row["Mu_Pos"]), self.moment(row["Mu_Neg"])
            fpr_pos, fpr_neg, a_pinch, nfactor = row["Fpr_Pos"], row["Fpr_Neg"], row["A_pinch"], row["nFactor"]
            lamda_s, lamda_c, lamda_a, lamda_k, c_s, c_c, c_a, c_k = row["Lamda_S"], row["Lamda_C"], row["Lamda_A"], row["Lamda_K"], row["c_S"], row["c_C"], row["c_A"], row["c_K"]
            theta_p_pos, theta_p_neg, theta_pc_pos, theta_pc_neg, res_pos, res_neg = row["theta_p_Pos"], row["theta_p_Neg"], row["theta_pc_Pos"], row["theta_pc_Neg"], row["Res_Pos"], row["Res_Neg"]
            theta_u_pos, theta_u_neg, d_pos, d_neg = row["theta_u_Pos"], row["theta_u_Neg"], row["D_Pos"], row["D_Neg"]
            mat_imk[str(mat_name)] = Mat_IMK(
                mat_name = str(mat_name),
                mat_type = str(mat_type),
                mat_model = str(mat_model),
                K0 = float(K0),
                as_pos = float(as_pos),
                as_neg = float(as_neg),
                my_pos = float(my_pos),
                my_neg = float(my_neg),
                mu_pos = float(mu_pos),
                mu_neg = float(mu_neg),
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
    
    def translate_frame_sections(self):
        data = self.reader.read_inputfile(sheet_name="Frame Sections", start_row=16) # Reading Sheet "Frame Sections" in the Input file
        frame_sections = {}
        for row in data:
            sec_name, sec_shape, base_mat, sec_model, element_type = row["Section Name"], row["Section Shape"], row["Base Material"], row["Section Model"], row["Element Type"]
            h, b = self.length(row["h"]), self.length(row["b"])
            A, Avy, Avz, Iz, Iy, Jxx, alphaY, alphaZ = SectionProperties(row)
            k_A, k_Avy, k_Avz, k_Iz, k_Iy, k_Jxx = row["k_A"], row["k_Avy"], row["k_Avz"], row["k_Iz"], row["k_Iy"], row["k_Jxx"]
            frame_sections[str(sec_name)] = FrameSections(
                sec_name = str(sec_name),
                sec_shape = str (sec_shape),
                base_mat = str(base_mat),
                sec_model = str(sec_model),
                element_type = str(element_type),
                h = float(h),
                b = float(b),
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
