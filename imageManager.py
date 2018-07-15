import pymel.core as pm
import os
import logging
from manager import TikManager
# reload(TikManager)
from manager import pathOps, getPathsFromScene, folderCheck
from manager import loadJson, dumpJson
logging.basicConfig()
logger = logging.getLogger('ImageManager')
logger.setLevel(logging.DEBUG)

def parseTemplate(template):
    pass


class ImageManager(TikManager):
    def __init__(self):
        super(ImageManager, self).__init__()
        self.sceneInfo = self.getSceneInfo()

        if not self.sceneInfo:
            logger.warning("This is not a base scene (Untitled)")
            return
        if not self.sceneInfo["category"] == "Render":
            logger.warning("Base Scene must be under Render Category")
            print "AMAM", self.sceneInfo["category"]
            return
        # logger.info(self.resolveImageName())
        self.shotImgDir = self.resolveImageName()



    def resolveImageName(self):

        #get the images folder
        sceneVersion = pathOps(pm.sceneName(), "filename")[-4:]
        projectImgDir = os.path.join(self.sceneInfo["projectPath"], "images")

        if self.sceneInfo["subProject"] != "None":
            shotImgDir = os.path.join(projectImgDir, self.sceneInfo["subProject"], self.sceneInfo["shotName"])
        else:
            shotImgDir = os.path.join(projectImgDir, self.sceneInfo["shotName"])

        folderCheck(shotImgDir ) # folder check creates the directory if it does not (or they dont) exist

        resolvedName = "{0}/{1}/<RenderLayer>/{2}_{1}".format(shotImgDir, sceneVersion, self.sceneInfo["shotName"])

        # curRenderer = pm.getAttr('defaultRenderGlobals.currentRenderer')
        # if curRenderer == "arnold":
        #     pass
        # if curRenderer == "vray":
        #     pass
        # if curRenderer == "mentalRay":
        #     pass
        # if curRenderer == "redshift":
        #     pass

        pm.setAttr("defaultRenderGlobals.imageFilePrefix", resolvedName)
        return shotImgDir


