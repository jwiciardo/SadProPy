import openseespy.opensees as ops
import numpy as np
from ..preprocessing.preprocessing_class_index import MaterialModel, SectionProperties

def _define_elements(ndim, modeldata):
    materials = modeldata.materials # Retrieve materials data
    mat_model = materials.mat_model
    mat_def = materials.mat_def
    mat_props = materials.properties
    sections = modeldata.frame_sections # Retrieve sections data
    sec_mat_idx = sections.mats_idx[:, np.argmax(sections.mats_idx != -1)] # Get the first non -1 material index in list of material indices
    sec_props = sections.properties

    nodes = modeldata.nodes # Retrieve nodes data
    elements = modeldata.elements # Retrieve elements data
    ele_tag = elements.element_tag
    ele_nodes_idx = elements.end_nodes_idx
    ele_nodes_tag = nodes.node_tag[ele_nodes_idx]
    ele_sec_idx = elements.sec_idx
    ele_mat_idx = sec_mat_idx[ele_sec_idx]
    ele_transformation_tag = elements.transformation_tag
    ele_transf_tag = elements.transf_tag
    ele_transf_vec = elements.transf_vec
    ele_transf_offsets = elements.transf_offsets
    is_pdelta = modeldata.analysis_preferences.is_pdelta
    if ndim == 3:
        for transf_idx in range(len(ele_transf_tag)):
            vec_z = list(map(float, ele_transf_vec[transf_idx]))
            I_offset = list(map(float, ele_transf_offsets[transf_idx, :3]))
            J_offset = list(map(float, ele_transf_offsets[transf_idx, 3:6]))
            if is_pdelta:
                ops.geomTransf(
                    'PDelta',
                    int(ele_transf_tag[transf_idx]), # transfTag
                    *vec_z, # *vecxz
                    '-jntOffset',
                    *I_offset, # *dI
                    *J_offset, # *dJ
                )
            else:
                ops.geomTransf(
                    'Linear',
                    int(ele_transf_tag[transf_idx]), # transfTag
                    *vec_z, # *vecxz
                    '-jntOffset',
                    *I_offset, # *dI
                    *J_offset, # *dJ
                )
        for i in elements.index:
            ele_nodes = list(map(int, ele_nodes_tag[i]))
            if mat_model[ele_mat_idx[i]] == MaterialModel.Elastic:
                ops.element(
                    'ElasticTimoshenkoBeam',
                    int(ele_tag[i]), # eleTag
                    *ele_nodes, # *eleNodes
                    float(mat_props[ele_mat_idx[i], mat_def[ele_mat_idx[i]].properties.E]), # E_mod
                    float(mat_props[ele_mat_idx[i], mat_def[ele_mat_idx[i]].properties.G]), # G_mod
                    float(sec_props[ele_sec_idx[i], SectionProperties.A]), # Area
                    float(sec_props[ele_sec_idx[i], SectionProperties.Jxx]), # Jxx
                    float(sec_props[ele_sec_idx[i], SectionProperties.Iy]), # Iy
                    float(sec_props[ele_sec_idx[i], SectionProperties.Iz]), # Iz
                    float(sec_props[ele_sec_idx[i], SectionProperties.Avy]), # Avy
                    float(sec_props[ele_sec_idx[i], SectionProperties.Avz]), # Avz
                    int(ele_transformation_tag[i]), # transfTag
                )
    else:
        for transf_idx in range(len(ele_transf_tag)):
            I_offset = list(map(float, ele_transf_offsets[transf_idx, :3]))
            J_offset = list(map(float, ele_transf_offsets[transf_idx, 3:6]))
            if is_pdelta:
                ops.geomTransf(
                    'PDelta',
                    int(ele_transf_tag[transf_idx]), # transfTag
                    '-jntOffset',
                    *I_offset, # *dI
                    *J_offset, # *dJ
                )
            else:
                ops.geomTransf(
                    'Linear',
                    int(ele_transf_tag[transf_idx]), # transfTag
                    '-jntOffset',
                    *I_offset, # *dI
                    *J_offset, # *dJ
                )
        for i in sections.index:
            ele_nodes = list(map(int, ele_nodes_tag[i]))
            if mat_model[ele_mat_idx[i]] == MaterialModel.Elastic:
                ops.element(
                    'ElasticTimoshenkoBeam',
                    int(ele_tag[i]), # eleTag
                    *ele_nodes, # *eleNodes
                    float(mat_props[ele_mat_idx[i], mat_def[ele_mat_idx[i]].properties.E]), # E_mod
                    float(mat_props[ele_mat_idx[i], mat_def[ele_mat_idx[i]].properties.G]), # G_mod
                    float(sec_props[ele_sec_idx[i], SectionProperties.A]), # Area
                    float(sec_props[ele_sec_idx[i], SectionProperties.Iz]), # Iz
                    float(sec_props[ele_sec_idx[i], SectionProperties.Avy]), # Avy
                    int(ele_transformation_tag[i]), # transfTag
                )