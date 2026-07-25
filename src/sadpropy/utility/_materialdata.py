import numpy as np
from sadpropy.preprocessing._class import PropertiesClassRegistry

# GET SECTION DATA
def get_material_data(mats_list, mat_class=np.ndarray):
    n = len(mat_class)
    mat_data = np.zeros(n, dtype=object)
    for cls in np.unique(mat_class):
            mask = mat_class == cls
            mat = mats_list[cls]
            mat_data[mask] = mat
    return mat_data

# GET MATERIAL PROPERTIES
def get_material_properties(mats_list, mat_class=np.ndarray, mat_idx=np.ndarray, props_name=list[str]):
    n = len(mat_class) # Get length of array (rows)
    props_class = PropertiesClassRegistry()._get_mat_props_class(mat_class=mat_class) # Get Properties class index of material, look at _propertiesclass.py
    max_ncol_props_class = np.max(np.array([len(propcls) for propcls in props_class])) # Determine maximum number of columns among all material properties arrays
    mat_props = np.zeros((n, max_ncol_props_class), dtype=np.float64) # Allocate material properties array which has shape (n, max number of columns)
    for cls in np.unique(mat_class): # Filter material properties array using material class mask
            mask = mat_class == cls
            mat = mats_list[cls]
            props = mat.properties[mat_idx[mask]]
            mat_props[mask, :props.shape[1]] = props
    row_idx = np.arange(n)[:, None] # Build array of index
    col_idx = np.array(
        [[getattr(propcls, propname) for propname in props_name]
        for propcls in props_class
    ]) # Build array of properties class
    return mat_props[row_idx, col_idx]
