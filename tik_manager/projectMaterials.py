#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------------------------
# Copyright (c) 2017-2018, Arda Kutlu (ardakutlu@gmail.com)
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  - Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
#  - Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
#  - Neither the name of the software nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# -----------------------------------------------------------------------------


# Module to view and organize project materials
# ---------------
# GET ENVIRONMENT
# ---------------
import _version
BoilerDict = {"Environment": "Standalone",
              "MainWindow": None,
              "WindowTitle": "Project Materials - Standalone v%s" % _version.__version__,
              "Stylesheet": "mayaDark.stylesheet"}

try:
    from maya import OpenMayaUI as omui
    import maya.cmds as cmds
    import Qt
    from Qt import QtWidgets, QtCore, QtGui
    from tik_manager.coreFunctions.coreFunctions_Maya import MayaCoreFunctions as CoreFunctions

    BoilerDict["Environment"] = "Maya"
    BoilerDict["WindowTitle"] = "Project Materials Maya v%s" % _version.__version__
except ImportError:
    pass

try:
    import MaxPlus
    import Qt
    from Qt import QtWidgets, QtCore, QtGui
    from tik_manager.coreFunctions.coreFunctions_Max import MaxCoreFunctions as CoreFunctions

    BoilerDict["Environment"] = "3dsMax"
    BoilerDict["WindowTitle"] = "Project Materials 3ds Max v%s" % _version.__version__
except ImportError:
    pass

try:
    import hou
    import Qt
    from Qt import QtWidgets, QtCore, QtGui
    from tik_manager.coreFunctions.coreFunctions_Houdini import HoudiniCoreFunctions as CoreFunctions

    BoilerDict["Environment"] = "Houdini"
    BoilerDict["WindowTitle"] = "Project Materials Houdini v%s" % _version.__version__
except ImportError:
    pass

try:
    import nuke
    import Qt
    from Qt import QtWidgets, QtCore, QtGui
    from tik_manager.coreFunctions.coreFunctions_Nuke import NukeCoreFunctions as CoreFunctions

    BoilerDict["Environment"] = "Nuke"
    BoilerDict["WindowTitle"] = "Project Materials Nuke v%s" % _version.__version__
except ImportError:
    pass

try:
    from PyQt5 import QtWidgets, QtCore, QtGui
    CoreFunctions = object
    BoilerDict["Environment"] = "Standalone"
    BoilerDict["WindowTitle"] = "Project Materials Standalone v%s" % _version.__version__
    FORCE_QT5 = True
except ImportError:
    FORCE_QT5 = False

import os
import sys
import unicodedata
from glob import glob



# FORCE_QT5 = bool(int(os.environ["FORCE_QT5"]))

# Enabele FORCE_QT5 for compiling with pyinstaller
# FORCE_QT5 = True

# if FORCE_QT5:
#     from PyQt4 import QtCore, Qt
#     from PyQt4 import QtGui as QtWidgets
# else:
#     import Qt
#     from Qt import QtWidgets, QtCore, QtGui

from SmRoot import RootManager

# import pyseq as seq

# import json
import datetime
# from shutil import copyfile
import shutil
import logging

## DO NOT REMOVE THIS:
import iconsSource as icons
## DO NOT REMOVE THIS:

logging.basicConfig()
logger = logging.getLogger('projectMaterials')
logger.setLevel(logging.WARNING)

__author__ = "Arda Kutlu"
__copyright__ = "Copyright 2018, Scene Manager - Project materials"
__credits__ = []
__license__ = "GPL"
__maintainer__ = "Arda Kutlu"
__email__ = "ardakutlu@gmail.com"
__status__ = "Development"



ColorStyleDict = {"Storyboard": "border: 2px solid #ff7b00",
             "Brief": "border: 2px solid #faff00",
             "Reference": "border: 2px solid #72ff00",
             "Artwork": "border: 2px solid #00f6ff",
             "Footage": "border: 2px solid #003fff",
             "Other": "border: 2px solid #dc00ff"
             }
# ColorStyleDict = {"Storyboard": "background: #ff7b00",
#              "Brief": "background: #faff00",
#              "Reference": "background: #72ff00",
#              "Artwork": "background: #00f6ff",
#              "Footage": "background: #003fff",
#              "Other": "background: #dc00ff"
#              }




def getMainWindow():
    """This function should be overriden"""
    if BoilerDict["Environment"] == "Maya":
        if Qt.__binding__ == "PySide":
            from shiboken import wrapInstance
        elif Qt.__binding__.startswith('PyQt'):
            from sip import wrapinstance as wrapInstance
        else:
            from shiboken2 import wrapInstance
        win = omui.MQtUtil_mainWindow()
        ptr = wrapInstance(long(win), QtWidgets.QMainWindow)
        return ptr

    elif BoilerDict["Environment"] == "3dsMax":
        try: mainWindow = MaxPlus.GetQMaxWindow()
        except AttributeError: mainWindow = MaxPlus.GetQMaxMainWindow()
        return mainWindow

    elif BoilerDict["Environment"] == "Houdini":
        return hou.qt.mainWindow()

    elif BoilerDict["Environment"] == "Nuke":
        app = QtWidgets.QApplication.instance()
        for widget in app.topLevelWidgets():
            if widget.metaObject().className() == 'Foundry::UI::DockMainWindow':
                return widget
        return None

    else:
        return None


# class ImageWidget(QtWidgets.QLabel):
#     """Custom class for thumbnail section. Keeps the aspect ratio when resized."""
#     def __init__(self, parent=None):
#         super(ImageWidget, self).__init__(parent)
#         self.aspectRatio = 1.78
#         sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
#         sizePolicy.setHeightForWidth(True)
#         self.setSizePolicy(sizePolicy)
#
#     def resizeEvent(self, r):
#         h = self.width()
#         # self.setFixedHeight(h/self.aspectRatio)
#         self.set(self.width(), self.width()/self.aspectRatio)
#         # self.setMinimumHeight(h/self.aspectRatio)
#         # self.setMaximumHeight(h/self.aspectRatio)
#         # self.heightForWidth(h/self.aspectRatio)
#         # self.setBaseSize(50, 50)
#         # self.set

class QFileAndFolderDialog(QtWidgets.QFileDialog):
    def __init__(self, *args):
        QtWidgets.QFileDialog.__init__(self, *args)
        self.setOption(self.DontUseNativeDialog, True)
        self.setFileMode(self.ExistingFiles)
        btns = self.findChildren(QtWidgets.QPushButton)
        self.openBtn = [x for x in btns if 'open' in str(x.text()).lower()][0]
        self.openBtn.clicked.disconnect()
        self.openBtn.clicked.connect(self.openClicked)
        self.tree = self.findChild(QtWidgets.QTreeView)

    def openClicked(self):
        inds = self.tree.selectionModel().selectedIndexes()
        files = []
        for i in inds:
            if i.column() == 0:
                # print self.directory().absolutePath(), i.data()
                # files.append(os.path.join(str(self.directory().absolutePath()),str(i.data().toString())))
                # print "varyant", i.data().toString()
                dir = str(self.directory().absolutePath())
                # file = str((i.data().toString()))
                if not type(i.data()) == unicode:
                    file = str(i.data().toString())
                else:
                    # PyQt4 differences...
                    file = str(i.data())
                path = os.path.normpath(os.path.join(dir, file))
                # encodedPath = path.encode("ascii", )
                files.append(path)
        self.selectedFiles = files
        self.hide()

    def filesSelected(self):
        return self.selectedFiles

class QtImageViewer(QtWidgets.QGraphicsView):
    """ PyQt image viewer widget for a QPixmap in a QGraphicsView scene with mouse zooming and panning.
    Displays a QImage or QPixmap (QImage is internally converted to a QPixmap).
    To display any other image format, you must first convert it to a QImage or QPixmap.
    Some useful image format conversion utilities:
        qimage2ndarray: NumPy ndarray <==> QImage    (https://github.com/hmeine/qimage2ndarray)
        ImageQt: PIL Image <==> QImage  (https://github.com/python-pillow/Pillow/blob/master/PIL/ImageQt.py)
    Mouse interaction:
        Left mouse button drag: Pan image.
        Right mouse button drag: Zoom box.
        Right mouse button doubleclick: Zoom to show entire image.
    """

    # Mouse button signals emit image scene (x, y) coordinates.
    # !!! For image (row, column) matrix indexing, row = y and column = x.
    if FORCE_QT5:
        leftMouseButtonPressed = QtCore.pyqtSignal(float, float)
        rightMouseButtonPressed = QtCore.pyqtSignal(float, float)
        leftMouseButtonReleased = QtCore.pyqtSignal(float, float)
        rightMouseButtonReleased = QtCore.pyqtSignal(float, float)
        leftMouseButtonDoubleClicked = QtCore.pyqtSignal(float, float)
        rightMouseButtonDoubleClicked = QtCore.pyqtSignal(float, float)
    else:
        leftMouseButtonPressed = QtCore.Signal(float, float)
        rightMouseButtonPressed = QtCore.Signal(float, float)
        leftMouseButtonReleased = QtCore.Signal(float, float)
        rightMouseButtonReleased = QtCore.Signal(float, float)
        leftMouseButtonDoubleClicked = QtCore.Signal(float, float)
        rightMouseButtonDoubleClicked = QtCore.Signal(float, float)

    def __init__(self):
        QtWidgets.QGraphicsView.__init__(self)

        # Image is displayed as a QPixmap in a QGraphicsScene attached to this QGraphicsView.
        self.scene = QtWidgets.QGraphicsScene()
        self.setScene(self.scene)

        # Store a local handle to the scene's current image pixmap.
        self._pixmapHandle = None

        # Image aspect ratio mode.
        # !!! ONLY applies to full image. Aspect ratio is always ignored when zooming.
        #   Qt.IgnoreAspectRatio: Scale image to fit viewport.
        #   Qt.KeepAspectRatio: Scale image to fit inside viewport, preserving aspect ratio.
        #   Qt.KeepAspectRatioByExpanding: Scale image to fill the viewport, preserving aspect ratio.
        self.aspectRatioMode = QtCore.Qt.KeepAspectRatio

        # Scroll bar behaviour.
        #   Qt.ScrollBarAlwaysOff: Never shows a scroll bar.
        #   Qt.ScrollBarAlwaysOn: Always shows a scroll bar.
        #   Qt.ScrollBarAsNeeded: Shows a scroll bar only when zoomed.
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        # Stack of QRectF zoom boxes in scene coordinates.
        self.zoomStack = []

        # Flags for enabling/disabling mouse interaction.
        self.canZoom = True
        self.canPan = True

    def hasImage(self):
        """ Returns whether or not the scene contains an image pixmap.
        """
        return self._pixmapHandle is not None

    def clearImage(self):
        """ Removes the current image pixmap from the scene if it exists.
        """
        if self.hasImage():
            self.scene.removeItem(self._pixmapHandle)
            self._pixmapHandle = None

    def pixmap(self):
        """ Returns the scene's current image pixmap as a QPixmap, or else None if no image exists.
        :rtype: QPixmap | None
        """
        if self.hasImage():
            return self._pixmapHandle.pixmap()
        return None

    def image(self):
        """ Returns the scene's current image pixmap as a QImage, or else None if no image exists.
        :rtype: QImage | None
        """
        if self.hasImage():
            return self._pixmapHandle.pixmap().toImage()
        return None

    def setImage(self, image):
        """ Set the scene's current image pixmap to the input QImage or QPixmap.
        Raises a RuntimeError if the input image has type other than QImage or QPixmap.
        :type image: QImage | QPixmap
        """
        if type(image) is QtGui.QPixmap:
            pixmap = image
        elif type(image) is QtGui.QImage:
            pixmap = QtGui.QPixmap.fromImage(image)
        else:
            raise RuntimeError("ImageViewer.setImage: Argument must be a QImage or QPixmap.")

        if self.hasImage():
            self._pixmapHandle.setPixmap(pixmap)
        else:
            self._pixmapHandle = self.scene.addPixmap(pixmap)

        self.setSceneRect(QtCore.QRectF(pixmap.rect()))  # Set scene size to image size.
        self.updateViewer()

    def loadImageFromFile(self, fileName=""):
        """ Load an image from file.
        Without any arguments, loadImageFromFile() will popup a file dialog to choose the image file.
        With a fileName argument, loadImageFromFile(fileName) will attempt to load the specified image file directly.
        """
        if len(fileName) == 0:
            if QtCore.QT_VERSION_STR[0] == '5':
                fileName, dummy = QtWidgets.QFileDialog.getOpenFileName(self, "Open image file.")
            else:
                fileName = QtWidgets.QFileDialog.getOpenFileName(self, "Open image file.")

        if len(fileName) and os.path.isfile(fileName):
            image = QtWidgets.QImage(fileName)
            self.setImage(image)

    def updateViewer(self):
        """ Show current zoom (if showing entire image, apply current aspect ratio mode).
        """
        if not self.hasImage():
            return
        if len(self.zoomStack) and self.sceneRect().contains(self.zoomStack[-1]):
            self.fitInView(self.zoomStack[-1], QtCore.Qt.IgnoreAspectRatio)  # Show zoomed rect (ignore aspect ratio).
        else:
            self.zoomStack = []  # Clear the zoom stack (in case we got here because of an invalid zoom).
            self.fitInView(self.sceneRect(), self.aspectRatioMode)  # Show entire image (use current aspect ratio mode).

    def resizeEvent(self, event):
        """ Maintain current zoom on resize.
        """
        self.updateViewer()

    def mousePressEvent(self, event):
        """ Start mouse pan or zoom mode.
        """
        scenePos = self.mapToScene(event.pos())
        if event.button() == QtCore.Qt.LeftButton:
            if self.canPan:
                self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            self.leftMouseButtonPressed.emit(scenePos.x(), scenePos.y())
        elif event.button() == QtCore.Qt.RightButton:
            if self.canZoom:
                self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
            self.rightMouseButtonPressed.emit(scenePos.x(), scenePos.y())
        QtWidgets.QGraphicsView.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        """ Stop mouse pan or zoom mode (apply zoom if valid).
        """
        QtWidgets.QGraphicsView.mouseReleaseEvent(self, event)
        scenePos = self.mapToScene(event.pos())
        if event.button() == QtCore.Qt.LeftButton:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self.leftMouseButtonReleased.emit(scenePos.x(), scenePos.y())
        elif event.button() == QtCore.Qt.RightButton:
            if self.canZoom:
                viewBBox = self.zoomStack[-1] if len(self.zoomStack) else self.sceneRect()
                selectionBBox = self.scene.selectionArea().boundingRect().intersected(viewBBox)
                self.scene.setSelectionArea(QtGui.QPainterPath())  # Clear current selection area.
                if selectionBBox.isValid() and (selectionBBox != viewBBox):
                    self.zoomStack.append(selectionBBox)
                    self.updateViewer()
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self.rightMouseButtonReleased.emit(scenePos.x(), scenePos.y())

    def mouseDoubleClickEvent(self, event):
        """ Show entire image.
        """
        scenePos = self.mapToScene(event.pos())
        if event.button() == QtCore.Qt.LeftButton:
            self.leftMouseButtonDoubleClicked.emit(scenePos.x(), scenePos.y())
        elif event.button() == QtCore.Qt.RightButton:
            if self.canZoom:
                self.zoomStack = []  # Clear zoom stack.
                self.updateViewer()
            self.rightMouseButtonDoubleClicked.emit(scenePos.x(), scenePos.y())
        QtWidgets.QGraphicsView.mouseDoubleClickEvent(self, event)

class CopyProgress(QtWidgets.QWidget):
    """Custom Widget for visualizing progress of file transfer"""

    def __init__(self, logPath=None):
        super(CopyProgress, self).__init__()
        self.logPath = logPath
        self.logger = None
        # self.src = src
        # self.dest = dest
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

    def results_ui(self, status, color="white", logPath=None, destPath=None):

        self.msgDialog = QtWidgets.QDialog(parent=self)
        self.msgDialog.setModal(True)
        self.msgDialog.setObjectName("Result_Dialog")
        self.msgDialog.setWindowTitle("Transfer Results")
        self.msgDialog.resize(300, 120)
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
        showInExplorer = QtWidgets.QPushButton("Show in Explorer")
        layoutH.addWidget(showInExplorer)
        okButton = QtWidgets.QPushButton("OK")
        layoutH.addWidget(okButton)

        showInExplorer.clicked.connect(lambda x=destPath: self.onShowInExplorer(destPath))

        okButton.clicked.connect(self.msgDialog.close)

        self.msgDialog.show()

    def onShowInExplorer(self, path):
        """Open the folder in explorer"""
        # TODO // Make it compatible with Linux
        os.startfile(os.path.normpath(path))
        pass

    def closeEvent(self, *args, **kwargs):
        """Override close behaviour"""
        self.terminated = True

    def terminate(self, all=False):
        """Terminate the progress"""
        self.terminated = True
        self.cancelAll = all

    def safeLog(self, msg):
        try:
            self.logger.debug(msg)
        except:
            pass

    def masterCopy(self, srcList, dst):
        # logName = "fileTransferLog_{0}.txt".format(now.strftime("%Y.%m.%d.%H.%M"))
        # logFile = os.path.join(logPath, logName)
        # self.logger = self.setupLogger(logFile)
        totalCount = len(srcList)
        current = 0
        copiedPathList = []
        for sel in srcList:
            if self.cancelAll:
                # self.safeLog("ALL CANCELED")
                break
            # self.logger.debug(
            #     "---------------------------------------------\n"
            #     "Copy Progress - {0}\n"
            #     "---------------------------------------------".format(
            #         sequenceData[sel]))
            percent = (100 * current) / totalCount
            self.pbOverall.setValue(percent)
            current += 1
            # tFilesList = [i.path for i in sequenceData[sel]]
            # subPath = os.path.split(os.path.relpath(tFilesList[0], root))[0]  ## get the relative path
            # currentDate = now.strftime("%y%m%d")
            # targetPath = os.path.join(destination, currentDate, subPath)

            if os.path.isdir(sel):
                # re-define dst starting from the folder name
                newDst = os.path.join(dst, os.path.basename(sel))
                # if not os.path.isdir(os.path.normpath(newDst)):
                #     os.makedirs(os.path.normpath(newDst))
                newDst = self.strip_accents(newDst)
                # if not os.path.isdir(os.path.normpath(newDst)):
                #     os.makedirs(os.path.normpath(newDst))

                copiedPathList.append(self.copyFolder(src=sel, dst=newDst))

            else:
                dst = self.strip_accents(dst)

                if not os.path.isdir(os.path.normpath(dst)):
                    os.makedirs(os.path.normpath(dst))

                copiedPathList.append(self.copyItem(src=sel, dst=dst))

        # self.deleteLogger(self.logger)

        self.close()
        if self.cancelAll:
            self.results_ui("Canceled by user", logPath=self.logPath, destPath=dst)
        elif self.errorFlag:
            self.results_ui("Finished with Error(s)", color="red", logPath=self.logPath, destPath=dst)
        else:
            self.results_ui("Success", logPath=self.logPath, destPath=dst)
        return copiedPathList

    def copyFolder(self, src, dst):

        # src = os.path.normpath(src.replace(" ", "_"))
        # dst = os.path.normpath(dst.replace(" ", "_"))
        dst = self.uniqueFolderName(os.path.normpath(dst.replace(" ", "_")))
        # print "defcon", dst
        if not os.path.isdir(dst):
            os.makedirs(dst)

        self.pb.setValue(0)
        self.terminated = False  # reset the termination status
        totalCount = self.countFiles(src)
        current = 0

        for path, dirs, filenames in os.walk(src):
            for directory in dirs:

                destDir = path.replace(src, dst)
                targetDir = os.path.join(destDir, directory)
                targetDir = self.strip_accents(targetDir)

                if not os.path.isdir(targetDir):
                    os.makedirs(targetDir)

            for sfile in filenames:
                srcFile = os.path.join(path, sfile)

                destFile = os.path.join(path.replace(src, dst), sfile)
                destFile = self.strip_accents(destFile)

                try:
                    shutil.copyfile(srcFile, destFile)

                except:
                    self.errorFlag = True
                    #     # self.safeLog("FAILED - unknown error")
                    return None
                percent = (100 * current) / totalCount
                self.pb.setValue(percent)
                current += 1
                QtWidgets.QApplication.processEvents()
                # self.safeLog("Success - {0}".format(targetPath))
                if self.terminated or self.cancelAll:
                    self.errorFlag = True
                    # self.safeLog("FAILED - skipped by user")
                    return None
                    # break

        return dst

    def copyItem(self, src, dst):
        src = os.path.normpath(src)
        dst = os.path.normpath(dst)

        self.pb.setValue(0)
        self.terminated = False  # reset the termination status
        totalCount = self.countFiles(src)
        current = 0

        try:
            fileLocation = self.uniqueFileName(os.path.join(dst, os.path.basename(src)))
            fileLocation = self.strip_accents(fileLocation)

            shutil.copyfile(src, fileLocation)
            return fileLocation
        except:
            self.errorFlag = True
            # self.safeLog("FAILED - unknown error")
            return None

    def uniqueFolderName(self, folderLocation):
        count = 0
        max_iter = 100
        while os.path.isdir(folderLocation) and count < max_iter:
            count += 1
            directory, baseName = os.path.split(folderLocation)
            niceName, ext = os.path.splitext(baseName)
            if niceName.endswith("_sm({0})".format(count - 1)):
                niceName = niceName.replace("_sm({0})".format(str(count - 1)), "_sm({0})".format(str(count)))
            else:
                niceName = "{0}_sm({1})".format(niceName, str(count))
            folderLocation = os.path.join(directory, "{0}{1}".format(niceName, ext))
        return folderLocation

    def uniqueFileName(self, fileLocation):
        count = 0
        max_iter = 100
        while os.path.isfile(fileLocation) and count < max_iter:
            count += 1
            directory, baseName = os.path.split(fileLocation)
            niceName, ext = os.path.splitext(baseName)
            if niceName.endswith("_sm({0})".format(count - 1)):
                niceName = niceName.replace("_sm({0})".format(str(count - 1)), "_sm({0})".format(str(count)))
            else:
                niceName = "{0}_sm({1})".format(niceName, str(count))
            fileLocation = os.path.join(directory, "{0}{1}".format(niceName, ext))
        return fileLocation

    def countFiles(self, directory):
        files = []

        if os.path.isdir(directory):
            for path, dirs, filenames in os.walk(directory):
                files.extend(filenames)
            return len(files)
        else:
            return 1

    # def copysequence(self, sequenceData, selectionList, destination, logPath, root):
    #     """
    #     Copies the sequences to the destination
    #     :param sequenceData: (List) list of sequences - Usually all found sequences
    #     :param selectionList: (List) Index list of selected sequences to iterate
    #     :param destination: (String) Absolute Path of remote destination
    #     :param logPath: (String) Absolute folder Path for log file
    #     :param root: (String) Root path of the images. Difference between sequence file folder
    #                     and root path will be used as the folder structure at remote location
    #     :return:
    #     """
    #     now = datetime.datetime.now()
    #     logName = "fileTransferLog_{0}.txt".format(now.strftime("%Y.%m.%d.%H.%M"))
    #     logFile = os.path.join(logPath, logName)
    #     self.logger = self.setupLogger(logFile)
    #     totalCount = len(selectionList)
    #     current = 0
    #     for sel in selectionList:
    #         if self.cancelAll:
    #             self.safeLog("ALL CANCELED")
    #             break
    #         self.logger.debug(
    #             "---------------------------------------------\n"
    #             "Copy Progress - {0}\n"
    #             "---------------------------------------------".format(
    #                 sequenceData[sel]))
    #         percent = (100 * current) / totalCount
    #         self.pbOverall.setValue(percent)
    #         current += 1
    #         tFilesList = [i.path for i in sequenceData[sel]]
    #         subPath = os.path.split(os.path.relpath(tFilesList[0], root))[0]  ## get the relative path
    #         currentDate = now.strftime("%y%m%d")
    #         targetPath = os.path.join(destination, currentDate, subPath)
    #         if not os.path.isdir(os.path.normpath(targetPath)):
    #             os.makedirs(os.path.normpath(targetPath))
    #         self.copyfileobj(src=tFilesList, dst=targetPath)
    #
    #     self.deleteLogger(self.logger)
    #
    #     self.close()
    #     if self.cancelAll:
    #         self.results_ui("Canceled by user", logPath=logFile, destPath=destination)
    #     elif self.errorFlag:
    #         self.results_ui("Check log file for errors", color="red", logPath=logFile, destPath=destination)
    #     else:
    #         self.results_ui("Transfer Successfull", logPath=logFile, destPath=destination)
    #     pass

    def setupLogger(self, handlerPath):
        """Prepares logger to write into log file"""
        logger = logging.getLogger('imageViewer')
        file_logger = logging.FileHandler(handlerPath)
        logger.addHandler(file_logger)
        logger.setLevel(logging.DEBUG)
        return logger

    def deleteLogger(self, logger):
        """Deletes the looger object once the logging into file finishes"""
        try:
            for i in logger.handlers:
                logger.removeHandler(i)
                i.flush()
                i.close()
        except:
            pass

    def strip_accents(self, s):
        """
        Sanitarize the given unicode string and remove all special/localized
        characters from it.

        Category "Mn" stands for Nonspacing_Mark
        """

        if type(s) == str:
            s = unicode(s, "utf-8")

        newNameList = []
        for c in unicodedata.normalize('NFKD', s):
            if unicodedata.category(c) != 'Mn':
                if c == u'ı':
                    newNameList.append(u'i')
                else:
                    newNameList.append(c)
        return ''.join(newNameList)
        # try:
        #     return ''.join(
        #         c for c in unicodedata.normalize('NFD', s)
        #         if unicodedata.category(c) != 'Mn'
        #     )
        # except:
        #     return s

class ProjectMaterials(RootManager, CoreFunctions):
    def __init__(self):
        super(ProjectMaterials, self).__init__()
        #
        self.swName = BoilerDict["Environment"]
        self.init_paths()
        self.init_database()

    def init_paths(self):
        """OVERRIDEN FUNCTION - Initializes necessary paths for project materials module"""
        # all paths in here must be absolute paths
        self._pathsDict["userSettingsDir"] = os.path.normpath(os.path.join(self.getUserDir(), "TikManager"))
        self._folderCheck(self._pathsDict["userSettingsDir"])
        self._pathsDict["userSettingsFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], "userSettings.json"))
        self._pathsDict["projectsFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], "smProjects.json"))

        self._pathsDict["commonFolderFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], "smCommonFolder.json"))
        self._pathsDict["sharedSettingsDir"] = self._getCommonFolder()
        if self._pathsDict["sharedSettingsDir"] == -1:
            self._exception(201, "Cannot Continue Without Common Database")
            return -1

        self._pathsDict["projectDir"] = self.getProjectDir()

        self._pathsDict["masterDir"] = os.path.normpath(os.path.join(self._pathsDict["projectDir"], "smDatabase"))
        if not os.path.isdir(self._pathsDict["masterDir"]):
            return False

        self._pathsDict["projectSettingsFile"] = os.path.normpath(os.path.join(self._pathsDict["masterDir"], "projectSettings.json"))


        self._pathsDict["databaseDir"] = os.path.normpath(os.path.join(self._pathsDict["masterDir"], "projectMaterialsDB"))


        self._pathsDict["subprojectsFile"] = os.path.normpath(os.path.join(self._pathsDict["masterDir"], "subPdata.json"))

        self._pathsDict["usersFile"] = os.path.normpath(
            os.path.join(self._pathsDict["sharedSettingsDir"], "sceneManagerUsers.json"))

        # self._pathsDict["iconsDir"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CSS", "rc")


        # project material specific
        self._pathsDict["Storyboard"] = os.path.join(self.projectDir, "_REF", "storyboard")
        self._pathsDict["Brief"] = os.path.join(self.projectDir, "_REF", "brief")
        self._pathsDict["Reference"] = os.path.join(self.projectDir, "_REF", "reference")
        self._pathsDict["Artwork"] = os.path.join(self.projectDir, "_REF", "artwork")
        self._pathsDict["Footage"] = os.path.join(self.projectDir, "sourceimages", "_FOOTAGE")
        self._pathsDict["Other"] = os.path.join(self.projectDir, "_REF", "other")

        return True

    def init_database(self):
        """OVERRIDEN FUNCTION - Initializes only necessary databases"""

        self._subProjectsList = self.loadSubprojects()

        # override _currentsDict (disconnected from  the json database)
        self._currentsDict = {"currentSubIndex": 0}  # default is 0 as "None"

        self.materialsInCategory = {}  # empty materials directory
        self.currentMaterialInfo = None

    @property
    def currentSubIndex(self):
        """OVERRIDEN FUNCTION - Returns the sub-project index at cursor position"""
        return self._currentsDict["currentSubIndex"]

    @currentSubIndex.setter
    def currentSubIndex(self, indexData):
        """Moves the cursor to the given sub-project index"""
        if not 0 <= indexData < len(self._subProjectsList):
            msg = "Sub Project index is out of range!"
            # raise Exception([101, msg])
            self._exception(101, msg)
            return

        # print indexData
        if indexData == self.currentSubIndex:
            self.cursorInfo()
            return
        # self._setCurrents("currentSubIndex", indexData)

        # change only the attribute, dont update currents database
        self._currentsDict["currentSubIndex"] = indexData

    def _loadMaterialInfo(self, path):
        """Loads material info from json file and holds it in the self.currentMaterialInfo"""
        self.currentMaterialInfo = self._loadJson(path)
        return self.currentMaterialInfo

    def getMaterialPath(self):
        """Returns the absolute material path of currentMaterialInfo"""
        return os.path.join(self.projectDir, self.currentMaterialInfo["relativePath"].replace("\\", "/"))

    def getFileContent(self):

        filePath = os.path.join(self.projectDir, self.currentMaterialInfo["relativePath"].replace("\\", "/"))
        validDocList = [".txt", ".rtf", ".doc", ".docx"]
        ext = os.path.splitext(filePath)[1]

        if ext not in validDocList:
            return ""
        with open(filePath, 'r') as doc:
            # Return a list of lines (strings)
            # data = theFile.read().split('\n')

            # Return as string without line breaks
            # data = theFile.read().replace('\n', '')

            # Return as string
            data = doc.read()
            return data


    def saveMaterial(self, pathList, materialType):
        subProject = "" if self.currentSubIndex == 0 else self.subProject
        copier = CopyProgress()
        dateDir = datetime.datetime.now().strftime("%y%m%d")
        # targetLocation = os.path.join(self._pathsDict[materialType], subProject, dateDir)
        targetLocation = os.path.join(self._pathsDict[materialType], subProject)
        # matDatabaseDir = os.path.join(self._pathsDict["databaseDir"], materialType, subProject, dateDir)
        matDatabaseDir = os.path.join(self._pathsDict["databaseDir"], materialType, subProject)
        self._folderCheck(matDatabaseDir)

        # copy the files and collect returned absolute paths in a list
        absPaths = copier.masterCopy(pathList, targetLocation)

        for item in absPaths:
            # build a dictionary
            baseName = os.path.basename(item)
            # niceName = os.path.splitext(baseName)[0]
            niceName = baseName
            relativePath = os.path.relpath(item, self._pathsDict["projectDir"])
            dictItem = {
                "niceName": niceName,
                "relativePath": relativePath,
                "materialType": materialType,
                "subProject": subProject,
                "entryDate": dateDir
            }
            matDatabaseFile = os.path.join(matDatabaseDir, "%s.json" % niceName)
            self._dumpJson(dictItem, matDatabaseFile)

    def deleteMaterial(self, dbPath):

        dbInfo = self._loadJson(dbPath)

        material_absPath = os.path.join(self._pathsDict["projectDir"], dbInfo["relativePath"])

        if os.path.isdir(material_absPath):
            os.rmdir(material_absPath)
        else:
            os.remove(material_absPath)

        os.remove(dbPath)
        return True

    def scanMaterials(self, materialType, sortBy="date"):
        # materialType = str(materialType)
        subProject = "" if self.currentSubIndex == 0 else self.subProject
        # matDatabaseDir = os.path.join(self._pathsDict["databaseDir"], materialType, subProject, dateDir)
        searchDir = os.path.join(self._pathsDict["databaseDir"], materialType, subProject)

        dbFiles = glob(os.path.join(searchDir, '*.json'))
        if sortBy == "date":
            dbFiles.sort(key=os.path.getmtime)
        elif sortBy == "size":
            dbFiles.sort(key=os.path.getsize)
        elif sortBy == "name":
            dbFiles.sort()
        self.materialsInCategory = {self.niceName(file): file for file in glob(os.path.join(searchDir, '*.json'))}
        return self.materialsInCategory

    def execute(self):
        if not self.currentMaterialInfo:
            msg = "No material selected"
            self._exception(360, msg)
            return

        path = os.path.join(self.projectDir, self.currentMaterialInfo["relativePath"])

        if self.currentPlatform == "Windows":
            os.startfile(path)
        elif self.currentPlatform == "Linux":
            os.system('nautilus %s' % path)
        else:
            msg = "%s is not supported" %self.currentPlatform
            self._exception(210, msg)
            return

    def cursorInfo(self):
        """OVERRIDEN - function to return cursor position info for debugging purposes"""
        pass




class MainUI(QtWidgets.QMainWindow):
    """Main UI function"""

    def __init__(self, projectPath=None, relativePath=None, recursive=False):
        for entry in QtWidgets.QApplication.allWidgets():
            try:
                if entry.objectName() == BoilerDict["Environment"]:
                    entry.close()
            except AttributeError:
                pass
        parent = getMainWindow()
        super(MainUI, self).__init__(parent=parent)

        # # Set Stylesheet
        dirname = os.path.dirname(os.path.abspath(__file__))
        stylesheetFile = os.path.join(dirname, "CSS", "tikManager.qss")

        with open(stylesheetFile, "r") as fh:
            self.setStyleSheet(fh.read())

        self.promat = ProjectMaterials()

        self.setObjectName(BoilerDict["Environment"])
        # self.resize(670, 624)
        self.setWindowTitle(BoilerDict["WindowTitle"])
        self.centralwidget = QtWidgets.QWidget(self)

        self.buildUI()

        self.setCentralWidget(self.centralwidget)

        self.initMainUI()
        self.show()

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.WindowStateChange:
            if self.windowState() & QtCore.Qt.WindowMaximized:
                self.stb_label.resize(1, 1)  ## 1, 1 is random, can be any number
                # event.ignore()
                # self.close()
                return

    def buildUI(self):

        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_6.setObjectName(("verticalLayout_6"))

        # ----------
        # HEADER BAR
        # ----------
        margin = 5
        colorWidget = QtWidgets.QWidget()
        colorWidget.setObjectName("header")
        headerLayout = QtWidgets.QHBoxLayout(colorWidget)
        headerLayout.setSpacing(0)
        try: headerLayout.setMargin(0)
        except AttributeError: pass

        tikIcon_label = QtWidgets.QLabel(self.centralwidget)
        tikIcon_label.setObjectName("header")
        tikIcon_label.setMaximumWidth(135)
        tikIcon_label.setMargin(margin)
        tikIcon_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        tikIcon_label.setScaledContents(False)

        headerBitmap = QtGui.QPixmap(":/icons/CSS/rc/tmProjectMaterials.png")
        tikIcon_label.setPixmap(headerBitmap)


        headerLayout.addWidget(tikIcon_label)


        resolvedPath_label = QtWidgets.QLabel()
        resolvedPath_label.setObjectName("header")
        try: resolvedPath_label.setMargin(margin)
        except AttributeError: pass
        resolvedPath_label.setIndent(2)

        resolvedPath_label.setFont(QtGui.QFont("Times", 7, QtGui.QFont.Bold))
        resolvedPath_label.setWordWrap(True)

        headerLayout.addWidget(resolvedPath_label)

        self.verticalLayout_6.addWidget(colorWidget)
        # ----------
        # ----------

        self.subP_HLayout = QtWidgets.QHBoxLayout()

        self.project_label = QtWidgets.QLabel(self.centralwidget)
        self.project_label.setText(("Project:"))
        self.project_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.project_label.setObjectName(("project_label"))


        self.project_lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.project_lineEdit.setText((""))
        self.project_lineEdit.setPlaceholderText((""))
        self.project_lineEdit.setObjectName(("project_lineEdit"))
        self.project_lineEdit.setReadOnly(True)



        self.subP_label = QtWidgets.QLabel()
        self.subP_label.setText("Sub-Project:")
        self.subP_label.setAlignment((QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
        self.subP_combobox = QtWidgets.QComboBox()
        self.subP_combobox.setMinimumWidth(150)

        self.subP_HLayout.addWidget(self.project_label)
        self.subP_HLayout.addWidget(self.project_lineEdit)
        self.subP_HLayout.addWidget(self.subP_label)
        self.subP_HLayout.addWidget(self.subP_combobox)
        self.verticalLayout_6.addLayout(self.subP_HLayout)



        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setToolTip((""))
        self.tabWidget.setStatusTip((""))

        # --------------
        # STORYBOARD TAB
        # --------------
        self.stb_tab = QtWidgets.QWidget()
        self.stb_tab.setToolTip((""))
        self.stb_tab.setStatusTip((""))
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.stb_tab)

        self.stb_label = QtImageViewer()
        self.stb_label.setMinimumSize(QtCore.QSize(10, 10))
        self.stb_label.setFrameShape(QtWidgets.QFrame.Box)
        self.stb_label.setAlignment(QtCore.Qt.AlignCenter)

        self.stb_label.canZoom = True
        self.stb_label.canPan = True

        self.left_layout = QtWidgets.QVBoxLayout()
        self.left_layout.setSpacing(0)
        self.left_layout.addWidget(self.stb_label)
        self.left_layout.setContentsMargins(0, 0, 0, 0)

        self.left_widget = QtWidgets.QFrame()
        self.left_widget.setContentsMargins(0, 0, 0, 0)
        self.left_widget.setLayout(self.left_layout)

        # SPLITTER RIGHT SIDE

        self.storyboard_treeWidget = QtWidgets.QTreeWidget(self.centralwidget)
        self.storyboard_treeWidget.setToolTip((""))
        self.storyboard_treeWidget.setStatusTip((""))
        self.storyboard_treeWidget.setSortingEnabled(True)
        header = QtWidgets.QTreeWidgetItem(["Name", "Date"])
        self.storyboard_treeWidget.setHeaderItem(header)

        self.right_layout = QtWidgets.QVBoxLayout()
        self.right_layout.addWidget(self.storyboard_treeWidget)
        self.right_layout.setContentsMargins(0, 0, 0, 0)

        self.right_widget = QtWidgets.QFrame()
        self.right_widget.setLayout(self.right_layout)
        self.right_widget.setContentsMargins(0, 0, 0, 0)


        self.splitter = QtWidgets.QSplitter(parent=self.tabWidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setHandleWidth(8)
        self.splitter.addWidget(self.left_widget)
        self.splitter.addWidget(self.right_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        self.splitter.setSizePolicy(sizePolicy)

        self.splitter.setStretchFactor(0, 1)

        self.verticalLayout_5.addWidget(self.splitter)

        self.addStb_pushButton = DropPushButton(self.stb_tab)
        self.addStb_pushButton.setMinimumSize(QtCore.QSize(0, 40))
        self.addStb_pushButton.setToolTip(("Click to select file or drop the file(s) here"))
        self.addStb_pushButton.setStatusTip((""))
        self.addStb_pushButton.setText(("Add New Storyboard"))
        self.addStb_pushButton.setStyleSheet(ColorStyleDict["Storyboard"])
        self.verticalLayout_5.addWidget(self.addStb_pushButton)
        self.tabWidget.addTab(self.stb_tab, ("Storyboard"))

        # ---------
        # BRIEF TAB
        # ---------
        self.brief_tab = QtWidgets.QWidget()
        self.brief_tab.setToolTip((""))
        self.brief_tab.setStatusTip((""))
        self.brief_tab.setObjectName(("brief_tab"))

        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.brief_tab)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()

        self.brief_textEdit = QtWidgets.QTextEdit(self.brief_tab)
        self.brief_textEdit.setToolTip((""))
        self.brief_textEdit.setStatusTip((""))
        self.brief_textEdit.setReadOnly(True)
        self.horizontalLayout_2.addWidget(self.brief_textEdit)

        self.brief_treeWidget = QtWidgets.QTreeWidget(self.brief_tab)
        self.brief_treeWidget.setSortingEnabled(True)
        header = QtWidgets.QTreeWidgetItem(["Name", "Date"])
        self.brief_treeWidget.setHeaderItem(header)
        self.brief_treeWidget.sortItems(1, QtCore.Qt.AscendingOrder)  # 1 is Date Column, 0 is Ascending order

        self.horizontalLayout_2.addWidget(self.brief_treeWidget)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)

        self.addBrief_pushButton = DropPushButton(self.brief_tab)
        self.addBrief_pushButton.setMinimumSize(QtCore.QSize(0, 40))
        self.addBrief_pushButton.setText(("Add New Document"))
        self.addBrief_pushButton.setStyleSheet(ColorStyleDict["Brief"])

        self.verticalLayout_4.addWidget(self.addBrief_pushButton)
        self.tabWidget.addTab(self.brief_tab, ("Brief"))

        # -----------
        # REFERENCE TAB
        # -----------
        self.reference_tab = QtWidgets.QWidget()
        self.reference_tab.setToolTip((""))
        self.reference_tab.setStatusTip((""))
        self.reference_verticalLayout = QtWidgets.QVBoxLayout(self.reference_tab)

        self.reference_label = QtImageViewer()
        self.reference_label.setMinimumSize(QtCore.QSize(10, 10))
        self.reference_label.setFrameShape(QtWidgets.QFrame.Box)
        self.reference_label.setAlignment(QtCore.Qt.AlignCenter)

        self.leftR_layout = QtWidgets.QVBoxLayout()
        self.leftR_layout.setSpacing(0)
        self.leftR_layout.addWidget(self.reference_label)
        self.leftR_layout.setContentsMargins(0, 0, 0, 0)

        self.leftR_widget = QtWidgets.QFrame()
        self.leftR_widget.setContentsMargins(0, 0, 0, 0)
        self.leftR_widget.setLayout(self.leftR_layout)

        # SPLITTER RIGHT SIDE

        self.reference_treeWidget = QtWidgets.QTreeWidget(self.centralwidget)
        self.reference_treeWidget.setToolTip((""))
        self.reference_treeWidget.setStatusTip((""))
        self.reference_treeWidget.setSortingEnabled(True)
        header = QtWidgets.QTreeWidgetItem(["Name", "Date"])
        self.reference_treeWidget.setHeaderItem(header)

        self.rightR_layout = QtWidgets.QVBoxLayout()
        self.rightR_layout.addWidget(self.reference_treeWidget)
        self.rightR_layout.setContentsMargins(0, 0, 0, 0)

        self.rightR_widget = QtWidgets.QFrame()
        self.rightR_widget.setLayout(self.rightR_layout)
        self.rightR_widget.setContentsMargins(0, 0, 0, 0)


        self.splitterRef = QtWidgets.QSplitter(parent=self.tabWidget)
        self.splitterRef.setOrientation(QtCore.Qt.Horizontal)
        self.splitterRef.setHandleWidth(8)
        self.splitterRef.addWidget(self.leftR_widget)
        self.splitterRef.addWidget(self.rightR_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        self.splitterRef.setSizePolicy(sizePolicy)

        self.splitterRef.setStretchFactor(0, 1)

        self.reference_verticalLayout.addWidget(self.splitterRef)

        self.addReference_pushButton = DropPushButton(self.stb_tab)
        self.addReference_pushButton.setMinimumSize(QtCore.QSize(0, 40))
        self.addReference_pushButton.setToolTip(("Click to select file or drop the file(s) here"))
        self.addReference_pushButton.setStatusTip((""))
        self.addReference_pushButton.setText(("Add New Reference"))
        self.addReference_pushButton.setStyleSheet(ColorStyleDict["Reference"])
        self.reference_verticalLayout.addWidget(self.addReference_pushButton)
        self.tabWidget.addTab(self.reference_tab, ("Reference"))

        # -----------------------------------------

        # -----------
        # ARTWORK TAB
        # -----------
        self.artwork_tab = QtWidgets.QWidget()
        self.artwork_tab.setToolTip((""))
        self.artwork_tab.setStatusTip((""))
        self.artwork_tab.setWhatsThis((""))
        self.artwork_tab.setAccessibleName((""))
        self.artwork_tab.setAccessibleDescription((""))
        self.artwork_tab.setObjectName(("artwork_tab"))

        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.artwork_tab)
        self.verticalLayout_3.setObjectName(("verticalLayout_3"))

        self.artwork_treeWidget = QtWidgets.QTreeWidget(self.artwork_tab)
        self.artwork_treeWidget.setToolTip((""))
        self.artwork_treeWidget.setStatusTip((""))

        self.artwork_treeWidget.setSortingEnabled(True)
        header = QtWidgets.QTreeWidgetItem(["Name", "Date"])
        self.artwork_treeWidget.setHeaderItem(header)
        self.artwork_treeWidget.sortItems(1, QtCore.Qt.AscendingOrder)  # 1 is Date Column, 0 is Ascending order

        self.verticalLayout_3.addWidget(self.artwork_treeWidget)

        self.addArtwork_pushButton = DropPushButton(self.artwork_tab)
        self.addArtwork_pushButton.setMinimumSize(QtCore.QSize(0, 40))
        self.addArtwork_pushButton.setToolTip((""))
        self.addArtwork_pushButton.setStatusTip((""))
        self.addArtwork_pushButton.setText(("Add New Artwork (Folder)"))
        self.addArtwork_pushButton.setStyleSheet(ColorStyleDict["Artwork"])

        self.verticalLayout_3.addWidget(self.addArtwork_pushButton)
        self.tabWidget.addTab(self.artwork_tab, ("Artwork"))

        # -----------
        # FOOTAGE TAB
        # -----------
        self.footage_tab = QtWidgets.QWidget()
        self.footage_tab.setToolTip((""))
        self.footage_tab.setStatusTip((""))

        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.footage_tab)

        self.footage_treeWidget = QtWidgets.QTreeWidget(self.footage_tab)
        self.footage_treeWidget.setToolTip((""))
        self.footage_treeWidget.setStatusTip((""))
        self.footage_treeWidget.setSortingEnabled(True)
        header = QtWidgets.QTreeWidgetItem(["Name", "Date"])
        self.footage_treeWidget.setHeaderItem(header)
        self.footage_treeWidget.sortItems(1, QtCore.Qt.AscendingOrder)  # 1 is Date Column, 0 is Ascending order

        self.verticalLayout_2.addWidget(self.footage_treeWidget)

        self.addFootage_pushButton = DropPushButton(self.footage_tab)
        self.addFootage_pushButton.setMinimumSize(QtCore.QSize(0, 40))
        self.addFootage_pushButton.setToolTip((""))
        self.addFootage_pushButton.setStatusTip((""))
        self.addFootage_pushButton.setText(("Add New Footage"))
        self.addFootage_pushButton.setStyleSheet(ColorStyleDict["Footage"])

        self.verticalLayout_2.addWidget(self.addFootage_pushButton)
        self.tabWidget.addTab(self.footage_tab, ("Footage"))

        # ---------
        # OTHER TAB
        # ---------
        self.other_tab = QtWidgets.QWidget()
        self.other_tab.setToolTip((""))
        self.other_tab.setStatusTip((""))

        self.verticalLayout = QtWidgets.QVBoxLayout(self.other_tab)

        self.other_treeWidget = QtWidgets.QTreeWidget(self.other_tab)
        self.other_treeWidget.setToolTip((""))
        self.other_treeWidget.setStatusTip((""))
        self.other_treeWidget.setSortingEnabled(True)
        header = QtWidgets.QTreeWidgetItem(["Name", "Date"])
        self.other_treeWidget.setHeaderItem(header)
        self.other_treeWidget.sortItems(1, QtCore.Qt.AscendingOrder)  # 1 is Date Column, 0 is Ascending order

        self.verticalLayout.addWidget(self.other_treeWidget)

        self.addOther_pushButton = DropPushButton(self.other_tab)
        self.addOther_pushButton.setMinimumSize(QtCore.QSize(0, 40))
        self.addOther_pushButton.setToolTip((""))
        self.addOther_pushButton.setStatusTip((""))
        self.addOther_pushButton.setText(("Add New Footage"))
        self.addOther_pushButton.setStyleSheet(ColorStyleDict["Other"])

        self.verticalLayout.addWidget(self.addOther_pushButton)
        self.tabWidget.addTab(self.other_tab, ("Other"))

        self.verticalLayout_6.addWidget(self.tabWidget)

        self.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 715, 21))
        self.menubar.setToolTip((""))
        self.menubar.setStatusTip((""))
        self.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setToolTip((""))
        self.statusbar.setStatusTip((""))
        self.setStatusBar(self.statusbar)

        self.tabWidget.setCurrentIndex(0)

        # ----------------
        # RIGHT CLICK MENU
        # ----------------

        # SEQUENCE RC
        # -----------
        tabTrees = [self.storyboard_treeWidget, self.brief_treeWidget, self.reference_treeWidget, self.artwork_treeWidget, self.footage_treeWidget, self.other_treeWidget]

        self.popMenu = QtWidgets.QMenu()
        rcA = QtWidgets.QAction('Show in Explorer', self)
        rcB = QtWidgets.QAction('Delete Item', self)
        for tree in tabTrees:
            tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            self.popMenu.addAction(rcB)
            self.popMenu.addAction(rcA)

        rcA.triggered.connect(lambda: self.onRightClick("showInExplorer"))
        rcB.triggered.connect(lambda: self.onRightClick("deleteItem"))

        #
        self.storyboard_treeWidget.customContextMenuRequested.connect(lambda x: self.onContextMenu(x, self.storyboard_treeWidget))
        self.brief_treeWidget.customContextMenuRequested.connect(lambda x: self.onContextMenu(x, self.brief_treeWidget))
        self.reference_treeWidget.customContextMenuRequested.connect(lambda x: self.onContextMenu(x, self.reference_treeWidget))
        self.artwork_treeWidget.customContextMenuRequested.connect(lambda x: self.onContextMenu(x, self.artwork_treeWidget))
        self.footage_treeWidget.customContextMenuRequested.connect(lambda x: self.onContextMenu(x, self.footage_treeWidget))
        self.other_treeWidget.customContextMenuRequested.connect(lambda x: self.onContextMenu(x, self.other_treeWidget))


        # ------------------
        # SIGNAL CONNECTIONS
        # ------------------
        # rcAction_0.triggered.connect(lambda: self.onShowInExplorer())


        self.subP_combobox.activated.connect(self.initSubProjects)

        for tree in tabTrees:
            tree.currentItemChanged.connect(self.onChangeItem)


        self.addStb_pushButton.dropped.connect(lambda path: self.droppedPath(path, "Storyboard"))
        self.addBrief_pushButton.dropped.connect(lambda path: self.droppedPath(path, "Brief"))
        self.addReference_pushButton.dropped.connect(lambda path: self.droppedPath(path, "Reference"))
        self.addFootage_pushButton.dropped.connect(lambda path: self.droppedPath(path, "Footage"))
        self.addArtwork_pushButton.dropped.connect(lambda path: self.droppedPath(path, "Artwork"))
        self.addOther_pushButton.dropped.connect(lambda path: self.droppedPath(path, "Other"))

        self.addStb_pushButton.clicked.connect(lambda: self.onButtonPush("Storyboard"))
        self.addBrief_pushButton.clicked.connect(lambda: self.onButtonPush("Brief"))
        self.addReference_pushButton.clicked.connect(lambda: self.onButtonPush("Reference"))
        self.addFootage_pushButton.clicked.connect(lambda: self.onButtonPush("Footage"))
        self.addArtwork_pushButton.clicked.connect(lambda: self.onButtonPush("Artwork"))
        self.addOther_pushButton.clicked.connect(lambda: self.onButtonPush("Other"))

        self.storyboard_treeWidget.doubleClicked.connect(self.promat.execute)
        self.brief_treeWidget.doubleClicked.connect(self.promat.execute)
        self.reference_treeWidget.doubleClicked.connect(self.promat.execute)
        self.artwork_treeWidget.doubleClicked.connect(self.promat.execute)
        self.footage_treeWidget.doubleClicked.connect(self.promat.execute)
        self.other_treeWidget.doubleClicked.connect(self.promat.execute)

        self.tabWidget.currentChanged.connect(self.initCategoryItems)

    def onContextMenu(self, point, treeWidget):
        """Method to pop the menu at the position of the mouse cursor"""
        # print se
        if treeWidget.currentItem():
            self.popMenu.exec_(treeWidget.mapToGlobal(point))

    def initMainUI(self):
        """Inits the ui elements with the information from  logic class"""

        # Initalization Hierarchy:

        # InitMainUI -> triggered by initial execution
        # InitSubProjects -> triggered by self.subP_combobox.activated signal
        # Init Material Category Items -> triggered by self.tabWidget.currentChanged signal and drop action/new material by file
        # Display info for selected item -> triggered by self.storyboard_treeWidget.currentItemChanged and self.brief_treeWidget.currentItemChanged signals

        # update current project line
        self.project_lineEdit.setText(self.promat.projectDir)
        # update sub-projects
        self.subP_combobox.addItems(self.promat.getSubProjects())
        self.subP_combobox.setCurrentIndex(0)
        self.initSubProjects()
        self.statusBar().showMessage("Status | Idle")

    def initSubProjects(self):
        self.statusBar().showMessage("Status | Idle")
        self.promat.currentSubIndex = self.subP_combobox.currentIndex()
        self.initCategoryItems()

    def initCategoryItems(self):
        self.statusBar().showMessage("Status | Idle")

        self.matCategory = self.tabWidget.tabText(self.tabWidget.currentIndex())

        materials = self.promat.scanMaterials(str(self.matCategory))

        # get the right widget
        if self.matCategory == "Storyboard":
            treewidget = self.storyboard_treeWidget
        elif self.matCategory == "Brief":
            treewidget = self.brief_treeWidget
        elif self.matCategory == "Reference":
            treewidget = self.reference_treeWidget
        elif self.matCategory == "Artwork":
            treewidget = self.artwork_treeWidget
        elif self.matCategory == "Footage":
            treewidget = self.footage_treeWidget
        elif self.matCategory == "Other":
            treewidget = self.other_treeWidget
        else:
            print("cannot get category")
            return

        treewidget.clear()
        for x in materials.items():
            timestamp = os.path.getmtime(x[1])
            timestampFormatted = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
            item = QtWidgets.QTreeWidgetItem(treewidget, [x[0], str(timestampFormatted)])
        # sort by date default
        treewidget.sortItems(1, QtCore.Qt.AscendingOrder)  # 1 is Date Column, 0 is Ascending order

    def onChangeItem(self, item):
        self.statusBar().showMessage("Status | Idle")
        # print item
        if not item:
            return

        try:
            self.matDBpath = self.promat.materialsInCategory[str(item.text(0))]
        except KeyError:
            return

        self.promat._loadMaterialInfo(self.matDBpath)

        if self.matCategory == "Storyboard":
            # print item
            pic = os.path.normpath(self.promat.getMaterialPath())
            # update thumb
            self.tPixmap = QtGui.QPixmap(pic)


            self.stb_label.setImage(self.tPixmap)

        elif self.matCategory == "Brief":
            docContent = self.promat.getFileContent()
            self.brief_textEdit.setPlainText(docContent)

        elif self.matCategory == "Reference":
            # print item
            self.promat._loadMaterialInfo(self.matDBpath)
            pic = self.promat.getMaterialPath()
            # update thumb

            self.tPixmap = QtGui.QPixmap(pic)

            self.reference_label.setImage(self.tPixmap)
        else:
            return

    def onRightClick(self, cmd):

        if cmd == "showInExplorer":
            pathDir = os.path.dirname(self.promat.getMaterialPath())
            self.promat.showInExplorer(pathDir)

        if cmd == "deleteItem":
            title = "Are you Sure?"
            header = "The selected item and its database will be deleted if you continue"
            msg = "Choose OK to confirm"

            q = QtWidgets.QMessageBox(parent=self)
            q.setIcon(QtWidgets.QMessageBox.Question)
            q.setWindowTitle(title)
            q.setInformativeText(header)
            q.setText(msg)
            q.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            q.button(QtWidgets.QMessageBox.Ok).setFixedHeight(30)
            q.button(QtWidgets.QMessageBox.Ok).setFixedWidth(100)
            q.button(QtWidgets.QMessageBox.Cancel).setFixedHeight(30)
            q.button(QtWidgets.QMessageBox.Cancel).setFixedWidth(100)
            ret = q.exec_()
            if ret == QtWidgets.QMessageBox.Ok:
                # print("HedeHot")
                # print(self.matDBpath)
                self.promat.deleteMaterial(self.matDBpath)
                self.initCategoryItems()
            elif ret == QtWidgets.QMessageBox.Cancel:
                return

    def droppedPath(self, paths, material):
        self.statusBar().showMessage("Status | Idle")
        paths = [os.path.normpath(unicode(path)) for path in paths if path != u'']
        if len(paths) == 0:
            self.statusBar().showMessage("Warning | There is no file path in dropped item")
            return

        self.promat.saveMaterial(paths, material)
        self.initCategoryItems()
        self.statusBar().showMessage("Success | Item(s) added")

    def onButtonPush(self, material):
        self.statusBar().showMessage("Status | Idle")
        selDialog = QFileAndFolderDialog()
        selDialog.setLabelText(selDialog.Accept, "Choose")
        x = selDialog.exec_()

        paths = selDialog.filesSelected()

        # len(paths) throws an error is the dialog canceled without selecting an item.
        # this is a workaround for skipping the save material procedure when the gui closed
        try:
            len(paths)
            self.promat.saveMaterial(paths, material)
            self.initCategoryItems()
            self.statusBar().showMessage("Success | Item(s) added")
        except:
            pass



class DropPushButton(QtWidgets.QPushButton):
    """Custom LineEdit Class accepting drops"""
    # PyInstaller and Standalone version compatibility
    if FORCE_QT5:
        dropped = QtCore.pyqtSignal(list)
    else:
        dropped = Qt.QtCore.Signal(list)

    def __init__(self, type, parent=None):
        super(DropPushButton, self).__init__(parent)
        self.oldText = ""
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        # if event.mimeData().hasFormat('text/uri-list'):
        if event.mimeData().hasUrls():
            event.accept()
            self.oldText = (self.text())
            self.setText("Drop to add")
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setText(self.oldText)

    def dragMoveEvent(self, event):
        # if event.mimeData().hasFormat('text/uri-list'):

        if event.mimeData().hasUrls:

            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):

        links = []

        for url in event.mimeData().urls():
            # print "g", unicode(str(url), "utf-8")
            # print "str", url.toString()
            # print "str", url.toLocalFile()
            # links.append(str(url.toLocalFile()))

            links.append((url.toLocalFile()))
        self.dropped.emit(links)

        # self.addItem(path)


    # def dragEnterEvent(self, event):
    #     if event.mimeData().hasFormat('text/uri-list'):
    #         event.accept()
    #     else:
    #         event.ignore()
    #
    # def dragMoveEvent(self, event):
    #     if event.mimeData().hasFormat('text/uri-list'):
    #         event.setDropAction(QtCore.Qt.CopyAction)
    #         event.accept()
    #     else:
    #         event.ignore()

    # def dropEvent(self, event):
    #     rawPath = event.mimeData().data('text/uri-list').__str__()
    #     print "rawPath", rawPath
    #     path = rawPath.replace("file:///", "").splitlines()[0]
    #     self.dropped.emit(path)


if __name__ == '__main__':
    os.environ["FORCE_QT5"] = "1"
    app = QtWidgets.QApplication(sys.argv)
    selfLoc = os.path.dirname(os.path.abspath(__file__))
    stylesheetFile = os.path.join(selfLoc, "CSS", "tikManager.qss")

    with open(stylesheetFile, "r") as fh:
        app.setStyleSheet(fh.read())
    window = MainUI()
    window.show()
    #
    # window = MainUI(projectPath= os.path.normpath("E:\\SceneManager_Projects\\SceneManager_DemoProject_None_181101"))
    # window.show()
    sys.exit(app.exec_())
