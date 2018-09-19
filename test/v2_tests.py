
import maya.standalone
maya.standalone.initialize()
from tik_manager import SmMaya

e = SmMaya.MayaManager()

print e.projectDir


print e.currentBaseSceneName