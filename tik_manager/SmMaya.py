import os
import SmRoot
reload(SmRoot)
from SmRoot import RootManager

import maya.cmds as cmds
import maya.mel as mel

class MayaManager(RootManager):
    def __init__(self):
        super(MayaManager, self).__init__()
        self.init_paths()
        self.init_database()
        # self.backwardcompatibility() # DO NOT RUN UNTIL RELEASE

    def getProjectDir(self):
        p_path = cmds.workspace(q=1, rd=1)
        norm_p_path = os.path.normpath(p_path)
        return norm_p_path
    def getSceneFile(self):
        s_path = cmds.file(q=True, sn=True)
        norm_s_path = os.path.normpath(s_path)
        return norm_s_path

    def set_project(self, path):
        # totally software specific or N/A
        melCompPath = path.replace("\\", "/") # mel is picky
        command = 'setProject "%s";' %melCompPath
        mel.eval(command)
        self.projectDir = cmds.workspace(q=1, rd=1)

    def saveCallback(self):
        pass

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

    def loadBasescene(self):
        pass

    def loadReference(self):
        pass

    def createThumbnail(self):
        pass

    def replaceThumbnail(self):
        pass

