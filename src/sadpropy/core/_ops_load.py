import openseespy.opensees as ops
import numpy as np

def _assign_loads(modeldata):
    nodal_loads = modeldata.nodal_loads # Retrieve nodal loads data
    concentrated_elemental_loads = modeldata.concentrated_elemental_loads # Retrieve concentrated elemental loads data
    distributed_elemental_loads = modeldata.distributed_elemental_loads # Retrieve distributed elemental loads data
    shell_to_elemental_loads = modeldata.shell_to_elemental_loads # Retrieve shell to elemental loads data
    print(nodal_loads)