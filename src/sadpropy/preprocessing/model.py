from ..utility._exception import ValidationError
from ..visualisation.visualiser import Visualisation

class Model:
    def __init__(self, modeldata):
        self._modeldata = modeldata
        self._plot = None

    @property
    def plot(self):
        if self._plot is None:
            if len(self._modeldata.nodes.coords) == 0:
                raise ValidationError("The Model contains no objects")
            self._plot = Visualisation(self._modeldata)
        return self._plot