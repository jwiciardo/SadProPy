from ..preprocessing.preprocessing_class_index import LoadType

view_definition_dict = {
    "3D": {
        "projection": "3d",
        "elev": 35,
        "azim": -120,
    },
    "XY": {
        "projection": "2d",
        "plane": "XY",
        "axes": (0, 1),
        "perpendicular": 2,
        "xlabel": "X",
        "ylabel": "Y",
    },
    "XZ": {
        "projection": "2d",
        "plane": "XZ",
        "axes": (0, 2),
        "perpendicular": 1,
        "xlabel": "X",
        "ylabel": "Z",
    },
    "YZ": {
        "projection": "2d",
        "plane": "YZ",
        "axes": (1, 2),
        "perpendicular": 0,
        "xlabel": "Y",
        "ylabel": "Z",
    },
}
loadcase_dict = {
    # Fullname
    "Dead": LoadType.Dead,
    "Live": LoadType.Live,
    "Live Roof": LoadType.LiveRoof,
    "Seismic": LoadType.Seismic,
    "Wind": LoadType.Wind,

    # Shortname
    "D": LoadType.Dead,
    "L": LoadType.Live,
    "Lr": LoadType.LiveRoof,
    "S": LoadType.Seismic,
    "W": LoadType.Wind,
}
load_dict = {None, "all", "nodal", "elemental", "shell to elemental", "n", "e", "ste"}