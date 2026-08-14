from datetime import datetime

def get_filepath(inputfile_path):
    parent_path = inputfile_path.parent
    output_path = parent_path / "result"
    logfile_path = output_path / "log" / f"logfile_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log"
    return parent_path, output_path, logfile_path