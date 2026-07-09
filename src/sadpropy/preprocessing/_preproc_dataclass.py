import numpy as np
from dataclasses import dataclass, field
from typing import Dict
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
    ids: np.ndarray                     # int32, shape (N,)
    unique_names: np.ndarray            # str, shape (N,)
    coords: np.ndarray                  # float64, shape (N,3)
    uname_to_id: dict[str, np.int32]

@dataclass(slots=True, frozen=True)
class LineObjects:
    ids: np.ndarray                     # int32, shape (N,)
    unique_names: np.ndarray            # str, shape (N,)
    end_point_ids: np.ndarray           # int32, shape (N,2)
    end_offset_option: np.ndarray       # str, shape (N,)
    end_offsets: np.ndarray             # float64, shape (N,2)
    length: np.ndarray                  # float64, shape (N,)
    centroids: np.ndarray               # float64, shape (N,3)
    uname_to_id: dict[str, np.int32]

@dataclass(slots=True, frozen=True)
class SurfaceObjects:
    ids: np.ndarray                     # int32, shape (N,)
    unique_names: np.ndarray            # str, shape (N,)
    edge_ids: np.ndarray                # int32, shape (N,4)
    vertex_ids: np.ndarray              # int32, shape (N,4)
    uname_to_id: dict[str, np.int32]

@dataclass(slots=True, frozen=True)
class Storeys:
    name: str
    height: float
    elevation: float

# PROPERTIES: MATERIALS
@dataclass(slots=True, frozen=True)
class Materials:
    mat_name: str
    mat_type: str
    E: float
    nu: float
    G: float
    unitweight: float
    fc: float
    fy: float
    fu: float

@dataclass(slots=True, frozen=True)
class Mat_Concrete04:
    mat_name: str
    base_mat: str
    mat_type: str
    mat_model: str
    E: float
    nu: float
    G: float
    unitweight: float
    fc: float
    epsc: float
    epscu: float
    fct: float
    et: float
    beta: float

@dataclass(slots=True, frozen=True)
class Mat_Steel02:
    mat_name: str
    base_mat: str
    mat_type: str
    mat_model: str
    E: float
    nu: float
    G: float
    unitweight: float
    fy: float
    fu: float
    ey: float
    eu: float
    b: float
    R0: int
    cR1: float
    cR2: float
    a1: float
    a2: float
    a3: float
    a4: float
    f_init: float

@dataclass(slots=True, frozen=True)
class Mat_MinMax:
    mat_name: str
    base_nonlinear_mat: str
    mat_type: str
    mat_model: str
    E: float
    nu: float
    G: float
    unitweight: float
    ec_max: float
    et_max: float

@dataclass(slots=True, frozen=True)
class Mat_IMK:
    mat_name: str
    mat_type: str
    mat_model: str
    K0: float
    as_pos: float
    as_neg: float
    my_pos: float
    my_neg: float
    mu_pos: float
    mu_neg: float
    fpr_pos: float
    fpr_neg: float
    a_pinch: float
    nfactor: float
    lamda_s: float
    lamda_c: float
    lamda_a: float
    lamda_k: float
    c_s: float
    c_c: float
    c_a: float
    c_k: float
    theta_p_pos: float
    theta_p_neg: float
    theta_pc_pos: float
    theta_pc_neg: float
    res_pos: float
    res_neg: float
    theta_u_pos: float
    theta_u_neg: float
    d_pos: float
    d_neg: float

# PROPERTIES: FRAME SECTIONS
@dataclass(slots=True, frozen=True)
class FrameSections:
    sec_name: str
    sec_shape: str
    base_mat: str
    sec_model: str
    element_type: str
    h: float
    b: float
    A: float
    Avy: float
    Avz: float
    Iz: float
    Iy: float
    Jxx: float
    alphaY: float
    alphaZ: float

@dataclass(slots=True, frozen=True)
class Sec_Fiber:
    sec_name: str
    base_sec: str
    integration_type: str
    mat_type: str
    mat_1: str
    mat_2: str
    mat_3: str
    sec_model: str
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
@dataclass
class ModelData:
    project_information: ProjectInformation
    user_unitsystem: UnitSystem
    analysis_preferences: AnalysisPreferences
    materials: Dict[str, Materials] = field(default_factory=dict)
    frame_sections: Dict[str, FrameSections] = field(default_factory=dict)
    slab_sections: Dict[str, SlabSections] = field(default_factory=dict)
    storeys: Dict[str, Storeys] = field(default_factory=dict)
    point_objects: Dict[int, PointObjects] = field(default_factory=dict)
    line_objects: Dict[int, LineObjects] = field(default_factory=dict)
    surface_objects: Dict[int, SurfaceObjects] = field(default_factory=dict)
    mat_concrete04: Dict[str, Mat_Concrete04] = field(default_factory=dict)
    mat_steel02: Dict[str, Mat_Steel02] = field(default_factory=dict)
    mat_minmax: Dict[str, Mat_MinMax] = field(default_factory=dict)
    mat_imk: Dict[str, Mat_IMK] = field(default_factory=dict)
    sec_fiber: Dict[str, Sec_Fiber] = field(default_factory=dict)
    sec_aggregator: Dict[str, Sec_Aggregator] = field(default_factory=dict)

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

