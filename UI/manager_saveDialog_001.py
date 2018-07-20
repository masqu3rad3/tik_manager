# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manager_saveDialog_001.ui'
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

class Ui_save_Dialog(object):
    def setupUi(self, save_Dialog):
        save_Dialog.setObjectName(_fromUtf8("save_Dialog"))
        save_Dialog.resize(255, 164)
        save_Dialog.setMinimumSize(QtCore.QSize(255, 164))
        save_Dialog.setMaximumSize(QtCore.QSize(255, 164))
        save_Dialog.setWindowTitle(_fromUtf8("Save New Base Scene"))
        save_Dialog.setToolTip(_fromUtf8(""))
        save_Dialog.setStatusTip(_fromUtf8(""))
        save_Dialog.setWhatsThis(_fromUtf8(""))
        save_Dialog.setAccessibleName(_fromUtf8(""))
        save_Dialog.setAccessibleDescription(_fromUtf8(""))
        self.buttonBox = QtGui.QDialogButtonBox(save_Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(20, 110, 220, 32))
        self.buttonBox.setToolTip(_fromUtf8(""))
        self.buttonBox.setStatusTip(_fromUtf8(""))
        self.buttonBox.setWhatsThis(_fromUtf8(""))
        self.buttonBox.setAccessibleName(_fromUtf8(""))
        self.buttonBox.setAccessibleDescription(_fromUtf8(""))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.comboBox = QtGui.QComboBox(save_Dialog)
        self.comboBox.setGeometry(QtCore.QRect(90, 70, 151, 22))
        self.comboBox.setToolTip(_fromUtf8(""))
        self.comboBox.setStatusTip(_fromUtf8(""))
        self.comboBox.setWhatsThis(_fromUtf8(""))
        self.comboBox.setAccessibleName(_fromUtf8(""))
        self.comboBox.setAccessibleDescription(_fromUtf8(""))
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.setItemText(0, _fromUtf8("Model"))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.setItemText(1, _fromUtf8("Shading"))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.setItemText(2, _fromUtf8("Rig"))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.setItemText(3, _fromUtf8("Animation"))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.setItemText(4, _fromUtf8("Render"))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.setItemText(5, _fromUtf8("Other"))
        self.label = QtGui.QLabel(save_Dialog)
        self.label.setGeometry(QtCore.QRect(20, 70, 61, 20))
        self.label.setToolTip(_fromUtf8(""))
        self.label.setStatusTip(_fromUtf8(""))
        self.label.setWhatsThis(_fromUtf8(""))
        self.label.setAccessibleName(_fromUtf8(""))
        self.label.setAccessibleDescription(_fromUtf8(""))
        self.label.setFrameShape(QtGui.QFrame.Box)
        self.label.setText(_fromUtf8("Category"))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(save_Dialog)
        self.label_2.setGeometry(QtCore.QRect(20, 30, 61, 20))
        self.label_2.setToolTip(_fromUtf8(""))
        self.label_2.setStatusTip(_fromUtf8(""))
        self.label_2.setWhatsThis(_fromUtf8(""))
        self.label_2.setAccessibleName(_fromUtf8(""))
        self.label_2.setAccessibleDescription(_fromUtf8(""))
        self.label_2.setFrameShape(QtGui.QFrame.Box)
        self.label_2.setText(_fromUtf8("Name"))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.lineEdit = QtGui.QLineEdit(save_Dialog)
        self.lineEdit.setGeometry(QtCore.QRect(90, 30, 151, 20))
        self.lineEdit.setToolTip(_fromUtf8(""))
        self.lineEdit.setStatusTip(_fromUtf8(""))
        self.lineEdit.setWhatsThis(_fromUtf8(""))
        self.lineEdit.setAccessibleName(_fromUtf8(""))
        self.lineEdit.setAccessibleDescription(_fromUtf8(""))
        self.lineEdit.setText(_fromUtf8(""))
        self.lineEdit.setCursorPosition(0)
        self.lineEdit.setPlaceholderText(_fromUtf8("Choose a unique name"))
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))

        self.retranslateUi(save_Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), save_Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), save_Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(save_Dialog)

    def retranslateUi(self, save_Dialog):
        pass

