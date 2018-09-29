import os
import SmRoot
from SmRoot import RootManager
from PyQt4 import QtCore, QtGui, Qt

import _version

import sys, os
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

class StandaloneManager(RootManager)
    def __init__(self):
        super(StandaloneManager, self).__init__()

    def getProjectDir(self):
        """Overriden function"""

    def initSoftwares(self):

    def getSoftwarePaths(self):
        """Overriden function"""
        # To tell the base class maya specific path names
        return {"databaseDir": "mayaDB",
                "scenesDir": "scenes",
                "pbSettingsFile": "pbSettings"}



class MainUI(QtGui.QMainWindow):
    def __init__(self):
        super(MainUI, self).__init__()
        # self.projectPath = os.path.normpath("M:\Projects\Bambi_Yatak_shortcut_171130\images")

        self.tempCategories = ["Model", "Rig", "Shading", "Layout", "Animation", "Render", "Other"]

        self.setObjectName(SM_Version)
        self.resize(680, 600)
        self.setWindowTitle(SM_Version)
        self.centralwidget = QtGui.QWidget(self)

        self.setupUi(self)

        self.setCentralWidget(self.centralwidget)

    def setupUi(self, sceneManager_MainWindow):
        sceneManager_MainWindow.setObjectName(("sceneManager_MainWindow"))
        sceneManager_MainWindow.setCentralWidget(self.centralwidget)

        self.centralwidget = QtGui.QWidget(sceneManager_MainWindow)
        self.centralwidget.setObjectName(("centralwidget"))

        self.main_gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.main_gridLayout.setObjectName(("main_gridLayout"))

        self.main_horizontalLayout = QtGui.QHBoxLayout()
        self.main_horizontalLayout.setContentsMargins(-1, -1, 0, -1)
        self.main_horizontalLayout.setSpacing(6)
        self.main_horizontalLayout.setObjectName(("horizontalLayout"))
        self.main_horizontalLayout.setStretch(0, 1)

        # self.saveVersion_pushButton = QtGui.QPushButton(self.centralwidget)
        # self.saveVersion_pushButton.setMinimumSize(QtCore.QSize(150, 45))
        # self.saveVersion_pushButton.setMaximumSize(QtCore.QSize(150, 45))
        # self.saveVersion_pushButton.setText(("Save As Version"))
        # self.saveVersion_pushButton.setObjectName(("saveVersion_pushButton"))
        # self.main_horizontalLayout.addWidget(self.saveVersion_pushButton)
        #
        # self.saveBaseScene_pushButton = QtGui.QPushButton(self.centralwidget)
        # self.saveBaseScene_pushButton.setMinimumSize(QtCore.QSize(150, 45))
        # self.saveBaseScene_pushButton.setMaximumSize(QtCore.QSize(150, 45))
        # self.saveBaseScene_pushButton.setText(("Save Base Scene"))
        # self.saveBaseScene_pushButton.setObjectName(("saveBaseScene_pushButton"))
        # self.main_horizontalLayout.addWidget(self.saveBaseScene_pushButton)

        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.main_horizontalLayout.addItem(spacerItem)

        self.loadScene_pushButton = QtGui.QPushButton(self.centralwidget)
        self.loadScene_pushButton.setMinimumSize(QtCore.QSize(150, 45))
        self.loadScene_pushButton.setMaximumSize(QtCore.QSize(150, 45))
        self.loadScene_pushButton.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.loadScene_pushButton.setText(("Load Scene"))
        self.loadScene_pushButton.setObjectName(("loadScene_pushButton"))
        self.main_horizontalLayout.addWidget(self.loadScene_pushButton)

        self.main_gridLayout.addLayout(self.main_horizontalLayout, 4, 0, 1, 1)

        self.r2_gridLayout = QtGui.QGridLayout()
        self.r2_gridLayout.setObjectName(("r2_gridLayout"))
        self.r2_gridLayout.setColumnStretch(1, 1)

        # self.load_radioButton = QtGui.QRadioButton(self.centralwidget)
        # self.load_radioButton.setText(("Load Mode"))
        # self.load_radioButton.setChecked(False)
        # self.load_radioButton.setObjectName(("load_radioButton"))
        # self.r2_gridLayout.addWidget(self.load_radioButton, 0, 0, 1, 1)

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

        # self.reference_radioButton = QtGui.QRadioButton(self.centralwidget)
        # self.reference_radioButton.setText(("Reference Mode"))
        # self.reference_radioButton.setChecked(True)
        # self.reference_radioButton.setObjectName(("reference_radioButton"))
        # self.r2_gridLayout.addWidget(self.reference_radioButton, 0, 1, 1, 1)

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
        self.r1_gridLayout.setObjectName(("gridLayout"))

        self.baseScene_label = QtGui.QLabel(self.centralwidget)
        self.baseScene_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.baseScene_label.setText(("Base Scene:"))
        self.baseScene_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.baseScene_label.setObjectName(("baseScene_label"))
        self.r1_gridLayout.addWidget(self.baseScene_label, 0, 0, 1, 1)

        self.baseScene_lineEdit = QtGui.QLineEdit(self.centralwidget)
        self.baseScene_lineEdit.setText((""))
        self.baseScene_lineEdit.setPlaceholderText((""))
        self.baseScene_lineEdit.setObjectName(("baseScene_lineEdit"))
        self.r1_gridLayout.addWidget(self.baseScene_lineEdit, 0, 1, 1, 1)

        self.project_label = QtGui.QLabel(self.centralwidget)
        self.project_label.setText(("Project:"))
        self.project_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.project_label.setObjectName(("project_label"))
        self.r1_gridLayout.addWidget(self.project_label, 1, 0, 1, 1)

        self.project_lineEdit = QtGui.QLineEdit(self.centralwidget)
        self.project_lineEdit.setText((""))
        self.project_lineEdit.setPlaceholderText((""))
        self.project_lineEdit.setObjectName(("project_lineEdit"))
        self.r1_gridLayout.addWidget(self.project_lineEdit, 1, 1, 1, 1)

        self.setProject_pushButton = QtGui.QPushButton(self.centralwidget)
        self.setProject_pushButton.setText(("SET"))
        self.setProject_pushButton.setObjectName(("setProject_pushButton"))
        self.r1_gridLayout.addWidget(self.setProject_pushButton, 1, 2, 1, 1)

        self.main_gridLayout.addLayout(self.r1_gridLayout, 0, 0, 1, 1)

        self.category_tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.category_tabWidget.setMaximumSize(QtCore.QSize(16777215, 22))
        self.category_tabWidget.setTabPosition(QtGui.QTabWidget.North)
        self.category_tabWidget.setElideMode(QtCore.Qt.ElideNone)
        self.category_tabWidget.setUsesScrollButtons(False)
        self.category_tabWidget.setObjectName(("tabWidget"))

        for i in self.tempCategories:
            self.preTab = QtGui.QWidget()
            self.preTab.setObjectName((i))
            self.category_tabWidget.addTab(self.preTab, (i))

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

        self.versionNotes_label = QtGui.QLabel(self.frame)
        self.versionNotes_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.versionNotes_label.setText(("Version Notes:"))
        self.versionNotes_label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.versionNotes_label.setObjectName(("version_label_2"))
        self.verticalLayout.addWidget(self.versionNotes_label)

        self.notes_textEdit = QtGui.QTextEdit(self.frame)
        self.notes_textEdit.setObjectName(("textEdit"))
        self.verticalLayout.addWidget(self.notes_textEdit)

        # testFile = os.path.normpath("D:\\PROJECT_AND_ARGE\\testo_testo_testo_180715\\DSC_2179.JPG")
        testFile = os.path.normpath("C:\\a.JPG")
        self.tPixmap = QtGui.QPixmap((testFile))
        # os.startfile(testFile)
        self.thumbnail_label = ImageWidget(self.frame)
        # self.label = QtGui.QLabel(self.frame)
        self.thumbnail_label.setPixmap(self.tPixmap)

        # self.label.setPixmap(self.tPixmap.scaledToWidth(self.label.width()))
        # sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        # sizePolicy.setHeightForWidth(True)
        # self.label.setSizePolicy(sizePolicy)

        self.thumbnail_label.setMinimumSize(QtCore.QSize(221, 124))
        # self.label.setMaximumSize(QtCore.QSize(884, 496))
        # self.label.setSizeIncrement(QtCore.QSize(1, 1))
        # self.label.setBaseSize(QtCore.QSize(0, 0))
        # self.label.setText(("test"))
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
        # self.horizontalLayout_4.setMargin(0)
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

        self.splitter.setStretchFactor(0, 1)

        self.menubar = QtGui.QMenuBar(sceneManager_MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 680, 18))
        self.menubar.setObjectName(("menubar"))

        sceneManager_MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(sceneManager_MainWindow)
        self.statusbar.setObjectName(("statusbar"))
        sceneManager_MainWindow.setStatusBar(self.statusbar)

        # MENU BAR / STATUS BAR
        # ---------------------
        file = self.menubar.addMenu("File")
        saveVersion_fm = QtGui.QAction("&Save Version", self)
        saveBaseScene_fm = QtGui.QAction("&Save Base Scene", self)
        loadReferenceScene_fm = QtGui.QAction("&Load/Reference Scene", self)
        createProject_fm = QtGui.QAction("&Create Project", self)
        pb_settings_fm = QtGui.QAction("&Playblast Settings", self)
        add_remove_users_fm = QtGui.QAction("&Add/Remove Users", self)
        deleteFile_fm = QtGui.QAction("&Delete Selected Base Scene", self)
        deleteReference_fm = QtGui.QAction("&Delete Reference of Selected Scene", self)
        reBuildDatabase_fm = QtGui.QAction("&Re-build Project Database", self)
        projectReport_fm = QtGui.QAction("&Project Report", self)
        checkReferences_fm = QtGui.QAction("&Check References", self)

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

        tools = self.menubar.addMenu("Tools")
        imanager = QtGui.QAction("&Image Manager", self)
        iviewer = QtGui.QAction("&Image Viewer", self)
        createPB = QtGui.QAction("&Create PlayBlast", self)

        tools.addAction(imanager)
        tools.addAction(iviewer)
        tools.addAction(createPB)

        # RIGHT CLICK MENUS
        # -----------------

        # List Widget Right Click Menu
        self.scenes_listWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.scenes_listWidget.customContextMenuRequested.connect(self.onContextMenu_scenes)
        self.popMenu_scenes = QtGui.QMenu()

        scenes_rcAction_0 = QtGui.QAction('Import Scene', self)
        self.popMenu_scenes.addAction(scenes_rcAction_0)

        scenes_rcAction_1 = QtGui.QAction('Show Maya Folder in Explorer', self)
        self.popMenu_scenes.addAction(scenes_rcAction_1)

        scenes_rcAction_2 = QtGui.QAction('Show Playblast Folder in Explorer', self)
        self.popMenu_scenes.addAction(scenes_rcAction_2)

        scenes_rcAction_3 = QtGui.QAction('Show Data Folder in Explorer', self)
        self.popMenu_scenes.addAction(scenes_rcAction_3)

        self.popMenu_scenes.addSeparator()
        scenes_rcAction_4 = QtGui.QAction('Scene Info', self)
        self.popMenu_scenes.addAction(scenes_rcAction_4)

        # Thumbnail Right Click Menu
        self.thumbnail_label.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.thumbnail_label.customContextMenuRequested.connect(self.onContextMenu_thumbnail)
        self.popMenu_thumbnail = QtGui.QMenu()

        thumb_rcAction_0 = QtGui.QAction('Replace with current view', self)
        self.popMenu_thumbnail.addAction(thumb_rcAction_0)

        thumb_rcAction_1 = QtGui.QAction('Replace with external file', self)
        self.popMenu_thumbnail.addAction(thumb_rcAction_1)

        # SHORTCUTS
        # ---------
        # shortcutRefresh = Qt.QShortcut(Qt.QKeySequence("F5"), self, self.refresh)

        # SIGNAL CONNECTIONS
        # ------------------

        self.statusBar().showMessage("Status | Idle")

    def onContextMenu_scenes(self, point):
        # show context menu
        self.popMenu_scenes.exec_(self.scenes_listWidget.mapToGlobal(point))
    def onContextMenu_thumbnail(self, point):
        # show context menu
        self.popMenu_thumbnail.exec_(self.thumbnail_label.mapToGlobal(point))

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
