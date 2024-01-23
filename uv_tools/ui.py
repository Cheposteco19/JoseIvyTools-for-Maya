from maya import cmds
from uv_tools import core as uv_tools_core
import maya.mel as mm

WINDOW_NAME='uv_editing_tool_ui'
CAMERA_BASED_BUTTON_NAME='camera_based_button'
CUT_SEW_BUTTON_NAME='cut_sew_button'
UNFOLD_BUTTON_NAME='unfold_button'
STRAIGTEN_UVS_BUTTON_NAME='straighten_uvs_button'
STRAIGHTEN_UVS_VALUE_NAME='straighten_uvs_value'
STRAIGTEN_U_CHECKBOX_NAME= 'straighten_u_checkbox'
STRAIGTEN_V_CHECKBOX_NAME= 'straighten_v_checkbox'
STRAIGTEN_SHELL_BUTTON_NAME='straighten_shell_button'
AUTO_UNWRAP_BUTTON_NAME='auto_unwrap_button'
TILEABLE_1M_BUTTON_NAME='tileable_1m_button'
TILEABLE_2M_BUTTON_NAME='tileable_2m_button'
TILEABLE_CUSTOM_BUTTON_NAME='tileable_custom_button'
CUSTOM_DENSITY_FLOATBOX_NAME= 'custom_density_value'
CUSTOM_MAP_SIZE_INTBOX_NAME= 'custom_map_size_value'
RESET_MOVE_TOOL_BUTTON_NAME='reset_move_tool_button'
PRESERVE_UVS_CHECKBOX_NAME='preserve_UVs_checkbox'
GET_TEXEL_DENSITY_BUTTON_NAME='get_texel_density_button'

#Colors
TITLE_GREEN=(.5,.7,.5)
LIGHT_GREEN=(.2,.4,.2)
GREEN=(.2,.3,.2)
DARK_GREEN=(.1,.2,.1)
TITLE_BLUE=(.7,.7,1)
LIGHT_BLUE=(.2,.2,.4)
BLUE=(.2,.2,.3)
DARK_BLUE=(.1,.1,.2)

def show_ui():
    """Creates the window"""

    # Initialize Unfold3D
    cmds.loadPlugin("Unfold3D.mll")

    if cmds.window(WINDOW_NAME,query=True,exists=True):
        cmds.deleteUI(WINDOW_NAME)

    cmds.window(WINDOW_NAME, title='UV tools', widthHeight=(291,212))

    #Baked column
    cmds.columnLayout(adjustableColumn=True)
    cmds.rowLayout(numberOfColumns=2)
    cmds.columnLayout(adjustableColumn=True, backgroundColor=BLUE)
    cmds.text(label='BAKED',font='boldLabelFont', backgroundColor=TITLE_BLUE)
    cmds.button(CAMERA_BASED_BUTTON_NAME, label='Camera-based', command=uv_tools_core.camera_based, backgroundColor=LIGHT_BLUE)
    cmds.button(CUT_SEW_BUTTON_NAME, label='Cut/Sew Tool', command=uv_tools_core.set_cut_sew_tool, backgroundColor=LIGHT_BLUE)
    cmds.button(UNFOLD_BUTTON_NAME, label='Unfold', command=uv_tools_core.unfold,annotation='unfold / orient shells / layout / uv selection', backgroundColor=LIGHT_BLUE)

    #Gridify
    cmds.text(label='GRIDIFY',font='boldLabelFont', backgroundColor=DARK_BLUE)
    cmds.button(STRAIGTEN_UVS_BUTTON_NAME, label='Straighten\nUVs', backgroundColor=LIGHT_BLUE, command=straighten_uvs)
    cmds.rowLayout(numberOfColumns=3)
    cmds.floatField(STRAIGHTEN_UVS_VALUE_NAME, value=35, precision=2, backgroundColor=DARK_BLUE, width=35)
    cmds.checkBox(STRAIGTEN_U_CHECKBOX_NAME, label='U', highlightColor=DARK_BLUE, value=True, width=35)
    cmds.checkBox(STRAIGTEN_V_CHECKBOX_NAME, label='V', highlightColor=DARK_BLUE, value=True)
    cmds.setParent('..')
    cmds.button(STRAIGTEN_SHELL_BUTTON_NAME, label='Straighten\nShell', backgroundColor=LIGHT_BLUE, command=straighten_shell)
    cmds.setParent('..')

    #Tiled column
    cmds.columnLayout(adjustableColumn=True,backgroundColor=GREEN)
    cmds.text(label='TILED', font='boldLabelFont', backgroundColor=TITLE_GREEN)
    cmds.button(AUTO_UNWRAP_BUTTON_NAME, label='Automatic', command=uv_tools_core.auto_unwrap, backgroundColor=LIGHT_GREEN, annotation='auto-uwraps / orient shells / layout')

    #Preset Densities
    cmds.rowLayout(numberOfColumns=2)
    cmds.button(TILEABLE_1M_BUTTON_NAME, label='Tileable 1M\n(10.24|1024)',command=texel_density_1m, backgroundColor=LIGHT_GREEN, annotation='set texel density / orient shells / unstack shells / sets edge mode')
    cmds.button(TILEABLE_2M_BUTTON_NAME, label='Tileable 2M\n(10.24|2048)',command=texel_density_2m, backgroundColor=LIGHT_GREEN, annotation='set texel density / orient shells / unstack shells / sets edge mode', width=96)
    cmds.setParent('..')

    cmds.text(label='CUSTOM',font='boldLabelFont', backgroundColor=DARK_GREEN)
    cmds.rowLayout(numberOfColumns=2)

    #Density first column
    cmds.columnLayout(adjustableColumn=True)

    cmds.button(GET_TEXEL_DENSITY_BUTTON_NAME,label='Get',command=get_texel_density, backgroundColor=LIGHT_GREEN)
    cmds.text(label='Texel density\n(px/inch)')
    cmds.floatField(CUSTOM_DENSITY_FLOATBOX_NAME, value=10.24, precision=2, backgroundColor=DARK_GREEN)


    cmds.button(RESET_MOVE_TOOL_BUTTON_NAME, label='Reset Tools', command=uv_tools_core.reset_tools,annotation='reset move / rotate / scale tools', backgroundColor=LIGHT_GREEN)
    cmds.setParent('..')

    #Density second column
    cmds.columnLayout(adjustableColumn=True)

    cmds.button(TILEABLE_CUSTOM_BUTTON_NAME, label='Set',command=texel_density_custom, backgroundColor=LIGHT_GREEN)
    cmds.text(label='Map size', height=27)
    cmds.intField(CUSTOM_MAP_SIZE_INTBOX_NAME, value=4096, backgroundColor=DARK_GREEN)

    cmds.checkBox(PRESERVE_UVS_CHECKBOX_NAME, label="preserve UVs", onCommand=uv_tools_core.preserve_uvs, offCommand=uv_tools_core.dont_preserve_uvs, height=22, highlightColor=DARK_GREEN)
    cmds.setParent('..')
    cmds.setParent('..')
    cmds.separator(height=6)
    cmds.setParent('..')
    cmds.setParent('..')
    cmds.setParent('..')

    #Credits
    cmds.rowLayout(numberOfColumns=2,adjustableColumn=2)
    cmds.text(label='V 1.1.2')
    cmds.text(label='GD67_JoseMunguia   ', align='right')

    cmds.showWindow()

def texel_density_1m(*args):
    uv_tools_core.set_tileable_size(10.24, 1024)

def texel_density_2m(*args):
    uv_tools_core.set_tileable_size(10.24, 2048)

def texel_density_custom(*args):
    """Reads the user input for setting the new texel density for the selection"""
    density=cmds.floatField(CUSTOM_DENSITY_FLOATBOX_NAME, query=True, value=True)
    map_size=cmds.intField(CUSTOM_MAP_SIZE_INTBOX_NAME, query=True, value=True)
    uv_tools_core.set_simple_tileable_size(density, map_size)

def straighten_uvs(*args):
    """Reads the user input for straighten the UVs for the selection"""
    angle=cmds.floatField(STRAIGHTEN_UVS_VALUE_NAME, query=True, value=True)
    u_bool=cmds.checkBox(STRAIGTEN_U_CHECKBOX_NAME, query=True, value=True)
    v_bool = cmds.checkBox(STRAIGTEN_V_CHECKBOX_NAME, query=True, value=True)
    u_string = ''
    v_string = ''
    if u_bool==True:
        u_string='U'
    if v_bool==True:
        v_string='V'
    mm.eval('texStraightenUVs "{}{}" {};'.format(u_string,v_string,angle))

def straighten_shell(*args):
    """Reads the user input for straighten the UVs for the selection"""
    mm.eval('texStraightenShell;')

def uncheck_preserve_uvs():
    """

    Unchecks the preserve UV checkbox in the window

    """
    cmds.checkBox(PRESERVE_UVS_CHECKBOX_NAME,edit=True,value=False)

def get_texel_density(*args):
    """Gets the texel density of the selection and writes it in the texel density float box"""
    map_size=cmds.intField(CUSTOM_MAP_SIZE_INTBOX_NAME,query=True,value=True)
    texel_density=mm.eval("texGetTexelDensity(%i);" % map_size)
    cmds.floatField(CUSTOM_DENSITY_FLOATBOX_NAME,edit=True,value=texel_density)