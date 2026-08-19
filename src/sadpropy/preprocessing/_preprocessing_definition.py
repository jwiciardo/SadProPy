from .preprocessing_class_index import (
    MaterialType,
    MaterialModel,
    SectionShape,
    SectionModel,
    IntegrationType,
    ElementType,
    LoadCaseType,
)
from .material_class_index.concrete import ConcreteElastic, Concrete04, Concrete04MinMax
from .material_class_index.steel import SteelElastic, Steel02, Steel02MinMax
from .material_class_index.spring import SpringIMKBilinear, SpringIMKPeakOriented, SpringIMKPinching
from .section_class_index.rectangular import RectangularElastic, RectangularConcreteFiber

_material_type = {
    "Concrete": MaterialType.Concrete,
    "Rebar": MaterialType.Steel,
    "Steel": MaterialType.Steel,
    "Spring": MaterialType.Spring,
}
_material_model = {
    "Elastic": MaterialModel.Elastic,
    "Concrete04": MaterialModel.Concrete04,
    "Concrete04+MinMax": MaterialModel.Concrete04MinMax,
    "Steel02": MaterialModel.Steel02,
    "Steel02+MinMax": MaterialModel.Steel02MinMax,
    "IMKBilinear": MaterialModel.IMKBilinear,
    "IMKPeakOriented": MaterialModel.IMKPeakOriented,
    "IMKPinching": MaterialModel.IMKPinching,
}
_material_definition = {
    (MaterialType.Concrete, MaterialModel.Elastic): ConcreteElastic,
    (MaterialType.Concrete, MaterialModel.Concrete04): Concrete04,
    (MaterialType.Concrete, MaterialModel.Concrete04MinMax): Concrete04MinMax,
    (MaterialType.Steel, MaterialModel.Elastic): SteelElastic,
    (MaterialType.Steel, MaterialModel.Steel02): Steel02,
    (MaterialType.Steel, MaterialModel.Steel02MinMax): Steel02MinMax,
    (MaterialType.Spring, MaterialModel.IMKBilinear): SpringIMKBilinear,
    (MaterialType.Spring, MaterialModel.IMKPeakOriented): SpringIMKPeakOriented,
    (MaterialType.Spring, MaterialModel.IMKPinching): SpringIMKPinching,
}
_section_shape = {
    "Rectangular": SectionShape.Rectangular,
    "Circular": SectionShape.Circular,
    "Wide Flange": SectionShape.WideFlange,
    "Channel": SectionShape.Channel,
    "Rectangular Hollow": SectionShape.RectangularHollow,
    "Circular Hollow": SectionShape.CircularHollow,
}
_section_model = {
    "Elastic": SectionModel.Elastic,
    "Fiber": SectionModel.Fiber,
    "Aggregator": SectionModel.Aggregator,
}
_section_definition = {
    (MaterialType.Concrete, SectionShape.Rectangular, SectionModel.Elastic): RectangularElastic,
    (MaterialType.Steel, SectionShape.Rectangular, SectionModel.Elastic): RectangularElastic,
    (MaterialType.Concrete, SectionShape.Rectangular, SectionModel.Fiber): RectangularConcreteFiber,
}
_integration_type = {
    "Lobatto": IntegrationType.Lobatto,
    "Hinge Radau": IntegrationType.HingeRadau,
}
_element_type = {
    "Column": ElementType.Column,
    "Beam": ElementType.Beam,
    "Slab": ElementType.Slab,
    "Brace": ElementType.Brace,
    "Zero Length": ElementType.ZeroLength,
}
_loadcase_type = {
    "Selfweight": LoadCaseType.SW,
    "Dead": LoadCaseType.D,
    "Live": LoadCaseType.L,
    "Live Roof": LoadCaseType.Lr,
    "Earthquake-X": LoadCaseType.Ex,
    "Earthquake-Y": LoadCaseType.Ey,
    "Wind-X": LoadCaseType.Wx,
    "Wind-Y": LoadCaseType.Wy,
}