## Early steps
## run commands
## import sys
## sys.path.append("C:\\Users\\kutlu\\Documents\\maya\\scripts\\tik_manager")
## import manager3dsMax as man
## reload(man)
## r=man.MainUI().show()



from PySide import QtGui
from PySide import QtCore
import os, ctypes
import MaxPlus

import json
import os, fnmatch
from shutil import copyfile
import socket
import filecmp
import re
import ctypes
import unicodedata
import pprint
import ftplib
import io
import datetime

SM_Version = "SceneManager"

def getOldestFile(rootfolder, extension=".avi"):
    return min(
        (os.path.join(dirname, filename)
        for dirname, dirnames, filenames in os.walk(rootfolder)
        for filename in filenames
        if filename.endswith(extension)),
        key=lambda fn: os.stat(fn).st_mtime)

def getNewestFile(rootfolder, extension=".avi"):
    return max(
        (os.path.join(dirname, filename)
        for dirname, dirnames, filenames in os.walk(rootfolder)
        for filename in filenames
        if filename.endswith(extension)),
        key=lambda fn: os.stat(fn).st_mtime)

def folderCheck(folder):
    if not os.path.isdir(os.path.normpath(folder)):
        os.makedirs(os.path.normpath(folder))

def loadJson(file):
    if os.path.isfile(file):
        with open(file, 'r') as f:
            # The JSON module will read our file, and convert it to a python dictionary
            data = json.load(f)
            return data
    else:
        return None

def dumpJson(data, file):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

def nameCheck(text):
    if re.match("^[A-Za-z0-9_-]*$", text):
        if text == "":
            return -1
        text = text.replace(" ", "_")
        return text
    else:
        return -1

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

def getPathsFromScene(*args, **kwargs):
    ## TODO .. TEMPORARY STATIC PATH /FIX IT
    projectPath = os.path.normpath(MaxPlus.Core.EvalMAXScript("maxfilepath").Get())
    dataPath = os.path.normpath(os.path.join(projectPath, "data"))
    folderCheck(dataPath)
    jsonPath = os.path.normpath(os.path.join(dataPath, "SMdata"))
    folderCheck(jsonPath)
    scenesPath = os.path.normpath(os.path.join(projectPath, "scenes"))
    folderCheck(scenesPath)
    playBlastRoot = os.path.normpath(os.path.join(projectPath, "Playblasts"))
    folderCheck(playBlastRoot)
    returnList = []
    for i in args:
        if i == "projectPath":
            returnList.append(projectPath)
        if i== "dataPath":
            returnList.append(dataPath)
        if i=="jsonPath":
            returnList.append(jsonPath)
        if i=="scenesPath":
            returnList.append(scenesPath)
        if i=="playBlastRoot":
            returnList.append(playBlastRoot)
    if len(returnList)<2:
        returnList = returnList[0]
    return returnList

class TikManager(object):
    def __init__(self):
        super(TikManager, self).__init__()
        self.currentProject = MaxPlus.Core.EvalMAXScript("maxfilepath").Get()
        self.currentSubProjectIndex = 0

        self.userDB = "M://Projects//__database//sceneManagerUsers.json"
        if os.path.isfile(self.userDB):
            self.userList = loadJson(self.userDB)
        else:
            self.userList = {"Generic":"gn"}
        self.validCategories = ["Model", "Shading", "Rig", "Layout", "Animation", "Render", "Other"]
        self.padding = 3
        self.subProjectList = self.scanSubProjects()

    def scanSubProjects(self):
        projectPath, jsonPath = getPathsFromScene("projectPath", "jsonPath")
        subPjson = os.path.normpath(os.path.join(jsonPath, "subPdata.json"))
        if not os.path.isfile(subPjson):
            subInfo = ["None"]
            dumpJson(subInfo, subPjson)

        else:
            subInfo=loadJson(subPjson)
        return subInfo

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
        projectPath, jsonPath = getPathsFromScene("projectPath", "jsonPath")

        subPjson = os.path.normpath(os.path.join(jsonPath, "subPdata.json"))
        if not os.path.isfile(subPjson):
            dumpJson(["None"], subPjson)
        # eger subproject olarak aranilacaksa
        if not (subProjectIndex == 0):
            jsonCategoryPath = os.path.normpath(os.path.join(jsonPath, category))
            folderCheck(jsonCategoryPath)

            jsonCategorySubPath = os.path.normpath(os.path.join(jsonCategoryPath, (self.subProjectList)[subProjectIndex]))

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
                file=os.path.join(searchFolder, file)
                allJsonFiles.append(file)
        return allJsonFiles, subPjson

    def getScene(self, *args, **kwargs):

        sceneName = MaxPlus.Core.EvalMAXScript("maxFileName").Get()
        if not sceneName:
            # // TODO find a way to warn
            # pm.warning("This is not a base scene (Untitled)")
            return ""

        projectPath, jsonPath = getPathsFromScene("projectPath", "jsonPath")

        # first get the parent dir
        scenePath = MaxPlus.Core.EvalMAXScript("maxFilePath + maxFileName").Get()
        shotDirectory = os.path.abspath(os.path.join(scenePath, os.pardir))
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

        else:
            subProject = ""
            categoryDir = upperShotDir
            category = upperShot
            jsonPath = os.path.normpath(os.path.join(jsonPath, category))

        jsonFile = os.path.join(jsonPath, "{}.json".format(shotName))

        if os.path.isfile(jsonFile):
            return "%s ==> %s ==> %s" %(subProject, category, shotName)

        else:
            return ""

    def initUserList(self):
        imajDefaultDB = "M://Projects//__database//sceneManagerUsers.json"
        homedir = os.path.expanduser("~")
        usersFilePath = os.path.join(homedir, "smUserpaths.json")
        if os.path.isfile(usersFilePath):
            info = loadJson(usersFilePath)
            try:
                self.userDB = info["userDBLocation"]
            except KeyError:
                if os.path.isfile(imajDefaultDB):
                    self.userDB = imajDefaultDB
                    self.userList = loadJson(self.userDB)
                else:
                    self.userList = {"Generic": "gn"}
        else:
            info={"userDBLocation":None}
            dumpJson(info, usersFilePath)
        pass

    def createNewProject(self, projectPath):
        # projectDate = datetime.datetime.now().strftime("%y%m%d")
        # if brandName:
        #     brandName = "%s_" %brandName
        # else:
        #     brandName = ""
        # fullName = "{0}{1}_{2}_{3}".format(brandName, projectName, clientName, projectDate)
        # fullPath = os.path.join(projectPath, fullName)
        # check if there is a duplicate
        if not os.path.isdir(os.path.normpath(projectPath)):
            os.makedirs(os.path.normpath(projectPath))
        else:
            print "Project already exists"
            return

        # create Directory structure:
        os.mkdir(os.path.join(projectPath, "_COMP"))
        os.makedirs(os.path.join(projectPath, "_MAX\\Animation"))
        os.makedirs(os.path.join(projectPath, "_MAX\\Model"))
        os.makedirs(os.path.join(projectPath, "_MAX\\Render"))
        os.mkdir(os.path.join(projectPath, "_SCULPT"))
        os.mkdir(os.path.join(projectPath, "_REALFLOW"))
        os.mkdir(os.path.join(projectPath, "_HOUDINI"))
        os.mkdir(os.path.join(projectPath, "_REF"))
        os.mkdir(os.path.join(projectPath, "_TRACK"))
        os.makedirs(os.path.join(projectPath, "_TRANSFER\\FBX"))
        os.makedirs(os.path.join(projectPath, "_TRANSFER\\ALEMBIC"))
        os.makedirs(os.path.join(projectPath, "_TRANSFER\\OBJ"))
        os.makedirs(os.path.join(projectPath, "_TRANSFER\\MA"))
        os.mkdir(os.path.join(projectPath, "assets"))
        os.mkdir(os.path.join(projectPath, "cache"))
        os.mkdir(os.path.join(projectPath, "clips"))
        os.mkdir(os.path.join(projectPath, "data"))
        os.makedirs(os.path.join(projectPath, "images\\_CompRenders"))
        os.mkdir(os.path.join(projectPath, "movies"))
        os.mkdir(os.path.join(projectPath, "particles"))
        os.mkdir(os.path.join(projectPath, "Playblasts"))
        os.makedirs(os.path.join(projectPath, "renderData\\depth"))
        os.makedirs(os.path.join(projectPath, "renderData\\fur"))
        os.makedirs(os.path.join(projectPath, "renderData\\iprImages"))
        os.makedirs(os.path.join(projectPath, "renderData\\mentalray"))
        os.makedirs(os.path.join(projectPath, "renderData\\shaders"))
        os.mkdir(os.path.join(projectPath, "scenes"))
        os.mkdir(os.path.join(projectPath, "scripts"))
        os.mkdir(os.path.join(projectPath, "sound"))
        os.makedirs(os.path.join(projectPath, "sourceimages\\_FOOTAGE"))
        os.makedirs(os.path.join(projectPath, "sourceimages\\_HDR"))

        filePath = os.path.join(projectPath, "workspace.mel")
        file = open(filePath, "w")
        # file.write("{0}\n".format(L1))
        # file.write("{0}\n".format(L2))
        # file.write("{0}\n".format(L3))
        # file.write("{0}\n".format(L4))
        # file.write("{0}\n".format(L5))
        file.close()
        pass

    def projectReport(self):

        # // TODO Create a through REPORT
        projectPath, dataPath, jsonPath, scenesPath, playBlastRoot = getPathsFromScene("projectPath", "dataPath", "jsonPath", "scenesPath", "playBlastRoot")
        # get All json files:
        oldestFile = getOldestFile(scenesPath, extension=(".mb", ".ma"))
        # oldestTime = os.stat(oldestFile).st_mtime
        oldestTimeMod = datetime.datetime.fromtimestamp(os.path.getmtime(oldestFile))

        newestFile = getNewestFile(scenesPath, extension=(".mb", ".ma"))
        # newestTime = os.stat(newestFile ).st_mtime
        newestTimeMod = datetime.datetime.fromtimestamp(os.path.getmtime(newestFile))

        L1 = "Oldest Scene file: {0} - {1}".format (pathOps(oldestFile, "basename"), oldestTimeMod)
        L2 = "Newest Scene file: {0} - {1}".format (pathOps(newestFile, "basename"), newestTimeMod)
        L3 = "Elapsed Time: {0}".format (str(newestTimeMod-oldestTimeMod))
        L4 = "Scene Counts:"
        # L5 = ""
        report = {}
        for subP in range (len(self.subProjectList)):
            subReport={}
            for category in self.validCategories:

                categoryItems=(self.scanScenes(category, subProjectAs=subP)[0])
                categoryItems = [x for x in categoryItems if x != []]

                L4 = "{0}\n{1}: {2}".format(L4, category, len(categoryItems))
                subReport[category]=categoryItems
            # allItems.append(categoryItems)
            report[self.subProjectList[subP]]=subReport

        # L3 = "There are total {0} Base Scenes in {1} Categories and {2} Sub-Projects".format
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

    def regularSaveUpdate(self):
        sceneName = os.path.normpath(pm.sceneName())

        # if the scene is untitled, dont bother to continue
        if not sceneName:
            return

        projectPath, jsonPath = getPathsFromScene("projectPath", "jsonPath")

        sceneName = MaxPlus.Core.EvalMAXScript("maxFileName").Get()
        shotDirectory = os.path.abspath(os.path.join(sceneName, os.pardir))
        shotName = os.path.basename(shotDirectory)

        upperShotDir = os.path.abspath(os.path.join(shotDirectory, os.pardir))
        upperShot = os.path.basename(upperShotDir)


        if upperShot in self.subProjectList:
            subProjectDir= upperShotDir
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
                absBaseSceneVersion = os.path.join(projectPath, jsonInfo["Versions"][int(jsonInfo["ReferencedVersion"])-1][0])
                # if the refererenced scene file is the saved file (saved or saved as)
                if sceneName == absBaseSceneVersion:
                    # copy over the forReference file
                    try:
                        copyfile(sceneName, absRefFile)
                        print "Scene Manager Update:\nReference File Updated"
                    except:
                        pass


    def saveNewScene(self, category, userName, baseName, subProject=0, makeReference=True, versionNotes="", *args, **kwargs):
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

        scenesToCheck = self.scanScenes(category, subProjectAs=subProject)[0]
        for z in scenesToCheck:
            if baseName.lower() == loadJson(z)["Name"].lower():
                # pm.warning("Choose an unique name")
                ## //TODO find a way to print out a warning in Max
                return -1

        projectPath, jsonPath, scenesPath = getPathsFromScene("projectPath", "jsonPath", "scenesPath")
        categoryPath = os.path.normpath(os.path.join(scenesPath, category))
        folderCheck(category)

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

        version=1
        sceneName = "{0}_{1}_{2}_v{3}".format(baseName, category, userName, str(version).zfill(self.padding))
        sceneFile = os.path.join(shotPath, "{0}.mb".format(sceneName))
        ## relativity update
        relSceneFile = os.path.relpath(sceneFile, start=projectPath)

        ##pm.saveAs(sceneFile)
        ## //TODO // SAVE AS

        jsonInfo = {}

        ## // TODO re-write below
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

        jsonInfo["ID"]="SceneManagerV01_sceneFile"
        # jsonInfo["MayaVersion"]=pm.versions.current()
        jsonInfo["Name"]=baseName
        jsonInfo["Path"]=os.path.relpath(shotPath, start=projectPath)
        jsonInfo["Category"]=category
        jsonInfo["Creator"]=userName
        jsonInfo["CreatorHost"]=(socket.gethostname())
        jsonInfo["Versions"]=[[relSceneFile, versionNotes, userName, socket.gethostname(), {}]] ## last item is for playplast
        dumpJson(jsonInfo, jsonFile)
        return relSceneFile

class _GCProtector(object):
    widgets = []


# noinspection PyArgumentList
app = QtGui.QApplication.instance()
if not app:
    app = QtGui.QApplication([])

def checkAdminRights():
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin

class MainUI(QtGui.QMainWindow):
    def __init__(self):
        # noinspection PyArgumentList
        for entry in QtGui.QApplication.allWidgets():
            try:
                if entry.objectName() == SM_Version:
                    entry.close()
            except AttributeError:
                pass
        parent = QtGui.QWidget(MaxPlus.GetQMaxWindow())
        super(MainUI, self).__init__(parent=parent)

        if not checkAdminRights():
            q = QtGui.QMessageBox()
            q.setIcon(QtGui.QMessageBox.Information)
            q.setText("Maya does not have the administrator rights")
            q.setInformativeText("You need to run Maya as administrator to work with Scene Manager")
            q.setWindowTitle("Admin Rights")
            q.setStandardButtons(QtGui.QMessageBox.Ok)

            ret = q.exec_()
            if ret == QtGui.QMessageBox.Ok:
                self.close()
                self.deleteLater()

        self.manager = TikManager()
        self.scenesInCategory = None

    #     self.buildUI()
    #
    # def buildUI(self):

        self.setObjectName((SM_Version))
        self.resize(680, 600)
        self.setMaximumSize(QtCore.QSize(680, 600))
        self.setWindowTitle((SM_Version))
        self.setToolTip((""))
        self.setStatusTip((""))
        self.setWhatsThis((""))
        self.setAccessibleName((""))
        self.setAccessibleDescription((""))

        self.centralwidget = QtGui.QWidget(self)
        self.centralwidget.setObjectName(("centralwidget"))

        self.baseScene_label = QtGui.QLabel(self.centralwidget)
        self.baseScene_label.setGeometry(QtCore.QRect(12, 10, 68, 21))
        self.baseScene_label.setToolTip((""))
        self.baseScene_label.setStatusTip((""))
        self.baseScene_label.setWhatsThis((""))
        self.baseScene_label.setAccessibleName((""))
        self.baseScene_label.setAccessibleDescription((""))
        self.baseScene_label.setFrameShape(QtGui.QFrame.Box)
        self.baseScene_label.setLineWidth(1)
        self.baseScene_label.setText(("Base Scene:"))
        self.baseScene_label.setTextFormat(QtCore.Qt.AutoText)
        self.baseScene_label.setScaledContents(False)
        self.baseScene_label.setObjectName(("baseScene_label"))

        self.baseScene_lineEdit = QtGui.QLabel(self.centralwidget)
        self.baseScene_lineEdit.setGeometry(QtCore.QRect(90, 10, 471, 21))
        self.baseScene_lineEdit.setToolTip((""))
        self.baseScene_lineEdit.setStatusTip((""))
        self.baseScene_lineEdit.setWhatsThis((""))
        self.baseScene_lineEdit.setAccessibleName((""))
        self.baseScene_lineEdit.setAccessibleDescription((""))
        self.baseScene_lineEdit.setText("")
        self.baseScene_lineEdit.setObjectName(("baseScene_lineEdit"))
        self.baseScene_lineEdit.setStyleSheet("QLabel {color:cyan}")

        self.projectPath_label = QtGui.QLabel(self.centralwidget)
        self.projectPath_label.setGeometry(QtCore.QRect(30, 36, 51, 21))
        self.projectPath_label.setToolTip((""))
        self.projectPath_label.setStatusTip((""))
        self.projectPath_label.setWhatsThis((""))
        self.projectPath_label.setAccessibleName((""))
        self.projectPath_label.setAccessibleDescription((""))
        self.projectPath_label.setFrameShape(QtGui.QFrame.Box)
        self.projectPath_label.setLineWidth(1)
        self.projectPath_label.setText(("Project:"))
        self.projectPath_label.setTextFormat(QtCore.Qt.AutoText)
        self.projectPath_label.setScaledContents(False)
        self.projectPath_label.setObjectName(("projectPath_label"))

        self.projectPath_lineEdit = QtGui.QLineEdit(self.centralwidget)
        self.projectPath_lineEdit.setGeometry(QtCore.QRect(90, 36, 471, 21))
        self.projectPath_lineEdit.setToolTip((""))
        self.projectPath_lineEdit.setStatusTip((""))
        self.projectPath_lineEdit.setWhatsThis((""))
        self.projectPath_lineEdit.setAccessibleName((""))
        self.projectPath_lineEdit.setAccessibleDescription((""))
        self.projectPath_lineEdit.setText((self.manager.currentProject))
        self.projectPath_lineEdit.setReadOnly(True)
        self.projectPath_lineEdit.setObjectName(("projectPath_lineEdit"))

        self.setProject_pushButton = QtGui.QPushButton(self.centralwidget)
        self.setProject_pushButton.setGeometry(QtCore.QRect(580, 36, 75, 23))
        self.setProject_pushButton.setToolTip((""))
        self.setProject_pushButton.setStatusTip((""))
        self.setProject_pushButton.setWhatsThis((""))
        self.setProject_pushButton.setAccessibleName((""))
        self.setProject_pushButton.setAccessibleDescription((""))
        self.setProject_pushButton.setText(("SET"))
        self.setProject_pushButton.setObjectName(("setProject_pushButton"))

        self.category_tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.category_tabWidget.setGeometry(QtCore.QRect(30, 110, 621, 21))
        self.category_tabWidget.setToolTip((""))
        self.category_tabWidget.setStatusTip((""))
        self.category_tabWidget.setWhatsThis((""))
        self.category_tabWidget.setAccessibleName((""))
        self.category_tabWidget.setAccessibleDescription((""))
        self.category_tabWidget.setDocumentMode(True)
        self.category_tabWidget.setObjectName(("category_tabWidget"))

        for i in self.manager.validCategories:
            self.preTab = QtGui.QWidget()
            self.preTab.setObjectName((i))
            self.category_tabWidget.addTab(self.preTab, (i))

        self.loadMode_radioButton = QtGui.QRadioButton(self.centralwidget)
        self.loadMode_radioButton.setGeometry(QtCore.QRect(30, 70, 82, 31))
        self.loadMode_radioButton.setToolTip((""))
        self.loadMode_radioButton.setStatusTip((""))
        self.loadMode_radioButton.setWhatsThis((""))
        self.loadMode_radioButton.setAccessibleName((""))
        self.loadMode_radioButton.setAccessibleDescription((""))
        self.loadMode_radioButton.setText(("Load Mode"))
        self.loadMode_radioButton.setChecked(True)
        self.loadMode_radioButton.setObjectName(("loadMode_radioButton"))

        self.referenceMode_radioButton = QtGui.QRadioButton(self.centralwidget)
        self.referenceMode_radioButton.setGeometry(QtCore.QRect(110, 70, 101, 31))
        self.referenceMode_radioButton.setToolTip((""))
        self.referenceMode_radioButton.setStatusTip((""))
        self.referenceMode_radioButton.setWhatsThis((""))
        self.referenceMode_radioButton.setAccessibleName((""))
        self.referenceMode_radioButton.setAccessibleDescription((""))
        self.referenceMode_radioButton.setText(("Reference Mode"))
        self.referenceMode_radioButton.setObjectName(("referenceMode_radioButton"))

        self.userName_comboBox = QtGui.QComboBox(self.centralwidget)
        self.userName_comboBox.setGeometry(QtCore.QRect(553, 70, 101, 31))
        self.userName_comboBox.setToolTip((""))
        self.userName_comboBox.setStatusTip((""))
        self.userName_comboBox.setWhatsThis((""))
        self.userName_comboBox.setAccessibleName((""))
        self.userName_comboBox.setAccessibleDescription((""))
        self.userName_comboBox.setObjectName(("userName_comboBox"))
        userListSorted = sorted(self.manager.userList.keys())
        for num in range(len(userListSorted)):
            self.userName_comboBox.addItem((userListSorted[num]))
            self.userName_comboBox.setItemText(num, (userListSorted[num]))

        # self.userName_comboBox.addItem((""))
        # self.userName_comboBox.setItemText(0, ("Arda Kutlu")

        self.userName_label = QtGui.QLabel(self.centralwidget)
        self.userName_label.setGeometry(QtCore.QRect(520, 70, 31, 31))
        self.userName_label.setToolTip((""))
        self.userName_label.setStatusTip((""))
        self.userName_label.setWhatsThis((""))
        self.userName_label.setAccessibleName((""))
        self.userName_label.setAccessibleDescription((""))
        self.userName_label.setText(("User:"))
        self.userName_label.setObjectName(("userName_label"))

        self.subProject_label = QtGui.QLabel(self.centralwidget)
        self.subProject_label.setGeometry(QtCore.QRect(240, 70, 100, 31))
        self.subProject_label.setToolTip((""))
        self.subProject_label.setStatusTip((""))
        self.subProject_label.setWhatsThis((""))
        self.subProject_label.setAccessibleName((""))
        self.subProject_label.setAccessibleDescription((""))
        self.subProject_label.setText(("Sub-Project:"))
        self.subProject_label.setObjectName(("subProject_label"))

        self.subProject_comboBox = QtGui.QComboBox(self.centralwidget)
        self.subProject_comboBox.setGeometry(QtCore.QRect(305, 70, 165, 31))
        self.subProject_comboBox.setToolTip((""))
        self.subProject_comboBox.setStatusTip((""))
        self.subProject_comboBox.setWhatsThis((""))
        self.subProject_comboBox.setAccessibleName((""))
        self.subProject_comboBox.setAccessibleDescription((""))
        self.subProject_comboBox.setObjectName(("subProject_comboBox"))

        self.subProject_pushbutton = QtGui.QPushButton("+", self.centralwidget)
        self.subProject_pushbutton.setGeometry(QtCore.QRect(475, 70, 31, 31))
        self.subProject_pushbutton.setToolTip((""))
        self.subProject_pushbutton.setStatusTip((""))
        self.subProject_pushbutton.setWhatsThis((""))
        self.subProject_pushbutton.setAccessibleName((""))
        self.subProject_pushbutton.setAccessibleDescription((""))
        self.subProject_pushbutton.setObjectName(("subProject_pushbutton"))

        self.scenes_listWidget = QtGui.QListWidget(self.centralwidget)
        self.scenes_listWidget.setGeometry(QtCore.QRect(30, 140, 381, 351))
        self.scenes_listWidget.setToolTip((""))
        self.scenes_listWidget.setStatusTip((""))
        self.scenes_listWidget.setWhatsThis((""))
        self.scenes_listWidget.setAccessibleName((""))
        self.scenes_listWidget.setAccessibleDescription((""))
        self.scenes_listWidget.setObjectName(("scenes_listWidget"))
        self.scenes_listWidget.setStyleSheet("border-style: solid; border-width: 2px; border-color: grey;")

        self.notes_textEdit = QtGui.QTextEdit(self.centralwidget, readOnly=True)
        self.notes_textEdit.setGeometry(QtCore.QRect(430, 260, 221, 231))
        self.notes_textEdit.setToolTip((""))
        self.notes_textEdit.setStatusTip((""))
        self.notes_textEdit.setWhatsThis((""))
        self.notes_textEdit.setAccessibleName((""))
        self.notes_textEdit.setAccessibleDescription((""))
        self.notes_textEdit.setObjectName(("notes_textEdit"))

        self.version_comboBox = QtGui.QComboBox(self.centralwidget)
        self.version_comboBox.setGeometry(QtCore.QRect(490, 150, 71, 31))
        self.version_comboBox.setToolTip((""))
        self.version_comboBox.setStatusTip((""))
        self.version_comboBox.setWhatsThis((""))
        self.version_comboBox.setAccessibleName((""))
        self.version_comboBox.setAccessibleDescription((""))
        self.version_comboBox.setObjectName(("version_comboBox"))

        self.version_label = QtGui.QLabel(self.centralwidget)
        self.version_label.setGeometry(QtCore.QRect(430, 151, 51, 31))
        self.version_label.setToolTip((""))
        self.version_label.setStatusTip((""))
        self.version_label.setWhatsThis((""))
        self.version_label.setAccessibleName((""))
        self.version_label.setAccessibleDescription((""))
        self.version_label.setFrameShape(QtGui.QFrame.Box)
        self.version_label.setFrameShadow(QtGui.QFrame.Plain)
        self.version_label.setText(("Version:"))
        self.version_label.setObjectName(("version_label"))

        self.showPB_pushButton = QtGui.QPushButton(self.centralwidget)
        self.showPB_pushButton.setGeometry(QtCore.QRect(580, 151, 72, 28))
        self.showPB_pushButton.setToolTip((""))
        self.showPB_pushButton.setStatusTip((""))
        self.showPB_pushButton.setWhatsThis((""))
        self.showPB_pushButton.setAccessibleName((""))
        self.showPB_pushButton.setAccessibleDescription((""))
        self.showPB_pushButton.setText(("Show PB"))
        self.showPB_pushButton.setObjectName(("showPB_pushButton"))

        self.makeReference_pushButton = QtGui.QPushButton(self.centralwidget)
        self.makeReference_pushButton.setGeometry(QtCore.QRect(430, 200, 131, 23))
        self.makeReference_pushButton.setToolTip(("Creates a copy the scene as \'forReference\' file"))
        self.makeReference_pushButton.setStatusTip((""))
        self.makeReference_pushButton.setWhatsThis((""))
        self.makeReference_pushButton.setAccessibleName((""))
        self.makeReference_pushButton.setAccessibleDescription((""))
        self.makeReference_pushButton.setText(("Make Reference"))
        self.makeReference_pushButton.setShortcut((""))
        self.makeReference_pushButton.setObjectName(("makeReference_pushButton"))

        self.notes_label = QtGui.QLabel(self.centralwidget)
        self.notes_label.setGeometry(QtCore.QRect(430, 240, 70, 13))
        self.notes_label.setToolTip((""))
        self.notes_label.setStatusTip((""))
        self.notes_label.setWhatsThis((""))
        self.notes_label.setAccessibleName((""))
        self.notes_label.setAccessibleDescription((""))
        self.notes_label.setText(("Version Notes:"))
        self.notes_label.setObjectName(("notes_label"))

        self.saveScene_pushButton = QtGui.QPushButton(self.centralwidget)
        self.saveScene_pushButton.setGeometry(QtCore.QRect(40, 510, 151, 41))
        self.saveScene_pushButton.setToolTip(
            ("Saves the Base Scene. This will save the scene and will make versioning possible."))
        self.saveScene_pushButton.setStatusTip((""))
        self.saveScene_pushButton.setWhatsThis((""))
        self.saveScene_pushButton.setAccessibleName((""))
        self.saveScene_pushButton.setAccessibleDescription((""))
        self.saveScene_pushButton.setText(("Save Base Scene"))
        self.saveScene_pushButton.setObjectName(("saveScene_pushButton"))

        self.saveAsVersion_pushButton = QtGui.QPushButton(self.centralwidget)
        self.saveAsVersion_pushButton.setGeometry(QtCore.QRect(210, 510, 151, 41))
        self.saveAsVersion_pushButton.setToolTip(
            ("Saves the current scene as a version. A base scene must be present."))
        self.saveAsVersion_pushButton.setStatusTip((""))
        self.saveAsVersion_pushButton.setWhatsThis((""))
        self.saveAsVersion_pushButton.setAccessibleName((""))
        self.saveAsVersion_pushButton.setAccessibleDescription((""))
        self.saveAsVersion_pushButton.setText(("Save As Version"))
        self.saveAsVersion_pushButton.setObjectName(("saveAsVersion_pushButton"))

        self.load_pushButton = QtGui.QPushButton(self.centralwidget)
        self.load_pushButton.setGeometry(QtCore.QRect(500, 510, 151, 41))
        self.load_pushButton.setToolTip(("Loads the scene or Creates the selected reference depending on the mode"))
        self.load_pushButton.setStatusTip((""))
        self.load_pushButton.setWhatsThis((""))
        self.load_pushButton.setAccessibleName((""))
        self.load_pushButton.setAccessibleDescription((""))
        self.load_pushButton.setText(("Load Scene"))
        self.load_pushButton.setObjectName(("load_pushButton"))

        self.setCentralWidget(self.centralwidget)

        self.menubar = QtGui.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 680, 18))
        self.menubar.setObjectName(("menubar"))
        self.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(self)
        self.statusbar.setObjectName(("statusbar"))
        self.setStatusBar(self.statusbar)
        self.setStatusBar(self.statusbar)

        file = self.menubar.addMenu("File")
        create_project = QtGui.QAction("&Create Project", self)
        pb_settings = QtGui.QAction("&Playblast Settings", self)
        add_remove_users = QtGui.QAction("&Add/Remove Users", self)
        deleteFile = QtGui.QAction("&Delete Selected Base Scene", self)
        deleteReference = QtGui.QAction("&Delete Reference of Selected Scene", self)
        reBuildDatabase = QtGui.QAction("&Re-build Project Database", self)
        projectReport = QtGui.QAction("&Project Report", self)
        checkReferences = QtGui.QAction("&Check References", self)

        file.addAction(create_project)
        file.addAction(pb_settings)
        file.addAction(add_remove_users)
        file.addAction(deleteFile)
        file.addAction(deleteReference)
        file.addAction(reBuildDatabase)
        file.addAction(projectReport)
        file.addAction(checkReferences)

        # create_project.triggered.connect(self.createProjectUI)
        # deleteFile.triggered.connect(lambda: self.onDeleteBaseScene())
        # deleteReference.triggered.connect(self.onDeleteReference)
        # projectReport.triggered.connect(lambda: self.manager.projectReport())
        # pb_settings.triggered.connect(self.pbSettingsUI)
        # checkReferences.triggered.connect(lambda: self.referenceCheck(deepCheck=True))
        # add_remove_users.triggered.connect(self.addRemoveUserUI)

        tools = self.menubar.addMenu("Tools")
        foolsMate = QtGui.QAction("&Fool's Mate", self)
        createPB = QtGui.QAction("&Create PlayBlast", self)
        tools.addAction(foolsMate)
        tools.addAction(createPB)

        # foolsMate.triggered.connect(self.onFoolsMate)
        # createPB.triggered.connect(self.manager.createPlayblast)

        # self.loadMode_radioButton.toggled.connect(self.onRadioButtonsToggled)
        # self.referenceMode_radioButton.toggled.connect(self.onRadioButtonsToggled)
        # self.setProject_pushButton.clicked.connect(self.onSetProject)
        # self.category_tabWidget.currentChanged.connect(self.populateScenes)
        # self.scenes_listWidget.currentItemChanged.connect(self.sceneInfo)
        # self.makeReference_pushButton.clicked.connect(self.makeReference)
        # self.saveScene_pushButton.clicked.connect(self.saveBaseSceneDialog)
        # self.saveAsVersion_pushButton.clicked.connect(self.saveAsVersionDialog)
        # self.subProject_pushbutton.clicked.connect(self.createSubProjectUI)
        # self.subProject_comboBox.activated.connect(self.onSubProjectChanged)
        # self.load_pushButton.clicked.connect(self.onloadScene)
        # self.userName_comboBox.currentIndexChanged.connect(self.onUsernameChanged)
        # self.version_comboBox.activated.connect(self.refreshNotes)
        # self.scenes_listWidget.doubleClicked.connect(self.onloadScene)
        # self.showPB_pushButton.clicked.connect(self.onShowPBclicked)

        ## RIGHT CLICK MENUS
        self.scenes_listWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # self.scenes_listWidget.customContextMenuRequested.connect(self.on_context_menu)
        self.popMenu = QtGui.QMenu()

        rcAction_0 = QtGui.QAction('Import Scene', self)
        self.popMenu.addAction(rcAction_0)
        # rcAction_0.triggered.connect(lambda: self.rcAction("importScene"))

        self.popMenu.addSeparator()

        rcAction_1 = QtGui.QAction('Show Maya Folder in Explorer', self)
        self.popMenu.addAction(rcAction_1)
        # rcAction_1.triggered.connect(lambda: self.rcAction("showInExplorerMaya"))

        rcAction_2 = QtGui.QAction('Show Playblast Folder in Explorer', self)
        self.popMenu.addAction(rcAction_2)
        # rcAction_2.triggered.connect(lambda: self.rcAction("showInExplorerPB"))

        rcAction_3 = QtGui.QAction('Show Data Folder in Explorer', self)
        self.popMenu.addAction(rcAction_3)
        # rcAction_3.triggered.connect(lambda: self.rcAction("showInExplorerData"))

        self.popMenu.addSeparator()

        rcAction_4 = QtGui.QAction('Scene Info', self)
        self.popMenu.addAction(rcAction_4)
        # rcAction_4.triggered.connect(lambda: self.onSceneInfo())

        #######
        # shortcutRefresh = QtGui.QShortcut(QtGui.QKeySequence("F5"), self, self.populateScenes)

        # self.userPrefLoad()
        self.populateScenes()

    def populateScenes(self):

        self.scenes_listWidget.clear()
        self.version_comboBox.clear()
        self.notes_textEdit.clear()
        self.subProject_comboBox.clear()
        # currentTabName = self.category_tabWidget.currentWidget().objectName()
        # scannedScenes = self.manager.scanScenes(currentTabName)

        self.scenesInCategory, subProjectFile=self.manager.scanScenes(self.category_tabWidget.currentWidget().objectName())

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
            # self.referenceCheck()
            self.version_comboBox.setEnabled(True)
        # self.manager.subProjectList = loadJson(subProjectFile)


        self.subProject_comboBox.addItems((self.manager.subProjectList))
        # index = self.manager.subProjectList.index(self.manager.currentSubProject)


        self.subProject_comboBox.setCurrentIndex(self.manager.currentSubProjectIndex)

        self.baseScene_lineEdit.setText(self.manager.getScene())

        self.refreshNotes()
        self.userPrefSave()

        # self.referenceCheck()

    def refreshNotes(self):
        row = self.scenes_listWidget.currentRow()
        if not row == -1:
            sceneName = "%s.json" % self.scenes_listWidget.currentItem().text()
            # takethefirstjson as example for rootpath
            jPath = pathOps(self.scenesInCategory[0], "path")

            sceneData = loadJson(os.path.join(jPath, sceneName))
            # sceneData = loadJson(self.scenesInCategory[row])
            currentIndex = self.version_comboBox.currentIndex()
            self.notes_textEdit.setPlainText(sceneData["Versions"][currentIndex][1])

            if sceneData["Versions"][currentIndex][4].keys():
                self.showPB_pushButton.setEnabled(True)
            else:
                self.showPB_pushButton.setEnabled(False)
        else:

            self.showPB_pushButton.setEnabled(False)

    def userPrefSave(self):
        # pass

        homedir = os.path.expanduser("~")
        settingsFilePath = os.path.join(homedir, "smSettings.json")

        settingsData = {"currentTabIndex": self.category_tabWidget.currentIndex(),
                        "currentSubIndex": self.subProject_comboBox.currentIndex(),
                        "currentUserIndex": self.userName_comboBox.currentIndex(),
                        "currentMode": self.referenceMode_radioButton.isChecked()}

        dumpJson(settingsData, settingsFilePath)
