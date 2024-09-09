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
    group='{}_grp'.format(static_mesh)
    static_mesh='SM_{}'.format(static_mesh)
    ucx='UCX_{}'.format(static_mesh)
    cmds.rename(static_mesh)
    cmds.duplicate(static_mesh,name=ucx)
    cmds.group(static_mesh,ucx,n=group)
    return static_mesh
    
def ucx_process_mult(selected_objects):
    """
    Processes multiple selected objects to create UCX copies, group them, 
    and return the list of new static meshes (originals with SM_ prefix).
    """
    ucx_groups = []
    for obj in selected_objects:
        group = '{}_grp'.format(obj)
        static_mesh = 'SM_{}'.format(obj)
        ucx = 'UCX_{}'.format(static_mesh)
        cmds.rename(obj, static_mesh)  # Rename the original object
        cmds.duplicate(static_mesh, name=ucx)  # Duplicate to create UCX
        cmds.group(static_mesh, ucx, n=group)  # Group the original and UCX copy
        ucx_groups.append((static_mesh, ucx, group))  # Keep track of renamed objects and their groups
    return ucx_groups  # Return a list of tuples (original object, UCX copy, group)
   