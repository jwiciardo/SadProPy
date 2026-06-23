from math import sqrt
from sadpropy.model.dataclasses import (
    ProjectInformation,
    AnalysisPreferences,
    PointCoordinates,
    LineConnectivity,
    SurfaceConnectivity
    )
from .units import UnitConverter, UnitRegistry, UnitSystem
from .exceptions import ValidationError
from .input_reader import InputReader
from .helper import create_storeys
from .operator import LengthfromCoordinate

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
        units = self.translate_units()
        self.units = units
        analysis_preferences = self.translate_analysis_preferences()
        point_coordinates, storey_elevations = self.translate_point_objects()
        storey_data = create_storeys(storey_elevations)
        line_connectivity = self.translate_line_objects(point_coordinates)
        surface_connectivity = self.translate_surface_objects(line_connectivity)

        #materials = self.translate_materials()
        #mat_concrete04 = self.translate_mat_concrete04(materials)
        #mat_steel02 = self.translate_mat_steel02(materials)
        #mat_minmax = self.translate_mat_minmax()
        return {
            "Project Information": project_information,
            "System Units": units,
            "Analysis Preferences": analysis_preferences,
            "Storey Data": storey_data,
            "Point Coordinates": point_coordinates,
            "Line Connectivity": line_connectivity,
            "Surface Connectivity": surface_connectivity,
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
    
    def translate_units(self):
        data = self.reader.read_inputfile(sheet_name="System Units", start_row=9) # Reading Sheet "System Units" in the Input file
        row = {r["Item"]: r["Value"] for r in data}
        units = UnitSystem(
                force = str(row["Force"]),
                length = str(row["Length"]),
                mass = str(row["Mass"]),
                stress = str(row["Stress"]),
                time = str(row["Time"]),
                angle = str(row["Angle"]),
        ) # Defining dictionary for units
        return units

    def translate_analysis_preferences(self):
        data = self.reader.read_inputfile(sheet_name="Analysis Preferences", start_row=6) # Reading Sheet "Analysis Preferences" in the Input file
        row = {r["Item"]: r["Value"] for r in data}
        analysis_preferences = AnalysisPreferences(
                nl_analysis = str(row["Nonlinear Analysis"]),
                pdelta = str(row["P-Delta"]),
                ll_mass_factor = float(row["LL Mass Factor"]),
        ) # Defining dictionary for analysis preferences
        return analysis_preferences
    
    def translate_point_objects(self):
        data = self.reader.read_inputfile(sheet_name="Point Objects", start_row=7) # Reading Sheet "Point Objects" in the Input file
        ids = [int(row["Point ID"]) for row in data]
        duplicates = {id for id in ids if ids.count(id) > 1}
        if duplicates:
            raise ValidationError(f"Duplicate Point IDs found: {sorted(duplicates)}")
        point_coordinates = {}
        for row in data: # Defining dictionary for each point object
            point_id, x_coord, y_coord, z_coord = row["Point ID"], row["X"], row["Y"], row["Z"]
            point_coordinates[int(point_id)] = PointCoordinates(
                point_id = int(point_id),
                x_coord = self.length(x_coord),
                y_coord = self.length(y_coord),
                z_coord = self.length(z_coord),
            )
        storey_elevations = sorted({self.length(row["Z"]) for row in data}) # Retrieving Storey elevation from point coordinates data
        return point_coordinates, storey_elevations
    
    def translate_line_objects(self, point_coordinates):
        data = self.reader.read_inputfile(sheet_name="Line Objects", start_row=6) # Reading Sheet "Line Objects" in the Input file
        ids = [int(row["Line ID"]) for row in data]
        duplicates = {id for id in ids if ids.count(id) > 1}
        if duplicates:
            raise ValidationError(f"Duplicate Line IDs found: {sorted(duplicates)}")
        line_connectivity = {}
        for row in data: # Defining dictionary for each line object
            line_id, i_end, j_end = row["Line ID"], row["I-End"], row["J-End"]
            vertex_i, vertex_j = point_coordinates[i_end], point_coordinates[j_end]
            i_coord = (vertex_i.x_coord, vertex_i.y_coord, vertex_i.z_coord)
            j_coord = (vertex_j.x_coord, vertex_j.y_coord, vertex_j.z_coord)
            length = LengthfromCoordinate(i_coord, j_coord)
            centroid_x = (vertex_i.x_coord + vertex_j.x_coord) / 2.0
            centroid_y = (vertex_i.y_coord + vertex_j.y_coord) / 2.0
            centroid_z = (vertex_i.z_coord + vertex_j.z_coord) / 2.0
            line_connectivity[int(line_id)] = LineConnectivity(
                line_id = int(line_id),
                i_end = int(i_end),
                j_end = int(j_end),
                length = self.length(length),
                centroid_x = self.length(centroid_x),
                centroid_y = self.length(centroid_y),
                centroid_z = self.length(centroid_z),
            )
        return line_connectivity
    
    def translate_surface_objects(self, line_connectivity):
        data = self.reader.read_inputfile(sheet_name="Surface Objects", start_row=8) # Reading Sheet "Surface Objects" in the Input file
        ids = [int(row["Surface ID"]) for row in data]
        duplicates = {id for id in ids if ids.count(id) > 1}
        if duplicates:
            raise ValidationError(f"Duplicate Surface IDs found: {sorted(duplicates)}")
        surface_connectivity = {}
        for row in data: # Defining dictionary for each surface object
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
            )
        return surface_connectivity

    #def translate_materials(self):
        data = self.reader.read_inputfile("Materials") # Reading Sheet "Materials" in the Input file
        ret = {}
        for row in data.to_dict("records"): # Defining dictionary for each material
            mat_name, mat_type = row["Name"], row["Type"]
            E, nu, Unitweight, fc, fy, fu = row["E"], row["nu"], row["Unitweight"], row["fc"], row["fy"], row["fu"], 
            G = E / (2 * (1 + nu))
            if mat_type == "Concrete":
                ret[str(mat_name)] = Materials(
                    name = str(mat_name),
                    type = str(mat_type),
                    E = self.stress(E),
                    nu = float(nu),
                    G = self.stress(G),
                    unitweight = self.unitweight(Unitweight),
                    fc = self.stress(fc),
                    fy = 0.0,
                    fu = 0.0,
                )
            elif mat_type == "Rebar" or mat_type == "Steel":
                ret[str(mat_name)] = Materials(
                    name = str(mat_name),
                    type = str(mat_type),
                    E = self.stress(E),
                    nu = float(nu),
                    G = self.stress(G),
                    unitweight = self.unitweight(Unitweight),
                    fc = 0.0,
                    fy = self.stress(fy),
                    fu = self.stress(fu),
                )
        return ret
    
    #def translate_mat_concrete04(self, Mats):
        data = self.reader.read_inputfile("Mat_Concrete04") # Reading Sheet "Mat_Concrete04" in the Input file
        ret = {}
        for row in data.to_dict("records"):
            mat_name, base_mat, mat_type, mat_model = row["Material Name"], row["Base Material"], row["Material Type"], row["Material Model"]
            fc, epsc, epscu, E, fct, et, beta = row["fc"], row["epsc"], row["epscu"], row["E"], row["fct"], row["et"], row["beta"]
            base_mat_data = Mats[base_mat]
            nu, G, Unitweight = base_mat_data.nu, base_mat_data.G, base_mat_data.unitweight
            Esec = fc / epsc
            et_default = fct / Esec
            ret[str(mat_name)] = Mat_Concrete04(
                name = str(mat_name),
                base_mat = str(base_mat),
                type = str(mat_type),
                model = str(mat_model),
                fc = self.Stress(-fc),
                epsc = float(-epsc),
                epscu = float(-epscu),
                fct = self.Stress(fct),
                et = float(et if et != 0.0 else et_default),
                beta = float(beta),
                E = self.Stress(E),
                nu = float(nu),
                G = float(G),
                Esec = self.Stress(Esec),
                unitweight = float(Unitweight),
            ) # Defining dictionary for each material
        return ret
    
    #def translate_mat_steel02(self, Mats):
        data = self.reader.read_inputfile("Mat_Steel02") # Reading Sheet "Mat_Steel02" in the Input file
        ret = {}
        for row in data.to_dict("records"):
            mat_name, base_mat, mat_type, mat_model = row["Material Name"], row["Base Material"], row["Material Type"], row["Material Model"]
            fy, fu, eu, E, b, R0, cR1, cR2 = row["fy"], row["fu"], row["eu"], row["E"], row["b"], row["R0"], row["cR1"], row["cR2"]
            base_mat_data = Mats[base_mat]
            nu, G, Unitweight = base_mat_data.nu, base_mat_data.G, base_mat_data.unitweight
            ey = fy / E
            eoffset = ey + 0.002
            Epy = (fu - fy) / (eu - eoffset)
            b_default = Epy / E
            ret[str(mat_name)] = Mat_Steel02(
                name = str(mat_name),
                base_mat = str(base_mat),
                type = str(mat_type),
                model = str(mat_model),
                fy = self.Stress(fy),
                fu = self.Stress(fu),
                ey = float(ey),
                eoffset = float(eoffset),
                eu = float(eu),
                E = self.Stress(E),
                nu = float(nu),
                G = float(G),
                Epy = self.Stress(Epy),
                b = float(b if b != 0.0 else b_default),
                R0 = float(R0),
                cR1 = float(cR1),
                cR2 = float(cR2),
                unitweight = float(Unitweight),
            ) # Defining dictionary for each material
        return ret
    
    #def translate_mat_minmax(self):
        data = self.reader.read_inputfile("Mat_MinMax") # Reading Sheet "Mat_MinMax" in the Input file
        ret = {}
        for row in data.to_dict("records"):
            mat_name, base_nl_mat, mat_type, mat_model = row["Material Name"], row["Base NL Material"], row["Material Type"], row["Material Model"]
            ec, et = row["ec"], row["et"]
            ret[str(mat_name)] = Mat_MinMax(
                name = str(mat_name),
                base_nl_mat = str(base_nl_mat),
                type = str(mat_type),
                model = str(mat_model),
                ec = float(-ec),
                et = float(et),
            ) # Defining dictionary for each material
        return ret