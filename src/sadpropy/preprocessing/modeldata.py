from ._preproc_dataclass import ModelDataclass
from ._exceltranslator import ExcelTranslator

__all__ = ["ModelData"]

class ModelData:
    def __init__(self):
        # TRANSLATE INPUTFILE AND STORE TO MODEL DATA
        self._translator_result = ExcelTranslator().translate()

    def retrieve(self):
        return ModelDataclass(**self._translator_result)