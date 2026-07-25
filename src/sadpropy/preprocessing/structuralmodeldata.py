import warnings
import numpy as np
from ._preproc_dataclass import (
    Nodes,
    BeamColumnElements,
    Restraints,
    )
from ._class import (
    MaterialProperties,
    Concrete04Properties,
    Steel02Properties,
    MinMaxProperties,
    IMKProperties,
    FrameSectionProperties,
    FiberSectionProperties,
    SectionAggregatorProperties,
    SlabSectionProperties,
)
from sadpropy.utility import (
    UserDefinedUnits,
    section_properties,
    fibersection_properties,
    TagManager,
)
from sadpropy.utility._exceptions import ValidationError
from sadpropy.utility.helperfunc import retrieve_output_from_input

__all__ = ["StructuralModelData"]

class StructuralModelData:
    def __init__(self, modeldata):
        self._modeldata = modeldata
        self._tagmanager = TagManager()
    
    def generate(self):
        nodes = self._generate_nodes()
        beamcolumn_elements = self._generate_beamcolumn_elements(nodes=nodes)
        return beamcolumn_elements
    
    def _generate_nodes(self):
        data = self._modeldata.point_objects # Recall point_objects data
        point_idx = data.index
        n = len(point_idx)
        index = np.arange(n, dtype=np.int32)
        nodes = Nodes(
            index = index,
            label = data.unique_name,
            coords = data.coords,
        )
        return nodes
    
    def _generate_beamcolumn_elements(self, nodes):
        data = self._modeldata.line_objects # Recall line_objects data
        data_pointobj = self._modeldata.point_objects # Recall point_objects data
        secs_list = self._modeldata.sections_list # Recall sections_list data
        element_type = np.fromiter((secs_list[sc].element_type[idx]
            for sc, idx in zip(data.sec_class, data.sec_idx)), dtype="U15")
        mask = (element_type == "Beam")
        #mask = (element_type == "Column") | (element_type == "Beam")
        n = len(data.index[mask])
        index = np.arange(n, dtype=np.int32)
        label = data.unique_name[mask]
        point_name = data_pointobj.unique_name
        end_points_idx = data.end_points_idx[mask]
        end_nodes_idx = retrieve_output_from_input(
            inputdata=end_points_idx,
            shared_data_in=point_name,
            outputdata=nodes.index, 
            shared_data_out=nodes.label,
        )
        return element_type
    
    def _translate_line_objects(self, point_objects, project_information):
        sheet_name = "Line Objects"
        data = self._reader.read(sheet_name=sheet_name, start_row=13) # Reading Sheet "Line Objects" in the Input file
        self._validate_data(data=data, sheet_name=sheet_name, mandatory=True)
        n = len(data)
        index = np.arange(n, dtype=np.int32)
        unique_name = np.empty(n, dtype="U15")
        end_points_idx = np.empty((n, 2), dtype=np.int32)
        sec_class = np.empty(n, dtype=np.int32)
        sec_idx = np.empty(n, dtype=np.int32)
        is_zero_length_element = np.empty(n, dtype=bool)
        centroids = np.empty((n, 3), dtype=np.float64)
        end_offset_option = np.empty(n, dtype="U22")
        end_offsets = np.empty((n, 2), dtype=np.float64)
        name_to_idx = {}
        for i, row in enumerate(data):
            name = str(row["Unique Name"])
            if name in name_to_idx:
                raise ValidationError(f"Duplicate Line object name '{name}'")
            name_to_idx[name] = index[i]
            unique_name[i] = name
            end_points_idx[i] = (point_objects.name_to_idx[str(row["I-End"])], point_objects.name_to_idx[str(row["J-End"])],)
            end_offset_option[i] = str(row["End Offset"])
            end_offsets[i] = (
                self._to_internalunits.length(value=row["I-End Offset Length"] if row["I-End Offset Length"] is not None else 0.0),
                self._to_internalunits.length(value=row["J-End Offset Length"] if row["J-End Offset Length"] is not None else 0.0),
            )
            sec_class[i], _, sec_idx[i] = self._retrieve_section_index(sec_name=str(row["Section"]))
            is_zero_length_element[i] = (str(row["Zero Length Element"]).strip().lower() == "yes")
        i_coords = point_objects.coords[end_points_idx[:, 0]]
        j_coords = point_objects.coords[end_points_idx[:, 1]]
        centroids = (i_coords + j_coords) / 2.0 # Calculate centroid of line objects
        length, local_x, local_y, local_z, rotation_matrix = generate_local_axes(
            end_points_index=end_points_idx,
            point_objects=point_objects,
            ndim=project_information.ndim,
        )
        connected_lines, connection_direction = generate_line_connectivity(
            end_points_idx=end_points_idx,
            centroids=centroids,
            rotation=rotation_matrix,
        )
        sec_data = get_section_data(secs_list=self._secs_list, sec_class=sec_class)
        sec_99 = sec_data[99].properties[sec_idx[99]]
        sec_100 = sec_data[100].properties[sec_idx[100]]
        print(sec_99, sec_100)
        line_objects = LineObjects(
            index = index,
            unique_name = unique_name,
            end_points_idx = end_points_idx,
            end_offset_option = end_offset_option,
            end_offsets = end_offsets,
            sec_class = sec_class,
            sec_idx = sec_idx,
            is_zero_length_element = is_zero_length_element,
            centroids = centroids,
            length = length,
            local_x = local_x,
            local_y = local_y,
            local_z = local_z,
            rotation_matrix = rotation_matrix,
            line_connectivity = connected_lines,
            connection_end = connection_direction,
            name_to_idx = name_to_idx,
        ) # Defining dataclass for each line object
        return line_objects