import numpy as np
import matplotlib.pyplot as plt
from .object._axes_object import _set_axes, _draw_global_axes, _draw_local_axes
from .object._grid_object import _draw_grid
from .object._node_object import _plot_nodes
from .object._element_object import _plot_elements
from .object._shell_object import _plot_shells
from .object._zerolengthelement_object import _plot_zerolength_elements
from .object._restraint_object import _plot_restraints
from .object._elementalload_object import _plot_elemental_loads

class Visualisation:
    def __init__(self, modeldata):
        self._modeldata = modeldata

        # General Data
        self._ndim = self._modeldata.project_information.ndim # Retrieve number of dimensional space
        self._storeys = self._modeldata.storeys # Retrieve storeys data
        self._materials = self._modeldata.materials # Retrieve materials data
        self._sections = self._modeldata.frame_sections # Retrieve frame sections data

        # Nodes
        self._nodes = self._modeldata.nodes # Retrieve nodes data
        self._coords = self._nodes.coords # Retrieve nodes coordinates data
        self._restraints = self._modeldata.restraints # Retrieve restraints data

        # Elements
        self._elements = self._modeldata.elements # Retrieve beam/column/brace elements data
        self._zerolength_elements = self._modeldata.zerolength_elements # Retrieve zero length elements data

        # Shells
        self._shells = self._modeldata.shells # Retrieve shells data

        # Loads
        self._nodal_loads = self._modeldata.nodal_loads # Retrieve nodal loads data
        self._concentrated_elemental_loads = self._modeldata.concentrated_elemental_loads # Retrieve concentrated elemental loads
        self._distributed_elemental_loads = self._modeldata.distributed_elemental_loads # Retrieve distributed elemental loads
        self._shell_to_elemental_loads = self._modeldata.shell_to_elemental_loads # Retrieve shell to elemental loads

        # Colour List
        self._colour_cycle = [
            "blue",
            "green",
            "red",
            "cyan",
            "yellow",
            "magenta",
            "tab:blue",
            "tab:green",
            "tab:red",
            "tab:orange",
            "tab:purple",
            "tab:brown",
            "tab:pink",
            "tab:gray",
            "tab:olive",
            "tab:cyan",
        ]

        # View Dictionary
        self._views = {
            "Isometric": (35, -120),
            "Front": (0, -90),
            "Back": (0, 90),
            "Left": (0, 180),
            "Right": (0, 0),
            "Top": (90, -90),
            "Bottom": (-90, -90),
        }

        # DOFs Symbol Dictionary
        self._dof_style = {
            "UX": {"offset": (-1, 0, 0), "marker": ">"},
            "UY": {"offset": (0, 1, 0), "marker": ">"},
            "UZ": {"offset": (0, 0, 1), "marker": "^"},
            "RX": {"offset": (1, 0, 0), "marker": "_"},
            "RY": {"offset": (0, -1, 0), "marker": "_"},
            "RZ": {"offset": (0, 0, -1), "marker": "|"},
        }

    # MAIN METHOD
    def undeformed_shape(
            self,
            view="Isometric",
            colour_by=None,
            show_grids=True,
            show_nodes=True,
            show_elements=True,
            show_shells=True,
            show_restraints=True,
            show_nodal_loads=True,
            show_elemental_loads=True,
            show_node_labels=True,
            show_element_labels=True,
            show_shell_labels=True,
            show_nodal_load_labels=False,
            show_elemental_load_labels=False,
            show_spring_hinges=False,
            show_end_releases=False,
            show_rigid_end_offsets=False,
            show_global_axes=True,
            show_local_axes=False,
            show_hinges_length=False,
            show_fiber_section=False,
        ):
        fig = plt.figure(figsize=(12, 8)) # Start plotting figure
        ax = fig.add_subplot(111, projection="3d") # Add axis in 3D
        title = "Undeformed Shape"
        
        _set_axes(ax=ax, title=title, view=view, coords=self._coords) # Set axes
        _draw_global_axes(ax=ax, ndim=self._ndim, coords=self._coords, show_axes=show_global_axes) # Set global axes arrows
        _draw_local_axes(ax=ax, elements=self._elements, show_axes=show_local_axes) # Set local axes arrows
        _draw_grid(ax=ax, ndim=self._ndim, storeys=self._storeys, coords=self._coords, show_grids=show_grids) # Set gridlines
        if show_nodes: # Set condition if show_nodes is True or False
            _plot_nodes(
                ax=ax,
                nodes=self._nodes,
                coords=self._coords,
                show_labels=show_node_labels,
            ) # Plot nodes if show_nodes is True
        if show_elements: # Set condition if show_elements is True or False
            _plot_elements(
                ax=ax,
                materials=self._materials,
                sections=self._sections,
                coords=self._coords,
                elements=self._elements,
                colour_by=colour_by,
                show_labels=show_element_labels,
                show_rigid_end_offsets=show_rigid_end_offsets,
            ) # Plot elements if show_elements is True
            _plot_zerolength_elements(
                ax=ax,
                coords=self._coords,
                zerolength_elements=self._zerolength_elements,
                rotation_matrices=self._zerolength_elements.rotation_matrices,
                show_labels=show_element_labels,
                show_hinges=show_spring_hinges,
            ) # Plot zero length elements if show_elements is True
        if show_shells: # Set condition if show_shells is True or False
            _plot_shells(
                ax=ax,
                coords=self._coords,
                shells=self._shells,
                show_labels=show_shell_labels,
            ) # Plot shells if show_shells is True
        if show_restraints: # Set condition if show_restraints is True or False
            _plot_restraints(
                ax=ax,
                coords=self._coords,
                rotation_matrix=np.eye(3), # Define rotation matrix as identity matrix
                restraints=self._restraints,
            ) # Plot nodes if show_restraints is True
        if show_elemental_loads: # Set condition if show_elemental_loads is True or False
            _plot_elemental_loads(
                ax=ax,
                coords=self._coords,
                elements=self._elements,
                distributed_loads=self._distributed_elemental_loads,
                concentrated_loads=self._concentrated_elemental_loads,
                rotation_matrices=self._elements.rotation_matrices,
                show_labels=show_elemental_load_labels,
                scale=1.0,
            ) # Plot loads if show_elemental_loads is True

        
        plt.tight_layout()
        plt.show()