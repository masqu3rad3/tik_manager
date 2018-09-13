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



import platform
import SmDatabase as db
import pymel.core as pm
import os
import logging

logging.basicConfig()
logger = logging.getLogger('smSkeleton')
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

class TikManager(object):
    def __init__(self):
        super(TikManager, self).__init__()
        self.database = db.SmDatabase()
        self.validCategories = ["Model", "Shading", "Rig", "Layout", "Animation", "Render", "Other"]
        self.__init_paths()
        self.__init_database()
        self.__backwardcompatibility()

        self.currentPlatform = platform.system()

        self.padding = 3


    def __backwardcompatibility(self):
        """
        This function checks for the old database structure and creates a copy with the new structure
        :return: None
        """
        old_dbDir = os.path.normpath(os.path.join(self.projectDir, "data", "SMdata"))
        if os.path.isdir(old_dbDir):
            # TODO: copy/move all contents of the folder to the new structure
            logger.info("All database contents moved to the new structure folder => %s" %self.databaseDir)
            pass




    def __init_paths(self):
        # This function should be overridden for each software
        # all paths in here must be absolute paths

        self.projectDir = os.path.normpath(pm.workspace(q=1, rd=1))
        self.masterDir = os.path.normpath(os.path.join(self.projectDir, "smDatabase"))
        folderCheck(self.masterDir)
        self.databaseDir = os.path.normpath(os.path.join(self.masterDir, "mayaDB"))
        folderCheck(self.databaseDir)
        self.scenesDir = os.path.normpath(os.path.join(self.projectDir, "scenes"))
        folderCheck(self.scenesDir)
        self.sceneFile = pm.sceneName()
        self.subprojectsFile = os.path.normpath(os.path.join(self.databaseDir, "subPdata.json")) # dont change
        self.previewsDir = os.path.normpath(os.path.join(self.projectDir, "Playblasts")) # dont change
        folderCheck(self.scenesDir)
        self.pbSettingsFile = os.path.normpath(os.path.join(self.previewsDir, "PBsettings.json")) # dont change
        self.generalSettingsDir = os.path.dirname(os.path.abspath(__file__))
        self.usersFile = os.path.normpath(os.path.join(self.generalSettingsDir, "sceneManagerUsers.json"))
        self.userSettingsDir = os.path.join(os.path.expanduser("~"), "SceneManager")
        folderCheck(self.userSettingsDir)
        self.bookmarksFile = os.path.normpath(os.path.join(self.userSettingsDir, "smBookmarks.json"))
        self.currentsFile = os.path.normpath(os.path.join(self.userSettingsDir, "smCurrents.json"))

    def __init_database(self):
        self.usersDict = self.database.loadUsers(self.usersFile)
        self.currentsDict = self.database.loadUserPrefs(self.currentsFile)
        self.subProjectsList = self.database.loadSubprojects(self.subprojectsFile)
        # self.pbSettingsDict = self.database.loadPBSettings(self.pbSettingsFile) # not immediate
        # self.bookmarksList = self.database.loadFavorites(self.bookmarksFile) # not immediate

    def change_currentTabIndex(self, category):
        self.currentsDict["currentTabIndex"] = category
        self.database.saveUserPrefs(self.currentsDict, self.currentsFile)

    def change_currentSubIndex(self, subindex):
        self.currentsDict["currentSubIndex"] = subindex
        self.database.saveUserPrefs(self.currentsDict, self.currentsFile)

    def change_currentUser(self, user):
        self.currentsDict["currentSubIndex"] = user
        self.database.saveUserPrefs(self.currentsDict, self.currentsFile)

    def change_currentMode(self, mode):
        self.currentsDict["currentSubIndex"] = mode
        self.database.saveUserPrefs(self.currentsDict, self.currentsFile)

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


    def set_project(self, path):
        # totally software specific or N/A
        melCompPath = path.replace("\\", "/") # mel is picky
        command = 'setProject "%s";' %melCompPath
        mel.eval(command)
        self.scenePaths["projectPath"] = pm.workspace(q=1, rd=1)


    def get_project_report(self):
        pass
        ## What we need:
        # PATH(abs) projectPath
        # PATH(abs) software specific Real Scenes Folder Path
        # software project file extensions

    def save_callback(self):
        pass
        ## What we need:
        # Results of getSceneInfo

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




