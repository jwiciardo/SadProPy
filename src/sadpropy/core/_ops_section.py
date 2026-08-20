import openseespy.opensees as ops
import numpy as np
from ._ops_fiber_section import _generate_fiber_model
from ._ops_beam_integration import _generate_beam_integration_for_distributed_placticity
from ..preprocessing.preprocessing_class_index import SectionModel, SectionProperties, AggregatorElasticProperties
from ..preprocessing.preprocessing_dictionary import section_definition_dict, section_fiber_dict

def _define_sections(ndim, modeldata):
    materials = modeldata.materials # Retrieve materials data
    mat_def = materials.mat_def
    mat_props = materials.properties

    sections = modeldata.frame_sections # Retrieve sections data
    sec_tag = sections.sec_tag
    sec_model = sections.sec_model
    sec_def = sections.sec_def
    sec_mats_idx = sections.mats_idx
    sec_mats_tag = np.full_like(sec_mats_idx, -1)
    sec_mats_tag[sec_mats_idx >= 0] = materials.mat_tag[sec_mats_idx[sec_mats_idx >= 0]]
    sec_integration_type = sections.integration_type
    sec_integration_points = sections.integration_points
    sec_integration_tag = sections.integration_tag
    sec_dims = sections.dimensions
    sec_props = sections.properties
    print(sections)

    if ndim == 3:
        for i in sections.index:
            mat_idx = sec_mats_idx[i][np.argmax(sec_mats_idx[i] != -1)] # Get the first non -1 material index in list of material indices
            if sec_model[i] == SectionModel.Elastic:
                ops.section(
                    'Elastic',
                    int(sec_tag[i]), # secTag
                    float(mat_props[mat_idx, mat_def[i].properties.E]), # E_mod
                    float(sec_props[i, SectionProperties.A]), # A
                    float(sec_props[i, SectionProperties.Iz]), # Iz
                    float(sec_props[i, SectionProperties.Iy]), # Iy
                    float(mat_props[mat_idx, mat_def[i].properties.G]), # G_mod
                    float(sec_props[i, SectionProperties.Jxx]), # Jxx
                    float(sec_props[i, SectionProperties.alphaY]), # alphaY
                    float(sec_props[i, SectionProperties.alphaZ]), # alphaZ
                )
            if sec_model[i] == SectionModel.Fiber:
                ops.section(
                    'Fiber',
                    int(sec_tag[i]), # secTag
                    '-GJ',
                    float(mat_props[mat_idx, mat_def[i].properties.G] * sec_props[i, SectionProperties.Jxx]), # GJ
                )
                _generate_fiber_model(
                    section_definition=sec_def[i],
                    section_tag=int(sec_tag[i]),
                    materials_tag=sec_mats_tag[i],
                    dimensions=sec_dims[i],
                    properties=sec_props[i]
                )
                _generate_beam_integration_for_distributed_placticity(
                    integration_type=sec_integration_type[i],
                    integration_tag=int(sec_integration_tag[i]),
                    section_tag=int(sec_tag[i]),
                    integration_points=int(sec_integration_points[i]),
                )
            if sec_model[i] == SectionModel.Aggregator:
                float(mat_props[AggregatorProperties.Vy, mat_def[i].properties.G] * sec_props[i, SectionProperties.Avy])
                ops.section(
                    'Aggregator',
                    int(sec_tag[i]), # secTag

                )
    else:
        for i in sections.index:
            mat_idx = sec_mats_idx[i, 0]
            if sec_model[i] == SectionModel.Elastic:
                ops.section(
                    'Elastic',
                    int(sec_tag[i]), # secTag
                    float(mat_props[mat_idx, mat_def[i].properties.E]), # E_mod
                    float(sec_props[i, SectionProperties.A]), # A
                    float(sec_props[i, SectionProperties.Iz]), # Iz
                    float(mat_props[mat_idx, mat_def[i].properties.G]), # G_mod
                    float(sec_props[i, SectionProperties.alphaY]), # alphaY
                )




class Sec:
    def __init__(self, workspace):
        self.ws = workspace
        self.tag = self.ws.tag_manager
    
    def define(self):
        if data['Integration Type'] == 'Lobatto':
            IntegrationTag = self.tag.add('Integration', f"{SectionName}")
            SectionTag = self.tag.get_tag('Section', f"{SectionName}")
            Nip = 5 # Number of integration point
                        # type: 'Lobatto', tag,            secTag,     N
            ops.beamIntegration('Lobatto', IntegrationTag, SectionTag, Nip) # Defining integration method