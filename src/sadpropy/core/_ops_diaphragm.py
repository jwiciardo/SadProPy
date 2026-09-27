import openseespy.opensees as ops
import pandas as pd

def _assign_diaphragms(modeldata):
    diaphragms = modeldata.diaphragms # Retrieve diaphragms data
    diaph_tag = diaphragms.diaph_tag
    diaph_coords = diaphragms.coords
    diaph_dofs = diaphragms.dofs
    constrained_nodes_tag = diaphragms.constrained_nodes_tag
    perpendicular_dir = 3
    for tag, coords, dofs, constrained_nodes in zip(diaph_tag, diaph_coords, diaph_dofs, constrained_nodes_tag):
        coords = list(map(float, coords))
        dofs = list(map(int, dofs))
        constrained_nodes = list(map(int, constrained_nodes))
        ops.node(
            int(tag), # nodeTag
            *coords, # *crds = [X, Y, Z]
        )
        ops.fix(
            int(tag), # nodeTag
            *dofs # *constrValues = [UX, UY, UZ, RX, RY, RZ]
        )
        ops.rigidDiaphragm(
            perpendicular_dir, # perpDirn
            int(tag), # rNodeTag
            *constrained_nodes, # *cNodeTags
        )