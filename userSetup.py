from maya import cmds
from uv_tools import core as uv_tools_core
from uv_tools import ui as uv_tools_ui
from baking_tools import ui as baking_tools_ui
import maya.utils


#UV window component names
UV_TOOLOS_WINDOW_NAME= 'uv_editing_tool_ui'
STRAIGHTEN_UVS_VALUE_NAME='straighten_uvs_value'
STRAIGTEN_U_CHECKBOX_NAME= 'straighten_u_checkbox'
STRAIGTEN_V_CHECKBOX_NAME= 'straighten_v_checkbox'
TILEABLE_1M_BUTTON_NAME='tileable_1m_button'
TILEABLE_2M_BUTTON_NAME='tileable_2m_button'
CUSTOM_DENSITY_FLOATBOX_NAME= 'custom_density_value'
CUSTOM_MAP_SIZE_INTBOX_NAME= 'custom_map_size_value'
PRESERVE_UVS_CHECKBOX_NAME='preserve_UVs_checkbox'
WIREFRAME_CHECKBOX_NAME='wireframe_checkbox'

#Baking window components names
BAKE_WINDOW_NAME= 'bake_test_ui'
AUTOUNWRAP_CHECK_BOX_NAME= 'auto_unwrap_check_box'
LOW_POLY_PATH_TEXT_BOX_NAME='low_poly_path_text_box'
HIGH_POLY_PATH_TEXT_BOX_NAME='high_poly_path_text_box'
EXTRA_PATH_TEXT_BOX_NAME_1='extra_path_text_box_1'
EXTRA_PATH_TEXT_BOX_NAME_2='extra_path_text_box_2'
EXTRA_PATH_TEXT_BOX_NAME_3='extra_path_text_box_3'
EXTRA_PATH_TEXT_BOX_NAME_4='extra_path_text_box_4'
EXTRA_PATH_TEXT_BOX_NAME_5='extra_path_text_box_5'
EXTRA_PATH_TEXT_BOX_NAME_6='extra_path_text_box_6'
EXTRA_PATH_TEXT_BOX_NAME_7='extra_path_text_box_7'
EXTRA_PATH_TEXT_BOX_NAME_8='extra_path_text_box_8'
DOCK_CONTROL_NAME='bake_tester_dock_control'

#Colors
TITLE_GREEN=(.5,.7,.5)
LIGHT_GREEN=(.2,.4,.2)
GREEN=(.2,.3,.2)
DARK_GREEN=(.1,.2,.1)
TITLE_BLUE=(.7,.7,1)
LIGHT_BLUE=(.2,.2,.4)
BLUE=(.2,.2,.3)
DARK_BLUE=(.1,.1,.2)

LAYER_EDITOR_OPENED=False

if cmds.workspaceControl(BAKE_WINDOW_NAME, exists=True):
    cmds.deleteUI(BAKE_WINDOW_NAME)
if cmds.workspaceControl(UV_TOOLOS_WINDOW_NAME, exists=True):
    cmds.deleteUI(UV_TOOLOS_WINDOW_NAME)
    print('UV_tools_deleted')

class uv_tool_window(object):
    def __init__(self):
        print('uv_tool_created')

    def create_ui(self,*args):
        """Creates the window"""

        cmds.columnLayout(adjustableColumn=True)
        cmds.rowLayout(numberOfColumns=8)
        cmds.shelfButton(command=uv_tools_core.center_pivot, image="CenterPivot.png",
                         annotation="Resets the selected object's pivot to center")
        cmds.shelfButton(command=uv_tools_core.delete_history, image="DeleteHistory.png",
                         annotation="Delete construction history on the selected object(s)")
        cmds.shelfButton(command=uv_tools_core.freeze_transformations, image="FreezeTransform.png",
                         annotation="Freeze transformations of the selected object(s)")
        cmds.shelfButton(command=uv_tools_core.combine, image="polyUnite.png",
                         annotation="Combine the selected polygon objects into one single object")
        cmds.shelfButton(command=uv_tools_core.separate, image="polySeparate.png",
                         annotation="Combine the selected polygon objects into one single object")
        cmds.shelfButton(command=uv_tools_core.stack_shells, image="polyStackShell.png",
                         annotation="Stack selected UV shells on top of each other")
        cmds.shelfButton(command=uv_tools_core.randomize_shells, image="polyRandomizeShell.png",
                         annotation="Randomize UV shells translation")
        cmds.shelfButton(image="textureEditor.png", command=cmds.TextureViewWindow,
                         annotation="Opens the UV editor")
        cmds.setParent('..')

        # Baked column
        cmds.rowLayout(numberOfColumns=2)
        cmds.columnLayout(adjustableColumn=True, backgroundColor=BLUE)
        cmds.text(label='BAKED', font='boldLabelFont', backgroundColor=TITLE_BLUE)
        cmds.button(label='Camera-based', command=uv_tools_core.camera_based,
                    backgroundColor=LIGHT_BLUE)
        cmds.button(label='Cut/Sew Tool', command=uv_tools_core.set_cut_sew_tool,
                    backgroundColor=LIGHT_BLUE)
        cmds.button(label='Unfold', command=uv_tools_core.unfold,
                    annotation='unfold / orient shells / layout / uv selection', backgroundColor=LIGHT_BLUE)

        # Gridify
        cmds.text(label='GRIDIFY', font='boldLabelFont', backgroundColor=DARK_BLUE)
        cmds.button(label='Straighten\nShell', backgroundColor=LIGHT_BLUE,
                    command=uv_tools_ui.straighten_shell, height=44)
        cmds.rowLayout(numberOfColumns=3)
        cmds.floatField(STRAIGHTEN_UVS_VALUE_NAME, value=35, precision=2, backgroundColor=DARK_BLUE, width=35)
        cmds.checkBox(STRAIGTEN_U_CHECKBOX_NAME, label='U', highlightColor=DARK_BLUE, value=True, width=35)
        cmds.checkBox(STRAIGTEN_V_CHECKBOX_NAME, label='V', highlightColor=DARK_BLUE, value=True)
        cmds.setParent('..')
        cmds.button(label='Straighten\nUVs', backgroundColor=LIGHT_BLUE,
                    command=uv_tools_ui.straighten_uvs, height=34)
        cmds.setParent('..')

        # Tiled column
        cmds.columnLayout(adjustableColumn=True, backgroundColor=GREEN)
        cmds.text(label='TILED', font='boldLabelFont', backgroundColor=TITLE_GREEN)
        cmds.button(label='Automatic', command=uv_tools_core.auto_unwrap,
                    backgroundColor=LIGHT_GREEN, annotation='auto-uwraps / orient shells / layout')

        # Preset Densities
        cmds.rowLayout(numberOfColumns=2)
        cmds.button(label='Tileable 1M\n(10.24|1024)', command=uv_tools_ui.texel_density_1m,
                    backgroundColor=LIGHT_GREEN,
                    annotation='set texel density / orient shells / unstack shells / sets edge mode')
        cmds.button(label='Tileable 2M\n(10.24|2048)', command=uv_tools_ui.texel_density_2m,
                    backgroundColor=LIGHT_GREEN,
                    annotation='set texel density / orient shells / unstack shells / sets edge mode', width=96)
        cmds.setParent('..')

        cmds.text(label='CUSTOM', font='boldLabelFont', backgroundColor=DARK_GREEN)
        cmds.rowLayout(numberOfColumns=2)

        # Density first column
        cmds.columnLayout(adjustableColumn=True)

        cmds.button(label='Get', command=uv_tools_ui.get_texel_density,
                    backgroundColor=LIGHT_GREEN)
        cmds.text(label='Texel density\n(px/inch)', height=27)
        cmds.floatField(CUSTOM_DENSITY_FLOATBOX_NAME, value=10.24, precision=2, backgroundColor=DARK_GREEN)

        cmds.button(label='Reset\nTools', command=uv_tools_core.reset_tools,
                    annotation='reset move / rotate / scale tools', backgroundColor=LIGHT_GREEN, height=34)
        cmds.setParent('..')

        # Density second column
        cmds.columnLayout(adjustableColumn=True)

        cmds.button(label='Set', command=uv_tools_ui.texel_density_custom,
                    backgroundColor=LIGHT_GREEN)
        cmds.text(label='Map size', height=27)
        cmds.intField(CUSTOM_MAP_SIZE_INTBOX_NAME, value=4096, backgroundColor=DARK_GREEN)

        cmds.checkBox(PRESERVE_UVS_CHECKBOX_NAME, label="preserve UVs", onCommand=uv_tools_core.preserve_uvs,
                      offCommand=uv_tools_core.dont_preserve_uvs, highlightColor=DARK_GREEN)
        cmds.checkBox(WIREFRAME_CHECKBOX_NAME, label="wireframe", onCommand=uv_tools_core.wireframe_on,
                      offCommand=uv_tools_core.wireframe_off, highlightColor=DARK_GREEN, value=True)
        cmds.setParent('..')
        cmds.setParent('..')
        cmds.setParent('..')
        cmds.setParent('..')

        # Credits
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=2)
        cmds.text(label='V 1.3.0')
        cmds.text(label='GD67_JoseMunguia   ', align='right')
        print('UV UI content created')

    def show_ui(self):
        # Initialize Unfold3D
        print('UV show ui')
        cmds.loadPlugin("Unfold3D.mll")
        if not cmds.workspaceControl(UV_TOOLOS_WINDOW_NAME, exists=True):
            cmds.workspaceControl(UV_TOOLOS_WINDOW_NAME, label='UV tools', width=291, height=255, retain=False,
                                  floating=True, uiScript='uv_tool_window().create_ui()')
            print('UV did not exist')
        cmds.workspaceControl(UV_TOOLOS_WINDOW_NAME, edit=True, restore=True)
        cmds.workspaceControl(UV_TOOLOS_WINDOW_NAME, edit=True, visible=True)

#Layer editor
def load_layer_editor():
    print("Loading layer editor...")
    if not cmds.workspaceControl(baking_tools_ui.DISPLAY_LAYER_WORKSPACE_CONTROL_NAME, exists=True):
        print('Workspace didnt exist')
        cmds.workspaceControl(baking_tools_ui.DISPLAY_LAYER_WORKSPACE_CONTROL_NAME, label="Display Layer Editor",
                              retain=False, floating=True,
                              uiScript='baking_tools_ui.display_layer_ui().create_display_layer_ui()')

    # Create the workspace control and set it to restore the previous state
    else:
        print('Workspace existed')

    cmds.workspaceControl(baking_tools_ui.DISPLAY_LAYER_WORKSPACE_CONTROL_NAME, edit=True, restore=True)
    cmds.workspaceControl(baking_tools_ui.DISPLAY_LAYER_WORKSPACE_CONTROL_NAME, edit=True, visible=True)


def on_scene_change():
    print("Scene changed...")
    if not cmds.workspaceControl(baking_tools_ui.DISPLAY_LAYER_WORKSPACE_CONTROL_NAME, exists=True):
        return
    baking_tools_ui.update_display_layer_ui()

def create_script_jobs():
    print("Creating script jobs...")
    cmds.scriptJob(event=["NewSceneOpened", on_scene_change], protected=True)
    cmds.scriptJob(event=["SceneOpened", on_scene_change], protected=True)
    cmds.scriptJob(event=["SceneSaved", on_scene_change], protected=True)

def deferred_startup():
    print("Deferring startup...")
    #load_layer_editor()
    create_script_jobs()

# Use executeDeferred to ensure Maya is fully loaded
maya.utils.executeDeferred(deferred_startup)

print("userSetup script finished.")
