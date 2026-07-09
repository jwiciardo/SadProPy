from enum import IntEnum

class MaterialIndex(IntEnum):
    UNITWEIGHT = 0
    E = 1
    NU = 2
    G = 3
    FC = 4
    FY = 5
    FU = 6
 
class Concrete04Index(IntEnum):
    UNITWEIGHT = 0
    E = 1
    NU = 2
    G = 3
    FC = 4
    EPSC = 5
    EPSCU = 6
    FCT = 7
    ET = 8
    BETA = 9
