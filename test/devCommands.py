

delModules=["tik_manager", "tik_manager.manager", "tik_manager.imageManager", "tik_manager.imageViewer", "tik_manager.__init__"]
import sys
for i in delModules:
    try:
        del sys.modules[i]
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