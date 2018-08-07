"""As a part of SceneManager, ImageManager checks the scene for possible errors before
sending it to Deadline render manager.
On initialization, script changes the image name template according to the defined template
and checks the scene for possible errors
Double Clicking on warnings open up the related dialog.
"""
import __init__
import pymel.core as pm
import os
import logging
import maya.mel as mel
from manager import TikManager

import Qt
from Qt import QtWidgets, QtCore, QtGui
from maya import OpenMayaUI as omui
if Qt.__binding__ == "PySide":
    from shiboken import wrapInstance
    from Qt.QtCore import Signal
elif Qt.__binding__.startswith('PyQt'):
    from sip import wrapinstance as wrapInstance
    from Qt.Core import pyqtSignal as Signal
else:
    from shiboken2 import wrapInstance
    from Qt.QtCore import Signal

# from manager import loadJson, dumpJson

__author__ = "Arda Kutlu"
__copyright__ = "Copyright 2018, Scene Manager for Maya Project"
__credits__ = []
__license__ = "GPL"
# __version__ = "0.2"
__maintainer__ = "Arda Kutlu"
__email__ = "ardakutlu@gmail.com"
__status__ = "Development"

windowName = "Image Manager v%s" %__init__.__version__

logging.basicConfig()
logger = logging.getLogger('ImageManager')
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

class ImageManager(TikManager):
    def __init__(self):
        super(ImageManager, self).__init__()

        self.sceneInfo = self.getSceneInfo()
        if not self.sceneInfo:
            logger.warning("This is not a Base Scene")
            return
        if not self.sceneInfo["category"] == "Render":
            logger.warning("Base Scene must be under Render Category")
            return

        self.folderTemplate = "{4}/{0}/{1}/{3}/{2}/"
        self.nameTemplate = "{0}_{1}_{2}_{3}_"
        self.supportedRenderers = ["arnold", "vray", "mentalRay", "redShift"]
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

    def resolvePath(self, vray=False):
        projectImgDir = os.path.join(self.sceneInfo["projectPath"], "images")
        # folderCheck(projectImgDir)
        if vray:
            renderlayer="<Layer>"
        else:
            renderlayer="<RenderLayer>"

        # print "A", self.sceneInfo["subProject"]
        subProject = "" if self.sceneInfo["subProject"] == "None" else self.sceneInfo["subProject"]

        shotName = self.sceneInfo["shotName"]
        version=self.sceneInfo["version"]

        self.folderTemplate = os.path.normpath(self.folderTemplate.format(subProject,shotName,renderlayer,version,projectImgDir))
        self.nameTemplate = (self.nameTemplate.format(subProject,shotName,renderlayer,version)).lstrip("_")

        # print self.folderTemplate
        # print self.nameTemplate
        return os.path.join(self.folderTemplate, self.nameTemplate)

    def initRenderer(self):
        self.currentRenderer = pm.getAttr('defaultRenderGlobals.currentRenderer')

        if self.currentRenderer == "arnold":
            # set the image format to 'exr'
            arnoldDriver = pm.PyNode('defaultArnoldDriver')
            arnoldDriver.ai_translator.set("exr")
            # set the compression to 'zips'
            pm.setAttr("%s.exrCompression" % arnoldDriver, 2)
            # Frame/Animation ext and Frame Padding
            pm.setAttr("defaultRenderGlobals.outFormatControl", 0)
            pm.setAttr("defaultRenderGlobals.animation", 1)
            pm.setAttr("defaultRenderGlobals.putFrameBeforeExt", 1)
            pm.setAttr("defaultRenderGlobals.extensionPadding", 4)
            # set File Name Prefix
            self.resolvedName = self.resolvePath()
            pm.setAttr("defaultRenderGlobals.imageFilePrefix", self.resolvedName)
            return

        elif self.currentRenderer == "vray":
            # set the image format to 'exr'
            vraySettings = pm.PyNode("vraySettings")
            pm.setAttr("%s.imageFormatStr" % vraySettings, 'exr')
            # set the compression to 'zips'
            pm.setAttr("%s.imgOpt_exr_compression" % vraySettings, 3)
            # Frame/Animation ext and Frame Padding
            pm.setAttr("%s.animType" % vraySettings, 1)
            pm.setAttr(vraySettings.fileNamePadding, 4)
            # set File Name Prefix
            self.resolvedName = self.resolvePath(vray=True)
            pm.setAttr("%s.fileNamePrefix" %vraySettings, self.resolvedName)
            return

        elif self.currentRenderer == "mentalRay":
            # set the image format to 'exr'
            pm.setAttr("defaultRenderGlobals.imageFormat", 51)
            pm.setAttr("defaultRenderGlobals.imfPluginKey", "exr")
            pm.setAttr("defaultRenderGlobals.imageCompression", 0)
            # set the compression to 'zips'
            pm.setAttr("mentalrayGlobals.imageCompression", 5)
            # Frame/Animation ext and Frame Padding
            pm.setAttr("defaultRenderGlobals.outFormatControl", 0)
            pm.setAttr("defaultRenderGlobals.animation", 1)
            pm.setAttr("defaultRenderGlobals.putFrameBeforeExt", 1)
            pm.setAttr("defaultRenderGlobals.extensionPadding", 4)
            # set File Name Prefix
            self.resolvedName = self.resolvePath()
            pm.setAttr("defaultRenderGlobals.imageFilePrefix", self.resolvedName)
            return

        elif self.currentRenderer == "redshift":
            # set the image format to 'exr'
            pm.setAttr("redshiftOptions.imageFormat", 1)
            # set the compression to 'zips'
            pm.setAttr("redshiftOptions.exrCompression", 3)
            pm.setAttr("redshiftOptions.exrIsTiled", 0)
            # Frame/Animation ext and Frame Padding
            pm.setAttr("defaultRenderGlobals.outFormatControl", 0)
            pm.setAttr("defaultRenderGlobals.animation", 1)
            pm.setAttr("defaultRenderGlobals.putFrameBeforeExt", 1)
            pm.setAttr("defaultRenderGlobals.extensionPadding", 4)
            # set File Name Prefix
            self.resolvedName = self.resolvePath()
            pm.setAttr("defaultRenderGlobals.imageFilePrefix", self.resolvedName)
            return

        else:
            logger.warning("Render Engine is not supported. Skipping Engine specific settings")
            self.resolvedName = ("Render Engine is NOT supported, set image path manually")
            return
            pass

    def getAttrInLayer(self, node, attr, layer, returnAnyWay=False):
        nodeAttr = "%s.%s" % (node, attr)
        connection_list = pm.listConnections(nodeAttr, plugs=True)
        if layer == "defaultRenderLayer":
            return pm.getAttr(nodeAttr)  # return

        if len(connection_list) == 0:  # hicbir layerda olmasinin mumkunati yoksa
            if returnAnyWay:
                return pm.getAttr(nodeAttr)  # return
            else:
                return None

        for connection in connection_list:

            attr_component_list = connection.split(".")
            if attr_component_list[0] == layer:  # eger bu layerdaysa
                nodeAttr = ".".join(attr_component_list[0:-1])
                return pm.getAttr("%s.value" % nodeAttr)  # return
            else:
                if returnAnyWay:
                    return pm.getAttr(nodeAttr)  # return
                else:
                    return None

    def foolCheckImagePlane(self, renderLayerList):

        # self.ImagePlaneSeverity = 0
        severity = 0

        # Calculate the maximum possible severity

        allImagePlanes = pm.ls(type="imagePlane")

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
                            # return severity, maxSeverity

    def foolCheckRenderCamera(self, renderLayerList):
        # self.cameraSeverity = 0
        severity = 0
        allCameras = pm.ls(type="camera")

        for layer in renderLayerList:
            renderCameras = []  # reset renderable camera list for each render layer
            # get the renderable cameras
            for x in allCameras:

                rMode = self.getAttrInLayer(x, "renderable", layer=layer, returnAnyWay=True)
                if rMode:
                    renderCameras.append(x)
            for rcam in renderCameras:
                # check if the perspective camera is among renderable cameras
                if "perspShape" in rcam.name():
                    if len(renderCameras) > 1:
                        msg = "Multiple Renderable Cameras => (%s)" % layer
                        self.minorProblemNodes.append([rcam, layer, "unifiedRenderGlobalsWindow;", msg])
                        # self.cameraSeverity += 5
                        severity += 5
                    else:
                        msg = "Perspective Camera is renderable (%s)" % layer
                        self.minorProblemNodes.append([rcam, layer, "unifiedRenderGlobalsWindow;", msg])
                        # self.cameraSeverity += 1
                        severity += 1

            if len(renderCameras) == 0:
                msg = "No renderable cameras(%s)" % layer
                # self.cameraSeverity += 10
                severity += 10
                self.majorProblemNodes.append([None, None, "", msg])
        # Calculate the maximum possible severity
        # maxSeverity = 5 * len(renderLayerList)  # manual calculation by worst case scenario
        return severity

    def foolCheckRenderSettings(self, renderLayerList):
        severity = 0

        # get the timeslider range:
        startFrame = pm.playbackOptions(q=True, minTime=True)
        endFrame = pm.playbackOptions(q=True, maxTime=True)

        activeRenderLayer = pm.editRenderLayerGlobals(q=True, currentRenderLayer=True)
        # go through all renderlayers:
        for layer in renderLayerList:
            pm.editRenderLayerGlobals(currentRenderLayer=layer)

            # get paths
            comparePath = pm.renderSettings(firstImageName=True, lastImageName=True, fp=True)
            filePath, fileBase = os.path.split(comparePath[0])

            ## COmmon for all render engines
            # get the render range
            animStart = pm.getAttr("defaultRenderGlobals.startFrame")
            animEnd = pm.getAttr("defaultRenderGlobals.endFrame")
            if animStart != startFrame or animEnd != endFrame:
                # msg = "Timeslider range and render ranges are different in {4}. {0}-{1} >> {2}-{3}".format(startFrame,
                msg = "Timeslider range and Render ranges are different (%s)" %layer
                self.minorProblemNodes.append(
                    ["defaultRenderGlobals", layer, "unifiedRenderGlobalsWindow;", msg])  # RG is for Render Globals
                severity += 1
        return severity

    def foolCheckPaths(self):
        acceptables = ["mesh", "shape", "transform"]
        def isAssigned(fileNode):

            try:

                matInfo = pm.listConnections(fileNode, s=False, d=True, type="materialInfo")[0]
            except:

                matInfo = None

            if not matInfo == None:
                sGroup = pm.getAttr(matInfo.shadingGroup)
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
        validDrive = "M:"
        projectsFolder = os.path.abspath(os.path.join(self.currentProject, os.pardir))
        allImagePlanes = pm.ls(type="imagePlane")
        ### TODO // PATHS may NOT WORK with LINUX os
        currentProjectPath = os.path.normpath(pm.workspace.path)
        # check for the image planes:
        ipPPcount = 0.0
        for ip in allImagePlanes:
            fullPath = os.path.normpath(pm.getAttr(ip.imageName))
            filePath, fileBase = os.path.split(fullPath)
            # fileDrive, tmp = os.path.splitdrive(filePath)
            if currentProjectPath not in filePath:
                ipPPcount += 1
                msg = "ImagePlane (%s) is not in the Project Folder" % ip
                self.minorProblemNodes.append([ip, "defaultRenderLayer", "openAEWindow;", msg])
                severity += 3
            # if fileDrive != validDrive:
            #     msg = "Image Plane file is NOT in M:/ !!! (%s)" % fileBase
            #     self.majorProblemNodes.append([ip, "defaultRenderLayer", "openAEWindow;"])
            #     self.feedBackMajor.append(msg)
            #     self.pathsSeverity += 9
            if projectsFolder not in filePath:
                msg = "Image Plane file is NOT even in %s !!! (%s)" % (projectsFolder,fileBase)
                self.majorProblemNodes.append([ip, "defaultRenderLayer", "openAEWindow;", msg])
                severity += 9

        # ipPPratio = 0 if ipPPcount == 0 else ipPPcount / len(allImagePlanes)  # The Almighty Ternery Operator!!!

        # check for the file nodes:
        allFileNodes = pm.ls(type="file")
        fnPPcount = 0.0
        for fn in allFileNodes:
            fullPath = os.path.normpath(pm.getAttr(fn.fileTextureName))
            filePath, fileBase = os.path.split(fullPath)
            # fileDrive, tmp = os.path.splitdrive(filePath)
            if currentProjectPath not in filePath:

                fnPPcount += 1
                msg = "Texture File (%s => %s) is not in the Project Folder" % (fn, fileBase)
                if (isAssigned(fn)):

                    self.majorProblemNodes.append([fn, "defaultRenderLayer", "openAEWindow;", msg])
                    severity += 6
                else:

                    self.minorProblemNodes.append([fn, "defaultRenderLayer", "openAEWindow;", msg])
                    severity += 1
            # if fileDrive != validDrive:
            #     if (isAssigned(fn)) == True:
            #         msg = "Texture File (ASSIGNED) is NOT in M:/  (%s)" % fileBase
            #         self.majorProblemNodes.append([fn, "defaultRenderLayer", "openAEWindow;"])
            #         self.feedBackMajor.append(msg)
            #         self.pathsSeverity += 10
            #     else:
            #         msg = "Texture File (unassigned) is NOT in M:/  (%s)" % fileBase
            #         self.minorProblemNodes.append([fn, "defaultRenderLayer", "openAEWindow;"])
            #         self.feedBackMinor.append(msg)
            #         self.pathsSeverity += 1
            if projectsFolder not in filePath:
                if (isAssigned(fn)):
                    msg = "Texture File (ASSIGNED) is NOT even in %s !!! (%s)" % (projectsFolder,fileBase)
                    self.majorProblemNodes.append([fn, "defaultRenderLayer", "openAEWindow;", msg])
                    severity += 10
                else:
                    msg = "Texture File (unassigned) is NOT even in %s !!! (%s)" % (projectsFolder,fileBase)
                    self.minorProblemNodes.append([fn, "defaultRenderLayer", "openAEWindow;", msg])
                    severity += 1
        # fnPPratio = 0 if fnPPcount == 0 else fnPPcount / len(allFileNodes)  # The Almighty Ternery Operator!!!

        # check for the cache files:
        allCacheFiles = pm.ls(type="cacheFile")
        cPPcount = 0.0
        for c in allCacheFiles:
            filePath = os.path.normpath(pm.getAttr(c.cachePath))
            fileDrive, tmp = os.path.splitdrive(filePath)
            if currentProjectPath not in filePath:
                cPPcount += 1
                msg = "Cache File (%s) is not in the Project Folder" % c
                self.majorProblemNodes.append([c, "defaultRenderLayer", "openAEWindow;", msg])
                severity += 6
            # if fileDrive != validDrive:
            #     msg = "Cache file is NOT in M:/ !!! (%s)" % c
            #     # take the average of the missing filenodes. If it is above([c, "defaultRenderLayer", "openAEWindow;"])
            #     self.majorProblemNodes.append([c, "defaultRenderLayer", "openAEWindow;"])
            #     self.feedBackMajor.append(msg)
            #     self.pathsSeverity += 9
            if projectsFolder not in filePath:
                msg = "Cache file is NOT even in %s !!! (%s)" % c
                # take the average of the missing filenodes. If it is above([c, "defaultRenderLayer", "openAEWindow;"])
                self.majorProblemNodes.append([c, "defaultRenderLayer", "openAEWindow;", msg])
                severity += 9

        cPPratio = 0 if cPPcount == 0 else cPPcount / len(allCacheFiles)  # The Almighty Ternery Operator!!!

        # if ((ipPPratio + fnPPratio + cPPratio) / 3) >= 0.3:
        #     msg = "Project Folder is probably not set"
        #     self.minorProblemNodes.append([None, None, "SetProject;"])
        #     self.feedBackMinor.append(msg)
        #     self.pathsSeverity += 0

        return severity

    def foolerMaster(self):

        self.minorProblemNodes = []  # reset the problem Lists
        self.majorProblemNodes = []
        allRenderLayers = pm.ls(type="renderLayer")
        #
        # # get the non referenced render layers
        self.allUsableRenderLayers = []
        for i in allRenderLayers:
            if not (pm.referenceQuery([i], isNodeReferenced=True)) and pm.getAttr(i.renderable):
                self.allUsableRenderLayers.append(i)

        # self.feedBack.removeAll()
        # self.feedBackMajor.removeAll()
        # self.feedBackMinor.removeAll()

        # self.initCommons()
        # self.feedBackMajor.append("!!! >> POSSIBLE ERRORS << !!!")
        # self.majorProblemNodes.append([None, None, ""])
        # self.feedBackMinor.append("!!! >> WARNINGS << !!!")
        # self.minorProblemNodes.append([None, None, ""])

        warningLevel = 0

        # imagePlaneScore = self.foolCheckImagePlane(self.allUsableRenderLayers)
        # warningLevel += imagePlaneScore
        # renderCameraScore = self.foolCheckRenderCamera(self.allUsableRenderLayers)

        warningLevel += self.foolCheckImagePlane(self.allUsableRenderLayers)
        warningLevel += self.foolCheckRenderCamera(self.allUsableRenderLayers)
        warningLevel += self.foolCheckRenderSettings(self.allUsableRenderLayers)
        warningLevel += self.foolCheckPaths()

        # print "MAJORS:\n", self.majorProblemNodes
        # print "minors:\n", self.minorProblemNodes
        # print "Warning Level:", warningLevel

    def callDeadlineScript(self):
        scriptLocation = os.path.dirname(os.path.abspath(__file__))
        scriptPath = os.path.join(scriptLocation, "SubmitMayaToDeadlineCustom.mel")
        print "hede", scriptPath
        if os.path.isfile(scriptPath):
            scriptPath = scriptPath.replace("\\", "//") ## for compatibility with mel syntax.
            # mel.eval('source "%s//SubmitMayaToDeadlineCustom.mel";' % compatibility)
            # print os.path.normpath(scriptPath)
            cmd = ('source "{0}";'.format(scriptPath))
            mel.eval(cmd)
            mel.eval('SubmitJobToDeadline()')
            return None, None
        else:
            msg = "SubmitMayaToDeadlineCustom.mel is not exist under the tik_manager directory"
            pm.warning(msg)
            return -1, msg

class MainUI(QtWidgets.QMainWindow):
    def __init__(self, scriptJob=None):

        for entry in QtWidgets.QApplication.allWidgets():
            try:
                if entry.objectName() == windowName:
                    entry.close()
            except AttributeError:
                pass
        parent = getMayaMainWindow()
        super(MainUI, self).__init__(parent=parent)
        self.imanager = ImageManager()
        if not self.imanager.sceneInfo:
            self.infoPop(textTitle="Warning - Not a Base Scene", textHeader="Scene is not a Base Scene. Save it using SceneManager")
            return

        if not self.imanager.sceneInfo["category"] == "Render":
            self.infoPop(textTitle="Warning - Not under Render Category", textHeader="Scene is not under Render Category.")
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
        self.centralwidget.setObjectName("centralwidget")

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.buildUI()
        self.refresh()
        scriptJobs = []
        if scriptJob:
            ## create a script jobs
            self.job_1 = pm.scriptJob(ac=["defaultRenderGlobals.currentRenderer", "%s.refresh()" %scriptJob], parent=windowName)
            self.job_2 = pm.scriptJob(e=["NewSceneOpened", "%s.refresh()" %scriptJob], parent=windowName)
            self.job_3 = pm.scriptJob(e=["playbackRangeSliderChanged", "%s.refresh()" %scriptJob], parent=windowName)
            self.job_4 = pm.scriptJob(e=["SceneOpened", "%s.refresh()" %scriptJob], parent=windowName)
            self.job_5 = pm.scriptJob(e=["timeUnitChanged", "%s.refresh()" %scriptJob], parent=windowName)
            self.job_6 = pm.scriptJob(e=["renderLayerChange", "%s.refresh()" %scriptJob], parent=windowName)
            self.job_7 = pm.scriptJob(e=["workspaceChanged", "%s.refresh()" %scriptJob], parent=windowName)
            self.scriptJobs = [self.job_1, self.job_2, self.job_3, self.job_4, self.job_5, self.job_6, self.job_7]

            # return
    def buildUI(self):

        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        self.projectPath_label = QtWidgets.QLabel(self.centralwidget)
        self.projectPath_label.setFrameShape(QtWidgets.QFrame.Box)
        self.projectPath_label.setLineWidth(1)
        self.projectPath_label.setScaledContents(False)
        self.projectPath_label.setObjectName("projectPath_label")
        self.projectPath_label.setText("Project:")
        self.gridLayout.addWidget(self.projectPath_label, 0, 0, 1, 1)

        self.projectPath_lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.projectPath_lineEdit.setObjectName("projectPath_lineEdit")
        # self.projectPath_lineEdit.setText(self.imanager.currentProject)
        self.projectPath_lineEdit.setReadOnly(True)
        self.gridLayout.addWidget(self.projectPath_lineEdit, 0, 1, 1, 1)

        self.setProject_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.setProject_pushButton.setObjectName("setProject_pushButton")
        self.setProject_pushButton.setText("SET")
        self.gridLayout.addWidget(self.setProject_pushButton, 0, 2, 1, 1)

        self.imagePath_label = QtWidgets.QLabel(self.centralwidget)
        self.imagePath_label.setFrameShape(QtWidgets.QFrame.Box)
        self.imagePath_label.setObjectName("imagePath_label")
        self.imagePath_label.setText("Image Path:")
        self.gridLayout.addWidget(self.imagePath_label, 1, 0, 1, 1)

        self.imagePath_lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.imagePath_lineEdit.sizePolicy().hasHeightForWidth())
        self.imagePath_lineEdit.setReadOnly(True)
        self.imagePath_lineEdit.setSizePolicy(sizePolicy)
        self.imagePath_lineEdit.setObjectName("imagePath_lineEdit")
        self.gridLayout.addWidget(self.imagePath_lineEdit, 1, 1, 1, 2)

        self.foolcheck_label = QtWidgets.QLabel(self.centralwidget)
        self.foolcheck_label.setObjectName("foolcheck_label")
        self.foolcheck_label.setText("Warnings:")
        self.gridLayout.addWidget(self.foolcheck_label, 3, 0, 1, 1)

        self.foolcheck_listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.foolcheck_listWidget.setObjectName("foolcheck_listView")
        self.foolcheck_listWidget.setStyleSheet("border-style: solid; border-width: 2px; border-color: grey;")

        self.gridLayout.addWidget(self.foolcheck_listWidget, 4, 0, 1, 3)

        self.sendDeadline_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.sendDeadline_pushButton.setObjectName("sendDeadline_pushButton")
        self.sendDeadline_pushButton.setText("Send To Deadline")
        self.gridLayout.addWidget(self.sendDeadline_pushButton, 6, 0, 1, 3)

        spacerItem = QtWidgets.QSpacerItem(20, 15, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 15, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.gridLayout.addItem(spacerItem1, 5, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 656, 21))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.setProject_pushButton.clicked.connect(self.onSetProject)
        self.foolcheck_listWidget.doubleClicked.connect(self.onDoubleClick)
        self.sendDeadline_pushButton.clicked.connect(self.onDeadline)

        shortcutRefresh = Qt.QtWidgets.QShortcut(Qt.QtGui.QKeySequence("F5"), self, self.refresh)


        self.setCentralWidget(self.centralwidget)
        # self.imagePath_lineEdit.setText(self.imanager.resolvedName)
        # self.populateWarnings()
        self.show()


    def onSetProject(self):
        self.imanager.setProject()
        self.projectPath_lineEdit.setText(self.imanager.currentProject)

    def refresh(self):

        self.imanager.initRenderer()
        self.imanager.foolerMaster()
        self.imanager.currentProject = pm.workspace(q=1, rd=1)

        if not self.imanager.currentRenderer in self.imanager.supportedRenderers:
            self.infoPop(textTitle="Render Engine Not Supported", textHeader="%s is not supported by Image Manager" %self.imanager.currentRenderer, textInfo="Image Path will not be set by Image Manager")
            self.imagePath_lineEdit.setStyleSheet("color: red")
        else:
            self.imagePath_lineEdit.setStyleSheet("color: rgb(200,200,200)")

        self.imagePath_lineEdit.setText(self.imanager.resolvedName)
        self.projectPath_lineEdit.setText(self.imanager.currentProject)
        self.populateWarnings()

    # def closeEvent(self, event):
    #     # do stuff
    #     try:
    #         for i in self.scriptJobs:
    #             pm.scriptJob(kill=i)
    #     except AttributeError:
    #         pass


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
            pm.editRenderLayerGlobals(currentRenderLayer=layerToGo)
            pm.select(nodeToGet)

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