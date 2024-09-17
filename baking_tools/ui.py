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
    if all(value == '' for value in paths_dict.values()):
        cmds.warning(("Please browse and select a folder to export the layer to"))
        return
    if paths_dict[layer] == '':
        paths_dict[layer] = paths_dict['defaultLayer']
    path_to_export = paths_dict[layer]
    fbx = 'SM_{}'.format(layer)
    export_name_with_path = '{}/{}'.format(path_to_export,fbx)
    if not cmds.pluginInfo('fbxmaya', query=True, loaded=True):
        cmds.loadPlugin('fbxmaya')
    objects_in_layer = cmds.editDisplayLayerMembers(layer, query=True) or []
    cmds.select(clear=True)
    cmds.select(objects_in_layer, replace=True)
    cmds.file(export_name_with_path, force=True, options='v=0;', type='FBX export', exportSelected=True, preserveReferences=True)

#Export All Layers
def export_all_layers(layer_list):
    for layer in layer_list:
        if layer == 'defaultLayer':
            continue
        exportFBX(layer)


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
    set_display_type(layer, checkbox, new_state)

def set_display_type(layer, checkbox, new_state):
    cmds.setAttr(layer + ".displayType", new_state)
    if new_state == 0:
        cmds.checkBox(checkbox, edit=True, label=" ", value=False)
    elif new_state == 1:
        cmds.checkBox(checkbox, edit=True, label="T", value=True)
    elif new_state == 2:
        cmds.checkBox(checkbox, edit=True, label="R", value=True)

# Add the "Global Display Type" Checkbox (to control all layers except defaultLayer)
def toggle_all_display_types(layers, display_type_checkboxes):
    current_state = cmds.checkBox(display_type_checkboxes[-1], query=True, label=True)

    if current_state == 'R':
        cmds.checkBox(display_type_checkboxes[-1], edit=True, label=" ", value=False)
        new_state = 0
    elif current_state == ' ':
        cmds.checkBox(display_type_checkboxes[-1], edit=True, label="T", value=True)
        new_state = 1
    elif current_state == 'T':
        cmds.checkBox(display_type_checkboxes[-1], edit=True, label="R", value=True)
        new_state = 2

    for index, layer in enumerate(layers):
        if layer != "defaultLayer":
            set_display_type(layer, display_type_checkboxes[index], new_state)

def toggle_all_visibility(layers, visibility_checkboxes):
    current_state = cmds.checkBox(visibility_checkboxes[-1], query=True, value=True)  # Check the checkbox state (True if checked)

    # If it's checked, turn all layers' visibility on, otherwise turn them off
    if current_state:
        new_visibility = True
    else:
        new_visibility = False

    # Apply the new visibility to all layers except the defaultLayer
    for index, layer in enumerate(layers):
        if layer != "defaultLayer":
            cmds.setAttr(f"{layer}.visibility", new_visibility)
            cmds.checkBox(visibility_checkboxes[index], edit=True, value=new_visibility)

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

    if not selected_objects:
        cmds.warning("No objects selected. Please select at least one object to create a layer.")
        return

    if len(selected_objects) == 1:
        obj_name = selected_objects[0]

        if cmds.nodeType(obj_name) == 'transform':
            renamed_mesh = baking_tools_core.ucx_process(obj_name)
            print("Renamed Mesh:", renamed_mesh)

            # The UCX object is named 'UCX_SM_<original_name>'
            ucx_name = f"UCX_{renamed_mesh}"
            print("UCX Object Name:", ucx_name)

            # Check if the material 'UCX_M' already exists
            if not cmds.objExists('UCX_M'):
                print("Creating new material 'UCX_M'")
                ucx_material = cmds.shadingNode('lambert', asShader=True, name='UCX_M')
                shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=f'{ucx_material}SG')
                cmds.connectAttr(f'{ucx_material}.outColor', f'{shading_group}.surfaceShader', force=True)
                cmds.setAttr(f'{ucx_material}.color', 1, 0, 0, type='double3')
                cmds.setAttr(f'{ucx_material}.transparency', 0.75, 0.75, 0.75, type='double3')
            else:
                print("Using existing material 'UCX_M'")
                shading_group = cmds.listConnections('UCX_M', type='shadingEngine')[0]

            # Double-check if the UCX object exists before assigning the material
            if cmds.objExists(ucx_name):
                print(f"Assigning material 'UCX_M' to {ucx_name}")
                cmds.sets(ucx_name, edit=True, forceElement=shading_group)
            else:
                print(f"Error: UCX object '{ucx_name}' does not exist and cannot be assigned a material.")

            # Name the layer as the original object's name without appended
            layer_name = f"{obj_name}"

            # Create a new display layer with the determined name
            new_layer = cmds.createDisplayLayer(name=layer_name, empty=True)

            # Add the renamed static mesh and its UCX copy to the new display layer
            cmds.editDisplayLayerMembers(new_layer, [renamed_mesh, ucx_name])
        else:
            print(f"Error: The selected object '{obj_name}' is not of type 'transform'.")
    else:
        # If multiple objects are selected, generate a group-based layer name
        base_name = "group"
        existing_layers = cmds.ls(type="displayLayer")  # Get a list of existing display layers
        index = 1
        layer_name = f"{base_name}_{index}"  
        
        # Increment the index until a unique layer name is found
        while layer_name in existing_layers:
            index += 1
            layer_name = f"{base_name}_{index}"
        
        # Create a new display layer with the determined name
        new_layer = cmds.createDisplayLayer(name=layer_name, empty=True)
        
        # Call the new function to create UCX copies and groups for each selected object
        ucx_groups = baking_tools_core.ucx_process_mult(selected_objects)
        
        # Check if the material 'UCX_M' already exists
        if not cmds.objExists('UCX_M'):
            print("Creating new material 'UCX_M'")
            ucx_material = cmds.shadingNode('lambert', asShader=True, name='UCX_M')
            shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=f'{ucx_material}SG')
            cmds.connectAttr(f'{ucx_material}.outColor', f'{shading_group}.surfaceShader', force=True)
            cmds.setAttr(f'{ucx_material}.color', 1, 0, 0, type='double3')
            cmds.setAttr(f'{ucx_material}.transparency', 0.75, 0.75, 0.75, type='double3')
        else:
            print("Using existing material 'UCX_M'")
            shading_group = cmds.listConnections('UCX_M', type='shadingEngine')[0]
        
        # Add all original objects and their UCX copies to the display layer
        all_groups = []
        ucx_objects = [] 
        for static_mesh, ucx_copy, group in ucx_groups:
            # Add the UCX object to the list
            ucx_objects.append(ucx_copy)
            
             # Assign the UCX material
            cmds.sets(ucx_copy, edit=True, forceElement=shading_group)
            cmds.editDisplayLayerMembers(new_layer, [static_mesh, ucx_copy])
            
            # Collect the groups of the original objects and UCX for the larger group
            all_groups.append(group)
        
        # Group all smaller groups under a new larger group named after the display layer
        cmds.group(all_groups, name=f"{layer_name}_layer")

    # Update the UI to reflect the new layer
    update_display_layer_ui()

def rename_layer(layer, text_field):

    #Define new layer and group names
    new_name = cmds.textField(text_field, query=True, text=True)
    new_group_name = '{}_grp'.format(new_name)

    #If name not unique
    if cmds.objExists(new_name):
        cmds.warning(f"An object named '{new_name}' already exists. Choose a different name.")
    else:
        layer_members = cmds.editDisplayLayerMembers(layer, q=True)
        #Check that the member whose parent is the group is not a shape
        group_name = cmds.listRelatives(layer_members[0], parent=True)
        while cmds.listRelatives(group_name, parent=True):
            group_name = cmds.listRelatives(group_name, parent=True)

        #Rename
        cmds.rename(layer, new_name)
        cmds.rename(group_name, new_group_name)
        update_display_layer_ui()

def toggle_ucx_visibility(ucx_objects, visibility):
    """ Toggles the visibility of all UCX objects in the list. """
    for ucx in ucx_objects:
        if cmds.objExists(ucx):
            cmds.setAttr(ucx + ".visibility", visibility)

def toggle_all_ucx_visibility(layers, ucx_visibility_checkboxes):
    current_state = cmds.checkBox(ucx_visibility_checkboxes[-1], query=True, value=True)  

    # If it's checked, turn all UCX objects' visibility on, otherwise turn them off
    if current_state:
        new_visibility = True
    else:
        new_visibility = False

    # Iterate through layers to find and toggle UCX objects
    for index, layer in enumerate(layers):
        if layer == "defaultLayer":
            continue  # Skip the default layer
        
        # Get UCX objects in this layer
        layer_members = cmds.editDisplayLayerMembers(layer, q=True)
        ucx_objects = [obj for obj in layer_members if obj.startswith("UCX_")]

        if ucx_objects:
            # Set visibility for all UCX objects in the layer
            toggle_ucx_visibility(ucx_objects, new_visibility)
            cmds.checkBox(ucx_visibility_checkboxes[index], edit=True, value=new_visibility)

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

def move_layer_up(layer, layer_list):
    index = layer_list.index(layer)
    if index > 0:
        # Swap the displayOrder of the current layer with the one above it
        current_order = cmds.getAttr(f"{layer}.displayOrder")
        above_order = cmds.getAttr(f"{layer_list[index - 1]}.displayOrder")

        # Set the new displayOrder for both layers
        cmds.setAttr(f"{layer}.displayOrder", above_order)
        cmds.setAttr(f"{layer_list[index - 1]}.displayOrder", current_order)

        # Swap the layers in the list
        layer_list[index], layer_list[index - 1] = layer_list[index - 1], layer_list[index]
        
        new_layer = cmds.createDisplayLayer(name="NewLayer", empty=True)
        cmds.delete(new_layer)
        
        # Update the UI
        update_display_layer_ui()

def move_layer_down(layer, layer_list):
    index = layer_list.index(layer)
    if index < len(layer_list) - 1:
        # Swap the displayOrder of the current layer with the one below it
        current_order = cmds.getAttr(f"{layer}.displayOrder")
        below_order = cmds.getAttr(f"{layer_list[index + 1]}.displayOrder")

        # Set the new displayOrder for both layers
        cmds.setAttr(f"{layer}.displayOrder", below_order)
        cmds.setAttr(f"{layer_list[index + 1]}.displayOrder", current_order)

        # Swap the layers in the list
        layer_list[index], layer_list[index + 1] = layer_list[index + 1], layer_list[index]
        
        new_layer = cmds.createDisplayLayer(name="NewLayer", empty=True)
        cmds.delete(new_layer)
        
        # Update the UI
        update_display_layer_ui()

def create_display_layer_ui():
    # Delete the existing UI if it exists to avoid duplication
    if cmds.workspaceControl(DISPLAY_LAYER_WORKSPACE_CONTROL_NAME, exists=True):
        cmds.deleteUI(DISPLAY_LAYER_WORKSPACE_CONTROL_NAME, control=True)

    # Create the workspace control and set it to restore the previous state
    cmds.workspaceControl(
        DISPLAY_LAYER_WORKSPACE_CONTROL_NAME,
        label="Display Layer Editor",
        retain=False
        #loadImmediately=True  # Load the workspace immediately
    )

    BROWSE_BUTTON_NAME_DICT.clear()

    cmds.columnLayout(adjustableColumn=True)

    layer_dict = {}
    layer_list = cmds.ls(type="displayLayer")

    # Reorder the layers
    for layer in layer_list:
        layer_display_order_name = '{}.displayOrder'.format(layer)
        layer_dict[layer] = cmds.getAttr(layer_display_order_name)
    for layer, display_order in layer_dict.items():
        new_value = len(layer_list) - display_order - 1
        layer_list[new_value] = layer

    for layer in layer_list:
        BROWSE_BUTTON_NAME_DICT[layer] = '{}_browse_button'.format(layer)

    paths_dict = read_directory_from_file()

    #Controls for all
    cmds.rowLayout(numberOfColumns=9, adjustableColumn=True, columnAlign=(1, 'left'))
    cmds.text(label="All Display Layers", align='left', height=20)

    # Visibility all
    visibility_checkboxes = []
    visibility_checkboxes.append(cmds.checkBox(label="V", width=30,
                                           onCommand=lambda *args: toggle_all_visibility(layer_list, visibility_checkboxes),
                                           offCommand=lambda *args: toggle_all_visibility(layer_list, visibility_checkboxes)))

    #Display type all
    display_type_checkboxes = []
    if not display_type_checkboxes:
        display_type_checkboxes.append('')
    display_type_checkboxes[-1] = cmds.checkBox(label=' ', value=0, width=30)

     # UCX Visibility all
    ucx_visibility_checkboxes = []
    ucx_visibility_checkboxes.append(cmds.checkBox(label="UCX", width=45,
                                                   onCommand=lambda *args: toggle_all_ucx_visibility(layer_list, ucx_visibility_checkboxes),
                                                   offCommand=lambda *args: toggle_all_ucx_visibility(layer_list, ucx_visibility_checkboxes)))

    #Separators
    cmds.separator(width=30)
    cmds.separator(width=30)
    cmds.separator(width=30)

    #Browse all
    cmds.button(BROWSE_BUTTON_NAME_DICT['defaultLayer'], label="...", width=50, command=lambda *args, b=BROWSE_BUTTON_NAME_DICT['defaultLayer']: browse(b), annotation=paths_dict['defaultLayer'])

    #Export all
    cmds.button(label="Export all", width=100, command=lambda *args, l=layer_list: export_all_layers(l))

    cmds.setParent('..')

    for index, layer in enumerate(layer_list):
        if layer == "defaultLayer":
            continue  # Skip the default layer

        layer_row_layout = cmds.rowLayout(numberOfColumns=9, adjustableColumn=True, columnAlign=(1, 'left'))
        
        # Layer Name
        text_field = cmds.textField(width=100)
        cmds.textField(text_field, edit=True, text=layer, changeCommand=lambda *args, l=layer, tf=text_field: rename_layer(l, tf))

        # Visibility Checkbox
        visibility = cmds.getAttr(layer + ".visibility")
        visibility_checkboxes.insert(index, '')
        visibility_checkboxes[index] = cmds.checkBox(label="V", value=visibility, width=30, 
                      onCommand=lambda *args, l=layer: cmds.setAttr(l + ".visibility", 1), 
                      offCommand=lambda *args, l=layer: cmds.setAttr(l + ".visibility", 0))
        
        # Template/Reference Checkbox
        display_type = cmds.getAttr(layer + ".displayType")
        checkbox_label = " " if display_type == 0 else "T" if display_type == 1 else "R" if display_type == 2 else "T"
        display_type_checkboxes.insert(index,'')
        display_type_checkboxes[index] = cmds.checkBox(label=checkbox_label, value=(display_type != 0), width=30)

        # UCX Visibility (individual)
        layer_members = cmds.editDisplayLayerMembers(layer, q=True)
        ucx_objects = [obj for obj in layer_members if obj.startswith("UCX_")]

        if ucx_objects:
            # Get the visibility of the first UCX object (assuming all have the same visibility)
            ucx_visibility = cmds.getAttr(ucx_objects[0] + ".visibility")
            
            # Create the checkbox to control visibility of all UCX objects
            ucx_visibility_checkboxes.insert(index, '')
            ucx_visibility_checkboxes[index] = cmds.checkBox(label="UCX", value=ucx_visibility, width=45,
                                                             onCommand=lambda *args, ucx_list=ucx_objects: toggle_ucx_visibility(ucx_list, 1),
                                                             offCommand=lambda *args, ucx_list=ucx_objects: toggle_ucx_visibility(ucx_list, 0))
        else:
            ucx_visibility_checkboxes.insert(index, '')
            cmds.separator(width=45)

        # Color Box
        layer_color = get_layer_color(layer)
        color_box = cmds.iconTextButton(style='textOnly', label="", width=30, bgc=layer_color,
                                        command=lambda *args, l=layer: set_layer_color(l))  
        
        # Correctly reference the display type checkbox
        cmds.checkBox(display_type_checkboxes[index], edit=True,
                      onCommand=lambda *args, c=display_type_checkboxes[index], l=layer: toggle_display_type(l, c),
                      offCommand=lambda *args, c=display_type_checkboxes[index], l=layer: toggle_display_type(l, c))

        # Existing code that sets up the UI for each layer (skipping the default layer)
        #layer_row_layout = cmds.rowLayout(numberOfColumns=9, adjustableColumn=True, columnAlign=(1, 'left'))
        
        # Up Button
        if layer != layer_list[0]:  # No up button for the first layer
            cmds.button(label="↑", width=30, command=lambda *args, l=layer: move_layer_up(l, layer_list))
        else:
            cmds.separator(width=30)

        # Down Button
        if layer != layer_list[-2]:  # No down button for the last layer
            cmds.button(label="↓", width=30, command=lambda *args, l=layer: move_layer_down(l, layer_list))
        else:
            cmds.separator(width=30)

        # Ensure the correct initial label
        if display_type == 0:
            cmds.checkBox(display_type_checkboxes[index], edit=True, label=" ", value=False)
        elif display_type == 1:
            cmds.checkBox(display_type_checkboxes[index], edit=True, label="T", value=True)
        elif display_type == 2:
            cmds.checkBox(display_type_checkboxes[index], edit=True, label="R", value=True)

        # Color Picker
        if cmds.attributeQuery("overrideColorRGB", node=layer, exists=True):
            color = cmds.getAttr(layer + ".overrideColorRGB")[0]
            if color == (0.0, 0.0, 0.0):
                color = [.5, .5, .5]
        else:
            color = [0.5, 0.5, 0.5]  # Default color if not set

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

    # Correctly reference the all display type checkbox
    cmds.checkBox(display_type_checkboxes[-1], edit=True,
                  onCommand=lambda *args, c=display_type_checkboxes, l=layer_list: toggle_all_display_types(l, c),
                  offCommand=lambda *args, c=display_type_checkboxes, l=layer_list: toggle_all_display_types(l, c))
    
    # Add Layer Button
    cmds.button(label="Add Layer", command=add_layer)