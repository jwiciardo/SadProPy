# %%
import sadpropy as sa

session = sa.start_session()

# %%
#inputfile = r"D:\Projects\SadProPy\src\sadpropy\model_inputfile.xlsx"
inputfile = r"/Users/jwiciardo/Projects/SadProPy/src/sadpropy/model_inputfile.xlsx"
#session.new()
session.open(inputfile_path=inputfile)
#print(session.model._modeldata.shell_to_elemental_loads)

# %%
session.model.analysis_model.generate()

# %%
session.model.plot.undeformed_shape(views=["3D", "XY", "XZ", "YZ"], show_grids=True,
    show_nodes=True,
    show_node_labels=True,
    show_global_axes=True, show_local_axes=False)
#session.model.plot.show()

#session.model.plot.undeformed_shape(view="Isometric", colour_by="Section", show_grids=True,
#    show_nodes=True, show_elements=True, show_shells=False, show_restraints=True, loadcase="Ex", load_scale=1.0, show_loads="n",
#    show_node_labels=False, show_element_labels=False, show_zerolengthelement_labels=False, show_shell_labels=False, show_load_labels=True,
#    show_spring_hinges=False, show_rigid_end_offsets=True,
#    show_global_axes=False, show_local_axes=False)

# %%