from pathlib import Path
from datetime import datetime

def get_filepath():
    parent_path = Path(__file__).resolve().parent.parent
    input_path = parent_path / "io" / "input"
    output_path = parent_path / "io" / "output"
    inputfile_path = input_path / "model_inputfile.xlsx"
    logfile_path = output_path / f"logfile_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log"
    return parent_path, input_path, output_path, inputfile_path, logfile_path