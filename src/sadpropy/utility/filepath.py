from pathlib import Path
from datetime import datetime

class FilePath:
    def __init__(self):
        self.parent_path = Path(__file__).resolve().parent.parent
        self.input_path = self.parent_path / "io" / "input"
        self.output_path = self.parent_path / "io" / "output"
        self.inputfile_path = self.input_path / "model_inputfile.xlsx"
        self.logfile_path = self.output_path / f"logfile_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log"
