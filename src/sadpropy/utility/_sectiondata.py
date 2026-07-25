import numpy as np
from sadpropy.preprocessing._class import PropertiesClassRegistry

# GET SECTION DATA
def get_section_data(secs_list, sec_class=np.ndarray):
    n = len(sec_class)
    sec_data = np.zeros(n, dtype=object)
    for cls in np.unique(sec_class):
            mask = sec_class == cls
            sec = secs_list[cls]
            sec_data[mask] = sec
    return sec_data

# GET SECTION PROPERTIES
def get_section_properties(secs_list, sec_class=np.ndarray, sec_idx=np.ndarray, props_name=list[str]):
    n = len(sec_class)
    props_class = PropertiesClassRegistry()._get_sec_props_class(sec_class=sec_class)
    max_ncol_props_class = np.max(np.array([len(propcls) for propcls in props_class])) # Maximum number of array columns in all section properties
    sec_props = np.zeros((n, max_ncol_props_class), dtype=np.float64)
    for cls in np.unique(sec_class):
            mask = sec_class == cls
            sec = secs_list[cls]
            props = sec.properties[sec_idx[mask]]
            sec_props[mask, :props.shape[1]] = props
    row_idx = np.arange(n)[:, None]
    col_idx = np.array(
        [[getattr(propcls, propname) for propname in props_name]
        for propcls in props_class
    ])
    return sec_props[row_idx, col_idx]