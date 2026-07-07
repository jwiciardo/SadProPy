from ._preprocessingclass import ModelData
from ._exceltranslator import ExcelTranslator
from sadpropy.utility._filepath import get_filepath

__all__ = ["Model", "retrieve_model_data"]

class Model:
    def __init__(self):
        # FILE PATH
        _, _, _, self.inputfile_path, _ = get_filepath()
        self.model = self._store_model_data()

    def _store_model_data(self):
        # TRANSLATE INPUTFILE AND STORE TO MODEL DATA
        translator = ExcelTranslator(self.inputfile_path)
        data = translator.translate_excel()
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
            nodes = data["Nodes"],
        )

    def retrieve_model_data(self):
        return self.model