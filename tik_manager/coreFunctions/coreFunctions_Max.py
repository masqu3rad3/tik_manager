import os
from MaxPlus import FileManager as fManager
from MaxPlus import PathManager as pManager
from pymxs import runtime as rt
import logging

logging.basicConfig()
logger = logging.getLogger('coreFunctions_Max')
logger.setLevel(logging.WARNING)

class MaxCoreFunctions(object):
    def __init__(self):
        super(MaxCoreFunctions, self).__init__()

    def _new(self, force=True, fps=None):
        fManager.Reset(noPrompt=force)
        if fps:
            rt.frameRate = fps

    def _save(self, *args, **kwargs):
        fManager.Save()

    def _saveAs(self, filePath, *args, **kwargs):
        fManager.Save(filePath)

    def _load(self, filePath, force=True, *args, **kwargs):
        fManager.Open(filePath)

    def _reference(self, filePath):
        Xrefobjs = rt.getMAXFileObjectNames(filePath)
        rt.xrefs.addNewXRefObject(filePath, Xrefobjs)

    def _import(self, filePath, prompt=True, *args, **kwargs):
        if prompt:
            fManager.Merge(filePath)
        else:
            command = 'mergeMAXFile "%s"' %filePath.replace(os.sep, "/")
            rt.execute(command)

    def _importSequence(self, pySeq_sequence, *args, **kwargs):
        logger.warning("This function is not yet implemented")

    def _importObj(self, filePath, importSettings, *args, **kwargs):
        if rt.pluginManager.loadclass(rt.ObjExp):
            # Set OBJ Options
            maxImp_obj = importSettings["objImportMax"]
            iniPath_importSettings = rt.objImp.getIniName()
            rt.setINISetting(iniPath_importSettings, "General", "UseLogging", maxImp_obj["UseLogging"])
            rt.setINISetting(iniPath_importSettings, "General", "ResetScene", maxImp_obj["ResetScene"])
            rt.setINISetting(iniPath_importSettings, "General", "CurrObjColor", maxImp_obj["CurrObjColor"])
            rt.setINISetting(iniPath_importSettings, "General", "MapSearchPath", maxImp_obj["MapSearchPath"])
            rt.setINISetting(iniPath_importSettings, "Objects", "SingleMesh", maxImp_obj["SingleMesh"])
            rt.setINISetting(iniPath_importSettings, "Objects", "AsEditablePoly", maxImp_obj["AsEditablePoly"])
            rt.setINISetting(iniPath_importSettings, "Objects", "Retriangulate", maxImp_obj["Retriangulate"])
            rt.setINISetting(iniPath_importSettings, "Geometry", "FlipZyAxis", maxImp_obj["FlipZyAxis"])
            rt.setINISetting(iniPath_importSettings, "Geometry", "CenterPivots", maxImp_obj["CenterPivots"])
            rt.setINISetting(iniPath_importSettings, "Geometry", "Shapes", maxImp_obj["Shapes"])
            rt.setINISetting(iniPath_importSettings, "Geometry", "TextureCoords", maxImp_obj["TextureCoords"])
            rt.setINISetting(iniPath_importSettings, "Geometry", "SmoothingGroups", maxImp_obj["SmoothingGroups"])
            rt.setINISetting(iniPath_importSettings, "Geometry", "NormalsType", maxImp_obj["NormalsType"])
            rt.setINISetting(iniPath_importSettings, "Geometry", "SmoothAngle", maxImp_obj["SmoothAngle"])
            rt.setINISetting(iniPath_importSettings, "Geometry", "FlipNormals", maxImp_obj["FlipNormals"])
            rt.setINISetting(iniPath_importSettings, "Units/Scale", "Convert", maxImp_obj["Convert"])
            rt.setINISetting(iniPath_importSettings, "Units/Scale", "ConvertFrom", maxImp_obj["ConvertFrom"])
            rt.setINISetting(iniPath_importSettings, "Units/Scale", "ObjScale", maxImp_obj["ObjScale"])
            rt.setINISetting(iniPath_importSettings, "Material", "UniqueWireColor", maxImp_obj["UniqueWireColor"])
            rt.setINISetting(iniPath_importSettings, "Material", "ImportMaterials", maxImp_obj["ImportMaterials"])
            rt.setINISetting(iniPath_importSettings, "Material", "UseMatPrefix", maxImp_obj["UseMatPrefix"])
            rt.setINISetting(iniPath_importSettings, "Material", "DefaultBump", maxImp_obj["DefaultBump"])
            rt.setINISetting(iniPath_importSettings, "Material", "ForceBlackAmbient", maxImp_obj["ForceBlackAmbient"])
            rt.setINISetting(iniPath_importSettings, "Material", "ImportIntoMatEditor", maxImp_obj["ImportIntoMatEditor"])
            rt.setINISetting(iniPath_importSettings, "Material", "ShowMapsInViewport", maxImp_obj["ShowMapsInViewport"])
            rt.setINISetting(iniPath_importSettings, "Material", "CopyMapsToProj", maxImp_obj["CopyMapsToProj"])
            rt.setINISetting(iniPath_importSettings, "Material", "OverwriteImages", maxImp_obj["OverwriteImages"])
            rt.importFile(filePath, rt.Name("NoPrompt"), using=rt.ObjImp)
            return True
        else:
            msg = "OBJ Plugin cannot be initialized. Skipping import"
            rt.messageBox(msg, title='Info')
            return False

    def _importAlembic(self, filePath, importSettings, *args, **kwargs):
        # Set Alembic Options according to the Max Version:
        v = rt.maxVersion()[0]
        maxImp_abc = importSettings["alembicImportMax"]

        if v > 17000:  # Alembic export is not supported before 3ds Max 2016
            if rt.pluginManager.loadclass(rt.Alembic_Export):
                if 18000 <= v < 21000:  # between versions 2016 - 2018
                    rt.AlembicImport.CoordinateSystem = rt.Name(maxImp_abc["CoordinateSystem"])
                    rt.AlembicImport.CacheTimeRange = rt.Name(maxImp_abc["AnimTimeRange"])
                    rt.AlembicImport.ShapeName = maxImp_abc["ShapeSuffix"]
                    rt.AlembicImport.ImportToRoot = maxImp_abc["ImportToRoot"]
                    rt.AlembicImport.FitTimeRange = maxImp_abc["FitTimeRange"]
                    rt.AlembicImport.SetStartTime = maxImp_abc["SetStartTime"]
                    rt.AlembicExport.StepFrameTime = maxImp_abc["SamplesPerFrame"]


                elif v >= 21000:  # version 2019 and up
                    rt.AlembicImport.CoordinateSystem = rt.Name(maxImp_abc["CoordinateSystem"])
                    rt.AlembicImport.AnimTimeRange = rt.Name(maxImp_abc["AnimTimeRange"])
                    rt.AlembicImport.ShapeSuffix = maxImp_abc["ShapeSuffix"]
                    rt.AlembicImport.SamplesPerFrame = maxImp_abc["SamplesPerFrame"]
                    rt.AlembicImport.Hidden = maxImp_abc["Hidden"]
                    rt.AlembicImport.UVs = maxImp_abc["UVs"]
                    rt.AlembicImport.Normals = maxImp_abc["Normals"]
                    rt.AlembicImport.VertexColors = maxImp_abc["VertexColors"]
                    rt.AlembicImport.ExtraChannels = maxImp_abc["ExtraChannels"]
                    rt.AlembicImport.Velocity = maxImp_abc["Velocity"]
                    rt.AlembicImport.MaterialIDs = maxImp_abc["MaterialIDs"]
                    rt.AlembicImport.Visibility = maxImp_abc["Visibility"]
                    rt.AlembicImport.LayerName = maxImp_abc["LayerName"]
                    rt.AlembicImport.MaterialName = maxImp_abc["MaterialName"]
                    rt.AlembicImport.ObjectID = maxImp_abc["ObjectID"]
                    rt.AlembicImport.CustomAttributes = maxImp_abc["CustomAttributes"]

                # Export
                rt.importFile(filePath, rt.Name("NoPrompt"), using=rt.Alembic_Import)
                return True

            else:
                rt.messageBox("Alembic Plugin cannot be initialized. Skipping", title="Alembic not supported")
                return False
        else:
            rt.messageBox("There is no alembic support for this version. Skipping", title="Alembic not supported")
            return False

    def _importFbx(self, filePath, importSettings, *args, **kwargs):
        if rt.pluginManager.loadclass(rt.FBXIMP):
            maxImp_fbx = importSettings["fbxImportMax"]
            # Set FBX Options
            for item in maxImp_fbx.items():
                rt.FBXImporterSetParam(rt.Name(item[0]), item[1])
            rt.FBXImporterSetParam(rt.Name("UpAxis"), "Z")
            try:
                rt.importFile(filePath, rt.Name("NoPrompt"), using=rt.FBXIMP)
                return True
            except:
                msg = "Cannot import FBX file for unknown reason. Skipping import"
                rt.messageBox(msg, title='Info')
                return False
        else:
            msg = "FBX Plugin cannot be initialized. Skipping import"
            rt.messageBox(msg, title='Info')
            return False

    def _importVray(self, filePath, importSettings, *args, **kwargs):
        # TODO: // import vray core function for 3ds Max
        rt.messageBox("Vray Proxy Import for 3ds Max is under development", title='Info')

    def _importRedshift(self, filePath, importSettings, *args, **kwargs):
        # TODO: // import redshift core function for 3ds Max
        rt.messageBox("Redshift Proxy Import for 3ds Max is under development", title='Info')

    def _exportObj(self, filePath, exportSettings, exportSelected=True):
        """
        Exports wavefront Obj file
        Args:
            filePath: (String) Absolute File path for exported file
            exportSettings: (Dictionary) settings file (see getExportSettings)
            exportSelected: (Boolean) If True, exports only currently selected objects, else whole scene. Default True

        Returns: (Boolean) True for success False for failure

        """
        if rt.pluginManager.loadclass(rt.ObjExp):
            maxExp_obj = exportSettings["objExportMax"]
            # Set OBJ Options
            iniPath_exportSettings = rt.objExp.getIniName()
            rt.setINISetting(iniPath_exportSettings, "Geometry", "FlipZyAxis", maxExp_obj["FlipZyAxis"])
            rt.setINISetting(iniPath_exportSettings, "Geometry", "Shapes", maxExp_obj["Shapes"])
            rt.setINISetting(iniPath_exportSettings, "Geometry", "ExportHiddenObjects",
                             maxExp_obj["ExportHiddenObjects"])
            rt.setINISetting(iniPath_exportSettings, "Geometry", "FaceType", maxExp_obj["FaceType"])
            rt.setINISetting(iniPath_exportSettings, "Geometry", "TextureCoords", maxExp_obj["TextureCoords"])
            rt.setINISetting(iniPath_exportSettings, "Geometry", "Normals", maxExp_obj["Normals"])
            rt.setINISetting(iniPath_exportSettings, "Geometry", "SmoothingGroups", maxExp_obj["SmoothingGroups"])
            rt.setINISetting(iniPath_exportSettings, "Geometry", "ObjScale", maxExp_obj["ObjScale"])

            rt.setINISetting(iniPath_exportSettings, "Output", "RelativeIndex", maxExp_obj["RelativeIndex"])
            rt.setINISetting(iniPath_exportSettings, "Output", "Target", maxExp_obj["Target"])
            rt.setINISetting(iniPath_exportSettings, "Output", "Precision", maxExp_obj["Precision"])

            rt.setINISetting(iniPath_exportSettings, "Optimize", "optVertex", maxExp_obj["optVertex"])
            rt.setINISetting(iniPath_exportSettings, "Optimize", "optNormals", maxExp_obj["optNormals"])
            rt.setINISetting(iniPath_exportSettings, "Optimize", "optTextureCoords", maxExp_obj["optTextureCoords"])

            try:
                rt.exportFile(filePath, rt.Name("NoPrompt"), selectedOnly=exportSelected, using=rt.ObjExp)
                return True
            except:
                msg = "Cannot export OBJ for unknown reason. Skipping OBJ export"
                rt.messageBox(msg, title='Info')
                return False

            # objName = "{0}.obj".format(assetName)
        else:
            msg = "Wavefront(Obj) Export Plugin cannot be initialized. Skipping Obj export"
            rt.messageBox(msg, title='Info')
            return False

    def _exportAlembic(self, filePath, exportSettings, exportSelected=True, timeRange=[0,10]):
        """
        Exports Alembic (.abc) file
        Args:
            filePath: (String) Absolute File path for exported file
            exportSettings: (Dictionary) settings file (see getExportSettings)
            exportSelected: (Boolean) If True, exports only currently selected objects, else whole scene. Default True

        Returns: (Boolean) True for success False for failure

        """
        # Set Alembic Options according to the Max Version:
        v = rt.maxVersion()[0]
        maxExp_abc = exportSettings["alembicExportMax"]

        # override animation related settings
        maxExp_abc["AnimTimeRange"] = "StartEnd"
        maxExp_abc["StartFrame"] = timeRange[0]
        maxExp_abc["EndFrame"] = timeRange[1]



        if v > 17000:  # Alembic export is not supported before 3ds Max 2016
            if rt.pluginManager.loadclass(rt.Alembic_Export):
                if 18000 <= v < 21000:  # between versions 2016 - 2018
                    rt.AlembicExport.CoordinateSystem = rt.Name(maxExp_abc["CoordinateSystem"])
                    rt.AlembicExport.ArchiveType = rt.Name(maxExp_abc["ArchiveType"])
                    rt.AlembicExport.ParticleAsMesh = maxExp_abc["ParticleAsMesh"]
                    rt.AlembicExport.CacheTimeRange = rt.Name(maxExp_abc["AnimTimeRange"])
                    rt.AlembicExport.ShapeName = maxExp_abc["ShapeSuffix"]
                    rt.AlembicExport.StepFrameTime = maxExp_abc["SamplesPerFrame"]
                    rt.AlembicExport.AnimTimeRange = maxExp_abc["AnimTimeRange"]
                    rt.AlembicExport.StartFrame = maxExp_abc["StartFrame"]
                    rt.AlembicExport.EndFrame = maxExp_abc["EndFrame"]

                elif v >= 21000:  # version 2019 and up
                    rt.AlembicExport.CoordinateSystem = rt.Name(maxExp_abc["CoordinateSystem"])
                    rt.AlembicExport.ArchiveType = rt.Name(maxExp_abc["ArchiveType"])
                    rt.AlembicExport.ParticleAsMesh = maxExp_abc["ParticleAsMesh"]
                    rt.AlembicExport.ShapeSuffix = maxExp_abc["ShapeSuffix"]
                    rt.AlembicExport.SamplesPerFrame = maxExp_abc["SamplesPerFrame"]
                    rt.AlembicExport.Hidden = maxExp_abc["Hidden"]
                    rt.AlembicExport.UVs = maxExp_abc["UVs"]
                    rt.AlembicExport.Normals = maxExp_abc["Normals"]
                    rt.AlembicExport.VertexColors = maxExp_abc["VertexColors"]
                    rt.AlembicExport.ExtraChannels = maxExp_abc["ExtraChannels"]
                    rt.AlembicExport.Velocity = maxExp_abc["Velocity"]
                    rt.AlembicExport.MaterialIDs = maxExp_abc["MaterialIDs"]
                    rt.AlembicExport.Visibility = maxExp_abc["Visibility"]
                    rt.AlembicExport.LayerName = maxExp_abc["LayerName"]
                    rt.AlembicExport.MaterialName = maxExp_abc["MaterialName"]
                    rt.AlembicExport.ObjectID = maxExp_abc["ObjectID"]
                    rt.AlembicExport.CustomAttributes = maxExp_abc["CustomAttributes"]
                    rt.AlembicExport.AnimTimeRange = maxExp_abc["AnimTimeRange"]
                    rt.AlembicExport.StartFrame = maxExp_abc["StartFrame"]
                    rt.AlembicExport.EndFrame = maxExp_abc["EndFrame"]

                # Export
                rt.exportFile(filePath, rt.Name("NoPrompt"), selectedOnly=exportSelected,
                              using=rt.Alembic_Export)
                return True

            else:
                rt.messageBox("Alembic Plugin cannot be initialized. Skipping", title="Alembic not supported")
                return False
        else:
            rt.messageBox("There is no alembic support for this version. Skipping", title="Alembic not supported")
            return False

    def _exportFbx(self, filePath, exportSettings, exportSelected=True, timeRange=[0,10]):
        """
        Exports FBX (.fbx) file
        Args:
            filePath: (String) Absolute File path for exported file
            exportSettings: (Dictionary) settings file (see getExportSettings)
            exportSelected: (Boolean) If True, exports only currently selected objects, else whole scene. Default True

        Returns: (Boolean) True for success False for failure

        """
        if rt.pluginManager.loadclass(rt.FBXEXP):
            maxExp_fbx = exportSettings["fbxExportMax"]

            # OVERRIDE ANIMATION SETTINGS
            if timeRange[0] != timeRange[1]:
                maxExp_fbx["Animation"] = True
                maxExp_fbx["BakeFrameStart"] = timeRange[0]
                maxExp_fbx["BakeFrameEnd"] = timeRange[1]
            else:
                maxExp_fbx["Animation"] = False

            # Set FBX Options
            for item in maxExp_fbx.items():
                rt.FBXExporterSetParam(rt.Name(item[0]), item[1])

            try:
                rt.exportFile(filePath, rt.Name("NoPrompt"), selectedOnly=exportSelected,
                              using=rt.FBXEXP)
                return True
            except:
                msg = "Cannot export FBX for unknown reason. Skipping FBX export"
                rt.messageBox(msg, title='Info')
                return False
        else:
            msg = "FBX Plugin cannot be initialized. Skipping FBX export"
            rt.messageBox(msg, title='Info')
            return False

    def _exportVray(self, filePath, exportSettings, exportSelected=True, timeRange=[0,10]):
        # TODO: // export vray core function for 3ds Max
        rt.messageBox("Vray Proxy Export for 3ds Max is under development", title='Info')
        return False

    def _exportRedshift(self, filePath, exportSettings, exportSelected=True, timeRange=[0,10]):
        # TODO: // export redshift core function for 3ds Max
        rt.messageBox("Redshift Proxy Export for 3ds Max is under development", title='Info')
        return False

    def _getSceneFile(self):
        s_path = fManager.GetFileNameAndPath()
        norm_s_path = os.path.normpath(s_path)
        return norm_s_path

    def _getProject(self):
        """returns the project folder DEFINED BY THE HOST SOFTWARE, not the Tik Manager Project"""
        norm_p_path = os.path.normpath(pManager.GetProjectFolderDir())
        return norm_p_path

    def _getVersion(self):
        return rt.maxversion()

    def _getCurrentFrame(self):
        return int(rt.sliderTime)

    def _getSelection(self, asMaxArray=False):
        sel = rt.execute("selection as array")
        if not asMaxArray:
            return [x.name for x in sel]
        else:
            return sel

    def _isSceneModified(self):
        return fManager.IsSaveRequired()

    def _getTimelineRanges(self):
        R_ast = int(rt.animationRange.start)
        R_min = int(rt.animationRange.start)
        R_max = int(rt.animationRange.end)
        R_aet = int(rt.animationRange.end)
        return [R_ast, R_min, R_max, R_aet]

    def _setTimelineRanges(self, rangeList):
        """Sets the timeline ranges [AnimationStart, Min, Max, AnimationEnd]"""
        rt.animationRange = rt.interval(rangeList[0], rangeList[-1])

    def _setFPS(self, fps, *args, **kwargs):
        pass

    def _getFPS(self, *args, **kwargs):
        pass