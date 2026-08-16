import sadpropy as sa

#inputfile = r"D:\Projects\SadProPy\src\sadpropy\model_inputfile.xlsx"
inputfile = r"/Users/jwiciardo/Projects/SadProPy/src/sadpropy/model_inputfile.xlsx"
session = sa.start_session()
session.new()
session.open(inputfile_path=inputfile)
#print(session.model()._modeldata.frame_sections)

session.model().plot.undeformed_model(view="Isometric", colour_by="Material", show_grids=True,
    show_nodes=True, show_elements=True, show_restraints=True, show_node_labels=False, show_element_labels=False,
    show_global_axes=False, show_local_axes=False)

print()
