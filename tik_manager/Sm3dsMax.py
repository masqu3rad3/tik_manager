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

from SmUIRoot import MainUI as baseUI
from SmRoot import RootManager

import shutil

# import MaxPlus
from MaxPlus import FileManager as fManager
from MaxPlus import PathManager as pManager
from pymxs import runtime as rt

import datetime
import socket
import logging
# from glob import glob

from Qt import QtWidgets, QtCore, QtGui

import _version

# import pprint



__author__ = "Arda Kutlu"
__copyright__ = "Copyright 2018, Scene Manager for 3dsMax Projects"
__credits__ = []
__version__ = "2.0.0"
__license__ = "GPL"
__maintainer__ = "Arda Kutlu"
__email__ = "ardakutlu@gmail.com"
__status__ = "Development"

SM_Version = "Scene Manager 3ds Max v%s" %_version.__version__

logging.basicConfig()
logger = logging.getLogger('sm3dsMax')
logger.setLevel(logging.WARNING)

class MaxCoreFunctions(object):
    def __init__(self):
        super(MaxCoreFunctions, self).__init__()

    def _save(self, *args, **kwargs):
        fManager.Save()

    def _saveAs(self, filePath, format=None, *args, **kwargs):
        fManager.Save(filePath)

    def _load(self, filePath, force=True, *args, **kwargs):
        fManager.Open(filePath)

    def _reference(self, filePath):
        Xrefobjs = rt.getMAXFileObjectNames(filePath)
        rt.xrefs.addNewXRefObject(filePath, Xrefobjs)

    def _import(self, filePath, *args, **kwargs):
        fManager.Merge(filePath)

    def _importObj(self, filePath, importSettings, *args, **kwargs):
        if rt.pluginManager.loadclass(rt.ObjExp):
            # Set OBJ Options
            maxImp_obj = importSettings["objImportMax"]
            iniPath_importSettings = rt.objImp.getIniName()
            rt.setINISetting(iniPath_importSettings, "General", "UseLogging", maxImp_obj["UseLogging"])
            rt.setINISetting(iniPath_importSettings, "General", "ResetScene", maxImp_obj["ResetScene"])
            rt.setINISetting(iniPath_importSettings, "General", "CurrObjColor", maxImp_obj["CurrObjColor"])
            rt.setINISetting(iniPath_importSettings, "General", "MapSearchPath", maxImp_obj["MapSearchPath"])
            rt.setINISetting(iniPath_importSettings, "Objects", "SingleMesh", maxImp_obj["SingleMesh"])
            rt.setINISetting(iniPath_importSettings, "Objects", "AsEditablePoly", maxImp_obj["AsEditablePoly"])
            rt.setINISetting(iniPath_importSettings, "Objects", "Retriangulate", maxImp_obj["Retriangulate"])
            rt.setINISetting(iniPath_importSettings, "Geometry", "FlipZyAxis", maxImp_obj["FlipZyAxis"])
            rt.setINISetting(iniPath_importSettings, "Geometry", "CenterPivots", maxImp_obj["CenterPivots"])
            rt.setINISetting(iniPath_importSettings, "Geometry", "Shapes", maxImp_obj["Shapes"])
            rt.setINISetting(iniPath_importSettings, "Geometry", "TextureCoords", maxImp_obj["TextureCoords"])
            rt.setINISetting(iniPath_importSettings, "Geometry", "SmoothingGroups", maxImp_obj["SmoothingGroups"])
            rt.setINISetting(iniPath_importSettings, "Geometry", "NormalsType", maxImp_obj["NormalsType"])
            rt.setINISetting(iniPath_importSettings, "Geometry", "SmoothAngle", maxImp_obj["SmoothAngle"])
            rt.setINISetting(iniPath_importSettings, "Geometry", "FlipNormals", maxImp_obj["FlipNormals"])
            rt.setINISetting(iniPath_importSettings, "Units/Scale", "Convert", maxImp_obj["Convert"])
            rt.setINISetting(iniPath_importSettings, "Units/Scale", "ConvertFrom", maxImp_obj["ConvertFrom"])
            rt.setINISetting(iniPath_importSettings, "Units/Scale", "ObjScale", maxImp_obj["ObjScale"])
            rt.setINISetting(iniPath_importSettings, "Material", "UniqueWireColor", maxImp_obj["UniqueWireColor"])
            rt.setINISetting(iniPath_importSettings, "Material", "ImportMaterials", maxImp_obj["ImportMaterials"])
            rt.setINISetting(iniPath_importSettings, "Material", "UseMatPrefix", maxImp_obj["UseMatPrefix"])
            rt.setINISetting(iniPath_importSettings, "Material", "DefaultBump", maxImp_obj["DefaultBump"])
            rt.setINISetting(iniPath_importSettings, "Material", "ForceBlackAmbient", maxImp_obj["ForceBlackAmbient"])
            rt.setINISetting(iniPath_importSettings, "Material", "ImportIntoMatEditor", maxImp_obj["ImportIntoMatEditor"])
            rt.setINISetting(iniPath_importSettings, "Material", "ShowMapsInViewport", maxImp_obj["ShowMapsInViewport"])
            rt.setINISetting(iniPath_importSettings, "Material", "CopyMapsToProj", maxImp_obj["CopyMapsToProj"])
            rt.setINISetting(iniPath_importSettings, "Material", "OverwriteImages", maxImp_obj["OverwriteImages"])
            rt.importFile(filePath, rt.Name("NoPrompt"), using=rt.ObjImp)
            return True
        else:
            msg = "OBJ Plugin cannot be initialized. Skipping import"
            rt.messageBox(msg, title='Info')
            return False


    def _importAlembic(self, filePath, importSettings, *args, **kwargs):
        # Set Alembic Options according to the Max Version:
        v = rt.maxVersion()[0]
        maxImp_abc = importSettings["alembicImportMax"]

        if v > 17000:  # Alembic export is not supported before 3ds Max 2016
            if rt.pluginManager.loadclass(rt.Alembic_Export):
                if 18000 <= v < 21000:  # between versions 2016 - 2018
                    rt.AlembicImport.CoordinateSystem = rt.Name(maxImp_abc["CoordinateSystem"])
                    rt.AlembicImport.CacheTimeRange = rt.Name(maxImp_abc["AnimTimeRange"])
                    rt.AlembicImport.ShapeName = maxImp_abc["ShapeSuffix"]
                    rt.AlembicImport.ImportToRoot = maxImp_abc["ImportToRoot"]
                    rt.AlembicImport.FitTimeRange = maxImp_abc["FitTimeRange"]
                    rt.AlembicImport.SetStartTime = maxImp_abc["SetStartTime"]
                    # rt.AlembicExport.StepFrameTime = exportSettings["StepFrameTime"]

                elif v >= 21000:  # version 2019 and up
                    rt.AlembicImport.CoordinateSystem = rt.Name(maxImp_abc["CoordinateSystem"])
                    rt.AlembicImport.AnimTimeRange = rt.Name(maxImp_abc["AnimTimeRange"])
                    rt.AlembicImport.ShapeSuffix = maxImp_abc["ShapeSuffix"]
                    rt.AlembicImport.SamplesPerFrame = maxImp_abc["SamplesPerFrame"]
                    rt.AlembicImport.Hidden = maxImp_abc["Hidden"]
                    rt.AlembicImport.UVs = maxImp_abc["UVs"]
                    rt.AlembicImport.Normals = maxImp_abc["Normals"]
                    rt.AlembicImport.VertexColors = maxImp_abc["VertexColors"]
                    rt.AlembicImport.ExtraChannels = maxImp_abc["ExtraChannels"]
                    rt.AlembicImport.Velocity = maxImp_abc["Velocity"]
                    rt.AlembicImport.MaterialIDs = maxImp_abc["MaterialIDs"]
                    rt.AlembicImport.Visibility = maxImp_abc["Visibility"]
                    rt.AlembicImport.LayerName = maxImp_abc["LayerName"]
                    rt.AlembicImport.MaterialName = maxImp_abc["MaterialName"]
                    rt.AlembicImport.ObjectID = maxImp_abc["ObjectID"]
                    rt.AlembicImport.CustomAttributes = maxImp_abc["CustomAttributes"]

                # Export
                rt.importFile(filePath, rt.Name("NoPrompt"), using=rt.Alembic_Import)
                return True

            else:
                rt.messageBox("Alembic Plugin cannot be initialized. Skipping", title="Alembic not supported")
                return False
        else:
            rt.messageBox("There is no alembic support for this version. Skipping", title="Alembic not supported")
            return False

    def _importFbx(self, filePath, importSettings, *args, **kwargs):
        if rt.pluginManager.loadclass(rt.FBXIMP):
            maxImp_fbx = importSettings["fbxImportMax"]
            # Set FBX Options
            for item in maxImp_fbx.items():
                rt.FBXImporterSetParam(rt.Name(item[0]), item[1])
            rt.FBXImporterSetParam(rt.Name("UpAxis"), "Z")
            try:
                rt.importFile(filePath, rt.Name("NoPrompt"), using=rt.FBXIMP)
                return True
            except:
                msg = "Cannot import FBX file for unknown reason. Skipping import"
                rt.messageBox(msg, title='Info')
                return False
        else:
            msg = "FBX Plugin cannot be initialized. Skipping import"
            rt.messageBox(msg, title='Info')
            return False

    def _exportObj(self, filePath, exportSettings, exportSelected=True):
        """
        Exports wavefront Obj file
        Args:
            filePath: (String) Absolute File path for exported file
            exportSettings: (Dictionary) settings file (see getExportSettings)
            exportSelected: (Boolean) If True, exports only currently selected objects, else whole scene. Default True

        Returns: (Boolean) True for success False for failure

        """
        if rt.pluginManager.loadclass(rt.ObjExp):
            maxExp_obj = exportSettings["objExportMax"]
            # Set OBJ Options
            iniPath_exportSettings = rt.objExp.getIniName()
            rt.setINISetting(iniPath_exportSettings, "Geometry", "FlipZyAxis", maxExp_obj["FlipZyAxis"])
            rt.setINISetting(iniPath_exportSettings, "Geometry", "Shapes", maxExp_obj["Shapes"])
            rt.setINISetting(iniPath_exportSettings, "Geometry", "ExportHiddenObjects",
                             exportSettings["ExportHiddenObjects"])
            rt.setINISetting(iniPath_exportSettings, "Geometry", "FaceType", maxExp_obj["FaceType"])
            rt.setINISetting(iniPath_exportSettings, "Geometry", "TextureCoords", maxExp_obj["TextureCoords"])
            rt.setINISetting(iniPath_exportSettings, "Geometry", "Normals", maxExp_obj["Normals"])
            rt.setINISetting(iniPath_exportSettings, "Geometry", "SmoothingGroups", maxExp_obj["SmoothingGroups"])
            rt.setINISetting(iniPath_exportSettings, "Geometry", "ObjScale", maxExp_obj["ObjScale"])

            rt.setINISetting(iniPath_exportSettings, "Output", "RelativeIndex", maxExp_obj["RelativeIndex"])
            rt.setINISetting(iniPath_exportSettings, "Output", "Target", maxExp_obj["Target"])
            rt.setINISetting(iniPath_exportSettings, "Output", "Precision", maxExp_obj["Precision"])

            rt.setINISetting(iniPath_exportSettings, "Optimize", "optVertex", maxExp_obj["optVertex"])
            rt.setINISetting(iniPath_exportSettings, "Optimize", "optNormals", maxExp_obj["optNormals"])
            rt.setINISetting(iniPath_exportSettings, "Optimize", "optTextureCoords", maxExp_obj["optTextureCoords"])

            try:
                rt.exportFile(filePath, rt.Name("NoPrompt"), selectedOnly=exportSelected, using=rt.ObjExp)
                return True
            except:
                msg = "Cannot export OBJ for unknown reason. Skipping OBJ export"
                rt.messageBox(msg, title='Info')
                return False

            # objName = "{0}.obj".format(assetName)
        else:
            msg = "Wavefront(Obj) Export Plugin cannot be initialized. Skipping Obj export"
            rt.messageBox(msg, title='Info')
            return False

    def _exportAlembic(self, filePath, exportSettings, exportSelected=True):
        """
        Exports Alembic (.abc) file
        Args:
            filePath: (String) Absolute File path for exported file
            exportSettings: (Dictionary) settings file (see getExportSettings)
            exportSelected: (Boolean) If True, exports only currently selected objects, else whole scene. Default True

        Returns: (Boolean) True for success False for failure

        """
        # Set Alembic Options according to the Max Version:
        v = rt.maxVersion()[0]
        maxExp_abc = exportSettings["alembicExportMax"]

        if v > 17000:  # Alembic export is not supported before 3ds Max 2016
            if rt.pluginManager.loadclass(rt.Alembic_Export):
                if 18000 <= v < 21000:  # between versions 2016 - 2018
                    rt.AlembicExport.CoordinateSystem = rt.Name(maxExp_abc["CoordinateSystem"])
                    rt.AlembicExport.ArchiveType = rt.Name(maxExp_abc["ArchiveType"])
                    rt.AlembicExport.ParticleAsMesh = maxExp_abc["ParticleAsMesh"]
                    rt.AlembicExport.CacheTimeRange = rt.Name(maxExp_abc["AnimTimeRange"])
                    rt.AlembicExport.ShapeName = maxExp_abc["ShapeSuffix"]
                    # rt.AlembicExport.StepFrameTime = exportSettings["StepFrameTime"]

                elif v >= 21000:  # version 2019 and up
                    rt.AlembicExport.CoordinateSystem = rt.Name(maxExp_abc["CoordinateSystem"])
                    rt.AlembicExport.ArchiveType = rt.Name(maxExp_abc["ArchiveType"])
                    rt.AlembicExport.ParticleAsMesh = maxExp_abc["ParticleAsMesh"]
                    rt.AlembicExport.AnimTimeRange = rt.Name(maxExp_abc["AnimTimeRange"])
                    rt.AlembicExport.ShapeSuffix = maxExp_abc["ShapeSuffix"]
                    rt.AlembicExport.SamplesPerFrame = maxExp_abc["SamplesPerFrame"]
                    rt.AlembicExport.Hidden = maxExp_abc["Hidden"]
                    rt.AlembicExport.UVs = maxExp_abc["UVs"]
                    rt.AlembicExport.Normals = maxExp_abc["Normals"]
                    rt.AlembicExport.VertexColors = maxExp_abc["VertexColors"]
                    rt.AlembicExport.ExtraChannels = maxExp_abc["ExtraChannels"]
                    rt.AlembicExport.Velocity = maxExp_abc["Velocity"]
                    rt.AlembicExport.MaterialIDs = maxExp_abc["MaterialIDs"]
                    rt.AlembicExport.Visibility = maxExp_abc["Visibility"]
                    rt.AlembicExport.LayerName = maxExp_abc["LayerName"]
                    rt.AlembicExport.MaterialName = maxExp_abc["MaterialName"]
                    rt.AlembicExport.ObjectID = maxExp_abc["ObjectID"]
                    rt.AlembicExport.CustomAttributes = maxExp_abc["CustomAttributes"]

                # Export
                rt.exportFile(filePath, rt.Name("NoPrompt"), selectedOnly=exportSelected,
                              using=rt.Alembic_Export)
                return True

            else:
                rt.messageBox("Alembic Plugin cannot be initialized. Skipping", title="Alembic not supported")
                return False
        else:
            rt.messageBox("There is no alembic support for this version. Skipping", title="Alembic not supported")
            return False

    def _exportFbx(self, filePath, exportSettings, exportSelected=True, timeRange=[0,10]):
        """
        Exports FBX (.fbx) file
        Args:
            filePath: (String) Absolute File path for exported file
            exportSettings: (Dictionary) settings file (see getExportSettings)
            exportSelected: (Boolean) If True, exports only currently selected objects, else whole scene. Default True

        Returns: (Boolean) True for success False for failure

        """
        if rt.pluginManager.loadclass(rt.FBXEXP):
            maxExp_fbx = exportSettings["fbxExportMax"]

            # OVERRIDE ANIMATION SETTINGS
            if timeRange[0] != timeRange[1]:
                maxExp_fbx["Animation"] = True
                maxExp_fbx["BakeFrameStart"] = timeRange[0]
                maxExp_fbx["BakeFrameEnd"] = timeRange[1]
            else:
                maxExp_fbx["Animation"] = False

            # Set FBX Options
            for item in maxExp_fbx.items():
                rt.FBXExporterSetParam(rt.Name(item[0]), item[1])

            try:
                rt.exportFile(filePath, rt.Name("NoPrompt"), selectedOnly=exportSelected,
                              using=rt.FBXEXP)
                return True
            except:
                msg = "Cannot export FBX for unknown reason. Skipping FBX export"
                rt.messageBox(msg, title='Info')
                return False
        else:
            msg = "FBX Plugin cannot be initialized. Skipping FBX export"
            rt.messageBox(msg, title='Info')
            return False

    def _getSceneFile(self):
        s_path = fManager.GetFileNameAndPath()
        norm_s_path = os.path.normpath(s_path)
        return norm_s_path

    def _getProject(self):
        norm_p_path = os.path.normpath(pManager.GetProjectFolderDir())
        return norm_p_path

    def _getVersion(self):
        return rt.maxversion()

    def _getCurrentFrame(self):
        return int(rt.sliderTime)

    def _getSelection(self):
        sel = rt.execute("selection as array")
        strList = [x.name for x in sel]
        return strList

class MaxManager(RootManager, MaxCoreFunctions):
    def __init__(self):
        super(MaxManager, self).__init__()
        self.swName = "3dsMax"
        self.init_paths(self.swName)
        # self.backwardcompatibility()  # DO NOT RUN UNTIL RELEASE
        self.init_database()


    def getSoftwarePaths(self):
        """Overriden function"""
        logger.debug("Func: getSoftwarePaths")
        self._pathsDict["generalSettingsDir"]
        # softwareDatabaseFile = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "softwareDatabase.json"))
        softwareDatabaseFile = os.path.normpath(os.path.join(self._pathsDict["generalSettingsDir"], "softwareDatabase.json"))
        # softwareDatabaseFile = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "softwareDatabase.json"))
        softwareDB = self._loadJson(softwareDatabaseFile)
        return softwareDB["3dsMax"]
        # To tell the base class maya specific path names
        # return {"niceName": "3dsMax",
        #         "databaseDir": "maxDB",
        #         "scenesDir": "scenes_3dsMax",
        #         "pbSettingsFile": "pbSettings_3dsMax.json",
        #         "categoriesFile": "categories3dsMax.json",
        #         "userSettingsDir": "SceneManager\\3dsMax"} # this is just for 3ds max. expanduser"~" returns different in max

    def getProjectDir(self):
        """Overriden function"""
        # p_path = pManager.GetProjectFolderDir()
        # norm_p_path = os.path.normpath(p_path)
        projectsDict = self._loadProjects()


        if not projectsDict:
            norm_p_path = self._getProject()
            projectsDict = {"3dsMaxProject": norm_p_path}
            self._saveProjects(projectsDict)
            return norm_p_path

        # get the project defined in the database file
        try:
            norm_p_path = projectsDict["3dsMaxProject"]
            return norm_p_path
        except KeyError:
            norm_p_path = self._getProject()
            projectsDict = {"3dsMaxProject": norm_p_path}
            self._saveProjects(projectsDict)
            return norm_p_path


    def getSceneFile(self):
        """Overriden function"""
        # Gets the current scene path ("" if untitled)
        logger.debug("GETSCENEFILE")
        s_path = fManager.GetFileNameAndPath()
        norm_s_path = os.path.normpath(s_path)
        return norm_s_path

    def setProject(self, path):
        """Sets the project"""
        projectsDict = self._loadProjects()
        if not projectsDict:
            projectsDict = {"3dsMaxProject": path}
        else:
            projectsDict["3dsMaxProject"] = path
        self._saveProjects(projectsDict)
        self.projectDir = path

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
            "date": now
        }
        sceneName = self.resolveSaveName(nameDict, version)

        # sceneName = "{0}_{1}_{2}_v{3}".format(baseName, categoryName, self._usersDict[self.currentUser], str(version).zfill(3))

        sceneFile = os.path.join(shotPath, "{0}.{1}".format(sceneName, sceneFormat))
        ## relativity update
        relSceneFile = os.path.relpath(sceneFile, start=projectPath)

        fManager.Save(sceneFile)

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
        versionInfo = rt.maxversion()
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
        # jsonInfo["Versions"] = [ # PATH => Notes => User Initials => Machine ID => Playblast => Thumbnail
        #     [relSceneFile, completeNote,  self._usersDict[self.currentUser], socket.gethostname(), {}, thumbPath]]
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
        return [0, ""]

    def saveVersion(self, makeReference=True, versionNotes="", sceneFormat="max", *args, **kwargs):
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
            logger.warning(msg)
            return -1, msg

        sceneInfo = self.getOpenSceneInfo()

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
                "date": now
            }
            sceneName = self.resolveSaveName(nameDict, currentVersion)

            # sceneName = "{0}_{1}_{2}_v{3}".format(jsonInfo["Name"], jsonInfo["Category"], self._usersDict[self.currentUser],
            #                                       str(currentVersion).zfill(3))
            relSceneFile = os.path.join(jsonInfo["Path"], "{0}.{1}".format(sceneName, sceneFormat))

            sceneFile = os.path.join(sceneInfo["projectPath"], relSceneFile)

            # killTurtle()
            # TODO // cmds?
            fManager.Save(sceneFile)

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
        print "CVP", viewportType
        if str(viewportType) == "view_camera":
            currentCam = str(rt.getActiveCamera().name)
        else:
            currentCam = str(viewportType)

        validName = currentCam.replace("|", "__").replace(" ", "_")
        extension = "avi"

        # versionName = rt.getFilenameFile(rt.maxFileName) #
        versionName = rt.maxFilePath + rt.maxFileName # abs path of the filename with extension
        print "versionName", versionName
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


        # find the path of where the avi file be created
        # if rt.maxFilePath:
        #     previewname = rt.getFilenameFile(rt.maxFileName)
        # else:
        #     previewname = "Untitled"

        sourceClip = rt.GetDir(rt.execute("#preview")) + "\_scene.avi "

        # destination = os.path.join(rt.maxFilePath, previewname)

        print "sourceClip is: %s" % sourceClip

        print "test: %s" %os.path.isfile(sourceClip)

        if os.path.isfile(sourceClip):
            try:
                os.remove(sourceClip)
            except WindowsError:
                msg = "Cannot continue creating preview.\n Close '%s' and try again" %sourceClip
                logger.error(msg)
                return -1, msg

        rt.createPreview(percentSize=percentSize, dspGeometry=dspGeometry,
                         dspShapes=dspShapes, dspLights=dspLights,
                         dspCameras=dspCameras, dspHelpers=dspHelpers,
                         dspParticles=dspParticles, dspBones=dspBones,
                         dspGrid=dspGrid, dspFrameNums=dspFrameNums,
                         rndLevel=rndLevel)


        # return the render width and height to original:
        rt.renderWidth = originalValues["width"]
        rt.renderHeight = originalValues["height"]

        rt.select(originalSelection)

        shutil.copy(sourceClip, playBlastFile)

        ## find this version in the json data
        print "relVersionName", relVersionName
        print "jInfo", jsonInfo

        for version in jsonInfo["Versions"]:
            if relVersionName == version["RelativePath"]:
                version["Preview"][currentCam] = relPlayBlastFile

        self._dumpJson(jsonInfo, openSceneInfo["jsonFile"])
        return 0, ""


    def loadBaseScene(self, force=False):
        """Loads the scene at cursor position"""
        # TODO // TEST IT
        relSceneFile = self._currentSceneInfo["Versions"][self._currentVersionIndex-1]["RelativePath"]
        absSceneFile = os.path.join(self.projectDir, relSceneFile)
        if os.path.isfile(absSceneFile):
            fManager.Open(absSceneFile)
            # cmds.file(absSceneFile, o=True, force=force)
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
            fManager.Merge(absSceneFile)
            # cmds.file(absSceneFile, i=True)
            return 0
        else:
            msg = "File in Scene Manager database doesnt exist"
            logger.error(msg)
            return -1, msg

    def referenceBaseScene(self):
        """Creates reference from the scene at cursor position"""

        projectPath = self.projectDir
        relReferenceFile = self._currentSceneInfo["ReferenceFile"]


        if relReferenceFile:
            referenceFile = os.path.join(projectPath, relReferenceFile)

            # software specific
            Xrefobjs = rt.getMAXFileObjectNames(referenceFile)
            rt.xrefs.addNewXRefObject(referenceFile, Xrefobjs)
            try:
                ranges = self._currentSceneInfo["Versions"][self._currentSceneInfo["ReferencedVersion"]-1]["Ranges"]
                q = self._question("Do You want to set the Time ranges same with the reference?")
                if q:
                    self._setTimelineRanges(ranges)
            except KeyError:
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
        # rt = pymxs.runtime
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

        # rt.display(thumbFrame)

        thumbFrame.filename = thumbPath
        rt.save(thumbFrame)
        rt.close(thumbFrame)



        # img = rt.gw.getViewportDib()
        # img.fileName = thumbPath
        # rt.save(img)
        # rt.close(img)

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


        # try:
        #     self._currentSceneInfo["Versions"][self.currentVersionIndex-1][5]=filePath
        # except IndexError: # if this is an older file without thumbnail
        #     self._currentSceneInfo["Versions"][self.currentVersionIndex-1].append(filePath)

        self._dumpJson(self._currentSceneInfo, self.currentDatabasePath)

    def compareVersions(self):
        """Compares the versions of current session and database version at cursor position"""
        # TODO : Write compare function for 3ds max
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
        # version, api, sdk = rt.maxversion()
        versionInfo = self._getVersion()
        # currentVersion = [version, api, sdk]
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
        return fManager.IsSaveRequired()

    def saveSimple(self):
        """Save the currently open file"""
        fManager.Save()

    def getFormatsAndCodecs(self):
        """Returns the codecs which can be used in current workstation"""
        # TODO : Write Get Formats and Codecs for 3ds max (if applicable)
        logger.warning ("getFormatsAndCodecs Function not yet implemented")


    def preSaveChecklist(self):
        """Checks the scene for inconsistencies"""
        checklist = []

        # TODO : Create a fps comparison with the settings file
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

    def _getTimelineRanges(self):
        R_ast = int(rt.animationRange.start)
        R_min = int(rt.animationRange.start)
        R_max = int(rt.animationRange.end)
        R_aet = int(rt.animationRange.end)
        return [R_ast, R_min, R_max, R_aet]

    def _setTimelineRanges(self, rangeList):
        """Sets the timeline ranges [AnimationStart, Min, Max, AnimationEnd]"""
        rt.animationRange = rt.interval(rangeList[0], rangeList[-1])

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
        self.mIconPixmap = QtGui.QPixmap(os.path.join(self.manager._pathsDict["generalSettingsDir"], "icons", "iconMax.png"))
        self.managerIcon_label.setPixmap(self.mIconPixmap)

    def onModeChange(self):
        """OVERRIDEN METHOD - This method is overriden to make the color changing compatible with 3ds max"""
        self._vEnableDisable()

        if self.load_radioButton.isChecked():
            self.loadScene_pushButton.setText("Load Scene")
            # self.scenes_listWidget.setStyleSheet("border-style: solid; border-width: 2px; border-color: grey;")
            self.scenes_listWidget.setStyleSheet("background-color: rgb(100,100,100); border-style: solid; border-width: 2px; border-color: grey;")
        else:
            self.loadScene_pushButton.setText("Reference Scene")
            # self.scenes_listWidget.setStyleSheet("background-color: rgb(100,100,100);")
            self.scenes_listWidget.setStyleSheet("background-color: rgb(80,120,120); border-style: solid ; border-width: 2px; border-color: cyan;")
        self.populateBaseScenes()




