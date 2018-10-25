import sys
import os
import shutil

def checkIntegrity():
    networkDir = os.path.dirname(os.path.abspath(__file__))
    fileList = ["__init__.py",
                "_version.py",
                "ImMaya.py",
                "IvMaya.py",
                "IvStandalone.py",
                "pyseq.py",
                "Qt.py",
                "SmHoudini.py",
                "SmMaya.py",
                "SmRoot.py",
                "SmStandalone.py"
                "SubmitMayaToDeadlineCustom.mel"
                ]
    for file in fileList:
        if not os.path.isfile(os.path.join(networkDir, file)):
            raise Exception ("MISSING FILE: %s" %file)





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
        if (startIndex != -1) and (endIndex != -1):
            del contentList[startIndex: endIndex + 1]
            dumpList = contentList + newContentList
            _dumpContent(file, dumpList)
        else:
            raise Exception ("Cannot edit %s. Edit it manually" %(file))
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


    ## SHELF
    mayaVersions = [x for x in os.listdir(userMayaDir) if os.path.isdir(os.path.join(userMayaDir, x)) and x.startswith('20')]

    managerIcon = os.path.join(networkDir, "icons", "manager_ICON.png").replace("\\", "\\\\")
    saveVersionIcon = os.path.join(networkDir, "icons", "saveVersion_ICON.png").replace("\\", "\\\\")
    imageManagerIcon = os.path.join(networkDir, "icons", "imageManager_ICON.png").replace("\\", "\\\\")
    imageViewerIcon = os.path.join(networkDir, "icons", "imageViewer_ICON.png").replace("\\", "\\\\")
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

} """ %(managerIcon,managerIcon,saveVersionIcon,saveVersionIcon,imageManagerIcon,imageManagerIcon,imageViewerIcon,imageViewerIcon)

    for v in mayaVersions:
        shelfDir = os.path.join(userMayaDir, v, "prefs", "shelves")
        shelfFile = os.path.join(shelfDir, "shelf_SceneManager.mel")
        if os.path.isdir(shelfDir):
            _dumpContent(shelfFile, shelfContent)



checkIntegrity()
mayaSetup()


