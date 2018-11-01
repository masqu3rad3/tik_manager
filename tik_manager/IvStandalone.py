"""Creates a tree structure for image sequences

Image sequences can be listed recursively if the checkbox is checked.
Meaning all the sequence under the selected folder will be listed
recursively.
Double clicking on the seguence will execute the file on the defined application
"""
import _version
import pyseq as seq
import sys, os
from PyQt4 import QtCore, QtGui, Qt

# import SmRoot
# reload(SmRoot)
# from SmRoot import RootManager

import json
import datetime
from shutil import copyfile



import logging


__author__ = "Arda Kutlu"
__copyright__ = "Copyright 2018, Scene Manager for Maya Project"
__credits__ = []
__license__ = "GPL"
# __version__ = "0.1"
__maintainer__ = "Arda Kutlu"
__email__ = "ardakutlu@gmail.com"
__status__ = "Development"


windowName = "Image Viewer Standalone v%s" %_version.__version__

def folderCheck(folder):
    if not os.path.isdir(os.path.normpath(folder)):
        os.makedirs(os.path.normpath(folder))

class MainUI(QtGui.QMainWindow):
    def __init__(self, projectPath, relativePath=None, recursive=False):
        super(MainUI, self).__init__()

        self.projectPath = projectPath
        self.databaseDir = os.path.normpath(os.path.join(self.projectPath, "smDatabase"))

        if relativePath:
            self.rootPath = os.path.join(self.projectPath, relativePath)
        else:
            self.rootPath = os.path.join(self.projectPath, "images")

        if not os.path.isdir(self.databaseDir):
            msg=["Nothing to view", "No Scene Manager Database",
             "There is no Scene Manager Database Folder in this project path"]
            q = QtGui.QMessageBox()
            q.setIcon(QtGui.QMessageBox.Information)
            q.setText(msg[0])
            q.setInformativeText(msg[1])
            q.setWindowTitle(msg[2])
            q.setStandardButtons(QtGui.QMessageBox.Ok)
            ret = q.exec_()
            if ret == QtGui.QMessageBox.Ok:
                self.close()
                self.deleteLater()

        self.recursiveInitial = recursive

        self._generator = None
        self._timerId = None


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
        self.centralwidget = QtGui.QWidget(self)
        self.model = QtGui.QFileSystemModel()
        self.model.setRootPath(self.rootPath)
        self.model.setFilter(QtCore.QDir.AllDirs|QtCore.QDir.NoDotAndDotDot)
        self.tLocation = self.getRaidPath()

        self.buildUI()

        self.setCentralWidget(self.centralwidget)

    # def getTlocation(self):
    #     tLocationFile = os.path.normpath(os.path.join(self.databaseDir, "tLocation.json"))
    #     if os.path.isfile(tLocationFile):
    #         tLocation = self._loadJson(tLocationFile)
    #     else:
    #         tLocation = "N/A"
    #         self._dumpJson(tLocation, tLocationFile)
    #     return tLocation

    def buildUI(self):
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(("gridLayout"))

        self.recursive_checkBox = QtGui.QCheckBox(self.centralwidget)
        self.recursive_checkBox.setText(("Recursive"))
        self.recursive_checkBox.setChecked(self.recursiveInitial)
        # self.recursive_checkBox.setObjectName(("recursive_checkBox"))
        self.gridLayout.addWidget(self.recursive_checkBox, 0, 3, 1, 1)

        self.rootFolder_label = QtGui.QLabel(self.centralwidget)
        self.rootFolder_label.setFrameShape(QtGui.QFrame.Box)
        self.rootFolder_label.setLineWidth(1)
        self.rootFolder_label.setText(("Root Folder:"))
        self.rootFolder_label.setTextFormat(QtCore.Qt.AutoText)
        self.rootFolder_label.setScaledContents(False)
        # self.rootFolder_label.setObjectName(("rootFolder_label"))
        self.gridLayout.addWidget(self.rootFolder_label, 0, 0, 1, 1)

        self.rootFolder_lineEdit = DropLineEdit(self.centralwidget)
        self.rootFolder_lineEdit.setText((self.rootPath))
        self.rootFolder_lineEdit.setReadOnly(True)
        self.rootFolder_lineEdit.setPlaceholderText((""))
        # self.rootFolder_lineEdit.setObjectName(("rootFolder_lineEdit"))
        self.gridLayout.addWidget(self.rootFolder_lineEdit, 0, 1, 1, 1)

        self.browse_pushButton = QtGui.QPushButton(self.centralwidget)
        self.browse_pushButton.setText(("Browse"))
        # self.browse_pushButton.setObjectName(("browse_pushButton"))
        self.gridLayout.addWidget(self.browse_pushButton, 0, 2, 1, 1)

        self.raidFolder_label = QtGui.QLabel(self.centralwidget)
        self.raidFolder_label.setFrameShape(QtGui.QFrame.Box)
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

        self.browseRaid_pushButton = QtGui.QPushButton(self.centralwidget)
        self.browseRaid_pushButton.setText(("Browse"))
        # self.browseRaid_pushButton.setObjectName(("browseRaid_pushButton"))
        self.gridLayout.addWidget(self.browseRaid_pushButton, 1, 2, 1, 1)

        self.chkboxLayout = QtGui.QHBoxLayout()
        self.chkboxLayout.setAlignment(QtCore.Qt.AlignRight)

        self.checkboxes=[]
        for key in (self.extensionDictionary.keys()):
            tCheck = QtGui.QCheckBox()
            tCheck.setText(key)
            tCheck.setChecked(True)
            # name = lambda x=key: key
            # tCheck.setObjectName(str(name))
            self.chkboxLayout.addWidget(tCheck)
            tCheck.toggled.connect(lambda state, item=self.extensionDictionary[key]: self.onCheckbox(item, state))
            self.checkboxes.append(tCheck)



        self.selectAll_pushbutton = QtGui.QPushButton()
        self.selectAll_pushbutton.setText("Select All")

        self.selectNone_pushbutton = QtGui.QPushButton()
        self.selectNone_pushbutton.setText("Select None")

        spacerItem = QtGui.QSpacerItem(400, 25, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)

        self.chkboxLayout.addWidget(self.selectAll_pushbutton)
        self.chkboxLayout.addWidget(self.selectNone_pushbutton)
        self.chkboxLayout.addItem(spacerItem)

        self.gridLayout.addLayout(self.chkboxLayout, 2, 0, 1, 4)


        # Splitter LEFT side:

        self.directories_treeView = DeselectableTreeView(self.centralwidget)
        self.directories_treeView.setModel(self.model)
        self.directories_treeView.setRootIndex(self.model.index(self.rootPath))
        self.directories_treeView.setSortingEnabled(True)
        self.directories_treeView.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.directories_treeView.setColumnWidth(0, 250)
        self.directories_treeView.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.directories_treeView.hideColumn(1)
        self.directories_treeView.hideColumn(2)
        # self.directories_treeView.setCurrentIndex(self.model.index(self.locationsDic["rootLocation"]))
        self.directories_treeView.setContentsMargins(0, 0, 0, 0)

        self.left_layout = QtGui.QVBoxLayout()
        self.left_layout.setSpacing(0)
        self.left_layout.addWidget(self.directories_treeView)
        self.left_layout.setContentsMargins(0, 0, 0, 0)

        self.left_widget = QtGui.QFrame()
        self.left_widget.setContentsMargins(0, 0, 0, 0)
        self.left_widget.setLayout(self.left_layout)

        # Splitter Right Side:

        self.sequences_listWidget = QtGui.QListWidget(self.centralwidget)
        self.sequences_listWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

        self.nameFilter_label = QtGui.QLabel(self.centralwidget)
        self.nameFilter_label.setText("Filter:")
        self.nameFilter_lineEdit = QtGui.QLineEdit(self.centralwidget)
        self.nameFilterApply_pushButton = QtGui.QPushButton(self.centralwidget, text="Apply")



        self.right_layout = QtGui.QVBoxLayout()
        self.right_layout.addWidget(self.sequences_listWidget)

        nameFilter_layout = QtGui.QHBoxLayout()
        nameFilter_layout.addWidget(self.nameFilter_label)
        nameFilter_layout.addWidget(self.nameFilter_lineEdit)
        nameFilter_layout.addWidget(self.nameFilterApply_pushButton)

        self.right_layout.addLayout(nameFilter_layout)
        self.right_layout.setContentsMargins(0, 0, 0, 0)



        self.right_widget = QtGui.QFrame()
        self.right_widget.setLayout(self.right_layout)
        self.right_widget.setContentsMargins(0, 0, 0, 0)

        ######


        self.splitter = QtGui.QSplitter(parent=self)
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
        self.popMenu = QtGui.QMenu()

        rcAction_0 = QtGui.QAction('Show in Explorer', self)
        rcAction_1 = QtGui.QAction('Transfer Files to Raid', self)
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

        self.populate()

    def deselectTree(self):
        self.directories_treeView.setCurrentIndex(self.model.index(self.rootPath))
        self.populate()

    def selectAll(self):
        for c in self.checkboxes:
            c.setChecked(True)

    def selectNone(self):
        for c in self.checkboxes:
            c.setChecked(False)

    def setRootPath(self, dir):
        dir = str(dir)
        self.rootPath=dir
        self.directories_treeView.reset()
        self.model.setRootPath(dir)
        self.directories_treeView.setRootIndex(self.model.index(dir))
        self.rootFolder_lineEdit.setText(os.path.normpath(dir))
        self.sequences_listWidget.clear()

    def getRaidPath(self):
        tLocationFile = os.path.normpath(os.path.join(self.databaseDir, "tLocation.json"))
        if os.path.isfile(tLocationFile):
            tLocation = self._loadJson(tLocationFile)
        else:
            tLocation = "N/A"
            self._dumpJson(tLocation, tLocationFile)
        return tLocation

    def setRaidPath(self, dir):
        tLocationFile = os.path.normpath(os.path.join(self.databaseDir, "tLocation.json"))
        self.tLocation = str(dir)
        self._dumpJson(self.tLocation, tLocationFile)
        self.raidFolder_lineEdit.setText(self.tLocation)

    def onCheckbox(self, extensions, state):
        if state:
            self.filterList += extensions
        else:
            self.filterList = list(set(self.filterList)-set(extensions))
        self.populate()

    def onContextMenu_images(self, point):
        if not self.sequences_listWidget.currentRow() is -1:
            self.popMenu.exec_(self.sequences_listWidget.mapToGlobal(point))

    def onBrowse(self):
        dir = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory"))
        if dir:
            self.setRootPath(dir)
        else:
            return

    def onBrowseRaid(self):
        path = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory", self.tLocation))
        if path:
            self.setRaidPath(path)
            return

    def onTransferFiles(self):
        if self.tLocation == "N/A":
            raise Exception ([341], "Raid Location not defined")
            return
        row = self.sequences_listWidget.currentRow()
        selList = [x.row() for x in self.sequences_listWidget.selectedIndexes()]
        # return
        if row == -1:
            raise Exception([101], "No sequence selected")
            return

        logPath = os.path.join(self.databaseDir,"transferLogs")
        folderCheck(logPath)

        seqCopy = SeqCopyProgress()
        seqCopy.copysequence(self.sequenceData, selList, self.tLocation, logPath, self.rootPath)

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
            fullPath = self.rootPath
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
                QtGui.QApplication.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
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

    # def _loadJson(self, file):
    #     """Loads the given json file"""
    #     if os.path.isfile(file):
    #         try:
    #             with open(file, 'r') as f:
    #                 data = json.load(f)
    #                 return data
    #         except ValueError:
    #             msg = "Corrupted JSON file => %s" % file
    #             logger.error(msg)
    #             return -2 # code for corrupted json file
    #     else:
    #         return None
    #
    # def _dumpJson(self, data, file):
    #     """Saves the data to the json file"""
    #     with open(file, "w") as f:
    #         json.dump(data, f, indent=4)
    def _loadJson(self, file):
        """Loads the given json file"""
        # TODO : Is it paranoid checking?
        if os.path.isfile(file):
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    return data
            except ValueError:
                msg = "Corrupted JSON file => %s" % file
                # logger.error(msg)
                self._exception(200, msg)
                # return -2 # code for corrupted json file
        else:
            msg = "File cannot be found => %s" % file
            self._exception(201, msg)

    def _dumpJson(self, data, file):
        """Saves the data to the json file"""
        name, ext = os.path.splitext(file)
        tempFile = "{0}.tmp".format(name)
        with open(tempFile, "w") as f:
            json.dump(data, f, indent=4)
        copyfile(tempFile, file)
        os.remove(tempFile)


class DropLineEdit(QtGui.QLineEdit):
    dropped = QtCore.pyqtSignal(str)
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

class DeselectableTreeView(QtGui.QTreeView):
    deselected = QtCore.pyqtSignal(bool)
    def mousePressEvent(self, event):
        index = self.indexAt(event.pos()) # returns  -1 if click is outside
        if index.row() == -1:
            self.clearSelection()
            self.deselected.emit(True)
        QtGui.QTreeView.mousePressEvent(self, event)

class SeqCopyProgress(QtGui.QWidget):

    def __init__(self, src=None, dest=None):
        super(SeqCopyProgress, self).__init__()
        self.logger = None
        self.src = src
        self.dest = dest
        self.build_ui()
        self.terminated = False
        self.cancelAll = False
        self.errorFlag = False
        # self.copyfileobj(src=self.src, dst=self.dest)


    def build_ui(self):

        hbox = QtGui.QVBoxLayout()

        vbox = QtGui.QHBoxLayout()

        lbl_src = QtGui.QLabel('Source: ')
        lbl_dest = QtGui.QLabel('Destination: ')
        lbl_overall = QtGui.QLabel('Overall Progress:')
        self.pb = QtGui.QProgressBar()
        self.pbOverall = QtGui.QProgressBar()
        self.cancelButton = QtGui.QPushButton("Cancel")
        self.cancelAllButton = QtGui.QPushButton("Cancel All")

        self.pb.setMinimum(0)
        self.pb.setMaximum(100)
        self.pb.setValue(0)

        self.pbOverall.setMinimum(0)
        self.pbOverall.setMaximum(100)
        self.pbOverall.setValue(0)

        hbox.addWidget(lbl_src)
        hbox.addWidget(lbl_dest)
        hbox.addWidget(self.pb)
        hbox.addWidget(lbl_overall)
        hbox.addWidget(self.pbOverall)
        vbox.addWidget(self.cancelButton)
        vbox.addWidget(self.cancelAllButton)
        hbox.addLayout(vbox)
        self.setLayout(hbox)
        self.setWindowTitle('File copy')
        self.cancelButton.clicked.connect(self.terminate)
        self.cancelAllButton.clicked.connect(lambda: self.terminate(all=True))
        self.show()

    def results_ui(self, status, color="white", logPath=None, destPath = None):

        self.msgDialog = QtGui.QDialog(parent=self)
        self.msgDialog.QtGui(True)
        self.msgDialog.setObjectName("Result_Dialog")
        self.msgDialog.setWindowTitle("Transfer Results")
        self.msgDialog.resize(300,120)
        layoutMain = QtGui.QVBoxLayout()
        self.msgDialog.setLayout(layoutMain)

        infoHeader = QtGui.QLabel(status)

        infoHeader.setStyleSheet(""
                               "border: 18px solid black;"
                               "background-color: black;"
                               "font-size: 14px;"
                               "color: {0}"
                               "".format(color))

        layoutMain.addWidget(infoHeader)
        layoutH = QtGui.QHBoxLayout()
        layoutMain.addLayout(layoutH)
        if logPath:
            showLogButton = QtGui.QPushButton("Show Log File")
            layoutH.addWidget(showLogButton)
            showLogButton.clicked.connect(lambda x=logPath: os.startfile(x))
        showInExplorer = QtGui.QPushButton("Show in Explorer")
        layoutH.addWidget(showInExplorer)
        okButton = QtGui.QPushButton("OK")
        layoutH.addWidget(okButton)

        showInExplorer.clicked.connect(lambda x=destPath: self.onShowInExplorer(x))

        okButton.clicked.connect(self.msgDialog.close)

        self.msgDialog.show()



    def onShowInExplorer(self, path):
        os.startfile(path)
        pass


    def closeEvent(self, *args, **kwargs):
        self.terminated = True

    def terminate(self, all=False):
        self.terminated = True
        self.cancelAll = all
        # self.pb.setValue(100)
        # self.close()

    def safeLog(self, msg):
        try:
            self.logger.debug(msg)
        except AttributeError:
            pass

    def copyfileobj(self, src, dst):

        self.pb.setValue(0)
        self.terminated = False # reset the termination status
        totalCount = len(src)
        current = 0

        for i in src:
            targetPath = os.path.join(dst, os.path.basename(i))
            try:
                copyfile(i, targetPath)
            except:
                self.errorFlag = True
                self.safeLog("FAILED - unknown error")
            percent = (100 * current) / totalCount
            self.pb.setValue(percent)
            current += 1
            QtGui.QApplication.processEvents()
            self.safeLog("Success - {0}".format(targetPath))
            if self.terminated or self.cancelAll:
                self.errorFlag = True
                self.safeLog("FAILED - skipped by user")
                break

    def copysequence(self, sequenceData, selectionList, destination, logPath, root):

        now = datetime.datetime.now()
        logName = "fileTransferLog_{0}.txt".format(now.strftime("%Y.%m.%d.%H.%M"))
        logFile = os.path.join(logPath, logName)
        self.logger = self.setupLogger(logFile)
        totalCount = len(selectionList)
        current = 0
        for sel in selectionList:
            if self.cancelAll:
                self.safeLog("ALL CANCELED")
                break
            self.logger.debug(
                "---------------------------------------------\n"
                "Copy Progress - {0}\n"
                "---------------------------------------------".format(
                    sequenceData[sel]))
            percent = (100 * current) / totalCount
            self.pbOverall.setValue(percent)
            current += 1
            tFilesList = [i.path for i in sequenceData[sel]]
            subPath = os.path.split(os.path.relpath(tFilesList[0], root))[0]  ## get the relative path
            currentDate = now.strftime("%y%m%d")
            targetPath = os.path.join(destination, currentDate, subPath)
            if not os.path.isdir(os.path.normpath(targetPath)):
                os.makedirs(os.path.normpath(targetPath))
            self.copyfileobj(src=tFilesList, dst=targetPath)

        self.deleteLogger(self.logger)

        self.close()
        if self.cancelAll:
            self.results_ui("Canceled by user", logPath=logFile, destPath=destination)
        elif self.errorFlag:
            self.results_ui("Check log file for errors", color="red", logPath=logFile, destPath=destination)
        else:
            self.results_ui("Transfer Successfull", logPath=logFile, destPath=destination)
        pass

    def setupLogger(self, handlerPath):
        logger = logging.getLogger('imageViewer')
        file_logger = logging.FileHandler(handlerPath)
        logger.addHandler(file_logger)
        logger.setLevel(logging.DEBUG)
        return logger

    def deleteLogger(self, logger):
        for i in logger.handlers:
            logger.removeHandler(i)
            i.flush()
            i.close()