import warnings
from openpyxl import load_workbook

class InputReader:
    def __init__(self, inputfile_path):
        self.inputfile_path = inputfile_path
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message="Data Validation extension is not supported*"
            )
            self.workbook = load_workbook(inputfile_path, data_only=True)
    
    # CENTRAL FUNCTION: READER
    def read_inputfile(self, sheet_name, start_row=1):
        worksheet = self.workbook[sheet_name]
        rows = list(worksheet.values)
        headers = rows[start_row - 1]
        records = []
        for row in rows[start_row:]:
            record = dict(zip(headers, row))
            if all(value is None for value in record.values()): # Skip completely empty rows
                continue
            records.append(record)
        return records