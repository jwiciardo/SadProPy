from sadpropy import *

modeldata = ModelData().retrieve()
filepath_information = modeldata.filepath_information
project_information = modeldata.project_information
analysis_preferences = modeldata.analysis_preferences
materials = modeldata.materials
mat_concrete04 = modeldata.mat_concrete04
mat_steel02 = modeldata.mat_steel02
mat_minmax = modeldata.mat_minmax
mat_imk = modeldata.mat_imk
materials_list = modeldata.materials_list
frame_sections = modeldata.frame_sections
sec_fiber = modeldata.sec_fiber
sec_aggregator = modeldata.sec_aggregator
sections_list = modeldata.sections_list
slab_sections = modeldata.slab_sections
storeys = modeldata.storeys
nodes = modeldata.nodes
beamcolumn_elements = modeldata.beamcolumn_elements
restraints = modeldata.restraints

vis = Visualisation(modeldata)
vis.plot_undeformed_model(view="Isometric", colour_by="Section", show_grids=True,
    show_nodes=True, show_elements=True, show_restraints=True, show_node_labels=False, show_element_labels=False,
    show_global_axes=True, show_local_axes=False)

print()
