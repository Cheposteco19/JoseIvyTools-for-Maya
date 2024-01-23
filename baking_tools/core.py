from maya import cmds
import maya.mel as mm

def auto_unwrap():
    """
    Auto unwraps, unfolds, unlocks normals and set to face normals, soften/harden faces along texture borders
    Deletes history and freezes transformations
    """
    selected_items = cmds.ls(sl=True)

    for item in selected_items:
        cmds.polyAutoProjection(item)

    # Orient Shells
    mm.eval("texOrientShells;")

    #Layout
    cmds.u3dLayout(res=256, scl=1, spc=0.001953125, box=(0,1,0,1))

def soft_texture_borders():

    selected_items = cmds.ls(sl=True)

    for item in selected_items:
        cmds.UnlockNormals()
        cmds.polySetToFaceNormal(item)
        mm.eval('polyUVBorderHard;')
        cmds.DeleteHistory(item)
        cmds.FreezeTransformations()
