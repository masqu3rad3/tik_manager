"""Manager is the main module for tik_manager.
Manages the file names and conventions for Save, Load, Reference and Playblast operations
"""
import ctypes
import datetime
import filecmp
import ftplib
import io
import json
import os
import platform
import pprint
import re
import socket
from shutil import copyfile

import Qt
import maya.cmds as cmds
import maya.mel
import maya.mel as mel
import pymel.core as pm
from Qt import QtWidgets, QtCore, QtGui
from maya import OpenMayaUI as omui
import _version

if Qt.__binding__ == "PySide":
    from shiboken import wrapInstance
elif Qt.__binding__.startswith('PyQt'):
    from sip import wrapinstance as wrapInstance
else:
    from shiboken2 import wrapInstance

__author__ = "Arda Kutlu"
__copyright__ = "Copyright 2018, Scene Manager for Maya Project"
__credits__ = []
__license__ = "GPL"
__maintainer__ = "Arda Kutlu"
__email__ = "ardakutlu@gmail.com"
__status__ = "Development"

SM_Version = "Scene Manager v%s" %(_version.__version__)


def getOldestFile(rootfolder, extension=".avi"):
    """
    Gets the oldest file in given folder
    Args:
        rootfolder: (String) Folder to search
        extension: (String) Extensions to filter down

    Returns: (String) OldestFile
    """
    return min(
        (os.path.join(dirname, filename)
         for dirname, dirnames, filenames in os.walk(rootfolder)
         for filename in filenames
         if filename.endswith(extension)),
        key=lambda fn: os.stat(fn).st_mtime)

def getNewestFile(rootfolder, extension=".avi"):
    """
    Gets the most recent file in given folder
    Args:
        rootfolder: (String) Folder to search
        extension: (String) Extensions to filter down

    Returns: (String) MostRecentFile
    """
    return max(
        (os.path.join(dirname, filename)
         for dirname, dirnames, filenames in os.walk(rootfolder)
         for filename in filenames
         if filename.endswith(extension)),
        key=lambda fn: os.stat(fn).st_mtime)


def killTurtle():
    """
    Kills the turtle nodes
    Returns:None

    """
    try:
        pm.lockNode('TurtleDefaultBakeLayer', lock=False)
        pm.delete('TurtleDefaultBakeLayer')
    except:
        pass
    try:
        pm.lockNode('TurtleBakeLayerManager', lock=False)
        pm.delete('TurtleBakeLayerManager')
    except:
        pass
    try:
        pm.lockNode('TurtleRenderOptions', lock=False)
        pm.delete('TurtleRenderOptions')
    except:
        pass
    try:
        pm.lockNode('TurtleUIOptions', lock=False)
        pm.delete('TurtleUIOptions')
    except:
        pass
    # pm.unloadPlugin("Turtle.mll", f=True)
    try:
        pm.unloadPlugin("Turtle.mll")
    except:
        pass


def checkRequirements():
    """
    Checks the requirements for platform and administrator rights. Returns [None, None] if passes both
    Returns: (List) [ErrorCode, ErrorMessage]

    """
    ## check platform
    currentOs = platform.system()
    if currentOs != "Linux" and currentOs != "Windows":
        return -1, ["OS Error", "Operating System is not supported", "Scene Manager only supports Windows and Linux Operating Systems"]
    ## check admin rights
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    if not is_admin:
        return -1, ["Admin Rights", "Maya does not have the administrator rights", "You need to run Maya as administrator to work with Scene Manager"]
    return None, None




# noinspection PyArgumentList
def getMayaMainWindow():
    """
    Gets the memory adress of the main window to connect Qt dialog to it.
    Returns:
        (long) Memory Adress
    """
    win = omui.MQtUtil_mainWindow()
    ptr = wrapInstance(long(win), QtWidgets.QMainWindow)
    return ptr


def folderCheck(folder):
    """
    Checks the folder for existence. If not, creates it
    Args:
        folder: (String) Folder to check

    Returns: None

    """
    if not os.path.isdir(os.path.normpath(folder)):
        os.makedirs(os.path.normpath(folder))


def loadJson(file):
    """
    Loads the given json file
    Args:
        file: (String) Path to the json file

    Returns: JsonData

    """
    if os.path.isfile(file):
        with open(file, 'r') as f:
            # The JSON module will read our file, and convert it to a python dictionary
            data = json.load(f)
            return data
    else:
        return None


def dumpJson(data, file):
    """
    Saves the data to the json file
    Args:
        data: Data to save
        file: (String) Path to the json file

    Returns: None

    """
    with open(file, "w") as f:
        json.dump(data, f, indent=4)


def nameCheck(text):
    """
    Checks the given text for illegal characters
    Args:
        text: (String) Text to check

    Returns: (Integer)/(String) -1 for Error, <String> for corrected Text

    """
    text = text.replace("|", "__")
    if re.match("^[A-Za-z0-9_-]*$", text):
        if text == "":
            return -1
        text = text.replace(" ", "_")
        # text = text.replace("|", "__")
        return text
    else:
        return -1


def checkValidity(text, button, lineEdit):
    """
    Checks the given text for illegal characters. If illegal, disables the QPushButton and outlines the lineEdit QWidget Red
    Args:
        text: (String)
        button: (QPushButton)
        lineEdit: (QLineEdit)

    Returns: None

    """
    if not re.match("^[A-Za-z0-9_-]*$", text):
        lineEdit.setStyleSheet("background-color: red; color: black")
        button.setEnabled(False)
    else:
        lineEdit.setStyleSheet("background-color: rgb(40,40,40); color: white")
        button.setEnabled(True)


def pathOps(fullPath, mode):
    """
    performs basic path operations.
    Args:
        fullPath: (Unicode) Absolute Path
        mode: (String) Valid modes are 'path', 'basename', 'filename', 'extension', 'drive'

    Returns:
        Unicode

    """

    if mode == "drive":
        drive = os.path.splitdrive(fullPath)
        return drive

    path, basename = os.path.split(fullPath)
    if mode == "path":
        return path
    if mode == "basename":
        return basename
    filename, ext = os.path.splitext(basename)
    if mode == "filename":
        return filename
    if mode == "extension":
        return ext

def getPaths():
    """
    Collects the necessary path data from the scene
    Returns: (Dictionary) projectPath, dataPath, jsonPath, scenesPath, playBlastRoot

    """
    projectPath = os.path.normpath(pm.workspace(q=1, rd=1))
    dataPath = os.path.normpath(os.path.join(projectPath, "data"))
    folderCheck(dataPath)
    jsonPath = os.path.normpath(os.path.join(dataPath, "SMdata"))
    folderCheck(jsonPath)
    scenesPath = os.path.normpath(os.path.join(projectPath, "scenes"))
    folderCheck(scenesPath)
    playBlastRoot = os.path.normpath(os.path.join(projectPath, "Playblasts"))
    folderCheck(playBlastRoot)
    pathDictionary = {"projectPath": projectPath,
                      "dataPath": dataPath,
                      "jsonPath": jsonPath,
                      "scenesPath": scenesPath,
                      "playBlastRoot": playBlastRoot
                      }
    return pathDictionary


def compareVersions(version):
    print "version", version
    versionDict = {200800: "v2008",
                   200806: "v2008_EXT2",
                   200806: "v2008_SP1",
                   200900: "v2009",
                   200904: "v2009_EXT1",
                   200906: "v2009_SP1A",
                   201000: "v2010",
                   201100: "v2011",
                   201101: "v2011_HOTFIX1",
                   201102: "v2011_HOTFIX2",
                   201103: "v2011_HOTFIX3",
                   201104: "v2011_SP1",
                   201200: "v2012",
                   201201: "v2012_HOTFIX1",
                   201202: "v2012_HOTFIX2",
                   201203: "v2012_HOTFIX3",
                   201204: "v2012_HOTFIX4",
                   201209: "v2012_SAP1",
                   201217: "v2012_SAP1SP1",
                   201209: "v2012_SP1",
                   201217: "v2012_SP2",
                   201300: "v2013",
                   201400: "v2014",
                   201450: "v2014_EXT1",
                   201451: "v2014_EXT1SP1",
                   201459: "v2014_EXT1SP2",
                   201402: "v2014_SP1",
                   201404: "v2014_SP2",
                   201406: "v2014_SP3",
                   201500: "v2015",
                   201506: "v2015_EXT1",
                   201507: "v2015_EXT1SP5",
                   201501: "v2015_SP1",
                   201502: "v2015_SP2",
                   201505: "v2015_SP3",
                   201506: "v2015_SP4",
                   201507: "v2015_SP5",
                   201600: "v2016",
                   201650: "v20165",
                   201651: "v20165_SP1",
                   201653: "v20165_SP2",
                   201605: "v2016_EXT1",
                   201607: "v2016_EXT1SP4",
                   201650: "v2016_EXT2",
                   201651: "v2016_EXT2SP1",
                   201653: "v2016_EXT2SP2",
                   201605: "v2016_SP3",
                   201607: "v2016_SP4",
                   201700: "v2017",
                   201701: "v2017U1",
                   201720: "v2017U2",
                   201740: "v2017U3",
                   20180000: "v2018"}

    currentVersion = pm.versions.current()
    try:
        niceVName=versionDict[version]
    except KeyError:
        niceVName = version
    message = ""
    if version == currentVersion:
        return 0, message
    elif pm.versions.current() > version:
        message = "Base Scene is created with a LOWER Maya version ({0}). Are you sure you want to continue?".format(
            niceVName)
        return -1, message
    elif pm.versions.current() < version:
        message = "Base Scene is created with a HIGHER Maya version ({0}). Are you sure you want to continue?".format(
            niceVName)
        return -1, message

class TikManager(object):
    def __init__(self):
        super(TikManager, self).__init__()
        self.currentPlatform = platform.system()
        # self.currentProject = pm.workspace(q=1, rd=1)
        self.currentSubProjectIndex = 0
        self.userList = self.initUserList()[0]
        self.validCategories = ["Model", "Shading", "Rig", "Layout", "Animation", "Render", "Other"]
        self.padding = 3
        self.scenePaths = getPaths()
        self.subProjectList = self.scanSubProjects()


    def getSceneInfo(self):
        """
        Gets the necessary scene info by resolving the scene name and current project
        Returns: Dictionary{jsonFile, projectPath, subProject, category, shotName} or None

        """
        sceneName = pm.sceneName()
        if not sceneName:
            # pm.warning("This is not a base scene (Untitled)")
            return None

        # projectPath, jsonPath = getPathsFromScene("projectPath", "jsonPath")
        projectPath = self.scenePaths["projectPath"]
        jsonPath = self.scenePaths["jsonPath"]
        # first get the parent dir
        shotDirectory = os.path.abspath(os.path.join(pm.sceneName(), os.pardir))
        shotName = os.path.basename(shotDirectory)

        upperShotDir = os.path.abspath(os.path.join(shotDirectory, os.pardir))
        upperShot = os.path.basename(upperShotDir)

        if upperShot in self.subProjectList:
            subProjectDir = upperShotDir
            subProject = upperShot
            categoryDir = os.path.abspath(os.path.join(subProjectDir, os.pardir))
            category = os.path.basename(categoryDir)

            jsonCategoryPath = os.path.normpath(os.path.join(jsonPath, category))
            folderCheck(jsonCategoryPath)
            jsonPath = os.path.normpath(os.path.join(jsonCategoryPath, subProject))
            folderCheck(jsonPath)

        else:
            subProject = self.subProjectList[0]
            categoryDir = upperShotDir
            category = upperShot
            jsonPath = os.path.normpath(os.path.join(jsonPath, category))
            folderCheck(jsonPath)

        jsonFile = os.path.join(jsonPath, "{}.json".format(shotName))
        if os.path.isfile(jsonFile):
            version = (pathOps(sceneName, "filename")[-4:])
            return {"jsonFile":jsonFile,
                    "projectPath":projectPath,
                    "subProject":subProject,
                    "category":category,
                    "shotName":shotName,
                    "version":version
                    }
        else:
            return None

    def initUserList(self):
        userDBLocation = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sceneManagerUsers.json")
        if not os.path.isfile(userDBLocation):
            userDB = {"Generic": "gn"}
            dumpJson(userDB, userDBLocation)
            return userDB, userDBLocation
        else:
            userDB = loadJson(userDBLocation)
            return userDB, userDBLocation

    def addUser(self, fullName, initials):
        currentDB, dbFile = self.initUserList()
        initialsList = currentDB.values()
        if initials in initialsList:
            msg="Initials are in use"
            print msg
            return -1, msg
        currentDB[fullName] = initials
        dumpJson(currentDB, dbFile)
        self.userList = currentDB
        return None, None

    def removeUser(self, fullName):
        currentDB, dbFile = self.initUserList()
        del currentDB[fullName]
        dumpJson(currentDB, dbFile)
        self.userList = currentDB

    def listUsers(self):
        print self.userList

    def createNewProject(self, projectPath):
        # check if there is a duplicate
        if not os.path.isdir(os.path.normpath(projectPath)):
            os.makedirs(os.path.normpath(projectPath))
        else:
            print "Project already exists"
            return

        # create Directory structure:
        os.mkdir(os.path.join(projectPath, "_COMP"))
        os.makedirs(os.path.join(projectPath, "_MAX", "Animation"))
        os.makedirs(os.path.join(projectPath, "_MAX", "Model"))
        os.makedirs(os.path.join(projectPath, "_MAX", "Render"))
        os.mkdir(os.path.join(projectPath, "_SCULPT"))
        os.mkdir(os.path.join(projectPath, "_REALFLOW"))
        os.mkdir(os.path.join(projectPath, "_HOUDINI"))
        os.mkdir(os.path.join(projectPath, "_REF"))
        os.mkdir(os.path.join(projectPath, "_TRACK"))
        os.makedirs(os.path.join(projectPath, "_TRANSFER", "FBX"))
        os.makedirs(os.path.join(projectPath, "_TRANSFER", "ALEMBIC"))
        os.makedirs(os.path.join(projectPath, "_TRANSFER", "OBJ"))
        os.makedirs(os.path.join(projectPath, "_TRANSFER", "MA"))
        os.mkdir(os.path.join(projectPath, "assets"))
        os.mkdir(os.path.join(projectPath, "cache"))
        os.mkdir(os.path.join(projectPath, "clips"))
        os.mkdir(os.path.join(projectPath, "data"))
        os.makedirs(os.path.join(projectPath, "images", "_CompRenders"))
        os.mkdir(os.path.join(projectPath, "movies"))
        os.mkdir(os.path.join(projectPath, "particles"))
        os.mkdir(os.path.join(projectPath, "Playblasts"))
        os.makedirs(os.path.join(projectPath, "renderData", "depth"))
        os.makedirs(os.path.join(projectPath, "renderData", "fur"))
        os.makedirs(os.path.join(projectPath, "renderData", "iprImages"))
        os.makedirs(os.path.join(projectPath, "renderData", "mentalray"))
        os.makedirs(os.path.join(projectPath, "renderData", "shaders"))
        os.mkdir(os.path.join(projectPath, "scenes"))
        os.mkdir(os.path.join(projectPath, "scripts"))
        os.mkdir(os.path.join(projectPath, "sound"))
        os.makedirs(os.path.join(projectPath, "sourceimages", "_FOOTAGE"))
        os.makedirs(os.path.join(projectPath, "sourceimages", "_HDR"))

        filePath = os.path.join(projectPath, "workspace.mel")
        file = open(filePath, "w")

        file.write('workspace -fr "scene" "scenes";\n')
        file.write('workspace -fr "3dPaintTextures" "sourceimages/3dPaintTextures";\n')
        file.write('workspace -fr "eps" "data";\n')
        file.write('workspace -fr "mentalRay" "renderData/mentalray";\n')
        file.write('workspace -fr "OBJexport" "_TRANSFER/OBJ";\n')
        file.write('workspace -fr "mel" "scripts";\n')
        file.write('workspace -fr "particles" "particles";\n')
        file.write('workspace -fr "STEP_DC" "data";\n')
        file.write('workspace -fr "CATIAV5_DC" "data";\n')
        file.write('workspace -fr "sound" "sound";\n')
        file.write('workspace -fr "furFiles" "renderData/fur/furFiles";\n')
        file.write('workspace -fr "depth" "renderData/depth";\n')
        file.write('workspace -fr "CATIAV4_DC" "data";\n')
        file.write('workspace -fr "autoSave" "autosave";\n')
        file.write('workspace -fr "diskCache" "cache";\n')
        file.write('workspace -fr "fileCache" "";\n')
        file.write('workspace -fr "IPT_DC" "data";\n')
        file.write('workspace -fr "SW_DC" "data";\n')
        file.write('workspace -fr "DAE_FBX export" "data";\n')
        file.write('workspace -fr "Autodesk Packet File" "";\n')
        file.write('workspace -fr "DAE_FBX" "data";\n')
        file.write('workspace -fr "DXF_DCE" "";\n')
        file.write('workspace -fr "mayaAscii" "scenes";\n')
        file.write('workspace -fr "iprImages" "renderData/iprImages";\n')
        file.write('workspace -fr "move" "data";\n')
        file.write('workspace -fr "mayaBinary" "scenes";\n')
        file.write('workspace -fr "fluidCache" "cache/fluid";\n')
        file.write('workspace -fr "clips" "clips";\n')
        file.write('workspace -fr "animExport" "data";\n')
        file.write('workspace -fr "templates" "assets";\n')
        file.write('workspace -fr "DWG_DC" "data";\n')
        file.write('workspace -fr "offlineEdit" "scenes/edits";\n')
        file.write('workspace -fr "translatorData" "data";\n')
        file.write('workspace -fr "renderData" "renderData";\n')
        file.write('workspace -fr "DXF_DC" "data";\n')
        file.write('workspace -fr "SPF_DCE" "";\n')
        file.write('workspace -fr "ZPR_DCE" "";\n')
        file.write('workspace -fr "furShadowMap" "renderData/fur/furShadowMap";\n')
        file.write('workspace -fr "audio" "sound";\n')
        file.write('workspace -fr "scripts" "scripts";\n')
        file.write('workspace -fr "IV_DC" "data";\n')
        file.write('workspace -fr "studioImport" "data";\n')
        file.write('workspace -fr "STL_DCE" "";\n')
        file.write('workspace -fr "furAttrMap" "renderData/fur/furAttrMap";\n')
        file.write('workspace -fr "FBX export" "data";\n')
        file.write('workspace -fr "JT_DC" "data";\n')
        file.write('workspace -fr "sourceImages" "sourceimages";\n')
        file.write('workspace -fr "DWG_DCE" "";\n')
        file.write('workspace -fr "animImport" "data";\n')
        file.write('workspace -fr "FBX" "data";\n')
        file.write('workspace -fr "movie" "movies";\n')
        file.write('workspace -fr "Alembic" "";\n')
        file.write('workspace -fr "furImages" "renderData/fur/furImages";\n')
        file.write('workspace -fr "IGES_DC" "data";\n')
        file.write('workspace -fr "furEqualMap" "renderData/fur/furEqualMap";\n')
        file.write('workspace -fr "illustrator" "data";\n')
        file.write('workspace -fr "UG_DC" "";\n')
        file.write('workspace -fr "images" "images";\n')
        file.write('workspace -fr "SPF_DC" "data";\n')
        file.write('workspace -fr "PTC_DC" "data";\n')
        file.write('workspace -fr "OBJ" "_TRANSFER/OBJ";\n')
        file.write('workspace -fr "CSB_DC" "data";\n')
        file.write('workspace -fr "STL_DC" "data";\n')
        file.write('workspace -fr "IGES_DCE" "";\n')
        file.write('workspace -fr "shaders" "renderData/shaders";\n')
        file.write('workspace -fr "UG_DCE" "";\n')

        # file.write("{0}\n".format(L1))
        # file.write("{0}\n".format(L2))
        # file.write("{0}\n".format(L3))
        # file.write("{0}\n".format(L4))
        # file.write("{0}\n".format(L5))
        file.close()
        pass

    def setProject(self):
        mel.eval("SetProject;")
        self.scenePaths["projectPath"] = pm.workspace(q=1, rd=1)

    def projectReport(self):

        # // TODO Create a through REPORT
        # projectPath, dataPath, jsonPath, scenesPath, playBlastRoot = getPathsFromScene("projectPath", "dataPath",
        #                                                                                "jsonPath", "scenesPath",
        #                                                                                "playBlastRoot")
        projectPath = self.scenePaths["projectPath"]
        dataPath = self.scenePaths["dataPath"]
        jsonPath = self.scenePaths["jsonPath"]
        scenesPath = self.scenePaths["scenePath"]
        playBlastRoot = self.scenePaths["playBlastRoot"]

        # get All json files:
        oldestFile = getOldestFile(scenesPath, extension=(".mb", ".ma"))
        # oldestTime = os.stat(oldestFile).st_mtime
        oldestTimeMod = datetime.datetime.fromtimestamp(os.path.getmtime(oldestFile))

        newestFile = getNewestFile(scenesPath, extension=(".mb", ".ma"))
        # newestTime = os.stat(newestFile ).st_mtime
        newestTimeMod = datetime.datetime.fromtimestamp(os.path.getmtime(newestFile))

        L1 = "Oldest Scene file: {0} - {1}".format(pathOps(oldestFile, "basename"), oldestTimeMod)
        L2 = "Newest Scene file: {0} - {1}".format(pathOps(newestFile, "basename"), newestTimeMod)
        L3 = "Elapsed Time: {0}".format(str(newestTimeMod - oldestTimeMod))
        L4 = "Scene Counts:"
        # L5 = ""
        report = {}
        for subP in range(len(self.subProjectList)):
            subReport = {}
            for category in self.validCategories:
                categoryItems = (self.scanScenes(category, subProjectAs=subP)[0])
                categoryItems = [x for x in categoryItems if x != []]

                L4 = "{0}\n{1}: {2}".format(L4, category, len(categoryItems))
                subReport[category] = categoryItems
            report[self.subProjectList[subP]] = subReport

        report = pprint.pformat(report)

        now = datetime.datetime.now()
        filename = "summary_{0}.txt".format(now.strftime("%Y.%m.%d.%H.%M"))
        filePath = os.path.join(projectPath, filename)
        file = open(filePath, "w")

        file.write("{0}\n".format(L1))
        file.write("{0}\n".format(L2))
        file.write("{0}\n".format(L3))
        file.write("{0}\n".format(L4))
        # file.write("{0}\n".format(L5))
        file.write((report))

        file.close()

        return report

    def remoteLogger(self):

        try:
            session = ftplib.FTP('ardakutlu.com', 'customLogs@ardakutlu.com', 'Dq%}3LwVMZms')
            now = datetime.datetime.now()
            # filename = ("{0}_{1}".format(now.strftime("%Y.%m.%d.%H.%M"), pathOps(getPathsFromScene("projectPath"), "basename")))
            filename = ("{0}_{1}".format(now.strftime("%Y.%m.%d.%H.%M"), pathOps(self.scenePaths["projectPath"], "basename")))

            logInfo = "{0}\n{1}\n{2}".format(
                # getPathsFromScene("projectPath"),
                self.scenePaths["projectPath"],
                socket.gethostname(),
                (socket.gethostbyname(socket.gethostname())),
            )

            bio = io.BytesIO(logInfo)

            session.storbinary('STOR ' + filename, bio)  # send the file
            # for l in logFiles:
            #     filename = pathOps(l, "basename")
            #     # print l
            #     file = open(l, 'rb')  # file to send
            #     session.storbinary('STOR '+filename, file)  # send the file
            #     file.close()  # close file and FTP
            session.quit()
        except:
            pass

    def regularSaveUpdate(self):
        sceneName = os.path.normpath(pm.sceneName())

        # if the scene is untitled, dont bother to continue
        if not sceneName:
            return

        # projectPath, jsonPath = getPathsFromScene("projectPath", "jsonPath")
        projectPath = self.scenePaths["projectPath"]
        jsonPath = self.scenePaths["jsonPath"]

        shotDirectory = os.path.abspath(os.path.join(pm.sceneName(), os.pardir))
        shotName = os.path.basename(shotDirectory)

        upperShotDir = os.path.abspath(os.path.join(shotDirectory, os.pardir))
        upperShot = os.path.basename(upperShotDir)

        if upperShot in self.subProjectList:
            subProjectDir = upperShotDir
            subProject = upperShot
            categoryDir = os.path.abspath(os.path.join(subProjectDir, os.pardir))
            category = os.path.basename(categoryDir)

            jsonCategoryPath = os.path.normpath(os.path.join(jsonPath, category))
            folderCheck(jsonCategoryPath)
            jsonPath = os.path.normpath(os.path.join(jsonCategoryPath, subProject))
            folderCheck(jsonPath)

        else:
            categoryDir = upperShotDir
            category = upperShot
            jsonPath = os.path.normpath(os.path.join(jsonPath, category))
            folderCheck(jsonPath)

        jsonFile = os.path.join(jsonPath, "{}.json".format(shotName))

        # check if the saved file be
        if os.path.isfile(jsonFile):
            jsonInfo = loadJson(jsonFile)
            # check is the baseScene has a reference file
            if jsonInfo["ReferenceFile"]:
                absRefFile = os.path.join(projectPath, jsonInfo["ReferenceFile"])
                absBaseSceneVersion = os.path.join(projectPath,
                                                   jsonInfo["Versions"][int(jsonInfo["ReferencedVersion"]) - 1][0])
                # if the refererenced scene file is the saved file (saved or saved as)
                if sceneName == absBaseSceneVersion:
                    # copy over the forReference file
                    try:
                        copyfile(sceneName, absRefFile)
                        print "Scene Manager Update:\nReference File Updated"
                    except:
                        pass

    def saveBaseScene(self, category, userName, baseName, subProject=0, makeReference=True, versionNotes="", *args,
                      **kwargs):
        """
        Saves the scene with formatted name and creates a json file for the scene
        Args:
            category: (String) Category if the scene. Valid categories are 'Model', 'Animation', 'Rig', 'Shading', 'Other'
            userName: (String) Predefined user who initiates the process
            baseName: (String) Base name of the scene. Eg. 'Shot01', 'CharacterA', 'BookRig' etc...
            subProject: (Integer) The scene will be saved under the sub-project according to the given integer value. The 'self.subProjectList' will be
                searched with that integer.
            makeReference: (Boolean) If set True, a copy of the scene will be saved as forReference
            versionNotes: (String) This string will be stored in the json file as version notes.
            *args: 
            **kwargs: 

        Returns: None

        """
        fullName = self.userList.keys()[self.userList.values().index(userName)]
        now = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M")
        completeNote = "[%s] on %s\n%s\n" % (fullName, now, versionNotes)

        scenesToCheck = self.scanScenes(category, subProjectAs=subProject)[0]
        for z in scenesToCheck:
            if baseName.lower() == loadJson(z)["Name"].lower():
                pm.warning("Choose an unique name")
                return -1

        # projectPath, jsonPath, scenesPath = getPathsFromScene("projectPath", "jsonPath", "scenesPath")
        projectPath = self.scenePaths["projectPath"]
        jsonPath = self.scenePaths["jsonPath"]
        scenesPath = self.scenePaths["scenesPath"]

        categoryPath = os.path.normpath(os.path.join(scenesPath, category))
        folderCheck(categoryPath)

        ## eger subproject olarak kaydedilecekse
        if not subProject == 0:
            subProjectPath = os.path.normpath(os.path.join(categoryPath, self.subProjectList[subProject]))
            folderCheck(subProjectPath)
            shotPath = os.path.normpath(os.path.join(subProjectPath, baseName))
            folderCheck(shotPath)

            jsonCategoryPath = os.path.normpath(os.path.join(jsonPath, category))
            folderCheck(jsonCategoryPath)
            jsonCategorySubPath = os.path.normpath(os.path.join(jsonCategoryPath, self.subProjectList[subProject]))
            folderCheck(jsonCategorySubPath)
            jsonFile = os.path.join(jsonCategorySubPath, "{}.json".format(baseName))
        else:
            shotPath = os.path.normpath(os.path.join(categoryPath, baseName))
            folderCheck(shotPath)

            jsonCategoryPath = os.path.normpath(os.path.join(jsonPath, category))
            folderCheck(jsonCategoryPath)
            jsonFile = os.path.join(jsonCategoryPath, "{}.json".format(baseName))

        version = 1
        sceneName = "{0}_{1}_{2}_v{3}".format(baseName, category, userName, str(version).zfill(self.padding))
        sceneFile = os.path.join(shotPath, "{0}.mb".format(sceneName))
        ## relativity update
        relSceneFile = os.path.relpath(sceneFile, start=projectPath)
        # killTurtle()
        pm.saveAs(sceneFile)
        thumbPath = self.createThumbnail(jsonPath=jsonFile, version=version)

        jsonInfo = {}

        if makeReference:
            referenceName = "{0}_{1}_forReference".format(baseName, category)
            referenceFile = os.path.join(shotPath, "{0}.mb".format(referenceName))
            ## relativity update
            relReferenceFile = os.path.relpath(referenceFile, start=projectPath)
            copyfile(sceneFile, referenceFile)
            jsonInfo["ReferenceFile"] = relReferenceFile
            jsonInfo["ReferencedVersion"] = version
        else:
            jsonInfo["ReferenceFile"] = None
            jsonInfo["ReferencedVersion"] = None

        jsonInfo["ID"] = "SceneManagerV01_sceneFile"
        jsonInfo["MayaVersion"] = pm.versions.current()
        jsonInfo["Name"] = baseName
        jsonInfo["Path"] = os.path.relpath(shotPath, start=projectPath)
        jsonInfo["Category"] = category
        jsonInfo["Creator"] = userName
        jsonInfo["CreatorHost"] = (socket.gethostname())
        jsonInfo["Versions"] = [ # PATH => Notes => User Initials => Machine ID => Playblast => Thumbnail
            [relSceneFile, completeNote, userName, socket.gethostname(), {}, thumbPath]]
        dumpJson(jsonInfo, jsonFile)
        return relSceneFile

    def getVersionNotes(self, jsonFile, version=None):
        """
        Returns: [versionNotes, playBlastDictionary]
        """
        jsonInfo = loadJson(jsonFile)
        # print "versions\n"
        # pprint.pprint(jsonInfo["Versions"][version][1])
        return jsonInfo["Versions"][version][1], jsonInfo["Versions"][version][4]

    def addVersionNotes(self, additionalNote, jsonFile, version, user):
        jsonInfo = loadJson(jsonFile)
        currentNotes = jsonInfo["Versions"][version][1]
        ## add username and date to the beginning of the note:
        now = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M")
        completeNote = "%s\n[%s] on %s\n%s\n" % (currentNotes, user, now, additionalNote)
        jsonInfo["Versions"][version][1] = completeNote
        ##
        dumpJson(jsonInfo, jsonFile)

    def saveVersion(self, userName, makeReference=True, versionNotes="", *args, **kwargs):
        """
        Saves a version for the predefined scene. The scene json file must be present at the /data/[Category] folder.
        Args:
            userName: (String) Predefined user who initiates the process
            makeReference: (Boolean) If set True, make a copy of the forReference file. There can be only one 'forReference' file for each scene
            versionNotes: (String) This string will be hold in the json file as well. Notes about the changes in the version.
            *args: 
            **kwargs: 

        Returns: None

        """

        # get the full username
        fullName = self.userList.keys()[self.userList.values().index(userName)]
        now = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M")
        completeNote = "[%s] on %s\n%s\n" % (fullName, now, versionNotes)
        sceneName = pm.sceneName()
        if not sceneName:
            pm.warning("This is not a base scene (Untitled)")
            return -1

        sceneInfo = self.getSceneInfo()



        if sceneInfo: ## getCurrentJson returns None if the resolved json path is missing
            jsonFile = sceneInfo["jsonFile"]
            jsonInfo = loadJson(jsonFile)

            currentVersion = len(jsonInfo["Versions"]) + 1
            sceneName = "{0}_{1}_{2}_v{3}".format(jsonInfo["Name"], jsonInfo["Category"], userName,
                                                  str(currentVersion).zfill(self.padding))
            relSceneFile = os.path.join(jsonInfo["Path"], "{0}.mb".format(sceneName))

            sceneFile = os.path.join(sceneInfo["projectPath"], relSceneFile)

            # killTurtle()
            pm.saveAs(sceneFile)
            thumbPath = self.createThumbnail(jsonPath=jsonFile, version=currentVersion)

            jsonInfo["Versions"].append(
                # PATH => Notes => User Initials => Machine ID => Playblast => Thumbnail
                [relSceneFile, completeNote, userName, (socket.gethostname()), {}, thumbPath])

            if makeReference:
                referenceName = "{0}_{1}_forReference".format(jsonInfo["Name"], jsonInfo["Category"])
                relReferenceFile = os.path.join(jsonInfo["Path"], "{0}.mb".format(referenceName))
                # referenceFile = "%s%s" %(projectPath, relReferenceFile)
                referenceFile = os.path.join(sceneInfo["projectPath"], relReferenceFile)

                copyfile(sceneFile, referenceFile)
                jsonInfo["ReferenceFile"] = relReferenceFile
                jsonInfo["ReferencedVersion"] = currentVersion
            dumpJson(jsonInfo, jsonFile)
        else:
            pm.warning("This is not a base scene (Json file cannot be found)")
            return -1
        return relSceneFile

    def getPBsettings(self):

        # projectPath, playBlastRoot = getPathsFromScene("projectPath", "playBlastRoot")
        projectPath = self.scenePaths["projectPath"]
        playBlastRoot = self.scenePaths["playBlastRoot"]

        # pbSettingsFile = "{0}\\PBsettings.json".format(os.path.join(projectPath, playBlastRoot))
        pbSettingsFile = os.path.join(os.path.join(projectPath, playBlastRoot), "PBsettings.json")

        if not os.path.isfile(pbSettingsFile):
            defaultSettings = {"Resolution": (1280, 720),  ## done
                               "Format": 'avi',  ## done
                               "Codec": 'IYUV',  ## done
                               "Percent": 100,  ## done
                               "Quality": 100,  ## done
                               "ShowFrameNumber": True,
                               "ShowSceneName": False,
                               "ShowCategory": False,
                               "ShowFrameRange": True,
                               "ShowFPS": True,
                               "PolygonOnly": True,  ## done
                               "ShowGrid": False,  ## done
                               "ClearSelection": True,  ## done
                               "DisplayTextures": True,  ## done
                               "WireOnShaded": False,
                               "UseDefaultMaterial": False,
                               }
            dumpJson(defaultSettings, pbSettingsFile)
            return defaultSettings
        else:
            pbSettings = loadJson(pbSettingsFile)
            return pbSettings

    def setPBsettings(self, pbSettingsDict):

        # projectPath, playBlastRoot = getPathsFromScene("projectPath", "playBlastRoot")
        projectPath = self.scenePaths["projectPath"]
        playBlastRoot = self.scenePaths["playBlastRoot"]

        pbSettingsFile = os.path.join(os.path.join(projectPath, playBlastRoot), "PBsettings.json")
        dumpJson(pbSettingsDict, pbSettingsFile)
        return

    def createPlayblast(self, *args, **kwargs):
        pbSettings = self.getPBsettings()

        validFormats = pm.playblast(format=True, q=True)
        validCodecs = pm.playblast(c=True, q=True)
        if not pbSettings["Format"] in validFormats:
            msg = ("Format specified in project settings is not supported. Install {0}".format(pbSettings["Format"]))
            pm.warning(msg)
            return -1, msg

        if not pbSettings["Codec"] in validCodecs:
            msg = ("Codec specified in project settings is not supported. Install {0}".format(pbSettings["Codec"]))
            pm.warning(msg)
            return -1, msg

        print pbSettings
        extension = "mov" if pbSettings["Format"] == "qt" else "avi"

        # Quicktime format is missing the final frame all the time. Add an extra frame to compansate
        if pbSettings["Format"] == 'qt':
            maxTime = pm.playbackOptions(q=True, maxTime=True)
            endTime = pm.playbackOptions(q=True, animationEndTime=True)
            pm.playbackOptions(maxTime=maxTime + 1)
            pm.playbackOptions(animationEndTime=endTime + 1)

        sceneName = pm.sceneName()
        if not sceneName:
            msg = "This is not a base scene. Scene must be saved as a base scene before playblasting."
            pm.warning(msg)
            return -1, msg

        # projectPath, jsonPath, playBlastRoot = getPathsFromScene("projectPath", "jsonPath", "playBlastRoot")
        projectPath = self.scenePaths["projectPath"]
        jsonPath = self.scenePaths["jsonPath"]
        playBlastRoot = self.scenePaths["playBlastRoot"]

        # first get the parent dir
        shotDirectory = os.path.abspath(os.path.join(pm.sceneName(), os.pardir))
        shotName = os.path.basename(shotDirectory)

        upperShotDir = os.path.abspath(os.path.join(shotDirectory, os.pardir))
        upperShot = os.path.basename(upperShotDir)

        if upperShot in self.subProjectList:
            subProjectDir = upperShotDir
            subProject = upperShot
            categoryDir = os.path.abspath(os.path.join(subProjectDir, os.pardir))
            category = os.path.basename(categoryDir)

            jsonCategoryPath = os.path.normpath(os.path.join(jsonPath, category))
            folderCheck(jsonCategoryPath)
            jsonPath = os.path.normpath(os.path.join(jsonCategoryPath, subProject))
            folderCheck(jsonPath)

            pbCategoryPath = os.path.normpath(os.path.join(playBlastRoot, category))
            folderCheck(pbCategoryPath)
            pbSubPath = os.path.normpath(os.path.join(pbCategoryPath, subProject))
            folderCheck(pbSubPath)
            pbPath = os.path.normpath(os.path.join(pbSubPath, shotName))
            folderCheck(pbPath)

        else:
            # categoryDir = upperShotDir
            category = upperShot
            jsonPath = os.path.normpath(os.path.join(jsonPath, category))
            folderCheck(jsonPath)
            pbCategoryPath = os.path.normpath(os.path.join(playBlastRoot, category))
            folderCheck(pbCategoryPath)
            pbPath = os.path.normpath(os.path.join(pbCategoryPath, shotName))
            folderCheck(pbPath)

        jsonFile = os.path.join(jsonPath, "{}.json".format(shotName))

        if os.path.isfile(jsonFile):

            selection = pm.ls(sl=True)
            pm.select(d=pbSettings["ClearSelection"])
            jsonInfo = loadJson(jsonFile)

            currentCam = pm.modelPanel(pm.getPanel(wf=True), q=True, cam=True)

            validName = "_"
            if not nameCheck(currentCam) == -1:
                validName = nameCheck(currentCam)
            else:
                msg = "A scene view must be highlighted"
                pm.warning(msg)
                return -1, msg

            versionName = pm.sceneName()
            relVersionName = os.path.relpath(versionName, start=projectPath)
            playBlastFile = os.path.join(pbPath,
                                         "{0}_{1}_PB.{2}".format(pathOps(versionName, mode="filename"), validName, extension))
            relPlayBlastFile = os.path.relpath(playBlastFile, start=projectPath)

            if os.path.isfile(playBlastFile):
                try:
                    os.remove(playBlastFile)
                except WindowsError:
                    msg = "The file is open somewhere else"
                    pm.warning(msg)
                    return -1, msg

            ## CREATE A CUSTOM PANEL WITH DESIRED SETTINGS

            tempWindow = pm.window(title="SM_Playblast",
                                   widthHeight=(pbSettings["Resolution"][0] * 1.1, pbSettings["Resolution"][1] * 1.1),
                                   tlc=(0, 0))
            # panel = pm.getPanel(wf=True)

            pm.paneLayout()

            pbPanel = pm.modelPanel(camera=currentCam)
            pm.showWindow(tempWindow)
            pm.setFocus(pbPanel)

            pm.modelEditor(pbPanel, e=1,
                           allObjects=not pbSettings["PolygonOnly"],
                           da="smoothShaded",
                           displayTextures=pbSettings["DisplayTextures"],
                           wireframeOnShaded=pbSettings["WireOnShaded"],
                           grid=pbSettings["ShowGrid"],
                           useDefaultMaterial=pbSettings["UseDefaultMaterial"],
                           polymeshes=True,
                           imagePlane=True,
                           hud=True
                           )

            pm.camera(currentCam, e=True, overscan=True, displayFilmGate=False, displayResolution=False)

            ## get previous HUD States and turn them all off
            hudPreStates = {}
            HUDS = pm.headsUpDisplay(lh=True)
            for hud in HUDS:
                hudPreStates[hud] = pm.headsUpDisplay(hud, q=True, vis=True)
                pm.headsUpDisplay(hud, e=True, vis=False)

            ## clear the custom HUDS
            customHuds = ['SMFrame', 'SMScene', 'SMCategory', 'SMFPS', 'SMCameraName', 'SMFrange']
            for hud in customHuds:
                if pm.headsUpDisplay(hud, ex=True):
                    pm.headsUpDisplay(hud, rem=True)

            if pbSettings["ShowFrameNumber"]:
                freeBl = pm.headsUpDisplay(nfb=5)  ## this is the next free block on section 5
                pm.headsUpDisplay('SMFrame', s=5, b=freeBl, label="Frame", preset="currentFrame", dfs="large",
                                  lfs="large")
            if pbSettings["ShowSceneName"]:
                freeBl = pm.headsUpDisplay(nfb=5)  ## this is the next free block on section 5
                pm.headsUpDisplay('SMScene', s=5, b=freeBl, label="Scene: %s" % (pathOps(versionName, mode="filename")),
                                  lfs="large")
            if pbSettings["ShowCategory"]:
                freeBl = pm.headsUpDisplay(nfb=5)  ## this is the next free block on section 5
                pm.headsUpDisplay('SMCategory', s=5, b=freeBl, label="Category: %s" % (jsonInfo["Category"]),
                                  lfs="large")
            if pbSettings["ShowFPS"]:
                freeBl = pm.headsUpDisplay(nfb=5)  ## this is the next free block on section 5
                pm.headsUpDisplay('SMFPS', s=5, b=freeBl, label="Time Unit: %s" % (pm.currentUnit(q=True, time=True)),
                                  lfs="large")

            # v1.1 SPECIFIC
            try:
                if pbSettings["ShowFrameRange"]:
                    freeBl = pm.headsUpDisplay(nfb=5)  ## this is the next free block on section 5
                    pm.headsUpDisplay('SMFrange', s=5, b=freeBl,
                                      label="Frame Range: {} - {}".format(int(pm.playbackOptions(q=True, minTime=True)),
                                                                          int(pm.playbackOptions(q=True,
                                                                                                 maxTime=True))),
                                      lfs="large")
            except KeyError:
                pass

            freeBl = pm.headsUpDisplay(nfb=2)
            pm.headsUpDisplay('SMCameraName', s=2, b=freeBl, ba='center', dw=50, pre='cameraNames')

            ## Get the active sound

            aPlayBackSliderPython = maya.mel.eval('$tmpVar=$gPlayBackSlider')
            activeSound = pm.timeControl(aPlayBackSliderPython, q=True, sound=True)

            ## Check here: http://download.autodesk.com/us/maya/2011help/pymel/generated/functions/pymel.core.windows/pymel.core.windows.headsUpDisplay.html
            print "playBlastFile", playBlastFile
            normPB = os.path.normpath(playBlastFile)
            print "normPath", normPB
            pm.playblast(format=pbSettings["Format"],
                         filename=playBlastFile,
                         widthHeight=pbSettings["Resolution"],
                         percent=pbSettings["Percent"],
                         quality=pbSettings["Quality"],
                         compression=pbSettings["Codec"],
                         sound=activeSound,
                         uts=True)
            ## remove window when pb is donw
            pm.deleteUI(tempWindow)

            # Get back to the original frame range if the codec is Quick Time
            if pbSettings["Format"] == 'qt':
                pm.playbackOptions(maxTime=maxTime)
                pm.playbackOptions(animationEndTime=endTime)

            ## remove the custom HUdS
            if pbSettings["ShowFrameNumber"]:
                pm.headsUpDisplay('SMFrame', rem=True)
            if pbSettings["ShowSceneName"]:
                pm.headsUpDisplay('SMScene', rem=True)
            if pbSettings["ShowCategory"]:
                pm.headsUpDisplay('SMCategory', rem=True)
            if pbSettings["ShowFPS"]:
                pm.headsUpDisplay('SMFPS', rem=True)
            try:
                if pbSettings["ShowFrameRange"]:
                    pm.headsUpDisplay('SMFrange', rem=True)
            except KeyError:
                pass

            pm.headsUpDisplay('SMCameraName', rem=True)

            ## get back the previous state of HUDS
            for hud in hudPreStates.keys():
                pm.headsUpDisplay(hud, e=True, vis=hudPreStates[hud])
            pm.select(selection)
            ## find this version in the json data
            for i in jsonInfo["Versions"]:
                if relVersionName == i[0]:
                    i[4][currentCam] = relPlayBlastFile

            dumpJson(jsonInfo, jsonFile)
        else:
            msg = "This is not a base scene (Json file cannot be found)"
            pm.warning(msg)
            return -1, msg

            #######

    def playPlayblast(self, relativePath):
        # projectPath = getPathsFromScene("projectPath")
        projectPath = self.scenePaths["projectPath"]

        PBfile = os.path.join(projectPath, relativePath)
        if self.currentPlatform == "Windows":
            try:
                os.startfile(PBfile)
            except WindowsError:
                return -1, ["Cannot Find Playblast", "Playblast File is missing", "Do you want to remove it from the Database?"]
        return

    def removePlayblast(self, relativePath, jsonFile, version):
        jsonInfo = loadJson(jsonFile)
        pbDict = jsonInfo["Versions"][version][4]
        for key, value in pbDict.iteritems():  # for name, age in list.items():  (for Python 3.x)
            if value == relativePath:
                pbDict.pop(key, None)
                jsonInfo["Versions"][version][4] = pbDict
                dumpJson(jsonInfo, jsonFile)
                return


    def createSubProject(self, nameOfSubProject):
        if (nameOfSubProject.lower()) == "none":
            pm.warning("Naming mismatch")
            return None
        # projectPath, jsonPath = getPathsFromScene("projectPath", "jsonPath")
        projectPath = self.scenePaths["projectPath"]
        jsonPath = self.scenePaths["jsonPath"]
        subPjson = os.path.normpath(os.path.join(jsonPath, "subPdata.json"))
        subInfo = []
        if os.path.isfile(subPjson):
            subInfo = loadJson(subPjson)

        subInfo.append(nameOfSubProject)
        self.currentSubProjectIndex = len(subInfo) - 1  ## make the current sub project index the new created one.
        dumpJson(subInfo, subPjson)
        return subInfo

    def scanSubProjects(self):
        # projectPath, jsonPath = getPathsFromScene("projectPath", "jsonPath")
        projectPath = self.scenePaths["projectPath"]
        jsonPath = self.scenePaths["jsonPath"]
        subPjson = os.path.normpath(os.path.join(jsonPath, "subPdata.json"))
        if not os.path.isfile(subPjson):
            subInfo = ["None"]
            dumpJson(subInfo, subPjson)

        else:
            subInfo = loadJson(subPjson)
        return subInfo

        # def renameScene(self, jsonFile, newName, version=None):
        #
        #     projectPath = getPathsFromScene("projectPath")
        #     jsonInfo = loadJson(jsonFile)
        #     category = jsonInfo["Category"]
        #
        #     # PSUEDO CODE:
        #
        #     # subproject = get the scenes sub-project
        #
        #     versionCount = 0
        #     for version in jsonInfo["Versions"]:
        #         versionCount += 1
        #         rel_scene_file = version[0]
        #         scene_file = os.path.join(projectPath, rel_scene_file)
        #
        #         newSceneName = "{0}_{1}_{2}_v{3}".format(newName, category, version[2], str(versionCount).zfill(self.padding))
        #
        #
        #         # Change the name of the actual file
        #
        #         # Update the jsonInfo with the me
        #             # for pb in all playblasts in this version
        #                 # Change the name of the playblast
        #
        # def moveToSubProject(self, newSubproject):
        #     # // TODO write subproject moving method
        #     pass




        # relSceneFile = jsonInfo["Versions"][version][0] ## this is the relative scene path of the specified version
        # sceneFile = os.path.join(projectPath, relSceneFile)
        #
        # # check name for duplicate
        # scenesToCheck = self.scanScenes(jsonInfo["Category"], subProjectAs=subProject)[0]
        # for z in scenesToCheck:
        #     if newName == loadJson(z)["Name"]:
        #         pm.warning("Choose an unique name")
        #         return -1
        #
        # # check name for invalid characters
        # if nameCheck(newName) == -1:
        #     pm.warning("Give a unique and proper name with latin characters, without spaces")
        #     return -1

    # // TODO // Create a method to delete playblasts (or change the playblast load method with scanning directories)

    def scanScenes(self, category, subProjectAs=None):
        """
        Scans the folder for json files. Instead of scanning all of the json files at once, It will scan only the target category to speed up the process.
        Args:
            category: (String) This is the category which will be scanned
            subProjectAs: (String / None) If a sub project is given Scans the given sub project. If None, it scans the current sub-project
                declared the classes 'currentSubProjectIndex' variable. Default = None

        Returns: List of all json files in the category, sub-project json file

        """
        if not subProjectAs is None:
            subProjectIndex = subProjectAs
        else:
            subProjectIndex = self.currentSubProjectIndex
        # projectPath, jsonPath = getPathsFromScene("projectPath", "jsonPath")
        projectPath = self.scenePaths["projectPath"]
        jsonPath = self.scenePaths["jsonPath"]

        subPjson = os.path.normpath(os.path.join(jsonPath, "subPdata.json"))
        if not os.path.isfile(subPjson):
            dumpJson(["None"], subPjson)
        # eger subproject olarak aranilacaksa
        if not (subProjectIndex == 0):
            jsonCategoryPath = os.path.normpath(os.path.join(jsonPath, category))
            folderCheck(jsonCategoryPath)

            jsonCategorySubPath = os.path.normpath(
                os.path.join(jsonCategoryPath, (self.subProjectList)[subProjectIndex]))

            folderCheck(jsonCategorySubPath)
            searchFolder = jsonCategorySubPath
        else:
            jsonCategoryPath = os.path.normpath(os.path.join(jsonPath, category))
            folderCheck(jsonCategoryPath)
            searchFolder = jsonCategoryPath

        allJsonFiles = []
        # niceNames = []
        for file in os.listdir(searchFolder):
            if file.endswith('.json'):
                file = os.path.join(searchFolder, file)
                allJsonFiles.append(file)
        return allJsonFiles, subPjson

    def loadScene(self, jsonFile, version=None, force=False, importFile=False):
        """
        Opens the scene with the related json file and given version.
        Args:
            jsonFile: (String) This is the path of the json file which holds the scene properties.
            version: (integer) The version specified in this flag will be loaded. If not specified, last saved version will be used. Default=None
            force: (Boolean) If True, it forces the scene to load LOSING ALL THE UNSAVED CHANGES in the current scene. Default is 'False' 
            importFile: (Boolean) If True, it imports the file instead of opening it.

        Returns: None

        """
        # projectPath = getPathsFromScene("projectPath")
        projectPath = self.scenePaths["projectPath"]
        jsonInfo = loadJson(jsonFile)
        relSceneFile = jsonInfo["Versions"][version][0]  ## this is the relative scene path of the specified version
        sceneFile = os.path.join(projectPath, relSceneFile)

        if os.path.isfile(sceneFile):
            if importFile:
                cmds.file(sceneFile, i=True, force=force)
            else:
                cmds.file(sceneFile, o=True, force=force)
        else:
            pm.error("File in Scene Manager database doesnt exist")

    def deleteBaseScene(self, jsonFile):
        # projectPath = getPathsFromScene("projectPath")
        projectPath = self.scenePaths["projectPath"]

        jsonInfo = loadJson(jsonFile)

        # delete all version files
        for s in jsonInfo["Versions"]:
            try:
                os.remove(os.path.join(projectPath, s[0]))
            except:
                pm.warning("Cannot delete scene version:%s" % (s[0]))
                pass
        # delete reference file
        if jsonInfo["ReferenceFile"]:
            try:
                os.remove(os.path.join(projectPath, jsonInfo["ReferenceFile"]))
            except:
                pm.warning("Cannot delete reference file %s" % (jsonInfo["ReferenceFile"]))
                pass
        # delete base scene directory
        try:
            scene_path = os.path.join(projectPath, jsonInfo["Path"])
            os.rmdir(scene_path)
        except:
            pm.warning("Cannot delete scene path %s" % (scene_path))
            pass
        # delete json database file
        try:
            os.remove(os.path.join(projectPath, jsonFile))
        except:
            pm.warning("Cannot delete scene path %s" % (jsonFile))
            pass

    def deleteReference(self, jsonFile):
        # projectPath = getPathsFromScene("projectPath")
        projectPath = self.scenePaths["projectPath"]

        jsonInfo = loadJson(jsonFile)
        if jsonInfo["ReferenceFile"]:
            try:
                os.remove(os.path.join(projectPath, jsonInfo["ReferenceFile"]))
                jsonInfo["ReferenceFile"] = None
                jsonInfo["ReferencedVersion"] = None
                dumpJson(jsonInfo, jsonFile)
            except:
                pm.warning("Cannot delete reference file %s" % (jsonInfo["ReferenceFile"]))
                pass

    def makeReference(self, jsonFile, version):
        """
        Makes the given version valid reference file. Basically it copies that file and names it as <Shot Name>_forReference.mb.
        There can be only one reference file for one scene. If there is another reference file it will be written on. Since Reference files
        are duplicates of a version in the folder, it is safe to do that.
        Args:
            jsonFile: (String) Path to the json file which holds the information about the scene
            version: (Integer) Version number of the scene which will be copied as reference file.

        Returns: None

        """

        # projectPath = pm.workspace(q=1, rd=1)
        # projectPath = getPathsFromScene("projectPath")
        projectPath = self.scenePaths["projectPath"]

        jsonInfo = loadJson(jsonFile)

        if version == 0 or version > len(jsonInfo["Versions"]):
            pm.error("version number mismatch - (makeReference method)")
            return
        relSceneFile = jsonInfo["Versions"][version - 1][0]

        # sceneFile = "%s%s" %(projectPath, relSceneFile)
        sceneFile = os.path.join(projectPath, relSceneFile)
        referenceName = "{0}_{1}_forReference".format(jsonInfo["Name"], jsonInfo["Category"])
        relReferenceFile = os.path.join(jsonInfo["Path"], "{0}.mb".format(referenceName))
        # referenceFile = "%s%s" %(projectPath, relReferenceFile)
        referenceFile = os.path.join(projectPath, relReferenceFile)
        copyfile(sceneFile, referenceFile)
        jsonInfo["ReferenceFile"] = relReferenceFile
        jsonInfo["ReferencedVersion"] = version

        dumpJson(jsonInfo, jsonFile)

    def checkReference(self, jsonFile, deepCheck=False):
        """
        Checks the reference file in the json data exists or not.
        Args:
            jsonFile: (string path) data file path to look at
            deepCheck: (Boolean) if set yes, a checksum comparison will be performed. (Time consuming)

        Returns: True => 1 False => -1 No Reference => 0

        """
        # projectPath = getPathsFromScene("projectPath")
        projectPath = self.scenePaths["projectPath"]

        jsonInfo = loadJson(jsonFile)
        if jsonInfo["ReferenceFile"]:
            relRefVersion = jsonInfo["Versions"][jsonInfo["ReferencedVersion"] - 1][0]
            refVersion = os.path.join(projectPath, relRefVersion)
            relRefFile = jsonInfo["ReferenceFile"]
            absRefFile = os.path.join(projectPath, relRefFile)
            if not os.path.isfile(absRefFile):
                return -1 # code red
            else:
                if deepCheck:
                    if filecmp.cmp(refVersion, absRefFile):
                        return 1 # code green
                    else:
                        return -1 # code red (checksum mismatch)
                else:
                    return 1 # code green
        else:
            return 0 # code yellow


    def loadReference(self, jsonFile):
        # projectPath = getPathsFromScene("projectPath")
        projectPath = self.scenePaths["projectPath"]

        jsonInfo = loadJson(jsonFile)
        relReferenceFile = jsonInfo["ReferenceFile"]

        # os.path.isfile(referenceFile)
        if relReferenceFile:
            # referenceFile = "%s%s" % (projectPath, relReferenceFile)
            referenceFile = os.path.join(projectPath, relReferenceFile)
            # pm.FileReference(referenceFile)
            namespace = pathOps(referenceFile, "filename")
            cmds.file(os.path.normpath(referenceFile), reference=True, gl=True, mergeNamespacesOnClash=False,
                      namespace=namespace)

        else:
            pm.warning("There is no reference set for this scene. Nothing changed")

    def createThumbnail(self, jsonPath=None, version=None):

        if jsonPath and version:
            version= "v%s" %(str(version).zfill(self.padding))
            shotName=pathOps(jsonPath, "filename")
            projectPath = self.scenePaths["projectPath"]

        else: # if keywords are not given
        # resolve the path of the currently open scene
            sceneInfo = self.getSceneInfo()
            if not sceneInfo:
                return None
            projectPath=sceneInfo["projectPath"]
            jsonPath=sceneInfo["jsonFile"]
            shotName=sceneInfo["shotName"]
            version=sceneInfo["version"]

        thumbPath = "{0}_{1}_thumb.jpg".format(os.path.join(pathOps(jsonPath, "path"), shotName), version)
        relThumbPath = os.path.relpath(thumbPath, projectPath)
        # print thumbPath
        # create a thumbnail using playblast
        if os.path.exists(pathOps(thumbPath, "path")):
            frame = pm.currentTime(query=True)
            store = pm.getAttr("defaultRenderGlobals.imageFormat")
            pm.setAttr("defaultRenderGlobals.imageFormat", 8)  # This is the value for jpeg
            pm.playblast(completeFilename=thumbPath, forceOverwrite=True, format='image', width=221, height=124,
                         showOrnaments=False, frame=[frame], viewer=False, percent=100)
            pm.setAttr("defaultRenderGlobals.imageFormat", store) #take it back
        else:
            pm.warning("something went wrong with thumbnail. Skipping thumbnail")
            return None
        # return thumbPath
        return relThumbPath



    def replaceThumbnail(self, mode="file", jsonPath=None, version=None, filePath=None ):
        jsonInfo = loadJson(jsonPath)
        if mode == "file":
            if not filePath:
                pm.warning("filePath flag cannot be None in mode='file'")
                return
            ## do the replacement
            pass

        if mode == "currentView":
            ## do the replacement
            filePath = self.createThumbnail(jsonPath=jsonPath, version=version)

        try:
            jsonInfo["Versions"][version][5]=filePath
        except IndexError: # if this is an older file without thumbnail
            jsonInfo["Versions"][version].append(filePath)
        dumpJson(jsonInfo, jsonPath)

class MainUI(QtWidgets.QMainWindow):
    def __init__(self, scriptJob=None):
        self.scriptJob=scriptJob
        for entry in QtWidgets.QApplication.allWidgets():
            try:
                if entry.objectName() == SM_Version:
                    entry.close()
            except AttributeError:
                pass
        parent = getMayaMainWindow()
        super(MainUI, self).__init__(parent=parent)
        # super(MainUI, self).__init__(parent=None)

        problem, msg = checkRequirements()
        if problem:
            q = QtWidgets.QMessageBox()
            q.setIcon(QtWidgets.QMessageBox.Information)
            q.setText(msg[0])
            q.setInformativeText(msg[1])
            q.setWindowTitle(msg[2])
            q.setStandardButtons(QtWidgets.QMessageBox.Ok)

            ret = q.exec_()
            if ret == QtWidgets.QMessageBox.Ok:
                self.close()
                self.deleteLater()

        self.manager = TikManager()
        self.favList = []
        self.scenesInCategory = None
        self.imageManagerINS = None
        self.setObjectName((SM_Version))
        self.resize(680, 600)
        self.setMaximumSize(QtCore.QSize(680, 600))
        self.setWindowTitle((SM_Version))
        self.setToolTip((""))
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName(("centralwidget"))
        self.buildUI()

        # create scripJobs
        # scriptJob = "tik_sceneManager"
        if scriptJob:
            self.job_1 = pm.scriptJob(e=["workspaceChanged", "%s.refresh()" % scriptJob], parent=SM_Version)

        # self.statusBar().showMessage("System Status | Normal")

    def buildUI(self):
        self.baseScene_label = QtWidgets.QLabel(self.centralwidget)
        self.baseScene_label.setGeometry(QtCore.QRect(12, 10, 68, 21))
        self.baseScene_label.setStatusTip((""))
        self.baseScene_label.setFrameShape(QtWidgets.QFrame.Box)
        self.baseScene_label.setLineWidth(1)
        self.baseScene_label.setText(("Base Scene:"))
        self.baseScene_label.setTextFormat(QtCore.Qt.AutoText)
        self.baseScene_label.setScaledContents(False)
        self.baseScene_label.setObjectName(("baseScene_label"))

        self.baseScene_lineEdit = QtWidgets.QLabel(self.centralwidget)
        self.baseScene_lineEdit.setGeometry(QtCore.QRect(90, 10, 471, 21))
        self.baseScene_lineEdit.setStatusTip((""))
        self.baseScene_lineEdit.setText("")
        self.baseScene_lineEdit.setObjectName(("baseScene_lineEdit"))
        self.baseScene_lineEdit.setStyleSheet("QLabel {color:cyan}")

        self.projectPath_label = QtWidgets.QLabel(self.centralwidget)
        self.projectPath_label.setGeometry(QtCore.QRect(30, 36, 51, 21))
        self.projectPath_label.setStatusTip((""))
        self.projectPath_label.setFrameShape(QtWidgets.QFrame.Box)
        self.projectPath_label.setLineWidth(1)
        self.projectPath_label.setText(("Project:"))
        self.projectPath_label.setTextFormat(QtCore.Qt.AutoText)
        self.projectPath_label.setScaledContents(False)
        self.projectPath_label.setObjectName(("projectPath_label"))

        self.projectPath_lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.projectPath_lineEdit.setGeometry(QtCore.QRect(90, 36, 471, 21))
        self.projectPath_lineEdit.setStatusTip((""))
        self.projectPath_lineEdit.setText((self.manager.scenePaths["projectPath"]))
        self.projectPath_lineEdit.setReadOnly(True)
        self.projectPath_lineEdit.setObjectName(("projectPath_lineEdit"))

        self.setProject_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.setProject_pushButton.setGeometry(QtCore.QRect(580, 36, 75, 23))
        self.setProject_pushButton.setStatusTip((""))
        self.setProject_pushButton.setText(("SET"))
        self.setProject_pushButton.setObjectName(("setProject_pushButton"))

        self.category_tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.category_tabWidget.setGeometry(QtCore.QRect(30, 110, 621, 21))
        self.category_tabWidget.setStatusTip((""))
        self.category_tabWidget.setDocumentMode(True)
        self.category_tabWidget.setObjectName(("category_tabWidget"))

        for i in self.manager.validCategories:
            self.preTab = QtWidgets.QWidget()
            self.preTab.setObjectName((i))
            self.category_tabWidget.addTab(self.preTab, (i))

        self.loadMode_radioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.loadMode_radioButton.setGeometry(QtCore.QRect(30, 70, 82, 31))
        self.loadMode_radioButton.setStatusTip((""))
        self.loadMode_radioButton.setText(("Load Mode"))
        self.loadMode_radioButton.setChecked(True)
        self.loadMode_radioButton.setObjectName(("loadMode_radioButton"))

        self.referenceMode_radioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.referenceMode_radioButton.setGeometry(QtCore.QRect(110, 70, 101, 31))
        self.referenceMode_radioButton.setStatusTip((""))
        self.referenceMode_radioButton.setText(("Reference Mode"))
        self.referenceMode_radioButton.setObjectName(("referenceMode_radioButton"))

        self.userName_comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.userName_comboBox.setGeometry(QtCore.QRect(553, 70, 101, 31))
        self.userName_comboBox.setStatusTip((""))
        self.userName_comboBox.setObjectName(("userName_comboBox"))
        userListSorted = sorted(self.manager.userList.keys())
        for num in range(len(userListSorted)):
            self.userName_comboBox.addItem((userListSorted[num]))
            self.userName_comboBox.setItemText(num, (userListSorted[num]))

        # self.userName_comboBox.addItem((""))
        # self.userName_comboBox.setItemText(0, ("Arda Kutlu")

        self.userName_label = QtWidgets.QLabel(self.centralwidget)
        self.userName_label.setGeometry(QtCore.QRect(520, 70, 31, 31))
        self.userName_label.setStatusTip((""))
        self.userName_label.setText(("User:"))
        self.userName_label.setObjectName(("userName_label"))

        self.subProject_label = QtWidgets.QLabel(self.centralwidget)
        self.subProject_label.setGeometry(QtCore.QRect(240, 70, 100, 31))
        self.subProject_label.setStatusTip((""))
        self.subProject_label.setText(("Sub-Project:"))
        self.subProject_label.setObjectName(("subProject_label"))

        self.subProject_comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.subProject_comboBox.setGeometry(QtCore.QRect(305, 70, 165, 31))
        self.subProject_comboBox.setStatusTip((""))
        self.subProject_comboBox.setObjectName(("subProject_comboBox"))

        self.subProject_pushbutton = QtWidgets.QPushButton("+", self.centralwidget)
        self.subProject_pushbutton.setGeometry(QtCore.QRect(475, 70, 31, 31))
        self.subProject_pushbutton.setStatusTip((""))
        self.subProject_pushbutton.setObjectName(("subProject_pushbutton"))

        self.scenes_listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.scenes_listWidget.setGeometry(QtCore.QRect(30, 140, 381, 351))
        self.scenes_listWidget.setStatusTip((""))
        self.scenes_listWidget.setObjectName(("scenes_listWidget"))
        self.scenes_listWidget.setStyleSheet("border-style: solid; border-width: 2px; border-color: grey;")

        self.version_label = QtWidgets.QLabel(self.centralwidget)
        self.version_label.setGeometry(QtCore.QRect(430, 140, 51, 31))
        self.version_label.setStatusTip((""))
        self.version_label.setFrameShape(QtWidgets.QFrame.Box)
        self.version_label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.version_label.setText(("Version:"))
        self.version_label.setObjectName(("version_label"))

        self.version_comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.version_comboBox.setGeometry(QtCore.QRect(490, 140, 71, 31))
        self.version_comboBox.setStatusTip((""))
        self.version_comboBox.setObjectName(("version_comboBox"))

        self.showPB_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.showPB_pushButton.setGeometry(QtCore.QRect(580, 140, 72, 28))
        self.showPB_pushButton.setStatusTip((""))
        self.showPB_pushButton.setText(("Show PB"))
        self.showPB_pushButton.setObjectName(("showPB_pushButton"))

        self.makeReference_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.makeReference_pushButton.setGeometry(QtCore.QRect(430, 185, 102, 23))
        self.makeReference_pushButton.setStatusTip((""))
        self.makeReference_pushButton.setText(("Make Reference"))
        self.makeReference_pushButton.setShortcut((""))
        self.makeReference_pushButton.setObjectName(("makeReference_pushButton"))

        self.addNotes_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.addNotes_pushButton.setGeometry(QtCore.QRect(550, 185, 102, 23))
        self.addNotes_pushButton.setStatusTip((""))
        self.addNotes_pushButton.setText(("Add Note"))
        self.addNotes_pushButton.setShortcut((""))
        self.addNotes_pushButton.setObjectName(("addNotes_pushButton"))

        self.notes_label = QtWidgets.QLabel(self.centralwidget)
        self.notes_label.setGeometry(QtCore.QRect(430, 220, 70, 13))
        self.notes_label.setStatusTip((""))
        self.notes_label.setText(("Version Notes:"))
        self.notes_label.setObjectName(("notes_label"))

        self.notes_textEdit = QtWidgets.QTextEdit(self.centralwidget, readOnly=True)
        self.notes_textEdit.setGeometry(QtCore.QRect(430, 240, 221, 110))
        self.notes_textEdit.setStatusTip((""))
        self.notes_textEdit.setObjectName(("notes_textEdit"))

        self.thumbnail_label = QtWidgets.QLabel(self.centralwidget)
        self.thumbnail_label.setGeometry(QtCore.QRect(430, 365, 221, 124))
        self.thumbnail_label.setStatusTip((""))
        self.thumbnail_label.setFrameShape(QtWidgets.QFrame.Box)
        self.thumbnail_label.setLineWidth(1)
        self.thumbnail_label.setText((""))
        self.thumbnail_label.setTextFormat(QtCore.Qt.AutoText)
        self.thumbnail_label.setScaledContents(False)
        self.thumbnail_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.thumbnail_label.setObjectName(("thumbnail_label"))

        self.saveScene_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.saveScene_pushButton.setGeometry(QtCore.QRect(40, 510, 151, 41))
        self.saveScene_pushButton.setStatusTip((""))
        self.saveScene_pushButton.setText(("Save Base Scene"))
        self.saveScene_pushButton.setObjectName(("saveScene_pushButton"))

        self.saveAsVersion_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.saveAsVersion_pushButton.setGeometry(QtCore.QRect(210, 510, 151, 41))
        self.saveAsVersion_pushButton.setStatusTip((""))
        self.saveAsVersion_pushButton.setText(("Save As Version"))
        self.saveAsVersion_pushButton.setObjectName(("saveAsVersion_pushButton"))

        self.load_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.load_pushButton.setGeometry(QtCore.QRect(500, 510, 151, 41))
        self.load_pushButton.setStatusTip((""))
        self.load_pushButton.setText(("Load Scene"))
        self.load_pushButton.setObjectName(("load_pushButton"))

        self.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 680, 18))
        self.menubar.setObjectName(("menubar"))
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName(("statusbar"))
        self.setStatusBar(self.statusbar)
        self.setStatusBar(self.statusbar)

        file = self.menubar.addMenu("File")
        saveVersion_fm = QtWidgets.QAction("&Save Version", self)
        saveBaseScene_fm = QtWidgets.QAction("&Save Base Scene", self)
        loadReferenceScene_fm = QtWidgets.QAction("&Load/Reference Scene", self)
        createProject_fm = QtWidgets.QAction("&Create Project", self)
        pb_settings_fm = QtWidgets.QAction("&Playblast Settings", self)
        add_remove_users_fm = QtWidgets.QAction("&Add/Remove Users", self)
        deleteFile_fm = QtWidgets.QAction("&Delete Selected Base Scene", self)
        deleteReference_fm = QtWidgets.QAction("&Delete Reference of Selected Scene", self)
        reBuildDatabase_fm = QtWidgets.QAction("&Re-build Project Database", self)
        projectReport_fm = QtWidgets.QAction("&Project Report", self)
        checkReferences_fm = QtWidgets.QAction("&Check References", self)

        # file.addAction(createProject_fm)
        # file.addAction(pb_settings_fm)
        # file.addAction(add_remove_users_fm)
        # file.addAction(deleteFile_fm)
        # file.addAction(deleteReference_fm)
        # file.addAction(reBuildDatabase_fm)
        # file.addAction(projectReport_fm)
        # file.addAction(checkReferences_fm)

        #save
        file.addAction(createProject_fm)
        file.addAction(saveVersion_fm)
        file.addAction(saveBaseScene_fm)

        #load
        file.addSeparator()
        file.addAction(loadReferenceScene_fm)

        #settings
        file.addSeparator()
        file.addAction(add_remove_users_fm)
        file.addAction(pb_settings_fm)

        #delete
        file.addSeparator()
        file.addAction(deleteFile_fm)
        file.addAction(deleteReference_fm)

        #misc
        file.addSeparator()
        file.addAction(projectReport_fm)
        file.addAction(checkReferences_fm)


        createProject_fm.triggered.connect(self.createProjectUI)
        saveVersion_fm.triggered.connect(self.saveAsVersionDialog)
        saveBaseScene_fm.triggered.connect(self.saveBaseSceneDialog)
        loadReferenceScene_fm.triggered.connect(self.onloadScene)
        add_remove_users_fm.triggered.connect(self.addRemoveUserUI)
        deleteFile_fm.triggered.connect(lambda: self.onDeleteBaseScene())
        deleteReference_fm.triggered.connect(self.onDeleteReference)
        # reBuildDatabase_fm.triggered.connect(lambda: suMod.SuManager().rebuildDatabase())
        projectReport_fm.triggered.connect(lambda: self.manager.projectReport())
        pb_settings_fm.triggered.connect(self.pbSettingsUI)
        checkReferences_fm.triggered.connect(lambda: self.onReferenceCheck(deepCheck=True))



        tools = self.menubar.addMenu("Tools")
        # foolsMate = QtWidgets.QAction("&Fool's Mate", self)
        imanager = QtWidgets.QAction("&Image Manager", self)
        iviewer = QtWidgets.QAction("&Image Viewer", self)
        createPB = QtWidgets.QAction("&Create PlayBlast", self)
        # tools.addAction(foolsMate)
        tools.addAction(imanager)
        tools.addAction(iviewer)
        tools.addAction(createPB)
        # submitToDeadline = QtWidgets.QAction("&Submit to Deadline", self)
        # tools.addAction(submitToDeadline)

        # foolsMate.triggered.connect(self.onFoolsMate)
        imanager.triggered.connect(self.onImanager)
        iviewer.triggered.connect(self.onIviewer)
        createPB.triggered.connect(self.onCreatePB)
        # submitToDeadline.triggered.connect()

        self.loadMode_radioButton.toggled.connect(self.onRadioButtonsToggled)
        self.referenceMode_radioButton.toggled.connect(self.onRadioButtonsToggled)


        self.setProject_pushButton.clicked.connect(self.onSetProject)

        self.category_tabWidget.currentChanged.connect(self.populateScenes)

        self.scenes_listWidget.currentItemChanged.connect(self.sceneInfo)

        self.makeReference_pushButton.clicked.connect(self.onMakeReference)
        self.addNotes_pushButton.clicked.connect(self.onAddNotes)

        self.saveScene_pushButton.clicked.connect(self.saveBaseSceneDialog)

        self.saveAsVersion_pushButton.clicked.connect(self.saveAsVersionDialog)

        self.subProject_pushbutton.clicked.connect(self.createSubProjectUI)

        self.subProject_comboBox.activated.connect(self.onSubProjectChanged)

        self.load_pushButton.clicked.connect(self.onloadScene)

        # self.userName_comboBox.currentIndexChanged.connect(self.userPrefSave)
        self.userName_comboBox.activated.connect(self.userPrefSave)

        self.version_comboBox.activated.connect(self.refreshNotes)
        self.version_comboBox.activated.connect(self.refreshThumbnail)

        self.scenes_listWidget.doubleClicked.connect(self.onloadScene)

        self.showPB_pushButton.clicked.connect(self.onShowPBclicked)

        ## RIGHT CLICK MENUS
        self.scenes_listWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.scenes_listWidget.customContextMenuRequested.connect(self.onContextMenu_scenes)
        self.popMenu = QtWidgets.QMenu()

        rcAction_0 = QtWidgets.QAction('Import Scene', self)
        self.popMenu.addAction(rcAction_0)
        rcAction_0.triggered.connect(lambda: self.rcAction("importScene"))

        self.popMenu.addSeparator()

        rcAction_1 = QtWidgets.QAction('Show Maya Folder in Explorer', self)
        self.popMenu.addAction(rcAction_1)
        rcAction_1.triggered.connect(lambda: self.rcAction("showInExplorerMaya"))

        rcAction_2 = QtWidgets.QAction('Show Playblast Folder in Explorer', self)
        self.popMenu.addAction(rcAction_2)
        rcAction_2.triggered.connect(lambda: self.rcAction("showInExplorerPB"))

        rcAction_3 = QtWidgets.QAction('Show Data Folder in Explorer', self)
        self.popMenu.addAction(rcAction_3)
        rcAction_3.triggered.connect(lambda: self.rcAction("showInExplorerData"))

        self.popMenu.addSeparator()

        rcAction_4 = QtWidgets.QAction('Scene Info', self)
        self.popMenu.addAction(rcAction_4)
        rcAction_4.triggered.connect(lambda: self.onSceneInfo())

        ########

        self.thumbnail_label.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.thumbnail_label.customContextMenuRequested.connect(self.onContextMenu_thumbnail)
        self.popMenu_thumbnail = QtWidgets.QMenu()

        rcAction_5 = QtWidgets.QAction('Replace with current view', self)
        self.popMenu_thumbnail.addAction(rcAction_5)
        rcAction_5.triggered.connect(lambda: self.onChangeThumbnail("currentView"))

        rcAction_6 = QtWidgets.QAction('Replace with external file', self)
        self.popMenu_thumbnail.addAction(rcAction_6)
        rcAction_6.triggered.connect(lambda: self.onChangeThumbnail("file"))

        #######
        shortcutRefresh = Qt.QtWidgets.QShortcut(Qt.QtGui.QKeySequence("F5"), self, self.refresh)

        self.userPrefLoad()
        self.populateScenes()
        # self.manager.remoteLogger()
        self.statusBar().showMessage("Status | Idle")

    def pbSettingsUI(self):

        admin_pswd = "682"
        passw, ok = QtWidgets.QInputDialog.getText(self, "Password Query", "Enter Admin Password:",
                                                   QtWidgets.QLineEdit.Password)
        if ok:
            if passw == admin_pswd:
                pass
            else:
                self.infoPop(textTitle="Incorrect Password", textHeader="The Password is invalid")
                return
        else:
            return
        currentSettings = self.manager.getPBsettings()

        self.pbSettings_dialog = QtWidgets.QDialog(parent=self)
        self.pbSettings_dialog.setModal(True)
        self.pbSettings_dialog.setObjectName(("Playblast_Dialog"))
        self.pbSettings_dialog.resize(380, 483)
        self.pbSettings_dialog.setMinimumSize(QtCore.QSize(380, 550))
        self.pbSettings_dialog.setMaximumSize(QtCore.QSize(380, 550))
        self.pbSettings_dialog.setWindowTitle(("Set Playblast Settings"))
        self.pbSettings_dialog.setToolTip((""))
        self.pbSettings_dialog.setStatusTip((""))
        self.pbSettings_dialog.setWhatsThis((""))
        self.pbSettings_dialog.setAccessibleName((""))
        self.pbSettings_dialog.setAccessibleDescription((""))

        self.pbsettings_buttonBox = QtWidgets.QDialogButtonBox(self.pbSettings_dialog)
        self.pbsettings_buttonBox.setGeometry(QtCore.QRect(20, 500, 341, 30))
        self.pbsettings_buttonBox.setToolTip((""))
        self.pbsettings_buttonBox.setStatusTip((""))
        self.pbsettings_buttonBox.setWhatsThis((""))
        self.pbsettings_buttonBox.setAccessibleName((""))
        self.pbsettings_buttonBox.setAccessibleDescription((""))
        self.pbsettings_buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.pbsettings_buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Save)
        self.pbsettings_buttonBox.setObjectName(("pbsettings_buttonBox"))

        self.videoproperties_groupBox = QtWidgets.QGroupBox(self.pbSettings_dialog)
        self.videoproperties_groupBox.setGeometry(QtCore.QRect(10, 20, 361, 191))
        self.videoproperties_groupBox.setToolTip((""))
        self.videoproperties_groupBox.setStatusTip((""))
        self.videoproperties_groupBox.setWhatsThis((""))
        self.videoproperties_groupBox.setAccessibleName((""))
        self.videoproperties_groupBox.setAccessibleDescription((""))
        self.videoproperties_groupBox.setTitle(("Video Properties"))
        self.videoproperties_groupBox.setObjectName(("videoproperties_groupBox"))

        self.fileformat_label = QtWidgets.QLabel(self.videoproperties_groupBox)
        self.fileformat_label.setGeometry(QtCore.QRect(20, 30, 71, 20))
        self.fileformat_label.setToolTip((""))
        self.fileformat_label.setStatusTip((""))
        self.fileformat_label.setWhatsThis((""))
        self.fileformat_label.setAccessibleName((""))
        self.fileformat_label.setAccessibleDescription((""))
        self.fileformat_label.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.fileformat_label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.fileformat_label.setText(("Format"))
        self.fileformat_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.fileformat_label.setObjectName(("fileformat_label"))

        self.fileformat_comboBox = QtWidgets.QComboBox(self.videoproperties_groupBox)
        self.fileformat_comboBox.setGeometry(QtCore.QRect(100, 30, 111, 22))
        self.fileformat_comboBox.setToolTip((""))
        self.fileformat_comboBox.setStatusTip((""))
        self.fileformat_comboBox.setWhatsThis((""))
        self.fileformat_comboBox.setAccessibleName((""))
        self.fileformat_comboBox.setAccessibleDescription((""))
        self.fileformat_comboBox.setObjectName(("fileformat_comboBox"))
        formats = pm.playblast(query=True, format=True)
        self.fileformat_comboBox.addItems(formats)

        # get the index number from the name in the settings file and make that index active
        ffindex = self.fileformat_comboBox.findText(currentSettings["Format"], QtCore.Qt.MatchFixedString)
        if ffindex >= 0:
            self.fileformat_comboBox.setCurrentIndex(ffindex)

        self.codec_label = QtWidgets.QLabel(self.videoproperties_groupBox)
        self.codec_label.setGeometry(QtCore.QRect(30, 70, 61, 20))
        self.codec_label.setToolTip((""))
        self.codec_label.setStatusTip((""))
        self.codec_label.setWhatsThis((""))
        self.codec_label.setAccessibleName((""))
        self.codec_label.setAccessibleDescription((""))
        self.codec_label.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.codec_label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.codec_label.setText(("Codec"))
        self.codec_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.codec_label.setObjectName(("codec_label"))

        self.codec_comboBox = QtWidgets.QComboBox(self.videoproperties_groupBox)
        self.codec_comboBox.setGeometry(QtCore.QRect(100, 70, 111, 22))
        self.codec_comboBox.setToolTip((""))
        self.codec_comboBox.setStatusTip((""))
        self.codec_comboBox.setWhatsThis((""))
        self.codec_comboBox.setAccessibleName((""))
        self.codec_comboBox.setAccessibleDescription((""))
        self.codec_comboBox.setObjectName(("codec_comboBox"))
        self.updateCodecs()

        self.fileformat_comboBox.currentIndexChanged.connect(self.updateCodecs)

        # get the index number from the name in the settings file and make that index active
        cindex = self.codec_comboBox.findText(currentSettings["Codec"], QtCore.Qt.MatchFixedString)
        if cindex >= 0:
            self.codec_comboBox.setCurrentIndex(cindex)

        self.quality_label = QtWidgets.QLabel(self.videoproperties_groupBox)
        self.quality_label.setGeometry(QtCore.QRect(30, 110, 61, 20))
        self.quality_label.setToolTip((""))
        self.quality_label.setStatusTip((""))
        self.quality_label.setWhatsThis((""))
        self.quality_label.setAccessibleName((""))
        self.quality_label.setAccessibleDescription((""))
        self.quality_label.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.quality_label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.quality_label.setText(("Quality"))
        self.quality_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.quality_label.setObjectName(("quality_label"))

        self.quality_spinBox = QtWidgets.QSpinBox(self.videoproperties_groupBox)
        self.quality_spinBox.setGeometry(QtCore.QRect(100, 110, 41, 21))
        self.quality_spinBox.setToolTip((""))
        self.quality_spinBox.setStatusTip((""))
        self.quality_spinBox.setWhatsThis((""))
        self.quality_spinBox.setAccessibleName((""))
        self.quality_spinBox.setAccessibleDescription((""))
        self.quality_spinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.quality_spinBox.setMinimum(1)
        self.quality_spinBox.setMaximum(100)
        self.quality_spinBox.setProperty("value", currentSettings["Quality"])
        self.quality_spinBox.setObjectName(("quality_spinBox"))

        self.quality_horizontalSlider = QtWidgets.QSlider(self.videoproperties_groupBox)
        self.quality_horizontalSlider.setGeometry(QtCore.QRect(150, 110, 191, 21))
        self.quality_horizontalSlider.setToolTip((""))
        self.quality_horizontalSlider.setStatusTip((""))
        self.quality_horizontalSlider.setWhatsThis((""))
        self.quality_horizontalSlider.setAccessibleName((""))
        self.quality_horizontalSlider.setAccessibleDescription((""))
        self.quality_horizontalSlider.setMinimum(1)
        self.quality_horizontalSlider.setMaximum(100)
        self.quality_horizontalSlider.setProperty("value", currentSettings["Quality"])
        self.quality_horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.quality_horizontalSlider.setTickInterval(0)
        self.quality_horizontalSlider.setObjectName(("quality_horizontalSlider"))

        self.resolution_label = QtWidgets.QLabel(self.videoproperties_groupBox)
        self.resolution_label.setGeometry(QtCore.QRect(30, 150, 61, 20))
        self.resolution_label.setToolTip((""))
        self.resolution_label.setStatusTip((""))
        self.resolution_label.setWhatsThis((""))
        self.resolution_label.setAccessibleName((""))
        self.resolution_label.setAccessibleDescription((""))
        self.resolution_label.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.resolution_label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.resolution_label.setText(("Resolution"))
        self.resolution_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.resolution_label.setObjectName(("resolution_label"))

        self.resolutionx_spinBox = QtWidgets.QSpinBox(self.videoproperties_groupBox)
        self.resolutionx_spinBox.setGeometry(QtCore.QRect(100, 150, 61, 21))
        self.resolutionx_spinBox.setToolTip((""))
        self.resolutionx_spinBox.setStatusTip((""))
        self.resolutionx_spinBox.setWhatsThis((""))
        self.resolutionx_spinBox.setAccessibleName((""))
        self.resolutionx_spinBox.setAccessibleDescription((""))
        self.resolutionx_spinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.resolutionx_spinBox.setMinimum(0)
        self.resolutionx_spinBox.setMaximum(4096)
        self.resolutionx_spinBox.setProperty("value", currentSettings["Resolution"][0])
        self.resolutionx_spinBox.setObjectName(("resolutionx_spinBox"))

        self.resolutiony_spinBox = QtWidgets.QSpinBox(self.videoproperties_groupBox)
        self.resolutiony_spinBox.setGeometry(QtCore.QRect(170, 150, 61, 21))
        self.resolutiony_spinBox.setToolTip((""))
        self.resolutiony_spinBox.setStatusTip((""))
        self.resolutiony_spinBox.setWhatsThis((""))
        self.resolutiony_spinBox.setAccessibleName((""))
        self.resolutiony_spinBox.setAccessibleDescription((""))
        self.resolutiony_spinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.resolutiony_spinBox.setMinimum(1)
        self.resolutiony_spinBox.setMaximum(4096)
        self.resolutiony_spinBox.setProperty("value", currentSettings["Resolution"][1])
        self.resolutiony_spinBox.setObjectName(("resolutiony_spinBox"))

        self.viewportoptions_groupBox = QtWidgets.QGroupBox(self.pbSettings_dialog)
        self.viewportoptions_groupBox.setGeometry(QtCore.QRect(10, 230, 361, 120))
        self.viewportoptions_groupBox.setTitle(("Viewport Options"))
        self.viewportoptions_groupBox.setObjectName(("viewportoptions_groupBox"))

        self.polygononly_checkBox = QtWidgets.QCheckBox(self.viewportoptions_groupBox)
        self.polygononly_checkBox.setGeometry(QtCore.QRect(60, 30, 91, 20))
        self.polygononly_checkBox.setToolTip((""))
        self.polygononly_checkBox.setStatusTip((""))
        self.polygononly_checkBox.setWhatsThis((""))
        self.polygononly_checkBox.setAccessibleName((""))
        self.polygononly_checkBox.setAccessibleDescription((""))
        self.polygononly_checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.polygononly_checkBox.setText(("Polygon Only"))
        self.polygononly_checkBox.setChecked(currentSettings["PolygonOnly"])
        self.polygononly_checkBox.setObjectName(("polygononly_checkBox"))

        self.showgrid_checkBox = QtWidgets.QCheckBox(self.viewportoptions_groupBox)
        self.showgrid_checkBox.setGeometry(QtCore.QRect(210, 30, 91, 20))
        self.showgrid_checkBox.setToolTip((""))
        self.showgrid_checkBox.setStatusTip((""))
        self.showgrid_checkBox.setWhatsThis((""))
        self.showgrid_checkBox.setAccessibleName((""))
        self.showgrid_checkBox.setAccessibleDescription((""))
        self.showgrid_checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.showgrid_checkBox.setText(("Show Grid"))
        self.showgrid_checkBox.setChecked(currentSettings["ShowGrid"])
        self.showgrid_checkBox.setObjectName(("showgrid_checkBox"))

        self.clearselection_checkBox = QtWidgets.QCheckBox(self.viewportoptions_groupBox)
        self.clearselection_checkBox.setGeometry(QtCore.QRect(60, 60, 91, 20))
        self.clearselection_checkBox.setToolTip((""))
        self.clearselection_checkBox.setStatusTip((""))
        self.clearselection_checkBox.setWhatsThis((""))
        self.clearselection_checkBox.setAccessibleName((""))
        self.clearselection_checkBox.setAccessibleDescription((""))
        self.clearselection_checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.clearselection_checkBox.setText(("Clear Selection"))
        self.clearselection_checkBox.setChecked(currentSettings["ClearSelection"])
        self.clearselection_checkBox.setObjectName(("clearselection_checkBox"))

        self.wireonshaded_checkBox = QtWidgets.QCheckBox(self.viewportoptions_groupBox)
        self.wireonshaded_checkBox.setGeometry(QtCore.QRect(51, 90, 100, 20))
        self.wireonshaded_checkBox.setToolTip((""))
        self.wireonshaded_checkBox.setStatusTip((""))
        self.wireonshaded_checkBox.setWhatsThis((""))
        self.wireonshaded_checkBox.setAccessibleName((""))
        self.wireonshaded_checkBox.setAccessibleDescription((""))
        self.wireonshaded_checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.wireonshaded_checkBox.setText(("Wire On Shaded"))
        try:
            self.wireonshaded_checkBox.setChecked(currentSettings["WireOnShaded"])
        except KeyError:
            self.wireonshaded_checkBox.setChecked(False)
        self.wireonshaded_checkBox.setObjectName(("wireonshaded_checkBox"))

        self.usedefaultmaterial_checkBox = QtWidgets.QCheckBox(self.viewportoptions_groupBox)
        self.usedefaultmaterial_checkBox.setGeometry(QtCore.QRect(180, 90, 120, 20))
        self.usedefaultmaterial_checkBox.setToolTip((""))
        self.usedefaultmaterial_checkBox.setStatusTip((""))
        self.usedefaultmaterial_checkBox.setWhatsThis((""))
        self.usedefaultmaterial_checkBox.setAccessibleName((""))
        self.usedefaultmaterial_checkBox.setAccessibleDescription((""))
        self.usedefaultmaterial_checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.usedefaultmaterial_checkBox.setText(("Use Default Material"))
        try:
            self.usedefaultmaterial_checkBox.setChecked(currentSettings["UseDefaultMaterial"])
        except KeyError:
            self.usedefaultmaterial_checkBox.setChecked(False)

        self.displaytextures_checkBox = QtWidgets.QCheckBox(self.viewportoptions_groupBox)
        self.displaytextures_checkBox.setGeometry(QtCore.QRect(190, 60, 111, 20))
        self.displaytextures_checkBox.setToolTip((""))
        self.displaytextures_checkBox.setStatusTip((""))
        self.displaytextures_checkBox.setWhatsThis((""))
        self.displaytextures_checkBox.setAccessibleName((""))
        self.displaytextures_checkBox.setAccessibleDescription((""))
        self.displaytextures_checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.displaytextures_checkBox.setText(("Display Textures"))
        self.displaytextures_checkBox.setChecked(currentSettings["DisplayTextures"])
        self.displaytextures_checkBox.setObjectName(("displaytextures_checkBox"))

        self.hudoptions_groupBox = QtWidgets.QGroupBox(self.pbSettings_dialog)
        self.hudoptions_groupBox.setGeometry(QtCore.QRect(10, 370, 361, 110))
        self.hudoptions_groupBox.setToolTip((""))
        self.hudoptions_groupBox.setStatusTip((""))
        self.hudoptions_groupBox.setWhatsThis((""))
        self.hudoptions_groupBox.setAccessibleName((""))
        self.hudoptions_groupBox.setAccessibleDescription((""))
        self.hudoptions_groupBox.setTitle(("HUD Options"))
        self.hudoptions_groupBox.setObjectName(("hudoptions_groupBox"))

        self.showframenumber_checkBox = QtWidgets.QCheckBox(self.hudoptions_groupBox)
        self.showframenumber_checkBox.setGeometry(QtCore.QRect(20, 20, 131, 20))
        self.showframenumber_checkBox.setToolTip((""))
        self.showframenumber_checkBox.setStatusTip((""))
        self.showframenumber_checkBox.setWhatsThis((""))
        self.showframenumber_checkBox.setAccessibleName((""))
        self.showframenumber_checkBox.setAccessibleDescription((""))
        self.showframenumber_checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.showframenumber_checkBox.setText(("Show Frame Number"))
        self.showframenumber_checkBox.setChecked(currentSettings["ShowFrameNumber"])
        self.showframenumber_checkBox.setObjectName(("showframenumber_checkBox"))

        self.showscenename_checkBox = QtWidgets.QCheckBox(self.hudoptions_groupBox)
        self.showscenename_checkBox.setGeometry(QtCore.QRect(20, 50, 131, 20))
        self.showscenename_checkBox.setToolTip((""))
        self.showscenename_checkBox.setStatusTip((""))
        self.showscenename_checkBox.setWhatsThis((""))
        self.showscenename_checkBox.setAccessibleName((""))
        self.showscenename_checkBox.setAccessibleDescription((""))
        self.showscenename_checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.showscenename_checkBox.setText(("Show Scene Name"))
        self.showscenename_checkBox.setChecked(currentSettings["ShowSceneName"])
        self.showscenename_checkBox.setObjectName(("showscenename_checkBox"))

        self.showcategory_checkBox = QtWidgets.QCheckBox(self.hudoptions_groupBox)
        self.showcategory_checkBox.setGeometry(QtCore.QRect(200, 20, 101, 20))
        self.showcategory_checkBox.setToolTip((""))
        self.showcategory_checkBox.setStatusTip((""))
        self.showcategory_checkBox.setWhatsThis((""))
        self.showcategory_checkBox.setAccessibleName((""))
        self.showcategory_checkBox.setAccessibleDescription((""))
        self.showcategory_checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.showcategory_checkBox.setText(("Show Category"))
        self.showcategory_checkBox.setChecked(currentSettings["ShowCategory"])
        self.showcategory_checkBox.setObjectName(("showcategory_checkBox"))

        self.showfps_checkBox = QtWidgets.QCheckBox(self.hudoptions_groupBox)
        self.showfps_checkBox.setGeometry(QtCore.QRect(200, 50, 101, 20))
        self.showfps_checkBox.setToolTip((""))
        self.showfps_checkBox.setStatusTip((""))
        self.showfps_checkBox.setWhatsThis((""))
        self.showfps_checkBox.setAccessibleName((""))
        self.showfps_checkBox.setAccessibleDescription((""))
        self.showfps_checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.showfps_checkBox.setText(("Show FPS"))
        self.showfps_checkBox.setChecked(currentSettings["ShowFPS"])
        self.showfps_checkBox.setObjectName(("showfps_checkBox"))

        self.showframerange_checkBox = QtWidgets.QCheckBox(self.hudoptions_groupBox)
        self.showframerange_checkBox.setGeometry(QtCore.QRect(20, 80, 131, 20))
        self.showframerange_checkBox.setToolTip((""))
        self.showframerange_checkBox.setStatusTip((""))
        self.showframerange_checkBox.setWhatsThis((""))
        self.showframerange_checkBox.setAccessibleName((""))
        self.showframerange_checkBox.setAccessibleDescription((""))
        self.showframerange_checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.showframerange_checkBox.setText(("Show Frame Range"))
        # v1.1 SPECIFIC
        try:
            self.showframerange_checkBox.setChecked(currentSettings["ShowFrameRange"])
        except KeyError:
            self.showframerange_checkBox.setChecked(True)
        self.showframerange_checkBox.setObjectName(("showframerange_checkBox"))

        self.pbsettings_buttonBox.accepted.connect(self.pbSettings_dialog.accept)
        self.pbsettings_buttonBox.accepted.connect(self.onPbSettingsAccept)
        self.pbsettings_buttonBox.rejected.connect(self.pbSettings_dialog.reject)
        self.quality_spinBox.valueChanged.connect(self.quality_horizontalSlider.setValue)
        self.quality_horizontalSlider.valueChanged.connect(self.quality_spinBox.setValue)

        self.pbSettings_dialog.show()

    def createSubProjectUI(self):

        newSub, ok = QtWidgets.QInputDialog.getText(self, "Create New Sub-Project", "Enter an unique Sub-Project name:")
        if ok:
            name = nameCheck(newSub)
            if not name == -1:
                self.subProject_comboBox.clear()
                self.manager.subProjectList = self.manager.createSubProject(name)
                self.populateScenes()
            else:
                self.infoPop(textTitle="Naming Error", textHeader="Naming Error",
                             textInfo="Choose an unique name with latin characters without spaces", type="C")

    def createProjectUI(self):

        self.createproject_Dialog = QtWidgets.QDialog(parent=self)
        self.createproject_Dialog.setObjectName(("createproject_Dialog"))
        self.createproject_Dialog.resize(419, 249)
        self.createproject_Dialog.setWindowTitle(("Create New Project"))
        self.createproject_Dialog.setToolTip((""))
        self.createproject_Dialog.setStatusTip((""))
        self.createproject_Dialog.setWhatsThis((""))
        self.createproject_Dialog.setAccessibleName((""))
        self.createproject_Dialog.setAccessibleDescription((""))

        self.projectroot_label = QtWidgets.QLabel(self.createproject_Dialog)
        self.projectroot_label.setGeometry(QtCore.QRect(20, 30, 71, 20))
        self.projectroot_label.setText(("Project Path:"))
        self.projectroot_label.setObjectName(("projectpath_label"))

        currentProjects = os.path.abspath(os.path.join(self.manager.scenePaths["projectPath"], os.pardir))
        self.projectroot_lineEdit = QtWidgets.QLineEdit(self.createproject_Dialog)
        self.projectroot_lineEdit.setGeometry(QtCore.QRect(90, 30, 241, 21))
        self.projectroot_lineEdit.setText((currentProjects))
        self.projectroot_lineEdit.setPlaceholderText((""))
        self.projectroot_lineEdit.setObjectName(("projectpath_lineEdit"))

        self.browse_pushButton = QtWidgets.QPushButton(self.createproject_Dialog)
        self.browse_pushButton.setText(("Browse"))
        self.browse_pushButton.setGeometry(QtCore.QRect(340, 30, 61, 21))
        self.browse_pushButton.setObjectName(("browse_pushButton"))

        self.resolvedpath_label = QtWidgets.QLabel(self.createproject_Dialog)
        self.resolvedpath_label.setGeometry(QtCore.QRect(20, 70, 381, 21))
        self.resolvedpath_label.setObjectName(("resolvedpath_label"))

        self.brandname_label = QtWidgets.QLabel(self.createproject_Dialog)
        self.brandname_label.setGeometry(QtCore.QRect(20, 110, 111, 20))
        self.brandname_label.setFrameShape(QtWidgets.QFrame.Box)
        self.brandname_label.setText(("Brand Name"))
        self.brandname_label.setAlignment(QtCore.Qt.AlignCenter)
        self.brandname_label.setObjectName(("brandname_label"))

        self.projectname_label = QtWidgets.QLabel(self.createproject_Dialog)
        self.projectname_label.setGeometry(QtCore.QRect(140, 110, 131, 20))
        self.projectname_label.setFrameShape(QtWidgets.QFrame.Box)
        self.projectname_label.setText(("Project Name"))
        self.projectname_label.setAlignment(QtCore.Qt.AlignCenter)
        self.projectname_label.setObjectName(("projectname_label"))

        self.client_label = QtWidgets.QLabel(self.createproject_Dialog)
        self.client_label.setGeometry(QtCore.QRect(280, 110, 121, 20))
        self.client_label.setFrameShape(QtWidgets.QFrame.Box)
        self.client_label.setText(("Client"))
        self.client_label.setAlignment(QtCore.Qt.AlignCenter)
        self.client_label.setObjectName(("client_label"))

        self.brandname_lineEdit = QtWidgets.QLineEdit(self.createproject_Dialog)
        self.brandname_lineEdit.setGeometry(QtCore.QRect(20, 140, 111, 21))
        self.brandname_lineEdit.setText((""))
        self.brandname_lineEdit.setPlaceholderText(("(optional)"))
        self.brandname_lineEdit.setObjectName(("brandname_lineEdit"))

        self.projectname_lineEdit = QtWidgets.QLineEdit(self.createproject_Dialog)
        self.projectname_lineEdit.setGeometry(QtCore.QRect(140, 140, 131, 21))
        self.projectname_lineEdit.setText((""))
        self.projectname_lineEdit.setPlaceholderText(("Mandatory Field"))
        self.projectname_lineEdit.setObjectName(("projectname_lineEdit"))

        self.client_lineEdit = QtWidgets.QLineEdit(self.createproject_Dialog)
        self.client_lineEdit.setGeometry(QtCore.QRect(280, 140, 121, 21))
        self.client_lineEdit.setText((""))
        self.client_lineEdit.setPlaceholderText(("Mandatory Field"))
        self.client_lineEdit.setObjectName(("client_lineEdit"))

        self.createproject_buttonBox = QtWidgets.QDialogButtonBox(self.createproject_Dialog)
        self.createproject_buttonBox.setGeometry(QtCore.QRect(30, 190, 371, 32))
        self.createproject_buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.createproject_buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.createproject_buttonBox.setObjectName(("buttonBox"))

        self.cp_button = self.createproject_buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
        self.cp_button.setText('Create Project')

        self.createproject_Dialog.show()

        self.resolveProjectPath()
        self.browse_pushButton.clicked.connect(self.browseProjectRoot)
        self.brandname_lineEdit.textEdited.connect(self.resolveProjectPath)
        self.projectname_lineEdit.textEdited.connect(self.resolveProjectPath)
        self.client_lineEdit.textEdited.connect(self.resolveProjectPath)

        self.createproject_buttonBox.accepted.connect(self.onAcceptNewProject)
        self.createproject_buttonBox.rejected.connect(self.createproject_Dialog.reject)

        self.brandname_lineEdit.textChanged.connect(
            lambda: checkValidity(self.brandname_lineEdit.text(), self.createproject_buttonBox,
                                  self.brandname_lineEdit))
        self.projectname_lineEdit.textChanged.connect(
            lambda: checkValidity(self.projectname_lineEdit.text(), self.createproject_buttonBox,
                                  self.projectname_lineEdit))
        self.client_lineEdit.textChanged.connect(
            lambda: checkValidity(self.client_lineEdit.text(), self.createproject_buttonBox, self.client_lineEdit))

    def addRemoveUserUI(self):

        admin_pswd = "682"
        passw, ok = QtWidgets.QInputDialog.getText(self, "Password Query", "Enter Admin Password:",
                                                   QtWidgets.QLineEdit.Password)
        if ok:
            if passw == admin_pswd:
                pass
            else:
                self.infoPop(textTitle="Incorrect Password", textHeader="The Password is invalid")
                return
        else:
            return

        users_Dialog = QtWidgets.QDialog(parent=self)
        users_Dialog.setModal(True)
        users_Dialog.setObjectName(("users_Dialog"))
        users_Dialog.resize(380, 483)
        users_Dialog.setMinimumSize(QtCore.QSize(342, 177))
        users_Dialog.setMaximumSize(QtCore.QSize(342, 177))
        users_Dialog.setWindowTitle(("Add/Remove Users"))
        users_Dialog.setFocus()

        addnewuser_groupBox = QtWidgets.QGroupBox(users_Dialog)
        addnewuser_groupBox.setGeometry(QtCore.QRect(10, 10, 321, 91))
        addnewuser_groupBox.setTitle(("Add New User"))
        addnewuser_groupBox.setObjectName(("addnewuser_groupBox"))

        fullname_label = QtWidgets.QLabel(addnewuser_groupBox)
        fullname_label.setGeometry(QtCore.QRect(0, 30, 81, 21))
        fullname_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        fullname_label.setText(("Full Name:"))
        fullname_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        fullname_label.setObjectName(("fullname_label"))

        self.fullname_lineEdit = QtWidgets.QLineEdit(addnewuser_groupBox)
        self.fullname_lineEdit.setGeometry(QtCore.QRect(90, 30, 151, 20))
        self.fullname_lineEdit.setPlaceholderText(("e.g \"John Doe\""))
        self.fullname_lineEdit.setObjectName(("fullname_lineEdit"))

        initials_label = QtWidgets.QLabel(addnewuser_groupBox)
        initials_label.setGeometry(QtCore.QRect(0, 60, 81, 21))
        initials_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        initials_label.setText(("Initials:"))
        initials_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        initials_label.setObjectName(("initials_label"))

        self.initials_lineEdit = QtWidgets.QLineEdit(addnewuser_groupBox)
        self.initials_lineEdit.setGeometry(QtCore.QRect(90, 60, 151, 20))
        self.initials_lineEdit.setText((""))
        self.initials_lineEdit.setPlaceholderText(("e.g \"jd\" (must be unique)"))
        self.initials_lineEdit.setObjectName(("initials_lineEdit"))

        addnewuser_pushButton = QtWidgets.QPushButton(addnewuser_groupBox)
        addnewuser_pushButton.setGeometry(QtCore.QRect(250, 30, 61, 51))
        addnewuser_pushButton.setText(("Add"))
        addnewuser_pushButton.setObjectName(("addnewuser_pushButton"))

        deleteuser_groupBox = QtWidgets.QGroupBox(users_Dialog)
        deleteuser_groupBox.setGeometry(QtCore.QRect(10, 110, 321, 51))
        deleteuser_groupBox.setTitle(("Delete User"))
        deleteuser_groupBox.setObjectName(("deleteuser_groupBox"))

        self.selectuser_comboBox = QtWidgets.QComboBox(deleteuser_groupBox)
        self.selectuser_comboBox.setGeometry(QtCore.QRect(10, 20, 231, 22))
        self.selectuser_comboBox.setObjectName(("selectuser_comboBox"))

        userListSorted = sorted(self.manager.userList.keys())
        for num in range(len(userListSorted)):
            self.selectuser_comboBox.addItem((userListSorted[num]))
            self.selectuser_comboBox.setItemText(num, (userListSorted[num]))

        deleteuser_pushButton = QtWidgets.QPushButton(deleteuser_groupBox)
        deleteuser_pushButton.setGeometry(QtCore.QRect(250, 20, 61, 21))
        deleteuser_pushButton.setText(("Delete"))
        deleteuser_pushButton.setObjectName(("deleteuser_pushButton"))

        addnewuser_pushButton.clicked.connect(self.onAddUser)
        # addnewuser_pushButton.clicked.connect(self.refresh)
        # addnewuser_pushButton.clicked.connect(users_Dialog.close)
        deleteuser_pushButton.clicked.connect(self.onRemoveUser)
        # deleteuser_pushButton.clicked.connect(self.refresh)
        # deleteuser_pushButton.clicked.connect(users_Dialog.close)

        self.fullname_lineEdit.textChanged.connect(
            lambda: checkValidity(self.fullname_lineEdit.text(), addnewuser_pushButton,
                                  self.fullname_lineEdit))
        self.initials_lineEdit.textChanged.connect(
            lambda: checkValidity(self.initials_lineEdit.text(), addnewuser_pushButton,
                                  self.initials_lineEdit))

        users_Dialog.show()

    def setProjectUI(self):

        self.setProject_Dialog = QtWidgets.QDialog(parent=self)
        self.setProject_Dialog.setObjectName(("setProject_Dialog"))
        self.setProject_Dialog.resize(982, 928)
        self.setProject_Dialog.setWindowTitle(("Set Project"))

        gridLayout = QtWidgets.QGridLayout(self.setProject_Dialog)
        gridLayout.setObjectName(("gridLayout"))

        M1_horizontalLayout = QtWidgets.QHBoxLayout()
        M1_horizontalLayout.setObjectName(("M1_horizontalLayout"))

        lookIn_label = QtWidgets.QLabel(self.setProject_Dialog)
        lookIn_label.setText(("Look in:"))
        lookIn_label.setObjectName(("lookIn_label"))

        M1_horizontalLayout.addWidget(lookIn_label)

        self.lookIn_lineEdit = QtWidgets.QLineEdit(self.setProject_Dialog)
        self.lookIn_lineEdit.setText((""))
        self.lookIn_lineEdit.setPlaceholderText((""))
        self.lookIn_lineEdit.setObjectName(("lookIn_lineEdit"))

        M1_horizontalLayout.addWidget(self.lookIn_lineEdit)

        browse_pushButton = QtWidgets.QPushButton(self.setProject_Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(browse_pushButton.sizePolicy().hasHeightForWidth())
        browse_pushButton.setSizePolicy(sizePolicy)
        browse_pushButton.setMaximumSize(QtCore.QSize(50, 16777215))
        browse_pushButton.setText("Browse")
        browse_pushButton.setObjectName(("browse_pushButton"))

        M1_horizontalLayout.addWidget(browse_pushButton)

        back_pushButton = QtWidgets.QPushButton(self.setProject_Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(back_pushButton.sizePolicy().hasHeightForWidth())
        back_pushButton.setSizePolicy(sizePolicy)
        back_pushButton.setMaximumSize(QtCore.QSize(30, 16777215))
        back_pushButton.setText(("<"))
        back_pushButton.setShortcut((""))
        back_pushButton.setObjectName(("back_pushButton"))

        M1_horizontalLayout.addWidget(back_pushButton)

        forward_pushButton = QtWidgets.QPushButton(self.setProject_Dialog)
        forward_pushButton.setMaximumSize(QtCore.QSize(30, 16777215))
        forward_pushButton.setText((">"))
        forward_pushButton.setShortcut((""))
        forward_pushButton.setObjectName(("forward_pushButton"))

        M1_horizontalLayout.addWidget(forward_pushButton)

        up_pushButton = QtWidgets.QPushButton(self.setProject_Dialog)
        up_pushButton.setMaximumSize(QtCore.QSize(30, 16777215))
        up_pushButton.setText(("Up"))
        up_pushButton.setShortcut((""))
        up_pushButton.setObjectName(("up_pushButton"))

        M1_horizontalLayout.addWidget(up_pushButton)

        gridLayout.addLayout(M1_horizontalLayout, 0, 0, 1, 1)

        M2_horizontalLayout = QtWidgets.QHBoxLayout()
        M2_horizontalLayout.setObjectName(("M2_horizontalLayout"))

        M2_splitter = QtWidgets.QSplitter(self.setProject_Dialog)
        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.M2_splitter.sizePolicy().hasHeightForWidth())
        #
        # self.M2_splitter.setSizePolicy(sizePolicy)
        # self.M2_splitter.setFrameShape(QtWidgets.QFrame.NoFrame)
        # self.M2_splitter.setOrientation(QtCore.Qt.Horizontal)
        M2_splitter.setHandleWidth(10)
        M2_splitter.setObjectName(("M2_splitter"))


        # self.folders_tableView = QtWidgets.QTableView(self.M2_splitter)
        self.folders_tableView = QtWidgets.QTreeView(M2_splitter)
        self.folders_tableView.setMinimumSize(QtCore.QSize(0, 0))
        self.folders_tableView.setDragEnabled(True)
        self.folders_tableView.setDragDropMode(QtWidgets.QAbstractItemView.DragOnly)
        self.folders_tableView.setObjectName(("folders_tableView"))

        self.folders_tableView.setFrameShape(QtWidgets.QFrame.NoFrame)
        # self.folders_tableView.setGridStyle(QtCore.Qt.PenStyle.NoPen)
        # self.folders_tableView.setColumnHidden(2, True)
        self.folders_tableView.setItemsExpandable(False)
        self.folders_tableView.setRootIsDecorated(False)
        self.folders_tableView.setSortingEnabled(True)
        self.folders_tableView.sortByColumn(0, QtCore.Qt.SortOrder.AscendingOrder)

        # self.folders_tableView.sortByColumn(0)

        verticalLayoutWidget = QtWidgets.QWidget(M2_splitter)
        verticalLayoutWidget.setObjectName(("verticalLayoutWidget"))

        M2_S2_verticalLayout = QtWidgets.QVBoxLayout(verticalLayoutWidget)
        M2_S2_verticalLayout.setContentsMargins(0, 10, 0, 10)
        M2_S2_verticalLayout.setSpacing(6)
        M2_S2_verticalLayout.setObjectName(("M2_S2_verticalLayout"))

        favorites_label = QtWidgets.QLabel(verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        favorites_label.setFont(font)
        favorites_label.setText(("Favorites"))
        favorites_label.setObjectName(("favorites_label"))

        M2_S2_verticalLayout.addWidget(favorites_label)

        self.favorites_listWidget = DropListWidget(verticalLayoutWidget)
        self.favorites_listWidget.setAlternatingRowColors(True)
        self.favorites_listWidget.setObjectName(("favorites_listWidget"))


        # self.favorites_listWidget.dropped.connect(self.onDragAndDrop)

        M2_S2_verticalLayout.addWidget(self.favorites_listWidget)
        M2_S2_horizontalLayout = QtWidgets.QHBoxLayout()
        M2_S2_horizontalLayout.setObjectName(("M2_S2_horizontalLayout"))

        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        M2_S2_horizontalLayout.addItem(spacerItem)

        remove_pushButton = QtWidgets.QPushButton(verticalLayoutWidget)
        remove_pushButton.setMaximumSize(QtCore.QSize(25, 16777215))
        remove_pushButton.setText(("-"))
        remove_pushButton.setObjectName(("remove_pushButton"))

        M2_S2_horizontalLayout.addWidget(remove_pushButton)

        add_pushButton = QtWidgets.QPushButton(verticalLayoutWidget)
        add_pushButton.setMaximumSize(QtCore.QSize(25, 16777215))
        add_pushButton.setText(("+"))
        add_pushButton.setObjectName(("add_pushButton"))

        M2_S2_horizontalLayout.addWidget(add_pushButton)

        M2_S2_verticalLayout.addLayout(M2_S2_horizontalLayout)

        M2_horizontalLayout.addWidget(M2_splitter)

        gridLayout.addLayout(M2_horizontalLayout, 1, 0, 1, 1)

        M3_horizontalLayout = QtWidgets.QHBoxLayout()

        M3_horizontalLayout.setContentsMargins(0, 20, -1, -1)

        M3_horizontalLayout.setObjectName(("M3_horizontalLayout"))

        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        M3_horizontalLayout.addItem(spacerItem1)

        cancel_pushButton = QtWidgets.QPushButton(self.setProject_Dialog)
        cancel_pushButton.setMaximumSize(QtCore.QSize(70, 16777215))
        cancel_pushButton.setText("Cancel")
        cancel_pushButton.setObjectName(("cancel_pushButton"))

        M3_horizontalLayout.addWidget(cancel_pushButton, QtCore.Qt.AlignRight)

        set_pushButton = QtWidgets.QPushButton(self.setProject_Dialog)
        set_pushButton.setMaximumSize(QtCore.QSize(70, 16777215))
        set_pushButton.setText("Set")
        set_pushButton.setObjectName(("set_pushButton"))

        M3_horizontalLayout.addWidget(set_pushButton, QtCore.Qt.AlignRight)

        gridLayout.addLayout(M3_horizontalLayout, 2, 0, 1, 1)

        verticalLayoutWidget.raise_()

        M2_splitter.setStretchFactor(0,1)

        ## Initial Stuff
        # projectsDir = os.pardir(self.manager.scenePaths["projectPath"])
        self.projectsDir = os.path.abspath(os.path.join(self.manager.scenePaths["projectPath"], os.pardir))
        self.projectsHistory = [self.projectsDir]
        self.projectsDirIndex = 0

        self.setPmodel = QtWidgets.QFileSystemModel()
        self.setPmodel.setRootPath(self.projectsDir)
        self.setPmodel.setFilter(QtCore.QDir.AllDirs | QtCore.QDir.NoDotAndDotDot | QtCore.QDir.Time)


        self.folders_tableView.setModel(self.setPmodel)
        self.folders_tableView.setRootIndex(self.setPmodel.index(self.projectsDir))
        self.folders_tableView.hideColumn(1)
        self.folders_tableView.hideColumn(2)
        self.folders_tableView.setColumnWidth(0,400)

        self.userFavoritesLoad()
        self.favorites_listWidget.addItems([x[0] for x in self.favList])

        self.lookIn_lineEdit.setText(self.projectsDir)



        ## SIGNALS & SLOTS
        self.favorites_listWidget.dropped.connect(lambda path: self.onDragAndDrop(path, mode="favorites"))
        remove_pushButton.clicked.connect(self.onRemoveFavs)
        add_pushButton.clicked.connect(self.onAddFavs)

        self.favorites_listWidget.doubleClicked.connect(self.onSetProject)

        up_pushButton.clicked.connect(lambda: self.onBrowseSetProject("up"))

        self.setProject_Dialog.show()

    def onBrowseSetProject(self, command):
        if command == "init":
            pass
        if command == "up":
            upDir = os.path.abspath(os.path.join(self.projectsDir, os.pardir))
            if not upDir == self.projectsDir:
                self.projectsHistory.append(upDir)
                self.projectsDirIndex = len(self.projectsHistory)-1
            self.folders_tableView.setRootIndex(self.setPmodel.index(self.projectsHistory[self.projectsDirIndex]))
            self.lookIn_lineEdit.setText(self.projectsHistory[self.projectsDirIndex])
            pass
        if command == "back":
            self.folders_tableView.setRootIndex(self.setPmodel.index(self.projectsHistory[self.projectsDirIndex-1]))
            self.lookIn_lineEdit.setText(self.projectsHistory[self.projectsDirIndex-1])
            pass
        if command == "forward":
            self.folders_tableView.setRootIndex(self.setPmodel.index(self.projectsHistory[self.projectsDirIndex+1]))
            self.lookIn_lineEdit.setText(self.projectsHistory[self.projectsDirIndex+1])
            pass
        if command == "browse":
            pass


    def onRemoveFavs(self):
        row = self.favorites_listWidget.currentRow()
        if row == -1:
            return
        # item = self.favList[row]
        self.userFavoritesRemove(row)
        self.favorites_listWidget.takeItem(row)

    def onAddFavs(self):
        index = self.folders_tableView.currentIndex()
        if index.row() == -1: # no row selected, abort
            return
        fullPath = self.setPmodel.filePath(index)
        self.onDragAndDrop(fullPath, "favorites")


    def refresh(self):
        self.manager.__init__()
        # self.__init__()
        # if the project changed:
        if self.projectPath_lineEdit.text() != self.manager.scenePaths["projectPath"]:
            self.projectPath_lineEdit.setText(self.manager.scenePaths["projectPath"])
            self.manager.subProjectList = self.manager.scanSubProjects()
            self.manager.currentSubProjectIndex = 0

        # user DB
        self.userName_comboBox.clear() # clear the combobox items
        userListSorted = sorted(self.manager.userList.keys())
        for num in range(len(userListSorted)):
            self.userName_comboBox.addItem((userListSorted[num]))
            self.userName_comboBox.setItemText(num, (userListSorted[num]))
        self.userPrefLoad()
        self.populateScenes()


    def onAddUser(self):
        ret, msg = self.manager.addUser(self.fullname_lineEdit.text(), self.initials_lineEdit.text())
        if ret == -1:
            self.infoPop(textTitle="Cannot Add User", textHeader=msg)
            return
        self.refresh()
        userListSorted = sorted(self.manager.userList.keys())
        self.selectuser_comboBox.clear()
        for num in range(len(userListSorted)):
            self.selectuser_comboBox.addItem((userListSorted[num]))
            self.selectuser_comboBox.setItemText(num, (userListSorted[num]))
        self.statusBar().showMessage("Status | User Added => %s" % self.fullname_lineEdit.text())
        self.fullname_lineEdit.setText("")
        self.initials_lineEdit.setText("")
        pass

    def onRemoveUser(self):
        self.manager.removeUser(self.selectuser_comboBox.currentText())
        self.refresh()
        userListSorted = sorted(self.manager.userList.keys())
        self.selectuser_comboBox.clear()
        for num in range(len(userListSorted)):
            self.selectuser_comboBox.addItem((userListSorted[num]))
            self.selectuser_comboBox.setItemText(num, (userListSorted[num]))
        pass

    def onAcceptNewProject(self):

        self.resolveProjectPath()

        if self.newProjectPath:
            self.manager.createNewProject(self.newProjectPath)
            self.createproject_Dialog.accept()
            melProofPath = self.newProjectPath.replace("\\", "\\\\")
            evalstr = 'setProject("' + (melProofPath) + '");'  # OK
            mel.eval(evalstr)  # OK

            # mel.eval('setProject \"' + os.path.normpath(self.newProjectPath) + '\"')
            # self.manager.currentProject = pm.workspace(q=1, rd=1)
            self.manager.setProject()
            self.projectPath_lineEdit.setText(self.manager.scenePaths["projectPath"])
            # self.onSubProjectChanged()
            self.manager.subProjectList = self.manager.scanSubProjects()
            self.populateScenes()
            self.statusBar().showMessage("Status | Project Created => %s" %self.newProjectPath)
            return
        else:
            self.infoPop(textTitle="Missing Fields", textHeader="There are missing fields",
                         textInfo="Project Root, Brand Name and Project Names must be filled", type="C")
            return

    def resolveProjectPath(self):
        if self.projectname_lineEdit.text() == "" or self.client_lineEdit.text() == "" or self.projectroot_lineEdit.text() == "":
            self.resolvedpath_label.setText("Fill the mandatory fields")
            self.newProjectPath = None
            return
        projectDate = datetime.datetime.now().strftime("%y%m%d")
        brandname = self.brandname_lineEdit.text()
        projectname = self.projectname_lineEdit.text()
        clientname = self.client_lineEdit.text()
        projectroot = self.projectroot_lineEdit.text()
        if brandname:
            brandname = "%s_" % brandname
        else:
            brandname = ""
        fullName = "{0}{1}_{2}_{3}".format(brandname, projectname, clientname, projectDate)
        self.newProjectPath = os.path.join(projectroot, fullName)
        self.resolvedpath_label.setText(self.newProjectPath)

    def browseProjectRoot(self, updateLine=None):
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.Directory)

        if dlg.exec_():
            selectedroot = os.path.normpath(dlg.selectedFiles()[0])
            self.projectroot_lineEdit.setText(selectedroot)
            self.resolveProjectPath()


    def onCreatePB(self):
        code, msg = self.manager.createPlayblast()
        if code == -1:
            self.infoPop(textHeader="PlayBlast Error", textTitle="Cannot Create Playblast", textInfo=msg)
        else:
            self.statusBar().showMessage("Status | Playblast Created")

    def updateCodecs(self):
        codecs = pm.mel.eval('playblast -format "{0}" -q -compression;'.format(self.fileformat_comboBox.currentText()))
        self.codec_comboBox.clear()
        self.codec_comboBox.addItems(codecs)

    def onPbSettingsAccept(self):
        newPbSettings = {"Resolution": (self.resolutionx_spinBox.value(), self.resolutiony_spinBox.value()),
                         "Format": self.fileformat_comboBox.currentText(),
                         "Codec": self.codec_comboBox.currentText(),
                         "Percent": 100,  ## this one never changes
                         "Quality": self.quality_spinBox.value(),
                         "ShowFrameNumber": self.showframenumber_checkBox.isChecked(),
                         "ShowSceneName": self.showscenename_checkBox.isChecked(),
                         "ShowCategory": self.showcategory_checkBox.isChecked(),
                         "ShowFPS": self.showfps_checkBox.isChecked(),
                         "ShowFrameRange": self.showframerange_checkBox.isChecked(),
                         "PolygonOnly": self.polygononly_checkBox.isChecked(),
                         "ShowGrid": self.showgrid_checkBox.isChecked(),
                         "ClearSelection": self.clearselection_checkBox.isChecked(),
                         "DisplayTextures": self.displaytextures_checkBox.isChecked(),
                         "WireOnShaded": self.wireonshaded_checkBox.isChecked(),
                         "UseDefaultMaterial": self.usedefaultmaterial_checkBox.isChecked()
                         }
        self.manager.setPBsettings(newPbSettings)

    def onImanager(self):
        import imageManager as iman
        if self.scriptJob:
            scriptJob = "%s.imageManagerINS" %(self.scriptJob)
        else:
            scriptJob = None

        self.imageManagerINS = iman.MainUI(scriptJob=scriptJob)

    def onIviewer(self):
        import imageViewer as iview
        iview.MainUI().show()

    def saveBaseSceneDialog(self):
        self.save_Dialog = QtWidgets.QDialog(parent=self)
        self.save_Dialog.setModal(True)
        self.save_Dialog.setObjectName(("save_Dialog"))
        self.save_Dialog.resize(500, 240)
        self.save_Dialog.setMinimumSize(QtCore.QSize(500, 240))
        self.save_Dialog.setMaximumSize(QtCore.QSize(500, 240))
        self.save_Dialog.setWindowTitle(("Save New Base Scene"))
        self.save_Dialog.setToolTip((""))
        self.save_Dialog.setStatusTip((""))
        self.save_Dialog.setWhatsThis((""))
        self.save_Dialog.setAccessibleName((""))
        self.save_Dialog.setAccessibleDescription((""))

        self.sdNotes_label = QtWidgets.QLabel(self.save_Dialog)
        self.sdNotes_label.setGeometry(QtCore.QRect(260, 15, 61, 20))
        self.sdNotes_label.setToolTip((""))
        self.sdNotes_label.setStatusTip((""))
        self.sdNotes_label.setWhatsThis((""))
        self.sdNotes_label.setAccessibleName((""))
        self.sdNotes_label.setAccessibleDescription((""))
        # self.sdNotes_label.setFrameShape(QtWidgets.QFrame.Box)
        self.sdNotes_label.setText(("Notes"))
        self.sdNotes_label.setObjectName(("sdNotes_label"))

        self.sdNotes_textEdit = QtWidgets.QTextEdit(self.save_Dialog)
        self.sdNotes_textEdit.setGeometry(QtCore.QRect(260, 40, 215, 180))
        self.sdNotes_textEdit.setToolTip((""))
        self.sdNotes_textEdit.setStatusTip((""))
        self.sdNotes_textEdit.setWhatsThis((""))
        self.sdNotes_textEdit.setAccessibleName((""))
        self.sdNotes_textEdit.setAccessibleDescription((""))
        self.sdNotes_textEdit.setObjectName(("sdNotes_textEdit"))

        self.sdSubP_label = QtWidgets.QLabel(self.save_Dialog)
        self.sdSubP_label.setGeometry(QtCore.QRect(20, 30, 61, 20))
        self.sdSubP_label.setToolTip((""))
        self.sdSubP_label.setStatusTip((""))
        self.sdSubP_label.setWhatsThis((""))
        self.sdSubP_label.setAccessibleName((""))
        self.sdSubP_label.setAccessibleDescription((""))
        self.sdSubP_label.setFrameShape(QtWidgets.QFrame.Box)
        self.sdSubP_label.setText(("Sub-Project"))
        self.sdSubP_label.setObjectName(("sdSubP_label"))

        self.sdSubP_comboBox = QtWidgets.QComboBox(self.save_Dialog)
        self.sdSubP_comboBox.setFocus()
        self.sdSubP_comboBox.setGeometry(QtCore.QRect(90, 30, 151, 22))
        self.sdSubP_comboBox.setToolTip((""))
        self.sdSubP_comboBox.setStatusTip((""))
        self.sdSubP_comboBox.setWhatsThis((""))
        self.sdSubP_comboBox.setAccessibleName((""))
        self.sdSubP_comboBox.setAccessibleDescription((""))
        self.sdSubP_comboBox.setObjectName(("sdCategory_comboBox"))
        self.sdSubP_comboBox.addItems((self.manager.subProjectList))
        self.sdSubP_comboBox.setCurrentIndex(self.subProject_comboBox.currentIndex())

        self.sdName_label = QtWidgets.QLabel(self.save_Dialog)
        self.sdName_label.setGeometry(QtCore.QRect(20, 70, 61, 20))
        self.sdName_label.setToolTip((""))
        self.sdName_label.setStatusTip((""))
        self.sdName_label.setWhatsThis((""))
        self.sdName_label.setAccessibleName((""))
        self.sdName_label.setAccessibleDescription((""))
        self.sdName_label.setFrameShape(QtWidgets.QFrame.Box)
        self.sdName_label.setText(("Name"))
        self.sdName_label.setObjectName(("sdName_label"))

        self.sdName_lineEdit = QtWidgets.QLineEdit(self.save_Dialog)
        self.sdName_lineEdit.setGeometry(QtCore.QRect(90, 70, 151, 20))
        self.sdName_lineEdit.setToolTip((""))
        self.sdName_lineEdit.setStatusTip((""))
        self.sdName_lineEdit.setWhatsThis((""))
        self.sdName_lineEdit.setAccessibleName((""))
        self.sdName_lineEdit.setAccessibleDescription((""))
        self.sdName_lineEdit.setText((""))
        self.sdName_lineEdit.setCursorPosition(0)
        self.sdName_lineEdit.setPlaceholderText(("Choose an unique name"))
        self.sdName_lineEdit.setObjectName(("sdName_lineEdit"))

        self.sdCategory_label = QtWidgets.QLabel(self.save_Dialog)
        self.sdCategory_label.setGeometry(QtCore.QRect(20, 110, 61, 20))
        self.sdCategory_label.setToolTip((""))
        self.sdCategory_label.setStatusTip((""))
        self.sdCategory_label.setWhatsThis((""))
        self.sdCategory_label.setAccessibleName((""))
        self.sdCategory_label.setAccessibleDescription((""))
        self.sdCategory_label.setFrameShape(QtWidgets.QFrame.Box)
        self.sdCategory_label.setText(("Category"))
        self.sdCategory_label.setObjectName(("sdCategory_label"))

        self.sdCategory_comboBox = QtWidgets.QComboBox(self.save_Dialog)
        self.sdCategory_comboBox.setFocus()
        self.sdCategory_comboBox.setGeometry(QtCore.QRect(90, 110, 151, 22))
        self.sdCategory_comboBox.setToolTip((""))
        self.sdCategory_comboBox.setStatusTip((""))
        self.sdCategory_comboBox.setWhatsThis((""))
        self.sdCategory_comboBox.setAccessibleName((""))
        self.sdCategory_comboBox.setAccessibleDescription((""))
        self.sdCategory_comboBox.setObjectName(("sdCategory_comboBox"))
        for i in range(len(self.manager.validCategories)):
            self.sdCategory_comboBox.addItem((self.manager.validCategories[i]))
            self.sdCategory_comboBox.setItemText(i, (self.manager.validCategories[i]))
        self.sdCategory_comboBox.setCurrentIndex(self.category_tabWidget.currentIndex())

        self.sdMakeReference_checkbox = QtWidgets.QCheckBox("Make it Reference", self.save_Dialog)
        self.sdMakeReference_checkbox.setGeometry(QtCore.QRect(130, 150, 151, 22))

        self.sd_buttonBox = QtWidgets.QDialogButtonBox(self.save_Dialog)
        self.sd_buttonBox.setGeometry(QtCore.QRect(20, 190, 220, 32))
        self.sd_buttonBox.setToolTip((""))
        self.sd_buttonBox.setStatusTip((""))
        self.sd_buttonBox.setWhatsThis((""))
        self.sd_buttonBox.setAccessibleName((""))
        self.sd_buttonBox.setAccessibleDescription((""))
        self.sd_buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.sd_buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.sd_buttonBox.setObjectName(("sd_buttonBox"))

        self.sdName_lineEdit.textChanged.connect(
            lambda: checkValidity(self.sdName_lineEdit.text(), self.sd_buttonBox, self.sdName_lineEdit))

        self.sd_buttonBox.accepted.connect(self.onSaveBaseScene)
        self.sd_buttonBox.accepted.connect(self.save_Dialog.accept)
        self.sd_buttonBox.rejected.connect(self.save_Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(self.save_Dialog)

        self.save_Dialog.show()

    def saveAsVersionDialog(self):
        saveV_Dialog = QtWidgets.QDialog(parent=self)
        saveV_Dialog.setModal(True)
        saveV_Dialog.setObjectName(("saveV_Dialog"))
        saveV_Dialog.resize(255, 290)
        saveV_Dialog.setMinimumSize(QtCore.QSize(255, 290))
        saveV_Dialog.setMaximumSize(QtCore.QSize(255, 290))
        saveV_Dialog.setWindowTitle(("Save As Version"))
        saveV_Dialog.setToolTip((""))
        saveV_Dialog.setStatusTip((""))
        saveV_Dialog.setWhatsThis((""))
        saveV_Dialog.setAccessibleName((""))
        saveV_Dialog.setAccessibleDescription((""))

        svNotes_label = QtWidgets.QLabel(saveV_Dialog)
        svNotes_label.setGeometry(QtCore.QRect(15, 15, 61, 20))
        svNotes_label.setToolTip((""))
        svNotes_label.setStatusTip((""))
        svNotes_label.setWhatsThis((""))
        svNotes_label.setAccessibleName((""))
        svNotes_label.setAccessibleDescription((""))
        svNotes_label.setText(("Version Notes"))
        svNotes_label.setObjectName(("sdNotes_label"))

        self.svNotes_textEdit = QtWidgets.QTextEdit(saveV_Dialog)
        self.svNotes_textEdit.setGeometry(QtCore.QRect(15, 40, 215, 170))
        self.svNotes_textEdit.setToolTip((""))
        self.svNotes_textEdit.setStatusTip((""))
        self.svNotes_textEdit.setWhatsThis((""))
        self.svNotes_textEdit.setAccessibleName((""))
        self.svNotes_textEdit.setAccessibleDescription((""))
        self.svNotes_textEdit.setObjectName(("sdNotes_textEdit"))

        self.svMakeReference_checkbox = QtWidgets.QCheckBox("Make it Reference", saveV_Dialog)
        self.svMakeReference_checkbox.setGeometry(QtCore.QRect(130, 215, 151, 22))
        self.svMakeReference_checkbox.setChecked(False)

        sv_buttonBox = QtWidgets.QDialogButtonBox(saveV_Dialog)
        sv_buttonBox.setGeometry(QtCore.QRect(20, 250, 220, 32))
        sv_buttonBox.setToolTip((""))
        sv_buttonBox.setStatusTip((""))
        sv_buttonBox.setWhatsThis((""))
        sv_buttonBox.setAccessibleName((""))
        sv_buttonBox.setAccessibleDescription((""))
        sv_buttonBox.setOrientation(QtCore.Qt.Horizontal)
        sv_buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel)

        buttonS = sv_buttonBox.button(QtWidgets.QDialogButtonBox.Save)
        buttonS.setText('Save As Version')
        buttonC = sv_buttonBox.button(QtWidgets.QDialogButtonBox.Cancel)
        buttonC.setText('Cancel')

        sv_buttonBox.setObjectName(("sd_buttonBox"))
        sv_buttonBox.accepted.connect(self.onSaveAsVersion)
        sv_buttonBox.accepted.connect(saveV_Dialog.accept)
        sv_buttonBox.rejected.connect(saveV_Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(saveV_Dialog)

        sceneInfo = self.manager.getSceneInfo()
        if sceneInfo:
            saveV_Dialog.show()
        else:
            self.infoPop(textInfo="Save Version FAILED",
                         textHeader="Current Scene is not a Base Scene. No Version saved", textTitle="ERROR: SAVE VERSION", type="C")

    def onSaveBaseScene(self):
        userInitials = self.manager.userList[self.userName_comboBox.currentText()]
        subProject = self.sdSubP_comboBox.currentIndex()

        name = nameCheck(self.sdName_lineEdit.text())
        if name == -1:
            self.infoPop(textHeader="Invalid characters. Use <A-Z> and <0-9>", textInfo="",
                         textTitle="ERROR: ASCII Error", type="C")
            return

        sceneFile = self.manager.saveBaseScene(self.sdCategory_comboBox.currentText(), userInitials, name,
                                               subProject=subProject,
                                               makeReference=self.sdMakeReference_checkbox.checkState(),
                                               versionNotes=self.sdNotes_textEdit.toPlainText())

        if not sceneFile == -1:
            self.populateScenes()
            self.statusBar().showMessage("Status | Base Scene Created => %s" % sceneFile)

        else:
            self.infoPop(textInfo="Save Version FAILED",
                         textHeader="Current Scene is not a Base Scene. No Version saved", textTitle="ERROR: SAVE VERSION", type="C")



    def onSaveAsVersion(self):
        userInitials = self.manager.userList[self.userName_comboBox.currentText()]
        sceneFile = self.manager.saveVersion(userInitials, makeReference=self.svMakeReference_checkbox.checkState(),
                                             versionNotes=self.svNotes_textEdit.toPlainText())
        self.populateScenes()
        if not sceneFile == -1:
            self.statusBar().showMessage("Status | Version Saved => %s" % sceneFile)

        else:
            self.infoPop(textHeader="Save Version FAILED",
                         textInfo="Cannot Find The Database. The File is not saved as a Base Scene, or database file is missing".format(
                             sceneFile), textTitle="ERROR: Saving New Version", type="C")

    def onloadScene(self):

        row = self.scenes_listWidget.currentRow()
        if row == -1:
            pm.warning("no scene selected")
            return

        sceneName = "%s.json" % self.scenes_listWidget.currentItem().text()
        # takethefirstjson as example for rootpath

        sceneJson = os.path.join(pathOps(self.scenesInCategory[0], "path"), sceneName)
        try:
            sceneInfo = loadJson(sceneJson)
        except:
            self.infoPop(textTitle="Error Finding Database", textInfo="Database file => {0} does not exist".format(sceneJson), type="C")
            return

        res, msg = compareVersions(sceneInfo["MayaVersion"])
        if res == -1:
            mismatch = self.queryPop(type="yesNo", textTitle="Version Mismatch", textHeader=msg)
            if mismatch == "no":
                return

        # sceneJson = self.scenesInCategory[row]

        if self.loadMode_radioButton.isChecked():
            fileCheckState = cmds.file(q=True, modified=True)
            ## Eger dosya save edilmemisse:
            if fileCheckState:
                q = self.queryPop(type="yesNoCancel", textTitle="Save Changes", textInfo="Save Changes to", textHeader=(pm.sceneName()))
                if q == "yes":
                    pm.saveFile()
                    self.manager.loadScene(sceneJson, version=self.version_comboBox.currentIndex(), force=True)
                if q == "no":
                    self.manager.loadScene(sceneJson, version=self.version_comboBox.currentIndex(), force=True)
                if q == "cancel":
                    pass

            ## Dosya saveli ise devam
            else:
                self.manager.loadScene(sceneJson, version=self.version_comboBox.currentIndex(), force=True)
            self.populateScenes()
            self.statusBar().showMessage("Status | Scene Loaded => %s" % sceneName)

        if self.referenceMode_radioButton.isChecked():
            self.manager.loadReference(sceneJson)
            self.populateScenes()
            self.statusBar().showMessage("Status | Scene Referenced => %s" % sceneName)

    def onShowPBclicked(self):
        row = self.scenes_listWidget.currentRow()
        if row == -1:
            pm.warning("no scene selected")
            return

        sceneName = "%s.json" % self.scenes_listWidget.currentItem().text()
        # takethefirstjson as example for rootpath
        sceneJson = os.path.join(pathOps(self.scenesInCategory[0], "path"), sceneName)
        version = self.version_comboBox.currentIndex()
        notes, pbDict = self.manager.getVersionNotes(sceneJson, version=version)
        if len(pbDict.keys()) == 1:
            path = pbDict[pbDict.keys()[0]]
            self.manager.playPlayblast(path)
        else:
            zortMenu = QtWidgets.QMenu()

            for z in pbDict.keys():
                tempAction = QtWidgets.QAction(z, self)
                zortMenu.addAction(tempAction)
                tempAction.triggered.connect(lambda item=pbDict[z]: self.onPlayPb(
                    item))  ## Take note about the usage of lambda "item=pbDict[z]" makes it possible using the loop

            zortMenu.exec_((QtGui.QCursor.pos()))

    def onPlayPb(self, item):
        code= self.manager.playPlayblast(item)

        if code:
            state = self.queryPop("yesNo", textTitle=code[1][0], textHeader=code[1][1], textInfo=code[1][2])
            if state == "yes":
                sceneName = "%s.json" % self.scenes_listWidget.currentItem().text()
                sceneJson = os.path.join(pathOps(self.scenesInCategory[0], "path"), sceneName)
                version = self.version_comboBox.currentIndex()
                self.manager.removePlayblast(item, sceneJson, version)


    def onAddNotes(self):

        row = self.scenes_listWidget.currentRow()
        if row == -1:
            return

        sceneName = "%s.json" % self.scenes_listWidget.currentItem().text()
        # takethefirstjson as example for rootpath
        sceneJson = os.path.join(pathOps(self.scenesInCategory[0], "path"), sceneName)
        version = self.version_comboBox.currentIndex()
        userName = self.userName_comboBox.currentText()

        addNotes_Dialog = QtWidgets.QDialog(parent=self)
        addNotes_Dialog.setModal(True)
        addNotes_Dialog.setObjectName(("addNotes_Dialog"))
        addNotes_Dialog.resize(255, 290)
        addNotes_Dialog.setMinimumSize(QtCore.QSize(255, 290))
        addNotes_Dialog.setMaximumSize(QtCore.QSize(255, 290))
        addNotes_Dialog.setWindowTitle(("Add Notes"))
        addNotes_Dialog.setToolTip((""))
        addNotes_Dialog.setStatusTip((""))
        addNotes_Dialog.setWhatsThis((""))
        addNotes_Dialog.setAccessibleName((""))
        addNotes_Dialog.setAccessibleDescription((""))

        addNotes_label = QtWidgets.QLabel(addNotes_Dialog)
        addNotes_label.setGeometry(QtCore.QRect(15, 15, 100, 20))
        addNotes_label.setToolTip((""))
        addNotes_label.setStatusTip((""))
        addNotes_label.setWhatsThis((""))
        addNotes_label.setAccessibleName((""))
        addNotes_label.setAccessibleDescription((""))
        addNotes_label.setText(("Additional Notes"))
        addNotes_label.setObjectName(("addNotes_label"))

        addNotes_textEdit = QtWidgets.QTextEdit(addNotes_Dialog)
        addNotes_textEdit.setGeometry(QtCore.QRect(15, 40, 215, 170))
        addNotes_textEdit.setToolTip((""))
        addNotes_textEdit.setStatusTip((""))
        addNotes_textEdit.setWhatsThis((""))
        addNotes_textEdit.setAccessibleName((""))
        addNotes_textEdit.setAccessibleDescription((""))
        addNotes_textEdit.setObjectName(("addNotes_textEdit"))

        addNotes_buttonBox = QtWidgets.QDialogButtonBox(addNotes_Dialog)
        addNotes_buttonBox.setGeometry(QtCore.QRect(20, 250, 220, 32))
        addNotes_buttonBox.setToolTip((""))
        addNotes_buttonBox.setStatusTip((""))
        addNotes_buttonBox.setWhatsThis((""))
        addNotes_buttonBox.setAccessibleName((""))
        addNotes_buttonBox.setAccessibleDescription((""))
        addNotes_buttonBox.setOrientation(QtCore.Qt.Horizontal)
        addNotes_buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel)

        buttonS = addNotes_buttonBox.button(QtWidgets.QDialogButtonBox.Save)
        buttonS.setText('Add Notes')
        buttonC = addNotes_buttonBox.button(QtWidgets.QDialogButtonBox.Cancel)
        buttonC.setText('Cancel')

        addNotes_buttonBox.setObjectName(("addNotes_buttonBox"))
        addNotes_buttonBox.accepted.connect(
            lambda: self.manager.addVersionNotes(addNotes_textEdit.toPlainText(), sceneJson, version, userName))
        addNotes_buttonBox.accepted.connect(self.populateScenes)
        addNotes_buttonBox.accepted.connect(addNotes_Dialog.accept)

        addNotes_buttonBox.rejected.connect(addNotes_Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(addNotes_Dialog)

        addNotes_Dialog.show()

    def onRadioButtonsToggled(self):
        state = self.loadMode_radioButton.isChecked()
        self.version_label.setEnabled(state)
        self.makeReference_pushButton.setEnabled(state)
        self.notes_label.setEnabled(state)
        self.notes_textEdit.setEnabled(state)
        self.showPB_pushButton.setEnabled(state)
        if state:
            self.load_pushButton.setText("Load Scene")
            self.scenes_listWidget.setStyleSheet("border-style: solid; border-width: 2px; border-color: grey;")
        else:
            self.load_pushButton.setText("Reference Scene")
            self.scenes_listWidget.setStyleSheet("border-style: solid; border-width: 2px; border-color: cyan;")
        self.populateScenes()

    def userPrefSave(self):
        # pass

        homedir = os.path.expanduser("~")
        settingsFilePath = os.path.join(homedir, "smSettings.json")

        settingsData = {"currentTabIndex": self.category_tabWidget.currentIndex(),
                        "currentSubIndex": self.subProject_comboBox.currentIndex(),
                        #"currentUserIndex": self.userName_comboBox.currentIndex(),
                        "currentUser": self.userName_comboBox.currentText(),
                        "currentMode": self.referenceMode_radioButton.isChecked()}
        dumpJson(settingsData, settingsFilePath)

    def userPrefLoad(self):
        # pass
        homedir = os.path.expanduser("~")
        settingsFilePath = os.path.join(homedir, "smSettings.json")
        if os.path.isfile(settingsFilePath):
            settingsData = loadJson(settingsFilePath)
        else:
            # return defaults
            # settingsData = {"currentTabIndex": 0, "currentSubIndex": 0, "currentUserIndex": 0, "currentMode": 0}
            settingsData = {"currentTabIndex": 0, "currentSubIndex": 0, "currentUser": "", "currentMode": 0}
            dumpJson(settingsData, settingsFilePath)

        self.referenceMode_radioButton.setChecked(settingsData["currentMode"])
        self.loadMode_radioButton.setChecked(not settingsData["currentMode"])

        # if settingsData["currentUserIndex"] <= (len(self.manager.userList)):
        #     currentUserIndex = settingsData["currentUserIndex"]
        # else:
        #     currentUserIndex = 0
        if not settingsData["currentUser"] in (self.manager.userList.keys()):
            currentUser = self.manager.userList[self.manager.userList.keys()[0]]
        else:
            currentUser = settingsData["currentUser"]
        # self.manager.currentUserIndex=currentUserIndex
        userNameindex = self.userName_comboBox.findText(currentUser, QtCore.Qt.MatchFixedString)
        if userNameindex >= 0:
            self.userName_comboBox.setCurrentIndex(userNameindex)
        else:
            self.userName_comboBox.setCurrentIndex(0)

        if settingsData["currentSubIndex"] < (len(self.manager.subProjectList)):
            currentSubIndex = settingsData["currentSubIndex"]
        else:
            currentSubIndex = 0

        self.manager.currentSubProjectIndex = currentSubIndex
        self.subProject_comboBox.setCurrentIndex(currentSubIndex)

        self.category_tabWidget.setCurrentIndex(settingsData["currentTabIndex"])

    def userFavoritesLoad(self):
        homedir = os.path.expanduser("~")
        bookmarksFilePath = os.path.join(homedir, "smBookmarks.json")
        if os.path.isfile(bookmarksFilePath):
            bookmarksData = loadJson(bookmarksFilePath)
        else:
            bookmarksData = []
            dumpJson(bookmarksData, bookmarksFilePath)
        self.favList = bookmarksData
        return bookmarksData, bookmarksFilePath

    def userFavoritesAdd(self, shortName, path):
        data, filePath = self.userFavoritesLoad()
        data.append([shortName, path])
        self.favList = data
        dumpJson(data, filePath)

    def userFavoritesRemove(self, index):
        data, filePath = self.userFavoritesLoad()
        # data.remove([shortName, path])
        del data[index]
        self.favList = data
        dumpJson(data, filePath)

    def rcAction(self, command):
        if command == "importScene":
            row = self.scenes_listWidget.currentRow()
            if not row == -1:
                sceneName = "%s.json" % self.scenes_listWidget.currentItem().text()
                # takethefirstjson as example for rootpath
                jsonPath = os.path.join(pathOps(self.scenesInCategory[0], "path"), sceneName)
                self.manager.loadScene(jsonPath, version=self.version_comboBox.currentIndex(), importFile=True)

        if command == "showInExplorerMaya":
            row = self.scenes_listWidget.currentRow()
            if not row == -1:
                sceneName = "%s.json" % self.scenes_listWidget.currentItem().text()
                # takethefirstjson as example for rootpath
                jPath = os.path.join(pathOps(self.scenesInCategory[0], "path"), sceneName)

                sceneData = loadJson(jPath)

                path = os.path.join(os.path.normpath(self.manager.scenePaths["projectPath"]), os.path.normpath(sceneData["Path"]))

                if self.manager.currentPlatform == "Windows":
                    os.startfile(path)
                if self.manager.currentPlatform == "Linux":
                    os.system('nautilus %s' % path)

        if command == "showInExplorerPB":
            row = self.scenes_listWidget.currentRow()
            if not row == -1:
                sceneName = "%s.json" % self.scenes_listWidget.currentItem().text()
                # takethefirstjson as example for rootpath
                jPath = os.path.join(pathOps(self.scenesInCategory[0], "path"), sceneName)

                # sceneData = loadJson(os.path.join(jPath, sceneName))
                sceneData = loadJson(jPath)

                path = os.path.join(os.path.normpath(self.manager.scenePaths["projectPath"]), os.path.normpath(sceneData["Path"]))
                path = path.replace("scenes", "Playblasts")
                if os.path.isdir(path):
                    if self.manager.currentPlatform == "Windows":
                        os.startfile(path)
                    if self.manager.currentPlatform == "Linux":
                        os.system('nautilus %s' % path)
                else:
                    self.infoPop(textTitle="", textHeader="Scene does not have a playblast",
                                 textInfo="There is no playblast folder created for this scene yet")

        if command == "showInExplorerData":
            row = self.scenes_listWidget.currentRow()
            if not row == -1:
                try:
                    path = pathOps(self.scenesInCategory[row], "path")
                except:
                    path = pathOps(self.scenesInCategory[0], "path")
                if self.manager.currentPlatform == "Windows":
                    os.startfile(path)
                if self.manager.currentPlatform == "Linux":
                    os.system('nautilus %s' % path)

    def onContextMenu_scenes(self, point):
        # show context menu
        self.popMenu.exec_(self.scenes_listWidget.mapToGlobal(point))
    def onContextMenu_thumbnail(self, point):
        # show context menu
        self.popMenu_thumbnail.exec_(self.thumbnail_label.mapToGlobal(point))

    def onSubProjectChanged(self):
        self.manager.currentSubProjectIndex = self.subProject_comboBox.currentIndex()
        self.populateScenes()

    def onReferenceCheck(self, deepCheck=False):
        codeDict = {-1: QtGui.QColor(255, 0, 0, 255), 1: QtGui.QColor(0, 255, 0, 255), 0: QtGui.QColor(255, 255, 0, 255)} # dictionary for color codes red, green, yellow
        for path in self.scenesInCategory:
            code = self.manager.checkReference(path, deepCheck=deepCheck)
            color = codeDict[code]
            index = self.scenesInCategory.index(path)
            if self.scenes_listWidget.item(index):
                self.scenes_listWidget.item(index).setForeground(color)
        self.statusBar().showMessage("References Checked")


    def onSetProject(self):
        # mel.eval("SetProject;")
        # self.manager.currentProject = pm.workspace(q=1, rd=1)
        self.manager.setProject()
        self.projectPath_lineEdit.setText(self.manager.scenePaths["projectPath"])
        # self.onSubProjectChanged()
        self.manager.subProjectList = self.manager.scanSubProjects()
        self.manager.currentSubProjectIndex = 0
        self.populateScenes()

    def sceneInfo(self):
        self.version_comboBox.clear()
        row = self.scenes_listWidget.currentRow()
        if row == -1:
            return
        sceneName = "%s.json" % self.scenes_listWidget.currentItem().text()
        # takethefirstjson as example for rootpath
        jPath = pathOps(self.scenesInCategory[0], "path")
        sceneData = loadJson(os.path.join(jPath, sceneName))

        for num in range(len(sceneData["Versions"])):
            self.version_comboBox.addItem("v{0}".format(str(num + 1).zfill(3)))
        if sceneData["ReferencedVersion"]:
            currentIndex = sceneData["ReferencedVersion"] - 1
        else:
            currentIndex = len(sceneData["Versions"]) - 1

        self.version_comboBox.setCurrentIndex(currentIndex)
        if currentIndex != len(sceneData["Versions"]) - 1:  # if current index is not the last saved scene
            self.version_comboBox.setStyleSheet("background-color: rgb(80,80,80); color: yellow")
        else:
            self.version_comboBox.setStyleSheet("background-color: rgb(80,80,80); color: white")
        self.refreshNotes()
        self.refreshThumbnail()
        self.statusBar().showMessage("Status | Idle")

    def refreshNotes(self):
        row = self.scenes_listWidget.currentRow()

        if not row == -1:
            sceneName = "%s.json" % self.scenes_listWidget.currentItem().text()
            sceneJson = os.path.join(pathOps(self.scenesInCategory[0], "path"), sceneName)
            version = self.version_comboBox.currentIndex()

            notes, pbDict = self.manager.getVersionNotes(sceneJson, version)

            self.notes_textEdit.setPlainText(notes)
            if pbDict.keys():
                self.showPB_pushButton.setEnabled(True)
            else:
                self.showPB_pushButton.setEnabled(False)
            self.addNotes_pushButton.setEnabled(True)
            self.makeReference_pushButton.setEnabled(True)
        else:

            self.showPB_pushButton.setEnabled(False)
            self.addNotes_pushButton.setEnabled(False)
            self.makeReference_pushButton.setEnabled(False)

    def refreshThumbnail(self):
        row = self.scenes_listWidget.currentRow()

        if not row == -1:
            sceneName = "%s.json" % self.scenes_listWidget.currentItem().text()
            # takethefirstjson as example for rootpath
            sceneJson = os.path.join(pathOps(self.scenesInCategory[0], "path"), sceneName)
            version = self.version_comboBox.currentIndex()

            jsonInfo = loadJson(sceneJson)
            try:
                thumb = os.path.join(self.manager.scenePaths["projectPath"], jsonInfo["Versions"][version][5])
                # print "thumb", thumb
                if os.path.isfile(thumb):
                    self.tPixmap = QtGui.QPixmap((thumb))
                    self.thumbnail_label.setPixmap(self.tPixmap.scaledToHeight(124))
                else: # if the path is in db but file is deleted
                    self.thumbnail_label.setText("No Thumbnail")
            except IndexError: # for backward compatibilty
                self.thumbnail_label.setText("No Thumbnail")
        else:
            self.tPixmap = QtGui.QPixmap((""))
            self.thumbnail_label.setPixmap(self.tPixmap)
            self.thumbnail_label.setText("")

    def onChangeThumbnail(self, mode):

        row = self.scenes_listWidget.currentRow()
        if not row == -1:
            sceneName = "%s.json" % self.scenes_listWidget.currentItem().text()
            jPath = pathOps(self.scenesInCategory[0], "path")
            jsonPath = os.path.join(jPath, sceneName)
            version = self.version_comboBox.currentIndex()
        else:
            return
        if mode == "file":
            fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', self.manager.scenePaths["projectPath"],"Image files (*.jpg *.gif)")[0]
            if not fname: # if dialog is canceled
                return

        elif mode == "currentView":
            fname = ""

        self.manager.replaceThumbnail(mode=mode, jsonPath=jsonPath, version=version, filePath=fname)
        self.statusBar().showMessage("Status | Thumbnail changed")

        self.refreshThumbnail()




    def onSceneInfo(self):
        row = self.scenes_listWidget.currentRow()
        if not row == -1:
            sceneName = "%s.json" % self.scenes_listWidget.currentItem().text()
            # takethefirstjson as example for rootpath
            jPath = os.path.join(pathOps(self.scenesInCategory[0], "path"), sceneName)
            sceneData = loadJson(jPath)
            textInfo = pprint.pformat(sceneData)

            self.messageDialog = QtWidgets.QDialog()
            self.messageDialog.setWindowTitle("Scene Info")

            self.messageDialog.resize(800, 700)
            self.messageDialog.show()
            messageLayout = QtWidgets.QVBoxLayout(self.messageDialog)
            messageLayout.setContentsMargins(0, 0, 0, 0)
            helpText = QtWidgets.QTextEdit()
            helpText.setReadOnly(True)

            helpText.setStyleSheet("background-color: rgb(255, 255, 255);")
            helpText.setStyleSheet(""
                                   "border: 20px solid black;"
                                   "background-color: black;"
                                   "font-size: 16px"
                                   "")
            helpText.setText(textInfo)
            # testLabel = QtWidgets.QLabel("TESTING")
            # helpText.textCursor().insertHtml("""
            # <h1><span style="color: #ff6600;">Creating Initial Spine Joints</span></h1>
            # <p><span style="font-weight: 400;">This section is for creating or defining </span><em><span style="font-weight: 400;">Spine Initialization Joints.</span></em></p>
            # <p><span style="font-weight: 400;">These joints will inform the rigging module about the locations of spine joints and pass various options through extra attributes.</span></p>
            # <h3><strong><span style="color: #ff6600;">How To use?</span></strong></h3>
            # <p><span style="font-weight: 400;">Pressing the <em>Create</em>&nbsp;button will create number of joints defined by the </span><span style="font-weight: 400; color: #800080;"><strong>Segments</strong> </span><span style="font-weight: 400;">value.</span></p>
            # <p><span style="font-weight: 400;">Pressing the CTRL will change the mode to define mode which allows defining pre-existing joints as spine.</span></p>
            # <p><span style="font-weight: 400;">To define existing joints, first select all the joints that you wish to define with the correct order (starting from the root of spine), then CTRL+click <em>Create</em>&nbsp;button.</span></p>
            # <p><strong><span style="color: #800080;">Segments</span></strong><span style="font-weight: 400;"> value is </span><strong>not </strong><span style="font-weight: 400;">the final resolution of the spine rig. <strong><span style="color: #800080;">Segments</span> </strong>are used to tell the rig module, where and how many controllers will be on the spine rig.</span></p>
            # <h3><span style="color: #ff6600;">What next?</span></h3>
            # <p><span style="font-weight: 400;">After creating (or defining) the initial spine joints, various options can be reached through the Spine Root. These options are stored in extra attributes. During the rigging process, these options will be derived by the rigging module.</span></p>
            # <p><span style="font-weight: 400;">These extra attributes are:</span></p>
            # <p><span style="font-weight: 400;"><span style="color: #3366ff;"><strong>Resolution:</strong></span>&nbsp;</span><span style="font-weight: 400;">This is the actual final joint resolution for the spine deformation joints.</span></p>
            # <p><span style="font-weight: 400;"><span style="color: #3366ff;"><strong>DropOff:</strong></span>&nbsp;</span><span style="font-weight: 400;">This value will change the way the controllers are affecting the spline IK chain. Usually the default value is ok. If the rig have too many segments (This means more controllers will be created) then tweaking this value may be necessary.</span></p>
            #
            #         """)
            messageLayout.addWidget(helpText)

        pass

    def populateScenes(self):
        row = self.scenes_listWidget.currentRow()
        self.scenes_listWidget.clear()
        self.version_comboBox.clear()
        self.notes_textEdit.clear()
        self.subProject_comboBox.clear()

        self.scenesInCategory, subProjectFile = self.manager.scanScenes(
            self.category_tabWidget.currentWidget().objectName())

        if self.referenceMode_radioButton.isChecked():
            for i in self.scenesInCategory:
                jsonFile = loadJson(i)
                if jsonFile["ReferenceFile"]:
                    self.scenes_listWidget.addItem(pathOps(i, "filename"))
            self.version_comboBox.setEnabled(False)


        else:
            # self.scenes_listWidget.addItems(self.scenesInCategory)
            for i in self.scenesInCategory:
                self.scenes_listWidget.addItem(pathOps(i, "filename"))
            self.onReferenceCheck()
            self.version_comboBox.setEnabled(True)

        self.subProject_comboBox.addItems((self.manager.subProjectList))

        self.subProject_comboBox.setCurrentIndex(self.manager.currentSubProjectIndex)

        sceneInfo = self.manager.getSceneInfo()
        if sceneInfo: ## getSceneInfo returns None if there is no json database fil
            self.baseScene_lineEdit.setText("%s ==> %s ==> %s" % (sceneInfo["subProject"], sceneInfo["category"], sceneInfo["shotName"]))
            self.baseScene_lineEdit.setStyleSheet("background-color: rgb(40,40,40); color: cyan")
        else:
            self.baseScene_lineEdit.setText("Current Scene is not a Base Scene")
            self.baseScene_lineEdit.setStyleSheet("background-color: rgb(40,40,40); color: yellow")

        self.scenes_listWidget.setCurrentRow(row)
        self.refreshNotes()
        self.refreshThumbnail()
        self.userPrefSave()

        # self.referenceCheck()

    def onMakeReference(self):
        row = self.scenes_listWidget.currentRow()
        if not row == -1:
            sceneName = "%s.json" % self.scenes_listWidget.currentItem().text()
            # takethefirstjson as example for rootpath
            jPath = pathOps(self.scenesInCategory[0], "path")

            jsonFile = os.path.join(jPath, sceneName)

            # jsonFile = self.scenesInCategory[row]
            version = self.version_comboBox.currentIndex()
            self.manager.makeReference(jsonFile, version + 1)
            # self.sceneInfo()

            self.populateScenes()
            self.statusBar().showMessage(
                "Status | Version {1} is the new reference of {0}".format(pathOps(jsonFile, "filename"),
                                                                              version + 1))

    def infoPop(self, textTitle="info", textHeader="", textInfo="", type="I"):
        self.msg = QtWidgets.QMessageBox(parent=self)
        if type == "I":
            self.msg.setIcon(QtWidgets.QMessageBox.Information)
        if type == "C":
            self.msg.setIcon(QtWidgets.QMessageBox.Critical)

        self.msg.setText(textHeader)
        self.msg.setInformativeText(textInfo)
        self.msg.setWindowTitle(textTitle)
        self.msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        self.msg.show()

    def queryPop(self, type, textTitle="Question", textHeader="", textInfo="", password=""):
        if type == "password":
            if password != "":
                passw, ok= QtWidgets.QInputDialog.getText(self, textTitle,
                                                       textInfo, QtWidgets.QLineEdit.Password, parent=self)
                if ok:
                    if passw == password:
                        return True
                    else:
                        self.infoPop(textTitle="Incorrect Passsword", textHeader="Incorrect Password", type="C")
                        return False
                else:
                    return False
            else:
                return -1

        if type == "yesNoCancel":

            q = QtWidgets.QMessageBox(parent=self)
            q.setIcon(QtWidgets.QMessageBox.Question)
            q.setText(textHeader)
            q.setInformativeText(textInfo)
            q.setWindowTitle(textTitle)
            q.setStandardButtons(
                QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
            ret = q.exec_()
            if ret == QtWidgets.QMessageBox.Save:
                return "yes"
            elif ret == QtWidgets.QMessageBox.No:
                return "no"
            elif ret == QtWidgets.QMessageBox.Cancel:
                return "cancel"

        if type == "okCancel":
            q = QtWidgets.QMessageBox(parent=self)
            q.setIcon(QtWidgets.QMessageBox.Question)
            q.setText(textHeader)
            q.setInformativeText(textInfo)
            q.setWindowTitle(textTitle)
            q.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            ret = q.exec_()
            if ret == QtWidgets.QMessageBox.Ok:
                return "ok"
            elif ret == QtWidgets.QMessageBox.Cancel:
                return "cancel"

        if type == "yesNo":
            q = QtWidgets.QMessageBox(parent=self)
            q.setIcon(QtWidgets.QMessageBox.Question)
            q.setText(textHeader)
            q.setInformativeText(textInfo)
            q.setWindowTitle(textTitle)
            q.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            ret = q.exec_()
            if ret == QtWidgets.QMessageBox.Yes:
                return "yes"
            elif ret == QtWidgets.QMessageBox.No:
                return "no"

    def onDeleteBaseScene(self):

        state = self.queryPop("password", textTitle= "DELETE BASE SCENE", textInfo="!!!DELETING BASE SCENE!!!\n\nAre you absolutely sure?", password="682")
        if state:
            row = self.scenes_listWidget.currentRow()
            if not row == -1:
                sceneName = "%s.json" % self.scenes_listWidget.currentItem().text()
                jPath = pathOps(self.scenesInCategory[0], "path")
                jsonFilePath = os.path.join(jPath, sceneName)
                self.manager.deleteBaseScene(jsonFilePath)
                self.populateScenes()
                self.statusBar().showMessage("Status | Scene Deleted => %s" % sceneName)


    def onDeleteReference(self):
        state = self.queryPop("password", textTitle= "DELETE BASE SCENE", textInfo="DELETING Reference File\n\nAre you sure?", password="682")
        if state:
            row = self.scenes_listWidget.currentRow()
            if not row == -1:
                sceneName = "%s.json" % self.scenes_listWidget.currentItem().text()
                jPath = pathOps(self.scenesInCategory[0], "path")
                jsonFilePath = os.path.join(jPath, sceneName)
                self.manager.deleteReference(jsonFilePath)
                self.populateScenes()
                self.statusBar().showMessage("Status | Reference of %s is deleted" % sceneName)

    def onDragAndDrop(self, path, mode):
        """
        drag and drop actions
        :param path: (String) value emitted by the custom listwidget
        :param mode: (String) This condition is for possible use of the function on multiple dragDrop scenartios
        :return: None
        """
        if mode=="favorites":
            normPath = os.path.normpath(path)
            fName = pathOps(normPath,"basename")
            if [fName, normPath] in self.favList:
                return
            self.favorites_listWidget.addItem(fName)
            self.userFavoritesAdd(fName, normPath)


class DropListWidget(QtWidgets.QListWidget):
    dropped = Qt.QtCore.Signal(str)
    def __init__(self, type, parent=None):
        super(DropListWidget, self).__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        # print (help(event.mimeData()))
        print event.mimeData().formats()
        if event.mimeData().hasFormat('text/uri-list'):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('text/uri-list'):
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        rawPath = event.mimeData().data('text/uri-list').__str__()
        path = rawPath.replace("file:///", "").splitlines()[0]
        self.dropped.emit(path)
        # self.addItem(path)
