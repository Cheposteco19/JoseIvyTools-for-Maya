from maya import cmds
from uv_tools import core as uv_tools_core
from uv_tools import ui as uv_tools_ui
from baking_tools import ui as baking_tools_ui

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

class export_tool_window(object):

    def __init__(self):
        print('bake_tool_created')

    def create_ui(self,*args):
        """

        Creates the window

        """
        paths_dict=baking_tools_ui.read_directory_from_file()

        #Auto-Unwrap
        cmds.columnLayout(adjustableColumn=True, columnOffset=('both',10))
        cmds.columnLayout(adjustableColumn=True, backgroundColor=BLUE)


        #Colapsable menu 1
        cmds.frameLayout('BAKED', collapsable=True, collapse=False, backgroundColor=DARK_BLUE, fn='boldLabelFont')
        cmds.checkBox(AUTOUNWRAP_CHECK_BOX_NAME, label="Auto-Unwrap Slot 1", annotation="auto-unwrap / unfold / kills history and numbers", highlightColor=DARK_BLUE)

        # Browse Low Export
        cmds.rowLayout(numberOfColumns=4,adjustableColumn=2)
        cmds.text(label='1 ')
        if paths_dict.get(LOW_POLY_PATH_TEXT_BOX_NAME) is not None:
            cmds.textField(LOW_POLY_PATH_TEXT_BOX_NAME, text=paths_dict[LOW_POLY_PATH_TEXT_BOX_NAME], backgroundColor=DARK_BLUE)
        else:
            cmds.textField(LOW_POLY_PATH_TEXT_BOX_NAME, backgroundColor=DARK_BLUE)
        cmds.button(label='...',command=baking_tools_ui.browse_low, backgroundColor=LIGHT_BLUE)
        cmds.button(label='Export LOW',command=baking_tools_ui.low_exportFBX,width=73, backgroundColor=LIGHT_BLUE, annotation='unlock normals / conditions normals')
        cmds.setParent('..')

        # Browse High Export
        cmds.rowLayout(numberOfColumns=4,adjustableColumn=2)
        cmds.text(label='2 ')
        if paths_dict.get(HIGH_POLY_PATH_TEXT_BOX_NAME) is not None:
            cmds.textField(HIGH_POLY_PATH_TEXT_BOX_NAME, text=paths_dict[HIGH_POLY_PATH_TEXT_BOX_NAME], backgroundColor=DARK_BLUE)
        else:
            cmds.textField(HIGH_POLY_PATH_TEXT_BOX_NAME, backgroundColor=DARK_BLUE)
        cmds.button(label='...',command=baking_tools_ui.browse_high, backgroundColor=LIGHT_BLUE)
        cmds.button(label='Export HIGH',command=baking_tools_ui.high_exportFBX, backgroundColor=LIGHT_BLUE)
        cmds.setParent('..')
        cmds.setParent('..')
        cmds.setParent('..')

        #Colapsable menu 2
        cmds.columnLayout(adjustableColumn=True, backgroundColor=GREEN)
        cmds.frameLayout('TILED',collapsable=True,collapse=True, backgroundColor=DARK_GREEN, fn='boldLabelFont')

        # Browse Extra Export 1
        cmds.rowLayout(numberOfColumns=4, adjustableColumn=2)
        cmds.text(label='1 ')
        if paths_dict.get(EXTRA_PATH_TEXT_BOX_NAME_1) is not None:
            cmds.textField(EXTRA_PATH_TEXT_BOX_NAME_1, text=paths_dict[EXTRA_PATH_TEXT_BOX_NAME_1], backgroundColor=DARK_GREEN)
        else:
            cmds.textField(EXTRA_PATH_TEXT_BOX_NAME_1, backgroundColor=DARK_GREEN)
        cmds.button(label='...', command=baking_tools_ui.browse_extra_1, backgroundColor=LIGHT_GREEN)
        cmds.button(label='Export', command=baking_tools_ui.extra_exportFBX1, backgroundColor=LIGHT_GREEN)
        cmds.setParent('..')

        # Browse Extra Export 2
        cmds.rowLayout(numberOfColumns=4, adjustableColumn=2)
        cmds.text(label='2 ')
        if paths_dict.get(EXTRA_PATH_TEXT_BOX_NAME_2) is not None:
            cmds.textField(EXTRA_PATH_TEXT_BOX_NAME_2, text=paths_dict[EXTRA_PATH_TEXT_BOX_NAME_2], backgroundColor=DARK_GREEN)
        else:
            cmds.textField(EXTRA_PATH_TEXT_BOX_NAME_2, backgroundColor=DARK_GREEN)
        cmds.button(label='...', command=baking_tools_ui.browse_extra_2, backgroundColor=LIGHT_GREEN)
        cmds.button(label='Export', command=baking_tools_ui.extra_exportFBX2, backgroundColor=LIGHT_GREEN)
        cmds.setParent('..')

        # Browse Extra Export 3
        cmds.rowLayout(numberOfColumns=4, adjustableColumn=2)
        cmds.text(label='3 ')
        if paths_dict.get(EXTRA_PATH_TEXT_BOX_NAME_3) is not None:
            cmds.textField(EXTRA_PATH_TEXT_BOX_NAME_3, text=paths_dict[EXTRA_PATH_TEXT_BOX_NAME_3], backgroundColor=DARK_GREEN)
        else:
            cmds.textField(EXTRA_PATH_TEXT_BOX_NAME_3, backgroundColor=DARK_GREEN)
        cmds.button(label='...', command=baking_tools_ui.browse_extra_3, backgroundColor=LIGHT_GREEN)
        cmds.button(label='Export', command=baking_tools_ui.extra_exportFBX3, backgroundColor=LIGHT_GREEN)
        cmds.setParent('..')

        # Browse Extra Export 4
        cmds.rowLayout(numberOfColumns=4, adjustableColumn=2)
        cmds.text(label='4 ')
        if paths_dict.get(EXTRA_PATH_TEXT_BOX_NAME_4) is not None:
            cmds.textField(EXTRA_PATH_TEXT_BOX_NAME_4, text=paths_dict[EXTRA_PATH_TEXT_BOX_NAME_4], backgroundColor=DARK_GREEN)
        else:
            cmds.textField(EXTRA_PATH_TEXT_BOX_NAME_4, backgroundColor=DARK_GREEN)
        cmds.button(label='...', command=baking_tools_ui.browse_extra_4, backgroundColor=LIGHT_GREEN)
        cmds.button(label='Export', command=baking_tools_ui.extra_exportFBX4, backgroundColor=LIGHT_GREEN)
        cmds.setParent('..')

        # Browse Extra Export 5
        cmds.rowLayout(numberOfColumns=4, adjustableColumn=2)
        cmds.text(label='5 ')
        if paths_dict.get(EXTRA_PATH_TEXT_BOX_NAME_5) is not None:
            cmds.textField(EXTRA_PATH_TEXT_BOX_NAME_5, text=paths_dict[EXTRA_PATH_TEXT_BOX_NAME_5], backgroundColor=DARK_GREEN)
        else:
            cmds.textField(EXTRA_PATH_TEXT_BOX_NAME_5, backgroundColor=DARK_GREEN)
        cmds.button(label='...', command=baking_tools_ui.browse_extra_5, backgroundColor=LIGHT_GREEN)
        cmds.button(label='Export', command=baking_tools_ui.extra_exportFBX5, backgroundColor=LIGHT_GREEN)
        cmds.setParent('..')

        # Browse Extra Export 6
        cmds.rowLayout(numberOfColumns=4, adjustableColumn=2)
        cmds.text(label='6 ')
        if paths_dict.get(EXTRA_PATH_TEXT_BOX_NAME_6) is not None:
            cmds.textField(EXTRA_PATH_TEXT_BOX_NAME_6, text=paths_dict[EXTRA_PATH_TEXT_BOX_NAME_6], backgroundColor=DARK_GREEN)
        else:
            cmds.textField(EXTRA_PATH_TEXT_BOX_NAME_6, backgroundColor=DARK_GREEN)
        cmds.button(label='...', command=baking_tools_ui.browse_extra_6, backgroundColor=LIGHT_GREEN)
        cmds.button(label='Export', command=baking_tools_ui.extra_exportFBX6, backgroundColor=LIGHT_GREEN)
        cmds.setParent('..')

        # Browse Extra Export 7
        cmds.rowLayout(numberOfColumns=4, adjustableColumn=2)
        cmds.text(label='7 ')
        if paths_dict.get(EXTRA_PATH_TEXT_BOX_NAME_7) is not None:
            cmds.textField(EXTRA_PATH_TEXT_BOX_NAME_7, text=paths_dict[EXTRA_PATH_TEXT_BOX_NAME_7],
                           backgroundColor=DARK_GREEN)
        else:
            cmds.textField(EXTRA_PATH_TEXT_BOX_NAME_7, backgroundColor=DARK_GREEN)
        cmds.button(label='...', command=baking_tools_ui.browse_extra_7, backgroundColor=LIGHT_GREEN)
        cmds.button(label='Export', command=baking_tools_ui.extra_exportFBX7, backgroundColor=LIGHT_GREEN)
        cmds.setParent('..')

        # Browse Extra Export 8
        cmds.rowLayout(numberOfColumns=4, adjustableColumn=2)
        cmds.text(label='8 ')
        if paths_dict.get(EXTRA_PATH_TEXT_BOX_NAME_8) is not None:
            cmds.textField(EXTRA_PATH_TEXT_BOX_NAME_8, text=paths_dict[EXTRA_PATH_TEXT_BOX_NAME_8],
                           backgroundColor=DARK_GREEN)
        else:
            cmds.textField(EXTRA_PATH_TEXT_BOX_NAME_8, backgroundColor=DARK_GREEN)
        cmds.button(label='...', command=baking_tools_ui.browse_extra_8, backgroundColor=LIGHT_GREEN)
        cmds.button(label='Export', command=baking_tools_ui.extra_exportFBX8, backgroundColor=LIGHT_GREEN)
        cmds.setParent('..')
        cmds.setParent('..')
        cmds.setParent('..')

        #Credits
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=2)
        cmds.text(label='V 1.2.0')
        cmds.text(label='GD67_JoseMunguia   ', align='right')

    def show_ui(self):
        #Initialize Unfold3D
        cmds.loadPlugin("Unfold3D.mll")

        # Delete old window
        if not cmds.workspaceControl(BAKE_WINDOW_NAME, exists=True):
            cmds.workspaceControl(BAKE_WINDOW_NAME, floating=True, label='Exporter', uiScript='export_tool_window().create_ui()', width=500, height=150, retain=True)

        cmds.workspaceControl(BAKE_WINDOW_NAME, edit=True, restore=True)
        cmds.workspaceControl(BAKE_WINDOW_NAME, edit=True, visible=True)


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
        cmds.text(label='V 1.2.0')
        cmds.text(label='GD67_JoseMunguia   ', align='right')

    def show_ui(self):
        # Initialize Unfold3D
        cmds.loadPlugin("Unfold3D.mll")
        if not cmds.workspaceControl(UV_TOOLOS_WINDOW_NAME, exists=True):
            cmds.workspaceControl(UV_TOOLOS_WINDOW_NAME, label='UV tools', width=291, height=255, retain=False,
                                  floating=True, uiScript='uv_tool_window().create_ui()')
        cmds.workspaceControl(UV_TOOLOS_WINDOW_NAME, edit=True, restore=True)
        cmds.workspaceControl(UV_TOOLOS_WINDOW_NAME, edit=True, visible=True)

