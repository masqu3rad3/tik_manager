"""Creates a tree structure for image sequences

Image sequences can be listed recursively if the checkbox is checked.
Meaning all the sequence under the selected folder will be listed
recursively.
Double clicking on the seguence will execute the file on the defined application
"""
import _version
# reload(_version)
import pyseq as seq
# reload(seq)
import os
import pymel.core as pm

import Qt
from Qt import QtWidgets, QtCore, QtGui
from maya import OpenMayaUI as omui
import json
import datetime

import seqCopyProgress as sCopy
# reload(sCopy)

import logging


__author__ = "Arda Kutlu"
__copyright__ = "Copyright 2018, Scene Manager for Maya Project"
__credits__ = []
__license__ = "GPL"
# __version__ = "0.1"
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

windowName = "Image Viewer v%s" %_version.__version__

# def getTheImages():
#     imagesFolder = os.path.join(os.path.normpath(pm.workspace(q=1, rd=1)), "images")
#
#     treeDataList = [a for a in seq.walk(imagesFolder, topdown=True)]
#
#
#     return treeDataList

def setupLogger(handlerPath):
    logger = logging.getLogger('imageViewer')
    file_logger = logging.FileHandler(handlerPath)
    logger.addHandler(file_logger)
    logger.setLevel(logging.DEBUG)
    return logger

def deleteLogger(logger):
    for i in logger.handlers:
        logger.removeHandler(i)
        i.flush()
        i.close()

# def getTheImages(path, level=1):
#     treeDataList = [a for a in seq.walk(path, level=level)]
#     return treeDataList

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
    """
    Initializes json Database for remote server transfer location
    Returns: (List) if successfull [0, transferLocation] if failed [-1, "N/A"]

    """
    projectPath = os.path.normpath(pm.workspace(q=1, rd=1))
    jsonPath = os.path.normpath(os.path.join(projectPath, "smDatabase"))
    tLocationFile = os.path.normpath(os.path.join(jsonPath, "tLocation.json"))
    if os.path.isfile(tLocationFile):
        tLocation = loadJson(tLocationFile)
        return 0, tLocation
    else:
        return -1, "N/A"

def setTlocation(path):
    """
    Sets the Remote Server transfer location and saves it into the json database
    Args:
        path: (String) Path of the remote directory

    Returns: None

    """
    projectPath = os.path.normpath(pm.workspace(q=1, rd=1))
    jsonPath = os.path.normpath(os.path.join(projectPath, "smDatabase"))
    folderCheck(jsonPath)
    tLocationFile = os.path.normpath(os.path.join(jsonPath, "tLocation.json"))
    dumpJson(path, tLocationFile)

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
        self._generator = None
        self._timerId = None

        self.projectPath = os.path.join(os.path.normpath(pm.workspace(q=1, rd=1)), "images")
        # self.projectPath = os.path.join(os.path.normpath(pm.workspace(q=1, rd=1)), "") # temporary
        self.sequenceData = []

        self.extensionDictionary = {"jpg": ["*.jpg", "*.jpeg"],
                                   "png": ["*.png"],
                                   "exr": ["*.exr"],
                                   "tif": ["*.tif", "*.tiff"],
                                   "tga": ["*.tga"]
                                   }

        self.filterList = sum(self.extensionDictionary.values(), [])

        self.setObjectName(windowName)
        self.resize(670, 624)
        self.setWindowTitle(windowName)
        self.centralwidget = QtWidgets.QWidget(self)
        # self.centralwidget.setObjectName(("centralwidget"))
        self.model = QtWidgets.QFileSystemModel()
        self.model.setRootPath(self.projectPath)
        # filter = Qt.QStringList("")
        # self.model.setFilter(QtCore.QDir.AllDirs|QtCore.QDir.NoDotAndDotDot)
        self.model.setFilter(QtCore.QDir.AllDirs|QtCore.QDir.NoDotAndDotDot)
        self.tLocation = initDB()[1]
        self.buildUI()
        # self.filterList=[]
        # self.onCheckbox()

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
        # self.recursive_checkBox.setObjectName(("recursive_checkBox"))
        self.gridLayout.addWidget(self.recursive_checkBox, 0, 3, 1, 1)

        self.rootFolder_label = QtWidgets.QLabel(self.centralwidget)
        self.rootFolder_label.setFrameShape(QtWidgets.QFrame.Box)
        self.rootFolder_label.setLineWidth(1)
        self.rootFolder_label.setText(("Root Folder:"))
        self.rootFolder_label.setTextFormat(QtCore.Qt.AutoText)
        self.rootFolder_label.setScaledContents(False)
        # self.rootFolder_label.setObjectName(("rootFolder_label"))
        self.gridLayout.addWidget(self.rootFolder_label, 0, 0, 1, 1)

        self.rootFolder_lineEdit = DropLineEdit(self.centralwidget)
        self.rootFolder_lineEdit.setText((self.projectPath))
        self.rootFolder_lineEdit.setReadOnly(True)
        self.rootFolder_lineEdit.setPlaceholderText((""))
        # self.rootFolder_lineEdit.setObjectName(("rootFolder_lineEdit"))
        self.gridLayout.addWidget(self.rootFolder_lineEdit, 0, 1, 1, 1)

        self.browse_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.browse_pushButton.setText(("Browse"))
        # self.browse_pushButton.setObjectName(("browse_pushButton"))
        self.gridLayout.addWidget(self.browse_pushButton, 0, 2, 1, 1)

        self.raidFolder_label = QtWidgets.QLabel(self.centralwidget)
        self.raidFolder_label.setFrameShape(QtWidgets.QFrame.Box)
        self.raidFolder_label.setLineWidth(1)
        self.raidFolder_label.setText(("Raid Folder:"))
        self.raidFolder_label.setTextFormat(QtCore.Qt.AutoText)
        self.raidFolder_label.setScaledContents(False)
        # self.raidFolder_label.setObjectName(("rootFolder_label"))
        self.gridLayout.addWidget(self.raidFolder_label, 1, 0, 1, 1)

        self.raidFolder_lineEdit = DropLineEdit(self.centralwidget)
        self.raidFolder_lineEdit.setText(self.tLocation)
        self.raidFolder_lineEdit.setReadOnly(True)
        self.raidFolder_lineEdit.setPlaceholderText((""))
        # self.raidFolder_lineEdit.setObjectName(("raidFolder_lineEdit"))
        self.gridLayout.addWidget(self.raidFolder_lineEdit, 1, 1, 1, 1)

        self.browseRaid_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.browseRaid_pushButton.setText(("Browse"))
        # self.browseRaid_pushButton.setObjectName(("browseRaid_pushButton"))
        self.gridLayout.addWidget(self.browseRaid_pushButton, 1, 2, 1, 1)

        self.chkboxLayout = QtWidgets.QHBoxLayout()
        self.chkboxLayout.setAlignment(QtCore.Qt.AlignRight)

        self.checkboxes=[]
        for key in (self.extensionDictionary.keys()):
            tCheck = QtWidgets.QCheckBox()
            tCheck.setText(key)
            tCheck.setChecked(True)
            # name = lambda x=key: key
            # tCheck.setObjectName(str(name))
            self.chkboxLayout.addWidget(tCheck)
            tCheck.toggled.connect(lambda state, item=self.extensionDictionary[key]: self.onCheckbox(item, state))
            self.checkboxes.append(tCheck)



        self.selectAll_pushbutton = QtWidgets.QPushButton()
        self.selectAll_pushbutton.setText("Select All")

        self.selectNone_pushbutton = QtWidgets.QPushButton()
        self.selectNone_pushbutton.setText("Select None")

        spacerItem = QtWidgets.QSpacerItem(400, 25, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)

        self.chkboxLayout.addWidget(self.selectAll_pushbutton)
        self.chkboxLayout.addWidget(self.selectNone_pushbutton)
        self.chkboxLayout.addItem(spacerItem)

        self.gridLayout.addLayout(self.chkboxLayout, 2, 0, 1, 4)


        # Splitter LEFT side:

        self.directories_treeView = DeselectableTreeView(self.centralwidget)
        self.directories_treeView.setModel(self.model)
        self.directories_treeView.setRootIndex(self.model.index(self.projectPath))
        self.directories_treeView.setSortingEnabled(True)
        self.directories_treeView.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.directories_treeView.setColumnWidth(0, 250)
        self.directories_treeView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.directories_treeView.hideColumn(1)
        self.directories_treeView.hideColumn(2)
        # self.directories_treeView.setCurrentIndex(self.model.index(self.locationsDic["rootLocation"]))
        self.directories_treeView.setContentsMargins(0, 0, 0, 0)

        self.left_layout = QtWidgets.QVBoxLayout()
        self.left_layout.setSpacing(0)
        self.left_layout.addWidget(self.directories_treeView)
        self.left_layout.setContentsMargins(0, 0, 0, 0)

        self.left_widget = QtWidgets.QFrame()
        self.left_widget.setContentsMargins(0, 0, 0, 0)
        self.left_widget.setLayout(self.left_layout)

        # Splitter Right Side:

        self.sequences_listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.sequences_listWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.nameFilter_label = QtWidgets.QLabel(self.centralwidget)
        self.nameFilter_label.setText("Filter:")
        self.nameFilter_lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.nameFilterApply_pushButton = QtWidgets.QPushButton(self.centralwidget, text="Apply")



        self.right_layout = QtWidgets.QVBoxLayout()
        self.right_layout.addWidget(self.sequences_listWidget)

        nameFilter_layout = QtWidgets.QHBoxLayout()
        nameFilter_layout.addWidget(self.nameFilter_label)
        nameFilter_layout.addWidget(self.nameFilter_lineEdit)
        nameFilter_layout.addWidget(self.nameFilterApply_pushButton)

        self.right_layout.addLayout(nameFilter_layout)
        self.right_layout.setContentsMargins(0, 0, 0, 0)



        self.right_widget = QtWidgets.QFrame()
        self.right_widget.setLayout(self.right_layout)
        self.right_widget.setContentsMargins(0, 0, 0, 0)

        ######


        self.splitter = QtWidgets.QSplitter(parent=self)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setHandleWidth(8)
        # self.splitter.setOpaqueResize(False)
        self.splitter.addWidget(self.left_widget)
        self.splitter.addWidget(self.right_widget)
        # self.splitter.setStretchFactor(1, 0)


        self.gridLayout.addWidget(self.splitter, 3, 0, 1, 4)
        # self.splitter.setSizes([80, 10])
        self.splitter.setStretchFactor(0, 1)

        self.browse_pushButton.clicked.connect(self.onBrowse)
        self.directories_treeView.selectionModel().selectionChanged.connect(self.populate)
        self.recursive_checkBox.toggled.connect(self.populate)
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

        self.rootFolder_lineEdit.dropped.connect(self.setRootPath)
        self.raidFolder_lineEdit.dropped.connect(self.setRaidPath)

        self.selectAll_pushbutton.clicked.connect(self.selectAll)
        self.selectNone_pushbutton.clicked.connect(self.selectNone)
        # self.popMenu.addSeparator()
        self.directories_treeView.deselected.connect(self.deselectTree)

        self.nameFilterApply_pushButton.clicked.connect(self.populate)
        self.nameFilter_lineEdit.returnPressed.connect(self.populate)

        ## check if there is a json file on the project data path for target drive

        # index = self.directories_treeView.currentIndex()
        # print index.row()
        self.populate()





        #
        # self.splitter = QtWidgets.QSplitter(self.centralwidget)
        # self.splitter.setOrientation(QtCore.Qt.Horizontal)
        # # self.splitter.setObjectName(("splitter"))
        #
        # self.directories_treeView = QtWidgets.QTreeView(self.splitter)
        # # self.directories_treeView.setObjectName(("directories_treeView"))
        # self.directories_treeView.setModel(self.model)
        # self.directories_treeView.setRootIndex(self.model.index(self.projectPath))
        # self.directories_treeView.hideColumn(1)
        # self.directories_treeView.hideColumn(2)
        # self.directories_treeView.hideColumn(3)
        #
        # self.sequences_listWidget = QtWidgets.QListWidget(self.splitter)
        # # self.sequences_listWidget.setObjectName(("sequences_listWidget"))
        # self.sequences_listWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        # self.gridLayout.addWidget(self.splitter, 3, 0, 1, 4)
        #
        # self.browse_pushButton.clicked.connect(self.onBrowse)
        # self.directories_treeView.selectionModel().selectionChanged.connect(self.populate)
        # self.recursive_checkBox.stateChanged.connect(self.populate)
        # self.sequences_listWidget.doubleClicked.connect(self.onRunItem)
        # self.browseRaid_pushButton.clicked.connect(self.onBrowseRaid)
        #
        # self.chkbox1_checkbox.toggled.connect(self.onCheckbox)
        # self.chkbox2_checkbox.toggled.connect(self.onCheckbox)
        # self.chkbox3_checkbox.toggled.connect(self.onCheckbox)
        # self.chkbox4_checkbox.toggled.connect(self.onCheckbox)
        # self.chkbox5_checkbox.toggled.connect(self.onCheckbox)
        #
        # ## RIGHT CLICK MENUS
        # self.sequences_listWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # self.sequences_listWidget.customContextMenuRequested.connect(self.onContextMenu_images)
        # self.popMenu = QtWidgets.QMenu()
        #
        # rcAction_0 = QtWidgets.QAction('Show in Explorer', self)
        # rcAction_1 = QtWidgets.QAction('Transfer Files to Raid', self)
        # self.popMenu.addAction(rcAction_0)
        # self.popMenu.addAction(rcAction_1)
        # rcAction_0.triggered.connect(lambda: self.onShowInExplorer())
        # rcAction_1.triggered.connect(lambda: self.onTransferFiles())
        #
        # ## check if there is a json file on the project data path for target drive

    def deselectTree(self):
        self.directories_treeView.setCurrentIndex(self.model.index(self.projectPath))
        self.populate()

    def selectAll(self):
        for c in self.checkboxes:
            c.setChecked(True)

    def selectNone(self):
        for c in self.checkboxes:
            c.setChecked(False)

    def setRootPath(self, dir):
        dir = str(dir)
        self.directories_treeView.reset()
        # self.locationsDic["rootLocation"] = os.path.normpath(dir)
        self.model.setRootPath(dir)
        self.directories_treeView.setRootIndex(self.model.index(dir))
        self.rootFolder_lineEdit.setText(os.path.normpath(dir))
        self.sequences_listWidget.clear()

    def setRaidPath(self, dir):
        dir = str(dir)
        setTlocation(os.path.normpath(dir))
        self.raidFolder_lineEdit.setText(dir)

    def onCheckbox(self, extensions, state):
        if state:
            self.filterList += extensions
        else:
            self.filterList = list(set(self.filterList)-set(extensions))
        self.populate()
        # self.filterList = []
        # if self.chkbox1_checkbox.isChecked():
        #     self.filterList.append("*.jpg")
        # if self.chkbox2_checkbox.isChecked():
        #     self.filterList.append("*.png")
        # if self.chkbox3_checkbox.isChecked():
        #     self.filterList.append("*.exr")
        # if self.chkbox4_checkbox.isChecked():
        #     self.filterList.append("*.tif")
        # if self.chkbox5_checkbox.isChecked():
        #     self.filterList.append("*.tga")
        # self.populate()

    # @Qt.QtCore.pyqtSlot("QItemSelection, QItemSelection")
    def onContextMenu_images(self, point):
        self.popMenu.exec_(self.sequences_listWidget.mapToGlobal(point))

    def onBrowse(self):
        dir = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
        if dir:
            self.setRootPath(dir)
        else:
            return

    def onBrowseRaid(self):
        path = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory", self.tLocation))
        if path:
            self.setRaidPath(path)
            return



    def onTransferFiles(self):
        if self.tLocation == "N/A":
            return
        row = self.sequences_listWidget.currentRow()
        selList = [x.row() for x in self.sequences_listWidget.selectedIndexes()]
        # return
        if row == -1:
            return

        projectPath = os.path.normpath(pm.workspace(q=1, rd=1))
        logPath = os.path.join(projectPath,"data","transferLogs")
        folderCheck(logPath)

        seqCopy = sCopy.SeqCopyProgress()
        seqCopy.copysequence(self.sequenceData, selList, self.tLocation, logPath, projectPath)


    def onShowInExplorer(self):
        row = self.sequences_listWidget.currentRow()
        if row == -1:
            return
        os.startfile(self.sequenceData[row].dirname)


    def populate(self):
        self.sequences_listWidget.clear()
        self.sequenceData=[] # clear the custom list
        index = self.directories_treeView.currentIndex()
        if not self.filterList:
            self.stop()
            return

        index = self.directories_treeView.currentIndex()

        if index.row() == -1: # no row selected
            fullPath = self.projectPath
        else:
            fullPath = str(self.model.filePath(index))

        if self.recursive_checkBox.isChecked():
            rec=-1
        else:
            rec=1

        # gen = seq.walk(fullPath, level=rec, includes=self.filterList)
        filter = (f for f in self.filterList)
        gen = seq.walk(fullPath, level=rec, includes=filter)
        self.stop() # Stop any existing Timer
        self._generator = self.listingLoop(gen) # start the loop
        self._timerId = self.startTimer(0) # idle timer


    def listingLoop(self, gen):
        for x in gen:
            for i in x[2]:
                QtWidgets.QApplication.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
                # filtertest
                filterWord = str(self.nameFilter_lineEdit.text())
                # print filterWord
                if filterWord != "" and filterWord.lower() not in i.lower():
                    continue
                self.sequenceData.append(i)
                self.sequences_listWidget.addItem(i.format('%h%t %R'))
                yield

    def onRunItem(self):
        row = self.sequences_listWidget.currentRow()
        item = self.sequenceData[row]
        firstImagePath = os.path.join(os.path.normpath(item.dirname), item.name)
        os.startfile(firstImagePath)

    def stop(self):  # Connect to Stop-button clicked()
        if self._timerId is not None:
            self.killTimer(self._timerId)
        self._generator = None
        self._timerId = None

    def timerEvent(self, event):
        # This is called every time the GUI is idle.
        if self._generator is None:
            return
        try:
            next(self._generator)  # Run the next iteration
        except StopIteration:
            self.stop()  # Iteration has finshed, kill the timer

class DropLineEdit(QtWidgets.QLineEdit):
    dropped = Qt.QtCore.Signal(str)
    def __init__(self, type, parent=None):
        super(DropLineEdit, self).__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('text/uri-list'):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('text/uri-list'):
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        rawPath = event.mimeData().data('text/uri-list').__str__()
        path = rawPath.replace("file:///", "").splitlines()[0]
        self.dropped.emit(path)
        # self.addItem(path)


class DeselectableTreeView(QtWidgets.QTreeView):
    # deselected = QtCore.pyqtSignal(bool)
    deselected = Qt.QtCore.Signal(bool)
    def mousePressEvent(self, event):
        index = self.indexAt(event.pos()) # returns  -1 if click is outside
        if index.row() == -1:
            self.clearSelection()
            self.deselected.emit(True)
        QtWidgets.QTreeView.mousePressEvent(self, event)




