from layer_editor_tools import core as layer_editor_tools_core
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

def exportFBX(layer, origin_checkboxes, layers):
    """
    Checks if auto unwrap is necessary, gets the user input path, saves it, and exports the FBX.
    Only performs the export if the "Move to Origin" checkbox for the individual layer is unchecked.
    Args:
        layer: which layer will the FBX be named after.
        origin_checkboxes: List of checkboxes corresponding to each layer.
        layers: List of layers.
    """
    # Check if "Move to Origin" checkbox for the current layer is checked
    origin_states = check_origin_states(layers, origin_checkboxes)
    
    if origin_states[layer]:
        toggle_layer_origin(layer, origin_checkboxes[layers.index(layer)], True)
        
    # Path handling and FBX export process
    paths_dict = save_paths_to_file()
    if all(value == '' for value in paths_dict.values()):
        cmds.warning("Please browse and select a folder to export the layer to")
        return
    if paths_dict[layer] == '':
        paths_dict[layer] = paths_dict['defaultLayer']
    path_to_export = paths_dict[layer]
    fbx = 'SM_{}'.format(layer)
    export_name_with_path = '{}/{}'.format(path_to_export, fbx)

    # Ensure FBX plugin is loaded
    if not cmds.pluginInfo('fbxmaya', query=True, loaded=True):
        cmds.loadPlugin('fbxmaya')

    # Get objects in the layer
    objects_in_layer = cmds.editDisplayLayerMembers(layer, query=True) or []
    if not objects_in_layer:
        cmds.warning(f"No objects found in layer {layer} for export")
        return

    # If it is the fist layer and it needs to unwrap
    if layer == layers[0]:
        if cmds.checkBox(AUTOUNWRAP_CHECK_BOX_NAME,query=True,value=True)==True:
            layer_editor_tools_core.auto_unwrap(objects_in_layer)
        layer_editor_tools_core.soft_texture_borders(objects_in_layer)

    # Select and export objects
    cmds.select(clear=True)
    cmds.select(objects_in_layer, replace=True)

    cmds.file(export_name_with_path, force=True, options='v=0;', type='FBX export', exportSelected=True, preserveReferences=True)

    # Move objects back to their original positions if they were moved to origin
    if origin_states[layer]:
        toggle_layer_origin(layer, origin_checkboxes[layers.index(layer)], False)
        
    print(f"Exported layer {layer} to {export_name_with_path}")

def export_all_layers(layer_list, origin_checkboxes):
    """
    Exports all layers to FBX. Only performs the export if the "Move to Origin" global checkbox is unchecked.
    Args:
        layer_list: List of layers to export.
        origin_checkboxes: List of checkboxes corresponding to each layer (including global).
    """
    # Check if the global "Move to Origin" checkbox is checked
    origin_states = check_origin_states(layer_list, origin_checkboxes)

    if origin_states['global']:
        toggle_all_origin(layer_list, origin_checkboxes)

    # Export each layer individually
    for layer in layer_list:
        if layer == 'defaultLayer':
            continue  # Skip the default layer
        exportFBX(layer, origin_checkboxes, layer_list)  # Call the modified exportFBX function for each layer

# Dictionary to store the original locators and positions for each group
original_locators = {}

def toggle_layer_origin(layer, checkbox, move_to_origin):
    """
    Toggle the position of the group in the layer between the origin and its original position.
    """

    def create_locator_at_origin():
        locator_name = cmds.spaceLocator(position=(0, 0, 0))[0]
        cmds.xform(locator_name, worldSpace=True, translation=(0, 0, 0))
        return locator_name

    def create_locator_at_group(group):
        locator_name = cmds.spaceLocator(name=f"tempLocator_{group}")[0]

        world_matrix = cmds.xform(group, query=True, matrix=True, worldSpace=True)

        # Extract the translation from the world matrix
        translation = (world_matrix[12], world_matrix[13], world_matrix[14])

        # Move the locator to the group's world space position
        cmds.xform(locator_name, translation=translation, worldSpace=True)

        return locator_name

    # Get the objects in the display layer
    objects_in_layer = cmds.editDisplayLayerMembers(layer, query=True)

    if not objects_in_layer:
        cmds.warning(f"No objects found in layer {layer}.")
        return

    # Filter out invalid objects
    valid_groups = [obj for obj in objects_in_layer if cmds.nodeType(obj) == 'transform']

    if not valid_groups:
        cmds.warning(f"No valid transform groups found in layer {layer}.")
        return

    if move_to_origin:
        origin_locator = create_locator_at_origin()
        
        # Query the locator's world-space position
        origin_position = cmds.xform(origin_locator, query=True, worldSpace=True, translation=True)

        for group in valid_groups:
            # Save the original position of the group before moving to origin
            if group not in original_locators:
                try:
                    # Create a locator at the group's original world space position
                    original_locators[group] = {
                        'locator': create_locator_at_group(group),
                        'translation': cmds.xform(group, query=True, worldSpace=True, translation=True),
                        'rotation': cmds.xform(group, query=True, worldSpace=True, rotation=True)
                    }
                    print(f"Saving original position for group {group}: {original_locators[group]}")
                except RuntimeError as e:
                    cmds.warning(f"Could not query original position for {group}: {e}")
                    continue  # Skip if we can't query the position

            cmds.xform(group, worldSpace=True, translation=origin_position)
            print(f"Moved group {group} to origin")

        # Delete the temporary origin locator
        cmds.delete(origin_locator)

    else:
        # Restore the groups to their original positions
        for group in valid_groups:
            if group in original_locators and cmds.objExists(group):
                try:
                    print(f"Restoring original position for group {group}: {original_locators[group]['translation']}")

                    # Restore both translation and rotation in world space
                    cmds.xform(group, worldSpace=True, translation=original_locators[group]['translation'])
                    cmds.xform(group, worldSpace=True, rotation=original_locators[group]['rotation'])
                    print(f"Restored group {group} to original position")

                    # Delete the locator created for this group
                    locator_to_delete = original_locators[group]['locator']
                    if cmds.objExists(locator_to_delete):
                        cmds.delete(locator_to_delete)

                    # Remove the group from original_locators after restoration
                    del original_locators[group]
                except RuntimeError as e:
                    cmds.warning(f"Could not restore original position for {group}: {e}")
                    continue  # Skip if we can't restore the position

def toggle_all_origin(layers, origin_checkboxes):
    # Check the current state of the global "Origin All" checkbox
    current_state = cmds.checkBox(origin_checkboxes[-1], query=True, value=True)
    move_to_origin = current_state

    # Loop through all layers and checkboxes, excluding the global checkbox
    for index, layer in enumerate(layers):
        if layer == "defaultLayer":
            continue

        # Update the origin state for each layer
        #toggle_layer_origin(layer, origin_checkboxes[index], move_to_origin)

        # Update the UI checkbox state to match the global checkbox
        cmds.checkBox(origin_checkboxes[index], edit=True, value=move_to_origin)

def check_origin_states(layers, origin_checkboxes):
    origin_states = {}

    # Loop through each layer's checkbox and check its state
    for index, layer in enumerate(layers):
        if layer == "defaultLayer":
            continue  

        # Query the state of the checkbox for each individual layer
        checkbox_state = cmds.checkBox(origin_checkboxes[index], query=True, value=True)
        origin_states[layer] = checkbox_state  

    # Check the global "Origin All" checkbox state
    global_checkbox_state = cmds.checkBox(origin_checkboxes[-1], query=True, value=True)
    origin_states["global"] = global_checkbox_state

    return origin_states

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

    for obj_name in selected_objects:
        if cmds.nodeType(obj_name) != 'transform':
            cmds.warning(f"Skipping {obj_name}: Not a valid transform node.")
            continue

        # Define names
        static_mesh = f"SM_{obj_name}"
        ucx_group_name = f"UCX_{obj_name}_grp"
        ucx_mesh_name = f"UCX_SM_{obj_name}"
        main_group = f"{obj_name}_grp"

        # Rename the original object to include SM_ prefix
        if not cmds.objExists(static_mesh):
            cmds.rename(obj_name, static_mesh)

        # Create UCX group if it does not exist
        if not cmds.objExists(ucx_group_name):
            cmds.group(empty=True, name=ucx_group_name)
            print(f"Created UCX group: {ucx_group_name}")

        # Find existing UCX objects that match either "UCX_<mesh>" or "UCX_SM_<mesh>"
        existing_ucx_objects = cmds.ls(f"UCX_{obj_name}", f"UCX_SM_{obj_name}", type="transform")

        for ucx_object in existing_ucx_objects:
            # Ensure it is inside the UCX group
            current_parent = cmds.listRelatives(ucx_object, parent=True)
            if not current_parent or current_parent[0] != ucx_group_name:
                cmds.parent(ucx_object, ucx_group_name)
                print(f"Moved {ucx_object} into {ucx_group_name}.")

            # If it is named "UCX_<mesh>" instead of "UCX_SM_<mesh>", rename it
            if ucx_object == f"UCX_{obj_name}":
                ucx_object_renamed = cmds.rename(ucx_object, ucx_mesh_name)
                print(f"Renamed {ucx_object} to {ucx_object_renamed}.")

        # Ensure material 'UCX_M' exists
        if not cmds.objExists('UCX_M'):
            print("Creating new material 'UCX_M'")
            ucx_material = cmds.shadingNode('lambert', asShader=True, name='UCX_M')
            shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=f'{ucx_material}SG')
            cmds.connectAttr(f'{ucx_material}.outColor', f'{shading_group}.surfaceShader', force=True)
            cmds.setAttr(f'{ucx_material}.color', 1, 0, 0, type='double3')
            cmds.setAttr(f'{ucx_material}.transparency', 0.75, 0.75, 0.75, type='double3')
        else:
            shading_group = cmds.listConnections('UCX_M', type='shadingEngine')[0]

        # Apply material if UCX mesh exists
        if cmds.objExists(ucx_mesh_name):
            cmds.sets(ucx_mesh_name, edit=True, forceElement=shading_group)
            print(f"Applied material 'UCX_M' to {ucx_mesh_name}")

        # Ensure the main group exists and parent objects correctly
        if not cmds.objExists(main_group):
            cmds.group(static_mesh, ucx_group_name, name=main_group)
            print(f"Created main group {main_group} containing {static_mesh} and {ucx_group_name}")
        else:
            # Ensure objects are inside the main group
            if not cmds.listRelatives(static_mesh, parent=True) or cmds.listRelatives(static_mesh, parent=True)[0] != main_group:
                cmds.parent(static_mesh, main_group)
                print(f"Added {static_mesh} to {main_group}")
            if not cmds.listRelatives(ucx_group_name, parent=True) or cmds.listRelatives(ucx_group_name, parent=True)[0] != main_group:
                cmds.parent(ucx_group_name, main_group)
                print(f"Added {ucx_group_name} to {main_group}")

        # 🌟 Fix: **Layer Name is now the Mesh Name**
        layer_name = obj_name  # Use mesh name as layer name
        if not cmds.objExists(layer_name):
            new_layer = cmds.createDisplayLayer(name=layer_name, empty=True)
        else:
            new_layer = layer_name

        # Add the main group to the display layer
        cmds.editDisplayLayerMembers(new_layer, main_group)

    # Update UI
    update_display_layer_ui()

def rename_layer(layer, text_field):
    """
    Renames the display layer, the associated main group, and all relevant meshes while keeping the UCX group format consistent.
    """
    # Get the new name from the user input
    new_name = cmds.textField(text_field, query=True, text=True)

    # Define new names based on the new input
    new_main_group = f"{new_name}_grp"
    new_static_mesh = f"SM_{new_name}"
    new_ucx_group = f"UCX_{new_name}_grp"
    new_ucx_mesh = f"UCX_SM_{new_name}"  # Expected correct UCX mesh name

    # Ensure the name is unique
    if cmds.objExists(new_name):
        cmds.warning(f"An object named '{new_name}' already exists. Choose a different name.")
        return

    # Get members of the current layer
    layer_members = cmds.editDisplayLayerMembers(layer, query=True) or []
    if not layer_members:
        cmds.warning(f"No objects found in layer {layer}.")
        return

    # Identify the main group and UCX group
    main_group = None
    ucx_group = None

    for obj in layer_members:
        if obj.endswith("_grp") and not obj.startswith("UCX_"):
            main_group = obj
        elif obj.startswith("UCX_") and obj.endswith("_grp"):
            ucx_group = obj

    if not main_group:
        cmds.warning(f"Could not find a valid main group in layer {layer}.")
        return

    # Find Static Mesh inside the main group
    children = cmds.listRelatives(main_group, children=True, fullPath=False) or []
    static_mesh = None
    ucx_mesh = None

    for obj in children:
        if obj.startswith("SM_"):
            static_mesh = obj
        elif obj.startswith("UCX_SM_") or obj.startswith("UCX_"):  # Identify UCX mesh
            ucx_mesh = obj

    # Rename the display layer
    cmds.rename(layer, new_name)

    # Rename the main group
    try:
        main_group_renamed = cmds.rename(main_group, new_main_group)
    except RuntimeError:
        cmds.warning(f"Could not rename main group '{main_group}' to '{new_main_group}'.")
        return

    # Rename Static Mesh
    if static_mesh:
        try:
            static_mesh_renamed = cmds.rename(static_mesh, new_static_mesh)
        except RuntimeError:
            cmds.warning(f"Could not rename static mesh '{static_mesh}' to '{new_static_mesh}'.")
            return
    else:
        static_mesh_renamed = None

    # Fix: Ensure UCX Group Exists & Rename it Correctly**
    if ucx_group:
        try:
            ucx_group_renamed = cmds.rename(ucx_group, new_ucx_group)
        except RuntimeError:
            cmds.warning(f"Could not rename UCX group '{ucx_group}' to '{new_ucx_group}'.")
            return
    else:
        # If UCX group does not exist, create one
        try:
            ucx_group_renamed = cmds.group(empty=True, name=new_ucx_group)
        except RuntimeError:
            cmds.warning(f"Could not create UCX group '{new_ucx_group}'.")
            return

    # Fix: Ensure We Rename the Correct UCX Mesh**
    if ucx_group_renamed:
        # Get all children inside the UCX group
        ucx_children = cmds.listRelatives(ucx_group_renamed, children=True, fullPath=False) or []

        for obj in ucx_children:
            if obj.startswith("UCX_SM_") or obj.startswith("UCX_"):
                try:
                    new_name_for_ucx_mesh = f"UCX_SM_{new_name}"
                    cmds.rename(obj, new_name_for_ucx_mesh)
                    print(f"Renamed UCX mesh '{obj}' to '{new_name_for_ucx_mesh}'")
                except RuntimeError:
                    cmds.warning(f"Could not rename UCX mesh '{obj}' to '{new_name_for_ucx_mesh}'.")
                break  # Stop after renaming the first valid UCX mesh

    # Refresh UI
    update_display_layer_ui()

"""def rename_layer_popup(layer):

    window = cmds.window(title="Rename Layer", widthHeight=(300, 130), sizeable=False)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=10, columnAlign="center", columnAttach=('both', 10))
    cmds.text(label="Enter New Layer Name", align='center', font='boldLabelFont', height = 30)

    # text field for user input
    text_field = cmds.textField(placeholderText="Enter new layer name...", width=280)
    cmds.rowLayout(numberOfColumns=2, columnAttach=[(1, 'right', 5), (2, 'left', 5)], adjustableColumn=True, columnWidth=[(1, 140), (2, 140)])

    # Call rename_layer when the user confirms
    def on_confirm(*args):
        rename_layer(layer, text_field)
        cmds.deleteUI(window, window=True)  # Close the window

    # Add Rename and Cancel buttons
    cmds.button(label="Rename", command=on_confirm, width=120, height=30)
    cmds.button(label="Cancel", command=lambda *args: cmds.deleteUI(window, window=True), width=120, height=30)
    
    cmds.showWindow(window)"""

def toggle_sm_visibility(sm_objects, visibility):
    """ Toggles the visibility of all SM objects in the list. """
    for sm in sm_objects:
        if cmds.objExists(sm):
            cmds.setAttr(sm + ".visibility", visibility)

def toggle_all_sm_visibility(layers, sm_visibility_checkboxes):
    current_state = cmds.checkBox(sm_visibility_checkboxes[-1], query=True, value=True)

    # If it's checked, turn all SM objects' visibility on, otherwise turn them off
    if current_state:
        new_visibility = True
    else:
        new_visibility = False

    # Iterate through layers to find and toggle SM objects
    for index, layer in enumerate(layers):
        if layer == "defaultLayer":
            continue  # Skip the default layer

        # Get SM objects in this layer
        layer_members = cmds.editDisplayLayerMembers(layer, q=True)
        sm_objects = [obj for obj in layer_members if obj.startswith("SM_")]

        if sm_objects:
            # Set visibility for all SM objects in the layer
            toggle_sm_visibility(sm_objects, new_visibility)
            cmds.checkBox(sm_visibility_checkboxes[index], edit=True, value=new_visibility)

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
    display_layer_ui().open_ui()

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

class display_layer_ui(object):
    def __init__(self):
        print('display layer ui constructed')

    def open_ui(self):
        # Delete the existing UI if it exists to avoid duplication
        if not cmds.workspaceControl(DISPLAY_LAYER_WORKSPACE_CONTROL_NAME, exists=True):
            # Create the workspace control and set it to restore the previous state
            cmds.workspaceControl(DISPLAY_LAYER_WORKSPACE_CONTROL_NAME, label="Display Layer Editor", retain=False, floating=True,
                                  uiScript='layer_editor_tools_ui.display_layer_ui().create_display_layer_ui()')
        cmds.workspaceControl(DISPLAY_LAYER_WORKSPACE_CONTROL_NAME, edit=True, restore=True)
        cmds.workspaceControl(DISPLAY_LAYER_WORKSPACE_CONTROL_NAME, edit=True, visible=True)

    def create_display_layer_ui(self):

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

        # Controls for all
        cmds.rowLayout(numberOfColumns=11, adjustableColumn=True, columnAlign=(1, 'left'))
        cmds.text(label="All Layers", align='center', height=20)

        # Visibility all
        visibility_checkboxes = []
        visibility_checkboxes.append(cmds.checkBox(label="V", width=30, annotation='All Visibility',
                                                   onCommand=lambda *args: toggle_all_visibility(layer_list,
                                                                                                 visibility_checkboxes),
                                                   offCommand=lambda *args: toggle_all_visibility(layer_list,
                                                                                                  visibility_checkboxes)))

        # Display type all
        display_type_checkboxes = []
        if not display_type_checkboxes:
            display_type_checkboxes.append('')
        display_type_checkboxes[-1] = cmds.checkBox(label=' ', value=0, width=30,
                                                    annotation='All Display Type\nNormal/Transparent/Reference')

        # SM Visibility all
        sm_visibility_checkboxes = []
        sm_visibility_checkboxes.append(cmds.checkBox(label="SM", width=45, annotation='All Static Mesh Visibility',
                                                      onCommand=lambda *args: toggle_all_sm_visibility(layer_list,
                                                                                                       sm_visibility_checkboxes),
                                                      offCommand=lambda *args: toggle_all_sm_visibility(layer_list,
                                                                                                        sm_visibility_checkboxes)))

        # UCX Visibility all
        ucx_visibility_checkboxes = []
        ucx_visibility_checkboxes.append(cmds.checkBox(label="UCX", width=45, annotation='All UCX Visibility',
                                                       onCommand=lambda *args: toggle_all_ucx_visibility(layer_list,
                                                                                                         ucx_visibility_checkboxes),
                                                       offCommand=lambda *args: toggle_all_ucx_visibility(layer_list,
                                                                                                          ucx_visibility_checkboxes)))

        # Separators
        cmds.separator(width=30)
        cmds.separator(width=30)
        cmds.separator(width=30)
        
        
        # Origin Checkbox all
        origin_checkboxes = []
        origin_checkboxes.append(cmds.checkBox(label="Origin", width=60, annotation='Move All to Origin',
                                       onCommand=lambda *args: toggle_all_origin(layer_list, origin_checkboxes),
                                       offCommand=lambda *args: toggle_all_origin(layer_list, origin_checkboxes)))

        # Browse all
        cmds.button(BROWSE_BUTTON_NAME_DICT['defaultLayer'], label="...", width=50,
                    command=lambda *args, b=BROWSE_BUTTON_NAME_DICT['defaultLayer']: browse(b),
                    annotation=paths_dict['defaultLayer'])

        # Export all
        cmds.button(label="Export All", width=100, command=lambda *args, l=layer_list: export_all_layers(layer_list, origin_checkboxes))

        cmds.setParent('..')

        for index, layer in enumerate(layer_list):
            if layer == "defaultLayer":
                continue  # Skip the default layer

            layer_row_layout = cmds.rowLayout(numberOfColumns=11, adjustableColumn=True, columnAlign=(1, 'left'))

            # Layer Name
            text_field = cmds.textField(width=100)
            cmds.textField(text_field, edit=True, text=layer,
                           changeCommand=lambda *args, l=layer, tf=text_field: rename_layer(l, tf))

            # Visibility Checkbox
            visibility = cmds.getAttr(layer + ".visibility")
            visibility_checkboxes.insert(index, '')
            visibility_checkboxes[index] = cmds.checkBox(label="V", value=visibility, width=30, annotation='Visibility',
                                                         onCommand=lambda *args, l=layer: cmds.setAttr(
                                                             l + ".visibility", 1),
                                                         offCommand=lambda *args, l=layer: cmds.setAttr(
                                                             l + ".visibility", 0))

            # Template/Reference Checkbox
            display_type = cmds.getAttr(layer + ".displayType")
            checkbox_label = " " if display_type == 0 else "T" if display_type == 1 else "R" if display_type == 2 else "T"
            display_type_checkboxes.insert(index, '')
            display_type_checkboxes[index] = cmds.checkBox(label=checkbox_label, value=(display_type != 0), width=30,
                                                           annotation='Display Type\nNormal/Transparent/Reference')

            # SM Visibility (individual)
            layer_members = cmds.editDisplayLayerMembers(layer, q=True)
            sm_objects = [obj for obj in layer_members if obj.startswith("SM_")]

            if sm_objects:
                # Get the visibility of the first SM object (assuming all have the same visibility)
                sm_visibility = cmds.getAttr(sm_objects[0] + ".visibility")

                # Create the checkbox to control visibility of all SM objects
                sm_visibility_checkboxes.insert(index, '')
                sm_visibility_checkboxes[index] = cmds.checkBox(label="SM", value=sm_visibility, width=45,
                                                                annotation='Static Mesh Visibility',
                                                                onCommand=lambda *args,
                                                                                 sm_list=sm_objects: toggle_sm_visibility(
                                                                    sm_list, 1),
                                                                offCommand=lambda *args,
                                                                                  sm_list=sm_objects: toggle_sm_visibility(
                                                                    sm_list, 0))
            else:
                sm_visibility_checkboxes.insert(index, '')
                cmds.separator(width=45)

            # UCX Visibility (individual)
            layer_members = cmds.editDisplayLayerMembers(layer, q=True)
            ucx_objects = [obj for obj in layer_members if obj.startswith("UCX_")]

            if ucx_objects:
                # Get the visibility of the first UCX object (assuming all have the same visibility)
                ucx_visibility = cmds.getAttr(ucx_objects[0] + ".visibility")

                # Create the checkbox to control visibility of all UCX objects
                ucx_visibility_checkboxes.insert(index, '')
                ucx_visibility_checkboxes[index] = cmds.checkBox(label="UCX", value=ucx_visibility, width=45,
                                                                 annotation='UCX Visibility',
                                                                 onCommand=lambda *args,
                                                                                  ucx_list=ucx_objects: toggle_ucx_visibility(
                                                                     ucx_list, 1),
                                                                 offCommand=lambda *args,
                                                                                   ucx_list=ucx_objects: toggle_ucx_visibility(
                                                                     ucx_list, 0))
            else:
                ucx_visibility_checkboxes.insert(index, '')
                cmds.separator(width=45)

            # Color Box
            layer_color = get_layer_color(layer)
            color_box = cmds.iconTextButton(style='textOnly', label="", width=30, bgc=layer_color,
                                            annotation='Layer Color',
                                            command=lambda *args, l=layer: set_layer_color(l))

            # Correctly reference the display type checkbox
            cmds.checkBox(display_type_checkboxes[index], edit=True,
                          onCommand=lambda *args, c=display_type_checkboxes[index], l=layer: toggle_display_type(l, c),
                          offCommand=lambda *args, c=display_type_checkboxes[index], l=layer: toggle_display_type(l, c))

            # Up Button
            if layer != layer_list[0]:  # No up button for the first layer
                cmds.button(label="▲", width=30, command=lambda *args, l=layer: move_layer_up(l, layer_list))
            else:
                cmds.separator(width=30)

            # Down Button
            if layer != layer_list[-2]:  # No down button for the last layer
                cmds.button(label="▼", width=30, command=lambda *args, l=layer: move_layer_down(l, layer_list))
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

            # Origin Checkbox for each layer
            origin_checkboxes.insert(index, '')
            origin_checkboxes[index] = cmds.checkBox(label="Origin", width=60, annotation='Move to Origin',
                                        onCommand=lambda *args, l=layer: toggle_layer_origin(l, origin_checkboxes[index], True),
                                        offCommand=lambda *args, l=layer: toggle_layer_origin(l, origin_checkboxes[index], False))

            # Browse button
            cmds.button(BROWSE_BUTTON_NAME_DICT[layer], label="...", width=50,
                        command=lambda *args, b=BROWSE_BUTTON_NAME_DICT[layer]: browse(b), annotation=paths_dict[layer])

            # Export Button
            cmds.button(label="Export", width=100, command=lambda *args, l=layer: exportFBX(l, origin_checkboxes, layer_list))

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

        # Add "Update" Button
        cmds.separator(height=10, style='none')  # Space before the button
        cmds.button(label="Update", backgroundColor=(0.3, 0.3, 0.3), 
        command=lambda *args: update_display_layer_ui(), annotation="Refresh the Display Layer UI")

        # Credits
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=2)
        cmds.text(label='V 3.0.0')
        cmds.text(label='GD67_JoseMunguia & GD68_IvyMedina   ', align='right')