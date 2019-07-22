#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------------------------
# Copyright (c) 2017-2018, Arda Kutlu (ardakutlu@gmail.com)
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  - Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
#  - Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
#  - Neither the name of the software nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# -----------------------------------------------------------------------------

# Abstract Module for main UI

# ---------------
# GET ENVIRONMENT
# ---------------
import os
import _version
from copy import deepcopy
import re
import datetime

# Below is the standard dictionary for Scene Manager Standalone
BoilerDict = {"Environment":"Standalone",
              "MainWindow":None,
              "WindowTitle":"Scene Manager Standalone v%s" %_version.__version__,
              "SceneFormats":None
              }

FORCE_QT4 = False
# Get Environment and edit the dictionary according to the Environment
try:
    from maya import OpenMayaUI as omui
    import Qt
    from Qt import QtWidgets, QtCore, QtGui
    BoilerDict["Environment"] = "Maya"
    BoilerDict["WindowTitle"] = "Tik Manager Maya v%s" %_version.__version__
    BoilerDict["SceneFormats"] = ["mb", "ma"]
except ImportError:
    pass

try:
    import MaxPlus
    import Qt
    from Qt import QtWidgets, QtCore, QtGui
    BoilerDict["Environment"] = "3dsMax"
    BoilerDict["WindowTitle"] = "Tik Manager 3ds Max v%s" %_version.__version__
    BoilerDict["SceneFormats"] = ["max"]
except ImportError:
    pass

try:
    import hou
    import Qt
    from Qt import QtWidgets, QtCore, QtGui
    BoilerDict["Environment"] = "Houdini"
    BoilerDict["WindowTitle"] = "Tik Manager Houdini v%s" %_version.__version__
    BoilerDict["SceneFormats"] = ["hip", "hiplc"]
except ImportError:
    pass

try:
    import nuke
    import Qt
    from Qt import QtWidgets, QtCore, QtGui
    BoilerDict["Environment"] = "Nuke"
    BoilerDict["WindowTitle"] = "Tik Manager Nuke v%s" % _version.__version__
    BoilerDict["SceneFormats"] = ["nk"]
except ImportError:
    pass

try:
    from PyQt4 import QtCore, Qt
    from PyQt4 import QtGui as QtWidgets
    FORCE_QT4 = True
    if bool(os.getenv("PS_APP")):  # if the request is coming from the SmPhotoshop
        BoilerDict["Environment"] = "Standalone"  # technically it is still standalone...
        BoilerDict["WindowTitle"] = "Tik Manager Photoshop v%s" % _version.__version__
        BoilerDict["SceneFormats"] = ["psd", "psb"]
    else:
        BoilerDict["Environment"] = "Standalone"
        BoilerDict["WindowTitle"] = "Tik Manager Standalone v%s" % _version.__version__
        BoilerDict["SceneFormats"] = None
except ImportError:
    pass

import webbrowser

## DO NOT REMOVE THIS:
import iconsSource as icons
## DO NOT REMOVE THIS:

import pprint

import ImageViewer

import logging

__author__ = "Arda Kutlu"
__copyright__ = "Copyright 2018, Tik Manager UI Boilerplate"
__credits__ = []
__license__ = "GPL"
__maintainer__ = "Arda Kutlu"
__email__ = "ardakutlu@gmail.com"
__status__ = "Development"

logging.basicConfig()
logger = logging.getLogger('smUIRoot')
logger.setLevel(logging.WARNING)

def getMainWindow():
    """This function should be overriden"""
    if BoilerDict["Environment"] == "Maya":
        if Qt.__binding__ == "PySide":
            from shiboken import wrapInstance
        elif Qt.__binding__.startswith('PyQt'):
            from sip import wrapinstance as wrapInstance
        else:
            from shiboken2 import wrapInstance
        win = omui.MQtUtil_mainWindow()
        ptr = wrapInstance(long(win), QtWidgets.QMainWindow)
        return ptr

    elif BoilerDict["Environment"] == "3dsMax":
        try: mainWindow = MaxPlus.GetQMaxWindow()
        except AttributeError: mainWindow = MaxPlus.GetQMaxMainWindow()
        return mainWindow

    elif BoilerDict["Environment"] == "Houdini":
        return hou.qt.mainWindow()

    elif BoilerDict["Environment"] == "Nuke":
        app = QtWidgets.QApplication.instance()
        for widget in app.topLevelWidgets():
            if widget.metaObject().className() == 'Foundry::UI::DockMainWindow':
                return widget
        return None

    else:
        return None

class MainUI(QtWidgets.QMainWindow):
    """Main UI Class for Tik Scene Manager"""
    def __init__(self, callback=None):
        self.isCallback = callback
        self.windowName = BoilerDict["WindowTitle"]
        for entry in QtWidgets.QApplication.allWidgets():
            try:
                if entry.objectName() == self.windowName:
                    entry.close()
            except AttributeError:
                pass
        parent = getMainWindow()
        super(MainUI, self).__init__(parent=parent)

        # Set Stylesheet
        dirname = os.path.dirname(os.path.abspath(__file__))
        stylesheetFile = os.path.join(dirname, "CSS", "tikManager.qss")

        with open(stylesheetFile, "r") as fh:
            self.setStyleSheet(fh.read())

        ## fonts:
        if FORCE_QT4:
            self.iconFont = QtWidgets.QFont("Segoe UI Symbol", 12, QtWidgets.QFont.Bold)
            self.headerAFont = QtWidgets.QFont("Segoe UI Symbol", 14, QtWidgets.QFont.Bold)
            self.headerBFont = QtWidgets.QFont("Segoe UI Symbol", 10, QtWidgets.QFont.Bold)
            self.displayFont = QtWidgets.QFont("Segoe UI Symbol", 8, QtWidgets.QFont.Bold)
            self.infoFont = QtWidgets.QFont("", 8, QtWidgets.QFont.Helvetica)
            self.Pixmap = QtWidgets.QPixmap
            self.QIcon = QtWidgets.QIcon
        else:
            self.iconFont = QtGui.QFont("Segoe UI Symbol", 12, QtGui.QFont.Bold)
            self.headerAFont = QtGui.QFont("Segoe UI Symbol", 14, QtGui.QFont.Bold)
            self.headerBFont = QtGui.QFont("Segoe UI Symbol", 10, QtGui.QFont.Bold)
            self.displayFont = QtGui.QFont("Segoe UI Symbol", 8, QtGui.QFont.Bold)
            self.infoFont = QtGui.QFont("", 8, QtGui.QFont.Helvetica)
            self.Pixmap = QtGui.QPixmap
            self.QIcon = QtGui.QIcon

        self.superUser = False

    def buildUI(self):
        self.setObjectName(self.windowName)
        self.resize(680, 600)
        self.setWindowTitle(self.windowName)

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.setCentralWidget(self.centralwidget)

        mainLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        try: mainLayout.setMargin(0)
        except AttributeError: pass

        mainLayout.setContentsMargins(10, 10, 10, 10)

        # ----------
        # HEADER BAR
        # ----------
        margin = 5
        self.colorBar = QtWidgets.QLabel()
        headerColor = self.manager.getColorCoding(self.manager.swName)
        self.colorBar.setStyleSheet("background-color: %s;" %headerColor)
        mainLayout.addWidget(self.colorBar)
        # pyside does not have setMargin attribute
        try: self.colorBar.setMargin(0)
        except AttributeError: pass
        self.colorBar.setIndent(0)
        self.colorBar.setMaximumHeight(1)

        colorWidget = QtWidgets.QWidget(self.centralwidget)
        colorWidget.setProperty("header", True)
        headerLayout = QtWidgets.QHBoxLayout(colorWidget)
        headerLayout.setSpacing(0)
        try: headerLayout.setMargin(0)
        except AttributeError: pass

        tikIcon_label = QtWidgets.QLabel(self.centralwidget)
        tikIcon_label.setProperty("header", True)
        try: tikIcon_label.setMargin(margin)
        except AttributeError: pass
        tikIcon_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        tikIcon_label.setScaledContents(False)
        headerBitmap = self.Pixmap(":/icons/CSS/rc/tmMain.png")

        tikIcon_label.setPixmap(headerBitmap)

        headerLayout.addWidget(tikIcon_label)

        self.baseScene_label = QtWidgets.QLabel(self.centralwidget)
        self.baseScene_label.setProperty("header", True)
        try: self.baseScene_label.setMargin(margin)
        except AttributeError: pass
        self.baseScene_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        self.baseScene_label.setFont(self.displayFont)
        headerLayout.addWidget(self.baseScene_label)

        self.managerIcon_label = QtWidgets.QLabel(self.centralwidget)
        self.managerIcon_label.setProperty("header", True)
        try: self.managerIcon_label.setMargin(margin)
        except AttributeError: pass
        self.managerIcon_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.managerIcon_label.setScaledContents(False)

        headerLayout.addWidget(self.managerIcon_label)

        mainLayout.addWidget(colorWidget)
        # ----------
        # ----------

        self.main_gridLayout = QtWidgets.QGridLayout()
        mainLayout.addLayout(self.main_gridLayout)


        self.main_horizontalLayout = QtWidgets.QHBoxLayout()
        self.main_horizontalLayout.setContentsMargins(-1, -1, 0, -1)
        self.main_horizontalLayout.setSpacing(6)
        # self.main_horizontalLayout.setStretch(0, 1)

        self.saveBaseScene_pushButton = QtWidgets.QPushButton(self.centralwidget, text="Save Base Scene", font=self.iconFont)
        self.saveBaseScene_pushButton.setProperty("menuButton", True)
        self.saveBaseScene_pushButton.setToolTip("Saves the currently open scene as a Base Scene ")
        self.main_horizontalLayout.addWidget(self.saveBaseScene_pushButton)

        self.saveVersion_pushButton = QtWidgets.QPushButton(self.centralwidget, text="Save As Version", font=self.iconFont)
        self.saveVersion_pushButton.setProperty("menuButton", True)
        self.saveVersion_pushButton.setToolTip("Saves a new version from the currently open Base Scene ")

        self.main_horizontalLayout.addWidget(self.saveVersion_pushButton)

        self.export_pushButton = QtWidgets.QPushButton(self.centralwidget, text="Transfer Central", font=self.iconFont)
        self.export_pushButton.setProperty("menuButton", True)
        self.export_pushButton.setToolTip("Export/Import Geometry formats")
        self.main_horizontalLayout.addWidget(self.export_pushButton)

        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.main_horizontalLayout.addItem(spacerItem)

        self.loadScene_pushButton = QtWidgets.QPushButton(self.centralwidget, text="Load Scene", font=self.iconFont)
        self.loadScene_pushButton.setProperty("menuButton", True)
        self.loadScene_pushButton.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.main_horizontalLayout.addWidget(self.loadScene_pushButton)
        #
        self.main_gridLayout.addLayout(self.main_horizontalLayout, 4, 0, 1, 1)
        #
        self.r2_gridLayout = QtWidgets.QGridLayout()
        self.r2_gridLayout.setColumnStretch(1, 1)

        self.load_radioButton = QtWidgets.QRadioButton(self.centralwidget, text="Load Mode")
        self.load_radioButton.setToolTip("Activates Loading mode and lists all base scenes")
        self.r2_gridLayout.addWidget(self.load_radioButton, 0, 0, 1, 1)

        self.reference_radioButton = QtWidgets.QRadioButton(self.centralwidget, text="Reference Mode")
        self.reference_radioButton.setToolTip("Activates Referencing mode and lists base scenes with references")
        self.r2_gridLayout.addWidget(self.reference_radioButton, 0, 1, 1, 1)

        self.subProject_label = QtWidgets.QLabel(self.centralwidget, text="Sub-Project:")
        self.subProject_label.setToolTip("Changes sub-project level")
        self.subProject_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.r2_gridLayout.addWidget(self.subProject_label, 0, 2, 1, 1)

        self.subProject_comboBox = QtWidgets.QComboBox(self.centralwidget, minimumSize=QtCore.QSize(150, 30), maximumSize=QtCore.QSize(16777215, 30))
        self.subProject_comboBox.setToolTip("Changes sub-project level")
        self.r2_gridLayout.addWidget(self.subProject_comboBox, 0, 3, 1, 1)

        self.addSubProject_pushButton = QtWidgets.QPushButton(self.centralwidget, size=QtCore.QSize(30, 30), font=self.iconFont)
        self.addSubProject_pushButton.setToolTip("Adds a new sub-project level")
        self.addSubProject_pushButton.setIcon(self.QIcon(":/icons/CSS/rc/plus.png"))

        self.r2_gridLayout.addWidget(self.addSubProject_pushButton, 0, 4, 1, 1)

        self.user_label = QtWidgets.QLabel(self.centralwidget, text="User:", alignment=(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter))
        self.user_label.setToolTip("Changes the current user")
        self.r2_gridLayout.addWidget(self.user_label, 0, 5, 1, 1)

        self.user_comboBox = QtWidgets.QComboBox(self.centralwidget, minimumSize=QtCore.QSize(130, 30), maximumSize=QtCore.QSize(16777215, 30))
        self.user_comboBox.setToolTip("Changes the current user")
        self.r2_gridLayout.addWidget(self.user_comboBox, 0, 6, 1, 1)

        self.main_gridLayout.addLayout(self.r2_gridLayout, 1, 0, 1, 1)
        self.r1_gridLayout = QtWidgets.QGridLayout()


        self.project_label = QtWidgets.QLabel(self.centralwidget, text="Project:", alignment=(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter))
        self.r1_gridLayout.addWidget(self.project_label, 1, 0, 1, 1)

        self.project_lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.r1_gridLayout.addWidget(self.project_lineEdit, 1, 1, 1, 1)

        self.setProject_pushButton = QtWidgets.QPushButton(self.centralwidget, text="SET")
        self.setProject_pushButton.setToolTip("Changes the active project")

        self.r1_gridLayout.addWidget(self.setProject_pushButton, 1, 2, 1, 1)

        self.main_gridLayout.addLayout(self.r1_gridLayout, 0, 0, 1, 1)

        self.category_tabWidget = QtWidgets.QTabWidget(self.centralwidget, maximumSize=QtCore.QSize(16777215, 20), tabPosition=QtWidgets.QTabWidget.North, elideMode=QtCore.Qt.ElideNone, usesScrollButtons=False)

        self.main_gridLayout.addWidget(self.category_tabWidget, 2, 0, 1, 1)

        self.splitter = QtWidgets.QSplitter(self.centralwidget, orientation=QtCore.Qt.Horizontal)

        self.scenes_listWidget = QtWidgets.QTreeWidget(self.splitter, sortingEnabled=True, selectionMode=QtWidgets.QAbstractItemView.SingleSelection, rootIsDecorated=False)
        header = QtWidgets.QTreeWidgetItem(["Name", "Date"])
        self.scenes_listWidget.setHeaderItem(header)
        self.scenes_listWidget.setColumnWidth(0, 250)

        self.frame = QtWidgets.QFrame(self.splitter, frameShape=QtWidgets.QFrame.StyledPanel, frameShadow=QtWidgets.QFrame.Raised)

        self.gridLayout_6 = QtWidgets.QGridLayout(self.frame)
        self.gridLayout_6.setContentsMargins(-1, -1, 0, 0)

        self.verticalLayout = QtWidgets.QVBoxLayout()

        self.notes_label = QtWidgets.QLabel(self.frame, text="Version Notes:", layoutDirection=QtCore.Qt.LeftToRight, alignment=(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter))
        self.verticalLayout.addWidget(self.notes_label)

        self.notes_textEdit = QtWidgets.QTextEdit(self.frame, readOnly=True)
        self.verticalLayout.addWidget(self.notes_textEdit)

        self.E_tPixmap = self.Pixmap(":/icons/CSS/rc/empty_thumbnail.png")
        self.thumbnail_label = ImageWidget(self.frame)
        self.thumbnail_label.setProperty("image", True)
        self.thumbnail_label.setPixmap(self.E_tPixmap)

        self.thumbnail_label.setMinimumSize(QtCore.QSize(221, 124))
        self.thumbnail_label.setFrameShape(QtWidgets.QFrame.Box)
        self.thumbnail_label.setScaledContents(True)
        self.thumbnail_label.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.thumbnail_label)

        self.gridLayout_6.addLayout(self.verticalLayout, 3, 0, 1, 1)

        self.gridLayout_7 = QtWidgets.QGridLayout()
        self.gridLayout_7.setContentsMargins(-1, -1, 10, 10)

        self.showPreview_pushButton = QtWidgets.QPushButton(self.frame, text="Show Preview", minimumSize=QtCore.QSize(100, 30), maximumSize=QtCore.QSize(150, 30))
        self.gridLayout_7.addWidget(self.showPreview_pushButton, 0, 3, 1, 1)

        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setSpacing(1)

        self.version_label = QtWidgets.QLabel(self.frame, text="Version:", minimumSize=QtCore.QSize(60, 30), maximumSize=QtCore.QSize(60, 30), frameShape=QtWidgets.QFrame.Box, alignment=QtCore.Qt.AlignCenter)
        self.horizontalLayout_4.addWidget(self.version_label)

        self.version_comboBox = QtWidgets.QComboBox(self.frame, minimumSize=QtCore.QSize(60, 30), maximumSize=QtCore.QSize(100, 30))
        self.horizontalLayout_4.addWidget(self.version_comboBox)

        self.gridLayout_7.addLayout(self.horizontalLayout_4, 0, 0, 1, 1)

        self.makeReference_pushButton = QtWidgets.QPushButton(self.frame, text="Make Reference", minimumSize=QtCore.QSize(100, 30), maximumSize=QtCore.QSize(300, 30))
        self.gridLayout_7.addWidget(self.makeReference_pushButton, 1, 0, 1, 1)

        self.addNote_pushButton = QtWidgets.QPushButton(self.frame,  text="Add Note", minimumSize=QtCore.QSize(100, 30), maximumSize=QtCore.QSize(150, 30))
        self.gridLayout_7.addWidget(self.addNote_pushButton, 1, 3, 1, 1)

        self.gridLayout_6.addLayout(self.gridLayout_7, 0, 0, 1, 1)

        self.main_gridLayout.addWidget(self.splitter, 3, 0, 1, 1)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        self.splitter.setSizePolicy(sizePolicy)

        self.splitter.setStretchFactor(0, 1)

        # MENU BAR / STATUS BAR
        # ---------------------

        self.menubar = QtWidgets.QMenuBar(self, geometry=QtCore.QRect(0, 0, 680, 18))
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.setStatusBar(self.statusbar)

        self.fileMenu = self.menubar.addMenu("File")
        createProject_fm = QtWidgets.QAction("&Create Project", self)
        self.saveVersion_fm = QtWidgets.QAction("&Save Version", self)
        self.saveBaseScene_fm = QtWidgets.QAction("&Save Base Scene", self)

        loadReferenceScene_fm = QtWidgets.QAction("&Load/Reference Scene", self)

        settings_fm = QtWidgets.QAction(self.QIcon(":/icons/CSS/rc/settings.png"), "&Settings", self)

        deleteFile_fm = QtWidgets.QAction(self.QIcon(":/icons/CSS/rc/delete.png"), "&Delete Selected Base Scene", self)
        deleteReference_fm = QtWidgets.QAction(self.QIcon(":/icons/CSS/rc/delete.png"), "&Delete Reference of Selected Scene", self)
        projectReport_fm = QtWidgets.QAction("&Project Report", self)
        projectReport_fm.setEnabled(False)
        checkReferences_fm = QtWidgets.QAction("&Check References", self)

        #save
        self.fileMenu.addAction(createProject_fm)
        self.fileMenu.addAction(self.saveVersion_fm)
        self.fileMenu.addAction(self.saveBaseScene_fm)
        self.fileMenu.addSeparator()

        #load
        self.fileMenu.addAction(loadReferenceScene_fm)
        self.fileMenu.addSeparator()

        #settings
        self.fileMenu.addAction(settings_fm)
        self.fileMenu.addSeparator()

        #delete
        self.fileMenu.addAction(deleteFile_fm)
        self.fileMenu.addAction(deleteReference_fm)

        self.fileMenu.addSeparator()

        #misc
        self.fileMenu.addAction(projectReport_fm)
        self.fileMenu.addAction(checkReferences_fm)

        self.toolsMenu = self.menubar.addMenu("Tools")
        imageViewer_mi = QtWidgets.QAction("&Image Viewer", self)
        projectMaterials_mi = QtWidgets.QAction("&Project Materials", self)
        self.assetLibrary_mi = QtWidgets.QAction("&Asset Library", self)
        self.createPB = QtWidgets.QAction("&Create Preview", self)

        self.toolsMenu.addAction(imageViewer_mi)
        self.toolsMenu.addAction(projectMaterials_mi)
        self.toolsMenu.addAction(self.assetLibrary_mi)
        self.toolsMenu.addAction(self.createPB)

        helpMenu = self.menubar.addMenu("Help")
        onlineHelp_mi = QtWidgets.QAction("&Online Help", self)
        checkVersion_mi = QtWidgets.QAction("&Check for updates", self)

        helpMenu.addAction(onlineHelp_mi)
        helpMenu.addAction(checkVersion_mi)

        # RIGHT CLICK MENUS
        # -----------------

        # List Widget Right Click Menu
        self.scenes_listWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.scenes_listWidget.customContextMenuRequested.connect(self.onContextMenu_scenes)
        self.popMenu_scenes = QtWidgets.QMenu()

        self.scenes_rcItem_0 = QtWidgets.QAction('Import Scene', self)
        self.popMenu_scenes.addAction(self.scenes_rcItem_0)
        self.scenes_rcItem_0.triggered.connect(lambda: self.rcAction_scenes("importScene"))

        self.scenes_rcItem_1 = QtWidgets.QAction('Show Scene Folder in Explorer', self)
        self.popMenu_scenes.addAction(self.scenes_rcItem_1)
        self.scenes_rcItem_1.triggered.connect(lambda: self.rcAction_scenes("showInExplorerMaya"))

        self.scenes_rcItem_2 = QtWidgets.QAction('Show Preview Folder in Explorer', self)
        self.popMenu_scenes.addAction(self.scenes_rcItem_2)
        self.scenes_rcItem_2.triggered.connect(lambda: self.rcAction_scenes("showInExplorerPB"))

        self.scenes_rcItem_3 = QtWidgets.QAction('Show Data Folder in Explorer', self)
        self.popMenu_scenes.addAction(self.scenes_rcItem_3)
        self.scenes_rcItem_3.triggered.connect(lambda: self.rcAction_scenes("showInExplorerData"))

        self.scenes_rcItem_6 = QtWidgets.QAction('Show Project Folder in Explorer', self)
        self.popMenu_scenes.addAction(self.scenes_rcItem_6)
        self.scenes_rcItem_6.triggered.connect(lambda: self.rcAction_scenes("showInExplorerProject"))

        self.popMenu_scenes.addSeparator()
        self.scenes_rcItem_4 = QtWidgets.QAction('Scene Info', self)
        self.popMenu_scenes.addAction(self.scenes_rcItem_4)
        self.scenes_rcItem_4.triggered.connect(lambda: self.rcAction_scenes("showSceneInfo"))

        self.popMenu_scenes.addSeparator()
        self.scenes_rcItem_5 = QtWidgets.QAction('View Rendered Images', self)
        self.popMenu_scenes.addAction(self.scenes_rcItem_5)
        self.scenes_rcItem_5.triggered.connect(lambda: self.rcAction_scenes("viewRender"))



        # Thumbnail Right Click Menu
        self.thumbnail_label.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.thumbnail_label.customContextMenuRequested.connect(self.onContextMenu_thumbnail)
        self.popMenu_thumbnail = QtWidgets.QMenu()

        rcAction_thumb_0 = QtWidgets.QAction('Replace with current view', self)
        self.popMenu_thumbnail.addAction(rcAction_thumb_0)
        rcAction_thumb_0.triggered.connect(lambda: self.rcAction_thumb("currentView"))


        rcAction_thumb_1 = QtWidgets.QAction('Replace with external file', self)
        self.popMenu_thumbnail.addAction(rcAction_thumb_1)
        rcAction_thumb_1.triggered.connect(lambda: self.rcAction_thumb("file"))


        # SHORTCUTS
        # ---------

        # PyInstaller and Standalone version compatibility
        if FORCE_QT4:
            shortcutRefresh = Qt.QShortcut(QtWidgets.QKeySequence("F5"), self, self.refresh)
        else:
            shortcutRefresh = QtWidgets.QShortcut(QtGui.QKeySequence("F5"), self, self.refresh)

        # SIGNAL CONNECTIONS
        # ------------------

        createProject_fm.triggered.connect(self.createProjectUI)

        settings_fm.triggered.connect(self.settingsUI)

        deleteFile_fm.triggered.connect(self.onDeleteBaseScene)

        deleteReference_fm.triggered.connect(self.onDeleteReference)

        checkReferences_fm.triggered.connect(lambda: self.populateBaseScenes(deepCheck=True))

        imageViewer_mi.triggered.connect(self.onIviewer)
        projectMaterials_mi.triggered.connect(self.onPMaterials)
        self.assetLibrary_mi.triggered.connect(self.onAssetLibrary)
        self.createPB.triggered.connect(self.onCreatePreview)

        onlineHelp_mi.triggered.connect(lambda: webbrowser.open_new("http://www.ardakutlu.com/tik-manager-documentation/"))
        checkVersion_mi.triggered.connect(self.onCheckNewVersion)

        self.statusBar().showMessage("Status | Idle")

        self.load_radioButton.clicked.connect(self.onModeChange)
        self.reference_radioButton.clicked.connect(self.onModeChange)

        self.category_tabWidget.currentChanged.connect(self.onCategoryChange)

        self.scenes_listWidget.currentItemChanged.connect(self.onBaseSceneChange)

        self.version_comboBox.activated.connect(self.onVersionChange)

        self.makeReference_pushButton.clicked.connect(self.onMakeReference)

        self.subProject_comboBox.activated.connect(self.onSubProjectChange)

        self.user_comboBox.activated.connect(self.onUserChange)

        self.showPreview_pushButton.clicked.connect(self.onShowPreview)

        self.addSubProject_pushButton.clicked.connect(self.createSubProjectUI)

        self.setProject_pushButton.clicked.connect(self.setProjectUI)

        self.saveBaseScene_pushButton.clicked.connect(self.saveBaseSceneDialog)
        self.saveBaseScene_fm.triggered.connect(self.saveBaseSceneDialog)

        self.saveVersion_pushButton.clicked.connect(self.saveAsVersionDialog)
        self.saveVersion_fm.triggered.connect(self.saveAsVersionDialog)

        self.scenes_listWidget.doubleClicked.connect(self.onLoadScene)
        self.loadScene_pushButton.clicked.connect(self.onLoadScene)

        self.addNote_pushButton.clicked.connect(self.addNoteDialog)

        self.export_pushButton.clicked.connect(self.transferCentralUI)

    def createSubProjectUI(self):

        # This method is NOT Software Specific
        newSub, ok = QtWidgets.QInputDialog.getText(self, "Create New Sub-Project", "Enter an unique Sub-Project name:")
        if ok:
            if self.manager.nameCheck(newSub):
                self.subProject_comboBox.clear()
                self.subProject_comboBox.addItems(self.manager.createSubproject(newSub))
                self.subProject_comboBox.setCurrentIndex(self.manager.currentSubIndex)
                self.populateBaseScenes()
            else:
                self.infoPop(textTitle="Naming Error", textHeader="Naming Error",
                             textInfo="Choose an unique name with latin characters without spaces", type="C")

    def createProjectUI(self):
        createProject_Dialog = QtWidgets.QDialog(parent=self, windowTitle="Create New Project")
        createProject_Dialog.resize(420,220)

        masterLayout = QtWidgets.QVBoxLayout(createProject_Dialog)

        formLayout = QtWidgets.QFormLayout(spacing=15, labelAlignment=(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter))
        masterLayout.addLayout(formLayout)


        resolvedPath_lbl = QtWidgets.QLabel(createProject_Dialog, text="Fill the mandatory fields")
        formLayout.addRow(resolvedPath_lbl)

        projectRoot_lbl = QtWidgets.QLabel(createProject_Dialog, text="Projects Root")
        projectRoot_lbl.setFocus()
        projectRoot_hLay = QtWidgets.QHBoxLayout(spacing=4)
        projectRoot_le = QtWidgets.QLineEdit(text=os.path.abspath(os.path.join(self.manager.projectDir, os.pardir)))
        projectRoot_pb = QtWidgets.QPushButton(text="Browse")
        projectRoot_hLay.addWidget(projectRoot_le)
        projectRoot_hLay.addWidget(projectRoot_pb)
        formLayout.addRow(projectRoot_lbl, projectRoot_hLay)

        nameFields_hLay = QtWidgets.QHBoxLayout()

        brandName_vLay = QtWidgets.QVBoxLayout(spacing=6)
        brandName_lbl = QtWidgets.QLabel(text="Brand Name", alignment=QtCore.Qt.AlignCenter)
        brandName_le = QtWidgets.QLineEdit(placeholderText="(optional)")
        brandName_vLay.addWidget(brandName_lbl)
        brandName_vLay.addWidget(brandName_le)
        nameFields_hLay.addLayout(brandName_vLay)

        projectName_vLay = QtWidgets.QVBoxLayout(spacing=6)
        projectName_lbl = QtWidgets.QLabel(text="Project Name", alignment=QtCore.Qt.AlignCenter)
        projectName_le = QtWidgets.QLineEdit(placeholderText="Mandatory Field")
        projectName_vLay.addWidget(projectName_lbl)
        projectName_vLay.addWidget(projectName_le)
        nameFields_hLay.addLayout(projectName_vLay)

        client_vLay = QtWidgets.QVBoxLayout(spacing=6)
        client_lbl = QtWidgets.QLabel(text="Client", alignment=QtCore.Qt.AlignCenter)
        client_le = QtWidgets.QLineEdit(placeholderText="Mandatory Field")
        client_vLay.addWidget(client_lbl)
        client_vLay.addWidget(client_le)
        nameFields_hLay.addLayout(client_vLay)

        formLayout.addRow(nameFields_hLay)

        resolution_lbl = QtWidgets.QLabel(text="Resolution")
        resolution_hLay = QtWidgets.QHBoxLayout(spacing=4)
        resolutionX_spinBox = QtWidgets.QSpinBox(minimum=1, maximum=99999, value=1920, minimumWidth=(65), maximumWidth=(65), buttonSymbols=QtWidgets.QAbstractSpinBox.NoButtons)
        resolutionY_spinBox = QtWidgets.QSpinBox(minimum=1, maximum=99999, value=1080, minimumWidth=(65), maximumWidth=(65), buttonSymbols=QtWidgets.QAbstractSpinBox.NoButtons)
        resolution_hLay.addWidget(resolutionX_spinBox)
        resolution_hLay.addWidget(resolutionY_spinBox)
        formLayout.addRow(resolution_lbl, resolution_hLay)

        fps_lbl = QtWidgets.QLabel(text="FPS")
        fps_combo = QtWidgets.QComboBox(maximumWidth=(65))
        fps_combo.addItems(self.manager.fpsList)
        fps_combo.setCurrentIndex(13)
        formLayout.addRow(fps_lbl, fps_combo)

        createproject_buttonBox = QtWidgets.QDialogButtonBox(createProject_Dialog, orientation=QtCore.Qt.Horizontal)
        createproject_buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        createproject_buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).setMinimumSize(QtCore.QSize(100, 30))
        createproject_buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setMinimumSize(QtCore.QSize(100, 30))

        cp_button = createproject_buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
        cp_button.setText('Create Project')
        cp_button.setProperty("menuButton", True)

        masterLayout.addWidget(createproject_buttonBox)

        def browseProjectRoot():
            dlg = QtWidgets.QFileDialog()
            dlg.setFileMode(QtWidgets.QFileDialog.Directory)

            if dlg.exec_():
                # selectedroot = os.path.normpath(unicode(dlg.selectedFiles()[0]))
                selectedroot = os.path.normpath(unicode(dlg.selectedFiles()[0])).encode("utf-8")
                projectRoot_le.setText(selectedroot)
                resolve()


        def onCreateNewProject():
            root = os.path.normpath(unicode(projectRoot_le.text()).decode("utf-8"))
            if not self.manager.nameCheck(root, allowSpaces=True, directory=True):
                self.infoPop(textTitle="Non-Ascii Character", textHeader="Selected Project Root cannot be used",
                             textInfo="There are non-ascii characters in the selected path.", type="C")
                return
            if not os.path.isdir(root):
                self.infoPop(textTitle="Path Error", textHeader="Selected Project Root does not exist", type="C")
                return

            pName = unicode(projectName_le.text()).decode("utf-8")
            bName = unicode(brandName_le.text()).decode("utf-8")
            cName = unicode(client_le.text()).decode("utf-8")
            projectSettingsDB = {"Resolution": [resolutionX_spinBox.value(), resolutionY_spinBox.value()],
                                   "FPS": int(fps_combo.currentText())}

            pPath = self.manager.createNewProject(root, pName, bName, cName, settingsData=projectSettingsDB)
            if pPath:
                self.manager.setProject(pPath)
            # self.onProjectChange()

            self.initMainUI()
            createProject_Dialog.close()

        def resolve():
            if projectName_le.text() == "" or client_le.text() == "" or projectRoot_le.text() == "":
                resolvedPath_lbl.setText("Fill the mandatory fields")
                return
            resolvedPath = self.manager.resolveProjectPath(unicode(projectRoot_le.text()).decode("utf-8"),
                                                           unicode(projectName_le.text()).decode("utf-8"),
                                                           unicode(brandName_le.text()).decode("utf-8"),
                                                           unicode(client_le.text()).decode("utf-8"))
            resolvedPath_lbl.setText(resolvedPath)

        resolve()

        projectRoot_pb.clicked.connect(browseProjectRoot)

        brandName_le.textEdited.connect(lambda: resolve())
        projectName_le.textEdited.connect(lambda: resolve())
        client_le.textEdited.connect(lambda: resolve())

        createproject_buttonBox.accepted.connect(onCreateNewProject)
        createproject_buttonBox.rejected.connect(createProject_Dialog.reject)

        brandName_le.textChanged.connect(
            lambda: self._checkValidity(brandName_le.text(), cp_button,
                                        brandName_le))
        projectName_le.textChanged.connect(
            lambda: self._checkValidity(projectName_le.text(), cp_button,
                                        projectName_le))
        client_le.textChanged.connect(
            lambda: self._checkValidity(client_le.text(), cp_button, client_le))

        createProject_Dialog.show()


    def setProjectUI(self):

        # This method is NOT Software Specific

        self.setProject_Dialog = QtWidgets.QDialog(parent=self, windowTitle="SetProject")
        self.setProject_Dialog.resize(982, 450)
        self.setProject_Dialog.setFocus()

        gridLayout = QtWidgets.QGridLayout(self.setProject_Dialog)

        M1_horizontalLayout = QtWidgets.QHBoxLayout()

        lookIn_label = QtWidgets.QLabel(self.setProject_Dialog, text="Look in:")

        M1_horizontalLayout.addWidget(lookIn_label)

        self.lookIn_lineEdit = QtWidgets.QLineEdit(self.setProject_Dialog)

        M1_horizontalLayout.addWidget(self.lookIn_lineEdit)

        # a fake button which actually does nothing
        # fakeButton = QtWidgets.QPushButton(self.setProject_Dialog)
        # fakeButton.setVisible(False)


        browse_pushButton = QtWidgets.QPushButton(self.setProject_Dialog, text="Browse")

        M1_horizontalLayout.addWidget(browse_pushButton)

        self.back_pushButton = QtWidgets.QPushButton(self.setProject_Dialog)
        self.back_pushButton.setIcon(self.QIcon(":/icons/CSS/rc/arrow_left.png"))

        M1_horizontalLayout.addWidget(self.back_pushButton)

        self.forward_pushButton = QtWidgets.QPushButton(self.setProject_Dialog)
        self.forward_pushButton.setIcon(self.QIcon(":/icons/CSS/rc/arrow_right.png"))

        M1_horizontalLayout.addWidget(self.forward_pushButton)

        up_pushButton = QtWidgets.QPushButton(self.setProject_Dialog)
        up_pushButton.setIcon(self.QIcon(":/icons/CSS/rc/arrow_up.png"))
        up_pushButton.setShortcut((""))

        M1_horizontalLayout.addWidget(up_pushButton)

        gridLayout.addLayout(M1_horizontalLayout, 0, 0, 1, 1)

        M2_horizontalLayout = QtWidgets.QHBoxLayout()

        M2_splitter = QtWidgets.QSplitter(self.setProject_Dialog)
        M2_splitter.setHandleWidth(10)


        self.folders_treeView = QtWidgets.QTreeView(M2_splitter, minimumSize=QtCore.QSize(0,0), dragEnabled=True, dragDropMode=QtWidgets.QAbstractItemView.DragOnly,
                                                    selectionMode=QtWidgets.QAbstractItemView.SingleSelection, itemsExpandable=False, rootIsDecorated=False,
                                                    sortingEnabled=True, frameShape=QtWidgets.QFrame.NoFrame)

        verticalLayoutWidget = QtWidgets.QWidget(M2_splitter)

        M2_S2_verticalLayout = QtWidgets.QVBoxLayout(verticalLayoutWidget)
        M2_S2_verticalLayout.setContentsMargins(0, 10, 0, 10)
        M2_S2_verticalLayout.setSpacing(6)

        favorites_label = QtWidgets.QLabel(verticalLayoutWidget, text="Bookmarks:", font=self.headerBFont)

        M2_S2_verticalLayout.addWidget(favorites_label)

        self.favorites_listWidget = DropListWidget(verticalLayoutWidget)

        M2_S2_verticalLayout.addWidget(self.favorites_listWidget)
        M2_S2_horizontalLayout = QtWidgets.QHBoxLayout()

        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        M2_S2_horizontalLayout.addItem(spacerItem)

        remove_pushButton = QtWidgets.QPushButton(verticalLayoutWidget)
        remove_pushButton.setIcon(self.QIcon(":/icons/CSS/rc/minus.png"))

        M2_S2_horizontalLayout.addWidget(remove_pushButton)

        add_pushButton = QtWidgets.QPushButton(verticalLayoutWidget)
        add_pushButton.setIcon(self.QIcon(":/icons/CSS/rc/plus.png"))

        M2_S2_horizontalLayout.addWidget(add_pushButton)

        M2_S2_verticalLayout.addLayout(M2_S2_horizontalLayout)

        M2_horizontalLayout.addWidget(M2_splitter)

        gridLayout.addLayout(M2_horizontalLayout, 1, 0, 1, 1)

        M3_horizontalLayout = QtWidgets.QHBoxLayout()
        M3_horizontalLayout.setContentsMargins(0, 10, -1, -1)

        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        dirFilter_label = QtWidgets.QLabel(text="Search Filter")

        self.dirFilter_lineEdit = QtWidgets.QLineEdit(self.setProject_Dialog, maximumWidth=175)
        self.dirFilter_lineEdit.setFont(self.iconFont)
        self.dirFilter_lineEdit.setPlaceholderText("🔍".decode("utf-8"))

        M3_horizontalLayout.addWidget(dirFilter_label)
        M3_horizontalLayout.addWidget(self.dirFilter_lineEdit)

        M3_horizontalLayout.addItem(spacerItem1)

        setproject_buttonBox = QtWidgets.QDialogButtonBox(self.setProject_Dialog, orientation=QtCore.Qt.Horizontal)
        setproject_buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        setproject_buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).setMinimumSize(QtCore.QSize(100, 30))
        setproject_buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setMinimumSize(QtCore.QSize(100, 30))

        set_pushButton = setproject_buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
        set_pushButton.setText('Set')

        M3_horizontalLayout.addWidget(setproject_buttonBox, QtCore.Qt.AlignRight)

        gridLayout.addLayout(M3_horizontalLayout, 2, 0, 1, 1)

        verticalLayoutWidget.raise_()

        M2_splitter.setStretchFactor(0,1)

        ## Initial Stuff
        self.projectsRoot = os.path.abspath(os.path.join(self.manager.projectDir, os.pardir))
        self.browser = Browse()
        self.spActiveProjectPath = None
        self.__flagView = True

        self.sourceModel = QtWidgets.QFileSystemModel(nameFilterDisables=False)
        self.sourceModel.setNameFilters(["*"])

        self.sourceModel.setRootPath(self.projectsRoot)
        self.sourceModel.setFilter(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot | QtCore.QDir.Time)

        self.folders_treeView.setModel(self.sourceModel)
        self.folders_treeView.setRootIndex(self.sourceModel.index(self.projectsRoot))

        self.folders_treeView.setColumnWidth(0,400)
        self.folders_treeView.setColumnWidth(1,0)
        self.folders_treeView.setColumnWidth(2,0)

        self.favList = self.manager.loadFavorites()
        self.favorites_listWidget.addItems([x[0] for x in self.favList])

        self.lookIn_lineEdit.setText(self.projectsRoot)

        def navigate(command):
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
                dir = unicode(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")).encode("utf-8")
                if dir:
                    self.projectsRoot = dir
                    self.browser.addData(self.projectsRoot)

                else:
                    return

            if command == "folder":
                index = self.folders_treeView.currentIndex()
                self.projectsRoot = os.path.normpath(unicode(self.sourceModel.filePath(index)).encode("utf-8"))
                self.browser.addData(self.projectsRoot)

            if command == "lineEnter":
                dir = self.lookIn_lineEdit.text()
                if os.path.isdir(dir):
                    self.projectsRoot = dir
                    self.browser.addData(self.projectsRoot)

                else:
                    self.lookIn_lineEdit.setText(self.projectsRoot)

            self.sourceModel.setRootPath(self.projectsRoot)
            self.forward_pushButton.setDisabled(self.browser.isForwardLocked())
            self.back_pushButton.setDisabled(self.browser.isBackwardLocked())
            self.folders_treeView.setRootIndex(self.sourceModel.index(self.browser.getData()))
            self.lookIn_lineEdit.setText(self.browser.getData())

        def onRemoveFavs():

            row = self.favorites_listWidget.currentRow()
            if row == -1:
                return
            # item = self.favList[row]
            self.favList = self.manager.removeFromFavorites(row)
            # block the signal to prevent unwanted cycle

            self.favorites_listWidget.blockSignals(True)
            self.favorites_listWidget.takeItem(row)
            self.favorites_listWidget.blockSignals(False)

        def onAddFavs():
            index = self.folders_treeView.currentIndex()
            if index.row() == -1:  # no row selected, abort
                return
            fullPath = self.sourceModel.filePath(index)
            onDragAndDrop(fullPath)

        def onDragAndDrop(path):
            normPath = os.path.normpath(str(path))

            path, fName = os.path.split(normPath)
            if [fName, normPath] in self.favList:
                return
            self.favorites_listWidget.addItem(fName)
            self.favList = self.manager.addToFavorites(fName, normPath)

        def favoritesActivated():
            # block the signal to prevent unwanted cycle
            self.folders_treeView.selectionModel().blockSignals(True)
            row = self.favorites_listWidget.currentRow()
            self.spActiveProjectPath = self.favList[row][1]

            # clear the selection in folders view
            self.folders_treeView.setCurrentIndex(self.sourceModel.index(self.projectsRoot))
            self.folders_treeView.selectionModel().blockSignals(False)

        def foldersViewActivated():
            # block the signal to prevent unwanted cycle
            self.favorites_listWidget.blockSignals(True)
            index = self.folders_treeView.currentIndex()
            self.spActiveProjectPath = os.path.normpath(unicode(self.sourceModel.filePath(index)).encode("utf-8"))


            # clear the selection in favorites view
            self.favorites_listWidget.setCurrentRow(-1)
            self.favorites_listWidget.blockSignals(False)

        def setProject():
            if not self.manager.nameCheck(self.spActiveProjectPath, allowSpaces=True, directory=True):
                self.infoPop(textTitle="Invalid Path", textHeader="There are invalid (non-ascii) characters in the selected path.",
                             textInfo="This Path cannot be used", type="C")
                return
            self.manager.setProject(self.spActiveProjectPath)
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
        # self.folders_treeView.doubleClicked.connect(lambda index: navigate("folder", index=index))



        self.favorites_listWidget.currentItemChanged.connect(favoritesActivated)
        # self.folders_tableView.selectionModel().currentRowChanged.connect(foldersViewActivated)
        # There is a bug in here. If following two lines are run in a single line, a segmentation fault occurs and crashes 3ds max immediately
        selectionModel = self.folders_treeView.selectionModel()
        selectionModel.selectionChanged.connect(foldersViewActivated)

        self.favorites_listWidget.doubleClicked.connect(setProject)

        self.dirFilter_lineEdit.textChanged.connect(self._filterDirectories)

        set_pushButton.clicked.connect(setProject)

        self.setProject_Dialog.show()

    def transferCentralUI(self):

        try: self.transferCentral_Dialog.close()
        except AttributeError: pass

        sceneInfo = self.manager.getOpenSceneInfo()


        self.transferCentral_Dialog = QtWidgets.QDialog(parent=self, windowTitle="Transfer Central")
        self.transferCentral_Dialog.resize(460, 320)
        self.transferCentral_Dialog.setFocus()

        tc_verticalLayout = QtWidgets.QVBoxLayout(self.transferCentral_Dialog)

        # ----------
        # HEADER BAR
        # ----------
        margin = 5
        colorWidget = QtWidgets.QWidget(self.transferCentral_Dialog)
        headerLayout = QtWidgets.QHBoxLayout(colorWidget)
        headerLayout.setSpacing(0)
        try: headerLayout.setMargin(0)
        except AttributeError: pass

        tikIcon_label = QtWidgets.QLabel(self.centralwidget, alignment=(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter), scaledContents=False)
        tikIcon_label.setProperty("header", True)
        tikIcon_label.setMaximumWidth(125)
        try: tikIcon_label.setMargin(margin)
        except AttributeError: pass
        headerBitmap = self.Pixmap(":/icons/CSS/rc/tmTransfer.png")
        tikIcon_label.setPixmap(headerBitmap)

        headerLayout.addWidget(tikIcon_label)

        resolvedPath_label = QtWidgets.QLabel()
        resolvedPath_label.setProperty("header", True)
        try: resolvedPath_label.setMargin(margin)
        except AttributeError: pass
        resolvedPath_label.setIndent(2)
        resolvedPath_label.setFont(self.displayFont)
        resolvedPath_label.setWordWrap(True)

        headerLayout.addWidget(resolvedPath_label)

        tc_verticalLayout.addWidget(colorWidget)
        # ----------
        # ----------

        tabWidget = QtWidgets.QTabWidget(self.transferCentral_Dialog)
        exportTab = QtWidgets.QWidget()

        exp_verticalLayout = QtWidgets.QVBoxLayout(exportTab)
        currentProject_label = QtWidgets.QLabel(exportTab, text="Current Project:")
        currentProject_label.setAlignment(QtCore.Qt.AlignTop)
        exp_verticalLayout.addWidget(currentProject_label)

        formLayout = QtWidgets.QFormLayout()

        name_label = QtWidgets.QLabel(exportTab, text="Name:")
        formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, name_label)

        name_horizontalLayout = QtWidgets.QHBoxLayout()
        autoName_radioButton = QtWidgets.QRadioButton(exportTab, text="Auto from Scene/Object", checked=True)

        customName_radioButton = QtWidgets.QRadioButton(exportTab, text="Custom")

        naming_buttonGroup = QtWidgets.QButtonGroup(self.transferCentral_Dialog)
        naming_buttonGroup.addButton(autoName_radioButton)
        naming_buttonGroup.addButton(customName_radioButton)
        name_horizontalLayout.addWidget(autoName_radioButton)
        name_horizontalLayout.addWidget(customName_radioButton)

        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        name_horizontalLayout.addItem(spacerItem)
        formLayout.setLayout(0, QtWidgets.QFormLayout.FieldRole, name_horizontalLayout)

        customName_lineEdit = QtWidgets.QLineEdit(exportTab, placeholderText="Custom Export Name", frame=True)

        formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, customName_lineEdit)

        selection_label = QtWidgets.QLabel(exportTab, text="Selection:")
        formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, selection_label)

        selection_horizontalLayout = QtWidgets.QHBoxLayout()
        selection_radioButton = QtWidgets.QRadioButton(exportTab, text="Selection", checked=True)

        scene_radioButton = QtWidgets.QRadioButton(exportTab, text="Scene")

        sel_buttonGroup = QtWidgets.QButtonGroup(self.transferCentral_Dialog)
        sel_buttonGroup.addButton(selection_radioButton)
        selection_horizontalLayout.addWidget(selection_radioButton)
        sel_buttonGroup.addButton(scene_radioButton)
        selection_horizontalLayout.addWidget(scene_radioButton)

        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        selection_horizontalLayout.addItem(spacerItem1)

        formLayout.setLayout(2, QtWidgets.QFormLayout.FieldRole, selection_horizontalLayout)
        format_label = QtWidgets.QLabel(exportTab, text="Format:")
        formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, format_label)

        format_horizontalLayout = QtWidgets.QHBoxLayout()

        obj_checkBox = QtWidgets.QCheckBox(exportTab, text="Obj", checked=True)
        format_horizontalLayout.addWidget(obj_checkBox)

        alembic_checkBox = QtWidgets.QCheckBox(exportTab, text="Alembic", checked=False)
        format_horizontalLayout.addWidget(alembic_checkBox)

        fbx_checkBox = QtWidgets.QCheckBox(exportTab, text="FBX", checked=False)
        format_horizontalLayout.addWidget(fbx_checkBox)

        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        format_horizontalLayout.addItem(spacerItem2)
        formLayout.setLayout(3, QtWidgets.QFormLayout.FieldRole, format_horizontalLayout)

        range_label = QtWidgets.QLabel(exportTab, text="Time Range:")
        formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, range_label)

        timeRange_horizontalLayout1 = QtWidgets.QHBoxLayout()

        timeSlider_radioButton = QtWidgets.QRadioButton(exportTab, text="Time Slider", checked=True)

        timerange_buttonGroup = QtWidgets.QButtonGroup(self.transferCentral_Dialog)
        timerange_buttonGroup.addButton(timeSlider_radioButton)
        timeRange_horizontalLayout1.addWidget(timeSlider_radioButton)

        singleFrame_radioButton = QtWidgets.QRadioButton(exportTab, text="Single Frame", checked=False)
        timerange_buttonGroup.addButton(singleFrame_radioButton)
        timeRange_horizontalLayout1.addWidget(singleFrame_radioButton)

        customRange_radioButton = QtWidgets.QRadioButton(exportTab, text="Custom", checked=False)

        timerange_buttonGroup.addButton(customRange_radioButton)
        timeRange_horizontalLayout1.addWidget(customRange_radioButton)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        timeRange_horizontalLayout1.addItem(spacerItem3)
        formLayout.setLayout(4, QtWidgets.QFormLayout.FieldRole, timeRange_horizontalLayout1)

        timeRange_horizontalLayout2 = QtWidgets.QHBoxLayout()

        frameStart_label = QtWidgets.QLabel(exportTab, text="Start")

        timeRange_horizontalLayout2.addWidget(frameStart_label)

        frameStart_doubleSpinBox = QtWidgets.QDoubleSpinBox(exportTab, wrapping=False, frame=True, buttonSymbols=QtWidgets.QAbstractSpinBox.NoButtons, keyboardTracking=True)
        timeRange_horizontalLayout2.addWidget(frameStart_doubleSpinBox)
        spacerItem4 = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        timeRange_horizontalLayout2.addItem(spacerItem4)

        frameEnd_label = QtWidgets.QLabel(exportTab, text="End")
        timeRange_horizontalLayout2.addWidget(frameEnd_label)

        frameEnd_doubleSpinBox = QtWidgets.QDoubleSpinBox(exportTab, wrapping=False, frame=True, buttonSymbols=QtWidgets.QAbstractSpinBox.NoButtons, keyboardTracking=True, value=10.0)
        timeRange_horizontalLayout2.addWidget(frameEnd_doubleSpinBox)

        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        timeRange_horizontalLayout2.addItem(spacerItem5)
        formLayout.setLayout(5, QtWidgets.QFormLayout.FieldRole, timeRange_horizontalLayout2)

        exp_verticalLayout.addLayout(formLayout)

        spacerItem_m = QtWidgets.QSpacerItem(40, 40, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        exp_verticalLayout.addItem(spacerItem_m)

        expButtons_horizontalLayout = QtWidgets.QHBoxLayout()
        export_pushButton = QtWidgets.QPushButton(exportTab, text="Export")
        expButtons_horizontalLayout.addWidget(export_pushButton)
        exp_verticalLayout.addLayout(expButtons_horizontalLayout)
        cancel_pushButton = QtWidgets.QPushButton(exportTab, text="Cancel")
        expButtons_horizontalLayout.addWidget(cancel_pushButton)
        tabWidget.addTab(exportTab, ("Export"))

        ## ------------------
        ## ---IMPORT TAB-----
        ## ------------------

        importTab = QtWidgets.QWidget()
        imp_verticalLayout = QtWidgets.QVBoxLayout(importTab)
        transfers_treeWidget = QtWidgets.QTreeWidget(importTab)

        imp_verticalLayout.addWidget(transfers_treeWidget)
        impButtons_horizontalLayout = QtWidgets.QHBoxLayout()
        import_pushButton = QtWidgets.QPushButton(importTab, text="Import")
        impButtons_horizontalLayout.addWidget(import_pushButton)
        imp_verticalLayout.addLayout(impButtons_horizontalLayout)
        cancel_pushButton_2 = QtWidgets.QPushButton(importTab, text="Cancel")
        impButtons_horizontalLayout.addWidget(cancel_pushButton_2)
        tabWidget.addTab(importTab, ("Import"))
        tc_verticalLayout.addWidget(tabWidget)
        #

        def populateImports():
            if str(tabWidget.tabText(tabWidget.currentIndex())) != 'Import':
                return
            transfers_treeWidget.clear()
            obj_topLevel = QtWidgets.QTreeWidgetItem(["OBJ"])
            obj_topLevel.setBackground(0, QtGui.QBrush(QtGui.QColor("yellow")))
            obj_topLevel.setForeground(0, QtGui.QBrush(QtGui.QColor("black")))
            fbx_topLevel = QtWidgets.QTreeWidgetItem(["FBX"])
            fbx_topLevel.setBackground(0, QtGui.QBrush(QtGui.QColor("cyan")))
            fbx_topLevel.setForeground(0, QtGui.QBrush(QtGui.QColor("black")))
            alembic_topLevel = QtWidgets.QTreeWidgetItem(["ALEMBIC"])
            alembic_topLevel.setBackground(0, QtGui.QBrush(QtGui.QColor("magenta")))
            alembic_topLevel.setForeground(0, QtGui.QBrush(QtGui.QColor("black")))

            transfers_treeWidget.setHeaderLabels(["Transfer Items", "Path"])
            transfers_treeWidget.addTopLevelItem(obj_topLevel)
            transfers_treeWidget.addTopLevelItem(fbx_topLevel)
            transfers_treeWidget.addTopLevelItem(alembic_topLevel)

            self.importDict = self.manager.scanTransfers()
            for item in self.importDict["obj"].items():
                treeItem = QtWidgets.QTreeWidgetItem([item[0], item[1]])
                treeItem.setForeground(0, QtGui.QBrush(QtGui.QColor("yellow")))
                obj_topLevel.addChild(treeItem)
            for item in self.importDict["fbx"].items():
                treeItem = QtWidgets.QTreeWidgetItem([item[0], item[1]])
                treeItem.setForeground(0, QtGui.QBrush(QtGui.QColor("cyan")))
                fbx_topLevel.addChild(treeItem)
            for item in self.importDict["abc"].items():
                treeItem = QtWidgets.QTreeWidgetItem([item[0], item[1]])
                treeItem.setForeground(0, QtGui.QBrush(QtGui.QColor("magenta")))
                alembic_topLevel.addChild(treeItem)


        tabWidget.setCurrentIndex(0)

        def formatProof():
            timeRangeState = False
            if alembic_checkBox.isChecked() or fbx_checkBox.isChecked():
                timeRangeState = True

            timeSlider_radioButton.setEnabled(timeRangeState)
            singleFrame_radioButton.setEnabled(timeRangeState)
            customRange_radioButton.setEnabled(timeRangeState)
            frameStart_label.setEnabled(timeRangeState)
            frameStart_doubleSpinBox.setEnabled(timeRangeState)
            frameEnd_label.setEnabled(timeRangeState)
            frameEnd_doubleSpinBox.setEnabled(timeRangeState)

        def resolveName():
            # resolve name
            if not sceneInfo:
                customName_lineEdit.setProperty("error", True)
                customName_lineEdit.setStyleSheet("") # refresh
                customName_lineEdit.setText("Scene Needs to be saved as Base Scene")
                return
            customName_lineEdit.setProperty("error", False)
            customName_lineEdit.setStyleSheet("")

            if customName_radioButton.isChecked():
                customName_lineEdit.setText("")
                customName_lineEdit.setReadOnly(False)
                return
            else:
                if selection_radioButton.isChecked():
                    sel = self.manager._getSelection()
                    if len(sel) > 1:
                        name = "{0}/{0}_{1}_{2}sel".format(sceneInfo["shotName"], sceneInfo["version"], len(sel))
                    elif len(sel) == 1:
                        name = "{0}/{0}_{1}_{2}".format(sceneInfo["shotName"], sceneInfo["version"], sel[0])
                    else:
                        customName_lineEdit.setProperty("error", True)
                        customName_lineEdit.setStyleSheet("")  # refresh
                        customName_lineEdit.setText("No Object Selected")
                        return
                else:
                    name = "{0}/{0}_{1}".format(sceneInfo["shotName"], sceneInfo["version"])

            customName_lineEdit.setReadOnly(True)
            customName_lineEdit.setText(name)
            self._checkValidity(customName_lineEdit.text(), export_pushButton, customName_lineEdit, directory=True)

            return name


        resolveName()


        def executeExport():
            if not sceneInfo:
                self.infoPop(textTitle="Base Scene Not Saved",
                             textHeader="Current scene is not a Base Scene.\nBefore Exporting items, scene must be saved as Base Scene")
                self.transferCentral_Dialog.close()
                return
            # get time range:
            if timeSlider_radioButton.isChecked():
                wideRange = self.manager._getTimelineRanges()
                timeRange = wideRange[1:-1]
            elif customRange_radioButton.isChecked():
                timeRange = [frameStart_doubleSpinBox.value(), frameEnd_doubleSpinBox.value()]
            else:
                timeRange = [self.manager._getCurrentFrame(), self.manager._getCurrentFrame()]

            name = customName_lineEdit.text()

            isSelection = selection_radioButton.isChecked()
            isObj = obj_checkBox.isChecked()
            isAlembic = alembic_checkBox.isChecked()
            isFbx = fbx_checkBox.isChecked()
            res = self.manager.exportTransfers(name,
                                               isSelection=isSelection,
                                               isObj=isObj,
                                               isAlembic=isAlembic,
                                               isFbx=isFbx,
                                               timeRange=timeRange
                                               )
            self.infoPop(textTitle="Transfers Exported", textHeader="Transfers Exported under '_TRANSFER' folder")

        def executeImport():

            absPath = transfers_treeWidget.currentItem().text(1)
            if absPath:
                self.manager.importTransfers(absPath)

        def onContextMenu_transfers(point):
            if transfers_treeWidget.selectedItems()[0].text(1): # if there is a path info on the widget item
                popMenu_transfers.exec_(transfers_treeWidget.mapToGlobal(point))

        def importRc_actions(action):
            if action == "showInExplorer":
                manager = self._getManager()
                manager.showInExplorer(transfers_treeWidget.selectedItems()[0].text(1))
            if action == "execute":
                manager = self._getManager()
                manager.executeFile(transfers_treeWidget.selectedItems()[0].text(1))
        ## -----------------
        ## RIGHT CLICK MENUS
        ## -----------------
        transfers_treeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        transfers_treeWidget.customContextMenuRequested.connect(onContextMenu_transfers)
        popMenu_transfers = QtWidgets.QMenu()

        transfers_rcItem_0 = QtWidgets.QAction('Show in Explorer', self)
        popMenu_transfers.addAction(transfers_rcItem_0)
        transfers_rcItem_0.triggered.connect(lambda: importRc_actions("showInExplorer"))

        transfers_rcItem_1 = QtWidgets.QAction('Execute', self)
        popMenu_transfers.addAction(transfers_rcItem_1)
        transfers_rcItem_1.triggered.connect(lambda: importRc_actions("execute"))

        ## ------------------
        ## SIGNAL CONNECTIONS
        ## ------------------

        # Export Signals
        customName_lineEdit.textChanged.connect(lambda x: self._checkValidity(customName_lineEdit.text(), export_pushButton, customName_lineEdit, directory=True))
        obj_checkBox.toggled.connect(formatProof)
        alembic_checkBox.toggled.connect(formatProof)
        fbx_checkBox.toggled.connect(formatProof)

        export_pushButton.clicked.connect(executeExport)
        cancel_pushButton.clicked.connect(self.transferCentral_Dialog.close)

        autoName_radioButton.toggled.connect(resolveName)
        autoName_radioButton.clicked.connect(resolveName)
        selection_radioButton.clicked.connect(resolveName)
        scene_radioButton.clicked.connect(resolveName)

        # Import Signals
        cancel_pushButton_2.clicked.connect(self.transferCentral_Dialog.close)

        tabWidget.currentChanged.connect(populateImports)

        transfers_treeWidget.doubleClicked.connect(executeImport)
        import_pushButton.clicked.connect(executeImport)

        self.transferCentral_Dialog.show()

    def _filterDirectories(self):
        filterWord = self.dirFilter_lineEdit.text()
        self.DirFilter = [(unicode("*%s*" %filterWord))]
        self.sourceModel.setNameFilters(self.DirFilter)

    def settingsUI(self):
        self.allSettingsDict=Settings()

        self.minSPBSize = (70, 25)

        settings_Dialog = QtWidgets.QDialog(parent=self, windowTitle="Settings")
        settings_Dialog.resize(960, 630)

        verticalLayout_2 = QtWidgets.QVBoxLayout(settings_Dialog)

        try: verticalLayout_2.setMargin(0)
        except AttributeError: pass
        verticalLayout_2.setContentsMargins(10, 10 ,10 ,10)

        verticalLayout = QtWidgets.QVBoxLayout()
        verticalLayout.setSpacing(6)

        splitter = QtWidgets.QSplitter(settings_Dialog)
        splitter.setChildrenCollapsible(False)

        splitter.setLineWidth(0)
        splitter.setOrientation(QtCore.Qt.Horizontal)

        left_frame = QtWidgets.QFrame(splitter, minimumSize=QtCore.QSize(150, 0), frameShape=QtWidgets.QFrame.NoFrame, frameShadow=QtWidgets.QFrame.Plain)

        # left_frame.setMinimumSize(QtCore.QSize(150, 0))
        # left_frame.setMaximumSize(QtCore.QSize(16777215, 16777215))
        # left_frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        # left_frame.setFrameShadow(QtWidgets.QFrame.Plain)
        left_frame.setLineWidth(0)

        verticalLayout_4 = QtWidgets.QVBoxLayout(left_frame)
        verticalLayout_4.setSpacing(0)

        leftFrame_verticalLayout = QtWidgets.QVBoxLayout()
        leftFrame_verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        leftFrame_verticalLayout.setSpacing(6)

        self.settingsMenu_treeWidget = QtWidgets.QTreeWidget(left_frame)
        self.settingsMenu_treeWidget.setLineWidth(1)
        self.settingsMenu_treeWidget.setRootIsDecorated(True)
        self.settingsMenu_treeWidget.setHeaderHidden(True)

        self.settingsMenu_treeWidget.setFont(self.headerBFont)


        self.userSettings_item = QtWidgets.QTreeWidgetItem(["User Settings"])
        self.settingsMenu_treeWidget.addTopLevelItem(self.userSettings_item)

        # TOP ITEM
        self.projectSettings_item = QtWidgets.QTreeWidgetItem(["Project Settings"])
        self.settingsMenu_treeWidget.addTopLevelItem(self.projectSettings_item)

        # children
        self.previewSettings_item = QtWidgets.QTreeWidgetItem(["Preview Settings"])
        self.projectSettings_item.addChild(self.previewSettings_item)

        self.categories_item = QtWidgets.QTreeWidgetItem(["Categories"])
        self.projectSettings_item.addChild(self.categories_item)

        self.importExport_item = QtWidgets.QTreeWidgetItem(["Import/Export Options"])
        self.projectSettings_item.addChild(self.importExport_item)

        # TOP ITEM
        self.sharedSettings_item = QtWidgets.QTreeWidgetItem(["Shared Settings"])
        self.settingsMenu_treeWidget.addTopLevelItem(self.sharedSettings_item)

        # children
        self.users_item = QtWidgets.QTreeWidgetItem(["Users"])
        self.sharedSettings_item.addChild(self.users_item)

        self.passwords_item = QtWidgets.QTreeWidgetItem(["Passwords"])
        self.sharedSettings_item.addChild(self.passwords_item)

        self.namingConventions_item = QtWidgets.QTreeWidgetItem(["Naming Conventions"])
        self.sharedSettings_item.addChild(self.namingConventions_item)

        leftFrame_verticalLayout.addWidget(self.settingsMenu_treeWidget)
        verticalLayout_4.addLayout(leftFrame_verticalLayout)

        self.contents_frame = QtWidgets.QFrame(splitter)
        self.contents_frame.setEnabled(True)


        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.contents_frame)
        self.contents_Layout = QtWidgets.QVBoxLayout()
        self.contents_Layout.setSpacing(0)

        self.scrollArea = QtWidgets.QScrollArea(self.contents_frame)

        self.scrollArea.setWidgetResizable(True)

        self.scrollAreaWidgetContents_2 = QtWidgets.QWidget()

        self.contentsMaster_layout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents_2)
        try: self.contentsMaster_layout.setMargin(9)
        except AttributeError: pass
        self.contentsMaster_layout.setSpacing(9)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents_2)
        self.contents_Layout.addWidget(self.scrollArea)
        self.verticalLayout_5.addLayout(self.contents_Layout)
        verticalLayout.addWidget(splitter)

        ## CONTENTS START

        # Visibility Widgets for EACH page
        self.userSettings_vis = QtWidgets.QWidget()
        self.projectSettings_vis = QtWidgets.QWidget()
        self.previewSettings_vis = QtWidgets.QWidget()
        self.categories_vis = QtWidgets.QWidget()
        self.importExportOptions_vis = QtWidgets.QWidget()
        self.sharedSettings_vis = QtWidgets.QWidget()
        self.users_vis = QtWidgets.QWidget()
        self.passwords_vis = QtWidgets.QWidget()
        self.namingConventions_vis = QtWidgets.QWidget()


        def pageUpdate():
            if self.settingsMenu_treeWidget.currentItem().text(0) != "User Settings" and not self.superUser:
                passw, ok = QtWidgets.QInputDialog.getText(self, "Password Query",
                                                           "This Section requires Admin Password:", QtWidgets.QLineEdit.Password)

                if ok:
                    if self.manager.checkPassword(passw):
                        self.superUser = True
                        pass
                    else:
                        self.infoPop(textTitle="Incorrect Password", textHeader="The Password is invalid")
                        self.settingsMenu_treeWidget.setCurrentItem(self.userSettings_item)
                        return
                else:
                    self.settingsMenu_treeWidget.setCurrentItem(self.userSettings_item)

                    return

            allPages = {"User Settings": self.userSettings_vis,
                        "Project Settings": self.projectSettings_vis,
                        "Preview Settings": self.previewSettings_vis,
                        "Categories": self.categories_vis,
                        "Import/Export Options": self.importExportOptions_vis,
                        "Shared Settings": self.sharedSettings_vis,
                        "Users": self.users_vis,
                        "Passwords": self.passwords_vis,
                        "Naming Conventions": self.namingConventions_vis}
            for item in allPages.items():
                isVisible = False if item[0] == self.settingsMenu_treeWidget.currentItem().text(0) else True
                item[1].setHidden(isVisible)

        self.softwareDB = self.manager.loadSoftwareDatabase()


        ## USER SETTINGS
        currentUserSettings = self.manager.loadUserSettings()
        self.allSettingsDict.add("userSettings", currentUserSettings, self.manager._pathsDict["userSettingsFile"])
        currentCommonFolder = self.manager._getCommonFolder()
        self.allSettingsDict.add("sharedSettingsDir", currentCommonFolder, self.manager._pathsDict["commonFolderFile"])
        self._userSettingsContent()
        #
        #
        ## PROJECT SETTINGS
        currentProjectSettings = self.manager.loadProjectSettings()
        self.allSettingsDict.add("projectSettings", currentProjectSettings, self.manager._pathsDict["projectSettingsFile"])
        self._projectSettingsContent()

        ## PREVIEW SETTINGS
        self.previewMasterLayout = QtWidgets.QVBoxLayout(self.previewSettings_vis)
        sw = BoilerDict["Environment"].lower()
        #temp
        # sw="standalone"

        if sw == "maya" or sw == "standalone":
            settingsFilePathMaya = os.path.join(self.manager._pathsDict["previewsRoot"], self.softwareDB["Maya"]["pbSettingsFile"])
            currentMayaSettings = self.manager.loadPBSettings(filePath=settingsFilePathMaya)
            # backward compatibility:
            try:
                currentMayaSettings["ConvertMP4"]
                currentMayaSettings["CrfValue"]
            except KeyError:
                currentMayaSettings["ConvertMP4"] = True
                currentMayaSettings["CrfValue"] = 23

            # update the settings dictionary
            self.allSettingsDict.add("preview_maya", currentMayaSettings, settingsFilePathMaya)

            self._previewSettingsContent_maya()
        if sw == "3dsmax" or sw == "standalone":
            settingsFilePathMax = os.path.join(self.manager._pathsDict["previewsRoot"], self.softwareDB["3dsMax"]["pbSettingsFile"])
            currentMaxSettings = self.manager.loadPBSettings(filePath=settingsFilePathMax)
            # backward compatibility:
            try:
                currentMaxSettings["ConvertMP4"]
                currentMaxSettings["CrfValue"]
            except KeyError:
                currentMaxSettings["ConvertMP4"] = True
                currentMaxSettings["CrfValue"] = 23

            # update the settings dictionary
            self.allSettingsDict.add("preview_max", currentMaxSettings, settingsFilePathMax)

            self._previewSettingsContent_max()
        if sw == "houdini" or sw == "standalone":
            settingsFilePathHou = os.path.join(self.manager._pathsDict["previewsRoot"], self.softwareDB["Houdini"]["pbSettingsFile"])
            currentHoudiniSettings = self.manager.loadPBSettings(filePath=settingsFilePathHou)
            # backward compatibility:
            try:
                currentHoudiniSettings["ConvertMP4"]
                currentHoudiniSettings["CrfValue"]
            except KeyError:
                currentHoudiniSettings["ConvertMP4"] = True
                currentHoudiniSettings["CrfValue"] = 23

            # update the settings dictionary
            self.allSettingsDict.add("preview_houdini", currentHoudiniSettings, settingsFilePathHou)

            self._previewSettingsContent_houdini()

        self.contentsMaster_layout.addWidget(self.previewSettings_vis)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.previewMasterLayout.addItem(spacerItem)

        ## CATEGORIES
        #temp

        if sw == "standalone":
            # if it is standalone, get all categories for all softwares
            for value in self.softwareDB.values():
                niceName = value["niceName"]
                folderPath = os.path.normpath(os.path.join(self.manager._pathsDict["masterDir"], value["databaseDir"]))
                self.manager._folderCheck(folderPath)

                filePath = os.path.normpath(os.path.join(folderPath, value["categoriesFile"]))
                categoryData = self.manager.loadCategories(filePath=filePath, swName=niceName)
                self.allSettingsDict.add("categories_%s" %niceName, categoryData, filePath)
        else:
            currentCategories = self.manager.loadCategories()
            self.allSettingsDict.add("categories_%s" %self.manager.swName, currentCategories, self.manager._pathsDict["categoriesFile"])

        # pprint.pprint(self.allSettingsDict)

        self._categoriesContent()
        #
        ## IMPORT/EXPORT OPTIONS
        currentImportSettings = self.manager.loadImportSettings()
        self.allSettingsDict.add("importSettings", currentImportSettings, self.manager._pathsDict["importSettingsFile"])
        currentExportSettings = self.manager.loadExportSettings()
        self.allSettingsDict.add("exportSettings", currentExportSettings, self.manager._pathsDict["exportSettingsFile"])
        self._importExportContent()

        self._sharedSettingsContent()

        ## USERS
        currentUsers = self.manager.loadUsers()
        self.allSettingsDict.add("users", currentUsers, self.manager._pathsDict["usersFile"])
        self._usersContent()

        ## PASSWORDS
        self._passwordsContent()

        ## NAMING CONVENTIONS
        currentConventions = self.manager.loadNameConventions()
        self.allSettingsDict.add("nameConventions", currentConventions, self.manager._pathsDict["tikConventions"])
        self._namingConventions()

        self.settingsButtonBox = QtWidgets.QDialogButtonBox(settings_Dialog)
        self.settingsButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.settingsOk_btn = self.settingsButtonBox.button(QtWidgets.QDialogButtonBox.Ok)
        self.settingsOk_btn.setFocusPolicy(QtCore.Qt.NoFocus)

        self.settingsApply_btn = self.settingsButtonBox.button(QtWidgets.QDialogButtonBox.Apply)
        self.settingsApply_btn.setFocusPolicy(QtCore.Qt.NoFocus)
        verticalLayout.addWidget(self.settingsButtonBox)
        verticalLayout_2.addLayout(verticalLayout)

        settings_Dialog.setTabOrder(self.settingsButtonBox, self.settingsMenu_treeWidget)
        # self.settingsButtonBox.button(QtWidgets.QDialogButtonBox.Apply).setEnabled(False)
        self.settingsApply_btn.setEnabled(False)

        def applySettingChanges():
            for x in self.allSettingsDict.apply():
                self.manager._dumpJson(x["data"], x["filepath"])
            self.settingsApply_btn.setEnabled(False)
            self.initMainUI()

        # # SIGNALS
        # # -------
        #
        self.settingsMenu_treeWidget.currentItemChanged.connect(pageUpdate)
        self.settingsMenu_treeWidget.setCurrentItem(self.userSettings_item)

        self.settingsButtonBox.accepted.connect(applySettingChanges)
        self.settingsButtonBox.accepted.connect(settings_Dialog.accept)
        self.settingsApply_btn.clicked.connect(applySettingChanges)

        self.settingsButtonBox.rejected.connect(settings_Dialog.reject)

        splitter.setStretchFactor(1, 20)
        settings_Dialog.show()

    def _userSettingsContent(self):
        # manager = self._getManager()
        userSettings_Layout = QtWidgets.QVBoxLayout(self.userSettings_vis)
        userSettings_Layout.setSpacing(6)
        userSettings = self.allSettingsDict.get("userSettings")
        # sharedSettingsDir = self.allSettingsDict.get("sharedSettingsDir")


        def updateDictionary():
            # self.allSettingsDict["userSettings"]["newSettings"][
            #     "globalFavorites"] = globalFavorites_radiobutton.isChecked()
            userSettings["globalFavorites"] = globalFavorites_radiobutton.isChecked()

            enteredPath = os.path.normpath(unicode(commonDir_lineEdit.text()).encode("utf-8"))
            if self.manager._checkCommonFolder(enteredPath):
                self.allSettingsDict["sharedSettingsDir"]["newSettings"] = enteredPath
            else:
                commonDir_lineEdit.setText(self.allSettingsDict["sharedSettingsDir"]["oldSettings"])
                return

            self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())
            # self._isSettingsChanged()

        userSettings_formLayout = QtWidgets.QFormLayout()
        userSettings_formLayout.setSpacing(6)
        userSettings_formLayout.setHorizontalSpacing(15)
        userSettings_formLayout.setVerticalSpacing(15)
        userSettings_formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)

        userSettings_Layout.addLayout(userSettings_formLayout)

        # form item 0
        userSettings_label = QtWidgets.QLabel()
        userSettings_label.setFont(self.headerAFont)
        userSettings_label.setText(("User Settings"))
        userSettings_formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, userSettings_label)

        # form item 1
        favorites_label = QtWidgets.QLabel()
        favorites_label.setText("Project Favorites:")
        userSettings_formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, favorites_label)

        favorites_layout = QtWidgets.QHBoxLayout()
        globalFavorites_radiobutton = QtWidgets.QRadioButton()
        globalFavorites_radiobutton.setText("Global Favorites")
        globalFavorites_radiobutton.setChecked(self.manager.isGlobalFavorites())

        localFavorites_radiobutton = QtWidgets.QRadioButton()
        localFavorites_radiobutton.setText("Software Specific")
        localFavorites_radiobutton.setChecked(not self.manager.isGlobalFavorites())

        favorites_buttonGroup = QtWidgets.QButtonGroup(self.userSettings_vis)
        favorites_buttonGroup.addButton(globalFavorites_radiobutton)
        favorites_buttonGroup.addButton(localFavorites_radiobutton)
        favorites_layout.addWidget(globalFavorites_radiobutton)
        favorites_layout.addWidget(localFavorites_radiobutton)
        userSettings_formLayout.setLayout(1, QtWidgets.QFormLayout.FieldRole, favorites_layout)

        # form item 2
        commonDir_label = QtWidgets.QLabel()
        commonDir_label.setText("Common Settings Directory:")
        userSettings_formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, commonDir_label)

        commonDir_layout = QtWidgets.QHBoxLayout()
        commonDir_layout.setSpacing(2)

        commonDir_lineEdit = QtWidgets.QLineEdit()
        commonDir_lineEdit.setText(self.manager.getSharedSettingsDir())
        commonDir_lineEdit.setMinimumWidth(350)
        commonDir_layout.addWidget(commonDir_lineEdit)

        setCommon_button = QtWidgets.QPushButton()
        setCommon_button.setText("...")
        commonDir_layout.addWidget(setCommon_button)
        userSettings_formLayout.setLayout(2, QtWidgets.QFormLayout.FieldRole, commonDir_layout)

        # form item 3
        colorCoding_label = QtWidgets.QLabel()
        colorCoding_label.setText("Color Codes: ")
        userSettings_formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, colorCoding_label)

        colorCoding_formlayout = QtWidgets.QFormLayout()
        colorCoding_formlayout.setSpacing(2)
        colorCoding_formlayout.setVerticalSpacing(5)
        userSettings_formLayout.setLayout(3, QtWidgets.QFormLayout.FieldRole, colorCoding_formlayout)

        # Executable paths
        # header lbl
        executables_lbl = QtWidgets.QLabel()
        executables_lbl.setFont(self.headerBFont)
        executables_lbl.setText("Executable Paths")
        userSettings_formLayout.addRow(executables_lbl)

        executablesInfo_lbl = QtWidgets.QLabel()
        executablesInfo_lbl.setFont(self.infoFont)
        executablesInfo_lbl.setText("Defined executables will be used to run corresponding items. "
                                    "When left blank, system defaults will be used.\n\n"
                                    "If arguments want to be passed <itemPath> token can be used")
        executablesInfo_lbl.setWordWrap(True)
        userSettings_formLayout.addRow(executablesInfo_lbl)
        #images
        exeImages_lbl = QtWidgets.QLabel()
        exeImages_lbl.setText("Image viewer: ")
        exeImages_hlay = QtWidgets.QHBoxLayout(spacing=2)
        exeImages_le = QtWidgets.QLineEdit()
        try: exeImages_le.setText(userSettings["executables"]["image_exec"])
        except KeyError: pass
        exeImages_le.setMinimumWidth(350)
        exeImages_le.setPlaceholderText("Define an executable for images (Optional) ")
        exeImages_hlay.addWidget(exeImages_le)
        exeImages_btn = QtWidgets.QPushButton(text="...")
        exeImages_hlay.addWidget(exeImages_btn)
        userSettings_formLayout.addRow(exeImages_lbl, exeImages_hlay)
        #imageSeq
        exeImageSeq_lbl = QtWidgets.QLabel()
        exeImageSeq_lbl.setText("Sequence viewer: ")
        exeImageSeq_hlay = QtWidgets.QHBoxLayout(spacing=2)
        exeImageSeq_le = QtWidgets.QLineEdit()
        try: exeImageSeq_le.setText(userSettings["executables"]["imageSeq_exec"])
        except KeyError: pass
        exeImageSeq_le.setMinimumWidth(350)
        exeImageSeq_le.setPlaceholderText("Define an executable for imageSeq (Optional) ")
        exeImageSeq_hlay.addWidget(exeImageSeq_le)
        exeImageSeq_btn = QtWidgets.QPushButton(text="...")
        exeImageSeq_hlay.addWidget(exeImageSeq_btn)
        userSettings_formLayout.addRow(exeImageSeq_lbl, exeImageSeq_hlay)
        #Video Files
        exeVideo_lbl = QtWidgets.QLabel()
        exeVideo_lbl.setText("Video viewer: ")
        exeVideo_hlay = QtWidgets.QHBoxLayout(spacing=2)
        exeVideo_le = QtWidgets.QLineEdit()
        try: exeVideo_le.setText(userSettings["executables"]["video_exec"])
        except KeyError: pass
        exeVideo_le.setMinimumWidth(350)
        exeVideo_le.setPlaceholderText("Define an executable for video (Optional) ")
        exeVideo_hlay.addWidget(exeVideo_le)
        exeVideo_btn = QtWidgets.QPushButton(text="...")
        exeVideo_hlay.addWidget(exeVideo_btn)
        userSettings_formLayout.addRow(exeVideo_lbl, exeVideo_hlay)
        #Obj
        exeObj_lbl = QtWidgets.QLabel()
        exeObj_lbl.setText("Obj viewer: ")
        exeObj_hlay = QtWidgets.QHBoxLayout(spacing=2)
        exeObj_le = QtWidgets.QLineEdit()
        try: exeObj_le.setText(userSettings["executables"]["obj_exec"])
        except KeyError: pass
        exeObj_le.setMinimumWidth(350)
        exeObj_le.setPlaceholderText("Define an executable for obj (Optional) ")
        exeObj_hlay.addWidget(exeObj_le)
        exeObj_btn = QtWidgets.QPushButton(text="...")
        exeObj_hlay.addWidget(exeObj_btn)
        userSettings_formLayout.addRow(exeObj_lbl, exeObj_hlay)
        #Fbx
        exeFbx_lbl = QtWidgets.QLabel()
        exeFbx_lbl.setText("Fbx viewer: ")
        exeFbx_hlay = QtWidgets.QHBoxLayout(spacing=2)
        exeFbx_le = QtWidgets.QLineEdit()
        try: exeFbx_le.setText(userSettings["executables"]["fbx_exec"])
        except KeyError: pass
        exeFbx_le.setMinimumWidth(350)
        exeFbx_le.setPlaceholderText("Define an executable for fbx (Optional) ")
        exeFbx_hlay.addWidget(exeFbx_le)
        exeFbx_btn = QtWidgets.QPushButton(text="...")
        exeFbx_hlay.addWidget(exeFbx_btn)
        userSettings_formLayout.addRow(exeFbx_lbl, exeFbx_hlay)
        #Abc
        exeAbc_lbl = QtWidgets.QLabel()
        exeAbc_lbl.setText("Alembic viewer: ")
        exeAbc_hlay = QtWidgets.QHBoxLayout(spacing=2)
        exeAbc_le = QtWidgets.QLineEdit()
        try: exeAbc_le.setText(userSettings["executables"]["alembic_exec"])
        except KeyError: pass
        exeAbc_le.setMinimumWidth(350)
        exeAbc_le.setPlaceholderText("Define an executable for abc (Optional) ")
        exeAbc_hlay.addWidget(exeAbc_le)
        exeAbc_btn = QtWidgets.QPushButton(text="...")
        exeAbc_hlay.addWidget(exeAbc_btn)
        userSettings_formLayout.addRow(exeAbc_lbl, exeAbc_hlay)


        def colorSet(button, niceName):
            color = QtWidgets.QColorDialog.getColor()
            button.setStyleSheet("background-color: %s; min-width: 80px;" % color.name())
            userSettings["colorCoding"][niceName] = "rgb%s" % str(color.getRgb())
            # self.allSettingsDict["userSettings"]["newSettings"]["colorCoding"][niceName] = "rgb%s" % str(color.getRgb())
            self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())

        def resetColors():
            try:
                defaults = deepcopy(self.manager._sceneManagerDefaults["defaultColorCoding"])
                for key in userSettings["colorCoding"].keys():
                    userSettings["colorCoding"][key] = defaults[key]
            except KeyError:
                self.infoPop(textTitle="Cannot get default database",
                             textHeader="Default Color Coding Database cannot be found")
                return
            for item in userSettings["colorCoding"].items():
                niceName = item[0]
                color = item[1]
                # try:
                pushbutton = self.findChild(QtWidgets.QPushButton, "cc_%s" % niceName)
                pushbutton.setStyleSheet("background-color:%s; min-width: 80px;" % color)
                # except AttributeError:
                #     pass
            self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())

        def browseCommonDatabase():
            dlg = QtWidgets.QFileDialog()
            dlg.setFileMode(QtWidgets.QFileDialog.Directory)

            if dlg.exec_():
                # selectedroot = os.path.normpath(unicode(dlg.selectedFiles()[0]))
                selectedroot = os.path.normpath(unicode(dlg.selectedFiles()[0])).encode("utf-8")
                if self.manager._checkCommonFolder(selectedroot):
                    commonDir_lineEdit.setText(selectedroot)
                else:
                    return
            updateDictionary()
            # self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())

            # self._isSettingsChanged()
            return

        def editExecutable(lineEdit):
            dbItem = (unicode(lineEdit.text()).encode("utf-8"))
            try:
                userSettings["executables"][str(lineEdit.objectName())] = dbItem
            except KeyError:
                userSettings["executables"]={"image_exec": "",
                                             "imageSeq_exec": "",
                                             "video_exec": "",
                                             "obj_exec": "",
                                             "fbx_exec": "",
                                             "alembic_exec": ""}
                userSettings["executables"][str(lineEdit.objectName())] = dbItem
            self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())
            return

        def browseExecutable(lineEdit):
            dlg = QtWidgets.QFileDialog()
            dlg.setFileMode(QtWidgets.QFileDialog.ExistingFile)

            if dlg.exec_():
                selectedFile = os.path.normpath(unicode(dlg.selectedFiles()[0])).encode("utf-8")
                dbItem = (unicode(selectedFile).encode("utf-8"))
                lineEdit.setText(dbItem)
                try:
                    userSettings["executables"][str(lineEdit.objectName())] = dbItem
                except KeyError:
                    userSettings["executables"]={"image_exec": "",
                                                 "imageSeq_exec": "",
                                                 "video_exec": "",
                                                 "obj_exec": "",
                                                 "fbx_exec": "",
                                                 "alembic_exec": ""}
                    userSettings["executables"][str(lineEdit.objectName())] = dbItem
            self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())
            return

        # colorCoding = self.allSettingsDict.get("userSettings")["colorCoding"]
        # for item in colorCoding.items():
        for item in userSettings["colorCoding"].items():
            cclabel = QtWidgets.QLabel()
            if item[0] == "":
                cclabel.setText("      Standalone:  ")
            else:
                cclabel.setText("      %s:  " % item[0])
            ccpushbutton = QtWidgets.QPushButton()
            ccpushbutton.setObjectName("cc_%s" % item[0])
            ccpushbutton.setStyleSheet("background-color:%s; min-width: 80px;" % item[1])
            ccpushbutton.setMinimumSize(80, 20)

            colorCoding_formlayout.addRow(cclabel, ccpushbutton)
            ccpushbutton.clicked.connect(lambda ignore=item[0], button=ccpushbutton, item=item[0]: colorSet(button, item))


        ccReset_button = QtWidgets.QPushButton()
        ccReset_button.setText("Reset Colors")
        ccReset_button.setMinimumSize(80, 30)
        # ccReset_button.setFixedSize(150, 30)
        colorCoding_formlayout.setWidget((len(userSettings["colorCoding"].items())) + 1, QtWidgets.QFormLayout.FieldRole, ccReset_button)
        # colorCoding_formlayout.setWidget((len(niceNameList)) + 1, QtWidgets.QFormLayout.FieldRole, ccReset_button)

        # end of form

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        userSettings_Layout.addItem(spacerItem)
        self.contentsMaster_layout.addWidget(self.userSettings_vis)

        # SIGNALS USER SETTINGS
        # ---------------------
        ccReset_button.clicked.connect(resetColors)
        setCommon_button.clicked.connect(browseCommonDatabase)

        globalFavorites_radiobutton.clicked.connect(updateDictionary)
        localFavorites_radiobutton.clicked.connect(updateDictionary)
        # commonDir_lineEdit.textChanged.connect(updateDictionary)
        commonDir_lineEdit.editingFinished.connect(updateDictionary)

        exeImages_btn.clicked.connect(lambda: browseExecutable(exeImages_le))
        exeImageSeq_btn.clicked.connect(lambda: browseExecutable(exeImageSeq_le))
        exeVideo_btn.clicked.connect(lambda: browseExecutable(exeVideo_le))
        exeObj_btn.clicked.connect(lambda: browseExecutable(exeObj_le))
        exeFbx_btn.clicked.connect(lambda: browseExecutable(exeFbx_le))
        exeAbc_btn.clicked.connect(lambda: browseExecutable(exeAbc_le))

        exeImages_le.editingFinished.connect(lambda: editExecutable(exeImages_le))
        exeImageSeq_le.editingFinished.connect(lambda: editExecutable(exeImageSeq_le))
        exeVideo_le.editingFinished.connect(lambda: editExecutable(exeVideo_le))
        exeObj_le.editingFinished.connect(lambda: editExecutable(exeObj_le))
        exeFbx_le.editingFinished.connect(lambda: editExecutable(exeFbx_le))
        exeAbc_le.editingFinished.connect(lambda: editExecutable(exeAbc_le))

    def _projectSettingsContent(self):
        manager = self._getManager()
        settings = self.allSettingsDict.get("projectSettings")

        def updateDictionary():
            settings["Resolution"] = [resolutionX_spinBox.value(), resolutionY_spinBox.value()]
            settings["FPS"] = float(fps_comboBox.currentText())

            self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())

        projectSettings_Layout = QtWidgets.QVBoxLayout(self.projectSettings_vis)
        projectSettings_Layout.setSpacing(0)

        h1_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_label = QtWidgets.QLabel(self.projectSettings_vis)
        h1_label.setText("Project Settings")
        h1_label.setFont(self.headerAFont)
        h1_horizontalLayout.addWidget(h1_label)
        projectSettings_Layout.addLayout(h1_horizontalLayout)

        projectSettings_formLayout = QtWidgets.QFormLayout()
        # projectSettings_formLayout.setSpacing(2)
        # projectSettings_formLayout.setVerticalSpacing(5)

        # projectSettings_formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        # projectSettings_formLayout.setLabelAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        # projectSettings_formLayout.setFormAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        projectSettings_formLayout.setSpacing(6)
        projectSettings_formLayout.setHorizontalSpacing(15)
        projectSettings_formLayout.setVerticalSpacing(5)
        projectSettings_formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)

        projectSettings_formLayout.setContentsMargins(-1, 15, -1, -1)

        currentProject_lbl = QtWidgets.QLabel()
        currentProject_lbl.setText("Project")
        project_hLayout = QtWidgets.QHBoxLayout()
        currentProject_le = QtWidgets.QLineEdit()
        currentProject_le.setText(self.manager.getProjectDir())
        currentProject_le.setReadOnly(True)
        currentProject_le.setMinimumWidth(500)
        project_hLayout.addWidget(currentProject_le)

        projectSettings_formLayout.addRow(currentProject_lbl, project_hLayout)

        resolution_label = QtWidgets.QLabel(self.projectSettings_vis)
        resolution_label.setText("Resolution: ")
        resolution_label.setMinimumSize(70, 25)

        resolution_hLay = QtWidgets.QHBoxLayout()
        resolution_hLay.setSpacing(5)

        resolutionX_spinBox = QtWidgets.QSpinBox(self.projectSettings_vis)
        resolutionX_spinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        resolutionX_spinBox.setMinimumSize(self.minSPBSize[0], self.minSPBSize[1])
        resolution_hLay.addWidget(resolutionX_spinBox)
        resolutionX_spinBox.setRange(1, 99999)
        resolutionX_spinBox.setValue(settings["Resolution"][0])

        resolutionY_spinBox = QtWidgets.QSpinBox(self.projectSettings_vis)
        resolutionY_spinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        resolutionY_spinBox.setMinimumSize(self.minSPBSize[0], self.minSPBSize[1])
        resolution_hLay.addWidget(resolutionY_spinBox)
        resolutionY_spinBox.setRange(1, 99999)
        resolutionY_spinBox.setValue(settings["Resolution"][1])

        projectSettings_formLayout.addRow(resolution_label, resolution_hLay)

        fps_label = QtWidgets.QLabel(self.projectSettings_vis)
        fps_label.setText("FPS: ")
        fps_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)

        fps_comboBox = QtWidgets.QComboBox(self.projectSettings_vis)
        # fps_comboBox.setMaximumSize(QtCore.QSize(60, 16777215))
        fps_comboBox.addItems(self.manager.fpsList)
        try:
            index = self.manager.fpsList.index(str(settings["FPS"]))
        except:
            index = 13
        fps_comboBox.setCurrentIndex(index)

        projectSettings_formLayout.addRow(fps_label, fps_comboBox)

        projectSettings_Layout.addLayout(projectSettings_formLayout)

        # projectSettings_label = QtWidgets.QLabel(self.projectSettings_vis)
        # projectSettings_label.setText("Project Settings")
        # projectSettings_label.setFont(self.headerAFont)
        # projectSettings_label.setIndent(10)
        # projectSettings_label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        # projectSettings_Layout.addWidget(projectSettings_label)

        cmdButtons_layout = QtWidgets.QVBoxLayout()
        cmdButtons_layout.setContentsMargins(-1, 15, -1, -1)
        projectSettings_Layout.addLayout(cmdButtons_layout)

        previewSettings_cmdButton = QtWidgets.QCommandLinkButton()
        previewSettings_cmdButton.setText("Preview Settings")
        cmdButtons_layout.addWidget(previewSettings_cmdButton)

        categories_cmdButton = QtWidgets.QCommandLinkButton()
        categories_cmdButton.setText("Categories")
        cmdButtons_layout.addWidget(categories_cmdButton)

        importExportOptions_cmdButton = QtWidgets.QCommandLinkButton()
        importExportOptions_cmdButton.setText("Import/Export Options")
        cmdButtons_layout.addWidget(importExportOptions_cmdButton)

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        projectSettings_Layout.addItem(spacerItem)
        self.contentsMaster_layout.addWidget(self.projectSettings_vis)

        # SIGNALS
        # setProject_pb.clicked.connect(self.setProjectUI)
        resolutionX_spinBox.valueChanged.connect(updateDictionary)
        resolutionY_spinBox.valueChanged.connect(updateDictionary)
        fps_comboBox.currentIndexChanged.connect(updateDictionary)

        previewSettings_cmdButton.clicked.connect(lambda: self.settingsMenu_treeWidget.setCurrentItem(self.previewSettings_item))
        categories_cmdButton.clicked.connect(lambda: self.settingsMenu_treeWidget.setCurrentItem(self.categories_item))
        importExportOptions_cmdButton.clicked.connect(lambda: self.settingsMenu_treeWidget.setCurrentItem(self.importExport_item))

    def _previewSettingsContent_maya(self):
        # manager = self._getManager()
        settings = self.allSettingsDict.get("preview_maya")
        def updateMayaCodecs():
            codecList = self.manager.getFormatsAndCodecs()[self.format_Maya_comboBox.currentText()]
            self.codec_Maya_comboBox.clear()
            self.codec_Maya_comboBox.addItems(codecList)

        previewSettings_MAYA_Layout = QtWidgets.QVBoxLayout()
        previewSettings_MAYA_Layout.setSpacing(0)

        def toggleMp4():
            state = self.convertMP4_Maya_chb.isChecked()
            self.crf_Maya_spinBox.setEnabled(state)
            self.format_Maya_comboBox.setDisabled(state)
            self.codec_Maya_comboBox.setDisabled(state)
            self.quality_Maya_spinBox.setDisabled(state)

        def updateDictionary():

            settings["ConvertMP4"] = self.convertMP4_Maya_chb.isChecked()
            settings["CrfValue"] = self.crf_Maya_spinBox.value()
            settings["Format"] = self.format_Maya_comboBox.currentText()
            settings["Codec"] = self.codec_Maya_comboBox.currentText()
            settings["Quality"] = self.quality_Maya_spinBox.value()
            settings["Resolution"] = [self.resX_Maya_spinBox.value(), self.resY_Maya_spinBox.value()]
            settings["PolygonOnly"] = self.polygonOnly_Maya_chb.isChecked()
            settings["ShowGrid"] = self.showGrid_Maya_chb.isChecked()
            settings["ClearSelection"] = self.clearSelection_Maya_chb.isChecked()
            settings["DisplayTextures"] = self.displayTextures_Maya_chb.isChecked()
            settings["WireOnShaded"] = self.wireOnShaded_Maya_chb.isChecked()
            settings["UseDefaultMaterial"] = self.useDefaultMaterial_Maya_chb.isChecked()
            settings["ShowFrameNumber"] = self.frameNumber_Maya_chb.isChecked()
            settings["ShowCategory"] = self.category_Maya_chb.isChecked()
            settings["ShowSceneName"] = self.sceneName_Maya_chb.isChecked()
            settings["ShowFPS"] = self.fps_Maya_chb.isChecked()
            settings["ShowFrameRange"] = self.frameRange_Maya_chb.isChecked()

            self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())


        ## HEADER
        h1_horizontalLayout = QtWidgets.QHBoxLayout()
        # h1_horizontalLayout.setContentsMargins(-1, -1, -1, 10)
        h1_label = QtWidgets.QLabel()
        h1_label.setText("Maya Playblast Settings")
        h1_label.setFont(self.headerAFont)
        h1_horizontalLayout.addWidget(h1_label)
        previewSettings_MAYA_Layout.addLayout(h1_horizontalLayout)

        ## VIDEO PROPERTIES
        h1_s1_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_s1_horizontalLayout.setContentsMargins(-1, 15, -1, -1)
        h1_s1_label = QtWidgets.QLabel()
        h1_s1_label.setText("Video Properties  ")
        h1_s1_label.setFont(self.headerBFont)
        h1_s1_horizontalLayout.addWidget(h1_s1_label)

        h1_s1_line = QtWidgets.QLabel()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        h1_s1_line.setSizePolicy(sizePolicy)
        # h1_s1_line.setStyleSheet("background-color: gray;")
        h1_s1_line.setProperty("seperator", True)
        h1_s1_horizontalLayout.addWidget(h1_s1_line)
        try: h1_s1_line.setMargin(0)
        except AttributeError: pass
        h1_s1_line.setIndent(0)
        h1_s1_line.setMaximumHeight(1)
        previewSettings_MAYA_Layout.addLayout(h1_s1_horizontalLayout)

        h1_s2_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_s2_horizontalLayout.setContentsMargins(20, 10, -1, -1)
        h1_s2_horizontalLayout.setSpacing(6)

        videoProperties_formLayout = QtWidgets.QFormLayout()
        videoProperties_formLayout.setSpacing(6)
        videoProperties_formLayout.setHorizontalSpacing(15)
        videoProperties_formLayout.setVerticalSpacing(10)
        videoProperties_formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
        h1_s2_horizontalLayout.addLayout(videoProperties_formLayout)

        self.convertMP4_Maya_chb = QtWidgets.QCheckBox()
        self.convertMP4_Maya_chb.setText("Convert To MP4")
        self.convertMP4_Maya_chb.setMinimumSize(QtCore.QSize(100, 0))
        self.convertMP4_Maya_chb.setLayoutDirection(QtCore.Qt.LeftToRight)
        # videoProperties_formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.convertMP4_Maya_chb)
        videoProperties_formLayout.addRow(self.convertMP4_Maya_chb)
        if self.manager.currentPlatform is not "Windows":
            self.convertMP4_Maya_chb.setChecked(False)
            self.convertMP4_Maya_chb.setEnabled(False)
        else:
            try:
                self.convertMP4_Maya_chb.setChecked(settings["ConvertMP4"])
            except KeyError:
                self.convertMP4_Maya_chb.setChecked(True)

        crf_Maya_label = QtWidgets.QLabel()
        crf_Maya_label.setText("Compression (0-51)")

        self.crf_Maya_spinBox = QtWidgets.QSpinBox()
        self.crf_Maya_spinBox.setMinimumSize(self.minSPBSize[0], self.minSPBSize[1])
        self.crf_Maya_spinBox.setMinimum(0)
        self.crf_Maya_spinBox.setMaximum(51)
        self.crf_Maya_spinBox.setValue(settings["CrfValue"])
        videoProperties_formLayout.addRow(crf_Maya_label, self.crf_Maya_spinBox)

        format_label = QtWidgets.QLabel()
        format_label.setText("Format: ")
        self.format_Maya_comboBox = QtWidgets.QComboBox()
        videoProperties_formLayout.addRow(format_label, self.format_Maya_comboBox)

        formatsAndCodecs = self.manager.getFormatsAndCodecs()
        if not formatsAndCodecs:
            self.format_Maya_comboBox.setEnabled(False)
        else:
            try:
                self.format_Maya_comboBox.addItems(formatsAndCodecs.keys())
                # get the index number from the name in the settings file and make that index active
                ffindex = self.format_Maya_comboBox.findText(settings["Format"], QtCore.Qt.MatchFixedString)
                if ffindex >= 0:
                    self.format_Maya_comboBox.setCurrentIndex(ffindex)
            except:
                pass

        codec_label = QtWidgets.QLabel()
        codec_label.setText("Codec: ")
        self.codec_Maya_comboBox = QtWidgets.QComboBox()
        videoProperties_formLayout.addRow(codec_label, self.codec_Maya_comboBox)

        if not formatsAndCodecs:
            self.codec_Maya_comboBox.setEnabled(False)
        else:
            updateMayaCodecs()

        self.format_Maya_comboBox.currentIndexChanged.connect(updateMayaCodecs)

        quality_label = QtWidgets.QLabel()
        quality_label.setText("Quality: ")
        self.quality_Maya_spinBox = QtWidgets.QSpinBox()
        self.quality_Maya_spinBox.setMinimumSize(self.minSPBSize[0], self.minSPBSize[1])
        self.quality_Maya_spinBox.setMinimum(1)
        self.quality_Maya_spinBox.setMaximum(100)
        self.quality_Maya_spinBox.setValue(settings["Quality"])
        videoProperties_formLayout.addRow(quality_label, self.quality_Maya_spinBox)

        resolution_label = QtWidgets.QLabel()
        resolution_label.setText("Resolution: ")
        resolution_horizontalLayout = QtWidgets.QHBoxLayout()
        resolution_horizontalLayout.setSpacing(5)
        self.resX_Maya_spinBox = QtWidgets.QSpinBox()
        self.resX_Maya_spinBox.setMinimumSize(self.minSPBSize[0], self.minSPBSize[1])
        self.resX_Maya_spinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.resX_Maya_spinBox.setMinimum(1)
        self.resX_Maya_spinBox.setMaximum(99999)
        self.resX_Maya_spinBox.setValue(settings["Resolution"][0])
        resolution_horizontalLayout.addWidget(self.resX_Maya_spinBox)
        self.resY_Maya_spinBox = QtWidgets.QSpinBox()
        self.resY_Maya_spinBox.setMinimumSize(self.minSPBSize[0], self.minSPBSize[1])
        self.resY_Maya_spinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.resY_Maya_spinBox.setMinimum(1)
        self.resY_Maya_spinBox.setMaximum(99999)
        self.resY_Maya_spinBox.setValue(settings["Resolution"][1])
        resolution_horizontalLayout.addWidget(self.resY_Maya_spinBox)
        videoProperties_formLayout.addRow(resolution_label, resolution_horizontalLayout)

        previewSettings_MAYA_Layout.addLayout(h1_s2_horizontalLayout)

        ## VIEWPORT OPTIONS
        h1_s3_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_s3_horizontalLayout.setContentsMargins(-1, 30, -1, -1)
        h1_s3_label = QtWidgets.QLabel()
        h1_s3_label.setText("Viewport Options  ")
        h1_s3_label.setFont(self.headerBFont)
        h1_s3_horizontalLayout.addWidget(h1_s3_label)

        h1_s3_line = QtWidgets.QLabel()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        h1_s3_line.setSizePolicy(sizePolicy)
        h1_s3_line.setProperty("seperator", True)
        h1_s3_horizontalLayout.addWidget(h1_s3_line)
        try: h1_s3_line.setMargin(0)
        except AttributeError: pass
        h1_s3_line.setIndent(0)
        h1_s3_line.setMaximumHeight(1)
        previewSettings_MAYA_Layout.addLayout(h1_s3_horizontalLayout)

        h1_s4_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_s4_horizontalLayout.setContentsMargins(20, 10, -1, -1)

        viewportOptions_gridLayout = QtWidgets.QGridLayout()
        # viewportOptions_gridLayout.setContentsMargins(-1, 15, -1, -1)
        h1_s4_horizontalLayout.addLayout(viewportOptions_gridLayout)

        self.polygonOnly_Maya_chb = QtWidgets.QCheckBox()
        self.polygonOnly_Maya_chb.setText("Polygon Only")
        viewportOptions_gridLayout.addWidget(self.polygonOnly_Maya_chb, 0, 0)
        self.polygonOnly_Maya_chb.setChecked(settings["PolygonOnly"])

        self.showGrid_Maya_chb = QtWidgets.QCheckBox()
        self.showGrid_Maya_chb.setText("Show Grid")
        viewportOptions_gridLayout.addWidget(self.showGrid_Maya_chb, 0, 1)
        self.showGrid_Maya_chb.setChecked(settings["ShowGrid"])

        self.clearSelection_Maya_chb = QtWidgets.QCheckBox()
        self.clearSelection_Maya_chb.setText("Clear Selection")
        viewportOptions_gridLayout.addWidget(self.clearSelection_Maya_chb, 1, 0)
        self.clearSelection_Maya_chb.setChecked(settings["ClearSelection"])

        self.displayTextures_Maya_chb = QtWidgets.QCheckBox()
        self.displayTextures_Maya_chb.setText("Display Textures")
        viewportOptions_gridLayout.addWidget(self.displayTextures_Maya_chb, 1, 1)
        self.displayTextures_Maya_chb.setChecked(settings["DisplayTextures"])

        self.wireOnShaded_Maya_chb = QtWidgets.QCheckBox()
        self.wireOnShaded_Maya_chb.setText("Wire On Shaded")
        viewportOptions_gridLayout.addWidget(self.wireOnShaded_Maya_chb, 2, 0)
        self.wireOnShaded_Maya_chb.setChecked(settings["WireOnShaded"])

        self.useDefaultMaterial_Maya_chb = QtWidgets.QCheckBox()
        self.useDefaultMaterial_Maya_chb.setText("Use Default Material")
        viewportOptions_gridLayout.addWidget(self.useDefaultMaterial_Maya_chb, 2, 1)
        self.useDefaultMaterial_Maya_chb.setChecked(settings["UseDefaultMaterial"])


        previewSettings_MAYA_Layout.addLayout(h1_s4_horizontalLayout)

        ## HUD OPTIONS
        h1_s5_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_s5_horizontalLayout.setContentsMargins(-1, 30, -1, -1)
        h1_s5_label = QtWidgets.QLabel()
        h1_s5_label.setText("Heads Up Display Options  ")
        h1_s5_label.setFont(self.headerBFont)
        h1_s5_horizontalLayout.addWidget(h1_s5_label)

        h1_s5_line = QtWidgets.QLabel()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        h1_s5_line.setSizePolicy(sizePolicy)
        h1_s5_line.setProperty("seperator", True)
        h1_s5_horizontalLayout.addWidget(h1_s5_line)
        try: h1_s5_line.setMargin(0)
        except AttributeError: pass
        h1_s5_line.setIndent(0)
        h1_s5_line.setMaximumHeight(1)
        previewSettings_MAYA_Layout.addLayout(h1_s5_horizontalLayout)

        h1_s6_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_s6_horizontalLayout.setContentsMargins(20, 10, -1, 30)

        hudOptions_gridLayout = QtWidgets.QGridLayout()
        h1_s6_horizontalLayout.addLayout(hudOptions_gridLayout)

        self.frameNumber_Maya_chb = QtWidgets.QCheckBox()
        self.frameNumber_Maya_chb.setText("Frame Number")
        hudOptions_gridLayout.addWidget(self.frameNumber_Maya_chb, 0, 0)
        self.frameNumber_Maya_chb.setChecked(settings["ShowFrameNumber"])

        self.category_Maya_chb = QtWidgets.QCheckBox()
        self.category_Maya_chb.setText("Category")
        hudOptions_gridLayout.addWidget(self.category_Maya_chb, 0, 1)
        self.category_Maya_chb.setChecked(settings["ShowCategory"])


        self.sceneName_Maya_chb = QtWidgets.QCheckBox()
        self.sceneName_Maya_chb.setText("Scene Name")
        hudOptions_gridLayout.addWidget(self.sceneName_Maya_chb, 1, 0)
        self.sceneName_Maya_chb.setChecked(settings["ShowSceneName"])


        self.fps_Maya_chb = QtWidgets.QCheckBox()
        self.fps_Maya_chb.setText("FPS")
        hudOptions_gridLayout.addWidget(self.fps_Maya_chb, 1, 1)
        self.fps_Maya_chb.setChecked(settings["ShowFPS"])


        self.frameRange_Maya_chb = QtWidgets.QCheckBox()
        self.frameRange_Maya_chb.setText("Frame Range")
        hudOptions_gridLayout.addWidget(self.frameRange_Maya_chb, 2, 0)
        self.frameRange_Maya_chb.setChecked(settings["ShowFrameRange"])


        previewSettings_MAYA_Layout.addLayout(h1_s6_horizontalLayout)

        self.previewMasterLayout.addLayout(previewSettings_MAYA_Layout)

        toggleMp4()

        ## SIGNALS
        ## -------

        self.convertMP4_Maya_chb.stateChanged.connect(toggleMp4)
        self.convertMP4_Maya_chb.stateChanged.connect(updateDictionary)

        self.crf_Maya_spinBox.valueChanged.connect(updateDictionary)
        self.format_Maya_comboBox.currentIndexChanged.connect(updateDictionary)
        self.codec_Maya_comboBox.currentIndexChanged.connect(updateDictionary)
        self.quality_Maya_spinBox.valueChanged.connect(updateDictionary)
        self.resX_Maya_spinBox.valueChanged.connect(updateDictionary)
        self.resY_Maya_spinBox.valueChanged.connect(updateDictionary)
        self.polygonOnly_Maya_chb.stateChanged.connect(updateDictionary)
        self.showGrid_Maya_chb.stateChanged.connect(updateDictionary)
        self.clearSelection_Maya_chb.stateChanged.connect(updateDictionary)
        self.displayTextures_Maya_chb.stateChanged.connect(updateDictionary)
        self.wireOnShaded_Maya_chb.stateChanged.connect(updateDictionary)
        self.useDefaultMaterial_Maya_chb.stateChanged.connect(updateDictionary)
        self.frameNumber_Maya_chb.stateChanged.connect(updateDictionary)
        self.category_Maya_chb.stateChanged.connect(updateDictionary)
        self.sceneName_Maya_chb.stateChanged.connect(updateDictionary)
        self.fps_Maya_chb.stateChanged.connect(updateDictionary)
        self.frameRange_Maya_chb.stateChanged.connect(updateDictionary)

        # spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        # previewMasterLayout.addItem(spacerItem)

        # self.contentsMaster_layout.addWidget(self.previewSettings_vis)

    def _previewSettingsContent_max(self):
        # manager = self._getManager()
        # settings = self.allSettingsDict["preview_max"]["oldSettings"]
        settings = self.allSettingsDict.get("preview_max")

        previewSettings_MAX_Layout = QtWidgets.QVBoxLayout()
        previewSettings_MAX_Layout.setSpacing(0)


        def updateDictionary():
            settings["ConvertMP4"] = self.convertMP4_Max_chb.isChecked()
            settings["CrfValue"] = self.crf_Max_spinBox.value()
            settings["Resolution"] = [self.resX_Max_spinBox.value(), self.resY_Max_spinBox.value()]
            settings["PolygonOnly"] = self.polygonOnly_Max_chb.isChecked()
            settings["ShowGrid"] = self.showGrid_Max_chb.isChecked()
            settings["ClearSelection"] = self.clearSelection_Max_chb.isChecked()
            settings["WireOnShaded"] = self.wireOnShaded_Max_chb.isChecked()
            settings["ShowFrameNumber"] = self.frameNumber_Max_chb.isChecked()

            self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())
            # self._isSettingsChanged()

        ## HEADER
        h1_horizontalLayout = QtWidgets.QHBoxLayout()
        # h1_horizontalLayout.setContentsMargins(-1, -1, -1, 10)
        h1_label = QtWidgets.QLabel(self.previewSettings_vis)
        h1_label.setText("3ds Max Preview Animation Settings")
        h1_label.setFont(self.headerAFont)
        h1_horizontalLayout.addWidget(h1_label)
        previewSettings_MAX_Layout.addLayout(h1_horizontalLayout)

        ## VIDEO PROPERTIES
        h1_s1_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_s1_horizontalLayout.setContentsMargins(-1, 15, -1, -1)
        h1_s1_label = QtWidgets.QLabel()
        h1_s1_label.setText("Video Properties  ")
        h1_s1_label.setFont(self.headerBFont)
        h1_s1_horizontalLayout.addWidget(h1_s1_label)

        h1_s1_line = QtWidgets.QLabel()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        h1_s1_line.setSizePolicy(sizePolicy)
        h1_s1_line.setProperty("seperator", True)
        h1_s1_horizontalLayout.addWidget(h1_s1_line)
        try: h1_s1_line.setMargin(0)
        except AttributeError: pass
        h1_s1_line.setIndent(0)
        h1_s1_line.setMaximumHeight(1)
        previewSettings_MAX_Layout.addLayout(h1_s1_horizontalLayout)

        h1_s2_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_s2_horizontalLayout.setContentsMargins(20, 10, -1, -1)
        h1_s2_horizontalLayout.setSpacing(6)

        videoProperties_formLayout = QtWidgets.QFormLayout()
        videoProperties_formLayout.setSpacing(6)
        videoProperties_formLayout.setHorizontalSpacing(15)
        videoProperties_formLayout.setVerticalSpacing(10)
        videoProperties_formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
        h1_s2_horizontalLayout.addLayout(videoProperties_formLayout)

        self.convertMP4_Max_chb = QtWidgets.QCheckBox()
        self.convertMP4_Max_chb.setText("Convert To MP4")
        self.convertMP4_Max_chb.setMinimumSize(QtCore.QSize(100, 0))
        self.convertMP4_Max_chb.setLayoutDirection(QtCore.Qt.LeftToRight)
        # videoProperties_formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.convertMP4_Max_chb)
        videoProperties_formLayout.addRow(self.convertMP4_Max_chb)
        if self.manager.currentPlatform is not "Windows":
            self.convertMP4_Max_chb.setChecked(False)
            self.convertMP4_Max_chb.setEnabled(False)
        else:
            try:
                self.convertMP4_Max_chb.setChecked(settings["ConvertMP4"])
            except KeyError:
                self.convertMP4_Max_chb.setChecked(True)

        crf_Max_label = QtWidgets.QLabel()
        crf_Max_label.setText("Compression (0-51)")

        self.crf_Max_spinBox = QtWidgets.QSpinBox()
        self.crf_Max_spinBox.setMinimumSize(self.minSPBSize[0], self.minSPBSize[1])
        self.crf_Max_spinBox.setMinimum(0)
        self.crf_Max_spinBox.setMaximum(51)
        self.crf_Max_spinBox.setValue(settings["CrfValue"])
        videoProperties_formLayout.addRow(crf_Max_label, self.crf_Max_spinBox)

        resolution_label = QtWidgets.QLabel()
        resolution_label.setText("Resolution: ")
        resolution_horizontalLayout = QtWidgets.QHBoxLayout()
        self.resX_Max_spinBox = QtWidgets.QSpinBox()
        self.resX_Max_spinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.resX_Max_spinBox.setMinimumSize(self.minSPBSize[0], self.minSPBSize[1])
        self.resX_Max_spinBox.setMinimum(1)
        self.resX_Max_spinBox.setMaximum(99999)
        self.resX_Max_spinBox.setValue(settings["Resolution"][0])
        resolution_horizontalLayout.addWidget(self.resX_Max_spinBox)
        self.resY_Max_spinBox = QtWidgets.QSpinBox()
        self.resY_Max_spinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.resY_Max_spinBox.setMinimumSize(self.minSPBSize[0], self.minSPBSize[1])
        self.resY_Max_spinBox.setMinimum(1)
        self.resY_Max_spinBox.setMaximum(99999)
        self.resY_Max_spinBox.setValue(settings["Resolution"][1])
        resolution_horizontalLayout.addWidget(self.resY_Max_spinBox)
        videoProperties_formLayout.addRow(resolution_label, resolution_horizontalLayout)

        previewSettings_MAX_Layout.addLayout(h1_s2_horizontalLayout)

        ## VIEWPORT OPTIONS
        h1_s3_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_s3_horizontalLayout.setContentsMargins(-1, 30, -1, -1)
        h1_s3_label = QtWidgets.QLabel()
        h1_s3_label.setText("Viewport Options  ")
        h1_s3_label.setFont(self.headerBFont)
        h1_s3_horizontalLayout.addWidget(h1_s3_label)

        h1_s3_line = QtWidgets.QLabel()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        h1_s3_line.setSizePolicy(sizePolicy)
        h1_s3_line.setProperty("seperator", True)
        h1_s3_horizontalLayout.addWidget(h1_s3_line)
        try: h1_s3_line.setMargin(0)
        except AttributeError: pass
        h1_s3_line.setIndent(0)
        h1_s3_line.setMaximumHeight(1)
        previewSettings_MAX_Layout.addLayout(h1_s3_horizontalLayout)

        h1_s4_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_s4_horizontalLayout.setContentsMargins(20, 10, -1, -1)

        viewportOptions_gridLayout = QtWidgets.QGridLayout()
        h1_s4_horizontalLayout.addLayout(viewportOptions_gridLayout)

        self.polygonOnly_Max_chb = QtWidgets.QCheckBox()
        self.polygonOnly_Max_chb.setText("Polygon Only")
        viewportOptions_gridLayout.addWidget(self.polygonOnly_Max_chb, 0, 0)
        self.polygonOnly_Max_chb.setChecked(settings["PolygonOnly"])

        self.showGrid_Max_chb = QtWidgets.QCheckBox()
        self.showGrid_Max_chb.setText("Show Grid")
        viewportOptions_gridLayout.addWidget(self.showGrid_Max_chb, 0, 1)
        self.showGrid_Max_chb.setChecked(settings["ShowGrid"])

        self.clearSelection_Max_chb = QtWidgets.QCheckBox()
        self.clearSelection_Max_chb.setText("Clear Selection")
        viewportOptions_gridLayout.addWidget(self.clearSelection_Max_chb, 1, 0)
        self.clearSelection_Max_chb.setChecked(settings["ClearSelection"])

        self.wireOnShaded_Max_chb = QtWidgets.QCheckBox()
        self.wireOnShaded_Max_chb.setText("Wire On Shaded")
        viewportOptions_gridLayout.addWidget(self.wireOnShaded_Max_chb, 1, 1)
        self.wireOnShaded_Max_chb.setChecked(settings["WireOnShaded"])

        previewSettings_MAX_Layout.addLayout(h1_s4_horizontalLayout)

        ## HUD OPTIONS
        h1_s5_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_s5_horizontalLayout.setContentsMargins(-1, 30, -1, -1)
        h1_s5_label = QtWidgets.QLabel()
        h1_s5_label.setText("Heads Up Display Options  ")
        h1_s5_label.setFont(self.headerBFont)
        h1_s5_horizontalLayout.addWidget(h1_s5_label)

        h1_s5_line = QtWidgets.QLabel()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        h1_s5_line.setSizePolicy(sizePolicy)
        h1_s5_line.setProperty("seperator", True)
        h1_s5_horizontalLayout.addWidget(h1_s5_line)
        try: h1_s5_line.setMargin(0)
        except AttributeError: pass
        h1_s5_line.setIndent(0)
        h1_s5_line.setMaximumHeight(1)
        previewSettings_MAX_Layout.addLayout(h1_s5_horizontalLayout)

        h1_s6_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_s6_horizontalLayout.setContentsMargins(20, 10, -1, -1)

        hudOptions_gridLayout = QtWidgets.QGridLayout()
        h1_s6_horizontalLayout.addLayout(hudOptions_gridLayout)

        self.frameNumber_Max_chb = QtWidgets.QCheckBox()
        self.frameNumber_Max_chb.setText("Frame Number")
        hudOptions_gridLayout.addWidget(self.frameNumber_Max_chb, 0, 0)
        self.frameNumber_Max_chb.setChecked(settings["ShowFrameNumber"])

        previewSettings_MAX_Layout.addLayout(h1_s6_horizontalLayout)

        self.previewMasterLayout.addLayout(previewSettings_MAX_Layout)

        ## SIGNALS
        ## -------

        self.convertMP4_Max_chb.stateChanged.connect(updateDictionary)
        self.convertMP4_Max_chb.stateChanged.connect(lambda: self.crf_Max_spinBox.setEnabled(self.convertMP4_Max_chb.isChecked()))

        self.crf_Max_spinBox.valueChanged.connect(updateDictionary)
        self.resX_Max_spinBox.valueChanged.connect(updateDictionary)
        self.resY_Max_spinBox.valueChanged.connect(updateDictionary)
        self.polygonOnly_Max_chb.stateChanged.connect(updateDictionary)
        self.showGrid_Max_chb.stateChanged.connect(updateDictionary)
        self.clearSelection_Max_chb.stateChanged.connect(updateDictionary)
        self.wireOnShaded_Max_chb.stateChanged.connect(updateDictionary)
        self.frameNumber_Max_chb.stateChanged.connect(updateDictionary)

        # spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        # self.previewMasterLayout.addItem(spacerItem)

        # self.contentsMaster_layout.addWidget(self.previewSettings_vis)

    def _previewSettingsContent_houdini(self):
        # manager = self._getManager()
        # settings = self.allSettingsDict["preview_houdini"]["oldSettings"]
        settings = self.allSettingsDict.get("preview_houdini")

        previewSettings_HOU_Layout = QtWidgets.QVBoxLayout()
        previewSettings_HOU_Layout.setSpacing(0)


        def updateDictionary():
            settings["ConvertMP4"] = self.convertMP4_Houdini_chb.isChecked()
            settings["CrfValue"] = self.crf_Houdini_spinBox.value()
            settings["Resolution"] = [self.resX_Houdini_spinBox.value(), self.resY_Houdini_spinBox.value()]

            self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())
            # self._isSettingsChanged()

        ## HEADER
        h1_horizontalLayout = QtWidgets.QHBoxLayout()
        # h1_horizontalLayout.setContentsMargins(-1, -1, -1, 10)
        h1_label = QtWidgets.QLabel(self.previewSettings_vis)
        h1_label.setText("Houdini Flipbook Settings")
        h1_label.setFont(self.headerAFont)
        h1_horizontalLayout.addWidget(h1_label)
        previewSettings_HOU_Layout.addLayout(h1_horizontalLayout)

        ## VIDEO PROPERTIES
        h1_s1_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_s1_horizontalLayout.setContentsMargins(-1, 15, -1, -1)
        h1_s1_label = QtWidgets.QLabel()
        h1_s1_label.setText("Video Properties  ")
        h1_s1_label.setFont(self.headerBFont)
        h1_s1_horizontalLayout.addWidget(h1_s1_label)

        h1_s1_line = QtWidgets.QLabel()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        h1_s1_line.setSizePolicy(sizePolicy)
        h1_s1_line.setProperty("seperator", True)
        h1_s1_horizontalLayout.addWidget(h1_s1_line)
        try: h1_s1_line.setMargin(0)
        except AttributeError: pass
        h1_s1_line.setIndent(0)
        h1_s1_line.setMaximumHeight(1)
        previewSettings_HOU_Layout.addLayout(h1_s1_horizontalLayout)

        h1_s2_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_s2_horizontalLayout.setContentsMargins(20, 10, -1, -1)
        h1_s2_horizontalLayout.setSpacing(6)

        videoProperties_formLayout = QtWidgets.QFormLayout()
        videoProperties_formLayout.setSpacing(6)
        videoProperties_formLayout.setHorizontalSpacing(15)
        videoProperties_formLayout.setVerticalSpacing(10)
        videoProperties_formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
        h1_s2_horizontalLayout.addLayout(videoProperties_formLayout)

        self.convertMP4_Houdini_chb = QtWidgets.QCheckBox()
        self.convertMP4_Houdini_chb.setText("Convert To MP4")
        self.convertMP4_Houdini_chb.setMinimumSize(QtCore.QSize(100, 0))
        self.convertMP4_Houdini_chb.setLayoutDirection(QtCore.Qt.LeftToRight)
        # videoProperties_formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.convertMP4_Houdini_chb)
        videoProperties_formLayout.addRow(self.convertMP4_Houdini_chb)
        if self.manager.currentPlatform is not "Windows":
            self.convertMP4_Houdini_chb.setChecked(False)
            self.convertMP4_Houdini_chb.setEnabled(False)
        else:
            try:
                self.convertMP4_Houdini_chb.setChecked(settings["ConvertMP4"])
            except KeyError:
                self.convertMP4_Houdini_chb.setChecked(True)

        crf_Houdini_label = QtWidgets.QLabel()
        crf_Houdini_label.setText("Compression (0-51)")

        self.crf_Houdini_spinBox = QtWidgets.QSpinBox()
        self.crf_Houdini_spinBox.setMinimumSize(self.minSPBSize[0], self.minSPBSize[1])
        self.crf_Houdini_spinBox.setMinimum(0)
        self.crf_Houdini_spinBox.setMaximum(51)
        self.crf_Houdini_spinBox.setValue(settings["CrfValue"])
        videoProperties_formLayout.addRow(crf_Houdini_label, self.crf_Houdini_spinBox)

        resolution_label = QtWidgets.QLabel()
        resolution_label.setText("Resolution: ")
        resolution_horizontalLayout = QtWidgets.QHBoxLayout()
        self.resX_Houdini_spinBox = QtWidgets.QSpinBox()
        self.resX_Houdini_spinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.resX_Houdini_spinBox.setMinimumSize(self.minSPBSize[0], self.minSPBSize[1])
        self.resX_Houdini_spinBox.setMinimum(1)
        self.resX_Houdini_spinBox.setMaximum(99999)
        self.resX_Houdini_spinBox.setValue(settings["Resolution"][0])
        resolution_horizontalLayout.addWidget(self.resX_Houdini_spinBox)
        self.resY_Houdini_spinBox = QtWidgets.QSpinBox()
        self.resY_Houdini_spinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.resY_Houdini_spinBox.setMinimumSize(self.minSPBSize[0], self.minSPBSize[1])
        self.resY_Houdini_spinBox.setMinimum(1)
        self.resY_Houdini_spinBox.setMaximum(99999)
        self.resY_Houdini_spinBox.setValue(settings["Resolution"][1])
        resolution_horizontalLayout.addWidget(self.resY_Houdini_spinBox)
        videoProperties_formLayout.addRow(resolution_label, resolution_horizontalLayout)

        previewSettings_HOU_Layout.addLayout(h1_s2_horizontalLayout)

        self.previewMasterLayout.addLayout(previewSettings_HOU_Layout)

        ## SIGNALS
        ## -------

        self.convertMP4_Houdini_chb.stateChanged.connect(updateDictionary)
        self.convertMP4_Houdini_chb.stateChanged.connect(lambda: self.crf_Houdini_spinBox.setEnabled(self.convertMP4_Houdini_chb.isChecked()))

        self.crf_Houdini_spinBox.valueChanged.connect(updateDictionary)
        self.resX_Houdini_spinBox.valueChanged.connect(updateDictionary)
        self.resY_Houdini_spinBox.valueChanged.connect(updateDictionary)

    def _categoriesContent(self):
        # manager = self._getManager()
        categorySwList = [key for key in self.allSettingsDict.listNames() if key.startswith("categories")]

        categories_Layout = QtWidgets.QVBoxLayout(self.categories_vis)
        categories_Layout.setSpacing(0)

        h1_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_label = QtWidgets.QLabel()
        h1_label.setText("Add/Remove Categories")
        h1_label.setFont(self.headerAFont)
        h1_horizontalLayout.addWidget(h1_label)
        categories_Layout.addLayout(h1_horizontalLayout)

        h1_s1_layout = QtWidgets.QVBoxLayout()
        h1_s1_layout.setContentsMargins(-1, 15, -1, -1)

        swTabs = QtWidgets.QTabWidget()
        swTabs.setMaximumSize(QtCore.QSize(16777215, 167777))
        swTabs.setTabPosition(QtWidgets.QTabWidget.North)
        swTabs.setElideMode(QtCore.Qt.ElideNone)
        swTabs.setUsesScrollButtons(False)

        def onRemove(settingKey, listWidget):
            row = listWidget.currentRow()
            if row == -1:
                return
            trashCategory = unicode(listWidget.currentItem().text()).decode("utf-8")
            categories = self.allSettingsDict.get(settingKey)
            ## check if this is the last category
            if len(categories) == 1:
                self.infoPop(textTitle="Cannot Remove Category",
                             textHeader="Last Category cannot be removed")

            ## Check if this category is REALLY trash
            niceName=settingKey.replace("categories_", "")
            dbPath = os.path.normpath(os.path.join(manager._pathsDict["masterDir"], self.softwareDB[niceName]["databaseDir"]))

            if self.manager.isCategoryTrash(trashCategory, dbPath=dbPath):
                categories.remove(trashCategory)
                listWidget.clear()
                listWidget.addItems(categories)
            else:
                self.infoPop(textTitle="Cannot Remove Category",
                             textHeader="%s Category is not empty. Aborting..." % trashCategory)
            self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())


        def onAdd(settingKey, listWidget):
            addCategory_Dialog = QtWidgets.QDialog(parent=self)
            addCategory_Dialog.resize(260, 114)
            addCategory_Dialog.setMaximumSize(QtCore.QSize(16777215, 150))
            addCategory_Dialog.setFocusPolicy(QtCore.Qt.ClickFocus)
            addCategory_Dialog.setWindowTitle(("Add New Category"))

            verticalLayout = QtWidgets.QVBoxLayout(addCategory_Dialog)

            addNewCategory_label = QtWidgets.QLabel(addCategory_Dialog)
            addNewCategory_label.setText("Add New Category:")
            verticalLayout.addWidget(addNewCategory_label)

            categoryName_lineEdit = QtWidgets.QLineEdit(addCategory_Dialog)
            categoryName_lineEdit.setPlaceholderText("e.g \'Shading\'")
            verticalLayout.addWidget(categoryName_lineEdit)

            buttonBox = QtWidgets.QDialogButtonBox(addCategory_Dialog)
            buttonBox.setOrientation(QtCore.Qt.Horizontal)
            buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
            verticalLayout.addWidget(buttonBox)
            addCategory_Dialog.show()

            buttonBox.setMaximumSize(QtCore.QSize(16777215, 30))
            buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setMinimumSize(QtCore.QSize(100, 30))
            buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).setMinimumSize(QtCore.QSize(100, 30))

            def addCategory():
                newCategory = unicode(categoryName_lineEdit.text()).decode("utf-8")
                categories = self.allSettingsDict.get(settingKey)
                for x in categories:
                    if newCategory.lower() == x.lower():
                        self.infoPop(textTitle="Cannot Add Category",
                                     textHeader="%s category already exist" % newCategory)
                        return False

                categories.append(newCategory)
                listWidget.clear()
                listWidget.addItems(categories)
                addCategory_Dialog.accept()
                self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())


            buttonBox.accepted.connect(addCategory)
            buttonBox.rejected.connect(addCategory_Dialog.reject)

        for cat in sorted(categorySwList):
            tabWidget = QtWidgets.QWidget()
            horizontalLayout = QtWidgets.QHBoxLayout(tabWidget)
            categories_listWidget = QtWidgets.QListWidget()
            horizontalLayout.addWidget(categories_listWidget)

            verticalLayout = QtWidgets.QVBoxLayout()
            verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)

            add_pushButton = QtWidgets.QPushButton()
            add_pushButton.setText(("Add..."))
            verticalLayout.addWidget(add_pushButton)

            remove_pushButton = QtWidgets.QPushButton()
            remove_pushButton.setText(("Remove"))
            verticalLayout.addWidget(remove_pushButton)

            spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            verticalLayout.addItem(spacerItem)

            horizontalLayout.addLayout(verticalLayout)

            swTabs.addTab(tabWidget, cat.replace("categories_", ""))

            categories_listWidget.addItems(self.allSettingsDict[cat]["newSettings"])
            add_pushButton.clicked.connect(lambda ignore, settingKey=cat, listWidget=categories_listWidget: onAdd(settingKey, listWidget))
            # add_pushButton.clicked.connect(lambda: onAdd(cat, categories_listWidget))
            remove_pushButton.clicked.connect(lambda ignore, settingKey=cat, listWidget=categories_listWidget: onRemove(settingKey, listWidget))
            # remove_pushButton.clicked.connect(lambda: onRemove(cat, categories_listWidget))


        h1_s1_layout.addWidget(swTabs)
        categories_Layout.addLayout(h1_s1_layout)


        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        categories_Layout.addItem(spacerItem)
        self.contentsMaster_layout.addWidget(self.categories_vis)

    def _importExportContent(self):
        # convertDict = {"true": True,
        #                "True": True,
        #                "false": False,
        #                "False": False,
        #                "0": False,
        #                "1": True}
        # manager = self._getManager()
        # sw = manager.swName.lower()
        sw = BoilerDict["Environment"].lower()
        exportSettings = self.allSettingsDict.get("exportSettings")
        importSettings = self.allSettingsDict.get("importSettings")

        def updateImportDictionary(sw, key, value):
            importSettings[sw][key]=value
            self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())

        def updateExportDictionary(sw, key, value):
            exportSettings[sw][key] = value
            self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())
            pass

        importExport_Layout = QtWidgets.QVBoxLayout(self.importExportOptions_vis)
        importExport_Layout.setSpacing(0)

        h1_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_label = QtWidgets.QLabel()
        h1_label.setText("Import/Export Geometry Settings")
        h1_label.setFont(self.headerAFont)
        h1_horizontalLayout.addWidget(h1_label)
        importExport_Layout.addLayout(h1_horizontalLayout)

        h1_s1_layout = QtWidgets.QVBoxLayout()
        h1_s1_layout.setContentsMargins(-1, 15, -1, -1)

        softwaresTabWidget = QtWidgets.QTabWidget()
        softwaresTabWidget.setMaximumSize(QtCore.QSize(16777215, 167777))
        softwaresTabWidget.setTabPosition(QtWidgets.QTabWidget.North)
        softwaresTabWidget.setElideMode(QtCore.Qt.ElideNone)
        softwaresTabWidget.setUsesScrollButtons(False)

        ## TEMP
        sw="standalone"

        if sw == "maya" or sw == "standalone":
            mayaTab = QtWidgets.QWidget()
            maya_verticalLayout = QtWidgets.QVBoxLayout(mayaTab)
            maya_verticalLayout.setSpacing(0)

            softwaresTabWidget.addTab(mayaTab, "Maya")

            formatsTabWidget = QtWidgets.QTabWidget(mayaTab)
            objTab = QtWidgets.QWidget(mayaTab)
            fbxTab = QtWidgets.QWidget(mayaTab)
            alembicTab = QtWidgets.QWidget(mayaTab)
            formatsTabWidget.addTab(objTab, "Obj")
            formatsTabWidget.addTab(fbxTab, "FBX")
            formatsTabWidget.addTab(alembicTab, "Alembic")
            maya_verticalLayout.addWidget(formatsTabWidget)

            ## MAYA OBJ
            ## --------
            def _maya_obj():
                obj_horizontal_layout = QtWidgets.QHBoxLayout(objTab)
                obj_import_layout = QtWidgets.QVBoxLayout()
                obj_seperator = QtWidgets.QLabel()
                obj_seperator.setProperty("seperator", True)
                obj_seperator.setMaximumWidth(2)
                obj_export_layout = QtWidgets.QVBoxLayout()

                obj_horizontal_layout.addLayout(obj_import_layout)
                obj_horizontal_layout.addWidget(obj_seperator)
                obj_horizontal_layout.addLayout(obj_export_layout)

                ## MAYA OBJ IMPORT WIDGETS
                obj_import_label = QtWidgets.QLabel()
                obj_import_label.setText("Obj Import Settings")
                obj_import_label.setFont(self.headerBFont)
                obj_import_layout.addWidget(obj_import_label)

                obj_import_formlayout = QtWidgets.QFormLayout()
                obj_import_formlayout.setSpacing(6)
                obj_import_formlayout.setHorizontalSpacing(15)
                obj_import_formlayout.setVerticalSpacing(10)
                obj_import_formlayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
                obj_import_layout.addLayout(obj_import_formlayout)
                
                mayaObjImpCreateDict = [
                    {"NiceName": "Legacy Vertex Ordering", "DictName": "LegacyVertexOrdering", "Type": "chb", "asFlag": "lo="},
                    {"NiceName": "Multiple Objects", "DictName": "MultipleObjects", "Type": "chb", "asFlag": "mo="},
                ]
                self._createFormWidgets(mayaObjImpCreateDict, importSettings, "objImportMaya",
                                        obj_import_formlayout, updateImportDictionary)


                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                obj_import_layout.addItem(spacerItem)

                ## MAYA OBJ EXPORT WIDGETS
                obj_export_label = QtWidgets.QLabel()
                obj_export_label.setText("Obj Export Settings")
                obj_export_label.setFont(self.headerBFont)
                obj_export_layout.addWidget(obj_export_label)

                obj_export_formlayout = QtWidgets.QFormLayout()
                obj_export_formlayout.setSpacing(6)
                obj_export_formlayout.setHorizontalSpacing(15)
                obj_export_formlayout.setVerticalSpacing(10)
                obj_export_formlayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
                obj_export_layout.addLayout(obj_export_formlayout)

                mayaObjExpCreateDict = [
                    {"NiceName": "Normals", "DictName": "normals", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Materials", "DictName": "materials", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Point Groups", "DictName": "ptgroups", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Groups", "DictName": "groups", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Smoothing", "DictName": "smoothing", "Type": "chb", "asFlag": ""},
                ]
                self._createFormWidgets(mayaObjExpCreateDict, exportSettings, "objExportMaya",
                                        obj_export_formlayout, updateExportDictionary)


                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                obj_export_layout.addItem(spacerItem)

            ## MAYA FBX
            ## --------
            def _maya_fbx():
                fbx_horizontal_layout = QtWidgets.QHBoxLayout(fbxTab)
                fbx_import_layout = QtWidgets.QVBoxLayout()
                fbx_seperator = QtWidgets.QLabel()
                fbx_seperator.setProperty("seperator", True)
                fbx_seperator.setMaximumWidth(2)
                fbx_export_layout = QtWidgets.QVBoxLayout()

                fbx_horizontal_layout.addLayout(fbx_import_layout)
                fbx_horizontal_layout.addWidget(fbx_seperator)
                fbx_horizontal_layout.addLayout(fbx_export_layout)

                ## MAYA FBX IMPORT WIDGETS
                fbx_import_label = QtWidgets.QLabel()
                fbx_import_label.setText("Fbx Import Settings")
                fbx_import_label.setFont(self.headerBFont)
                fbx_import_layout.addWidget(fbx_import_label)

                fbx_import_formlayout = QtWidgets.QFormLayout()
                fbx_import_formlayout.setSpacing(6)
                fbx_import_formlayout.setHorizontalSpacing(15)
                fbx_import_formlayout.setVerticalSpacing(10)
                fbx_import_formlayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
                fbx_import_layout.addLayout(fbx_import_formlayout)

                mayaFbxImpCreateDict = [
                    {"NiceName": "Up Axis: ", "DictName": "FBXImportUpAxis", "Type": "combo", "items": ["y", "z"], "asFlag": ""},
                    {"NiceName": "Import Mode: ", "DictName": "FBXImportMode", "Type": "combo", "items": ["add", "merge", "exmerge"], "asFlag": "-v "},
                    {"NiceName": "Scale Factor: ", "DictName": "FBXImportScaleFactor", "Type": "spbDouble", "asFlag": ""},
                    {"NiceName": "Treat Quaternions: ", "DictName": "FBXImportQuaternion", "Type": "combo", "items":["quaternion", "euler", "resample"], "asFlag": "-v "},
                    {"NiceName": "Resampling Rate Source: ", "DictName": "FBXImportResamplingRateSource", "Type": "combo", "items":["Scene", "File"], "asFlag": "-v "},
                    {"NiceName": "Merge Back Null Pivots: ", "DictName": "FBXImportMergeBackNullPivots", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Set Locked Attribute: ", "DictName": "FBXImportSetLockedAttribute", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Unlock Normals: ", "DictName": "FBXImportUnlockNormals", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Protect Driven Keys: ", "DictName": "FBXImportProtectDrivenKeys", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Shapes: ", "DictName": "FBXImportShapes", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Cameras: ", "DictName": "FBXImportCameras", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Set Maya Frame Rate: ", "DictName": "FBXImportSetMayaFrameRate", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Generate Log: ", "DictName": "FBXImportGenerateLog", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Constraints: ", "DictName": "FBXImportConstraints", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Lights: ", "DictName": "FBXImportLights", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Convert Nulls to Joints: ", "DictName": "FBXImportConvertDeformingNullsToJoint", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Fill Timeline: ", "DictName": "FBXImportFillTimeline", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Merge Animation Layers: ", "DictName": "FBXImportMergeAnimationLayers", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Hard Edges: ", "DictName": "FBXImportHardEdges", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Axis Conversion Enable: ", "DictName": "FBXImportAxisConversionEnable", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Cache File: ", "DictName": "FBXImportCacheFile", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Skins: ", "DictName": "FBXImportSkins", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Convert Unit String: ", "DictName": "FBXImportConvertUnitString", "Type": "chb", "asFlag": "-v "},
                ]
                self._createFormWidgets(mayaFbxImpCreateDict, importSettings, "fbxImportMaya", fbx_import_formlayout, updateImportDictionary)


                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                fbx_import_layout.addItem(spacerItem)

                ## MAYA FBX EXPORT WIDGETS
                fbx_export_label = QtWidgets.QLabel()
                fbx_export_label.setText("Fbx Export Settings")
                fbx_export_label.setFont(self.headerBFont)
                fbx_export_layout.addWidget(fbx_export_label)

                fbx_export_formlayout = QtWidgets.QFormLayout()
                fbx_export_formlayout.setSpacing(6)
                fbx_export_formlayout.setHorizontalSpacing(15)
                fbx_export_formlayout.setVerticalSpacing(10)
                fbx_export_formlayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
                fbx_export_layout.addLayout(fbx_export_formlayout)

                mayaFbxExpCreateDict = [
                    {"NiceName": "Up Axis: ", "DictName": "FBXExportUpAxis", "Type": "combo", "items": ["y", "z"], "asFlag": ""},
                    {"NiceName": "Axis Conversion Method: ", "DictName": "FBXExportAxisConversionMethod", "Type": "combo", "items": ["none", "convertAnimation", "addFbxRoot"], "asFlag": ""},
                    {"NiceName": "Bake Step: ", "DictName": "FBXExportBakeComplexStep", "Type": "spbInt", "asFlag": "-v "},
                    {"NiceName": "Convert Units: ", "DictName": "FBXExportConvertUnitString", "Type": "combo", "items": ["mm", "dm", "cm", "m", "km", "In", "ft", "yd", "mi"], "asFlag": ""},
                    {"NiceName": "Treat Quaternion: ", "DictName": "FBXExportQuaternion", "Type": "combo", "items": ["quaternion", "euler", "resample"], "asFlag": "-v "},
                    {"NiceName": "FBX Version: ", "DictName": "FBXExportFileVersion", "Type": "str", "asFlag": "-v "},
                    {"NiceName": "Scale Factor: ", "DictName": "FBXExportScaleFactor", "Type": "spbDouble", "asFlag": ""},
                    {"NiceName": "Apply Constant Key Reducer: ", "DictName": "FBXExportApplyConstantKeyReducer", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Shapes: ", "DictName": "FBXExportShapes", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Use Scene Name: ", "DictName": "FBXExportUseSceneName", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Skeleton Definitions: ", "DictName": "FBXExportSkeletonDefinitions", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Instances: ", "DictName": "FBXExportInstances", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Cameras: ", "DictName": "FBXExportCameras", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "FBXExportTangents: ", "DictName": "FBXExportTangents", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Ascii: ", "DictName": "FBXExportInAscii", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Lights: ", "DictName": "FBXExportLights", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Referenced Assets: ", "DictName": "FBXExportReferencedAssetsContent", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Constraints: ", "DictName": "FBXExportConstraints", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Smooth Mesh: ", "DictName": "FBXExportSmoothMesh", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Hard Edges: ", "DictName": "FBXExportHardEdges", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Input Connections: ", "DictName": "FBXExportInputConnections", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Embed Textures: ", "DictName": "FBXExportEmbeddedTextures", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Bake Animation: ", "DictName": "FBXExportBakeComplexAnimation", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Cache File: ", "DictName": "FBXExportCacheFile", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Smoothing Groups: ", "DictName": "FBXExportSmoothingGroups", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Resample Animation: ", "DictName": "FBXExportBakeResampleAnimation", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Triangulate: ", "DictName": "FBXExportTriangulate", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Skins: ", "DictName": "FBXExportSkins", "Type": "chb", "asFlag": "-v "},
                ]
                self._createFormWidgets(mayaFbxExpCreateDict, exportSettings, "fbxExportMaya", fbx_export_formlayout, updateExportDictionary)

                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                fbx_export_layout.addItem(spacerItem)

            ## MAYA ALEMBIC
            ## ------------
            def _maya_alembic():
                alembic_horizontal_layout = QtWidgets.QHBoxLayout(alembicTab)
                alembic_import_layout = QtWidgets.QVBoxLayout()
                alembic_seperator = QtWidgets.QLabel()
                alembic_seperator.setProperty("seperator", True)
                alembic_seperator.setMaximumWidth(2)
                alembic_export_layout = QtWidgets.QVBoxLayout()

                alembic_horizontal_layout.addLayout(alembic_import_layout)
                alembic_horizontal_layout.addWidget(alembic_seperator)
                alembic_horizontal_layout.addLayout(alembic_export_layout)

                ## MAYA ALEMBIC IMPORT WIDGETS
                alembic_import_label = QtWidgets.QLabel()
                alembic_import_label.setText("Alembic Import Settings")
                alembic_import_label.setFont(self.headerBFont)
                alembic_import_layout.addWidget(alembic_import_label)

                alembic_import_formlayout = QtWidgets.QFormLayout()
                alembic_import_formlayout.setSpacing(6)
                alembic_import_formlayout.setHorizontalSpacing(15)
                alembic_import_formlayout.setVerticalSpacing(10)
                alembic_import_formlayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
                alembic_import_layout.addLayout(alembic_import_formlayout)

                mayaAlembicImpCreateDict = [
                    {"NiceName": "Fit Time Range: ", "DictName": "fitTimeRange", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Set To Start Frame: ", "DictName": "setToStartFrame", "Type": "chb", "asFlag": ""},
                ]
                self._createFormWidgets(mayaAlembicImpCreateDict, importSettings, "alembicImportMaya", alembic_import_formlayout, updateImportDictionary)

                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                alembic_import_layout.addItem(spacerItem)

                ## MAYA ALEMBIC EXPORT WIDGETS
                alembic_export_label = QtWidgets.QLabel()
                alembic_export_label.setText("Alembic Export Settings")
                alembic_export_label.setFont(self.headerBFont)
                alembic_export_layout.addWidget(alembic_export_label)

                alembic_export_formlayout = QtWidgets.QFormLayout()
                alembic_export_formlayout.setSpacing(6)
                alembic_export_formlayout.setHorizontalSpacing(15)
                alembic_export_formlayout.setVerticalSpacing(10)
                alembic_export_formlayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
                alembic_export_layout.addLayout(alembic_export_formlayout)

                mayaAlembicExpCreateDict = [
                    {"NiceName": "Step: ", "DictName": "step", "Type": "spbDouble", "asFlag": ""},
                    {"NiceName": "Data Format: ", "DictName": "dataFormat", "Type": "combo", "items":["Ogawa", "HDF5"], "asFlag": ""},
                    {"NiceName": "Face Sets: ", "DictName": "writeFaceSets", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Uv Sets: ", "DictName": "writeUVSets", "Type": "chb", "asFlag": ""},
                    {"NiceName": "No Normals: ", "DictName": "noNormals", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Auto Subdivide: ", "DictName": "autoSubd", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Strip Namespaces: ", "DictName": "stripNamespaces", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Whole Frame Geo: ", "DictName": "wholeFrameGeo", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Renderable Only: ", "DictName": "renderableOnly", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Worldspace: ", "DictName": "worldSpace", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Visibility: ", "DictName": "writeVisibility", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Euler Filter: ", "DictName": "eulerFilter", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Color Sets: ", "DictName": "writeColorSets", "Type": "chb", "asFlag": ""},
                    {"NiceName": "UV: ", "DictName": "uvWrite", "Type": "chb", "asFlag": ""},
                ]
                self._createFormWidgets(mayaAlembicExpCreateDict, exportSettings, "alembicExportMaya", alembic_export_formlayout, updateExportDictionary)

                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                alembic_export_layout.addItem(spacerItem)

            _maya_obj()
            _maya_fbx()
            _maya_alembic()

        if sw == "3dsmax" or sw == "standalone":
            maxTab = QtWidgets.QWidget()
            max_verticalLayout = QtWidgets.QVBoxLayout(maxTab)
            max_verticalLayout.setSpacing(0)

            softwaresTabWidget.addTab(maxTab, "3dsMax")

            formatsTabWidget = QtWidgets.QTabWidget(maxTab)
            objTab = QtWidgets.QWidget(maxTab)
            fbxTab = QtWidgets.QWidget(maxTab)
            alembicTab = QtWidgets.QWidget(maxTab)
            formatsTabWidget.addTab(objTab, "Obj")
            formatsTabWidget.addTab(fbxTab, "FBX")
            formatsTabWidget.addTab(alembicTab, "Alembic")
            max_verticalLayout.addWidget(formatsTabWidget)

            ## MAX OBJ
            ## --------
            def _max_obj():

                obj_horizontal_layout = QtWidgets.QHBoxLayout(objTab)
                obj_import_layout = QtWidgets.QVBoxLayout()
                obj_seperator = QtWidgets.QLabel()
                obj_seperator.setProperty("seperator", True)
                obj_seperator.setMaximumWidth(2)
                obj_export_layout = QtWidgets.QVBoxLayout()

                obj_horizontal_layout.addLayout(obj_import_layout)
                obj_horizontal_layout.addWidget(obj_seperator)
                obj_horizontal_layout.addLayout(obj_export_layout)

                ## MAX OBJ IMPORT WIDGETS
                obj_import_label = QtWidgets.QLabel()
                obj_import_label.setText("Obj Import Settings")
                obj_import_label.setFont(self.headerBFont)
                obj_import_layout.addWidget(obj_import_label)

                obj_import_formlayout = QtWidgets.QFormLayout()
                obj_import_formlayout.setSpacing(6)
                obj_import_formlayout.setHorizontalSpacing(15)
                obj_import_formlayout.setVerticalSpacing(10)
                obj_import_formlayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
                obj_import_layout.addLayout(obj_import_formlayout)

                # CREATE WIDGETS
                maxObjImpCreateDict = [
                    {"NiceName": "General", "DictName": "General", "Type": "inf", "asFlag": ""},
                    {"NiceName": "Use Logging", "DictName": "UseLogging", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Reset Scene", "DictName": "ResetScene", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Objects", "DictName": "Objects", "Type": "inf", "asFlag": ""},
                    {"NiceName": "Import as single mesh", "DictName": "SingleMesh", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Import as Editable Poly", "DictName": "AsEditablePoly", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Retriangulate", "DictName": "Retriangulate", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Flip ZY-axis", "DictName": "FlipZyAxis", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Center Pivots", "DictName": "CenterPivots", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Shapes/Lines", "DictName": "Shapes", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Texture coordinates", "DictName": "TextureCoords", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Smoothing groups", "DictName": "SmoothingGroups", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Normals Type: ", "DictName": "NormalsType", "Type": "combo", "items": ["Import from file", "From SM group", "Auto Smooth", "Faceted"], "asFlag": ""},
                    {"NiceName": "Smooth Angle: ", "DictName": "SmoothAngle", "Type": "spbDouble", "asFlag": ""},
                    {"NiceName": "Flip Normals: ", "DictName": "FlipNormals", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Units/Scale", "DictName": "Units/Scale", "Type": "inf", "asFlag": ""},
                    {"NiceName": "Convert", "DictName": "Convert", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Convert From: ", "DictName": "ConvertFrom", "Type": "combo", "items": ["Inches", "Feet", "Miles", "Millimeters", "Centimeters", "Meters", "Kilometers"], "asFlag": ""},
                    {"NiceName": "Object Scale: ", "DictName": "ObjScale", "Type": "spbDouble", "asFlag": ""},
                    {"NiceName": "Material", "DictName": "Material", "Type": "inf", "asFlag": ""},
                    {"NiceName": "Unique Wire Color", "DictName": "UniqueWireColor", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Import Materials", "DictName": "ImportMaterials", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Default Bump: ", "DictName": "DefaultBump", "Type": "spbDouble", "asFlag": ""},
                    {"NiceName": "Force Black Ambient", "DictName": "ForceBlackAmbient", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Import Into Mat-Editor", "DictName": "ImportIntoMatEditor", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Show maps in viewport", "DictName": "ShowMapsInViewport", "Type": "chb", "asFlag": ""}
                ]
                self._createFormWidgets(maxObjImpCreateDict, importSettings, "objImportMax", obj_import_formlayout, updateImportDictionary)


                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                obj_import_layout.addItem(spacerItem)

                ## MAX OBJ EXPORT WIDGETS

                obj_export_label = QtWidgets.QLabel()
                obj_export_label.setText("Obj Export Settings")
                obj_export_label.setFont(self.headerBFont)
                obj_export_layout.addWidget(obj_export_label)

                obj_export_formlayout = QtWidgets.QFormLayout()
                obj_export_formlayout.setSpacing(6)
                obj_export_formlayout.setHorizontalSpacing(15)
                obj_export_formlayout.setVerticalSpacing(10)
                obj_export_formlayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
                obj_export_layout.addLayout(obj_export_formlayout)

                maxObjExpCreateDict = [
                    {"NiceName": "Geometry", "DictName": "Geometry", "Type": "inf", "asFlag": ""},
                    {"NiceName": "Flip ZY-axis", "DictName": "FlipZyAxis", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Shapes/Lines", "DictName": "Shapes", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Hidden Objects", "DictName": "ExportHiddenObjects", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Faces: ", "DictName": "FaceType", "Type": "combo", "items": ["Triangles", "Quads", "Polygons"], "asFlag": ""},
                    {"NiceName": "Texture Coordinates", "DictName": "TextureCoords", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Normals", "DictName": "Normals", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Smoothing Groups", "DictName": "SmoothingGroups", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Object Scale: ", "DictName": "ObjScale", "Type": "spbDouble", "asFlag": ""},
                    {"NiceName": "Output", "DictName": "Output", "Type": "inf", "asFlag": ""},
                    {"NiceName": "Relative Numbers", "DictName": "RelativeIndex", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Target: ", "DictName": "Target", "Type": "combo", "items": ["PC/Win", "Unix", "Mac"],"asFlag": ""},
                    {"NiceName": "Precision: ", "DictName": "Precision", "Type": "spbDouble", "asFlag": ""},
                    {"NiceName": "Optimize", "DictName": "Optimize", "Type": "inf", "asFlag": ""},
                    {"NiceName": "Optimize Vertex", "DictName": "optVertex", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Optimize Normals", "DictName": "optNormals", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Optimize Texture Coordinates", "DictName": "optTextureCoords", "Type": "chb", "asFlag": ""},
                ]
                self._createFormWidgets(maxObjExpCreateDict, exportSettings, "objExportMax", obj_export_formlayout, updateExportDictionary)


                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                obj_export_layout.addItem(spacerItem)

            ## MAX FBX
            ## --------
            def _max_fbx():
                fbx_horizontal_layout = QtWidgets.QHBoxLayout(fbxTab)
                fbx_import_layout = QtWidgets.QVBoxLayout()
                fbx_seperator = QtWidgets.QLabel()
                fbx_seperator.setProperty("seperator", True)
                fbx_seperator.setMaximumWidth(2)
                fbx_export_layout = QtWidgets.QVBoxLayout()

                fbx_horizontal_layout.addLayout(fbx_import_layout)
                fbx_horizontal_layout.addWidget(fbx_seperator)
                fbx_horizontal_layout.addLayout(fbx_export_layout)

                ## MAX FBX IMPORT WIDGETS
                fbx_import_label = QtWidgets.QLabel()
                fbx_import_label.setText("Fbx Import Settings")
                fbx_import_label.setFont(self.headerBFont)
                fbx_import_layout.addWidget(fbx_import_label)

                fbx_import_formlayout = QtWidgets.QFormLayout()
                fbx_import_formlayout.setSpacing(6)
                fbx_import_formlayout.setHorizontalSpacing(15)
                fbx_import_formlayout.setVerticalSpacing(10)
                fbx_import_formlayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
                fbx_import_layout.addLayout(fbx_import_formlayout)

                maxFbxImpCreateDict = [
                    {"NiceName": "Mode", "DictName": "Mode", "Type": "combo", "items": ["create", "exmerge", "merge"] ,"asFlag": ""},
                    {"NiceName": "Skin", "DictName": "Skin", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Convert Unit", "DictName": "ConvertUnit", "Type": "combo", "items": ["mm", "cm", "dm", "m", "km", "in", "ft", "yd"], "asFlag": ""},
                    {"NiceName": "Markers", "DictName": "Markers", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Bake Animation Layers", "DictName": "BakeAnimationLayers", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Filter Key Reducer", "DictName": "FilterKeyReducer", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Fill Timeline", "DictName": "FillTimeline", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Cameras", "DictName": "Cameras", "Type": "chb", "asFlag": ""},
                    {"NiceName": "GenerateLog", "DictName": "GenerateLog", "Type": "chb", "asFlag": ""},
                    {"NiceName": "FilterKeySync", "DictName": "FilterKeySync", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Resampling: ", "DictName": "Resampling", "Type": "spbInt", "asFlag": ""},
                    {"NiceName": "Lights: ", "DictName": "Lights", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Shape: ", "DictName": "Shape", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Axis Conversion: ", "DictName": "AxisConversion", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Import Bone As Dummy: ", "DictName": "ImportBoneAsDummy", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Scale Conversion: ", "DictName": "ScaleConversion", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Smoothing Groups: ", "DictName": "SmoothingGroups", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Point Cache: ", "DictName": "PointCache", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Scale Factor: ", "DictName": "ScaleFactor", "Type": "spbDouble", "asFlag": ""},
                    {"NiceName": "Keep Frame Rate: ", "DictName": "KeepFrameRate", "Type": "chb", "asFlag": ""},
                ]
                self._createFormWidgets(maxFbxImpCreateDict, importSettings, "fbxImportMax", fbx_import_formlayout, updateImportDictionary)

                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                fbx_import_layout.addItem(spacerItem)

                ## MAX FBX EXPORT WIDGETS
                fbx_export_label = QtWidgets.QLabel()
                fbx_export_label.setText("Fbx Export Settings")
                fbx_export_label.setFont(self.headerBFont)
                fbx_export_layout.addWidget(fbx_export_label)

                fbx_export_formlayout = QtWidgets.QFormLayout()
                fbx_export_formlayout.setSpacing(6)
                fbx_export_formlayout.setHorizontalSpacing(15)
                fbx_export_formlayout.setVerticalSpacing(10)
                fbx_export_formlayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
                fbx_export_layout.addLayout(fbx_export_formlayout)

                maxFbxExpCreateDict = [
                    {"NiceName": "CAT2HIK", "DictName": "CAT2HIK", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Bake Animation", "DictName": "BakeAnimation", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Tangent Space Export", "DictName": "TangentSpaceExport", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Lights", "DictName": "Lights", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Use Scene Name", "DictName": "UseSceneName", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Smoothing Groups", "DictName": "SmoothingGroups", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Axis Conversion Method", "DictName": "AxisConversionMethod", "Type": "combo", "items":["None", "Animation", "Fbx_Root"], "asFlag": ""},
                    {"NiceName": "Bake Frame Step", "DictName": "BakeFrameStep", "Type": "spbInt", "asFlag": ""},
                    {"NiceName": "FBX Version", "DictName": "FileVersion", "Type": "str", "asFlag": ""},
                    {"NiceName": "Remove single keys", "DictName": "Removesinglekeys", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Up Axis", "DictName": "UpAxis", "Type": "combo", "items": ["Y", "Z"], "asFlag": ""},
                    {"NiceName": "Generate Log", "DictName": "GenerateLog", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Preserve instances", "DictName": "Preserveinstances", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Selection Set Export", "DictName": "SelectionSetExport", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Convert to Tiff", "DictName": "Convert2Tiff", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Show Warnings", "DictName": "ShowWarnings", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Collada Triangulate", "DictName": "ColladaTriangulate", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Filter Key Reducer", "DictName": "FilterKeyReducer", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Triangulate", "DictName": "Triangulate", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Normals Per Poly", "DictName": "NormalsPerPoly", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Smooth Mesh Export", "DictName": "SmoothMeshExport", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Collada Single Matrix", "DictName": "ColladaSingleMatrix", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Convert Unit", "DictName": "ConvertUnit", "Type": "combo", "items":["mm", "cm", "dm", "m", "km", "in", "ft", "mi", "yd"], "asFlag": ""},
                    {"NiceName": "ASCII", "DictName": "ASCII", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Geometry As Bone", "DictName": "GeomAsBone", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Shape", "DictName": "Shape", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Embed Textures", "DictName": "EmbedTextures", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Point Cache", "DictName": "PointCache", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Skin", "DictName": "Skin", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Scale Factor", "DictName": "ScaleFactor", "Type": "spbDouble", "asFlag": ""},
                    {"NiceName": "Resample Animation Factor", "DictName": "BakeResampleAnimation", "Type": "chb", "asFlag": ""},
                ]

                self._createFormWidgets(maxFbxExpCreateDict, exportSettings, "fbxExportMax", fbx_export_formlayout, updateExportDictionary)


                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                fbx_export_layout.addItem(spacerItem)

            ## MAX ALEMBIC
            ## ------------
            def _max_alembic():
                alembic_horizontal_layout = QtWidgets.QHBoxLayout(alembicTab)
                alembic_import_layout = QtWidgets.QVBoxLayout()
                alembic_seperator = QtWidgets.QLabel()
                alembic_seperator.setProperty("seperator", True)
                alembic_seperator.setMaximumWidth(2)
                alembic_export_layout = QtWidgets.QVBoxLayout()

                alembic_horizontal_layout.addLayout(alembic_import_layout)
                alembic_horizontal_layout.addWidget(alembic_seperator)
                alembic_horizontal_layout.addLayout(alembic_export_layout)


                ## MAX ALEMBIC IMPORT WIDGETS
                alembic_import_label = QtWidgets.QLabel()
                alembic_import_label.setText("Alembic Import Settings")
                alembic_import_label.setFont(self.headerBFont)
                alembic_import_layout.addWidget(alembic_import_label)

                alembic_import_formlayout = QtWidgets.QFormLayout()
                alembic_import_formlayout.setSpacing(6)
                alembic_import_formlayout.setHorizontalSpacing(15)
                alembic_import_formlayout.setVerticalSpacing(10)
                alembic_import_formlayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
                alembic_import_layout.addLayout(alembic_import_formlayout)

                maxAlembicImpCreateDict = [
                    {"NiceName": "Fit Time Range", "DictName": "FitTimeRange", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Object ID", "DictName": "ObjectID", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Vertex Colors", "DictName": "VertexColors", "Type": "chb", "asFlag": ""},
                    {"NiceName": "UV's", "DictName": "UVs", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Coordinate System", "DictName": "CoordinateSystem", "Type": "combo", "items": ["YUp", "ZUp"], "asFlag": ""},
                    {"NiceName": "Visibility", "DictName": "Visibility", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Custom Attributes", "DictName": "CustomAttributes", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Set Start Time", "DictName": "SetStartTime", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Material ID's", "DictName": "MaterialIDs", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Normals", "DictName": "Normals", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Import To Root", "DictName": "ImportToRoot", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Velocity", "DictName": "Velocity", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Hidden", "DictName": "Hidden", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Layer Name", "DictName": "LayerName", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Shape Suffix", "DictName": "ShapeSuffix", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Material Name", "DictName": "MaterialName", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Samples Per Frame", "DictName": "SamplesPerFrame", "Type": "spbInt", "asFlag": ""},
                    {"NiceName": "Extra Channels", "DictName": "ExtraChannels", "Type": "spbInt", "asFlag": ""},
                ]
                self._createFormWidgets(maxAlembicImpCreateDict, importSettings, "alembicImportMax", alembic_import_formlayout, updateImportDictionary)


                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                alembic_import_layout.addItem(spacerItem)

                ## MAX ALEMBIC EXPORT WIDGETS
                alembic_export_label = QtWidgets.QLabel()
                alembic_export_label.setText("Alembic Export Settings")
                alembic_export_label.setFont(self.headerBFont)
                alembic_export_layout.addWidget(alembic_export_label)

                alembic_export_formlayout = QtWidgets.QFormLayout()
                alembic_export_formlayout.setSpacing(6)
                alembic_export_formlayout.setHorizontalSpacing(15)
                alembic_export_formlayout.setVerticalSpacing(10)
                alembic_export_formlayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
                alembic_export_layout.addLayout(alembic_export_formlayout)

                maxAlembicExpCreateDict = [
                    {"NiceName": "Particle As Mesh", "DictName": "ParticleAsMesh", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Object ID", "DictName": "ObjectID", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Vertex Colors", "DictName": "VertexColors", "Type": "chb", "asFlag": ""},
                    {"NiceName": "UV's", "DictName": "UVs", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Coordinate System", "DictName": "CoordinateSystem", "Type": "combo", "items": ["YUp", "ZUp"], "asFlag": ""},
                    {"NiceName": "Visibility", "DictName": "Visibility", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Archive Type", "DictName": "ArchiveType", "Type": "combo", "items": ["Ogawa", "HDF5"], "asFlag": ""},
                    {"NiceName": "Custom Attributes", "DictName": "CustomAttributes", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Shape Suffix", "DictName": "ShapeSuffix", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Material ID's", "DictName": "MaterialIDs", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Normals", "DictName": "Normals", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Velocity", "DictName": "Velocity", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Hidden", "DictName": "Hidden", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Layer Name", "DictName": "LayerName", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Material Name", "DictName": "MaterialName", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Material Name", "DictName": "MaterialName", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Samples Per Frame", "DictName": "SamplesPerFrame", "Type": "spbInt", "asFlag": ""},
                    {"NiceName": "Extra Channels", "DictName": "ExtraChannels", "Type": "spbInt", "asFlag": ""},
                ]
                self._createFormWidgets(maxAlembicExpCreateDict, exportSettings, "alembicExportMax", alembic_export_formlayout, updateExportDictionary)




                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                alembic_export_layout.addItem(spacerItem)

            _max_obj()
            _max_fbx()
            _max_alembic()

        if sw == "houdini" or sw == "standalone":
            houdiniTab = QtWidgets.QWidget()
            houdini_verticalLayout = QtWidgets.QVBoxLayout(houdiniTab)
            houdini_verticalLayout.setSpacing(0)

            softwaresTabWidget.addTab(houdiniTab, "Houdini")

            formatsTabWidget = QtWidgets.QTabWidget(houdiniTab)
            # objTab = QtWidgets.QWidget(houdiniTab)
            fbxTab = QtWidgets.QWidget(houdiniTab)
            alembicTab = QtWidgets.QWidget(houdiniTab)
            # formatsTabWidget.addTab(objTab, "Obj")
            formatsTabWidget.addTab(fbxTab, "FBX")
            formatsTabWidget.addTab(alembicTab, "Alembic")
            houdini_verticalLayout.addWidget(formatsTabWidget)


            ## HOUDINI FBX
            ## --------
            def _houdini_fbx():
                fbx_horizontal_layout = QtWidgets.QHBoxLayout(fbxTab)
                fbx_import_layout = QtWidgets.QVBoxLayout()
                fbx_seperator = QtWidgets.QLabel()
                fbx_seperator.setProperty("seperator", True)
                fbx_seperator.setMaximumWidth(2)
                fbx_export_layout = QtWidgets.QVBoxLayout()

                fbx_horizontal_layout.addLayout(fbx_import_layout)
                fbx_horizontal_layout.addWidget(fbx_seperator)
                fbx_horizontal_layout.addLayout(fbx_export_layout)

                ## HOUDINI FBX IMPORT WIDGETS
                fbx_import_label = QtWidgets.QLabel()
                fbx_import_label.setText("Fbx Import Settings")
                fbx_import_label.setFont(self.headerBFont)
                fbx_import_layout.addWidget(fbx_import_label)

                fbx_import_formlayout = QtWidgets.QFormLayout()
                fbx_import_formlayout.setSpacing(6)
                fbx_import_formlayout.setHorizontalSpacing(15)
                fbx_import_formlayout.setVerticalSpacing(10)
                fbx_import_formlayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
                fbx_import_layout.addLayout(fbx_import_formlayout)

                houdiniFbxImpCreateDict = [
                    {"NiceName": "Import Lights", "DictName": "import_lights", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Resample Interval Lights", "DictName": "resample_interval", "Type": "spbDouble", "asFlag": ""},
                    {"NiceName": "Import Global Ambient Light", "DictName": "import_global_ambient_light", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Import Geometry", "DictName": "import_geometry", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Triangulate Patches", "DictName": "triangulate_patches", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Convert File Paths to Relative", "DictName": "convert_file_paths_to_relative", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Single Precision Vertex Caches", "DictName": "single_precision_vertex_caches", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Import Joints and Skin", "DictName": "import_joints_and_skin", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Resample Animation", "DictName": "resample_animation", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Override Framerate", "DictName": "override_framerate", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Import Animation", "DictName": "import_animation", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Import Cameras", "DictName": "import_cameras", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Segment Scale Already Baked-in", "DictName": "segment_scale_already_baked_in", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Convert Y Up", "DictName": "convert_into_y_up_coordinate_system", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Import Materials", "DictName": "import_materials", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Unlock Geometry", "DictName": "unlock_geometry", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Import into object subnet", "DictName": "import_into_object_subnet", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Triangulate Nurbs", "DictName": "triangulate_nurbs", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Import Nulls as subnets", "DictName": "import_nulls_as_subnets", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Blend deformers as blend sops", "DictName": "import_blend_deformers_as_blend_sops", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Hide attached Joints", "DictName": "hide_joints_attached_to_skin", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Unlock Deformations", "DictName": "unlock_deformations", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Convert joints to zyx rotation order", "DictName": "convert_joints_to_zyx_rotation_order", "Type": "chb", "asFlag": ""}
                ]
                self._createFormWidgets(houdiniFbxImpCreateDict, importSettings, "fbxImportHoudini", fbx_import_formlayout,
                                        updateImportDictionary)

                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                fbx_import_layout.addItem(spacerItem)

                ## HOUDINI FBX EXPORT WIDGETS
                fbx_export_label = QtWidgets.QLabel()
                fbx_export_label.setText("Fbx Export Settings")
                fbx_export_label.setFont(self.headerBFont)
                fbx_export_layout.addWidget(fbx_export_label)

                fbx_export_formlayout = QtWidgets.QFormLayout()
                fbx_export_formlayout.setSpacing(6)
                fbx_export_formlayout.setHorizontalSpacing(15)
                fbx_export_formlayout.setVerticalSpacing(10)
                fbx_export_formlayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
                fbx_export_layout.addLayout(fbx_export_formlayout)

                houdiniFbxExpCreateDict = [
                    {"NiceName": "FBX Version", "DictName": "sdkversion", "Type": "str", "asFlag": ""},
                    {"NiceName": "Export Invisible Objects as: ", "DictName": "invisobj", "Type": "combo", "items":["nullnodes", "fullnodes"], "asFlag": ""},
                    {"NiceName": "Detect Constant Point Cloud Dynamic Objects", "DictName": "detectconstpointobjs", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Export Deforms as Vertex Caches", "DictName": "deformsasvcs", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Vertex Cache Format", "DictName": "vcformat", "Type": "combo", "items": ["mayaformat", "maxformat"], "asFlag": ""},
                    {"NiceName": "Force Skin Deform", "DictName": "forceskindeform", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Convert Surfaces", "DictName": "convertsurfaces", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Force Blend Shape Export", "DictName": "forceblendshape", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Export End Effectors", "DictName": "exportendeffectors", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Conserve memory", "DictName": "conservemem", "Type": "chb", "asFlag": ""},
                ]

                self._createFormWidgets(houdiniFbxExpCreateDict, exportSettings, "fbxExportHoudini", fbx_export_formlayout,
                                        updateExportDictionary)

                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                fbx_export_layout.addItem(spacerItem)

            ## HOUDINI ALEMBIC
            ## ------------
            def _houdini_alembic():
                alembic_horizontal_layout = QtWidgets.QHBoxLayout(alembicTab)
                alembic_import_layout = QtWidgets.QVBoxLayout()
                alembic_seperator = QtWidgets.QLabel()
                alembic_seperator.setProperty("seperator", True)
                alembic_seperator.setMaximumWidth(2)
                alembic_export_layout = QtWidgets.QVBoxLayout()

                alembic_horizontal_layout.addLayout(alembic_import_layout)
                alembic_horizontal_layout.addWidget(alembic_seperator)
                alembic_horizontal_layout.addLayout(alembic_export_layout)

                ## HOUDINI ALEMBIC IMPORT WIDGETS
                alembic_import_label = QtWidgets.QLabel()
                alembic_import_label.setText("Alembic Import Settings")
                alembic_import_label.setFont(self.headerBFont)
                alembic_import_layout.addWidget(alembic_import_label)

                alembic_import_formlayout = QtWidgets.QFormLayout()
                alembic_import_formlayout.setSpacing(6)
                alembic_import_formlayout.setHorizontalSpacing(15)
                alembic_import_formlayout.setVerticalSpacing(10)
                alembic_import_formlayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
                alembic_import_layout.addLayout(alembic_import_formlayout)

                houdiniAlembicImpCreateDict = [
                    {"NiceName": "Display As", "DictName": "viewportlod", "Type": "combo", "items": ["full", "points", "box", "centroid", "hidden"], "asFlag": ""},
                    {"NiceName": "Flatten Visibility Evaluation", "DictName": "flattenVisibility", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Hierarchy with Channel References", "DictName": "channelRef", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Single Geometry", "DictName": "buildSingleGeoNode", "Type": "chb", "asFlag": ""},
                    {"NiceName": "User Properties", "DictName": "loadUserProps", "Type": "combo", "items":["none", "data", "both"], "asFlag": ""},
                    {"NiceName": "Load As", "DictName": "loadmode", "Type": "combo", "items":["alembic", "houdini", "hpoints", "hboxes"], "asFlag": ""},
                    {"NiceName": "Hierarchy using Subnetworks", "DictName": "buildSubnet", "Type": "chb", "asFlag": ""},
                ]
                self._createFormWidgets(houdiniAlembicImpCreateDict, importSettings, "alembicImportHoudini",
                                        alembic_import_formlayout, updateImportDictionary)

                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                alembic_import_layout.addItem(spacerItem)

                ## HOUDINI ALEMBIC EXPORT WIDGETS
                alembic_export_label = QtWidgets.QLabel()
                alembic_export_label.setText("Alembic Export Settings")
                alembic_export_label.setFont(self.headerBFont)
                alembic_export_layout.addWidget(alembic_export_label)

                alembic_export_formlayout = QtWidgets.QFormLayout()
                alembic_export_formlayout.setSpacing(6)
                alembic_export_formlayout.setHorizontalSpacing(15)
                alembic_export_formlayout.setVerticalSpacing(10)
                alembic_export_formlayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
                alembic_export_layout.addLayout(alembic_export_formlayout)

                houdiniAlembicExpCreateDict = [
                    {"NiceName": "Create Shape Nodes", "DictName": "shape_nodes", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Format", "DictName": "format", "Type": "combo", "items": ["default", "hdf5", "ogawa"], "asFlag": ""},
                    {"NiceName": "Face Sets", "DictName": "facesets", "Type": "combo", "items": ["no", "nonempty", "all"], "asFlag": ""},
                    {"NiceName": "Use Instancing", "DictName": "use_instancing", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Save Attributes Instancing", "DictName": "save_attributes", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Motion Blur", "DictName": "motionBlur", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Samples", "DictName": "samples", "Type": "spbInt", "asFlag": ""},
                    {"NiceName": "Shutter Open", "DictName": "shutter1", "Type": "spbInt", "asFlag": ""},
                    {"NiceName": "Shutter Close", "DictName": "shutter2", "Type": "spbInt", "asFlag": ""},
                ]
                self._createFormWidgets(houdiniAlembicExpCreateDict, exportSettings, "alembicExportHoudini",
                                        alembic_export_formlayout, updateExportDictionary)

                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                alembic_export_layout.addItem(spacerItem)

            # _houdini_obj()
            _houdini_fbx()
            _houdini_alembic()

        h1_s1_layout.addWidget(softwaresTabWidget)
        importExport_Layout.addLayout(h1_s1_layout)

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        importExport_Layout.addItem(spacerItem)
        self.contentsMaster_layout.addWidget(self.importExportOptions_vis)

    def _sharedSettingsContent(self):
        sharedSettings_Layout = QtWidgets.QVBoxLayout(self.sharedSettings_vis)
        sharedSettings_Layout.setSpacing(6)

        sharedSettings_label = QtWidgets.QLabel()
        sharedSettings_label.setText("Shared Settings")
        sharedSettings_label.setFont(self.headerAFont)
        sharedSettings_label.setIndent(10)
        sharedSettings_label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        sharedSettings_Layout.addWidget(sharedSettings_label)

        users_cmdButton = QtWidgets.QCommandLinkButton()
        users_cmdButton.setText("Users")
        sharedSettings_Layout.addWidget(users_cmdButton)

        passwords_cmdButton = QtWidgets.QCommandLinkButton()
        passwords_cmdButton.setText("Passwords")
        sharedSettings_Layout.addWidget(passwords_cmdButton)

        namingConventions_cmdButton = QtWidgets.QCommandLinkButton()
        namingConventions_cmdButton.setText("Naming Conventions")
        sharedSettings_Layout.addWidget(namingConventions_cmdButton)

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sharedSettings_Layout.addItem(spacerItem)
        self.contentsMaster_layout.addWidget(self.sharedSettings_vis)

        # SIGNALS
        users_cmdButton.clicked.connect(lambda: self.settingsMenu_treeWidget.setCurrentItem(self.users_item))
        passwords_cmdButton.clicked.connect(lambda: self.settingsMenu_treeWidget.setCurrentItem(self.passwords_item))
        namingConventions_cmdButton.clicked.connect(lambda: self.settingsMenu_treeWidget.setCurrentItem(self.namingConventions_item))

    def _usersContent(self):
        # manager = self._getManager()
        userList = self.allSettingsDict.get("users")

        users_Layout = QtWidgets.QVBoxLayout(self.users_vis)
        users_Layout.setSpacing(0)

        h1_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_label = QtWidgets.QLabel()
        h1_label.setText("Add/Remove Users")
        h1_label.setFont(self.headerAFont)
        h1_horizontalLayout.addWidget(h1_label)
        users_Layout.addLayout(h1_horizontalLayout)

        h1_s1_layout = QtWidgets.QVBoxLayout()
        h1_s1_layout.setContentsMargins(-1, 15, -1, -1)

        ################################################

        users_hLayout = QtWidgets.QHBoxLayout()
        users_hLayout.setSpacing(10)

        users_treeWidget = QtWidgets.QTreeWidget()
        users_treeWidget.setRootIsDecorated(False)

        ### THIS MAY BE CAUSING THE CRASH ###
        # header = users_treeWidget.header()
        # if FORCE_QT4:
        #     header.setResizeMode(QtWidgets.QHeaderView.Stretch)
        # else:
        #     header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        ### THIS MAY BE CAUSING THE CRASH ### -end

        users_treeWidget.setSortingEnabled(True)
        headerItem = QtWidgets.QTreeWidgetItem(["Full Name", "Initials"])

        users_treeWidget.setHeaderItem(headerItem)
        users_treeWidget.sortItems(1, QtCore.Qt.AscendingOrder)  # 1 is Date Column, 0 is Ascending order
        users_hLayout.addWidget(users_treeWidget)

        users_treeWidget.setColumnWidth(1000,10)



        users_vLayout = QtWidgets.QVBoxLayout()
        users_vLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)

        add_pushButton = QtWidgets.QPushButton()
        add_pushButton.setText(("Add..."))
        users_vLayout.addWidget(add_pushButton)

        remove_pushButton = QtWidgets.QPushButton()
        remove_pushButton.setText(("Remove"))
        users_vLayout.addWidget(remove_pushButton)

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        users_vLayout.addItem(spacerItem)

        users_hLayout.addLayout(users_vLayout)

        ################################################

        h1_s1_layout.addLayout(users_hLayout)
        users_Layout.addLayout(h1_s1_layout)

        def updateUsers():
            users_treeWidget.clear()
            for item in userList.items():
                name = item[0]
                initial = item[1]
                QtWidgets.QTreeWidgetItem(users_treeWidget, [name, initial])

        def addNewUserUI():
            addUser_Dialog = QtWidgets.QDialog(parent=self)
            addUser_Dialog.resize(260, 114)
            addUser_Dialog.setMaximumSize(QtCore.QSize(16777215, 150))
            addUser_Dialog.setFocusPolicy(QtCore.Qt.ClickFocus)
            addUser_Dialog.setWindowTitle(("Add New User"))

            verticalLayout = QtWidgets.QVBoxLayout(addUser_Dialog)

            addNewUser_label = QtWidgets.QLabel(addUser_Dialog)
            addNewUser_label.setText("Add New User:")
            verticalLayout.addWidget(addNewUser_label)

            formLayout = QtWidgets.QFormLayout()
            formLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
            formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
            formLayout.setRowWrapPolicy(QtWidgets.QFormLayout.DontWrapRows)
            formLayout.setLabelAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
            formLayout.setFormAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

            fullname_label = QtWidgets.QLabel(addUser_Dialog)
            fullname_label.setFocusPolicy(QtCore.Qt.StrongFocus)
            fullname_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
            fullname_label.setText("Full Name:")
            formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, fullname_label)

            fullname_lineEdit = QtWidgets.QLineEdit(addUser_Dialog)
            # fullname_lineEdit.setFocusPolicy(QtCore.Qt.TabFocus)
            fullname_lineEdit.setPlaceholderText("e.g \'Jon Snow\'")
            formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, fullname_lineEdit)

            initials_label = QtWidgets.QLabel(addUser_Dialog)
            initials_label.setText("Initials:")
            formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, initials_label)

            initials_lineEdit = QtWidgets.QLineEdit(addUser_Dialog)
            # initials_lineEdit.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            initials_lineEdit.setPlaceholderText("e.g \'js\' (must be unique)")
            formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, initials_lineEdit)
            verticalLayout.addLayout(formLayout)

            buttonBox = QtWidgets.QDialogButtonBox(addUser_Dialog)
            buttonBox.setOrientation(QtCore.Qt.Horizontal)
            buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
            verticalLayout.addWidget(buttonBox)
            addUser_Dialog.show()


            # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
            # sizePolicy.setHorizontalStretch(0)
            # sizePolicy.setVerticalStretch(0)
            buttonBox.setMaximumSize(QtCore.QSize(16777215, 30))
            buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setMinimumSize(QtCore.QSize(100, 30))
            buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).setMinimumSize(QtCore.QSize(100, 30))

            def onAddUser():
                userList[str(fullname_lineEdit.text())] = str(initials_lineEdit.text())
                updateUsers()
                self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())
                addUser_Dialog.close()

            buttonBox.accepted.connect(onAddUser)
            buttonBox.rejected.connect(addUser_Dialog.reject)

        def onRemoveUser():
            getSelected = users_treeWidget.selectedItems()
            if not getSelected:
                return
            for item in getSelected:
                del userList[unicode(item.text(0)).decode("utf-8")]
            updateUsers()
            self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())

        updateUsers()

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        users_Layout.addItem(spacerItem)
        self.contentsMaster_layout.addWidget(self.users_vis)

        ## SIGNALS

        add_pushButton.clicked.connect(addNewUserUI)
        remove_pushButton.clicked.connect(onRemoveUser)

    def _passwordsContent(self):
        # manager = self._getManager()
        # userList = self.allSettingsDict.get("users")

        passwords_Layout = QtWidgets.QVBoxLayout(self.passwords_vis)
        passwords_Layout.setSpacing(0)

        h1_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_label = QtWidgets.QLabel()
        h1_label.setText("Change Admin Password")
        h1_label.setFont(self.headerAFont)
        h1_horizontalLayout.addWidget(h1_label)
        passwords_Layout.addLayout(h1_horizontalLayout)

        h1_s1_layout = QtWidgets.QVBoxLayout()
        h1_s1_layout.setContentsMargins(-1, 15, -1, -1)
        h1_s1_layout.setSpacing(8)
        # h1_s1_layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)

        ################################################

        formLayout = QtWidgets.QFormLayout()
        formLayout.setSpacing(6)
        formLayout.setHorizontalSpacing(15)
        formLayout.setVerticalSpacing(10)
        formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
        formLayout.setSpacing(8)
        oldPass_label = QtWidgets.QLabel()
        oldPass_label.setText("Old Password: ")
        oldPass_lineEdit = QtWidgets.QLineEdit()
        oldPass_lineEdit.setMinimumWidth(200)
        oldPass_lineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        formLayout.addRow(oldPass_label, oldPass_lineEdit)

        newPass_label = QtWidgets.QLabel()
        newPass_label.setText("New Password: ")
        newPass_lineEdit = QtWidgets.QLineEdit()
        newPass_lineEdit.setMinimumWidth(200)
        newPass_lineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        formLayout.addRow(newPass_label, newPass_lineEdit)

        newPassAgain_label = QtWidgets.QLabel()
        newPassAgain_label.setText("New Password Again: ")
        newPassAgain_lineEdit = QtWidgets.QLineEdit()
        newPassAgain_lineEdit.setMinimumWidth(200)
        newPassAgain_lineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        formLayout.addRow(newPassAgain_label, newPassAgain_lineEdit)

        changePass_btn = QtWidgets.QPushButton()
        changePass_btn.setText("Change Password")
        changePass_btn.setMinimumWidth(200)
        changePass_btn.setMaximumWidth(200)
        # formLayout.addRow(changePass_btn)
        formLayout.setWidget(3,QtWidgets.QFormLayout.FieldRole, changePass_btn)


        ################################################

        h1_s1_layout.addLayout(formLayout)
        #
        # changePass_btn = QtWidgets.QPushButton()
        # changePass_btn.setText("Change Password")
        # h1_s1_layout.addWidget(changePass_btn)
        #
        passwords_Layout.addLayout(h1_s1_layout)


        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        passwords_Layout.addItem(spacerItem)
        self.contentsMaster_layout.addWidget(self.passwords_vis)

        def changePass():

            if not self.manager.checkPassword(oldPass_lineEdit.text()):
                self.infoPop(textTitle="Incorrect Password", textHeader="Invalid Old Password", type="C")
            if newPass_lineEdit.text() == "" or newPassAgain_lineEdit.text() == "":
                self.infoPop(textTitle="Error", textHeader="Admin Password cannot be blank", type="C")
            if newPass_lineEdit.text() != newPassAgain_lineEdit.text():
                self.infoPop(textTitle="Error", textHeader="New passwords are not matching", type="C")
            if self.manager.changePassword(oldPass_lineEdit.text(), newPass_lineEdit.text()):
                self.infoPop(textTitle="Success", textHeader="Success!\nPassword Changed", type="I")
            oldPass_lineEdit.setText("")
            newPass_lineEdit.setText("")
            newPassAgain_lineEdit.setText("")
            return

        ## SIGNALS
        changePass_btn.clicked.connect(changePass)

    def _namingConventions(self):
        # manager = self._getManager()
        settings = self.allSettingsDict.get("nameConventions")

        validFileNameTokens = ["<date>", "<baseName>", "<categoryName>", "<userInitials>"]

        namingConv_Layout = QtWidgets.QVBoxLayout(self.namingConventions_vis)
        namingConv_Layout.setSpacing(0)

        h1_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_label = QtWidgets.QLabel()
        h1_label.setText("Naming Conventions")
        h1_label.setFont(self.headerAFont)
        h1_label.setFocusPolicy(QtCore.Qt.StrongFocus)
        h1_horizontalLayout.addWidget(h1_label)
        namingConv_Layout.addLayout(h1_horizontalLayout)

        h1_s1_layout = QtWidgets.QVBoxLayout()
        h1_s1_layout.setContentsMargins(-1, 15, -1, -1)
        h1_s1_layout.setSpacing(8)
        # h1_s1_layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)

        ################################################
        formLayout = QtWidgets.QFormLayout()
        formLayout.setSpacing(8)

        fileNameConv_lbl = QtWidgets.QLabel()
        fileNameConv_lbl.setText("Scene Name Convention: ")
        fileNameConv_le = QtWidgets.QLineEdit()
        fileNameConv_le.setText(settings["fileName"])

        formLayout.addRow(fileNameConv_lbl, fileNameConv_le)

        infoLabel = QtWidgets.QLabel()
        infoLabel.setText("Valid tokens are %s" %(",".join(validFileNameTokens)))
        infoLabel.setWordWrap(True)
        formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, infoLabel)

        templateFolder_lbl = QtWidgets.QLabel()
        templateFolder_lbl.setText("Template Folder: ")
        templateFolder_hLayout = QtWidgets.QHBoxLayout()
        templateFolder_le = QtWidgets.QLineEdit()
        templateFolder_le.setPlaceholderText("Define Template Folder")
        templateFolder_le.setText(settings["templateFolder"])
        templateFolderBrowse_pb = QtWidgets.QPushButton()
        templateFolderBrowse_pb.setText("...")
        templateFolder_hLayout.addWidget(templateFolder_le)
        templateFolder_hLayout.addWidget(templateFolderBrowse_pb)
        formLayout.addRow(templateFolder_lbl, templateFolder_hLayout)
        infoLabel = QtWidgets.QLabel()
        infoLabel.setText("While creating a new project, all contents of the template folder will be copied into the project folder")
        infoLabel.setWordWrap(True)
        formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, infoLabel)


        h1_s1_layout.addLayout(formLayout)

        namingConv_Layout.addLayout(h1_s1_layout)

        def browseTemplateFolder():
            dlg = QtWidgets.QFileDialog()
            dlg.setFileMode(QtWidgets.QFileDialog.Directory)

            if dlg.exec_():
                # selectedroot = os.path.normpath(unicode(dlg.selectedFiles()[0]))
                selectedroot = os.path.normpath(unicode(dlg.selectedFiles()[0])).encode("utf-8")
                folderSize_inMB = get_size(selectedroot)/(1024*1024)
                if folderSize_inMB > settings["warningSizeLimit"]:
                    msg = "Selected Folder size is %s\n\nFrom now on this data will be copied EACH new project created with Tik Manager.\n\n Do you want to continue?" %folderSize_inMB
                    q = self.queryPop(type="yesNo", textTitle="Large Folder Size", textHeader=msg)
                    if q == "no":
                        return

                settings["templateFolder"] = selectedroot
                self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())
                templateFolder_le.setText(selectedroot)
            return

        def updateTemplateFolder():
            folder = unicode(templateFolder_le.text()).encode("utf-8")
            if not os.path.isdir(folder) and folder != "":
                msg = "Entered path is invalid. Resetting to default"
                self.infoPop(textTitle="Invalid Path", textHeader=msg)
                templateFolder_le.setText(settings["templateFolder"])
            else:
                settings["templateFolder"] = folder
                self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())


        def updateFileName():
            template = unicode(fileNameConv_le.text()).encode("utf-8")
            items = re.findall(r'<(.*?)\>', template)
            for x in items:
                if ("<%s>" %x) not in validFileNameTokens:
                    msg = "%s token is invalid\nValid tokens are: %s" %(x, ",".join(validFileNameTokens))
                    self.infoPop(textTitle="Invalid Token", textHeader=msg)
                    fileNameConv_le.setText(settings["fileName"])
                    return
            settings["fileName"] = template
            self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())

        def get_size(start_path='.'):
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(start_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    # skip if it is symbolic link
                    if not os.path.islink(fp):
                        total_size += os.path.getsize(fp)
            return total_size

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        namingConv_Layout.addItem(spacerItem)
        self.contentsMaster_layout.addWidget(self.namingConventions_vis)

        ## SIGNALS
        templateFolderBrowse_pb.clicked.connect(browseTemplateFolder)
        templateFolder_le.editingFinished.connect(updateTemplateFolder)
        fileNameConv_le.editingFinished.connect(updateFileName)


    def _createFormWidgets(self, loopList, settingsDict, formattingType, formlayout, dictUpdateMethod):
        """Creates widgets for the given form layout"""
        convertDict = {"true": True,
                       "True": True,
                       "false": False,
                       "False": False,
                       "0": False,
                       "1": True}

        if formattingType == "objImportMax" or \
                formattingType == "objExportMax" or \
                formattingType == "objImportMaya" or \
                formattingType == "objExportMaya" or \
                formattingType == "fbxImportMaya" or \
                formattingType == "fbxExportMaya":
            databaseType = "String"
        else:
            databaseType = "Direct"

        for widget in loopList:
            ## if the setting item is missing, skip its widget
            try:
                settingsDict[formattingType][widget["DictName"]]
            except KeyError:
                if widget["Type"] == "inf":
                    pass
                else:
                    continue

            if widget["Type"] == "inf":
                infoLabel = QtWidgets.QLabel()
                infoLabel.setText(widget["NiceName"])
                infoLabel.setFont(self.headerBFont)
                formlayout.addRow(infoLabel)
            elif widget["Type"] == "chb":
                chb = QtWidgets.QCheckBox()
                chb.setText(widget["NiceName"])
                chb.setObjectName(widget["DictName"])
                formlayout.addRow(chb)
                if databaseType == "String":
                    chb.setChecked(convertDict[settingsDict[formattingType][widget["DictName"]].replace(widget["asFlag"],"")])
                    if formattingType == "fbxImportMaya" or formattingType == "fbxExportMaya":
                        chb.stateChanged.connect(
                            lambda state, dict=widget["DictName"], flag=widget["asFlag"]: dictUpdateMethod(formattingType, dict, "%s%s" % (flag,str(bool(state)).lower()))
                        )
                    else:
                        chb.stateChanged.connect(
                            lambda state, dict=widget["DictName"], flag=widget["asFlag"]: dictUpdateMethod(formattingType, dict, "%s%s" % (flag,int(bool(state))))
                        )
                else:
                    chb.setChecked(settingsDict[formattingType][widget["DictName"]])
                    chb.stateChanged.connect(
                        lambda state, dict=widget["DictName"]: dictUpdateMethod(formattingType, dict, bool(int((state))))
                    )

            elif widget["Type"] == "combo":
                lbl = QtWidgets.QLabel()
                lbl.setText(widget["NiceName"])
                combo = QtWidgets.QComboBox()
                combo.setFocusPolicy(QtCore.Qt.NoFocus)
                combo.setObjectName(widget["DictName"])
                formlayout.addRow(lbl, combo)
                combo.addItems(widget["items"])
                if databaseType == "String":

                    if formattingType == "fbxImportMaya" or formattingType == "fbxExportMaya":
                        ffindex = combo.findText(settingsDict[formattingType][widget["DictName"]].replace(widget["asFlag"], ""), QtCore.Qt.MatchFixedString)
                        combo.setCurrentIndex(ffindex)
                        combo.currentIndexChanged[str].connect(
                            lambda arg, dict=widget["DictName"], flag=widget["asFlag"] : dictUpdateMethod(formattingType, dict,
                                                           "%s%s" %(flag, arg))
                        )
                    else:
                        combo.setCurrentIndex(int(settingsDict[formattingType][widget["DictName"]].replace(widget["asFlag"], "")))
                        combo.currentIndexChanged.connect(
                            lambda index, dict=widget["DictName"]: dictUpdateMethod(formattingType, dict,
                                                           unicode(index).encode("utf-8"))
                        )
                else:
                    ffindex = combo.findText(settingsDict[formattingType][widget["DictName"]],
                                                        QtCore.Qt.MatchFixedString)
                    combo.setCurrentIndex(ffindex)
                    combo.currentIndexChanged[str].connect(
                        lambda text, dict=widget["DictName"]: dictUpdateMethod(formattingType, dict,
                                                       unicode(text).encode("utf-8"))
                    )

            elif widget["Type"] == "spbDouble":
                lbl = QtWidgets.QLabel()
                lbl.setText(widget["NiceName"])
                spb = QtWidgets.QDoubleSpinBox()
                spb.setMinimumSize(self.minSPBSize[0], self.minSPBSize[1])
                spb.setFocusPolicy(QtCore.Qt.NoFocus)
                spb.setMinimumWidth(60)
                spb.setObjectName(widget["DictName"])
                formlayout.addRow(lbl, spb)
                if databaseType == "String":
                    spb.setValue(float(settingsDict[formattingType][widget["DictName"]].replace(widget["asFlag"],"")))
                    spb.valueChanged.connect(
                        lambda value, dict=widget["DictName"], flag=widget["asFlag"]: dictUpdateMethod(formattingType, dict,
                                                       "%s%s" %(flag, value))
                    )
                else:
                    spb.setValue(settingsDict[formattingType][widget["DictName"]])
                    spb.valueChanged.connect(
                        lambda value, dict=widget["DictName"]: dictUpdateMethod(formattingType, dict, value)
                    )

            elif widget["Type"] == "spbInt":
                lbl = QtWidgets.QLabel()
                lbl.setText(widget["NiceName"])
                spb = QtWidgets.QSpinBox()
                spb.setMinimumSize(self.minSPBSize[0], self.minSPBSize[1])
                spb.setFocusPolicy(QtCore.Qt.NoFocus)
                spb.setMinimumWidth(60)
                spb.setObjectName(widget["DictName"])
                formlayout.addRow(lbl, spb)
                if databaseType == "String":
                    spb.setValue(int(settingsDict[formattingType][widget["DictName"]].replace(widget["asFlag"],"")))
                    spb.valueChanged.connect(
                        lambda value, dict=widget["DictName"], flag=widget["asFlag"]: dictUpdateMethod(formattingType, dict, "%s%s" % (flag, value))
                    )
                else:
                    spb.setValue(settingsDict[formattingType][widget["DictName"]])
                    spb.valueChanged.connect(
                        lambda value, dict=widget["DictName"]: dictUpdateMethod(formattingType, dict, value)
                    )

            elif widget["Type"] == "str":
                lbl = QtWidgets.QLabel()
                lbl.setText(widget["NiceName"])
                le = QtWidgets.QLineEdit()
                le.setObjectName(widget["DictName"])
                formlayout.addRow(lbl, le)
                le.setText(settingsDict[formattingType][widget["DictName"]].replace(widget["asFlag"],""))
                le.textEdited.connect(
                    lambda text, dict=widget["DictName"], flag=widget["asFlag"]: dictUpdateMethod(formattingType, dict, "%s%s" %(flag, text))
                )


    def saveBaseSceneDialog(self):
        # This method IS Software Specific
        saveBaseScene_Dialog = QtWidgets.QDialog(parent=self)
        saveBaseScene_Dialog.setModal(True)
        saveBaseScene_Dialog.setObjectName(("save_Dialog"))
        saveBaseScene_Dialog.setWindowTitle("Save Base Scene")
        saveBaseScene_Dialog.resize(600, 350)

        sbs_masterLayout = QtWidgets.QVBoxLayout(saveBaseScene_Dialog)

        # ----------
        # HEADER BAR
        # ----------
        margin = 5
        colorWidget = QtWidgets.QWidget(saveBaseScene_Dialog)
        headerLayout = QtWidgets.QHBoxLayout(colorWidget)
        headerLayout.setSpacing(0)
        try: headerLayout.setMargin(0)
        except AttributeError: pass

        tikIcon_label = QtWidgets.QLabel(self.centralwidget)
        tikIcon_label.setProperty("header", True)
        tikIcon_label.setMaximumWidth(150)
        try: tikIcon_label.setMargin(margin)
        except AttributeError: pass
        tikIcon_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        tikIcon_label.setScaledContents(False)
        # saveBaseHeaderBitmap = QtGui.QPixmap(os.path.join(self.manager.getIconsDir(), "tmBaseScene.png"))
        # if FORCE_QT4:
        #     saveBaseHeaderBitmap = QtWidgets.QPixmap(":/icons/CSS/rc/tmBaseScene.png")
        # else:
        #     saveBaseHeaderBitmap = QtGui.QPixmap(":/icons/CSS/rc/tmBaseScene.png")
        saveBaseHeaderBitmap = self.Pixmap(":/icons/CSS/rc/tmBaseScene.png")
        tikIcon_label.setPixmap(saveBaseHeaderBitmap)

        headerLayout.addWidget(tikIcon_label)

        resolvedPath_label = QtWidgets.QLabel()
        resolvedPath_label.setProperty("header", True)
        try:resolvedPath_label.setMargin(margin)
        except AttributeError: pass
        resolvedPath_label.setIndent(12)
        # resolvedPath_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        if FORCE_QT4:
            resolvedPath_label.setFont(QtWidgets.QFont("Times", 10, QtWidgets.QFont.Bold))
        else:
            resolvedPath_label.setFont(QtGui.QFont("Times", 10, QtGui.QFont.Bold))

        resolvedPath_label.setWordWrap(True)

        headerLayout.addWidget(resolvedPath_label)


        sbs_masterLayout.addWidget(colorWidget)
        # ----------
        # ----------



        splitter = QtWidgets.QSplitter(saveBaseScene_Dialog)
        splitter.setFrameShape(QtWidgets.QFrame.NoFrame)
        splitter.setOrientation(QtCore.Qt.Horizontal)

        verticalLayoutWidget_2 = QtWidgets.QWidget(splitter)

        left_verticalLayout = QtWidgets.QVBoxLayout(verticalLayoutWidget_2)

        left_verticalLayout.setContentsMargins(0, -1, 12, 10)

        formLayout = QtWidgets.QFormLayout()
        formLayout.setContentsMargins(12, 20, 0, 12)
        formLayout.setHorizontalSpacing(16)
        formLayout.setVerticalSpacing(20)

        # resolvedName_label = QtWidgets.QLabel(verticalLayoutWidget_2)
        # resolvedName_label.setFrameShape(QtWidgets.QFrame.StyledPanel)
        # resolvedName_label.setText(("Resolved Name "))
        # formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, resolvedName_label)

        subProject_label = QtWidgets.QLabel(verticalLayoutWidget_2)
        subProject_label.setFrameShape(QtWidgets.QFrame.StyledPanel)
        subProject_label.setText(("Sub-Project "))
        formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, subProject_label)

        subProject_comboBox = QtWidgets.QComboBox(verticalLayoutWidget_2)
        subProject_comboBox.setMinimumSize(QtCore.QSize(150, 20))
        # subProject_comboBox.addItems((self.manager._subProjectsList))
        subProject_comboBox.addItems(self.manager.getSubProjects())
        subProject_comboBox.setCurrentIndex(self.subProject_comboBox.currentIndex())
        formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, subProject_comboBox)

        name_label = QtWidgets.QLabel(verticalLayoutWidget_2)
        name_label.setFrameShape(QtWidgets.QFrame.StyledPanel)
        name_label.setText(("Name          "))
        formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, name_label)

        lineEdit = QtWidgets.QLineEdit(verticalLayoutWidget_2)
        lineEdit.setPlaceholderText(("Choose an unique name"))
        formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, lineEdit)

        category_label = QtWidgets.QLabel(verticalLayoutWidget_2)
        category_label.setFrameShape(QtWidgets.QFrame.StyledPanel)
        category_label.setText(("Category    "))
        formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, category_label)

        category_comboBox = QtWidgets.QComboBox(verticalLayoutWidget_2)
        category_comboBox.setMinimumSize(QtCore.QSize(150, 20))
        # category_comboBox.addItems((self.manager._categories))
        category_comboBox.addItems(self.manager.getCategories())
        category_comboBox.setCurrentIndex(self.category_tabWidget.currentIndex())
        formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, category_comboBox)

        makeReference_checkBox = QtWidgets.QCheckBox(verticalLayoutWidget_2)
        makeReference_checkBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        makeReference_checkBox.setCheckable(True)
        makeReference_checkBox.setText("Make Reference")
        formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, makeReference_checkBox)

        if BoilerDict["Environment"] == "Houdini" or\
                BoilerDict["Environment"] == "Nuke" or \
                BoilerDict["Environment"] == "Standalone":
            makeReference_checkBox.setVisible(False)


        formats_horizontalLayout = QtWidgets.QHBoxLayout()

        # If there are multiple formats create radio buttons for each
        radioButtonList = []
        for format in BoilerDict["SceneFormats"]:
            radioButton = QtWidgets.QRadioButton(verticalLayoutWidget_2)
            radioButton.setText(format)
            radioButton.setMinimumSize(50,10)
            formats_horizontalLayout.addWidget(radioButton)
            radioButtonList.append(radioButton)

        # select the first radio button
        radioButtonList[0].setChecked(True)

        # hide radiobutton if only one format exists
        if len(radioButtonList) == 1:
            radioButtonList[0].setVisible(False)

        spacerItem = QtWidgets.QSpacerItem(80, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        formats_horizontalLayout.addItem(spacerItem)
        formLayout.setLayout(3, QtWidgets.QFormLayout.FieldRole, formats_horizontalLayout)
        left_verticalLayout.addLayout(formLayout)

        buttonBox = QtWidgets.QDialogButtonBox(verticalLayoutWidget_2)
        buttonBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        buttonBox.setCenterButtons(False)
        buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).setMinimumSize(QtCore.QSize(100, 30))
        buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setMinimumSize(QtCore.QSize(100, 30))

        left_verticalLayout.addWidget(buttonBox)

        verticalLayoutWidget = QtWidgets.QWidget(splitter)

        right_verticalLayout = QtWidgets.QVBoxLayout(verticalLayoutWidget)
        right_verticalLayout.setContentsMargins(-1, -1, 10, 10)
        right_verticalLayout.setSpacing(6)

        notes_label = QtWidgets.QLabel(verticalLayoutWidget)
        notes_label.setText(("Notes"))
        right_verticalLayout.addWidget(notes_label)

        notes_plainTextEdit = QtWidgets.QPlainTextEdit(verticalLayoutWidget)
        # notes_plainTextEdit.setFrameShape(QtWidgets.QFrame.StyledPanel)
        right_verticalLayout.addWidget(notes_plainTextEdit)

        sbs_masterLayout.addWidget(splitter)

        ######
        scenesDir = self.manager.scenesDir
        projectDir = self.manager.projectDir
        relScenesDir = os.path.relpath(scenesDir, projectDir)
        def getResolvedPath():

            category = category_comboBox.currentText()
            name = lineEdit.text()
            userInitials = self.manager.currentUserInitials

            ## Naming Dictionary
            nameDict = {
                "baseName": name,
                "categoryName": category,
                "userInitials": userInitials,
                "date": "" # date is unnecessary since it will be calculated in SmRoot->resolveSaveName
            }
            sceneName = self.manager.resolveSaveName(nameDict, 1)

            if self._checkValidity(lineEdit.text(), buttonBox, lineEdit):
                subP=subProject_comboBox.currentText()
                subProject = "" if subP == "None" else subP
                sceneFormat = ""
                for button in radioButtonList:
                    if button.isChecked():
                        sceneFormat = button.text()
                        break
                resolvedText = "{0}\{1}\{2}\{3}\{4}.{5}".format(relScenesDir, category, subProject, name, sceneName, sceneFormat)
                resolvedText = resolvedText.replace("\\\\", "\\")
            else:
                resolvedText = ""
            resolvedPath_label.setText(resolvedText)

        def saveCommand():
            checklist = self.manager.preSaveChecklist()
            for msg in checklist:
                q = self.queryPop(type="yesNo", textTitle="Checklist", textHeader=msg)
                if q == "no":
                    return
                else:
                    self.manager.errorLogger(title = "Disregarded warning" , errorMessage=msg)
            category = category_comboBox.currentText()
            name = lineEdit.text()
            subIndex = subProject_comboBox.currentIndex()
            makeReference = makeReference_checkBox.checkState()
            notes = notes_plainTextEdit.toPlainText()
            for button in radioButtonList:
                if button.isChecked():
                    sceneFormat = button.text()
                    break
            AssertionError(sceneFormat)
            state = self.manager.saveBaseScene(str(category), str(name), subIndex, makeReference, notes, sceneFormat)
            if state[0] != -1:
                self.populateBaseScenes()
                self.manager.getOpenSceneInfo()
                self._initOpenScene()
                saveBaseScene_Dialog.accept()
            else:
                pass

        # SIGNALS
        # -------
        lineEdit.textChanged.connect(getResolvedPath)
        # lineEdit.textChanged.connect(lambda: self._checkValidity(lineEdit.text(), buttonBox, lineEdit))


        buttonBox.accepted.connect(saveCommand)

        for rb in radioButtonList:
            rb.toggled.connect(getResolvedPath)


        # self.sd_buttonBox.accepted.connect(self.save_Dialog.accept)
        buttonBox.rejected.connect(saveBaseScene_Dialog.reject)
        # QtCore.QMetaObject.connectSlotsByName(self.save_Dialog)

        saveBaseScene_Dialog.show()

    def saveAsVersionDialog(self):
        # This method IS Software Specific
        saveV_Dialog = QtWidgets.QDialog(parent=self)
        saveV_Dialog.setModal(True)
        saveV_Dialog.resize(300, 250)
        saveV_Dialog.setMinimumSize(QtCore.QSize(300, 250))
        saveV_Dialog.setMaximumSize(QtCore.QSize(600, 600))
        saveV_Dialog.setWindowTitle(("Save As Version"))

        sv_masterLayout = QtWidgets.QVBoxLayout(saveV_Dialog)

        # ----------
        # HEADER BAR
        # ----------
        margin = 5
        # barColor = "background-color: rgb(80,80,80);"
        # barColor = "background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #565656, stop: 0.1 #525252, stop: 0.5 #4e4e4e, stop: 0.9 #4a4a4a, stop: 1 #464646);"
        colorWidget = QtWidgets.QWidget(saveV_Dialog)
        headerLayout = QtWidgets.QHBoxLayout(colorWidget)
        headerLayout.setSpacing(0)
        try: headerLayout.setMargin(0)
        except AttributeError: pass

        tikIcon_label = QtWidgets.QLabel(self.centralwidget)
        # tikIcon_label.setFixedSize(115, 30)
        tikIcon_label.setProperty("header", True)
        tikIcon_label.setMaximumWidth(114)
        try: tikIcon_label.setMargin(margin)
        except AttributeError: pass
        tikIcon_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        tikIcon_label.setScaledContents(False)
        # saveVersionHeaderBitmap = QtGui.QPixmap(os.path.join(self.manager.getIconsDir(), "tmVersion.png"))
        # if FORCE_QT4:
        #     saveVersionHeaderBitmap = QtWidgets.QPixmap(":/icons/CSS/rc/tmVersion.png")
        # else:
        #     saveVersionHeaderBitmap = QtGui.QPixmap(":/icons/CSS/rc/tmVersion.png")
        saveVersionHeaderBitmap = self.Pixmap(":/icons/CSS/rc/tmVersion.png")
        tikIcon_label.setPixmap(saveVersionHeaderBitmap)

        headerLayout.addWidget(tikIcon_label)

        resolvedPath_label = QtWidgets.QLabel()
        resolvedPath_label.setProperty("header", True)
        try: resolvedPath_label.setMargin(margin)
        except AttributeError: pass
        resolvedPath_label.setIndent(2)
        # resolvedPath_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        if FORCE_QT4:
            resolvedPath_label.setFont(QtWidgets.QFont("Times", 7, QtWidgets.QFont.Bold))
        else:
            resolvedPath_label.setFont(QtGui.QFont("Times", 7, QtGui.QFont.Bold))
        resolvedPath_label.setWordWrap(True)

        headerLayout.addWidget(resolvedPath_label)


        sv_masterLayout.addWidget(colorWidget)
        # ----------
        # ----------


        right_verticalLayout = QtWidgets.QVBoxLayout()
        right_verticalLayout.setContentsMargins(-1, -1, 10, 10)
        right_verticalLayout.setSpacing(6)

        # resolvedPath_label = QtWidgets.QLabel(saveV_Dialog)
        # resolvedPath_label.setText((""))
        # resolvedPath_label.setIndent(12)
        # resolvedPath_label.setWordWrap(True)
        # # resolvedPath_label.setFont(QtGui.QFont("Time", 7, QtGui.QFont.Bold))
        # right_verticalLayout.addWidget(resolvedPath_label)


        notes_label = QtWidgets.QLabel(saveV_Dialog)
        notes_label.setText(("Notes"))
        right_verticalLayout.addWidget(notes_label)

        notes_plainTextEdit = QtWidgets.QPlainTextEdit(saveV_Dialog)
        notes_plainTextEdit.setFrameShape(QtWidgets.QFrame.StyledPanel)
        right_verticalLayout.addWidget(notes_plainTextEdit)

        formats_horizontalLayout = QtWidgets.QHBoxLayout()
        right_verticalLayout.addLayout(formats_horizontalLayout)
        spacerItem = QtWidgets.QSpacerItem(80, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        formats_horizontalLayout.addItem(spacerItem)

        ext = os.path.splitext(self.manager.getSceneFile())[1][1:]
        radioButtonList = []
        for format in BoilerDict["SceneFormats"]:
            radioButton = QtWidgets.QRadioButton(saveV_Dialog)
            radioButton.setText(format)
            formats_horizontalLayout.addWidget(radioButton)
            radioButtonList.append(radioButton)
            if format == ext:
                radioButton.setChecked(True)

        # select the first radio button
        # radioButtonList[0].setChecked(True)

        # hide radiobutton if only one format exists
        if len(radioButtonList) == 1:
            radioButtonList[0].setVisible(False)

        formats_horizontalLayout_2 = QtWidgets.QHBoxLayout()
        spacerItem1 = QtWidgets.QSpacerItem(80, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        formats_horizontalLayout_2.addItem(spacerItem1)

        makeReference_checkBox = QtWidgets.QCheckBox(saveV_Dialog)
        makeReference_checkBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        makeReference_checkBox.setInputMethodHints(QtCore.Qt.ImhPreferUppercase)
        makeReference_checkBox.setText("Make Reference")
        makeReference_checkBox.setCheckable(True)

        if BoilerDict["Environment"] == "Houdini" or\
                BoilerDict["Environment"] == "Nuke" or \
                BoilerDict["Environment"] == "Standalone":
            makeReference_checkBox.setVisible(False)

        formats_horizontalLayout_2.addWidget(makeReference_checkBox)
        right_verticalLayout.addLayout(formats_horizontalLayout_2)

        sv_buttonBox = QtWidgets.QDialogButtonBox(saveV_Dialog)
        sv_buttonBox.setOrientation(QtCore.Qt.Horizontal)
        sv_buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        right_verticalLayout.addWidget(sv_buttonBox)
        sv_masterLayout.addLayout(right_verticalLayout)


        buttonS = sv_buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
        buttonS.setText('Save As Version')
        buttonS.setMinimumSize(QtCore.QSize(100, 30))
        buttonC = sv_buttonBox.button(QtWidgets.QDialogButtonBox.Cancel)
        buttonC.setText('Cancel')
        buttonC.setMinimumSize(QtCore.QSize(100, 30))

        def saveAsVersionCommand():
            # TODO : ref
            checklist = self.manager.preSaveChecklist()
            for msg in checklist:
                q = self.queryPop(type="yesNo", textTitle="Checklist", textHeader=msg)
                if q == "no":
                    return
                else:
                    self.manager.errorLogger(title = "Disregarded warning" , errorMessage=msg)

            for button in radioButtonList:
                if button.isChecked():
                    sceneFormat = button.text()
                    break

            sceneInfo = self.manager.saveVersion(makeReference=makeReference_checkBox.checkState(),
                                                 versionNotes=notes_plainTextEdit.toPlainText(),
                                                 sceneFormat=sceneFormat)

            if not sceneInfo == -1:
                self.statusBar().showMessage("Status | Version Saved => %s" % len(sceneInfo["Versions"]))
            self.manager.currentBaseSceneName = sceneInfo["Name"]
            self.manager.currentVersionIndex = len(sceneInfo["Versions"])

            # currentRow = self.scenes_listWidget.currentRow()
            # currentIndex = self.scenes_listWidget.currentIndex()


            self.populateBaseScenes()
            self.onBaseSceneChange()
            # self.scenes_listWidget.setCurrentRow(currentRow)
            # self.scenes_listWidget.setCurrentIndex(currentIndex)
            saveV_Dialog.accept()

        def getResolvedPath():
            # Resolve and display filename info
            sceneFormat = ""
            for button in radioButtonList:
                if button.isChecked():
                    sceneFormat = button.text()
                    break

            sceneInfo = self.manager.getOpenSceneInfo()
            if not sceneInfo:
                return
            jsonFile = sceneInfo["jsonFile"]
            jsonInfo = self.manager._loadJson(jsonFile)

            currentVersion = len(jsonInfo["Versions"]) + 1
            ## Naming Dictionary
            nameDict = {
                "baseName": jsonInfo["Name"],
                "categoryName": jsonInfo["Category"],
                "userInitials": self.manager.currentUserInitials,
                "date": "" # date is unnecessary since it will be calculated in SmRoot->resolveSaveName
            }
            sceneName = self.manager.resolveSaveName(nameDict, currentVersion)

            # sceneName = "{0}_{1}_{2}_v{3}".format(jsonInfo["Name"], jsonInfo["Category"],
            #                                       self.manager.currentUserInitials,
            #                                       str(currentVersion).zfill(3))
            relSceneFile = os.path.join(jsonInfo["Path"], "{0}.{1}".format(sceneName, sceneFormat))
            resolvedPath_label.setText("\\%s" %relSceneFile)

        getResolvedPath()

        # SIGNALS
        # -------
        sv_buttonBox.accepted.connect(saveAsVersionCommand)
        sv_buttonBox.rejected.connect(saveV_Dialog.reject)

        for rb in radioButtonList:
            rb.toggled.connect(getResolvedPath)

        sceneInfo = self.manager.getOpenSceneInfo()
        if sceneInfo:
            saveV_Dialog.show()
        else:
            self.manager.errorLogger(title="Misuse Error", errorMessage="A version tried to be saved without base scene")
            self.infoPop(textInfo="Version Saving not possible",
                         textHeader="Current Scene is not a Base Scene. Only versions of Base Scenes can be saved", textTitle="Not a Base File", type="C")

    def addNoteDialog(self):
        # This method IS Software Specific
        manager = self._getManager()
        # if BoilerDict["Environment"]=="Standalone":
        #     manager=self._getManager()
        # else:
        #     manager = self.manager

        row =  self.scenes_listWidget.currentIndex().row()
        if row == -1:
            return

        addNotes_Dialog = QtWidgets.QDialog(parent=self)
        addNotes_Dialog.setModal(True)
        addNotes_Dialog.resize(255, 290)
        addNotes_Dialog.setMinimumSize(QtCore.QSize(255, 290))
        addNotes_Dialog.setMaximumSize(QtCore.QSize(255, 290))
        addNotes_Dialog.setWindowTitle(("Add Notes"))

        addNotes_label = QtWidgets.QLabel(addNotes_Dialog)
        addNotes_label.setGeometry(QtCore.QRect(15, 15, 100, 20))
        addNotes_label.setText(("Additional Notes"))

        addNotes_textEdit = QtWidgets.QTextEdit(addNotes_Dialog)
        addNotes_textEdit.setGeometry(QtCore.QRect(15, 40, 215, 170))

        addNotes_buttonBox = QtWidgets.QDialogButtonBox(addNotes_Dialog)
        addNotes_buttonBox.setGeometry(QtCore.QRect(20, 250, 220, 32))
        addNotes_buttonBox.setOrientation(QtCore.Qt.Horizontal)
        addNotes_buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel)
        addNotes_buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).setMinimumSize(QtCore.QSize(100, 30))
        addNotes_buttonBox.button(QtWidgets.QDialogButtonBox.Save).setMinimumSize(QtCore.QSize(100, 30))

        buttonS = addNotes_buttonBox.button(QtWidgets.QDialogButtonBox.Save)
        buttonS.setText('Add Notes')
        buttonC = addNotes_buttonBox.button(QtWidgets.QDialogButtonBox.Cancel)
        buttonC.setText('Cancel')

        addNotes_buttonBox.accepted.connect(lambda: manager.addNote(addNotes_textEdit.toPlainText()))
        addNotes_buttonBox.accepted.connect(self.onVersionChange)
        addNotes_buttonBox.accepted.connect(addNotes_Dialog.accept)

        addNotes_buttonBox.rejected.connect(addNotes_Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(addNotes_Dialog)

        addNotes_Dialog.show()

    def callbackRefresh(self):
        """
        Buffer script for workspace change scriptjob
        when a scene saved it also triggers "workspaceChanged" scriptjob event.
        To prevent unnecessary initialization, this functions acts as a buffer
        """
        manager = self._getManager()
        # logger.debug("callbackRefresh called")
        oldProject = manager.projectDir
        newProject = manager.getProjectDir()
        if not oldProject == newProject:
            # logger.debug("callbackRefresh - project changed")
            self.initMainUI()
        else:
            # logger.debug("callbackRefresh - project same")
            return

    def initMainUI(self, newborn=False):
        """Initialization Method for MainUI. Needs to be overriden for Standalone Version"""

        self.load_radioButton.setChecked(self.manager.currentMode)
        self.reference_radioButton.setChecked(not self.manager.currentMode)
        self.category_tabWidget.setCurrentIndex(self.manager.currentTabIndex)

        if not newborn:
            swName = self.manager.swName
            self.manager.init_paths(swName)
            self.manager.init_database()

        self._initCategories()

        self.manager.getOpenSceneInfo()

        self._initOpenScene()

        # init project
        self.project_lineEdit.setText(self.manager.projectDir)

        # init subproject

        self._initSubProjects()

        # init base scenes
        self.populateBaseScenes()


        self._initUsers()

        # disable the version related stuff
        # self._vEnableDisable()
        self.onModeChange()

    def refresh(self):
        # currentUserIndex = self.user_comboBox.currentIndex()
        # currentTabIndex = self
        self.initMainUI()

        self.populateBaseScenes()

    def rcAction_scenes(self, command):
        # This method IS Software Specific
        manager = self._getManager()
        # if BoilerDict["Environment"]=="Standalone":
        #     manager=self._getManager()
        # else:
        #     manager = self.manager

        if command == "importScene":
            manager.importBaseScene()

        if command == "showInExplorerMaya":
            manager.showInExplorer(manager.currentBaseScenePath)

        if command == "showInExplorerPB":
            manager.showInExplorer(manager.currentPreviewPath)

        if command == "showInExplorerData":
            # filePath = manager._baseScenesInCategory[manager.currentBaseSceneName]
            filePath = manager.getBaseScenesInCategory()[manager.currentBaseSceneName]
            dirPath = os.path.dirname(filePath)
            manager.showInExplorer(dirPath)

        if command == "showInExplorerProject":
            manager.showInExplorer(manager.projectDir)

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
            helpText.setFontPointSize(14)
            helpText.setText(textInfo)
            messageLayout.addWidget(helpText)

        if command == "viewRender":
            imagePath = os.path.join(manager.projectDir, "images", manager.currentBaseSceneName)
            ImageViewer.MainUI(manager.projectDir, relativePath=imagePath, recursive=True).show()

    def rcAction_thumb(self, command):
        # This method IS Software Specific
        manager = self._getManager()
        if command == "file":
            fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', manager.projectDir,"Image files (*.jpg *.gif)")[0]
            if not fname: # if dialog is canceled
                return

        elif command == "currentView":
            fname = ""

        else:
            return

        manager.replaceThumbnail(filePath=fname)
        self.onVersionChange()

    def onContextMenu_scenes(self, point):
        # This method IS Software Specific
        manager = self._getManager()

        # row = self.scenes_listWidget.currentRow()
        row = self.scenes_listWidget.currentIndex().row()

        if row == -1:
            self.scenes_rcItem_0.setEnabled(False)
            self.scenes_rcItem_1.setEnabled(False)
            self.scenes_rcItem_2.setEnabled(False)
            self.scenes_rcItem_3.setEnabled(False)
            self.scenes_rcItem_4.setEnabled(False)
            self.scenes_rcItem_5.setEnabled(False)
            self.scenes_rcItem_6.setEnabled(True)
        else:
            self.scenes_rcItem_0.setEnabled(True)
            self.scenes_rcItem_1.setEnabled(os.path.isdir(manager.currentBaseScenePath))
            self.scenes_rcItem_2.setEnabled(os.path.isdir(manager.currentPreviewPath))
            self.scenes_rcItem_3.setEnabled(True)
            self.scenes_rcItem_4.setEnabled(True)
            # show context menu
            self.scenes_rcItem_5.setEnabled(
                os.path.isdir(os.path.join(manager.projectDir, "images", manager.currentBaseSceneName)))
            self.scenes_rcItem_6.setEnabled(True)

        self.popMenu_scenes.exec_(self.scenes_listWidget.mapToGlobal(point))

    def onContextMenu_thumbnail(self, point):
        # This method is NOT Software Specific
        row = self.scenes_listWidget.currentIndex().row()
        if row == -1:
            return
        # show context menu
        self.popMenu_thumbnail.exec_(self.thumbnail_label.mapToGlobal(point))

    def onPbSettings(self, env=None):
        """This function acts as a software switcher for PB settings"""
        if not env:
            env = BoilerDict["Environment"]
        if env == "Maya":
            self.pbSettingsMayaUI()
            return
        elif env == "3dsMax":
            self.pbSettingsMaxUI()
            return
        elif env == "Houdini":
            print("not yet implemented")
            return
        elif env == "Standalone":
            manager = self._getManager()
            self.onPbSettings(env=manager.niceName)

    def onProjectChange(self):
        # This method is NOT Software Specific
        self.initMainUI()

    def onSubProjectChange(self):
        # This method IS Software Specific
        manager = self._getManager()
        manager.currentSubIndex = self.subProject_comboBox.currentIndex()
        self.onCategoryChange()

    def onCategoryChange(self):
        # This method IS Software Specific
        manager = self._getManager()
        manager.currentTabIndex = self.category_tabWidget.currentIndex()
        self.populateBaseScenes()
        self.onBaseSceneChange()

    def onUserChange(self):
        # This method is NOT Software Specific
        self.manager.currentUser = str(self.user_comboBox.currentText())

    def onModeChange(self):
        # This method is NOT Software Specific

        self._vEnableDisable()

        if self.load_radioButton.isChecked():
            self.loadScene_pushButton.setText("Load Scene")
            self.scenes_listWidget.setProperty("reference", False)
        else:
            self.loadScene_pushButton.setText("Reference Scene")
            self.scenes_listWidget.setProperty("reference", True)

        self.scenes_listWidget.setStyleSheet("") #refresh
        self.manager.currentMode = self.load_radioButton.isChecked()
        self.populateBaseScenes()

    def onBaseSceneChange(self):
        # This method IS Software Specific
        manager = self._getManager()
        self.version_comboBox.blockSignals(True)
        #clear version_combobox
        self.version_comboBox.clear()

        # row = self.scenes_listWidget.currentRow()
        row = self.scenes_listWidget.currentIndex().row()
        if row == -1:
            manager.currentBaseSceneName = ""
        else:
            # manager.currentBaseSceneName = str(self.scenes_listWidget.currentItem().text())
            manager.currentBaseSceneName = str(self.scenes_listWidget.currentItem().text(0))

        self._vEnableDisable()
        #get versions and add it to the combobox
        versionData = manager.getVersions()
        for num in range(len(versionData)):
            self.version_comboBox.addItem("v{0}".format(str(num + 1).zfill(3)))
        self.version_comboBox.setCurrentIndex(manager.currentVersionIndex-1)
        self.onVersionChange()

        self.version_comboBox.blockSignals(False)

    def onVersionChange(self):
        # This method IS Software Specific
        manager = self._getManager()


        if self.version_comboBox.currentIndex() is not -1:
            manager.currentVersionIndex = self.version_comboBox.currentIndex() + 1

        # self.version_comboBox.blockSignals(True)

        # clear Notes and verison combobox
        self.notes_textEdit.clear()

        # update notes
        self.notes_textEdit.setPlainText(manager.getNotes())

        self.tPixmap = self.Pixmap(manager.getThumbnail())

        if self.tPixmap.isNull():
            self.thumbnail_label.setPixmap(self.E_tPixmap)
        else:
            self.thumbnail_label.setPixmap(self.tPixmap)

        if manager.currentVersionIndex != len(manager.getVersions()) and manager.currentVersionIndex != -1:
            self.version_comboBox.setProperty("preVersion", True)
        else:
            self.version_comboBox.setProperty("preVersion", False)
        self.version_comboBox.setStyleSheet("")

        self._vEnableDisable()

    def populateBaseScenes(self, deepCheck=False):
        # This method IS Software Specific
        manager = self._getManager()
        if not manager:
            return

        self.scenes_listWidget.blockSignals(True)
        self.scenes_listWidget.clear()
        baseScenesDict = manager.getBaseScenesInCategory()
        if self.reference_radioButton.isChecked():
            for key in baseScenesDict:
                if manager.checkReference(baseScenesDict[key]) == 1:
                    timestamp = os.path.getmtime(baseScenesDict[key])
                    timestampFormatted = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                    item = QtWidgets.QTreeWidgetItem(self.scenes_listWidget, [key, str(timestampFormatted)])

        else:
            if BoilerDict["Environment"] == "Standalone":
                codeDict = {-1: QtWidgets.QColor(255, 0, 0, 255), 1: QtWidgets.QColor(0, 255, 0, 255),
                            0: QtWidgets.QColor(255, 255, 0, 255), -2: QtWidgets.QColor(20, 20, 20, 255)}
            else:
                codeDict = {-1: QtGui.QColor(255, 0, 0, 255), 1: QtGui.QColor(0, 255, 0, 255),
                            0: QtGui.QColor(255, 255, 0, 255), -2: QtGui.QColor(20, 20, 20, 255)}  # dictionary for color codes red, green, yellow

            for key in baseScenesDict:
                retCode = manager.checkReference(baseScenesDict[key], deepCheck=deepCheck) # returns -1, 0 or 1 for color ref
                color = codeDict[retCode]
                timestamp = os.path.getmtime(baseScenesDict[key])
                timestampFormatted = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                item = QtWidgets.QTreeWidgetItem(self.scenes_listWidget, [key, str(timestampFormatted)])
                item.setForeground(0, color)


        self.scenes_listWidget.blockSignals(False)

    def onLoadScene(self):
        # This method IS Software Specific. BUT overriding it is better, so it is not selecting manager
        # row = self.scenes_listWidget.currentRow()
        row = self.scenes_listWidget.currentIndex().row()
        if row == -1:
            return

        res, msg = self.manager.compareVersions()
        if res == -1:
            mismatch = self.queryPop(type="yesNo", textTitle="Version Mismatch", textHeader=msg)
            if mismatch == "no":
                return
            else:
                self.manager.errorLogger(title="Disregarded warning", errorMessage=msg)

        if self.load_radioButton.isChecked():
            if self.manager.isSceneModified():
                q = self.queryPop(type="yesNoCancel", textTitle="Save Changes", textInfo="Save Changes to",
                                  textHeader=("Scene Modified"))
                if q == "yes":
                    self.manager.saveSimple()
                    self.manager.loadBaseScene(force=True)
                if q == "no":
                    self.manager.loadBaseScene(force=True)
                if q == "cancel":
                    pass


            else: # if current scene saved and secure
                self.manager.loadBaseScene(force=True)
                self.manager.getOpenSceneInfo()
                self._initOpenScene()

            self.statusBar().showMessage("Status | Scene Loaded => %s" % self.manager.currentBaseSceneName)

        if self.reference_radioButton.isChecked():
            self.manager.referenceBaseScene()
            # self.populateScenes()
            self.statusBar().showMessage("Status | Scene Referenced => %s" % self.manager.currentBaseSceneName)

    def onMakeReference(self):
        # This method IS Software Specific.

        manager = self._getManager()

        manager.makeReference()

        self.onVersionChange()
        self.statusBar().showMessage(
            "Status | Version {1} is the new reference of {0}".format(manager.currentBaseSceneName, manager.currentVersionIndex))
        # currentRow = self.scenes_listWidget.currentIndex().row()

        # currentIndex = self.scenes_listWidget.currentIndex()
        self.populateBaseScenes()
        return

        # self.scenes_listWidget.setCurrentRow(currentRow)
        # self.scenes_listWidget.setCurrentIndex(currentIndex)

    def onShowPreview(self):
        # This method IS Software Specific.
        manager = self._getManager()

        # row = self.scenes_listWidget.currentRow()
        row = self.scenes_listWidget.currentIndex().row()
        if row == -1:
            return
        cameraList = manager.getPreviews()
        if len(manager.getPreviews()) == 1:
            manager.playPreview(cameraList[0])
        else:
            zortMenu = QtWidgets.QMenu()
            for z in cameraList:
                tempAction = QtWidgets.QAction(z, self)
                zortMenu.addAction(tempAction)
                ## Take note about the usage of lambda "item=z" makes it possible using the loop, ignore -> for discarding emitted value
                tempAction.triggered.connect(lambda ignore=z, item=z: manager.playPreview(str(item)))
                # tempAction.triggered.connect(lambda item=z: manager.playPreview(str(item)))

            if BoilerDict["Environment"] == "Standalone":
                zortMenu.exec_((QtWidgets.QCursor.pos()))
            else:
                zortMenu.exec_((QtGui.QCursor.pos()))

    def onDeleteBaseScene(self):
        # This method IS Software Specific.

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

        row = self.scenes_listWidget.currentIndex().row()
        if not row == -1:
            manager.deleteBasescene(manager.currentDatabasePath)
            self.populateBaseScenes()
            self.statusBar().showMessage("Status | Scene Deleted => %s" % name)

    def onDeleteReference(self):
        # This method IS Software Specific.

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

        row = self.scenes_listWidget.currentIndex().row()
        if not row == -1:
            manager.deleteReference(manager.currentDatabasePath)
            self.populateBaseScenes()
            self.statusBar().showMessage("Status | Reference of %s is deleted" % name)

    def onIviewer(self):
        # This method is NOT Software Specific.
        ImageViewer.MainUI(self.manager.projectDir).show()

    def onPMaterials(self):
        import projectMaterials
        pMat = projectMaterials.MainUI(projectPath=self.manager.projectDir)
        pMat.show()

    def onAssetLibrary(self):
        import assetLibrary
        assLib = assetLibrary.MainUI().show()

    def onCreatePreview(self):
        self.statusBar().showMessage("Creating Preview...")
        self.manager.createPreview()
        self.statusBar().showMessage("Status | Idle")

    def _getManager(self):
        """Returns current manager"""
        return self.manager

    def _initSubProjects(self):
        # This method IS Software Specific.
        manager = self._getManager()
        if not manager:
            return

        self.subProject_comboBox.blockSignals(True)

        self.subProject_comboBox.clear()
        self.subProject_comboBox.addItems(manager.getSubProjects())
        self.subProject_comboBox.setCurrentIndex(manager.currentSubIndex)

        self.subProject_comboBox.blockSignals(False)

    def _initCategories(self):
        # This method IS Software Specific.
        manager = self._getManager()
        if not manager:
            return

        self.category_tabWidget.blockSignals(True)
        self.category_tabWidget.clear()

        for i in manager._categories:
            self.preTab = QtWidgets.QWidget()
            self.preTab.setObjectName((i))
            self.category_tabWidget.addTab(self.preTab, (i))

        self.category_tabWidget.setCurrentIndex(manager.currentTabIndex)
        self.category_tabWidget.blockSignals(False)

    def _initUsers(self):
        # init users
        self.user_comboBox.blockSignals(True)

        self.user_comboBox.clear()
        self.user_comboBox.addItems(self.manager.getUsers())
        index = self.user_comboBox.findText(self.manager.currentUser, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.user_comboBox.setCurrentIndex(index)

        self.user_comboBox.blockSignals(False)

    def _initOpenScene(self):
        openSceneInfo = self.manager._openSceneInfo

        if openSceneInfo:
            jList = []
            if openSceneInfo["subProject"] != "None":
                jList.append(openSceneInfo["subProject"])
            jList.extend([openSceneInfo["category"], openSceneInfo["shotName"]])
            dMsg = " > ".join(jList)
            self.baseScene_label.setText(dMsg)
            # self.baseScene_label.setStyleSheet("color: cyan")
            self.baseScene_label.setProperty("baseScene", True)
        else:
            self.baseScene_label.setText("Current Scene is not a Base Scene")
            # self.baseScene_label.setStyleSheet("color: yellow")
            self.baseScene_label.setProperty("baseScene", False)
        self.baseScene_label.setStyleSheet("")

    def _checkValidity(self, text, button, lineEdit, allowSpaces=False, directory=False):
        if text == "":
            lineEdit.setProperty("error", False)
            lineEdit.setStyleSheet("") #update
            return False
        if self.manager.nameCheck(text, allowSpaces=allowSpaces, directory=directory):
            # lineEdit.setStyleSheet("background-color: rgb(40,40,40); color: white")
            lineEdit.setProperty("error", False)
            lineEdit.setStyleSheet("") #update
            button.setEnabled(True)
            return True
        else:
            # lineEdit.setStyleSheet("background-color: red; color: black")
            lineEdit.setProperty("error", True)
            lineEdit.setStyleSheet("") #update
            button.setEnabled(False)
            return False
        # print lineEdit.styleSheet()

    def _vEnableDisable(self):
        manager = self._getManager()
        if self.load_radioButton.isChecked() and manager.currentBaseSceneName:
            self.version_comboBox.setEnabled(True)
            # if manager.getPreviews() is not []:
            #     self.showPreview_pushButton.setEnabled(True)
            # else:
            #     self.showPreview_pushButton.setEnabled(False)
            self.makeReference_pushButton.setEnabled(True)
            self.addNote_pushButton.setEnabled(True)
            self.version_label.setEnabled(True)
        else:
            self.version_comboBox.setEnabled(False)
            self.showPreview_pushButton.setEnabled(False)
            self.makeReference_pushButton.setEnabled(False)
            self.addNote_pushButton.setEnabled(False)
            self.version_label.setEnabled(False)

        if manager.getPreviews():
            self.showPreview_pushButton.setEnabled(True)
        else:
            self.showPreview_pushButton.setEnabled(False)

    def onCheckNewVersion(self):
        manager = self._getManager()
        message, downloadPath, whatsNewPath = manager.checkNewVersion()

        vCheck_mBox = QtWidgets.QMessageBox(parent=self)
        vCheck_mBox.setIcon(QtWidgets.QMessageBox.Information)

        vCheck_mBox.setWindowTitle("Check for updates")
        vCheck_mBox.setText(message)
        if downloadPath:
            # downloadBtn = vCheck_mBox.addButton(QtWidgets.QPushButton('Download'), QtWidgets.QMessageBox.HelpRole)
            # whatsNewBtn = vCheck_mBox.addButton(QtWidgets.QPushButton('Whats new'), QtWidgets.QMessageBox.HelpRole)
            # cancelBtn = vCheck_mBox.addButton(QtWidgets.QPushButton('Cancel'), QtWidgets.QMessageBox.RejectRole)

            vCheck_mBox.setStandardButtons(QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Help | QtWidgets.QMessageBox.Cancel)
            # vCheck_mBox.button(QtWidgets.QMessageBox.Cancel).setMinimumSize(QtCore.QSize(100, 30))
            # vCheck_mBox.button(QtWidgets.QMessageBox.Save).setMinimumSize(QtCore.QSize(100, 30))
            # vCheck_mBox.button(QtWidgets.QMessageBox.Help).setMinimumSize(QtCore.QSize(100, 30))

            buttonS = vCheck_mBox.button(QtWidgets.QMessageBox.Save)
            buttonS.setText('Download')
            buttonS = vCheck_mBox.button(QtWidgets.QMessageBox.Help)
            buttonS.setText('Whats New?')

            # ret = vCheck_mBox.exec_()
            # print ret
            # if ret == 0:
            #     webbrowser.open_new(downloadPath)
            # elif ret == 1:
            #     webbrowser.open_new(whatsNewPath)
        else:
            vCheck_mBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
            # vCheck_mBox.button(QtWidgets.QMessageBox.Ok).setMinimumSize(QtCore.QSize(100, 30))

        ret = vCheck_mBox.exec_()

        if ret == QtWidgets.QMessageBox.Save:
            webbrowser.open_new(downloadPath)
        elif ret == QtWidgets.QMessageBox.Help:
            webbrowser.open_new(whatsNewPath)

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
        self.msg.button(QtWidgets.QMessageBox.Ok).setFixedHeight(30)
        self.msg.button(QtWidgets.QMessageBox.Ok).setFixedWidth(100)
        self.msg.show()

    def queryPop(self, type, textTitle="Question", textHeader="", textInfo="", password=""):
        # if type == "password":
        #     if password != "":
        #         passw, ok= QtWidgets.QInputDialog.getText(self, textTitle,
        #                                                   textInfo, QtWidgets.QLineEdit.Password, parent=self)
        #         if ok:
        #             if passw == password:
        #                 return True
        #             else:
        #                 self.infoPop(textTitle="Incorrect Passsword", textHeader="Incorrect Password", type="C")
        #                 return False
        #         else:
        #             return False
        #     else:
        #         return -1

        if type == "yesNoCancel":

            q = QtWidgets.QMessageBox(parent=self)
            q.setIcon(QtWidgets.QMessageBox.Question)
            q.setText(textHeader)
            q.setInformativeText(textInfo)
            q.setWindowTitle(textTitle)
            q.setStandardButtons(
                QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)

            q.button(QtWidgets.QMessageBox.Save).setFixedHeight(30)
            q.button(QtWidgets.QMessageBox.Save).setFixedWidth(100)
            q.button(QtWidgets.QMessageBox.No).setFixedHeight(30)
            q.button(QtWidgets.QMessageBox.No).setFixedWidth(100)
            q.button(QtWidgets.QMessageBox.Cancel).setFixedHeight(30)
            q.button(QtWidgets.QMessageBox.Cancel).setFixedWidth(100)
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
            q.button(QtWidgets.QMessageBox.Ok).setFixedHeight(30)
            q.button(QtWidgets.QMessageBox.Ok).setFixedWidth(100)
            q.button(QtWidgets.QMessageBox.Cancel).setFixedHeight(30)
            q.button(QtWidgets.QMessageBox.Cancel).setFixedWidth(100)
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
            q.button(QtWidgets.QMessageBox.Yes).setFixedHeight(30)
            q.button(QtWidgets.QMessageBox.Yes).setFixedWidth(100)
            q.button(QtWidgets.QMessageBox.No).setFixedHeight(30)
            q.button(QtWidgets.QMessageBox.No).setFixedWidth(100)
            ret = q.exec_()
            if ret == QtWidgets.QMessageBox.Yes:
                return "yes"
            elif ret == QtWidgets.QMessageBox.No:
                return "no"

class ImageWidget(QtWidgets.QLabel):
    """Custom class for thumbnail section. Keeps the aspect ratio when resized."""
    def __init__(self, parent=None):
        super(ImageWidget, self).__init__()
        self.aspectRatio = 1.78
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)

    def resizeEvent(self, r):
        h = self.width()
        self.setMinimumHeight(h/self.aspectRatio)
        self.setMaximumHeight(h/self.aspectRatio)

class DropListWidget(QtWidgets.QListWidget):
    """Custom List Widget which accepts drops"""
    # dropped = Qt.QtCore.Signal(str)
    # dropped = QtCore.Signal(str)
    # PyInstaller and Standalone version compatibility
    if FORCE_QT4:
        dropped = QtCore.pyqtSignal(str)
    else:
        dropped = QtCore.Signal(str)

    def __init__(self, type, parent=None):
        super(DropListWidget, self).__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
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

class Browse(object):
    """Browsing class with history"""
    def __init__(self):
        super(Browse, self).__init__()
        self.history = []
        self.index = 0
        self.undoCount = 10

    def forward(self):
        if not self.isForwardLocked():
            self.index += 1
        else:
            pass
    def backward(self):
        if not self.isBackwardLocked():
            self.index -= 1
        else:
            pass
    def addData(self, data):
        # if the incoming data is identical with the current, do nothing
        try:
            currentData = self.history[self.index]
            if data == currentData:
                return
        except IndexError:
            pass
        # delete history after index
        del self.history[self.index+1:]
        self.history.append(data)
        if len(self.history) > self.undoCount:
            self.history.pop(0)
        self.index = len(self.history)-1
        # the new data writes the history, so there is no future
        self.forwardLimit = True
        # but there is past
        self.backwardLimit = False
    def getData(self, index=None):
        if index:
            return self.history[index]
        else:
            return self.history[self.index]
    def isBackwardLocked(self):
        return self.index == 0
    def isForwardLocked(self):
        return self.index == (len(self.history)-1)

class Settings(dict):
    def __init__(self):
        super(Settings, self).__init__()

    def isChanged(self):
        """Checks for differences between old and new settings"""
        for key in self.listNames():
            if self[key]["newSettings"] != self[key]["oldSettings"]:
                return True
        return False

    def apply(self):
        """Equals original settings to the new settings"""
        applyList=[]
        for key in self.listNames():
            newSettings = self[key]["newSettings"]
            oldSettings = self[key]["oldSettings"]
            if newSettings != oldSettings:
                self[key]["oldSettings"] = deepcopy(newSettings)
                applyInfo = {"data": newSettings,
                               "filepath": self[key]["databaseFilePath"]}
                applyList.append(applyInfo)
        return applyList

    def add(self, name, data, filePath):
        """Adds a new setting database"""
        # self[name] = {"oldSettings": type(data)(data),
        #               "newSettings": type(data)(data),
        #               "databaseFilePath": filePath}
        self[name] = {"oldSettings": deepcopy(data),
                      "newSettings": deepcopy(data),
                      "databaseFilePath": filePath}
        return True


    def listNames(self):
        """Returns all setting names"""
        return self.keys()

    def getOriginal(self, settingName):
        return self[settingName]["oldSettings"]

    def setOriginal(self, settingName, data):
        self[settingName]["oldSettings"] = deepcopy(data)

    def get(self, settingName):
        return self[settingName]["newSettings"]

    def set(self, settingName, data):
        self[settingName]["newSettings"] = deepcopy(data)
