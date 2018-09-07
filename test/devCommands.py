

delModules=["tik_manager", "tik_manager.manager", "tik_manager.imageManager", "tik_manager.imageViewer", "tik_manager.__init__", "tik_manager._version"]
import sys
for i in delModules:
    try:
        toDel = str(sys.modules[i])
        del sys.modules[i]
        print "{0} removed from memory".format(toDel)
    except KeyError:
        pass

from tik_manager import manager
reload(manager)
# manager.MainUI().saveAsVersionDialog()
tik_sceneManager = manager.MainUI(scriptJob="tik_sceneManager")
tik_sceneManager.show()

from tik_manager import imageManager
reload(imageManager)
tik_imageManager = imageManager.MainUI(scriptJob="tik_imageManager")

from tik_manager import imageViewer
reload(imageViewer)
tik_imageViewer = imageViewer.MainUI().show()