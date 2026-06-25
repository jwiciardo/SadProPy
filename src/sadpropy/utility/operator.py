from math import pi, sqrt

__all__ = ["SignificantFigures", "CoordinateToLength", "RayleighDampingCoefficients", "RebarArea", "SectionProperties", "FiberSectionProperties"]

# NUMERICAL CORRECTION
def SignificantFigures(x, tol=1e-12):
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

# COMPUTE LENGTH FROM COORDINATE DATA
def CoordinateToLength(i_coord, j_coord):
     i_x_coord, i_y_coord, i_z_coord = i_coord
     j_x_coord, j_y_coord, j_z_coord = j_coord
     length = sqrt((i_x_coord - j_x_coord)**2 + (i_y_coord - j_y_coord)**2 + (i_z_coord - j_z_coord)**2)
     return length

# COMPUTE RAYLEIGH DAMPING COEFFICIENTS
def RayleighDampingCoefficients(damp_ratio1, damp_ratio2, omega1, omega2):
     alpha = 2 * (damp_ratio2 * omega1**2 * omega2 - damp_ratio1 * omega1 * omega2**2) / (omega1**2 - omega2**2)
     beta = 2 * (damp_ratio1 * omega1 - damp_ratio2 * omega2) / (omega1**2 - omega2**2)
     return alpha, beta

# COMPUTE REINFORCEMENT AREA
def RebarArea(dia):
     A_rebar = pi * dia**2 /4
     return A_rebar

# COMPUTE SECTION PROPERTIES
def SectionProperties(section_data):
     row = section_data
     if row['Section Shape'] == 'Rectangular':
          h, b = row['h'], row['b'] # Section data

          # Section properties
          alphaY = alphaZ = 5/6 # Shear shape factor
          A = h * b # Area of section
          Avy = Avz = alphaY * A # Shear area of section
          Iz = b * h**3 / 12 # Second moment of area of section about local z axis
          Iy = h * b**3 / 12 # Second moment of area of section about local y axis
          Jxx = h * b**3 * ((16/3) - 3.36 * (b / h) * (1 - b**4 / (12 * h**4))) / 16 # Torsional constant
     return A, Avy, Avz, Iz, Iy, Jxx, alphaY, alphaZ

def FiberSectionProperties(fibersection_data, ):
     row = fibersection_data
     if row['Material Type'] == 'Concrete':
          if row['Section Shape'] == 'Rectangular':
               # Section data
               h, b = row['h'], row['b']
               cover, nBars_top, nBars_bot, nBars_int = row['cover'], row['nBarsTop'], row['nBarsBot'], row['nBarsInt']
               barDia_hoop, barDia_top, barDia_bot, barDia_int = row['barDiaHoop'], row['barDiaTop'], row['barDiaBot'], row['barDiaInt']
               Abar_hoop, Abar_top, Abar_bot, Abar_int = RebarArea(barDia_hoop), RebarArea(barDia_top), RebarArea(barDia_bot), RebarArea(barDia_int)
               d_prime = cover + barDia_hoop + barDia_top / 2.0
               yCentroid, zCentroid = 0.0, 0.0 # Local axis coordinate of section centroid
               yCover, zCover = yCentroid + h / 2.0, yCentroid + b / 2.0 # Local axis coordinate of cover edge from centroid
               yCore, zCore = yCentroid + yCover - d_prime, zCentroid + zCover - d_prime # Local axis coordinate of core edge from centroid
               nBars_side = int(nBars_int / 2)
               barCoords_top = [] # Local axis coordinate of top bars centroid
               barCoords_int = [] # Local axis coordinate of intermediate bars centroid
               barCoords_bot = [] # Local axis coordinate of bottom bars centroid
               for n in range(nBars_top): # Top bars
                    yStart, zStart = yCore, -zCore
                    yEnd, zEnd = yCore, zCore
                    ySpace, zSpace = (yEnd - yStart) / (nBars_top - 1), (zEnd - zStart) / (nBars_top - 1)
                    y, z = yStart + n * ySpace, zStart + n * zSpace
                    barCoords_top.append((y, z))
               for n in range(nBars_side): # Intermediate bars
                    # Left side
                    yStartLeft, zStartLeft = yCore, -zCore
                    yEndLeft, zEndLeft = -yCore, -zCore
                    ySpaceLeft, zSpaceLeft = (yEndLeft - yStartLeft) / (nBars_side + 1), (zEndLeft - zStartLeft) / (nBars_side + 1)
                    yLeft, zLeft = yStartLeft + ySpaceLeft + n * ySpaceLeft, zStartLeft + zSpaceLeft + n * zSpaceLeft
                    barCoords_int.append((yLeft, zLeft))
                         
                    # Right side
                    yStartRight, zStartRight = yCore, zCore
                    yEndRight, zEndRight = -yCore, zCore
                    ySpaceRight, zSpaceRight = (yEndRight - yStartRight) / (nBars_side + 1), (zEndRight - zStartRight) / (nBars_side + 1)
                    yRight, zRight = yStartRight + ySpaceRight + n * ySpaceRight, zStartRight + zSpaceRight + n * zSpaceRight
                    barCoords_int.append((yRight, zRight))
               for n in range(nBars_bot): # Bottom bars
                    yStart, zStart = -yCore, -zCore
                    yEnd, zEnd = -yCore, zCore
                    ySpace, zSpace = (yEnd - yStart) / (nBars_bot - 1), (zEnd - zStart) / (nBars_bot - 1)
                    y, z = yStart + n * ySpace, zStart + n * zSpace
                    barCoords_bot.append((y, z))
                    
               # Section properties
               alphaY = alphaZ = 5/6 # Shear shape factor
               A = h * b # Total area of section
               Avy = Avz = alphaY * A # Shear area of section
               Ac = A - (nBars_top * Abar_top + nBars_bot * Abar_bot + nBars_int * Abar_int) # Area of concrete section
               ycCentroid, zcCentroid = (h / 2.0) - yCover, (b / 2.0) - zCover # Local axis coordinate of concrete section centroid
               dzc = zcCentroid - zCentroid # distance of concrete section centroid to section centriod about local z axis
               Izc = (b * h**3 / 12) + (Ac * dzc**2) # Second moment of area of concrete section about local z axis
               dyc = ycCentroid - yCentroid # distance of concrete section centroid to section centriod about local y axis
               Iyc = (h * b**3 / 12) + (Ac * dyc**2) # Second moment of area of concrete section about local y axis
               Izbar_top = 0.0
               Iybar_top = 0.0
               for y, z in barCoords_top:
                    Iz = (pi * barDia_top**4 / 64) + Abar_top * z**2 # Second moment of area of top rebars section about local z axis
                    Iy = (pi * barDia_top**4 / 64) + Abar_top * y**2 # Second moment of area of top rebars section about local y axis
                    Izbar_top += Iz
                    Iybar_top += Iy
               Izbar_int = 0.0
               Iybar_int = 0.0
               for y, z in barCoords_int:
                    Iz = (pi * barDia_int**4 / 64) + Abar_int * z**2 # Second moment of area of intermediate rebars section about local z axis
                    Iy = (pi * barDia_int**4 / 64) + Abar_int * y**2 # Second moment of area of intermediate rebars section about local y axis
                    Izbar_int += Iz
                    Iybar_int += Iy
               Izbar_bot = 0.0
               Iybar_bot = 0.0
               for y, z in barCoords_bot:
                    Iz = (pi * barDia_bot**4 / 64) + Abar_bot * z**2 # Second moment of area of bottom rebars section about local z axis
                    Iy = (pi * barDia_bot**4 / 64) + Abar_bot * y**2 # Second moment of area of bottom rebars section about local y axis
                    Izbar_bot += Iz
                    Iybar_bot += Iy
               Iz = Izc + Izbar_top + Izbar_int + Izbar_bot
               Iy = Iyc + Iybar_top + Iybar_int + Iybar_bot
               Jxx = h * b**3 * ((16/3) - 3.36 * (b / h) * (1 - b**4 / (12 * h**4))) / 16 # Torsional constant
     return A, Avy, Avz, Iz, Iy, Jxx, Abar_top, Abar_bot, Abar_int
