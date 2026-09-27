from ..utility.exception import ValidationError

class Model:
    def __init__(self, modeldata):
        self._modeldata = modeldata

    @property
    def draw_node_objects(self, index, unique_name, coords):
        return self._modeldata

