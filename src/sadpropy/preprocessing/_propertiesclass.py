from enum import IntEnum
from dataclasses import dataclass
from sadpropy.utility._exceptions import ValidationError

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
    H = 0
    B = 1
    A = 2
    AVY = 3
    AVZ = 4
    IZ = 5
    IY = 6
    JXX = 7
    ALPHAY = 8
    ALPHAZ = 9


class FiberSectionProperties(IntEnum):
    H = 0
    B = 1
    A = 2
    AVY = 3
    AVZ = 4
    IZ = 5
    IY = 6
    JXX = 7
    ALPHAY = 8
    ALPHAZ = 9

class PropertiesRegistry:
    MATERIALS = {
        int(0): MaterialProperties,
        int(1): Concrete04Properties,
        int(2): Steel02Properties,
        int(3): MinMaxProperties,
        int(4): IMKProperties,
    }

    def _get_materialproperties(self, mat_class):
        return self.MATERIALS[mat_class]

class MaterialClass(IntEnum):
    Materials = 0
    Mat_Concrete04 = 1
    Mat_Steel02 = 2
    Mat_MinMax = 3
    Mat_IMK = 4