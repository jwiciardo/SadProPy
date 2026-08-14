import numpy as np
from enum import IntEnum

class ConcreteElasticProperties(IntEnum):
    Unitweight = 0
    E = 1
    nu = 2
    G = 3
    fc = 4
    Count = 5 # Total number of properties

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
    Count = 10 # Total number of properties

class Concrete04MinMaxProperties(IntEnum):
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
    ecmax = 10
    etmax = 11
    Count = 12 # Total number of properties

class ConcreteElastic:
    properties = ConcreteElasticProperties
    @staticmethod
    def translate(data, units):
        Unitweight = units.unitweight(values=data["Unitweight"])
        E = units.stress(values=data["E"])
        nu = np.asarray(data["nu"], dtype=np.float64)
        G = E / (2.0 * (1.0 + nu))
        fc = units.stress(values=data["Prop1"])
        return np.column_stack((
            Unitweight,
            E,
            nu,
            G,
            fc,
        ))

class Concrete04:
    properties = Concrete04Properties
    @staticmethod
    def translate(data, units):
        Unitweight = units.unitweight(values=data["Unitweight"])
        E = units.stress(values=data["E"])
        nu = np.asarray(data["nu"], dtype=np.float64)
        G = E / (2.0 * (1.0 + nu))
        fc = units.stress(values=data["Prop1"])
        epsc = np.asarray(data["Prop2"], dtype=np.float64)
        epscu = np.asarray(data["Prop3"], dtype=np.float64)
        fct = units.stress(values=data["Prop4"])
        et = np.where(
            np.asarray(data["Prop5"], dtype=np.float64) != 0.0,
            np.asarray(data["Prop5"], dtype=np.float64), 
            fct * epsc / fc,
        )
        beta = np.asarray(data["Prop6"], dtype=np.float64)
        return np.column_stack((
            Unitweight,
            E,
            nu,
            G,
            fc,
            epsc,
            epscu,
            fct,
            et,
            beta,
        ))

class Concrete04MinMax:
    properties = Concrete04MinMaxProperties
    @staticmethod
    def translate(data, units):
        Unitweight = units.unitweight(values=data["Unitweight"])
        E = units.stress(values=data["E"])
        nu = np.asarray(data["nu"], dtype=np.float64)
        G = E / (2.0 * (1.0 + nu))
        fc = units.stress(values=data["Prop1"])
        epsc = np.asarray(data["Prop2"], dtype=np.float64)
        epscu = np.asarray(data["Prop3"], dtype=np.float64)
        fct = units.stress(values=data["Prop4"])
        et = np.where(
            np.asarray(data["Prop5"], dtype=np.float64) != 0.0,
            np.asarray(data["Prop5"], dtype=np.float64), 
            fct * epsc / fc,
        )
        beta = np.asarray(data["Prop6"], dtype=np.float64)
        ecmax = np.asarray(data["Prop7"], dtype=np.float64)
        etmax = np.asarray(data["Prop8"], dtype=np.float64)
        return np.column_stack((
            Unitweight,
            E,
            nu,
            G,
            fc,
            epsc,
            epscu,
            fct,
            et,
            beta,
            ecmax,
            etmax,
        ))