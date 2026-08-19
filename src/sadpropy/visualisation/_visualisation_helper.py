def _project_coords(coords, view_info):
    if view_info["projection"] == "3d":
        return coords
    axes = view_info["axes"]
    return coords[:, axes]