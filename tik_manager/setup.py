#!/usr/bin/python
from builtins import input
import sys, getopt
import os
import shutil
import psutil
# import tik_manager._version as _version
import tik_manager._version as _version

import json
try: import _winreg as reg
except ModuleNotFoundError: import winreg as reg



def checkRuninngInstances(sw):
    running = True
    aborted = False

    while not aborted and running:
        # closed = not (sw in (p.name() for p in psutil.process_iter()))
        # processes = psutil.process_iter()
        # matchList = [p for p in processes if p._name.startswith(sw)]
        # matchList = []

        running = False
        for p in psutil.process_iter():
            name = str(p._name)
            if name:
                if name.startswith(sw):
                    running = True
                    break
        #
        # if matchList:
        #     running = True
        # else:
        #     running = False

        if running:
            # msg = "%s is running. Exit software and ok to continue" % (sw)
            msg = "%s is running. Exit software and type 'y'. type 'n' to abort" % (sw)
            # ret = ctypes.windll.user32.MessageBoxA(0, msg, "Setup Cannot Continue", 1)
            # ret = win32ui.MessageBox(msg, "Setup Cannot Continue", win32con.MB_OKCANCEL)
            ret = okCancel(msg)
            if ret == 1:  # OK
                pass

            if ret == 2:
                aborted = True
                return -1
        else:
            return 1
        # return -1

def _loadContent(filePath):
    f = open(filePath, "r")
    if f.mode == "r":
        contentList = f.readlines()
    else:
        return None
    f.close()
    return contentList

def _dumpContent(filePath, contentList, backup=False):
    # if backup:
    #     shutil.copyfile(filePath)
    name, ext = os.path.splitext(filePath)
    if backup:
        if os.path.isfile(filePath):
            backupFile = "{0}.bak".format(name)
            shutil.copyfile(filePath, backupFile)
            print("Backup complete\n%s => %s" %(filePath, backupFile))
    tempFile = "{0}_TMP{1}".format(name, ext)
    f = open(tempFile, "w+")
    f.writelines(contentList)
    f.close()
    shutil.copyfile(tempFile, filePath)
    os.remove(tempFile)

def inject(file, newContentList, between=None, after=None, before=None, matchMode="equal", force=True, searchDirection="forward"):
    if type(newContentList) == str:
        newContentList = [newContentList]

    if not os.path.isfile(file):
        if force:
            _dumpContent(file, newContentList)
            print("Created %s with new content" % file)
            return True
        else:
            print("File does not exist (%s)" %file)
            return False

    contentList = _loadContent(file)

    # if the file is empty ->
    if not contentList:
        if force:
            _dumpContent(file, newContentList)
            print("New content added to empty %s" %file)
            return True
        else:
            print("File is empty, nothing to change")
            return False

    # make sure last line ends with a break line
    if "\n" not in contentList[-1] and contentList[-1] is not "":
        contentList[-1] = "%s\n" % (contentList[-1])

    if not between and not after and not before:
        # no search, just append
        _dumpContent(file, (contentList + newContentList))
        return True

    #continue with search and replace

    startIndex = None
    endIndex = None


    searchList = list(reversed(contentList)) if searchDirection == "backward" else contentList

    ####################################

    def collectIndex(searchList, line, beginFrom=0, mode="equal"):
        if mode == "equal":
            try:
                index = searchList.index(line)
            except ValueError:
                index = None
            return index
        elif mode == "includes":
            for i in range(beginFrom, len(searchList)):
                if line in searchList[i]:
                    index = i
                    return index
            return None # if no match

    if between:
        startLine = between[0]
        endLine = between[1]
        startIndex = collectIndex(searchList, startLine, mode=matchMode)
        if not startIndex == None:
            endIndex = collectIndex(searchList, endLine, beginFrom=startIndex, mode=matchMode)
        if startIndex == None or not endIndex:
            if force:
                "Cannot find Start Line. Just appending to the file"
                _dumpContent(file, (contentList + newContentList))
            else:
                print("Cannot find Start Line. Skipping replace injection")
                return

    elif after:
        startIndex = collectIndex(searchList, after, mode=matchMode)
        if not startIndex:
            print("Cannot find After Line. Aborting")
            return
        endIndex = startIndex+1

    elif before:
        startIndex = collectIndex(searchList, before, mode=matchMode)
        if not startIndex:
            print("Cannot find After Line. Aborting")
            return
        endIndex = startIndex-1

    if searchDirection == "backward":
        injectedContent = contentList[:-endIndex] + newContentList + contentList[-startIndex - 1:]
    else:
        injectedContent = contentList[:startIndex] + newContentList + contentList[endIndex + 1:]


    _dumpContent(file, injectedContent)
    return True

def nukeSetup(prompt=True):
    print("Starting Nuke Setup")
    print("Checking files...")

    networkDir = os.path.dirname(os.path.abspath(__file__))
    fileList = ["__init__.py",
                "_version.py",
                "ImageViewer.py",
                "pyseq.py",
                "Qt.py",
                "SmUIRoot.py",
                "SmNuke.py",
                "SmRoot.py",
                "projectMaterials.py",
                ]
    for file in fileList:
        if not os.path.isfile(os.path.join(networkDir, file)):
            # if the extension is pyc give it another chance
            if os.path.splitext(file)[1] == ".py":
                if not os.path.isfile(os.path.join(networkDir, "%sc" %file)): # make the extension pyc
                    print("Missing file:\nCannot find %s or %sc" % (file, file))
                    # raw_input("Press Enter to continue...")
                    r = input("Press Enter to continue...")
                    assert isinstance(r, str)

                    return
            else:
                print("Missing file:\nCannot find %s" %file)
                # raw_input("Press Enter to continue...")
                r = input("Press Enter to continue...")
                assert isinstance(r, str)
                return

    # check for running instances
    state = checkRuninngInstances("Nuke")
    if state == -1:
        print("Installation Aborted by User")
        return # user aborts

    upNetworkDir = os.path.abspath(os.path.join(networkDir, os.pardir))
    userHomeDir = os.path.normpath(os.path.join(os.path.expanduser("~")))
    pluginDir = os.path.join(userHomeDir, '.nuke')
    initFile = os.path.join(pluginDir, 'init.py')
    menuFile = os.path.join(pluginDir, 'menu.py')

    if not os.path.isdir(pluginDir):
        print("No Nuke version can be found, try manual installation")
        if prompt:
            # raw_input("Press Enter to continue...")
            r = input("Press Enter to continue...")
            assert isinstance(r, str)
        return

    managerIcon = os.path.join(networkDir, "icons", "manager_ICON.png").replace("\\", "\\\\")
    saveVersionIcon = os.path.join(networkDir, "icons", "saveVersion_ICON.png").replace("\\", "\\\\")
    # imageManagerIcon = os.path.join(networkDir, "icons", "imageManager_ICON.png").replace("\\", "\\\\")
    imageViewerIcon = os.path.join(networkDir, "icons", "imageViewer_ICON.png").replace("\\", "\\\\")
    # takePreviewIcon = os.path.join(networkDir, "icons", "takePreview_ICON.png").replace("\\", "\\\\")
    projectMaterialsIcon = os.path.join(networkDir, "icons", "projectMaterials_ICON.png").replace("\\", "\\\\")

    shutil.copyfile(managerIcon, os.path.join(pluginDir, "manager_ICON.png"))
    shutil.copyfile(saveVersionIcon, os.path.join(pluginDir, "saveVersion_ICON.png"))
    shutil.copyfile(imageViewerIcon, os.path.join(pluginDir, "imageViewer_ICON.png"))
    shutil.copyfile(projectMaterialsIcon, os.path.join(pluginDir, "projectMaterials_ICON.png"))

    initContent = [
        "# start Scene Manager\n",
        "import os\n",
        "import sys\n",
        "\n",
        "def initFolder(targetFolder):\n",
        "    if targetFolder in sys.path:\n",
        "        return\n",
        "    if not os.path.isdir(targetFolder):\n",
        "        print ('Path is not valid (%s)' % targetFolder)\n",
        "    sys.path.append(targetFolder)\n",
        "\n",
        "initFolder('{0}')\n".format((upNetworkDir.replace("\\", "//"))),
        "# end Scene Manager\n"
    ]

    inject(initFile, initContent, between=("# start Scene Manager\n", "# end Scene Manager\n"))
    print("init.py file updated at: %s" %(initFile))

    menuContent = [
        "# start Scene Manager\n",
        "toolbar = nuke.menu('Nodes')\n",
        "smMenu = toolbar.addMenu('SceneManager', icon='manager_ICON.png')\n",
        "smMenu.addCommand('Scene Manager', 'from tik_manager import SmNuke\\nSmNuke.MainUI().show()', icon='manager_ICON.png')\n",
        "smMenu.addCommand('Save Version', 'from tik_manager import SmNuke\\nSmNuke.MainUI().saveAsVersionDialog()', icon='saveVersion_ICON.png')\n",
        "smMenu.addCommand('Image Viewer', 'from tik_manager import SmNuke\\ntik_imageViewer = SmNuke.MainUI()\\ntik_imageViewer.onIviewer()', icon='imageViewer_ICON.png')\n",
        "smMenu.addCommand('Project Materials', 'from tik_manager import SmNuke\\ntik_projectMaterials = SmNuke.MainUI()\\ntik_projectMaterials.onPMaterials()', icon='projectMaterials_ICON.png')\n",
        "# end Scene Manager\n"
    ]
    inject(menuFile, menuContent, between=("# start Scene Manager\n", "# end Scene Manager\n"))
    print("menu.py updated at: %s" %(menuFile))

    print("Successfull => Nuke Setup")
    if prompt:
        # raw_input("Press Enter to continue...")
        r = input("Press Enter to continue...")
        assert isinstance(r, str)


def mayaSetup(prompt=True):
    # Check file integrity
    print("Starting Maya Setup")
    print("Checking files...")
    networkDir = os.path.dirname(os.path.abspath(__file__))
    fileList = ["__init__.py",
                "_version.py",
                "ImMaya.py",
                "ImageViewer.py",
                "assetLibrary.py",
                "assetEditorMaya.py",
                "pyseq.py",
                "Qt.py",
                "SmUIRoot.py",
                "SmMaya.py",
                "SmRoot.py",
                "projectMaterials.py",
                ]
    for file in fileList:
        if not os.path.isfile(os.path.join(networkDir, file)):
            # if the extension is pyc give it another chance
            if os.path.splitext(file)[1] == ".py":
                if not os.path.isfile(os.path.join(networkDir, "%sc" %file)): # make the extension pyc
                    print("Missing file:\nCannot find %s or %sc" % (file, file))
                    # raw_input("Press Enter to continue...")
                    r = input("Press Enter to continue...")
                    assert isinstance(r, str)
                    return
            else:
                print("Missing file:\nCannot find %s" %file)
                # raw_input("Press Enter to continue...")
                r = input("Press Enter to continue...")
                assert isinstance(r, str)
                return

    # check for running instances
    state = checkRuninngInstances("maya")
    if state == -1:
        print("Installation Aborted by User")
        return # user aborts

    upNetworkDir = os.path.abspath(os.path.join(networkDir, os.pardir))
    userHomeDir = os.path.normpath(os.path.join(os.path.expanduser("~")))
    userDocDir = os.path.join(userHomeDir, "Documents")
    userMayaDir = os.path.join(userDocDir, "maya")
    userScriptsDir = os.path.join(userMayaDir, "scripts")
    userSetupFile = os.path.join(userScriptsDir, "userSetup.py")

    print("Finding Maya Versions...")
    mayaVersions = [x for x in os.listdir(userMayaDir) if os.path.isdir(os.path.join(userMayaDir, x)) and x.startswith('20')]
    if mayaVersions:
        print("Found Maya Versions: %s " % str(mayaVersions))
    else:
        print("No Maya version can be found, try manual installation")
        # raw_input("Press Enter to continue...")
        r = input("Press Enter to continue...")
        assert isinstance(r, str)
        return

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
        "    try:\n",
        "        from tik_manager import SmMaya\n",
        "        m = SmMaya.MayaManager()\n",
        "        m.saveCallback()\n",
        "    except:\n",
        "        pass\n",
        "\n",
        "initFolder('{0}')\n".format((upNetworkDir.replace("\\", "//"))),
        "maya.utils.executeDeferred('SMid = OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterSave, smUpdate)')\n",
        "# end Scene Manager\n"
    ]
    # createOrReplace(userSetupFile, newUserSetupContent)
    inject(userSetupFile, newUserSetupContent, between=("# start Scene Manager\n", "# end Scene Manager\n"))
    print("userSetup updated at: %s" %(userSetupFile))

    ## SHELF


    managerIcon = os.path.join(networkDir, "icons", "manager_ICON.png").replace("\\", "\\\\")
    saveVersionIcon = os.path.join(networkDir, "icons", "saveVersion_ICON.png").replace("\\", "\\\\")
    imageManagerIcon = os.path.join(networkDir, "icons", "imageManager_ICON.png").replace("\\", "\\\\")
    imageViewerIcon = os.path.join(networkDir, "icons", "imageViewer_ICON.png").replace("\\", "\\\\")
    takePreviewIcon = os.path.join(networkDir, "icons", "takePreview_ICON.png").replace("\\", "\\\\")
    projectMaterialsIcon = os.path.join(networkDir, "icons", "projectMaterials_ICON.png").replace("\\", "\\\\")
    assetLibraryIcon = os.path.join(networkDir, "icons", "assetLibrary_ICON.png").replace("\\", "\\\\")
    shelfContent = """global proc shelf_TikManager () {
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
        -annotation "TikManager" 
        -enableBackground 0
        -align "center" 
        -label "TikManager" 
        -labelOffset 0
        -font "plainLabelFont" 
        -overlayLabelColor 0.9 0.9 0.9 
        -overlayLabelBackColor 0 0 0 0 
        -image "%s" 
        -image1 "%s"
        -style "iconOnly" 
        -marginWidth 1
        -marginHeight 1
        -command "\\nfrom tik_manager import SmMaya\\ntik_sceneManager = SmMaya.MainUI(callback=\\"tik_sceneManager\\")\\ntik_sceneManager.show()\\n" 
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
        -command "\\nfrom tik_manager import ImageViewer\\ntik_imageViewer = ImageViewer.MainUI().show()\\n" 
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
        -command "\\nfrom tik_manager import SmMaya\\nSmMaya.MayaManager().createPreview()\\n" 
        -sourceType "python"
        -doubleClickCommand "from tik_manager import SmMaya\\nSmMaya.MainUI().onCreatePreview()\\n" 
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
        -annotation "projectMaterials" 
        -enableBackground 0
        -align "center" 
        -label "projectMaterials" 
        -labelOffset 0
        -font "plainLabelFont" 
        -overlayLabelColor 0.9 0.9 0.9 
        -overlayLabelBackColor 0 0 0 0 
        -image "%s"
        -image1 "%s"
        -style "iconOnly" 
        -marginWidth 1
        -marginHeight 1
        -command "\\nfrom tik_manager import projectMaterials\\nprojectMaterials.MainUI().show()\\n" 
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
        -annotation "assetLibrary" 
        -enableBackground 0
        -align "center" 
        -label "assetLibrary" 
        -labelOffset 0
        -font "plainLabelFont" 
        -overlayLabelColor 0.9 0.9 0.9 
        -overlayLabelBackColor 0 0 0 0 
        -image "%s"
        -image1 "%s"
        -style "iconOnly" 
        -marginWidth 1
        -marginHeight 1
        -command "\\nfrom tik_manager import assetLibrary\\nassetLibrary.MainUI().show()\\n" 
        -sourceType "python" 
        -commandRepeatable 1
        -flat 1
    ;

} """ %(managerIcon,managerIcon,saveVersionIcon,saveVersionIcon,imageManagerIcon,imageManagerIcon,imageViewerIcon,imageViewerIcon, takePreviewIcon, takePreviewIcon, projectMaterialsIcon, projectMaterialsIcon, assetLibraryIcon, assetLibraryIcon)

    for v in mayaVersions:
        shelfDir = os.path.join(userMayaDir, v, "prefs", "shelves")
        folderCheck(shelfDir)
        oldShelfFile = os.path.join(shelfDir, "shelf_SceneManager.mel")
        try: os.remove(oldShelfFile)
        except: pass
        newShelfFile = os.path.join(shelfDir, "shelf_TikManager.mel")
        _dumpContent(newShelfFile, shelfContent)
        print("Shelf created for %s" %v)

    print("Successfull => Maya Setup")
    if prompt:
        # raw_input("Press Enter to continue...")
        r = input("Press Enter to continue...")
        assert isinstance(r, str)

def houdiniSetup(prompt=True):

    # Check file integrity
    print("Starting Houdini Setup")
    print("Checking files...")
    networkDir = os.path.dirname(os.path.abspath(__file__))
    fileList = ["__init__.py",
                "_version.py",
                "pyseq.py",
                "SmHoudini.py",
                "ImageViewer.py",
                "SmUIRoot.py",
                "SmRoot.py",
                "projectMaterials.py",
                ]
    for file in fileList:
        if not os.path.isfile(os.path.join(networkDir, file)):
            # if the extension is pyc give it another chance
            if os.path.splitext(file)[1] == ".py":
                if not os.path.isfile(os.path.join(networkDir, "%sc" %file)): # make the extension pyc
                    print("Missing file:\nCannot find %s or %sc" % (file, file))
                    # raw_input("Press Enter to continue...")
                    r = input("Press Enter to continue...")
                    assert isinstance(r, str)
                    return
            else:
                print("Missing file:\nCannot find %s" %file)
                # raw_input("Press Enter to continue...")
                r = input("Press Enter to continue...")
                assert isinstance(r, str)
                return

    # check for running instances
    state = checkRuninngInstances("houdini")
    if state == -1:
        print("Aborted bt user")
        return # user aborts

    upNetworkDir = os.path.abspath(os.path.join(networkDir, os.pardir))
    userHomeDir = os.path.normpath(os.path.join(os.path.expanduser("~")))
    userDocDir = os.path.join(userHomeDir, "Documents")
    print("Finding Houdini Versions...")
    houdiniVersions = [x for x in os.listdir(userDocDir) if
                    os.path.isdir(os.path.join(userDocDir, x)) and x.startswith('houdini')]
    if houdiniVersions:
        print("Found Houdini Versions: %s " % str(houdiniVersions))
    else:
        print("No Houdini version can be found, try manual installation")
        if prompt:
            # raw_input("Press Enter to continue...")
            r = input("Press Enter to continue...")
            assert isinstance(r, str)
        return
    # ICON PATHS
    managerIcon = os.path.join(networkDir, "icons", "manager_ICON.png").replace("\\", "\\\\")
    saveVersionIcon = os.path.join(networkDir, "icons", "saveVersion_ICON.png").replace("\\", "\\\\")
    imageManagerIcon = os.path.join(networkDir, "icons", "imageManager_ICON.png").replace("\\", "\\\\")
    imageViewerIcon = os.path.join(networkDir, "icons", "imageViewer_ICON.png").replace("\\", "\\\\")
    takePreviewIcon = os.path.join(networkDir, "icons", "takePreview_ICON.png").replace("\\", "\\\\")
    projectMaterialsIcon = os.path.join(networkDir, "icons", "projectMaterials_ICON.png").replace("\\", "\\\\")
    assetLibraryIcon = os.path.join(networkDir, "icons", "assetLibrary_ICON.png").replace("\\", "\\\\")

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

  <toolshelf name="tikManager" label="Tik Manager">
    <memberTool name="tikManager"/>
    <memberTool name="saveVersion"/>
    <memberTool name="imageViewer"/>
    <memberTool name="takePreview"/>
    <memberTool name="projectMaterials"/>
    <memberTool name="assetLibrary"/>
  </toolshelf>

  <tool name="tikManager" label="Tik Manager" icon="%s">
    <script scriptType="python"><![CDATA[from tik_manager import SmHoudini
SmHoudini.MainUI().show()]]></script>
  </tool>

  <tool name="saveVersion" label="Version" icon="%s">
    <script scriptType="python"><![CDATA[from tik_manager import SmHoudini
SmHoudini.MainUI().saveAsVersionDialog()]]></script>
  </tool>

  <tool name="imageViewer" label="Images" icon="%s">
    <script scriptType="python"><![CDATA[from tik_manager import ImageViewer
tik_imageViewer = ImageViewer.MainUI().show()]]></script>
  </tool>
  
  <tool name="takePreview" label="Preview" icon="%s">
    <script scriptType="python"><![CDATA[from tik_manager import SmHoudini
SmHoudini.HoudiniManager().createPreview()]]></script>
  </tool>
  
  <tool name="projectMaterials" label="Project Materials" icon="%s">
    <script scriptType="python"><![CDATA[from tik_manager import projectMaterials
projectMaterials.MainUI().show()]]></script>
  </tool>
  
  <tool name="assetLibrary" label="Asset Library" icon="%s">
    <script scriptType="python"><![CDATA[from tik_manager import assetLibrary
assetLibrary.MainUI().show()]]></script>
  </tool>
</shelfDocument>
    """ %(managerIcon, saveVersionIcon, imageViewerIcon, takePreviewIcon, projectMaterialsIcon, assetLibraryIcon)


    for v in houdiniVersions:
        scriptsFolder = os.path.join(userDocDir, v, "scripts")
        # create the directory if does not exist
        folderCheck(scriptsFolder)
        sScriptFile = os.path.join(scriptsFolder, "456.py")
        # createOrReplace(sScriptFile, sScriptContent)
        inject(sScriptFile, sScriptContent, between=("# start Scene Manager\n", "# end Scene Manager\n"))

        print("Path config appended to %s" %sScriptFile)

        ## SHELF
        shelfDir = os.path.join(userDocDir, v, "toolbar")
        # create the directory if does not exist
        folderCheck(shelfDir)
        shelfFile = os.path.join(shelfDir, "tikManager.shelf")
        _dumpContent(shelfFile, shelfContent)

        print("Tik Manager shelf created or updated at %s" % shelfFile)

    print("\nInside Houdini, Tik Manager shelf should be enabled for the desired shelf set by clicking to '+' icon and selecting 'shelves' sub menu.")

    print("Successfull => Houdini Setup")

    if prompt:
        # raw_input("Press Enter to continue...")
        r = input("Press Enter to continue...")
        assert isinstance(r, str)

def maxSetup(prompt=True):

    # TODO Prevent installation for unsupported versions
    print("Starting 3ds Max Setup")
    print("Checking files...")
    networkDir = os.path.dirname(os.path.abspath(__file__))
    upNetworkDir = os.path.abspath(os.path.join(networkDir, os.pardir))
    fileList = ["__init__.py",
                "_version.py",
                "pyseq.py",
                "ImageViewer.py",
                "SmUIRoot.py",
                "SmRoot.py",
                "Sm3dsMax.py",
                "projectMaterials.py",
                "assetLibrary.py",
                "assetEditor3dsMax.py"
                ]

    for file in fileList:
        if not os.path.isfile(os.path.join(networkDir, file)):
            # if the extension is pyc give it another chance
            if os.path.splitext(file)[1] == ".py":
                if not os.path.isfile(os.path.join(networkDir, "%sc" %file)): # make the extension pyc
                    print("Missing file:\nCannot find %s or %sc" % (file, file))
                    # raw_input("Press Enter to continue...")
                    r = input("Press Enter to continue...")
                    assert isinstance(r, str)
                    return
            else:
                print("Missing file:\nCannot find %s" %file)
                # raw_input("Press Enter to continue...")
                r = input("Press Enter to continue...")
                assert isinstance(r, str)
                return

    # check for running instances
    state = checkRuninngInstances("3dsmax")
    if state == -1:
        print("Installation Aborted by User")
        return # user aborts

    userHomeDir = os.path.normpath(os.path.join(os.path.expanduser("~")))
    userMaxDir = os.path.join(userHomeDir, "AppData", "Local", "Autodesk", "3dsMax")

    # ICON PATHS
    pack_16a = os.path.join(networkDir, "icons", "SceneManager_16a.bmp").replace("\\", "\\\\")
    pack_16i = os.path.join(networkDir, "icons", "SceneManager_16i.bmp").replace("\\", "\\\\")
    pack_24a = os.path.join(networkDir, "icons", "SceneManager_24a.bmp").replace("\\", "\\\\")
    pack_24i = os.path.join(networkDir, "icons", "SceneManager_24i.bmp").replace("\\", "\\\\")

    workSpaceInjection ="""        <Window name="Tik Manager" type="T" rank="0" subRank="2" hidden="0" dPanel="1" tabbed="0" curTab="-1" cType="1" toolbarRows="1" toolbarType="3">
            <FRect left="198" top="125" right="350" bottom="199" />
            <DRect left="1395" top="53" right="1504" bottom="92" />
            <DRectPref left="2147483647" top="2147483647" right="-2147483648" bottom="-2147483648" />
            <CurPos left="198" top="125" right="600" bottom="199" floating="1" panelID="16" />
            <Items>
                <Item typeID="2" type="CTB_MACROBUTTON" width="0" height="0" controlID="0" macroTypeID="3" macroType="MB_TYPE_ACTION" actionTableID="647394" imageID="-1" imageName="" actionID="manager`Tik Works" tip="Tik Manager" label="Tik Manager" />
                <Item typeID="2" type="CTB_MACROBUTTON" width="0" height="0" controlID="0" macroTypeID="3" macroType="MB_TYPE_ACTION" actionTableID="647394" imageID="-1" imageName="" actionID="saveVersion`Tik Works" tip="Tik Manager - Version Save" label="Save Version" />
                <Item typeID="2" type="CTB_MACROBUTTON" width="0" height="0" controlID="0" macroTypeID="3" macroType="MB_TYPE_ACTION" actionTableID="647394" imageID="-1" imageName="" actionID="imageViewer`Tik Works" tip="Tik Manager - Image Viewer" label="Image Viewer" />
                <Item typeID="2" type="CTB_MACROBUTTON" width="0" height="0" controlID="0" macroTypeID="3" macroType="MB_TYPE_ACTION" actionTableID="647394" imageID="-1" imageName="" actionID="makePreview`Tik Works" tip="Tik Manager - Make Preview" label="Make Preview" />
                <Item typeID="2" type="CTB_MACROBUTTON" width="0" height="0" controlID="0" macroTypeID="3" macroType="MB_TYPE_ACTION" actionTableID="647394" imageID="-1" imageName="" actionID="projectMaterials`Tik Works" tip="Tik Manager - Project Materials" label="Project Materials" />
                <Item typeID="2" type="CTB_MACROBUTTON" width="0" height="0" controlID="0" macroTypeID="3" macroType="MB_TYPE_ACTION" actionTableID="647394" imageID="-1" imageName="" actionID="assetLibrary`Tik Works" tip="Tik Manager - Asset Library" label="Asset Library" />
            </Items>
        </Window>\n"""

    print("Finding 3ds Max Versions...")

    try: maxVersions = [x for x in os.listdir(userMaxDir)]
    except: maxVersions = None

    if maxVersions:
        print("Found 3ds Max Versions: %s " % str(maxVersions))
    else:
        print("No 3ds Max version can be found, try manual installation")
        if prompt:
            # raw_input("Press Enter to continue...")
            r = input("Press Enter to continue...")
            assert isinstance(r, str)
        return


    for v in maxVersions:
        print("Setup for version %s" %v)
        sScriptsDir = os.path.join(userMaxDir, v, "ENU", "scripts", "startup")
        folderCheck(sScriptsDir)
        iconsDir = os.path.join(userMaxDir, v, "ENU", "usericons")
        folderCheck(iconsDir)
        macrosDir = os.path.join(userMaxDir, v, "ENU", "usermacros")
        folderCheck(macrosDir)
        print("Copying Icon sets...")
        print(iconsDir)
        shutil.copy(pack_16a, os.path.normpath(os.path.join(iconsDir, "SceneManager_16a.bmp")))
        shutil.copy(pack_16i, os.path.normpath(os.path.join(iconsDir, "SceneManager_16i.bmp")))
        shutil.copy(pack_24a, os.path.normpath(os.path.join(iconsDir, "SceneManager_24a.bmp")))
        shutil.copy(pack_24i, os.path.normpath(os.path.join(iconsDir, "SceneManager_24i.bmp")))

        workspaceDir =  os.path.join(userMaxDir, v, "ENU", "en-US", "UI", "Workspaces", "usersave")
        folderCheck(workspaceDir)
        workspaceFile = os.path.join(workspaceDir, "Workspace1__usersave__.cuix")\

        # workSpaceContentList = _loadContent(workspaceFile)

        print("Creating Callback and path initialization startup script")
        startupScriptContent = """
python.Execute "import sys"
python.Execute "import os"
python.Execute "import MaxPlus"
python.Execute "sys.path.append(os.path.normpath('{0}'))"
python.Execute "def smUpdate(*args):\\n    try:\\n        from tik_manager import Sm3dsMax\\n        m = Sm3dsMax.MaxManager()\\n        m.saveCallback()\\n    except:\\n        pass"
python.Execute "MaxPlus.NotificationManager.Register(14, smUpdate)"
""".format(upNetworkDir.replace("\\", "//"))

        _dumpContent(os.path.join(sScriptsDir, "smManagerCallback.ms"), startupScriptContent)


        print("Creating Macroscripts")
        manager = """
macroScript manager
category: "Tik Works"
tooltip: "Tik Manager"
ButtonText: "TikManager"
icon: #("SceneManager",1)
(
	python.Execute "from tik_manager import Sm3dsMax"
	python.Execute "Sm3dsMax.MainUI().show()"
)
"""
        saveVersion = """
macroScript saveVersion
category: "Tik Works"
tooltip: "Tik Manager - Save Version"
ButtonText: "TM_SaveV"
icon: #("SceneManager",2)
(
	python.Execute "from tik_manager import Sm3dsMax"
	python.Execute "Sm3dsMax.MainUI().saveAsVersionDialog()"
)"""
        imageViewer = """
macroScript imageViewer
category: "Tik Works"
tooltip: "Tik Manager - Image Viewer"
ButtonText: "ImageViewer"
icon: #("SceneManager",4)
(
    python.Execute "from tik_manager import Sm3dsMax"
    python.Execute "tik_imageViewer = Sm3dsMax.MainUI()"
    python.Execute "tik_imageViewer.onIviewer()"
)"""
        makePreview = """
macroScript makePreview
category: "Tik Works"
tooltip: "Tik Manager - Make Preview"
ButtonText: "Make Preview"
icon: #("SceneManager",5)
(
	python.Execute "from tik_manager import Sm3dsMax"
	python.Execute "Sm3dsMax.MaxManager().createPreview()"
)"""
        projectMaterials = """
macroScript projectMaterials
category: "Tik Works"
tooltip: "Tik Manager - Project Materials"
ButtonText: "Project Materials"
icon: #("SceneManager",6)
(
	python.Execute "from tik_manager import Sm3dsMax"
	python.Execute "tik_projectMaterials = Sm3dsMax.MainUI()"
	python.Execute "tik_projectMaterials.onPMaterials()"
)"""
        assetLibrary = """
macroScript assetLibrary
category: "Tik Works"
tooltip: "Tik Manager - Asset Library"
ButtonText: "Asset Library"
icon: #("SceneManager",7)
(
    python.Execute "from tik_manager import assetLibrary"
    python.Execute "assetLibrary = assetLibrary.MainUI().show()"
)"""
        _dumpContent(os.path.join(macrosDir, "tikManager-manager.mcr"), manager)
        _dumpContent(os.path.join(macrosDir, "tikManager-saveVersion.mcr"), saveVersion)
        _dumpContent(os.path.join(macrosDir, "tikManager-imageViewer.mcr"), imageViewer)
        _dumpContent(os.path.join(macrosDir, "tikManager-makePreview.mcr"), makePreview)
        _dumpContent(os.path.join(macrosDir, "tikManager-projectMaterials.mcr"), projectMaterials)
        _dumpContent(os.path.join(macrosDir, "tikManager-assetLibrary.mcr"), assetLibrary)

        searchLines = ['"Tik Manager"', "</Window>"]
        print("Removing older versions of Manager (Scene Manager)")
        oldLines = ['"sceneManager"', "</Window>"]
        oldState = inject(workspaceFile, "", between=oldLines, matchMode="includes", force=False)
        if oldState:
            print("Old version shelf (Scene Manager) removed")

        print("Injecting the Tik Manager toolbar to the workspace")
        state = inject(workspaceFile, workSpaceInjection, between=searchLines , matchMode="includes", force=False)
        if not state: # fresh install
            state = inject(workspaceFile, workSpaceInjection, before="</CUIWindows>", matchMode="includes")
            if not state:
                print("Toolbar cannot be injected to the workplace, you can set toolbar manually within 3ds max\nFailed => 3ds Max Setup\n")
                return

    print("Successfull => 3ds Max Setup")

    if prompt:
        # raw_input("Press Enter to continue...")
        r = input("Press Enter to continue...")
        assert isinstance(r, str)

def photoshopSetup(prompt=True):
    print("Starting Photoshop Setup")
    print("Checking files...")
    # check for running instances
    state = checkRuninngInstances("Photoshop")
    if state == -1:
        print("Installation Aborted by User")
        return # user aborts

    def copy_and_overwrite(from_path, to_path):
        # TODO make this method better
        if os.path.exists(to_path):
            shutil.rmtree(to_path)
        shutil.copytree(from_path, to_path)

    sourceDir = os.path.dirname(os.path.abspath(__file__))
    extensionSourceDir = os.path.join(sourceDir, "setupFiles", "Photoshop", "extensionFolder", "tikManager")
    if not os.path.isdir(extensionSourceDir):
        print("Photoshop installation error.\nCannot locate the extension folder.")
        # raw_input("Press Enter to continue")
        r = input("Press Enter to continue...")
        assert isinstance(r, str)
        return

    ## EDIT HTML FILE
    ## --------------

    indexHTMLFile = os.path.join(extensionSourceDir, "client", "index.html")

    managerIcon = os.path.join(sourceDir, "icons", "manager_ICON.png")
    saveVersionIcon = os.path.join(sourceDir, "icons", "saveVersion_ICON.png")

    indexHTMLContent = """<!DOCTYPE html>
<html>
<body style="background-color:black;">
<head>
    <meta charset="utf-8">
    <title>Tik Manager</title>
</head>
<body>
    <input type="image" id="tikManager-button" src="{0}" />
    <input type="image" id="version-button" src="{1}" />
    <!-- Do not display this at the moment
    <button id="open-button">Open</button>
    -->
    <script type="text/javascript" src="CSInterface.js"></script>
    <script type="text/javascript" src="index.js"></script>
</body>
</html>""".format(managerIcon, saveVersionIcon)

    _dumpContent(indexHTMLFile, indexHTMLContent, backup=False)

    ## EDIT VBS FILE
    appLocation = os.path.join(sourceDir, "bin", "SmPhotoshop.exe").replace("\\", "//")
    vbsFilePath = os.path.join(sourceDir, "bin", "saveVersion.vbs").replace("\\", "//")
    vbsContent = """Set oShell = CreateObject ("Wscript.Shell") 
Dim strArgs
strArgs = "%comspec% /K ""{0}"" saveVersion"
oShell.Run strArgs, 0, false""".format(appLocation)

    _dumpContent(vbsFilePath, vbsContent, backup=False)

    ## EDIT HOST (index.jsx) FILE
    ## --------------

    hostFile = os.path.join(extensionSourceDir, "host", "index.jsx")
    hostContent = """function tikUI(){
    var bat = new File("%s");
    bat.execute();
}
function tikSaveVersion(){
    var ver = new File("%s");
    ver.execute();
}
""" % (appLocation, vbsFilePath)

    _dumpContent(hostFile, hostContent, backup=False)

    userHomeDir = os.path.normpath(os.path.join(os.path.expanduser("~")))
    extensionTargetDir = os.path.join(userHomeDir, "AppData", "Roaming", "Adobe", "CEP", "extensions", "tikManager")

    copy_and_overwrite(extensionSourceDir, extensionTargetDir)

    # edit registry
    def getCSXkey(val):
        try:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, r'Software\Adobe\CSXS.%s' % val, 0, reg.KEY_ALL_ACCESS)
            reg.SetValueEx(key, "PlayerDebugMode", 1, reg.REG_SZ, "1")
            reg.CloseKey(key)
            return key
        except WindowsError:
            return None

    # map the function for all keys between CSXS.0 - CSXS.19
    map(lambda x: getCSXkey(x), range(20))

    if prompt:
        # raw_input("Press Enter to continue...")
        r = input("Press Enter to continue...")
        assert isinstance(r, str)

def installAll():
    mayaSetup(prompt=False)
    houdiniSetup(prompt=False)
    maxSetup(prompt=False)
    nukeSetup(prompt=False)
    photoshopSetup(prompt=False)
    # raw_input("Setup Completed. Press Enter to Exit...")
    r = input("Setup Completed. Press Enter to Exit...")
    assert isinstance(r, str)
    sys.exit()

def prepareCommonFolder(targetCommonFolderPath):
    """Copy common files to the common folder if they are not already exist"""
    currentCommonPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "TikManager_Commons")

    # if the initial install folder will be used as common folder:
    if os.path.normpath(currentCommonPath) == os.path.normpath(targetCommonFolderPath):
        return True
    folderCheck(targetCommonFolderPath)
    folderCheck(os.path.join(targetCommonFolderPath, "icons"))

    files = [
        ["", "sceneManagerDefaults.json"],
        ["", "sceneManagerUsers.json"],
        ["", "softwareDatabase.json"],
        ["", "SubmitMayaToDeadlineCustom.mel"],
        ["", "tikConventions.json"],
        ["", "alExportSettings.json"],
        ["", "alImportSettings.json"],
        ["", "conversionLUT.json"],
        ["", "adminPass.psw"],
        # ["icons", "iconHoudini.png"],
        # ["icons", "iconMax.png"],
        # ["icons", "iconMaya.png"],
        # ["icons", "iconNuke.png"],
        # ["icons", "iconPS.png"],
    ]

    for file in files:
        # check if the folder exists, create if it doesnt
        folderCheck(os.path.join(targetCommonFolderPath, file[0]))
        # check if the file exists, copy if it doesnt
        targetFile = os.path.join(targetCommonFolderPath, file[0], file[1])
        if os.path.isfile(targetFile):
            continue
        else:
            sourceFile = os.path.join(currentCommonPath, file[0], file[1])
            shutil.copyfile(sourceFile, targetFile)
            try:
                print("debug:", sourceFile, targetFile)
                # shutil.copyfile(sourceFile, targetFile)
            except:
                print("Cannot copy %s to %s" %(file[1], os.path.join(targetCommonFolderPath, file[0])))
                # raw_input("ABORTING")
                r = input("ABORTING")
                assert isinstance(r, str)

                return False
    return True

def folderCheck(folder):
    if not os.path.isdir(folder):
        os.makedirs(os.path.normpath(folder))

def decideNetworkPath():
    """Yes/No question terminal"""
    yes = {'yes', 'y', 'ye', ''}
    no = {'no', 'n'}

    currentCommonPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "TikManager_Commons")

    print("""
Select Common Folder
--------------------""")
    print("Current file path is %s" %currentCommonPath)
    msg = "Do you want to use this as common folder?  [y/n]"
    # choice = raw_input(msg).lower()
    choice = input(msg)
    assert isinstance(choice, str)

    if choice.lower() in yes:
        return currentCommonPath
    elif choice.lower() in no:
        cf_path = ""
        while not os.path.isdir(cf_path):
            # cf_path = raw_input("Enter the common folder path:")
            cf_path = input("Enter the common folder path:")
            assert isinstance(cf_path, str)
            if not os.path.isdir(cf_path):
                print("invalid path. Try again")
            else:
                return cf_path
        else:
            pass
    else:
        print("Please respond with 'yes' or 'no'")
        return ""

header = """
---------------------------
Scene Manager Setup v%s
---------------------------""" % _version.__version__


menuItems = [
    { "Maya": mayaSetup },
    { "Houdini": houdiniSetup },
    { "3dsMax": maxSetup },
    { "Nuke": nukeSetup },
    { "Photoshop": photoshopSetup },
    { "Install All": installAll },
    { "Exit": sys.exit}
]


def okCancel(msg):
    # reply = str(raw_input(msg+' (y/n): ')).lower().strip()
    reply = input(msg+' (y/n): ')
    assert isinstance(reply, str)
    reply = reply.lower().strip()

    if reply[0] == 'y':
        return 1
    if reply[0] == 'n':
        return 2
    else:
        return okCancel(msg)

def cli():
    print(header)
    networkPath = ""
    while networkPath == "":
        networkPath = decideNetworkPath()
    print("Preparing Common Folder")
    prepareCommonFolder(networkPath)
    userHomeDir = os.path.normpath(os.path.join(os.path.expanduser("~")))
    localSettingsDir = os.path.join(userHomeDir, "Documents", "TikManager")
    if not os.path.isdir(os.path.normpath(localSettingsDir)):
        os.makedirs(os.path.normpath(localSettingsDir))
    smFile = os.path.join(localSettingsDir, "smCommonFolder.json")
    _dumpJson(os.path.normpath(networkPath), smFile)
    while True:
        print("""
    Choose the software you want to setup Scene Manager:
    ----------------------------------------------------""")
        for item in menuItems:
            # print("dbg",list(item)[0])
            print("[{0}] {1}".format(str(menuItems.index(item)), list(item)[0]))
            # print("[" + str(menuItems.index(item)) + "] ") + list(item)[0]
        # choice = raw_input(">> ")
        choice = input(">> ")
        assert isinstance(choice, str)

        try:
            if int(choice) < 0: raise ValueError
            # Call the matching function

            # menuItems[int(choice)].values()[0]() # only compatible with py2
            # python3 compatibility
            key = list(menuItems[int(choice)])[0]
            cmd = menuItems[int(choice)][key]
            cmd()

            os.system('cls')
        except (ValueError, IndexError):
            pass

def noCli(networkPath, softwareList):
    print("Preparing Common Folder")
    prepareCommonFolder(networkPath)
    userHomeDir = os.path.normpath(os.path.join(os.path.expanduser("~")))
    localSettingsDir = os.path.join(userHomeDir,"Documents","TikManager")
    if not os.path.isdir(os.path.normpath(localSettingsDir)):
        os.makedirs(os.path.normpath(localSettingsDir))
    smFile = os.path.join(localSettingsDir, "smCommonFolder.json")

    _dumpJson(os.path.normpath(networkPath), smFile)

    swDictionary = {
        "maya": mayaSetup,
        "houdini": houdiniSetup,
        "3dsmax": maxSetup,
        "nuke": nukeSetup,
        "photoshop": photoshopSetup
    }

    for sw in softwareList:
        print(sw)
        if sw.lower() not in swDictionary.keys():
            print("%s is not in the supported product list. Skipping" %sw)
            continue

        swDictionary[sw.lower()](prompt=False)
    # raw_input("Setup Completed. Press Enter to Exit...")
    r = input("Setup Completed. Press Enter to Exit...")
    assert isinstance(r, str)


def main(argv):
    # parse the arguments
    opts, args = getopt.getopt(argv, "n:h:v", ["networkpath", "help", "verbose"])

    if not opts and not args:
        cli()
    else:
        if not opts and args:
            print("You must enter -n argument")
            sys.exit()

        networkPath = ""
        for o, a in opts:
            if o == "-n":
                networkPath = a
            else:
                assert False, "unhandled option"
                # raw_input("Something went wrong.. Try manual installation")
                r = input("Something went wrong.. Try manual installation")
                assert isinstance(r, str)

        softwareList = args


        folderCheck(networkPath)
        print("networkPath", networkPath)
        print("softwareList", softwareList)

        noCli(networkPath, softwareList)

        # isCli = True
        # if isCli:
        #     cli()
        # else:
        #     noCli("C:\\", ["Maya", "3dsMax", "Houdini", "Nuke"])

def _dumpJson(data, file):
    """Saves the data to the json file"""
    name, ext = os.path.splitext(file)
    tempFile = "{0}.tmp".format(name)
    with open(tempFile, "w") as f:
        json.dump(data, f, indent=4)
    shutil.copyfile(tempFile, file)
    os.remove(tempFile)

if __name__ == "__main__":
    main(sys.argv[1:])
