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
    thetauPos = 23
    thetauNeg = 24
    ResPos = 25
    ResNeg = 26
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
    thetauPos = 23
    thetauNeg = 24
    ResPos = 25
    ResNeg = 26
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
    thetauPos = 23
    thetauNeg = 24
    ResPos = 25
    ResNeg = 26
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
        my_pos = units.moment(values=data["Prop4"])
        my_neg = units.moment(values=data["Prop5"])
        theta_e_pos = my_pos / K0
        theta_e_neg = my_neg / K0
        mu_pos = units.moment(values=data["Prop6"])
        mu_neg = units.moment(values=data["Prop7"])
        lamda_S = np.asarray(data["Prop8"], dtype=np.float64)
        lamda_C = np.asarray(data["Prop9"], dtype=np.float64)
        lamda_A = np.asarray(data["Prop10"], dtype=np.float64)
        lamda_K = np.asarray(data["Prop11"], dtype=np.float64)
        c_S = np.asarray(data["Prop12"], dtype=np.float64)
        c_C = np.asarray(data["Prop13"], dtype=np.float64)
        c_A = np.asarray(data["Prop14"], dtype=np.float64)
        c_K = np.asarray(data["Prop15"], dtype=np.float64)
        theta_p_pos = units.angle(values=data["Prop16"])
        theta_p_neg = units.angle(values=data["Prop17"])
        Kpy_pos = (mu_pos - my_pos) / (theta_p_pos - theta_e_pos)
        Kpy_neg = (mu_neg - my_neg) / (theta_p_neg - theta_e_neg)
        as_pos = np.asarray(data["Prop2"], dtype=np.float64)
        as_pos = np.where(
            as_pos != 0.0,
            as_pos, 
            K0 / Kpy_pos,
        )
        as_neg = np.asarray(data["Prop3"], dtype=np.float64)
        as_neg = np.where(
            as_neg != 0.0,
            as_neg, 
            K0 / Kpy_neg,
        )
        theta_pc_pos = units.angle(values=data["Prop18"])
        theta_pc_neg = units.angle(values=data["Prop19"])
        theta_u_pos = units.angle(values=data["Prop20"])
        theta_u_neg = units.angle(values=data["Prop21"])
        res_pos = np.asarray(data["Prop22"], dtype=np.float64)
        res_neg = np.asarray(data["Prop23"], dtype=np.float64)
        D_pos = np.asarray(data["Prop24"], dtype=np.float64)
        D_neg = np.asarray(data["Prop25"], dtype=np.float64)
        nfactor = np.asarray(data["Prop26"], dtype=np.float64)
        return np.column_stack((
            Unitweight,
            E,
            nu,
            G,
            K0,
            as_pos,
            as_neg,
            my_pos,
            my_neg,
            mu_pos,
            mu_neg,
            lamda_S,
            lamda_C,
            lamda_A,
            lamda_K,
            c_S,
            c_C,
            c_A,
            c_K,
            theta_p_pos,
            theta_p_neg,
            theta_pc_pos,
            theta_pc_neg,
            theta_u_pos,
            theta_u_neg,
            res_pos,
            res_neg,
            D_pos,
            D_neg,
            nfactor,
        ))

class SpringIMKPeakOriented:
    properties = SpringIMKPeakOrientedProperties
    @staticmethod
    def translate(data, units):
        Unitweight = units.unitweight(values=data["Unitweight"])
        E = units.stress(values=data["E"])
        nu = np.asarray(data["nu"], dtype=np.float64)
        G = E / (2.0 * (1.0 + nu))
        K0 = units.rotational_stiffness(values=data["Prop1"])
        my_pos = units.moment(values=data["Prop4"])
        my_neg = units.moment(values=data["Prop5"])
        theta_e_pos = my_pos / K0
        theta_e_neg = my_neg / K0
        mu_pos = units.moment(values=data["Prop6"])
        mu_neg = units.moment(values=data["Prop7"])
        lamda_S = np.asarray(data["Prop8"], dtype=np.float64)
        lamda_C = np.asarray(data["Prop9"], dtype=np.float64)
        lamda_A = np.asarray(data["Prop10"], dtype=np.float64)
        lamda_K = np.asarray(data["Prop11"], dtype=np.float64)
        c_S = np.asarray(data["Prop12"], dtype=np.float64)
        c_C = np.asarray(data["Prop13"], dtype=np.float64)
        c_A = np.asarray(data["Prop14"], dtype=np.float64)
        c_K = np.asarray(data["Prop15"], dtype=np.float64)
        theta_p_pos = units.angle(values=data["Prop16"])
        theta_p_neg = units.angle(values=data["Prop17"])
        Kpy_pos = (mu_pos - my_pos) / (theta_p_pos - theta_e_pos)
        Kpy_neg = (mu_neg - my_neg) / (theta_p_neg - theta_e_neg)
        as_pos = np.asarray(data["Prop2"], dtype=np.float64)
        as_pos = np.where(
            as_pos != 0.0,
            as_pos, 
            K0 / Kpy_pos,
        )
        as_neg = np.asarray(data["Prop3"], dtype=np.float64)
        as_neg = np.where(
            as_neg != 0.0,
            as_neg, 
            K0 / Kpy_neg,
        )
        theta_pc_pos = units.angle(values=data["Prop18"])
        theta_pc_neg = units.angle(values=data["Prop19"])
        theta_u_pos = units.angle(values=data["Prop20"])
        theta_u_neg = units.angle(values=data["Prop21"])
        res_pos = np.asarray(data["Prop22"], dtype=np.float64)
        res_neg = np.asarray(data["Prop23"], dtype=np.float64)
        D_pos = np.asarray(data["Prop24"], dtype=np.float64)
        D_neg = np.asarray(data["Prop25"], dtype=np.float64)
        return np.column_stack((
            Unitweight,
            E,
            nu,
            G,
            K0,
            as_pos,
            as_neg,
            my_pos,
            my_neg,
            mu_pos,
            mu_neg,
            lamda_S,
            lamda_C,
            lamda_A,
            lamda_K,
            c_S,
            c_C,
            c_A,
            c_K,
            theta_p_pos,
            theta_p_neg,
            theta_pc_pos,
            theta_pc_neg,
            theta_u_pos,
            theta_u_neg,
            res_pos,
            res_neg,
            D_pos,
            D_neg,
        ))

class SpringIMKPinching:
    properties = SpringIMKPinchingProperties
    @staticmethod
    def translate(data, units):
        Unitweight = units.unitweight(values=data["Unitweight"])
        E = units.stress(values=data["E"])
        nu = np.asarray(data["nu"], dtype=np.float64)
        G = E / (2.0 * (1.0 + nu))
        K0 = units.rotational_stiffness(values=data["Prop1"])
        my_pos = units.moment(values=data["Prop4"])
        my_neg = units.moment(values=data["Prop5"])
        theta_e_pos = my_pos / K0
        theta_e_neg = my_neg / K0
        mu_pos = units.moment(values=data["Prop6"])
        mu_neg = units.moment(values=data["Prop7"])
        lamda_S = np.asarray(data["Prop8"], dtype=np.float64)
        lamda_C = np.asarray(data["Prop9"], dtype=np.float64)
        lamda_A = np.asarray(data["Prop10"], dtype=np.float64)
        lamda_K = np.asarray(data["Prop11"], dtype=np.float64)
        c_S = np.asarray(data["Prop12"], dtype=np.float64)
        c_C = np.asarray(data["Prop13"], dtype=np.float64)
        c_A = np.asarray(data["Prop14"], dtype=np.float64)
        c_K = np.asarray(data["Prop15"], dtype=np.float64)
        theta_p_pos = units.angle(values=data["Prop16"])
        theta_p_neg = units.angle(values=data["Prop17"])
        Kpy_pos = (mu_pos - my_pos) / (theta_p_pos - theta_e_pos)
        Kpy_neg = (mu_neg - my_neg) / (theta_p_neg - theta_e_neg)
        as_pos = np.asarray(data["Prop2"], dtype=np.float64)
        as_pos = np.where(
            as_pos != 0.0,
            as_pos, 
            K0 / Kpy_pos,
        )
        as_neg = np.asarray(data["Prop3"], dtype=np.float64)
        as_neg = np.where(
            as_neg != 0.0,
            as_neg, 
            K0 / Kpy_neg,
        )
        theta_pc_pos = units.angle(values=data["Prop18"])
        theta_pc_neg = units.angle(values=data["Prop19"])
        theta_u_pos = units.angle(values=data["Prop20"])
        theta_u_neg = units.angle(values=data["Prop21"])
        res_pos = np.asarray(data["Prop22"], dtype=np.float64)
        res_neg = np.asarray(data["Prop23"], dtype=np.float64)
        D_pos = np.asarray(data["Prop24"], dtype=np.float64)
        D_neg = np.asarray(data["Prop25"], dtype=np.float64)
        fpr_pos = np.asarray(data["Prop26"], dtype=np.float64)
        fpr_neg = np.asarray(data["Prop27"], dtype=np.float64)
        a_pinch = np.asarray(data["Prop28"], dtype=np.float64)
        return np.column_stack((
            Unitweight,
            E,
            nu,
            G,
            K0,
            as_pos,
            as_neg,
            my_pos,
            my_neg,
            mu_pos,
            mu_neg,
            lamda_S,
            lamda_C,
            lamda_A,
            lamda_K,
            c_S,
            c_C,
            c_A,
            c_K,
            theta_p_pos,
            theta_p_neg,
            theta_pc_pos,
            theta_pc_neg,
            theta_u_pos,
            theta_u_neg,
            res_pos,
            res_neg,
            D_pos,
            D_neg,
            fpr_pos,
            fpr_neg,
            a_pinch,
        ))
