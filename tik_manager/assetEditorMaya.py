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
from shutil import copyfile
import json
import logging


class AssetEditorMaya(object):
    def __init__(self):
        super(AssetEditorMaya, self).__init__()

    def saveAsset(self, assetName, exportUV=True, exportOBJ=False, exportFBX=False, selectionOnly=True, mbFormat=False, notes="N/A", **info):
        """
        Saves the selected object(s) as an asset into the predefined library
        """

        if mbFormat:
            ext = "mb"
            saveFormat = "mayaBinary"
        else:
            ext = "ma"
            saveFormat = "mayaAscii"

        originalPath = cmds.file(q=True, sn=True)


        # TODO // Query box to inform if the file cannot be saved different than the original format.
        # TODO // Like: "Because of the unknown nodes, current format cannot be changed. Do you want to continue with <other format here>?

        assetDirectory = os.path.join(self.directory, assetName)
        tempAssetPath = os.path.join(assetDirectory, "temp.%s" %ext)

        assetSourcePath = os.path.join(assetDirectory, "%s.%s" %(assetName, ext))




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

        # SAVE THE TEMP FILE FIRST (Disaster Prevention)
        # ----------------------------------------------
        cmds.file(rename=tempAssetPath)
        temporaryFile = cmds.file(save=True, type=saveFormat)

        # GET TEXTURES
        # ------------
        possibleFileHolders = cmds.listRelatives(selection, ad=True, type=["mesh", "nurbsSurface"])
        allFileTexturesGen = self._repathFileNodes(possibleFileHolders, assetDirectory)
        uniqueFileTextures = self.uniqueList([x for x in allFileTexturesGen][0])


        # CREATE PREVIEWS
        # ---------------
        thumbPath, ssPath, swPath = self._createThumbnail(assetName, selectionOnly=selectionOnly, viewFit=True)

        # SAVE SOURCE
        # -----------
        # return
        cmds.file(assetSourcePath, type=saveFormat, exportSelected=True)


        # EXPORT OBJ
        # ----------

        # EXPORT FBX
        # ----------

        # DATABASE
        # --------
        return
        dataDict = {}
        info['sourceProject'] = "Maya(%s)" %ext
        info['version'] = cmds.about(q=True, api=True)
        info['assetName'] = assetName
        info['objPath'] = self.pathOps(objName, "basename")
        info['maPath'] = self.pathOps(maName, "basename")
        info['thumbPath'] = os.path.basename(thumbPath)
        info['ssPath'] = os.path.basename(ssPath)
        info['swPath'] = os.path.basename(swPath)
        info['textureFiles'] = uniqueFileTextures
        info['Faces/Triangles'] = ("%s/%s" % (str(polyCount), str(tiangleCount)))
        info['sourceProject'] = originalPath
        info['Notes'] = notes


        #
        # if selectionOnly:
        #     pm.select(selection)
        #     # objName = "N/A"
        #     if exportOBJ:
        #         if not pm.pluginInfo('objExport', l=True, q=True):
        #             pm.loadPlugin('objExport')
        #         objName = pm.exportSelected(os.path.join(assetDirectory, assetName), type="OBJexport", force=True,
        #                                     options="groups=1;ptgroups=1;materials=1;smoothing=1;normals=1", pr=True,
        #                                     es=True)
        #     else:
        #         objName = "NA"
        #     maName = pm.exportSelected(os.path.join(assetDirectory, assetName), type="mayaAscii")
        #
        #     # selection for poly evaluate
        #     pm.select(possibleFileHolders)
        #     polyCount = pm.polyEvaluate(f=True)
        #     tiangleCount = pm.polyEvaluate(t=True)
        #
        # else:
        #     pm.select(d=True)
        #     # objName = "N/A"
        #     if exportOBJ:
        #         objName = pm.exportAll(os.path.join(assetDirectory, assetName), type="OBJexport", force=True,
        #                             options="groups=1;ptgroups=1;materials=1;smoothing=1;normals=1", pr=True)
        #     else:
        #         objName = "NA"
        #     maName = pm.exportAll(os.path.join(assetDirectory, assetName), type="mayaAscii")
        #
        #     # selection for poly evaluate
        #     pm.select(d=True)
        #     polyCount = pm.polyEvaluate(f=True)
        #     tiangleCount = pm.polyEvaluate(t=True)
        #
        # ## Json stuff
        #
        # info['assetName'] = assetName
        # info['objPath'] = self.pathOps(objName, "basename")
        # info['maPath'] = self.pathOps(maName, "basename")
        # info['thumbPath'] = self.pathOps(thumbPath, "basename")
        # info['ssPath'] = self.pathOps(ssPath, "basename")
        # info['swPath'] = self.pathOps(swPath, "basename")
        # info['textureFiles'] = allFileTextures
        # info['Faces/Trianges'] = ("%s/%s" % (str(polyCount), str(tiangleCount)))
        # info['sourceProject'] = originalPath
        #
        # # query the number of faces
        # # pm.polyEvaluate(f=True)
        # # Result: 16
        #
        # # query the number of triangles
        # # pm.polyEvaluate(t=True)
        #
        # propFile = os.path.join(assetDirectory, "%s.json" % assetName)
        #
        # with open(propFile, "w") as f:
        #     json.dump(info, f, indent=4)
        #
        # self[assetName] = info
        #
        # ## TODO // REVERT BACK
        # # if not originalPath == "":
        # #     pm.openFile(originalPath, force=True)
        # #     os.remove(newScenePath)

        # LOAD BACK
        # ---------
        cmds.file(originalPath, o=True, force=True)

    # def findFileNodes(self, shape):
    #     print "shape:", shape
    #
    #     def checkInputs(node):
    #         inputNodes = node.inputs()
    #         if len(inputNodes) == 0:
    #             return []
    #         else:
    #             filteredNodes = [x for x in inputNodes if x.type() != "renderLayer"]
    #             return filteredNodes
    #
    #     # geo = obj.getShape()
    #     # Get the shading group from the selected mesh
    #     try:
    #         sg = shape.outputs(type='shadingEngine')
    #     except:
    #         # if there is no sg, return en empty list
    #         return []
    #     everyInput = []
    #     for i in sg:
    #         everyInput += pm.listHistory(i)
    #
    #     everyInput = self.makeUnique(everyInput)
    #     print "everyInput", everyInput
    #
    #     fileNodes = pm.ls(everyInput, type="file")
    #     return fileNodes

    # def _findAllFileNodes(self, candidateList):
    #     for obj in candidateList:
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
    #         yield fileNodes

    def _createThumbnail(self, assetName, selectionOnly=True, viewFit=True):

        selection = cmds.ls(sl=True)
        if not selectionOnly:
            # deselect if you dont want to focus only on the selection
            selection = cmds.ls(type="transform")
            cmds.select(d=True)

        thumbPath = os.path.join(self.directory, assetName, "%s_thumb.jpg" % assetName)
        SSpath = os.path.join(self.directory, assetName, "%s_s.jpg" % assetName)
        WFpath = os.path.join(self.directory, assetName, "%s_w.jpg" % assetName)

        # make sure the viewport display is suitable
        panel = cmds.getPanel(wf=True)

        if cmds.getPanel(to=panel) != "modelPanel":
            panel = cmds.getPanel(wl="Persp View")


        cmds.modelEditor(panel, e=1, allObjects=1)
        cmds.modelEditor(panel, e=1, da="smoothShaded")
        cmds.modelEditor(panel, e=1, displayTextures=1)
        cmds.modelEditor(panel, e=1, wireframeOnShaded=0)
        if viewFit:
            cmds.viewFit()

        if selectionOnly:
            cmds.isolateSelect(panel, state=1)
            cmds.isolateSelect(panel, addSelected=True)
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
        cmds.modelEditor(panel, e=1, displayTextures=0)
        cmds.modelEditor(panel, e=1, wireframeOnShaded=1)
        cmds.playblast(completeFilename=WFpath, forceOverwrite=True, format='image', width=1600, height=1600,
                     showOrnaments=False, frame=[frame], viewer=False)

        # print panel
        cmds.select(selection)
        return thumbPath, SSpath, WFpath


    def _repathFileNodes(self, objList, newPath):
        for obj in objList:
            # Get the shading group from the selected mesh
            sg = cmds.listConnections(obj, type='shadingEngine')
            if not sg:
                continue
            allInputs = []
            for i in sg:
                allInputs += cmds.listHistory(i)

            uniqueInputs =self.uniqueList(allInputs)
            fileNodes = cmds.ls(uniqueInputs, type="file")
            textures = self._filePass(fileNodes, newPath)
            yield [x for x in textures]

    def _filePass(self, fileNodes, newPath, *args):
        # textures = []
        for file in fileNodes:
            fullPath = os.path.normpath(cmds.getAttr("%s.fileTextureName" %file))
            filePath, fileBase = os.path.split(fullPath)
            newLocation = os.path.normpath(os.path.join(newPath, fileBase))

            if fullPath == newLocation:
                cmds.warning("File Node copy skipped")
                # textureName = self.pathOps(newLocation, "basename")
                textureName = os.path.basename(newLocation)
                # textures.append(textureName)
                yield textureName
                continue

            copyfile(fullPath, newLocation)

            cmds.setAttr("%s.fileTextureName" %file, newLocation, type="string")
            textureName = os.path.basename(newLocation)
            # textures.append(textureName)
            yield textureName
        # return textures

    # def uniqueList(self, seq):  # Dave Kirby
    #     # Order preserving
    #     seen = set()
    #     return [x for x in seq if x not in seen and not seen.add(x)]

    def uniqueList(self, fList):
        keys = {}
        for e in fList:
            keys[e] = 1
        return keys.keys()





