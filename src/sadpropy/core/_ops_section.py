import openseespy.opensees as ops
import numpy as np
import opsvis as opsv
import matplotlib.pyplot as plt
import os
from ._ops_fiber_section import _generate_rectangular_concrete_fiber_division
from ..preprocessing.preprocessing_class_index import SectionModel, SectionProperties
from ..preprocessing._preprocessing_definition import _section_definition, _section_fiber

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
    sec_dims = sections.dimensions
    sec_props = sections.properties

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
                print(mat_props[mat_idx, mat_def[i].properties])
                ops.section(
                    'Fiber',
                    int(sec_tag[i]), # secTag
                    '-GJ',
                    float(mat_props[mat_idx, mat_def[i].properties.G] * sec_props[i, SectionProperties.Jxx]), # GJ
                )
                _generate_rectangular_concrete_fiber_division(section_tag=int(sec_tag[i]), materials_tag=sec_mats_tag[i], dimensions=sec_dims[i], properties=sec_props[i])
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