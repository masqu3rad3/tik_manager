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
    if Qt.__binding__ == "PySide":
        from shiboken import wrapInstance
    elif Qt.__binding__.startswith('PyQt'):
        from sip import wrapinstance as wrapInstance
    else:
        from shiboken2 import wrapInstance
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
logger = logging.getLogger('smPhotoshop')
logger.setLevel(logging.WARNING)

def getMainWindow():
    """This function should be overriden"""
    if BoilerDict["Environment"] == "Maya":
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
        # TODO // Needs a main window getter for nuke
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
        # stylesheetFile = os.path.join(dirname, "CSS", "darkorange.stylesheet")
        stylesheetFile = os.path.join(dirname, "CSS", "tikManager.qss")

        with open(stylesheetFile, "r") as fh:
            self.setStyleSheet(fh.read())

        # super(MainUI, self).closeEvent(event)

    def buildUI(self):

        self.setObjectName(self.windowName)
        self.resize(680, 600)
        self.setWindowTitle(self.windowName)

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # self.buildUI()
        self.setCentralWidget(self.centralwidget)

        mainLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        try: mainLayout.setMargin(0)
        except AttributeError: pass

        mainLayout.setContentsMargins(10, 10, 10, 10)

        # ----------
        # HEADER BAR
        # ----------
        margin = 5
        # barColor = "background-color: rgb(80,80,80);"
        # barColor = "background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #565656, stop: 0.1 #525252, stop: 0.5 #4e4e4e, stop: 0.9 #4a4a4a, stop: 1 #464646);"
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
        colorWidget.setObjectName("header")
        headerLayout = QtWidgets.QHBoxLayout(colorWidget)
        headerLayout.setSpacing(0)
        try: headerLayout.setMargin(0)
        except AttributeError: pass

        tikIcon_label = QtWidgets.QLabel(self.centralwidget)
        tikIcon_label.setObjectName("header")
        try: tikIcon_label.setMargin(margin)
        except AttributeError: pass
        tikIcon_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        tikIcon_label.setScaledContents(False)
        if FORCE_QT4:
            # headerBitmap = QtWidgets.QPixmap(os.path.join(self.manager.getIconsDir(), "tmMain.png"))
            headerBitmap = QtWidgets.QPixmap(":/icons/CSS/rc/tmMain.png")
        else:
            # headerBitmap = QtGui.QPixmap(os.path.join(self.manager.getIconsDir(), "tmMain.png"))
            headerBitmap = QtGui.QPixmap(":/icons/CSS/rc/tmMain.png")
        tikIcon_label.setPixmap(headerBitmap)

        headerLayout.addWidget(tikIcon_label)

        self.baseScene_label = QtWidgets.QLabel(self.centralwidget)
        self.baseScene_label.setObjectName("header")
        try: self.baseScene_label.setMargin(margin)
        except AttributeError: pass
        self.baseScene_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        if FORCE_QT4:
            self.baseScene_label.setFont(QtWidgets.QFont("Times", 10, QtWidgets.QFont.Bold))
        else:
            self.baseScene_label.setFont(QtGui.QFont("Times", 10, QtGui.QFont.Bold))

        headerLayout.addWidget(self.baseScene_label)

        self.managerIcon_label = QtWidgets.QLabel(self.centralwidget)
        self.managerIcon_label.setObjectName("header")
        try: self.managerIcon_label.setMargin(margin)
        except AttributeError: pass
        self.managerIcon_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.managerIcon_label.setScaledContents(False)

        headerLayout.addWidget(self.managerIcon_label)

        # colorWidget.setStyleSheet(barColor)
        mainLayout.addWidget(colorWidget)
        # ----------
        # ----------


        # self.main_gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.main_gridLayout = QtWidgets.QGridLayout()
        mainLayout.addLayout(self.main_gridLayout)

        self.main_gridLayout.setObjectName(("main_gridLayout"))

        self.main_horizontalLayout = QtWidgets.QHBoxLayout()
        self.main_horizontalLayout.setContentsMargins(-1, -1, 0, -1)
        self.main_horizontalLayout.setSpacing(6)
        self.main_horizontalLayout.setStretch(0, 1)

        self.saveBaseScene_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.saveBaseScene_pushButton.setMinimumSize(QtCore.QSize(150, 45))
        self.saveBaseScene_pushButton.setMaximumSize(QtCore.QSize(150, 45))
        self.saveBaseScene_pushButton.setText(("Save Base Scene"))
        self.main_horizontalLayout.addWidget(self.saveBaseScene_pushButton)

        self.saveVersion_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.saveVersion_pushButton.setMinimumSize(QtCore.QSize(150, 45))
        self.saveVersion_pushButton.setMaximumSize(QtCore.QSize(150, 45))
        self.saveVersion_pushButton.setText(("Save As Version"))
        self.main_horizontalLayout.addWidget(self.saveVersion_pushButton)

        self.export_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.export_pushButton.setMinimumSize(QtCore.QSize(150, 45))
        self.export_pushButton.setMaximumSize(QtCore.QSize(150, 45))
        self.export_pushButton.setText(("Transfer Central"))
        self.main_horizontalLayout.addWidget(self.export_pushButton)
        # make it invisible
        self.export_pushButton.setVisible(True)

        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.main_horizontalLayout.addItem(spacerItem)

        self.loadScene_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.loadScene_pushButton.setMinimumSize(QtCore.QSize(150, 45))
        self.loadScene_pushButton.setMaximumSize(QtCore.QSize(150, 45))
        self.loadScene_pushButton.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.loadScene_pushButton.setText(("Load Scene"))
        self.main_horizontalLayout.addWidget(self.loadScene_pushButton)
        #
        self.main_gridLayout.addLayout(self.main_horizontalLayout, 4, 0, 1, 1)
        #
        self.r2_gridLayout = QtWidgets.QGridLayout()
        self.r2_gridLayout.setColumnStretch(1, 1)

        self.load_radioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.load_radioButton.setText(("Load Mode"))
        self.r2_gridLayout.addWidget(self.load_radioButton, 0, 0, 1, 1)

        self.reference_radioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.reference_radioButton.setText(("Reference Mode"))
        self.r2_gridLayout.addWidget(self.reference_radioButton, 0, 1, 1, 1)

        self.subProject_label = QtWidgets.QLabel(self.centralwidget)
        self.subProject_label.setText(("Sub-Project:"))
        self.subProject_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.r2_gridLayout.addWidget(self.subProject_label, 0, 2, 1, 1)

        self.subProject_comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.subProject_comboBox.setMinimumSize(QtCore.QSize(150, 30))
        self.subProject_comboBox.setMaximumSize(QtCore.QSize(16777215, 30))
        self.r2_gridLayout.addWidget(self.subProject_comboBox, 0, 3, 1, 1)

        self.addSubProject_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.addSubProject_pushButton.setMinimumSize(QtCore.QSize(30, 30))
        self.addSubProject_pushButton.setMaximumSize(QtCore.QSize(30, 30))
        self.addSubProject_pushButton.setText(("+"))
        self.r2_gridLayout.addWidget(self.addSubProject_pushButton, 0, 4, 1, 1)

        self.user_label = QtWidgets.QLabel(self.centralwidget)
        self.user_label.setText(("User:"))
        self.user_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.r2_gridLayout.addWidget(self.user_label, 0, 5, 1, 1)

        self.user_comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.user_comboBox.setMinimumSize(QtCore.QSize(130, 30))
        self.user_comboBox.setMaximumSize(QtCore.QSize(16777215, 30))
        self.r2_gridLayout.addWidget(self.user_comboBox, 0, 6, 1, 1)

        self.main_gridLayout.addLayout(self.r2_gridLayout, 1, 0, 1, 1)
        self.r1_gridLayout = QtWidgets.QGridLayout()

        # # ----------
        # # HEADER BAR
        # # ----------
        #
        # # self.headerBar_layout = QtWidgets.QHBoxLayout()
        # # self.r1_gridLayout.addLayout(self.headerBar_layout, 0, 0, 1, 1)
        #
        # tikIcon_label = QtWidgets.QLabel(self.centralwidget)
        # tikIcon_label.setAutoFillBackground(True)
        # tikIcon_label.setText("iconHere")
        # tikIcon_label.setFixedSize(115, 30)
        # headerBitmap = QtGui.QPixmap(os.path.join(self.manager.getIconsDir(), "tmMain.png"))
        #
        # tikIcon_label.setPixmap(headerBitmap)
        # # tikIcon_label.setScaledContents(False)
        #
        # # self.headerBar_layout.addWidget(self.tikIcon_label)
        # self.r1_gridLayout.addWidget(tikIcon_label, 0, 0, 1, 1)
        #
        # self.baseScene_label = QtWidgets.QLabel(self.centralwidget)
        # self.baseScene_label.setText((""))
        # self.baseScene_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        # self.baseScene_label.setMargin(15)
        # self.baseScene_label.setObjectName("headerBar")
        #
        #
        # # self.headerBar_layout.addWidget(self.tikIcon_label)
        # self.r1_gridLayout.addWidget(self.baseScene_label, 0, 1, 1, 1)
        #
        # self.managerIcon_label = QtWidgets.QLabel(self.centralwidget)
        # self.managerIcon_label.setText("")
        # self.managerIcon_label.setFixedSize(30, 30)
        # self.managerIcon_label.setScaledContents(True)
        # self.r1_gridLayout.addWidget(self.managerIcon_label, 0, 2, 1, 1)
        #
        # # ----------
        # # ----------


        ## DUMP


        # self.baseScene_label = QtWidgets.QLabel(self.centralwidget)
        # self.baseScene_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        # self.baseScene_label.setText(("Base Scene:"))
        # self.baseScene_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        # self.r1_gridLayout.addWidget(self.baseScene_label, 0, 0, 1, 1)
        #
        # self.baseScene_lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        # self.baseScene_lineEdit.setText((""))
        # self.baseScene_lineEdit.setPlaceholderText((""))
        # self.baseScene_lineEdit.setReadOnly(True)
        # self.r1_gridLayout.addWidget(self.baseScene_lineEdit, 0, 1, 1, 1)
        #
        # self.managerIcon_label = QtWidgets.QLabel(self.centralwidget)
        # self.managerIcon_label.setText("")
        # self.managerIcon_label.setFixedSize(30, 30)
        # self.managerIcon_label.setScaledContents(True)
        # self.r1_gridLayout.addWidget(self.managerIcon_label, 0, 2, 1, 1)
        # self.headerBar_layout.addWidget(self.managerIcon_label)





        self.project_label = QtWidgets.QLabel(self.centralwidget)
        self.project_label.setText(("Project:"))
        self.project_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.r1_gridLayout.addWidget(self.project_label, 1, 0, 1, 1)

        self.project_lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.project_lineEdit.setText((""))
        self.project_lineEdit.setPlaceholderText((""))
        self.r1_gridLayout.addWidget(self.project_lineEdit, 1, 1, 1, 1)

        self.setProject_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.setProject_pushButton.setText(("SET"))
        self.r1_gridLayout.addWidget(self.setProject_pushButton, 1, 2, 1, 1)

        self.main_gridLayout.addLayout(self.r1_gridLayout, 0, 0, 1, 1)

        self.category_tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.category_tabWidget.setMaximumSize(QtCore.QSize(16777215, 20))
        self.category_tabWidget.setTabPosition(QtWidgets.QTabWidget.North)
        self.category_tabWidget.setElideMode(QtCore.Qt.ElideNone)
        self.category_tabWidget.setUsesScrollButtons(False)

        self.main_gridLayout.addWidget(self.category_tabWidget, 2, 0, 1, 1)

        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)


        self.scenes_listWidget = QtWidgets.QListWidget(self.splitter)

        self.frame = QtWidgets.QFrame(self.splitter)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)

        self.gridLayout_6 = QtWidgets.QGridLayout(self.frame)
        self.gridLayout_6.setContentsMargins(-1, -1, 0, 0)

        self.verticalLayout = QtWidgets.QVBoxLayout()

        self.notes_label = QtWidgets.QLabel(self.frame)
        self.notes_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.notes_label.setText(("Version Notes:"))
        self.notes_label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.verticalLayout.addWidget(self.notes_label)

        self.notes_textEdit = QtWidgets.QTextEdit(self.frame)
        self.notes_textEdit.setReadOnly(True)
        self.verticalLayout.addWidget(self.notes_textEdit)

        # PyInstaller and Standalone version compatibility

        # emptyIcon = os.path.normpath(os.path.join(self.manager.getIconsDir(), "empty_thumbnail.png"))

        if FORCE_QT4:
            # self.E_tPixmap = QtWidgets.QPixmap(emptyIcon)
            self.E_tPixmap = QtWidgets.QPixmap(":/icons/CSS/rc/empty_thumbnail.png")
        else:
            # self.E_tPixmap = QtGui.QPixmap(emptyIcon)
            self.E_tPixmap = QtGui.QPixmap(":/icons/CSS/rc/empty_thumbnail.png")
        self.thumbnail_label = ImageWidget(self.frame)
        self.thumbnail_label.setObjectName("image")
        self.thumbnail_label.setPixmap(self.E_tPixmap)

        self.thumbnail_label.setMinimumSize(QtCore.QSize(221, 124))
        self.thumbnail_label.setFrameShape(QtWidgets.QFrame.Box)
        self.thumbnail_label.setScaledContents(True)
        self.thumbnail_label.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.thumbnail_label)

        self.gridLayout_6.addLayout(self.verticalLayout, 3, 0, 1, 1)

        self.gridLayout_7 = QtWidgets.QGridLayout()
        self.gridLayout_7.setContentsMargins(-1, -1, 10, 10)

        self.showPreview_pushButton = QtWidgets.QPushButton(self.frame)
        self.showPreview_pushButton.setMinimumSize(QtCore.QSize(100, 30))
        self.showPreview_pushButton.setMaximumSize(QtCore.QSize(150, 30))
        self.showPreview_pushButton.setText(("Show Preview"))
        self.gridLayout_7.addWidget(self.showPreview_pushButton, 0, 3, 1, 1)

        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setSpacing(1)

        self.version_label = QtWidgets.QLabel(self.frame)
        self.version_label.setMinimumSize(QtCore.QSize(60, 30))
        self.version_label.setMaximumSize(QtCore.QSize(60, 30))
        self.version_label.setFrameShape(QtWidgets.QFrame.Box)
        self.version_label.setText(("Version:"))
        self.version_label.setAlignment(QtCore.Qt.AlignCenter)
        self.horizontalLayout_4.addWidget(self.version_label)

        self.version_comboBox = QtWidgets.QComboBox(self.frame)
        self.version_comboBox.setMinimumSize(QtCore.QSize(60, 30))
        self.version_comboBox.setMaximumSize(QtCore.QSize(100, 30))
        self.horizontalLayout_4.addWidget(self.version_comboBox)

        self.gridLayout_7.addLayout(self.horizontalLayout_4, 0, 0, 1, 1)

        self.makeReference_pushButton = QtWidgets.QPushButton(self.frame)
        self.makeReference_pushButton.setMinimumSize(QtCore.QSize(100, 30))
        self.makeReference_pushButton.setMaximumSize(QtCore.QSize(300, 30))
        self.makeReference_pushButton.setText(("Make Reference"))
        self.gridLayout_7.addWidget(self.makeReference_pushButton, 1, 0, 1, 1)

        self.addNote_pushButton = QtWidgets.QPushButton(self.frame)
        self.addNote_pushButton.setMinimumSize(QtCore.QSize(100, 30))
        self.addNote_pushButton.setMaximumSize(QtCore.QSize(150, 30))
        self.addNote_pushButton.setText(("Add Note"))
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

        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 680, 18))
        self.menubar.setObjectName(("menubar"))

        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName(("statusbar"))
        self.setStatusBar(self.statusbar)

        self.fileMenu = self.menubar.addMenu("File")
        createProject_fm = QtWidgets.QAction("&Create Project", self)
        self.saveVersion_fm = QtWidgets.QAction("&Save Version", self)
        self.saveBaseScene_fm = QtWidgets.QAction("&Save Base Scene", self)

        loadReferenceScene_fm = QtWidgets.QAction("&Load/Reference Scene", self)

        add_remove_users_fm = QtWidgets.QAction("&Add/Remove Users", self)

        add_remove_categories_fm = QtWidgets.QAction("&Add/Remove Categories", self)

        settings_fm = QtWidgets.QAction("&Settings", self)

        pb_settings_fm = QtWidgets.QAction("&Playblast Settings", self)

        projectSettings_fm = QtWidgets.QAction("&Project Settings", self)

        changeAdminPass_fm = QtWidgets.QAction("&Change Admin Password", self)

        self.changeCommonFolder =  QtWidgets.QAction("&Change Common Database", self)
        # self.changeCommonFolder.setVisible(False)

        deleteFile_fm = QtWidgets.QAction("&Delete Selected Base Scene", self)
        deleteReference_fm = QtWidgets.QAction("&Delete Reference of Selected Scene", self)
        reBuildDatabase_fm = QtWidgets.QAction("&Re-build Project Database", self)
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
        self.fileMenu.addAction(add_remove_users_fm)
        self.fileMenu.addAction(add_remove_categories_fm)
        self.fileMenu.addAction(pb_settings_fm)
        self.fileMenu.addAction(projectSettings_fm)
        self.fileMenu.addAction(changeAdminPass_fm)
        self.fileMenu.addAction(self.changeCommonFolder)

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

        self.changeCommonFolder.triggered.connect(self.manager._defineCommonFolder)
        self.changeCommonFolder.triggered.connect(lambda: self.manager.init_paths(self.manager.swName))
        self.changeCommonFolder.triggered.connect(self.manager.init_database)
        self.changeCommonFolder.triggered.connect(self._initUsers)
        self.changeCommonFolder.triggered.connect(self.onUserChange)

        createProject_fm.triggered.connect(self.createProjectUI)

        settings_fm.triggered.connect(self.settingsUI)
        add_remove_users_fm.triggered.connect(self.addRemoveUserUI)
        pb_settings_fm.triggered.connect(self.onPbSettings)

        add_remove_categories_fm.triggered.connect(self.addRemoveCategoryUI)

        projectSettings_fm.triggered.connect(self.projectSettingsUI)

        changeAdminPass_fm.triggered.connect(self.changePasswordUI)




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

        # self.project_lineEdit.

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
                # self.onSubProjectChange()
            else:
                self.infoPop(textTitle="Naming Error", textHeader="Naming Error",
                             textInfo="Choose an unique name with latin characters without spaces", type="C")

    def createProjectUI(self):

        # This method is NOT Software Specific
        self.createproject_Dialog = QtWidgets.QDialog(parent=self)
        self.createproject_Dialog.setObjectName(("createproject_Dialog"))
        self.createproject_Dialog.resize(419, 300)
        self.createproject_Dialog.setWindowTitle(("Create New Project"))

        self.projectroot_label = QtWidgets.QLabel(self.createproject_Dialog)
        self.projectroot_label.setGeometry(QtCore.QRect(20, 30, 71, 20))
        self.projectroot_label.setText(("Project Path:"))
        self.projectroot_label.setObjectName(("projectpath_label"))

        currentProjects = os.path.abspath(os.path.join(self.manager.projectDir, os.pardir))
        self.projectroot_lineEdit = QtWidgets.QLineEdit(self.createproject_Dialog)
        self.projectroot_lineEdit.setGeometry(QtCore.QRect(90, 30, 241, 21))
        self.projectroot_lineEdit.setText((currentProjects))
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
        self.brandname_lineEdit.setPlaceholderText(("(optional)"))
        self.brandname_lineEdit.setObjectName(("brandname_lineEdit"))

        self.projectname_lineEdit = QtWidgets.QLineEdit(self.createproject_Dialog)
        self.projectname_lineEdit.setGeometry(QtCore.QRect(140, 140, 131, 21))
        self.projectname_lineEdit.setPlaceholderText(("Mandatory Field"))
        self.projectname_lineEdit.setObjectName(("projectname_lineEdit"))

        self.client_lineEdit = QtWidgets.QLineEdit(self.createproject_Dialog)
        self.client_lineEdit.setGeometry(QtCore.QRect(280, 140, 121, 21))
        self.client_lineEdit.setPlaceholderText(("Mandatory Field"))
        self.client_lineEdit.setObjectName(("client_lineEdit"))

        # TODO : ref

        resolution_label = QtWidgets.QLabel(self.createproject_Dialog)
        resolution_label.setGeometry(QtCore.QRect(24, 180 , 111, 21))
        resolution_label.setText("Resolution")

        resolutionX_spinBox = QtWidgets.QSpinBox(self.createproject_Dialog)
        resolutionX_spinBox.setGeometry(QtCore.QRect(80, 180, 60, 21))
        resolutionX_spinBox.setObjectName(("resolutionX_spinBox"))
        resolutionX_spinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        resolutionX_spinBox.setRange(1,99999)
        resolutionX_spinBox.setValue(1920)

        resolutionY_spinBox = QtWidgets.QSpinBox(self.createproject_Dialog)
        resolutionY_spinBox.setGeometry(QtCore.QRect(145, 180, 60, 21))
        resolutionY_spinBox.setObjectName(("resolutionY_spinBox"))
        resolutionY_spinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        resolutionY_spinBox.setRange(1,99999)
        resolutionY_spinBox.setValue(1080)

        fps_label = QtWidgets.QLabel(self.createproject_Dialog)
        fps_label.setGeometry(QtCore.QRect(54, 210 , 111, 21))
        fps_label.setText("FPS")

        fps_comboBox = QtWidgets.QComboBox(self.createproject_Dialog)
        fps_comboBox.setGeometry(QtCore.QRect(80, 210 , 60, 21))
        fps_comboBox.addItems(self.manager.fpsList)
        fps_comboBox.setCurrentIndex(2)

        self.createproject_buttonBox = QtWidgets.QDialogButtonBox(self.createproject_Dialog)
        self.createproject_buttonBox.setGeometry(QtCore.QRect(30, 250, 371, 32))
        self.createproject_buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.createproject_buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.createproject_buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).setMinimumSize(QtCore.QSize(100, 30))
        self.createproject_buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setMinimumSize(QtCore.QSize(100, 30))
        self.createproject_buttonBox.setObjectName(("buttonBox"))

        self.cp_button = self.createproject_buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
        self.cp_button.setText('Create Project')

        def browseProjectRoot():
            dlg = QtWidgets.QFileDialog()
            dlg.setFileMode(QtWidgets.QFileDialog.Directory)

            if dlg.exec_():
                # selectedroot = os.path.normpath(unicode(dlg.selectedFiles()[0]))
                selectedroot = os.path.normpath(unicode(dlg.selectedFiles()[0])).encode("utf-8")
                self.projectroot_lineEdit.setText(selectedroot)
                resolve()


        def onCreateNewProject():
            root = os.path.normpath(self.projectroot_lineEdit.text())
            if not self.manager.nameCheck(root, allowSpaces=True, directory=True):
                self.infoPop(textTitle="Non-Ascii Character", textHeader="Selected Project Root cannot be used",
                             textInfo="There are non-ascii characters in the selected path.", type="C")
                return
            if not os.path.isdir(root):
                self.infoPop(textTitle="Path Error", textHeader="Selected Project Root does not exist", type="C")
                return

            # root = unicode(self.projectroot_lineEdit.text()).encode("utf-8")
            # root = unicode(self.projectroot_lineEdit.text(), "utf-8")
            pName = self.projectname_lineEdit.text()
            bName = self.brandname_lineEdit.text()
            cName = self.client_lineEdit.text()
            projectSettingsDB = {"Resolution": [resolutionX_spinBox.value(), resolutionY_spinBox.value()],
                                   "FPS": int(fps_comboBox.currentText())}

            pPath = self.manager.createNewProject(root, pName, bName, cName, settingsData=projectSettingsDB)
            if pPath:
                self.manager.setProject(pPath)
            # self.onProjectChange()

            self.initMainUI()
            self.createproject_Dialog.close()

        def resolve():
            if self.projectname_lineEdit.text() == "" or self.client_lineEdit.text() == "" or self.projectroot_lineEdit.text() == "":
                self.resolvedpath_label.setText("Fill the mandatory fields")
                self.newProjectPath = None
                return
            resolvedPath = self.manager.resolveProjectPath(self.projectroot_lineEdit.text(),
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

        # This method is NOT Software Specific
        if FORCE_QT4:
            iconFont = QtWidgets.QFont()
        else:
            iconFont = QtGui.QFont()
        # iconFont = QtGui.QFont()
        iconFont.setPointSize(12)
        iconFont.setBold(True)
        iconFont.setWeight(75)

        self.setProject_Dialog = QtWidgets.QDialog(parent=self)
        self.setProject_Dialog.resize(982, 450)
        self.setProject_Dialog.setWindowTitle(("Set Project"))
        self.setProject_Dialog.setFocus()

        gridLayout = QtWidgets.QGridLayout(self.setProject_Dialog)
        gridLayout.setObjectName(("gridLayout"))

        M1_horizontalLayout = QtWidgets.QHBoxLayout()

        lookIn_label = QtWidgets.QLabel(self.setProject_Dialog)
        lookIn_label.setText(("Look in:"))
        lookIn_label.setFocusPolicy(QtCore.Qt.StrongFocus)
        # lookIn_label.setFocus()

        M1_horizontalLayout.addWidget(lookIn_label)

        self.lookIn_lineEdit = QtWidgets.QLineEdit(self.setProject_Dialog)
        self.lookIn_lineEdit.setText((""))
        self.lookIn_lineEdit.setPlaceholderText((""))
        # self.lookIn_lineEdit.setStyleSheet("background-color: rgb(80,80,80); color: white")


        M1_horizontalLayout.addWidget(self.lookIn_lineEdit)

        # a fake button which actually does nothing
        fakeButton = QtWidgets.QPushButton(self.setProject_Dialog)
        fakeButton.setVisible(False)


        browse_pushButton = QtWidgets.QPushButton(self.setProject_Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(browse_pushButton.sizePolicy().hasHeightForWidth())
        browse_pushButton.setSizePolicy(sizePolicy)
        browse_pushButton.setMaximumSize(QtCore.QSize(50, 16777215))
        browse_pushButton.setText("Browse")

        M1_horizontalLayout.addWidget(browse_pushButton)

        self.back_pushButton = QtWidgets.QPushButton(self.setProject_Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.back_pushButton.sizePolicy().hasHeightForWidth())
        self.back_pushButton.setSizePolicy(sizePolicy)
        self.back_pushButton.setMaximumSize(QtCore.QSize(30, 16777215))
        self.back_pushButton.setFont(iconFont)
        self.back_pushButton.setText(("<"))
        self.back_pushButton.setShortcut((""))

        M1_horizontalLayout.addWidget(self.back_pushButton)

        self.forward_pushButton = QtWidgets.QPushButton(self.setProject_Dialog)
        self.forward_pushButton.setMaximumSize(QtCore.QSize(30, 16777215))
        self.forward_pushButton.setFont(iconFont)
        self.forward_pushButton.setText((">"))
        self.forward_pushButton.setShortcut((""))

        M1_horizontalLayout.addWidget(self.forward_pushButton)

        up_pushButton = QtWidgets.QPushButton(self.setProject_Dialog)
        up_pushButton.setMaximumSize(QtCore.QSize(30, 16777215))
        up_pushButton.setText(("Up"))
        up_pushButton.setShortcut((""))

        M1_horizontalLayout.addWidget(up_pushButton)

        gridLayout.addLayout(M1_horizontalLayout, 0, 0, 1, 1)

        M2_horizontalLayout = QtWidgets.QHBoxLayout()

        M2_splitter = QtWidgets.QSplitter(self.setProject_Dialog)
        M2_splitter.setHandleWidth(10)


        # self.folders_tableView = QtWidgets.QTableView(self.M2_splitter)
        self.folders_treeView = QtWidgets.QTreeView(M2_splitter)
        self.folders_treeView.setMinimumSize(QtCore.QSize(0, 0))
        self.folders_treeView.setDragEnabled(True)
        self.folders_treeView.setDragDropMode(QtWidgets.QAbstractItemView.DragOnly)
        self.folders_treeView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self.folders_treeView.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.folders_treeView.setItemsExpandable(False)
        self.folders_treeView.setRootIsDecorated(False)
        self.folders_treeView.setSortingEnabled(True)
        # self.folders_treeView.setStyleSheet("background-color: rgb(80,80,80); color: white")

        verticalLayoutWidget = QtWidgets.QWidget(M2_splitter)

        M2_S2_verticalLayout = QtWidgets.QVBoxLayout(verticalLayoutWidget)
        M2_S2_verticalLayout.setContentsMargins(0, 10, 0, 10)
        M2_S2_verticalLayout.setSpacing(6)

        favorites_label = QtWidgets.QLabel(verticalLayoutWidget)
        if FORCE_QT4:
            font = QtWidgets.QFont()
        else:
            font = QtGui.QFont()
        # font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        favorites_label.setFont(font)
        favorites_label.setText(("Bookmarks:"))
        favorites_label.setObjectName(("favorites_label"))

        M2_S2_verticalLayout.addWidget(favorites_label)

        self.favorites_listWidget = DropListWidget(verticalLayoutWidget)
        # self.favorites_listWidget.setAlternatingRowColors(True)
        self.favorites_listWidget.setObjectName(("favorites_listWidget"))
        # self.favorites_listWidget.setStyleSheet("background-color: rgb(80,80,80); color: white")

        M2_S2_verticalLayout.addWidget(self.favorites_listWidget)
        M2_S2_horizontalLayout = QtWidgets.QHBoxLayout()
        M2_S2_horizontalLayout.setObjectName(("M2_S2_horizontalLayout"))

        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        M2_S2_horizontalLayout.addItem(spacerItem)

        remove_pushButton = QtWidgets.QPushButton(verticalLayoutWidget)
        remove_pushButton.setMaximumSize(QtCore.QSize(35, 35))
        remove_pushButton.setFont(iconFont)
        remove_pushButton.setText(("-"))
        remove_pushButton.setObjectName(("remove_pushButton"))

        M2_S2_horizontalLayout.addWidget(remove_pushButton)

        add_pushButton = QtWidgets.QPushButton(verticalLayoutWidget)
        add_pushButton.setMaximumSize(QtCore.QSize(35, 35))
        add_pushButton.setFont(iconFont)
        add_pushButton.setText(("+"))
        add_pushButton.setObjectName(("add_pushButton"))

        M2_S2_horizontalLayout.addWidget(add_pushButton)

        M2_S2_verticalLayout.addLayout(M2_S2_horizontalLayout)

        M2_horizontalLayout.addWidget(M2_splitter)

        gridLayout.addLayout(M2_horizontalLayout, 1, 0, 1, 1)

        M3_horizontalLayout = QtWidgets.QHBoxLayout()
        M3_horizontalLayout.setContentsMargins(0, 10, -1, -1)
        M3_horizontalLayout.setObjectName(("M3_horizontalLayout"))

        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        dirFilter_label = QtWidgets.QLabel()
        dirFilter_label.setText("Search Filter")
        self.dirFilter_lineEdit = QtWidgets.QLineEdit(self.setProject_Dialog)
        self.dirFilter_lineEdit.setMaximumWidth(175)

        if FORCE_QT4:
            placeholderFont = QtWidgets.QFont("Seqoe UI Symbol")
        else:
            placeholderFont = QtGui.QFont("Seqoe UI Symbol")

        self.dirFilter_lineEdit.setFont(placeholderFont)
        self.dirFilter_lineEdit.setPlaceholderText("🔍")

        M3_horizontalLayout.addWidget(dirFilter_label)
        M3_horizontalLayout.addWidget(self.dirFilter_lineEdit)


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
        self.projectsRoot = os.path.abspath(os.path.join(self.manager.projectDir, os.pardir))
        self.browser = Browse()
        self.spActiveProjectPath = None
        self.__flagView = True

        # self.proxyModel = QtWidgets.QSortFilterProxyModel()
        # self.proxyModel.setDynamicSortFilter(True)

        self.sourceModel = QtWidgets.QFileSystemModel()
        self.sourceModel.setNameFilterDisables(False)
        self.sourceModel.setNameFilters(["*"])

        self.sourceModel.setRootPath(self.projectsRoot)
        self.sourceModel.setFilter(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot | QtCore.QDir.Time)


        # self.proxyModel.setSourceModel(self.sourceModel)
        # self.folders_treeView.setModel(self.proxyModel)
        self.folders_treeView.setModel(self.sourceModel)
        self.folders_treeView.setRootIndex(self.sourceModel.index(self.projectsRoot))


        # self.folders_treeView.hideColumn(1)
        # self.folders_treeView.hideColumn(2)
        self.folders_treeView.setColumnWidth(0,400)
        self.folders_treeView.setColumnWidth(1,0)
        self.folders_treeView.setColumnWidth(2,0)


        # self.setPmodel.setRootPath(self.projectsRoot)
        # self.setPmodel.setFilter(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot | QtCore.QDir.Time)
        # # self.setPmodel.setFilter(QtCore.QDir.Dirs)
        # # self.setPmodel.setFilter(QtCore.QDir.Files)
        #
        # # --------------s
        # if FORCE_QT4:
        #     self.DirFilter = QtCore.QStringList()
        # else:
        #     self.DirFilter = []
        #
        # self.setPmodel.setNameFilterDisables(False)
        # # --------------e
        #
        #
        #
        # self.folders_tableView.setModel(self.setPmodel)
        # self.folders_tableView.setRootIndex(self.setPmodel.index(self.projectsRoot))
        # self.folders_tableView.hideColumn(1)
        # self.folders_tableView.hideColumn(2)
        # self.folders_tableView.setColumnWidth(0,400)

        self.favList = self.manager.loadFavorites()
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
        # self.dirFilter_lineEdit.returnPressed.connect(self.filterDirectories)

        cancel_pushButton.clicked.connect(self.setProject_Dialog.close)
        set_pushButton.clicked.connect(setProject)
        # set_pushButton.clicked.connect(self.setProject_Dialog.close)

        self.setProject_Dialog.show()

    def transferCentralUI(self):

        try: self.transferCentral_Dialog.close()
        except AttributeError: pass

        sceneInfo = self.manager.getOpenSceneInfo()


        self.transferCentral_Dialog = QtWidgets.QDialog(parent=self)
        self.transferCentral_Dialog.resize(460, 320)
        self.transferCentral_Dialog.setWindowTitle(("Transfer Central"))
        self.transferCentral_Dialog.setFocus()
        # transferCentral_Dialog.setModal(True)

        tc_verticalLayout = QtWidgets.QVBoxLayout(self.transferCentral_Dialog)

        # ----------
        # HEADER BAR
        # ----------
        margin = 5
        # barColor = "background-color: rgb(80,80,80);"
        # barColor = "background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #565656, stop: 0.1 #525252, stop: 0.5 #4e4e4e, stop: 0.9 #4a4a4a, stop: 1 #464646);"
        colorWidget = QtWidgets.QWidget(self.transferCentral_Dialog)
        headerLayout = QtWidgets.QHBoxLayout(colorWidget)
        headerLayout.setSpacing(0)
        try: headerLayout.setMargin(0)
        except AttributeError: pass

        tikIcon_label = QtWidgets.QLabel(self.centralwidget)
        # tikIcon_label.setFixedSize(115, 30)
        tikIcon_label.setObjectName("header")
        tikIcon_label.setMaximumWidth(125)
        try: tikIcon_label.setMargin(margin)
        except AttributeError: pass
        tikIcon_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        tikIcon_label.setScaledContents(False)
        # testBitmap = QtGui.QPixmap(os.path.join(self.manager.getIconsDir(), "tmTransfer.png"))
        testBitmap = QtGui.QPixmap(":/icons/CSS/rc/tmTransfer.png")
        tikIcon_label.setPixmap(testBitmap)

        headerLayout.addWidget(tikIcon_label)

        resolvedPath_label = QtWidgets.QLabel()
        resolvedPath_label.setObjectName("header")
        try: resolvedPath_label.setMargin(margin)
        except AttributeError: pass
        resolvedPath_label.setIndent(2)
        # resolvedPath_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        resolvedPath_label.setFont(QtGui.QFont("Times", 7, QtGui.QFont.Bold))
        resolvedPath_label.setWordWrap(True)

        headerLayout.addWidget(resolvedPath_label)


        # colorWidget.setStyleSheet(barColor)
        tc_verticalLayout.addWidget(colorWidget)
        # ----------
        # ----------

        tabWidget = QtWidgets.QTabWidget(self.transferCentral_Dialog)
        exportTab = QtWidgets.QWidget()

        exp_verticalLayout = QtWidgets.QVBoxLayout(exportTab)
        currentProject_label = QtWidgets.QLabel(exportTab)
        currentProject_label.setAlignment(QtCore.Qt.AlignTop)
        currentProject_label.setText("Current Project:")
        exp_verticalLayout.addWidget(currentProject_label)

        formLayout = QtWidgets.QFormLayout()
        formLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        formLayout.setFormAlignment(QtCore.Qt.AlignJustify | QtCore.Qt.AlignTop)
        formLayout.setAlignment(QtCore.Qt.AlignTop)

        name_label = QtWidgets.QLabel(exportTab)
        name_label.setText(("Name:"))
        formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, name_label)

        name_horizontalLayout = QtWidgets.QHBoxLayout()
        autoName_radioButton = QtWidgets.QRadioButton(exportTab)
        autoName_radioButton.setText(("Auto from Scene/Object"))
        autoName_radioButton.setChecked(True)

        customName_radioButton = QtWidgets.QRadioButton(exportTab)
        customName_radioButton.setText(("Custom"))

        naming_buttonGroup = QtWidgets.QButtonGroup(self.transferCentral_Dialog)
        naming_buttonGroup.addButton(autoName_radioButton)
        naming_buttonGroup.addButton(customName_radioButton)
        name_horizontalLayout.addWidget(autoName_radioButton)
        name_horizontalLayout.addWidget(customName_radioButton)

        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        name_horizontalLayout.addItem(spacerItem)
        formLayout.setLayout(0, QtWidgets.QFormLayout.FieldRole, name_horizontalLayout)

        customName_lineEdit = QtWidgets.QLineEdit(exportTab)
        customName_lineEdit.setFrame(True)
        customName_lineEdit.setPlaceholderText(("Custom Export Name"))
        formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, customName_lineEdit)

        selection_label = QtWidgets.QLabel(exportTab)
        selection_label.setText(("Selection:"))
        formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, selection_label)

        selection_horizontalLayout = QtWidgets.QHBoxLayout()
        selection_radioButton = QtWidgets.QRadioButton(exportTab)
        selection_radioButton.setText(("Selection"))
        selection_radioButton.setChecked(True)
        selection_radioButton.setObjectName(("selection_radioButton"))

        scene_radioButton = QtWidgets.QRadioButton(exportTab)
        scene_radioButton.setText(("Scene"))

        sel_buttonGroup = QtWidgets.QButtonGroup(self.transferCentral_Dialog)
        sel_buttonGroup.addButton(selection_radioButton)
        selection_horizontalLayout.addWidget(selection_radioButton)
        sel_buttonGroup.addButton(scene_radioButton)
        selection_horizontalLayout.addWidget(scene_radioButton)

        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        selection_horizontalLayout.addItem(spacerItem1)

        formLayout.setLayout(2, QtWidgets.QFormLayout.FieldRole, selection_horizontalLayout)
        format_label = QtWidgets.QLabel(exportTab)
        format_label.setText(("Format:"))
        formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, format_label)

        format_horizontalLayout = QtWidgets.QHBoxLayout()

        obj_checkBox = QtWidgets.QCheckBox(exportTab)
        obj_checkBox.setText(("Obj"))
        obj_checkBox.setChecked(True)
        format_horizontalLayout.addWidget(obj_checkBox)

        alembic_checkBox = QtWidgets.QCheckBox(exportTab)
        alembic_checkBox.setText(("Alembic"))
        alembic_checkBox.setChecked(False)
        format_horizontalLayout.addWidget(alembic_checkBox)

        fbx_checkBox = QtWidgets.QCheckBox(exportTab)
        fbx_checkBox.setText(("FBX"))
        fbx_checkBox.setChecked(False)
        format_horizontalLayout.addWidget(fbx_checkBox)

        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        format_horizontalLayout.addItem(spacerItem2)
        formLayout.setLayout(3, QtWidgets.QFormLayout.FieldRole, format_horizontalLayout)

        range_label = QtWidgets.QLabel(exportTab)
        range_label.setText(("Time Range:"))
        formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, range_label)

        timeRange_horizontalLayout1 = QtWidgets.QHBoxLayout()

        timeSlider_radioButton = QtWidgets.QRadioButton(exportTab)
        timeSlider_radioButton.setText(("Time Slider"))
        timeSlider_radioButton.setShortcut((""))
        timeSlider_radioButton.setChecked(True)

        timerange_buttonGroup = QtWidgets.QButtonGroup(self.transferCentral_Dialog)
        timerange_buttonGroup.addButton(timeSlider_radioButton)
        timeRange_horizontalLayout1.addWidget(timeSlider_radioButton)

        singleFrame_radioButton = QtWidgets.QRadioButton(exportTab)
        singleFrame_radioButton.setText(("Single Frame"))
        singleFrame_radioButton.setChecked(False)
        timerange_buttonGroup.addButton(singleFrame_radioButton)
        timeRange_horizontalLayout1.addWidget(singleFrame_radioButton)

        customRange_radioButton = QtWidgets.QRadioButton(exportTab)
        customRange_radioButton.setText(("Custom"))
        customRange_radioButton.setChecked(False)

        timerange_buttonGroup.addButton(customRange_radioButton)
        timeRange_horizontalLayout1.addWidget(customRange_radioButton)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        timeRange_horizontalLayout1.addItem(spacerItem3)
        formLayout.setLayout(4, QtWidgets.QFormLayout.FieldRole, timeRange_horizontalLayout1)

        timeRange_horizontalLayout2 = QtWidgets.QHBoxLayout()

        frameStart_label = QtWidgets.QLabel(exportTab)
        frameStart_label.setText(("Start"))

        timeRange_horizontalLayout2.addWidget(frameStart_label)

        frameStart_doubleSpinBox = QtWidgets.QDoubleSpinBox(exportTab)
        frameStart_doubleSpinBox.setWrapping(False)
        frameStart_doubleSpinBox.setFrame(True)
        frameStart_doubleSpinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        frameStart_doubleSpinBox.setSpecialValueText((""))
        frameStart_doubleSpinBox.setKeyboardTracking(True)
        timeRange_horizontalLayout2.addWidget(frameStart_doubleSpinBox)
        spacerItem4 = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        timeRange_horizontalLayout2.addItem(spacerItem4)

        frameEnd_label = QtWidgets.QLabel(exportTab)
        frameEnd_label.setText(("End"))
        timeRange_horizontalLayout2.addWidget(frameEnd_label)

        frameEnd_doubleSpinBox = QtWidgets.QDoubleSpinBox(exportTab)
        frameEnd_doubleSpinBox.setWrapping(False)
        frameEnd_doubleSpinBox.setFrame(True)
        frameEnd_doubleSpinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        frameEnd_doubleSpinBox.setSpecialValueText((""))
        frameEnd_doubleSpinBox.setKeyboardTracking(True)
        frameEnd_doubleSpinBox.setProperty("value", 10.0)
        timeRange_horizontalLayout2.addWidget(frameEnd_doubleSpinBox)

        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        timeRange_horizontalLayout2.addItem(spacerItem5)
        formLayout.setLayout(5, QtWidgets.QFormLayout.FieldRole, timeRange_horizontalLayout2)

        # options_label = QtWidgets.QLabel(exportTab)
        # options_label.setEnabled(True)
        # options_label.setInputMethodHints(QtCore.Qt.ImhNone)
        # options_label.setText(("Options:"))
        # formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, options_label)

        # options_horizontalLayout = QtWidgets.QHBoxLayout()
        #
        # useAssetLibrarySettings_radioButton = QtWidgets.QRadioButton(exportTab)
        # useAssetLibrarySettings_radioButton.setText(("Use Asset Library Settings"))
        # useAssetLibrarySettings_radioButton.setChecked(False)
        #
        # options_buttonGroup = QtWidgets.QButtonGroup(self.transferCentral_Dialog)
        # options_buttonGroup.addButton(useAssetLibrarySettings_radioButton)
        # options_horizontalLayout.addWidget(useAssetLibrarySettings_radioButton)
        # openExportOptions_radioButton = QtWidgets.QRadioButton(exportTab)
        # openExportOptions_radioButton.setText(("Open Export Options"))
        # openExportOptions_radioButton.setChecked(True)
        # options_buttonGroup.addButton(openExportOptions_radioButton)
        # options_horizontalLayout.addWidget(openExportOptions_radioButton)
        # spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        # options_horizontalLayout.addItem(spacerItem6)
        # formLayout.setLayout(6, QtWidgets.QFormLayout.FieldRole, options_horizontalLayout)
        #
        #

        # revision_label = QtWidgets.QLabel(exportTab)
        # revision_label.setText(("Revision:"))
        # revision_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        # formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, revision_label)
        #
        # rev_horizontalLayout = QtWidgets.QHBoxLayout()
        #
        # revision_Spinbox = QtWidgets.QSpinBox(exportTab)
        # revision_Spinbox.setMaximumSize(QtCore.QSize(50, 16777215))
        # revision_Spinbox.setMinimum(1)
        # revision_Spinbox.setMaximum(999)
        # rev_horizontalLayout.addWidget(revision_Spinbox)
        #
        # incremental_checkBox = QtWidgets.QCheckBox(exportTab)
        # incremental_checkBox.setText(("Use Next Available Revision"))
        # incremental_checkBox.setChecked(True)
        # rev_horizontalLayout.addWidget(incremental_checkBox)

        # formLayout.setLayout(6, QtWidgets.QFormLayout.FieldRole, rev_horizontalLayout)

        exp_verticalLayout.addLayout(formLayout)

        spacerItem_m = QtWidgets.QSpacerItem(40, 40, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        exp_verticalLayout.addItem(spacerItem_m)

        expButtons_horizontalLayout = QtWidgets.QHBoxLayout()
        export_pushButton = QtWidgets.QPushButton(exportTab)
        export_pushButton.setText(("Export"))
        expButtons_horizontalLayout.addWidget(export_pushButton)
        exp_verticalLayout.addLayout(expButtons_horizontalLayout)
        cancel_pushButton = QtWidgets.QPushButton(exportTab)
        cancel_pushButton.setText(("Cancel"))
        expButtons_horizontalLayout.addWidget(cancel_pushButton)
        tabWidget.addTab(exportTab, ("Export"))

        ## ------------------
        ## ---IMPORT TAB-----
        ## ------------------

        importTab = QtWidgets.QWidget()
        imp_verticalLayout = QtWidgets.QVBoxLayout(importTab)
        transfers_treeWidget = QtWidgets.QTreeWidget(importTab)

        # obj_topLevel = QtWidgets.QTreeWidgetItem(["OBJ"])
        # fbx_topLevel = QtWidgets.QTreeWidgetItem(["FBX"])
        # alembic_topLevel = QtWidgets.QTreeWidgetItem(["ALEMBIC"])
        #
        # transfers_treeWidget.setHeaderLabels(["Transfer Items"])
        # transfers_treeWidget.addTopLevelItem(obj_topLevel)
        # transfers_treeWidget.addTopLevelItem(fbx_topLevel)
        # transfers_treeWidget.addTopLevelItem(alembic_topLevel)



        # transfers_treeWidget.headerItem().setText(0, "Transfer Items")

        # # items_OBJ = QtWidgets.QTreeWidgetItem(transfers_treeWidget)
        # items_OBJ = QtWidgets.QTreeWidgetItem(transfers_treeWidget)
        # items_OBJ.setText(0, "OBJ")
        # # item_1 = QtWidgets.QTreeWidgetItem(item_0)
        # # item_1 = QtWidgets.QTreeWidgetItem(item_0)
        # items_FBX = QtWidgets.QTreeWidgetItem(transfers_treeWidget)
        # items_FBX.setText(0, "FBX")
        # # item_1 = QtWidgets.QTreeWidgetItem(item_0)
        # # item_1 = QtWidgets.QTreeWidgetItem(item_0)
        # items_ABC = QtWidgets.QTreeWidgetItem(transfers_treeWidget)
        # items_ABC.setText(0, "ALEMBIC")
        # # item_1 = QtWidgets.QTreeWidgetItem(item_0)
        # # item_1 = QtWidgets.QTreeWidgetItem(item_0)
        imp_verticalLayout.addWidget(transfers_treeWidget)
        impButtons_horizontalLayout = QtWidgets.QHBoxLayout()
        import_pushButton = QtWidgets.QPushButton(importTab)
        import_pushButton.setText(("Import"))
        impButtons_horizontalLayout.addWidget(import_pushButton)
        imp_verticalLayout.addLayout(impButtons_horizontalLayout)
        cancel_pushButton_2 = QtWidgets.QPushButton(importTab)
        cancel_pushButton_2.setText(("Cancel"))
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

        # def enableDisableRevision():
        #     revision_Spinbox.setDisabled(incremental_checkBox.isChecked())

        # enableDisableRevision()

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
                customName_lineEdit.setStyleSheet("color: red;")
                customName_lineEdit.setText("Scene Needs to be saves as Base Scene")
                return
            customName_lineEdit.setStyleSheet("color: white;")
            if customName_radioButton.isChecked():
                customName_lineEdit.setText("")
                customName_lineEdit.setReadOnly(False)
                return
                # name = customName_lineEdit.text()
            else:
                if selection_radioButton.isChecked():
                    sel = self.manager._getSelection()
                    if len(sel) > 1:
                        name = "{0}/{0}_{1}_{2}sel".format(sceneInfo["shotName"], sceneInfo["version"], len(sel))
                    elif len(sel) == 1:
                        print "hoyt", sel
                        name = "{0}/{0}_{1}_{2}".format(sceneInfo["shotName"], sceneInfo["version"], sel[0])
                    else:
                        customName_lineEdit.setStyleSheet("color: red;")
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

            # print tabWidget.tabText(tabWidget.currentIndex())
            absPath = transfers_treeWidget.currentItem().text(1)
            # print it
            if absPath:
                self.manager.importTransfers(absPath)

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

        # incremental_checkBox.toggled.connect(enableDisableRevision)


        # Import Signals
        cancel_pushButton_2.clicked.connect(self.transferCentral_Dialog.close)

        tabWidget.currentChanged.connect(populateImports)

        # transfers_treeWidget.doubleClicked.connect(executeImport)
        # transfers_treeWidget.currentItemChanged.connect(executeImport)
        transfers_treeWidget.doubleClicked.connect(executeImport)
        import_pushButton.clicked.connect(executeImport)

        self.transferCentral_Dialog.show()

    def _filterDirectories(self):
        filterWord = self.dirFilter_lineEdit.text()
        self.DirFilter = [(unicode("*%s*" %filterWord))]
        self.sourceModel.setNameFilters(self.DirFilter)

    def settingsUI(self):
        manager = self._getManager()

        # self.allSettingsDict={}
        self.allSettingsDict=Settings()

        settings_Dialog = QtWidgets.QDialog(parent=self)
        settings_Dialog.setWindowTitle(("Settings"))
        settings_Dialog.resize(960, 630)
        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(settings_Dialog.sizePolicy().hasHeightForWidth())

        # settings_Dialog.setSizePolicy(sizePolicy)

        verticalLayout_2 = QtWidgets.QVBoxLayout(settings_Dialog)
        # verticalLayout_2.setContentsMargins(-1, -1, -1, -1)
        try: verticalLayout_2.setMargin(0)
        except AttributeError: pass
        verticalLayout_2.setContentsMargins(10, 10 ,10 ,10)

        verticalLayout = QtWidgets.QVBoxLayout()
        verticalLayout.setSpacing(6)

        splitter = QtWidgets.QSplitter(settings_Dialog)
        splitter.setChildrenCollapsible(False)

        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(splitter.sizePolicy().hasHeightForWidth())
        # splitter.setSizePolicy(sizePolicy)
        splitter.setLineWidth(0)
        splitter.setOrientation(QtCore.Qt.Horizontal)

        left_frame = QtWidgets.QFrame(splitter)
        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(left_frame.sizePolicy().hasHeightForWidth())
        # left_frame.setSizePolicy(sizePolicy)
        left_frame.setMinimumSize(QtCore.QSize(150, 0))
        left_frame.setMaximumSize(QtCore.QSize(16777215, 16777215))
        left_frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        left_frame.setFrameShadow(QtWidgets.QFrame.Plain)
        left_frame.setLineWidth(0)

        verticalLayout_4 = QtWidgets.QVBoxLayout(left_frame)
        # verticalLayout_4.setMargin(10)
        verticalLayout_4.setSpacing(0)

        leftFrame_verticalLayout = QtWidgets.QVBoxLayout()
        leftFrame_verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        leftFrame_verticalLayout.setSpacing(6)

        self.settingsMenu_treeWidget = QtWidgets.QTreeWidget(left_frame)
        self.settingsMenu_treeWidget.setLineWidth(1)
        self.settingsMenu_treeWidget.setRootIsDecorated(True)
        self.settingsMenu_treeWidget.setHeaderHidden(True)
        if FORCE_QT4:
            font = QtWidgets.QFont()
        else:
            font = QtGui.QFont()
        # font = QtGui.QFont()
        font.setPointSize(12)
        # font.setBold(False)
        # font.setWeight(75)
        self.settingsMenu_treeWidget.setFont(font)


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
        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        # sizePolicy.setHorizontalStretch(100)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.contents_frame.sizePolicy().hasHeightForWidth())
        # self.contents_frame.setSizePolicy(sizePolicy)
        # self.contents_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        # self.contents_frame.setFrameShadow(QtWidgets.QFrame.Raised)

        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.contents_frame)
        self.contents_Layout = QtWidgets.QVBoxLayout()
        self.contents_Layout.setSpacing(0)

        self.scrollArea = QtWidgets.QScrollArea(self.contents_frame)
        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        # self.scrollArea.setSizePolicy(sizePolicy)
        # self.scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)

        self.scrollAreaWidgetContents_2 = QtWidgets.QWidget()
        # self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 656, 567))

        self.contentsMaster_layout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.contentsMaster_layout.setMargin(9)
        self.contentsMaster_layout.setSpacing(9)



        self.scrollArea.setWidget(self.scrollAreaWidgetContents_2)
        self.contents_Layout.addWidget(self.scrollArea)
        self.verticalLayout_5.addLayout(self.contents_Layout)
        verticalLayout.addWidget(splitter)

        ## CONTENTS START
        if FORCE_QT4:
            self.headerAFont = QtWidgets.QFont()
            self.headerBFont = QtWidgets.QFont()
        else:
            self.headerAFont = QtGui.QFont()
            self.headerBFont = QtGui.QFont()

        self.headerAFont.setPointSize(14)
        self.headerAFont.setBold(True)
        self.headerAFont.setWeight(75)

        self.headerBFont.setPointSize(10)
        self.headerBFont.setBold(True)
        self.headerBFont.setWeight(75)


        # Visibility Widgets for EACH page
        self.userSettings_vis = QtWidgets.QWidget(self.scrollAreaWidgetContents_2)
        self.projectSettings_vis = QtWidgets.QWidget(self.scrollAreaWidgetContents_2)
        self.previewSettings_vis = QtWidgets.QWidget(self.scrollAreaWidgetContents_2)
        self.categories_vis = QtWidgets.QWidget(self.scrollAreaWidgetContents_2)
        self.importExportOptions_vis = QtWidgets.QWidget(self.scrollAreaWidgetContents_2)
        self.sharedSettings_vis = QtWidgets.QWidget(self.scrollAreaWidgetContents_2)
        self.users_vis = QtWidgets.QWidget(self.scrollAreaWidgetContents_2)
        self.passwords_vis = QtWidgets.QWidget(self.scrollAreaWidgetContents_2)
        self.namingConventions_vis = QtWidgets.QWidget(self.scrollAreaWidgetContents_2)

        self.softwareDB = manager.loadSoftwareDatabase()

        ## USER SETTINGS
        currentUserSettings = manager.loadUserSettings()
        self.allSettingsDict.add("userSettings", currentUserSettings, manager._pathsDict["userSettingsFile"])
        currentCommonFolder = manager._getCommonFolder()
        self.allSettingsDict.add("sharedSettingsDir", currentCommonFolder, manager._pathsDict["commonFolderFile"])
        self._userSettingsContent()


        ## PROJECT SETTINGS
        currentProjectSettings = manager.loadProjectSettings()
        self.allSettingsDict.add("projectSettings", currentProjectSettings, manager._pathsDict["projectSettingsFile"])
        self._projectSettingsContent()

        ## PREVIEW SETTINGS
        self.previewMasterLayout = QtWidgets.QVBoxLayout(self.previewSettings_vis)
        sw = manager.swName.lower()
        #temp
        # sw=""
        if sw == "maya" or sw == "":
            settingsFilePath = os.path.join(manager._pathsDict["previewsDir"], self.softwareDB["Maya"]["pbSettingsFile"])
            currentMayaSettings = manager.loadPBSettings(filePath=settingsFilePath)
            # backward compatibility:
            try:
                currentMayaSettings["ConvertMP4"]
                currentMayaSettings["CrfValue"]
            except KeyError:
                currentMayaSettings["ConvertMP4"] = True
                currentMayaSettings["CrfValue"] = 23

            # update the settings dictionary
            self.allSettingsDict.add("preview_maya", currentMayaSettings, settingsFilePath)

            self._previewSettingsContent_maya()
        if sw == "3dsmax" or sw == "":
            settingsFilePath = os.path.join(manager._pathsDict["previewsDir"], self.softwareDB["3dsMax"]["pbSettingsFile"])
            currentMaxSettings = manager.loadPBSettings(filePath=settingsFilePath)
            # backward compatibility:
            try:
                currentMaxSettings["ConvertMP4"]
                currentMaxSettings["CrfValue"]
            except KeyError:
                currentMaxSettings["ConvertMP4"] = True
                currentMaxSettings["CrfValue"] = 23

            # update the settings dictionary
            self.allSettingsDict.add("preview_max", currentMaxSettings, settingsFilePath)

            self._previewSettingsContent_max()

        self.contentsMaster_layout.addWidget(self.previewSettings_vis)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.previewMasterLayout.addItem(spacerItem)

        ## CATEGORIES
        #temp
        # sw=""
        if sw == "":
            # if it is standalone, get all categories for all softwares
            for value in self.softwareDB.values():
                niceName = value["niceName"]
                folderPath = os.path.normpath(os.path.join(manager._pathsDict["masterDir"], value["databaseDir"]))
                manager._folderCheck(folderPath)

                filePath = os.path.normpath(os.path.join(folderPath, value["categoriesFile"]))
                categoryData = manager.loadCategories(filePath=filePath, swName=niceName)
                self.allSettingsDict.add("categories_%s" %niceName, categoryData, filePath)
        else:
            currentCategories = manager.loadCategories()
            self.allSettingsDict.add("categories_%s" %manager.swName, currentCategories, manager._pathsDict["categoriesFile"])

        # pprint.pprint(self.allSettingsDict)

        self._categoriesContent()

        ## IMPORT/EXPORT OPTIONS
        currentImportSettings = manager.loadImportSettings()
        self.allSettingsDict.add("importSettings", currentImportSettings, manager._pathsDict["importSettingsFile"])
        currentExportSettings = manager.loadExportSettings()
        self.allSettingsDict.add("exportSettings", currentExportSettings, manager._pathsDict["exportSettingsFile"])
        self._importExportContent()

        self._sharedSettingsContent()


        def pageUpdate():
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
                # print item[0], item[1], isVisible
                item[1].setHidden(isVisible)
                # self.userSettings_vis.setHidden(True)


        self.settingsButtonBox = QtWidgets.QDialogButtonBox(settings_Dialog)
        self.settingsButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.settingsApply_btn = self.settingsButtonBox.button(QtWidgets.QDialogButtonBox.Apply)
        verticalLayout.addWidget(self.settingsButtonBox)
        verticalLayout_2.addLayout(verticalLayout)



        settings_Dialog.setTabOrder(self.settingsButtonBox, self.settingsMenu_treeWidget)
        # self.settingsButtonBox.button(QtWidgets.QDialogButtonBox.Apply).setEnabled(False)
        self.settingsApply_btn.setEnabled(False)

        def applySettingChanges():
            for x in self.allSettingsDict.apply():
                manager._dumpJson(x["data"], x["filepath"])
            self.settingsApply_btn.setEnabled(False)

        # # SIGNALS
        # # -------
        #
        self.settingsMenu_treeWidget.currentItemChanged.connect(pageUpdate)

        self.settingsButtonBox.accepted.connect(applySettingChanges)
        self.settingsButtonBox.accepted.connect(settings_Dialog.accept)
        self.settingsApply_btn.clicked.connect(applySettingChanges)

        self.settingsButtonBox.rejected.connect(settings_Dialog.reject)

        splitter.setStretchFactor(1, 20)
        settings_Dialog.show()

    def _userSettingsContent(self):
        manager = self._getManager()
        userSettings_Layout = QtWidgets.QVBoxLayout(self.userSettings_vis)
        userSettings_Layout.setSpacing(6)

        def updateDictionary():
            self.allSettingsDict["userSettings"]["newSettings"][
                "globalFavorites"] = globalFavorites_radiobutton.isChecked()

            enteredPath = os.path.normpath(commonDir_lineEdit.text())
            if manager._checkCommonFolder(enteredPath):
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

        userSettings_Layout.addLayout(userSettings_formLayout)

        # form item 0
        userSettings_label = QtWidgets.QLabel(self.userSettings_vis)
        userSettings_label.setFont(self.headerAFont)
        userSettings_label.setText(("User Settings"))
        userSettings_formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, userSettings_label)

        # form item 1
        favorites_label = QtWidgets.QLabel(self.userSettings_vis)
        favorites_label.setText("Project Favorites:")
        userSettings_formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, favorites_label)

        favorites_layout = QtWidgets.QHBoxLayout()
        globalFavorites_radiobutton = QtWidgets.QRadioButton(self.userSettings_vis)
        globalFavorites_radiobutton.setText("Global Favorites")
        globalFavorites_radiobutton.setChecked(manager.isGlobalFavorites())

        localFavorites_radiobutton = QtWidgets.QRadioButton(self.userSettings_vis)
        localFavorites_radiobutton.setText("Software Specific")
        localFavorites_radiobutton.setChecked(not manager.isGlobalFavorites())

        favorites_buttonGroup = QtWidgets.QButtonGroup(self.userSettings_vis)
        favorites_buttonGroup.addButton(globalFavorites_radiobutton)
        favorites_buttonGroup.addButton(localFavorites_radiobutton)
        favorites_layout.addWidget(globalFavorites_radiobutton)
        favorites_layout.addWidget(localFavorites_radiobutton)
        userSettings_formLayout.setLayout(1, QtWidgets.QFormLayout.FieldRole, favorites_layout)

        # form item 2
        commonDir_label = QtWidgets.QLabel(self.userSettings_vis)
        commonDir_label.setText("Common Settings Directory:")
        userSettings_formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, commonDir_label)

        commonDir_layout = QtWidgets.QHBoxLayout()
        commonDir_layout.setSpacing(2)

        commonDir_lineEdit = QtWidgets.QLineEdit(self.userSettings_vis)
        commonDir_lineEdit.setText(manager.getSharedSettingsDir())
        commonDir_layout.addWidget(commonDir_lineEdit)

        setCommon_button = QtWidgets.QPushButton(self.userSettings_vis)
        setCommon_button.setText("...")
        commonDir_layout.addWidget(setCommon_button)
        userSettings_formLayout.setLayout(2, QtWidgets.QFormLayout.FieldRole, commonDir_layout)

        # form item 3
        colorCoding_label = QtWidgets.QLabel(self.userSettings_vis)
        colorCoding_label.setText("Color Codes: ")
        userSettings_formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, colorCoding_label)

        colorCoding_formlayout = QtWidgets.QFormLayout(self.userSettings_vis)
        colorCoding_formlayout.setSpacing(2)
        colorCoding_formlayout.setVerticalSpacing(5)
        userSettings_formLayout.setLayout(3, QtWidgets.QFormLayout.FieldRole, colorCoding_formlayout)

        def colorSet(button, niceName):

            color = QtWidgets.QColorDialog.getColor()
            button.setStyleSheet("background-color: %s" % color.name())
            self.allSettingsDict["userSettings"]["newSettings"]["colorCoding"][niceName] = "rgb%s" % str(color.getRgb())
            self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())

        def resetColors():
            try:
                userSettings = self.allSettingsDict.get("userSettings")
                userSettings["colorCoding"] = manager._sceneManagerDefaults["defaultColorCoding"]
                self.allSettingsDict.set("userSettings", userSettings)
            except KeyError:
                self.infoPop(textTitle="Cannot get default database",
                             textHeader="Default Color Coding Database cannot be found")
                return
            for item in self.allSettingsDict["userSettings"]["newSettings"]["colorCoding"].items():
                niceName = item[0]
                color = item[1]
                try:
                    pushbutton = self.findChild(QtWidgets.QPushButton, "cc_%s" % niceName)
                    pushbutton.setStyleSheet("background-color:%s" % color)
                except AttributeError:
                    pass
            self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())

            # self._isSettingsChanged()

        def browseCommonDatabase():
            dlg = QtWidgets.QFileDialog()
            dlg.setFileMode(QtWidgets.QFileDialog.Directory)

            if dlg.exec_():
                # selectedroot = os.path.normpath(unicode(dlg.selectedFiles()[0]))
                selectedroot = os.path.normpath(unicode(dlg.selectedFiles()[0])).encode("utf-8")
                if manager._checkCommonFolder(selectedroot):
                    commonDir_lineEdit.setText(selectedroot)
                else:
                    return
            self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())

            # self._isSettingsChanged()
            return

        colorCoding = self.allSettingsDict.get("userSettings")["colorCoding"]
        for item in colorCoding.items():
            cclabel = QtWidgets.QLabel(self.userSettings_vis)
            if item[0] == "":
                cclabel.setText("      Standalone:  ")
            else:
                cclabel.setText("      %s:  " % item[0])
            ccpushbutton = QtWidgets.QPushButton(self.userSettings_vis)
            ccpushbutton.setObjectName("cc_%s" % item[0])
            ccpushbutton.setStyleSheet("background-color:%s" % item[1])
            ccpushbutton.setMinimumSize(100, 20)

            colorCoding_formlayout.addRow(cclabel, ccpushbutton)
            ccpushbutton.clicked.connect(lambda button=ccpushbutton: colorSet(button, item[0]))

        # niceNameList = self.allSettingsDict["userSettings"]["newSettings"]["colorCoding"].keys()
        # for x in range(len(niceNameList)):
        #     cclabel = QtWidgets.QLabel(self.userSettings_vis)
        #     if niceNameList[x] == "":
        #         cclabel.setText("      Standalone:  ")
        #     else:
        #         cclabel.setText("      %s:  " % niceNameList[x])
        #     print "AA", niceNameList
        #     colorCoding_formlayout.setWidget(x, QtWidgets.QFormLayout.LabelRole, cclabel)
        #
        #     ccpushbutton = QtWidgets.QPushButton(self.userSettings_vis)
        #     ccpushbutton.setObjectName("cc_%s" % niceNameList[x])
        #     ccpushbutton.setStyleSheet("background-color:%s" % manager.getColorCoding(niceNameList[x]))
        #     ccpushbutton.setMinimumSize(100, 20)
        #     colorCoding_formlayout.setWidget(x, QtWidgets.QFormLayout.FieldRole, ccpushbutton)
        #     ccpushbutton.clicked.connect(lambda item=ccpushbutton: colorSet(item, niceNameList[x]))

        ccReset_button = QtWidgets.QPushButton(self.userSettings_vis)
        ccReset_button.setText("Reset Colors")
        ccReset_button.setFixedSize(100, 20)
        colorCoding_formlayout.setWidget((len(colorCoding.items())) + 1, QtWidgets.QFormLayout.FieldRole, ccReset_button)
        # colorCoding_formlayout.setWidget((len(niceNameList)) + 1, QtWidgets.QFormLayout.FieldRole, ccReset_button)

        # end of form

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        userSettings_Layout.addItem(spacerItem)
        self.contentsMaster_layout.addWidget(self.userSettings_vis)
        print "DEBUGwe"

        # SIGNALS USER SETTINGS
        # ---------------------
        ccReset_button.clicked.connect(resetColors)
        setCommon_button.clicked.connect(browseCommonDatabase)

        globalFavorites_radiobutton.clicked.connect(updateDictionary)
        localFavorites_radiobutton.clicked.connect(updateDictionary)
        # commonDir_lineEdit.textChanged.connect(updateDictionary)
        commonDir_lineEdit.editingFinished.connect(updateDictionary)



    def _projectSettingsContent(self):
        manager = self._getManager()
        settings = self.allSettingsDict.get("projectSettings")

        def updateDictionary():
            settings["Resolution"] = [resolutionX_spinBox.value(), resolutionY_spinBox.value()]
            settings["FPS"] = float(fps_comboBox.currentText())

            self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())

        projectSettings_Layout = QtWidgets.QVBoxLayout(self.projectSettings_vis)
        projectSettings_Layout.setSpacing(0)

        h1_horizontalLayout = QtWidgets.QHBoxLayout(self.projectSettings_vis)
        h1_label = QtWidgets.QLabel(self.projectSettings_vis)
        h1_label.setText("Project Settings")
        h1_label.setFont(self.headerAFont)
        h1_horizontalLayout.addWidget(h1_label)
        projectSettings_Layout.addLayout(h1_horizontalLayout)

        projectSettings_formLayout = QtWidgets.QFormLayout(self.projectSettings_vis)
        projectSettings_formLayout.setSpacing(2)
        projectSettings_formLayout.setVerticalSpacing(5)
        # projectSettings_formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        # projectSettings_formLayout.setLabelAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        # projectSettings_formLayout.setFormAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        projectSettings_formLayout.setContentsMargins(-1, 15, -1, -1)

        resolution_label = QtWidgets.QLabel(self.projectSettings_vis)
        resolution_label.setText("Resolution: ")
        resolution_label.setObjectName("resolution_label")

        horizontalLayout = QtWidgets.QHBoxLayout()
        horizontalLayout.setObjectName("horizontalLayout")

        resolutionX_spinBox = QtWidgets.QSpinBox(self.projectSettings_vis)
        resolutionX_spinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        horizontalLayout.addWidget(resolutionX_spinBox)
        resolutionX_spinBox.setRange(1, 99999)
        resolutionX_spinBox.setValue(settings["Resolution"][0])

        resolutionY_spinBox = QtWidgets.QSpinBox(self.projectSettings_vis)
        resolutionY_spinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        horizontalLayout.addWidget(resolutionY_spinBox)
        resolutionY_spinBox.setRange(1, 99999)
        resolutionY_spinBox.setValue(settings["Resolution"][1])

        projectSettings_formLayout.addRow(resolution_label, horizontalLayout)

        fps_label = QtWidgets.QLabel(self.projectSettings_vis)
        fps_label.setText("FPS: ")
        fps_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)

        fps_comboBox = QtWidgets.QComboBox(self.projectSettings_vis)
        # fps_comboBox.setMaximumSize(QtCore.QSize(60, 16777215))
        fps_comboBox.addItems(manager.fpsList)
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

        cmdButtons_layout = QtWidgets.QVBoxLayout(self.projectSettings_vis)
        cmdButtons_layout.setContentsMargins(-1, 15, -1, -1)
        projectSettings_Layout.addLayout(cmdButtons_layout)

        previewSettings_cmdButton = QtWidgets.QCommandLinkButton(self.projectSettings_vis)
        previewSettings_cmdButton.setText("Preview Settings")
        cmdButtons_layout.addWidget(previewSettings_cmdButton)

        categories_cmdButton = QtWidgets.QCommandLinkButton(self.projectSettings_vis)
        categories_cmdButton.setText("Categories")
        cmdButtons_layout.addWidget(categories_cmdButton)

        importExportOptions_cmdButton = QtWidgets.QCommandLinkButton(self.projectSettings_vis)
        importExportOptions_cmdButton.setText("Import/Export Options")
        cmdButtons_layout.addWidget(importExportOptions_cmdButton)

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        projectSettings_Layout.addItem(spacerItem)
        self.contentsMaster_layout.addWidget(self.projectSettings_vis)

        # SIGNALS
        resolutionX_spinBox.valueChanged.connect(updateDictionary)
        resolutionY_spinBox.valueChanged.connect(updateDictionary)
        fps_comboBox.currentIndexChanged.connect(updateDictionary)

        previewSettings_cmdButton.clicked.connect(lambda: self.settingsMenu_treeWidget.setCurrentItem(self.previewSettings_item))
        categories_cmdButton.clicked.connect(lambda: self.settingsMenu_treeWidget.setCurrentItem(self.categories_item))
        importExportOptions_cmdButton.clicked.connect(lambda: self.settingsMenu_treeWidget.setCurrentItem(self.importExport_item))

    def _previewSettingsContent_maya(self):
        manager = self._getManager()
        settings = self.allSettingsDict.get("preview_maya")
        def updateMayaCodecs():
            codecList = manager.getFormatsAndCodecs()[self.format_Maya_comboBox.currentText()]
            self.codec_Maya_comboBox.clear()
            self.codec_Maya_comboBox.addItems(codecList)

        previewSettings_MAYA_Layout = QtWidgets.QVBoxLayout(self.previewSettings_vis)
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
        h1_label = QtWidgets.QLabel(self.previewSettings_vis)
        h1_label.setText("Maya Playblast Settings")
        h1_label.setFont(self.headerAFont)
        h1_horizontalLayout.addWidget(h1_label)
        previewSettings_MAYA_Layout.addLayout(h1_horizontalLayout)

        ## VIDEO PROPERTIES
        h1_s1_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_s1_horizontalLayout.setContentsMargins(-1, 15, -1, -1)
        h1_s1_label = QtWidgets.QLabel(self.previewSettings_vis)
        h1_s1_label.setText("Video Properties  ")
        h1_s1_label.setFont(self.headerBFont)
        h1_s1_horizontalLayout.addWidget(h1_s1_label)

        h1_s1_line = QtWidgets.QLabel(self.previewSettings_vis)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        h1_s1_line.setSizePolicy(sizePolicy)
        h1_s1_line.setStyleSheet("background-color: gray;")
        h1_s1_horizontalLayout.addWidget(h1_s1_line)
        try: h1_s1_line.setMargin(0)
        except AttributeError: pass
        h1_s1_line.setIndent(0)
        h1_s1_line.setMaximumHeight(1)
        previewSettings_MAYA_Layout.addLayout(h1_s1_horizontalLayout)

        h1_s2_horizontalLayout = QtWidgets.QHBoxLayout(self.previewSettings_vis)
        h1_s2_horizontalLayout.setContentsMargins(20, 10, -1, -1)
        h1_s2_horizontalLayout.setSpacing(6)

        videoProperties_formLayout = QtWidgets.QFormLayout(self.previewSettings_vis)
        h1_s2_horizontalLayout.addLayout(videoProperties_formLayout)

        self.convertMP4_Maya_chb = QtWidgets.QCheckBox(self.previewSettings_vis)
        self.convertMP4_Maya_chb.setText("Convert To MP4")
        self.convertMP4_Maya_chb.setMinimumSize(QtCore.QSize(100, 0))
        self.convertMP4_Maya_chb.setLayoutDirection(QtCore.Qt.LeftToRight)
        # videoProperties_formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.convertMP4_Maya_chb)
        videoProperties_formLayout.addRow(self.convertMP4_Maya_chb)
        if manager.currentPlatform is not "Windows":
            self.convertMP4_Maya_chb.setChecked(False)
            self.convertMP4_Maya_chb.setEnabled(False)
        else:
            try:
                self.convertMP4_Maya_chb.setChecked(settings["ConvertMP4"])
            except KeyError:
                self.convertMP4_Maya_chb.setChecked(True)

        crf_Maya_label = QtWidgets.QLabel(self.previewSettings_vis)
        crf_Maya_label.setText("CRF Value (0-51)")

        self.crf_Maya_spinBox = QtWidgets.QSpinBox(self.previewSettings_vis)
        self.crf_Maya_spinBox.setMinimumWidth(50)
        self.crf_Maya_spinBox.setMinimum(0)
        self.crf_Maya_spinBox.setMaximum(51)
        self.crf_Maya_spinBox.setValue(settings["CrfValue"])
        videoProperties_formLayout.addRow(crf_Maya_label, self.crf_Maya_spinBox)

        format_label = QtWidgets.QLabel(self.previewSettings_vis)
        format_label.setText("Format: ")
        self.format_Maya_comboBox = QtWidgets.QComboBox(self.previewSettings_vis)
        videoProperties_formLayout.addRow(format_label, self.format_Maya_comboBox)

        formatsAndCodecs = manager.getFormatsAndCodecs()
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

        codec_label = QtWidgets.QLabel(self.previewSettings_vis)
        codec_label.setText("Codec: ")
        self.codec_Maya_comboBox = QtWidgets.QComboBox(self.previewSettings_vis)
        videoProperties_formLayout.addRow(codec_label, self.codec_Maya_comboBox)

        if not formatsAndCodecs:
            self.codec_Maya_comboBox.setEnabled(False)
        else:
            updateMayaCodecs()

        self.format_Maya_comboBox.currentIndexChanged.connect(updateMayaCodecs)

        quality_label = QtWidgets.QLabel(self.previewSettings_vis)
        quality_label.setText("Quality: ")
        self.quality_Maya_spinBox = QtWidgets.QSpinBox(self.previewSettings_vis)
        self.quality_Maya_spinBox.setMinimumWidth(50)
        self.quality_Maya_spinBox.setMinimum(1)
        self.quality_Maya_spinBox.setMaximum(100)
        self.quality_Maya_spinBox.setValue(settings["Quality"])
        videoProperties_formLayout.addRow(quality_label, self.quality_Maya_spinBox)

        resolution_label = QtWidgets.QLabel(self.previewSettings_vis)
        resolution_label.setText("Resolution: ")
        resolution_horizontalLayout = QtWidgets.QHBoxLayout(self.previewSettings_vis)
        self.resX_Maya_spinBox = QtWidgets.QSpinBox(self.previewSettings_vis)
        self.resX_Maya_spinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.resX_Maya_spinBox.setMinimum(1)
        self.resX_Maya_spinBox.setMaximum(99999)
        self.resX_Maya_spinBox.setValue(settings["Resolution"][0])
        resolution_horizontalLayout.addWidget(self.resX_Maya_spinBox)
        self.resY_Maya_spinBox = QtWidgets.QSpinBox(self.previewSettings_vis)
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
        h1_s3_label = QtWidgets.QLabel(self.previewSettings_vis)
        h1_s3_label.setText("Viewport Options  ")
        h1_s3_label.setFont(self.headerBFont)
        h1_s3_horizontalLayout.addWidget(h1_s3_label)

        h1_s3_line = QtWidgets.QLabel(self.previewSettings_vis)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        h1_s3_line.setSizePolicy(sizePolicy)
        h1_s3_line.setStyleSheet("background-color: gray;")
        h1_s3_horizontalLayout.addWidget(h1_s3_line)
        try: h1_s3_line.setMargin(0)
        except AttributeError: pass
        h1_s3_line.setIndent(0)
        h1_s3_line.setMaximumHeight(1)
        previewSettings_MAYA_Layout.addLayout(h1_s3_horizontalLayout)

        h1_s4_horizontalLayout = QtWidgets.QHBoxLayout(self.previewSettings_vis)
        h1_s4_horizontalLayout.setContentsMargins(20, 10, -1, -1)

        viewportOptions_gridLayout = QtWidgets.QGridLayout(self.previewSettings_vis)
        # viewportOptions_gridLayout.setContentsMargins(-1, 15, -1, -1)
        h1_s4_horizontalLayout.addLayout(viewportOptions_gridLayout)

        self.polygonOnly_Maya_chb = QtWidgets.QCheckBox(self.previewSettings_vis)
        self.polygonOnly_Maya_chb.setText("Polygon Only")
        viewportOptions_gridLayout.addWidget(self.polygonOnly_Maya_chb, 0, 0)
        self.polygonOnly_Maya_chb.setChecked(settings["PolygonOnly"])

        self.showGrid_Maya_chb = QtWidgets.QCheckBox(self.previewSettings_vis)
        self.showGrid_Maya_chb.setText("Show Grid")
        viewportOptions_gridLayout.addWidget(self.showGrid_Maya_chb, 0, 1)
        self.showGrid_Maya_chb.setChecked(settings["ShowGrid"])

        self.clearSelection_Maya_chb = QtWidgets.QCheckBox(self.previewSettings_vis)
        self.clearSelection_Maya_chb.setText("Clear Selection")
        viewportOptions_gridLayout.addWidget(self.clearSelection_Maya_chb, 1, 0)
        self.clearSelection_Maya_chb.setChecked(settings["ClearSelection"])

        self.displayTextures_Maya_chb = QtWidgets.QCheckBox(self.previewSettings_vis)
        self.displayTextures_Maya_chb.setText("Display Textures")
        viewportOptions_gridLayout.addWidget(self.displayTextures_Maya_chb, 1, 1)
        self.displayTextures_Maya_chb.setChecked(settings["DisplayTextures"])

        self.wireOnShaded_Maya_chb = QtWidgets.QCheckBox(self.previewSettings_vis)
        self.wireOnShaded_Maya_chb.setText("Wire On Shaded")
        viewportOptions_gridLayout.addWidget(self.wireOnShaded_Maya_chb, 2, 0)
        self.wireOnShaded_Maya_chb.setChecked(settings["WireOnShaded"])

        self.useDefaultMaterial_Maya_chb = QtWidgets.QCheckBox(self.previewSettings_vis)
        self.useDefaultMaterial_Maya_chb.setText("Use Default Material")
        viewportOptions_gridLayout.addWidget(self.useDefaultMaterial_Maya_chb, 2, 1)
        self.useDefaultMaterial_Maya_chb.setChecked(settings["UseDefaultMaterial"])


        previewSettings_MAYA_Layout.addLayout(h1_s4_horizontalLayout)

        ## HUD OPTIONS
        h1_s5_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_s5_horizontalLayout.setContentsMargins(-1, 30, -1, -1)
        h1_s5_label = QtWidgets.QLabel(self.previewSettings_vis)
        h1_s5_label.setText("Heads Up Display Options  ")
        h1_s5_label.setFont(self.headerBFont)
        h1_s5_horizontalLayout.addWidget(h1_s5_label)

        h1_s5_line = QtWidgets.QLabel(self.previewSettings_vis)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        h1_s5_line.setSizePolicy(sizePolicy)
        h1_s5_line.setStyleSheet("background-color: gray;")
        h1_s5_horizontalLayout.addWidget(h1_s5_line)
        try: h1_s5_line.setMargin(0)
        except AttributeError: pass
        h1_s5_line.setIndent(0)
        h1_s5_line.setMaximumHeight(1)
        previewSettings_MAYA_Layout.addLayout(h1_s5_horizontalLayout)

        h1_s6_horizontalLayout = QtWidgets.QHBoxLayout(self.previewSettings_vis)
        h1_s6_horizontalLayout.setContentsMargins(20, 10, -1, 30)

        hudOptions_gridLayout = QtWidgets.QGridLayout(self.previewSettings_vis)
        h1_s6_horizontalLayout.addLayout(hudOptions_gridLayout)

        self.frameNumber_Maya_chb = QtWidgets.QCheckBox(self.previewSettings_vis)
        self.frameNumber_Maya_chb.setText("Frame Number")
        hudOptions_gridLayout.addWidget(self.frameNumber_Maya_chb, 0, 0)
        self.frameNumber_Maya_chb.setChecked(settings["ShowFrameNumber"])

        self.category_Maya_chb = QtWidgets.QCheckBox(self.previewSettings_vis)
        self.category_Maya_chb.setText("Category")
        hudOptions_gridLayout.addWidget(self.category_Maya_chb, 0, 1)
        self.category_Maya_chb.setChecked(settings["ShowCategory"])


        self.sceneName_Maya_chb = QtWidgets.QCheckBox(self.previewSettings_vis)
        self.sceneName_Maya_chb.setText("Scene Name")
        hudOptions_gridLayout.addWidget(self.sceneName_Maya_chb, 1, 0)
        self.sceneName_Maya_chb.setChecked(settings["ShowSceneName"])


        self.fps_Maya_chb = QtWidgets.QCheckBox(self.previewSettings_vis)
        self.fps_Maya_chb.setText("FPS")
        hudOptions_gridLayout.addWidget(self.fps_Maya_chb, 1, 1)
        self.fps_Maya_chb.setChecked(settings["ShowFPS"])


        self.frameRange_Maya_chb = QtWidgets.QCheckBox(self.previewSettings_vis)
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
        manager = self._getManager()
        # settings = self.allSettingsDict["preview_max"]["oldSettings"]
        settings = self.allSettingsDict.get("preview_max")

        previewSettings_MAX_Layout = QtWidgets.QVBoxLayout(self.previewSettings_vis)
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
        h1_horizontalLayout = QtWidgets.QHBoxLayout(self.previewSettings_vis)
        # h1_horizontalLayout.setContentsMargins(-1, -1, -1, 10)
        h1_label = QtWidgets.QLabel(self.previewSettings_vis)
        h1_label.setText("3ds Max Preview Animation Settings")
        h1_label.setFont(self.headerAFont)
        h1_horizontalLayout.addWidget(h1_label)
        previewSettings_MAX_Layout.addLayout(h1_horizontalLayout)

        ## VIDEO PROPERTIES
        h1_s1_horizontalLayout = QtWidgets.QHBoxLayout(self.previewSettings_vis)
        h1_s1_horizontalLayout.setContentsMargins(-1, 15, -1, -1)
        h1_s1_label = QtWidgets.QLabel(self.previewSettings_vis)
        h1_s1_label.setText("Video Properties  ")
        h1_s1_label.setFont(self.headerBFont)
        h1_s1_horizontalLayout.addWidget(h1_s1_label)

        h1_s1_line = QtWidgets.QLabel(self.previewSettings_vis)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        h1_s1_line.setSizePolicy(sizePolicy)
        h1_s1_line.setStyleSheet("background-color: gray;")
        h1_s1_horizontalLayout.addWidget(h1_s1_line)
        try: h1_s1_line.setMargin(0)
        except AttributeError: pass
        h1_s1_line.setIndent(0)
        h1_s1_line.setMaximumHeight(1)
        previewSettings_MAX_Layout.addLayout(h1_s1_horizontalLayout)

        h1_s2_horizontalLayout = QtWidgets.QHBoxLayout(self.previewSettings_vis)
        h1_s2_horizontalLayout.setContentsMargins(20, 10, -1, -1)
        h1_s2_horizontalLayout.setSpacing(6)

        videoProperties_formLayout = QtWidgets.QFormLayout(self.previewSettings_vis)
        # videoProperties_formLayout.setContentsMargins(10, -1, -1, -1)
        h1_s2_horizontalLayout.addLayout(videoProperties_formLayout)

        self.convertMP4_Max_chb = QtWidgets.QCheckBox(self.previewSettings_vis)
        self.convertMP4_Max_chb.setText("Convert To MP4")
        self.convertMP4_Max_chb.setMinimumSize(QtCore.QSize(100, 0))
        self.convertMP4_Max_chb.setLayoutDirection(QtCore.Qt.LeftToRight)
        # videoProperties_formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.convertMP4_Max_chb)
        videoProperties_formLayout.addRow(self.convertMP4_Max_chb)
        if manager.currentPlatform is not "Windows":
            self.convertMP4_Max_chb.setChecked(False)
            self.convertMP4_Max_chb.setEnabled(False)
        else:
            try:
                self.convertMP4_Max_chb.setChecked(settings["ConvertMP4"])
            except KeyError:
                self.convertMP4_Max_chb.setChecked(True)

        crf_Max_label = QtWidgets.QLabel(self.previewSettings_vis)
        crf_Max_label.setText("CRF Value (0-51)")

        self.crf_Max_spinBox = QtWidgets.QSpinBox(self.previewSettings_vis)
        self.crf_Max_spinBox.setMinimumWidth(50)
        self.crf_Max_spinBox.setMinimum(0)
        self.crf_Max_spinBox.setMaximum(51)
        self.crf_Max_spinBox.setValue(settings["CrfValue"])
        videoProperties_formLayout.addRow(crf_Max_label, self.crf_Max_spinBox)

        resolution_label = QtWidgets.QLabel(self.previewSettings_vis)
        resolution_label.setText("Resolution: ")
        resolution_horizontalLayout = QtWidgets.QHBoxLayout(self.previewSettings_vis)
        self.resX_Max_spinBox = QtWidgets.QSpinBox(self.previewSettings_vis)
        self.resX_Max_spinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.resX_Max_spinBox.setMinimum(1)
        self.resX_Max_spinBox.setMaximum(99999)
        self.resX_Max_spinBox.setValue(settings["Resolution"][0])
        resolution_horizontalLayout.addWidget(self.resX_Max_spinBox)
        self.resY_Max_spinBox = QtWidgets.QSpinBox(self.previewSettings_vis)
        self.resY_Max_spinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.resY_Max_spinBox.setMinimum(1)
        self.resY_Max_spinBox.setMaximum(99999)
        self.resY_Max_spinBox.setValue(settings["Resolution"][1])
        resolution_horizontalLayout.addWidget(self.resY_Max_spinBox)
        videoProperties_formLayout.addRow(resolution_label, resolution_horizontalLayout)

        previewSettings_MAX_Layout.addLayout(h1_s2_horizontalLayout)

        ## VIEWPORT OPTIONS
        h1_s3_horizontalLayout = QtWidgets.QHBoxLayout(self.previewSettings_vis)
        h1_s3_horizontalLayout.setContentsMargins(-1, 30, -1, -1)
        h1_s3_label = QtWidgets.QLabel(self.previewSettings_vis)
        h1_s3_label.setText("Viewport Options  ")
        h1_s3_label.setFont(self.headerBFont)
        h1_s3_horizontalLayout.addWidget(h1_s3_label)

        h1_s3_line = QtWidgets.QLabel(self.previewSettings_vis)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        h1_s3_line.setSizePolicy(sizePolicy)
        h1_s3_line.setStyleSheet("background-color: gray;")
        h1_s3_horizontalLayout.addWidget(h1_s3_line)
        try: h1_s3_line.setMargin(0)
        except AttributeError: pass
        h1_s3_line.setIndent(0)
        h1_s3_line.setMaximumHeight(1)
        previewSettings_MAX_Layout.addLayout(h1_s3_horizontalLayout)

        h1_s4_horizontalLayout = QtWidgets.QHBoxLayout(self.previewSettings_vis)
        h1_s4_horizontalLayout.setContentsMargins(20, 10, -1, -1)

        viewportOptions_gridLayout = QtWidgets.QGridLayout(self.previewSettings_vis)
        h1_s4_horizontalLayout.addLayout(viewportOptions_gridLayout)

        self.polygonOnly_Max_chb = QtWidgets.QCheckBox(self.previewSettings_vis)
        self.polygonOnly_Max_chb.setText("Polygon Only")
        viewportOptions_gridLayout.addWidget(self.polygonOnly_Max_chb, 0, 0)
        self.polygonOnly_Max_chb.setChecked(settings["PolygonOnly"])

        self.showGrid_Max_chb = QtWidgets.QCheckBox(self.previewSettings_vis)
        self.showGrid_Max_chb.setText("Show Grid")
        viewportOptions_gridLayout.addWidget(self.showGrid_Max_chb, 0, 1)
        self.showGrid_Max_chb.setChecked(settings["ShowGrid"])

        self.clearSelection_Max_chb = QtWidgets.QCheckBox(self.previewSettings_vis)
        self.clearSelection_Max_chb.setText("Clear Selection")
        viewportOptions_gridLayout.addWidget(self.clearSelection_Max_chb, 1, 0)
        self.clearSelection_Max_chb.setChecked(settings["ClearSelection"])

        self.wireOnShaded_Max_chb = QtWidgets.QCheckBox(self.previewSettings_vis)
        self.wireOnShaded_Max_chb.setText("Wire On Shaded")
        viewportOptions_gridLayout.addWidget(self.wireOnShaded_Max_chb, 1, 1)
        self.wireOnShaded_Max_chb.setChecked(settings["WireOnShaded"])

        previewSettings_MAX_Layout.addLayout(h1_s4_horizontalLayout)

        ## HUD OPTIONS
        h1_s5_horizontalLayout = QtWidgets.QHBoxLayout(self.previewSettings_vis)
        h1_s5_horizontalLayout.setContentsMargins(-1, 30, -1, -1)
        h1_s5_label = QtWidgets.QLabel(self.previewSettings_vis)
        h1_s5_label.setText("Heads Up Display Options  ")
        h1_s5_label.setFont(self.headerBFont)
        h1_s5_horizontalLayout.addWidget(h1_s5_label)

        h1_s5_line = QtWidgets.QLabel(self.previewSettings_vis)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        h1_s5_line.setSizePolicy(sizePolicy)
        h1_s5_line.setStyleSheet("background-color: gray;")
        h1_s5_horizontalLayout.addWidget(h1_s5_line)
        try: h1_s5_line.setMargin(0)
        except AttributeError: pass
        h1_s5_line.setIndent(0)
        h1_s5_line.setMaximumHeight(1)
        previewSettings_MAX_Layout.addLayout(h1_s5_horizontalLayout)

        h1_s6_horizontalLayout = QtWidgets.QHBoxLayout(self.previewSettings_vis)
        h1_s6_horizontalLayout.setContentsMargins(20, 10, -1, -1)

        hudOptions_gridLayout = QtWidgets.QGridLayout(self.previewSettings_vis)
        h1_s6_horizontalLayout.addLayout(hudOptions_gridLayout)

        self.frameNumber_Max_chb = QtWidgets.QCheckBox(self.previewSettings_vis)
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

    def _categoriesContent(self):
        manager = self._getManager()
        categorySwList = [key for key in self.allSettingsDict.listNames() if key.startswith("categories")]

        categories_Layout = QtWidgets.QVBoxLayout(self.categories_vis)
        categories_Layout.setSpacing(0)

        h1_horizontalLayout = QtWidgets.QHBoxLayout(self.categories_vis)
        h1_label = QtWidgets.QLabel(self.categories_vis)
        h1_label.setText("Add/Remove Categories")
        h1_label.setFont(self.headerAFont)
        h1_horizontalLayout.addWidget(h1_label)
        categories_Layout.addLayout(h1_horizontalLayout)

        h1_s1_layout = QtWidgets.QVBoxLayout(self.categories_vis)
        h1_s1_layout.setContentsMargins(-1, 15, -1, -1)

        swTabs = QtWidgets.QTabWidget(self.categories_vis)
        swTabs.setMaximumSize(QtCore.QSize(16777215, 167777))
        swTabs.setTabPosition(QtWidgets.QTabWidget.North)
        swTabs.setElideMode(QtCore.Qt.ElideNone)
        swTabs.setUsesScrollButtons(False)

        def onRemove(settingKey, listWidget):
            row = listWidget.currentRow()
            if row == -1:
                return
            trashCategory = listWidget.currentItem().text()
            categories = self.allSettingsDict.get(settingKey)
            ## check if this is the last category
            if len(categories) == 1:
                self.infoPop(textTitle="Cannot Remove Category",
                             textHeader="Last Category cannot be removed")

            ## Check if this category is REALLY trash
            niceName=settingKey.replace("categories_", "")
            dbPath = os.path.normpath(os.path.join(manager._pathsDict["masterDir"], self.softwareDB[niceName]["databaseDir"]))

            if manager.isCategoryTrash(trashCategory, dbPath=dbPath):
                categories.remove(trashCategory)
                listWidget.clear()
                listWidget.addItems(categories)
            else:
                self.infoPop(textTitle="Cannot Remove Category",
                             textHeader="%s Category is not empty. Aborting..." % trashCategory)

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
                newCategory = categoryName_lineEdit.text()
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

                # pprint.pprint(self.allSettingsDict)

            buttonBox.accepted.connect(addCategory)
            buttonBox.rejected.connect(addCategory_Dialog.reject)

        for cat in sorted(categorySwList):
            tabWidget = QtWidgets.QWidget(self.categories_vis)
            horizontalLayout = QtWidgets.QHBoxLayout(tabWidget)
            categories_listWidget = QtWidgets.QListWidget(self.categories_vis)
            horizontalLayout.addWidget(categories_listWidget)

            verticalLayout = QtWidgets.QVBoxLayout(self.categories_vis)
            verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)

            add_pushButton = QtWidgets.QPushButton(self.categories_vis)
            add_pushButton.setText(("Add..."))
            verticalLayout.addWidget(add_pushButton)

            remove_pushButton = QtWidgets.QPushButton(self.categories_vis)
            remove_pushButton.setText(("Remove"))
            verticalLayout.addWidget(remove_pushButton)

            spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            verticalLayout.addItem(spacerItem)

            horizontalLayout.addLayout(verticalLayout)

            swTabs.addTab(tabWidget, cat.replace("categories_", ""))

            categories_listWidget.addItems(self.allSettingsDict[cat]["newSettings"])
            add_pushButton.clicked.connect(lambda settingKey=cat, listWidget=categories_listWidget: onAdd(settingKey, listWidget))
            # add_pushButton.clicked.connect(lambda: onAdd(cat, categories_listWidget))
            remove_pushButton.clicked.connect(lambda settingKey=cat, listWidget=categories_listWidget: onRemove(settingKey, listWidget))
            # remove_pushButton.clicked.connect(lambda: onRemove(cat, categories_listWidget))


        h1_s1_layout.addWidget(swTabs)
        categories_Layout.addLayout(h1_s1_layout)


        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        categories_Layout.addItem(spacerItem)
        self.contentsMaster_layout.addWidget(self.categories_vis)

    def _importExportContent(self):
        manager = self._getManager()
        sw = manager.swName.lower()
        exportSettings = self.allSettingsDict.get("exportSettings")
        importSettings = self.allSettingsDict.get("importSettings")

        def updateImportDictionary(sw, key, value):
            importSettings[sw][key]=value
            print sw, key, importSettings[sw][key]
            pass

        def updateExportDictionary(sw, key, value):
            exportSettings[sw][key] = value
            print sw, key, exportSettings[sw][key]
            pass

        importExport_Layout = QtWidgets.QVBoxLayout(self.importExportOptions_vis)
        importExport_Layout.setSpacing(0)

        h1_horizontalLayout = QtWidgets.QHBoxLayout(self.importExportOptions_vis)
        h1_label = QtWidgets.QLabel(self.importExportOptions_vis)
        h1_label.setText("Import/Export Geometry Settings")
        h1_label.setFont(self.headerAFont)
        h1_horizontalLayout.addWidget(h1_label)
        importExport_Layout.addLayout(h1_horizontalLayout)

        h1_s1_layout = QtWidgets.QVBoxLayout(self.importExportOptions_vis)
        h1_s1_layout.setContentsMargins(-1, 15, -1, -1)

        softwaresTabWidget = QtWidgets.QTabWidget(self.importExportOptions_vis)
        softwaresTabWidget.setMaximumSize(QtCore.QSize(16777215, 167777))
        softwaresTabWidget.setTabPosition(QtWidgets.QTabWidget.North)
        softwaresTabWidget.setElideMode(QtCore.Qt.ElideNone)
        softwaresTabWidget.setUsesScrollButtons(False)

        if sw == "maya" or sw == "":
            mayaTab = QtWidgets.QWidget(self.importExportOptions_vis)
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
                obj_seperator.setStyleSheet("background-color: rgb(255,141,28,60);")
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
                obj_import_layout.addLayout(obj_import_formlayout)

                LegacyVertexOrdering_chb = QtWidgets.QCheckBox()
                LegacyVertexOrdering_chb.setText("Legacy Vertex Ordering")
                LegacyVertexOrdering_chb.setObjectName("LegacyVertexOrdering")
                LegacyVertexOrdering_chb.setChecked(bool(int(importSettings["objImportMaya"]["LegacyVertexOrdering"].replace("lo=", ""))))
                obj_import_formlayout.addRow(LegacyVertexOrdering_chb)
                LegacyVertexOrdering_chb.stateChanged.connect(
                    lambda state: updateImportDictionary("objImportMaya", "LegacyVertexOrdering", "lo=%s" %int(bool(state))))

                MultipleObjects_chb = QtWidgets.QCheckBox()
                MultipleObjects_chb.setText("Multiple Objects")
                MultipleObjects_chb.setObjectName("MultipleObjects")
                MultipleObjects_chb.setChecked(bool(int(importSettings["objImportMaya"]["MultipleObjects"].replace("mo=", ""))))
                obj_import_formlayout.addRow(MultipleObjects_chb)
                # MultipleObjects_chb.stateChanged.connect(lambda state=MultipleObjects_chb.isChecked():
                #                                               updateImportDictionary("objImportMaya", "MultipleObjects", "lo=%s" %int(bool(state))))
                MultipleObjects_chb.stateChanged.connect(
                    lambda state: updateImportDictionary("objImportMaya", "MultipleObjects", "lo=%s" % int(bool(state))))

                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                obj_import_layout.addItem(spacerItem)

                ## MAYA OBJ EXPORT WIDGETS
                obj_export_label = QtWidgets.QLabel()
                obj_export_label.setText("Obj Export Settings")
                obj_export_label.setFont(self.headerBFont)
                obj_export_layout.addWidget(obj_export_label)

                obj_export_formlayout = QtWidgets.QFormLayout()
                obj_export_layout.addLayout(obj_export_formlayout)

                normals_chb = QtWidgets.QCheckBox()
                normals_chb.setText("Normals")
                normals_chb.setObjectName("normals")
                obj_export_formlayout.addRow(normals_chb)
                normals_chb.setChecked(bool(int(exportSettings["objExportMaya"]["normals"])))
                normals_chb.stateChanged.connect(
                    lambda state: updateExportDictionary("objExportMaya", "normals", "%s" %int(bool(state))))

                materials_chb = QtWidgets.QCheckBox()
                materials_chb.setText("Materials")
                materials_chb.setObjectName("materials")
                obj_export_formlayout.addRow(materials_chb)
                materials_chb.setChecked(bool(int(exportSettings["objExportMaya"]["materials"])))
                materials_chb.stateChanged.connect(
                    lambda state: updateExportDictionary("objExportMaya", "materials", "%s" %int(bool(state))))

                ptgroups_chb = QtWidgets.QCheckBox()
                ptgroups_chb.setText("Point Groups")
                ptgroups_chb.setObjectName("ptgroups")
                obj_export_formlayout.addRow(ptgroups_chb)
                ptgroups_chb.setChecked(bool(int(exportSettings["objExportMaya"]["ptgroups"])))
                ptgroups_chb.stateChanged.connect(
                    lambda state: updateExportDictionary("objExportMaya", "ptgroups", "%s" % int(bool(state))))

                groups_chb = QtWidgets.QCheckBox()
                groups_chb.setText("Groups")
                groups_chb.setObjectName("groups")
                obj_export_formlayout.addRow(groups_chb)
                groups_chb.setChecked(bool(int(exportSettings["objExportMaya"]["groups"])))
                groups_chb.stateChanged.connect(
                    lambda state: updateExportDictionary("objExportMaya", "groups", "%s" % int(bool(state))))

                smoothing_chb = QtWidgets.QCheckBox()
                smoothing_chb.setText("Smoothing")
                smoothing_chb.setObjectName("smoothing")
                obj_export_formlayout.addRow(smoothing_chb)
                smoothing_chb.setChecked(bool(int(exportSettings["objExportMaya"]["smoothing"])))
                smoothing_chb.stateChanged.connect(
                    lambda state: updateExportDictionary("objExportMaya", "smoothing", "%s" % int(bool(state))))

                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                obj_export_layout.addItem(spacerItem)

            ## MAYA FBX
            ## --------
            def _maya_fbx():
                fbx_horizontal_layout = QtWidgets.QHBoxLayout(fbxTab)
                fbx_import_layout = QtWidgets.QVBoxLayout()
                fbx_seperator = QtWidgets.QLabel()
                fbx_seperator.setStyleSheet("background-color: rgb(255,141,28,60);")
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
                fbx_import_layout.addLayout(fbx_import_formlayout)

                FBXImportUpAxis_lbl = QtWidgets.QLabel()
                FBXImportUpAxis_lbl.setText("Up Axis: ")
                FBXImportUpAxis_combo = QtWidgets.QComboBox()
                FBXImportUpAxis_combo.addItems(["y", "z"])
                FBXImportUpAxis_combo.setObjectName("FBXImportUpAxis")
                fbx_import_formlayout.addRow(FBXImportUpAxis_lbl, FBXImportUpAxis_combo)
                ffindex = FBXImportUpAxis_combo.findText(importSettings["fbxImportMaya"]["FBXImportUpAxis"], QtCore.Qt.MatchFixedString)
                FBXImportUpAxis_combo.setCurrentIndex(ffindex)
                FBXImportUpAxis_combo.currentIndexChanged.connect(
                    lambda: updateImportDictionary("fbxImportMaya", "FBXImportUpAxis", FBXImportUpAxis_combo.currentText()))

                FBXImportMode_lbl = QtWidgets.QLabel()
                FBXImportMode_lbl.setText("Import Mode")
                FBXImportMode_combo = QtWidgets.QComboBox()
                FBXImportMode_combo.addItems(["add", "merge", "exmerge"])
                FBXImportMode_combo.setObjectName("FBXImportMode")
                fbx_import_formlayout.addRow(FBXImportMode_lbl, FBXImportMode_combo)
                ffindex = FBXImportMode_combo.findText(importSettings["fbxImportMaya"]["FBXImportMode"].replace("-v ", ""),
                                                         QtCore.Qt.MatchFixedString)
                FBXImportMode_combo.setCurrentIndex(ffindex)
                FBXImportMode_combo.currentIndexChanged.connect(
                    lambda: updateImportDictionary("fbxImportMaya", "FBXImportUpAxis", "-v %s" %FBXImportMode_combo.currentText()))

                FBXImportScaleFactor_lbl = QtWidgets.QLabel()
                FBXImportScaleFactor_lbl.setText("Scale Factor")
                FBXImportScaleFactor_spn = QtWidgets.QDoubleSpinBox()
                FBXImportScaleFactor_spn.setObjectName("FBXImportScaleFactor")
                fbx_import_formlayout.addRow(FBXImportScaleFactor_lbl, FBXImportScaleFactor_spn)
                FBXImportScaleFactor_spn.setValue(float(importSettings["fbxImportMaya"]["FBXImportScaleFactor"]))
                FBXImportScaleFactor_spn.valueChanged.connect(
                    lambda: updateImportDictionary("fbxImportMaya", "FBXImportScaleFactor", str(FBXImportScaleFactor_spn.value()))
                )

                FBXImportQuaternion_lbl = QtWidgets.QLabel()
                FBXImportQuaternion_lbl.setText("Treat Quaternions: ")
                FBXImportQuaternion_combo = QtWidgets.QComboBox()
                FBXImportQuaternion_combo.addItems(["quaternion", "euler", "resample"])
                FBXImportQuaternion_combo.setObjectName("FBXImportQuaternion")
                fbx_import_formlayout.addRow(FBXImportQuaternion_lbl, FBXImportQuaternion_combo)

                FBXImportResamplingRateSource_lbl = QtWidgets.QLabel()
                FBXImportResamplingRateSource_lbl.setText("Resampling Rate Source: ")
                FBXImportResamplingRateSource_combo = QtWidgets.QComboBox()
                FBXImportResamplingRateSource_combo.addItems(["Maya", "FBX"])
                FBXImportResamplingRateSource_combo.setObjectName("FBXImportResamplingRateSource")
                fbx_import_formlayout.addRow(FBXImportResamplingRateSource_lbl, FBXImportResamplingRateSource_combo)

                FBXImportMergeBackNullPivots_chb = QtWidgets.QCheckBox()
                FBXImportMergeBackNullPivots_chb.setText("Merge Back Null Pivots")
                FBXImportMergeBackNullPivots_chb.setObjectName("FBXImportMergeBackNullPivots")
                fbx_import_formlayout.addRow(FBXImportMergeBackNullPivots_chb)

                FBXImportSetLockedAttribute_chb = QtWidgets.QCheckBox()
                FBXImportSetLockedAttribute_chb.setText("Set Locked Attribute")
                FBXImportSetLockedAttribute_chb.setObjectName("FBXImportSetLockedAttribute")
                fbx_import_formlayout.addRow(FBXImportSetLockedAttribute_chb)

                FBXImportUnlockNormals_chb = QtWidgets.QCheckBox()
                FBXImportUnlockNormals_chb.setText("Unlock Normals")
                FBXImportUnlockNormals_chb.setObjectName("FBXImportUnlockNormals")
                fbx_import_formlayout.addRow(FBXImportUnlockNormals_chb)

                FBXImportProtectDrivenKeys_chb = QtWidgets.QCheckBox()
                FBXImportProtectDrivenKeys_chb.setText("Protect Driven Keys")
                FBXImportProtectDrivenKeys_chb.setObjectName("FBXImportProtectDrivenKeys")
                fbx_import_formlayout.addRow(FBXImportProtectDrivenKeys_chb)

                FBXImportShapes_chb = QtWidgets.QCheckBox()
                FBXImportShapes_chb.setText("Shapes")
                FBXImportShapes_chb.setObjectName("FBXImportShapes")
                fbx_import_formlayout.addRow(FBXImportShapes_chb)

                FBXImportCameras_chb = QtWidgets.QCheckBox()
                FBXImportCameras_chb.setText("Cameras")
                FBXImportCameras_chb.setObjectName("FBXImportCameras")
                fbx_import_formlayout.addRow(FBXImportCameras_chb)

                FBXImportSetMayaFrameRate_chb = QtWidgets.QCheckBox()
                FBXImportSetMayaFrameRate_chb.setText("Set Maya Frame Rate")
                FBXImportSetMayaFrameRate_chb.setObjectName("FBXImportSetMayaFrameRate")
                fbx_import_formlayout.addRow(FBXImportSetMayaFrameRate_chb)

                FBXImportGenerateLog_chb = QtWidgets.QCheckBox()
                FBXImportGenerateLog_chb.setText("Generate Log")
                FBXImportGenerateLog_chb.setObjectName("FBXImportGenerateLog")
                fbx_import_formlayout.addRow(FBXImportGenerateLog_chb)

                FBXImportConstraints_chb = QtWidgets.QCheckBox()
                FBXImportConstraints_chb.setText("Constraints")
                FBXImportConstraints_chb.setObjectName("FBXImportConstraints")
                fbx_import_formlayout.addRow(FBXImportConstraints_chb)

                FBXImportLights_chb = QtWidgets.QCheckBox()
                FBXImportLights_chb.setText("Lights")
                FBXImportLights_chb.setObjectName("FBXImportLights")
                fbx_import_formlayout.addRow(FBXImportLights_chb)

                FBXImportConvertDeformingNullsToJoint_chb = QtWidgets.QCheckBox()
                FBXImportConvertDeformingNullsToJoint_chb.setText("Convert Nulls to Joints")
                FBXImportConvertDeformingNullsToJoint_chb.setObjectName("FBXImportConvertDeformingNullsToJoint")
                fbx_import_formlayout.addRow(FBXImportConvertDeformingNullsToJoint_chb)

                FBXImportFillTimeline_chb = QtWidgets.QCheckBox()
                FBXImportFillTimeline_chb.setText("Fill Timeline")
                FBXImportFillTimeline_chb.setObjectName("FBXImportFillTimeline")
                fbx_import_formlayout.addRow(FBXImportFillTimeline_chb)

                FBXImportMergeAnimationLayers_chb = QtWidgets.QCheckBox()
                FBXImportMergeAnimationLayers_chb.setText("Merge Animation Layers")
                FBXImportMergeAnimationLayers_chb.setObjectName("FBXImportMergeAnimationLayers")
                fbx_import_formlayout.addRow(FBXImportMergeAnimationLayers_chb)

                FBXImportHardEdges_chb = QtWidgets.QCheckBox()
                FBXImportHardEdges_chb.setText("Hard Edges")
                FBXImportHardEdges_chb.setObjectName("FBXImportHardEdges")
                fbx_import_formlayout.addRow(FBXImportHardEdges_chb)

                FBXImportAxisConversionEnable_chb = QtWidgets.QCheckBox()
                FBXImportAxisConversionEnable_chb.setText("Axis Conversion Enable")
                FBXImportAxisConversionEnable_chb.setObjectName("FBXImportAxisConversionEnable")
                fbx_import_formlayout.addRow(FBXImportAxisConversionEnable_chb)

                FBXImportCacheFile_chb = QtWidgets.QCheckBox()
                FBXImportCacheFile_chb.setText("Cache File")
                FBXImportCacheFile_chb.setObjectName("FBXImportCacheFile")
                fbx_import_formlayout.addRow(FBXImportCacheFile_chb)

                FBXImportSkins_chb = QtWidgets.QCheckBox()
                FBXImportSkins_chb.setText("Skins")
                FBXImportSkins_chb.setObjectName("FBXImportSkins")
                fbx_import_formlayout.addRow(FBXImportSkins_chb)

                FBXImportConvertUnitString_chb = QtWidgets.QCheckBox()
                FBXImportConvertUnitString_chb.setText("Convert Unit String")
                FBXImportConvertUnitString_chb.setObjectName("FBXImportConvertUnitString")
                fbx_import_formlayout.addRow(FBXImportConvertUnitString_chb)

                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                fbx_import_layout.addItem(spacerItem)

                ## MAYA FBX EXPORT WIDGETS
                fbx_export_label = QtWidgets.QLabel()
                fbx_export_label.setText("Fbx Export Settings")
                fbx_export_label.setFont(self.headerBFont)
                fbx_export_layout.addWidget(fbx_export_label)

                fbx_export_formlayout = QtWidgets.QFormLayout()
                fbx_export_layout.addLayout(fbx_export_formlayout)

                FBXExportUpAxis_lbl = QtWidgets.QLabel()
                FBXExportUpAxis_lbl.setText("Up Axis: ")
                FBXExportUpAxis_combo = QtWidgets.QComboBox()
                FBXExportUpAxis_combo.addItems(["y", "z"])
                FBXExportUpAxis_combo.setObjectName("FBXExportUpAxis")
                fbx_export_formlayout.addRow(FBXExportUpAxis_lbl, FBXExportUpAxis_combo)

                FBXExportAxisConversionMethod_lbl = QtWidgets.QLabel()
                FBXExportAxisConversionMethod_lbl.setText("Axis Conversion Method: ")
                FBXExportAxisConversionMethod_combo = QtWidgets.QComboBox()
                FBXExportAxisConversionMethod_combo.addItems(["none", "convertAnimation", "addFbxRoot"])
                FBXExportAxisConversionMethod_combo.setObjectName("FBXExportAxisConversionMethod")
                fbx_export_formlayout.addRow(FBXExportAxisConversionMethod_lbl, FBXExportAxisConversionMethod_combo)

                FBXExportBakeComplexStep_lbl = QtWidgets.QLabel()
                FBXExportBakeComplexStep_lbl.setText("Bake Step: ")
                FBXExportBakeComplexStep_spb = QtWidgets.QSpinBox()
                FBXExportBakeComplexStep_spb.setValue(1)
                FBXExportBakeComplexStep_spb.setObjectName("FBXExportBakeComplexStep")
                fbx_export_formlayout.addRow(FBXExportBakeComplexStep_lbl, FBXExportBakeComplexStep_spb)

                FBXExportConvertUnitString_lbl = QtWidgets.QLabel()
                FBXExportConvertUnitString_lbl.setText("Convert Units")
                FBXExportConvertUnitString_combo = QtWidgets.QComboBox()
                FBXExportConvertUnitString_combo.addItems(["mm", "dm", "cm", "m", "km", "In", "ft", "yd", "mi"])
                FBXExportConvertUnitString_combo.setObjectName("FBXExportConvertUnitString")
                fbx_export_formlayout.addRow(FBXExportConvertUnitString_lbl)

                FBXExportQuaternion_lbl = QtWidgets.QLabel()
                FBXExportQuaternion_lbl.setText("Treat Quaternion: ")
                FBXExportQuaternion_combo = QtWidgets.QComboBox()
                FBXExportQuaternion_combo.addItems(["quaternion", "euler", "resample"])
                FBXExportQuaternion_combo.setObjectName("FBXExportQuaternion")
                fbx_export_formlayout.addRow(FBXExportQuaternion_lbl, FBXExportQuaternion_combo)

                FBXExportFileVersion_lbl = QtWidgets.QLabel()
                FBXExportFileVersion_lbl.setText("FBX Verison: ")
                FBXExportFileVersion_le = QtWidgets.QLineEdit()
                FBXExportFileVersion_le.setMaximumWidth(150)
                FBXExportFileVersion_le.setText("FBX201400")
                FBXExportFileVersion_le.setObjectName("FBXExportFileVersion")
                fbx_export_formlayout.addRow(FBXExportFileVersion_lbl, FBXExportFileVersion_le)

                FBXExportScaleFactor_lbl = QtWidgets.QLabel()
                FBXExportScaleFactor_lbl.setText("Scale Factor: ")
                FBXExportScaleFactor_spb = QtWidgets.QDoubleSpinBox()
                FBXExportScaleFactor_spb.setValue(1.0)
                FBXExportScaleFactor_spb.setObjectName("FBXExportScaleFactor")
                fbx_export_formlayout.addRow(FBXExportScaleFactor_lbl, FBXExportScaleFactor_spb)

                FBXExportApplyConstantKeyReducer_chb = QtWidgets.QCheckBox()
                FBXExportApplyConstantKeyReducer_chb.setText("Apply Constant Key Reducer")
                FBXExportApplyConstantKeyReducer_chb.setObjectName("FBXExportApplyConstantKeyReducer")
                fbx_export_formlayout.addRow(FBXExportApplyConstantKeyReducer_chb)

                FBXExportShapes_chb = QtWidgets.QCheckBox()
                FBXExportShapes_chb.setText("Shapes")
                FBXExportShapes_chb.setObjectName("FBXExportShapes")
                fbx_export_formlayout.addRow(FBXExportShapes_chb)

                FBXExportUseSceneName_chb = QtWidgets.QCheckBox()
                FBXExportUseSceneName_chb.setText("Use Scene Name")
                FBXExportUseSceneName_chb.setObjectName("FBXExportUseSceneName")
                fbx_export_formlayout.addRow(FBXExportUseSceneName_chb)

                FBXExportSkeletonDefinitions_chb = QtWidgets.QCheckBox()
                FBXExportSkeletonDefinitions_chb.setText("Skeleton Definitions")
                FBXExportSkeletonDefinitions_chb.setObjectName("FBXExportSkeletonDefinitions")
                fbx_export_formlayout.addRow(FBXExportSkeletonDefinitions_chb)

                FBXExportInstances_chb = QtWidgets.QCheckBox()
                FBXExportInstances_chb.setText("Instances")
                FBXExportInstances_chb.setObjectName("FBXExportInstances")
                fbx_export_formlayout.addRow(FBXExportInstances_chb)

                FBXExportCameras_chb = QtWidgets.QCheckBox()
                FBXExportCameras_chb.setText("Cameras")
                FBXExportCameras_chb.setObjectName("FBXExportCameras")
                fbx_export_formlayout.addRow(FBXExportCameras_chb)

                FBXExportTangents_chb = QtWidgets.QCheckBox()
                FBXExportTangents_chb.setText("Tangents")
                FBXExportTangents_chb.setObjectName("FBXExportTangents")
                fbx_export_formlayout.addRow(FBXExportTangents_chb)

                FBXExportInAscii_chb = QtWidgets.QCheckBox()
                FBXExportInAscii_chb.setText("Ascii")
                FBXExportInAscii_chb.setObjectName("FBXExportInAscii")
                fbx_export_formlayout.addRow(FBXExportInAscii_chb)

                FBXExportLights_chb = QtWidgets.QCheckBox()
                FBXExportLights_chb.setText("Lights")
                FBXExportLights_chb.setObjectName("FBXExportLights")
                fbx_export_formlayout.addRow(FBXExportLights_chb)

                FBXExportReferencedAssetsContent_chb = QtWidgets.QCheckBox()
                FBXExportReferencedAssetsContent_chb.setText("Referenced Assets")
                FBXExportReferencedAssetsContent_chb.setObjectName("FBXExportReferencedAssetsContent")
                fbx_export_formlayout.addRow(FBXExportReferencedAssetsContent_chb)

                FBXExportConstraints_chb = QtWidgets.QCheckBox()
                FBXExportConstraints_chb.setText("Constraints")
                FBXExportConstraints_chb.setObjectName("FBXExportConstraints")
                fbx_export_formlayout.addRow(FBXExportConstraints_chb)

                FBXExportSmoothMesh_chb = QtWidgets.QCheckBox()
                FBXExportSmoothMesh_chb.setText("Smooth Mesh")
                FBXExportSmoothMesh_chb.setObjectName("FBXExportSmoothMesh")
                fbx_export_formlayout.addRow(FBXExportSmoothMesh_chb)

                FBXExportHardEdges_chb = QtWidgets.QCheckBox()
                FBXExportHardEdges_chb.setText("Hard Edges")
                FBXExportHardEdges_chb.setObjectName("FBXExportHardEdges")
                fbx_export_formlayout.addRow(FBXExportHardEdges_chb)

                FBXExportInputConnections_chb = QtWidgets.QCheckBox()
                FBXExportInputConnections_chb.setText("Input Connections")
                FBXExportInputConnections_chb.setObjectName("FBXExportInputConnections")
                fbx_export_formlayout.addRow(FBXExportInputConnections_chb)

                FBXExportEmbeddedTextures_chb = QtWidgets.QCheckBox()
                FBXExportEmbeddedTextures_chb.setText("Embed Textures")
                FBXExportEmbeddedTextures_chb.setObjectName("FBXExportEmbeddedTextures")
                fbx_export_formlayout.addRow(FBXExportEmbeddedTextures_chb)

                FBXExportBakeComplexAnimation_chb = QtWidgets.QCheckBox()
                FBXExportBakeComplexAnimation_chb.setText("Bake Animation")
                FBXExportBakeComplexAnimation_chb.setObjectName("FBXExportBakeComplexAnimation")
                fbx_export_formlayout.addRow(FBXExportBakeComplexAnimation_chb)

                FBXExportCacheFile_chb = QtWidgets.QCheckBox()
                FBXExportCacheFile_chb.setText("Cache File")
                FBXExportCacheFile_chb.setObjectName("FBXExportCacheFile")
                fbx_export_formlayout.addRow(FBXExportCacheFile_chb)

                FBXExportSmoothingGroups_chb = QtWidgets.QCheckBox()
                FBXExportSmoothingGroups_chb.setText("Smoothing Groups")
                FBXExportSmoothingGroups_chb.setObjectName("FBXExportSmoothingGroups")
                fbx_export_formlayout.addRow(FBXExportSmoothingGroups_chb)

                FBXExportBakeResampleAnimation_chb = QtWidgets.QCheckBox()
                FBXExportBakeResampleAnimation_chb.setText("Resample Animation")
                FBXExportBakeResampleAnimation_chb.setObjectName("FBXExportBakeResampleAnimation")
                fbx_export_formlayout.addRow(FBXExportBakeResampleAnimation_chb)

                FBXExportTriangulate_chb = QtWidgets.QCheckBox()
                FBXExportTriangulate_chb.setText("Triangulate")
                FBXExportTriangulate_chb.setObjectName("FBXExportTriangulate")
                fbx_export_formlayout.addRow(FBXExportTriangulate_chb)

                FBXExportSkins_chb = QtWidgets.QCheckBox()
                FBXExportSkins_chb.setText("Skins")
                FBXExportSkins_chb.setObjectName("FBXExportSkins")
                fbx_export_formlayout.addRow(FBXExportSkins_chb)

                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                fbx_export_layout.addItem(spacerItem)

            ## MAYA ALEMBIC
            ## ------------
            def _maya_alembic():
                alembic_horizontal_layout = QtWidgets.QHBoxLayout(alembicTab)
                alembic_import_layout = QtWidgets.QVBoxLayout()
                alembic_seperator = QtWidgets.QLabel()
                alembic_seperator.setStyleSheet("background-color: rgb(255,141,28,60);")
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
                alembic_import_layout.addLayout(alembic_import_formlayout)

                fitTimeRange_chb = QtWidgets.QCheckBox()
                fitTimeRange_chb.setText("Fit Time Range")
                fitTimeRange_chb.setObjectName("fitTimeRange")
                alembic_import_formlayout.addRow(fitTimeRange_chb)

                setToStartFrame_chb = QtWidgets.QCheckBox()
                setToStartFrame_chb.setText("Set To Start Frame")
                setToStartFrame_chb.setObjectName("setToStartFrame")
                alembic_import_formlayout.addRow(setToStartFrame_chb)

                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                alembic_import_layout.addItem(spacerItem)

                ## MAYA ALEMBIC EXPORT WIDGETS
                alembic_export_label = QtWidgets.QLabel()
                alembic_export_label.setText("Alembic Export Settings")
                alembic_export_label.setFont(self.headerBFont)
                alembic_export_layout.addWidget(alembic_export_label)

                alembic_export_formlayout = QtWidgets.QFormLayout()
                alembic_export_layout.addLayout(alembic_export_formlayout)

                step_lbl = QtWidgets.QLabel()
                step_lbl.setText("Step")
                step_spb = QtWidgets.QDoubleSpinBox()
                step_spb.setObjectName("step")
                alembic_export_formlayout.addRow(step_lbl, step_spb)

                dataFormat_lbl = QtWidgets.QLabel()
                dataFormat_lbl.setText("Data Format")
                dataFormat_combo = QtWidgets.QComboBox()
                dataFormat_combo.addItems(["Ogawa", "HDF5"])
                dataFormat_combo.setObjectName("dataFormat")
                alembic_export_formlayout.addRow(dataFormat_lbl, dataFormat_combo)

                writeFaceSets_chb = QtWidgets.QCheckBox()
                writeFaceSets_chb.setText("Face Sets")
                writeFaceSets_chb.setObjectName("writeFaceSets")
                alembic_export_formlayout.addRow(writeFaceSets_chb)

                writeUVSets_chb = QtWidgets.QCheckBox()
                writeUVSets_chb.setText("Uv Sets")
                writeUVSets_chb.setObjectName("writeUVSets")
                alembic_export_formlayout.addRow(writeUVSets_chb)

                noNormals_chb = QtWidgets.QCheckBox()
                noNormals_chb.setText("No Normals")
                noNormals_chb.setObjectName("noNormals")
                alembic_export_formlayout.addRow(noNormals_chb)

                autoSubd_chb = QtWidgets.QCheckBox()
                autoSubd_chb.setText("Auto Subdivide")
                autoSubd_chb.setObjectName("autoSubd")
                alembic_export_formlayout.addRow(autoSubd_chb)

                stripNamespaces_chb = QtWidgets.QCheckBox()
                stripNamespaces_chb.setText("Strip Namespaces")
                stripNamespaces_chb.setObjectName("stripNamespaces")
                alembic_export_formlayout.addRow(stripNamespaces_chb)

                wholeFrameGeo_chb = QtWidgets.QCheckBox()
                wholeFrameGeo_chb.setText("Whole Frame Geo")
                wholeFrameGeo_chb.setObjectName("wholeFrameGeo")
                alembic_export_formlayout.addRow(wholeFrameGeo_chb)

                renderableOnly_chb = QtWidgets.QCheckBox()
                renderableOnly_chb.setText("Renderable Only")
                renderableOnly_chb.setObjectName("renderableOnly")
                alembic_export_formlayout.addRow(renderableOnly_chb)

                worldSpace_chb = QtWidgets.QCheckBox()
                worldSpace_chb.setText("Worldspace")
                worldSpace_chb.setObjectName("worldSpace")
                alembic_export_formlayout.addRow(worldSpace_chb)

                writeVisibility_chb = QtWidgets.QCheckBox()
                writeVisibility_chb.setText("Visibility")
                writeVisibility_chb.setObjectName("writeVisibility")
                alembic_export_formlayout.addRow(writeVisibility_chb)

                eulerFilter_chb = QtWidgets.QCheckBox()
                eulerFilter_chb.setText("Euler Filter")
                eulerFilter_chb.setObjectName("eulerFilter")
                alembic_export_formlayout.addRow(eulerFilter_chb)

                writeColorSets_chb = QtWidgets.QCheckBox()
                writeColorSets_chb.setText("Color Sets")
                writeColorSets_chb.setObjectName("writeColorSets")
                alembic_export_formlayout.addRow(writeColorSets_chb)

                uvWrite_chb = QtWidgets.QCheckBox()
                uvWrite_chb.setText("UV")
                uvWrite_chb.setObjectName("uvWrite")
                alembic_export_formlayout.addRow(uvWrite_chb)

                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                alembic_export_layout.addItem(spacerItem)

            _maya_obj()
            _maya_fbx()
            _maya_alembic()

        if sw == "3dsmax" or sw == "":
            pass

        if sw == "houdini" or sw == "":
            pass

        h1_s1_layout.addWidget(softwaresTabWidget)
        importExport_Layout.addLayout(h1_s1_layout)

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        importExport_Layout.addItem(spacerItem)
        self.contentsMaster_layout.addWidget(self.importExportOptions_vis)

    def _sharedSettingsContent(self):
        sharedSettings_Layout = QtWidgets.QVBoxLayout(self.sharedSettings_vis)
        sharedSettings_Layout.setSpacing(6)

        sharedSettings_label = QtWidgets.QLabel(self.sharedSettings_vis)
        sharedSettings_label.setText("Shared Settings")
        sharedSettings_label.setFont(self.headerAFont)
        sharedSettings_label.setIndent(10)
        sharedSettings_label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        sharedSettings_Layout.addWidget(sharedSettings_label)

        users_cmdButton = QtWidgets.QCommandLinkButton(self.sharedSettings_vis)
        users_cmdButton.setText("Users")
        sharedSettings_Layout.addWidget(users_cmdButton)

        passwords_cmdButton = QtWidgets.QCommandLinkButton(self.sharedSettings_vis)
        passwords_cmdButton.setText("Passwords")
        sharedSettings_Layout.addWidget(passwords_cmdButton)

        namingConventions_cmdButton = QtWidgets.QCommandLinkButton(self.sharedSettings_vis)
        namingConventions_cmdButton.setText("Naming Conventions")
        sharedSettings_Layout.addWidget(namingConventions_cmdButton)

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sharedSettings_Layout.addItem(spacerItem)
        self.contentsMaster_layout.addWidget(self.sharedSettings_vis)

        # SIGNALS
        users_cmdButton.clicked.connect(lambda: self.settingsMenu_treeWidget.setCurrentItem(self.users_item))
        passwords_cmdButton.clicked.connect(lambda: self.settingsMenu_treeWidget.setCurrentItem(self.passwords_item))
        namingConventions_cmdButton.clicked.connect(lambda: self.settingsMenu_treeWidget.setCurrentItem(self.namingConventions_item))

    def pbSettingsMayaUI(self):
        # This method iS Software Specific
        if BoilerDict["Environment"]=="Standalone":
            # manager=self._getManager()
            formatFlag = False
        else:
            # manager = self.manager
            formatFlag = True

        manager = self._getManager()

        passw, ok = QtWidgets.QInputDialog.getText(self, "Password Query",
                                               "Enter Admin Password:", QtWidgets.QLineEdit.Password)

        if ok:
            if manager.checkPassword(passw):
                pass
            else:
                self.infoPop(textTitle="Incorrect Password", textHeader="The Password is invalid")
                return
        else:
            return


        if formatFlag:
            formatDict = manager.getFormatsAndCodecs()
        else:
            formatDict = {}

        def updateCodecs():
            codecList = formatDict[self.fileformat_comboBox.currentText()]
            self.codec_comboBox.clear()

            self.codec_comboBox.addItems(codecList)
        def onPbSettingsAccept():
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
            manager.savePBSettings(newPbSettings)
            self.statusBar().showMessage("Status | Playblast Settings Saved")
            self.pbSettings_dialog.accept()


        currentSettings = manager.loadPBSettings()
        self.pbSettings_dialog = QtWidgets.QDialog(parent=self)
        self.pbSettings_dialog.setModal(True)
        self.pbSettings_dialog.setObjectName(("Playblast_Dialog"))
        self.pbSettings_dialog.resize(380, 483)
        self.pbSettings_dialog.setMinimumSize(QtCore.QSize(380, 550))
        self.pbSettings_dialog.setMaximumSize(QtCore.QSize(380, 550))
        self.pbSettings_dialog.setWindowTitle(("Set Playblast Settings"))

        self.pbsettings_buttonBox = QtWidgets.QDialogButtonBox(self.pbSettings_dialog)
        self.pbsettings_buttonBox.setGeometry(QtCore.QRect(20, 500, 341, 30))
        self.pbsettings_buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.pbsettings_buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Save)
        self.pbsettings_buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).setMinimumSize(QtCore.QSize(100, 30))
        self.pbsettings_buttonBox.button(QtWidgets.QDialogButtonBox.Save).setMinimumSize(QtCore.QSize(100, 30))
        self.pbsettings_buttonBox.setObjectName(("pbsettings_buttonBox"))

        self.videoproperties_groupBox = QtWidgets.QGroupBox(self.pbSettings_dialog)
        self.videoproperties_groupBox.setGeometry(QtCore.QRect(10, 20, 361, 191))
        self.videoproperties_groupBox.setTitle(("Video Properties"))
        self.videoproperties_groupBox.setObjectName(("videoproperties_groupBox"))

        self.fileformat_label = QtWidgets.QLabel(self.videoproperties_groupBox)
        self.fileformat_label.setGeometry(QtCore.QRect(20, 30, 71, 20))
        self.fileformat_label.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.fileformat_label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.fileformat_label.setText(("Format"))
        self.fileformat_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.fileformat_label.setObjectName(("fileformat_label"))
        self.fileformat_label.setEnabled(formatFlag)

        self.fileformat_comboBox = QtWidgets.QComboBox(self.videoproperties_groupBox)
        self.fileformat_comboBox.setGeometry(QtCore.QRect(100, 30, 111, 22))
        self.fileformat_comboBox.setObjectName(("fileformat_comboBox"))
        self.fileformat_comboBox.addItems(formatDict.keys())
        self.fileformat_comboBox.setEnabled(formatFlag)

        # get the index number from the name in the settings file and make that index active
        ffindex = self.fileformat_comboBox.findText(currentSettings["Format"], QtCore.Qt.MatchFixedString)
        if ffindex >= 0:
            self.fileformat_comboBox.setCurrentIndex(ffindex)

        self.codec_label = QtWidgets.QLabel(self.videoproperties_groupBox)
        self.codec_label.setGeometry(QtCore.QRect(30, 70, 61, 20))
        self.codec_label.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.codec_label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.codec_label.setText(("Codec"))
        self.codec_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.codec_label.setObjectName(("codec_label"))
        self.codec_label.setEnabled(formatFlag)

        self.codec_comboBox = QtWidgets.QComboBox(self.videoproperties_groupBox)
        self.codec_comboBox.setGeometry(QtCore.QRect(100, 70, 111, 22))
        self.codec_comboBox.setObjectName(("codec_comboBox"))
        self.codec_comboBox.setEnabled(formatFlag)
        if formatFlag:
            updateCodecs()

        self.fileformat_comboBox.currentIndexChanged.connect(updateCodecs)

        # get the index number from the name in the settings file and make that index active
        cindex = self.codec_comboBox.findText(currentSettings["Codec"], QtCore.Qt.MatchFixedString)
        if cindex >= 0:
            self.codec_comboBox.setCurrentIndex(cindex)

        self.quality_label = QtWidgets.QLabel(self.videoproperties_groupBox)
        self.quality_label.setGeometry(QtCore.QRect(30, 110, 61, 20))
        self.quality_label.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.quality_label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.quality_label.setText(("Quality"))
        self.quality_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.quality_label.setObjectName(("quality_label"))

        self.quality_spinBox = QtWidgets.QSpinBox(self.videoproperties_groupBox)
        self.quality_spinBox.setGeometry(QtCore.QRect(100, 110, 41, 21))
        self.quality_spinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.quality_spinBox.setMinimum(1)
        self.quality_spinBox.setMaximum(100)
        self.quality_spinBox.setProperty("value", currentSettings["Quality"])
        self.quality_spinBox.setObjectName(("quality_spinBox"))

        self.quality_horizontalSlider = QtWidgets.QSlider(self.videoproperties_groupBox)
        self.quality_horizontalSlider.setGeometry(QtCore.QRect(150, 110, 191, 21))
        self.quality_horizontalSlider.setMinimum(1)
        self.quality_horizontalSlider.setMaximum(100)
        self.quality_horizontalSlider.setProperty("value", currentSettings["Quality"])
        self.quality_horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.quality_horizontalSlider.setTickInterval(0)
        self.quality_horizontalSlider.setObjectName(("quality_horizontalSlider"))

        self.resolution_label = QtWidgets.QLabel(self.videoproperties_groupBox)
        self.resolution_label.setGeometry(QtCore.QRect(30, 150, 61, 20))
        self.resolution_label.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.resolution_label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.resolution_label.setText(("Resolution"))
        self.resolution_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.resolution_label.setObjectName(("resolution_label"))

        self.resolutionx_spinBox = QtWidgets.QSpinBox(self.videoproperties_groupBox)
        self.resolutionx_spinBox.setGeometry(QtCore.QRect(100, 150, 61, 21))
        self.resolutionx_spinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.resolutionx_spinBox.setMinimum(0)
        self.resolutionx_spinBox.setMaximum(4096)
        self.resolutionx_spinBox.setProperty("value", currentSettings["Resolution"][0])
        self.resolutionx_spinBox.setObjectName(("resolutionx_spinBox"))

        self.resolutiony_spinBox = QtWidgets.QSpinBox(self.videoproperties_groupBox)
        self.resolutiony_spinBox.setGeometry(QtCore.QRect(170, 150, 61, 21))
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
        self.polygononly_checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.polygononly_checkBox.setText(("Polygon Only"))
        self.polygononly_checkBox.setChecked(currentSettings["PolygonOnly"])
        self.polygononly_checkBox.setObjectName(("polygononly_checkBox"))

        self.showgrid_checkBox = QtWidgets.QCheckBox(self.viewportoptions_groupBox)
        self.showgrid_checkBox.setGeometry(QtCore.QRect(210, 30, 91, 20))
        self.showgrid_checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.showgrid_checkBox.setText(("Show Grid"))
        self.showgrid_checkBox.setChecked(currentSettings["ShowGrid"])
        self.showgrid_checkBox.setObjectName(("showgrid_checkBox"))

        self.clearselection_checkBox = QtWidgets.QCheckBox(self.viewportoptions_groupBox)
        self.clearselection_checkBox.setGeometry(QtCore.QRect(60, 60, 91, 20))
        self.clearselection_checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.clearselection_checkBox.setText(("Clear Selection"))
        self.clearselection_checkBox.setChecked(currentSettings["ClearSelection"])
        self.clearselection_checkBox.setObjectName(("clearselection_checkBox"))

        self.wireonshaded_checkBox = QtWidgets.QCheckBox(self.viewportoptions_groupBox)
        self.wireonshaded_checkBox.setGeometry(QtCore.QRect(51, 90, 100, 20))
        self.wireonshaded_checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.wireonshaded_checkBox.setText(("Wire On Shaded"))
        try:
            self.wireonshaded_checkBox.setChecked(currentSettings["WireOnShaded"])
        except KeyError:
            self.wireonshaded_checkBox.setChecked(False)
        self.wireonshaded_checkBox.setObjectName(("wireonshaded_checkBox"))

        self.usedefaultmaterial_checkBox = QtWidgets.QCheckBox(self.viewportoptions_groupBox)
        self.usedefaultmaterial_checkBox.setGeometry(QtCore.QRect(180, 90, 120, 20))
        self.usedefaultmaterial_checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.usedefaultmaterial_checkBox.setText(("Use Default Material"))
        try:
            self.usedefaultmaterial_checkBox.setChecked(currentSettings["UseDefaultMaterial"])
        except KeyError:
            self.usedefaultmaterial_checkBox.setChecked(False)

        self.displaytextures_checkBox = QtWidgets.QCheckBox(self.viewportoptions_groupBox)
        self.displaytextures_checkBox.setGeometry(QtCore.QRect(190, 60, 111, 20))
        self.displaytextures_checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.displaytextures_checkBox.setText(("Display Textures"))
        self.displaytextures_checkBox.setChecked(currentSettings["DisplayTextures"])
        self.displaytextures_checkBox.setObjectName(("displaytextures_checkBox"))

        self.hudoptions_groupBox = QtWidgets.QGroupBox(self.pbSettings_dialog)
        self.hudoptions_groupBox.setGeometry(QtCore.QRect(10, 370, 361, 110))
        self.hudoptions_groupBox.setTitle(("HUD Options"))
        self.hudoptions_groupBox.setObjectName(("hudoptions_groupBox"))

        self.showframenumber_checkBox = QtWidgets.QCheckBox(self.hudoptions_groupBox)
        self.showframenumber_checkBox.setGeometry(QtCore.QRect(20, 20, 131, 20))
        self.showframenumber_checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.showframenumber_checkBox.setText(("Show Frame Number"))
        self.showframenumber_checkBox.setChecked(currentSettings["ShowFrameNumber"])
        self.showframenumber_checkBox.setObjectName(("showframenumber_checkBox"))

        self.showscenename_checkBox = QtWidgets.QCheckBox(self.hudoptions_groupBox)
        self.showscenename_checkBox.setGeometry(QtCore.QRect(20, 50, 131, 20))
        self.showscenename_checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.showscenename_checkBox.setText(("Show Scene Name"))
        self.showscenename_checkBox.setChecked(currentSettings["ShowSceneName"])
        self.showscenename_checkBox.setObjectName(("showscenename_checkBox"))

        self.showcategory_checkBox = QtWidgets.QCheckBox(self.hudoptions_groupBox)
        self.showcategory_checkBox.setGeometry(QtCore.QRect(200, 20, 101, 20))
        self.showcategory_checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.showcategory_checkBox.setText(("Show Category"))
        self.showcategory_checkBox.setChecked(currentSettings["ShowCategory"])
        self.showcategory_checkBox.setObjectName(("showcategory_checkBox"))

        self.showfps_checkBox = QtWidgets.QCheckBox(self.hudoptions_groupBox)
        self.showfps_checkBox.setGeometry(QtCore.QRect(200, 50, 101, 20))
        self.showfps_checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.showfps_checkBox.setText(("Show FPS"))
        self.showfps_checkBox.setChecked(currentSettings["ShowFPS"])
        self.showfps_checkBox.setObjectName(("showfps_checkBox"))

        self.showframerange_checkBox = QtWidgets.QCheckBox(self.hudoptions_groupBox)
        self.showframerange_checkBox.setGeometry(QtCore.QRect(20, 80, 131, 20))
        self.showframerange_checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.showframerange_checkBox.setText(("Show Frame Range"))
        # v1.1 SPECIFIC
        try:
            self.showframerange_checkBox.setChecked(currentSettings["ShowFrameRange"])
        except KeyError:
            self.showframerange_checkBox.setChecked(True)
        self.showframerange_checkBox.setObjectName(("showframerange_checkBox"))

        self.pbsettings_buttonBox.accepted.connect(onPbSettingsAccept)
        self.pbsettings_buttonBox.rejected.connect(self.pbSettings_dialog.reject)
        self.quality_spinBox.valueChanged.connect(self.quality_horizontalSlider.setValue)
        self.quality_horizontalSlider.valueChanged.connect(self.quality_spinBox.setValue)

        self.pbSettings_dialog.show()

    def pbSettingsMaxUI(self):
        # This method iS Software Specific

        # if BoilerDict["Environment"]=="Standalone":
        #     manager=self._getManager()
        # else:
        #     manager = self.manager
        manager = self._getManager()

        passw, ok = QtWidgets.QInputDialog.getText(self, "Password Query",
                                               "Enter Admin Password:", QtWidgets.QLineEdit.Password)

        if ok:
            if manager.checkPassword(passw):
                pass
            else:
                self.infoPop(textTitle="Incorrect Password", textHeader="The Password is invalid")
                return
        else:
            return

        def onPbSettingsAccept():
            newPbSettings = {"Resolution": (self.resolutionx_spinBox.value(), self.resolutiony_spinBox.value()),
                             "Format": "avi",
                             "Codec": "N/A",
                             "Percent": 100,  ## this one never changes
                             "Quality": "N/A",
                             "ShowFrameNumber": self.showframenumber_checkBox.isChecked(),
                             "ShowSceneName": "N/A",
                             "ShowCategory": "N/A",
                             "ShowFPS": "N/A",
                             "ShowFrameRange": "N/A",
                             "PolygonOnly": self.polygononly_checkBox.isChecked(),
                             "ShowGrid": self.showgrid_checkBox.isChecked(),
                             "ClearSelection": self.clearselection_checkBox.isChecked(),
                             "DisplayTextures": "N/A",
                             "WireOnShaded": self.wireonshaded_checkBox.isChecked(),
                             "UseDefaultMaterial": "N/A"
                             }
            manager.savePBSettings(newPbSettings)
            self.statusBar().showMessage("Status | Playblast Settings Saved")
            self.pbSettings_dialog.accept()

        currentSettings = manager.loadPBSettings()

        self.pbSettings_dialog = QtWidgets.QDialog(parent=self)
        self.pbSettings_dialog.setModal(True)
        self.pbSettings_dialog.setObjectName(("Playblast_Dialog"))
        self.pbSettings_dialog.resize(380, 483)
        self.pbSettings_dialog.setMaximumSize(QtCore.QSize(380, 400))
        self.pbSettings_dialog.setWindowTitle(("Set Playblast Settings"))

        self.pbsettings_buttonBox = QtWidgets.QDialogButtonBox(self.pbSettings_dialog)
        self.pbsettings_buttonBox.setGeometry(QtCore.QRect(20, 345, 341, 30))
        self.pbsettings_buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.pbsettings_buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Save)
        self.pbsettings_buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).setMinimumSize(QtCore.QSize(100, 30))
        self.pbsettings_buttonBox.button(QtWidgets.QDialogButtonBox.Save).setMinimumSize(QtCore.QSize(100, 30))
        self.pbsettings_buttonBox.setObjectName(("pbsettings_buttonBox"))

        self.videoproperties_groupBox = QtWidgets.QGroupBox(self.pbSettings_dialog)
        self.videoproperties_groupBox.setGeometry(QtCore.QRect(10, 20, 361, 80))
        self.videoproperties_groupBox.setTitle(("Video Properties"))
        self.videoproperties_groupBox.setObjectName(("videoproperties_groupBox"))

        self.resolution_label = QtWidgets.QLabel(self.videoproperties_groupBox)
        self.resolution_label.setGeometry(QtCore.QRect(30, 30, 61, 20))
        self.resolution_label.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.resolution_label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.resolution_label.setText(("Resolution"))
        self.resolution_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.resolution_label.setObjectName(("resolution_label"))

        self.resolutionx_spinBox = QtWidgets.QSpinBox(self.videoproperties_groupBox)
        self.resolutionx_spinBox.setGeometry(QtCore.QRect(100, 30, 61, 21))
        self.resolutionx_spinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.resolutionx_spinBox.setMinimum(0)
        self.resolutionx_spinBox.setMaximum(4096)
        self.resolutionx_spinBox.setProperty("value", currentSettings["Resolution"][0])
        self.resolutionx_spinBox.setObjectName(("resolutionx_spinBox"))

        self.resolutiony_spinBox = QtWidgets.QSpinBox(self.videoproperties_groupBox)
        self.resolutiony_spinBox.setGeometry(QtCore.QRect(170, 30, 61, 21))
        self.resolutiony_spinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.resolutiony_spinBox.setMinimum(1)
        self.resolutiony_spinBox.setMaximum(4096)
        self.resolutiony_spinBox.setProperty("value", currentSettings["Resolution"][1])
        self.resolutiony_spinBox.setObjectName(("resolutiony_spinBox"))

        self.viewportoptions_groupBox = QtWidgets.QGroupBox(self.pbSettings_dialog)
        self.viewportoptions_groupBox.setGeometry(QtCore.QRect(10, 120, 361, 95))
        self.viewportoptions_groupBox.setTitle(("Viewport Options"))
        self.viewportoptions_groupBox.setObjectName(("viewportoptions_groupBox"))

        self.polygononly_checkBox = QtWidgets.QCheckBox(self.viewportoptions_groupBox)
        self.polygononly_checkBox.setGeometry(QtCore.QRect(60, 30, 91, 20))
        self.polygononly_checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.polygononly_checkBox.setText(("Polygon Only"))
        self.polygononly_checkBox.setChecked(currentSettings["PolygonOnly"])
        self.polygononly_checkBox.setObjectName(("polygononly_checkBox"))

        self.showgrid_checkBox = QtWidgets.QCheckBox(self.viewportoptions_groupBox)
        self.showgrid_checkBox.setGeometry(QtCore.QRect(210, 30, 91, 20))
        self.showgrid_checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.showgrid_checkBox.setText(("Show Grid"))
        self.showgrid_checkBox.setChecked(currentSettings["ShowGrid"])
        self.showgrid_checkBox.setObjectName(("showgrid_checkBox"))

        self.clearselection_checkBox = QtWidgets.QCheckBox(self.viewportoptions_groupBox)
        self.clearselection_checkBox.setGeometry(QtCore.QRect(60, 60, 91, 20))
        self.clearselection_checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.clearselection_checkBox.setText(("Clear Selection"))
        self.clearselection_checkBox.setChecked(currentSettings["ClearSelection"])
        self.clearselection_checkBox.setObjectName(("clearselection_checkBox"))

        self.wireonshaded_checkBox = QtWidgets.QCheckBox(self.viewportoptions_groupBox)
        self.wireonshaded_checkBox.setGeometry(QtCore.QRect(201, 60, 100, 20))
        self.wireonshaded_checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.wireonshaded_checkBox.setText(("Wire On Shaded"))
        try:
            self.wireonshaded_checkBox.setChecked(currentSettings["WireOnShaded"])
        except KeyError:
            self.wireonshaded_checkBox.setChecked(False)
        self.wireonshaded_checkBox.setObjectName(("wireonshaded_checkBox"))

        self.hudoptions_groupBox = QtWidgets.QGroupBox(self.pbSettings_dialog)
        self.hudoptions_groupBox.setGeometry(QtCore.QRect(10, 240, 361, 80))
        self.hudoptions_groupBox.setTitle(("HUD Options"))
        self.hudoptions_groupBox.setObjectName(("hudoptions_groupBox"))

        self.showframenumber_checkBox = QtWidgets.QCheckBox(self.hudoptions_groupBox)
        self.showframenumber_checkBox.setGeometry(QtCore.QRect(20, 20, 131, 20))
        self.showframenumber_checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.showframenumber_checkBox.setText(("Show Frame Number"))
        self.showframenumber_checkBox.setChecked(currentSettings["ShowFrameNumber"])
        self.showframenumber_checkBox.setObjectName(("showframenumber_checkBox"))

        self.pbsettings_buttonBox.accepted.connect(onPbSettingsAccept)
        self.pbsettings_buttonBox.rejected.connect(self.pbSettings_dialog.reject)

        self.pbSettings_dialog.show()

    def addRemoveUserUI(self):
        # This method is NOT Software Specific
        passw, ok = QtWidgets.QInputDialog.getText(self, "Password Query",
                                               "Enter Admin Password:", QtWidgets.QLineEdit.Password)

        if ok:
            if self.manager.checkPassword(passw):
                pass
            else:
                self.infoPop(textTitle="Incorrect Password", textHeader="The Password is invalid")
                return
        else:
            return

        userControl_Dialog = QtWidgets.QDialog(parent=self)
        userControl_Dialog.setObjectName(("userControl_Dialog"))
        userControl_Dialog.resize(349, 285)
        userControl_Dialog.setWindowTitle(("Add/Remove Users"))

        verticalLayout_2 = QtWidgets.QVBoxLayout(userControl_Dialog)

        users_label = QtWidgets.QLabel(userControl_Dialog)
        users_label.setText("Users:")
        verticalLayout_2.addWidget(users_label)

        horizontalLayout = QtWidgets.QHBoxLayout()

        users_listWidget = QtWidgets.QListWidget(userControl_Dialog)
        horizontalLayout.addWidget(users_listWidget)

        verticalLayout = QtWidgets.QVBoxLayout()
        verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)

        add_pushButton = QtWidgets.QPushButton(userControl_Dialog)
        add_pushButton.setText(("Add..."))
        verticalLayout.addWidget(add_pushButton)

        remove_pushButton = QtWidgets.QPushButton(userControl_Dialog)
        remove_pushButton.setText(("Remove"))
        verticalLayout.addWidget(remove_pushButton)

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        verticalLayout.addItem(spacerItem)

        horizontalLayout.addLayout(verticalLayout)
        verticalLayout_2.addLayout(horizontalLayout)

        buttonBox = QtWidgets.QDialogButtonBox(userControl_Dialog)
        CloseButton = buttonBox.addButton("Close", QtWidgets.QDialogButtonBox.RejectRole)
        CloseButton.setMinimumSize(QtCore.QSize(100, 30))

        verticalLayout_2.addWidget(buttonBox)

        # list the users
        def updateUsers():
            user_list_sorted = self.manager.getUsers()
            users_listWidget.clear()
            users_listWidget.addItems(user_list_sorted)

        def onRemoveUser():
            row = users_listWidget.currentRow()
            if row == -1:
                return
            self.manager.removeUser(str(users_listWidget.currentItem().text()))
            self.manager.currentUser = self.manager.getUsers()[0]
            self._initUsers()
            updateUsers()

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
                ret, msg = self.manager.addUser(str(fullname_lineEdit.text()), str(initials_lineEdit.text()))
                if ret == -1:
                    self.infoPop(textTitle="Cannot Add User", textHeader=msg)
                    return
                self.manager.currentUser = fullname_lineEdit.text()
                self._initUsers()
                updateUsers()
                addUser_Dialog.close()

            buttonBox.accepted.connect(onAddUser)
            buttonBox.rejected.connect(addUser_Dialog.reject)




        updateUsers()

        add_pushButton.clicked.connect(addNewUserUI)
        remove_pushButton.clicked.connect(onRemoveUser)

        buttonBox.rejected.connect(userControl_Dialog.reject)

        # buttonBox.accepted.connect(onAccepted)
        # buttonBox.rejected.connect(projectSettings_Dialog.reject)

        userControl_Dialog.show()

    def addRemoveCategoryUI(self):
        # This method IS Software Specific
        manager = self._getManager()

        passw, ok = QtWidgets.QInputDialog.getText(self, "Password Query",
                                               "Enter Admin Password:", QtWidgets.QLineEdit.Password)

        if ok:
            if manager.checkPassword(passw):
                pass
            else:
                self.infoPop(textTitle="Incorrect Password", textHeader="The Password is invalid")
                return
        else:
            return


        # if BoilerDict["Environment"]=="Standalone":
        #     manager=self._getManager()
        # else:
        #     manager = self.manager


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
        deletecategory_groupBox.setTitle(("Delete category"))
        deletecategory_groupBox.setObjectName(("deletecategory_groupBox"))

        self.selectcategory_comboBox = QtWidgets.QComboBox(deletecategory_groupBox)
        self.selectcategory_comboBox.setGeometry(QtCore.QRect(10, 20, 231, 22))
        self.selectcategory_comboBox.setObjectName(("selectcategory_comboBox"))

        # self.selectcategory_comboBox.addItems(manager._categories)
        self.selectcategory_comboBox.addItems(manager.getCategories())
        # userListSorted = manager._categories
        # for num in range(len(userListSorted)):
        #     self.selectuser_comboBox.addItem((userListSorted[num]))
        #     self.selectuser_comboBox.setItemText(num, (userListSorted[num]))

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
        # This method is NOT Software Specific
        passw, ok = QtWidgets.QInputDialog.getText(self, "Password Query",
                                               "Enter Admin Password:", QtWidgets.QLineEdit.Password)

        if ok:
            if self.manager.checkPassword(passw):
                pass
            else:
                self.infoPop(textTitle="Incorrect Password", textHeader="The Password is invalid")
                return
        else:
            return


        projectSettingsDB = self.manager.loadProjectSettings()

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
        buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).setMinimumSize(QtCore.QSize(100, 30))
        buttonBox.button(QtWidgets.QDialogButtonBox.Save).setMinimumSize(QtCore.QSize(100, 30))
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
            self.manager.saveProjectSettings(projectSettingsDB)
            projectSettings_Dialog.close()

        buttonBox.accepted.connect(onAccepted)
        buttonBox.rejected.connect(projectSettings_Dialog.reject)

        projectSettings_Dialog.show()

    def changePasswordUI(self):
        # This method is NOT Software Specific
        changePassword_Dialog = QtWidgets.QDialog(parent=self)
        changePassword_Dialog.setObjectName("projectSettings_Dialog")
        changePassword_Dialog.resize(270, 120)
        changePassword_Dialog.setMinimumSize(QtCore.QSize(270, 120))
        changePassword_Dialog.setMaximumSize(QtCore.QSize(270, 120))
        changePassword_Dialog.setWindowTitle("Project Settings")

        gridLayout = QtWidgets.QGridLayout(changePassword_Dialog)
        gridLayout.setObjectName(("gridLayout"))

        buttonBox = QtWidgets.QDialogButtonBox(changePassword_Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        buttonBox.setMaximumSize(QtCore.QSize(16777215, 30))
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Save)
        buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).setMinimumSize(QtCore.QSize(100, 30))
        buttonBox.button(QtWidgets.QDialogButtonBox.Save).setMinimumSize(QtCore.QSize(100, 30))
        buttonBox.setObjectName("buttonBox")

        gridLayout.addWidget(buttonBox, 1, 0, 1, 1)

        formLayout = QtWidgets.QFormLayout()
        formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        formLayout.setLabelAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        formLayout.setFormAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        formLayout.setObjectName("formLayout")

        oldPass_label = QtWidgets.QLabel(changePassword_Dialog)
        oldPass_label.setText("Old Password:")
        formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, oldPass_label)

        oldPass_lineEdit = QtWidgets.QLineEdit(changePassword_Dialog)
        oldPass_lineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, oldPass_lineEdit)


        newPass_label = QtWidgets.QLabel(changePassword_Dialog)
        newPass_label.setText("New Password:")
        newPass_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, newPass_label)

        newPass_lineEdit = QtWidgets.QLineEdit(changePassword_Dialog)
        newPass_lineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, newPass_lineEdit)

        newPassAgain_label = QtWidgets.QLabel(changePassword_Dialog)
        newPassAgain_label.setText("New Password Again:")
        newPassAgain_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, newPassAgain_label)

        newPassAgain_lineEdit = QtWidgets.QLineEdit(changePassword_Dialog)
        newPassAgain_lineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, newPassAgain_lineEdit)

        gridLayout.addLayout(formLayout, 0, 0, 1, 1)
        # SIGNALS
        # -------
        def onAccepted():

            if not self.manager.checkPassword(oldPass_lineEdit.text()):
                self.infoPop(textTitle="Incorrect Password", textHeader="Invalid Old Password", type="C")
                return
            if newPass_lineEdit.text() == "" or newPassAgain_lineEdit.text() == "":
                self.infoPop(textTitle="Error", textHeader="Admin Password cannot be blank", type="C")
                return
            if newPass_lineEdit.text() != newPassAgain_lineEdit.text():
                self.infoPop(textTitle="Error", textHeader="New passwords are not matching", type="C")
                return

            if self.manager.changePassword(oldPass_lineEdit.text(), newPass_lineEdit.text()):
                self.infoPop(textTitle="Success", textHeader="Password Changed", type="I")
                changePassword_Dialog.close()

        buttonBox.accepted.connect(onAccepted)
        buttonBox.rejected.connect(changePassword_Dialog.reject)

        changePassword_Dialog.show()

    def saveBaseSceneDialog(self):
        # This method IS Software Specific
        saveBaseScene_Dialog = QtWidgets.QDialog(parent=self)
        saveBaseScene_Dialog.setModal(True)
        saveBaseScene_Dialog.setObjectName(("save_Dialog"))
        saveBaseScene_Dialog.setWindowTitle("Save Base Scene")
        saveBaseScene_Dialog.resize(600, 350)

        sbs_masterLayout = QtWidgets.QVBoxLayout(saveBaseScene_Dialog)

        # headerLayout = QtWidgets.QHBoxLayout(saveBaseScene_Dialog)
        # sbs_masterLayout.addLayout(headerLayout)
        #
        # tikIcon_label = QtWidgets.QLabel()
        # tikIcon_label.setFixedSize(115, 30)
        # saveBaseHeaderBitmap = QtGui.QPixmap(os.path.join(self.manager.getIconsDir(), "tmMain.png"))
        # tikIcon_label.setPixmap(saveBaseHeaderBitmap)
        # tikIcon_label.setScaledContents(True)
        # headerLayout.addWidget(tikIcon_label)
        #
        # resolvedPath_label = QtWidgets.QLabel()
        # resolvedPath_label.setText((""))
        # resolvedPath_label.setIndent(12)
        # resolvedPath_label.setWordWrap(True)
        # headerLayout.addWidget(resolvedPath_label)


        # ----------
        # HEADER BAR
        # ----------
        margin = 5
        # barColor = "background-color: rgb(80,80,80);"
        # barColor = "background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #565656, stop: 0.1 #525252, stop: 0.5 #4e4e4e, stop: 0.9 #4a4a4a, stop: 1 #464646);"
        colorWidget = QtWidgets.QWidget(saveBaseScene_Dialog)
        headerLayout = QtWidgets.QHBoxLayout(colorWidget)
        headerLayout.setSpacing(0)
        try: headerLayout.setMargin(0)
        except AttributeError: pass

        tikIcon_label = QtWidgets.QLabel(self.centralwidget)
        # tikIcon_label.setFixedSize(115, 30)
        tikIcon_label.setObjectName("header")
        tikIcon_label.setMaximumWidth(150)
        try: tikIcon_label.setMargin(margin)
        except AttributeError: pass
        tikIcon_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        tikIcon_label.setScaledContents(False)
        # saveBaseHeaderBitmap = QtGui.QPixmap(os.path.join(self.manager.getIconsDir(), "tmBaseScene.png"))
        saveBaseHeaderBitmap = QtGui.QPixmap(":/icons/CSS/rc/tmBaseScene.png")
        tikIcon_label.setPixmap(saveBaseHeaderBitmap)

        headerLayout.addWidget(tikIcon_label)

        resolvedPath_label = QtWidgets.QLabel()
        resolvedPath_label.setObjectName("header")
        try:resolvedPath_label.setMargin(margin)
        except AttributeError: pass
        resolvedPath_label.setIndent(12)
        # resolvedPath_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        resolvedPath_label.setFont(QtGui.QFont("Times", 10, QtGui.QFont.Bold))
        resolvedPath_label.setWordWrap(True)

        headerLayout.addWidget(resolvedPath_label)


        # colorWidget.setStyleSheet(barColor)
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

        if BoilerDict["Environment"] == "Houdini" or BoilerDict["Environment"] == "Nuke":
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
        saveV_Dialog.setObjectName(("saveV_Dialog"))
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
        tikIcon_label.setObjectName("header")
        tikIcon_label.setMaximumWidth(114)
        try: tikIcon_label.setMargin(margin)
        except AttributeError: pass
        tikIcon_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        tikIcon_label.setScaledContents(False)
        # saveVersionHeaderBitmap = QtGui.QPixmap(os.path.join(self.manager.getIconsDir(), "tmVersion.png"))
        saveVersionHeaderBitmap = QtGui.QPixmap(":/icons/CSS/rc/tmVersion.png")
        tikIcon_label.setPixmap(saveVersionHeaderBitmap)

        headerLayout.addWidget(tikIcon_label)

        resolvedPath_label = QtWidgets.QLabel()
        resolvedPath_label.setObjectName("header")
        try: resolvedPath_label.setMargin(margin)
        except AttributeError: pass
        resolvedPath_label.setIndent(2)
        # resolvedPath_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        resolvedPath_label.setFont(QtGui.QFont("Times", 7, QtGui.QFont.Bold))
        resolvedPath_label.setWordWrap(True)

        headerLayout.addWidget(resolvedPath_label)


        # colorWidget.setStyleSheet(barColor)
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

        print self.manager.getSceneFile()
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

        if BoilerDict["Environment"] == "Houdini" or BoilerDict["Environment"] == "Nuke":
            makeReference_checkBox.setVisible(False)

        formats_horizontalLayout_2.addWidget(makeReference_checkBox)
        right_verticalLayout.addLayout(formats_horizontalLayout_2)

        sv_buttonBox = QtWidgets.QDialogButtonBox(saveV_Dialog)
        sv_buttonBox.setOrientation(QtCore.Qt.Horizontal)
        sv_buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        sv_buttonBox.setObjectName(("buttonBox"))
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

            # print "sceneFormat", sceneFormat
            sceneInfo = self.manager.saveVersion(makeReference=makeReference_checkBox.checkState(),
                                                 versionNotes=notes_plainTextEdit.toPlainText(),
                                                 sceneFormat=sceneFormat)

            if not sceneInfo == -1:
                self.statusBar().showMessage("Status | Version Saved => %s" % len(sceneInfo["Versions"]))
            self.manager.currentBaseSceneName = sceneInfo["Name"]
            self.manager.currentVersionIndex = len(sceneInfo["Versions"])

            currentRow = self.scenes_listWidget.currentRow()
            self.populateBaseScenes()
            self.onBaseSceneChange()
            logger.debug("row %s" %currentRow)
            self.scenes_listWidget.setCurrentRow(currentRow)
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
        addNotes_buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).setMinimumSize(QtCore.QSize(100, 30))
        addNotes_buttonBox.button(QtWidgets.QDialogButtonBox.Save).setMinimumSize(QtCore.QSize(100, 30))

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
        # self.version_comboBox.setStyleSheet("background-color: rgb(80,80,80); color: white")
        # self._vEnableDisable()
        self.onModeChange()
        # print "ASDFASDFASDFASDF"

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
            helpText.setStyleSheet("background-color: rgb(255, 255, 255);")
            helpText.setStyleSheet(""
                                   "border: 20px solid black;"
                                   "background-color: black;"
                                   "font-size: 16px"
                                   "")
            helpText.setText(textInfo)
            messageLayout.addWidget(helpText)

        if command == "viewRender":
            imagePath = os.path.join(manager.projectDir, "images", manager.currentBaseSceneName)
            ImageViewer.MainUI(manager.projectDir, relativePath=imagePath, recursive=True).show()

    def rcAction_thumb(self, command):
        # This method IS Software Specific
        manager = self._getManager()
        # print "comm: ", command
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

        row = self.scenes_listWidget.currentRow()
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
            self.scenes_rcItem_5.setEnabled(os.path.isdir(os.path.join(manager.projectDir, "images", manager.currentBaseSceneName)))
            self.scenes_rcItem_6.setEnabled(True)

        self.popMenu_scenes.exec_(self.scenes_listWidget.mapToGlobal(point))

    def onContextMenu_thumbnail(self, point):
        # This method is NOT Software Specific
        row = self.scenes_listWidget.currentRow()
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
        # manager = self._getManager()
        self.manager.currentUser = str(self.user_comboBox.currentText())

    def onModeChange(self):
        # This method is NOT Software Specific

        self._vEnableDisable()

        if self.load_radioButton.isChecked():
            self.loadScene_pushButton.setText("Load Scene")
            self.scenes_listWidget.setStyleSheet("border-style: solid; border-width: 2px; border-color: #242424;")
        else:
            self.loadScene_pushButton.setText("Reference Scene")
            self.scenes_listWidget.setStyleSheet("border-style: solid; border-width: 2px; border-color: cyan;")

        self.manager.currentMode = self.load_radioButton.isChecked()
        self.populateBaseScenes()

    def onBaseSceneChange(self):
        # This method IS Software Specific
        manager = self._getManager()
        self.version_comboBox.blockSignals(True)
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
        # This method IS Software Specific
        manager = self._getManager()


        if self.version_comboBox.currentIndex() is not -1:
            manager.currentVersionIndex = self.version_comboBox.currentIndex() + 1

        # self.version_comboBox.blockSignals(True)

        # clear Notes and verison combobox
        self.notes_textEdit.clear()

        # update notes
        self.notes_textEdit.setPlainText(manager.getNotes())


        # update thumb
        if FORCE_QT4:
            self.tPixmap = QtWidgets.QPixmap(manager.getThumbnail())
        else:
            self.tPixmap = QtGui.QPixmap(manager.getThumbnail())

        # self.tPixmap = QtGui.QPixmap(self.manager.getThumbnail())

        if self.tPixmap.isNull():
            self.thumbnail_label.setPixmap(self.E_tPixmap)
        else:
            self.thumbnail_label.setPixmap(self.tPixmap)

        if manager.currentVersionIndex != len(manager.getVersions()) and manager.currentVersionIndex != -1:
            self.version_comboBox.setStyleSheet("color: yellow")
        else:
            self.version_comboBox.setStyleSheet("color: white")

        # self.version_comboBox.blockSignals(False)
        self._vEnableDisable()

    def populateBaseScenes(self, deepCheck=False):
        # This method IS Software Specific
        manager = self._getManager()
        if not manager:
            return

        self.scenes_listWidget.blockSignals(True)
        self.scenes_listWidget.clear()
        # logger.debug("populateBaseScenes")
        baseScenesDict = manager.getBaseScenesInCategory()
        if self.reference_radioButton.isChecked():
            for key in baseScenesDict:
                if manager.checkReference(baseScenesDict[key]) == 1:
                    self.scenes_listWidget.addItem(key)
        else:
            if BoilerDict["Environment"] == "Standalone":
                codeDict = {-1: QtWidgets.QColor(255, 0, 0, 255), 1: QtWidgets.QColor(0, 255, 0, 255),
                            0: QtWidgets.QColor(255, 255, 0, 255), -2: QtWidgets.QColor(20, 20, 20, 255)}
            else:
                codeDict = {-1: QtGui.QColor(255, 0, 0, 255), 1: QtGui.QColor(0, 255, 0, 255),
                            0: QtGui.QColor(255, 255, 0, 255), -2: QtGui.QColor(20, 20, 20, 255)}  # dictionary for color codes red, green, yellow

            for key in sorted(baseScenesDict):
                retCode = manager.checkReference(baseScenesDict[key], deepCheck=deepCheck) # returns -1, 0 or 1 for color ref
                color = codeDict[retCode]
                listItem = QtWidgets.QListWidgetItem()
                listItem.setText(key)
                listItem.setForeground(color)
                self.scenes_listWidget.addItem(listItem)
        self.scenes_listWidget.blockSignals(False)

    def onLoadScene(self):
        # This method IS Software Specific. BUT overriding it is better, so it is not selecting manager

        row = self.scenes_listWidget.currentRow()
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
        currentRow = self.scenes_listWidget.currentRow()
        self.populateBaseScenes()
        self.scenes_listWidget.setCurrentRow(currentRow)

    def onShowPreview(self):
        # This method IS Software Specific.
        manager = self._getManager()

        row = self.scenes_listWidget.currentRow()
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
                tempAction.triggered.connect(lambda ignore, item=z: manager.playPreview(str(item)))

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

        row = self.scenes_listWidget.currentRow()
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

        row = self.scenes_listWidget.currentRow()
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
        # if openSceneInfo: ## getSceneInfo returns None if there is no json database fil
        #     self.baseScene_lineEdit.setText("%s ==> %s ==> %s" % (openSceneInfo["subProject"], openSceneInfo["category"], openSceneInfo["shotName"]))
        #     self.baseScene_lineEdit.setStyleSheet("background-color: rgb(40,40,40); color: cyan")
        # else:
        #     self.baseScene_lineEdit.setText("Current Scene is not a Base Scene")
        #     self.baseScene_lineEdit.setStyleSheet("background-color: rgb(40,40,40); color: yellow")

        if openSceneInfo:
            jList = []
            if openSceneInfo["subProject"] != "None":
                jList.append(openSceneInfo["subProject"])
            jList.extend([openSceneInfo["category"], openSceneInfo["shotName"]])
            dMsg = " > ".join(jList)
            self.baseScene_label.setText(dMsg)
            # self.baseScene_label.setStyleSheet("background-color: rgb(40,40,40); color: cyan")
            self.baseScene_label.setStyleSheet("color: cyan")
        else:
            self.baseScene_label.setText("Current Scene is not a Base Scene")
            # self.baseScene_label.setStyleSheet("background-color: rgb(40,40,40); color: yellow")
            self.baseScene_label.setStyleSheet("color: yellow")

    def _checkValidity(self, text, button, lineEdit, allowSpaces=False, directory=False):
        if text == "":
            return False
        if self.manager.nameCheck(text, allowSpaces=allowSpaces, directory=directory):
            lineEdit.setStyleSheet("background-color: rgb(40,40,40); color: white")
            button.setEnabled(True)
            return True
        else:
            lineEdit.setStyleSheet("background-color: red; color: black")
            button.setEnabled(False)
            return False

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
            vCheck_mBox.button(QtWidgets.QMessageBox.Cancel).setMinimumSize(QtCore.QSize(100, 30))
            vCheck_mBox.button(QtWidgets.QMessageBox.Save).setMinimumSize(QtCore.QSize(100, 30))
            vCheck_mBox.button(QtWidgets.QMessageBox.Help).setMinimumSize(QtCore.QSize(100, 30))

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
            vCheck_mBox.button(QtWidgets.QMessageBox.Ok).setMinimumSize(QtCore.QSize(100, 30))

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
