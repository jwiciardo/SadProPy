from enum import IntEnum

# LOAD CLASS INDEX
class OpenseesLoad(IntEnum):
    NodalLoad = 1
    Beam2dUniformLoad = 3
    Beam2dPointLoad = 4
    Beam3dUniformLoad = 5
    Beam3dPointLoad = 6
    Beam2dPartialUniformLoad = 12
    Beam3dPartialUniformLoad = 121

class OpenseesLoadNdata(IntEnum):
    NodalLoad = 6
    Beam2dUniformLoad = 2
    Beam2dPointLoad = 3
    Beam3dUniformLoad = 3
    Beam3dPointLoad = 4
    Beam2dPartialUniformLoad = 6
    Beam3dPartialUniformLoad = 8

class OpenseesLoadType(IntEnum):
    BeamUniform = 1
    BeamPartialUniform = 2
    BeamPoint = 3