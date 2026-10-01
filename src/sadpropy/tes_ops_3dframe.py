import openseespy.opensees as ops
import numpy as np
from sadpropy.postprocessing.output_storer import OutputStorer
from sadpropy.preprocessing.preprocessing_dataclass import UserDefinedUnits
from sadpropy.utility import ConverterToInternalUnits, ConverterFromInternalUnits

units = UserDefinedUnits(
    force="kN",
    length="m",
    mass="kg",
    stress="MPa",
    time="s",
    angle="rad",
)
to_internalunits = ConverterToInternalUnits(units=units)
from_internalunits = ConverterFromInternalUnits()

ndim = 3
ndof = 6
ops.wipe()
ops.model('basic', '-ndm', ndim, '-ndf', ndof)
node_idx = np.asarray((
    0,
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    ), dtype=np.int32
)
node_tag = np.asarray((
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    ), dtype=np.int32
)
node_coords = np.asarray((
    (0.0, 0.0, 0.0),
    (8.0, 0.0, 0.0),
    (0.0, 8.0, 0.0),
    (8.0, 8.0, 0.0),
    (0.0, 0.0, 4.0),
    (8.0, 0.0, 4.0),
    (0.0, 8.0, 4.0),
    (8.0, 8.0, 4.0),
    ), dtype=np.float64
)
for tag, coords in zip(node_tag, node_coords):
    coords = list(map(float, coords))
    ops.node(int(tag), *coords)

# Material Properties
fc = 30.0
fc = to_internalunits.stress(values=fc)
E = 4700*np.sqrt(30.0)
E = to_internalunits.stress(values=E)
nu = 0.2
G = E/(2.0*(1.0 + nu))

# Section Properties
Abeam = 0.3*0.6
Abeam = to_internalunits.area(values=Abeam)
Izbeam = (0.3*(0.6**3))/12
Izbeam = to_internalunits.second_moment_of_area(values=Izbeam)
Iybeam = (0.6*(0.3**3))/12
Iybeam = to_internalunits.second_moment_of_area(values=Iybeam)
Jxbeam = 0.6 * 0.3**3 * ((16.0/3.0) - 3.36 * (0.3 / 0.6) * (1.0 - 0.3**4 / (12.0 * 0.6**4))) / 16.0
Jxbeam = to_internalunits.second_moment_of_area(values=Jxbeam)
Avybeam = 5/6*Abeam
Avzbeam = 5/6*Abeam
beam_weight = to_internalunits.unitweight(values=23.6)*Abeam

Acol = 0.75*0.75
Acol = to_internalunits.area(values=Acol)
Izcol = (0.75*(0.75**3))/12
Izcol = to_internalunits.second_moment_of_area(values=Izcol)
Iycol = (0.75*(0.75**3))/12
Iycol = to_internalunits.second_moment_of_area(values=Iycol)
Jxcol = 0.75 * 0.75**3 * ((16.0/3.0) - 3.36 * (0.75 / 0.75) * (1.0 - 0.75**4 / (12.0 * 0.75**4))) / 16.0
Jxcol = to_internalunits.second_moment_of_area(values=Jxcol)
Avycol = 5/6*Acol
Avzcol = 5/6*Acol
col_weight = to_internalunits.unitweight(values=23.6)*Acol

ops.uniaxialMaterial('Elastic', 1, E * Acol)
ops.uniaxialMaterial('Elastic', 2, E * Izcol)
ops.uniaxialMaterial('Elastic', 3, E * Iycol)
ops.uniaxialMaterial('Elastic', 4, G * Avycol)
ops.uniaxialMaterial('Elastic', 5, G * Avzcol)
ops.uniaxialMaterial('Elastic', 6, G * Jxcol)
ops.uniaxialMaterial('Elastic', 7, E * Abeam)
ops.uniaxialMaterial('Elastic', 8, E * Izbeam)
ops.uniaxialMaterial('Elastic', 9, E * Iybeam)
ops.uniaxialMaterial('Elastic', 10, G * Avybeam)
ops.uniaxialMaterial('Elastic', 11, G * Avzbeam)
ops.uniaxialMaterial('Elastic', 12, G * Jxbeam)

ops.section('Aggregator', 1, *(1, 'P', 2, 'Mz', 3, 'My', 4, 'Vy', 5, 'Vz', 6, 'T'))
ops.section('Aggregator', 2, *(7, 'P', 8, 'Mz', 9, 'My', 10, 'Vy', 11, 'Vz', 12, 'T'))

element_idx = np.asarray((
    0,
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    ), dtype=np.int32
)
element_tag = np.asarray((
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    ), dtype=np.int32
)
end_nodes_idx = np.asarray((
    (0, 4),
    (1, 5),
    (2, 6),
    (3, 7),
    (4, 5),
    (6, 7),
    (4, 6),
    (5, 7),
    ), dtype=np.int32
)
element_type = np.asarray((
    "Column",
    "Column",
    "Column",
    "Column",
    "Beam",
    "Beam",
    "Beam",
    "Beam",
    ), dtype="U32"
)
rigid_zone_factor = np.asanyarray((
    1.0,
    1.0,
    1.0,
    1.0,
    0.0,
    0.0,
    0.0,
    0.0,
    ), dtype=np.float64
)
offsets_length = np.asarray((
    (0.0, 0.6),
    (0.0, 0.6),
    (0.0, 0.6),
    (0.0, 0.6),
    (0.375, 0.375),
    (0.375, 0.375),
    (0.375, 0.375),
    (0.375, 0.375),
    ), dtype=np.float64
)
end_offsets = np.asarray((
    (0.0, 0.0, 0.0, 0.0, 0.0, -0.6),
    (0.0, 0.0, 0.0, 0.0, 0.0, -0.6),
    (0.0, 0.0, 0.0, 0.0, 0.0, -0.6),
    (0.0, 0.0, 0.0, 0.0, 0.0, -0.6),
    (0.375, 0.0, 0.0, -0.375, 0.0, 0.0),
    (0.375, 0.0, 0.0, -0.375, 0.0, 0.0),
    (0.0, 0.375, 0.0, 0.0, -0.375, 0.0),
    (0.0, 0.375, 0.0, 0.0, -0.375, 0.0),
    ), dtype=np.float64
)
vecxz = np.array((
    (0.0, 1.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, -1.0, 0.0),
    (0.0, -1.0, 0.0),
    (1.0, 0.0, 0.0),
    (1.0, 0.0, 0.0),
    ), dtype=np.float64
)
print()
ops.beamIntegration('ConcentratedPlasticity', 1, 1, 1, 1)
ops.geomTransf('Linear', 1, *list(map(float, vecxz[0])), '-jntOffset', *list(map(float, rigid_zone_factor[0] * end_offsets[0, :3])), *list(map(float, rigid_zone_factor[0] * end_offsets[0, 3:6])))
ops.element('forceBeamColumn', 1, *(1, 5), 1, 1)
ops.geomTransf('Linear', 2, *list(map(float, vecxz[1])), '-jntOffset', *list(map(float, rigid_zone_factor[1] * end_offsets[1, :3])), *list(map(float, rigid_zone_factor[1] * end_offsets[1, 3:6])))
ops.element('forceBeamColumn', 2, *(2, 6), 2, 1)
ops.geomTransf('Linear', 3, *list(map(float, vecxz[2])), '-jntOffset', *list(map(float, rigid_zone_factor[2] * end_offsets[2, :3])), *list(map(float, rigid_zone_factor[2] * end_offsets[2, 3:6])))
ops.element('forceBeamColumn', 3, *(3, 7), 3, 1)
ops.geomTransf('Linear', 4, *list(map(float, vecxz[3])), '-jntOffset', *list(map(float, rigid_zone_factor[3] * end_offsets[3, :3])), *list(map(float, rigid_zone_factor[3] * end_offsets[3, 3:6])))
ops.element('forceBeamColumn', 4, *(4, 8), 4, 1)

ops.beamIntegration('ConcentratedPlasticity', 2, 2, 2, 2)
ops.geomTransf('Linear', 5, *list(map(float, vecxz[4])), '-jntOffset', *list(map(float, rigid_zone_factor[4] * end_offsets[4, :3])), *list(map(float, rigid_zone_factor[4] * end_offsets[4, 3:6])))
ops.element('forceBeamColumn', 5, *(5, 6), 5, 2)
ops.geomTransf('Linear', 6, *list(map(float, vecxz[5])), '-jntOffset', *list(map(float, rigid_zone_factor[5] * end_offsets[5, :3])), *list(map(float, rigid_zone_factor[5] * end_offsets[5, 3:6])))
ops.element('forceBeamColumn', 6, *(7, 8), 6, 2)
ops.geomTransf('Linear', 7, *list(map(float, vecxz[6])), '-jntOffset', *list(map(float, rigid_zone_factor[6] * end_offsets[6, :3])), *list(map(float, rigid_zone_factor[6] * end_offsets[6, 3:6])))
ops.element('forceBeamColumn', 7, *(5, 7), 7, 2)
ops.geomTransf('Linear', 8, *list(map(float, vecxz[7])), '-jntOffset', *list(map(float, rigid_zone_factor[7] * end_offsets[7, :3])), *list(map(float, rigid_zone_factor[7] * end_offsets[7, 3:6])))
ops.element('forceBeamColumn', 8, *(6, 8), 8, 2)

ops.fix(1, 1, 1, 1, 1, 1, 1)
ops.fix(2, 1, 1, 1, 1, 1, 1)
ops.fix(3, 1, 1, 1, 1, 1, 1)
ops.fix(4, 1, 1, 1, 1, 1, 1)

ops.timeSeries('Constant', 1, '-factor', 1.0)
ops.pattern('Plain', 1, 1)
# Selfweight
ops.eleLoad('-ele', 1, '-type', '-beamUniform', 0.0, 0.0, -col_weight)
ops.eleLoad('-ele', 2, '-type', '-beamUniform', 0.0, 0.0, -col_weight)
ops.eleLoad('-ele', 3, '-type', '-beamUniform', 0.0, 0.0, -col_weight)
ops.eleLoad('-ele', 4, '-type', '-beamUniform', 0.0, 0.0, -col_weight)
ops.eleLoad('-ele', 5, '-type', '-beamUniform', -beam_weight, 0.0, 0.0)
ops.eleLoad('-ele', 6, '-type', '-beamUniform', -beam_weight, 0.0, 0.0)
ops.eleLoad('-ele', 7, '-type', '-beamUniform', -beam_weight, 0.0, 0.0)
ops.eleLoad('-ele', 8, '-type', '-beamUniform', -beam_weight, 0.0, 0.0)

for idx in [0, 1, 2, 3]:
    if rigid_zone_factor[idx] == 1.0:
        jnode = end_nodes_idx[idx, 1]
        tag = int(node_tag[jnode])
        offset_length = float(offsets_length[idx, 1])
        ops.load(tag, *(0.0, 0.0, -col_weight * offset_length, 0.0, 0.0, 0.0))

# Dead
#ops.eleLoad('-ele', 3, '-type', '-beamUniform', -5*kN/m, 0.0)

# Live
#ops.eleLoad('-ele', 3, '-type', '-beamUniform', -7.5*kN/m, 0.0)

# Run Analysis
tol=1.0e-13,
Maxiter=10,
pFlag=1
ops.wipeAnalysis()
ops.test('NormDispIncr', tol, Maxiter, pFlag)
ops.algorithm('Newton', '-initial')
ops.numberer('RCM')
ops.system('UmfPack')
ops.constraints('Transformation')
ops.integrator('LoadControl', 1)
ops.analysis('Static')

analysis_code = ops.analyze(1)
output = OutputStorer(modeldata=None)
element_load_data = output._get_element_load_data()
element_force_data = output._get_element_force_data(
    converter=to_internalunits,
    ndim=ndim,
    coords=node_coords,
    element_idx=element_idx,
    element_tag=element_tag,
    end_nodes_idx=end_nodes_idx,
    element_type=element_type,
    rigid_zone_factor=rigid_zone_factor,
    offsets_length=offsets_length,
)
print(element_force_data)

if analysis_code != 0:
    raise RuntimeError(
        f"Analysis failed with code {analysis_code}"
    )

ops.reactions()

for node in (1, 2, 3, 4):
    print(
        "Node",
        node,
        "Reaction",
        ops.nodeReaction(node, 1),
        ops.nodeReaction(node, 2),
        ops.nodeReaction(node, 3),
        ops.nodeReaction(node, 4),
        ops.nodeReaction(node, 5),
        ops.nodeReaction(node, 6),
    )

for node in (5, 6, 7, 8):
    print(
        "Node",
        node,
        "Displacement",
        from_internalunits.length(values=ops.nodeDisp(node, 1), unit='mm'),
        from_internalunits.length(values=ops.nodeDisp(node, 2), unit='mm'),
        from_internalunits.length(values=ops.nodeDisp(node, 3), unit='mm'),
        from_internalunits.angle(values=ops.nodeDisp(node, 4), unit='rad'),
        from_internalunits.angle(values=ops.nodeDisp(node, 5), unit='rad'),
        from_internalunits.angle(values=ops.nodeDisp(node, 6), unit='rad'),
    )

for ele_tag in (1, 2, 3, 4, 5, 6, 7, 8):
    print(
        "Element",
        ele_tag,
        "local:",
        ops.eleResponse(ele_tag, "localForces"),
    )

    print(
        "Element",
        ele_tag,
        "global:",
        ops.eleForce(ele_tag),
    )

ops.loadConst('-time', 0.0)