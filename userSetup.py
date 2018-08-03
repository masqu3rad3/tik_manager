import os
import sys
import maya.utils
import maya.OpenMaya as OpenMaya

def initFolder(targetFolder):
    if targetFolder in sys.path:
        return
    if not os.path.isdir(targetFolder):
        print ('Path is not valid (%s)' % targetFolder)
    sys.path.append(targetFolder)

def smUpdate(*args):
    import sceneManager
    m = sceneManager.TikManager()
    m.regularSaveUpdate()


maya.utils.executeDeferred('initFolder("M:\\Projects\\__database\\scripts")')

maya.utils.executeDeferred('SMid = OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterSave, smUpdate)')
