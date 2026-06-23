import openseespy.opensees as ops

class MaterialProperties:
    def __init__(self, workspace):
        self.ws = workspace
        self.tag = self.ws.tag_manager
    
    def define(self):
        MatConcrete04_dict = self.ws.mat_concrete04
        for MaterialName, data in MatConcrete04_dict.items():
            MaterialTag = self.tag.add('Material', f"{MaterialName}")
                      # matType: 'Concrete04', matTag,      fc,         epsc,         epscu,         Ec,        fct,         et,         beta
            ops.uniaxialMaterial('Concrete04', MaterialTag, data['fc'], data['epsc'], data['epscu'], data['E'], data['fct'], data['et'], data['beta']) # Defining Material objects

        MatSteel02_dict = self.ws.mat_steel02
        for MaterialName, data in MatSteel02_dict.items():
            MaterialTag = self.tag.add('Material', f"{MaterialName}")
                        # matType: Steel02, matTag,      Fy,         E0,        b,         *params(RO, cR1, cR2)
            ops.uniaxialMaterial('Steel02', MaterialTag, data['fy'], data['E'], data['b'], *(data['R0'], data['cR1'], data['cR2'])) # Defining Material objects
        
        MatMinMax_dict = self.ws.mat_minmax
        for MaterialName, data in MatMinMax_dict.items():
            MaterialTag = self.tag.add('Material', f"{MaterialName}")
            BaseMatTag = self.tag.get_tag('Material', f"{data['Base NL Material']}")
                        # matType: MinMax, matTag,      otherTag,   '-min', minStrain,         '-max', maxStrain
            ops.uniaxialMaterial('MinMax', MaterialTag, BaseMatTag, '-min', data['minStrain'], '-max', data['maxStrain']) # Defining Material objects
        
        MatIMK_dict = self.ws.mat_imk
        for MaterialName, data in MatIMK_dict.items():
            MaterialTag = self.tag.add('Material', f"{MaterialName}")
            if data['Material Model'] == 'IMKBilinear':
                          # matType: 'IMKBilinear',
                ops.uniaxialMaterial('IMKBilinear', MaterialTag, data['K0'], data['as_Pos'], data['as_Neg'], data['My_Pos'], data['My_Neg'], data['Lamda_S'],
                                    data['Lamda_C'], data['Lamda_A'], data['Lamda_K'], data['c_S'],  data['c_C'], data['c_A'], data['c_K'], data['theta_p_Pos'],
                                    data['theta_p_Neg'], data['theta_pc_Pos'], data['theta_pc_Neg'], data['Res_Pos'], data['Res_Neg'], data['theta_u_Pos'],
                                    data['theta_u_Neg'], data['D_Pos'], data['D_Neg'], data['nFactor']) # Defining Material objects
            elif data['Material Model'] == 'IMKPeakOriented':
                          # matType: 'IMKPeakOriented',
                ops.uniaxialMaterial('IMKPeakOriented', MaterialTag, data['K0'], data['as_Pos'], data['as_Neg'], data['My_Pos'], data['My_Neg'], data['Lamda_S'],
                                    data['Lamda_C'], data['Lamda_A'], data['Lamda_K'], data['c_S'],  data['c_C'], data['c_A'], data['c_K'], data['theta_p_Pos'],
                                    data['theta_p_Neg'], data['theta_pc_Pos'], data['theta_pc_Neg'], data['Res_Pos'], data['Res_Neg'], data['theta_u_Pos'],
                                    data['theta_u_Neg'], data['D_Pos'], data['D_Neg']) # Defining Material objects
            elif data['Material Model'] == 'IMKPinching':
                          # matType: 'IMKPinching',
                ops.uniaxialMaterial('IMKPinching', MaterialTag, data['K0'], data['as_Pos'], data['as_Neg'], data['My_Pos'], data['My_Neg'], data['Fpr_Pos'], data['Fpr_Neg'],
                                    data['A_pinch'], data['Lamda_S'], data['Lamda_C'], data['Lamda_A'], data['Lamda_K'], data['c_S'],  data['c_C'], data['c_A'], data['c_K'],
                                    data['theta_p_Pos'], data['theta_p_Neg'], data['theta_pc_Pos'], data['theta_pc_Neg'], data['Res_Pos'], data['Res_Neg'], data['theta_u_Pos'],
                                    data['theta_u_Neg'], data['D_Pos'], data['D_Neg']) # Defining Material objects