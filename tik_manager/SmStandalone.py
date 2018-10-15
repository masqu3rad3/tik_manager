import os
import SmRoot
reload(SmRoot)
from SmRoot import RootManager
from PyQt4 import QtCore, QtGui, Qt

import _version

import json
import sys, os
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

    # def setProject(self, path):


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
                            "userSettingsDir": "SceneManager\\Maya"}]

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
        # logger.debug("Func: setProject")
        # self.currentProject = path
        # # totally software specific or N/A
        #
        # # self.projectDir = cmds.workspace(q=1, rd=1)
        projectsDict = self._loadProjects()
        if not projectsDict:
            projectsDict = {"StandaloneProject": path}
        else:
            projectsDict["StandaloneProject"] = path
        self._saveProjects(projectsDict)
        self.projectDir = path


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



    # @property
    # def currentSoftware(self):
    #     """returns current sofware"""
    #     pass

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



class MainUI(QtGui.QMainWindow):
    def __init__(self):
        super(MainUI, self).__init__()

        self.masterManager = StandaloneManager()
        # self.tempCategories = ["Model", "Rig", "Shading", "Layout", "Animation", "Render", "Other"]

        self.setObjectName(SM_Version)
        self.resize(680, 600)
        self.setWindowTitle(SM_Version)
        self.centralwidget = QtGui.QWidget(self)

        self.buildUI(self)

        self.setCentralWidget(self.centralwidget)

        self.initMainUI(newborn=True)

    def buildUI(self):

        self.main_gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.main_gridLayout.setObjectName(("main_gridLayout"))

        self.main_horizontalLayout = QtGui.QHBoxLayout()
        self.main_horizontalLayout.setContentsMargins(-1, -1, 0, -1)
        self.main_horizontalLayout.setSpacing(6)
        self.main_horizontalLayout.setObjectName(("horizontalLayout"))
        self.main_horizontalLayout.setStretch(0, 1)

        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.main_horizontalLayout.addItem(spacerItem)

        self.loadScene_pushButton = QtGui.QPushButton(self.centralwidget)
        self.loadScene_pushButton.setMinimumSize(QtCore.QSize(150, 45))
        self.loadScene_pushButton.setMaximumSize(QtCore.QSize(150, 45))
        self.loadScene_pushButton.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.loadScene_pushButton.setText(("Load Scene"))
        self.loadScene_pushButton.setObjectName(("loadScene_pushButton"))
        self.main_horizontalLayout.addWidget(self.loadScene_pushButton)
        #
        self.main_gridLayout.addLayout(self.main_horizontalLayout, 4, 0, 1, 1)
        #
        self.r2_gridLayout = QtGui.QGridLayout()
        self.r2_gridLayout.setObjectName(("r2_gridLayout"))
        self.r2_gridLayout.setColumnStretch(1, 1)

        self.subProject_label = QtGui.QLabel(self.centralwidget)
        self.subProject_label.setText(("Sub-Project:"))
        self.subProject_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.subProject_label.setObjectName(("subProject_label"))
        self.r2_gridLayout.addWidget(self.subProject_label, 0, 2, 1, 1)

        self.subProject_comboBox = QtGui.QComboBox(self.centralwidget)
        self.subProject_comboBox.setMinimumSize(QtCore.QSize(150, 30))
        self.subProject_comboBox.setMaximumSize(QtCore.QSize(16777215, 30))
        self.subProject_comboBox.setObjectName(("subProject_comboBox"))
        self.r2_gridLayout.addWidget(self.subProject_comboBox, 0, 3, 1, 1)

        self.addSubProject_pushButton = QtGui.QPushButton(self.centralwidget)
        self.addSubProject_pushButton.setMinimumSize(QtCore.QSize(30, 30))
        self.addSubProject_pushButton.setMaximumSize(QtCore.QSize(30, 30))
        self.addSubProject_pushButton.setText(("+"))
        self.addSubProject_pushButton.setObjectName(("addSubProject_pushButton"))
        self.r2_gridLayout.addWidget(self.addSubProject_pushButton, 0, 4, 1, 1)

        self.user_label = QtGui.QLabel(self.centralwidget)
        self.user_label.setText(("User:"))
        self.user_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.user_label.setObjectName(("user_label"))
        self.r2_gridLayout.addWidget(self.user_label, 0, 5, 1, 1)

        self.user_comboBox = QtGui.QComboBox(self.centralwidget)
        self.user_comboBox.setMinimumSize(QtCore.QSize(130, 30))
        self.user_comboBox.setMaximumSize(QtCore.QSize(16777215, 30))
        self.user_comboBox.setObjectName(("user_comboBox"))
        self.r2_gridLayout.addWidget(self.user_comboBox, 0, 6, 1, 1)

        self.main_gridLayout.addLayout(self.r2_gridLayout, 1, 0, 1, 1)
        self.r1_gridLayout = QtGui.QGridLayout()
        self.r1_gridLayout.setObjectName(("r1_gridLayout"))

        self.project_label = QtGui.QLabel(self.centralwidget)
        self.project_label.setText(("Project:"))
        self.project_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.project_label.setObjectName(("project_label"))
        self.r1_gridLayout.addWidget(self.project_label, 1, 0, 1, 1)

        self.project_lineEdit = QtGui.QLineEdit(self.centralwidget)
        self.project_lineEdit.setText((""))
        self.project_lineEdit.setPlaceholderText((""))
        self.project_lineEdit.setObjectName(("project_lineEdit"))
        self.project_lineEdit.setReadOnly(True)
        self.r1_gridLayout.addWidget(self.project_lineEdit, 1, 1, 1, 1)

        self.setProject_pushButton = QtGui.QPushButton(self.centralwidget)
        self.setProject_pushButton.setText(("SET"))
        self.setProject_pushButton.setObjectName(("setProject_pushButton"))
        self.r1_gridLayout.addWidget(self.setProject_pushButton, 1, 2, 1, 1)

        self.main_gridLayout.addLayout(self.r1_gridLayout, 0, 0, 1, 1)

        self.category_tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.category_tabWidget.setMaximumSize(QtCore.QSize(16777215, 20))
        self.category_tabWidget.setTabPosition(QtGui.QTabWidget.North)
        self.category_tabWidget.setElideMode(QtCore.Qt.ElideNone)
        self.category_tabWidget.setUsesScrollButtons(False)
        self.category_tabWidget.setObjectName(("tabWidget"))

        # for i in self.manager._categories:
        #     self.preTab = QtGui.QWidget()
        #     self.preTab.setObjectName((i))
        #     self.category_tabWidget.addTab(self.preTab, (i))

        self.category_tabWidget.setCurrentIndex(self.masterManager.currentTabIndex)

        self.main_gridLayout.addWidget(self.category_tabWidget, 2, 0, 1, 1)

        self.splitter = QtGui.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(("splitter"))


        self.scenes_listWidget = QtGui.QListWidget(self.splitter)
        self.scenes_listWidget.setObjectName(("listWidget"))

        self.frame = QtGui.QFrame(self.splitter)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(("frame"))

        self.gridLayout_6 = QtGui.QGridLayout(self.frame)
        self.gridLayout_6.setContentsMargins(-1, -1, 0, 0)
        self.gridLayout_6.setObjectName(("gridLayout_6"))

        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(("verticalLayout"))

        self.notes_label = QtGui.QLabel(self.frame)
        self.notes_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.notes_label.setText(("Version Notes:"))
        self.notes_label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.notes_label.setObjectName(("version_label_2"))
        self.verticalLayout.addWidget(self.notes_label)

        self.notes_textEdit = QtGui.QTextEdit(self.frame)
        self.notes_textEdit.setObjectName(("textEdit"))
        self.notes_textEdit.setReadOnly(True)
        self.verticalLayout.addWidget(self.notes_textEdit)

        self.tPixmap = QtGui.QPixmap("")
        self.thumbnail_label = ImageWidget(self.frame)
        self.thumbnail_label.setPixmap(self.tPixmap)

        self.thumbnail_label.setMinimumSize(QtCore.QSize(221, 124))
        self.thumbnail_label.setFrameShape(QtGui.QFrame.Box)
        self.thumbnail_label.setScaledContents(True)
        self.thumbnail_label.setAlignment(QtCore.Qt.AlignCenter)
        self.thumbnail_label.setObjectName(("label"))
        self.verticalLayout.addWidget(self.thumbnail_label)

        self.gridLayout_6.addLayout(self.verticalLayout, 3, 0, 1, 1)

        self.gridLayout_7 = QtGui.QGridLayout()
        self.gridLayout_7.setContentsMargins(-1, -1, 10, 10)
        self.gridLayout_7.setObjectName(("gridLayout_7"))

        self.showPreview_pushButton = QtGui.QPushButton(self.frame)
        self.showPreview_pushButton.setMinimumSize(QtCore.QSize(100, 30))
        self.showPreview_pushButton.setMaximumSize(QtCore.QSize(150, 30))
        self.showPreview_pushButton.setText(("Show Preview"))
        self.showPreview_pushButton.setObjectName(("setProject_pushButton_5"))
        self.gridLayout_7.addWidget(self.showPreview_pushButton, 0, 3, 1, 1)

        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setSpacing(1)
        self.horizontalLayout_4.setObjectName(("horizontalLayout_4"))

        self.version_label = QtGui.QLabel(self.frame)
        self.version_label.setMinimumSize(QtCore.QSize(60, 30))
        self.version_label.setMaximumSize(QtCore.QSize(60, 30))
        self.version_label.setFrameShape(QtGui.QFrame.Box)
        self.version_label.setText(("Version:"))
        self.version_label.setAlignment(QtCore.Qt.AlignCenter)
        self.version_label.setObjectName(("version_label"))
        self.horizontalLayout_4.addWidget(self.version_label)

        self.version_comboBox = QtGui.QComboBox(self.frame)
        self.version_comboBox.setMinimumSize(QtCore.QSize(60, 30))
        self.version_comboBox.setMaximumSize(QtCore.QSize(100, 30))
        self.version_comboBox.setObjectName(("version_comboBox"))
        self.horizontalLayout_4.addWidget(self.version_comboBox)

        self.gridLayout_7.addLayout(self.horizontalLayout_4, 0, 0, 1, 1)

        self.makeReference_pushButton = QtGui.QPushButton(self.frame)
        self.makeReference_pushButton.setMinimumSize(QtCore.QSize(100, 30))
        self.makeReference_pushButton.setMaximumSize(QtCore.QSize(300, 30))
        self.makeReference_pushButton.setText(("Make Reference"))
        self.makeReference_pushButton.setObjectName(("makeReference_pushButton"))
        self.gridLayout_7.addWidget(self.makeReference_pushButton, 1, 0, 1, 1)

        self.addNote_pushButton = QtGui.QPushButton(self.frame)
        self.addNote_pushButton.setMinimumSize(QtCore.QSize(100, 30))
        self.addNote_pushButton.setMaximumSize(QtCore.QSize(150, 30))
        self.addNote_pushButton.setToolTip((""))
        self.addNote_pushButton.setStatusTip((""))
        self.addNote_pushButton.setWhatsThis((""))
        self.addNote_pushButton.setAccessibleName((""))
        self.addNote_pushButton.setAccessibleDescription((""))
        self.addNote_pushButton.setText(("Add Note"))
        self.addNote_pushButton.setObjectName(("addNote_pushButton"))
        self.gridLayout_7.addWidget(self.addNote_pushButton, 1, 3, 1, 1)

        self.gridLayout_6.addLayout(self.gridLayout_7, 0, 0, 1, 1)

        self.main_gridLayout.addWidget(self.splitter, 3, 0, 1, 1)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        self.splitter.setSizePolicy(sizePolicy)

        self.splitter.setStretchFactor(0, 1)

        self.menubar = QtGui.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 680, 18))
        self.menubar.setObjectName(("menubar"))

        self.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(self)
        self.statusbar.setObjectName(("statusbar"))
        self.setStatusBar(self.statusbar)

        # MENU BAR / STATUS BAR
        # ---------------------
        file = self.menubar.addMenu("File")
        loadReferenceScene_fm = QtGui.QAction("&Load/Reference Scene", self)
        createProject_fm = QtGui.QAction("&Create Project", self)
        add_remove_users_fm = QtGui.QAction("&Add/Remove Users", self)
        add_remove_categories_fm = QtGui.QAction("&Add/Remove Categories", self)

        deleteFile_fm = QtGui.QAction("&Delete Selected Base Scene", self)
        deleteReference_fm = QtGui.QAction("&Delete Reference of Selected Scene", self)
        reBuildDatabase_fm = QtGui.QAction("&Re-build Project Database", self)
        projectReport_fm = QtGui.QAction("&Project Report", self)
        checkReferences_fm = QtGui.QAction("&Check References", self)

        #load
        file.addSeparator()
        file.addAction(loadReferenceScene_fm)

        #settings
        file.addSeparator()
        file.addAction(add_remove_users_fm)
        file.addAction(add_remove_categories_fm)

        #delete
        file.addSeparator()
        file.addAction(deleteFile_fm)
        file.addAction(deleteReference_fm)

        #misc
        file.addSeparator()
        file.addAction(projectReport_fm)
        file.addAction(checkReferences_fm)

        # RIGHT CLICK MENUS
        # -----------------

        # List Widget Right Click Menu
        self.scenes_listWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.scenes_listWidget.customContextMenuRequested.connect(self.onContextMenu_scenes)
        self.popMenu_scenes = QtGui.QMenu()

        self.scenes_rcItem_0 = QtGui.QAction('Import Scene', self)
        self.popMenu_scenes.addAction(self.scenes_rcItem_0)
        self.scenes_rcItem_0.triggered.connect(lambda: self.rcAction_scenes("importScene"))

        self.scenes_rcItem_1 = QtGui.QAction('Show Maya Folder in Explorer', self)
        self.popMenu_scenes.addAction(self.scenes_rcItem_1)
        self.scenes_rcItem_1.triggered.connect(lambda: self.rcAction_scenes("showInExplorerMaya"))

        self.scenes_rcItem_2 = QtGui.QAction('Show Playblast Folder in Explorer', self)
        self.popMenu_scenes.addAction(self.scenes_rcItem_2)
        self.scenes_rcItem_2.triggered.connect(lambda: self.rcAction_scenes("showInExplorerPB"))

        self.scenes_rcItem_3 = QtGui.QAction('Show Data Folder in Explorer', self)
        self.popMenu_scenes.addAction(self.scenes_rcItem_3)
        self.scenes_rcItem_3.triggered.connect(lambda: self.rcAction_scenes("showInExplorerData"))

        self.popMenu_scenes.addSeparator()
        self.scenes_rcItem_4 = QtGui.QAction('Scene Info', self)
        self.popMenu_scenes.addAction(self.scenes_rcItem_4)
        self.scenes_rcItem_4.triggered.connect(lambda: self.rcAction_scenes("showSceneInfo"))

        # Thumbnail Right Click Menu
        self.thumbnail_label.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.thumbnail_label.customContextMenuRequested.connect(self.onContextMenu_thumbnail)
        self.popMenu_thumbnail = QtGui.QMenu()

        rcAction_thumb_0 = QtGui.QAction('Replace with current view', self)
        self.popMenu_thumbnail.addAction(rcAction_thumb_0)
        rcAction_thumb_0.triggered.connect(lambda: self.rcAction_thumb("currentView"))


        rcAction_thumb_1 = QtGui.QAction('Replace with external file', self)
        self.popMenu_thumbnail.addAction(rcAction_thumb_1)
        rcAction_thumb_1.triggered.connect(lambda: self.rcAction_thumb("file"))


        # SHORTCUTS
        # ---------
        # shortcutRefresh = Qt.QShortcut(Qt.QKeySequence("F5"), self, self.refresh)

        # SIGNAL CONNECTIONS
        # ------------------

        createProject_fm.triggered.connect(self.createProjectUI)

        add_remove_users_fm.triggered.connect(self.addRemoveUserUI)
        add_remove_categories_fm.triggered.connect(self.addRemoveCategoryUI)


        deleteFile_fm.triggered.connect(self.onDeleteBaseScene)

        deleteReference_fm.triggered.connect(self.onDeleteReference)

        checkReferences_fm.triggered.connect(lambda: self.populateBaseScenes(deepCheck=True))

        self.statusBar().showMessage("Status | Idle")

        self.load_radioButton.clicked.connect(self.onModeChange)

        self.category_tabWidget.currentChanged.connect(self.onCategoryChange)

        self.scenes_listWidget.currentItemChanged.connect(self.onBaseSceneChange)

        self.version_comboBox.activated.connect(self.onVersionChange)

        self.makeReference_pushButton.clicked.connect(self.onMakeReference)

        self.subProject_comboBox.activated.connect(self.onSubProjectChange)

        self.user_comboBox.activated.connect(self.onUserChange)

        self.showPreview_pushButton.clicked.connect(self.onShowPreview)

        self.addSubProject_pushButton.clicked.connect(self.createSubProjectUI)

        self.setProject_pushButton.clicked.connect(self.setProjectUI)

        self.scenes_listWidget.doubleClicked.connect(self.onLoadScene)
        self.loadScene_pushButton.clicked.connect(self.onLoadScene)

        self.addNote_pushButton.clicked.connect(self.addNoteDialog)

    # def setupUi(self, sceneManager_MainWindow):
    #     sceneManager_MainWindow.setObjectName(("sceneManager_MainWindow"))
    #     sceneManager_MainWindow.setCentralWidget(self.centralwidget)
    #
    #     self.centralwidget = QtGui.QWidget(sceneManager_MainWindow)
    #     self.centralwidget.setObjectName(("centralwidget"))
    #
    #     self.main_gridLayout = QtGui.QGridLayout(self.centralwidget)
    #     self.main_gridLayout.setObjectName(("main_gridLayout"))
    #
    #     self.main_horizontalLayout = QtGui.QHBoxLayout()
    #     self.main_horizontalLayout.setContentsMargins(-1, -1, 0, -1)
    #     self.main_horizontalLayout.setSpacing(6)
    #     self.main_horizontalLayout.setObjectName(("horizontalLayout"))
    #     self.main_horizontalLayout.setStretch(0, 1)
    #
    #     # self.saveVersion_pushButton = QtGui.QPushButton(self.centralwidget)
    #     # self.saveVersion_pushButton.setMinimumSize(QtCore.QSize(150, 45))
    #     # self.saveVersion_pushButton.setMaximumSize(QtCore.QSize(150, 45))
    #     # self.saveVersion_pushButton.setText(("Save As Version"))
    #     # self.saveVersion_pushButton.setObjectName(("saveVersion_pushButton"))
    #     # self.main_horizontalLayout.addWidget(self.saveVersion_pushButton)
    #     #
    #     # self.saveBaseScene_pushButton = QtGui.QPushButton(self.centralwidget)
    #     # self.saveBaseScene_pushButton.setMinimumSize(QtCore.QSize(150, 45))
    #     # self.saveBaseScene_pushButton.setMaximumSize(QtCore.QSize(150, 45))
    #     # self.saveBaseScene_pushButton.setText(("Save Base Scene"))
    #     # self.saveBaseScene_pushButton.setObjectName(("saveBaseScene_pushButton"))
    #     # self.main_horizontalLayout.addWidget(self.saveBaseScene_pushButton)
    #
    #     spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
    #     self.main_horizontalLayout.addItem(spacerItem)
    #
    #     self.loadScene_pushButton = QtGui.QPushButton(self.centralwidget)
    #     self.loadScene_pushButton.setMinimumSize(QtCore.QSize(150, 45))
    #     self.loadScene_pushButton.setMaximumSize(QtCore.QSize(150, 45))
    #     self.loadScene_pushButton.setLayoutDirection(QtCore.Qt.LeftToRight)
    #     self.loadScene_pushButton.setText(("Load Scene"))
    #     self.loadScene_pushButton.setObjectName(("loadScene_pushButton"))
    #     self.main_horizontalLayout.addWidget(self.loadScene_pushButton)
    #
    #     self.main_gridLayout.addLayout(self.main_horizontalLayout, 4, 0, 1, 1)
    #
    #     self.r2_gridLayout = QtGui.QGridLayout()
    #     self.r2_gridLayout.setObjectName(("r2_gridLayout"))
    #     self.r2_gridLayout.setColumnStretch(1, 1)
    #
    #     # self.load_radioButton = QtGui.QRadioButton(self.centralwidget)
    #     # self.load_radioButton.setText(("Load Mode"))
    #     # self.load_radioButton.setChecked(False)
    #     # self.load_radioButton.setObjectName(("load_radioButton"))
    #     # self.r2_gridLayout.addWidget(self.load_radioButton, 0, 0, 1, 1)
    #
    #     self.subProject_label = QtGui.QLabel(self.centralwidget)
    #     self.subProject_label.setText(("Sub-Project:"))
    #     self.subProject_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
    #     self.subProject_label.setObjectName(("subProject_label"))
    #     self.r2_gridLayout.addWidget(self.subProject_label, 0, 2, 1, 1)
    #
    #     self.subProject_comboBox = QtGui.QComboBox(self.centralwidget)
    #     self.subProject_comboBox.setMinimumSize(QtCore.QSize(150, 30))
    #     self.subProject_comboBox.setMaximumSize(QtCore.QSize(16777215, 30))
    #     self.subProject_comboBox.setObjectName(("subProject_comboBox"))
    #     self.r2_gridLayout.addWidget(self.subProject_comboBox, 0, 3, 1, 1)
    #
    #     # self.reference_radioButton = QtGui.QRadioButton(self.centralwidget)
    #     # self.reference_radioButton.setText(("Reference Mode"))
    #     # self.reference_radioButton.setChecked(True)
    #     # self.reference_radioButton.setObjectName(("reference_radioButton"))
    #     # self.r2_gridLayout.addWidget(self.reference_radioButton, 0, 1, 1, 1)
    #
    #     self.addSubProject_pushButton = QtGui.QPushButton(self.centralwidget)
    #     self.addSubProject_pushButton.setMinimumSize(QtCore.QSize(30, 30))
    #     self.addSubProject_pushButton.setMaximumSize(QtCore.QSize(30, 30))
    #     self.addSubProject_pushButton.setText(("+"))
    #     self.addSubProject_pushButton.setObjectName(("addSubProject_pushButton"))
    #     self.r2_gridLayout.addWidget(self.addSubProject_pushButton, 0, 4, 1, 1)
    #
    #     self.user_label = QtGui.QLabel(self.centralwidget)
    #     self.user_label.setText(("User:"))
    #     self.user_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
    #     self.user_label.setObjectName(("user_label"))
    #     self.r2_gridLayout.addWidget(self.user_label, 0, 5, 1, 1)
    #
    #     self.user_comboBox = QtGui.QComboBox(self.centralwidget)
    #     self.user_comboBox.setMinimumSize(QtCore.QSize(130, 30))
    #     self.user_comboBox.setMaximumSize(QtCore.QSize(16777215, 30))
    #     self.user_comboBox.setObjectName(("user_comboBox"))
    #     self.r2_gridLayout.addWidget(self.user_comboBox, 0, 6, 1, 1)
    #
    #     self.main_gridLayout.addLayout(self.r2_gridLayout, 1, 0, 1, 1)
    #     self.r1_gridLayout = QtGui.QGridLayout()
    #     self.r1_gridLayout.setObjectName(("gridLayout"))
    #
    #     self.baseScene_label = QtGui.QLabel(self.centralwidget)
    #     self.baseScene_label.setLayoutDirection(QtCore.Qt.LeftToRight)
    #     self.baseScene_label.setText(("Base Scene:"))
    #     self.baseScene_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
    #     self.baseScene_label.setObjectName(("baseScene_label"))
    #     self.r1_gridLayout.addWidget(self.baseScene_label, 0, 0, 1, 1)
    #
    #     self.baseScene_lineEdit = QtGui.QLineEdit(self.centralwidget)
    #     self.baseScene_lineEdit.setText((""))
    #     self.baseScene_lineEdit.setPlaceholderText((""))
    #     self.baseScene_lineEdit.setObjectName(("baseScene_lineEdit"))
    #     self.r1_gridLayout.addWidget(self.baseScene_lineEdit, 0, 1, 1, 1)
    #
    #     self.project_label = QtGui.QLabel(self.centralwidget)
    #     self.project_label.setText(("Project:"))
    #     self.project_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
    #     self.project_label.setObjectName(("project_label"))
    #     self.r1_gridLayout.addWidget(self.project_label, 1, 0, 1, 1)
    #
    #     self.project_lineEdit = QtGui.QLineEdit(self.centralwidget)
    #     self.project_lineEdit.setText((""))
    #     self.project_lineEdit.setPlaceholderText((""))
    #     self.project_lineEdit.setObjectName(("project_lineEdit"))
    #     self.r1_gridLayout.addWidget(self.project_lineEdit, 1, 1, 1, 1)
    #
    #     self.setProject_pushButton = QtGui.QPushButton(self.centralwidget)
    #     self.setProject_pushButton.setText(("SET"))
    #     self.setProject_pushButton.setObjectName(("setProject_pushButton"))
    #     self.r1_gridLayout.addWidget(self.setProject_pushButton, 1, 2, 1, 1)
    #
    #     self.main_gridLayout.addLayout(self.r1_gridLayout, 0, 0, 1, 1)
    #
    #     self.category_tabWidget = QtGui.QTabWidget(self.centralwidget)
    #     self.category_tabWidget.setMaximumSize(QtCore.QSize(16777215, 22))
    #     self.category_tabWidget.setTabPosition(QtGui.QTabWidget.North)
    #     self.category_tabWidget.setElideMode(QtCore.Qt.ElideNone)
    #     self.category_tabWidget.setUsesScrollButtons(False)
    #     self.category_tabWidget.setObjectName(("tabWidget"))
    #
    #     for i in self.tempCategories:
    #         self.preTab = QtGui.QWidget()
    #         self.preTab.setObjectName((i))
    #         self.category_tabWidget.addTab(self.preTab, (i))
    #
    #     self.main_gridLayout.addWidget(self.category_tabWidget, 2, 0, 1, 1)
    #
    #     self.splitter = QtGui.QSplitter(self.centralwidget)
    #     self.splitter.setOrientation(QtCore.Qt.Horizontal)
    #     self.splitter.setObjectName(("splitter"))
    #
    #
    #     self.scenes_listWidget = QtGui.QListWidget(self.splitter)
    #     self.scenes_listWidget.setObjectName(("listWidget"))
    #
    #     self.frame = QtGui.QFrame(self.splitter)
    #     self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
    #     self.frame.setFrameShadow(QtGui.QFrame.Raised)
    #     self.frame.setObjectName(("frame"))
    #
    #     self.gridLayout_6 = QtGui.QGridLayout(self.frame)
    #     self.gridLayout_6.setContentsMargins(-1, -1, 0, 0)
    #     self.gridLayout_6.setObjectName(("gridLayout_6"))
    #
    #     self.verticalLayout = QtGui.QVBoxLayout()
    #     self.verticalLayout.setObjectName(("verticalLayout"))
    #
    #     self.versionNotes_label = QtGui.QLabel(self.frame)
    #     self.versionNotes_label.setLayoutDirection(QtCore.Qt.LeftToRight)
    #     self.versionNotes_label.setText(("Version Notes:"))
    #     self.versionNotes_label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
    #     self.versionNotes_label.setObjectName(("version_label_2"))
    #     self.verticalLayout.addWidget(self.versionNotes_label)
    #
    #     self.notes_textEdit = QtGui.QTextEdit(self.frame)
    #     self.notes_textEdit.setObjectName(("textEdit"))
    #     self.verticalLayout.addWidget(self.notes_textEdit)
    #
    #     # testFile = os.path.normpath("D:\\PROJECT_AND_ARGE\\testo_testo_testo_180715\\DSC_2179.JPG")
    #     testFile = os.path.normpath("C:\\a.JPG")
    #     self.tPixmap = QtGui.QPixmap((testFile))
    #     # os.startfile(testFile)
    #     self.thumbnail_label = ImageWidget(self.frame)
    #     # self.label = QtGui.QLabel(self.frame)
    #     self.thumbnail_label.setPixmap(self.tPixmap)
    #
    #     # self.label.setPixmap(self.tPixmap.scaledToWidth(self.label.width()))
    #     # sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
    #     # sizePolicy.setHorizontalStretch(0)
    #     # sizePolicy.setVerticalStretch(0)
    #     # sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
    #     # sizePolicy.setHeightForWidth(True)
    #     # self.label.setSizePolicy(sizePolicy)
    #
    #     self.thumbnail_label.setMinimumSize(QtCore.QSize(221, 124))
    #     # self.label.setMaximumSize(QtCore.QSize(884, 496))
    #     # self.label.setSizeIncrement(QtCore.QSize(1, 1))
    #     # self.label.setBaseSize(QtCore.QSize(0, 0))
    #     # self.label.setText(("test"))
    #     self.thumbnail_label.setFrameShape(QtGui.QFrame.Box)
    #     self.thumbnail_label.setScaledContents(True)
    #     self.thumbnail_label.setAlignment(QtCore.Qt.AlignCenter)
    #     self.thumbnail_label.setObjectName(("label"))
    #     self.verticalLayout.addWidget(self.thumbnail_label)
    #
    #     self.gridLayout_6.addLayout(self.verticalLayout, 3, 0, 1, 1)
    #
    #     self.gridLayout_7 = QtGui.QGridLayout()
    #     self.gridLayout_7.setContentsMargins(-1, -1, 10, 10)
    #     self.gridLayout_7.setObjectName(("gridLayout_7"))
    #
    #     self.showPreview_pushButton = QtGui.QPushButton(self.frame)
    #     self.showPreview_pushButton.setMinimumSize(QtCore.QSize(100, 30))
    #     self.showPreview_pushButton.setMaximumSize(QtCore.QSize(150, 30))
    #     self.showPreview_pushButton.setText(("Show Preview"))
    #     self.showPreview_pushButton.setObjectName(("setProject_pushButton_5"))
    #     self.gridLayout_7.addWidget(self.showPreview_pushButton, 0, 3, 1, 1)
    #
    #     self.horizontalLayout_4 = QtGui.QHBoxLayout()
    #     # self.horizontalLayout_4.setMargin(0)
    #     self.horizontalLayout_4.setSpacing(1)
    #     self.horizontalLayout_4.setObjectName(("horizontalLayout_4"))
    #
    #     self.version_label = QtGui.QLabel(self.frame)
    #     self.version_label.setMinimumSize(QtCore.QSize(60, 30))
    #     self.version_label.setMaximumSize(QtCore.QSize(60, 30))
    #     self.version_label.setFrameShape(QtGui.QFrame.Box)
    #     self.version_label.setText(("Version:"))
    #     self.version_label.setAlignment(QtCore.Qt.AlignCenter)
    #     self.version_label.setObjectName(("version_label"))
    #     self.horizontalLayout_4.addWidget(self.version_label)
    #
    #     self.version_comboBox = QtGui.QComboBox(self.frame)
    #     self.version_comboBox.setMinimumSize(QtCore.QSize(60, 30))
    #     self.version_comboBox.setMaximumSize(QtCore.QSize(100, 30))
    #     self.version_comboBox.setObjectName(("version_comboBox"))
    #     self.horizontalLayout_4.addWidget(self.version_comboBox)
    #
    #     self.gridLayout_7.addLayout(self.horizontalLayout_4, 0, 0, 1, 1)
    #
    #     self.makeReference_pushButton = QtGui.QPushButton(self.frame)
    #     self.makeReference_pushButton.setMinimumSize(QtCore.QSize(100, 30))
    #     self.makeReference_pushButton.setMaximumSize(QtCore.QSize(300, 30))
    #     self.makeReference_pushButton.setText(("Make Reference"))
    #     self.makeReference_pushButton.setObjectName(("makeReference_pushButton"))
    #     self.gridLayout_7.addWidget(self.makeReference_pushButton, 1, 0, 1, 1)
    #
    #     self.addNote_pushButton = QtGui.QPushButton(self.frame)
    #     self.addNote_pushButton.setMinimumSize(QtCore.QSize(100, 30))
    #     self.addNote_pushButton.setMaximumSize(QtCore.QSize(150, 30))
    #     self.addNote_pushButton.setToolTip((""))
    #     self.addNote_pushButton.setStatusTip((""))
    #     self.addNote_pushButton.setWhatsThis((""))
    #     self.addNote_pushButton.setAccessibleName((""))
    #     self.addNote_pushButton.setAccessibleDescription((""))
    #     self.addNote_pushButton.setText(("Add Note"))
    #     self.addNote_pushButton.setObjectName(("addNote_pushButton"))
    #     self.gridLayout_7.addWidget(self.addNote_pushButton, 1, 3, 1, 1)
    #
    #     self.gridLayout_6.addLayout(self.gridLayout_7, 0, 0, 1, 1)
    #
    #     self.main_gridLayout.addWidget(self.splitter, 3, 0, 1, 1)
    #
    #     sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
    #     sizePolicy.setHorizontalStretch(1)
    #     sizePolicy.setVerticalStretch(1)
    #     self.splitter.setSizePolicy(sizePolicy)
    #
    #     self.splitter.setStretchFactor(0, 1)
    #
    #     self.menubar = QtGui.QMenuBar(sceneManager_MainWindow)
    #     self.menubar.setGeometry(QtCore.QRect(0, 0, 680, 18))
    #     self.menubar.setObjectName(("menubar"))
    #
    #     sceneManager_MainWindow.setMenuBar(self.menubar)
    #     self.statusbar = QtGui.QStatusBar(sceneManager_MainWindow)
    #     self.statusbar.setObjectName(("statusbar"))
    #     sceneManager_MainWindow.setStatusBar(self.statusbar)
    #
    #     # MENU BAR / STATUS BAR
    #     # ---------------------
    #     file = self.menubar.addMenu("File")
    #     saveVersion_fm = QtGui.QAction("&Save Version", self)
    #     saveBaseScene_fm = QtGui.QAction("&Save Base Scene", self)
    #     loadReferenceScene_fm = QtGui.QAction("&Load/Reference Scene", self)
    #     createProject_fm = QtGui.QAction("&Create Project", self)
    #     pb_settings_fm = QtGui.QAction("&Playblast Settings", self)
    #     add_remove_users_fm = QtGui.QAction("&Add/Remove Users", self)
    #     deleteFile_fm = QtGui.QAction("&Delete Selected Base Scene", self)
    #     deleteReference_fm = QtGui.QAction("&Delete Reference of Selected Scene", self)
    #     reBuildDatabase_fm = QtGui.QAction("&Re-build Project Database", self)
    #     projectReport_fm = QtGui.QAction("&Project Report", self)
    #     checkReferences_fm = QtGui.QAction("&Check References", self)
    #
    #     #save
    #     file.addAction(createProject_fm)
    #     file.addAction(saveVersion_fm)
    #     file.addAction(saveBaseScene_fm)
    #
    #     #load
    #     file.addSeparator()
    #     file.addAction(loadReferenceScene_fm)
    #
    #     #settings
    #     file.addSeparator()
    #     file.addAction(add_remove_users_fm)
    #     file.addAction(pb_settings_fm)
    #
    #     #delete
    #     file.addSeparator()
    #     file.addAction(deleteFile_fm)
    #     file.addAction(deleteReference_fm)
    #
    #     #misc
    #     file.addSeparator()
    #     file.addAction(projectReport_fm)
    #     file.addAction(checkReferences_fm)
    #
    #     tools = self.menubar.addMenu("Tools")
    #     imanager = QtGui.QAction("&Image Manager", self)
    #     iviewer = QtGui.QAction("&Image Viewer", self)
    #     createPB = QtGui.QAction("&Create PlayBlast", self)
    #
    #     tools.addAction(imanager)
    #     tools.addAction(iviewer)
    #     tools.addAction(createPB)
    #
    #     # RIGHT CLICK MENUS
    #     # -----------------
    #
    #     # List Widget Right Click Menu
    #     self.scenes_listWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
    #     self.scenes_listWidget.customContextMenuRequested.connect(self.onContextMenu_scenes)
    #     self.popMenu_scenes = QtGui.QMenu()
    #
    #     scenes_rcAction_0 = QtGui.QAction('Import Scene', self)
    #     self.popMenu_scenes.addAction(scenes_rcAction_0)
    #
    #     scenes_rcAction_1 = QtGui.QAction('Show Maya Folder in Explorer', self)
    #     self.popMenu_scenes.addAction(scenes_rcAction_1)
    #
    #     scenes_rcAction_2 = QtGui.QAction('Show Playblast Folder in Explorer', self)
    #     self.popMenu_scenes.addAction(scenes_rcAction_2)
    #
    #     scenes_rcAction_3 = QtGui.QAction('Show Data Folder in Explorer', self)
    #     self.popMenu_scenes.addAction(scenes_rcAction_3)
    #
    #     self.popMenu_scenes.addSeparator()
    #     scenes_rcAction_4 = QtGui.QAction('Scene Info', self)
    #     self.popMenu_scenes.addAction(scenes_rcAction_4)
    #
    #     # Thumbnail Right Click Menu
    #     self.thumbnail_label.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
    #     self.thumbnail_label.customContextMenuRequested.connect(self.onContextMenu_thumbnail)
    #     self.popMenu_thumbnail = QtGui.QMenu()
    #
    #     thumb_rcAction_0 = QtGui.QAction('Replace with current view', self)
    #     self.popMenu_thumbnail.addAction(thumb_rcAction_0)
    #
    #     thumb_rcAction_1 = QtGui.QAction('Replace with external file', self)
    #     self.popMenu_thumbnail.addAction(thumb_rcAction_1)
    #
    #     # SHORTCUTS
    #     # ---------
    #     # shortcutRefresh = Qt.QShortcut(Qt.QKeySequence("F5"), self, self.refresh)
    #
    #     # SIGNAL CONNECTIONS
    #     # ------------------
    #
    #     self.statusBar().showMessage("Status | Idle")

    def createSubProjectUI(self):

        newSub, ok = QtGui.QInputDialog.getText(self, "Create New Sub-Project", "Enter an unique Sub-Project name:")
        if ok:
            if self.masterManager._nameCheck(newSub):
                self.subProject_comboBox.clear()
                self.subProject_comboBox.addItems(self.masterManager.createSubproject(newSub))
                self.subProject_comboBox.setCurrentIndex(self.masterManager.currentSubIndex)
                self.populateBaseScenes()
            else:
                self.infoPop(textTitle="Naming Error", textHeader="Naming Error",
                             textInfo="Choose an unique name with latin characters without spaces", type="C")

    def createProjectUI(self):

        self.createproject_Dialog = QtGui.QDialog(parent=self)
        self.createproject_Dialog.setObjectName(("createproject_Dialog"))
        self.createproject_Dialog.resize(419, 249)
        self.createproject_Dialog.setWindowTitle(("Create New Project"))

        self.projectroot_label = QtGui.QLabel(self.createproject_Dialog)
        self.projectroot_label.setGeometry(QtCore.QRect(20, 30, 71, 20))
        self.projectroot_label.setText(("Project Path:"))
        self.projectroot_label.setObjectName(("projectpath_label"))

        currentProjects = os.path.abspath(os.path.join(self.masterManager.projectDir, os.pardir))
        self.projectroot_lineEdit = QtGui.QLineEdit(self.createproject_Dialog)
        self.projectroot_lineEdit.setGeometry(QtCore.QRect(90, 30, 241, 21))
        self.projectroot_lineEdit.setText((currentProjects))
        self.projectroot_lineEdit.setObjectName(("projectpath_lineEdit"))

        self.browse_pushButton = QtGui.QPushButton(self.createproject_Dialog)
        self.browse_pushButton.setText(("Browse"))
        self.browse_pushButton.setGeometry(QtCore.QRect(340, 30, 61, 21))
        self.browse_pushButton.setObjectName(("browse_pushButton"))

        self.resolvedpath_label = QtGui.QLabel(self.createproject_Dialog)
        self.resolvedpath_label.setGeometry(QtCore.QRect(20, 70, 381, 21))
        self.resolvedpath_label.setObjectName(("resolvedpath_label"))

        self.brandname_label = QtGui.QLabel(self.createproject_Dialog)
        self.brandname_label.setGeometry(QtCore.QRect(20, 110, 111, 20))
        self.brandname_label.setFrameShape(QtGui.QFrame.Box)
        self.brandname_label.setText(("Brand Name"))
        self.brandname_label.setAlignment(QtCore.Qt.AlignCenter)
        self.brandname_label.setObjectName(("brandname_label"))

        self.projectname_label = QtGui.QLabel(self.createproject_Dialog)
        self.projectname_label.setGeometry(QtCore.QRect(140, 110, 131, 20))
        self.projectname_label.setFrameShape(QtGui.QFrame.Box)
        self.projectname_label.setText(("Project Name"))
        self.projectname_label.setAlignment(QtCore.Qt.AlignCenter)
        self.projectname_label.setObjectName(("projectname_label"))

        self.client_label = QtGui.QLabel(self.createproject_Dialog)
        self.client_label.setGeometry(QtCore.QRect(280, 110, 121, 20))
        self.client_label.setFrameShape(QtGui.QFrame.Box)
        self.client_label.setText(("Client"))
        self.client_label.setAlignment(QtCore.Qt.AlignCenter)
        self.client_label.setObjectName(("client_label"))

        self.brandname_lineEdit = QtGui.QLineEdit(self.createproject_Dialog)
        self.brandname_lineEdit.setGeometry(QtCore.QRect(20, 140, 111, 21))
        self.brandname_lineEdit.setPlaceholderText(("(optional)"))
        self.brandname_lineEdit.setObjectName(("brandname_lineEdit"))

        self.projectname_lineEdit = QtGui.QLineEdit(self.createproject_Dialog)
        self.projectname_lineEdit.setGeometry(QtCore.QRect(140, 140, 131, 21))
        self.projectname_lineEdit.setPlaceholderText(("Mandatory Field"))
        self.projectname_lineEdit.setObjectName(("projectname_lineEdit"))

        self.client_lineEdit = QtGui.QLineEdit(self.createproject_Dialog)
        self.client_lineEdit.setGeometry(QtCore.QRect(280, 140, 121, 21))
        self.client_lineEdit.setPlaceholderText(("Mandatory Field"))
        self.client_lineEdit.setObjectName(("client_lineEdit"))

        self.createproject_buttonBox = QtGui.QDialogButtonBox(self.createproject_Dialog)
        self.createproject_buttonBox.setGeometry(QtCore.QRect(30, 190, 371, 32))
        self.createproject_buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.createproject_buttonBox.setStandardButtons(
            QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        self.createproject_buttonBox.setObjectName(("buttonBox"))

        self.cp_button = self.createproject_buttonBox.button(QtGui.QDialogButtonBox.Ok)
        self.cp_button.setText('Create Project')

        def browseProjectRoot():
            dlg = QtGui.QFileDialog()
            dlg.setFileMode(QtGui.QFileDialog.Directory)

            if dlg.exec_():
                selectedroot = os.path.normpath(dlg.selectedFiles()[0])
                self.projectroot_lineEdit.setText(selectedroot)
                resolve()

        def onCreateNewProject():
            root = self.projectroot_lineEdit.text()
            pName = self.projectname_lineEdit.text()
            bName = self.brandname_lineEdit.text()
            cName = self.client_lineEdit.text()
            pPath = self.masterManager.createNewProject(root, pName, bName, cName)
            self.masterManager.setProject(pPath)
            self.onProjectChange()
            self.createproject_Dialog.close()

        def resolve():
            if self.projectname_lineEdit.text() == "" or self.client_lineEdit.text() == "" or self.projectroot_lineEdit.text() == "":
                self.resolvedpath_label.setText("Fill the mandatory fields")
                self.newProjectPath = None
                return
            resolvedPath = self.masterManager._resolveProjectPath(self.projectroot_lineEdit.text(),
                                                                  self.projectname_lineEdit.text(),
                                                                  self.brandname_lineEdit.text(),
                                                                  self.client_lineEdit.text())
            self.resolvedpath_label.setText(resolvedPath)

        resolve()
        self.browse_pushButton.clicked.connect(browseProjectRoot)

        self.brandname_lineEdit.textEdited.connect(lambda: resolve())
        self.projectname_lineEdit.textEdited.connect(lambda: resolve())
        self.client_lineEdit.textEdited.connect(lambda: resolve())

        self.createproject_buttonBox.accepted.connect(onCreateNewProject)
        self.createproject_buttonBox.rejected.connect(self.createproject_Dialog.reject)

        self.brandname_lineEdit.textChanged.connect(
            lambda: self._checkValidity(self.brandname_lineEdit.text(), self.cp_button,
                                  self.brandname_lineEdit))
        self.projectname_lineEdit.textChanged.connect(
            lambda: self._checkValidity(self.projectname_lineEdit.text(), self.cp_button,
                                  self.projectname_lineEdit))
        self.client_lineEdit.textChanged.connect(
            lambda: self._checkValidity(self.client_lineEdit.text(), self.cp_button, self.client_lineEdit))

        self.createproject_Dialog.show()

    def setProjectUI(self):

        iconFont = QtGui.QFont()
        iconFont.setPointSize(12)
        iconFont.setBold(True)
        iconFont.setWeight(75)

        self.setProject_Dialog = QtGui.QDialog(parent=self)
        self.setProject_Dialog.setObjectName(("setProject_Dialog"))
        self.setProject_Dialog.resize(982, 450)
        self.setProject_Dialog.setWindowTitle(("Set Project"))

        gridLayout = QtGui.QGridLayout(self.setProject_Dialog)
        gridLayout.setObjectName(("gridLayout"))

        M1_horizontalLayout = QtGui.QHBoxLayout()
        M1_horizontalLayout.setObjectName(("M1_horizontalLayout"))

        lookIn_label = QtGui.QLabel(self.setProject_Dialog)
        lookIn_label.setText(("Look in:"))
        lookIn_label.setObjectName(("lookIn_label"))

        M1_horizontalLayout.addWidget(lookIn_label)

        self.lookIn_lineEdit = QtGui.QLineEdit(self.setProject_Dialog)
        self.lookIn_lineEdit.setText((""))
        self.lookIn_lineEdit.setPlaceholderText((""))
        self.lookIn_lineEdit.setObjectName(("lookIn_lineEdit"))

        M1_horizontalLayout.addWidget(self.lookIn_lineEdit)

        browse_pushButton = QtGui.QPushButton(self.setProject_Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(browse_pushButton.sizePolicy().hasHeightForWidth())
        browse_pushButton.setSizePolicy(sizePolicy)
        browse_pushButton.setMaximumSize(QtCore.QSize(50, 16777215))
        browse_pushButton.setText("Browse")
        browse_pushButton.setObjectName(("browse_pushButton"))

        M1_horizontalLayout.addWidget(browse_pushButton)

        self.back_pushButton = QtGui.QPushButton(self.setProject_Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.back_pushButton.sizePolicy().hasHeightForWidth())
        self.back_pushButton.setSizePolicy(sizePolicy)
        self.back_pushButton.setMaximumSize(QtCore.QSize(30, 16777215))
        self.back_pushButton.setFont(iconFont)
        self.back_pushButton.setText(("<"))
        self.back_pushButton.setShortcut((""))
        self.back_pushButton.setObjectName(("back_pushButton"))

        M1_horizontalLayout.addWidget(self.back_pushButton)

        self.forward_pushButton = QtGui.QPushButton(self.setProject_Dialog)
        self.forward_pushButton.setMaximumSize(QtCore.QSize(30, 16777215))
        self.forward_pushButton.setFont(iconFont)
        self.forward_pushButton.setText((">"))
        self.forward_pushButton.setShortcut((""))
        self.forward_pushButton.setObjectName(("forward_pushButton"))

        M1_horizontalLayout.addWidget(self.forward_pushButton)

        up_pushButton = QtGui.QPushButton(self.setProject_Dialog)
        up_pushButton.setMaximumSize(QtCore.QSize(30, 16777215))
        up_pushButton.setText(("Up"))
        up_pushButton.setShortcut((""))
        up_pushButton.setObjectName(("up_pushButton"))

        M1_horizontalLayout.addWidget(up_pushButton)

        gridLayout.addLayout(M1_horizontalLayout, 0, 0, 1, 1)

        M2_horizontalLayout = QtGui.QHBoxLayout()
        M2_horizontalLayout.setObjectName(("M2_horizontalLayout"))

        M2_splitter = QtGui.QSplitter(self.setProject_Dialog)
        M2_splitter.setHandleWidth(10)
        M2_splitter.setObjectName(("M2_splitter"))


        # self.folders_tableView = QtWidgets.QTableView(self.M2_splitter)
        self.folders_tableView = QtGui.QTreeView(M2_splitter)
        self.folders_tableView.setMinimumSize(QtCore.QSize(0, 0))
        self.folders_tableView.setDragEnabled(True)
        self.folders_tableView.setDragDropMode(QtGui.QAbstractItemView.DragOnly)
        self.folders_tableView.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.folders_tableView.setObjectName(("folders_tableView"))

        self.folders_tableView.setFrameShape(QtGui.QFrame.NoFrame)
        self.folders_tableView.setItemsExpandable(False)
        self.folders_tableView.setRootIsDecorated(False)
        self.folders_tableView.setSortingEnabled(True)
        self.folders_tableView.sortByColumn(0, QtCore.Qt.SortOrder.AscendingOrder)


        verticalLayoutWidget = QtGui.QWidget(M2_splitter)
        verticalLayoutWidget.setObjectName(("verticalLayoutWidget"))

        M2_S2_verticalLayout = QtGui.QVBoxLayout(verticalLayoutWidget)
        M2_S2_verticalLayout.setContentsMargins(0, 10, 0, 10)
        M2_S2_verticalLayout.setSpacing(6)
        M2_S2_verticalLayout.setObjectName(("M2_S2_verticalLayout"))

        favorites_label = QtGui.QLabel(verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        favorites_label.setFont(font)
        favorites_label.setText(("Bookmarks:"))
        favorites_label.setObjectName(("favorites_label"))

        M2_S2_verticalLayout.addWidget(favorites_label)

        self.favorites_listWidget = DropListWidget(verticalLayoutWidget)
        self.favorites_listWidget.setAlternatingRowColors(True)
        self.favorites_listWidget.setObjectName(("favorites_listWidget"))

        M2_S2_verticalLayout.addWidget(self.favorites_listWidget)
        M2_S2_horizontalLayout = QtGui.QHBoxLayout()
        M2_S2_horizontalLayout.setObjectName(("M2_S2_horizontalLayout"))

        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)

        M2_S2_horizontalLayout.addItem(spacerItem)

        remove_pushButton = QtGui.QPushButton(verticalLayoutWidget)
        remove_pushButton.setMaximumSize(QtCore.QSize(35, 35))
        remove_pushButton.setFont(iconFont)
        remove_pushButton.setText(("-"))
        remove_pushButton.setObjectName(("remove_pushButton"))

        M2_S2_horizontalLayout.addWidget(remove_pushButton)

        add_pushButton = QtGui.QPushButton(verticalLayoutWidget)
        add_pushButton.setMaximumSize(QtCore.QSize(35, 35))
        add_pushButton.setFont(iconFont)
        add_pushButton.setText(("+"))
        add_pushButton.setObjectName(("add_pushButton"))

        M2_S2_horizontalLayout.addWidget(add_pushButton)

        M2_S2_verticalLayout.addLayout(M2_S2_horizontalLayout)

        M2_horizontalLayout.addWidget(M2_splitter)

        gridLayout.addLayout(M2_horizontalLayout, 1, 0, 1, 1)

        M3_horizontalLayout = QtGui.QHBoxLayout()

        M3_horizontalLayout.setContentsMargins(0, 20, -1, -1)

        M3_horizontalLayout.setObjectName(("M3_horizontalLayout"))

        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)

        M3_horizontalLayout.addItem(spacerItem1)

        cancel_pushButton = QtGui.QPushButton(self.setProject_Dialog)
        cancel_pushButton.setMaximumSize(QtCore.QSize(70, 16777215))
        cancel_pushButton.setText("Cancel")
        cancel_pushButton.setObjectName(("cancel_pushButton"))

        M3_horizontalLayout.addWidget(cancel_pushButton, QtCore.Qt.AlignRight)

        set_pushButton = QtGui.QPushButton(self.setProject_Dialog)
        set_pushButton.setMaximumSize(QtCore.QSize(70, 16777215))
        set_pushButton.setText("Set")
        set_pushButton.setObjectName(("set_pushButton"))

        M3_horizontalLayout.addWidget(set_pushButton, QtCore.Qt.AlignRight)

        gridLayout.addLayout(M3_horizontalLayout, 2, 0, 1, 1)

        verticalLayoutWidget.raise_()

        M2_splitter.setStretchFactor(0,1)

        ## Initial Stuff
        self.projectsRoot = os.path.abspath(os.path.join(self.masterManager.projectDir, os.pardir))
        self.browser = Browse()
        self.spActiveProjectPath = None
        self.__flagView = True

        self.setPmodel = QtGui.QFileSystemModel()
        self.setPmodel.setRootPath(self.projectsRoot)
        self.setPmodel.setFilter(QtCore.QDir.AllDirs | QtCore.QDir.NoDotAndDotDot | QtCore.QDir.Time)

        self.folders_tableView.setModel(self.setPmodel)
        self.folders_tableView.setRootIndex(self.setPmodel.index(self.projectsRoot))
        self.folders_tableView.hideColumn(1)
        self.folders_tableView.hideColumn(2)
        self.folders_tableView.setColumnWidth(0,400)

        self.favList = self.masterManager._loadFavorites()
        self.favorites_listWidget.addItems([x[0] for x in self.favList])

        self.lookIn_lineEdit.setText(self.projectsRoot)

        def navigate(command, index=None):
            if command == "init":
                # feed the initial data
                self.browser.addData(self.projectsRoot)

            if command == "up":
                self.projectsRoot = os.path.abspath(os.path.join(self.projectsRoot, os.pardir))
                self.browser.addData(self.projectsRoot)

            if command == "back":
                self.browser.backward()

            if command == "forward":
                self.browser.forward()

            if command == "browse":
                dir = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory"))
                if dir:
                    self.projectsRoot = dir
                    self.browser.addData(self.projectsRoot)
                else:
                    return

            if command == "folder":
                index = self.folders_tableView.currentIndex()
                self.projectsRoot = os.path.normpath((self.setPmodel.filePath(index)))
                self.browser.addData(self.projectsRoot)

            if command == "lineEnter":
                dir = self.lookIn_lineEdit.text()
                if os.path.isdir(dir):
                    self.projectsRoot = dir
                    self.browser.addData(self.projectsRoot)
                else:
                    self.lookIn_lineEdit.setText(self.projectsRoot)

            self.forward_pushButton.setDisabled(self.browser.isForwardLocked())
            self.back_pushButton.setDisabled(self.browser.isBackwardLocked())
            self.folders_tableView.setRootIndex(self.setPmodel.index(self.browser.getData()))
            self.lookIn_lineEdit.setText(self.browser.getData())

        def onRemoveFavs():

            row = self.favorites_listWidget.currentRow()
            print row
            if row == -1:
                return
            # item = self.favList[row]
            self.favList = self.masterManager._removeFromFavorites(row)
            # block the signal to prevent unwanted cycle

            self.favorites_listWidget.blockSignals(True)
            self.favorites_listWidget.takeItem(row)
            self.favorites_listWidget.blockSignals(False)

        def onAddFavs():
            index = self.folders_tableView.currentIndex()
            if index.row() == -1:  # no row selected, abort
                return
            fullPath = self.setPmodel.filePath(index)
            onDragAndDrop(fullPath)

        def onDragAndDrop(path):
            normPath = os.path.normpath(path)

            path, fName = os.path.split(normPath)
            if [fName, normPath] in self.favList:
                return
            self.favorites_listWidget.addItem(fName)
            self.favList = self.masterManager._addToFavorites(fName, normPath)

        def favoritesActivated():
            # block the signal to prevent unwanted cycle
            self.folders_tableView.selectionModel().blockSignals(True)
            row = self.favorites_listWidget.currentRow()
            self.spActiveProjectPath = self.favList[row][1]

            # clear the selection in folders view
            self.folders_tableView.setCurrentIndex(self.setPmodel.index(self.projectsRoot))
            self.folders_tableView.selectionModel().blockSignals(False)

        def foldersViewActivated():
            # block the signal to prevent unwanted cycle
            self.favorites_listWidget.blockSignals(True)
            index = self.folders_tableView.currentIndex()
            self.spActiveProjectPath = os.path.normpath((self.setPmodel.filePath(index)))


            # clear the selection in favorites view
            self.favorites_listWidget.setCurrentRow(-1)
            self.favorites_listWidget.blockSignals(False)

        def setProject():
            self.masterManager.setProject(self.spActiveProjectPath)
            self.onProjectChange()
            self.setProject_Dialog.close()

        navigate("init")

        ## SIGNALS & SLOTS
        self.favorites_listWidget.dropped.connect(lambda path: onDragAndDrop(path))
        remove_pushButton.clicked.connect(onRemoveFavs)
        add_pushButton.clicked.connect(onAddFavs)

        self.favorites_listWidget.doubleClicked.connect(setProject)

        up_pushButton.clicked.connect(lambda: navigate("up"))
        self.back_pushButton.clicked.connect(lambda: navigate("back"))
        self.forward_pushButton.clicked.connect(lambda: navigate("forward"))
        browse_pushButton.clicked.connect(lambda: navigate("browse"))
        self.lookIn_lineEdit.returnPressed.connect(lambda: navigate("lineEnter"))
        self.folders_tableView.doubleClicked.connect(lambda index: navigate("folder", index=index))


        self.favorites_listWidget.currentItemChanged.connect(favoritesActivated)
        # self.folders_tableView.selectionModel().currentRowChanged.connect(foldersViewActivated)
        # There is a bug in here. If following two lines are run in a single line, a segmentation fault occurs and crashes 3ds max immediately
        selectionModel = self.folders_tableView.selectionModel()
        selectionModel.selectionChanged.connect(foldersViewActivated)


        self.favorites_listWidget.doubleClicked.connect(setProject)
        #
        cancel_pushButton.clicked.connect(self.setProject_Dialog.close)
        set_pushButton.clicked.connect(setProject)
        # set_pushButton.clicked.connect(self.setProject_Dialog.close)
        #
        self.setProject_Dialog.show()

    def addRemoveUserUI(self):

        admin_pswd = "682"
        passw, ok = QtGui.QInputDialog.getText(self, "Password Query", "Enter Admin Password:",
                                               QtGui.QLineEdit.Password)
        if ok:
            if passw == admin_pswd:
                pass
            else:
                self.infoPop(textTitle="Incorrect Password", textHeader="The Password is invalid")
                return
        else:
            return

        users_Dialog = QtGui.QDialog(parent=self)
        users_Dialog.setModal(True)
        users_Dialog.setObjectName(("users_Dialog"))
        users_Dialog.resize(380, 483)
        users_Dialog.setMinimumSize(QtCore.QSize(342, 177))
        users_Dialog.setMaximumSize(QtCore.QSize(342, 177))
        users_Dialog.setWindowTitle(("Add/Remove Users"))
        users_Dialog.setFocus()

        addnewuser_groupBox = QtGui.QGroupBox(users_Dialog)
        addnewuser_groupBox.setGeometry(QtCore.QRect(10, 10, 321, 91))
        addnewuser_groupBox.setTitle(("Add New User"))
        addnewuser_groupBox.setObjectName(("addnewuser_groupBox"))

        fullname_label = QtGui.QLabel(addnewuser_groupBox)
        fullname_label.setGeometry(QtCore.QRect(0, 30, 81, 21))
        fullname_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        fullname_label.setText(("Full Name:"))
        fullname_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        fullname_label.setObjectName(("fullname_label"))

        self.fullname_lineEdit = QtGui.QLineEdit(addnewuser_groupBox)
        self.fullname_lineEdit.setGeometry(QtCore.QRect(90, 30, 151, 20))
        self.fullname_lineEdit.setPlaceholderText(("e.g \"John Doe\""))
        self.fullname_lineEdit.setObjectName(("fullname_lineEdit"))

        initials_label = QtGui.QLabel(addnewuser_groupBox)
        initials_label.setGeometry(QtCore.QRect(0, 60, 81, 21))
        initials_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        initials_label.setText(("Initials:"))
        initials_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        initials_label.setObjectName(("initials_label"))

        self.initials_lineEdit = QtGui.QLineEdit(addnewuser_groupBox)
        self.initials_lineEdit.setGeometry(QtCore.QRect(90, 60, 151, 20))
        self.initials_lineEdit.setText((""))
        self.initials_lineEdit.setPlaceholderText(("e.g \"jd\" (must be unique)"))
        self.initials_lineEdit.setObjectName(("initials_lineEdit"))

        addnewuser_pushButton = QtGui.QPushButton(addnewuser_groupBox)
        addnewuser_pushButton.setGeometry(QtCore.QRect(250, 30, 61, 51))
        addnewuser_pushButton.setText(("Add"))
        addnewuser_pushButton.setObjectName(("addnewuser_pushButton"))

        deleteuser_groupBox = QtGui.QGroupBox(users_Dialog)
        deleteuser_groupBox.setGeometry(QtCore.QRect(10, 110, 321, 51))
        deleteuser_groupBox.setTitle(("Delete User"))
        deleteuser_groupBox.setObjectName(("deleteuser_groupBox"))

        self.selectuser_comboBox = QtGui.QComboBox(deleteuser_groupBox)
        self.selectuser_comboBox.setGeometry(QtCore.QRect(10, 20, 231, 22))
        self.selectuser_comboBox.setObjectName(("selectuser_comboBox"))

        userListSorted = sorted(self.masterManager._usersDict.keys())
        for num in range(len(userListSorted)):
            self.selectuser_comboBox.addItem((userListSorted[num]))
            self.selectuser_comboBox.setItemText(num, (userListSorted[num]))

        deleteuser_pushButton = QtGui.QPushButton(deleteuser_groupBox)
        deleteuser_pushButton.setGeometry(QtCore.QRect(250, 20, 61, 21))
        deleteuser_pushButton.setText(("Delete"))
        deleteuser_pushButton.setObjectName(("deleteuser_pushButton"))


        def onAddUser():
            ret, msg = self.masterManager.addUser(self.fullname_lineEdit.text(), self.initials_lineEdit.text())
            if ret == -1:
                self.infoPop(textTitle="Cannot Add User", textHeader=msg)
                return
            self.masterManager.currentUser = self.fullname_lineEdit.text()
            self._initUsers()
            userListSorted = sorted(self.masterManager._usersDict.keys())
            self.selectuser_comboBox.clear()
            for num in range(len(userListSorted)):
                self.selectuser_comboBox.addItem((userListSorted[num]))
                self.selectuser_comboBox.setItemText(num, (userListSorted[num]))
            self.statusBar().showMessage("Status | User Added => %s" % self.fullname_lineEdit.text())
            self.fullname_lineEdit.setText("")
            self.initials_lineEdit.setText("")

            pass

        def onRemoveUser():
            self.masterManager.removeUser(self.selectuser_comboBox.currentText())
            self.masterManager.currentUser = self.masterManager._usersDict.keys()[0]
            self._initUsers()
            userListSorted = sorted(self.masterManager._usersDict.keys())
            self.selectuser_comboBox.clear()
            for num in range(len(userListSorted)):
                self.selectuser_comboBox.addItem((userListSorted[num]))
                self.selectuser_comboBox.setItemText(num, (userListSorted[num]))
            pass

        addnewuser_pushButton.clicked.connect(onAddUser)
        deleteuser_pushButton.clicked.connect(onRemoveUser)

        self.fullname_lineEdit.textChanged.connect(
            lambda: self._checkValidity(self.fullname_lineEdit.text(), addnewuser_pushButton,
                                  self.fullname_lineEdit, allowSpaces=True))
        self.initials_lineEdit.textChanged.connect(
            lambda: self._checkValidity(self.initials_lineEdit.text(), addnewuser_pushButton,
                                  self.initials_lineEdit))

        users_Dialog.show()

    def addRemoveCategoryUI(self):

        admin_pswd = "682"
        passw, ok = QtGui.QInputDialog.getText(self, "Password Query", "Enter Admin Password:",
                                               QtGui.QLineEdit.Password)
        if ok:
            if passw == admin_pswd:
                pass
            else:
                self.infoPop(textTitle="Incorrect Password", textHeader="The Password is invalid")
                return
        else:
            return

        categories_dialog = QtGui.QDialog(parent=self)
        categories_dialog.setModal(True)
        categories_dialog.setObjectName(("category_Dialog"))
        categories_dialog.setMinimumSize(QtCore.QSize(342, 177))
        categories_dialog.setMaximumSize(QtCore.QSize(342, 177))
        categories_dialog.setWindowTitle(("Add/Remove Categories"))
        categories_dialog.setFocus()

        addnewcategory_groupbox = QtGui.QGroupBox(categories_dialog)
        addnewcategory_groupbox.setGeometry(QtCore.QRect(10, 10, 321, 81))
        addnewcategory_groupbox.setTitle(("Add New Category"))
        addnewcategory_groupbox.setObjectName(("addnewcategory_groupBox"))

        categoryName_label = QtGui.QLabel(addnewcategory_groupbox)
        categoryName_label.setGeometry(QtCore.QRect(10, 30, 81, 21))
        categoryName_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        categoryName_label.setText(("Category Name:"))
        categoryName_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        categoryName_label.setObjectName(("categoryName_label"))

        self.categoryName_lineEdit= QtGui.QLineEdit(addnewcategory_groupbox)
        self.categoryName_lineEdit.setGeometry(QtCore.QRect(105, 30, 135, 20))
        self.categoryName_lineEdit.setPlaceholderText(("e.g \"Look Dev\""))
        self.categoryName_lineEdit.setObjectName(("categoryName_lineEdit"))

        addnewcategory_pushButton = QtGui.QPushButton(addnewcategory_groupbox)
        addnewcategory_pushButton.setGeometry(QtCore.QRect(250, 28, 61, 26))
        addnewcategory_pushButton.setText(("Add"))
        addnewcategory_pushButton.setObjectName(("addnewcategory_pushButton"))

        deletecategory_groupBox = QtGui.QGroupBox(categories_dialog)
        deletecategory_groupBox.setGeometry(QtCore.QRect(10, 110, 321, 51))
        deletecategory_groupBox.setTitle(("Delete category"))
        deletecategory_groupBox.setObjectName(("deletecategory_groupBox"))

        self.selectcategory_comboBox = QtGui.QComboBox(deletecategory_groupBox)
        self.selectcategory_comboBox.setGeometry(QtCore.QRect(10, 20, 231, 22))
        self.selectcategory_comboBox.setObjectName(("selectcategory_comboBox"))

        self.selectcategory_comboBox.addItems(self.masterManager._categories)

        deletecategory_pushButton = QtGui.QPushButton(deletecategory_groupBox)
        deletecategory_pushButton.setGeometry(QtCore.QRect(250, 20, 61, 21))
        deletecategory_pushButton.setText(("Delete"))
        deletecategory_pushButton.setObjectName(("deletecategory_pushButton"))


        def onAddCategory():
            self.masterManager.addCategory(self.categoryName_lineEdit.text())


            preTab = QtGui.QWidget()
            preTab.setObjectName(self.categoryName_lineEdit.text())
            self.category_tabWidget.addTab(preTab, self.categoryName_lineEdit.text())
            self.selectcategory_comboBox.addItem(self.categoryName_lineEdit.text())

            self.categoryName_lineEdit.setText("")

        def onRemoveCategory():
            self.masterManager.removeCategory(self.selectcategory_comboBox.currentText())
            self.selectcategory_comboBox.clear()
            self.selectcategory_comboBox.addItems(self.masterManager.getCategories())

            self._initCategories()


        addnewcategory_pushButton.clicked.connect(onAddCategory)
        deletecategory_pushButton.clicked.connect(onRemoveCategory)

        self.categoryName_lineEdit.textChanged.connect(
            lambda: self._checkValidity(self.categoryName_lineEdit.text(), addnewcategory_pushButton,
                                        self.categoryName_lineEdit))


        categories_dialog.show()

    def onContextMenu_scenes(self, point):
        # show context menu
        self.popMenu_scenes.exec_(self.scenes_listWidget.mapToGlobal(point))
    def onContextMenu_thumbnail(self, point):
        # show context menu
        self.popMenu_thumbnail.exec_(self.thumbnail_label.mapToGlobal(point))

    def addNoteDialog(self):
        row = self.scenes_listWidget.currentRow()
        if row == -1:
            return

        addNotes_Dialog = QtGui.QDialog(parent=self)
        addNotes_Dialog.setModal(True)
        addNotes_Dialog.setObjectName(("addNotes_Dialog"))
        addNotes_Dialog.resize(255, 290)
        addNotes_Dialog.setMinimumSize(QtCore.QSize(255, 290))
        addNotes_Dialog.setMaximumSize(QtCore.QSize(255, 290))
        addNotes_Dialog.setWindowTitle(("Add Notes"))

        addNotes_label = QtGui.QLabel(addNotes_Dialog)
        addNotes_label.setGeometry(QtCore.QRect(15, 15, 100, 20))
        addNotes_label.setText(("Additional Notes"))
        addNotes_label.setObjectName(("addNotes_label"))

        addNotes_textEdit = QtGui.QTextEdit(addNotes_Dialog)
        addNotes_textEdit.setGeometry(QtCore.QRect(15, 40, 215, 170))
        addNotes_textEdit.setObjectName(("addNotes_textEdit"))

        addNotes_buttonBox = QtGui.QDialogButtonBox(addNotes_Dialog)
        addNotes_buttonBox.setGeometry(QtCore.QRect(20, 250, 220, 32))
        addNotes_buttonBox.setOrientation(QtCore.Qt.Horizontal)
        addNotes_buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Save | QtGui.QDialogButtonBox.Cancel)

        buttonS = addNotes_buttonBox.button(QtGui.QDialogButtonBox.Save)
        buttonS.setText('Add Notes')
        buttonC = addNotes_buttonBox.button(QtGui.QDialogButtonBox.Cancel)
        buttonC.setText('Cancel')

        addNotes_buttonBox.setObjectName(("addNotes_buttonBox"))
        addNotes_buttonBox.accepted.connect(lambda: self.masterManager.addNote(addNotes_textEdit.toPlainText()))
        addNotes_buttonBox.accepted.connect(self.onVersionChange)
        addNotes_buttonBox.accepted.connect(addNotes_Dialog.accept)

        addNotes_buttonBox.rejected.connect(addNotes_Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(addNotes_Dialog)

        addNotes_Dialog.show()

    def initMainUI(self, newborn=False):

        if not newborn:
            for manager in self.masterManager.swList:
                manager.init_paths()
                manager.init_database()

        self._initCategories()

        # init project
        self.project_lineEdit.setText(self.masterManager.projectDir)

        # init subproject
        self._initSubProjects()

        # init base scenes
        self.populateBaseScenes()

        # init users
        self._initUsers()

        # disable the version related stuff
        self.version_comboBox.setStyleSheet("background-color: rgb(80,80,80); color: white")
        self._vEnableDisable()

    def rcAction_scenes(self, command):

        if command == "showInExplorerMaya":
            self.manager.showInExplorer(self.manager.currentBaseScenePath)

        if command == "showInExplorerPB":
            self.manager.showInExplorer(self.manager.currentPreviewPath)

        if command == "showInExplorerData":
            filePath = self.manager._baseScenesInCategory[self.manager.currentBaseSceneName]
            dirPath = os.path.dirname(filePath)
            self.manager.showInExplorer(dirPath)

        if command == "showSceneInfo":
            textInfo = pprint.pformat(self.manager._currentSceneInfo)
            print self.manager._currentSceneInfo
            self.messageDialog = QtGui.QDialog()
            self.messageDialog.setWindowTitle("Scene Info")
            self.messageDialog.resize(800, 700)
            self.messageDialog.show()
            messageLayout = QtGui.QVBoxLayout(self.messageDialog)
            messageLayout.setContentsMargins(0, 0, 0, 0)
            helpText = QtGui.QTextEdit()
            helpText.setReadOnly(True)
            helpText.setStyleSheet("background-color: rgb(255, 255, 255);")
            helpText.setStyleSheet(""
                                   "border: 20px solid black;"
                                   "background-color: black;"
                                   "font-size: 16px"
                                   "")
            helpText.setText(textInfo)
            messageLayout.addWidget(helpText)

class ImageWidget(QtGui.QLabel):
    def __init__(self, parent=None):
        super(ImageWidget, self).__init__()
        self.aspectRatio = 1.78
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)

    def resizeEvent(self, r):
        h = self.width()
        self.setMinimumHeight(h/self.aspectRatio)
        self.setMaximumHeight(h/self.aspectRatio)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MainUI()
    window.show()
    sys.exit(app.exec_())
