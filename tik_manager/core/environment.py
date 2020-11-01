import os
import tik_manager.core._version as _version

def get_dcc():
    """Returns the current dcc"""
    try:
        from maya import cmds
        return "maya"
    except ImportError: pass

    try:
        from pymxs import runtime
        return "3dsmax"
    except ImportError: pass

    try:
        import hou
        return "houdini"
    except ImportError: pass

    try:
        import nuke
        return "nuke"
    except ImportError: pass

    try:
        from PyQt5 import QtWidgets
        if  bool(os.getenv("PS_APP")):
            return "photoshop"
        else:
            return "standalone"
    except ImportError: pass

    return None

def get_environment_data():
    """Returns environment data dictionary"""
    all_dcc_data = {
        "maya": {
            "dcc": "maya",
            "core_module": "tik_manager.dcc.maya.core_maya",
            "core_class": "MayaCoreFunctions",
            "main_ui_title": "Tik Manager Maya v%s" % _version.__version__,
            "asset_library_title": "Asset Library Maya v%s" % _version.__version__,
            "image_viewer_title": "Image Viewer Maya v%s" % _version.__version__,
            "project_materials_title": "Project Materials Maya v%s" % _version.__version__,
            "scene_formats": ["mb", "ma"],
            "asset_formats": ["mb", "ma"],
        },
        "3dsmax": {
            "dcc": "3dsmax",
            "core_module": "tik_manager.dcc.max.core_max",
            "core_class": "MaxCoreFunctions",
            "main_ui_title": "Tik Manager 3dsMax v%s" % _version.__version__,
            "asset_library_title": "Asset Library 3dsMax v%s" % _version.__version__,
            "image_viewer_title": "Image Viewer 3dsMax v%s" % _version.__version__,
            "project_materials_title": "Project Materials 3dsMax v%s" % _version.__version__,
            "scene_formats": ["max"],
            "asset_formats": ["max"],
        },
        "houdini": {
            "dcc": "houdini",
            "core_module": "tik_manager.dcc.houdini.core_houdini",
            "core_class": "HoudiniCoreFunctions",
            "main_ui_title": "Tik Manager Houdini v%s" % _version.__version__,
            "asset_library_title": "Asset Library Houdini v%s" % _version.__version__,
            "image_viewer_title": "Image Viewer Houdini v%s" % _version.__version__,
            "project_materials_title": "Project Materials Houdini v%s" % _version.__version__,
            "scene_formats": ["hip", "hiplc"],
            "asset_formats": ["hda"],
        },
        "nuke": {
            "dcc": "nuke",
            "core_module": "tik_manager.dcc.nuke.core_nuke",
            "core_class": "NukeCoreFunctions",
            "main_ui_title": "Tik Manager Nuke v%s" % _version.__version__,
            "asset_library_title": "Asset Library Nuke v%s" % _version.__version__,
            "image_viewer_title": "Image Viewer Nuke v%s" % _version.__version__,
            "project_materials_title": "Project Materials Nuke v%s" % _version.__version__,
            "scene_formats": ["nk"],
            "asset_formats": None,
        },
        "photoshop": {
            "dcc": "photoshop",
            "core_module": "tik_manager.dcc.photoshop.core_photoshop",
            "core_class": "PsCoreFunctions",
            "main_ui_title": "Tik Manager Photoshop v%s" % _version.__version__,
            "asset_library_title": "Asset Library Photoshop v%s" % _version.__version__,
            "image_viewer_title": "Image Viewer Photoshop v%s" % _version.__version__,
            "project_materials_title": "Project Materials Photoshop v%s" % _version.__version__,
            "scene_formats": ["psd", "psb"],
            "asset_formats": None,
        },
        "standalone": {
            "dcc": "standalone",
            "core_module": "tik_manager.dcc.standalone.core_standalone",
            "core_class": "StandaloneCoreFunctions",
            "main_ui_title": "Tik Manager Standalone v%s" % _version.__version__,
            "asset_library_title": "Asset Library Standalone v%s" % _version.__version__,
            "image_viewer_title": "Image Viewer Standalone v%s" % _version.__version__,
            "project_materials_title": "Project Materials Standalone v%s" % _version.__version__,
            "scene_formats": None,
            "asset_formats": None,
        },
    }

    dcc = get_dcc()
    return all_dcc_data.get(dcc)

def getMainWindow(dcc=None):
    """Returns main window"""
    if not dcc:
        dcc = get_dcc()

    if dcc == "maya":
        from tik_manager.ui.Qt import QtCompat, QtWidgets
        from maya import OpenMayaUI as omui
        win = omui.MQtUtil_mainWindow()
        ptr = QtCompat.wrapInstance(int(win), QtWidgets.QMainWindow)
        return ptr

    elif dcc == "3dsmax":
        from pymxs import runtime
        from PySide2.QtWidgets import QWidget
        return QWidget.find(runtime.windows.getMAXHWND())

    elif dcc == "houdini":
        import hou
        return hou.qt.mainWindow()

    elif dcc == "nuke":
        from tik_manager.ui.Qt import QtWidgets
        app = QtWidgets.QApplication.instance()
        for widget in app.topLevelWidgets():
            if widget.metaObject().className() == 'Foundry::UI::DockMainWindow':
                return widget
        return None
    else:
        return None