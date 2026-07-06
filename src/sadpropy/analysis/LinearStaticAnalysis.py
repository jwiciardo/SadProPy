import openseespy.opensees as ops
import pandas as pd
import numpy as np
from analysis.AnalysisEngine import AnalysisEngine
from utility.Operator import SignificantNumber
from utility.Units import UnitDatabase, UnitConverter

class LinearStaticAnalysis:
    def __init__(self, workspace):
        self.ws = workspace
        self.unitdb = UnitDatabase()
        self.unitconverter = UnitConverter(self.unitdb)
        self.analysis = AnalysisEngine(self.ws)

        # UNIT CONVERTER
        self.Length_mm = lambda x: self.unitconverter.from_SI(x, 'mm')
        self.Force_kN = lambda x: self.unitconverter.from_SI(x, 'kN')
        self.Moment_kNm = lambda x: self.unitconverter.from_SI(x, 'kN-m')

    def _perform_LinearStaticAnalysis(self, tol=1.0e-13, Maxiter=10, pFlag=1):
        """
        Input
        -----
        tol : float
            Tolerance criteria used to check for convergence.
        Maxiter : int
            Maximum iterations number to check.
        nSteps : int
            Number of step to be done by solver.
        pFlag : int (0 - 5)
            Print flag:
            0 : Print nothing
            1 : Print information on norms each time convergence test is invoked
            2 : Print information on norms and number of iterations at end of successful test
            4 : At each step, it will print the norms and also ΔU and R(U) vectors
            5 : If it fails to converge at the end of maximum iterations, it will print an error message but return a successful test

        Output
        -------
        BeamForces : dataframe
            Response of the elements: Beam Forces.
        ColForces : dataframe
            Response of the elements: Column Forces.
        NodalDisps : dataframe
            Response of the nodes: Node Displacements.
        
        Information
        -----------
            Author: Julian Wiciardo, Earthquake Engineering MSc Student
            Affiliation: Imperial College London
            e-mail: julian.wiciardo24@imperial.ac.uk
        """

        LoadOptions = self.ws.options['Load Options'] # Retrieving Load options
        SupportNodes = self.ws.model['Support Nodes']
        Selfweight_load = LoadOptions['Selfweight']
        SuperimposedDead_load = LoadOptions['Superimposed Dead Load']
        Live_load = LoadOptions['Live Load']
        RoofLive_load = LoadOptions['Roof Live Load']
        Gravity_load = LoadOptions['Gravity']

        # LOAD CASE TO BE SOLVED
        print(f'Load Case to be solved:')
        if Selfweight_load == 1 or Gravity_load == 1:
            print(f'Case: Selfweight')
        if SuperimposedDead_load == 1 or Gravity_load == 1:
            print(f'Case: Superimposed Dead Load')
        if Live_load == 1 or Gravity_load == 1:
            print(f'Case: Live Load')
        if RoofLive_load == 1 or Gravity_load == 1:
            print(f'Case: Roof Live Load')

        ops.wipeAnalysis() # Wiping any previous Analysis object
        
        # ANALYSIS OPTION
        ## Convergence Test
                    # testType, *testArgs
        ops.test('NormDispIncr', tol, Maxiter, pFlag) # Setting when convergence has been achieved
                    # algoType
        ops.algorithm('Newton', '-initial') # Setting the sequence of steps taken to solve the non-linear equation at the current time step
        # numbererType:'RCM'
        ops.numberer('RCM') # Setting the mapping between equation numbers and DOFs
                # systemType
        ops.system('UmfPack') # Setting how to store and solve the system of equations in the analysis
        # constraintType: 'Transformation'
        ops.constraints('Transformation') # Setting how the constraint equations are enforced in the analysis
                           # intType, incr
        ops.integrator('LoadControl', 1) # Setting the predictive step for time (t+dt)
        # analysisType: 'Static'
        ops.analysis('Static') # Creating Analysis objects
            
        # PERFORM ANALYSIS
                # numIncr
        ops.analyze(1) # Performing the Analysis
                    # '-time', pseudoTime
        ops.loadConst('-time', 0.0) # Setting the load constants and time

        # RETRIEVE ANALYSIS RESULTS
        BeamForces = self.analysis.compute_LinearBeamForce(nEvalPoints=17) # Retrieving Beam forces
        BeamForces_df = pd.DataFrame(BeamForces)
        ColForces = self.analysis.compute_LinearColumnForce(nEvalPoints=3) # Retrieving Column forces
        ColForces_df = pd.DataFrame(ColForces)
        NodalDisps = {}
        for NodeTag in ops.getNodeTags():
            Disps = np.array(ops.nodeDisp(NodeTag))
            NodalDisps[NodeTag] = Disps
        NodalDisps_df = pd.DataFrame([{'Node': key, 'Ux (mm)': SignificantNumber(self.Length_mm(Ux)), 'Uy (mm)': SignificantNumber(self.Length_mm(Uy)), 'Uz (mm)': SignificantNumber(self.Length_mm(Uz)),
                        'Rx (rad)': SignificantNumber(Rx), 'Ry (rad)': SignificantNumber(Ry), 'Rz (rad)': SignificantNumber(Rz)} for key, (Ux, Uy, Uz, Rx, Ry, Rz) in NodalDisps.items()
                        ]) # Creating Dataframe for Nodal displacements
        ops.reactions()
        BaseForce = np.zeros(3)
        BaseMoment = np.zeros(3)
        SupportReaction = {}
        for NodeTag in SupportNodes:
            Reaction = np.array(ops.nodeReaction(NodeTag))
            xCoord, yCoord, zCoord = ops.nodeCoord(NodeTag)
            FX, FY, FZ = Reaction[:3]
            BaseForce += [FX, FY, FZ]
            BaseMoment[0] += (yCoord * FZ) - (zCoord * FY)
            BaseMoment[1] += (zCoord * FX) - (xCoord * FZ)
            BaseMoment[2] += (xCoord * FY) - (yCoord * FX)
            SupportReaction[NodeTag] = Reaction
        BaseReaction = np.concatenate((BaseForce, BaseMoment))
        FX, FY, FZ, MX, MY, MZ = BaseReaction
        BaseReaction_df = pd.DataFrame([{'FX (kN)': SignificantNumber(self.Force_kN(FX)), 'FY (kN)': SignificantNumber(self.Force_kN(FY)), 'FZ (kN)': SignificantNumber(self.Force_kN(FZ)),
                        'MX (kNm)': SignificantNumber(self.Moment_kNm(MX)), 'MY (kNm)': SignificantNumber(self.Moment_kNm(MY)), 'MZ (kNm)': SignificantNumber(self.Moment_kNm(MZ))}
                        ]) # Creating Dataframe for Base reactions
        SupportReaction_df = pd.DataFrame([{'Node': key, 'FX (kN)': SignificantNumber(self.Force_kN(FX)), 'FY (kN)': SignificantNumber(self.Force_kN(FY)), 'FZ (kN)': SignificantNumber(self.Force_kN(FZ)),
                        'MX (kNm)': SignificantNumber(self.Moment_kNm(MX)), 'MY (kNm)': SignificantNumber(self.Moment_kNm(MY)), 'MZ (kNm)': SignificantNumber(self.Moment_kNm(MZ))}
                        for key, (FX, FY, FZ, MX, MY, MZ) in SupportReaction.items()]) # Creating Dataframe for Nodal reactions
        return BeamForces_df, ColForces_df, NodalDisps_df, BaseReaction_df, SupportReaction_df


    
