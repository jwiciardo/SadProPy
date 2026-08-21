import numpy as np
from ..preprocessing_class_index import AggregatorElasticProperties

class AggregatorElastic:
    properties = AggregatorElasticProperties
    @staticmethod
    def translate(data, converter):
        Unitweight = converter.unitweight(values=data["Unitweight"])
        E = converter.stress(values=data["E"])
        nu = np.asarray(data["nu"], dtype=np.float64)
        G = E / (2.0 * (1.0 + nu))
        EA = converter.axial_rigidity(values=data["Prop1"])
        EIz = converter.flexural_rigidity(values=data["Prop2"])
        GAvy = converter.shear_rigidity(values=data["Prop3"])
        EIy = converter.flexural_rigidity(values=data["Prop4"])
        GAvz = converter.shear_rigidity(values=data["Prop5"])
        GJxx = converter.torsional_rigidity(values=data["Prop6"])
        return np.column_stack((
            Unitweight,
            E,
            nu,
            G,
            EA,
            EIz,
            GAvy,
            EIy,
            GAvz,
            GJxx,
        ))