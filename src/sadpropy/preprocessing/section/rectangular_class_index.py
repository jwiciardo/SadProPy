import numpy as np
from ..preprocessing_class_index import RectangularElasticDimensions, RectangularConcreteFiberDimensions
from .._section import _rectangular_elastic_props, _rectangular_concrete_fiber_props

class RectangularElastic:
    dimensions = RectangularElasticDimensions
    compute = staticmethod(_rectangular_elastic_props)
    @staticmethod
    def translate(data, units):
        h = units.length(values=data["Dim1"])
        b = units.length(values=data["Dim2"])
        return np.column_stack((
            h,
            b,
        ))

class RectangularConcreteFiber:
    dimensions = RectangularConcreteFiberDimensions
    compute = staticmethod(_rectangular_concrete_fiber_props)
    @staticmethod
    def translate(data, units):
        h = units.length(values=data["Dim1"])
        b = units.length(values=data["Dim2"])
        cover = units.length(values=data["FiberProp1"])
        barDiaHoop = units.length(values=data["FiberProp2"])
        barDiaTop = units.length(values=data["FiberProp3"])
        barDiaBot = units.length(values=data["FiberProp4"])
        barDiaInt = units.length(values=data["FiberProp5"])
        nBarsTop = np.asarray(data["FiberProp6"], dtype=np.int8)
        nBarsBot = np.asarray(data["FiberProp7"], dtype=np.int8)
        nBarsInt = np.asarray(data["FiberProp8"], dtype=np.int8)
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