# %%
import sadpropy as sa

session = sa.start_session()

# %%
#inputfile = r"D:\Projects\SadProPy\src\sadpropy\model_inputfile.xlsx"
inputfile = r"/Users/jwiciardo/Projects/SadProPy/src/sadpropy/model_inputfile.xlsx"
#session.new()
session.open(inputfile_path=inputfile)
#print(session.model._modeldata.distributed_elemental_loads)

# %%
session.model.plot.undeformed_shape(view="Isometric", colour_by="Section", show_grids=True,
    show_nodes=True, show_elements=True, show_shells=True, show_restraints=True, loadcase="Dead", show_loads="Elemental",
    show_node_labels=False, show_element_labels=False, show_zerolengthelement_labels=False, show_shell_labels=False, show_load_labels=False,
    show_spring_hinges=False, show_rigid_end_offsets=True,
    show_global_axes=False, show_local_axes=False)

# %%
