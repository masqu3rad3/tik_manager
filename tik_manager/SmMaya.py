
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
        self.backwardcompatibility()

    def get_currentProjectDir(self):
        return (cmds.workspace(q=1, rd=1))
    def get_currentSceneFile(self):
        return (cmds.file(q=True, sn=True))

    def set_project(self, path):
        # totally software specific or N/A
        melCompPath = path.replace("\\", "/") # mel is picky
        command = 'setProject "%s";' %melCompPath
        mel.eval(command)
        self.projectDir = cmds.workspace(q=1, rd=1)


