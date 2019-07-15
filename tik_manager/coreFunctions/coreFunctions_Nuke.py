import os
import nuke

class NukeCoreFunctions(object):
    def __init__(self):
        super(NukeCoreFunctions, self).__init__()

    def _save(self, *args, **kwargs):
        pass
        # not needed

    def _saveAs(self, filePath, format=None, *args, **kwargs):
        nuke.scriptSaveAs(filePath)

    def _load(self, filePath, force=True, *args, **kwargs):
        nuke.scriptOpen(filePath)

    def _reference(self, filePath):
        pass

    def _import(self, filePath, *args, **kwargs):
        nuke.nodePaste(filePath)

    def _importObj(self, filePath, importSettings, *args, **kwargs):
        # TODO: May prove useful to implement this as well
        pass

    def _importAlembic(self, filePath, importSettings, *args, **kwargs):
        # TODO: May prove useful to implement this as well
        pass

    def _importFbx(self, filePath, importSettings, *args, **kwargs):
        # TODO: May prove useful to implement this as well
        pass

    def _exportObj(self, filePath, exportSettings, exportSelected=True):
        pass

    def _exportAlembic(self, filePath, exportSettings, exportSelected=True, timeRange=[0,10]):
        pass

    def _exportFbx(self, filePath, exportSettings, exportSelected=True, timeRange=[0,10]):
        pass

    def _getSceneFile(self):
        sceneName = nuke.root().knob('name').value()
        norm_s_path = os.path.normpath(sceneName)
        return norm_s_path

    def _getProject(self):
        homeDir = os.path.expanduser("~")
        norm_p_path = os.path.normpath(homeDir)
        return norm_p_path

    def _getVersion(self):
        return [nuke.NUKE_VERSION_MAJOR, nuke.NUKE_VERSION_MINOR]

    def _getCurrentFrame(self):
        return nuke.frame()

    def _getSelection(self):
        return nuke.selectedNodes()

    def _isSceneModified(self):
        return nuke.modified()