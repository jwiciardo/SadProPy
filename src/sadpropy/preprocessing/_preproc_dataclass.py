import numpy as np
from dataclasses import dataclass
from sadpropy.utility import UserDefinedUnits
from ._preproc_class import (
    Concrete04Properties,
    Steel02Properties,
    MinMaxProperties,
    IMKProperties,
    FiberSectionProperties,
    SectionAggregatorProperties,
)

# PROJECT
@dataclass(slots=True, frozen=True)
class FilePathInformation:
    parent_path: str
    output_path: str
    inputfile_path: str
    logfile_path: str

@dataclass(slots=True, frozen=True)
class ProjectInformation:
    name: str
    desc: str
    ndim: int

@dataclass(slots=True, frozen=True)
class AnalysisPreferences:
    is_nonlinear_analysis: str
    is_pdelta: str
    liveload_mass_factor: float

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
    mat_type: np.ndarray                # str, shape (N,)
    base_mat_class: np.ndarray          # int32, shape (N,)
    base_mat_idx: np.ndarray            # int32, shape (N,)
    mat_model: np.ndarray               # str, shape (N,)
    properties: np.ndarray              # float64, shape (N,10)
    name_to_idx: dict[str, np.int32]

    @classmethod
    def empty(cls):
        return cls(
            index=np.empty(0, dtype=np.int32),
            mat_name=np.empty(0, dtype="U32"),
            mat_type=np.empty(0, dtype="U15"),
            base_mat_class=np.empty(0, dtype=np.int32),
            base_mat_idx=np.empty(0, dtype=np.int32),
            mat_model=np.empty(0, dtype="U15"),
            properties=np.empty((0, len(Concrete04Properties)), dtype=np.float64),
            name_to_idx={},
        )

@dataclass(slots=True, frozen=True)
class Mat_Steel02:
    index: np.ndarray                   # int32, shape (N,)
    mat_name: np.ndarray                # str, shape (N,)
    mat_type: np.ndarray                # str, shape (N,)
    base_mat_class: np.ndarray          # int32, shape (N,)
    base_mat_idx: np.ndarray            # int32, shape (N,)
    mat_model: np.ndarray               # str, shape (N,)
    properties: np.ndarray              # float64, shape (N,14)
    name_to_idx: dict[str, np.int32]

    @classmethod
    def empty(cls):
        return cls(
            index=np.empty(0, dtype=np.int32),
            mat_name=np.empty(0, dtype="U32"),
            mat_type=np.empty(0, dtype="U15"),
            base_mat_class=np.empty(0, dtype=np.int32),
            base_mat_idx=np.empty(0, dtype=np.int32),
            mat_model=np.empty(0, dtype="U15"),
            properties=np.empty((0, len(Steel02Properties)), dtype=np.float64),
            name_to_idx={},
        )

@dataclass(slots=True, frozen=True)
class Mat_MinMax:
    index: np.ndarray                   # int32, shape (N,)
    mat_name: np.ndarray                # str, shape (N,)
    mat_type: np.ndarray                # str, shape (N,)
    base_nl_mat_class: np.ndarray       # int32, shape (N,)
    base_nl_mat_idx: np.ndarray         # int32, shape (N,)
    mat_model: np.ndarray               # str, shape (N,)
    properties: np.ndarray              # float64, shape (N,6)
    name_to_idx: dict[str, np.int32]

    @classmethod
    def empty(cls):
        return cls(
            index=np.empty(0, dtype=np.int32),
            mat_name=np.empty(0, dtype="U32"),
            mat_type=np.empty(0, dtype="U15"),
            base_nl_mat_class=np.empty(0, dtype=np.int32),
            base_nl_mat_idx=np.empty(0, dtype=np.int32),
            mat_model=np.empty(0, dtype="U15"),
            properties=np.empty((0, len(MinMaxProperties)), dtype=np.float64),
            name_to_idx={},
        )

@dataclass(slots=True, frozen=True)
class Mat_IMK:
    index: np.ndarray                   # int32, shape (N,)
    mat_name: np.ndarray                # str, shape (N,)
    mat_model: np.ndarray               # str, shape (N,)
    properties: np.ndarray              # float64, shape (N,27)
    name_to_idx: dict[str, np.int32]

    @classmethod
    def empty(cls):
        return cls(
            index=np.empty(0, dtype=np.int32),
            mat_name=np.empty(0, dtype="U32"),
            mat_model=np.empty(0, dtype="U15"),
            properties=np.empty((0, len(IMKProperties)), dtype=np.float64),
            name_to_idx={},
        )

# PROPERTIES: FRAME SECTIONS
@dataclass(slots=True, frozen=True)
class FrameSections:
    index: np.ndarray                   # int32, shape (N,)
    sec_name: np.ndarray                # str, shape (N,)
    sec_shape: np.ndarray               # str, shape (N,)
    mats_class: np.ndarray              # int32, shape (N,1)
    mats_idx: np.ndarray                # int32, shape (N,1)
    mat_type: np.ndarray                # str, shape (N,)
    sec_model: np.ndarray               # str, shape (N,)
    properties: np.ndarray              # float64, shape (N,10)
    name_to_idx: dict[str, np.int32]
    
@dataclass(slots=True, frozen=True)
class Sec_Fiber:
    index: np.ndarray                   # int32, shape (N,)
    sec_name: np.ndarray                # str, shape (N,)
    sec_shape: np.ndarray               # str, shape (N,)
    base_sec_class: np.ndarray          # int32, shape (N,)
    base_sec_idx: np.ndarray            # int32, shape (N,)
    integration_type: np.ndarray        # str, shape (N,)
    mats_class: np.ndarray              # float64, shape (N,3) --> mat_1, mat_2, mat_3
    mats_idx: np.ndarray                # float64, shape (N,3) --> mat_1, mat_2, mat_3
    mat_type: np.ndarray                # str, shape (N,)
    sec_model: np.ndarray               # str, shape (N,)
    properties: np.ndarray              # float64, shape (N,19)
    name_to_idx: dict[str, np.int32]

    @classmethod
    def empty(cls):
        return cls(
            index=np.empty(0, dtype=np.int32),
            sec_name=np.empty(0, dtype="U32"),
            sec_shape=np.empty(0, dtype="U32"),
            base_sec_class=np.empty(0, dtype=np.int32),
            base_sec_idx=np.empty(0, dtype=np.int32),
            integration_type=np.empty(0, dtype="U15"),
            mats_class=np.empty((0, 3), dtype=np.int32),
            mats_idx=np.empty((0, 3), dtype=np.int32),
            mat_type=np.empty(0, dtype="U15"),
            sec_model=np.empty(0, dtype="U15"),
            properties=np.empty((0, len(FiberSectionProperties)), dtype=np.float64),
            name_to_idx={},
        )
    
@dataclass(slots=True, frozen=True)
class Sec_Aggregator:
    index: np.ndarray                   # int32, shape (N,)
    sec_name: np.ndarray                # str, shape (N,)
    sec_shape: np.ndarray               # str, shape (N,)
    base_sec_class: np.ndarray          # int32, shape (N,)
    base_sec_idx: np.ndarray            # int32, shape (N,)
    mats_class: np.ndarray              # int32, shape (N,6)
    mats_idx: np.ndarray                # int32, shape (N,6)
    mat_type: np.ndarray                # str, shape (N,)
    sec_model: str                      # str, shape (N,)
    aggregated_sec_class: np.ndarray    # int32, shape (N,)
    aggregated_sec_idx: np.ndarray      # int32, shape (N,)
    properties: np.ndarray              # float64, shape (N,8)
    name_to_idx: dict[str, np.int32]

    @classmethod
    def empty(cls):
        return cls(
            index=np.empty(0, dtype=np.int32),
            sec_name=np.empty(0, dtype="U32"),
            sec_shape=np.empty(0, dtype="U32"),
            base_sec_class=np.empty(0, dtype=np.int32),
            base_sec_idx=np.empty(0, dtype=np.int32),
            mats_class=np.empty((0, 6), dtype=np.int32),
            mats_idx=np.empty((0, 6), dtype=np.int32),
            mat_type=np.empty(0, dtype="U15"),
            sec_model=np.empty(0, dtype="U15"),
            aggregated_sec_class=np.empty(0, dtype=np.int32),
            aggregated_sec_idx=np.empty(0, dtype=np.int32),
            properties=np.empty((0, len(SectionAggregatorProperties)), dtype=np.float64),
            name_to_idx={},
        )
    
# PROPERTIES: SLAB SECTIONS
@dataclass(slots=True, frozen=True)
class SlabSections:
    index: np.ndarray                   # int32, shape (N,)
    sec_name: np.ndarray                # str, shape (N,)
    mats_class: np.ndarray              # int32, shape (N,1)
    mats_idx: np.ndarray                # int32, shape (N,1)
    properties: np.ndarray              # float64, shape (N,)
    name_to_idx: dict[str, np.int32]

    @classmethod
    def empty(cls):
        return cls(
            index=np.empty(0, dtype=np.int32),
            sec_name=np.empty(0, dtype="U32"),
            mats_class=np.empty((0, 1), dtype=np.int32),
            mats_idx=np.empty((0, 1), dtype=np.int32),
            properties=np.empty((0, len(SectionAggregatorProperties)), dtype=np.float64),
            name_to_idx={},
        )
    
# STRUCTURE DATA
@dataclass(slots=True, frozen=True)
class Storeys:
    name: str
    height: float
    elevation: float

# STRUCTURAL OBJECTS
@dataclass(slots=True, frozen=True)
class Nodes:
    index: np.ndarray                   # int32, shape (N,)
    unique_name: np.ndarray             # str, shape (N,)
    tag: np.ndarray                     # int32, shape (N,)
    coords: np.ndarray                  # float64, shape (N,3)
    generated_source: np.ndarray        # int32, shape (N,)
    generated_from: np.ndarray          # str, shape (N,)
    name_to_idx: dict[str, np.int32]

@dataclass(slots=True, frozen=True)
class BeamColumnElements:
    index: np.ndarray                   # int32, shape (N,)
    unique_name: np.ndarray             # str, shape (N,)
    tag: np.ndarray                     # int32, shape (N,)
    end_nodes_idx: np.ndarray           # int32, shape (N,2)
    element_type: np.ndarray            # str, shape(N,)
    sec_class: np.ndarray               # int32, shape (N,)
    sec_idx: np.ndarray                 # int32, shape (N,)
    centroids: np.ndarray               # float64, shape (N,3)
    length: np.ndarray                  # float64, shape (N,)
    local_x: np.ndarray                 # int32, shape (N,3)
    local_y: np.ndarray                 # int32, shape (N,3)
    local_z: np.ndarray | None          # int32, shape (N,3)
    rotation_matrix: np.ndarray         # int32, shape (N,3,3) for 3D or (N,2,2) for 2D
    elements_connectivity: np.ndarray   # int32, shape (N,Max. connections)
    shared_connected_nodes: np.ndarray  # int32, shape (N,Max. connections)
    current_elements_end: np.ndarray    # int32, shape (N,Max. connections)
    neighbour_elements_end: np.ndarray  # int32, shape (N,Max. connections)
    rigid_zone_factor: np.ndarray       # float64, shape (N,)
    offsets_length: np.ndarray          # float64, shape (N,2)
    end_offsets: np.ndarray             # float64, shape (N,6)
    name_to_idx: dict[str, np.int32]

@dataclass(slots=True, frozen=True)
class Slabs:
    tag: int
    elements: tuple[int, ...]
    nodes: tuple[int, ...]

# PROPERTIES: RESTRAINTS
@dataclass(slots=True, frozen=True)
class Restraints:
    node_idx: np.ndarray                # int32, shape (N,)
    node_name: np.ndarray               # str, shape (N,)
    node_tag: np.ndarray                # int32, shape (N,)
    dofs: np.ndarray                    # int32, shape (N,6)

# MODEL DATA
@dataclass(slots=True)
class ModelDataclass:
    filepath_information: FilePathInformation
    project_information: ProjectInformation
    userdefined_units: UserDefinedUnits
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
    sections_list: list
    slab_sections: SlabSections
    storeys: Storeys
    nodes: Nodes
    beamcolumn_elements: BeamColumnElements

    restraints: Restraints

