## This version is not working with Pyinstaller compile because of the Qt module

import SmRoot
reload(SmRoot)
from SmRoot import RootManager
from SmUIRoot import MainUI as baseUI
import Qt
from Qt import QtWidgets, QtCore, QtGui



import sys, os
import ImageViewer
# reload(ImageViewer)
import _version
import subprocess
# import json

import pprint
import logging




__author__ = "Arda Kutlu"
__copyright__ = "Copyright 2018, Scene Manager for Maya Project"
__credits__ = []
__version__ = "2.0.0"
__license__ = "GPL"
__maintainer__ = "Arda Kutlu"
__email__ = "ardakutlu@gmail.com"
__status__ = "Development"

SM_Version = "Scene Manager Standalone v%s" %_version.__version__

logging.basicConfig()
logger = logging.getLogger('smStandalone')
logger.setLevel(logging.DEBUG)

class SwViewer(RootManager):
    def __init__(self, swDict, projectDir):
        super(SwViewer, self).__init__()
        self.swDict = swDict
        self.niceName = swDict["niceName"]
        self.projectDir = projectDir

        self.init_paths()
        self.init_database()

    def getSoftwarePaths(self):
        """Overriden function"""
        return self.swDict

    def getProjectDir(self):
        """Overriden function"""
        return self.projectDir

    def getSceneFile(self):
        """Overriden function"""
        return ""

    def getExecutables(self, rootPath, relativePath, executableList, searchword=None):
        if searchword:
            try:
                versionRoots = [x for x in os.listdir(rootPath) if x.startswith(searchword) and os.path.isdir(os.path.join(rootPath, x))]
            except WindowsError:
                msg = "Cannot resolve executable paths"
                self._exception(360, msg)
                return
        else:
            try:
                versionRoots = [x for x in os.listdir(rootPath) if os.path.isdir(os.path.join(rootPath, x))]
            except WindowsError:
                msg = "Cannot resolve executable paths"
                self._exception(360, msg)
                return
        for v in versionRoots:
            exeDir = os.path.join(rootPath, v, relativePath)
            for exe in executableList:
                exePath = os.path.join(exeDir, exe)
                if os.path.isfile(exePath):
                    yield [v, exePath]

    def executeScene(self):
        if self.currentPlatform is not "Windows":
            logger.warning("Currently only windows executables are supported")
            return None

        ID = self._currentSceneInfo["ID"]
        if ID.startswith("SmMaya"):
            swID = "SmMaya"
        elif ID.startswith("Sm3dsMax"):
            swID = "Sm3dsMax"
        elif ID.startswith("SmHoudini"):
            swID = "SmHoudini"
        else:
            msg = "Cannot resolve software version from database"
            self._exception(360, msg)
            return


        # resolve executables
        programFiles32 = os.environ["PROGRAMFILES(X86)"]
        programFiles64 = os.environ["PROGRAMFILES"]

        pDict={"SmMaya":
                    {
                        "root": "Autodesk",
                        "relPath": "bin",
                        "exeList": ["maya.exe"],
                        "searchWord": "Maya"
                     },
                "Sm3dsMax":
                    {
                        "root": "Autodesk",
                        "relPath": "",
                        "exeList": ["3dsmax.exe"],
                        "searchWord": "3ds"
                    },
                "SmHoudini":
                    {
                        "root": "Side Effects Software",
                        "relPath": "bin",
                        "exeList": ["houdini.exe", "houdinifx.exe"],
                        "searchWord": "Hou"
                    }
                }

        exeGen32Bit = self.getExecutables(os.path.join(programFiles32, pDict[swID]["root"]), pDict[swID]["relPath"],
                                           pDict[swID]["exeList"], searchword=pDict[swID]["searchWord"])


        exeGen64Bit = self.getExecutables(os.path.join(programFiles64, pDict[swID]["root"]), pDict[swID]["relPath"],
                                           pDict[swID]["exeList"], searchword=pDict[swID]["searchWord"])

        # for x in exeGen64Bit:
        #     print x
        if not exeGen32Bit and exeGen64Bit:
            msg = "Cannot resolve executable paths"
            self._exception(360, msg)
            return

        # resolve versions

        #----
        #MAYA
        #----
        if swID == "SmMaya":
            versionDict = {201400: "Maya2014",
                           201450: "Maya2014",
                           201451: "Maya2014",
                           201459: "Maya2014",
                           201402: "Maya2014",
                           201404: "Maya2014",
                           201406: "Maya2014",
                           201500: "Maya2015",
                           201506: "Maya2015",
                           201507: "Maya2015",
                           201501: "Maya2015",
                           201502: "Maya2015",
                           201505: "Maya2015",
                           201506: "Maya2015",
                           201507: "Maya2015",
                           201600: "Maya2016",
                           201650: "Maya2016.5",
                           201651: "Maya2016.5",
                           201653: "Maya2016.5",
                           201605: "Maya2016",
                           201607: "Maya2016",
                           201650: "Maya2016.5",
                           201651: "Maya2016.5",
                           201653: "Maya2016.5",
                           201605: "Maya2016",
                           201607: "Maya2016",
                           201700: "Maya2017",
                           201701: "Maya2017",
                           201720: "Maya2017",
                           201740: "Maya2017",
                           20180000: "Maya2018"}
            try:
                versionName = versionDict[self._currentSceneInfo["MayaVersion"]]
            except KeyError:
                msg = "Maya version cannot resolved"
                self._exception(360, msg)
                return

            exePath = None
            for v in exeGen64Bit:
                if v[0] == versionName:
                    exePath = v[1]
                    break
            for v in exeGen32Bit:
                if v[0] == versionName:
                    exePath = v[1]
                    break

            if not exePath:
                msg = "%s is not installed on this workstation" %versionName
                self._exception(360, msg)
                return
            # subprocess.check_call([exePath, "-file", self.currentScenePath], shell=True)
            subprocess.Popen([exePath, "-file", self.currentScenePath], shell=True)
            return

        elif swID == "Sm3dsMax":
            versionDict = {16000: "3ds Max 2014",
                           17000: "3ds Max 2015",
                           18000: "3ds Max 2016",
                           19000: "3ds Max 2017",
                           20000: "3ds Max 2018"
                           }
            try:
                versionName = versionDict[self._currentSceneInfo["3dsMaxVersion"][0]]
            except KeyError:
                msg = "3ds Max version cannot resolved"
                self._exception(360, msg)
                return

            exePath = None
            for v in exeGen64Bit:
                if v[0] == versionName:
                    exePath = v[1]
                    break
            for v in exeGen32Bit:
                if v[0] == versionName:
                    exePath = v[1]
                    break

            if not exePath:
                msg = "%s is not installed on this workstation" % versionName
                self._exception(360, msg)
                return
            # subprocess.check_call([exePath, "-file", self.currentScenePath], shell=True)
            subprocess.Popen([exePath, "-file", self.currentScenePath], shell=True)
            return

        elif swID == "SmHoudini":
            dbVersion = self._currentSceneInfo["HoudiniVersion"][0]
            dbIsApprentice = self._currentSceneInfo["HoudiniVersion"][1]
            for v in exeGen64Bit:
                versionNumber = v[0].split()[1]
                versionAsList = [int(s) for s in versionNumber.split(".") if s.isdigit()]
                exePath = v[1]
                if dbVersion == versionAsList:
                    if dbIsApprentice:
                        subprocess.Popen([exePath, "-apprentice", self.currentScenePath], shell=True)
                    else:
                        subprocess.Popen([exePath, self.currentScenePath], shell=True)
                    return
            msg = "Houdini %s is not installed on this workstation" % dbVersion
            self._exception(360, msg)
            return

            # return

    def _exception(self, code, msg):
        """OVERRIDEN"""
        # logger.error("Exception %s" %self.errorCodeDict[code])
        # logger.error(msg)

        errorbox = QtWidgets.QMessageBox()
        errorbox.setModal(True)
        errorbox.setText(msg)
        errorbox.setWindowTitle(self.errorCodeDict[code])
        errorbox.exec_()

        if (200 >= code < 210):
            raise Exception(code, msg)


class StandaloneManager(RootManager):
    def __init__(self):
        super(StandaloneManager, self).__init__()

        self.swDictList = [{"niceName": "3dsMax",
                            "databaseDir": "maxDB",
                            "scenesDir": "scenes_3dsMax",
                            "pbSettingsFile": "pbSettings_3dsMax.json",
                            "categoriesFile": "categories3dsMax.json",
                            "userSettingsDir": "Documents\\SceneManager\\3dsMax"},

                           {"niceName": "Maya",
                            "databaseDir": "mayaDB",
                            "scenesDir": "scenes",
                            "pbSettingsFile": "pbSettings.json",
                            "categoriesFile": "categoriesMaya.json",
                            "userSettingsDir": "Documents\\SceneManager\\Maya"},

                           {"niceName": "Houdini",
                            "databaseDir": "houdiniDB",
                            "scenesDir": "scenes_houdini",
                            "pbSettingsFile": "pbSettings_houdini.json",
                            "categoriesFile": "categoriesHoudini.json",
                            "userSettingsDir": "Documents\\SceneManager\\Houdini"}

                           ]

        # self.validSoftwares = []
        self.swList = []
        self.init_paths()
        self.init_database()

        self.initSoftwares()


    def init_paths(self):
        """Overriden function"""
        # homeDir = os.path.expanduser("~")
        # self.userSettingsDir = os.path.normpath(os.path.join(homeDir, "Documents", "SceneManager", "Standalone"))
        # self._folderCheck(self.userSettingsDir)
        # self.projectsFile = os.path.join(self.userSettingsDir, "smProjects.json")

        self._pathsDict["userSettingsDir"] = os.path.normpath(os.path.join(os.path.expanduser("~"), "Documents", "SceneManager", "Standalone"))
        self._folderCheck(self._pathsDict["userSettingsDir"])

        self._pathsDict["bookmarksFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], "smBookmarks.json"))
        self._pathsDict["currentsFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], "smCurrents.json"))
        self._pathsDict["projectsFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], "smProjects.json"))


        self._pathsDict["projectDir"] = self.getProjectDir()
        self._pathsDict["sceneFile"] = ""

        self._pathsDict["masterDir"] = os.path.normpath(os.path.join(self._pathsDict["projectDir"], "smDatabase"))

        self._pathsDict["projectSettingsFile"] = os.path.normpath(os.path.join(self._pathsDict["masterDir"], "projectSettings.json"))


        self._pathsDict["generalSettingsDir"] = os.path.dirname(os.path.abspath(__file__))
        self._pathsDict["usersFile"] = os.path.normpath(os.path.join(self._pathsDict["generalSettingsDir"], "sceneManagerUsers.json"))

    def init_database(self):
        """Overriden function"""

        self._usersDict = self._loadUsers()
        self._currentsDict = self._loadUserPrefs()

    def getProjectDir(self):
        """Overriden function"""
        # get the projects file for standalone manager
        projectsDict = self._loadProjects()

        if not projectsDict:
            norm_p_path = os.path.normpath(os.path.expanduser("~"))
            projectsDict = {"StandaloneProject": norm_p_path}
            self._saveProjects(projectsDict)
            return norm_p_path

        # get the project defined in the database file
        try:
            norm_p_path = projectsDict["StandaloneProject"]
            return norm_p_path
        except KeyError:
            norm_p_path = os.path.normpath(os.path.expanduser("~"))
            projectsDict = {"StandaloneProject": norm_p_path}
            self._saveProjects(projectsDict)
            return norm_p_path

    def setProject(self, path):
        """Sets the project"""
        projectsDict = self._loadProjects()
        if not projectsDict:
            projectsDict = {"StandaloneProject": path}
        else:
            projectsDict["StandaloneProject"] = path
        self._saveProjects(projectsDict)
        self.projectDir = path
        self.init_paths()
        self.init_database()
        self.initSoftwares()


    def initSoftwares(self):
        # We need to get which softwares are used in the current project
        self.swList = []
        dbFolder = self._pathsDict["masterDir"]
        if not os.path.isdir(dbFolder):
            self.swList = [] # empty software list
            return self.swList#this is not a sceneManager project
        for swDict in self.swDictList:
            searchPath = (os.path.join(self.projectDir, "smDatabase", swDict["databaseDir"]))
            if os.path.isdir(searchPath):
                self.swList.append(SwViewer(swDict, self.projectDir))
        return self.swList

    @property
    def currentSwIndex(self):
        """returns current sofware"""
        return self._currentsDict["currentSwIndex"]

    @currentSwIndex.setter
    def currentSwIndex(self, indexData):
        """Moves the cursor to the given software index"""
        if not 0 <= indexData < len(self.swList):
            msg="Software index is out of range!"
            raise Exception([101, msg])
        if indexData == self.currentSwIndex:
            self.swList[indexData].cursorInfo()
            return
        self._setCurrents("currentSwIndex", indexData)
        # self.swList[indexData].scanBaseScenes()
        # self.swList[indexData].currentBaseSceneName = ""
        # self.swList[indexData]._currentPreviewCamera = ""
        # self.swList[indexData].cursorInfo()
        pass

    # def getSoftwareList(self):
    #     return self.swList

    def _exception(self, code, msg):
        """OVERRIDEN"""
        logger.error("Exception %s" %self.errorCodeDict[code])
        logger.error(msg)

        errorCodeDict = {200: "Corrupted File",
                         201: "Missing File",
                         202: "Read/Write Error",
                         203: "Delete Error",
                         210: "OS Not Supported",
                         101: "Out of range",
                         102: "Missing Override",
                         340: "Naming Error",
                         341: "Mandatory fields are not filled",
                         360: "Action not permitted"}


        errorbox = QtGui.QMessageBox()
        errorbox.setModal(True)
        errorbox.setText(msg)
        errorbox.setWindowTitle(errorCodeDict[code])
        errorbox.exec_()

        if (200 >= code < 210):
            raise Exception(code, msg)


    def _loadUserPrefs(self):
        """OVERRIDEN FUNCTION Load Last CategoryIndex, SubProject Index,
        User name and Access mode from file as dictionary"""
        if os.path.isfile(self._pathsDict["currentsFile"]):
            settingsData = self._loadJson(self._pathsDict["currentsFile"])
            if settingsData == -2:
                return -2
        else:
            settingsData = {"currentTabIndex": 0,
                            "currentSubIndex": 0,
                            "currentUser": self._usersDict.keys()[0],
                            "currentSwIndex": -1, # added multi software switch
                            "currentMode": 1} # for compatibility issues
            self._dumpJson(settingsData, self._pathsDict["currentsFile"])
        return settingsData




    # def getAllBaseScenes(self):
    #     """Collects all base scenes for each category at cursor category and subproject"""
    #     pass

    # def _folderCheck(self, folder):
    #     if not os.path.isdir(os.path.normpath(folder)):
    #         os.makedirs(os.path.normpath(folder))
    #
    # def _loadJson(self, file):
    #     """Loads the given json file"""
    #     if os.path.isfile(file):
    #         try:
    #             with open(file, 'r') as f:
    #                 data = json.load(f)
    #                 return data
    #         except ValueError:
    #             msg = "Corrupted JSON file => %s" % file
    #             return -2 # code for corrupted json file
    #     else:
    #         return None
    #
    # def _dumpJson(self, data, file):
    #     """Saves the data to the json file"""
    #     with open(file, "w") as f:
    #         json.dump(data, f, indent=4)

class MainUI(baseUI):
    def __init__(self):
        super(MainUI, self).__init__()

        self.manager = StandaloneManager()
        # self.manager = self._getManager()
        # problem, msg = self.manager._checkRequirements()
        # if problem:
        #     self.close()
        #     self.deleteLater()

        self.buildUI()
        self.extraMenus()
        self.modify()
        self.initMainUI(newborn=True)


    def extraMenus(self):
        self.software_comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.software_comboBox.setMinimumSize(QtCore.QSize(150, 30))
        self.software_comboBox.setMaximumSize(QtCore.QSize(16777215, 30))
        self.software_comboBox.setObjectName(("software_comboBox"))
        self.r2_gridLayout.addWidget(self.software_comboBox, 0, 1, 1, 1)
        self.software_comboBox.activated.connect(self.onSoftwareChange)

    def modify(self):
        # make sure load mode is checked and hidden
        self.load_radioButton.setChecked(True)
        self.load_radioButton.setVisible(False)
        self.reference_radioButton.setChecked(False)
        self.reference_radioButton.setVisible(False)

        self.baseScene_label.setVisible(False)
        self.baseScene_lineEdit.setVisible(False)

        self.createPB.setVisible(False)

        self.saveVersion_pushButton.setVisible(False)
        self.saveVersion_fm.setVisible(False)
        self.saveBaseScene_pushButton.setVisible(False)
        self.saveBaseScene_fm.setVisible(False)


    def initMainUI(self, newborn=False):

        if not newborn:
            self.manager.init_paths()
            self.manager.init_database()
        # init softwares
        self.manager.initSoftwares()
        self._initSoftwares()

        self._initCategories()
        # init project
        self.project_lineEdit.setText(self.manager.projectDir)
        # init subproject
        self._initSubProjects()
        # init base scenes
        self.populateBaseScenes()
        # init users
        self._initUsers()
        # # disable the version related stuff
        self.version_comboBox.setStyleSheet("background-color: rgb(80,80,80); color: white")
        self._vEnableDisable()

    def _getManager(self):
        swList = self.manager.swList
        swIndex = self.software_comboBox.currentIndex()
        try:
            manager = swList[swIndex]
        except IndexError:
            return
        return manager

    def _initSoftwares(self):
        self.software_comboBox.blockSignals(True)

        self.software_comboBox.clear()
        for x in self.manager.swList:
            self.software_comboBox.addItem(x.niceName)

        self.software_comboBox.setStyleSheet("background-color: %s; color: black" %self.swColorDict[str(self.software_comboBox.currentText())])

        self.software_comboBox.blockSignals(False)

    def addRemoveCategoryUI(self):

        passw, ok = QtWidgets.QInputDialog.getText(self, "Password Query",
                                               "Enter Admin Password:", QtWidgets.QLineEdit.Password)

        manager = self._getManager()
        if not manager:
            return

        if ok:
            if self.manager.checkPassword(passw):
                pass
            else:
                self.infoPop(textTitle="Incorrect Password", textHeader="The Password is invalid")
                return
        else:
            return


        categories_dialog = QtWidgets.QDialog(parent=self)
        categories_dialog.setModal(True)
        categories_dialog.setObjectName(("category_Dialog"))
        categories_dialog.setMinimumSize(QtCore.QSize(342, 177))
        categories_dialog.setMaximumSize(QtCore.QSize(342, 177))
        categories_dialog.setWindowTitle(("Add/Remove Categories"))
        categories_dialog.setFocus()

        addnewcategory_groupbox = QtWidgets.QGroupBox(categories_dialog)
        addnewcategory_groupbox.setGeometry(QtCore.QRect(10, 10, 321, 81))
        addnewcategory_groupbox.setTitle(("Add New Category"))
        addnewcategory_groupbox.setObjectName(("addnewcategory_groupBox"))

        categoryName_label = QtWidgets.QLabel(addnewcategory_groupbox)
        categoryName_label.setGeometry(QtCore.QRect(10, 30, 81, 21))
        categoryName_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        categoryName_label.setText(("Category Name:"))
        categoryName_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        categoryName_label.setObjectName(("categoryName_label"))

        self.categoryName_lineEdit= QtWidgets.QLineEdit(addnewcategory_groupbox)
        self.categoryName_lineEdit.setGeometry(QtCore.QRect(105, 30, 135, 20))
        self.categoryName_lineEdit.setPlaceholderText(("e.g \"Look Dev\""))
        self.categoryName_lineEdit.setObjectName(("categoryName_lineEdit"))

        addnewcategory_pushButton = QtWidgets.QPushButton(addnewcategory_groupbox)
        addnewcategory_pushButton.setGeometry(QtCore.QRect(250, 28, 61, 26))
        addnewcategory_pushButton.setText(("Add"))
        addnewcategory_pushButton.setObjectName(("addnewcategory_pushButton"))

        deletecategory_groupBox = QtWidgets.QGroupBox(categories_dialog)
        deletecategory_groupBox.setGeometry(QtCore.QRect(10, 110, 321, 51))
        deletecategory_groupBox.setTitle(("Delete and Change Order"))
        deletecategory_groupBox.setObjectName(("deletecategory_groupBox"))

        self.selectcategory_comboBox = QtWidgets.QComboBox(deletecategory_groupBox)
        self.selectcategory_comboBox.setGeometry(QtCore.QRect(10, 20, 231, 22))
        self.selectcategory_comboBox.setObjectName(("selectcategory_comboBox"))

        self.selectcategory_comboBox.addItems(manager._categories)

        deletecategory_pushButton = QtWidgets.QPushButton(deletecategory_groupBox)
        deletecategory_pushButton.setGeometry(QtCore.QRect(250, 20, 61, 21))
        deletecategory_pushButton.setText(("Delete"))
        deletecategory_pushButton.setObjectName(("deletecategory_pushButton"))


        def onAddCategory():
            manager.addCategory(str(self.categoryName_lineEdit.text()))


            preTab = QtWidgets.QWidget()
            preTab.setObjectName(self.categoryName_lineEdit.text())
            self.category_tabWidget.addTab(preTab, self.categoryName_lineEdit.text())
            self.selectcategory_comboBox.addItem(self.categoryName_lineEdit.text())

            self.categoryName_lineEdit.setText("")

        def onRemoveCategory():
            manager.removeCategory(str(self.selectcategory_comboBox.currentText()))
            self.selectcategory_comboBox.clear()
            self.selectcategory_comboBox.addItems(manager.getCategories())

            self._initCategories()


        addnewcategory_pushButton.clicked.connect(onAddCategory)
        deletecategory_pushButton.clicked.connect(onRemoveCategory)

        self.categoryName_lineEdit.textChanged.connect(
            lambda: self._checkValidity(self.categoryName_lineEdit.text(), addnewcategory_pushButton,
                                        self.categoryName_lineEdit))


        categories_dialog.show()

        def projectSettingsUI(self):
            passw, ok = QtWidgets.QInputDialog.getText(self, "Password Query", "Enter Admin Password:",
                                                       QtWidgets.QLineEdit.Password)

            if ok:
                if self.manager.checkPassword(passw):
                    pass
                else:
                    self.infoPop(textTitle="Incorrect Password", textHeader="The Password is invalid")
                    return
            else:
                return

            projectSettingsDB = self.manager._loadProjectSettings()

            projectSettings_Dialog = QtWidgets.QDialog(parent=self)
            projectSettings_Dialog.setObjectName("projectSettings_Dialog")
            projectSettings_Dialog.resize(270, 120)
            projectSettings_Dialog.setMinimumSize(QtCore.QSize(270, 120))
            projectSettings_Dialog.setMaximumSize(QtCore.QSize(270, 120))
            projectSettings_Dialog.setWindowTitle("Project Settings")

            gridLayout = QtWidgets.QGridLayout(projectSettings_Dialog)
            gridLayout.setObjectName(("gridLayout"))

            buttonBox = QtWidgets.QDialogButtonBox(projectSettings_Dialog)
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            buttonBox.setMaximumSize(QtCore.QSize(16777215, 30))
            buttonBox.setOrientation(QtCore.Qt.Horizontal)
            buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Save)
            buttonBox.setObjectName("buttonBox")

            gridLayout.addWidget(buttonBox, 1, 0, 1, 1)

            formLayout = QtWidgets.QFormLayout()
            formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
            formLayout.setLabelAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
            formLayout.setFormAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
            formLayout.setObjectName("formLayout")

            resolution_label = QtWidgets.QLabel(projectSettings_Dialog)
            resolution_label.setText("Resolution:")
            resolution_label.setObjectName("resolution_label")
            formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, resolution_label)

            horizontalLayout = QtWidgets.QHBoxLayout()
            horizontalLayout.setObjectName("horizontalLayout")

            resolutionX_spinBox = QtWidgets.QSpinBox(projectSettings_Dialog)
            resolutionX_spinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
            resolutionX_spinBox.setObjectName("resolutionX_spinBox")
            horizontalLayout.addWidget(resolutionX_spinBox)
            resolutionX_spinBox.setRange(1, 99999)
            resolutionX_spinBox.setValue(projectSettingsDB["Resolution"][0])

            resolutionY_spinBox = QtWidgets.QSpinBox(projectSettings_Dialog)
            resolutionY_spinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
            resolutionY_spinBox.setObjectName("resolutionY_spinBox")
            horizontalLayout.addWidget(resolutionY_spinBox)
            resolutionY_spinBox.setRange(1, 99999)
            resolutionY_spinBox.setValue(projectSettingsDB["Resolution"][1])

            formLayout.setLayout(0, QtWidgets.QFormLayout.FieldRole, horizontalLayout)
            fps_label = QtWidgets.QLabel(projectSettings_Dialog)
            fps_label.setText("FPS")
            fps_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
            fps_label.setObjectName("fps_label")
            formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, fps_label)

            fps_comboBox = QtWidgets.QComboBox(projectSettings_Dialog)
            fps_comboBox.setMaximumSize(QtCore.QSize(60, 16777215))
            fps_comboBox.setObjectName("fps_comboBox")
            formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, fps_comboBox)
            fps_comboBox.addItems(self.manager.fpsList)
            try:
                index = self.manager.fpsList.index(str(projectSettingsDB["FPS"]))
            except:
                index = 2
            fps_comboBox.setCurrentIndex(index)
            gridLayout.addLayout(formLayout, 0, 0, 1, 1)

            # SIGNALS
            # -------
            def onAccepted():
                projectSettingsDB = {"Resolution": [resolutionX_spinBox.value(), resolutionY_spinBox.value()],
                                     "FPS": int(fps_comboBox.currentText())}
                self.manager._saveProjectSettings(projectSettingsDB)
                projectSettings_Dialog.close()

            buttonBox.accepted.connect(onAccepted)
            buttonBox.rejected.connect(projectSettings_Dialog.reject)

            projectSettings_Dialog.show()

    def addNoteDialog(self):
        manager = self._getManager()
        if not manager:
            return
        row = self.scenes_listWidget.currentRow()
        if row == -1:
            return

        addNotes_Dialog = QtWidgets.QDialog(parent=self)
        addNotes_Dialog.setModal(True)
        addNotes_Dialog.setObjectName(("addNotes_Dialog"))
        addNotes_Dialog.resize(255, 290)
        addNotes_Dialog.setMinimumSize(QtCore.QSize(255, 290))
        addNotes_Dialog.setMaximumSize(QtCore.QSize(255, 290))
        addNotes_Dialog.setWindowTitle(("Add Notes"))

        addNotes_label = QtWidgets.QLabel(addNotes_Dialog)
        addNotes_label.setGeometry(QtCore.QRect(15, 15, 100, 20))
        addNotes_label.setText(("Additional Notes"))
        addNotes_label.setObjectName(("addNotes_label"))

        addNotes_textEdit = QtWidgets.QTextEdit(addNotes_Dialog)
        addNotes_textEdit.setGeometry(QtCore.QRect(15, 40, 215, 170))
        addNotes_textEdit.setObjectName(("addNotes_textEdit"))

        addNotes_buttonBox = QtWidgets.QDialogButtonBox(addNotes_Dialog)
        addNotes_buttonBox.setGeometry(QtCore.QRect(20, 250, 220, 32))
        addNotes_buttonBox.setOrientation(QtCore.Qt.Horizontal)
        addNotes_buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel)

        buttonS = addNotes_buttonBox.button(QtWidgets.QDialogButtonBox.Save)
        buttonS.setText('Add Notes')
        buttonC = addNotes_buttonBox.button(QtWidgets.QDialogButtonBox.Cancel)
        buttonC.setText('Cancel')

        addNotes_buttonBox.setObjectName(("addNotes_buttonBox"))
        addNotes_buttonBox.accepted.connect(lambda: manager.addNote(addNotes_textEdit.toPlainText()))
        addNotes_buttonBox.accepted.connect(self.onVersionChange)
        addNotes_buttonBox.accepted.connect(addNotes_Dialog.accept)

        addNotes_buttonBox.rejected.connect(addNotes_Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(addNotes_Dialog)

        addNotes_Dialog.show()

    def onContextMenu_scenes(self, point):
        # show context menu
        row = self.scenes_listWidget.currentRow()
        if row == -1:
            return
        # check paths
        manager = self._getManager()
        self.scenes_rcItem_1.setEnabled(os.path.isdir(manager.currentBaseScenePath))
        self.scenes_rcItem_2.setEnabled(os.path.isdir(manager.currentPreviewPath))
        self.scenes_rcItem_5.setEnabled(os.path.isdir(os.path.join(self.manager.projectDir, "images", manager.currentBaseSceneName)))
        self.popMenu_scenes.exec_(self.scenes_listWidget.mapToGlobal(point))

    def rcAction_scenes(self, command):
        manager = self._getManager()
        if not manager:
            return

        if command == "showInExplorerMaya":
            manager.showInExplorer(manager.currentBaseScenePath)

        if command == "showInExplorerPB":
            manager.showInExplorer(manager.currentPreviewPath)

        if command == "showInExplorerData":
            filePath = manager._baseScenesInCategory[manager.currentBaseSceneName]
            dirPath = os.path.dirname(filePath)
            manager.showInExplorer(dirPath)

        if command == "showSceneInfo":
            textInfo = pprint.pformat(manager._currentSceneInfo)
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
            messageLayout.addWidget(helpText)

        if command == "viewRender":
            imagePath = os.path.join(self.manager.projectDir, "images", manager.currentBaseSceneName)
            ImageViewer.MainUI(self.manager.projectDir, relativePath=imagePath, recursive=True).show()

    def onSoftwareChange(self):

        self.manager.currentSwIndex = self.software_comboBox.currentIndex()
        #
        self._initCategories()
        self._initSubProjects()
        self.populateBaseScenes()
        self.software_comboBox.setStyleSheet("background-color: %s; color: black" %self.swColorDict[str(self.software_comboBox.currentText())])
        self.version_comboBox.setStyleSheet("background-color: rgb(80,80,80); color: white")
        self._vEnableDisable()
        manager = self._getManager()
        if manager.niceName == "Houdini":
            self.makeReference_pushButton.setVisible(False)
        else:
            self.makeReference_pushButton.setVisible(True)

    def onSubProjectChange(self):
        manager = self._getManager()


        manager.currentSubIndex = self.subProject_comboBox.currentIndex()
        self.onCategoryChange()

    def onCategoryChange(self):
        manager = self._getManager()


        manager.currentTabIndex = self.category_tabWidget.currentIndex()
        self.populateBaseScenes()
        self.onBaseSceneChange()

    def onUserChange(self):
        manager = self._getManager()
        manager.currentUser = str(self.user_comboBox.currentText())

    def onBaseSceneChange(self):
        self.version_comboBox.blockSignals(True)

        manager = self._getManager()
        #clear version_combobox
        self.version_comboBox.clear()

        row = self.scenes_listWidget.currentRow()
        if row == -1:
            manager.currentBaseSceneName = ""

        else:
            manager.currentBaseSceneName = str(self.scenes_listWidget.currentItem().text())

        self._vEnableDisable()
        #get versions and add it to the combobox
        versionData = manager.getVersions()
        for num in range(len(versionData)):
            self.version_comboBox.addItem("v{0}".format(str(num + 1).zfill(3)))
        self.version_comboBox.setCurrentIndex(manager.currentVersionIndex-1)
        self.onVersionChange()

        self.version_comboBox.blockSignals(False)

    def onVersionChange(self):

        manager = self._getManager()
        self.version_comboBox.blockSignals(True)

        if self.version_comboBox.currentIndex() is not -1:
            manager.currentVersionIndex = self.version_comboBox.currentIndex() + 1

        # clear Notes and verison combobox
        self.notes_textEdit.clear()

        # update notes
        self.notes_textEdit.setPlainText(manager.getNotes())

        # update thumb
        self.tPixmap = QtGui.QPixmap(manager.getThumbnail())
        self.thumbnail_label.setPixmap(self.tPixmap)

        if manager.currentVersionIndex != len(manager.getVersions()) and manager.currentVersionIndex != -1:
            self.version_comboBox.setStyleSheet("background-color: rgb(80,80,80); color: yellow")
        else:
            self.version_comboBox.setStyleSheet("background-color: rgb(80,80,80); color: white")

        self.version_comboBox.blockSignals(False)

    def onLoadScene(self):
        if self.scenes_listWidget.currentRow() == -1:
            return
        manager = self._getManager()
        if not manager:
            return
        manager.executeScene()

    def onMakeReference(self):
        manager = self._getManager()

        manager.makeReference()
        self.onVersionChange()
        self.statusBar().showMessage(
            "Status | Version {1} is the new reference of {0}".format(manager.currentBaseSceneName, manager.currentVersionIndex))
        currentRow = self.scenes_listWidget.currentRow()
        self.populateBaseScenes()
        self.scenes_listWidget.setCurrentRow(currentRow)

    def onShowPreview(self):
        row = self.scenes_listWidget.currentRow()
        if row == -1:
            return

        manager = self._getManager()

        cameraList = manager.getPreviews()
        if len(manager.getPreviews()) == 1:
            manager.playPreview(cameraList[0])
        else:
            zortMenu = QtWidgets.QMenu()
            for z in cameraList:
                tempAction = QtWidgets.QAction(z, self)
                zortMenu.addAction(tempAction)
                tempAction.triggered.connect(lambda item=z: manager.playPreview(item)) ## Take note about the usage of lambda "item=pbDict[z]" makes it possible using the loop

            zortMenu.exec_((QtGui.QCursor.pos()))

    def onDeleteBaseScene(self):
        passw, ok = QtWidgets.QInputDialog.getText(self, "!!!DELETING BASE SCENE!!! %s\n\nAre you absolutely sure?", "Enter Admin Password:", QtWidgets.QLineEdit.Password)

        if ok:
            if self.manager.checkPassword(passw):
                pass
            else:
                self.infoPop(textTitle="Incorrect Password", textHeader="The Password is invalid")
                return
        else:
            return

        manager = self._getManager()

        name = manager.currentBaseSceneName

        row = self.scenes_listWidget.currentRow()
        if not row == -1:
            manager.deleteBasescene(manager.currentDatabasePath)
            self.populateBaseScenes()
            self.statusBar().showMessage("Status | Scene Deleted => %s" % name)

    def onDeleteReference(self):
        passw, ok = QtWidgets.QInputDialog.getText(self, "DELETING Reference File of %s\n\nAre you sure?", "Enter Admin Password:", QtWidgets.QLineEdit.Password)

        if ok:
            if self.manager.checkPassword(passw):
                pass
            else:
                self.infoPop(textTitle="Incorrect Password", textHeader="The Password is invalid")
                return
        else:
            return


        manager = self._getManager()

        name = manager.currentBaseSceneName

        row = self.scenes_listWidget.currentRow()
        if not row == -1:
            manager.deleteReference(manager.currentDatabasePath)
            self.populateBaseScenes()
            self.statusBar().showMessage("Status | Reference of %s is deleted" % name)

    def populateBaseScenes(self, deepCheck=False):
        self.scenes_listWidget.blockSignals(True)

        manager = self._getManager()
        if not manager:
            return

        self.scenes_listWidget.clear()
        baseScenesDict = manager.getBaseScenesInCategory()

        codeDict = {-1: QtGui.QColor(255, 0, 0, 255), 1: QtGui.QColor(0, 255, 0, 255),
                    0: QtGui.QColor(255, 255, 0, 255), -2: QtGui.QColor(20, 20, 20, 255)}  # dictionary for color codes red, green, yellow
                    # gray for the corrupted database file

        for key in sorted(baseScenesDict):
            retCode = manager.checkReference(baseScenesDict[key], deepCheck=deepCheck) # returns -1, 0, 1 or -2 for color ref
            color = codeDict[retCode]
            listItem = QtWidgets.QListWidgetItem()
            listItem.setText(key)
            listItem.setForeground(color)
            self.scenes_listWidget.addItem(listItem)
        self.scenes_listWidget.blockSignals(False)

    def _initCategories(self):
        self.category_tabWidget.blockSignals(True)


        manager = self._getManager()
        if not manager:
            return

        self.category_tabWidget.clear()

        for i in manager._categories:
            self.preTab = QtWidgets.QWidget()
            self.preTab.setObjectName((i))
            self.category_tabWidget.addTab(self.preTab, (i))

        self.category_tabWidget.setCurrentIndex(manager.currentTabIndex)
        self.category_tabWidget.blockSignals(False)

    def _initUsers(self):
        self.user_comboBox.blockSignals(True)

        manager = self._getManager()
        if not manager:
            return
        # init users
        self.user_comboBox.clear()
        self.user_comboBox.addItems(manager.getUsers())
        index = self.user_comboBox.findText(manager.currentUser, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.user_comboBox.setCurrentIndex(index)

        self.user_comboBox.blockSignals(False)

    def _initSubProjects(self):

        self.subProject_comboBox.blockSignals(True)

        manager = self._getManager()
        if not manager:
            return

        self.subProject_comboBox.clear()
        self.subProject_comboBox.addItems(manager.getSubProjects())
        self.subProject_comboBox.setCurrentIndex(manager.currentSubIndex)

        self.subProject_comboBox.blockSignals(False)

    def _vEnableDisable(self):
        manager = self._getManager()
        if not manager:
            return

        if  manager.currentBaseSceneName:
            self.version_comboBox.setEnabled(True)
            if manager.getPreviews():
                self.showPreview_pushButton.setEnabled(True)
            else:
                self.showPreview_pushButton.setEnabled(False)
            self.makeReference_pushButton.setEnabled(True)
            self.addNote_pushButton.setEnabled(True)
            self.version_label.setEnabled(True)

        else:
            self.version_comboBox.setEnabled(False)
            self.showPreview_pushButton.setEnabled(False)
            self.makeReference_pushButton.setEnabled(False)
            self.addNote_pushButton.setEnabled(False)
            self.version_label.setEnabled(False)




if __name__ == '__main__':
    selfLoc = os.path.dirname(os.path.abspath(__file__))
    stylesheetFile = os.path.join(selfLoc, "CSS", "darkorange.stylesheet")

    app = QtWidgets.QApplication(sys.argv)
    with open(stylesheetFile, "r") as fh:
        app.setStyleSheet(fh.read())
    window = MainUI()
    window.show()
    # window.changePasswordUI()
    sys.exit(app.exec_())
