from pathlib import Path
from ..preprocessing.excel_translator import ExcelTranslator
from ..preprocessing.modeldata_storer import ModelDataStorer
from ..preprocessing.preprocessing_dataclass import ModelData
from ..preprocessing.model import Model

class Session:
    def __init__(self):
        self._model = None

    def new(self):
        modeldata = ModelData.empty()
        model = Model(modeldata=modeldata)
        self._model = model
        return self._model

    def open(self, inputfile_path):
        inputfile_path = Path(inputfile_path)
        if inputfile_path.suffix.lower() in [".xlsx", ".xls"]:
            translator = ExcelTranslator(inputfile_path=inputfile_path)
            data = translator.translate()
        modeldata = ModelDataStorer(translator_data=data).retrieve()
        model = Model(modeldata=modeldata)
        self._model = model
        return self._model

    def model(self):
        if self._model is None:
            raise RuntimeError("No active model. Create new() model or open() model first")
        return self._model

def start_session():
    return Session()