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

# Asset save functions for 3ds Max to be used with assetLibrary
import os

from MaxPlus import FileManager as fManager
from pymxs import runtime as rt
from shutil import copyfile
from tik_manager.dcc.max.core_max import MaxCoreFunctions


class AssetEditor3dsMax(MaxCoreFunctions):
    def __init__(self):
        super(AssetEditor3dsMax, self).__init__()
        self.directory=""

    def getSwName(self):
        return "3dsMax"

    def saveAsset(self, assetName, exportUV=True, exportOBJ=True, exportFBX=True, exportABC=True, selectionOnly=True, sceneFormat="max", notes="N/A", **info):
        """
        Saves the selected object(s) as an asset into the predefined library
        """
        # self.ssResolution = 1000
        if assetName == "":
            msg = "Asset Name cannot be empty"
            state = rt.messageBox(msg, title='Info')
            return

        if assetName in self.assetsList:
            msg = "This Asset already exists.\nDo you want to overwrite?"
            state = rt.queryBox( msg, title='Manager Question')
            if state:
                pass
            else:
                return


        originalSelection = self._getSelection(asMaxArray=True)
        originalPath = self._getSceneFile()

        dump, origExt = os.path.splitext(originalPath)

        assetDirectory = os.path.join(self.directory, assetName)

        assetAbsPath = os.path.join(assetDirectory, "%s%s" %(assetName, u'.%s'%sceneFormat))


        if selectionOnly:
            selection = self._getSelection(asMaxArray=True)
            if len(selection) == 0:
                msg = "No object selected"
                rt.messageBox(msg, title='Info')
                return
        else:
            rt.select(rt.objects)
            selection = self._getSelection(asMaxArray=True)


        # originalSelection = self._getSelection(asMaxArray=True)


        if not os.path.exists(assetDirectory):
            os.mkdir(assetDirectory)

        # GET TEXTURES
        # ------------

        if selectionOnly:

            possibleFileHolders = rt.execute("selection as Array")
            filteredBitmaps = self._getFileNodes(possibleFileHolders)

        else:
            allTexture = rt.usedMaps()
            allBitmap = rt.getClassInstances(rt.bitmapTexture)
            # this makes sure only the USED bitmaps will stored
            filteredBitmaps = [x for x in allBitmap if x.filename in allTexture]


        textureDatabase = [x for x in self._buildPathDatabase(filteredBitmaps, assetDirectory)]

        self._copyTextures(textureDatabase)

        # CREATE PREVIEWS
        # ---------------
        thumbPath, ssPath, swPath = self._createThumbnail(assetName, selectionOnly=selectionOnly, viewFit=True)

        # CREATE UV SNAPSHOTS
        # ----------------
        rt.select(selection)

        if exportUV:
            self._uvSnaps(assetName)

        # SAVE SOURCE
        # -----------
        fManager.SaveSelected(assetAbsPath)

        # EXPORT OBJ
        # ----------

        if exportOBJ:
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
            fbxFilePath = os.path.join(assetDirectory, "%s.fbx" %assetName)
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

            abcFilePath = os.path.join(assetDirectory, "%s.abc" % assetName)
            frame = self._getCurrentFrame()

            if self._exportAlembic(abcFilePath, exportSettings=self.exportSettings, timeRange=[frame, frame]):
                abcName = "{0}.abc".format(assetName)
            else:
                abcName = "N/A"
        else:
            abcName = "N/A"

        # NUMERIC DATA
        # ------------

        polyCount = sum(rt.getPolygonCount(x)[0] for x in selection)
        tiangleCount = sum(rt.getPolygonCount(x)[1] for x in selection)

        versionInfo = rt.maxversion()
        vInfo = [versionInfo[0], versionInfo[1], versionInfo[2]]

        # DATABASE
        # --------

        dataDict = {}
        dataDict['sourceProject'] = "3dsMax"
        dataDict['version'] = vInfo
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

        rt.clearSelection()
        self._returnOriginal(textureDatabase)
        rt.select(originalSelection)
        rt.messageBox("Asset Created Successfully", title='Info', beep=False)

    def _createThumbnail(self, assetName, selectionOnly=True, viewFit=True):
        # ssResolution = 1000

        thumbPath = os.path.join(self.directory, assetName, "%s_thumb.jpg" % assetName)
        SSpath = os.path.join(self.directory, assetName, "%s_s.jpg" % assetName)
        WFpath = os.path.join(self.directory, assetName, "%s_w.jpg" % assetName)

        if selectionOnly:
            rt.IsolateSelection.EnterIsolateSelectionMode()
            rt.redrawViews()

        selection = self._getSelection(asMaxArray=True)
        rt.clearSelection()

        originalState = rt.viewport.GetRenderLevel()
        oWidth = 1600
        oHeight = 1600

        rt.viewport.SetRenderLevel(rt.Name("smoothhighlights"))
        rt.redrawViews()
        grabShaded = rt.gw.getViewportDib()
        rt.viewport.SetRenderLevel(rt.Name("wireframe"))
        rt.redrawViews()
        grabWire = rt.gw.getViewportDib()
        # rt.redrawViews()

        ratio = float(grabShaded.width) / float(grabShaded.height)

        if ratio < 1.0:
            new_width = oHeight * ratio
            new_height = oHeight
        elif ratio > 1.0:
            new_width = oWidth
            new_height = oWidth / ratio
        else:
            new_width = oWidth
            new_height = oWidth

        resizeFrameShaded = rt.bitmap(new_width, new_height, color=rt.color(0, 0, 0))
        rt.copy(grabShaded, resizeFrameShaded)

        resizeFrameWire = rt.bitmap(new_width, new_height, color=rt.color(0, 0, 0))
        rt.copy(grabWire, resizeFrameWire)

        ssFrame = rt.bitmap(oWidth, oHeight, color=rt.color(0, 0, 0))
        wfFrame = rt.bitmap(oWidth, oHeight, color=rt.color(0, 0, 0))

        xOffset = (oWidth - resizeFrameShaded.width) / 2
        yOffset = (oHeight - resizeFrameShaded.height) / 2

        rt.pasteBitmap(resizeFrameShaded, ssFrame, rt.point2(0, 0), rt.point2(xOffset, yOffset))
        rt.pasteBitmap(resizeFrameWire, wfFrame, rt.point2(0, 0), rt.point2(xOffset, yOffset))

        thumbFrame = rt.bitmap(200, 200, color=rt.color(0, 0, 0))
        rt.copy(ssFrame, thumbFrame)

        rt.display(thumbFrame)

        thumbFrame.filename = thumbPath
        rt.save(thumbFrame)
        rt.close(thumbFrame)

        ssFrame.filename = SSpath
        rt.save(ssFrame)
        rt.close(ssFrame)

        wfFrame.filename = WFpath
        rt.save(wfFrame)
        rt.close(wfFrame)

        # switch to original view
        rt.viewport.SetRenderLevel(originalState)

        rt.IsolateSelection.ExitIsolateSelectionMode()
        rt.redrawViews()

        return thumbPath, SSpath, WFpath

    def replaceWithCurrentView(self, assetName):

        thumbPath = os.path.join(self.directory, assetName, "%s_thumb.jpg" % assetName)
        SSpath = os.path.join(self.directory, assetName, "%s_s.jpg" % assetName)
        WFpath = os.path.join(self.directory, assetName, "%s_w.jpg" % assetName)

        self._createThumbnail(assetName, selectionOnly=False)

    def replaceWithExternalFile(self, assetName, FilePath):
        # TODO
        pass

    def _uvSnaps(self, assetName):
        originalSelection = rt.execute("selection as array")
        validShapes = rt.execute("for o in selection where superClassOf o == geometryClass collect o")

        if len(validShapes) > 10:
            msg = "There are %s objects for UV snapshots.\nAre you sure you want to include snapshots to the Asset?" %(len(validShapes))
            state = rt.queryBox( msg, title='Too many objects for UV Snapshot')
            if state:
                pass
            else:
                return


        assetDirectory = os.path.join(self.directory, assetName)
        UVdir = os.path.join(assetDirectory, "UV_snaps")

        if not os.path.isdir(os.path.normpath(UVdir)):
            os.makedirs(os.path.normpath(UVdir))


        rt.execute("max modify mode")

        for i in validShapes:
            objName = i.name
            UVpath = os.path.join(UVdir, '%s_uv.jpg' % objName)
            rt.select(i)
            defUnwrapMod = rt.Unwrap_UVW()
            rt.addModifier(i, defUnwrapMod)
            defUnwrapMod.setMapChannel = 1
            defUnwrapMod.renderuv_fillmode = 0
            defUnwrapMod.renderuv_seamColor = rt.Name("green")
            defUnwrapMod.renderuv_showframebuffer = False
            defUnwrapMod.renderuv_force2sided = False
            defUnwrapMod.renderuv_fillColor = rt.Name("black")
            defUnwrapMod.renderuv_showoverlap = False
            defUnwrapMod.renderuv_overlapColor = rt.Name("red")
            defUnwrapMod.renderuv_edgeColor = rt.Name("white")
            defUnwrapMod.renderuv_visibleedges = True
            defUnwrapMod.renderuv_invisibleedges = False
            defUnwrapMod.renderuv_seamedges = False
            defUnwrapMod.renderUV(UVpath)
            rt.deleteModifier(i, defUnwrapMod)

        rt.select(originalSelection)


    def _getFileNodes(self, objList):
        returnList = []
        for x in objList:
            map(lambda x:(returnList.append(x)), rt.getClassInstances(rt.bitmapTexture, target=x, asTrackViewPick=False))
        return returnList

    def _buildPathDatabase(self, fileNodeList, newRoot):
        for file in fileNodeList:
            oldAbsPath = os.path.normpath(file.filename)
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
                data["FileNode"].filename = data["NewPath"]

    def _returnOriginal(self, pathDatabase):
        for data in pathDatabase:
            # print data
            data["FileNode"].filename = data["OldPath"]

    def _checkVersionMatch(self, databaseVersion):
        currentVersion = rt.maxversion()

        if currentVersion != databaseVersion:
            msg = "Database version ({0}) and Current version ({1}) are not matching. Do you want to try anyway?".format(databaseVersion, currentVersion)
            state = rt.queryBox(msg, title='Version Mismatch')
            if state:
                return True
            else:
                return False
        else:
            return True

    def _mergeAsset(self, assetName):
        assetData = self._getData(assetName)
        if not self._checkVersionMatch(assetData["version"]):
            return
        absSourcePath = os.path.join(self.directory, assetName, assetData["sourcePath"])

        textureList = assetData['textureFiles']
        self._import(absSourcePath, prompt=False)

        ## if there are not textures files to handle, do not waste time
        if len(textureList) == 0:
            return
        # currentProjectPath = self._getProject()
        currentProjectPath = self.projectDir
        sourceImagesPath = os.path.join(currentProjectPath, "sourceimages")
        if not os.path.isdir(os.path.normpath(sourceImagesPath)):
            os.makedirs(os.path.normpath(sourceImagesPath))

        fileNodes = rt.getClassInstances(rt.bitmapTexture)
        for texture in textureList:
            path = os.path.join(self.directory, assetData['assetName'], texture)
            ## find the textures file Node
            for file in fileNodes:
                if os.path.normpath(file.fileName) == path:
                    filePath, fileBase = os.path.split(path)
                    newLocation = os.path.join(sourceImagesPath, assetName)
                    if not os.path.exists(newLocation):
                        os.mkdir(newLocation)
                    newPath = os.path.normpath(os.path.join(newLocation, fileBase))

                    copyfile(path, newPath)
                    file.fileName = newPath

    def uniqueList(self, fList):
        keys = {}
        for e in fList:
            keys[e] = 1
        return keys.keys()

