from ._preproc_dataclass import ModelData
from ._exceltranslator import ExcelTranslator
from sadpropy.utility._filepath import get_filepath

__all__ = ["Model"]

class Model:
    def __init__(self):
        # FILE PATH
        parent_path, input_path, output_path, inputfile_path, logfile_path = get_filepath()
        self.parent_path = parent_path
        self.input_path = input_path
        self.output_path = output_path
        self.inputfile_path = inputfile_path
        self.logfile_path = logfile_path

        # TRANSLATE INPUTFILE AND STORE TO MODEL DATA
        translator = ExcelTranslator(inputfile_path)
        modeldata = translator.translate()
        self.data = ModelData(
            project_information = modeldata["Project Information"],
            user_unitsystem = modeldata["User Specified Unitsystem"],
            analysis_preferences = modeldata["Analysis Preferences"],
            point_coordinates = modeldata["Point Coordinates"],
            storey_data = modeldata["Storey Data"],
            line_connectivity = modeldata["Line Connectivity"],
            surface_connectivity = modeldata["Surface Connectivity"],
            materials = modeldata["Materials"],
            mat_concrete04 = modeldata["Mat: Concrete04"],
            mat_steel02 = modeldata["Mat: Steel02"],
            mat_minmax = modeldata["Mat: MinMax"],
            mat_imk = modeldata["Mat: IMK Hinge"],
            frame_sections = modeldata["Frame Sections"],
            sec_fiber = modeldata["Sec: Fiber"],
            sec_aggregator = modeldata["Sec: Aggregator"],
            slab_sections = modeldata["Slab Sections"],
            nodes = modeldata["Nodes"],
        )