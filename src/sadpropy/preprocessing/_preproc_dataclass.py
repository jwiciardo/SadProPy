import numpy as np
from dataclasses import dataclass
from sadpropy.utility import UnitSystem

# PROJECT
@dataclass(slots=True, frozen=True)
class ProjectInformation:
    name: str
    desc: str
    ndim: int

@dataclass(slots=True, frozen=True)
class AnalysisPreferences:
    nonlinear_analysis: str
    pdelta: str
    liveload_mass_factor: float

# STRUCTURE DATA
@dataclass(slots=True, frozen=True)
class PointObjects:
    index: np.ndarray                   # int32, shape (N,)
    unique_name: np.ndarray             # str, shape (N,)
    coords: np.ndarray                  # float64, shape (N,3)
    name_to_idx: dict[str, np.int32]

@dataclass(slots=True, frozen=True)
class LineObjects:
    index: np.ndarray                   # int32, shape (N,)
    unique_name: np.ndarray             # str, shape (N,)
    end_points_idx: np.ndarray          # int32, shape (N,2)
    end_offset_option: np.ndarray       # str, shape (N,)
    end_offsets: np.ndarray             # float64, shape (N,2)
    length: np.ndarray                  # float64, shape (N,)
    centroids: np.ndarray               # float64, shape (N,3)
    name_to_idx: dict[str, np.int32]

@dataclass(slots=True, frozen=True)
class SurfaceObjects:
    index: np.ndarray                   # int32, shape (N,)
    unique_name: np.ndarray             # str, shape (N,)
    edges_idx: np.ndarray               # int32, shape (N,4)
    vertices_idx: np.ndarray            # int32, shape (N,4)
    name_to_idx: dict[str, np.int32]

@dataclass(slots=True, frozen=True)
class Storeys:
    name: str
    height: float
    elevation: float

# PROPERTIES: MATERIALS
@dataclass(slots=True, frozen=True)
class Materials:
    index: np.ndarray                   # int32, shape (N,)
    mat_name: np.ndarray                # str, shape (N,)
    mat_type: np.ndarray                # str, shape (N,)
    properties: np.ndarray              # float64, shape (N,7)
    name_to_idx: dict[str, np.int32]

@dataclass(slots=True, frozen=True)
class Mat_Concrete04:
    index: np.ndarray                   # int32, shape (N,)
    mat_name: np.ndarray                # str, shape (N,)
    base_mat_class: np.ndarray          # int32, shape (N,)
    base_mat_idx: np.ndarray            # int32, shape (N,)
    mat_model: np.ndarray               # str, shape (N,)
    properties: np.ndarray              # float64, shape (N,10)
    name_to_idx: dict[str, np.int32]


@dataclass(slots=True, frozen=True)
class Mat_Steel02:
    index: np.ndarray                   # int32, shape (N,)
    mat_name: np.ndarray                # str, shape (N,)
    base_mat_class: np.ndarray          # int32, shape (N,)
    base_mat_idx: np.ndarray            # int32, shape (N,)
    mat_model: np.ndarray               # str, shape (N,)
    properties: np.ndarray              # float64, shape (N,14)
    name_to_idx: dict[str, np.int32]

@dataclass(slots=True, frozen=True)
class Mat_MinMax:
    index: np.ndarray                   # int32, shape (N,)
    mat_name: np.ndarray                # str, shape (N,)
    base_nl_mat_class: np.ndarray       # int32, shape (N,)
    base_nl_mat_idx: np.ndarray         # int32, shape (N,)
    mat_model: np.ndarray               # str, shape (N,)
    properties: np.ndarray              # float64, shape (N,6)
    name_to_idx: dict[str, np.int32]

@dataclass(slots=True, frozen=True)
class Mat_IMK:
    index: np.ndarray                   # int32, shape (N,)
    mat_name: np.ndarray                # str, shape (N,)
    mat_model: np.ndarray               # str, shape (N,)
    properties: np.ndarray              # float64, shape (N,27)
    name_to_idx: dict[str, np.int32]

# PROPERTIES: FRAME SECTIONS
@dataclass(slots=True, frozen=True)
class FrameSections:
    index: np.ndarray                   # int32, shape (N,)
    sec_name: np.ndarray                # str, shape (N,)
    sec_shape: np.ndarray               # str, shape (N,)
    sec_model: np.ndarray               # str, shape (N,)
    base_mat_class: np.ndarray          # int32, shape (N,)
    base_mat_idx: np.ndarray            # int32, shape (N,)
    element_type: np.ndarray            # str, shape (N,)
    properties: np.ndarray              # float64, shape (N,10)
    name_to_idx: dict[str, np.int32]

@dataclass(slots=True, frozen=True)
class Sec_Fiber:
    index: np.ndarray                   # int32, shape (N,)
    sec_name: np.ndarray                # str, shape (N,)
    base_sec_idx: np.ndarray            # int32, shape (N,)
    integration_type: np.ndarray        # str, shape (N,)
    mat_type: np.ndarray                # str, shape (N,)
    mat_idx: np.ndarray                 # float64, shape (N,3) --> mat_1, mat_2, mat_3
    sec_model: np.ndarray               # str, shape (N,)
    properties: np.ndarray              # float64, shape (N,19)
    name_to_idx: dict[str, np.int32]
    h: float
    b: float
    cover: float
    nbars_top: int
    nbars_bot: int
    nbars_int: int
    bar_dia_hoop: float
    bar_dia_top: float
    bar_dia_bot: float
    bar_dia_int: float
    A: float
    Avy: float
    Avz: float
    Iz: float
    Iy: float 
    Jxx: float
    Abar_top: float
    Abar_bot: float
    Abar_int: float

@dataclass(slots=True, frozen=True)
class Sec_Aggregator:
    sec_name: str
    aggregated_sec: str
    base_mat: str
    sec_model: str
    aggregator_type: str
    h: float
    b: float
    A: float
    Avy: float
    Avz: float
    Iz: float
    Iy: float
    Jxx: float

# PROPERTIES: SLAB SECTIONS
@dataclass(slots=True, frozen=True)
class SlabSections:
    sec_name: str
    base_mat: str
    t: float

# MODEL DATA
@dataclass(slots=True)
class ModelData:
    project_information: ProjectInformation
    user_unitsystem: UnitSystem
    analysis_preferences: AnalysisPreferences
    materials: Materials
    mat_concrete04: Mat_Concrete04
    mat_steel02: Mat_Steel02
    mat_minmax: Mat_MinMax
    mat_imk: Mat_IMK
    materials_list: list
    frame_sections: FrameSections
    sec_fiber: Sec_Fiber
    sec_aggregator: Sec_Aggregator
    slab_sections: SlabSections
    storeys: Storeys
    point_objects: PointObjects
    line_objects: LineObjects
    surface_objects: SurfaceObjects

# STRUCTURAL OBJECTS
@dataclass(slots=True, frozen=True)
class Nodes:
    tag: int
    point_id: int
    index: int
    x: float
    y: float
    z: float

@dataclass(slots=True, frozen=True)
class BeamColumnElements:
    tag: int
    iend_node: int
    jend_node: int

@dataclass(slots=True, frozen=True)
class Slabs:
    tag: int
    elements: tuple[int, ...]
    nodes: tuple[int, ...]

