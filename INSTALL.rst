Installing Scene Manager
=========================

- Put all contents in a network folder where all users can reach.
*eg: M:\Projects\__database\scripts\tik_manager\*

- Add following lines to usersetup.py under scripts folder (Or create the file)
replace 'M://Projects//__database//scripts'

.. code-block::
import os
import sys
import maya.utils
import maya.OpenMaya as OpenMaya

def initFolder(targetFolder):
    if targetFolder in sys.path:
        return
    if not os.path.isdir(targetFolder):
        print ('Path is not valid (%s)' % targetFolder)
    sys.path.append(targetFolder)

def smUpdate(*args):
    import sceneManager
    m = sceneManager.TikManager()
    m.regularSaveUpdate()

initFolder('M://Projects//__database//scripts')
maya.utils.executeDeferred('SMid = OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterSave, smUpdate)')

- Restart Maya
- Run from python commandline:
.. code-block::
from tik_manager import setup