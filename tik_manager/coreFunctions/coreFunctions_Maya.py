import os
import maya.cmds as cmds
import maya.mel as mel
import logging

logging.basicConfig()
logger = logging.getLogger('coreFunctions_Maya')
logger.setLevel(logging.WARNING)

class MayaCoreFunctions(object):
    def __init__(self):
        super(MayaCoreFunctions, self).__init__()

    def _new(self, force=True, fps=None):
        cmds.file(new=True, f=force)
        if fps:
            fpsDict = {15: "game",
                       24: "film",
                       25: "pal",
                       30: "ntsc",
                       48: "show",
                       50: "palf",
                       60: "ntscf"}
            ranges = self._getTimelineRanges()
            cmds.currentUnit(time=fpsDict[fps])
            self._setTimelineRanges(ranges)
            cmds.currentTime(1)

    def _save(self, *args, **kwargs):
        cmds.file(save=True)

    def _saveAs(self, filePath, format, *args, **kwargs):
        cmds.file(rename=filePath)
        cmds.file(save=True, type=format)

    def _load(self, filePath, force=True, *args, **kwargs):
        cmds.file(filePath, o=True, force=force)

    def _reference(self, filePath, namespace):
        cmds.file(os.path.normpath(filePath), reference=True, gl=True, mergeNamespacesOnClash=False,
                  namespace=namespace)

    def _import(self, filePath, *args, **kwargs):
        cmds.file(filePath, i=True)

    def _importSequence(self, pySeq_sequence, *args, **kwargs):
        logger.warning("This function is not yet implemented")

    def _importObj(self, filePath, importSettings, *args, **kwargs):
        mayaImp_obj = importSettings["objImportMaya"]

        opFlag = ""
        for item in mayaImp_obj.items():
            opFlag = "%s %s" %(opFlag, item[1])

        cmds.file(filePath, i=True, op=opFlag)

    def _importAlembic(self, filePath, importSettings, *args, **kwargs):
        mayaImp_alembic = importSettings["alembicImportMaya"]

        if not cmds.pluginInfo('AbcImport.mll', l=True, q=True):
            try:
                cmds.loadPlugin('AbcImport.mll')
            except:
                msg = "Alembic Import Plugin cannot be initialized. Skipping"
                cmds.confirmDialog(title='Plugin Error', message=msg)
                return False

        cmds.AbcImport(filePath, ftr=mayaImp_alembic["fitTimeRange"], sts=mayaImp_alembic["setToStartFrame"])

    def _importFbx(self, filePath, importSettings, *args, **kwargs):
        mayaImp_fbx = importSettings["fbxImportMaya"]
        if not cmds.pluginInfo('fbxmaya', l=True, q=True):
            try:
                cmds.loadPlugin('fbxmaya')
            except:
                msg = "FBX Plugin cannot be initialized. Skipping"
                cmds.confirmDialog(title='Plugin Error', message=msg)
                return False

        for item in mayaImp_fbx.items():
            # TODO : Test with more versions of Maya
            mel.eval('%s %s' % (item[0], item[1]))

        try:
            compFilePath = filePath.replace("\\", "//")  ## for compatibility with mel syntax.
            cmd = ('FBXImport -f "{0}";'.format(compFilePath))
            mel.eval(cmd)
            return True
        except:
            msg = "Cannot import FBX for unknown reason. Skipping"
            cmds.confirmDialog(title='Unknown Error', message=msg)
            return False

    def _importVray(self, filePath, importSettings, *args, **kwargs):
        # cmds.confirmDialog(title='Ongoing development', message="Vray Proxy Import for Maya is under development")
        directory, name = os.path.split(filePath)
        cmds.vrayCreateProxy(node="%s" %name, existing=True, dir=filePath, createProxyNode=True)

    def _importRedshift(self, filePath, importSettings, *args, **kwargs):
        # TODO: // import redshift core function for Maya
        cmds.confirmDialog(title='Ongoing development', message="Redshift Proxy Import for Maya is under development")

    def _exportObj(self, filePath, exportSettings=None, exportSelected=True):
        """
        Exports wavefront Obj file
        Args:
            filePath: (String) Absolute File path for exported file
            exportSettings: (Dictionary) settings file (see getExportSettings)
            exportSelected: (Boolean) If True, exports only currently selected objects, else whole scene. Default True

        Returns: (Boolean) True for success False for failure

        """
        mayaExp_obj = exportSettings["objExportMaya"]
        if not cmds.pluginInfo('objExport', l=True, q=True):
            try:
                cmds.loadPlugin('objExport')
            except:
                msg = "Wavefront(Obj) Export Plugin cannot be initialized. Skipping Obj export"
                cmds.confirmDialog(title='Plugin Error', message=msg)
                return False

        opFlag = "groups={0}; ptgroups={1}; materials={2}; smoothing={3}; normals={4}".format(
            mayaExp_obj["groups"],
            mayaExp_obj["ptgroups"],
            mayaExp_obj["materials"],
            mayaExp_obj["smoothing"],
            mayaExp_obj["normals"]
        )
        try:
            cmds.file(os.path.splitext(filePath)[0], pr=True, force=True, typ="OBJexport", es=exportSelected,
                      ea=not exportSelected, op=opFlag)
            return True
        except:
            msg = "Cannot export OBJ for unknown reason. Skipping OBJ export"
            cmds.confirmDialog(title='Unknown Error', message=msg)
            return False

    def _exportAlembic(self, filePath, exportSettings=None, exportSelected=True, timeRange=[0,10]):
        """
        Exports Alembic (.abc) file
        Args:
            filePath: (String) Absolute File path for exported file
            exportSettings: (Dictionary) settings file (see getExportSettings)
            exportSelected: (Boolean) If True, exports only currently selected objects, else whole scene. Default True

        Returns: (Boolean) True for success False for failure

        """
        mayaExp_alembic = exportSettings["alembicExportMaya"]
        # TODO : THIS WILL FAIL ON LINUX!!! What were you thinking???
        if not cmds.pluginInfo('AbcExport.mll', l=True, q=True):
            try:
                cmds.loadPlugin('AbcExport.mll')
            except:
                msg = "Alembic Export Plugin cannot be initialized. Skipping Alembic export"
                cmds.confirmDialog(title='Plugin Error', message=msg)
                return False

        root = ""
        if exportSelected:
            selection = cmds.ls(sl=True)
            for x in selection:
                root = "%s-root %s " % (root, x)
            root = root[:-1]


        # edit in - out
        mayaExp_alembic["frameRange"] = "%s %s" %(timeRange[0], timeRange[1])

        flags = ""
        for item in mayaExp_alembic.items():
            if type(item[1]) != bool:
                flags = "%s-%s %s " % (flags, item[0], item[1])
            else:
                if item[1]: # if flag is true:
                    flags = "%s-%s " %(flags, item[0])
                else:
                    pass
        flags = flags[:-1]

        command = "-file {0} {1} {2}".format(filePath, flags, root)

        try:
            cmds.AbcExport(j=command)
            return True
        except:
            msg = "Cannot export Alembic for unknown reason. Skipping Alembic export"
            cmds.confirmDialog(title='Unknown Error', message=msg)
            return False

    def _exportFbx(self, filePath, exportSettings=None, exportSelected=True, timeRange=[0,10]):
        # TODO : TEST EXPORT RANGES, SINGLE FRAMES, ETC
        """
        Exports FBX (.fbx) file
        Args:
            filePath: (String) Absolute File path for exported file
            exportSettings: (Dictionary) settings file (see getExportSettings)
            exportSelected: (Boolean) If True, exports only currently selected objects, else whole scene. Default True

        Returns: (Boolean) True for success False for failure

        """
        mayaExp_fbx = exportSettings["fbxExportMaya"]

        if not cmds.pluginInfo('fbxmaya', l=True, q=True):
            try:
                cmds.loadPlugin('fbxmaya')
            except:
                msg = "FBX Export Plugin cannot be initialized. Skipping FBX export"
                cmds.confirmDialog(title='Plugin Error', message=msg)
                return False

        expSelectedFlag = "-s" if exportSelected else ""

        # OVERRIDE ANIMATION SETTINGS
        if timeRange[0] != timeRange[1]:
            mayaExp_fbx["FBXExportBakeComplexStart"] = "-v %s" %timeRange[0]
            mayaExp_fbx["FBXExportBakeComplexEnd"] = "-v %s" %timeRange[1]
        else:
            mayaExp_fbx["FBXExportBakeComplexAnimation"] = "-v false"

        for item in mayaExp_fbx.items():
            # TODO : Test with more versions of Maya
            mel.eval('%s %s'%(item[0], item[1]))

        try:
            compFilePath = filePath.replace("\\", "//")  ## for compatibility with mel syntax.
            cmd = ('FBXExport -f "{0}"{1};'.format(compFilePath, expSelectedFlag))
            mel.eval(cmd)
            return True
        except:
            msg = "Cannot export FBX for unknown reason. Skipping"
            cmds.confirmDialog(title='Unknown Error', message=msg)
            return False

    def _exportVray(self, filePath, exportSettings, exportSelected=True, timeRange=[0,10]):
        # TODO: // export vray core function for Maya
        # cmds.confirmDialog(title='Ongoing development', message="Vray Proxy Export for Maya is under development")

        # mayaExp_vrayProxy = exportSettings["vrayProxyExportMaya"]

        # export settings / Choices / Default Value:
        # exportType / 1 2 / 1
        # velocityOn / True False / True
        # velocityIntervalStart / 0.0 1.0 /0.0
        # velocityIntervalEnd / 0.0 1.0 /0.050
        # pointSize / 0.0 1.0 / 0.0
        # previewFaces / Integer / 10000
        # previewType / "clustering" "edge_collapse" "face_sampling" "combined" / "clustering"
        # vertexColorsOn / True False / False
        # ignoreHiddenObjects / True False / True
        # oneVoxelPerMesh / True False / False
        # facesPerVoxel / Integer / 20000
        # createProxyNode / True False / False
        # makeBackup / True False / False




        if not cmds.pluginInfo('vrayformaya.mll', l=True, q=True):
            try:
                cmds.loadPlugin('vrayformaya.mll')
            except:
                msg = "Vray cannot be initialized. Skipping Vray Proxy export"
                cmds.confirmDialog(title='Plugin Error', message=msg)
                return False

        originalSelection = cmds.ls(sl=True)
        if not exportSelected:
            cmds.SelectAll()

        # OVERRIDE ANIMATION SETTINGS
        if timeRange[0] != timeRange[1]:
            animOn = True
        else:
            animOn = False


        directory, name = os.path.split(filePath)
        proxyNode = "%s_proxy" %name

        cmds.vrayCreateProxy(dir=directory, fname=name, overwrite=True, animOn=animOn, animType=3, startFrame=timeRange[0], endFrame=timeRange[1], node=proxyNode,
                             exportType=1,
                             makeBackup=False,
                             velocityOn=True,
                             velocityIntervalStart=0.0,
                             velocityIntervalEnd=0.050,
                             pointSize=0.0,
                             previewFaces=10000,
                             previewType="clustering",
                             vertexColorsOn=False,
                             ignoreHiddenObjects=True,
                             oneVoxelPerMesh=False,
                             facesPerVoxel=20000,
                             createProxyNode=False)

        # re-select original selection
        cmds.select(originalSelection)
        return False

    def _exportRedshift(self, filePath, exportSettings, exportSelected=True, timeRange=[0,10]):
        # TODO: // export redshift core function for Maya
        cmds.confirmDialog(title='Ongoing development', message="Redshift Proxy Export for Maya is under development")
        return False

    def _getSceneFile(self):
        s_path = cmds.file(q=True, sn=True)
        norm_s_path = os.path.normpath(s_path)
        return norm_s_path

    def _getProject(self):
        pPath = cmds.workspace(q=1, rd=1)
        return os.path.normpath(pPath)

    def _setProject(self, path):
        encodedPath = unicode(path).encode("utf-8")
        # melCompPath = path.replace("\\", "/") # mel is picky
        melCompPath = encodedPath.replace("\\", "/") # mel is picky
        melCompPath = melCompPath.replace("file:", "/") # compatibility with network paths
        command = 'setProject "%s";' %melCompPath
        mel.eval(command)

    def _getVersion(self):
        return cmds.about(q=True, api=True)

    def _getCurrentFrame(self):
        return cmds.currentTime(query=True)

    def _getSelection(self):
        return cmds.ls(sl=True)

    def _isSceneModified(self):
        return cmds.file(q=True, modified=True)

    def _getCameras(self):
        return cmds.ls(type="camera")

    def _getTimelineRanges(self):
        # TODO : Make sure the time ranges are INTEGERS
        R_ast = cmds.playbackOptions(q=True, ast=True)
        R_min = cmds.playbackOptions(q=True, min=True)
        R_max = cmds.playbackOptions(q=True, max=True)
        R_aet = cmds.playbackOptions(q=True, aet=True)
        return [R_ast, R_min, R_max, R_aet]

    def _setTimelineRanges(self, rangeList):
        """Sets the timeline ranges [AnimationStart, Min, Max, AnimationEnd]"""
        # TODO : Make sure the time ranges are INTEGERS
        print("DB", rangeList)
        cmds.playbackOptions(ast=rangeList[0], min=rangeList[1], max=rangeList[2], aet=rangeList[3])

    def _setFPS(self, fps, *args, **kwargs):
        pass

    def _getFPS(self, *args, **kwargs):
        pass