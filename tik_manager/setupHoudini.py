import os
import hou

# find

selfLocation = os.path.dirname(os.path.abspath(__file__))
iconsLocation = os.path.join(selfLocation, "icons")

try:
    smShelf = hou.shelves.shelves()["SceneManager"]
except KeyError:
    smShelf = hou.shelves.newShelf(name="SceneManager", label="SceneManager")

smShelf.setTools([])

tools =[]

smScript = """
from tik_manager import SmHoudini
reload(SmHoudini)
SmHoudini.MainUI().show()
"""
smIcon = os.path.join(iconsLocation, "manager_ICON.png")

smTool = hou.shelves.newTool(name="SceneManager", label="SManager", script=smScript, icon=smIcon)

tools.append(smTool)


## add saveVersion button
avScript = """
from tik_manager import SmHoudini
SmHoudini.MainUI().saveAsVersionDialog()
"""
avIcon = os.path.join(iconsLocation, "saveVersion_ICON.png")

avTool = hou.shelves.newTool(name="SaveVersion", label="AddVersion", script=avScript, icon=avIcon)

tools.append(avTool)
smShelf.setTools(tools)
