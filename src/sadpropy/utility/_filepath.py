from pathlib import Path
from datetime import datetime

def get_filepath():
    parent_path = Path(__file__).resolve().parent.parent
    output_path = parent_path / "result"
    inputfile_path = parent_path / "model_inputfile.xlsx"
    logfile_path = output_path / f"logfile_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log"
    return parent_path, output_path, inputfile_path, logfile_path