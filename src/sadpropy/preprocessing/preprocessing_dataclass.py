import numpy as np
from dataclasses import dataclass
from ..utility import UserDefinedUnits
from ..utility.exception import ValidationError

# PROJECT
@dataclass(slots=True, frozen=True)
class FilePathInformation:
    parent_path: str
    output_path: str
    inputfile_path: str
    logfile_path: str

    @classmethod
    def empty(cls):
        return cls(
            parent_path = "",
            output_path = "",
            inputfile_path = "",
            logfile_path = "",
        )
    
@dataclass(slots=True, frozen=True)
class ProjectInformation:
    name: str
    desc: str
    ndim: int

    @classmethod
    def empty(cls):
        return cls(
            name = "",
            desc = "",
            ndim = 0,
        )
    
@dataclass(slots=True, frozen=True)
class AnalysisPreferences:
    is_nonlinear_analysis: bool
    is_pdelta: bool
    mass_source_ref: int

    @classmethod
    def empty(cls):
        return cls(
            is_nonlinear_analysis = None,
            is_pdelta = None,
            mass_source_ref = 0,
        )
    
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
        # Scalar case
        if np.isscalar(names):
            if names is None:
                return -1
            name = str(names).strip()
            if not name or name.lower() in {"none", "nan"}:
                return -1
            try:
                return lookup[name]
            except KeyError:
                raise ValidationError(f"Material '{name}' does not exist") from None

        # Array case
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

    @classmethod
    def empty(cls):
        return cls(
            index = np.empty(0, dtype=np.int32),
            mat_name = np.empty(0, dtype="U32"),
            mat_tag = np.empty(0, dtype=np.int32),
            mat_type = np.empty(0, dtype=np.int8),            
            mat_model = np.empty(0, dtype=np.int8),
            mat_def = np.empty(0, dtype=object),
            properties = np.empty((0, 1), dtype=np.float64),
        )
    
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
    integration_def: np.ndarray         # object, shape (N,)
    integration_points: np.ndarray      # int32, shape (N,)
    integration_tag: np.ndarray         # int32, shape (N,)
    aggregated_sec_idx: np.ndarray      # int32, shape (N,)
    dimensions: np.ndarray              # float64, shape (N,Max.columns)
    properties: np.ndarray              # float64, shape (N,12)

    def name_to_idx(self, names):
        lookup = dict(zip(self.sec_name, self.index))
        # Scalar case
        if np.isscalar(names):
            if names is None:
                return -1
            name = str(names).strip()
            if not name or name.lower() in {"none", "nan"}:
                return -1
            try:
                return lookup[name]
            except KeyError:
                raise ValidationError(f"Section '{name}' does not exist") from None

        # Array case
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
                raise ValidationError(f"Section '{name}' does not exist") from None
        return result

    @classmethod
    def empty(cls):
        return cls(
            index = np.empty(0, dtype=np.int32),
            sec_name = np.empty(0, dtype="U32"),
            sec_tag = np.empty(0, dtype=np.int32),
            sec_shape = np.empty(0, dtype=np.int8),            
            sec_model = np.empty(0, dtype=np.int8),
            sec_def = np.empty(0, dtype=object),
            mats_idx = np.empty((0, 6), dtype=np.int32),
            mat_type = np.empty(0, dtype=np.int8),
            integration_type = np.empty(0, dtype=np.int8),
            integration_def = np.empty(0, dtype=object),
            integration_points = np.empty(0, dtype=np.int32),
            integration_tag = np.empty(0, dtype=np.int32),
            aggregated_sec_idx = np.empty(0, dtype=np.int32),
            dimensions = np.empty((0, 1), dtype=object),
            properties = np.empty((0, 12), dtype=np.float64),
        )
    
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
        # Scalar case
        if np.isscalar(names):
            if names is None:
                return -1
            name = str(names).strip()
            if not name or name.lower() in {"none", "nan"}:
                return -1
            try:
                return lookup[name]
            except KeyError:
                raise ValidationError(f"Section '{name}' does not exist") from None

        # Array case
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
                raise ValidationError(f"Section '{name}' does not exist") from None
        return result

    @classmethod
    def empty(cls):
        return cls(
            index = np.empty(0, dtype=np.int32),
            sec_name = np.empty(0, dtype="U32"),
            mats_idx = np.empty((0, 1), dtype=np.int32),
            mat_type = np.empty(0, dtype=np.int8),            
            dimensions = np.empty((0, 1), dtype=np.float64),
        )
    
# STRUCTURE DATA
@dataclass(slots=True, frozen=True)
class Storeys:
    name: np.ndarray                    # str, shape (N,)
    height: np.ndarray                  # float64, shape (N,)
    elevation: np.ndarray               # float64, shpae(N,)

    @classmethod
    def empty(cls):
        return cls(
            name = np.empty(0, dtype="U15"),
            height = np.empty(0, dtype=np.float64),
            elevation = np.empty(0, dtype=np.float64),
        )
    
# STRUCTURAL OBJECTS
@dataclass(slots=True, frozen=True)
class Nodes:
    index: np.ndarray                   # int32, shape (N,)
    unique_name: np.ndarray             # str, shape (N,)
    node_tag: np.ndarray                # int32, shape (N,)
    coords: np.ndarray                  # float64, shape (N,3)
    generated_source: np.ndarray        # int32, shape (N,)
    generated_from: np.ndarray          # str, shape (N,)

    def name_to_idx(self, names):
        lookup = dict(zip(self.unique_name, self.index))
        # Scalar case
        if np.isscalar(names):
            if names is None:
                return -1
            name = str(names).strip()
            if not name or name.lower() in {"none", "nan"}:
                return -1
            try:
                return lookup[name]
            except KeyError:
                raise ValidationError(f"Node '{name}' does not exist") from None

        # Array case
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
                raise ValidationError(f"Node '{name}' does not exist") from None
        return result

    def tag_to_idx(self, tags):
        lookup = dict(zip(self.node_tag, self.index))
        # Scalar case
        if np.isscalar(tags):
            if tags is None:
                return -1
            if isinstance(tags, str):
                tag = tags.strip()
                if not tag or tag.lower() in {"none", "nan"}:
                    return -1
                try:
                    tag = int(tag)
                except ValueError:
                    raise ValidationError(f"Invalid node tag '{tags}'") from None
            else:
                tag = int(tags)
            try:
                return lookup[tag]
            except KeyError:
                raise ValidationError(f"Node tag '{tag}' does not exist") from None

        # Array case
        result = np.full(len(tags), -1, dtype=np.int32)
        for i, tag in enumerate(tags):
            if tag is None:
                continue
            if isinstance(tag, str):
                tag = tag.strip()
                if not tag or tag.lower() in {"none", "nan"}:
                    continue
                try:
                    tag = int(tag)
                except ValueError:
                    raise ValidationError(f"Invalid node tag '{tag}'") from None
            else:
                tag = int(tag)
            try:
                result[i] = lookup[tag]
            except KeyError:
                raise ValidationError(f"Node tag '{tag}' does not exist") from None
        return result

    @classmethod
    def empty(cls):
        return cls(
            index = np.empty(0, dtype=np.int32),
            unique_name = np.empty(0, dtype="U32"),
            node_tag = np.empty(0, dtype=np.int32),
            coords = np.empty((0, 3), dtype=np.float64),            
            generated_source = np.empty(0, dtype=np.int32),
            generated_from = np.empty(0, dtype="U32"),
        )
    
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
    elements_connectivity: np.ndarray   # int32, shape (N,Max. connections)
    shared_connected_nodes: np.ndarray  # int32, shape (N,Max. connections)
    current_elements_end: np.ndarray    # int32, shape (N,Max. connections)
    neighbour_elements_end: np.ndarray  # int32, shape (N,Max. connections)
    rigid_zone_factor: np.ndarray       # float64, shape (N,)
    offsets_length: np.ndarray          # float64, shape (N,2)
    end_offsets: np.ndarray             # float64, shape (N,6)
    transf_tag: np.ndarray              # int32, shape (N,)
    transf_vec: np.ndarray              # int32, shape (N,3)
    transf_offsets: np.ndarray          # int32, shape (N,6)
    transformation_tag: np.ndarray      # int32, shape (N,)
    selfweight: np.ndarray              # float64, shape (N,)

    def name_to_idx(self, names):
        lookup = dict(zip(self.unique_name, self.index))
        # Scalar case
        if np.isscalar(names):
            if names is None:
                return -1
            name = str(names).strip()
            if not name or name.lower() in {"none", "nan"}:
                return -1
            try:
                return lookup[name]
            except KeyError:
                raise ValidationError(f"Element '{name}' does not exist") from None

        # Array case
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
                raise ValidationError(f"Element '{name}' does not exist") from None
        return result

    def tag_to_idx(self, tags):
        lookup = dict(zip(self.element_tag, self.index))
        # Scalar case
        if np.isscalar(tags):
            if tags is None:
                return -1
            if isinstance(tags, str):
                tag = tags.strip()
                if not tag or tag.lower() in {"none", "nan"}:
                    return -1
                try:
                    tag = int(tag)
                except ValueError:
                    raise ValidationError(f"Invalid element tag '{tags}'") from None
            else:
                tag = int(tags)
            try:
                return lookup[tag]
            except KeyError:
                raise ValidationError(f"Element tag '{tag}' does not exist") from None

        # Array case
        result = np.full(len(tags), -1, dtype=np.int32)
        for i, tag in enumerate(tags):
            if tag is None:
                continue
            if isinstance(tag, str):
                tag = tag.strip()
                if not tag or tag.lower() in {"none", "nan"}:
                    continue
                try:
                    tag = int(tag)
                except ValueError:
                    raise ValidationError(f"Invalid element tag '{tag}'") from None
            else:
                tag = int(tag)
            try:
                result[i] = lookup[tag]
            except KeyError:
                raise ValidationError(f"Element tag '{tag}' does not exist") from None
        return result

    @classmethod
    def empty(cls):
        return cls(
            index = np.empty(0, dtype=np.int32),
            unique_name = np.empty(0, dtype="U32"),
            element_tag = np.empty(0, dtype=np.int32),
            end_nodes_idx = np.empty((0, 2), dtype=np.int32),
            element_type = np.empty(0, dtype=np.int8),   
            sec_idx = np.empty(0, dtype=np.int32),
            centroids = np.empty((0, 3), dtype=np.float64),
            length = np.empty(0, dtype=np.float64),
            rotation_matrices = np.empty((0, 3, 3), dtype=np.int32),
            elements_connectivity = np.empty((0, 1), dtype=np.int32),
            shared_connected_nodes = np.empty((0, 1), dtype=np.int32),
            current_elements_end = np.empty((0, 1), dtype=np.int32),
            neighbour_elements_end = np.empty((0, 1), dtype=np.int32),
            rigid_zone_factor = np.empty(0, dtype=np.float64),
            offsets_length = np.empty((0, 2), dtype=np.float64),
            end_offsets = np.empty((0, 6), dtype=np.float64),
            transf_tag = np.empty(0, dtype=np.int32),
            transf_vec = np.empty((0, 3), dtype=np.int32),
            transf_offsets = np.empty((0, 6), dtype=np.float64),
            transformation_tag = np.empty(0, dtype=np.int32),
            selfweight = np.empty(0, dtype=np.float64),
        )
    
@dataclass(slots=True, frozen=True)
class ZeroLengthElements:
    index: np.ndarray                   # int32, shape (N,)
    unique_name: np.ndarray             # str, shape (N,)
    element_tag: np.ndarray             # int32, shape (N,)
    end_nodes_idx: np.ndarray           # int32, shape (N,2)
    element_type: np.ndarray            # int8, shape(N,)
    rotation_matrices: np.ndarray       # int32, shape (N,3,3) for 3D or (N,2,2) for 2D

    def name_to_idx(self, names):
        lookup = dict(zip(self.unique_name, self.index))
        # Scalar case
        if np.isscalar(names):
            if names is None:
                return -1
            name = str(names).strip()
            if not name or name.lower() in {"none", "nan"}:
                return -1
            try:
                return lookup[name]
            except KeyError:
                raise ValidationError(f"Element '{name}' does not exist") from None

        # Array case
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
                raise ValidationError(f"Element '{name}' does not exist") from None
        return result

    def tag_to_idx(self, tags):
        lookup = dict(zip(self.element_tag, self.index))
        # Scalar case
        if np.isscalar(tags):
            if tags is None:
                return -1
            if isinstance(tags, str):
                tag = tags.strip()
                if not tag or tag.lower() in {"none", "nan"}:
                    return -1
                try:
                    tag = int(tag)
                except ValueError:
                    raise ValidationError(f"Invalid element tag '{tags}'") from None
            else:
                tag = int(tags)
            try:
                return lookup[tag]
            except KeyError:
                raise ValidationError(f"Element tag '{tag}' does not exist") from None

        # Array case
        result = np.full(len(tags), -1, dtype=np.int32)
        for i, tag in enumerate(tags):
            if tag is None:
                continue
            if isinstance(tag, str):
                tag = tag.strip()
                if not tag or tag.lower() in {"none", "nan"}:
                    continue
                try:
                    tag = int(tag)
                except ValueError:
                    raise ValidationError(f"Invalid element tag '{tag}'") from None
            else:
                tag = int(tag)
            try:
                result[i] = lookup[tag]
            except KeyError:
                raise ValidationError(f"Element tag '{tag}' does not exist") from None
        return result

    @classmethod
    def empty(cls):
        return cls(
            index = np.empty(0, dtype=np.int32),
            unique_name = np.empty(0, dtype="U15"),
            element_tag = np.empty(0, dtype=np.int32),
            end_nodes_idx = np.empty((0, 2), dtype=np.int32),
            element_type = np.empty(0, dtype=np.int8),
            rotation_matrices = np.empty((0, 3, 3), dtype=np.int32),
        )

@dataclass(slots=True, frozen=True)
class Shells:
    index: np.ndarray                   # int32, shape (N,)
    unique_name: np.ndarray             # str, shape (N,)
    elements_idx: np.ndarray            # int32, shape (N,4)
    nodes_idx: np.ndarray               # int32, shape (N,4)
    element_type: np.ndarray            # int8, shape(N,)
    sec_idx: np.ndarray                 # int32, shape (N,)
    area: np.ndarray                    # float64, shape (N,)
    selfweight: np.ndarray              # float64, shape (N,)

    def name_to_idx(self, names):
        lookup = dict(zip(self.unique_name, self.index))
        # Scalar case
        if np.isscalar(names):
            if names is None:
                return -1
            name = str(names).strip()
            if not name or name.lower() in {"none", "nan"}:
                return -1
            try:
                return lookup[name]
            except KeyError:
                raise ValidationError(f"Shell '{name}' does not exist") from None

        # Array case
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
                raise ValidationError(f"Shell '{name}' does not exist") from None
        return result

    @classmethod
    def empty(cls):
        return cls(
            index = np.empty(0, dtype=np.int32),
            unique_name = np.empty(0, dtype="U32"),
            elements_idx = np.empty((0, 4), dtype=np.int32),
            nodes_idx = np.empty((0, 4), dtype=np.int32),
            element_type = np.empty(0, dtype=np.int8),            
            sec_idx = np.empty(0, dtype=np.int32),
            area = np.empty(0, dtype=np.float64),
            selfweight = np.empty(0, dtype=np.float64),
        )
    
# PROPERTIES: RESTRAINTS
@dataclass(slots=True, frozen=True)
class Restraints:
    node_idx: np.ndarray                # int32, shape (N,)
    node_name: np.ndarray               # str, shape (N,)
    node_tag: np.ndarray                # int32, shape (N,)
    dofs: np.ndarray                    # int8, shape (N,6)

    @classmethod
    def empty(cls):
        return cls(
            node_idx = np.empty(0, dtype=np.int32),
            node_name = np.empty(0, dtype="U32"),
            node_tag = np.empty(0, dtype=np.int32),
            dofs = np.empty((0, 6), dtype=np.int8),
        )

# LOADS: LOAD CASES
@dataclass(slots=True, frozen=True)
class LoadCases:
    index: np.ndarray                           # int32, shape (N,)
    load_case_name: np.ndarray                  # str, shape (N,)
    load_case_type: np.ndarray                  # int8, shape (N,)
    load_types: np.ndarray                      # int8, shape (N,6)
    function_names: np.ndarray                  # str, shape (N,6)
    modal_combination_method: np.ndarray        # int8, shape (N,)
    directional_combination_type: np.ndarray    # int8, shpae (N,)
    parameters: np.ndarray                      # float64, shape (N,8)

    def name_to_idx(self, names):
        lookup = dict(zip(self.load_case_name, self.index))
        # Scalar case
        if np.isscalar(names):
            if names is None:
                return -1
            name = str(names).strip()
            if not name or name.lower() in {"none", "nan"}:
                return -1
            try:
                return lookup[name]
            except KeyError:
                raise ValidationError(f"Load case '{name}' does not exist") from None

        # Array case
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
                raise ValidationError(f"Load case '{name}' does not exist") from None
        return result
    
    @classmethod
    def empty(cls):
        return cls(
            index = np.empty(0, dtype=np.int32),
            load_Case_name = np.empty(0, dtype="U32"),
            load_case_type = np.empty(0, dtype=np.int8),
            load_types = np.empty((0, 6), dtype=np.int8),
            function_names = np.empty((0, 6), dtype="U64"),
            modal_combination_method = np.empty(0, dtype=np.int8),
            directional_combination_type = np.empty(0, dtype=np.int8),
            parameters = np.empty((0, 8), dtype=np.float64),
        )

# LOADS: LOAD COMBINATIONS
@dataclass(slots=True, frozen=True)
class LoadCombinations:
    index: np.ndarray                           # int32, shape (N,)
    load_combination_name: np.ndarray           # str, shape (N,)
    load_cases_idx: np.ndarray                 # int32, shape (N,10)
    scale_factors: np.ndarray                   # float64, shape (N,10)

    @classmethod
    def empty(cls):
        return cls(
            index = np.empty(0, dtype=np.int32),
            load_combination_name = np.empty(0, dtype="U32"),
            load_cases_idx = np.empty((0, 10), dtype=np.int32),
            scale_factors = np.empty((0, 10), dtype=np.float64),
        )

    
# LOADS: NODAL LOADS
@dataclass(slots=True, frozen=True)
class NodalLoads:
    node_tag: np.ndarray                # int32, shape (N,)
    loadcase: np.ndarray                # int8, shape (N,)
    loads: np.ndarray                   # float64, shape (N,6)

    @classmethod
    def empty(cls):
        return cls(
            node_tag = np.empty(0, dtype=np.int32),
            loadcase = np.empty(0, dtype=np.int8),
            loads = np.empty((0, 6), dtype=np.float64),
        )

# LOADS: CONCENTRATED ELEMENTAL LOADS
@dataclass(slots=True, frozen=True)
class ConcentratedElementalLoads:
    element_tag: np.ndarray             # int32, shape (N,)
    loadcase: np.ndarray                # int8, shape (N,)
    location: np.ndarray                # float64, shape (N,)
    loads: np.ndarray                   # float64, shape (N,3)

    @classmethod
    def empty(cls):
        return cls(
            element_tag = np.empty(0, dtype=np.int32),
            loadcase = np.empty(0, dtype=np.int8),
            location = np.empty(0, dtype=np.float64),
            loads = np.empty((0, 3), dtype=np.float64),
        )

# LOADS: DISTRIBUTED ELEMENTAL LOADS
@dataclass(slots=True, frozen=True)
class DistributedElementalLoads:
    element_tag: np.ndarray             # int32, shape (N,)
    loadcase: np.ndarray                # int8, shape (N,)
    location: np.ndarray                # float64, shape (N,)
    loads: np.ndarray                   # float64, shape (N,3)

    @classmethod
    def empty(cls):
        return cls(
            element_tag = np.empty(0, dtype=np.int32),
            loadcase = np.empty(0, dtype=np.int8),
            location = np.empty((0, 2), dtype=np.float64),
            loads = np.empty((0, 2, 3), dtype=np.float64),
        )

# LOADS: SHELL TO ELEMENTAL LOADS
@dataclass(slots=True, frozen=True)
class ShellToElementalLoads:
    element_tag: np.ndarray             # int32, shape (N,)
    loadcase: np.ndarray                # int8, shape (N,)
    location: np.ndarray                # float64, shape (N,)
    loads: np.ndarray                   # float64, shape (N,3)

    @classmethod
    def empty(cls):
        return cls(
            element_tag = np.empty(0, dtype=np.int32),
            loadcase = np.empty(0, dtype=np.int8),
            location = np.empty((0, 2), dtype=np.float64),
            loads = np.empty((0, 2, 3), dtype=np.float64),
        )

# LOADS: SELFWEIGHT TO ELEMENTAL LOADS
@dataclass(slots=True, frozen=True)
class SelfweightToElementalLoads:
    element_tag: np.ndarray             # int32, shape (N,)
    loadcase: np.ndarray                # int8, shape (N,)
    location: np.ndarray                # float64, shape (N,)
    loads: np.ndarray                   # float64, shape (N,3)

    @classmethod
    def empty(cls):
        return cls(
            element_tag = np.empty(0, dtype=np.int32),
            loadcase = np.empty(0, dtype=np.int8),
            location = np.empty((0, 2), dtype=np.float64),
            loads = np.empty((0, 2, 3), dtype=np.float64),
        )

# MASSES
@dataclass(slots=True, frozen=True)
class NodalMasses:
    node_tag: np.ndarray                # int32, shape (N,)
    weight: np.ndarray                  # float64, shape (N,)
    mass: np.ndarray                    # float64, shape (N,)

    @classmethod
    def empty(cls):
        return cls(
            node_tag = np.empty(0, dtype=np.int32),
            weight = np.empty(0, dtype=np.float64),
            mass = np.empty(0, dtype=np.float64),
        )

# DIAPHRAGMS
@dataclass(slots=True, frozen=True)
class Diaphragms:
    index: np.ndarray                   # int32, shape (N,)
    unique_name: np.ndarray             # str, shape (N,)
    diaph_tag: np.ndarray               # int32, shape (N,)
    coords: np.ndarray                  # float64, shape (N,3)
    dofs: np.ndarray                    # int8, shape (N,6)
    constrained_nodes_idx: np.ndarray   # int32, shape(N, N_node)
    constrained_nodes_tag: np.ndarray   # int32, shape(N, N_node)
    storey_mass: np.ndarray             # float64, shape (N,)

    @classmethod
    def empty(cls):
        return cls(
            node_idx = np.empty(0, dtype=np.int32),
            unique_name = np.empty(0, dtype="U32"),
            node_tag = np.empty(0, dtype=np.int32),
            coords = np.empty((0, 3), dtype=np.float64),
            dofs = np.empty((0, 6), dtype=np.int8),
            constrained_nodes_idx = np.empty(0, dtype=np.int32),
            constrained_nodes_tag = np.empty(0, dtype=np.int32),
            storey_mass = np.empty(0, dtype=np.float64),
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
    load_cases: LoadCases
    load_combinations: LoadCombinations
    nodal_loads: NodalLoads
    concentrated_elemental_loads: ConcentratedElementalLoads
    distributed_elemental_loads: DistributedElementalLoads
    shell_to_elemental_loads: ShellToElementalLoads
    selfweight_to_elemental_loads: SelfweightToElementalLoads
    nodal_masses: NodalMasses
    diaphragms: Diaphragms

    @classmethod
    def empty(cls):
        return cls(
            filepath_information = FilePathInformation.empty(),
            project_information = ProjectInformation.empty(),
            userdefined_units = UserDefinedUnits(
                force="kN",
                length="m",
                mass="kg",
                stress="MPa",
                time="s",
                angle="rad"
            ),
            analysis_preferences = AnalysisPreferences.empty(),
            materials = Materials.empty(),
            frame_sections = FrameSections.empty(),
            slab_sections = SlabSections.empty(),
            storeys = Storeys.empty(),
            nodes = Nodes.empty(),
            elements = Elements.empty(),
            zerolength_elements = ZeroLengthElements.empty(),
            shells = Shells.empty(),
            restraints = Restraints.empty(),
            load_cases = LoadCases.empty(),
            load_combinations = LoadCombinations.empty(),
            nodal_loads = NodalLoads.empty(),
            concentrated_elemental_loads = ConcentratedElementalLoads.empty(),
            distributed_elemental_loads = DistributedElementalLoads.empty(),
            shell_to_elemental_loads = ShellToElementalLoads.empty(),
            selfweight_to_elemental_loads = SelfweightToElementalLoads.empty(),
            nodal_masses = NodalMasses.empty(),
            diaphragms = Diaphragms.empty()
        )