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

class MayaManager(RootManager):
    def __init__(self):
        super(MayaManager, self).__init__()
        self.init_paths()
        self.init_database()
        # self.backwardcompatibility() # DO NOT RUN UNTIL RELEASE

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

    def set_project(self, path):
        # totally software specific or N/A
        melCompPath = path.replace("\\", "/") # mel is picky
        command = 'setProject "%s";' %melCompPath
        mel.eval(command)
        # self.projectDir = cmds.workspace(q=1, rd=1)
        self.projectDir = self.getProjectDir()

    def getSceneInfo(self):
        """
        Collects the necessary scene info by resolving the scene name and current project
        Returns: Dictionary{jsonFile, projectPath, subProject, category, shotName} or None
        """
        # TODO // TEST IT
        self._pathsDict["sceneFile"] = self.getSceneFile()
        if not self._pathsDict["sceneFile"]:
            return None

        # get name of the upper directory to find out base name
        sceneDir = os.path.abspath(os.path.join(self._pathsDict["sceneFile"], os.pardir))
        baseSceneName = os.path.basename(sceneDir)

        upperSceneDir = os.path.abspath(os.path.join(sceneDir, os.pardir))
        upperSceneDirName = os.path.basename(upperSceneDir)

        if upperSceneDirName in self._subProjectsList:
            subProjectDir = upperSceneDir
            subProject = upperSceneDirName
            categoryDir = os.path.abspath(os.path.join(subProjectDir, os.pardir))
            category = os.path.basename(categoryDir)

            dbCategoryPath = os.path.normpath(os.path.join(self._pathsDict["databaseDir"], category))
            dbPath = os.path.normpath(os.path.join(dbCategoryPath, subProject))

        else:
            subProject = self._subProjectsList[0]
            categoryDir = upperSceneDir
            category = upperSceneDirName
            dbPath = os.path.normpath(os.path.join(self._pathsDict["databaseDir"], category))

        jsonFile = os.path.join(dbPath, "{}.json".format(baseSceneName))
        if os.path.isfile(jsonFile):
            version = (self._niceName(baseSceneName)[-4:])
            return {"jsonFile":jsonFile,
                    "projectPath":self._pathsDict["projectDir"],
                    "subProject":subProject,
                    "category":category,
                    "shotName":baseSceneName,
                    "version":version
                    }
        else:
            return None

    def saveCallback(self):
        """Callback function to update reference files when files saved regularly"""
        ## TODO // TEST IT
        self._pathsDict["sceneFile"] = self.getSceneFile()
        openSceneInfo = self.getSceneInfo()
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

        # projectPath, jsonPath, scenesPath = getPathsFromScene("projectPath", "jsonPath", "scenesPath")
        projectPath = self.projectDir
        jsonPath = self._pathsDict["databaseDir"]
        scenesPath = self._pathsDict["scenesDir"]
        categoryPath = os.path.normpath(os.path.join(scenesPath, categoryName))
        self._folderCheck(categoryPath)

        ## if its going to be saved as a subproject
        if not subProjectIndex == 0:
            subProjectPath = os.path.normpath(os.path.join(categoryPath, self._subProjectsList[subProjectIndex]))
            self._folderCheck(subProjectPath)
            shotPath = os.path.normpath(os.path.join(subProjectPath, baseName))
            self._folderCheck(shotPath)

            jsonCategoryPath = os.path.normpath(os.path.join(jsonPath, categoryName))
            self._folderCheck(jsonCategoryPath)
            jsonCategorySubPath = os.path.normpath(os.path.join(jsonCategoryPath, self._subProjectsList[subProjectIndex]))
            self._folderCheck(jsonCategorySubPath)
            jsonFile = os.path.join(jsonCategorySubPath, "{}.json".format(baseName))
        else:
            shotPath = os.path.normpath(os.path.join(categoryPath, baseName))
            self._folderCheck(shotPath)

            jsonCategoryPath = os.path.normpath(os.path.join(jsonPath, categoryName))
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

        thumbPath = self.createThumbnail(jsonPath=jsonFile, version=version)

        jsonInfo = {}

        if makeReference:
            referenceName = "{0}_{1}_forReference".format(baseName, categoryName)
            referenceFile = os.path.join(shotPath, "{0}.mb".format(referenceName))
            ## relativity update
            relReferenceFile = os.path.relpath(referenceFile, start=projectPath)
            shutil.copyfile(sceneFile, referenceFile)
            jsonInfo["ReferenceFile"] = relReferenceFile
            jsonInfo["ReferencedVersion"] = version
        else:
            jsonInfo["ReferenceFile"] = None
            jsonInfo["ReferencedVersion"] = None

        jsonInfo["ID"] = "SceneManagerV01_sceneFile"
        jsonInfo["MayaVersion"] = pm.versions.current()
        jsonInfo["Name"] = baseName
        jsonInfo["Path"] = os.path.relpath(shotPath, start=projectPath)
        jsonInfo["Category"] = categoryName
        jsonInfo["Creator"] = self.currentUser
        jsonInfo["CreatorHost"] = (socket.gethostname())
        jsonInfo["Versions"] = [ # PATH => Notes => User Initials => Machine ID => Playblast => Thumbnail
            [relSceneFile, completeNote,  self._usersDict[self.currentUser], socket.gethostname(), {}, thumbPath]]
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

        sceneInfo = self.getSceneInfo()

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
                relReferenceFile = os.path.join(jsonInfo["Path"], "{0}.mb".format(referenceName))
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

        sceneName = self.getSceneFile()
        if not sceneName:
            msg = "This is not a base scene. Scene must be saved as a base scene before playblasting."
            pm.warning(msg)
            return -1, msg

        projectPath = self.projectDir
        jsonPath = self._pathsDict["databaseDir"]
        playBlastRoot = self._pathsDict["previewsDir"]

        # TODO // FOLLOWING LINES ARE USED MULTIPLE TIMES, GATHER THEM IN A FUNCTION
        # first get the parent dir
        shotDirectory = os.path.abspath(os.path.join(pm.sceneName(), os.pardir))
        shotName = os.path.basename(shotDirectory)

        upperShotDir = os.path.abspath(os.path.join(shotDirectory, os.pardir))
        upperShot = os.path.basename(upperShotDir)

        if upperShot in self._subProjectsList:
            subProjectDir = upperShotDir
            subProject = upperShot
            categoryDir = os.path.abspath(os.path.join(subProjectDir, os.pardir))
            category = os.path.basename(categoryDir)

            jsonCategoryPath = os.path.normpath(os.path.join(jsonPath, category))
            self._folderCheck(jsonCategoryPath)
            jsonPath = os.path.normpath(os.path.join(jsonCategoryPath, subProject))
            self._folderCheck(jsonPath)

            pbCategoryPath = os.path.normpath(os.path.join(playBlastRoot, category))
            self._folderCheck(pbCategoryPath)
            pbSubPath = os.path.normpath(os.path.join(pbCategoryPath, subProject))
            self._folderCheck(pbSubPath)
            pbPath = os.path.normpath(os.path.join(pbSubPath, shotName))
            self._folderCheck(pbPath)

        else:
            # categoryDir = upperShotDir
            category = upperShot
            jsonPath = os.path.normpath(os.path.join(jsonPath, category))
            self._folderCheck(jsonPath)
            pbCategoryPath = os.path.normpath(os.path.join(playBlastRoot, category))
            self._folderCheck(pbCategoryPath)
            pbPath = os.path.normpath(os.path.join(pbCategoryPath, shotName))
            self._folderCheck(pbPath)

        jsonFile = os.path.join(jsonPath, "{}.json".format(shotName))

        if os.path.isfile(jsonFile):

            selection = pm.ls(sl=True)
            pm.select(d=pbSettings["ClearSelection"])
            jsonInfo = self.database.loadJson(jsonFile)

            currentCam = cmds.modelPanel(cmds.getPanel(wf=True), q=True, cam=True)

            validName = "_"
            if not self._nameCheck(currentCam) == -1:
                validName = self._nameCheck(currentCam)
            else:
                msg = "A scene view must be highlighted"
                cmds.warning(msg)
                return -1, msg

            versionName = self.getSceneFile()
            relVersionName = os.path.relpath(versionName, start=projectPath)
            playBlastFile = os.path.join(pbPath,
                                         "{0}_{1}_PB.{2}".format(self._niceName(versionName), validName, extension))
            relPlayBlastFile = os.path.relpath(playBlastFile, start=projectPath)

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
            print "playBlastFile", playBlastFile
            normPB = os.path.normpath(playBlastFile)
            print "normPath", normPB
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

            self._dumpJson(jsonInfo, jsonFile)
            return 0, ""

        else:
            msg = "This is not a base scene (Json file cannot be found)"
            cmds.warning(msg)
            return -1, msg



    def loadBasescene(self):
        pass

    def loadReference(self):
        pass

    def createThumbnail(self, jsonPath=None, version=None):

        ## TODO // CONTINUE

        if jsonPath and version:
            version= "v%s" %(str(version).zfill(3))
            shotName=self._niceName(jsonPath)
            projectPath = self.projectDir

        else: # if keywords are not given
        # resolve the path of the currently open scene
            sceneInfo = self.getSceneInfo()
            if not sceneInfo:
                return None
            projectPath=sceneInfo["projectPath"]
            jsonPath=sceneInfo["jsonFile"]
            shotName=sceneInfo["shotName"]
            version=sceneInfo["version"]


        thumbPath = "{0}_{1}_thumb.jpg".format(os.path.join(pathOps(jsonPath, "path"), shotName), version)
        relThumbPath = os.path.relpath(thumbPath, projectPath)
        # print thumbPath
        # create a thumbnail using playblast
        if os.path.exists(pathOps(thumbPath, "path")):
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


    def replaceThumbnail(self):
        pass





