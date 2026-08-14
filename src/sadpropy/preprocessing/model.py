from pathlib import Path
from sadpropy.preprocessing.excel_translator import ExcelTranslator
from sadpropy.preprocessing.modeldata_storer import ModelDataStorer
from sadpropy.preprocessing.preprocessing_dataclass import ModelData

class Model:
    def __init__(self):
        self._modeldata = ModelData.empty()

    def open(self, inputfile_path):
        inputfile_path = Path(inputfile_path)
        if inputfile_path.suffix.lower() in [".xlsx", ".xls"]:
            translator = ExcelTranslator(inputfile_path=inputfile_path)
            data = translator.translate()
        modeldata = ModelDataStorer(data).retrieve()
        self._modeldata = modeldata
        return self
    