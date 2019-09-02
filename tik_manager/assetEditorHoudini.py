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

from tik_manager.coreFunctions.coreFunctions_Houdini import HoudiniCoreFunctions


# TODO : Subclass MayaCoreFunctions
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
        ## TODO // ASSET CREATE
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

        # if hou.isApprentice():
        #     sceneFormat="hipnc"

        # if self._isSceneModified():
        #     msg = "Current scene is modified. It must be saved before continue.\nDo you wish to save?"
        #     state = hou.ui.displayConfirmation(msg, title='Save?')
        #     if not state:
        #         return


        originalPath = self._getSceneFile()


        # if sceneFormat == "mb":
        #     ext = u'.mb'
        #     saveFormat = "mayaBinary"
        # else:
        #     ext = u'.ma'
        #     saveFormat = "mayaAscii"
        #
        #
        # dump, origExt = os.path.splitext(originalPath)
        #
        # if len(cmds.ls(type="unknown")) > 0 and ext != origExt:
        #     msg = "There are unknown nodes in the scene. Cannot proceed with %s extension.\n\nDo you want to continue with %s?" %(ext, origExt)
        #     state = cmds.confirmDialog(title='Cannot Continue', message=msg, button=['Ok', 'Cancel'])
        #     # cmds.warning("There are unknown nodes in the scene. Cannot proceed with %s extension. Do you want to proceed with %s?" %(ext, origExt))
        #     if state == "Ok":
        #         if origExt == u'.mb':
        #             ext = u'.mb'
        #             saveFormat = "mayaBinary"
        #         else:
        #             ext = u'.ma'
        #             saveFormat = "mayaAscii"
        #
        #     elif state == "Cancel":
        #         return
        #
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

        # # GET TEXTURES
        # # ------------
        #
        # possibleFileHolders = cmds.listRelatives(selection, ad=True, type=["mesh", "nurbsSurface"], fullPath=True)
        # allFileNodes = self._getFileNodes(possibleFileHolders)
        #
        # textureDatabase = [x for x in self._buildPathDatabase(allFileNodes, assetDirectory)]
        #
        # self._copyTextures(textureDatabase)
        #
        # CREATE PREVIEWS
        # ---------------
        thumbPath, ssPath, swPath = self._createThumbnail(assetName, selectionOnly=selectionOnly, viewFit=True)
        #
        # # CREATE UV SNAPSHOTS
        # # ----------------
        # if exportUV:
        #     self._uvSnaps(assetName)
        #
        # SAVE SOURCE
        # -----------
        # cmds.file(assetAbsPath, type=saveFormat, exportSelected=True, force=True)
        # p = selection[0].parent()
        # p.saveChildrenToFile(selection,"",assetAbsPath)
        # p.saveChildrenToFile(selection,"",assetAbsPath)
        # p.saveItemsToFile(selection, assetAbsPath)
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

        # # NUMERIC DATA
        # # ------------
        # cmds.select(hi=True)
        # polyCount = cmds.polyEvaluate(f=True)
        # tiangleCount = cmds.polyEvaluate(t=True)
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
        # dataDict['thumbPath'] = ""
        dataDict['ssPath'] = os.path.basename(ssPath)
        # dataDict['ssPath'] = ""
        dataDict['swPath'] = os.path.basename(swPath)
        # dataDict['swPath'] = ""
        # dataDict['textureFiles'] = [x["Texture"] for x in textureDatabase]
        dataDict['textureFiles'] = ""
        # dataDict['Faces/Triangles'] = ("%s/%s" % (str(polyCount), str(tiangleCount)))
        dataDict['Faces/Triangles'] = ""
        dataDict['origin'] = originalPath
        dataDict['notes'] = notes

        self._setData(assetName, dataDict)

        # cmds.select(d=True)
        # self._returnOriginal(textureDatabase)

        # self.scanAssets() # scanning issued at populate function on ui class

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
        #
        #
        # ## CREATE A CUSTOM PANEL WITH DESIRED SETTINGS
        #
        # try:
        #     currentCam = cmds.modelPanel(cmds.getPanel(wf=True), q=True, cam=True)
        #     vRenderer = cmds.modelEditor(cmds.getPanel(wf=True), q=True, rnm=True)
        # except RuntimeError:
        #     currentCam = u'persp'
        #     vRenderer = 'vp2Renderer'
        #
        # tempWindow = cmds.window(title="AssetLibrary_SS",
        #                        widthHeight=(ssResolution * 1.1, ssResolution * 1.1),
        #                        tlc=(0, 0))
        #
        # cmds.paneLayout()
        # pbPanel = cmds.modelPanel(camera=currentCam)
        # cmds.showWindow(tempWindow)
        # cmds.setFocus(pbPanel)
        # cmds.modelEditor(pbPanel, edit=True, rendererName=vRenderer)
        #
        # ########################################
        #
        #
        # cmds.modelEditor(pbPanel, e=1, allObjects=1)
        # cmds.modelEditor(pbPanel, e=1, da="smoothShaded")
        # cmds.modelEditor(pbPanel, e=1, displayTextures=1)
        # cmds.modelEditor(pbPanel, e=1, wireframeOnShaded=0)
        # if viewFit:
        #     cmds.viewFit()
        #
        # if selectionOnly:
        #     cmds.isolateSelect(pbPanel, state=1)
        #     cmds.isolateSelect(pbPanel, addSelected=True)
        # # temporarily deselect
        # cmds.select(d=True)
        #
        # cmds.setAttr("defaultRenderGlobals.imageFormat", 8)  # This is the value for jpeg
        #
        # frame = cmds.currentTime(query=True)
        # # thumb
        # cmds.playblast(completeFilename=thumbPath, forceOverwrite=True, format='image', width=200, height=200,
        #              showOrnaments=False, frame=[frame], viewer=False)
        #
        # # screenshot
        # cmds.playblast(completeFilename=SSpath, forceOverwrite=True, format='image', width=1600, height=1600,
        #              showOrnaments=False, frame=[frame], viewer=False)
        #
        # # Wireframe
        # cmds.modelEditor(pbPanel, e=1, displayTextures=0)
        # cmds.modelEditor(pbPanel, e=1, wireframeOnShaded=1)
        # cmds.playblast(completeFilename=WFpath, forceOverwrite=True, format='image', width=1600, height=1600,
        #              showOrnaments=False, frame=[frame], viewer=False)
        #
        # ## remove window when pb is donw
        # cmds.deleteUI(tempWindow)
        #
        # # print panel
        # cmds.select(selection)
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





