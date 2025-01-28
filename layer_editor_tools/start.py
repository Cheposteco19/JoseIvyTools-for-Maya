from layer_editor_tools import ui as layer_editor_ui

try:
    layer_editor_ui.show_ui()

except ImportError:
    import traceback
    traceback.print_exc()
    cmds.warning("Failed to import 'layer_editor.ui'. Make sure the module is correctly installed and accessible.")
except AttributeError:
    cmds.warning("'show_ui' function not found in 'layer_editor.ui' module.")