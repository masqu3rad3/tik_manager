import pymel.core as pm


class TikManager(object):
    def __init__(self):
        super(TikManager, self).__init__()
        self.currentProject = pm.workspace(q=1, rd=1)
        self.validCategories = ["model", "animation", "rig", "shading", "render", "other"]

    def saveScene(self, category, user, shotName, mode="newScene"):
        ## if the file is untitled, make sure to save it as a new scene
        if pm.sceneName() == "":
            mode="newScene"
        else:
        ## file is not in the database? (or folder structure) tag it also as a newScene
            ## TODO // Check the file is in the database if true, tag it as

        if mode == "version" or


    def getSceneProperties(self):
        ## check the folder to understand the category
        if not pm.sceneName() == "":
            ## get the category folder somehow



    def loadScene(self):
        pass

    def getScenesInCategory(self, category):
        pass




