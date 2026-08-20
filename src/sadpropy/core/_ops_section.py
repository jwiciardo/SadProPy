import openseespy.opensees as ops
import numpy as np
from ._ops_fiber_section import _generate_fiber_model
from ._ops_beam_integration import _generate_beam_integration_for_distributed_placticity
from ..preprocessing.preprocessing_class_index import SectionModel, SectionProperties, AggregatorSectionDofs

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
    sec_integration_tag = sections.integration_tag
    sec_aggregated_idx = sections.aggregated_sec_idx
    sec_aggregated_tag = np.full_like(sec_aggregated_idx, -1)
    sec_aggregated_tag[sec_aggregated_idx >= 0] = sections.sec_tag[sec_aggregated_idx[sec_aggregated_idx >= 0]]
    sec_dims = sections.dimensions
    sec_props = sections.properties
    if ndim == 3:
        for i in sections.index:
            mat_idx = sec_mats_idx[i][np.argmax(sec_mats_idx[i] != -1)] # Get the first non -1 material index in list of material indices
            if sec_model[i] == SectionModel.Elastic:
                ops.section(
                    'Elastic',
                    int(sec_tag[i]), # secTag
                    float(mat_props[mat_idx, mat_def[mat_idx].properties.E]), # E_mod
                    float(sec_props[i, SectionProperties.A]), # A
                    float(sec_props[i, SectionProperties.Iz]), # Iz
                    float(sec_props[i, SectionProperties.Iy]), # Iy
                    float(mat_props[mat_idx, mat_def[mat_idx].properties.G]), # G_mod
                    float(sec_props[i, SectionProperties.Jxx]), # Jxx
                    float(sec_props[i, SectionProperties.alphaY]), # alphaY
                    float(sec_props[i, SectionProperties.alphaZ]), # alphaZ
                )
            if sec_model[i] == SectionModel.Fiber:
                ops.section(
                    'Fiber',
                    int(sec_tag[i]), # secTag
                    '-GJ',
                    float(mat_props[mat_idx, mat_def[mat_idx].properties.G] * sec_props[i, SectionProperties.Jxx]), # GJ
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
                mats = []
                for idx, tag in enumerate(sec_mats_tag[i]):
                    if tag >= 1:
                        mats.append(int(tag))
                        if idx == AggregatorSectionDofs.P:
                            mats.append('P')
                        elif idx == AggregatorSectionDofs.Mz:
                            mats.append('Mz')
                        elif idx == AggregatorSectionDofs.Vy:
                            mats.append('Vy')
                        elif idx == AggregatorSectionDofs.My:
                            mats.append('My')
                        elif idx == AggregatorSectionDofs.Vz:
                            mats.append('Vz')
                        elif idx == AggregatorSectionDofs.T:
                            mats.append('T')
                ops.section(
                    'Aggregator',
                    int(sec_tag[i]), # secTag
                    *mats, # *mats = [matTag1,dof1,matTag2,dof2,...]
                    int(sec_aggregated_tag[i]), # sectionTag
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
    # NEED TO FINISH CODE FOR 2D-STRUCTURE