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

from tik_manager.ui.SmUIRoot import MainUI as baseUI
from tik_manager.core.sm_root import RootManager
from tik_manager.dcc.houdini.core_houdini import HoudiniCoreFunctions


import tik_manager._version as _version
import shutil

import datetime
import socket
import logging
import hou
import toolutils

import subprocess
import platform

from tik_manager.ui.Qt import QtWidgets, QtCore, QtGui


__author__ = "Arda Kutlu"
__copyright__ = "Copyright 2018, Scene Manager for Maya Project"
__credits__ = []
__version__ = _version.__version__
__license__ = "GPL"
__maintainer__ = "Arda Kutlu"
__email__ = "ardakutlu@gmail.com"
__status__ = "Development"

SM_Version = "Scene Manager Houdini v%s" %_version.__version__

logging.basicConfig()
logger = logging.getLogger('smMaya')
logger.setLevel(logging.WARNING)



class HoudiniManager(RootManager, HoudiniCoreFunctions):
    def __init__(self):
        super(HoudiniManager, self).__init__()

        self.swName = "Houdini"
        self.init_paths(self.swName)
        self.init_database()
        if self.currentPlatform == "Windows":
            self._setEnvVariable("HOUDINI_ACCESS_METHOD", "1")
        self.setProject(self.projectDir)

    def getSceneFile(self):
        """Overriden function"""
        return self._getSceneFile()

    def setProject(self, path):
        """Sets the project"""
        logger.debug("Func: setProject")
        projectsDict = self.loadProjects()
        if not projectsDict:
            projectsDict = {self.swName: path}
        else:
            projectsDict[self.swName] = path
        self.saveProjects(projectsDict)
        self.projectDir = path
        self._setProject(path)

    def saveBaseScene(self, categoryName, baseName, subProjectIndex=0, makeReference=False, versionNotes="", sceneFormat="hip", *args, **kwargs):
        """
        Saves the scene with formatted name and creates a json file for the scene
        Args:
            category: (String) Category if the scene. Valid categories are 'Model', 'Animation', 'Rig', 'Shading', 'Other'
            userName: (String) Predefined user who initiates the process
            baseName: (String) Base name of the scene. Eg. 'Shot01', 'CharacterA', 'BookRig' etc...
            subProject: (Integer) The scene will be saved under the sub-project according to the given integer value. The 'self.subProjectList' will be
                searched with that integer.
            makeReference: (Boolean) If set True, a copy of the scene will be saved as forReference
            versionNotes: (String) This string will be stored in the json file as version notes.
            *args:
            **kwargs:

        Returns: Scene DB Dictionary

        """
        if hou.isApprentice():
            sceneFormat="hipnc"
        logger.debug("Func: saveBaseScene")

        now = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M")
        completeNote = "[%s] on %s\n%s\n" % (self.currentUser, now, versionNotes)

        # Check if the base name is unique
        scenesToCheck = self.scanBaseScenes(categoryAs = categoryName, subProjectAs = subProjectIndex)
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

        # sceneName = "{0}_{1}_{2}_v{3}".format(baseName, categoryName, self._usersDict[self.currentUser], str(version).zfill(3))
        absSceneFile = os.path.join(shotPath, "{0}.{1}".format(sceneName, sceneFormat))
        # houdini opens the scene with "\" paths but cannot resolve some inside paths. So convert them to "/"
        absSceneFile = absSceneFile.replace('\\', '/')
        ## relativity update
        relSceneFile = os.path.relpath(absSceneFile, start=projectPath)
        # killTurtle()

        # hou.hipFile.save(file_name=absSceneFile)
        self._saveAs(absSceneFile)

        thumbPath = self.createThumbnail(dbPath=jsonFile, versionInt=version)

        jsonInfo = {}

        if makeReference:
            # TODO // Find an elegant solution and add MA compatibility. Can be merged with makeReference function in derived class
            referenceName = "{0}_{1}_forReference".format(baseName, categoryName)
            referenceFile = os.path.join(shotPath, "{0}.{1}".format(referenceName, sceneFormat))
            ## relativity update
            relReferenceFile = os.path.relpath(referenceFile, start=projectPath)
            shutil.copyfile(absSceneFile, referenceFile)
            jsonInfo["ReferenceFile"] = relReferenceFile
            jsonInfo["ReferencedVersion"] = version
        else:
            jsonInfo["ReferenceFile"] = None
            jsonInfo["ReferencedVersion"] = None

        jsonInfo["ID"] = "SmHoudiniV02_sceneFile"
        jsonInfo["HoudiniVersion"] = [self._getVersion(), hou.isApprentice()]
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
        # return jsonInfo
        self.progressLogger("save", absSceneFile)
        return [0, ""]

    def saveVersion(self, makeReference=False, versionNotes="", sceneFormat="hip", insertTo=None, *args, **kwargs):
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

        if hou.isApprentice():
            sceneFormat="hipnc"

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

            # sceneName = "{0}_{1}_{2}_v{3}".format(jsonInfo["Name"], jsonInfo["Category"], self._usersDict[self.currentUser],
            #                                       str(currentVersion).zfill(3))
            relSceneFile = os.path.join(jsonInfo["Path"], "{0}.{1}".format(sceneName, sceneFormat))

            absSceneFile = os.path.join(sceneInfo["projectPath"], relSceneFile)
            # print "absSceneFile", absSceneFile
            # houdini opens the scene with "\" paths but cannot resolve some inside paths. So convert them to "/"
            absSceneFile = absSceneFile.replace('\\', '/')

            # killTurtle()
            # hou.hipFile.save(file_name=absSceneFile)
            self._saveAs(absSceneFile)

            thumbPath = self.createThumbnail(dbPath=jsonFile, versionInt=currentVersion)


            # thumbPath = ""

            jsonInfo["Versions"].append(
                # PATH => Notes => User Initials => Machine ID => Playblast => Thumbnail
                # [relSceneFile, completeNote, self._usersDict[self.currentUser], (socket.gethostname()), {}, thumbPath])
            # TODO : ref => Dict
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

                shutil.copyfile(absSceneFile, referenceFile)
                jsonInfo["ReferenceFile"] = relReferenceFile
                jsonInfo["ReferencedVersion"] = currentVersion
            self._dumpJson(jsonInfo, jsonFile)
        else:
            msg = "This is not a base scene (Json file cannot be found)"
            return -1, msg
        self.progressLogger("save", absSceneFile)
        return jsonInfo


    def createPreview(self, *args, **kwargs):
        """Creates a Playblast preview from currently open scene"""
        logger.debug("Func: createPreview")



        #
        pbSettings = self.loadPBSettings()
        #
        extension = "jpg"

        openSceneInfo = self.getOpenSceneInfo()
        if not openSceneInfo:
            msg = "This is not a base scene. Scene must be saved as a base scene before playblasting."
            self._exception(360, msg)
            return

        selection = self._getSelection()
        hou.clearAllSelected()
        jsonInfo = self._loadJson(openSceneInfo["jsonFile"])
        #

        scene_view = toolutils.sceneViewer()
        viewport = scene_view.curViewport()
        cam = viewport.camera()
        if cam:
            currentCam = cam.name()
        else:
            currentCam = 'persp'

        flip_options = scene_view.flipbookSettings().stash()



        versionName = self.getSceneFile()
        relVersionName = os.path.relpath(versionName, start=openSceneInfo["projectPath"])
        playBlastDir = os.path.join(openSceneInfo["previewPath"], openSceneInfo["version"])
        self._folderCheck(playBlastDir)
        playBlastFile = os.path.join(playBlastDir, "{0}_{1}_PB_$F4.{2}".format(self.niceName(versionName), currentCam, extension))
        # relPlayBlastFile = os.path.relpath(playBlastFile, start=openSceneInfo["projectPath"])
        #
        if os.path.isfile(playBlastFile):
            try:
                os.remove(playBlastFile)
            except WindowsError:
                msg = "The file is open somewhere else"
                self._exception(202, msg)
                return

        flip_options.output(playBlastFile)

        ranges = self._getTimelineRanges()
        flip_options.frameRange((ranges[1], ranges[2]))
        flip_options.outputToMPlay(not pbSettings["ConvertMP4"])
        flip_options.useResolution(True)
        flip_options.resolution((pbSettings["Resolution"][0], pbSettings["Resolution"][1]))
        scene_view.flipbook(viewport, flip_options)

        if pbSettings["ConvertMP4"]:
            nonVarPBfile = playBlastFile.replace("_$F4", "_0001")
            convertedFile = self._convertPreview(nonVarPBfile, overwrite=True, deleteAfter=True, crf=pbSettings["CrfValue"])
            relPlayBlastFile = os.path.relpath(convertedFile, start=openSceneInfo["projectPath"])
            os.startfile(convertedFile)
        else:
            relPlayBlastFile = os.path.relpath(playBlastFile, start=openSceneInfo["projectPath"])


        ## find this version in the json data
        for version in jsonInfo["Versions"]:
            if relVersionName == version["RelativePath"]:
                # replace the houdini variable with first frame
                nonVarPBfile = relPlayBlastFile.replace("_$F4", "_0001")
                # version["Preview"][currentCam] = nonVarPBfile
                version["Preview"][currentCam] = relPlayBlastFile

        self._dumpJson(jsonInfo, openSceneInfo["jsonFile"])
        # return 0, ""


    def playPreview(self, camera):
        """OVERRIDEN - Runs the playblast at cursor position"""

        absPath = os.path.join(self.projectDir, self._currentPreviewsDict[camera])

        if self.currentPlatform == "Windows":
            ext = os.path.splitext(absPath)[1]
            if ext == ".mp4":
                os.startfile(absPath)
                return
            try:
                subprocess.check_call(["mplay", absPath], shell=True)
                # subprocess.check_call(["mplay", "-viewer", absPath], shell=True)
            except WindowsError:
                return -1, ["Cannot Find Playblast", "Playblast File is missing", "Do you want to remove it from the Database?"]
        # TODO something to play the file in linux
        return

    def loadBaseScene(self, force=False):
        """Loads the scene at cursor position"""
        logger.debug("Func: loadBaseScene")
        # TODO : ref => Dict
        relSceneFile = self._currentSceneInfo["Versions"][self._currentVersionIndex-1]["RelativePath"]
        absSceneFile = os.path.join(self.projectDir, relSceneFile)
        if os.path.isfile(absSceneFile):
            # houdini opens the scene with "\" paths but cannot resolve some inside paths. So convert them to "/"
            absSceneFile = absSceneFile.replace('\\', '/')
            # hou.hipFile.load(absSceneFile, suppress_save_prompt=force, ignore_load_warnings=False)
            self._load(absSceneFile, force=force)
            self.progressLogger("load", absSceneFile)
            return 0
        else:
            msg = "File in Scene Manager database doesnt exist"
            # cmds.error(msg)
            return -1, msg

    def importBaseScene(self):
        """Imports the scene at cursor position"""
        logger.debug("Func: importBaseScene")
        # TODO : ref => Dict
        relSceneFile = self._currentSceneInfo["Versions"][self._currentVersionIndex-1]["RelativePath"]
        absSceneFile = os.path.join(self.projectDir, relSceneFile)
        if os.path.isfile(absSceneFile):
            absSceneFile = absSceneFile.replace('\\', '/')
            self._import(absSceneFile)
            return 0
        else:
            msg = "File in Scene Manager database doesnt exist"
            return -1, msg

    def referenceBaseScene(self):
        """Not implemented for Houdini"""
        logger.debug("Func: referenceBaseScene")


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

        # create a thumbnail using playblast
        thumbDir = os.path.split(thumbPath)[0]
        if os.path.exists(thumbDir):

            # frame = hou.frame()
            frame = self._getCurrentFrame()
            cur_desktop = hou.ui.curDesktop()
            scene = cur_desktop.paneTabOfType(hou.paneTabType.SceneViewer)
            flip_options = scene.flipbookSettings().stash()
            flip_options.frameRange((frame, frame))
            flip_options.outputToMPlay(False)
            flip_options.output(thumbPath)
            flip_options.useResolution(True)
            flip_options.resolution((221, 124))
            scene.flipbook(scene.curViewport(), flip_options)

        else:
            print ("something went wrong with thumbnail. Skipping thumbnail")
            return ""
        return relThumbPath

    def replaceThumbnail(self, filePath=None ):
        """
        Replaces the thumbnail with given file or current view
        :param filePath: (String)  if a filePath is defined, this image (.jpg or .gif) will be used as thumbnail
        :return: None
        """
        if not filePath:
            filePath = self.createThumbnail(useCursorPosition=True)

        self._currentSceneInfo["Versions"][self.currentVersionIndex-1]["Thumb"]=filePath
        self._dumpJson(self._currentSceneInfo, self.currentDatabasePath)

    def compareVersions(self):

        # // TODO : Find a BETTER way to compare versions.
        # // TODO : You may question each individual scen file for version insteas of base scene database

        """Compares the versions of current session and database version at cursor position"""
        logger.debug("Func: compareVersions")

        # version serialization:
        vTup = self._getVersion()
        vIsApprentice = hou.isApprentice()
        currentVersion = float("%s.%s%s" % (vTup[0], vTup[1], vTup[2]))

        dbVersionAsTuple = self._currentSceneInfo["HoudiniVersion"][0]
        dbIsApprentice = self._currentSceneInfo["HoudiniVersion"][1]
        baseSceneVersion = float("%s.%s%s" % (dbVersionAsTuple[0], dbVersionAsTuple[1], dbVersionAsTuple[2]))

        messageList = []

        if vIsApprentice and not dbIsApprentice:
            msg = "Base Scene Created with Commercial License. Current Houdini session is Apprentice. Are you sure you want to continue?"
            messageList.append(msg)

        if not vIsApprentice and dbIsApprentice:
            msg = "Base Scene Created with Apprentice License. Current Houdini session is Commercial. Are you sure you want to continue?"
            messageList.append(msg)

        if currentVersion == baseSceneVersion:
            pass

        if currentVersion < baseSceneVersion: # version compare
            message = "Base Scene is created with a HIGHER Houdini version ({0}). Are you sure you want to continue?".format(baseSceneVersion)
            messageList.append(message)

        if currentVersion > baseSceneVersion:
            message = "Base Scene is created with a LOWER Houdini version ({0}). Are you sure you want to continue?".format(baseSceneVersion)
            messageList.append(message)

        # old or corrupted databasek       return 0, ""  # skip
        message=""
        for x in messageList:
            message = message + "\n" + str(x)

        if messageList == []:
            return 0, message
        else:
            return -1, message


    def isSceneModified(self):
        """Checks the currently open scene saved or not"""
        return self._isSceneModified()


    def saveSimple(self):
        """Save the currently open file"""
        logger.debug("Func: saveSimple")
        self._save()
        self.progressLogger("save", self.getSceneFile())

    def getFormatsAndCodecs(self):
        """Returns the codecs which can be used in current workstation"""
        pass

    def preSaveChecklist(self):
        """Checks the scene for inconsistencies"""
        checklist = []

        fpsValue_setting = self.getFPS()
        fpsValue_current = int(hou.fps())
        if int(fpsValue_setting) is not fpsValue_current:
            msg = "FPS values are not matching with the project settings.\n Project FPS => {0}\n scene FPS => {1}\nDo you want to continue?".format(fpsValue_setting, fpsValue_current)
            checklist.append(msg)

        return checklist

    def _exception(self, code, msg):
        """Overriden Function"""

        hou.ui.displayMessage(msg, title=self.errorCodeDict[code])
        if (200 >= code < 210):
            raise Exception(code, msg)

    def _question(self, msg):
        """OVERRIDEN METHOD"""
        state = hou.ui.displayConfirmation(msg, title='Manager Question')
        return state

    def _info(self, msg):
        """OVERRIDEN METHOD"""
        hou.ui.displayMessage(msg)

    def _inputDir(self):
        """OVERRIDEN METHOD"""
        # Qt File dialog is preferred because it is faster
        inputDir = QtWidgets.QFileDialog.getExistingDirectory()
        return os.path.normpath(inputDir)

    def _createCallbacks(self, handler):
        pass


    def _killCallbacks(self, callbackIDList):
        pass

    def _checkRequirements(self):
        """OVERRIDEN METHOD"""
        logger.debug("Func: _checkRequirements")

        ## check platform
        currentOs = platform.system()
        if currentOs != "Linux" and currentOs != "Windows":
            self._exception(210, "Operating System is not supported\nCurrently only Windows and Linux supported")
            return -1, ["OS Error", "Operating System is not supported",
                        "Scene Manager only supports Windows and Linux Operating Systems"]

        return None, None

class MainUI(baseUI):
    def __init__(self):
        super(MainUI, self).__init__()

        self.manager = HoudiniManager()
        problem, msg = self.manager._checkRequirements()
        if problem:
            self.close()
            self.deleteLater()

        self.buildUI()
        self.initMainUI(newborn=True)
        self.extraMenus()
        self.modify()


    def extraMenus(self):
        pass

    def modify(self):
        # make sure load mode is checked and hidden
        self.load_radioButton.setChecked(True)
        self.load_radioButton.setVisible(False)
        self.reference_radioButton.setChecked(False)
        self.reference_radioButton.setVisible(False)
        self.makeReference_pushButton.setVisible(False)
        # idk why this became necessary for houdini..
        self.category_tabWidget.setMaximumSize(QtCore.QSize(16777215, 30))

        self.mIconPixmap = QtGui.QPixmap(":/icons/CSS/rc/iconHoudini.png")
        self.managerIcon_label.setPixmap(self.mIconPixmap)


