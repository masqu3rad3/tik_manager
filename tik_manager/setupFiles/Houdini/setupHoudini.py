import os
import hou

# find
selfLocation = os.path.dirname(os.path.abspath(__file__))
setupFolder = os.path.abspath(os.path.join(selfLocation, os.pardir))
tikManagerFolder = os.path.abspath(os.path.join(setupFolder, os.pardir))
iconsLocation = os.path.join(tikManagerFolder, "icons")

try:
    smShelf = hou.shelves.shelves()["TikManager"]
except KeyError:
    smShelf = hou.shelves.newShelf(name="TikManager", label="TikManager")

smShelf.setTools([])

tools =[]

smScript = """
from tik_manager import SmHoudini
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
# smShelf.setTools(tools)


## add imageViewer button
ivScript = """
from tik_manager import ImageViewer
tik_imageViewer = ImageViewer.MainUI().show()
"""
ivIcon = os.path.join(iconsLocation, "imageViewer_ICON.png")

ivTool = hou.shelves.newTool(name="ImageViewer", label="ImageViewer", script=ivScript, icon=ivIcon)

tools.append(ivTool)

## add projectMaterials button
pmScript = """
from tik_manager import projectMaterials
projectMaterials.MainUI().show()
"""
pmIcon = os.path.join(iconsLocation, "projectMaterials_ICON.png")

pmTool = hou.shelves.newTool(name="ProjectMaterials", label="ProjectMaterials", script=pmScript, icon=pmIcon)

tools.append(pmTool)

## add assetLibrary button
alScript = """
from tik_manager import projectMaterials
projectMaterials.MainUI().show()
"""
alIcon = os.path.join(iconsLocation, "assetLibrary_ICON.png")

alTool = hou.shelves.newTool(name="ProjectMaterials", label="ProjectMaterials", script=alScript, icon=alIcon)

tools.append(alTool)


smShelf.setTools(tools)
