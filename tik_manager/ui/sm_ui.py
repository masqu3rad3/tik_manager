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
import re
import datetime

from tik_manager.core import project_materials
from tik_manager.core import asset_library

import tik_manager.core.compatibility as compat
from tik_manager.core.environment import get_environment_data, getMainWindow
from tik_manager.ui.widgets import ImageWidget, DropListWidget
from tik_manager.ui.settings import SettingsUI
from tik_manager.ui.feedback import Feedback

ENV_DATA = get_environment_data()

# import Qt module depending on the DCC
# The reason not to use directly is that pyinstaller is not working well with Qt.py
if ENV_DATA["dcc"] == "standalone" or ENV_DATA["dcc"] == "photoshop":
    from PyQt5 import QtWidgets, QtCore, QtGui
else:
    from tik_manager.ui.Qt import QtWidgets, QtCore, QtGui

import webbrowser

## DO NOT REMOVE THIS:
import tik_manager.iconsSource as icons
## DO NOT REMOVE THIS:

import pprint

from tik_manager.core import image_viewer

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
logger.setLevel(logging.DEBUG)

class MainUI(QtWidgets.QMainWindow, SettingsUI, Feedback):
    """Main UI Class for Tik Scene Manager"""

    def __init__(self, callback=None):
        self.isCallback = callback
        self.windowName = ENV_DATA["main_ui_title"]
        for entry in QtWidgets.QApplication.allWidgets():
            try:
                if entry.objectName() == self.windowName:
                    entry.close()
            except (AttributeError, TypeError):
                pass
        self.parent = getMainWindow()
        super(MainUI, self).__init__(parent=self.parent)

        # Set Stylesheet

        dirname = os.path.dirname(os.path.abspath(__file__))
        stylesheetFile = os.path.join(dirname, "../CSS", "tikManager.qss")

        try:
            with open(stylesheetFile, "r") as fh:
                self.setStyleSheet(fh.read())
        except IOError:
            pass

        ## fonts:

        self.iconFont = QtGui.QFont("Segoe UI Symbol", 12, QtGui.QFont.Bold)
        self.headerAFont = QtGui.QFont("Segoe UI Symbol", 14, QtGui.QFont.Bold)
        self.headerBFont = QtGui.QFont("Segoe UI Symbol", 10, QtGui.QFont.Bold)
        self.displayFont = QtGui.QFont("Segoe UI Symbol", 8, QtGui.QFont.Bold)
        self.infoFont = QtGui.QFont("", 8, QtGui.QFont.Helvetica)

        self.superUser = False

    def buildUI(self):
        self.setObjectName(self.windowName)
        self.resize(680, 620)
        self.setWindowTitle(self.windowName)

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.setCentralWidget(self.centralwidget)

        mainLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        try:
            mainLayout.setMargin(0)
        except AttributeError:
            pass

        mainLayout.setContentsMargins(10, 10, 10, 10)

        # ----------
        # HEADER BAR
        # ----------
        margin = 5
        self.colorBar = QtWidgets.QLabel()
        headerColor = self.manager.getColorCoding(self.manager.dcc)
        self.colorBar.setStyleSheet("background-color: %s;" % headerColor)
        mainLayout.addWidget(self.colorBar)
        # pyside does not have setMargin attribute
        try:
            self.colorBar.setMargin(0)
        except AttributeError:
            pass
        self.colorBar.setIndent(0)
        self.colorBar.setMaximumHeight(1)

        colorWidget = QtWidgets.QWidget(self.centralwidget)
        colorWidget.setProperty("header", True)
        headerLayout = QtWidgets.QHBoxLayout(colorWidget)
        headerLayout.setSpacing(0)
        try:
            headerLayout.setMargin(0)
        except AttributeError:
            pass

        tikIcon_label = QtWidgets.QLabel(self.centralwidget)
        tikIcon_label.setProperty("header", True)
        try:
            tikIcon_label.setMargin(margin)
        except AttributeError:
            pass
        tikIcon_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        tikIcon_label.setScaledContents(False)
        headerBitmap = QtGui.QPixmap(":/icons/CSS/rc/tmMain.png")

        tikIcon_label.setPixmap(headerBitmap)

        headerLayout.addWidget(tikIcon_label)

        self.baseScene_label = QtWidgets.QLabel(self.centralwidget)
        self.baseScene_label.setProperty("header", True)
        try:
            self.baseScene_label.setMargin(margin)
        except AttributeError:
            pass
        self.baseScene_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        self.baseScene_label.setFont(self.displayFont)
        headerLayout.addWidget(self.baseScene_label)

        self.managerIcon_label = QtWidgets.QLabel(self.centralwidget)
        self.managerIcon_label.setProperty("header", True)
        try:
            self.managerIcon_label.setMargin(margin)
        except AttributeError:
            pass
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

        self.saveBaseScene_pushButton = QtWidgets.QPushButton(self.centralwidget, text="Save Base Scene",
                                                              font=self.iconFont)
        self.saveBaseScene_pushButton.setProperty("menuButton", True)
        self.saveBaseScene_pushButton.setToolTip("Saves the currently open scene as a Base Scene ")
        self.main_horizontalLayout.addWidget(self.saveBaseScene_pushButton)

        self.saveVersion_pushButton = QtWidgets.QPushButton(self.centralwidget, text="Save As Version",
                                                            font=self.iconFont)
        self.saveVersion_pushButton.setProperty("menuButton", True)
        self.saveVersion_pushButton.setToolTip("Saves a new version from the currently open Base Scene ")

        self.main_horizontalLayout.addWidget(self.saveVersion_pushButton)

        self.export_pushButton = QtWidgets.QPushButton(self.centralwidget, text="Transfer Central", font=self.iconFont)
        self.export_pushButton.setProperty("menuButton", True)
        self.export_pushButton.setToolTip("Export/Import Geometry formats")
        self.main_horizontalLayout.addWidget(self.export_pushButton)

        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.main_horizontalLayout.addItem(spacerItem)

        self.multi_reference_cb = QtWidgets.QComboBox(self.centralwidget)
        self.multi_reference_cb.addItems(["1x","2x","3x","4x","5x","6x","7x","8x","9x","10x"])
        self.multi_reference_cb.setProperty("menuButton", True)
        self.main_horizontalLayout.addWidget(self.multi_reference_cb)
        self.loadScene_pushButton = QtWidgets.QPushButton(self.centralwidget, text="Load Scene", font=self.iconFont)
        self.loadScene_pushButton.setProperty("menuButton", True)
        self.loadScene_pushButton.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.loadScene_pushButton.setToolTip("Loads or Reference the selected Base Scene depending on the mode")
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

        self.subProject_comboBox = QtWidgets.QComboBox(self.centralwidget, minimumSize=QtCore.QSize(150, 30),
                                                       maximumSize=QtCore.QSize(16777215, 30))
        self.subProject_comboBox.setToolTip("Changes sub-project level")
        self.r2_gridLayout.addWidget(self.subProject_comboBox, 0, 3, 1, 1)

        self.addSubProject_pushButton = QtWidgets.QPushButton(self.centralwidget, minimumSize=QtCore.QSize(30, 30),
                                                              font=self.iconFont)
        self.addSubProject_pushButton.setToolTip("Adds a new sub-project level")
        self.addSubProject_pushButton.setIcon(QtGui.QIcon(":/icons/CSS/rc/plus.png"))

        self.r2_gridLayout.addWidget(self.addSubProject_pushButton, 0, 4, 1, 1)

        self.user_label = QtWidgets.QLabel(self.centralwidget, text="User:", alignment=(
                    QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter))
        self.user_label.setToolTip("Changes the current user")
        self.r2_gridLayout.addWidget(self.user_label, 0, 5, 1, 1)

        self.user_comboBox = QtWidgets.QComboBox(self.centralwidget, minimumSize=QtCore.QSize(130, 30),
                                                 maximumSize=QtCore.QSize(16777215, 30))
        self.user_comboBox.setToolTip("Changes the current user")
        self.r2_gridLayout.addWidget(self.user_comboBox, 0, 6, 1, 1)

        self.main_gridLayout.addLayout(self.r2_gridLayout, 1, 0, 1, 1)
        self.r1_gridLayout = QtWidgets.QGridLayout()

        self.project_label = QtWidgets.QLabel(self.centralwidget, text="Project:", alignment=(
                    QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter))
        self.r1_gridLayout.addWidget(self.project_label, 1, 0, 1, 1)

        self.project_lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.r1_gridLayout.addWidget(self.project_lineEdit, 1, 1, 1, 1)

        self.setProject_pushButton = QtWidgets.QPushButton(self.centralwidget, text="SET")
        self.setProject_pushButton.setToolTip("Opens the Set Project window")

        self.setProject_pushButton.setToolTip("Set Recent Project")
        self.setRecent_pushButton = QtWidgets.QPushButton(self.centralwidget, text="R")

        pLayout = QtWidgets.QHBoxLayout()
        pLayout.addWidget(self.setProject_pushButton)
        pLayout.addWidget(self.setRecent_pushButton)

        self.r1_gridLayout.addLayout(pLayout, 1, 2, 1, 1)

        self.main_gridLayout.addLayout(self.r1_gridLayout, 0, 0, 1, 1)

        self.category_tabWidget = QtWidgets.QTabWidget(self.centralwidget, maximumSize=QtCore.QSize(16777215, 23),
                                                       tabPosition=QtWidgets.QTabWidget.North,
                                                       elideMode=QtCore.Qt.ElideNone, usesScrollButtons=True)

        self.main_gridLayout.addWidget(self.category_tabWidget, 2, 0, 1, 1)

        self.splitter = QtWidgets.QSplitter(self.centralwidget, orientation=QtCore.Qt.Horizontal)

        left_frame = QtWidgets.QFrame(self.splitter, frameShape=QtWidgets.QFrame.StyledPanel,
                                      frameShadow=QtWidgets.QFrame.Raised)
        scenes_vLay = QtWidgets.QVBoxLayout(left_frame)
        scenes_vLay.setContentsMargins(0, 0, 0, 0)
        self.scenes_listWidget = QtWidgets.QTreeWidget(sortingEnabled=True, rootIsDecorated=False)
        self.scenes_listWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        scenes_vLay.addWidget(self.scenes_listWidget)

        self.scene_filter_lineEdit = QtWidgets.QLineEdit()
        self.scene_filter_lineEdit.setFont(self.iconFont)
        self.scene_filter_lineEdit.setPlaceholderText("🔍")
        scenes_vLay.addWidget(self.scene_filter_lineEdit)


        self.frame = QtWidgets.QFrame(self.splitter, frameShape=QtWidgets.QFrame.StyledPanel,
                                      frameShadow=QtWidgets.QFrame.Raised)

        self.gridLayout_6 = QtWidgets.QGridLayout(self.frame)
        self.gridLayout_6.setContentsMargins(-1, -1, 0, 0)

        self.verticalLayout = QtWidgets.QVBoxLayout()

        self.notes_label = QtWidgets.QLabel(self.frame, text="Version Notes:", layoutDirection=QtCore.Qt.LeftToRight,
                                            alignment=(
                                                        QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter))
        self.verticalLayout.addWidget(self.notes_label)

        self.notes_textEdit = QtWidgets.QTextEdit(self.frame, readOnly=True)
        self.verticalLayout.addWidget(self.notes_textEdit)

        self.E_tPixmap = QtGui.QPixmap(":/icons/CSS/rc/empty_thumbnail.png")
        self.thumbnail_label = ImageWidget(self.frame)
        self.thumbnail_label.setToolTip("Right Click for replace options")
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

        self.showPreview_pushButton = QtWidgets.QPushButton(self.frame, text="Show Preview",
                                                            minimumSize=QtCore.QSize(100, 30),
                                                            maximumSize=QtCore.QSize(150, 30))
        self.showPreview_pushButton.setToolTip("Shows selected versions preview file(s)")
        self.gridLayout_7.addWidget(self.showPreview_pushButton, 0, 3, 1, 1)

        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setSpacing(1)

        self.version_label = QtWidgets.QLabel(self.frame, text="Version:", minimumSize=QtCore.QSize(60, 30),
                                              maximumSize=QtCore.QSize(60, 30), frameShape=QtWidgets.QFrame.Box,
                                              alignment=QtCore.Qt.AlignCenter)
        self.horizontalLayout_4.addWidget(self.version_label)

        self.version_comboBox = QtWidgets.QComboBox(self.frame, minimumSize=QtCore.QSize(60, 30),
                                                    maximumSize=QtCore.QSize(100, 30))
        self.version_comboBox.setToolTip("Changes between versions of thw selected Base Scene")
        self.horizontalLayout_4.addWidget(self.version_comboBox)

        self.gridLayout_7.addLayout(self.horizontalLayout_4, 0, 0, 1, 1)

        self.makeReference_pushButton = QtWidgets.QPushButton(self.frame, text="Make Reference",
                                                              minimumSize=QtCore.QSize(100, 30),
                                                              maximumSize=QtCore.QSize(300, 30))
        self.makeReference_pushButton.setToolTip("Promotes the selected Base Scene version as Reference")
        self.gridLayout_7.addWidget(self.makeReference_pushButton, 1, 0, 1, 1)

        self.addNote_pushButton = QtWidgets.QPushButton(self.frame, text="Add Note", minimumSize=QtCore.QSize(100, 30),
                                                        maximumSize=QtCore.QSize(150, 30))
        self.addNote_pushButton.setToolTip("Opens the Add Version notes dialog")
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

        settings_fm = QtWidgets.QAction(QtGui.QIcon(":/icons/CSS/rc/settings.png"), "&Settings", self)

        deleteFile_fm = QtWidgets.QAction(QtGui.QIcon(":/icons/CSS/rc/delete.png"), "&Delete Selected Base Scene", self)
        deleteReference_fm = QtWidgets.QAction(QtGui.QIcon(":/icons/CSS/rc/delete.png"),
                                               "&Delete Reference of Selected Scene", self)
        projectReport_fm = QtWidgets.QAction("&Project Report", self)
        projectReport_fm.setEnabled(True)
        checkReferences_fm = QtWidgets.QAction("&Check References", self)

        # save
        self.fileMenu.addAction(createProject_fm)
        self.fileMenu.addAction(self.saveVersion_fm)
        self.fileMenu.addAction(self.saveBaseScene_fm)
        self.fileMenu.addSeparator()

        # load
        self.fileMenu.addAction(loadReferenceScene_fm)
        self.fileMenu.addSeparator()

        # settings
        self.fileMenu.addAction(settings_fm)
        self.fileMenu.addSeparator()

        # delete
        self.fileMenu.addAction(deleteFile_fm)
        self.fileMenu.addAction(deleteReference_fm)

        self.fileMenu.addSeparator()

        # misc
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

        # self.baseSceneFromReference = QtWidgets.QAction('Create Base Scene from', self)
        self.baseSceneFromReference = self.popMenu_scenes.addMenu('Create Base Scene to:')
        self.popMenu_scenes.addSeparator()


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

        self.popMenu_scenes.addSeparator()
        self.scenes_rcItem_6 = QtWidgets.QAction('Ingest Current Scene As the New Version', self)
        self.popMenu_scenes.addAction(self.scenes_rcItem_6)
        self.scenes_rcItem_6.triggered.connect(lambda: self.rcAction_scenes("insertTo"))

        # Thumbnail Right Click Menu
        self.thumbnail_label.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.thumbnail_label.customContextMenuRequested.connect(self.onContextMenu_thumbnail)
        self.popMenu_thumbnail = QtWidgets.QMenu()

        if ENV_DATA["dcc"] != "standalone":
            rcAction_thumb_0 = QtWidgets.QAction('Replace with current view', self)
            self.popMenu_thumbnail.addAction(rcAction_thumb_0)
            rcAction_thumb_0.triggered.connect(lambda: self.rcAction_thumb("currentView"))

        rcAction_thumb_1 = QtWidgets.QAction('Replace with external file', self)
        self.popMenu_thumbnail.addAction(rcAction_thumb_1)
        rcAction_thumb_1.triggered.connect(lambda: self.rcAction_thumb("file"))

        # SHORTCUTS
        # ---------

        # PyInstaller and Standalone version compatibility

        shortcutRefresh = QtWidgets.QShortcut(QtGui.QKeySequence("F5"), self, self.refresh)

        # SIGNAL CONNECTIONS
        # ------------------

        createProject_fm.triggered.connect(self.createProjectUI)

        settings_fm.triggered.connect(self.settingsUI)

        deleteFile_fm.triggered.connect(self.onDeleteBaseScene)

        deleteReference_fm.triggered.connect(self.onDeleteReference)

        projectReport_fm.triggered.connect(self.onProjectReport)

        checkReferences_fm.triggered.connect(lambda: self.populateBaseScenes(deepCheck=True))

        imageViewer_mi.triggered.connect(self.onIviewer)
        projectMaterials_mi.triggered.connect(self.onPMaterials)
        self.assetLibrary_mi.triggered.connect(self.onAssetLibrary)
        self.createPB.triggered.connect(self.onCreatePreview)

        onlineHelp_mi.triggered.connect(
            lambda: webbrowser.open_new("http://www.ardakutlu.com/tik-manager-documentation/"))
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
        self.setRecent_pushButton.clicked.connect(self.rcAction_recent)

        self.saveBaseScene_pushButton.clicked.connect(self.saveBaseSceneDialog)
        self.saveBaseScene_fm.triggered.connect(self.saveBaseSceneDialog)

        self.saveVersion_pushButton.clicked.connect(self.saveAsVersionDialog)
        self.saveVersion_fm.triggered.connect(self.saveAsVersionDialog)

        self.scenes_listWidget.doubleClicked.connect(self.onLoadScene)
        self.loadScene_pushButton.clicked.connect(self.onLoadScene)

        self.addNote_pushButton.clicked.connect(self.addNoteDialog)

        self.export_pushButton.clicked.connect(self.transferCentralUI)

        self.scene_filter_lineEdit.textChanged.connect(self.populateBaseScenes)

    def createSubProjectUI(self):
        manager = self._getManager()
        # This method is NOT Software Specific
        newSub, ok = QtWidgets.QInputDialog.getText(self, "Create New Sub-Project", "Enter an unique Sub-Project name:")
        if ok:
            if self.manager.nameCheck(newSub):
                self.subProject_comboBox.clear()
                self.subProject_comboBox.addItems(manager.createSubproject(newSub))
                self.subProject_comboBox.setCurrentIndex(manager.currentSubIndex)
                self.populateBaseScenes()
            else:
                self.pop_info(title="Naming Error", text="Choose an unique name with latin characters without spaces", critical=True)


    def createProjectUI(self):

        ## ROAD MAP
        ## load tikConventions.json to a pConvention variable
        nameConventions = self.manager.loadNameConventions()
        pConvention = nameConventions["newProjectName"]

        ## get the used tokens
        allTokens = re.findall(r'<(.*?)\>', pConvention)
        exceptions = ["yy", "mm", "dd"]
        tokens = [t for t in allTokens if t not in exceptions]
        autoTokens = [t for t in allTokens if t in exceptions]

        ## assign values to <yy>, <mm> and <dd> tokens
        if len(autoTokens) > 0:
            today = datetime.date.today()
            for ta in autoTokens:
                if ta == "yy":
                    pConvention = pConvention.replace("<%s>" % ta, today.strftime("%y"))
                elif ta == "mm":
                    pConvention = pConvention.replace("<%s>" % ta, today.strftime("%m"))
                elif ta == "dd":
                    pConvention = pConvention.replace("<%s>" % ta, today.strftime("%d"))



        ## resolve the project name and update it with each character entered to the fields


        createProject_Dialog = QtWidgets.QDialog(parent=self, windowTitle="Create New Project")
        createProject_Dialog.resize(420, 220)

        masterLayout = QtWidgets.QVBoxLayout(createProject_Dialog)

        formLayout = QtWidgets.QFormLayout(spacing=15, labelAlignment=(
                    QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter))
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

        # token_le_list = []
        for t in tokens:
            token_vLay = QtWidgets.QVBoxLayout(spacing=6)
            token_lbl = QtWidgets.QLabel(text=t.capitalize().replace("name", " Name"), alignment=QtCore.Qt.AlignCenter)
            token_le = QtWidgets.QLineEdit(placeholderText="Mandatory Field")
            token_le.setObjectName(t)
            token_vLay.addWidget(token_lbl)
            token_vLay.addWidget(token_le)
            nameFields_hLay.addLayout(token_vLay)
            token_le.textChanged.connect(lambda: self._checkValidity(token_le.text(), cp_button, token_le))
            token_le.textEdited.connect(lambda: resolve())

        formLayout.addRow(nameFields_hLay)

        resolution_lbl = QtWidgets.QLabel(text="Resolution")
        resolution_hLay = QtWidgets.QHBoxLayout(spacing=4)
        resolutionX_spinBox = QtWidgets.QSpinBox(minimum=1, maximum=99999, value=1920, minimumWidth=(65),
                                                 maximumWidth=(65), buttonSymbols=QtWidgets.QAbstractSpinBox.NoButtons)
        resolutionY_spinBox = QtWidgets.QSpinBox(minimum=1, maximum=99999, value=1080, minimumWidth=(65),
                                                 maximumWidth=(65), buttonSymbols=QtWidgets.QAbstractSpinBox.NoButtons)
        resolution_presets_cb = QtWidgets.QComboBox()
        resolution_presets_cb.addItem("Custom Resolution")
        resolution_presets_cb.addItems(self.manager.resolutionPresets.keys())

        resolution_hLay.addWidget(resolutionX_spinBox)
        resolution_hLay.addWidget(resolutionY_spinBox)
        resolution_hLay.addWidget(resolution_presets_cb)

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

        def onPresetChange():
            resolutionX_spinBox.blockSignals(True)
            resolutionY_spinBox.blockSignals(True)
            if resolution_presets_cb.currentIndex() == 0:
                return
            key = resolution_presets_cb.currentText()
            resolutionX_spinBox.setValue(self.manager.resolutionPresets[key][0])
            resolutionY_spinBox.setValue(self.manager.resolutionPresets[key][1])
            resolutionX_spinBox.blockSignals(False)
            resolutionY_spinBox.blockSignals(False)

        def onValueChange():
            if resolution_presets_cb.currentIndex() == 0:
                return
            preset_res = (self.manager.resolutionPresets[resolution_presets_cb.currentText()])
            x_val = resolutionX_spinBox.value()
            y_val = resolutionY_spinBox.value()
            if x_val != preset_res[0] or y_val != preset_res[1]:
                resolution_presets_cb.setCurrentIndex(0)


        def resolve():
            resolvedProjectName = str(pConvention)
            for t in tokens:
                t_le = createProject_Dialog.findChild(QtWidgets.QLineEdit, t)
                if t_le.text() == "":
                    resolvedPath_lbl.setText("Fill the mandatory fields")
                    return
                else:
                    resolvedProjectName = resolvedProjectName.replace("<%s>" % t, t_le.text())
                    resolvedPath = os.path.join(compat.decode(projectRoot_le.text()), resolvedProjectName)
                    resolvedPath_lbl.setText(resolvedPath)
            return resolvedProjectName

        def onCreateNewProject():
            root = os.path.normpath(compat.encode(projectRoot_le.text()))
            if not self.manager.nameCheck(root, allowSpaces=True, directory=True):
                self.pop_info(title="Non-Ascii Character", text="Selected Project Root cannot be used", details="There are non-ascii characters in the selected path", critical=True)
                return
            if not os.path.isdir(root):
                self.pop_info(title="Path Error", text="Selected Project Root does not exist", critical=True)
                return

            projectName = resolve()
            if not projectName:
                self.pop_info(title="Missing Fields", text="Fill All Mandatory Fields")
            return
            resolvedPath = os.path.join(root, projectName)
            projectSettingsDB = {"Resolution": [resolutionX_spinBox.value(), resolutionY_spinBox.value()],
                                 "FPS": int(fps_combo.currentText())}

            pPath = self.manager.createNewProject(resolvedPath, settingsData=projectSettingsDB)

            if pPath:
                self.manager.setProject(pPath)
                self.manager.addToRecentProjects(pPath) #moved to the SmRoot

            self.initMainUI()
            createProject_Dialog.close()



        def browseProjectRoot():
            dlg = QtWidgets.QFileDialog()
            dlg.setFileMode(QtWidgets.QFileDialog.Directory)

            if dlg.exec_():
                # selectedroot = os.path.normpath(unicode(dlg.selectedFiles()[0])).encode("utf-8")
                selectedroot = os.path.normpath(compat.encode(dlg.selectedFiles()[0]))
                projectRoot_le.setText(selectedroot)
                resolve()

        resolution_presets_cb.currentIndexChanged.connect(onPresetChange)
        resolutionX_spinBox.valueChanged.connect(onValueChange)
        resolutionY_spinBox.valueChanged.connect(onValueChange)
        projectRoot_pb.clicked.connect(browseProjectRoot)
        createproject_buttonBox.accepted.connect(onCreateNewProject)
        createproject_buttonBox.rejected.connect(createProject_Dialog.reject)

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
        fakeButton = QtWidgets.QPushButton(self.setProject_Dialog)
        fakeButton.setVisible(False)
        fakeButton.setFocus()

        browse_pushButton = QtWidgets.QPushButton(self.setProject_Dialog, text="Browse")

        M1_horizontalLayout.addWidget(browse_pushButton)

        self.back_pushButton = QtWidgets.QPushButton(self.setProject_Dialog)
        self.back_pushButton.setIcon(QtGui.QIcon(":/icons/CSS/rc/arrow_left.png"))

        M1_horizontalLayout.addWidget(self.back_pushButton)

        self.forward_pushButton = QtWidgets.QPushButton(self.setProject_Dialog)
        self.forward_pushButton.setIcon(QtGui.QIcon(":/icons/CSS/rc/arrow_right.png"))

        M1_horizontalLayout.addWidget(self.forward_pushButton)

        up_pushButton = QtWidgets.QPushButton(self.setProject_Dialog)
        up_pushButton.setIcon(QtGui.QIcon(":/icons/CSS/rc/arrow_up.png"))
        up_pushButton.setShortcut((""))

        M1_horizontalLayout.addWidget(up_pushButton)

        recent_pushButton = QtWidgets.QPushButton(self.setProject_Dialog, text="Recent")
        M1_horizontalLayout.addWidget(recent_pushButton)

        gridLayout.addLayout(M1_horizontalLayout, 0, 0, 1, 1)

        M2_horizontalLayout = QtWidgets.QHBoxLayout()

        M2_splitter = QtWidgets.QSplitter(self.setProject_Dialog)
        M2_splitter.setHandleWidth(10)

        self.folders_treeView = QtWidgets.QTreeView(M2_splitter, minimumSize=QtCore.QSize(0, 0), dragEnabled=True,
                                                    dragDropMode=QtWidgets.QAbstractItemView.DragOnly,
                                                    selectionMode=QtWidgets.QAbstractItemView.SingleSelection,
                                                    itemsExpandable=False, rootIsDecorated=False,
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
        remove_pushButton.setIcon(QtGui.QIcon(":/icons/CSS/rc/minus.png"))

        M2_S2_horizontalLayout.addWidget(remove_pushButton)

        add_pushButton = QtWidgets.QPushButton(verticalLayoutWidget)
        add_pushButton.setIcon(QtGui.QIcon(":/icons/CSS/rc/plus.png"))

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
        # self.dirFilter_lineEdit.setPlaceholderText("🔍".decode("utf-8"))
        self.dirFilter_lineEdit.setPlaceholderText("🔍")

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

        M2_splitter.setStretchFactor(0, 1)

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

        self.folders_treeView.setColumnWidth(0, 400)
        self.folders_treeView.setColumnWidth(1, 0)
        self.folders_treeView.setColumnWidth(2, 0)

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
                # dir = unicode(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")).encode("utf-8")
                dir = compat.encode(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
                if dir:
                    self.projectsRoot = dir
                    self.browser.addData(self.projectsRoot)

                else:
                    return

            if command == "folder":
                index = self.folders_treeView.currentIndex()
                # self.projectsRoot = os.path.normpath(unicode(self.sourceModel.filePath(index)).encode("utf-8"))
                self.projectsRoot = os.path.normpath(compat.encode(self.sourceModel.filePath(index)))
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
            # normPath = os.path.normpath(str(path))
            normPath = os.path.normpath((path))
            path, fName = os.path.split(normPath)
            if [fName, normPath] in self.favList:
                return
            self.favorites_listWidget.addItem(fName)
            self.favList = self.manager.addToFavorites(fName, normPath)

        def favoritesActivated():
            # block the signal to prevent unwanted cycle
            self.folders_treeView.selectionModel().blockSignals(True)
            row = self.favorites_listWidget.currentRow()
            # self.spActiveProjectPath = self.favList[row][1]
            self.spActiveProjectPath = os.path.normpath(compat.encode(self.favList[row][1]))

            # clear the selection in folders view
            self.folders_treeView.setCurrentIndex(self.sourceModel.index(self.projectsRoot))
            self.folders_treeView.selectionModel().blockSignals(False)

        def foldersViewActivated():
            # block the signal to prevent unwanted cycle
            self.favorites_listWidget.blockSignals(True)
            index = self.folders_treeView.currentIndex()
            # self.spActiveProjectPath = os.path.normpath(unicode(self.sourceModel.filePath(index)).encode("utf-8"))
            self.spActiveProjectPath = os.path.normpath(compat.encode(self.sourceModel.filePath(index)))
            # clear the selection in favorites view
            self.favorites_listWidget.setCurrentRow(-1)
            self.favorites_listWidget.blockSignals(False)

        def recentMenu():
            recentList = reversed(self.manager.loadRecentProjects())

            zortMenu = QtWidgets.QMenu()
            for p in recentList:
                tempAction = QtWidgets.QAction(p, self)
                zortMenu.addAction(tempAction)
                ## Take note about the usage of lambda "item=z" makes it possible using the loop, ignore -> for discarding emitted value
                tempAction.triggered.connect(lambda ignore=p, item=p: setAndClose(custompath=(item)))
                # tempAction.triggered.connect(lambda item=z: manager.playPreview(str(item)))

            zortMenu.exec_((QtGui.QCursor.pos()))

        def setAndClose(custompath=None):
            self.setProject(custompath=custompath)

            self.setProject_Dialog.close()

        navigate("init")

        ## SIGNALS & SLOTS
        self.favorites_listWidget.dropped.connect(lambda path: onDragAndDrop(path))
        remove_pushButton.clicked.connect(onRemoveFavs)
        add_pushButton.clicked.connect(onAddFavs)

        self.favorites_listWidget.doubleClicked.connect(setAndClose)

        up_pushButton.clicked.connect(lambda: navigate("up"))
        self.back_pushButton.clicked.connect(lambda: navigate("back"))
        self.forward_pushButton.clicked.connect(lambda: navigate("forward"))
        browse_pushButton.clicked.connect(lambda: navigate("browse"))
        self.lookIn_lineEdit.returnPressed.connect(lambda: navigate("lineEnter"))
        # self.folders_treeView.doubleClicked.connect(lambda index: navigate("folder", index=index))
        recent_pushButton.clicked.connect(recentMenu)

        self.favorites_listWidget.currentItemChanged.connect(favoritesActivated)
        # self.folders_tableView.selectionModel().currentRowChanged.connect(foldersViewActivated)
        # There is a bug in here. If following two lines are run in a single line, a segmentation fault occurs and crashes 3ds max immediately
        selectionModel = self.folders_treeView.selectionModel()
        selectionModel.selectionChanged.connect(foldersViewActivated)

        self.favorites_listWidget.doubleClicked.connect(setAndClose)

        self.dirFilter_lineEdit.textChanged.connect(self._filterDirectories)

        # set_pushButton.clicked.connect(setProject)
        set_pushButton.clicked.connect(setAndClose)
        setproject_buttonBox.rejected.connect(self.setProject_Dialog.reject)

        self.setProject_Dialog.show()

    def transferCentralUI(self):

        try:
            self.transferCentral_Dialog.close()
        except AttributeError:
            pass

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
        try:
            headerLayout.setMargin(0)
        except AttributeError:
            pass

        tikIcon_label = QtWidgets.QLabel(self.centralwidget, alignment=(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter),
                                         scaledContents=False)
        tikIcon_label.setProperty("header", True)
        tikIcon_label.setMaximumWidth(125)
        try:
            tikIcon_label.setMargin(margin)
        except AttributeError:
            pass
        headerBitmap = QtGui.QPixmap(":/icons/CSS/rc/tmTransfer.png")
        tikIcon_label.setPixmap(headerBitmap)

        headerLayout.addWidget(tikIcon_label)

        resolvedPath_label = QtWidgets.QLabel()
        resolvedPath_label.setProperty("header", True)
        try:
            resolvedPath_label.setMargin(margin)
        except AttributeError:
            pass
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

        vrayProxy_checkBox = QtWidgets.QCheckBox(exportTab, text="VrayProxy", checked=False)
        format_horizontalLayout.addWidget(vrayProxy_checkBox)

        redShiftProxy_checkBox = QtWidgets.QCheckBox(exportTab, text="RedShiftProxy", checked=False)
        format_horizontalLayout.addWidget(redShiftProxy_checkBox)
        redShiftProxy_checkBox.setEnabled(False)

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

        frameStart_doubleSpinBox = QtWidgets.QDoubleSpinBox(exportTab, wrapping=False, frame=True,
                                                            buttonSymbols=QtWidgets.QAbstractSpinBox.NoButtons,
                                                            keyboardTracking=True)
        timeRange_horizontalLayout2.addWidget(frameStart_doubleSpinBox)
        spacerItem4 = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        timeRange_horizontalLayout2.addItem(spacerItem4)

        frameEnd_label = QtWidgets.QLabel(exportTab, text="End")
        timeRange_horizontalLayout2.addWidget(frameEnd_label)

        frameEnd_doubleSpinBox = QtWidgets.QDoubleSpinBox(exportTab, wrapping=False, frame=True,
                                                          buttonSymbols=QtWidgets.QAbstractSpinBox.NoButtons,
                                                          keyboardTracking=True, value=10.0)
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
            vrayProxy_topLevel = QtWidgets.QTreeWidgetItem(["VrayProxy"])
            vrayProxy_topLevel.setBackground(0, QtGui.QBrush(QtGui.QColor("green")))
            vrayProxy_topLevel.setForeground(0, QtGui.QBrush(QtGui.QColor("black")))

            transfers_treeWidget.setHeaderLabels(["Transfer Items", "Path"])
            transfers_treeWidget.addTopLevelItem(obj_topLevel)
            transfers_treeWidget.addTopLevelItem(fbx_topLevel)
            transfers_treeWidget.addTopLevelItem(alembic_topLevel)
            transfers_treeWidget.addTopLevelItem(vrayProxy_topLevel)

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
            for item in self.importDict["vrmesh"].items():
                treeItem = QtWidgets.QTreeWidgetItem([item[0], item[1]])
                treeItem.setForeground(0, QtGui.QBrush(QtGui.QColor("green")))
                vrayProxy_topLevel.addChild(treeItem)

        tabWidget.setCurrentIndex(0)

        def formatProof():
            timeRangeState = False
            if alembic_checkBox.isChecked() or fbx_checkBox.isChecked() or vrayProxy_checkBox.isChecked() or redShiftProxy_checkBox.isChecked():
                timeRangeState = True

            timeSlider_radioButton.setEnabled(timeRangeState)
            singleFrame_radioButton.setEnabled(timeRangeState)
            customRange_radioButton.setEnabled(timeRangeState)
            frameStart_label.setEnabled(timeRangeState)
            frameStart_doubleSpinBox.setEnabled(timeRangeState)
            frameEnd_label.setEnabled(timeRangeState)
            frameEnd_doubleSpinBox.setEnabled(timeRangeState)

            if customRange_radioButton.isChecked():
                frameStart_doubleSpinBox.setEnabled(True)
                frameEnd_doubleSpinBox.setEnabled(True)
                frameStart_label.setEnabled(True)
                frameEnd_label.setEnabled(True)
            else:
                frameStart_doubleSpinBox.setEnabled(False)
                frameEnd_doubleSpinBox.setEnabled(False)
                frameStart_label.setEnabled(False)
                frameEnd_label.setEnabled(False)

        formatProof()

        def resolveName():
            # resolve name
            if not sceneInfo:
                customName_lineEdit.setProperty("error", True)
                customName_lineEdit.setStyleSheet("")  # refresh
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
                    subProjectFolder = "" if sceneInfo["subProject"] == "None" else "{0}/".format(sceneInfo["subProject"])
                    sel = self.manager._getSelection()
                    if len(sel) > 1:
                        name = "{0}{1}/{1}_{2}_{3}sel".format(subProjectFolder, sceneInfo["shotName"], sceneInfo["version"], len(sel))
                    elif len(sel) == 1:
                        name = "{0}{1}/{1}_{2}_{3}".format(subProjectFolder, sceneInfo["shotName"], sceneInfo["version"], sel[0])
                    else:
                        customName_lineEdit.setProperty("error", True)
                        customName_lineEdit.setStyleSheet("")  # refresh
                        customName_lineEdit.setText("No Object Selected")
                        return
                else:
                    name = "{0}/{0}_{1}".format(sceneInfo["shotName"], sceneInfo["version"])
            # else:
            #     if selection_radioButton.isChecked():
            #         sel = self.manager._getSelection()
            #         if len(sel) > 1:
            #             name = "{0}/{0}_{1}_{2}sel".format(sceneInfo["shotName"], sceneInfo["version"], len(sel))
            #         elif len(sel) == 1:
            #             name = "{0}/{0}_{1}_{2}".format(sceneInfo["shotName"], sceneInfo["version"], sel[0])
            #         else:
            #             customName_lineEdit.setProperty("error", True)
            #             customName_lineEdit.setStyleSheet("")  # refresh
            #             customName_lineEdit.setText("No Object Selected")
            #             return
            #     else:
            #         name = "{0}/{0}_{1}".format(sceneInfo["shotName"], sceneInfo["version"])

            customName_lineEdit.setReadOnly(True)
            customName_lineEdit.setText(name)
            self._checkValidity(customName_lineEdit.text(), export_pushButton, customName_lineEdit, directory=True)

            return name

        resolveName()

        def executeExport():
            if not sceneInfo:
                self.pop_info(title="Base Scene Not Saved", text="Current scene is not a Base Scene.\nBefore Exporting items, scene must be saved as Base Scene")
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
            isVrayProxy = vrayProxy_checkBox.isChecked()
            isRedShiftProxy = redShiftProxy_checkBox.isChecked()
            res = self.manager.exportTransfers(name,
                                               isSelection=isSelection,
                                               isObj=isObj,
                                               isAlembic=isAlembic,
                                               isFbx=isFbx,
                                               isRedShiftProxy=isRedShiftProxy,
                                               isVrayProxy=isVrayProxy,
                                               timeRange=timeRange
                                               )
            self.pop_info(title="Transfers Exported", text="Transfers Exported under '_TRANSFER' folder")

        def executeImport():

            absPath = transfers_treeWidget.currentItem().text(1)
            if absPath:
                self.manager.importTransfers(absPath)

        def onContextMenu_transfers(point):
            if transfers_treeWidget.selectedItems()[0].text(1):  # if there is a path info on the widget item
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
        customName_lineEdit.textChanged.connect(
            lambda x: self._checkValidity(customName_lineEdit.text(), export_pushButton, customName_lineEdit,
                                          directory=True))
        obj_checkBox.toggled.connect(formatProof)
        alembic_checkBox.toggled.connect(formatProof)
        fbx_checkBox.toggled.connect(formatProof)
        vrayProxy_checkBox.toggled.connect(formatProof)
        redShiftProxy_checkBox.toggled.connect(formatProof)

        timeSlider_radioButton.toggled.connect(formatProof)
        singleFrame_radioButton.toggled.connect(formatProof)
        customRange_radioButton.toggled.connect(formatProof)

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
        # self.DirFilter = [(unicode("*%s*" % filterWord))]
        self.DirFilter = [(("*%s*" % filterWord))]
        self.sourceModel.setNameFilters(self.DirFilter)

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
        try:
            headerLayout.setMargin(0)
        except AttributeError:
            pass

        tikIcon_label = QtWidgets.QLabel(self.centralwidget)
        tikIcon_label.setProperty("header", True)
        tikIcon_label.setMaximumWidth(150)
        try:
            tikIcon_label.setMargin(margin)
        except AttributeError:
            pass
        tikIcon_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        tikIcon_label.setScaledContents(False)
        saveBaseHeaderBitmap = QtGui.QPixmap(":/icons/CSS/rc/tmBaseScene.png")
        tikIcon_label.setPixmap(saveBaseHeaderBitmap)

        headerLayout.addWidget(tikIcon_label)

        resolvedPath_label = QtWidgets.QLabel()
        resolvedPath_label.setProperty("header", True)
        try:
            resolvedPath_label.setMargin(margin)
        except AttributeError:
            pass
        resolvedPath_label.setIndent(12)

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

        subProject_label = QtWidgets.QLabel(verticalLayoutWidget_2)
        subProject_label.setFrameShape(QtWidgets.QFrame.StyledPanel)
        subProject_label.setText(("Sub-Project "))
        formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, subProject_label)

        subProject_comboBox = QtWidgets.QComboBox(verticalLayoutWidget_2)
        subProject_comboBox.setMinimumSize(QtCore.QSize(150, 20))
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

        if ENV_DATA["dcc"] == "Houdini" or \
                ENV_DATA["dcc"] == "Nuke" or \
                ENV_DATA["dcc"] == "Standalone":
            makeReference_checkBox.setVisible(False)

        formats_horizontalLayout = QtWidgets.QHBoxLayout()

        # If there are multiple formats create radio buttons for each
        radioButtonList = []
        for format in ENV_DATA["scene_formats"]:
            radioButton = QtWidgets.QRadioButton(verticalLayoutWidget_2)
            radioButton.setText(format)
            radioButton.setMinimumSize(50, 10)
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
                "subproject": self.manager.subProject,
                "date": ""  # date is unnecessary since it will be calculated in SmRoot->resolveSaveName
            }

            sceneName = self.manager.resolveSaveName(nameDict, 1)
            if self._checkValidity(lineEdit.text(), buttonBox, lineEdit):
                subP = subProject_comboBox.currentText()
                subProject = "" if subP == "None" else subP
                sceneFormat = ""
                for button in radioButtonList:
                    if button.isChecked():
                        sceneFormat = button.text()
                        break
                resolvedText = r"{0}\{1}\{2}\{3}\{4}.{5}".format(relScenesDir, category, subProject, name, sceneName, sceneFormat)
                resolvedText = resolvedText.replace("\\\\", "\\")
            else:
                resolvedText = ""
            resolvedPath_label.setText(resolvedText)

        def saveCommand():
            if notes_plainTextEdit.toPlainText() == "":
                self.pop_info(title="Cannot Continue", text="Notes MUST be filled ('dtgfd' is not a version note)")
                return
            checklist = self.manager.preSaveChecklist()
            for msg in checklist:
                q = self.pop_question(title="Checklist", text=msg, buttons=["yes", "no"])
                if q == "no":
                    return
                else:
                    self.manager.errorLogger(title="Disregarded warning", errorMessage=msg)
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

        buttonBox.accepted.connect(saveCommand)

        for rb in radioButtonList:
            rb.toggled.connect(getResolvedPath)

        buttonBox.rejected.connect(saveBaseScene_Dialog.reject)

        saveBaseScene_Dialog.show()
        
    def ingestAsVersionDialog(self):
        ingestV_Dialog = QtWidgets.QDialog(parent=self)
        ingestV_Dialog.setModal(True)
        ingestV_Dialog.resize(500, 220)
        ingestV_Dialog.setMinimumSize(QtCore.QSize(300, 220))
        ingestV_Dialog.setMaximumSize(QtCore.QSize(600, 600))
        ingestV_Dialog.setWindowTitle(("Ingest Scene To the Base Scene as Version"))

        ing_masterLayout = QtWidgets.QVBoxLayout(ingestV_Dialog)

        # ----------
        # HEADER BAR
        # ----------
        margin = 5
        colorWidget = QtWidgets.QWidget(ingestV_Dialog)
        headerLayout = QtWidgets.QHBoxLayout(colorWidget)
        headerLayout.setSpacing(0)
        try:
            headerLayout.setMargin(0)
        except AttributeError:
            pass

        tikIcon_label = QtWidgets.QLabel(self.centralwidget)
        tikIcon_label.setProperty("header", True)
        tikIcon_label.setMaximumWidth(80)
        try:
            tikIcon_label.setMargin(margin)
        except AttributeError:
            pass
        tikIcon_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        tikIcon_label.setScaledContents(False)

        tikIcon_label.setText("Ingesting As:")
        tikIcon_label.setStyleSheet("color: red")

        headerLayout.addWidget(tikIcon_label)

        resolvedPath_label = QtWidgets.QLabel()
        resolvedPath_label.setProperty("header", True)
        try:
            resolvedPath_label.setMargin(margin)
        except AttributeError:
            pass
        resolvedPath_label.setIndent(2)

        resolvedPath_label.setFont(QtGui.QFont("Times", 10, QtGui.QFont.Bold))
        resolvedPath_label.setWordWrap(True)

        headerLayout.addWidget(resolvedPath_label)

        ing_masterLayout.addWidget(colorWidget)
        # ----------
        # ----------

        right_verticalLayout = QtWidgets.QVBoxLayout()
        right_verticalLayout.setContentsMargins(-1, -1, 10, 10)
        right_verticalLayout.setSpacing(6)

        notes_label = QtWidgets.QLabel(ingestV_Dialog)
        notes_label.setText(("Notes"))
        right_verticalLayout.addWidget(notes_label)

        notes_plainTextEdit = QtWidgets.QPlainTextEdit(ingestV_Dialog)
        notes_plainTextEdit.setFrameShape(QtWidgets.QFrame.StyledPanel)
        right_verticalLayout.addWidget(notes_plainTextEdit)

        formats_horizontalLayout = QtWidgets.QHBoxLayout()
        right_verticalLayout.addLayout(formats_horizontalLayout)
        spacerItem = QtWidgets.QSpacerItem(80, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        formats_horizontalLayout.addItem(spacerItem)

        ext = os.path.splitext(self.manager.getSceneFile())[1][1:]
        radioButtonList = []
        for format in ENV_DATA["scene_formats"]:
            radioButton = QtWidgets.QRadioButton(ingestV_Dialog)
            radioButton.setText(format)
            formats_horizontalLayout.addWidget(radioButton)
            radioButtonList.append(radioButton)
            if format == ext:
                radioButton.setChecked(True)

        # hide radiobutton if only one format exists
        if len(radioButtonList) == 1:
            radioButtonList[0].setVisible(False)

        formats_horizontalLayout_2 = QtWidgets.QHBoxLayout()
        spacerItem1 = QtWidgets.QSpacerItem(80, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        formats_horizontalLayout_2.addItem(spacerItem1)

        makeReference_checkBox = QtWidgets.QCheckBox(ingestV_Dialog)
        makeReference_checkBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        makeReference_checkBox.setInputMethodHints(QtCore.Qt.ImhPreferUppercase)
        makeReference_checkBox.setText("Make Reference")
        makeReference_checkBox.setCheckable(True)

        if ENV_DATA["dcc"] == "Houdini" or \
                ENV_DATA["dcc"] == "Nuke" or \
                ENV_DATA["dcc"] == "Standalone":
            makeReference_checkBox.setVisible(False)

        formats_horizontalLayout_2.addWidget(makeReference_checkBox)
        right_verticalLayout.addLayout(formats_horizontalLayout_2)

        sv_buttonBox = QtWidgets.QDialogButtonBox(ingestV_Dialog)
        sv_buttonBox.setOrientation(QtCore.Qt.Horizontal)
        sv_buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        right_verticalLayout.addWidget(sv_buttonBox)
        ing_masterLayout.addLayout(right_verticalLayout)

        buttonS = sv_buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
        buttonS.setText('Save As Version')
        buttonS.setMinimumSize(QtCore.QSize(100, 30))
        buttonC = sv_buttonBox.button(QtWidgets.QDialogButtonBox.Cancel)
        buttonC.setText('Cancel')
        buttonC.setMinimumSize(QtCore.QSize(100, 30))

        def ingestAsVersionCommand():
            # TODO : ref
            if notes_plainTextEdit.toPlainText() == "":
                self.pop_info(title="Cannot Continue", text="Version Notes MUST be filled ('dtgfd' is not a version note)")
                return
            checklist = self.manager.preSaveChecklist()
            for msg in checklist:
                q = self.pop_question(title="Checklist", text=msg, buttons=["yes", "no"])
                if q == "no":
                    return
                else:
                    self.manager.errorLogger(title="Disregarded warning", errorMessage=msg)

            for button in radioButtonList:
                if button.isChecked():
                    sceneFormat = button.text()
                    break

            sceneInfo = self.manager.saveVersion(makeReference=makeReference_checkBox.checkState(),
                                                 versionNotes=notes_plainTextEdit.toPlainText(),
                                                 sceneFormat=sceneFormat, insertTo=True)

            if not sceneInfo == -1:
                self.statusBar().showMessage("Status | Version Saved => %s" % len(sceneInfo["Versions"]))
            self.manager.currentBaseSceneName = sceneInfo["Name"]
            self.manager.currentVersionIndex = len(sceneInfo["Versions"])

            self.populateBaseScenes()
            self.onBaseSceneChange()
            ingestV_Dialog.accept()

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
                "subproject": self.manager.subProject,
                "date": ""  # date is unnecessary since it will be calculated in SmRoot->resolveSaveName
            }
            sceneName = self.manager.resolveSaveName(nameDict, currentVersion)

            relSceneFile = os.path.join(jsonInfo["Path"], "{0}.{1}".format(sceneName, sceneFormat))
            resolvedPath_label.setText("\\%s" % relSceneFile)

        getResolvedPath()

        # SIGNALS
        # -------
        sv_buttonBox.accepted.connect(ingestAsVersionCommand)
        sv_buttonBox.rejected.connect(ingestV_Dialog.reject)

        for rb in radioButtonList:
            rb.toggled.connect(getResolvedPath)

        ingestV_Dialog.show()

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
        colorWidget = QtWidgets.QWidget(saveV_Dialog)
        headerLayout = QtWidgets.QHBoxLayout(colorWidget)
        headerLayout.setSpacing(0)
        try:
            headerLayout.setMargin(0)
        except AttributeError:
            pass

        tikIcon_label = QtWidgets.QLabel(self.centralwidget)
        # tikIcon_label.setFixedSize(115, 30)
        tikIcon_label.setProperty("header", True)
        tikIcon_label.setMaximumWidth(114)
        try:
            tikIcon_label.setMargin(margin)
        except AttributeError:
            pass
        tikIcon_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        tikIcon_label.setScaledContents(False)
        saveVersionHeaderBitmap = QtGui.QPixmap(":/icons/CSS/rc/tmVersion.png")
        tikIcon_label.setPixmap(saveVersionHeaderBitmap)

        headerLayout.addWidget(tikIcon_label)

        resolvedPath_label = QtWidgets.QLabel()
        resolvedPath_label.setProperty("header", True)
        try:
            resolvedPath_label.setMargin(margin)
        except AttributeError:
            pass
        resolvedPath_label.setIndent(2)

        resolvedPath_label.setFont(QtGui.QFont("Times", 7, QtGui.QFont.Bold))
        resolvedPath_label.setWordWrap(True)

        headerLayout.addWidget(resolvedPath_label)

        sv_masterLayout.addWidget(colorWidget)
        # ----------
        # ----------

        right_verticalLayout = QtWidgets.QVBoxLayout()
        right_verticalLayout.setContentsMargins(-1, -1, 10, 10)
        right_verticalLayout.setSpacing(6)

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
        for format in ENV_DATA["scene_formats"]:
            radioButton = QtWidgets.QRadioButton(saveV_Dialog)
            radioButton.setText(format)
            formats_horizontalLayout.addWidget(radioButton)
            radioButtonList.append(radioButton)
            if format == ext:
                radioButton.setChecked(True)

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

        if ENV_DATA["dcc"] == "Houdini" or \
                ENV_DATA["dcc"] == "Nuke" or \
                ENV_DATA["dcc"] == "Standalone":
            makeReference_checkBox.setVisible(False)

        formats_horizontalLayout_2.addWidget(makeReference_checkBox)
        right_verticalLayout.addLayout(formats_horizontalLayout_2)

        sv_buttonBox = QtWidgets.QDialogButtonBox(saveV_Dialog)
        sv_buttonBox.setOrientation(QtCore.Qt.Horizontal)
        sv_buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
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
            if notes_plainTextEdit.toPlainText() == "":
                self.pop_info(title="Cannot Continue", text="Version Notes MUST be filled ('dtgfd' is not a version note)")
                return
            checklist = self.manager.preSaveChecklist()
            for msg in checklist:
                q = self.pop_question(title="Checklist", text=msg, buttons=["yes", "no"])
                if q == "no":
                    return
                else:
                    self.manager.errorLogger(title="Disregarded warning", errorMessage=msg)

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


            self.populateBaseScenes()
            self.onBaseSceneChange()
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
                "subproject": self.manager.subProject,
                "date": ""  # date is unnecessary since it will be calculated in SmRoot->resolveSaveName
            }
            sceneName = self.manager.resolveSaveName(nameDict, currentVersion)

            relSceneFile = os.path.join(jsonInfo["Path"], "{0}.{1}".format(sceneName, sceneFormat))
            resolvedPath_label.setText("\\%s" % relSceneFile)

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
            self.manager.errorLogger(title="Misuse Error",
                                     errorMessage="A version tried to be saved without base scene")
            self.pop_info(title="Not a Base File", text="Current Scene is not a Base Scene. Only versions of Base Scenes can be saved", critical=True)

    def addNoteDialog(self):
        # This method IS Software Specific
        manager = self._getManager()

        row = self.scenes_listWidget.currentIndex().row()
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
        oldProject = manager.projectDir
        newProject = manager.getProjectDir()
        if not oldProject == newProject:
            self.initMainUI()
        else:
            return

    def initMainUI(self, newborn=False):
        """Initialization Method for MainUI. Needs to be overriden for Standalone Version"""

        extraColumnList = ["Name"] + self.manager.getExtraColumns()
        header = QtWidgets.QTreeWidgetItem(extraColumnList)
        self.scenes_listWidget.setHeaderItem(header)
        self.scenes_listWidget.setColumnWidth(0, 250)

        self.baseSceneFromReference.clear()
        for c in self.manager.getCategories():
            createBaseSceneInCategory_rcItem = QtWidgets.QAction(c, self)
            self.baseSceneFromReference.addAction(createBaseSceneInCategory_rcItem)
            createBaseSceneInCategory_rcItem.triggered.connect(lambda ignore=c, cat=c: self.onBaseSceneFromReference(category=cat))


        self.load_radioButton.setChecked(self.manager.currentMode)
        self.reference_radioButton.setChecked(not self.manager.currentMode)
        self.category_tabWidget.setCurrentIndex(self.manager.currentTabIndex)

        if not newborn:
            swName = self.manager.dcc
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
        self.onModeChange()

    def refresh(self):
        self.initMainUI()

        self.populateBaseScenes()

    def setProject(self, custompath=None):
        try:
            passPy2 = True if type(custompath) == unicode else False
        except:
            passPy2 = False
        if type(custompath) == str or passPy2:
            pPath = custompath
        else:
            if not self.spActiveProjectPath:
                self.pop_info(title="Cannot set project", text="Nothing Selected\nSelect the project from the list or bookmarks and hit 'set' again\nPress 'Ok' to continue")
                return
            pPath = os.path.normpath(compat.decode(self.spActiveProjectPath))

            # if not self.manager.nameCheck(self.spActiveProjectPath, allowSpaces=True, directory=True):
            if not self.manager.nameCheck(pPath, allowSpaces=True, directory=True):
                self.pop_info(title="Invalid Path", text="There are invalid (non-ascii) characters in the selected path", details="This Path cannot be used", critical=True)
                return
            if self.manager.currentPlatform == "Linux":
                pPath = "/%s" % pPath
            else:
                pPath = pPath

        self.manager.setProject(pPath)
        # recentData
        self.manager.addToRecentProjects(pPath)  # moved to the SmRoot

        self.onProjectChange()

    def rcAction_recent(self):
        recentList = reversed(self.manager.loadRecentProjects())

        zortMenu = QtWidgets.QMenu()
        for p in recentList:
            tempAction = QtWidgets.QAction(p, self)
            zortMenu.addAction(tempAction)
            ## Take note about the usage of lambda "item=z" makes it possible using the loop, ignore -> for discarding emitted value
            tempAction.triggered.connect(lambda ignore=p, item=p: self.setProject(custompath=(item)))

        zortMenu.exec_((QtGui.QCursor.pos()))

    def rcAction_scenes(self, command):
        # This method IS Software Specific
        manager = self._getManager()

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
            # use self.manager here in case there is no software database yet in the project
            self.manager.showInExplorer(self.manager.projectDir)

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

        if command == "insertTo":
            success = self.ingestAsVersionDialog()

        if command == "viewRender":
            imagePath = os.path.join(manager.projectDir, "images", manager.currentBaseSceneName)
            image_viewer.MainUI(manager.projectDir, relativePath=imagePath, recursive=True).show()

    def rcAction_thumb(self, command):
        # This method IS Software Specific
        manager = self._getManager()
        if command == "file":
            fname = \
            QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', manager.projectDir, "Image files (*.jpg *.gif)")[0]
            if not fname:  # if dialog is canceled
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

        row = self.scenes_listWidget.currentIndex().row()

        if row == -1:
            self.scenes_rcItem_0.setEnabled(False)
            self.scenes_rcItem_1.setEnabled(False)
            self.scenes_rcItem_2.setEnabled(False)
            self.scenes_rcItem_3.setEnabled(False)
            self.scenes_rcItem_4.setEnabled(False)
            self.scenes_rcItem_5.setEnabled(False)
            self.scenes_rcItem_6.setEnabled(False)
        else:
            self.scenes_rcItem_0.setEnabled(True)
            self.scenes_rcItem_1.setEnabled(os.path.isdir(manager.currentBaseScenePath))
            self.scenes_rcItem_2.setEnabled(os.path.isdir(manager.currentPreviewPath))
            # self.scenes_rcItem_2.setEnabled(True)
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
            env = ENV_DATA["dcc"]
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
        self.scene_filter_lineEdit.blockSignals(True)
        self.scene_filter_lineEdit.setText("")
        self.scene_filter_lineEdit.blockSignals(False)
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
            self.multi_reference_cb.setHidden(True)
            self.scenes_listWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
            self.scenes_rcItem_6.setVisible(True)
        else:
            self.loadScene_pushButton.setText("Reference Scene")
            self.scenes_listWidget.setProperty("reference", True)
            self.multi_reference_cb.setHidden(False)
            self.scenes_listWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
            self.scenes_rcItem_6.setVisible(False)


        self.scenes_listWidget.setStyleSheet("")  # refresh
        self.manager.currentMode = self.load_radioButton.isChecked()
        self.populateBaseScenes()

    def onBaseSceneChange(self):
        # This method IS Software Specific
        manager = self._getManager()
        self.version_comboBox.blockSignals(True)
        # clear version_combobox
        self.version_comboBox.clear()

        row = self.scenes_listWidget.currentIndex().row()
        if row == -1:
            manager.currentBaseSceneName = ""
        else:
            manager.currentBaseSceneName = str(self.scenes_listWidget.currentItem().text(0))

        self._vEnableDisable()
        # get versions and add it to the combobox
        versionData = manager.getVersions()
        for num in range(len(versionData)):
            self.version_comboBox.addItem("v{0}".format(str(num + 1).zfill(3)))
        self.version_comboBox.setCurrentIndex(manager.currentVersionIndex - 1)
        self.onVersionChange()

        self.version_comboBox.blockSignals(False)

    def onVersionChange(self):
        # This method IS Software Specific
        manager = self._getManager()

        if self.version_comboBox.currentIndex() is not -1:
            manager.currentVersionIndex = self.version_comboBox.currentIndex() + 1

        # clear Notes and verison combobox
        self.notes_textEdit.clear()

        # update notes
        self.notes_textEdit.setPlainText(manager.getNotes())

        self.tPixmap = QtGui.QPixmap(manager.getThumbnail())

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
        header = self.scenes_listWidget.headerItem()
        columnCount = header.columnCount()
        extraColumns = [header.text(x) for x in range(1, columnCount)]
        baseScenesDict = manager.getBaseScenesInCategory()
        filter_word = self.scene_filter_lineEdit.text()
        if filter_word:
            baseScenesDict = dict(filter(lambda elem: filter_word.lower() in elem[0].lower(), baseScenesDict.items()))

        if self.reference_radioButton.isChecked():
            for key in baseScenesDict:
                if manager.checkReference(baseScenesDict[key]) == 1:
                    timestamp = os.path.getmtime(baseScenesDict[key])
                    timestampFormatted = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                    item = QtWidgets.QTreeWidgetItem(self.scenes_listWidget, [key, str(timestampFormatted)])

        else:

            codeDict = {-1: QtGui.QColor(255, 0, 0, 255), 1: QtGui.QColor(0, 255, 0, 255),
                        0: QtGui.QColor(255, 255, 0, 255),
                        -2: QtGui.QColor(20, 20, 20, 255)}  # dictionary for color codes red, green, yellow

            for key in baseScenesDict:
                retCode = manager.checkReference(baseScenesDict[key],
                                                 deepCheck=deepCheck)  # returns -1, 0 or 1 for color ref
                color = codeDict[retCode]

                columnData = [key]
                if "Date" in extraColumns:
                    timestamp = os.path.getmtime(baseScenesDict[key])
                    timestampFormatted = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                    columnData.append(timestampFormatted)

                if "Ref. Version" in extraColumns or "Creator" in extraColumns or "Version Count" in extraColumns:
                    manager.getBaseScenesInCategory()
                    sInfo = manager.loadSceneInfo(asBaseScene=key)
                    if 'Ref. Version' in extraColumns:
                        refVersion = sInfo["ReferencedVersion"]
                        refVersion = "" if not refVersion else str(refVersion)
                        columnData.append(refVersion)
                    if "Creator" in extraColumns:
                        creator = sInfo["Creator"]
                        columnData.append(creator)
                    if "Version Count" in extraColumns:
                        vCount = str(len(sInfo["Versions"]))
                        columnData.append(vCount)

                item = QtWidgets.QTreeWidgetItem(self.scenes_listWidget, columnData)

                item.setForeground(0, color)

        self.scenes_listWidget.blockSignals(False)

    def onLoadScene(self):
        # This method IS Software Specific. BUT overriding it is better, so it is not selecting manager
        row = self.scenes_listWidget.currentIndex().row()
        if row == -1:
            return

        res, msg = self.manager.compareVersions()
        if res == -1:
            mismatch = self.pop_question(title="Version Mismatch", text=msg, buttons=["yes", "no"])
            if mismatch == "no":
                return
            else:
                self.manager.errorLogger(title="Disregarded warning", errorMessage=msg)

        if self.load_radioButton.isChecked():
            if self.manager.isSceneModified():
                q = self.pop_question(title="Save Changes", text="Scene Modified", details="Save Changes to", buttons=["yes", "no", "cancel"])
                if q == "yes":
                    self.manager.saveSimple()
                    self.manager.loadBaseScene(force=True)
                if q == "no":
                    self.manager.loadBaseScene(force=True)
                if q == "cancel":
                    pass


            else:  # if current scene saved and secure
                self.manager.loadBaseScene(force=True)
                self.manager.getOpenSceneInfo()
                self._initOpenScene()

            self.statusBar().showMessage("Status | Scene Loaded => %s" % self.manager.currentBaseSceneName)

        if self.reference_radioButton.isChecked():
            loop_count = self.multi_reference_cb.currentIndex() +1
            for nmb, tree_item in enumerate(self.scenes_listWidget.selectedItems()):
                self.manager.currentBaseSceneName = tree_item.text(0)
                for count in range(loop_count):
                    set_ranges = self.manager.getInheritRangePolicy() if count == 0 else "no"
                    self.manager.referenceBaseScene(set_ranges=set_ranges)
                    self.statusBar().showMessage("Status | Scene Referenced => %s" % self.manager.currentBaseSceneName)

    def onMakeReference(self):
        # This method IS Software Specific.

        manager = self._getManager()

        manager.makeReference()

        self.onVersionChange()
        self.statusBar().showMessage(
            "Status | Version {1} is the new reference of {0}".format(manager.currentBaseSceneName,
                                                                      manager.currentVersionIndex))
        self.populateBaseScenes()
        return

    def onShowPreview(self):
        # This method IS Software Specific.
        manager = self._getManager()

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
            zortMenu.exec_((QtGui.QCursor.pos()))

    def onDeleteBaseScene(self):
        # This method IS Software Specific.

        passw, ok = QtWidgets.QInputDialog.getText(self, "!!!DELETING BASE SCENE!!! %s\n\nAre you absolutely sure?",
                                                   "Enter Admin Password:", QtWidgets.QLineEdit.Password)

        if ok:
            if self.manager.checkPassword(passw):
                pass
            else:
                self.pop_info(title="Incorrect Password", text="Password is invalid")
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

        passw, ok = QtWidgets.QInputDialog.getText(self, "DELETING Reference File of %s\n\nAre you sure?",
                                                   "Enter Admin Password:", QtWidgets.QLineEdit.Password)

        if ok:
            if self.manager.checkPassword(passw):
                pass
            else:
                self.pop_info(title="Incorrect Password", text="Password is invalid")
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

    def onBaseSceneFromReference(self, category):
        row = self.scenes_listWidget.currentIndex().row()
        if row == -1:
            return

        ## Query: Prevent data loss, ask for unsaved changes
        if self.manager.isSceneModified():
            q = self.pop_question(title="Save Changes", text="Scene Modified", details="Save Changes to", buttons=["yes", "no", "cancel"])
            if q == "yes":
                self.manager.saveSimple()
            if q == "no":
                pass
            if q == "cancel":
                return

        ## open a new scene with project settings
        self.manager._new(fps=self.manager.getFPS())

        ## reference the selected base scene to the scene
        self.manager.referenceBaseScene()

        ## save it as a base scene to the specified category with proper naming
        name = self.manager.currentBaseSceneName
        subIndex = self.manager.currentSubIndex
        makeReference = False
        # notes = "Automatically referenced from %s/%s" %(self.manager.getCategories()[self.manager.currentTabIndex], name)
        notes = "Automatically referenced from %s/%s" %(self.manager.currentTabName, name)
        sceneFormat = os.path.splitext(self.manager._currentSceneInfo["ReferenceFile"])[1].replace(".", "")
        state = self.manager.saveBaseScene(str(category), str(name), subIndex, makeReference, notes, sceneFormat)
        if state[0] is not -1:
            self.manager.currentMode = 1
            self.manager.currentTabName = category
            self.initMainUI()
            self.statusBar().showMessage("Status | Scene Referenced => %s" % self.manager.currentBaseSceneName)

    def onProjectReport(self):
        manager = self._getManager()

        report = manager.getProjectReport()
        print(report)
        self.messageDialog = QtWidgets.QDialog()
        self.messageDialog.setWindowTitle("Project Progress Report")
        self.messageDialog.resize(800, 700)
        messageLayout = QtWidgets.QVBoxLayout(self.messageDialog)
        messageLayout.setContentsMargins(0, 0, 0, 0)
        report_te = QtWidgets.QTextEdit()
        report_te.setFont(QtGui.QFont("Courier New", 12, QtGui.QFont.Bold))
        report_te.setReadOnly(True)
        report_te.setText(report)
        messageLayout.addWidget(report_te)
        self.messageDialog.show()

    def onIviewer(self):
        # This method is NOT Software Specific.
        image_viewer.MainUI(self.manager.projectDir).show()

    def onPMaterials(self):
        pMat = project_materials.MainUI(projectPath=self.manager.projectDir)
        pMat.show()

    def onAssetLibrary(self):
        _ = asset_library.MainUI().show()

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
            self.baseScene_label.setProperty("baseScene", True)
        else:
            self.baseScene_label.setText("Current Scene is not a Base Scene")
            self.baseScene_label.setProperty("baseScene", False)
        self.baseScene_label.setStyleSheet("")

    def _checkValidity(self, text, button, lineEdit, allowSpaces=False, directory=False):
        if text == "":
            lineEdit.setProperty("error", False)
            lineEdit.setStyleSheet("")  # update
            return False
        if self.manager.nameCheck(text, allowSpaces=allowSpaces, directory=directory):
            lineEdit.setProperty("error", False)
            lineEdit.setStyleSheet("")  # update
            button.setEnabled(True)
            return True
        else:
            lineEdit.setProperty("error", True)
            lineEdit.setStyleSheet("")  # update
            button.setEnabled(False)
            return False

    def _vEnableDisable(self):
        manager = self._getManager()
        if self.load_radioButton.isChecked() and manager.currentBaseSceneName:
            self.version_comboBox.setEnabled(True)
            self.makeReference_pushButton.setEnabled(True)
            self.addNote_pushButton.setEnabled(True)
            self.version_label.setEnabled(True)
            self.baseSceneFromReference.menuAction().setVisible(False)
        else:
            self.version_comboBox.setEnabled(False)
            self.showPreview_pushButton.setEnabled(False)
            self.makeReference_pushButton.setEnabled(False)
            self.addNote_pushButton.setEnabled(False)
            self.version_label.setEnabled(False)
            self.baseSceneFromReference.menuAction().setVisible(True)

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
            vCheck_mBox.setStandardButtons(
                QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Help | QtWidgets.QMessageBox.Cancel)

            buttonS = vCheck_mBox.button(QtWidgets.QMessageBox.Save)
            buttonS.setText('Download')
            buttonS = vCheck_mBox.button(QtWidgets.QMessageBox.Help)
            buttonS.setText('Whats New?')

        else:
            vCheck_mBox.setStandardButtons(QtWidgets.QMessageBox.Ok)

        ret = vCheck_mBox.exec_()

        if ret == QtWidgets.QMessageBox.Save:
            webbrowser.open_new(downloadPath)
        elif ret == QtWidgets.QMessageBox.Help:
            webbrowser.open_new(whatsNewPath)

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
        del self.history[self.index + 1:]
        self.history.append(data)
        if len(self.history) > self.undoCount:
            self.history.pop(0)
        self.index = len(self.history) - 1
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
        return self.index == (len(self.history) - 1)

