import numpy as np
from ..preprocessing_class_index import LoadType, LinearStaticParameters, ModalParameters, ResponseSpectrumParameters

class LinearStatic:
    parameters = LinearStaticParameters
    @staticmethod
    def translate(data, converter, load_types):
        scale_factor_columns = ["Param1", "Param2", "Param3", "Param4", "Param5", "Param6"]
        scale_factors = np.column_stack([
            np.asarray([
                value if value is not None else np.nan
                for value in data[column]
            ], dtype=np.float64)
            for column in scale_factor_columns
        ])
        return scale_factors

class Modal:
    parameters = ModalParameters
    @staticmethod
    def translate(data, converter, load_types):
        n_modes = np.asarray(data["Param1"], dtype=np.float64)
        return n_modes[:, None]

class ResponseSpectrum:
    parameters = ResponseSpectrumParameters
    @staticmethod
    def translate(data, converter, load_types):
        scale_factor_columns = ["Param1", "Param2", "Param3", "Param4", "Param5", "Param6"]
        scale_factors = np.column_stack([
            np.asarray([
                value if value is not None else np.nan
                for value in data[column]
            ], dtype=np.float64)
            for column in scale_factor_columns
        ])
        trans_accel_load_type_mask = (load_types == LoadType.AccelUX) | (load_types == LoadType.AccelUY) | (load_types == LoadType.AccelUZ)
        rot_accel_load_type_mask = (load_types == LoadType.AccelRX) | (load_types == LoadType.AccelRY) | (load_types == LoadType.AccelRZ)
        scale_factors[trans_accel_load_type_mask] = converter.acceleration(values=scale_factors[trans_accel_load_type_mask])
        scale_factors[rot_accel_load_type_mask] = converter.rotational_acceleration(values=scale_factors[rot_accel_load_type_mask])
        modal_damping = np.asarray(data["Param7"], dtype=np.float64)
        ecc_ratio = np.asarray(data["Param8"], dtype=np.float64)
        return np.column_stack((
            scale_factors,
            modal_damping,
            ecc_ratio,
        ))