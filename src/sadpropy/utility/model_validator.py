import warnings
from model.dataclass_model_data import ModelData
    
class ModelValidator:

    # CENTRAL FUNCTION: TRANSLATOR
    def validate_model(self, modeldata: ModelData):
        self._validate_materials(modeldata)
        self._validate_mat_concrete04(modeldata)
        self._validate_mat_steel02(modeldata)
        self._validate_nodes(modeldata)
        self._validate_elements(modeldata)

    def _validate_materials(self, modeldata: ModelData):
        mats = modeldata.materials

        if len(mats) == 0:
            raise ValueError("No materials found")
        
        for mat in mats.values():
            if mat.type == "Concrete":
                if mat.fc == 0.0:
                    raise ValueError(f"Material {mat.name} has zero fc value")
                elif mat.E == 0.0:
                    raise ValueError(f"Material {mat.name} has zero E value")
                elif mat.nu == 0.0:
                    raise ValueError(f"Material {mat.name} has zero nu value")
                elif mat.G == 0.0:
                    raise ValueError(f"Material {mat.name} has zero G value")
                elif mat.unitweight == 0.0:
                    raise ValueError(f"Material {mat.name} has zero Unitweight value")
            elif mat.type == "Steel" or mat.type == "Rebar":
                if mat.fy == 0.0:
                    raise ValueError(f"Material {mat.name} has zero fy value")
                if mat.fu == 0.0:
                    raise ValueError(f"Material {mat.name} has zero fu value")
                elif mat.E == 0.0:
                    raise ValueError(f"Material {mat.name} has zero E value")
                elif mat.nu == 0.0:
                    raise ValueError(f"Material {mat.name} has zero nu value")
                elif mat.G == 0.0:
                    raise ValueError(f"Material {mat.name} has zero G value")
                elif mat.unitweight == 0.0:
                    raise ValueError(f"Material {mat.name} has zero Unitweight value")

    def _validate_mat_concrete04(self, modeldata: ModelData):
        mat_concrete04 = modeldata.mat_concrete04

        if len(mat_concrete04) == 0:
            raise ValueError("No materials found")
        
        for mat in mat_concrete04.values():
            if mat.base_mat is None:
                raise ValueError(f"Material {mat.name} has null base material")
            if mat.fc == 0.0:
                raise ValueError(f"Material {mat.name} has zero fc value")
            if mat.epsc == 0.0:
                raise ValueError(f"Material {mat.name} has zero epsc value")
            if mat.epscu == 0.0:
                raise ValueError(f"Material {mat.name} has zero epscu value")
            elif mat.E == 0.0:
                raise ValueError(f"Material {mat.name} has zero E value")
            if mat.fct == 0.0:
                raise ValueError(f"Material {mat.name} has zero fct value")
            if mat.beta == 0.0:
                raise ValueError(f"Material {mat.name} has zero beta value")

    def _validate_mat_steel02(self, modeldata: ModelData):
        mat_steel02 = modeldata.mat_steel02
        
        for mat in mat_steel02.values():
            if mat.base_mat is None:
                raise ValueError(f"Material {mat.name} has null base material")
            if mat.fy == 0.0:
                raise ValueError(f"Material {mat.name} has zero fy value")
            if mat.fu == 0.0:
                raise ValueError(f"Material {mat.name} has zero fu value")
            if mat.eu == 0.0:
                raise ValueError(f"Material {mat.name} has zero eu value")
            elif mat.E == 0.0:
                raise ValueError(f"Material {mat.name} has zero E value")
            if mat.R0 == 0.0:
                raise ValueError(f"Material {mat.name} has zero R0 value")
            if mat.cR1 == 0.0:
                raise ValueError(f"Material {mat.name} has zero cR1 value")
            if mat.cR2 == 0.0:
                raise ValueError(f"Material {mat.name} has zero cR2 value")

    def _validate_nodes(self, modeldata: ModelData):
        nodes = modeldata.nodes

        if len(nodes) == 0:
            raise ValueError("No nodes found")
        
        for node in nodes.values():
            if any(v is None for v in [node.x, node.y, node.z]):
                raise ValueError(f"Node {node.id} has null coordinates")
    
    def _validate_elements(self, modeldata: ModelData):
        elements = modeldata.elements
        nodes = modeldata.nodes

        if len(elements) == 0:
            raise ValueError("No elements found")

        for e in elements.values():
            if e.ni == e.nj:
                raise ValueError(f"Element {e.id} has zero length")

            if e.ni not in nodes:
                raise ValueError(f"Element {e.id} references missing node {e.ni}")

            if e.nj not in nodes:
                raise ValueError(f"Element {e.id} references missing node {e.nj}")
        
        ni = nodes[e.ni]
        nj = nodes[e.nj]
        ele_length = ((nj.x - ni.x)**2 + (nj.y - ni.y)**2 + (nj.z - ni.z)**2)**0.5
        if ele_length < 1e-9:
            warnings.warn(f"Element {e.id} is extremely short")
