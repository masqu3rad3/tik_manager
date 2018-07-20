# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manager_creageProjectDialog_001.ui'
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

class Ui_createproject_Dialog(object):
    def setupUi(self, createproject_Dialog):
        createproject_Dialog.setObjectName(("createproject_Dialog"))
        createproject_Dialog.resize(419, 249)
        createproject_Dialog.setWindowTitle(("Create New Project"))
        createproject_Dialog.setToolTip((""))
        createproject_Dialog.setStatusTip((""))
        createproject_Dialog.setWhatsThis((""))
        createproject_Dialog.setAccessibleName((""))
        createproject_Dialog.setAccessibleDescription((""))

        self.projectpath_label = QtGui.QLabel(createproject_Dialog)
        self.projectpath_label.setGeometry(QtCore.QRect(20, 30, 71, 20))
        self.projectpath_label.setText(("Project Path:"))
        self.projectpath_label.setObjectName(("projectpath_label"))

        self.projectpath_lineEdit = QtGui.QLineEdit(createproject_Dialog)
        self.projectpath_lineEdit.setGeometry(QtCore.QRect(90, 30, 241, 21))
        self.projectpath_lineEdit.setText((""))
        self.projectpath_lineEdit.setPlaceholderText((""))
        self.projectpath_lineEdit.setObjectName(("projectpath_lineEdit"))

        self.browse_pushButton = QtGui.QPushButton(createproject_Dialog)
        self.browse_pushButton.setGeometry(QtCore.QRect(340, 30, 61, 21))
        self.browse_pushButton.setObjectName(("browse_pushButton"))

        self.resolvedpath_label = QtGui.QLabel(createproject_Dialog)
        self.resolvedpath_label.setGeometry(QtCore.QRect(20, 70, 381, 21))
        self.resolvedpath_label.setObjectName(("resolvedpath_label"))

        self.brandname_label = QtGui.QLabel(createproject_Dialog)
        self.brandname_label.setGeometry(QtCore.QRect(20, 110, 111, 20))
        self.brandname_label.setFrameShape(QtGui.QFrame.Box)
        self.brandname_label.setText(("Brand Name"))
        self.brandname_label.setAlignment(QtCore.Qt.AlignCenter)
        self.brandname_label.setObjectName(("brandname_label"))

        self.projectname_label = QtGui.QLabel(createproject_Dialog)
        self.projectname_label.setGeometry(QtCore.QRect(140, 110, 131, 20))
        self.projectname_label.setFrameShape(QtGui.QFrame.Box)
        self.projectname_label.setText(("Project Name"))
        self.projectname_label.setAlignment(QtCore.Qt.AlignCenter)
        self.projectname_label.setObjectName(("projectname_label"))

        self.client_label = QtGui.QLabel(createproject_Dialog)
        self.client_label.setGeometry(QtCore.QRect(280, 110, 121, 20))
        self.client_label.setFrameShape(QtGui.QFrame.Box)
        self.client_label.setText(("Client"))
        self.client_label.setAlignment(QtCore.Qt.AlignCenter)
        self.client_label.setObjectName(("client_label"))

        self.brandname_lineEdit = QtGui.QLineEdit(createproject_Dialog)
        self.brandname_lineEdit.setGeometry(QtCore.QRect(20, 140, 111, 21))
        self.brandname_lineEdit.setText((""))
        self.brandname_lineEdit.setPlaceholderText(("(optional)"))
        self.brandname_lineEdit.setObjectName(("brandname_lineEdit"))

        self.projectname_lineEdit = QtGui.QLineEdit(createproject_Dialog)
        self.projectname_lineEdit.setGeometry(QtCore.QRect(140, 140, 131, 21))
        self.projectname_lineEdit.setText((""))
        self.projectname_lineEdit.setPlaceholderText(("Mandatory Field"))
        self.projectname_lineEdit.setObjectName(("projectname_lineEdit"))

        self.client_lineEdit = QtGui.QLineEdit(createproject_Dialog)
        self.client_lineEdit.setGeometry(QtCore.QRect(280, 140, 121, 21))
        self.client_lineEdit.setText((""))
        self.client_lineEdit.setPlaceholderText(("Mandatory Field"))
        self.client_lineEdit.setObjectName(("client_lineEdit"))

        self.buttonBox = QtGui.QDialogButtonBox(createproject_Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(30, 190, 371, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(("buttonBox"))



