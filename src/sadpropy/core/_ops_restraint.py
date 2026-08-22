import openseespy.opensees as ops


def _define_restraint(modeldata):
    restraints = modeldata.restraints # Retrieve restraints data
    node_tag = restraints.node_tag
    dofs = restraints.dofs
    for i in restraints.node_idx:
        dofs_value = list(map(int, dofs[i]))
        ops.fix(
            int(node_tag[i]), # nodeTag
            *dofs_value, # *constrValues
        )