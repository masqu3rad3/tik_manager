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

# Asset save functions for Maya to be used with assetLibrary
import os
# import pymel.core as pm
import maya.cmds as cmds
# import maya.mel as mel
from shutil import copyfile
# import json
# import logging
# from SmMaya import MayaCoreFunctions
from coreFunctions.coreFunctions_Maya import MayaCoreFunctions


# TODO : Subclass MayaCoreFunctions
class AssetEditorMaya(MayaCoreFunctions):
    def __init__(self):
        super(AssetEditorMaya, self).__init__()
        self.directory=""


    def getSwName(self):
        return "Maya"

    def saveAsset(self, assetName, exportUV=True, exportOBJ=True, exportFBX=True, exportABC=True, selectionOnly=True, sceneFormat="mb", notes="N/A", **info):
        """
        Saves the selected object(s) as an asset into the predefined library
        """
        # self.ssResolution = 1000
        if assetName == "":
            msg = "Asset Name cannot be empty"
            state = cmds.confirmDialog(title='Asset Exists', message=msg, button=['Ok'])
            return

        if assetName in self.assetsList:
            msg = "This Asset already exists.\nDo you want to overwrite?"
            state = cmds.confirmDialog(title='Asset Exists', message=msg, button=['Ok', 'Cancel'])
            # cmds.warning("There are unknown nodes in the scene. Cannot proceed with %s extension. Do you want to proceed with %s?" %(ext, origExt))
            if state == "Ok":
                pass
            elif state == "Cancel":
                return

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
            # cmds.warning("There are unknown nodes in the scene. Cannot proceed with %s extension. Do you want to proceed with %s?" %(ext, origExt))
            if state == "Ok":
                if origExt == u'.mb':
                    ext = u'.mb'
                    saveFormat = "mayaBinary"
                else:
                    ext = u'.ma'
                    saveFormat = "mayaAscii"

            elif state == "Cancel":
                return

        assetDirectory = os.path.join(self.directory, assetName)

        assetAbsPath = os.path.join(assetDirectory, "%s%s" %(assetName, ext))


        if selectionOnly:
            selection = cmds.ls(sl=True, type="transform")
            if len(selection) == 0:
                cmds.confirmDialog(title="Selection Error", message="No Transform object selected", button=['Ok'])
                return
        else:
            selection = cmds.ls()

        if not os.path.exists(assetDirectory):
            os.mkdir(assetDirectory)

        # GET TEXTURES
        # ------------

        possibleFileHolders = cmds.listRelatives(selection, ad=True, type=["mesh", "nurbsSurface"], fullPath=True)
        allFileNodes = self._getFileNodes(possibleFileHolders)

        textureDatabase = [x for x in self._buildPathDatabase(allFileNodes, assetDirectory)]

        self._copyTextures(textureDatabase)

        # CREATE PREVIEWS
        # ---------------
        thumbPath, ssPath, swPath = self._createThumbnail(assetName, selectionOnly=selectionOnly, viewFit=True)

        # CREATE UV SNAPSHOTS
        # ----------------
        if exportUV:
            self._uvSnaps(assetName)

        # SAVE SOURCE
        # -----------
        cmds.file(assetAbsPath, type=saveFormat, exportSelected=True, force=True)

        # if selectionOnly:
        #     cmds.file(assetPath, type=saveFormat, exportSelected=True)
        # else:
        #     cmds.file(rename=assetPath)
        #     cmds.file(save=True, type=saveFormat)

        # EXPORT OBJ
        # ----------

        if exportOBJ:
            # objSettings = self.exportSettings["objExportMaya"]
            objFilePath = os.path.join(assetDirectory, "%s.obj" %assetName)
            if self._exportObj(objFilePath, exportSettings=self.exportSettings):
                objName = "{0}.obj".format(assetName)
            else:
                objName = "N/A"

        else:
            objName = "N/A"

        # EXPORT FBX
        # ----------
        if exportFBX:
            # fbxSettings = self.exportSettings["fbxExportMaya"]
            fbxFilePath = os.path.join(assetDirectory, "%s.fbx" % assetName)
            # frame = cmds.currentTime(query=True)
            frame = self._getCurrentFrame()

            if self._exportFbx(fbxFilePath, exportSettings=self.exportSettings, timeRange=[frame, frame]):
                fbxName = "{0}.fbx".format(assetName)
            else:
                fbxName = "N/A"

        else:
            fbxName = "N/A"

        # EXPORT ALEMBIC
        # --------------

        if exportABC:
            # abcSettings = self.exportSettings["alembicExportMaya"]
            abcFilePath = os.path.join(assetDirectory, "%s.abc" % assetName)
            # frame = cmds.currentTime(query=True)
            frame = self._getCurrentFrame()

            if self._exportAlembic(abcFilePath, exportSettings=self.exportSettings, timeRange=[frame, frame]):
                abcName = "{0}.abc".format(assetName)
            else:
                abcName = "N/A"

        else:
            abcName = "N/A"

        # NUMERIC DATA
        # ------------
        cmds.select(hi=True)
        polyCount = cmds.polyEvaluate(f=True)
        tiangleCount = cmds.polyEvaluate(t=True)

        # DATABASE
        # --------

        dataDict = {}
        dataDict['sourceProject'] = "Maya(%s)" %ext
        dataDict['version'] = cmds.about(q=True, api=True)
        dataDict['assetName'] = assetName
        dataDict['objPath'] = objName
        dataDict['fbxPath'] = fbxName
        dataDict['abcPath'] = abcName
        dataDict['sourcePath'] = os.path.basename(assetAbsPath)
        dataDict['thumbPath'] = os.path.basename(thumbPath)
        dataDict['ssPath'] = os.path.basename(ssPath)
        dataDict['swPath'] = os.path.basename(swPath)
        dataDict['textureFiles'] = [x["Texture"] for x in textureDatabase]
        dataDict['Faces/Triangles'] = ("%s/%s" % (str(polyCount), str(tiangleCount)))
        dataDict['origin'] = originalPath
        dataDict['notes'] = notes

        self._setData(assetName, dataDict)

        cmds.select(d=True)
        self._returnOriginal(textureDatabase)

        # self.scanAssets() # scanning issued at populate function on ui class

        cmds.confirmDialog(title="Success", message="Asset Created Successfully", button=['Ok'])

    def _createThumbnail(self, assetName, selectionOnly=True, viewFit=True):
        ssResolution = 1000
        thumbPath = os.path.join(self.directory, assetName, "%s_thumb.jpg" % assetName)
        SSpath = os.path.join(self.directory, assetName, "%s_s.jpg" % assetName)
        WFpath = os.path.join(self.directory, assetName, "%s_w.jpg" % assetName)

        selection = cmds.ls(sl=True)

        # if not update:

        if not selectionOnly:
            # deselect if you dont want to focus only on the selection
            selection = cmds.ls(type="transform")
            cmds.select(d=True)


        ## CREATE A CUSTOM PANEL WITH DESIRED SETTINGS

        try:
            currentCam = cmds.modelPanel(cmds.getPanel(wf=True), q=True, cam=True)
            vRenderer = cmds.modelEditor(cmds.getPanel(wf=True), q=True, rnm=True)
        except RuntimeError:
            currentCam = u'persp'
            vRenderer = 'vp2Renderer'

        tempWindow = cmds.window(title="AssetLibrary_SS",
                               widthHeight=(ssResolution * 1.1, ssResolution * 1.1),
                               tlc=(0, 0))

        cmds.paneLayout()
        pbPanel = cmds.modelPanel(camera=currentCam)
        cmds.showWindow(tempWindow)
        cmds.setFocus(pbPanel)
        cmds.modelEditor(pbPanel, edit=True, rendererName=vRenderer)

        ########################################

        # make sure the viewport display is suitable
        # panel = cmds.getPanel(wf=True)
        #
        # if cmds.getPanel(to=panel) != "modelPanel":
        #     panel = cmds.getPanel(wl="Persp View")


        cmds.modelEditor(pbPanel, e=1, allObjects=1)
        cmds.modelEditor(pbPanel, e=1, da="smoothShaded")
        cmds.modelEditor(pbPanel, e=1, displayTextures=1)
        cmds.modelEditor(pbPanel, e=1, wireframeOnShaded=0)
        if viewFit:
            cmds.viewFit()

        if selectionOnly:
            cmds.isolateSelect(pbPanel, state=1)
            cmds.isolateSelect(pbPanel, addSelected=True)
        # temporarily deselect
        cmds.select(d=True)

        cmds.setAttr("defaultRenderGlobals.imageFormat", 8)  # This is the value for jpeg

        frame = cmds.currentTime(query=True)
        # thumb
        cmds.playblast(completeFilename=thumbPath, forceOverwrite=True, format='image', width=200, height=200,
                     showOrnaments=False, frame=[frame], viewer=False)

        # screenshot
        cmds.playblast(completeFilename=SSpath, forceOverwrite=True, format='image', width=1600, height=1600,
                     showOrnaments=False, frame=[frame], viewer=False)

        # Wireframe
        cmds.modelEditor(pbPanel, e=1, displayTextures=0)
        cmds.modelEditor(pbPanel, e=1, wireframeOnShaded=1)
        cmds.playblast(completeFilename=WFpath, forceOverwrite=True, format='image', width=1600, height=1600,
                     showOrnaments=False, frame=[frame], viewer=False)

        ## remove window when pb is donw
        cmds.deleteUI(tempWindow)

        # print panel
        cmds.select(selection)
        return thumbPath, SSpath, WFpath

    def replaceWithCurrentView(self, assetName):

        thumbPath = os.path.join(self.directory, assetName, "%s_thumb.jpg" % assetName)
        SSpath = os.path.join(self.directory, assetName, "%s_s.jpg" % assetName)
        WFpath = os.path.join(self.directory, assetName, "%s_w.jpg" % assetName)

        pbPanel = cmds.getPanel(wf=True)
        if cmds.getPanel(to=pbPanel) != "modelPanel":
            cmds.warning("The focus is not on a model panel. Cancelling")
            return None, None, None
        wireMode = cmds.modelEditor(pbPanel, q=1, wireframeOnShaded=1)
        textureMode = cmds.modelEditor(pbPanel, q=1, displayTextures=1)

        cmds.setAttr("defaultRenderGlobals.imageFormat", 8)  # This is the value for jpeg

        frame = cmds.currentTime(query=True)
        # thumb
        cmds.modelEditor(pbPanel, e=1, displayTextures=1)
        cmds.modelEditor(pbPanel, e=1, wireframeOnShaded=0)
        cmds.playblast(completeFilename=thumbPath, forceOverwrite=True, format='image', width=200, height=200,
                     showOrnaments=False, frame=[frame], viewer=False)

        # screenshot
        cmds.playblast(completeFilename=SSpath, forceOverwrite=True, format='image', width=1600, height=1600,
                     showOrnaments=False, frame=[frame], viewer=False)

        # Wireframe
        cmds.modelEditor(pbPanel, e=1, displayTextures=0)
        cmds.modelEditor(pbPanel, e=1, wireframeOnShaded=1)
        cmds.playblast(completeFilename=WFpath, forceOverwrite=True, format='image', width=1600, height=1600,
                     showOrnaments=False, frame=[frame], viewer=False)

        # leave it as it was
        cmds.modelEditor(pbPanel, e=1, wireframeOnShaded=wireMode)
        cmds.modelEditor(pbPanel, e=1, displayTextures=textureMode)

    def replaceWithExternalFile(self, assetName, FilePath):
        # TODO
        pass

    def _uvSnaps(self, assetName):
        selection = cmds.ls(sl=True)
        validShapes = cmds.listRelatives(selection, ad=True, type=["mesh", "nurbsSurface"])
        if len(validShapes) > 10:
            msg = "There are %s objects for UV snapshots.\nAre you sure you want to include snapshots to the Asset?" %(len(validShapes))
            state = cmds.confirmDialog(title='Too many objects for UV Snapshot', message=msg, button=['Ok', 'Cancel'])
            # cmds.warning("There are unknown nodes in the scene. Cannot proceed with %s extension. Do you want to proceed with %s?" %(ext, origExt))
            if state == "Ok":
                pass
            else:
                cmds.warning("Uv snapshots skipped")
                return

        assetDirectory = os.path.join(self.directory, assetName)
        UVdir = os.path.join(assetDirectory, "UV_snaps")
        if not os.path.isdir(os.path.normpath(UVdir)):
            os.makedirs(os.path.normpath(UVdir))

        for i in range(0, len(validShapes)):
            objName = validShapes[i].replace(":", "_")
            UVpath = os.path.join(UVdir, '%s_uv.jpg' % objName)
            cmds.select(validShapes[i])
            try:
                cmds.uvSnapshot(o=True, ff="jpg", n=UVpath, xr=1600, yr=1600)
            except:
                cmds.warning("Cannot create UV snapshot for %s" % validShapes[i])
        cmds.select(selection)

    def _getFileNodes(self, objList):
        returnList = []
        if not objList:
            return returnList
        for obj in objList:
            # Get the shading group from the selected mesh
            sg = cmds.listConnections(obj, type='shadingEngine')
            if not sg:
                continue
            allInputs = []
            for i in sg:
                allInputs.extend(cmds.listHistory(i))

            uniqueInputs =self.uniqueList(allInputs)

            fileNodes = cmds.ls(uniqueInputs, type="file")
            if len(fileNodes) != 0:
                returnList.extend(fileNodes)
        returnList = self.uniqueList(returnList)
        return returnList

    def _buildPathDatabase(self, fileNodeList, newRoot):
        for file in fileNodeList:
            oldAbsPath = os.path.normpath(cmds.getAttr("%s.fileTextureName" %file))
            filePath, fileBase = os.path.split(oldAbsPath)
            newAbsPath = os.path.normpath(os.path.join(newRoot, fileBase))

            yield {"FileNode": file,
                   "Texture": os.path.basename(oldAbsPath),
                   "OldPath": oldAbsPath,
                   "NewPath": newAbsPath
                   }

    def _copyTextures(self, pathDatabase):
        for data in pathDatabase:
            if data["OldPath"] != data["NewPath"]:
                copyfile(data["OldPath"], data["NewPath"])
                cmds.setAttr("%s.fileTextureName" % data["FileNode"], data["NewPath"], type="string")

    def _returnOriginal(self, pathDatabase):
        for data in pathDatabase:
            # print data
            cmds.setAttr("%s.fileTextureName" % data["FileNode"], data["OldPath"], type="string")

    def _checkVersionMatch(self, databaseVersion):
        # currentVersion = cmds.about(api=True)
        currentVersion = self._getVersion()

        if currentVersion != databaseVersion:
            msg = "Database version ({0}) and Current version ({1}) are not matching. Do you want to try anyway?".format(databaseVersion, currentVersion)
            state = cmds.confirmDialog(title='Version Mismatch', message=msg, button=['Yes', 'No'], defaultButton='Yes',
                                       cancelButton='No', dismissString='No')
            if state == "Yes":
                return True
            else:
                return False
        else:
            return True

    def _mergeAsset(self, assetName):
        assetData = self._getData(assetName)
        if not self._checkVersionMatch(assetData["version"]):
            print "versionMatching"
            return
        absSourcePath = os.path.join(self.directory, assetName, assetData["sourcePath"])

        textureList = assetData['textureFiles']
        cmds.file(absSourcePath, i=True)

        ## if there are not textures files to handle, do not waste time
        if len(textureList) == 0:
            return

        currentProjectPath = os.path.normpath(cmds.workspace(q=1, rd=1))
        sourceImagesPath = os.path.join(currentProjectPath, "sourceimages")
        if not os.path.isdir(os.path.normpath(sourceImagesPath)):
            os.makedirs(os.path.normpath(sourceImagesPath))

        fileNodes = cmds.ls(type="file")
        for texture in textureList:
            path = os.path.join(self.directory, assetData['assetName'], texture)
            ## find the textures file Node
            for file in fileNodes:
                if os.path.normpath(cmds.getAttr("%s.fileTextureName" %file)) == path:
                    filePath, fileBase = os.path.split(path)
                    newLocation = os.path.join(sourceImagesPath, assetName)
                    if not os.path.exists(newLocation):
                        os.mkdir(newLocation)
                    newPath = os.path.normpath(os.path.join(newLocation, fileBase))

                    copyfile(path, newPath)
                    cmds.setAttr("%s.fileTextureName" %file, newPath, type="string")

    # def importAsset(self, assetName):
    #     assetData = self._getData(assetName)
    #     if not self._checkVersionMatch(assetData["version"]):
    #         return
    #     absSourcePath = os.path.join(self.directory, assetName, assetData["sourcePath"])
    #
    #     cmds.file(absSourcePath, i=True)
    #
    # def importObj(self, assetName):
    #     assetData = self._getData(assetName)
    #     absObjPath = os.path.join(self.directory, assetName, assetData["objPath"])
    #     if os.path.isfile(absObjPath):
    #         # cmds.file(absObjPath, i=True)
    #         self._importObj(absObjPath, self.importSettings)
    #
    # def importAbc(self, assetName):
    #     assetData = self._getData(assetName)
    #     absAbcPath = os.path.join(self.directory, assetName, assetData["abcPath"])
    #     if os.path.isfile(absAbcPath):
    #         # cmds.AbcImport(absAbcPath)
    #         self._importAlembic(absAbcPath, self.importSettings)
    #
    # def importFbx(self, assetName):
    #     assetData = self._getData(assetName)
    #     absFbxPath = os.path.join(self.directory, assetName, assetData["fbxPath"])
    #     if os.path.isfile(absFbxPath):
    #         # cmds.file(absFbxPath, i=True)
    #         self._importFbx(absFbxPath, self.importSettings)

    # def exportObj(self, exportPath, exportSettings, exportSelected=True):
    #     if not cmds.pluginInfo('objExport', l=True, q=True):
    #         try:
    #             cmds.loadPlugin('objExport')
    #         except:
    #             msg = "Wavefront(Obj) Export Plugin cannot be initialized. Skipping Obj export"
    #             cmds.confirmDialog(title='Plugin Error', message=msg)
    #             return False
    #
    #     opFlag = "groups={0}; ptgroups={1}; materials={2}; smoothing={3}; normals={4}".format(
    #         exportSettings["SmoothingGroups"],
    #         exportSettings["SmoothingGroups"],
    #         0,
    #         exportSettings["SmoothingGroups"],
    #         exportSettings["Normals"]
    #     )
    #     try:
    #         cmds.file(exportPath, pr=True, force=True, typ="OBJexport", es=exportSelected, op=opFlag)
    #         return True
    #     except:
    #         msg = "Cannot export OBJ for unknown reason. Skipping OBJ export"
    #         cmds.confirmDialog(title='Unknown Error', message=msg)
    #         return False
    #
    # def exportAlembic(self, exportPath, exportSettings, exportSelected=True):
    #     if not cmds.pluginInfo('AbcExport.mll', l=True, q=True):
    #         try:
    #             cmds.loadPlugin('AbcExport.mll')
    #         except:
    #             msg = "Alembic Export Plugin cannot be initialized. Skipping Alembic export"
    #             cmds.confirmDialog(title='Plugin Error', message=msg)
    #             return False
    #
    #     if exportSelected:
    #         root = ""
    #         selection = cmds.ls(sl=True)
    #         for x in selection:
    #             root = "%s-root %s " % (root, x)
    #         root = root[:-1]
    #     else:
    #         root = ""
    #
    #     file = "-file %s" %exportPath
    #     dataFormat = "-dataFormat '%s'" %exportSettings["ArchiveType"]
    #     frameRange = "-frameRange %s %s" %(exportSettings["StartFrame"], exportSettings["EndFrame"])
    #     noNormal = "" if exportSettings["Normals"] else "-noNormals"
    #     renderableOnly  = "" if exportSettings["Hidden"] else "-renderableOnly"
    #     step = "-step %s" %float(exportSettings["SamplesPerFrame"])
    #     # selection = "-selection" if exportSelected else ""
    #     selection = ""
    #     uv = "-uvWrite" if exportSettings["UVs"] else ""
    #     visibility = "-writeVisibility" if exportSettings["Visibility"] else ""
    #
    #     command = "{0} {1} {3} {4} {5} {6} {7} {8} {9}".format(file,
    #                                                            dataFormat,
    #                                                            frameRange,
    #                                                            noNormal,
    #                                                            renderableOnly,
    #                                                            step,
    #                                                            selection,
    #                                                            uv,
    #                                                            visibility,
    #                                                            root)
    #
    #     # print command
    #     #
    #     # command = "-frameRange 1 1 -uvWrite -worldSpace {0} -file {1}".format(root, exportPath)
    #
    #     try:
    #         cmds.AbcExport(j=command)
    #         return True
    #     except:
    #         msg = "Cannot export Alembic for unknown reason. Skipping Alembic export"
    #         cmds.confirmDialog(title='Unknown Error', message=msg)
    #         return False
    #
    #
    # def exportFbx(self, exportPath, exportSettings, exportSelected=True):
    #     if not cmds.pluginInfo('fbxmaya', l=True, q=True):
    #         try:
    #             cmds.loadPlugin('fbxmaya')
    #         except:
    #             msg = "FBX Export Plugin cannot be initialized. Skipping FBX export"
    #             cmds.confirmDialog(title='Plugin Error', message=msg)
    #             return False
    #
    #     opFlag = ""
    #     for item in exportSettings.items():
    #         if type(item[1]) == bool:
    #             opFlag += "%s=%s; " % (item[0], int(item[1]))
    #         elif type(item[1]) == str:
    #             opFlag += "%s='%s'; " % (item[0], item[1])
    #         else:
    #             opFlag += "%s=%s; " % (item[0], item[1])
    #     opFlag = opFlag[:-2]
    #
    #     try:
    #         cmds.file(exportPath, force=True, op=opFlag, typ="FBX export", pr=True, es=exportSelected, pmt=False)
    #         return True
    #     except:
    #         msg = "Cannot export FBX for unknown reason. Skipping FBX export"
    #         cmds.confirmDialog(title='Unknown Error', message=msg)
    #         return False


    # def loadAsset(self, assetName):
    #     assetData = self._getData(assetName)
    #     absSourcePath = os.path.join(self.directory, assetName, assetData["sourcePath"])
    #     isSceneModified = cmds.file(q=True, modified=True)
    #     if isSceneModified:
    #         state = cmds.confirmDialog(title='Scene Modified', message="Save Changes to", button=['Yes', 'No'])
    #         if state == "Yes":
    #             cmds.file(save=True)
    #         elif state == "No":
    #             pass
    #
    #     if os.path.isfile(absSourcePath):
    #         cmds.file(absSourcePath, o=True, force=True)

    def uniqueList(self, fList):
        keys = {}
        for e in fList:
            keys[e] = 1
        return keys.keys()





