import openseespy.opensees as ops
import opsvis as opsv
import matplotlib.pyplot as plt
from ..preprocessing.preprocessing_class_index import SectionProperties, RectangularConcreteFiberDimensions

# GENERATE FIBER DIVISION
def _rectangular_concrete_fiber_model(section_tag, materials_tag, dimensions, properties):
    h = float(dimensions[RectangularConcreteFiberDimensions.h])
    b = float(dimensions[RectangularConcreteFiberDimensions.b])
    cover = float(dimensions[RectangularConcreteFiberDimensions.cover])
    barDiaHoop = float(dimensions[RectangularConcreteFiberDimensions.barDiaHoop])
    barDiaTop = float(dimensions[RectangularConcreteFiberDimensions.barDiaTop])
    nBarsTop = int(dimensions[RectangularConcreteFiberDimensions.nBarsTop])
    nBarsBot = int(dimensions[RectangularConcreteFiberDimensions.nBarsBot])
    nBarsInt = int(dimensions[RectangularConcreteFiberDimensions.nBarsInt])
    AbarTop = float(properties[SectionProperties.AbarTop])
    AbarInt = float(properties[SectionProperties.AbarInt])
    AbarBot = float(properties[SectionProperties.AbarBot])
    mat_core_tag = int(materials_tag[0])
    mat_cover_tag = int(materials_tag[1])
    mat_rebar_tag = int(materials_tag[2])

    d_prime = cover + barDiaHoop + barDiaTop / 2.0 # cover to centroid of longitudinal reinforcements
    yCentroid, zCentroid = 0.0, 0.0 # Coordinate of section centroid in local axes
    yCover, zCover = yCentroid + h / 2.0, zCentroid + b / 2.0 # Coordinate of cover edge from centroid in local axes
    yCore, zCore = yCentroid + yCover - d_prime, zCentroid + zCover - d_prime # Coordinate of core edge from centroid in local axes

    nBarsSide = int(nBarsInt / 2)
    nMeshYCore = 15 # Number of mesh along local y-axis of core
    nMeshZCore = 15 # Number of mesh along local z-axis of core
    nMeshYCover = 15 # Number of mesh along local y-axis of cover
    nMeshZCover = 15 # Number of mesh along local z-axis of cover
    yStartInt = -yCore + (h - 2 * d_prime) / (nBarsSide + 1) # Coordinate of intermediate bars at start in local y-axis
    yEndInt = yCore - (h - 2 * d_prime) / (nBarsSide + 1) # Coordinate of intermediate bars at end in local y-axis

    # type: 'quad', matTag,        numSubdivIJ, numSubdivJK, *crdsI (y, z),     *crdsJ (y, z),      *crdsK (y, z),       *crdsL (y, z)
    ops.patch('quad', mat_core_tag,  nMeshYCore,  nMeshZCore,  *(yCore, zCore),   *(-yCore, zCore),   *(-yCore, -zCore),   *(yCore, -zCore)) # Define Patch object: core
    ops.patch('quad', mat_cover_tag, 2,           nMeshZCover, *(yCover, zCover), *(yCore, zCore),    *(yCore, -zCore),    *(yCover, -zCover)) # Define Patch object: top cover
    ops.patch('quad', mat_cover_tag, nMeshYCover, 2,           *(yCover, zCover), *(-yCover, zCover), *(-yCore, zCore),    *(yCore, zCore)) # Define Patch object: left cover
    ops.patch('quad', mat_cover_tag, 2,           nMeshZCover, *(-yCore, zCore),  *(-yCover, zCover), *(-yCover, -zCover), *(-yCore, -zCore)) # Define Patch object: bottom cover
    ops.patch('quad', mat_cover_tag, nMeshYCover, 2,           *(yCore, -zCore),  *(-yCore, -zCore),  *(-yCover, -zCover), *(yCover, -zCover)) # Define Patch object: right cover
    # type: 'straight', matTag,        numFiber, areaFiber, *start (y, z),        *end (y, z)
    ops.layer('straight', mat_rebar_tag, nBarsTop, AbarTop,   *(yCore, zCore),      *(yCore, -zCore)) # Define Layer object: top reinforcements
    ops.layer('straight', mat_rebar_tag, nBarsSide, AbarInt,   *(yStartInt, zCore),  *(yEndInt, zCore)) # Define Layer object: left reinforcements
    ops.layer('straight', mat_rebar_tag, nBarsBot, AbarBot,   *(-yCore, zCore),     *(-yCore, -zCore)) # Define Layer object: bottom reinforcements
    ops.layer('straight', mat_rebar_tag, nBarsSide, AbarInt,   *(yStartInt, -zCore), *(yEndInt, -zCore)) # Define Layer object: right reinforcements

    # Plot the fiber section data
    fiber_sec = [['section', 'Fiber', section_tag],
                ['patch', 'quad', mat_core_tag,  nMeshYCore,  nMeshZCore,  yCore, zCore,   -yCore, zCore,   -yCore, -zCore,   yCore, -zCore],
                ['patch', 'quad', mat_cover_tag, 2,           nMeshZCover, yCover, zCover, yCore, zCore,    yCore, -zCore,    yCover, -zCover],
                ['patch', 'quad', mat_cover_tag, nMeshYCover, 2,           yCover, zCover, -yCover, zCover, -yCore, zCore,    yCore, zCore],
                ['patch', 'quad', mat_cover_tag, 2,           nMeshZCover, -yCore, zCore,  -yCover, zCover, -yCover, -zCover, -yCore, -zCore],
                ['patch', 'quad', mat_cover_tag, nMeshYCover, 2,           yCore, -zCore,  -yCore, -zCore,  -yCover, -zCover, yCover, -zCover],
                ['layer', 'straight', mat_rebar_tag, nBarsTop, AbarTop, yCore, zCore,      yCore, -zCore],
                ['layer', 'straight', mat_rebar_tag, nBarsSide, AbarInt, yStartInt, zCore,  yEndInt, zCore],
                ['layer', 'straight', mat_rebar_tag, nBarsBot, AbarBot, -yCore, zCore,     -yCore, -zCore],
                ['layer', 'straight', mat_rebar_tag, nBarsSide, AbarInt, yStartInt, -zCore, yEndInt, -zCore]]
    matcolor = ['r', 'lightgrey', 'gold', 'w', 'w', 'w']
    opsv.plot_fiber_section(fiber_sec, matcolor=matcolor)
    plt.title('Section ID:%d' %section_tag)
    plt.axis('equal')

def _generate_fiber_model(section_definition, section_tag, materials_tag, dimensions, properties):
    section_definition.generate_fiber_model(section_tag=section_tag, materials_tag=materials_tag, dimensions=dimensions, properties=properties)