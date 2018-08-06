"""Creates a tree structure for image sequences

Image sequences can be listed recursively if the checkbox is checked.
Meaning all the sequence under the selected folder will be listed
recursively.
Double clicking on the seguence will execute the file on the defined application
"""

import pyseq as seq
import os
import pymel.core as pm

import Qt
from Qt import QtWidgets, QtCore, QtGui
from maya import OpenMayaUI as omui
import json
import datetime
import fileCopyProgress as fCopy
# reload(fCopy)

__author__ = "Arda Kutlu"
__copyright__ = "Copyright 2018, Scene Manager for Maya Project"
__credits__ = []
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Arda Kutlu"
__email__ = "ardakutlu@gmail.com"
__status__ = "Development"

if Qt.__binding__ == "PySide":
    from shiboken import wrapInstance
    from Qt.QtCore import Signal
elif Qt.__binding__.startswith('PyQt'):
    from sip import wrapinstance as wrapInstance
    from Qt.Core import pyqtSignal as Signal
else:
    from shiboken2 import wrapInstance
    from Qt.QtCore import Signal

windowName = "Image Viewer v0.1"

# def getTheImages():
#     imagesFolder = os.path.join(os.path.normpath(pm.workspace(q=1, rd=1)), "images")
#
#     treeDataList = [a for a in seq.walk(imagesFolder, topdown=True)]
#
#
#     return treeDataList
def getTheImages(path, level=1):
    treeDataList = [a for a in seq.walk(path, level=level)]
    return treeDataList

def getMayaMainWindow():
    """
    Gets the memory adress of the main window to connect Qt dialog to it.
    Returns:
        (long) Memory Adress
    """
    win = omui.MQtUtil_mainWindow()
    ptr = wrapInstance(long(win), QtWidgets.QMainWindow)
    return ptr

def folderCheck(folder):
    if not os.path.isdir(os.path.normpath(folder)):
        os.makedirs(os.path.normpath(folder))

def loadJson(file):
    if os.path.isfile(file):
        with open(file, 'r') as f:
            # The JSON module will read our file, and convert it to a python dictionary
            data = json.load(f)
            return data
    else:
        return None

def dumpJson(data, file):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

def initDB():
    projectPath = os.path.normpath(pm.workspace(q=1, rd=1))
    jsonPath = os.path.normpath(os.path.join(projectPath, "data", "SMdata"))
    tLocationFile = os.path.normpath(os.path.join(jsonPath, "tLocation.json"))
    if os.path.isfile(tLocationFile):
        tLocation = loadJson(tLocationFile)
        return 0, tLocation
    else:
        return -1, "N/A"

def setTlocation(path):
    projectPath = os.path.normpath(pm.workspace(q=1, rd=1))
    jsonPath = os.path.normpath(os.path.join(projectPath, "data", "SMdata"))
    folderCheck(jsonPath)
    tLocationFile = os.path.normpath(os.path.join(jsonPath, "tLocation.json"))
    dumpJson(path, tLocationFile)

def transferFiles(files, tLocation, projectPath):
    if not os.path.isdir(tLocation):
        # transfer location is not exist
        return -1, "Transfer Location not exists"

    subPath = os.path.split(os.path.relpath(files[0], projectPath))[0] ## get the relative path


    now = datetime.datetime.now()
    currentDate = now.strftime("%y%m%d")

    targetPath = os.path.join(tLocation, currentDate, subPath)
    folderCheck(targetPath)

    ret = fCopy.FileCopyProgress(src=files, dest=targetPath)
    ret.close()
    return ret.cancelAll
    # try:
    #     copyfile(files, targetPath)
    # except:
    #     pass





class MainUI(QtWidgets.QMainWindow):
    def __init__(self):
        for entry in QtWidgets.QApplication.allWidgets():
            try:
                if entry.objectName() == windowName:
                    entry.close()
            except AttributeError:
                pass
        parent = getMayaMainWindow()
        super(MainUI, self).__init__(parent=parent)
        self.projectPath = os.path.join(os.path.normpath(pm.workspace(q=1, rd=1)), "images")
        # self.projectPath = os.path.join(os.path.normpath(pm.workspace(q=1, rd=1)), "") # temporary
        self.sequenceData = []
        self.setObjectName(windowName)
        self.resize(670, 624)
        self.setWindowTitle(windowName)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName(("centralwidget"))
        self.model = QtWidgets.QFileSystemModel()

        self.model.setRootPath(self.projectPath)
        # filter = Qt.QStringList("")
        self.model.setFilter(QtCore.QDir.AllDirs|QtCore.QDir.NoDotAndDotDot)
        self.tLocation = initDB()[1]
        self.buildUI()

        self.setCentralWidget(self.centralwidget)
        # self.menubar = QtGui.QMenuBar(self)
        # self.menubar.setGeometry(QtCore.QRect(0, 0, 670, 21))
        # self.menubar.setObjectName(("menubar"))
        # self.setMenuBar(self.menubar)
        # self.statusbar = QtGui.QStatusBar(self)
        # self.statusbar.setObjectName(("statusbar"))
        # self.setStatusBar(self.statusbar)

    def buildUI(self):
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(("gridLayout"))

        self.recursive_checkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.recursive_checkBox.setText(("Recursive"))
        self.recursive_checkBox.setChecked(False)
        self.recursive_checkBox.setObjectName(("recursive_checkBox"))
        self.gridLayout.addWidget(self.recursive_checkBox, 0, 3, 1, 1)

        self.rootFolder_label = QtWidgets.QLabel(self.centralwidget)
        self.rootFolder_label.setFrameShape(QtWidgets.QFrame.Box)
        self.rootFolder_label.setLineWidth(1)
        self.rootFolder_label.setText(("Root Folder:"))
        self.rootFolder_label.setTextFormat(QtCore.Qt.AutoText)
        self.rootFolder_label.setScaledContents(False)
        self.rootFolder_label.setObjectName(("rootFolder_label"))
        self.gridLayout.addWidget(self.rootFolder_label, 0, 0, 1, 1)

        self.rootFolder_lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.rootFolder_lineEdit.setText((self.projectPath))
        self.rootFolder_lineEdit.setReadOnly(True)
        self.rootFolder_lineEdit.setPlaceholderText((""))
        self.rootFolder_lineEdit.setObjectName(("rootFolder_lineEdit"))
        self.gridLayout.addWidget(self.rootFolder_lineEdit, 0, 1, 1, 1)

        self.browse_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.browse_pushButton.setText(("Browse"))
        self.browse_pushButton.setObjectName(("browse_pushButton"))
        self.gridLayout.addWidget(self.browse_pushButton, 0, 2, 1, 1)

        self.raidFolder_label = QtWidgets.QLabel(self.centralwidget)
        self.raidFolder_label.setFrameShape(QtWidgets.QFrame.Box)
        self.raidFolder_label.setLineWidth(1)
        self.raidFolder_label.setText(("Raid Folder:"))
        self.raidFolder_label.setTextFormat(QtCore.Qt.AutoText)
        self.raidFolder_label.setScaledContents(False)
        self.raidFolder_label.setObjectName(("rootFolder_label"))
        self.gridLayout.addWidget(self.raidFolder_label, 1, 0, 1, 1)

        self.raidFolder_lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.raidFolder_lineEdit.setText(self.tLocation)
        self.raidFolder_lineEdit.setReadOnly(True)
        self.raidFolder_lineEdit.setPlaceholderText((""))
        self.raidFolder_lineEdit.setObjectName(("raidFolder_lineEdit"))
        self.gridLayout.addWidget(self.raidFolder_lineEdit, 1, 1, 1, 1)

        self.browseRaid_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.browseRaid_pushButton.setText(("Browse"))
        self.browseRaid_pushButton.setObjectName(("browseRaid_pushButton"))
        self.gridLayout.addWidget(self.browseRaid_pushButton, 1, 2, 1, 1)


        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(("splitter"))

        self.directories_treeView = QtWidgets.QTreeView(self.splitter)
        self.directories_treeView.setObjectName(("directories_treeView"))
        # self.directories_treeView.headerItem().setText(0, "Directories")
        # self.directories_treeView.setSortingEnabled(False)
        self.directories_treeView.setModel(self.model)
        self.directories_treeView.setRootIndex(self.model.index(self.projectPath))
        self.directories_treeView.hideColumn(1)
        self.directories_treeView.hideColumn(2)
        self.directories_treeView.hideColumn(3)

        self.sequences_listWidget = QtWidgets.QListWidget(self.splitter)
        self.sequences_listWidget.setObjectName(("sequences_listWidget"))
        self.sequences_listWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.gridLayout.addWidget(self.splitter, 2, 0, 1, 4)

        self.browse_pushButton.clicked.connect(self.onBrowse)
        self.directories_treeView.selectionModel().selectionChanged.connect(self.populate)
        self.recursive_checkBox.stateChanged.connect(self.populate)
        self.sequences_listWidget.doubleClicked.connect(self.onRunItem)
        self.browseRaid_pushButton.clicked.connect(self.onBrowseRaid)

        ## RIGHT CLICK MENUS
        self.sequences_listWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.sequences_listWidget.customContextMenuRequested.connect(self.onContextMenu_images)
        self.popMenu = QtWidgets.QMenu()

        rcAction_0 = QtWidgets.QAction('Show in Explorer', self)
        rcAction_1 = QtWidgets.QAction('Transfer Files to Raid', self)
        self.popMenu.addAction(rcAction_0)
        self.popMenu.addAction(rcAction_1)
        rcAction_0.triggered.connect(lambda: self.onShowInExplorer())
        rcAction_1.triggered.connect(lambda: self.onTransferFiles())

        # self.popMenu.addSeparator()


        ## check if there is a json file on the project data path for target drive

    # @Qt.QtCore.pyqtSlot("QItemSelection, QItemSelection")
    def onContextMenu_images(self, point):
        self.popMenu.exec_(self.sequences_listWidget.mapToGlobal(point))

    def onBrowse(self):
        dir = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
        if dir:
            self.projectPath=os.path.normpath(dir)
            self.model.setRootPath(dir)
            self.directories_treeView.setRootIndex(self.model.index(dir))
            self.rootFolder_lineEdit.setText(self.projectPath)
            self.sequences_listWidget.clear()
            # self.populate()
        else:
            return

    def onBrowseRaid(self):
        path = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory", self.tLocation))
        if path:
            setTlocation(path)
            self.raidFolder_lineEdit.setText(path)
            return path

    def onTransferFiles(self):
        row = self.sequences_listWidget.currentRow()
        selList = [x.row() for x in self.sequences_listWidget.selectedIndexes()]
        # return
        if row == -1:
            return

        for sel in selList:
            tFilesList = [i.path for i in self.sequenceData[sel]]
            # print tFilesList

            ret = transferFiles(tFilesList, tLocation=self.tLocation, projectPath=self.projectPath)
            if ret == True: ## cancel all?
                return

    def onShowInExplorer(self):
        row = self.sequences_listWidget.currentRow()
        if row == -1:
            return
        os.startfile(self.sequenceData[row].dirname)


    def populate(self):
        self.sequences_listWidget.clear()
        self.sequenceData=[] # clear the custom list
        index = self.directories_treeView.currentIndex()
        if index.row() == -1: # no row selected, abort
            return

        fullPath = self.model.filePath(index)

        if self.recursive_checkBox.isChecked():
            rec=-1
        else:
            rec=1

        gen = seq.walk(fullPath, level=rec, includes=['*.jpg', '*.exr', '*.tga', '*.png'])

        id = 0
        for x in gen:
            for i in x[2]:
                QtWidgets.QApplication.processEvents()
                # execPath = os.path.join(x[0],i[0])
                # execPath = i[0].path
                self.sequenceData.append(i)
                # name = i.format('%h%t %R')
                self.sequences_listWidget.addItem(i.format('%h%t %R'))
                # self.sequenceData.append()
                id += 1
    def onRunItem(self):
        row = self.sequences_listWidget.currentRow()
        item = self.sequenceData[row]
        firstImagePath = os.path.join(os.path.normpath(item.dirname), item.name)
        # firstImagePath = os.path.join(os.path.normpath(item.dirname), str(item[0]))
        os.startfile(firstImagePath)



