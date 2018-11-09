# Module to view and organize project materials


import os
import sys
import _version

FORCE_QT4 = bool(os.getenv("FORCE_QT4"))
if FORCE_QT4:
    from PyQt4 import QtCore, Qt
    from PyQt4 import QtGui as QtWidgets
else:
    import Qt
    from Qt import QtWidgets, QtCore, QtGui

import pyseq as seq

import json
import datetime
from shutil import copyfile

__author__ = "Arda Kutlu"
__copyright__ = "Copyright 2018, Scene Manager - Project materials"
__credits__ = []
__license__ = "GPL"
__maintainer__ = "Arda Kutlu"
__email__ = "ardakutlu@gmail.com"
__status__ = "Development"

BoilerDict = {"Environment":"Standalone",
              "MainWindow":None,
              "WindowTitle":"Project Materials - Standalone v%s" %_version.__version__,
              "Stylesheet": "mayaDark.stylesheet"}

# ---------------
# GET ENVIRONMENT
# ---------------
try:
    from maya import OpenMayaUI as omui
    import maya.cmds as cmds
    BoilerDict["Environment"] = "Maya"
    BoilerDict["WindowTitle"] = "Image Viewer Maya v%s" %_version.__version__
    if Qt.__binding__ == "PySide":
        from shiboken import wrapInstance
    elif Qt.__binding__.startswith('PyQt'):
        from sip import wrapinstance as wrapInstance
    else:
        from shiboken2 import wrapInstance
except ImportError:
    pass

try:
    import MaxPlus
    BoilerDict["Environment"] = "3dsMax"
    BoilerDict["WindowTitle"] = "Scene Manager 3ds Max v%s" %_version.__version__
except ImportError:
    pass

try:
    import hou
    BoilerDict["Environment"] = "Houdini"
    BoilerDict["WindowTitle"] = "Scene Manager Houdini v%s" %_version.__version__
except ImportError:
    pass

try:
    import nuke
    BoilerDict["Environment"] = "Nuke"
    BoilerDict["WindowTitle"] = "Scene Manager Nuke v%s" % _version.__version__
except ImportError:
    pass

def getMainWindow():
    """This function should be overriden"""
    if BoilerDict["Environment"] == "Maya":
        win = omui.MQtUtil_mainWindow()
        ptr = wrapInstance(long(win), QtWidgets.QMainWindow)
        return ptr

    elif BoilerDict["Environment"] == "3dsMax":
        return MaxPlus.GetQMaxWindow()

    elif BoilerDict["Environment"] == "Houdini":
        return hou.qt.mainWindow()

    elif BoilerDict["Environment"] == "Nuke":
        # TODO // Needs a main window getter for nuke
        return None

    else:
        return None

def getProject():
    """Returns the project folder"""
    if BoilerDict["Environment"] == "Maya":
        return os.path.normpath(cmds.workspace(q=1, rd=1))
    elif BoilerDict["Environment"] == "3dsMax":
        return os.path.normpath(MaxPlus.PathManager.GetProjectFolderDir())
    elif BoilerDict["Environment"] == "Houdini":
        return os.path.normpath((hou.hscript('echo $JOB')[0])[:-1]) # [:-1] is for the extra \n
    elif BoilerDict["Environment"] == "Nuke":
        # TODO // Needs a project getter for nuke
        return os.path.normpath(os.path.join(os.path.expanduser("~")))
    else:
        return os.path.normpath(os.path.join(os.path.expanduser("~")))


class MainUI(QtWidgets.QMainWindow):
    """Main UI function"""
    def __init__(self, projectPath=None, relativePath=None, recursive=False):
        for entry in QtWidgets.QApplication.allWidgets():
            try:
                if entry.objectName() == BoilerDict["Environment"]:
                    entry.close()
            except AttributeError:
                pass
        parent = getMainWindow()
        super(MainUI, self).__init__(parent=parent)
        # super(MainUI, self).__init__()

        # Set Stylesheet
        # dirname = os.path.dirname(os.path.abspath(__file__))
        # # stylesheetFile = os.path.join(dirname, "CSS", "darkorange.stylesheet")
        # stylesheetFile = os.path.join(dirname, "CSS", BoilerDict["Stylesheet"])

        # with open(stylesheetFile, "r") as fh:
        #     self.setStyleSheet(fh.read())


        if projectPath:
            self.projectPath=str(projectPath)
        else:
            self.projectPath = getProject()

        if relativePath:
            self.rootPath = os.path.join(self.projectPath, str(relativePath))
        else:
            self.rootPath = os.path.join(self.projectPath, "images")
            if not os.path.isdir(self.rootPath):
                self.rootPath = self.projectPath

        # self.databaseDir = os.path.normpath(os.path.join(self.projectPath, "smDatabase"))
        #
        # if not os.path.isdir(self.databaseDir):
        #     msg=["Nothing to view", "No Scene Manager Database",
        #      "There is no Scene Manager Database Folder in this project path"]
        #     q = QtWidgets.QMessageBox()
        #     q.setIcon(QtWidgets.QMessageBox.Information)
        #     q.setText(msg[0])
        #     q.setInformativeText(msg[1])
        #     q.setWindowTitle(msg[2])
        #     q.setStandardButtons(QtWidgets.QMessageBox.Ok)
        #     ret = q.exec_()
        #     if ret == QtWidgets.QMessageBox.Ok:
        #         self.close()
        #         self.deleteLater()


        self.setObjectName(BoilerDict["Environment"])
        # self.resize(670, 624)
        self.setWindowTitle(BoilerDict["WindowTitle"])
        self.centralwidget = QtWidgets.QWidget(self)

        self.buildUI()

        self.setCentralWidget(self.centralwidget)

        self.show()

    def buildUI(self):

        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_6.setObjectName(("verticalLayout_6"))
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setToolTip((""))
        self.tabWidget.setStatusTip((""))
        self.tabWidget.setWhatsThis((""))
        self.tabWidget.setAccessibleName((""))
        self.tabWidget.setAccessibleDescription((""))
        self.tabWidget.setObjectName(("tabWidget"))
        self.stb_tab = QtWidgets.QWidget()
        self.stb_tab.setToolTip((""))
        self.stb_tab.setStatusTip((""))
        self.stb_tab.setWhatsThis((""))
        self.stb_tab.setAccessibleName((""))
        self.stb_tab.setAccessibleDescription((""))
        self.stb_tab.setObjectName(("stb_tab"))
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.stb_tab)
        self.verticalLayout_5.setObjectName(("verticalLayout_5"))
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName(("horizontalLayout"))
        self.stb_label = QtWidgets.QLabel(self.stb_tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stb_label.sizePolicy().hasHeightForWidth())
        self.stb_label.setSizePolicy(sizePolicy)
        self.stb_label.setMinimumSize(QtCore.QSize(221, 124))
        self.stb_label.setMaximumSize(QtCore.QSize(9999, 9999))
        self.stb_label.setSizeIncrement(QtCore.QSize(1, 1))
        self.stb_label.setBaseSize(QtCore.QSize(0, 0))
        self.stb_label.setToolTip((""))
        self.stb_label.setStatusTip((""))
        self.stb_label.setWhatsThis((""))
        self.stb_label.setAccessibleName((""))
        self.stb_label.setAccessibleDescription((""))
        self.stb_label.setFrameShape(QtWidgets.QFrame.Box)
        self.stb_label.setText(("Storyboard"))
        self.stb_label.setScaledContents(False)
        self.stb_label.setAlignment(QtCore.Qt.AlignCenter)
        self.stb_label.setObjectName(("stb_label"))
        self.horizontalLayout.addWidget(self.stb_label)
        self.stb_tableWidget = QtWidgets.QTableWidget(self.stb_tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stb_tableWidget.sizePolicy().hasHeightForWidth())
        self.stb_tableWidget.setSizePolicy(sizePolicy)
        self.stb_tableWidget.setToolTip((""))
        self.stb_tableWidget.setStatusTip((""))
        self.stb_tableWidget.setWhatsThis((""))
        self.stb_tableWidget.setAccessibleName((""))
        self.stb_tableWidget.setAccessibleDescription((""))
        self.stb_tableWidget.setObjectName(("stb_tableWidget"))
        self.stb_tableWidget.setColumnCount(2)
        self.stb_tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        item.setText(("Name"))
        self.stb_tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(("Date"))
        self.stb_tableWidget.setHorizontalHeaderItem(1, item)
        self.stb_tableWidget.horizontalHeader().setStretchLastSection(True)
        self.horizontalLayout.addWidget(self.stb_tableWidget)
        self.verticalLayout_5.addLayout(self.horizontalLayout)
        self.addStb_pushButton = QtWidgets.QPushButton(self.stb_tab)
        self.addStb_pushButton.setMinimumSize(QtCore.QSize(0, 40))
        self.addStb_pushButton.setToolTip((""))
        self.addStb_pushButton.setStatusTip((""))
        self.addStb_pushButton.setWhatsThis((""))
        self.addStb_pushButton.setAccessibleName((""))
        self.addStb_pushButton.setAccessibleDescription((""))
        self.addStb_pushButton.setText(("Add New Storyboard"))
        self.addStb_pushButton.setObjectName(("addStb_pushButton"))
        self.verticalLayout_5.addWidget(self.addStb_pushButton)
        self.tabWidget.addTab(self.stb_tab, ("Storyboard"))
        self.brief_tab = QtWidgets.QWidget()
        self.brief_tab.setToolTip((""))
        self.brief_tab.setStatusTip((""))
        self.brief_tab.setWhatsThis((""))
        self.brief_tab.setAccessibleName((""))
        self.brief_tab.setAccessibleDescription((""))
        self.brief_tab.setObjectName(("brief_tab"))
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.brief_tab)
        self.verticalLayout_4.setObjectName(("verticalLayout_4"))
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(("horizontalLayout_2"))
        self.brief_textEdit = QtWidgets.QTextEdit(self.brief_tab)
        self.brief_textEdit.setToolTip((""))
        self.brief_textEdit.setStatusTip((""))
        self.brief_textEdit.setWhatsThis((""))
        self.brief_textEdit.setAccessibleName((""))
        self.brief_textEdit.setAccessibleDescription((""))
        self.brief_textEdit.setObjectName(("brief_textEdit"))
        self.horizontalLayout_2.addWidget(self.brief_textEdit)
        self.brief_tableWidget = QtWidgets.QTableWidget(self.brief_tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.brief_tableWidget.sizePolicy().hasHeightForWidth())
        self.brief_tableWidget.setSizePolicy(sizePolicy)
        self.brief_tableWidget.setToolTip((""))
        self.brief_tableWidget.setStatusTip((""))
        self.brief_tableWidget.setWhatsThis((""))
        self.brief_tableWidget.setAccessibleName((""))
        self.brief_tableWidget.setAccessibleDescription((""))
        self.brief_tableWidget.setObjectName(("brief_tableWidget"))
        self.brief_tableWidget.setColumnCount(2)
        self.brief_tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        item.setText(("Name"))
        self.brief_tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(("Date"))
        self.brief_tableWidget.setHorizontalHeaderItem(1, item)
        self.brief_tableWidget.horizontalHeader().setStretchLastSection(True)
        self.horizontalLayout_2.addWidget(self.brief_tableWidget)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)
        self.addBrief_pushButton = QtWidgets.QPushButton(self.brief_tab)
        self.addBrief_pushButton.setMinimumSize(QtCore.QSize(0, 40))
        self.addBrief_pushButton.setText(("Add New Document"))
        self.addBrief_pushButton.setObjectName(("addBrief_pushButton"))
        self.verticalLayout_4.addWidget(self.addBrief_pushButton)
        self.tabWidget.addTab(self.brief_tab, ("Brief"))
        self.artwork_tab = QtWidgets.QWidget()
        self.artwork_tab.setToolTip((""))
        self.artwork_tab.setStatusTip((""))
        self.artwork_tab.setWhatsThis((""))
        self.artwork_tab.setAccessibleName((""))
        self.artwork_tab.setAccessibleDescription((""))
        self.artwork_tab.setObjectName(("artwork_tab"))
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.artwork_tab)
        self.verticalLayout_3.setObjectName(("verticalLayout_3"))
        self.artwork_tableWidget = QtWidgets.QTableWidget(self.artwork_tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.artwork_tableWidget.sizePolicy().hasHeightForWidth())
        self.artwork_tableWidget.setSizePolicy(sizePolicy)
        self.artwork_tableWidget.setToolTip((""))
        self.artwork_tableWidget.setStatusTip((""))
        self.artwork_tableWidget.setWhatsThis((""))
        self.artwork_tableWidget.setAccessibleName((""))
        self.artwork_tableWidget.setAccessibleDescription((""))
        self.artwork_tableWidget.setObjectName(("artwork_tableWidget"))
        self.artwork_tableWidget.setColumnCount(3)
        self.artwork_tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        item.setText(("Name"))
        self.artwork_tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(("Date"))
        self.artwork_tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(("Notes"))
        self.artwork_tableWidget.setHorizontalHeaderItem(2, item)
        self.artwork_tableWidget.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout_3.addWidget(self.artwork_tableWidget)
        self.addArtwork_pushButton = QtWidgets.QPushButton(self.artwork_tab)
        self.addArtwork_pushButton.setMinimumSize(QtCore.QSize(0, 40))
        self.addArtwork_pushButton.setToolTip((""))
        self.addArtwork_pushButton.setStatusTip((""))
        self.addArtwork_pushButton.setWhatsThis((""))
        self.addArtwork_pushButton.setAccessibleName((""))
        self.addArtwork_pushButton.setAccessibleDescription((""))
        self.addArtwork_pushButton.setText(("Add New Artwork (Folder)"))
        self.addArtwork_pushButton.setShortcut((""))
        self.addArtwork_pushButton.setObjectName(("addArtwork_pushButton"))
        self.verticalLayout_3.addWidget(self.addArtwork_pushButton)
        self.tabWidget.addTab(self.artwork_tab, ("Artwork"))
        self.footage_tab = QtWidgets.QWidget()
        self.footage_tab.setToolTip((""))
        self.footage_tab.setStatusTip((""))
        self.footage_tab.setWhatsThis((""))
        self.footage_tab.setAccessibleName((""))
        self.footage_tab.setAccessibleDescription((""))
        self.footage_tab.setObjectName(("footage_tab"))
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.footage_tab)
        self.verticalLayout_2.setObjectName(("verticalLayout_2"))
        self.footage_tableWidget = QtWidgets.QTableWidget(self.footage_tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.footage_tableWidget.sizePolicy().hasHeightForWidth())
        self.footage_tableWidget.setSizePolicy(sizePolicy)
        self.footage_tableWidget.setToolTip((""))
        self.footage_tableWidget.setStatusTip((""))
        self.footage_tableWidget.setWhatsThis((""))
        self.footage_tableWidget.setAccessibleName((""))
        self.footage_tableWidget.setAccessibleDescription((""))
        self.footage_tableWidget.setObjectName(("footage_tableWidget"))
        self.footage_tableWidget.setColumnCount(3)
        self.footage_tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        item.setText(("Name"))
        self.footage_tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(("Date"))
        self.footage_tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(("Notes"))
        self.footage_tableWidget.setHorizontalHeaderItem(2, item)
        self.footage_tableWidget.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout_2.addWidget(self.footage_tableWidget)
        self.addFootage_pushButton = QtWidgets.QPushButton(self.footage_tab)
        self.addFootage_pushButton.setMinimumSize(QtCore.QSize(0, 40))
        self.addFootage_pushButton.setToolTip((""))
        self.addFootage_pushButton.setStatusTip((""))
        self.addFootage_pushButton.setWhatsThis((""))
        self.addFootage_pushButton.setAccessibleName((""))
        self.addFootage_pushButton.setAccessibleDescription((""))
        self.addFootage_pushButton.setText(("Add New Footage"))
        self.addFootage_pushButton.setObjectName(("addFootage_pushButton"))
        self.verticalLayout_2.addWidget(self.addFootage_pushButton)
        self.tabWidget.addTab(self.footage_tab, ("Footage"))
        self.other_tab = QtWidgets.QWidget()
        self.other_tab.setToolTip((""))
        self.other_tab.setStatusTip((""))
        self.other_tab.setWhatsThis((""))
        self.other_tab.setAccessibleName((""))
        self.other_tab.setAccessibleDescription((""))
        self.other_tab.setObjectName(("other_tab"))
        self.verticalLayout = QtWidgets.QVBoxLayout(self.other_tab)
        self.verticalLayout.setObjectName(("verticalLayout"))
        self.other_tableWidget = QtWidgets.QTableWidget(self.other_tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.other_tableWidget.sizePolicy().hasHeightForWidth())
        self.other_tableWidget.setSizePolicy(sizePolicy)
        self.other_tableWidget.setToolTip((""))
        self.other_tableWidget.setStatusTip((""))
        self.other_tableWidget.setWhatsThis((""))
        self.other_tableWidget.setAccessibleName((""))
        self.other_tableWidget.setAccessibleDescription((""))
        self.other_tableWidget.setColumnCount(3)
        self.other_tableWidget.setObjectName(("other_tableWidget"))
        self.other_tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        item.setText(("Name"))
        self.other_tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(("Date"))
        self.other_tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(("Notes"))
        self.other_tableWidget.setHorizontalHeaderItem(2, item)
        self.other_tableWidget.horizontalHeader().setCascadingSectionResizes(False)
        self.other_tableWidget.horizontalHeader().setDefaultSectionSize(100)
        self.other_tableWidget.horizontalHeader().setMinimumSectionSize(35)
        self.other_tableWidget.horizontalHeader().setSortIndicatorShown(False)
        self.other_tableWidget.horizontalHeader().setStretchLastSection(True)
        self.other_tableWidget.verticalHeader().setVisible(False)
        self.other_tableWidget.verticalHeader().setMinimumSectionSize(19)
        self.other_tableWidget.verticalHeader().setStretchLastSection(False)
        self.verticalLayout.addWidget(self.other_tableWidget)
        self.addOther_pushButton = QtWidgets.QPushButton(self.other_tab)
        self.addOther_pushButton.setMinimumSize(QtCore.QSize(0, 40))
        self.addOther_pushButton.setToolTip((""))
        self.addOther_pushButton.setStatusTip((""))
        self.addOther_pushButton.setWhatsThis((""))
        self.addOther_pushButton.setAccessibleName((""))
        self.addOther_pushButton.setAccessibleDescription((""))
        self.addOther_pushButton.setText(("Add New Footage"))
        self.addOther_pushButton.setShortcut((""))
        self.addOther_pushButton.setObjectName(("addOther_pushButton"))
        self.verticalLayout.addWidget(self.addOther_pushButton)
        self.tabWidget.addTab(self.other_tab, ("Other"))
        self.verticalLayout_6.addWidget(self.tabWidget)
        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 715, 21))
        self.menubar.setToolTip((""))
        self.menubar.setStatusTip((""))
        self.menubar.setWhatsThis((""))
        self.menubar.setAccessibleName((""))
        self.menubar.setAccessibleDescription((""))
        self.menubar.setObjectName(("menubar"))
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setToolTip((""))
        self.statusbar.setStatusTip((""))
        self.statusbar.setWhatsThis((""))
        self.statusbar.setAccessibleName((""))
        self.statusbar.setAccessibleDescription((""))
        self.statusbar.setObjectName(("statusbar"))
        self.setStatusBar(self.statusbar)

        self.tabWidget.setCurrentIndex(1)

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    selfLoc = os.path.dirname(os.path.abspath(__file__))
    stylesheetFile = os.path.join(selfLoc, "CSS", "darkorange.stylesheet")


    with open(stylesheetFile, "r") as fh:
        app.setStyleSheet(fh.read())
    window = MainUI()
    window.show()
    sys.exit(app.exec_())