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


"""Global Module for all Sm softwares
Creates a tree structure for image sequences
Image sequences can be listed recursively if the checkbox is checked.
Meaning all the sequence under the selected folder will be listed
recursively.
Double clicking on the seguence will execute the file on the defined application
"""

import os
import sys

# ---------------
# GET ENVIRONMENT
# ---------------
# import tik_manager._version as _version
import _version
# import tik_manager.compatibility as compat
import compatibility as compat

BoilerDict = {"Environment": "Standalone",
              "MainWindow": None,
              "WindowTitle": "Image Viewer Standalone v%s" % _version.__version__,
              }
try:
    from maya import OpenMayaUI as omui
    import maya.cmds as cmds
    import Qt
    from Qt import QtWidgets, QtCore, QtGui
    from tik_manager.coreFunctions.coreFunctions_Maya import MayaCoreFunctions as CoreFunctions
    BoilerDict["Environment"] = "Maya"
    BoilerDict["WindowTitle"] = "Image Viewer Maya v%s" % _version.__version__
except ImportError:
    pass

try:
    import MaxPlus
    import Qt
    from Qt import QtWidgets, QtCore, QtGui
    from tik_manager.coreFunctions.coreFunctions_Max import MaxCoreFunctions as CoreFunctions
    BoilerDict["Environment"] = "3dsMax"
    BoilerDict["WindowTitle"] = "Image Viewer 3ds Max v%s" % _version.__version__

except ImportError:
    pass

try:
    import hou
    import Qt
    from Qt import QtWidgets, QtCore, QtGui
    from tik_manager.coreFunctions.coreFunctions_Houdini import HoudiniCoreFunctions as CoreFunctions
    BoilerDict["Environment"] = "Houdini"
    BoilerDict["WindowTitle"] = "Image Viewer Houdini v%s" % _version.__version__
except ImportError:
    pass

try:
    import nuke
    import Qt
    from Qt import QtWidgets, QtCore, QtGui
    from tik_manager.coreFunctions.coreFunctions_Nuke import NukeCoreFunctions as CoreFunctions
    BoilerDict["Environment"] = "Nuke"
    BoilerDict["WindowTitle"] = "Image Viewer Nuke v%s" % _version.__version__
except ImportError:
    pass

try:
    from PyQt5 import QtWidgets, QtCore, QtGui
    CoreFunctions = object
    BoilerDict["Environment"] = "Standalone"
    BoilerDict["WindowTitle"] = "Image Viewer Standalone v%s" % _version.__version__
    FORCE_QT5 = True
except ImportError:
    FORCE_QT5 = False

try:
    from PyQt5 import QtWidgets, QtCore, QtGui
    FORCE_QT5 = True
    if bool(os.getenv("PS_APP")):  # if the request is coming from the SmPhotoshop
        from tik_manager.coreFunctions.coreFunctions_PS import PsCoreFunctions as CoreFunctions
        BoilerDict["Environment"] = "Photoshop"  # technically it is still standalone...
        BoilerDict["WindowTitle"] = "Image Viewer Photoshop v%s" % _version.__version__
    else:
        CoreFunctions = object
        BoilerDict["Environment"] = "Standalone"
        BoilerDict["WindowTitle"] = "Image Viewer Standalone v%s" % _version.__version__
except ImportError:
    FORCE_QT5 = False



## DO NOT REMOVE THIS:
# import tik_manager.iconsSource as icons
import iconsSource as icons
## DO NOT REMOVE THIS:

# PyInstaller and Standalone version compatibility

## SAFE BLOCK
## ----------
# FORCE_QT5 = bool(int(os.environ["FORCE_QT5"]))
# if FORCE_QT5:
#     from PyQt4 import QtCore, Qt
#     from PyQt4 import QtGui as QtWidgets
# else:
#     import Qt
#     from Qt import QtWidgets, QtCore, QtGui
## ----------

# for standalone compatibility uncomment following 3 and disable safe block
# FORCE_QT5 = True
# from PyQt4 import QtCore, Qt
# from PyQt4 import QtGui as QtWidgets

# import tik_manager.pyseq as seq
import pyseq as seq

import datetime
from shutil import copyfile
# from tik_manager.SmRoot import RootManager
from SmRoot import RootManager


import logging



__author__ = "Arda Kutlu"
__copyright__ = "Copyright 2018, Image Viewer"
__credits__ = []
__license__ = "GPL"
__maintainer__ = "Arda Kutlu"
__email__ = "ardakutlu@gmail.com"
__status__ = "Development"


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


# def getProject():
#     """Returns the project folder"""
#     if BoilerDict["Environment"] == "Maya":
#         return os.path.normpath(cmds.workspace(q=1, rd=1))
#     elif BoilerDict["Environment"] == "3dsMax":
#         return os.path.normpath(MaxPlus.PathManager.GetProjectFolderDir())
#     elif BoilerDict["Environment"] == "Houdini":
#         return os.path.normpath((hou.hscript('echo $JOB')[0])[:-1])  # [:-1] is for the extra \n
#     elif BoilerDict["Environment"] == "Nuke":
#         # TODO // Needs a project getter for nuke
#         return os.path.normpath(os.path.join(os.path.expanduser("~")))
#     else:
#         return os.path.normpath(os.path.join(os.path.expanduser("~")))


# def folderCheck(folder):
#     """Checks if the folder exists, creates it if it doesnt"""
#     if not os.path.isdir(os.path.normpath(folder)):
#         os.makedirs(os.path.normpath(folder))

class ImageViewer(RootManager, CoreFunctions):
    def __init__(self, projectPath=None):
        super(ImageViewer, self).__init__()

        # self.swName = "" if BoilerDict["Environment"] == "Standalone" else BoilerDict["Environment"]
        self.swName = BoilerDict["Environment"]
        self.init_paths(self.swName)
        self.init_database()

    def init_paths(self, nicename):
        """Initializes all the necessary paths"""

        self._pathsDict["userSettingsDir"] = os.path.normpath(os.path.join(self.getUserDir(), "TikManager"))
        self._folderCheck(os.path.join(self._pathsDict["userSettingsDir"], nicename))
        self._pathsDict["userSettingsFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], "userSettings.json"))

        self._pathsDict["localBookmarksFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], nicename, "smBookmarks.json"))
        self._pathsDict["bookmarksFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], "smBookmarks.json"))
        self._pathsDict["recentProjectsFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], "smRecentProjects.json"))
        self._pathsDict["currentsFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], nicename, "smCurrents.json"))
        self._pathsDict["projectsFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], "smProjects.json"))

        self._pathsDict["commonFolderFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], "smCommonFolder.json"))

        self._pathsDict["sharedSettingsDir"] = self._getCommonFolder()
        if self._pathsDict["sharedSettingsDir"] == -1:
            self._exception(201, "Cannot Continue Without Common Database")
            return -1
        # if self.swName:
        # _softwarePathsDict = self.getSoftwarePaths()
        self._pathsDict["projectDir"] = self.getProjectDir()
        self._pathsDict["sceneFile"] = ""
        self._pathsDict["masterDir"] = os.path.normpath(os.path.join(self._pathsDict["projectDir"], "smDatabase"))
        self._pathsDict["transferDir"] = os.path.normpath(os.path.join(self._pathsDict["projectDir"], "_TRANSFER"))
        self._pathsDict["projectSettingsFile"] = os.path.normpath(os.path.join(self._pathsDict["masterDir"], "projectSettings.json"))
        self._pathsDict["subprojectsFile"] = os.path.normpath(os.path.join(self._pathsDict["masterDir"], "subPdata.json"))
        self._pathsDict["exportSettingsFile"] = os.path.normpath(os.path.join(self._pathsDict["masterDir"], "exportSettings.json"))
        self._pathsDict["importSettingsFile"] = os.path.normpath(os.path.join(self._pathsDict["masterDir"], "importSettings.json"))
        self._pathsDict["previewsRoot"] = os.path.normpath(os.path.join(self._pathsDict["projectDir"], "Playblasts")) # dont change

        self._pathsDict["usersFile"] = os.path.normpath(os.path.join(self._pathsDict["sharedSettingsDir"], "sceneManagerUsers.json"))
        self._pathsDict["alImportSettingsFile"] = os.path.normpath(os.path.join(self._pathsDict["sharedSettingsDir"], "alImportSettings.json"))
        self._pathsDict["alExportSettingsFile"] = os.path.normpath(os.path.join(self._pathsDict["sharedSettingsDir"], "alExportSettings.json"))
        self._pathsDict["softwareDatabase"] = os.path.normpath(os.path.join(self._pathsDict["sharedSettingsDir"], "softwareDatabase.json"))
        self._pathsDict["sceneManagerDefaults"] = os.path.normpath(os.path.join(self._pathsDict["sharedSettingsDir"], "sceneManagerDefaults.json"))
        self._pathsDict["tikConventions"] = os.path.normpath(os.path.join(self._pathsDict["sharedSettingsDir"], "tikConventions.json"))
        self._pathsDict["adminPass"] = os.path.normpath(os.path.join(self._pathsDict["sharedSettingsDir"], "adminPass.psw"))

    def init_database(self):
        self._sceneManagerDefaults = self.loadManagerDefaults()
        self._userSettings = self.loadUserSettings()


class MainUI(QtWidgets.QMainWindow):
    """Main UI function"""

    def __init__(self, projectPath=None, relativePath=None, recursive=False):
        for entry in QtWidgets.QApplication.allWidgets():
            try:
                if entry.objectName() == BoilerDict["WindowTitle"]:
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

        self.imageViewer = ImageViewer()
        self.projectPath = self.imageViewer.getProjectDir()


        if relativePath:
            self.rootPath = os.path.join(self.projectPath, str(relativePath))
        else:
            # setting the project path as the root seems like a better option
            self.rootPath = os.path.join(self.projectPath)
            if not os.path.isdir(self.rootPath):
                self.rootPath = self.projectPath

        self.databaseDir = os.path.normpath(os.path.join(self.projectPath, "smDatabase"))

        if not os.path.isdir(self.databaseDir):
            msg = ["Nothing to view", "No Scene Manager Database",
                   "There is no Scene Manager Database Folder in this project path"]
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

        self.recursiveInitial = recursive

        self._generator = None
        self._timerId = None

        # self.sequenceData = []
        self.sequenceData = {}

        self.extensionDictionary = {"jpg": ["*.jpg", "*.jpeg"],
                                    "png": ["*.png"],
                                    "exr": ["*.exr"],
                                    "tif": ["*.tif", "*.tiff"],
                                    "tga": ["*.tga"]
                                    }

        self.filterList = sum(self.extensionDictionary.values(), [])

        self.setObjectName(BoilerDict["WindowTitle"])
        self.resize(1000, 624)
        self.setWindowTitle(BoilerDict["WindowTitle"])
        self.centralwidget = QtWidgets.QWidget(self)
        self.model = QtWidgets.QFileSystemModel()
        self.model.setRootPath(self.rootPath)
        self.model.setFilter(QtCore.QDir.AllDirs | QtCore.QDir.NoDotAndDotDot)
        self.tLocation = self.getRaidPath()
        self.buildUI()

        self.setCentralWidget(self.centralwidget)

    def buildUI(self):
        """Elements of the Main UI"""
        masterLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        # ----------
        # HEADER BAR
        # ----------
        margin = 5
        self.colorBar = QtWidgets.QLabel()
        self.colorBar.setStyleSheet("background-color: %s;" %self.imageViewer.getColorCoding())
        masterLayout.addWidget(self.colorBar)
        # pyside does not have setMargin attribute
        try: self.colorBar.setMargin(0)
        except AttributeError: pass
        self.colorBar.setIndent(0)
        self.colorBar.setMaximumHeight(1)

        colorWidget = QtWidgets.QWidget(self.centralwidget)
        colorWidget.setProperty("header", True)
        colorWidget.setStyleSheet("")
        headerLayout = QtWidgets.QHBoxLayout(colorWidget)
        headerLayout.setSpacing(0)
        try: headerLayout.setMargin(0)
        except AttributeError: pass


        colorWidget = QtWidgets.QWidget(self.centralwidget)
        colorWidget.setMaximumHeight(60)
        colorWidget.setProperty("header", True)
        colorWidget.setStyleSheet("")
        headerLayout = QtWidgets.QHBoxLayout(colorWidget)
        headerLayout.setSpacing(0)
        # headerLayout.setContentsMargins(100, -1, -1, -1)
        try: headerLayout.setMargin(0)
        except AttributeError: pass

        tikIcon_label = QtWidgets.QLabel(self.centralwidget)
        tikIcon_label.setProperty("header", True)
        tikIcon_label.setStyleSheet("")
        try: tikIcon_label.setMargin(margin)
        except AttributeError: pass
        tikIcon_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        tikIcon_label.setScaledContents(False)

        headerBitmap = QtGui.QPixmap(":/icons/CSS/rc/tmImageViewer.png")
        tikIcon_label.setPixmap(headerBitmap)

        headerLayout.addWidget(tikIcon_label)

        self.baseScene_label = QtWidgets.QLabel(self.centralwidget)
        self.baseScene_label.setProperty("header", True)
        self.baseScene_label.setStyleSheet("")
        try: self.baseScene_label.setMargin(margin)
        except AttributeError: pass
        self.baseScene_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        self.baseScene_label.setFont(QtGui.QFont("Times", 10, QtGui.QFont.Bold))

        # self.baseScene_label.setFont(self.displayFont)
        headerLayout.addWidget(self.baseScene_label)

        self.managerIcon_label = QtWidgets.QLabel(self.centralwidget)
        self.managerIcon_label.setProperty("header", True)
        self.managerIcon_label.setStyleSheet("")
        try: self.managerIcon_label.setMargin(margin)
        except AttributeError: pass
        self.managerIcon_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.managerIcon_label.setScaledContents(False)

        headerLayout.addWidget(self.managerIcon_label)

        masterLayout.addWidget(colorWidget)
        # ----------
        # ----------


        self.gridLayout = QtWidgets.QGridLayout()
        masterLayout.addLayout(self.gridLayout)

        self.recursive_checkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.recursive_checkBox.setText(("Recursive"))
        self.recursive_checkBox.setChecked(self.recursiveInitial)
        self.gridLayout.addWidget(self.recursive_checkBox, 0, 3, 1, 1)

        self.rootFolder_label = QtWidgets.QLabel(self.centralwidget)
        self.rootFolder_label.setFrameShape(QtWidgets.QFrame.Box)
        self.rootFolder_label.setLineWidth(1)
        self.rootFolder_label.setText(("Root Folder:"))
        self.rootFolder_label.setTextFormat(QtCore.Qt.AutoText)
        self.rootFolder_label.setScaledContents(False)
        self.gridLayout.addWidget(self.rootFolder_label, 0, 0, 1, 1)

        self.rootFolder_lineEdit = DropLineEdit(self.centralwidget)
        self.rootFolder_lineEdit.setText((self.rootPath))
        self.rootFolder_lineEdit.setReadOnly(False)
        self.rootFolder_lineEdit.setPlaceholderText((""))
        self.gridLayout.addWidget(self.rootFolder_lineEdit, 0, 1, 1, 1)

        self.browse_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.browse_pushButton.setText(("Browse"))
        self.gridLayout.addWidget(self.browse_pushButton, 0, 2, 1, 1)

        self.raidFolder_label = QtWidgets.QLabel(self.centralwidget)
        self.raidFolder_label.setFrameShape(QtWidgets.QFrame.Box)
        self.raidFolder_label.setLineWidth(1)
        self.raidFolder_label.setText(("Remote Location:"))
        self.raidFolder_label.setTextFormat(QtCore.Qt.AutoText)
        self.raidFolder_label.setScaledContents(False)
        self.gridLayout.addWidget(self.raidFolder_label, 1, 0, 1, 1)

        self.raidFolder_lineEdit = DropLineEdit(self.centralwidget)
        self.raidFolder_lineEdit.setText(self.tLocation)
        self.raidFolder_lineEdit.setReadOnly(False)
        self.raidFolder_lineEdit.setPlaceholderText((""))
        self.gridLayout.addWidget(self.raidFolder_lineEdit, 1, 1, 1, 1)

        self.browseRaid_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.browseRaid_pushButton.setText(("Browse"))
        self.gridLayout.addWidget(self.browseRaid_pushButton, 1, 2, 1, 1)

        self.transferTo = QtWidgets.QPushButton()
        self.transferTo.setText("Transfer Files")
        if self.tLocation == "N/A":
            self.transferTo.setEnabled(False)
        else:
            self.transferTo.setEnabled(True)
        self.gridLayout.addWidget(self.transferTo, 1, 3, 1, 1)


##
        self.chkboxLayout = QtWidgets.QHBoxLayout()
        self.chkboxLayout.setAlignment(QtCore.Qt.AlignRight)

        self.checkboxes = []
        for key in (self.extensionDictionary.keys()):
            tCheck = QtWidgets.QCheckBox()
            tCheck.setText(key)
            tCheck.setChecked(True)
            self.chkboxLayout.addWidget(tCheck)
            tCheck.toggled.connect(lambda state, item=self.extensionDictionary[key]: self.onCheckbox(item, state))
            self.checkboxes.append(tCheck)

        self.selectAll_pushbutton = QtWidgets.QPushButton()
        self.selectAll_pushbutton.setText("Select All")

        self.selectNone_pushbutton = QtWidgets.QPushButton()
        self.selectNone_pushbutton.setText("Select None")

        spacerItem = QtWidgets.QSpacerItem(400, 25, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)

        self.chkboxLayout.addWidget(self.selectAll_pushbutton)
        self.chkboxLayout.addWidget(self.selectNone_pushbutton)
        self.chkboxLayout.addItem(spacerItem)
##
        self.gridLayout.addLayout(self.chkboxLayout, 2, 0, 1, 4)

        # Splitter LEFT side:

        self.directories_treeView = DeselectableTreeView(self.centralwidget)
        self.directories_treeView.setModel(self.model)
        self.directories_treeView.setRootIndex(self.model.index(self.rootPath))
        self.directories_treeView.setSortingEnabled(True)
        self.directories_treeView.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.directories_treeView.setColumnWidth(0, 250)
        # self.directories_treeView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.directories_treeView.hideColumn(1)
        self.directories_treeView.hideColumn(2)
        self.directories_treeView.setContentsMargins(0, 0, 0, 0)
        self.directories_treeView.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.left_layout = QtWidgets.QVBoxLayout()
        self.left_layout.setSpacing(0)
        self.left_layout.addWidget(self.directories_treeView)
        self.left_layout.setContentsMargins(0, 0, 0, 0)

        self.left_widget = QtWidgets.QFrame()
        self.left_widget.setContentsMargins(0, 0, 0, 0)
        self.left_widget.setLayout(self.left_layout)

        # Splitter Right Side:

        self.sequences_treeWidget = QtWidgets.QTreeWidget(self.centralwidget)
        self.sequences_treeWidget.setToolTip((""))
        self.sequences_treeWidget.setStatusTip((""))
        self.sequences_treeWidget.setSortingEnabled(True)
        header = QtWidgets.QTreeWidgetItem(["Name", "Date"])
        self.sequences_treeWidget.setColumnWidth(0, 250)
        self.sequences_treeWidget.setHeaderItem(header)
        self.sequences_treeWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        # self.sequences_listWidget = QtWidgets.QListWidget(self.centralwidget)
        # self.sequences_listWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.nameFilter_label = QtWidgets.QLabel(self.centralwidget)
        self.nameFilter_label.setText("Filter:")
        self.nameFilter_lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.nameFilterApply_pushButton = QtWidgets.QPushButton(self.centralwidget, text="Apply")

        self.right_layout = QtWidgets.QVBoxLayout()
        self.right_layout.addWidget(self.sequences_treeWidget)

        nameFilter_layout = QtWidgets.QHBoxLayout()
        nameFilter_layout.addWidget(self.nameFilter_label)
        nameFilter_layout.addWidget(self.nameFilter_lineEdit)
        nameFilter_layout.addWidget(self.nameFilterApply_pushButton)

        self.right_layout.addLayout(nameFilter_layout)
        self.right_layout.setContentsMargins(0, 0, 0, 0)

        self.right_widget = QtWidgets.QFrame()
        self.right_widget.setLayout(self.right_layout)
        self.right_widget.setContentsMargins(0, 0, 0, 0)

        ######

        self.splitter = QtWidgets.QSplitter(parent=self)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setHandleWidth(8)
        self.splitter.addWidget(self.left_widget)
        self.splitter.addWidget(self.right_widget)
        # self.splitter.setStretchFactor(1, 0)

        self.gridLayout.addWidget(self.splitter, 3, 0, 1, 4)
        self.splitter.setStretchFactor(0, 0)

        self.browse_pushButton.clicked.connect(self.onBrowse)
        # Below line causes to a segmentation fault, so splitted into two
        # self.directories_treeView.selectionModel().selectionChanged.connect(self.populate)
        selectionModel = self.directories_treeView.selectionModel()
        selectionModel.selectionChanged.connect(self.populate)
        self.recursive_checkBox.toggled.connect(self.populate)
        self.sequences_treeWidget.doubleClicked.connect(self.onRunItem)
        self.browseRaid_pushButton.clicked.connect(self.onBrowseRaid)

        self.rootFolder_lineEdit.editingFinished.connect(self.onEditRoot)
        self.raidFolder_lineEdit.editingFinished.connect(self.onEditRaid)

        # -----------------
        # RIGHT CLICK MENUS
        # -----------------

        # SEQUENCE RC
        # -----------

        self.sequences_treeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.sequences_treeWidget.customContextMenuRequested.connect(self.onContextMenu_images)
        self.popMenu = QtWidgets.QMenu()

        rcAction_0 = QtWidgets.QAction('Show in Explorer', self)
        rcAction_1 = QtWidgets.QAction('Transfer Files to Raid', self)
        rcAction_4 = QtWidgets.QAction('Import Sequences', self)
        if BoilerDict["Environment"] == "Standalone":
            rcAction_4.setDisabled(True)
        self.popMenu.addAction(rcAction_0)
        self.popMenu.addAction(rcAction_1)
        self.popMenu.addAction(rcAction_4)

        # ROOT and RAID Folder RC
        # -----------------------
        self.rootFolder_label.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.raidFolder_label.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.rootFolder_label.customContextMenuRequested.connect(self.onContextMenu_labels)
        self.raidFolder_label.customContextMenuRequested.connect(self.onContextMenu_labels)
        self.popMenuLabels = QtWidgets.QMenu()

        rcAction_2 = QtWidgets.QAction('Show Root Folder in Explorer', self)
        rcAction_3 = QtWidgets.QAction('Show Transfer Folder in Explorer', self)
        self.popMenuLabels.addAction(rcAction_2)
        self.popMenuLabels.addAction(rcAction_3)

        ## SIGNAL CONNECTIONS
        rcAction_0.triggered.connect(self.onShowInExplorer)
        rcAction_1.triggered.connect(self.onTransferFiles)
        rcAction_4.triggered.connect(self.onImportSequence)


        # rcAction_2.triggered.connect(lambda: self.onShowInExplorer(path=unicode(self.rootFolder_lineEdit.text())))
        rcAction_2.triggered.connect(lambda: self.onShowInExplorer(path=compat.decode(self.rootFolder_lineEdit.text())))
        # rcAction_3.triggered.connect(lambda: self.onShowInExplorer(path=unicode(self.raidFolder_lineEdit.text())))
        rcAction_3.triggered.connect(lambda: self.onShowInExplorer(path=compat.decode(self.raidFolder_lineEdit.text())))


        self.rootFolder_lineEdit.dropped.connect(self.setRootPath)
        self.raidFolder_lineEdit.dropped.connect(self.setRaidPath)

        self.selectAll_pushbutton.clicked.connect(self.selectAll)
        self.selectNone_pushbutton.clicked.connect(self.selectNone)
        self.directories_treeView.deselected.connect(self.deselectTree)

        self.nameFilterApply_pushButton.clicked.connect(self.populate)
        self.nameFilter_lineEdit.returnPressed.connect(self.populate)

        self.transferTo.clicked.connect(self.onTransferFiles)

        # SHORTCUTS
        # ---------

        # PyInstaller and Standalone version compatibility

        shortcutRefresh = QtWidgets.QShortcut(QtGui.QKeySequence("F5"), self, self.populate)

        self.populate()

    def deselectTree(self):
        """Method for clearing the selection"""
        self.directories_treeView.setCurrentIndex(self.model.index(self.rootPath))
        self.populate()

    def selectAll(self):
        """Checks all checkboxes"""
        for c in self.checkboxes:
            c.setChecked(True)

    def selectNone(self):
        """Clears all checkboxes"""
        for c in self.checkboxes:
            c.setChecked(False)

    def setRootPath(self, dir):
        """Declares the given directory as the root of the tree view"""
        dir = str(dir)
        self.rootPath = dir
        self.directories_treeView.reset()
        self.model.setRootPath(dir)
        self.directories_treeView.setRootIndex(self.model.index(dir))
        self.rootFolder_lineEdit.setText(os.path.normpath(dir))
        self.sequences_treeWidget.clear()

    def getRaidPath(self):
        """
        Returns the absolute path of remote transfer location from database file
        If data base file does not exists, creates it
        """
        tLocationFile = os.path.normpath(os.path.join(self.databaseDir, "tLocation.json"))
        if os.path.isfile(tLocationFile):
            tLocation = self.imageViewer._loadJson(tLocationFile)
            # self.transferTo.setEnabled(True)
        else:
            tLocation = "N/A"
            # self.transferTo.setEnabled(False)
            self.imageViewer._dumpJson(tLocation, tLocationFile)
        return tLocation

    def setRaidPath(self, dir):
        """Updates the Remote Location Folder database"""
        tLocationFile = os.path.normpath(os.path.join(self.databaseDir, "tLocation.json"))
        # self.tLocation = unicode(dir).encode("utf-8")
        self.tLocation = compat.encode(dir)
        self.imageViewer._dumpJson(self.tLocation, tLocationFile)
        self.raidFolder_lineEdit.setText(self.tLocation)

    def onCheckbox(self, extensions, state):
        """adds and removes the extensions according to the checkbox state"""
        if state:
            self.filterList += extensions
        else:
            self.filterList = list(set(self.filterList) - set(extensions))
        self.populate()

    # @Qt.QtCore.pyqtSlot("QItemSelection, QItemSelection")
    def onContextMenu_images(self, point):
        """Method to pop the menu at the position of the mouse cursor"""
        # print se
        if not self.sequences_treeWidget.currentIndex().row() is -1:
            self.popMenu.exec_(self.sequences_treeWidget.mapToGlobal(point))

    def onContextMenu_labels(self, point):
        """Method to pop the menu at the position of the mouse cursor"""
        self.popMenuLabels.exec_(self.centralwidget.mapToGlobal(point))

    def onEditRoot(self):
        # candidatePath = unicode(self.rootFolder_lineEdit.text()).encode("utf-8")
        candidatePath = compat.encode(self.rootFolder_lineEdit.text())
        if os.path.isdir(candidatePath):
            self.setRootPath(candidatePath)
        else:
            self.rootFolder_lineEdit.setText(self.rootPath)
            self.infoPop(textTitle="Invalid Path", textHeader="Entered path is invalid")


    def onEditRaid(self):
        # candidatePath = unicode(self.raidFolder_lineEdit.text()).encode("utf-8")
        candidatePath = compat.encode(self.raidFolder_lineEdit.text())
        if candidatePath == "" or candidatePath == "N/A":
            self.setRaidPath("N/A")
            self.transferTo.setEnabled(False)
            return
        if os.path.isdir(candidatePath):
            self.setRaidPath(candidatePath)
            self.transferTo.setEnabled(True)

            return
        else:
            self.raidFolder_lineEdit.setText(self.tLocation)
            self.infoPop(textTitle="Invalid Path", textHeader="Entered path is invalid")
            return

    def onBrowse(self):
        """Opens a directory select menu to define it as the root path"""
        dir = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory", self.rootPath))
        if dir:
            self.setRootPath(dir)
        else:
            return

    def onBrowseRaid(self):
        """Opens a directory select menu to define it as the remote location path"""
        path = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory", self.tLocation))
        if path:
            self.setRaidPath(path)
            self.transferTo.setEnabled(True)
            return

    def onTransferFiles(self):
        """Transfer sequences to the remote location"""
        if self.tLocation == "N/A":
            self.infoPop(textTitle="Cannot Continue", textHeader="Remote Location is not defined")
            # raise Exception([341], "Raid Location not defined")
            return

        selectedItemNames = [x.text(0) for x in self.sequences_treeWidget.selectedItems()]
        if len(selectedItemNames) == 0:
            self.infoPop(textTitle="Cannot Continue", textHeader="No sequence selected")
            # raise Exception([101], "No sequence selected")
            return

        logPath = os.path.join(self.databaseDir, "transferLogs")
        self.imageViewer._folderCheck(logPath)

        seqCopy = SeqCopyProgress()
        seqCopy.copysequence(self.sequenceData, selectedItemNames, self.tLocation, logPath, self.rootPath)

    def onImportSequence(self):
        """Executes the import sequence command"""
        selectedItemNames = [x.text(0) for x in self.sequences_treeWidget.selectedItems()]
        # importSequence(selectedItemNames)

        for itemName in selectedItemNames:
            seq = self.sequenceData[str(itemName)]
            self.imageViewer._importSequence(seq)


    def onShowInExplorer(self, path=None):
        """Open the folder of sequence in explorer"""
        if path:
            path = os.path.normpath(path) # just in case
            os.startfile(path)
            return

        selectedItemNames = [x.text(0) for x in self.sequences_treeWidget.selectedItems()]
        if len(selectedItemNames) == 0:
            raise Exception([101], "No sequence selected")
            return

        for itemName in selectedItemNames:
            seq = self.sequenceData[str(itemName)]
            # os.startfile(seq.dirname)
            self.imageViewer.showInExplorer(seq.dirname)

    def populate(self):
        """Search for sequences"""

        self.sequences_treeWidget.clear()  # fresh page
        # self.sequenceData = []  # clear the custom list
        self.sequenceData = {}  # clear the custom dictionary

        # if no filter extension selected, stop iterating through folders
        if not self.filterList:
            self.stop()
            return

        index = self.directories_treeView.currentIndex()

        # indexes = [x for x in self.directories_treeView.selectedIndexes()]
        # paths = self.uniqueList([str(self.model.filePath(i)) for i in indexes])

        if index.row() == -1:  # no row selected
            pathList = [self.rootPath]
        else:
            indexes = [x for x in self.directories_treeView.selectedIndexes()]
            pathList = self.uniqueList([str(self.model.filePath(i)) for i in indexes])

        # genList = [seq.walk(path, level=rec, includes=filter) for path in pathList]
        # self.stop()  # Stop any existing Timer
        # self._generator = self.listingLoop(genList)  # start the loop
        # self._timerId = self.startTimer(0)  # idle timer

        if index.row() == -1:  # no row selected
            fullPath = self.rootPath
        else:
            fullPath = str(self.model.filePath(index))

        if self.recursive_checkBox.isChecked():
            rec = -1
        else:
            rec = 1

        # convert filterList to tuple
        filter = (f for f in self.filterList)
        # create a generator
        # genList = seq.walk(pathList[0], level=rec, includes=filter)
        genList = [seq.walk(path, level=rec, includes=filter) for path in pathList]

        self.stop()  # Stop any existing Timer
        self._generator = self.listingLoop(genList)  # start the loop
        self._timerId = self.startTimer(0)  # idle timer


    def listingLoop(self, genList):
        """Add found sequences to the List widget"""
        for gen in genList:
            for x in gen:
                for i in x[2]:
                    QtWidgets.QApplication.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
                    # filtertest
                    filterWord = str(self.nameFilter_lineEdit.text())
                    if filterWord != "" and filterWord.lower() not in i.lower():
                        continue

                    itemName = i.format('%h%t %R')
                    self.sequenceData[itemName] = i
                    # self.sequenceData.append(i)
                    # self.sequences_listWidget.addItem(i.format('%h%t %R'))
                    firstImagePath = os.path.join(os.path.normpath(i.dirname), i.name)
                    timestamp = os.path.getmtime(firstImagePath)
                    timestampFormatted = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                    item = QtWidgets.QTreeWidgetItem(self.sequences_treeWidget, [itemName, str(timestampFormatted)])
                    self.sequences_treeWidget.sortItems(1, QtCore.Qt.AscendingOrder)  # 1 is Date Column, 0 is Ascending order

                    yield

    def onRunItem(self):
        """Execute the sequence"""
        itemName = str(self.sequences_treeWidget.currentItem().text(0))
        seq = self.sequenceData[itemName]
        # row = self.sequences_treeWidget.currentRow()
        # item = self.sequenceData[row]
        firstImagePath = os.path.join(os.path.normpath(seq.dirname), seq.name)
        self.imageViewer.executeFile(firstImagePath)
        # os.startfile(firstImagePath)

    def stop(self):  # Connect to Stop-button clicked()
        """Stops the search progress for sequences"""
        if self._timerId is not None:
            self.killTimer(self._timerId)
        self._generator = None
        self._timerId = None

    def timerEvent(self, event):
        # This is called every time the GUI is idle.
        if self._generator is None:
            return
        try:
            next(self._generator)  # Run the next iteration
        except StopIteration:
            self.stop()  # Iteration has finshed, kill the timer

    # def _loadJson(self, file):
    #     """Loads the given json file"""
    #     if os.path.isfile(file):
    #         try:
    #             with open(file, 'r') as f:
    #                 data = json.load(f)
    #                 return data
    #         except ValueError:
    #             msg = "Corrupted JSON file => %s" % file
    #             # logger.error(msg)
    #             return -2  # code for corrupted json file
    #     else:
    #         return None

    # def _dumpJson(self, data, file):
    #     """Saves the data to the json file"""
    #     # with open(file, "w") as f:
    #     #     json.dump(data, f, indent=4)
    #     name, ext = os.path.splitext(file)
    #     tempFile = "{0}.tmp".format(name)
    #     with open(tempFile, "w") as f:
    #         json.dump(data, f, indent=4)
    #     copyfile(tempFile, file)
    #     os.remove(tempFile)

    def uniqueList(self, seq):  # Dave Kirby
        # Order preserving
        seen = set()
        return [x for x in seq if x not in seen and not seen.add(x)]


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


class DropLineEdit(QtWidgets.QLineEdit):
    """Custom LineEdit Class accepting drops"""
    # PyInstaller and Standalone version compatibility
    if FORCE_QT5:
        dropped = QtCore.pyqtSignal(str)
    else:
        dropped = Qt.QtCore.Signal(str)

    def __init__(self, type, parent=None):
        super(DropLineEdit, self).__init__(parent)
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
        # self.addItem(path)


class DeselectableTreeView(QtWidgets.QTreeView):
    """Custom Deselectable TreeView Class"""
    # PyInstaller and Standalone version compatibility
    if FORCE_QT5:
        deselected = QtCore.pyqtSignal(bool)
    else:
        deselected = QtCore.Signal(bool)

    def mousePressEvent(self, event):
        index = self.indexAt(event.pos())  # returns  -1 if click is outside
        if index.row() == -1:
            self.clearSelection()
            self.deselected.emit(True)
        QtWidgets.QTreeView.mousePressEvent(self, event)


class SeqCopyProgress(QtWidgets.QWidget, RootManager):
    """Custom Widget for visualizing progress of file transfer"""

    def __init__(self, src=None, dest=None):
        super(SeqCopyProgress, self).__init__()
        self.logger = None
        self.src = src
        self.dest = dest
        self.build_ui()
        self.terminated = False
        self.cancelAll = False
        self.errorFlag = False
        # self.copyfileobj(src=self.src, dst=self.dest)
        self.currentPlatform = self.getPlatform()

        dirname = os.path.dirname(os.path.abspath(__file__))
        stylesheetFile = os.path.join(dirname, "CSS", "tikManager.qss")

        with open(stylesheetFile, "r") as fh:
            self.setStyleSheet(fh.read())

    def build_ui(self):

        hbox = QtWidgets.QVBoxLayout()

        vbox = QtWidgets.QHBoxLayout()

        lbl_src = QtWidgets.QLabel('Source: ')
        lbl_dest = QtWidgets.QLabel('Destination: ')
        lbl_overall = QtWidgets.QLabel('Overall Progress:')
        self.pb = QtWidgets.QProgressBar()
        self.pbOverall = QtWidgets.QProgressBar()
        self.cancelButton = QtWidgets.QPushButton("Cancel")
        self.cancelAllButton = QtWidgets.QPushButton("Cancel All")

        self.pb.setMinimum(0)
        self.pb.setMaximum(100)
        self.pb.setValue(0)

        self.pbOverall.setMinimum(0)
        self.pbOverall.setMaximum(100)
        self.pbOverall.setValue(0)

        hbox.addWidget(lbl_src)
        hbox.addWidget(lbl_dest)
        hbox.addWidget(self.pb)
        hbox.addWidget(lbl_overall)
        hbox.addWidget(self.pbOverall)
        vbox.addWidget(self.cancelButton)
        vbox.addWidget(self.cancelAllButton)
        hbox.addLayout(vbox)
        self.setLayout(hbox)
        self.setWindowTitle('File copy')
        self.cancelButton.clicked.connect(self.terminate)
        self.cancelAllButton.clicked.connect(lambda: self.terminate(all=True))
        self.show()

    def results_ui(self, status, success=True, logPath=None, destPath=None):

        self.msgDialog = QtWidgets.QDialog(parent=self)
        self.msgDialog.setModal(True)
        self.msgDialog.setWindowTitle("Transfer Results")
        # self.msgDialog.resize(300, 120)
        layoutMain = QtWidgets.QVBoxLayout()
        self.msgDialog.setLayout(layoutMain)

        infoHeader = QtWidgets.QLabel(status)
        #
        infoHeader.setProperty("infoHeader", True)
        infoHeader.setProperty("success", success)
        infoHeader.setStyleSheet("")


        layoutMain.addWidget(infoHeader)
        layoutH = QtWidgets.QHBoxLayout()
        layoutMain.addLayout(layoutH)
        if logPath:
            showLogButton = QtWidgets.QPushButton("Show Log File")
            layoutH.addWidget(showLogButton)
            showLogButton.clicked.connect(lambda: self.executeFile(logPath))
        showInExplorer = QtWidgets.QPushButton("Show in Explorer")
        layoutH.addWidget(showInExplorer)
        okButton = QtWidgets.QPushButton("OK")
        layoutH.addWidget(okButton)

        showInExplorer.clicked.connect(lambda: self.onShowInExplorer(destPath))

        okButton.clicked.connect(self.msgDialog.close)

        self.msgDialog.show()

    def onShowInExplorer(self, path):
        """Open the folder in explorer"""
        # TODO // Make it compatible with Linux
        # os.startfile(str(os.path.normpath(path)))

        # self.showInExplorer(unicode(os.path.normpath(path)).decode("utf-8"))
        self.showInExplorer(compat.decode(os.path.normpath(path)))
        pass

    def closeEvent(self, *args, **kwargs):
        """Override close behaviour"""
        self.terminated = True

    def terminate(self, all=False):
        """Terminate the progress"""
        self.terminated = True
        self.cancelAll = all

    def safeLog(self, msg):
        try:
            self.logger.debug(msg)
        except AttributeError:
            pass

    def copyfileobj(self, src, dst):

        self.pb.setValue(0)
        self.terminated = False  # reset the termination status
        totalCount = len(src)
        current = 0

        for i in src:
            targetPath = os.path.join(dst, os.path.basename(i))
            try:
                copyfile(i, targetPath)
            except:
                self.errorFlag = True
                self.safeLog("FAILED - unknown error")
            percent = (100 * current) / totalCount
            self.pb.setValue(percent)
            current += 1
            QtWidgets.QApplication.processEvents()
            self.safeLog("Success - {0}".format(targetPath))
            if self.terminated or self.cancelAll:
                self.errorFlag = True
                self.safeLog("FAILED - skipped by user")
                break

    def copysequence(self, sequenceData, selectionList, destination, logPath, root):
        """
        Copies the sequences to the destination
        :param sequenceData: (Dictionary) Dictionary of sequences - Usually all found sequences
        :param selectionList: (List) Name list of selected sequences to iterate
        :param destination: (String) Absolute Path of remote destination
        :param logPath: (String) Absolute folder Path for log file
        :param root: (String) Root path of the images. Difference between sequence file folder
                        and root path will be used as the folder structure at remote location
        :return:
        """
        now = datetime.datetime.now()
        logName = "fileTransferLog_{0}.txt".format(now.strftime("%Y.%m.%d.%H.%M"))
        logFile = os.path.join(logPath, logName)
        self.logger = self.setupLogger(logFile)
        totalCount = len(selectionList)
        current = 0
        for sel in selectionList:
            if self.cancelAll:
                self.safeLog("ALL CANCELED")
                break
            self.logger.debug(
                "---------------------------------------------\n"
                "Copy Progress - {0}\n"
                "---------------------------------------------".format(
                    sequenceData[str(sel)]))
            percent = (100 * current) / totalCount
            self.pbOverall.setValue(percent)
            current += 1
            tFilesList = [i.path for i in sequenceData[str(sel)]]
            subPath = os.path.split(os.path.relpath(tFilesList[0], root))[0]  ## get the relative path
            currentDate = now.strftime("%y%m%d")
            targetPath = os.path.join(destination, currentDate, subPath)
            if not os.path.isdir(os.path.normpath(targetPath)):
                os.makedirs(os.path.normpath(targetPath))
            self.copyfileobj(src=tFilesList, dst=targetPath)

        self.deleteLogger(self.logger)

        self.close()
        if self.cancelAll:
            self.results_ui("Canceled by user", success=False, logPath=logFile, destPath=destination)
        elif self.errorFlag:
            self.results_ui("Check log file for errors", success=False, logPath=logFile, destPath=destination)
        else:
            self.results_ui("Transfer Successfull", success=True, logPath=logFile, destPath=destination)
        pass

    def setupLogger(self, handlerPath):
        """Prepares logger to write into log file"""
        logger = logging.getLogger('imageViewer')
        file_logger = logging.FileHandler(handlerPath)
        logger.addHandler(file_logger)
        logger.setLevel(logging.DEBUG)
        return logger

    def deleteLogger(self, logger):
        """Deletes the looger object once the logging into file finishes"""
        for i in logger.handlers:
            logger.removeHandler(i)
            i.flush()
            i.close()

if __name__ == '__main__':
    # os.environ["FORCE_QT5"] = "True"
    app = QtWidgets.QApplication(sys.argv)
    selfLoc = os.path.dirname(os.path.abspath(__file__))
    stylesheetFile = os.path.join(selfLoc, "CSS", "tikManager.qss")

    with open(stylesheetFile, "r") as fh:
        app.setStyleSheet(fh.read())
    window = MainUI()
    window.show()
    #
    # window = MainUI(projectPath= os.path.normpath("E:\\SceneManager_Projects\\SceneManager_DemoProject_None_181101"))
    # window.show()
    sys.exit(app.exec_())


