import pyseq as seq
import os
import pymel.core as pm

import Qt
from Qt import QtWidgets, QtCore, QtGui
from maya import OpenMayaUI as omui

if Qt.__binding__ == "PySide":
    from shiboken import wrapInstance
    from Qt.QtCore import Signal
elif Qt.__binding__.startswith('PyQt'):
    from sip import wrapinstance as wrapInstance
    from Qt.Core import pyqtSignal as Signal
else:
    from shiboken2 import wrapInstance
    from Qt.QtCore import Signal

windowName = "Image_Viewer"

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

        self.setObjectName(windowName)
        self.resize(670, 624)
        self.setWindowTitle(windowName)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName(("centralwidget"))
        self.model = QtWidgets.QFileSystemModel()
        self.projectPath=os.path.join(os.path.normpath(pm.workspace(q=1, rd=1)), "images")
        self.model.setRootPath(self.projectPath)
        # filter = Qt.QStringList("")
        self.model.setFilter(QtCore.QDir.AllDirs|QtCore.QDir.NoDotAndDotDot)
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

        self.rootFolder_lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.rootFolder_lineEdit.setText((""))
        self.rootFolder_lineEdit.setPlaceholderText((""))
        self.rootFolder_lineEdit.setObjectName(("rootFolder_lineEdit"))
        self.gridLayout.addWidget(self.rootFolder_lineEdit, 0, 1, 1, 1)

        self.browse_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.browse_pushButton.setText(("Browse"))
        self.browse_pushButton.setObjectName(("browse_pushButton"))
        self.gridLayout.addWidget(self.browse_pushButton, 0, 2, 1, 1)

        self.rootFolder_label = QtWidgets.QLabel(self.centralwidget)
        self.rootFolder_label.setFrameShape(QtWidgets.QFrame.Box)
        self.rootFolder_label.setLineWidth(1)
        self.rootFolder_label.setText(("Root Folder:"))
        self.rootFolder_label.setTextFormat(QtCore.Qt.AutoText)
        self.rootFolder_label.setScaledContents(False)
        self.rootFolder_label.setObjectName(("rootFolder_label"))
        self.gridLayout.addWidget(self.rootFolder_label, 0, 0, 1, 1)

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
        self.gridLayout.addWidget(self.splitter, 1, 0, 1, 4)

        # QtCore.QObject.connect(self.directories_treeView.selectionModel(), QtCore.Signal('selectionChanged(QItemSelection, QItemSelection)'),
        #                        self.test)
        self.directories_treeView.selectionModel().selectionChanged.connect(self.populate)
        self.recursive_checkBox.stateChanged.connect(self.populate)

    # @Qt.QtCore.pyqtSlot("QItemSelection, QItemSelection")
    def populate(self):
        self.sequences_listWidget.clear()
        index = self.directories_treeView.currentIndex()
        fullPath = self.model.filePath(index)

        # if self.recursive_checkBox.isChecked():
        #     anan = getTheImages(fullPath, level=-1)
        # else:
        #     anan = getTheImages(fullPath, level=1)
        #
        #
        #
        # for x in anan:
        #     for i in x[2]:
        #         self.sequences_listWidget.addItem(i.format('%h%t %R'))

        if self.recursive_checkBox.isChecked():
            rec=-1
        else:
            rec=1

        gen = seq.walk(fullPath, level=rec)

        for x in gen:
            for i in x[2]:
                self.sequences_listWidget.addItem(i.format('%h%t %R'))


        # for i in anan[0][2]:
        #     self.sequences_listWidget.addItem(i.format('%h%t %R'))



# testUI().show()

