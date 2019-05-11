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

import sys, os

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