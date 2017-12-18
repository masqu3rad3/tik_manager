import pymel.core as pm
import json
import os, fnmatch

class TikManager(dict):
    def __init__(self):
        super(TikManager, self).__init__()
        self.currentProject = pm.workspace(q=1, rd=1)
        self.validCategories = ["model", "animation", "rig", "shading", "render", "other"]

    def saveScene(self, category, user, shotName, mode="newScene"):
        # ## if the file is untitled, make sure to save it as a new scene
        # if pm.sceneName() == "":
        #     mode="newScene"
        # else:
        # ## file is not in the database? (or folder structure) tag it also as a newScene
        #     ## TODO // Check the file is in the database if true, tag it as
        #
        # # if mode == "version" or
        pass


    def getSceneProperties(self, **sceneInfo):

        ## check the folder to understand the category
        if not pm.sceneName() == "":
            pass
            ## get the category folder somehow

        sceneInfo['category'] = ""



    def loadScene(self):
        pass

    def getScenesInCategory(self, category):
        pass

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

    def initSceneDB(self, settingsFile):
        ## create an initial scene database
        initialDB={}
        for category in self.validCategories:
            initialDB[category] = {}
        with open(settingsFile, "w") as f:
            json.dump(initialDB, f, indent=4)

    def addToSceneDB(self, settingsFile, sceneInfo):
        pass

    # def sceneDB(self, data, file, mode):
    #     if mode == "load":
    #         if os.path.isfile(file):
    #             with open(file, 'r') as f:
    #                 # The JSON module will read the file, and convert it to a python dictionary
    #                 data = json.load(f)
    #                 return data
    #         else:
    #             return []
    #
    #     if mode == "add":
    #         currentData = self.database(data, file, mode="load")
    #         currentData.append()



