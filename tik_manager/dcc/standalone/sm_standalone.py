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

import sys, os

# Set the force pyqt environment variable to tell the other modulea not to use Qt.py module
os.environ["FORCE_QT5"]="1"

import __pyinstallerPathFix
from PyQt5 import QtWidgets, QtCore

# from tik_manager.SmRoot import RootManager
from SmRoot import RootManager
# from tik_manager.SmUIRoot import MainUI as baseUI
from SmUIRoot import MainUI as baseUI

# import tik_manager._version as _version
import _version
import subprocess

# import pprint
import logging
__author__ = "Arda Kutlu"
__copyright__ = "Copyright 2018, Scene Manager for Maya Project"
__credits__ = []
__license__ = "GPL"
__maintainer__ = "Arda Kutlu"
__email__ = "ardakutlu@gmail.com"
__status__ = "Development"

SM_Version = "Scene Manager Standalone v%s" %_version.__version__

logging.basicConfig()
logger = logging.getLogger('smStandalone')
logger.setLevel(logging.WARNING)

# class StandaloneCoreFunctions(object):
#     def __init__(self):
#         super(StandaloneCoreFunctions, self).__init__()


class SwViewer(RootManager):
    """
    Helper class for StandaloneManager. Views and opens Scenes.
    swDict must contain:
    "niceName", "databaseDir", "scenesDir", "pbSettingsFile", "categoriesFile", "userSettingsDir"
    This dictionary(s) defined in the StandaloneManager class
    """

    def __init__(self, dccDict, projectDir, commonFolder):
        super(SwViewer, self).__init__()
        self.dccDict = dccDict
        self.dcc = dccDict["niceName"]
        self.projectDir = projectDir

        self.init_paths(dccDict["niceName"])
        self.init_database()

    def getSoftwarePaths(self):
        """Overriden function"""
        return self.dccDict

    def getProjectDir(self):
        """Overriden function"""
        return self.projectDir

    def getSceneFile(self):
        """Overriden function"""
        return ""

    def _findExecutables(self, rootPath, relativePath, executableList, searchword=None):

        print("DB", rootPath, relativePath, executableList, searchword)
        if searchword:
            try:
                versionRoots = [x for x in os.listdir(rootPath) if x.startswith(searchword) and os.path.isdir(os.path.join(rootPath, x))]
            except WindowsError:
                return
        else:
            try:
                versionRoots = [x for x in os.listdir(rootPath) if os.path.isdir(os.path.join(rootPath, x))]
            except WindowsError:
                return
        for v in versionRoots:
            exeDir = os.path.join(rootPath, v, relativePath)
            for exe in executableList:
                exePath = os.path.join(exeDir, exe)
                if os.path.isfile(exePath):
                    yield [v, exePath]

    def getAvailableExecutables(self, software = None):
        # searched the default locations to get the available executables
        if self.currentPlatform is not "Windows":
            logger.warning("Currently only windows executables are supported")
            return None

        programFiles32 = os.environ["PROGRAMFILES(X86)"]
        programFiles64 = os.environ["PROGRAMW6432"]
        # programFiles64 = os.environ["PROGRAMFILES"]

        # empty dictionary to hold findings
        exeDict = {}

        if software:
            try:
                # lookupDict = {software: softwareDictionary[software]}
                lookupDict = {software: self.dccDict}
            except KeyError:
                self._exception(360, "Incorrect Software name")
                return

        for sw in lookupDict.items():
            exeGen32Bit = self._findExecutables(os.path.join(programFiles32, sw[1]["root"]),
                                                sw[1]["relPath"],
                                                sw[1]["exeList"], searchword=sw[1]["searchWord"])

            exeGen64Bit = self._findExecutables(os.path.join(programFiles64, sw[1]["root"]),
                                                sw[1]["relPath"],
                                                sw[1]["exeList"], searchword=sw[1]["searchWord"])
            # software dictionary inside exeDict
            exeDict[sw[1]["niceName"]]={}
            # turn generators into lists and put them into 32 and 64 bit keys
            list32Bit = [exe for exe in exeGen32Bit]
            list64Bit = [exe for exe in exeGen64Bit]
            if list32Bit == [] and list64Bit == []:
                msg = "Cannot find any executable"
                self._exception(360, msg)
                return
            exeDict[sw[1]["niceName"]]["32Bit"] = list32Bit
            exeDict[sw[1]["niceName"]]["64Bit"] = list64Bit

        return exeDict

    def executeScene(self):
        """
        Executes the scene at cursor position
        Tries to open the scene with the same version of the appropeiate Software
        which is defined at the Base Scene database
        """
        if self.currentPlatform is not "Windows":
            logger.warning("Currently only windows executables are supported")
            return None

        ID = self._currentSceneInfo["ID"]


        swID = self.dccDict["niceName"]

        executables = self.getAvailableExecutables(software=swID)
        if not executables:
            return None
        # return

        # ------------
        # MAYA VERSION
        # ------------

        if swID == "Maya":
            versionName = "Maya%s" % (str(self._currentSceneInfo["MayaVersion"])[:4])
            exePath = None
            for v in executables["Maya"]["64Bit"]:
                if v[0] == versionName:
                    exePath = v[1]
                    break
            if not exePath: # take a look for 32 bit versions
                for v in executables["Maya"]["32Bit"]:
                    if v[0] == versionName:
                        exePath = v[1]
                        break
            if not exePath: # if still no match
                msg = "%s is not installed on this workstation" %versionName
                self._exception(360, msg)
                return
            subprocess.Popen([exePath, "-file", self.currentScenePath], shell=True)
            return

        elif swID == "3dsMax":
            versionDict = {16000: "3ds Max 2014",
                           17000: "3ds Max 2015",
                           18000: "3ds Max 2016",
                           19000: "3ds Max 2017",
                           20000: "3ds Max 2018",
                           21000: "3ds Max 2019",
                           22000: "3ds Max 2020",
                           23000: "3ds Max 2021",
                           24000: "3ds Max 2022",
                           }
            try:
                versionName = versionDict[self._currentSceneInfo["3dsMaxVersion"][0]]
            except KeyError:
                msg = "3ds Max version cannot resolved"
                self._exception(360, msg)
                return

            exePath = None
            for v in executables["3dsMax"]["64Bit"]:
                if v[0] == versionName:
                    exePath = v[1]
                    break
            if not exePath: # take a look for 32 bit versions
                for v in executables["3dsMax"]["32Bit"]:
                    if v[0] == versionName:
                        exePath = v[1]
                        break
            if not exePath: # if still no match
                msg = "%s is not installed on this workstation" %versionName
                self._exception(360, msg)
                return

            subprocess.Popen([exePath, "-file", self.currentScenePath], shell=True)
            return

        elif swID == "Houdini":
            dbVersion = self._currentSceneInfo["HoudiniVersion"][0]
            dbIsApprentice = self._currentSceneInfo["HoudiniVersion"][1]
            for v in executables["Houdini"]["64Bit"]:
                versionNumber = v[0].split()[1]
                versionAsList = [int(s) for s in versionNumber.split(".") if s.isdigit()]
                exePath = v[1]
                if dbVersion == versionAsList:
                    if dbIsApprentice:
                        subprocess.Popen([exePath, "-apprentice", self.currentScenePath], shell=True)
                        return
                    else:
                        subprocess.Popen([exePath, self.currentScenePath], shell=True)
                        return
            for v in executables["Houdini"]["32Bit"]:
                versionNumber = v[0].split()[1]
                versionAsList = [int(s) for s in versionNumber.split(".") if s.isdigit()]
                exePath = v[1]
                if dbVersion == versionAsList:
                    if dbIsApprentice:
                        subprocess.Popen([exePath, "-apprentice", self.currentScenePath], shell=True)
                        return
                    else:
                        subprocess.Popen([exePath, self.currentScenePath], shell=True)
                        return
            msg = "Houdini %s is not installed on this workstation" % dbVersion
            self._exception(360, msg)
            return

        elif swID == "Nuke":
            dbMajorV = self._currentSceneInfo["NukeVersion"][0]
            dbMinorV = self._currentSceneInfo["NukeVersion"][1]
            sringVersion = "Nuke{0}.{1}".format(dbMajorV, dbMinorV)

            #first try the 64bit version
            for v in executables["Nuke"]["64Bit"]:
                versionFromFolderName = v[0] # eg Nuke10.0v1
                exePath = v[1]
                if versionFromFolderName.startswith(sringVersion):
                    subprocess.Popen([exePath, self.currentScenePath], shell=True)
                    return

            for v in executables["Nuke"]["32Bit"]:
                versionFromFolderName = v[0] # eg Nuke10.0v1
                exePath = v[1]
                if versionFromFolderName.startswith(sringVersion):
                    subprocess.Popen([exePath, self.currentScenePath], shell=True)
                    return

            msg = "Nuke %s is not installed on this workstation" % sringVersion
            self._exception(360, msg)
            return

        elif swID == "Photoshop":
            # use the last available version for photoshop
            if len(executables["Photoshop"]["64Bit"]) != 0:
                exePath = executables["Photoshop"]["64Bit"][-1][1] # this is the last one in the list
                subprocess.Popen([exePath, self.currentScenePath], shell=True)
                return

            if len(executables["Photoshop"]["32Bit"]) != 0:
                exePath = executables["Photoshop"]["32Bit"][-1][1] # this is the last one in the list
                subprocess.Popen([exePath, self.currentScenePath], shell=True)
                return

            msg = "Photoshop is not installed on this workstation"
            self._exception(360, msg)
            return

    def _exception(self, code, msg):
        """OVERRIDEN"""

        errorbox = QtWidgets.QMessageBox()
        errorbox.setModal(True)
        errorbox.setText(msg)
        errorbox.setWindowTitle(self.errorCodeDict[code])
        errorbox.exec_()

        if (200 >= code < 210):
            raise Exception(code, msg)


class StandaloneManager(RootManager):
    """Command Class. Inherits SmRoot.py"""
    def __init__(self):
        super(StandaloneManager, self).__init__()

        self.dcc = ""
        self.dccList = []
        self.init_paths("Standalone")
        self.init_database()

        self.initSoftwares()

    def init_paths(self, nicename):
        """Overriden function"""

        self._pathsDict["userSettingsDir"] = os.path.normpath(os.path.join(self.getUserDir(), "TikManager"))
        self._folderCheck(os.path.join(self._pathsDict["userSettingsDir"], nicename))
        self._pathsDict["userSettingsFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], "userSettings.json"))

        self._pathsDict["localBookmarksFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], nicename, "smBookmarks.json"))
        self._pathsDict["bookmarksFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], "smBookmarks.json"))
        self._pathsDict["recentProjectsFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], "smRecentProjects.json"))
        self._pathsDict["currentsFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], nicename, "smCurrents.json"))
        self._pathsDict["projectsFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], "smProjects.json"))

        # self._pathsDict["commonFolderDir"] = os.path.abspath(os.path.join(self._pathsDict["userSettingsDir"], os.pardir))
        self._pathsDict["commonFolderFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], "smCommonFolder.json"))

        self._pathsDict["projectDir"] = self.getProjectDir()
        self._pathsDict["sceneFile"] = ""

        self._pathsDict["masterDir"] = os.path.normpath(os.path.join(self._pathsDict["projectDir"], "smDatabase"))
        self._pathsDict["exportSettingsFile"] = os.path.normpath(os.path.join(self._pathsDict["masterDir"], "exportSettings.json"))
        self._pathsDict["importSettingsFile"] = os.path.normpath(os.path.join(self._pathsDict["masterDir"], "importSettings.json"))

        # self._pathsDict["categoriesFile"] = os.path.normpath(os.path.join(self._pathsDict["databaseDir"], _softwarePathsDict["categoriesFile"]))


        self._pathsDict["projectSettingsFile"] = os.path.normpath(os.path.join(self._pathsDict["masterDir"], "projectSettings.json"))
        self._pathsDict["subprojectsFile"] = os.path.normpath(os.path.join(self._pathsDict["masterDir"], "subPdata.json"))
        self._pathsDict["sharedSettingsDir"] = self._getCommonFolder()
        if self._pathsDict["sharedSettingsDir"] == -1:
            self._exception(201, "Cannot Continue Without Common Database")
            return -1

        self._pathsDict["previewsRoot"] = os.path.normpath(os.path.join(self._pathsDict["projectDir"], "Playblasts")) # dont change

        self._pathsDict["usersFile"] = os.path.normpath(os.path.join(self._pathsDict["sharedSettingsDir"], "sceneManagerUsers.json"))

        self._pathsDict["softwareDatabase"] = os.path.normpath(os.path.join(self._pathsDict["sharedSettingsDir"], "softwareDatabase.json"))
        self._pathsDict["sceneManagerDefaults"] = os.path.normpath(os.path.join(self._pathsDict["sharedSettingsDir"], "sceneManagerDefaults.json"))
        self._pathsDict["tikConventions"] = os.path.normpath(os.path.join(self._pathsDict["sharedSettingsDir"], "tikConventions.json"))
        self._pathsDict["adminPass"] = os.path.normpath(os.path.join(self._pathsDict["sharedSettingsDir"], "adminPass.psw"))
        # self._pathsDict["exportSettingsFile"] = os.path.normpath(os.path.join(self._pathsDict["sharedSettingsDir"], "exportSettings.json"))
        # self._pathsDict["importSettingsFile"] = os.path.normpath(os.path.join(self._pathsDict["sharedSettingsDir"], "importSettings.json"))
        self._pathsDict["iconsDir"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../CSS", "rc")


    def init_database(self):
        """OVERRIDEN FUNCTION"""
        self._sceneManagerDefaults = self.loadManagerDefaults()
        self._userSettings = self.loadUserSettings()

        # self._categories = self.loadCategories()


        self._usersDict = self.loadUsers()
        self._currentsDict = self.loadUserPrefs()

        if not os.path.isdir(self._pathsDict["masterDir"]):
            return
        self._subProjectsList = self.loadSubprojects()
        # get hardcoded software list
        # hardCodedSwPath = os.path.normpath(os.path.join(self._pathsDict["sharedSettingsDir"], "softwareDatabase.json"))

        # get hardcoded software list
        self.softwareDictionary = self._loadJson(self._pathsDict["softwareDatabase"])

    def getProjectDir(self):
        """OVERRIDEN FUNCTION"""
        # get the projects file for standalone manager
        projectsDict = self.loadProjects()

        if not projectsDict:
            currentProject = os.path.normpath(os.path.expanduser("~"))
            projectsDict = {"Standalone": currentProject}
            self.saveProjects(projectsDict)
            return currentProject

        # get the project defined in the database file
        try:
            dbProject = projectsDict["Standalone"]
            if dbProject: #some error can save it as None
                return dbProject
            else:
                return os.path.normpath(os.path.expanduser("~"))
        except KeyError:
            currentProject = os.path.normpath(os.path.expanduser("~"))
            # projectsDict = {"Standalone": currentProject}
            projectsDict["Standalone"] = currentProject
            self.saveProjects(projectsDict)
            return currentProject

    def setProject(self, path):
        """Sets the project"""
        # print("d", type(path), path)
        path = path.replace("file:", "\\")
        projectsDict = self.loadProjects()
        if not projectsDict:
            projectsDict = {"Standalone": path}
        else:
            projectsDict["Standalone"] = path
        self.saveProjects(projectsDict)
        self.projectDir = path
        self.init_paths("Standalone")
        self.init_database()
        self.initSoftwares()


    def initSoftwares(self):
        # We need to get which softwares are used in the current project
        self.dccList = []
        dbFolder = self._pathsDict["masterDir"]
        if not os.path.isdir(dbFolder):
            self.dccList = [] # empty software list
            return self.dccList#this is not a sceneManager project
        # for swDict in self.swDictList:
        #     searchPath = (os.path.join(self.projectDir, "smDatabase", swDict["databaseDir"]))
        #     if os.path.isdir(searchPath):
        #         self.swList.append(SwViewer(swDict, self.projectDir))
        # for swDict in softwareDictionary.items():

        for (key, value) in self.softwareDictionary.items():
            searchPath = (os.path.join(self.projectDir, "smDatabase", value["databaseDir"]))
            if os.path.isdir(searchPath):
                filesInFolders = [filenames for (dirpath, dirnames, filenames) in os.walk(searchPath)]
                if len(filesInFolders) > 1:
                    # create a new software viewer object with the accessed project path
                    # and append it to the list of valid softwares for the current project
                    self.dccList.append(SwViewer(value, self.projectDir, self._pathsDict["sharedSettingsDir"]))

        return self.dccList

    @property
    def currentSwIndex(self):
        """returns current sofware"""
        return self._currentsDict["currentSwIndex"]

    @currentSwIndex.setter
    def currentSwIndex(self, indexData):
        """Moves the cursor to the given software index"""
        if not 0 <= indexData < len(self.dccList):
            msg="Software index is out of range!"
            raise Exception([101, msg])
        if indexData == self.currentSwIndex:
            self.dccList[indexData].cursorInfo()
            return
        self._setCurrents("currentSwIndex", indexData)
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


        errorbox = QtWidgets.QMessageBox()
        errorbox.setModal(True)
        errorbox.setText(msg)
        errorbox.setWindowTitle(errorCodeDict[code])
        errorbox.exec_()

        if (200 >= code < 210):
            raise Exception(code, msg)

    def _question(self, header="", msg="", title="Manager Question"):
        """OVERRIDEN METHOD"""
        q = QtWidgets.QMessageBox()
        q.setIcon(QtWidgets.QMessageBox.Question)
        q.setText(header)
        q.setInformativeText(msg)
        q.setWindowTitle(title)
        q.setStandardButtons(
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)
        q.button(QtWidgets.QMessageBox.Yes).setFixedHeight(30)
        q.button(QtWidgets.QMessageBox.Yes).setFixedWidth(100)
        q.button(QtWidgets.QMessageBox.Cancel).setFixedHeight(30)
        q.button(QtWidgets.QMessageBox.Cancel).setFixedWidth(100)

        ret = q.exec_()
        if ret == QtWidgets.QMessageBox.Yes:
            return True
        else:
            return False

    def _info(self, msg):
        """OVERRIDEN METHOD"""
        infobox = QtWidgets.QMessageBox()
        infobox.setModal(True)
        infobox.setText(msg)
        infobox.setWindowTitle("Info")
        infobox.exec_()

    def _inputDir(self):
        """OVERRIDEN METHOD"""
        # Qt File dialog is preferred because it is faster
        inputDir = str(QtWidgets.QFileDialog.getExistingDirectory())
        return os.path.normpath(inputDir)

    def loadUserPrefs(self):
        """OVERRIDEN FUNCTION Load Last CategoryIndex, SubProject Index,
        User name and Access mode from file as dictionary"""

        if os.path.isfile(self._pathsDict["currentsFile"]):
            settingsData = self._loadJson(self._pathsDict["currentsFile"])
            if settingsData == -2:
                return -2
        else:
            settingsData = {"currentTabIndex": 0,
                            "currentSubIndex": 0,
                            "currentUser": list(self._usersDict)[0],
                            "currentSwIndex": -1, # added multi software switch
                            "currentMode": 1} # for compatibility issues
            self._dumpJson(settingsData, self._pathsDict["currentsFile"])
        return settingsData

class MainUI(baseUI):
    """Main UI Class. Inherits SmUIRoot.py"""
    def __init__(self):
        super(MainUI, self).__init__()

        self.manager = StandaloneManager()


        self.buildUI()
        self.extraMenus()
        self.modify()
        self.initMainUI(newborn=True)
        # self.settingsUI()

    def extraMenus(self):
        """Adds extra menu and widgets to the base UI"""

        swComboLayout = QtWidgets.QVBoxLayout(spacing=0)
        self.comboColorbar = QtWidgets.QLabel(maximumHeight=2)
        self.comboColorbar.setStyleSheet("background-color: black;")
        swComboLayout.addWidget(self.comboColorbar)

        self.software_comboBox = QtWidgets.QComboBox(self.centralwidget, minimumSize=QtCore.QSize(150, 28), maximumSize=QtCore.QSize(16777215, 28))
        self.software_comboBox.setToolTip("Switches between software databases")
        swComboLayout.addWidget(self.software_comboBox)

        # self.r2_gridLayout.addWidget(self.software_comboBox, 0, 1, 1, 1)
        self.r2_gridLayout.addLayout(swComboLayout, 0, 1, 1, 1)

        self.software_comboBox.activated.connect(self.onSoftwareChange)

    def modify(self):
        """Modifications to the base UI"""

        # make sure load mode is checked and hidden
        self.load_radioButton.setChecked(True)
        self.load_radioButton.setVisible(False)
        self.reference_radioButton.setChecked(False)
        self.reference_radioButton.setVisible(False)

        self.baseScene_label.setVisible(False)
        # self.baseScene_lineEdit.setVisible(False)

        self.createPB.setVisible(False)

        self.export_pushButton.setHidden(True)
        self.saveVersion_pushButton.setVisible(False)
        self.saveVersion_fm.setVisible(False)
        self.saveBaseScene_pushButton.setVisible(False)
        self.saveBaseScene_fm.setVisible(False)
        self.scenes_rcItem_0.setVisible(False)
        self.scenes_rcItem_6.setVisible(False)

        self.baseSceneFromReference.menuAction().setVisible(False)

        # self.changeCommonFolder.setVisible(True)
        # self.changeCommonFolder.triggered.connect(self.manager._defineCommonFolder)

    def rcAction_load(self):
        pass

    def initMainUI(self, newborn=False):
        """OVERRIDEN METHOD"""

        extraColumnList = ["Name"] + self.manager.getExtraColumns()
        # header = QtWidgets.QTreeWidgetItem(["Name", "Date", "Ref. Version", "Creator", "Version Count"])
        header = QtWidgets.QTreeWidgetItem(extraColumnList)
        self.scenes_listWidget.setHeaderItem(header)
        self.scenes_listWidget.setColumnWidth(0, 250)

        if not newborn:
            self.manager.init_paths("Standalone")
            self.manager.init_database()
        # init softwares
        self.manager.initSoftwares()
        self._initSoftwares()


        if self.manager.dccList == []:
            self._zero()
            return

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
        # self.version_comboBox.setStyleSheet("background-color: rgb(80,80,80); color: white")
        self._vEnableDisable()

    def _zero(self):
        self.project_lineEdit.setText(self.manager.projectDir)
        self.category_tabWidget.blockSignals(True)
        self.category_tabWidget.clear()
        self.software_comboBox.clear()
        self.subProject_comboBox.clear()
        self.scenes_listWidget.clear()
        # self.software_comboBox.setStyleSheet("background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:1 #404040, stop:0.11 #404040, stop:0.1 %s); " %self.manager.getColorCoding(str(self.software_comboBox.currentText())))
        self.comboColorbar.setStyleSheet("background-color: %s" %self.manager.getColorCoding(str(self.software_comboBox.currentText())))
        # self.colorBar.setStyleSheet("background-color: %s;" %self.manager.getColorCoding(niceName=""))

        self._vEnableDisable()
        self.category_tabWidget.blockSignals(False)

    def _getManager(self):
        """OVERRIDEN to select different software managers"""
        swList = self.manager.dccList
        swIndex = self.software_comboBox.currentIndex()
        try:
            manager = swList[swIndex]
        except IndexError:
            return
        return manager

    def _initSoftwares(self):
        """Gets the softwares available in the project and updated the UI"""
        self.software_comboBox.blockSignals(True)

        self.software_comboBox.clear()
        for x in self.manager.dccList:
            self.software_comboBox.addItem(x.dcc)
        # print self.manager.getColorCoding(niceName="standalone")
        if self.manager.dccList:
            self.addSubProject_pushButton.setEnabled(True)
        else:
            self.addSubProject_pushButton.setEnabled(False)
        # self.software_comboBox.setStyleSheet("background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:1 #404040, stop:0.11 #404040, stop:0.1 %s)" %self.manager.getColorCoding(str(self.software_comboBox.currentText())))
        self.comboColorbar.setStyleSheet("background-color: %s" %self.manager.getColorCoding(str(self.software_comboBox.currentText())))
        # self.colorBar.setStyleSheet("background-color: %s;" %self.manager.getColorCoding(niceName=""))

        self.software_comboBox.blockSignals(False)

    def onSoftwareChange(self):
        """Method to redirect manager when software selection changed by user"""
        self.manager.currentSwIndex = self.software_comboBox.currentIndex()
        #
        self._initCategories()
        self._initSubProjects()
        self.populateBaseScenes()
        # self.software_comboBox.setStyleSheet("background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:1 #404040, stop:0.11 #404040, stop:0.1 %s)" %self.manager.getColorCoding(str(self.software_comboBox.currentText())))
        self.comboColorbar.setStyleSheet("background-color: %s" %self.manager.getColorCoding(str(self.software_comboBox.currentText())))
        # self.colorBar.setStyleSheet("background-color: %s;" %self.manager.getColorCoding(niceName=""))

        # self.version_comboBox.setStyleSheet("background-color: rgb(80,80,80); color: white")
        self._vEnableDisable()
        manager = self._getManager()
        if manager.swName == "Houdini":
            self.makeReference_pushButton.setVisible(False)
        else:
            self.makeReference_pushButton.setVisible(True)

    def onLoadScene(self):
        """OVERRIDEN METHOD"""

        if self.scenes_listWidget.currentIndex().row() == -1:
            return
        manager = self._getManager()
        if not manager:
            return
        manager.executeScene()

    def _vEnableDisable(self):
        """OVERRIDEN METHOD"""
        manager = self._getManager()
        # if not manager:
        #     return

        if  manager and manager.currentBaseSceneName:
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
    app = QtWidgets.QApplication(sys.argv)
    stylesheetFile = os.path.join(selfLoc, "../../CSS", "tikManager.qss")
    if os.path.isfile(stylesheetFile):
        with open(stylesheetFile, "r") as fh:
            app.setStyleSheet(fh.read())
    window = MainUI()
    window.show()
    sys.exit(app.exec_())
