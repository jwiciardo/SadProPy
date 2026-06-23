from sadpropy import *

paths = FilePath()
ws = Workspace(paths)
ws.store_model_data()
modeldata = ws.modeldata
project_information = modeldata.project_information
system_units = modeldata.units
analysis_preferences = modeldata.analysis_preferences
storey_data = modeldata.storey_data
point_coordinates = modeldata.point_coordinates
line_connectivity = modeldata.line_connectivity
surface_connectivity = modeldata.surface_connectivity
print(surface_connectivity)






