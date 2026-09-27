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

ndim = 2
ndof = 3
ops.wipe()
ops.model('basic', '-ndm', ndim, '-ndf', ndof)
node_idx = np.asarray((
    0,
    1,
    2,
    3,
    ), dtype=np.int32
)
node_tag = np.asarray((
    1,
    2,
    3,
    4,
    ), dtype=np.int32
)
coords = np.asarray((
    (0.0, 0.0, 0.0),
    (8.0, 0.0, 0.0),
    (0.0, 4.0, 0.0),
    (8.0, 4.0, 0.0),
    ), dtype=np.float64
)
ops.node(1, *(0.0, 0.0))
ops.node(2, *(8.0, 0.0))
ops.node(3, *(0.0, 4.0))
ops.node(4, *(8.0, 4.0))

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
Ibeam = (0.3*(0.6**3))/12
Ibeam = to_internalunits.second_moment_of_area(values=Ibeam)
Avbeam = 5/6*Abeam
beam_weight = to_internalunits.unitweight(values=23.6)*Abeam
Acol = 0.75*0.75
Acol = to_internalunits.area(values=Acol)
Icol = (0.75*(0.75**3))/12
Icol = to_internalunits.second_moment_of_area(values=Icol)
Avcol = 5/6*Acol
col_weight = to_internalunits.unitweight(values=23.6)*Acol

ops.uniaxialMaterial('Elastic', 1, E * Acol)
ops.uniaxialMaterial('Elastic', 2, E * Icol)
ops.uniaxialMaterial('Elastic', 3, G * Avcol)
ops.uniaxialMaterial('Elastic', 4, E * Abeam)
ops.uniaxialMaterial('Elastic', 5, E * Ibeam)
ops.uniaxialMaterial('Elastic', 6, G * Avbeam)

ops.section('Aggregator', 1, *(1, 'P', 2, 'Mz', 3, 'Vy'))
ops.section('Aggregator', 2, *(4, 'P', 5, 'Mz', 6, 'Vy'))

element_idx = np.asarray((
    0,
    1,
    2,
    ), dtype=np.int32
)
element_tag = np.asarray((
    1,
    2,
    3,
    ), dtype=np.int32
)
end_nodes_idx = np.asarray((
    (0, 2),
    (1, 3),
    (2, 3),
    ), dtype=np.int32
)
element_type = np.asarray((
    "Column",
    "Column",
    "Beam",
    ), dtype="U32"
)
rigid_zone_factor = np.asanyarray((
    1.0,
    1.0,
    0.0,
    ), dtype=np.float64
)
offsets_length = np.asarray((
    (0.0, 0.6),
    (0.0, 0.6),
    (0.375, 0.375),
    ), dtype=np.float64
)
end_offsets = np.asarray((
    (0.0, 0.0, 0.0, -0.6),
    (0.0, 0.0, 0.0, -0.6),
    (0.375, 0.0, -0.375, 0.0),
    ), dtype=np.float64
)
print()
ops.beamIntegration('ConcentratedPlasticity', 1, 1, 1, 1)
ops.geomTransf('Linear', 1, '-jntOffset', *list(map(float, rigid_zone_factor[0] * end_offsets[0, :2])), *list(map(float, rigid_zone_factor[0] * end_offsets[0, 2:4])))
#ops.element('elasticBeamColumn', 1, *(1, 3), 1, 1)
ops.element('forceBeamColumn', 1, *(1, 3), 1, 1)
#ops.element('elasticBeamColumn', 1, *(1, 3), Acol, E, Icol, 1)
ops.beamIntegration('ConcentratedPlasticity', 2, 1, 1, 1)
ops.geomTransf('Linear', 2, '-jntOffset', *list(map(float, rigid_zone_factor[1] * end_offsets[1, :2])), *list(map(float, rigid_zone_factor[1] * end_offsets[1, 2:4])))
#ops.element('elasticBeamColumn', 2, *(2, 4), 1, 2)
ops.element('forceBeamColumn', 2, *(2, 4), 2, 2)
#ops.element('elasticBeamColumn', 2, *(2, 4), Acol, E, Icol, 2)

ops.beamIntegration('ConcentratedPlasticity', 3, 2, 2, 2)
ops.geomTransf('Linear', 3, '-jntOffset', *list(map(float, rigid_zone_factor[2] * end_offsets[2, :2])), *list(map(float, rigid_zone_factor[2] * end_offsets[2, 2:4])))
#ops.element('elasticBeamColumn', 3, *(3, 4), 2, 3)
ops.element('forceBeamColumn', 3, *(3, 4), 3, 3)
#ops.element('elasticBeamColumn', 3, *(3, 4), Abeam, E, Ibeam, 3)

ops.fix(1, 1, 1, 1)
ops.fix(2, 1, 1, 1)

ops.timeSeries('Constant', 1, '-factor', 1.0)
ops.pattern('Plain', 1, 1)
# Selfweight
ops.eleLoad('-ele', 1, '-type', '-beamUniform', 0.0, -col_weight)
ops.eleLoad('-ele', 2, '-type', '-beamUniform', 0.0, -col_weight)
ops.eleLoad('-ele', 3, '-type', '-beamUniform', -beam_weight, 0.0)

for idx in [0, 1]:
    if rigid_zone_factor[idx] == 1.0:
        jnode = end_nodes_idx[idx, 1]
        tag = int(node_tag[jnode])
        offset_length = float(offsets_length[idx, 1])
        ops.load(tag, *(0.0, -col_weight * offset_length, 0.0))



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
    coords=coords,
    element_idx=element_idx,
    element_tag=element_tag,
    end_nodes_idx=end_nodes_idx,
    element_type=element_type,
    rigid_zone_factor=rigid_zone_factor,
    offsets_length=offsets_length
)
print(element_force_data)

if analysis_code != 0:
    raise RuntimeError(
        f"Analysis failed with code {analysis_code}"
    )

ops.reactions()

for node in (1, 2):
    print(
        "Node",
        node,
        "Reaction",
        ops.nodeReaction(node, 1),
        ops.nodeReaction(node, 2),
        ops.nodeReaction(node, 3),
    )

for node in (1, 2, 3, 4):
    print(
        "Node",
        node,
        "Displacement",
        from_internalunits.length(values=ops.nodeDisp(node, 1), unit='mm'),
        from_internalunits.length(values=ops.nodeDisp(node, 2), unit='mm'),
        from_internalunits.angle(values=ops.nodeDisp(node, 3), unit='rad'),
    )

for ele_tag in (1, 2, 3):
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