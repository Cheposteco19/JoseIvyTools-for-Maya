from baking_tools import core as bake_tester_core
from maya import cmds

WINDOW_NAME='bake_test_ui'
CHECK_BOX_NAME='auto_unwrap_check_box'
LOW_POLY_PATH_TEXT_BOX_NAME='low_poly_path_text_box'
HIGH_POLY_PATH_TEXT_BOX_NAME='high_poly_path_text_box'
DOCK_CONTROL_NAME='bake_tester_dock_control'

def show_ui():
    # Delete old window
    if cmds.window(WINDOW_NAME, exists=True,query=True):
        cmds.deleteUI(WINDOW_NAME)

    if cmds.dockControl(DOCK_CONTROL_NAME, exists=True,query=True):
        cmds.deleteUI(DOCK_CONTROL_NAME)

    # Create new window
    cmds.window(WINDOW_NAME, title='Baking tools', widthHeight=(500,100))

    #Auto-Unwrap
    cmds.columnLayout(adjustableColumn=True, columnOffset=('both',10))
    cmds.checkBox(CHECK_BOX_NAME,label="Auto-Unwrap")

    # Browse Low Export
    cmds.rowLayout(numberOfColumns=3,adjustableColumn=True)
    cmds.textField(LOW_POLY_PATH_TEXT_BOX_NAME)
    cmds.button(label='...',command=browse_low)
    cmds.button(label='Export LOW',command=low_exportFBX,width=73)
    cmds.setParent('..')

    # Browse High Export
    cmds.rowLayout(numberOfColumns=3,adjustableColumn=True)
    cmds.textField(HIGH_POLY_PATH_TEXT_BOX_NAME)
    cmds.button(label='...',command=browse_high)
    cmds.button(label='Export HIGH',command=high_exportFBX)
    cmds.setParent('..')

    #Credits
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2)
    cmds.text(label='V 1.0.0')
    cmds.text(label='GD67_JoseMunguia   ', align='right')

    cmds.setParent('..')
    cmds.dockControl(DOCK_CONTROL_NAME,floating=True,label='Bake tester',content=WINDOW_NAME,area='left',width=500,height=100,allowedArea=('top','bottom'))

    # Show window
    cmds.showWindow()

    # Browse defined
def browse_low(*args):
    low_path = cmds.fileDialog2(fileFilter="*.fbx", dialogStyle=2)
    cmds.textField(LOW_POLY_PATH_TEXT_BOX_NAME,edit=True,text=low_path[0])

def browse_high(*args):
    high_path = cmds.fileDialog2(fileFilter="*.fbx", dialogStyle=2)
    cmds.textField(HIGH_POLY_PATH_TEXT_BOX_NAME,edit=True,text=high_path[0])

#Export buttons
def low_exportFBX(*args):
    if cmds.checkBox(CHECK_BOX_NAME,query=True,value=True)==True:
        bake_tester_core.auto_unwrap()
    low_path = cmds.textField(LOW_POLY_PATH_TEXT_BOX_NAME, query=True, text=True)
    cmds.file(low_path,force=True,options='v=0;',type='FBX export',exportSelected=True,preserveReferences=True)

def high_exportFBX(*args):
    high_path = cmds.textField(HIGH_POLY_PATH_TEXT_BOX_NAME, query=True, text=True)
    cmds.file(high_path,force=True,options='v=0;',type='FBX export',exportSelected=True,preserveReferences=True)