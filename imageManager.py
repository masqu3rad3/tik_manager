import pymel.core as pm
import os
import logging
from manager import TikManager
# reload(TikManager)
from manager import pathOps, getPathsFromScene, folderCheck
from manager import loadJson, dumpJson
logging.basicConfig()
logger = logging.getLogger('ImageManager')
logger.setLevel(logging.DEBUG)

def parseTemplate(template):
    pass


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

        self.minorProblemNodes = []
        self.majorProblemNodes = []
        self.feedBackMinor = []
        self.feedBackMajor = []
        self.initRenderer()



    # def resolveImageName(self):
    #
    #     #get the images folder
    #     sceneVersion = pathOps(pm.sceneName(), "filename")[-4:]
    #     projectImgDir = os.path.join(self.sceneInfo["projectPath"], "images")
    #
    #     if self.sceneInfo["subProject"] != "None":
    #         shotImgDir = os.path.join(projectImgDir, self.sceneInfo["subProject"], self.sceneInfo["shotName"])
    #     else:
    #         shotImgDir = os.path.join(projectImgDir, self.sceneInfo["shotName"])
    #
    #     folderCheck(shotImgDir ) # folder check creates the directory if it does not (or they dont) exist
    #
    #     curRenderer = pm.getAttr('defaultRenderGlobals.currentRenderer')
    #
    #
    #     if curRenderer == "arnold":
    #         # set the image format to 'exr'
    #         arnoldDriver = pm.PyNode('defaultArnoldDriver')
    #         arnoldDriver.ai_translator.set("exr")
    #         # set the compression to 'zips'
    #         pm.setAttr("%s.exrCompression" %arnoldDriver, 2)
    #         # Frame/Animation ext and Frame Padding
    #         pm.setAttr("defaultRenderGlobals.outFormatControl", 0)
    #         pm.setAttr("defaultRenderGlobals.animation", 1)
    #         pm.setAttr("defaultRenderGlobals.putFrameBeforeExt", 1)
    #         pm.setAttr("defaultRenderGlobals.extensionPadding", 4)
    #
    #     elif curRenderer == "vray":
    #         # set the image format to 'exr'
    #         vraySettings = pm.PyNode("vraySettings")
    #         pm.setAttr("%s.imageFormatStr" % vraySettings, 'exr')
    #         # set the compression to 'zips'
    #         pm.setAttr("%s.imgOpt_exr_compression" % vraySettings, 3)
    #         # Frame/Animation ext and Frame Padding
    #         pm.setAttr("%s.animType" % vraySettings, 1)
    #         pm.setAttr(vraySettings.fileNamePadding, 4)
    #
    #
    #     elif curRenderer == "mentalRay":
    #         pass
    #     elif curRenderer == "redshift":
    #         pass
    #     else:
    #         pass
    #
    #     resolvedName = "{0}/{1}/<RenderLayer>/{2}_{1}".format(shotImgDir, sceneVersion, self.sceneInfo["shotName"])
    #
    #     pm.setAttr("defaultRenderGlobals.imageFilePrefix", resolvedName)
    #     return shotImgDir

    def getImageDir(self):

        # get the images folder
        projectImgDir = os.path.join(self.sceneInfo["projectPath"], "images")

        if self.sceneInfo["subProject"] != "None":
            shotImgDir = os.path.join(projectImgDir, self.sceneInfo["subProject"], self.sceneInfo["shotName"])
        else:
            shotImgDir = os.path.join(projectImgDir, self.sceneInfo["shotName"])

        folderCheck(shotImgDir)  # folder check creates the directory if it does not (or they dont) exist
        return shotImgDir

    def initRenderer(self):
        curRenderer = pm.getAttr('defaultRenderGlobals.currentRenderer')
        imgDir = self.getImageDir()
        # sceneVersion = pathOps(pm.sceneName(), "filename")[-4:]
        resolvedName = "{0}/{1}/<RenderLayer>/{2}_{1}".format(imgDir, self.sceneInfo["version"], self.sceneInfo["shotName"])
        pm.setAttr("defaultRenderGlobals.imageFilePrefix", resolvedName)

        if curRenderer == "arnold":
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
            resolvedName = "{0}/{1}/<RenderLayer>/{2}_{1}".format(imgDir, self.sceneInfo["version"], self.sceneInfo["shotName"])
            pm.setAttr("defaultRenderGlobals.imageFilePrefix", resolvedName)

        elif curRenderer == "vray":
            # set the image format to 'exr'
            vraySettings = pm.PyNode("vraySettings")
            pm.setAttr("%s.imageFormatStr" % vraySettings, 'exr')
            # set the compression to 'zips'
            pm.setAttr("%s.imgOpt_exr_compression" % vraySettings, 3)
            # Frame/Animation ext and Frame Padding
            pm.setAttr("%s.animType" % vraySettings, 1)
            pm.setAttr(vraySettings.fileNamePadding, 4)
            # set File Name Prefix
            resolvedName = "{0}/{1}/<Layer>/{2}_{1}".format(imgDir, self.sceneInfo["version"], self.sceneInfo["shotName"])
            pm.setAttr("%s.fileNamePrefix" %vraySettings, resolvedName)

        elif curRenderer == "mentalRay":
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
            resolvedName = "{0}/{1}/<RenderLayer>/{2}_{1}".format(imgDir, self.sceneInfo["version"], self.sceneInfo["shotName"])
            pm.setAttr("defaultRenderGlobals.imageFilePrefix", resolvedName)

        elif curRenderer == "redshift":
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
            resolvedName = "{0}/{1}/<RenderLayer>/{2}_{1}".format(imgDir, self.sceneInfo["version"], self.sceneInfo["shotName"])
            pm.setAttr("defaultRenderGlobals.imageFilePrefix", resolvedName)

        else:
            logger.warning("Render Engine is not supported. Skipping Engine specific settings")
            renderLayer = "<RenderLayer>"
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
                if returnAnyWay == True:
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
                if dMode != None:
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
                        msg = "Multiple renderable cameras in the scene (%s)" % layer
                        self.minorProblemNodes.append([rcam, layer, "unifiedRenderGlobalsWindow;", msg])
                        # self.cameraSeverity += 5
                        severity += 5
                    else:
                        msg = "Perspective Camera is renderable (%s)" % layer
                        self.minorProblemNodes.append([rcam, layer, "unifiedRenderGlobalsWindow;", msg])
                        # self.cameraSeverity += 1
                        severity += 1

            if len(renderCameras) == 0:
                msg = "No renderable cameras in the scene (%s)" % layer
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
                msg = "Timeslider range and render ranges are different in {4}. {0}-{1} >> {2}-{3}".format(startFrame,
                                                                                                    endFrame, animStart,
                                                                                                    animEnd, layer)
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

            if matInfo != None:
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
                if (isAssigned(fn)) == True:

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
                if (isAssigned(fn)) == True:
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

        print "MAJORS:\n", self.majorProblemNodes
        print "minors:\n", self.minorProblemNodes
        print "Warning Level:", warningLevel

