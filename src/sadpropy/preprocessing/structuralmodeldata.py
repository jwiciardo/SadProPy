import warnings
import numpy as np
from ._preproc_dataclass import (
    Nodes,
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
from sadpropy.utility.helperfunc import get_material_properties, get_section_properties

__all__ = ["StructuralModelData"]

class StructuralModelData:
    def __init__(self, modeldata):
        self._modeldata = modeldata
        self._tagmanager = TagManager()
    
    def generate(self):
        nodes = self._generate_nodes()
        beamcolumn_elements = self._generate_beamcolumn_elements()
        return nodes
    
    def _generate_nodes(self):
        data = self._modeldata.point_objects # Recall point_objects data
        n = len(data.index)
        point_name = data.unique_name
        tag = self._tagmanager.add("Node", n, point_name)
        next_tag = self._tagmanager.next_tag("Node")
        count = self._tagmanager.count("Node")
        print(next_tag, count)
        nodes = Nodes(
            tag = tag,
            point_name = point_name,
            coords = data.coords,
        )
        return nodes
    
    def _generate_beamcolumn_elements(self):
        data = self._modeldata.line_objects # Recall line_objects data
        secs_list = self._modeldata.sections_list # Recall sections_list data
        element_type = np.fromiter((secs_list[sc].element_type[idx]
            for sc, idx in zip(data.sec_class, data.sec_idx)), dtype="U15")
        return element_type