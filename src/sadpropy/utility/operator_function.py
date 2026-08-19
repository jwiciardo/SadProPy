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
#def PolygonArea(coords):
        x = coords[:,0]
        y = coords[:,1]
        return 0.5 * abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1))) # Defining formula to calculate polygon area (Shoelace formula)

# COMPUTE RAYLEIGH DAMPING COEFFICIENTS
def rayleigh_damping_coefficients(damp_ratio1, damp_ratio2, omega1, omega2):
     alpha = 2 * (damp_ratio2 * omega1**2 * omega2 - damp_ratio1 * omega1 * omega2**2) / (omega1**2 - omega2**2)
     beta = 2 * (damp_ratio1 * omega1 - damp_ratio2 * omega2) / (omega1**2 - omega2**2)
     return alpha, beta

