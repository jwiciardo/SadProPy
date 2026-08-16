from ..visualisation.visualiser import Visualisation

class Model:
    def __init__(self, modeldata):
        self._modeldata = modeldata
        self.plot = Visualisation(self._modeldata)