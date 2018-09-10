Installing Scene Manager
========================

* Put all tik_manager folder and all of its contents in a network folder where all users can reach.
    ``*eg:: M:\Projects\__database\scripts\*``
* Add following lines to usersetup.py under scripts folder (Or create the file).
    replace ``M://Projects//__database//scripts`` with the path of where the tik_manager folder copied

::

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
        from tik_manager import manager
        m = manager.TikManager()
        m.regularSaveUpdate()

    initFolder('M://Projects//__database//scripts')
    maya.utils.executeDeferred('SMid = OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterSave, smUpdate)')

* Restart Maya
* Run from python commandline:

::

    from tik_manager import setup
