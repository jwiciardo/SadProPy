import openseespy.opensees as ops


def _assign_restraints(modeldata):
    restraints = modeldata.restraints # Retrieve restraints data
    node_tag = restraints.node_tag
    restraint_dofs = restraints.dofs
    for i in restraints.node_idx:
        dofs = list(map(int, restraint_dofs[i]))
        ops.fix(
            int(node_tag[i]), # nodeTag
            *dofs, # *constrValues = [UX, UY, UZ, RX, RY, RZ]
        )