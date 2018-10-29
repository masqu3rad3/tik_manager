import sys
import os
import shutil
import psutil
# import win32ui
# import win32con


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

        if ((startIndex == -1) and (endIndex != -1)) or ((startIndex != -1) and (endIndex == -1)):
            raise Exception("Cannot edit %s. Edit it manually" % file)
        del contentList[startIndex: endIndex + 1]
        dumpList = contentList + newContentList
        _dumpContent(file, dumpList)

    else:
        _dumpContent(file, newContentList)

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
            if os.path.splitext(file)[1] == "py":
                if not os.path.isfile(os.path.join(networkDir, "%sc" %file)): # make the extension pyc
                    print "Missing file:\nCannot find %s" % file
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
            if os.path.splitext(file)[1] == "py":
                if not os.path.isfile(os.path.join(networkDir, "%sc" %file)): # make the extension pyc
                    print "Missing file:\nCannot find %s" % file
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
        createOrReplace(sScriptFile, sScriptContent)

        print "Path config appended to %s" %sScriptFile

        ## SHELF
        shelfDir = os.path.join(userDocDir, v, "toolbar")
        # create the directory if does not exist
        folderCheck(shelfDir)
        shelfFile = os.path.join(shelfDir, "sceneManager.shelf")
        _dumpContent(shelfFile, shelfContent)

        print "Scene manager shelf created or updated at %s" % shelfFile

    print "\nInside Houdini, Scene Manager shelf should be enabled for the desired shelf set by clicking to '+' icon and selecting 'shelves' sub menu."

    print "Successfull => Maya Setup"

    if prompt:
        raw_input("Press Enter to continue...")

def maxSetup(prompt=True):

    #WIP
    # "C:\Program Files\Autodesk\3ds Max 2017\scripts\startup"
    # "C:\Program Files\Autodesk\3ds Max 2017\scripts"
    # "C:\Users\kutlu\AppData\Local\Autodesk\3dsMax\2017 - 64bit\ENU\scripts"
    # "C:\Users\kutlu\AppData\Local\Autodesk\3dsMax\2017 - 64bit\ENU\scripts\startup"
    # "C:\Users\kutlu\AppData\Local\Autodesk\3dsMax\2017 - 64bit\ENU\usericons"
    # "C:\Users\kutlu\AppData\Local\Autodesk\3dsMax\2017 - 64bit\ENU\usermacros"

    networkDir = os.path.dirname(os.path.abspath(__file__))
    fileList = ["__init__.pyc",
                "_version.pyc",
                "pyseq.pyc",
                "SmRoot.pyc",
                "SmStandalone.pyc",
                "SubmitMayaToDeadlineCustom.mel",
                "adminPass.psw"
                ]
    for file in fileList:
        if not os.path.isfile(os.path.join(networkDir, file)):
            # if the extension is pyc give it another chance
            if os.path.splitext(file)[1] == "py":
                if not os.path.isfile(os.path.join(networkDir, "%sc" %file)): # make the extension pyc
                    print "Missing file:\nCannot find %s" % file
                    raw_input("Press Enter to continue...")
                    return
            else:
                print "Missing file:\nCannot find %s" %file
                raw_input("Press Enter to continue...")
                return

    userHomeDir = os.path.normpath(os.path.join(os.path.expanduser("~")))
    userMaxDir = os.path.join(userHomeDir, "AppData", "Local", "Autodesk", "3dsMax")

    # ICON PATHS
    pack_16a = os.path.join(networkDir, "icons", "SceneManager_16a.bmp").replace("\\", "\\\\")
    pack_16i = os.path.join(networkDir, "icons", "SceneManager_16i.bmp").replace("\\", "\\\\")
    pack_24a = os.path.join(networkDir, "icons", "SceneManager_24a.bmp").replace("\\", "\\\\")
    pack_24i = os.path.join(networkDir, "icons", "SceneManager_24i.bmp").replace("\\", "\\\\")

    workSpaceInjection ="""<Window name="findThisBar" type="T" rank="0" subRank="2" hidden="0" dPanel="1" tabbed="0" curTab="-1" cType="1" toolbarRows="1" toolbarType="3">
            <FRect left="828" top="213" right="937" bottom="287" />
            <DRect left="1395" top="53" right="1504" bottom="92" />
            <DRectPref left="2147483647" top="2147483647" right="-2147483648" bottom="-2147483648" />
            <CurPos left="1395" top="53" right="1504" bottom="92" floating="0" panelID="1" />
            <Items>
                <Item typeID="2" type="CTB_MACROBUTTON" width="0" height="0" controlID="0" macroTypeID="3" macroType="MB_TYPE_ACTION" imageID="-1" imageName="" actionID="manager`SceneManager" tip="Scene Manager" label="Scene Manager" />
                <Item typeID="2" type="CTB_MACROBUTTON" width="0" height="0" controlID="0" macroTypeID="3" macroType="MB_TYPE_ACTION" imageID="-1" imageName="" actionID="saveVersion`SceneManager" tip="Scene Manager - Version Save" label="Save Version" />
                <Item typeID="2" type="CTB_MACROBUTTON" width="0" height="0" controlID="0" macroTypeID="3" macroType="MB_TYPE_ACTION" imageID="-1" imageName="" actionID="makePreview`SceneManager" tip="Scene Manager - Make Preview" label="Make Preview" />
            </Items>
        </Window>"""

    print "Finding 3ds Max Versions..."
    maxVersions = [x for x in os.listdir(userMaxDir)]

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
        shutil.copy(pack_16a, os.path.join(iconsDir, "SceneManager_16a.bmp"))
        shutil.copy(pack_16i, os.path.join(iconsDir, "SceneManager_16i.bmp"))
        shutil.copy(pack_24a, os.path.join(iconsDir, "SceneManager_24a.bmp"))
        shutil.copy(pack_24i, os.path.join(iconsDir, "SceneManager_24i.bmp"))

        workspaceDir =  os.path.join(userMaxDir, v, "ENU", "en-US", "UI", "Workspaces", "usersave")
        folderCheck(workspaceDir)
        workspaceFile = os.path.join(workspaceDir, "Workspace1__usersave__.cuix")\

        workSpaceContentList = _loadContent(workspaceFile)

        startLine = None
        for line in workSpaceContentList:
            if "findThisBar" in line:
                print "found"
                startLine = workSpaceContentList.index(line)
                print "line", startLine
                break

        if startLine:
            for line in workSpaceContentList[startLine:]:
                print line
                if "</Window>" in line:
                    endLine = workSpaceContentList.index(line)
                    break

        # TODO : Write an inject function








    print "Successfull => 3ds Max Setup"

    if prompt:
        raw_input("Press Enter to continue...")

def installAll():
    mayaSetup(prompt=False)
    houdiniSetup(prompt=False)
    maxSetup()

def folderCheck(folder):
    if not os.path.isdir(folder):
        os.makedirs(os.path.normpath(folder))
# checkIntegrity()
# houdiniSetup()

# runCode = True
# def terminate():
#     runCode = False


header = """
-------------------
Scene Manager Setup
-------------------

Choose the software you want to setup Scene Manager:"""

# colors = {
#         'blue': '\033[94m',
#         'pink': '\033[1;35m',
#         'green': '\033[92m',
#         }

menuItems = [
    { "Maya": mayaSetup },
    { "Houdini": houdiniSetup },
    { "3dsMax": maxSetup },
    { "Install All": installAll },
    { "Exit": sys.exit}
]

# def message():
#     print "Setup Cannot Continue"

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
        # os.system('cls')
        # Print some badass ascii art header here !
        # print colorize(header, 'green')
        print (header)
        # print colorize('version 0.1\n', 'green')
        for item in menuItems:
            # print colorize("[" + str(menuItems.index(item)) + "] ", 'blue') + item.keys()[0]
            print ("[" + str(menuItems.index(item)) + "] ") + item.keys()[0]
        choice = raw_input(">> ")
        try:
            if int(choice) < 0 : raise ValueError
            # Call the matching function
            menuItems[int(choice)].values()[0]()
            os.system('cls')


        except (ValueError, IndexError):
            pass

# def colorize(string, color):
#     if not color in colors: return string
#     return colors[color] + string + '\033[0m'

# Main Program
# main()
if __name__ == "__main__":
    # main()
    maxSetup()