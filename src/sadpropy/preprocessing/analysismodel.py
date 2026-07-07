class AnalysisModel:
    def __init__(self, modeldata):
        self.modeldata = modeldata
        self.project_information = modeldata.project_information
        self.user_unitsystem = modeldata.user_unitsystem
        self.analysis_preferences = modeldata.analysis_preferences
        self.materials = modeldata.materials
        self.sections = modeldata.sections
        self.nodes = modeldata.nodes