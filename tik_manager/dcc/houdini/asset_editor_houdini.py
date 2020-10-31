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
import hou
# from shutil import copyfile

from tik_manager.dcc.houdini.core_houdini import HoudiniCoreFunctions


class AssetEditorHoudini(HoudiniCoreFunctions):
    def __init__(self):
        super(AssetEditorHoudini, self).__init__()
        self.directory=""

    def getSwName(self):
        return "Houdini"

    def _load(self, filePath, *args, **kwargs):
        """OVERRIDE default load function with load HDA"""
        node = hou.node('/obj')
        hou.hda.installFile(filePath)
        callName = "TM_%s" %os.path.splitext(os.path.basename(filePath))[0]
        node.createNode(callName)

    def saveAsset(self, assetName, exportUV=True, exportOBJ=True, exportFBX=True, exportABC=True, selectionOnly=True, sceneFormat="mb", notes="N/A", **info):
        """
        Saves the selected object(s) as an asset into the predefined library
        """
        # hou.ui.displayMessage("This Function is not available yet", title="Not yet available")
        # self.ssResolution = 1000
        if assetName == "":
            msg = "Asset Name cannot be empty"
            hou.ui.displayMessage(msg)
            return

        if assetName in self.assetsList:
            msg = "This Asset already exists.\nDo you want to overwrite?"
            state = hou.ui.displayConfirmation(msg, title='Overwrite?')
            if state:
                pass
            else:
                return

        originalPath = self._getSceneFile()

        assetDirectory = os.path.join(self.directory, assetName)
        #
        assetAbsPath = os.path.join(assetDirectory, "%s.%s" %(assetName, sceneFormat))
        #
        #
        if selectionOnly:
            selection = hou.selectedNodes()
            if len(selection) == 0:
                hou.ui.displayMessage("No Transform object selected")
                return
        else:
            rootNode = hou.node('obj')
            selection = rootNode.children()

        if not os.path.exists(assetDirectory):
            os.mkdir(assetDirectory)

        #
        # CREATE PREVIEWS
        # ---------------
        thumbPath, ssPath, swPath = self._createThumbnail(assetName, selectionOnly=selectionOnly, viewFit=True)
        #
        # # CREATE UV SNAPSHOTS
        # # ----------------

        node = hou.node('/obj')
        subnet = node.collapseIntoSubnet(selection)
        hda_node = subnet.createDigitalAsset("TM_%s" %assetName, hda_file_name=assetAbsPath, description="TM_%s" %assetName, min_num_inputs=0, max_num_inputs=0)
        hda_node.extractAndDelete()

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
            frame = self._getCurrentFrame()

            if self._exportAlembic(abcFilePath, exportSettings=self.exportSettings, timeRange=[frame, frame]):
                abcName = "{0}.abc".format(assetName)
            else:
                abcName = "N/A"

        else:
            abcName = "N/A"

        #
        # DATABASE
        # --------

        dataDict = {}
        dataDict['sourceProject'] = "Houdini(%s)" %sceneFormat
        dataDict['version'] = self._getVersion()
        dataDict['assetName'] = assetName
        dataDict['objPath'] = objName
        dataDict['fbxPath'] = fbxName
        dataDict['abcPath'] = abcName
        dataDict['sourcePath'] = os.path.basename(assetAbsPath)
        dataDict['thumbPath'] = os.path.basename(thumbPath)
        dataDict['ssPath'] = os.path.basename(ssPath)
        dataDict['swPath'] = os.path.basename(swPath)
        dataDict['textureFiles'] = ""
        dataDict['Faces/Triangles'] = ""
        dataDict['origin'] = originalPath
        dataDict['notes'] = notes

        self._setData(assetName, dataDict)

        hou.ui.displayMessage("Asset Created Successfully")

    def _createThumbnail(self, assetName, selectionOnly=True, viewFit=True):

        thumbPath = os.path.join(self.directory, assetName, "%s_thumb.jpg" % assetName)
        SSpath = os.path.join(self.directory, assetName, "%s_s.jpg" % assetName)
        WFpath = os.path.join(self.directory, assetName, "%s_w.jpg" % assetName)
        #
        selection = self._getSelection()

        # if not update:

        if not selectionOnly:
            rootNode = hou.node('obj')
            selection = rootNode.children()
            self._clearSelection()

        # get current display mode
        # Get a reference to the geometry viewer
        pane = hou.ui.curDesktop().paneTabOfType(hou.paneTabType.SceneViewer)
        # Get the display settings
        settings = pane.curViewport().settings()
        # Get the GeometryViewportDisplaySet for objects
        tmplset = settings.displaySet(hou.displaySetType.SceneObject)
        originalDisplayMode = tmplset.shadedMode()

        tmplset.setShadedMode(hou.glShadingType.Smooth)

        frame = self._getCurrentFrame()
        cur_desktop = hou.ui.curDesktop()
        scene = cur_desktop.paneTabOfType(hou.paneTabType.SceneViewer)

        # screenshot
        flip_options = scene.flipbookSettings().stash()
        flip_options.frameRange((frame, frame))
        flip_options.outputToMPlay(False)
        flip_options.output(SSpath)
        flip_options.useResolution(True)
        flip_options.resolution((1600, 1600))
        scene.flipbook(scene.curViewport(), flip_options)

        # thumb
        flip_options = scene.flipbookSettings().stash()
        flip_options.frameRange((frame, frame))
        flip_options.outputToMPlay(False)
        flip_options.output(thumbPath)
        flip_options.useResolution(True)
        flip_options.resolution((200, 200))
        scene.flipbook(scene.curViewport(), flip_options)

        tmplset.setShadedMode(hou.glShadingType.Wire)

        flip_options = scene.flipbookSettings().stash()
        flip_options.frameRange((frame, frame))
        flip_options.outputToMPlay(False)
        flip_options.output(WFpath)
        flip_options.useResolution(True)
        flip_options.resolution((1600, 1600))
        scene.flipbook(scene.curViewport(), flip_options)

        tmplset.setShadedMode(originalDisplayMode)
        return thumbPath, SSpath, WFpath

    def replaceWithCurrentView(self, assetName):

        hou.ui.displayMessage("This Function is not available yet", title="Not yet available")

    def replaceWithExternalFile(self, assetName, FilePath):
        # TODO
        pass

    def _uvSnaps(self, assetName):
        hou.ui.displayMessage("This Function is not available yet", title="Not yet available")


    def _checkVersionMatch(self, databaseVersion):
        currentVersion = self._getVersion()

        if currentVersion != databaseVersion:
            msg = "Database version ({0}) and Current version ({1}) are not matching. Do you want to try anyway?".format(databaseVersion, currentVersion)
            state = hou.ui.displayConfirmation(msg, title='Version Mismatch')
            return state
        else:
            return True

    def _mergeAsset(self, assetName):
        hou.ui.displayMessage("This Function is not available yet", title="Not yet available")

    def uniqueList(self, fList):
        keys = {}
        for e in fList:
            keys[e] = 1
        return keys.keys()





