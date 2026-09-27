from .postprocessing_class_index import (
    OpenseesLoad,
    OpenseesLoadNdata,
    OpenseesLoadType,
)

element_load_dict = {
    OpenseesLoad.Beam2dUniformLoad:
        (OpenseesLoadType.BeamUniform, OpenseesLoadNdata.Beam2dUniformLoad),
    OpenseesLoad.Beam2dPartialUniformLoad:
        (OpenseesLoadType.BeamPartialUniform, OpenseesLoadNdata.Beam2dPartialUniformLoad),
    OpenseesLoad.Beam2dPointLoad:
        (OpenseesLoadType.BeamPoint, OpenseesLoadNdata.Beam2dPointLoad),
    OpenseesLoad.Beam3dUniformLoad:
        (OpenseesLoadType.BeamUniform, OpenseesLoadNdata.Beam3dUniformLoad),
    OpenseesLoad.Beam3dPartialUniformLoad:
        (OpenseesLoadType.BeamPartialUniform, OpenseesLoadNdata.Beam3dPartialUniformLoad),
    OpenseesLoad.Beam3dPointLoad:
        (OpenseesLoadType.BeamPoint, OpenseesLoadNdata.Beam3dPointLoad),
}