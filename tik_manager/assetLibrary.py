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

# Module to access Library of global assets

import os
import sys
import shutil
import _version

import time

FORCE_QT4 = bool(os.getenv("FORCE_QT4"))

# Enabele FORCE_QT4 for compiling with pyinstaller
# FORCE_QT4 = True

if FORCE_QT4:
    from PyQt4 import QtCore, Qt
    from PyQt4 import QtGui as QtWidgets
else:
    import Qt
    from Qt import QtWidgets, QtCore, QtGui

import json
import os, fnmatch
import logging

__author__ = "Arda Kutlu"
__copyright__ = "Copyright 2018, Asset Library"
__credits__ = []
__license__ = "GPL"
__maintainer__ = "Arda Kutlu"
__email__ = "ardakutlu@gmail.com"
__status__ = "Development"

logging.basicConfig()
logger = logging.getLogger('AssetLibrary')
logger.setLevel(logging.WARNING)

BoilerDict = {"Environment": "Standalone",
              "MainWindow": None,
              "WindowTitle": "Asset Library Standalone v%s" % _version.__version__,
              "Stylesheet": "mayaDark.stylesheet"}

# ---------------
# GET ENVIRONMENT
# ---------------
try:
    from maya import OpenMayaUI as omui
    import maya.cmds as cmds

    BoilerDict["Environment"] = "Maya"
    BoilerDict["WindowTitle"] = "Asset Library Maya v%s" % _version.__version__
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

    BoilerDict["Environment"] = "3dsMax"
    BoilerDict["WindowTitle"] = "Asset Library 3ds Max v%s" % _version.__version__
except ImportError:
    pass

try:
    import hou

    BoilerDict["Environment"] = "Houdini"
    BoilerDict["WindowTitle"] = "Asset Library Houdini v%s" % _version.__version__
except ImportError:
    pass

try:
    import nuke

    BoilerDict["Environment"] = "Nuke"
    BoilerDict["WindowTitle"] = "Asset Library Nuke v%s" % _version.__version__
except ImportError:
    pass

def getMainWindow():
    """This function should be overriden"""
    if BoilerDict["Environment"] == "Maya":
        win = omui.MQtUtil_mainWindow()
        ptr = wrapInstance(long(win), QtWidgets.QMainWindow)
        return ptr

    elif BoilerDict["Environment"] == "3dsMax":
        return MaxPlus.GetQMaxWindow()

    elif BoilerDict["Environment"] == "Houdini":
        return hou.qt.mainWindow()

    elif BoilerDict["Environment"] == "Nuke":
        # TODO // Needs a main window getter for nuke
        return None

    else:
        return None

def _loadJson(file):
    """Loads the given json file"""
    try:
        with open(file, 'r') as f:
            data = json.load(f)
            return data
    except ValueError:
        # msg = "Corrupted JSON file => %s" % file
        # logger.error(msg)
        # self._exception(200, msg)
        return(-1) # code for corrupted json file

def _dumpJson(data, file):
    """Saves the data to the json file"""
    name, ext = os.path.splitext(file)
    tempFile = "{0}.tmp".format(name)
    with open(tempFile, "w") as f:
        json.dump(data, f, indent=4)
    shutil.copyfile(tempFile, file)
    os.remove(tempFile)

class AssetLibrary(object):
    """
    Asset Library Logical operations Class. This Class holds the main functions (save,import,scan)
    """

    def __init__(self, directory):
        self.directory = directory
        if not os.path.exists(directory):
            logger.error("Cannot reach the library directory: \n" + directory)

        self.errorCodeDict = {200: "Corrupted File",
                         201: "Missing File",
                         202: "Read/Write Error",
                         203: "Delete Error",
                         210: "OS Not Supported",
                         101: "Out of range",
                         102: "Missing Override",
                         340: "Naming Error",
                         341: "Mandatory fields are not filled",
                         360: "Action not permitted"}

        self.assetsList=[]

    # def getLibraries(self):
    #     pass
    #
    # def addLibrary(self):
    #     pass
    #
    # def removeLibrary(self):
    #     pass

    def saveAsset(self, assetName, screenshot=True, moveCenter=False, selectionOnly=True, exportUV=True, exportOBJ=True, **info):
        """
        Saves the selected object(s) as an asset into the predefined library
        Args:
            assetName: (Unicode) Asset will be saved as with this name
            screenshot: (Bool) If true, screenshots (Screenshot, Thumbnail, Wireframe, UV Snapshots) will be taken with playblast. Default True
            directory: (Unicode) Default Library location. Default is predefined outside of this class
            moveCenter: (Bool) If True, selected object(s) will be moved to World 0 point. Pivot will be the center of selection. Default False
            **info: (Any) Extra information which will be hold in the .json file

        Returns:
            None

        """

        pass


    def scanAssets(self):
        """
        Scans the directory for .json files, and gather info.
        Args:
            directory: (Unicode) Default Library location. Default is predefined outside of this class

        Returns:
            None

        """
        if not os.path.exists(self.directory):
            return
        # first collect all the json files from second level subfolders
        subDirs = next(os.walk(self.directory))[1]
        # for dir in subDirs:
        #     filePath = os.path.join(self.directory, dir, "%s.json" %dir)
        #     if os.path.isfile(filePath):
        #         self[dir]={"dataPath": filePath}
        self.assetsList = [d for d in subDirs if os.path.isfile(os.path.join(self.directory, d, "%s.json" %d))]

    def getThumbnail(self, assetName):
        thumbPath = os.path.join(self.directory, assetName, "%s_thumb.jpg" %assetName)
        return thumbPath

    def showInExplorer(self, assetName):
        path = os.path.join(self.directory, assetName)
        os.startfile(path)

    def getData(self, assetName):
        jsonFile = os.path.join(self.directory, assetName, "%s.json" %assetName)
        data = _loadJson(jsonFile)
        return data

    def importAsset(self, name, copyTextures, mode="maPath"):
        """
        Imports the selected asset into the current scene

        Args:
            name: (Unicode) Name of the asset which will be imported
            copyTextures: (Bool) If True, all texture files of the asset will be copied to the current project directory

        Returns:
            None

        """

        pass

    def savePreviews(self, name, assetDirectory, uvSnap=True, selectionOnly=True):
        """
        Saves the preview files under the Asset Directory
        Args:
            name: (Unicode) Name of the Asset
            assetDirectory: (Unicode) Directory of Asset

        Returns:
            (Tuple) Thumbnail path, Screenshot path, Wireframe path

        """

        pass

    def updatePreviews(self, name, assetDirectory):

        pass


    def _exception(self, code, msg):
        """Exception report function. Throws a log error and raises an exception"""
        logger.error("Exception %s" %self.errorCodeDict[code])
        logger.error(msg)
        raise Exception (code, msg)

class MainUI(QtWidgets.QMainWindow):
    """Main UI function"""
    def __init__(self, projectPath=None, relativePath=None, recursive=False):
        for entry in QtWidgets.QApplication.allWidgets():
            try:
                if entry.objectName() == BoilerDict["Environment"]:
                    entry.close()
            except AttributeError:
                pass
        parent = getMainWindow()
        super(MainUI, self).__init__(parent=parent)

        # Set Stylesheet
        dirname = os.path.dirname(os.path.abspath(__file__))
        stylesheetFile = os.path.join(dirname, "CSS", "darkorange.stylesheet")

        self.homedir = os.path.expanduser("~")
        self.DocumentsDir = "Documents" if BoilerDict["Environment"] == "Standalone" else ""
        self.settingsFile = os.path.join(self.homedir, self.DocumentsDir, "assetLibraryConfig.json")

        self.setObjectName(BoilerDict["Environment"])
        self.resize(670, 624)
        self.setWindowTitle(BoilerDict["Environment"])
        self.centralwidget = QtWidgets.QWidget(self)

        # MENU BAR / STATUS BAR
        # ---------------------
        menubar = QtWidgets.QMenuBar(self)
        menubar.setGeometry(QtCore.QRect(0, 0, 735, 21))
        self.setMenuBar(menubar)
        statusbar = QtWidgets.QStatusBar(self)
        self.setStatusBar(statusbar)

        fileMenu = menubar.addMenu("File")
        addNewLibrary_mi= QtWidgets.QAction("&Add New Library", self)
        createNewAsset_mi = QtWidgets.QAction("&Create New Asset", self)
        loadAsset_mi = QtWidgets.QAction("&Load Selected Asset", self)
        importAssetWithTextures_mi = QtWidgets.QAction("&Import Asset and Copy Textures", self)
        importAsset_mi = QtWidgets.QAction("&Import only", self)
        deleteAsset_mi = QtWidgets.QAction("&Delete Selected Asset", self)
        removeLibrary_mi = QtWidgets.QAction("&Remove Library", self)

        fileMenu.addAction(addNewLibrary_mi)
        fileMenu.addAction(createNewAsset_mi)

        fileMenu.addSeparator()
        fileMenu.addAction(loadAsset_mi)
        fileMenu.addAction(importAssetWithTextures_mi)
        fileMenu.addAction(importAsset_mi)

        fileMenu.addSeparator()
        fileMenu.addAction(deleteAsset_mi)
        fileMenu.addAction(removeLibrary_mi)





        self.tabDialog()
        self.setCentralWidget(self.centralwidget)

    def tabDialog(self):

        self.masterLayout = QtWidgets.QVBoxLayout(self.centralwidget)

        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setMaximumSize(QtCore.QSize(16777215, 167777))
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.North)
        self.tabWidget.setElideMode(QtCore.Qt.ElideNone)
        self.tabWidget.setUsesScrollButtons(False)

        self.masterLayout.addWidget(self.tabWidget)



        for lib in self.getLibraryPaths():
            name = lib[0]
            path = lib[1]
            if not os.path.exists(path):
                logger.warning("Cannot reach library path: \n%s \n Removing from the database..." % (path))
                self.removeLibrary(lib)
                continue
            preTab = libraryTab(path)
            self.tabWidget.addTab(preTab, name)
            preTab.setObjectName(name)
            preTab.setLayout(preTab.layout)

        self.tabWidget.currentChanged.connect(self.refreshTab)
        # self.tabWidget.currentChanged.connect(self.tabWidget.currentWidget().populate)
        self.refreshTab()

    def refreshTab(self):
        self.tabWidget.currentWidget().populate()

        #
        # libs = self.settings(mode="load")
        # junkPaths = []
        # for item in libs:
        #     name = item[0]
        #     path = item[1]
        #     if not os.path.exists(path):
        #         logger.warning("Cannot reach library path: \n%s \n Removing from the database..." % (path))
        #         junkPaths.append(item)
        #         continue
        #     preTab = libraryTab(path)
        #     self.addTab(preTab, name)
        #     preTab.setLayout(preTab.layout)
        #
        # ## Remove the junk paths from the config file
        # for x in junkPaths:
        #     self.settings(mode="remove", item=x)
        #
        # if len(libs) == 0:
        #     self.createNewTab()
        #
        # self.addNew = QtWidgets.QWidget()
        # self.addTab(self.addNew, "+")
        #
        # self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        #
        # self.customContextMenuRequested.connect(self.on_context_menu)
        #
        # self.tabsRightMenu = QtWidgets.QMenu()
        #
        # renameTabAction = QtWidgets.QAction('Rename', self)
        # self.tabsRightMenu.addAction(renameTabAction)
        # renameTabAction.triggered.connect(lambda val="rename": self.settings(mode=val))
        #
        # repathTabAction = QtWidgets.QAction('Re-path', self)
        # self.tabsRightMenu.addAction(repathTabAction)
        # repathTabAction.triggered.connect(lambda val="repath": self.settings(mode=val))
        #
        # removeTabAction = QtWidgets.QAction('Remove Selected Library', self)
        # self.tabsRightMenu.addAction(removeTabAction)
        # removeTabAction.triggered.connect(self.deleteCurrentTab)
        #
        # self.currentChanged.connect(self.createNewTab)  # changed!

    def getLibraryPaths(self):
        try:
            libraryPaths = _loadJson(self.settingsFile)
        except IOError: # it file does not exist
            libraryPaths = []
            _dumpJson(libraryPaths, self.settingsFile)
        return libraryPaths

    def addLibrary(self, path, name):
        libraryPaths = self.getLibraryPaths()
        newItem = [name, path]
        libraryPaths.append(newItem)
        _dumpJson(libraryPaths, self.settingsFile)
        pass

    def removeLibrary(self, item):
        print item
        libraryPaths = self.getLibraryPaths()
        libraryPaths.pop(libraryPaths.index(item))
        _dumpJson(libraryPaths, self.settingsFile)
        pass

    def on_context_menu(self, point):
        # show context menu
        self.tabsRightMenu.exec_(self.mapToGlobal(point))
        # print (QtWidgets.QApplication.widgetAt(self.mapToGlobal(point)))

    def createNewTab(self):
        currentIndex = self.currentIndex()
        totalTabs = self.count()
        if currentIndex >= (totalTabs - 1):  ## if it is not the last tab (+)
            self.setCurrentIndex(currentIndex - 1)
            ## ASK For the new direcory location:

            directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Asset Directory",
                                                                   QtCore.QDir.currentPath())
            if directory:
                tabName = str(os.path.basename(directory))

                self.tabID += 1
                # testTab = libraryTab(directory)
                # self.addTab(testTab, tabName)
                self.tabBar().moveTab(currentIndex, currentIndex + 1)
                self.setCurrentIndex(currentIndex)
                self.settings(mode="add", name=tabName, path=directory)

    # def eventFilter(self, QObject, event):
    #     if event.type() == QtCore.Event.MouseButtonPress:
    #         if event.button() == Qt.RightButton:
    #             print("Right button clicked")
    #     return False

    ## TODO: FOOL PROOF config.json file. Test possible situations
    ## TODO: FOOL PROOF missing library folder (a re-path sub menu item within the right click menu?)

    def deleteCurrentTab(self):

        currentIndex = self.currentIndex()
        totalTabs = self.count()

        if currentIndex < (totalTabs):  ## if it is not the last tab (+)
            widget = self.widget(currentIndex)
            if widget is not None:
                widget.deleteLater()
            self.setCurrentIndex(currentIndex - 1)
            self.removeTab(currentIndex)
            self.settings(mode="remove", itemIndex=currentIndex)


    def settings(self, mode, name=None, path=None, itemIndex=None, item=None):
        """
        Reads and write Library name and path information on/from config file (assetLibraryConfig.json)

        Add mode
        adds the name and path of the directory to the database. "name" and "path" arguments are required.
        Ex.
        settings(mode="add", name="NameOfTheLib", path="Absolute/path/of/the/library")

        Remove mode
        Removes the given item from the database. Either "itemIndex" or "item" arguments are required. If both given, "item" will be used.
        Ex.
        settings(mode="remove", itemIndex=2)
        or
        settings(mode="remove", item=["Name","Path"])

        Rename mode
        Opens a input dialog, renames the selected tab and updates database with the new name

        Repath mode
        Opens a folder selection dialog, updates database with the selected folder

        Load mode
        Returns the database list.

        Args:
            mode: (String) Valid values are "add", "remove", "load".
            name: (String) Tab Name of the Library to be added. Required by "add" mode
            path: (String) Absolute Path of the Library to be added. Required by "add" mode
            itemIndex: (Int) Index value of the item which will be removed from the database. Required by "remove" mode IF item flag is not set
            item: (Int) item which will be removed from the database. Required by "remove" mode IF itemIndex flag is not set.

        Returns:
            Load mode returns List

        """
        ## get the file location
        homedir = os.path.expanduser("~")
        settingsFile = os.path.join(homedir, "assetLibraryConfig.json")

        # settingsFile = os.path.join(os.path.dirname(os.path.abspath( __file__ )),"assetLibraryConfig.json")
        def dump(data, file):
            with open(file, "w") as f:
                json.dump(data, f, indent=4)

        if mode == "add" and name is not None and path is not None:
            currentData = self.settings(mode="load")
            currentData.append([name, path])
            dump(currentData, settingsFile)
            return
        if mode == "remove":
            print "itemIndex", itemIndex
            print "item", item
            currentData = self.settings(mode="load")
            if itemIndex is not None:
                currentData.pop(itemIndex)
            elif item is not None:
                currentData.remove(item)
            else:
                logger.warning("You need to specify itemIndex or item for remove action")
                return
            dump(currentData, settingsFile)
            return

        if mode == "rename":
            currentIndex = self.currentIndex()
            if currentIndex == self.count():
                return
            currentData = self.settings(mode="load")
            exportWindow, ok = QtWidgets.QInputDialog.getText(self, 'Text Input Dialog', 'New Name:')
            if ok:
                newInput = str(exportWindow)
                if not newInput.strip():
                    logger.warn("You must give a name!")
                    return
                self.setTabText(currentIndex, newInput)
                ## update the settings file
                currentData[currentIndex][0] = newInput
                dump(currentData, settingsFile)
                return

        if mode == "repath":
            currentIndex = self.currentIndex()
            if currentIndex == self.count():
                return
            currentData = self.settings(mode="load")

            newDir = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Asset Directory",
                                                                QtCore.QDir.currentPath())
            if newDir:
                currentData[currentIndex][1] = newDir
                dump(currentData, settingsFile)
                return

        if mode == "load":
            if os.path.isfile(settingsFile):
                with open(settingsFile, 'r') as f:
                    # The JSON module will read our file, and convert it to a python dictionary
                    data = json.load(f)
                    return data
            else:
                return []
        logger.warning("Settings file not changed")

class libraryTab(QtWidgets.QWidget):
    viewModeState = -1

    def __init__(self, directory):
        self.directory = directory

        # super is an interesting function
        # It gets the class that our class is inheriting from
        # This is called the superclass
        # The reason is that because we redefined __init__ in our class, we no longer call the code in the super's init
        # So we need to call our super's init to make sure we are initialized like it wants us to be
        # me=self
        # for entry in QtWidgets.QApplication.allWidgets():
        #     if entry.objectName() == "assetLib":
        #         # print entry
        #         entry.close()

        # parent = getMayaMainWindow()

        super(libraryTab, self).__init__()

        # self.exportUV_def = True
        # self.exportOBJ_def = True
        # self.selectionOnly_def = True

        self.library = AssetLibrary(directory)
        self.buildTabUI()

    def buildTabUI(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        self.splitter = QtWidgets.QSplitter(self)
        self.splitter.setGeometry(QtCore.QRect(20, 10, 693, 437))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.layout.addWidget(self.splitter)

        self.createNewAsset_pushButton = QtWidgets.QPushButton(self)
        self.createNewAsset_pushButton.setMinimumSize(QtCore.QSize(150, 45))
        self.createNewAsset_pushButton.setMaximumSize(QtCore.QSize(15000, 45))
        self.createNewAsset_pushButton.setText("Create New Asset")
        self.layout.addWidget(self.createNewAsset_pushButton)


        self.frame = QtWidgets.QFrame(self.splitter)
        self.frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame.setLineWidth(0)

        self.gridLayout = QtWidgets.QGridLayout(self.frame)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(0)

        self.rightBelow_verticalLayout = QtWidgets.QVBoxLayout()
        self.rightBelow_verticalLayout.setSpacing(0)

        self.assets_listWidget = QtWidgets.QListWidget(self.frame)

        self.rightBelow_verticalLayout.addWidget(self.assets_listWidget)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 6, -1, -1)
        self.horizontalLayout.setSpacing(6)

        self.filter_label = QtWidgets.QLabel(self.frame)

        self.horizontalLayout.addWidget(self.filter_label)

        self.filter_lineEdit = QtWidgets.QLineEdit(self.frame)
        self.horizontalLayout.addWidget(self.filter_lineEdit)

        self.rightBelow_verticalLayout.addLayout(self.horizontalLayout)

        self.gridLayout.addLayout(self.rightBelow_verticalLayout, 2, 0, 1, 1)

        self.frame_right = QtWidgets.QFrame(self.splitter)
        self.frame_right.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_right.setFrameShadow(QtWidgets.QFrame.Raised)

        self.gridLayout_2 = QtWidgets.QGridLayout(self.frame_right)
        self.gridLayout_2.setContentsMargins(-1, -1, 0, 0)

        self.rightBelow_verticalLayout = QtWidgets.QVBoxLayout()

        self.assetNotes_label = QtWidgets.QLabel(self.frame_right)
        self.assetNotes_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.assetNotes_label.setText(("Asset Notes"))
        self.assetNotes_label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.rightBelow_verticalLayout.addWidget(self.assetNotes_label)

        self.notes_textEdit = QtWidgets.QTextEdit(self.frame_right)

        self.rightBelow_verticalLayout.addWidget(self.notes_textEdit)

        self.thumb_label = QtWidgets.QLabel(self.frame_right)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.thumb_label.sizePolicy().hasHeightForWidth())

        self.thumb_label.setSizePolicy(sizePolicy)
        self.thumb_label.setMinimumSize(QtCore.QSize(221, 124))
        self.thumb_label.setMaximumSize(QtCore.QSize(884, 496))
        self.thumb_label.setSizeIncrement(QtCore.QSize(1, 1))
        self.thumb_label.setBaseSize(QtCore.QSize(0, 0))
        self.thumb_label.setFrameShape(QtWidgets.QFrame.Box)
        self.thumb_label.setScaledContents(False)
        self.thumb_label.setAlignment(QtCore.Qt.AlignCenter)

        self.rightBelow_verticalLayout.addWidget(self.thumb_label)

        self.gridLayout_2.addLayout(self.rightBelow_verticalLayout, 3, 0, 1, 1)

        self.rightUp_gridLayout = QtWidgets.QGridLayout()
        self.rightUp_gridLayout.setContentsMargins(-1, -1, 10, 10)

        self.importOnly_pushButton = QtWidgets.QPushButton(self.frame_right)
        self.importOnly_pushButton.setMinimumSize(QtCore.QSize(100, 30))
        self.importOnly_pushButton.setMaximumSize(QtCore.QSize(150, 30))
        self.importOnly_pushButton.setText(("Import Only"))

        self.rightUp_gridLayout.addWidget(self.importOnly_pushButton, 1, 0, 1, 1)

        self.load_pushButton = QtWidgets.QPushButton(self.frame_right)
        self.load_pushButton.setMinimumSize(QtCore.QSize(100, 30))
        self.load_pushButton.setMaximumSize(QtCore.QSize(150, 30))
        self.load_pushButton.setText(("Load"))

        self.rightUp_gridLayout.addWidget(self.load_pushButton, 0, 3, 1, 1)

        self.importObj_pushButton = QtWidgets.QPushButton(self.frame_right)
        self.importObj_pushButton.setMinimumSize(QtCore.QSize(100, 30))
        self.importObj_pushButton.setMaximumSize(QtCore.QSize(150, 30))
        self.importObj_pushButton.setText(("Import .obj"))

        self.rightUp_gridLayout.addWidget(self.importObj_pushButton, 1, 3, 1, 1)

        self.importAndCopy_pushButton = QtWidgets.QPushButton(self.frame_right)
        self.importAndCopy_pushButton.setMinimumSize(QtCore.QSize(100, 30))
        self.importAndCopy_pushButton.setMaximumSize(QtCore.QSize(150, 30))
        self.importAndCopy_pushButton.setText(("Import/Copy Textures"))
        self.rightUp_gridLayout.addWidget(self.importAndCopy_pushButton, 0, 0, 1, 1)

        self.gridLayout_2.addLayout(self.rightUp_gridLayout, 0, 0, 1, 1)

        self.filter_lineEdit.textChanged.connect(self.populate)

        # RIGHT CLICK MENU
        # ----------------

        self.assets_listWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.assets_listWidget.customContextMenuRequested.connect(self.onContextMenu_assets)
        self.popMenu_assets = QtWidgets.QMenu()

        self.assets_rcItem_0 = QtWidgets.QAction('View as Icons', self)
        self.popMenu_assets.addAction(self.assets_rcItem_0)
        self.assets_rcItem_0.triggered.connect(lambda: self.rcAction_assets("viewModeChange"))

        self.assets_rcItem_1 = QtWidgets.QAction('Show in Explorer', self)
        self.popMenu_assets.addAction(self.assets_rcItem_1)
        self.assets_rcItem_1.triggered.connect(lambda: self.rcAction_assets("showInExplorer"))





        # self.populate()

    def populate(self):
        """
        UI populate function - linkes to the assetLibrary.scan()
        Returns:

        """
        filterWord = self.filter_lineEdit.text()

        self.assets_listWidget.clear()
        self.library.scanAssets()


        if self.viewModeState == 1:
            self.assets_listWidget.setViewMode(QtWidgets.QListWidget.IconMode)
            self.assets_listWidget.setIconSize(QtCore.QSize(100, 100))
            self.assets_listWidget.setMovement(QtWidgets.QListView.Static)
            self.assets_listWidget.setResizeMode(QtWidgets.QListWidget.Adjust)
            self.assets_listWidget.setGridSize(QtCore.QSize(100*1.2, 100*1.4))

            # self.assets_listWidget.addItems(self.filterList(self.library.assetsList, filterWord))
            filteredItems = self.filterList(self.library.assetsList, filterWord)
            for itemName in filteredItems:
                item = QtWidgets.QListWidgetItem(itemName)
                thumbPath = self.library.getThumbnail(itemName)

                icon = QtGui.QIcon(thumbPath)
                item.setIcon(icon)

                self.assets_listWidget.addItem(item)

        else:
            self.assets_listWidget.setViewMode(QtWidgets.QListWidget.ListMode)
            self.assets_listWidget.setGridSize(QtCore.QSize(15,15))
            self.assets_listWidget.addItems(self.filterList(self.library.assetsList, filterWord))


        # for name, info in sorted(self.library.items()):
        #
        #     # if there is a filterword, filter the item
        #     if filterWord != "" and filterWord.lower() not in name.lower():
        #         continue
        #     # We create an item for the list widget and tell it to have our controller name as a label
        #     item = QtWidgets.QListWidgetItem(name)
        #
        #     # We set its tooltip to be the info from the json
        #     # The pprint.pformat will format our dictionary nicely
        #     item.setToolTip(pprint.pformat(info))
        #
        #     # Finally we check if there's a screenshot available
        #     thumb = info.get('thumbPath')
        #     asset = info.get('assetName')
        #     thumbPath = os.path.join(self.directory, asset, thumb)
        #     # If there is, then we will load it
        #     if thumb:
        #         # So first we make an icon with the path to our screenshot
        #         icon = QtGui.QIcon(thumbPath)
        #         # then we set the icon onto our item
        #         item.setIcon(icon)
        #
        #     # Finally we add our item to the list
        #     self.listWidget.addItem(item)

    def filterList(self, sourceList, filterWord):
        if filterWord == "":
            return sourceList
        else:
            filteredList = [item for item in sourceList if (filterWord.lower() in item.lower())]
            return filteredList

    def onContextMenu_assets(self, point):
        # This method IS Software Specific
        row = self.assets_listWidget.currentRow()
        if row == -1:
            return
        #
        #     self.scenes_rcItem_1.setEnabled(False)
        #     self.scenes_rcItem_2.setEnabled(False)
        #     self.scenes_rcItem_3.setEnabled(False)
        #     self.scenes_rcItem_4.setEnabled(False)
        #     self.scenes_rcItem_5.setEnabled(False)
        #     self.scenes_rcItem_6.setEnabled(True)
        # else:
        #     self.scenes_rcItem_1.setEnabled(os.path.isdir(manager.currentBaseScenePath))
        #     self.scenes_rcItem_2.setEnabled(os.path.isdir(manager.currentPreviewPath))
        #     self.scenes_rcItem_3.setEnabled(True)
        #     self.scenes_rcItem_4.setEnabled(True)
        #     # show context menu
        #     self.scenes_rcItem_5.setEnabled(os.path.isdir(os.path.join(manager.projectDir, "images", manager.currentBaseSceneName)))
        #     self.scenes_rcItem_6.setEnabled(True)

        self.popMenu_assets.exec_(self.assets_listWidget.mapToGlobal(point))


    def rcAction_assets(self, item):
        currentItem = self.assets_listWidget.currentItem()
        name = currentItem.text()
        info = self.library.getData(name)

        if item == 'showInExplorer':
            self.library.showInExplorer(name)

        elif item == 'viewModeChange':
            self.viewModeState = self.viewModeState * -1
            if self.viewModeState == 1:
                self.assets_rcItem_0.setText("View As List")
                self.populate()
                # self.assets_listWidget.setViewMode(QtWidgets.QListWidget.IconMode)
            elif self.viewModeState == -1:
                self.assets_rcItem_0.setText("View As Icons")
                self.populate()
                # self.assets_listWidget.setViewMode(QtWidgets.QListWidget.ListMode)




if __name__ == '__main__':
    os.environ["FORCE_QT4"] = "True"
    app = QtWidgets.QApplication(sys.argv)
    selfLoc = os.path.dirname(os.path.abspath(__file__))
    stylesheetFile = os.path.join(selfLoc, "CSS", "darkorange.stylesheet")

    with open(stylesheetFile, "r") as fh:
        app.setStyleSheet(fh.read())
    window = MainUI()
    window.show()
    #
    # window = MainUI(projectPath= os.path.normpath("E:\\SceneManager_Projects\\SceneManager_DemoProject_None_181101"))
    # window.show()
    sys.exit(app.exec_())