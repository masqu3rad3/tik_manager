## platform and software independent logic class


## Necessary paths
##-----------------
## project folderpath: absolute path where the whole project is (COMMON)
    ## database folderpath: Where all the database files are (COMMON)
        ## softwareDatabase folderpath: Where all the software SPECIFIC database files are
            ## sub-project database path
            ## raid location database path
            ## Category Folders Path
                ## sub-project Folders Path
                    ## sub-project Files Path
                ## SceneDatabase filepaths

    ## scenes folderpath (SPECIFIC to software)
    ## previews folder(Common)
        ## previewoptions filepath (Sofware SPECIFIC)
## userSettings filePath (COMMON)
## userBookmarks filePath (COMMON
##
##
##
##
##

# software specific commands used in common functions:

# Init
# pm.workspace(q=1, rd=1)
# pm.sceneName()
# pm.scriptJob() # optional, previously used in UI

# Compare versions
# pm.versions.current()

# Save Base Scene()
# pm.versions.current()

# Save Version
# pm.saveAs()

# Load Scene
# cmds.file()

# Load Reference
# cmds.file()

# SetProject
# mel.eval('setProject "%s";' %melCompPath)

# create Playblast
# mel.eval('$tmpVar=$gPlayBackSlider')  # get playback slier
# pm.playblast()
# pm.playbackOptions()
# pm.ls()
# pm.select()
# pm.modelPanel()
# pm.window()
# pm.paneLayout()
# pm.modelPanel()
# pm.showWindow()
# pm.setFocus()
# pm.modelEditor()
# pm.camera()
# pm.headsUpDisplay()
# pm.timeControl()
# pm.deleteUI()

# Create Thumbnail
# pm.currentTime()
# pm.getAttr()
# pm.setAttr()
# pm.playblast()



import platform
# import SmDatabase as db
# reload(db)
import datetime

# import pymel.core as pm
import os
import logging
import pprint
# from shutil import copyfile
# from shutil import copytree
import shutil
from glob import glob
import json

logging.basicConfig()
logger = logging.getLogger('smRoot')
logger.setLevel(logging.INFO)

def folderCheck(folder):
    if not os.path.isdir(os.path.normpath(folder)):
        os.makedirs(os.path.normpath(folder))

# def pathOps(fullPath, mode):
#     """
#     performs basic path operations.
#     Args:
#         fullPath: (Unicode) Absolute Path
#         mode: (String) Valid modes are 'path', 'basename', 'filename', 'extension', 'drive'
#
#     Returns:
#         Unicode
#
#     """
#
#     if mode == "drive":
#         drive = os.path.splitdrive(fullPath)
#         return drive
#
#     path, basename = os.path.split(fullPath)
#     if mode == "path":
#         return path
#     if mode == "basename":
#         return basename
#     filename, ext = os.path.splitext(basename)
#     if mode == "filename":
#         return filename
#     if mode == "extension":
#         return ext

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
        if os.path.isdir(old_dbDir):

            recursive_overwrite(old_dbDir, new_dbDir)
            logger.info("All old database contents copied to the new structure folder => %s" % self._pathsDict["databaseDir"])

            # TODO: gather all scene json files, update the self locations
            oldCategories = ["Model", "Shading", "Rig", "Layout", "Animation", "Render", "Other"]
            for category in oldCategories:
                categoryDBpath = os.path.normpath(os.path.join(new_dbDir, category))
                if os.path.isdir(categoryDBpath):
                    jsonFiles = [y for x in os.walk(categoryDBpath) for y in glob(os.path.join(x[0], '*.json'))]
                    for file in jsonFiles:
                        fileData = self._loadJson(file)
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

        self._pathsDict["projectDir"] = self.getProjectDir()
        self._pathsDict["sceneFile"] = self.getSceneFile()
        if self._pathsDict["projectDir"] == -1 or self._pathsDict["sceneFile"] == -1:
            logger.error("The following functions must be overridden in inherited class:\n'__get_currentProjectDir'\n'__get_currentSceneFile'")
            raise Exception()

        self._pathsDict["masterDir"] = os.path.normpath(os.path.join(self._pathsDict["projectDir"], "smDatabase"))
        folderCheck(self._pathsDict["masterDir"])

        self._pathsDict["databaseDir"] = os.path.normpath(os.path.join(self._pathsDict["masterDir"], "mayaDB"))
        folderCheck(self._pathsDict["databaseDir"])

        self._pathsDict["scenesDir"] = os.path.normpath(os.path.join(self._pathsDict["projectDir"], "scenes"))
        folderCheck(self._pathsDict["scenesDir"])

        self._pathsDict["subprojectsFile"] = os.path.normpath(os.path.join(self._pathsDict["databaseDir"], "subPdata.json"))
        self._pathsDict["categoriesFile"] = os.path.normpath(os.path.join(self._pathsDict["databaseDir"], "categories.json"))

        self._pathsDict["previewsDir"] = os.path.normpath(os.path.join(self._pathsDict["projectDir"], "Playblasts")) # dont change
        folderCheck(self._pathsDict["previewsDir"])

        self._pathsDict["pbSettingsFile"] = os.path.normpath(os.path.join(self._pathsDict["previewsDir"], "PBsettings.json")) # dont change

        self._pathsDict["generalSettingsDir"] = os.path.dirname(os.path.abspath(__file__))

        self._pathsDict["usersFile"] = os.path.normpath(os.path.join(self._pathsDict["generalSettingsDir"], "sceneManagerUsers.json"))

        self._pathsDict["userSettingsDir"] = os.path.join(os.path.expanduser("~"), "SceneManager")
        folderCheck(self._pathsDict["userSettingsDir"])

        self._pathsDict["bookmarksFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], "smBookmarks.json"))
        self._pathsDict["currentsFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], "smCurrents.json"))

    def getProjectDir(self):
        """This function must be overriden"""
        return -1

    def getSceneFile(self):
        """This function must be overriden"""
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
        self._currentVersionIndex = 0
        self._currentPreviewCamera = ""
        self._currentSceneInfo = {}

        #Scene related
        self._currentVersionIndex = -1
        self._currentPreviewsDict = {}
        self._currentNotes = ""
        self._currentThumbFile = ""

        self.scanBaseScenes()

    # @property
    # def projectDir(self):
    #     return self._pathsDict["projectDir"]

    # @property
    # def sceneFile(self):
    #     return self._pathsDict["sceneFile"]

    # @property
    # def masterDir(self):
    #     return self._pathsDict["masterDir"]

    # @property
    # def databaseDir(self):
    #     return self._pathsDict["databaseDir"]

    # @property
    # def scenesDir(self):
    #     return self._pathsDict["scenesDir"]

    # @property
    # def subprojectsFile(self):
    #     return self._pathsDict["subprojectsFile"]

    # @property
    # def previewsDir(self):
    #     return self._pathsDict["previewsDir"]

    # @property
    # def pbSettingsFile(self):
    #     return self._pathsDict["pbSettingsFile"]

    # @property
    # def generalSettingsDir(self):
    #     return self._pathsDict["generalSettingsDir"]

    # @property
    # def usersFile(self):
    #     return self._pathsDict["usersFile"]

    # @property
    # def userSettingsDir(self):
    #     return self._pathsDict["userSettingsDir"]

    # @property
    # def bookmarksFile(self):
    #     return self._pathsDict["bookmarksFile"]

    # @property
    # def currentsFile(self):
    #     return self._pathsDict["currentsFile"]

    @property
    def projectDir(self):
        return self._pathsDict["projectDir"]

    @property
    def subProject(self):
        return self._subProjectsList[self.currentSubIndex]

    @property
    def baseScene(self):
        baseSceneDir = os.path.abspath(os.path.join(self._pathsDict["sceneFile"], os.pardir))
        return os.path.basename(baseSceneDir)

    #Currents (Database)
    @property
    def currentTabIndex(self):
        return self._currentsDict["currentTabIndex"]

    @property
    def currentSubIndex(self):
        return self._currentsDict["currentSubIndex"]

    @property
    def currentUser(self):
        return self._currentsDict["currentUser"]

    @property
    def currentMode(self):
        return self._currentsDict["currentMode"]

    # Currents (Non-Database)
    @property
    def currentBaseSceneName(self):
        return self._currentBaseSceneName

    @property
    def currentVersionIndex(self):
        return self._currentVersionIndex

    @property
    def currentPreviewCamera(self):
        return self._currentPreviewCamera

    @property
    def baseScenesInCategory(self):
        return sorted(self._baseScenesInCategory.keys())

    @currentTabIndex.setter
    def currentTabIndex(self, indexData):
        if not 0 <= indexData < len(self._categories):
            logger.error(("out of range!"))
            return
        if indexData == self.currentTabIndex:
            # logger.warning("Cursor is already at %s" %indexData)
            return
        self._setCurrents("currentTabIndex", indexData)
        self.scanBaseScenes()
        self.CurrentBaseSceneName = ""
        self._currentVersionIndex = -1
        self._currentPreviewCamera = -1
        self.cursorInfo()

        # self._currentVersionIndex = -1
        # self._currentPreviewIndex = -1

    @currentSubIndex.setter
    def currentSubIndex(self, indexData):
        if not 0 <= indexData < len(self._subProjectsList):
            logger.error(("entered index is out of range!"))
            return
        if indexData == self.currentSubIndex:
            # logger.warning("Cursor is already at %s" %indexData)
            return

        self._setCurrents("currentSubIndex", indexData)
        self.scanBaseScenes()
        # de-select previous base scene
        self._currentBaseSceneName = ""
        self._currentVersionIndex = -1
        self._currentPreviewCamera = -1
        self.cursorInfo()

    @currentBaseSceneName.setter
    def currentBaseSceneName(self, sceneName):
        if sceneName not in self._baseScenesInCategory.keys():
            logger.error("invalid name")
            return
        # if sceneName == self._currentBaseSceneName:
        #     logger.warning("Cursor is already at %s" %sceneName)
        #     return

        self._currentBaseSceneName = sceneName
        self.getSceneInfo()
        if not sceneName:
            self._currentVersionIndex = -1

        if self._currentSceneInfo["ReferencedVersion"]:
            self._currentVersionIndex = self._currentSceneInfo["ReferencedVersion"]
        else:
            self._currentVersionIndex = len(self._currentSceneInfo["Versions"])-1
        self.cursorInfo()
        # self._currentPreviewIndex = 0

    @currentVersionIndex.setter
    def currentVersionIndex(self, indexData):
        if not self._currentSceneInfo:
            logger.warning(("BaseScene not Selected"))
            return
        if not 0 <= indexData < len(self._currentSceneInfo["Versions"]):
            logger.error(("out of range!"))
            return
        # if self._currentVersionIndex == indexData:
        #     logger.warning("Cursor is already at %s" % indexData)
        #     return
        self._currentVersionIndex = indexData
        self._currentNotes = self._currentSceneInfo["Versions"][self._currentVersionIndex][3]
        self._currentPreviewsDict = self._currentSceneInfo["Versions"][self._currentVersionIndex][4]
        if not self._currentPreviewsDict.keys():
            self._currentPreviewCamera = ""
        else:
            self._currentPreviewCamera = sorted(self._currentPreviewsDict.keys())[0]


        self._currentThumbFile = self._currentSceneInfo["Versions"][self._currentVersionIndex][5]


        self.cursorInfo()

    @currentPreviewCamera.setter
    def currentPreviewIndex(self, indexData):
        if not self._currentSceneInfo:
            logger.warning(("BaseScene not Selected"))
            return
        if not 0 <= indexData < len(self._currentPreviewsDict.items()):
            logger.error(("out of range!"))
            return
        self._currentPreviewCamera = indexData

        self.cursorInfo()



    @currentUser.setter
    def currentUser(self, name):
        if name not in self._usersDict.keys():
            logger.error(("%s is not a user!" %name))
            return
        self._setCurrents("currentUser", name)

    @currentMode.setter
    def currentMode(self, bool):
        if not type(bool) is 'bool':
            if bool is 0:
                bool = False
            elif bool is 1:
                bool = True
            else:
                logger.error("only boolean or 0-1 accepted, entered %s" %bool)
                return
        self._setCurrents("currentMode", bool)


    def cursorInfo(self):
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

    def _setCurrents(self, att, newdata):
        self._currentsDict[att] = newdata
        self._saveUserPrefs(self._currentsDict)

    def getCategories(self):
        return self._categories

    def getUsers(self):
        return sorted(self._usersDict.keys())

    def getSubProjects(self):
        return self._subProjectsList

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


    def projectChanged(self):
        pass
        # update Project
        # update SubProject
        # update Category
        # get scenes in category
        # set scene index to -1

    def getNotes(self):
        """returns (String) version notes on cursor position"""
        return self._currentNotes

    def getPreviews(self):
        """returns (list) nice preview names of version on cursor position"""
        return sorted(self._currentPreviewsDict.keys())

    def getThumbnail(self):
        """returns (String) thumbnail path of version on cursor position"""

    ## Database loading / saving functions
    ## -----------------------------

    def _loadJson(self, file):
        """
        Loads the given json file
        Args:
            file: (String) Path to the json file

        Returns: JsonData

        """
        if os.path.isfile(file):
            with open(file, 'r') as f:
                # The JSON module will read our file, and convert it to a python dictionary
                data = json.load(f)
                return data
        else:
            return None

    def _dumpJson(self, data, file):
        """
        Saves the data to the json file
        Args:
            data: Data to save
            file: (String) Path to the json file

        Returns: None

        """

        with open(file, "w") as f:
            json.dump(data, f, indent=4)

    def _loadUsers(self):
        # old Name
        if not os.path.isfile(self._pathsDict["usersFile"]):
            userDB = {"Generic": "gn"}
            self._dumpJson(userDB, self._pathsDict["usersFile"])
            return userDB
        else:
            userDB = self._loadJson(self._pathsDict["usersFile"])
            return userDB

    def _loadCategories(self):
        if os.path.isfile(self._pathsDict["categoriesFile"]):
            categoriesData = self._loadJson(self._pathsDict["categoriesFile"])
        else:
            categoriesData = ["Model", "Shading", "Rig", "Layout", "Animation", "Render", "Other"]
            self._dumpJson(categoriesData, self._pathsDict["categoriesFile"])
        return categoriesData

    def _loadUserPrefs(self):

        if os.path.isfile(self._pathsDict["currentsFile"]):
            settingsData = self._loadJson(self._pathsDict["currentsFile"])
        else:
            settingsData = {"currentTabIndex": 0, "currentSubIndex": 0, "currentUser": self._usersDict.keys()[0], "currentMode": False}
            self._dumpJson(settingsData, self._pathsDict["currentsFile"])
        return settingsData

    def _saveUserPrefs(self, settingsData):
        try:
            self._dumpJson(settingsData,  self._pathsDict["currentsFile"])
            msg = ""
            return 0, msg
        except:
            msg = "Cannot save current settings"
            return -1, msg

    def _loadSubprojects(self):
        if not os.path.isfile(self._pathsDict["subprojectsFile"]):
            data = ["None"]
            self._dumpJson(data, self._pathsDict["subprojectsFile"])
        else:
            data = self._loadJson(self._pathsDict["subprojectsFile"])
        return data


    def createNewProject(self, projectRoot, projectName, brandName, client):
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


    def showInExplorer(self, path):
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
    def _niceName(self, path):
        basename = os.path.split(path)[1]
        return os.path.splitext(basename)[0]

    def scanBaseScenes(self):
        """Returns the basescene database files in current category"""
        categoryDBpath = os.path.normpath(os.path.join(self._pathsDict["databaseDir"], self._categories[self.currentTabIndex]))
        folderCheck(categoryDBpath)
        if not (self.currentSubIndex == 0):
            categorySubDBpath = os.path.normpath(os.path.join(categoryDBpath, (self._subProjectsList)[self.currentSubIndex])) # category name
            folderCheck(categorySubDBpath)

            searchDir = categorySubDBpath
        else:
            searchDir = categoryDBpath



        self._baseScenesInCategory = {self._niceName(file):file for file in glob(os.path.join(searchDir, '*.json'))}
        # self._currentBaseScenes = [os.path.join(searchDir, file) for file in os.listdir(searchDir) if file.endswith('.json')]

        # glob(os.path.join(x[0], '*.json'))
        return self._baseScenesInCategory # dictionary of json files


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



    def getSceneInfo(self):
        # sceneInfo = self._loadJson(basesceneFile)
        self._currentSceneInfo = self._loadJson(self._baseScenesInCategory[self._currentBaseSceneName])
        return self._currentSceneInfo

    # def getVersionInfo(self, basesceneFile, version):
    #     versionData = self._loadJson(basesceneFile)
    #     return versionData["Versions"][version][1], versionData["Versions"][version][4] # versionNotes, playBlastDictionary

    def addNote(self, note):
        if not self._currentBaseSceneName:
            logger.warning("No Base Scene file selected")
            return
        # sceneInfo = self.getSceneInfo()
        # self._currentNotes = self._currentSceneInfo["Versions"][self._currentVersionIndex][1]
        now = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M")
        self._currentNotes = "%s\n[%s] on %s\n%s\n" % (self._currentNotes, self.currentUser, now, note)
        self._currentSceneInfo["Versions"][self._currentVersionIndex][1] = self._currentNotes
        self._dumpJson(self._currentSceneInfo, self._baseScenesInCategory[self._currentBaseSceneName])



    def getPreviews(self, sceneInfo, version):

        try:
            previewDict = sceneInfo["Versions"][version][4]
            return previewDict
        except KeyError:
            msg = "cannot get preview dictionary from sceneInfo"
            logger.error(msg)
            raise AssertionError()
            # return -1, msg



    def playPreview(self, sceneInfo, version, camera):

        previewDict = self.getPreviews(sceneInfo, version)
        relativePath = previewDict[camera]
        absPath = os.path.join(self.projectDir, relativePath)
        if self.currentPlatform == "Windows":
            try:
                os.startfile(absPath)
            except WindowsError:
                return -1, ["Cannot Find Playblast", "Playblast File is missing", "Do you want to remove it from the Database?"]
        # TODO something to play the file in linux
        return

    # def removePreview(self, relativePath, jsonFile, version):
    # def removePreview(self, basesceneFile, sceneInfo, version, camera):
    #
    #     previewDict = self.getPreviews(sceneInfo, version)
    #     relativePath = previewDict[camera]
    #     dbFile =
    #
    #     for key, value in previewDict.iteritems():  # for name, age in list.items():  (for Python 3.x)
    #         if value == relativePath:
    #             previewDict.pop(key, None)
    #             sceneInfo["Versions"][version][4] = previewDict
    #             self._dumpJson(sceneInfo, basesceneFile)
    #             return

    def createSubproject(self, nameOfSubProject):
        pass
        ## What we need:
        # PATH(abs) software database (jsonPath)
        # PATH(s)(abs, list) sub-projects

    def deleteBasescene(self):
        #ADMIN ACCESS
        pass

    def deleteReference(self):
        #ADMIN ACCESS
        pass

    def makeReference(self):
        pass

    def checkReference(self):
        pass








