import pymel.core as pm
import json
import os, fnmatch
from shutil import copyfile

class TikManager(dict):
    def __init__(self):
        super(TikManager, self).__init__()
        self.currentProject = pm.workspace(q=1, rd=1)
        self.validCategories = ["Model", "Animation", "Rig", "Shading", "Render", "Other"]
        self.padding = 3

    def dumpJson(self, data,file):
        with open(file, "w") as f:
            json.dump(data, f, indent=4)


    def loadJson(self, file):
        if os.path.isfile(file):
            with open(file, 'r') as f:
                # The JSON module will read our file, and convert it to a python dictionary
                data = json.load(f)
                return data
        else:
            return None


    def folderCheck(self, folder):
        if not os.path.isdir(folder):
            os.makedirs(folder)

    def saveNewScene(self, category, userName, shotName, *args, **kwargs):
        """
        Saves the scene with formatted name and creates a json file for the scene
        Args:
            category: (String) Category if the scene. Valid categories are 'Model', 'Animation', 'Rig', 'Shading', 'Other'
            userName: (String) Predefined user who initiates the process
            shotName: (String) Base name of the scene. Eg. 'Shot01', 'CharacterA', 'BookRig' etc...
            *args: 
            **kwargs: 

        Returns: None

        """

        projectPath = pm.workspace(q=1, rd=1)
        dataPath = os.path.normpath(os.path.join(projectPath, "data"))
        self.folderCheck(dataPath)
        jsonPath = os.path.normpath(os.path.join(dataPath, "json"))
        self.folderCheck(jsonPath)
        jsonCategoryPath = os.path.normpath(os.path.join(jsonPath, category))
        self.folderCheck(jsonCategoryPath)
        scenesPath = os.path.normpath(os.path.join(projectPath, "scenes"))
        self.folderCheck(scenesPath)
        categoryPath = os.path.normpath(os.path.join(scenesPath, category))
        self.folderCheck(category)
        shotPath = os.path.normpath(os.path.join(categoryPath, shotName))
        self.folderCheck(shotPath)

        jsonFile = os.path.join(jsonCategoryPath, "{}.json".format(shotName))

        version=1
        sceneName = "{0}_{1}_{2}_v{3}".format(shotName, category, userName, str(version).zfill(self.padding))
        sceneFile = os.path.join(shotPath, "{0}.mb".format(sceneName))
        pm.saveAs(sceneFile)

        referenceName = "{0}_{1}_forReference".format(shotName, category)
        referenceFile = os.path.join(shotPath, "{0}.mb".format(referenceName))
        copyfile(sceneFile, referenceFile)

        jsonInfo = {}
        jsonInfo["Name"]=shotName
        jsonInfo["Path"]=shotPath
        jsonInfo["Category"]=category
        jsonInfo["Creator"]=userName
        # jsonInfo["CurrentVersion"]=001
        # jsonInfo["LastVersion"] = version
        jsonInfo["ReferencedVersion"]=version
        jsonInfo["Versions"]=[[sceneFile, "Initial Save"]]
        self.dumpJson(jsonInfo, jsonFile)
        print "New Scene Saved as %s" %sceneName

    def saveVersion(self, userName, makeReference=True, versionNotes="", *args, **kwargs):
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

        projectPath = pm.workspace(q=1, rd=1)
        dataPath = os.path.normpath(os.path.join(projectPath, "data"))
        self.folderCheck(dataPath)
        jsonPath = os.path.normpath(os.path.join(dataPath, "json"))
        self.folderCheck(jsonPath)


        ## get the category from the folder
        # first get the parent dir
        shotDirectory = os.path.abspath(os.path.join(pm.sceneName(), os.pardir))
        shotName = os.path.basename(shotDirectory)
        # get the category directory
        categoryDir = os.path.abspath(os.path.join(shotDirectory, os.pardir))
        category = os.path.basename(categoryDir)

        jsonCategoryPath = os.path.normpath(os.path.join(jsonPath, category))
        self.folderCheck(jsonCategoryPath)

        # print shotName, category
        jsonFile = os.path.join(jsonCategoryPath, "{}.json".format(shotName))
        if os.path.isfile(jsonFile):
            jsonInfo = self.loadJson(jsonFile)


            currentVersion = len(jsonInfo["Versions"])+1
            # jsonInfo["LastVersion"] = jsonInfo["LastVersion"] + 1
            sceneName = "{0}_{1}_{2}_v{3}".format(jsonInfo["Name"], jsonInfo["Category"], userName, str(currentVersion).zfill(self.padding))
            sceneFile = os.path.join(jsonInfo["Path"], "{0}.mb".format(sceneName))
            pm.saveAs(sceneFile)
            jsonInfo["Versions"].append([sceneFile, versionNotes])

            if makeReference:
                referenceName = "{0}_{1}_forReference".format(shotName, category)
                referenceFile = os.path.join(jsonInfo["Path"], "{0}.mb".format(referenceName))
                copyfile(sceneFile, referenceFile)
            self.dumpJson(jsonInfo, jsonFile)

    def scanScenes(self, category):
        """
        Scans the folder for json files. Instead of scanning all of the json files at once, It will scan only the target category to speed up the process.
        Args:
            category: (String) This is the category which will be scanned

        Returns: List of all json files in the category

        """
        projectPath = pm.workspace(q=1, rd=1)
        dataPath = os.path.normpath(os.path.join(projectPath, "data"))
        self.folderCheck(dataPath)
        jsonPath = os.path.normpath(os.path.join(dataPath, "json"))
        self.folderCheck(jsonPath)
        jsonCategoryPath = os.path.normpath(os.path.join(jsonPath, category))
        self.folderCheck(jsonCategoryPath)

        allJsonFiles = []
        # niceNames = []
        for file in os.listdir(jsonCategoryPath):
            file=os.path.join(jsonCategoryPath, file)
            allJsonFiles.append(file)
            # niceNames.append(self.pathOps(file, "basename"))
        return allJsonFiles

    def loadScene(self, jsonFile, version=None, force=False):
        """
        Opens the scene with the related json file and given version.
        Args:
            jsonFile: (String) This is the path of the json file which holds the scene properties.
            version: (integer) The version specified in this flag will be loaded. If not specified, last saved version will be used. Default=None
            force: (Boolean) If True, it forces the scene to load LOSING ALL THE UNSAVED CHANGES in the current scene. Default is 'False' 

        Returns: None

        """
        jsonInfo = self.loadJson(jsonFile)
        print jsonInfo["Versions"]
        if not version:
            # print jsonInfo["Versions"]
            sceneFile = jsonInfo["Versions"][-1][0] ## this is the absolute scene path of the last saved version
        else:
            sceneFile = jsonInfo["Versions"][version-1][0] ## this is the absolute scene path of the specified version

        pm.openFile(sceneFile, prompt=False, force=force)


    def pathOps(self, fullPath, mode):
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


