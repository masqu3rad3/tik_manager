import maya.cmds as mc
import os

selfLocation = os.path.dirname(os.path.abspath(__file__))
iconsLocation = os.path.join(selfLocation, "icons")
shelfName = "SceneManager"
labelBackground = (0, 0, 0, 0)
labelColour = (.9, .9, .9)

def addButton(label, command="", doubleCommand="", icon=None):
    if not icon:
        icon = "commandButton.png"
    mc.setParent(shelfName)
    mc.shelfButton(width=37, height=37, image=icon, l=label, command=command, dcc=doubleCommand, imageOverlayLabel="", olb=labelBackground, olc=labelColour)


## check if the shelf exists. If it is empty it
if mc.shelfLayout(shelfName , ex=1):
    if mc.shelfLayout(shelfName , q=1, ca=1): # empty inside
        for each in mc.shelfLayout(shelfName , q=1, ca=1):
            mc.deleteUI(each)
else:
    mc.shelfLayout(shelfName, p="ShelfLayout")

## add Manager button:

cmd = """
from tik_manager import manager
tik_sceneManager = manager.MainUI(scriptJob="tik_sceneManager")
tik_sceneManager.show()
"""
icon = os.path.join(iconsLocation, "manager_ICON.png")
if not os.path.isfile(icon):
    mc.warning("Icon cannot found - %s" %icon)
    icon = None
addButton("SceneManager", command=cmd, icon=icon )

## add saveVersion button
cmd = """
from tik_manager import manager
manager.MainUI().saveAsVersionDialog()
"""
icon = os.path.join(iconsLocation, "saveVersion_ICON.png")
if not os.path.isfile(icon):
    mc.warning("Icon cannot found - %s" %icon)
    icon = None
addButton("saveVersion", command=cmd, icon=icon )

## add imageManager button
cmd = """
from tik_manager import imageManager
tik_imageManager = imageManager.MainUI(scriptJob="tik_imageManager")
"""
icon = os.path.join(iconsLocation, "imageManager_ICON.png")
if not os.path.isfile(icon):
    mc.warning("Icon cannot found - %s" %icon)
    icon = None
addButton("imageManager", command=cmd, icon=icon )

## add imageViewer button
cmd = """
from tik_manager import imageViewer
tik_imageViewer = imageViewer.MainUI().show()
"""
icon = os.path.join(iconsLocation, "imageViewer_ICON.png")
if not os.path.isfile(icon):
    mc.warning("Icon cannot found - %s" %icon)
    icon = None
addButton("imageViewer", command=cmd, icon=icon )