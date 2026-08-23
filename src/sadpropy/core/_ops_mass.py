import openseespy.opensees as ops
import numpy as np
from ..utility.tolerance import Tolerance

def _compute_and_define_masses(modeldata):
    nodal_masses = modeldata.nodal_masses # Retrieve nodal mass data
    node_tag = nodal_masses.node_tag
    nodal_mass = nodal_masses.mass
    applied_nodal_mass = []
    for tag, mass in zip(node_tag, nodal_mass):
        ops.mass(
            int(tag), # nodeTag
            *(float(mass), float(mass), Tolerance.FLOAT, Tolerance.FLOAT, Tolerance.FLOAT, Tolerance.FLOAT), # *massValues
        )
        applied_nodal_mass.append(ops.nodeMass(int(tag)))
    return np.asarray(applied_nodal_mass, dtype=np.float64)