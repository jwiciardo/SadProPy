from ..utility.exception import ValidationError
from ..core.analysis_model import AnalysisModel
from ..visualisation.visualiser import Visualisation

class Model:
    def __init__(self, modeldata):
        self._modeldata = modeldata
        self._analysis_model = None
        self._plot = None

    @property
    def analysis_model(self):
        if self._analysis_model is None:
            if len(self._modeldata.nodes.coords) == 0:
                raise ValidationError("The Model contains no objects")
            self._analysis_model = AnalysisModel(self._modeldata)
        return self._analysis_model
    
    @property
    def plot(self):
        if self._plot is None:
            if len(self._modeldata.nodes.coords) == 0:
                raise ValidationError("The Model contains no objects")
            self._plot = Visualisation(self._modeldata)
        return self._plot

