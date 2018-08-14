"""
Transfers sequences to the defined location
Works on PySeq objects
"""

import os
from shutil import copyfile
import pyseq
import datetime
import logging

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

class SeqCopyProgress(QtWidgets.QWidget):

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

        hbox = QtWidgets.QVBoxLayout()

        vbox = QtWidgets.QHBoxLayout()

        lbl_src = QtWidgets.QLabel('Source: ')
        lbl_dest = QtWidgets.QLabel('Destination: ')
        lbl_overall = QtWidgets.QLabel('Overall Progress:')
        self.pb = QtWidgets.QProgressBar()
        self.pbOverall = QtWidgets.QProgressBar()
        self.cancelButton = QtWidgets.QPushButton("Cancel")
        self.cancelAllButton = QtWidgets.QPushButton("Cancel All")

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

    def results_ui(self, status, color="white", logPath=None):

        self.msgDialog = QtWidgets.QDialog(parent=self)
        self.msgDialog.setModal(True)
        self.msgDialog.setObjectName("Result_Dialog")
        self.msgDialog.setWindowTitle("Transfer Results")
        self.msgDialog.resize(300,120)
        layoutMain = QtWidgets.QVBoxLayout()
        self.msgDialog.setLayout(layoutMain)

        infoHeader = QtWidgets.QLabel(status)

        infoHeader.setStyleSheet(""
                               "border: 18px solid black;"
                               "background-color: black;"
                               "font-size: 14px;"
                               "color: {0}"
                               "".format(color))

        layoutMain.addWidget(infoHeader)
        layoutH = QtWidgets.QHBoxLayout()
        layoutMain.addLayout(layoutH)
        if logPath:
            showLogButton = QtWidgets.QPushButton("Show Log File")
            layoutH.addWidget(showLogButton)
            showLogButton.clicked.connect(lambda x=logPath: os.startfile(x))
        okButton = QtWidgets.QPushButton("OK")
        layoutH.addWidget(okButton)


        okButton.clicked.connect(self.msgDialog.close)

        self.msgDialog.show()


        # # self.msg = QtWidgets.QMessageBox(parent=self)
        # # self.msg.setIcon(QtWidgets.QMessageBox.Information)
        # # self.msg.setText("Transfer Successfull")
        # # self.msg.setInformativeText("Log file saved to")
        # # self.msg.setWindowTitle("Transfer report")
        # # self.msg.setDefaultButton(QtWidgets.QPushButton("ANBAN"))
        # # # self.msg.setDetailedText("The details are as follows:")
        # # self.msg.show()
        # self.msgBox = QtWidgets.QMessageBox()
        # self.msgBox.setText("Transfer Successfull")
        # self.msgBox.setStandardButtons(QtWidgets.QMessageBox.Open | QtWidgets.QMessageBox.Ok);
        # self.msgBox.setDefaultButton(QtWidgets.QMessageBox.Ok);
        # # self.msgBox.addButton(QtWidgets.QPushButton('Show Log'), QtWidgets.QMessageBox.HelpRole)
        # # self.msgBox.addButton(QtWidgets.QPushButton('Ok'), QtWidgets.QMessageBox.AcceptRole)
        # self.msgBox.show()
        # # ret = self.msgBox.exec_()



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
            QtWidgets.QApplication.processEvents()
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
            self.results_ui("Canceled by user", logPath=logFile)
        elif self.errorFlag:
            self.results_ui("Check log file for errors", color="red", logPath=logFile)
        else:
            self.results_ui("Transfer Successfull", logPath=logFile)
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