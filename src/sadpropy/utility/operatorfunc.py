import numpy as np
from sadpropy.preprocessing._propertiesclass import FrameSectionProperties, FiberSectionProperties
from ._exceptions import ValidationError

__all__ = ["significant_figures", "rayleigh_damping_coefficients", "rebar_area", "section_properties", "fibersection_properties"]

# NUMERICAL CORRECTION
def significant_figures(x, tol=1e-12):
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

# COMPUTE REINFORCEMENT AREA
def rebar_area(dia):
     A_rebar = np.pi * dia**2 / 4.0
     return A_rebar

# COMPUTE SECTION PROPERTIES
def _rectangular_concrete_section(properties):
    h = properties[:, FrameSectionProperties.h]
    b = properties[:, FrameSectionProperties.b]

    alphaY = np.full(len(h), 5.0 / 6.0) # Shear shape factor
    alphaZ = np.full(len(b), 5.0 / 6.0) # Shear shape factor

    A = h * b # Cross-sectional area
    Avy = alphaY * A # Shear area of section
    Avz = alphaZ * A # Shear area of section
    Iz = b * h**3 / 12.0 # Second moment of area of section about local z axis
    Iy = h * b**3 / 12.0 # Second moment of area of section about local y axis
    Jxx = h * b**3 * ((16.0/3.0) - 3.36 * (b / h) * (1.0 - b**4 / (12.0 * h**4))) / 16.0 # Torsional constant
    return (A, Avy, Avz, Iz, Iy, Jxx, alphaY, alphaZ,)

SECTION_FUNCTIONS = {
    ("Concrete", "Rectangular"): _rectangular_concrete_section,
    #("Steel", "Wide Flange"): _wideflange_steel_section,
    #("Concrete", "Circular"): _circular_concrete_section,
}

def section_properties(sec_shape, mat_type, properties):
     n = len(sec_shape)
     A = np.zeros(n)
     Avy = np.zeros(n)
     Avz = np.zeros(n)
     Iz = np.zeros(n)
     Iy = np.zeros(n)
     Jxx = np.zeros(n)
     alphaY = np.zeros(n)
     alphaZ = np.zeros(n)
     for mattype, shape in np.unique(np.column_stack((mat_type, sec_shape)), axis=0,):
          mask = ((mat_type == mattype) & (sec_shape == shape))
          try:
               section_func = SECTION_FUNCTIONS[(mattype, shape)]
          except KeyError:
               raise ValidationError(
                    f"Unsupported section "
                    f"'{mattype} {shape}'"
               )
          (
               A[mask],
               Avy[mask],
               Avz[mask],
               Iz[mask],
               Iy[mask],
               Jxx[mask],
               alphaY[mask],
               alphaZ[mask],
          ) = section_func(properties=properties[mask])
     return (A, Avy, Avz, Iz, Iy, Jxx, alphaY, alphaZ,)

def _rectangular_concrete_fibersection(properties):
     h = properties[:, FiberSectionProperties.h]
     b = properties[:, FiberSectionProperties.b]
     cover = properties[:, FiberSectionProperties.cover]
     nBars_top = (properties[:, FiberSectionProperties.nBars_top].astype(np.int32))
     nBars_bot = (properties[:, FiberSectionProperties.nBars_bot].astype(np.int32))
     nBars_int = (properties[:, FiberSectionProperties.nBars_int].astype(np.int32))
     barDia_hoop = properties[:, FiberSectionProperties.barDia_hoop]
     barDia_top = properties[:, FiberSectionProperties.barDia_top]
     barDia_bot = properties[:, FiberSectionProperties.barDia_bot]
     barDia_int = properties[:, FiberSectionProperties.barDia_int]
     Abar_hoop, Abar_top, Abar_bot, Abar_int = rebar_area(barDia_hoop), rebar_area(barDia_top), rebar_area(barDia_bot), rebar_area(barDia_int)
     
     # General Section Properties
     alphaY = np.full(len(h), 5.0 / 6.0) # Shear shape factor
     alphaZ = np.full(len(b), 5.0 / 6.0) # Shear shape factor
     A = h * b # Cross-sectional area
     Avy = alphaY * A # Shear area of section
     Avz = alphaZ * A # Shear area of section
     Jxx = h * b**3 * ((16.0/3.0) - 3.36 * (b / h) * (1.0 - b**4 / (12.0 * h**4))) / 16.0 # Torsional constant

     # Concrete Section
     Ac = A - (nBars_top * Abar_top + nBars_bot * Abar_bot + nBars_int * Abar_int) # Area of concrete section
     d_prime = cover + barDia_hoop + barDia_top / 2.0
     yCentroid, zCentroid = 0.0, 0.0 # Local axis coordinate of section centroid
     yCover, zCover = yCentroid + h / 2.0, yCentroid + b / 2.0 # Local axis coordinate of cover edge from centroid
     yCore, zCore = yCentroid + yCover - d_prime, zCentroid + zCover - d_prime # Local axis coordinate of core edge from centroid
     ycCentroid, zcCentroid = (h / 2.0) - yCover, (b / 2.0) - zCover # Local axis coordinate of concrete section centroid
     dzc = zcCentroid - zCentroid # distance of concrete section centroid to section centriod about local z axis
     Izc = (b * h**3 / 12) + (Ac * dzc**2) # Second moment of area of concrete section about local z axis
     dyc = ycCentroid - yCentroid # distance of concrete section centroid to section centriod about local y axis
     Iyc = (h * b**3 / 12) + (Ac * dyc**2) # Second moment of area of concrete section about local y axis

     # Rebar Section
     nBars_side = nBars_int // 2
     Izbar = np.zeros(len(h))
     Iybar = np.zeros(len(h))
     Ibar_top = np.pi * barDia_top**4 / 64.0 # Second moment of area of top rebar section
     Ibar_bot = np.pi * barDia_bot**4 / 64.0 # Second moment of area of bottom rebar section
     Ibar_int = np.pi * barDia_int**4 / 64.0 # Second moment of area of intermediate rebar section
     barCoords_top = [] # Local axis coordinate of top bars centroid
     barCoords_bot = [] # Local axis coordinate of bottom bars centroid
     barCoords_int = [] # Local axis coordinate of intermediate bars centroid
     
     for i in range(len(h)):
          # Top bar
          zTop = np.linspace(-zCore[i], zCore[i], nBars_top[i])
          yTop = np.full(nBars_top[i], yCore[i])
          top = np.column_stack((yTop, zTop))
          barCoords_top.append(top)
          Izbar[i] += np.sum(Ibar_top[i] + Abar_top[i] * top[:,1]**2)
          Iybar[i] += np.sum(Ibar_top[i] + Abar_top[i] * top[:,0]**2)
          
          # Bottom bar
          zBot = np.linspace(-zCore[i], zCore[i], nBars_bot[i])
          yBot = np.full(nBars_bot[i], -yCore[i])
          bot = np.column_stack((yBot, zBot))
          barCoords_bot.append(bot)
          Izbar[i] += np.sum(Ibar_bot[i] + Abar_bot[i] * bot[:,1]**2)
          Iybar[i] += np.sum(Ibar_bot[i] + Abar_bot[i] * bot[:,0]**2)

          # Intermediate bar
          ySide = np.linspace(yCore[i], -yCore[i], nBars_side[i] + 2,)[1:-1]
          left = np.column_stack((ySide, np.full_like(ySide, -zCore[i]),))
          right = np.column_stack((ySide, np.full_like(ySide, zCore[i]),))
          intermediate = np.vstack((left, right))
          barCoords_int.append(intermediate)
          Izbar[i] += np.sum(Ibar_int[i] + Abar_int[i] * intermediate[:,1]**2)
          Iybar[i] += np.sum(Ibar_int[i] + Abar_int[i] * intermediate[:,0]**2)
     Iz = Izc + Izbar # Second moment of area of section about local z axis
     Iy = Iyc + Iybar # Second moment of area of section about local y axis
     return (A, Avy, Avz, Iz, Iy, Jxx, Abar_top, Abar_bot, Abar_int,)

FIBERSECTION_FUNCTIONS = {
    ("Concrete", "Rectangular"): _rectangular_concrete_fibersection,
    #("Steel", "Wide Flange"): _wideflange_steel_fibersection,
    #("Concrete", "Circular"): _circular_concrete_fibersection,
}

def fibersection_properties(sec_shape, mat_type, properties):
     n = len(sec_shape)
     A = np.zeros(n)
     Avy = np.zeros(n)
     Avz = np.zeros(n)
     Iz = np.zeros(n)
     Iy = np.zeros(n)
     Jxx = np.zeros(n)
     Abar_top = np.zeros(n)
     Abar_bot = np.zeros(n)
     Abar_int = np.zeros(n)
     for mattype, shape in np.unique(np.column_stack((mat_type, sec_shape)), axis=0,):
          mask = ((mat_type == mattype) & (sec_shape == shape))
          try:
               section_func = FIBERSECTION_FUNCTIONS[(mattype, shape)]
          except KeyError:
               raise ValidationError(
                    f"Unsupported section "
                    f"'{mattype} {shape}'"
               )
          (
               A[mask],
               Avy[mask],
               Avz[mask],
               Iz[mask],
               Iy[mask],
               Jxx[mask],
               Abar_top[mask],
               Abar_bot[mask],
               Abar_int[mask],
          ) = section_func(properties=properties[mask])
     return (A, Avy, Avz, Iz, Iy, Jxx, Abar_top, Abar_bot, Abar_int,)