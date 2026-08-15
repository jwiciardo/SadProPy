import numpy as np
from enum import IntEnum

class MaterialType(IntEnum):
    Concrete = 0
    Steel = 1
    Spring = 2

class MaterialModel(IntEnum):
    Elastic = 0
    Concrete04 = 1
    Concrete04MinMax = 2
    Steel02 = 11
    Steel02MinMax = 12
    IMKBilinear = 91
    IMKPeakOriented = 92
    IMKPinching = 93

class SectionShape(IntEnum):
    Rectangular = 0
    Circular = 1
    WideFlange = 2
    Channel = 3
    RectangularHollow = 4
    CircularHollow = 5

class SectionModel(IntEnum):
    Elastic = 0
    Fiber = 1

class IntegrationType(IntEnum):
    Lobatto = 0
    HingeRadau = 11


class FrameSectionProperties(IntEnum):
    h = 0
    b = 1
    A = 2
    Avy = 3
    Avz = 4
    Iz = 5
    Iy = 6
    Jxx = 7
    AlphaY = 8
    AlphaZ = 9

class FiberSectionProperties(IntEnum):
    h = 0
    b = 1
    cover = 2
    nBars_top = 3
    nBars_bot = 4
    nBars_int = 5
    barDia_hoop = 6
    barDia_top = 7
    barDia_bot = 8
    barDia_int = 9
    A = 10
    Avy = 11
    Avz = 12
    Iz = 13
    Iy = 14
    Jxx = 15    
    Abar_top = 16
    Abar_bot = 17
    Abar_int = 18

class SectionAggregatorProperties(IntEnum):
    h = 0
    b = 1
    A = 2
    Avy = 3
    Avz = 4
    Iz = 5
    Iy = 6
    Jxx = 7

class SlabSectionProperties(IntEnum):
    t = 0

class PropertiesClassRegistry:
    SECTIONS = np.array([
        FrameSectionProperties, # Index 0
        FiberSectionProperties, # Index 1
        SectionAggregatorProperties, # Index 2
    ], dtype=object)

    def _get_sec_props_class(self, sec_class):
        return self.SECTIONS[sec_class]

class NodeSource(IntEnum):
    USR = 0 # Userdefined Generated source
    ZLE = 1 # Zero Length Auto Generated source
    PZ = 2 # Panel Zone Auto Generated source

class ConnectionEnd(IntEnum):
    I_End = 0
    J_End = 1

class LoadCaseType:
    case = {
        "SW": 0,
        "D": 1,
        "L": 2,
        "Lr": 3,
        "E": 4,
        "W": 5,
    }
    def _get_loadcase_class(self, loadcase):
        return self.case[loadcase]

class LoadDirection:
    global_direction = {
        3 : {
            "Global-X": np.asarray([1, 0, 0], dtype=np.float64),
            "Global-Y": np.asarray([0, 1, 0], dtype=np.float64),
            "Gravity": np.asarray([0, 0, -1], dtype=np.float64),
        },
        2 : {
            "Global-X": np.asarray([1, 0], dtype=np.float64),
            "Global-Y": np.asarray([0, 1], dtype=np.float64),
            "Gravity": np.asarray([0, -1], dtype=np.float64),
        }
    }
    local_direction = {
        3: {
            "Local-x": np.asarray([1, 0, 0], dtype=np.float64),
            "Local-y": np.asarray([0, 1, 0], dtype=np.float64),
            "Local-z": np.asarray([0, 0, 1], dtype=np.float64),
        },
        2: {
            "Local-x": np.asarray([1, 0], dtype=np.float64),
            "Local-y": np.asarray([0, 1], dtype=np.float64),
        }
    }

    @classmethod
    def get_direction(cls, ndim):
        return {**cls.global_direction[ndim], **cls.local_direction[ndim]}