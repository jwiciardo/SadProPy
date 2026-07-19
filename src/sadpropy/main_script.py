from sadpropy import *

modeldata = ModelData().retrieve()
materials = modeldata.materials
mat_concrete04 = modeldata.mat_concrete04
mat_steel02 = modeldata.mat_steel02
mat_minmax = modeldata.mat_minmax
mat_imk = modeldata.mat_imk
frame_sections = modeldata.frame_sections
sec_fiber = modeldata.sec_fiber
sec_aggregator = modeldata.sec_aggregator
slab_sections = modeldata.slab_sections
point_objects = modeldata.point_objects
line_objects = modeldata.line_objects
surface_objects = modeldata.surface_objects
storeys = modeldata.storeys
restraints = modeldata.restraints

model = StructuralModelData(modeldata).generate()
vis = Visualisation(modeldata)
#vis.plot_line_connectivity(colour_by="Section")

print(mat_minmax)