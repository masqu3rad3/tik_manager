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
import sys
import SmRoot
reload(SmRoot)
from SmRoot import RootManager

import _version
import shutil

import datetime
import socket
import pprint
import logging
import hou
import toolutils
from glob import glob

import subprocess
import platform

from Qt import QtWidgets, QtCore, QtGui
# from PySide2 import QtWidgets
# from PySide2 import QtGui

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

class HoudiniCoreFunctions(object):
    def __init__(self):
        super(HoudiniCoreFunctions, self).__init__()

    def _save(self, *args, **kwargs):
        hou.hipFile.save()

    def _saveAs(self, filePath, format=None, *args, **kwargs):
        hou.hipFile.save(file_name=filePath)

    def _load(self, filePath, force=True, *args, **kwargs):
        hou.hipFile.load(filePath, suppress_save_prompt=force, ignore_load_warnings=False)

    def _reference(self, filePath):
        pass

    def _import(self, filePath, *args, **kwargs):
        hou.hipFile.merge(filePath, node_pattern="*", overwrite_on_conflict=False, ignore_load_warnings=False)

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
                    rt.AlembicExport.StepFrameTime = maxImp_abc["SamplesPerFrame"]


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
                             maxExp_obj["ExportHiddenObjects"])
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

    def _exportAlembic(self, filePath, exportSettings, exportSelected=True, timeRange=[0,10]):
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

        # override animation related settings
        maxExp_abc["AnimTimeRange"] = "StartEnd"
        maxExp_abc["StartFrame"] = timeRange[0]
        maxExp_abc["EndFrame"] = timeRange[1]



        if v > 17000:  # Alembic export is not supported before 3ds Max 2016
            if rt.pluginManager.loadclass(rt.Alembic_Export):
                if 18000 <= v < 21000:  # between versions 2016 - 2018
                    rt.AlembicExport.CoordinateSystem = rt.Name(maxExp_abc["CoordinateSystem"])
                    rt.AlembicExport.ArchiveType = rt.Name(maxExp_abc["ArchiveType"])
                    rt.AlembicExport.ParticleAsMesh = maxExp_abc["ParticleAsMesh"]
                    rt.AlembicExport.CacheTimeRange = rt.Name(maxExp_abc["AnimTimeRange"])
                    rt.AlembicExport.ShapeName = maxExp_abc["ShapeSuffix"]
                    rt.AlembicExport.StepFrameTime = maxExp_abc["SamplesPerFrame"]
                    rt.AlembicExport.AnimTimeRange = maxExp_abc["AnimTimeRange"]
                    rt.AlembicExport.StartFrame = maxExp_abc["StartFrame"]
                    rt.AlembicExport.EndFrame = maxExp_abc["EndFrame"]

                elif v >= 21000:  # version 2019 and up
                    rt.AlembicExport.CoordinateSystem = rt.Name(maxExp_abc["CoordinateSystem"])
                    rt.AlembicExport.ArchiveType = rt.Name(maxExp_abc["ArchiveType"])
                    rt.AlembicExport.ParticleAsMesh = maxExp_abc["ParticleAsMesh"]
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
                    rt.AlembicExport.AnimTimeRange = maxExp_abc["AnimTimeRange"]
                    rt.AlembicExport.StartFrame = maxExp_abc["StartFrame"]
                    rt.AlembicExport.EndFrame = maxExp_abc["EndFrame"]

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
        s_path = hou.hipFile.path()
        niceName = os.path.splitext(hou.hipFile.basename())[0]
        if niceName == "untitled":
            s_path = ""
        norm_s_path = os.path.normpath(s_path)
        return norm_s_path

    def _getProject(self):
        p_path = (hou.hscript('echo $JOB')[0])[:-1]  # [:-1] is for the extra \n
        norm_p_path = os.path.normpath(p_path)
        return norm_p_path

    def _getVersion(self):
        return hou.applicationVersion()

    def _getCurrentFrame(self):
        return hou.frame()

    def _getSelection(self):
        return hou.selectedItems()

class HoudiniManager(RootManager, HoudiniCoreFunctions):
    def __init__(self):
        super(HoudiniManager, self).__init__()

        # self.formatDict = {"hip": ".hip", "hiplc": ".hiplc"}
        self.swName = "Houdini"
        self.init_paths(self.swName)
        self.init_database()


    def getSoftwarePaths(self):
        """Overriden function"""
        logger.debug("Func: getSoftwarePaths")
        self._pathsDict["generalSettingsDir"]
        # softwareDatabaseFile = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "softwareDatabase.json"))
        softwareDatabaseFile = os.path.normpath(os.path.join(self._pathsDict["generalSettingsDir"], "softwareDatabase.json"))
        # softwareDatabaseFile = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "softwareDatabase.json"))
        softwareDB = self._loadJson(softwareDatabaseFile)
        return softwareDB["Houdini"]
        # To tell the base class maya specific path names
        # return {"niceName": "Houdini",
        #         "databaseDir": "houdiniDB",
        #         "scenesDir": "scenes_houdini",
        #         "pbSettingsFile": "pbSettings_houdini.json",
        #         "categoriesFile": "categoriesHoudini.json",
        #         "userSettingsDir": "SceneManager\\Houdini"}

    def getProjectDir(self):
        """Overriden function"""
        logger.debug("Func: getProjectDir")

        projectsDict = self._loadProjects()

        if not projectsDict:
            # p_path = (hou.hscript('echo $JOB')[0])[:-1] # [:-1] is for the extra \n
            # norm_p_path = os.path.normpath(p_path)
            norm_p_path = self._getProject()
            projectsDict = {"HoudiniProject": norm_p_path}
            self._saveProjects(projectsDict)
            return norm_p_path

        # get the project defined in the database file
        try:
            norm_p_path = projectsDict["HoudiniProject"]
            self.setProject(norm_p_path)
            return norm_p_path
        except KeyError:
            p_path = (hou.hscript('echo $JOB')[0])[:-1] # [:-1] is for the extra \n
            norm_p_path = os.path.normpath(p_path)
            projectsDict = {"HoudiniProject": norm_p_path}
            self._saveProjects(projectsDict)
            return norm_p_path

    def getSceneFile(self):
        """Overriden function"""
        # logger.debug("Func: getSceneFile")
        # # # Gets the current scene path ("" if untitled)
        # s_path = hou.hipFile.path()
        # niceName = os.path.splitext(hou.hipFile.basename())[0]
        # if niceName == "untitled":
        #     s_path = ""
        # norm_s_path = os.path.normpath(s_path)
        # return norm_s_path
        return self._getSceneFile()

    def setProject(self, path):
        """Sets the project"""

        logger.debug("Func: setProject")

        projectsDict = self._loadProjects()
        if not projectsDict:
            projectsDict = {"HoudiniProject": path}
        else:
            projectsDict["HoudiniProject"] = path
        self._saveProjects(projectsDict)
        self.projectDir = path
        self._setEnvVariable('JOB', path)


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
            "date": now
        }
        sceneName = self.resolveSaveName(nameDict, version)

        # sceneName = "{0}_{1}_{2}_v{3}".format(baseName, categoryName, self._usersDict[self.currentUser], str(version).zfill(3))
        absSceneFile = os.path.join(shotPath, "{0}.{1}".format(sceneName, sceneFormat))
        # print "absSceneFile", absSceneFile
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
        return [0, ""]

    def saveVersion(self, makeReference=False, versionNotes="", sceneFormat="hip", *args, **kwargs):
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
            # cmds.warning(msg)
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
            self.saveAs(absSceneFile)

            thumbPath = self.createThumbnail(dbPath=jsonFile, versionInt=currentVersion)

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
        return jsonInfo


    def createPreview(self, *args, **kwargs):
        """Creates a Playblast preview from currently open scene"""
        logger.debug("Func: createPreview")



        #
        pbSettings = self.loadPBSettings()
        # validFormats = cmds.playblast(format=True, q=True)
        # validCodecs = cmds.playblast(c=True, q=True)
        #
        # if not pbSettings["Format"] in validFormats:
        #     msg = ("Format specified in project settings is not supported. Install {0}".format(pbSettings["Format"]))
        #     cmds.warning(msg)
        #     return -1, msg
        #
        # if not pbSettings["Codec"] in validCodecs:
        #     msg = ("Codec specified in project settings is not supported. Install {0}".format(pbSettings["Codec"]))
        #     cmds.warning(msg)
        #     return -1, msg
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

        # flip_options.output("E:\\test\\{0}_$F4.{1}".format(camName, "tga"))
        # flip_options.useResolution(True)
        # flip_options.resolution((221, 124))
        # scene_view.flipbook(viewport, flip_options)


        versionName = self.getSceneFile()
        relVersionName = os.path.relpath(versionName, start=openSceneInfo["projectPath"])
        playBlastDir = os.path.join(openSceneInfo["previewPath"], openSceneInfo["version"])
        self._folderCheck(playBlastDir)
        playBlastFile = os.path.join(playBlastDir, "{0}_{1}_PB_$F4.{2}".format(self.niceName(versionName), currentCam, extension))
        relPlayBlastFile = os.path.relpath(playBlastFile, start=openSceneInfo["projectPath"])
        #
        if os.path.isfile(playBlastFile):
            try:
                os.remove(playBlastFile)
            except WindowsError:
                msg = "The file is open somewhere else"
                self._exception(202, msg)
                return

        flip_options.output(playBlastFile)
        #
        # ## CREATE A CUSTOM PANEL WITH DESIRED SETTINGS
        #
        # tempWindow = cmds.window(title="SM_Playblast",
        #                        widthHeight=(pbSettings["Resolution"][0] * 1.1, pbSettings["Resolution"][1] * 1.1),
        #                        tlc=(0, 0))
        # # panel = pm.getPanel(wf=True)
        #
        # cmds.paneLayout()
        #
        # pbPanel = cmds.modelPanel(camera=currentCam)
        # cmds.showWindow(tempWindow)
        # cmds.setFocus(pbPanel)
        #
        # cmds.modelEditor(pbPanel, e=1,
        #                allObjects=not pbSettings["PolygonOnly"],
        #                da="smoothShaded",
        #                displayTextures=pbSettings["DisplayTextures"],
        #                wireframeOnShaded=pbSettings["WireOnShaded"],
        #                grid=pbSettings["ShowGrid"],
        #                useDefaultMaterial=pbSettings["UseDefaultMaterial"],
        #                polymeshes=True,
        #                imagePlane=True,
        #                hud=True
        #                )
        #
        # cmds.camera(currentCam, e=True, overscan=True, displayFilmGate=False, displayResolution=False)
        #
        # ## get previous HUD States and turn them all off
        # hudPreStates = {}
        # HUDS = cmds.headsUpDisplay(lh=True)
        # for hud in HUDS:
        #     hudPreStates[hud] = cmds.headsUpDisplay(hud, q=True, vis=True)
        #     cmds.headsUpDisplay(hud, e=True, vis=False)
        #
        # ## clear the custom HUDS
        # customHuds = ['SMFrame', 'SMScene', 'SMCategory', 'SMFPS', 'SMCameraName', 'SMFrange']
        # for hud in customHuds:
        #     if cmds.headsUpDisplay(hud, ex=True):
        #         cmds.headsUpDisplay(hud, rem=True)
        #
        # if pbSettings["ShowFrameNumber"]:
        #     freeBl = cmds.headsUpDisplay(nfb=5)  ## this is the next free block on section 5
        #     cmds.headsUpDisplay('SMFrame', s=5, b=freeBl, label="Frame", preset="currentFrame", dfs="large",
        #                       lfs="large")
        # if pbSettings["ShowSceneName"]:
        #     freeBl = cmds.headsUpDisplay(nfb=5)  ## this is the next free block on section 5
        #     cmds.headsUpDisplay('SMScene', s=5, b=freeBl, label="Scene: %s" % (self.niceName(versionName)),
        #                       lfs="large")
        # if pbSettings["ShowCategory"]:
        #     freeBl = cmds.headsUpDisplay(nfb=5)  ## this is the next free block on section 5
        #     cmds.headsUpDisplay('SMCategory', s=5, b=freeBl, label="Category: %s" % (jsonInfo["Category"]),
        #                       lfs="large")
        # if pbSettings["ShowFPS"]:
        #     freeBl = cmds.headsUpDisplay(nfb=5)  ## this is the next free block on section 5
        #     cmds.headsUpDisplay('SMFPS', s=5, b=freeBl, label="Time Unit: %s" % (cmds.currentUnit(q=True, time=True)),
        #                       lfs="large")
        #
        # # v1.1 SPECIFIC
        # try:
        #     if pbSettings["ShowFrameRange"]:
        #         freeBl = cmds.headsUpDisplay(nfb=5)  ## this is the next free block on section 5
        #         cmds.headsUpDisplay('SMFrange', s=5, b=freeBl,
        #                           label="Frame Range: {} - {}".format(int(cmds.playbackOptions(q=True, minTime=True)),
        #                                                               int(cmds.playbackOptions(q=True,
        #                                                                                      maxTime=True))),
        #                           lfs="large")
        # except KeyError:
        #     pass
        #
        # freeBl = cmds.headsUpDisplay(nfb=2)
        # cmds.headsUpDisplay('SMCameraName', s=2, b=freeBl, ba='center', dw=50, pre='cameraNames')
        #
        # ## Get the active sound
        #
        # aPlayBackSliderPython = mel.eval('$tmpVar=$gPlayBackSlider')
        # activeSound = cmds.timeControl(aPlayBackSliderPython, q=True, sound=True)
        #
        # ## Check here: http://download.autodesk.com/us/maya/2011help/pymel/generated/functions/pymel.core.windows/pymel.core.windows.headsUpDisplay.html
        # # print "playBlastFile", playBlastFile
        # normPB = os.path.normpath(playBlastFile)
        # # print "normPath", normPB
        ranges = self._getTimelineRanges()
        flip_options.frameRange((ranges[1], ranges[2]))
        flip_options.outputToMPlay(True)
        flip_options.useResolution(True)
        flip_options.resolution((pbSettings["Resolution"][0], pbSettings["Resolution"][1]))
        scene_view.flipbook(viewport, flip_options)


        # cmds.playblast(format=pbSettings["Format"],
        #              filename=playBlastFile,
        #              widthHeight=pbSettings["Resolution"],
        #              percent=pbSettings["Percent"],
        #              quality=pbSettings["Quality"],
        #              compression=pbSettings["Codec"],
        #              sound=activeSound,
        #              uts=True)
        # ## remove window when pb is donw
        # cmds.deleteUI(tempWindow)
        #
        # # Get back to the original frame range if the codec is Quick Time
        # if pbSettings["Format"] == 'qt':
        #     cmds.playbackOptions(maxTime=maxTime)
        #     cmds.playbackOptions(animationEndTime=endTime)
        #
        # ## remove the custom HUdS
        # if pbSettings["ShowFrameNumber"]:
        #     cmds.headsUpDisplay('SMFrame', rem=True)
        # if pbSettings["ShowSceneName"]:
        #     cmds.headsUpDisplay('SMScene', rem=True)
        # if pbSettings["ShowCategory"]:
        #     cmds.headsUpDisplay('SMCategory', rem=True)
        # if pbSettings["ShowFPS"]:
        #     cmds.headsUpDisplay('SMFPS', rem=True)
        # try:
        #     if pbSettings["ShowFrameRange"]:
        #         cmds.headsUpDisplay('SMFrange', rem=True)
        # except KeyError:
        #     pass
        #
        #     cmds.headsUpDisplay('SMCameraName', rem=True)
        #
        # ## get back the previous state of HUDS
        # for hud in hudPreStates.keys():
        #     cmds.headsUpDisplay(hud, e=True, vis=hudPreStates[hud])
        # pm.select(selection)

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
        # logger.debug("Func: playPreview")

        # absPath = os.path.join(self.projectDir, self._currentPreviewsDict[self._currentPreviewCamera])
        absPath = os.path.join(self.projectDir, self._currentPreviewsDict[camera])
        # absPath.replace("_$F4", "_0001")
        if self.currentPlatform == "Windows":
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
            # print "absSceneFile", absSceneFile
            # houdini opens the scene with "\" paths but cannot resolve some inside paths. So convert them to "/"
            absSceneFile = absSceneFile.replace('\\', '/')
            # hou.hipFile.load(absSceneFile, suppress_save_prompt=force, ignore_load_warnings=False)
            self._load(absSceneFile, force=force)
            # self._setEnvVariable('HIP', os.path.split(absSceneFile)[0])
            self._setEnvVariable('HIP', os.path.split(absSceneFile)[0])
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
            # print "absSceneFile", absSceneFile
            # houdini opens the scene with "\" paths but cannot resolve some inside paths. So convert them to "/"
            absSceneFile = absSceneFile.replace('\\', '/')
            # hou.hipFile.merge(absSceneFile, node_pattern="*", overwrite_on_conflict=False, ignore_load_warnings=False)
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
        # vTup = hou.applicationVersion()
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
        return hou.hipFile.hasUnsavedChanges()


    def saveSimple(self):
        """Save the currently open file"""
        # hou.hipFile.save()
        self._save()

    def getFormatsAndCodecs(self):
        """Returns the codecs which can be used in current workstation"""
        pass
        # logger.debug("Func: getFormatsAndCodecs")
        # formatList = cmds.playblast(query=True, format=True)
        # codecsDictionary = dict(
        #     (item, mel.eval('playblast -format "{0}" -q -compression;'.format(item))) for item in formatList)
        # return codecsDictionary

    def preSaveChecklist(self):
        """Checks the scene for inconsistencies"""
        checklist = []

        fpsValue_setting = self.getFPS()
        fpsValue_current = int(hou.fps())
        if fpsValue_setting is not fpsValue_current:
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

    def _getTimelineRanges(self):
        pass
        R_ast = int(hou.playbar.frameRange()[0])
        R_min = int(hou.playbar.playbackRange()[0])
        R_max = int(hou.playbar.playbackRange()[1])
        R_aet = int(hou.playbar.frameRange()[1])
        return [R_ast, R_min, R_max, R_aet]

    def _setTimelineRanges(self, rangeList):
        """Sets the timeline ranges [AnimationStart, Min, Max, AnimationEnd]"""
        hou.playbar.setFrameRange(rangeList[0], rangeList[3])
        hou.playbar.setPlaybackRange(rangeList[1], rangeList[2])

        #
    def _createCallbacks(self, handler):
        pass
        # logger.debug("Func: _createCallbacks")
        # callbackIDList=[]
        # callbackIDList.append(cmds.scriptJob(e=["workspaceChanged", "%s.callbackRefresh()" % handler], replacePrevious=True, parent=SM_Version))
        # return callbackIDList

    def _killCallbacks(self, callbackIDList):
        pass
        # logger.debug("Func: _killCallbacks")
        # for x in callbackIDList:
        #     if cmds.scriptJob(ex=x):
        #         cmds.scriptJob(kill=x)

    def _setEnvVariable(self, var, value):
        """sets environment var
        :param str var: The name of the var
        :param value: The value of the variable
        """
        os.environ[var] = value
        try:
            hou.allowEnvironmentVariableToOverwriteVariable(var, True)
        except AttributeError:
            # should be Houdini 12
            hou.allowEnvironmentToOverwriteVariable(var, True)

        value = value.replace('\\', '/')
        hscript_command = "set -g %s = '%s'" % (var, value)

        hou.hscript(str(hscript_command))

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

        # # Set Stylesheet
        # dirname = os.path.dirname(os.path.abspath(__file__))
        # stylesheetFile = os.path.join(dirname, "CSS", "darkorange.stylesheet")
        #
        # with open(stylesheetFile, "r") as fh:
        #     self.setStyleSheet(fh.read())

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

        self.mIconPixmap = QtGui.QPixmap(os.path.join(self.manager._pathsDict["generalSettingsDir"], "icons", "iconHoudini.png"))
        self.managerIcon_label.setPixmap(self.mIconPixmap)


