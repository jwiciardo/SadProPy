import openseespy.opensees as ops
import numpy as np
from .postprocessing_class_index import (
    OpenseesLoadType,
)
from .postprocessing_dictionary import element_load_dict
from .postprocessing_dataclass import (
    ElementLoadData,
    ElementForceData,
    OutputData,
)
from ..preprocessing.preprocessing_class_index import ConnectionEnd
from ..utility.exception import ValidationError

class OutputStorer:
    def __init__(self, modeldata):
        self._modeldata = modeldata
        
    def _get_element_load_data(self):
        element_tag = np.asarray(ops.getEleLoadTags(), dtype=np.int32) # Retrieve element tag subjected to elemental load for all load cases
        element_load_class_tag = np.asarray(ops.getEleLoadClassTags(), dtype=np.int32) # Retrieve element load class tag for all load cases
        element_loads = np.asarray(ops.getEleLoadData(), dtype=np.float64) # Retrieve element loads for all load cases
        n = len(element_tag)
        element_load_type = np.empty(n, dtype=np.int8)
        element_load_values = np.full((n, 8), np.nan, dtype=np.float64)

        idx = 0
        for i, class_tag in enumerate(element_load_class_tag):
            load_type, ndata = element_load_dict[class_tag]
            element_load_type[i] = load_type
            element_load_values[i, :ndata] = (
                element_loads[idx:idx+ndata]
            )
            idx += ndata
        element_load_data = ElementLoadData (
            element_tag=element_tag,
            type_=element_load_type,
            values=element_load_values,
        ) # Store element load data to dataclass
        return element_load_data

    def _generate_evaluation_points(self, start_point, end_point, Length, ep_type, value):
        n = len(Length)
        nep_mask = ep_type == "-nEvaluationPoints"
        maxspacing_mask = ep_type == "-maxSpacing"
        if np.any(value[nep_mask] < 2.0):
            raise ValidationError("Number of evaluation points must be at least 2")
        if np.any(value[maxspacing_mask] <= 0.0):
            raise ValidationError("Maximum spacing must be greater than 0.0")

        nep = np.empty(n, dtype=np.int32)
        nep[nep_mask] = value[nep_mask].astype(np.int32)
        nep[maxspacing_mask] = (np.ceil((end_point[maxspacing_mask] - start_point[maxspacing_mask]) / value[maxspacing_mask]).astype(np.int32) + 1)

        add_iend = start_point > 0.0 
        add_jend = end_point < Length
        n_points = (nep + add_iend.astype(np.int32) + add_jend.astype(np.int32))
        max_points = np.max(n_points)

        evaluation_points = np.full((n, max_points), np.nan, dtype=np.float64)
        step = ((end_point - start_point) / (nep - 1))
        max_nep = np.max(nep)
        point_idx = np.arange(max_nep)
        generated_points = (start_point[:, None] + step[:, None] * point_idx[None, :])
        valid_points = (point_idx[None, :] < nep[:, None])
        generated_points = np.where(valid_points, generated_points, np.nan)
        generated_points = np.round(generated_points, 10)

        row_idx = np.arange(n)
        offset = add_iend.astype(np.int32)
        evaluation_points[add_iend, 0] = 0.0
        for j in range(max_nep):
            valid = j < nep
            evaluation_points[row_idx[valid], offset[valid] + j] = generated_points[valid, j]
        evaluation_points[row_idx[add_jend], offset[add_jend] + nep[add_jend]] = Length[add_jend]
        return evaluation_points

    def _trim_force_distribution(self, evaluation_points, start_point, end_point, force_arrays):
        valid = ((evaluation_points >= start_point[:, None]) & (evaluation_points <= end_point[:, None]))
        npoints = np.sum( valid, axis=1)
        max_npoints = np.max(npoints)
        n_elements = len(evaluation_points)

        trimmed_points = np.full((n_elements, max_npoints), np.nan, dtype=np.float64)
        trimmed_forces = [np.full(
            (n_elements, max_npoints),
            np.nan,
            dtype=np.float64,
            ) for _ in force_arrays
        ]

        for i in range(n_elements):
            mask = valid[i]
            n = npoints[i]
            trimmed_points[i, :n] = (evaluation_points[i, mask])
            for trimmed, force in zip(trimmed_forces, force_arrays):
                trimmed[i, :n] = force[i, mask]
        return (trimmed_points, *trimmed_forces)

    def _get_element_force_data(self, converter, ndim, coords, element_idx, element_tag, end_nodes_idx, element_type, offsets_length, rigid_zone_factor):
        tag_to_idx = {
            tag: idx
            for idx, tag in zip(element_idx, element_tag)
        }
        element_load_data = self._get_element_load_data() # Retrieve element load data for all load cases
        element_load_idx = np.fromiter((
            tag_to_idx[tag]
            for tag in element_load_data.element_tag
            ), dtype=np.int32, count=len(element_load_data.element_tag),
        )
        n = len(element_tag)
                
        inode_coords = coords[end_nodes_idx[:, ConnectionEnd.I_End]] # Retrieve I-end node coordinates from node coordinates
        jnode_coords = coords[end_nodes_idx[:, ConnectionEnd.J_End]] # Retrieve J-end node coordinates from node coordinates
        if ndim == 3:
            element_local_end_forces = np.empty((n, 12), dtype=np.float64)
            d_vectors = jnode_coords - inode_coords # Determine direction vectors
            length = np.linalg.norm(d_vectors, axis=1) # Compute length of elements
            vector_x = d_vectors / length[:, None] # Determine vector x-axis
            reference = np.tile(np.array([0.0, 0.0, 1.0]), (len(vector_x), 1)) # Define reference direction, default is toward global Z-axis
            vertical = np.abs(vector_x[:, 2]) > 0.99 # Build masking for vertical elements
            reference[vertical] = np.array([1.0, 0.0, 0.0]) # Change reference direction for vertical elements which is toward global X-axis
            vector_z = np.cross(vector_x, reference) # Determine vector z-axis using cross product of vector x-axis and reference direction
            vector_z /= np.linalg.norm(vector_z, axis=1)[:, None] # Normalise vector z-axis
            vector_y = np.cross(vector_z, vector_x) # Determine vector y-axis using cross product of vector z-axis and vector x-axis
            vector_y /= np.linalg.norm(vector_y, axis=1)[:, None] # Normalise vector y-axis
        else:
            element_local_end_forces = np.empty((n, 6), dtype=np.float64)
            inode_coords = inode_coords[:, :2] # Retrieve I-end node coordinates (X, Y)
            jnode_coords = jnode_coords[:, :2] # Retrieve J-end node coordinates (X, Y)
            d_vectors = jnode_coords - inode_coords # Determine direction vectors
            length = np.linalg.norm(d_vectors, axis=1) # Compute length of elements
            cx = d_vectors[:, 0] / length # Compute the x-component of the direction cosine of elements
            cy = d_vectors[:, 1] / length # Compute the y-component of the direction cosine of elements
            vector_x = np.column_stack((cx, cy)) # Determine vector x-axis
            vector_y = np.column_stack((-cy, cx)) # Determine vector y-axis

        # Element forces distributions from end forces
        for i, ele_tag in enumerate(element_tag):
            element_local_end_forces[i] = ops.eleResponse(int(ele_tag), 'localForces') # Retrieve element local end forces

        if ndim == 3:
            (Fxi, Fyi, Fzi, Mxi, Myi, Mzi, Fxj, Fyj, Fzj, Mxj, Myj, Mzj) = element_local_end_forces.T # Unpack element end local forces
        else:
            (Fxi, Fyi, Mzi, Fxj, Fyj, Mzj) = element_local_end_forces.T # Unpack element end local forces
            Fzi = np.zeros(n, dtype=np.float64)
            Mxi = np.zeros(n, dtype=np.float64)
            Myi = np.zeros(n, dtype=np.float64)
            Fzj = np.zeros(n, dtype=np.float64)
            Mxj = np.zeros(n, dtype=np.float64)
            Myj = np.zeros(n, dtype=np.float64)

        iend_offset_length = offsets_length[:, 0] # I-end offset length of element
        jend_offset_length = offsets_length[:, 1] # J-end offset length of element
        start_point = iend_offset_length # Start point for evaluation
        end_point = length - jend_offset_length # End point for evaluation
        ep_type = np.where(element_type == "Column", "-nEvaluationPoints", "-maxSpacing")
        ep_value = np.where(element_type == "Column", 3.0, converter.length(values=0.5))
        evaluation_points = self._generate_evaluation_points(start_point, end_point, length, ep_type, ep_value)

        P_in = np.where(np.isnan(evaluation_points), np.nan, (-1.0 * Fxi)[:, None])
        Vy_in = np.where(np.isnan(evaluation_points), np.nan, (Fyi)[:, None])
        Vz_in = np.where(np.isnan(evaluation_points), np.nan, (Fzi)[:, None])
        T_in = np.where(np.isnan(evaluation_points), np.nan, (-1.0 * Mxi)[:, None]) # Need to check further
        My_in = np.where(np.isnan(evaluation_points), np.nan, (-1.0 * Myi)[:, None])
        Mz_in = np.where(np.isnan(evaluation_points), np.nan, (-1.0 * Mzi)[:, None])

        # Element force distributions from loads
        P_load = np.zeros_like(evaluation_points)
        Vy_load = np.zeros_like(evaluation_points)
        Vz_load = np.zeros_like(evaluation_points)
        My_load = np.zeros_like(evaluation_points)
        Mz_load = np.zeros_like(evaluation_points)

        uniform_mask = (element_load_data.type_ == OpenseesLoadType.BeamUniform)
        if np.any(uniform_mask):
            idx = element_load_idx[uniform_mask]
            values = (element_load_data.values[uniform_mask])
            if ndim == 3:
                wy = values[:, 0]
                wz = values[:, 1]
                wx = values[:, 2]
            else:
                wy = values[:, 0]
                wx = values[:, 1]
                wz = np.zeros_like(wy)
            x = evaluation_points[idx]
            Fx_uniform = (-1.0 * wx[:, None] * x)
            Fy_uniform = (wy[:, None] * x)
            Fz_uniform = (wz[:, None] * x)
            My_uniform = ((Fzi)[idx, None] * evaluation_points) + (0.5 * wz[:, None] * x**2)
            Mz_uniform = ((Fyi)[idx, None] * evaluation_points) + (0.5 * wy[:, None] * x**2)
            np.add.at(P_load, idx, Fx_uniform)
            np.add.at(Vy_load, idx, Fy_uniform)
            np.add.at(Vz_load, idx, Fz_uniform)
            np.add.at(My_load, idx, My_uniform)
            np.add.at(Mz_load, idx, Mz_uniform)

        partialuniform_mask = (element_load_data.type_ == OpenseesLoadType.BeamPartialUniform)
        point_mask = (element_load_data.type_ == OpenseesLoadType.BeamPoint)

        # Element force distributions
        P = (P_in + P_load)
        Vy = (Vy_in + Vy_load)
        Vz = (Vz_in + Vz_load)
        T = (T_in)
        My = (My_in + My_load)
        Mz = (Mz_in + Mz_load)

        # Trim force distribution
        (evaluation_points, P, Vy, Vz, T, My, Mz) = self._trim_force_distribution(
            evaluation_points=evaluation_points,
            start_point=start_point,
            end_point=end_point,
            force_arrays=(P, Vy, Vz, T, My, Mz)
        )
        element_force_data = ElementForceData(
            element_tag=element_tag,
            locations=evaluation_points,
            P=P,
            Vy=Vy,
            Vz=Vz,
            T=T,
            My=My,
            Mz=Mz,
        ) # Store element force data to dataclass
        return element_force_data