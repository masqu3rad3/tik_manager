import sys
import os
import shutil
import psutil

def checkRuninngInstances(sw):
    running = True
    aborted=False

    while not aborted and running:
        # closed = not (sw in (p.name() for p in psutil.process_iter()))
        matchList = [p for p in psutil.process_iter() if p.name().startswith(sw)]
        if matchList:
            running = True
        else:
            running = False

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
    if backup:
        shutil.copyfile(filePath)
    name, ext = os.path.splitext(filePath)
    if backup:
        if os.path.isdir(filePath):
            backupFile = "{0}.bak".format(name)
            shutil.copyfile(filePath, backupFile)
            print "Backup complete\n%s => %s" %(filePath, backupFile)
    tempFile = "{0}_TMP{1}".format(name, ext)
    f = open(tempFile, "w+")
    f.writelines(contentList)
    f.close()
    shutil.copyfile(tempFile, filePath)
    os.remove(tempFile)

def inject(file, newContentList, between=None, after=None, before=None, matchMode="equal", force=True, searchDirection="forward"):
    if type(newContentList) == str:
        newContentList = [newContentList]

    # try:
    #     content = _loadContent(file)
    # except IOError:
    #     print "Error Writing to file %s aborting" %file
    #     return None
    if not os.path.isfile(file):
        if force:
            _dumpContent(file, newContentList)
            print "Created %s with new content" % file
            return True
        else:
            print "File does not exist (%s)" %file
            return False

    contentList = _loadContent(file)

    # if the file is empty ->
    if not contentList:
        if force:
            _dumpContent(file, newContentList)
            print "New content added to empty %s" %file
            return True
        else:
            print "File is empty, nothing to change"
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
                print "Cannot find Start Line. Skipping replace injection"
                return

    elif after:
        startIndex = collectIndex(searchList, after, mode=matchMode)
        if not startIndex:
            print "Cannot find After Line. Aborting"
            return
        endIndex = startIndex+1

    elif before:
        startIndex = collectIndex(searchList, before, mode=matchMode)
        if not startIndex:
            print "Cannot find After Line. Aborting"
            return
        endIndex = startIndex-1

    if searchDirection == "backward":
        injectedContent = contentList[:-endIndex] + newContentList + contentList[-startIndex - 1:]
    else:
        injectedContent = contentList[:startIndex] + newContentList + contentList[endIndex + 1:]


    _dumpContent(file, injectedContent)
    return True


# def createOrReplace(file, newContentList, startLine="# start Scene Manager\n", endLine="# end Scene Manager\n"):
#     # if there is no file
#     if os.path.isfile(file):
#         contentList = _loadContent(file)
#
#         # if the file is empty ->
#         if not contentList:
#             _dumpContent(file, newContentList)
#             return
#
#         # make sure last line ends with a break line
#         if "\n" not in contentList[-1] and contentList[-1] is not "":
#             contentList[-1] = "%s\n" % (contentList[-1])
#         # find start / end of previous content
#         startIndex = -1
#         endIndex = -1
#         for i in contentList:
#             if i == startLine:
#                 startIndex = contentList.index(i)
#             if i == endLine:
#                 endIndex = contentList.index(i)
#
#         if ((startIndex == -1) and (endIndex != -1)) or ((startIndex != -1) and (endIndex == -1)):
#             raise Exception("Cannot edit %s. Edit it manually" % file)
#         del contentList[startIndex: endIndex + 1]
#         dumpList = contentList + newContentList
#         _dumpContent(file, dumpList)
#
#     else:
#         _dumpContent(file, newContentList)

def mayaSetup(prompt=True):
    # Check file integrity
    print "Starting Maya Setup"
    print "Checking files..."
    networkDir = os.path.dirname(os.path.abspath(__file__))
    fileList = ["__init__.py",
                "_version.py",
                "ImMaya.py",
                "IvMaya.py",
                "pyseq.py",
                "Qt.py",
                "SmMaya.py",
                "SmRoot.py",
                "SubmitMayaToDeadlineCustom.mel",
                "adminPass.psw"
                ]
    for file in fileList:
        if not os.path.isfile(os.path.join(networkDir, file)):
            # if the extension is pyc give it another chance
            if os.path.splitext(file)[1] == ".py":
                if not os.path.isfile(os.path.join(networkDir, "%sc" %file)): # make the extension pyc
                    print "Missing file:\nCannot find %s or %sc" % (file, file)
                    raw_input("Press Enter to continue...")
                    return
            else:
                print "Missing file:\nCannot find %s" %file
                raw_input("Press Enter to continue...")
                return

    # check for running instances
    state = checkRuninngInstances("maya")
    if state == -1:
        print "Installation Aborted by User"
        return # user aborts

    upNetworkDir = os.path.abspath(os.path.join(networkDir, os.pardir))
    userHomeDir = os.path.normpath(os.path.join(os.path.expanduser("~")))
    userDocDir = os.path.join(userHomeDir, "Documents")
    userMayaDir = os.path.join(userDocDir, "maya")
    userScriptsDir = os.path.join(userMayaDir, "scripts")
    userSetupFile = os.path.join(userScriptsDir, "userSetup.py")

    print "Finding Maya Versions..."
    mayaVersions = [x for x in os.listdir(userMayaDir) if os.path.isdir(os.path.join(userMayaDir, x)) and x.startswith('20')]
    if mayaVersions:
        print "Found Maya Versions: %s " % str(mayaVersions)
    else:
        print "No Maya version can be found, try manual installation"
        raw_input("Press Enter to continue...")
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
        "    from tik_manager import SmMaya\n",
        "    m = SmMaya.TikManager()\n",
        "    m.regularSaveUpdate()\n",
        "\n",
        "initFolder('{0}')\n".format((upNetworkDir.replace("\\", "//"))),
        "maya.utils.executeDeferred('SMid = OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterSave, smUpdate)')\n",
        "# end Scene Manager\n"
    ]
    # createOrReplace(userSetupFile, newUserSetupContent)
    inject(userSetupFile, newUserSetupContent, between=("# start Scene Manager\n", "# end Scene Manager\n"))
    print "userSetup updated at: %s" %(userSetupFile)

    ## SHELF


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
        folderCheck(shelfDir)
        shelfFile = os.path.join(shelfDir, "shelf_SceneManager.mel")
        _dumpContent(shelfFile, shelfContent)
        print "Shelf created for %s" %v

    print "Successfull => Maya Setup"
    if prompt:
        raw_input("Press Enter to continue...")

def houdiniSetup(prompt=True):

    # TODO : implement workspace injection to XML
    # TODO : TEST IT
    # Check file integrity
    print "Starting Houdini Setup"
    print "Checking files..."
    networkDir = os.path.dirname(os.path.abspath(__file__))
    fileList = ["__init__.py",
                "_version.py",
                "pyseq.py",
                "SmHoudini.py",
                "SmRoot.py",
                "adminPass.psw"
                ]
    for file in fileList:
        if not os.path.isfile(os.path.join(networkDir, file)):
            # if the extension is pyc give it another chance
            if os.path.splitext(file)[1] == ".py":
                if not os.path.isfile(os.path.join(networkDir, "%sc" %file)): # make the extension pyc
                    print "Missing file:\nCannot find %s or %sc" % (file, file)
                    raw_input("Press Enter to continue...")
                    return
            else:
                print "Missing file:\nCannot find %s" %file
                raw_input("Press Enter to continue...")
                return

    # check for running instances
    state = checkRuninngInstances("houdini")
    if state == -1:
        print "Aborted bt user"
        return # user aborts

    upNetworkDir = os.path.abspath(os.path.join(networkDir, os.pardir))
    userHomeDir = os.path.normpath(os.path.join(os.path.expanduser("~")))
    userDocDir = os.path.join(userHomeDir, "Documents")
    print "Finding Houdini Versions..."
    houdiniVersions = [x for x in os.listdir(userDocDir) if
                    os.path.isdir(os.path.join(userDocDir, x)) and x.startswith('houdini')]
    if houdiniVersions:
        print "Found Houdini Versions: %s " % str(houdiniVersions)
    else:
        print "No Houdini version can be found, try manual installation"
        raw_input("Press Enter to continue...")
        return
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
        folderCheck(scriptsFolder)
        sScriptFile = os.path.join(scriptsFolder, "456.py")
        # createOrReplace(sScriptFile, sScriptContent)
        inject(sScriptFile, sScriptContent, between=("# start Scene Manager\n", "# end Scene Manager\n"))

        print "Path config appended to %s" %sScriptFile

        ## SHELF
        shelfDir = os.path.join(userDocDir, v, "toolbar")
        # create the directory if does not exist
        folderCheck(shelfDir)
        shelfFile = os.path.join(shelfDir, "sceneManager.shelf")
        _dumpContent(shelfFile, shelfContent)

        print "Scene manager shelf created or updated at %s" % shelfFile

    print "\nInside Houdini, Scene Manager shelf should be enabled for the desired shelf set by clicking to '+' icon and selecting 'shelves' sub menu."

    print "Successfull => Houdini Setup"

    if prompt:
        raw_input("Press Enter to continue...")

def maxSetup(prompt=True):

    networkDir = os.path.dirname(os.path.abspath(__file__))
    upNetworkDir = os.path.abspath(os.path.join(networkDir, os.pardir))
    fileList = ["__init__.pyc",
                "_version.pyc",
                "pyseq.pyc",
                "SmRoot.pyc",
                "SubmitMayaToDeadlineCustom.mel",
                "adminPass.psw"
                ]

    for file in fileList:
        if not os.path.isfile(os.path.join(networkDir, file)):
            # if the extension is pyc give it another chance
            if os.path.splitext(file)[1] == ".py":
                if not os.path.isfile(os.path.join(networkDir, "%sc" %file)): # make the extension pyc
                    print "Missing file:\nCannot find %s or %sc" % (file, file)
                    raw_input("Press Enter to continue...")
                    return
            else:
                print "Missing file:\nCannot find %s" %file
                raw_input("Press Enter to continue...")
                return

    # check for running instances
    state = checkRuninngInstances("3dsmax")
    if state == -1:
        print "Installation Aborted by User"
        return # user aborts

    userHomeDir = os.path.normpath(os.path.join(os.path.expanduser("~")))
    userMaxDir = os.path.join(userHomeDir, "AppData", "Local", "Autodesk", "3dsMax")

    # ICON PATHS
    pack_16a = os.path.join(networkDir, "icons", "SceneManager_16a.bmp").replace("\\", "\\\\")
    pack_16i = os.path.join(networkDir, "icons", "SceneManager_16i.bmp").replace("\\", "\\\\")
    pack_24a = os.path.join(networkDir, "icons", "SceneManager_24a.bmp").replace("\\", "\\\\")
    pack_24i = os.path.join(networkDir, "icons", "SceneManager_24i.bmp").replace("\\", "\\\\")

    workSpaceInjection ="""        <Window name="sceneManager" type="T" rank="0" subRank="2" hidden="0" dPanel="1" tabbed="0" curTab="-1" cType="1" toolbarRows="1" toolbarType="3">
            <FRect left="198" top="125" right="310" bottom="199" />
            <DRect left="1395" top="53" right="1504" bottom="92" />
            <DRectPref left="2147483647" top="2147483647" right="-2147483648" bottom="-2147483648" />
            <CurPos left="198" top="125" right="310" bottom="199" floating="1" panelID="16" />
            <Items>
                <Item typeID="2" type="CTB_MACROBUTTON" width="0" height="0" controlID="0" macroTypeID="3" macroType="MB_TYPE_ACTION" actionTableID="647394" imageID="-1" imageName="" actionID="manager`SceneManager" tip="Scene Manager" label="Scene Manager" />
                <Item typeID="2" type="CTB_MACROBUTTON" width="0" height="0" controlID="0" macroTypeID="3" macroType="MB_TYPE_ACTION" actionTableID="647394" imageID="-1" imageName="" actionID="saveVersion`SceneManager" tip="Scene Manager - Version Save" label="Save Version" />
                <Item typeID="2" type="CTB_MACROBUTTON" width="0" height="0" controlID="0" macroTypeID="3" macroType="MB_TYPE_ACTION" actionTableID="647394" imageID="-1" imageName="" actionID="makePreview`SceneManager" tip="Scene Manager - Make Preview" label="Make Preview" />
            </Items>
        </Window>\n"""

    print "Finding 3ds Max Versions..."
    maxVersions = [x for x in os.listdir(userMaxDir)]
    if maxVersions:
        print "Found 3ds Max Versions: %s " % str(maxVersions)
    else:
        print "No 3ds Max version can be found, try manual installation"
        raw_input("Press Enter to continue...")
        return


    for v in maxVersions:
        print "Setup for version %s" %v
        sScriptsDir = os.path.join(userMaxDir, v, "ENU", "scripts", "startup")
        folderCheck(sScriptsDir)
        iconsDir = os.path.join(userMaxDir, v, "ENU", "usericons")
        folderCheck(iconsDir)
        macrosDir = os.path.join(userMaxDir, v, "ENU", "usermacros")
        folderCheck(macrosDir)
        print "Copying Icon sets..."
        print iconsDir
        shutil.copy(pack_16a, os.path.normpath(os.path.join(iconsDir, "SceneManager_16a.bmp")))
        shutil.copy(pack_16i, os.path.normpath(os.path.join(iconsDir, "SceneManager_16i.bmp")))
        shutil.copy(pack_24a, os.path.normpath(os.path.join(iconsDir, "SceneManager_24a.bmp")))
        shutil.copy(pack_24i, os.path.normpath(os.path.join(iconsDir, "SceneManager_24i.bmp")))

        workspaceDir =  os.path.join(userMaxDir, v, "ENU", "en-US", "UI", "Workspaces", "usersave")
        folderCheck(workspaceDir)
        workspaceFile = os.path.join(workspaceDir, "Workspace1__usersave__.cuix")\

        # workSpaceContentList = _loadContent(workspaceFile)

        print "Creating Callback and path initialization startup script"
        startupScriptContent = """
python.Execute "import sys"
python.Execute "import os"
python.Execute "import MaxPlus"
python.Execute "sys.path.append(os.path.normpath('{0}'))"
python.Execute "def smUpdate(*args):\\n	from tik_manager import Sm3dsMax\\n	m = Sm3dsMax.MaxManager()\\n	m.saveCallback()"
python.Execute "MaxPlus.NotificationManager.Register(14, smUpdate)"
""".format(upNetworkDir.replace("\\", "//"))

        _dumpContent(os.path.join(sScriptsDir, "smManagerCallback.ms"), startupScriptContent)


        print "Creating Macroscripts"
        manager = """
macroScript TIK_sm3dsMax
category: "SceneManager"
tooltip: "Scene Manager"
ButtonText: "SM"
icon: #("SceneManager",1)
(
	python.Execute "from tik_manager import Sm3dsMax"
	python.Execute "Sm3dsMax.MainUI().show()"
)
"""
        saveVersion = """
macroScript TIK_smSaveVersion
category: "SceneManager"
tooltip: "Scene Manager - Save Version"
ButtonText: "SM_SaveV"
icon: #("SceneManager",2)
(
	python.Execute "from tik_manager import Sm3dsMax"
	python.Execute "Sm3dsMax.MainUI().saveAsVersionDialog()"
)"""
        makePreview = """
macroScript TIK_makePreview
category: "SceneManager"
tooltip: "Scene Manager - Make Preview"
ButtonText: "Make Preview"
icon: #("SceneManager",5)
(
	python.Execute "from tik_manager import Sm3dsMax"
	python.Execute "reload(Sm3dsMax)"
	python.Execute "Sm3dsMax.MaxManager().createPreview()"
)"""
        _dumpContent(os.path.join(macrosDir, "Tik Works-TIK_sm3dsMax.mcr"), manager)
        _dumpContent(os.path.join(macrosDir, "Tik Works-TIK_smSaveVersion.mcr"), saveVersion)
        _dumpContent(os.path.join(macrosDir, "Tik Works-TIK_smPreview.mcr"), makePreview)

        searchLines = ['"sceneManager"', "</Window>"]
        print "Injecting the Scene Manager toolbar to the workspace"
        state = inject(workspaceFile, workSpaceInjection, between=searchLines , matchMode="includes", force=False)
        if not state: # fresh install
            state = inject(workspaceFile, workSpaceInjection, before="</CUIWindows>", matchMode="includes")
            if not state:
                print "Toolbar cannot be injected to the workplace, you can set toolbar manually within 3ds max\nFailed => 3ds Max Setup\n"
                return

    print "Successfull => 3ds Max Setup"

    if prompt:
        raw_input("Press Enter to continue...")

def installAll():
    mayaSetup(prompt=False)
    houdiniSetup(prompt=False)
    maxSetup(prompt=False)
    raw_input("Setup Completed. Press Enter to Exit...")
    sys.exit()

def folderCheck(folder):
    if not os.path.isdir(folder):
        os.makedirs(os.path.normpath(folder))


header = """
-------------------
Scene Manager Setup
-------------------

Choose the software you want to setup Scene Manager:"""


menuItems = [
    { "Maya": mayaSetup },
    { "Houdini": houdiniSetup },
    { "3dsMax": maxSetup },
    { "Install All": installAll },
    { "Exit": sys.exit}
]


def okCancel(msg):
    reply = str(raw_input(msg+' (y/n): ')).lower().strip()
    if reply[0] == 'y':
        return 1
    if reply[0] == 'n':
        return 2
    else:
        return okCancel(msg)


def main():
    while True:
        print (header)
        for item in menuItems:
            print ("[" + str(menuItems.index(item)) + "] ") + item.keys()[0]
        choice = raw_input(">> ")
        try:
            if int(choice) < 0 : raise ValueError
            # Call the matching function
            menuItems[int(choice)].values()[0]()
            os.system('cls')


        except (ValueError, IndexError):
            pass


if __name__ == "__main__":
    main()
