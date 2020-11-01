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

import os
os.environ["FORCE_QT5"]="0"

from tik_manager.ui.sm_ui import MainUI as baseUI
from tik_manager.core.sm_root import RootManager
from tik_manager.dcc.nuke.core_nuke import NukeCoreFunctions


import tik_manager.core._version as _version
import shutil
import nuke
import datetime
import socket
import logging

from tik_manager.ui.Qt import QtWidgets, QtCore, QtGui

## DO NOT REMOVE THIS:
## DO NOT REMOVE THIS:

__author__ = "Arda Kutlu"
__copyright__ = "Copyright 2018, Scene Manager for Maya Project"
__credits__ = []
__license__ = "GPL"
__maintainer__ = "Arda Kutlu"
__email__ = "ardakutlu@gmail.com"
__status__ = "Development"

SM_Version = "Scene Manager Nuke v%s" % _version.__version__

logging.basicConfig()
logger = logging.getLogger('smNuke')
logger.setLevel(logging.WARNING)




class NukeManager(RootManager, NukeCoreFunctions):
    def __init__(self):
        super(NukeManager, self).__init__()
        self.swName = "Nuke"
        self.init_paths(self.swName)
        self.init_database()


    def getSceneFile(self):
        """Overriden function"""
        logger.debug("Func: getSceneFile")
        return self._getSceneFile()


    def saveBaseScene(self, categoryName, baseName, subProjectIndex=0, makeReference=True, versionNotes="", sceneFormat="nk", *args, **kwargs):
        """
        Saves the scene with formatted name and creates a json file for the scene
        Args:
            category: (String) Category if the scene. Valid categories are 'Model', 'Animation', 'Rig', 'Shading', 'Other'
            baseName: (String) Base name of the scene. Eg. 'Shot01', 'CharacterA', 'BookRig' etc...
            subProject: (Integer) The scene will be saved under the sub-project according to the given integer value. The 'self.subProjectList' will be
                searched with that integer.
            makeReference: (Boolean) If set True, a copy of the scene will be saved as forReference
            versionNotes: (String) This string will be stored in the json file as version notes.
            *args:
            **kwargs:

        Returns: Scene DB Dictionary

        """
        logger.debug("Func: saveBaseScene")

        now = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M")
        completeNote = "[%s] on %s\n%s\n" % (self.currentUser, now, versionNotes)

        # Check if the base name is unique
        scenesToCheck = self.scanBaseScenes(categoryAs=categoryName, subProjectAs=subProjectIndex)
        for key in scenesToCheck.keys():
            if baseName.lower() == key.lower():
                msg = ("Base Scene Name is not unique!\nABORTING")
                self._exception(360, msg)
                return -1, msg

        projectPath = self.projectDir
        databaseDir = self._pathsDict["databaseDir"]
        scenesPath = self._pathsDict["scenesDir"]
        categoryPath = os.path.normpath(os.path.join(scenesPath, categoryName))
        self._folderCheck(categoryPath)

        ## if its going to be saved as a subproject
        if not subProjectIndex == 0:
            subProjectPath = os.path.normpath(os.path.join(categoryPath, self._subProjectsList[subProjectIndex]))
            self._folderCheck(subProjectPath)
            shotPath = os.path.normpath(os.path.join(subProjectPath, baseName))
            self._folderCheck(shotPath)

            jsonCategoryPath = os.path.normpath(os.path.join(databaseDir, categoryName))
            self._folderCheck(jsonCategoryPath)
            jsonCategorySubPath = os.path.normpath(os.path.join(jsonCategoryPath, self._subProjectsList[subProjectIndex]))
            self._folderCheck(jsonCategorySubPath)
            jsonFile = os.path.join(jsonCategorySubPath, "{}.json".format(baseName))

        else:
            shotPath = os.path.normpath(os.path.join(categoryPath, baseName))
            self._folderCheck(shotPath)

            jsonCategoryPath = os.path.normpath(os.path.join(databaseDir, categoryName))
            self._folderCheck(jsonCategoryPath)
            jsonFile = os.path.join(jsonCategoryPath, "{}.json".format(baseName))


        version = 1
        ## Naming Dictionary
        nameDict = {
            "baseName": baseName,
            "categoryName": categoryName,
            "userInitials": self._usersDict[self.currentUser],
            "subproject": self.subProject,
            "date": now
        }
        sceneName = self.resolveSaveName(nameDict, version)

        sceneFile = os.path.join(shotPath, "{0}.{1}".format(sceneName, sceneFormat))
        ## relativity update
        relSceneFile = os.path.relpath(sceneFile, start=projectPath)
        self._saveAs(sceneFile)

        thumbPath = self.createThumbnail(dbPath=jsonFile, versionInt=version)

        jsonInfo = {}

        if makeReference:
            referenceName = "{0}_{1}_forReference".format(baseName, categoryName)
            referenceFile = os.path.join(shotPath, "{0}.{1}".format(referenceName, sceneFormat))
            ## relativity update
            relReferenceFile = os.path.relpath(referenceFile, start=projectPath)
            shutil.copyfile(sceneFile, referenceFile)
            jsonInfo["ReferenceFile"] = relReferenceFile
            jsonInfo["ReferencedVersion"] = version
        else:
            jsonInfo["ReferenceFile"] = None
            jsonInfo["ReferencedVersion"] = None

        jsonInfo["ID"] = "SmNukeV02_sceneFile"
        jsonInfo["NukeVersion"] = self._getVersion()
        # jsonInfo["NukeVersion"] = "test"
        jsonInfo["Name"] = baseName
        jsonInfo["Path"] = os.path.relpath(shotPath, start=projectPath)
        jsonInfo["Category"] = categoryName
        jsonInfo["Creator"] = self.currentUser
        jsonInfo["CreatorHost"] = (socket.gethostname())
        jsonInfo["Versions"] = [ # PATH => Notes => User Initials => Machine ID => Playblast => Thumbnail
            {"RelativePath": relSceneFile,
             "Note": completeNote,
             "User": self._usersDict[self.currentUser],
             "Workstation": socket.gethostname(),
             "Preview": {},
             "Thumb": thumbPath,
             "Ranges": self._getTimelineRanges()
             }
        ]

        jsonInfo["SubProject"] = self._subProjectsList[subProjectIndex]
        self._dumpJson(jsonInfo, jsonFile)
        self.progressLogger("save", sceneFile)
        return [0, ""]

    def saveSimple(self):
        """Save the currently open file"""
        logger.debug("Func: saveSimple")
        self._save()
        self.progressLogger("save", self.getSceneFile())

    def saveVersion(self, makeReference=True, versionNotes="", sceneFormat="mb", insertTo=None, *args, **kwargs):
        """
        Saves a version for the predefined scene. The scene json file must be present at the /data/[Category] folder.
        Args:
            userName: (String) Predefined user who initiates the process
            makeReference: (Boolean) If set True, make a copy of the forReference file. There can be only one 'forReference' file for each scene
            versionNotes: (String) This string will be hold in the json file as well. Notes about the changes in the version.
            *args:
            **kwargs:

        Returns: Scene DB Dictionary

        """
        logger.debug("Func: saveVersion")



        now = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M")
        completeNote = "[%s] on %s\n%s\n" % (self.currentUser, now, versionNotes)

        currentSceneName = self.getSceneFile()
        if not currentSceneName:
            msg = "This is not a base scene (Untitled)"
            self._exception(360, msg)
            return -1, msg

        if not insertTo:
            sceneInfo = self.getOpenSceneInfo()
            if not sceneInfo:
                msg = "This is not a base scene (Json file cannot be found)"
                self._exception(360, msg)
                return -1, msg
        else:
            sceneInfo = {
                    "jsonFile":self.currentDatabasePath,
                    "projectPath":self._pathsDict["projectDir"],
                    "subProject":self.subProject,
                    "category":self.currentTabName,
                    "shotName":self.currentBaseSceneName,
                    "version":len(self.getVersions()),
                    "previewPath":self.currentPreviewPath,
                    }
            # ingesting overrides make reference
            makeReference = False

        # sceneInfo = self.getOpenSceneInfo()

        if sceneInfo: ## getCurrentJson returns None if the resolved json path is missing
            jsonFile = sceneInfo["jsonFile"]
            jsonInfo = self._loadJson(jsonFile)

            currentVersion = len(jsonInfo["Versions"]) + 1
            ## Naming Dictionary
            nameDict = {
                "baseName": jsonInfo["Name"],
                "categoryName": jsonInfo["Category"],
                "userInitials": self._usersDict[self.currentUser],
                "subproject": self.subProject,
                "date": now
            }
            sceneName = self.resolveSaveName(nameDict, currentVersion)

            #                                       str(currentVersion).zfill(3))
            relSceneFile = os.path.join(jsonInfo["Path"], "{0}.{1}".format(sceneName, sceneFormat))

            sceneFile = os.path.join(sceneInfo["projectPath"], relSceneFile)

            self._saveAs(sceneFile)

            thumbPath = self.createThumbnail(dbPath=jsonFile, versionInt=currentVersion)

            jsonInfo["Versions"].append(
                # PATH => Notes => User Initials => Machine ID => Playblast => Thumbnail
                {"RelativePath": relSceneFile,
                 "Note": completeNote,
                 "User": self._usersDict[self.currentUser],
                 "Workstation": socket.gethostname(),
                 "Preview": {},
                 "Thumb": thumbPath,
                 "Ranges": self._getTimelineRanges()
                 }
                )

            if makeReference:
                referenceName = "{0}_{1}_forReference".format(jsonInfo["Name"], jsonInfo["Category"])
                relReferenceFile = os.path.join(jsonInfo["Path"], "{0}.{1}".format(referenceName, sceneFormat))
                referenceFile = os.path.join(sceneInfo["projectPath"], relReferenceFile)

                shutil.copyfile(sceneFile, referenceFile)
                jsonInfo["ReferenceFile"] = relReferenceFile
                jsonInfo["ReferencedVersion"] = currentVersion
            self._dumpJson(jsonInfo, jsonFile)
        else:
            msg = "This is not a base scene (Json file cannot be found)"
            self._exception(360, msg)
            return -1, msg
        self.progressLogger("save", sceneFile)
        return jsonInfo

    def loadBaseScene(self, force=False):
        """Loads the scene at cursor position"""
        logger.debug("Func: loadBaseScene")
        relSceneFile = self._currentSceneInfo["Versions"][self._currentVersionIndex-1]["RelativePath"].replace("\\", "/")
        absSceneFile = os.path.join(self.projectDir, relSceneFile)
        if os.path.isfile(absSceneFile):
            self._new(force=True)
            self._load(absSceneFile)
            self.progressLogger("load", absSceneFile)
            return 0
        else:
            msg = "File in Scene Manager database doesnt exist"
            self._exception(201, msg)
            return -1, msg
    #
    def importBaseScene(self):
        """Imports the scene at cursor position"""
        logger.debug("Func: importBaseScene")
        relSceneFile = self._currentSceneInfo["Versions"][self._currentVersionIndex-1]["RelativePath"].replace("\\", "/")
        absSceneFile = os.path.join(self.projectDir, relSceneFile)
        if os.path.isfile(absSceneFile):
            self._import(absSceneFile)
            return 0
        else:
            msg = "File in Scene Manager database doesnt exist"
            self._exception(210, msg)
            return -1, msg


    def createThumbnail(self, useCursorPosition=False, dbPath = None, versionInt = None):
        """
        Creates the thumbnail file.
        :param databaseDir: (String) If defined, this folder will be used to store the created database.
        :param version: (integer) if defined this version number will be used instead currently open scene version.
        :return: (String) Relative path of the thumbnail file
        """
        logger.debug("Func: createThumbnail")
        projectPath = self.projectDir
        if useCursorPosition:
            versionInt = self.currentVersionIndex
            dbPath = self.currentDatabasePath
        else:
            if not dbPath or not versionInt:
                msg = "Both dbPath and version must be defined if useCursorPosition=False"
                raise Exception ([360, msg])

        versionStr = "v%s" % (str(versionInt).zfill(3))
        dbDir, shotNameWithExt = os.path.split(dbPath)
        shotName = os.path.splitext(shotNameWithExt)[0]

        thumbPath = "{0}_{1}_thumb.jpg".format(os.path.join(dbDir, shotName), versionStr)
        relThumbPath = os.path.relpath(thumbPath, projectPath)

        # create a thumbnail
        thumbDir = os.path.split(thumbPath)[0]
        try:
            #############################################
            # get the node attached to the current viewer
            activeNode = nuke.activeViewer().node().input(0)

            # create reformat node
            reformatNode = nuke.createNode("Reformat")
            reformatNode["type"].setValue(1)
            reformatNode["box_fixed"].setValue(1)
            reformatNode["box_width"].setValue(221)
            reformatNode["box_height"].setValue(124)
            reformatNode["black_outside"].setValue(1)
            reformatNode.setInput(0, activeNode)

            # create a write node
            writeNode = nuke.createNode("Write")
            writeNode.setName("tik_tempWrite")
            writeNode['file'].setValue(thumbPath.replace("\\", "/"))
            writeNode["use_limit"].setValue(True)
            frame = self._getCurrentFrame()
            writeNode['first'].setValue(frame)
            writeNode['last'].setValue(frame)
            # writeNode['_jpeg_quality'].setValue(1)
            # writeNode['_jpeg_sub_sampling'].setValue(2)

            # execute & cleanup
            nuke.execute(writeNode, frame, frame)
            nuke.delete(writeNode)
            nuke.delete(reformatNode)
            ####################################################

        except:
            # pm.warning("something went wrong with thumbnail. Skipping thumbnail")
            nuke.warning("something went wrong with thumbnail. Skipping thumbnail")
            return ""
        # return thumbPath
        return relThumbPath



        #############################################
        # get the node attached to the current viewer
        activeNode = nuke.activeViewer().node().input(0)

        # create a write node
        writeNode = nuke.createNode("Write")
        writeNode.setName("tik_tempWrite")
        writeNode['file'].setValue("TEST.jpg")
        r = nuke.createNode("Reformat")

        # create reformat node
        reformatNode = nuke.createNode("Reformat")
        reformatNode["type"].setValue(1)
        reformatNode["box_width"].setValue(123)
        reformatNode["box_height"].setValue(123)
        reformatNode["black_outside"].setValue(1)
        reformatNode["box_fixed"].setValue(1)

        # make Connections
        writeNode.setInput(0, reformatNode)
        reformatNode.setInput(0, activeNode)
        ####################################################

    def compareVersions(self):
        """Compares the versions of current session and database version at cursor position"""
        logger.debug("Func: compareVersions")

        nukeVersion = self._getVersion()
        print(nukeVersion)
        cMajorV = nukeVersion[0]
        cMinorV = nukeVersion[1]
        currentVersion = float("{0}.{1}".format(cMajorV, cMinorV))

        dbMajorV = self._currentSceneInfo["NukeVersion"][0]
        dbMinorV = self._currentSceneInfo["NukeVersion"][1]
        databaseVersion = float("{0}.{1}".format(dbMajorV, dbMinorV))

        messageList = []


        if currentVersion == databaseVersion:
            pass

        if currentVersion < databaseVersion: # version compare
            message = "Base Scene is created with a HIGHER Nuke version ({0}). Are you sure you want to continue?".format(databaseVersion)
            messageList.append(message)

        if currentVersion > databaseVersion:
            message = "Base Scene is created with a LOWER Nuke version ({0}). Are you sure you want to continue?".format(databaseVersion)
            messageList.append(message)

        message=""
        for x in messageList:
            message = message + "\n" + str(x)

        if messageList == []:
            return 0, message
        else:
            return -1, message

    def isSceneModified(self):
        """Checks the currently open scene saved or not"""
        logger.debug("Func: isSceneModified")
        self._isSceneModified()
        return nuke.modified()


    def preSaveChecklist(self):
        """Checks the scene for inconsistencies"""
        checklist = []

        fpsValue_setting = float(self.getFPS())
        fpsValue_current = float(nuke.root().fps())

        if fpsValue_setting is not fpsValue_current:
            msg = "FPS values are not matching with the project settings.\n Project FPS => {0}\n scene FPS => {1}\nDo you want to continue?".format(fpsValue_setting, fpsValue_current)
            checklist.append(msg)

        return checklist

    def _exception(self, code, msg):
        """Overriden Function"""
        # cmds.confirmDialog(title=self.errorCodeDict[code], message=msg, button=['Ok'])
        nuke.message(msg)
        if (200 >= code < 210):
            raise Exception(code, msg)

    def _question(self, msg):
        """OVERRIDEN METHOD"""
        state = nuke.ask(msg)
        return state

    def _info(self, msg):
        """OVERRIDEN METHOD"""
        nuke.message(msg)

    def _inputDir(self):
        """OVERRIDEN METHOD"""
        # Qt File dialog is preferred because it is faster
        inputDir = QtWidgets.QFileDialog.getExistingDirectory()
        return os.path.normpath(inputDir)

class MainUI(baseUI):
    def __init__(self, callback=None):
        super(MainUI, self).__init__()

        self.manager = NukeManager()
        problem, msg = self.manager._checkRequirements()
        if problem:
            self.close()
            self.deleteLater()
        self.buildUI()
        self.initMainUI(newborn=True)
        self.modify()

    def modify(self):
        # make sure load mode is checked and hidden
        self.load_radioButton.setChecked(True)
        self.load_radioButton.setVisible(False)
        self.reference_radioButton.setChecked(False)
        self.reference_radioButton.setVisible(False)
        self.makeReference_pushButton.setVisible(False)

        self.showPreview_pushButton.setVisible(False)
        self.createPB.setVisible(False)
        self.assetLibrary_mi.setVisible(False)

        # idk why this became necessary for nuke..
        self.category_tabWidget.setMaximumSize(QtCore.QSize(16777215, 30))

        self.mIconPixmap = QtGui.QPixmap(":/icons/CSS/rc/iconNuke.png")
        self.managerIcon_label.setPixmap(self.mIconPixmap)