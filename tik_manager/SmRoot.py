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

        self.padding = 3


    def backwardcompatibility(self):
        """
        This function checks for the old database structure and creates a copy with the new structure
        :return: None
        """
        old_dbDir = os.path.normpath(os.path.join(self.__projectDir, "data", "SMdata"))
        if os.path.isdir(old_dbDir):
            # TODO: copy all contents of the folder to the new structure
            # TODO: gather all scene json files, update the self locations
            logger.info("All database contents moved to the new structure folder => %s" % self.__databaseDir)
            pass


    def init_paths(self):
        # This function should be overridden for each software
        # all paths in here must be absolute paths

        self.__projectDir = self.get_currentProjectDir()
        self.__sceneFile = self.get_currentSceneFile()
        if self.__projectDir == -1 or self.__sceneFile == -1:
            logger.error("The following functions must be overridden in inherited class:\n'__get_currentProjectDir'\n'__get_currentSceneFile'")
            raise Exception()

        self.__masterDir = os.path.normpath(os.path.join(self.__projectDir, "smDatabase"))
        folderCheck(self.__masterDir)
        self.__databaseDir = os.path.normpath(os.path.join(self.__masterDir, "mayaDB"))
        folderCheck(self.__databaseDir)
        self.__scenesDir = os.path.normpath(os.path.join(self.__projectDir, "scenes"))
        folderCheck(self.__scenesDir)
        self.__subprojectsFile = os.path.normpath(os.path.join(self.__databaseDir, "subPdata.json")) # dont change
        self.__previewsDir = os.path.normpath(os.path.join(self.__projectDir, "Playblasts")) # dont change
        folderCheck(self.__scenesDir)
        self.__pbSettingsFile = os.path.normpath(os.path.join(self.__previewsDir, "PBsettings.json")) # dont change
        self.__generalSettingsDir = os.path.dirname(os.path.abspath(__file__))
        self.__usersFile = os.path.normpath(os.path.join(self.__generalSettingsDir, "sceneManagerUsers.json"))
        self.__userSettingsDir = os.path.join(os.path.expanduser("~"), "SceneManager")
        folderCheck(self.__userSettingsDir)
        self.__bookmarksFile = os.path.normpath(os.path.join(self.__userSettingsDir, "smBookmarks.json"))
        self.__currentsFile = os.path.normpath(os.path.join(self.__userSettingsDir, "smCurrents.json"))

        self.__acayipTest = "asdf"

    def get_currentProjectDir(self):
        """This function must be overriden"""
        return -1

    def get_currentSceneFile(self):
        """This function must be overriden"""
        return -1

    def init_database(self):
        self.__usersDict = self.database.loadUsers(self.__usersFile)
        self.__currentsDict = self.database.loadUserPrefs(self.__currentsFile)
        self.__subProjectsList = self.database.loadSubprojects(self.__subprojectsFile)
        # self.pbSettingsDict = self.database.loadPBSettings(self.pbSettingsFile) # not immediate
        # self.bookmarksList = self.database.loadFavorites(self.bookmarksFile) # not immediate

    @property
    def projectDir(self):
        return self.__projectDir

    @property
    def sceneFile(self):
        return self.__sceneFile

    @property
    def masterDir(self):
        return self.__masterDir

    @property
    def databaseDir(self):
        return self.__databaseDir

    @property
    def scenesDir(self):
        return self.__scenesDir

    @property
    def subprojectsFile(self):
        return self.__subprojectsFile

    @property
    def previewsDir(self):
        return self.__previewsDir

    @property
    def pbSettingsFile(self):
        return self.__pbSettingsFile

    @property
    def generalSettingsDir(self):
        return self.__generalSettingsDir

    @property
    def usersFile(self):
        return self.__usersFile

    @property
    def acayipTest(self):
        return self.__acayipTest

    @acayipTest.setter
    def acayipTest (self, data):
        self.setPath (self.acayipTest, data)

    def setPath(self, att, path):
        att = path


    def change_currentTabIndex(self, category):
        self.__currentsDict["currentTabIndex"] = category
        self.database.saveUserPrefs(self.__currentsDict, self.__currentsFile)

    def change_currentSubIndex(self, subindex):
        self.__currentsDict["currentSubIndex"] = subindex
        self.database.saveUserPrefs(self.__currentsDict, self.__currentsFile)

    def change_currentUser(self, user):
        self.__currentsDict["currentSubIndex"] = user
        self.database.saveUserPrefs(self.__currentsDict, self.__currentsFile)

    def change_currentMode(self, mode):
        self.__currentsDict["currentSubIndex"] = mode
        self.database.saveUserPrefs(self.__currentsDict, self.__currentsFile)

    def create_newproject(self, projectPath):
        # check if there is a duplicate
        if not os.path.isdir(os.path.normpath(projectPath)):
            os.makedirs(os.path.normpath(projectPath))
        else:
            logger.warning("Project already exists")
            return

        # create Directory structure:
        os.mkdir(os.path.join(projectPath, "_COMP"))
        os.makedirs(os.path.join(projectPath, "_MAX", "Animation"))
        os.makedirs(os.path.join(projectPath, "_MAX", "Model"))
        os.makedirs(os.path.join(projectPath, "_MAX", "Render"))
        os.mkdir(os.path.join(projectPath, "_SCULPT"))
        os.mkdir(os.path.join(projectPath, "_REALFLOW"))
        os.mkdir(os.path.join(projectPath, "_HOUDINI"))
        os.mkdir(os.path.join(projectPath, "_REF"))
        os.mkdir(os.path.join(projectPath, "_TRACK"))
        os.makedirs(os.path.join(projectPath, "_TRANSFER", "FBX"))
        os.makedirs(os.path.join(projectPath, "_TRANSFER", "ALEMBIC"))
        os.makedirs(os.path.join(projectPath, "_TRANSFER", "OBJ"))
        os.makedirs(os.path.join(projectPath, "_TRANSFER", "MA"))
        os.mkdir(os.path.join(projectPath, "assets"))
        os.mkdir(os.path.join(projectPath, "cache"))
        os.mkdir(os.path.join(projectPath, "clips"))
        os.mkdir(os.path.join(projectPath, "data"))
        os.makedirs(os.path.join(projectPath, "images", "_CompRenders"))
        os.mkdir(os.path.join(projectPath, "movies"))
        os.mkdir(os.path.join(projectPath, "particles"))
        os.mkdir(os.path.join(projectPath, "Playblasts"))
        os.makedirs(os.path.join(projectPath, "renderData", "depth"))
        os.makedirs(os.path.join(projectPath, "renderData", "fur"))
        os.makedirs(os.path.join(projectPath, "renderData", "iprImages"))
        os.makedirs(os.path.join(projectPath, "renderData", "mentalray"))
        os.makedirs(os.path.join(projectPath, "renderData", "shaders"))
        os.mkdir(os.path.join(projectPath, "scenes"))
        os.mkdir(os.path.join(projectPath, "scripts"))
        os.mkdir(os.path.join(projectPath, "sound"))
        os.makedirs(os.path.join(projectPath, "sourceimages", "_FOOTAGE"))
        os.makedirs(os.path.join(projectPath, "sourceimages", "_HDR"))

        filePath = os.path.join(projectPath, "workspace.mel")
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


    def get_project_report(self):
        pass
        ## What we need:
        # PATH(abs) projectPath
        # PATH(abs) software specific Real Scenes Folder Path
        # software project file extensions

    def save_callback(self):
        if not self.__sceneFile:
            return

    def save_basescene(self):
        pass
        ## What we need:
        # current user
        # PATH(abs) projectPath
        # PATH(abs) software database (jsonPath)
        # PATH(abs) software specific Real Scenes Folder Path

    def save_version(self):
        pass
        ## What we need:
        # current user

    def create_preview(self):
        pass
        ## What we need:
        # PATH(abs) pbSettings file

    def play_preview(self):
        pass
        ## What we need:
        # PATH(abs) projectPath

    def remove_preview(self, relativePath, jsonFile, version):
        pass

    def create_subproject(self, nameOfSubProject):
        pass
        ## What we need:
        # PATH(abs) software database (jsonPath)
        # PATH(s)(abs, list) sub-projects

    def scan_subprojects(self):
        pass

    def scan_basescenes(self):
        pass

    def load_basescene(self):
        pass

    def delete_basescene(self):
        #ADMIN ACCESS
        pass

    def delete_reference(self):
        #ADMIN ACCESS
        pass

    def make_reference(self):
        pass

    def check_reference(self):
        pass

    def load_reference(self):
        pass

    def create_thumbnail(self):
        pass

    def replace_thumbnail(self):
        pass




