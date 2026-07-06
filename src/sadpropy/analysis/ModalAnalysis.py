import openseespy.opensees as ops
import pandas as pd
import numpy as np
import os
from utility.Operator import SignificantNumber

class ModalAnalysis:
    def __init__(self, workspace):
        self.ws = workspace

    def perform_ModalAnalysis(self, nEigenModes):
        output_path = self.ws.file['Output Path']
                    #numEigenvalues
        Lambda = ops.eigen(nEigenModes) # Performing Eigenvalue Analysis (Modal Analysis)
        ModalPeriods = [] # Predefined Modal periods and frequencies list
        for mode in range(nEigenModes):
            Omega = np.sqrt(Lambda[mode])
            T = 2 * np.pi / Omega
            f = Omega / (2 * np.pi)
            ModalPeriods.append({
                'Mode': mode+1,
                'Period (s)': SignificantNumber(T),
                'Frequency (cyc/s)': SignificantNumber(f),
                'Circular Frequency (rad/s)': SignificantNumber(Omega),
                'Eigenvalue (rad2/s2)': SignificantNumber(Lambda[mode])
            }) # Appending Modal periods and frequencies data to Modal periods and frequencies list
            print(f'Mode {mode+1:>2} of {nEigenModes:<2}:     λ = {Lambda[mode]:>9.3e} rad2/s2,     f = {f:>6.3f} cyc/s,     T = {T:>6.3f} s')
        ModalPeriods_df = pd.DataFrame(ModalPeriods) # Creating Dataframe for Modal periods and frequencies data
                        # '-print', '-file', reportFileName,                                   '-unorm'
        ops.modalProperties('-print', '-file', output_path + os.sep + 'ModalAnalysisReport.txt', '-unorm') # Computing modal properties after eigenvalue analysis is performed
        return ModalPeriods_df