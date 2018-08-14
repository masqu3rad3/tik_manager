# Obselete

import os
from shutil import copyfile

import Qt
from Qt import QtWidgets, QtCore, QtGui
if Qt.__binding__ == "PySide":
    from shiboken import wrapInstance
    from Qt.QtCore import Signal
elif Qt.__binding__.startswith('PyQt'):
    from sip import wrapinstance as wrapInstance
    from Qt.Core import pyqtSignal as Signal
else:
    from shiboken2 import wrapInstance
    from Qt.QtCore import Signal

class FileCopyProgress(QtWidgets.QWidget):

    def __init__(self, src=None, dest=None, logger=None):
        super(FileCopyProgress, self).__init__()
        self.logger = logger
        self.src = src
        self.dest = dest
        self.build_ui()
        self.terminated = False
        self.cancelAll = False
        self.copyfileobj(src=self.src, dst=self.dest)


    def build_ui(self):

        hbox = QtWidgets.QVBoxLayout()

        vbox = QtWidgets.QHBoxLayout()

        lbl_src = QtWidgets.QLabel('Source: %s' %os.path.split(self.src[0])[0])
        lbl_dest = QtWidgets.QLabel('Destination: %s' %self.dest)
        self.pb = QtWidgets.QProgressBar()
        self.cancelButton = QtWidgets.QPushButton("Cancel")
        self.cancelAllButton = QtWidgets.QPushButton("Cancel All")

        self.pb.setMinimum(0)
        self.pb.setMaximum(100)
        self.pb.setValue(0)

        hbox.addWidget(lbl_src)
        hbox.addWidget(lbl_dest)
        hbox.addWidget(self.pb)
        vbox.addWidget(self.cancelButton)
        vbox.addWidget(self.cancelAllButton)
        hbox.addLayout(vbox)
        self.setLayout(hbox)
        self.setWindowTitle('File copy')
        self.cancelButton.clicked.connect(self.terminate)
        self.cancelAllButton.clicked.connect(lambda: self.terminate(all=True))
        self.show()

    def success_ui(self):

        self.msg = QtWidgets.QMessageBox(parent=self)
        self.msg.setIcon(QtWidgets.QMessageBox.Information)
        self.msg.setText("Transfer Successfull")
        self.msg.setInformativeText("All selected sequences are transferred to the target location. Log file saved under <project>/data/transferLogs")
        self.msg.setWindowTitle("Transfer report")
        self.msg.setDetailedText("The details are as follows:")
        self.msg.show()


    def closeEvent(self, *args, **kwargs):
        self.terminated = True

    def terminate(self, all=False):
        self.terminated = True
        self.cancelAll = all
        self.pb.setValue(100)
        self.close()

    def safeLog(self, msg):
        try:
            self.logger.debug(msg)
        except AttributeError:
            pass

    def copyfileobj(self, src, dst):

        totalCount = len(src)
        current = 0

        for i in src:
            targetPath = os.path.join(dst, os.path.basename(i))
            try:
                copyfile(i, targetPath)
                print i
            except:
                self.safeLog("FAILED - unknown error")
            percent = (100 * current) / totalCount
            self.pb.setValue(percent)
            current += 1
            QtWidgets.QApplication.processEvents()
            self.safeLog("Success - {0}".format(targetPath))
            if self.terminated:
                self.safeLog("FAILED - terminated by user")
                break
