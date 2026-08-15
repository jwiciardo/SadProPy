import numpy as np
from ..preprocessing_class_index import SteelElasticProperties, Steel02Properties, Steel02MinMaxProperties

class SteelElastic:
    properties = SteelElasticProperties
    @staticmethod
    def translate(data, units):
        Unitweight = units.unitweight(values=data["Unitweight"])
        E = units.stress(values=data["E"])
        nu = np.asarray(data["nu"], dtype=np.float64)
        G = E / (2.0 * (1.0 + nu))
        fy = units.stress(values=data["Prop1"])
        fu = units.stress(values=data["Prop2"])
        return np.column_stack((
            Unitweight,
            E,
            nu,
            G,
            fy,
            fu,
        ))

class Steel02:
    properties = Steel02Properties
    @staticmethod
    def translate(data, units):
        Unitweight = units.unitweight(values=data["Unitweight"])
        E = units.stress(values=data["E"])
        nu = np.asarray(data["nu"], dtype=np.float64)
        G = E / (2.0 * (1.0 + nu))
        fy = units.stress(values=data["Prop1"])
        fu = units.stress(values=data["Prop2"])
        eu = np.asarray(data["Prop3"], dtype=np.float64)
        ey = fy / E
        eoffset = ey + 0.002
        Epy = (fu - fy) / (eu - eoffset)
        b = np.asarray(data["Prop4"], dtype=np.float64) 
        b = np.where(
            b != 0.0,
            b, 
            Epy / E,
        )
        R0 = np.asarray(data["Prop5"], dtype=np.float64)
        cR1 = np.asarray(data["Prop6"], dtype=np.float64)
        cR2 = np.asarray(data["Prop7"], dtype=np.float64)
        a1 = np.asarray(data["Prop8"], dtype=np.float64)
        a2 = np.asarray(data["Prop9"], dtype=np.float64)
        a3 = np.asarray(data["Prop10"], dtype=np.float64)
        a4 = np.asarray(data["Prop11"], dtype=np.float64)
        f_init = units.stress(values=data["Prop12"])
        return np.column_stack((
            Unitweight,
            E,
            nu,
            G,
            fy,
            fu,
            eu,
            b,
            R0,
            cR1,
            cR2,
            a1,
            a2,
            a3,
            a4,
            f_init,
        ))

class Steel02MinMax:
    properties = Steel02MinMaxProperties
    @staticmethod
    def translate(data, units):
        Unitweight = units.unitweight(values=data["Unitweight"])
        E = units.stress(values=data["E"])
        nu = np.asarray(data["nu"], dtype=np.float64)
        G = E / (2.0 * (1.0 + nu))
        fy = units.stress(values=data["Prop1"])
        fu = units.stress(values=data["Prop2"])
        eu = np.asarray(data["Prop3"], dtype=np.float64)
        ey = fy / E
        eoffset = ey + 0.002
        Epy = (fu - fy) / (eu - eoffset)
        b = np.asarray(data["Prop4"], dtype=np.float64) 
        b = np.where(
            b != 0.0,
            b, 
            Epy / E,
        )
        R0 = np.asarray(data["Prop5"], dtype=np.float64)
        cR1 = np.asarray(data["Prop6"], dtype=np.float64)
        cR2 = np.asarray(data["Prop7"], dtype=np.float64)
        a1 = np.asarray(data["Prop8"], dtype=np.float64)
        a2 = np.asarray(data["Prop9"], dtype=np.float64)
        a3 = np.asarray(data["Prop10"], dtype=np.float64)
        a4 = np.asarray(data["Prop11"], dtype=np.float64)
        f_init = units.stress(values=data["Prop12"])
        ecmax = units.stress(values=data["Prop13"])
        etmax = units.stress(values=data["Prop14"])
        return np.column_stack((
            Unitweight,
            E,
            nu,
            G,
            fy,
            fu,
            eu,
            b,
            R0,
            cR1,
            cR2,
            a1,
            a2,
            a3,
            a4,
            f_init,
            -ecmax,
            etmax,
        ))
