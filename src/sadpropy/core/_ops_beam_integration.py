import openseespy.opensees as ops
from ..preprocessing.preprocessing_class_index import IntegrationType

def _generate_beam_integration_for_distributed_placticity(integration_type, integration_tag, section_tag, integration_points):
    if integration_type == IntegrationType.Lobatto:
        ops.beamIntegration(
            'Lobatto',
            integration_tag, # tag
            section_tag, # secTag
            integration_points, # N
        )

def _generate_beam_integration_for_concentrated_placticity(integration_type, integration_tag, sections_tag, locations):
    if integration_type == IntegrationType.HingeRadau:
        secI_tag = sections_tag[0]
        secJ_tag = sections_tag[1]
        secE_tag = sections_tag[2]
        LpI = locations[0]
        LpJ = locations[1]
        ops.beamIntegration(
            'HingeRadau',
            integration_tag, # tag
            secI_tag, # secI
            LpI, # lpI
            secJ_tag, # secJ
            LpJ, # lpJ
            secE_tag, # secE
        )


