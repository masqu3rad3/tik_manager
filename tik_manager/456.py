# Houdini Startup Script

import os
import sys

def initFolder(targetFolder):
    if targetFolder in sys.path:
        return
    if not os.path.isdir(targetFolder):
        print ('Path is not valid (%s)' % targetFolder)
    sys.path.append(targetFolder)

initFolder("M:\\Projects\\__database\\scripts")

