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
from tik_manager.dcc.max.core_max import MaxCoreFunctions
import shutil

from pymxs import runtime as rt

import datetime
import socket
import logging
# from glob import glob

from Qt import QtWidgets, QtGui

import tik_manager.core._version as _version

__author__ = "Arda Kutlu"
__copyright__ = "Copyright 2018, Scene Manager for 3dsMax Projects"
__credits__ = []
__version__ = "2.0.0"
__license__ = "GPL"
__maintainer__ = "Arda Kutlu"
__email__ = "ardakutlu@gmail.com"
__status__ = "Development"

SM_Version = "Scene Manager 3ds Max v%s" % _version.__version__

logging.basicConfig()
logger = logging.getLogger('sm3dsMax')
logger.setLevel(logging.WARNING)


class MaxManager(RootManager, MaxCoreFunctions):
    def __init__(self):
        super(MaxManager, self).__init__()
        self.dcc = "3dsMax"
        self.init_paths(self.dcc)
        self.init_database()


    def getSceneFile(self):
        """Overriden function"""
        return self._getSceneFile()


    def saveBaseScene(self, categoryName, baseName, subProjectIndex=0, makeReference=True, versionNotes="", sceneFormat="max", *args, **kwargs):
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


        # fullName = self.userList.keys()[self.userList.values().index(userName)]
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

        sceneFile = os.path.join(shotPath, "{0}.{1}".format(sceneName, sceneFormat))
        ## relativity update
        relSceneFile = os.path.relpath(sceneFile, start=projectPath)

        # fManager.Save(sceneFile)
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

        # version serialization:
        # version, api, sdk = rt.maxversion()
        versionInfo = self._getVersion()
        # vInfo = [version, api, sdk]
        vInfo = [versionInfo[0], versionInfo[1], versionInfo[2]]

        jsonInfo["ID"] = "Sm3dsMaxV02_sceneFile"
        # jsonInfo["3dsMaxVersion"] = os.path.basename(os.path.split(pManager.GetMaxSysRootDir())[0])
        jsonInfo["3dsMaxVersion"] = vInfo
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
        self.progressLogger("save", sceneFile)
        return [0, ""]

    def saveVersion(self, makeReference=True, versionNotes="", sceneFormat="max", insertTo=None, *args, **kwargs):
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

        if sceneInfo: ## getCurrentJson returns None if the resolved json path is missing
            jsonFile = sceneInfo["jsonFile"]
            jsonInfo = self._loadJson(jsonFile)
            if jsonInfo == -1:
                msg = "Database file is corrupted"
                return -1, msg

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
            relSceneFile = os.path.join(jsonInfo["Path"], "{0}.{1}".format(sceneName, sceneFormat))

            sceneFile = os.path.join(sceneInfo["projectPath"], relSceneFile)

            self._saveAs(sceneFile)

            thumbPath = self.createThumbnail(dbPath=jsonFile, versionInt=currentVersion)

            jsonInfo["Versions"].append(
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
            logger.warning(msg)
            return -1, msg
        self.progressLogger("save", sceneFile)
        return jsonInfo


    def createPreview(self, *args, **kwargs):
        """Creates a Playblast preview from currently open scene"""
        # rt = pymxs.runtime

        openSceneInfo = self.getOpenSceneInfo()
        if not openSceneInfo:
            msg = "This is not a base scene. Scene must be saved as a base scene before playblasting."
            # raise Exception([360, msg])
            self._exception(360, msg)
            return
            # logger.warning(msg)
            # return -1, msg

        # get view info
        viewportType = rt.viewport.getType()
        if str(viewportType) == "view_camera":
            currentCam = str(rt.getActiveCamera().name)
        else:
            currentCam = str(viewportType)

        validName = currentCam.replace("|", "__").replace(" ", "_")
        extension = "avi"

        versionName = rt.maxFilePath + rt.maxFileName # abs path of the filename with extension
        relVersionName = os.path.relpath(versionName, start=openSceneInfo["projectPath"]) # relative path of filename with ext

        if not os.path.isdir(os.path.normpath(openSceneInfo["previewPath"])):
            os.makedirs(os.path.normpath(openSceneInfo["previewPath"]))
        playBlastFile = os.path.join(openSceneInfo["previewPath"], "{0}_{1}_PB.{2}".format(self.niceName(versionName), validName, extension))
        relPlayBlastFile = os.path.relpath(playBlastFile, start=openSceneInfo["projectPath"])

        if os.path.isfile(playBlastFile):
            try:
                os.remove(playBlastFile)
            except WindowsError:
                msg = "The file is open somewhere else"
                logger.warning(msg)
                return -1, msg

        jsonInfo = self._loadJson(openSceneInfo["jsonFile"])
        if jsonInfo == -1:
            msg = "Database file is corrupted"
            return -1, msg
        # returns 0,"" if everything is ok, -1,msg if error

        pbSettings = self.loadPBSettings()
        originalValues = {"width": rt.renderWidth,
                        "height": rt.renderHeight
                        }

        originalSelection = rt.execute("selection as array")



        # change the render settings temporarily
        rt.renderWidth = pbSettings["Resolution"][0]
        rt.renderHeight = pbSettings["Resolution"][1]

        if pbSettings["PolygonOnly"]:
            dspGeometry = True
            dspShapes = False
            dspLights = False
            dspCameras = False
            dspHelpers = False
            dspParticles = False
            dspBones = False
        else:
            dspGeometry = True
            dspShapes = True
            dspLights = True
            dspCameras = True
            dspHelpers = True
            dspParticles = True
            dspBones = True

        dspGrid = pbSettings["ShowGrid"]
        dspFrameNums = pbSettings["ShowFrameNumber"]
        percentSize = pbSettings["Percent"]

        if pbSettings["WireOnShaded"]:
            rndLevel = rt.execute("#litwireframe")
        else:
            rndLevel = rt.execute("#smoothhighlights")

        if pbSettings["ClearSelection"]:
            rt.clearSelection()

        test = rt.createPreview(filename=playBlastFile, percentSize=percentSize, dspGeometry=dspGeometry,
                         dspShapes=dspShapes, dspLights=dspLights,
                         dspCameras=dspCameras, dspHelpers=dspHelpers,
                         dspParticles=dspParticles, dspBones=dspBones,
                         dspGrid=dspGrid, dspFrameNums=dspFrameNums,
                         rndLevel=rndLevel)

        # prior to version 2020, filename flag is not working
        if not os.path.isfile(playBlastFile):
        # find the path of where the avi file be created
            if rt.maxFilePath:
                previewname = rt.getFilenameFile(rt.maxFileName)
            else:
                previewname = "Untitled"

            sourceClip = rt.GetDir(rt.execute("#preview")) + "\_scene.avi"
            shutil.copy(sourceClip, playBlastFile)

        rt.renderWidth = originalValues["width"]
        rt.renderHeight = originalValues["height"]

        rt.select(originalSelection)

        if pbSettings["ConvertMP4"]:
            convertedFile = self._convertPreview(playBlastFile, overwrite=True, deleteAfter=False, crf=pbSettings["CrfValue"])
            relPlayBlastFile = os.path.relpath(convertedFile, start=openSceneInfo["projectPath"])
            # os.startfile(convertedFile)
        else:
            relPlayBlastFile = os.path.relpath(playBlastFile, start=openSceneInfo["projectPath"])

        ## find this version in the json data

        for version in jsonInfo["Versions"]:
            if relVersionName == version["RelativePath"]:
                version["Preview"][currentCam] = relPlayBlastFile

        self._dumpJson(jsonInfo, openSceneInfo["jsonFile"])
        return 0, ""


    def loadBaseScene(self, force=False):
        """Loads the scene at cursor position"""
        relSceneFile = self._currentSceneInfo["Versions"][self._currentVersionIndex-1]["RelativePath"]
        absSceneFile = os.path.join(self.projectDir, relSceneFile)
        if os.path.isfile(absSceneFile):
            # fManager.Open(absSceneFile)
            self._load(absSceneFile)
            self.progressLogger("load", absSceneFile)
            return 0
        else:
            msg = "File in Scene Manager database doesnt exist"
            logger.error(msg)
            return -1, msg

    def importBaseScene(self):
        """Imports the scene at cursor position"""
        relSceneFile = self._currentSceneInfo["Versions"][self._currentVersionIndex-1]["RelativePath"]
        absSceneFile = os.path.join(self.projectDir, relSceneFile)
        if os.path.isfile(absSceneFile):
            # fManager.Merge(absSceneFile, mergeAll=True, selectMerged=True)
            # fManager.Merge(absSceneFile)
            self._import(absSceneFile)
            # cmds.file(absSceneFile, i=True)
            return 0
        else:
            msg = "File in Scene Manager database doesnt exist"
            logger.error(msg)
            return -1, msg

    def referenceBaseScene(self, set_ranges="ask"):
        """Creates reference from the scene at cursor position"""

        projectPath = self.projectDir
        relReferenceFile = self._currentSceneInfo["ReferenceFile"]


        if relReferenceFile:
            referenceFile = os.path.join(projectPath, relReferenceFile)

            self._reference(referenceFile)
            if set_ranges == "ask":
                try:
                    ranges = self._currentSceneInfo["Versions"][self._currentSceneInfo["ReferencedVersion"]-1]["Ranges"]
                    q = self._question("Do You want to set the Time ranges same with the reference?")
                    if q:
                        self._setTimelineRanges(ranges)
                except KeyError:
                    pass
            elif set_ranges == "yes":
                try:
                    ranges = self._currentSceneInfo["Versions"][self._currentSceneInfo["ReferencedVersion"]-1]["Ranges"]
                    self._setTimelineRanges(ranges)
                except KeyError:
                    pass
            else:
                pass
        else:
            logger.warning("There is no reference set for this scene. Nothing changed")


    def createThumbnail(self, useCursorPosition=False, dbPath = None, versionInt = None):
        """
        Creates the thumbnail file.
        :param databaseDir: (String) If defined, this folder will be used to store the created database.
        :param version: (integer) if defined this version number will be used instead currently open scene version.
        :return: (String) Relative path of the thumbnail file
        """
        projectPath = self.projectDir
        if useCursorPosition:
            versionInt = self.currentVersionIndex
            dbPath = self.currentDatabasePath
        else:
            if not dbPath or not versionInt:
                logger.warning (("Both dbPath and version must be defined if useCursorPosition=False"))

        versionStr = "v%s" % (str(versionInt).zfill(3))
        dbDir, shotNameWithExt = os.path.split(dbPath)
        shotName = os.path.splitext(shotNameWithExt)[0]

        thumbPath = "{0}_{1}_thumb.jpg".format(os.path.join(dbDir, shotName), versionStr)
        relThumbPath = os.path.relpath(thumbPath, projectPath)

        ## Software specific section
        oWidth = 221
        oHeight = 124

        grab = rt.gw.getViewportDib()

        ratio = float(grab.width)/float(grab.height)

        if ratio <= 1.782:
            new_width = oHeight * ratio
            new_height = oHeight
        else:
            new_width = oWidth
            new_height = oWidth / ratio

        resizeFrame = rt.bitmap(new_width, new_height, color = rt.color(0,0,0))
        rt.copy(grab, resizeFrame)
        thumbFrame = rt.bitmap(oWidth, oHeight, color = rt.color(0,0,0))
        xOffset = (oWidth - resizeFrame.width) /2
        yOffset = (oHeight - resizeFrame.height) /2

        rt.pasteBitmap(resizeFrame, thumbFrame, rt.point2(0, 0), rt.point2(xOffset, yOffset))
        thumbFrame.filename = thumbPath
        rt.save(thumbFrame)
        rt.close(thumbFrame)

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
        """Compares the versions of current session and database version at cursor position"""
        # return 0, ""
        if not self._currentSceneInfo["3dsMaxVersion"]:
            logger.warning("Cursor is not on a base scene")
            return
        versionDict = {11000: "v2009",
                       12000: "v2010",
                       13000: "v2011",
                       14000: "v2012",
                       15000: "v2013",
                       16000: "v2014",
                       17000: "v2015",
                       18000: "v2016",
                       19000: "v2017",
                       20000: "v2018"
                       }

        #version serialization:
        versionInfo = self._getVersion()
        currentVersion = [versionInfo[0], versionInfo[1], versionInfo[2]]
        logger.debug("currentversion %s" %currentVersion)
        baseSceneVersion = self._currentSceneInfo["3dsMaxVersion"]
        logger.debug("baseVersion %s" % baseSceneVersion)

        try:
            niceVName = versionDict[currentVersion[0]]
        except KeyError:
            niceVName = str(currentVersion[0])

        if currentVersion == baseSceneVersion:
            msg = ""
            return 0, msg

        if currentVersion[0] > baseSceneVersion[0]: # max version compare
            message = "Base Scene is created with a LOWER 3ds Max version ({0}). Are you sure you want to continue?".format(niceVName)
            return -1, message

        if currentVersion[0] < baseSceneVersion[0]:
            message = "Base Scene is created with a HIGHER 3ds Max version ({0}). Are you sure you want to continue?".format(niceVName)
            return -1, message

        if currentVersion[1] > baseSceneVersion[1]: # max Api
            message = "Base Scene is created with a LOWER Build ({0}). Are you sure you want to continue?".format(niceVName)
            return -1, message

        if currentVersion[1] < baseSceneVersion[1]:
            message = "Base Scene is created with a HIGHER Build ({0}). Are you sure you want to continue?".format(niceVName)
            return -1, message

        # old or corrupted database
        return 0, ""  # skip


    def isSceneModified(self):
        """Checks the currently open scene saved or not"""
        return self._isSceneModified()

    def saveSimple(self):
        """Save the currently open file"""
        self._save()
        self.progressLogger("save", self.getSceneFile())

    def getFormatsAndCodecs(self):
        """Returns the codecs which can be used in current workstation"""
        # TODO : Write Get Formats and Codecs for 3ds max (if applicable)
        logger.warning ("getFormatsAndCodecs Function not yet implemented")


    def preSaveChecklist(self):
        """Checks the scene for inconsistencies"""
        checklist = []
        fpsValue_setting = self.getFPS()
        fpsValue_current = rt.framerate
        if fpsValue_setting is not fpsValue_current:
            msg = "FPS values are not matching with the project settings.\n Project FPS => {0}\n scene FPS => {1}\nDo you want to continue?".format(fpsValue_setting, fpsValue_current)
            checklist.append(msg)

        return checklist

    def _exception(self, code, msg, *args, **kwargs):
        """Overriden Function"""

        rt.messageBox(msg, title=self.errorCodeDict[code])
        if (200 >= code < 210):
            raise Exception(code, msg)

    def _question(self, msg, *args, **kwargs):
        state = rt.queryBox( msg, title='Manager Question')
        return state

    def _info(self, msg, *args, **kwargs):
        rt.messageBox(msg, title='Info')

    def _inputDir(self):
        """OVERRIDEN METHOD"""
        # Qt File dialog is preferred because it is faster
        inputDir = QtWidgets.QFileDialog.getExistingDirectory()
        return os.path.normpath(inputDir)

    def _createCallbacks(self, handler):
        logger.warning("_createCallbacks Function yet implemented")

    def _killCallbacks(self, callbackIDList):
        logger.warning("_killCallbacks Function not yet implemented")

class MainUI(baseUI):
    def __init__(self):
        super(MainUI, self).__init__()

        self.manager = MaxManager()
        problem, msg = self.manager._checkRequirements()
        if problem:
            self.close()
            self.deleteLater()

        self.buildUI()
        self.initMainUI(newborn=True)
        self.extraMenus()
        self.modify()

    def extraMenus(self):
        self.scenes_rcItem_0.setText('Merge Scene')

    def modify(self):
        self.mIconPixmap = QtGui.QPixmap(":/icons/CSS/rc/iconMax.png")
        self.managerIcon_label.setPixmap(self.mIconPixmap)

    def onModeChange(self):
        """OVERRIDEN METHOD - This method is overriden to make the color changing compatible with 3ds max"""
        self._vEnableDisable()

        if self.load_radioButton.isChecked():
            self.loadScene_pushButton.setText("Load Scene")
            self.scenes_listWidget.setProperty("reference_pyside", False)
            self.multi_reference_cb.setHidden(True)
            self.scenes_listWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
            self.scenes_rcItem_6.setVisible(True)
        else:
            self.loadScene_pushButton.setText("Reference Scene")
            self.scenes_listWidget.setProperty("reference_pyside", True)
            self.multi_reference_cb.setHidden(False)
            self.scenes_listWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
            self.scenes_rcItem_6.setVisible(False)

        self.scenes_listWidget.setStyleSheet("")
        self.populateBaseScenes()




