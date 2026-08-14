from sadpropy.preprocessing.model import Model

class Session:
    def __init__(self):
        self._model = None

    def new(self):
        model = Model()
        self._model = model
        return self._model

    def open(self, inputfile_path):
        model = Model().open(inputfile_path=inputfile_path)
        self._model = model
        return self._model

    def model(self):
        if self._model is None:
            raise RuntimeError("No active model. Create new() model or open() model first")
        return self._model

def start_session():
    return Session()