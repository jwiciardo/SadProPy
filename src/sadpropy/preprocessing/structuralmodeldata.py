import warnings
import numpy as np
from ._preproc_dataclass import (
    Nodes,
    BeamColumnElements,
    Restraints,
    )
from ._propertiesclass import (
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
from sadpropy.utility.helperfunc import get_material_properties, get_section_properties, retrieve_output_from_input

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
            point_name = data.unique_name,
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
        line_name = data.unique_name[mask]
        point_name = data_pointobj.unique_name
        end_points_idx = data.end_points_idx[mask]
        end_nodes_idx = retrieve_output_from_input(
            inputdata=end_points_idx,
            shared_data_in=point_name,
            outputdata=nodes.index, 
            shared_data_out=nodes.point_name,
        )
        return element_type