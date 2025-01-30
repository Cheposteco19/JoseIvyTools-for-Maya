from maya import cmds
import maya.mel as mm

def auto_unwrap(selected_items):
    """
    Auto unwraps, unfolds, unlocks normals and set to face normals, soften/harden faces along texture borders
    Deletes history and freezes transformations
    """

    if not selected_items:
        cmds.warning("No items selected for auto unwrap.")
        return

    for item in selected_items:
        if cmds.objExists(item):
            cmds.polyAutoProjection(item)
        else:
            cmds.warning(f"Item {item} does not exist.")

    # Orient Shells
    mm.eval("texOrientShells;")

    #Layout
    cmds.u3dLayout(res=256, scl=1, spc=0.001953125, box=(0,1,0,1))

def soft_texture_borders(selected_items):

    if not selected_items:
        cmds.warning("No items selected for softening texture borders.")
        return

    for item in selected_items:
        if cmds.objExists(item):
            cmds.UnlockNormals()
            cmds.polySetToFaceNormal(item)
            mm.eval('polyUVBorderHard;')
            cmds.DeleteHistory(item)
            cmds.FreezeTransformations()
        else:
            cmds.warning(f"Item {item} does not exist.")

def ucx_process(static_mesh):
    """
    Processes a static mesh to create a UCX group.
    - Does not duplicate the static mesh.
    - Creates an empty UCX group if not already present.
    - Moves any existing UCX mesh into the UCX group.
    """
    group_name = f"UCX_{static_mesh}_grp"
    ucx_mesh = f"UCX_SM_{static_mesh}"

    # Create UCX group if it does not exist
    if not cmds.objExists(group_name):
        cmds.group(empty=True, name=group_name)
        print(f"Created UCX group: {group_name}")
    else:
        print(f"UCX group {group_name} already exists.")

    # If UCX mesh exists, move it inside the UCX group
    if cmds.objExists(ucx_mesh):
        current_parent = cmds.listRelatives(ucx_mesh, parent=True)
        if not current_parent or current_parent[0] != group_name:
            cmds.parent(ucx_mesh, group_name)
            print(f"Moved {ucx_mesh} into {group_name}.")
    else:
        print(f"No existing UCX mesh found for {ucx_mesh}. UCX group remains empty.")

    return static_mesh  # Return the original mesh name
    
def ucx_process_mult(selected_objects):
    """
    Processes multiple selected objects:
    - No duplication.
    - Creates an empty UCX group for each static mesh.
    - Moves any existing UCX mesh (`UCX_SM_<mesh>`) into the UCX group.
    - Returns a list of tuples: (original mesh, UCX group name).
    """
    ucx_groups = []

    for obj in selected_objects:
        static_mesh = f"SM_{obj}"
        ucx_group_name = f"UCX_{obj}_grp"
        ucx_mesh_name = f"UCX_SM_{obj}"

        # Create UCX group if it does not exist
        if not cmds.objExists(ucx_group_name):
            cmds.group(empty=True, name=ucx_group_name)
            print(f"Created UCX group: {ucx_group_name}")
        else:
            print(f"UCX group {ucx_group_name} already exists.")

        # If UCX mesh exists, move it inside the UCX group
        if cmds.objExists(ucx_mesh_name):
            current_parent = cmds.listRelatives(ucx_mesh_name, parent=True)
            if not current_parent or current_parent[0] != ucx_group_name:
                cmds.parent(ucx_mesh_name, ucx_group_name)
                print(f"Moved {ucx_mesh_name} into {ucx_group_name}.")
        else:
            print(f"No existing UCX mesh found for {ucx_mesh_name}. UCX group remains empty.")

        ucx_groups.append((static_mesh, ucx_group_name))

    return ucx_groups  # Return list of tuples (original object, UCX group)  