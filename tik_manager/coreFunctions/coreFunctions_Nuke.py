import os
import nuke
import logging

logging.basicConfig()
logger = logging.getLogger('coreFunctions_Nuke')
logger.setLevel(logging.WARNING)

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

    def _importSequence(self, pySeq_sequence, *args, **kwargs):
        seqFormatted = "{0}{1}{2}".format(pySeq_sequence.head(), pySeq_sequence._get_padding(),
                                          pySeq_sequence.tail())
        seqPath = os.path.join(pySeq_sequence.dirname, seqFormatted)

        firstFrame = pySeq_sequence.start()
        lastFrame = pySeq_sequence.end()

        readNode = nuke.createNode('Read')
        readNode.knob('file').fromUserText(seqPath)
        readNode.knob('first').setValue(firstFrame)
        readNode.knob('last').setValue(lastFrame)
        readNode.knob('origfirst').setValue(firstFrame)
        readNode.knob('origlast').setValue(lastFrame)

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
        return [int(nuke.NUKE_VERSION_MAJOR), int(nuke.NUKE_VERSION_MINOR)]

    def _getCurrentFrame(self):
        return nuke.frame()

    def _getSelection(self):
        return nuke.selectedNodes()

    def _isSceneModified(self):
        return nuke.modified()