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
os.environ["FORCE_QT4"]="1"

from PyQt4 import QtCore, Qt
from PyQt4 import QtGui as QtWidgets

import SmUIRoot
reload(SmUIRoot)
from SmRoot import RootManager
from SmUIRoot import MainUI as baseUI

import _version
import subprocess

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
logger.setLevel(logging.WARNING)

class SwViewer(RootManager):
    """
    Helper class for StandaloneManager. Views and opens Scenes.
    swDict must contain:
    "niceName", "databaseDir", "scenesDir", "pbSettingsFile", "categoriesFile", "userSettingsDir"
    This dictionary(s) defined in the StandaloneManager class
    """

    def __init__(self, swDict, projectDir, commonFolder):
        super(SwViewer, self).__init__()
        self.swDict = swDict
        self.swNiceName = swDict["niceName"]
        self.projectDir = projectDir

        self.init_paths(commonFolder)
        self.init_database()

    def init_paths(self, commonFolder):
        """Initializes all the necessary paths"""
        logger.debug("Func: init_paths")
        # all paths in here must be absolute paths
        _softwarePathsDict = self.getSoftwarePaths()

        self._pathsDict["userSettingsDir"] = os.path.normpath(os.path.join(self.getUserDirectory(), _softwarePathsDict["userSettingsDir"]))
        self._folderCheck(self._pathsDict["userSettingsDir"])

        self._pathsDict["bookmarksFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], "smBookmarks.json"))
        self._pathsDict["currentsFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], "smCurrents.json"))
        self._pathsDict["projectsFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], "smProjects.json"))

        self._pathsDict["projectDir"] = self.getProjectDir()
        self._pathsDict["sceneFile"] = ""
        # _softwarePathsDict = self.getSoftwarePaths()
        if self._pathsDict["projectDir"] == -1 or self._pathsDict["sceneFile"] == -1 or _softwarePathsDict == -1:
            msg = "The following functions must be overridden in inherited class:\n'getSoftware'\n'getProjectDir'\n'getSceneFile'"
            logger.error(msg)
            raise Exception([102, msg])

        self._pathsDict["masterDir"] = os.path.normpath(os.path.join(self._pathsDict["projectDir"], "smDatabase"))
        self._folderCheck(self._pathsDict["masterDir"])


        self._pathsDict["databaseDir"] = os.path.normpath(os.path.join(self._pathsDict["masterDir"], _softwarePathsDict["databaseDir"]))
        self._folderCheck(self._pathsDict["databaseDir"])

        self._pathsDict["scenesDir"] = os.path.normpath(os.path.join(self._pathsDict["projectDir"], _softwarePathsDict["scenesDir"]))
        self._folderCheck(self._pathsDict["scenesDir"])

        self._pathsDict["projectSettingsFile"] = os.path.normpath(os.path.join(self._pathsDict["masterDir"], "projectSettings.json"))
        # self._pathsDict["subprojectsFile"] = os.path.normpath(os.path.join(self._pathsDict["databaseDir"], "subPdata.json"))
        self._pathsDict["subprojectsFile"] = os.path.normpath(os.path.join(self._pathsDict["masterDir"], "subPdata.json"))
        self._pathsDict["categoriesFile"] = os.path.normpath(os.path.join(self._pathsDict["databaseDir"], _softwarePathsDict["categoriesFile"]))

        self._pathsDict["previewsDir"] = os.path.normpath(os.path.join(self._pathsDict["projectDir"], "Playblasts", _softwarePathsDict["niceName"])) # dont change
        self._folderCheck(self._pathsDict["previewsDir"])

        self._pathsDict["pbSettingsFile"] = os.path.normpath(os.path.join(self._pathsDict["previewsDir"], _softwarePathsDict["pbSettingsFile"]))

        self._pathsDict["generalSettingsDir"] = commonFolder

        self._pathsDict["usersFile"] = os.path.normpath(os.path.join(self._pathsDict["generalSettingsDir"], "sceneManagerUsers.json"))

        self._pathsDict["softwareDatabase"] = os.path.normpath(os.path.join(self._pathsDict["generalSettingsDir"], "softwareDatabase.json"))
        self._pathsDict["sceneManagerDefaults"] = os.path.normpath(os.path.join(self._pathsDict["generalSettingsDir"], "sceneManagerDefaults.json"))

    def getSoftwarePaths(self):
        """Overriden function"""
        return self.swDict

    def getProjectDir(self):
        """Overriden function"""
        return self.projectDir

    def getSceneFile(self):
        """Overriden function"""
        return ""

    def _findExecutables(self, rootPath, relativePath, executableList, searchword=None):

        if searchword:
            try:
                versionRoots = [x for x in os.listdir(rootPath) if x.startswith(searchword) and os.path.isdir(os.path.join(rootPath, x))]
            except WindowsError:
                # msg = "Cannot resolve executable paths"
                # self._exception(360, msg)
                return
        else:
            try:
                versionRoots = [x for x in os.listdir(rootPath) if os.path.isdir(os.path.join(rootPath, x))]
            except WindowsError:
                # msg = "Cannot resolve executable paths"
                # self._exception(360, msg)
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
        programFiles64 = os.environ["PROGRAMFILES"]

        # empty dictionary to hold findings
        exeDict = {}

        if software:
            try:
                # lookupDict = {software: softwareDictionary[software]}
                lookupDict = {software: self.swDict}
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

        # if ID.startswith("SmMaya"):
        #     swID = "Maya"
        # elif ID.startswith("Sm3dsMax"):
        #     swID = "3dsMax"
        # elif ID.startswith("SmHoudini"):
        #     swID = "Houdini"
        # elif ID.startswith("SmNuke"):
        #     swID = "Nuke"
        # else:
        #     msg = "Cannot resolve software version from database"
        #     self._exception(360, msg)
        #     return

        swID = self.swDict["niceName"]

        executables = self.getAvailableExecutables(software=swID)
        # return

        # ------------
        # MAYA VERSION
        # ------------

        if swID == "Maya":
            versionDict = {201400: "Maya2014",
                           201414: "Maya2014",
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
                           20180000: "Maya2018",
                           20180100: "Maya2018",
                           20180200: "Maya2018",
                           20180300: "Maya2018",
                           20180400: "Maya2018",
                           20180500: "Maya2018"
                           }
            try:
                versionName = versionDict[self._currentSceneInfo["MayaVersion"]]
            except KeyError:
                msg = "Maya version cannot resolved"
                self._exception(360, msg)
                return

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
                           20000: "3ds Max 2018"
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

        self.swList = []
        self.init_paths()
        self.init_database()

        self.initSoftwares()

    def init_paths(self):
        """Overriden function"""


        self._pathsDict["userSettingsDir"] = os.path.normpath(os.path.join(os.path.expanduser("~"), "Documents", "SceneManager", "Standalone"))
        self._folderCheck(self._pathsDict["userSettingsDir"])

        self._pathsDict["bookmarksFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], "smBookmarks.json"))
        self._pathsDict["currentsFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], "smCurrents.json"))
        self._pathsDict["projectsFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], "smProjects.json"))

        self._pathsDict["commonFolderDir"] = os.path.abspath(os.path.join(self._pathsDict["userSettingsDir"], os.pardir))
        self._pathsDict["commonFolderFile"] = os.path.normpath(os.path.join(self._pathsDict["commonFolderDir"], "smCommonFolder.json"))

        self._pathsDict["projectDir"] = self.getProjectDir()
        self._pathsDict["sceneFile"] = ""

        self._pathsDict["masterDir"] = os.path.normpath(os.path.join(self._pathsDict["projectDir"], "smDatabase"))

        self._pathsDict["projectSettingsFile"] = os.path.normpath(os.path.join(self._pathsDict["masterDir"], "projectSettings.json"))

        self._pathsDict["generalSettingsDir"] = self._getCommonFolder()
        if self._pathsDict["generalSettingsDir"] == -1:
            self._exception(201, "Cannot Continue Without Common Database")
            return -1

        self._pathsDict["usersFile"] = os.path.normpath(os.path.join(self._pathsDict["generalSettingsDir"], "sceneManagerUsers.json"))

        self._pathsDict["softwareDatabase"] = os.path.normpath(os.path.join(self._pathsDict["generalSettingsDir"], "softwareDatabase.json"))
        self._pathsDict["sceneManagerDefaults"] = os.path.normpath(os.path.join(self._pathsDict["generalSettingsDir"], "sceneManagerDefaults.json"))

    def init_database(self):
        """OVERRIDEN FUNCTION"""

        self._usersDict = self._loadUsers()
        self._currentsDict = self._loadUserPrefs()
        # get hardcoded software list
        # hardCodedSwPath = os.path.normpath(os.path.join(self._pathsDict["generalSettingsDir"], "softwareDatabase.json"))

        # get hardcoded software list
        self.softwareDictionary = self._loadJson(self._pathsDict["softwareDatabase"])

    def getProjectDir(self):
        """OVERRIDEN FUNCTION"""
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
            if norm_p_path: #some error can save it as None
                return norm_p_path
            else:
                return os.path.normpath(os.path.expanduser("~"))
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
        # for swDict in self.swDictList:
        #     searchPath = (os.path.join(self.projectDir, "smDatabase", swDict["databaseDir"]))
        #     if os.path.isdir(searchPath):
        #         self.swList.append(SwViewer(swDict, self.projectDir))
        # for swDict in softwareDictionary.items():
        for swDict in self.softwareDictionary.items():
            searchPath = (os.path.join(self.projectDir, "smDatabase", swDict[1]["databaseDir"]))
            if os.path.isdir(searchPath):
                # create a new software viewer object with the accessed project path
                # and append it to the list of valid softwares for the current project
                self.swList.append(SwViewer(swDict[1], self.projectDir, self._pathsDict["generalSettingsDir"]))

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

    # def _checkCommonFolder(self, folder):
    #     checkList = [os.path.join(folder, "sceneManagerDefaults.json"),
    #                  os.path.join(folder, "sceneManagerUsers.json"),
    #                  os.path.join(folder, "softwareDatabase.json")]
    #     missingList = [os.path.basename(path) for path in checkList if not os.path.isfile(path)]
    #     if len(missingList) > 0:
    #
    #         errorBox = QtWidgets.QMessageBox()
    #         errorBox.setText("Common Database Folder missing some necessary files")
    #         errorBox.setDetailedText("Following files are missing:\n %s" %pprint.pformat(missingList))
    #         errorBox.exec_()
    #         return False
    #     else:
    #         return True
    #
    # def _getCommonFolder(self):
    #     """Standalone Specific function - Different from software modules,
    #     Standalone version needs to know where common files exist"""
    #     if os.path.isfile(self._pathsDict["commonFolderFile"]):
    #         commonFolder = self._loadJson(self._pathsDict["commonFolderFile"])
    #         if commonFolder == -2:
    #             return -2
    #
    #     else:
    #         # in case there is no file found (Initial Run)
    #         q = QtWidgets.QMessageBox()
    #         q.setIcon(QtWidgets.QMessageBox.Question)
    #         q.setText("Please define the Common Database Folder which contains general database files\n\nPress Ok to continue")
    #         # q.setInformativeText(textInfo)
    #         q.setWindowTitle("Select the Common Database Folder")
    #         q.setDetailedText(
    #             "Common Database Folder is the one which has the common modules for all software modules. Common Database Folder must include:\n"
    #             "sceneManagerDefaults.json\n"
    #             "sceneManagerUsers.json\n"
    #             "softwareDatabase.json")
    #         q.setStandardButtons(
    #             QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Abort)
    #
    #         # q.button(QtWidgets.QMessageBox.Ok).setFixedHeight(30)
    #         q.button(QtWidgets.QMessageBox.Ok).setFixedWidth(100)
    #         #
    #         # q.button(QtWidgets.QMessageBox.Abort).setFixedHeight(30)
    #         q.button(QtWidgets.QMessageBox.Abort).setFixedWidth(100)
    #         ret = q.exec_()
    #         if ret == QtWidgets.QMessageBox.Ok:
    #             commonFolder = self._defineCommonFolder()
    #
    #         elif ret == QtWidgets.QMessageBox.Abort:
    #             return -1
    #
    #     return commonFolder
    #
    # def _defineCommonFolder(self):
    #     dlg = QtWidgets.QFileDialog.getExistingDirectory()
    #     if dlg:
    #         selectedDir = os.path.normpath(str(dlg))
    #         if self._checkCommonFolder(selectedDir):
    #             commonFolder = selectedDir
    #             self._saveCommonFolder(commonFolder)
    #
    #             q = QtWidgets.QMessageBox()
    #             q.setIcon(QtWidgets.QMessageBox.Information)
    #             q.setText("Common Database Defined Successfully")
    #             # q.setInformativeText(textInfo)
    #             q.setWindowTitle("Success")
    #             q.exec_()
    #
    #             return commonFolder
    #         else:
    #             return self._getCommonFolder()
    #     else:
    #         return self._getCommonFolder()
    #         # self._getCommonFolder()
    #
    # def _saveCommonFolder(self, data):
    #     try:
    #         self._dumpJson(data, self._pathsDict["commonFolderFile"])
    #         msg = ""
    #         return 0, msg
    #     except:
    #         msg = "Cannot save common folder file"
    #         return -1, msg

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

class MainUI(baseUI):
    """Main UI Class. Inherits SmUIRoot.py"""
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
        """Adds extra menu and widgets to the base UI"""

        self.software_comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.software_comboBox.setMinimumSize(QtCore.QSize(150, 30))
        self.software_comboBox.setMaximumSize(QtCore.QSize(16777215, 30))
        self.software_comboBox.setObjectName(("software_comboBox"))
        self.r2_gridLayout.addWidget(self.software_comboBox, 0, 1, 1, 1)
        self.software_comboBox.activated.connect(self.onSoftwareChange)

    def modify(self):
        """Modifications to the base UI"""

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
        self.scenes_rcItem_0.setVisible(False)

        self.changeCommonFolder.setVisible(True)
        self.changeCommonFolder.triggered.connect(self.manager._defineCommonFolder)

    def rcAction_load(self):
        pass

    def initMainUI(self, newborn=False):
        """OVERRIDEN METHOD"""

        if not newborn:
            self.manager.init_paths()
            self.manager.init_database()
        # init softwares
        self.manager.initSoftwares()
        self._initSoftwares()


        if self.manager.swList == []:
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
        self.version_comboBox.setStyleSheet("background-color: rgb(80,80,80); color: white")
        self._vEnableDisable()

    def _zero(self):
        self.project_lineEdit.setText(self.manager.projectDir)
        self.category_tabWidget.blockSignals(True)
        self.category_tabWidget.clear()
        self.software_comboBox.clear()
        self.subProject_comboBox.clear()
        self.scenes_listWidget.clear()
        self.software_comboBox.setStyleSheet("background-color: %s; color: black" %self.swColorDict[str(self.software_comboBox.currentText())])

        self._vEnableDisable()
        self.category_tabWidget.blockSignals(False)

    def _getManager(self):
        """OVERRIDEN to select different software managers"""
        swList = self.manager.swList
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
        for x in self.manager.swList:
            self.software_comboBox.addItem(x.swNiceName)

        self.software_comboBox.setStyleSheet("background-color: %s; color: black" %self.swColorDict[str(self.software_comboBox.currentText())])

        self.software_comboBox.blockSignals(False)

    def onSoftwareChange(self):
        """Method to redirect manager when software selection changed by user"""
        self.manager.currentSwIndex = self.software_comboBox.currentIndex()
        #
        self._initCategories()
        self._initSubProjects()
        self.populateBaseScenes()
        self.software_comboBox.setStyleSheet("background-color: %s; color: black" %self.swColorDict[str(self.software_comboBox.currentText())])
        self.version_comboBox.setStyleSheet("background-color: rgb(80,80,80); color: white")
        self._vEnableDisable()
        manager = self._getManager()
        if manager.swNiceName == "Houdini":
            self.makeReference_pushButton.setVisible(False)
        else:
            self.makeReference_pushButton.setVisible(True)

    def onLoadScene(self):
        """OVERRIDEN METHOD"""
        if self.scenes_listWidget.currentRow() == -1:
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
    stylesheetFile = os.path.join(selfLoc, "CSS", "darkorange.stylesheet")
    if os.path.isfile(stylesheetFile):
        with open(stylesheetFile, "r") as fh:
            app.setStyleSheet(fh.read())
    window = MainUI()
    window.show()
    sys.exit(app.exec_())
