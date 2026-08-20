from ..preprocessing.preprocessing_class_index import LoadCaseType

_view_definitions = {
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
_loadcase_type = {
    # Fullname
    "Selfweight": LoadCaseType.SW,
    "Dead": LoadCaseType.D,
    "Live": LoadCaseType.L,
    "Live Roof": LoadCaseType.Lr,
    "Earthquake-X": LoadCaseType.Ex,
    "Earthquake-Y": LoadCaseType.Ey,
    "Wind-X": LoadCaseType.Wx,
    "Wind-Y": LoadCaseType.Wy,

    # Shortname
    "Sw": LoadCaseType.SW,
    "D": LoadCaseType.D,
    "L": LoadCaseType.L,
    "Lr Roof": LoadCaseType.Lr,
    "Ex": LoadCaseType.Ex,
    "Ey": LoadCaseType.Ey,
    "Wx": LoadCaseType.Wx,
    "Wy": LoadCaseType.Wy,
}
_load = {None, "all", "nodal", "elemental", "shell to elemental", "n", "e", "ste"}