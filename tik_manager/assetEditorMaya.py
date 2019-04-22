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
import maya.mel as mel
from shutil import copyfile
import json
import logging


class AssetEditorMaya(object):
    def __init__(self):
        super(AssetEditorMaya, self).__init__()
        self.directory=""


    def saveAsset(self, assetName, exportUV=True, exportOBJ=True, exportFBX=True, selectionOnly=True, mbFormat=False, notes="N/A", **info):
        """
        Saves the selected object(s) as an asset into the predefined library
        """
        # self.ssResolution = 1000
        if assetName in self.assetsList:
            msg = "This Asset already exists.\nDo you want to overwrite?"
            state = cmds.confirmDialog(title='Asset Exists', message=msg, button=['Ok', 'Cancel'])
            # cmds.warning("There are unknown nodes in the scene. Cannot proceed with %s extension. Do you want to proceed with %s?" %(ext, origExt))
            if state == "Ok":
                pass
            elif state == "Cancel":
                return


        if mbFormat:
            ext = u'.mb'
            saveFormat = "mayaBinary"
        else:
            ext = u'.ma'
            saveFormat = "mayaAscii"

        originalPath = cmds.file(q=True, sn=True)

        dump, origExt = os.path.splitext(originalPath)

        # print origExt, ext, len(cmds.ls(type="unknown"))
        # print cmds.ls(type="unknown")
        # if len(cmds.ls(type="unknown")) > 0 and ext != origExt:
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
        # tempAssetPath = os.path.join(assetDirectory, "temp.%s" %ext)

        assetAbsPath = os.path.join(assetDirectory, "%s%s" %(assetName, ext))


        # return

        if selectionOnly:
            selection = cmds.ls(sl=True, type="transform")
            if len(selection) == 0:
                cmds.confirmDialog(title="Selection Error", message="No Transform object selected", button=['Ok'])
                return
            # cmds.file(tempAssetPath, type=saveFormat, exportSelected=True)



        else:
            selection = cmds.ls()
            # cmds.file(rename=tempAssetPath)
            # cmds.file(save=True, type=saveFormat)
        #
        #
        if not os.path.exists(assetDirectory):
            os.mkdir(assetDirectory)

        # # SAVE THE TEMP FILE FIRST (Disaster Prevention)
        # # ----------------------------------------------
        # cmds.file(rename=tempAssetPath)
        # temporaryFile = cmds.file(save=True, type=saveFormat)



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
            if not cmds.pluginInfo('objExport', l=True, q=True):
                cmds.loadPlugin('objExport')

            cmds.file(os.path.join(assetDirectory, assetName), pr=True, force=True, typ="OBJexport", es=True,
                                op="groups=0; ptgroups=0; materials=0; smoothing=0; normals=0")
            objName = "{0}.obj".format(assetName)
        else:
            objName = "N/A"

        # EXPORT FBX
        # ----------
        if exportFBX:
            if not cmds.pluginInfo('fbxmaya', l=True, q=True):
                cmds.loadPlugin('fbxmaya')
            fileName = "{0}.fbx".format(os.path.join(assetDirectory, assetName))
            # mel.eval('FBXResetExport; '
            #          'FBXExportInputConnections -v false; '
            #          'FBXExportBakeComplexAnimation -v true; '
            #          'FBXExportLights -v false; '
            #          'FBXExportCameras -v false; '
            #          'FBXExportInAscii -v true; '
            #          'FBXExportFileVersion FBX201200; '
            #          'FBXExportSmoothingGroups -v false; '
            #          'FBXExportSmoothMesh -v false; '
            #          'FBXExportApplyConstantKeyReducer -v false; '
            #          'FBXExportBakeComplexAnimation -v true;  '
            #          'FBXExportBakeComplexStep -v 1;  '
            #          'FBXExportCameras -v false;')
            # mel.eval('FBXExport -f "{0}" -s'.format(fileName))
            try:
                cmds.file(fileName, force=True,
                          op="groups=1;ptgroups=1;materials=1;smoothing=1;normals=1", typ="FBX export", pr=True, es=True,
                          pmt=False)
                fbxName = "{0}.fbx".format(assetName)
            except:
                cmds.warning("Cannot export FBX for unknown reason. Skipping FBX export")
                fbxName = "N/A"

        else:
            fbxName = "N/A"

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
        dataDict['sourcePath'] = os.path.basename(assetAbsPath)
        dataDict['thumbPath'] = os.path.basename(thumbPath)
        dataDict['ssPath'] = os.path.basename(ssPath)
        dataDict['swPath'] = os.path.basename(swPath)
        dataDict['textureFiles'] = [x["Texture"] for x in textureDatabase]
        dataDict['Faces/Triangles'] = ("%s/%s" % (str(polyCount), str(tiangleCount)))
        dataDict['origin'] = originalPath
        dataDict['Notes'] = notes

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

        # else:
        #     pbPanel = cmds.getPanel(wf=True)
        #
        #     if cmds.getPanel(to=pbPanel) != "modelPanel":
        #         cmds.warning("The focus is not on a model panel, using the perspective view")
        #         return None, None, None


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

    # def replaceWithCurrentView(self, assetName):
    #     thumbPath, ssPath, swPath = self._createThumbnail(assetName, viewFit=False, selectionOnly=False)

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
            # print "validShape", validShapes[i]
            # transformNode = validShapes[i].getParent()
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
                # print "sdf", fileNodes
                # yield fileNodes
                returnList.extend(fileNodes)
        returnList = self.uniqueList(returnList)
        return returnList

    def _buildPathDatabase(self, fileNodeList, newRoot):
        for file in fileNodeList:
            oldAbsPath = os.path.normpath(cmds.getAttr("%s.fileTextureName" %file))
            filePath, fileBase = os.path.split(oldAbsPath)
            newAbsPath = os.path.normpath(os.path.join(newRoot, fileBase))

            # if oldAbsPath == newAbsPath:
            #     cmds.warning("File Node copy skipped. Target Path and Source Path is same")
            #     # textureName = self.pathOps(newLocation, "basename")
            #     textureName = os.path.basename(newAbsPath)
            #     # textures.append(textureName)
            #     continue
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

    def mergeAsset(self, assetName):

        assetData = self._getData(assetName)
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
                    cmds.setAttr("%s.fileTextureName" %file, newPath)


    def importAsset(self, assetName):
        assetData = self._getData(assetName)
        absSourcePath = os.path.join(self.directory, assetName, assetData["sourcePath"])

        cmds.file(absSourcePath, i=True)


    def importObj(self, assetName):
        assetData = self._getData(assetName)
        absObjPath = os.path.join(self.directory, assetName, assetData["objPath"])
        if os.path.isfile(absObjPath):
            cmds.file(absObjPath, i=True)

    def loadAsset(self, assetName):
        assetData = self._getData(assetName)
        absSourcePath = os.path.join(self.directory, assetName, assetData["sourcePath"])
        isSceneModified = cmds.file(q=True, modified=True)

        state = cmds.confirmDialog(title='Scene Modified', message="Save Changes to", button=['Yes', 'No'])
        if state == "Yes":
            cmds.file(save=True)
        elif state == "No":
            pass

        if os.path.isfile(absSourcePath):
            cmds.file(absSourcePath, o=True, force=True)



    # def _repathFileNodes(self, objList, newPath):
    #     for obj in objList:
    #         # Get the shading group from the selected mesh
    #         sg = cmds.listConnections(obj, type='shadingEngine')
    #         if not sg:
    #             continue
    #         allInputs = []
    #         for i in sg:
    #             allInputs += cmds.listHistory(i)
    #
    #         uniqueInputs =self.uniqueList(allInputs)
    #         fileNodes = cmds.ls(uniqueInputs, type="file")
    #         textures = self._filePass(fileNodes, newPath)
    #         yield [x for x in textures]
    #
    # def _filePass(self, fileNodes, newPath, *args):
    #     # textures = []
    #     for file in fileNodes:
    #         fullPath = os.path.normpath(cmds.getAttr("%s.fileTextureName" %file))
    #         filePath, fileBase = os.path.split(fullPath)
    #         newLocation = os.path.normpath(os.path.join(newPath, fileBase))
    #
    #         if fullPath == newLocation:
    #             cmds.warning("File Node copy skipped")
    #             # textureName = self.pathOps(newLocation, "basename")
    #             textureName = os.path.basename(newLocation)
    #             # textures.append(textureName)
    #             yield textureName
    #             continue
    #
    #         copyfile(fullPath, newLocation)
    #
    #         cmds.setAttr("%s.fileTextureName" %file, newLocation, type="string")
    #         textureName = os.path.basename(newLocation)
    #         # textures.append(textureName)
    #         yield textureName
    #     # return textures

    # def uniqueList(self, seq):  # Dave Kirby
    #     # Order preserving
    #     seen = set()
    #     return [x for x in seq if x not in seen and not seen.add(x)]

    def uniqueList(self, fList):
        keys = {}
        for e in fList:
            keys[e] = 1
        return keys.keys()





