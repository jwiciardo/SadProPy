import numpy as np
from dataclasses import dataclass

# LOAD DATA: ELEMENT LOAD DATA
@dataclass(slots=True, frozen=True)
class ElementLoadData:
    element_tag: np.ndarray             # int32, shape (N,)
    type_: np.ndarray                   # int8, shape (N,)
    values: np.ndarray                  # float64, shape (N,8)

# FORCE DATA: ELEMENT FORCE DATA
@dataclass(slots=True, frozen=True)
class ElementForceData:
    element_tag: np.ndarray             # int32, shape (N,)
    locations: np.ndarray               # float64, shape (N, Max.EvaluationPoints)
    P: np.ndarray                       # float64, shape (N, Max.EvaluationPoints)
    Vy: np.ndarray                      # float64, shape (N, Max.EvaluationPoints)
    Vz: np.ndarray                      # float64, shape (N, Max.EvaluationPoints)
    T: np.ndarray                       # float64, shape (N, Max.EvaluationPoints)
    My: np.ndarray                      # float64, shape (N, Max.EvaluationPoints)
    Mz: np.ndarray                      # float64, shape (N, Max.EvaluationPoints)

# OUTPUT DATA
@dataclass(slots=True)
class OutputData:
    element_load_data: ElementLoadData
    element_force_data: ElementForceData