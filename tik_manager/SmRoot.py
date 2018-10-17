
import platform
import datetime
import os
import logging
import pprint

import shutil
from glob import glob
import json
import filecmp
import re
import ctypes

logging.basicConfig()
logger = logging.getLogger('smRoot')
logger.setLevel(logging.WARNING)

# TODO : Make a project settings feature (Resolution, FPS, etc.)

class RootManager(object):
    def __init__(self):
        # super(RootManager, self).__init__()

        # self.database = db.SmDatabase()
        # self.validCategories = ["Model", "Shading", "Rig", "Layout", "Animation", "Render", "Other"]

        self.currentPlatform = platform.system()
        self._pathsDict={}
        # self.padding = 3


    def init_paths(self):
        # logger.debug("Func: init_paths")
        # all paths in here must be absolute paths
        _softwarePathsDict = self.getSoftwarePaths()

        self._pathsDict["userSettingsDir"] = os.path.normpath(os.path.join(os.path.expanduser("~"), _softwarePathsDict["userSettingsDir"]))
        self._folderCheck(self._pathsDict["userSettingsDir"])

        self._pathsDict["bookmarksFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], "smBookmarks.json"))
        self._pathsDict["currentsFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], "smCurrents.json"))
        self._pathsDict["projectsFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], "smProjects.json"))

        self._pathsDict["projectDir"] = self.getProjectDir()
        self._pathsDict["sceneFile"] = ""
        # _softwarePathsDict = self.getSoftwarePaths()
        if self._pathsDict["projectDir"] == -1 or self._pathsDict["sceneFile"] == -1 or _softwarePathsDict == -1:
            msg = "The following functions must be overridden in inherited class:\n'getSoftware'\n'getProjectDir'\n'getSceneFile'"
            logger.error(msg)
            raise Exception([102, msg])

        self._pathsDict["masterDir"] = os.path.normpath(os.path.join(self._pathsDict["projectDir"], "smDatabase"))
        self._folderCheck(self._pathsDict["masterDir"])
        self._pathsDict["projectSettingsFile"] = os.path.normpath(os.path.join(self._pathsDict["masterDir"], "projectSettings.json"))

        self._pathsDict["databaseDir"] = os.path.normpath(os.path.join(self._pathsDict["masterDir"], _softwarePathsDict["databaseDir"]))
        self._folderCheck(self._pathsDict["databaseDir"])

        self._pathsDict["scenesDir"] = os.path.normpath(os.path.join(self._pathsDict["projectDir"], _softwarePathsDict["scenesDir"]))
        self._folderCheck(self._pathsDict["scenesDir"])

        self._pathsDict["subprojectsFile"] = os.path.normpath(os.path.join(self._pathsDict["databaseDir"], "subPdata.json"))
        self._pathsDict["categoriesFile"] = os.path.normpath(os.path.join(self._pathsDict["databaseDir"], _softwarePathsDict["categoriesFile"]))

        self._pathsDict["previewsDir"] = os.path.normpath(os.path.join(self._pathsDict["projectDir"], "Playblasts")) # dont change
        self._folderCheck(self._pathsDict["previewsDir"])

        self._pathsDict["pbSettingsFile"] = os.path.normpath(os.path.join(self._pathsDict["previewsDir"], _softwarePathsDict["pbSettingsFile"]))

        self._pathsDict["generalSettingsDir"] = os.path.dirname(os.path.abspath(__file__))

        self._pathsDict["usersFile"] = os.path.normpath(os.path.join(self._pathsDict["generalSettingsDir"], "sceneManagerUsers.json"))

    def getSoftwarePaths(self):
        """This function must be overriden to return the software currently working on"""
        # This function should return a dictionary which includes string values for:
        # databaseDir, scenesDir, pbSettingsFile keys. Software specific paths will be resolved with these strings
        # logger.debug("Func: getSoftwarePaths")
        return -1

    def getProjectDir(self):
        """This function must be overriden to return the project directory of running software"""
        # logger.debug("Func: getProjectDir")
        return -1

    def getSceneFile(self):
        """This function must be overriden to return the full scene path ('' for unsaved) of current scene"""
        # logger.debug("Func: getSceneFile")
        return -1

    def init_database(self):
        # logger.debug("Func: init_database")

        # self.currentPlatform = platform.system()
        self._categories = self._loadCategories()
        self._usersDict = self._loadUsers()
        self._currentsDict = self._loadUserPrefs()
        self._subProjectsList = self._loadSubprojects()

        # unsaved DB
        self._baseScenesInCategory = []
        self._currentBaseSceneName = ""
        self._currentSceneInfo = {}

        #Scene Specific
        self._currentVersionIndex = -1
        self._currentPreviewsDict = {}
        self._currentPreviewCamera = ""
        self._currentNotes = ""
        self._currentThumbFile = ""

        self._openSceneInfo = ""

        self.scanBaseScenes()

    def _setCurrents(self, att, newdata):
        """Sets the database stored cursor positions and saves them to the database file"""
        # logger.debug("Func: _setCurrents")

        self._currentsDict[att] = newdata
        self._saveUserPrefs(self._currentsDict)

    @property
    def projectDir(self):
        """Returns Current Project Directory"""
        # logger.debug("Func: projectDir/getter")
        return self._pathsDict["projectDir"]

    @projectDir.setter
    def projectDir(self, path):
        # logger.debug("Func: projectDir/setter")
        self._pathsDict["projectDir"] = path
        # self.init_paths()
        # self.init_database()

    @property
    def subProject(self):
        """Returns the name of the current sub-project"""
        # logger.debug("Func: subProject/getter")
        return self._subProjectsList[self.currentSubIndex]

    # @property
    # def baseScene(self):
    #     """Returns the name of the Base Scene at cursor position"""
    #     baseSceneDir = os.path.abspath(os.path.join(self._pathsDict["sceneFile"], os.pardir))
    #     return os.path.basename(baseSceneDir)

    @property
    def currentTabIndex(self):
        """Returns the Category index at cursor position"""
        # logger.debug("Func: currentTabIndex/getter")
        return self._currentsDict["currentTabIndex"]

    @currentTabIndex.setter
    def currentTabIndex(self, indexData):
        """Moves the cursor to the given category index"""
        # logger.debug("Func: currentTabIndex/setter")
        if not 0 <= indexData < len(self._categories):
            msg="Tab index is out of range!"
            logger.error(msg)
            raise Exception([101, msg])
        if indexData == self.currentTabIndex:
            self.cursorInfo()
            return
        self._setCurrents("currentTabIndex", indexData)
        self.scanBaseScenes()
        self.currentBaseSceneName = ""
        self._currentVersionIndex = -1
        self._currentPreviewCamera = ""
        self.cursorInfo()

    @property
    def currentSubIndex(self):
        """Returns the sub-project index at cursor position"""
        # logger.debug("Func: currentSubIndex/getter")
        return self._currentsDict["currentSubIndex"]

    @currentSubIndex.setter
    def currentSubIndex(self, indexData):
        """Moves the cursor to the given sub-project index"""
        # logger.debug("Func: currentSubIndex/setter")
        if not 0 <= indexData < len(self._subProjectsList):
            msg="Sub Project index is out of range!"
            logger.error(msg)
            raise Exception([101, msg])
        if indexData == self.currentSubIndex:
            self.cursorInfo()
            return

        self._setCurrents("currentSubIndex", indexData)
        self.scanBaseScenes()
        # de-select previous base scene
        self._currentBaseSceneName = ""
        self._currentVersionIndex = -1
        self._currentPreviewCamera = ""
        self.cursorInfo()

    @property
    def currentUser(self):
        """Returns the current user"""
        # logger.debug("Func: currentUser/getter")

        return self._currentsDict["currentUser"]

    @currentUser.setter
    def currentUser(self, name):
        """Sets the current user"""
        # logger.debug("Func: currentUser/setter")

        if name not in self._usersDict.keys():
            msg="%s is not in the user list" %name
            logger.error(msg)
            raise Exception([101, msg])
        self._setCurrents("currentUser", name)

    @property
    def currentMode(self):
        """Returns the current access mode (Load or Reference)"""
        # logger.debug("Func: currentMode/getter")

        return self._currentsDict["currentMode"]

    @currentMode.setter
    def currentMode(self, state):
        """Sets the current access mode 0 == Load, 1 == Reference"""
        # logger.debug("Func: currentMode/setter")

        if not type(state) is bool:
            if bool is 0:
                state = False
            elif bool is 1:
                state = True
            else:
                msg = ("only boolean or 0-1 accepted, entered %s" %state)
                logger.error(msg)
                raise Exception([101, msg])
        self._setCurrents("currentMode", state)

    @property
    def currentBaseSceneName(self):
        """Returns current Base Scene Name at cursor position"""
        # logger.debug("Func: currentBaseSceneName/getter")

        return self._currentBaseSceneName

    @currentBaseSceneName.setter
    def currentBaseSceneName(self, sceneName):
        """Moves the cursor to the given base scene name"""
        # logger.debug("Func: currentBaseSceneName/setter")
        if not sceneName:
            self._currentBaseSceneName = ""
            self.currentVersionIndex = -1
            return
        if sceneName not in self._baseScenesInCategory.keys():
            # self._currentVersionIndex = -1
            # self._currentThumbFile = ""
            # self._currentNotes = ""
            self.currentVersionIndex = -1
            msg = "There is no scene called %s in current category" %sceneName
            logger.error(msg)
            raise Exception([101, msg])

        self._currentBaseSceneName = sceneName
        self._currentSceneInfo = self._loadSceneInfo()

        # assert (self._currentSceneInfo == -2)
        if self._currentSceneInfo == -2: # corrupted db file
            # self._currentSceneInfo == {}
            self._currentBaseSceneName = ""
            self.currentVersionIndex = -1
            raise Exception ([200, "Database file %s is corrupted\nDo you want to fix it manually?" %sceneName, self._baseScenesInCategory[sceneName]] )
        #     return


        if self._currentSceneInfo["ReferencedVersion"]:
            self.currentVersionIndex = self._currentSceneInfo["ReferencedVersion"]
        else:
            self.currentVersionIndex = len(self._currentSceneInfo["Versions"])

        self.cursorInfo()
        # self._currentPreviewIndex = 0

    @property
    def currentBaseScenePath(self):
        """Returns absolute path of Base Scene at cursor position"""
        # logger.debug("Func: currentBaseScenePath/getter")

        return os.path.join(self.projectDir, self._currentSceneInfo["Path"])

    @property
    def currentScenePath(self):
        """Returns absolute path of Base Scene at cursor position"""
        # logger.debug("Func: currentBaseScenePath/getter")

        return os.path.join(self.projectDir, self._currentSceneInfo["Versions"][self.currentVersionIndex-1][0])

    @property
    def currentPreviewPath(self):
        """Returns absolute path of preview folder of the Base scene at cursor position"""
        # logger.debug("Func: currentPreviewPath/getter")
        if self._currentSceneInfo["SubProject"] is not "None":
            path = os.path.join(self._pathsDict["previewsDir"], self._currentSceneInfo["Category"],
                                self._currentSceneInfo["SubProject"], self._currentSceneInfo["Name"])
        else:
            path = os.path.join(self._pathsDict["previewsDir"], self._currentSceneInfo["Category"],
                                self._currentSceneInfo["SubProject"], self._currentSceneInfo["Name"])
        return path
        # if os.path.isdir(path):
        #     return path
        # else:
        #     return ""

    @property
    def currentVersionIndex(self):
        # logger.debug("Func: currentVersionIndex/getter")

        """Returns current Version index at cursor position"""
        return self._currentVersionIndex

    @currentVersionIndex.setter
    def currentVersionIndex(self, indexData):
        """Moves the cursor to given Version index"""
        # logger.debug("Func: currentVersionIndex/setter")

        if indexData <= 0:
            self._currentVersionIndex = -1
            self._currentThumbFile = ""
            self._currentNotes = ""
            self._currentPreviewCamera = ""
            return
        if not self._currentSceneInfo:
            # logger.warning(("BaseScene not Selected"))
            return
        if not 1 <= indexData <= len(self._currentSceneInfo["Versions"]):
            msg = "out of range! %s" %indexData
            logger.error(msg)
            raise Exception([101, msg])
        # if self._currentVersionIndex == indexData:
        #     logger.warning("Cursor is already at %s" % indexData)
        #     return
        self._currentVersionIndex = indexData
        self._currentNotes = self._currentSceneInfo["Versions"][self._currentVersionIndex-1][1]
        self._currentPreviewsDict = self._currentSceneInfo["Versions"][self._currentVersionIndex-1][4]
        if not self._currentPreviewsDict.keys():
            self._currentPreviewCamera = ""
        else:
            self._currentPreviewCamera = sorted(self._currentPreviewsDict.keys())[0]

        self._currentThumbFile = self._currentSceneInfo["Versions"][self._currentVersionIndex-1][5]
        self.cursorInfo()

    # @property
    # def currentPreviewCamera(self):
    #     """Returns current Previewed Camera name at cursor position"""
    #     logger.debug("Func: currentPreviewCamera/getter")
    #
    #     return self._currentPreviewCamera
    #
    # @currentPreviewCamera.setter
    # def currentPreviewCamera(self, cameraName):
    #     """Moves the cursor to the given Preview Camera Name"""
    #     logger.debug("Func: currentPreviewCamera/setter")
    #
    #     if not self._currentSceneInfo:
    #         logger.warning(("BaseScene not Selected"))
    #         return
    #     if cameraName not in self._currentPreviewsDict.keys():
    #         logger.error(("There is no preview for that camera"))
    #         return
    #     self._currentPreviewCamera = cameraName
    #     self.cursorInfo()

    # @property
    # def baseScenesInCategory(self):
    #     return sorted(self._baseScenesInCategory.keys())

    @property
    def currentDatabasePath(self):
        # logger.debug("Func: currentDatabasePath/getter")

        if not self._currentSceneInfo:
            msg = "no current info"
            logger.error(msg)
            raise Exception([101, msg])
        if self._currentSceneInfo["SubProject"] == "None":
            subP = ""
        else:
            subP = self._currentSceneInfo["SubProject"]

        dbFile = os.path.join (self.projectDir,
                      self._pathsDict["databaseDir"],
                      self._currentSceneInfo["Category"],
                      subP, "%s.json" %self._currentSceneInfo["Name"])
        return dbFile

    def cursorInfo(self):
        """function to return cursor position info for debugging purposes"""

        logger.info("""
        Category: {0}
        SubProject: {1}
        BaseScenes Under: {2}
        Current BaseScene: {3}
        Version: {4}
        Preview: {5}
        Thumbnail: {6}
        """.format(
            self._categories[self.currentTabIndex],
            self._subProjectsList[self.currentSubIndex],
            sorted(self._baseScenesInCategory.keys()),
            self._currentBaseSceneName,
            self._currentVersionIndex,
            self._currentPreviewCamera,
            self._currentThumbFile
            ))

    def getOpenSceneInfo(self):
        """
        Collects the necessary scene info by resolving the scene name and current project
        Returns: Dictionary{jsonFile, projectPath, subProject, category, shotName} or None
        """
        # logger.debug("Func: getOpenSceneInfo")

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

            pbCategoryPath = os.path.normpath(os.path.join(self._pathsDict["previewsDir"], category))
            pbSubPath = os.path.normpath(os.path.join(pbCategoryPath, subProject))
            pbPath = os.path.normpath(os.path.join(pbSubPath, baseSceneName))

        else:
            subProject = self._subProjectsList[0]
            categoryDir = upperSceneDir
            category = upperSceneDirName
            dbPath = os.path.normpath(os.path.join(self._pathsDict["databaseDir"], category))
            pbCategoryPath = os.path.normpath(os.path.join(self._pathsDict["previewsDir"], category))
            pbPath = os.path.normpath(os.path.join(pbCategoryPath, baseSceneName))

        jsonFile = os.path.join(dbPath, "{}.json".format(baseSceneName))
        if os.path.isfile(jsonFile):
            version = (self._niceName(self._pathsDict["sceneFile"])[-4:])
            self._openSceneInfo = {
                    "jsonFile":jsonFile,
                    "projectPath":self._pathsDict["projectDir"],
                    "subProject":subProject,
                    "category":category,
                    "shotName":baseSceneName,
                    "version":version,
                    "previewPath":pbPath
                    }
            return self._openSceneInfo
        else:
            return None

    def getCategories(self):
        """Returns All Valid Categories"""
        # logger.debug("Func: getCategories")

        return self._categories

    def getSubProjects(self):
        """Returns list of sub-projects"""
        # logger.debug("Func: getSubProjects")

        return self._subProjectsList

    def getUsers(self):
        """Returns nice names of all users"""
        # logger.debug("Func: getUsers")

        return sorted(self._usersDict.keys())
    #
    def getBaseScenesInCategory(self):
        """Returns list of nice base scene names under the category at cursor position"""
        # logger.debug("Func: getBaseScenesInCategory")

        self.scanBaseScenes()
        # return sorted(self._baseScenesInCategory.keys())
        return self._baseScenesInCategory

    # def getBaseScenesInCategory(self):
    #     """Returns list of nice base scene names under the category at cursor position"""
    #     self.scanBaseScenes()
    #     return self._baseScenesInCategory

    def getVersions(self):
        """Returns Versions List of base scene at cursor position"""
        # logger.debug("Func: getVersions")

        try:
            return self._currentSceneInfo["Versions"]
        except:
            return []

    def getNotes(self):
        """returns (String) version notes on cursor position"""
        # logger.debug("Func: getNotes")

        return self._currentNotes

    def getPreviews(self):
        """returns (list) nice preview names of version on cursor position"""
        # logger.debug("Func: getPreviews")

        return sorted(self._currentPreviewsDict.keys())

    def getThumbnail(self):
        """returns (String) absolute thumbnail path of version on cursor position"""
        # logger.debug("Func: getThumbnail")

        return os.path.join(self.projectDir, self._currentThumbFile)

    # def getFavorites(self):
    #     """returns List of favorite projects"""
    #     self._bookmarksList = self.loadFavorites(self.bookmarksFile)  # not immediate
    #     return self._bookmarksList

    def createNewProject(self, projectRoot, projectName, brandName, client, settingsData=None):
        """
        Creates New Project Structure
        :param projectRoot: (String) Path to where all projects are
        :param projectName: (String) Name of the project
        :param brandName: (String) Optional. Brand name
        :param client: (String) Client Name
        :return: None
        """
        # logger.debug("Func: createNewProject")

        # resolve the project path
        resolvedPath = self._resolveProjectPath(projectRoot, projectName, brandName, client)

        # check if there is a duplicate
        if not os.path.isdir(os.path.normpath(resolvedPath)):
            os.makedirs(os.path.normpath(resolvedPath))
        else:
            msg = "Project already exists"
            logger.warning(msg)
            raise Exception ([340, msg])

        # create Directory structure:
        os.mkdir(os.path.join(resolvedPath, "_COMP"))
        # os.makedirs(os.path.join(resolvedPath, "maxScenes", "Animation"))
        # os.makedirs(os.path.join(resolvedPath, "maxScenes", "Model"))
        # os.makedirs(os.path.join(resolvedPath, "maxScenes", "Render"))
        # os.mkdir(os.path.join(resolvedPath, "_SCULPT"))
        # os.mkdir(os.path.join(resolvedPath, "_REALFLOW"))
        # os.mkdir(os.path.join(resolvedPath, "_HOUDINI"))
        os.mkdir(os.path.join(resolvedPath, "_REF"))
        # os.mkdir(os.path.join(resolvedPath, "_TRACK"))
        os.makedirs(os.path.join(resolvedPath, "_TRANSFER", "FBX"))
        os.makedirs(os.path.join(resolvedPath, "_TRANSFER", "ALEMBIC"))
        os.makedirs(os.path.join(resolvedPath, "_TRANSFER", "OBJ"))
        os.makedirs(os.path.join(resolvedPath, "_TRANSFER", "MA"))
        # os.mkdir(os.path.join(resolvedPath, "assets"))
        os.mkdir(os.path.join(resolvedPath, "cache"))
        # os.mkdir(os.path.join(resolvedPath, "clips"))
        os.mkdir(os.path.join(resolvedPath, "data"))
        os.makedirs(os.path.join(resolvedPath, "images", "_CompRenders"))
        # os.mkdir(os.path.join(resolvedPath, "movies"))
        os.mkdir(os.path.join(resolvedPath, "particles"))
        os.mkdir(os.path.join(resolvedPath, "Playblasts"))
        os.makedirs(os.path.join(resolvedPath, "renderData", "depth"))
        os.makedirs(os.path.join(resolvedPath, "renderData", "fur"))
        os.makedirs(os.path.join(resolvedPath, "renderData", "iprImages"))
        os.makedirs(os.path.join(resolvedPath, "renderData", "mentalray"))
        os.makedirs(os.path.join(resolvedPath, "renderData", "shaders"))
        os.mkdir(os.path.join(resolvedPath, "scenes"))
        os.mkdir(os.path.join(resolvedPath, "scripts"))
        os.mkdir(os.path.join(resolvedPath, "sound"))
        os.makedirs(os.path.join(resolvedPath, "sourceimages", "_FOOTAGE"))
        os.makedirs(os.path.join(resolvedPath, "sourceimages", "_HDR"))
        os.makedirs(os.path.join(resolvedPath, "smDatabase"))

        # Create project settings file
        if not settingsData:
            settingsData = {"Resolution": [1920, 1080],
                                   "FPS": 25}

        self._dumpJson(settingsData, os.path.join(resolvedPath, "smDatabase", "projectSettings.json"))


        filePath = os.path.join(resolvedPath, "workspace.mel")
        file = open(filePath, "w")

        file.write('workspace -fr "scene" "scenes";\n')
        file.write('workspace -fr "3dPaintTextures" "sourceimages/3dPaintTextures";\n')
        file.write('workspace -fr "eps" "data";\n')
        file.write('workspace -fr "mentalRay" "renderData/mentalray";\n')
        file.write('workspace -fr "OBJexport" "_TRANSFER/OBJ";\n')
        file.write('workspace -fr "mel" "scripts";\n')
        file.write('workspace -fr "particles" "particles";\n')
        file.write('workspace -fr "STEP_DC" "data";\n')
        file.write('workspace -fr "CATIAV5_DC" "data";\n')
        file.write('workspace -fr "sound" "sound";\n')
        file.write('workspace -fr "furFiles" "renderData/fur/furFiles";\n')
        file.write('workspace -fr "depth" "renderData/depth";\n')
        file.write('workspace -fr "CATIAV4_DC" "data";\n')
        file.write('workspace -fr "autoSave" "autosave";\n')
        file.write('workspace -fr "diskCache" "cache";\n')
        file.write('workspace -fr "fileCache" "";\n')
        file.write('workspace -fr "IPT_DC" "data";\n')
        file.write('workspace -fr "SW_DC" "data";\n')
        file.write('workspace -fr "DAE_FBX export" "data";\n')
        file.write('workspace -fr "Autodesk Packet File" "";\n')
        file.write('workspace -fr "DAE_FBX" "data";\n')
        file.write('workspace -fr "DXF_DCE" "";\n')
        file.write('workspace -fr "mayaAscii" "scenes";\n')
        file.write('workspace -fr "iprImages" "renderData/iprImages";\n')
        file.write('workspace -fr "move" "data";\n')
        file.write('workspace -fr "mayaBinary" "scenes";\n')
        file.write('workspace -fr "fluidCache" "cache/fluid";\n')
        file.write('workspace -fr "clips" "clips";\n')
        file.write('workspace -fr "animExport" "data";\n')
        file.write('workspace -fr "templates" "assets";\n')
        file.write('workspace -fr "DWG_DC" "data";\n')
        file.write('workspace -fr "offlineEdit" "scenes/edits";\n')
        file.write('workspace -fr "translatorData" "data";\n')
        file.write('workspace -fr "renderData" "renderData";\n')
        file.write('workspace -fr "DXF_DC" "data";\n')
        file.write('workspace -fr "SPF_DCE" "";\n')
        file.write('workspace -fr "ZPR_DCE" "";\n')
        file.write('workspace -fr "furShadowMap" "renderData/fur/furShadowMap";\n')
        file.write('workspace -fr "audio" "sound";\n')
        file.write('workspace -fr "scripts" "scripts";\n')
        file.write('workspace -fr "IV_DC" "data";\n')
        file.write('workspace -fr "studioImport" "data";\n')
        file.write('workspace -fr "STL_DCE" "";\n')
        file.write('workspace -fr "furAttrMap" "renderData/fur/furAttrMap";\n')
        file.write('workspace -fr "FBX export" "data";\n')
        file.write('workspace -fr "JT_DC" "data";\n')
        file.write('workspace -fr "sourceImages" "sourceimages";\n')
        file.write('workspace -fr "DWG_DCE" "";\n')
        file.write('workspace -fr "animImport" "data";\n')
        file.write('workspace -fr "FBX" "data";\n')
        file.write('workspace -fr "movie" "movies";\n')
        file.write('workspace -fr "Alembic" "";\n')
        file.write('workspace -fr "furImages" "renderData/fur/furImages";\n')
        file.write('workspace -fr "IGES_DC" "data";\n')
        file.write('workspace -fr "furEqualMap" "renderData/fur/furEqualMap";\n')
        file.write('workspace -fr "illustrator" "data";\n')
        file.write('workspace -fr "UG_DC" "";\n')
        file.write('workspace -fr "images" "images";\n')
        file.write('workspace -fr "SPF_DC" "data";\n')
        file.write('workspace -fr "PTC_DC" "data";\n')
        file.write('workspace -fr "OBJ" "_TRANSFER/OBJ";\n')
        file.write('workspace -fr "CSB_DC" "data";\n')
        file.write('workspace -fr "STL_DC" "data";\n')
        file.write('workspace -fr "IGES_DCE" "";\n')
        file.write('workspace -fr "shaders" "renderData/shaders";\n')
        file.write('workspace -fr "UG_DCE" "";\n')
        file.close()

        return resolvedPath

    def createSubproject(self, nameOfSubProject):
        # logger.debug("Func: createSubproject")

        if nameOfSubProject in self._subProjectsList:
            msg = "%s is already in sub-projects list" % nameOfSubProject
            logger.warning(msg)
            raise Exception([340, msg])
        self._subProjectsList.append(nameOfSubProject)
        self._saveSubprojects(self._subProjectsList)
        self.currentSubIndex = len(self._subProjectsList)-1
        return self._subProjectsList


    def showInExplorer(self, path):
        """Opens the path in Windows Explorer(Windows) or Nautilus(Linux)"""
        # logger.debug("Func: showInExplorer")

        # raise Exception (200, "cok fena exception")
        # raise RuntimeError ((0,"cok fena RuntimeError"))

        # if not path or not os.path.isdir(path):
        #     logger.error("path is not a directory path or does not exist")
        #     return
        if self.currentPlatform == "Windows":
            os.startfile(path)
        elif self.currentPlatform == "Linux":
            os.system('nautilus %s' % path)
        else:
            msg = "%s is not supported" %self.currentPlatform
            logger.warning(msg)
            raise Exception([210, msg])
            # return

    # def scanBaseScenes(self, categoryAs=None, subProjectAs=None):


    def scanBaseScenes(self, categoryAs=None, subProjectAs=None):
        """Returns the basescene database files in current category"""
        # logger.debug("Func: scanBaseScenes")

        if self.currentSubIndex >= len(self._subProjectsList):
            self.currentSubIndex = 0

        if categoryAs:
            category = categoryAs
        else:
            try:
                category = self._categories[self.currentTabIndex]
            except IndexError:
                self.currentTabIndex = 0
                category = self._categories[self.currentTabIndex]

        if subProjectAs:
            if type(subProjectAs) == int: # it index number of projects list is given, get the name from t
                subProject = self._subProjectsList[subProjectAs]
            else:
                subProject = subProjectAs
        else:
            subProject = self._subProjectsList[self.currentSubIndex]

        categoryDBpath = os.path.normpath(os.path.join(self._pathsDict["databaseDir"], category))
        self._folderCheck(categoryDBpath)
        if not (self.currentSubIndex == 0):
            try:
                categorySubDBpath = os.path.normpath(os.path.join(categoryDBpath, subProject)) # category name
            except IndexError:
                self.currentSubIndex = 0
                categorySubDBpath = os.path.normpath(os.path.join(categoryDBpath, subProject)) # category name
            self._folderCheck(categorySubDBpath)

            searchDir = categorySubDBpath
        else:
            searchDir = categoryDBpath

        self._baseScenesInCategory = {self._niceName(file):file for file in glob(os.path.join(searchDir, '*.json'))}
        # self._baseScenesInCategory = {self._niceName(file): self.filterReferenced(file) for file in glob(os.path.join(searchDir, '*.json'))}
        # self._currentBaseScenes = [os.path.join(searchDir, file) for file in os.listdir(searchDir) if file.endswith('.json')]
        return self._baseScenesInCategory # dictionary of json files

    # def filterReferenced(self, jsonFile):
    #     jInfo = self._loadJson(jsonFile)
    #     if jInfo["ReferenceFile"]:
    #         return [jsonFile, True]
    #     else:
    #         return [jsonFile, False]

    # def getProjectReport(self):
    #     # TODO This function should be re-written considering all possible softwares
    #     # TODO instead of clunking scanBaseScenes with extra arguments, do the scanning inside this function
    #     def getOldestFile(rootfolder, extension=".avi"):
    #         return min(
    #             (os.path.join(dirname, filename)
    #              for dirname, dirnames, filenames in os.walk(rootfolder)
    #              for filename in filenames
    #              if filename.endswith(extension)),
    #             key=lambda fn: os.stat(fn).st_mtime)
    #
    #     def getNewestFile(rootfolder, extension=".avi"):
    #         return max(
    #             (os.path.join(dirname, filename)
    #              for dirname, dirnames, filenames in os.walk(rootfolder)
    #              for filename in filenames
    #              if filename.endswith(extension)),
    #             key=lambda fn: os.stat(fn).st_mtime)
    #
    #     oldestFile = getOldestFile(self.scenesDir, extension=(".mb", ".ma"))
    #     pathOldestFile, nameOldestFile = os.path.split(oldestFile)
    #     oldestTimeMod = datetime.datetime.fromtimestamp(os.path.getmtime(oldestFile))
    #     newestFile = getNewestFile(self.scenesDir, extension=(".mb", ".ma"))
    #     pathNewestFile, nameNewestFile = os.path.split(oldestFile)
    #     newestTimeMod = datetime.datetime.fromtimestamp(os.path.getmtime(newestFile))
    #
    #     L1 = "Oldest Scene file: {0} - {1}".format(nameOldestFile, oldestTimeMod)
    #     L2 = "Newest Scene file: {0} - {1}".format(nameNewestFile, newestTimeMod)
    #     L3 = "Elapsed Time: {0}".format(str(newestTimeMod - oldestTimeMod))
    #     L4 = "Scene Counts:"
    #
    #     report = {}
    #     for subP in range(len(self._subProjectsList)):
    #         subReport = {}
    #         for category in self._categories:
    #             categoryItems = (self.scanBaseScenes(categoryAs=category, subProjectAs=subP))
    #             categoryItems = [x for x in categoryItems if x != []]
    #
    #             L4 = "{0}\n{1}: {2}".format(L4, category, len(categoryItems))
    #             subReport[category] = categoryItems
    #         report[self._subProjectsList[subP]] = subReport
    #
    #     report = pprint.pformat(report)
    #     now = datetime.datetime.now()
    #     filename = "summary_{0}.txt".format(now.strftime("%Y.%m.%d.%H.%M"))
    #     filePath = os.path.join(self.projectDir, filename)
    #     file = open(filePath, "w")
    #     file.write("{0}\n".format(L1))
    #     file.write("{0}\n".format(L2))
    #     file.write("{0}\n".format(L3))
    #     file.write("{0}\n".format(L4))
    #     file.write((report))
    #
    #     file.close()
    #     logger.info("Report has been logged => %s" %filePath)
    #     return report





    def addNote(self, note):
        """Adds a note to the version at current position"""
        # logger.debug("Func: addNote")

        # assert (not self._currentBaseSceneName), [101, "No Base Scene file selected"]
        # assert (self._currentVersionIndex == -1), [101, "No Version selected"]

        if not self._currentBaseSceneName:
            logger.warning("No Base Scene file selected")
            return
        if self._currentVersionIndex == -1:
            logger.warning("No Version selected")
            return
        now = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M")
        self._currentNotes = "%s\n[%s] on %s\n%s\n" % (self._currentNotes, self.currentUser, now, note)
        self._currentSceneInfo["Versions"][self._currentVersionIndex-1][1] = self._currentNotes
        self._dumpJson(self._currentSceneInfo, self._baseScenesInCategory[self._currentBaseSceneName])

    def addUser(self, fullName, initials):
        # logger.debug("Func: addUser")

        # old Name
        currentDB = self._loadUsers()
        # currentDB, dbFile = self.initUsers()
        initialsList = currentDB.values()
        if initials in initialsList:
            msg="Initials are in use"
            raise Exception([340, msg])
            # return -1, msg
        currentDB[fullName] = initials
        self._dumpJson(currentDB, self._pathsDict["usersFile"])
        self._usersDict = currentDB
        return None, None

    def removeUser(self, fullName):
        # logger.debug("Func: removeUser")

        # old Name removeUser
        currentDB = self._loadUsers()
        del currentDB[fullName]
        self._dumpJson(currentDB, self._pathsDict["usersFile"])
        self._usersDict = currentDB
        return None, None

    def addCategory(self, categoryName):
        curCategories = self._loadCategories()
        if categoryName in curCategories:
            msg = "Duplicate Category names are not allowed"
            logger.warning(msg)
            raise Exception([340, msg])
            # return -1
        curCategories.append(categoryName)
        self._dumpJson(curCategories, self._pathsDict["categoriesFile"])
        self._categories = curCategories
        return


    def removeCategory(self, categoryName):
        # TODO // TEST IT
        curCategories = self._loadCategories()
        if len(curCategories) == 1:
            # Last category cannot be removed
            msg = "Last Category cannot be removed"
            logger.warning(msg)
            raise Exception([360, msg])

        if categoryName in curCategories:
            # Check if category about to be removed is empty
            for subP in self._subProjectsList:
                baseScenes = self.scanBaseScenes(categoryAs=categoryName, subProjectAs=subP)
                if baseScenes:
                    # if it in not empty abort
                    msg = "Category is not empty. Aborting..."
                    logger.warning(msg)
                    raise Exception([360, msg])
                    # return -1

            # remove the empty category
            curCategories.remove(categoryName)
            self._dumpJson(curCategories, self._pathsDict["categoriesFile"])
            self._categories = curCategories
            return

        else:
            msg = "Specified Category does not exist"
            logger.warning(msg)
            raise Exception([101, msg])
            # return -1

        # try:
        #     curCategories.remove(categoryName)
        #     self._dumpJson(curCategories, self._pathsDict["categoriesFile"])
        #     self._categories = curCategories
        #     return
        # except ValueError:
        #     logger.warning("Specified Category does not exist")



    def playPreview(self, camera):
        """Runs the playblast at cursor position"""
        # logger.debug("Func: playPreview")

        # absPath = os.path.join(self.projectDir, self._currentPreviewsDict[self._currentPreviewCamera])
        absPath = os.path.join(self.projectDir, self._currentPreviewsDict[camera])
        if self.currentPlatform == "Windows":
            try:
                os.startfile(absPath)
            except WindowsError:
                return -1, ["Cannot Find Playblast", "Playblast File is missing", "Do you want to remove it from the Database?"]
        # TODO something to play the file in linux
        return

    def removePreview(self):
        # logger.debug("Func: removePreview")

        if self._currentPreviewCamera:
            previewName = self._currentPreviewCamera
            previewFile = self._currentPreviewsDict[self._currentPreviewCamera]
            os.remove(os.path.join(self.projectDir, self._currentPreviewsDict[self._currentPreviewCamera]))
            del self._currentPreviewsDict[self._currentPreviewCamera]
            self._currentSceneInfo["Versions"][self._currentVersionIndex-1][4] = self._currentPreviewsDict
            self._dumpJson(self._currentSceneInfo, self._baseScenesInCategory[self.currentBaseSceneName])
            logger.info("""Preview file deleted and removed from database successfully 
            Preview Name: {0}
            Path: {1}
                        """.format(previewName, previewFile))

    def deleteBasescene(self, databaseFile):
        # logger.debug("Func: deleteBasescene")

        #ADMIN ACCESS
        jsonInfo = self._loadJson(databaseFile)
        if jsonInfo == -2:
            return -2
        # delete all version files
        for s in jsonInfo["Versions"]:
            try:
                os.remove(os.path.join(self.projectDir, s[0]))
            except:
                msg = "Cannot delete scene version:%s" % (s[0])
                logger.warning(msg)
                raise Exception([203, msg])
                # pass

        # delete reference file
        if jsonInfo["ReferenceFile"]:
            try:
                os.remove(os.path.join(self.projectDir, jsonInfo["ReferenceFile"]))
            except:
                msg = "Cannot delete reference file %s" % (jsonInfo["ReferenceFile"])
                logger.warning(msg)
                raise Exception([203, msg])
                # pass

        # delete base scene directory
        scene_path = os.path.join(self.projectDir, jsonInfo["Path"])
        try:
            os.rmdir(scene_path)
        except:
            msg = "Cannot delete scene path %s" % (scene_path)
            logger.warning(msg)
            raise Exception([203, msg])
            # pass
        # delete json database file
        try:
            os.remove(os.path.join(self.projectDir, databaseFile))
        except:
            msg = "Cannot delete scene path %s" % (databaseFile)
            logger.warning(msg)
            raise Exception([203, msg])
            # pass
        logger.debug("all database entries and version files of %s deleted" %databaseFile)

    def deleteReference(self, databaseFile):
        # logger.debug("Func: deleteReference")

        #ADMIN ACCESS
        jsonInfo = self._loadJson(databaseFile)
        if jsonInfo == -2:
            return -2

        if jsonInfo["ReferenceFile"]:
            try:
                os.remove(os.path.join(self.projectDir, jsonInfo["ReferenceFile"]))
                jsonInfo["ReferenceFile"] = None
                jsonInfo["ReferencedVersion"] = None
                self._dumpJson(jsonInfo, databaseFile)
            except:
                msg = "Cannot delete reference file %s" % (jsonInfo["ReferenceFile"])
                logger.warning(msg)
                raise Exception([203, msg])
                pass

    def makeReference(self):
        """Creates a Reference copy from the base scene version at cursor position"""
        # logger.debug("Func: makeReference")

        if self._currentVersionIndex == -1:
            msg = "Cursor is not on a Base Scene Version. Cancelling"
            logger.warning(msg)
            raise Exception([101, msg])
            # return

        absVersionFile = os.path.join(self.projectDir, self._currentSceneInfo["Versions"][self._currentVersionIndex-1][0])
        name = os.path.split(absVersionFile)[1]
        filename, extension = os.path.splitext(name)
        referenceName = "{0}_{1}_forReference".format(self._currentSceneInfo["Name"], self._currentSceneInfo["Category"])
        relReferenceFile = os.path.join(self._currentSceneInfo["Path"], "{0}{1}".format(referenceName, extension))
        absReferenceFile = os.path.join(self.projectDir, relReferenceFile)
        shutil.copyfile(absVersionFile, absReferenceFile)
        self._currentSceneInfo["ReferenceFile"] = relReferenceFile
        # SET the referenced version as the 'VISUAL INDEX NUMBER' starting from 1
        self._currentSceneInfo["ReferencedVersion"] = self._currentVersionIndex

        self._dumpJson(self._currentSceneInfo, self._baseScenesInCategory[self.currentBaseSceneName])


    def checkReference(self, jsonFile, deepCheck=False):
        # logger.debug("Func: checkReference")

        sceneInfo = self._loadJson(jsonFile)
        # assert (sceneInfo == -2)
        if sceneInfo == -2:
            # raise AssertionError(200, "cok fena exception")
            return -2 # Corrupted database file

        if sceneInfo["ReferenceFile"]:
            relVersionFile = sceneInfo["Versions"][sceneInfo["ReferencedVersion"] - 1][0]
            absVersionFile = os.path.join(self.projectDir, relVersionFile)
            relRefFile = sceneInfo["ReferenceFile"]
            absRefFile = os.path.join(self.projectDir, relRefFile)

            if not os.path.isfile(absRefFile):
                logger.info("CODE RED: Reference File does not exist")
                return -1 # code red
            else:
                if deepCheck:
                    if filecmp.cmp(absVersionFile, absRefFile):
                        logger.info("CODE GREEN: Everything is OK")
                        return 1 # code Green
                    else:
                        logger.info("CODE RED: Checksum mismatch with reference file")
                        return -1 # code red
                else:
                    logger.info("CODE GREEN: Everything is OK")
                    return 1 # code Green
        else:
            logger.info("CODE YELLOW: File does not have a reference copy")
            return 0 # code yellow

    def _checkRequirements(self):
        """
        Checks the requirements for platform and administrator rights. Returns [None, None] if passes both
        Returns: (List) [ErrorCode, ErrorMessage]

        """
        # logger.debug("Func: _checkRequirements")

        ## check platform
        currentOs = platform.system()
        if currentOs != "Linux" and currentOs != "Windows":
            return -1, ["OS Error", "Operating System is not supported",
                        "Scene Manager only supports Windows and Linux Operating Systems"]
        ## check admin rights
        try:
            is_admin = os.getuid() == 0
        except AttributeError:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        if not is_admin:
            return -1, ["Admin Rights", "You dont have the administrator rights",
                        "You need to run the Software as administrator to work with Scene Manager"]
        return None, None

    def _folderCheck(self, folder):
        # logger.debug("Func: _folderCheck")

        if not os.path.isdir(os.path.normpath(folder)):
            os.makedirs(os.path.normpath(folder))

    # def _nameCheck(self, text):
    #     """Checks the text for illegal characters, Returns:  corrected Text or -1 for Error """
    #     text = text.replace("|", "__")
    #     if re.match("^[A-Za-z0-9_-]*$", text):
    #         if text == "":
    #             return -1
    #         text = text.replace(" ", "_")
    #         # text = text.replace("|", "__")
    #         return text
    #     else:
    #         return -1

    def _nameCheck(self, text, allowSpaces=False):
        """Checks the text for illegal characters, Returns:  corrected Text or -1 for Error """
        # logger.debug("Func: _nameCheck")

        if allowSpaces:
            pattern = "^[ A-Za-z0-9_-]*$"
        else:
            pattern = "^[A-Za-z0-9_-]*$"

        if re.match(pattern, text):
            return True
        else:
            return False


    def _niceName(self, path):
        """Gets the base name of the given filename"""
        # logger.debug("Func: _niceName")

        basename = os.path.split(path)[1]
        return os.path.splitext(basename)[0]

    def _resolveProjectPath(self, projectRoot, projectName, brandName, client):
        # logger.debug("Func: _resolveProjectPath")

        if projectName == "" or client == "" or projectRoot == "":
            msg = ("Fill the mandatory fields")
            logger.warning(msg)
            raise Exception([341, msg])
            # return -1, msg
        projectDate = datetime.datetime.now().strftime("%y%m%d")

        if brandName:
            brandName = "%s_" % brandName
        else:
            brandName = ""
        fullName = "{0}{1}_{2}_{3}".format(brandName, projectName, client, projectDate)
        fullPath = os.path.join(os.path.normpath(str(projectRoot)), fullName)
        return fullPath

    ## Database loading / saving functions
    ## -----------------------------

    def _loadJson(self, file):
        """Loads the given json file"""
        # raise Exception((200, "ASSDFSDFSD"))
        # logger.debug("Func: _loadJson")

        if os.path.isfile(file):
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    return data
            except ValueError:
                msg = "Corrupted JSON file => %s" % file
                logger.error(msg)
                # raise Exception(200, "cok fena exception")
                return -2 # code for corrupted json file
        else:
            return None

    def _dumpJson(self, data, file):
        """Saves the data to the json file"""
        # logger.debug("Func: _dumpJson %s %s" %(data, file))


        with open(file, "w") as f:
            json.dump(data, f, indent=4)

    def _loadProjectSettings(self):
        """Loads Project Settings from file"""
        if not os.path.isdir(self._pathsDict["projectSettingsFile"]):
            projectSettingsDB = {"Resolution": [1920, 1080],
                                   "FPS": 25}
            self._dumpJson(projectSettingsDB, self._pathsDict["projectSettingsFile"])
            return projectSettingsDB
        else:
            projectSettingsDB = self._loadJson(self._pathsDict["projectSettingsFile"])
            if projectSettingsDB== -2:
                return -2
            return projectSettingsDB

    def _saveProjectSettings(self, data):
        try:
            self._dumpJson(data, self._pathsDict["projectSettingsFile"])
            msg = ""
            return 0, msg
        except:
            msg = "Cannot save current settings"
            return -1, msg

    def _loadUsers(self):
        """Load Users from file"""
        # logger.debug("Func: _loadUsers")

        # old Name
        if not os.path.isfile(self._pathsDict["usersFile"]):
            userDB = {"Generic": "gn"}
            self._dumpJson(userDB, self._pathsDict["usersFile"])
            return userDB
        else:
            userDB = self._loadJson(self._pathsDict["usersFile"])
            if userDB == -2:
                return -2
            return userDB


    def _loadFavorites(self):
        """Loads Bookmarked projects"""
        # logger.debug("Func: _loadFavorites")

        if os.path.isfile(self._pathsDict["bookmarksFile"]):
            bookmarksData = self._loadJson(self._pathsDict["bookmarksFile"])
            if bookmarksData == -2:
                return -2
        else:
            bookmarksData = []
            self._dumpJson(bookmarksData, self._pathsDict["bookmarksFile"])
        return bookmarksData

    def _addToFavorites(self, shortName, absPath):
        # logger.debug("Func: _addToFavorites")

        # old Name userFavoritesAdd
        bookmarksData = self._loadFavorites()
        bookmarksData.append([shortName, absPath])
        self._dumpJson(bookmarksData, self._pathsDict["bookmarksFile"])
        return bookmarksData

    def _removeFromFavorites(self, index):
        # logger.debug("Func: _removeFromFavorites")

        # old Name userFavoritesRemove
        bookmarksData = self._loadFavorites()
        del bookmarksData[index]
        self._dumpJson(bookmarksData, self._pathsDict["bookmarksFile"])
        return bookmarksData

    def _loadCategories(self):
        """Load Categories from file"""
        # logger.debug("Func: _loadCategories")

        if os.path.isfile(self._pathsDict["categoriesFile"]):
            categoriesData = self._loadJson(self._pathsDict["categoriesFile"])
            if categoriesData == -2:
                return -2
        else:
            categoriesData = ["Model", "Shading", "Rig", "Layout", "Animation", "Render", "Other"]
            self._dumpJson(categoriesData, self._pathsDict["categoriesFile"])
        return categoriesData

    def _loadSceneInfo(self):
        """Returns scene info of base scene at cursor position"""
        # logger.debug("Func: _loadSceneInfo")

        sceneInfo = self._loadJson(self._baseScenesInCategory[self._currentBaseSceneName])
        if sceneInfo == -2:
            return -2
        return sceneInfo

    def _loadUserPrefs(self):
        """Load Last CategoryIndex, SubProject Index, User name and Access mode from file as dictionary"""
        # logger.debug("Func: _loadUserPrefs")

        if os.path.isfile(self._pathsDict["currentsFile"]):
            settingsData = self._loadJson(self._pathsDict["currentsFile"])
            if settingsData == -2:
                return -2
        else:
            settingsData = {"currentTabIndex": 0, "currentSubIndex": 0, "currentUser": self._usersDict.keys()[0],
                            "currentMode": False}
            self._dumpJson(settingsData, self._pathsDict["currentsFile"])
        return settingsData

    def _saveUserPrefs(self, settingsData):
        """Save Last CategoryIndex, SubProject Index, User name and Access mode to file as dictionary"""
        # logger.debug("Func: _saveUserPrefs")

        try:
            self._dumpJson(settingsData, self._pathsDict["currentsFile"])
            msg = ""
            return 0, msg
        except:
            msg = "Cannot save current settings"
            return -1, msg

    def _loadSubprojects(self):
        """Loads Subprojects of current project"""
        # logger.debug("Func: _loadSubprojects")

        if not os.path.isfile(self._pathsDict["subprojectsFile"]):
            data = ["None"]
            self._dumpJson(data, self._pathsDict["subprojectsFile"])
        else:
            data = self._loadJson(self._pathsDict["subprojectsFile"])
            if data == -2:
                return -2
        return data

    def _saveSubprojects(self, subprojectsList):
        """Save Subprojects to the file"""
        # logger.debug("Func: _saveSubprojects")

        self._dumpJson(subprojectsList, self._pathsDict["subprojectsFile"])

    def _loadProjects(self):
        """Loads Projects dictionary for each software"""
        # logger.debug("Func: _loadProjects")

        if not os.path.isfile(self._pathsDict["projectsFile"]):
            return
        else:
            projectsData = self._loadJson(self._pathsDict["projectsFile"])
            if projectsData == -2:
                return -2
        return projectsData

    def _saveProjects(self, data):
        """Saves the current project data to the file"""
        # logger.debug("Func: _saveProjects %s")

        self._dumpJson(data, self._pathsDict["projectsFile"])

    def _loadPBSettings(self):
        # logger.debug("Func: _loadPBSettings")

        # old Name getPBsettings

        # pbSettingsFile = os.path.normpath(os.path.join(self.project_Path, "Playblasts", "PBsettings.json"))

        if not os.path.isfile(self._pathsDict["pbSettingsFile"]):
            defaultSettings = {"Resolution": (1280, 720),  ## done
                               "Format": 'avi',  ## done
                               "Codec": 'IYUV codec',  ## done
                               "Percent": 100,  ## done
                               "Quality": 100,  ## done
                               "ShowFrameNumber": True,
                               "ShowSceneName": False,
                               "ShowCategory": False,
                               "ShowFrameRange": True,
                               "ShowFPS": True,
                               "PolygonOnly": True,  ## done
                               "ShowGrid": False,  ## done
                               "ClearSelection": True,  ## done
                               "DisplayTextures": True,  ## done
                               "WireOnShaded": False,
                               "UseDefaultMaterial": False,
                               }
            self._dumpJson(defaultSettings, self._pathsDict["pbSettingsFile"])
            return defaultSettings
        else:
            pbSettings = self._loadJson(self._pathsDict["pbSettingsFile"])
            if pbSettings == -2:
                return -2
            return pbSettings

    def _savePBSettings(self, pbSettings):
        # logger.debug("Func: _savePBSettings")

        # old Name setPBsettings

        self._dumpJson(pbSettings, self._pathsDict["pbSettingsFile"])
        return










