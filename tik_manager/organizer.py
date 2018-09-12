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
import smDatabaseOps as db
import os

def pathOps(fullPath, mode):
    """
    performs basic path operations.
    Args:
        fullPath: (Unicode) Absolute Path
        mode: (String) Valid modes are 'path', 'basename', 'filename', 'extension', 'drive'

    Returns:
        Unicode

    """

    if mode == "drive":
        drive = os.path.splitdrive(fullPath)
        return drive

    path, basename = os.path.split(fullPath)
    if mode == "path":
        return path
    if mode == "basename":
        return basename
    filename, ext = os.path.splitext(basename)
    if mode == "filename":
        return filename
    if mode == "extension":
        return ext

def getPaths():
    """
    Collects the necessary path data from the scene
    Returns: (Dictionary) projectPath, dataPath, jsonPath, scenesPath, playBlastRoot

    """
    projectPath = os.path.normpath(pm.workspace(q=1, rd=1))
    dataPath = os.path.normpath(os.path.join(projectPath, "data"))
    db.folderCheck(dataPath)
    jsonPath = os.path.normpath(os.path.join(dataPath, "SMdata"))
    db.folderCheck(jsonPath)
    scenesPath = os.path.normpath(os.path.join(projectPath, "scenes"))
    db.folderCheck(scenesPath)
    playBlastRoot = os.path.normpath(os.path.join(projectPath, "Playblasts"))
    db.folderCheck(playBlastRoot)
    pathDictionary = {"projectPath": projectPath,
                      "dataPath": dataPath,
                      "jsonPath": jsonPath,
                      "scenesPath": scenesPath,
                      "playBlastRoot": playBlastRoot
                      }
    return pathDictionary


class TikManager(object):
    def __init__(self):
        super(TikManager, self).__init__()
        self.database = db.SmDatabase()
        self.currentPlatform = platform.system()
        # self.currentProject = pm.workspace(q=1, rd=1)

        self.userList = self.database.initUsers()[0]
        self.currentUserIndex = 0
        self.validCategories = ["Model", "Shading", "Rig", "Layout", "Animation", "Render", "Other"]
        self.currentCategoryIndex = 0
        self.padding = 3
        self.scenePaths = getPaths()
        self.subProjectList = self.scanSubProjects()

        ## currents
        self.current = {}
        self.currentTabIndex = 0
        self.currentSubIndex = 0
        self.currentUser = ""
        self.currentMode = False

    def __initializePaths(self):
        # PATH(abs) projectPath
        # PATH(abs) software database (jsonPath)
        # PATH(abs) current scene file
        # PATH(s)(abs, list) sub-projects
        # PATH(abs) software specific Real Scenes Folder Path

        pass

    def __initializeUsers(self):
        self.userList = self.database.initUsers()[0]
        pass

    def __initializeHistory(self):
        self.current = self.database.loadUserPrefs()
        if not self.current["currentUser"] in (self.userList.keys()):
            self.current["currentUser"] = self.userList[self.userList.keys()[0]]
        # pass

    def __updateHistory(self):

    def getSceneInfo(self):
        pass
        ## What we need:
        # current scene name
        # PATH(abs) projectPath
        # PATH(abs) software database (jsonPath)
        # PATH(abs) current scene file
        # PATH(s)(abs, list) sub-projects

    def createNewProject(self, projectPath):
        pass
        # totally software specific or N/A


    def setProject(self, path):
        pass
        # totally software specific or N/A


    def projectReport(self):
        pass
        ## What we need:
        # PATH(abs) projectPath
        # PATH(abs) software specific Real Scenes Folder Path
        # software project file extensions

    def regularSaveUpdate(self):
        pass
        ## What we need:
        # Results of getSceneInfo

      def saveBaseScene(self, category, userName, baseName, subProject=0, makeReference=True, versionNotes="", *args,
                          **kwargs):
          pass
        ## What we need:
        # current user
        # PATH(abs) projectPath
        # PATH(abs) software database (jsonPath)
        # PATH(abs) software specific Real Scenes Folder Path




