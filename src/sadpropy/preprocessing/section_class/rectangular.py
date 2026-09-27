import numpy as np
from ..preprocessing_class_index import RectangularElasticDimensions, RectangularConcreteFiberDimensions
from ..preprocessing_object._section import _rectangular_elastic_props, _rectangular_concrete_fiber_props
from ...core._ops_fiber_section import _rectangular_concrete_fiber_model

class RectangularElastic:
    dimensions = RectangularElasticDimensions
    compute = staticmethod(_rectangular_elastic_props)
    @staticmethod
    def translate(data, converter):
        h = converter.length(values=data["Dim1"])
        b = converter.length(values=data["Dim2"])
        return np.column_stack((
            h,
            b,
        ))

class RectangularConcreteFiber:
    dimensions = RectangularConcreteFiberDimensions
    compute = staticmethod(_rectangular_concrete_fiber_props)
    generate_fiber_model = staticmethod(_rectangular_concrete_fiber_model)
    @staticmethod
    def translate(data, converter):
        h = converter.length(values=data["Dim1"])
        b = converter.length(values=data["Dim2"])
        cover = converter.length(values=data["FiberProp1"])
        barDiaHoop = converter.length(values=data["FiberProp2"])
        barDiaTop = converter.length(values=data["FiberProp3"])
        barDiaBot = converter.length(values=data["FiberProp4"])
        barDiaInt = converter.length(values=data["FiberProp5"])
        nBarsTop = np.asarray(data["FiberProp6"], dtype=np.float64)
        nBarsBot = np.asarray(data["FiberProp7"], dtype=np.float64)
        nBarsInt = np.asarray(data["FiberProp8"], dtype=np.float64)
        return np.column_stack((
            h,
            b,
            cover,
            barDiaHoop,
            barDiaTop,
            barDiaBot,
            barDiaInt,
            nBarsTop,
            nBarsBot,
            nBarsInt,
        ))