import numpy as np
from dataclasses import dataclass
from .constant import GRAVITATIONAL_ACCELERATION
from .exception import ValidationError

g = GRAVITATIONAL_ACCELERATION

class UnitRegistry:
    UNITS = {
        # Axial Rigidity = Shear Rigidity = Concentrated Elemental Load = Force Nodal Load = Force
        "N":    1.0,
        "kN":   1e3,
        "MN":   1e6,
        "kgf":  1.0 * g,
        "tonf": 1e3 * g,
        "lbf":  4.44822,
        "kipf": 4.44822e3,
            
        # Length
        "m":  1.0,
        "mm": 1e-3,
        "cm": 1e-2,
        "ft": 0.3048,
        "in": 0.0254,

        # Area = Length^2
        "m2":  1.0**2,
        "mm2": 1e-3**2,
        "cm2": 1e-2**2,
        "ft2": 0.3048**2,
        "in2": 0.0254**2,

        # Volume = Length^3
        "m3":  1.0**3,
        "mm3": 1e-3**3,
        "cm3": 1e-2**3,
        "ft3": 0.3048**3,
        "in3": 0.0254**3,

        # Second Moment of Area = Length^4
        "m4":  1.0**4,
        "mm4": 1e-3**4,
        "cm4": 1e-2**4,
        "ft4": 0.3048**4,
        "in4": 0.0254**4,

        # Mass
        "kg":  1.0,
        "gr":  1e-3,
        "ton": 1e3,
        "lbs": 0.45359237,
        "kip": 0.45359237e3,
        
        # Velocity = Length / Time
        "m/s":  1.0 / 1.0,
        "mm/s": 1e-3 / 1.0,
        "cm/s": 1e-2 / 1.0,
        "ft/s": 0.3048 / 1.0,
        "in/s": 0.0254 / 1.0,

        # Acceleration = Length / Time^2
        "m/s2":  1.0 / 1.0**2,
        "mm/s2": 1e-3 / 1.0**2,
        "cm/s2": 1e-2 / 1.0**2,
        "ft/s2": 0.3048 / 1.0**2,
        "in/s2": 0.0254 / 1.0**2,

        # Stress = Force / Area
        "Pa":  1.0 / 1.0**2,
        "kPa": 1e3 / 1.0**2,
        "MPa": 1e6 / 1.0**2,
        "GPa": 1e9 / 1.0**2,
        "psi": 4.44822 / 0.0254**2,
        "psf": 4.44822 / 0.3048**2,
        "ksi": 4.44822e3 / 0.0254**2,
        "ksf": 4.44822e3 / 0.3048**2,

        # Moment = Moment Nodal Load = Force × Length
        "N-m":     1.0 * 1.0,
        "kN-m":    1e3 * 1.0,
        "kN-mm":   1e3 * 1e-3,
        "kgf-m":   1.0 * g * 1.0,
        "kgf-mm":  1.0 * g * 1e-3,
        "tonf-m":  1e3 * g * 1.0,
        "tonf-mm": 1e3 * g * 1e-3,
        "lbf-in":  4.44822 * 0.0254,
        "lbf-ft":  4.44822 * 0.3048,
        "kipf-in": 4.44822e3 * 0.0254,
        "kipf-ft": 4.44822e3 * 0.3048,

        # Flexuaral Rigidity = Torsional Rigidity = Force × Length^2
        "N-m2":     1.0 * 1.0**2,
        "kN-m2":    1e3 * 1.0**2,
        "kN-mm2":   1e3 * 1e-3**2,
        "kgf-m2":   1.0 * g * 1.0**2,
        "kgf-mm2":  1.0 * g * 1e-3**2,
        "tonf-m2":  1e3 * g * 1.0**2,
        "tonf-mm2": 1e3 * g * 1e-3**2,
        "lbf-in2":  4.44822 * 0.0254**2,
        "lbf-ft2":  4.44822 * 0.3048**2,
        "kipf-in2": 4.44822e3 * 0.0254**2,
        "kipf-ft2": 4.44822e3 * 0.3048**2,

        # Unitweight or Density = Force / Volume
        "N/m3":     1.0 / 1.0**3,
        "N/mm3":    1.0 / 1e3**3,
        "kN/m3":    1e3 / 1.0**3,
        "kN/mm3":   1e3 / 1e3**3,
        "lbf/in3":  4.44822 / 0.0254**3,
        "lbf/ft3":  4.44822 / 0.3048**3,
        "kipf/in3": 4.44822e3 / 0.0254**3,
        "kipf/ft3": 4.44822e3 / 0.3048**3,
            
        # Shell load = Force / Area
        "N/m2":     1.0 / 1.0**2,
        "N/mm2":    1.0 / 1e3**2,
        "kN/m2":    1e3 / 1.0**2,
        "kN/mm2":   1e3 / 1e3**2,
        "lbf/in2":  4.44822 / 0.0254**2,
        "lbf/ft2":  4.44822 / 0.3048**2,
        "kipf/in2": 4.44822e3 / 0.0254**2,
        "kipf/ft2": 4.44822e3 / 0.3048**2,
            
        # Distributed Elemental load = Translational Stiffness = Force / Length
        "N/m":     1.0 / 1.0,
        "N/mm":    1.0 / 1e3,
        "kN/m":    1e3 / 1.0,
        "kN/mm":   1e3 / 1e3,
        "lbf/in":  4.44822 / 0.0254,
        "lbf/ft":  4.44822 / 0.3048,
        "kipf/in": 4.44822e3 / 0.0254,
        "kipf/ft": 4.44822e3 / 0.3048,

        # Rotational Stiffness = Force × Length / Angle
        "N-m/rad":     1.0 * 1.0 / 1.0,
        "kN-m/rad":    1e3 * 1.0 / 1.0,
        "kN-mm/rad":   1e3 * 1e-3 / 1.0,
        "kgf-m/rad":   1.0 * g * 1.0 / 1.0,
        "kgf-mm/rad":  1.0 * g * 1e-3 / 1.0,
        "tonf-m/rad":  1e3 * g * 1.0 / 1.0,
        "tonf-mm/rad": 1e3 * g * 1e-3 / 1.0,
        "lbf-in/rad":  4.44822 * 0.0254 / 1.0,
        "lbf-ft/rad":  4.44822 * 0.3048 / 1.0,
        "kipf-in/rad": 4.44822e3 * 0.0254 / 1.0,
        "kipf-ft/rad": 4.44822e3 * 0.3048 / 1.0,
        "N-m/deg":     1.0 * 1.0 / (np.pi / 180),
        "kN-m/deg":    1e3 * 1.0 / (np.pi / 180),
        "kN-mm/deg":   1e3 * 1e-3 / (np.pi / 180),
        "kgf-m/deg":   1.0 * g * 1.0 / (np.pi / 180),
        "kgf-mm/deg":  1.0 * g * 1e-3 / (np.pi / 180),
        "tonf-m/deg":  1e3 * g * 1.0 / (np.pi / 180),
        "tonf-mm/deg": 1e3 * g * 1e-3 / (np.pi / 180),
        "lbf-in/deg":  4.44822 * 0.0254 / (np.pi / 180),
        "lbf-ft/deg":  4.44822 * 0.3048 / (np.pi / 180),
        "kipf-in/deg": 4.44822e3 * 0.0254 / (np.pi / 180),
        "kipf-ft/deg": 4.44822e3 * 0.3048 / (np.pi / 180),

        # Time
        "s":  1.0,
        "ms": 1e-3,

        # Angle
        "rad": 1.0,
        "deg": np.pi / 180,
    }

    def get(self, unit):
        if unit not in self.UNITS:
            raise ValidationError(f"Unit '{unit}' not found in the Unit Registry")
        return self.UNITS[unit]
    
class ConverterToInternalUnits:
    def __init__(self, units):
        self._registry = UnitRegistry()
        self._units = units

    def _convert_to_internalunits(self, values, unit):
        factor = self._registry.get(unit)
        return np.asarray(values, dtype=np.float64) * factor
    
    def length(self, values):
        return self._convert_to_internalunits(values=values, unit=self._units.length)
    
    def force(self, values):
        return self._convert_to_internalunits(values=values, unit=self._units.force)
    
    def mass(self, values):
        return self._convert_to_internalunits(values=values, unit=self._units.mass)
    
    def velocity(self, values):
        return self._convert_to_internalunits(values=values, unit=self._units.velocity())
    
    def acceleration(self, values):
        return self._convert_to_internalunits(values=values, unit=self._units.acceleration())
    
    def stress(self, values):
        return self._convert_to_internalunits(values=values, unit=self._units.stress)
    
    def time(self, values):
        return self._convert_to_internalunits(values=values, unit=self._units.time)
    
    def angle(self, values):
        return self._convert_to_internalunits(values=values, unit=self._units.angle)
    
    def area(self, values):
        return self._convert_to_internalunits(values=values, unit=self._units.area())
    
    def volume(self, values):
        return self._convert_to_internalunits(values=values, unit=self._units.volume())
    
    def second_moment_of_area(self, values):
        return self._convert_to_internalunits(values=values, unit=self._units.second_moment_of_area())
    
    def moment(self, values):
        return self._convert_to_internalunits(values=values, unit=self._units.moment())
    
    def unitweight(self, values):
        return self._convert_to_internalunits(values=values, unit=self._units.unitweight())
    
    def shell_load(self, values):
        return self._convert_to_internalunits(values=values, unit=self._units.shell_load())
    
    def distributed_elemental_load(self, values):
        return self._convert_to_internalunits(values=values, unit=self._units.distributed_elemental_load())
    
    def concentrated_elemental_load(self, values):
        return self._convert_to_internalunits(values=values, unit=self._units.concentrated_elemental_load())
    
    def force_nodal_load(self, values):
        return self._convert_to_internalunits(values=values, unit=self._units.force_nodal_load())
    
    def moment_nodal_load(self, values):
        return self._convert_to_internalunits(values=values, unit=self._units.moment_nodal_load())
    
    def translational_stiffness(self, values):
        return self._convert_to_internalunits(values=values, unit=self._units.translational_stiffness())
    
    def rotational_stiffness(self, values):
        return self._convert_to_internalunits(values=values, unit=self._units.rotational_stiffness())
    
    def axial_rigidity(self, values):
        return self._convert_to_internalunits(values=values, unit=self._units.axial_rigidity())
    
    def flexural_rigidity(self, values):
        return self._convert_to_internalunits(values=values, unit=self._units.flexural_rigidity())
    
    def shear_rigidity(self, values):
        return self._convert_to_internalunits(values=values, unit=self._units.shear_rigidity())

    def torsional_rigidity(self, values):
        return self._convert_to_internalunits(values=values, unit=self._units.torsional_rigidity())

class ConverterFromInternalUnits:
    def __init__(self, units):
        self._registry = UnitRegistry()
        self._units = units

    def _convert_from_internalunits(self, values, unit):
        factor = self._registry.get(unit)
        return np.asarray(values, dtype=np.float64) / factor
    
    def length(self, values):
        return self._convert_from_internalunits(values=values, unit=self._units.length)
    
    def force(self, values):
        return self._convert_from_internalunits(values=values, unit=self._units.force)
    
    def mass(self, values):
        return self._convert_from_internalunits(values=values, unit=self._units.mass)
    
    def velocity(self, values):
        return self._convert_from_internalunits(values=values, unit=self._units.velocity())
    
    def acceleration(self, values):
        return self._convert_from_internalunits(values=values, unit=self._units.acceleration())
    
    def stress(self, values):
        return self._convert_from_internalunits(values=values, unit=self._units.stress)
    
    def time(self, values):
        return self._convert_from_internalunits(values=values, unit=self._units.time)
    
    def angle(self, values):
        return self._convert_from_internalunits(values=values, unit=self._units.angle)
    
    def area(self, values):
        return self._convert_from_internalunits(values=values, unit=self._units.area())
    
    def volume(self, values):
        return self._convert_from_internalunits(values=values, unit=self._units.volume())
    
    def second_moment_of_area(self, values):
        return self._convert_from_internalunits(values=values, unit=self._units.second_moment_of_area())
    
    def moment(self, values):
        return self._convert_from_internalunits(values=values, unit=self._units.moment())
    
    def unitweight(self, values):
        return self._convert_from_internalunits(values=values, unit=self._units.unitweight())
    
    def shell_load(self, values):
        return self._convert_from_internalunits(values=values, unit=self._units.shell_load())
    
    def distributed_elemental_load(self, values):
        return self._convert_from_internalunits(values=values, unit=self._units.distributed_elemental_load())
    
    def concentrated_elemental_load(self, values):
        return self._convert_from_internalunits(values=values, unit=self._units.concentrated_elemental_load())
    
    def force_nodal_load(self, values):
        return self._convert_from_internalunits(values=values, unit=self._units.force_nodal_load())
    
    def moment_nodal_load(self, values):
        return self._convert_from_internalunits(values=values, unit=self._units.moment_nodal_load())
    
    def translational_stiffness(self, values):
        return self._convert_from_internalunits(values=values, unit=self._units.translational_stiffness())
    
    def rotational_stiffness(self, values):
        return self._convert_from_internalunits(values=values, unit=self._units.rotational_stiffness())
    
    def axial_rigidity(self, values):
        return self._convert_from_internalunits(values=values, unit=self._units.axial_rigidity())
    
    def flexural_rigidity(self, values):
        return self._convert_from_internalunits(values=values, unit=self._units.flexural_rigidity())
    
    def shear_rigidity(self, values):
        return self._convert_from_internalunits(values=values, unit=self._units.shear_rigidity())

    def torsional_rigidity(self, values):
        return self._convert_from_internalunits(values=values, unit=self._units.torsional_rigidity())
    
@dataclass(slots=True, frozen=True)   
class UserDefinedUnits:
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

    def second_moment_of_area(self):
        return f'{self.length}4'
    
    def velocity(self):
        return f'{self.length}/{self.time}'
        
    def acceleration(self):
        return f'{self.length}/{self.time}2'

    def moment(self):
        return f'{self.force}-{self.length}'
    
    def unitweight(self):
        return f'{self.force}/{self.length}3'
    
    def shell_load(self):
        return f'{self.force}/{self.length}2'
    
    def distributed_elemental_load(self):
        return f'{self.force}/{self.length}'
    
    def concentrated_elemental_load(self):
        return f'{self.force}'
    
    def force_nodal_load(self):
        return f'{self.force}'
    
    def moment_nodal_load(self):
        return f'{self.force}-{self.length}'
    
    def translational_stiffness(self):
        return f'{self.force}/{self.length}'
    
    def rotational_stiffness(self):
        return f'{self.force}-{self.length}/{self.angle}'

    def axial_rigidity(self):
        return f'{self.force}'
    
    def flexural_rigidity(self):
        return f'{self.force}-{self.length}2'

    def shear_rigidity(self):
        return f'{self.force}'

    def torsional_rigidity(self):
        return f'{self.force}-{self.length}2'