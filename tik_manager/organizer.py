## platform and software independent logic class

dataPath, jsonPath, scenesPath, playBlastRoot
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

class TikManager(object):
    def __init__(self):
        super(TikManager, self).__init__()

        self.__init_paths()
        self.__backwardcompatibility()
        self.database = db.SmDatabase()
        self.currentPlatform = platform.system()
        # self.currentProject = pm.workspace(q=1, rd=1)

        self.currentUserIndex = 0
        self.validCategories = ["Model", "Shading", "Rig", "Layout", "Animation", "Render", "Other"]
        self.currentCategoryIndex = 0
        self.padding = 3
        self.subProjectList = self.scanSubProjects()

        ## currents
        self.current = {}
        self.currentTabIndex = 0
        self.currentSubIndex = 0
        self.currentUser = ""
        self.currentMode = False

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
        # This function should be overriden for each software
        # all paths in here must be absolute paths

        self.projectDir = os.path.normpath(pm.workspace(q=1, rd=1))
        self.masterDir = os.path.normpath(os.path.join(self.projectDir, "smDatabase"))
        folderCheck(self.masterDir)
        self.databaseDir = os.path.normpath(os.path.join(self.masterDir, "mayaDB"))
        folderCheck(self.databaseDir)
        self.scenesDir = os.path.normpath(os.path.join(self.projectDir, "scenes"))
        folderCheck(self.scenesDir)
        self.sceneFile = pm.sceneName()
        self.subprojectFile = os.path.normpath(os.path.join(self.databaseDir, "subPdata.json")) # dont change
        self.previewsDir = os.path.normpath(os.path.join(self.projectDir, "Playblasts")) # dont change
        folderCheck(self.scenesDir)
        self.previewSettingsFile = os.path.normpath(os.path.join(self.previewsDir, "PBsettings.json")) # dont change
        self.generalSettingsDir = os.path.dirname(os.path.abspath(__file__))
        self.usersFile = os.path.normpath(os.path.join(self.generalSettingsDir, "sceneManagerUsers.json"))
        pass

    def __init_users(self):
        self.userList = self.database.initUsers(self.usersFile)
        pass

    def __init_history(self):
        self.current = self.database.loadUserPrefs()
        if not self.current["currentUser"] in (self.userList.keys()):
            self.current["currentUser"] = self.userList[self.userList.keys()[0]]
        # pass

    def __init_databases(self):
        self.userList = self.database.initUsers(self.usersFile)

    def __update_history(self):
        pass

    def change_user(self):
        pass

    def change_category(self):
        pass

    def change_mode(self):
        pass

    def change_subproject(self):

    def get_sceneinfo(self):
        pass
        ## What we need:
        # current scene name
        # PATH(abs) projectPath
        # PATH(abs) software database (jsonPath)
        # PATH(abs) current scene file
        # PATH(s)(abs, list) sub-projects

    def create_newproject(self, projectPath):
        pass
        # totally software specific or N/A


    def set_project(self, path):
        pass
        # totally software specific or N/A


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

    def save_basescene(self, category, baseName, subProject=0, makeReference=True, versionNotes="", *args,
                          **kwargs):
        pass
        ## What we need:
        # current user
        # PATH(abs) projectPath
        # PATH(abs) software database (jsonPath)
        # PATH(abs) software specific Real Scenes Folder Path

    def save_version(self, makeReference=True, versionNotes="", *args, **kwargs):
        pass
        ## What we need:
        # current user

    def create_preview(self, *args, **kwargs):
        pass
        ## What we need:
        # PATH(abs) pbSettings file

    def play_preview(self, relativePath):
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




