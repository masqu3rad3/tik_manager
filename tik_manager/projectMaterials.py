# Module to view and organize project materials


import os
import sys
from glob import glob

import _version

FORCE_QT4 = bool(os.getenv("FORCE_QT4"))

# Enabele FORCE_QT4 for compiling with pyinstaller
# FORCE_QT4 = False

if FORCE_QT4:
    from PyQt4 import QtCore, Qt
    from PyQt4 import QtGui as QtWidgets
else:
    import Qt
    from Qt import QtWidgets, QtCore, QtGui

from SmRoot import RootManager

import pyseq as seq

import json
import datetime
# from shutil import copyfile
import shutil
import logging

__author__ = "Arda Kutlu"
__copyright__ = "Copyright 2018, Scene Manager - Project materials"
__credits__ = []
__license__ = "GPL"
__maintainer__ = "Arda Kutlu"
__email__ = "ardakutlu@gmail.com"
__status__ = "Development"

BoilerDict = {"Environment":"Standalone",
              "MainWindow":None,
              "WindowTitle":"Project Materials - Standalone v%s" %_version.__version__,
              "Stylesheet": "mayaDark.stylesheet"}

# ---------------
# GET ENVIRONMENT
# ---------------
try:
    from maya import OpenMayaUI as omui
    import maya.cmds as cmds
    BoilerDict["Environment"] = "Maya"
    BoilerDict["WindowTitle"] = "Image Viewer Maya v%s" %_version.__version__
    if Qt.__binding__ == "PySide":
        from shiboken import wrapInstance
    elif Qt.__binding__.startswith('PyQt'):
        from sip import wrapinstance as wrapInstance
    else:
        from shiboken2 import wrapInstance
except ImportError:
    pass

try:
    import MaxPlus
    BoilerDict["Environment"] = "3dsMax"
    BoilerDict["WindowTitle"] = "Scene Manager 3ds Max v%s" %_version.__version__
except ImportError:
    pass

try:
    import hou
    BoilerDict["Environment"] = "Houdini"
    BoilerDict["WindowTitle"] = "Scene Manager Houdini v%s" %_version.__version__
except ImportError:
    pass

try:
    import nuke
    BoilerDict["Environment"] = "Nuke"
    BoilerDict["WindowTitle"] = "Scene Manager Nuke v%s" % _version.__version__
except ImportError:
    pass

def getMainWindow():
    """This function should be overriden"""
    if BoilerDict["Environment"] == "Maya":
        win = omui.MQtUtil_mainWindow()
        ptr = wrapInstance(long(win), QtWidgets.QMainWindow)
        return ptr

    elif BoilerDict["Environment"] == "3dsMax":
        return MaxPlus.GetQMaxWindow()

    elif BoilerDict["Environment"] == "Houdini":
        return hou.qt.mainWindow()

    elif BoilerDict["Environment"] == "Nuke":
        # TODO // Needs a main window getter for nuke
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
    leftMouseButtonPressed = QtCore.pyqtSignal(float, float)
    rightMouseButtonPressed = QtCore.pyqtSignal(float, float)
    leftMouseButtonReleased = QtCore.pyqtSignal(float, float)
    rightMouseButtonReleased = QtCore.pyqtSignal(float, float)
    leftMouseButtonDoubleClicked = QtCore.pyqtSignal(float, float)
    rightMouseButtonDoubleClicked = QtCore.pyqtSignal(float, float)

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
        if type(image) is QtWidgets.QPixmap:
            pixmap = image
        elif type(image) is QtWidgets.QImage:
            pixmap = QtWidgets.QPixmap.fromImage(image)
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
        elif event.button() == Qt.RightButton:
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
                self.scene.setSelectionArea(QtWidgets.QPainterPath())  # Clear current selection area.
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

# class QtImageViewer(QtWidgets.QLabel):
#     """Custom class for thumbnail section. Keeps the aspect ratio when resized."""
#     def __init__(self, parent=None):
#         super(QtImageViewer, self).__init__(parent)
#         self.aspectRatio = 1.78
#         sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
#         sizePolicy.setHeightForWidth(True)
#         self.setSizePolicy(sizePolicy)
#
#     def resizeEvent(self, r):
#         # print r
#         x = r.oldSize()
#         w = x.width()
#         h = x.height()
#         # print r.size()
#
#         # h = self.width()
#         # self.setFixedHeight(h/self.aspectRatio)
#         # self.set(self.width(), self.width()/self.aspectRatio)
#         self.setMinimumHeight(w/self.aspectRatio)
#
#         self.setMaximumHeight(w/self.aspectRatio)
#         # self.heightForWidth(h/self.aspectRatio)
#         # self.setBaseSize(50, 50)
#         # self.set


class CopyProgress(QtWidgets.QWidget):
    """Custom Widget for visualizing progress of file transfer"""
    def __init__(self, logPath = None):
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

    def results_ui(self, status, color="white", logPath=None, destPath = None):

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


                copiedPathList.append(self.copyFolder(src=sel, dst=newDst))

            else:
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

        src = os.path.normpath(src.replace(" ", "_"))
        # dst = os.path.normpath(dst.replace(" ", "_"))
        dst = self.uniqueFolderName(os.path.normpath(dst.replace(" ", "_")))

        self.pb.setValue(0)
        self.terminated = False # reset the termination status
        totalCount = self.countFiles(src)
        current = 0

        for path, dirs, filenames in os.walk(src):
            for directory in dirs:
                destDir = path.replace(src, dst)
                targetDir = os.path.join(destDir, directory)
                if not os.path.isdir(targetDir):
                    os.makedirs(targetDir)

            for sfile in filenames:
                srcFile = os.path.join(path, sfile)

                destFile = os.path.join(path.replace(src, dst), sfile)
                # shutil.copy(srcFile, destFile)
                try:
                    shutil.copy(srcFile, destFile)
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
        self.terminated = False # reset the termination status
        totalCount = self.countFiles(src)
        current = 0

        try:
            fileLocation = self.uniqueFileName(os.path.join(dst, os.path.basename(src)))

            shutil.copyfile(src, fileLocation)
            return fileLocation
        except:
            self.errorFlag = True
            # self.safeLog("FAILED - unknown error")
            return None

    def uniqueFolderName(self, folderLocation):
        count=0
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
        count=0
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


class ProjectMaterials(RootManager):
    def __init__(self):
        super(ProjectMaterials, self).__init__()
        #
        # self.init_paths()
        # self.init_database()


    def init_paths(self):
        """OVERRIDEN FUNCTION - Initializes necessary paths for project materials module"""
        # all paths in here must be absolute paths

        self._pathsDict["projectDir"] = self.getProjectDir()

        self._pathsDict["masterDir"] = os.path.normpath(os.path.join(self._pathsDict["projectDir"], "smDatabase"))
        if not os.path.isdir(self._pathsDict["masterDir"]):
            return False

        self._pathsDict["projectSettingsFile"] = os.path.normpath(os.path.join(self._pathsDict["masterDir"], "projectSettings.json"))

        self._pathsDict["databaseDir"] = os.path.normpath(os.path.join(self._pathsDict["masterDir"], "projectMaterialsDB"))


        self._pathsDict["subprojectsFile"] = os.path.normpath(os.path.join(self._pathsDict["masterDir"], "subPdata.json"))

        self._pathsDict["generalSettingsDir"] = os.path.dirname(os.path.abspath(__file__))
        self._pathsDict["usersFile"] = os.path.normpath(os.path.join(self._pathsDict["generalSettingsDir"], "sceneManagerUsers.json"))

        #project material specific
        self._pathsDict["storyboard"] = os.path.join(self.projectDir, "_REF", "storyboard")
        self._pathsDict["brief"] = os.path.join(self.projectDir, "_REF", "brief")
        self._pathsDict["artwork"] = os.path.join(self.projectDir, "_REF", "artwork")
        self._pathsDict["footage"] = os.path.join(self.projectDir, "sourceimages", "_FOOTAGE")
        self._pathsDict["other"] = os.path.join(self.projectDir, "_REF", "other")

        return True

    def init_database(self):
        """OVERRIDEN FUNCTION - Initializes only necessary databases"""

        self._subProjectsList = self._loadSubprojects()

        # override _currentsDict (disconnected from  the json database)
        self._currentsDict ={"currentSubIndex":0} # default is 0 as "None"

        self.materialsInCategory={} # empty materials directory
        self.currentMaterialInfo = None



    @property
    def currentSubIndex(self):
        """OVERRIDEN FUNCTION - Returns the sub-project index at cursor position"""
        return self._currentsDict["currentSubIndex"]

    @currentSubIndex.setter
    def currentSubIndex(self, indexData):
        """Moves the cursor to the given sub-project index"""
        if not 0 <= indexData < len(self._subProjectsList):
            msg="Sub Project index is out of range!"
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
        return os.path.join(self.projectDir, self.currentMaterialInfo["relativePath"])


    def getProjectDir(self):
        """OVERRIDEN FUNCTION Returns the project folder according to the environment"""
        # if BoilerDict["Environment"] == "Maya":
        #     return os.path.normpath(cmds.workspace(q=1, rd=1))
        # elif BoilerDict["Environment"] == "3dsMax":
        #     return os.path.normpath(MaxPlus.PathManager.GetProjectFolderDir())
        # elif BoilerDict["Environment"] == "Houdini":
        #     return os.path.normpath((hou.hscript('echo $JOB')[0])[:-1])  # [:-1] is for the extra \n
        # elif BoilerDict["Environment"] == "Nuke":
        #     # TODO // Needs a project getter for nuke
        #     return os.path.normpath(os.path.join(os.path.expanduser("~")))
        # else:
        #     return os.path.normpath(os.path.join(os.path.expanduser("~")))

        # ---------
        # TEMPORARY
        # ---------

        tempPath = os.path.normpath("E:\\SceneManager_Projects\\SceneManager_DemoProject_None_181101")
        # tempPath = os.path.normpath("D:\\PROJECT_AND_ARGE\\V3Test_V3Test_V3Test_181106")
        return tempPath



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
            niceName = os.path.splitext(baseName)[0]
            relativePath = os.path.relpath(item, self._pathsDict["projectDir"])
            dictItem = {
                "niceName": niceName,
                "relativePath": relativePath,
                "materialType": materialType,
                "subProject": subProject,
                "entryDate": dateDir
                        }
            matDatabaseFile = os.path.join(matDatabaseDir, "%s.json" %niceName)
            self._dumpJson(dictItem, matDatabaseFile)

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
        self.materialsInCategory = {self._niceName(file): file for file in glob(os.path.join(searchDir, '*.json'))}
        return self.materialsInCategory



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
        # super(MainUI, self).__init__()

        # Set Stylesheet
        # dirname = os.path.dirname(os.path.abspath(__file__))
        # # stylesheetFile = os.path.join(dirname, "CSS", "darkorange.stylesheet")
        # stylesheetFile = os.path.join(dirname, "CSS", BoilerDict["Stylesheet"])

        # with open(stylesheetFile, "r") as fh:
        #     self.setStyleSheet(fh.read())

        # matCategories = ["Storyboard", "Brief", "Artwork", "Footage", "Other"]

        self.promat = ProjectMaterials()

        pStatus = self.promat.init_paths()
        if not pStatus:
            msg=["Nothing to view", "No Scene Manager Database",
                 "There is no Scene Manager Database Folder in this project path"]
            q = QtWidgets.QMessageBox()
            q.setIcon(QtWidgets.QMessageBox.Information)
            q.setText(msg[0])
            q.setInformativeText(msg[1])
            q.setWindowTitle(msg[2])
            q.setStandardButtons(QtWidgets.QMessageBox.Ok)
            ret = q.exec_()
            if ret == QtWidgets.QMessageBox.Ok:
                self.close()
                self.deleteLater()

        self.promat.init_database()

        # if projectPath:
        #     self.projectPath=str(projectPath)
        # else:
        #     self.projectPath = self.promat.getProjectDir()
        #
        # if relativePath:
        #     self.rootPath = os.path.join(self.projectPath, str(relativePath))
        # else:
        #     self.rootPath = os.path.join(self.projectPath, "images")
        #     if not os.path.isdir(self.rootPath):
        #         self.rootPath = self.projectPath

        # if not self.promat.checkDatabase():


        # self.databaseDir = os.path.normpath(os.path.join(self.projectPath, "smDatabase"))
        #
        # if not os.path.isdir(self.databaseDir):
        #     msg=["Nothing to view", "No Scene Manager Database",
        #      "There is no Scene Manager Database Folder in this project path"]
        #     q = QtWidgets.QMessageBox()
        #     q.setIcon(QtWidgets.QMessageBox.Information)
        #     q.setText(msg[0])
        #     q.setInformativeText(msg[1])
        #     q.setWindowTitle(msg[2])
        #     q.setStandardButtons(QtWidgets.QMessageBox.Ok)
        #     ret = q.exec_()
        #     if ret == QtWidgets.QMessageBox.Ok:
        #         self.close()
        #         self.deleteLater()


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
                self.stb_label.resize(1, 1) ## 1, 1 is random, can be any number
                # event.ignore()
                # self.close()
                return

    def buildUI(self):

        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_6.setObjectName(("verticalLayout_6"))

        self.subP_HLayout = QtWidgets.QHBoxLayout()
        self.subP_label = QtWidgets.QLabel()
        self.subP_label.setText("Sub-Project:")
        self.subP_label.setAlignment((QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
        self.subP_combobox = QtWidgets.QComboBox()
        self.subP_HLayout.addWidget(self.subP_label)
        self.subP_HLayout.addWidget(self.subP_combobox)
        self.verticalLayout_6.addLayout(self.subP_HLayout)

        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setToolTip((""))
        self.tabWidget.setStatusTip((""))


        self.stb_tab = QtWidgets.QWidget()
        self.stb_tab.setToolTip((""))
        self.stb_tab.setStatusTip((""))
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.stb_tab)
        # self.horizontalLayout = QtWidgets.QHBoxLayout()


        # self.stb_label = ImageWidget()
        self.stb_label = QtImageViewer()
        self.stb_label.setMinimumSize(QtCore.QSize(10, 10))
        self.stb_label.setFrameShape(QtWidgets.QFrame.Box)
        # self.stb_label.setScaledContents(True)
        self.stb_label.setAlignment(QtCore.Qt.AlignCenter)

        # self.stb_label.setText(("Storyboard"))


        self.left_layout = QtWidgets.QVBoxLayout()
        self.left_layout.setSpacing(0)
        self.left_layout.addWidget(self.stb_label)
        self.left_layout.setContentsMargins(0, 0, 0, 0)

        self.left_widget = QtWidgets.QFrame()
        self.left_widget.setContentsMargins(0, 0, 0, 0)
        self.left_widget.setLayout(self.left_layout)

        # SPLITTER RIGHT SIDE

        self.storyboard_treeWidget = QtWidgets.QTreeWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.storyboard_treeWidget.sizePolicy().hasHeightForWidth())
        self.storyboard_treeWidget.setSizePolicy(sizePolicy)
        self.storyboard_treeWidget.setToolTip((""))
        self.storyboard_treeWidget.setStatusTip((""))

        self.storyboard_treeWidget.setSortingEnabled(True)
        header = QtWidgets.QTreeWidgetItem(["Name", "Date"])
        self.storyboard_treeWidget.setHeaderItem(header)

        self.right_layout = QtWidgets.QVBoxLayout()
        self.right_layout.addWidget(self.storyboard_treeWidget)






        self.right_widget = QtWidgets.QFrame()
        self.right_widget.setLayout(self.right_layout)
        self.right_widget.setContentsMargins(0, 0, 0, 0)

        # self.stb_label = QtWidgets.QLabel(self.splitter)

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


        # sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.stb_label.sizePolicy().hasHeightForWidth())
        # self.stb_label.setSizePolicy(sizePolicy)
        # self.stb_label.setMinimumSize(QtCore.QSize(221, 124))
        # self.stb_label.setMaximumSize(QtCore.QSize(9999, 9999))
        # self.stb_label.setSizeIncrement(QtCore.QSize(1, 1))
        # self.stb_label.setBaseSize(QtCore.QSize(0, 0))






        # self.stb_label = ImageWidget(self.splitter)
        # self.stb_label.setFrameShape(QtWidgets.QFrame.Box)
        # self.stb_label.setText(("Storyboard"))
        # self.stb_label.setObjectName(("stb_label"))





        # PyInstaller and Standalone version compatibility
        # if FORCE_QT4:
        #     self.tPixmap = QtWidgets.QPixmap("")
        # else:
        #     self.tPixmap = QtGui.QPixmap("")
        # # self.tPixmap = QtGui.QPixmap("")
        #
        # self.stb_label.setPixmap(self.tPixmap)

        




        # self.stb_listWidget.setColumnCount(2)
        # self.stb_listWidget.setRowCount(0)
        # item = QtWidgets.QTableWidgetItem()
        # item.setText(("Name"))
        # self.stb_listWidget.setHorizontalHeaderItem(0, item)
        # item = QtWidgets.QTableWidgetItem()
        # item.setText(("Date"))
        # self.stb_listWidget.setHorizontalHeaderItem(1, item)
        # self.stb_listWidget.horizontalHeader().setStretchLastSection(True)



        # self.horizontalLayout.addWidget(self.storyboard_treeWidget)
        
        # self.storyboard_listWidget = QtWidgets.QListWidget(self.stb_tab)
        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.storyboard_listWidget.sizePolicy().hasHeightForWidth())
        # self.storyboard_listWidget.setSizePolicy(sizePolicy)
        # self.storyboard_listWidget.setToolTip((""))
        # self.storyboard_listWidget.setStatusTip((""))
        # self.storyboard_listWidget.setWhatsThis((""))
        # self.storyboard_listWidget.setAccessibleName((""))
        # self.storyboard_listWidget.setAccessibleDescription((""))
        # self.storyboard_listWidget.setObjectName(("stb_tableWidget"))
        # # self.stb_listWidget.setColumnCount(2)
        # # self.stb_listWidget.setRowCount(0)
        # # item = QtWidgets.QTableWidgetItem()
        # # item.setText(("Name"))
        # # self.stb_listWidget.setHorizontalHeaderItem(0, item)
        # # item = QtWidgets.QTableWidgetItem()
        # # item.setText(("Date"))
        # # self.stb_listWidget.setHorizontalHeaderItem(1, item)
        # # self.stb_listWidget.horizontalHeader().setStretchLastSection(True)
        # self.horizontalLayout.addWidget(self.storyboard_listWidget)
        
        
        # self.verticalLayout_5.addLayout(self.horizontalLayout)
        self.verticalLayout_5.addWidget(self.splitter)

        self.addStb_pushButton = DropPushButton(self.stb_tab)
        self.addStb_pushButton.setMinimumSize(QtCore.QSize(0, 40))
        self.addStb_pushButton.setToolTip((""))
        self.addStb_pushButton.setStatusTip((""))
        self.addStb_pushButton.setWhatsThis((""))
        self.addStb_pushButton.setAccessibleName((""))
        self.addStb_pushButton.setAccessibleDescription((""))
        self.addStb_pushButton.setText(("Add New Storyboard"))
        self.addStb_pushButton.setObjectName(("addStb_pushButton"))
        self.verticalLayout_5.addWidget(self.addStb_pushButton)
        self.tabWidget.addTab(self.stb_tab, ("Storyboard"))

        self.brief_tab = QtWidgets.QWidget()
        self.brief_tab.setToolTip((""))
        self.brief_tab.setStatusTip((""))
        self.brief_tab.setWhatsThis((""))
        self.brief_tab.setAccessibleName((""))
        self.brief_tab.setAccessibleDescription((""))
        self.brief_tab.setObjectName(("brief_tab"))

        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.brief_tab)
        self.verticalLayout_4.setObjectName(("verticalLayout_4"))
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(("horizontalLayout_2"))

        self.brief_textEdit = QtWidgets.QTextEdit(self.brief_tab)
        self.brief_textEdit.setToolTip((""))
        self.brief_textEdit.setStatusTip((""))
        self.brief_textEdit.setWhatsThis((""))
        self.brief_textEdit.setAccessibleName((""))
        self.brief_textEdit.setAccessibleDescription((""))
        self.brief_textEdit.setObjectName(("brief_textEdit"))
        self.horizontalLayout_2.addWidget(self.brief_textEdit)

        self.brief_listWidget = QtWidgets.QListWidget(self.brief_tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.brief_listWidget.sizePolicy().hasHeightForWidth())
        self.brief_listWidget.setSizePolicy(sizePolicy)
        self.brief_listWidget.setToolTip((""))
        self.brief_listWidget.setStatusTip((""))
        self.brief_listWidget.setWhatsThis((""))
        self.brief_listWidget.setAccessibleName((""))
        self.brief_listWidget.setAccessibleDescription((""))
        self.brief_listWidget.setObjectName(("brief_tableWidget"))
        # self.brief_listWidget.setColumnCount(2)
        # self.brief_listWidget.setRowCount(0)
        # item = QtWidgets.QTableWidgetItem()
        # item.setText(("Name"))
        # self.brief_listWidget.setHorizontalHeaderItem(0, item)
        # item = QtWidgets.QTableWidgetItem()
        # item.setText(("Date"))
        # self.brief_listWidget.setHorizontalHeaderItem(1, item)
        # self.brief_listWidget.horizontalHeader().setStretchLastSection(True)
        self.horizontalLayout_2.addWidget(self.brief_listWidget)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)

        self.addBrief_pushButton = DropPushButton(self.brief_tab)
        self.addBrief_pushButton.setMinimumSize(QtCore.QSize(0, 40))
        self.addBrief_pushButton.setText(("Add New Document"))
        self.addBrief_pushButton.setObjectName(("addBrief_pushButton"))

        self.verticalLayout_4.addWidget(self.addBrief_pushButton)
        self.tabWidget.addTab(self.brief_tab, ("Brief"))

        self.artwork_tab = QtWidgets.QWidget()
        self.artwork_tab.setToolTip((""))
        self.artwork_tab.setStatusTip((""))
        self.artwork_tab.setWhatsThis((""))
        self.artwork_tab.setAccessibleName((""))
        self.artwork_tab.setAccessibleDescription((""))
        self.artwork_tab.setObjectName(("artwork_tab"))

        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.artwork_tab)
        self.verticalLayout_3.setObjectName(("verticalLayout_3"))

        self.artwork_listWidget = QtWidgets.QListWidget(self.artwork_tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.artwork_listWidget.sizePolicy().hasHeightForWidth())
        self.artwork_listWidget.setSizePolicy(sizePolicy)
        self.artwork_listWidget.setToolTip((""))
        self.artwork_listWidget.setStatusTip((""))
        self.artwork_listWidget.setWhatsThis((""))
        self.artwork_listWidget.setAccessibleName((""))
        self.artwork_listWidget.setAccessibleDescription((""))
        self.artwork_listWidget.setObjectName(("artwork_tableWidget"))
        # self.artwork_listWidget.setColumnCount(3)
        # self.artwork_listWidget.setRowCount(0)
        # item = QtWidgets.QTableWidgetItem()
        # item.setText(("Name"))
        # self.artwork_listWidget.setHorizontalHeaderItem(0, item)
        # item = QtWidgets.QTableWidgetItem()
        # item.setText(("Date"))
        # self.artwork_listWidget.setHorizontalHeaderItem(1, item)
        # item = QtWidgets.QTableWidgetItem()
        # item.setText(("Notes"))
        # self.artwork_listWidget.setHorizontalHeaderItem(2, item)
        # self.artwork_listWidget.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout_3.addWidget(self.artwork_listWidget)

        self.addArtwork_pushButton = DropPushButton(self.artwork_tab)
        self.addArtwork_pushButton.setMinimumSize(QtCore.QSize(0, 40))
        self.addArtwork_pushButton.setToolTip((""))
        self.addArtwork_pushButton.setStatusTip((""))
        self.addArtwork_pushButton.setWhatsThis((""))
        self.addArtwork_pushButton.setAccessibleName((""))
        self.addArtwork_pushButton.setAccessibleDescription((""))
        self.addArtwork_pushButton.setText(("Add New Artwork (Folder)"))
        self.addArtwork_pushButton.setShortcut((""))
        self.addArtwork_pushButton.setObjectName(("addArtwork_pushButton"))

        self.verticalLayout_3.addWidget(self.addArtwork_pushButton)
        self.tabWidget.addTab(self.artwork_tab, ("Artwork"))
        self.footage_tab = QtWidgets.QWidget()
        self.footage_tab.setToolTip((""))
        self.footage_tab.setStatusTip((""))
        self.footage_tab.setWhatsThis((""))
        self.footage_tab.setAccessibleName((""))
        self.footage_tab.setAccessibleDescription((""))
        self.footage_tab.setObjectName(("footage_tab"))

        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.footage_tab)
        self.verticalLayout_2.setObjectName(("verticalLayout_2"))

        self.footage_listWidget = QtWidgets.QListWidget(self.footage_tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.footage_listWidget.sizePolicy().hasHeightForWidth())
        self.footage_listWidget.setSizePolicy(sizePolicy)
        self.footage_listWidget.setToolTip((""))
        self.footage_listWidget.setStatusTip((""))
        self.footage_listWidget.setWhatsThis((""))
        self.footage_listWidget.setAccessibleName((""))
        self.footage_listWidget.setAccessibleDescription((""))
        self.footage_listWidget.setObjectName(("footage_tableWidget"))
        # self.footage_listWidget.setColumnCount(3)
        # self.footage_listWidget.setRowCount(0)
        # item = QtWidgets.QTableWidgetItem()
        # item.setText(("Name"))
        # self.footage_listWidget.setHorizontalHeaderItem(0, item)
        # item = QtWidgets.QTableWidgetItem()
        # item.setText(("Date"))
        # self.footage_listWidget.setHorizontalHeaderItem(1, item)
        # item = QtWidgets.QTableWidgetItem()
        # item.setText(("Notes"))
        # self.footage_listWidget.setHorizontalHeaderItem(2, item)
        # self.footage_listWidget.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout_2.addWidget(self.footage_listWidget)

        self.addFootage_pushButton = DropPushButton(self.footage_tab)
        self.addFootage_pushButton.setMinimumSize(QtCore.QSize(0, 40))
        self.addFootage_pushButton.setToolTip((""))
        self.addFootage_pushButton.setStatusTip((""))
        self.addFootage_pushButton.setWhatsThis((""))
        self.addFootage_pushButton.setAccessibleName((""))
        self.addFootage_pushButton.setAccessibleDescription((""))
        self.addFootage_pushButton.setText(("Add New Footage"))
        self.addFootage_pushButton.setObjectName(("addFootage_pushButton"))

        self.verticalLayout_2.addWidget(self.addFootage_pushButton)
        self.tabWidget.addTab(self.footage_tab, ("Footage"))

        self.other_tab = QtWidgets.QWidget()
        self.other_tab.setToolTip((""))
        self.other_tab.setStatusTip((""))
        self.other_tab.setWhatsThis((""))
        self.other_tab.setAccessibleName((""))
        self.other_tab.setAccessibleDescription((""))
        self.other_tab.setObjectName(("other_tab"))

        self.verticalLayout = QtWidgets.QVBoxLayout(self.other_tab)
        self.verticalLayout.setObjectName(("verticalLayout"))

        self.other_listWidget = QtWidgets.QListWidget(self.other_tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.other_listWidget.sizePolicy().hasHeightForWidth())
        self.other_listWidget.setSizePolicy(sizePolicy)
        self.other_listWidget.setToolTip((""))
        self.other_listWidget.setStatusTip((""))
        self.other_listWidget.setWhatsThis((""))
        self.other_listWidget.setAccessibleName((""))
        self.other_listWidget.setAccessibleDescription((""))
        self.other_listWidget.setObjectName(("other_tableWidget"))
        # self.other_listWidget.setColumnCount(3)
        # self.other_listWidget.setRowCount(0)
        # item = QtWidgets.QTableWidgetItem()
        # item.setText(("Name"))
        # self.other_listWidget.setHorizontalHeaderItem(0, item)
        # item = QtWidgets.QTableWidgetItem()
        # item.setText(("Date"))
        # self.other_listWidget.setHorizontalHeaderItem(1, item)
        # item = QtWidgets.QTableWidgetItem()
        # item.setText(("Notes"))
        # self.other_listWidget.setHorizontalHeaderItem(2, item)
        # self.other_listWidget.horizontalHeader().setCascadingSectionResizes(False)
        # self.other_listWidget.horizontalHeader().setDefaultSectionSize(100)
        # self.other_listWidget.horizontalHeader().setMinimumSectionSize(35)
        # self.other_listWidget.horizontalHeader().setSortIndicatorShown(False)
        # self.other_listWidget.horizontalHeader().setStretchLastSection(True)
        # self.other_listWidget.verticalHeader().setVisible(False)
        # self.other_listWidget.verticalHeader().setMinimumSectionSize(19)
        # self.other_listWidget.verticalHeader().setStretchLastSection(False)
        self.verticalLayout.addWidget(self.other_listWidget)
        self.addOther_pushButton = DropPushButton(self.other_tab)
        self.addOther_pushButton.setMinimumSize(QtCore.QSize(0, 40))
        self.addOther_pushButton.setToolTip((""))
        self.addOther_pushButton.setStatusTip((""))
        self.addOther_pushButton.setWhatsThis((""))
        self.addOther_pushButton.setAccessibleName((""))
        self.addOther_pushButton.setAccessibleDescription((""))
        self.addOther_pushButton.setText(("Add New Footage"))
        self.addOther_pushButton.setShortcut((""))
        self.addOther_pushButton.setObjectName(("addOther_pushButton"))
        self.verticalLayout.addWidget(self.addOther_pushButton)
        self.tabWidget.addTab(self.other_tab, ("Other"))
        self.verticalLayout_6.addWidget(self.tabWidget)
        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 715, 21))
        self.menubar.setToolTip((""))
        self.menubar.setStatusTip((""))
        self.menubar.setWhatsThis((""))
        self.menubar.setAccessibleName((""))
        self.menubar.setAccessibleDescription((""))
        self.menubar.setObjectName(("menubar"))
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setToolTip((""))
        self.statusbar.setStatusTip((""))
        self.statusbar.setWhatsThis((""))
        self.statusbar.setAccessibleName((""))
        self.statusbar.setAccessibleDescription((""))
        self.statusbar.setObjectName(("statusbar"))
        self.setStatusBar(self.statusbar)

        self.tabWidget.setCurrentIndex(0)

        # ------------------
        # SIGNAL CONNECTIONS
        # ------------------

        self.subP_combobox.activated.connect(self.onSubProjectChange)

        self.storyboard_treeWidget.currentItemChanged.connect(lambda item: self.onChangeItem(item, "storyboard"))

        self.addStb_pushButton.dropped.connect(lambda path: self.droppedPath(path, "storyboard"))
        self.addBrief_pushButton.dropped.connect(lambda path: self.droppedPath(path, "brief"))
        self.addFootage_pushButton.dropped.connect(lambda path: self.droppedPath(path, "footage"))
        self.addArtwork_pushButton.dropped.connect(lambda path: self.droppedPath(path, "artwork"))
        self.addOther_pushButton.dropped.connect(lambda path: self.droppedPath(path, "other"))

        self.tabWidget.currentChanged.connect(self.onMatCategoryChange)

    def initMainUI(self):
        """Inits the ui elements with the information from  logic class"""
        # update sub-projects
        self.subP_combobox.addItems(self.promat.getSubProjects())
        self.updateViews()
        pass

    def onChangeItem(self, item, matCategory):
        if not item:
            return

        # print item
        matDBpath = self.promat.materialsInCategory[str(item.text(0))]
        self.promat._loadMaterialInfo(matDBpath)
        pic = self.promat.getMaterialPath()

        # print pic
        # self.stb_label.setImage(pic)

        # update thumb
        if FORCE_QT4:
            self.tPixmap = QtWidgets.QPixmap(pic)
        else:
            self.tPixmap = QtGui.QPixmap(pic)

        self.stb_label.setImage(self.tPixmap)

        # h = float(self.tPixmap.height())
        # w = float(self.tPixmap.width())
        # if h > 0 and w > 0:
        #     self.stb_label.aspectRatio = float(w/h)
        #     self.stb_label.setPixmap(self.tPixmap)
        # else:
        #     self.stb_label.clear()
        #     self.stb_label.setText("No Preview")



    def onSubProjectChange(self):
        self.promat.currentSubIndex = self.subP_combobox.currentIndex()

    def onMatCategoryChange(self):
        matCategoryName = self.tabWidget.tabText(self.tabWidget.currentIndex())
        # print self.promat.scanMaterials(matCategoryName)
        self.updateViews()

    def updateViews(self):
        matCategory = self.tabWidget.tabText(self.tabWidget.currentIndex())
        materials = self.promat.scanMaterials(str(matCategory))

        # keys = materials.keys()
        # for date in sorted(keys, key=lambda date: os.path.getmtime(materials[date])):
        #     print date

        if matCategory == "Storyboard":
            self.storyboard_treeWidget.clear()
            for x in materials.items():
                timestamp = os.path.getmtime(x[1])
                timestampFormatted = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                item = QtWidgets.QTreeWidgetItem(self.storyboard_treeWidget, [x[0], str(timestampFormatted)])
            # sort by date default
            self.storyboard_treeWidget.sortItems(1, 0) # 1 is Date Column, 0 is Ascending order



        # if matCategory == "Storyboard":
        #     self.storyboard_listWidget.clear()
        #     self.storyboard_listWidget.addItems(self._sortDictionary(materials, sortBy="date", reversed=False))
        #     pass



        # elif matCategory == "Brief":
        #     self.brief_listWidget.clear()
        #     self.brief_listWidget.addItems(materials)
        #     pass
        # elif matCategory == "Artwork":
        #     self.artwork_listWidget.clear()
        #     self.artwork_listWidget.addItems(materials)
        #     pass
        # elif matCategory == "Footage":
        #     self.footage_listWidget.clear()
        #     self.footage_listWidget.addItems(materials)
        #     pass
        # elif matCategory == "Other":
        #     self.other_listWidget.clear()
        #     self.other_listWidget.addItems(materials)
        #     pass
        # self.stb_tableWidget.

    def _sortDictionary(self, dictionary, sortBy="date", reversed=False):
        """sorts the Sm Dictionary and returns the sorted keys"""
        keys = dictionary.keys()
        if sortBy == "date":
            sortedKeys = [date for date in sorted(keys, key=lambda date: os.path.getmtime(dictionary[date]), reverse=reversed)]
        elif sortBy == "name":
            sortedKeys = [name for name in sorted(keys, reverse=reversed)]
        elif sortBy == "size":
            sortedKeys = [size for size in sorted(keys, key=lambda size: os.path.getsize(dictionary[size]), reverse=reversed)]
        else:
            raise Exception("projectMaterials - _sortDictionary - unidentified sorting type")
        return sortedKeys


    def droppedPath(self, path, material):
        self.promat.saveMaterial(path, material)




class DropPushButton(QtWidgets.QPushButton):
    """Custom LineEdit Class accepting drops"""
    # PyInstaller and Standalone version compatibility
    if FORCE_QT4:
        dropped = QtCore.pyqtSignal(list)
    else:
        dropped = Qt.QtCore.Signal(list)

    def __init__(self, type, parent=None):
        super(DropPushButton, self).__init__(parent)
        self.oldText=""
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
        # rawPath = event.mimeData().data('text/uri-list').__str__()
        # path = rawPath.replace("file:///", "").splitlines()[0]
        # self.dropped.emit(path)
        links = []

        for url in event.mimeData().urls():
            links.append(str(url.toLocalFile()))
        self.dropped.emit(links)
        # self.addItem(path)


if __name__ == '__main__':
    os.environ["FORCE_QT4"] = "True"
    app = QtWidgets.QApplication(sys.argv)
    selfLoc = os.path.dirname(os.path.abspath(__file__))
    stylesheetFile = os.path.join(selfLoc, "CSS", "darkorange.stylesheet")


    with open(stylesheetFile, "r") as fh:
        app.setStyleSheet(fh.read())
    window = MainUI()
    window.show()
    sys.exit(app.exec_())



