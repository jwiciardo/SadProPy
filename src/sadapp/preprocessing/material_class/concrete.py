import numpy as np
from ..preprocessing_class_index import ConcreteElasticProperties, Concrete04Properties, Concrete04MinMaxProperties

class ConcreteElastic:
    properties = ConcreteElasticProperties
    @staticmethod
    def translate(data, converter):
        Unitweight = converter.unitweight(values=data["Unitweight"])
        E = converter.stress(values=data["E"])
        nu = np.asarray(data["nu"], dtype=np.float64)
        G = E / (2.0 * (1.0 + nu))
        fc = converter.stress(values=data["Prop1"])
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
    def translate(data, converter):
        Unitweight = converter.unitweight(values=data["Unitweight"])
        E = converter.stress(values=data["E"])
        nu = np.asarray(data["nu"], dtype=np.float64)
        G = E / (2.0 * (1.0 + nu))
        fc = converter.stress(values=data["Prop1"])
        epsc = np.asarray(data["Prop2"], dtype=np.float64)
        epscu = np.asarray(data["Prop3"], dtype=np.float64)
        fct = converter.stress(values=data["Prop4"])
        et = np.asarray(data["Prop5"], dtype=np.float64)
        et = np.where(
            et != 0.0,
            et,
            fct * epsc / fc,
        )
        beta = np.asarray(data["Prop6"], dtype=np.float64)
        return np.column_stack((
            Unitweight,
            E,
            nu,
            G,
            -fc,
            -epsc,
            -epscu,
            fct,
            et,
            beta,
        ))

class Concrete04MinMax:
    properties = Concrete04MinMaxProperties
    @staticmethod
    def translate(data, converter):
        Unitweight = converter.unitweight(values=data["Unitweight"])
        E = converter.stress(values=data["E"])
        nu = np.asarray(data["nu"], dtype=np.float64)
        G = E / (2.0 * (1.0 + nu))
        fc = converter.stress(values=data["Prop1"])
        epsc = np.asarray(data["Prop2"], dtype=np.float64)
        epscu = np.asarray(data["Prop3"], dtype=np.float64)
        fct = converter.stress(values=data["Prop4"])
        et = np.asarray(data["Prop5"], dtype=np.float64)
        et = np.where(
            et != 0.0,
            et,
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
            -fc,
            -epsc,
            -epscu,
            fct,
            et,
            beta,
            -ecmax,
            etmax,
        ))