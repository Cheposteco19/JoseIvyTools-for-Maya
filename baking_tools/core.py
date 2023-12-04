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

    cmds.unfold(selected_items,i=5000, ss=0.001, gb=0, gmb=0.5, pub=0, ps=0, oa=0, us=1, s=0.02)

    for item in selected_items:
        cmds.polySetToFaceNormal(item)
        mm.eval('polyUVBorderHard;')
        cmds.DeleteHistory(item)
        cmds.FreezeTransformations()
