import openseespy.opensees as ops
import numpy as np
import matplotlib.pyplot as plt

def _plot_material(title, matTag, ec, et):
    ops.testUniaxialMaterial(matTag)
    strain_comp = np.linspace(0, ec, 150)
    stress_comp = []
    for eps in strain_comp:
        ops.setStrain(eps)
        stress_comp.append(ops.getStress())

    ops.testUniaxialMaterial(matTag)
    strain_ten = np.linspace(0, et, 150)
    stress_ten = []
    for eps in strain_ten:
        ops.setStrain(eps)
        stress_ten.append(ops.getStress())

    # Plot
    plt.plot(strain_comp, stress_comp, label='Compression', color="tab:red")
    plt.plot(strain_ten, stress_ten, label='Tension', color="tab:cyan")
    plt.xlabel('Strain')
    plt.ylabel('Stress')
    plt.title(title)
    plt.gca().invert_yaxis()
    plt.gca().invert_xaxis()
    plt.axhline(0)
    plt.axvline(0)
    plt.grid()
    plt.show()