from pathlib import Path
from ..preprocessing.excel_translator import ExcelTranslator
from ..preprocessing.modeldata_storer import ModelDataStorer
from ..preprocessing.preprocessing_dataclass import ModelData
from ..preprocessing.model import Model
from ..utility.exception import ValidationError
from ..core.analysis_model import AnalysisModel
from ..visualisation.visualiser import Visualisation

class Session:
    def __init__(self):
        self._model = None
        self._analysis_model = None
        self._plot = None

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

    @property
    def model(self):
        if self._model is None:
            raise RuntimeError("No active model. Create new() model or open() model first")
        return self._model

    @property
    def analysis_model(self):
        if self._analysis_model is None:
            if len(self._model._modeldata.nodes.coords) == 0:
                raise ValidationError("The Model contains no objects")
            self._analysis_model = AnalysisModel(self._model._modeldata)
        return self._analysis_model
    
    @property
    def plot(self):
        if self._plot is None:
            if len(self._model._modeldata.nodes.coords) == 0:
                raise ValidationError("The Model contains no objects")
            self._plot = Visualisation(self._model._modeldata)
        return self._plot

def start_session():
    return Session()