import os
from workspace.workspace import Workspace

##########################################################################################################################
## JOB DETAILS                                                                                                          ##
##########################################################################################################################
home_path = './DISSERTATION' # Job's home folder
output_path = home_path + os.sep + 'OUTPUT SNI' # Job's output folder
inputfile_path = home_path + os.sep + 'model_inputfile.xlsx' # Filename of Input Model which placed at the same folder as python file
scriptname = os.path.splitext(os.path.basename(__file__))[0] # Filename of this python's script
logfilename = output_path + os.sep + f'{scriptname}.log' # Filename of log file

ws = Workspace(home_path, output_path, inputfile_path, scriptname, logfilename)
ws.store_model_data()

modeldata = ws.modeldata
project_information = modeldata.project_information
system_units = modeldata.units
analysis_preferences = modeldata.analysis_preferences
storey_data = modeldata.storey_data
point_coordinates = modeldata.point_coordinates
line_connectivity = modeldata.line_connectivity
surface_connectivity = modeldata.surface_connectivity
#area_connectivity = modeldata.area_connectivity
#materials = modeldata.materials
print(surface_connectivity)


