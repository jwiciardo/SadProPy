import numpy as np
from enum import IntEnum

class MaterialProperties(IntEnum):
    Unitweight = 0
    E = 1
    nu = 2
    G = 3
    fc= 4
    fy = 5
    fu = 6
 
class Concrete04Properties(IntEnum):
    Unitweight = 0
    E = 1
    nu = 2
    G = 3
    fc = 4
    epsc = 5
    epscu = 6
    fct = 7
    et = 8
    beta = 9

class Steel02Properties(IntEnum):
    Unitweight = 0
    E = 1
    nu = 2
    G = 3
    fy = 4
    b = 5
    R0 = 6
    cR1 = 7
    cR2 = 8
    a1 = 9
    a2 = 10
    a3 = 11
    a4 = 12
    f_init = 13

class MinMaxProperties(IntEnum):
    Unitweight = 0
    E = 1
    nu = 2
    G = 3
    ecmax = 4
    etmax = 5

class IMKProperties(IntEnum):
    K0 = 0
    as_pos = 1
    as_neg = 2
    My_pos = 3
    My_neg = 4
    Fpr_pos = 5
    Fpr_neg = 6
    a_pinch = 7
    nFactor = 8
    Lamda_S = 9
    Lamda_C = 10
    Lamda_A = 11
    Lamda_K = 12
    c_S = 13
    c_C= 14
    c_A = 15
    c_K = 16
    theta_p_pos = 17
    theta_p_neg = 18
    theta_pc_pos = 19
    theta_pc_neg = 20
    Res_pos = 21
    Res_neg = 22
    theta_u_pos = 23
    theta_u_neg = 24
    D_pos = 25
    D_neg = 26

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
    MATERIALS = np.array([
        MaterialProperties, # Index 0
        Concrete04Properties, # Index 1
        Steel02Properties, # Index 2
        MinMaxProperties, # Index 3
    ], dtype=object)

    SPRING_MATERIALS = np.array([
            IMKProperties, # Index 0
        ], dtype=object)

    SECTIONS = np.array([
        FrameSectionProperties, # Index 0
        FiberSectionProperties, # Index 1
        SectionAggregatorProperties, # Index 2
    ], dtype=object)

    def _get_mat_props_class(self, mat_class):
        return self.MATERIALS[mat_class]

    def _get_spring_mat_props_class(self, mat_class):
            return self.SPRING_MATERIALS[mat_class]
    
    def _get_sec_props_class(self, sec_class):
        return self.SECTIONS[sec_class]

class SectionShape:
    shape = {
        "Rectangular": 0,
        "Circular": 1,
        "Wide Flange": 2,
        "Channel": 3,
        "Rectangular Hollow": 4,
        "Circular Hollow": 5,
    }

    def _get_sec_shape_class(self, shape):
        return self.shape[shape]

class NodeSource(IntEnum):
    USR = 0 # Userdefined Generated source
    ZLE = 1 # Zero Length Auto Generated source
    PZ = 2 # Panel Zone Auto Generated source

class ConnectionEnd(IntEnum):
    I_End = 0
    J_End = 1

class LoadCaseType:
    case = {
        "D": 0,
        "L": 1,
        "Lr": 2,
        "E": 3,
        "W": 4,
    }
    def _get_loadcase_class(self, loadcase):
        return self.case[loadcase]

class LoadDirection:
    direction3D = {
        "Global-X": (1, 0, 0),
        "Global-Y": (0, 1, 0),
        "Gravity": (0, 0, 1), 
        "Local-x": (1, 0, 0),
        "Local-y": (0, 1, 0),
        "Local-z": (0, 0, 1),
    }
    def _get_load_direction3D_class(self, direction):
        return self.direction3D[direction]

    direction2D = {
        "Global-X": (1, 0),
        "Gravity": (0, 1),
        "Local-x": (1, 0),
        "Local-y": (0, 1),
    }
    def _get_load_direction2D_class(self, direction):
        return self.direction2D[direction]