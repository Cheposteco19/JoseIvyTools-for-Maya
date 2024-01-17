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

    cmds.u3dUnfold(selected_items,ite=1, p=0, bi=1, tf=1, ms=1024, rs=2)
    cmds.polyMultiLayoutUV(selected_items,lm=1, sc=1, rbf=1, fr=1, ps=0.2, l=2, gu=1, gv=1, psc=0, su=1, sv=1, ou=0, ov=0)

def soft_texture_borders():

    selected_items = cmds.ls(sl=True)

    for item in selected_items:
        cmds.polySetToFaceNormal(item)
        mm.eval('polyUVBorderHard;')
        cmds.DeleteHistory(item)
        cmds.FreezeTransformations()
