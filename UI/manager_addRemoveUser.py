# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manager_addRemoveUser.ui'
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

class Ui_users_Dialog(object):
    def setupUi(self, users_Dialog):
        users_Dialog.setObjectName(_fromUtf8("users_Dialog"))
        users_Dialog.resize(342, 243)

        self.userdatabase_groupBox = QtGui.QGroupBox(users_Dialog)
        self.userdatabase_groupBox.setGeometry(QtCore.QRect(10, 10, 321, 51))
        self.userdatabase_groupBox.setTitle(("User Database"))
        self.userdatabase_groupBox.setObjectName(("userdatabase_groupBox"))

        self.userdatabase_lineEdit = QtGui.QLineEdit(self.userdatabase_groupBox)
        self.userdatabase_lineEdit.setGeometry(QtCore.QRect(10, 20, 231, 20))
        self.userdatabase_lineEdit.setObjectName(_fromUtf8("userdatabase_lineEdit"))

        self.userdatabasebrowse_pushButton = QtGui.QPushButton(self.userdatabase_groupBox)
        self.userdatabasebrowse_pushButton.setGeometry(QtCore.QRect(250, 20, 61, 21))

        self.userdatabasebrowse_pushButton.setText(("Browse"))
        self.userdatabasebrowse_pushButton.setObjectName(("userdatabasebrowse_pushButton"))

        self.addnewuser_groupBox = QtGui.QGroupBox(users_Dialog)
        self.addnewuser_groupBox.setGeometry(QtCore.QRect(10, 70, 321, 91))
        self.addnewuser_groupBox.setTitle(("Add New User"))
        self.addnewuser_groupBox.setObjectName(("addnewuser_groupBox"))

        self.fullname_label = QtGui.QLabel(self.addnewuser_groupBox)
        self.fullname_label.setGeometry(QtCore.QRect(0, 30, 81, 21))
        self.fullname_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.fullname_label.setText(("Full Name:"))
        self.fullname_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.fullname_label.setObjectName(("fullname_label"))

        self.fullname_lineEdit = QtGui.QLineEdit(self.addnewuser_groupBox)
        self.fullname_lineEdit.setGeometry(QtCore.QRect(90, 30, 151, 20))
        self.fullname_lineEdit.setAccessibleDescription((""))
        self.fullname_lineEdit.setText((""))
        self.fullname_lineEdit.setPlaceholderText(("e.g \"John Doe\""))
        self.fullname_lineEdit.setObjectName(("fullname_lineEdit"))

        self.initials_label = QtGui.QLabel(self.addnewuser_groupBox)
        self.initials_label.setGeometry(QtCore.QRect(0, 60, 81, 21))
        self.initials_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.initials_label.setText(("Initials:"))
        self.initials_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.initials_label.setObjectName(("initials_label"))

        self.initials_lineEdit = QtGui.QLineEdit(self.addnewuser_groupBox)
        self.initials_lineEdit.setGeometry(QtCore.QRect(90, 60, 151, 20))
        self.initials_lineEdit.setText((""))
        self.initials_lineEdit.setPlaceholderText(("e.g \"jd\" (must be unique)"))
        self.initials_lineEdit.setObjectName(("initials_lineEdit"))

        self.addnewuser_pushButton = QtGui.QPushButton(self.addnewuser_groupBox)
        self.addnewuser_pushButton.setGeometry(QtCore.QRect(250, 30, 61, 51))
        self.addnewuser_pushButton.setText(("Add"))
        self.addnewuser_pushButton.setObjectName(("addnewuser_pushButton"))

        self.deleteuser_groupBox = QtGui.QGroupBox(users_Dialog)
        self.deleteuser_groupBox.setGeometry(QtCore.QRect(10, 170, 321, 51))
        self.deleteuser_groupBox.setTitle(("Delete User"))
        self.deleteuser_groupBox.setObjectName(("deleteuser_groupBox"))

        self.selectuser_comboBox = QtGui.QComboBox(self.deleteuser_groupBox)
        self.selectuser_comboBox.setGeometry(QtCore.QRect(10, 20, 231, 22))
        self.selectuser_comboBox.setObjectName(("selectuser_comboBox"))

        self.deleteuser_pushButton = QtGui.QPushButton(self.deleteuser_groupBox)
        self.deleteuser_pushButton.setGeometry(QtCore.QRect(250, 20, 61, 21))
        self.deleteuser_pushButton.setText(("Delete"))
        self.deleteuser_pushButton.setObjectName(("deleteuser_pushButton"))






        # QtCore.QMetaObject.connectSlotsByName(users_Dialog)