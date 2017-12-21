import pymel.core as pm
import json
import os, fnmatch
from shutil import copyfile
import maya.mel as mel
import socket


#### Import for UI
import Qt
from Qt import QtWidgets, QtCore, QtGui
from maya import OpenMayaUI as omui

if Qt.__binding__ == "PySide":
    from shiboken import wrapInstance
    from Qt.QtCore import Signal
elif Qt.__binding__.startswith('PyQt'):
    from sip import wrapinstance as wrapInstance
    from Qt.Core import pyqtSignal as Signal
else:
    from shiboken2 import wrapInstance
    from Qt.QtCore import Signal

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

class TikManager(dict):
    def __init__(self):
        super(TikManager, self).__init__()
        self.currentProject = pm.workspace(q=1, rd=1)
        self.currentSubProject = 0
        self.userDB = "M://Projects//__database//sceneManagerUsers.json"
        if os.path.isfile(self.userDB):
            self.userList = loadJson(self.userDB)
        else:
            self.userList = {"Generic":"gn"}
        self.validCategories = ["Model", "Shading", "Rig", "Layout", "Animation",   "Render", "Other"]
        self.padding = 3
        dump, self.subProjectList = self.scanScenes(self.validCategories[0])


    def saveNewScene(self, category, userName, shotName, subProject=0, makeReference=True, *args, **kwargs):
        """
        Saves the scene with formatted name and creates a json file for the scene
        Args:
            category: (String) Category if the scene. Valid categories are 'Model', 'Animation', 'Rig', 'Shading', 'Other'
            userName: (String) Predefined user who initiates the process
            shotName: (String) Base name of the scene. Eg. 'Shot01', 'CharacterA', 'BookRig' etc...
            *args: 
            **kwargs: 

        Returns: None

        """

        ## TODO // make sure for the unique naming
        projectPath = pm.workspace(q=1, rd=1)
        dataPath = os.path.normpath(os.path.join(projectPath, "data"))
        folderCheck(dataPath)
        jsonPath = os.path.normpath(os.path.join(dataPath, "json"))
        folderCheck(jsonPath)
        jsonCategoryPath = os.path.normpath(os.path.join(jsonPath, category))
        folderCheck(jsonCategoryPath)
        scenesPath = os.path.normpath(os.path.join(projectPath, "scenes"))
        folderCheck(scenesPath)
        categoryPath = os.path.normpath(os.path.join(scenesPath, category))
        folderCheck(category)

        print "subProject", subProject

        ## eger subproject olarak kaydedilecekse
        if not subProject == 0:
            subProjectPath = os.path.normpath(os.path.join(categoryPath, self.subProjectList[subProject]))
            folderCheck(subProjectPath)
            shotPath = os.path.normpath(os.path.join(subProjectPath, shotName))
            folderCheck(shotPath)

            jsonCategoryPath = os.path.normpath(os.path.join(jsonPath, category))
            folderCheck(jsonCategoryPath)
            jsonCategorySubPath = os.path.normpath(os.path.join(jsonCategoryPath, self.subProjectList[subProject]))
            folderCheck(jsonCategorySubPath)
            jsonFile = os.path.join(jsonCategorySubPath, "{}.json".format(shotName))
        else:
            shotPath = os.path.normpath(os.path.join(categoryPath, shotName))
            folderCheck(shotPath)

            jsonCategoryPath = os.path.normpath(os.path.join(jsonPath, category))
            folderCheck(jsonCategoryPath)
            jsonFile = os.path.join(jsonCategoryPath, "{}.json".format(shotName))

        # jsonFile = os.path.join(jsonCategoryPath, "{}.json".format(shotName))

        version=1
        sceneName = "{0}_{1}_{2}_v{3}".format(shotName, category, userName, str(version).zfill(self.padding))
        sceneFile = os.path.join(shotPath, "{0}.mb".format(sceneName))
        pm.saveAs(sceneFile)

        jsonInfo = {}

        if makeReference:
            referenceName = "{0}_{1}_forReference".format(shotName, category)
            referenceFile = os.path.join(shotPath, "{0}.mb".format(referenceName))
            copyfile(sceneFile, referenceFile)
            jsonInfo["ReferenceFile"] = referenceFile
            jsonInfo["ReferencedVersion"] = version
        else:
            jsonInfo["ReferenceFile"] = None
            jsonInfo["ReferencedVersion"] = None

        jsonInfo["Name"]=shotName
        jsonInfo["Path"]=shotPath
        jsonInfo["Category"]=category
        jsonInfo["Creator"]=userName
        jsonInfo["CreatorHost"]=(socket.gethostname())
        # jsonInfo["CurrentVersion"]=001
        # jsonInfo["LastVersion"] = version
        # jsonInfo["ReferenceFile"]=referenceFile
        # jsonInfo["ReferencedVersion"]=version
        jsonInfo["Versions"]=[[sceneFile, "Initial Save", userName]]
        dumpJson(jsonInfo, jsonFile)
        print "Base Scene Saved as %s" %sceneName

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

        projectPath = pm.workspace(q=1, rd=1)
        dataPath = os.path.normpath(os.path.join(projectPath, "data"))
        folderCheck(dataPath)
        jsonPath = os.path.normpath(os.path.join(dataPath, "json"))
        folderCheck(jsonPath)


        ## get the category from the folder
        # first get the parent dir
        shotDirectory = os.path.abspath(os.path.join(pm.sceneName(), os.pardir))
        shotName = os.path.basename(shotDirectory)
        # get the category directory
        categoryDir = os.path.abspath(os.path.join(shotDirectory, os.pardir))
        category = os.path.basename(categoryDir)

        jsonCategoryPath = os.path.normpath(os.path.join(jsonPath, category))
        folderCheck(jsonCategoryPath)

        # print shotName, category
        jsonFile = os.path.join(jsonCategoryPath, "{}.json".format(shotName))
        if os.path.isfile(jsonFile):
            jsonInfo = loadJson(jsonFile)


            currentVersion = len(jsonInfo["Versions"])+1
            # jsonInfo["LastVersion"] = jsonInfo["LastVersion"] + 1
            sceneName = "{0}_{1}_{2}_v{3}".format(jsonInfo["Name"], jsonInfo["Category"], userName, str(currentVersion).zfill(self.padding))
            sceneFile = os.path.join(jsonInfo["Path"], "{0}.mb".format(sceneName))
            pm.saveAs(sceneFile)
            jsonInfo["Versions"].append([sceneFile, versionNotes, userName, (socket.gethostname())])

            if makeReference:
                referenceName = "{0}_{1}_forReference".format(shotName, category)
                referenceFile = os.path.join(jsonInfo["Path"], "{0}.mb".format(referenceName))
                copyfile(sceneFile, referenceFile)
                jsonInfo["ReferenceFile"] = referenceFile
                jsonInfo["ReferencedVersion"] = currentVersion
            dumpJson(jsonInfo, jsonFile)

    def createSubProject(self, nameOfSubProject):
        if (nameOfSubProject.lower()) == "none":
            pm.warning("Naming mismatch")
            return None
        projectPath = pm.workspace(q=1, rd=1)
        dataPath = os.path.normpath(os.path.join(projectPath, "data"))
        folderCheck(dataPath)
        jsonPath = os.path.normpath(os.path.join(dataPath, "json"))
        folderCheck(jsonPath)
        subPjson = os.path.normpath(os.path.join(jsonPath, "subPdata.json"))
        subInfo = []
        if os.path.isfile(subPjson):
            subInfo= loadJson(subPjson)

        subInfo.append(nameOfSubProject)
        self.currentSubProject = len(subInfo)-1 ## make the current sub project index the new created one.
        print "GHERE", self.currentSubProject
        dumpJson(subInfo, subPjson)
        return subInfo


    def scanScenes(self, category):
        """
        Scans the folder for json files. Instead of scanning all of the json files at once, It will scan only the target category to speed up the process.
        Args:
            category: (String) This is the category which will be scanned

        Returns: List of all json files in the category, sub-project json file

        """
        projectPath = pm.workspace(q=1, rd=1)
        dataPath = os.path.normpath(os.path.join(projectPath, "data"))
        folderCheck(dataPath)
        jsonPath = os.path.normpath(os.path.join(dataPath, "json"))
        folderCheck(jsonPath)

        subPjson = os.path.normpath(os.path.join(jsonPath, "subPdata.json"))
        if not os.path.isfile(subPjson):
            dumpJson(["None"], subPjson)

        # jsonCategoryPath = os.path.normpath(os.path.join(jsonPath, category))
        # folderCheck(jsonCategoryPath)
        # searchFolder = jsonCategoryPath


        # eger subproject olarak kaydedilecekse
        if not (self.currentSubProject == 0):
            jsonCategoryPath = os.path.normpath(os.path.join(jsonPath, category))
            folderCheck(jsonCategoryPath)
            jsonCategorySubPath = os.path.normpath(os.path.join(jsonCategoryPath, self.subProjectList[self.currentSubProject]))
            folderCheck(jsonCategorySubPath)
            searchFolder = jsonCategorySubPath
        else:
            jsonCategoryPath = os.path.normpath(os.path.join(jsonPath, category))
            folderCheck(jsonCategoryPath)
            searchFolder = jsonCategoryPath

        allJsonFiles = []
        # niceNames = []
        print "searchFolder", searchFolder
        for file in os.listdir(searchFolder):
            if file.endswith('.json'):
                file=os.path.join(searchFolder, file)
                print "file", file
                allJsonFiles.append(file)
        return allJsonFiles, subPjson

    def loadScene(self, jsonFile, version=None, force=False):
        """
        Opens the scene with the related json file and given version.
        Args:
            jsonFile: (String) This is the path of the json file which holds the scene properties.
            version: (integer) The version specified in this flag will be loaded. If not specified, last saved version will be used. Default=None
            force: (Boolean) If True, it forces the scene to load LOSING ALL THE UNSAVED CHANGES in the current scene. Default is 'False' 

        Returns: None

        """
        ## TODO // Check for the target path exists
        jsonInfo = loadJson(jsonFile)
        print jsonInfo["Versions"]
        if not version:
            # print jsonInfo["Versions"]
            sceneFile = jsonInfo["Versions"][-1][0] ## this is the absolute scene path of the last saved version
        else:
            sceneFile = jsonInfo["Versions"][version-1][0] ## this is the absolute scene path of the specified version

        pm.openFile(sceneFile, prompt=False, force=force)

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
        jsonInfo = loadJson(jsonFile)

        if version == 0 or version > len(jsonInfo["Versions"]):
            pm.error("version number mismatch - (makeReference method)")
            return
        print "anan", version
        sceneFile = jsonInfo["Versions"][version-1][0]
        referenceName = "{0}_{1}_forReference".format(jsonInfo["Name"], jsonInfo["Category"])
        referenceFile = os.path.join(jsonInfo["Path"], "{0}.mb".format(referenceName))
        copyfile(sceneFile, referenceFile)
        jsonInfo["ReferenceFile"] = referenceFile
        jsonInfo["ReferencedVersion"] = version

        print referenceFile, version
        dumpJson(jsonInfo, jsonFile)

    def loadReference(self, jsonFile):
        jsonInfo = loadJson(jsonFile)
        referenceFile = jsonInfo["ReferenceFile"]
        if referenceFile:
            pm.FileReference(referenceFile)
        else:
            pm.warning("There is no reference set for this scene. Nothing changed")





class MainUI(QtWidgets.QMainWindow):

    ## // TODO make the UI unique (should close the prior one)
    def __init__(self):
        for entry in QtWidgets.QApplication.allWidgets():
            if entry.objectName() == "SceneManager":
                entry.close()
        parent = getMayaMainWindow()
        super(MainUI, self).__init__(parent=parent)

        self.manager = TikManager()
        self.scenesInCategory = None

        self.setObjectName(("MainWindow"))
        self.resize(680, 600)
        self.setMaximumSize(QtCore.QSize(680, 600))
        self.setWindowTitle(("Scene Manager"))
        self.setToolTip((""))
        self.setStatusTip((""))
        self.setWhatsThis((""))
        self.setAccessibleName((""))
        self.setAccessibleDescription((""))

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName(("centralwidget"))

        self.projectPath_label = QtWidgets.QLabel(self.centralwidget)
        self.projectPath_label.setGeometry(QtCore.QRect(30, 30, 51, 21))
        self.projectPath_label.setToolTip((""))
        self.projectPath_label.setStatusTip((""))
        self.projectPath_label.setWhatsThis((""))
        self.projectPath_label.setAccessibleName((""))
        self.projectPath_label.setAccessibleDescription((""))
        self.projectPath_label.setFrameShape(QtWidgets.QFrame.Box)
        self.projectPath_label.setLineWidth(1)
        self.projectPath_label.setText(("Project:"))
        self.projectPath_label.setTextFormat(QtCore.Qt.AutoText)
        self.projectPath_label.setScaledContents(False)
        self.projectPath_label.setObjectName(("projectPath_label"))

        self.projectPath_lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.projectPath_lineEdit.setGeometry(QtCore.QRect(90, 30, 471, 21))
        self.projectPath_lineEdit.setToolTip((""))
        self.projectPath_lineEdit.setStatusTip((""))
        self.projectPath_lineEdit.setWhatsThis((""))
        self.projectPath_lineEdit.setAccessibleName((""))
        self.projectPath_lineEdit.setAccessibleDescription((""))
        self.projectPath_lineEdit.setText((self.manager.currentProject))
        self.projectPath_lineEdit.setReadOnly(True)
        self.projectPath_lineEdit.setObjectName(("projectPath_lineEdit"))

        self.setProject_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.setProject_pushButton.setGeometry(QtCore.QRect(580, 30, 75, 23))
        self.setProject_pushButton.setToolTip((""))
        self.setProject_pushButton.setStatusTip((""))
        self.setProject_pushButton.setWhatsThis((""))
        self.setProject_pushButton.setAccessibleName((""))
        self.setProject_pushButton.setAccessibleDescription((""))
        self.setProject_pushButton.setText(("SET"))
        self.setProject_pushButton.setObjectName(("setProject_pushButton"))
        
        self.category_tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.category_tabWidget.setGeometry(QtCore.QRect(30, 110, 621, 21))
        self.category_tabWidget.setToolTip((""))
        self.category_tabWidget.setStatusTip((""))
        self.category_tabWidget.setWhatsThis((""))
        self.category_tabWidget.setAccessibleName((""))
        self.category_tabWidget.setAccessibleDescription((""))
        self.category_tabWidget.setDocumentMode(True)
        self.category_tabWidget.setObjectName(("category_tabWidget"))

        for i in self.manager.validCategories:
            self.preTab = QtWidgets.QWidget()
            self.preTab.setObjectName((i))
            self.category_tabWidget.addTab(self.preTab, (i))


        self.loadMode_radioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.loadMode_radioButton.setGeometry(QtCore.QRect(30, 70, 82, 31))
        self.loadMode_radioButton.setToolTip((""))
        self.loadMode_radioButton.setStatusTip((""))
        self.loadMode_radioButton.setWhatsThis((""))
        self.loadMode_radioButton.setAccessibleName((""))
        self.loadMode_radioButton.setAccessibleDescription((""))
        self.loadMode_radioButton.setText(("Load Mode"))
        self.loadMode_radioButton.setChecked(True)
        self.loadMode_radioButton.setObjectName(("loadMode_radioButton"))

        self.referenceMode_radioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.referenceMode_radioButton.setGeometry(QtCore.QRect(110, 70, 101, 31))
        self.referenceMode_radioButton.setToolTip((""))
        self.referenceMode_radioButton.setStatusTip((""))
        self.referenceMode_radioButton.setWhatsThis((""))
        self.referenceMode_radioButton.setAccessibleName((""))
        self.referenceMode_radioButton.setAccessibleDescription((""))
        self.referenceMode_radioButton.setText(("Reference Mode"))
        self.referenceMode_radioButton.setObjectName(("referenceMode_radioButton"))

        self.userName_comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.userName_comboBox.setGeometry(QtCore.QRect(553, 70, 101, 31))
        self.userName_comboBox.setToolTip((""))
        self.userName_comboBox.setStatusTip((""))
        self.userName_comboBox.setWhatsThis((""))
        self.userName_comboBox.setAccessibleName((""))
        self.userName_comboBox.setAccessibleDescription((""))
        self.userName_comboBox.setObjectName(("userName_comboBox"))
        userListSorted = sorted(self.manager.userList.keys())
        for num in range (len(userListSorted)):
            self.userName_comboBox.addItem((userListSorted[num]))
            self.userName_comboBox.setItemText(num, (userListSorted[num]))

        # self.userName_comboBox.addItem((""))
        # self.userName_comboBox.setItemText(0, ("Arda Kutlu")

        self.userName_label = QtWidgets.QLabel(self.centralwidget)
        self.userName_label.setGeometry(QtCore.QRect(520, 70, 31, 31))
        self.userName_label.setToolTip((""))
        self.userName_label.setStatusTip((""))
        self.userName_label.setWhatsThis((""))
        self.userName_label.setAccessibleName((""))
        self.userName_label.setAccessibleDescription((""))
        self.userName_label.setText(("User:"))
        self.userName_label.setObjectName(("userName_label"))

        self.subProject_label = QtWidgets.QLabel(self.centralwidget)
        self.subProject_label.setGeometry(QtCore.QRect(240, 70, 100, 31))
        self.subProject_label.setToolTip((""))
        self.subProject_label.setStatusTip((""))
        self.subProject_label.setWhatsThis((""))
        self.subProject_label.setAccessibleName((""))
        self.subProject_label.setAccessibleDescription((""))
        self.subProject_label.setText(("Sub-Project:"))
        self.subProject_label.setObjectName(("subProject_label"))

        self.subProject_comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.subProject_comboBox.setGeometry(QtCore.QRect(305, 70, 165, 31))
        self.subProject_comboBox.setToolTip((""))
        self.subProject_comboBox.setStatusTip((""))
        self.subProject_comboBox.setWhatsThis((""))
        self.subProject_comboBox.setAccessibleName((""))
        self.subProject_comboBox.setAccessibleDescription((""))
        self.subProject_comboBox.setObjectName(("subProject_comboBox"))

        self.subProject_pushbutton = QtWidgets.QPushButton("+", self.centralwidget)
        self.subProject_pushbutton.setGeometry(QtCore.QRect(475, 70, 31, 31))
        self.subProject_pushbutton.setToolTip((""))
        self.subProject_pushbutton.setStatusTip((""))
        self.subProject_pushbutton.setWhatsThis((""))
        self.subProject_pushbutton.setAccessibleName((""))
        self.subProject_pushbutton.setAccessibleDescription((""))
        self.subProject_pushbutton.setObjectName(("subProject_pushbutton"))


        self.scenes_listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.scenes_listWidget.setGeometry(QtCore.QRect(30, 140, 381, 351))
        self.scenes_listWidget.setToolTip((""))
        self.scenes_listWidget.setStatusTip((""))
        self.scenes_listWidget.setWhatsThis((""))
        self.scenes_listWidget.setAccessibleName((""))
        self.scenes_listWidget.setAccessibleDescription((""))
        self.scenes_listWidget.setObjectName(("scenes_listWidget"))

        self.notes_textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.notes_textEdit.setGeometry(QtCore.QRect(430, 260, 221, 231))
        self.notes_textEdit.setToolTip((""))
        self.notes_textEdit.setStatusTip((""))
        self.notes_textEdit.setWhatsThis((""))
        self.notes_textEdit.setAccessibleName((""))
        self.notes_textEdit.setAccessibleDescription((""))
        self.notes_textEdit.setObjectName(("notes_textEdit"))

        self.version_comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.version_comboBox.setGeometry(QtCore.QRect(490, 150, 71, 31))
        self.version_comboBox.setToolTip((""))
        self.version_comboBox.setStatusTip((""))
        self.version_comboBox.setWhatsThis((""))
        self.version_comboBox.setAccessibleName((""))
        self.version_comboBox.setAccessibleDescription((""))
        self.version_comboBox.setObjectName(("version_comboBox"))

        self.version_label = QtWidgets.QLabel(self.centralwidget)
        self.version_label.setGeometry(QtCore.QRect(430, 151, 51, 31))
        self.version_label.setToolTip((""))
        self.version_label.setStatusTip((""))
        self.version_label.setWhatsThis((""))
        self.version_label.setAccessibleName((""))
        self.version_label.setAccessibleDescription((""))
        self.version_label.setFrameShape(QtWidgets.QFrame.Box)
        self.version_label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.version_label.setText(("Version:"))
        self.version_label.setObjectName(("version_label"))

        self.makeReference_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.makeReference_pushButton.setGeometry(QtCore.QRect(430, 200, 131, 23))
        self.makeReference_pushButton.setToolTip(("Creates a copy the scene as \'forReference\' file"))
        self.makeReference_pushButton.setStatusTip((""))
        self.makeReference_pushButton.setWhatsThis((""))
        self.makeReference_pushButton.setAccessibleName((""))
        self.makeReference_pushButton.setAccessibleDescription((""))
        self.makeReference_pushButton.setText(("Make Reference"))
        self.makeReference_pushButton.setShortcut((""))
        self.makeReference_pushButton.setObjectName(("makeReference_pushButton"))

        self.notes_label = QtWidgets.QLabel(self.centralwidget)
        self.notes_label.setGeometry(QtCore.QRect(430, 240, 46, 13))
        self.notes_label.setToolTip((""))
        self.notes_label.setStatusTip((""))
        self.notes_label.setWhatsThis((""))
        self.notes_label.setAccessibleName((""))
        self.notes_label.setAccessibleDescription((""))
        self.notes_label.setText(("NOTES"))
        self.notes_label.setObjectName(("notes_label"))

        self.saveScene_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.saveScene_pushButton.setGeometry(QtCore.QRect(40, 510, 151, 41))
        self.saveScene_pushButton.setToolTip(("Saves the Base Scene. This will save the scene and will make versioning possible."))
        self.saveScene_pushButton.setStatusTip((""))
        self.saveScene_pushButton.setWhatsThis((""))
        self.saveScene_pushButton.setAccessibleName((""))
        self.saveScene_pushButton.setAccessibleDescription((""))
        self.saveScene_pushButton.setText(("Save Base Scene"))
        self.saveScene_pushButton.setObjectName(("saveScene_pushButton"))

        self.saveAsVersion_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.saveAsVersion_pushButton.setGeometry(QtCore.QRect(210, 510, 151, 41))
        self.saveAsVersion_pushButton.setToolTip(("Saves the current scene as a version. A base scene must be present."))
        self.saveAsVersion_pushButton.setStatusTip((""))
        self.saveAsVersion_pushButton.setWhatsThis((""))
        self.saveAsVersion_pushButton.setAccessibleName((""))
        self.saveAsVersion_pushButton.setAccessibleDescription((""))
        self.saveAsVersion_pushButton.setText(("Save As Version"))
        self.saveAsVersion_pushButton.setObjectName(("saveAsVersion_pushButton"))

        self.load_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.load_pushButton.setGeometry(QtCore.QRect(500, 510, 151, 41))
        self.load_pushButton.setToolTip(("Loads the scene or Creates the selected reference depending on the mode"))
        self.load_pushButton.setStatusTip((""))
        self.load_pushButton.setWhatsThis((""))
        self.load_pushButton.setAccessibleName((""))
        self.load_pushButton.setAccessibleDescription((""))
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

        self.loadMode_radioButton.toggled.connect(lambda: self.version_comboBox.setEnabled(self.loadMode_radioButton.isChecked()))
        self.loadMode_radioButton.toggled.connect(lambda: self.version_label.setEnabled(self.loadMode_radioButton.isChecked()))
        self.loadMode_radioButton.toggled.connect(lambda: self.makeReference_pushButton.setEnabled(self.loadMode_radioButton.isChecked()))
        self.loadMode_radioButton.toggled.connect(lambda: self.notes_label.setEnabled(self.loadMode_radioButton.isChecked()))
        self.loadMode_radioButton.toggled.connect(lambda: self.notes_textEdit.setEnabled(self.loadMode_radioButton.isChecked()))

        self.loadMode_radioButton.toggled.connect(lambda: self.load_pushButton.setText("Load Scene"))
        self.referenceMode_radioButton.toggled.connect(lambda: self.load_pushButton.setText("Reference Scene"))
        self.loadMode_radioButton.toggled.connect(self.populateScenes)
        self.referenceMode_radioButton.toggled.connect(self.populateScenes)

        self.setProject_pushButton.clicked.connect(self.setProject)

        self.category_tabWidget.currentChanged.connect(self.populateScenes)

        self.scenes_listWidget.currentItemChanged.connect(self.sceneInfo)

        self.makeReference_pushButton.clicked.connect(self.makeReference)

        self.saveScene_pushButton.clicked.connect(self.saveDialogUI)

        self.subProject_pushbutton.clicked.connect(self.createSubProjectUI)

        self.subProject_comboBox.activated.connect(self.onSubProjectChanged)

        self.populateScenes()



    def onSubProjectChanged(self):
        self.manager.currentSubProject=self.subProject_comboBox.currentIndex()
        self.populateScenes()
        print "subPChanged",  self.manager.currentSubProject
        # dumpJson()

    def createSubProjectUI(self):
        nama = raw_input()
        self.subProject_comboBox.clear()

        self.manager.subProjectList = self.manager.createSubProject(nama)


        self.populateScenes()
        # index = self.manager.subProjectList.index(self.manager.currentSubProject)
        # self.subProject_comboBox.setCurrentIndex(index)
        # print self.manager.subProjectList


    def saveDialogUI(self):
        self.save_Dialog = QtWidgets.QDialog(parent=self)
        self.save_Dialog.setModal(True)
        self.save_Dialog.setObjectName(("save_Dialog"))
        self.save_Dialog.resize(255, 240)
        self.save_Dialog.setMinimumSize(QtCore.QSize(255, 240))
        self.save_Dialog.setMaximumSize(QtCore.QSize(255, 240))
        self.save_Dialog.setWindowTitle(("Save New Base Scene"))
        self.save_Dialog.setToolTip((""))
        self.save_Dialog.setStatusTip((""))
        self.save_Dialog.setWhatsThis((""))
        self.save_Dialog.setAccessibleName((""))
        self.save_Dialog.setAccessibleDescription((""))

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
        for i in range (len(self.manager.validCategories)):
            self.sdCategory_comboBox.addItem((self.manager.validCategories[i]))
            self.sdCategory_comboBox.setItemText(i, (self.manager.validCategories[i]))

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
        self.sd_buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.sd_buttonBox.setObjectName(("sd_buttonBox"))


        self.sd_buttonBox.accepted.connect(self.saveBaseScene)
        self.sd_buttonBox.accepted.connect(self.save_Dialog.accept)
        self.sd_buttonBox.rejected.connect(self.save_Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(self.save_Dialog)

        self.save_Dialog.show()

    def saveBaseScene(self):
        userInitials = self.manager.userList[self.userName_comboBox.currentText()]
        subProject = self.sdSubP_comboBox.currentIndex()
        self.manager.saveNewScene(self.sdCategory_comboBox.currentText(), userInitials, self.sdName_lineEdit.text(), subProject = subProject, makeReference= self.sdMakeReference_checkbox.checkState())
        self.populateScenes()

    def setProject(self):
        mel.eval("SetProject;")
        self.manager.currentProject = pm.workspace(q=1, rd=1)
        self.projectPath_lineEdit.setText(self.manager.currentProject)
        ## TODO INIT AGAIN

    # def testMethod(self):
    #     print self.category_tabWidget.currentIndex()
    #     print self.category_tabWidget.currentWidget().objectName()

    def sceneInfo(self):
        ## //TODO : SHOW REFERENCED SCENES WITH DIFFERENT COLOR
        sceneData = loadJson(self.scenesInCategory[self.scenes_listWidget.currentRow()])
        print "sceneData", sceneData
        self.version_comboBox.clear()
        for num in range (len(sceneData["Versions"])):
            self.version_comboBox.addItem("v{0}".format(str(num+1).zfill(3)))

        if sceneData["ReferencedVersion"]:
            self.version_comboBox.setCurrentIndex(sceneData["ReferencedVersion"]-1)
        else:
            self.version_comboBox.setCurrentIndex(len(sceneData["Versions"])-1)




    def populateScenes(self):
        # print self.category_tabWidget
        self.scenes_listWidget.clear()
        self.version_comboBox.clear()
        self.notes_textEdit.clear()
        self.subProject_comboBox.clear()
        self.scenesInCategory, subProjectFile=self.manager.scanScenes(self.category_tabWidget.currentWidget().objectName())
        if self.referenceMode_radioButton.isChecked():
            for i in self.scenesInCategory:
                jsonFile = loadJson()
                if jsonFile["ReferenceFile"]:
                    self.scenes_listWidget.addItem(pathOps(i, "filename"))

        else:
            # self.scenes_listWidget.addItems(self.scenesInCategory)
            for i in self.scenesInCategory:
                self.scenes_listWidget.addItem(pathOps(i, "filename"))

        self.manager.subProjectList = loadJson(subProjectFile)
        self.subProject_comboBox.addItems((self.manager.subProjectList))
        # index = self.manager.subProjectList.index(self.manager.currentSubProject)
        self.subProject_comboBox.setCurrentIndex(self.manager.currentSubProject)

        # print (self.manager.currentSubProject)

        # print scenesInCategory

    def makeReference(self):
        jsonFile = self.scenesInCategory[self.scenes_listWidget.currentRow()]
        version = self.version_comboBox.currentIndex()
        self.manager.makeReference(jsonFile, version+1)
        # self.sceneInfo()

