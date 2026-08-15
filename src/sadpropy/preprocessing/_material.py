import numpy as np
from sadpropy.preprocessing.preprocessing_class_index import PropertiesClassRegistry

# GET MATERIAL DATA
def get_material_data(mats_list, mat_class=np.ndarray):
    n = len(mat_class)
    mat_data = np.zeros(n, dtype=object)
    for cls in np.unique(mat_class):
            mask = mat_class == cls
            mat = mats_list[cls]
            mat_data[mask] = mat
    return mat_data
