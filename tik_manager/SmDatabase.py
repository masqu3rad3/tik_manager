import json
import os

import datetime

def folderCheck(folder):
    if not os.path.isdir(os.path.normpath(folder)):
        os.makedirs(os.path.normpath(folder))

class SmDatabase(object):
    def __init__(self):
        super(SmDatabase, self).__init__()
        # self.userSettings_Path = os.path.join(os.path.expanduser("~"),"SceneManager")
        # self.project_Path =  os.path.normpath(pm.workspace(q=1, rd=1))
        # self.generalSettings_Path = os.path.dirname(os.path.abspath(__file__))



    def loadJson(self, file):
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

    def dumpJson(self, data, file):
        """
        Saves the data to the json file
        Args:
            data: Data to save
            file: (String) Path to the json file

        Returns: None

        """

        with open(file, "w") as f:
            json.dump(data, f, indent=4)

    def loadDatabaseFiles(self, searchPath):
        """returns all database files in given search path"""
        # allDatabaseFiles = []
        #
        # for file in os.listdir(searchPath)
        #     if file.endswith('.json'):
        #         file = os.path.join(searchPath, file)
        #         allDatabaseFiles.append(file)
        allDatabaseFiles = [os.path.join(searchPath, file) for file in os.listdir(searchPath) if file.endswith('.json')]
        return allDatabaseFiles



    # def loadVersionNotes(self, jsonFile, version=None):
    #     # oldname getVersionNotes
    #     """
    #     Returns: [versionNotes, playBlastDictionary]
    #     """
    #     jsonInfo = self.loadJson(jsonFile)
    #     return jsonInfo["Versions"][version][1], jsonInfo["Versions"][version][4]

    def addVersionNotes(self, additionalNote, jsonFile, version, user):
        jsonInfo = self.loadJson(jsonFile)
        currentNotes = jsonInfo["Versions"][version][1]
        ## add username and date to the beginning of the note:
        now = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M")
        completeNote = "%s\n[%s] on %s\n%s\n" % (currentNotes, user, now, additionalNote)
        jsonInfo["Versions"][version][1] = completeNote
        ##
        self.dumpJson(jsonInfo, jsonFile)

    def loadUsers(self, dbfilePath):
        # old Name
        if not os.path.isfile(dbfilePath):
            userDB = {"Generic": "gn"}
            self.dumpJson(userDB, dbfilePath)
            return userDB
        else:
            userDB = self.loadJson(dbfilePath)
            return userDB

    def addUser(self, fullName, initials):
        # old Name
        currentDB, dbFile = self.loadUsers()
        initialsList = currentDB.values()
        if initials in initialsList:
            msg="Initials are in use"
            print msg
            return -1, msg
        currentDB[fullName] = initials
        self.dumpJson(currentDB, dbFile)
        self.userList = currentDB
        return None, None

    def removeUser(self, fullName):
        # old Name removeUser
        currentDB, dbFile = self.loadUsers()
        del currentDB[fullName]
        self.dumpJson(currentDB, dbFile)
        self.userList = currentDB

    def loadPBSettings(self, pbSettingsFile):
        # old Name getPBsettings

        # pbSettingsFile = os.path.normpath(os.path.join(self.project_Path, "Playblasts", "PBsettings.json"))

        if not os.path.isfile(pbSettingsFile):
            defaultSettings = {"Resolution": (1280, 720),  ## done
                               "Format": 'avi',  ## done
                               "Codec": 'IYUV',  ## done
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
            self.dumpJson(defaultSettings, pbSettingsFile)
            return defaultSettings
        else:
            pbSettings = self.loadJson(pbSettingsFile)
            return pbSettings

    def savePBSettings(self, pbSettingsDict):
        # old Name setPBsettings
        pbSettingsFolder = os.path.normpath(os.path.join(self.project_Path, "Playblasts"))
        folderCheck(pbSettingsFolder)
        pbSettingsFile = os.path.join(pbSettingsFolder, "PBsettings.json")
        self.dumpJson(pbSettingsDict, pbSettingsFile)
        return

    def loadUserPrefs(self, settingsFilePath, firstUser):
        # old Name userPrefLoad

        # settingsFilePath = os.path.join(self.userSettings_Path, "smSettings.json")
        if os.path.isfile(settingsFilePath):
            settingsData = self.loadJson(settingsFilePath)
        else:
            settingsData = {"currentTabIndex": 0, "currentSubIndex": 0, "currentUser": firstUser, "currentMode": False}
            self.dumpJson(settingsData, settingsFilePath)
        return settingsData

    def saveUserPrefs(self, settingsData, settingsFilePath):
        try:
            self.dumpJson(settingsData, settingsFilePath)
            msg = ""
            return 0, msg
        except:
            msg = "Cannot save current settings"
            return -1, msg


    def loadFavorites(self, bookmarksFilePath):
        # old Name userFavoritesLoad
        # bookmarksFilePath = os.path.join(self.userSettings_Path, "smBookmarks.json")
        if os.path.isfile(bookmarksFilePath):
            bookmarksData = self.loadJson(bookmarksFilePath)
        else:
            bookmarksData = []
            self.dumpJson(bookmarksData, bookmarksFilePath)
        return bookmarksData, bookmarksFilePath

    def addToFavorites(self, shortName, absPath, bookmarksFilePath):
        # old Name userFavoritesAdd
        data, filePath = self.loadFavorites(bookmarksFilePath)
        data.append([shortName, absPath])
        self.dumpJson(data, filePath)
        return data

    def removeFromFavorites(self, index, bookmarksFilePath):
        # old Name userFavoritesRemove
        data, filePath = self.loadFavorites(bookmarksFilePath)
        del data[index]
        self.dumpJson(data, filePath)
        return data

    def loadSubprojects(self, subprojectsFilePath):
        if not os.path.isfile(subprojectsFilePath):
            data = ["None"]
            self.dumpJson(data, subprojectsFilePath)
        else:
            data = self.loadJson(subprojectsFilePath)
        return data

    def loadCurrentSceneInfo(self, sceneFile, projectDir, subProjectsList, databaseDir):
        if not sceneFile:
            msg = "This is not a base scene (Untitled)"
            return -1, msg
        sceneDir = os.path.abspath(os.path.join(sceneFile, os.pardir))
        sceneName = os.path.basename(sceneDir)

        upSceneDir = os.path.abspath(os.path.join(sceneDir, os.pardir))
        upScene = os.path.basename(upSceneDir)

        if upScene in subProjectsList:
            subprojectDir = upSceneDir
            subproject = upScene
            categoryDir = os.path.abspath(os.path.join(subprojectDir, os.pardir))
            category = os.path.basename(categoryDir)

            dbCategoryDir = os.path.normpath(os.path.join(databaseDir, category))
            dbPath = os.path.normpath(os.path.join(dbCategoryDir, subproject))

        else:
            subproject = subProjectsList[0] # meaning None
            categoryDir = upSceneDir
            category = upScene
            dbPath = os.path.normpath(os.path.join(databaseDir, category))

        jsonFile = os.path.join(dbPath, "{}.json".format(sceneName))
        if os.path.isfile(jsonFile):
            path, basename = os.path.split(sceneFile)
            filename, ext = os.path.splitext(basename)
            version = filename[-4:]
            return {"jsonFile":jsonFile,
                    "projectPath":projectDir,
                    "subProject":subproject,
                    "category":category,
                    "shotName":sceneName,
                    "version":version
                    }
        else:
            return None

    def loadCategories(self, categoriesFilePath):
        if os.path.isfile(categoriesFilePath):
            categoriesData = self.loadJson(categoriesFilePath)
        else:
            categoriesData = ["Model", "Shading", "Rig", "Layout", "Animation", "Render", "Other"]
            self.dumpJson(categoriesData, categoriesFilePath)
        return categoriesData

    def addCategory(self, newCategory, categoriesFilePath):
        categoryList = self.getCategories(categoriesFilePath)
        categoryList.append(newCategory)
        self.dumpJson(categoryList, categoriesFilePath)
        return categoryList

    def removeCategory(self, categoryIndex, categoriesFilePath):
        categoryList = self.getCategories(categoriesFilePath)
        del categoryList[categoryIndex]
        self.dumpJson(categoryList, categoriesFilePath)
        return categoryList

    def loadPreview(self, sceneDBfile, version,):
        pass

    def addPreview(self):
        pass

    def removePreview(self):
        pass




    def loadCurrentProject(self, currentProjectFile):
        """Function to read the current project setting file.
        Does not apply for Maya since its own project structure has been used"""
        try:
            currentProject = self.loadJson(currentProjectFile)
        except:
            msg = "Cannot load current project file (%s)" %currentProjectFile
            return -1, msg



    def setCurrentProject(self, currentProject, currentProjectFile):
        """Function to read the current project setting file.
        Does not apply for Maya since its own project structure has been used"""
        try:
            self.dumpJson(currentProject, currentProjectFile)
        except:
            msg = "Cannot save current project file (%s)" %currentProjectFile
            return -1, msg


