from dataclasses import dataclass, field
from typing import Dict
from sadpropy.utility.units import UnitSystem

__all__ = [
    "ProjectInformation", "AnalysisPreferences", "PointCoordinates", "LineConnectivity", "SurfaceConnectivity", "StoreyData",
    "Materials", "Mat_Concrete04", "Mat_Steel02", "Mat_MinMax", "Mat_IMK", "FrameSections", "Sec_Fiber", "Sec_Aggregator", "SlabSections",
    "Nodes", "BeamColumnElements", "Slabs",
    "ModelData"
    ]

# Project
@dataclass(slots=True, frozen=True)
class ProjectInformation:
    name: str
    desc: str

@dataclass(slots=True, frozen=True)
class AnalysisPreferences:
    nonlinear_analysis: str
    auto_zero_length: str
    pdelta: str
    liveload_mass_factor: float

# Structure Data
@dataclass(slots=True, frozen=True)
class PointCoordinates:
    id: int
    x: float
    y: float
    z: float

@dataclass(slots=True, frozen=True)
class LineConnectivity:
    id: int
    i_end: int
    j_end: int
    end_offset: str
    i_end_offset: float
    j_end_offset: float
    length: float
    centroid_x: float
    centroid_y: float
    centroid_z: float

@dataclass(slots=True, frozen=True)
class SurfaceConnectivity:
    id: int
    n_edges: int
    edges: tuple[int, ...]
    vertices: tuple[int, ...]

@dataclass(slots=True, frozen=True)
class StoreyData:
    name: str
    height: float
    elevation: float

# Properties: Materials
@dataclass(slots=True, frozen=True)
class Materials:
    name: str
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
    name: str
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
    name: str
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
    name: str
    base_nl_mat: str
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
    name: str
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

# Properties: Frame Sections
@dataclass(slots=True, frozen=True)
class FrameSections:
    name: str
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
    name: str
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
    name: str
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

# Properties: Slab Sections
@dataclass(slots=True, frozen=True)
class SlabSections:
    name: str
    base_mat: str
    t: float

# Structural Objects
@dataclass(slots=True, frozen=True)
class Nodes:
    tag: int
    point_id: int
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

# Model Data
@dataclass
class ModelData:
    project_information: ProjectInformation
    user_unitsystem: UnitSystem
    analysis_preferences: AnalysisPreferences
    storey_data: Dict[str, StoreyData] = field(default_factory=dict)
    point_coordinates: Dict[int, PointCoordinates] = field(default_factory=dict)
    line_connectivity: Dict[int, LineConnectivity] = field(default_factory=dict)
    surface_connectivity: Dict[int, SurfaceConnectivity] = field(default_factory=dict)
    materials: Dict[str, Materials] = field(default_factory=dict)
    mat_concrete04: Dict[str, Mat_Concrete04] = field(default_factory=dict)
    mat_steel02: Dict[str, Mat_Steel02] = field(default_factory=dict)
    mat_minmax: Dict[str, Mat_MinMax] = field(default_factory=dict)
    mat_imk: Dict[str, Mat_IMK] = field(default_factory=dict)
    frame_sections: Dict[str, FrameSections] = field(default_factory=dict)
    sec_fiber: Dict[str, Sec_Fiber] = field(default_factory=dict)
    sec_aggregator: Dict[str, Sec_Aggregator] = field(default_factory=dict)
    slab_sections: Dict[str, SlabSections] = field(default_factory=dict)
    nodes: Dict[int, Nodes] = fiel(default_factory=dict)