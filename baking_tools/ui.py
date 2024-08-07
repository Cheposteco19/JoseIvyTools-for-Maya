from baking_tools import core as baking_tools_core
from maya import cmds
import maya.mel as mm
import pickle
import os

#Window components names
DISPLAY_LAYER_WORKSPACE_CONTROL_NAME= 'displayLayerWorkspaceControl'
AUTOUNWRAP_CHECK_BOX_NAME= 'auto_unwrap_check_box'
BROWSE_BUTTON_NAME_DICT={}

#Save preferances settings

SCENE_NAME_AND_PATH=cmds.file(query=True, expandName=True)
DIRECTORY_HISTORY_NAME='{}_directory_history'.format(os.path.basename(SCENE_NAME_AND_PATH))
DIRECTORY_HISTORY_ROOT_DIR = '{}/{}/prefs'.format(mm.eval('getenv "MAYA_APP_DIR";'), cmds.about(version=True))
DIRECTORY_HISTORY_EXT= 'pck'

#Colors
LIGHT_GREEN=(.2,.4,.2)
GREEN=(.2,.3,.2)
DARK_GREEN=(.1,.2,.1)
LIGHT_BLUE=(.2,.2,.4)
BLUE=(.2,.2,.3)
DARK_BLUE=(.1,.1,.2) 

#Browse defined

def browse(browseButton):
    """
    Browses
    Args:
        browseButton: for writing the user input when he browses
    """
    path = cmds.fileDialog2(dialogStyle=2, fileMode=3, okCaption="Select Folder")
    cmds.button(browseButton, edit=True, annotation=path[0])
    save_paths_to_file()

#Export defined

def extra_exportFBX1(*args):
    """exports the selection to the first browse path in the directory_history"""
    exportFBX(next(iter(BROWSE_BUTTON_NAME_DICT.keys())))

def exportFBX(layer):
    """
    Checks if auto unwrap is necessary and
    Gets the user input path, saves it and exports the FBX
    Args:
        layer:which layer will the fbx is the one to be named after
    """
    #    selected_items = cmds.ls(sl=True)
    #    if cmds.checkBox(AUTOUNWRAP_CHECK_BOX_NAME, query=True, value=True)==True:
    #        baking_tools_core.auto_unwrap(selected_items)
    #    baking_tools_core.soft_texture_borders(selected_items)
    paths_dict = save_paths_to_file()
    print(paths_dict)
    if all(value == '' for value in paths_dict.values()):
        cmds.warning(("Please browse and select a folder to export the layer to"))
        return
    if paths_dict[layer]=='':
        paths_dict[layer]=next(iter(paths_dict.values()))
    path_to_export = paths_dict[layer]
    export_name_with_path='{}/{}'.format(path_to_export,layer)
    if not cmds.pluginInfo('fbxmaya', query=True, loaded=True):
        cmds.loadPlugin('fbxmaya')
    objects_in_layer = cmds.editDisplayLayerMembers(layer, query=True) or []
    cmds.select(clear=True)
    cmds.select(objects_in_layer, replace=True)
    cmds.file(export_name_with_path, force=True, options='v=0;', type='FBX export', exportSelected=True, preserveReferences=True)

def save_paths_to_file():
    """
    Saves paths in user preferences
    Returns: previous paths dictionary
    """
    paths_dict = read_directories_from_browse_buttons()
    write_directory_to_file(DIRECTORY_HISTORY_NAME, paths_dict)
    return paths_dict

def read_directories_from_browse_buttons():
    """
    Reads paths from user input
    Returns: paths dictionary read
    """
    paths_dict={}
    for layer, button in BROWSE_BUTTON_NAME_DICT.items():
        if button == 'defaultLayer_browse_button':
            continue
        path=cmds.button(button, query=True, annotation=True)
        paths_dict[layer]=path
    return paths_dict

def write_directory_to_file(directory_history_name, directory_dict):
    """Writes paths into user preferences"""
    file_name='{}.{}'.format(directory_history_name, DIRECTORY_HISTORY_EXT)
    file_path=os.path.join(DIRECTORY_HISTORY_ROOT_DIR, file_name)

    try:
        with open(file_path,'wb') as f:
            pickle.dump(directory_dict,f)
    except IOError:
        cmds.warning((f"Failed to write directory history to {file_path}"))

def read_directory_from_file():
    """
    Reads paths from user preferences
    Returns: paths dictionary read
    """
    file_path = r'{}\{}.{}'.format(DIRECTORY_HISTORY_ROOT_DIR,DIRECTORY_HISTORY_NAME,DIRECTORY_HISTORY_EXT)
    if not os.path.exists(file_path):
        directory_dict={}
        for layer in BROWSE_BUTTON_NAME_DICT.keys():
            directory_dict[layer]=''
        return directory_dict
    
    try:
        with open(file_path, 'rb') as f:
            directory_dict = pickle.load(f)
    except IOError:
        cmds.warning(f"Failed to read directory history from {file_path}")

    for layer in BROWSE_BUTTON_NAME_DICT.keys():
        if layer not in directory_dict:
            directory_dict[layer] = ''
        
    return directory_dict


# ----------------------------------------------------------------------
# Display Layer functions

def toggle_display_type(layer, checkbox):
    current_state = cmds.getAttr(layer + ".displayType")
    new_state = (current_state + 1) % 3  # Cycle through 0, 1, 2

    cmds.setAttr(layer + ".displayType", new_state)

    if new_state == 0:
        cmds.checkBox(checkbox, edit=True, label=" ", value=False)
    elif new_state == 1:
        cmds.checkBox(checkbox, edit=True, label="T", value=True)
    elif new_state == 2:
        cmds.checkBox(checkbox, edit=True, label="R", value=True)

def set_layer_color(layer):
    color = cmds.colorEditor()
    if cmds.colorEditor(query=True, result=True):
        rgb = cmds.colorEditor(query=True, rgb=True)
        cmds.setAttr(layer + ".overrideColorRGB", rgb[0], rgb[1], rgb[2])
        cmds.setAttr(layer + ".overrideRGBColors", 1)
        update_display_layer_ui()

def set_layer_color(layer, color_field=None):
    if color_field:
        color = cmds.colorSliderGrp(color_field, query=True, rgbValue=True)
    else:
        color = cmds.colorEditor()
        if not cmds.colorEditor(query=True, result=True):
            return  # User cancelled the color editor
        color = cmds.colorEditor(query=True, rgb=True)

    cmds.setAttr(layer + ".overrideColorRGB", color[0], color[1], color[2])
    cmds.setAttr(layer + ".overrideRGBColors", 1)
    update_display_layer_ui()

def get_layer_color(layer):
    if cmds.attributeQuery("overrideColorRGB", node=layer, exists=True):
        if cmds.getAttr(layer + ".overrideColorRGB")[0] == (0, 0, 0):
            return [0.5, 0.5, 0.5]
        return cmds.getAttr(layer + ".overrideColorRGB")[0]
    else:
        return [0.5, 0.5, 0.5]  # Default color if not set

def add_layer(*args):
    selected_objects = cmds.ls(selection=True)
    new_layer = cmds.createDisplayLayer(name="NewLayer", empty=True)
    if selected_objects:
        cmds.editDisplayLayerMembers(new_layer, selected_objects)
    update_display_layer_ui()

def rename_layer(layer, text_field):
    new_name = cmds.textField(text_field, query=True, text=True)
    if cmds.objExists(new_name):
        cmds.warning(f"An object named '{new_name}' already exists. Choose a different name.")
    else:
        cmds.rename(layer, new_name)
        update_display_layer_ui()

def update_display_layer_ui():
    if cmds.workspaceControl(DISPLAY_LAYER_WORKSPACE_CONTROL_NAME, exists=True):
        cmds.deleteUI(DISPLAY_LAYER_WORKSPACE_CONTROL_NAME, control=True)
    create_display_layer_ui()

def delete_layer(layer):
    if layer and layer != "defaultLayer":
        cmds.delete(layer)
        update_display_layer_ui()

def add_objects_to_layer(layer):
    selected_objects = cmds.ls(selection=True)
    if selected_objects:
        cmds.editDisplayLayerMembers(layer, selected_objects)
        update_display_layer_ui()

def remove_objects_from_layer(layer):
    selected_objects = cmds.ls(selection=True)
    if selected_objects:
        for object in selected_objects:
            if object not in cmds.editDisplayLayerMembers(layer, query=True):
                continue
            cmds.editDisplayLayerMembers('defaultLayer', object)
    update_display_layer_ui()

def create_display_layer_ui():
    if cmds.workspaceControl(DISPLAY_LAYER_WORKSPACE_CONTROL_NAME, exists=True):
        cmds.deleteUI(DISPLAY_LAYER_WORKSPACE_CONTROL_NAME, control=True)

    BROWSE_BUTTON_NAME_DICT.clear()

    workspace_ctrl = cmds.workspaceControl(DISPLAY_LAYER_WORKSPACE_CONTROL_NAME, label="Display Layer Editor")
    cmds.columnLayout(adjustableColumn=True)

    cmds.text(label="Display Layers", align='left', height=20)

    layer_list = cmds.ls(type="displayLayer")

    for layer in layer_list:
        BROWSE_BUTTON_NAME_DICT[layer] = '{}_browse_button'.format(layer)

    paths_dict = read_directory_from_file()

    for layer in layer_list:
        if layer == "defaultLayer":
            continue  # Skip the default layer

        layer_row_layout = cmds.rowLayout(numberOfColumns=9, adjustableColumn=True, columnAlign=(1, 'left'))
        
        # Layer Name
        text_field = cmds.textField(width=100)
        cmds.textField(text_field, edit=True, text=layer, changeCommand=lambda *args, l=layer, tf=text_field: rename_layer(l, tf))

        # Visibility Checkbox
        visibility = cmds.getAttr(layer + ".visibility")
        cmds.checkBox(label="V", value=visibility, width=30, 
                      onCommand=lambda *args, l=layer: cmds.setAttr(l + ".visibility", 1), 
                      offCommand=lambda *args, l=layer: cmds.setAttr(l + ".visibility", 0))
        
        # Template/Reference Checkbox
        display_type = cmds.getAttr(layer + ".displayType")
        checkbox_label = " " if display_type == 0 else "T" if display_type == 1 else "R" if display_type == 2 else "T"
        template_checkbox = cmds.checkBox(label=checkbox_label, value=(display_type != 0), width=30)
        
        # Color Box
        layer_color = get_layer_color(layer)
        color_box = cmds.iconTextButton(style='textOnly', label="", width=30, bgc=layer_color,
                                        command=lambda *args, l=layer: set_layer_color(l))  
        
        # Correctly reference the checkbox
        cmds.checkBox(template_checkbox, edit=True, 
                      onCommand=lambda *args, c=template_checkbox, l=layer: toggle_display_type(l, c), 
                      offCommand=lambda *args, c=template_checkbox, l=layer: toggle_display_type(l, c))
        
        # Ensure the correct initial label
        if display_type == 0:
            cmds.checkBox(template_checkbox, edit=True, label=" ", value=False)
        elif display_type == 1:
            cmds.checkBox(template_checkbox, edit=True, label="T", value=True)
        elif display_type == 2:
            cmds.checkBox(template_checkbox, edit=True, label="R", value=True)

        # Color Picker
        if cmds.attributeQuery("overrideColorRGB", node=layer, exists=True):
            color = cmds.getAttr(layer + ".overrideColorRGB")[0]
            if color == (0.0, 0.0, 0.0):
                color = [.5, .5, .5]
        else:
            color = [0.5, 0.5, 0.5]  # Default color if not set

        if color:
            color_field = cmds.colorSliderGrp(label="Color", rgb=(color[0], color[1], color[2]), width=100)
        else:
            color_field = cmds.colorSliderGrp(label="Color", width=100)
        cmds.colorSliderGrp(color_field, edit=True, changeCommand=lambda *args, l=layer, cf=color_field: set_layer_color(l, cf))    

        # Browse button
        cmds.button(BROWSE_BUTTON_NAME_DICT[layer], label="...", width=50, command=lambda *args, b=BROWSE_BUTTON_NAME_DICT[layer]: browse(b), annotation=paths_dict[layer])
        
        # Export Button
        cmds.button(label="Export", width=100, command=lambda *args, l=layer: exportFBX(l))
        
        # Add a right-click context menu to the text field
        cmds.popupMenu(parent=text_field)
        cmds.menuItem(label="Delete Layer", command=lambda *args, l=layer: delete_layer(l))
        cmds.menuItem(label="Add Selected Objects", command=lambda *args, l=layer: add_objects_to_layer(l))
        cmds.menuItem(label="Remove Selected Objects", command=lambda *args, l=layer: remove_objects_from_layer(l))
        
        cmds.setParent('..')  # End rowLayout
    
    # Add Layer Button
    cmds.button(label="Add Layer", command=add_layer)
