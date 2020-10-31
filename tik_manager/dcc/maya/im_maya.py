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

"""As a part of SceneManager, ImageManager checks the scene for possible errors before
sending it to Deadline render manager.
On initialization, script changes the image name template according to the defined template
and checks the scene for possible errors
Double Clicking on warnings open up the related dialog.
"""


import tik_manager._version as _version
# import pymel.core as pm
import maya.cmds as cmds
import os
os.environ["FORCE_QT5"]="0"
import maya.mel as mel

from tik_manager.core.sm_root import RootManager
# from SmMaya import MayaCoreFunctions as CoreFunctions
from tik_manager.dcc.maya.core_maya import MayaCoreFunctions

import logging


import tik_manager.ui.Qt as Qt
from tik_manager.ui.Qt import QtWidgets, QtCore, QtGui
from maya import OpenMayaUI as omui
if Qt.__binding__ == "PySide":
    from shiboken import wrapInstance
elif Qt.__binding__.startswith('PyQt'):
    from sip import wrapinstance as wrapInstance
else:
    from shiboken2 import wrapInstance

__author__ = "Arda Kutlu"
__copyright__ = "Copyright 2018, Image Manager for Maya Project"
__credits__ = []
__license__ = "GPL"
__maintainer__ = "Arda Kutlu"
__email__ = "ardakutlu@gmail.com"
__status__ = "Development"

windowName = "Image Manager v%s" %_version.__version__

logging.basicConfig()
logger = logging.getLogger('imMaya')
logger.setLevel(logging.DEBUG)

def parseTemplate(template):
    pass

def getMayaMainWindow():
    """
    Gets the memory adress of the main window to connect Qt dialog to it.
    Returns:
        (long) Memory Adress
    """
    win = omui.MQtUtil_mainWindow()
    ptr = wrapInstance(long(win), QtWidgets.QMainWindow)
    return ptr

class ImageManager(RootManager, MayaCoreFunctions):
    def __init__(self):
        super(ImageManager, self).__init__()

        self.swName = "Maya"
        self.init_paths(self.swName)
        self.init_database()

        self.sceneInfo = self.getOpenSceneInfo()
        if not self.sceneInfo:
            msg = "Scene is not a Base Scene. Save it using SceneManager"
            self._exception(360, msg)
            # logger.warning("This is not a Base Scene")
            return

        self.renderFlag = True



        # self.folderTemplate = "{4}/{0}/{1}/{3}/{2}/"
        self.folderTemplate = "{0}{1}/{3}/{2}/"
        self.nameTemplate = "{0}_{1}_{2}_{3}_"
        self.supportedRenderers = ["arnold", "vray", "mentalRay", "redshift"]
        self.currentRenderer = ""

        # 0 => subProject
        # 1 => shotName
        # 2 => RenderLayer
        # 3 => Version
        # 4 => images directory,

        self.resolvedName=""
        self.minorProblemNodes = []
        self.majorProblemNodes = []
        self.initRenderer()
        self.foolerMaster()

    def getSoftwarePaths(self):
        """Overriden function"""
        logger.debug("Func: getSoftwarePaths")
        softwareDatabaseFile = os.path.normpath(os.path.join(self.getSharedSettingsDir(), "softwareDatabase.json"))
        softwareDB = self._loadJson(softwareDatabaseFile)
        return softwareDB["Maya"]

    def getSceneFile(self):
        """Overriden function"""
        # Gets the current scene path ("" if untitled)
        s_path = cmds.file(q=True, sn=True)
        norm_s_path = os.path.normpath(s_path)
        return norm_s_path

    def resolvePath(self, renderer="default"):
        projectImgDir = os.path.join(self.projectDir, "images")
        # folderCheck(projectImgDir)

        if renderer == "vray":
            renderlayer="<Layer>"
        elif renderer == "arnold":
            renderlayer="<RenderLayer>_<RenderPass>"
        else:
            renderlayer="<RenderLayer>"

        subProject = "" if self.sceneInfo["subProject"] == "None" else "%s\\" %self.sceneInfo["subProject"]

        shotName = self.sceneInfo["shotName"]
        version=self.sceneInfo["version"]

        logger.warning(subProject)
        logger.warning(shotName)
        logger.warning(version)
        logger.warning(self.folderTemplate)

        # self.folderTemplate = os.path.normpath(self.folderTemplate.format(subProject,shotName,renderlayer,version,projectImgDir))
        self.folderTemplate = os.path.normpath(self.folderTemplate.format(subProject,shotName,renderlayer,version))
        self.nameTemplate = (self.nameTemplate.format(subProject,shotName,renderlayer,version)).lstrip("_")

        return os.path.join(self.folderTemplate, self.nameTemplate)

    def initRenderer(self):
        # self.currentRenderer = pm.getAttr('defaultRenderGlobals.currentRenderer')
        self.currentRenderer = cmds.getAttr('defaultRenderGlobals.currentRenderer')
        logger.debug("Renderer:%s" %self.currentRenderer)

        if self.currentRenderer == "arnold":
            if cmds.objExists('defaultArnoldDriver'):
                # set the image format to 'exr'
                cmds.setAttr('defaultArnoldDriver.ai_translator', 'exr', type='string')

                # set the compression to 'zips'
                cmds.setAttr("defaultArnoldDriver.exrCompression" , 2)
                # Frame/Animation ext and Frame Padding
                cmds.setAttr("defaultRenderGlobals.outFormatControl", 0)
                cmds.setAttr("defaultRenderGlobals.animation", 1)
                cmds.setAttr("defaultRenderGlobals.putFrameBeforeExt", 1)
                cmds.setAttr("defaultRenderGlobals.extensionPadding", 4)
                # set File Name Prefix
                self.resolvedName = self.resolvePath(self.currentRenderer)
                cmds.setAttr("defaultRenderGlobals.imageFilePrefix", self.resolvedName, type='string')
                return
            else:
                logger.warning("Cannot Find arnold settings file. Switch between render engines and try again")
                self.resolvedName = ("defaultArnoldDriver missing. Switch between render engines and try again")

        elif self.currentRenderer == "vray":
            if cmds.objExists('vraySettings'):
                # set the image format to 'exr'
                cmds.setAttr('vraySettings.imageFormatStr', 'exr', type='string')
                # set the compression to 'zips'
                cmds.setAttr("vraySettings.imgOpt_exr_compression", 3)
                # Frame/Animation ext and Frame Padding
                cmds.setAttr("vraySettings.animType", 1)
                cmds.setAttr("vraySettings.fileNamePadding", 4)
                # set File Name Prefix
                self.resolvedName = self.resolvePath(self.currentRenderer)
                cmds.setAttr("vraySettings.fileNamePrefix", self.resolvedName, type='string')
                return
            else:
                logger.warning("Cannot Find vray settings file. Switch between render engines and try again")
                self.resolvedName = ("vraySettings missing. Switch between render engines and try again")

        elif self.currentRenderer == "mentalRay":
            if cmds.objExists('defaultRenderGlobals'):
                # set the image format to 'exr'
                cmds.setAttr("defaultRenderGlobals.imageFormat", 51)
                cmds.setAttr("defaultRenderGlobals.imfPluginKey", "exr")
                cmds.setAttr("defaultRenderGlobals.imageCompression", 0)
                # set the compression to 'zips'
                cmds.setAttr("mentalrayGlobals.imageCompression", 5)
                # Frame/Animation ext and Frame Padding
                cmds.setAttr("defaultRenderGlobals.outFormatControl", 0)
                cmds.setAttr("defaultRenderGlobals.animation", 1)
                cmds.setAttr("defaultRenderGlobals.putFrameBeforeExt", 1)
                cmds.setAttr("defaultRenderGlobals.extensionPadding", 4)
                # set File Name Prefix
                self.resolvedName = self.resolvePath()
                cmds.setAttr("defaultRenderGlobals.imageFilePrefix", self.resolvedName, type='string')
                return
            else:
                logger.warning("Cannot Find defaultRenderGlobals file. Switch between render engines and try again")
                self.resolvedName = ("defaultRenderGlobals missing. Switch between render engines and try again")



        elif self.currentRenderer == "redshift":
            if cmds.objExists('redshiftOptions'):
                # set the image format to 'exr'
                cmds.setAttr("redshiftOptions.imageFormat", 1)
                # set the compression to 'zips'
                cmds.setAttr("redshiftOptions.exrCompression", 3)
                cmds.setAttr("redshiftOptions.exrIsTiled", 0)
                # Frame/Animation ext and Frame Padding
                cmds.setAttr("defaultRenderGlobals.outFormatControl", 0)
                cmds.setAttr("defaultRenderGlobals.animation", 1)
                cmds.setAttr("defaultRenderGlobals.putFrameBeforeExt", 1)
                cmds.setAttr("defaultRenderGlobals.extensionPadding", 4)
                # set File Name Prefix
                self.resolvedName = self.resolvePath()
                cmds.setAttr("defaultRenderGlobals.imageFilePrefix", self.resolvedName, type='string')
                return
            else:
                logger.warning("Cannot Find redshiftOptions file. Switch between render engines and try again")
                self.resolvedName = ("redshiftOptions missing. Switch between render engines and try again")

        else:
            logger.warning("Render Engine is not supported. Skipping Engine specific settings")
            self.resolvedName = ("Render Engine is NOT supported, set image path manually")
            return
            pass

    def getAttrInLayer(self, node, attr, layer, returnAnyWay=False):
        nodeAttr = "%s.%s" % (node, attr)
        connection_list = cmds.listConnections(nodeAttr, plugs=True)
        if layer == "defaultRenderLayer":
            return cmds.getAttr(nodeAttr)  # return

        if not connection_list:  # if it cannot exist in any layer
            if returnAnyWay:
                return cmds.getAttr(nodeAttr)  # return
            else:
                return None

        for connection in connection_list:

            attr_component_list = connection.split(".")
            if attr_component_list[0] == layer:  # eger bu layerdaysa
                nodeAttr = ".".join(attr_component_list[0:-1])
                return cmds.getAttr("%s.value" % nodeAttr)  # return
            else:
                if returnAnyWay:
                    return cmds.getAttr(nodeAttr)  # return
                else:
                    return None

    def foolCheckImagePlane(self, renderLayerList):
        severity = 0

        # Calculate the maximum possible severity

        allImagePlanes = cmds.ls(type="imagePlane")

        if len(allImagePlanes) <= 0:  # if there are no image planes, no need to continue
            return 0
            # return severity, maxSeverity
        for layer in renderLayerList:
            for ip in allImagePlanes:
                dMode = self.getAttrInLayer(ip, "displayMode", layer=layer, returnAnyWay=False)
                if not dMode == None:
                    if dMode != 0:
                        msg = "ImagePlane (%s) in %s is renderable!" % (ip, layer)
                        if len(renderLayerList) > 1 and layer == "defaultRenderLayer":
                            # self.ImagePlaneSeverity += 1
                            severity += 1
                            # object, renderlayer, command, message
                            self.minorProblemNodes.append([ip, layer, "openAEWindow;", msg])  # AE is for attribute Editor
                        else:
                            # self.ImagePlaneSeverity += 7
                            severity += 7
                            self.majorProblemNodes.append([ip, layer, "openAEWindow;", msg])  # AE is for attribute Editor

        return severity

    def foolCheckRenderCamera(self, renderLayerList):
        severity = 0
        allCameras = cmds.ls(type="camera")

        for layer in renderLayerList:
            renderCameras = []  # reset renderable camera list for each render layer
            # get the renderable cameras
            for x in allCameras:

                rMode = self.getAttrInLayer(x, "renderable", layer=layer, returnAnyWay=True)
                if rMode:
                    renderCameras.append(x)
            for rcam in renderCameras:
                # check if the perspective camera is among renderable cameras
                if "perspShape" in rcam:
                    if len(renderCameras) > 1:
                        msg = "Multiple Renderable Cameras => (%s)" % layer
                        self.minorProblemNodes.append([rcam, layer, "unifiedRenderGlobalsWindow;", msg])
                        severity += 5
                    else:
                        msg = "Perspective Camera is renderable (%s)" % layer
                        self.minorProblemNodes.append([rcam, layer, "unifiedRenderGlobalsWindow;", msg])
                        severity += 1

            if len(renderCameras) == 0:
                msg = "No renderable cameras(%s)" % layer
                severity += 10
                self.majorProblemNodes.append([None, None, "", msg])
        # Calculate the maximum possible severity
        return severity

    def foolCheckRenderSettings(self, renderLayerList):
        severity = 0

        # get the timeslider range:
        startFrame = cmds.playbackOptions(q=True, minTime=True)
        endFrame = cmds.playbackOptions(q=True, maxTime=True)

        activeRenderLayer = cmds.editRenderLayerGlobals(q=True, currentRenderLayer=True)

        # go through all renderlayers:
        for layer in renderLayerList:
            try:
                cmds.editRenderLayerGlobals(currentRenderLayer=layer)
            except RuntimeError:
                continue
            # get paths
            comparePath = cmds.renderSettings(firstImageName=True, lastImageName=True, fp=True)
            filePath, fileBase = os.path.split(comparePath[0])

            ## COmmon for all render engines
            # get the render range
            animStart = cmds.getAttr("defaultRenderGlobals.startFrame")
            animEnd = cmds.getAttr("defaultRenderGlobals.endFrame")
            if animStart != startFrame or animEnd != endFrame:
                msg = "Timeslider range and Render ranges are different (%s)" %layer
                self.minorProblemNodes.append(
                    ["defaultRenderGlobals", layer, "unifiedRenderGlobalsWindow;", msg])  # RG is for Render Globals
                severity += 1
        return severity

    def foolCheckPaths(self):

        acceptables = ["mesh", "shape", "transform"]
        def isAssigned(fileNode):

            try:
                matInfo = cmds.listConnections(fileNode, s=False, d=True, type="materialInfo")[0]
            except:

                matInfo = None

            if not matInfo == None:
                sGroup = cmds.listConnections(matInfo, type="shadingEngine")[0]

                if len(sGroup) > 0:
                    try:
                        for i in sGroup:
                            if i.type() in acceptables:
                                return True
                    except:
                        return False
                else:
                    return False
            return False

        severity = 0

        # return severity
        validDrive = "M:"
        projectsFolder = os.path.abspath(os.path.join(self.projectDir, os.pardir))
        allImagePlanes = cmds.ls(type="imagePlane")
        ### TODO // PATHS may NOT WORK with LINUX os
        currentProjectPath = os.path.normpath(cmds.workspace(q=1, rd=1))
        # check for the image planes:
        ipPPcount = 0.0
        for ip in allImagePlanes:
            fullPath = os.path.normpath(cmds.getAttr("%s.imageName" %ip))
            filePath, fileBase = os.path.split(fullPath)
            # fileDrive, tmp = os.path.splitdrive(filePath)
            if currentProjectPath not in filePath:
                ipPPcount += 1
                msg = "ImagePlane (%s) is not in the Project Folder" % ip
                self.minorProblemNodes.append([ip, "defaultRenderLayer", "openAEWindow;", msg])
                severity += 3
            if projectsFolder not in filePath:
                msg = "Image Plane file is NOT even in %s !!! (%s)" % (projectsFolder,fileBase)
                self.majorProblemNodes.append([ip, "defaultRenderLayer", "openAEWindow;", msg])
                severity += 9
        allFileNodes = cmds.ls(type="file")
        fnPPcount = 0.0
        for fn in allFileNodes:
            fullPath = os.path.normpath(cmds.getAttr("%s.fileTextureName" %fn))
            filePath, fileBase = os.path.split(fullPath)
            if currentProjectPath not in filePath:

                fnPPcount += 1
                msg = "Texture File (%s => %s) is not in the Project Folder" % (fn, fileBase)
                if (isAssigned(fn)):

                    self.majorProblemNodes.append([fn, "defaultRenderLayer", "openAEWindow;", msg])
                    severity += 6
                else:

                    self.minorProblemNodes.append([fn, "defaultRenderLayer", "openAEWindow;", msg])
                    severity += 1
            if projectsFolder not in filePath:
                if (isAssigned(fn)):
                    msg = "Texture File (ASSIGNED) is NOT even in %s !!! (%s)" % (projectsFolder,fileBase)
                    self.majorProblemNodes.append([fn, "defaultRenderLayer", "openAEWindow;", msg])
                    severity += 10
                else:
                    msg = "Texture File (unassigned) is NOT even in %s !!! (%s)" % (projectsFolder,fileBase)
                    self.minorProblemNodes.append([fn, "defaultRenderLayer", "openAEWindow;", msg])
                    severity += 1

        # check for the cache files:
        allCacheFiles = cmds.ls(type="cacheFile")
        cPPcount = 0.0
        for c in allCacheFiles:
            filePath = os.path.normpath(cmds.getAttr("%s.cachePath" %c))
            fileDrive, tmp = os.path.splitdrive(filePath)
            if currentProjectPath not in filePath:
                cPPcount += 1
                msg = "Cache File (%s) is not in the Project Folder" % c
                self.majorProblemNodes.append([c, "defaultRenderLayer", "openAEWindow;", msg])
                severity += 6
            if projectsFolder not in filePath:
                msg = "Cache file is NOT even in %s !!! (%s)" % c
                # take the average of the missing filenodes. If it is above([c, "defaultRenderLayer", "openAEWindow;"])
                self.majorProblemNodes.append([c, "defaultRenderLayer", "openAEWindow;", msg])
                severity += 9

        cPPratio = 0 if cPPcount == 0 else cPPcount / len(allCacheFiles)  # The Almighty Ternery Operator!!!

        return severity

    def foolerMaster(self):

        self.minorProblemNodes = []  # reset the problem Lists
        self.majorProblemNodes = []
        allRenderLayers = cmds.ls(type="renderLayer")
        #
        # # get the non referenced render layers
        self.allUsableRenderLayers = []
        for i in allRenderLayers:
            if not (cmds.referenceQuery([i], isNodeReferenced=True)) and cmds.getAttr("%s.renderable" % (i)):
                self.allUsableRenderLayers.append(i)
        warningLevel = 0
        warningLevel += self.foolCheckImagePlane(self.allUsableRenderLayers)
        warningLevel += self.foolCheckRenderCamera(self.allUsableRenderLayers)
        warningLevel += self.foolCheckRenderSettings(self.allUsableRenderLayers)
        warningLevel += self.foolCheckPaths()


    def callDeadlineScript(self):
        scriptPath = os.path.join(self.getSharedSettingsDir(), "SubmitMayaToDeadlineCustom.mel")

        if os.path.isfile(scriptPath):
            scriptPath = scriptPath.replace("\\", "//") ## for compatibility with mel syntax.
            cmd = ('source "{0}";'.format(scriptPath))
            try:
                mel.eval(cmd)
            except:
                logger.warning("Second try")
                mel.eval(cmd)
            mel.eval('SubmitJobToDeadline()')
            return None, None
        else:
            msg = "SubmitMayaToDeadlineCustom.mel is not exist under the Common Directory"
            cmds.warning(msg)
            return -1, msg

    def batchRender(self, optionBox=False):
        if not optionBox:
            cmds.BatchRender()
        else:
            cmds.BatchRenderOptions()

    def imageSequencer(self, optionBox=False):
        if not optionBox:
            cmds.RenderSequence()
        else:
            mel.eval("renderSequenceOptionsWindow")

    def _exception(self, code, msg):
        """Overriden Function"""
        cmds.confirmDialog(title=self.errorCodeDict[code], message=msg, button=['Ok'])
        if (200 >= code < 210):
            raise Exception(code, msg)

class MainUI(QtWidgets.QMainWindow):
    def __init__(self, callback=None):

        for entry in QtWidgets.QApplication.allWidgets():
            try:
                if entry.objectName() == windowName:
                    entry.close()
            except (AttributeError, TypeError):
                pass
        parent = getMayaMainWindow()
        super(MainUI, self).__init__(parent=parent)
        self.imanager = ImageManager()
        if not self.imanager.sceneInfo:
            return

        self.setObjectName(windowName)
        self.resize(656, 402)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setWindowTitle(windowName)
        self.centralwidget = QtWidgets.QWidget(self)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # Set Stylesheet
        dirname = os.path.dirname(os.path.abspath(__file__))
        stylesheetFile = os.path.join(dirname, "../../CSS", "tikManager.qss")
        with open(stylesheetFile, "r") as fh:
            self.setStyleSheet(fh.read())

        self.buildUI()
        self.refresh()
        scriptJobs = []
        if callback:
            ## create script jobs
            self.job_1 = cmds.scriptJob(ac=["defaultRenderGlobals.currentRenderer", "%s.refresh()" %callback], parent=windowName)
            self.job_2 = cmds.scriptJob(e=["NewSceneOpened", "%s.refresh()" %callback], parent=windowName)
            self.job_3 = cmds.scriptJob(e=["playbackRangeSliderChanged", "%s.refresh()" %callback], parent=windowName)
            self.job_4 = cmds.scriptJob(e=["SceneOpened", "%s.refresh()" %callback], parent=windowName)
            self.job_5 = cmds.scriptJob(e=["timeUnitChanged", "%s.refresh()" %callback], parent=windowName)
            self.job_6 = cmds.scriptJob(e=["renderLayerChange", "%s.refresh()" %callback], parent=windowName)
            self.job_7 = cmds.scriptJob(e=["workspaceChanged", "%s.refresh()" %callback], parent=windowName)
            self.scriptJobs = [self.job_1, self.job_2, self.job_3, self.job_4, self.job_5, self.job_6, self.job_7]

    def buildUI(self):

        masterLayout = QtWidgets.QVBoxLayout(self.centralwidget)



        # ----------
        # HEADER BAR
        # ----------
        margin = 5
        colorWidget = QtWidgets.QWidget(self.centralwidget)
        headerLayout = QtWidgets.QHBoxLayout(colorWidget)
        headerLayout.setSpacing(0)
        try: headerLayout.setMargin(0)
        except AttributeError: pass

        tikIcon_label = QtWidgets.QLabel(self.centralwidget)
        tikIcon_label.setProperty("header", True)
        tikIcon_label.setStyleSheet("")
        tikIcon_label.setMaximumWidth(125)
        tikIcon_label.setMargin(margin)
        tikIcon_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        tikIcon_label.setScaledContents(False)
        # testBitmap = QtGui.QPixmap(os.path.join(self.imanager.getIconsDir(), "tmImageManager.png"))
        testBitmap = QtGui.QPixmap(":/icons/CSS/rc/tmImageManager.png")
        tikIcon_label.setPixmap(testBitmap)

        headerLayout.addWidget(tikIcon_label)

        self.imagePath_lineEdit = QtWidgets.QLabel()
        self.imagePath_lineEdit.setProperty("header", True)
        self.imagePath_lineEdit.setStyleSheet("")
        self.imagePath_lineEdit.setMargin(margin)
        self.imagePath_lineEdit.setIndent(2)
        self.imagePath_lineEdit.setFont(QtGui.QFont("Times", 7, QtGui.QFont.Bold))
        self.imagePath_lineEdit.setWordWrap(True)

        headerLayout.addWidget(self.imagePath_lineEdit)

        masterLayout.addWidget(colorWidget)
        # ----------
        # ----------

        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        masterLayout.addLayout(self.gridLayout)

        self.projectPath_label = QtWidgets.QLabel(self.centralwidget)
        self.projectPath_label.setFrameShape(QtWidgets.QFrame.Box)
        self.projectPath_label.setLineWidth(1)
        self.projectPath_label.setScaledContents(False)
        self.projectPath_label.setText("Project:")
        self.gridLayout.addWidget(self.projectPath_label, 0, 0, 1, 1)

        self.projectPath_lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.projectPath_lineEdit.setReadOnly(True)
        self.gridLayout.addWidget(self.projectPath_lineEdit, 0, 1, 1, 1)


        self.foolcheck_label = QtWidgets.QLabel(self.centralwidget)
        self.foolcheck_label.setText("Warnings:")
        self.gridLayout.addWidget(self.foolcheck_label, 3, 0, 1, 1)

        self.foolcheck_listWidget = QtWidgets.QListWidget(self.centralwidget)

        self.gridLayout.addWidget(self.foolcheck_listWidget, 4, 0, 1, 3)

        renderLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        renderLayout.setSpacing(25)

        self.gridLayout.addLayout(renderLayout, 6, 0, 1, 3)

        imageSequencerLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        imageSequencerLayout.setSpacing(2)
        batchLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        batchLayout.setSpacing(2)

        deadlineLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        deadlineLayout.setSpacing(2)
        renderLayout.addLayout(imageSequencerLayout)
        renderLayout.addLayout(batchLayout)
        renderLayout.addLayout(deadlineLayout)

        self.imageSequencer_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.imageSequencer_pushButton.setText("Image Sequencer")
        self.imageSequencer_pushButton.setEnabled(self.imanager.renderFlag)
        imageSequencerLayout.addWidget(self.imageSequencer_pushButton)

        self.batch_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.batch_pushButton.setText("Batch Render")
        self.batch_pushButton.setEnabled(self.imanager.renderFlag)
        batchLayout.addWidget(self.batch_pushButton)


        self.sendDeadline_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.sendDeadline_pushButton.setText("Send To Deadline")
        self.sendDeadline_pushButton.setEnabled(self.imanager.renderFlag)
        deadlineLayout.addWidget(self.sendDeadline_pushButton)


        spacerItem = QtWidgets.QSpacerItem(20, 15, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 15, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.gridLayout.addItem(spacerItem1, 5, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 656, 21))
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.setStatusBar(self.statusbar)

        self.foolcheck_listWidget.doubleClicked.connect(self.onDoubleClick)
        self.sendDeadline_pushButton.clicked.connect(self.onDeadline)

        self.imageSequencer_pushButton.clicked.connect(lambda: self.imanager.imageSequencer(optionBox=True))
        self.batch_pushButton.clicked.connect(lambda: self.imanager.batchRender(optionBox=False))

        shortcutRefresh = Qt.QtWidgets.QShortcut(Qt.QtGui.QKeySequence("F5"), self, self.refresh)


        self.setCentralWidget(self.centralwidget)
        self.show()

    def refresh(self):

        self.imanager.initRenderer()
        self.imanager.foolerMaster()
        self.imanager.projectDir = os.path.normpath(cmds.workspace(q=1, rd=1))

        if not self.imanager.currentRenderer in self.imanager.supportedRenderers:
            self.infoPop(textTitle="Render Engine Not Supported", textHeader="%s is not supported by Image Manager" %self.imanager.currentRenderer, textInfo="Image Path will not be set by Image Manager")
            self.imagePath_lineEdit.setProperty("error", True)
        else:
            self.imagePath_lineEdit.setProperty("error", False)
        self.imagePath_lineEdit.setStyleSheet("")

        self.imagePath_lineEdit.setText(self.imanager.resolvedName)
        self.projectPath_lineEdit.setText(self.imanager.projectDir)
        self.populateWarnings()

    def populateWarnings(self):

        self.foolcheck_listWidget.clear()
        #first major warnings
        for warning in self.imanager.majorProblemNodes:
            widgetItem = QtWidgets.QListWidgetItem()
            widgetItem.setText(warning[3])
            widgetItem.setForeground(QtGui.QColor(255, 0, 0, 255))
            widgetItem.setFont(QtGui.QFont('Helvetica', 12, bold=True))
            self.foolcheck_listWidget.addItem(widgetItem)

        for warning in self.imanager.minorProblemNodes:
            widgetItem = QtWidgets.QListWidgetItem()
            widgetItem.setText(warning[3])
            widgetItem.setForeground(QtGui.QColor(255, 255, 0, 255))
            widgetItem.setFont(QtGui.QFont('Arial', 12, bold=True))
            self.foolcheck_listWidget.addItem(widgetItem)

    def onDoubleClick(self):
        row = self.foolcheck_listWidget.currentRow()
        if row == -1:
            return
        if (row+1) <= len(self.imanager.majorProblemNodes):
            nodeToGet = self.imanager.majorProblemNodes[(row)][0]
            layerToGo = self.imanager.majorProblemNodes[(row)][1]
            melToEval = self.imanager.majorProblemNodes[(row)][2]
        else:
            nodeToGet = self.imanager.minorProblemNodes[(row)-(len(self.imanager.majorProblemNodes))][0]
            layerToGo = self.imanager.minorProblemNodes[(row)-(len(self.imanager.majorProblemNodes))][1]
            melToEval = self.imanager.minorProblemNodes[(row)-(len(self.imanager.majorProblemNodes))][2]

        if not nodeToGet == None:
            # first go to the problematic layer
            cmds.editRenderLayerGlobals(currentRenderLayer=layerToGo)
            cmds.select(nodeToGet)

        mel.eval(melToEval)

    def onDeadline(self):
        code, msg = self.imanager.callDeadlineScript()
        if code == -1:
            if code == -1:
                self.infoPop(textTitle="Missing File", textInfo="Cannot Submit Scene", textHeader=msg)




    def infoPop(self, textTitle="info", textHeader="", textInfo="", type="I", parent=None):
        self.msg = QtWidgets.QMessageBox(parent=parent)
        if type == "I":
            self.msg.setIcon(QtWidgets.QMessageBox.Information)
        if type == "C":
            self.msg.setIcon(QtWidgets.QMessageBox.Critical)

        self.msg.setText(textHeader)
        self.msg.setInformativeText(textInfo)
        self.msg.setWindowTitle(textTitle)
        self.msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        self.msg.show()