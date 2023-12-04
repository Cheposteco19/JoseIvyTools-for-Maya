from maya import cmds
from uv_tools import core as uv_tools_core
import maya.mel as mm

WINDOW_NAME='uv_editing_tool_ui'
CAMERA_BASED_BUTTON_NAME='camera_based_button'
CUT_SEW_BUTTON_NAME='cut_sew_button'
UNFOLD_BUTTON_NAME='unfold_button'
AUTO_UNWRAP_BUTTON_NAME='auto_unwrap_button'
TILEABLE_1M_BUTTON_NAME='tileable_1m_button'
TILEABLE_2M_BUTTON_NAME='tileable_2m_button'
TILEABLE_CUSTOM_BUTTON_NAME='tileable_custom_button'
CUSTOM_DENSITY_FLOATBOX_NAME= 'custom_density_textbox'
CUSTOM_MAP_SIZE_INTBOX_NAME= 'custom_map_size_textbox'
RESET_MOVE_TOOL_BUTTON_NAME='reset_move_tool_button'
PRESERVE_UVS_CHECKBOX_NAME='preserve_UVs_checkbox'
GET_TEXEL_DENSITY_BUTTON_NAME='get_texel_density_button'

def show_ui():
    """Creates the window"""
    if cmds.window(WINDOW_NAME,query=True,exists=True):
        cmds.deleteUI(WINDOW_NAME)

    cmds.window(WINDOW_NAME, title='UV tools', widthHeight=(260,210))

    #Baked column
    cmds.columnLayout(adjustableColumn=True)
    cmds.rowLayout(numberOfColumns=2)
    cmds.columnLayout(adjustableColumn=True, backgroundColor=(.1, .1, .2))
    cmds.text(label='BAKED',font='boldLabelFont')
    cmds.button(CAMERA_BASED_BUTTON_NAME, label='Camera-based', command=uv_tools_core.camera_based)
    cmds.button(CUT_SEW_BUTTON_NAME, label='Cut/Sew\nTool', height=38, command=uv_tools_core.set_cut_sew_tool)
    cmds.button(UNFOLD_BUTTON_NAME, label='Unfold', height=47, command=uv_tools_core.unfold,annotation='unfold/orient shells/layout/uv selection')
    cmds.text(label='',height=47)
    cmds.setParent('..')

    #Tiled column
    cmds.columnLayout(adjustableColumn=True,backgroundColor=(.1,.2,.1))
    cmds.text(label='TILED', font='boldLabelFont')
    cmds.button(AUTO_UNWRAP_BUTTON_NAME, label='Automatic', command=uv_tools_core.auto_unwrap)
    cmds.rowLayout(numberOfColumns=2)

    #Density first column
    cmds.columnLayout(adjustableColumn=True)
    cmds.button(TILEABLE_1M_BUTTON_NAME, label='Tileable 1M\n(10.24|1024)',command=texel_density_1m)
    cmds.button(GET_TEXEL_DENSITY_BUTTON_NAME,label='Get',command=get_texel_density)
    cmds.text(label='Texel density\n(px/inch)')
    cmds.floatField(CUSTOM_DENSITY_FLOATBOX_NAME, value=10.24, precision=2)


    cmds.button(RESET_MOVE_TOOL_BUTTON_NAME, label='Reset Tools', command=uv_tools_core.reset_tools, width=10,annotation='reset move/rotate/scale tools')
    cmds.setParent('..')

    #Density second column
    cmds.columnLayout(adjustableColumn=True)
    cmds.button(TILEABLE_2M_BUTTON_NAME, label='Tileable 2M\n(10.24|2048)',command=texel_density_2m)
    cmds.button(TILEABLE_CUSTOM_BUTTON_NAME, label='Set',command=texel_density_custom)
    cmds.text(label='Map size', height=27)
    cmds.intField(CUSTOM_MAP_SIZE_INTBOX_NAME, value=4096)

    cmds.checkBox(PRESERVE_UVS_CHECKBOX_NAME, label="preserve UVs", onCommand=uv_tools_core.preserve_uvs, offCommand=uv_tools_core.dont_preserve_uvs, height=22)
    cmds.setParent('..')
    cmds.setParent('..')
    cmds.setParent('..')
    cmds.setParent('..')
    cmds.setParent('..')

    #Credits
    cmds.rowLayout(numberOfColumns=2,adjustableColumn=2)
    cmds.text(label='V 1.1.0')
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
    uv_tools_core.set_tileable_size(density, map_size)

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