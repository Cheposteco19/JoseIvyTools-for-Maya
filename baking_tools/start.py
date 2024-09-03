from baking_tools import ui as bake_tester_ui

try:
    bake_tester_ui.show_ui()

except ImportError:
    import traceback
    traceback.print_exc()
    cmds.warning("Failed to import 'baking_tools.ui'. Make sure the module is correctly installed and accessible.")
except AttributeError:
    cmds.warning("'show_ui' function not found in 'baking_tools.ui' module.")