import numpy as np

# GET MATERIAL DATA
def get_material_properties(materials, mat_idx, props_name):
    mat_idx = np.asarray(mat_idx, dtype=np.int32)
    result = np.full((len(mat_idx), len(props_name)), np.nan, dtype=np.float64)
    mask = mat_idx != -1
    for i in np.flatnonzero(mask):
        definition = materials.mat_def[mat_idx[i]]
        for j, name in enumerate(props_name):
            try:
                column = definition.properties[name]
            except KeyError:
                raise ValueError(
                    f"Property '{name}' is not defined for "
                    f"material '{materials.mat_name[mat_idx[i]]}'"
                ) from None
            result[i, j] = materials.properties[mat_idx[i], column]
    return result