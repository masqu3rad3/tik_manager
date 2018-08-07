"""
Switches between DEV and SHARED system paths
"""

import sys
import maya.cmds as cmds

shareDir = 'M:\\Projects\\__database\\scripts'
devDir = 'C:\\Users\\User\\Documents\\maya\\scripts\\dev\\tik_manager'


def devSwitch():
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