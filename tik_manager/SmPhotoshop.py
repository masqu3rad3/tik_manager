#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------------------------
# Copyright (c) 2017-2018, Arda Kutlu (ardakutlu@gmail.com)
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  - Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
#  - Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
#  - Neither the name of the software nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# -----------------------------------------------------------------------------
import datetime
import socket
import sys, os
import shutil

# Set the force pyqt environment variable to tell the other modulea not to use Qt.py module
os.environ["FORCE_QT4"]="True"
os.environ["PS_APP"]="True"

from PyQt4 import QtCore, Qt
from PyQt4 import QtGui as QtWidgets

import SmUIRoot
reload(SmUIRoot)
from SmRoot import RootManager
from SmUIRoot import MainUI as baseUI

import _version
# import subprocess

from win32com.client import Dispatch

# import pprint
import logging

psApp = Dispatch("Photoshop.Application")

__author__ = "Arda Kutlu"
__copyright__ = "Copyright 2018, Scene Manager for Photoshop"
__credits__ = []
__license__ = "GPL"
__maintainer__ = "Arda Kutlu"
__email__ = "ardakutlu@gmail.com"
__status__ = "Development"

SM_Version = "Scene Manager Photoshop v%s" %_version.__version__

logging.basicConfig()
logger = logging.getLogger('smPhotoshop')
logger.setLevel(logging.WARNING)

class PsManager(RootManager):
    def __init__(self):
        super(PsManager, self).__init__()
        # hard coded format dictionary to pass the format info to cmds
        self.formatDict = {"psd": "PSD", "psb": "PSB"}
        self.exportFormats = ["png", "jpg", "tif", "tga", "psd", "bmp"]
        self.textureTypes = ["Diffuse", "Opacity", "Reflection", "Subsurface", "Displacement", "Normal", "Cavity", "AO", "ID", "Mask", "Custom"]
        self.init_paths()
        self.init_database()

    def getSoftwarePaths(self):
        """Overriden function"""
        logger.debug("Func: getSoftwarePaths")

        softwareDatabaseFile = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "softwareDatabase.json"))
        softwareDB = self._loadJson(softwareDatabaseFile)
        # To tell the base class maya specific path names
        # print softwareDB
        return softwareDB["Photoshop"]

    def getProjectDir(self):
        """OVERRIDEN FUNCTION"""
        # get the projects file for standalone manager
        projectsDict = self._loadProjects()
        if not projectsDict:
            norm_p_path = os.path.normpath(os.path.expanduser("~"))
            projectsDict = {"PhotoshopProject": norm_p_path}

            self._saveProjects(projectsDict)
            return norm_p_path

        # get the project defined in the database file
        try:
            norm_p_path = projectsDict["PhotoshopProject"]
            if norm_p_path: #some error can save it as None
                return norm_p_path
            else:
                return os.path.normpath(os.path.expanduser("~"))
        except KeyError:
            norm_p_path = os.path.normpath(os.path.expanduser("~"))
            projectsDict = {"PhotoshopProject": norm_p_path}
            self._saveProjects(projectsDict)
            return norm_p_path

    def setProject(self, path):
        """Sets the project"""
        projectsDict = self._loadProjects()
        if not projectsDict:
            projectsDict = {"PhotoshopProject": path}
        else:
            projectsDict["PhotoshopProject"] = path
        self._saveProjects(projectsDict)
        self.projectDir = path
        self.init_paths()
        self.init_database()
        # self.initSoftwares()

    def getSceneFile(self):
        # """This method must be overridden to return the full scene path ('' for unsaved) of current scene"""
        logger.debug("Func: getSceneFile")
        try:
            activeDocument = psApp.Application.ActiveDocument
            docName = activeDocument.name
            docPath = activeDocument.path
            return os.path.join(docPath, docName)
        except:
            return False

    def saveBaseScene(self, categoryName, baseName, subProjectIndex=0, makeReference=False, versionNotes="", sceneFormat="psd", *args, **kwargs):
        """
        Saves the PS document with formatted name and creates a json file for the scene
        Args:
            category: (String) Category if the scene. Valid categories are 'Model', 'Animation', 'Rig', 'Shading', 'Other'
            baseName: (String) Base name of the document. Eg. 'initialConcept', 'CharacterA', 'BookDesign' etc...
            subProject: (Integer) The scene will be saved under the sub-project according to the given integer value. The 'self.subProjectList' will be
                searched with that integer.
            makeReference: (Boolean) This has no effect, needed for compatibility issues.
            versionNotes: (String) This string will be stored in the json file as version notes.
            *args:
            **kwargs:

        Returns: Scene DB Dictionary
        """
        logger.debug("Func: saveBaseScene")

        now = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M")
        completeNote = "[%s] on %s\n%s\n" % (self.currentUser, now, versionNotes)

        # Check if the base name is unique
        scenesToCheck = self.scanBaseScenes(categoryAs=categoryName, subProjectAs=subProjectIndex)
        for key in scenesToCheck.keys():
            if baseName.lower() == key.lower():
                msg = ("Base Scene Name is not unique!\nABORTING")
                self._exception(360, msg)
                return -1, msg

        projectPath = self.projectDir
        databaseDir = self._pathsDict["databaseDir"]
        scenesPath = self._pathsDict["scenesDir"]
        categoryPath = os.path.normpath(os.path.join(scenesPath, categoryName))
        self._folderCheck(categoryPath)

        ## if its going to be saved as a subproject
        if not subProjectIndex == 0:
            subProjectPath = os.path.normpath(os.path.join(categoryPath, self._subProjectsList[subProjectIndex]))
            self._folderCheck(subProjectPath)
            shotPath = os.path.normpath(os.path.join(subProjectPath, baseName))
            self._folderCheck(shotPath)

            jsonCategoryPath = os.path.normpath(os.path.join(databaseDir, categoryName))
            self._folderCheck(jsonCategoryPath)
            jsonCategorySubPath = os.path.normpath(os.path.join(jsonCategoryPath, self._subProjectsList[subProjectIndex]))
            self._folderCheck(jsonCategorySubPath)
            jsonFile = os.path.join(jsonCategorySubPath, "{}.json".format(baseName))

        else:
            shotPath = os.path.normpath(os.path.join(categoryPath, baseName))
            self._folderCheck(shotPath)

            jsonCategoryPath = os.path.normpath(os.path.join(databaseDir, categoryName))
            self._folderCheck(jsonCategoryPath)
            jsonFile = os.path.join(jsonCategoryPath, "{}.json".format(baseName))

        version = 1
        sceneName = "{0}_{1}_{2}_v{3}".format(baseName, categoryName, self._usersDict[self.currentUser], str(version).zfill(3))
        sceneFile = os.path.join(shotPath, "{0}.{1}".format(sceneName, sceneFormat))
        ## relativity update
        relSceneFile = os.path.relpath(sceneFile, start=projectPath)

        openDocs = psApp.Application.Documents
        if openDocs.Count == 0:
            activeDocument = psApp.Documents.Add(2048, 2048, 72)
        else:
            activeDocument = psApp.Application.ActiveDocument
        PhotoshopSaveOptions=Dispatch("Photoshop.PhotoshopSaveOptions")
        PhotoshopSaveOptions.AlphaChannels = True
        PhotoshopSaveOptions.Annotations = True
        PhotoshopSaveOptions.Layers = True
        PhotoshopSaveOptions.SpotColors = True
        activeDocument.SaveAs(sceneFile, PhotoshopSaveOptions, False)

        thumbPath = self.createThumbnail(dbPath=jsonFile, versionInt=version)

        jsonInfo = {}


        jsonInfo["ReferenceFile"] = None
        jsonInfo["ReferencedVersion"] = None

        jsonInfo["ID"] = "SmNukeV02_sceneFile"
        jsonInfo["PSVersion"] = psApp.Version
        jsonInfo["Name"] = baseName
        jsonInfo["Path"] = os.path.relpath(shotPath, start=projectPath)
        jsonInfo["Category"] = categoryName
        jsonInfo["Creator"] = self.currentUser
        jsonInfo["CreatorHost"] = (socket.gethostname())
        jsonInfo["Versions"] = [ # PATH => Notes => User Initials => Machine ID => Playblast => Thumbnail
            {"RelativePath": relSceneFile,
             "Note": completeNote,
             "User": self._usersDict[self.currentUser],
             "Workstation": socket.gethostname(),
             "Preview": {},
             "Thumb": thumbPath,
             "Ranges": ""
             }
        ]

        jsonInfo["SubProject"] = self._subProjectsList[subProjectIndex]
        self._dumpJson(jsonInfo, jsonFile)
        return [0, ""]

    def saveVersion(self, makeReference=False, versionNotes="", sceneFormat="mb", *args, **kwargs):
        """
        Saves a version for the predefined scene. The scene json file must be present at the /data/[Category] folder.
        Args:
            makeReference: (Boolean) ** Does nothing, consistency purposes
            versionNotes: (String) This string will be hold in the json file as well. Notes about the changes in the version.
            *args:
            **kwargs:

        Returns: Scene DB Dictionary

        """
        logger.debug("Func: saveVersion")

        now = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M")
        completeNote = "[%s] on %s\n%s\n" % (self.currentUser, now, versionNotes)

        sceneName = self.getSceneFile()
        if not sceneName:
            msg = "This is not a base scene (Untitled)"
            self._exception(360, msg)
            return -1, msg

        sceneInfo = self.getOpenSceneInfo()

        if sceneInfo: ## getCurrentJson returns None if the resolved json path is missing
            jsonFile = sceneInfo["jsonFile"]
            jsonInfo = self._loadJson(jsonFile)

            currentVersion = len(jsonInfo["Versions"]) + 1
            sceneName = "{0}_{1}_{2}_v{3}".format(jsonInfo["Name"], jsonInfo["Category"], self._usersDict[self.currentUser],
                                                  str(currentVersion).zfill(3))
            relSceneFile = os.path.join(jsonInfo["Path"], "{0}.{1}".format(sceneName, sceneFormat))

            sceneFile = os.path.join(sceneInfo["projectPath"], relSceneFile)

            # -- Save PSD
            activeDocument = psApp.Application.ActiveDocument
            PhotoshopSaveOptions=Dispatch("Photoshop.PhotoshopSaveOptions")
            PhotoshopSaveOptions.AlphaChannels = True
            PhotoshopSaveOptions.Annotations = True
            PhotoshopSaveOptions.Layers = True
            PhotoshopSaveOptions.SpotColors = True
            activeDocument.SaveAs(sceneFile, PhotoshopSaveOptions, False)

            thumbPath = self.createThumbnail(dbPath=jsonFile, versionInt=currentVersion)

            jsonInfo["Versions"].append(
                # PATH => Notes => User Initials => Machine ID => Playblast => Thumbnail
            # TODO : ref => Dict
                {"RelativePath": relSceneFile,
                 "Note": completeNote,
                 "User": self._usersDict[self.currentUser],
                 "Workstation": socket.gethostname(),
                 "Preview": {},
                 "Thumb": thumbPath,
                 "Ranges": ""
                 }
                )

            self._dumpJson(jsonInfo, jsonFile)
        else:
            msg = "This is not a base scene (Json file cannot be found)"
            self._exception(360, msg)
            return -1, msg
        return jsonInfo

    def getTextureVersions(self, baseSceneName):

        #resolve the available texture versions and return the list

        pass

    def exportAsSourceImage(self, format="jpg"):
        # ???
        if format not in self.exportFormats:
            msg = "Format is not valid. Valid formats are %s" %self.exportFormats
            self._exception(101, msg)
            return -1, msg
        # resolve path as <sourceImages folder>/<baseName>.<format>

        activeDocument = psApp.Application.ActiveDocument
        if format == "jpg":
            pass
            # jpgSaveOptions=Dispatch("Photoshop.JPEGSaveOptions")
            # jpgSaveOptions.EmbedColorProfile = True
            # jpgSaveOptions.FormatOptions = 1 # => psStandardBaseline
            # jpgSaveOptions.Matte = 1 # => No Matte
            # jpgSaveOptions.Quality = 12
            # activeDocument.SaveAs("E:\\JPGCopy", jpgSaveOptions, True)
        if format == "png":
            pass
        if format == "bmp":
            pass
        if format == "tga":
            pass
        if format == "psd":
            pass
        if format == "tif":
            pass


        pass


    def loadBaseScene(self, force=False):
        """Loads the scene at cursor position"""
        logger.debug("Func: loadBaseScene")
        relSceneFile = self._currentSceneInfo["Versions"][self._currentVersionIndex-1]["RelativePath"]
        absSceneFile = os.path.join(self.projectDir, relSceneFile)
        if os.path.isfile(absSceneFile):
            psApp.Open(absSceneFile)
            return 0
        else:
            msg = "File in Scene Manager database doesnt exist"
            self._exception(201, msg)
            return -1, msg

    def createThumbnail(self, useCursorPosition=False, dbPath = None, versionInt = None):
        """
        Creates the thumbnail file.
        :param databaseDir: (String) If defined, this folder will be used to store the created database.
        :param version: (integer) if defined this version number will be used instead currently open scene version.
        :return: (String) Relative path of the thumbnail file
        """

        logger.debug("Func: createThumbnail")
        projectPath = self.projectDir
        if useCursorPosition:
            versionInt = self.currentVersionIndex
            dbPath = self.currentDatabasePath
        else:
            if not dbPath or not versionInt:
                msg = "Both dbPath and version must be defined if useCursorPosition=False"
                raise Exception ([360, msg])

        versionStr = "v%s" % (str(versionInt).zfill(3))
        dbDir, shotNameWithExt = os.path.split(dbPath)
        shotName = os.path.splitext(shotNameWithExt)[0]

        thumbPath = "{0}_{1}_thumb.jpg".format(os.path.join(dbDir, shotName), versionStr)
        relThumbPath = os.path.relpath(thumbPath, projectPath)

        # create a thumbnail using playblast
        thumbDir = os.path.split(thumbPath)[0]
        if os.path.exists(thumbDir):
            psApp.Preferences.RulerUnits = 1
            activeDocument = psApp.Application.ActiveDocument
            dupDocument = activeDocument.Duplicate("thumbnailCopy", True)
            oWidth = 221
            oHeight = 124
            ratio = float(dupDocument.Width) / float(dupDocument.Height)
            if ratio <= 1.782:
                new_width = oHeight * ratio
                new_height = oHeight
            else:
                new_width = oWidth
                new_height = oWidth / ratio
            dupDocument.ResizeImage(new_width, new_height)
            dupDocument.ResizeCanvas(oWidth, oHeight)
            jpgSaveOptions = Dispatch("Photoshop.JPEGSaveOptions")
            jpgSaveOptions.EmbedColorProfile = True
            jpgSaveOptions.FormatOptions = 1  # => psStandardBaseline
            jpgSaveOptions.Matte = 1  # => No Matte
            jpgSaveOptions.Quality = 6
            dupDocument.SaveAs(thumbPath, jpgSaveOptions, True)
            dupDocument.Close(2)  # 2 means without saving
        else:
            print ("something went wrong with thumbnail. Skipping thumbnail")
            return ""
        return relThumbPath

    def preSaveChecklist(self):
        """Checks the scene for inconsistencies"""
        checklist = []

        # TODO check for something?
        # fpsValue_setting = self.getFPS()
        # fpsValue_current = nuke.root().fps()
        #
        # if fpsValue_setting is not fpsValue_current:
        #     msg = "FPS values are not matching with the project settings.\n Project FPS => {0}\n scene FPS => {1}\nDo you want to continue?".format(fpsValue_setting, fpsValue_current)
        #     checklist.append(msg)

        return checklist

    def compareVersions(self):
        """Compares the versions of current session and database version at cursor position"""
        logger.debug("Func: compareVersions")

        # assumes compatibilty maximized
        return 0, ""

    def isSceneModified(self):
        """Checks the currently open scene saved or not"""
        logger.debug("Func: isSceneModified")
        return False

    def _loadCategories(self):
        """OVERRIDEN FUNCTION for specific category default of Photoshop"""
        logger.debug("Func: _loadCategories")

        if os.path.isfile(self._pathsDict["categoriesFile"]):
            categoriesData = self._loadJson(self._pathsDict["categoriesFile"])
            if categoriesData == -2:
                return -2
        else:
            # categoriesData = self._sceneManagerDefaults["defaultCategories"]
            categoriesData = ["Concept", "Storyboard", "Texture", "Other"]
            self._dumpJson(categoriesData, self._pathsDict["categoriesFile"])
        return categoriesData


class MainUI(baseUI):
    """Main UI Class. Inherits SmUIRoot.py"""
    def __init__(self):
        super(MainUI, self).__init__()

        self.manager = PsManager()
        # self.manager = self._getManager()
        # problem, msg = self.manager._checkRequirements()
        # if problem:
        #     self.close()
        #     self.deleteLater()

        # self.windowName = "Tik Manager Photoshop v%s" %_version.__version__


        self.buildUI()
        self.extraMenus()
        self.modify()
        self.initMainUI(newborn=True)

        self.exportTextureUI()

    def extraMenus(self):
        """Adds extra menu and widgets to the base UI"""
        pass
        # self.software_comboBox = QtWidgets.QComboBox(self.centralwidget)
        # self.software_comboBox.setMinimumSize(QtCore.QSize(150, 30))
        # self.software_comboBox.setMaximumSize(QtCore.QSize(16777215, 30))
        # self.software_comboBox.setObjectName(("software_comboBox"))
        # self.r2_gridLayout.addWidget(self.software_comboBox, 0, 1, 1, 1)
        # self.software_comboBox.activated.connect(self.onSoftwareChange)

    def modify(self):
        """Modifications to the base UI"""
        pass
        # make sure load mode is checked and hidden
        self.load_radioButton.setChecked(True)
        self.load_radioButton.setVisible(False)
        self.reference_radioButton.setChecked(False)
        self.reference_radioButton.setVisible(False)

        self.makeReference_pushButton.setVisible(False)
        self.showPreview_pushButton.setVisible(False)
        #
        # self.baseScene_label.setVisible(False)
        # self.baseScene_lineEdit.setVisible(False)
        #
        # self.createPB.setVisible(False)
        #
        # self.saveVersion_pushButton.setVisible(False)
        # self.saveVersion_fm.setVisible(False)
        # self.saveBaseScene_pushButton.setVisible(False)
        # self.saveBaseScene_fm.setVisible(False)
        # self.scenes_rcItem_0.setVisible(False)
        #
        # self.changeCommonFolder.setVisible(True)
        # self.changeCommonFolder.triggered.connect(self.manager._defineCommonFolder)

    def exportTextureUI(self):
        self.exportTexture_Dialog = QtWidgets.QDialog(parent=self)
        self.exportTexture_Dialog.resize(336, 194)
        self.exportTexture_Dialog.setWindowTitle(("Export Textures"))

        self.verticalLayout = QtWidgets.QVBoxLayout(self.exportTexture_Dialog)
        self.verticalLayout.setObjectName(("verticalLayout"))

        self.resolvedName_label = QtWidgets.QLabel(self.exportTexture_Dialog)
        self.resolvedName_label.setText(("Resolved File Name"))
        self.resolvedName_label.setWordWrap(True)
        self.resolvedName_label.setObjectName(("resolvedName_label"))
        self.verticalLayout.addWidget(self.resolvedName_label)

        self.line = QtWidgets.QFrame(self.exportTexture_Dialog)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.verticalLayout.addWidget(self.line)

        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)
        self.formLayout.setRowWrapPolicy(QtWidgets.QFormLayout.DontWrapRows)
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.formLayout.setFormAlignment(QtCore.Qt.AlignCenter)
        self.formLayout.setSpacing(12)

        self.format_label = QtWidgets.QLabel(self.exportTexture_Dialog)
        self.format_label.setText(("Format:"))
        self.format_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.format_label)

        self.format_layout = QtWidgets.QHBoxLayout()

        self.format_comboBox = QtWidgets.QComboBox(self.exportTexture_Dialog)
        self.format_comboBox.setMinimumSize(QtCore.QSize(60, 16777215))
        self.format_comboBox.setMaximumSize(QtCore.QSize(200, 16777215))
        self.format_comboBox.setObjectName(("format_comboBox"))
        self.format_comboBox.addItems(self.manager.exportFormats)
        self.format_layout.addWidget(self.format_comboBox)

        self.alpha_checkBox = QtWidgets.QCheckBox(self.exportTexture_Dialog)
        self.alpha_checkBox.setText(("Alpha"))
        self.alpha_checkBox.setChecked(True)
        self.format_layout.addWidget(self.alpha_checkBox)

        self.formLayout.setLayout(0, QtWidgets.QFormLayout.FieldRole, self.format_layout)

        self.type_label = QtWidgets.QLabel(self.exportTexture_Dialog)
        self.type_label.setText(("Type:"))
        self.type_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.type_label)

        self.type_layout =  QtWidgets.QHBoxLayout()

        self.type_comboBox = QtWidgets.QComboBox(self.exportTexture_Dialog)
        self.type_comboBox.setMinimumSize(QtCore.QSize(75, 16777215))
        self.type_comboBox.setMaximumSize(QtCore.QSize(200, 16777215))
        self.type_comboBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.type_comboBox.setFrame(True)
        self.type_comboBox.addItems(self.manager.textureTypes)
        self.type_layout.addWidget(self.type_comboBox)

        self.customType_lineEdit = QtWidgets.QLineEdit(self.exportTexture_Dialog)
        self.type_layout.addWidget(self.customType_lineEdit)

        self.formLayout.setLayout(1, QtWidgets.QFormLayout.FieldRole, self.type_layout)

        self.version_label = QtWidgets.QLabel(self.exportTexture_Dialog)
        self.version_label.setText(("Version:"))
        self.version_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.version_label)

        self.horizontalLayout = QtWidgets.QHBoxLayout()

        version_spinBox = QtWidgets.QSpinBox(self.exportTexture_Dialog)
        version_spinBox.setMaximumSize(QtCore.QSize(50, 16777215))
        version_spinBox.setMinimum(1)
        version_spinBox.setMaximum(999)
        self.horizontalLayout.addWidget(version_spinBox)

        self.incremental_checkBox = QtWidgets.QCheckBox(self.exportTexture_Dialog)
        self.incremental_checkBox.setText(("Use Next Available Version"))
        self.incremental_checkBox.setChecked(True)
        self.horizontalLayout.addWidget(self.incremental_checkBox)

        self.formLayout.setLayout(2, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout)
        self.verticalLayout.addLayout(self.formLayout)

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        buttonBox = QtWidgets.QDialogButtonBox(self.exportTexture_Dialog)
        buttonBox.setGeometry(QtCore.QRect(20, 250, 220, 32))
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).setMinimumSize(QtCore.QSize(100, 30))
        buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setMinimumSize(QtCore.QSize(100, 30))

        buttonE = buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
        buttonE.setText('Export')
        buttonC = buttonBox.button(QtWidgets.QDialogButtonBox.Cancel)
        buttonC.setText('Cancel')


        self.verticalLayout.addWidget(buttonBox)

        def hideUnhideCustom():
            if self.type_comboBox.currentText() == "Custom":
                self.customType_lineEdit.setHidden(False)
            else:
                self.customType_lineEdit.setHidden(True)
        hideUnhideCustom()

        def enableDisableVersion():
            version_spinBox.setDisabled(self.incremental_checkBox.isChecked())

        enableDisableVersion()

        # SIGNALS
        # -------

        self.type_comboBox.currentIndexChanged.connect(hideUnhideCustom)
        self.incremental_checkBox.toggled.connect(enableDisableVersion)

        buttonC.clicked.connect(self.exportTexture_Dialog.reject)
        buttonE.clicked.connect(self.exportTexture_Dialog.accept)


        self.exportTexture_Dialog.show()

if __name__ == '__main__':
    selfLoc = os.path.dirname(os.path.abspath(__file__))
    app = QtWidgets.QApplication(sys.argv)
    stylesheetFile = os.path.join(selfLoc, "CSS", "darkorange.stylesheet")
    if os.path.isfile(stylesheetFile):
        with open(stylesheetFile, "r") as fh:
            app.setStyleSheet(fh.read())
    window = MainUI()
    window.show()
    sys.exit(app.exec_())