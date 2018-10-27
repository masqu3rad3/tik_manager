
====================
INSTALL INSTRUCTIONS
====================

AUTOMATIC INSTALLATION (Windows Only)
-------------------------------------

-------
GENERAL
-------
- Put entire tik_manager folder and all of its contents in a network folder where all users can reach.
    ``*eg:: M:\Projects\__database\scripts\*``
- Maya and 3ds Max must run as admin in order to Scene Manager work. Right click on each executable and make sure "Run as Admin" is checked

- (FOR WINDOWS 10 USERS) If a mapped network drive used to share the projects among team members
    (This is the most likely scenario) you need to enable linked connections through registry.
    Simply right click
    enableLinkedConnectionsW10.reg and "merge" to add the key to the registry





MANUAL INSTALLATION
-------------------

-------
GENERAL
-------

* Registry Edit for Linked Connections
    1) In Registry Editor, locate and then click the following registry subkey:
        HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System

    2) Right-click Configuration, click New, and then click DWORD (32-bit) Value.

    3) Name the new registry entry as EnableLinkedConnections.

    4) Double-click the EnableLinkedConnections registry entry.

    5) In the Edit DWORD Value dialog box, type 1 in the Value data field, and then click OK.

    6) Exit Registry Editor, and then restart the computer.



MAYA
----
* Make sure you are executing Maya as administrator
* Add following lines to usersetup.py under scripts folder (Or create the file if it does not exist).
    replace ``M:\\<YOUR>\\<SCRIPTS>\\<PATH>`` with the path of where the tik_manager folder copied

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

    initFolder('M:\\<YOUR>\\<SCRIPTS>\\<PATH>')
    maya.utils.executeDeferred('SMid = OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterSave, smUpdate)')

* Restart Maya
* Run from python commandline:

::

    from tik_manager import mayaSetup


HOUDINI
-------
* Add following lines to 456.py under scripts in HOUDINI_PATH.
    Default Windows location is C:\Program Files\Side Effects Software\<Houdini Version>\houdini\scripts\

    replace ``M:\\<YOUR>\\<SCRIPTS>\\<PATH>`` with the path of where the tik_manager folder copied

::

    import os
    import sys

    def initFolder(targetFolder):
        if targetFolder in sys.path:
            return
        if not os.path.isdir(targetFolder):
            print ('Path is not valid (%s)' % targetFolder)
        sys.path.append(targetFolder)

    initFolder("M:\\<YOUR>\\<SCRIPTS>\\<PATH>")

* Restart Houdini
* Run from python shell:

::

    from tik_manager import houdiniSetup

3DS MAX
-------
*

