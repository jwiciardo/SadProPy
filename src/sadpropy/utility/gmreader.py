import numpy as np
import matplotlib.pyplot as plt
import os

class GroundMotionReader:
    def __init__(self, home_path):
        self.home = home_path
    
    def _read_record(self):
        # GROUND MOTION RECORD
        event = 'N. PALM SPRINGS_RSN515'
        dt = 0.005
        dir_x = 'E'
        dir_y = 'N'
        acc_x = np.loadtxt(self.home + os.sep + 'GM' + os.sep + 'ORIGINAL' + os.sep + f'{dt}' + os.sep + f'Original_{event}_{dir_x}.txt')
        acc_y = np.loadtxt(self.home + os.sep + 'GM' + os.sep + 'ORIGINAL' + os.sep + f'{dt}' + os.sep + f'Original_{event}_{dir_y}.txt')
        N_acc = np.minimum(len(acc_x), len(acc_y))
        tFinal = N_acc * dt
        t_arr = np.arange(0.0, tFinal, dt)

        fig = plt.figure(figsize=(30,8))
        ax = fig.add_subplot(111)
        ax.plot(t_arr, acc_x, 'r--')
        return acc_x, acc_y, dt, N_acc