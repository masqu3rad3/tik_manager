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
import datetime
import socket
import sys, os
# import shutil

import __pyinstallerPathFix

# Set the force pyqt environment variable to tell the other modulea not to use Qt.py module
os.environ["FORCE_QT5"]="1"
os.environ["PS_APP"]="1"

from PyQt5 import QtWidgets, QtCore, QtGui

from SmRoot import RootManager
# from tik_manager.coreFunctions.coreFunctions_PS import PsCoreFunctions
from coreFunctions.coreFunctions_PS import PsCoreFunctions

from SmUIRoot import MainUI as baseUI

# import tik_manager._version as _version
import _version
# import subprocess

# from win32com.client import Dispatch
# import comtypes.client as ct
# import win32gui

# import pprint
import logging

## DO NOT REMOVE THIS:
import tik_manager.iconsSource as icons
## DO NOT REMOVE THIS:

__author__ = "Arda Kutlu"
__copyright__ = "Copyright 2018, Scene Manager for Photoshop"
__credits__ = []
__license__ = "GPL"
__maintainer__ = "Arda Kutlu"
__email__ = "ardakutlu@gmail.com"
__status__ = "Development"

SM_Version = "Scene Manager Photoshop v%s" %_version.__version__

logging.basicConfig()
logger = logging.getLogger('smPhotoshop')
logger.setLevel(logging.WARNING)

class PsManager(RootManager, PsCoreFunctions):
    def __init__(self):
        super(PsManager, self).__init__()
        # hard coded format dictionary to pass the format info to cmds
        self.formatDict = {"psd": "PSD", "psb": "PSB"}
        # self.exportFormats = ["png", "jpg", "exr", "tif", "tga", "psd", "bmp"]
        self.exportFormats8Bit =["png", "jpg", "tif", "tga", "bmp", "psd"]
        self.exportFormats16Bit =["png", "jpg", "tif", "psd"]
        self.exportFormats32Bit =["exr", "tif", "hdr", "psd"]
        self.swName = "Photoshop"
        self.init_paths(self.swName)
        self.init_database()
        self.textureTypes = self._sceneManagerDefaults["exportTextureTypes"]
        self.psApp = self.comLink()


    def getSceneFile(self):
        # """This method must be overridden to return the full scene path ('' for unsaved) of current scene"""
        logger.debug("Func: getSceneFile")
        return self._getSceneFile()

    def getFormatOptions(self):
        """returns the format options according to the bit depth of active document"""
        try:
            activeDocument = self.psApp.Application.ActiveDocument
            bitDepth = activeDocument.bitsPerChannel
        except:
            return []

        if bitDepth == 8:
            return self.exportFormats8Bit
        if bitDepth == 16:
            return self.exportFormats16Bit
        if bitDepth == 32:
            return self.exportFormats32Bit



    def saveBaseScene(self, categoryName, baseName, subProjectIndex=0, makeReference=False, versionNotes="", sceneFormat="psd", *args, **kwargs):
        """
        Saves the PS document with formatted name and creates a json file for the scene
        Args:
            category: (String) Category if the scene. Valid categories are 'Model', 'Animation', 'Rig', 'Shading', 'Other'
            baseName: (String) Base name of the document. Eg. 'initialConcept', 'CharacterA', 'BookDesign' etc...
            subProject: (Integer) The scene will be saved under the sub-project according to the given integer value. The 'self.subProjectList' will be
                searched with that integer.
            makeReference: (Boolean) This has no effect, needed for compatibility issues.
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

        # sceneName = "{0}_{1}_{2}_v{3}".format(baseName, categoryName, self._usersDict[self.currentUser], str(version).zfill(3))
        sceneFile = os.path.join(shotPath, "{0}.{1}".format(sceneName, sceneFormat))
        ## relativity update
        relSceneFile = os.path.relpath(sceneFile, start=projectPath)

        openDocs = self.psApp.Application.Documents
        if openDocs.Count == 0:
            activeDocument = self.psApp.Documents.Add(2048, 2048, 72)
        else:
            activeDocument = self.psApp.Application.ActiveDocument
        self._saveAs(sceneFile, format=sceneFormat)
        # openDocs = self.psApp.Application.Documents
        # if openDocs.Count == 0:
        #     activeDocument = self.psApp.Documents.Add(2048, 2048, 72)
        # else:
        #     activeDocument = self.psApp.Application.ActiveDocument
        #
        # if sceneFormat == "psd":
        #     # PhotoshopSaveOptions=ct.CreateObject("Photoshop.PhotoshopSaveOptions")
        #     # PhotoshopSaveOptions.AlphaChannels = True
        #     # PhotoshopSaveOptions.Annotations = True
        #     # PhotoshopSaveOptions.Layers = True
        #     # PhotoshopSaveOptions.SpotColors = True
        #     # activeDocument.SaveAs(sceneFile, PhotoshopSaveOptions, False)
        #
        #     desc19 = Dispatch("Photoshop.ActionDescriptor")
        #     desc20 = Dispatch("Photoshop.ActionDescriptor")
        #     desc20.PutBoolean(self.psApp.StringIDToTypeID('maximizeCompatibility'), True)
        #     desc19.PutObject(
        #         self.psApp.CharIDToTypeID('As  '), self.psApp.CharIDToTypeID('Pht3'), desc20)
        #     desc19.PutPath(self.psApp.CharIDToTypeID('In  '), sceneFile)
        #     desc19.PutBoolean(self.psApp.CharIDToTypeID('LwCs'), True)
        #     self.psApp.ExecuteAction(self.psApp.CharIDToTypeID('save'), desc19, 3)
        #
        # else:
        #
        #     desc19 = Dispatch("Photoshop.ActionDescriptor")
        #     desc20 = Dispatch("Photoshop.ActionDescriptor")
        #     desc20.PutBoolean(self.psApp.StringIDToTypeID('maximizeCompatibility'), True)
        #
        #     desc19.PutObject(
        #         self.psApp.CharIDToTypeID('As  '), self.psApp.CharIDToTypeID('Pht8'), desc20)
        #     desc19.PutPath(self.psApp.CharIDToTypeID('In  '), sceneFile)
        #     desc19.PutBoolean(self.psApp.CharIDToTypeID('LwCs'), True)
        #     self.psApp.ExecuteAction(self.psApp.CharIDToTypeID('save'), desc19, 3)

        thumbPath = self.createThumbnail(dbPath=jsonFile, versionInt=version)

        jsonInfo = {}


        jsonInfo["ReferenceFile"] = None
        jsonInfo["ReferencedVersion"] = None

        jsonInfo["ID"] = "SmNukeV02_sceneFile"
        jsonInfo["PSVersion"] = self.psApp.Version
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
             "Ranges": ""
             }
        ]

        jsonInfo["SubProject"] = self._subProjectsList[subProjectIndex]
        self._dumpJson(jsonInfo, jsonFile)
        return [0, ""]

    def saveVersion(self, makeReference=False, versionNotes="", sceneFormat="psd", *args, **kwargs):
        """
        Saves a version for the predefined scene. The scene json file must be present at the /data/[Category] folder.
        Args:
            makeReference: (Boolean) ** Does nothing, consistency purposes
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

        sceneInfo = self.getOpenSceneInfo()

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

            # sceneName = "{0}_{1}_{2}_v{3}".format(jsonInfo["Name"], jsonInfo["Category"], self._usersDict[self.currentUser], str(currentVersion).zfill(3))
            relSceneFile = os.path.join(jsonInfo["Path"], "{0}.{1}".format(sceneName, sceneFormat))

            sceneFile = os.path.join(sceneInfo["projectPath"], relSceneFile)

            # -- Save PSD
            self._saveAs(sceneFile, format=sceneFormat)
            # if sceneFormat == "psd":
            #     # activeDocument = psApp.Application.ActiveDocument
            #     # PhotoshopSaveOptions = ct.CreateObject("Photoshop.PhotoshopSaveOptions")
            #     # PhotoshopSaveOptions.AlphaChannels = True
            #     # PhotoshopSaveOptions.Annotations = True
            #     # PhotoshopSaveOptions.Layers = True
            #     # PhotoshopSaveOptions.SpotColors = True
            #     # activeDocument.SaveAs(sceneFile, PhotoshopSaveOptions, False)
            #
            #     desc19 = Dispatch("Photoshop.ActionDescriptor")
            #     desc20 = Dispatch("Photoshop.ActionDescriptor")
            #     desc20.PutBoolean(self.psApp.StringIDToTypeID('maximizeCompatibility'), True)
            #
            #     desc19.PutObject(
            #         self.psApp.CharIDToTypeID('As  '), self.psApp.CharIDToTypeID('Pht3'), desc20)
            #     desc19.PutPath(self.psApp.CharIDToTypeID('In  '), sceneFile)
            #     desc19.PutBoolean(self.psApp.CharIDToTypeID('LwCs'), True)
            #     self.psApp.ExecuteAction(self.psApp.CharIDToTypeID('save'), desc19, 3)
            #
            # else:
            #
            #     desc19 = Dispatch("Photoshop.ActionDescriptor")
            #     desc20 = Dispatch("Photoshop.ActionDescriptor")
            #     desc20.PutBoolean(self.psApp.StringIDToTypeID('maximizeCompatibility'), True)
            #
            #     desc19.PutObject(
            #         self.psApp.CharIDToTypeID('As  '), self.psApp.CharIDToTypeID('Pht8'), desc20)
            #     desc19.PutPath(self.psApp.CharIDToTypeID('In  '), sceneFile)
            #     desc19.PutBoolean(self.psApp.CharIDToTypeID('LwCs'), True)
            #     self.psApp.ExecuteAction(self.psApp.CharIDToTypeID('save'), desc19, 3)

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
                 "Ranges": ""
                 }
                )

            self._dumpJson(jsonInfo, jsonFile)
        else:
            msg = "This is not a base scene (Json file cannot be found)"
            self._exception(360, msg)
            return -1, msg
        return jsonInfo

    # def getTextureVersions(self, baseSceneName):
    #
    #     #resolve the available texture versions and return the list
    #
    #     pass

    def exportSourceimage(self, extension="jpg", textureType="diffuse", asNextRevision=True, revisionNumber=1):
        # ???
        # if extension not in self.exportFormats:
        #     msg = "Format is not valid. Valid formats are:\n\n %s" %self.exportFormats
        #     self._exception(101, msg)
        #     return -1, msg

        # resolve path as <sourceImages folder>/<baseName>.<format>
        sceneName = self.getSceneFile()
        if not sceneName:
            msg = "Current document is not a Base Scene File.\n\nSave it as a Base Scene first."
            self._exception(360, msg)
            return False

        sceneInfo = self.getOpenSceneInfo()
        if not sceneInfo:
            msg = "Current document is not a Base Scene File.\n\nSave it as a Base Scene first."
            self._exception(360, msg)
            return False

        # TEMPLATE
        # --------
        # <sourceImagesPath>/<category>/<subProject(ifAny)/<baseName>_<version>/<baseName>_<type>_<revision>.<extension>

        baseName = sceneInfo["shotName"]
        version = sceneInfo["version"]
        category = sceneInfo["category"]
        subProject = "" if sceneInfo["subProject"] == "None" else sceneInfo["subProject"]
        projectPath = sceneInfo["projectPath"]
        sourceimagesPath = self._folderCheck(os.path.join(projectPath, "sourceimages"))

        # resolve export folder
        exportFolderPath = self._folderCheck(os.path.join(sourceimagesPath, category, subProject, "%s_%s" %(baseName, version)))

        if asNextRevision:
            # get all files in destination folder
            wholeList = os.listdir(exportFolderPath)
            # filter the files related with the particular export
            revisionHistory = list(filter(lambda x: x.startswith("{0}_{1}_".format(baseName, textureType)), wholeList))

            def tryGetNumber(xString):
                try:
                    number = int(os.path.splitext(xString)[0][-3:])
                    return number
                except ValueError:
                    return 0

            # find the maximum revision number and increment it by 1
            revisionNumberList = (map(lambda x: tryGetNumber(x), revisionHistory))
            revisionNumber = 1 if len(revisionNumberList) == 0 else max(revisionNumberList)+1

        fileName = "{0}_{1}_r{2}.{3}".format(baseName, textureType, str(revisionNumber).zfill(3), extension)

        filePath = os.path.join(exportFolderPath, fileName)

        if os.path.isfile(filePath):
            header = "The following file will be overwritten if you continue:\n %s" %fileName
            msg = "Choose Yes to overwrite file and continue"
            title = "Are you Sure?"
            if not self._question(header=header, msg=msg, title=title):
                return False
            else:
                pass

        if extension == "jpg":
            self._exportJPG(filePath)

        if extension == "png":
            self._exportPNG(filePath)

        if extension == "bmp":
            self._exportBMP(filePath)

        if extension == "tga":
            self._exportTGA(filePath)

        if extension == "psd":
            self._exportPSD(filePath)

        if extension == "tif":
            self._exportTIF(filePath)

        if extension == "exr":
            self._exportEXR(filePath)

        if extension == "hdr":
            self._exportHDR(filePath)

        # activeDocument = self.psApp.Application.ActiveDocument
        # if extension == "jpg":
        #     saveOPT=Dispatch("Photoshop.JPEGSaveOptions")
        #     saveOPT.EmbedColorProfile = True
        #     saveOPT.FormatOptions = 1 # => psStandardBaseline
        #     saveOPT.Matte = 1 # => No Matte
        #     saveOPT.Quality = 12
        #     activeDocument.SaveAs(filePath, saveOPT, True)
        # if extension == "png":
        #     saveOPT=Dispatch("Photoshop.PNGSaveOptions")
        #     activeDocument.SaveAs(filePath, saveOPT, True)
        # if extension == "bmp":
        #     saveOPT=Dispatch("Photoshop.BMPSaveOptions")
        #     activeDocument.SaveAs(filePath, saveOPT, True)
        # if extension == "tga":
        #     saveOPT=Dispatch("Photoshop.TargaSaveOptions")
        #     saveOPT.Resolution=32
        #     saveOPT.AlphaChannels=True
        #     saveOPT.RLECompression=True
        #     activeDocument.SaveAs(filePath, saveOPT, True)
        # if extension == "psd":
        #     saveOPT=Dispatch("Photoshop.PhotoshopSaveOptions")
        #     saveOPT.AlphaChannels = True
        #     saveOPT.Annotations = True
        #     saveOPT.Layers = True
        #     saveOPT.SpotColors = True
        #     activeDocument.SaveAs(filePath, saveOPT, True)
        # if extension == "tif":
        #     saveOPT=Dispatch("Photoshop.TiffSaveOptions")
        #     saveOPT.AlphaChannels = True
        #     saveOPT.EmbedColorProfile = True
        #     saveOPT.Layers = False
        #     activeDocument.SaveAs(filePath, saveOPT, True)
        # if extension == "exr":
        #     idsave = self.psApp.CharIDToTypeID("save")
        #     desc182 = Dispatch("Photoshop.ActionDescriptor")
        #     idAs = self.psApp.CharIDToTypeID("As  ")
        #     desc183 = Dispatch("Photoshop.ActionDescriptor")
        #     idBtDp = self.psApp.CharIDToTypeID("BtDp")
        #     desc183.PutInteger(idBtDp, 16);
        #     idCmpr = self.psApp.CharIDToTypeID("Cmpr")
        #     desc183.PutInteger(idCmpr, 1)
        #     idAChn = self.psApp.CharIDToTypeID("AChn")
        #     desc183.PutInteger(idAChn, 0)
        #     idEXRf = self.psApp.CharIDToTypeID("EXRf")
        #     desc182.PutObject(idAs, idEXRf, desc183)
        #     idIn = self.psApp.CharIDToTypeID("In  ")
        #     desc182.PutPath(idIn, (filePath))
        #     idDocI = self.psApp.CharIDToTypeID("DocI")
        #     desc182.PutInteger(idDocI, 340)
        #     idCpy = self.psApp.CharIDToTypeID("Cpy ")
        #     desc182.PutBoolean(idCpy, True)
        #     idsaveStage = self.psApp.StringIDToTypeID("saveStage")
        #     idsaveStageType = self.psApp.StringIDToTypeID("saveStageType")
        #     idsaveSucceeded = self.psApp.StringIDToTypeID("saveSucceeded")
        #     desc182.PutEnumerated(idsaveStage, idsaveStageType, idsaveSucceeded)
        #     self.psApp.ExecuteAction(idsave, desc182, 3)
        #
        # if extension == "hdr":
        #     idsave = self.psApp.CharIDToTypeID("save")
        #     desc419 = Dispatch("Photoshop.ActionDescriptor")
        #     idAs = self.psApp.CharIDToTypeID("As  ")
        #     desc419.PutString(idAs, """Radiance""")
        #     idIn = self.psApp.CharIDToTypeID("In  ")
        #     desc419.PutPath(idIn, (filePath))
        #     idDocI = self.psApp.CharIDToTypeID("DocI")
        #     desc419.PutInteger(idDocI, 333)
        #     idCpy = self.psApp.CharIDToTypeID("Cpy ")
        #     desc419.PutBoolean(idCpy, True)
        #     idsaveStage = self.psApp.StringIDToTypeID("saveStage")
        #     idsaveStageType = self.psApp.StringIDToTypeID("saveStageType")
        #     idsaveSucceeded = self.psApp.StringIDToTypeID("saveSucceeded")
        #     desc419.PutEnumerated(idsaveStage, idsaveStageType, idsaveSucceeded)
        #     self.psApp.ExecuteAction(idsave, desc419, 3)

        success = os.path.isfile(filePath)
        if success:
            return filePath
        else:
            self._exception(202, "Unknown Error")
            return False


    def loadBaseScene(self, force=False):
        """Loads the scene at cursor position"""
        logger.debug("Func: loadBaseScene")
        relSceneFile = self._currentSceneInfo["Versions"][self._currentVersionIndex-1]["RelativePath"]
        absSceneFile = os.path.join(self.projectDir, relSceneFile)
        if os.path.isfile(absSceneFile):
            # self.psApp.Open(absSceneFile)
            self._load(absSceneFile)
            return 0
        else:
            msg = "File in Scene Manager database doesnt exist"
            self._exception(201, msg)
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

        # create a thumbnail using playblast
        thumbDir = os.path.split(thumbPath)[0]
        if os.path.exists(thumbDir):
            self.psApp.Preferences.RulerUnits = 1
            activeDocument = self.psApp.Application.ActiveDocument
            dupDocument = activeDocument.Duplicate("thumbnailCopy", True)
            dupDocument.bitsPerChannel = 8
            oWidth = 221
            oHeight = 124
            ratio = float(dupDocument.Width) / float(dupDocument.Height)
            if ratio <= 1.782:
                new_width = oHeight * ratio
                new_height = oHeight
            else:
                new_width = oWidth
                new_height = oWidth / ratio
            dupDocument.ResizeImage(new_width, new_height)
            dupDocument.ResizeCanvas(oWidth, oHeight)

            self._exportJPG(thumbPath, quality=6)
            # jpgSaveOptions = Dispatch("Photoshop.JPEGSaveOptions")
            # jpgSaveOptions.EmbedColorProfile = True
            # jpgSaveOptions.FormatOptions = 1  # => psStandardBaseline
            # jpgSaveOptions.Matte = 1  # => No Matte
            # jpgSaveOptions.Quality = 6
            # dupDocument.SaveAs(thumbPath, jpgSaveOptions, True)
            dupDocument.Close(2)  # 2 means without saving
        else:
            print ("something went wrong with thumbnail. Skipping thumbnail")
            return ""
        return relThumbPath

    def preSaveChecklist(self):
        """Checks the scene for inconsistencies"""
        checklist = []

        # TODO check for something?
        # fpsValue_setting = self.getFPS()
        # fpsValue_current = nuke.root().fps()
        #
        # if fpsValue_setting is not fpsValue_current:
        #     msg = "FPS values are not matching with the project settings.\n Project FPS => {0}\n scene FPS => {1}\nDo you want to continue?".format(fpsValue_setting, fpsValue_current)
        #     checklist.append(msg)

        return checklist

    def compareVersions(self):
        """Compares the versions of current session and database version at cursor position"""
        logger.debug("Func: compareVersions")

        # assumes compatibilty maximized
        return 0, ""

    def isSceneModified(self):
        """Checks the currently open scene saved or not"""
        logger.debug("Func: isSceneModified")
        return self._isSceneModified()

    # def loadCategories(self, filePath=None):
    #     """OVERRIDEN FUNCTION for specific category default of Photoshop"""
    #     logger.debug("Func: loadCategories")
    #
    #     if not filePath:
    #         filePath = self._pathsDict["categoriesFile"]
    #
    #     if os.path.isfile(filePath):
    #         categoriesData = self._loadJson(filePath)
    #         if categoriesData == -2:
    #             return -2
    #     else:
    #         categoriesData = self._sceneManagerDefaults["defaultPSCategories"]
    #         # categoriesData = ["Concept", "Storyboard", "Texture", "Other"]
    #         self._dumpJson(categoriesData, filePath)
    #     return categoriesData





    def _exception(self, code, msg):
        """OVERRIDEN"""

        errorbox = QtWidgets.QMessageBox()
        errorbox.setModal(True)
        errorbox.setText(msg)
        errorbox.setWindowTitle(self.errorCodeDict[code])
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

    # def _question(self, msg):
    #     """OVERRIDEN METHOD"""
    #     state = cmds.confirmDialog( title='Manager Question', message=msg, button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
    #     if state == "Yes":
    #         return True
    #     else:
    #         return False

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

class MainUI(baseUI):
    """Main UI Class. Inherits SmUIRoot.py"""
    def __init__(self):
        super(MainUI, self).__init__()
        # self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.manager = PsManager()
        # self.manager = self._getManager()
        # problem, msg = self.manager._checkRequirements()
        # if problem:
        #     self.close()
        #     self.deleteLater()

        # self.windowName = "Tik Manager Photoshop v%s" %_version.__version__
        # whndl = win32gui.FindWindow(None, "Photoshop.Application")

        # self.setParent(whndl, int(self.winId()))

        self.buildUI()
        self.extraMenus()
        self.modify()
        self.initMainUI(newborn=True)



    def extraMenus(self):
        """Adds extra menu and widgets to the base UI"""
        pass


    def modify(self):
        """Modifications to the base UI"""
        pass
        # make sure load mode is checked and hidden
        self.load_radioButton.setChecked(True)
        self.load_radioButton.setVisible(False)
        self.reference_radioButton.setChecked(False)
        self.reference_radioButton.setVisible(False)

        self.makeReference_pushButton.setVisible(False)
        self.showPreview_pushButton.setVisible(False)

        self.export_pushButton.setVisible(True)
        self.export_pushButton.setText("Export Texture")
        self.export_pushButton.clicked.connect(self.exportSourceUI)

        # self.mIconPixmap = QtWidgets.QPixmap(os.path.join(self.manager.getIconsDir(), "iconPS.png"))
        self.mIconPixmap = QtGui.QPixmap(":/icons/CSS/rc/iconPS.png")
        self.managerIcon_label.setPixmap(self.mIconPixmap)
        #
        # self.baseScene_label.setVisible(False)
        # self.baseScene_lineEdit.setVisible(False)
        #
        # self.createPB.setVisible(False)
        #
        # self.saveVersion_pushButton.setVisible(False)
        # self.saveVersion_fm.setVisible(False)
        # self.saveBaseScene_pushButton.setVisible(False)
        # self.saveBaseScene_fm.setVisible(False)
        # self.scenes_rcItem_0.setVisible(False)
        #
        # self.changeCommonFolder.setVisible(True)
        # self.changeCommonFolder.triggered.connect(self.manager._defineCommonFolder)

    def exportSourceUI(self):
        self.exportTexture_Dialog = QtWidgets.QDialog(parent=self)
        self.exportTexture_Dialog.resize(336, 194)
        self.exportTexture_Dialog.setWindowTitle(("Export Textures"))

        self.verticalLayout = QtWidgets.QVBoxLayout(self.exportTexture_Dialog)

        self.resolvedName_label = QtWidgets.QLabel(self.exportTexture_Dialog)
        self.resolvedName_label.setText(("Resolved File Name"))
        self.resolvedName_label.setWordWrap(True)
        self.verticalLayout.addWidget(self.resolvedName_label)

        self.line = QtWidgets.QFrame(self.exportTexture_Dialog)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.verticalLayout.addWidget(self.line)

        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)
        self.formLayout.setRowWrapPolicy(QtWidgets.QFormLayout.DontWrapRows)
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.formLayout.setFormAlignment(QtCore.Qt.AlignCenter)
        self.formLayout.setSpacing(12)

        self.format_label = QtWidgets.QLabel(self.exportTexture_Dialog)
        self.format_label.setText(("Format:"))
        self.format_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.format_label)

        self.format_layout = QtWidgets.QHBoxLayout()

        self.format_comboBox = QtWidgets.QComboBox(self.exportTexture_Dialog)
        self.format_comboBox.setMinimumSize(QtCore.QSize(60, 16777215))
        self.format_comboBox.setMaximumSize(QtCore.QSize(200, 16777215))
        self.format_comboBox.addItems(self.manager.getFormatOptions())
        self.format_layout.addWidget(self.format_comboBox)

        self.alpha_checkBox = QtWidgets.QCheckBox(self.exportTexture_Dialog)
        self.alpha_checkBox.setText(("Alpha"))
        self.alpha_checkBox.setChecked(True)
        self.format_layout.addWidget(self.alpha_checkBox)

        self.formLayout.setLayout(0, QtWidgets.QFormLayout.FieldRole, self.format_layout)

        self.type_label = QtWidgets.QLabel(self.exportTexture_Dialog)
        self.type_label.setText(("Type:"))
        self.type_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.type_label)

        self.type_layout =  QtWidgets.QHBoxLayout()

        self.type_comboBox = QtWidgets.QComboBox(self.exportTexture_Dialog)
        self.type_comboBox.setMinimumSize(QtCore.QSize(75, 16777215))
        self.type_comboBox.setMaximumSize(QtCore.QSize(200, 16777215))
        self.type_comboBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.type_comboBox.setFrame(True)
        self.type_comboBox.addItems(self.manager.textureTypes)
        self.type_layout.addWidget(self.type_comboBox)

        self.customType_lineEdit = QtWidgets.QLineEdit(self.exportTexture_Dialog)
        self.type_layout.addWidget(self.customType_lineEdit)

        self.formLayout.setLayout(1, QtWidgets.QFormLayout.FieldRole, self.type_layout)

        self.version_label = QtWidgets.QLabel(self.exportTexture_Dialog)
        self.version_label.setText(("Revision:"))
        self.version_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.version_label)

        self.horizontalLayout = QtWidgets.QHBoxLayout()

        version_spinBox = QtWidgets.QSpinBox(self.exportTexture_Dialog)
        version_spinBox.setMaximumSize(QtCore.QSize(50, 16777215))
        version_spinBox.setMinimum(1)
        version_spinBox.setMaximum(999)
        self.horizontalLayout.addWidget(version_spinBox)

        self.incremental_checkBox = QtWidgets.QCheckBox(self.exportTexture_Dialog)
        self.incremental_checkBox.setText(("Use Next Available Revision"))
        self.incremental_checkBox.setChecked(True)
        self.horizontalLayout.addWidget(self.incremental_checkBox)

        self.formLayout.setLayout(2, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout)
        self.verticalLayout.addLayout(self.formLayout)

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        buttonBox = QtWidgets.QDialogButtonBox(self.exportTexture_Dialog)
        buttonBox.setGeometry(QtCore.QRect(20, 250, 220, 32))
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).setMinimumSize(QtCore.QSize(100, 30))
        buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setMinimumSize(QtCore.QSize(100, 30))

        buttonE = buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
        buttonE.setText('Export')
        buttonC = buttonBox.button(QtWidgets.QDialogButtonBox.Cancel)
        buttonC.setText('Cancel')


        self.verticalLayout.addWidget(buttonBox)

        def hideUnhideCustom():
            if self.type_comboBox.currentText() == "Custom":
                self.customType_lineEdit.setHidden(False)
            else:
                self.customType_lineEdit.setHidden(True)
        hideUnhideCustom()

        def enableDisableVersion():
            version_spinBox.setDisabled(self.incremental_checkBox.isChecked())

        enableDisableVersion()

        def exportCommand():
            extension = self.format_comboBox.currentText()
            textureType = self.customType_lineEdit.text() if self.type_comboBox.currentText() == "Custom" else self.type_comboBox.currentText()
            asNextRevision = self.incremental_checkBox.isChecked()
            revisionNumber = version_spinBox.value()
            exportedFilePath = self.manager.exportSourceimage(extension=extension, textureType=textureType, asNextRevision=asNextRevision, revisionNumber=revisionNumber)
            if exportedFilePath:
                successUI("Success", success=True, destPath=exportedFilePath)
            else:
                successUI("Failure", success=False)
            self.exportTexture_Dialog.close()

        def successUI(status, success=True, destPath=None):

            self.msgDialog = QtWidgets.QDialog(parent=self)
            self.msgDialog.setModal(True)
            self.msgDialog.setWindowTitle("Export Successfull")
            self.msgDialog.resize(300, 120)
            layoutMain = QtWidgets.QVBoxLayout()
            self.msgDialog.setLayout(layoutMain)

            infoHeader = QtWidgets.QLabel(status)
            isEnabled = False if status=="Failure" else True

            infoHeader.setProperty("infoHeader", True)
            infoHeader.setProperty("success", success)
            infoHeader.setStyleSheet("")

            layoutMain.addWidget(infoHeader)
            layoutH = QtWidgets.QHBoxLayout()
            layoutMain.addLayout(layoutH)

            openFile = QtWidgets.QPushButton("Open File")
            openFile.setEnabled(isEnabled)
            layoutH.addWidget(openFile)
            openFile.clicked.connect(lambda x: self.manager.showInExplorer(destPath))
            showInExplorer = QtWidgets.QPushButton("Show in Explorer")
            showInExplorer.setEnabled(isEnabled)
            layoutH.addWidget(showInExplorer)
            okButton = QtWidgets.QPushButton("OK")
            layoutH.addWidget(okButton)

            showInExplorer.clicked.connect(lambda x: self.manager.showInExplorer(os.path.split(destPath)[0]))

            okButton.clicked.connect(self.msgDialog.close)

            self.msgDialog.show()

        # SIGNALS
        # -------

        self.type_comboBox.currentIndexChanged.connect(hideUnhideCustom)
        self.incremental_checkBox.toggled.connect(enableDisableVersion)

        buttonC.clicked.connect(self.exportTexture_Dialog.reject)

        buttonE.clicked.connect(exportCommand)
        # buttonE.clicked.connect(self.exportTexture_Dialog.accept)



        self.exportTexture_Dialog.show()




if __name__ == '__main__':
    selfLoc = os.path.dirname(os.path.abspath(__file__))
    app = QtWidgets.QApplication(sys.argv)
    stylesheetFile = os.path.join(selfLoc, "CSS", "tikManager.qss")
    if os.path.isfile(stylesheetFile):
        with open(stylesheetFile, "r") as fh:
            app.setStyleSheet(fh.read())
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "saveVersion":
            window = MainUI().saveAsVersionDialog()
        else:
            print("Argument %s is invalid" %(sys.argv[1]))
    else:
        window = MainUI()
        window.show()
    sys.exit(app.exec_())