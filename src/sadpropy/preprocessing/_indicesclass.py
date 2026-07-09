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

class Steel02Index(IntEnum):
    UNITWEIGHT = 0
    E = 1
    NU = 2
    G = 3
    FY = 4
    B = 5
    R0 = 6
    CR1 = 7
    CR2 = 8
    A1 = 9
    A2 = 10
    A3 = 11
    A4 = 12
    FINIT = 13
