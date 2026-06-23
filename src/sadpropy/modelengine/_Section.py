import openseespy.opensees as ops
import opsvis as opsv
import matplotlib.pyplot as plt
import os

class SectionProperties:
    def __init__(self, workspace):
        self.ws = workspace
        self.tag = self.ws.tag_manager
    
    def define(self):
        FrameSections_dict = self.ws.framesections
        Materials_dict = self.ws.materials
        for SectionName, data in FrameSections_dict.items():
            SectionTag = self.tag.add('Section', f"{SectionName}")
            Mat = Materials_dict[data['Base Material']]
            E = Mat['E'] # Modulus of elasticity of section
            G = Mat['G'] # Shear modulus of section
             # secType: 'Elastic', secTag,     E_mod, A,                       Iz,                        Iy,                        G_mod, Jx,                          alphaY,         alphaZ
            ops.section('Elastic', SectionTag, E,     data['k_A'] * data['A'], data['k_Iz'] * data['Iz'], data['k_Iy'] * data['Iy'], G,     data['k_Jxx'] * data['Jxx'], data['alphaY'], data['alphaZ']) # Defining Section objects
            
        Sec_Fiber_dict = self.ws.sec_fiber
        for SectionName, data in Sec_Fiber_dict.items():
            SectionTag = self.tag.add('Section', f"{SectionName}")
            Mat = Materials_dict[data['Base Material']]
            if data['Section Shape'] == 'Rectangular':
                Mat_coverTag = self.tag.get_tag('Material', f"{data['Material 1']}")
                Mat_coreTag = self.tag.get_tag('Material', f"{data['Material 2']}")
                Mat_rebarTag = self.tag.get_tag('Material', f"{data['Material 3']}")

                G = Mat['G'] # Shear modulus of section
                Jxx = data['Jxx'] # Torsional constant of section

                d_prime = data['cover'] + data['barDiaHoop'] + data['barDiaTop'] / 2.0 # cover to centroid of longitudinal reinforcements
                yCentroid, zCentroid = 0.0, 0.0 # Local axis coordinate of section centroid
                yCover, zCover = yCentroid + data['h'] / 2.0, zCentroid + data['b'] / 2.0 # Local axis coordinate of cover edge from centroid
                yCore, zCore = yCentroid + yCover - d_prime, zCentroid + zCover - d_prime # Local axis coordinate of core edge from centroid
                nBarsTop = data['nBarsTop']
                nBarsBot = data['nBarsBot']
                nBarsInt = data['nBarsInt']
                nBarsSide = int(nBarsInt / 2)
                AbarTop = data['barAreaTop']
                AbarBot = data['barAreaBot']
                AbarInt = data['barAreaInt']
                nMeshYCore = 15 # Number of mesh along local y-axis of core
                nMeshZCore = 15 # Number of mesh along local z-axis of core
                nMeshYCover = 15 # Number of mesh along local y-axis of cover
                nMeshZCover = 15 # Number of mesh along local z-axis of cover
                yStartInt = -yCore + (data['h'] - 2 * d_prime) / (nBarsSide + 1) # Local y-axis coordinate of intermediate bars at start
                yEndInt = yCore - (data['h'] - 2 * d_prime) / (nBarsSide + 1) # Local y-axis coordinate of intermediate bars at end

                 # secType: 'Fiber', secTag,     '-GJ', GJ
                ops.section('Fiber', SectionTag, '-GJ', G * Jxx) # Defining Section objects
                  # type: 'quad', matTag,       numSubdivIJ, numSubdivJK, *crdsI (y, z),     *crdsJ (y, z),      *crdsK (y, z),       *crdsL (y, z)
                ops.patch('quad', Mat_coreTag,  nMeshYCore,  nMeshZCore,  *(yCore, zCore),   *(-yCore, zCore),   *(-yCore, -zCore),   *(yCore, -zCore)) # Defining Patch object: core
                ops.patch('quad', Mat_coverTag, 2,           nMeshZCover, *(yCover, zCover), *(yCore, zCore),    *(yCore, -zCore),    *(yCover, -zCover)) # Defining Patch object: top cover
                ops.patch('quad', Mat_coverTag, nMeshYCover, 2,           *(yCover, zCover), *(-yCover, zCover), *(-yCore, zCore),    *(yCore, zCore)) # Defining Patch object: left cover
                ops.patch('quad', Mat_coverTag, 2,           nMeshZCover, *(-yCore, zCore),  *(-yCover, zCover), *(-yCover, -zCover), *(-yCore, -zCore)) # Defining Patch object: bottom cover
                ops.patch('quad', Mat_coverTag, nMeshYCover, 2,           *(yCore, -zCore),  *(-yCore, -zCore),  *(-yCover, -zCover), *(yCover, -zCover)) # Defining Patch object: right cover
                  # type: 'straight', matTag,       numFiber, areaFiber, *start (y, z),        *end (y, z)
                ops.layer('straight', Mat_rebarTag, nBarsTop, AbarTop,   *(yCore, zCore),      *(yCore, -zCore)) # Defining Layer object: top reinforcements
                ops.layer('straight', Mat_rebarTag, nBarsInt, AbarInt,   *(yStartInt, zCore),  *(yEndInt, zCore)) # Defining Layer object: left reinforcements
                ops.layer('straight', Mat_rebarTag, nBarsBot, AbarBot,   *(-yCore, zCore),     *(-yCore, -zCore)) # Defining Layer object: bottom reinforcements
                ops.layer('straight', Mat_rebarTag, nBarsInt, AbarInt,   *(yStartInt, -zCore), *(yEndInt, -zCore)) # Defining Layer object: right reinforcements

                # Plot the fiber section data
                fiber_sec = [['section', 'Fiber', SectionTag],
                            ['patch', 'quad', Mat_coreTag,  nMeshYCore,  nMeshZCore,  yCore, zCore,   -yCore, zCore,   -yCore, -zCore,   yCore, -zCore],
                            ['patch', 'quad', Mat_coverTag, 2,           nMeshZCover, yCover, zCover, yCore, zCore,    yCore, -zCore,    yCover, -zCover],
                            ['patch', 'quad', Mat_coverTag, nMeshYCover, 2,           yCover, zCover, -yCover, zCover, -yCore, zCore,    yCore, zCore],
                            ['patch', 'quad', Mat_coverTag, 2,           nMeshZCover, -yCore, zCore,  -yCover, zCover, -yCover, -zCover, -yCore, -zCore],
                            ['patch', 'quad', Mat_coverTag, nMeshYCover, 2,           yCore, -zCore,  -yCore, -zCore,  -yCover, -zCover, yCover, -zCover],
                            ['layer', 'straight', Mat_rebarTag, nBarsTop, AbarTop, yCore, zCore,      yCore, -zCore],
                            ['layer', 'straight', Mat_rebarTag, nBarsInt, AbarInt, yStartInt, zCore,  yEndInt, zCore],
                            ['layer', 'straight', Mat_rebarTag, nBarsBot, AbarBot, -yCore, zCore,     -yCore, -zCore],
                            ['layer', 'straight', Mat_rebarTag, nBarsInt, AbarInt, yStartInt, -zCore, yEndInt, -zCore]
                            ]

                matcolor = ['r', 'lightgrey', 'gold', 'w', 'w', 'w']
                opsv.plot_fiber_section(fiber_sec, matcolor=matcolor)
                plt.title('Section ID:%d' %SectionTag)
                plt.axis('equal')
                plt.savefig(f'{self.ws.file['Output Path'] + os.sep + f'fiber_sec_{SectionTag}.png'}')
                plt.close()
            
            if data['Integration Type'] == 'Lobatto':
                IntegrationTag = self.tag.add('Integration', f"{SectionName}")
                SectionTag = self.tag.get_tag('Section', f"{SectionName}")
                Nip = 5 # Number of integration point
                            # type: 'Lobatto', tag,            secTag,     N
                ops.beamIntegration('Lobatto', IntegrationTag, SectionTag, Nip) # Defining integration method
        
        Sec_Aggregator_dict = self.ws.sec_aggregator
        for SectionName, data in Sec_Aggregator_dict.items():
            if data['Aggregator Type'] in FrameSections_dict:
                BaseSection = FrameSections_dict[data['Aggregator Type']]
            elif data['Aggregator Type'] in Sec_Fiber_dict:
                BaseSection = FrameSections_dict[Sec_Fiber_dict['Aggregator Type']['Base Section']]
            
            SectionTag = self.tag.add('Section', f"{SectionName}")
            Mat = Materials_dict[data['Base Material']]
            if data['Aggregator Type'] == 'Aggregator:Flexural Stiffness':
                AggregatedSectionTag = self.tag.get_tag('Section', f"{data['Aggregated Section']}")
                MaterialTagMz = self.tag.add('Material', f"{data['Aggregator Type']}_{SectionName}_Mz")
                MaterialTagMy = self.tag.add('Material', f"{data['Aggregator Type']}_{SectionName}_My")

                E = Mat['E'] # Modulus of elasticity of section
                Iz = BaseSection['Iz'] # Second moment of area of section about local z axis
                Iy = BaseSection['Iy'] # Second moment of area of section about local y axis

                          # matType: 'Elastic', matTag,        E
                ops.uniaxialMaterial('Elastic', MaterialTagMz, E * Iz) # Defining Material objects
                ops.uniaxialMaterial('Elastic', MaterialTagMy, E * Iy) # Defining Material objects
                 # secType: 'Aggregator', secTag,     *mats (matTag, dof),                         '-section', sectionTag
                ops.section('Aggregator', SectionTag, *(MaterialTagMz, 'Mz', MaterialTagMy, 'My'), '-section', AggregatedSectionTag) # Defining Section aggregator object
            elif data['Aggregator Type'] == 'Aggregator:Axial Stiffness':
                AggregatedSectionTag = self.tag.get_tag('Section', f"{data['Aggregated Section']}")
                MaterialTagP = self.tag.add('Material', f"{data['Aggregator Type']}_{SectionName}_P")
                
                E = Mat['E'] # Modulus of elasticity of section
                A = BaseSection['A'] # Area of section

                          # matType: 'Elastic', matTag,      E
                ops.uniaxialMaterial('Elastic', MaterialTagP, E * A) # Defining Material objects
                 # secType: 'Aggregator', secTag,     *mats (matTag, dof), '-section', sectionTag
                ops.section('Aggregator', SectionTag, *(MaterialTagP, 'P'), '-section', AggregatedSectionTag) # Defining Section aggregator object
            elif data['Aggregator Type'] == 'Aggregator:Shear Stiffness':
                AggregatedSectionTag = self.tag.get_tag('Section', f"{data['Aggregated Section']}")
                MaterialTagVy = self.tag.add('Material', f"{data['Aggregator Type']}_{SectionName}_Vy")
                MaterialTagVz = self.tag.add('Material', f"{data['Aggregator Type']}_{SectionName}_Vz")

                G = Mat['G'] # Shear modulus of section
                Avy = BaseSection['Avy'] # Shear area of section along local y axis
                Avz = BaseSection['Avz'] # Shear area of section along local z axis

                          # matType: 'Elastic', matTag,        E
                ops.uniaxialMaterial('Elastic', MaterialTagVy, G * Avy) # Defining Material objects
                ops.uniaxialMaterial('Elastic', MaterialTagVz, G * Avz) # Defining Material objects
                 # secType: 'Aggregator', secTag,     *mats (matTag, dof),                         '-section', sectionTag
                ops.section('Aggregator', SectionTag, *(MaterialTagVy, 'Vy', MaterialTagVz, 'Vz'), '-section', AggregatedSectionTag) # Defining Section aggregator object
            elif data['Aggregator Type'] == 'Aggregator:Torsional Stiffness':
                AggregatedSectionTag = self.tag.get_tag('Section', f"{data['Aggregated Section']}")
                MaterialTagT = self.tag.add('Material', f"{data['Aggregator Type']}_{SectionName}_T")

                G = Mat['G'] # Shear modulus of section
                Jxx = BaseSection['Jxx'] # Torsional constant

                          # matType: 'Elastic', matTag,      E
                ops.uniaxialMaterial('Elastic', MaterialTagT, G * Jxx) # Defining Material objects
                 # secType: 'Aggregator', secTag,     *mats (matTag, dof), '-section', sectionTag
                ops.section('Aggregator', SectionTag, *(MaterialTagT, 'T'),  '-section', AggregatedSectionTag) # Defining Section aggregator object