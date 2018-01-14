import pymel.core as pm
import os

class SuManager(object):
    def __init__(self):
        super(SuManager, self).__init__()

    def passwCheck(self, passw):
        # passw = raw_input()
        if passw == "682":
            return True
        else:
            return False

    def rebuildDatabase(self, passw):
        if not self.passwCheck(passw):
            pm.warning ("Incorrect Password")
            return

        # Gather all scene json data





        print "Work In Progress"

    def deleteItem(self, jsonPath, jsonData, passw):
        if not self.passwCheck(passw):
            pm.warning ("Incorrect Password")
            return
        # get the scenePath
        ## delete everything
        for s in jsonData["Versions"]:
            try:
                os.remove(s[0])
            except:
                pass
        if jsonData["ReferenceFile"]:
            try:
                os.remove(jsonData["ReferenceFile"])
            except:
                pass
        try:
            os.rmdir(jsonData["Path"])
        except:
            pass
        try:
            os.remove(jsonPath)
        except:
            pass


