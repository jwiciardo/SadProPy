import numpy as np
from .preprocessing_class_index import FrameSectionProperties, FiberSectionProperties, PropertiesClassRegistry
from sadpropy.utility._exceptions import ValidationError

# COMPUTE REINFORCEMENT AREA
def rebar_area(dia):
     A_rebar = np.pi * dia**2 / 4.0
     return A_rebar

# COMPUTE SECTION PROPERTIES
def _rectangular_concrete_section(dimensions):
    h = dimensions[:, FrameSectionProperties.h]
    b = dimensions[:, FrameSectionProperties.b]

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

def compute_section_properties(sec_shape, mat_type, dimensions):
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
          ) = section_func(dimensions=dimensions[mask])
     return (A, Avy, Avz, Iz, Iy, Jxx, alphaY, alphaZ,)

def _rectangular_concrete_fibersection(dimensions):
     h = dimensions[:, FiberSectionProperties.h]
     b = dimensions[:, FiberSectionProperties.b]
     cover = dimensions[:, FiberSectionProperties.cover]
     nBars_top = (dimensions[:, FiberSectionProperties.nBars_top].astype(np.int32))
     nBars_bot = (dimensions[:, FiberSectionProperties.nBars_bot].astype(np.int32))
     nBars_int = (dimensions[:, FiberSectionProperties.nBars_int].astype(np.int32))
     barDia_hoop = dimensions[:, FiberSectionProperties.barDia_hoop]
     barDia_top = dimensions[:, FiberSectionProperties.barDia_top]
     barDia_bot = dimensions[:, FiberSectionProperties.barDia_bot]
     barDia_int = dimensions[:, FiberSectionProperties.barDia_int]
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
     
     for idx in range(len(h)):
          # Top bar
          zTop = np.linspace(-zCore[idx], zCore[idx], nBars_top[idx])
          yTop = np.full(nBars_top[idx], yCore[idx])
          top = np.column_stack((yTop, zTop))
          barCoords_top.append(top)
          Izbar[idx] += np.sum(Ibar_top[idx] + Abar_top[idx] * top[:,1]**2)
          Iybar[idx] += np.sum(Ibar_top[idx] + Abar_top[idx] * top[:,0]**2)
          
          # Bottom bar
          zBot = np.linspace(-zCore[idx], zCore[idx], nBars_bot[idx])
          yBot = np.full(nBars_bot[idx], -yCore[idx])
          bot = np.column_stack((yBot, zBot))
          barCoords_bot.append(bot)
          Izbar[idx] += np.sum(Ibar_bot[idx] + Abar_bot[idx] * bot[:,1]**2)
          Iybar[idx] += np.sum(Ibar_bot[idx] + Abar_bot[idx] * bot[:,0]**2)

          # Intermediate bar
          ySide = np.linspace(yCore[idx], -yCore[idx], nBars_side[idx] + 2,)[1:-1]
          left = np.column_stack((ySide, np.full_like(ySide, -zCore[idx]),))
          right = np.column_stack((ySide, np.full_like(ySide, zCore[idx]),))
          intermediate = np.vstack((left, right))
          barCoords_int.append(intermediate)
          Izbar[idx] += np.sum(Ibar_int[idx] + Abar_int[idx] * intermediate[:,1]**2)
          Iybar[idx] += np.sum(Ibar_int[idx] + Abar_int[idx] * intermediate[:,0]**2)
     Iz = Izc + Izbar # Second moment of area of section about local z axis
     Iy = Iyc + Iybar # Second moment of area of section about local y axis
     return (A, Avy, Avz, Iz, Iy, Jxx, Abar_top, Abar_bot, Abar_int,)

FIBERSECTION_FUNCTIONS = {
    ("Concrete", "Rectangular"): _rectangular_concrete_fibersection,
    #("Steel", "Wide Flange"): _wideflange_steel_fibersection,
    #("Concrete", "Circular"): _circular_concrete_fibersection,
}
def compute_fibersection_properties(sec_shape, mat_type, dimensions):
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
          ) = section_func(dimensions=dimensions[mask])
     return (A, Avy, Avz, Iz, Iy, Jxx, Abar_top, Abar_bot, Abar_int,)

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
    n = len(sec_class) # Get length of array (rows)
    registry = PropertiesClassRegistry() # Define Properties Class Registry
    props_class = registry._get_sec_props_class(sec_class=sec_class) # Get Properties class index of section, look at _preproc_class.py
    max_ncol_props_class = max(map(len, props_class)) # Maximum number of array columns in all section properties
    sec_props = np.zeros((n, max_ncol_props_class), dtype=np.float64) # Allocate material properties array which has shape (n, max number of columns)
    for cls in np.unique(sec_class): # Loop over section class
            mask = sec_class == cls
            sec = secs_list[cls]
            props = sec.properties[sec_idx[mask]] # Filter section properties array using section class mask
            sec_props[mask, :props.shape[1]] = props
    row_idx = np.arange(n)[:, None] # Build array of index
    col_idx = np.array(
        [[getattr(propcls, propname) for propname in props_name]
        for propcls in props_class
    ]) # Build array of properties class
    return sec_props[row_idx, col_idx]