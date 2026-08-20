import numpy as np
from ..preprocessing_class_index import RectangularElasticDimensions, RectangularConcreteFiberDimensions
from ...utility.exception import ValidationError

# COMPUTE REINFORCEMENT AREA
def rebar_area(dia):
     A_rebar = np.pi * dia**2 / 4.0
     return A_rebar

# COMPUTE SECTION PROPERTIES
def _rectangular_elastic_props(dimensions):
     h = dimensions[:, RectangularElasticDimensions.h]
     b = dimensions[:, RectangularElasticDimensions.b]

     alphaY = np.full(len(h), 5.0 / 6.0) # Shear shape factor
     alphaZ = np.full(len(b), 5.0 / 6.0) # Shear shape factor

     A = h * b # Cross-sectional area
     Avy = alphaY * A # Shear area of section
     Avz = alphaZ * A # Shear area of section
     Iz = b * h**3 / 12.0 # Second moment of area of section about local z axis
     Iy = h * b**3 / 12.0 # Second moment of area of section about local y axis
     Jxx = h * b**3 * ((16.0/3.0) - 3.36 * (b / h) * (1.0 - b**4 / (12.0 * h**4))) / 16.0 # Torsional constant
     return (A, Avy, Avz, Iz, Iy, Jxx, alphaY, alphaZ, np.nan, np.nan, np.nan, np.nan)

def _rectangular_concrete_fiber_props(dimensions):
     h = dimensions[:, RectangularConcreteFiberDimensions.h]
     b = dimensions[:, RectangularConcreteFiberDimensions.b]
     cover = dimensions[:, RectangularConcreteFiberDimensions.cover]
     barDiaHoop = dimensions[:, RectangularConcreteFiberDimensions.barDiaHoop]
     barDiaTop = dimensions[:, RectangularConcreteFiberDimensions.barDiaTop]
     barDiaBot = dimensions[:, RectangularConcreteFiberDimensions.barDiaBot]
     barDiaInt = dimensions[:, RectangularConcreteFiberDimensions.barDiaInt]
     nBarsTop = (dimensions[:, RectangularConcreteFiberDimensions.nBarsTop].astype(np.int8))
     nBarsBot = (dimensions[:, RectangularConcreteFiberDimensions.nBarsBot].astype(np.int8))
     nBarsInt = (dimensions[:, RectangularConcreteFiberDimensions.nBarsInt].astype(np.int8))     
     AbarHoop, AbarTop, AbarBot, AbarInt = rebar_area(barDiaHoop), rebar_area(barDiaTop), rebar_area(barDiaBot), rebar_area(barDiaInt)
     
     # General Section Properties
     alphaY = np.full(len(h), 5.0 / 6.0) # Shear shape factor
     alphaZ = np.full(len(b), 5.0 / 6.0) # Shear shape factor
     A = h * b # Cross-sectional area
     Avy = alphaY * A # Shear area of section
     Avz = alphaZ * A # Shear area of section
     Jxx = h * b**3 * ((16.0/3.0) - 3.36 * (b / h) * (1.0 - b**4 / (12.0 * h**4))) / 16.0 # Torsional constant

     # Concrete Section
     Ac = A - (nBarsTop * AbarTop + nBarsBot * AbarBot + nBarsInt * AbarInt) # Area of concrete section
     d_prime = cover + barDiaHoop + barDiaTop / 2.0
     yCentroid, zCentroid = 0.0, 0.0 # Coordinate of section centroid in local axes
     yCover, zCover = yCentroid + h / 2.0, zCentroid + b / 2.0 # Coordinate of cover edge from centroid in local axes
     yCore, zCore = yCentroid + yCover - d_prime, zCentroid + zCover - d_prime # Coordinate of core edge from centroid in local axes
     ycCentroid, zcCentroid = (h / 2.0) - yCover, (b / 2.0) - zCover # Coordinate of concrete section centroid in local axes
     dzc = zcCentroid - zCentroid # Distance of concrete section centroid to section centriod about local z axis
     Izc = (b * h**3 / 12) + (Ac * dzc**2) # Second moment of area of concrete section about local z axis
     dyc = ycCentroid - yCentroid # Distance of concrete section centroid to section centriod about local y axis
     Iyc = (h * b**3 / 12) + (Ac * dyc**2) # Second moment of area of concrete section about local y axis

     # Rebar Section
     nBarsSide = nBarsInt // 2
     Izbar = np.zeros(len(h))
     Iybar = np.zeros(len(h))
     IbarTop = np.pi * barDiaTop**4 / 64.0 # Second moment of area of top rebar section
     IbarBot = np.pi * barDiaBot**4 / 64.0 # Second moment of area of bottom rebar section
     IbarInt = np.pi * barDiaInt**4 / 64.0 # Second moment of area of intermediate rebar section
     barCoordsTop = [] # Coordinates of top bars centroid in local axes
     barCoordsBot = [] # Coordinates of bottom bars centroid in local axes
     barCoordsInt = [] # Coordinates of intermediate bars centroid in local axes
     for idx in range(len(h)):
          # Top bar
          zTop = np.linspace(-zCore[idx], zCore[idx], nBarsTop[idx])
          yTop = np.full(nBarsTop[idx], yCore[idx])
          top = np.column_stack((yTop, zTop))
          barCoordsTop.append(top)
          Izbar[idx] += np.sum(IbarTop[idx] + AbarTop[idx] * top[:,1]**2)
          Iybar[idx] += np.sum(IbarTop[idx] + AbarTop[idx] * top[:,0]**2)
          
          # Bottom bar
          zBot = np.linspace(-zCore[idx], zCore[idx], nBarsBot[idx])
          yBot = np.full(nBarsBot[idx], -yCore[idx])
          bot = np.column_stack((yBot, zBot))
          barCoordsBot.append(bot)
          Izbar[idx] += np.sum(IbarBot[idx] + AbarBot[idx] * bot[:,1]**2)
          Iybar[idx] += np.sum(IbarBot[idx] + AbarBot[idx] * bot[:,0]**2)

          # Intermediate bar
          ySide = np.linspace(yCore[idx], -yCore[idx], nBarsSide[idx] + 2)[1:-1]
          left = np.column_stack((ySide, np.full_like(ySide, -zCore[idx])))
          right = np.column_stack((ySide, np.full_like(ySide, zCore[idx])))
          intermediate = np.vstack((left, right))
          barCoordsInt.append(intermediate)
          Izbar[idx] += np.sum(IbarInt[idx] + AbarInt[idx] * intermediate[:,1]**2)
          Iybar[idx] += np.sum(IbarInt[idx] + AbarInt[idx] * intermediate[:,0]**2)
     Iz = Izc + Izbar # Second moment of area of section about local z axis
     Iy = Iyc + Iybar # Second moment of area of section about local y axis
     return (A, Avy, Avz, Iz, Iy, Jxx, alphaY, alphaZ, AbarHoop, AbarTop, AbarBot, AbarInt)

def _compute_section_properties(section_definitions, dimensions):
     n = len(section_definitions)
     A = np.full(n, np.nan)
     Avy = np.full(n, np.nan)
     Avz = np.full(n, np.nan)
     Iz = np.full(n, np.nan)
     Iy = np.full(n, np.nan)
     Jxx = np.full(n, np.nan)
     alphaY = np.full(n, np.nan)
     alphaZ = np.full(n, np.nan)
     Abar_hoop = np.full(n, np.nan)
     Abar_top = np.full(n, np.nan)
     Abar_bot = np.full(n, np.nan)
     Abar_int = np.full(n, np.nan)
     unique_definitions = list(dict.fromkeys(section_definitions))
     for definition in unique_definitions:
          mask = np.asarray([d is definition for d in section_definitions], dtype=bool)
          result = definition.compute(dimensions=dimensions[mask])
          (
               A[mask],
               Avy[mask],
               Avz[mask],
               Iz[mask],
               Iy[mask],
               Jxx[mask],
               alphaY[mask],
               alphaZ[mask],
               Abar_hoop[mask],
               Abar_top[mask],
               Abar_bot[mask],
               Abar_int[mask],
          ) = result
     return (A, Avy, Avz, Iz, Iy, Jxx, alphaY, alphaZ, Abar_hoop, Abar_top, Abar_bot, Abar_int)

# GET SECTION DATA
def _get_section_dimensions(sections, sec_idx, dims_name):
     sec_idx = np.asarray(sec_idx, dtype=np.int32)
     sec_dims = np.full((len(sec_idx), len(dims_name)), np.nan, dtype=np.float64)
     mask = sec_idx != -1
     for i in np.flatnonzero(mask):
          definition = sections.sec_def[sec_idx[i]]
          for j, name in enumerate(dims_name):
               try:
                    column = definition.dimensions[name]
               except KeyError:
                    raise ValueError(
                         f"Dimension '{name}' is not defined for "
                         f"section '{sections.sec_name[sec_idx[i]]}'"
                    ) from None
               sec_dims[i, j] = sections.dimensions[sec_idx[i], column]
     return sec_dims

# TRACE AGGREGATED SECTION CHAIN OF SECTION AGGREGATION
def _trace_aggregated_sections(aggregated_sec_idx, aggregator_mask, sec_name):
     n = len(aggregated_sec_idx)
     invalid_aggregator = (aggregator_mask & (aggregated_sec_idx < 0))
     if np.any(invalid_aggregator):
          invalid_names = sec_name[invalid_aggregator]
          raise ValidationError(
               "The following Aggregator sections do not"
               "specify an Aggregated Section: "
               f"{invalid_names.tolist()}")

     resolved_sec_idx = np.arange(n, dtype=np.int32)
     resolved_sec_idx[aggregator_mask] = (aggregated_sec_idx[aggregator_mask])
     for _ in range(n):
          chained = aggregator_mask[resolved_sec_idx]
          if not np.any(chained):
               break
          next_idx = resolved_sec_idx.copy()
          next_idx[chained] = (aggregated_sec_idx[resolved_sec_idx[chained]])
          if np.array_equal(next_idx, resolved_sec_idx):
               break
          resolved_sec_idx = next_idx
     else:
          raise ValidationError(
               "Circular reference detected in "
               "'Aggregated Section'"
          )
     return resolved_sec_idx