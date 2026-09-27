import openseespy.opensees as ops
import numpy as np
from ..preprocessing.preprocessing_dictionary import load_case_type_dict

def _assign_loads(modeldata, load_case_type, load_case_idx):
    load_cases = modeldata.load_cases # Retrieve load cases data
    nodal_loads = modeldata.nodal_loads # Retrieve nodal loads data
    concentrated_elemental_loads = modeldata.concentrated_elemental_loads # Retrieve concentrated elemental loads data
    distributed_elemental_loads = modeldata.distributed_elemental_loads # Retrieve distributed elemental loads data
    shell_to_elemental_loads = modeldata.shell_to_elemental_loads # Retrieve shell to elemental loads

    # Linear Static Load Cases
    ts_tag = int(load_case_type+1)
    print(ts_tag)
    pattern_tag = int(load_case_idx+1)
    ops.timeSeries(
        'Constant',
        ts_tag, # tsTag
        '-factor',
        float(1.0), # factor
    )
    ops.pattern(
        'Plain',
        pattern_tag, # patternTag
        ts_tag, # tsTag
    )
    nod_load_case_mask = np.isin(nodal_loads.load_case_idx, load_case_idx)
    print(nod_load_case_mask)

    