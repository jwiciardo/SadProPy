import numpy as np
from .exception import ValidationError
from .tolerance import Tolerance

__all__ = ["significant_figures", "rayleigh_damping_coefficients"]

# NUMERICAL CORRECTION
def significant_figures(x, tol=Tolerance.FLOAT):
    try:
        return [0.0 if abs(float(v)) < tol else float(v) for v in x]
    except TypeError:
        x = float(x)
        return 0.0 if abs(x) < tol else x

# COMPUTE POLYGON AREA
def PolygonArea(vertices_coords): # Defining formula to calculate polygon area (Shoelace formula)
    if vertices_coords.ndim == 3:
        x = vertices_coords[:, :, 0]
        y = vertices_coords[:, :, 1]
        x_next = np.roll(x, -1, axis=1)
        y_next = np.roll(y, -1, axis=1)
        cross = x * y_next - x_next * y
        return 0.5 * np.abs(np.sum(cross, axis=1))
    elif vertices_coords.ndim == 2:
        x = vertices_coords[:, 0]
        y = vertices_coords[:, 1]
        x_next = np.roll(x, -1)
        y_next = np.roll(y, -1)
        cross = x * y_next - x_next * y
        return 0.5 * np.abs(np.sum(cross))
    else:
        raise ValidationError("Vertices coordinates must have 2 or 3 dimensions")

# COMPUTE POLYGON CNETROID
def PolygonCentroid(vertices_coords):
    if vertices_coords.ndim == 3:
        x = vertices_coords[:, :, 0]
        y = vertices_coords[:, :, 1]
        x_next = np.roll(x, -1, axis=1)
        y_next = np.roll(y, -1, axis=1)
        cross = x * y_next - x_next * y
        area = 0.5 * np.abs(np.sum(cross, axis=1))
        cx = np.sum((x + x_next) * cross, axis=1) / (6.0 * area)
        cy = np.sum((y + y_next) * cross, axis=1) / (6.0 * area)
        return np.column_stack([cx, cy])
    elif vertices_coords.ndim == 2:
        x = vertices_coords[:, 0]
        y = vertices_coords[:, 1]
        x_next = np.roll(x, -1)
        y_next = np.roll(y, -1)
        cross = x * y_next - x_next * y
        area = 0.5 * np.sum(cross)
        cx = np.sum((x + x_next) * cross) / (6.0 * area)
        cy = np.sum((y + y_next) * cross) / (6.0 * area)
        return np.array([cx, cy])
    else:
        raise ValidationError("Vertices coordinates must have 2 or 3 dimensions")


# COMPUTE RAYLEIGH DAMPING COEFFICIENTS
def rayleigh_damping_coefficients(damp_ratio1, damp_ratio2, omega1, omega2):
     alpha = 2 * (damp_ratio2 * omega1**2 * omega2 - damp_ratio1 * omega1 * omega2**2) / (omega1**2 - omega2**2)
     beta = 2 * (damp_ratio1 * omega1 - damp_ratio2 * omega2) / (omega1**2 - omega2**2)
     return alpha, beta

