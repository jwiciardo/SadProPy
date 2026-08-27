import openseespy.opensees as ops
import opsvis as opsv
import matplotlib.pyplot as plt
from ._ops_material import _define_materials
from ._ops_section import _define_sections
from ._ops_node import _define_nodes
from ._ops_element import _define_elements
from ._ops_restraint import _assign_restraints
from ._ops_mass import _compute_and_define_masses
from ._ops_diaphragm import _assign_diaphragms
from ._ops_load import _assign_loads

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
        _define_nodes(modeldata=self._modeldata) # Define nodes
        _define_elements(ndim=ndim, modeldata=self._modeldata) # Define elements
        _assign_restraints(modeldata=self._modeldata) # Define restraints
        applied_nodal_mass = _compute_and_define_masses(modeldata=self._modeldata) # Compute Masses
        _assign_diaphragms(modeldata=self._modeldata) # Define diaphragms
        _assign_loads(modeldata=self._modeldata) # Define loads

    def plot_model(self):
        opsv.plot_model(node_labels=0, element_labels=0, fig_wi_he=(50,20), az_el=(-150,35), fig_lbrt=(0.05,0.05,0.95,0.95), local_axes=False,
                fmt_model={'color':'blue', 'linestyle':'solid', 'linewidth':1.2, 'marker':'.', 'markersize':6})
        plt.title('Undeformed Shape')
        plt.show()

        