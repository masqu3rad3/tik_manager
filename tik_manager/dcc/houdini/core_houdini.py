import os
import hou
import logging

logging.basicConfig()
logger = logging.getLogger('coreFunctions_Houdini')
logger.setLevel(logging.WARNING)

class HoudiniCoreFunctions(object):
    def __init__(self):
        super(HoudiniCoreFunctions, self).__init__()

    def _new(self, force=True, fps=None):
        pass

    def _save(self, *args, **kwargs):
        hou.hipFile.save()

    def _saveAs(self, filePath, format=None, *args, **kwargs):
        hou.hipFile.save(file_name=filePath)

    def _load(self, filePath, force=True, *args, **kwargs):
        hou.hipFile.load(filePath, suppress_save_prompt=force, ignore_load_warnings=False)
        self._setEnvVariable('HIP', os.path.split(filePath)[0])

    def _reference(self, filePath):
        pass

    def _import(self, filePath, *args, **kwargs):
        hou.hipFile.merge(filePath, node_pattern="*", overwrite_on_conflict=False, ignore_load_warnings=False)

    def _importSequence(self, pySeq_sequence, *args, **kwargs):
        logger.warning("This function is not yet implemented")

    def _importObj(self, filePath, importSettings, *args, **kwargs):
        houdiniImp_obj = importSettings["objImportHoudini"]
        niceName = os.path.splitext(os.path.basename(filePath))[0]

        try: relPath = "$JOB\\%s" % (os.path.relpath(filePath, self.projectDir))
        except ValueError: relPath = filePath #if its on another drive, use absolute path

        node = hou.node('obj')
        objNode = node.createNode('geo', node_name=niceName)
        try: objNode.allSubChildren()[0].destroy()
        except IndexError: pass
        objNode.moveToGoodPosition()
        fileNode = objNode.createNode('file')
        # fileNode = objNode.allSubChildren()[0]
        fileNode.parm('file').set(relPath)

    def _importAlembic(self, filePath, importSettings, *args, **kwargs):
        houdiniImp_abc = importSettings["alembicImportHoudini"]
        niceName = os.path.splitext(os.path.basename(filePath))[0]

        # relPath = "$JOB\\%s" % (os.path.relpath(filePath, self._getProject()))
        try: relPath = "$JOB\\%s" % (os.path.relpath(filePath, self.projectDir))
        except ValueError: relPath = filePath #if its on another drive, use absolute path

        node = hou.node('obj')
        alembicNode = node.createNode('alembicarchive', node_name=niceName)
        alembicNode.moveToGoodPosition()
        alembicNode.parm('fileName').set(relPath)

        for item in houdiniImp_abc.items():
            alembicNode.parm(item[0]).set(item[1])
        alembicNode.parm('buildHierarchy').pressButton()

    def _importFbx(self, filePath, importSettings, *args, **kwargs):
        houdiniImp_fbx = importSettings["fbxImportHoudini"]
        niceName = os.path.splitext(os.path.basename(filePath))[0]

        ret = hou.hipFile.importFBX(filePath.replace(os.sep,'/'),
                              suppress_save_prompt=True,
                              merge_into_scene=True,
                              import_cameras=houdiniImp_fbx["import_cameras"],
                              import_joints_and_skin=houdiniImp_fbx["import_joints_and_skin"],
                              import_geometry=houdiniImp_fbx["import_geometry"],
                              import_lights=houdiniImp_fbx["import_lights"],
                              import_animation=houdiniImp_fbx["import_animation"],
                              import_materials=houdiniImp_fbx["import_materials"],
                              resample_animation=houdiniImp_fbx["resample_animation"],
                              resample_interval=houdiniImp_fbx["resample_interval"],
                              override_framerate=houdiniImp_fbx["override_framerate"],
                              framerate=houdiniImp_fbx["framerate"],
                              hide_joints_attached_to_skin=houdiniImp_fbx["hide_joints_attached_to_skin"],
                              convert_joints_to_zyx_rotation_order=houdiniImp_fbx["convert_joints_to_zyx_rotation_order"],
                              material_mode=hou.fbxMaterialMode.FBXShaderNodes,
                              compatibility_mode=hou.fbxCompatibilityMode.Maya,
                              single_precision_vertex_caches=houdiniImp_fbx["single_precision_vertex_caches"],
                              triangulate_nurbs=houdiniImp_fbx["triangulate_nurbs"],
                              triangulate_patches=houdiniImp_fbx["triangulate_patches"],
                              import_global_ambient_light=houdiniImp_fbx["import_global_ambient_light"],
                              import_blend_deformers_as_blend_sops=houdiniImp_fbx["import_blend_deformers_as_blend_sops"],
                              segment_scale_already_baked_in=houdiniImp_fbx["segment_scale_already_baked_in"],
                              convert_file_paths_to_relative=houdiniImp_fbx["convert_file_paths_to_relative"],
                              unlock_geometry=houdiniImp_fbx["unlock_geometry"],
                              unlock_deformations=houdiniImp_fbx["unlock_deformations"],
                              import_nulls_as_subnets=houdiniImp_fbx["import_nulls_as_subnets"],
                              import_into_object_subnet=houdiniImp_fbx["import_into_object_subnet"],
                              convert_into_y_up_coordinate_system=houdiniImp_fbx["convert_into_y_up_coordinate_system"]
                              )

        ret[0].setName(niceName)
        ret[0].moveToGoodPosition()

    def _importVray(self, filePath, importSettings, *args, **kwargs):
        # TODO: // import vray core function for Houdini
        hou.ui.displayMessage("Vray Proxy Import for Houdini is under development")

    def _importRedshift(self, filePath, importSettings, *args, **kwargs):
        # TODO: // import redshift core function for Houdini
        hou.ui.displayMessage("Redshift Proxy Import for Houdini is under development")

    def _exportObj(self, filePath, exportSettings, exportSelected=True):
        rootNode = hou.node('obj')
        if exportSelected:
            exportList = hou.selectedNodes()
        else:
            exportList = rootNode.children()

        if len(exportList) == 0:
            hou.ui.displayMessage("Nothing to export. Aborting")
            return False

        geoNode = rootNode.createNode('geo', node_name="tmpExport")
        try: geoNode.allSubChildren()[0].destroy()
        except IndexError: pass
        mergeNode = geoNode.createNode('object_merge')

        numObj = len(exportList)
        mergeNode.parm('numobj').set(numObj)
        mergeNode.parm('xformtype').set("local")
        # mergeNode.parm('pack').set(True)

        for x in range(numObj):
            parameter = 'objpath%s' % (x + 1)
            mergeNode.parm(parameter).set(exportList[x].path())

        # rop sop
        ropSop = geoNode.createNode('rop_geometry')
        ropSop.setInput(0, mergeNode)

        ropSop.parm('sopoutput').set(filePath)
        ropSop.render()
        # delete the export nodes
        geoNode.destroy()
        return True

    def _exportAlembic(self, filePath, exportSettings, exportSelected=True, timeRange=[0,10]):
        if hou.isApprentice():
            hou.ui.displayMessage("Alembic export is not supported in Houdini Apprentice. ")
            return False
        houdiniExp_abc = exportSettings["alembicExportHoudini"]

        rootNode = hou.node('obj')
        if exportSelected:
            exportList = hou.selectedNodes()
        else:
            exportList = rootNode.children()

        if len(exportList) == 0:
            hou.ui.displayMessage("Nothing to export. Aborting")
            return False


        geoNode = rootNode.createNode('geo', node_name="tmpExport")
        try: geoNode.allSubChildren()[0].destroy()
        except IndexError: pass
        mergeNode = geoNode.createNode('object_merge')

        numObj = len(exportList)
        mergeNode.parm('numobj').set(numObj)
        mergeNode.parm('xformtype').set("local")
        mergeNode.parm('pack').set(True)


        for x in range(numObj):
            parameter = 'objpath%s' % (x + 1)
            mergeNode.parm(parameter).set(exportList[x].path())

        # rop sop
        ropSop = geoNode.createNode('rop_alembic')
        ropSop.setInput(0, mergeNode)

        ropSop.parm('filename').set(filePath)

        # --------------
        # SET PROPERTIES
        # --------------

        # timeline:
        if timeRange[0] == timeRange[1]:
            ropSop.parm('trange').set("off")
        else:
            ropSop.parm('trange').set("normal")
            ropSop.parm('f1').deleteAllKeyframes()
            ropSop.parm('f2').deleteAllKeyframes()
            ropSop.parm('f1').set(timeRange[0])
            ropSop.parm('f2').set(timeRange[1])

        for item in houdiniExp_abc.items():
            ropSop.parm(item[0]).set(item[1])

        ropSop.render()
        # delete the export nodes
        geoNode.destroy()
        return True

    def _exportFbx(self, filePath, exportSettings, exportSelected=True, timeRange=[0,10]):
        if hou.isApprentice():
            hou.ui.displayMessage("FBX export is not supported in Houdini Apprentice. ")
            return False
        houdiniExp_fbx = exportSettings["fbxExportHoudini"]

        rootNode = hou.node('obj')
        if exportSelected:
            exportList = hou.selectedNodes()
        else:
            exportList = rootNode.children()

        if len(exportList) == 0:
            hou.ui.displayMessage("Nothing to export. Aborting")
            return False

        geoNode = rootNode.createNode('geo', node_name="tmpExport")
        try: geoNode.allSubChildren()[0].destroy()
        except IndexError: pass
        mergeNode = geoNode.createNode('object_merge')

        numObj = len(exportList)
        mergeNode.parm('numobj').set(numObj)
        mergeNode.parm('xformtype').set("local")
        mergeNode.parm('pack').set(True)


        for x in range(numObj):
            parameter = 'objpath%s' % (x + 1)
            mergeNode.parm(parameter).set(exportList[x].path())

        # rop sop
        ropSop = geoNode.createNode('rop_fbx')
        ropSop.setInput(0, mergeNode)

        ropSop.parm('sopoutput').set(filePath)

        # --------------
        # SET PROPERTIES
        # --------------

        # timeline:
        if timeRange[0] == timeRange[1]:
            ropSop.parm('trange').set("off")
        else:
            ropSop.parm('trange').set("normal")
            ropSop.parm('f1').deleteAllKeyframes()
            ropSop.parm('f2').deleteAllKeyframes()
            ropSop.parm('f1').set(timeRange[0])
            ropSop.parm('f2').set(timeRange[1])

        for item in houdiniExp_fbx.items():
            ropSop.parm(item[0]).set(item[1])

        ropSop.render()
        # delete the export nodes
        geoNode.destroy()
        return True

    def _exportVray(self, filePath, exportSettings, exportSelected=True, timeRange=[0,10]):
        # TODO: // export vray core function for Houdini
        hou.ui.displayMessage("Vray Proxy Export for Houdini is under development")
        return False

    def _exportRedshift(self, filePath, exportSettings, exportSelected=True, timeRange=[0,10]):
        # TODO: // export redshift core function for Houdini
        hou.ui.displayMessage("Redshift Proxy Export for Houdini is under development")
        return False

    def _getSceneFile(self):
        s_path = hou.hipFile.path()
        niceName = os.path.splitext(hou.hipFile.basename())[0]
        if niceName == "untitled":
            s_path = ""
        norm_s_path = os.path.normpath(s_path)
        return norm_s_path

    def _getProject(self):
        p_path = (hou.hscript('echo $JOB')[0])[:-1]  # [:-1] is for the extra \n
        norm_p_path = os.path.normpath(p_path)
        return norm_p_path

    def _setProject(self, path):
        self._setEnvVariable('JOB', path)

    def _getVersion(self):
        return hou.applicationVersion()

    def _getCurrentFrame(self):
        return hou.frame()

    def _getSelection(self):
        return hou.selectedItems()

    def _clearSelection(self):
        node = hou.node("/obj")
        hou.Node.setSelected(node, False, clear_all_selected=True)

    def _isSceneModified(self):
        return hou.hipFile.hasUnsavedChanges()

    def _setEnvVariable(self, var, value):
        """sets environment var
        :param str var: The name of the var
        :param value: The value of the variable
        """
        os.environ[var] = value
        try:
            hou.allowEnvironmentVariableToOverwriteVariable(var, True)
        except AttributeError:
            # should be Houdini 12
            hou.allowEnvironmentToOverwriteVariable(var, True)

        value = value.replace('\\', '/')
        hscript_command = "set -g %s = '%s'" % (var, value)

        hou.hscript(str(hscript_command))

    def _getTimelineRanges(self):
        pass
        R_ast = int(hou.playbar.frameRange()[0])
        R_min = int(hou.playbar.playbackRange()[0])
        R_max = int(hou.playbar.playbackRange()[1])
        R_aet = int(hou.playbar.frameRange()[1])
        return [R_ast, R_min, R_max, R_aet]

    def _setTimelineRanges(self, rangeList):
        """Sets the timeline ranges [AnimationStart, Min, Max, AnimationEnd]"""
        hou.playbar.setFrameRange(rangeList[0], rangeList[3])
        hou.playbar.setPlaybackRange(rangeList[1], rangeList[2])

    def _setFPS(self, fps, *args, **kwargs):
        pass

    def _getFPS(self, *args, **kwargs):
        pass