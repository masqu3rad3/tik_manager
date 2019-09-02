# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'assetLibrary_UI_MAIN_STR.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
     = QtCore.QString.fromUtf8
except AttributeError:
    def (s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_sceneManager_MainWindow(object):
    def setupUi(self, sceneManager_MainWindow):
        sceneManager_MainWindow.setObjectName(("sceneManager_MainWindow"))
        sceneManager_MainWindow.resize(735, 622)

        self.centralwidget = QtGui.QWidget(sceneManager_MainWindow)

        self.gridLayout_3 = QtGui.QGridLayout(self.centralwidget)
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setMaximumSize(QtCore.QSize(16777215, 167777))
        self.tabWidget.setTabPosition(QtGui.QTabWidget.North)
        self.tabWidget.setElideMode(QtCore.Qt.ElideNone)
        self.tabWidget.setUsesScrollButtons(False)
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(("tab"))
        self.gridLayout_4 = QtGui.QGridLayout(self.tab)
        self.gridLayout_4.setContentsMargins(9, -1, -1, -1)
        self.tabWidget.addTab(self.tab, ("Tab 1"))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(("tab_2"))
        self.tabWidget.addTab(self.tab_2, (""))
        self.gridLayout_3.addWidget(self.tabWidget, 1, 0, 1, 1)
        sceneManager_MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(sceneManager_MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 735, 21))
        self.menubar.setObjectName(("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuTools = QtGui.QMenu(self.menubar)
        sceneManager_MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(sceneManager_MainWindow)
        sceneManager_MainWindow.setStatusBar(self.statusbar)
        self.actionCreate_Project = QtGui.QAction(sceneManager_MainWindow)
        self.actionSave_Version = QtGui.QAction(sceneManager_MainWindow)
        self.actionSave_Base_Scene = QtGui.QAction(sceneManager_MainWindow)
        self.actionLoad_Reference_Scene = QtGui.QAction(sceneManager_MainWindow)
        self.actionAdd_Remove_Users = QtGui.QAction(sceneManager_MainWindow)
        self.actionPreview_Settings = QtGui.QAction(sceneManager_MainWindow)
        self.actionDelete_Selected_Base_Scene = QtGui.QAction(sceneManager_MainWindow)
        self.actionDelete_Reference_of_Selected_Scene = QtGui.QAction(sceneManager_MainWindow)
        self.actionProject_Report = QtGui.QAction(sceneManager_MainWindow)
        self.actionCheck_References = QtGui.QAction(sceneManager_MainWindow)
        self.actionImage_Manager = QtGui.QAction(sceneManager_MainWindow)
        self.actionSequence_Viewer = QtGui.QAction(sceneManager_MainWindow)
        self.actionImport_Selected_Item = QtGui.QAction(sceneManager_MainWindow)
        self.actionImport_Only = QtGui.QAction(sceneManager_MainWindow)
        self.actionAdd_New_Library = QtGui.QAction(sceneManager_MainWindow)
        self.actionRemove_Library = QtGui.QAction(sceneManager_MainWindow)
        self.menuFile.addAction(self.actionAdd_New_Library)
        self.menuFile.addAction(self.actionCreate_Project)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionLoad_Reference_Scene)
        self.menuFile.addAction(self.actionImport_Selected_Item)
        self.menuFile.addAction(self.actionImport_Only)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionAdd_Remove_Users)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionRemove_Library)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())

        self.retranslateUi(sceneManager_MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(sceneManager_MainWindow)

    def retranslateUi(self, sceneManager_MainWindow):
        sceneManager_MainWindow.setWindowTitle(_translate("sceneManager_MainWindow", "Scene Manager", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("sceneManager_MainWindow", "Tab 2", None))
        self.menuFile.setTitle(_translate("sceneManager_MainWindow", "File", None))
        self.menuTools.setTitle(_translate("sceneManager_MainWindow", "Tools", None))
        self.actionCreate_Project.setText(_translate("sceneManager_MainWindow", "Create New Asset", None))
        self.actionSave_Version.setText(_translate("sceneManager_MainWindow", "Save Version", None))
        self.actionSave_Base_Scene.setText(_translate("sceneManager_MainWindow", "Save Base Scene", None))
        self.actionLoad_Reference_Scene.setText(_translate("sceneManager_MainWindow", "Load Selected Asset", None))
        self.actionAdd_Remove_Users.setText(_translate("sceneManager_MainWindow", "Delete Selected Asset", None))
        self.actionPreview_Settings.setText(_translate("sceneManager_MainWindow", "Preview Settings", None))
        self.actionDelete_Selected_Base_Scene.setText(_translate("sceneManager_MainWindow", "Delete Selected Base Scene", None))
        self.actionDelete_Reference_of_Selected_Scene.setText(_translate("sceneManager_MainWindow", "Delete Reference of Selected Scene", None))
        self.actionProject_Report.setText(_translate("sceneManager_MainWindow", "Project Report", None))
        self.actionCheck_References.setText(_translate("sceneManager_MainWindow", "Check References", None))
        self.actionImage_Manager.setText(_translate("sceneManager_MainWindow", "Image Manager", None))
        self.actionSequence_Viewer.setText(_translate("sceneManager_MainWindow", "Sequence Viewer", None))
        self.actionImport_Selected_Item.setText(_translate("sceneManager_MainWindow", "Import and Copy Textures", None))
        self.actionImport_Only.setText(_translate("sceneManager_MainWindow", "Import Only", None))
        self.actionAdd_New_Library.setText(_translate("sceneManager_MainWindow", "Add New Library", None))
        self.actionRemove_Library.setText(_translate("sceneManager_MainWindow", "Remove Library", None))

