import numpy as np
from dataclasses import dataclass
from ..utility import UserDefinedUnits
from ..utility._exceptions import ValidationError

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
    is_nonlinear_analysis: bool
    is_pdelta: bool
    liveload_mass_factor: float

# PROPERTIES: MATERIALS
@dataclass(slots=True, frozen=True)
class Materials:
    index: np.ndarray                   # int32, shape (N,)
    mat_name: np.ndarray                # str, shape (N,)
    mat_tag: np.ndarray                 # int32, shape (N,)
    mat_type: np.ndarray                # int8, shape (N,)
    mat_model: np.ndarray               # int8, shape (N,)
    mat_def: np.ndarray                 # object, shape (N,)
    properties: np.ndarray              # float64, shape (N,Max.columns)

    def name_to_idx(self, names):
        lookup = dict(zip(self.mat_name, self.index))
        result = np.full(len(names), -1, dtype=np.int32)
        for i, name in enumerate(names):
            if name is None:
                continue
            name = str(name).strip()
            if not name or name.lower() in {"none", "nan"}:
                continue
            try:
                result[i] = lookup[name]
            except KeyError:
                raise ValidationError(f"Material '{name}' does not exist") from None
        return result

# PROPERTIES: FRAME SECTIONS
@dataclass(slots=True, frozen=True)
class FrameSections:
    index: np.ndarray                   # int32, shape (N,)
    sec_name: np.ndarray                # str, shape (N,)
    sec_tag: np.ndarray                 # int32, shape (N,)
    sec_shape: np.ndarray               # int8, shape (N,)
    sec_model: np.ndarray               # int8, shape (N,)
    sec_def: np.ndarray                 # object, shape (N,)
    mats_idx: np.ndarray                # int32, shape (N,6)
    mat_type: np.ndarray                # int8, shape (N,)
    integration_type: np.ndarray        # int8, shape (N,)
    integration_tag: np.ndarray         # int32, shape (N,)
    aggregated_sec_idx: np.ndarray      # int32, shape (N,)
    dimensions: np.ndarray              # float64, shape (N,Max.columns)
    properties: np.ndarray              # float64, shape (N,12)

    def name_to_idx(self, names):
        lookup = dict(zip(self.sec_name, self.index))
        result = np.full(len(names), -1, dtype=np.int32)
        for i, name in enumerate(names):
            if name is None:
                continue
            name = str(name).strip()
            if not name or name.lower() in {"none", "nan"}:
                continue
            try:
                result[i] = lookup[name]
            except KeyError:
                raise ValidationError(f"Frame Section '{name}' does not exist") from None
        return result
    
# PROPERTIES: SLAB SECTIONS
@dataclass(slots=True, frozen=True)
class SlabSections:
    index: np.ndarray                   # int32, shape (N,)
    sec_name: np.ndarray                # str, shape (N,)
    mats_idx: np.ndarray                # int32, shape (N,1)
    mat_type: np.ndarray                # int8, shape (N,)
    dimensions: np.ndarray              # float64, shape (N,)

    def name_to_idx(self, names):
        lookup = dict(zip(self.sec_name, self.index))
        result = np.full(len(names), -1, dtype=np.int32)
        for i, name in enumerate(names):
            if name is None:
                continue
            name = str(name).strip()
            if not name or name.lower() in {"none", "nan"}:
                continue
            try:
                result[i] = lookup[name]
            except KeyError:
                raise ValidationError(f"Slab Section '{name}' does not exist") from None
        return result

    @classmethod
    def empty(cls):
        return cls(
            index=np.empty(0, dtype=np.int32),
            sec_name=np.empty(0, dtype="U32"),
            mats_idx=np.empty((0, 1), dtype=np.int32),
            mat_type=np.empty(0, dtype=np.int8),            
            dimensions=np.empty((0, 1), dtype=np.float64),
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
    node_tag: np.ndarray                # int32, shape (N,)
    coords: np.ndarray                  # float64, shape (N,3)
    generated_source: np.ndarray        # int32, shape (N,)
    generated_from: np.ndarray          # str, shape (N,)
    name_to_idx: dict[str, np.int32]
    tag_to_idx: dict[np.int32, np.int32]

@dataclass(slots=True, frozen=True)
class Elements:
    index: np.ndarray                   # int32, shape (N,)
    unique_name: np.ndarray             # str, shape (N,)
    element_tag: np.ndarray             # int32, shape (N,)
    end_nodes_idx: np.ndarray           # int32, shape (N,2)
    element_type: np.ndarray            # int8, shape(N,)
    sec_idx: np.ndarray                 # int32, shape (N,)
    centroids: np.ndarray               # float64, shape (N,3)
    length: np.ndarray                  # float64, shape (N,)
    rotation_matrices: np.ndarray       # int32, shape (N,3,3) for 3D or (N,2,2) for 2D
    transformation_tag: np.ndarray      # int32, shape (N,)
    elements_connectivity: np.ndarray   # int32, shape (N,Max. connections)
    shared_connected_nodes: np.ndarray  # int32, shape (N,Max. connections)
    current_elements_end: np.ndarray    # int32, shape (N,Max. connections)
    neighbour_elements_end: np.ndarray  # int32, shape (N,Max. connections)
    rigid_zone_factor: np.ndarray       # float64, shape (N,)
    offsets_length: np.ndarray          # float64, shape (N,2)
    end_offsets: np.ndarray             # float64, shape (N,6)
    name_to_idx: dict[str, np.int32]
    tag_to_idx: dict[np.int32, np.int32]

@dataclass(slots=True, frozen=True)
class ZeroLengthElements:
    index: np.ndarray                   # int32, shape (N,)
    unique_name: np.ndarray             # str, shape (N,)
    element_tag: np.ndarray             # int32, shape (N,)
    end_nodes_idx: np.ndarray           # int32, shape (N,2)
    element_type: np.ndarray            # str, shape(N,)
    rotation_matrices: np.ndarray       # int32, shape (N,3,3) for 3D or (N,2,2) for 2D
    name_to_idx: dict[str, np.int32]
    tag_to_idx: dict[np.int32, np.int32]

@dataclass(slots=True, frozen=True)
class Shells:
    index: np.ndarray                   # int32, shape (N,)
    unique_name: np.ndarray             # str, shape (N,)
    elements_idx: np.ndarray            # int32, shape (N,4)
    nodes_idx: np.ndarray               # int32, shape (N,4)
    element_type: np.ndarray            # int8, shape(N,)
    sec_idx: np.ndarray                 # int32, shape (N,)
    name_to_idx: dict[str, np.int32]

# PROPERTIES: RESTRAINTS
@dataclass(slots=True, frozen=True)
class Restraints:
    node_idx: np.ndarray                # int32, shape (N,)
    node_name: np.ndarray               # str, shape (N,)
    node_tag: np.ndarray                # int32, shape (N,)
    dofs: np.ndarray                    # int32, shape (N,6)

# LOADS: NODAL LOADS
@dataclass(slots=True, frozen=True)
class NodalLoads:
    node_tag: np.ndarray                # int32, shape (N,)
    loadcase: np.ndarray                # int32, shape (N,)
    loads: np.ndarray                   # float64, shape (N,6)

    @classmethod
    def empty(cls):
        return cls(
            node_tag=np.empty(0, dtype=np.int32),
            loadcase=np.empty(0, dtype=np.int32),
            loads=np.empty((0, 6), dtype=np.float64),
        )

# LOADS: CONCENTRATED ELEMENT LOADS
@dataclass(slots=True, frozen=True)
class ConcentratedElementLoads:
    element_tag: np.ndarray             # int32, shape (N,)
    loadcase: np.ndarray                # int32, shape (N,)
    location: np.ndarray                # float64, shape (N,)
    loads: np.ndarray                   # float64, shape (N,3)

    @classmethod
    def empty(cls):
        return cls(
            element_tag=np.empty(0, dtype=np.int32),
            loadcase=np.empty(0, dtype=np.int32),
            location=np.empty(0, dtype=np.float64),
            loads=np.empty((0, 3), dtype=np.float64),
        )

# LOADS: DISTRIBUTED ELEMENT LOADS
@dataclass(slots=True, frozen=True)
class DistributedElementLoads:
    element_tag: np.ndarray             # int32, shape (N,)
    loadcase: np.ndarray                # int32, shape (N,)
    location: np.ndarray                # float64, shape (N,)
    loads: np.ndarray                   # float64, shape (N,3)

    @classmethod
    def empty(cls):
        return cls(
            element_tag=np.empty(0, dtype=np.int32),
            loadcase=np.empty(0, dtype=np.int32),
            location=np.empty((0, 2), dtype=np.float64),
            loads=np.empty((0, 2, 3), dtype=np.float64),
        )

# LOADS: SURFACE TO ELEMENT LOADS
@dataclass(slots=True, frozen=True)
class SurfaceToElementLoads:
    element_tag: np.ndarray             # int32, shape (N,)
    loadcase: np.ndarray                # int32, shape (N,)
    location: np.ndarray                # float64, shape (N,)
    loads: np.ndarray                   # float64, shape (N,3)

    @classmethod
    def empty(cls):
        return cls(
            element_tag=np.empty(0, dtype=np.int32),
            loadcase=np.empty(0, dtype=np.int32),
            location=np.empty(0, dtype=np.float64),
            loads=np.empty((0, 3), dtype=np.float64),
        )

# MODEL DATA
@dataclass(slots=True)
class ModelData:
    filepath_information: FilePathInformation
    project_information: ProjectInformation
    userdefined_units: UserDefinedUnits
    analysis_preferences: AnalysisPreferences
    materials: Materials
    frame_sections: FrameSections
    slab_sections: SlabSections
    storeys: Storeys
    nodes: Nodes
    elements: Elements
    zerolength_elements: ZeroLengthElements
    shells: Shells
    restraints: Restraints
    nodal_loads: NodalLoads
    concentrated_element_loads: ConcentratedElementLoads
    distributed_element_loads: DistributedElementLoads
    surface_to_element_loads: SurfaceToElementLoads

    @classmethod
    def empty(cls):
        return cls(
            filepath_information = None,
            project_information = None,
            userdefined_units = None,
            analysis_preferences = None,
            materials = None,
            frame_sections = None,
            slab_sections = None,
            storeys = None,
            nodes = None,
            elements = None,
            zerolength_elements = None,
            shells = None,
            restraints = None,
            nodal_loads = None,
            concentrated_element_loads = None,
            distributed_element_loads = None,
            surface_to_element_loads = None,
        )