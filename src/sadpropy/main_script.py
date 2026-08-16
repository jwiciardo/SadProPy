import sadpropy as sa

#inputfile = r"D:\Projects\SadProPy\src\sadpropy\model_inputfile.xlsx"
inputfile = r"/Users/jwiciardo/Projects/SadProPy/src/sadpropy/model_inputfile.xlsx"
session = sa.start_session()
session.new()
session.open(inputfile_path=inputfile)
session.model().plot.undeformed_model(view="Isometric", colour_by="Section", show_grids=True,
    show_nodes=True, show_elements=False, show_restraints=True, show_node_labels=False, show_element_labels=False,
    show_global_axes=False, show_local_axes=False)
#print(session.model()._modeldata.nodes)

print()
