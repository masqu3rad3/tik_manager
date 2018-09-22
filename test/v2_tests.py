
# import maya.standalone
# maya.standalone.initialize()
# from tik_manager import SmMaya

from tik_manager import SmMaya as tm
reload(tm)

# initializer
e = tm.MayaManager()

e.saveBaseScene("Model", "v2CommandTest", subProjectIndex=0, makeReference=False, versionNotes="Testing V2", sceneFormat="ma")

e.deleteBasescene(e.getSceneInfo()["jsonFile"])

# cursor controls (Get/Set)
e.projectDir
e.currentTabIndex = 0
e.currentSubIndex = 1
e.currentUser
e.currentMode

e.subProject

e.currentBaseSceneName = "v2CommandTest"
e.currentVersionIndex = 4
e.currentPreviewCamera


# getters
e.getCategories()
e.getSubProjects()
e.getUsers()
e.getBaseScenesInCategory()
e.getVersions()
e.getNotes()
e.getPreviews()
e.getThumbnail()

# commands
e.createNewProject(projectRoot, projectName, brandName, client)
e.createSubproject("testingV2")
e.showInExplorer("E:\\testingArea\\testV2_testV2_testV2_180922\\smDatabase\\mayaDB\\Animation\\yeniFilm\\")
e.scanBaseScenes()
e.addNote(note)
e.playPreview()
e.removePreview()
e.deleteBasescene(databaseFile)
e.deleteReference(databaseFile)
e.makeReference()
e.checkReference()