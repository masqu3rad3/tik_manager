"""
Switches between DEV and SHARED system paths
"""

import sys
import maya.cmds as cmds

shareDir = 'M:\\Projects\\__database\\scripts'
devDir = 'C:\\Users\\User\\Documents\\maya\\scripts\\dev\\tik_manager'
delModules = ["tik_manager", "tik_manager.manager", "tik_manager.imageManager", "tik_manager.imageViewer", "tik_manager.__init__", "tik_manager._version"]

def devSwitch():
    for module in sys.modules.keys():
        for key in delModules:
            if key in module:
                try:
                    r = module
                    del sys.modules[module]
                    print ("%s removed from memory" % r)
                except KeyError:
                    pass

    if shareDir in sys.path:
        sys.path.remove(shareDir)
        sys.path.append(devDir)
        cmds.warning("DEV FOLDER is import folder")
        # print("DEV FOLDER is import folder")
        return
    elif devDir in sys.path:
        sys.path.remove(devDir)
        sys.path.append(shareDir)
        cmds.warning("SHARED FOLDER is import folder")
        return
    else:
        sys.path.append(shareDir)
        cmds.warning("DEV FOLDER is import folder")


devSwitch()