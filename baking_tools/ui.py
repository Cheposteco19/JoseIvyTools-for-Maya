from baking_tools import core as bake_tester_core
from maya import cmds
import maya.mel as mm
import json
import os

WINDOW_NAME='bake_test_ui'
CHECK_BOX_NAME='auto_unwrap_check_box'
LOW_POLY_PATH_TEXT_BOX_NAME='low_poly_path_text_box'
HIGH_POLY_PATH_TEXT_BOX_NAME='high_poly_path_text_box'
DOCK_CONTROL_NAME='bake_tester_dock_control'

DIRECTORY_HISTORY_NAME='directory_history'
DIRECTORY_HISTORY_ROOT_DIR = mm.eval('getenv "MAYA_APP_DIR";')
DIRECTORY_HISTORY_EXT= 'json'

def show_ui():
    # Delete old window
    if cmds.window(WINDOW_NAME, exists=True,query=True):
        cmds.deleteUI(WINDOW_NAME)

    if cmds.dockControl(DOCK_CONTROL_NAME, exists=True,query=True):
        cmds.deleteUI(DOCK_CONTROL_NAME)
    paths_dict=read_directory_from_file()

    # Create new window
    cmds.window(WINDOW_NAME, title='Baking tools', widthHeight=(500,100))

    #Auto-Unwrap
    cmds.columnLayout(adjustableColumn=True, columnOffset=('both',10))
    cmds.checkBox(CHECK_BOX_NAME,label="Auto-Unwrap")

    # Browse Low Export
    cmds.rowLayout(numberOfColumns=3,adjustableColumn=True)
    cmds.textField(LOW_POLY_PATH_TEXT_BOX_NAME, text=paths_dict[LOW_POLY_PATH_TEXT_BOX_NAME])
    cmds.button(label='...',command=browse_low)
    cmds.button(label='Export LOW',command=low_exportFBX,width=73)
    cmds.setParent('..')

    # Browse High Export
    cmds.rowLayout(numberOfColumns=3,adjustableColumn=True)
    cmds.textField(HIGH_POLY_PATH_TEXT_BOX_NAME, text=paths_dict[HIGH_POLY_PATH_TEXT_BOX_NAME])
    cmds.button(label='...',command=browse_high)
    cmds.button(label='Export HIGH',command=high_exportFBX)
    cmds.setParent('..')

    #Credits
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2)
    cmds.text(label='V 1.0.3')
    cmds.text(label='GD67_JoseMunguia   ', align='right')

    cmds.setParent('..')
    cmds.dockControl(DOCK_CONTROL_NAME,floating=True,label='Bake tester',content=WINDOW_NAME,area='left',width=500,height=100,allowedArea=('top','bottom'))

    # Show window
    cmds.showWindow()

    # Browse defined
def browse_low(*args):
    browse(LOW_POLY_PATH_TEXT_BOX_NAME)

def browse_high(*args):
    browse(HIGH_POLY_PATH_TEXT_BOX_NAME)

def browse(textbox):
    path = cmds.fileDialog2(fileFilter="*.fbx", dialogStyle=2)
    cmds.textField(textbox, edit=True, text=path[0])

#Export buttons
def low_exportFBX(*args):
    if cmds.checkBox(CHECK_BOX_NAME,query=True,value=True)==True:
        bake_tester_core.auto_unwrap()
    exportFBX(LOW_POLY_PATH_TEXT_BOX_NAME)

def high_exportFBX(*args):
    exportFBX(HIGH_POLY_PATH_TEXT_BOX_NAME)

def exportFBX(text_box):
    paths_dict = save_paths_to_file()
    path_to_export = paths_dict[text_box]
    cmds.file(path_to_export, force=True, options='v=0;', type='FBX export', exportSelected=True, preserveReferences=True)

def save_paths_to_file():
    paths_dict = read_directories_from_text_boxes()
    write_directory_to_file(DIRECTORY_HISTORY_NAME, paths_dict)
    return paths_dict

def read_directories_from_text_boxes():
    paths_dict={}
    paths_dict[HIGH_POLY_PATH_TEXT_BOX_NAME] = cmds.textField(HIGH_POLY_PATH_TEXT_BOX_NAME, query=True, text=True)
    paths_dict[LOW_POLY_PATH_TEXT_BOX_NAME] = cmds.textField(LOW_POLY_PATH_TEXT_BOX_NAME, query=True, text=True)
    return paths_dict
def get_directory_dict():
    directory_dict={}
    for file_name in os.listdir(DIRECTORY_HISTORY_ROOT_DIR):
        if not file_name.endswith(DIRECTORY_HISTORY_EXT):
            continue
        directory_history_name=file_name.split('.')[0]
        file_path=os.path.join(DIRECTORY_HISTORY_ROOT_DIR, file_name)
        directory_dict[directory_history_name]=file_path

    return directory_dict

def write_directory_to_file(directory_history_name, directory_dict):
    file_name='{}.{}'.format(directory_history_name, DIRECTORY_HISTORY_EXT)
    file_path=os.path.join(DIRECTORY_HISTORY_ROOT_DIR, file_name)

    with open(file_path,'w') as f:
        json.dump(directory_dict, f, indent=4)

def read_directory_from_file():
    file_path = r'{}\{}.{}'.format(DIRECTORY_HISTORY_ROOT_DIR,DIRECTORY_HISTORY_NAME,DIRECTORY_HISTORY_EXT)
    if not os.path.exists(file_path):
        directory_dict={}
        directory_dict[HIGH_POLY_PATH_TEXT_BOX_NAME]=''
        directory_dict[LOW_POLY_PATH_TEXT_BOX_NAME]=''
        return directory_dict
    with open(file_path, 'r') as f:
        directory_dict = json.load(f)
    return directory_dict