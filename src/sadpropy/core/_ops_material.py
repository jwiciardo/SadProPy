import openseespy.opensees as ops
from ..preprocessing.preprocessing_class_index import MaterialModel
from ..preprocessing._preprocessing_definition import _material_definition

def _define_material(modeldata):
    # Define Material
    materials = modeldata.materials # Retrieve materials data
    mat_tag = materials.mat_tag
    mat_model = materials.mat_model
    mat_def = materials.mat_def
    mat_props = materials.properties
    print(materials)
    for i in materials.index:
        if mat_model[i] == MaterialModel.Elastic:
            ops.uniaxialMaterial(
                'Elastic',
                int(mat_tag[i]), # matTag
                float(mat_props[i, mat_def[i].properties.E]), # E
            )
        if mat_model[i] == MaterialModel.Concrete04:
            ops.uniaxialMaterial(
                'Concrete04',
                int(mat_tag[i]), # matTag
                float(mat_props[i, mat_def[i].properties.fc]), # fc
                float(mat_props[i, mat_def[i].properties.epsc]), # epsc
                float(mat_props[i, mat_def[i].properties.epscu]), # epscu
                float(mat_props[i, mat_def[i].properties.E]), # Ec
                float(mat_props[i, mat_def[i].properties.fct]), # fct
                float(mat_props[i, mat_def[i].properties.et]), # et
                float(mat_props[i, mat_def[i].properties.beta]), # beta
            )
        if mat_model[i] == MaterialModel.Concrete04MinMax:
            ops.uniaxialMaterial(
                'Concrete04',
                int(mat_tag[i]), # matTag
                float(mat_props[i, mat_def[i].properties.fc]), # fc
                float(mat_props[i, mat_def[i].properties.epsc]), # epsc
                float(mat_props[i, mat_def[i].properties.epscu]), # epscu
                float(mat_props[i, mat_def[i].properties.E]), # Ec
                float(mat_props[i, mat_def[i].properties.fct]), # fct
                float(mat_props[i, mat_def[i].properties.et]), # et
                float(mat_props[i, mat_def[i].properties.beta]), # beta
            )
            ops.uniaxialMaterial(
                'MinMax',
                int(mat_tag[i]) + int(1000), # matTag
                int(mat_tag[i]), # otherTag
                '-min',
                float(mat_props[i, mat_def[i].properties.ecmax]), # minStrain
                '-max',
                float(mat_props[i, mat_def[i].properties.etmax]), # maxStrain
            )
        if mat_model[i] == MaterialModel.Steel02:
            ops.uniaxialMaterial(
                'Steel02',
                int(mat_tag[i]), # matTag
                float(mat_props[i, mat_def[i].properties.fy]), # Fy
                float(mat_props[i, mat_def[i].properties.E]), # E0
                float(mat_props[i, mat_def[i].properties.b]), # b
                float(mat_props[i, mat_def[i].properties.R0]), # R0
                float(mat_props[i, mat_def[i].properties.cR1]), # cR1
                float(mat_props[i, mat_def[i].properties.cR2]), # cR2
                float(mat_props[i, mat_def[i].properties.a1]), # a1
                float(mat_props[i, mat_def[i].properties.a2]), # a2
                float(mat_props[i, mat_def[i].properties.a3]), # a3
                float(mat_props[i, mat_def[i].properties.a4]), # a4
                float(mat_props[i, mat_def[i].properties.finit]), # sigInit
            )
        if mat_model[i] == MaterialModel.Steel02MinMax:
            ops.uniaxialMaterial(
                'Steel02',
                int(mat_tag[i]), # matTag
                float(mat_props[i, mat_def[i].properties.fy]), # Fy
                float(mat_props[i, mat_def[i].properties.E]), # E0
                float(mat_props[i, mat_def[i].properties.b]), # b
                float(mat_props[i, mat_def[i].properties.R0]), # R0
                float(mat_props[i, mat_def[i].properties.cR1]), # cR1
                float(mat_props[i, mat_def[i].properties.cR2]), # cR2
                float(mat_props[i, mat_def[i].properties.a1]), # a1
                float(mat_props[i, mat_def[i].properties.a2]), # a2
                float(mat_props[i, mat_def[i].properties.a3]), # a3
                float(mat_props[i, mat_def[i].properties.a4]), # a4
                float(mat_props[i, mat_def[i].properties.finit]), # sigInit
            )
            ops.uniaxialMaterial(
                'MinMax',
                int(mat_tag[i]) + int(1000), # matTag
                int(mat_tag[i]), # otherTag
                '-min',
                float(mat_props[i, mat_def[i].properties.ecmax]), # minStrain
                '-max',
                float(mat_props[i, mat_def[i].properties.etmax]), # maxStrain
            )