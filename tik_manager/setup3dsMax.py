

import os
import sys
import MaxPlus
#
def initFolder(targetFolder, *args):
    if targetFolder in sys.path:
        return
    if not os.path.isdir(targetFolder):
        print ('Path is not valid (%s)' % targetFolder)
    sys.path.append(targetFolder)
#
def smUpdate(*args):
    from tik_manager import Sm3dsMax
    m = Sm3dsMax.MaxManager()
    m.saveCallback()

initFolder("M:\\Projects\\__database\\scripts")
MaxPlus.NotificationManager.Register(14, smUpdate)


/*
macroScript TIK_sceneManager
category: "Tik Works"
tooltip: "Scene Manager"
ButtonText: "Scene Manager"
*/

(
	python.Execute "from tik_manager import Sm3dsMax as man"
	python.Execute "reload(man)"
	python.Execute "r=man.MainUI().show()"
)

