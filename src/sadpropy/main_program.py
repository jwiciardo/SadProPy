from sadpropy.workspace.workspace import Workspace
from sadpropy.utility.filepath import FilePath
from sadpropy.utility.input_reader import InputReader

paths = FilePath()
ws = Workspace(paths)
ws.store_model_data()
modeldata = ws.modeldata
project_information = modeldata.project_information
print(project_information)






