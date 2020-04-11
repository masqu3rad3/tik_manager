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

import platform
import subprocess
import datetime
import os
import logging
# import pprint
import hashlib

import shutil
from glob import glob
import json
import filecmp
import re
# import ctypes
import socket

# import urllib
try:
    from urllib.request import urlopen
except:
    from urllib import urlopen ## python 2.7 compatibility
# import tik_manager.pyseq as pyseq
import pyseq
# import tik_manager._version as _version
import _version
# import tik_manager.compatibility as compat
import compatibility as compat

__author__ = "Arda Kutlu"
__copyright__ = "Copyright 2018, Tik Manager Root Functions"
__credits__ = []
__license__ = "GPL"
__maintainer__ = "Arda Kutlu"
__email__ = "ardakutlu@gmail.com"
__status__ = "Development"

logging.basicConfig()
logger = logging.getLogger('smRoot')
logger.setLevel(logging.WARNING)


class RootManager(object):
    """Base of all Scene Manager Command Classes"""
    def __init__(self):
        self.currentPlatform = self.getPlatform()
        self._pathsDict={}
        self.fpsList=["2", "3", "4", "5", "6", "8", "10", "12", "15", "16", "20",
                      "23.976", "24", "25", "29.97", "30", "40", "47.952", "48",
                      "50", "59.94", "60", "75", "80", "100", "120", "125", "150",
                      "200", "240", "250", "300", "375", "400", "500", "600", "750",
                      "1200", "1500", "2000", "3000", "6000", "44100", "48000"]
        self.resolutionPresets={
            "HD_720": [1280, 720],
            "HD_1080": [1920, 1080],
            "UHD_4K": [3840, 2160],
            "UHD_8K": [7680, 4320],
            "Academy_2K": [1828, 1332],
            "Full_Aperture_2K": [2048, 1556],
            "Academy_4K": [3656 , 2664],
            "Full_Aperture_4K": [4096, 3112],
            "IMAX": [5616, 4096],
        }

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
    def init_paths(self, nicename):
        """Initializes all the necessary paths"""
        logger.debug("Func: init_paths")
        # all paths in here must be absolute paths
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
        _softwarePathsDict = self.getSoftwarePaths()

        self._pathsDict["projectDir"] = self.getProjectDir()
        self._pathsDict["sceneFile"] = ""

        self._pathsDict["masterDir"] = os.path.normpath(os.path.join(self._pathsDict["projectDir"], "smDatabase"))
        self._pathsDict["databaseDir"] = os.path.normpath(os.path.join(self._pathsDict["masterDir"], _softwarePathsDict["databaseDir"]))
        self._pathsDict["scenesDir"] = os.path.normpath(os.path.join(self._pathsDict["projectDir"], _softwarePathsDict["scenesDir"]))
        self._pathsDict["transferDir"] = os.path.normpath(os.path.join(self._pathsDict["projectDir"], "_TRANSFER"))
        self._pathsDict["projectSettingsFile"] = os.path.normpath(os.path.join(self._pathsDict["masterDir"], "projectSettings.json"))
        self._pathsDict["subprojectsFile"] = os.path.normpath(os.path.join(self._pathsDict["masterDir"], "subPdata.json"))
        self._pathsDict["exportSettingsFile"] = os.path.normpath(os.path.join(self._pathsDict["masterDir"], "exportSettings.json"))
        self._pathsDict["importSettingsFile"] = os.path.normpath(os.path.join(self._pathsDict["masterDir"], "importSettings.json"))
        self._pathsDict["categoriesFile"] = os.path.normpath(os.path.join(self._pathsDict["databaseDir"], _softwarePathsDict["categoriesFile"]))
        self._pathsDict["previewsRoot"] = os.path.normpath(os.path.join(self._pathsDict["projectDir"], "Playblasts")) # dont change
        self._pathsDict["previewsDir"] = os.path.normpath(os.path.join(self._pathsDict["previewsRoot"], _softwarePathsDict["niceName"])) # dont change
        self._pathsDict["pbSettingsFile"] = os.path.normpath(os.path.join(self._pathsDict["previewsRoot"], _softwarePathsDict["pbSettingsFile"]))
        self._pathsDict["usersFile"] = os.path.normpath(os.path.join(self._pathsDict["sharedSettingsDir"], "sceneManagerUsers.json"))
        self._pathsDict["softwareDatabase"] = os.path.normpath(os.path.join(self._pathsDict["sharedSettingsDir"], "softwareDatabase.json"))
        self._pathsDict["sceneManagerDefaults"] = os.path.normpath(os.path.join(self._pathsDict["sharedSettingsDir"], "sceneManagerDefaults.json"))
        self._pathsDict["tikConventions"] = os.path.normpath(os.path.join(self._pathsDict["sharedSettingsDir"], "tikConventions.json"))
        self._pathsDict["adminPass"] = os.path.normpath(os.path.join(self._pathsDict["sharedSettingsDir"], "adminPass.psw"))
        self._pathsDict["iconsDir"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CSS", "rc")
        ## FFMPEG conversion paths
        self._pathsDict["conversionLUTFile"] = os.path.normpath(os.path.join(self._pathsDict["sharedSettingsDir"], "conversionLUT.json"))

    def _checkCommonFolder(self, folder):
        checkList = [os.path.join(folder, "sceneManagerDefaults.json"),
                     os.path.join(folder, "sceneManagerUsers.json"),
                     os.path.join(folder, "softwareDatabase.json"),
                     os.path.join(folder, "adminPass.psw")
                     ]
        missingList = [os.path.basename(path) for path in checkList if not os.path.isfile(path)]
        if len(missingList) > 0:
            self._info("This folder cannot be set as Common Database Folder.\n\n It is missing necessary files:\n\nFollowing files are missing:\n %s" %(missingList))
            return False
        else:
            return True

    def _getCommonFolder(self):
        """prompts input for the common folder"""
        if os.path.isfile(self._pathsDict["commonFolderFile"]):
            commonFolder = self._loadJson(self._pathsDict["commonFolderFile"])
            if commonFolder == -2:
                return -2
        else:
            msg = "Common Folder is not defined.\n\nDo you want to define now?"
            if self._question(msg):
                commonFolder = self._defineCommonFolder()
            else:
                return -1
        return commonFolder

    def _defineCommonFolder(self, path=None):

        if path:
            selectedDir = path
        else:
            selectedDir = self._inputDir()

        if os.path.isdir(selectedDir):
            if self._checkCommonFolder(selectedDir):
                commonFolder = selectedDir
                self._saveCommonFolder(commonFolder)
                self._info("Common Database Defined Successfully")
                return commonFolder
            else:
                return self._getCommonFolder()
        else:
            return self._getCommonFolder()

    def _saveCommonFolder(self, data):
        try:
            self._dumpJson(data, self._pathsDict["commonFolderFile"])
            msg = ""
            return 0, msg
        except:
            msg = "Cannot save common folder file"
            return -1, msg

    def getProjectDir(self):
        ## Load dictionary from database

        projectsDict = self.loadProjects()
        try: currentProject = self._getProject()
        except AttributeError: currentProject = os.path.normpath(os.path.expanduser("~"))

        ## If there is no database, create one with current project and return
        if not projectsDict:
            projectsDict = {self.swName: currentProject}
            self.saveProjects(projectsDict)
            return currentProject
        # get the project defined in the database file
        try:
            dbProject = projectsDict[self.swName]
        except KeyError:
            # if the software is not in the database create the key, dump db and return
            projectsDict[self.swName] = currentProject
            self.saveProjects(projectsDict)
            return currentProject

        # if the current project matches with the database, return it
        if dbProject == currentProject:
            return currentProject

        # make an exception for maya. Maya returns the currently set project always
        if self.swName == "Maya":
            projectsDict[self.swName] = currentProject
            self.saveProjects(projectsDict)
            return currentProject
        else:
            projectsDict[self.swName] = dbProject
            self.saveProjects(projectsDict)
            return dbProject

    def setProject(self, path):
        """Sets the project"""
        logger.debug("Func: setProject")
        path = path.replace("file:", "\\")
        projectsDict = self.loadProjects()
        if not projectsDict:
            projectsDict = {self.swName: path}
        else:
            projectsDict[self.swName] = path
        self.saveProjects(projectsDict)
        self.projectDir = path

    def getSoftwarePaths(self):
        """Returns the database dictionary of CURRENT SOFTWARE"""
        logger.debug("Func: getSoftwarePaths")
        softwareDatabaseFile = os.path.normpath(os.path.join(self.getSharedSettingsDir(), "softwareDatabase.json"))
        softwareDB = self._loadJson(softwareDatabaseFile)
        return softwareDB[self.swName]

    def getSceneFile(self):
        """This method must be overridden to return the full scene path ('' for unsaved) of current scene"""
        logger.debug("Func: getSceneFile")
        return -1

    def init_database(self):
        """Initializes all databases"""
        logger.debug("Func: init_database")

        self._folderCheck(self._pathsDict["masterDir"])
        self._folderCheck(self._pathsDict["databaseDir"])
        self._folderCheck(self._pathsDict["scenesDir"])
        self._folderCheck(self._pathsDict["previewsDir"])

        # defaults dictionary holding "defaultCategories", "defaultPreviewSettings", "defaultUsers"
        self._sceneManagerDefaults = self.loadManagerDefaults()
        self._userSettings = self.loadUserSettings()
        self._nameConventions = self.loadNameConventions()

        # self.currentPlatform = platform.system()
        self._categories = self.loadCategories()
        self._usersDict = self.loadUsers()
        self._currentsDict = self.loadUserPrefs()
        self._subProjectsList = self.loadSubprojects()

        # unsaved DB
        self._baseScenesInCategory = []
        self._currentBaseSceneName = ""
        self._currentSceneInfo = {}

        #Scene Specific
        self._currentVersionIndex = -1
        self._currentPreviewsDict = {}
        self._currentPreviewCamera = ""
        self._currentNotes = ""
        self._currentThumbFile = ""

        self._openSceneInfo = ""

        self.scanBaseScenes()


    def _setCurrents(self, att, newdata):
        """Sets the database stored cursor positions and saves them to the database file"""
        logger.debug("Func: _setCurrents")

        self._currentsDict[att] = newdata
        self.saveUserPrefs(self._currentsDict)

    @property
    def projectDir(self):
        """Returns Current Project Directory"""
        logger.debug("Func: projectDir/getter")
        return self._pathsDict["projectDir"]

    @projectDir.setter
    def projectDir(self, path):
        """Sets the Scene Manager Project directory to given path"""
        logger.debug("Func: projectDir/setter")
        self._pathsDict["projectDir"] = path

    @property
    def subProject(self):
        """Returns the name of the active sub-project"""
        logger.debug("Func: subProject/getter")
        return self._subProjectsList[self.currentSubIndex]

    @property
    def scenesDir(self):
        """Returns the absolute path of the scenes folder"""
        logger.debug("Func: scenesDir/getter")
        return self._pathsDict["scenesDir"]

    @property
    def currentTabIndex(self):
        """Returns the Category index at cursor position"""
        logger.debug("Func: currentTabIndex/getter")
        return self._currentsDict["currentTabIndex"]

    @currentTabIndex.setter
    def currentTabIndex(self, indexData):
        """Moves the cursor to the given category index"""
        logger.debug("Func: currentTabIndex/setter")
        if not 0 <= indexData < len(self._categories):
            msg="Tab index is out of range!"
            self._exception(101, msg)
            return
        if indexData == self.currentTabIndex:
            self.cursorInfo()
            return
        self._setCurrents("currentTabIndex", indexData)
        self.scanBaseScenes()
        self.currentBaseSceneName = ""
        self._currentVersionIndex = -1
        self._currentPreviewCamera = ""
        self.cursorInfo()

    @property
    def currentTabName(self):
        """Returns the Category name at cursor position"""
        logger.debug("Func: currentTabName/getter")
        return self._categories[self._currentsDict["currentTabIndex"]]

    @currentTabName.setter
    def currentTabName(self, tabName):
        """Moves the cursor to the given category name"""
        logger.debug("Func: currentTabIndex/setter")
        if tabName is self.currentTabName:
            self.cursorInfo()
            return
        try:
            index = self._categories.index(tabName)
        except ValueError:
            msg="Tab Name is not valid!"
            self._exception(101, msg)
            return
        self._setCurrents("currentTabIndex", index)
        self.scanBaseScenes()
        self.currentBaseSceneName = ""
        self._currentVersionIndex = -1
        self._currentPreviewCamera = ""
        self.cursorInfo()

    @property
    def currentSubIndex(self):
        """Returns the sub-project index at cursor position"""
        logger.debug("Func: currentSubIndex/getter")
        return self._currentsDict["currentSubIndex"]

    @currentSubIndex.setter
    def currentSubIndex(self, indexData):
        """Moves the cursor to the given sub-project index"""
        logger.debug("Func: currentSubIndex/setter")
        if not 0 <= indexData < len(self._subProjectsList):
            msg="Sub Project index is out of range!"
            # raise Exception([101, msg])
            self._exception(101, msg)
            return

        if indexData == self.currentSubIndex:
            self.cursorInfo()
            return

        self._setCurrents("currentSubIndex", indexData)
        self.scanBaseScenes()
        # de-select previous base scene
        self._currentBaseSceneName = ""
        self._currentVersionIndex = -1
        self._currentPreviewCamera = ""
        self.cursorInfo()

    @property
    def currentUser(self):
        """Returns the current user"""
        logger.debug("Func: currentUser/getter")

        return self._currentsDict["currentUser"]

    @currentUser.setter
    def currentUser(self, name):
        """Sets the current user"""
        logger.debug("Func: currentUser/setter")
        if name not in list(self._usersDict):
            msg="%s is not in the user list" %name
            # raise Exception([101, msg])
            self._exception(101, msg)
            return
        self._setCurrents("currentUser", name)

    @property
    def currentUserInitials(self):
        """Returns the current user initials"""
        logger.debug("Func: currentUserInitials/getter")
        try:
            return self._usersDict[self.currentUser]
        except KeyError: # safety purposes
            self.currentUser = list(self._usersDict)[0]
            return self._usersDict[self.currentUser]

    @property
    def currentMode(self):
        """Returns the current access mode (Load or Reference)"""
        logger.debug("Func: currentMode/getter")

        return self._currentsDict["currentMode"]

    @currentMode.setter
    def currentMode(self, state):
        """Sets the current access mode 0 == Load, 1 == Reference"""
        logger.debug("Func: currentMode/setter")

        if not type(state) is bool:
            print("DEBUGGGG", type(state))
            if state is 0:
                state = False
            elif state is 1:
                state = True
            else:
                msg = ("only boolean or 0-1 accepted, entered %s" %state)
                logger.error(msg)
                # raise Exception([101, msg])
                self._exception(101, msg)
                return
        self._setCurrents("currentMode", state)

    @property
    def currentBaseSceneName(self):
        """Returns current Base Scene Name at cursor position"""
        logger.debug("Func: currentBaseSceneName/getter")

        return self._currentBaseSceneName

    @currentBaseSceneName.setter
    def currentBaseSceneName(self, sceneName):
        """Moves the cursor to the given base scene name"""
        logger.debug("Func: currentBaseSceneName/setter")
        if not sceneName:
            self._currentBaseSceneName = ""
            self.currentVersionIndex = -1
            return
        if sceneName not in list(self._baseScenesInCategory):

            self.currentVersionIndex = -1
            return

        self._currentBaseSceneName = sceneName
        self._currentSceneInfo = self.loadSceneInfo()

        if self._currentSceneInfo == -2: # corrupted db file
            # self._currentSceneInfo == {}
            self._currentBaseSceneName = ""
            self.currentVersionIndex = -1
            msg = "Database file %s is corrupted"
            self._exception(200, msg)
            return

        if self._currentSceneInfo["ReferencedVersion"]:
            self.currentVersionIndex = self._currentSceneInfo["ReferencedVersion"]
        else:
            self.currentVersionIndex = len(self._currentSceneInfo["Versions"])
        self.cursorInfo()

    @property
    def currentBaseScenePath(self):
        """Returns absolute path of Base Scene at cursor position"""
        logger.debug("Func: currentBaseScenePath/getter")
        return os.path.join(self.projectDir, self._currentSceneInfo["Path"])

    @property
    def currentScenePath(self):
        """Returns absolute path of Base Scene Version at cursor position"""
        logger.debug("Func: currentBaseScenePath/getter")
        return os.path.join(self.projectDir, self._currentSceneInfo["Versions"][self.currentVersionIndex-1]["RelativePath"])

    @property
    def currentPreviewPath(self):
        """Returns absolute path of preview folder of the Base scene at cursor position"""
        logger.debug("Func: currentPreviewPath/getter")
        if self._currentSceneInfo["SubProject"] is not "None":
            path = os.path.join(self._pathsDict["previewsDir"], self._currentSceneInfo["Category"],
                                self._currentSceneInfo["Name"])
        else:
            path = os.path.join(self._pathsDict["previewsDir"], self._currentSceneInfo["Category"],
                                self._currentSceneInfo["SubProject"], self._currentSceneInfo["Name"])
        return path

    @property
    def currentVersionIndex(self):
        """Returns the index number of Version at cursor position"""
        logger.debug("Func: currentVersionIndex/getter")
        return self._currentVersionIndex

    @currentVersionIndex.setter
    def currentVersionIndex(self, indexData):
        """Moves the cursor to given Version index"""
        logger.debug("Func: currentVersionIndex/setter")
        if indexData <= 0:
            self._currentVersionIndex = -1
            self._currentThumbFile = ""
            self._currentNotes = ""
            self._currentPreviewCamera = ""
            return
        if not self._currentSceneInfo:
            return
        if not 1 <= indexData <= len(self._currentSceneInfo["Versions"]):
            msg = "out of range! %s" %indexData
            self._exception(101, msg)
            return
        self._currentVersionIndex = indexData
        self._currentNotes = self._currentSceneInfo["Versions"][self._currentVersionIndex-1]["Note"]
        self._currentPreviewsDict = self._currentSceneInfo["Versions"][self._currentVersionIndex-1]["Preview"]
        if not list(self._currentPreviewsDict):
            self._currentPreviewCamera = ""
        else:
            self._currentPreviewCamera = sorted(list(self._currentPreviewsDict))[0]

        self._currentThumbFile = self._currentSceneInfo["Versions"][self._currentVersionIndex-1]["Thumb"]
        self.cursorInfo()

    @property
    def currentDatabasePath(self):
        """Returns absolute path of database file of the scene at cursor position"""
        logger.debug("Func: currentDatabasePath/getter")

        if not self._currentSceneInfo:
            msg = "no current info"
            # logger.error(msg)
            # raise Exception([101, msg])
            self._exception(101, msg)
            return

        if self._currentSceneInfo["SubProject"] == "None":
            subP = ""
        else:
            subP = self._currentSceneInfo["SubProject"]

        dbFile = os.path.join (self.projectDir,
                      self._pathsDict["databaseDir"],
                      self._currentSceneInfo["Category"],
                      subP, "%s.json" %self._currentSceneInfo["Name"])
        return dbFile

    def cursorInfo(self):
        """function to return cursor position info for debugging purposes"""

        logger.info("""
        Category: {0}
        SubProject: {1}
        BaseScenes Under: {2}
        Current BaseScene: {3}
        Version: {4}
        Preview: {5}
        Thumbnail: {6}
        """.format(
            self._categories[self.currentTabIndex],
            self._subProjectsList[self.currentSubIndex],
            sorted(list(self._baseScenesInCategory)),
            self._currentBaseSceneName,
            self._currentVersionIndex,
            self._currentPreviewCamera,
            self._currentThumbFile
            ))

    def isGlobalFavorites(self):
        return self._userSettings["globalFavorites"]

    def getExtraColumns(self):
        return self._userSettings["extraColumns"]

    def getMasterDir(self):
        return self._pathsDict["masterDir"]

    def getUserDir(self):
        """Returns Documents Directory"""
        dir = os.path.expanduser('~')
        if not "Documents" in dir:
            dir = os.path.join(dir, "Documents")
        return os.path.normpath(dir)

    def getLocalSettingsDir(self):
        return self._pathsDict["localSettingsDir"]

    def getSharedSettingsDir(self):
        """Returns the general settings Directory where common settings are"""
        return self._pathsDict["sharedSettingsDir"]

    def getOpenSceneInfo(self):
        """
        Collects the necessary scene info by resolving the scene name and current project
        Returns: Dictionary{jsonFile, projectPath, subProject, category, shotName} or None
        """
        logger.debug("Func: getOpenSceneInfo")

        self._pathsDict["sceneFile"] = self.getSceneFile()
        if not self._pathsDict["sceneFile"]:
            return None

        # get name of the upper directory to find out base name
        sceneDir = os.path.abspath(os.path.join(self._pathsDict["sceneFile"], os.pardir))
        baseSceneName = os.path.basename(sceneDir)

        upperSceneDir = os.path.abspath(os.path.join(sceneDir, os.pardir))
        upperSceneDirName = os.path.basename(upperSceneDir)

        if upperSceneDirName in self._subProjectsList:
            subProjectDir = upperSceneDir
            subProject = upperSceneDirName
            categoryDir = os.path.abspath(os.path.join(subProjectDir, os.pardir))
            category = os.path.basename(categoryDir)

            dbCategoryPath = os.path.normpath(os.path.join(self._pathsDict["databaseDir"], category))
            dbPath = os.path.normpath(os.path.join(dbCategoryPath, subProject))

            pbCategoryPath = os.path.normpath(os.path.join(self._pathsDict["previewsDir"], category))
            pbSubPath = os.path.normpath(os.path.join(pbCategoryPath, subProject))
            pbPath = os.path.normpath(os.path.join(pbSubPath, baseSceneName))

        else:
            subProject = self._subProjectsList[0]
            categoryDir = upperSceneDir
            category = upperSceneDirName
            dbPath = os.path.normpath(os.path.join(self._pathsDict["databaseDir"], category))
            pbCategoryPath = os.path.normpath(os.path.join(self._pathsDict["previewsDir"], category))
            pbPath = os.path.normpath(os.path.join(pbCategoryPath, baseSceneName))

        jsonFile = os.path.join(dbPath, "{}.json".format(baseSceneName))
        if os.path.isfile(jsonFile):
            version = (self.niceName(self._pathsDict["sceneFile"])[-4:])
            self._openSceneInfo = {
                    "jsonFile":jsonFile,
                    "projectPath":self._pathsDict["projectDir"],
                    "subProject":subProject,
                    "category":category,
                    "shotName":baseSceneName,
                    "version":version,
                    "previewPath":pbPath
                    }
            return self._openSceneInfo
        else:
            return None

    def getCategories(self):
        """Returns All Valid Categories"""
        logger.debug("Func: getCategories")
        return self._categories

    def getSubProjects(self):
        """Returns list of sub-projects"""
        logger.debug("Func: getSubProjects")
        return self._subProjectsList

    def getUsers(self):
        """Returns nice names of all users"""
        logger.debug("Func: getUsers")
        return sorted(list(self._usersDict))

    def getBaseScenesInCategory(self):
        """Returns list of nice base scene names under the category at cursor position"""
        logger.debug("Func: getBaseScenesInCategory")
        self.scanBaseScenes()
        return self._baseScenesInCategory

    def getVersions(self):
        """Returns Versions List of base scene at cursor position"""
        logger.debug("Func: getVersions")
        try:
            return self._currentSceneInfo["Versions"]
        except:
            return []

    def getNotes(self):
        """returns (String) version notes on cursor position"""
        logger.debug("Func: getNotes")
        return self._currentNotes

    def getPreviews(self):
        """returns (list) nice preview names of version on cursor position"""
        logger.debug("Func: getPreviews")
        return sorted(list(self._currentPreviewsDict))

    def getThumbnail(self):
        """returns (String) absolute thumbnail path of version on cursor position"""
        logger.debug("Func: getThumbnail")
        return os.path.join(self.projectDir, self._currentThumbFile.replace("\\", "/"))

    def getFPS(self):
        """returns the project FPS setting"""
        # load it each time, since this setting is not limited to a single user
        projectSettingsDB = self.loadProjectSettings()
        try:
            fpsValue = projectSettingsDB["FPS"]
            return fpsValue
        except KeyError:
            msg = "Database Error while reading projectSettings.json"
            logger.error(msg)
            return None

    def getResolution(self):
        """returns the project Resolution setting as a list"""
        # load it each time, since this setting is not limited to a single user
        projectSettingsDB = self.loadProjectSettings()
        try:
            resolution = projectSettingsDB["Resolution"]
            return resolution
        except KeyError:
            msg = "Database Error while reading projectSettings.json"
            logger.error(msg)
            return None

    def getColorCoding(self, niceName=None):
        if niceName or niceName == "":
            try: keyColor = self._userSettings["colorCoding"][niceName]
            except KeyError: keyColor = "rgb (0, 0, 0, 255)"
            return keyColor
        else:
            return self._userSettings["colorCoding"]

    def getFormatsAndCodecs(self):
        """Returns the codecs which can be used in current workstation"""
        return None

    def createNewProject(self, resolvedPath, settingsData=None):
        """
        Creates New Project Structure

        Args:
            resolvedPath: (String) Destionation path of the project
            settingsData: (Dictionary) Dictionary data for project settings. (Optional)
                Example:
                    {"Resolution": [1920, 1080],
                                   "FPS": 25}

        Returns: (String) Resolved Path

        """

        logger.debug("Func: createNewProject")
        # check if there is a duplicate
        if not os.path.isdir(os.path.normpath(resolvedPath)):
            os.makedirs(os.path.normpath(resolvedPath))
        else:
            msg = "Project already exists"
            self._exception(340, msg)
            return

        # create Bare Minimum structure:
        os.mkdir(os.path.join(resolvedPath, "_REF"))
        os.makedirs(os.path.join(resolvedPath, "_TRANSFER", "FBX"))
        os.makedirs(os.path.join(resolvedPath, "_TRANSFER", "ALEMBIC"))
        os.makedirs(os.path.join(resolvedPath, "_TRANSFER", "OBJ"))
        os.mkdir(os.path.join(resolvedPath, "cache"))
        os.mkdir(os.path.join(resolvedPath, "data"))
        os.makedirs(os.path.join(resolvedPath, "images", "_CompRenders"))
        os.mkdir(os.path.join(resolvedPath, "particles"))
        os.mkdir(os.path.join(resolvedPath, "Playblasts"))
        os.makedirs(os.path.join(resolvedPath, "renderData", "depth"))
        os.makedirs(os.path.join(resolvedPath, "renderData", "fur"))
        os.makedirs(os.path.join(resolvedPath, "renderData", "iprImages"))
        os.makedirs(os.path.join(resolvedPath, "renderData", "mentalray"))
        os.makedirs(os.path.join(resolvedPath, "renderData", "shaders"))
        os.mkdir(os.path.join(resolvedPath, "scenes"))
        os.mkdir(os.path.join(resolvedPath, "scripts"))
        os.mkdir(os.path.join(resolvedPath, "sound"))
        os.makedirs(os.path.join(resolvedPath, "sourceimages", "_FOOTAGE"))
        os.makedirs(os.path.join(resolvedPath, "sourceimages", "_HDR"))
        os.makedirs(os.path.join(resolvedPath, "smDatabase"))

        # Create project settings file
        if not settingsData:
            settingsData = {"Resolution": [1920, 1080],
                                   "FPS": 25}

        self._dumpJson(settingsData, os.path.join(resolvedPath, "smDatabase", "projectSettings.json"))

        filePath = os.path.join(resolvedPath, "workspace.mel")
        file = open(filePath, "w")

        file.write('workspace -fr "scene" "scenes";\n')
        file.write('workspace -fr "3dPaintTextures" "sourceimages/3dPaintTextures";\n')
        file.write('workspace -fr "eps" "data";\n')
        file.write('workspace -fr "mentalRay" "renderData/mentalray";\n')
        file.write('workspace -fr "OBJexport" "_TRANSFER/OBJ";\n')
        file.write('workspace -fr "mel" "scripts";\n')
        file.write('workspace -fr "particles" "particles";\n')
        file.write('workspace -fr "STEP_DC" "data";\n')
        file.write('workspace -fr "CATIAV5_DC" "data";\n')
        file.write('workspace -fr "sound" "sound";\n')
        file.write('workspace -fr "furFiles" "renderData/fur/furFiles";\n')
        file.write('workspace -fr "depth" "renderData/depth";\n')
        file.write('workspace -fr "CATIAV4_DC" "data";\n')
        file.write('workspace -fr "autoSave" "autosave";\n')
        file.write('workspace -fr "diskCache" "cache";\n')
        file.write('workspace -fr "fileCache" "";\n')
        file.write('workspace -fr "IPT_DC" "data";\n')
        file.write('workspace -fr "SW_DC" "data";\n')
        file.write('workspace -fr "DAE_FBX export" "data";\n')
        file.write('workspace -fr "Autodesk Packet File" "";\n')
        file.write('workspace -fr "DAE_FBX" "data";\n')
        file.write('workspace -fr "DXF_DCE" "";\n')
        file.write('workspace -fr "mayaAscii" "scenes";\n')
        file.write('workspace -fr "iprImages" "renderData/iprImages";\n')
        file.write('workspace -fr "move" "data";\n')
        file.write('workspace -fr "mayaBinary" "scenes";\n')
        file.write('workspace -fr "fluidCache" "cache/fluid";\n')
        file.write('workspace -fr "clips" "clips";\n')
        file.write('workspace -fr "animExport" "data";\n')
        file.write('workspace -fr "templates" "assets";\n')
        file.write('workspace -fr "DWG_DC" "data";\n')
        file.write('workspace -fr "offlineEdit" "scenes/edits";\n')
        file.write('workspace -fr "translatorData" "data";\n')
        file.write('workspace -fr "renderData" "renderData";\n')
        file.write('workspace -fr "DXF_DC" "data";\n')
        file.write('workspace -fr "SPF_DCE" "";\n')
        file.write('workspace -fr "ZPR_DCE" "";\n')
        file.write('workspace -fr "furShadowMap" "renderData/fur/furShadowMap";\n')
        file.write('workspace -fr "audio" "sound";\n')
        file.write('workspace -fr "scripts" "scripts";\n')
        file.write('workspace -fr "IV_DC" "data";\n')
        file.write('workspace -fr "studioImport" "data";\n')
        file.write('workspace -fr "STL_DCE" "";\n')
        file.write('workspace -fr "furAttrMap" "renderData/fur/furAttrMap";\n')
        file.write('workspace -fr "FBX export" "data";\n')
        file.write('workspace -fr "JT_DC" "data";\n')
        file.write('workspace -fr "sourceImages" "sourceimages";\n')
        file.write('workspace -fr "DWG_DCE" "";\n')
        file.write('workspace -fr "animImport" "data";\n')
        file.write('workspace -fr "FBX" "data";\n')
        file.write('workspace -fr "movie" "movies";\n')
        file.write('workspace -fr "Alembic" "";\n')
        file.write('workspace -fr "furImages" "renderData/fur/furImages";\n')
        file.write('workspace -fr "IGES_DC" "data";\n')
        file.write('workspace -fr "furEqualMap" "renderData/fur/furEqualMap";\n')
        file.write('workspace -fr "illustrator" "data";\n')
        file.write('workspace -fr "UG_DC" "";\n')
        file.write('workspace -fr "images" "images";\n')
        file.write('workspace -fr "SPF_DC" "data";\n')
        file.write('workspace -fr "PTC_DC" "data";\n')
        file.write('workspace -fr "OBJ" "_TRANSFER/OBJ";\n')
        file.write('workspace -fr "CSB_DC" "data";\n')
        file.write('workspace -fr "STL_DC" "data";\n')
        file.write('workspace -fr "IGES_DCE" "";\n')
        file.write('workspace -fr "shaders" "renderData/shaders";\n')
        file.write('workspace -fr "UG_DCE" "";\n')
        file.close()

        # Copy the template project contents (if any)
        currentConventions = self.loadNameConventions()
        if currentConventions["templateFolder"]:
            if not os.path.isdir(currentConventions["templateFolder"]):
                self._info("Cannot find template folder => %s\n\nThe folder specified at shared settings cannot be found." %currentConventions["templateFolder"])
            else:
                self._copytree(currentConventions["templateFolder"], resolvedPath, symlinks=False, ignore=None)

        return resolvedPath

    def createSubproject(self, nameOfSubProject):
        """Creates a Scene Manager Sub-project"""
        logger.debug("Func: createSubproject")

        if nameOfSubProject in self._subProjectsList:
            msg = "%s is already in sub-projects list" % nameOfSubProject
            self._exception(340, msg)
            return

        self._subProjectsList.append(nameOfSubProject)
        self.saveSubprojects(self._subProjectsList)
        self.currentSubIndex = len(self._subProjectsList)-1
        return self._subProjectsList

    def executeFile(self, filePath, asSeq=True):
        """executes the file"""
        logger.debug("Func: showInExplorer")

        if not os.path.isfile(filePath.replace("\\", "/")):
            logger.warning("Given path is not a file")
            return
            pass

        # get execution user list
        try: exeDict = self._userSettings["executables"]
        except: exeDict = {"image_exec": "",
                                    "imageSeq_exec": "",
                                    "video_exec": "",
                                    "obj_exec": "",
                                    "fbx_exec": "",
                                    "alembic_exec": ""}

        def resolveExeFlags(rawFlag, filePath):
            extraFlags = re.findall(r'<(.*?)\>', rawFlag)
            exePath = rawFlag.split("<")[0]
            if exePath.endswith(" "):
                exePath = exePath[:-1]

            if "itemPath" in extraFlags:
                extraFlags[extraFlags.index("itemPath")] = filePath
            else:
                extraFlags.append(filePath)

            return [exePath]+extraFlags


        dump, ext = os.path.splitext(filePath)
        validImageFormats = [".jpg", ".png", ".exr", ".tga", ".tif", ".tiff", ".bmp", ".iff", ".dng", ".hdr", ".hdri", ".dpx"]
        validVideoFormats = [".avi", ".mp4", ".mov", ".mkv"]

        if ext in validImageFormats and asSeq==False and exeDict["image_exec"] != "":
            # execute image
            flagList = resolveExeFlags(exeDict["image_exec"], filePath)
            subprocess.Popen(flagList, shell=True)
            return
        elif ext in validImageFormats and asSeq==True and exeDict["imageSeq_exec"] != "":
            # execute imageSeq
            flagList = resolveExeFlags(exeDict["imageSeq_exec"], filePath)
            subprocess.Popen(flagList, shell=True)
            return
        elif ext in validVideoFormats and exeDict["video_exec"] != "":
            # execute video
            flagList = resolveExeFlags(exeDict["video_exec"], filePath)
            subprocess.Popen(flagList, shell=True)
            return
        elif ext == ".obj" and exeDict["obj_exec"] != "":
            # execute obj
            flagList = resolveExeFlags(exeDict["obj_exec"], filePath)
            subprocess.Popen(flagList, shell=True)
            return
        elif ext == ".fbx" and exeDict["fbx_exec"] != "":
            # execute fbx
            flagList = resolveExeFlags(exeDict["fbx_exec"], filePath)
            subprocess.Popen(flagList, shell=True)
            return
        elif ext == ".abc" and exeDict["alembic_exec"] != "":
            # execute alembic
            flagList = resolveExeFlags(exeDict["alembic_exec"], filePath)
            subprocess.Popen(flagList, shell=True)
            return
        else:
            if self.currentPlatform == "Windows":
                os.startfile(filePath)
            elif self.currentPlatform == "Linux":
                # logger.warning("Linux execution not yet implemented")
                subprocess.Popen(["xdg-open", filePath])
                pass
            else:
                # logger.warning("MacOs execution not yet implemented")
                subprocess.Popen(["open", filePath])
                pass

    def showInExplorer(self, tpath):
        """Opens the path in Windows Explorer(Windows) or Nautilus(Linux)"""
        logger.debug("Func: showInExplorer")
        if os.path.isfile(tpath):
            tpath = os.path.dirname(tpath)
        if self.currentPlatform == "Windows":
            os.startfile(tpath)
        elif self.currentPlatform == "Linux":
            subprocess.Popen(["xdg-open", tpath])
        else:
            subprocess.Popen(["open", tpath])

    def scanBaseScenes(self, categoryAs=None, subProjectAs=None, databaseDirAs=None):
        """Returns the basescene database files in current category"""
        logger.debug("Func: scanBaseScenes")
        if not databaseDirAs:
            databaseDirAs = self._pathsDict["databaseDir"]

        if self.currentSubIndex >= len(self._subProjectsList):
            self.currentSubIndex = 0

        if categoryAs:
            category = categoryAs
        else:
            try:
                category = self._categories[self.currentTabIndex]
            except IndexError:
                self.currentTabIndex = 0
                category = self._categories[self.currentTabIndex]

        if subProjectAs:
            if type(subProjectAs) == int: # it index number of projects list is given, get the name from t
                subProject = self._subProjectsList[subProjectAs]
            else:
                subProject = subProjectAs
        else:
            subProject = self._subProjectsList[self.currentSubIndex]

        categoryDBpath = os.path.normpath(os.path.join(databaseDirAs, category))
        self._folderCheck(categoryDBpath)
        if not (self.currentSubIndex == 0):
            try:
                categorySubDBpath = os.path.normpath(os.path.join(categoryDBpath, subProject)) # category name
            except IndexError:
                self.currentSubIndex = 0
                categorySubDBpath = os.path.normpath(os.path.join(categoryDBpath, subProject)) # category name
            self._folderCheck(categorySubDBpath)

            searchDir = categorySubDBpath
        else:
            searchDir = categoryDBpath

        self._baseScenesInCategory = {self.niceName(file):file for file in glob(os.path.join(searchDir, '*.json'))}
        return self._baseScenesInCategory # dictionary of json files

    def exportTransfers(self, name, isSelection=True, isObj=True, isAlembic=True, isFbx=True, isVrayProxy=False, isRedShiftProxy=False, timeRange=[1, 10]):
        """
        Exports scene or selection with defined settings
        :param name: (string) name of the export
        :param isSelection: (Boolean) If true, exports only selected items, else whole scene
        :param isObj: (Boolean) if True, exports obj format
        :param isAlembic: (Boolean) if True, exports alembic format
        :param isFbx: (Boolean) if True, exports fbx format
        :param timeRange: (List) Defines export time range as [Startframe, Endframe]
        :return: True if successfull
        """

        subFolders = os.path.dirname(os.path.normpath(name))
        baseName = os.path.basename(name)
        exportSettings = self.loadExportSettings()


        if isObj:
            objSettings = exportSettings
            objDir = os.path.join(self._pathsDict["transferDir"],"OBJ", subFolders)
            self._folderCheck(objDir)
            objFilePath = os.path.join(objDir,"%s.obj" %baseName)

            if os.path.isfile(objFilePath):
                msg = "The following file will be overwritten if you continue:\n %s\nChoose Yes to overwrite file and continue" % (
                    os.path.basename(objFilePath))
                title = "Are you Sure?"
                if not self._question(msg=msg):
                    pass
                else:
                    self._exportObj(objFilePath, exportSettings=objSettings, exportSelected=isSelection)
            else:
                self._exportObj(objFilePath, exportSettings=objSettings, exportSelected=isSelection)


        if isAlembic:
            alembicSettings = exportSettings
            # edit in - out
            # alembicSettings["AnimTimeRange"] = "StartEnd"
            # alembicSettings["StartFrame"] = timeRange[0]
            # alembicSettings["EndFrame"] = timeRange[1]


            alembicDir = os.path.join(self._pathsDict["transferDir"],"ALEMBIC", subFolders)
            self._folderCheck(alembicDir)
            alembicFilePath = os.path.join(alembicDir,"%s.abc" %baseName)
            if os.path.isfile(alembicFilePath):
                msg = "The following file will be overwritten if you continue:\n %s\nChoose Yes to overwrite file and continue" % (
                    os.path.basename(alembicFilePath))
                title = "Are you Sure?"
                if not self._question(msg=msg):
                    pass
                else:
                    self._exportAlembic(alembicFilePath, exportSettings=alembicSettings, exportSelected=isSelection, timeRange=timeRange)
            else:
                self._exportAlembic(alembicFilePath, exportSettings=alembicSettings, exportSelected=isSelection, timeRange=timeRange)

        if isFbx:
            fbxSettings = exportSettings

            fbxDir = os.path.join(self._pathsDict["transferDir"],"FBX", subFolders)
            self._folderCheck(fbxDir)
            fbxFilePath = os.path.join(fbxDir,"%s.fbx" %baseName)
            if os.path.isfile(fbxFilePath):
                msg = "The following file will be overwritten if you continue:\n %s\nChoose Yes to overwrite file and continue" % (
                    os.path.basename(fbxFilePath))
                title = "Are you Sure?"
                if not self._question(msg=msg):
                    pass
                else:
                    self._exportFbx(fbxFilePath, exportSettings=fbxSettings, exportSelected=isSelection, timeRange=timeRange)
            else:
                self._exportFbx(fbxFilePath, exportSettings=fbxSettings, exportSelected=isSelection, timeRange=timeRange)

        if isVrayProxy:
            vrayProxySettings = exportSettings
            vrayProxyDir = os.path.join(self._pathsDict["transferDir"], "vrayProxy", subFolders)
            self._folderCheck(vrayProxyDir)
            vrayProxyFilePath = os.path.join(vrayProxyDir, "%s.vrmesh" % baseName)
            if os.path.isfile(vrayProxyFilePath):
                msg = "The following file will be overwritten if you continue:\n %s\nChoose Yes to overwrite file and continue" % (
                    os.path.basename(vrayProxyFilePath))
                title = "Are you Sure?"
                if not self._question(msg=msg):
                    pass
                else:
                    self._exportVray(vrayProxyFilePath, exportSettings=vrayProxySettings, exportSelected=isSelection, timeRange=timeRange)
            else:
                self._exportVray(vrayProxyFilePath, exportSettings=vrayProxySettings, exportSelected=isSelection, timeRange=timeRange)

            pass

        if isRedShiftProxy:
            print("export RedShift Proxy function is under progress")
            pass

        return True

    def importTransfers(self, itemAbsPath):
        importSettings = self.loadImportSettings()
        extension = os.path.splitext(itemAbsPath)[1]

        if extension.lower() == ".obj":
            objSettings = importSettings
            self._importObj(itemAbsPath, objSettings)
        elif extension.lower() == ".fbx":
            fbxSettings = importSettings
            self._importFbx(itemAbsPath, fbxSettings)
        elif extension.lower() == ".abc":
            alembicSettings = importSettings
            self._importAlembic(itemAbsPath, alembicSettings)
        elif extension.lower() == ".vrmesh":
            vrayProxySettings = importSettings
            self._importVray(itemAbsPath, vrayProxySettings)
        else:
            self._info("Format is not supported")

    def scanTransfers(self):

        transferDict = {"obj":{},
                        "fbx":{},
                        "abc":{},
                        "vrmesh":{},
                        "rs":{}}

        objPath = os.path.join(self._pathsDict["transferDir"], "OBJ")
        if os.path.exists(objPath):
            # first collect all the obj files
            transferDict["obj"] = {self.niceName(y):y for x in os.walk(objPath) for y in glob(os.path.join(x[0], '*.obj'))}

        abcPath = os.path.join(self._pathsDict["transferDir"], "ALEMBIC")
        if os.path.exists(abcPath):
            transferDict["abc"] = {self.niceName(y):y for x in os.walk(abcPath) for y in glob(os.path.join(x[0], '*.abc'))}
        #
        fbxPath = os.path.join(self._pathsDict["transferDir"], "FBX")
        if os.path.exists(fbxPath):
            transferDict["fbx"] = {self.niceName(y):y for x in os.walk(fbxPath) for y in glob(os.path.join(x[0], '*.fbx'))}

        vrayProxyPath = os.path.join(self._pathsDict["transferDir"], "vrayProxy")
        if os.path.exists(fbxPath):
            transferDict["vrmesh"] = {self.niceName(y):y for x in os.walk(vrayProxyPath) for y in glob(os.path.join(x[0], '*.vrmesh'))}

        rsProxyPath = os.path.join(self._pathsDict["transferDir"], "rsProxy")
        if os.path.exists(fbxPath):
            transferDict["rs"] = {self.niceName(y):y for x in os.walk(rsProxyPath) for y in glob(os.path.join(x[0], '*.rs'))}

        return transferDict

    def getProjectReport(self):
        projectDir = self.getProjectDir()

        # check for the databaseDirectory
        databaseDir = self._pathsDict["masterDir"]
        if not os.path.isdir(databaseDir):
            self._exception(360, "Project Folder does not have Tik Manager Database")
            return

        def uniqueList(seq, idfun=None):
            # order preserving
            if idfun is None:
                def idfun(x): return x
            seen = {}
            result = []
            for item in seq:
                marker = idfun(item)
                # in old Python versions:
                # if seen.has_key(marker)
                # but in new ones:
                if marker in seen: continue
                seen[marker] = 1
                result.append(item)
            return result

        def getdbfiles(folder):
            if os.path.isdir(folder):
                swCategories = os.listdir(folder)
                for category in swCategories:
                    # get all json files in it recursively
                    for root, dirs, files in os.walk(os.path.join(folder, category)):
                        for file in files:
                            if file.endswith(".json"):
                                yield (os.path.join(root, file))

        def getSoftwareReports():
            softwareReport = "-----------------\nSoftware Reports:\n-----------------\n"
            softwareDBList = ["mayaDB", "maxDB", "houdiniDB", "nukeDB", "photoshopDB"]
            allUsers = []
            for dbName in softwareDBList:
                # get all base scenes in database folder
                dbFiles = getdbfiles(os.path.join(databaseDir, dbName))

                # get users in the base scene database files
                users = []
                workstations = []
                categories = []
                for file in dbFiles:
                    dbData = self._loadJson(file)
                    users += [v["User"] for v in dbData["Versions"]]
                    workstations += [v["Workstation"] for v in dbData["Versions"]]
                    categories.append(dbData["Category"])

                if categories != []:
                    softwareReport = """
{0}
{1}
{2}
Users: {3}
Used Workstations: {4}
Used Categories: {5}""".format(softwareReport,
                               dbName.replace("DB", "").capitalize(),
                               "-" * len(dbName.replace("DB", "")),
                               ", ".join(uniqueList(users)),
                               ", ".join(uniqueList(workstations)),
                               ", ".join(uniqueList(categories)),
                               )

                return softwareReport

        def getWorkstationReports():
            # find the workstation log paths
            logFolder = os.path.join(self._pathsDict["masterDir"], "progressLogs")
            workstationReport = "--------------------\nWorkstation Reports:\n--------------------\n"
            if not os.path.isdir(logFolder):
                return "%sNo Report for Workstations" %workstationReport
            # get all folders in here and add them to the workstations list
            folderContent = os.listdir(logFolder)
            workstationList = [x for x in folderContent if os.path.isdir(os.path.join(logFolder, x))]
            # go through each workstation folder
            grandTotalDays = 0
            grandTotalHours = 0
            grandDaysList = []
            for ws in workstationList:
                # get total log files and put the number to workingDays variable
                wsFolder = os.path.join(logFolder, ws)
                logFiles = [logFile for logFile in os.listdir(wsFolder) if os.path.splitext(logFile)[1] == ".log"]
                totalWorkDays = len(logFiles)
                totalWorkHours = 0
                firstDay = datetime.datetime.strptime(logFiles[0].replace(".log", ""), "%y%m%d").strftime("%d.%b.%Y")
                lastDay = datetime.datetime.strptime(logFiles[-1].replace(".log", ""), "%y%m%d").strftime("%d.%b.%Y")
                grandDaysList.append(int(logFiles[0].replace(".log", "")))
                grandDaysList.append(int(logFiles[-1].replace(".log", "")))
                wsUsers=[]
                # for each log file:
                # get first and last line

                for file in logFiles:
                    absFilePath = os.path.join(wsFolder, file)
                    f = open(absFilePath, "r")
                    if f.mode == "r":
                        fileContent = f.readlines()
                    else:
                        return "Cannot Read Log File %s" %absFilePath
                    f.close()

                    firstLineInfo = fileContent[0].split("***")
                    lastLineInfo = fileContent[-1].split("***")
                    totalWorkHours += (float(lastLineInfo[3]) - float(firstLineInfo[3])) / 60
                    wsUsers += [x.split("***")[1] for x in fileContent]

                grandTotalDays += totalWorkDays
                grandTotalHours += totalWorkHours

                grandFirstDay = datetime.datetime.strptime(str(min(grandDaysList)), "%y%m%d").strftime("%d.%b.%Y")
                grandLastDay = datetime.datetime.strptime(str(max(grandDaysList)), "%y%m%d").strftime("%d.%b.%Y")
                workstationReport = """
{0}
{1}:
{2}
Total Work Days: {3} ({4} - {5})
Estimated Total Hours of work*: {6}
User(s): {7}

""".format(workstationReport, ws, "-" * len(str(ws)), totalWorkDays, firstDay, lastDay, '%.1f'%(totalWorkHours), ", ".join(uniqueList(wsUsers)))

            workstationReport = "{0}\nGrand Total:\n------------\nTotal Days: {1} ({2} - {3}\nTotal Hours: {4}\n\n*Please note that work hours are a rough estimation based on save/load periods".format(workstationReport, grandTotalDays, grandFirstDay, grandLastDay, '%.1f'%(grandTotalHours))
            return workstationReport

        totalReport = "Tik Manager Report for Project: '{0}'\n\n{1}\n\n{2}".format(os.path.basename(projectDir), getSoftwareReports(), getWorkstationReports())
        # print(totalReport)

        now = datetime.datetime.now()
        filename = "_ProjectReport_{0}.txt".format(now.strftime("%Y.%m.%d.%H.%M"))
        filePath = os.path.join(databaseDir, filename)
        file = open(filePath, "w")
        file.write(totalReport)
        file.close()
        logger.info("Report has been logged => %s" %filePath)


        return totalReport


    def addNote(self, note):
        """Adds a note to the version at current position"""
        logger.debug("Func: addNote")

        if not self._currentBaseSceneName:
            logger.warning("No Base Scene file selected")
            return
        if self._currentVersionIndex == -1:
            logger.warning("No Version selected")
            return
        now = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M")
        self._currentNotes = "%s\n[%s] on %s\n%s\n" % (self._currentNotes, self.currentUser, now, note)
        self._currentSceneInfo["Versions"][self._currentVersionIndex-1]["Note"] = self._currentNotes
        self._dumpJson(self._currentSceneInfo, self._baseScenesInCategory[self._currentBaseSceneName])

    def addUser(self, fullName, initials):
        """
        Adds a new user to the database
        :param fullName: (String)
        :param initials: (String)
        :return: None
        """
        logger.debug("Func: addUser")

        # old Name
        currentDB = self.loadUsers()
        # currentDB, dbFile = self.initUsers()
        initialsList = currentDB.values()
        if initials in initialsList:
            msg="Initials are in use"
            # raise Exception([340, msg])
            self._exception(340, msg)
            return
            # return -1, msg
        currentDB[fullName] = initials
        self._dumpJson(currentDB, self._pathsDict["usersFile"])
        self._usersDict = currentDB
        return None, None

    def removeUser(self, fullName):
        """Removes the user from database"""
        logger.debug("Func: removeUser")

        # old Name removeUser
        currentDB = self.loadUsers()
        del currentDB[fullName]
        self._dumpJson(currentDB, self._pathsDict["usersFile"])
        self._usersDict = currentDB
        return None, None

    def addCategory(self, categoryName):
        """Adds a new category to the database"""
        curCategories = self.loadCategories()
        if categoryName in curCategories:
            msg = "Duplicate Category names are not allowed"
            # logger.warning(msg)
            # raise Exception([340, msg])
            self._exception(101, msg)
            return
            # return -1
        curCategories.append(categoryName)
        self._dumpJson(curCategories, self._pathsDict["categoriesFile"])
        self._categories = curCategories
        return

    def moveCategory(self, category, direction):
        """
        Moves the category index one step towards given direction
        This Fuction has been moved to the UI
        """
        pass

    def isCategoryTrash(self, categoryName, dbPath=None):
        """Checks if the given category(by name) is empty or not"""
        if not dbPath:
            dbPath = self._pathsDict["databaseDir"]
        for subP in self._subProjectsList:
            baseScenes = self.scanBaseScenes(categoryAs=categoryName, subProjectAs=subP, databaseDirAs=dbPath)
            if baseScenes:
                return False #This category is NOT TRASH
        return True


    def removeCategory(self, categoryName):
        """Removes the category from database"""
        curCategories = self.loadCategories()
        if len(curCategories) == 1:
            # Last category cannot be removed
            msg = "Last Category cannot be removed"
            # logger.warning(msg)
            # raise Exception([360, msg])
            self._exception(360, msg)
            return

        if categoryName in curCategories:
            # Check if category about to be removed is empty
            for subP in self._subProjectsList:
                baseScenes = self.scanBaseScenes(categoryAs=categoryName, subProjectAs=subP)
                if baseScenes:
                    # if it in not empty abort
                    msg = "Category is not empty. Aborting..."
                    # logger.warning(msg)
                    # raise Exception([360, msg])
                    self._exception(360, msg)
                    return

            # remove the empty category
            curCategories.remove(categoryName)
            self._dumpJson(curCategories, self._pathsDict["categoriesFile"])
            self._categories = curCategories
            return

        else:
            msg = "Specified Category does not exist"
            # logger.warning(msg)
            # raise Exception([101, msg])
            self._exception(101, msg)
            return

    def playPreview(self, camera):
        """Runs the playblast at cursor position"""
        logger.debug("Func: playPreview")
        absPath = os.path.join(self.projectDir, self._currentPreviewsDict[camera].replace("\\", "/"))
        self.executeFile(absPath)
        return

    def removePreview(self):
        """Deletes the preview file and removes it from the database"""
        logger.debug("Func: removePreview")

        if self._currentPreviewCamera:
            previewName = self._currentPreviewCamera
            previewFile = self._currentPreviewsDict[self._currentPreviewCamera]
            os.remove(os.path.join(self.projectDir, self._currentPreviewsDict[self._currentPreviewCamera]))
            del self._currentPreviewsDict[self._currentPreviewCamera]
            self._currentSceneInfo["Versions"][self._currentVersionIndex-1]["Preview"] = self._currentPreviewsDict
            self._dumpJson(self._currentSceneInfo, self._baseScenesInCategory[self.currentBaseSceneName])
            logger.info("""Preview file deleted and removed from database successfully 
            Preview Name: {0}
            Path: {1}
                        """.format(previewName, previewFile))


    def deleteBasescene(self, databaseFile):
        """
        Deletes the given Base Scene and ALL its versions. Removes it from the database completely
        !!!USE WITH CAUTION!!!
        :param databaseFile: (String) Absolute path of the database file
        :return: None
        """
        logger.debug("Func: deleteBasescene")

        #ADMIN ACCESS
        jsonInfo = self._loadJson(databaseFile)
        if jsonInfo == -2:
            return -2
        # delete all version files
        for version in jsonInfo["Versions"]:
            try:
                os.remove(os.path.join(self.projectDir, version["RelativePath"]))
            except:
                msg = "Cannot delete scene version:%s" % (version["RelativePath"])
                logger.warning(msg)
                raise Exception([203, msg])
                # pass

        # delete reference file
        if jsonInfo["ReferenceFile"]:
            try:
                os.remove(os.path.join(self.projectDir, jsonInfo["ReferenceFile"]))
            except:
                msg = "Cannot delete reference file %s" % (jsonInfo["ReferenceFile"])
                logger.warning(msg)
                raise Exception([203, msg])
                # pass

        # delete base scene directory
        scene_path = os.path.join(self.projectDir, jsonInfo["Path"])
        try:
            os.rmdir(scene_path)
        except:
            msg = "Cannot delete scene path %s" % (scene_path)
            self._exception(203, msg)
        # delete json database file
        try:
            os.remove(os.path.join(self.projectDir, databaseFile))
        except:
            msg = "Cannot delete scene path %s" % (databaseFile)
            self._exception(203, msg)
        msg = "all database entries and version files of %s deleted" %databaseFile
        logger.debug(msg)
        self.errorLogger(title="Deleted Base Scene", errorMessage=msg)

    def deleteReference(self, databaseFile):
        """
        Deletes the Reference file of the given Base Scene (If exists).
        Basically this is opposite of what "makeReference"  method does.
        :param databaseFile: (String) Absolute path of the database file
        :return: None
        """
        logger.debug("Func: deleteReference")

        #ADMIN ACCESS
        jsonInfo = self._loadJson(databaseFile)
        if jsonInfo == -2:
            return -2

        if jsonInfo["ReferenceFile"]:
            try:
                referenceFile = jsonInfo["ReferenceFile"]
                os.remove(os.path.join(self.projectDir, jsonInfo["ReferenceFile"]))
                jsonInfo["ReferenceFile"] = None
                jsonInfo["ReferencedVersion"] = None
                self._dumpJson(jsonInfo, databaseFile)
                self.errorLogger(title="Deleted Reference File", errorMessage="%s deleted" %referenceFile)
            except:
                msg = "Cannot delete reference file %s" % (jsonInfo["ReferenceFile"])
                logger.warning(msg)
                raise Exception([203, msg])
                pass

    def makeReference(self):
        """Creates a Reference copy from the base scene version at cursor position"""
        logger.debug("Func: makeReference")

        if self._currentVersionIndex == -1:
            msg = "Cursor is not on a Base Scene Version. Cancelling"
            self._exception(101, msg)
            return
            # return

        absVersionFile = os.path.join(self.projectDir, self._currentSceneInfo["Versions"][self._currentVersionIndex-1]["RelativePath"])
        name = os.path.split(absVersionFile)[1]
        filename, extension = os.path.splitext(name)
        referenceName = "{0}_{1}_forReference".format(self._currentSceneInfo["Name"], self._currentSceneInfo["Category"])
        relReferenceFile = os.path.join(self._currentSceneInfo["Path"], "{0}{1}".format(referenceName, extension))
        absReferenceFile = os.path.join(self.projectDir, relReferenceFile)
        shutil.copyfile(absVersionFile, absReferenceFile)
        self._currentSceneInfo["ReferenceFile"] = relReferenceFile
        # SET the referenced version as the 'VISUAL INDEX NUMBER' starting from 1
        self._currentSceneInfo["ReferencedVersion"] = self._currentVersionIndex

        self._dumpJson(self._currentSceneInfo, self._baseScenesInCategory[self.currentBaseSceneName])

    def saveCallback(self):
        """Callback function to update reference files when files saved regularly"""

        ## TODO // TEST IT
        self._pathsDict["sceneFile"] = self.getSceneFile()
        try:
            openSceneInfo = self.getOpenSceneInfo()
            if not openSceneInfo:
                return
        except TypeError:
            return
        if openSceneInfo["jsonFile"]:
            jsonInfo = self._loadJson(openSceneInfo["jsonFile"])
            if jsonInfo["ReferenceFile"]:
                absRefFile = os.path.join(self._pathsDict["projectDir"], jsonInfo["ReferenceFile"])
                # TODO : ref => Dict
                absBaseSceneVersion = os.path.join(self._pathsDict["projectDir"], jsonInfo["Versions"][int(jsonInfo["ReferencedVersion"]) - 1]["RelativePath"])
                # if the refererenced scene file is the saved file (saved or saved as)
                if self._pathsDict["sceneFile"] == absBaseSceneVersion:
                    # copy over the forReference file
                    try:
                        shutil.copyfile(self._pathsDict["sceneFile"], absRefFile)
                        print("Scene Manager Update:\nReference File Updated")
                    except:
                        pass

    def checkReference(self, databaseFile, deepCheck=False):
        """
        Checks the Reference integrity of the base scene
        :param databaseFile: (String) Absolute path of the database file of the Base Scene
        :param deepCheck: (Bool) If True, iterates an additional checksum test. May be time
        consuming for large files or on systems with slow network speed.
        :return: Integer Codes: -2 => Error code for corrupted database file
                                -1 => Code Red : Reference File does not exist or checksum mismatch
                                0 => Code Yellow : No reference file found on database file
                                1 => Code Green : Checked without error
        """
        logger.debug("Func: checkReference")

        sceneInfo = self._loadJson(databaseFile)
        if sceneInfo == -2:
            return -2 # Corrupted database file

        if sceneInfo["ReferenceFile"]:
            relVersionFile = sceneInfo["Versions"][sceneInfo["ReferencedVersion"] - 1]["RelativePath"].replace("\\", "/")
            absVersionFile = os.path.join(self.projectDir, relVersionFile)
            relRefFile = sceneInfo["ReferenceFile"].replace("\\", "/")
            absRefFile = os.path.join(self.projectDir, relRefFile)

            if not os.path.isfile(absRefFile):
                logger.info("CODE RED: Reference File does not exist")
                return -1 # code red
            else:
                if deepCheck:
                    if filecmp.cmp(absVersionFile, absRefFile):
                        logger.info("CODE GREEN: Everything is OK")
                        return 1 # code Green
                    else:
                        logger.info("CODE RED: Checksum mismatch with reference file")
                        return -1 # code red
                else:
                    logger.info("CODE GREEN: Everything is OK")
                    return 1 # code Green
        else:
            logger.info("CODE YELLOW: File does not have a reference copy")
            return 0 # code yellow

    def errorLogger(self, title="", errorMessage=""):
        """
        Logs the error message
        :param title: (String) Title of the message
        :param errorMessage: (String) Body of the error message
        :return:
        """
        #
        logger = logging.getLogger('SceneManager')
        filePath = os.path.join(self._pathsDict["masterDir"], "sm_logs.log")
        file_logger = logging.FileHandler(filePath)
        logger.addHandler(file_logger)
        logger.setLevel(logging.DEBUG)

        now = datetime.datetime.now()
        timeInfo = now.strftime("%d.%m.%Y - %H:%M")
        userInfo = self.currentUser
        machineInfo = socket.gethostname()
        ## stuff
        logMessage = "-----------------------------------------\n" \
                     "{0} - {1}\n" \
                     "-----------------------------------------\n" \
                     "Log Message:\n" \
                     "{2}\n\n" \
                     "User: {3}\n" \
                     "Workstation: {4}\n".format(title, timeInfo, errorMessage, userInfo, machineInfo)

        logger.debug(logMessage)

        logger.removeHandler(file_logger)
        file_logger.flush()
        file_logger.close()

    def progressLogger(self, action, actionPath):
        logger = logging.getLogger('progressLogs')
        userInfo = self.currentUser
        machineInfo = socket.gethostname()

        currentDT = datetime.datetime.now()
        today = currentDT.strftime("%y%m%d")
        timeStamp = currentDT.hour*60+currentDT.minute

        logFolder = os.path.join(self._pathsDict["masterDir"], "progressLogs", machineInfo)
        self._folderCheck(logFolder)
        logFile = os.path.join(logFolder, "%s.log" %today)
        file_logger = logging.FileHandler(logFile)
        logger.addHandler(file_logger)
        logger.setLevel(logging.DEBUG)

        logMessage = "{0}***{1}***{2}***{3}".format(action, userInfo, actionPath, timeStamp)

        logger.debug(logMessage)
        logger.removeHandler(file_logger)
        file_logger.flush()
        file_logger.close()


    def checkPassword(self, password):
        """Compares the given password with the hashed password file. Returns True if matches else False"""
        # get the hash
        pswFile = self._pathsDict["adminPass"]

        if os.path.isfile(pswFile):
            f = open(pswFile, "r")
            if f.mode == "r":
                hashedPass = f.read()
            else:
                return None
            f.close()
        ## use the default password hash if there is no password file
        else:
            hashedPass="7110eda4d09e062aa5e4a390b0a572ac0d2c0220"

        passToCheck = (hashlib.sha1(str(password).encode('utf-8')).hexdigest())

        if passToCheck == hashedPass:
            return True
        else:
            return False

    def changePassword(self, oldPassword, newPassword):
        """
        Changes the password and saves the hash
        :param oldPassword: (String)
        :param newPassword: (String)
        :return: (bool) True if successfull
        """
        if self.checkPassword(oldPassword):
            pswFile = self._pathsDict["adminPass"]
            tempFile = os.path.normpath(os.path.join(self._pathsDict["sharedSettingsDir"], "adminPassTmp.psw"))
            newHash = (hashlib.sha1(str(newPassword).encode('utf-8')).hexdigest())

            f = open(tempFile, "w+")
            f.write(newHash)
            f.close()
            shutil.copyfile(tempFile, pswFile)
            os.remove(tempFile)
            return True
        else:
            return False

    def _exception(self, code, msg):
        """Exception report function. Throws a log error and raises an exception"""

        logger.error("Exception %s" %self.errorCodeDict[code])
        logger.error(msg)
        raise Exception (code, msg)

    def _checkRequirements(self):
        """
        Checks the requirements for platform and administrator rights. Returns [None, None] if passes both
        Returns: (List) [ErrorCode, ErrorMessage]
        """
        logger.debug("Func: _checkRequirements")

        # check platform
        currentOs = platform.system()
        if currentOs != "Linux" and currentOs != "Windows":
            self._exception(210, "Operating System is not supported\nCurrently only Windows and Linux supported")
            return -1, ["OS Error", "Operating System is not supported",
                        "Scene Manager only supports Windows and Linux Operating Systems"]
        return None, None

    def _folderCheck(self, folder):
        """Checks if the folder exists, creates it if doesnt"""
        logger.debug("Func: _folderCheck")

        if not os.path.isdir(os.path.normpath(folder)):
            os.makedirs(os.path.normpath(folder))
        return folder

    def nameCheck(self, text, allowSpaces=False, directory=False):
        """Checks the text for illegal characters, Returns:  corrected Text or -1 for Error """
        logger.debug("Func: nameCheck")
        aSpa = " " if allowSpaces else ""
        dir = "\\\\:" if directory else ""

        pattern = r'^[:/A-Za-z0-9%s%s.A_-]*$' %(dir, aSpa)

        if re.match(pattern, text):
            return True
        else:
            return False


    def niceName(self, path):
        """Gets the base name of the given filename"""
        logger.debug("Func: niceName")

        basename = os.path.split(path)[1]
        return os.path.splitext(basename)[0]

    def resolveProjectPath(self, projectRoot, projectName, brandName, client):
        """
        METHOD IS DEPRECATED AND NO LONGER NEEDED
        Parses the info to the absolute project folder path
        """
        logger.debug("Func: resolveProjectPath")

        if projectName == "" or projectRoot == "":
            msg = ("Fill the mandatory fields")
            self._exception(341, msg)
            return

        projectDate = datetime.datetime.now().strftime("%y%m%d")

        nameList = [x for x in [brandName, projectName, client, projectDate] if x != ""]
        fullName = "_".join(nameList)
        fullPath = os.path.join(os.path.normpath(projectRoot), fullName)
        return fullPath

    ## Database loading / saving functions
    ## -----------------------------

    def _loadJson(self, file):
        """Loads the given json file"""
        # TODO : Is it paranoid checking?
        if os.path.isfile(file):
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    return data
            except ValueError:
                msg = "Corrupted JSON file => %s" % file
                # logger.error(msg)
                self._exception(200, msg)
                # return -2 # code for corrupted json file
        else:
            msg = "File cannot be found => %s" % file
            self._exception(201, msg)

    def _dumpJson(self, data, file):
        """Saves the data to the json file"""
        # name, ext = os.path.splitext(unicode(file).encode("utf-8"))
        name, ext = os.path.splitext(compat.encode(file))
        # tempFile = ("{0}.tmp".format(name)).decode("utf-8")
        tempFile = ("{0}.tmp".format(name))
        with open(tempFile, "w") as f:
            json.dump(data, f, indent=4)
        shutil.copyfile(tempFile, file)
        os.remove(tempFile)

    def loadProjectSettings(self):
        """Loads Project Settings from file"""
        if not os.path.isfile(self._pathsDict["projectSettingsFile"]):
            defaultProjectSettings = self._sceneManagerDefaults["defaultProjectSettings"]
            self._dumpJson(defaultProjectSettings, self._pathsDict["projectSettingsFile"])
            return defaultProjectSettings
        else:
            projectSettingsDB = self._loadJson(self._pathsDict["projectSettingsFile"])
            if projectSettingsDB== -2:
                return -2
            return projectSettingsDB

    def saveProjectSettings(self, data):
        """Dumps the data to the project settings database file"""
        try:
            self._dumpJson(data, self._pathsDict["projectSettingsFile"])
            msg = ""
            return 0, msg
        except:
            msg = "Cannot save current settings"
            return -1, msg

    def loadUsers(self):
        """Load Users from file"""
        logger.debug("Func: loadUsers")

        # old Name
        if not os.path.isfile(self._pathsDict["usersFile"]):
            # userDB = {"Generic": "gn"}
            defaultUsers = self._sceneManagerDefaults["defaultUsers"]
            self._dumpJson(defaultUsers, self._pathsDict["usersFile"])
            return defaultUsers
        else:
            userDB = self._loadJson(self._pathsDict["usersFile"])
            if userDB == -2:
                return -2
            return userDB

    def loadRecentProjects(self):
        """Loads Recent Projects List"""
        logger.debug("Func: loadRecentProjects")
        recentProjectsFilePath = self._pathsDict["recentProjectsFile"]

        if os.path.isfile(recentProjectsFilePath):
            recentProjectsData = self._loadJson(recentProjectsFilePath)
            if recentProjectsData == -2:
                return -2
        else: # no recent projects
            recentProjectsData = []

        return recentProjectsData

    def addToRecentProjects(self, absPath):
        """
        Adds the given project info to the favorites database
        :param shortName: (String) Name of the project
        :param absPath: (String) Absolute path of the project folder
        :return: (List) [Favorites Data]
        """
        logger.debug("Func: addToFavorites")

        # old Name userFavoritesAdd
        recentProjectsData = self.loadRecentProjects()

        if absPath in recentProjectsData:
            recentProjectsData.remove(absPath)
        recentProjectsData.append(absPath)
        if len(recentProjectsData) > 10:
            recentProjectsData.pop(0)
        self._dumpJson(recentProjectsData, self._pathsDict["recentProjectsFile"])
        return recentProjectsData

    def loadFavorites(self):
        """Loads Bookmarked projects"""
        logger.debug("Func: loadFavorites")
        bookmarkPath = self._pathsDict["bookmarksFile"] if self._userSettings["globalFavorites"] else self._pathsDict["localBookmarksFile"]

        if os.path.isfile(bookmarkPath):
            bookmarksData = self._loadJson(bookmarkPath)
            if bookmarksData == -2:
                return -2
        else:
            bookmarksData = []
            self._dumpJson(bookmarksData, bookmarkPath)
        return bookmarksData

    def addToFavorites(self, shortName, absPath):
        """
        Adds the given project info to the favorites database
        :param shortName: (String) Name of the project
        :param absPath: (String) Absolute path of the project folder
        :return: (List) [Favorites Data]
        """
        logger.debug("Func: addToFavorites")

        # old Name userFavoritesAdd
        bookmarksData = self.loadFavorites()
        bookmarksData.append([shortName, absPath])
        self._dumpJson(bookmarksData, self._pathsDict["bookmarksFile"])
        return bookmarksData

    def removeFromFavorites(self, index):
        """Removes the data from the Favorites database. Accepts index number of the Favorites list"""
        logger.debug("Func: removeFromFavorites")

        # old Name userFavoritesRemove
        bookmarksData = self.loadFavorites()
        del bookmarksData[index]
        self._dumpJson(bookmarksData, self._pathsDict["bookmarksFile"])
        return bookmarksData

    def resolveSaveName(self, nameDict, version):
        nameDict["date"] = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M")
        # get the template defined in tikConventions.json file under Common Folder
        template = "%s_v%s" %(self._nameConventions["fileName"], str(version).zfill(3))

        items = re.findall(r'<(.*?)\>', template)

        for i in items:
            if i in list(nameDict):
                template = template.replace("<%s>" %i, nameDict[i])
        return template

    def loadSoftwareDatabase(self):
        """Returns all softwareDatabase"""
        softwareDB = self._loadJson(self._pathsDict["softwareDatabase"])
        return softwareDB

    def loadManagerDefaults(self):
        """returns the scene manager defaults from the common folder"""
        return self._loadJson(self._pathsDict["sceneManagerDefaults"])

    def loadNameConventions(self):
        if os.path.isfile(self._pathsDict["tikConventions"]):
            nameConventions = self._loadJson(self._pathsDict["tikConventions"])
            # compatibility prior to version 3.0.606
            try: nameConventions["newProjectName"]
            except KeyError:
                nameConventions["newProjectName"] = "<brandName>_<projectName>_<clientName>_<yy><mm><dd>"
                self._dumpJson(nameConventions, self._pathsDict["tikConventions"])
            return nameConventions
        else:
            defaultNameConventions = self._sceneManagerDefaults["defaultTikConvention"]
            # compatibility prior to version 3.0.606
            try: defaultNameConventions["newProjectName"]
            except KeyError:
                defaultNameConventions["newProjectName"] = "<brandName>_<projectName>_<clientName>_<yy><mm><dd>"
            self._dumpJson(defaultNameConventions, self._pathsDict["tikConventions"])
            return defaultNameConventions

    def loadCategories(self, filePath=None, swName=None):
        """Load Categories from file"""
        logger.debug("Func: loadCategories")

        if not swName:
            swName = self.swName

        if not filePath:
            filePath = self._pathsDict["categoriesFile"]

        if os.path.isfile(filePath):
            categoriesData = self._loadJson(filePath)
            if categoriesData == -2:
                return -2
        else:
            categoriesData = self._sceneManagerDefaults["defaultCategories"][swName]
            self._dumpJson(categoriesData, filePath)
        return categoriesData

    def loadSceneInfo(self, asBaseScene=None):
        """Returns scene info of base scene at cursor position"""
        logger.debug("Func: loadSceneInfo")
        if not asBaseScene:
            sceneInfo = self._loadJson(self._baseScenesInCategory[self._currentBaseSceneName])
            if sceneInfo == -2:
                return -2
        else:
            sceneInfo = self._loadJson(self._baseScenesInCategory[asBaseScene])
        return sceneInfo

    def loadUserPrefs(self):
        """Load Last CategoryIndex, SubProject Index, User name and Access mode from file as dictionary"""
        logger.debug("Func: loadUserPrefs")

        if os.path.isfile(self._pathsDict["currentsFile"]):
            settingsData = self._loadJson(self._pathsDict["currentsFile"])
            if settingsData == -2:
                return -2
        else:
            settingsData = {"currentTabIndex": 0, "currentSubIndex": 0, "currentUser": list(self._usersDict)[0],
                            "currentMode": True}
            self._dumpJson(settingsData, self._pathsDict["currentsFile"])
        return settingsData

    def saveUserPrefs(self, settingsData):
        """Save Last CategoryIndex, SubProject Index, User name and Access mode to file as dictionary"""
        logger.debug("Func: saveUserPrefs")
        try:
            self._dumpJson(settingsData, self._pathsDict["currentsFile"])
            msg = ""
            return 0, msg
        except:
            msg = "Cannot save current settings"
            return -1, msg

    def loadSubprojects(self):
        """Loads Subprojects of current project"""
        logger.debug("Func: loadSubprojects")

        if not os.path.isfile(self._pathsDict["subprojectsFile"]):
            data = ["None"]
            self._dumpJson(data, self._pathsDict["subprojectsFile"])
        else:
            data = self._loadJson(self._pathsDict["subprojectsFile"])
            if data == -2:
                return -2
        return data

    def saveSubprojects(self, subprojectsList):
        """Save Subprojects to the file"""
        logger.debug("Func: saveSubprojects")

        self._dumpJson(subprojectsList, self._pathsDict["subprojectsFile"])

    def loadProjects(self):
        """Loads Projects dictionary for each software"""
        logger.debug("Func: loadProjects")

        if not os.path.isfile(self._pathsDict["projectsFile"]):
            return
        else:
            projectsData = self._loadJson(self._pathsDict["projectsFile"])
            if projectsData == -2:
                return -2
        return projectsData

    def saveProjects(self, data):
        """Saves the current project data to the file"""
        logger.debug("Func: saveProjects %s")
        self._dumpJson(data, self._pathsDict["projectsFile"])

    def loadUserSettings(self):
        if os.path.isfile(self._pathsDict["userSettingsFile"]):
            userSettings = self._loadJson(self._pathsDict["userSettingsFile"])
            try: userSettings["extraColumns"] # safety for pre 3.0.701 version
            except KeyError:
                userSettings["extraColumns"] = ["Date"]
                self.saveUserSettings(userSettings)
            if userSettings == -2:
                return -2
        else:
            # self._sceneManagerDefaults = self.loadManagerDefaults()
            userSettings = self._sceneManagerDefaults["defaultUserSettings"]
            self.saveUserSettings(userSettings)
        return userSettings

    def saveUserSettings(self, userSettings):
        """Dumps the data to the database"""
        logger.debug("Func: savePBSettings")
        self._userSettings = userSettings
        self._dumpJson(userSettings, self._pathsDict["userSettingsFile"])
        return

    def loadAlImportSettings(self):
        """Load Asset Library Import Setting options from file in Common Folder"""
        if os.path.isfile(self._pathsDict["alImportSettingsFile"]):
            alImportSettings = self._loadJson(self._pathsDict["alImportSettingsFile"])
            if alImportSettings == -2:
                return -2
        else:
            # self._sceneManagerDefaults = self.loadManagerDefaults()
            alImportSettings = self._sceneManagerDefaults["transferImportSettings"]
            self.saveExportSettings(alImportSettings)
        return alImportSettings

    def saveAlImportSettings(self, alImportSettings):
        """Dumps the data to the database"""
        self._dumpJson(alImportSettings, self._pathsDict["alImportSettingsFile"])
        return

    def loadAlExportSettings(self):
        """Load Asset Library Export Setting options from file in Common Folder"""
        if os.path.isfile(self._pathsDict["alExportSettingsFile"]):
            alExportSettings = self._loadJson(self._pathsDict["alExportSettingsFile"])
            if alExportSettings == -2:
                return -2
        else:
            alExportSettings = self._sceneManagerDefaults["transferExportSettings"]
            self.saveExportSettings(alExportSettings)
        return alExportSettings

    def saveAlExportSettings(self, alExportSettings):
        """Dumps the data to the database"""
        self._dumpJson(alExportSettings, self._pathsDict["alExportSettingsFile"])
        return

    def loadExportSettings(self):
        """Load Export Setting options from file in Common Folder"""

        if os.path.isfile(self._pathsDict["exportSettingsFile"]):
            exportSettings = self._loadJson(self._pathsDict["exportSettingsFile"])
            if exportSettings == -2:
                return -2
        else:
            exportSettings = self._sceneManagerDefaults["transferExportSettings"]
            self.saveExportSettings(exportSettings)
        return exportSettings

    def saveExportSettings(self, exportSettings):
        """Dumps the data to the database"""
        logger.debug("Func: savePBSettings")
        self._dumpJson(exportSettings, self._pathsDict["exportSettingsFile"])
        return

    def loadImportSettings(self):
        """Load Export Setting options from file in Common Folder"""

        if os.path.isfile(self._pathsDict["importSettingsFile"]):
            importSettings = self._loadJson(self._pathsDict["importSettingsFile"])
            if importSettings == -2:
                return -2
        else:
            importSettings = self._sceneManagerDefaults["transferImportSettings"]
            self.saveImportSettings(importSettings)
        return importSettings

    def saveImportSettings(self, importSettings):
        """Dumps the data to the database"""
        logger.debug("Func: savePBSettings")
        self._dumpJson(importSettings, self._pathsDict["importSettingsFile"])
        return

    def loadPBSettings(self, filePath=None):
        """Loads the preview settings data"""
        # TODO // NEEDS to be IMPROVED and compatible with all softwares (Nuke and Houdini)

        if not filePath:
            filePath = self._pathsDict["pbSettingsFile"]

        logger.debug("Func: loadPBSettings")
        if not os.path.isfile(filePath):
            defaultSettings = self._sceneManagerDefaults["defaultPreviewSettings"]
            self._dumpJson(defaultSettings, filePath)
            return defaultSettings
        else:
            pbSettings = self._loadJson(filePath)
            if pbSettings == -2:
                return -2
            return pbSettings

    def savePBSettings(self, pbSettings):
        """Dumps the Preview settings data to the database"""
        logger.debug("Func: savePBSettings")
        # old Name setPBsettings
        self._dumpJson(pbSettings, self._pathsDict["pbSettingsFile"])
        return

    def loadConversionLUT(self):
        logger.debug("Func: loadConversionLUT")
        if not os.path.isfile(self._pathsDict["conversionLUTFile"]):
            defaultLUT = self._sceneManagerDefaults["defaultConversionLUT"]
            self._dumpJson(defaultLUT, self._pathsDict["conversionLUTFile"])
            return defaultLUT
        else:
            conversionLUT = self._loadJson(self._pathsDict["conversionLUTFile"])
            if conversionLUT == -2:
                return -2
            return conversionLUT

    def saveConversionLUT(self, conversionLUT):
        logger.debug("Func: saveConversionLUT")
        self._dumpJson(conversionLUT, self._pathsDict["conversionLUTFile"])
        return

    def checkNewVersion(self):

        url = "http://www.ardakutlu.com/Tik_Manager/versionCheck/versionInfo.json"
        print("DB1tt")
        # response = urllib.urlopen(url)
        response = urlopen(url)
        data = json.loads(response.read())
        majorV_remote, minorV_remote, patch_remote = map(lambda x: int(x), data["CurrentVersion"].split("."))
        versionStr_remote = data["CurrentVersion"]
        downloadPath = data["DownloadPath"]
        whatsNewPath = data["WhatsNew"]

        majorV, minorV, patch = map(lambda x: int(x) ,_version.__version__.split("."))

        if majorV_remote > majorV:
            vMsg = "New major version!\nTik Manager v{0} is now available".format(versionStr_remote)
            return vMsg, downloadPath, whatsNewPath
        else:
            vMsg = "Tik Manager is up to date"
            return vMsg, None, None

        if minorV_remote > minorV:
            vMsg = "Tik Manager v{0} is now available".format(versionStr_remote)
            return vMsg, downloadPath, whatsNewPath
        else:
            vMsg = "Tik Manager is up to date"
            return vMsg, None, None

        if patch_remote > patch:
            vMsg = "Tik Manager v{0} with minor bug fixes and improvements is now available".format(versionStr_remote)
            return vMsg, downloadPath, whatsNewPath
        else:
            vMsg = "Tik Manager is up to date"
            return vMsg, None, None

    def getPlatform(self):
        return platform.system()

    def checkFFMPEG(self):
        platform = self.getPlatform()
        if platform == "Windows":
            ffmpeg = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg.exe")
            if not os.path.isfile(ffmpeg):
                return False
            else:
                return ffmpeg
        else:
            try:
                v = subprocess.call(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return "ffmpeg"
            except OSError:
                return False


    def _convertPreview(self, sourceFile, overwrite=True, deleteAfter=False, crf=None):
        # abort if system is not supported or converter exe is missing
        compatibleVideos = [".avi", ".mov", ".mp4", ".flv", ".webm", ".mkv", ".mp4"]
        compatibleImages = [".tga", ".jpg", ".exr", ".png", ".pic"]

        ffmpeg = self.checkFFMPEG()
        if not ffmpeg:
            self._info("Cannot find ffmpeg")
            return

        # get the conversion lut
        presetLUT = self.loadConversionLUT()

        # if the compression value passed, override the LUT dictionary with that value
        if crf:
            presetLUT["compression"] = "-crf %s" %crf
        # set output file
        base, ext = os.path.splitext(sourceFile)
        outputFile = "%s.mp4" %(base)
        # deal with the existing output
        if os.path.isfile(outputFile):
            if overwrite:
                os.remove(outputFile)
            else:
                self._info("Target path already exists. Aborting")
                return False

        if ext in compatibleVideos:
            flagStart = ["%s" %ffmpeg, "-i", sourceFile]

        elif ext in compatibleImages:
            filename, startFrame, sourceSequence = self._formatImageSeq(sourceFile)
            flagStart = ["%s" %ffmpeg, '-start_number', str(startFrame), '-i', filename]
            presetLUT["audioCodec"] = ""

        fullFlagList = flagStart + \
                       presetLUT["videoCodec"].split() + \
                       presetLUT["compression"].split() + \
                       presetLUT["audioCodec"].split() + \
                       presetLUT["resolution"].split() + \
                       presetLUT["foolproof"].split() + \
                       [str(outputFile)]

        if self.currentPlatform == "Windows":
            subprocess.check_call(fullFlagList, shell=False)
        else:
            subprocess.check_call(fullFlagList)
        if deleteAfter:
            if ext in compatibleImages:
                rootPath = os.path.split(os.path.normpath(sourceFile))[0]
                for x in sourceSequence:
                    imageP = os.path.join(rootPath, str(x))
                    os.remove(imageP)
            else:
                os.remove(sourceFile)
        return outputFile

    def _formatImageSeq(self, filePath):
        """
        Checks the path if it belongs to a sequence and formats it ready to be passes to FFMPEG
        :param filePath: a single member of a sequence
        :return: (String) Formatted path, (int) Starting frame
        """
        sourceDir, sourceFile = os.path.split(filePath)

        seqList = pyseq.get_sequences(sourceDir)
        theSeq = self._findItem(sourceFile, seqList)
        if not theSeq:
            msg = "Cannot get the sequence list."
            raise Exception(msg)

        formattedName = "{0}{1}{2}".format(theSeq.head(), theSeq._get_padding(), theSeq.tail())
        formattedPath = os.path.normpath(os.path.join(sourceDir, formattedName))
        return formattedPath, theSeq.start(), theSeq

    def _findItem(self, itemPath, seqlist):
        """finds out which sequence the given file belongs to among the given sequence list"""
        for x in seqlist:
            if x.contains(itemPath):
                return x

    def _question(self, msg, *args, **kwargs):
        """Yes/No question terminal"""
        yes = {'yes', 'y', 'ye', ''}
        no = {'no', 'n'}

        msg = "%s [y/n]" %msg
        choice = raw_input(msg).lower()
        if choice in yes:
            return True
        elif choice in no:
            return False
        else:
            print("Please respond with 'yes' or 'no'")
            self._question(msg)

    def _info(self, msg):
        """Information"""
        print(msg)

    def _inputDir(self):
        """Input directory terminal"""
        inputDir = os.path.normpath(raw_input("Enter Path for the Common Directory:"))
        normInputDir = os.path.normpath(inputDir)
        if os.path.isdir(normInputDir):
            return normInputDir
        else:
            return False

    def _copytree(self, src, dst, symlinks=False, ignore=None):
        names = os.listdir(src)
        if ignore is not None:
            ignored_names = ignore(src, names)
        else:
            ignored_names = set()

        if not os.path.isdir(dst):  # This one line does the trick
            os.makedirs(dst)
        errors = []
        for name in names:
            if name in ignored_names:
                continue
            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)
            try:
                if symlinks and os.path.islink(srcname):
                    linkto = os.readlink(srcname)
                    os.symlink(linkto, dstname)
                elif os.path.isdir(srcname):
                    self._copytree(srcname, dstname, symlinks, ignore)
                else:
                    # Will raise a SpecialFileError for unsupported file types
                    shutil.copy2(srcname, dstname)
            # catch the Error from the recursive copytree so that we can
            # continue with other files
            ##############

            except shutil.Error as err:
                errors.extend(err.args[0])
            except EnvironmentError as why:
                errors.append((srcname, dstname, str(why)))
        try:
            shutil.copystat(src, dst)
        except OSError as why:
            if WindowsError is not None and isinstance(why, WindowsError):
                # Copying file access times may fail on Windows
                pass
            else:
                errors.extend((src, dst, str(why)))
        if errors:
            raise shutil.Error(errors)

        ###############################











