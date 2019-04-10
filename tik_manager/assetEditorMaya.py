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
import pymel.core as pm
import json
import logging
import assetLibrary
reload(assetLibrary)
from assetLibrary import AssetLibrary
from assetLibrary import MainUI as baseUI
from assetLibrary import LibraryTab as baseLibraryUI




__author__ = "Arda Kutlu"
__copyright__ = "Copyright 2018, Asset Library"
__credits__ = []
__license__ = "GPL"
__maintainer__ = "Arda Kutlu"
__email__ = "ardakutlu@gmail.com"
__status__ = "Development"

logging.basicConfig()
logger = logging.getLogger('AssetLibrary')
logger.setLevel(logging.WARNING)


class AssetEditor(assetLibrary.AssetLibrary):
    def __init__(self):
        super(AssetEditor, self).__init__()

    def saveAsset(self, assetName, screenshot=True, moveCenter=False, selectionOnly=True, exportUV=True, exportOBJ=True, **info):
        """
        Saves the selected object(s) as an asset into the predefined library
        Args:
            assetName: (Unicode) Asset will be saved as with this name
            screenshot: (Bool) If true, screenshots (Screenshot, Thumbnail, Wireframe, UV Snapshots) will be taken with playblast. Default True
            directory: (Unicode) Default Library location. Default is predefined outside of this class
            moveCenter: (Bool) If True, selected object(s) will be moved to World 0 point. Pivot will be the center of selection. Default False
            **info: (Any) Extra information which will be hold in the .json file

        Returns:
            None

        """
        logger.info("Saving the asset")
        originalPath = pm.sceneName()


        assetDirectory = os.path.join(self.directory, assetName)

        ## TODO // in a scenario where a group object selected, select all meshes under the group recursively (you did that before somewhere else)
        if selectionOnly:
            selection = pm.ls(sl=True, type="transform")
            if len(selection) == 0:
                pm.warning("No object selected, nothing to do")
                return
        else:
            selection = pm.ls(type="transform")


        if not os.path.exists(assetDirectory):
            os.mkdir(assetDirectory)

        possibleFileHolders = pm.listRelatives(selection, ad=True, type=["mesh", "nurbsSurface"])

        allFileTextures = []
        for obj in possibleFileHolders:
            fileNodes = self.findFileNodes(obj)
            fileTextures = self.filePass(fileNodes, assetDirectory)
            allFileTextures += fileTextures

        allFileTextures = self.makeUnique(allFileTextures)

        if moveCenter:
            pm.select(selection)
            slGrp = pm.group(name=assetName)

            pm.xform(slGrp, cp=True)

            tempLoc = pm.spaceLocator()
            tempPo = pm.pointConstraint(tempLoc, slGrp)
            pm.delete(tempPo)
            pm.delete(tempLoc)

        thumbPath, ssPath, swPath = self.previewSaver(assetName, assetDirectory, selectionOnly=selectionOnly, uvSnap=exportUV)


        if selectionOnly:
            pm.select(selection)
            # objName = "N/A"
            if exportOBJ:
                if not pm.pluginInfo('objExport', l=True, q=True):
                    pm.loadPlugin('objExport')
                objName = pm.exportSelected(os.path.join(assetDirectory, assetName), type="OBJexport", force=True,
                                            options="groups=1;ptgroups=1;materials=1;smoothing=1;normals=1", pr=True,
                                            es=True)
            else:
                objName = "NA"
            maName = pm.exportSelected(os.path.join(assetDirectory, assetName), type="mayaAscii")

            # selection for poly evaluate
            pm.select(possibleFileHolders)
            polyCount = pm.polyEvaluate(f=True)
            tiangleCount = pm.polyEvaluate(t=True)

        else:
            pm.select(d=True)
            # objName = "N/A"
            if exportOBJ:
                objName = pm.exportAll(os.path.join(assetDirectory, assetName), type="OBJexport", force=True,
                                    options="groups=1;ptgroups=1;materials=1;smoothing=1;normals=1", pr=True)
            else:
                objName = "NA"
            maName = pm.exportAll(os.path.join(assetDirectory, assetName), type="mayaAscii")

            # selection for poly evaluate
            pm.select(d=True)
            polyCount = pm.polyEvaluate(f=True)
            tiangleCount = pm.polyEvaluate(t=True)

        ## Json stuff

        info['assetName'] = assetName
        info['objPath'] = self.pathOps(objName, "basename")
        info['maPath'] = self.pathOps(maName, "basename")
        info['thumbPath'] = self.pathOps(thumbPath, "basename")
        info['ssPath'] = self.pathOps(ssPath, "basename")
        info['swPath'] = self.pathOps(swPath, "basename")
        info['textureFiles'] = allFileTextures
        info['Faces/Trianges'] = ("%s/%s" % (str(polyCount), str(tiangleCount)))
        info['sourceProject'] = originalPath

        # query the number of faces
        # pm.polyEvaluate(f=True)
        # Result: 16

        # query the number of triangles
        # pm.polyEvaluate(t=True)

        propFile = os.path.join(assetDirectory, "%s.json" % assetName)

        with open(propFile, "w") as f:
            json.dump(info, f, indent=4)

        self[assetName] = info

        ## TODO // REVERT BACK
        # if not originalPath == "":
        #     pm.openFile(originalPath, force=True)
        #     os.remove(newScenePath)

class MainUI(baseUI):
    def __init__(self):
        super(MainUI, self).__init__(viewOnly=False)

        # self.viewOnly=False

        # self.manager = MayaManager()
        # problem, msg = self.manager._checkRequirements()
        # if problem:
        #     self.close()
        #     self.deleteLater()
        #
        # self.callbackIDList=[]
        # if self.isCallback:
        #     self.callbackIDList = self.manager._createCallbacks(self.isCallback, self.windowName)
        #
        # self.buildUI()
        # self.initMainUI(newborn=True)
        # self.extraMenus()



