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