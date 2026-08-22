import openseespy.opensees as ops
import opsvis as opsv
import matplotlib.pyplot as plt
from ._ops_material import _define_materials
from ._ops_section import _define_sections
from ._ops_node import _define_node
from ._ops_element import _define_element
from ._ops_restraint import _define_restraint
from ._ops_mass import _compute_and_define_mass

class AnalysisModel:
    def __init__(self, modeldata):
        self._modeldata = modeldata

    # HELPER METHOD
    def _initialise_model(self, ndim):
        # Create Model
        ops.wipe() # Wipe all constructed objects, i.e. all components of the model
        if ndim == 3:
                    # 'basic', '-ndm', ndm,  '-ndf', ndf
            ops.model('basic', '-ndm', ndim, '-ndf', 6) # Defining model dimensions and number of dofs
        else:
                    # 'basic', '-ndm', ndm,  '-ndf', ndf
            ops.model('basic', '-ndm', ndim, '-ndf', 3) # Defining model dimensions and number of dofs

    # MAIN METHOD
    def generate(self):
        ndim = self._modeldata.project_information.ndim # Retrieve number of dimensional space
        self._initialise_model(ndim=ndim) # Initialise model
        _define_materials(modeldata=self._modeldata) # Define materials
        _define_sections(ndim=ndim, modeldata=self._modeldata) # Define sections
        _define_node(modeldata=self._modeldata) # Define nodes
        _define_element(ndim=ndim, modeldata=self._modeldata) # Define elements
        _define_restraint(modeldata=self._modeldata) # Define restraint
        _compute_and_define_mass(modeldata=self._modeldata) # Compute Mass

    def plot_model(self):
        opsv.plot_model(node_labels=0, element_labels=0, fig_wi_he=(50,20), az_el=(-150,35), fig_lbrt=(0.05,0.05,0.95,0.95), local_axes=False,
                fmt_model={'color':'blue', 'linestyle':'solid', 'linewidth':1.2, 'marker':'.', 'markersize':6})
        plt.title('Undeformed Shape')
        plt.show()

        