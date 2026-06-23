from sadpropy.model.modeldata import ModelDataStorer

__all__ = ["Workspace"]

class Workspace:
    def __init__(self, paths):
        # FILE PATH
        self.parent_path = paths.parent_path
        self.input_path = paths.input_path
        self.output_path = paths.output_path
        self.inputfile_path = paths.inputfile_path
        self.logfile_path = paths.logfile_path

        # CALL CLASSES
        self.modeldatastorer = ModelDataStorer(self)

        # MODEL DATA
        self.modeldata = None
    
    # STORE MODEL DATA
    def store_model_data(self):
        self.modeldata = self.modeldatastorer.store_data()