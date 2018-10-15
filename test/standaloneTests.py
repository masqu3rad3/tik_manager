from tik_manager import SmStandalone
reload(SmStandalone)

n = SmStandalone.StandaloneManager()


# n.setProject("E:\\testingArea\\Friday_test_test_181012")

# n._pathsDict["userSettingsDir"]
n.initSoftwares()

# n.swList[0].getBaseScenesInCategory()


print n.swList[1].swDict
