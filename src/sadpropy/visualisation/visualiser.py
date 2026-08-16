import numpy as np
import matplotlib.pyplot as plt
from .object._axes_object import _set_axes, _draw_global_axes, _draw_local_axes
from .object._grid_object import _draw_grid
from .object._node_object import _plot_nodes
from .object._element_object import _plot_elements
from .object._zerolengthelement_object import _plot_zerolength_elements
from .object._restraint_object import _plot_restraints

class Visualisation:
    def __init__(self, modeldata):
        self._modeldata = modeldata

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

    # HELPER METHOD
    
    

    # MAIN METHOD
    def undeformed_model(
            self,
            view="Isometric",
            colour_by=None,
            show_grids=True,
            show_nodes=True,
            show_elements=True,
            show_restraints=True,
            show_node_labels=True,
            show_element_labels=True,
            show_spring_hinges=False,
            show_end_releases=False,
            show_end_length_offsets=False,
            show_global_axes=True,
            show_local_axes=False,
            show_finite_length_hinges=False,
            show_fiber_section=False,
        ):
        fig = plt.figure(figsize=(12, 8)) # Start plotting figure
        ax = fig.add_subplot(111, projection="3d") # Add axis in 3D

        # General Data
        title = "UNDEFORMED MODEL"
        ndim = self._modeldata.project_information.ndim # Retrieve number of dimensional space
        storeys = self._modeldata.storeys # Retrieve storeys data
        materials = self._modeldata.materials # Retrieve materials data
        sections = self._modeldata.frame_sections # Retrieve frame sections data

        # Nodes
        nodes = self._modeldata.nodes # Retrieve nodes data
        coords = nodes.coords # Retrieve nodes coordinates data
        restraints = self._modeldata.restraints # Retrieve restraints data

        # Elements
        elements = self._modeldata.elements # Retrieve beam column elements data
        zerolength_elements = self._modeldata.zerolength_elements # Retrieve zero length elements data
        
        _set_axes(ax=ax, title=title, view=view, coords=coords) # Set axes
        _draw_global_axes(ax=ax, ndim=ndim, coords=coords, show_axes=show_global_axes) # Set global axes arrows
        _draw_local_axes(ax=ax, elements=elements, show_axes=show_local_axes) # Set local axes arrows
        _draw_grid(ax=ax, ndim=ndim, storeys=storeys, coords=coords, show_grids=show_grids) # Set gridlines
        if show_nodes: # Set condition if show_nodes is True or False
            _plot_nodes(
                ax=ax,
                nodes=nodes,
                coords=coords,
                show_labels=show_node_labels,
            ) # Plot nodes if show_nodes is True
        if show_elements: # Set condition if show_elements is True or False
            _plot_elements(
                ax=ax,
                materials=materials,
                sections=sections,
                coords=coords,
                elements=elements,
                colour_by=colour_by,
                show_labels=show_element_labels,
            ) # Plot nodes if show_elements is True
            _plot_zerolength_elements(
                ax=ax,
                coords=coords,
                zerolength_elements=zerolength_elements,
                rotation_matrices=zerolength_elements.rotation_matrices,
                show_labels=show_element_labels,
            )
        if show_restraints: # Set condition if show_restraints is True or False
            _plot_restraints(
                ax=ax,
                coords=coords,
                rotation_matrix=np.eye(3), # Define rotation matrix as identity matrix
                restraints=restraints,
            ) # Plot nodes if show_restraints is True
        
        plt.tight_layout()
        plt.show()