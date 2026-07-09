from ._preproc_dataclass import ModelData
from ._exceltranslator import ExcelTranslator
from sadpropy.utility._filepath import get_filepath

__all__ = ["Model"]

class Model:
    def __init__(self):
        # FILE PATH
        parent_path, input_path, output_path, inputfile_path, logfile_path = get_filepath()
        self.parent_path = parent_path
        self.input_path = input_path
        self.output_path = output_path
        self.inputfile_path = inputfile_path
        self.logfile_path = logfile_path

        # TRANSLATE INPUTFILE AND STORE TO MODEL DATA
        translator = ExcelTranslator(inputfile_path)
        modeldata = translator.translate()
        self.data = ModelData(**modeldata)