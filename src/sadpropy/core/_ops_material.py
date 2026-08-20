import openseespy.opensees as ops
from ..preprocessing.preprocessing_class_index import MaterialModel

def _define_materials(modeldata):
    materials = modeldata.materials # Retrieve materials data
    mat_tag = materials.mat_tag
    mat_model = materials.mat_model
    mat_def = materials.mat_def
    mat_props = materials.properties
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
        if mat_model[i] == MaterialModel.Axial:
            ops.uniaxialMaterial(
                'Elastic',
                int(mat_tag[i]), # matTag
                float(mat_props[i, mat_def[i].properties.EA]), # E
            )
        if mat_model[i] == MaterialModel.FlexuralZ:
            ops.uniaxialMaterial(
                'Elastic',
                int(mat_tag[i]), # matTag
                float(mat_props[i, mat_def[i].properties.EIz]), # E
            )
        if mat_model[i] == MaterialModel.ShearY:
            ops.uniaxialMaterial(
                'Elastic',
                int(mat_tag[i]), # matTag
                float(mat_props[i, mat_def[i].properties.GAvy]), # E
            )
        if mat_model[i] == MaterialModel.FlexuralY:
            ops.uniaxialMaterial(
                'Elastic',
                int(mat_tag[i]), # matTag
                float(mat_props[i, mat_def[i].properties.EIy]), # E
            )
        if mat_model[i] == MaterialModel.ShearZ:
            ops.uniaxialMaterial(
                'Elastic',
                int(mat_tag[i]), # matTag
                float(mat_props[i, mat_def[i].properties.GAvz]), # E
            )
        if mat_model[i] == MaterialModel.Torsional:
            ops.uniaxialMaterial(
                'Elastic',
                int(mat_tag[i]), # matTag
                float(mat_props[i, mat_def[i].properties.GJxx]), # E
            )
        if mat_model[i] == MaterialModel.IMKBilinear:
            ops.uniaxialMaterial(
                'Bilin',
                int(mat_tag[i]), # matTag
                float(mat_props[i, mat_def[i].properties.K0]), # K0
                float(mat_props[i, mat_def[i].properties.asPos]), # as_Plus
                float(mat_props[i, mat_def[i].properties.asNeg]), # as_Neg
                float(mat_props[i, mat_def[i].properties.MyPos]), # My_Plus
                float(mat_props[i, mat_def[i].properties.MyNeg]), # My_Neg
                float(mat_props[i, mat_def[i].properties.LamdaS]), # Lamda_S
                float(mat_props[i, mat_def[i].properties.LamdaC]), # Lamda_C
                float(mat_props[i, mat_def[i].properties.LamdaA]), # Lamda_A
                float(mat_props[i, mat_def[i].properties.LamdaK]), # Lamda_K
                float(mat_props[i, mat_def[i].properties.cS]), # c_S
                float(mat_props[i, mat_def[i].properties.cC]), # c_C
                float(mat_props[i, mat_def[i].properties.cA]), # c_A
                float(mat_props[i, mat_def[i].properties.cK]), # c_K
                float(mat_props[i, mat_def[i].properties.thetapPos]), # theta_p_Plus
                float(mat_props[i, mat_def[i].properties.thetapNeg]), # theta_p_Neg
                float(mat_props[i, mat_def[i].properties.thetapcPos]), # theta_pc_Plus
                float(mat_props[i, mat_def[i].properties.thetapcNeg]), # theta_pc_Neg
                float(mat_props[i, mat_def[i].properties.ResPos]), # Res_Pos
                float(mat_props[i, mat_def[i].properties.ResNeg]), # Res_Neg
                float(mat_props[i, mat_def[i].properties.thetauPos]), # theta_u_Plus
                float(mat_props[i, mat_def[i].properties.thetauNeg]), # theta_u_Neg
                float(mat_props[i, mat_def[i].properties.DPos]), # D_Plus
                float(mat_props[i, mat_def[i].properties.DNeg]), # D_Neg
                float(mat_props[i, mat_def[i].properties.nFactor]), # nFactor
            )
        if mat_model[i] == MaterialModel.IMKPeakOriented:
            ops.uniaxialMaterial(
                'IMKPeakOriented',
                int(mat_tag[i]), # matTag
                float(mat_props[i, mat_def[i].properties.K0]), # K0
                float(mat_props[i, mat_def[i].properties.asPos]), # as_Plus
                float(mat_props[i, mat_def[i].properties.asNeg]), # as_Neg
                float(mat_props[i, mat_def[i].properties.MyPos]), # My_Plus
                float(mat_props[i, mat_def[i].properties.MyNeg]), # My_Neg
                float(mat_props[i, mat_def[i].properties.LamdaS]), # Lamda_S
                float(mat_props[i, mat_def[i].properties.LamdaC]), # Lamda_C
                float(mat_props[i, mat_def[i].properties.LamdaA]), # Lamda_A
                float(mat_props[i, mat_def[i].properties.LamdaK]), # Lamda_K
                float(mat_props[i, mat_def[i].properties.cS]), # c_S
                float(mat_props[i, mat_def[i].properties.cC]), # c_C
                float(mat_props[i, mat_def[i].properties.cA]), # c_A
                float(mat_props[i, mat_def[i].properties.cK]), # c_K
                float(mat_props[i, mat_def[i].properties.thetapPos]), # theta_p_Plus
                float(mat_props[i, mat_def[i].properties.thetapNeg]), # theta_p_Neg
                float(mat_props[i, mat_def[i].properties.thetapcPos]), # theta_pc_Plus
                float(mat_props[i, mat_def[i].properties.thetapcNeg]), # theta_pc_Neg
                float(mat_props[i, mat_def[i].properties.ResPos]), # Res_Pos
                float(mat_props[i, mat_def[i].properties.ResNeg]), # Res_Neg
                float(mat_props[i, mat_def[i].properties.thetauPos]), # theta_u_Plus
                float(mat_props[i, mat_def[i].properties.thetauNeg]), # theta_u_Neg
                float(mat_props[i, mat_def[i].properties.DPos]), # D_Plus
                float(mat_props[i, mat_def[i].properties.DNeg]), # D_Neg
            )
        if mat_model[i] == MaterialModel.IMKPinching:
            ops.uniaxialMaterial(
                'IMKPinching',
                int(mat_tag[i]), # matTag
                float(mat_props[i, mat_def[i].properties.K0]), # K0
                float(mat_props[i, mat_def[i].properties.asPos]), # as_Plus
                float(mat_props[i, mat_def[i].properties.asNeg]), # as_Neg
                float(mat_props[i, mat_def[i].properties.MyPos]), # My_Plus
                float(mat_props[i, mat_def[i].properties.MyNeg]), # My_Neg
                float(mat_props[i, mat_def[i].properties.FprPos]), # FprPos
                float(mat_props[i, mat_def[i].properties.FprNeg]), # FprNeg
                float(mat_props[i, mat_def[i].properties.Apinch]), # A_pinch
                float(mat_props[i, mat_def[i].properties.LamdaS]), # Lamda_S
                float(mat_props[i, mat_def[i].properties.LamdaC]), # Lamda_C
                float(mat_props[i, mat_def[i].properties.LamdaA]), # Lamda_A
                float(mat_props[i, mat_def[i].properties.LamdaK]), # Lamda_K
                float(mat_props[i, mat_def[i].properties.cS]), # c_S
                float(mat_props[i, mat_def[i].properties.cC]), # c_C
                float(mat_props[i, mat_def[i].properties.cA]), # c_A
                float(mat_props[i, mat_def[i].properties.cK]), # c_K
                float(mat_props[i, mat_def[i].properties.thetapPos]), # theta_p_Plus
                float(mat_props[i, mat_def[i].properties.thetapNeg]), # theta_p_Neg
                float(mat_props[i, mat_def[i].properties.thetapcPos]), # theta_pc_Plus
                float(mat_props[i, mat_def[i].properties.thetapcNeg]), # theta_pc_Neg
                float(mat_props[i, mat_def[i].properties.ResPos]), # Res_Pos
                float(mat_props[i, mat_def[i].properties.ResNeg]), # Res_Neg
                float(mat_props[i, mat_def[i].properties.thetauPos]), # theta_u_Plus
                float(mat_props[i, mat_def[i].properties.thetauNeg]), # theta_u_Neg
                float(mat_props[i, mat_def[i].properties.DPos]), # D_Plus
                float(mat_props[i, mat_def[i].properties.DNeg]), # D_Neg
            )