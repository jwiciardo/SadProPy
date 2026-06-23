import numpy as np
from model.dataclass_structure_data import AreaConnectivity
from utility.units import UnitDatabase, UnitConverter
from utility.helper import determine_pointconnectivity_for_areaobj

class InputProcessor:
    def __init__(self, inputdata):
        self.inputdata = inputdata
        self.units = self.inputdata["System Units"].unitsystem()
        self.unitdb = UnitDatabase()
        self.unitconverter = UnitConverter(self.unitdb)

        # UNIT CONVERTER
        self.length = lambda x: self.unitconverter.to_SI(x, self.units.length)
        self.force = lambda x: self.unitconverter.to_SI(x, self.units.force)
        self.mass = lambda x: self.unitconverter.to_SI(x, self.units.mass)
        self.stress = lambda x: self.unitconverter.to_SI(x, self.units.stress)
        self.time = lambda x: self.unitconverter.to_SI(x, self.units.time)
        self.angle = lambda x: self.unitconverter.to_SI(x, self.units.angle)
        self.area = lambda x: self.unitconverter.to_SI(x, self.units.area())
        self.volume = lambda x: self.unitconverter.to_SI(x, self.units.volume())
        self.inertia = lambda x: self.unitconverter.to_SI(x, self.units.length4())
        self.moment = lambda x: self.unitconverter.to_SI(x, self.units.moment())
        self.unitweight = lambda x: self.unitconverter.to_SI(x, self.units.unitweight())
        self.shell_load = lambda x: self.unitconverter.to_SI(x, self.units.shell_load())
        self.frame_load = lambda x: self.unitconverter.to_SI(x, self.units.frame_load())
        self.concentrated_load = lambda x: self.unitconverter.to_SI(x, self.units.concentrated_load())
        self.joint_load = lambda x: self.unitconverter.to_SI(x, self.units.joint_load())
    
    # CENTRAL FUNCTION: PROCESSOR
    def process_inputdata(self):
        area_conncetivity = self.process_areaconnectivity()

        return {
            "Area Connectivity": area_conncetivity,
        }
    
    # PROCESS FUNCTION
    def process_areaconnectivity(self):
        point_objects = self.inputdata["Point Objects"]
        line_objects = self.inputdata["Line Objects"]
        area_objects = self.inputdata["Area Objects"]
        ret = {}
        for area_id, area in area_objects.items():
            id = area_id
            nodes = determine_pointconnectivity_for_areaobj(area, line_objects, point_objects)
            ret[int(id)] = AreaConnectivity(
                unique_id = int(id),
                nodes = tuple(nodes),
            ) # Defining dictionary for each area object
        return ret

