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
import shutil
import _version

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
    BoilerDict["WindowTitle"] = "Image Viewer Maya v%s" % _version.__version__
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
    BoilerDict["WindowTitle"] = "Scene Manager 3ds Max v%s" % _version.__version__
except ImportError:
    pass

try:
    import hou

    BoilerDict["Environment"] = "Houdini"
    BoilerDict["WindowTitle"] = "Scene Manager Houdini v%s" % _version.__version__
except ImportError:
    pass

try:
    import nuke

    BoilerDict["Environment"] = "Nuke"
    BoilerDict["WindowTitle"] = "Scene Manager Nuke v%s" % _version.__version__
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

class AssetLibrary(dict):
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
        self.clear()
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

    def getData(self, assetName):
        jsonFile = os.path.join(self.directory, assetName, "%s.json" %assetName)
        data = self._loadJson(jsonFile)
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


    def _loadJson(self, file):
        """Loads the given json file"""
        try:
            with open(file, 'r') as f:
                data = json.load(f)
                return data
        except ValueError:
            msg = "Corrupted JSON file => %s" % file
            # logger.error(msg)
            self._exception(200, msg)
            # return -2 # code for corrupted json file


    def _dumpJson(self, data, file):
        """Saves the data to the json file"""
        name, ext = os.path.splitext(file)
        tempFile = "{0}.tmp".format(name)
        with open(tempFile, "w") as f:
            json.dump(data, f, indent=4)
        shutil.copyfile(tempFile, file)
        os.remove(tempFile)

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


        if projectPath:
            self.projectPath = str(projectPath)
        else:
            self.projectPath = getProject()

        if relativePath:
            self.rootPath = os.path.join(self.projectPath, str(relativePath))
        else:
            self.rootPath = os.path.join(self.projectPath, "images")
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

        self.setObjectName(BoilerDict["Environment"])
        self.resize(670, 624)
        self.setWindowTitle(BoilerDict["Environment"])
        self.centralwidget = QtWidgets.QWidget(self)
        self.model = QtWidgets.QFileSystemModel()
        self.model.setRootPath(self.rootPath)
        self.model.setFilter(QtCore.QDir.AllDirs | QtCore.QDir.NoDotAndDotDot)
        self.tLocation = self.getRaidPath()
        self.buildUI()

        self.setCentralWidget(self.centralwidget)