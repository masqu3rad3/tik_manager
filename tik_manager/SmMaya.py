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
os.environ["FORCE_QT4"]="0"

# DELETE
# ------

from SmUIRoot import MainUI as baseUI
# import SmRoot
# reload(SmRoot)
from SmRoot import RootManager
from tik_manager.coreFunctions.coreFunctions_Maya import MayaCoreFunctions

import shutil
import maya.cmds as cmds
import maya.mel as mel
# import pymel.core as pm
import datetime
import socket
import logging
from glob import glob

import ImMaya

# import Qt
from Qt import QtWidgets, QtGui

## DO NOT REMOVE THIS:
## DO NOT REMOVE THIS:

logging.basicConfig()
logger = logging.getLogger('smMaya')
logger.setLevel(logging.WARNING)

class MayaManager(RootManager, MayaCoreFunctions):
    def __init__(self):
        super(MayaManager, self).__init__()
        # hard coded format dictionary to pass the format info to cmds
        # self.formatDict = {"ma": "mayaAscii", "mb": "mayaBinary"}
        self.swName = "Maya"
        self.init_paths(self.swName)
        self.backwardcompatibility()  # DO NOT RUN UNTIL RELEASE
        self.init_database()

    def getSceneFile(self):
        """Overriden function"""
        logger.debug("Func: getSceneFile")
        return self._getSceneFile()

    def setProject(self, path):
        """Sets the project"""
        logger.debug("Func: setProject")
        self._setProject(path)
        self.projectDir = self.getProjectDir()

    def saveBaseScene(self, categoryName, baseName, subProjectIndex=0, makeReference=True, versionNotes="", sceneFormat="mb", *args, **kwargs):
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

        ## Unknown nodes Check
        if sceneFormat == "mb":
            ext = u'.mb'
            saveFormat = "mayaBinary"
        else:
            ext = u'.ma'
            saveFormat = "mayaAscii"

        originalPath = self._getSceneFile()

        dump, origExt = os.path.splitext(originalPath)

        if len(cmds.ls(type="unknown")) > 0 and ext != origExt:
            msg = "There are unknown nodes in the scene. Cannot proceed with %s extension.\n\nDo you want to continue with %s?" %(ext, origExt)
            state = cmds.confirmDialog(title='Cannot Continue', message=msg, button=['Ok', 'Cancel'])
            if state == "Ok":
                if origExt == u'.mb':
                    ext = u'.mb'
                    saveFormat = "mayaBinary"
                else:
                    ext = u'.ma'
                    saveFormat = "mayaAscii"

            elif state == "Cancel":
                return
        ## Unknown nodes Check - end

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
            "date": now
        }
        sceneName = self.resolveSaveName(nameDict, version)

        # sceneFile = os.path.join(shotPath, "{0}.{1}".format(sceneName, sceneFormat))
        sceneFile = os.path.join(shotPath, "{0}{1}".format(sceneName, ext))
        ## relativity update
        relSceneFile = os.path.relpath(sceneFile, start=projectPath)
        # killTurtle()
        # self._saveAs(sceneFile, format=self.formatDict[sceneFormat])
        self._saveAs(sceneFile, format=saveFormat)

        thumbPath = self.createThumbnail(dbPath=jsonFile, versionInt=version)

        jsonInfo = {}

        if makeReference:
            # TODO // Find an elegant solution and add MA compatibility. Can be merged with makeReference function in derived class
            referenceName = "{0}_{1}_forReference".format(baseName, categoryName)
            # referenceFile = os.path.join(shotPath, "{0}.{1}".format(referenceName, sceneFormat))
            referenceFile = os.path.join(shotPath, "{0}{1}".format(referenceName, ext))
            ## relativity update
            relReferenceFile = os.path.relpath(referenceFile, start=projectPath)
            shutil.copyfile(sceneFile, referenceFile)
            jsonInfo["ReferenceFile"] = relReferenceFile
            jsonInfo["ReferencedVersion"] = version
        else:
            jsonInfo["ReferenceFile"] = None
            jsonInfo["ReferencedVersion"] = None

        jsonInfo["ID"] = "SmMayaV03_sceneFile"
        # jsonInfo["MayaVersion"] = cmds.about(q=True, api=True)
        jsonInfo["MayaVersion"] = self._getVersion()
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
        return [0, ""]

    def saveVersion(self, makeReference=True, versionNotes="", sceneFormat="mb", *args, **kwargs):
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
            cmds.warning(msg)
            return -1, msg

        sceneInfo = self.getOpenSceneInfo()

        if not sceneInfo:
            msg = "This is not a base scene (Json file cannot be found)"
            cmds.warning(msg)
            return -1, msg

        ## Unknown nodes Check
        if sceneFormat == "mb":
            ext = u'.mb'
            saveFormat = "mayaBinary"
        else:
            ext = u'.ma'
            saveFormat = "mayaAscii"

        # originalPath = self._getSceneFile()

        dump, origExt = os.path.splitext(currentSceneName)

        if len(cmds.ls(type="unknown")) > 0 and ext != origExt:
            msg = "There are unknown nodes in the scene. Cannot proceed with %s extension.\n\nDo you want to continue with %s?" %(ext, origExt)
            state = cmds.confirmDialog(title='Cannot Continue', message=msg, button=['Ok', 'Cancel'])
            if state == "Ok":
                if origExt == u'.mb':
                    ext = u'.mb'
                    saveFormat = "mayaBinary"
                else:
                    ext = u'.ma'
                    saveFormat = "mayaAscii"

            elif state == "Cancel":
                return
        ## Unknown nodes Check - end

        jsonFile = sceneInfo["jsonFile"]
        jsonInfo = self._loadJson(jsonFile)

        currentVersion = len(jsonInfo["Versions"]) + 1
        ## Naming Dictionary
        nameDict = {
            "baseName": jsonInfo["Name"],
            "categoryName": jsonInfo["Category"],
            "userInitials": self._usersDict[self.currentUser],
            "date": now
        }
        sceneName = self.resolveSaveName(nameDict, currentVersion)

        # relSceneFile = os.path.join(jsonInfo["Path"], "{0}.{1}".format(sceneName, sceneFormat))
        relSceneFile = os.path.join(jsonInfo["Path"], "{0}{1}".format(sceneName, ext))

        sceneFile = os.path.join(sceneInfo["projectPath"], relSceneFile)

        # self._saveAs(sceneFile, format=self.formatDict[sceneFormat])
        self._saveAs(sceneFile, format=saveFormat)

        thumbPath = self.createThumbnail(dbPath=jsonFile, versionInt=currentVersion)

        jsonInfo["Versions"].append(
            # PATH => Notes => User Initials => Machine ID => Playblast => Thumbnail
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
            # relReferenceFile = os.path.join(jsonInfo["Path"], "{0}.{1}".format(referenceName, sceneFormat))
            relReferenceFile = os.path.join(jsonInfo["Path"], "{0}{1}".format(referenceName, ext))
            referenceFile = os.path.join(sceneInfo["projectPath"], relReferenceFile)

            shutil.copyfile(sceneFile, referenceFile)
            jsonInfo["ReferenceFile"] = relReferenceFile
            jsonInfo["ReferencedVersion"] = currentVersion
        self._dumpJson(jsonInfo, jsonFile)

        return jsonInfo

    def createPreview(self, previewCam=None, forceSequencer=False, *args, **kwargs):
        """Creates a Playblast preview from currently open scene"""
        logger.debug("Func: createPreview")

        pbSettings = self.loadPBSettings()

        # if the file will be converted, force it to uncompressed avi
        if pbSettings["ConvertMP4"]:
            # TODO // Make it compatible with LINUX and MAC
            validFormats = [u'avi']
            validCodecs = [u'none']
            extension = "avi"

        else:
            validFormats = cmds.playblast(format=True, q=True)
            validCodecs = cmds.playblast(c=True, q=True)

            if not pbSettings["Format"] in validFormats:
                msg = ("Format specified in project settings is not supported. Install {0}".format(pbSettings["Format"]))
                self._exception(360, msg)
                return

            if not pbSettings["Codec"] in validCodecs:
                msg = ("Codec specified in project settings is not supported. Install {0}".format(pbSettings["Codec"]))
                self._exception(360, msg)
                return

            extension = "mov" if pbSettings["Format"] == "qt" else "avi"

            # Quicktime format is missing the final frame all the time. Add an extra frame to compansate
            if pbSettings["Format"] == 'qt':
                maxTime = cmds.playbackOptions(q=True, maxTime=True)
                endTime = cmds.playbackOptions(q=True, animationEndTime=True)
                cmds.playbackOptions(maxTime=maxTime + 1)
                cmds.playbackOptions(animationEndTime=endTime + 1)

        openSceneInfo = self.getOpenSceneInfo()
        if not openSceneInfo:
            msg = "This is not a base scene. Scene must be saved as a base scene before playblasting."
            self._exception(360, msg)
            return

        selection = self._getSelection()
        cmds.select(d=pbSettings["ClearSelection"])
        jsonInfo = self._loadJson(openSceneInfo["jsonFile"])

        if previewCam:
            currentCam = previewCam
            validName = previewCam
            sequenceTime = False
        elif forceSequencer:
            currentCam = "persp"
            validName = "Sequencer"
            sequenceTime = True
        else:
            try:
                currentCam = cmds.modelPanel(cmds.getPanel(wf=True), q=True, cam=True)
                validName = currentCam
                sequenceTime = False
            except RuntimeError:
                panel = cmds.getPanel(wf=True)
                if "sequenceEditorPanel" in panel:
                    currentCam = "persp"
                    validName = "Sequence"
                    sequenceTime = True
                else:
                    msg = "Highlighted Pane is not a camera view"
                    self._exception(360, msg)
                    return

        # validName = currentCam

        replaceDict = {"|":"__",
                       " ":"_",
                       ":":"_"}
        for item in replaceDict.items():
            validName = validName.replace(item[0], item[1])

        if not self.nameCheck(validName):
            msg = "A scene view must be highlighted"
            self._exception(360, msg)
            return

        versionName = self.getSceneFile()
        relVersionName = os.path.relpath(versionName, start=openSceneInfo["projectPath"])
        playBlastFile = os.path.join(openSceneInfo["previewPath"], "{0}_{1}_PB.{2}".format(self.niceName(versionName), validName, extension))
        # relPlayBlastFile = os.path.relpath(playBlastFile, start=openSceneInfo["projectPath"])

        if os.path.isfile(playBlastFile):
            try:
                os.remove(playBlastFile)
            except WindowsError:
                msg = "The file is open somewhere else"
                self._exception(202, msg)
                return

        ## CREATE A CUSTOM PANEL WITH DESIRED SETTINGS

        tempWindow = cmds.window(title="SM_Playblast",
                               widthHeight=(pbSettings["Resolution"][0] * 1.1, pbSettings["Resolution"][1] * 1.1),
                               tlc=(0, 0))
        # panel = pm.getPanel(wf=True)

        cmds.paneLayout()

        pbPanel = cmds.modelPanel(camera=currentCam)
        cmds.showWindow(tempWindow)
        cmds.setFocus(pbPanel)

        cmds.modelEditor(pbPanel, e=1,
                       allObjects=not pbSettings["PolygonOnly"],
                       da="smoothShaded",
                       displayTextures=pbSettings["DisplayTextures"],
                       wireframeOnShaded=pbSettings["WireOnShaded"],
                       grid=pbSettings["ShowGrid"],
                       useDefaultMaterial=pbSettings["UseDefaultMaterial"],
                       polymeshes=True,
                       imagePlane=True,
                       hud=True
                       )

        cmds.camera(currentCam, e=True, overscan=True, displayFilmGate=False, displayResolution=False)

        ## get previous HUD States and turn them all off
        hudPreStates = {}
        HUDS = cmds.headsUpDisplay(lh=True)
        for hud in HUDS:
            hudPreStates[hud] = cmds.headsUpDisplay(hud, q=True, vis=True)
            cmds.headsUpDisplay(hud, e=True, vis=False)

        ## clear the custom HUDS
        customHuds = ['SMFrame', 'SMScene', 'SMCategory', 'SMFPS', 'SMCameraName', 'SMFrange']
        for hud in customHuds:
            if cmds.headsUpDisplay(hud, ex=True):
                cmds.headsUpDisplay(hud, rem=True)

        if pbSettings["ShowFrameNumber"]:
            freeBl = cmds.headsUpDisplay(nfb=5)  ## this is the next free block on section 5
            cmds.headsUpDisplay('SMFrame', s=5, b=freeBl, label="Frame", preset="currentFrame", dfs="large",
                              lfs="large")
        if pbSettings["ShowSceneName"]:
            freeBl = cmds.headsUpDisplay(nfb=5)  ## this is the next free block on section 5
            cmds.headsUpDisplay('SMScene', s=5, b=freeBl, label="Scene: %s" % (self.niceName(versionName)),
                                lfs="large")
        if pbSettings["ShowCategory"]:
            freeBl = cmds.headsUpDisplay(nfb=5)  ## this is the next free block on section 5
            cmds.headsUpDisplay('SMCategory', s=5, b=freeBl, label="Category: %s" % (jsonInfo["Category"]),
                              lfs="large")
        if pbSettings["ShowFPS"]:
            freeBl = cmds.headsUpDisplay(nfb=5)  ## this is the next free block on section 5
            cmds.headsUpDisplay('SMFPS', s=5, b=freeBl, label="Time Unit: %s" % (cmds.currentUnit(q=True, time=True)),
                              lfs="large")

        # v1.1 SPECIFIC
        try:
            if pbSettings["ShowFrameRange"]:
                freeBl = cmds.headsUpDisplay(nfb=5)  ## this is the next free block on section 5
                cmds.headsUpDisplay('SMFrange', s=5, b=freeBl,
                                  label="Frame Range: {} - {}".format(int(cmds.playbackOptions(q=True, minTime=True)),
                                                                      int(cmds.playbackOptions(q=True,
                                                                                             maxTime=True))),
                                  lfs="large")
        except KeyError:
            pass

        freeBl = cmds.headsUpDisplay(nfb=2)
        cmds.headsUpDisplay('SMCameraName', s=2, b=freeBl, ba='center', dw=50, pre='cameraNames')

        ## Get the active sound

        aPlayBackSliderPython = mel.eval('$tmpVar=$gPlayBackSlider')
        activeSound = cmds.timeControl(aPlayBackSliderPython, q=True, sound=True)

        ## Check here: http://download.autodesk.com/us/maya/2011help/pymel/generated/functions/pymel.core.windows/pymel.core.windows.headsUpDisplay.html
        # print "playBlastFile", playBlastFile
        normPB = os.path.normpath(playBlastFile)

        cmds.playblast(format=pbSettings["Format"],
                       sequenceTime=sequenceTime,
                       filename=playBlastFile,
                       widthHeight=pbSettings["Resolution"],
                       percent=pbSettings["Percent"],
                       quality=pbSettings["Quality"],
                       compression=pbSettings["Codec"],
                       sound=activeSound,
                       # uts=True,
                       v=not pbSettings["ConvertMP4"]
                       )
        ## remove window when pb is donw
        cmds.deleteUI(tempWindow)

        # Get back to the original frame range if the codec is Quick Time
        if pbSettings["Format"] == 'qt':
            cmds.playbackOptions(maxTime=maxTime)
            cmds.playbackOptions(animationEndTime=endTime)

        ## remove the custom HUdS
        if pbSettings["ShowFrameNumber"]:
            cmds.headsUpDisplay('SMFrame', rem=True)
        if pbSettings["ShowSceneName"]:
            cmds.headsUpDisplay('SMScene', rem=True)
        if pbSettings["ShowCategory"]:
            cmds.headsUpDisplay('SMCategory', rem=True)
        if pbSettings["ShowFPS"]:
            cmds.headsUpDisplay('SMFPS', rem=True)
        try:
            if pbSettings["ShowFrameRange"]:
                cmds.headsUpDisplay('SMFrange', rem=True)
        except KeyError:
            pass

            cmds.headsUpDisplay('SMCameraName', rem=True)

        ## get back the previous state of HUDS
        for hud in hudPreStates.keys():
            cmds.headsUpDisplay(hud, e=True, vis=hudPreStates[hud])
        # pm.select(selection)
        try:
            cmds.select(selection)
        except TypeError: # in case nothing selected
            pass

        if pbSettings["ConvertMP4"]:
            convertedFile = self._convertPreview(playBlastFile, overwrite=True, deleteAfter=True, crf=pbSettings["CrfValue"])
            relPlayBlastFile = os.path.relpath(convertedFile, start=openSceneInfo["projectPath"])
            os.startfile(convertedFile)
        else:
            relPlayBlastFile = os.path.relpath(playBlastFile, start=openSceneInfo["projectPath"])

        ## find this version in the json data
        for version in jsonInfo["Versions"]:
            if relVersionName == version["RelativePath"]:
                version["Preview"][validName] = relPlayBlastFile

        self._dumpJson(jsonInfo, openSceneInfo["jsonFile"])
        return 0, ""

    def loadBaseScene(self, force=False):
        """Loads the scene at cursor position"""
        logger.debug("Func: loadBaseScene")
        relSceneFile = self._currentSceneInfo["Versions"][self._currentVersionIndex-1]["RelativePath"]
        absSceneFile = os.path.normpath(os.path.join(self.projectDir, relSceneFile))
        linCorrect = unicode(absSceneFile.replace("\\", "/"))
        if os.path.isfile(linCorrect):
            # cmds.file(absSceneFile, o=True, force=force)
            self._load(linCorrect, force=True)
            return 0
        else:
            msg = "File in Scene Manager database doesnt exist"
            cmds.error(msg)
            return -1, msg

        # if os.path.isfile(absSceneFile.replace(os.sep, "/")):
        #     # cmds.file(absSceneFile, o=True, force=force)
        #     self._load(absSceneFile, force=True)
        #     return 0
        # else:
        #     msg = "File in Scene Manager database doesnt exist"
        #     cmds.error(msg)
        #     return -1, msg

    def importBaseScene(self):
        """Imports the scene at cursor position"""
        logger.debug("Func: importBaseScene")
        relSceneFile = self._currentSceneInfo["Versions"][self._currentVersionIndex-1]["RelativePath"]
        absSceneFile = os.path.join(self.projectDir, relSceneFile)
        if os.path.isfile(absSceneFile):
            # cmds.file(absSceneFile, i=True)
            self._import(absSceneFile)
            return 0
        else:
            msg = "File in Scene Manager database doesnt exist"
            cmds.error(msg)
            return -1, msg

    def referenceBaseScene(self):
        """Creates reference from the scene at cursor position"""
        logger.debug("Func: referenceBaseScene")
        projectPath = self.projectDir
        relReferenceFile = self._currentSceneInfo["ReferenceFile"]

        if relReferenceFile:
            referenceFile = os.path.join(projectPath, relReferenceFile)
            refFileBasename = os.path.split(relReferenceFile)[1]
            namespace = os.path.splitext(refFileBasename)[0]
            self._reference(os.path.normpath(referenceFile), namespace)
            # cmds.file(os.path.normpath(referenceFile), reference=True, gl=True, mergeNamespacesOnClash=False,
            #           namespace=namespace)
            try:
                ranges = self._currentSceneInfo["Versions"][self._currentSceneInfo["ReferencedVersion"]-1]["Ranges"]
                q = self._question("Do You want to set the Time ranges same with the reference?")
                if q:
                    self._setTimelineRanges(ranges)
            except KeyError:
                pass

        else:
            cmds.warning("There is no reference set for this scene. Nothing changed")

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
            # frame = pm.currentTime(query=True)
            frame = self._getCurrentFrame()
            # store = pm.getAttr("defaultRenderGlobals.imageFormat")
            store = cmds.getAttr("defaultRenderGlobals.imageFormat")
            # pm.setAttr("defaultRenderGlobals.imageFormat", 8)  # This is the value for jpeg
            cmds.setAttr("defaultRenderGlobals.imageFormat", 8)  # This is the value for jpeg
            # pm.playblast(completeFilename=thumbPath, forceOverwrite=True, format='image', width=221, height=124, showOrnaments=False, frame=[frame], viewer=False, percent=100)
            cmds.playblast(completeFilename=thumbPath, forceOverwrite=True, format='image', width=221, height=124, showOrnaments=False, frame=[frame], viewer=False, percent=100)
            # pm.setAttr("defaultRenderGlobals.imageFormat", store) #take it back
            cmds.setAttr("defaultRenderGlobals.imageFormat", store) #take it back
        else:
            # pm.warning("something went wrong with thumbnail. Skipping thumbnail")
            cmds.warning("something went wrong with thumbnail. Skipping thumbnail")
            return ""
        # return thumbPath
        return relThumbPath

    def replaceThumbnail(self, filePath=None ):
        """
        Replaces the thumbnail with given file or current view
        :param filePath: (String)  if a filePath is defined, this image (.jpg or .gif) will be used as thumbnail
        :return: None
        """
        logger.debug("Func: replaceThumbnail")
        if not filePath:
            filePath = self.createThumbnail(useCursorPosition=True)

        self._currentSceneInfo["Versions"][self.currentVersionIndex-1]["Thumb"]=filePath

        self._dumpJson(self._currentSceneInfo, self.currentDatabasePath)

    def compareVersions(self):

        # // TODO : Find a BETTER way to compare versions.
        # // TODO : You may question each individual scen file for version insteas of base scene database

        """Compares the versions of current session and database version at cursor position"""
        logger.debug("Func: compareVersions")
        if not self._currentSceneInfo["MayaVersion"]:
            cmds.warning("Cursor is not on a base scene")
            return
        versionDict = {200800: "v2008",
                       200806: "v2008_EXT2",
                       200806: "v2008_SP1",
                       200900: "v2009",
                       200904: "v2009_EXT1",
                       200906: "v2009_SP1A",
                       201000: "v2010",
                       201100: "v2011",
                       201101: "v2011_HOTFIX1",
                       201102: "v2011_HOTFIX2",
                       201103: "v2011_HOTFIX3",
                       201104: "v2011_SP1",
                       201200: "v2012",
                       201201: "v2012_HOTFIX1",
                       201202: "v2012_HOTFIX2",
                       201203: "v2012_HOTFIX3",
                       201204: "v2012_HOTFIX4",
                       201209: "v2012_SAP1",
                       201217: "v2012_SAP1SP1",
                       201209: "v2012_SP1",
                       201217: "v2012_SP2",
                       201300: "v2013",
                       201400: "v2014",
                       201450: "v2014_EXT1",
                       201451: "v2014_EXT1SP1",
                       201459: "v2014_EXT1SP2",
                       201402: "v2014_SP1",
                       201404: "v2014_SP2",
                       201406: "v2014_SP3",
                       201500: "v2015",
                       201506: "v2015_EXT1",
                       201507: "v2015_EXT1SP5",
                       201501: "v2015_SP1",
                       201502: "v2015_SP2",
                       201505: "v2015_SP3",
                       201506: "v2015_SP4",
                       201507: "v2015_SP5",
                       201600: "v2016",
                       201650: "v20165",
                       201651: "v20165_SP1",
                       201653: "v20165_SP2",
                       201605: "v2016_EXT1",
                       201607: "v2016_EXT1SP4",
                       201650: "v2016_EXT2",
                       201651: "v2016_EXT2SP1",
                       201653: "v2016_EXT2SP2",
                       201605: "v2016_SP3",
                       201607: "v2016_SP4",
                       201700: "v2017",
                       201701: "v2017U1",
                       201720: "v2017U2",
                       201740: "v2017U3",
                       20180000: "v2018",
                       20180100: "v2018.1",
                       20180200: "v2018.2",
                       20180300: "v2018.3",
                       20180400: "v2018.4",
                       20180500: "v2018.5"
                       }

        # currentVersion = pm.versions.current()
        # currentVersion = cmds.about(api=True)
        currentVersion = self._getVersion()
        try:
            niceVName=versionDict[self._currentSceneInfo["MayaVersion"]]
        except KeyError:
            niceVName = self._currentSceneInfo["MayaVersion"]
        message = ""
        if self._currentSceneInfo["MayaVersion"] == currentVersion:
            return 0, message
        elif currentVersion > self._currentSceneInfo["MayaVersion"]:
            message = "Base Scene is created with a LOWER Maya version ({0}). Are you sure you want to continue?".format(
                niceVName)
            return -1, message
        elif currentVersion < self._currentSceneInfo["MayaVersion"]:
            message = "Base Scene is created with a HIGHER Maya version ({0}). Are you sure you want to continue?".format(
                niceVName)
            return -1, message

    def isSceneModified(self):
        """Checks the currently open scene saved or not"""
        logger.debug("Func: isSceneModified")
        return self._isSceneModified()

    def saveSimple(self):
        """Save the currently open file"""
        logger.debug("Func: saveSimple")
        # pm.saveFile()
        # cmds.file(save=True)
        self._save()

    def getFormatsAndCodecs(self):
        """Returns the codecs which can be used in current workstation"""
        logger.debug("Func: getFormatsAndCodecs")
        formatList = cmds.playblast(query=True, format=True)
        codecsDictionary = dict(
            (item, mel.eval('playblast -format "{0}" -q -compression;'.format(item))) for item in formatList)
        return codecsDictionary

    def preSaveChecklist(self):
        """Checks the scene for inconsistencies"""
        checklist = []

        # check Fps
        fpsDict = {"game": 15, "film": 24, "pal": 25, "ntsc": 30, "show": 48, "palf": 50, "ntscf": 60}
        fpsValue_setting = self.getFPS()
        fpsName_current = cmds.currentUnit(query=True, time=True)
        fpsValue_current = fpsDict[fpsName_current]

        if fpsValue_setting is not fpsValue_current:
            msg = "FPS values are not matching with the project settings.\n Project FPS => {0}\n scene FPS => {1}\nDo you want to continue?".format(fpsValue_setting, fpsValue_current)
            checklist.append(msg)

        return checklist

    def _exception(self, code, msg, *args, **kwargs):
        """OVERRIDEN METHOD"""
        cmds.confirmDialog(title=self.errorCodeDict[code], message=msg, button=['Ok'])
        if (200 >= code < 210):
            raise Exception(code, msg)

    def _question(self, msg, *args, **kwargs):
        """OVERRIDEN METHOD"""
        state = cmds.confirmDialog( title='Manager Question', message=msg, button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
        if state == "Yes":
            return True
        else:
            return False

    def _info(self, msg, *args, **kwargs):
        """OVERRIDEN METHOD"""
        cmds.confirmDialog(title='Info', message=msg)

    def _inputDir(self):
        """OVERRIDEN METHOD"""
        # Qt File dialog is preferred because it is faster
        inputDir = QtWidgets.QFileDialog.getExistingDirectory()
        return os.path.normpath(inputDir)

    def _getTimelineRanges(self):
        # TODO : Make sure the time ranges are INTEGERS
        R_ast = cmds.playbackOptions(q=True, ast=True)
        R_min = cmds.playbackOptions(q=True, min=True)
        R_max = cmds.playbackOptions(q=True, max=True)
        R_aet = cmds.playbackOptions(q=True, aet=True)
        return [R_ast, R_min, R_max, R_aet]

    def _setTimelineRanges(self, rangeList):
        """Sets the timeline ranges [AnimationStart, Min, Max, AnimationEnd]"""
        # TODO : Make sure the time ranges are INTEGERS
        cmds.playbackOptions(ast=rangeList[0], min=rangeList[1], max=rangeList[2], aet=rangeList[3])


    def _createCallbacks(self, handler, parent):
        logger.debug("Func: _createCallbacks")
        callbackIDList=[]
        callbackIDList.append(cmds.scriptJob(e=["workspaceChanged", "%s.callbackRefresh()" % handler], replacePrevious=True, parent=parent))
        return callbackIDList

    def _killCallbacks(self, callbackIDList):
        logger.debug("Func: _killCallbacks")
        for x in callbackIDList:
            if cmds.scriptJob(ex=x):
                cmds.scriptJob(kill=x)

    def backwardcompatibility(self):
        """
        This function checks for the old database structure and creates a copy with the new structure
        :return: None
        """
        logger.debug("Func: backwardcompatibility")
        def recursive_overwrite(src, dest, ignore=None):
            if os.path.isdir(src):
                if not os.path.isdir(dest):
                    os.makedirs(dest)
                files = os.listdir(src)
                if ignore is not None:
                    ignored = ignore(src, files)
                else:
                    ignored = set()
                for f in files:
                    if f not in ignored:
                        recursive_overwrite(os.path.join(src, f),
                                            os.path.join(dest, f),
                                            ignore)
            else:
                shutil.copyfile(src, dest)

        old_dbDir = os.path.normpath(os.path.join(self._pathsDict["projectDir"], "data", "SMdata"))
        bck_dbDir = os.path.normpath(os.path.join(self._pathsDict["projectDir"], "data", "SMdata_oldVersion"))
        new_dbDir = self._pathsDict["databaseDir"]
        if os.path.isdir(bck_dbDir):
            logger.info("Old database backuped before. Returning without doing any modification")
            return
        if os.path.isdir(old_dbDir):

            recursive_overwrite(old_dbDir, new_dbDir)
            logger.info("All old database contents copied to the new structure folder => %s" % self._pathsDict["databaseDir"])

            oldCategories = ["Model", "Shading", "Rig", "Layout", "Animation", "Render", "Other"]

            # dump the category file
            self._dumpJson(oldCategories, os.path.join(self._pathsDict["databaseDir"], "categoriesMaya.json"))
            for category in oldCategories:
                categoryDBpath = os.path.normpath(os.path.join(new_dbDir, category))
                if os.path.isdir(categoryDBpath):
                    jsonFiles = [y for x in os.walk(categoryDBpath) for y in glob(os.path.join(x[0], '*.json'))]
                    for file in jsonFiles:
                        fileData = self._loadJson(file)
                        # figure out the subproject
                        fileData["ID"] = fileData["ID"].replace("SceneManager", "SmMaya")
                        path = fileData["Path"]
                        name = fileData["Name"]
                        cate = fileData["Category"]
                        parts = path.split("\\")
                        diff = list(set(parts) - set([name, cate, "scenes"]))
                        if diff:
                            fileData["SubProject"] = diff[0]
                        else:
                            fileData["SubProject"] = "None"
                        newVersions = []
                        for vers in fileData["Versions"]:
                            try:
                                thumb = vers[5].replace("data\\SMdata", "smDatabase\\mayaDB") # relative thumbnail path
                            except IndexError:
                                thumb = ""
                            versDict = {"RelativePath": vers[0],
                                        "Note": vers[1],
                                        "User": vers[2],
                                        "Workstation": vers[3],
                                        "Preview": vers[4],
                                        "Thumb": thumb}

                            for key in versDict["Preview"].keys(): # Playblast dictionary
                                versDict["Preview"][key] = versDict["Preview"][key].replace("data\\SMdata", "smDatabase\\mayaDB")

                            newVersions.append(versDict)
                        fileData["Versions"] = newVersions
                        self._dumpJson(fileData, file)
            logger.info("Database preview and thumbnail paths are fixed")
            try:
                os.rename(old_dbDir, bck_dbDir)
                logger.info("Old database folder renamed to 'SMdata_oldVersion'")
            except WindowsError:
                logger.warning("Cannot rename the old database folder because of windows bullshit")

class MainUI(baseUI):
    def __init__(self, callback=None):
        super(MainUI, self).__init__()

        self.manager = MayaManager()
        problem, msg = self.manager._checkRequirements()
        if problem:
            self.close()
            self.deleteLater()

        self.callbackIDList=[]
        if self.isCallback:
            self.callbackIDList = self.manager._createCallbacks(self.isCallback, self.windowName)

        self.buildUI()
        self.initMainUI(newborn=True)
        self.extraMenus()
        self.modify()

    def modify(self):
        # self.mIconPixmap = QtGui.QPixmap(os.path.join(self.manager.getIconsDir(), "iconMaya.png"))
        self.mIconPixmap = QtGui.QPixmap(":/icons/CSS/rc/iconMaya.png")
        self.managerIcon_label.setPixmap(self.mIconPixmap)
        # idk why this became necessary for houdini..

    def closeEvent(self, event):
        if self.isCallback:
            self.manager._killCallbacks(self.callbackIDList)

    def extraMenus(self):
        imanager = QtWidgets.QAction("&Image Manager", self)
        self.toolsMenu.addAction(imanager)
        imanager.triggered.connect(ImMaya.MainUI)

    def onCreatePreview(self):
        takePreview_Dialog = QtWidgets.QDialog(parent=self)
        takePreview_Dialog.resize(150, 180)
        takePreview_Dialog.setWindowTitle(("Select Preview Camera"))
        takePreview_Dialog.setFocus()

        masterLayout = QtWidgets.QVBoxLayout(takePreview_Dialog)
        takePreview_Dialog.setLayout(masterLayout)
        selectionLayout = QtWidgets.QVBoxLayout()
        masterLayout.addLayout(selectionLayout)

        active_rbtn = QtWidgets.QRadioButton()
        active_rbtn.setText("Active View")
        active_rbtn.setChecked(True)
        sequencer_rbtn = QtWidgets.QRadioButton()
        sequencer_rbtn.setText("Sequencer")
        select_rbtn = QtWidgets.QRadioButton()
        select_rbtn.setText("Select")

        buttonGroup = QtWidgets.QButtonGroup()
        buttonGroup.addButton(active_rbtn)
        buttonGroup.addButton(sequencer_rbtn)
        buttonGroup.addButton(select_rbtn)

        select_combo = QtWidgets.QComboBox()
        select_combo.addItems(self.manager._getCameras())
        select_combo.setEnabled(False)

        selectionLayout.addWidget(active_rbtn)
        selectionLayout.addWidget(sequencer_rbtn)
        selectionLayout.addWidget(select_rbtn)
        selectionLayout.addWidget(select_combo)

        execute_btn = QtWidgets.QPushButton()
        execute_btn.setText("Take Preview")

        masterLayout.addWidget(execute_btn)

        def rbtnSwitch():
            select_combo.setEnabled(select_rbtn.isChecked())

        def takePreview():
            if active_rbtn.isChecked():
                self.statusBar().showMessage("Creating Preview...")
                self.manager.createPreview()
                self.statusBar().showMessage("Status | Idle")

            if sequencer_rbtn.isChecked():
                self.statusBar().showMessage("Creating Preview from sequencer...")
                self.manager.createPreview(forceSequencer=True)
                self.statusBar().showMessage("Status | Idle")

            if select_rbtn.isChecked():
                self.statusBar().showMessage("Creating Preview from sequencer...")
                self.manager.createPreview(previewCam=select_combo.currentText())
                self.statusBar().showMessage("Status | Idle")

        ## -------
        ## SIGNALS
        ## -------

        active_rbtn.toggled.connect(rbtnSwitch)
        sequencer_rbtn.toggled.connect(rbtnSwitch)
        select_rbtn.toggled.connect(rbtnSwitch)

        execute_btn.clicked.connect(takePreview)

        takePreview_Dialog.show()





