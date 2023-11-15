from maya import cmds
import maya.mel as mm

def auto_unwrap():
    selected_items = cmds.ls(sl=True)

    for item in selected_items:
        cmds.polyAutoProjection(item)

    cmds.u3dLayout(selected_items,res=2048,scl=1,spc=0.015625,mar=0.0078125,box=(0,1,0,1))

    for item in selected_items:
        cmds.polySetToFaceNormal(item)
        mm.eval('polyUVBorderHard;')
        cmds.DeleteHistory(item)
        cmds.FreezeTransformations()
