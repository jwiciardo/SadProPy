import warnings
import numpy as np
from .modeldata import ModelData
from ._preproc_dataclass import (
    ProjectInformation,
    AnalysisPreferences,
    Materials,
    Mat_Concrete04,
    Mat_Steel02,
    Mat_MinMax,
    Mat_IMK,
    FrameSections,
    Sec_Fiber,
    Sec_Aggregator,
    SlabSections,
    PointObjects,
    LineObjects,
    SurfaceObjects,
    Storeys,
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
    UnitConverter,
    UnitRegistry,
    UnitSystem,
    section_properties,
    fibersection_properties,
    TagManager,
)
from sadpropy.utility._exceptions import ValidationError
from sadpropy.utility.helperfunc import get_material_properties, get_section_properties

class StructuralModelData:
    def __init__(self, modeldata):
        self._modeldata = modeldata
    
    def generate(self):
        nodes = self._generate_nodes()
        return 1
    
    def _generate_nodes(self):
        data = self._modeldata.point_objects # Recall point_objects data
        n = 