import openseespy.opensees as ops
from ._ops_material import _define_material


class AnalysisModel:
    def __init__(self, modeldata):
        self._modeldata = modeldata

    # HELPER METHOD
    def _initialise_model(self, ndim):
        # Create Model
        ops.wipe() # Wipe all constructed objects, i.e. all components of the model
        if ndim == 3:
                    # 'basic', '-ndm', ndm,  '-ndf', ndf
            ops.model('basic', '-ndm', ndim, '-ndf', 6) # Defining model dimensions and number of dofs
        else:
                    # 'basic', '-ndm', ndm,  '-ndf', ndf
            ops.model('basic', '-ndm', ndim, '-ndf', 3) # Defining model dimensions and number of dofs

    # MAIN METHOD
    def generate(self):
        ndim = self._modeldata.project_information.ndim # Retrieve number of dimensional space
        self._initialise_model(ndim=ndim) # Initialise model
        _define_material(modeldata=self._modeldata) # Define material properties
        