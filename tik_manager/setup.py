import sys
import os
import shutil
import psutil
import ctypes  # An included library with Python install.



def checkIntegrity():
    networkDir = os.path.dirname(os.path.abspath(__file__))
    fileList = ["__init__.pyc",
                "_version.pyc",
                "ImMaya.pyc",
                "IvMaya.pyc",
                "IvStandalone.pyc",
                "pyseq.pyc",
                "Qt.pyc",
                "SmHoudini.pyc",
                "SmMaya.pyc",
                "SmRoot.pyc",
                "SmStandalone.pyc",
                "SubmitMayaToDeadlineCustom.mel",
                "adminPass.psw"
                ]
    # for file in fileList:
    #     if not os.path.isfile(os.path.join(networkDir, file)):
    #
    #         raise Exception ("MISSING FILE: %s" %file)
    #
    # for p in psutil.process_iter():
    #     # if "houdini" in p.name():
    #     #
    #     #     msg = "houdini is running"
    #     #     ctypes.windll.user32.MessageBoxA(0, msg, "Cannot continue", 0)
    #     if "houdini" in p.name():
    #
    #         msg = "Houdini is running exit Houdini and hit ok to continue"
    #         ret = ctypes.windll.user32.MessageBoxA(0, msg, "Setup Cannot Continue", 1)
    #         if ret == 0: #OK
    # houdiniInstance = checkRuninngInstances("houdini")
    # if houdiniInstance == -1:
    #     print "user aborted"
    #     return # user aborts
    #
    aborted = checkRuninngInstances("maya.exe")
    if aborted:
        print "user aborted"
        return # user aborts

    aborted = checkRuninngInstances("3dsmax.exe")
    if aborted:
        print "user aborted"
        return # user aborts

    aborted = checkRuninngInstances("houdinifx.exe")
    if aborted:
        print "user aborted"
        return # user aborts

def checkRuninngInstances(sw):
    # for p in psutil.process_iter():
    #     if sw in p.name():
    #         msg = "%s is running. Exit software and hit ok to continue" %(sw)
    #         ret = ctypes.windll.user32.MessageBoxA(0, msg, "Setup Cannot Continue", 1)
    #         print "rr", ret
    #         if ret == 1:  # OK
    #             print "ok pressed"
    #             checkRuninngInstances(sw)
    #             return
    #         if ret == 2:
    #             return -1 #aborthi
    aborted=False
    closed=False
    while not aborted and not closed:
        closed = not (sw in (p.name() for p in psutil.process_iter()))
        print "cl", closed
        if not closed:
            msg = "%s is running. Exit software and hit ok to continue" % (sw)
            ret = ctypes.windll.user32.MessageBoxA(0, msg, "Setup Cannot Continue", 1)
            if ret == 1:  # OK
                print "ok pressed"

            if ret == 2:
                aborted = True
                print aborted
    return aborted




# if "maya" in p.name():
        #     print "maya is running"
        # if "3dsmax" in p.name():
        #     print "3ds max is running"

    # "houdinifx.exe" in (p.name() for p in psutil.process_iter())





def _loadContent(filePath):
    f = open(filePath, "r")
    if f.mode == "r":
        contentList = f.readlines()
    else:
        return None
    f.close()
    return contentList

def _dumpContent(filePath, contentList):
    name, ext = os.path.splitext(filePath)
    tempFile = "{0}_TMP{1}".format(name, ext)
    f = open(tempFile, "w+")
    f.writelines(contentList)
    f.close()
    shutil.copyfile(tempFile, filePath)
    os.remove(tempFile)

def createOrReplace(file, newContentList, startLine="# start Scene Manager\n", endLine="# end Scene Manager\n"):
    # if there is no file
    if os.path.isfile(file):
        contentList = _loadContent(file)

        # if the file is empty ->
        if not contentList:
            _dumpContent(file, newContentList)
            return

        # make sure last line ends with a break line
        if "\n" not in contentList[-1] and contentList[-1] is not "":
            contentList[-1] = "%s\n" % (contentList[-1])
        # find start / end of previous content
        startIndex = -1
        endIndex = -1
        for i in contentList:
            if i == startLine:
                startIndex = contentList.index(i)
            if i == endLine:
                endIndex = contentList.index(i)

        print startIndex, endIndex
        if ((startIndex == -1) and (endIndex != -1)) or ((startIndex != -1) and (endIndex == -1)):
            raise Exception("Cannot edit %s. Edit it manually" % file)
        del contentList[startIndex: endIndex + 1]
        print "sik", contentList
        dumpList = contentList + newContentList
        _dumpContent(file, dumpList)

    else:
        _dumpContent(file, newContentList)

def mayaSetup():
    networkDir = os.path.dirname(os.path.abspath(__file__))
    upNetworkDir = os.path.abspath(os.path.join(networkDir, os.pardir))
    userHomeDir = os.path.normpath(os.path.join(os.path.expanduser("~")))
    userDocDir = os.path.join(userHomeDir, "Documents")
    userMayaDir = os.path.join(userDocDir, "maya")
    userScriptsDir = os.path.join(userMayaDir, "scripts")
    userSetupFile = os.path.join(userScriptsDir, "userSetup.py")
    newUserSetupContent = [
        "# start Scene Manager\n",
        "import os\n",
        "import sys\n",
        "import maya.utils\n",
        "import maya.OpenMaya as OpenMaya\n",
        "\n",
        "def initFolder(targetFolder):\n",
        "    if targetFolder in sys.path:\n",
        "        return\n",
        "    if not os.path.isdir(targetFolder):\n",
        "        print ('Path is not valid (%s)' % targetFolder)\n",
        "    sys.path.append(targetFolder)\n",
        "\n",
        "def smUpdate(*args):\n",
        "    from tik_manager import manager\n",
        "    m = manager.TikManager()\n",
        "    m.regularSaveUpdate()\n",
        "\n",
        "initFolder('{0}')\n".format((upNetworkDir.replace("\\", "//"))),
        "maya.utils.executeDeferred('SMid = OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterSave, smUpdate)')\n",
        "# end Scene Manager\n"
    ]
    createOrReplace(userSetupFile, newUserSetupContent)
    print "userSetup updated at: %s" %(userSetupFile)

    ## SHELF
    mayaVersions = [x for x in os.listdir(userMayaDir) if os.path.isdir(os.path.join(userMayaDir, x)) and x.startswith('20')]

    managerIcon = os.path.join(networkDir, "icons", "manager_ICON.png").replace("\\", "\\\\")
    saveVersionIcon = os.path.join(networkDir, "icons", "saveVersion_ICON.png").replace("\\", "\\\\")
    imageManagerIcon = os.path.join(networkDir, "icons", "imageManager_ICON.png").replace("\\", "\\\\")
    imageViewerIcon = os.path.join(networkDir, "icons", "imageViewer_ICON.png").replace("\\", "\\\\")
    takePreviewIcon = os.path.join(networkDir, "icons", "takePreview_ICON.png").replace("\\", "\\\\")
    shelfContent = """global proc shelf_SceneManager () {
    global string $gBuffStr;
    global string $gBuffStr0;
    global string $gBuffStr1;


    shelfButton
        -enableCommandRepeat 1
        -enable 1
        -width 35
        -height 35
        -manage 1
        -visible 1
        -preventOverride 0
        -annotation "SceneManager" 
        -enableBackground 0
        -align "center" 
        -label "SceneManager" 
        -labelOffset 0
        -font "plainLabelFont" 
        -overlayLabelColor 0.9 0.9 0.9 
        -overlayLabelBackColor 0 0 0 0 
        -image "%s" 
        -image1 "%s"
        -style "iconOnly" 
        -marginWidth 1
        -marginHeight 1
        -command "\\nfrom tik_manager import SmMaya\\nreload(SmMaya)\\ntik_sceneManager = SmMaya.MainUI(callback=\\"tik_sceneManager\\")\\ntik_sceneManager.show()\\n" 
        -sourceType "python" 
        -commandRepeatable 1
        -flat 1
    ;
    shelfButton
        -enableCommandRepeat 1
        -enable 1
        -width 35
        -height 35
        -manage 1
        -visible 1
        -preventOverride 0
        -annotation "saveVersion" 
        -enableBackground 0
        -align "center" 
        -label "saveVersion" 
        -labelOffset 0
        -font "plainLabelFont" 
        -overlayLabelColor 0.9 0.9 0.9 
        -overlayLabelBackColor 0 0 0 0 
        -image "%s"
        -image1 "%s"
        -style "iconOnly" 
        -marginWidth 1
        -marginHeight 1
        -command "\\nfrom tik_manager import SmMaya\\nSmMaya.MainUI().saveAsVersionDialog()\\n" 
        -sourceType "python" 
        -commandRepeatable 1
        -flat 1
    ;
    shelfButton
        -enableCommandRepeat 1
        -enable 1
        -width 35
        -height 35
        -manage 1
        -visible 1
        -preventOverride 0
        -annotation "imageManager" 
        -enableBackground 0
        -align "center" 
        -label "imageManager" 
        -labelOffset 0
        -font "plainLabelFont" 
        -overlayLabelColor 0.9 0.9 0.9 
        -overlayLabelBackColor 0 0 0 0 
        -image "%s"
        -image1 "%s"
        -style "iconOnly" 
        -marginWidth 1
        -marginHeight 1
        -command "\\nfrom tik_manager import ImMaya\\ntik_imageManager = ImMaya.MainUI(callback=\\"tik_imageManager\\")\\n" 
        -sourceType "python" 
        -commandRepeatable 1
        -flat 1
    ;
    shelfButton
        -enableCommandRepeat 1
        -enable 1
        -width 35
        -height 35
        -manage 1
        -visible 1
        -preventOverride 0
        -annotation "imageViewer" 
        -enableBackground 0
        -align "center" 
        -label "imageViewer" 
        -labelOffset 0
        -font "plainLabelFont" 
        -overlayLabelColor 0.9 0.9 0.9 
        -overlayLabelBackColor 0 0 0 0 
        -image "%s"
        -image1 "%s"
        -style "iconOnly" 
        -marginWidth 1
        -marginHeight 1
        -command "\\nfrom tik_manager import IvMaya\\ntik_imageViewer = IvMaya.MainUI().show()\\n" 
        -sourceType "python" 
        -commandRepeatable 1
        -flat 1
    ;
        shelfButton
        -enableCommandRepeat 1
        -enable 1
        -width 35
        -height 35
        -manage 1
        -visible 1
        -preventOverride 0
        -annotation "takePreview" 
        -enableBackground 0
        -align "center" 
        -label "takePreview" 
        -labelOffset 0
        -font "plainLabelFont" 
        -overlayLabelColor 0.9 0.9 0.9 
        -overlayLabelBackColor 0 0 0 0 
        -image "%s"
        -image1 "%s"
        -style "iconOnly" 
        -marginWidth 1
        -marginHeight 1
        -command "\\nfrom tik_manager import SmMaya\\ntik_imageViewer = SmMaya.MayaManager().createPreview()\\n" 
        -sourceType "python" 
        -commandRepeatable 1
        -flat 1
    ;

} """ %(managerIcon,managerIcon,saveVersionIcon,saveVersionIcon,imageManagerIcon,imageManagerIcon,imageViewerIcon,imageViewerIcon, takePreviewIcon, takePreviewIcon)

    for v in mayaVersions:
        shelfDir = os.path.join(userMayaDir, v, "prefs", "shelves")
        if not os.path.isdir(shelfDir):
            os.makedirs(os.path.normpath(shelfDir))
        shelfFile = os.path.join(shelfDir, "shelf_SceneManager.mel")
        _dumpContent(shelfFile, shelfContent)
        print "Shelf created for %s" %v

def houdiniSetup():
    networkDir = os.path.dirname(os.path.abspath(__file__))
    upNetworkDir = os.path.abspath(os.path.join(networkDir, os.pardir))
    userHomeDir = os.path.normpath(os.path.join(os.path.expanduser("~")))
    userDocDir = os.path.join(userHomeDir, "Documents")
    houdiniVersions = [x for x in os.listdir(userDocDir) if
                    os.path.isdir(os.path.join(userDocDir, x)) and x.startswith('houdini')]

    # ICON PATHS
    managerIcon = os.path.join(networkDir, "icons", "manager_ICON.png").replace("\\", "\\\\")
    saveVersionIcon = os.path.join(networkDir, "icons", "saveVersion_ICON.png").replace("\\", "\\\\")
    imageManagerIcon = os.path.join(networkDir, "icons", "imageManager_ICON.png").replace("\\", "\\\\")
    imageViewerIcon = os.path.join(networkDir, "icons", "imageViewer_ICON.png").replace("\\", "\\\\")
    takePreviewIcon = os.path.join(networkDir, "icons", "takePreview_ICON.png").replace("\\", "\\\\")

    sScriptContent = [
        "# start Scene Manager\n",
        "import os\n"
        "import sys\n"
        "\n"
        "def initFolder(targetFolder):\n"
        "    if targetFolder in sys.path:\n"
        "        return\n"
        "    if not os.path.isdir(targetFolder):\n"
        "        print ('Path is not valid (%s)' % targetFolder)\n"
        "    sys.path.append(targetFolder)\n"
        "\n"
        "initFolder('{0}')\n".format((upNetworkDir.replace("\\", "//"))),
        "# end Scene Manager\n"
    ]

    shelfContent = """<?xml version="1.0" encoding="UTF-8"?>
<shelfDocument>
  <!-- This file contains definitions of shelves, toolbars, and tools.
 It should not be hand-edited when it is being used by the application.
 Note, that two definitions of the same element are not allowed in
 a single file. -->

  <toolshelf name="sceneManager" label="Scene Manager">
    <memberTool name="sceneManager"/>
    <memberTool name="saveVersion"/>
    <memberTool name="imageViewer"/>
    <memberTool name="takePreview"/>
  </toolshelf>

  <tool name="sceneManager" label="Manager" icon="%s">
    <script scriptType="python"><![CDATA[from tik_manager import SmHoudini
reload(SmHoudini)
SmHoudini.MainUI().show()]]></script>
  </tool>

  <tool name="saveVersion" label="Version" icon="%s">
    <script scriptType="python"><![CDATA[from tik_manager import SmHoudini
SmHoudini.MainUI().saveAsVersionDialog()]]></script>
  </tool>

  <tool name="imageViewer" label="Images" icon="%s">
    <script scriptType="python"><![CDATA[hou.ui.displayMessage("Not Yet Implemented")]]></script>
  </tool>

  <tool name="takePreview" label="Preview" icon="%s">
    <script scriptType="python"><![CDATA[from tik_manager import SmHoudini
SmHoudini.HoudiniManager().createPreview()]]></script>
  </tool>
</shelfDocument>
    """ %(managerIcon, saveVersionIcon, imageViewerIcon, takePreviewIcon)

    for v in houdiniVersions:
        scriptsFolder = os.path.join(userDocDir, v, "scripts")
        # create the directory if does not exist
        if not os.path.isdir(scriptsFolder):
            os.makedirs(os.path.normpath(scriptsFolder))
        sScriptFile = os.path.join(scriptsFolder, "456.py")
        createOrReplace(sScriptFile, sScriptContent)

        ## SHELF
        shelfDir = os.path.join(userDocDir, "toolbar")
        # create the directory if does not exist
        if not os.path.isdir(shelfDir):
            os.makedirs(os.path.normpath(shelfDir))
        shelfFile = os.path.join(shelfDir, "sceneManagerTEST.shelf")
        _dumpContent(shelfFile, shelfContent)




checkIntegrity()
# houdiniSetup()