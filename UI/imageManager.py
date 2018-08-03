# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'imageManager.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_imanager_MainWindow(object):
    def setupUi(self, imanager_MainWindow):
        imanager_MainWindow.setObjectName(_fromUtf8("imanager_MainWindow"))
        imanager_MainWindow.resize(656, 402)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(imanager_MainWindow.sizePolicy().hasHeightForWidth())
        imanager_MainWindow.setSizePolicy(sizePolicy)
        imanager_MainWindow.setToolTip(_fromUtf8(""))
        imanager_MainWindow.setStatusTip(_fromUtf8(""))
        imanager_MainWindow.setWhatsThis(_fromUtf8(""))
        imanager_MainWindow.setAccessibleName(_fromUtf8(""))
        imanager_MainWindow.setAccessibleDescription(_fromUtf8(""))
        imanager_MainWindow.setWindowFilePath(_fromUtf8(""))
        self.centralwidget = QtGui.QWidget(imanager_MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.foolcheck_label = QtGui.QLabel(self.centralwidget)
        self.foolcheck_label.setToolTip(_fromUtf8(""))
        self.foolcheck_label.setStatusTip(_fromUtf8(""))
        self.foolcheck_label.setWhatsThis(_fromUtf8(""))
        self.foolcheck_label.setAccessibleName(_fromUtf8(""))
        self.foolcheck_label.setAccessibleDescription(_fromUtf8(""))
        self.foolcheck_label.setObjectName(_fromUtf8("foolcheck_label"))
        self.gridLayout.addWidget(self.foolcheck_label, 3, 0, 1, 1)
        self.projectPath_label = QtGui.QLabel(self.centralwidget)
        self.projectPath_label.setFrameShape(QtGui.QFrame.Box)
        self.projectPath_label.setLineWidth(1)
        self.projectPath_label.setScaledContents(False)
        self.projectPath_label.setObjectName(_fromUtf8("projectPath_label"))
        self.gridLayout.addWidget(self.projectPath_label, 0, 0, 1, 1)
        self.imagePath_label = QtGui.QLabel(self.centralwidget)
        self.imagePath_label.setToolTip(_fromUtf8(""))
        self.imagePath_label.setStatusTip(_fromUtf8(""))
        self.imagePath_label.setWhatsThis(_fromUtf8(""))
        self.imagePath_label.setAccessibleName(_fromUtf8(""))
        self.imagePath_label.setAccessibleDescription(_fromUtf8(""))
        self.imagePath_label.setFrameShape(QtGui.QFrame.Box)
        self.imagePath_label.setObjectName(_fromUtf8("imagePath_label"))
        self.gridLayout.addWidget(self.imagePath_label, 1, 0, 1, 1)
        self.foolcheck_listView = QtGui.QListView(self.centralwidget)
        self.foolcheck_listView.setToolTip(_fromUtf8(""))
        self.foolcheck_listView.setStatusTip(_fromUtf8(""))
        self.foolcheck_listView.setWhatsThis(_fromUtf8(""))
        self.foolcheck_listView.setAccessibleName(_fromUtf8(""))
        self.foolcheck_listView.setAccessibleDescription(_fromUtf8(""))
        self.foolcheck_listView.setObjectName(_fromUtf8("foolcheck_listView"))
        self.gridLayout.addWidget(self.foolcheck_listView, 4, 0, 1, 3)
        self.sendDeadline_pushButton = QtGui.QPushButton(self.centralwidget)
        self.sendDeadline_pushButton.setToolTip(_fromUtf8(""))
        self.sendDeadline_pushButton.setStatusTip(_fromUtf8(""))
        self.sendDeadline_pushButton.setWhatsThis(_fromUtf8(""))
        self.sendDeadline_pushButton.setAccessibleName(_fromUtf8(""))
        self.sendDeadline_pushButton.setAccessibleDescription(_fromUtf8(""))
        self.sendDeadline_pushButton.setObjectName(_fromUtf8("sendDeadline_pushButton"))
        self.gridLayout.addWidget(self.sendDeadline_pushButton, 6, 0, 1, 3)
        self.setProject_pushButton = QtGui.QPushButton(self.centralwidget)
        self.setProject_pushButton.setObjectName(_fromUtf8("setProject_pushButton"))
        self.gridLayout.addWidget(self.setProject_pushButton, 0, 2, 1, 1)
        self.projectPath_lineEdit = QtGui.QLineEdit(self.centralwidget)
        self.projectPath_lineEdit.setObjectName(_fromUtf8("projectPath_lineEdit"))
        self.gridLayout.addWidget(self.projectPath_lineEdit, 0, 1, 1, 1)
        self.imagePath_lineEdit = QtGui.QLineEdit(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.imagePath_lineEdit.sizePolicy().hasHeightForWidth())
        self.imagePath_lineEdit.setSizePolicy(sizePolicy)
        self.imagePath_lineEdit.setObjectName(_fromUtf8("imagePath_lineEdit"))
        self.gridLayout.addWidget(self.imagePath_lineEdit, 1, 1, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 15, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 15, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        self.gridLayout.addItem(spacerItem1, 5, 0, 1, 1)
        imanager_MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(imanager_MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 656, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        imanager_MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(imanager_MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        imanager_MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(imanager_MainWindow)
        QtCore.QMetaObject.connectSlotsByName(imanager_MainWindow)

    def retranslateUi(self, imanager_MainWindow):
        imanager_MainWindow.setWindowTitle(_translate("imanager_MainWindow", "Image Manager", None))
        self.foolcheck_label.setText(_translate("imanager_MainWindow", "Warnings:", None))
        self.projectPath_label.setText(_translate("imanager_MainWindow", "Project:", None))
        self.imagePath_label.setText(_translate("imanager_MainWindow", "Image Path:", None))
        self.sendDeadline_pushButton.setText(_translate("imanager_MainWindow", "Send To Deadline", None))
        self.setProject_pushButton.setText(_translate("imanager_MainWindow", "SET", None))

