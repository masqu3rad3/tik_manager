import maya.cmds as mc
import os

selfLocation = os.path.dirname(os.path.abspath(__file__))
setupFolder = os.path.abspath(os.path.join(selfLocation, os.pardir))
tikManagerFolder = os.path.abspath(os.path.join(setupFolder, os.pardir))
iconsLocation = os.path.join(tikManagerFolder, "icons")
shelfName = "TikManager"
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
from tik_manager import SmMaya
tik_sceneManager = SmMaya.MainUI(callback="tik_sceneManager")
tik_sceneManager.show()
"""
icon = os.path.join(iconsLocation, "manager_ICON.png")
if not os.path.isfile(icon):
    mc.warning("Icon cannot found - %s" %icon)
    icon = None
addButton("SceneManager", command=cmd, icon=icon )

## add saveVersion button
cmd = """
from tik_manager import SmMaya
SmMaya.MainUI().saveAsVersionDialog()
"""
icon = os.path.join(iconsLocation, "saveVersion_ICON.png")
if not os.path.isfile(icon):
    mc.warning("Icon cannot found - %s" %icon)
    icon = None
addButton("saveVersion", command=cmd, icon=icon )

## add imageManager button
cmd = """
from tik_manager import ImMaya
tik_imageManager = ImMaya.MainUI(callback="tik_imageManager")
"""
icon = os.path.join(iconsLocation, "imageManager_ICON.png")
if not os.path.isfile(icon):
    mc.warning("Icon cannot found - %s" %icon)
    icon = None
addButton("imageManager", command=cmd, icon=icon )

## add imageViewer button
cmd = """
from tik_manager import ImageViewer
tik_imageViewer = ImageViewer.MainUI().show()
"""
icon = os.path.join(iconsLocation, "imageViewer_ICON.png")
if not os.path.isfile(icon):
    mc.warning("Icon cannot found - %s" %icon)
    icon = None
addButton("imageViewer", command=cmd, icon=icon )

## add createPreview button
cmd = """
from tik_manager import SmMaya
SmMaya.MayaManager().createPreview()
"""
dcmd = """
from tik_manager import SmMaya
SmMaya.MainUI().onCreatePreview()
"""
icon = os.path.join(iconsLocation, "takePreview_ICON.png")
if not os.path.isfile(icon):
    mc.warning("Icon cannot found - %s" %icon)
    icon = None
addButton("imageViewer", command=cmd, doubleCommand=dcmd, icon=icon)

## add projectMaterials button
cmd="""
from tik_manager import projectMaterials
projectMaterials.MainUI().show()
"""
icon = os.path.join(iconsLocation, "projectMaterials_ICON.png")
if not os.path.isfile(icon):
    mc.warning("Icon cannot found - %s" %icon)
    icon = None
addButton("projectMaterials", command=cmd, icon=icon)

## add assetLibrary button
cmd="""
from tik_manager import assetLibrary
assetLibrary.MainUI().show()
"""
icon = os.path.join(iconsLocation, "assetLibrary_ICON.png")
if not os.path.isfile(icon):
    mc.warning("Icon cannot found - %s" %icon)
    icon = None
addButton("assetLibrary", command=cmd, icon=icon )




# User Setup
# ----------
# Following lines should be added to the userSetup.py (without #'s)

# import os
# import sys
# import maya.utils
#
# def initFolder(targetFolder):
#     if targetFolder in sys.path:
#         return
#     if not os.path.isdir(targetFolder):
#         print ('Path is not valid (%s)' % targetFolder)
#     sys.path.append(targetFolder)
#
# def smUpdate(*args):
#    try:
#        from tik_manager import SmMaya
#        m = SmMaya.MayaManager()
#        m.saveCallback()
#    except:
#        pass
#
#
# maya.utils.executeDeferred('initFolder("M:\\Projects\\__database\\scripts")')
# maya.utils.executeDeferred('SMid = OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterSave, smUpdate)')

