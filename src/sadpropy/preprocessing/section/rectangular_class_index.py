import numpy as np
from enum import IntEnum

class RectangularElasticProperties(IntEnum):
    h = 0
    b = 1
    Count = 2 # Total number of properties

class RectangularFiberProperties(IntEnum):
    h = 0
    b = 1
    cover = 2
    barDiaHoop = 3
    barDiaTop = 4
    barDiaBot = 5
    barDiaInt = 6
    nBarsTop = 7
    nBarsBot = 8
    nBarsInt = 9
    Count = 10 # Total number of properties

class RectangularElastic:
    dimensions = RectangularElasticProperties
    @staticmethod
    def translate(data, units):
        h = units.length(values=data["Dim1"])
        b = units.length(values=data["Dim2"])
        return np.column_stack((
            h,
            b,
        ))

class RectangularFiber:
    dimensions = RectangularFiberProperties
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