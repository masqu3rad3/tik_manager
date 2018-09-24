import os
import SmRoot
reload(SmRoot)
from SmRoot import RootManager

import shutil
import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import datetime
import socket
import logging

import Qt
from Qt import QtWidgets, QtCore, QtGui
from maya import OpenMayaUI as omui

if Qt.__binding__ == "PySide":
    from shiboken import wrapInstance
elif Qt.__binding__.startswith('PyQt'):
    from sip import wrapinstance as wrapInstance
else:
    from shiboken2 import wrapInstance

__author__ = "Arda Kutlu"
__copyright__ = "Copyright 2018, Scene Manager for Maya Project"
__credits__ = []
__version__ = "V2.0.0"
__license__ = "GPL"
__maintainer__ = "Arda Kutlu"
__email__ = "ardakutlu@gmail.com"
__status__ = "Development"

SM_Version = "Scene Manager v%s" %(__version__)

logging.basicConfig()
logger = logging.getLogger('smMaya')
logger.setLevel(logging.DEBUG)

def getMayaMainWindow():
    """
    Gets the memory adress of the main window to connect Qt dialog to it.
    Returns:
        (long) Memory Adress
    """
    win = omui.MQtUtil_mainWindow()
    ptr = wrapInstance(long(win), QtWidgets.QMainWindow)
    return ptr

class MayaManager(RootManager):
    def __init__(self):
        super(MayaManager, self).__init__()

        self.init_paths()
        self.backwardcompatibility()  # DO NOT RUN UNTIL RELEASE
        self.init_database()


    def getSoftwarePaths(self):
        """Overriden function"""
        # To tell the base class maya specific path names
        return {"databaseDir": "mayaDB",
                "scenesDir": "scenes",
                "pbSettingsFile": "pbSettings"}

    def getProjectDir(self):
        """Overriden function"""
        # This function gets the current maya project and informs the base class
        # In addition it updates the projects file for (planned) interactivities with concurrent softwares
        p_path = cmds.workspace(q=1, rd=1)
        norm_p_path = os.path.normpath(p_path)
        projectsDict = self._loadProjects()
        if not projectsDict:
            projectsDict = {"MayaProject": norm_p_path}
        else:
            projectsDict["MayaProject"] = norm_p_path
        self._saveProjects(projectsDict)
        return norm_p_path

    def getSceneFile(self):
        """Overriden function"""
        # Gets the current scene path ("" if untitled)
        s_path = cmds.file(q=True, sn=True)
        norm_s_path = os.path.normpath(s_path)
        return norm_s_path

    def setProject(self, path):
        # totally software specific or N/A
        melCompPath = path.replace("\\", "/") # mel is picky
        command = 'setProject "%s";' %melCompPath
        mel.eval(command)
        # self.projectDir = cmds.workspace(q=1, rd=1)
        self.projectDir = self.getProjectDir()

    # def getSceneInfo(self):
    #     """
    #     Collects the necessary scene info by resolving the scene name and current project
    #     Returns: Dictionary{jsonFile, projectPath, subProject, category, shotName} or None
    #     """
    #     self._pathsDict["sceneFile"] = self.getSceneFile()
    #     if not self._pathsDict["sceneFile"]:
    #         return None
    #
    #     # get name of the upper directory to find out base name
    #     sceneDir = os.path.abspath(os.path.join(self._pathsDict["sceneFile"], os.pardir))
    #     baseSceneName = os.path.basename(sceneDir)
    #
    #     upperSceneDir = os.path.abspath(os.path.join(sceneDir, os.pardir))
    #     upperSceneDirName = os.path.basename(upperSceneDir)
    #
    #     if upperSceneDirName in self._subProjectsList:
    #         subProjectDir = upperSceneDir
    #         subProject = upperSceneDirName
    #         categoryDir = os.path.abspath(os.path.join(subProjectDir, os.pardir))
    #         category = os.path.basename(categoryDir)
    #
    #         dbCategoryPath = os.path.normpath(os.path.join(self._pathsDict["databaseDir"], category))
    #         dbPath = os.path.normpath(os.path.join(dbCategoryPath, subProject))
    #
    #         pbCategoryPath = os.path.normpath(os.path.join(self._pathsDict["previewsDir"], category))
    #         pbSubPath = os.path.normpath(os.path.join(pbCategoryPath, subProject))
    #         pbPath = os.path.normpath(os.path.join(pbSubPath, baseSceneName))
    #
    #     else:
    #         subProject = self._subProjectsList[0]
    #         categoryDir = upperSceneDir
    #         category = upperSceneDirName
    #         dbPath = os.path.normpath(os.path.join(self._pathsDict["databaseDir"], category))
    #         pbCategoryPath = os.path.normpath(os.path.join(self._pathsDict["previewsDir"], category))
    #         pbPath = os.path.normpath(os.path.join(pbCategoryPath, baseSceneName))
    #
    #     jsonFile = os.path.join(dbPath, "{}.json".format(baseSceneName))
    #     if os.path.isfile(jsonFile):
    #         version = (self._niceName(self._pathsDict["sceneFile"])[-4:])
    #         return {"jsonFile":jsonFile,
    #                 "projectPath":self._pathsDict["projectDir"],
    #                 "subProject":subProject,
    #                 "category":category,
    #                 "shotName":baseSceneName,
    #                 "version":version,
    #                 "previewPath":pbPath
    #                 }
    #     else:
    #         return None

    def saveCallback(self):
        """Callback function to update reference files when files saved regularly"""
        ## TODO // TEST IT
        self._pathsDict["sceneFile"] = self.getSceneFile()
        openSceneInfo = self.getOpenSceneInfo()
        if openSceneInfo["jsonFile"]:
            jsonInfo = self._loadJson(openSceneInfo["jsonFile"])
            if jsonInfo["ReferenceFile"]:
                absRefFile = os.path.join(self._pathsDict["projectDir"], jsonInfo["ReferenceFile"])
                absBaseSceneVersion = os.path.join(self._pathsDict["projectDir"], jsonInfo["Versions"][int(jsonInfo["ReferencedVersion"]) - 1][0])
                # if the refererenced scene file is the saved file (saved or saved as)
                if self._pathsDict["sceneFile"] == absBaseSceneVersion:
                    # copy over the forReference file
                    try:
                        shutil.copyfile(self._pathsDict["sceneFile"], absRefFile)
                        print "Scene Manager Update:\nReference File Updated"
                    except:
                        pass


    def saveBaseScene(self, categoryName, baseName, subProjectIndex=0, makeReference=True, versionNotes="", sceneFormat="mb", *args, **kwargs):

        # TODO // TEST IT
        """
        Saves the scene with formatted name and creates a json file for the scene
        Args:
            category: (String) Category if the scene. Valid categories are 'Model', 'Animation', 'Rig', 'Shading', 'Other'
            userName: (String) Predefined user who initiates the process
            baseName: (String) Base name of the scene. Eg. 'Shot01', 'CharacterA', 'BookRig' etc...
            subProject: (Integer) The scene will be saved under the sub-project according to the given integer value. The 'self.subProjectList' will be
                searched with that integer.
            makeReference: (Boolean) If set True, a copy of the scene will be saved as forReference
            versionNotes: (String) This string will be stored in the json file as version notes.
            *args:
            **kwargs:

        Returns: None

        """
        # fullName = self.userList.keys()[self.userList.values().index(userName)]
        now = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M")
        completeNote = "[%s] on %s\n%s\n" % (self.currentUser, now, versionNotes)

        # Check if the base name is unique
        scenesToCheck = self.scanBaseScenes(categoryAs = categoryName, subProjectAs = subProjectIndex)
        for key in scenesToCheck.keys():
            if baseName.lower() == key.lower():
                msg = ("Base Scene Name is not unique!")
                cmds.warning(msg)
                return -1, msg

        projectPath = self.projectDir
        databaseDir = self._pathsDict["databaseDir"]
        scenesPath = self._pathsDict["scenesDir"]
        categoryPath = os.path.normpath(os.path.join(scenesPath, categoryName))
        self._folderCheck(categoryPath)

        ## if its going to be saved as a subproject
        if not subProjectIndex == 0:
            subProjectPath = os.path.normpath(os.path.join(categoryPath, self._subProjectsList[subProjectIndex]))
            self._folderCheck(subProjectPath)
            shotPath = os.path.normpath(os.path.join(subProjectPath, baseName))
            self._folderCheck(shotPath)

            jsonCategoryPath = os.path.normpath(os.path.join(databaseDir, categoryName))
            self._folderCheck(jsonCategoryPath)
            jsonCategorySubPath = os.path.normpath(os.path.join(jsonCategoryPath, self._subProjectsList[subProjectIndex]))
            self._folderCheck(jsonCategorySubPath)
            jsonFile = os.path.join(jsonCategorySubPath, "{}.json".format(baseName))
        else:
            shotPath = os.path.normpath(os.path.join(categoryPath, baseName))
            self._folderCheck(shotPath)

            jsonCategoryPath = os.path.normpath(os.path.join(databaseDir, categoryName))
            self._folderCheck(jsonCategoryPath)
            jsonFile = os.path.join(jsonCategoryPath, "{}.json".format(baseName))

        version = 1
        sceneName = "{0}_{1}_{2}_v{3}".format(baseName, categoryName, self._usersDict[self.currentUser], str(version).zfill(3))
        sceneFile = os.path.join(shotPath, "{0}.{1}".format(sceneName, sceneFormat))
        ## relativity update
        relSceneFile = os.path.relpath(sceneFile, start=projectPath)
        # killTurtle()
        # TODO // cmds may be used instead
        pm.saveAs(sceneFile)

        thumbPath = self.createThumbnail(databaseDir=jsonFile, version=version)

        jsonInfo = {}

        if makeReference:
            # TODO // Find an elegant solution and add MA compatibility. Can be merged with makeReference function in derived class
            referenceName = "{0}_{1}_forReference".format(baseName, categoryName)
            referenceFile = os.path.join(shotPath, "{0}.{1}".format(referenceName, sceneFormat))
            ## relativity update
            relReferenceFile = os.path.relpath(referenceFile, start=projectPath)
            shutil.copyfile(sceneFile, referenceFile)
            jsonInfo["ReferenceFile"] = relReferenceFile
            jsonInfo["ReferencedVersion"] = version
        else:
            jsonInfo["ReferenceFile"] = None
            jsonInfo["ReferencedVersion"] = None

        jsonInfo["ID"] = "SceneManagerV02_sceneFile"
        jsonInfo["MayaVersion"] = cmds.about(q=True, api=True)
        jsonInfo["Name"] = baseName
        jsonInfo["Path"] = os.path.relpath(shotPath, start=projectPath)
        jsonInfo["Category"] = categoryName
        jsonInfo["Creator"] = self.currentUser
        jsonInfo["CreatorHost"] = (socket.gethostname())
        jsonInfo["Versions"] = [ # PATH => Notes => User Initials => Machine ID => Playblast => Thumbnail
            [relSceneFile, completeNote,  self._usersDict[self.currentUser], socket.gethostname(), {}, thumbPath]]
        jsonInfo["SubProject"] = self._subProjectsList[subProjectIndex]
        self._dumpJson(jsonInfo, jsonFile)
        return relSceneFile

    def saveVersion(self, makeReference=True, versionNotes="", sceneFormat="mb", *args, **kwargs):
        # TODO // TEST IT
        """
        Saves a version for the predefined scene. The scene json file must be present at the /data/[Category] folder.
        Args:
            userName: (String) Predefined user who initiates the process
            makeReference: (Boolean) If set True, make a copy of the forReference file. There can be only one 'forReference' file for each scene
            versionNotes: (String) This string will be hold in the json file as well. Notes about the changes in the version.
            *args:
            **kwargs:

        Returns: None

        """

        now = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M")
        completeNote = "[%s] on %s\n%s\n" % (self.currentUser, now, versionNotes)

        sceneName = self.getSceneFile()
        if not sceneName:
            msg = "This is not a base scene (Untitled)"
            cmds.warning(msg)
            return -1, msg

        sceneInfo = self.getOpenSceneInfo()

        if sceneInfo: ## getCurrentJson returns None if the resolved json path is missing
            jsonFile = sceneInfo["jsonFile"]
            jsonInfo = self._loadJson(jsonFile)

            currentVersion = len(jsonInfo["Versions"]) + 1
            sceneName = "{0}_{1}_{2}_v{3}".format(jsonInfo["Name"], jsonInfo["Category"], self._usersDict[self.currentUser],
                                                  str(currentVersion).zfill(3))
            relSceneFile = os.path.join(jsonInfo["Path"], "{0}.{1}".format(sceneName, sceneFormat))

            sceneFile = os.path.join(sceneInfo["projectPath"], relSceneFile)

            # killTurtle()
            # TODO // cmds?
            pm.saveAs(sceneFile)
            thumbPath = self.createThumbnail(jsonPath=jsonFile, version=currentVersion)

            jsonInfo["Versions"].append(
                # PATH => Notes => User Initials => Machine ID => Playblast => Thumbnail
                [relSceneFile, completeNote, self._usersDict[self.currentUser], (socket.gethostname()), {}, thumbPath])

            if makeReference:
                referenceName = "{0}_{1}_forReference".format(jsonInfo["Name"], jsonInfo["Category"])
                relReferenceFile = os.path.join(jsonInfo["Path"], "{0}.{1}".format(referenceName, sceneFormat))
                referenceFile = os.path.join(sceneInfo["projectPath"], relReferenceFile)

                shutil.copyfile(sceneFile, referenceFile)
                jsonInfo["ReferenceFile"] = relReferenceFile
                jsonInfo["ReferencedVersion"] = currentVersion
            self._dumpJson(jsonInfo, jsonFile)
        else:
            msg = "This is not a base scene (Json file cannot be found)"
            cmds.warning(msg)
            return -1, msg
        return relSceneFile


    def createPreview(self, *args, **kwargs):
        # TODO // TEST IT
        pbSettings = self._loadPBSettings()
        validFormats = cmds.playblast(format=True, q=True)
        validCodecs = cmds.playblast(c=True, q=True)

        if not pbSettings["Format"] in validFormats:
            msg = ("Format specified in project settings is not supported. Install {0}".format(pbSettings["Format"]))
            cmds.warning(msg)
            return -1, msg

        if not pbSettings["Codec"] in validCodecs:
            msg = ("Codec specified in project settings is not supported. Install {0}".format(pbSettings["Codec"]))
            cmds.warning(msg)
            return -1, msg

        extension = "mov" if pbSettings["Format"] == "qt" else "avi"

        # Quicktime format is missing the final frame all the time. Add an extra frame to compansate
        if pbSettings["Format"] == 'qt':
            maxTime = cmds.playbackOptions(q=True, maxTime=True)
            endTime = cmds.playbackOptions(q=True, animationEndTime=True)
            cmds.playbackOptions(maxTime=maxTime + 1)
            cmds.playbackOptions(animationEndTime=endTime + 1)

        openSceneInfo = self.getOpenSceneInfo()
        # sceneName = self.getSceneFile()
        if not openSceneInfo:
            msg = "This is not a base scene. Scene must be saved as a base scene before playblasting."
            pm.warning(msg)
            return -1, msg

        selection = cmds.ls(sl=True)
        cmds.select(d=pbSettings["ClearSelection"])
        jsonInfo = self._loadJson(openSceneInfo["jsonFile"])

        currentCam = cmds.modelPanel(cmds.getPanel(wf=True), q=True, cam=True)

        validName = "_"
        if not self._nameCheck(currentCam) == -1:
            validName = self._nameCheck(currentCam)
        else:
            msg = "A scene view must be highlighted"
            cmds.warning(msg)
            return -1, msg

        versionName = self.getSceneFile()
        relVersionName = os.path.relpath(versionName, start=openSceneInfo["projectPath"])
        playBlastFile = os.path.join(openSceneInfo["previewPath"], "{0}_{1}_PB.{2}".format(self._niceName(versionName), validName, extension))
        relPlayBlastFile = os.path.relpath(playBlastFile, start=openSceneInfo["projectPath"])

        if os.path.isfile(playBlastFile):
            try:
                os.remove(playBlastFile)
            except WindowsError:
                msg = "The file is open somewhere else"
                cmds.warning(msg)
                return -1, msg

        ## CREATE A CUSTOM PANEL WITH DESIRED SETTINGS

        tempWindow = cmds.window(title="SM_Playblast",
                               widthHeight=(pbSettings["Resolution"][0] * 1.1, pbSettings["Resolution"][1] * 1.1),
                               tlc=(0, 0))
        # panel = pm.getPanel(wf=True)

        cmds.paneLayout()

        pbPanel = cmds.modelPanel(camera=currentCam)
        cmds.showWindow(tempWindow)
        cmds.setFocus(pbPanel)

        cmds.modelEditor(pbPanel, e=1,
                       allObjects=not pbSettings["PolygonOnly"],
                       da="smoothShaded",
                       displayTextures=pbSettings["DisplayTextures"],
                       wireframeOnShaded=pbSettings["WireOnShaded"],
                       grid=pbSettings["ShowGrid"],
                       useDefaultMaterial=pbSettings["UseDefaultMaterial"],
                       polymeshes=True,
                       imagePlane=True,
                       hud=True
                       )

        cmds.camera(currentCam, e=True, overscan=True, displayFilmGate=False, displayResolution=False)

        ## get previous HUD States and turn them all off
        hudPreStates = {}
        HUDS = cmds.headsUpDisplay(lh=True)
        for hud in HUDS:
            hudPreStates[hud] = cmds.headsUpDisplay(hud, q=True, vis=True)
            cmds.headsUpDisplay(hud, e=True, vis=False)

        ## clear the custom HUDS
        customHuds = ['SMFrame', 'SMScene', 'SMCategory', 'SMFPS', 'SMCameraName', 'SMFrange']
        for hud in customHuds:
            if cmds.headsUpDisplay(hud, ex=True):
                cmds.headsUpDisplay(hud, rem=True)

        if pbSettings["ShowFrameNumber"]:
            freeBl = cmds.headsUpDisplay(nfb=5)  ## this is the next free block on section 5
            cmds.headsUpDisplay('SMFrame', s=5, b=freeBl, label="Frame", preset="currentFrame", dfs="large",
                              lfs="large")
        if pbSettings["ShowSceneName"]:
            freeBl = cmds.headsUpDisplay(nfb=5)  ## this is the next free block on section 5
            cmds.headsUpDisplay('SMScene', s=5, b=freeBl, label="Scene: %s" % (self._niceName(versionName)),
                              lfs="large")
        if pbSettings["ShowCategory"]:
            freeBl = cmds.headsUpDisplay(nfb=5)  ## this is the next free block on section 5
            cmds.headsUpDisplay('SMCategory', s=5, b=freeBl, label="Category: %s" % (jsonInfo["Category"]),
                              lfs="large")
        if pbSettings["ShowFPS"]:
            freeBl = cmds.headsUpDisplay(nfb=5)  ## this is the next free block on section 5
            cmds.headsUpDisplay('SMFPS', s=5, b=freeBl, label="Time Unit: %s" % (cmds.currentUnit(q=True, time=True)),
                              lfs="large")

        # v1.1 SPECIFIC
        try:
            if pbSettings["ShowFrameRange"]:
                freeBl = cmds.headsUpDisplay(nfb=5)  ## this is the next free block on section 5
                cmds.headsUpDisplay('SMFrange', s=5, b=freeBl,
                                  label="Frame Range: {} - {}".format(int(cmds.playbackOptions(q=True, minTime=True)),
                                                                      int(cmds.playbackOptions(q=True,
                                                                                             maxTime=True))),
                                  lfs="large")
        except KeyError:
            pass

        freeBl = cmds.headsUpDisplay(nfb=2)
        cmds.headsUpDisplay('SMCameraName', s=2, b=freeBl, ba='center', dw=50, pre='cameraNames')

        ## Get the active sound

        aPlayBackSliderPython = mel.eval('$tmpVar=$gPlayBackSlider')
        activeSound = cmds.timeControl(aPlayBackSliderPython, q=True, sound=True)

        ## Check here: http://download.autodesk.com/us/maya/2011help/pymel/generated/functions/pymel.core.windows/pymel.core.windows.headsUpDisplay.html
        # print "playBlastFile", playBlastFile
        normPB = os.path.normpath(playBlastFile)
        # print "normPath", normPB
        cmds.playblast(format=pbSettings["Format"],
                     filename=playBlastFile,
                     widthHeight=pbSettings["Resolution"],
                     percent=pbSettings["Percent"],
                     quality=pbSettings["Quality"],
                     compression=pbSettings["Codec"],
                     sound=activeSound,
                     uts=True)
        ## remove window when pb is donw
        cmds.deleteUI(tempWindow)

        # Get back to the original frame range if the codec is Quick Time
        if pbSettings["Format"] == 'qt':
            cmds.playbackOptions(maxTime=maxTime)
            cmds.playbackOptions(animationEndTime=endTime)

        ## remove the custom HUdS
        if pbSettings["ShowFrameNumber"]:
            cmds.headsUpDisplay('SMFrame', rem=True)
        if pbSettings["ShowSceneName"]:
            cmds.headsUpDisplay('SMScene', rem=True)
        if pbSettings["ShowCategory"]:
            cmds.headsUpDisplay('SMCategory', rem=True)
        if pbSettings["ShowFPS"]:
            cmds.headsUpDisplay('SMFPS', rem=True)
        try:
            if pbSettings["ShowFrameRange"]:
                cmds.headsUpDisplay('SMFrange', rem=True)
        except KeyError:
            pass

            cmds.headsUpDisplay('SMCameraName', rem=True)

        ## get back the previous state of HUDS
        for hud in hudPreStates.keys():
            cmds.headsUpDisplay(hud, e=True, vis=hudPreStates[hud])
        pm.select(selection)
        ## find this version in the json data
        for i in jsonInfo["Versions"]:
            if relVersionName == i[0]:
                i[4][currentCam] = relPlayBlastFile

        self._dumpJson(jsonInfo, openSceneInfo["jsonFile"])
        return 0, ""


    def loadBasescene(self, force=False):
        # TODO // TEST IT
        relSceneFile = self._currentSceneInfo["Versions"][self._currentVersionIndex][0]
        absSceneFile = os.path.join(self.projectDir, relSceneFile)
        if os.path.isfile(absSceneFile):
            cmds.file(absSceneFile, o=True, force=force)
            return 0
        else:
            msg = "File in Scene Manager database doesnt exist"
            cmds.error(msg)
            return -1, msg

    def importBaseScene(self, force=False):
        # TODO // TEST IT
        relSceneFile = self._currentSceneInfo["Versions"][self._currentVersionIndex][0]
        absSceneFile = os.path.join(self.projectDir, relSceneFile)
        if os.path.isfile(absSceneFile):
            cmds.file(absSceneFile, i=True, force=force)
            return 0
        else:
            msg = "File in Scene Manager database doesnt exist"
            cmds.error(msg)
            return -1, msg
        pass

    def loadReference(self):
        # TODO // TEST IT
        projectPath = self.projectDir
        relReferenceFile = self._currentSceneInfo["ReferenceFile"]

        # os.path.isfile(referenceFile)
        if relReferenceFile:
            # referenceFile = "%s%s" % (projectPath, relReferenceFile)
            referenceFile = os.path.join(projectPath, relReferenceFile)
            # pm.FileReference(referenceFile)
            refFileBasename = os.path.split(relReferenceFile)[1]
            namespace = os.path.splitext(refFileBasename)[0]
            cmds.file(os.path.normpath(referenceFile), reference=True, gl=True, mergeNamespacesOnClash=False,
                      namespace=namespace)

        else:
            cmds.warning("There is no reference set for this scene. Nothing changed")


    def createThumbnail(self, databaseDir=None, version=None):

        ## TODO // TEST IT

        if databaseDir and version:
            version= "v%s" %(str(version).zfill(3))
            shotName=self._niceName(databaseDir)
            projectPath = self.projectDir

        else: # if keywords are not given
        # resolve the path of the currently open scene
            openSceneInfo = self.getOpenSceneInfo()
            if not openSceneInfo:
                return None
            projectPath=openSceneInfo["projectPath"]
            databaseDir=openSceneInfo["jsonFile"]
            shotName=openSceneInfo["shotName"]
            version=openSceneInfo["version"]

        dbDir = os.path.split(databaseDir)[0]
        thumbPath = "{0}_{1}_thumb.jpg".format(os.path.join(dbDir, shotName), version)
        relThumbPath = os.path.relpath(thumbPath, projectPath)
        # print thumbPath
        # create a thumbnail using playblast
        thumbDir = os.path.split(thumbPath)[0]
        if os.path.exists(thumbDir):
            frame = pm.currentTime(query=True)
            store = pm.getAttr("defaultRenderGlobals.imageFormat")
            pm.setAttr("defaultRenderGlobals.imageFormat", 8)  # This is the value for jpeg
            pm.playblast(completeFilename=thumbPath, forceOverwrite=True, format='image', width=221, height=124,
                         showOrnaments=False, frame=[frame], viewer=False, percent=100)
            pm.setAttr("defaultRenderGlobals.imageFormat", store) #take it back
        else:
            pm.warning("something went wrong with thumbnail. Skipping thumbnail")
            return None
        # return thumbPath
        return relThumbPath


    def replaceThumbnail(self, mode="file", databaseDir=None, version=None, filePath=None ):
        jsonInfo = self._loadJson(databaseDir)
        if mode == "file":
            if not filePath:
                cmds.warning("filePath flag cannot be None in mode='file'")
                return
            ## do the replacement
            pass

        if mode == "currentView":
            ## do the replacement
            filePath = self.createThumbnail(databaseDir=databaseDir, version=version)

        try:
            jsonInfo["Versions"][version][5]=filePath
        except IndexError: # if this is an older file without thumbnail
            jsonInfo["Versions"][version].append(filePath)
            self._dumpJson(jsonInfo, databaseDir)

class MainUI(QtWidgets.QMainWindow):
    def __init__(self, scriptJob=None):
        # self.scriptJob=scriptJob
        for entry in QtWidgets.QApplication.allWidgets():
            try:
                if entry.objectName() == SM_Version:
                    entry.close()
            except AttributeError:
                pass
        parent = getMayaMainWindow()
        super(MainUI, self).__init__(parent=parent)
        # super(MainUI, self).__init__(parent=None)
        self.manager = MayaManager()
        problem, msg = self.manager._checkRequirements()
        if problem:
            q = QtWidgets.QMessageBox()
            q.setIcon(QtWidgets.QMessageBox.Information)
            q.setText(msg[0])
            q.setInformativeText(msg[1])
            q.setWindowTitle(msg[2])
            q.setStandardButtons(QtWidgets.QMessageBox.Ok)

            ret = q.exec_()
            if ret == QtWidgets.QMessageBox.Ok:
                self.close()
                self.deleteLater()

        self.setObjectName(SM_Version)
        self.resize(680, 600)
        self.setWindowTitle(SM_Version)
        self.centralwidget = QtWidgets.QWidget(self)

        self.buildUI()
        self.setCentralWidget(self.centralwidget)

        self.initMainUI()
        # create scripJobs
        # scriptJob = "tik_sceneManager"
        # if scriptJob:
        #     self.job_1 = pm.scriptJob(e=["workspaceChanged", "%s.refresh()" % scriptJob], parent=SM_Version)

        # self.statusBar().showMessage("System Status | Normal")

    # def buildUI(self, sceneManager_MainWindow):
    def buildUI(self):
        # sceneManager_MainWindow.setObjectName(("sceneManager_MainWindow"))
        # sceneManager_MainWindow.setCentralWidget(self.centralwidget)
        #
        # self.centralwidget = QtWidgets.QWidget(sceneManager_MainWindow)
        # self.centralwidget.setObjectName(("centralwidget"))

        self.main_gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.main_gridLayout.setObjectName(("main_gridLayout"))

        self.main_horizontalLayout = QtWidgets.QHBoxLayout()
        self.main_horizontalLayout.setContentsMargins(-1, -1, 0, -1)
        self.main_horizontalLayout.setSpacing(6)
        self.main_horizontalLayout.setObjectName(("horizontalLayout"))
        self.main_horizontalLayout.setStretch(0, 1)

        self.saveVersion_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.saveVersion_pushButton.setMinimumSize(QtCore.QSize(150, 45))
        self.saveVersion_pushButton.setMaximumSize(QtCore.QSize(150, 45))
        self.saveVersion_pushButton.setText(("Save As Version"))
        self.saveVersion_pushButton.setObjectName(("saveVersion_pushButton"))
        self.main_horizontalLayout.addWidget(self.saveVersion_pushButton)

        self.saveBaseScene_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.saveBaseScene_pushButton.setMinimumSize(QtCore.QSize(150, 45))
        self.saveBaseScene_pushButton.setMaximumSize(QtCore.QSize(150, 45))
        self.saveBaseScene_pushButton.setText(("Save Base Scene"))
        self.saveBaseScene_pushButton.setObjectName(("saveBaseScene_pushButton"))
        self.main_horizontalLayout.addWidget(self.saveBaseScene_pushButton)

        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.main_horizontalLayout.addItem(spacerItem)

        self.loadScene_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.loadScene_pushButton.setMinimumSize(QtCore.QSize(150, 45))
        self.loadScene_pushButton.setMaximumSize(QtCore.QSize(150, 45))
        self.loadScene_pushButton.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.loadScene_pushButton.setText(("Load Scene"))
        self.loadScene_pushButton.setObjectName(("loadScene_pushButton"))
        self.main_horizontalLayout.addWidget(self.loadScene_pushButton)
        #
        self.main_gridLayout.addLayout(self.main_horizontalLayout, 4, 0, 1, 1)
        #
        self.r2_gridLayout = QtWidgets.QGridLayout()
        self.r2_gridLayout.setObjectName(("r2_gridLayout"))
        self.r2_gridLayout.setColumnStretch(1, 1)

        self.load_radioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.load_radioButton.setText(("Load Mode"))
        # self.load_radioButton.setChecked(False)
        self.load_radioButton.setObjectName(("load_radioButton"))
        # print self.manager.currentMode
        self.load_radioButton.setChecked(self.manager.currentMode)
        self.r2_gridLayout.addWidget(self.load_radioButton, 0, 0, 1, 1)


        self.subProject_label = QtWidgets.QLabel(self.centralwidget)
        self.subProject_label.setText(("Sub-Project:"))
        self.subProject_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.subProject_label.setObjectName(("subProject_label"))
        self.r2_gridLayout.addWidget(self.subProject_label, 0, 2, 1, 1)

        self.subProject_comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.subProject_comboBox.setMinimumSize(QtCore.QSize(150, 30))
        self.subProject_comboBox.setMaximumSize(QtCore.QSize(16777215, 30))
        self.subProject_comboBox.setObjectName(("subProject_comboBox"))
        self.r2_gridLayout.addWidget(self.subProject_comboBox, 0, 3, 1, 1)

        self.reference_radioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.reference_radioButton.setText(("Reference Mode"))
        self.reference_radioButton.setChecked(not self.manager.currentMode)
        self.reference_radioButton.setObjectName(("reference_radioButton"))
        self.r2_gridLayout.addWidget(self.reference_radioButton, 0, 1, 1, 1)

        self.addSubProject_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.addSubProject_pushButton.setMinimumSize(QtCore.QSize(30, 30))
        self.addSubProject_pushButton.setMaximumSize(QtCore.QSize(30, 30))
        self.addSubProject_pushButton.setText(("+"))
        self.addSubProject_pushButton.setObjectName(("addSubProject_pushButton"))
        self.r2_gridLayout.addWidget(self.addSubProject_pushButton, 0, 4, 1, 1)

        self.user_label = QtWidgets.QLabel(self.centralwidget)
        self.user_label.setText(("User:"))
        self.user_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.user_label.setObjectName(("user_label"))
        self.r2_gridLayout.addWidget(self.user_label, 0, 5, 1, 1)

        self.user_comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.user_comboBox.setMinimumSize(QtCore.QSize(130, 30))
        self.user_comboBox.setMaximumSize(QtCore.QSize(16777215, 30))
        self.user_comboBox.setObjectName(("user_comboBox"))
        self.r2_gridLayout.addWidget(self.user_comboBox, 0, 6, 1, 1)

        self.main_gridLayout.addLayout(self.r2_gridLayout, 1, 0, 1, 1)
        self.r1_gridLayout = QtWidgets.QGridLayout()
        self.r1_gridLayout.setObjectName(("r1_gridLayout"))

        self.baseScene_label = QtWidgets.QLabel(self.centralwidget)
        self.baseScene_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.baseScene_label.setText(("Base Scene:"))
        self.baseScene_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.baseScene_label.setObjectName(("baseScene_label"))
        self.r1_gridLayout.addWidget(self.baseScene_label, 0, 0, 1, 1)

        self.baseScene_lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.baseScene_lineEdit.setText((""))
        self.baseScene_lineEdit.setPlaceholderText((""))
        self.baseScene_lineEdit.setObjectName(("baseScene_lineEdit"))
        self.r1_gridLayout.addWidget(self.baseScene_lineEdit, 0, 1, 1, 1)

        self.project_label = QtWidgets.QLabel(self.centralwidget)
        self.project_label.setText(("Project:"))
        self.project_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.project_label.setObjectName(("project_label"))
        self.r1_gridLayout.addWidget(self.project_label, 1, 0, 1, 1)

        self.project_lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.project_lineEdit.setText((""))
        self.project_lineEdit.setPlaceholderText((""))
        self.project_lineEdit.setObjectName(("project_lineEdit"))
        self.project_lineEdit.setReadOnly(True)
        self.r1_gridLayout.addWidget(self.project_lineEdit, 1, 1, 1, 1)

        self.setProject_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.setProject_pushButton.setText(("SET"))
        self.setProject_pushButton.setObjectName(("setProject_pushButton"))
        self.r1_gridLayout.addWidget(self.setProject_pushButton, 1, 2, 1, 1)

        self.main_gridLayout.addLayout(self.r1_gridLayout, 0, 0, 1, 1)

        self.category_tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.category_tabWidget.setMaximumSize(QtCore.QSize(16777215, 20))
        self.category_tabWidget.setTabPosition(QtWidgets.QTabWidget.North)
        self.category_tabWidget.setElideMode(QtCore.Qt.ElideNone)
        self.category_tabWidget.setUsesScrollButtons(False)
        self.category_tabWidget.setObjectName(("tabWidget"))

        for i in self.manager._categories:
            self.preTab = QtWidgets.QWidget()
            self.preTab.setObjectName((i))
            self.category_tabWidget.addTab(self.preTab, (i))

        self.category_tabWidget.setCurrentIndex(self.manager.currentTabIndex)

        self.main_gridLayout.addWidget(self.category_tabWidget, 2, 0, 1, 1)

        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(("splitter"))


        self.scenes_listWidget = QtWidgets.QListWidget(self.splitter)
        self.scenes_listWidget.setObjectName(("listWidget"))

        self.frame = QtWidgets.QFrame(self.splitter)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName(("frame"))

        self.gridLayout_6 = QtWidgets.QGridLayout(self.frame)
        self.gridLayout_6.setContentsMargins(-1, -1, 0, 0)
        self.gridLayout_6.setObjectName(("gridLayout_6"))

        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName(("verticalLayout"))

        self.notes_label = QtWidgets.QLabel(self.frame)
        self.notes_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.notes_label.setText(("Version Notes:"))
        self.notes_label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.notes_label.setObjectName(("version_label_2"))
        self.verticalLayout.addWidget(self.notes_label)

        self.notes_textEdit = QtWidgets.QTextEdit(self.frame)
        self.notes_textEdit.setObjectName(("textEdit"))
        self.notes_textEdit.setReadOnly(True)
        self.verticalLayout.addWidget(self.notes_textEdit)


        self.tPixmap = QtGui.QPixmap("")
        self.thumbnail_label = ImageWidget(self.frame)
        self.thumbnail_label.setPixmap(self.tPixmap)



        self.thumbnail_label.setMinimumSize(QtCore.QSize(221, 124))
        self.thumbnail_label.setFrameShape(QtWidgets.QFrame.Box)
        self.thumbnail_label.setScaledContents(True)
        self.thumbnail_label.setAlignment(QtCore.Qt.AlignCenter)
        self.thumbnail_label.setObjectName(("label"))
        self.verticalLayout.addWidget(self.thumbnail_label)

        self.gridLayout_6.addLayout(self.verticalLayout, 3, 0, 1, 1)

        self.gridLayout_7 = QtWidgets.QGridLayout()
        self.gridLayout_7.setContentsMargins(-1, -1, 10, 10)
        self.gridLayout_7.setObjectName(("gridLayout_7"))

        self.showPreview_pushButton = QtWidgets.QPushButton(self.frame)
        self.showPreview_pushButton.setMinimumSize(QtCore.QSize(100, 30))
        self.showPreview_pushButton.setMaximumSize(QtCore.QSize(150, 30))
        self.showPreview_pushButton.setText(("Show Preview"))
        self.showPreview_pushButton.setObjectName(("setProject_pushButton_5"))
        self.gridLayout_7.addWidget(self.showPreview_pushButton, 0, 3, 1, 1)

        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setSpacing(1)
        self.horizontalLayout_4.setObjectName(("horizontalLayout_4"))

        self.version_label = QtWidgets.QLabel(self.frame)
        self.version_label.setMinimumSize(QtCore.QSize(60, 30))
        self.version_label.setMaximumSize(QtCore.QSize(60, 30))
        self.version_label.setFrameShape(QtWidgets.QFrame.Box)
        self.version_label.setText(("Version:"))
        self.version_label.setAlignment(QtCore.Qt.AlignCenter)
        self.version_label.setObjectName(("version_label"))
        self.horizontalLayout_4.addWidget(self.version_label)

        self.version_comboBox = QtWidgets.QComboBox(self.frame)
        self.version_comboBox.setMinimumSize(QtCore.QSize(60, 30))
        self.version_comboBox.setMaximumSize(QtCore.QSize(100, 30))
        self.version_comboBox.setObjectName(("version_comboBox"))
        self.horizontalLayout_4.addWidget(self.version_comboBox)

        self.gridLayout_7.addLayout(self.horizontalLayout_4, 0, 0, 1, 1)

        self.makeReference_pushButton = QtWidgets.QPushButton(self.frame)
        self.makeReference_pushButton.setMinimumSize(QtCore.QSize(100, 30))
        self.makeReference_pushButton.setMaximumSize(QtCore.QSize(300, 30))
        self.makeReference_pushButton.setText(("Make Reference"))
        self.makeReference_pushButton.setObjectName(("makeReference_pushButton"))
        self.gridLayout_7.addWidget(self.makeReference_pushButton, 1, 0, 1, 1)

        self.addNote_pushButton = QtWidgets.QPushButton(self.frame)
        self.addNote_pushButton.setMinimumSize(QtCore.QSize(100, 30))
        self.addNote_pushButton.setMaximumSize(QtCore.QSize(150, 30))
        self.addNote_pushButton.setToolTip((""))
        self.addNote_pushButton.setStatusTip((""))
        self.addNote_pushButton.setWhatsThis((""))
        self.addNote_pushButton.setAccessibleName((""))
        self.addNote_pushButton.setAccessibleDescription((""))
        self.addNote_pushButton.setText(("Add Note"))
        self.addNote_pushButton.setObjectName(("addNote_pushButton"))
        self.gridLayout_7.addWidget(self.addNote_pushButton, 1, 3, 1, 1)

        self.gridLayout_6.addLayout(self.gridLayout_7, 0, 0, 1, 1)

        self.main_gridLayout.addWidget(self.splitter, 3, 0, 1, 1)

        self.splitter.setStretchFactor(0, 1)

        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 680, 18))
        self.menubar.setObjectName(("menubar"))

        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName(("statusbar"))
        self.setStatusBar(self.statusbar)

        # MENU BAR / STATUS BAR
        # ---------------------
        file = self.menubar.addMenu("File")
        saveVersion_fm = QtWidgets.QAction("&Save Version", self)
        saveBaseScene_fm = QtWidgets.QAction("&Save Base Scene", self)
        loadReferenceScene_fm = QtWidgets.QAction("&Load/Reference Scene", self)
        createProject_fm = QtWidgets.QAction("&Create Project", self)
        pb_settings_fm = QtWidgets.QAction("&Playblast Settings", self)
        add_remove_users_fm = QtWidgets.QAction("&Add/Remove Users", self)
        deleteFile_fm = QtWidgets.QAction("&Delete Selected Base Scene", self)
        deleteReference_fm = QtWidgets.QAction("&Delete Reference of Selected Scene", self)
        reBuildDatabase_fm = QtWidgets.QAction("&Re-build Project Database", self)
        projectReport_fm = QtWidgets.QAction("&Project Report", self)
        checkReferences_fm = QtWidgets.QAction("&Check References", self)

        #save
        file.addAction(createProject_fm)
        file.addAction(saveVersion_fm)
        file.addAction(saveBaseScene_fm)

        #load
        file.addSeparator()
        file.addAction(loadReferenceScene_fm)

        #settings
        file.addSeparator()
        file.addAction(add_remove_users_fm)
        file.addAction(pb_settings_fm)

        #delete
        file.addSeparator()
        file.addAction(deleteFile_fm)
        file.addAction(deleteReference_fm)

        #misc
        file.addSeparator()
        file.addAction(projectReport_fm)
        file.addAction(checkReferences_fm)

        tools = self.menubar.addMenu("Tools")
        imanager = QtWidgets.QAction("&Image Manager", self)
        iviewer = QtWidgets.QAction("&Image Viewer", self)
        createPB = QtWidgets.QAction("&Create PlayBlast", self)

        tools.addAction(imanager)
        tools.addAction(iviewer)
        tools.addAction(createPB)

        # RIGHT CLICK MENUS
        # -----------------

        # List Widget Right Click Menu
        self.scenes_listWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.scenes_listWidget.customContextMenuRequested.connect(self.onContextMenu_scenes)
        self.popMenu_scenes = QtWidgets.QMenu()

        scenes_rcAction_0 = QtWidgets.QAction('Import Scene', self)
        self.popMenu_scenes.addAction(scenes_rcAction_0)
        scenes_rcAction_0.triggered.connect(lambda: self.scenes_rcAction("importScene"))

        scenes_rcAction_1 = QtWidgets.QAction('Show Maya Folder in Explorer', self)
        self.popMenu_scenes.addAction(scenes_rcAction_1)
        scenes_rcAction_1.triggered.connect(lambda: self.scenes_rcAction("showInExplorerMaya"))

        scenes_rcAction_2 = QtWidgets.QAction('Show Playblast Folder in Explorer', self)
        self.popMenu_scenes.addAction(scenes_rcAction_2)
        scenes_rcAction_2.triggered.connect(lambda: self.scenes_rcAction("showInExplorerPB"))

        scenes_rcAction_3 = QtWidgets.QAction('Show Data Folder in Explorer', self)
        self.popMenu_scenes.addAction(scenes_rcAction_3)
        scenes_rcAction_3.triggered.connect(lambda: self.scenes_rcAction("showInExplorerData"))

        self.popMenu_scenes.addSeparator()
        scenes_rcAction_4 = QtWidgets.QAction('Scene Info', self)
        self.popMenu_scenes.addAction(scenes_rcAction_4)
        scenes_rcAction_3.triggered.connect(lambda: self.scenes_rcAction("showInExplorerData"))

        # Thumbnail Right Click Menu
        self.thumbnail_label.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.thumbnail_label.customContextMenuRequested.connect(self.onContextMenu_thumbnail)
        self.popMenu_thumbnail = QtWidgets.QMenu()

        thumb_rcAction_0 = QtWidgets.QAction('Replace with current view', self)
        self.popMenu_thumbnail.addAction(thumb_rcAction_0)

        thumb_rcAction_1 = QtWidgets.QAction('Replace with external file', self)
        self.popMenu_thumbnail.addAction(thumb_rcAction_1)

        # SHORTCUTS
        # ---------
        # shortcutRefresh = Qt.QShortcut(Qt.QKeySequence("F5"), self, self.refresh)

        # SIGNAL CONNECTIONS
        # ------------------

        self.statusBar().showMessage("Status | Idle")

        self.load_radioButton.clicked.connect(self.onModeChanged)
        self.reference_radioButton.clicked.connect(self.onModeChanged)

        self.category_tabWidget.currentChanged.connect(self.onCategoryChange)

        self.scenes_listWidget.currentItemChanged.connect(self.onBaseSceneChange)

        self.version_comboBox.activated.connect(self.onVersionChange)

        self.makeReference_pushButton.clicked.connect(self.onMakeReference)

        self.subProject_comboBox.activated.connect(self.onSubProjectChange)

    def scenes_rcAction(self, command):
        if command == "importScene":
            # TODO // add import function to root class
            print "Import Scene at cursor position"
        if command == "showInExplorerMaya":
            row = self.scenes_listWidget.currentRow()
            if not row == -1:
                if self.manager.currentPlatform == "Windows":
                    os.startfile(self.manager.currentBaseScenePath)
                if self.manager.currentPlatform == "Linux":
                    os.system('nautilus %s' % self.manager.currentBaseScenePath)

        # if command == "showInExplorerPB":
        #     row = self.scenes_listWidget.currentRow()
        #     if not row == -1:
        #         sceneName = "%s.json" % self.scenes_listWidget.currentItem().text()
        #         # takethefirstjson as example for rootpath
        #         jPath = os.path.join(pathOps(self.scenesInCategory[0], "path"), sceneName)
        #
        #         # sceneData = loadJson(os.path.join(jPath, sceneName))
        #         sceneData = self.manager.database.loadJson(jPath)
        #
        #         path = os.path.join(os.path.normpath(self.manager.scenePaths["projectPath"]), os.path.normpath(sceneData["Path"]))
        #         path = path.replace("scenes", "Playblasts")
        #         if os.path.isdir(path):
        #             if self.manager.currentPlatform == "Windows":
        #                 os.startfile(path)
        #             if self.manager.currentPlatform == "Linux":
        #                 os.system('nautilus %s' % path)
        #         else:
        #             self.infoPop(textTitle="", textHeader="Scene does not have a playblast",
        #                          textInfo="There is no playblast folder created for this scene yet")
        #
        # if command == "showInExplorerData":
        #     row = self.scenes_listWidget.currentRow()
        #     if not row == -1:
        #         try:
        #             path = pathOps(self.scenesInCategory[row], "path")
        #         except:
        #             path = pathOps(self.scenesInCategory[0], "path")
        #         if self.manager.currentPlatform == "Windows":
        #             os.startfile(path)
        #         if self.manager.currentPlatform == "Linux":
        #             os.system('nautilus %s' % path)


    def onContextMenu_scenes(self, point):
        # show context menu
        self.popMenu_scenes.exec_(self.scenes_listWidget.mapToGlobal(point))
    def onContextMenu_thumbnail(self, point):
        # show context menu
        self.popMenu_thumbnail.exec_(self.thumbnail_label.mapToGlobal(point))

    def onMakeReference(self):
        self.manager.makeReference()
        self.onVersionChange()
        self.statusBar().showMessage(
            "Status | Version {1} is the new reference of {0}".format(self.manager.currentBaseSceneName, self.manager.currentVersionIndex))

    def onPreviewChange(self):
        #get/set Previews
        pass

    def onSubProjectChange(self):
        pass

    def onVersionChange(self):
        logger.debug("onVersionChange%s" %self.version_comboBox.currentIndex())

        if self.version_comboBox.currentIndex() is not -1:
            self.manager.currentVersionIndex = self.version_comboBox.currentIndex() + 1
        # print self.manager.getThumbnail()
        # clear Notes and verison combobox

        self.notes_textEdit.clear()


        # update notes
        self.notes_textEdit.setPlainText(self.manager.getNotes())

        # update thumb
        self.tPixmap = QtGui.QPixmap(self.manager.getThumbnail())
        self.thumbnail_label.setPixmap(self.tPixmap)

        # logger.debug("currentVersionIndex: %s --- getVersions: %s" %(self.manager.currentVersionIndex, len(self.manager.getVersions())))
        if self.manager.currentVersionIndex != len(self.manager.getVersions()) and self.manager.currentVersionIndex != -1:
            self.version_comboBox.setStyleSheet("background-color: rgb(80,80,80); color: yellow")
        else:
            self.version_comboBox.setStyleSheet("background-color: rgb(80,80,80); color: white")

    def onBaseSceneChange(self):
        #clear version_combobox
        self.version_comboBox.clear()

        logger.debug("onBaseSceneChange")
        row = self.scenes_listWidget.currentRow()
        if row == -1:
            self.manager.currentBaseSceneName = ""
            self._vEnableDisable(False)
        else:
            self.manager.currentBaseSceneName = self.scenes_listWidget.currentItem().text()
            self._vEnableDisable(True)
        #get versions and add it to the combobox
        versionData = self.manager.getVersions()
        for num in range(len(versionData)):
            self.version_comboBox.addItem("v{0}".format(str(num + 1).zfill(3)))
        logger.debug("curIn %s" %self.manager.currentVersionIndex)
        self.version_comboBox.setCurrentIndex(self.manager.currentVersionIndex-1)
        # if self.manager.currentVersionIndex != len(versionData):
        #     self.version_comboBox.setStyleSheet("background-color: rgb(80,80,80); color: yellow")
        # else:
        #     self.version_comboBox.setStyleSheet("background-color: rgb(80,80,80); color: white")

        self.onVersionChange()

    def onSubProjectChange(self):
        self.manager.currentSubIndex = self.subProject_comboBox.currentIndex()
        self.onCategoryChange()

    def onProjectChange(self):
        self.onSubProjectChange()
        self.onCategoryChange()
        self.onBaseSceneChange()
        self.onVersionChange()
        self.onPreviewChange()


    def onCategoryChange(self):
        logger.debug("onCategoryChange %s" %self.category_tabWidget.currentIndex())
        self.manager.currentTabIndex = self.category_tabWidget.currentIndex()
        self.populateBaseScenes()
        self.onBaseSceneChange()

    def onModeChanged(self):
        state = self.load_radioButton.isChecked()
        logger.debug("onModeChanged_%s" %state)
        # logger.warning(state)
        self._vEnableDisable(state)
        # self.version_label.setEnabled(state)
        # self.notes_label.setEnabled(state)
        # self.notes_textEdit.setEnabled(state)
        # self.showPreview_pushButton.setEnabled(state)
        if state:
            self.loadScene_pushButton.setText("Load Scene")
            self.scenes_listWidget.setStyleSheet("border-style: solid; border-width: 2px; border-color: grey;")
        else:
            self.loadScene_pushButton.setText("Reference Scene")
            self.scenes_listWidget.setStyleSheet("border-style: solid; border-width: 2px; border-color: cyan;")

        self.manager.currentMode = state
        self.populateBaseScenes()

    def populateBaseScenes(self):
        self.scenes_listWidget.clear()
        logger.debug("populateBaseScenes")
        baseScenesDict = self.manager.getBaseScenesInCategory()
        if self.reference_radioButton.isChecked():
            for key in baseScenesDict:
                if self.manager.checkReference(baseScenesDict[key]) == 1:
                    self.scenes_listWidget.addItem(key)

        else:
            codeDict = {-1: QtGui.QColor(255, 0, 0, 255), 1: QtGui.QColor(0, 255, 0, 255),
                        0: QtGui.QColor(255, 255, 0, 255)}  # dictionary for color codes red, green, yellow

            for key in baseScenesDict:
                retCode = self.manager.checkReference(baseScenesDict[key]) # returns -1, 0 or 1 for color ref
                color = codeDict[retCode]
                listItem = QtWidgets.QListWidgetItem()
                listItem.setText(key)
                listItem.setForeground(color)
                self.scenes_listWidget.addItem(listItem)

    def initMainUI(self):
        logger.debug("initMainUI")
        # #remember mode
        #
        openSceneInfo = self.manager.getOpenSceneInfo()
        if openSceneInfo: ## getSceneInfo returns None if there is no json database fil
            self.baseScene_lineEdit.setText("%s ==> %s ==> %s" % (openSceneInfo["subProject"], openSceneInfo["category"], openSceneInfo["shotName"]))
            self.baseScene_lineEdit.setStyleSheet("background-color: rgb(40,40,40); color: cyan")
        else:
            self.baseScene_lineEdit.setText("Current Scene is not a Base Scene")
            self.baseScene_lineEdit.setStyleSheet("background-color: rgb(40,40,40); color: yellow")


        self.subProject_comboBox.addItems(self.manager.getSubProjects())
        self.subProject_comboBox.setCurrentIndex(self.manager.currentSubIndex)
        # #remember category
        # logger.warning(self.manager.currentTabIndex)
        # self.category_tabWidget.setCurrentIndex(self.manager.currentTabIndex)
        self.project_lineEdit.setText(self.manager.projectDir)
        self.populateBaseScenes()

        self.user_comboBox.addItems(self.manager.getUsers())
        # disable the version related stuff
        self._vEnableDisable(False)





    def _vEnableDisable(self, state):
        self.version_comboBox.setEnabled(state)
        self.showPreview_pushButton.setEnabled(state)
        self.makeReference_pushButton.setEnabled(state)
        self.addNote_pushButton.setEnabled(state)

        self.version_label.setEnabled(state)


    # def onModeChanged(self):
    #     state = self.load_radioButton.isChecked()
    #     self.version_label.setEnabled(state)
    #     self.makeReference_pushButton.setEnabled(state)
    #     self.notes_label.setEnabled(state)
    #     self.notes_textEdit.setEnabled(state)
    #     self.showPreview_pushButton.setEnabled(state)
    #     if state:
    #         self.loadScene_pushButton.setText("Load Scene")
    #         self.scenes_listWidget.setStyleSheet("border-style: solid; border-width: 2px; border-color: grey;")
    #     else:
    #         self.loadScene_pushButton.setText("Reference Scene")
    #         self.scenes_listWidget.setStyleSheet("border-style: solid; border-width: 2px; border-color: cyan;")
    #     self.populateBaseScenes()

class ImageWidget(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super(ImageWidget, self).__init__()
        self.aspectRatio = 1.78
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)

    def resizeEvent(self, r):
        h = self.width()
        self.setMinimumHeight(h/self.aspectRatio)
        self.setMaximumHeight(h/self.aspectRatio)



