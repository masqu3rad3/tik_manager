# version 1.2

# version 1.2 changes:
# fixed the loading and referencing system. Now it checks for the selected rows 'name' not the list number id.
# fixed the name check for duplicate base scenes. It doesnt allow creating base scenes with the same name disregarding it
    # has lower case or upper case characters.

# version 1.1 changes:
# "Frame Range" Hud option is added to playblast settings.
# In "Reference Mode" Scene List highlighted with red border for visual reference.

# version 1.0 initial

import pymel.core as pm
import json
import os, fnmatch
from shutil import copyfile
import maya.mel as mel
import maya.cmds as cmds
import socket
import filecmp
import re
import suMod
import ctypes
reload(suMod)
import unicodedata
import pprint



#### Import for UI
import Qt
from Qt import QtWidgets, QtCore, QtGui
from maya import OpenMayaUI as omui

if Qt.__binding__ == "PySide":
    from shiboken import wrapInstance
    from Qt.QtCore import Signal
elif Qt.__binding__.startswith('PyQt'):
    from sip import wrapinstance as wrapInstance
    from Qt.Core import pyqtSignal as Signal
else:
    from shiboken2 import wrapInstance
    from Qt.QtCore import Signal

def getOldestFile(rootfolder, extension=".avi"):
    return min(
        (os.path.join(dirname, filename)
        for dirname, dirnames, filenames in os.walk(rootfolder)
        for filename in filenames
        if filename.endswith(extension)),
        key=lambda fn: os.stat(fn).st_mtime)
def getNewestFile(rootfolder, extension=".avi"):
    return max(
        (os.path.join(dirname, filename)
        for dirname, dirnames, filenames in os.walk(rootfolder)
        for filename in filenames
        if filename.endswith(extension)),
        key=lambda fn: os.stat(fn).st_mtime)

def killTurtle():
    # print "turtle sikici"
    if pm.ls('TurtleDefaultBakeLayer'):
        pm.lockNode('TurtleDefaultBakeLayer', lock=False)
        pm.delete('TurtleDefaultBakeLayer')
        # print "Turtle anani sikim"

def checkAdminRights():
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin

def getMayaMainWindow():
    """
    Gets the memory adress of the main window to connect Qt dialog to it.
    Returns:
        (long) Memory Adress
    """
    win = omui.MQtUtil_mainWindow()
    ptr = wrapInstance(long(win), QtWidgets.QMainWindow)
    return ptr

def folderCheck(folder):
    if not os.path.isdir(os.path.normpath(folder)):
        os.makedirs(os.path.normpath(folder))

def loadJson(file):
    if os.path.isfile(file):
        with open(file, 'r') as f:
            # The JSON module will read our file, and convert it to a python dictionary
            data = json.load(f)
            return data
    else:
        return None

def dumpJson(data, file):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

def nameCheck(text):

    if re.match("^[A-Za-z0-9_-]*$", text):
        if text == "":
            return -1
        text = text.replace(" ", "_")
        return text
    else:
        return -1


def pathOps(fullPath, mode):
    """
    performs basic path operations.
    Args:
        fullPath: (Unicode) Absolute Path
        mode: (String) Valid modes are 'path', 'basename', 'filename', 'extension', 'drive'

    Returns:
        Unicode

    """

    if mode == "drive":
        drive = os.path.splitdrive(fullPath)
        return drive

    path, basename = os.path.split(fullPath)
    if mode == "path":
        return path
    if mode == "basename":
        return basename
    filename, ext = os.path.splitext(basename)
    if mode == "filename":
        return filename
    if mode == "extension":
        return ext

def getPathsFromScene(*args, **kwargs):

    projectPath = os.path.normpath(pm.workspace(q=1, rd=1))
    dataPath = os.path.normpath(os.path.join(projectPath, "data"))
    folderCheck(dataPath)
    jsonPath = os.path.normpath(os.path.join(dataPath, "SMdata"))
    folderCheck(jsonPath)
    scenesPath = os.path.normpath(os.path.join(projectPath, "scenes"))
    folderCheck(scenesPath)
    playBlastRoot = os.path.normpath(os.path.join(projectPath, "Playblasts"))
    folderCheck(playBlastRoot)
    returnList = []
    for i in args:
        if i == "projectPath":
            returnList.append(projectPath)
        if i== "dataPath":
            returnList.append(dataPath)
        if i=="jsonPath":
            returnList.append(jsonPath)
        if i=="scenesPath":
            returnList.append(scenesPath)
        if i=="playBlastRoot":
            returnList.append(playBlastRoot)
    if len(returnList)<2:
        returnList = returnList[0]
    return returnList

class TikManager(object):
    def __init__(self):
        super(TikManager, self).__init__()
        self.currentProject = pm.workspace(q=1, rd=1)
        self.currentSubProjectIndex = 0

        self.userDB = "M://Projects//__database//sceneManagerUsers.json"
        if os.path.isfile(self.userDB):
            self.userList = loadJson(self.userDB)
        else:
            self.userList = {"Generic":"gn"}
        self.validCategories = ["Model", "Shading", "Rig", "Layout", "Animation", "Render", "Other"]
        self.padding = 3
        self.subProjectList = self.scanSubProjects()



    def projectReport(self):

        # // TODO Create a through REPORT
        projectPath, dataPath, jsonPath, scenesPath, playBlastRoot = getPathsFromScene("projectPath", "dataPath", "jsonPath", "scenesPath", "playBlastRoot")
        # get All json files:
        oldestFile = getOldestFile(scenesPath, extension=(".mb", ".ma"))
        oldestTime = os.stat(oldestFile).st_mtime
        newestFile = getNewestFile(scenesPath, extension=(".mb", ".ma"))
        newestTime = os.stat(newestFile ).st_mtime

        L1 = "Oldest Scene file {0} created at {1}".format (oldestFile, oldestTime)
        L2 = "Newest Scene file {0} created at {1}".format (newestFile, newestTime)

        report = {}
        for subP in range (len(self.subProjectList)):
            subReport={}
            for category in self.validCategories:
                categoryItems=(self.scanScenes(category, subProjectAs=subP)[0])
                categoryItems = [x for x in categoryItems if x != []]
                subReport[category]=categoryItems
            # allItems.append(categoryItems)
            report[self.subProjectList[subP]]=subReport

        # L3 = "There are total {0} Base Scenes in {1} Categories and {2} Sub-Projects".format
        pprint.pprint(report)
        return report

    def saveNewScene(self, category, userName, baseName, subProject=0, makeReference=True, versionNotes="", *args, **kwargs):
        """
        Saves the scene with formatted name and creates a json file for the scene
        Args:
            category: (String) Category if the scene. Valid categories are 'Model', 'Animation', 'Rig', 'Shading', 'Other'
            userName: (String) Predefined user who initiates the process
            baseName: (String) Base name of the scene. Eg. 'Shot01', 'CharacterA', 'BookRig' etc...
            subProject: (Integer) The scene will be saved under the sub-project according to the given integer value. The 'self.subProjectList' will be
                searched with that integer.
            makeReference: (Boolean) If set True, a copy of the scene will be saved as forReference
            versionNotes: (String) This string will be stored in the json file as version notes.
            *args: 
            **kwargs: 

        Returns: None

        """

        scenesToCheck = self.scanScenes(category, subProjectAs=subProject)[0]
        for z in scenesToCheck:
            if baseName.lower() == loadJson(z)["Name"].lower():
                pm.warning("Choose an unique name")
                return -1

        projectPath, jsonPath, scenesPath = getPathsFromScene("projectPath", "jsonPath", "scenesPath")
        categoryPath = os.path.normpath(os.path.join(scenesPath, category))
        folderCheck(category)

        ## eger subproject olarak kaydedilecekse
        if not subProject == 0:
            subProjectPath = os.path.normpath(os.path.join(categoryPath, self.subProjectList[subProject]))
            folderCheck(subProjectPath)
            shotPath = os.path.normpath(os.path.join(subProjectPath, baseName))
            folderCheck(shotPath)

            jsonCategoryPath = os.path.normpath(os.path.join(jsonPath, category))
            folderCheck(jsonCategoryPath)
            jsonCategorySubPath = os.path.normpath(os.path.join(jsonCategoryPath, self.subProjectList[subProject]))
            folderCheck(jsonCategorySubPath)
            jsonFile = os.path.join(jsonCategorySubPath, "{}.json".format(baseName))
        else:
            shotPath = os.path.normpath(os.path.join(categoryPath, baseName))
            folderCheck(shotPath)

            jsonCategoryPath = os.path.normpath(os.path.join(jsonPath, category))
            folderCheck(jsonCategoryPath)
            jsonFile = os.path.join(jsonCategoryPath, "{}.json".format(baseName))

        version=1
        sceneName = "{0}_{1}_{2}_v{3}".format(baseName, category, userName, str(version).zfill(self.padding))
        sceneFile = os.path.join(shotPath, "{0}.mb".format(sceneName))
        ## relativity update
        relSceneFile = os.path.relpath(sceneFile, start=projectPath)
        killTurtle()
        pm.saveAs(sceneFile)

        jsonInfo = {}

        if makeReference:
            referenceName = "{0}_{1}_forReference".format(baseName, category)
            referenceFile = os.path.join(shotPath, "{0}.mb".format(referenceName))
            ## relativity update
            relReferenceFile = os.path.relpath(referenceFile, start=projectPath)
            copyfile(sceneFile, referenceFile)
            jsonInfo["ReferenceFile"] = relReferenceFile
            jsonInfo["ReferencedVersion"] = version
        else:
            jsonInfo["ReferenceFile"] = None
            jsonInfo["ReferencedVersion"] = None

        jsonInfo["ID"]="SceneManagerV01_sceneFile"
        jsonInfo["MayaVersion"]=pm.versions.current()
        jsonInfo["Name"]=baseName
        jsonInfo["Path"]=os.path.relpath(shotPath, start=projectPath)
        jsonInfo["Category"]=category
        jsonInfo["Creator"]=userName
        jsonInfo["CreatorHost"]=(socket.gethostname())
        jsonInfo["Versions"]=[[relSceneFile, versionNotes, userName, socket.gethostname(), {}]] ## last item is for playplast
        dumpJson(jsonInfo, jsonFile)
        return relSceneFile

    def saveVersion(self, userName, makeReference=True, versionNotes="", *args, **kwargs):
        """
        Saves a version for the predefined scene. The scene json file must be present at the /data/[Category] folder.
        Args:
            userName: (String) Predefined user who initiates the process
            makeReference: (Boolean) If set True, make a copy of the forReference file. There can be only one 'forReference' file for each scene
            versionNotes: (String) This string will be hold in the json file as well. Notes about the changes in the version.
            *args: 
            **kwargs: 

        Returns: None

        """

        sceneName = pm.sceneName()
        if not sceneName:
            pm.warning("This is not a base scene (Untitled)")
            return -1

        projectPath, jsonPath = getPathsFromScene("projectPath", "jsonPath")

        # first get the parent dir
        shotDirectory = os.path.abspath(os.path.join(pm.sceneName(), os.pardir))
        shotName = os.path.basename(shotDirectory)

        upperShotDir = os.path.abspath(os.path.join(shotDirectory, os.pardir))
        upperShot = os.path.basename(upperShotDir)


        if upperShot in self.subProjectList:
            subProjectDir= upperShotDir
            subProject = upperShot
            categoryDir = os.path.abspath(os.path.join(subProjectDir, os.pardir))
            category = os.path.basename(categoryDir)

            jsonCategoryPath = os.path.normpath(os.path.join(jsonPath, category))
            folderCheck(jsonCategoryPath)
            jsonPath = os.path.normpath(os.path.join(jsonCategoryPath, subProject))
            folderCheck(jsonPath)

        else:
            categoryDir = upperShotDir
            category = upperShot
            jsonPath = os.path.normpath(os.path.join(jsonPath, category))
            folderCheck(jsonPath)

        jsonFile = os.path.join(jsonPath, "{}.json".format(shotName))

        if os.path.isfile(jsonFile):
            jsonInfo = loadJson(jsonFile)

            currentVersion = len(jsonInfo["Versions"])+1
            sceneName = "{0}_{1}_{2}_v{3}".format(jsonInfo["Name"], jsonInfo["Category"], userName, str(currentVersion).zfill(self.padding))
            relSceneFile = os.path.join(jsonInfo["Path"], "{0}.mb".format(sceneName))

            sceneFile = os.path.join(projectPath, relSceneFile)

            killTurtle()
            pm.saveAs(sceneFile)
            jsonInfo["Versions"].append([relSceneFile, versionNotes, userName, (socket.gethostname()), {}]) ## last one is for playblast

            if makeReference:
                referenceName = "{0}_{1}_forReference".format(shotName, category)
                relReferenceFile = os.path.join(jsonInfo["Path"], "{0}.mb".format(referenceName))
                # referenceFile = "%s%s" %(projectPath, relReferenceFile)
                referenceFile = os.path.join(projectPath, relReferenceFile)

                copyfile(sceneFile, referenceFile)
                jsonInfo["ReferenceFile"] = relReferenceFile
                jsonInfo["ReferencedVersion"] = currentVersion
            dumpJson(jsonInfo, jsonFile)
        else:
            pm.warning("This is not a base scene (Json file cannot be found)")
            return -1
        return relSceneFile

    def getPBsettings(self):

        ## TODO / WIP

        projectPath, playBlastRoot = getPathsFromScene("projectPath","playBlastRoot")

        pbSettingsFile = "{0}\\PBsettings.json".format(os.path.join(projectPath, playBlastRoot))

        if not os.path.isfile(pbSettingsFile):
            defaultSettings={"Resolution":(1280,720), ## done
                             "Format":'avi', ## done
                             "Codec":'IYUV', ## done
                             "Percent":100, ## done
                             "Quality":100, ## done
                             "ShowFrameNumber":True,
                             "ShowSceneName":False,
                             "ShowCategory":False,
                             "ShowFrameRange":True,
                             "ShowFPS":True,
                             "PolygonOnly":True, ## done
                             "ShowGrid": False, ## done
                             "ClearSelection": True, ## done
                             "DisplayTextures": True ## done
            }
            dumpJson(defaultSettings, pbSettingsFile)
            return defaultSettings
        else:
            pbSettings = loadJson(pbSettingsFile)
            return pbSettings

    def createPlayblast(self, *args, **kwargs):

        pbSettings = self.getPBsettings()

        # Quicktime format is missing the final frame all the time. Add an extra frame to compansate
        if pbSettings["Format"] == 'qt':
            maxTime = pm.playbackOptions(q=True, maxTime=True)
            endTime = pm.playbackOptions(q=True, animationEndTime=True)
            pm.playbackOptions(maxTime=maxTime+1)
            pm.playbackOptions(animationEndTime=endTime+1)

        sceneName = pm.sceneName()
        if not sceneName:
            pm.warning("This is not a base scene. Scene must be saved as a base scene before playblasting.")
            return -1

        projectPath, jsonPath, playBlastRoot = getPathsFromScene("projectPath", "jsonPath", "playBlastRoot")

        # first get the parent dir
        shotDirectory = os.path.abspath(os.path.join(pm.sceneName(), os.pardir))
        shotName = os.path.basename(shotDirectory)

        upperShotDir = os.path.abspath(os.path.join(shotDirectory, os.pardir))
        upperShot = os.path.basename(upperShotDir)


        if upperShot in self.subProjectList:
            subProjectDir= upperShotDir
            subProject = upperShot
            categoryDir = os.path.abspath(os.path.join(subProjectDir, os.pardir))
            category = os.path.basename(categoryDir)

            jsonCategoryPath = os.path.normpath(os.path.join(jsonPath, category))
            folderCheck(jsonCategoryPath)
            jsonPath = os.path.normpath(os.path.join(jsonCategoryPath, subProject))
            folderCheck(jsonPath)

            pbCategoryPath = os.path.normpath(os.path.join(playBlastRoot, category))
            folderCheck(pbCategoryPath)
            pbSubPath = os.path.normpath(os.path.join(pbCategoryPath, subProject))
            folderCheck(pbSubPath)
            pbPath = os.path.normpath(os.path.join(pbSubPath, shotName))
            folderCheck(pbPath)

        else:
            # categoryDir = upperShotDir
            category = upperShot
            jsonPath = os.path.normpath(os.path.join(jsonPath, category))
            folderCheck(jsonPath)
            pbCategoryPath = os.path.normpath(os.path.join(playBlastRoot, category))
            folderCheck(pbCategoryPath)
            pbPath = os.path.normpath(os.path.join(pbCategoryPath, shotName))
            folderCheck(pbPath)

        jsonFile = os.path.join(jsonPath, "{}.json".format(shotName))

        if os.path.isfile(jsonFile):

            selection = pm.ls(sl=True)
            pm.select(d=pbSettings["ClearSelection"])
            jsonInfo = loadJson(jsonFile)

            currentCam = pm.modelPanel(pm.getPanel(wf=True), q=True, cam=True)

            versionName = pm.sceneName()
            relVersionName = os.path.relpath(versionName, start=projectPath)
            playBlastFile = os.path.join(pbPath, "{0}_{1}_PB.avi".format (pathOps(versionName, mode="filename"), currentCam))
            relPlayBlastFile = os.path.relpath(playBlastFile, start=projectPath)

            if os.path.isfile(playBlastFile):
                try:
                    os.remove(playBlastFile)
                except WindowsError:
                    pm.warning("The file is open somewhere else")
                    return -1




            ## CREATE A CUSTOM PANEL WITH DESIRED SETTINGS

            tempWindow = pm.window(title="SM_Playblast", widthHeight=(pbSettings["Resolution"][0]*1.1,pbSettings["Resolution"][1]*1.1), tlc=(0,0))
            # panel = pm.getPanel(wf=True)

            pm.paneLayout()

            pbPanel = pm.modelPanel(camera=currentCam)
            pm.showWindow(tempWindow)
            pm.setFocus(pbPanel)

            pm.modelEditor(pbPanel, e=1,
                           allObjects=not pbSettings["PolygonOnly"],
                           da="smoothShaded",
                           displayTextures=pbSettings["DisplayTextures"],
                           wireframeOnShaded=False,
                           grid=pbSettings["ShowGrid"],
                           polymeshes=True,
                           hud=True
                           )

            pm.camera(currentCam, e=True, overscan=True, displayFilmGate=False, displayResolution=False)

            ## TODO // Prepare the scene and hud interface before

            ## get previous HUD States and turn them all off
            hudPreStates = {}
            HUDS = pm.headsUpDisplay(lh=True)
            for hud in HUDS:
                hudPreStates[hud] = pm.headsUpDisplay(hud, q=True, vis=True)
                pm.headsUpDisplay(hud, e=True, vis=False)

            ## clear the custom HUDS
            customHuds=['SMFrame', 'SMScene', 'SMCategory', 'SMFPS', 'SMCameraName']
            for hud in customHuds:
                if pm.headsUpDisplay(hud, ex=True):
                    pm.headsUpDisplay(hud, rem=True)

            if pbSettings["ShowFrameNumber"]:
                freeBl = pm.headsUpDisplay(nfb=5) ## this is the next free block on section 5
                pm.headsUpDisplay('SMFrame', s=5, b=freeBl, label="Frame", preset="currentFrame", dfs="large", lfs="large")
            if pbSettings["ShowSceneName"]:
                freeBl = pm.headsUpDisplay(nfb=5) ## this is the next free block on section 5
                pm.headsUpDisplay('SMScene', s=5, b=freeBl, label="Scene: %s"%(pathOps(versionName, mode="filename")), lfs="large")
            if pbSettings["ShowCategory"]:
                freeBl = pm.headsUpDisplay(nfb=5)  ## this is the next free block on section 5
                pm.headsUpDisplay('SMCategory', s=5, b=freeBl, label="Category: %s"%(jsonInfo["Category"]), lfs="large")
            if pbSettings["ShowFPS"]:
                freeBl = pm.headsUpDisplay(nfb=5)  ## this is the next free block on section 5
                pm.headsUpDisplay('SMFPS', s=5, b=freeBl, label="Time Unit: %s" % (pm.currentUnit(q=True, time=True)), lfs="large")

            # v1.1 SPECIFIC
            try:
                if pbSettings["ShowFrameRange"]:
                    freeBl = pm.headsUpDisplay(nfb=5)  ## this is the next free block on section 5
                    pm.headsUpDisplay('SMFrange', s=5, b=freeBl, label="Frame Range: {} - {}".format(int(pm.playbackOptions(q=True, minTime=True)), int(pm.playbackOptions(q=True, maxTime=True))), lfs="large")
            except KeyError:
                pass

            pm.headsUpDisplay('SMCameraName', s=2, b=2, ba='center', dw=50, pre='cameraNames')

            ## Check here: http://download.autodesk.com/us/maya/2011help/pymel/generated/functions/pymel.core.windows/pymel.core.windows.headsUpDisplay.html
            pm.playblast(format=pbSettings["Format"],
                         filename=playBlastFile,
                         widthHeight=pbSettings["Resolution"],
                         percent=pbSettings["Percent"],
                         quality=pbSettings["Quality"],
                         compression=pbSettings["Codec"],
                         forceOverwrite=True)
            ## remove window when pb is donw
            pm.deleteUI(tempWindow)

            # Get back to the original frame range if the codec is Quick Time
            if pbSettings["Format"] == 'qt':
                pm.playbackOptions(maxTime=maxTime)
                pm.playbackOptions(animationEndTime=endTime)

            ## remove the custom HUdS
            if pbSettings["ShowFrameNumber"]:
                pm.headsUpDisplay('SMFrame', rem=True)
            if pbSettings["ShowSceneName"]:
                pm.headsUpDisplay('SMScene', rem=True)
            if pbSettings["ShowCategory"]:
                pm.headsUpDisplay('SMCategory', rem=True)
            if pbSettings["ShowFPS"]:
                pm.headsUpDisplay('SMFPS', rem=True)
            try:
                if pbSettings["ShowFrameRange"]:
                    pm.headsUpDisplay('SMFrange', rem=True)
            except KeyError:
                pass

            pm.headsUpDisplay('SMCameraName', rem=True)

            ## get back the previous state of HUDS
            for hud in hudPreStates.keys():
                pm.headsUpDisplay(hud, e=True, vis=hudPreStates[hud])

            pm.select(selection)
            ## find this version in the json data
            for i in jsonInfo["Versions"]:
                if relVersionName == i[0]:
                    i[4][currentCam]=relPlayBlastFile

            dumpJson(jsonInfo, jsonFile)
        else:
            pm.warning("This is not a base scene (Json file cannot be found)")
            return -1

        #######

    def playPlayblast(self, relativePath):
        projectPath = getPathsFromScene("projectPath")

        PBfile = os.path.join(projectPath, relativePath)
        os.startfile(PBfile)

    def createSubProject(self, nameOfSubProject):
        if (nameOfSubProject.lower()) == "none":
            pm.warning("Naming mismatch")
            return None
        projectPath, jsonPath = getPathsFromScene("projectPath", "jsonPath")
        subPjson = os.path.normpath(os.path.join(jsonPath, "subPdata.json"))
        subInfo = []
        if os.path.isfile(subPjson):
            subInfo= loadJson(subPjson)

        subInfo.append(nameOfSubProject)
        self.currentSubProjectIndex = len(subInfo) - 1 ## make the current sub project index the new created one.
        dumpJson(subInfo, subPjson)
        return subInfo

    def scanSubProjects(self):
        projectPath, jsonPath = getPathsFromScene("projectPath", "jsonPath")
        subPjson = os.path.normpath(os.path.join(jsonPath, "subPdata.json"))
        if not os.path.isfile(subPjson):
            subInfo = ["None"]
            dumpJson(subInfo, subPjson)

        else:
            subInfo=loadJson(subPjson)
        return subInfo

    # def renameScene(self, jsonFile, newName, version=None):
    #
    #     projectPath = getPathsFromScene("projectPath")
    #     jsonInfo = loadJson(jsonFile)
    #     category = jsonInfo["Category"]
    #
    #     # PSUEDO CODE:
    #
    #     # subproject = get the scenes sub-project
    #
    #     versionCount = 0
    #     for version in jsonInfo["Versions"]:
    #         versionCount += 1
    #         rel_scene_file = version[0]
    #         scene_file = os.path.join(projectPath, rel_scene_file)
    #
    #         newSceneName = "{0}_{1}_{2}_v{3}".format(newName, category, version[2], str(versionCount).zfill(self.padding))
    #
    #
    #         # Change the name of the actual file
    #
    #         # Update the jsonInfo with the me
    #             # for pb in all playblasts in this version
    #                 # Change the name of the playblast
    #
    # def moveToSubProject(self, newSubproject):
    #     # // TODO write subproject moving method
    #     pass




        # relSceneFile = jsonInfo["Versions"][version][0] ## this is the relative scene path of the specified version
        # sceneFile = os.path.join(projectPath, relSceneFile)
        #
        # # check name for duplicate
        # scenesToCheck = self.scanScenes(jsonInfo["Category"], subProjectAs=subProject)[0]
        # for z in scenesToCheck:
        #     if newName == loadJson(z)["Name"]:
        #         pm.warning("Choose an unique name")
        #         return -1
        #
        # # check name for invalid characters
        # if nameCheck(newName) == -1:
        #     pm.warning("Give a unique and proper name with latin characters, without spaces")
        #     return -1

    # // TODO // Create a method to delete playblasts (or change the playblast load method with scanning directories)

    def scanScenes(self, category, subProjectAs=None):
        """
        Scans the folder for json files. Instead of scanning all of the json files at once, It will scan only the target category to speed up the process.
        Args:
            category: (String) This is the category which will be scanned
            subProjectAs: (String / None) If a sub project is given Scans the given sub project. If None, it scans the current sub-project
                declared the classes 'currentSubProjectIndex' variable. Default = None

        Returns: List of all json files in the category, sub-project json file

        """
        if not subProjectAs == None:
            subProjectIndex = subProjectAs
        else:
            subProjectIndex = self.currentSubProjectIndex
        projectPath, jsonPath = getPathsFromScene("projectPath", "jsonPath")

        subPjson = os.path.normpath(os.path.join(jsonPath, "subPdata.json"))
        if not os.path.isfile(subPjson):
            dumpJson(["None"], subPjson)
        # eger subproject olarak aranilacaksa
        if not (subProjectIndex == 0):
            jsonCategoryPath = os.path.normpath(os.path.join(jsonPath, category))
            folderCheck(jsonCategoryPath)

            jsonCategorySubPath = os.path.normpath(os.path.join(jsonCategoryPath, (self.subProjectList)[subProjectIndex]))

            folderCheck(jsonCategorySubPath)
            searchFolder = jsonCategorySubPath
        else:
            jsonCategoryPath = os.path.normpath(os.path.join(jsonPath, category))
            folderCheck(jsonCategoryPath)
            searchFolder = jsonCategoryPath

        allJsonFiles = []
        # niceNames = []
        for file in os.listdir(searchFolder):
            if file.endswith('.json'):
                file=os.path.join(searchFolder, file)
                allJsonFiles.append(file)
        return allJsonFiles, subPjson

    def loadScene(self, jsonFile, version=None, force=False, importFile=False):
        """
        Opens the scene with the related json file and given version.
        Args:
            jsonFile: (String) This is the path of the json file which holds the scene properties.
            version: (integer) The version specified in this flag will be loaded. If not specified, last saved version will be used. Default=None
            force: (Boolean) If True, it forces the scene to load LOSING ALL THE UNSAVED CHANGES in the current scene. Default is 'False' 
            importFile: (Boolean) If True, it imports the file instead of opening it.

        Returns: None

        """
        projectPath = getPathsFromScene("projectPath")
        jsonInfo = loadJson(jsonFile)
        relSceneFile = jsonInfo["Versions"][version][0] ## this is the relative scene path of the specified version
        sceneFile = os.path.join(projectPath, relSceneFile)

        if os.path.isfile(sceneFile):
            if importFile:
                cmds.file(sceneFile, i=True, force=force)
            else:
                cmds.file(sceneFile, o=True, force=force)
        else:
            pm.error("File in Scene Manager database doesnt exist")

    def makeReference(self, jsonFile, version):
        """
        Makes the given version valid reference file. Basically it copies that file and names it as <Shot Name>_forReference.mb.
        There can be only one reference file for one scene. If there is another reference file it will be written on. Since Reference files
        are duplicates of a version in the folder, it is safe to do that.
        Args:
            jsonFile: (String) Path to the json file which holds the information about the scene
            version: (Integer) Version number of the scene which will be copied as reference file.

        Returns: None

        """

        # projectPath = pm.workspace(q=1, rd=1)
        projectPath = getPathsFromScene("projectPath")
        jsonInfo = loadJson(jsonFile)

        if version == 0 or version > len(jsonInfo["Versions"]):
            pm.error("version number mismatch - (makeReference method)")
            return
        relSceneFile = jsonInfo["Versions"][version-1][0]

        # sceneFile = "%s%s" %(projectPath, relSceneFile)
        sceneFile = os.path.join(projectPath, relSceneFile)
        referenceName = "{0}_{1}_forReference".format(jsonInfo["Name"], jsonInfo["Category"])
        relReferenceFile = os.path.join(jsonInfo["Path"], "{0}.mb".format(referenceName))
        # referenceFile = "%s%s" %(projectPath, relReferenceFile)
        referenceFile = os.path.join(projectPath, relReferenceFile)
        copyfile(sceneFile, referenceFile)
        jsonInfo["ReferenceFile"] = relReferenceFile
        jsonInfo["ReferencedVersion"] = version

        dumpJson(jsonInfo, jsonFile)

    def loadReference(self, jsonFile):
        projectPath = getPathsFromScene("projectPath")
        jsonInfo = loadJson(jsonFile)
        relReferenceFile = jsonInfo["ReferenceFile"]

        # os.path.isfile(referenceFile)
        if relReferenceFile:
            # referenceFile = "%s%s" % (projectPath, relReferenceFile)
            referenceFile = os.path.join(projectPath, relReferenceFile)
            # pm.FileReference(referenceFile)
            cmds.file(os.path.normpath(referenceFile), reference=True)
        else:
            pm.warning("There is no reference set for this scene. Nothing changed")





class MainUI(QtWidgets.QMainWindow):

    def __init__(self):



        for entry in QtWidgets.QApplication.allWidgets():
            if entry.objectName() == "SceneManager":
                entry.close()
        parent = getMayaMainWindow()
        super(MainUI, self).__init__(parent=parent)

        if not checkAdminRights():
            q = QtWidgets.QMessageBox()
            q.setIcon(QtWidgets.QMessageBox.Information)
            q.setText("Maya does not have the administrator rights")
            q.setInformativeText("You need to run Maya as administrator to work with Scene Manager")
            q.setWindowTitle("Admin Rights")
            q.setStandardButtons(QtWidgets.QMessageBox.Ok)

            ret = q.exec_()
            if ret == QtWidgets.QMessageBox.Ok:
                self.close()
                self.deleteLater()

        self.manager = TikManager()

        self.scenesInCategory = None

        self.setObjectName(("SceneManager"))
        self.resize(680, 600)
        self.setMaximumSize(QtCore.QSize(680, 600))
        self.setWindowTitle(("Scene Manager"))
        self.setToolTip((""))
        self.setStatusTip((""))
        self.setWhatsThis((""))
        self.setAccessibleName((""))
        self.setAccessibleDescription((""))

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName(("centralwidget"))

        self.projectPath_label = QtWidgets.QLabel(self.centralwidget)
        self.projectPath_label.setGeometry(QtCore.QRect(30, 30, 51, 21))
        self.projectPath_label.setToolTip((""))
        self.projectPath_label.setStatusTip((""))
        self.projectPath_label.setWhatsThis((""))
        self.projectPath_label.setAccessibleName((""))
        self.projectPath_label.setAccessibleDescription((""))
        self.projectPath_label.setFrameShape(QtWidgets.QFrame.Box)
        self.projectPath_label.setLineWidth(1)
        self.projectPath_label.setText(("Project:"))
        self.projectPath_label.setTextFormat(QtCore.Qt.AutoText)
        self.projectPath_label.setScaledContents(False)
        self.projectPath_label.setObjectName(("projectPath_label"))

        self.projectPath_lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.projectPath_lineEdit.setGeometry(QtCore.QRect(90, 30, 471, 21))
        self.projectPath_lineEdit.setToolTip((""))
        self.projectPath_lineEdit.setStatusTip((""))
        self.projectPath_lineEdit.setWhatsThis((""))
        self.projectPath_lineEdit.setAccessibleName((""))
        self.projectPath_lineEdit.setAccessibleDescription((""))
        self.projectPath_lineEdit.setText((self.manager.currentProject))
        self.projectPath_lineEdit.setReadOnly(True)
        self.projectPath_lineEdit.setObjectName(("projectPath_lineEdit"))

        self.setProject_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.setProject_pushButton.setGeometry(QtCore.QRect(580, 30, 75, 23))
        self.setProject_pushButton.setToolTip((""))
        self.setProject_pushButton.setStatusTip((""))
        self.setProject_pushButton.setWhatsThis((""))
        self.setProject_pushButton.setAccessibleName((""))
        self.setProject_pushButton.setAccessibleDescription((""))
        self.setProject_pushButton.setText(("SET"))
        self.setProject_pushButton.setObjectName(("setProject_pushButton"))
        
        self.category_tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.category_tabWidget.setGeometry(QtCore.QRect(30, 110, 621, 21))
        self.category_tabWidget.setToolTip((""))
        self.category_tabWidget.setStatusTip((""))
        self.category_tabWidget.setWhatsThis((""))
        self.category_tabWidget.setAccessibleName((""))
        self.category_tabWidget.setAccessibleDescription((""))
        self.category_tabWidget.setDocumentMode(True)
        self.category_tabWidget.setObjectName(("category_tabWidget"))

        for i in self.manager.validCategories:
            self.preTab = QtWidgets.QWidget()
            self.preTab.setObjectName((i))
            self.category_tabWidget.addTab(self.preTab, (i))


        self.loadMode_radioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.loadMode_radioButton.setGeometry(QtCore.QRect(30, 70, 82, 31))
        self.loadMode_radioButton.setToolTip((""))
        self.loadMode_radioButton.setStatusTip((""))
        self.loadMode_radioButton.setWhatsThis((""))
        self.loadMode_radioButton.setAccessibleName((""))
        self.loadMode_radioButton.setAccessibleDescription((""))
        self.loadMode_radioButton.setText(("Load Mode"))
        self.loadMode_radioButton.setChecked(True)
        self.loadMode_radioButton.setObjectName(("loadMode_radioButton"))

        self.referenceMode_radioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.referenceMode_radioButton.setGeometry(QtCore.QRect(110, 70, 101, 31))
        self.referenceMode_radioButton.setToolTip((""))
        self.referenceMode_radioButton.setStatusTip((""))
        self.referenceMode_radioButton.setWhatsThis((""))
        self.referenceMode_radioButton.setAccessibleName((""))
        self.referenceMode_radioButton.setAccessibleDescription((""))
        self.referenceMode_radioButton.setText(("Reference Mode"))
        self.referenceMode_radioButton.setObjectName(("referenceMode_radioButton"))

        self.userName_comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.userName_comboBox.setGeometry(QtCore.QRect(553, 70, 101, 31))
        self.userName_comboBox.setToolTip((""))
        self.userName_comboBox.setStatusTip((""))
        self.userName_comboBox.setWhatsThis((""))
        self.userName_comboBox.setAccessibleName((""))
        self.userName_comboBox.setAccessibleDescription((""))
        self.userName_comboBox.setObjectName(("userName_comboBox"))
        userListSorted = sorted(self.manager.userList.keys())
        for num in range (len(userListSorted)):
            self.userName_comboBox.addItem((userListSorted[num]))
            self.userName_comboBox.setItemText(num, (userListSorted[num]))

        # self.userName_comboBox.addItem((""))
        # self.userName_comboBox.setItemText(0, ("Arda Kutlu")

        self.userName_label = QtWidgets.QLabel(self.centralwidget)
        self.userName_label.setGeometry(QtCore.QRect(520, 70, 31, 31))
        self.userName_label.setToolTip((""))
        self.userName_label.setStatusTip((""))
        self.userName_label.setWhatsThis((""))
        self.userName_label.setAccessibleName((""))
        self.userName_label.setAccessibleDescription((""))
        self.userName_label.setText(("User:"))
        self.userName_label.setObjectName(("userName_label"))

        self.subProject_label = QtWidgets.QLabel(self.centralwidget)
        self.subProject_label.setGeometry(QtCore.QRect(240, 70, 100, 31))
        self.subProject_label.setToolTip((""))
        self.subProject_label.setStatusTip((""))
        self.subProject_label.setWhatsThis((""))
        self.subProject_label.setAccessibleName((""))
        self.subProject_label.setAccessibleDescription((""))
        self.subProject_label.setText(("Sub-Project:"))
        self.subProject_label.setObjectName(("subProject_label"))

        self.subProject_comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.subProject_comboBox.setGeometry(QtCore.QRect(305, 70, 165, 31))
        self.subProject_comboBox.setToolTip((""))
        self.subProject_comboBox.setStatusTip((""))
        self.subProject_comboBox.setWhatsThis((""))
        self.subProject_comboBox.setAccessibleName((""))
        self.subProject_comboBox.setAccessibleDescription((""))
        self.subProject_comboBox.setObjectName(("subProject_comboBox"))

        self.subProject_pushbutton = QtWidgets.QPushButton("+", self.centralwidget)
        self.subProject_pushbutton.setGeometry(QtCore.QRect(475, 70, 31, 31))
        self.subProject_pushbutton.setToolTip((""))
        self.subProject_pushbutton.setStatusTip((""))
        self.subProject_pushbutton.setWhatsThis((""))
        self.subProject_pushbutton.setAccessibleName((""))
        self.subProject_pushbutton.setAccessibleDescription((""))
        self.subProject_pushbutton.setObjectName(("subProject_pushbutton"))


        self.scenes_listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.scenes_listWidget.setGeometry(QtCore.QRect(30, 140, 381, 351))
        self.scenes_listWidget.setToolTip((""))
        self.scenes_listWidget.setStatusTip((""))
        self.scenes_listWidget.setWhatsThis((""))
        self.scenes_listWidget.setAccessibleName((""))
        self.scenes_listWidget.setAccessibleDescription((""))
        self.scenes_listWidget.setObjectName(("scenes_listWidget"))
        self.scenes_listWidget.setStyleSheet("border-style: solid; border-width: 2px; border-color: grey;")

        self.notes_textEdit = QtWidgets.QTextEdit(self.centralwidget, readOnly=True)
        self.notes_textEdit.setGeometry(QtCore.QRect(430, 260, 221, 231))
        self.notes_textEdit.setToolTip((""))
        self.notes_textEdit.setStatusTip((""))
        self.notes_textEdit.setWhatsThis((""))
        self.notes_textEdit.setAccessibleName((""))
        self.notes_textEdit.setAccessibleDescription((""))
        self.notes_textEdit.setObjectName(("notes_textEdit"))

        self.version_comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.version_comboBox.setGeometry(QtCore.QRect(490, 150, 71, 31))
        self.version_comboBox.setToolTip((""))
        self.version_comboBox.setStatusTip((""))
        self.version_comboBox.setWhatsThis((""))
        self.version_comboBox.setAccessibleName((""))
        self.version_comboBox.setAccessibleDescription((""))
        self.version_comboBox.setObjectName(("version_comboBox"))

        self.version_label = QtWidgets.QLabel(self.centralwidget)
        self.version_label.setGeometry(QtCore.QRect(430, 151, 51, 31))
        self.version_label.setToolTip((""))
        self.version_label.setStatusTip((""))
        self.version_label.setWhatsThis((""))
        self.version_label.setAccessibleName((""))
        self.version_label.setAccessibleDescription((""))
        self.version_label.setFrameShape(QtWidgets.QFrame.Box)
        self.version_label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.version_label.setText(("Version:"))
        self.version_label.setObjectName(("version_label"))

        self.showPB_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.showPB_pushButton.setGeometry(QtCore.QRect(580, 151, 72, 28))
        self.showPB_pushButton.setToolTip((""))
        self.showPB_pushButton.setStatusTip((""))
        self.showPB_pushButton.setWhatsThis((""))
        self.showPB_pushButton.setAccessibleName((""))
        self.showPB_pushButton.setAccessibleDescription((""))
        self.showPB_pushButton.setText(("Show PB"))
        self.showPB_pushButton.setObjectName(("showPB_pushButton"))

        self.makeReference_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.makeReference_pushButton.setGeometry(QtCore.QRect(430, 200, 131, 23))
        self.makeReference_pushButton.setToolTip(("Creates a copy the scene as \'forReference\' file"))
        self.makeReference_pushButton.setStatusTip((""))
        self.makeReference_pushButton.setWhatsThis((""))
        self.makeReference_pushButton.setAccessibleName((""))
        self.makeReference_pushButton.setAccessibleDescription((""))
        self.makeReference_pushButton.setText(("Make Reference"))
        self.makeReference_pushButton.setShortcut((""))
        self.makeReference_pushButton.setObjectName(("makeReference_pushButton"))

        self.notes_label = QtWidgets.QLabel(self.centralwidget)
        self.notes_label.setGeometry(QtCore.QRect(430, 240, 70, 13))
        self.notes_label.setToolTip((""))
        self.notes_label.setStatusTip((""))
        self.notes_label.setWhatsThis((""))
        self.notes_label.setAccessibleName((""))
        self.notes_label.setAccessibleDescription((""))
        self.notes_label.setText(("Version Notes:"))
        self.notes_label.setObjectName(("notes_label"))

        self.saveScene_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.saveScene_pushButton.setGeometry(QtCore.QRect(40, 510, 151, 41))
        self.saveScene_pushButton.setToolTip(("Saves the Base Scene. This will save the scene and will make versioning possible."))
        self.saveScene_pushButton.setStatusTip((""))
        self.saveScene_pushButton.setWhatsThis((""))
        self.saveScene_pushButton.setAccessibleName((""))
        self.saveScene_pushButton.setAccessibleDescription((""))
        self.saveScene_pushButton.setText(("Save Base Scene"))
        self.saveScene_pushButton.setObjectName(("saveScene_pushButton"))

        self.saveAsVersion_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.saveAsVersion_pushButton.setGeometry(QtCore.QRect(210, 510, 151, 41))
        self.saveAsVersion_pushButton.setToolTip(("Saves the current scene as a version. A base scene must be present."))
        self.saveAsVersion_pushButton.setStatusTip((""))
        self.saveAsVersion_pushButton.setWhatsThis((""))
        self.saveAsVersion_pushButton.setAccessibleName((""))
        self.saveAsVersion_pushButton.setAccessibleDescription((""))
        self.saveAsVersion_pushButton.setText(("Save As Version"))
        self.saveAsVersion_pushButton.setObjectName(("saveAsVersion_pushButton"))

        self.load_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.load_pushButton.setGeometry(QtCore.QRect(500, 510, 151, 41))
        self.load_pushButton.setToolTip(("Loads the scene or Creates the selected reference depending on the mode"))
        self.load_pushButton.setStatusTip((""))
        self.load_pushButton.setWhatsThis((""))
        self.load_pushButton.setAccessibleName((""))
        self.load_pushButton.setAccessibleDescription((""))
        self.load_pushButton.setText(("Load Scene"))
        self.load_pushButton.setObjectName(("load_pushButton"))

        self.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 680, 18))
        self.menubar.setObjectName(("menubar"))
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName(("statusbar"))
        self.setStatusBar(self.statusbar)
        self.setStatusBar(self.statusbar)

        file = self.menubar.addMenu("File")
        pb_settings = QtWidgets.QAction("&Playblast Settings", self)
        deleteFile = QtWidgets.QAction("&Delete Selected Base Scene", self)
        reBuildDatabase = QtWidgets.QAction("&Re-build Project Database", self)
        projectReport = QtWidgets.QAction("&Project Report", self)
        createPB = QtWidgets.QAction("&Create PlayBlast", self)
        file.addAction(pb_settings)
        file.addAction(deleteFile)
        file.addAction(reBuildDatabase)
        file.addAction(projectReport)
        file.addAction(createPB)

        # settings.triggered.connect(self.userPrefSave)
        deleteFile.triggered.connect(lambda: self.passwordBridge(command="deleteItem"))
        deleteFile.triggered.connect(self.populateScenes)
        reBuildDatabase.triggered.connect(lambda: suMod.SuManager().rebuildDatabase())
        projectReport.triggered.connect(lambda: self.manager.projectReport())
        # projectReport.triggered.connect(lambda: self.passwordBridge())
        pb_settings.triggered.connect(self.pbSettingsUI)
        createPB.triggered.connect(self.manager.createPlayblast)



        tools = self.menubar.addMenu("Tools")
        foolsMate = QtWidgets.QAction("&Fool's Mate", self)
        tools.addAction(foolsMate)
        # submitToDeadline = QtWidgets.QAction("&Submit to Deadline", self)
        # tools.addAction(submitToDeadline)

        foolsMate.triggered.connect(self.onFoolsMate)
        # submitToDeadline.triggered.connect()

        self.loadMode_radioButton.toggled.connect(self.onRadioButtonsToggled)
        self.referenceMode_radioButton.toggled.connect(self.onRadioButtonsToggled)

        # self.loadMode_radioButton.toggled.connect(lambda: self.version_comboBox.setEnabled(self.loadMode_radioButton.isChecked()))
        # self.loadMode_radioButton.toggled.connect(lambda: self.version_label.setEnabled(self.loadMode_radioButton.isChecked()))
        # self.loadMode_radioButton.toggled.connect(lambda: self.makeReference_pushButton.setEnabled(self.loadMode_radioButton.isChecked()))
        # self.loadMode_radioButton.toggled.connect(lambda: self.notes_label.setEnabled(self.loadMode_radioButton.isChecked()))
        # self.loadMode_radioButton.toggled.connect(lambda: self.notes_textEdit.setEnabled(self.loadMode_radioButton.isChecked()))

        # self.loadMode_radioButton.toggled.connect(lambda: self.load_pushButton.setText("Load Scene"))
        # self.referenceMode_radioButton.toggled.connect(lambda: self.load_pushButton.setText("Reference Scene"))
        # self.loadMode_radioButton.toggled.connect(self.populateScenes)
        # self.referenceMode_radioButton.toggled.connect(self.populateScenes)

        self.setProject_pushButton.clicked.connect(self.onSetProject)

        self.category_tabWidget.currentChanged.connect(self.populateScenes)

        self.scenes_listWidget.currentItemChanged.connect(self.sceneInfo)

        self.makeReference_pushButton.clicked.connect(self.makeReference)

        self.saveScene_pushButton.clicked.connect(self.saveBaseSceneDialog)

        self.saveAsVersion_pushButton.clicked.connect(self.saveAsVersionDialog)
        # self.saveAsVersion_pushButton.clicked.connect(self.onSaveAsVersion)

        self.subProject_pushbutton.clicked.connect(self.createSubProjectUI)

        self.subProject_comboBox.activated.connect(self.onSubProjectChanged)

        self.load_pushButton.clicked.connect(self.onloadScene)
        # self.load_pushButton.clicked.connect(self.referenceCheck)
        self.userName_comboBox.currentIndexChanged.connect(self.onUsernameChanged)

        self.version_comboBox.activated.connect(self.refreshNotes)

        self.scenes_listWidget.doubleClicked.connect(self.onloadScene)

        self.showPB_pushButton.clicked.connect(self.onShowPBclicked)

        ## RIGHT CLICK MENUS
        self.scenes_listWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.scenes_listWidget.customContextMenuRequested.connect(self.on_context_menu)
        self.popMenu = QtWidgets.QMenu()

        rcAction_0 = QtWidgets.QAction('Import Scene', self)
        self.popMenu.addAction(rcAction_0)
        rcAction_0.triggered.connect(lambda : self.rcAction("importScene"))

        self.popMenu.addSeparator()

        rcAction_1 = QtWidgets.QAction('Show Maya Folder in Explorer', self)
        self.popMenu.addAction(rcAction_1)
        rcAction_1.triggered.connect(lambda : self.rcAction("showInExplorerMaya"))


        rcAction_2 = QtWidgets.QAction('Show Playblast Folder in Explorer', self)
        self.popMenu.addAction(rcAction_2)
        rcAction_2.triggered.connect(lambda : self.rcAction("showInExplorerPB"))


        rcAction_3 = QtWidgets.QAction('Show Data Folder in Explorer', self)
        self.popMenu.addAction(rcAction_3)
        rcAction_3.triggered.connect(lambda : self.rcAction("showInExplorerData"))

        # swAction = QtWidgets.QAction('Show Wireframe', self)
        # self.popMenu.addAction(swAction)
        # swAction.triggered.connect(lambda item='swPath': self.actionTrigger(item))

        # self.popMenu.addSeparator()

        # importWithCopyAction = QtWidgets.QAction('Import and Copy Textures', self)
        # self.popMenu.addAction(importWithCopyAction)
        # importWithCopyAction.triggered.connect(lambda item='importWithCopy': self.actionTrigger(item))

        #######
        shortcutRefresh = Qt.QtWidgets.QShortcut(Qt.QtGui.QKeySequence("F5"), self, self.populateScenes)

        self.userPrefLoad()
        self.populateScenes()
        
    def pbSettingsUI(self):

        if not self.passwordBridge(command="simpleCheck"):
            self.infoPop(textTitle="Incorrect Password", textHeader="The Password is invalid")
            return

        currentSettings = self.manager.getPBsettings()

        self.pbSettings_dialog = QtWidgets.QDialog(parent=self)
        self.pbSettings_dialog.setModal(True)
        self.pbSettings_dialog.setObjectName(("Playblast_Dialog"))
        self.pbSettings_dialog.resize(380, 483)
        self.pbSettings_dialog.setMinimumSize(QtCore.QSize(380, 520))
        self.pbSettings_dialog.setMaximumSize(QtCore.QSize(380, 520))
        self.pbSettings_dialog.setWindowTitle(("Set Playblast Settings"))
        self.pbSettings_dialog.setToolTip((""))
        self.pbSettings_dialog.setStatusTip((""))
        self.pbSettings_dialog.setWhatsThis((""))
        self.pbSettings_dialog.setAccessibleName((""))
        self.pbSettings_dialog.setAccessibleDescription((""))

        self.pbsettings_buttonBox = QtWidgets.QDialogButtonBox(self.pbSettings_dialog)
        self.pbsettings_buttonBox.setGeometry(QtCore.QRect(20, 470, 341, 30))
        self.pbsettings_buttonBox.setToolTip((""))
        self.pbsettings_buttonBox.setStatusTip((""))
        self.pbsettings_buttonBox.setWhatsThis((""))
        self.pbsettings_buttonBox.setAccessibleName((""))
        self.pbsettings_buttonBox.setAccessibleDescription((""))
        self.pbsettings_buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.pbsettings_buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Save)
        self.pbsettings_buttonBox.setObjectName(("pbsettings_buttonBox"))

        self.videoproperties_groupBox = QtWidgets.QGroupBox(self.pbSettings_dialog)
        self.videoproperties_groupBox.setGeometry(QtCore.QRect(10, 20, 361, 191))
        self.videoproperties_groupBox.setToolTip((""))
        self.videoproperties_groupBox.setStatusTip((""))
        self.videoproperties_groupBox.setWhatsThis((""))
        self.videoproperties_groupBox.setAccessibleName((""))
        self.videoproperties_groupBox.setAccessibleDescription((""))
        self.videoproperties_groupBox.setTitle(("Video Properties"))
        self.videoproperties_groupBox.setObjectName(("videoproperties_groupBox"))

        self.fileformat_label = QtWidgets.QLabel(self.videoproperties_groupBox)
        self.fileformat_label.setGeometry(QtCore.QRect(20, 30, 71, 20))
        self.fileformat_label.setToolTip((""))
        self.fileformat_label.setStatusTip((""))
        self.fileformat_label.setWhatsThis((""))
        self.fileformat_label.setAccessibleName((""))
        self.fileformat_label.setAccessibleDescription((""))
        self.fileformat_label.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.fileformat_label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.fileformat_label.setText(("Format"))
        self.fileformat_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.fileformat_label.setObjectName(("fileformat_label"))

        self.fileformat_comboBox = QtWidgets.QComboBox(self.videoproperties_groupBox)
        self.fileformat_comboBox.setGeometry(QtCore.QRect(100, 30, 111, 22))
        self.fileformat_comboBox.setToolTip((""))
        self.fileformat_comboBox.setStatusTip((""))
        self.fileformat_comboBox.setWhatsThis((""))
        self.fileformat_comboBox.setAccessibleName((""))
        self.fileformat_comboBox.setAccessibleDescription((""))
        self.fileformat_comboBox.setObjectName(("fileformat_comboBox"))
        formats = pm.playblast(query = True, format = True)
        self.fileformat_comboBox.addItems(formats)

        # get the index number from the name in the settings file and make that index active
        ffindex = self.fileformat_comboBox.findText(currentSettings["Format"], QtCore.Qt.MatchFixedString)
        if ffindex >= 0:
            self.fileformat_comboBox.setCurrentIndex(ffindex)

        self.codec_label = QtWidgets.QLabel(self.videoproperties_groupBox)
        self.codec_label.setGeometry(QtCore.QRect(30, 70, 61, 20))
        self.codec_label.setToolTip((""))
        self.codec_label.setStatusTip((""))
        self.codec_label.setWhatsThis((""))
        self.codec_label.setAccessibleName((""))
        self.codec_label.setAccessibleDescription((""))
        self.codec_label.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.codec_label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.codec_label.setText(("Codec"))
        self.codec_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.codec_label.setObjectName(("codec_label"))

        self.codec_comboBox = QtWidgets.QComboBox(self.videoproperties_groupBox)
        self.codec_comboBox.setGeometry(QtCore.QRect(100, 70, 111, 22))
        self.codec_comboBox.setToolTip((""))
        self.codec_comboBox.setStatusTip((""))
        self.codec_comboBox.setWhatsThis((""))
        self.codec_comboBox.setAccessibleName((""))
        self.codec_comboBox.setAccessibleDescription((""))
        self.codec_comboBox.setObjectName(("codec_comboBox"))
        self.updateCodecs()

        self.fileformat_comboBox.currentIndexChanged.connect(self.updateCodecs)

        # get the index number from the name in the settings file and make that index active
        print currentSettings["Codec"]
        cindex = self.codec_comboBox.findText(currentSettings["Codec"], QtCore.Qt.MatchFixedString)
        if cindex >= 0:
            self.codec_comboBox.setCurrentIndex(cindex)

        self.quality_label = QtWidgets.QLabel(self.videoproperties_groupBox)
        self.quality_label.setGeometry(QtCore.QRect(30, 110, 61, 20))
        self.quality_label.setToolTip((""))
        self.quality_label.setStatusTip((""))
        self.quality_label.setWhatsThis((""))
        self.quality_label.setAccessibleName((""))
        self.quality_label.setAccessibleDescription((""))
        self.quality_label.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.quality_label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.quality_label.setText(("Quality"))
        self.quality_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.quality_label.setObjectName(("quality_label"))

        self.quality_spinBox = QtWidgets.QSpinBox(self.videoproperties_groupBox)
        self.quality_spinBox.setGeometry(QtCore.QRect(100, 110, 41, 21))
        self.quality_spinBox.setToolTip((""))
        self.quality_spinBox.setStatusTip((""))
        self.quality_spinBox.setWhatsThis((""))
        self.quality_spinBox.setAccessibleName((""))
        self.quality_spinBox.setAccessibleDescription((""))
        self.quality_spinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.quality_spinBox.setMinimum(1)
        self.quality_spinBox.setMaximum(100)
        self.quality_spinBox.setProperty("value", currentSettings["Quality"])
        self.quality_spinBox.setObjectName(("quality_spinBox"))

        self.quality_horizontalSlider = QtWidgets.QSlider(self.videoproperties_groupBox)
        self.quality_horizontalSlider.setGeometry(QtCore.QRect(150, 110, 191, 21))
        self.quality_horizontalSlider.setToolTip((""))
        self.quality_horizontalSlider.setStatusTip((""))
        self.quality_horizontalSlider.setWhatsThis((""))
        self.quality_horizontalSlider.setAccessibleName((""))
        self.quality_horizontalSlider.setAccessibleDescription((""))
        self.quality_horizontalSlider.setMinimum(1)
        self.quality_horizontalSlider.setMaximum(100)
        self.quality_horizontalSlider.setProperty("value", currentSettings["Quality"])
        self.quality_horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.quality_horizontalSlider.setTickInterval(0)
        self.quality_horizontalSlider.setObjectName(("quality_horizontalSlider"))

        self.resolution_label = QtWidgets.QLabel(self.videoproperties_groupBox)
        self.resolution_label.setGeometry(QtCore.QRect(30, 150, 61, 20))
        self.resolution_label.setToolTip((""))
        self.resolution_label.setStatusTip((""))
        self.resolution_label.setWhatsThis((""))
        self.resolution_label.setAccessibleName((""))
        self.resolution_label.setAccessibleDescription((""))
        self.resolution_label.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.resolution_label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.resolution_label.setText(("Resolution"))
        self.resolution_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.resolution_label.setObjectName(("resolution_label"))

        self.resolutionx_spinBox = QtWidgets.QSpinBox(self.videoproperties_groupBox)
        self.resolutionx_spinBox.setGeometry(QtCore.QRect(100, 150, 61, 21))
        self.resolutionx_spinBox.setToolTip((""))
        self.resolutionx_spinBox.setStatusTip((""))
        self.resolutionx_spinBox.setWhatsThis((""))
        self.resolutionx_spinBox.setAccessibleName((""))
        self.resolutionx_spinBox.setAccessibleDescription((""))
        self.resolutionx_spinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.resolutionx_spinBox.setMinimum(0)
        self.resolutionx_spinBox.setMaximum(4096)
        self.resolutionx_spinBox.setProperty("value", currentSettings["Resolution"][0])
        self.resolutionx_spinBox.setObjectName(("resolutionx_spinBox"))

        self.resolutiony_spinBox = QtWidgets.QSpinBox(self.videoproperties_groupBox)
        self.resolutiony_spinBox.setGeometry(QtCore.QRect(170, 150, 61, 21))
        self.resolutiony_spinBox.setToolTip((""))
        self.resolutiony_spinBox.setStatusTip((""))
        self.resolutiony_spinBox.setWhatsThis((""))
        self.resolutiony_spinBox.setAccessibleName((""))
        self.resolutiony_spinBox.setAccessibleDescription((""))
        self.resolutiony_spinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.resolutiony_spinBox.setMinimum(1)
        self.resolutiony_spinBox.setMaximum(4096)
        self.resolutiony_spinBox.setProperty("value", currentSettings["Resolution"][1])
        self.resolutiony_spinBox.setObjectName(("resolutiony_spinBox"))

        self.viewportoptions_groupBox = QtWidgets.QGroupBox(self.pbSettings_dialog)
        self.viewportoptions_groupBox.setGeometry(QtCore.QRect(10, 230, 361, 91))
        self.viewportoptions_groupBox.setTitle(("Viewport Options"))
        self.viewportoptions_groupBox.setObjectName(("viewportoptions_groupBox"))

        self.polygononly_checkBox = QtWidgets.QCheckBox(self.viewportoptions_groupBox)
        self.polygononly_checkBox.setGeometry(QtCore.QRect(60, 30, 91, 20))
        self.polygononly_checkBox.setToolTip((""))
        self.polygononly_checkBox.setStatusTip((""))
        self.polygononly_checkBox.setWhatsThis((""))
        self.polygononly_checkBox.setAccessibleName((""))
        self.polygononly_checkBox.setAccessibleDescription((""))
        self.polygononly_checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.polygononly_checkBox.setText(("Polygon Only"))
        self.polygononly_checkBox.setChecked(currentSettings["PolygonOnly"])
        self.polygononly_checkBox.setObjectName(("polygononly_checkBox"))

        self.showgrid_checkBox = QtWidgets.QCheckBox(self.viewportoptions_groupBox)
        self.showgrid_checkBox.setGeometry(QtCore.QRect(210, 30, 91, 20))
        self.showgrid_checkBox.setToolTip((""))
        self.showgrid_checkBox.setStatusTip((""))
        self.showgrid_checkBox.setWhatsThis((""))
        self.showgrid_checkBox.setAccessibleName((""))
        self.showgrid_checkBox.setAccessibleDescription((""))
        self.showgrid_checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.showgrid_checkBox.setText(("Show Grid"))
        self.showgrid_checkBox.setChecked(currentSettings["ShowGrid"])
        self.showgrid_checkBox.setObjectName(("showgrid_checkBox"))

        self.clearselection_checkBox = QtWidgets.QCheckBox(self.viewportoptions_groupBox)
        self.clearselection_checkBox.setGeometry(QtCore.QRect(60, 60, 91, 20))
        self.clearselection_checkBox.setToolTip((""))
        self.clearselection_checkBox.setStatusTip((""))
        self.clearselection_checkBox.setWhatsThis((""))
        self.clearselection_checkBox.setAccessibleName((""))
        self.clearselection_checkBox.setAccessibleDescription((""))
        self.clearselection_checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.clearselection_checkBox.setText(("Clear Selection"))
        self.clearselection_checkBox.setChecked(currentSettings["ClearSelection"])
        self.clearselection_checkBox.setObjectName(("clearselection_checkBox"))

        self.displaytextures_checkBox = QtWidgets.QCheckBox(self.viewportoptions_groupBox)
        self.displaytextures_checkBox.setGeometry(QtCore.QRect(190, 60, 111, 20))
        self.displaytextures_checkBox.setToolTip((""))
        self.displaytextures_checkBox.setStatusTip((""))
        self.displaytextures_checkBox.setWhatsThis((""))
        self.displaytextures_checkBox.setAccessibleName((""))
        self.displaytextures_checkBox.setAccessibleDescription((""))
        self.displaytextures_checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.displaytextures_checkBox.setText(("Display Textures"))
        self.displaytextures_checkBox.setChecked(currentSettings["DisplayTextures"])
        self.displaytextures_checkBox.setObjectName(("displaytextures_checkBox"))

        self.hudoptions_groupBox = QtWidgets.QGroupBox(self.pbSettings_dialog)
        self.hudoptions_groupBox.setGeometry(QtCore.QRect(10, 340, 361, 110))
        self.hudoptions_groupBox.setToolTip((""))
        self.hudoptions_groupBox.setStatusTip((""))
        self.hudoptions_groupBox.setWhatsThis((""))
        self.hudoptions_groupBox.setAccessibleName((""))
        self.hudoptions_groupBox.setAccessibleDescription((""))
        self.hudoptions_groupBox.setTitle(("HUD Options"))
        self.hudoptions_groupBox.setObjectName(("hudoptions_groupBox"))

        self.showframenumber_checkBox = QtWidgets.QCheckBox(self.hudoptions_groupBox)
        self.showframenumber_checkBox.setGeometry(QtCore.QRect(20, 20, 131, 20))
        self.showframenumber_checkBox.setToolTip((""))
        self.showframenumber_checkBox.setStatusTip((""))
        self.showframenumber_checkBox.setWhatsThis((""))
        self.showframenumber_checkBox.setAccessibleName((""))
        self.showframenumber_checkBox.setAccessibleDescription((""))
        self.showframenumber_checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.showframenumber_checkBox.setText(("Show Frame Number"))
        self.showframenumber_checkBox.setChecked(currentSettings["ShowFrameNumber"])
        self.showframenumber_checkBox.setObjectName(("showframenumber_checkBox"))

        self.showscenename_checkBox = QtWidgets.QCheckBox(self.hudoptions_groupBox)
        self.showscenename_checkBox.setGeometry(QtCore.QRect(20, 50, 131, 20))
        self.showscenename_checkBox.setToolTip((""))
        self.showscenename_checkBox.setStatusTip((""))
        self.showscenename_checkBox.setWhatsThis((""))
        self.showscenename_checkBox.setAccessibleName((""))
        self.showscenename_checkBox.setAccessibleDescription((""))
        self.showscenename_checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.showscenename_checkBox.setText(("Show Scene Name"))
        self.showscenename_checkBox.setChecked(currentSettings["ShowSceneName"])
        self.showscenename_checkBox.setObjectName(("showscenename_checkBox"))

        self.showcategory_checkBox = QtWidgets.QCheckBox(self.hudoptions_groupBox)
        self.showcategory_checkBox.setGeometry(QtCore.QRect(200, 20, 101, 20))
        self.showcategory_checkBox.setToolTip((""))
        self.showcategory_checkBox.setStatusTip((""))
        self.showcategory_checkBox.setWhatsThis((""))
        self.showcategory_checkBox.setAccessibleName((""))
        self.showcategory_checkBox.setAccessibleDescription((""))
        self.showcategory_checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.showcategory_checkBox.setText(("Show Category"))
        self.showcategory_checkBox.setChecked(currentSettings["ShowCategory"])
        self.showcategory_checkBox.setObjectName(("showcategory_checkBox"))

        self.showfps_checkBox = QtWidgets.QCheckBox(self.hudoptions_groupBox)
        self.showfps_checkBox.setGeometry(QtCore.QRect(200, 50, 101, 20))
        self.showfps_checkBox.setToolTip((""))
        self.showfps_checkBox.setStatusTip((""))
        self.showfps_checkBox.setWhatsThis((""))
        self.showfps_checkBox.setAccessibleName((""))
        self.showfps_checkBox.setAccessibleDescription((""))
        self.showfps_checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.showfps_checkBox.setText(("Show FPS"))
        self.showfps_checkBox.setChecked(currentSettings["ShowFPS"])
        self.showfps_checkBox.setObjectName(("showfps_checkBox"))

        self.showframerange_checkBox = QtWidgets.QCheckBox(self.hudoptions_groupBox)
        self.showframerange_checkBox.setGeometry(QtCore.QRect(20, 80, 131, 20))
        self.showframerange_checkBox.setToolTip((""))
        self.showframerange_checkBox.setStatusTip((""))
        self.showframerange_checkBox.setWhatsThis((""))
        self.showframerange_checkBox.setAccessibleName((""))
        self.showframerange_checkBox.setAccessibleDescription((""))
        self.showframerange_checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.showframerange_checkBox.setText(("Show Frame Range"))
        # v1.1 SPECIFIC
        try:
            self.showframerange_checkBox.setChecked(currentSettings["ShowFrameRange"])
        except KeyError:
            self.showframerange_checkBox.setChecked(True)
        self.showframerange_checkBox.setObjectName(("showframerange_checkBox"))


        self.pbsettings_buttonBox.accepted.connect(self.pbSettings_dialog.accept)
        self.pbsettings_buttonBox.accepted.connect(self.onPbSettingsAccept)
        self.pbsettings_buttonBox.rejected.connect(self.pbSettings_dialog.reject)
        self.quality_spinBox.valueChanged.connect(self.quality_horizontalSlider.setValue)
        self.quality_horizontalSlider.valueChanged.connect(self.quality_spinBox.setValue)

        self.pbSettings_dialog.show()

    def updateCodecs(self):
        codecs = pm.mel.eval('playblast -format "{0}" -q -compression;'.format(self.fileformat_comboBox.currentText()))
        self.codec_comboBox.clear()
        self.codec_comboBox.addItems(codecs)

    def onPbSettingsAccept(self):
        projectPath, playBlastRoot = getPathsFromScene("projectPath","playBlastRoot")

        pbSettingsFile = "{0}\\PBsettings.json".format(os.path.join(projectPath, playBlastRoot))

        newPbSettings = {"Resolution": (self.resolutionx_spinBox.value(), self.resolutiony_spinBox.value()),
                           "Format": self.fileformat_comboBox.currentText(),
                           "Codec": self.codec_comboBox.currentText(),
                           "Percent": 100, ## this one never changes
                           "Quality": self.quality_spinBox.value(),
                           "ShowFrameNumber": self.showframenumber_checkBox.isChecked(),
                           "ShowSceneName": self.showscenename_checkBox.isChecked(),
                           "ShowCategory": self.showcategory_checkBox.isChecked(),
                           "ShowFPS": self.showfps_checkBox.isChecked(),
                           "ShowFrameRange": self.showframerange_checkBox.isChecked(),
                           "PolygonOnly": self.polygononly_checkBox.isChecked(),
                           "ShowGrid": self.showgrid_checkBox.isChecked(),
                           "ClearSelection": self.clearselection_checkBox.isChecked(),
                           "DisplayTextures": self.displaytextures_checkBox.isChecked()
                         }
        dumpJson(newPbSettings, pbSettingsFile)
    def onFoolsMate(self):
        import foolsMate
        foolsMate.startFoolin()

    def saveBaseSceneDialog(self):
        self.save_Dialog = QtWidgets.QDialog(parent=self)
        self.save_Dialog.setModal(True)
        self.save_Dialog.setObjectName(("save_Dialog"))
        self.save_Dialog.resize(500, 240)
        self.save_Dialog.setMinimumSize(QtCore.QSize(500, 240))
        self.save_Dialog.setMaximumSize(QtCore.QSize(500, 240))
        self.save_Dialog.setWindowTitle(("Save New Base Scene"))
        self.save_Dialog.setToolTip((""))
        self.save_Dialog.setStatusTip((""))
        self.save_Dialog.setWhatsThis((""))
        self.save_Dialog.setAccessibleName((""))
        self.save_Dialog.setAccessibleDescription((""))

        self.sdNotes_label = QtWidgets.QLabel(self.save_Dialog)
        self.sdNotes_label.setGeometry(QtCore.QRect(260, 15, 61, 20))
        self.sdNotes_label.setToolTip((""))
        self.sdNotes_label.setStatusTip((""))
        self.sdNotes_label.setWhatsThis((""))
        self.sdNotes_label.setAccessibleName((""))
        self.sdNotes_label.setAccessibleDescription((""))
        # self.sdNotes_label.setFrameShape(QtWidgets.QFrame.Box)
        self.sdNotes_label.setText(("Notes"))
        self.sdNotes_label.setObjectName(("sdNotes_label"))

        self.sdNotes_textEdit = QtWidgets.QTextEdit(self.save_Dialog)
        self.sdNotes_textEdit.setGeometry(QtCore.QRect(260, 40, 215, 180))
        self.sdNotes_textEdit.setToolTip((""))
        self.sdNotes_textEdit.setStatusTip((""))
        self.sdNotes_textEdit.setWhatsThis((""))
        self.sdNotes_textEdit.setAccessibleName((""))
        self.sdNotes_textEdit.setAccessibleDescription((""))
        self.sdNotes_textEdit.setObjectName(("sdNotes_textEdit"))

        self.sdSubP_label = QtWidgets.QLabel(self.save_Dialog)
        self.sdSubP_label.setGeometry(QtCore.QRect(20, 30, 61, 20))
        self.sdSubP_label.setToolTip((""))
        self.sdSubP_label.setStatusTip((""))
        self.sdSubP_label.setWhatsThis((""))
        self.sdSubP_label.setAccessibleName((""))
        self.sdSubP_label.setAccessibleDescription((""))
        self.sdSubP_label.setFrameShape(QtWidgets.QFrame.Box)
        self.sdSubP_label.setText(("Sub-Project"))
        self.sdSubP_label.setObjectName(("sdSubP_label"))

        self.sdSubP_comboBox = QtWidgets.QComboBox(self.save_Dialog)
        self.sdSubP_comboBox.setFocus()
        self.sdSubP_comboBox.setGeometry(QtCore.QRect(90, 30, 151, 22))
        self.sdSubP_comboBox.setToolTip((""))
        self.sdSubP_comboBox.setStatusTip((""))
        self.sdSubP_comboBox.setWhatsThis((""))
        self.sdSubP_comboBox.setAccessibleName((""))
        self.sdSubP_comboBox.setAccessibleDescription((""))
        self.sdSubP_comboBox.setObjectName(("sdCategory_comboBox"))
        self.sdSubP_comboBox.addItems((self.manager.subProjectList))
        self.sdSubP_comboBox.setCurrentIndex(self.subProject_comboBox.currentIndex())

        self.sdName_label = QtWidgets.QLabel(self.save_Dialog)
        self.sdName_label.setGeometry(QtCore.QRect(20, 70, 61, 20))
        self.sdName_label.setToolTip((""))
        self.sdName_label.setStatusTip((""))
        self.sdName_label.setWhatsThis((""))
        self.sdName_label.setAccessibleName((""))
        self.sdName_label.setAccessibleDescription((""))
        self.sdName_label.setFrameShape(QtWidgets.QFrame.Box)
        self.sdName_label.setText(("Name"))
        self.sdName_label.setObjectName(("sdName_label"))

        self.sdName_lineEdit = QtWidgets.QLineEdit(self.save_Dialog)
        self.sdName_lineEdit.setGeometry(QtCore.QRect(90, 70, 151, 20))
        self.sdName_lineEdit.setToolTip((""))
        self.sdName_lineEdit.setStatusTip((""))
        self.sdName_lineEdit.setWhatsThis((""))
        self.sdName_lineEdit.setAccessibleName((""))
        self.sdName_lineEdit.setAccessibleDescription((""))
        self.sdName_lineEdit.setText((""))
        self.sdName_lineEdit.setCursorPosition(0)
        self.sdName_lineEdit.setPlaceholderText(("Choose an unique name"))
        self.sdName_lineEdit.setObjectName(("sdName_lineEdit"))

        self.sdCategory_label = QtWidgets.QLabel(self.save_Dialog)
        self.sdCategory_label.setGeometry(QtCore.QRect(20, 110, 61, 20))
        self.sdCategory_label.setToolTip((""))
        self.sdCategory_label.setStatusTip((""))
        self.sdCategory_label.setWhatsThis((""))
        self.sdCategory_label.setAccessibleName((""))
        self.sdCategory_label.setAccessibleDescription((""))
        self.sdCategory_label.setFrameShape(QtWidgets.QFrame.Box)
        self.sdCategory_label.setText(("Category"))
        self.sdCategory_label.setObjectName(("sdCategory_label"))

        self.sdCategory_comboBox = QtWidgets.QComboBox(self.save_Dialog)
        self.sdCategory_comboBox.setFocus()
        self.sdCategory_comboBox.setGeometry(QtCore.QRect(90, 110, 151, 22))
        self.sdCategory_comboBox.setToolTip((""))
        self.sdCategory_comboBox.setStatusTip((""))
        self.sdCategory_comboBox.setWhatsThis((""))
        self.sdCategory_comboBox.setAccessibleName((""))
        self.sdCategory_comboBox.setAccessibleDescription((""))
        self.sdCategory_comboBox.setObjectName(("sdCategory_comboBox"))
        for i in range (len(self.manager.validCategories)):
            self.sdCategory_comboBox.addItem((self.manager.validCategories[i]))
            self.sdCategory_comboBox.setItemText(i, (self.manager.validCategories[i]))
        self.sdCategory_comboBox.setCurrentIndex(self.category_tabWidget.currentIndex())

        self.sdMakeReference_checkbox = QtWidgets.QCheckBox("Make it Reference", self.save_Dialog)
        self.sdMakeReference_checkbox.setGeometry(QtCore.QRect(130, 150, 151, 22))

        self.sd_buttonBox = QtWidgets.QDialogButtonBox(self.save_Dialog)
        self.sd_buttonBox.setGeometry(QtCore.QRect(20, 190, 220, 32))
        self.sd_buttonBox.setToolTip((""))
        self.sd_buttonBox.setStatusTip((""))
        self.sd_buttonBox.setWhatsThis((""))
        self.sd_buttonBox.setAccessibleName((""))
        self.sd_buttonBox.setAccessibleDescription((""))
        self.sd_buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.sd_buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.sd_buttonBox.setObjectName(("sd_buttonBox"))


        self.sd_buttonBox.accepted.connect(self.onSaveBaseScene)
        self.sd_buttonBox.accepted.connect(self.save_Dialog.accept)
        self.sd_buttonBox.rejected.connect(self.save_Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(self.save_Dialog)

        self.save_Dialog.show()

    def saveAsVersionDialog(self):
        saveV_Dialog = QtWidgets.QDialog(parent=self)
        saveV_Dialog.setModal(True)
        saveV_Dialog.setObjectName(("saveV_Dialog"))
        saveV_Dialog.resize(255, 290)
        saveV_Dialog.setMinimumSize(QtCore.QSize(255, 290))
        saveV_Dialog.setMaximumSize(QtCore.QSize(255, 290))
        saveV_Dialog.setWindowTitle(("Save As Version"))
        saveV_Dialog.setToolTip((""))
        saveV_Dialog.setStatusTip((""))
        saveV_Dialog.setWhatsThis((""))
        saveV_Dialog.setAccessibleName((""))
        saveV_Dialog.setAccessibleDescription((""))

        svNotes_label = QtWidgets.QLabel(saveV_Dialog)
        svNotes_label.setGeometry(QtCore.QRect(15, 15, 61, 20))
        svNotes_label.setToolTip((""))
        svNotes_label.setStatusTip((""))
        svNotes_label.setWhatsThis((""))
        svNotes_label.setAccessibleName((""))
        svNotes_label.setAccessibleDescription((""))
        svNotes_label.setText(("Version Notes"))
        svNotes_label.setObjectName(("sdNotes_label"))

        self.svNotes_textEdit = QtWidgets.QTextEdit(saveV_Dialog)
        self.svNotes_textEdit.setGeometry(QtCore.QRect(15, 40, 215, 170))
        self.svNotes_textEdit.setToolTip((""))
        self.svNotes_textEdit.setStatusTip((""))
        self.svNotes_textEdit.setWhatsThis((""))
        self.svNotes_textEdit.setAccessibleName((""))
        self.svNotes_textEdit.setAccessibleDescription((""))
        self.svNotes_textEdit.setObjectName(("sdNotes_textEdit"))


        self.svMakeReference_checkbox = QtWidgets.QCheckBox("Make it Reference", saveV_Dialog)
        self.svMakeReference_checkbox.setGeometry(QtCore.QRect(130, 215, 151, 22))
        self.svMakeReference_checkbox.setChecked(True)

        sv_buttonBox = QtWidgets.QDialogButtonBox(saveV_Dialog)
        sv_buttonBox.setGeometry(QtCore.QRect(20, 250, 220, 32))
        sv_buttonBox.setToolTip((""))
        sv_buttonBox.setStatusTip((""))
        sv_buttonBox.setWhatsThis((""))
        sv_buttonBox.setAccessibleName((""))
        sv_buttonBox.setAccessibleDescription((""))
        sv_buttonBox.setOrientation(QtCore.Qt.Horizontal)
        sv_buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel)

        buttonS = sv_buttonBox.button(QtWidgets.QDialogButtonBox.Save)
        buttonS.setText('Save As Version')
        buttonC = sv_buttonBox.button(QtWidgets.QDialogButtonBox.Cancel)
        buttonC.setText('Cancel')


        sv_buttonBox.setObjectName(("sd_buttonBox"))
        sv_buttonBox.accepted.connect(self.onSaveAsVersion)
        sv_buttonBox.accepted.connect(saveV_Dialog.accept)
        sv_buttonBox.rejected.connect(saveV_Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(saveV_Dialog)

        saveV_Dialog.show()

    def onSaveBaseScene(self):
        userInitials = self.manager.userList[self.userName_comboBox.currentText()]
        subProject = self.sdSubP_comboBox.currentIndex()
        print subProject

        name = nameCheck(self.sdName_lineEdit.text())
        if name == -1:
            self.infoPop(textHeader="Invalid characters. Use <A-Z> and <0-9>", textInfo="", textTitle="ERROR: ASCII Error", type="C")
            return

        sceneFile = self.manager.saveNewScene(self.sdCategory_comboBox.currentText(), userInitials, name, subProject = subProject, makeReference= self.sdMakeReference_checkbox.checkState(), versionNotes=self.sdNotes_textEdit.toPlainText())

        if not sceneFile == -1:
            self.infoPop(textHeader="Save Base Scene Successfull",textInfo="New Version of Base Scene saved as {0}".format(sceneFile),textTitle="Saved Base Scene", type="I")
        else:
            self.infoPop(textHeader="Save Base Scene FAILED. A Base Scene with the same name already exists in the same sub-project and same category. Choose an unique one.", textInfo="", textTitle="ERROR: Saving Base Scene", type="C")
        self.populateScenes()

    def onSaveAsVersion(self):
        userInitials = self.manager.userList[self.userName_comboBox.currentText()]
        sceneFile=self.manager.saveVersion(userInitials, makeReference=self.svMakeReference_checkbox.checkState(), versionNotes=self.svNotes_textEdit.toPlainText())
        self.populateScenes()
        if not sceneFile == -1:
            self.infoPop(textHeader="Save Version Successfull",textInfo="New Version of Base Scene saved as {0}".format(sceneFile),textTitle="Saved New Version", type="I")
        else:
            self.infoPop(textHeader="Save Version FAILED", textInfo="Cannot Find The Database. The File is not saved as a Base Scene, or database file is missing".format(sceneFile), textTitle="ERROR: Saving New Version", type="C")

    def onloadScene(self):

        row = self.scenes_listWidget.currentRow()
        if row == -1:
            pm.warning("no scene selected")
            return

        sceneName = "%s.json" %self.scenes_listWidget.currentItem().text()
        # takethefirstjson as example for rootpath


        sceneJson = os.path.join(pathOps(self.scenesInCategory[0], "path"), sceneName)



        # sceneJson = self.scenesInCategory[row]

        if self.loadMode_radioButton.isChecked():
            fileCheckState = cmds.file(q=True, modified=True)
            ## Eger dosya save edilmemisse:
            if fileCheckState:
                q = QtWidgets.QMessageBox(parent=self)
                q.setIcon(QtWidgets.QMessageBox.Question)
                q.setText("Save changes to")
                q.setInformativeText(pm.sceneName())
                q.setWindowTitle("Save Changes")
                q.setStandardButtons(QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
                ret = q.exec_()
                if ret == QtWidgets.QMessageBox.Save:
                    pm.saveFile()
                    self.manager.loadScene(sceneJson, version=self.version_comboBox.currentIndex(), force=True)
                elif ret == QtWidgets.QMessageBox.No:
                    self.manager.loadScene(sceneJson, version=self.version_comboBox.currentIndex(), force=True)
                elif ret == QtWidgets.QMessageBox.Cancel:
                    pass
                    # elif ret == QtWidgets.QMessageBox.No:
            ## Dosya saveli ise devam
            else:
                self.manager.loadScene(sceneJson, version=self.version_comboBox.currentIndex(), force=True)

        if self.referenceMode_radioButton.isChecked():
            self.manager.loadReference(sceneJson)
        #     self.manager.loadScene(sceneJson, version=self.version_comboBox.currentIndex(),force=True)
        # if self.referenceMode_radioButton.isChecked():
        #     pass

    def onShowPBclicked(self):
        row = self.scenes_listWidget.currentRow()
        if row == -1:
            pm.warning("no scene selected")
            return

        sceneName = "%s.json" %self.scenes_listWidget.currentItem().text()
        # takethefirstjson as example for rootpath
        sceneJson = os.path.join(pathOps(self.scenesInCategory[0], "path"), sceneName)

        # sceneJson = self.scenesInCategory[row]
        version = self.version_comboBox.currentIndex()
        # print version
        sceneInfo = loadJson(sceneJson)
        # print sceneInfo
        # print sceneInfo["Versions"][version][4].keys()
        pbDict = sceneInfo["Versions"][version][4]
        if len(pbDict.keys()) == 1:
            path=pbDict[pbDict.keys()[0]]
            # print path
            self.manager.playPlayblast(path)
        else:
            zortMenu = QtWidgets.QMenu()

            for z in pbDict.keys():
                tempAction = QtWidgets.QAction(z, self)
                zortMenu.addAction(tempAction )
                tempAction.triggered.connect(lambda item=pbDict[z]: self.manager.playPlayblast(item)) ## Take note about the usage of lambda "item=pbDict[z]" makes it possible using the loop

            zortMenu.exec_((QtGui.QCursor.pos()))

    def onRadioButtonsToggled(self):
        state=self.loadMode_radioButton.isChecked()
        self.version_label.setEnabled(state)
        self.makeReference_pushButton.setEnabled(state)
        self.notes_label.setEnabled(state)
        self.notes_textEdit.setEnabled(state)
        self.showPB_pushButton.setEnabled(state)
        if state:
            self.load_pushButton.setText("Load Scene")
            self.scenes_listWidget.setStyleSheet("border-style: solid; border-width: 2px; border-color: grey;")
        else:
            self.load_pushButton.setText("Reference Scene")
            self.scenes_listWidget.setStyleSheet("border-style: solid; border-width: 2px; border-color: red;")
        self.populateScenes()

    def userPrefSave(self):
        # pass

        homedir = os.path.expanduser("~")
        settingsFilePath = os.path.join(homedir, "smSettings.json")

        settingsData = {"currentTabIndex": self.category_tabWidget.currentIndex(),
                        "currentSubIndex": self.subProject_comboBox.currentIndex(),
                        "currentUserIndex": self.userName_comboBox.currentIndex(),
                        "currentMode": self.referenceMode_radioButton.isChecked()}

        dumpJson(settingsData, settingsFilePath)

    def userPrefLoad(self):
        # pass
        homedir = os.path.expanduser("~")
        settingsFilePath = os.path.join(homedir, "smSettings.json")
        if os.path.isfile(settingsFilePath):
            settingsData = loadJson(settingsFilePath)
        else:
            # return defaults
            settingsData = {"currentTabIndex": 0, "currentSubIndex": 0, "currentUserIndex": 0, "currentMode": 0}
            dumpJson(settingsData, settingsFilePath)

        self.referenceMode_radioButton.setChecked(settingsData["currentMode"])
        self.loadMode_radioButton.setChecked(not settingsData["currentMode"])

        if settingsData["currentUserIndex"] <= (len(self.manager.userList)):
            currentUserIndex = settingsData["currentUserIndex"]
        else:
            currentUserIndex = 0
        # self.manager.currentUserIndex=currentUserIndex
        self.userName_comboBox.setCurrentIndex(currentUserIndex)

        if settingsData["currentSubIndex"] < (len(self.manager.subProjectList)):
            currentSubIndex = settingsData["currentSubIndex"]
        else:
            currentSubIndex = 0

        self.manager.currentSubProjectIndex=currentSubIndex
        print "index", self.manager.currentSubProjectIndex
        self.subProject_comboBox.setCurrentIndex(currentSubIndex)

        self.category_tabWidget.setCurrentIndex(settingsData["currentTabIndex"])

    def onUsernameChanged(self):
        self.userPrefSave()

    def rcAction(self, command):
        if command == "importScene":
            row = self.scenes_listWidget.currentRow()
            if not row == -1:
                # sceneData = loadJson(self.scenesInCategory[row])
                # path = os.path.join(os.path.normpath(self.manager.currentProject), os.path.normpath(sceneData["Path"]))
                sceneName = "%s.json" % self.scenes_listWidget.currentItem().text()
                # takethefirstjson as example for rootpath
                jsonPath = os.path.join(pathOps(self.scenesInCategory[0], "path"), sceneName)
                self.manager.loadScene(jsonPath, version=self.version_comboBox.currentIndex(), importFile=True)

                # self.manager.loadScene(self.scenesInCategory[row], version=self.version_comboBox.currentIndex(), importFile=True)
                # os.startfile(path)

        if command == "showInExplorerMaya":
            row = self.scenes_listWidget.currentRow()
            if not row == -1:
                sceneName = "%s.json" % self.scenes_listWidget.currentItem().text()
                # takethefirstjson as example for rootpath
                jPath = os.path.join(pathOps(self.scenesInCategory[0], "path"), sceneName)

                sceneData = loadJson(os.path.join(jPath, sceneName))
                # sceneData = loadJson(self.scenesInCategory[row])

                path = os.path.join(os.path.normpath(self.manager.currentProject), os.path.normpath(sceneData["Path"]))
                os.startfile(path)

        if command == "showInExplorerPB":
            row = self.scenes_listWidget.currentRow()
            if not row == -1:
                sceneName = "%s.json" % self.scenes_listWidget.currentItem().text()
                # takethefirstjson as example for rootpath
                jPath = pathOps(self.scenesInCategory[0], "path")

                sceneData = loadJson(os.path.join(jPath, sceneName))
                # sceneData = loadJson(self.scenesInCategory[row])

                path = os.path.join(os.path.normpath(self.manager.currentProject), os.path.normpath(sceneData["Path"]))
                path = path.replace("scenes", "Playblasts")
                print path
                if os.path.isdir(path):
                    os.startfile(path)
                else:
                    self.infoPop(textTitle="", textHeader="Scene does not have a playblast", textInfo="There is no playblast folder created for this scene yet")

        if command == "showInExplorerData":
            row = self.scenes_listWidget.currentRow()
            if not row == -1:
                try:
                    path = pathOps(self.scenesInCategory[row], "path")
                except:
                    path = pathOps(self.scenesInCategory[0], "path")
                os.startfile(path)

    def on_context_menu(self, point):
        # show context menu
        self.popMenu.exec_(self.scenes_listWidget.mapToGlobal(point))

    def onSubProjectChanged(self):
        self.manager.currentSubProjectIndex=self.subProject_comboBox.currentIndex()
        self.populateScenes()

    def createSubProjectUI(self):

        newSub, ok = QtWidgets.QInputDialog.getText(self, "Create New Sub-Project", "Enter an unique Sub-Project name:")
        if ok:
            name = nameCheck(newSub)
            if not name == -1:
                self.subProject_comboBox.clear()
                self.manager.subProjectList = self.manager.createSubProject(name)
                self.populateScenes()
            else:
                self.infoPop(textTitle="Naming Error", textHeader="Naming Error", textInfo="Choose an unique name with latin characters without spaces", type="C")

    def referenceCheck(self):
        projectPath = os.path.normpath(pm.workspace(q=1, rd=1))
        for path in self.scenesInCategory:
            data = loadJson(path)
            if data["ReferenceFile"]:
                relRefVersion = data["Versions"][data["ReferencedVersion"]-1][0]

                # refVersion = "%s%s" %(projectPath, relRefVersion)
                refVersion = os.path.join(projectPath, relRefVersion)

                relRefFile = data["ReferenceFile"]

                # refFile = "%s%s" %(projectPath, relRefFile)
                refFile = os.path.join(projectPath, relRefFile)

                if not os.path.isfile(refFile):
                    # reference file does not exist at all
                    color = QtGui.QColor(255, 0, 0, 255)  # "red"

                else:
                    if filecmp.cmp(refVersion, refFile):
                        # no problem
                        color = QtGui.QColor(0, 255, 0, 255) #"green"

                    else:
                        # checksum mismatch
                        color = QtGui.QColor(255, 0, 0, 255) #"red"

            else:
                #no reference defined for the base scene
                color = QtGui.QColor(255, 255, 0, 255) #"yellow"

            index = self.scenesInCategory.index(path)
            if self.scenes_listWidget.item(index):
                self.scenes_listWidget.item(index).setForeground(color)

    def onSetProject(self):
        mel.eval("SetProject;")
        self.manager.currentProject = pm.workspace(q=1, rd=1)
        self.projectPath_lineEdit.setText(self.manager.currentProject)
        # self.onSubProjectChanged()
        self.manager.subProjectList=self.manager.scanSubProjects()

        self.populateScenes()

    def sceneInfo(self):
        self.version_comboBox.clear()

        row = self.scenes_listWidget.currentRow()
        if row == -1:
            return

        sceneName = "%s.json" %self.scenes_listWidget.currentItem().text()
        # takethefirstjson as example for rootpath
        jPath = pathOps(self.scenesInCategory[0], "path")

        sceneData = loadJson(os.path.join(jPath, sceneName))

        #
        # sceneData = loadJson(self.scenesInCategory[row])

        for num in range (len(sceneData["Versions"])):
            self.version_comboBox.addItem("v{0}".format(str(num+1).zfill(3)))

        if sceneData["ReferencedVersion"]:
            currentIndex = sceneData["ReferencedVersion"]-1
            # self.version_comboBox.setCurrentIndex(sceneData["ReferencedVersion"]-1)
        else:
            currentIndex = len(sceneData["Versions"])-1
            # self.version_comboBox.setCurrentIndex(len(sceneData["Versions"])-1)
        self.version_comboBox.setCurrentIndex(currentIndex)
        self.notes_textEdit.setPlainText(sceneData["Versions"][currentIndex][1])
        self.refreshNotes()

    def refreshNotes(self):
        row = self.scenes_listWidget.currentRow()
        if not row == -1:
            sceneName = "%s.json" % self.scenes_listWidget.currentItem().text()
            # takethefirstjson as example for rootpath
            jPath = pathOps(self.scenesInCategory[0], "path")

            sceneData = loadJson(os.path.join(jPath, sceneName))
            # sceneData = loadJson(self.scenesInCategory[row])
            currentIndex = self.version_comboBox.currentIndex()
            self.notes_textEdit.setPlainText(sceneData["Versions"][currentIndex][1])

            if sceneData["Versions"][currentIndex][4].keys():
                self.showPB_pushButton.setEnabled(True)
            else:
                self.showPB_pushButton.setEnabled(False)
        else:

            self.showPB_pushButton.setEnabled(False)

    def populateScenes(self):

        self.scenes_listWidget.clear()
        self.version_comboBox.clear()
        self.notes_textEdit.clear()
        self.subProject_comboBox.clear()
        # currentTabName = self.category_tabWidget.currentWidget().objectName()
        # scannedScenes = self.manager.scanScenes(currentTabName)

        self.scenesInCategory, subProjectFile=self.manager.scanScenes(self.category_tabWidget.currentWidget().objectName())

        if self.referenceMode_radioButton.isChecked():
            for i in self.scenesInCategory:
                jsonFile = loadJson(i)
                if jsonFile["ReferenceFile"]:
                    self.scenes_listWidget.addItem(pathOps(i, "filename"))
            self.version_comboBox.setEnabled(False)


        else:
            # self.scenes_listWidget.addItems(self.scenesInCategory)
            for i in self.scenesInCategory:
                self.scenes_listWidget.addItem(pathOps(i, "filename"))
            self.referenceCheck()
            self.version_comboBox.setEnabled(True)
        # self.manager.subProjectList = loadJson(subProjectFile)


        self.subProject_comboBox.addItems((self.manager.subProjectList))
        # index = self.manager.subProjectList.index(self.manager.currentSubProject)


        self.subProject_comboBox.setCurrentIndex(self.manager.currentSubProjectIndex)
        self.refreshNotes()
        self.userPrefSave()

        # self.referenceCheck()

    def makeReference(self):
        row = self.scenes_listWidget.currentRow()
        if not row == -1:
            sceneName = "%s.json" % self.scenes_listWidget.currentItem().text()
            # takethefirstjson as example for rootpath
            jPath = pathOps(self.scenesInCategory[0], "path")

            jsonFile = loadJson(os.path.join(jPath, sceneName))
            # jsonFile = self.scenesInCategory[row]
            version = self.version_comboBox.currentIndex()
            self.manager.makeReference(jsonFile, version+1)
            # self.sceneInfo()
            self.populateScenes()

    def infoPop(self, textTitle="info", textHeader="", textInfo="", type="I"):
        self.msg = QtWidgets.QMessageBox(parent=self)
        if type=="I":
            self.msg.setIcon(QtWidgets.QMessageBox.Information)
        if type=="C":
            self.msg.setIcon(QtWidgets.QMessageBox.Critical)

        self.msg.setText(textHeader)
        self.msg.setInformativeText(textInfo)
        self.msg.setWindowTitle(textTitle)
        self.msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        self.msg.show()

    def passwordBridge(self, command):
        passw, ok = QtWidgets.QInputDialog.getText(self, "Password Query", "Enter Admin Password:", QtWidgets.QLineEdit.Password)
        if ok:
            if command == "deleteItem":
                row = self.scenes_listWidget.currentRow()
                if not row == -1:
                    ## TODO // If no item is selected should skip it
                    sceneName = "%s.json" % self.scenes_listWidget.currentItem().text()
                    jPath = pathOps(self.scenesInCategory[0], "path")
                    jsonFile = loadJson(os.path.join(jPath, sceneName))
                    suMod.SuManager().deleteItem(jsonFile, loadJson(jsonFile),passw)
            if command == "simpleCheck":
                return suMod.SuManager().passwCheck(passw)
            return passw
        # pwDialog = QtWidgets.QDialog(parent=self)
        # pwLabel = QtWidgets.QLabel("Enter the admin password", pwDialog)
        # pw = QtWidgets.QLineEdit(pwDialog)
        # pw.setEchoMode(QtWidgets.QLineEdit.Password)
        # pwDialog.show()
