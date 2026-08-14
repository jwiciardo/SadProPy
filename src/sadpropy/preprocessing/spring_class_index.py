import numpy as np
from enum import IntEnum

class SpringIMKBilinearProperties(IntEnum):
    Unitweight = 0
    E = 1
    nu = 2
    G = 3
    K0 = 4
    asPos = 5
    asNeg = 6
    MyPos = 7
    MyNeg = 8
    MuPos = 9
    MuNeg = 10
    LamdaS = 11
    LamdaC = 12
    LamdaA = 13
    LamdaK = 14
    cS = 15
    cC = 16
    cA = 17
    cK = 18
    thetapPos = 19
    thetapNeg = 20
    thetapcPos = 21
    thetapcNeg = 22
    ResPos = 23
    ResNeg = 24
    thetauPos = 25
    thetauNeg = 26
    DPos = 27
    DNeg = 28
    nFactor = 29
    Count = 30 # Total number of properties

class SpringIMKPeakOrientedProperties(IntEnum):
    Unitweight = 0
    E = 1
    nu = 2
    G = 3
    K0 = 4
    asPos = 5
    asNeg = 6
    MyPos = 7
    MyNeg = 8
    MuPos = 9
    MuNeg = 10
    LamdaS = 11
    LamdaC = 12
    LamdaA = 13
    LamdaK = 14
    cS = 15
    cC = 16
    cA = 17
    cK = 18
    thetapPos = 19
    thetapNeg = 20
    thetapcPos = 21
    thetapcNeg = 22
    ResPos = 23
    ResNeg = 24
    thetauPos = 25
    thetauNeg = 26
    DPos = 27
    DNeg = 28
    Count = 29 # Total number of properties

class SpringIMKPinchingProperties(IntEnum):
    Unitweight = 0
    E = 1
    nu = 2
    G = 3
    K0 = 4
    asPos = 5
    asNeg = 6
    MyPos = 7
    MyNeg = 8
    MuPos = 9
    MuNeg = 10
    LamdaS = 11
    LamdaC = 12
    LamdaA = 13
    LamdaK = 14
    cS = 15
    cC = 16
    cA = 17
    cK = 18
    thetapPos = 19
    thetapNeg = 20
    thetapcPos = 21
    thetapcNeg = 22
    ResPos = 23
    ResNeg = 24
    thetauPos = 25
    thetauNeg = 26
    DPos = 27
    DNeg = 28
    FprPos = 29
    FprNeg = 30
    Apinch = 31
    Count = 32 # Total number of properties

class SpringIMKBilinear:
    properties = SpringIMKBilinearProperties
    @staticmethod
    def translate(data, units):
        Unitweight = units.unitweight(values=data["Unitweight"])
        E = units.stress(values=data["E"])
        nu = np.asarray(data["nu"], dtype=np.float64)
        G = E / (2.0 * (1.0 + nu))
        K0 = units.rotational_stiffness(values=data["Prop1"])
        fu = units.stress(values=data["Prop2"])
        my_pos = units.moment(values=data["Prop4"])
        my_neg = units.moment(values=data["Prop5"])
        theta_e_pos = my_pos / K0
        theta_e_neg = my_neg / K0
        mu_pos = units.moment(values=data["Prop6"])
        mu_neg = units.moment(values=data["Prop7"])
        return np.column_stack((
            Unitweight,
            E,
            nu,
            G,
        ))
