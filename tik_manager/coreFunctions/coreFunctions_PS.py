import os
from win32com.client import Dispatch
import logging

logging.basicConfig()
logger = logging.getLogger('coreFunctions_PS')
logger.setLevel(logging.WARNING)

class PsCoreFunctions(object):
    def __init__(self):
        super(PsCoreFunctions, self).__init__()
        # self.psApp = Dispatch('Photoshop.Application')

    def comLink(self):
        return Dispatch('Photoshop.Application')

    def _save(self, *args, **kwargs):
        pass
        # not needed

    def _saveAs(self, filePath, format=None, *args, **kwargs):


        if format == "psd":

            desc19 = Dispatch("Photoshop.ActionDescriptor")
            desc20 = Dispatch("Photoshop.ActionDescriptor")
            desc20.PutBoolean(self.psApp.StringIDToTypeID('maximizeCompatibility'), True)
            desc19.PutObject(
                self.psApp.CharIDToTypeID('As  '), self.psApp.CharIDToTypeID('Pht3'), desc20)
            desc19.PutPath(self.psApp.CharIDToTypeID('In  '), filePath)
            desc19.PutBoolean(self.psApp.CharIDToTypeID('LwCs'), True)
            self.psApp.ExecuteAction(self.psApp.CharIDToTypeID('save'), desc19, 3)

        else:

            desc19 = Dispatch("Photoshop.ActionDescriptor")
            desc20 = Dispatch("Photoshop.ActionDescriptor")
            desc20.PutBoolean(self.psApp.StringIDToTypeID('maximizeCompatibility'), True)

            desc19.PutObject(
                self.psApp.CharIDToTypeID('As  '), self.psApp.CharIDToTypeID('Pht8'), desc20)
            desc19.PutPath(self.psApp.CharIDToTypeID('In  '), filePath)
            desc19.PutBoolean(self.psApp.CharIDToTypeID('LwCs'), True)
            self.psApp.ExecuteAction(self.psApp.CharIDToTypeID('save'), desc19, 3)

    def _load(self, filePath, force=True, *args, **kwargs):
        self.psApp.Open(filePath)

    def _reference(self, filePath):
        pass

    def _import(self, filePath, *args, **kwargs):
        pass

    def _importSequence(self, pySeq_sequence, *args, **kwargs):
        logger.warning("This function is not yet implemented")

    def _importObj(self, filePath, importSettings, *args, **kwargs):
        pass

    def _importAlembic(self, filePath, importSettings, *args, **kwargs):
        pass

    def _importFbx(self, filePath, importSettings, *args, **kwargs):
        pass

    def _exportObj(self, filePath, exportSettings, exportSelected=True):
        pass

    def _exportAlembic(self, filePath, exportSettings, exportSelected=True, timeRange=[0,10]):
        pass

    def _exportFbx(self, filePath, exportSettings, exportSelected=True, timeRange=[0,10]):
        pass

    def _getSceneFile(self):
        try:
            activeDocument = self.psApp.Application.ActiveDocument
            docName = activeDocument.name
            docPath = activeDocument.path
            return os.path.join(docPath, docName)
        except:
            return "Untitled"

    def _getProject(self):
        """returns the project folder DEFINED BY THE HOST SOFTWARE, not the Tik Manager Project"""
        homeDir = os.path.expanduser("~")
        norm_p_path = os.path.normpath(homeDir)
        return norm_p_path

    def _getVersion(self):
        pass

    def _getCurrentFrame(self):
        pass

    def _getSelection(self):
        pass

    def _isSceneModified(self):
        return False

    def _exportJPG(self, filePath, quality=12):
        activeDocument = self.psApp.Application.ActiveDocument
        saveOPT = Dispatch("Photoshop.JPEGSaveOptions")
        saveOPT.EmbedColorProfile = True
        saveOPT.FormatOptions = 1  # => psStandardBaseline
        saveOPT.Matte = 1  # => No Matte
        saveOPT.Quality = quality
        activeDocument.SaveAs(filePath, saveOPT, True)
        return True

    def _exportPNG(self, filePath):
        activeDocument = self.psApp.Application.ActiveDocument
        saveOPT = Dispatch("Photoshop.PNGSaveOptions")
        activeDocument.SaveAs(filePath, saveOPT, True)
        return True

    def _exportBMP(self, filePath):
        activeDocument = self.psApp.Application.ActiveDocument
        saveOPT = Dispatch("Photoshop.BMPSaveOptions")
        activeDocument.SaveAs(filePath, saveOPT, True)
        return True

    def _exportTGA(self, filePath):
        activeDocument = self.psApp.Application.ActiveDocument
        saveOPT = Dispatch("Photoshop.TargaSaveOptions")
        saveOPT.Resolution = 32
        saveOPT.AlphaChannels = True
        saveOPT.RLECompression = True
        activeDocument.SaveAs(filePath, saveOPT, True)
        return True

    def _exportPSD(self, filePath):
        activeDocument = self.psApp.Application.ActiveDocument
        saveOPT = Dispatch("Photoshop.PhotoshopSaveOptions")
        saveOPT.AlphaChannels = True
        saveOPT.Annotations = True
        saveOPT.Layers = True
        saveOPT.SpotColors = True
        activeDocument.SaveAs(filePath, saveOPT, True)
        return True

    def _exportTIF(self, filePath):
        activeDocument = self.psApp.Application.ActiveDocument
        saveOPT = Dispatch("Photoshop.TiffSaveOptions")
        saveOPT.AlphaChannels = True
        saveOPT.EmbedColorProfile = True
        saveOPT.Layers = False
        activeDocument.SaveAs(filePath, saveOPT, True)
        return True

    def _exportEXR(self, filePath):
        idsave = self.psApp.CharIDToTypeID("save")
        desc182 = Dispatch("Photoshop.ActionDescriptor")
        idAs = self.psApp.CharIDToTypeID("As  ")
        desc183 = Dispatch("Photoshop.ActionDescriptor")
        idBtDp = self.psApp.CharIDToTypeID("BtDp")
        desc183.PutInteger(idBtDp, 16);
        idCmpr = self.psApp.CharIDToTypeID("Cmpr")
        desc183.PutInteger(idCmpr, 1)
        idAChn = self.psApp.CharIDToTypeID("AChn")
        desc183.PutInteger(idAChn, 0)
        idEXRf = self.psApp.CharIDToTypeID("EXRf")
        desc182.PutObject(idAs, idEXRf, desc183)
        idIn = self.psApp.CharIDToTypeID("In  ")
        desc182.PutPath(idIn, (filePath))
        idDocI = self.psApp.CharIDToTypeID("DocI")
        desc182.PutInteger(idDocI, 340)
        idCpy = self.psApp.CharIDToTypeID("Cpy ")
        desc182.PutBoolean(idCpy, True)
        idsaveStage = self.psApp.StringIDToTypeID("saveStage")
        idsaveStageType = self.psApp.StringIDToTypeID("saveStageType")
        idsaveSucceeded = self.psApp.StringIDToTypeID("saveSucceeded")
        desc182.PutEnumerated(idsaveStage, idsaveStageType, idsaveSucceeded)
        self.psApp.ExecuteAction(idsave, desc182, 3)
        return True

    def _exportHDR(self, filePath):
        idsave = self.psApp.CharIDToTypeID("save")
        desc419 = Dispatch("Photoshop.ActionDescriptor")
        idAs = self.psApp.CharIDToTypeID("As  ")
        desc419.PutString(idAs, """Radiance""")
        idIn = self.psApp.CharIDToTypeID("In  ")
        desc419.PutPath(idIn, (filePath))
        idDocI = self.psApp.CharIDToTypeID("DocI")
        desc419.PutInteger(idDocI, 333)
        idCpy = self.psApp.CharIDToTypeID("Cpy ")
        desc419.PutBoolean(idCpy, True)
        idsaveStage = self.psApp.StringIDToTypeID("saveStage")
        idsaveStageType = self.psApp.StringIDToTypeID("saveStageType")
        idsaveSucceeded = self.psApp.StringIDToTypeID("saveSucceeded")
        desc419.PutEnumerated(idsaveStage, idsaveStageType, idsaveSucceeded)
        self.psApp.ExecuteAction(idsave, desc419, 3)
        return True

