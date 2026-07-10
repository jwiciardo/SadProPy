from enum import IntEnum

class MaterialProperties(IntEnum):
    UNITWEIGHT = 0
    E = 1
    NU = 2
    G = 3
    FC = 4
    FY = 5
    FU = 6
 
class Concrete04Properties(IntEnum):
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

class Steel02Properties(IntEnum):
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

class MinMaxProperties(IntEnum):
    UNITWEIGHT = 0
    E = 1
    NU = 2
    G = 3
    ECMAX = 4
    ETMAX = 5

class IMKProperties(IntEnum):
    K0 = 0
    ASPOS = 1
    ASNEG = 2
    MYPOS = 3
    MYNEG = 4
    FPRPOS = 5
    FPRNEG = 6
    APINCH = 7
    NFACTOR = 8
    LAMDAS = 9
    LAMDAC = 10
    LAMDAA = 11
    LAMDAK = 12
    CS = 13
    CC= 14
    CA = 15
    CK = 16
    THETAPPOS = 17
    THETAPNEG = 18
    THETAPCPOS = 19
    THETAPCNEG = 20
    RESPOS = 21
    RESNEG = 22
    THETAUPOS = 23
    THETAUNEG = 24
    DPOS = 25
    DNEG = 26
