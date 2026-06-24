from dataclasses import dataclass, field
from typing import Dict
from sadpropy.utility.units import UnitSystem

__all__ = [
    "ProjectInformation", "AnalysisPreferences", "PointCoordinates", "LineConnectivity", "SurfaceConnectivity", "StoreyData",
    "Materials", "Mat_Concrete04", "Mat_Steel02", "Mat_MinMax", "Nodes", "BeamColumnElements", "Slabs",
    "ModelData"
    ]

# Project
@dataclass(slots=True, frozen=True)
class ProjectInformation:
    project_name: str
    project_desc: str

@dataclass(slots=True, frozen=True)
class AnalysisPreferences:
    nl_analysis: str
    pdelta: str
    ll_mass_factor: float

# Structure Data
@dataclass(slots=True, frozen=True)
class PointCoordinates:
    point_id: int
    x_coord: float
    y_coord: float
    z_coord: float

@dataclass(slots=True, frozen=True)
class LineConnectivity:
    line_id: int
    i_end: int
    j_end: int
    length: float
    centroid_x: float
    centroid_y: float
    centroid_z: float

@dataclass(slots=True, frozen=True)
class SurfaceConnectivity:
    surface_id: int
    n_edges: int
    edges: tuple[int, ...]
    vertices: tuple[int, ...]

@dataclass(slots=True, frozen=True)
class StoreyData:
    storey_name: str
    height: float
    elevation: float

# Properties
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

@dataclass(frozen=True)
class Mat_Concrete04:
    name: str
    base_mat: str
    type: str
    model: str
    fc: float
    epsc: float
    epscu: float
    fct: float
    et: float
    beta: float
    E: float
    nu: float
    G: float
    Esec: float
    unitweight: float

@dataclass(frozen=True)
class Mat_Steel02:
    name: str
    base_mat: str
    type: str
    model: str
    fy: float
    fu: float
    ey: float
    eoffset: float
    eu: float
    E: float
    nu: float
    G: float
    Epy: float
    b: float
    R0: float
    cR1: float
    cR2: float
    unitweight: float

@dataclass(frozen=True)
class Mat_MinMax:
    name: str
    base_nl_mat: str
    type: str
    model: str
    ec: float
    et: float

# Structural Objects
@dataclass(frozen=True)
class Nodes:
    tag: int
    x: float
    y: float
    z: float

@dataclass(frozen=True)
class BeamColumnElements:
    tag: int
    iend_node: int
    jend_node: int

@dataclass(frozen=True)
class Slabs:
    tag: int
    elements: tuple[int, ...]
    nodes: tuple[int, ...]

# Model Data
@dataclass
class ModelData:
    project_information: ProjectInformation
    units: UnitSystem
    analysis_preferences: AnalysisPreferences
    storey_data: Dict[str, StoreyData] = field(default_factory=dict)
    point_coordinates: Dict[int, PointCoordinates] = field(default_factory=dict)
    line_connectivity: Dict[int, LineConnectivity] = field(default_factory=dict)
    surface_connectivity: Dict[int, SurfaceConnectivity] = field(default_factory=dict)
    materials: Dict[str, Materials] = field(default_factory=dict)

    #mat_concrete04: Dict[str, Mat_Concrete04] = field(default_factory=dict)
    #mat_steel02: Dict[str, Mat_Steel02] = field(default_factory=dict)
    #mat_minmax: Dict[str, Mat_MinMax] = field(default_factory=dict)