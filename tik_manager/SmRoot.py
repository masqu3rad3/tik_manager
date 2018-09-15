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
import SmDatabase as db
reload(db)
import datetime

# import pymel.core as pm
import os
import logging
# import maya.mel as mel

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
        self.database = db.SmDatabase()
        self.validCategories = ["Model", "Shading", "Rig", "Layout", "Animation", "Render", "Other"]

        self.currentPlatform = platform.system()
        self._pathsDict={}
        self.padding = 3


    def backwardcompatibility(self):
        """
        This function checks for the old database structure and creates a copy with the new structure
        :return: None
        """
        old_dbDir = os.path.normpath(os.path.join(self._pathsDict["projectDir"], "data", "SMdata"))
        if os.path.isdir(old_dbDir):
            # TODO: copy all contents of the folder to the new structure
            # TODO: gather all scene json files, update the self locations
            logger.info("All database contents moved to the new structure folder => %s" % self._pathsDict["databaseDir"])
            pass


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
        self._usersDict = self.database.loadUsers(self._pathsDict["usersFile"])
        self._currentsDict = self.database.loadUserPrefs(self._pathsDict["currentsFile"], self._usersDict.keys()[0])
        self._subProjectsList = self.database.loadSubprojects(self._pathsDict["subprojectsFile"])
        # self.pbSettingsDict = self.database.loadPBSettings(self.pbSettingsFile) # not immediate
        # self.bookmarksList = self.database.loadFavorites(self.bookmarksFile) # not immediate

    @property
    def projectDir(self):
        return self._pathsDict["projectDir"]

    @property
    def sceneFile(self):
        return self._pathsDict["sceneFile"]

    @property
    def masterDir(self):
        return self._pathsDict["masterDir"]

    @property
    def databaseDir(self):
        return self._pathsDict["databaseDir"]

    @property
    def scenesDir(self):
        return self._pathsDict["scenesDir"]

    @property
    def subprojectsFile(self):
        return self._pathsDict["subprojectsFile"]

    @property
    def previewsDir(self):
        return self._pathsDict["previewsDir"]

    @property
    def pbSettingsFile(self):
        return self._pathsDict["pbSettingsFile"]

    @property
    def generalSettingsDir(self):
        return self._pathsDict["generalSettingsDir"]

    @property
    def usersFile(self):
        return self._pathsDict["usersFile"]

    @property
    def userSettingsDir(self):
        return self._pathsDict["userSettingsDir"]

    @property
    def bookmarksFile(self):
        return self._pathsDict["bookmarksFile"]

    @property
    def currentsFile(self):
        return self._pathsDict["currentsFile"]

    #Currents
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

    @currentTabIndex.setter
    def currentTabIndex(self, indexData):
        if not 0 <= indexData < len(self.validCategories):
            logger.error(("entered index is out of range!"))
            return
        self._setCurrents("currentTabIndex", indexData)

    @currentSubIndex.setter
    def currentSubIndex(self, indexData):
        if not 0 <= indexData < len(self._subProjectsList):
            logger.error(("entered index is out of range!"))
            return
        self._setCurrents("currentSubIndex", indexData)

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

    def _setCurrents(self, att, newdata):
        self._currentsDict[att] = newdata
        self.database.saveUserPrefs(self._currentsDict, self._pathsDict["currentsFile"])

    def getUsers(self):
        return self._usersDict

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


    # def set_project(self, path):
    #     # totally software specific or N/A
    #     melCompPath = path.replace("\\", "/") # mel is picky
    #     command = 'setProject "%s";' %melCompPath
    #     mel.eval(command)
    #     self.projectDir = pm.workspace(q=1, rd=1)

    def showInExplorer(self, path):
        if not os.path.isdir(path):
            logger.error("path is not a directory path or does not exist")
            return
        if self.currentPlatform == "Windows":
            os.startfile(path)
        if self.currentPlatform == "Linux":
            os.system('nautilus %s' % path)

    def scanBasescenes(self):
        pass


    def getProjectReport(self):
        # TODO Before this finish scan functions
        def getOldestFile(rootfolder, extension=".avi"):
            return min(
                (os.path.join(dirname, filename)
                 for dirname, dirnames, filenames in os.walk(rootfolder)
                 for filename in filenames
                 if filename.endswith(extension)),
                key=lambda fn: os.stat(fn).st_mtime)

        def getNewestFile(rootfolder, extension=".avi"):
            return max(
                (os.path.join(dirname, filename)
                 for dirname, dirnames, filenames in os.walk(rootfolder)
                 for filename in filenames
                 if filename.endswith(extension)),
                key=lambda fn: os.stat(fn).st_mtime)

        oldestFile = getOldestFile(self.scenesDir, extension=(".mb", ".ma"))
        pathOldestFile, nameOldestFile = os.path.split(oldestFile)
        oldestTimeMod = datetime.datetime.fromtimestamp(os.path.getmtime(oldestFile))
        newestFile = getNewestFile(self.scenesDir, extension=(".mb", ".ma"))
        pathNewestFile, nameNewestFile = os.path.split(oldestFile)
        newestTimeMod = datetime.datetime.fromtimestamp(os.path.getmtime(newestFile))

        L1 = "Oldest Scene file: {0} - {1}".format(nameNewestFile, oldestTimeMod)
        L2 = "Newest Scene file: {0} - {1}".format(nameNewestFile, newestTimeMod)
        L3 = "Elapsed Time: {0}".format(str(newestTimeMod - oldestTimeMod))
        L4 = "Scene Counts:"

        report = {}
        for subP in range(len(self._subProjectsList)):
            subReport = {}
            for category in self.validCategories:
                categoryItems = (self.scanScenes(category, subProjectAs=subP)[0])
                categoryItems = [x for x in categoryItems if x != []]

                L4 = "{0}\n{1}: {2}".format(L4, category, len(categoryItems))
                subReport[category] = categoryItems
            report[self.subProjectList[subP]] = subReport

        report = pprint.pformat(report)
        ## What we need:
        # PATH(abs) projectPath
        # PATH(abs) software specific Real Scenes Folder Path
        # software project file extensions

    def saveCallback(self):
        if not self._pathsDict["sceneFile"]:
            return

    def saveBasescene(self):
        pass
        ## What we need:
        # current user
        # PATH(abs) projectPath
        # PATH(abs) software database (jsonPath)
        # PATH(abs) software specific Real Scenes Folder Path

    def saveVersion(self):
        pass
        ## What we need:
        # current user

    def createPreview(self):
        pass
        ## What we need:
        # PATH(abs) pbSettings file

    def playPreview(self):
        pass
        ## What we need:
        # PATH(abs) projectPath

    def removePreview(self, relativePath, jsonFile, version):
        pass

    def createSubproject(self, nameOfSubProject):
        pass
        ## What we need:
        # PATH(abs) software database (jsonPath)
        # PATH(s)(abs, list) sub-projects





    def loadBasescene(self):
        pass

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

    def loadReference(self):
        pass

    def createThumbnail(self):
        pass

    def replaceThumbnail(self):
        pass




