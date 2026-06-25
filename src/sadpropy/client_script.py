from sadpropy import FilePath, ModelDataStorer

paths = FilePath()
modeldata = ModelDataStorer(paths).store_model_data()
project_information = modeldata.project_information
system_units = modeldata.user_unitsystem
analysis_preferences = modeldata.analysis_preferences
storey_data = modeldata.storey_data
point_coordinates = modeldata.point_coordinates
line_connectivity = modeldata.line_connectivity
surface_connectivity = modeldata.surface_connectivity
materials = modeldata.materials
mat_concrete04 = modeldata.mat_concrete04
mat_steel02 = modeldata.mat_steel02
mat_minmax = modeldata.mat_minmax
mat_imk = modeldata.mat_imk
frame_sections = modeldata.frame_sections
sec_fiber = modeldata.sec_fiber
print(sec_fiber)
