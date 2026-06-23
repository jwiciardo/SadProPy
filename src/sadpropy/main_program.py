import os
from sadpropy.utility.filepath import FilePath
from sadpropy.utility.input_reader import InputReader

##########################################################################################################################
## JOB DETAILS                                                                                                          ##
##########################################################################################################################
#scriptname = os.path.splitext(os.path.basename(__file__))[0] # Filename of this python's script
#logfilename = output_path + os.sep + f'{scriptname}.log' # Filename of log file

paths = FilePath()
print(paths.logfile_path)
reader = InputReader(paths.inputfile_path)
project_information = reader.read_inputfile("Project Information", 5)
print(project_information)






