from .dataclasses import ModelData
from sadpropy.utility.input_translator import InputTranslator

__all__ = ["ModelDataStorer"]

class ModelDataStorer:
    def __init__(self, paths):
        # FILE PATH
        self.parent_path = paths.parent_path
        self.input_path = paths.input_path
        self.output_path = paths.output_path
        self.inputfile_path = paths.inputfile_path
        self.logfile_path = paths.logfile_path

        # TRANSLATE AND VALIDATE INPUTFILE
        self.translator = InputTranslator(self.inputfile_path)
    
    # CENTRAL FUNCTION: MODEL DATA STORER
    def store_model_data(self):
        # TRANSLATE INPUTFILE AND STORE TO MODELDATA
        data = self.translator.translate_inputfile()
        
        return ModelData(
            project_information = data["Project Information"],
            user_unitsystem = data["User Specified Unitsystem"],
            analysis_preferences = data["Analysis Preferences"],
            point_coordinates = data["Point Coordinates"],
            storey_data = data["Storey Data"],
            line_connectivity = data["Line Connectivity"],
            surface_connectivity = data["Surface Connectivity"],
            materials = data["Materials"],
            mat_concrete04 = data["Mat: Concrete04"],
            mat_steel02 = data["Mat: Steel02"],
            mat_minmax = data["Mat: MinMax"],
            mat_imk = data["Mat: IMK Hinge"],
            frame_sections = data["Frame Sections"],
            sec_fiber = data["Sec: Fiber"],
            sec_aggregator = data["Sec: Aggregator"],
            slab_sections = data["Slab Sections"],
        )

