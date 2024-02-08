from maya import cmds
import maya.mel as mm
from uv_tools import ui as uv_tools_ui

def select_objects(objects):
    """
    Goes to object mode and selects the objects
    Args:
        objects: To select

    """
    cmds.selectMode(object=True)
    cmds.select(objects, replace=True)

def get_objects(selected_items):
    """
    Gets the objects of the selection

    Args:
        selected_items:
    Returns:
        list of objects in the selection
    """
    if selected_items == []:
        cmds.warning('The selection is empty')
    objects = []
    for item in selected_items:
        if objects.append(item.split('.')[0]) not in objects:
            objects.append(item.split('.')[0])
    return objects

def clean_selection(objects,new_selection):
    """
    Clears the selection, and gets a new selection of the components of the objects
    Args:
        objects:
        new_selection:

    Returns:

    """
    cmds.select(clear=True)
    cmds.select(objects, replace=True)
    cmds.hilite(objects)
    cmds.select(new_selection, replace=True)

def auto_unwrap(*args):
    """
    Auto unwraps the selected objects and leaves the user with the objects selected

    Args:
        *args:

    Returns:

    """
    selected_items=cmds.ls(selection=True)

    objects = get_objects(selected_items)

    #Prevent user from selecting a vertex or edge
    if '.v' in selected_items[0]:
        cmds.warning('select faces or UVs')
        return
    elif '.e' in selected_items[0]:
        cmds.warning('select faces or UVs')
        return

    #Is the selection a UV shell
    elif '.map' in selected_items[0]:
        cmds.polyListComponentConversion(selected_items,fromUV=True,toFace=True)

    #Is the selection different than a face
    elif '.f' not in selected_items[0]:

        #Populate all object faces
        for item in objects:
            face_index = cmds.polyEvaluate(item, face=True) - 1
            faces = '{}.f[0:{}]'.format(item, face_index)
            cmds.polyAutoProjection(faces)

    # Orient shells
    mm.eval("texOrientShells;")

    # Layout
    cmds.u3dLayout(res=256, scl=1, spc=0.001953125, box=(0,1,0,1))

    #Select objects again
    clean_selection(objects,selected_items)

def camera_based(*args):
    """
    Quits whatever tool used prior and creates a camera based layout leaving the user with the objects selected
    Args:
        *args:

    Returns:

    """
    # Set the select tool
    cmds.SelectTool()

    # Get object from past selection
    cmds.selectMode(object=True)
    selected_items = cmds.ls(selection=True)

    faces=[]
    objects = get_objects(selected_items)

    #Populate faces
    for item in objects:
        face_index = cmds.polyEvaluate(item,face=True)-1
        faces.append('{}.f[0:{}]'.format(item,face_index))

    #Clean selection
    clean_selection(objects,faces)

    #Project the UVs
    cmds.polyProjection(type='Planar', mapDirection='p', constructionHistory=True)

    select_objects(objects)

def unfold(*args):
    """
    Quits the tool used prior, then unfolds, orient shells and layout leaving the user in UV mode with the UVs selected
    Args:
        *args:

    Returns:

    """

    #Set the select tool
    cmds.SelectTool()

    #Get object from past selection

    if cmds.selectType(query=True,edge=True):
        cmds.selectMode(object=True)
        print('Hello')

    #Unfold
    cmds.u3dUnfold(ite=1, p=0, bi=1, tf=1, ms=1024, rs=2)

    #Orient Shells
    mm.eval("texOrientShells;")

    #Layout
    cmds.u3dLayout(res=256, scl=1, spc=0.001953125, box=(0,1,0,1))

    #Set the user to UVmode
    cmds.selectMode(component=True)
    cmds.selectType(polymeshUV=True)

def set_cut_sew_tool(*args):
    """
    Turns on the cut/sew tool
    Args:
        *args:

    Returns:

    """
    cmds.SetCutSewUVTool()

def set_tileable_size(density,map_size):
    """
    Deletes history and freezes transformations
    Sets the selection to the specified texel density leaving the user in edge mode
    Deletes history and freezes transformations again
    Args:
        density:
        map_size:

    Returns:

    """
    selected_items = cmds.ls(selection=True)

    # Prevent user from selecting a vertex or edge
    if '.v' in selected_items[0]:
        cmds.warning('select objects, faces or UVs')
        return
    elif '.e' in selected_items[0]:
        cmds.warning('select objects, faces or UVs')
        return

    # Kill history and freeze numbers
    cmds.DeleteHistory()
    cmds.FreezeTransformations()

    uv_maps = []
    objects=get_objects(selected_items)
    edges=[]
    edge_index={}

    if '.f' in selected_items[0]:
        new_selection=cmds.polyListComponentConversion(selected_items,fromFace=True,toUV=True)
        clean_selection(objects,new_selection)
        selected_items = cmds.ls(selection=True)

    print(selected_items)

    #Populate map list and edge directory
    if '.map' not in selected_items[0]:
        for item in objects:
            map_index = cmds.polyEvaluate(item, uvcoord=True) - 1
            edge_index[item]=cmds.polyEvaluate(item, edge=True)
            uv_maps.append('{}.map[0:{}]'.format(item, map_index))
    else:
        uv_maps=selected_items

    #clean selection
    clean_selection(objects,uv_maps)

    #Set texel density
    mm.eval("texSetTexelDensity {} {};".format(density,map_size))

    #OrientShells
    mm.eval("texOrientShells;")

    #UnstackShells
    mm.eval("texUnstackShells 1;")

    #Kill history and freeze numbers
    cmds.DeleteHistory()
    cmds.FreezeTransformations()

    #Set the user to edgemode
    cmds.selectMode(component=True)
    cmds.selectType(edge=True)

    if '.map' not in selected_items[0]:

        #Get edges
        for object in edge_index:
            for edge in range(edge_index[object]):
                name='{}.e[{}]'.format(object,edge)
                edges.append(name)

        #Clean select edges
        clean_selection(objects,edges)

    else:
        clean_selection(objects, selected_items)

def reset_tools(*args):
    """
    Resets move, rotate and scale tools
    Args:
        *args:

    Returns:

    """
    cmds.resetTool('Move')
    cmds.resetTool('Rotate')
    cmds.resetTool('Scale')
    cmds.setToolTo('Rotate')
    cmds.setToolTo('Scale')
    cmds.setToolTo('Move')
    uv_tools_ui.uncheck_preserve_uvs()

def preserve_uvs(*args):
    """
    Sets to true the preserve UVs checkbox in tool settings
    Args:
        *args:

    Returns:

    """
    mm.eval('setTRSPreserveUVs true;')

def dont_preserve_uvs(*args):
    """
    Sets to false the preserve UVs checkbox in tool settings
    Args:
        *args:

    Returns:

    """
    mm.eval('setTRSPreserveUVs false;')