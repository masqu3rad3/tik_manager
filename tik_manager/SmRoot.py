
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



class RootManager(object):
    def __init__(self):
        super(RootManager, self).__init__()

        # self.database = db.SmDatabase()
        # self.validCategories = ["Model", "Shading", "Rig", "Layout", "Animation", "Render", "Other"]

        self.currentPlatform = platform.system()
        self._pathsDict={}
        # self.padding = 3


    def backwardcompatibility(self):
        """
        This function checks for the old database structure and creates a copy with the new structure
        :return: None
        """

        def recursive_overwrite(src, dest, ignore=None):
            if os.path.isdir(src):
                if not os.path.isdir(dest):
                    os.makedirs(dest)
                files = os.listdir(src)
                if ignore is not None:
                    ignored = ignore(src, files)
                else:
                    ignored = set()
                for f in files:
                    if f not in ignored:
                        recursive_overwrite(os.path.join(src, f),
                                            os.path.join(dest, f),
                                            ignore)
            else:
                shutil.copyfile(src, dest)

        old_dbDir = os.path.normpath(os.path.join(self._pathsDict["projectDir"], "data", "SMdata"))
        bck_dbDir = os.path.normpath(os.path.join(self._pathsDict["projectDir"], "data", "SMdata_oldVersion"))
        new_dbDir = self._pathsDict["databaseDir"]
        if os.path.isdir(bck_dbDir):
            logger.info("Old database backuped before. Returning without doing any modification")
            return
        if os.path.isdir(old_dbDir):

            recursive_overwrite(old_dbDir, new_dbDir)
            logger.info("All old database contents copied to the new structure folder => %s" % self._pathsDict["databaseDir"])

            oldCategories = ["Model", "Shading", "Rig", "Layout", "Animation", "Render", "Other"]
            for category in oldCategories:
                categoryDBpath = os.path.normpath(os.path.join(new_dbDir, category))
                if os.path.isdir(categoryDBpath):
                    jsonFiles = [y for x in os.walk(categoryDBpath) for y in glob(os.path.join(x[0], '*.json'))]
                    for file in jsonFiles:
                        fileData = self._loadJson(file)
                        # figure out the subproject
                        path = fileData["Path"]
                        name = fileData["Name"]
                        cate = fileData["Category"]
                        parts = path.split("\\")
                        diff = list(set(parts) - set([name, cate, "scenes"]))
                        if diff:
                            fileData["SubProject"] = diff[0]
                        else:
                            fileData["SubProject"] = "None"
                        for vers in fileData["Versions"]:

                            #if there is no thumbnail column, skip
                            try:
                                vers[5] = vers[5].replace("data\\SMdata", "smDatabase\\mayaDB") # relative thumbnail path
                            except IndexError:
                                vers.append("") ## create the fifth column

                            for key in vers[4].keys(): # Playblast dictionary
                                vers[4][key] = vers[4][key].replace("data\\SMdata", "smDatabase\\mayaDB")
                        self._dumpJson(fileData, file)
            logger.info("Database preview and thumbnail paths are fixed")
            try:
                os.rename(old_dbDir, bck_dbDir)
                logger.info("Old database folder renamed to 'SMdata_oldVersion'")
            except WindowsError:
                logger.warning("Cannot rename the old database folder because of windows bullshit")


    def init_paths(self):
        # This function should be overridden for each software
        # all paths in here must be absolute paths
        self._pathsDict["userSettingsDir"] = os.path.join(os.path.expanduser("~"), "SceneManager")
        self._folderCheck(self._pathsDict["userSettingsDir"])

        self._pathsDict["bookmarksFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], "smBookmarks.json"))
        self._pathsDict["currentsFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], "smCurrents.json"))
        self._pathsDict["projectsFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], "smProjects.json"))

        self._pathsDict["projectDir"] = self.getProjectDir()
        self._pathsDict["sceneFile"] = self.getSceneFile()
        _softwarePathsDict = self.getSoftwarePaths()
        if self._pathsDict["projectDir"] == -1 or self._pathsDict["sceneFile"] == -1 or _softwarePathsDict == -1:
            logger.error("The following functions must be overridden in inherited class:\n'getSoftware'\n'getProjectDir'\n'getSceneFile'")
            raise Exception()

        self._pathsDict["masterDir"] = os.path.normpath(os.path.join(self._pathsDict["projectDir"], "smDatabase"))
        self._folderCheck(self._pathsDict["masterDir"])

        self._pathsDict["databaseDir"] = os.path.normpath(os.path.join(self._pathsDict["masterDir"], _softwarePathsDict["databaseDir"]))
        self._folderCheck(self._pathsDict["databaseDir"])

        self._pathsDict["scenesDir"] = os.path.normpath(os.path.join(self._pathsDict["projectDir"], _softwarePathsDict["scenesDir"]))
        self._folderCheck(self._pathsDict["scenesDir"])

        self._pathsDict["subprojectsFile"] = os.path.normpath(os.path.join(self._pathsDict["databaseDir"], "subPdata.json"))
        self._pathsDict["categoriesFile"] = os.path.normpath(os.path.join(self._pathsDict["databaseDir"], "categories.json"))

        self._pathsDict["previewsDir"] = os.path.normpath(os.path.join(self._pathsDict["projectDir"], "Playblasts")) # dont change
        self._folderCheck(self._pathsDict["previewsDir"])

        self._pathsDict["pbSettingsFile"] = os.path.normpath(os.path.join(self._pathsDict["previewsDir"], _softwarePathsDict["pbSettingsFile"]))

        self._pathsDict["generalSettingsDir"] = os.path.dirname(os.path.abspath(__file__))

        self._pathsDict["usersFile"] = os.path.normpath(os.path.join(self._pathsDict["generalSettingsDir"], "sceneManagerUsers.json"))

    def getSoftwarePaths(self):
        """This function must be overriden to return the software currently working on"""
        # This function should return a dictionary which includes string values for:
        # databaseDir, scenesDir, pbSettingsFile keys. Software specific paths will be resolved with these strings
        return -1

    def getProjectDir(self):
        """This function must be overriden to return the project directory of running software"""
        return -1

    def getSceneFile(self):
        """This function must be overriden to return the full scene path ('' for unsaved) of current scene"""
        return -1

    def init_database(self):
        # self.currentPlatform = platform.system()
        self._categories = self._loadCategories()
        self._usersDict = self._loadUsers()
        self._currentsDict = self._loadUserPrefs()
        self._subProjectsList = self._loadSubprojects()
        # self._pbSettingsDict = self.loadPBSettings(self.pbSettingsFile) # not immediate
        # self._bookmarksList = self.loadFavorites(self.bookmarksFile) # not immediate

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

        self.scanBaseScenes()

    def _setCurrents(self, att, newdata):
        """Sets the database stored cursor positions and saves them to the database file"""
        self._currentsDict[att] = newdata
        self._saveUserPrefs(self._currentsDict)

    @property
    def projectDir(self):
        """Returns Current Project Directory"""
        return self._pathsDict["projectDir"]

    @property
    def subProject(self):
        """Returns the name of the current sub-project"""
        return self._subProjectsList[self.currentSubIndex]

    # @property
    # def baseScene(self):
    #     """Returns the name of the Base Scene at cursor position"""
    #     baseSceneDir = os.path.abspath(os.path.join(self._pathsDict["sceneFile"], os.pardir))
    #     return os.path.basename(baseSceneDir)

    @property
    def currentTabIndex(self):
        """Returns the Category index at cursor position"""
        return self._currentsDict["currentTabIndex"]

    @currentTabIndex.setter
    def currentTabIndex(self, indexData):
        """Moves the cursor to the given category index"""
        if not 0 <= indexData < len(self._categories):
            logger.error(("out of range!"))
            return
        if indexData == self.currentTabIndex:
            logger.info("Cursor is already at %s" %indexData)
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
        return self._currentsDict["currentSubIndex"]

    @currentSubIndex.setter
    def currentSubIndex(self, indexData):
        """Moves the cursor to the given sub-project index"""
        if not 0 <= indexData < len(self._subProjectsList):
            logger.error(("entered index is out of range!"))
            return
        if indexData == self.currentSubIndex:
            logger.info("Cursor is already at %s" %indexData)
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
        return self._currentsDict["currentUser"]

    @currentUser.setter
    def currentUser(self, name):
        """Sets the current user"""
        if name not in self._usersDict.keys():
            logger.error(("%s is not a user!" %name))
            return
        self._setCurrents("currentUser", name)

    @property
    def currentMode(self):
        """Returns the current access mode (Load or Reference)"""
        return self._currentsDict["currentMode"]

    @currentMode.setter
    def currentMode(self, state):
        """Sets the current access mode 0 == Load, 1 == Reference"""
        if not type(state) is bool:
            if bool is 0:
                state = False
            elif bool is 1:
                state = True
            else:
                logger.error("only boolean or 0-1 accepted, entered %s" %state)
                return
        self._setCurrents("currentMode", state)

    @property
    def currentBaseSceneName(self):
        """Returns current Base Scene Name at cursor position"""
        return self._currentBaseSceneName

    @currentBaseSceneName.setter
    def currentBaseSceneName(self, sceneName):
        """Moves the cursor to the given base scene name"""
        if sceneName not in self._baseScenesInCategory.keys():
            # self._currentVersionIndex = -1
            # self._currentThumbFile = ""
            # self._currentNotes = ""
            self.currentVersionIndex = -1
            logger.debug("There is no scene called %s in current category" %sceneName)
            return

        self._currentBaseSceneName = sceneName
        self._currentSceneInfo = self._loadSceneInfo()
        # if not sceneName:
        #     self._currentVersionIndex = -1

        if self._currentSceneInfo["ReferencedVersion"]:
            self.currentVersionIndex = self._currentSceneInfo["ReferencedVersion"]
        else:
            self.currentVersionIndex = len(self._currentSceneInfo["Versions"])

        self.cursorInfo()
        # self._currentPreviewIndex = 0

    @property
    def currentBaseScenePath(self):
        """Returns absolute path of Base Scene at cursor position"""
        return os.path.join(self.projectDir, self._currentSceneInfo["Path"])

    @property
    def currentPreviewPath(self):
        """Returns absolute path of preview folder of the Base scene at cursor position"""
        # TODO // CONTINUE
        # return self._

    @property
    def currentVersionIndex(self):
        """Returns current Version index at cursor position"""
        return self._currentVersionIndex

    @currentVersionIndex.setter
    def currentVersionIndex(self, indexData):
        """Moves the cursor to given Version index"""
        logger.warning(indexData)
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
            logger.error(("out of range! %s" %indexData))
            return
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

    @property
    def currentPreviewCamera(self):
        """Returns current Previewed Camera name at cursor position"""
        return self._currentPreviewCamera

    @currentPreviewCamera.setter
    def currentPreviewCamera(self, cameraName):
        """Moves the cursor to the given Preview Camera Name"""
        if not self._currentSceneInfo:
            logger.warning(("BaseScene not Selected"))
            return
        if cameraName not in self._currentPreviewsDict.keys():
            logger.error(("There is no preview for that camera"))
            return
        self._currentPreviewCamera = cameraName
        self.cursorInfo()

    # @property
    # def baseScenesInCategory(self):
    #     return sorted(self._baseScenesInCategory.keys())

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
            return {"jsonFile":jsonFile,
                    "projectPath":self._pathsDict["projectDir"],
                    "subProject":subProject,
                    "category":category,
                    "shotName":baseSceneName,
                    "version":version,
                    "previewPath":pbPath
                    }
        else:
            return None

    def getCategories(self):
        """Returns All Valid Categories"""
        return self._categories

    def getSubProjects(self):
        """Returns list of sub-projects"""
        return self._subProjectsList

    def getUsers(self):
        """Returns nice names of all users"""
        return sorted(self._usersDict.keys())
    #
    def getBaseScenesInCategory(self):
        """Returns list of nice base scene names under the category at cursor position"""
        self.scanBaseScenes()
        # return sorted(self._baseScenesInCategory.keys())
        return self._baseScenesInCategory

    # def getBaseScenesInCategory(self):
    #     """Returns list of nice base scene names under the category at cursor position"""
    #     self.scanBaseScenes()
    #     return self._baseScenesInCategory

    def getVersions(self):
        """Returns Versions List of base scene at cursor position"""
        try:
            return self._currentSceneInfo["Versions"]
        except KeyError:
            return []

    def getNotes(self):
        """returns (String) version notes on cursor position"""
        return self._currentNotes

    def getPreviews(self):
        """returns (list) nice preview names of version on cursor position"""
        return sorted(self._currentPreviewsDict.keys())

    def getThumbnail(self):
        """returns (String) absolute thumbnail path of version on cursor position"""
        return os.path.join(self.projectDir, self._currentThumbFile)





    def projectChanged(self):
        pass
        # update Project
        # update SubProject
        # update Category
        # get scenes in category
        # set scene index to -1




    def createNewProject(self, projectRoot, projectName, brandName, client):
        """
        Creates New Project Structure
        :param projectRoot: (String) Path to where all projects are
        :param projectName: (String) Name of the project
        :param brandName: (String) Optional. Brand name
        :param client: (String) Client Name
        :return: None
        """
        # resolve the project path
        resolvedPath = self._resolveProjectPath(projectRoot, projectName, brandName, client)

        # check if there is a duplicate
        if not os.path.isdir(os.path.normpath(resolvedPath)):
            os.makedirs(os.path.normpath(resolvedPath))
        else:
            logger.warning("Project already exists")
            return

        # create Directory structure:
        os.mkdir(os.path.join(resolvedPath, "_COMP"))
        os.makedirs(os.path.join(resolvedPath, "maxScenes", "Animation"))
        os.makedirs(os.path.join(resolvedPath, "maxScenes", "Model"))
        os.makedirs(os.path.join(resolvedPath, "maxScenes", "Render"))
        os.mkdir(os.path.join(resolvedPath, "_SCULPT"))
        os.mkdir(os.path.join(resolvedPath, "_REALFLOW"))
        os.mkdir(os.path.join(resolvedPath, "_HOUDINI"))
        os.mkdir(os.path.join(resolvedPath, "_REF"))
        os.mkdir(os.path.join(resolvedPath, "_TRACK"))
        os.makedirs(os.path.join(resolvedPath, "_TRANSFER", "FBX"))
        os.makedirs(os.path.join(resolvedPath, "_TRANSFER", "ALEMBIC"))
        os.makedirs(os.path.join(resolvedPath, "_TRANSFER", "OBJ"))
        os.makedirs(os.path.join(resolvedPath, "_TRANSFER", "MA"))
        os.mkdir(os.path.join(resolvedPath, "assets"))
        os.mkdir(os.path.join(resolvedPath, "cache"))
        os.mkdir(os.path.join(resolvedPath, "clips"))
        os.mkdir(os.path.join(resolvedPath, "data"))
        os.makedirs(os.path.join(resolvedPath, "images", "_CompRenders"))
        os.mkdir(os.path.join(resolvedPath, "movies"))
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

    def createSubproject(self, nameOfSubProject):
        if nameOfSubProject in self._subProjectsList:
            logger.warning("%s is already in sub-projects list" % nameOfSubProject)
            return self._subProjectsList
        self._subProjectsList.append(nameOfSubProject)
        self._saveSubprojects(self._subProjectsList)
        self.currentSubIndex = len(self._subProjectsList)-1
        return self._subProjectsList
        ## What we need:
        # PATH(abs) software database (jsonPath)
        # PATH(s)(abs, list) sub-projects

    def showInExplorer(self, path):
        """Opens the path in Windows Explorer(Windows) or Nautilus(Linux)"""
        if not os.path.isdir(path):
            logger.error("path is not a directory path or does not exist")
            return
        if self.currentPlatform == "Windows":
            os.startfile(path)
        elif self.currentPlatform == "Linux":
            os.system('nautilus %s' % path)
        else:
            logger.warning("OS is not supported")
            return

    # def scanBaseScenes(self, categoryAs=None, subProjectAs=None):


    def scanBaseScenes(self, categoryAs=None, subProjectAs=None):
        """Returns the basescene database files in current category"""
        if self.currentSubIndex >= len(self._subProjectsList):
            self.currentSubIndex = 0

        if categoryAs:
            category = categoryAs
        else:
            category = self._categories[self.currentTabIndex]

        if subProjectAs:
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

    def filterReferenced(self, jsonFile):
        jInfo = self._loadJson(jsonFile)
        if jInfo["ReferenceFile"]:
            return [jsonFile, True]
        else:
            return [jsonFile, False]

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

    def playPreview(self):
        """Runs the playblast at cursor position"""
        absPath = os.path.join(self.projectDir, self._currentPreviewsDict[self._currentPreviewCamera])
        if self.currentPlatform == "Windows":
            try:
                os.startfile(absPath)
            except WindowsError:
                return -1, ["Cannot Find Playblast", "Playblast File is missing", "Do you want to remove it from the Database?"]
        # TODO something to play the file in linux
        return

    def removePreview(self):
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
        # TODO TEST IT
        #ADMIN ACCESS
        jsonInfo = self._loadJson(databaseFile)
        # delete all version files
        for s in jsonInfo["Versions"]:
            try:
                os.remove(os.path.join(self.projectDir, s[0]))
            except:
                logger.warning("Cannot delete scene version:%s" % (s[0]))
                pass

        # delete reference file
        if jsonInfo["ReferenceFile"]:
            try:
                os.remove(os.path.join(self.projectDir, jsonInfo["ReferenceFile"]))
            except:
                logger.warning("Cannot delete reference file %s" % (jsonInfo["ReferenceFile"]))
                pass

        # delete base scene directory
        scene_path = os.path.join(self.projectDir, jsonInfo["Path"])
        try:
            os.rmdir(scene_path)
        except:
            logger.warning("Cannot delete scene path %s" % (scene_path))
            pass
        # delete json database file
        try:
            os.remove(os.path.join(self.projectDir, databaseFile))
        except:
            logger.warning("Cannot delete scene path %s" % (databaseFile))
            pass
        logger.debug("all database entries and version files of %s deleted" %databaseFile)

    def deleteReference(self, databaseFile):
        # TODO // TEST IT
        #ADMIN ACCESS
        jsonInfo = self._loadJson(databaseFile)

        if jsonInfo["ReferenceFile"]:
            try:
                os.remove(os.path.join(self.projectDir, jsonInfo["ReferenceFile"]))
                jsonInfo["ReferenceFile"] = None
                jsonInfo["ReferencedVersion"] = None
                self._dumpJson(jsonInfo, databaseFile)
            except:
                logger.warning("Cannot delete reference file %s" % (jsonInfo["ReferenceFile"]))
                pass

    def makeReference(self):
        """Creates a Reference copy from the base scene version at cursor position"""
        if self._currentVersionIndex == -1:
            logger.warning("Cursor is not on a Base Scene Version. Cancelling")
            return

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


    # def checkCurrentReference(self, deepCheck=False):
    #     if not self._currentBaseSceneName:
    #         logger.warning("Cursor is not on a Base Scene. Cancelling")
    #         return
    #     if self._currentSceneInfo["ReferenceFile"]:
    #         relVersionFile = self._currentSceneInfo["Versions"][self._currentSceneInfo["ReferencedVersion"] - 1][0]
    #         absVersionFile = os.path.join(self.projectDir, relVersionFile)
    #         relRefFile = self._currentSceneInfo["ReferenceFile"]
    #         absRefFile = os.path.join(self.projectDir, relRefFile)
    #
    #         if not os.path.isfile(absRefFile):
    #             logger.warning("CODE RED: Reference File does not exist")
    #             return -1 # code red
    #         else:
    #             if deepCheck:
    #                 if filecmp.cmp(absVersionFile, absRefFile):
    #                     logger.info("CODE GREEN: Everything is OK")
    #                     return 1 # code Green
    #                 else:
    #                     logger.warning("CODE RED: Checksum mismatch with reference file")
    #                     return -1 # code red
    #             else:
    #                 logger.info("CODE GREEN: Everything is OK")
    #                 return 1 # code Green
    #     else:
    #         logger.info("CODE YELLOW: File does not have a reference copy")
    #         return 0 # code yellow

    def checkReference(self, jsonFile, deepCheck=False):
        sceneInfo = self._loadJson(jsonFile)

        if sceneInfo["ReferenceFile"]:
            relVersionFile = sceneInfo["Versions"][sceneInfo["ReferencedVersion"] - 1][0]
            absVersionFile = os.path.join(self.projectDir, relVersionFile)
            relRefFile = sceneInfo["ReferenceFile"]
            absRefFile = os.path.join(self.projectDir, relRefFile)

            if not os.path.isfile(absRefFile):
                logger.warning("CODE RED: Reference File does not exist")
                return -1 # code red
            else:
                if deepCheck:
                    if filecmp.cmp(absVersionFile, absRefFile):
                        logger.info("CODE GREEN: Everything is OK")
                        return 1 # code Green
                    else:
                        logger.warning("CODE RED: Checksum mismatch with reference file")
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
            return -1, ["Admin Rights", "Maya does not have the administrator rights",
                        "You need to run Maya as administrator to work with Scene Manager"]
        return None, None

    def _folderCheck(self, folder):
        if not os.path.isdir(os.path.normpath(folder)):
            os.makedirs(os.path.normpath(folder))

    def _nameCheck(self, text):
        """Checks the text for illegal characters, Returns:  corrected Text or -1 for Error """
        text = text.replace("|", "__")
        if re.match("^[A-Za-z0-9_-]*$", text):
            if text == "":
                return -1
            text = text.replace(" ", "_")
            # text = text.replace("|", "__")
            return text
        else:
            return -1

    def _niceName(self, path):
        """Gets the base name of the given filename"""
        basename = os.path.split(path)[1]
        return os.path.splitext(basename)[0]

    def _resolveProjectPath(self, projectRoot, projectName, brandName, client):
        if projectName == "" or client == "" or projectRoot == "":
            msg = ("Fill the mandatory fields")
            logger.warning(msg)
            return -1, msg
        projectDate = datetime.datetime.now().strftime("%y%m%d")

        if brandName:
            brandName = "%s_" % brandName
        else:
            brandName = ""
        fullName = "{0}{1}_{2}_{3}".format(brandName, projectName, client, projectDate)
        fullPath = os.path.join(os.path.normpath(projectRoot), fullName)
        return fullPath

    ## Database loading / saving functions
    ## -----------------------------

    def _loadJson(self, file):
        """Loads the given json file"""
        if os.path.isfile(file):
            with open(file, 'r') as f:
                # The JSON module will read our file, and convert it to a python dictionary
                data = json.load(f)
                return data
        else:
            return None

    def _dumpJson(self, data, file):
        """Saves the data to the json file"""

        with open(file, "w") as f:
            json.dump(data, f, indent=4)

    def _loadUsers(self):
        """Load Users from file"""
        # old Name
        if not os.path.isfile(self._pathsDict["usersFile"]):
            userDB = {"Generic": "gn"}
            self._dumpJson(userDB, self._pathsDict["usersFile"])
            return userDB
        else:
            userDB = self._loadJson(self._pathsDict["usersFile"])
            return userDB

    def _loadCategories(self):
        """Load Categories from file"""
        if os.path.isfile(self._pathsDict["categoriesFile"]):
            categoriesData = self._loadJson(self._pathsDict["categoriesFile"])
        else:
            categoriesData = ["Model", "Shading", "Rig", "Layout", "Animation", "Render", "Other"]
            self._dumpJson(categoriesData, self._pathsDict["categoriesFile"])
        return categoriesData

    def _loadSceneInfo(self):
        """Returns scene info of base scene at cursor position"""
        sceneInfo = self._loadJson(self._baseScenesInCategory[self._currentBaseSceneName])
        return sceneInfo

    def _loadUserPrefs(self):
        """Load Last CategoryIndex, SubProject Index, User name and Access mode from file as dictionary"""
        if os.path.isfile(self._pathsDict["currentsFile"]):
            settingsData = self._loadJson(self._pathsDict["currentsFile"])
        else:
            settingsData = {"currentTabIndex": 0, "currentSubIndex": 0, "currentUser": self._usersDict.keys()[0],
                            "currentMode": False}
            self._dumpJson(settingsData, self._pathsDict["currentsFile"])
        return settingsData

    def _saveUserPrefs(self, settingsData):
        """Save Last CategoryIndex, SubProject Index, User name and Access mode to file as dictionary"""
        try:
            self._dumpJson(settingsData, self._pathsDict["currentsFile"])
            msg = ""
            return 0, msg
        except:
            msg = "Cannot save current settings"
            return -1, msg

    def _loadSubprojects(self):
        """Loads Subprojects of current project"""
        if not os.path.isfile(self._pathsDict["subprojectsFile"]):
            data = ["None"]
            self._dumpJson(data, self._pathsDict["subprojectsFile"])
        else:
            data = self._loadJson(self._pathsDict["subprojectsFile"])
        return data

    def _saveSubprojects(self, subprojectsList):
        """Save Subprojects to the file"""
        self._dumpJson(subprojectsList, self._pathsDict["subprojectsFile"])

    def _loadProjects(self):
        """Loads Projects dictionary for each software"""
        if not os.path.isfile(self._pathsDict["projectsFile"]):
            return
        else:
            projectsData = self._loadJson(self._pathsDict["projectsFile"])
        return projectsData

    def _saveProjects(self, data):
        """Saves the current project data to the file"""
        self._dumpJson(data, self._pathsDict["projectsFile"])

    def _loadPBSettings(self):
        # old Name getPBsettings

        # pbSettingsFile = os.path.normpath(os.path.join(self.project_Path, "Playblasts", "PBsettings.json"))

        if not os.path.isfile(self._pathsDict["pbSettingsFile"]):
            defaultSettings = {"Resolution": (1280, 720),  ## done
                               "Format": 'avi',  ## done
                               "Codec": 'IYUV Codec',  ## done
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
            return pbSettings










