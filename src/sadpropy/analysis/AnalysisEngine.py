import openseespy.opensees as ops
import numpy as np
from utility.Operator import SignificantNumber
from utility.Units import UnitDatabase, UnitConverter

class AnalysisEngine:
    def __init__(self, workspace):
        self.ws = workspace
        self.unitdb = UnitDatabase()
        self.unitconverter = UnitConverter(self.unitdb)

        # UNIT CONVERTER
        self.Length_mm = lambda x: self.unitconverter.from_SI(x, 'mm')
        self.Force_kN = lambda x: self.unitconverter.from_SI(x, 'kN')
        self.Moment_kNm = lambda x: self.unitconverter.from_SI(x, 'kN-m')

    def get_LoadData(self):
        # DEFINITION
        LoadData = {}
        beg_data_num = 0
        end_data_num = 0
        Beam3dUniformLoad = 5
        Beam3dUniformLoad_ndata = 3
        Beam3dPointLoad = 6
        Beam3dPointLoad_ndata = 4
        element_load_tags = ops.getEleLoadTags()
        element_load_types = ops.getEleLoadClassTags()
        element_load_data = ops.getEleLoadData()

        for element_load_tag in element_load_tags:
            LoadData[element_load_tag] = []

        for element_load_type, element_load_tag in zip(element_load_types, element_load_tags):

            # -beamUniform
            if element_load_type == Beam3dUniformLoad:
                end_data_num = beg_data_num + Beam3dUniformLoad_ndata
                ele_load_data = element_load_data[beg_data_num:end_data_num]
                beg_data_num = end_data_num
                wy, wz, wx = ele_load_data
                LoadData[element_load_tag].append(['-beamUniform', wy, wz, wx])
            # -beamPoint
            elif element_load_type == Beam3dPointLoad:
                end_data_num = beg_data_num + Beam3dPointLoad_ndata
                ele_load_data = element_load_data[beg_data_num:end_data_num]
                beg_data_num = end_data_num
                Py, Pz, Px, aL = ele_load_data
                LoadData[element_load_tag].append(['-beamPoint', Py, Pz, aL, Px])
            else:
                print(f'\nWarning! element_load_type:\n{element_load_type} - Unknown element load Error')
        return LoadData

    def compute_LinearBeamForce(self, nEvalPoints=17):
        # DEFINITION
        ElementBeamX_dict = self.ws.elementsbeamx # Dictionary of elements beam X data
        ElementBeamY_dict = self.ws.elementsbeamy # Dictionary of elements beam Y data
        ElementBeam_dict = ElementBeamX_dict | ElementBeamY_dict
        Beam_ElementTags = list(ElementBeam_dict)
        LoadData = self.get_LoadData()
        ElasticBeam3d = 5
        ForceBeamColumn3d = 74
        DispBeamColumn3d = 64
        truss = 12
        trussSection = 13
        TimoshenkoBeamColumn3d = 631
        ElasticTimoshenkoBeam3d = 146

        forces_data = []
        for i, ElementTag in enumerate(Beam_ElementTags):
            element_class_tag = ops.getEleClassTags(ElementTag)[0]
            element_node_tags = ops.eleNodes(ElementTag)
            element_coord = np.zeros((2, 3))
            for i, element_node_tag in enumerate(element_node_tags):
                element_coord[i, :] = ops.nodeCoord(element_node_tag)
            
            if (element_class_tag == ElasticBeam3d
                or element_class_tag == ForceBeamColumn3d
                or element_class_tag == DispBeamColumn3d
                or element_class_tag in [truss, trussSection]
                or element_class_tag == TimoshenkoBeamColumn3d
                or element_class_tag == ElasticTimoshenkoBeam3d):

                # Rigid Offset
                element_offsets = np.array(ops.eleResponse(ElementTag, 'offsets'))
                nz_offsets = np.nonzero(element_offsets)[0]  # Tuple of arrays
                if np.any(nz_offsets):
                    element_coord[:, 0] += element_offsets[[0, 3]] # X
                    element_coord[:, 1] += element_offsets[[1, 4]] # Y
                    element_coord[:, 2] += element_offsets[[2, 5]] # Z
                else:
                    pass

                Lxyz = element_coord[1, :] - element_coord[0, :]
                L = np.sqrt(Lxyz @ Lxyz)

                element_load_data = [['-beamUniform', 0., 0., 0.]] # Default element load data
                if ElementTag in LoadData:
                    element_load_data = LoadData[ElementTag]
                    
                element_nodal_forces = ops.eleResponse(ElementTag, 'localForces')
                n_nodal_forces = len(element_nodal_forces)
                xl = np.linspace(0., L, nEvalPoints) # X coordinate of Evaluation points along the element

                for element_load_data_i in element_load_data:
                    element_load_type = element_load_data_i[0]
                    if n_nodal_forces == 1:
                        Pi = element_nodal_forces[0]
                    elif n_nodal_forces == 12:
                        Pi, Vyi, Vzi, Ti, Myi, Mzi = element_nodal_forces[:6]
                    else:
                        print(f'\nWarning! Not supported. Number of nodal forces: {n_nodal_forces}')
                        
                    if element_load_type == '-beamUniform':
                        n_elementLoadData = len(element_load_data_i)
                        if n_elementLoadData == 4:
                            pass
                    elif element_load_type == '-beamPoint':
                        Py, Pz, aL, Px = element_load_data_i[1:5]
                        a = aL * L
                        if np.any(np.isclose(xl, a)):
                            pass
                        else:
                            xl = np.insert(xl, xl.searchsorted(a), a)
                            nEvalPoints = len(xl)
                    
                one = np.ones(nEvalPoints)
                P = -Pi * one # Axial force
                if n_nodal_forces == 12:
                    Vy = -Vyi * one # Shear force along local Y
                    Vz = -Vzi * one # Shear force along local Z
                    T = -Ti * one # Torsion
                    Mz = -Mzi * one + Vyi * xl # Bending moment about local Z
                    My = Myi * one + Vzi * xl # Bending moment about local Y
                elif n_nodal_forces == 1:
                    nEvalPoints = 7  # Evaluation points for truss only
                    Mz = My = Vy = Vz = np.zeros(nEvalPoints)
                forces = np.column_stack((P, Vy, Vz, T, My, Mz))

                for element_load_data_i in element_load_data:
                    element_load_type = element_load_data_i[0]
                    if element_load_type == '-beamUniform':
                        n_elementLoadData = len(element_load_data_i)
                        if n_elementLoadData == 4:
                            Wy, Wz, Wx = element_load_data_i[1:4]
                            P = -Wx * xl
                            if n_nodal_forces == 12:
                                Vy = -Wy * xl
                                Vz = -Wz * xl
                                T = np.zeros_like(one)
                                Mz = 0.5 * Wy * xl**2
                                My = 0.5 * Wz * xl**2
                                forces += np.column_stack((P, Vy, Vz, T, My, Mz))
                            elif n_nodal_forces == 1:
                                forces += np.column_stack((P))
                    elif element_load_type == '-beamPoint':
                        Py, Pz, aL, Px = element_load_data_i[1:5]
                        a = aL * L
                        indx = 0
                        for x in np.nditer(xl):
                            if x <= a:
                                pass
                            elif x > a:
                                forces[indx, 0] += -Px
                                forces[indx, 1] += -Py
                                forces[indx, 2] += -Pz
                                forces[indx, 4] += Pz * (x - a)
                                forces[indx, 5] += Py * (x - a)
                            indx += 1
                for i in range(len(xl)):
                    forces_data.append({
                        'Element': ElementTag,
                        'Location (m)': xl[i],
                        'P (kN)': SignificantNumber(self.Force_kN(forces[i, 0])),
                        'Vy (kN)': SignificantNumber(self.Force_kN(forces[i, 1])),
                        'Vz (kN)': SignificantNumber(self.Force_kN(forces[i, 2])),
                        'T (kNm)': SignificantNumber(self.Moment_kNm(forces[i, 3])),
                        'My (kNm)': SignificantNumber(self.Moment_kNm(forces[i, 4])),
                        'Mz (kNm)': SignificantNumber(self.Moment_kNm(forces[i, 5]))
                    })
        return forces_data

    def compute_LinearColumnForce(self, nEvalPoints=3):
        # DEFINITION
        ElementCol_dict = self.ws.elementscol # Dictionary of elements column data
        Col_ElementTags = list(ElementCol_dict)
        LoadData = self.get_LoadData()
        ElasticBeam3d = 5
        ForceBeamColumn3d = 74
        DispBeamColumn3d = 64
        truss = 12
        trussSection = 13
        TimoshenkoBeamColumn3d = 631
        ElasticTimoshenkoBeam3d = 146

        forces_data = []
        for i, ElementTag in enumerate(Col_ElementTags):
            element_class_tag = ops.getEleClassTags(ElementTag)[0]
            element_node_tags = ops.eleNodes(ElementTag)
            element_coord = np.zeros((2, 3))
            for i, element_node_tag in enumerate(element_node_tags):
                element_coord[i, :] = ops.nodeCoord(element_node_tag)
            
            if (element_class_tag == ElasticBeam3d
                or element_class_tag == ForceBeamColumn3d
                or element_class_tag == DispBeamColumn3d
                or element_class_tag in [truss, trussSection]
                or element_class_tag == TimoshenkoBeamColumn3d
                or element_class_tag == ElasticTimoshenkoBeam3d):

                # Rigid Offset
                element_offsets = np.array(ops.eleResponse(ElementTag, 'offsets'))
                nz_offsets = np.nonzero(element_offsets)[0]  # Tuple of arrays
                if np.any(nz_offsets):
                    element_coord[:, 0] += element_offsets[[0, 3]] # X
                    element_coord[:, 1] += element_offsets[[1, 4]] # Y
                    element_coord[:, 2] += element_offsets[[2, 5]] # Z
                else:
                    pass

                Lxyz = element_coord[1, :] - element_coord[0, :]
                L = np.sqrt(Lxyz @ Lxyz)

                element_load_data = [['-beamUniform', 0., 0., 0.]] # Default element load data
                if ElementTag in LoadData:
                    element_load_data = LoadData[ElementTag]
                    
                element_nodal_forces = ops.eleResponse(ElementTag, 'localForces')
                n_nodal_forces = len(element_nodal_forces)
                xl = np.linspace(0., L, nEvalPoints) # X coordinate of Evaluation points along the element

                for element_load_data_i in element_load_data:
                    element_load_type = element_load_data_i[0]
                    if n_nodal_forces == 1:
                        Pi = element_nodal_forces[0]
                    elif n_nodal_forces == 12:
                        Pi, Vyi, Vzi, Ti, Myi, Mzi = element_nodal_forces[:6]
                    else:
                        print(f'\nWarning! Not supported. Number of nodal forces: {n_nodal_forces}')
                        
                    if element_load_type == '-beamUniform':
                        n_elementLoadData = len(element_load_data_i)
                        if n_elementLoadData == 4:
                            pass
                    elif element_load_type == '-beamPoint':
                        Py, Pz, aL, Px = element_load_data_i[1:5]
                        a = aL * L
                        if np.any(np.isclose(xl, a)):
                            pass
                        else:
                            xl = np.insert(xl, xl.searchsorted(a), a)
                            nEvalPoints = len(xl)
                    
                one = np.ones(nEvalPoints)
                P = -Pi * one # Axial force
                if n_nodal_forces == 12:
                    Vy = -Vyi * one # Shear force along local Y
                    Vz = -Vzi * one # Shear force along local Z
                    T = -Ti * one # Torsion
                    Mz = -Mzi * one + Vyi * xl # Bending moment about local Z
                    My = Myi * one + Vzi * xl # Bending moment about local Y
                elif n_nodal_forces == 1:
                    nEvalPoints = 7  # Evaluation points for truss only
                    Mz = My = Vy = Vz = np.zeros(nEvalPoints)
                forces = np.column_stack((P, Vy, Vz, T, My, Mz))

                for element_load_data_i in element_load_data:
                    element_load_type = element_load_data_i[0]
                    if element_load_type == '-beamUniform':
                        n_elementLoadData = len(element_load_data_i)
                        if n_elementLoadData == 4:
                            Wy, Wz, Wx = element_load_data_i[1:4]
                            P = -Wx * xl
                            if n_nodal_forces == 12:
                                Vy = -Wy * xl
                                Vz = -Wz * xl
                                T = np.zeros_like(one)
                                Mz = 0.5 * Wy * xl**2
                                My = 0.5 * Wz * xl**2
                                forces += np.column_stack((P, Vy, Vz, T, My, Mz))
                            elif n_nodal_forces == 1:
                                forces += np.column_stack((P))
                    elif element_load_type == '-beamPoint':
                        Py, Pz, aL, Px = element_load_data_i[1:5]
                        a = aL * L
                        indx = 0
                        for x in np.nditer(xl):
                            if x <= a:
                                pass
                            elif x > a:
                                forces[indx, 0] += -Px
                                forces[indx, 1] += -Py
                                forces[indx, 2] += -Pz
                                forces[indx, 4] += Pz * (x - a)
                                forces[indx, 5] += Py * (x - a)
                            indx += 1
                for i in range(len(xl)):
                    forces_data.append({
                        'Element': ElementTag,
                        'Location (m)': xl[i],
                        'P (kN)': SignificantNumber(self.Force_kN(forces[i, 0])),
                        'Vy (kN)': SignificantNumber(self.Force_kN(forces[i, 1])),
                        'Vz (kN)': SignificantNumber(self.Force_kN(forces[i, 2])),
                        'T (kNm)': SignificantNumber(self.Moment_kNm(forces[i, 3])),
                        'My (kNm)': SignificantNumber(self.Moment_kNm(forces[i, 4])),
                        'Mz (kNm)': SignificantNumber(self.Moment_kNm(forces[i, 5]))
                    })
        return forces_data