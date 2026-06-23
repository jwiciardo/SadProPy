from enum import Enum
from math import pi
from dataclasses import dataclass

__all__ = ["UnitConverter", "UnitRegistry", "UnitSystem"]

class Dimension(Enum):
    FORCE = "force"
    LENGTH = "length"
    AREA = "area"
    VOLUME = "volume"
    LENGTH4 = "length4"
    MASS = "mass"
    STRESS = "stress"
    MOMENT = "moment"
    UNITWEIGHT = "unitweight"
    SURFACE_LOAD = "surface_load"
    DISTRIBUTED_LINE_LOAD = "distributed_line_load"
    CONCENTRATED_LINE_LOAD = "concentrated_line_load"
    POINT_LOAD = "point_load"
    TIME = "time"
    ANGLE = "angle"

class UnitRegistry:
    UNITS = {
        # Force
        "N":   (Dimension.FORCE, 1.0),
        "kN":  (Dimension.FORCE, 1e3),
        "MN":  (Dimension.FORCE, 1e6),
        "kgf": (Dimension.FORCE, 9.80665),
        "tonf": (Dimension.FORCE, 9.80665e3),
        "lbf":  (Dimension.FORCE, 4.44822),
        "kipf":  (Dimension.FORCE, 4.44822e3),
            
        # Length
        "m":   (Dimension.LENGTH, 1.0),
        "mm":  (Dimension.LENGTH, 1e-3),
        "cm":  (Dimension.LENGTH, 1e-2),
        "ft":  (Dimension.LENGTH, 0.3048),
        "in":  (Dimension.LENGTH, 0.0254),

        # Area = Length^2
        "m2": (Dimension.AREA, 1.0**2),
        "mm2":  (Dimension.AREA, 1e-3**2),
        "cm2":  (Dimension.AREA, 1e-2**2),
        "ft2":  (Dimension.AREA, 0.3048**2),
        "in2":  (Dimension.AREA, 0.0254**2),

        # Volume = Length^3
        "m3": (Dimension.VOLUME, 1.0**3),
        "mm3":  (Dimension.VOLUME, 1e-3**3),
        "cm3":  (Dimension.VOLUME, 1e-2**3),
        "ft3":  (Dimension.VOLUME, 0.3048**3),
        "in3":  (Dimension.VOLUME, 0.0254**3),

        # Length4 = Length^4
        "m4": (Dimension.LENGTH4, 1.0**4),
        "mm4":  (Dimension.LENGTH4, 1e-3**4),
        "cm4":  (Dimension.LENGTH4, 1e-2**4),
        "ft4":  (Dimension.LENGTH4, 0.3048**4),
        "in4":  (Dimension.LENGTH4, 0.0254**4),

        # Mass
        "kg": (Dimension.MASS, 1.0),
        "gr": (Dimension.MASS, 1e-3),
        "ton": (Dimension.MASS, 1e3),
        "lbs": (Dimension.MASS, 0.45359237),
        "kip": (Dimension.MASS, 0.45359237e3),
        
        # Stress = Force / Area
        "Pa":  (Dimension.STRESS, 1.0 / 1.0**2),
        "kPa": (Dimension.STRESS, 1e3 / 1.0**2),
        "MPa": (Dimension.STRESS, 1e6 / 1.0**2),
        "GPa": (Dimension.STRESS, 1e9 / 1.0**2),
        "psi": (Dimension.STRESS, 4.44822 / 0.0254**2),
        "psf": (Dimension.STRESS, 4.44822 / 0.3048**2),
        "ksi": (Dimension.STRESS, 4.44822e3 / 0.0254**2),
        "ksf": (Dimension.STRESS, 4.44822e3 / 0.3048**2),

        # Moment = Force × Length
        "N-m": (Dimension.MOMENT, 1.0 * 1.0),
        "kN-m": (Dimension.MOMENT, 1e3 * 1.0),
        "kN-mm": (Dimension.MOMENT, 1e3 * 1e-3),
        "kgf-m": (Dimension.MOMENT, 9.80665 * 1.0),
        "kgf-mm": (Dimension.MOMENT, 9.80665 * 1e-3),
        "tonf-m": (Dimension.MOMENT, 9.80665e3 * 1.0),
        "tonf-mm": (Dimension.MOMENT, 9.80665e3 * 1e-3),
        "lbf-in": (Dimension.MOMENT, 4.44822 * 0.0254),
        "lbf-ft": (Dimension.MOMENT, 4.44822 * 0.3048),
        "kipf-in": (Dimension.MOMENT, 4.44822e3 * 0.0254),
        "kipf-ft": (Dimension.MOMENT, 4.44822e3 * 0.3048),

        # Unitweight or Density = Force / Volume
        "N/m3": (Dimension.UNITWEIGHT, 1.0 / 1.0**3),
        "N/mm3": (Dimension.UNITWEIGHT, 1.0 / 1e3**3),
        "kN/m3": (Dimension.UNITWEIGHT, 1e3 / 1.0**3),
        "kN/mm3": (Dimension.UNITWEIGHT, 1e3 / 1e3**3),
        "lbf/in3": (Dimension.UNITWEIGHT, 4.44822 / 0.0254**3),
        "lbf/ft3": (Dimension.UNITWEIGHT, 4.44822 / 0.3048**3),
        "kipf/in3": (Dimension.UNITWEIGHT, 4.44822e3 / 0.0254**3),
        "kipf/ft3": (Dimension.UNITWEIGHT, 4.44822e3 / 0.3048**3),
            
        # Surface load = Force / Area
        "N/m2": (Dimension.SURFACE_LOAD, 1.0 / 1.0**2),
        "N/mm2": (Dimension.SURFACE_LOAD, 1.0 / 1e3**2),
        "kN/m2": (Dimension.SURFACE_LOAD, 1e3 / 1.0**2),
        "kN/mm2": (Dimension.SURFACE_LOAD, 1e3 / 1e3**2),
        "lbf/in2": (Dimension.SURFACE_LOAD, 4.44822 / 0.0254**2),
        "lbf/ft2": (Dimension.SURFACE_LOAD, 4.44822 / 0.3048**2),
        "kipf/in2": (Dimension.SURFACE_LOAD, 4.44822e3 / 0.0254**2),
        "kipf/ft2": (Dimension.SURFACE_LOAD, 4.44822e3 / 0.3048**2),
            
        # Distributed Line load = Force / Length
        "N/m": (Dimension.DISTRIBUTED_LINE_LOAD, 1.0 / 1.0),
        "N/mm": (Dimension.DISTRIBUTED_LINE_LOAD, 1.0 / 1e3),
        "kN/m": (Dimension.DISTRIBUTED_LINE_LOAD, 1e3 / 1.0),
        "kN/mm": (Dimension.DISTRIBUTED_LINE_LOAD, 1e3 / 1e3),
        "lbf/in": (Dimension.DISTRIBUTED_LINE_LOAD, 4.44822 / 0.0254),
        "lbf/ft": (Dimension.DISTRIBUTED_LINE_LOAD, 4.44822 / 0.3048),
        "kipf/in": (Dimension.DISTRIBUTED_LINE_LOAD, 4.44822e3 / 0.0254),
        "kipf/ft": (Dimension.DISTRIBUTED_LINE_LOAD, 4.44822e3 / 0.3048),
            
        # Concentrated Line load = Force
        "N":   (Dimension.CONCENTRATED_LINE_LOAD, 1.0),
        "kN":  (Dimension.CONCENTRATED_LINE_LOAD, 1e3),
        "MN":  (Dimension.CONCENTRATED_LINE_LOAD, 1e6),
        "kgf": (Dimension.CONCENTRATED_LINE_LOAD, 9.80665),
        "tonf": (Dimension.CONCENTRATED_LINE_LOAD, 9.80665e3),
        "lbf":  (Dimension.CONCENTRATED_LINE_LOAD, 4.44822),
        "kipf":  (Dimension.CONCENTRATED_LINE_LOAD, 4.44822e3),
            
        # Point load = Force
        "N":   (Dimension.POINT_LOAD, 1.0),
        "kN":  (Dimension.POINT_LOAD, 1e3),
        "MN":  (Dimension.POINT_LOAD, 1e6),
        "kgf": (Dimension.POINT_LOAD, 9.80665),
        "tonf": (Dimension.POINT_LOAD, 9.80665e3),
        "lbf":  (Dimension.POINT_LOAD, 4.44822),
        "kipf":  (Dimension.POINT_LOAD, 4.44822e3),
            
        # Time
        "s": (Dimension.TIME, 1.0),
        "ms": (Dimension.TIME, 1e-3),

        # Angle
        "rad": (Dimension.ANGLE, 1.0),
        "deg": (Dimension.ANGLE, pi / 180),
    }

    def get(self, unit):
        if unit not in self.UNITS:
            raise ValueError(f"Unit '{unit}' not defined")
        return self.UNITS[unit]
    
class UnitConverter:
    def __init__(self, registry):
        self.registry = registry
    
    def to_internal_units(self, value, unit):
        dimension, factor = self.registry.get(unit)
        return value * factor
    
    def from_internal_units(self, value, unit):
        dimension, factor = self.registry.get(unit)
        return value / factor

@dataclass(slots=True, frozen=True)   
class UnitSystem:
    force: str
    length: str
    mass: str
    stress: str
    time: str
    angle: str

    def area(self):
        return f'{self.length}2'
    
    def volume(self):
        return f'{self.length}3'

    def length4(self):
        return f'{self.length}4'
    
    def moment(self):
        return f'{self.force}-{self.length}'
    
    def unitweight(self):
        return f'{self.force}/{self.length}3'
    
    def surface_load(self):
        return f'{self.force}/{self.length}2'
    
    def distributed_line_load(self):
        return f'{self.force}/{self.length}'
    
    def concentrated_line_load(self):
        return f'{self.force}'
    
    def point_load(self):
        return f'{self.force}'