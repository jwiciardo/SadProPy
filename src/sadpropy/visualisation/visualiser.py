import numpy as np
import matplotlib.pyplot as plt
from ._visualisation_definition import _view_definitions, _loadcase_type, _load
from .object._axes_object import _set_axes, _draw_global_axes, _draw_local_axes
from .object._grid_object import _draw_grid
from .object._node_object import _plot_nodes
from .object._element_object import _plot_elements
from .object._shell_object import _plot_shells
from .object._zero_length_element_object import _plot_zerolength_elements
from .object._restraint_object import _plot_restraints
from .object._nodal_load_object import _plot_nodal_loads
from .object._elemental_load_object import _plot_elemental_loads
from .object._shell_to_elemental_load_object import _plot_shell_to_elemental_loads
from ..preprocessing.preprocessing_class_index import LoadCaseType
from ..utility.exception import ValidationError

class Visualisation:
    def __init__(self, modeldata):
        self._modeldata = modeldata
        self._plots = {}
        self._selected_planes = {"XY": None, "XZ": None, "YZ": None}

        # General Data
        self._ndim = self._modeldata.project_information.ndim # Retrieve number of dimensional space
        self._units = self._modeldata.userdefined_units # Retrieve userdefined units
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

    # HELPER METHOD
    def _project_coords(self, coords, view_info):
        if view_info["projection"] == "3d":
            return coords
        axes = view_info["axes"]
        return coords[:, axes]

    def _create_figure(self, view_info):
        fig = plt.figure(figsize=(12, 8)) # Start plotting figure
        if view_info["projection"] == "3d":
            ax = fig.add_subplot(111, projection="3d")
            ax.view_init(elev=view_info["elev"], azim=view_info["azim"]) # Set viewing angle
        else:
            ax = fig.add_subplot(111)
        return fig, ax
    
    def _plot_model(
            self,
            ax,
            view,
            show_grids,
            show_nodes,
            show_node_labels,
            show_global_axes,
            show_local_axes,
        ):
        view_info = _view_definitions[view]
        projection_coords = self._project_coords(coords=self._coords, view_info=view_info)
        if view_info["projection"] == "3d":
            selected_plane = None
        else:
            selected_plane = self._selected_planes[view_info["plane"]]
        _set_axes(ax=ax, view_info=view_info, coords=self._coords) # Set axes
        if show_global_axes: # Set condition if show_global_axes is True or False
            _draw_global_axes(ax=ax, view_info=view_info, coords=projection_coords) # Set global axes arrows
        if show_local_axes: # Set condition if show_local_axes is True or False
            _draw_local_axes(ax=ax, view_info=view_info, elements=self._elements, show_axes=show_local_axes) # Set local axes arrows
        if show_grids:
            _draw_grid(ax=ax, view_info=view_info, storeys=self._storeys, coords=projection_coords) # Set gridlines
        if show_nodes: # Set condition if show_nodes is True or False
            _plot_nodes(
                ax=ax,
                view_info=view_info,
                nodes=self._nodes,
                coords=self._coords,
                projection_coords=projection_coords,
                plane=selected_plane,
                show_labels=show_node_labels,
            ) # Plot nodes if show_nodes is True

    def _get_available_planes(self, view_info):
        if view_info["projection"] == "3d":
            return None
        perpendicular_idx = view_info["perpendicular"]
        planes = np.unique(self._coords[:, perpendicular_idx])
        return planes

    def _refresh_view(self, view):
        plot = self._plots[view]
        fig = plot["fig"]
        ax = plot["ax"]
        ax.clear() # Clear existing drawing
        view_info = _view_definitions[view] # Retrieve view definition
        self._plot_model(
            ax=ax,
            view_info=view_info,
            show_grids=plot["show_grids"],
            show_nodes=plot["show_nodes"],
            show_node_labels=plot["show_node_labels"],
            show_global_axes= plot["show_global_axes"],
            show_local_axes=plot["show_local_axes"],
        ) # Replot model
        fig.canvas.draw_idle() # Refresh canvas

    # MAIN METHOD
    def undeformed_shape(
            self,
            views="3D",
            show_grids=True,
            show_nodes=True,
            show_node_labels=True,
            show_global_axes=False,
            show_local_axes=False,
        ):
        if isinstance(views, str):
            views = [views]

        # Validation
        if len(views) > 4:
            raise ValidationError(f"Reach maximum number of active viewports. "
                                  f"Viewports: {len(views)} (> 4)")
        for view in views:
            if view not in _view_definitions:
                raise ValidationError(f"Unknwon view type: '{view}'. "
                                      f"Available views: {list(_view_definitions)}")
        self._plots.clear()
        for view in views:
            title = f"Undeformed Shape - {view} View"
            view_info = _view_definitions[view]
            fig, ax = self._create_figure(view_info) # Initialise figure
            ax.set_title(title, fontsize=14, y=1.0) # Set title for a plot
            self._plots[view] = {
                "fig": fig,
                "ax": ax,
                "show_grids": show_grids,
                "show_nodes": show_nodes,
                "show_node_labels": show_node_labels,
                "show_global_axes": show_global_axes,
            }
            self._plot_model(
                ax=ax,
                view=view,
                show_grids=show_grids,
                show_nodes=show_nodes,
                show_node_labels=show_node_labels,
                show_global_axes=show_global_axes,
                show_local_axes=show_local_axes,
            )
        plt.tight_layout()
        return self

    def select_plane(self, view, plane=1):
        view_info = _view_definitions[view]
        if view_info["projection"] == "3d":
            raise ValidationError("Plane selection is only available for "
                                  "2D views: XY, XZ, and YZ")
        if view not in self._plots:
            raise ValidationError(f"View '{view}' is not currently active "
                                  f"Initialise viewport using undeformed_shape()")
        planes = self._get_available_planes(view_info=view_info)
        if not isinstance(plane, (int, np.integer)):
            raise ValidationError("Plane number must be an integer")
        if plane < 1 or plane > len(planes):
            raise ValidationError(f"Invalid plane number: {plane}. "
                                  f"Available planes: 1-{len(planes)}")
        self._selected_planes[view] = plane
        self._refresh_view(view)
        return self

    def show(self):
        plt.show()

    def deformed_shape(
            self,
            view="3D",
            colour_by=None,
            show_grids=True,
            show_nodes=True,
            show_elements=True,
            show_shells=True,
            show_restraints=True,
            loadcase="Dead",
            load_scale=1.0,
            show_loads=None,
            show_node_labels=True,
            show_element_labels=True,
            show_zerolengthelement_labels=False,
            show_shell_labels=True,
            show_load_labels=False,
            show_spring_hinges=False,
            show_end_releases=False,
            show_rigid_end_offsets=False,
            show_global_axes=True,
            show_local_axes=False,
            show_hinges_length=False,
            show_fiber_section=False,
        ):
        fig = plt.figure(figsize=(12, 8)) # Start plotting figure
        ax = fig.add_subplot(111, projection="3d")
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
                show_labels=show_zerolengthelement_labels,
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
        if loadcase not in self._loadcase_type:
            raise ValidationError(f"Unknown loadcase: '{loadcase}'. "
                "Choose between 'Selfweight' or 'Sw', 'Dead' or 'D', 'Live' or 'L', 'Live Roof' or 'Lr',"
                "'Earthquake-X' or 'Ex', 'Earthquake-Y' or 'Ey', 'Wind-X' or 'Wx', or 'Wind-Y' or 'Wy'")
        if show_loads not in self._load:
            raise ValidationError(f"Unknown show loads: '{show_loads}'. "
                "Choose None or between 'all' for all loads, 'n' for nodal load, 'e' for elemental load, or 'ste' for shell-t0-elemental load")
        if show_loads == "all" or show_loads == "n": # Set condition if show_loads is "all" or "n"
            _plot_nodal_loads(
                ax=ax,
                units=self._units,
                nodes=self._nodes,
                coords=self._coords,
                nodal_loads=self._nodal_loads,
                loadcase=loadcase,
                loadcase_type=self._loadcase_type,
                scale=load_scale,
                show_labels=show_load_labels,
            ) # Plot loads if show_elemental_loads is True
        if show_loads == "all" or show_loads == "e": # Set condition if show_loads is "all" or "e"
            _plot_elemental_loads(
                ax=ax,
                units=self._units,
                coords=self._coords,
                elements=self._elements,
                distributed_loads=self._distributed_elemental_loads,
                concentrated_loads=self._concentrated_elemental_loads,
                loadcase=loadcase,
                loadcase_type=self._loadcase_type,
                scale=load_scale,
                show_labels=show_load_labels,
                is_arrow=True,
            ) # Plot loads if show_elemental_loads is True
        if show_loads == "all" or show_loads == "ste": # Set condition if show_loads is "all" or "ste"
            _plot_shell_to_elemental_loads(
                ax=ax,
                units=self._units,
                coords=self._coords,
                elements=self._elements,
                shell_to_elemental_loads=self._shell_to_elemental_loads,
                loadcase=loadcase,
                loadcase_type=self._loadcase_type,
                scale=load_scale,
                show_labels=show_load_labels,
                is_arrow=True,
            ) # Plot loads if show_shell_to_elemental_loads is True
        plt.tight_layout()
        return self
