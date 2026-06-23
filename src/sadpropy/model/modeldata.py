from sadpropy.utility.input_translator import InputTranslator
#from utility.inputprocessor import InputProcessor
#from utility.modelvalidator import ModelValidator
from .dataclasses import ModelData

class ModelDataStorer:
    def __init__(self, workspace):
        self.ws = workspace
        self.translator = InputTranslator(self.ws.inputfile_path)
        #self.validator = ModelValidator()
    
    # CENTRAL FUNCTION: MODEL DATA STORER
    def store_data(self):
        # TRANSLATE INPUTFILE AND STORE TO MODELDATA
        data = self.translator.translate_inputfile()

        # PROCESS INPUTDATA AND STORE TO MODELDATA
        #self.processor = InputProcessor(data)
        #data_p = self.processor.process_inputdata()
        
        modeldata = ModelData(
            project_information = data["Project Information"],
            units = data["System Units"],
            analysis_preferences = data["Analysis Preferences"],
            point_coordinates = data["Point Coordinates"],
            storey_data = data["Storey Data"],
            line_connectivity = data["Line Connectivity"],
            surface_connectivity = data["Surface Connectivity"],
        )

        #self.validator._validate(modeldata)
        #print("Model successfully validated")
        return modeldata

